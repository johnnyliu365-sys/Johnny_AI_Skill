"""CLOSURE-E8-02/03 tests: the runner verifies claimability and mints nothing.

`_issue_receipt_fixture` below is the dispatch-authority stand-in for tests:
it drives the control-plane store directly, exactly like the established
05B-series fixtures, and it exists only in test code.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import runner_receipt_seeding
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.live_dispatch_metadata_store import (
    LiveDispatchMetadataStore,
)
from library.local_orchestration.role_wake_composition import (
    DurableRoleWakeAttemptStore,
)
from library.local_orchestration.runner_receipt_seeding import (
    ReceiptVerificationFailure,
    ReceiptVerificationStatus,
    verify_receipt_claimable,
)
from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    TicketReceipt,
    TicketReceiptIssueRequest,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeAttemptClaimRequest,
    WakeAttemptClaimStatus,
    derive_role_wake_attempt_identity,
)
from tests.test_role_wake_composition import _receipt
from tests.test_senior_review_inbox import _request


def _boundary(root: Path) -> LiveDispatchMetadataBoundary:
    return LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root.resolve(strict=True)))


def _issue_receipt_fixture(
    boundary: LiveDispatchMetadataBoundary, receipt: TicketReceipt
) -> None:
    """Dispatch-authority stand-in: register and issue through the store."""

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
    store = LiveDispatchMetadataStore(boundary)
    store.register_artifact(
        ApprovedDispatchArtifactRegisterRequest(artifact=artifact)
    )
    store.issue_receipt(
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


class ReceiptVerificationTests(unittest.TestCase):
    def test_dispatched_receipt_verifies_and_admits_a_wake_claim(self) -> None:
        """CR-E6-01 causal chain: dispatched → claimable → claim succeeds."""

        receipt = _receipt()
        wake_request = _request(
            ticket_ref=receipt.ticket_reference,
            receipt_ref=receipt.receipt_id,
            task_ref=receipt.implementation_owner_id,
            handoff_id="handoff-e8-001",
            commit="a" * 40,
        )
        identity = derive_role_wake_attempt_identity(wake_request)
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            _issue_receipt_fixture(boundary, receipt)
            status, failure = verify_receipt_claimable(boundary, receipt)
            self.assertIs(status, ReceiptVerificationStatus.CLAIMABLE)
            self.assertIsNone(failure)
            claim = DurableRoleWakeAttemptStore(boundary).claim(
                RoleWakeAttemptClaimRequest(identity=identity)
            )
            self.assertIsNot(claim.status, WakeAttemptClaimStatus.ATTEMPT_CONFLICT)
            self.assertIsNotNone(claim.record)

    def test_undispatched_receipt_is_refused_and_cannot_claim(self) -> None:
        receipt = _receipt()
        wake_request = _request(
            ticket_ref=receipt.ticket_reference,
            receipt_ref=receipt.receipt_id,
            task_ref=receipt.implementation_owner_id,
            handoff_id="handoff-e8-002",
            commit="b" * 40,
        )
        identity = derive_role_wake_attempt_identity(wake_request)
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            status, failure = verify_receipt_claimable(boundary, receipt)
            self.assertIs(status, ReceiptVerificationStatus.BLOCKED)
            self.assertIs(failure, ReceiptVerificationFailure.RECEIPT_NOT_FOUND)
            claim = DurableRoleWakeAttemptStore(boundary).claim(
                RoleWakeAttemptClaimRequest(identity=identity)
            )
            self.assertIs(claim.status, WakeAttemptClaimStatus.ATTEMPT_CONFLICT)

    def test_verification_is_repeatable_and_writes_no_approved_state(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            boundary = _boundary(root)
            verify_receipt_claimable(boundary, receipt)
            for path in root.rglob("*"):
                if path.is_file():
                    body = path.read_text(encoding="utf-8", errors="replace")
                    self.assertNotIn(receipt.receipt_id, body)
                    self.assertNotIn(receipt.ticket_reference, body)
            self.assertIs(
                verify_receipt_claimable(boundary, receipt)[0],
                ReceiptVerificationStatus.BLOCKED,
            )

    def test_a_different_receipt_id_for_the_same_ticket_mismatches(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            _issue_receipt_fixture(boundary, receipt)
            foreign = receipt.model_copy(
                update={"receipt_id": "receipt-vita-feature-999"}
            )
            status, failure = verify_receipt_claimable(boundary, foreign)
            self.assertIs(status, ReceiptVerificationStatus.BLOCKED)
            self.assertIs(failure, ReceiptVerificationFailure.RECEIPT_MISMATCH)


class VerificationModuleSurfaceTests(unittest.TestCase):
    """P0 (rounds three and four): the verification module exposes reads only."""

    def test_the_module_exports_verification_only(self) -> None:
        self.assertEqual(
            runner_receipt_seeding.__all__,
            [
                "ReceiptReadPort",
                "ReceiptVerificationFailure",
                "ReceiptVerificationStatus",
                "verify_receipt_claimable",
            ],
        )
        for forbidden in ("issue_dispatch_receipt", "seed_receipt"):
            self.assertFalse(hasattr(runner_receipt_seeding, forbidden))


if __name__ == "__main__":
    unittest.main()
