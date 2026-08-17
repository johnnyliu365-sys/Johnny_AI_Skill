from __future__ import annotations

import ast
from pathlib import Path
from typing import cast
from unittest import TestCase

from library.local_orchestration.git_handoff_event_adapter import ReceiptBoundGitEventAdapter
from library.local_orchestration.project_runner_registry import (
    ProjectRunnerRegistry,
    RunnerStartResult,
    RunnerStarted,
    RunnerStopCapabilityUnavailable,
    RunnerStopResult,
    RunnerStopped,
)
from library.local_orchestration.project_subscription_runtime import (
    ProjectSubscriptionDecision,
    ProjectSubscriptionFailure,
    ProjectSubscriptionRegistrationRequest,
    ProjectSubscriptionResult,
    ProjectSubscriptionRuntime,
    ProjectSubscriptionState,
)
from library.workflow_router.git_handoff_contracts import (
    GitEventAdapterDecision,
    GitEventAdapterDecisionKind,
    GitEventRegistrationLifecycle,
    GitEventRegistrationState,
    GitObservationMode,
    GitRefRegistrationRequest,
    GitRefSignal,
    SupervisionFault,
    SupervisionFaultKind,
)
from library.workflow_router.live_dispatch_contracts import ReceiptLifecycle, TicketReceipt
from library.workflow_router.role_supervision_contracts import (
    HandoffAdmissionContext,
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)


_PROJECT_ALPHA = "prj_0123456789abcdef"
_PROJECT_BETA = "prj_fedcba9876543210"
_BASELINE = "abcdef1"
_COMMIT = "abcdef2"


class _RecordingLifecycle:
    def __init__(
        self,
        stop_result: RunnerStopResult | None = None,
        stop_results: tuple[RunnerStopResult, ...] = (),
    ) -> None:
        self.starts: list[str] = []
        self.stops: list[tuple[str, str]] = []
        self.stop_result = stop_result or RunnerStopped()
        self.stop_results = list(stop_results)

    def start(self, project_ref: str) -> RunnerStartResult:
        self.starts.append(project_ref)
        return RunnerStarted(runner_ref="runner-pd06")

    def stop(self, project_ref: str, runner_ref: str) -> RunnerStopResult:
        self.stops.append((project_ref, runner_ref))
        if self.stop_results:
            return self.stop_results.pop(0)
        return self.stop_result


def _receipt(project_id: str = _PROJECT_ALPHA) -> TicketReceipt:
    return TicketReceipt(
        project_id=project_id,
        receipt_id="receipt-pd06",
        ticket_reference="ticket-pd06",
        ticket_revision="rev-0123456789abcdef",
        ticket_digest="sha256_" + "1" * 64,
        ticket_document_commit=_BASELINE,
        handoff_reference="handoff-pd06",
        handoff_revision="rev-fedcba9876543210",
        handoff_digest="sha256_" + "2" * 64,
        handoff_document_commit=_COMMIT,
        baseline_commit=_BASELINE,
        implementation_owner_id="role-impl-pd06",
        expected_return="return-completed",
        descriptor_binding="binding-pd06",
        correlation_id="corr-pd06",
        dispatch_question_id="question-pd06",
        worktree_fingerprint="worktree-pd06-01",
        branch_fingerprint="branch-pd06-01",
        lifecycle=ReceiptLifecycle.ACTIVE,
    )


def _context(
    project_id: str = _PROJECT_ALPHA,
    target_task_ref: str | None = "task-target-pd06",
) -> HandoffAdmissionContext:
    return HandoffAdmissionContext(
        project_id=project_id,
        spec_ref="spec-pd06",
        spec_revision="rev-0123456789abcdef",
        ticket_ref="ticket-pd06",
        ticket_revision="rev-0123456789abcdef",
        router_receipt_ref="receipt-pd06",
        source_role_ref="role-source-pd06",
        source_task_ref="task-source-pd06",
        target_role_ref="role-impl-pd06",
        target_task_ref=target_task_ref,
        worktree_ref="worktree-pd06-01",
        branch_ref="branch-pd06-01",
        baseline_commit=_BASELINE,
        correlation_id="corr-pd06",
        observed_handoff_commit=_COMMIT,
        result_descends_from_baseline=True,
        handoff_descends_from_result=True,
        reserved_path_changed=True,
        consumed_handoff_ids=(),
    )


def _git_request(
    project_id: str = _PROJECT_ALPHA,
    subscription_id: str = "subscription-pd06",
) -> GitRefRegistrationRequest:
    return GitRefRegistrationRequest(
        event_source_ref="event-source-pd06",
        subscription_id=subscription_id,
        project_id=project_id,
        ticket_ref="ticket-pd06",
        router_receipt_ref="receipt-pd06",
        implementation_task_ref="task-target-pd06",
        worktree_ref="worktree-pd06-01",
        branch_ref="branch-pd06-01",
        baseline_commit=_BASELINE,
        correlation_id="corr-pd06",
        exact_git_ref="refs/heads/main",
        reserved_handoff_ref="doc/handoffs/2026/pd06/handoff.json",
    )


def _request(
    project_id: str = _PROJECT_ALPHA,
    receipt_project_id: str = _PROJECT_ALPHA,
) -> ProjectSubscriptionRegistrationRequest:
    return ProjectSubscriptionRegistrationRequest(
        receipt=_receipt(receipt_project_id),
        git_request=_git_request(project_id),
        handoff_context=_context(project_id),
    )


def _registration(request: GitRefRegistrationRequest) -> GitEventRegistrationState:
    return GitEventRegistrationState(
        event_source_ref=request.event_source_ref,
        subscription_id=request.subscription_id,
        project_id=request.project_id,
        ticket_ref=request.ticket_ref,
        router_receipt_ref=request.router_receipt_ref,
        implementation_task_ref=request.implementation_task_ref,
        worktree_ref=request.worktree_ref,
        branch_ref=request.branch_ref,
        baseline_commit=request.baseline_commit,
        correlation_id=request.correlation_id,
        exact_git_ref=request.exact_git_ref,
        reserved_handoff_ref=request.reserved_handoff_ref,
        mode=GitObservationMode.NATIVE_REF_EVENT,
        lifecycle=GitEventRegistrationLifecycle.ACTIVE,
        last_observed_commit=request.baseline_commit,
        consumed_handoff_ids=(),
        fault_emitted=False,
    )


def _fault(state: GitEventRegistrationState, kind: SupervisionFaultKind) -> SupervisionFault:
    return SupervisionFault(
        kind=kind,
        event_source_ref=state.event_source_ref,
        subscription_id=state.subscription_id,
        ticket_ref=state.ticket_ref,
        router_receipt_ref=state.router_receipt_ref,
        observed_commit=_COMMIT,
    )


class _FakeGitAdapter(ReceiptBoundGitEventAdapter):
    def __init__(
        self,
        observed: GitEventAdapterDecisionKind = GitEventAdapterDecisionKind.SILENT,
        malformed: bool = False,
    ) -> None:
        self.register_calls = 0
        self.observe_calls = 0
        self.close_calls: list[str] = []
        self.observed = observed
        self.malformed = malformed

    def register(
        self,
        request: GitRefRegistrationRequest,
        context: HandoffAdmissionContext,
    ) -> GitEventAdapterDecision:
        del context
        self.register_calls += 1
        return GitEventAdapterDecision(
            decision=GitEventAdapterDecisionKind.REGISTERED,
            registration=_registration(request),
        )

    def observe_signal(
        self,
        state: GitEventRegistrationState,
        signal: GitRefSignal,
        context: HandoffAdmissionContext,
    ) -> GitEventAdapterDecision:
        del context
        self.observe_calls += 1
        if (
            signal.event_source_ref != state.event_source_ref
            or signal.subscription_id != state.subscription_id
        ):
            return GitEventAdapterDecision(
                decision=GitEventAdapterDecisionKind.SILENT,
                registration=state,
            )
        if self.malformed:
            return cast(
                GitEventAdapterDecision,
                GitEventAdapterDecision.model_construct(
                    decision=GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED,
                    registration=state,
                    handoff=None,
                ),
            )
        if self.observed in (
            GitEventAdapterDecisionKind.INVALID_HANDOFF_FAULT,
            GitEventAdapterDecisionKind.STALE_BINDING_FAULT,
        ):
            fault_kind = (
                SupervisionFaultKind.INVALID_HANDOFF
                if self.observed is GitEventAdapterDecisionKind.INVALID_HANDOFF_FAULT
                else SupervisionFaultKind.STALE_BINDING
            )
            return GitEventAdapterDecision(
                decision=self.observed,
                registration=state,
                fault=_fault(state, fault_kind),
            )
        if self.observed is GitEventAdapterDecisionKind.READBACK_FAILED:
            return GitEventAdapterDecision(
                decision=self.observed,
                registration=state.model_copy(
                    update={"lifecycle": GitEventRegistrationLifecycle.CLOSED}
                ),
            )
        if self.observed is GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED:
            leaf = seal_handoff_leaf(
                HandoffLeafBody(
                    handoff_id="handoff-leaf-pd06",
                    schema_revision="handoff-schema-v1",
                    project_id=state.project_id,
                    spec_ref="spec-pd06",
                    spec_revision="rev-0123456789abcdef",
                    ticket_ref=state.ticket_ref,
                    ticket_revision="rev-0123456789abcdef",
                    router_receipt_ref=state.router_receipt_ref,
                    source_role_ref="role-source-pd06",
                    source_task_ref="task-source-pd06",
                    target_role_ref="role-impl-pd06",
                    target_task_ref="task-target-pd06",
                    worktree_ref=state.worktree_ref,
                    branch_ref=state.branch_ref,
                    result_commit=_COMMIT,
                    baseline_commit=state.baseline_commit,
                    terminal_kind=ImplementationTerminalKind.COMPLETED,
                    previous_handoff_ref=None,
                    supersedes_ref=None,
                    evidence_refs=("evidence-pd06",),
                    correlation_id=state.correlation_id,
                )
            )
            return GitEventAdapterDecision(
                decision=self.observed,
                registration=state,
                handoff=leaf,
            )
        return GitEventAdapterDecision(decision=self.observed, registration=state)

    def close(self, state: GitEventRegistrationState) -> GitEventRegistrationState:
        self.close_calls.append(state.subscription_id)
        return state.model_copy(update={"lifecycle": GitEventRegistrationLifecycle.CLOSED})


def _runtime(
    adapter: _FakeGitAdapter,
    lifecycle: _RecordingLifecycle | None = None,
) -> tuple[ProjectSubscriptionRuntime, _RecordingLifecycle]:
    actual_lifecycle = lifecycle or _RecordingLifecycle()
    return ProjectSubscriptionRuntime(ProjectRunnerRegistry(actual_lifecycle), adapter), actual_lifecycle


class ProjectSubscriptionRuntimeTests(TestCase):
    def test_exact_receipt_project_binding_is_required_before_effects(self) -> None:
        adapter = _FakeGitAdapter()
        runtime, lifecycle = _runtime(adapter)

        result = runtime.register(_request(project_id=_PROJECT_BETA))

        self.assertEqual(ProjectSubscriptionDecision.REJECTED, result.decision)
        self.assertEqual(ProjectSubscriptionFailure.INVALID_BINDING, result.failure)
        self.assertIsNone(result.state)
        self.assertEqual(0, adapter.register_calls)
        self.assertEqual([], lifecycle.starts)

    def test_exact_registration_round_trips_and_binds_one_runner(self) -> None:
        adapter = _FakeGitAdapter()
        runtime, lifecycle = _runtime(adapter)

        result = runtime.register(_request())

        self.assertEqual(ProjectSubscriptionDecision.REGISTERED, result.decision)
        self.assertIsNotNone(result.state)
        self.assertEqual([_PROJECT_ALPHA], lifecycle.starts)
        self.assertEqual(result, ProjectSubscriptionResult.model_validate_json(result.model_dump_json()))
        state = cast(ProjectSubscriptionState, result.state)
        self.assertEqual(_PROJECT_ALPHA, state.receipt.project_id)
        self.assertEqual("subscription-pd06", state.registration.subscription_id)
        self.assertEqual("runner-pd06", state.runner_ref)

    def test_ordinary_source_commit_is_silent_and_retains_state(self) -> None:
        adapter = _FakeGitAdapter(GitEventAdapterDecisionKind.SOURCE_ADVANCED)
        runtime, lifecycle = _runtime(adapter)
        registered = runtime.register(_request())
        state = cast(ProjectSubscriptionState, registered.state)

        observed = runtime.observe(
            state,
            GitRefSignal(event_source_ref="event-source-pd06", subscription_id="subscription-pd06"),
        )

        self.assertEqual(ProjectSubscriptionDecision.SILENT, observed.decision)
        self.assertEqual(state, observed.state)
        self.assertEqual(1, adapter.observe_calls)
        self.assertEqual([], lifecycle.stops)

    def test_only_valid_terminal_handoff_is_a_completion_candidate(self) -> None:
        adapter = _FakeGitAdapter(GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED)
        runtime, _ = _runtime(adapter)
        registered = runtime.register(_request())
        state = cast(ProjectSubscriptionState, registered.state)

        candidate = runtime.observe(
            state,
            GitRefSignal(event_source_ref="event-source-pd06", subscription_id="subscription-pd06"),
        )

        self.assertEqual(ProjectSubscriptionDecision.COMPLETION_CANDIDATE, candidate.decision)
        self.assertIsNotNone(candidate.git_decision)

    def test_two_subscriptions_close_only_their_own_runner_and_git_registration(self) -> None:
        first_adapter = _FakeGitAdapter()
        second_adapter = _FakeGitAdapter()
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)
        first_runtime = ProjectSubscriptionRuntime(registry, first_adapter)
        second_runtime = ProjectSubscriptionRuntime(registry, second_adapter)
        first = first_runtime.register(_request())
        second_request = _request().model_copy(
            update={"git_request": _git_request(subscription_id="subscription-pd06-two")}
        )
        second = second_runtime.register(second_request)

        first_state = cast(ProjectSubscriptionState, first.state)
        second_state = cast(ProjectSubscriptionState, second.state)
        first_closed = first_runtime.close(first_state)
        second_closed = second_runtime.close(second_state)

        self.assertEqual(ProjectSubscriptionDecision.CLOSED, first_closed.decision)
        self.assertEqual(ProjectSubscriptionDecision.CLOSED, second_closed.decision)
        self.assertEqual(["subscription-pd06"], first_adapter.close_calls)
        self.assertEqual(["subscription-pd06-two"], second_adapter.close_calls)
        self.assertEqual([(_PROJECT_ALPHA, "runner-pd06")], lifecycle.stops)

    def test_foreign_signal_is_silent_without_runner_or_peer_mutation(self) -> None:
        adapter = _FakeGitAdapter(GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED)
        runtime, lifecycle = _runtime(adapter)
        registered = runtime.register(_request())
        state = cast(ProjectSubscriptionState, registered.state)

        observed = runtime.observe(
            state,
            GitRefSignal(event_source_ref="event-source-foreign", subscription_id="subscription-foreign"),
        )

        self.assertEqual(ProjectSubscriptionDecision.SILENT, observed.decision)
        self.assertEqual(state, observed.state)
        self.assertEqual([], lifecycle.stops)
        self.assertEqual([], adapter.close_calls)

    def test_terminal_closed_registration_retries_unavailable_removal_and_completes(self) -> None:
        adapter = _FakeGitAdapter(GitEventAdapterDecisionKind.READBACK_FAILED)
        lifecycle = _RecordingLifecycle(
            stop_results=(RunnerStopCapabilityUnavailable(), RunnerStopped())
        )
        runtime, _ = _runtime(adapter, lifecycle)
        registered = runtime.register(_request())
        state = cast(ProjectSubscriptionState, registered.state)

        blocked = runtime.observe(
            state,
            GitRefSignal(event_source_ref="event-source-pd06", subscription_id="subscription-pd06"),
        )
        blocked_state = cast(ProjectSubscriptionState, blocked.state)
        closed = runtime.close(blocked_state)

        self.assertEqual(ProjectSubscriptionDecision.CLOSE_BLOCKED, blocked.decision)
        self.assertEqual(ProjectSubscriptionDecision.CLOSED, closed.decision)
        self.assertEqual(2, len(lifecycle.stops))
        self.assertEqual(["subscription-pd06"], adapter.close_calls)

    def test_replay_stale_and_malformed_adapter_outcomes_never_become_candidates(self) -> None:
        cases = (
            (GitEventAdapterDecisionKind.SILENT, False),
            (GitEventAdapterDecisionKind.STALE_BINDING_FAULT, False),
            (GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED, True),
        )
        for outcome, malformed in cases:
            with self.subTest(outcome=outcome, malformed=malformed):
                adapter = _FakeGitAdapter(outcome, malformed=malformed)
                runtime, _ = _runtime(adapter)
                registered = runtime.register(_request())
                state = cast(ProjectSubscriptionState, registered.state)

                observed = runtime.observe(
                    state,
                    GitRefSignal(
                        event_source_ref="event-source-pd06",
                        subscription_id="subscription-pd06",
                    ),
                )

                self.assertNotEqual(
                    ProjectSubscriptionDecision.COMPLETION_CANDIDATE,
                    observed.decision,
                )

    def test_unavailable_runner_stop_blocks_close_and_keeps_git_registration_active(self) -> None:
        adapter = _FakeGitAdapter()
        lifecycle = _RecordingLifecycle(stop_result=RunnerStopCapabilityUnavailable())
        runtime, _ = _runtime(adapter, lifecycle)
        registered = runtime.register(_request())
        state = cast(ProjectSubscriptionState, registered.state)

        blocked = runtime.close(state)

        self.assertEqual(ProjectSubscriptionDecision.CLOSE_BLOCKED, blocked.decision)
        self.assertEqual(ProjectSubscriptionFailure.RUNNER_CLOSE_REJECTED, blocked.failure)
        self.assertEqual([], adapter.close_calls)
        self.assertEqual(state, blocked.state)

    def test_runtime_has_no_host_or_process_effect_imports(self) -> None:
        runtime_path = Path(__file__).parents[1] / "library" / "local_orchestration" / "project_subscription_runtime.py"
        tree = ast.parse(runtime_path.read_text(encoding="utf-8"))
        forbidden = {"threading", "time", "watchdog", "subprocess", "pathlib", "socket", "requests", "httpx"}
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        self.assertTrue(forbidden.isdisjoint(imported))
