"""Integrated supervision acceptance tests without binding the Router."""

from __future__ import annotations

from pathlib import Path
import ast
from tempfile import TemporaryDirectory
import unittest

from library.local_orchestration.git_handoff_event_adapter import (
    GitCliReadbackPort,
    NativeGitRefNotificationFactory,
    NativeGitRefNotificationPort,
    NativeGitRefSignalSink,
)
from library.local_orchestration.one_shot_deadline import (
    DeadlineSignalSink,
    MonotonicClockPort,
    OneShotDeadlineFactory,
    OneShotDeadlinePort,
)
from library.local_orchestration.receipt_bound_supervision import (
    ReceiptBoundSupervisionController,
)
from library.local_orchestration.role_wake_composition import RoleWakeCoordinator
from library.workflow_router.deadline_contracts import (
    DeadlineArmRequest,
    DeadlineArmResult,
    DeadlineArmStatus,
    DeadlineCancelRequest,
    DeadlineCancelResult,
    DeadlineCancelStatus,
    DeadlineFailureKind,
    DeadlineFailureSignal,
    DeadlineSignal,
)
from library.workflow_router.git_handoff_contracts import (
    GitNativeFailureKind,
    GitNativeFailureSignal,
    GitNativeRegistrationRequest,
    GitNativeRegistrationResult,
    GitNativeRegistrationStatus,
    GitRefSignal,
)
from library.workflow_router.role_supervision_contracts import (
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeEffectResult,
    RoleWakeEffectStatus,
)
from library.workflow_router.supervision_policy import (
    ExecutionStartedEvidence,
    SupervisionClass,
    SupervisionDecisionKind,
)
from library.workflow_router.supervision_runtime_contracts import (
    SupervisionPreparationRequest,
    SupervisionPreparationStatus,
    SupervisionRuntimeLifecycle,
    SupervisionStartRequest,
    SupervisionStartStatus,
)
from tests.test_git_handoff_event_adapter import (
    _admission,
    _commit,
    _registration_request,
    _run_git,
)
from tests.test_role_wake_composition import (
    _deadline_capability,
    _MemoryWakeStore,
    _receipt,
    _RecordingWakePort,
    _wake_capability,
)


class _Clock(MonotonicClockPort):
    def __init__(self, value: int = 1_000) -> None:
        self.value = value

    def now_ms(self) -> int:
        return self.value


class _NativePort(NativeGitRefNotificationPort):
    def __init__(self) -> None:
        self.sink: NativeGitRefSignalSink | None = None
        self.requests: list[GitNativeRegistrationRequest] = []
        self.cancelled: list[str] = []

    def register(self, request: GitNativeRegistrationRequest) -> GitNativeRegistrationResult:
        self.requests.append(request)
        return GitNativeRegistrationResult(
            status=GitNativeRegistrationStatus.REGISTERED,
            event_source_ref=request.event_source_ref,
            subscription_id=request.subscription_id,
        )

    def cancel(self, subscription_id: str) -> bool:
        self.cancelled.append(subscription_id)
        return True


class _NativeFactory(NativeGitRefNotificationFactory):
    def __init__(self, port: _NativePort) -> None:
        self.port = port

    def create(self, sink: NativeGitRefSignalSink) -> NativeGitRefNotificationPort:
        self.port.sink = sink
        return self.port


class _DeadlinePort(OneShotDeadlinePort):
    def __init__(self) -> None:
        self.sink: DeadlineSignalSink | None = None
        self.active: DeadlineArmRequest | None = None
        self.arms: list[DeadlineArmRequest] = []
        self.cancelled: list[DeadlineCancelRequest] = []

    def arm(self, request: DeadlineArmRequest) -> DeadlineArmResult:
        status = DeadlineArmStatus.REPLACED if self.active is not None else DeadlineArmStatus.ARMED
        self.active = request
        self.arms.append(request)
        return DeadlineArmResult(status=status, lease_id=request.lease.lease_id)

    def cancel(self, request: DeadlineCancelRequest) -> DeadlineCancelResult:
        self.cancelled.append(request)
        self.active = None
        return DeadlineCancelResult(status=DeadlineCancelStatus.CANCELLED)

    def fire(self) -> None:
        if self.active is None or self.sink is None:
            raise AssertionError("deadline is not armed")
        lease = self.active.lease
        self.active = None
        self.sink.on_deadline(
            DeadlineSignal(
                lease_id=lease.lease_id,
                project_id=lease.project_id,
                ticket_ref=lease.ticket_ref,
                router_receipt_ref=lease.router_receipt_ref,
                task_ref=lease.task_ref,
                fired_at_ms=lease.deadline_ms,
            )
        )

    def fail(self) -> None:
        if self.active is None or self.sink is None:
            raise AssertionError("deadline is not armed")
        lease = self.active.lease
        self.sink.on_deadline_failure(
            DeadlineFailureSignal(
                lease_id=lease.lease_id,
                project_id=lease.project_id,
                ticket_ref=lease.ticket_ref,
                router_receipt_ref=lease.router_receipt_ref,
                task_ref=lease.task_ref,
                failure=DeadlineFailureKind.TIMER_UNAVAILABLE,
            )
        )


class _DeadlineFactory(OneShotDeadlineFactory):
    def __init__(self, port: _DeadlinePort) -> None:
        self.port = port

    def create(self, sink: DeadlineSignalSink) -> OneShotDeadlinePort:
        self.port.sink = sink
        return self.port


def _controller(root: Path) -> tuple[
    ReceiptBoundSupervisionController,
    _NativePort,
    _DeadlinePort,
    _RecordingWakePort,
    _Clock,
]:
    native = _NativePort()
    deadline = _DeadlinePort()
    wake = _RecordingWakePort(
        RoleWakeEffectResult(
            status=RoleWakeEffectStatus.HOST_ACCEPTED,
            delivery_reference="delivery-supervision-reviewer-001",
        )
    )
    clock = _Clock()
    return (
        ReceiptBoundSupervisionController(
            GitCliReadbackPort(root),
            _NativeFactory(native),
            _DeadlineFactory(deadline),
            RoleWakeCoordinator(_MemoryWakeStore(), wake),
            clock,
        ),
        native,
        deadline,
        wake,
        clock,
    )


def _prepare(
    controller: ReceiptBoundSupervisionController,
    baseline: str,
) -> SupervisionPreparationRequest:
    receipt = _receipt().model_copy(update={"baseline_commit": baseline})
    return SupervisionPreparationRequest(
        receipt=receipt,
        registration_request=_registration_request(baseline),
        handoff_context=_admission(
            baseline=baseline,
            observed_handoff_commit=baseline,
        ),
        reviewer_ref="role-supervisor-reviewer",
        implementation_task_ref="task-vita-implementation",
        wake_capability=_wake_capability(receipt),
        deadline_capability=_deadline_capability(receipt),
    )


def _started(baseline: str, started_at_ms: int = 1_000) -> ExecutionStartedEvidence:
    return ExecutionStartedEvidence(
        project_id="prj_0123456789abcdef",
        ticket_ref="ticket-vita-feature-001",
        router_receipt_ref="receipt-vita-feature-001",
        task_ref="task-vita-implementation",
        worktree_ref="worktree-vitafeature-01",
        branch_ref="branch-vitafeature-01",
        baseline_commit=baseline,
        started_at_ms=started_at_ms,
        host_readback_refs=("evidence-execution-start",),
        exact_ticket_received=True,
        task_active=True,
        ticket_executable=True,
        sole_active_receipt=True,
        binding_fresh=True,
    )


class ReceiptBoundSupervisionTests(unittest.TestCase):
    def test_composition_source_has_no_heartbeat_polling_or_active_wait(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "library"
            / "local_orchestration"
            / "receipt_bound_supervision.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertNotIn("heartbeat", source.casefold())
        self.assertNotIn("sleep(", source)
        self.assertNotIn("read_thread", source)
        self.assertNotIn("while ", source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertNotIn("time", imported_roots)

    def test_prepare_does_not_start_time_and_terra_source_activity_is_silent(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "supervision@example.invalid")
            _run_git(root, "config", "user.name", "Supervision")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")
            controller, _native, deadline, wake, clock = _controller(root)
            prepared = controller.prepare(_prepare(controller, baseline))
            self.assertEqual(SupervisionPreparationStatus.PREPARED, prepared.status)
            self.assertEqual([], deadline.arms)

            started = controller.start(
                SupervisionStartRequest(
                    subscription_id="subscription-vita-feature-001",
                    lease_id="lease-vita-feature-001",
                    supervision_class=SupervisionClass.TERRA_OR_HIGHER,
                    execution_started=_started(baseline),
                )
            )
            self.assertEqual(SupervisionStartStatus.ACTIVE, started.status)
            self.assertEqual(1, len(deadline.arms))
            original_deadline = deadline.arms[0].lease.deadline_ms

            clock.value = 20_000
            (root / "source.txt").write_text("baseline\nimplementation\n", encoding="utf-8")
            _commit(root, "source activity")
            controller.on_signal(
                GitRefSignal(
                    event_source_ref="event-source-vita-feature-001",
                    subscription_id="subscription-vita-feature-001",
                )
            )
            state = controller.read_state("subscription-vita-feature-001")
            self.assertIsNotNone(state)
            self.assertEqual(SupervisionRuntimeLifecycle.ACTIVE, state.lifecycle if state else None)
            self.assertGreater(
                state.lease.deadline_ms if state and state.lease else 0,
                original_deadline,
            )
            self.assertEqual(2, len(deadline.arms))
            self.assertEqual([], wake.commands)

    def test_committed_terminal_handoff_closes_and_wakes_reviewer_once(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "supervision@example.invalid")
            _run_git(root, "config", "user.name", "Supervision")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")
            controller, native, deadline, wake, clock = _controller(root)
            controller.prepare(_prepare(controller, baseline))
            controller.start(
                SupervisionStartRequest(
                    subscription_id="subscription-vita-feature-001",
                    lease_id="lease-vita-feature-001",
                    supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
                    execution_started=_started(baseline),
                )
            )
            (root / "source.txt").write_text("baseline\nimplementation\n", encoding="utf-8")
            result_commit = _commit(root, "implementation")
            controller.on_signal(
                GitRefSignal(
                    event_source_ref="event-source-vita-feature-001",
                    subscription_id="subscription-vita-feature-001",
                )
            )
            leaf = seal_handoff_leaf(
                HandoffLeafBody(
                    handoff_id="handoff-vita-feature-001",
                    schema_revision="handoff-schema-v1",
                    project_id="prj_0123456789abcdef",
                    spec_ref="spec-vita-feature",
                    spec_revision="rev-1111111111111111",
                    ticket_ref="ticket-vita-feature-001",
                    ticket_revision="rev-2222222222222222",
                    router_receipt_ref="receipt-vita-feature-001",
                    source_role_ref="role-implementation-owner",
                    source_task_ref="task-vita-implementation",
                    target_role_ref="role-supervisor-reviewer",
                    target_task_ref="task-vita-reviewer",
                    worktree_ref="worktree-vitafeature-01",
                    branch_ref="branch-vitafeature-01",
                    baseline_commit=baseline,
                    result_commit=result_commit,
                    terminal_kind=ImplementationTerminalKind.COMPLETED,
                    previous_handoff_ref=None,
                    supersedes_ref=None,
                    evidence_refs=("evidence-tests-green",),
                    correlation_id="correlation-vita-feature-001",
                )
            )
            leaf_path = root / _registration_request(baseline).reserved_handoff_ref
            leaf_path.parent.mkdir(parents=True)
            leaf_path.write_text(leaf.model_dump_json(indent=2), encoding="utf-8")
            clock.value = 30_000
            _commit(root, "terminal handoff")
            signal = GitRefSignal(
                event_source_ref="event-source-vita-feature-001",
                subscription_id="subscription-vita-feature-001",
            )
            controller.on_signal(signal)
            controller.on_signal(signal)
            state = controller.read_state(signal.subscription_id)
            self.assertIsNotNone(state)
            self.assertEqual(SupervisionRuntimeLifecycle.CLOSED, state.lifecycle if state else None)
            self.assertEqual(1, len(wake.commands))
            self.assertIn("action=REVIEW_HANDOFF", wake.commands[0].payload)
            self.assertEqual(1, len(deadline.cancelled))
            self.assertGreaterEqual(len(native.cancelled), 1)

    def test_luna_deadline_wakes_reviewer_once_and_routes_ticket_repair(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "supervision@example.invalid")
            _run_git(root, "config", "user.name", "Supervision")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")
            controller, _native, deadline, wake, _clock = _controller(root)
            controller.prepare(_prepare(controller, baseline))
            controller.start(
                SupervisionStartRequest(
                    subscription_id="subscription-vita-feature-001",
                    lease_id="lease-vita-feature-001",
                    supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
                    execution_started=_started(baseline),
                )
            )
            deadline.fire()
            state = controller.read_state("subscription-vita-feature-001")
            self.assertIsNotNone(state)
            self.assertEqual(
                SupervisionRuntimeLifecycle.REVIEW_PENDING,
                state.lifecycle if state else None,
            )
            self.assertEqual(
                SupervisionDecisionKind.TICKET_DEFECT_COMPLEXITY_EXCEEDED,
                state.last_supervision_decision.decision
                if state and state.last_supervision_decision
                else None,
            )
            self.assertEqual(1, len(wake.commands))
            self.assertIn("action=SUPERVISION_DEADLINE", wake.commands[0].payload)

    def test_native_capability_loss_fails_closed_and_wakes_named_reviewer(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "supervision@example.invalid")
            _run_git(root, "config", "user.name", "Supervision")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")
            controller, _native, deadline, wake, _clock = _controller(root)
            controller.prepare(_prepare(controller, baseline))
            controller.start(
                SupervisionStartRequest(
                    subscription_id="subscription-vita-feature-001",
                    lease_id="lease-vita-feature-001",
                    supervision_class=SupervisionClass.TERRA_OR_HIGHER,
                    execution_started=_started(baseline),
                )
            )
            controller.on_failure(
                GitNativeFailureSignal(
                    event_source_ref="event-source-vita-feature-001",
                    subscription_id="subscription-vita-feature-001",
                    failure=GitNativeFailureKind.NOTIFICATION_UNAVAILABLE,
                )
            )
            state = controller.read_state("subscription-vita-feature-001")
            self.assertIsNotNone(state)
            self.assertEqual(SupervisionRuntimeLifecycle.HALTED, state.lifecycle if state else None)
            self.assertEqual(1, len(deadline.cancelled))
            self.assertEqual(1, len(wake.commands))
            self.assertIn("action=SUPERVISION_FAULT", wake.commands[0].payload)
            self.assertIn("fault_kind=WAKE_CHAIN_LOST", wake.commands[0].payload)


if __name__ == "__main__":
    unittest.main()
