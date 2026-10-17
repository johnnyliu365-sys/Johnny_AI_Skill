"""Pure Shared Context lifecycle decisions."""

from __future__ import annotations

from .contracts import (
    AuthorityState,
    ProcessStage,
    SharedContextAccessDecision,
    SharedContextAccessRequest,
    SharedContextActorRole,
    SharedContextLifecycle,
    SharedContextMutationDecision,
    SharedContextOperation,
    SharedContextState,
)
from .profile import ProjectWorkflowProfile


class SharedContextAccessService:
    """Evaluate one profile-bound Shared Context lifecycle transition."""

    def decide_access(
        self,
        *,
        request: SharedContextAccessRequest,
        state: SharedContextState,
        profile: ProjectWorkflowProfile,
    ) -> SharedContextAccessDecision:
        """Return a deterministic decision without reading or writing external state."""

        if not (
            request.context_ref == profile.shared_context_ref
            and state.context_ref == profile.shared_context_ref
            and request.context_ref == state.context_ref
        ):
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.STALE_REVISION,
                resulting_state=state,
            )

        expected_revision = request.expected_current_revision
        if expected_revision is not None and expected_revision != state.revision:
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.STALE_REVISION,
                resulting_state=state,
            )

        if request.operation is not SharedContextOperation.READ_REFERENCE and (
            request.actor_role is not SharedContextActorRole.ARCHITECTURE_OWNER
            or request.actor_capability_ref != profile.architecture_owner_capability_ref
        ):
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                resulting_state=state,
            )

        if request.operation is SharedContextOperation.READ_REFERENCE:
            readable_stages = (
                ProcessStage.SPEC,
                ProcessStage.TICKETS,
                ProcessStage.IMPLEMENT,
                ProcessStage.SMOKE_TEST,
                ProcessStage.REVIEW,
                ProcessStage.HANDOFF,
            )
            if (
                state.lifecycle is SharedContextLifecycle.SEALED
                and request.process_stage in readable_stages
            ):
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.ALLOW,
                    resulting_state=state,
                )
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                resulting_state=state,
            )

        if request.operation is SharedContextOperation.CREATE_DRAFT:
            candidate = request.candidate_manifest
            if (
                state.lifecycle is not SharedContextLifecycle.ABSENT
                or request.process_stage not in (ProcessStage.ARCHITECTURE, ProcessStage.GRILL)
                or candidate is None
            ):
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                    resulting_state=state,
                )
            resulting_state = SharedContextState(
                context_ref=request.context_ref,
                lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
                revision=candidate.revision,
                content_digest=candidate.content_digest,
            )
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.ALLOW,
                resulting_state=resulting_state,
            )

        if request.operation is SharedContextOperation.REVISE_DRAFT:
            candidate = request.candidate_manifest
            if (
                request.process_stage not in (ProcessStage.ARCHITECTURE, ProcessStage.GRILL)
                or candidate is None
            ):
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                    resulting_state=state,
                )
            if state.revision is None or candidate.revision == state.revision:
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.STALE_REVISION,
                    resulting_state=state,
                )
            if state.lifecycle is SharedContextLifecycle.ARCHITECTURE_DRAFT:
                decision = SharedContextMutationDecision.ALLOW
            elif state.lifecycle is SharedContextLifecycle.SEALED:
                if (
                    request.change_authority_state is not AuthorityState.APPROVED
                    or request.approved_change_ref is None
                ):
                    return _shared_context_decision(
                        request=request,
                        decision=SharedContextMutationDecision.REQUIRE_CHANGE_CONTROL,
                        resulting_state=state,
                    )
                decision = SharedContextMutationDecision.ALLOW
            else:
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                    resulting_state=state,
                )
            resulting_state = SharedContextState(
                context_ref=request.context_ref,
                lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
                revision=candidate.revision,
                content_digest=candidate.content_digest,
            )
            return _shared_context_decision(
                request=request,
                decision=decision,
                resulting_state=resulting_state,
            )

        if request.operation is SharedContextOperation.SEAL:
            if (
                state.lifecycle is not SharedContextLifecycle.ARCHITECTURE_DRAFT
                or request.process_stage is not ProcessStage.CONTEXT
                or state.revision is None
                or state.content_digest is None
            ):
                return _shared_context_decision(
                    request=request,
                    decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
                    resulting_state=state,
                )
            resulting_state = SharedContextState(
                context_ref=request.context_ref,
                lifecycle=SharedContextLifecycle.SEALED,
                revision=state.revision,
                content_digest=state.content_digest,
            )
            return _shared_context_decision(
                request=request,
                decision=SharedContextMutationDecision.ALLOW,
                resulting_state=resulting_state,
            )

        return _shared_context_decision(
            request=request,
            decision=SharedContextMutationDecision.FORBID_ROLE_OR_STAGE,
            resulting_state=state,
        )


def _shared_context_decision(
    *,
    request: SharedContextAccessRequest,
    decision: SharedContextMutationDecision,
    resulting_state: SharedContextState,
) -> SharedContextAccessDecision:
    """Build the immutable metadata-only Shared Context decision."""

    return SharedContextAccessDecision(
        request_ref=request.request_ref,
        context_ref=request.context_ref,
        operation=request.operation,
        decision=decision,
        resulting_state=resulting_state,
    )
