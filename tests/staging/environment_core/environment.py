"""Exact provision and teardown implementation for Ticket 05S1 only."""

from __future__ import annotations

from pathlib import Path
import stat
import tempfile
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


class DisposableEnvironmentAllocator:
    """Creates marker-bound environment roots below one resolved OS temp parent."""

    def __init__(self, temporary_parent: EnvironmentLocator) -> None:
        validated_parent = EnvironmentLocator.model_validate(temporary_parent.model_dump())
        system_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        if validated_parent.path.resolve(strict=True) != system_parent:
            raise ValueError("environment allocator must use the resolved OS temporary directory")
        self._temporary_parent = EnvironmentLocator(value=str(system_parent))
        self._claimed_owner_values: set[str] = set()
        self._fault = EnvironmentFault.NONE

    @classmethod
    def from_system_temp(cls) -> DisposableEnvironmentAllocator:
        parent = Path(tempfile.gettempdir()).resolve(strict=True)
        return cls(EnvironmentLocator(value=str(parent)))

    def configure_fault(self, fault: EnvironmentFault) -> None:
        self._fault = EnvironmentFault(fault)

    def provision(self, owner: EnvironmentOwnerId) -> ProvisionResult:
        validated_owner = revalidate_owner(owner)
        if isinstance(validated_owner, ProvisionBlocked):
            return validated_owner
        if validated_owner.value in self._claimed_owner_values:
            return ProvisionBlocked(reason=ProvisionBlockReason.OWNER_REPLAYED)
        try:
            root = self._create_root()
        except OSError:
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
        self._remove_exact_tree(root)
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
            candidate = self._temporary_parent.path / f"{_ROOT_PREFIX}{uuid.uuid4().hex}"
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
            raise ValueError("new environment root must be an exact owned direct temporary child")

    def _is_exact_owned_root(self, root: Path) -> bool:
        return (
            root.is_absolute()
            and root.name.startswith(_ROOT_PREFIX)
            and root.parent.resolve(strict=True) == self._temporary_parent.path.resolve(strict=True)
            and root.exists()
        )

    def _consume_fault(self, expected: EnvironmentFault) -> bool:
        if self._fault is not expected:
            return False
        self._fault = EnvironmentFault.NONE
        return True

    def _remove_new_root(self, root: EnvironmentLocator) -> None:
        if not root.path.exists() or self._is_reparse_point(root.path) or not self._is_exact_owned_root(root.path):
            return
        if self._tree_is_exact(root.path):
            self._remove_exact_tree(root.path)

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
