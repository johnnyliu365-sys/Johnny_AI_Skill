"""E10 / CR-E7-01: the unbatched composition must fill the review instruction.

`RoleWakeCoordinator` refuses a `REVIEW_HANDOFF` wake whose
`review_instruction` is `None`, and the supervision controller always builds
handoff wakes with `None` (the batching layer normally fills it). The
unbatched composition removed the batching layer without reassigning that
responsibility, so every handoff-driven wake died as `ATTEMPT_CONFLICT`
before the durable store was consulted, while deadline wakes kept flowing.
"""

from __future__ import annotations

import unittest

from library.local_orchestration.role_wake_composition import RoleWakeCoordinator
from library.local_orchestration.windows_supervision_composition import (
    SingleHandoffReviewSubmission,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeRequest,
    RoleWakeResult,
    RoleWakeStatus,
    RoleWakeTriggerKind,
    preflight_role_wake_chain,
)
from tests.test_role_wake_composition import (
    _MemoryWakeStore,
    _preflight_request,
    _review_instruction,
)


def _handoff_request(instruction: object | None) -> RoleWakeRequest:
    preflight = preflight_role_wake_chain(_preflight_request())
    assert preflight.proof is not None
    return RoleWakeRequest(
        attempt_id="attempt-review-wake-001",
        chain=preflight.proof,
        trigger=RoleWakeTriggerKind.REVIEW_HANDOFF,
        observed_commit="6" * 40,
        handoff_id="handoff-vita-feature-001",
        lease_id=None,
        fault_kind=None,
        review_instruction=instruction,  # type: ignore[arg-type]
    )


def _deadline_request() -> RoleWakeRequest:
    preflight = preflight_role_wake_chain(_preflight_request())
    assert preflight.proof is not None
    return RoleWakeRequest(
        attempt_id="attempt-deadline-wake-001",
        chain=preflight.proof,
        trigger=RoleWakeTriggerKind.SUPERVISION_DEADLINE,
        observed_commit=None,
        handoff_id=None,
        lease_id="lease-vita-feature-001",
        fault_kind=None,
        review_instruction=None,
    )


class _RecordingSubmission:
    def __init__(self) -> None:
        self.requests: list[RoleWakeRequest] = []

    def wake(self, request: RoleWakeRequest) -> RoleWakeResult:
        self.requests.append(request)
        # EFFECT_UNCERTAIN is the one settled-family status the contract
        # admits without a record; the recorder is not a real store.
        return RoleWakeResult(status=RoleWakeStatus.EFFECT_UNCERTAIN)


class TheCoordinatorGateTests(unittest.TestCase):
    """Pin the boundary this defect hid behind: no instruction, no wake."""

    def test_an_instruction_less_handoff_wake_is_refused_before_the_store(
        self,
    ) -> None:
        store = _MemoryWakeStore()
        coordinator = RoleWakeCoordinator(store, _RecordingSubmission())  # type: ignore[arg-type]
        result = coordinator.wake(_handoff_request(None))
        self.assertIs(result.status, RoleWakeStatus.ATTEMPT_CONFLICT)
        self.assertIsNone(store.record, "the store must never see a claim")


class SingleHandoffSubmissionTests(unittest.TestCase):
    def test_a_bare_handoff_wake_gains_a_derived_instruction(self) -> None:
        inner = _RecordingSubmission()
        submission = SingleHandoffReviewSubmission(inner)
        submission.wake(_handoff_request(None))
        self.assertEqual(len(inner.requests), 1)
        forwarded = inner.requests[0]
        instruction = forwarded.review_instruction
        assert instruction is not None
        self.assertEqual(instruction.batch_id, "single-handoff-vita-feature-001")
        self.assertEqual(instruction.trigger_commit, "6" * 40)
        self.assertEqual(len(instruction.clusters), 1)
        cluster = instruction.clusters[0]
        self.assertEqual(cluster.cluster_commit, "6" * 40)
        self.assertEqual(len(cluster.tickets), 1)
        ticket = cluster.tickets[0]
        self.assertEqual(ticket.ticket_ref, forwarded.chain.receipt.ticket_reference)
        self.assertEqual(ticket.receipt_ref, forwarded.chain.receipt.receipt_id)

    def test_the_filled_request_passes_the_coordinator_gate(self) -> None:
        """The derived instruction is a valid model the gate accepts."""

        recorded = _RecordingSubmission()

        class _Gate:
            def wake(self, request: RoleWakeRequest) -> RoleWakeResult:
                trusted = RoleWakeRequest.model_validate(request, strict=True)
                if (
                    trusted.trigger is RoleWakeTriggerKind.REVIEW_HANDOFF
                    and trusted.review_instruction is None
                ):
                    return RoleWakeResult(status=RoleWakeStatus.ATTEMPT_CONFLICT)
                return recorded.wake(trusted)

        result = SingleHandoffReviewSubmission(_Gate()).wake(_handoff_request(None))
        self.assertIs(result.status, RoleWakeStatus.EFFECT_UNCERTAIN)
        self.assertEqual(len(recorded.requests), 1)

    def test_an_already_filled_instruction_is_left_untouched(self) -> None:
        inner = _RecordingSubmission()
        original = _handoff_request(_review_instruction())
        SingleHandoffReviewSubmission(inner).wake(original)
        self.assertEqual(inner.requests, [original])

    def test_a_deadline_wake_passes_through_unchanged(self) -> None:
        inner = _RecordingSubmission()
        original = _deadline_request()
        SingleHandoffReviewSubmission(inner).wake(original)
        self.assertEqual(inner.requests, [original])


if __name__ == "__main__":
    unittest.main()
