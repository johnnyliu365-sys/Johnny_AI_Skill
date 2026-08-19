"""E8 closure tests: the runner makes its subscription receipt claimable."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.role_wake_composition import (
    DurableRoleWakeAttemptStore,
)
from library.local_orchestration.runner_receipt_seeding import (
    ReceiptSeedFailure,
    ReceiptSeedStatus,
    issue_dispatch_receipt,
    verify_receipt_claimable,
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


class RunnerReceiptSeedingTests(unittest.TestCase):
    def test_seeding_makes_a_wake_claim_admissible(self) -> None:
        """CR-E6-01: without seeding the claim conflicts; with it, it claims."""

        receipt = _receipt()
        wake_request = _request(
            ticket_ref=receipt.ticket_reference,
            receipt_ref=receipt.receipt_id,
            task_ref=receipt.implementation_owner_id,
            handoff_id="handoff-e8-001",
            commit="a" * 40,
        )
        identity = derive_role_wake_attempt_identity(wake_request)

        with self.subTest(stage="unseeded_boundary_refuses"):
            with TemporaryDirectory() as temporary:
                boundary = _boundary(Path(temporary))
                store = DurableRoleWakeAttemptStore(boundary)
                claim = store.claim(RoleWakeAttemptClaimRequest(identity=identity))
                self.assertIs(claim.status, WakeAttemptClaimStatus.ATTEMPT_CONFLICT)

        with self.subTest(stage="seeded_boundary_admits"):
            with TemporaryDirectory() as temporary:
                boundary = _boundary(Path(temporary))
                status, failure = issue_dispatch_receipt(boundary, receipt)
                self.assertIs(status, ReceiptSeedStatus.SEEDED)
                self.assertIsNone(failure)
                store = DurableRoleWakeAttemptStore(boundary)
                claim = store.claim(RoleWakeAttemptClaimRequest(identity=identity))
                self.assertIsNot(
                    claim.status, WakeAttemptClaimStatus.ATTEMPT_CONFLICT
                )
                self.assertIsNotNone(claim.record)

    def test_seeding_is_idempotent(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            first, _ = issue_dispatch_receipt(boundary, receipt)
            second, failure = issue_dispatch_receipt(boundary, receipt)
            self.assertIs(first, ReceiptSeedStatus.SEEDED)
            self.assertIs(second, ReceiptSeedStatus.ALREADY_PRESENT)
            self.assertIsNone(failure)

    def test_a_foreign_receipt_for_the_same_ticket_is_a_mismatch(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            self.assertIs(issue_dispatch_receipt(boundary, receipt)[0], ReceiptSeedStatus.SEEDED)
            foreign = receipt.model_copy(
                update={"receipt_id": "receipt-vita-feature-999"}
            )
            status, failure = issue_dispatch_receipt(boundary, foreign)
            self.assertIs(status, ReceiptSeedStatus.BLOCKED)
            self.assertIn(
                failure,
                (
                    ReceiptSeedFailure.RECEIPT_ISSUE_FAILED,
                    ReceiptSeedFailure.RECEIPT_MISMATCH,
                ),
            )


if __name__ == "__main__":
    unittest.main()


class RunnerNeverMintsAuthorityTests(unittest.TestCase):
    """P0: the runner verifies a receipt; it must not create one."""

    def test_verification_refuses_an_undispatched_receipt(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            status, failure = verify_receipt_claimable(boundary, receipt)
            self.assertIs(status, ReceiptSeedStatus.BLOCKED)
            self.assertIs(failure, ReceiptSeedFailure.READBACK_FAILED)

    def test_verification_creates_no_approved_state(self) -> None:
        """Verification may touch its own lock file, but never authority."""

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
                ReceiptSeedStatus.BLOCKED,
            )

    def test_a_dispatched_receipt_then_verifies(self) -> None:
        receipt = _receipt()
        with TemporaryDirectory() as temporary:
            boundary = _boundary(Path(temporary))
            self.assertIs(
                issue_dispatch_receipt(boundary, receipt)[0],
                ReceiptSeedStatus.SEEDED,
            )
            self.assertIs(
                verify_receipt_claimable(boundary, receipt)[0],
                ReceiptSeedStatus.ALREADY_PRESENT,
            )
