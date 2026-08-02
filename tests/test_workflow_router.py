"""Acceptance tests for the reusable, profile-driven workflow router."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from library.workflow_router import (
    ArtifactKind,
    ArtifactRef,
    AgentUsage,
    AuthorityState,
    CitationLedger,
    ConsumerFingerprint,
    ContextResolver,
    ContextUsageRecord,
    ContextUsageValidator,
    DeliveryStage,
    InMemorySourceGateway,
    JsonlContextUsageStore,
    ProcessStage,
    ReferenceStatus,
    RouterEngine,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    RunAcceptance,
    SourceSnippet,
    build_router_graph,
    build_router_poc_profile,
)
from library.workflow_router.graph import RouterGraphState
from library.workflow_router.telemetry_cli import main as telemetry_main


class WorkflowRouterTests(unittest.TestCase):
    """Keep the POC closed, strongly typed, and free of shared raw context."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.engine = RouterEngine()
        self.goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-framework-goal",
            uri="project://router-framework/goal",
            revision="1",
        )
        self.wayfinder_output = ArtifactRef(
            kind=ArtifactKind.WAYFINDER_OUTPUT,
            identifier="wayfinder-router-poc",
            uri="context://router-framework/wayfinder",
            revision="1",
        )

    def test_intake_and_go_have_only_the_profile_declared_next_stage(self) -> None:
        intake_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.INTAKE,
            authority_state=AuthorityState.NOT_REQUIRED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.goal,),
        )
        intake = self.engine.decide(
            state=intake_state,
            event=RouterEvent(event_id="evt-intake-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, intake.outcome)
        self.assertEqual(ProcessStage.WAYFINDER, intake.next_stage)

        go_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.WAYFINDER,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.wayfinder_output,),
        )
        go = self.engine.decide(
            state=go_state,
            event=RouterEvent(event_id="evt-go-001", kind=RouterEventKind.WAYFINDER_GO),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.ADVANCE, go.outcome)
        self.assertEqual(ProcessStage.ARCHITECTURE, go.next_stage)

    def test_missing_approval_and_no_go_fail_closed(self) -> None:
        pending_state = RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.WAYFINDER,
            authority_state=AuthorityState.PENDING,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.wayfinder_output,),
        )
        suspended = self.engine.decide(
            state=pending_state,
            event=RouterEvent(event_id="evt-go-pending", kind=RouterEventKind.WAYFINDER_GO),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, suspended.outcome)
        self.assertIsNone(suspended.next_stage)

        no_go = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.WAYFINDER,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(self.wayfinder_output,),
            ),
            event=RouterEvent(event_id="evt-no-go-001", kind=RouterEventKind.WAYFINDER_NO_GO),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.STOP, no_go.outcome)
        self.assertEqual(ProcessStage.STOPPED, no_go.next_stage)

    def test_delivery_stage_must_match_the_approved_profile(self) -> None:
        decision = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.MVP,
                artifact_refs=(self.goal,),
            ),
            event=RouterEvent(event_id="evt-maturity-mismatch-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        self.assertEqual(RouterOutcome.SUSPEND, decision.outcome)
        self.assertEqual("delivery_stage_mismatch", decision.blockers[0].code.value)

    def test_each_new_reference_has_a_new_id_but_retry_is_idempotent(self) -> None:
        source = ArtifactRef(
            kind=ArtifactKind.CONTEXT,
            identifier="router-cost-assumption",
            uri="context://router-framework/poc-cost",
            revision="4",
        )
        target = ArtifactRef(
            kind=ArtifactKind.GRILL,
            identifier="GRILL-ROUTER-POC-001",
            uri="grill://router-framework/poc-001",
            revision="1",
        )
        gateway = InMemorySourceGateway(
            snippets=(
                SourceSnippet(source=source, span="poc.cost", text="no paid provider"),
            )
        )
        resolver = ContextResolver(source_gateway=gateway)
        consumer = ConsumerFingerprint(
            agent_profile="architecture",
            profile_version="1",
            worktree_id="worktree-a",
            execution_id="run-001",
        )

        first = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        retry = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        next_reference = resolver.resolve(
            event_id="evt-reference-002",
            required_sources=(source,),
            target_artifact=target,
            consumer=consumer,
        )
        other_consumer = resolver.resolve(
            event_id="evt-reference-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=ConsumerFingerprint(
                agent_profile="spec",
                profile_version="1",
                worktree_id="worktree-b",
                execution_id="run-003",
            ),
        )
        self.assertEqual(first.view.references[0].side_context_id, retry.view.references[0].side_context_id)
        self.assertNotEqual(first.view.references[0].side_context_id, next_reference.view.references[0].side_context_id)
        self.assertNotEqual(first.view.references[0].side_context_id, other_consumer.view.references[0].side_context_id)
        self.assertEqual("no paid provider", first.packet.snippets[0].text)
        self.assertNotIn("no paid provider", first.view.model_dump_json())

    def test_closed_reference_maps_without_raw_text_and_invalidates_by_revision(self) -> None:
        source = ArtifactRef(
            kind=ArtifactKind.CONTEXT,
            identifier="router-cost-assumption",
            uri="context://router-framework/poc-cost",
            revision="4",
        )
        target = ArtifactRef(
            kind=ArtifactKind.SPEC,
            identifier="SPEC-ROUTER-POC-001",
            uri="spec://router-framework/poc-001",
            revision="1",
        )
        resolved = ContextResolver(
            source_gateway=InMemorySourceGateway(
                snippets=(SourceSnippet(source=source, span="poc.cost", text="private evidence"),)
            )
        ).resolve(
            event_id="evt-close-001",
            required_sources=(source,),
            target_artifact=target,
            consumer=ConsumerFingerprint(
                agent_profile="spec",
                profile_version="1",
                worktree_id="worktree-b",
                execution_id="run-002",
            ),
        )
        ledger = CitationLedger()
        closed = ledger.close(reference=resolved.view.references[0])
        self.assertEqual(ReferenceStatus.CLOSED, closed.status)
        mapped = ledger.references_for_source(source=source)
        self.assertEqual(target, mapped[0].target_artifact)
        self.assertNotIn("private evidence", ledger.model_dump_json())

        invalidated = ledger.invalidate_source(
            source=ArtifactRef(
                kind=source.kind,
                identifier=source.identifier,
                uri=source.uri,
                revision="5",
            )
        )
        self.assertEqual(ReferenceStatus.INVALIDATED, invalidated[0].status)

    def test_langgraph_routes_advance_to_complete_and_suspend_to_blocked(self) -> None:
        graph = build_router_graph(engine=self.engine)
        completed = RouterGraphState.model_validate(
            graph.invoke(
                RouterGraphState(
                    router_state=RouterState(
                        project_id="router-framework-poc",
                        stage=ProcessStage.INTAKE,
                        authority_state=AuthorityState.NOT_REQUIRED,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(self.goal,),
                    ),
                    router_event=RouterEvent(event_id="evt-graph-001", kind=RouterEventKind.INTAKE),
                    profile=self.profile,
                )
            )
        )
        assert completed.decision is not None
        self.assertEqual(RouterOutcome.ADVANCE, completed.decision.outcome)
        self.assertEqual("complete", completed.graph_terminal)

        blocked = RouterGraphState.model_validate(
            graph.invoke(
                RouterGraphState(
                    router_state=RouterState(
                        project_id="router-framework-poc",
                        stage=ProcessStage.WAYFINDER,
                        authority_state=AuthorityState.PENDING,
                        delivery_stage=DeliveryStage.POC,
                        artifact_refs=(self.wayfinder_output,),
                    ),
                    router_event=RouterEvent(
                        event_id="evt-graph-002",
                        kind=RouterEventKind.WAYFINDER_GO,
                    ),
                    profile=self.profile,
                )
            )
        )
        assert blocked.decision is not None
        self.assertEqual(RouterOutcome.SUSPEND, blocked.decision.outcome)
        self.assertEqual("blocked", blocked.graph_terminal)

    def test_agents_mcp_and_temporal_adapters_load_without_external_services(self) -> None:
        from library.workflow_router.integrations import (
            AgentCapabilityDefinition,
            McpResourceGateway,
            OpenAICapabilityAdapter,
        )
        from library.workflow_router.temporal_runtime import RouterRoundInput, route_round

        intake = self.engine.decide(
            state=RouterState(
                project_id="router-framework-poc",
                stage=ProcessStage.INTAKE,
                authority_state=AuthorityState.NOT_REQUIRED,
                delivery_stage=DeliveryStage.POC,
                artifact_refs=(self.goal,),
            ),
            event=RouterEvent(event_id="evt-adapter-001", kind=RouterEventKind.INTAKE),
            profile=self.profile,
        )
        capability = intake.eligible_capabilities[0]
        agent = OpenAICapabilityAdapter(
            definitions=(
                AgentCapabilityDefinition(
                    capability=capability,
                    agent_name="wayfinder-agent",
                    instructions="Use only the supplied ContextView descriptor.",
                ),
            )
        ).resolve(capability=capability)
        self.assertEqual("wayfinder-agent", agent.name)
        self.assertEqual((), tuple(agent.handoffs))
        self.assertEqual("McpResourceGateway", McpResourceGateway.__name__)

        activity_decision = route_round(
            RouterRoundInput(
                router_state=RouterState(
                    project_id="router-framework-poc",
                    stage=ProcessStage.INTAKE,
                    authority_state=AuthorityState.NOT_REQUIRED,
                    delivery_stage=DeliveryStage.POC,
                    artifact_refs=(self.goal,),
                ),
                router_event=RouterEvent(
                    event_id="evt-temporal-activity-001",
                    kind=RouterEventKind.INTAKE,
                ),
                profile=self.profile,
            )
        )
        self.assertEqual(RouterOutcome.ADVANCE, activity_decision.outcome)


class ContextLoadTelemetryTests(unittest.TestCase):
    """Verify metadata-only evidence and fail-closed context-load comparisons."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="telemetry-goal",
            uri="project://telemetry/private-goal",
            revision="1",
        )
        self.target = ArtifactRef(
            kind=ArtifactKind.WAYFINDER_OUTPUT,
            identifier="WAYFINDER-TELEMETRY-001",
            uri="context://telemetry/wayfinder",
            revision="1",
        )
        self.state = RouterState(
            project_id="telemetry-poc",
            stage=ProcessStage.INTAKE,
            authority_state=AuthorityState.NOT_REQUIRED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(self.goal,),
        )
        self.event = RouterEvent(event_id="evt-telemetry-001", kind=RouterEventKind.INTAKE)
        self.decision = RouterEngine().decide(
            state=self.state,
            event=self.event,
            profile=self.profile,
        )
        self.raw_text = "never-persist-this-unique-raw-context"
        self.snippet = SourceSnippet(source=self.goal, span="goal.summary", text=self.raw_text)
        self.resolved = ContextResolver(
            source_gateway=InMemorySourceGateway(snippets=(self.snippet,))
        ).resolve(
            event_id=self.event.event_id,
            required_sources=self.decision.required_sources,
            target_artifact=self.target,
            consumer=ConsumerFingerprint(
                agent_profile="wayfinder",
                profile_version="1",
                worktree_id="telemetry-worktree",
                execution_id="telemetry-run",
            ),
        )
        self.agent = AgentUsage(
            provider="test-provider",
            model="test-model",
            consumer=ConsumerFingerprint(
                agent_profile="wayfinder",
                profile_version="1",
                worktree_id="telemetry-worktree",
                execution_id="telemetry-run",
            ),
            provider_input_tokens=2_000,
            provider_output_tokens=250,
            tool_read_count=1,
            retry_count=0,
            duration_ms=20,
        )

    def test_router_record_round_trips_without_raw_text_or_uri(self) -> None:
        record = ContextUsageRecord.from_router(
            run_id="router-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        with TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "router-usage.jsonl"
            JsonlContextUsageStore.append(path=log_path, record=record)
            serialized = log_path.read_text(encoding="utf-8")
            restored = JsonlContextUsageStore.read(path=log_path)
        self.assertNotIn(self.raw_text, serialized)
        self.assertNotIn(self.goal.uri, serialized)
        self.assertEqual((record,), restored)
        self.assertFalse(record.context.raw_text_in_shared_state)
        self.assertEqual(1, record.context.actual_source_count)

    def test_matched_baseline_and_router_prove_provider_token_reduction(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-001",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        report = ContextUsageValidator().validate(records=(baseline, router))
        self.assertTrue(report.evidence_valid)
        self.assertTrue(report.reduction_verified)
        self.assertEqual(5_000, report.median_reduction_basis_points)

    def test_guard_or_usage_failure_rejects_reduction_claim(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-002",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-002",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent.model_copy(update={"provider_input_tokens": None}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        report = ContextUsageValidator().validate(records=(baseline, router))
        self.assertFalse(report.evidence_valid)
        self.assertFalse(report.reduction_verified)

    def test_router_guard_violation_rejects_reduction_claim(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-003",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-003",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        invalid_context = router.context.model_copy(
            update={"undeclared_source_count": router.context.actual_source_count}
        )
        invalid_router = router.model_copy(update={"context": invalid_context})
        report = ContextUsageValidator().validate(records=(baseline, invalid_router))
        self.assertFalse(report.evidence_valid)
        self.assertFalse(report.reduction_verified)
        self.assertEqual("undeclared_source", report.issues[0].code.value)

    def test_budget_breach_rejects_reduction_claim(self) -> None:
        oversized_snippet = SourceSnippet(
            source=self.goal,
            span="goal.oversized",
            text="x" * 4_004,
        )
        oversized_resolved = ContextResolver(
            source_gateway=InMemorySourceGateway(snippets=(oversized_snippet,))
        ).resolve(
            event_id=self.event.event_id,
            required_sources=self.decision.required_sources,
            target_artifact=self.target,
            consumer=self.agent.consumer,
        )
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-004",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(oversized_snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-004",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=oversized_resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        report = ContextUsageValidator().validate(records=(baseline, router))
        self.assertTrue(router.context.budget_exceeded)
        self.assertFalse(report.evidence_valid)
        self.assertEqual("context_budget_exceeded", report.issues[0].code.value)

    def test_cli_accepts_only_a_verified_local_jsonl(self) -> None:
        baseline = ContextUsageRecord.from_baseline(
            run_id="baseline-run-005",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            stage=ProcessStage.INTAKE,
            delivery_stage=DeliveryStage.POC,
            source_snippets=(self.snippet,),
            agent=self.agent.model_copy(update={"provider_input_tokens": 4_000}),
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        router = ContextUsageRecord.from_router(
            run_id="router-run-005",
            comparison_group_id="wayfinder-poc",
            attempt=1,
            project_snapshot_id="snapshot-001",
            state=self.state,
            event=self.event,
            profile=self.profile,
            decision=self.decision,
            resolved_context=self.resolved,
            agent=self.agent,
            acceptance=RunAcceptance.PASSED,
            human_correction_required=False,
        )
        with TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "router-usage.jsonl"
            JsonlContextUsageStore.append(path=log_path, record=baseline)
            JsonlContextUsageStore.append(path=log_path, record=router)
            output = StringIO()
            with redirect_stdout(output):
                result = telemetry_main((str(log_path), "--minimum-reduction-bps", "5000"))
        self.assertEqual(0, result)
        self.assertIn('"reduction_verified": true', output.getvalue())

    def test_context_resolver_rejects_mismatched_source_adapter_output(self) -> None:
        other_source = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="other-goal",
            uri="project://telemetry/other-goal",
            revision="1",
        )

        class MismatchedSourceGateway:
            def read(self, source: ArtifactRef) -> SourceSnippet:
                return SourceSnippet(source=other_source, span="wrong", text="wrong source")

        with self.assertRaisesRegex(ValueError, "undeclared source"):
            ContextResolver(source_gateway=MismatchedSourceGateway()).resolve(
                event_id=self.event.event_id,
                required_sources=self.decision.required_sources,
                target_artifact=self.target,
                consumer=self.agent.consumer,
            )


if __name__ == "__main__":
    unittest.main()
