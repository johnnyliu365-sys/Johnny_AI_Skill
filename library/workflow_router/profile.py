"""Validated project profiles and the default router-framework POC profile."""

from __future__ import annotations

from pydantic import model_validator

from .contracts import (
    ArtifactKind,
    AuthorityState,
    CapabilityRef,
    DeliveryStage,
    NonBlankText,
    ProcessStage,
    RouterEventKind,
    RouterModel,
    RouterOutcome,
)


class TransitionRule(RouterModel):
    """One closed, profile-owned transition rule."""

    current_stage: ProcessStage
    event_kind: RouterEventKind
    outcome: RouterOutcome
    next_stage: ProcessStage | None
    required_authority: AuthorityState | None = None
    required_source_kinds: tuple[ArtifactKind, ...] = ()
    eligible_capabilities: tuple[CapabilityRef, ...] = ()


class ProjectWorkflowProfile(RouterModel):
    """Project-specific policy injected into the reusable routing engine."""

    profile_id: NonBlankText
    profile_version: NonBlankText
    delivery_stage: DeliveryStage
    transition_rules: tuple[TransitionRule, ...]

    @model_validator(mode="after")
    def has_unique_transition_keys(self) -> ProjectWorkflowProfile:
        """Reject ambiguous state/event rules before a graph is compiled."""

        keys = tuple((rule.current_stage, rule.event_kind) for rule in self.transition_rules)
        if len(keys) != len(set(keys)):
            raise ValueError("each current_stage and event_kind pair must have one rule")
        return self

    def rule_for(
        self,
        *,
        current_stage: ProcessStage,
        event_kind: RouterEventKind,
    ) -> TransitionRule | None:
        """Find the one declared rule for this state/event pair."""

        for rule in self.transition_rules:
            if rule.current_stage is current_stage and rule.event_kind is event_kind:
                return rule
        return None


def build_router_poc_profile() -> ProjectWorkflowProfile:
    """Build the closed profile used by the framework's own POC."""

    wayfinder = CapabilityRef(
        capability_id="cap-wayfinder",
        version="1",
        agent_profile="wayfinder",
    )
    architecture = CapabilityRef(
        capability_id="cap-architecture",
        version="1",
        agent_profile="architecture",
    )
    grill = CapabilityRef(
        capability_id="cap-grill",
        version="1",
        agent_profile="grill",
    )
    return ProjectWorkflowProfile(
        profile_id="router-framework-poc",
        profile_version="1",
        delivery_stage=DeliveryStage.POC,
        transition_rules=(
            TransitionRule(
                current_stage=ProcessStage.INTAKE,
                event_kind=RouterEventKind.INTAKE,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.WAYFINDER,
                required_source_kinds=(ArtifactKind.PROJECT_GOAL,),
                eligible_capabilities=(wayfinder,),
            ),
            TransitionRule(
                current_stage=ProcessStage.WAYFINDER,
                event_kind=RouterEventKind.WAYFINDER_GO,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.ARCHITECTURE,
                required_authority=AuthorityState.APPROVED,
                required_source_kinds=(ArtifactKind.WAYFINDER_OUTPUT,),
                eligible_capabilities=(architecture,),
            ),
            TransitionRule(
                current_stage=ProcessStage.WAYFINDER,
                event_kind=RouterEventKind.WAYFINDER_NO_GO,
                outcome=RouterOutcome.STOP,
                next_stage=ProcessStage.STOPPED,
                required_source_kinds=(ArtifactKind.WAYFINDER_OUTPUT,),
            ),
            TransitionRule(
                current_stage=ProcessStage.ARCHITECTURE,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.GRILL,
                required_source_kinds=(ArtifactKind.ARCHITECTURE,),
                eligible_capabilities=(grill,),
            ),
        ),
    )
