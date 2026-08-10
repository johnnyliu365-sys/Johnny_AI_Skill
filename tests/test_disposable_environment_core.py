"""Executable E1-E4 closure for the disposable environment core."""

from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import tempfile
from typing import Callable
import unittest
from unittest.mock import patch

from tests.staging.environment_core.contracts import EnvironmentLease, ProvisionBlocked
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_PREFIX = "johnny-stage-env-"
ENVIRONMENT_KEYS = ("USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", "CODEX_HOME")


class DisposableEnvironmentCoreTests(unittest.TestCase):
    def test_t1_two_distinct_owners_provision_unique_direct_temp_roots_and_reject_replay(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionBlockReason, ProvisionedEnvironment
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        before = self._owned_environment_roots()
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        first = allocator.provision(EnvironmentOwnerId(value="environment-owner-0123456789abcdef"))
        second = allocator.provision(EnvironmentOwnerId(value="environment-owner-fedcba9876543210"))
        self.assertIsInstance(first, ProvisionedEnvironment)
        self.assertIsInstance(second, ProvisionedEnvironment)
        assert isinstance(first, ProvisionedEnvironment)
        assert isinstance(second, ProvisionedEnvironment)
        self.assertNotEqual(first.environment.environment_id, second.environment.environment_id)
        self.assertNotEqual(first.environment.root, second.environment.root)
        for environment in (first.environment, second.environment):
            self.assertEqual(Path(tempfile.gettempdir()).resolve(strict=True), environment.root.path.parent)
            self.assertFalse(environment.root.path.is_relative_to(REPOSITORY_ROOT))
            self.assertTrue(environment.root.path.exists())
        replay = allocator.provision(EnvironmentOwnerId(value="environment-owner-0123456789abcdef"))
        self.assertIsInstance(replay, ProvisionBlocked)
        assert isinstance(replay, ProvisionBlocked)
        self.assertEqual(ProvisionBlockReason.OWNER_REPLAYED, replay.reason)
        for invalid in ("", " ", "owner", "environment-owner-0123456789abcdeg"):
            with self.subTest(invalid=invalid):
                malformed = EnvironmentOwnerId.model_construct(value=invalid)
                blocked = allocator.provision(malformed)
                self.assertIsInstance(blocked, ProvisionBlocked)
                assert isinstance(blocked, ProvisionBlocked)
                self.assertEqual(ProvisionBlockReason.INVALID_OWNER, blocked.reason)
        self.assertEqual(before | {first.environment.root.path, second.environment.root.path}, self._owned_environment_roots())
        self.assertEqual("REMOVED", allocator.teardown(first.environment).status.value)
        self.assertEqual("REMOVED", allocator.teardown(second.environment).status.value)
        self.assertEqual(before, self._owned_environment_roots())

    def test_t2_overlay_has_exact_owned_keys_without_mutating_parent_environment(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionedEnvironment
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        snapshot = {key: os.environ.get(key) for key in ENVIRONMENT_KEYS}
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        result = allocator.provision(EnvironmentOwnerId(value="environment-owner-0011223344556677"))
        self.assertIsInstance(result, ProvisionedEnvironment)
        assert isinstance(result, ProvisionedEnvironment)
        environment = result.environment
        self.assertEqual(ENVIRONMENT_KEYS, tuple(entry.key.value for entry in environment.overlay.entries))
        for entry in environment.overlay.entries:
            self.assertTrue(entry.path.path.is_relative_to(environment.root.path))
            self.assertTrue(entry.path.path.exists())
        self.assertEqual(snapshot, {key: os.environ.get(key) for key in ENVIRONMENT_KEYS})
        allocator.teardown(environment)
        self.assertEqual(snapshot, {key: os.environ.get(key) for key in ENVIRONMENT_KEYS})

    def test_t3_marker_reparse_and_child_escape_block_exact_teardown_then_intact_retry_works(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionedEnvironment, TeardownBlockReason, TeardownStatus
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        allocator = DisposableEnvironmentAllocator.from_system_temp()
        missing = self._provisioned(allocator, "environment-owner-1111222233334444")
        missing.marker_path.unlink()
        self.assertEqual(TeardownBlockReason.MARKER_MISSING, allocator.teardown(missing).reason)
        missing.marker_path.write_text(missing.marker.model_dump_json(warnings=False), encoding="utf-8")
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(missing).status)

        wrong = self._provisioned(allocator, "environment-owner-2222333344445555")
        wrong_marker = wrong.marker.model_copy(update={"environment_id": "environment-00000000000000000000000000000000"})
        wrong.marker_path.write_text(wrong_marker.model_dump_json(warnings=False), encoding="utf-8")
        self.assertEqual(TeardownBlockReason.MARKER_MISMATCH, allocator.teardown(wrong).reason)
        wrong.marker_path.write_text(wrong.marker.model_dump_json(warnings=False), encoding="utf-8")
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(wrong).status)

        reparse = self._provisioned(allocator, "environment-owner-3333444455556666")
        escape = reparse.root.path / "escape"
        escape.mkdir()
        try:
            with patch.object(Path, "is_symlink", self._path_is(escape)):
                self.assertEqual(TeardownBlockReason.CHILD_ESCAPE, allocator.teardown(reparse).reason)
            self.assertTrue(reparse.root.path.exists())
        finally:
            if escape.exists():
                escape.rmdir()
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(reparse).status)
        self.assertEqual(TeardownStatus.ALREADY_ABSENT, allocator.teardown(reparse).status)

    def test_t3_physical_root_junction_blocks_before_marker_read_through(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, TeardownBlockReason, TeardownStatus
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        allocator = DisposableEnvironmentAllocator.from_system_temp()
        lease = self._provisioned(allocator, "environment-owner-6666777788889999")
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(lease).status)
        target = Path(tempfile.mkdtemp(prefix="junction-target-"))
        target_marker = target / ".johnny-stage-env-owner.json"
        target_sentinel = target / "sentinel.bin"
        target_marker.write_text(lease.marker.model_dump_json(warnings=False), encoding="utf-8")
        target_sentinel.write_bytes(b"external junction target")
        try:
            junction = subprocess.run(
                ("cmd.exe", "/d", "/c", "mklink", "/J", str(lease.root.path), str(target)),
                shell=False,
                check=False,
                capture_output=True,
                encoding="utf-8",
                errors="strict",
                timeout=5,
            )
            self.assertEqual(0, junction.returncode, junction.stderr)
            attributes = lease.root.path.lstat().st_file_attributes
            self.assertNotEqual(0, attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
            with patch.object(Path, "read_text", side_effect=AssertionError("marker read-through")) as marker_reads:
                result = allocator.teardown(lease)
            self.assertEqual(0, marker_reads.call_count)
            self.assertEqual(TeardownStatus.BLOCKED, result.status)
            self.assertEqual(TeardownBlockReason.ROOT_REPARSE, result.reason)
            self.assertTrue(lease.root.path.exists())
            self.assertEqual(b"external junction target", target_sentinel.read_bytes())
        finally:
            if lease.root.path.exists():
                self.assertNotEqual(0, lease.root.path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
                lease.root.path.rmdir()
            target_marker.unlink()
            target_sentinel.unlink()
            target.rmdir()

    def test_t4_after_root_and_after_marker_faults_remove_only_owned_root_and_preserve_sibling(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentFault, EnvironmentOwnerId, ProvisionBlockReason
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        before = self._owned_environment_roots()
        with tempfile.NamedTemporaryFile(prefix="johnny-stage-env-sibling-", delete=False) as sibling:
            sibling.write(b"unrelated sibling")
            sibling.flush()
            sibling_path = Path(sibling.name)
            allocator = DisposableEnvironmentAllocator.from_system_temp()
            allocator.configure_fault(EnvironmentFault.AFTER_ROOT)
            after_root = allocator.provision(EnvironmentOwnerId(value="environment-owner-4444555566667777"))
            self.assertIsInstance(after_root, ProvisionBlocked)
            assert isinstance(after_root, ProvisionBlocked)
            self.assertEqual(ProvisionBlockReason.FAULT_AFTER_ROOT, after_root.reason)
            self.assertEqual(before, self._owned_environment_roots())
            allocator.configure_fault(EnvironmentFault.AFTER_MARKER)
            after_marker = allocator.provision(EnvironmentOwnerId(value="environment-owner-5555666677778888"))
            self.assertIsInstance(after_marker, ProvisionBlocked)
            assert isinstance(after_marker, ProvisionBlocked)
            self.assertEqual(ProvisionBlockReason.FAULT_AFTER_MARKER, after_marker.reason)
            self.assertEqual(before, self._owned_environment_roots())
        try:
            self.assertEqual(b"unrelated sibling", sibling_path.read_bytes())
        finally:
            sibling_path.unlink()

    @staticmethod
    def _owned_environment_roots() -> set[Path]:
        parent = Path(tempfile.gettempdir()).resolve(strict=True)
        return {child for child in parent.iterdir() if child.is_dir() and child.name.startswith(ENVIRONMENT_PREFIX)}

    def _provisioned(self, allocator: DisposableEnvironmentAllocator, owner: str) -> EnvironmentLease:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionedEnvironment

        result = allocator.provision(EnvironmentOwnerId(value=owner))
        self.assertIsInstance(result, ProvisionedEnvironment)
        assert isinstance(result, ProvisionedEnvironment)
        return result.environment

    @staticmethod
    def _path_is(target: Path) -> Callable[[Path], bool]:
        def is_reparse(path: Path) -> bool:
            return path == target

        return is_reparse


if __name__ == "__main__":
    unittest.main()
