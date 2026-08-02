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
    ConsumerFingerprint,
    ContextPacket,
    ContextReference,
    ContextView,
    NonBlankText,
    ReferenceStatus,
    ResolvedContext,
    RouterBlocker,
    RouterDecision,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    SourceSnippet,
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
        required_sources, missing = self._resolve_required_sources(
            artifacts=state.artifact_refs,
            required_kinds=rule.required_source_kinds,
        )
        if missing:
            missing_names = ", ".join(kind.value for kind in missing)
            return self._suspend(
                code=BlockerCode.MISSING_REQUIRED_SOURCE,
                detail=f"missing required source kinds: {missing_names}",
            )
        return RouterDecision(
            outcome=rule.outcome,
            next_stage=rule.next_stage,
            required_sources=required_sources,
            eligible_capabilities=rule.eligible_capabilities,
        )

    @staticmethod
    def _resolve_required_sources(
        *,
        artifacts: tuple[ArtifactRef, ...],
        required_kinds: tuple[ArtifactKind, ...],
    ) -> tuple[tuple[ArtifactRef, ...], tuple[ArtifactKind, ...]]:
        """Select only sources declared by the matching profile rule."""

        selected: list[ArtifactRef] = []
        missing: list[ArtifactKind] = []
        for required_kind in required_kinds:
            matching = tuple(artifact for artifact in artifacts if artifact.kind is required_kind)
            if not matching:
                missing.append(required_kind)
            else:
                selected.extend(matching)
        return (tuple(selected), tuple(missing))

    @staticmethod
    def _suspend(*, code: BlockerCode, detail: str) -> RouterDecision:
        """Build a fail-closed decision without inventing a next stage."""

        return RouterDecision(
            outcome=RouterOutcome.SUSPEND,
            next_stage=None,
            required_sources=(),
            eligible_capabilities=(),
            blockers=(RouterBlocker(code=code, detail=detail),),
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
    ) -> ResolvedContext:
        """Resolve minimum sources into a non-persistent packet plus metadata descriptor."""

        snippets = tuple(self._source_gateway.read(source) for source in required_sources)
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
            token_budget=1_000,
            invalidation_events=(
                RouterEventKind.REQUIREMENT_CHANGED,
                RouterEventKind.APPROVAL_DENIED,
                RouterEventKind.VALIDATION_FAILED,
            ),
        )
        return ResolvedContext(view=view, packet=ContextPacket(snippets=snippets))

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
