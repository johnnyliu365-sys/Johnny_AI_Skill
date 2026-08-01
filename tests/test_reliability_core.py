"""Behaviour tests for the local, fake-backed reliability core."""

from __future__ import annotations

import unittest

from library.功能集群.python.reliability_core import (
    AuditKind,
    ClaimAccepted,
    ClaimRejected,
    EnqueueAccepted,
    EnqueueRejected,
    FakeOutboxSender,
    FakeSenderScenario,
    InMemoryReliabilityCore,
    JobDescription,
    JobStatus,
    JobVersion,
    OutboxRejectionReason,
    OutboxWorker,
    ProcessCompleted,
    ProcessRejected,
    ProcessSenderFailed,
    WorkIdempotencyKey,
    WorkScopeId,
    WorkerId,
)


class ReliabilityCoreTests(unittest.TestCase):
    """Ensure local outbox state fails closed without external side effects."""

    def test_enqueue_claim_and_complete_a_job_once(self) -> None:
        scope = WorkScopeId(value="tenant-sandbox")
        core = InMemoryReliabilityCore.with_scopes(scopes=(scope,))

        enqueue_result = core.enqueue(
            scope=scope,
            idempotency_key=WorkIdempotencyKey(value="order-001"),
            description=JobDescription(value="send local receipt"),
        )
        self.assertIsInstance(enqueue_result, EnqueueAccepted)
        assert isinstance(enqueue_result, EnqueueAccepted)

        worker = OutboxWorker(worker_id=WorkerId(value="worker-a"))
        claim_result = enqueue_result.core.claim(
            job_id=enqueue_result.job.job_id,
            worker_id=worker.worker_id,
        )
        self.assertIsInstance(claim_result, ClaimAccepted)
        assert isinstance(claim_result, ClaimAccepted)

        completed = worker.process(
            core=claim_result.core,
            job_id=claim_result.job.job_id,
            expected_version=claim_result.job.version,
            sender=FakeOutboxSender(scenario=FakeSenderScenario.SUCCESS),
        )
        self.assertIsInstance(completed, ProcessCompleted)
        assert isinstance(completed, ProcessCompleted)
        self.assertEqual(JobStatus.COMPLETED, completed.job.status)
        self.assertEqual(
            (AuditKind.ENQUEUED, AuditKind.CLAIMED, AuditKind.COMPLETED),
            tuple(entry.kind for entry in completed.core.audit_entries),
        )

    def test_duplicate_idempotency_key_and_unknown_scope_are_rejected(self) -> None:
        known_scope = WorkScopeId(value="known-scope")
        unknown_scope = WorkScopeId(value="unknown-scope")
        key = WorkIdempotencyKey(value="same-key")
        core = InMemoryReliabilityCore.with_scopes(scopes=(known_scope,))
        first = core.enqueue(
            scope=known_scope,
            idempotency_key=key,
            description=JobDescription(value="first local job"),
        )
        self.assertIsInstance(first, EnqueueAccepted)
        assert isinstance(first, EnqueueAccepted)

        duplicate = first.core.enqueue(
            scope=known_scope,
            idempotency_key=key,
            description=JobDescription(value="duplicate local job"),
        )
        unknown = first.core.enqueue(
            scope=unknown_scope,
            idempotency_key=WorkIdempotencyKey(value="unknown-key"),
            description=JobDescription(value="unknown scoped job"),
        )

        self.assertIsInstance(duplicate, EnqueueRejected)
        assert isinstance(duplicate, EnqueueRejected)
        self.assertEqual(OutboxRejectionReason.DUPLICATE_IDEMPOTENCY_KEY, duplicate.reason)
        self.assertIsInstance(unknown, EnqueueRejected)
        assert isinstance(unknown, EnqueueRejected)
        self.assertEqual(OutboxRejectionReason.UNKNOWN_SCOPE, unknown.reason)

    def test_only_one_worker_claims_and_stale_expected_version_is_rejected(self) -> None:
        scope = WorkScopeId(value="claim-scope")
        core = InMemoryReliabilityCore.with_scopes(scopes=(scope,))
        enqueue_result = core.enqueue(
            scope=scope,
            idempotency_key=WorkIdempotencyKey(value="claim-key"),
            description=JobDescription(value="claim protected job"),
        )
        self.assertIsInstance(enqueue_result, EnqueueAccepted)
        assert isinstance(enqueue_result, EnqueueAccepted)

        first_worker = WorkerId(value="worker-first")
        first_claim = enqueue_result.core.claim(
            job_id=enqueue_result.job.job_id,
            worker_id=first_worker,
        )
        self.assertIsInstance(first_claim, ClaimAccepted)
        assert isinstance(first_claim, ClaimAccepted)

        second_claim = first_claim.core.claim(
            job_id=first_claim.job.job_id,
            worker_id=WorkerId(value="worker-second"),
        )
        self.assertIsInstance(second_claim, ClaimRejected)
        assert isinstance(second_claim, ClaimRejected)
        self.assertEqual(OutboxRejectionReason.JOB_NOT_PENDING, second_claim.reason)

        stale = first_claim.core.process_claimed(
            job_id=first_claim.job.job_id,
            worker_id=first_worker,
            expected_version=JobVersion(value=0),
            sender=FakeOutboxSender(scenario=FakeSenderScenario.SUCCESS),
        )
        self.assertIsInstance(stale, ProcessRejected)
        assert isinstance(stale, ProcessRejected)
        self.assertEqual(OutboxRejectionReason.STALE_EXPECTED_VERSION, stale.reason)

    def test_sender_failure_is_auditable_and_emergency_stop_blocks_without_sending(self) -> None:
        scope = WorkScopeId(value="safety-scope")
        core = InMemoryReliabilityCore.with_scopes(scopes=(scope,))
        failed_enqueue = core.enqueue(
            scope=scope,
            idempotency_key=WorkIdempotencyKey(value="failure-key"),
            description=JobDescription(value="record local sender failure"),
        )
        self.assertIsInstance(failed_enqueue, EnqueueAccepted)
        assert isinstance(failed_enqueue, EnqueueAccepted)
        failed_claim = failed_enqueue.core.claim(
            job_id=failed_enqueue.job.job_id,
            worker_id=WorkerId(value="failure-worker"),
        )
        self.assertIsInstance(failed_claim, ClaimAccepted)
        assert isinstance(failed_claim, ClaimAccepted)
        failed_process = failed_claim.core.process_claimed(
            job_id=failed_claim.job.job_id,
            worker_id=WorkerId(value="failure-worker"),
            expected_version=failed_claim.job.version,
            sender=FakeOutboxSender(scenario=FakeSenderScenario.FAILURE),
        )
        self.assertIsInstance(failed_process, ProcessSenderFailed)
        assert isinstance(failed_process, ProcessSenderFailed)
        self.assertEqual(JobStatus.FAILED, failed_process.job.status)
        self.assertEqual(AuditKind.SENDER_FAILED, failed_process.core.audit_entries[-1].kind)

        stopped_enqueue = failed_process.core.enqueue(
            scope=scope,
            idempotency_key=WorkIdempotencyKey(value="stop-key"),
            description=JobDescription(value="must not be sent after stop"),
        )
        self.assertIsInstance(stopped_enqueue, EnqueueAccepted)
        assert isinstance(stopped_enqueue, EnqueueAccepted)
        stopped_claim = stopped_enqueue.core.claim(
            job_id=stopped_enqueue.job.job_id,
            worker_id=WorkerId(value="stopped-worker"),
        )
        self.assertIsInstance(stopped_claim, ClaimAccepted)
        assert isinstance(stopped_claim, ClaimAccepted)
        stopped_core = stopped_claim.core.activate_emergency_stop()
        sender = FakeOutboxSender(scenario=FakeSenderScenario.SUCCESS)

        blocked = stopped_core.process_claimed(
            job_id=stopped_claim.job.job_id,
            worker_id=WorkerId(value="stopped-worker"),
            expected_version=stopped_claim.job.version,
            sender=sender,
        )
        self.assertIsInstance(blocked, ProcessRejected)
        assert isinstance(blocked, ProcessRejected)
        self.assertEqual(OutboxRejectionReason.JOB_NOT_CLAIMED, blocked.reason)
        self.assertEqual(0, sender.delivery_attempt_count)
        blocked_job = stopped_core.job(job_id=stopped_claim.job.job_id)
        self.assertEqual(JobStatus.BLOCKED, blocked_job.status)
        self.assertEqual(AuditKind.BLOCKED_BY_EMERGENCY_STOP, stopped_core.audit_entries[-1].kind)


if __name__ == "__main__":
    unittest.main()
