"""Validated project profiles and the default router-framework POC profile."""

from __future__ import annotations

from pydantic import model_validator

from .contracts import (
    ArtifactKind,
    AuthorityState,
    CapabilityRef,
    CompletionActionKind,
    DeliveryStage,
    HumanWaitReason,
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
    requires_human_approval: bool = False
    wait_reason: HumanWaitReason | None = None
    accepted_completion_actions: tuple[CompletionActionKind, ...] = ()
    requires_implementation_handoff: bool = False

    @model_validator(mode="after")
    def human_gate_is_a_declared_wait(self) -> TransitionRule:
        """Keep human waits explicit rather than treating every suspend as an approval wait."""

        if self.requires_human_approval and self.outcome is not RouterOutcome.SUSPEND:
            raise ValueError("human approval gates must suspend")
        if self.requires_human_approval and self.wait_reason is None:
            raise ValueError("human approval gates require a precise wait reason")
        if not self.requires_human_approval and self.wait_reason is not None:
            raise ValueError("only human approval gates may declare a wait reason")
        if self.outcome in (RouterOutcome.ADVANCE, RouterOutcome.RETRY) and self.next_stage is None:
            raise ValueError("advancing and retry rules require next_stage")
        if self.outcome is RouterOutcome.SUSPEND and self.next_stage is not None:
            raise ValueError("suspending rules must not declare a next stage")
        if self.outcome is RouterOutcome.STOP and self.next_stage is not ProcessStage.STOPPED:
            raise ValueError("stop rules must target stopped")
        if self.event_kind is not RouterEventKind.ACTION_COMPLETED and self.accepted_completion_actions:
            raise ValueError("only action_completed rules may accept completion actions")
        if self.requires_implementation_handoff and (
            self.current_stage is not ProcessStage.TICKETS
            or self.event_kind is not RouterEventKind.APPROVAL_GRANTED
            or self.outcome is not RouterOutcome.ADVANCE
            or self.next_stage is not ProcessStage.IMPLEMENT
        ):
            raise ValueError(
                "implementation handoff is valid only for ticket approval advancing to implement"
            )
        return self


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
    context = CapabilityRef(
        capability_id="cap-context",
        version="1",
        agent_profile="context",
    )
    specification = CapabilityRef(
        capability_id="cap-specification",
        version="1",
        agent_profile="specification",
    )
    tickets = CapabilityRef(
        capability_id="cap-tickets",
        version="1",
        agent_profile="tickets",
    )
    implementation = CapabilityRef(
        capability_id="cap-implementation",
        version="1",
        agent_profile="implementation",
    )
    smoke_test = CapabilityRef(
        capability_id="cap-smoke-test",
        version="1",
        agent_profile="smoke-test",
    )
    review = CapabilityRef(
        capability_id="cap-review",
        version="1",
        agent_profile="review",
    )
    handoff = CapabilityRef(
        capability_id="cap-handoff",
        version="1",
        agent_profile="handoff",
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
                accepted_completion_actions=(CompletionActionKind.DOCUMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.GRILL,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.CONTEXT,
                required_source_kinds=(ArtifactKind.GRILL,),
                eligible_capabilities=(context,),
                accepted_completion_actions=(CompletionActionKind.DOCUMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.CONTEXT,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.SPEC,
                required_source_kinds=(ArtifactKind.CONTEXT,),
                eligible_capabilities=(specification,),
                accepted_completion_actions=(CompletionActionKind.DOCUMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.SPEC,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.SUSPEND,
                next_stage=None,
                required_source_kinds=(ArtifactKind.SPEC,),
                requires_human_approval=True,
                wait_reason=HumanWaitReason.SPECIFICATION_APPROVAL_REQUIRED,
                accepted_completion_actions=(CompletionActionKind.DOCUMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.SPEC,
                event_kind=RouterEventKind.APPROVAL_GRANTED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.TICKETS,
                required_authority=AuthorityState.APPROVED,
                required_source_kinds=(ArtifactKind.SPEC,),
                eligible_capabilities=(tickets,),
            ),
            TransitionRule(
                current_stage=ProcessStage.TICKETS,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.SUSPEND,
                next_stage=None,
                required_source_kinds=(ArtifactKind.TICKET,),
                requires_human_approval=True,
                wait_reason=HumanWaitReason.TICKET_APPROVAL_REQUIRED,
                accepted_completion_actions=(CompletionActionKind.DOCUMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.TICKETS,
                event_kind=RouterEventKind.APPROVAL_GRANTED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.IMPLEMENT,
                required_authority=AuthorityState.APPROVED,
                required_source_kinds=(ArtifactKind.TICKET,),
                eligible_capabilities=(implementation,),
                requires_implementation_handoff=True,
            ),
            TransitionRule(
                current_stage=ProcessStage.IMPLEMENT,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.SMOKE_TEST,
                required_source_kinds=(ArtifactKind.TICKET,),
                eligible_capabilities=(smoke_test,),
                accepted_completion_actions=(CompletionActionKind.IMPLEMENTATION,),
            ),
            TransitionRule(
                current_stage=ProcessStage.SMOKE_TEST,
                event_kind=RouterEventKind.VALIDATION_PASSED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.REVIEW,
                required_source_kinds=(ArtifactKind.TICKET,),
                eligible_capabilities=(review,),
            ),
            TransitionRule(
                current_stage=ProcessStage.SMOKE_TEST,
                event_kind=RouterEventKind.VALIDATION_FAILED,
                outcome=RouterOutcome.RETRY,
                next_stage=ProcessStage.IMPLEMENT,
                required_source_kinds=(ArtifactKind.TICKET,),
                eligible_capabilities=(implementation,),
            ),
            TransitionRule(
                current_stage=ProcessStage.REVIEW,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.HANDOFF,
                required_source_kinds=(ArtifactKind.TICKET,),
                eligible_capabilities=(handoff,),
                accepted_completion_actions=(CompletionActionKind.REVIEW,),
            ),
            TransitionRule(
                current_stage=ProcessStage.HANDOFF,
                event_kind=RouterEventKind.ACTION_COMPLETED,
                outcome=RouterOutcome.STOP,
                next_stage=ProcessStage.STOPPED,
                required_source_kinds=(ArtifactKind.TICKET,),
                accepted_completion_actions=(CompletionActionKind.HANDOFF,),
            ),
            TransitionRule(
                current_stage=ProcessStage.IMPLEMENT,
                event_kind=RouterEventKind.REQUIREMENT_CHANGED,
                outcome=RouterOutcome.ADVANCE,
                next_stage=ProcessStage.GRILL,
                required_source_kinds=(ArtifactKind.CHANGE,),
                eligible_capabilities=(grill,),
            ),
        ),
    )
