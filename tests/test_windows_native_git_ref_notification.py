"""Windows native exact-ref notification tests without polling."""

from __future__ import annotations

from pathlib import Path
import ast
import subprocess
from tempfile import TemporaryDirectory
from threading import Event, Lock
import unittest

from library.local_orchestration.windows_native_git_ref import (
    NativeGitRefSignalSink,
    WindowsNativeGitRefNotificationPort,
)
from library.workflow_router.git_handoff_contracts import (
    GitNativeFailureSignal,
    GitNativeRegistrationRequest,
    GitNativeRegistrationStatus,
    GitRefSignal,
)


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def _repository(root: Path) -> None:
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.email", "native-event@example.invalid")
    _run_git(root, "config", "user.name", "Native Event")
    (root / "source.txt").write_text("baseline\n", encoding="utf-8")
    _run_git(root, "add", "source.txt")
    _run_git(root, "commit", "-m", "baseline")


class _Sink(NativeGitRefSignalSink):
    def __init__(self) -> None:
        self._lock = Lock()
        self._event = Event()
        self.signals: list[GitRefSignal] = []
        self.failures: list[GitNativeFailureSignal] = []

    def on_signal(self, signal: GitRefSignal) -> None:
        with self._lock:
            self.signals.append(signal)
            self._event.set()

    def on_failure(self, signal: GitNativeFailureSignal) -> None:
        with self._lock:
            self.failures.append(signal)
            self._event.set()

    def wait(self, timeout: float = 5.0) -> bool:
        return self._event.wait(timeout)

    def clear(self) -> None:
        self._event.clear()
        with self._lock:
            self.signals.clear()
            self.failures.clear()


class _SelfCancellingSink(NativeGitRefSignalSink):
    def __init__(self) -> None:
        self.port: WindowsNativeGitRefNotificationPort | None = None
        self.cancelled = Event()

    def on_signal(self, signal: GitRefSignal) -> None:
        if self.port is None:
            raise AssertionError("self-cancelling sink is not bound")
        if not self.port.cancel(signal.subscription_id):
            raise AssertionError("callback-local cancellation failed")
        self.cancelled.set()

    def on_failure(self, signal: GitNativeFailureSignal) -> None:
        raise AssertionError(f"unexpected native failure: {signal.failure}")


class WindowsNativeGitRefNotificationTests(unittest.TestCase):
    def test_exact_loose_ref_change_signals_but_sibling_ref_does_not(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _repository(root)
            sink = _Sink()
            port = WindowsNativeGitRefNotificationPort(root, sink)
            request = GitNativeRegistrationRequest(
                event_source_ref="event-source-native-main",
                subscription_id="subscription-native-main",
                exact_git_ref="refs/heads/main",
            )
            registered = port.register(request)
            self.assertEqual(GitNativeRegistrationStatus.REGISTERED, registered.status)

            head = _run_git(root, "rev-parse", "HEAD")
            _run_git(root, "update-ref", "refs/heads/unrelated", head)
            self.assertFalse(sink.wait(0.5))

            (root / "source.txt").write_text("baseline\nchange\n", encoding="utf-8")
            _run_git(root, "add", "source.txt")
            _run_git(root, "commit", "-m", "change main")
            self.assertTrue(sink.wait())
            self.assertTrue(
                all(signal.subscription_id == request.subscription_id for signal in sink.signals)
            )
            self.assertTrue(port.cancel(request.subscription_id))

    def test_source_uses_infinite_native_wait_without_polling_or_git_readback(self) -> None:
        source_path = (
            Path(__file__).resolve().parents[1]
            / "library"
            / "local_orchestration"
            / "windows_native_git_ref.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertIn("win32event.INFINITE", source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("heartbeat", source.casefold())
        self.assertNotIn("status --", source)
        self.assertNotIn("ls-files", source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertNotIn("time", imported_roots)

    def test_packed_refs_replacement_signals_and_cancel_is_idempotent(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _repository(root)
            sink = _Sink()
            port = WindowsNativeGitRefNotificationPort(root, sink)
            request = GitNativeRegistrationRequest(
                event_source_ref="event-source-native-packed",
                subscription_id="subscription-native-packed",
                exact_git_ref="refs/heads/main",
            )
            self.assertEqual(
                GitNativeRegistrationStatus.REGISTERED,
                port.register(request).status,
            )
            _run_git(root, "pack-refs", "--all", "--prune")
            self.assertTrue(sink.wait())
            self.assertTrue(port.cancel(request.subscription_id))
            self.assertTrue(port.cancel(request.subscription_id))

    def test_callback_can_cancel_its_own_subscription_without_deadlock(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _repository(root)
            sink = _SelfCancellingSink()
            port = WindowsNativeGitRefNotificationPort(root, sink)
            sink.port = port
            request = GitNativeRegistrationRequest(
                event_source_ref="event-source-native-self-cancel",
                subscription_id="subscription-native-self-cancel",
                exact_git_ref="refs/heads/main",
            )
            self.assertEqual(GitNativeRegistrationStatus.REGISTERED, port.register(request).status)
            (root / "source.txt").write_text("baseline\nself cancel\n", encoding="utf-8")
            _run_git(root, "add", "source.txt")
            _run_git(root, "commit", "-m", "trigger self cancellation")
            self.assertTrue(sink.cancelled.wait(5.0))
            self.assertTrue(port.cancel(request.subscription_id))


if __name__ == "__main__":
    unittest.main()
