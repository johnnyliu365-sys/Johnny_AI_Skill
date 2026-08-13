"""Exact provision and teardown implementation for Ticket 05S1 only."""

from __future__ import annotations

from pathlib import Path
import re
import stat
import uuid

from pydantic import ValidationError

from .contracts import (
    EnvironmentFault,
    EnvironmentId,
    EnvironmentLease,
    EnvironmentLocator,
    EnvironmentMarker,
    EnvironmentOverlay,
    EnvironmentOverlayEntry,
    EnvironmentOwnerId,
    EnvironmentPath,
    EnvironmentRelativeLocator,
    EnvironmentVariable,
    ProvisionBlocked,
    ProvisionBlockReason,
    ProvisionedEnvironment,
    ProvisionResult,
    TeardownBlockReason,
    TeardownResult,
    TeardownStatus,
    revalidate_lease,
    revalidate_owner,
)


_ROOT_PREFIX = "johnny-stage-env-"
_ROOT_NAME_PATTERN = re.compile(r"johnny-stage-env-[0-9a-f]{32}")
_RUNTIME_PARENT_NAME = ".johnny-runtime"
_TESTS_DIRECTORY = Path(__file__).resolve(strict=True).parents[2]
_PROJECT_RUNTIME_PARENT = _TESTS_DIRECTORY / _RUNTIME_PARENT_NAME
_CLAIMED_MARKERS: dict[Path, EnvironmentMarker] = {}


class DisposableEnvironmentAllocator:
    """Creates marker-bound roots below this checkout's project-owned runtime."""

    def __init__(self) -> None:
        self._runtime_parent = EnvironmentLocator(value=str(_PROJECT_RUNTIME_PARENT))
        self._claimed_owner_values: set[str] = set()
        self._fault = EnvironmentFault.NONE

    @classmethod
    def from_project_runtime(cls) -> DisposableEnvironmentAllocator:
        return cls()

    def configure_fault(self, fault: EnvironmentFault) -> None:
        self._fault = EnvironmentFault(fault)

    def provision(self, owner: EnvironmentOwnerId) -> ProvisionResult:
        validated_owner = revalidate_owner(owner)
        if isinstance(validated_owner, ProvisionBlocked):
            return validated_owner
        if validated_owner.value in self._claimed_owner_values:
            return ProvisionBlocked(reason=ProvisionBlockReason.OWNER_REPLAYED)
        if not self._prepare_runtime_parent():
            return ProvisionBlocked(reason=ProvisionBlockReason.INITIALIZATION_FAILED)
        try:
            root = self._create_root()
        except OSError:
            self._remove_runtime_parent_if_empty()
            return ProvisionBlocked(reason=ProvisionBlockReason.INITIALIZATION_FAILED)
        environment_id = EnvironmentId(value=f"environment-{uuid.uuid4().hex}")
        root_locator = EnvironmentLocator(value=str(root.resolve(strict=True)))
        try:
            self._validate_new_root(root_locator)
            if self._consume_fault(EnvironmentFault.AFTER_ROOT):
                self._remove_new_root(root_locator)
                return ProvisionBlocked(reason=ProvisionBlockReason.FAULT_AFTER_ROOT)
            marker = EnvironmentMarker(owner=validated_owner, environment_id=environment_id, root=root_locator)
            marker_path = root_locator.path / ".johnny-stage-env-owner.json"
            marker_path.write_text(marker.model_dump_json(warnings=False), encoding="utf-8")
            if self._consume_fault(EnvironmentFault.AFTER_MARKER):
                self._remove_new_root(root_locator)
                return ProvisionBlocked(reason=ProvisionBlockReason.FAULT_AFTER_MARKER)
            environment = self._build_environment(validated_owner, environment_id, root_locator, marker)
            self._claimed_owner_values.add(validated_owner.value)
            _CLAIMED_MARKERS[root_locator.path] = marker
            return ProvisionedEnvironment(environment=environment)
        except (OSError, ValidationError, ValueError):
            self._remove_new_root(root_locator)
            return ProvisionBlocked(reason=ProvisionBlockReason.INITIALIZATION_FAILED)

    def teardown(self, lease: EnvironmentLease) -> TeardownResult:
        validated_lease = revalidate_lease(lease)
        if isinstance(validated_lease, TeardownResult):
            return validated_lease
        root = validated_lease.root.path
        if self._is_reparse_point(root):
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.ROOT_REPARSE)
        if not root.exists():
            return TeardownResult(status=TeardownStatus.ALREADY_ABSENT, reason=TeardownBlockReason.NONE)
        if not self._is_exact_owned_root(root):
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.ROOT_ESCAPE)
        marker_path = validated_lease.marker_path
        if self._is_reparse_point(marker_path):
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.MARKER_MISMATCH)
        try:
            marker = EnvironmentMarker.model_validate_json(marker_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.MARKER_MISSING)
        except (OSError, ValidationError, ValueError):
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.MARKER_MISMATCH)
        if marker != validated_lease.marker:
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.MARKER_MISMATCH)
        if not self._tree_is_exact(root):
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.CHILD_ESCAPE)
        try:
            self._remove_exact_tree(root)
        except OSError:
            return TeardownResult(status=TeardownStatus.BLOCKED, reason=TeardownBlockReason.DELETE_FAILED)
        _CLAIMED_MARKERS.pop(root, None)
        self._remove_runtime_parent_if_empty()
        return TeardownResult(status=TeardownStatus.REMOVED, reason=TeardownBlockReason.NONE)

    def _build_environment(
        self,
        owner: EnvironmentOwnerId,
        environment_id: EnvironmentId,
        root: EnvironmentLocator,
        marker: EnvironmentMarker,
    ) -> EnvironmentLease:
        profile = self._create_child(root, "profile")
        local_app_data = self._create_child(root, "local-app-data")
        roaming_app_data = self._create_child(root, "roaming-app-data")
        temporary = self._create_child(root, "temp")
        codex_home = self._create_child(root, "codex-home")
        overlay = EnvironmentOverlay(
            entries=(
                EnvironmentOverlayEntry(key=EnvironmentVariable.USERPROFILE, path=profile.absolute),
                EnvironmentOverlayEntry(key=EnvironmentVariable.LOCALAPPDATA, path=local_app_data.absolute),
                EnvironmentOverlayEntry(key=EnvironmentVariable.APPDATA, path=roaming_app_data.absolute),
                EnvironmentOverlayEntry(key=EnvironmentVariable.TEMP, path=temporary.absolute),
                EnvironmentOverlayEntry(key=EnvironmentVariable.TMP, path=temporary.absolute),
                EnvironmentOverlayEntry(key=EnvironmentVariable.CODEX_HOME, path=codex_home.absolute),
            )
        )
        return EnvironmentLease(
            owner=owner,
            environment_id=environment_id,
            root=root,
            root_relative=EnvironmentRelativeLocator(value=root.path.name),
            profile=profile,
            local_app_data=local_app_data,
            roaming_app_data=roaming_app_data,
            temporary=temporary,
            codex_home=codex_home,
            overlay=overlay,
            marker=marker,
        )

    def _create_root(self) -> Path:
        for _ in range(4):
            candidate = self._runtime_parent.path / f"{_ROOT_PREFIX}{uuid.uuid4().hex}"
            try:
                candidate.mkdir()
                return candidate
            except FileExistsError:
                continue
        raise OSError("unable to create a unique disposable environment root")

    @staticmethod
    def _create_child(root: EnvironmentLocator, relative: str) -> EnvironmentPath:
        child = root.path / relative
        child.mkdir()
        return EnvironmentPath(
            relative=EnvironmentRelativeLocator(value=relative),
            absolute=EnvironmentLocator(value=str(child.resolve(strict=True))),
        )

    def _validate_new_root(self, root: EnvironmentLocator) -> None:
        if self._is_reparse_point(root.path) or not self._is_exact_owned_root(root.path):
            raise ValueError("new environment root must be an exact owned direct project child")

    def _is_exact_owned_root(self, root: Path) -> bool:
        return (
            root.is_absolute()
            and _ROOT_NAME_PATTERN.fullmatch(root.name) is not None
            and root.parent.resolve(strict=True) == self._runtime_parent.path.resolve(strict=True)
            and root.exists()
        )

    def _prepare_runtime_parent(self) -> bool:
        parent = self._runtime_parent.path
        try:
            if self._is_reparse_point(parent):
                return False
            if not parent.exists():
                parent.mkdir()
                if self._is_reparse_point(parent):
                    return False
            if not parent.is_dir():
                return False
            return self._runtime_children_are_claimed()
        except OSError:
            return False

    def _runtime_children_are_claimed(self) -> bool:
        parent = self._runtime_parent.path
        try:
            children = tuple(parent.iterdir())
        except OSError:
            return False
        for child in children:
            if self._is_reparse_point(child) or not child.is_dir() or not self._is_exact_owned_root(child):
                return False
            expected_marker = _CLAIMED_MARKERS.get(child)
            if expected_marker is None:
                return False
            marker_path = child / ".johnny-stage-env-owner.json"
            if self._is_reparse_point(marker_path):
                return False
            try:
                marker = EnvironmentMarker.model_validate_json(marker_path.read_text(encoding="utf-8"))
            except (OSError, ValidationError, ValueError):
                return False
            if marker != expected_marker:
                return False
        return True

    def _remove_runtime_parent_if_empty(self) -> None:
        parent = self._runtime_parent.path
        if self._is_reparse_point(parent) or not parent.is_dir():
            return
        try:
            if next(parent.iterdir(), None) is None:
                parent.rmdir()
        except (OSError, StopIteration):
            return

    def _consume_fault(self, expected: EnvironmentFault) -> bool:
        if self._fault is not expected:
            return False
        self._fault = EnvironmentFault.NONE
        return True

    def _remove_new_root(self, root: EnvironmentLocator) -> None:
        try:
            if not root.path.exists() or self._is_reparse_point(root.path) or not self._is_exact_owned_root(root.path):
                return
            if self._tree_is_exact(root.path):
                self._remove_exact_tree(root.path)
                self._remove_runtime_parent_if_empty()
        except OSError:
            return

    def _tree_is_exact(self, directory: Path) -> bool:
        for child in directory.iterdir():
            if child.is_symlink() or self._is_reparse_point(child):
                return False
            resolved_child = child.resolve(strict=True)
            if not resolved_child.is_relative_to(directory):
                return False
            if child.is_dir() and not self._tree_is_exact(child):
                return False
        return True

    def _remove_exact_tree(self, directory: Path) -> None:
        for child in directory.iterdir():
            if child.is_dir():
                self._remove_exact_tree(child)
            else:
                child.unlink()
        directory.rmdir()

    @staticmethod
    def _is_reparse_point(path: Path) -> bool:
        try:
            attributes = path.lstat().st_file_attributes
        except FileNotFoundError:
            return False
        except OSError:
            return True
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
