"""W3: one verdict drives one Router event, and never a second one."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.review_return import (
    ReviewReturnStatus,
    submit_review_return,
)
from library.local_orchestration.review_return_consumption import (
    ConsumptionFailure,
    ConsumptionStatus,
    consume_next_return,
    consumed_path,
    event_id_for,
    pending_returns,
    read_consumed,
)
from library.workflow_router.contracts import RouterEvent, RouterEventKind
from library.workflow_router.review_inbox_contracts import ReviewTicketVerdict
from tests.test_review_return import (
    _deliver_wake,
    _layout,
    _metadata,
    _verdict,
)
from tests.test_role_wake_composition import _receipt
from tests.test_runner_receipt_seeding import _issue_receipt_fixture


def _recorded(
    layout: JohnnyRootLayout,
    verdict: ReviewTicketVerdict = ReviewTicketVerdict.APPROVED,
) -> None:
    """Put one real, evidence-backed verdict on file."""

    receipt = _receipt()
    _issue_receipt_fixture(_metadata(layout), receipt)
    _deliver_wake(layout, receipt)
    status, failure = submit_review_return(layout, _verdict(receipt, verdict=verdict))
    assert status is ReviewReturnStatus.RECORDED, failure


class EmptyStateTests(unittest.TestCase):
    """W3-R1."""

    def test_nothing_pending_writes_no_marker(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            status, event, failure = consume_next_return(layout)
            self.assertIs(status, ConsumptionStatus.NOTHING_PENDING)
            self.assertIsNone(event)
            self.assertIsNone(failure)
            self.assertFalse(consumed_path(layout).exists())


class MappingTests(unittest.TestCase):
    """W3-R2/R3: decisions map, and a non-decision is refused."""

    def test_approved_emits_approval_granted(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)
            status, event, _ = consume_next_return(layout)
            self.assertIs(status, ConsumptionStatus.EMITTED)
            assert event is not None
            self.assertIs(event.kind, RouterEventKind.APPROVAL_GRANTED)

    def test_modify_and_reopen_emits_approval_denied(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout, ReviewTicketVerdict.MODIFY_AND_REOPEN)
            status, event, _ = consume_next_return(layout)
            self.assertIs(status, ConsumptionStatus.EMITTED)
            assert event is not None
            self.assertIs(event.kind, RouterEventKind.APPROVAL_DENIED)

    def test_a_blocked_verdict_is_not_a_decision(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout, ReviewTicketVerdict.BLOCKED_BY_DEPENDENCY)
            status, event, failure = consume_next_return(layout)
            self.assertIs(status, ConsumptionStatus.REFUSED)
            self.assertIsNone(event)
            self.assertIs(failure, ConsumptionFailure.VERDICT_NOT_A_DECISION)
            self.assertFalse(consumed_path(layout).exists())
            self.assertEqual(len(pending_returns(layout)), 1)

    def test_the_event_id_is_deterministic_and_identity_bound(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)
            record = pending_returns(layout)[0]
            expected = event_id_for(record)
            _, event, _ = consume_next_return(layout)
            assert event is not None
            self.assertEqual(event.event_id, expected)
            self.assertEqual(event_id_for(record), expected)
            for part in record.key:
                with self.subTest(part=part):
                    self.assertIn(part, event.event_id)


class ExactlyOnceTests(unittest.TestCase):
    """W3-R4/R5: consumed once, and the marker is durable before the event."""

    def test_the_same_return_never_emits_twice(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)
            first, event, _ = consume_next_return(layout)
            second, absent, _ = consume_next_return(layout)
            self.assertIs(first, ConsumptionStatus.EMITTED)
            assert event is not None
            self.assertIs(second, ConsumptionStatus.NOTHING_PENDING)
            self.assertIsNone(absent)
            self.assertEqual(len(read_consumed(layout)), 1)

    def test_two_returns_each_emit_once_in_file_order(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)
            receipt = _receipt()
            _deliver_wake(layout, receipt)
            second_request = _verdict(receipt).model_copy(
                update={"reviewer_ref": "role-second-reviewer"}
            )
            submit_review_return(layout, second_request)

            ordered = [record.reviewer_ref for record in pending_returns(layout)]
            emitted: list[str] = []
            for _ in range(2):
                status, event, _ = consume_next_return(layout)
                self.assertIs(status, ConsumptionStatus.EMITTED)
                assert event is not None
                emitted.append(event.event_id)
            self.assertIs(consume_next_return(layout)[0], ConsumptionStatus.NOTHING_PENDING)
            self.assertEqual(len(set(emitted)), 2)
            for reviewer, event_id in zip(ordered, emitted, strict=True):
                with self.subTest(reviewer=reviewer):
                    self.assertIn(reviewer, event_id)

    def test_the_marker_is_durable_before_the_caller_sees_the_event(self) -> None:
        """A caller that drops the event on the floor must not get it again.

        This is the ordering the module is built around: mark, then hand
        back. Simulated by discarding the returned event entirely and
        retrying, which is exactly what a crash between the two looks like
        to the next invocation.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)

            before = len(read_consumed(layout))
            status, _dropped, _ = consume_next_return(layout)
            self.assertIs(status, ConsumptionStatus.EMITTED)
            self.assertEqual(len(read_consumed(layout)), before + 1)

            retry, absent, _ = consume_next_return(layout)
            self.assertIs(retry, ConsumptionStatus.NOTHING_PENDING)
            self.assertIsNone(absent)


class RouterAcceptanceTests(unittest.TestCase):
    """W3-R6: the emitted event is a real RouterEvent the engine accepts."""

    def test_the_emitted_event_is_a_validated_router_event(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            _recorded(layout)
            _, event, _ = consume_next_return(layout)
            assert event is not None
            revalidated = RouterEvent.model_validate(event, strict=True)
            self.assertEqual(revalidated.event_id, event.event_id)
            self.assertIs(revalidated.kind, RouterEventKind.APPROVAL_GRANTED)
            self.assertIsNone(revalidated.completion_evidence)
            self.assertIsNone(revalidated.implementation_return)


if __name__ == "__main__":
    unittest.main()
