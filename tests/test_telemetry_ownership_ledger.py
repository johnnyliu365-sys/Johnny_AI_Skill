"""High-assurance acceptance tests for the private per-stream ownership ledger."""

from __future__ import annotations

import ast
import hashlib
import json
import multiprocessing
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import library.local_orchestration.telemetry_storage.ownership_ledger as ledger_module
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.contracts import (
    TelemetryStorageLifecycle,
    TelemetryStorageRef,
)
from library.local_orchestration.telemetry_storage.ownership_ledger import (
    LedgerResolutionDecision,
    LocalTelemetryOwnershipLedger,
    TelemetryOwnershipLedgerBoundaryRejected,
    TelemetryOwnershipLedgerConflict,
    TelemetryOwnershipLedgerFound,
    TelemetryOwnershipLedgerNotFound,
    TelemetryOwnershipLedgerOwnershipMismatch,
    TelemetryOwnershipLedgerResult,
)


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = "prj_0123456789abcdef"
_OTHER_PROJECT = "prj_fedcba9876543210"
_REVISION = "rev-0123456789abcdef"
_NEXT_REVISION = "rev-fedcba9876543210"
_OTHER_NEXT_REVISION = "rev-1111111111111111"
_STALE_REVISION = "rev-2222222222222222"
_DOMAIN_SEPARATION = "johnny-telemetry-ownership-ledger-v1"


def _layout(root: str) -> JohnnyRootLayout:
    return JohnnyRootLayout(base=Path(root).resolve() / "johnny")


def _reference(
    *,
    storage_ref: str = "storage-alpha",
    project_id: str = _PROJECT,
    stream_id: str = "stream-alpha",
    ledger_ref: str = "ledger-alpha",
    revision: str = _REVISION,
    lifecycle: TelemetryStorageLifecycle = TelemetryStorageLifecycle.ACTIVE,
) -> TelemetryStorageRef:
    return TelemetryStorageRef(
        storage_ref=storage_ref,
        project_id=project_id,
        stream_id=stream_id,
        ownership_ledger_ref=ledger_ref,
        storage_revision=revision,
        lifecycle=lifecycle,
    )


def _json_entry(
    reference: TelemetryStorageRef,
    locator: str = "streams/alpha.jsonl",
) -> dict[str, object]:
    return {
        "storage_ref": {
            "storage_ref": reference.storage_ref,
            "project_id": reference.project_id,
            "stream_id": reference.stream_id,
            "ownership_ledger_ref": reference.ownership_ledger_ref,
            "storage_revision": reference.storage_revision,
            "lifecycle": reference.lifecycle.value,
        },
        "stream_locator": locator,
    }


def _entry_digest(reference: TelemetryStorageRef) -> str:
    identity = "\0".join(
        (
            _DOMAIN_SEPARATION,
            reference.storage_ref,
            reference.project_id,
            reference.stream_id,
            reference.ownership_ledger_ref,
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _entry_path(layout: JohnnyRootLayout, reference: TelemetryStorageRef) -> Path:
    return (
        layout.telemetry_root
        / "ownership-ledger"
        / "entries"
        / f"{_entry_digest(reference)}.json"
    )


def _legacy_path(layout: JohnnyRootLayout) -> Path:
    return layout.telemetry_root / "ownership-ledger" / "ledger.json"


def _write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def _seed(layout: JohnnyRootLayout, reference: TelemetryStorageRef) -> Path:
    path = _entry_path(layout, reference)
    _write_json(path, {"schema_version": 1, "entry": _json_entry(reference)})
    return path


def _bytes(path: Path) -> bytes:
    return path.read_bytes()


def _require_found(result: TelemetryOwnershipLedgerResult) -> TelemetryOwnershipLedgerFound:
    if not isinstance(result, TelemetryOwnershipLedgerFound):
        raise AssertionError(f"expected FOUND, got {result!r}")
    return result


def _cas_worker(
    root: str,
    reference_data: dict[str, str],
    lifecycle: str,
    revision: str,
    result_queue: multiprocessing.queues.Queue[tuple[str, str]],
) -> None:
    reference = _reference(
        storage_ref=reference_data["storage_ref"],
        project_id=reference_data["project_id"],
        stream_id=reference_data["stream_id"],
        ledger_ref=reference_data["ownership_ledger_ref"],
        revision=reference_data["storage_revision"],
    )
    result = LocalTelemetryOwnershipLedger(_layout(root)).compare_and_swap(
        reference,
        reference.project_id,
        reference.storage_revision,
        TelemetryStorageLifecycle(lifecycle),
        revision,
    )
    result_queue.put((reference.stream_id, result.decision.value))


def _reference_data(reference: TelemetryStorageRef) -> dict[str, str]:
    return {
        "storage_ref": reference.storage_ref,
        "project_id": reference.project_id,
        "stream_id": reference.stream_id,
        "ownership_ledger_ref": reference.ownership_ledger_ref,
        "storage_revision": reference.storage_revision,
    }


class OwnershipLedgerBehaviorTests(unittest.TestCase):
    """LRA1-LRA5: per-entry lookup, recovery, isolation and boundary behavior."""

    def test_lra1_exact_entry_lookup_and_cas_use_domain_separated_path(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            path = _seed(layout, reference)
            ledger = LocalTelemetryOwnershipLedger(layout)
            found = _require_found(
                ledger.resolve(reference, reference.project_id, reference.storage_revision)
            )
            self.assertEqual(found.entry.storage_ref, reference)
            self.assertEqual(found.entry.stream_locator, "streams/alpha.jsonl")
            self.assertEqual(path.name, f"{_entry_digest(reference)}.json")
            self.assertFalse(_legacy_path(layout).exists())
            self.assertNotIn(str(layout.base), found.model_dump_json())
            self.assertNotIn(str(path), found.model_dump_json())

            advanced = _require_found(
                ledger.compare_and_swap(
                    reference,
                    reference.project_id,
                    reference.storage_revision,
                    TelemetryStorageLifecycle.ACTIVE,
                    _NEXT_REVISION,
                )
            )
            self.assertEqual(advanced.entry.storage_ref.storage_revision, _NEXT_REVISION)
            self.assertEqual(advanced.entry.storage_ref.lifecycle, TelemetryStorageLifecycle.ACTIVE)
            self.assertTrue(path.exists())
            self.assertFalse(_legacy_path(layout).exists())

    def test_lra2_missing_identity_and_stale_normal_admission_never_create(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            ledger = LocalTelemetryOwnershipLedger(layout)
            missing = ledger.resolve(reference, reference.project_id, reference.storage_revision)
            self.assertIsInstance(missing, TelemetryOwnershipLedgerNotFound)
            self.assertFalse((layout.telemetry_root / "ownership-ledger").exists())

            path = _seed(layout, reference)
            before = _bytes(path)
            for candidate in (
                _reference(project_id=_OTHER_PROJECT),
                _reference(stream_id="stream-beta"),
                _reference(ledger_ref="ledger-beta"),
            ):
                with self.subTest(candidate=candidate):
                    result = ledger.resolve(candidate, candidate.project_id, candidate.storage_revision)
                    self.assertIsInstance(result, TelemetryOwnershipLedgerNotFound)
                    self.assertEqual(_bytes(path), before)
                    self.assertFalse(_entry_path(layout, candidate).exists())

            stale = ledger.resolve(reference, reference.project_id, _STALE_REVISION)
            self.assertIsInstance(stale, TelemetryOwnershipLedgerOwnershipMismatch)
            stale_cas = ledger.compare_and_swap(
                reference,
                reference.project_id,
                _STALE_REVISION,
                TelemetryStorageLifecycle.ACTIVE,
                _STALE_REVISION,
            )
            self.assertIsInstance(stale_cas, TelemetryOwnershipLedgerConflict)
            self.assertEqual(_bytes(path), before)

    def test_lra3_recovery_ignores_candidate_revision_but_normal_paths_do_not(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            path = _seed(layout, reference)
            ledger = LocalTelemetryOwnershipLedger(layout)
            _require_found(
                ledger.compare_and_swap(
                    reference,
                    reference.project_id,
                    reference.storage_revision,
                    TelemetryStorageLifecycle.DETACHED,
                    _NEXT_REVISION,
                )
            )
            after = _bytes(path)

            recovered = _require_found(ledger.resolve_current(reference))
            self.assertEqual(recovered.entry.storage_ref.storage_revision, _NEXT_REVISION)
            self.assertEqual(recovered.entry.storage_ref.lifecycle, TelemetryStorageLifecycle.DETACHED)
            self.assertEqual(_bytes(path), after)

            normal = ledger.resolve(reference, reference.project_id, reference.storage_revision)
            self.assertIsInstance(normal, TelemetryOwnershipLedgerOwnershipMismatch)
            stale_cas = ledger.compare_and_swap(
                reference,
                reference.project_id,
                reference.storage_revision,
                TelemetryStorageLifecycle.ACTIVE,
                _STALE_REVISION,
            )
            self.assertIsInstance(stale_cas, TelemetryOwnershipLedgerConflict)
            self.assertEqual(_bytes(path), after)

            current_reference = _reference(
                revision=_NEXT_REVISION,
                lifecycle=TelemetryStorageLifecycle.DETACHED,
            )
            closed_recovered = _require_found(ledger.resolve_current(current_reference))
            self.assertEqual(closed_recovered.entry.storage_ref.lifecycle, TelemetryStorageLifecycle.DETACHED)
            self.assertEqual(_bytes(path), after)

    def test_lra4_independent_processes_preserve_distinct_entry_post_states(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            first = _reference()
            second = _reference(stream_id="stream-beta")
            first_path = _seed(layout, first)
            second_path = _seed(layout, second)
            self.assertNotEqual(first_path, second_path)
            context = multiprocessing.get_context("spawn")
            result_queue = context.Queue()
            processes = (
                context.Process(
                    target=_cas_worker,
                    args=(temporary, _reference_data(first), "DETACHED", _NEXT_REVISION, result_queue),
                ),
                context.Process(
                    target=_cas_worker,
                    args=(temporary, _reference_data(second), "REMOVED", _OTHER_NEXT_REVISION, result_queue),
                ),
            )
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=20)
                self.assertFalse(process.is_alive())
                self.assertEqual(process.exitcode, 0)
            observed = {result_queue.get(timeout=5) for _ in processes}
            self.assertEqual(
                observed,
                {
                    (first.stream_id, LedgerResolutionDecision.FOUND.value),
                    (second.stream_id, LedgerResolutionDecision.FOUND.value),
                },
            )
            self.assertFalse(_legacy_path(layout).exists())
            first_document = json.loads(first_path.read_text(encoding="utf-8"))
            second_document = json.loads(second_path.read_text(encoding="utf-8"))
            self.assertEqual(first_document["entry"]["storage_ref"]["lifecycle"], "DETACHED")
            self.assertEqual(first_document["entry"]["storage_ref"]["storage_revision"], _NEXT_REVISION)
            self.assertEqual(second_document["entry"]["storage_ref"]["lifecycle"], "REMOVED")
            self.assertEqual(second_document["entry"]["storage_ref"]["storage_revision"], _OTHER_NEXT_REVISION)

    def test_lra5_legacy_malformed_identity_redirect_and_replace_are_boundary(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            legacy = _legacy_path(layout)
            _write_json(legacy, {"schema_version": 1, "entries": [_json_entry(reference)]})
            legacy_before = _bytes(legacy)
            ledger = LocalTelemetryOwnershipLedger(layout)
            self.assertIsInstance(
                ledger.resolve(reference, reference.project_id, reference.storage_revision),
                TelemetryOwnershipLedgerBoundaryRejected,
            )
            self.assertIsInstance(
                ledger.compare_and_swap(
                    reference,
                    reference.project_id,
                    reference.storage_revision,
                    TelemetryStorageLifecycle.ACTIVE,
                    _NEXT_REVISION,
                ),
                TelemetryOwnershipLedgerBoundaryRejected,
            )
            self.assertEqual(_bytes(legacy), legacy_before)
            self.assertNotIn(str(legacy), ledger.resolve_current(reference).model_dump_json())

            legacy.unlink()
            path = _entry_path(layout, reference)
            _write_json(path, {"schema_version": 1, "entry": _json_entry(reference), "extra": "reject"})
            malformed = ledger.resolve_current(reference)
            self.assertIsInstance(malformed, TelemetryOwnershipLedgerBoundaryRejected)
            self.assertNotIn("extra", malformed.model_dump_json())

            mismatched = _json_entry(reference)
            mismatched_storage_ref = mismatched["storage_ref"]
            assert isinstance(mismatched_storage_ref, dict)
            mismatched_storage_ref["stream_id"] = "stream-beta"
            _write_json(path, {"schema_version": 1, "entry": mismatched})
            identity_mismatch = ledger.resolve_current(reference)
            self.assertIsInstance(identity_mismatch, TelemetryOwnershipLedgerBoundaryRejected)

            real = Path(temporary).resolve() / "real"
            outside = Path(temporary).resolve() / "outside"
            real.mkdir()
            outside.mkdir()
            linked = Path(temporary).resolve() / "linked"
            try:
                linked.symlink_to(real, target_is_directory=True)
                redirected_context = None
            except OSError:
                redirected_context = patch.object(ledger_module, "resolves_within_root", return_value=False)
            redirected = LocalTelemetryOwnershipLedger(JohnnyRootLayout(base=linked))
            if redirected_context is None:
                redirected_result = redirected.resolve_current(reference)
            else:
                with redirected_context:
                    redirected_result = redirected.resolve_current(reference)
            self.assertIsInstance(redirected_result, TelemetryOwnershipLedgerBoundaryRejected)

            ancestor_base = Path(temporary).resolve() / "ancestor"
            ancestor_telemetry = ancestor_base / "telemetry"
            ancestor_outside = Path(temporary).resolve() / "ancestor-outside"
            ancestor_outside.mkdir()
            ancestor_telemetry.mkdir(parents=True)
            ownership_dir = ancestor_telemetry / "ownership-ledger"
            ownership_dir.mkdir()
            ancestor_link = ownership_dir / "entries"
            try:
                ancestor_link.symlink_to(ancestor_outside, target_is_directory=True)
                ancestor_context = None
            except OSError:
                ancestor_context = patch.object(ledger_module, "resolves_within_root", return_value=False)
            ancestor_ledger = LocalTelemetryOwnershipLedger(JohnnyRootLayout(base=ancestor_base))
            if ancestor_context is None:
                ancestor_result = ancestor_ledger.resolve_current(reference)
            else:
                with ancestor_context:
                    ancestor_result = ancestor_ledger.resolve_current(reference)
            self.assertIsInstance(ancestor_result, TelemetryOwnershipLedgerBoundaryRejected)

            valid_path = _seed(layout, reference)
            before = _bytes(valid_path)
            with patch.object(os, "replace", side_effect=OSError("replace injected")):
                failed = ledger.compare_and_swap(
                    reference,
                    reference.project_id,
                    reference.storage_revision,
                    TelemetryStorageLifecycle.ACTIVE,
                    _NEXT_REVISION,
                )
            self.assertIsInstance(failed, TelemetryOwnershipLedgerBoundaryRejected)
            self.assertEqual(_bytes(valid_path), before)
            self.assertEqual(tuple(valid_path.parent.glob("*.tmp")), ())


class OwnershipLedgerSourceTests(unittest.TestCase):
    """LRA6-LRA7: private source and target-owned element-index gates."""

    def test_lra6_source_is_private_typed_and_per_entry(self) -> None:
        source_path = (
            _REPOSITORY_ROOT
            / "library"
            / "local_orchestration"
            / "telemetry_storage"
            / "ownership_ledger.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            (node.module, tuple(alias.name for alias in node.names))
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertIn(("library.local_orchestration.path_containment", ("resolves_within_root",)), imports)
        self.assertIn(("library.local_orchestration.johnny_root_layout", ("JohnnyRootLayout",)), imports)
        self.assertIn("hashlib.sha256", source)
        for coordinate in ("storage_ref", "project_id", "stream_id", "ownership_ledger_ref"):
            self.assertIn(coordinate, source)
        self.assertIn("resolve_current", source)
        self.assertNotIn("JsonlContextUsageStore", source)
        self.assertNotIn("TelemetryStoragePort", source)
        self.assertNotIn("file_lock", source)
        self.assertNotIn("local_lock_adapter", source)
        self.assertNotIn("provider", source.casefold())
        self.assertNotIn("host", source.casefold())
        self.assertNotIn("Any", source)
        self.assertNotIn("cast(", source)
        self.assertNotIn("model_construct", source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("retry", source.casefold())
        self.assertNotIn("poll", source.casefold())
        self.assertNotIn("entries: tuple", source)
        self.assertIn("tempfile.mkstemp", source)
        self.assertIn("os.replace", source)
        self.assertFalse(
            any(
                isinstance(node, ast.FunctionDef)
                and node.name.casefold() in {"create", "provision", "register", "repair"}
                for node in ast.walk(tree)
            )
        )
        init_source = (
            _REPOSITORY_ROOT
            / "library"
            / "local_orchestration"
            / "telemetry_storage"
            / "__init__.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("ownership_ledger", init_source)
        self.assertIn("from .contracts import", init_source)
        resolve = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "resolve"
        )
        self.assertNotIn("Path", ast.unparse(resolve))
        recovery = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "resolve_current"
        )
        self.assertEqual(len(recovery.args.args), 2)
        annotation = recovery.args.args[1].annotation
        assert annotation is not None
        self.assertEqual(ast.unparse(annotation), "TelemetryStorageRef")

    def test_lra7_element_index_names_exact_private_closure(self) -> None:
        index = (
            _REPOSITORY_ROOT
            / "modules"
            / "element"
            / "python"
            / "context-load-telemetry"
            / "11-per-stream-ownership-ledger-readiness"
            / "README.md"
        )
        body = index.read_text(encoding="utf-8")
        for required in (
            "11-per-stream-ownership-ledger-readiness.md",
            "ownership_ledger.py",
            "test_telemetry_ownership_ledger.py",
            "path-containment@cf9e126",
            "a06c0fd",
            "096d471",
            "ADR-20260827-026",
        ):
            self.assertIn(required, body)
        self.assertNotIn("production provisioning", body)
        self.assertNotIn("transaction journal", body.casefold())


if __name__ == "__main__":
    unittest.main()
