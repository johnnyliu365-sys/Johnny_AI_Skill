"""Regressions for the six blocking findings of the branch review.

Each cell fails if its correction is reverted, so a finding cannot come back
silently.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import windows_supervision_composition
from library.local_orchestration.bootstrap_install import (
    _APPROVED_LOCK_DIGEST,
    _render_requirements,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.live_uninstall_composition import (
    LiveOwnedStatePort,
)
from library.local_orchestration.payload_effect_ports import (
    RealPluginPayloadEffectPort,
)
from library.local_orchestration.plugin_install_transaction import (
    InstallEffectOutcomeStatus,
)
from library.local_orchestration.plugin_uninstall_transaction import (
    OwnedStateKind,
    OwnedStateRecord,
    UninstallOwnershipProbe,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.wake_capability import (
    WakeCapabilityFailure,
    WakeCapabilityStatus,
    WakeCommandConfig,
    probe_wake_capability,
    wake_config_path,
)
from library.local_orchestration.windows_package_manifest import (
    PayloadManifest,
    PayloadManifestEntry,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _make_reparse_point(link: Path, target: Path) -> bool:
    """Create a directory reparse point; junctions need no elevation."""

    try:
        link.symlink_to(target, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    completed = subprocess.run(
        ("cmd", "/c", "mklink", "/J", str(link), str(target)),
        capture_output=True,
        shell=False,
        timeout=30,
    )
    return completed.returncode == 0 and link.exists()


def _minimal_manifest() -> PayloadManifest:
    return PayloadManifest(
        plugin_id="johnny-ai-skill",
        plugin_version="0.4.0",
        source_commit="a" * 40,
        dependency_lock_digest=build_approved_runtime_lock().lock_digest,
        entries=(
            PayloadManifestEntry(
                archive_relative_path="AGENTS.md", sha256="0" * 64, byte_length=1
            ),
        ),
    )


class P0TamperedLockRejectedTests(unittest.TestCase):
    """P0: the bootstrap must not render a bundle-supplied, non-approved lock."""

    def test_approved_lock_digest_is_pinned_to_the_canonical_lock(self) -> None:
        self.assertEqual(
            _APPROVED_LOCK_DIGEST, build_approved_runtime_lock().lock_digest
        )

    def test_canonical_renders_and_tampered_locks_do_not(self) -> None:
        lock_path = _REPO_ROOT / "requirements-runtime.lock"
        canonical = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertIsNotNone(_render_requirements(lock_path))
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            with self.subTest(case="attacker_hash"):
                tampered = json.loads(json.dumps(canonical))
                tampered["dependencies"][0]["artifacts"][0]["sha256"] = "0" * 64
                path = base / "tampered.lock"
                path.write_text(json.dumps(tampered), encoding="utf-8")
                self.assertIsNone(_render_requirements(path))
            with self.subTest(case="attacker_version"):
                forged = json.loads(json.dumps(canonical))
                forged["dependencies"][0]["exact_version"] = "9.9.9"
                path = base / "forged.lock"
                path.write_text(json.dumps(forged), encoding="utf-8")
                self.assertIsNone(_render_requirements(path))
            with self.subTest(case="self_consistent_but_unapproved"):
                # Only the approved-digest pin catches this: the attacker
                # recomputes the lock's own digest so it is internally
                # consistent. Removing that pin turns this cell red.
                rogue = json.loads(json.dumps(canonical))
                rogue["dependencies"][0]["exact_version"] = "9.9.9"
                payload = json.dumps(
                    {
                        "schema_version": rogue["schema_version"],
                        "python_constraint": rogue["python_constraint"],
                        "dependencies": rogue["dependencies"],
                    },
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                rogue["lock_digest"] = hashlib.sha256(
                    payload.encode("utf-8")
                ).hexdigest()
                path = base / "rogue.lock"
                path.write_text(json.dumps(rogue), encoding="utf-8")
                self.assertIsNone(_render_requirements(path))

            with self.subTest(case="extra_dependency"):
                extended = json.loads(json.dumps(canonical))
                extended["dependencies"].append(
                    {
                        "normalized_name": "attacker_pkg",
                        "exact_version": "1.0.0",
                        "environment_marker": None,
                        "source_kind": "wheel",
                        "artifacts": [
                            {"filename": "attacker_pkg-1.0.0.whl", "sha256": "1" * 64}
                        ],
                    }
                )
                path = base / "extended.lock"
                path.write_text(json.dumps(extended), encoding="utf-8")
                self.assertIsNone(_render_requirements(path))


class P1SecondaryDirectoryOwnershipTests(unittest.TestCase):
    """P1: every directory a receipt would delete needs its own marker."""

    def test_unmarked_secondary_directory_is_foreign(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            (layout.base / "launcher").mkdir(parents=True)
            (layout.base / "launcher" / ".johnny-owned").write_text(
                "receipt-live-x", encoding="utf-8"
            )
            (layout.base / "runtime").mkdir(parents=True)
            port = LiveOwnedStatePort(layout, "receipt-live-x")
            record = OwnedStateRecord(
                kind=OwnedStateKind.LAUNCHER, receipt="launcher"
            )
            self.assertIs(port.probe(record), UninstallOwnershipProbe.FOREIGN)
            (layout.base / "runtime" / ".johnny-owned").write_text(
                "receipt-live-x", encoding="utf-8"
            )
            self.assertIs(port.probe(record), UninstallOwnershipProbe.OWNED)


class P1ReparsePayloadRootTests(unittest.TestCase):
    """P1: an empty but redirected plugin root must not receive payload bytes."""

    def test_redirected_empty_root_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            outside = base / "outside"
            outside.mkdir()
            layout = JohnnyRootLayout(base=base / "jr")
            layout.base.mkdir()
            if not _make_reparse_point(layout.plugin_root, outside):
                self.skipTest("this host cannot create a directory reparse point")
            port = RealPluginPayloadEffectPort(layout, base / "absent.zip")
            outcome = port.install("attempt-p1", _minimal_manifest())
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertEqual(list(outside.iterdir()), [])


class P1ProbeExercisesTheWakeCommandTests(unittest.TestCase):
    """P1: PROVEN must mean the declared wake command itself succeeded."""

    def test_a_failing_wake_command_cannot_be_proven(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            wake_config_path(layout).write_text(
                WakeCommandConfig(
                    command=(
                        sys.executable,
                        "-c",
                        "import sys; sys.exit(9)",
                        "{payload_file}",
                    ),
                    reviewer_ref="role-supervisor-reviewer",
                ).model_dump_json(),
                encoding="utf-8",
            )
            result = probe_wake_capability(layout)
            self.assertIs(result.status, WakeCapabilityStatus.UNAVAILABLE)
            self.assertIs(result.failure, WakeCapabilityFailure.PROBE_FAILED)

    def test_the_probe_hands_the_command_a_real_payload_file(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            wake_config_path(layout).write_text(
                WakeCommandConfig(
                    command=(
                        sys.executable,
                        "-c",
                        "import pathlib,sys;"
                        "sys.exit(0 if pathlib.Path(sys.argv[1]).is_file() else 5)",
                        "{payload_file}",
                    ),
                    reviewer_ref="role-supervisor-reviewer",
                ).model_dump_json(),
                encoding="utf-8",
            )
            result = probe_wake_capability(layout)
            self.assertIs(result.status, WakeCapabilityStatus.PROVEN)
            self.assertFalse(
                (layout.queue_root / "wake-capability-probe.json").exists()
            )


class P1UnbatchedBypassIsNamedTests(unittest.TestCase):
    """P1: skipping FIFO batching must be an explicit, named composition."""

    def test_canonical_builder_keeps_requiring_the_inbox_coordinator(self) -> None:
        annotations = (
            windows_supervision_composition.build_windows_receipt_bound_supervision.__annotations__
        )
        self.assertIn(
            "SeniorReviewInboxCoordinator", str(annotations["wake_coordinator"])
        )

    def test_the_bypass_declares_what_it_omits(self) -> None:
        documentation = (
            windows_supervision_composition.build_windows_supervision_without_review_batching.__doc__
            or ""
        )
        self.assertIn("NO FIFO batching", documentation)


class P2ResidueWithoutLedgerTests(unittest.TestCase):
    """P2: owned residue must be reported even when the ledger is gone."""

    def test_residue_is_detected_for_any_receipt(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            (layout.base / "venv").mkdir(parents=True)
            (layout.base / "venv" / ".johnny-owned").write_text(
                "receipt-live-from-an-older-install", encoding="utf-8"
            )
            port = LiveOwnedStatePort(layout, "receipt-live-absent-probe")
            self.assertTrue(port.has_owned_state("receipt-live-absent-probe"))


if __name__ == "__main__":
    unittest.main()
