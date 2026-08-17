"""One-shot monotonic deadline tests with a deterministic clock and timer."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Callable
import unittest

from library.local_orchestration.one_shot_deadline import (
    DeadlineSignalSink,
    MonotonicClockPort,
    MonotonicOneShotDeadlinePort,
    OneShotTimerFactory,
    OneShotTimerPort,
)
from library.workflow_router.deadline_contracts import (
    DeadlineArmRequest,
    DeadlineArmStatus,
    DeadlineCancelStatus,
    DeadlineFailureSignal,
    DeadlineSignal,
    cancel_request_for,
)
from library.workflow_router.role_wake_contracts import (
    DeadlineCapabilityState,
    MonotonicDeadlineCapabilityProof,
)
from library.workflow_router.supervision_policy import (
    ExecutionStartedEvidence,
    LeaseEvent,
    LeaseEventKind,
    SupervisionClass,
    SupervisionLease,
    reduce_supervision_lease,
    start_supervision_lease,
)


class _Clock(MonotonicClockPort):
    def __init__(self, now_ms: int) -> None:
        self.value = now_ms

    def now_ms(self) -> int:
        return self.value


class _Timer(OneShotTimerPort):
    def __init__(self, callback: Callable[[], None]) -> None:
        self.callback = callback
        self.started = False
        self.cancelled = False

    def start(self) -> None:
        self.started = True

    def cancel(self) -> None:
        self.cancelled = True

    def fire(self) -> None:
        self.callback()


class _TimerFactory(OneShotTimerFactory):
    def __init__(self) -> None:
        self.timers: list[_Timer] = []
        self.delays: list[float] = []

    def create(self, delay_seconds: float, callback: Callable[[], None]) -> OneShotTimerPort:
        timer = _Timer(callback)
        self.timers.append(timer)
        self.delays.append(delay_seconds)
        return timer


class _Sink(DeadlineSignalSink):
    def __init__(self) -> None:
        self.signals: list[DeadlineSignal] = []
        self.failures: list[DeadlineFailureSignal] = []

    def on_deadline(self, signal: DeadlineSignal) -> None:
        self.signals.append(signal)

    def on_deadline_failure(self, signal: DeadlineFailureSignal) -> None:
        self.failures.append(signal)


def _lease() -> SupervisionLease:
    decision = start_supervision_lease(
        "lease-vita-ticket-001",
        SupervisionClass.TERRA_OR_HIGHER,
        ExecutionStartedEvidence(
            project_id="prj_0123456789abcdef",
            ticket_ref="ticket-vita-feature-001",
            router_receipt_ref="receipt-vita-feature-001",
            task_ref="task-vita-implementation",
            worktree_ref="worktree-vitafeature-01",
            branch_ref="branch-vitafeature-01",
            baseline_commit="1234567",
            started_at_ms=1_000,
            host_readback_refs=("evidence-execution-start",),
            exact_ticket_received=True,
            task_active=True,
            ticket_executable=True,
            sole_active_receipt=True,
            binding_fresh=True,
        ),
    )
    if decision.lease is None:
        raise AssertionError("lease fixture failed")
    return decision.lease


def _request(lease: SupervisionLease) -> DeadlineArmRequest:
    return DeadlineArmRequest(
        lease=lease,
        capability=MonotonicDeadlineCapabilityProof(
            project_id=lease.project_id,
            ticket_ref=lease.ticket_ref,
            router_receipt_ref=lease.router_receipt_ref,
            implementation_task_ref=lease.task_ref,
            capability_revision="rev-1111111111111111",
            state=DeadlineCapabilityState.PROVEN,
            one_shot_supported=True,
            recurring_callback_required=False,
            evidence_refs=("evidence-deadline-port",),
        ),
    )


class OneShotDeadlineTests(unittest.TestCase):
    def test_arms_once_and_emits_exactly_one_signal(self) -> None:
        lease = _lease()
        clock = _Clock(1_000)
        factory = _TimerFactory()
        sink = _Sink()
        port = MonotonicOneShotDeadlinePort(sink, clock=clock, timer_factory=factory)

        first = port.arm(_request(lease))
        duplicate = port.arm(_request(lease))
        self.assertEqual(DeadlineArmStatus.ARMED, first.status)
        self.assertEqual(DeadlineArmStatus.ARMED, duplicate.status)
        self.assertEqual(1, len(factory.timers))
        self.assertEqual(7_200.0, factory.delays[0])

        clock.value = lease.deadline_ms
        factory.timers[0].fire()
        factory.timers[0].fire()
        self.assertEqual(1, len(sink.signals))
        self.assertEqual(lease.lease_id, sink.signals[0].lease_id)
        self.assertEqual([], sink.failures)

    def test_terra_activity_replaces_old_timer_and_stale_callback_is_silent(self) -> None:
        lease = _lease()
        clock = _Clock(2_000)
        factory = _TimerFactory()
        sink = _Sink()
        port = MonotonicOneShotDeadlinePort(sink, clock=clock, timer_factory=factory)
        self.assertEqual(DeadlineArmStatus.ARMED, port.arm(_request(lease)).status)

        reduced = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.EXACT_REF_ADVANCED, occurred_at_ms=2_000),
        )
        if reduced.lease is None:
            self.fail("activity did not preserve a lease")
        self.assertEqual(DeadlineArmStatus.REPLACED, port.arm(_request(reduced.lease)).status)
        self.assertTrue(factory.timers[0].cancelled)
        factory.timers[0].fire()
        self.assertEqual([], sink.signals)
        clock.value = reduced.lease.deadline_ms
        factory.timers[1].fire()
        self.assertEqual(1, len(sink.signals))

    def test_cancel_is_exact_and_idempotent(self) -> None:
        lease = _lease()
        factory = _TimerFactory()
        sink = _Sink()
        port = MonotonicOneShotDeadlinePort(
            sink,
            clock=_Clock(1_000),
            timer_factory=factory,
        )
        port.arm(_request(lease))
        cancel = cancel_request_for(lease)
        self.assertEqual(DeadlineCancelStatus.CANCELLED, port.cancel(cancel).status)
        self.assertEqual(DeadlineCancelStatus.ALREADY_CLOSED, port.cancel(cancel).status)
        factory.timers[0].fire()
        self.assertEqual([], sink.signals)

    def test_early_platform_callback_fails_closed_without_faking_deadline(self) -> None:
        lease = _lease()
        factory = _TimerFactory()
        sink = _Sink()
        port = MonotonicOneShotDeadlinePort(
            sink,
            clock=_Clock(1_001),
            timer_factory=factory,
        )
        port.arm(_request(lease))
        factory.timers[0].fire()
        self.assertEqual([], sink.signals)
        self.assertEqual(1, len(sink.failures))

    def test_source_has_no_recurring_loop_or_sleep(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "library"
            / "local_orchestration"
            / "one_shot_deadline.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertNotIn("while ", source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("heartbeat", source.casefold())
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("setInterval", calls)


if __name__ == "__main__":
    unittest.main()
