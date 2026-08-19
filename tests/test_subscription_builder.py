"""E7 unblocking: a subscription is derived, never asserted by its caller."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.deadline_capability import (
    DeadlineProbeStatus,
    probe_deadline_capability,
)
from library.local_orchestration.event_runner import (
    RunnerSubscriptionFile,
    subscriptions_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.subscription_builder import (
    SubscriptionBuildFailure,
    SubscriptionBuildStatus,
    SubscriptionInputs,
    build_subscription,
)
from library.local_orchestration.wake_capability import wake_config_path
from library.workflow_router.role_wake_contracts import RoleWakeCapabilityState
from library.workflow_router.supervision_policy import SupervisionClass
from tests.test_role_wake_composition import _receipt
from tests.test_runner_receipt_seeding import _issue_receipt_fixture


def _inputs(repository: Path) -> SubscriptionInputs:
    return SubscriptionInputs(
        repository_root=str(repository),
        event_source_ref="event-source-e7-001",
        subscription_id="subscription-e7-001",
        exact_git_ref="refs/heads/main",
        reserved_handoff_ref=(
            "doc/handoffs/2026/e7/ticket-e7-001/handoff-e7-001.json"
        ),
        spec_ref="spec-e7",
        spec_revision="rev-1111111111111111",
        source_role_ref="role-implementation-owner",
        reviewer_ref="role-supervisor-reviewer",
        reviewer_task_ref="task-e7-reviewer",
        reviewer_task_id="3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
        reviewer_host_id="local",
        lease_id="lease-e7-001",
        supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
    )


def _repository(base: Path) -> Path:
    repository = base / "repo"
    repository.mkdir(parents=True)
    subprocess.run(
        ("git", "-C", str(repository), "init", "--quiet"),
        check=True,
        capture_output=True,
    )
    return repository


def _layout(base: Path) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=(base / "johnny").resolve())
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _declare_wake_command(layout: JohnnyRootLayout) -> None:
    """A real host command that succeeds, so the probe has something to prove."""

    path = wake_config_path(layout)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command": [
                    sys.executable,
                    "-c",
                    "import sys; sys.exit(0)",
                    "{payload_file}",
                ],
                "reviewer_ref": "role-supervisor-reviewer",
                "timeout_seconds": 30,
            }
        ),
        encoding="utf-8",
    )


class DeadlineProbeTests(unittest.TestCase):
    """The deadline proof comes from a timer that actually fired."""

    def test_the_probe_proves_a_real_one_shot(self) -> None:
        receipt = _receipt()
        status, proof = probe_deadline_capability(
            receipt, receipt.implementation_owner_id
        )
        self.assertIs(status, DeadlineProbeStatus.PROVEN)
        assert proof is not None
        self.assertTrue(proof.one_shot_supported)
        self.assertFalse(proof.recurring_callback_required)
        self.assertEqual(proof.router_receipt_ref, receipt.receipt_id)


class ReceiptAuthorityTests(unittest.TestCase):
    """A subscription may not name a receipt dispatch never issued."""

    def test_an_undispatched_receipt_is_refused_before_any_write(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            _declare_wake_command(layout)
            status, failure = build_subscription(
                layout, _receipt(), _inputs(_repository(base))
            )
            self.assertIs(status, SubscriptionBuildStatus.REFUSED)
            self.assertIs(failure, SubscriptionBuildFailure.RECEIPT_NOT_DISPATCHED)
            self.assertFalse(subscriptions_path(layout).exists())

    def test_a_dispatched_receipt_yields_a_loadable_subscription(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            _declare_wake_command(layout)
            repository = _repository(base)
            receipt = _receipt()

            metadata_root = layout.queue_root / "metadata"
            metadata_root.mkdir(parents=True, exist_ok=True)
            _issue_receipt_fixture(
                LiveDispatchMetadataBoundary(
                    JohnnyMetadataRoot(metadata_root.resolve())
                ),
                receipt,
            )

            status, failure = build_subscription(
                layout, receipt, _inputs(repository)
            )
            self.assertIs(status, SubscriptionBuildStatus.WRITTEN, f"{failure}")

            parsed = RunnerSubscriptionFile.model_validate_json(
                subscriptions_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(len(parsed.subscriptions), 1)
            specification = parsed.subscriptions[0]
            preparation = specification.preparation
            self.assertEqual(preparation.receipt, receipt)
            self.assertEqual(
                preparation.registration_request.subscription_id,
                "subscription-e7-001",
            )
            self.assertEqual(
                specification.start.subscription_id, "subscription-e7-001"
            )
            self.assertIs(
                preparation.wake_capability.state, RoleWakeCapabilityState.PROVEN
            )

    def test_every_receipt_bound_field_is_derived_not_supplied(self) -> None:
        """The inputs model cannot carry a receipt-bound identifier at all."""

        forbidden = {
            "project_id",
            "ticket_ref",
            "ticket_reference",
            "router_receipt_ref",
            "receipt_id",
            "baseline_commit",
            "correlation_id",
            "worktree_ref",
            "branch_ref",
            "implementation_task_ref",
        }
        self.assertEqual(
            forbidden & set(SubscriptionInputs.model_fields),
            set(),
        )


class CapabilityAuthorityTests(unittest.TestCase):
    """PROVEN is produced by a probe, never accepted from the caller."""

    def test_an_unprovable_wake_command_refuses_the_subscription(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            repository = _repository(base)
            receipt = _receipt()
            metadata_root = layout.queue_root / "metadata"
            metadata_root.mkdir(parents=True, exist_ok=True)
            _issue_receipt_fixture(
                LiveDispatchMetadataBoundary(
                    JohnnyMetadataRoot(metadata_root.resolve())
                ),
                receipt,
            )
            # No wake command is declared, so the probe cannot prove one.
            status, failure = build_subscription(
                layout, receipt, _inputs(repository)
            )
            self.assertIs(status, SubscriptionBuildStatus.REFUSED)
            self.assertIs(
                failure, SubscriptionBuildFailure.WAKE_CAPABILITY_UNAVAILABLE
            )
            self.assertFalse(subscriptions_path(layout).exists())

    def test_the_inputs_cannot_declare_a_capability_state(self) -> None:
        for forbidden in ("wake_capability", "deadline_capability", "state"):
            with self.subTest(field=forbidden):
                self.assertNotIn(forbidden, SubscriptionInputs.model_fields)


class RepositoryBindingTests(unittest.TestCase):
    def test_a_path_that_is_not_a_repository_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            not_a_repository = base / "plain"
            not_a_repository.mkdir()
            status, failure = build_subscription(
                layout,
                _receipt(),
                _inputs(not_a_repository),
            )
            self.assertIs(status, SubscriptionBuildStatus.REFUSED)
            self.assertIs(failure, SubscriptionBuildFailure.REPOSITORY_UNAVAILABLE)

    def test_the_reviewer_may_not_be_the_implementation_owner(self) -> None:
        with self.assertRaises(ValueError):
            SubscriptionInputs(
                repository_root="C:/repo",
                event_source_ref="event-source-e7-001",
                subscription_id="subscription-e7-001",
                exact_git_ref="refs/heads/main",
                reserved_handoff_ref="doc/handoffs/x.json",
                spec_ref="spec-e7",
                spec_revision="rev-1111111111111111",
                source_role_ref="role-same",
                reviewer_ref="role-same",
                reviewer_task_ref="task-e7-reviewer",
                reviewer_task_id="3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                reviewer_host_id="local",
                lease_id="lease-e7-001",
                supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
            )


if __name__ == "__main__":
    unittest.main()
