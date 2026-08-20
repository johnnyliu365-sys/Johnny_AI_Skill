"""Executable E1-E4 closure for the disposable environment core."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
from typing import Callable
import unittest
from unittest.mock import patch

from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentLocator,
    EnvironmentMarker,
    EnvironmentOwnerId,
    ProvisionBlocked,
    ProvisionBlockReason,
    ProvisionedEnvironment,
    TeardownBlockReason,
    TeardownResult,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_PREFIX = "johnny-stage-env-"
ENVIRONMENT_KEYS = ("USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", "CODEX_HOME")
PROJECT_RUNTIME_ROOT = (REPOSITORY_ROOT / "tests" / ".johnny-runtime").resolve()
NON_EXACT_ROOT_NAMES = (
    "johnny-stage-env-prefix-similar",
    "johnny-stage-env-abcdef",
    "johnny-stage-env-" + ("a" * 33),
    "johnny-stage-env-" + ("g" * 32),
    "johnny-stage-env-" + ("A" * 32),
)
CR167_CELL = "test_cr167_non_exact_root_names_block_before_marker_read_or_delete"
RENAME_RETRY_DELAYS = (0.05, 0.1, 0.2, 0.4)


class DisposableEnvironmentCoreTests(unittest.TestCase):
    def test_r1_project_runtime_replaces_system_temp_factory(self) -> None:
        self.assertNotIn("from_system_temp", DisposableEnvironmentAllocator.__dict__)
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        result = allocator.provision(EnvironmentOwnerId(value="environment-owner-abcdefabcdefabcd"))
        if type(result) is not ProvisionedEnvironment:
            raise AssertionError("project-runtime provisioning must succeed")
        environment = result.environment
        self.addCleanup(self._assert_removed, allocator, environment)
        self.assertEqual(PROJECT_RUNTIME_ROOT, environment.root.path.parent)
        self.assertTrue(environment.root.path.is_relative_to(PROJECT_RUNTIME_ROOT))
        self.assertNotEqual(environment.root.path.parent, Path(tempfile.gettempdir()).resolve())

    def test_cr167_non_exact_root_names_block_before_marker_read_or_delete(self) -> None:
        for index, name in enumerate(NON_EXACT_ROOT_NAMES):
            with self.subTest(name=name):
                allocator = DisposableEnvironmentAllocator.from_project_runtime()
                lease = self._provisioned(allocator, f"environment-owner-{index + 1:016x}")
                original_root = lease.root.path
                invalid_root = original_root.with_name(name)
                invalid_marker_path = invalid_root / ".johnny-stage-env-owner.json"
                original_marker_bytes = lease.marker_path.read_bytes()
                try:
                    self._rename_past_transient_block(original_root, invalid_root)
                    invalid_locator = EnvironmentLocator(value=str(invalid_root.resolve(strict=True)))
                    invalid_marker = lease.marker.model_copy(update={"root": invalid_locator})
                    invalid_marker_path.write_text(invalid_marker.model_dump_json(warnings=False), encoding="utf-8")
                    invalid_lease = self._relocated_lease(lease, invalid_root, invalid_marker)
                    with patch.object(Path, "read_text", side_effect=AssertionError("marker read-through")) as marker_reads:
                        result = allocator.teardown(invalid_lease)
                    self.assertEqual(0, marker_reads.call_count)
                    self.assertEqual(TeardownStatus.BLOCKED, result.status)
                    self.assertIn(result.reason, (TeardownBlockReason.ROOT_ESCAPE, TeardownBlockReason.INVALID_LEASE))
                    self.assertTrue(invalid_root.exists())
                finally:
                    self._restore_exact_root_and_tear_down(
                        allocator,
                        lease,
                        original_root,
                        invalid_root,
                        invalid_marker_path,
                        original_marker_bytes,
                    )

    def test_cr168_delete_failure_is_finite_and_retains_live_claim(self) -> None:
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        lease = self._provisioned(allocator, "environment-owner-fedcbafedcbafedc")
        try:
            with patch.object(allocator, "_remove_exact_tree", side_effect=PermissionError("denied")):
                result = allocator.teardown(lease)
            self.assertEqual(TeardownStatus.BLOCKED, result.status)
            self.assertEqual(TeardownBlockReason.DELETE_FAILED, result.reason)
            self.assertTrue(lease.root.path.exists())
            self.assertTrue(lease.marker_path.exists())
        finally:
            self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(lease).status)

    def test_05_r1_a_transient_rename_block_leaves_no_orphan(self) -> None:
        self.addCleanup(self._purge_runtime_residue)
        attempts: list[Path] = []
        real_rename = Path.rename

        def blocked_once(path: Path, target: str | Path) -> Path:
            attempts.append(path)
            if len(attempts) == 1:
                raise PermissionError(13, "Access is denied", str(path), 5)
            return real_rename(path, target)

        with patch.object(Path, "rename", blocked_once):
            outcome = self._run_cr167()
        self.assertEqual([], self._reported(outcome.errors))
        self.assertEqual([], self._reported(outcome.failures))
        self.assertEqual(1, outcome.testsRun)
        self.assertGreater(len(attempts), 2 * len(NON_EXACT_ROOT_NAMES))
        self.assertEqual(set(), self._owned_environment_roots())
        self.assertFalse(PROJECT_RUNTIME_ROOT.exists())

    def test_05_r2_a_failed_cell_assertion_still_tears_the_environment_down(self) -> None:
        self.addCleanup(self._purge_runtime_residue)
        real_teardown = DisposableEnvironmentAllocator.teardown

        def teardown_claiming_removal(
            allocator: DisposableEnvironmentAllocator,
            lease: EnvironmentLease,
        ) -> TeardownResult:
            if lease.root.path.name in NON_EXACT_ROOT_NAMES:
                return TeardownResult(status=TeardownStatus.REMOVED, reason=TeardownBlockReason.NONE)
            return real_teardown(allocator, lease)

        with patch.object(DisposableEnvironmentAllocator, "teardown", teardown_claiming_removal):
            outcome = self._run_cr167()
        self.assertEqual([], self._reported(outcome.errors))
        self.assertEqual(len(NON_EXACT_ROOT_NAMES), len(outcome.failures))
        for reported in self._reported(outcome.failures):
            self.assertIn("TeardownStatus.BLOCKED", reported)
        self.assertEqual(set(), self._owned_environment_roots())
        self.assertFalse(PROJECT_RUNTIME_ROOT.exists())

    def test_05_r2_b_a_permanently_blocked_rename_still_tears_the_environment_down(self) -> None:
        self.addCleanup(self._purge_runtime_residue)

        def always_blocked(path: Path, target: str | Path) -> Path:
            raise PermissionError(13, "Access is denied", str(path), 5)

        with patch.object(Path, "rename", always_blocked):
            outcome = self._run_cr167()
        self.assertEqual([], self._reported(outcome.failures))
        self.assertEqual(len(NON_EXACT_ROOT_NAMES), len(outcome.errors))
        for reported in self._reported(outcome.errors):
            self.assertIn("WinError 5", reported)
        self.assertEqual(set(), self._owned_environment_roots())
        self.assertFalse(PROJECT_RUNTIME_ROOT.exists())

    def test_t1_two_distinct_owners_provision_unique_direct_project_roots_and_reject_replay(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionBlockReason, ProvisionedEnvironment
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        before = self._owned_environment_roots()
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        self.addCleanup(self._assert_runtime_absent)
        first = allocator.provision(EnvironmentOwnerId(value="environment-owner-0123456789abcdef"))
        second = allocator.provision(EnvironmentOwnerId(value="environment-owner-fedcba9876543210"))
        self.assertIsInstance(first, ProvisionedEnvironment)
        assert isinstance(first, ProvisionedEnvironment)
        self.addCleanup(self._teardown_exact, allocator, first.environment)
        self.assertIsInstance(second, ProvisionedEnvironment)
        assert isinstance(second, ProvisionedEnvironment)
        self.addCleanup(self._teardown_exact, allocator, second.environment)
        self.assertNotEqual(first.environment.environment_id, second.environment.environment_id)
        self.assertNotEqual(first.environment.root, second.environment.root)
        for environment in (first.environment, second.environment):
            self.assertEqual(PROJECT_RUNTIME_ROOT, environment.root.path.parent)
            self.assertNotEqual(environment.root.path.parent, Path(tempfile.gettempdir()).resolve())
            self.assertTrue(environment.root.path.is_relative_to(REPOSITORY_ROOT / "tests" / ".johnny-runtime"))
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

    def test_t2_overlay_has_exact_owned_keys_without_mutating_parent_environment(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionedEnvironment
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        snapshot = {key: os.environ.get(key) for key in ENVIRONMENT_KEYS}
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
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

        allocator = DisposableEnvironmentAllocator.from_project_runtime()
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

        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        lease = self._provisioned(allocator, "environment-owner-6666777788889999")
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(lease).status)
        target = Path(tempfile.mkdtemp(prefix="junction-target-"))
        target_marker = target / ".johnny-stage-env-owner.json"
        target_sentinel = target / "sentinel.bin"
        target_marker.write_text(lease.marker.model_dump_json(warnings=False), encoding="utf-8")
        target_sentinel.write_bytes(b"external junction target")
        runtime_parent = (REPOSITORY_ROOT / "tests" / ".johnny-runtime").resolve()
        runtime_parent.mkdir()
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
            if runtime_parent.exists():
                runtime_parent.rmdir()

    def test_t4_after_root_and_after_marker_faults_remove_only_owned_root_and_preserve_sibling(self) -> None:
        from tests.staging.environment_core.contracts import EnvironmentFault, EnvironmentOwnerId, ProvisionBlockReason
        from tests.staging.environment_core.environment import DisposableEnvironmentAllocator

        before = self._owned_environment_roots()
        with tempfile.NamedTemporaryFile(prefix="os-temp-sentinel-", delete=False) as sibling:
            sibling.write(b"unrelated sibling")
            sibling.flush()
            sibling_path = Path(sibling.name)
            allocator = DisposableEnvironmentAllocator.from_project_runtime()
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

    def test_r6_project_runtime_residue_blocks_and_preserves_exact_bytes(self) -> None:
        PROJECT_RUNTIME_ROOT.mkdir()
        unclaimed = PROJECT_RUNTIME_ROOT / "johnny-stage-env-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        sentinel = unclaimed / "residue.bin"
        unclaimed.mkdir()
        sentinel.write_bytes(b"unclaimed-project-residue")
        before = sentinel.read_bytes()
        try:
            allocator = DisposableEnvironmentAllocator.from_project_runtime()
            result = allocator.provision(EnvironmentOwnerId(value="environment-owner-9999888877776666"))
            self.assertIsInstance(result, ProvisionBlocked)
            assert isinstance(result, ProvisionBlocked)
            self.assertEqual(ProvisionBlockReason.INITIALIZATION_FAILED, result.reason)
            self.assertEqual(before, sentinel.read_bytes())
            self.assertTrue(unclaimed.exists())
        finally:
            sentinel.unlink()
            unclaimed.rmdir()
            PROJECT_RUNTIME_ROOT.rmdir()

    def test_r6_unexpected_sibling_and_malformed_parent_block_without_cleanup(self) -> None:
        PROJECT_RUNTIME_ROOT.mkdir()
        sibling = PROJECT_RUNTIME_ROOT / "unexpected-sibling"
        sibling.write_bytes(b"unexpected-sibling")
        try:
            allocator = DisposableEnvironmentAllocator.from_project_runtime()
            blocked = allocator.provision(EnvironmentOwnerId(value="environment-owner-1111000011110000"))
            self.assertIsInstance(blocked, ProvisionBlocked)
            assert isinstance(blocked, ProvisionBlocked)
            self.assertEqual(ProvisionBlockReason.INITIALIZATION_FAILED, blocked.reason)
            self.assertEqual(b"unexpected-sibling", sibling.read_bytes())
        finally:
            sibling.unlink()
            PROJECT_RUNTIME_ROOT.rmdir()

        PROJECT_RUNTIME_ROOT.write_bytes(b"malformed-runtime-parent")
        try:
            allocator = DisposableEnvironmentAllocator.from_project_runtime()
            blocked = allocator.provision(EnvironmentOwnerId(value="environment-owner-2222000022220000"))
            self.assertIsInstance(blocked, ProvisionBlocked)
            assert isinstance(blocked, ProvisionBlocked)
            self.assertEqual(ProvisionBlockReason.INITIALIZATION_FAILED, blocked.reason)
            self.assertEqual(b"malformed-runtime-parent", PROJECT_RUNTIME_ROOT.read_bytes())
        finally:
            PROJECT_RUNTIME_ROOT.unlink()

    @staticmethod
    def _rename_past_transient_block(source: Path, target: Path) -> None:
        """Survive a transient Windows share-mode block on rename (register B2/C9), finitely."""
        for delay in RENAME_RETRY_DELAYS:
            try:
                source.rename(target)
                return
            except PermissionError:
                time.sleep(delay)
        source.rename(target)

    def _restore_exact_root_and_tear_down(
        self,
        allocator: DisposableEnvironmentAllocator,
        lease: EnvironmentLease,
        original_root: Path,
        invalid_root: Path,
        invalid_marker_path: Path,
        original_marker_bytes: bytes,
    ) -> None:
        """Tear the lease down on every exit path, including one where the rename never happened."""
        if invalid_root.exists():
            invalid_marker_path.write_bytes(original_marker_bytes)
            try:
                self._rename_past_transient_block(invalid_root, original_root)
            except PermissionError:
                self._purge_runtime_residue()
                raise
        self.assertEqual(TeardownStatus.REMOVED, allocator.teardown(lease).status)

    @staticmethod
    def _run_cr167() -> unittest.TestResult:
        """Drive the real cr167 cell so its own teardown path is what gets observed."""
        outcome = unittest.TestResult()
        DisposableEnvironmentCoreTests(CR167_CELL).run(outcome)
        return outcome

    @staticmethod
    def _reported(entries: list[tuple[unittest.TestCase, str]]) -> list[str]:
        return [reported for _, reported in entries]

    @staticmethod
    def _purge_runtime_residue() -> None:
        """Last resort so one blocked cell cannot cascade into every later cell."""
        if not PROJECT_RUNTIME_ROOT.is_dir():
            return
        for child in PROJECT_RUNTIME_ROOT.iterdir():
            if not child.name.startswith(ENVIRONMENT_PREFIX) or child.is_symlink():
                continue
            if child.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                continue
            shutil.rmtree(child, ignore_errors=True)
        try:
            PROJECT_RUNTIME_ROOT.rmdir()
        except OSError:
            return

    @staticmethod
    def _relocated_lease(
        lease: EnvironmentLease,
        root: Path,
        marker: EnvironmentMarker,
    ) -> EnvironmentLease:
        relocated_children = tuple(
            child.model_copy(update={"absolute": EnvironmentLocator(value=str(root / child.relative.value))})
            for child in (
                lease.profile,
                lease.local_app_data,
                lease.roaming_app_data,
                lease.temporary,
                lease.codex_home,
            )
        )
        overlay_paths = (*relocated_children[:3], relocated_children[3], relocated_children[3], relocated_children[4])
        overlay = lease.overlay.model_copy(
            update={
                "entries": tuple(
                    entry.model_copy(update={"path": child.absolute})
                    for entry, child in zip(lease.overlay.entries, overlay_paths, strict=True)
                )
            }
        )
        return lease.model_copy(
            update={
                "root": EnvironmentLocator(value=str(root)),
                "root_relative": lease.root_relative.model_copy(update={"value": root.name}),
                "profile": relocated_children[0],
                "local_app_data": relocated_children[1],
                "roaming_app_data": relocated_children[2],
                "temporary": relocated_children[3],
                "codex_home": relocated_children[4],
                "overlay": overlay,
                "marker": marker,
            }
        )

    @staticmethod
    def _owned_environment_roots() -> set[Path]:
        parent = (REPOSITORY_ROOT / "tests" / ".johnny-runtime").resolve()
        if not parent.exists():
            return set()
        return {child for child in parent.iterdir() if child.is_dir() and child.name.startswith(ENVIRONMENT_PREFIX)}

    def _provisioned(self, allocator: DisposableEnvironmentAllocator, owner: str) -> EnvironmentLease:
        from tests.staging.environment_core.contracts import EnvironmentOwnerId, ProvisionedEnvironment

        result = allocator.provision(EnvironmentOwnerId(value=owner))
        self.assertIsInstance(result, ProvisionedEnvironment)
        assert isinstance(result, ProvisionedEnvironment)
        return result.environment

    @staticmethod
    def _assert_removed(allocator: DisposableEnvironmentAllocator, environment: EnvironmentLease) -> None:
        result = allocator.teardown(environment)
        if result.status is not TeardownStatus.REMOVED:
            raise AssertionError("the exact project-runtime lease did not tear down")
        if PROJECT_RUNTIME_ROOT.exists():
            raise AssertionError("the exact project-runtime parent was not removed")

    @staticmethod
    def _teardown_exact(allocator: DisposableEnvironmentAllocator, environment: EnvironmentLease) -> None:
        result = allocator.teardown(environment)
        if result.status is not TeardownStatus.REMOVED:
            raise AssertionError("the exact project-runtime lease did not tear down")

    @staticmethod
    def _assert_runtime_absent() -> None:
        if PROJECT_RUNTIME_ROOT.exists():
            raise AssertionError("the exact project-runtime parent was not removed")

    @staticmethod
    def _path_is(target: Path) -> Callable[[Path], bool]:
        def is_reparse(path: Path) -> bool:
            return path == target

        return is_reparse


if __name__ == "__main__":
    unittest.main()
