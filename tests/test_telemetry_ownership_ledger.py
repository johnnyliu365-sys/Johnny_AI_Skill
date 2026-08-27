"""High-assurance acceptance tests for the private ownership-ledger CAS seam."""

from __future__ import annotations

import ast
import json
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
    TelemetryOwnershipLedgerClosed,
    TelemetryOwnershipLedgerConflict,
    TelemetryOwnershipLedgerEntry,
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
_STALE_REVISION = "rev-1111111111111111"


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


def _json_entry(reference: TelemetryStorageRef, locator: str = "streams/alpha.jsonl") -> dict[str, object]:
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


def _seed(layout: JohnnyRootLayout, *entries: dict[str, object]) -> Path:
    path = layout.telemetry_root / "ownership-ledger" / "ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    document: dict[str, object] = {"schema_version": 1, "entries": list(entries)}
    path.write_text(
        json.dumps(document, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return path


def _bytes(path: Path) -> bytes:
    return path.read_bytes()


def _require_found(result: TelemetryOwnershipLedgerResult) -> TelemetryOwnershipLedgerFound:
    if not isinstance(result, TelemetryOwnershipLedgerFound):
        raise AssertionError(f"expected FOUND, got {result!r}")
    return result


class OwnershipLedgerBehaviorTests(unittest.TestCase):
    """OLA1-OLA5: lookup, ownership, lifecycle and atomic CAS behavior."""

    def test_ola1_exact_preprovisioned_lookup_returns_entry_without_path(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            path = _seed(layout, _json_entry(reference))
            result = _require_found(
                LocalTelemetryOwnershipLedger(layout).resolve(
                    reference, reference.project_id, reference.storage_revision
                )
            )
            self.assertEqual(result.entry.storage_ref, reference)
            self.assertEqual(result.entry.stream_locator, "streams/alpha.jsonl")
            self.assertNotIn(str(layout.base), result.model_dump_json())
            self.assertNotIn(str(path), result.model_dump_json())

    def test_ola2_missing_and_mismatch_never_create_or_change_bytes(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            ledger = LocalTelemetryOwnershipLedger(layout)
            reference = _reference()
            missing = ledger.resolve(reference, reference.project_id, reference.storage_revision)
            self.assertIsInstance(missing, TelemetryOwnershipLedgerNotFound)
            path = layout.telemetry_root / "ownership-ledger" / "ledger.json"
            self.assertFalse(path.exists())

            path = _seed(layout, _json_entry(reference))
            before = _bytes(path)
            cases = (
                _reference(project_id=_OTHER_PROJECT),
                _reference(stream_id="stream-beta"),
                _reference(ledger_ref="ledger-beta"),
            )
            for candidate in cases:
                with self.subTest(candidate=candidate):
                    result = ledger.resolve(candidate, candidate.project_id, candidate.storage_revision)
                    self.assertIsInstance(result, TelemetryOwnershipLedgerOwnershipMismatch)
                    self.assertEqual(_bytes(path), before)
            stale = ledger.resolve(reference, reference.project_id, _STALE_REVISION)
            self.assertIsInstance(stale, TelemetryOwnershipLedgerOwnershipMismatch)
            self.assertEqual(_bytes(path), before)

    def test_ola3_matching_cas_is_one_update_and_stale_repeat_is_conflict(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            path = _seed(layout, _json_entry(reference))
            ledger = LocalTelemetryOwnershipLedger(layout)
            first = _require_found(
                ledger.compare_and_swap(
                    reference,
                    reference.project_id,
                    reference.storage_revision,
                    TelemetryStorageLifecycle.DETACHED,
                    _NEXT_REVISION,
                )
            )
            self.assertEqual(first.entry.storage_ref.lifecycle, TelemetryStorageLifecycle.DETACHED)
            self.assertEqual(first.entry.storage_ref.storage_revision, _NEXT_REVISION)
            after_first = _bytes(path)

            stale = ledger.compare_and_swap(
                reference,
                reference.project_id,
                reference.storage_revision,
                TelemetryStorageLifecycle.ACTIVE,
                _STALE_REVISION,
            )
            self.assertIsInstance(stale, TelemetryOwnershipLedgerConflict)
            self.assertEqual(_bytes(path), after_first)

    def test_ola4_closed_entries_reject_lookup_and_cas_without_change(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            detached = _reference(storage_ref="storage-detached", lifecycle=TelemetryStorageLifecycle.DETACHED)
            removed = _reference(storage_ref="storage-removed", lifecycle=TelemetryStorageLifecycle.REMOVED)
            path = _seed(layout, _json_entry(detached), _json_entry(removed))
            before = _bytes(path)
            ledger = LocalTelemetryOwnershipLedger(layout)
            for reference in (detached, removed):
                with self.subTest(reference=reference):
                    lookup = ledger.resolve(reference, reference.project_id, reference.storage_revision)
                    self.assertIsInstance(lookup, TelemetryOwnershipLedgerClosed)
                    cas = ledger.compare_and_swap(
                        reference,
                        reference.project_id,
                        reference.storage_revision,
                        TelemetryStorageLifecycle.ACTIVE,
                        _NEXT_REVISION,
                    )
                    self.assertIsInstance(cas, TelemetryOwnershipLedgerClosed)
                    self.assertEqual(_bytes(path), before)

    def test_ola5_malformed_locator_redirect_and_failed_replace_are_boundary(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            reference = _reference()
            for locator in ("../outside.jsonl", "/absolute.jsonl", "C:\\outside.jsonl"):
                path = _seed(layout, _json_entry(reference, locator))
                malformed = LocalTelemetryOwnershipLedger(layout).resolve(
                    reference, reference.project_id, reference.storage_revision
                )
                self.assertIsInstance(malformed, TelemetryOwnershipLedgerBoundaryRejected)
                self.assertNotIn(str(path), malformed.model_dump_json())

            path.write_text("{not-json", encoding="utf-8")
            malformed_json = LocalTelemetryOwnershipLedger(layout).resolve(
                reference, reference.project_id, reference.storage_revision
            )
            self.assertIsInstance(malformed_json, TelemetryOwnershipLedgerBoundaryRejected)
            self.assertNotIn("not-json", malformed_json.model_dump_json())

            real = Path(temporary).resolve() / "real"
            outside = Path(temporary).resolve() / "outside"
            real.mkdir()
            outside.mkdir()
            linked = Path(temporary).resolve() / "linked"
            try:
                linked.symlink_to(real, target_is_directory=True)
                redirected_context = None
            except OSError:
                redirected_context = patch.object(
                    ledger_module, "resolves_within_root", return_value=False
                )
            redirected = LocalTelemetryOwnershipLedger(
                JohnnyRootLayout(base=linked)
            )
            if redirected_context is None:
                redirected_result = redirected.resolve(
                    reference, reference.project_id, reference.storage_revision
                )
            else:
                with redirected_context:
                    redirected_result = redirected.resolve(
                        reference, reference.project_id, reference.storage_revision
                    )
            self.assertIsInstance(redirected_result, TelemetryOwnershipLedgerBoundaryRejected)
            self.assertNotIn(str(linked), redirected_result.model_dump_json())

            ancestor_base = Path(temporary).resolve() / "ancestor"
            ancestor_telemetry = ancestor_base / "telemetry"
            ancestor_telemetry.mkdir(parents=True)
            ancestor_link = ancestor_telemetry / "ownership-ledger"
            try:
                ancestor_link.symlink_to(outside, target_is_directory=True)
                ancestor_context = None
            except OSError:
                ancestor_context = patch.object(
                    ledger_module, "resolves_within_root", return_value=False
                )
            ancestor_ledger = LocalTelemetryOwnershipLedger(
                JohnnyRootLayout(base=ancestor_base)
            )
            if ancestor_context is None:
                ancestor_result = ancestor_ledger.resolve(
                    reference, reference.project_id, reference.storage_revision
                )
            else:
                with ancestor_context:
                    ancestor_result = ancestor_ledger.resolve(
                        reference, reference.project_id, reference.storage_revision
                    )
            self.assertIsInstance(ancestor_result, TelemetryOwnershipLedgerBoundaryRejected)
            self.assertNotIn(str(outside), ancestor_result.model_dump_json())

            valid_path = _seed(layout, _json_entry(reference))
            before = _bytes(valid_path)
            with patch.object(os, "replace", side_effect=OSError("replace injected")):
                failed = LocalTelemetryOwnershipLedger(layout).compare_and_swap(
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
    """OLA6-OLA7: source boundary and element-index checks."""

    def test_ola6_source_is_private_typed_and_contains_no_forbidden_surface(self) -> None:
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
        self.assertNotIn("file_lock", source)
        self.assertNotIn("local_lock_adapter", source)
        self.assertNotIn("TelemetryStoragePort", source)
        self.assertNotIn("JsonlContextUsageStore", source)
        self.assertNotIn("provider", source.casefold())
        self.assertNotIn("host", source.casefold())
        self.assertNotIn("Any", source)
        self.assertNotIn("cast(", source)
        self.assertNotIn("model_construct", source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("retry", source.casefold())
        self.assertNotIn("poll", source.casefold())
        self.assertIn("tempfile.mkstemp", source)
        self.assertIn("os.replace", source)
        self.assertFalse(
            any(
                isinstance(node, ast.FunctionDef)
                and node.name.casefold() in {"create", "provision", "register"}
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
        self.assertEqual(
            sum(
                1
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "resolves_within_root"
            ),
            2,
        )
        constructor = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "__init__"
        )
        self.assertEqual(len(constructor.args.args), 2)
        annotation = constructor.args.args[1].annotation
        assert annotation is not None
        self.assertEqual(ast.unparse(annotation), "JohnnyRootLayout")

    def test_ola7_element_index_names_exact_private_closure(self) -> None:
        index = (
            _REPOSITORY_ROOT
            / "modules"
            / "element"
            / "python"
            / "context-load-telemetry"
            / "10-private-ownership-ledger-cas"
            / "README.md"
        )
        body = index.read_text(encoding="utf-8")
        for required in (
            "10-private-ownership-ledger-cas.md",
            "ownership_ledger.py",
            "test_telemetry_ownership_ledger.py",
            "path-containment@cf9e126",
            "ADR-20260827-025",
            "public provision API",
        ):
            self.assertIn(required, body)
        self.assertNotIn("production provisioning", body)


if __name__ == "__main__":
    unittest.main()
