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
from library.local_orchestration import event_runner
from library.local_orchestration.event_runner import (
    RunnerSubscriptionFile,
    RunnerSubscriptionSpec,
    subscriptions_path,
)
from library.local_orchestration.role_wake_composition import (
    DurableRoleWakeAttemptStore,
    RoleWakeAttemptBoundaryPort,
)
from library.local_orchestration.runner_receipt_seeding import (
    ReceiptVerificationFailure,
    ReceiptVerificationStatus,
)
from library.local_orchestration.wake_scoped_boundary import (
    WakeScopedDispatchBoundary,
)
from library.workflow_router.live_dispatch_contracts import TicketReceipt
from library.workflow_router.supervision_policy import SupervisionClass
from library.workflow_router.supervision_runtime_contracts import (
    SupervisionPreparationRequest,
    SupervisionStartRequest,
)
from tests.test_git_handoff_event_adapter import _admission, _registration_request
from tests.test_live_payload_ports import _write_bundle
from tests.test_receipt_bound_supervision import _started
from tests.test_role_wake_composition import (
    _deadline_capability,
    _receipt,
    _wake_capability,
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
        """The bundle is real and extractable, so this cell stays green only
        while the containment guard blocks: remove the guard and extraction
        lands in `outside`, turning the emptiness assertion red."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            outside = base / "outside"
            outside.mkdir()
            bundle = base / "bundle.zip"
            manifest = _write_bundle(bundle)
            layout = JohnnyRootLayout(base=base / "jr")
            layout.base.mkdir()
            if not _make_reparse_point(layout.plugin_root, outside):
                self.skipTest("this host cannot create a directory reparse point")
            port = RealPluginPayloadEffectPort(layout, bundle)
            outcome = port.install("attempt-p1", manifest)
            self.assertIs(outcome.status, InstallEffectOutcomeStatus.UNAVAILABLE)
            self.assertEqual(list(outside.iterdir()), [])



    def test_redirected_base_itself_is_refused(self) -> None:
        """Round three P1: a junction at the Johnny base defeats containment
        anchored to the resolved base. The bundle is real and extractable, so
        removing the base self-resolution guard makes extraction land in
        `outside` and turns the emptiness assertion red."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            outside = base / "outside"
            outside.mkdir()
            bundle = base / "bundle.zip"
            manifest = _write_bundle(bundle)
            link = base / "jr-link"
            if not _make_reparse_point(link, outside):
                self.skipTest("this host cannot create a directory reparse point")
            layout = JohnnyRootLayout(base=link)
            port = RealPluginPayloadEffectPort(layout, bundle)
            outcome = port.install("attempt-p1-base", manifest)
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



class P0RunnerBindingIdentityTests(unittest.TestCase):
    """Round five P0: observe the object the runner actually binds.

    Name-based namespace checks stay green under alias or factory reflow, so
    this cell records every boundary object the untouched production line
    hands to the wake chain (the attempt store and the verification call) and
    requires each to be exactly the canonical facade with no issuance
    attribute. Any mutation that routes an issuance-capable object into the
    runner turns this red, whatever it is named.
    """

    def test_the_runner_binds_exactly_the_wake_scoped_facade(self) -> None:
        captured: list[object] = []

        def recording_verify(
            boundary: object, receipt: TicketReceipt
        ) -> tuple[ReceiptVerificationStatus, ReceiptVerificationFailure | None]:
            captured.append(boundary)
            return (
                ReceiptVerificationStatus.BLOCKED,
                ReceiptVerificationFailure.RECEIPT_NOT_FOUND,
            )

        class RecordingStore(DurableRoleWakeAttemptStore):
            def __init__(self, boundary: RoleWakeAttemptBoundaryPort) -> None:
                captured.append(boundary)
                super().__init__(boundary)

        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            layout.queue_root.mkdir(parents=True)
            baseline = "c" * 40
            receipt = _receipt().model_copy(update={"baseline_commit": baseline})
            specification = RunnerSubscriptionSpec(
                repository_root=str(layout.base),
                preparation=SupervisionPreparationRequest(
                    receipt=receipt,
                    registration_request=_registration_request(baseline),
                    handoff_context=_admission(
                        baseline=baseline, observed_handoff_commit=baseline
                    ),
                    reviewer_ref="role-supervisor-reviewer",
                    implementation_task_ref="task-vita-implementation",
                    wake_capability=_wake_capability(receipt),
                    deadline_capability=_deadline_capability(receipt),
                ),
                start=SupervisionStartRequest(
                    subscription_id=_registration_request(
                        baseline
                    ).subscription_id,
                    lease_id="lease-p0-binding-001",
                    supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
                    execution_started=_started(baseline),
                ),
            )
            subscriptions_path(layout).write_text(
                RunnerSubscriptionFile(
                    subscriptions=(specification,)
                ).model_dump_json(),
                encoding="utf-8",
            )
            original_verify = getattr(event_runner, "verify_receipt_claimable")
            original_store = getattr(event_runner, "DurableRoleWakeAttemptStore")
            setattr(event_runner, "verify_receipt_claimable", recording_verify)
            setattr(event_runner, "DurableRoleWakeAttemptStore", RecordingStore)
            try:
                exit_code = event_runner.run_event_runner(layout)
            finally:
                setattr(event_runner, "verify_receipt_claimable", original_verify)
                setattr(event_runner, "DurableRoleWakeAttemptStore", original_store)

        self.assertEqual(exit_code, 2)
        self.assertGreaterEqual(len(captured), 2)
        for bound in captured:
            self.assertIs(type(bound), WakeScopedDispatchBoundary)
            for forbidden in ("issue_receipt", "register_artifact"):
                self.assertFalse(hasattr(bound, forbidden))


class P0RunnerHoldsNoIssuanceTests(unittest.TestCase):
    """Round four P0: no issuance-capable object flows through the runner."""

    def test_event_runner_namespace_has_no_issuance_names(self) -> None:
        from library.local_orchestration import event_runner

        for forbidden in (
            "LiveDispatchMetadataBoundary",
            "LiveDispatchMetadataStore",
            "JohnnyMetadataRoot",
        ):
            self.assertFalse(hasattr(event_runner, forbidden))

    def test_the_wake_scoped_surface_is_exactly_three_methods(self) -> None:
        from library.local_orchestration.wake_scoped_boundary import (
            WakeScopedDispatchBoundary,
        )

        surface = sorted(
            name
            for name in vars(WakeScopedDispatchBoundary)
            if not name.startswith("_")
        )
        self.assertEqual(
            surface,
            ["claim_role_wake_attempt", "read_receipt", "settle_role_wake_attempt"],
        )
        for forbidden in ("issue_receipt", "register_artifact"):
            self.assertNotIn(forbidden, surface)



if __name__ == "__main__":
    unittest.main()
