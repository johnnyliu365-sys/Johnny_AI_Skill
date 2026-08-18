"""L2 closure tests: finite failure semantics of the real venv effect port.

The real venv-plus-download happy path and the real hash-mismatch rejection
run in the L7 end-to-end qualification, gated by `JOHNNY_LIVE_QUAL`.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.plugin_install_transaction import (
    InstallDependencyPlan,
    InstallDependencyPlanEntry,
    InstallEffectOutcomeStatus,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.venv_effect_port import (
    RealVenvEffectPort,
    render_locked_requirements,
)


def _plan() -> InstallDependencyPlan:
    lock = build_approved_runtime_lock()
    return InstallDependencyPlan(
        python_constraint=lock.python_constraint,
        entries=tuple(
            InstallDependencyPlanEntry(
                name=dependency.normalized_name,
                version=dependency.exact_version,
                artifact_sha256s=tuple(
                    artifact.sha256 for artifact in dependency.artifacts
                ),
            )
            for dependency in lock.dependencies
        ),
    )


class RenderLockedRequirementsTests(unittest.TestCase):
    def test_rendering_is_exact_sorted_and_hash_locked(self) -> None:
        text = render_locked_requirements(_plan())
        lines = [line for line in text.splitlines() if not line.startswith("#")]
        self.assertEqual(len(lines), 6)
        self.assertEqual(lines, sorted(lines))
        for line in lines:
            with self.subTest(line=line.split(" ")[0]):
                self.assertIn("==", line)
                self.assertIn("--hash=sha256:", line)
        self.assertIn(
            "pydantic==2.13.4 --hash=sha256:45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba",
            lines,
        )


class RealVenvEffectPortTests(unittest.TestCase):
    def test_missing_bootstrap_python_is_unavailable_with_no_residue(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = RealVenvEffectPort(
                layout,
                bootstrap_command=("johnny-nonexistent-python-launcher",),
                create_timeout_seconds=30,
            )
            outcome = port.create("attempt-l2-01", _plan())
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertIsNone(outcome.receipt)
            self.assertFalse(layout.venv_root.exists())

    def test_populated_venv_location_is_never_clobbered(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            layout.venv_root.mkdir(parents=True)
            foreign = layout.venv_root / "foreign-user-file.txt"
            foreign.write_text("keep", encoding="utf-8")
            port = RealVenvEffectPort(layout, bootstrap_command=("whatever",))
            outcome = port.create("attempt-l2-02", _plan())
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertTrue(foreign.exists())
            self.assertEqual(foreign.read_text(encoding="utf-8"), "keep")

    def test_failing_bootstrap_leaves_no_partial_venv(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            # A real interpreter invoked with arguments venv cannot accept
            # exits nonzero after the target may exist; residue must clear.
            port = RealVenvEffectPort(
                layout,
                bootstrap_command=("py", "-3.11", "-c", "import sys; sys.exit(3)", "--"),
                create_timeout_seconds=60,
            )
            outcome = port.create("attempt-l2-03", _plan())
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertFalse(layout.venv_root.exists())

    def test_remove_semantics_are_receipt_bound_and_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = RealVenvEffectPort(layout)
            with self.subTest(case="foreign_receipt_refused"):
                self.assertFalse(port.remove("plugin"))
            with self.subTest(case="absent_is_idempotent_true"):
                self.assertTrue(port.remove("venv"))
            with self.subTest(case="existing_directory_removed"):
                nested = layout.venv_root / "Scripts"
                nested.mkdir(parents=True)
                (nested / "python.exe").write_bytes(b"stub")
                self.assertTrue(port.remove("venv"))
                self.assertFalse(layout.venv_root.exists())


if __name__ == "__main__":
    unittest.main()
