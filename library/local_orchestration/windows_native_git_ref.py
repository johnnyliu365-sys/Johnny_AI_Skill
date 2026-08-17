"""Windows-native exact Git ref hints using overlapped directory notifications."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess
from threading import current_thread, Lock, Thread
from typing import cast, Final, TYPE_CHECKING

from pydantic import ValidationError
import pywintypes
import win32con
import win32event
import win32file

from library.workflow_router.git_handoff_contracts import (
    GitNativeFailureKind,
    GitNativeFailureSignal,
    GitNativeRegistrationRequest,
    GitNativeRegistrationResult,
    GitNativeRegistrationStatus,
    GitRefSignal,
    SubscriptionId,
)
from .git_handoff_event_adapter import NativeGitRefSignalSink

if TYPE_CHECKING:
    import _win32typing


_NOTIFY_FILTER = (
    win32con.FILE_NOTIFY_CHANGE_FILE_NAME
    | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
)
_FILE_LIST_DIRECTORY: Final[int] = 0x0001


@dataclass(frozen=True, slots=True)
class _WatchSpec:
    directory: Path
    subtree: bool
    exact_names: frozenset[str]
    name_prefixes: tuple[str, ...]

    def matches(self, raw_name: str) -> bool:
        normalized = raw_name.replace("\\", "/").casefold()
        return normalized in self.exact_names or any(
            normalized.startswith(prefix) for prefix in self.name_prefixes
        )


@dataclass(slots=True)
class _ArmedWatch:
    spec: _WatchSpec
    handle: _win32typing.PyHANDLE
    buffer: _win32typing.PyOVERLAPPEDReadBuffer
    overlapped: _win32typing.PyOVERLAPPED


class _Subscription:
    def __init__(
        self,
        request: GitNativeRegistrationRequest,
        stop_event: int,
        watches: tuple[_ArmedWatch, ...],
    ) -> None:
        self.request = request
        self.stop_event = stop_event
        self.watches = watches
        self.thread: Thread | None = None


def _git_common_directory(repository_root: Path) -> Path:
    completed = subprocess.run(
        ("git", "-C", str(repository_root), "rev-parse", "--git-common-dir"),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise ValueError("repository has no readable Git common directory")
    raw = Path(completed.stdout.strip())
    candidate = raw if raw.is_absolute() else repository_root / raw
    common = candidate.resolve(strict=True)
    if not common.is_dir():
        raise ValueError("Git common directory must be an existing directory")
    return common


def _loose_ref_spec(common: Path, exact_git_ref: str) -> _WatchSpec:
    ref_parts = PurePosixPath(exact_git_ref).parts
    target = common.joinpath(*ref_parts)
    ancestor = target.parent
    while not ancestor.exists():
        if ancestor == common:
            raise ValueError("Git ref metadata parent is unavailable")
        ancestor = ancestor.parent
    resolved_ancestor = ancestor.resolve(strict=True)
    resolved_ancestor.relative_to(common)
    relative = target.relative_to(resolved_ancestor).as_posix().casefold()
    return _WatchSpec(
        directory=resolved_ancestor,
        subtree=len(PurePosixPath(relative).parts) > 1,
        exact_names=frozenset((relative,)),
        name_prefixes=(),
    )


def _packed_ref_spec(common: Path) -> _WatchSpec:
    return _WatchSpec(
        directory=common,
        subtree=False,
        exact_names=frozenset(("packed-refs",)),
        name_prefixes=("packed-refs.",),
    )


class WindowsNativeGitRefNotificationPort:
    """One native notification composition per exact subscription, with no polling."""

    def __init__(self, repository_root: Path, sink: NativeGitRefSignalSink) -> None:
        if not isinstance(repository_root, Path):
            raise TypeError("repository root must be a Path")
        if not repository_root.is_absolute():
            raise ValueError("repository root must be absolute")
        root = repository_root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("repository root must be an existing directory")
        self._common = _git_common_directory(root)
        self._sink = sink
        self._lock = Lock()
        self._subscriptions: dict[SubscriptionId, _Subscription] = {}

    def register(self, request: GitNativeRegistrationRequest) -> GitNativeRegistrationResult:
        if type(request) is not GitNativeRegistrationRequest:
            return GitNativeRegistrationResult(status=GitNativeRegistrationStatus.REJECTED)
        try:
            trusted = GitNativeRegistrationRequest.model_validate(request, strict=True)
        except ValidationError:
            return GitNativeRegistrationResult(status=GitNativeRegistrationStatus.REJECTED)
        with self._lock:
            existing = self._subscriptions.get(trusted.subscription_id)
            if existing is not None:
                if existing.request == trusted:
                    return GitNativeRegistrationResult(
                        status=GitNativeRegistrationStatus.REGISTERED,
                        event_source_ref=trusted.event_source_ref,
                        subscription_id=trusted.subscription_id,
                    )
                return GitNativeRegistrationResult(status=GitNativeRegistrationStatus.REJECTED)
            opened_watches: list[_ArmedWatch] = []
            try:
                specs = (
                    _loose_ref_spec(self._common, trusted.exact_git_ref),
                    _packed_ref_spec(self._common),
                )
                for spec in specs:
                    opened_watches.append(self._open_and_arm(spec))
                watches = tuple(opened_watches)
                stop_event = win32event.CreateEvent(None, True, False, None)
            except (OSError, ValueError, pywintypes.error):
                self._close_watches(tuple(opened_watches))
                return GitNativeRegistrationResult(
                    status=GitNativeRegistrationStatus.UNAVAILABLE
                )
            subscription = _Subscription(trusted, stop_event, watches)
            thread = Thread(
                target=self._run_subscription,
                args=(subscription,),
                name=f"git-ref-{trusted.subscription_id}",
                daemon=True,
            )
            subscription.thread = thread
            self._subscriptions[trusted.subscription_id] = subscription
            try:
                thread.start()
            except RuntimeError:
                self._subscriptions.pop(trusted.subscription_id, None)
                self._close_watches(watches)
                win32file.CloseHandle(stop_event)
                return GitNativeRegistrationResult(
                    status=GitNativeRegistrationStatus.UNAVAILABLE
                )
            return GitNativeRegistrationResult(
                status=GitNativeRegistrationStatus.REGISTERED,
                event_source_ref=trusted.event_source_ref,
                subscription_id=trusted.subscription_id,
            )

    @staticmethod
    def _open_and_arm(spec: _WatchSpec) -> _ArmedWatch:
        handle = win32file.CreateFile(
            str(spec.directory),
            _FILE_LIST_DIRECTORY,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS | win32con.FILE_FLAG_OVERLAPPED,
            None,
        )
        buffer = win32file.AllocateReadBuffer(8192)
        overlapped = pywintypes.OVERLAPPED()
        overlapped.hEvent = win32event.CreateEvent(None, True, False, None)
        watch = _ArmedWatch(spec, handle, buffer, overlapped)
        try:
            WindowsNativeGitRefNotificationPort._arm(watch)
        except pywintypes.error:
            handle.Close()
            win32file.CloseHandle(overlapped.hEvent)
            raise
        return watch

    @staticmethod
    def _arm(watch: _ArmedWatch) -> None:
        win32event.ResetEvent(watch.overlapped.hEvent)
        win32file.ReadDirectoryChangesW(
            int(watch.handle),
            watch.buffer,
            watch.spec.subtree,
            _NOTIFY_FILTER,
            watch.overlapped,
        )

    @staticmethod
    def _changed_names(watch: _ArmedWatch) -> tuple[str, ...]:
        byte_count = win32file.GetOverlappedResult(
            int(watch.handle),
            watch.overlapped,
            True,
        )
        if byte_count == 0:
            return ()
        raw: object = win32file.FILE_NOTIFY_INFORMATION(
            cast(str, watch.buffer), byte_count
        )
        if not isinstance(raw, (list, tuple)):
            return ()
        names: list[str] = []
        for item in raw:
            if not isinstance(item, tuple) or len(item) != 2:
                continue
            name = item[1]
            if isinstance(name, str):
                names.append(name)
        return tuple(names)

    def _run_subscription(self, subscription: _Subscription) -> None:
        wait_handles = [
            subscription.stop_event,
            *(watch.overlapped.hEvent for watch in subscription.watches),
        ]
        try:
            while True:
                wait_result = win32event.WaitForMultipleObjects(
                    wait_handles,
                    False,
                    win32event.INFINITE,
                )
                index = wait_result - win32event.WAIT_OBJECT_0
                if index == 0:
                    return
                if index < 1 or index > len(subscription.watches):
                    raise OSError("native wait returned an invalid handle index")
                watch = subscription.watches[index - 1]
                names = self._changed_names(watch)
                self._arm(watch)
                if any(watch.spec.matches(name) for name in names):
                    self._sink.on_signal(
                        GitRefSignal(
                            event_source_ref=subscription.request.event_source_ref,
                            subscription_id=subscription.request.subscription_id,
                        )
                    )
        except (OSError, pywintypes.error):
            self._sink.on_failure(
                GitNativeFailureSignal(
                    event_source_ref=subscription.request.event_source_ref,
                    subscription_id=subscription.request.subscription_id,
                    failure=GitNativeFailureKind.NOTIFICATION_UNAVAILABLE,
                )
            )
        finally:
            with self._lock:
                current = self._subscriptions.get(subscription.request.subscription_id)
                if current is subscription:
                    self._subscriptions.pop(subscription.request.subscription_id, None)
            self._close_watches(subscription.watches)
            win32file.CloseHandle(subscription.stop_event)

    def cancel(self, subscription_id: SubscriptionId) -> bool:
        with self._lock:
            subscription = self._subscriptions.pop(subscription_id, None)
        if subscription is None:
            return True
        win32event.SetEvent(subscription.stop_event)
        thread = subscription.thread
        if thread is not None and thread is not current_thread():
            thread.join(timeout=5.0)
        return thread is None or thread is current_thread() or not thread.is_alive()

    @staticmethod
    def _close_watches(watches: tuple[_ArmedWatch, ...]) -> None:
        for watch in watches:
            try:
                watch.handle.Close()
            except pywintypes.error:
                pass
            try:
                win32file.CloseHandle(watch.overlapped.hEvent)
            except pywintypes.error:
                pass


@dataclass(frozen=True, slots=True)
class WindowsNativeGitRefNotificationFactory:
    repository_root: Path

    def create(
        self,
        sink: NativeGitRefSignalSink,
    ) -> WindowsNativeGitRefNotificationPort:
        return WindowsNativeGitRefNotificationPort(self.repository_root, sink)


__all__ = [
    "NativeGitRefSignalSink",
    "WindowsNativeGitRefNotificationFactory",
    "WindowsNativeGitRefNotificationPort",
]
