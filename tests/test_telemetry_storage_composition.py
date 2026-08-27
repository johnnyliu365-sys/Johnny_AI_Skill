"""High-assurance acceptance tests for the private telemetry composition graph."""

from __future__ import annotations

import ast
import inspect
import tempfile
import unittest
from pathlib import Path

import library.local_orchestration.telemetry_storage.composition as composition_module
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.telemetry_storage.contracts import (
    TelemetryStoragePort,
    TelemetryStorageRequest,
    TelemetryStorageResponse,
)
from library.local_orchestration.telemetry_storage.johnny_owned_adapter import (
    JohnnyOwnedTelemetryStorageAdapter,
)
from library.local_orchestration.telemetry_storage.local_lock_adapter import (
    LocalTelemetryStorageLockAdapter,
)
from library.local_orchestration.telemetry_storage.ownership_ledger import (
    LocalTelemetryOwnershipLedger,
)


_ROOT = Path(__file__).resolve().parents[1]
_COMPOSITION = (
    _ROOT
    / "library"
    / "local_orchestration"
    / "telemetry_storage"
    / "composition.py"
)
_INDEX = (
    _ROOT
    / "modules"
    / "element"
    / "python"
    / "context-load-telemetry"
    / "13-private-storage-composition-binding"
    / "README.md"
)


class _FakeTelemetryPort(TelemetryStoragePort):
    """A direct typed caller seam that does not use production composition."""

    def execute(self, request: TelemetryStorageRequest) -> TelemetryStorageResponse:
        raise AssertionError(f"the direct fake must not execute: {request!r}")


def _accept_port(port: TelemetryStoragePort) -> TelemetryStoragePort:
    return port


class TelemetryStorageCompositionBehaviorTests(unittest.TestCase):
    """CPA1-CPA3: exact graph binding, lifetime and direct fake seam."""

    def test_cpa1_factory_binds_one_exact_graph_to_supplied_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary) / "johnny")
            port = composition_module.compose_johnny_owned_telemetry_storage(layout)
            self.assertIsInstance(port, TelemetryStoragePort)
            self.assertIsInstance(port, JohnnyOwnedTelemetryStorageAdapter)
            assert isinstance(port, JohnnyOwnedTelemetryStorageAdapter)
            self.assertIs(port._layout, layout)
            self.assertIsInstance(port._ledger, LocalTelemetryOwnershipLedger)
            self.assertIsInstance(port._lock, LocalTelemetryStorageLockAdapter)
            assert isinstance(port._ledger, LocalTelemetryOwnershipLedger)
            assert isinstance(port._lock, LocalTelemetryStorageLockAdapter)
            self.assertIs(port._ledger._layout, layout)
            self.assertIs(port._lock._layout, layout)

    def test_cpa2_calls_are_fresh_and_have_no_filesystem_effect(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary) / "johnny")
            self.assertFalse(layout.base.exists())
            self.assertFalse(layout.telemetry_root.exists())
            first = composition_module.compose_johnny_owned_telemetry_storage(layout)
            second = composition_module.compose_johnny_owned_telemetry_storage(layout)
            self.assertIsInstance(first, JohnnyOwnedTelemetryStorageAdapter)
            self.assertIsInstance(second, JohnnyOwnedTelemetryStorageAdapter)
            assert isinstance(first, JohnnyOwnedTelemetryStorageAdapter)
            assert isinstance(second, JohnnyOwnedTelemetryStorageAdapter)
            self.assertIsNot(first, second)
            self.assertIsNot(first._ledger, second._ledger)
            self.assertIsNot(first._lock, second._lock)
            self.assertIs(first._layout, layout)
            self.assertIs(second._layout, layout)
            self.assertFalse(layout.base.exists())
            self.assertFalse(layout.telemetry_root.exists())

    def test_cpa3_typed_fake_can_be_passed_directly_without_factory(self) -> None:
        fake = _FakeTelemetryPort()
        self.assertIs(_accept_port(fake), fake)
        self.assertEqual(
            tuple(inspect.signature(composition_module.compose_johnny_owned_telemetry_storage).parameters),
            ("layout",),
        )


class TelemetryStorageCompositionSourceTests(unittest.TestCase):
    """CPA4-CPA5: source direction, public surface and element index."""

    def test_cpa4_source_has_exact_imports_and_no_effect_direction(self) -> None:
        source = _COMPOSITION.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            (node.module, tuple(alias.name for alias in node.names))
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module != "__future__"
        }
        self.assertEqual(
            imports,
            {
                (
                    "library.local_orchestration.johnny_root_layout",
                    ("JohnnyRootLayout",),
                ),
                (
                    "library.local_orchestration.telemetry_storage.contracts",
                    ("TelemetryStoragePort",),
                ),
                (
                    "library.local_orchestration.telemetry_storage.johnny_owned_adapter",
                    ("JohnnyOwnedTelemetryStorageAdapter",),
                ),
                (
                    "library.local_orchestration.telemetry_storage.local_lock_adapter",
                    ("LocalTelemetryStorageLockAdapter",),
                ),
                (
                    "library.local_orchestration.telemetry_storage.ownership_ledger",
                    ("LocalTelemetryOwnershipLedger",),
                ),
            },
        )
        functions = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual([node.name for node in functions], ["compose_johnny_owned_telemetry_storage"])
        all_assignments = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
        ]
        self.assertEqual(len(all_assignments), 1)
        self.assertIn("compose_johnny_owned_telemetry_storage", ast.unparse(all_assignments[0].value))
        factory_source = ast.get_source_segment(source, functions[0])
        assert factory_source is not None
        construction_order = (
            "LocalTelemetryOwnershipLedger(layout)",
            "LocalTelemetryStorageLockAdapter(layout)",
            "JohnnyOwnedTelemetryStorageAdapter(layout, ledger, lock)",
        )
        positions = tuple(factory_source.index(expression) for expression in construction_order)
        self.assertEqual(positions, tuple(sorted(positions)))
        for forbidden in (
            "JsonlContextUsageStore",
            "Path",
            "import os",
            "os.",
            "environ",
            "mkdir",
            "open(",
            "execute(",
            "cache",
            "singleton",
            "provider",
            "host",
            "runner",
            "queue",
            "retry",
            "sleep",
            "poll",
            "Any",
            "cast(",
            "dict",
            "mapping",
            "getattr(",
            "setattr(",
            "__dict__",
        ):
            self.assertNotIn(forbidden.casefold(), source.casefold())
        package_init = (
            _ROOT / "library" / "local_orchestration" / "telemetry_storage" / "__init__.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("compose_johnny_owned_telemetry_storage", package_init)

    def test_cpa5_element_index_names_exact_private_boundary(self) -> None:
        body = _INDEX.read_text(encoding="utf-8")
        for required in (
            "13-private-storage-composition-binding.md",
            "composition.py",
            "test_telemetry_storage_composition.py",
            "contracts.py",
            "096d471",
            "e05f03a",
            "c359d92",
            "ADR-20260827-028",
        ):
            self.assertIn(required, body)
        self.assertIn("neither identity provisioning", body.casefold())
        self.assertIn("storage-operation", body.casefold())
        self.assertIn("invocation", body.casefold())


if __name__ == "__main__":
    unittest.main()
