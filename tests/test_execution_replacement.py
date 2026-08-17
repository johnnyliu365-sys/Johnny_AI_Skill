"""Controlled execution identity and model replacement tests."""

from __future__ import annotations

import unittest

from library.workflow_router.execution_replacement import (
    ExecutionActivationReadback,
    ExecutionBinding,
    ExecutionBindingLifecycle,
    ExecutionEventIdentity,
    ExecutionEventStatus,
    ExecutionIdentityObservation,
    ExecutionModel,
    ExecutionReplacementCandidate,
    ExecutionReplacementDecisionKind,
    ExecutionReplacementRequest,
    ExecutionRevocationReadback,
    ModelRebindEvidence,
    ReplacementReceiptAuthority,
    close_execution_binding,
    complete_execution_replacement,
    plan_execution_replacement,
    rebind_execution_model,
    validate_execution_event,
)
from library.workflow_router.live_dispatch_contracts import ReceiptLifecycle, TicketReceipt


_DIGEST_A = "sha256_" + ("a" * 64)
_DIGEST_B = "sha256_" + ("b" * 64)


def _receipt(
    *,
    receipt_id: str = "receipt-vita-feature-001",
    worktree: str = "worktree-vitafeature-01",
    branch: str = "branch-vitafeature-01",
    baseline: str = "3" * 40,
    lifecycle: ReceiptLifecycle = ReceiptLifecycle.ACTIVE,
) -> TicketReceipt:
    return TicketReceipt(
        project_id="prj_0123456789abcdef",
        receipt_id=receipt_id,
        ticket_reference="ticket-vita-feature-001",
        ticket_revision="rev-2222222222222222",
        ticket_digest=_DIGEST_A,
        ticket_document_commit="1" * 40,
        handoff_reference="handoff-vita-feature-001",
        handoff_revision="rev-3333333333333333",
        handoff_digest=_DIGEST_B,
        handoff_document_commit="2" * 40,
        baseline_commit=baseline,
        implementation_owner_id="role-implementation-owner",
        expected_return="return-implementation",
        descriptor_binding="descriptor-vita-feature-001",
        correlation_id="correlation-vita-feature-001",
        dispatch_question_id="question-vita-feature-001",
        worktree_fingerprint=worktree,
        branch_fingerprint=branch,
        lifecycle=lifecycle,
    )


def _binding(
    *,
    receipt: TicketReceipt | None = None,
    lifecycle: ExecutionBindingLifecycle = ExecutionBindingLifecycle.ACTIVE,
    task: str = "task-implementation-one",
    writer: str = "writer-implementation-one",
    host: str = "host-local-one",
    machine: str = "machine-local-one",
    correlation: str = "correlation-execution-one",
    model: ExecutionModel = ExecutionModel.LUNA_XHIGH,
) -> ExecutionBinding:
    exact_receipt = receipt or _receipt()
    return ExecutionBinding(
        binding_ref="binding-vita-feature-001",
        binding_revision="rev-4444444444444444",
        lifecycle=lifecycle,
        receipt=exact_receipt,
        implementation_owner_ref=exact_receipt.implementation_owner_id,
        task_ref=task,
        effective_writer_ref=writer,
        host_ref=host,
        machine_ref=machine,
        worktree_ref=exact_receipt.worktree_fingerprint,
        branch_ref=exact_receipt.branch_fingerprint,
        baseline_commit=exact_receipt.baseline_commit,
        correlation_id=correlation,
        model=model,
        write_lease_ref="write-lease-vita-feature-001",
        subscription_id="subscription-vita-feature-001",
        last_committed_commit="4" * 40,
    )


def _candidate(
    current: ExecutionBinding,
    *,
    receipt: TicketReceipt | None = None,
    task: str = "task-implementation-two",
    writer: str = "writer-implementation-two",
    host: str | None = None,
    machine: str | None = None,
    worktree_is_fresh_clean_checkout: bool = False,
    baseline: str | None = None,
    model: ExecutionModel = ExecutionModel.TERRA_HIGH,
) -> ExecutionReplacementCandidate:
    exact_receipt = receipt or current.receipt
    return ExecutionReplacementCandidate(
        binding_ref="binding-vita-feature-002",
        binding_revision="rev-5555555555555555",
        receipt=exact_receipt,
        implementation_owner_ref=exact_receipt.implementation_owner_id,
        task_ref=task,
        effective_writer_ref=writer,
        host_ref=host or current.host_ref,
        machine_ref=machine or current.machine_ref,
        worktree_ref=exact_receipt.worktree_fingerprint,
        branch_ref=exact_receipt.branch_fingerprint,
        baseline_commit=baseline or exact_receipt.baseline_commit,
        correlation_id="correlation-execution-two",
        model=model,
        write_lease_ref="write-lease-vita-feature-002",
        subscription_id="subscription-vita-feature-002",
        worktree_is_fresh_clean_checkout=worktree_is_fresh_clean_checkout,
    )


def _request(
    current: ExecutionBinding,
    candidate: ExecutionReplacementCandidate,
    *,
    old_task_available: bool = True,
    checkpoint_ref: str | None = "handoff-checkpoint-vita-001",
    checkpoint_commit: str | None = "4" * 40,
    receipt_authority: ReplacementReceiptAuthority | None = None,
) -> ExecutionReplacementRequest:
    return ExecutionReplacementRequest(
        replacement_id="replacement-vita-feature-001",
        current=current,
        candidate=candidate,
        old_task_available=old_task_available,
        checkpoint_ref=checkpoint_ref,
        checkpoint_commit=checkpoint_commit,
        receipt_authority=receipt_authority,
    )


class ExecutionIdentityTests(unittest.TestCase):
    def test_shell_change_inside_same_task_is_a_noop(self) -> None:
        current = _binding()
        observation = ExecutionIdentityObservation(
            task_ref=current.task_ref,
            effective_writer_ref=current.effective_writer_ref,
            host_ref=current.host_ref,
            machine_ref=current.machine_ref,
            shell_session_ref="shell-new",
        )
        result = plan_execution_replacement(
            ExecutionReplacementRequest(
                replacement_id="replacement-vita-feature-001",
                current=current,
                identity_observation=observation,
                candidate=None,
                old_task_available=True,
                checkpoint_ref=None,
                checkpoint_commit=None,
                receipt_authority=None,
            )
        )
        self.assertEqual(ExecutionReplacementDecisionKind.SAME_EXECUTION_NOOP, result.decision)
        self.assertEqual(ExecutionBindingLifecycle.ACTIVE, result.current.lifecycle)

    def test_task_writer_host_or_machine_change_requires_replacement(self) -> None:
        current = _binding()
        candidate = _candidate(current)
        result = plan_execution_replacement(_request(current, candidate))
        self.assertEqual(ExecutionReplacementDecisionKind.REPLACEMENT_READY, result.decision)
        self.assertEqual(ExecutionBindingLifecycle.REPLACEMENT_PENDING, result.current.lifecycle)


class ExecutionReplacementPolicyTests(unittest.TestCase):
    def test_available_old_task_requires_committed_checkpoint(self) -> None:
        current = _binding()
        candidate = _candidate(current)
        result = plan_execution_replacement(
            _request(
                current,
                candidate,
                checkpoint_ref=None,
                checkpoint_commit=None,
            )
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REJECTED, result.decision)

    def test_unavailable_old_task_recovers_last_commit_only(self) -> None:
        current = _binding()
        wrong_receipt = _receipt(
            receipt_id="receipt-vita-feature-002",
            baseline="5" * 40,
        )
        wrong = _candidate(current, receipt=wrong_receipt, baseline="5" * 40)
        rejected = plan_execution_replacement(
            _request(
                current,
                wrong,
                old_task_available=False,
                checkpoint_ref=None,
                checkpoint_commit=None,
            )
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REJECTED, rejected.decision)

        recovered_receipt = _receipt(
            receipt_id="receipt-vita-feature-003",
            baseline=current.last_committed_commit,
        )
        recovered = _candidate(
            current,
            receipt=recovered_receipt,
            baseline=current.last_committed_commit,
        )
        authority = ReplacementReceiptAuthority(
            router_authorized=True,
            old_receipt_revoked=True,
            replacement_receipt=recovered_receipt,
        )
        accepted = plan_execution_replacement(
            _request(
                current,
                recovered,
                old_task_available=False,
                checkpoint_ref=None,
                checkpoint_commit=None,
                receipt_authority=authority,
            )
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REPLACEMENT_READY, accepted.decision)

    def test_new_machine_requires_fresh_clean_checkout(self) -> None:
        current = _binding()
        candidate = _candidate(current, machine="machine-remote-two")
        rejected = plan_execution_replacement(_request(current, candidate))
        self.assertEqual(ExecutionReplacementDecisionKind.REJECTED, rejected.decision)
        clean = _candidate(
            current,
            machine="machine-remote-two",
            worktree_is_fresh_clean_checkout=True,
        )
        accepted = plan_execution_replacement(_request(current, clean))
        self.assertEqual(ExecutionReplacementDecisionKind.REPLACEMENT_READY, accepted.decision)

    def test_receipt_bound_field_change_requires_router_replacement_and_old_revocation(self) -> None:
        current = _binding()
        replacement_receipt = _receipt(
            receipt_id="receipt-vita-feature-002",
            worktree="worktree-vitafeature-02",
            branch="branch-vitafeature-02",
            baseline="5" * 40,
        )
        candidate = _candidate(current, receipt=replacement_receipt, baseline="5" * 40)
        rejected = plan_execution_replacement(_request(current, candidate))
        self.assertEqual(ExecutionReplacementDecisionKind.REJECTED, rejected.decision)

        authority = ReplacementReceiptAuthority(
            router_authorized=True,
            old_receipt_revoked=True,
            replacement_receipt=replacement_receipt,
        )
        accepted = plan_execution_replacement(
            _request(current, candidate, receipt_authority=authority)
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REPLACEMENT_READY, accepted.decision)
        self.assertEqual(ReceiptLifecycle.REVOKED, accepted.current.receipt.lifecycle)
        self.assertEqual(ReceiptLifecycle.ACTIVE, accepted.candidate.receipt.lifecycle if accepted.candidate else None)

    def test_revocation_readback_precedes_activation_and_old_events_become_stale(self) -> None:
        current = _binding()
        candidate = _candidate(current)
        plan = plan_execution_replacement(_request(current, candidate))
        self.assertIsNotNone(plan.candidate)
        completed = complete_execution_replacement(
            plan,
            ExecutionRevocationReadback(
                binding_ref=current.binding_ref,
                write_disabled=True,
                subscription_closed=True,
                evidence_refs=("evidence-old-writer-revoked",),
            ),
            ExecutionActivationReadback(
                binding_ref=candidate.binding_ref,
                task_ref=candidate.task_ref,
                effective_writer_ref=candidate.effective_writer_ref,
                host_ref=candidate.host_ref,
                machine_ref=candidate.machine_ref,
                write_enabled=True,
                evidence_refs=("evidence-new-writer-active",),
            ),
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REPLACED, completed.decision)
        self.assertEqual(ExecutionBindingLifecycle.REPLACED, completed.current.lifecycle)
        self.assertEqual(ExecutionBindingLifecycle.ACTIVE, completed.active.lifecycle if completed.active else None)
        old_event = validate_execution_event(
            completed,
            ExecutionEventIdentity(
                binding_ref=current.binding_ref,
                task_ref=current.task_ref,
                receipt_ref=current.receipt.receipt_id,
                correlation_id=current.correlation_id,
            ),
        )
        new_event = validate_execution_event(
            completed,
            ExecutionEventIdentity(
                binding_ref=candidate.binding_ref,
                task_ref=candidate.task_ref,
                receipt_ref=candidate.receipt.receipt_id,
                correlation_id=candidate.correlation_id,
            ),
        )
        self.assertEqual(ExecutionEventStatus.STALE_BINDING, old_event)
        self.assertEqual(ExecutionEventStatus.ACCEPTED, new_event)


class ModelRebindTests(unittest.TestCase):
    def test_in_place_rebind_requires_host_proof_and_same_execution(self) -> None:
        current = _binding()
        rejected = rebind_execution_model(
            current,
            ModelRebindEvidence(
                binding_revision="rev-5555555555555555",
                task_ref=current.task_ref,
                host_ref=current.host_ref,
                target_model=ExecutionModel.TERRA_HIGH,
                in_place_rebind_proven=False,
                evidence_refs=("evidence-model-readback",),
            ),
        )
        self.assertEqual(ExecutionReplacementDecisionKind.REJECTED, rejected.decision)
        rebound = rebind_execution_model(
            current,
            ModelRebindEvidence(
                binding_revision="rev-5555555555555555",
                task_ref=current.task_ref,
                host_ref=current.host_ref,
                target_model=ExecutionModel.TERRA_HIGH,
                in_place_rebind_proven=True,
                evidence_refs=("evidence-model-readback",),
            ),
        )
        self.assertEqual(ExecutionReplacementDecisionKind.MODEL_REBOUND_IN_PLACE, rebound.decision)
        self.assertEqual(ExecutionModel.TERRA_HIGH, rebound.active.model if rebound.active else None)
        self.assertEqual(current.task_ref, rebound.active.task_ref if rebound.active else None)

    def test_terminal_close_ends_write_authority(self) -> None:
        closed = close_execution_binding(_binding())
        self.assertEqual(ExecutionBindingLifecycle.CLOSED, closed.lifecycle)


if __name__ == "__main__":
    unittest.main()
