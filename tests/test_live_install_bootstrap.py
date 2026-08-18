"""L5 closure tests: bootstrap gates, requirement parity, composition gates."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.bootstrap_install import (
    _render_requirements,
    run_bootstrap,
)
from library.local_orchestration.johnny_live_install import run_live_install
from library.local_orchestration.plugin_install_transaction import (
    InstallDependencyPlan,
    InstallDependencyPlanEntry,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.venv_effect_port import (
    render_locked_requirements,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _staging_residue() -> set[str]:
    temp = Path(tempfile.gettempdir())
    return {path.name for path in temp.glob("johnny-install-staging-*")}


class BootstrapRequirementsParityTests(unittest.TestCase):
    def test_stdlib_rendering_matches_the_canonical_port(self) -> None:
        lock = build_approved_runtime_lock()
        plan = InstallDependencyPlan(
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
        canonical = render_locked_requirements(plan)
        stdlib_rendered = _render_requirements(
            _REPO_ROOT / "requirements-runtime.lock"
        )
        self.assertEqual(stdlib_rendered, canonical)

    def test_unreadable_lock_returns_none(self) -> None:
        with TemporaryDirectory() as temporary:
            broken = Path(temporary) / "broken.lock"
            broken.write_text("{not json", encoding="utf-8")
            self.assertIsNone(_render_requirements(broken))
            self.assertIsNone(_render_requirements(Path(temporary) / "absent"))


class RunBootstrapGateTests(unittest.TestCase):
    def test_missing_bundle_blocks_before_any_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "jr"
            captured = io.StringIO()
            with redirect_stdout(captured):
                code = run_bootstrap(Path(temporary) / "absent.zip", root)
            self.assertEqual(code, 2)
            self.assertIn("BUNDLE_NOT_FOUND", captured.getvalue())
            self.assertFalse(root.exists())

    def test_present_venv_blocks_before_any_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            bundle.write_bytes(b"placeholder")
            root = base / "jr"
            (root / "venv").mkdir(parents=True)
            (root / "venv" / "keep.txt").write_text("keep", encoding="utf-8")
            captured = io.StringIO()
            with redirect_stdout(captured):
                code = run_bootstrap(bundle, root)
            self.assertEqual(code, 2)
            self.assertIn("VENV_ALREADY_PRESENT", captured.getvalue())
            self.assertTrue((root / "venv" / "keep.txt").exists())

    def test_unreadable_bundle_blocks_and_cleans_staging(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            bundle.write_bytes(b"this is not a zip archive")
            before = _staging_residue()
            captured = io.StringIO()
            with redirect_stdout(captured):
                code = run_bootstrap(bundle, base / "jr")
            self.assertEqual(code, 2)
            self.assertIn("BUNDLE_UNREADABLE", captured.getvalue())
            self.assertEqual(_staging_residue(), before)


class RunLiveInstallGateTests(unittest.TestCase):
    def test_unreadable_manifest_blocks_before_any_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            bundle = base / "bundle.zip"
            bundle.write_bytes(b"not a zip")
            captured = io.StringIO()
            with redirect_stdout(captured):
                code = run_live_install(bundle, base / "jr")
            self.assertEqual(code, 2)
            self.assertIn("MANIFEST_UNREADABLE", captured.getvalue())
            self.assertFalse((base / "jr" / "plugin").exists())


if __name__ == "__main__":
    unittest.main()
