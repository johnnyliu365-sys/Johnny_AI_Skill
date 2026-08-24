"""Pure pre-push authority lifecycle reducer."""

from __future__ import annotations

from library.local_orchestration.project_authority.contracts import (
    AuthorityIntegrationState,
    PrePushLifecycleRequest,
    PrePushLifecycleTransition,
    _LifecycleFailure,
)

__all__ = ("PrePushLifecycleRequest", "PrePushLifecycleTransition", "advance_pre_push_lifecycle")


def advance_pre_push_lifecycle(
    request: PrePushLifecycleRequest,
) -> PrePushLifecycleTransition:
    """Apply only the local pre-push transitions admitted by Ticket 01."""

    if (
        request.current_state is AuthorityIntegrationState.CANDIDATE
        and request.requested_state is AuthorityIntegrationState.REVIEW_ACCEPTED
    ):
        return PrePushLifecycleTransition(state=AuthorityIntegrationState.REVIEW_ACCEPTED)
    if (
        request.current_state is AuthorityIntegrationState.REVIEW_ACCEPTED
        and request.requested_state is AuthorityIntegrationState.LOCAL_INTEGRATED
    ):
        return PrePushLifecycleTransition(state=AuthorityIntegrationState.LOCAL_INTEGRATED)
    if (
        request.current_state is AuthorityIntegrationState.LOCAL_INTEGRATED
        and request.requested_state is AuthorityIntegrationState.AUTHORITY_INTEGRATED
    ):
        return PrePushLifecycleTransition(
            state=AuthorityIntegrationState.LOCAL_INTEGRATED,
            failure=_LifecycleFailure.PUSH_UNCONFIRMED,
        )
    return PrePushLifecycleTransition(
        state=request.current_state,
        failure=_LifecycleFailure.TRANSITION_NOT_ALLOWED,
    )
