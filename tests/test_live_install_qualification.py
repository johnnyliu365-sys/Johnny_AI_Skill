"""L7 end-to-end live install/uninstall qualification.

Gated by `JOHNNY_LIVE_QUAL=1`: it performs real network wheel downloads and
real venv creation inside a disposable workspace, so the ordinary suite
skips it. Owner download consent for this line was granted on 2026-08-19.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from library.local_orchestration.bootstrap_install import run_bootstrap
from library.local_orchestration.johnny_root_layout import (
    FileUninstallLedgerStore,
    JohnnyRootLayout,
)
from library.local_orchestration.live_uninstall_composition import (
    run_live_uninstall,
)
from library.local_orchestration.plugin_bundle_builder import (
    PluginBundleBuilder,
    PluginBundleBuildRequest,
    PluginBundleBuildStatus,
)
from library.local_orchestration.plugin_install_transaction import (
    InstallDependencyPlan,
    InstallDependencyPlanEntry,
    InstallEffectOutcomeStatus,
)
from library.local_orchestration.plugin_uninstall_transaction import (
    UninstallLedgerReadStatus,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.venv_effect_port import RealVenvEffectPort
from library.local_orchestration.windows_package_manifest import (
    build_payload_manifest,
)
from tests.staging.plugin_distribution_vita.harness import delete_disposable_tree
from tests.test_plugin_distribution_bundle import _run_git

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CANDIDATE_ZIP = "johnny-ai-skill-0.4.5.zip"


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


def _tampered_plan() -> InstallDependencyPlan:
    plan = _plan()
    first = plan.entries[0]
    original = first.artifact_sha256s[0]
    flipped = ("0" if original[0] != "0" else "1") + original[1:]
    tampered = InstallDependencyPlanEntry(
        name=first.name,
        version=first.version,
        artifact_sha256s=(flipped, *first.artifact_sha256s[1:]),
    )
    return InstallDependencyPlan(
        python_constraint=plan.python_constraint,
        entries=(tampered, *plan.entries[1:]),
    )


def _staging_residue() -> set[str]:
    temp = Path(tempfile.gettempdir())
    return {path.name for path in temp.glob("johnny-install-staging-*")}


@unittest.skipUnless(
    os.environ.get("JOHNNY_LIVE_QUAL") == "1",
    "JOHNNY_LIVE_QUAL not set: real downloads and venv creation are gated",
)
class LiveInstallQualificationTests(unittest.TestCase):
    """Q1-Q5: the whole live chain against disposables, nothing simulated."""

    workspace: Path
    workspace_exists_after: bool
    staging_before: set[str]
    staging_after: set[str]
    scratch_create_status: InstallEffectOutcomeStatus
    scratch_remove_ok: bool
    scratch_residue_absent: bool
    tampered_status: InstallEffectOutcomeStatus
    tampered_residue_absent: bool
    bootstrap_exit: int
    installed_shape_ok: bool
    ledger_receipt: str | None
    entry_status_payload: dict[str, object] | None
    uninstall_exit: int
    uninstall_payload: dict[str, object]
    repeat_exit: int
    repeat_status: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.staging_before = _staging_residue()
        cls.workspace = Path(tempfile.mkdtemp(prefix="johnny-live-qual-"))
        try:
            cls._run_pipeline()
        finally:
            delete_disposable_tree(cls.workspace)
            cls.workspace_exists_after = cls.workspace.exists()
            cls.staging_after = _staging_residue()

    @classmethod
    def _run_pipeline(cls) -> None:
        # Build from a clean clone of HEAD so the live checkout's bytecode
        # or editor residue can never dirty the deterministic build.
        source = cls.workspace / "src"
        _run_git(_REPO_ROOT, "clone", "--no-hardlinks", str(_REPO_ROOT), str(source))
        head = _run_git(source, "rev-parse", "HEAD")
        manifest = build_payload_manifest(
            source, head, build_approved_runtime_lock()
        )
        dist = cls.workspace / "dist"
        dist.mkdir()
        build_result = PluginBundleBuilder().build(
            PluginBundleBuildRequest(
                repository_root=source, output_root=dist, manifest=manifest
            )
        )
        assert build_result.status is PluginBundleBuildStatus.BUNDLED, (
            build_result.failure
        )
        bundle_zip = dist / _CANDIDATE_ZIP

        # Q2: real from-scratch venv creation, removal, and the real
        # supply-chain rejection with a tampered pin.
        layout_a = JohnnyRootLayout(base=(cls.workspace / "root-a").resolve())
        port_a = RealVenvEffectPort(layout_a)
        cls.scratch_create_status = port_a.create("attempt-q2-good", _plan()).status
        cls.scratch_remove_ok = port_a.remove("venv")
        cls.scratch_residue_absent = not layout_a.venv_root.exists()
        cls.tampered_status = port_a.create(
            "attempt-q2-tampered", _tampered_plan()
        ).status
        cls.tampered_residue_absent = not layout_a.venv_root.exists()

        # Q1/Q3: the full bootstrap-to-transaction chain into a fresh root.
        root_b = (cls.workspace / "root-b").resolve()
        cls.bootstrap_exit = run_bootstrap(bundle_zip, root_b)
        layout_b = JohnnyRootLayout(base=root_b)
        cls.installed_shape_ok = all(
            (
                layout_b.venv_python.is_file(),
                (layout_b.plugin_root / "payload-manifest.json").is_file(),
                (layout_b.launcher_root / "johnny-router.ps1").is_file(),
                layout_b.runtime_entry.is_file(),
                (layout_b.queue_root / ".johnny-owned").is_file(),
                (layout_b.telemetry_root / ".johnny-owned").is_file(),
                layout_b.journal_path.is_file(),
            )
        )
        ledger_read = FileUninstallLedgerStore(layout_b.ledger_path).read()
        cls.ledger_receipt = (
            ledger_read.ledger.receipt_id
            if ledger_read.status is UninstallLedgerReadStatus.PRESENT
            and ledger_read.ledger is not None
            else None
        )

        # Q4: the installed runtime proves itself through its own entry chain.
        cls.entry_status_payload = None
        if cls.installed_shape_ok:
            completed = subprocess.run(
                (
                    str(layout_b.venv_python),
                    str(layout_b.runtime_entry),
                    "status",
                ),
                capture_output=True,
                shell=False,
                timeout=120,
            )
            if completed.returncode == 0:
                lines = completed.stdout.decode(
                    "utf-8", errors="replace"
                ).splitlines()
                cls.entry_status_payload = json.loads(lines[-1]) if lines else None

        # Q5: the real uninstall runs THROUGH THE INSTALLED LAUNCHER, exactly
        # as an owner would invoke it, so the venv self-deletion guard (the
        # launcher executes uninstall from a disposable venv copy) is proven
        # here rather than discovered on a real machine again.
        launcher = layout_b.launcher_root / "johnny-router.ps1"
        environment = dict(os.environ)
        environment["JOHNNY_ROOT"] = str(root_b)
        completed_uninstall = subprocess.run(
            (
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(launcher),
                "uninstall",
            ),
            capture_output=True,
            shell=False,
            timeout=300,
            env=environment,
        )
        cls.uninstall_exit = completed_uninstall.returncode
        lines = [
            line
            for line in completed_uninstall.stdout.decode(
                "utf-8", errors="replace"
            ).splitlines()
            if line.strip()
        ]
        cls.uninstall_payload = json.loads(lines[-1])
        repeat_captured = io.StringIO()
        with redirect_stdout(repeat_captured):
            cls.repeat_exit = run_live_uninstall(root_b)
        repeat_lines = [
            line
            for line in repeat_captured.getvalue().splitlines()
            if line.strip()
        ]
        cls.repeat_status = str(json.loads(repeat_lines[-1])["status"])

    def test_q1_bootstrap_chain_installs_end_to_end(self) -> None:
        self.assertEqual(self.bootstrap_exit, 0)
        self.assertTrue(self.installed_shape_ok)
        self.assertIsNotNone(self.ledger_receipt)
        assert self.ledger_receipt is not None
        self.assertTrue(self.ledger_receipt.startswith("receipt-live-"))

    def test_q2_real_venv_creation_and_supply_chain_rejection(self) -> None:
        self.assertIs(
            self.scratch_create_status, InstallEffectOutcomeStatus.COMPLETED
        )
        self.assertTrue(self.scratch_remove_ok)
        self.assertTrue(self.scratch_residue_absent)
        self.assertIs(
            self.tampered_status, InstallEffectOutcomeStatus.HASH_MISMATCH
        )
        self.assertTrue(self.tampered_residue_absent)

    def test_q3_no_staging_residue_survives(self) -> None:
        self.assertEqual(self.staging_after, self.staging_before)
        self.assertFalse(self.workspace_exists_after)

    def test_q4_installed_runtime_proves_its_own_chain(self) -> None:
        payload = self.entry_status_payload
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload.get("status"), "OK")
        self.assertEqual(payload.get("plugin_version"), "0.4.5")
        self.assertIs(payload.get("venv_present"), True)
        self.assertIs(payload.get("launcher_present"), True)
        self.assertIs(payload.get("ledger_present"), True)

    def test_q5_real_uninstall_reaches_zero_residue_and_repeats(self) -> None:
        self.assertEqual(self.uninstall_exit, 0)
        self.assertEqual(self.uninstall_payload["status"], "REMOVED")
        self.assertEqual(self.uninstall_payload["remaining"], [])
        self.assertTrue(self.uninstall_payload["root_deleted"])
        self.assertEqual(self.repeat_exit, 0)
        self.assertEqual(self.repeat_status, "NOT_INSTALLED")


if __name__ == "__main__":
    unittest.main()
