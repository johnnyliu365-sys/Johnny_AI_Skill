"""W2: a verdict is evidence, so it cannot be minted.

Every cell here exists to prove one thing: a recorded verdict implies both a
dispatched receipt and a wake that really reached a host. Neither can be
asserted by the caller.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionStatus,
    admit_dispatch,
    create_dispatch_grant,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.review_return import (
    ReviewReturnFailure,
    ReviewReturnRequest,
    ReviewReturnStatus,
    read_returns,
    returns_path,
    submit_review_return,
)
from library.local_orchestration.review_return_boundary import (
    ReviewReturnScopedDispatchBoundary,
)
from library.workflow_router.live_dispatch_contracts import TicketReceipt
from library.workflow_router.review_inbox_contracts import ReviewTicketVerdict
from library.workflow_router.role_wake_contracts import (
    RoleWakeAttemptClaimRequest,
    RoleWakeAttemptSettleRequest,
    RoleWakeEffectResult,
    RoleWakeEffectStatus,
    derive_role_wake_attempt_identity,
)
from tests.test_dispatch_authority import _repository, _request
from tests.test_role_wake_composition import _receipt
from tests.test_runner_receipt_seeding import _issue_receipt_fixture
from tests.test_senior_review_inbox import _request as _wake_request

_REVIEWED_COMMIT = "a" * 40


def _layout(base: Path) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=(base / "johnny").resolve())
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _metadata(layout: JohnnyRootLayout) -> LiveDispatchMetadataBoundary:
    root = layout.queue_root / "metadata"
    root.mkdir(parents=True, exist_ok=True)
    return LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root.resolve()))


def _deliver_wake(
    layout: JohnnyRootLayout,
    receipt: TicketReceipt,
    effect: RoleWakeEffectStatus = RoleWakeEffectStatus.HOST_ACCEPTED,
) -> None:
    """Record a wake attempt exactly as the coordinator would settle one."""

    boundary = _metadata(layout)
    identity = derive_role_wake_attempt_identity(
        _wake_request(
            ticket_ref=receipt.ticket_reference,
            receipt_ref=receipt.receipt_id,
            task_ref=receipt.implementation_owner_id,
            handoff_id="handoff-w2-001",
            commit=_REVIEWED_COMMIT,
        )
    )
    boundary.claim_role_wake_attempt(RoleWakeAttemptClaimRequest(identity=identity))
    reference = (
        "delivery-w2-001" if effect is RoleWakeEffectStatus.HOST_ACCEPTED else None
    )
    boundary.settle_role_wake_attempt(
        RoleWakeAttemptSettleRequest(
            identity=identity,
            effect=RoleWakeEffectResult(status=effect, delivery_reference=reference),
        )
    )


def _verdict(
    receipt: TicketReceipt,
    verdict: ReviewTicketVerdict = ReviewTicketVerdict.APPROVED,
    commit: str = _REVIEWED_COMMIT,
) -> ReviewReturnRequest:
    return ReviewReturnRequest(
        project_id=receipt.project_id,
        ticket_reference=receipt.ticket_reference,
        ticket_revision=receipt.ticket_revision,
        receipt_id=receipt.receipt_id,
        handoff_id="handoff-w2-001",
        reviewed_commit=commit,
        reviewer_ref="role-supervisor-reviewer",
        verdict=verdict,
    )


class ReceiptEvidenceTests(unittest.TestCase):
    """W2-R1: no dispatch, no verdict."""

    def test_an_undispatched_receipt_records_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            status, failure = submit_review_return(layout, _verdict(_receipt()))
            self.assertIs(status, ReviewReturnStatus.REFUSED)
            self.assertIs(failure, ReviewReturnFailure.RECEIPT_NOT_DISPATCHED)
            self.assertFalse(returns_path(layout).exists())


class WakeEvidenceTests(unittest.TestCase):
    """W2-R2: a verdict for a review nobody was asked to perform is refused."""

    def test_a_dispatched_receipt_without_a_wake_is_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = _receipt()
            _issue_receipt_fixture(_metadata(layout), receipt)
            status, failure = submit_review_return(layout, _verdict(receipt))
            self.assertIs(status, ReviewReturnStatus.REFUSED)
            self.assertIs(failure, ReviewReturnFailure.WAKE_NOT_DELIVERED)
            self.assertFalse(returns_path(layout).exists())

    def test_an_undelivered_wake_is_not_a_delivery(self) -> None:
        for effect in (
            RoleWakeEffectStatus.NO_EFFECT,
            RoleWakeEffectStatus.EFFECT_UNCERTAIN,
        ):
            with self.subTest(effect=effect):
                with TemporaryDirectory() as temporary:
                    layout = _layout(Path(temporary))
                    receipt = _receipt()
                    _issue_receipt_fixture(_metadata(layout), receipt)
                    _deliver_wake(layout, receipt, effect)
                    status, failure = submit_review_return(layout, _verdict(receipt))
                    self.assertIs(status, ReviewReturnStatus.REFUSED)
                    self.assertIs(failure, ReviewReturnFailure.WAKE_NOT_DELIVERED)


class RecordingTests(unittest.TestCase):
    """W2-R3/R4: the verdict records, reads back, and settles its own identity."""

    def _prepared(self, layout: JohnnyRootLayout) -> TicketReceipt:
        receipt = _receipt()
        _issue_receipt_fixture(_metadata(layout), receipt)
        _deliver_wake(layout, receipt)
        return receipt

    def test_a_delivered_review_records_and_reads_back(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = self._prepared(layout)
            status, failure = submit_review_return(layout, _verdict(receipt))
            self.assertIs(status, ReviewReturnStatus.RECORDED, f"{failure}")

            records = read_returns(layout)
            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record.receipt_id, receipt.receipt_id)
            self.assertEqual(record.handoff_id, "handoff-w2-001")
            self.assertEqual(record.reviewed_commit, _REVIEWED_COMMIT)
            self.assertEqual(record.reviewer_ref, "role-supervisor-reviewer")
            self.assertIs(record.verdict, ReviewTicketVerdict.APPROVED)
            self.assertTrue(record.recorded_by)

    def test_an_identical_repeat_records_once(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = self._prepared(layout)
            first, _ = submit_review_return(layout, _verdict(receipt))
            second, _ = submit_review_return(layout, _verdict(receipt))
            self.assertIs(first, ReviewReturnStatus.RECORDED)
            self.assertIs(second, ReviewReturnStatus.ALREADY_RECORDED)
            self.assertEqual(len(read_returns(layout)), 1)

    def test_a_contradicting_verdict_is_refused_and_changes_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = self._prepared(layout)
            submit_review_return(layout, _verdict(receipt))
            status, failure = submit_review_return(
                layout,
                _verdict(receipt, verdict=ReviewTicketVerdict.MODIFY_AND_REOPEN),
            )
            self.assertIs(status, ReviewReturnStatus.REFUSED)
            self.assertIs(failure, ReviewReturnFailure.VERDICT_CONFLICT)
            records = read_returns(layout)
            self.assertEqual(len(records), 1)
            self.assertIs(records[0].verdict, ReviewTicketVerdict.APPROVED)

    def test_a_different_reviewer_returns_separately(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = self._prepared(layout)
            submit_review_return(layout, _verdict(receipt))
            other = _verdict(receipt).model_copy(
                update={"reviewer_ref": "role-second-reviewer"}
            )
            status, _ = submit_review_return(layout, other)
            self.assertIs(status, ReviewReturnStatus.RECORDED)
            self.assertEqual(len(read_returns(layout)), 2)


class ReturnBoundaryIsolationTests(unittest.TestCase):
    """W2-R5: the return path can read, and cannot write."""

    def test_the_facade_exposes_exactly_two_reads(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            boundary = ReviewReturnScopedDispatchBoundary(root)
            self.assertTrue(hasattr(boundary, "read_receipt"))
            self.assertTrue(hasattr(boundary, "read_role_wake_attempt"))
            for forbidden in (
                "issue_receipt",
                "register_artifact",
                "claim_role_wake_attempt",
                "settle_role_wake_attempt",
            ):
                with self.subTest(name=forbidden):
                    self.assertFalse(hasattr(boundary, forbidden))

    def test_the_return_path_binds_exactly_that_facade(self) -> None:
        """The E8 discriminator: assert the runtime object, not the name."""

        from library.local_orchestration import review_return

        captured: list[object] = []
        original = cast(
            "type[ReviewReturnScopedDispatchBoundary]",
            getattr(review_return, "ReviewReturnScopedDispatchBoundary"),
        )

        def _recording(metadata_root: Path) -> ReviewReturnScopedDispatchBoundary:
            instance = original(metadata_root)
            captured.append(instance)
            return instance

        setattr(review_return, "ReviewReturnScopedDispatchBoundary", _recording)
        try:
            with TemporaryDirectory() as temporary:
                layout = _layout(Path(temporary))
                submit_review_return(layout, _verdict(_receipt()))
        finally:
            setattr(review_return, "ReviewReturnScopedDispatchBoundary", original)

        self.assertTrue(captured)
        for bound in captured:
            self.assertIs(type(bound), ReviewReturnScopedDispatchBoundary)
            for forbidden in ("issue_receipt", "settle_role_wake_attempt"):
                with self.subTest(name=forbidden):
                    self.assertFalse(hasattr(bound, forbidden))


class ClosedLoopTests(unittest.TestCase):
    """W2-R6: dispatch, wake, verdict — composed once, end to end."""

    def test_the_loop_closes(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            subprocess.run(
                ("git", "-C", str(repository), "init", "--quiet"),
                check=True,
                capture_output=True,
            )

            admitted = admit_dispatch(layout, _request(repository))
            self.assertIs(admitted.status, DispatchAdmissionStatus.DISPATCHED)
            assert admitted.receipt is not None

            _deliver_wake(layout, admitted.receipt)

            status, failure = submit_review_return(
                layout, _verdict(admitted.receipt)
            )
            self.assertIs(status, ReviewReturnStatus.RECORDED, f"{failure}")
            recorded = read_returns(layout)
            self.assertEqual(len(recorded), 1)
            self.assertEqual(recorded[0].receipt_id, admitted.receipt.receipt_id)


if __name__ == "__main__":
    unittest.main()
