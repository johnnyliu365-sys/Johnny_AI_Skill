"""W5: exactly-once holds across concurrent callers, not just within one.

The race window sits between reading the pending/consumed state and appending
to it. These cells widen that window deterministically with a barrier placed
inside the read, so two unsynchronized callers would demonstrably both pass
the check — and then assert that the lock makes the interleaving impossible:
the second caller cannot even reach the read until the first has appended.
"""

from __future__ import annotations

import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from library.local_orchestration import review_return, review_return_consumption
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.review_return import (
    ReviewReturnStatus,
    read_returns,
    submit_review_return,
)
from library.local_orchestration.review_return_consumption import (
    ConsumptionStatus,
    consume_next_return,
    read_consumed,
)
from library.workflow_router.contracts import RouterEvent
from tests.test_review_return import _deliver_wake, _layout, _metadata, _verdict
from tests.test_role_wake_composition import _receipt
from tests.test_runner_receipt_seeding import _issue_receipt_fixture


def _widened(
    original: Callable[[JohnnyRootLayout], object],
    barrier: threading.Barrier,
) -> Callable[[JohnnyRootLayout], object]:
    """Hold every caller inside the read until both arrive, or time out.

    Unsynchronized callers both reach the barrier and proceed together —
    the widest possible race. A locked caller keeps the second thread waiting
    at the lock, so the barrier times out and the first proceeds alone, which
    is exactly the serialization being asserted.
    """

    def widened(layout: JohnnyRootLayout) -> object:
        result = original(layout)
        try:
            barrier.wait(timeout=1.0)
        except threading.BrokenBarrierError:
            pass
        return result

    return widened


class ConcurrentConsumptionTests(unittest.TestCase):
    """W5-R1: two consumers, one emission."""

    def test_two_concurrent_consumers_emit_exactly_once(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = _receipt()
            _issue_receipt_fixture(_metadata(layout), receipt)
            _deliver_wake(layout, receipt)
            status, failure = submit_review_return(layout, _verdict(receipt))
            assert status is ReviewReturnStatus.RECORDED, failure

            barrier = threading.Barrier(2)
            original = review_return_consumption.read_consumed
            setattr(
                review_return_consumption,
                "read_consumed",
                _widened(original, barrier),
            )
            outcomes: list[tuple[ConsumptionStatus, RouterEvent | None]] = []
            lock = threading.Lock()

            def consume() -> None:
                consumption, event, _ = consume_next_return(layout)
                with lock:
                    outcomes.append((consumption, event))

            try:
                threads = [threading.Thread(target=consume) for _ in range(2)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=15)
            finally:
                setattr(review_return_consumption, "read_consumed", original)

            statuses = sorted(outcome[0].value for outcome in outcomes)
            self.assertEqual(statuses, ["EMITTED", "NOTHING_PENDING"])
            emitted = [event for _, event in outcomes if event is not None]
            self.assertEqual(len(emitted), 1)
            self.assertEqual(len(read_consumed(layout)), 1)


class ConcurrentSubmissionTests(unittest.TestCase):
    """W5-R2: two identical submits, one record."""

    def test_two_concurrent_identical_submits_record_once(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            receipt = _receipt()
            _issue_receipt_fixture(_metadata(layout), receipt)
            _deliver_wake(layout, receipt)

            barrier = threading.Barrier(2)
            original = review_return.read_returns
            setattr(review_return, "read_returns", _widened(original, barrier))
            outcomes: list[ReviewReturnStatus] = []
            lock = threading.Lock()

            def submit() -> None:
                status, _ = submit_review_return(layout, _verdict(receipt))
                with lock:
                    outcomes.append(status)

            try:
                threads = [threading.Thread(target=submit) for _ in range(2)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=15)
            finally:
                setattr(review_return, "read_returns", original)

            self.assertEqual(
                sorted(status.value for status in outcomes),
                ["ALREADY_RECORDED", "RECORDED"],
            )
            self.assertEqual(len(read_returns(layout)), 1)


if __name__ == "__main__":
    unittest.main()
