"""Wake-chain preflight and exactly-once reviewer wake tests."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from library.local_orchestration.role_wake_composition import (
    DurableRoleWakeAttemptStore,
    RoleWakeAttemptStorePort,
    RoleWakeCoordinator,
    RoleWakePort,
)
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.live_dispatch_metadata_store import (
    LiveDispatchMetadataStore,
)
from library.workflow_router.git_handoff_contracts import (
    GitEventAdapterDecision,
    GitEventAdapterDecisionKind,
    GitEventRegistrationLifecycle,
    GitEventRegistrationState,
    GitObservationMode,
)
from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    ReceiptLifecycle,
    TicketReceipt,
    TicketReceiptIssueRequest,
)
from library.workflow_router.role_wake_contracts import (
    DeadlineCapabilityState,
    MonotonicDeadlineCapabilityProof,
    RoleWakeAttemptClaimRequest,
    RoleWakeAttemptClaimResult,
    RoleWakeAttemptLifecycle,
    RoleWakeAttemptRecord,
    RoleWakeAttemptSettleRequest,
    RoleWakeAttemptSettleResult,
    RoleWakeCapabilityProof,
    RoleWakeCapabilityState,
    RoleWakeChainPreflightRequest,
    RoleWakeChainStatus,
    RoleWakeCommand,
    RoleWakeEffectResult,
    RoleWakeEffectStatus,
    RoleWakeRequest,
    RoleWakeStatus,
    RoleWakeTriggerKind,
    WakeAttemptClaimStatus,
    WakeAttemptSettleStatus,
    derive_role_wake_attempt_identity,
    preflight_role_wake_chain,
    wake_request_from_git_decision,
)
from library.workflow_router.thread_host_contracts import (
    CodexHostId,
    CodexTaskId,
)


_DIGEST_A = "sha256_" + ("a" * 64)
_DIGEST_B = "sha256_" + ("b" * 64)
_REVIEWER_TASK = "019ffb0c-c9c7-7b30-b614-02dea7ed9042"


def _receipt() -> TicketReceipt:
    return TicketReceipt(
        project_id="prj_0123456789abcdef",
        receipt_id="receipt-vita-feature-001",
        ticket_reference="ticket-vita-feature-001",
        ticket_revision="rev-2222222222222222",
        ticket_digest=_DIGEST_A,
        ticket_document_commit="1" * 40,
        handoff_reference="handoff-vita-feature-001",
        handoff_revision="rev-3333333333333333",
        handoff_digest=_DIGEST_B,
        handoff_document_commit="2" * 40,
        baseline_commit="3" * 40,
        implementation_owner_id="role-implementation-owner",
        expected_return="return-implementation",
        descriptor_binding="descriptor-vita-feature-001",
        correlation_id="correlation-vita-feature-001",
        dispatch_question_id="question-vita-feature-001",
        worktree_fingerprint="worktree-vitafeature-01",
        branch_fingerprint="branch-vitafeature-01",
        lifecycle=ReceiptLifecycle.ACTIVE,
    )


def _registration(receipt: TicketReceipt) -> GitEventRegistrationState:
    return GitEventRegistrationState(
        event_source_ref="event-source-vita-feature-001",
        subscription_id="subscription-vita-feature-001",
        project_id=receipt.project_id,
        ticket_ref=receipt.ticket_reference,
        router_receipt_ref=receipt.receipt_id,
        implementation_task_ref="task-vita-implementation",
        worktree_ref=receipt.worktree_fingerprint,
        branch_ref=receipt.branch_fingerprint,
        baseline_commit=receipt.baseline_commit,
        correlation_id=receipt.correlation_id,
        exact_git_ref="refs/heads/main",
        reserved_handoff_ref=(
            "doc/handoffs/2026/vita-feature/ticket-vita-feature-001/"
            "handoff-vita-feature-001.json"
        ),
        mode=GitObservationMode.NATIVE_REF_EVENT,
        lifecycle=GitEventRegistrationLifecycle.ACTIVE,
        last_observed_commit=receipt.baseline_commit,
        consumed_handoff_ids=(),
        fault_emitted=False,
    )


def _wake_capability(receipt: TicketReceipt) -> RoleWakeCapabilityProof:
    return RoleWakeCapabilityProof(
        project_id=receipt.project_id,
        ticket_ref=receipt.ticket_reference,
        router_receipt_ref=receipt.receipt_id,
        bound_event_source_ref="event-source-vita-feature-001",
        bound_subscription_id="subscription-vita-feature-001",
        bound_implementation_task_ref="task-vita-implementation",
        reviewer_ref="role-supervisor-reviewer",
        reviewer_task_id=_REVIEWER_TASK,
        reviewer_thread_id=_REVIEWER_TASK,
        host_id="local",
        wake_port_revision="rev-4444444444444444",
        binding_digest=_DIGEST_A,
        state=RoleWakeCapabilityState.PROVEN,
        evidence_refs=("evidence-reviewer-host-readback",),
    )


def _deadline_capability(receipt: TicketReceipt) -> MonotonicDeadlineCapabilityProof:
    return MonotonicDeadlineCapabilityProof(
        project_id=receipt.project_id,
        ticket_ref=receipt.ticket_reference,
        router_receipt_ref=receipt.receipt_id,
        implementation_task_ref="task-vita-implementation",
        capability_revision="rev-5555555555555555",
        state=DeadlineCapabilityState.PROVEN,
        one_shot_supported=True,
        recurring_callback_required=False,
        evidence_refs=("evidence-monotonic-one-shot",),
    )


def _preflight_request() -> RoleWakeChainPreflightRequest:
    receipt = _receipt()
    return RoleWakeChainPreflightRequest(
        receipt=receipt,
        registration=_registration(receipt),
        reviewer_ref="role-supervisor-reviewer",
        implementation_task_ref="task-vita-implementation",
        wake_capability=_wake_capability(receipt),
        deadline_capability=_deadline_capability(receipt),
    )


class _MemoryWakeStore(RoleWakeAttemptStorePort):
    def __init__(self) -> None:
        self.record: RoleWakeAttemptRecord | None = None

    def claim(self, request: RoleWakeAttemptClaimRequest) -> RoleWakeAttemptClaimResult:
        if self.record is None:
            self.record = RoleWakeAttemptRecord(
                identity=request.identity,
                lifecycle=RoleWakeAttemptLifecycle.CLAIMED,
            )
            return RoleWakeAttemptClaimResult(
                status=WakeAttemptClaimStatus.CLAIMED,
                record=self.record,
            )
        if self.record.identity == request.identity:
            return RoleWakeAttemptClaimResult(
                status=WakeAttemptClaimStatus.ALREADY_CLAIMED,
                record=self.record,
            )
        return RoleWakeAttemptClaimResult(
            status=WakeAttemptClaimStatus.ATTEMPT_CONFLICT,
        )

    def settle(self, request: RoleWakeAttemptSettleRequest) -> RoleWakeAttemptSettleResult:
        if self.record is None or self.record.identity != request.identity:
            return RoleWakeAttemptSettleResult(
                status=WakeAttemptSettleStatus.CLAIM_MISMATCH,
            )
        lifecycle = RoleWakeAttemptLifecycle(request.effect.status.value)
        self.record = RoleWakeAttemptRecord(
            identity=request.identity,
            lifecycle=lifecycle,
            delivery_reference=request.effect.delivery_reference,
        )
        return RoleWakeAttemptSettleResult(
            status=WakeAttemptSettleStatus.SETTLED,
            record=self.record,
        )


class _RecordingWakePort(RoleWakePort):
    def __init__(self, effect: RoleWakeEffectResult) -> None:
        self.effect = effect
        self.commands: list[RoleWakeCommand] = []

    def wake(self, command: RoleWakeCommand) -> RoleWakeEffectResult:
        self.commands.append(command)
        return self.effect


class WakeChainPreflightTests(unittest.TestCase):
    def test_complete_chain_is_proven_and_every_binding_is_digest_bound(self) -> None:
        result = preflight_role_wake_chain(_preflight_request())
        self.assertEqual(RoleWakeChainStatus.PROVEN, result.status)
        self.assertIsNotNone(result.proof)
        self.assertTrue(result.proof.chain_digest.startswith("sha256_") if result.proof else False)

    def test_missing_or_mismatched_capability_fails_before_host_effect(self) -> None:
        request = _preflight_request()
        mutations = (
            {"registration": request.registration.model_copy(update={"mode": GitObservationMode.UNAVAILABLE})},
            {"registration": request.registration.model_copy(update={"subscription_id": "subscription-wrong"})},
            {"implementation_task_ref": "task-wrong"},
            {"wake_capability": request.wake_capability.model_copy(update={"state": RoleWakeCapabilityState.UNAVAILABLE})},
            {"deadline_capability": request.deadline_capability.model_copy(update={"one_shot_supported": False})},
            {"deadline_capability": request.deadline_capability.model_copy(update={"recurring_callback_required": True})},
        )
        for update in mutations:
            with self.subTest(update=tuple(update)):
                bypassed = request.model_copy(update=update)
                result = preflight_role_wake_chain(bypassed)
                self.assertEqual(RoleWakeChainStatus.REJECTED, result.status)
                self.assertIsNone(result.proof)

    def test_contract_does_not_accept_missing_subscription_or_extra_heartbeat(self) -> None:
        payload = _preflight_request().model_dump(mode="json")
        registration = dict(payload["registration"])
        registration.pop("subscription_id")
        payload["registration"] = registration
        with self.assertRaises(ValidationError):
            RoleWakeChainPreflightRequest.model_validate(payload, strict=True)
        payload = _preflight_request().model_dump(mode="json")
        payload["heartbeat_interval"] = 60
        with self.assertRaises(ValidationError):
            RoleWakeChainPreflightRequest.model_validate(payload, strict=True)


class RoleWakeCoordinatorTests(unittest.TestCase):
    def _request(self) -> RoleWakeRequest:
        preflight = preflight_role_wake_chain(_preflight_request())
        if preflight.proof is None:
            self.fail("preflight did not create a proof")
        return RoleWakeRequest(
            attempt_id="attempt-review-wake-001",
            chain=preflight.proof,
            trigger=RoleWakeTriggerKind.REVIEW_HANDOFF,
            observed_commit="6" * 40,
            handoff_id="handoff-vita-feature-001",
            lease_id=None,
            fault_kind=None,
        )

    def test_claim_before_effect_and_duplicate_wake_calls_host_once(self) -> None:
        store = _MemoryWakeStore()
        port = _RecordingWakePort(
            RoleWakeEffectResult(
                status=RoleWakeEffectStatus.HOST_ACCEPTED,
                delivery_reference="delivery-review-wake-001",
            )
        )
        coordinator = RoleWakeCoordinator(store, port)
        request = self._request()
        first = coordinator.wake(request)
        second = coordinator.wake(request)
        self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, first.status)
        self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, second.status)
        self.assertEqual(1, len(port.commands))
        payload = port.commands[0].payload
        self.assertIn("action=REVIEW_HANDOFF", payload)
        self.assertIn("subscription_id=subscription-vita-feature-001", payload)
        self.assertNotIn("doc/handoffs", payload)
        self.assertNotIn("prompt", payload.casefold())

    def test_uncertain_host_effect_is_never_retried(self) -> None:
        store = _MemoryWakeStore()
        port = _RecordingWakePort(
            RoleWakeEffectResult(status=RoleWakeEffectStatus.EFFECT_UNCERTAIN)
        )
        coordinator = RoleWakeCoordinator(store, port)
        request = self._request()
        first = coordinator.wake(request)
        second = coordinator.wake(request)
        self.assertEqual(RoleWakeStatus.EFFECT_UNCERTAIN, first.status)
        self.assertEqual(RoleWakeStatus.EFFECT_UNCERTAIN, second.status)
        self.assertEqual(1, len(port.commands))

    def test_durable_claim_survives_boundary_restart_without_second_host_call(self) -> None:
        receipt = _receipt()
        artifact = ApprovedDispatchArtifactRecord(
            project_id=receipt.project_id,
            ticket_reference=receipt.ticket_reference,
            ticket_revision=receipt.ticket_revision,
            ticket_digest=receipt.ticket_digest,
            ticket_document_commit=receipt.ticket_document_commit,
            handoff_reference=receipt.handoff_reference,
            handoff_revision=receipt.handoff_revision,
            handoff_digest=receipt.handoff_digest,
            handoff_document_commit=receipt.handoff_document_commit,
            baseline_commit=receipt.baseline_commit,
            implementation_owner_id=receipt.implementation_owner_id,
            expected_return=receipt.expected_return,
            descriptor_binding=receipt.descriptor_binding,
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            metadata = LiveDispatchMetadataStore(boundary)
            metadata.register_artifact(
                ApprovedDispatchArtifactRegisterRequest(artifact=artifact)
            )
            metadata.issue_receipt(
                TicketReceiptIssueRequest(
                    artifact_identity=artifact.identity,
                    ticket_revision=receipt.ticket_revision,
                    ticket_digest=receipt.ticket_digest,
                    ticket_document_commit=receipt.ticket_document_commit,
                    handoff_revision=receipt.handoff_revision,
                    handoff_digest=receipt.handoff_digest,
                    handoff_document_commit=receipt.handoff_document_commit,
                    baseline_commit=receipt.baseline_commit,
                    receipt_id=receipt.receipt_id,
                    expected_return=receipt.expected_return,
                    descriptor_binding=receipt.descriptor_binding,
                    correlation_id=receipt.correlation_id,
                    dispatch_question_id=receipt.dispatch_question_id,
                    worktree_fingerprint=receipt.worktree_fingerprint,
                    branch_fingerprint=receipt.branch_fingerprint,
                )
            )
            first_port = _RecordingWakePort(
                RoleWakeEffectResult(
                    status=RoleWakeEffectStatus.HOST_ACCEPTED,
                    delivery_reference="delivery-review-wake-001",
                )
            )
            request = self._request()
            first = RoleWakeCoordinator(
                DurableRoleWakeAttemptStore(boundary),
                first_port,
            ).wake(request)
            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, first.status)
            self.assertEqual(1, len(first_port.commands))

            restarted_boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            restarted_port = _RecordingWakePort(
                RoleWakeEffectResult(status=RoleWakeEffectStatus.EFFECT_UNCERTAIN)
            )
            replay = RoleWakeCoordinator(
                DurableRoleWakeAttemptStore(restarted_boundary),
                restarted_port,
            ).wake(request)
            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, replay.status)
            self.assertEqual(0, len(restarted_port.commands))

    def test_only_terminal_or_fault_git_decisions_create_wake_requests(self) -> None:
        request = self._request()
        state = request.chain.registration
        source_only = GitEventAdapterDecision(
            decision=GitEventAdapterDecisionKind.SOURCE_ADVANCED,
            registration=state,
        )
        self.assertIsNone(
            wake_request_from_git_decision(
                "attempt-source-only-001",
                request.chain,
                source_only,
            )
        )


if __name__ == "__main__":
    unittest.main()
