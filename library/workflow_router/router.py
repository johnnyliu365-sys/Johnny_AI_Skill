"""Pure routing, minimal Context resolution, and metadata-only citation mapping."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, ConfigDict, Field

from .contracts import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    BlockerCode,
    CollaborationDispatchPlan,
    CollaborationTopology,
    ConsumerFingerprint,
    ContinuationDirective,
    ContextPacket,
    ContextReference,
    ContextView,
    HumanWaitReason,
    ImplementationReturnStatus,
    PlanningLaneState,
    ProcessStage,
    NonBlankText,
    PositiveTokenBudget,
    ReferenceStatus,
    ResolvedContext,
    RouterBlocker,
    RouterDecision,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    SourceSnippet,
    TicketDispatchConfirmation,
    TicketDispatchReceipt,
    TicketLaneState,
    TicketDispatchState,
)
from .profile import ProjectWorkflowProfile


class SourceGateway(Protocol):
    """Read exactly one declared official source into an ephemeral raw snippet."""

    def read(self, source: ArtifactRef) -> SourceSnippet:
        """Read one explicitly allowed source reference."""


class InMemorySourceGateway:
    """Local, no-network source adapter used only by router tests and POC smoke tests."""

    def __init__(self, *, snippets: tuple[SourceSnippet, ...]) -> None:
        self._snippets = snippets

    def read(self, source: ArtifactRef) -> SourceSnippet:
        """Return the exact versioned snippet or fail closed."""

        for snippet in self._snippets:
            if snippet.source == source:
                return snippet
        raise ValueError(f"required source is unavailable: {source.uri}@{source.revision}")


class RouterEngine:
    """Pure state/event evaluator; it never reads text or executes an Agent."""

    def decide(
        self,
        *,
        state: RouterState,
        event: RouterEvent,
        profile: ProjectWorkflowProfile,
    ) -> RouterDecision:
        """Produce the sole legal next action from a validated profile rule."""

        if state.delivery_stage is not profile.delivery_stage:
            return self._suspend(
                code=BlockerCode.DELIVERY_STAGE_MISMATCH,
                detail=(
                    f"state delivery stage {state.delivery_stage.value} does not match "
                    f"profile delivery stage {profile.delivery_stage.value}"
                ),
            )
        if (
            event.implementation_return is not None
            and event.implementation_return.status is ImplementationReturnStatus.BLOCKED
        ):
            return self._suspend(
                code=BlockerCode.IMPLEMENTATION_RETURN_BLOCKED,
                detail="implementation owner returned a blocked result",
            )
        rule = profile.rule_for(current_stage=state.stage, event_kind=event.kind)
        if rule is None:
            return self._suspend(
                code=BlockerCode.NO_DECLARED_TRANSITION,
                detail=f"no transition for {state.stage.value}/{event.kind.value}",
            )
        if rule.required_authority is not None and state.authority_state is not rule.required_authority:
            return self._suspend(
                code=BlockerCode.AUTHORITY_REQUIRED,
                detail=(
                    f"{state.stage.value}/{event.kind.value} requires "
                    f"{rule.required_authority.value} authority"
                ),
            )
        if rule.requires_implementation_handoff and event.implementation_handoff is None:
            return self._suspend(
                code=BlockerCode.IMPLEMENTATION_HANDOFF_REQUIRED,
                detail="this declared ticket approval requires an implementation handoff",
            )
        if not rule.requires_implementation_handoff and event.implementation_handoff is not None:
            return self._suspend(
                code=BlockerCode.IMPLEMENTATION_HANDOFF_UNDECLARED,
                detail="implementation handoff is not declared for this profile transition",
            )
        if event.completion_evidence is not None:
            if event.completion_evidence.action_kind not in rule.accepted_completion_actions:
                return self._suspend(
                    code=BlockerCode.INVALID_COMPLETION_EVIDENCE,
                    detail=(
                        f"{state.stage.value}/{event.kind.value} does not accept "
                        f"{event.completion_evidence.action_kind.value} completion evidence"
                    ),
                )
        if rule.requires_dispatch_receipt:
            receipt = event.dispatch_receipt
            if state.topology is None:
                return self._suspend(
                    code=BlockerCode.TOPOLOGY_REQUIRED,
                    detail="confirmed dispatch requires a selected collaboration topology",
                )
            if receipt is None:
                return self._suspend(
                    code=BlockerCode.DISPATCH_RECEIPT_REQUIRED,
                    detail="confirmed dispatch requires a typed receipt",
                )
            if event.dispatch_confirmation is not TicketDispatchConfirmation.POSITIVE:
                return self._suspend(
                    code=BlockerCode.INVALID_DISPATCH_RECEIPT,
                    detail="confirmed dispatch requires positive confirmation",
                )
            if receipt.correlation_id != event.event_id:
                return self._suspend(
                    code=BlockerCode.INVALID_DISPATCH_RECEIPT,
                    detail="dispatch receipt correlation does not match the event",
                )
        required_sources, missing, ambiguous = self._resolve_required_sources(
            artifacts=state.artifact_refs,
            required_kinds=rule.required_source_kinds,
        )
        if missing:
            missing_names = ", ".join(kind.value for kind in missing)
            return self._suspend(
                code=BlockerCode.MISSING_REQUIRED_SOURCE,
                detail=f"missing required source kinds: {missing_names}",
            )
        if ambiguous:
            ambiguous_names = ", ".join(kind.value for kind in ambiguous)
            return self._suspend(
                code=BlockerCode.AMBIGUOUS_REQUIRED_SOURCE,
                detail=f"multiple declared sources match required kinds: {ambiguous_names}",
            )
        if rule.requires_human_approval:
            return self._suspend(
                code=BlockerCode.AUTHORITY_REQUIRED,
                detail="this declared workflow gate requires an explicit human approval",
                continuation=ContinuationDirective.WAIT_FOR_HUMAN,
                wait_reason=rule.wait_reason,
            )
        if rule.requires_dispatch_receipt:
            assert event.dispatch_receipt is not None
            assert state.topology is not None
            assert len(required_sources) == 1
            if event.dispatch_receipt.ticket_reference != required_sources[0].identifier:
                return self._suspend(
                    code=BlockerCode.INVALID_DISPATCH_RECEIPT,
                    detail="dispatch receipt ticket does not match the declared ticket source",
                )
            return RouterDecision(
                outcome=rule.outcome,
                continuation=ContinuationDirective.AUTO_CONTINUE,
                next_stage=rule.next_stage,
                required_sources=required_sources,
                eligible_capabilities=rule.eligible_capabilities,
                dispatch_plan=self._dispatch_plan(
                    state=state,
                    event=event,
                    receipt=event.dispatch_receipt,
                    topology=state.topology,
                    ticket=required_sources[0],
                ),
            )
        return RouterDecision(
            outcome=rule.outcome,
            continuation=(
                ContinuationDirective.AUTO_CONTINUE
                if rule.outcome in (RouterOutcome.ADVANCE, RouterOutcome.RETRY)
                else ContinuationDirective.HALT
            ),
            next_stage=rule.next_stage,
            required_sources=required_sources,
            eligible_capabilities=rule.eligible_capabilities,
        )

    @staticmethod
    def _dispatch_plan(
        *,
        state: RouterState,
        event: RouterEvent,
        receipt: TicketDispatchReceipt,
        topology: CollaborationTopology,
        ticket: ArtifactRef,
    ) -> CollaborationDispatchPlan:
        """Create two immutable lane descriptors with disjoint correlation metadata."""

        dispatch_receipt = receipt
        seed = f"{state.project_id}:{event.event_id}:{ticket.identifier}"
        planning_suffix = uuid5(NAMESPACE_URL, f"planning:{seed}").hex[:20]
        ticket_suffix = uuid5(NAMESPACE_URL, f"ticket:{seed}").hex[:20]
        planning_lane = PlanningLaneState(
            project_id=state.project_id,
            stage=ProcessStage.GRILL,
            topology=topology,
            artifact_refs=(ticket,),
            active_ticket_refs=(ticket.identifier,),
            context_view_id=f"cvw-planning-{planning_suffix}",
            side_context_id=f"scx-planning-{planning_suffix}",
            event_id=f"evt-planning-{planning_suffix}",
            safety_ceiling=10,
        )
        ticket_lane = TicketLaneState(
            ticket_id=ticket.identifier,
            dispatch_state=TicketDispatchState.CONFIRMED,
            execution_stage=ProcessStage.IMPLEMENT,
            expected_main_revision=dispatch_receipt.expected_main_revision,
            source_grants=(ArtifactKind.TICKET,),
            context_view_id=f"cvw-ticket-{ticket_suffix}",
            side_context_id=f"scx-ticket-{ticket_suffix}",
            event_id=f"evt-ticket-{ticket_suffix}",
            worktree_fingerprint=dispatch_receipt.worktree_fingerprint,
            branch_fingerprint=dispatch_receipt.branch_fingerprint,
            safety_ceiling=10,
        )
        return CollaborationDispatchPlan(
            receipt=dispatch_receipt,
            planning_lane=planning_lane,
            ticket_lane=ticket_lane,
        )

    @staticmethod
    def _resolve_required_sources(
        *,
        artifacts: tuple[ArtifactRef, ...],
        required_kinds: tuple[ArtifactKind, ...],
    ) -> tuple[tuple[ArtifactRef, ...], tuple[ArtifactKind, ...], tuple[ArtifactKind, ...]]:
        """Select one exact source per kind or fail closed rather than inflating Context."""

        selected: list[ArtifactRef] = []
        missing: list[ArtifactKind] = []
        ambiguous: list[ArtifactKind] = []
        for required_kind in required_kinds:
            matching = tuple(artifact for artifact in artifacts if artifact.kind is required_kind)
            if not matching:
                missing.append(required_kind)
            elif len(matching) > 1:
                ambiguous.append(required_kind)
            else:
                selected.append(matching[0])
        return (tuple(selected), tuple(missing), tuple(ambiguous))

    @staticmethod
    def _suspend(
        *,
        code: BlockerCode,
        detail: str,
        continuation: ContinuationDirective = ContinuationDirective.HALT,
        wait_reason: HumanWaitReason | None = None,
    ) -> RouterDecision:
        """Build a fail-closed decision without inventing a next stage."""

        return RouterDecision(
            outcome=RouterOutcome.SUSPEND,
            continuation=continuation,
            next_stage=None,
            required_sources=(),
            eligible_capabilities=(),
            blockers=(RouterBlocker(code=code, detail=detail),),
            wait_reason=wait_reason,
        )


class ContextResolver:
    """Create a descriptor and temporary packet for explicitly required sources only."""

    def __init__(self, *, source_gateway: SourceGateway) -> None:
        self._source_gateway = source_gateway

    def resolve(
        self,
        *,
        event_id: NonBlankText,
        required_sources: tuple[ArtifactRef, ...],
        target_artifact: ArtifactRef,
        consumer: ConsumerFingerprint,
        token_budget: PositiveTokenBudget = 1_000,
    ) -> ResolvedContext:
        """Resolve minimum sources into a non-persistent packet plus metadata descriptor."""

        snippets = tuple(self._read_declared_source(source=source) for source in required_sources)
        estimated_packet_tokens = sum(self._estimate_tokens(snippet.text) for snippet in snippets)
        if estimated_packet_tokens > token_budget:
            raise ValueError("declared ContextPacket exceeds its Router token budget")
        references = tuple(
            self._reference_for(
                event_id=event_id,
                snippet=snippet,
                target_artifact=target_artifact,
                consumer=consumer,
                ordinal=ordinal,
            )
            for ordinal, snippet in enumerate(snippets, start=1)
        )
        view_id = self._stable_id(prefix="CVW", parts=(event_id, target_artifact.identifier))
        view = ContextView(
            view_id=view_id,
            purpose=f"source view for {target_artifact.kind.value}:{target_artifact.identifier}",
            references=references,
            token_budget=token_budget,
            invalidation_events=(
                RouterEventKind.REQUIREMENT_CHANGED,
                RouterEventKind.APPROVAL_DENIED,
                RouterEventKind.VALIDATION_FAILED,
            ),
        )
        return ResolvedContext(view=view, packet=ContextPacket(snippets=snippets))

    def _read_declared_source(self, *, source: ArtifactRef) -> SourceSnippet:
        """Reject a source adapter that returns content for a different source reference."""

        snippet = self._source_gateway.read(source)
        if snippet.source != source:
            raise ValueError("source gateway returned an undeclared source")
        return snippet

    def _reference_for(
        self,
        *,
        event_id: NonBlankText,
        snippet: SourceSnippet,
        target_artifact: ArtifactRef,
        consumer: ConsumerFingerprint,
        ordinal: int,
    ) -> ContextReference:
        """Create one idempotent reference for this event/source/span/ordinal combination."""

        side_context_id = self._stable_id(
            prefix="SCX",
            parts=(
                event_id,
                snippet.source.kind.value,
                snippet.source.identifier,
                snippet.source.uri,
                snippet.source.revision,
                snippet.span,
                target_artifact.kind.value,
                target_artifact.identifier,
                target_artifact.uri,
                target_artifact.revision,
                consumer.agent_profile,
                consumer.profile_version,
                consumer.worktree_id,
                consumer.execution_id,
                str(ordinal),
            ),
        )
        return ContextReference(
            source_context=snippet.source,
            source_revision=snippet.source.revision,
            source_span=snippet.span,
            side_context_id=side_context_id,
            consumer_fingerprint=consumer,
            target_artifact=target_artifact,
        )

    @staticmethod
    def _estimate_tokens(text: NonBlankText) -> int:
        """Return a deterministic local ceiling check; this is not a provider usage claim."""

        return (len(text.encode("utf-8")) + 3) // 4

    @staticmethod
    def _stable_id(*, prefix: str, parts: Sequence[str]) -> str:
        """Derive retry-stable IDs while a different event always yields a new reference."""

        seed = "\x1f".join(parts)
        return f"{prefix}-{uuid5(NAMESPACE_URL, seed).hex}"


class CitationLedger(BaseModel):
    """Metadata-only projection of closed Context references; it never receives raw text."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    records: tuple[ContextReference, ...] = Field(default_factory=tuple)

    def close(self, *, reference: ContextReference) -> ContextReference:
        """Close one reference idempotently and preserve previously closed mappings."""

        for index, existing in enumerate(self.records):
            if existing.side_context_id != reference.side_context_id:
                continue
            if existing != reference and existing.status is not ReferenceStatus.OPEN:
                raise ValueError("side_context_id already belongs to a different closed reference")
            closed = existing.model_copy(update={"status": ReferenceStatus.CLOSED})
            self.records = self.records[:index] + (closed,) + self.records[index + 1 :]
            return closed
        closed = reference.model_copy(update={"status": ReferenceStatus.CLOSED})
        self.records = self.records + (closed,)
        return closed

    def references_for_source(self, *, source: ArtifactRef) -> tuple[ContextReference, ...]:
        """Return closed or invalidated mappings for one exact source revision."""

        return tuple(record for record in self.records if record.source_context == source)

    def invalidate_source(self, *, source: ArtifactRef) -> tuple[ContextReference, ...]:
        """Invalidate all mappings for the same logical source after a new revision exists."""

        updated: list[ContextReference] = []
        invalidated: list[ContextReference] = []
        for record in self.records:
            if record.source_context.logical_key == source.logical_key:
                replacement = record.model_copy(update={"status": ReferenceStatus.INVALIDATED})
                updated.append(replacement)
                invalidated.append(replacement)
            else:
                updated.append(record)
        self.records = tuple(updated)
        return tuple(invalidated)
