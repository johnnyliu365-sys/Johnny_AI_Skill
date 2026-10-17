"""Evidence tests for pure test-consumer inventory extraction."""

from __future__ import annotations

import unittest

from library.local_orchestration.test_dependency_inventory import (
    DeclaredTestCommand,
    DependencyKind,
    InventoryStatus,
    PythonSource,
    PythonTestConsumerInventory,
)


class TestDependencyInventoryTests(unittest.TestCase):
    def test_import_forms_and_literal_importlib_are_direct_consumers(self) -> None:
        inventory = PythonTestConsumerInventory(
            sources=(
                PythonSource(
                    "tests/test_consumer.py",
                    """
import tests.test_helper
from tests import test_helper as helper
from tests.test_helper import make_case
import importlib as il
il.import_module("tests.test_helper")
from importlib import import_module as load
load("tests.test_helper")
""",
                ),
            )
        ).retirement_inventory("tests/test_helper.py")

        self.assertEqual(InventoryStatus.COMPLETE, inventory.status)
        self.assertEqual(("tests/test_consumer.py",), inventory.direct_consumers)
        self.assertEqual(2, len(inventory.direct_edges))
        self.assertTrue(
            all(edge.consumed_ref == "tests.test_helper" for edge in inventory.direct_edges)
        )
        self.assertFalse(inventory.retirement_authorized)

    def test_importers_wrapper_and_declared_entry_are_traced_transitively(self) -> None:
        sources = (
            PythonSource("tests/test_consumer.py", "from tests import test_helper\n"),
            PythonSource(
                "tests/test_wrapper.py",
                "import subprocess\n"
                "import sys\n"
                "subprocess.run([sys.executable, '-m', 'tests.test_consumer'])\n",
            ),
            PythonSource("doc/runbooks/smoke.py", "from tests.test_helper import run\n"),
        )
        result = PythonTestConsumerInventory(
            sources,
            declared_commands=(
                DeclaredTestCommand(
                    "ci:consumer",
                    ("python", "-m", "pytest", "tests/test_consumer.py"),
                ),
            ),
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.COMPLETE, result.status)
        self.assertEqual(
            ("doc/runbooks/smoke.py", "tests/test_consumer.py"),
            result.direct_consumers,
        )
        self.assertEqual(
            ("ci:consumer", "tests/test_wrapper.py"),
            result.transitive_consumers,
        )
        self.assertIn(
            DependencyKind.SUBPROCESS,
            {edge.kind for edge in result.transitive_edges},
        )
        self.assertIn(
            DependencyKind.DECLARED_COMMAND,
            {edge.kind for edge in result.transitive_edges},
        )

    def test_literal_subprocess_target_is_a_direct_consumer(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(
                PythonSource(
                    "tests/test_wrapper.py",
                    "from subprocess import run as execute\n"
                    "import sys\n"
                    "execute([sys.executable, '-m', 'tests.test_helper'])\n",
                ),
            )
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.COMPLETE, result.status)
        self.assertEqual(("tests/test_wrapper.py",), result.direct_consumers)
        self.assertEqual(DependencyKind.SUBPROCESS, result.direct_edges[0].kind)

    def test_named_wrapper_import_is_traversed_as_a_transitive_consumer(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(
                PythonSource("tests/test_consumer.py", "from doc.runbooks import smoke\n"),
                PythonSource("doc/runbooks/smoke.py", "from tests.test_helper import run\n"),
            )
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.COMPLETE, result.status)
        self.assertEqual(("doc/runbooks/smoke.py",), result.direct_consumers)
        self.assertEqual(("tests/test_consumer.py",), result.transitive_consumers)

    def test_from_import_resolves_available_child_module_and_keeps_parent_edge(self) -> None:
        sources = (
            PythonSource("tests/test_consumer.py", "from tests.test_pkg import test_helper\n"),
            PythonSource("tests/test_pkg.py", ""),
            PythonSource("tests/test_pkg/test_helper.py", ""),
        )
        child = PythonTestConsumerInventory(sources).retirement_inventory(
            "tests.test_pkg.test_helper"
        )
        parent = PythonTestConsumerInventory(sources).retirement_inventory("tests.test_pkg")

        self.assertEqual(("tests/test_consumer.py",), child.direct_consumers)
        self.assertEqual(("tests/test_consumer.py",), parent.direct_consumers)

    def test_from_import_keeps_every_available_alias_child_module(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(
                PythonSource(
                    "tests/test_consumer.py",
                    "from doc.runbooks import smoke, audit\n",
                ),
                PythonSource("doc/runbooks/smoke.py", "from tests.test_helper import run\n"),
                PythonSource("doc/runbooks/audit.py", "from tests.test_helper import check\n"),
            )
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(
            ("doc/runbooks/audit.py", "doc/runbooks/smoke.py"),
            result.direct_consumers,
        )
        self.assertEqual(("tests/test_consumer.py",), result.transitive_consumers)

    def test_dynamic_import_and_dynamic_command_are_unresolved(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(
                PythonSource(
                    "tests/test_dynamic.py",
                    "import importlib\n"
                    "importlib.import_module('tests.' + name)\n"
                    "import subprocess\n"
                    "subprocess.run(command)\n",
                ),
            )
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.UNRESOLVED, result.status)
        self.assertEqual((), result.direct_consumers)
        self.assertEqual(
            {"DYNAMIC_IMPORT", "DYNAMIC_COMMAND"},
            {item.reason for item in result.unresolved},
        )
        self.assertFalse(result.retirement_authorized)

    def test_relative_test_import_and_unparseable_source_stay_unresolved(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(
                PythonSource("tests/test_relative.py", "from . import test_helper\n"),
                PythonSource("tests/test_broken.py", "from tests import\n"),
            )
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.UNRESOLVED, result.status)
        self.assertEqual(
            {"RELATIVE_TEST_IMPORT", "UNPARSEABLE_SOURCE"},
            {item.reason for item in result.unresolved},
        )

    def test_non_python_or_non_specific_declared_entry_is_unresolved(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(),
            declared_commands=(
                DeclaredTestCommand("ci:npm", ("npm", "test")),
                DeclaredTestCommand("ci:pytest-all", ("python", "-m", "pytest")),
            ),
        ).retirement_inventory("tests.test_helper")

        self.assertEqual(InventoryStatus.UNRESOLVED, result.status)
        self.assertEqual(
            {"ci:npm", "ci:pytest-all"},
            {item.source_ref for item in result.unresolved},
        )

    def test_independent_module_has_empty_inventory_without_retirement_authority(self) -> None:
        result = PythonTestConsumerInventory(
            sources=(PythonSource("tests/test_independent.py", "def test_ok(): pass\n"),)
        ).retirement_inventory("tests.test_independent")

        self.assertEqual(InventoryStatus.COMPLETE, result.status)
        self.assertEqual((), result.direct_edges)
        self.assertEqual((), result.transitive_edges)
        self.assertEqual((), result.unresolved)
        self.assertFalse(result.retirement_authorized)

    def test_source_and_command_refs_must_be_unique(self) -> None:
        with self.assertRaises(ValueError):
            PythonTestConsumerInventory(
                (
                    PythonSource("tests/test_a.py", ""),
                    PythonSource("tests/test_a.py", ""),
                )
            )
        with self.assertRaises(ValueError):
            PythonTestConsumerInventory(
                (),
                (
                    DeclaredTestCommand("ci:test", ("python", "-m", "tests.test_a")),
                    DeclaredTestCommand("ci:test", ("python", "-m", "tests.test_b")),
                ),
            )


if __name__ == "__main__":
    unittest.main()
