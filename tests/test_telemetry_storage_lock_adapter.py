"""Acceptance and source checks for the local telemetry-storage lock port."""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import library.local_orchestration.telemetry_storage.local_lock_adapter as adapter_module
from library.local_orchestration.file_lock import ExclusiveFileLock
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.local_lock_adapter import (
    LocalTelemetryStorageLockAdapter,
    TelemetryStorageLockAdapterError,
)
from library.local_orchestration.telemetry_storage import (
    TelemetryStorageLockAcquired,
    TelemetryStorageLockContended,
    TelemetryStorageLockReleaseFailed,
    TelemetryStorageLockReleased,
    TelemetryStorageLockRequest,
    TelemetryStorageLockToken,
    TelemetryStorageRef,
    TelemetryStorageLifecycle,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = "prj_0123456789abcdef"
_REVISION = "rev-0123456789abcdef"
_STALE_REVISION = "rev-fedcba9876543210"

_HOLDER_CHILD = '''\
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.local_lock_adapter import (
    LocalTelemetryStorageLockAdapter,
)
from library.local_orchestration.telemetry_storage import (
    TelemetryStorageLockAcquired,
    TelemetryStorageLockRequest,
    TelemetryStorageRef,
    TelemetryStorageLifecycle,
)

layout = JohnnyRootLayout(base=Path(sys.argv[2]))
reference = TelemetryStorageRef(
    storage_ref="storage-alpha",
    project_id="prj_0123456789abcdef",
    stream_id="stream-alpha",
    ownership_ledger_ref="ledger-alpha",
    storage_revision="rev-0123456789abcdef",
    lifecycle=TelemetryStorageLifecycle.ACTIVE,
)
request = TelemetryStorageLockRequest(
    storage_ref=reference,
    expected_project_id="prj_0123456789abcdef",
    expected_storage_revision="rev-0123456789abcdef",
)
adapter = LocalTelemetryStorageLockAdapter(layout)
result = adapter.try_acquire(request)
if not isinstance(result, TelemetryStorageLockAcquired):
    print("not-held", flush=True)
    raise SystemExit(2)
print("held", flush=True)
sys.stdin.readline()
adapter.release(result.lock_token)
print("released", flush=True)
'''


def _reference(
    *,
    storage_ref: str = "storage-alpha",
    project_id: str = _PROJECT,
    stream_id: str = "stream-alpha",
    ledger_ref: str = "ledger-alpha",
    revision: str = _REVISION,
) -> TelemetryStorageRef:
    return TelemetryStorageRef(
        storage_ref=storage_ref,
        project_id=project_id,
        stream_id=stream_id,
        ownership_ledger_ref=ledger_ref,
        storage_revision=revision,
        lifecycle=TelemetryStorageLifecycle.ACTIVE,
    )


def _request(reference: TelemetryStorageRef) -> TelemetryStorageLockRequest:
    return TelemetryStorageLockRequest(
        storage_ref=reference,
        expected_project_id=reference.project_id,
        expected_storage_revision=reference.storage_revision,
    )


def _require_acquired(
    result: TelemetryStorageLockAcquired | TelemetryStorageLockContended,
) -> TelemetryStorageLockAcquired:
    if not isinstance(result, TelemetryStorageLockAcquired):
        raise AssertionError(f"expected acquisition, got {result!r}")
    return result


def _start_holder(base: Path) -> subprocess.Popen[str]:
    script = base / "holder_child.py"
    script.write_text(_HOLDER_CHILD, encoding="utf-8")
    return subprocess.Popen(
        (sys.executable, str(script), str(_REPOSITORY_ROOT), str(base / "johnny")),
        cwd=str(base),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )


def _await_line(process: subprocess.Popen[str], expected: str) -> None:
    assert process.stdout is not None
    line = process.stdout.readline().strip()
    if line != expected:
        errors = process.stderr.read() if process.stderr else ""
        raise AssertionError(f"child said {line!r}, expected {expected!r}: {errors}")


def _reap(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.kill()
    process.wait()


class LocalTelemetryStorageLockAdapterTests(unittest.TestCase):
    """LPA1-LPA6: the adapter's typed, bounded behavior."""

    def test_lpa1_acquires_exact_identity_and_releases_original_token(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve() / "johnny")
            reference = _reference()
            adapter = LocalTelemetryStorageLockAdapter(layout)

            result = _require_acquired(adapter.try_acquire(_request(reference)))
            token = result.lock_token
            self.assertEqual(
                token.model_dump(),
                {
                    "lock_ref": token.lock_ref,
                    "storage_ref": reference.storage_ref,
                    "project_id": reference.project_id,
                    "stream_id": reference.stream_id,
                    "ownership_ledger_ref": reference.ownership_ledger_ref,
                    "storage_revision": reference.storage_revision,
                },
            )
            self.assertRegex(token.lock_ref, r"^lock-[0-9a-f]{64}$")
            self.assertNotIn(str(layout.base), token.model_dump_json())
            self.assertNotIn(".lock", token.model_dump_json())
            lock_files = tuple(layout.telemetry_root.rglob("*.lock"))
            self.assertEqual(len(lock_files), 1)
            self.assertEqual(lock_files[0].parent, layout.telemetry_root / "storage-locks")
            self.assertIsInstance(adapter.release(token), TelemetryStorageLockReleased)

    def test_lpa2_real_independent_holder_contends_without_witness(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            request = _request(_reference())
            holder = _start_holder(base)
            contender = LocalTelemetryStorageLockAdapter(
                JohnnyRootLayout(base=base / "johnny")
            )
            try:
                _await_line(holder, "held")
                result = contender.try_acquire(request)
                self.assertIsInstance(result, TelemetryStorageLockContended)
                self.assertNotIsInstance(result, TelemetryStorageLockAcquired)
                self.assertFalse(hasattr(result, "lock_token"))
                self.assertFalse(hasattr(result, "contender_handle"))

                assert holder.stdin is not None
                holder.stdin.write("release\n")
                holder.stdin.flush()
                _await_line(holder, "released")
                self.assertEqual(holder.wait(timeout=30), 0)

                fresh = _require_acquired(contender.try_acquire(request))
                self.assertIsInstance(contender.release(fresh.lock_token), TelemetryStorageLockReleased)
            finally:
                _reap(holder)

    def test_lpa3_revision_is_not_key_but_each_identity_coordinate_is(self) -> None:
        with TemporaryDirectory() as temporary:
            adapter = LocalTelemetryStorageLockAdapter(
                JohnnyRootLayout(base=Path(temporary).resolve() / "johnny")
            )
            current = _reference()
            stale = _reference(revision=_STALE_REVISION)
            acquired = _require_acquired(adapter.try_acquire(_request(current)))
            self.assertIsInstance(
                adapter.try_acquire(_request(stale)), TelemetryStorageLockContended
            )
            self.assertIsInstance(adapter.release(acquired.lock_token), TelemetryStorageLockReleased)

            changed_references = (
                _reference(storage_ref="storage-beta"),
                _reference(project_id="prj_fedcba9876543210"),
                _reference(stream_id="stream-beta"),
                _reference(ledger_ref="ledger-beta"),
            )
            for changed in changed_references:
                with self.subTest(changed=changed):
                    first = _require_acquired(adapter.try_acquire(_request(current)))
                    second = _require_acquired(adapter.try_acquire(_request(changed)))
                    self.assertIsInstance(adapter.release(first.lock_token), TelemetryStorageLockReleased)
                    self.assertIsInstance(adapter.release(second.lock_token), TelemetryStorageLockReleased)

    def test_lpa4_only_exact_original_token_can_release_and_replay_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve() / "johnny")
            request = _request(_reference())
            adapter = LocalTelemetryStorageLockAdapter(layout)
            other = LocalTelemetryStorageLockAdapter(layout)
            acquired = _require_acquired(adapter.try_acquire(request))
            original = acquired.lock_token

            reconstructed = TelemetryStorageLockToken(**original.model_dump())
            self.assertIsInstance(adapter.release(reconstructed), TelemetryStorageLockReleaseFailed)
            self.assertIsInstance(adapter.try_acquire(request), TelemetryStorageLockContended)

            stale = TelemetryStorageLockToken(
                **{
                    **original.model_dump(),
                    "storage_revision": _STALE_REVISION,
                }
            )
            self.assertIsInstance(adapter.release(stale), TelemetryStorageLockReleaseFailed)
            self.assertIsInstance(adapter.try_acquire(request), TelemetryStorageLockContended)

            mismatched = TelemetryStorageLockToken(
                **{
                    **original.model_dump(),
                    "storage_ref": "storage-mismatch",
                }
            )
            self.assertIsInstance(adapter.release(mismatched), TelemetryStorageLockReleaseFailed)
            self.assertIsInstance(other.release(original), TelemetryStorageLockReleaseFailed)
            self.assertIsInstance(adapter.release(original), TelemetryStorageLockReleased)
            self.assertIsInstance(adapter.release(original), TelemetryStorageLockReleaseFailed)

            fresh = _require_acquired(other.try_acquire(request))
            self.assertIsInstance(other.release(fresh.lock_token), TelemetryStorageLockReleased)

    def test_lpa5_redirected_roots_and_lock_ancestors_are_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            real = base / "real"
            outside = base / "outside"
            real.mkdir()
            outside.mkdir()
            linked = base / "linked"
            try:
                linked.symlink_to(real, target_is_directory=True)
                redirected_symlink = True
            except OSError:
                redirected_symlink = False

            redirected = LocalTelemetryStorageLockAdapter(
                JohnnyRootLayout(base=linked)
            )

            def assert_redirected_rejected() -> None:
                with self.assertRaises(TelemetryStorageLockAdapterError) as redirected_error:
                    redirected.try_acquire(_request(_reference()))
                self.assertEqual(str(redirected_error.exception), "telemetry lock boundary rejected")
                self.assertNotIn(str(linked), str(redirected_error.exception))

            if redirected_symlink:
                assert_redirected_rejected()
            else:
                with patch.object(
                    adapter_module, "resolves_within_root", return_value=False
                ):
                    assert_redirected_rejected()

            normal_base = base / "normal"
            telemetry = normal_base / "telemetry"
            telemetry.mkdir(parents=True)
            storage_locks = telemetry / "storage-locks"
            try:
                storage_locks.symlink_to(outside, target_is_directory=True)
                ancestor_symlink = True
            except OSError:
                ancestor_symlink = False
            ancestor_adapter = LocalTelemetryStorageLockAdapter(
                JohnnyRootLayout(base=normal_base)
            )

            def assert_ancestor_rejected() -> None:
                with self.assertRaises(TelemetryStorageLockAdapterError) as ancestor_error:
                    ancestor_adapter.try_acquire(_request(_reference()))
                self.assertEqual(str(ancestor_error.exception), "telemetry lock boundary rejected")
                self.assertNotIn(str(outside), str(ancestor_error.exception))

            if ancestor_symlink:
                assert_ancestor_rejected()
            else:
                with patch.object(
                    adapter_module, "resolves_within_root", return_value=False
                ):
                    assert_ancestor_rejected()
            self.assertEqual(tuple(outside.iterdir()), ())

    def test_lpa6_non_contention_io_is_sanitized_and_release_failure_clears_state(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve() / "johnny")
            request = _request(_reference())
            with patch.object(Path, "mkdir", side_effect=OSError("mkdir injected")):
                with self.assertRaises(TelemetryStorageLockAdapterError) as mkdir_error:
                    LocalTelemetryStorageLockAdapter(layout).try_acquire(request)
            self.assertEqual(str(mkdir_error.exception), "telemetry lock unavailable")
            self.assertNotIn("mkdir injected", str(mkdir_error.exception))

            with patch.object(Path, "open", side_effect=OSError("open injected")):
                with self.assertRaises(TelemetryStorageLockAdapterError) as open_error:
                    LocalTelemetryStorageLockAdapter(layout).try_acquire(request)
            self.assertEqual(str(open_error.exception), "telemetry lock unavailable")

            with patch.object(
                ExclusiveFileLock, "try_acquire", side_effect=OSError("acquire injected")
            ):
                with self.assertRaises(TelemetryStorageLockAdapterError) as acquire_error:
                    LocalTelemetryStorageLockAdapter(layout).try_acquire(request)
            self.assertEqual(str(acquire_error.exception), "telemetry lock unavailable")

            adapter = LocalTelemetryStorageLockAdapter(layout)
            acquired = _require_acquired(adapter.try_acquire(request))
            original_release = ExclusiveFileLock.release
            held_lock = adapter._held[acquired.lock_token.lock_ref][0]

            def release_then_fail() -> None:
                original_release(held_lock)
                raise OSError("release injected")

            with patch.object(ExclusiveFileLock, "release", side_effect=release_then_fail):
                failed = adapter.release(acquired.lock_token)
            self.assertIsInstance(failed, TelemetryStorageLockReleaseFailed)
            self.assertEqual(failed.storage_ref, request.storage_ref.storage_ref)
            self.assertNotIn("release injected", failed.model_dump_json())

            fresh = _require_acquired(adapter.try_acquire(request))
            self.assertIsInstance(adapter.release(fresh.lock_token), TelemetryStorageLockReleased)


class LocalTelemetryStorageLockAdapterSourceTests(unittest.TestCase):
    """LPA7-LPA8: source boundary, element index, and exact changed paths."""

    def test_lpa7_source_has_selected_imports_and_two_pre_effect_containment_checks(self) -> None:
        source_path = (
            _REPOSITORY_ROOT
            / "library"
            / "local_orchestration"
            / "telemetry_storage"
            / "local_lock_adapter.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            (node.module, tuple(alias.name for alias in node.names))
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertIn(
            (
                "library.local_orchestration.file_lock",
                ("ExclusiveFileLock", "FileLockAcquireDecision"),
            ),
            imports,
        )
        self.assertIn(
            ("library.local_orchestration.path_containment", ("resolves_within_root",)),
            imports,
        )
        self.assertIn(
            ("library.local_orchestration.johnny_root_layout", ("JohnnyRootLayout",)),
            imports,
        )
        self.assertIn(("hashlib", ("sha256",)), imports)
        containment_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "resolves_within_root"
        ]
        self.assertEqual(len(containment_calls), 2)
        digest_method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_request_digest"
        )
        digest_source = ast.get_source_segment(source, digest_method)
        assert digest_source is not None
        self.assertNotIn("storage_revision", digest_source)
        self.assertLess(source.index("storage_ref.storage_ref"), source.index("storage_ref.project_id"))
        self.assertLess(source.index("storage_ref.project_id"), source.index("storage_ref.stream_id"))
        self.assertLess(source.index("storage_ref.stream_id"), source.index("storage_ref.ownership_ledger_ref"))
        self.assertIn("held[1] is not token", source)
        self.assertNotIn("TelemetryStorageRef.model_validate", source)
        self.assertNotIn("print(", source)
        self.assertNotIn("json", source)

        open_lock = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_open_lock"
        )
        resolve_lines = sorted(
            node.lineno
            for node in ast.walk(open_lock)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "resolves_within_root"
        )
        mkdir_line = next(
            node.lineno
            for node in ast.walk(open_lock)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "mkdir"
        )
        file_open_line = next(
            node.lineno
            for node in ast.walk(open_lock)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "ExclusiveFileLock"
        )
        self.assertEqual(len(resolve_lines), 2)
        self.assertLess(resolve_lines[0], mkdir_line)
        self.assertLess(resolve_lines[1], file_open_line)

        init_path = (
            _REPOSITORY_ROOT
            / "library"
            / "local_orchestration"
            / "telemetry_storage"
            / "__init__.py"
        )
        init_source = init_path.read_text(encoding="utf-8")
        init_tree = ast.parse(init_source)
        init_imports = [
            node
            for node in init_tree.body
            if isinstance(node, ast.ImportFrom)
        ]
        self.assertTrue(init_imports)
        self.assertTrue(
            all(node.level == 1 and node.module == "contracts" for node in init_imports)
        )
        self.assertNotIn("local_lock_adapter", init_source)
        self.assertNotIn("LocalTelemetryStorageLockAdapter", init_source)

    def test_lpa8_element_index_and_four_file_boundary_are_present(self) -> None:
        element = (
            _REPOSITORY_ROOT
            / "modules"
            / "element"
            / "python"
            / "context-load-telemetry"
            / "09-local-telemetry-storage-lock-port"
            / "README.md"
        )
        body = element.read_text(encoding="utf-8")
        for required in (
            "09-local-telemetry-storage-lock-port.md",
            "local_lock_adapter.py",
            "test_telemetry_storage_lock_adapter.py",
            "exclusive-file-lock@60d2ab0",
            "path-containment@ccefa77",
            "ADR-20260827-022",
        ):
            self.assertIn(required, body)
        self.assertNotIn("POSIX", body)
        self.assertNotIn("msvcrt", body)


if __name__ == "__main__":
    unittest.main()
