"""Receipt-bound Senior review inbox acceptance tests."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from library.local_orchestration.senior_review_inbox import (
    ReviewClusterBindingResolverPort,
    ReviewWakeSubmissionPort,
    SeniorReviewInboxCoordinator,
    WindowsSeniorReviewInboxStore,
)
from library.workflow_router.review_inbox_contracts import (
    CommittedReviewTicketEvent,
    ReviewBatchClaimRequest,
    ReviewBatchClaimStatus,
    ReviewBatchDecisionRequest,
    ReviewBatchDecisionStatus,
    ReviewClusterId,
    ReviewDependencyNode,
    ReviewEventResolutionRequest,
    ReviewEventResolutionResult,
    ReviewEventResolutionStatus,
    ReviewInboxAdmissionStatus,
    ReviewerActivity,
    ReviewInspectionRequest,
    ReviewInspectionStatus,
    ReviewSourceKind,
    ReviewSourceSection,
    ReviewTicketDecision,
    ReviewTicketInspection,
    ReviewTicketVerdict,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeAttemptLifecycle,
    RoleWakeAttemptRecord,
    RoleWakeChainPreflightRequest,
    RoleWakeRequest,
    RoleWakeResult,
    RoleWakeStatus,
    RoleWakeTriggerKind,
    derive_role_wake_attempt_identity,
    preflight_role_wake_chain,
)
from tests.test_role_wake_composition import (
    _deadline_capability,
    _receipt,
    _registration,
    _wake_capability,
)


_PROJECT = "prj_0123456789abcdef"
_REVIEWER = "role-supervisor-reviewer"
_COMMIT_A = "a" * 40
_COMMIT_B = "b" * 40
_COMMIT_C = "c" * 40


def _sections(ticket_ref: str, commit: str) -> tuple[ReviewSourceSection, ...]:
    suffix = ticket_ref.removeprefix("ticket-")
    return tuple(
        ReviewSourceSection(
            source_kind=kind,
            artifact_ref=f"source-{suffix}-{kind.value.casefold().replace('_', '-')}",
            source_commit=commit,
            section_anchor=f"{kind.value.casefold()}-{suffix}",
            content_digest="sha256_" + character * 64,
        )
        for kind, character in zip(
            ReviewSourceKind,
            ("1", "2", "3", "4", "5"),
            strict=True,
        )
    )


def _event(
    *,
    ticket_ref: str,
    receipt_ref: str,
    task_ref: str,
    handoff_id: str,
    commit: str,
    cluster_id: ReviewClusterId,
    cluster_revision: str,
    graph: tuple[ReviewDependencyNode, ...],
    previous_cluster_revision: str | None = None,
    cluster_commit: str | None = None,
) -> CommittedReviewTicketEvent:
    return CommittedReviewTicketEvent(
        project_id=_PROJECT,
        reviewer_ref=_REVIEWER,
        cluster_id=cluster_id,
        cluster_revision=cluster_revision,
        previous_cluster_revision=previous_cluster_revision,
        cluster_commit=commit if cluster_commit is None else cluster_commit,
        ticket_ref=ticket_ref,
        receipt_ref=receipt_ref,
        implementation_task_ref=task_ref,
        handoff_id=handoff_id,
        event_commit=commit,
        dependency_graph=graph,
        source_sections=_sections(ticket_ref, commit),
    )


def _request(
    *,
    ticket_ref: str,
    receipt_ref: str,
    task_ref: str,
    handoff_id: str,
    commit: str,
) -> RoleWakeRequest:
    receipt = _receipt().model_copy(
        update={
            "ticket_reference": ticket_ref,
            "receipt_id": receipt_ref,
        }
    )
    registration = _registration(receipt).model_copy(
        update={
            "implementation_task_ref": task_ref,
            "last_observed_commit": commit,
        }
    )
    wake = _wake_capability(receipt).model_copy(
        update={
            "bound_implementation_task_ref": task_ref,
        }
    )
    deadline = _deadline_capability(receipt).model_copy(
        update={"implementation_task_ref": task_ref}
    )
    preflight = preflight_role_wake_chain(
        RoleWakeChainPreflightRequest(
            receipt=receipt,
            registration=registration,
            reviewer_ref=_REVIEWER,
            implementation_task_ref=task_ref,
            wake_capability=wake,
            deadline_capability=deadline,
        )
    )
    assert preflight.proof is not None
    return RoleWakeRequest(
        attempt_id=f"wake-{ticket_ref}",
        chain=preflight.proof,
        trigger=RoleWakeTriggerKind.REVIEW_HANDOFF,
        observed_commit=commit,
        handoff_id=handoff_id,
        lease_id=None,
        fault_kind=None,
        review_instruction=None,
    )


class _Resolver(ReviewClusterBindingResolverPort):
    def __init__(self, events: dict[str, CommittedReviewTicketEvent]) -> None:
        self.events = events

    def resolve(self, request: ReviewEventResolutionRequest) -> ReviewEventResolutionResult:
        event = self.events.get(request.ticket_ref)
        if event is None:
            return ReviewEventResolutionResult(
                status=ReviewEventResolutionStatus.REJECTED,
            )
        return ReviewEventResolutionResult(
            status=ReviewEventResolutionStatus.RESOLVED,
            event=event,
        )


class _Wake(ReviewWakeSubmissionPort):
    def __init__(self) -> None:
        self.requests: list[RoleWakeRequest] = []

    def wake(self, request: RoleWakeRequest) -> RoleWakeResult:
        self.requests.append(request)
        return RoleWakeResult(
            status=RoleWakeStatus.HOST_ACCEPTED,
            record=RoleWakeAttemptRecord(
                identity=derive_role_wake_attempt_identity(request),
                lifecycle=RoleWakeAttemptLifecycle.HOST_ACCEPTED,
                delivery_reference="delivery-senior-review-inbox",
            ),
        )


class SeniorReviewInboxTests(unittest.TestCase):
    def test_batch_snapshot_closes_when_senior_claims_not_when_first_wake_is_sent(self) -> None:
        events = {
            ticket: _event(
                ticket_ref=ticket,
                receipt_ref="receipt-" + ticket[-1],
                task_ref="task-" + ticket[-1],
                handoff_id="handoff-" + ticket[-1],
                commit=commit,
                cluster_id="cluster-" + ticket[-1],
                cluster_revision=revision,
                graph=(ReviewDependencyNode(ticket_ref=ticket, depends_on=()),),
            )
            for ticket, commit, revision in (
                ("ticket-a", _COMMIT_A, "rev-1010101010101010"),
                ("ticket-b", _COMMIT_B, "rev-2020202020202020"),
            )
        }
        with TemporaryDirectory() as temporary_directory:
            store = WindowsSeniorReviewInboxStore(Path(temporary_directory).resolve())
            host = _Wake()
            inbox = SeniorReviewInboxCoordinator(store, _Resolver(events), host)
            first = inbox.wake(
                _request(
                    ticket_ref="ticket-a",
                    receipt_ref="receipt-a",
                    task_ref="task-a",
                    handoff_id="handoff-a",
                    commit=_COMMIT_A,
                )
            )
            second = inbox.wake(
                _request(
                    ticket_ref="ticket-b",
                    receipt_ref="receipt-b",
                    task_ref="task-b",
                    handoff_id="handoff-b",
                    commit=_COMMIT_B,
                )
            )
            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, first.status)
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, second.status)
            self.assertEqual(1, len(host.requests))
            claimed = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            assert claimed.batch is not None
            self.assertEqual(
                ("cluster-a", "cluster-b"),
                tuple(item.cluster_id for item in claimed.batch.clusters),
            )

    def test_busy_reviewer_queues_second_cluster_without_second_host_wake(self) -> None:
        graph_a = (ReviewDependencyNode(ticket_ref="ticket-a", depends_on=()),)
        graph_b = (ReviewDependencyNode(ticket_ref="ticket-b", depends_on=()),)
        event_a = _event(
            ticket_ref="ticket-a",
            receipt_ref="receipt-a",
            task_ref="task-a",
            handoff_id="handoff-a",
            commit=_COMMIT_A,
            cluster_id="cluster-a",
            cluster_revision="rev-1111111111111111",
            graph=graph_a,
        )
        event_b = _event(
            ticket_ref="ticket-b",
            receipt_ref="receipt-b",
            task_ref="task-b",
            handoff_id="handoff-b",
            commit=_COMMIT_B,
            cluster_id="cluster-b",
            cluster_revision="rev-2222222222222222",
            graph=graph_b,
        )
        with TemporaryDirectory() as temporary_directory:
            store = WindowsSeniorReviewInboxStore(Path(temporary_directory).resolve())
            host = _Wake()
            inbox = SeniorReviewInboxCoordinator(
                store,
                _Resolver({"ticket-a": event_a, "ticket-b": event_b}),
                host,
            )

            first = inbox.wake(
                _request(
                    ticket_ref="ticket-a",
                    receipt_ref="receipt-a",
                    task_ref="task-a",
                    handoff_id="handoff-a",
                    commit=_COMMIT_A,
                )
            )
            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, first.status)
            self.assertEqual(1, len(host.requests))
            instruction = host.requests[0].review_instruction
            self.assertIsNotNone(instruction)
            assert instruction is not None
            self.assertEqual(("cluster-a",), tuple(item.cluster_id for item in instruction.clusters))

            claimed = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            self.assertEqual(ReviewBatchClaimStatus.CLAIMED, claimed.status)
            self.assertIsNotNone(claimed.batch)

            second = inbox.wake(
                _request(
                    ticket_ref="ticket-b",
                    receipt_ref="receipt-b",
                    task_ref="task-b",
                    handoff_id="handoff-b",
                    commit=_COMMIT_B,
                )
            )
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, second.status)
            self.assertEqual(1, len(host.requests))
            state = store.read_state(_PROJECT, _REVIEWER)
            self.assertIsNotNone(state)
            assert state is not None
            self.assertEqual(ReviewerActivity.ACTIVE_REVIEW, state.activity)

    def test_dependency_cluster_is_reviewed_together_and_decided_after_all_inspections(self) -> None:
        graph = (
            ReviewDependencyNode(ticket_ref="ticket-a", depends_on=()),
            ReviewDependencyNode(ticket_ref="ticket-b", depends_on=("ticket-a",)),
        )
        event_a = _event(
            ticket_ref="ticket-a",
            receipt_ref="receipt-a",
            task_ref="task-a",
            handoff_id="handoff-a",
            commit=_COMMIT_A,
            cluster_id="cluster-ab",
            cluster_revision="rev-3333333333333333",
            graph=graph,
            cluster_commit=_COMMIT_A,
        )
        event_b = _event(
            ticket_ref="ticket-b",
            receipt_ref="receipt-b",
            task_ref="task-b",
            handoff_id="handoff-b",
            commit=_COMMIT_B,
            cluster_id="cluster-ab",
            cluster_revision="rev-3333333333333333",
            graph=graph,
            cluster_commit=_COMMIT_A,
        )
        with TemporaryDirectory() as temporary_directory:
            store = WindowsSeniorReviewInboxStore(Path(temporary_directory).resolve())
            host = _Wake()
            inbox = SeniorReviewInboxCoordinator(
                store,
                _Resolver({"ticket-a": event_a, "ticket-b": event_b}),
                host,
            )
            queued = inbox.wake(
                _request(
                    ticket_ref="ticket-a",
                    receipt_ref="receipt-a",
                    task_ref="task-a",
                    handoff_id="handoff-a",
                    commit=_COMMIT_A,
                )
            )
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, queued.status)
            self.assertEqual([], host.requests)
            awakened = inbox.wake(
                _request(
                    ticket_ref="ticket-b",
                    receipt_ref="receipt-b",
                    task_ref="task-b",
                    handoff_id="handoff-b",
                    commit=_COMMIT_B,
                )
            )
            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, awakened.status)
            self.assertEqual(1, len(host.requests))
            claimed = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            assert claimed.batch is not None
            batch_id = claimed.batch.batch_id

            first_inspection = store.record_inspection(
                ReviewInspectionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    cluster_id="cluster-ab",
                    cluster_revision="rev-3333333333333333",
                    ticket_ref="ticket-a",
                    inspection=ReviewTicketInspection.INSPECTED_FINDINGS,
                    inspection_commit=_COMMIT_C,
                    finding_refs=("finding-a",),
                )
            )
            self.assertEqual(ReviewInspectionStatus.RECORDED, first_inspection.status)
            premature_request = ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=(
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-3333333333333333",
                            ticket_ref="ticket-a",
                            verdict=ReviewTicketVerdict.MODIFY_AND_REOPEN,
                        ),
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-3333333333333333",
                            ticket_ref="ticket-b",
                            verdict=ReviewTicketVerdict.APPROVED,
                        ),
                    ),
                )
            premature = store.decide_batch(premature_request)
            self.assertEqual(ReviewBatchDecisionStatus.REJECTED, premature.status)

            complete = store.record_inspection(
                ReviewInspectionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    cluster_id="cluster-ab",
                    cluster_revision="rev-3333333333333333",
                    ticket_ref="ticket-b",
                    inspection=ReviewTicketInspection.INSPECTED_CLEAN,
                    inspection_commit=_COMMIT_C,
                    finding_refs=(),
                )
            )
            self.assertEqual(ReviewInspectionStatus.BATCH_EVALUATION_READY, complete.status)
            invalid_dependency_decision = store.decide_batch(premature_request)
            self.assertEqual(ReviewBatchDecisionStatus.REJECTED, invalid_dependency_decision.status)
            decided = store.decide_batch(
                ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=(
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-3333333333333333",
                            ticket_ref="ticket-a",
                            verdict=ReviewTicketVerdict.MODIFY_AND_REOPEN,
                        ),
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-3333333333333333",
                            ticket_ref="ticket-b",
                            verdict=ReviewTicketVerdict.BLOCKED_BY_DEPENDENCY,
                        ),
                    ),
                )
            )
            self.assertEqual(ReviewBatchDecisionStatus.DECIDED, decided.status)
            reopened_without_lineage = _event(
                ticket_ref="ticket-a",
                receipt_ref="receipt-a-reopen",
                task_ref="task-a-reopen",
                handoff_id="handoff-a-reopen",
                commit=_COMMIT_C,
                cluster_id="cluster-ab",
                cluster_revision="rev-3434343434343434",
                graph=graph,
            )
            self.assertEqual(
                ReviewInboxAdmissionStatus.REJECTED,
                store.admit_event(reopened_without_lineage).status,
            )
            reopened = reopened_without_lineage.model_copy(
                update={
                    "previous_cluster_revision": "rev-3333333333333333",
                }
            )
            self.assertEqual(
                ReviewInboxAdmissionStatus.QUEUED,
                store.admit_event(reopened).status,
            )

    def test_current_fifo_batch_is_fully_inspected_before_any_decision(self) -> None:
        events = {
            ticket: _event(
                ticket_ref=ticket,
                receipt_ref="receipt-" + ticket[-1],
                task_ref="task-" + ticket[-1],
                handoff_id="handoff-" + ticket[-1],
                commit=commit,
                cluster_id="cluster-" + ticket[-1],
                cluster_revision=revision,
                graph=(ReviewDependencyNode(ticket_ref=ticket, depends_on=()),),
            )
            for ticket, commit, revision in (
                ("ticket-a", _COMMIT_A, "rev-7777777777777777"),
                ("ticket-b", _COMMIT_B, "rev-8888888888888888"),
                ("ticket-c", _COMMIT_C, "rev-9999999999999999"),
            )
        }
        with TemporaryDirectory() as temporary_directory:
            store = WindowsSeniorReviewInboxStore(Path(temporary_directory).resolve())
            host = _Wake()
            inbox = SeniorReviewInboxCoordinator(store, _Resolver(events), host)

            def submit(ticket: str, commit: str) -> RoleWakeResult:
                suffix = ticket[-1]
                return inbox.wake(
                    _request(
                        ticket_ref=ticket,
                        receipt_ref="receipt-" + suffix,
                        task_ref="task-" + suffix,
                        handoff_id="handoff-" + suffix,
                        commit=commit,
                    )
                )

            self.assertEqual(RoleWakeStatus.HOST_ACCEPTED, submit("ticket-a", _COMMIT_A).status)
            first_claim = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            assert first_claim.batch is not None
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, submit("ticket-b", _COMMIT_B).status)
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, submit("ticket-c", _COMMIT_C).status)
            self.assertEqual(1, len(host.requests))

            self.assertEqual(
                ReviewInspectionStatus.BATCH_EVALUATION_READY,
                store.record_inspection(
                    ReviewInspectionRequest(
                        project_id=_PROJECT,
                        reviewer_ref=_REVIEWER,
                        batch_id=first_claim.batch.batch_id,
                        cluster_id="cluster-a",
                        cluster_revision="rev-7777777777777777",
                        ticket_ref="ticket-a",
                        inspection=ReviewTicketInspection.INSPECTED_CLEAN,
                        inspection_commit=_COMMIT_C,
                        finding_refs=(),
                    )
                ).status,
            )
            next_ready = store.decide_batch(
                ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=first_claim.batch.batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=(
                        ReviewTicketDecision(
                            cluster_id="cluster-a",
                            cluster_revision="rev-7777777777777777",
                            ticket_ref="ticket-a",
                            verdict=ReviewTicketVerdict.APPROVED,
                        ),
                    ),
                )
            )
            self.assertEqual(ReviewBatchDecisionStatus.NEXT_BATCH_READY, next_ready.status)
            assert next_ready.next_instruction is not None
            self.assertEqual(
                ("cluster-b", "cluster-c"),
                tuple(cluster.cluster_id for cluster in next_ready.next_instruction.clusters),
            )
            second_claim = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            assert second_claim.batch is not None
            self.assertEqual(
                ("cluster-b", "cluster-c"),
                tuple(cluster.cluster_id for cluster in second_claim.batch.clusters),
            )
            recorded = store.record_inspection(
                ReviewInspectionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=second_claim.batch.batch_id,
                    cluster_id="cluster-b",
                    cluster_revision="rev-8888888888888888",
                    ticket_ref="ticket-b",
                    inspection=ReviewTicketInspection.INSPECTED_CLEAN,
                    inspection_commit=_COMMIT_C,
                    finding_refs=(),
                )
            )
            self.assertEqual(ReviewInspectionStatus.RECORDED, recorded.status)
            premature = store.decide_batch(
                ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=second_claim.batch.batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=(
                        ReviewTicketDecision(
                            cluster_id="cluster-b",
                            cluster_revision="rev-8888888888888888",
                            ticket_ref="ticket-b",
                            verdict=ReviewTicketVerdict.APPROVED,
                        ),
                        ReviewTicketDecision(
                            cluster_id="cluster-c",
                            cluster_revision="rev-9999999999999999",
                            ticket_ref="ticket-c",
                            verdict=ReviewTicketVerdict.APPROVED,
                        ),
                    ),
                )
            )
            self.assertEqual(ReviewBatchDecisionStatus.REJECTED, premature.status)
            self.assertEqual(1, len(host.requests))

    def test_new_committed_dependency_revision_extends_active_cluster_without_wake(self) -> None:
        graph_a = (ReviewDependencyNode(ticket_ref="ticket-a", depends_on=()),)
        graph_ab = (
            ReviewDependencyNode(ticket_ref="ticket-a", depends_on=()),
            ReviewDependencyNode(ticket_ref="ticket-b", depends_on=("ticket-a",)),
        )
        event_a = _event(
            ticket_ref="ticket-a",
            receipt_ref="receipt-a",
            task_ref="task-a",
            handoff_id="handoff-a",
            commit=_COMMIT_A,
            cluster_id="cluster-ab",
            cluster_revision="rev-4444444444444444",
            graph=graph_a,
        )
        event_b = _event(
            ticket_ref="ticket-b",
            receipt_ref="receipt-b",
            task_ref="task-b",
            handoff_id="handoff-b",
            commit=_COMMIT_B,
            cluster_id="cluster-ab",
            cluster_revision="rev-5555555555555555",
            previous_cluster_revision="rev-4444444444444444",
            graph=graph_ab,
        )
        with TemporaryDirectory() as temporary_directory:
            store = WindowsSeniorReviewInboxStore(Path(temporary_directory).resolve())
            host = _Wake()
            inbox = SeniorReviewInboxCoordinator(
                store,
                _Resolver({"ticket-a": event_a, "ticket-b": event_b}),
                host,
            )
            inbox.wake(
                _request(
                    ticket_ref="ticket-a",
                    receipt_ref="receipt-a",
                    task_ref="task-a",
                    handoff_id="handoff-a",
                    commit=_COMMIT_A,
                )
            )
            claimed = store.claim_batch(
                ReviewBatchClaimRequest(project_id=_PROJECT, reviewer_ref=_REVIEWER)
            )
            assert claimed.batch is not None
            batch_id = claimed.batch.batch_id
            ready = store.record_inspection(
                ReviewInspectionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    cluster_id="cluster-ab",
                    cluster_revision="rev-4444444444444444",
                    ticket_ref="ticket-a",
                    inspection=ReviewTicketInspection.INSPECTED_CLEAN,
                    inspection_commit=_COMMIT_C,
                    finding_refs=(),
                )
            )
            self.assertEqual(ReviewInspectionStatus.BATCH_EVALUATION_READY, ready.status)

            revised = inbox.wake(
                _request(
                    ticket_ref="ticket-b",
                    receipt_ref="receipt-b",
                    task_ref="task-b",
                    handoff_id="handoff-b",
                    commit=_COMMIT_B,
                )
            )
            self.assertEqual(RoleWakeStatus.QUEUED_NO_WAKE, revised.status)
            self.assertEqual(1, len(host.requests))
            state = store.read_state(_PROJECT, _REVIEWER)
            assert state is not None and state.active_batch is not None
            self.assertEqual(
                "rev-5555555555555555",
                state.active_batch.clusters[0].cluster_revision,
            )
            cluster = next(item for item in state.clusters if item.cluster_id == "cluster-ab")
            self.assertEqual(ReviewInboxAdmissionStatus.ACTIVE_BATCH_REVISED, store.last_admission_status)
            self.assertTrue(
                all(
                    ticket.inspection is ReviewTicketInspection.PENDING
                    for ticket in cluster.tickets
                )
            )
            stale_decision = store.decide_batch(
                ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=(
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-4444444444444444",
                            ticket_ref="ticket-a",
                            verdict=ReviewTicketVerdict.APPROVED,
                        ),
                    ),
                )
            )
            self.assertEqual(ReviewBatchDecisionStatus.REJECTED, stale_decision.status)
            for ticket_ref in ("ticket-a", "ticket-b"):
                inspected = store.record_inspection(
                    ReviewInspectionRequest(
                        project_id=_PROJECT,
                        reviewer_ref=_REVIEWER,
                        batch_id=batch_id,
                        cluster_id="cluster-ab",
                        cluster_revision="rev-5555555555555555",
                        ticket_ref=ticket_ref,
                        inspection=ReviewTicketInspection.INSPECTED_CLEAN,
                        inspection_commit=_COMMIT_C,
                        finding_refs=(),
                    )
                )
            self.assertEqual(ReviewInspectionStatus.BATCH_EVALUATION_READY, inspected.status)
            decided = store.decide_batch(
                ReviewBatchDecisionRequest(
                    project_id=_PROJECT,
                    reviewer_ref=_REVIEWER,
                    batch_id=batch_id,
                    decision_commit=_COMMIT_C,
                    decisions=tuple(
                        ReviewTicketDecision(
                            cluster_id="cluster-ab",
                            cluster_revision="rev-5555555555555555",
                            ticket_ref=ticket_ref,
                            verdict=ReviewTicketVerdict.APPROVED,
                        )
                        for ticket_ref in ("ticket-a", "ticket-b")
                    ),
                )
            )
            self.assertEqual(ReviewBatchDecisionStatus.DECIDED, decided.status)

    def test_inbox_state_survives_store_reopen(self) -> None:
        event = _event(
            ticket_ref="ticket-a",
            receipt_ref="receipt-a",
            task_ref="task-a",
            handoff_id="handoff-a",
            commit=_COMMIT_A,
            cluster_id="cluster-a",
            cluster_revision="rev-6666666666666666",
            graph=(ReviewDependencyNode(ticket_ref="ticket-a", depends_on=()),),
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve()
            first = WindowsSeniorReviewInboxStore(root)
            admitted = first.admit_event(event)
            self.assertEqual(ReviewInboxAdmissionStatus.WAKE_REQUIRED, admitted.status)
            second = WindowsSeniorReviewInboxStore(root)
            restored = second.read_state(_PROJECT, _REVIEWER)
            self.assertIsNotNone(restored)
            assert restored is not None
            self.assertEqual(ReviewerActivity.WAKE_PENDING, restored.activity)
            self.assertEqual(("cluster-a",), tuple(item.cluster_id for item in restored.clusters))


if __name__ == "__main__":
    unittest.main()
