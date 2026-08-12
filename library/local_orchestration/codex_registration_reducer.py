"""Pure forward reduction for one exact current Codex registration attempt."""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, ValidationError

from .codex_command_attempts import (
    CodexCommandClassificationRejected,
    CodexCommandObservation,
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
    CodexPreStartFailure,
    CodexStartedFailure,
    CodexStartedFailureReason,
    classify_command_attempt,
)
from .codex_compensation_reducer import (
    CodexCompensationPlan,
    build_compensation_plan,
)
from .codex_registration_contracts import (
    CodexAttemptEffectState,
    CodexMarketplaceAddObservation,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationAttemptJournal,
    CodexRegistrationProofRequest,
    CodexRegistrationRejected,
    revalidate_current_attempt_journal,
)
from .codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexFreshPreflightRejected,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortRequest,
    CodexRegistrationPortValueRejectReason,
    CodexRegistrationPortValueRejected,
    revalidate_fresh_preflight_result,
    revalidate_marketplace_add_result,
    revalidate_plugin_add_result,
    revalidate_registration_port_request,
)


class _StrictModel(BaseModel):
    """Frozen, strict values at the pure reducer boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class CodexRegistrationBlockReason(str, Enum):
    """Finite metadata-only reasons that never carry raw caller values."""

    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_STATE = "INVALID_STATE"
    FRESH_PREFLIGHT_INVALID = "FRESH_PREFLIGHT_INVALID"
    FRESH_PREFLIGHT_REJECTED = "FRESH_PREFLIGHT_REJECTED"
    MARKETPLACE_PREEXISTING = "MARKETPLACE_PREEXISTING"
    MARKETPLACE_ADD_NOT_STARTED = "MARKETPLACE_ADD_NOT_STARTED"
    CLASSIFICATION_INVALID = "CLASSIFICATION_INVALID"
    COMPENSATION_PLAN_INVALID = "COMPENSATION_PLAN_INVALID"
    PROOF_REQUEST_INVALID = "PROOF_REQUEST_INVALID"


class _PendingState(_StrictModel):
    request: CodexRegistrationPortRequest
    journal: CodexRegistrationAttemptJournal


class CodexFreshPreflightPending(_PendingState):
    status: Literal["FRESH_PREFLIGHT_PENDING"] = "FRESH_PREFLIGHT_PENDING"


class CodexMarketplaceAddPending(_PendingState):
    status: Literal["MARKETPLACE_ADD_PENDING"] = "MARKETPLACE_ADD_PENDING"


class CodexPluginAddPending(_PendingState):
    status: Literal["PLUGIN_ADD_PENDING"] = "PLUGIN_ADD_PENDING"
    marketplace_observation: CodexMarketplaceAddObservation


CodexRegistrationPending: TypeAlias = (
    CodexFreshPreflightPending | CodexMarketplaceAddPending | CodexPluginAddPending
)


class CodexRegistrationProofRequired(_StrictModel):
    status: Literal["PROOF_REQUIRED"] = "PROOF_REQUIRED"
    journal: CodexRegistrationAttemptJournal
    proof_request: CodexRegistrationProofRequest


class CodexRegistrationCompensationRequired(_StrictModel):
    status: Literal["COMPENSATION_REQUIRED"] = "COMPENSATION_REQUIRED"
    journal: CodexRegistrationAttemptJournal
    plan: CodexCompensationPlan


class CodexRegistrationBlocked(_StrictModel):
    status: Literal["REGISTRATION_BLOCKED"] = "REGISTRATION_BLOCKED"
    reason: CodexRegistrationBlockReason


CodexRegistrationReduction: TypeAlias = (
    CodexRegistrationPending
    | CodexRegistrationProofRequired
    | CodexRegistrationCompensationRequired
    | CodexRegistrationBlocked
)


def begin_codex_registration(value: object) -> CodexRegistrationReduction:
    """Begin one pure current attempt with no effect invocation."""

    request = revalidate_registration_port_request(value)
    if isinstance(request, CodexRegistrationPortValueRejected):
        return _blocked(CodexRegistrationBlockReason.INVALID_REQUEST)
    try:
        journal = CodexRegistrationAttemptJournal(
            request=request.preflight,
            attempt_id=request.attempt_id,
            marketplace_state=CodexAttemptEffectState.NOT_ATTEMPTED,
            plugin_state=CodexAttemptEffectState.NOT_ATTEMPTED,
        )
    except (AttributeError, TypeError, ValidationError, ValueError):
        return _blocked(CodexRegistrationBlockReason.INVALID_REQUEST)
    return _fresh_pending(request, journal)


def advance_codex_registration(state: object, result: object) -> CodexRegistrationReduction:
    """Reduce one exact phase result without calling any operation."""

    current = _revalidate_pending(state)
    if isinstance(current, CodexRegistrationBlocked):
        return current
    if isinstance(current, CodexFreshPreflightPending):
        return _advance_fresh_preflight(current, result)
    if isinstance(current, CodexMarketplaceAddPending):
        return _advance_marketplace_add(current, result)
    return _advance_plugin_add(current, result)


def _fresh_pending(
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
) -> CodexFreshPreflightPending:
    return CodexFreshPreflightPending(request=request, journal=journal)


def _marketplace_pending(
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
) -> CodexMarketplaceAddPending:
    return CodexMarketplaceAddPending(request=request, journal=journal)


def _plugin_pending(
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
    observation: CodexMarketplaceAddObservation,
) -> CodexPluginAddPending:
    return CodexPluginAddPending(
        request=request,
        journal=journal,
        marketplace_observation=observation,
    )


def _revalidate_pending(value: object) -> CodexRegistrationPending | CodexRegistrationBlocked:
    if type(value) not in (CodexFreshPreflightPending, CodexMarketplaceAddPending, CodexPluginAddPending):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    state = cast(_PendingState, value)
    try:
        request_value: object = state.request
        journal_value: object = state.journal
        request = revalidate_registration_port_request(request_value)
    except (AttributeError, TypeError, ValidationError, ValueError):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    if isinstance(request, CodexRegistrationPortValueRejected):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    journal = _revalidate_pending_journal(journal_value, request)
    if isinstance(journal, CodexRegistrationBlocked):
        return journal
    pair = (journal.marketplace_state, journal.plugin_state)
    if type(value) is CodexFreshPreflightPending:
        if value.status != "FRESH_PREFLIGHT_PENDING" or pair != (
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        ):
            return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
        return _fresh_pending(request, journal)
    if type(value) is CodexMarketplaceAddPending:
        if value.status != "MARKETPLACE_ADD_PENDING" or pair != (
            CodexAttemptEffectState.NOT_ATTEMPTED,
            CodexAttemptEffectState.NOT_ATTEMPTED,
        ):
            return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
        return _marketplace_pending(request, journal)
    plugin_state = cast(CodexPluginAddPending, value)
    if plugin_state.status != "PLUGIN_ADD_PENDING" or pair != (
        CodexAttemptEffectState.OWNED,
        CodexAttemptEffectState.NOT_ATTEMPTED,
    ):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    try:
        observation_value: object = plugin_state.marketplace_observation
    except AttributeError:
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    observation = _revalidate_carried_marketplace_observation(observation_value, request)
    if isinstance(observation, CodexRegistrationBlocked):
        return observation
    return _plugin_pending(request, journal, observation)


def _revalidate_pending_journal(
    value: object,
    request: CodexRegistrationPortRequest,
) -> CodexRegistrationAttemptJournal | CodexRegistrationBlocked:
    if type(value) is not CodexRegistrationAttemptJournal:
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    journal = value
    try:
        if (
            type(journal.request) is not type(request.preflight)
            or type(journal.attempt_id) is not type(request.attempt_id)
            or type(journal.marketplace_state) is not CodexAttemptEffectState
            or type(journal.plugin_state) is not CodexAttemptEffectState
        ):
            return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
        request_probe = CodexRegistrationPortRequest.model_construct(
            preflight=journal.request,
            attempt_id=journal.attempt_id,
            expected_version=request.expected_version,
            source_locator=request.source_locator,
            installed_locator=request.installed_locator,
            digest=request.digest,
            expected_auth_policy=request.expected_auth_policy,
            expected_plugin_id=request.expected_plugin_id,
        )
        validated_probe = revalidate_registration_port_request(request_probe)
        if isinstance(validated_probe, CodexRegistrationPortValueRejected):
            return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
        validated = revalidate_current_attempt_journal(journal, request.preflight, request.attempt_id)
    except (AttributeError, TypeError, ValidationError, ValueError):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    if isinstance(validated, CodexRegistrationRejected):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    return validated


def _revalidate_carried_marketplace_observation(
    value: object,
    request: CodexRegistrationPortRequest,
) -> CodexMarketplaceAddObservation | CodexRegistrationBlocked:
    try:
        candidate = CodexMarketplaceAddSucceeded.model_construct(
            request=request,
            confirmed=CodexMarketplaceAddConfirmed(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                start_state=CodexCommandStartState.STARTED,
                already_added=False,
            ),
            observation=value,
        )
        rebuilt = revalidate_marketplace_add_result(candidate, request)
    except (AttributeError, TypeError, ValidationError, ValueError):
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    if type(rebuilt) is not CodexMarketplaceAddSucceeded or rebuilt.confirmed.already_added:
        return _blocked(CodexRegistrationBlockReason.INVALID_STATE)
    return rebuilt.observation


def _advance_fresh_preflight(
    state: CodexFreshPreflightPending,
    result: object,
) -> CodexRegistrationReduction:
    validated = revalidate_fresh_preflight_result(result, state.request)
    if isinstance(validated, CodexRegistrationPortValueRejected):
        return _blocked(CodexRegistrationBlockReason.FRESH_PREFLIGHT_INVALID)
    if isinstance(validated, CodexFreshPreflightRejected):
        return _blocked(CodexRegistrationBlockReason.FRESH_PREFLIGHT_REJECTED)
    if type(validated) is not CodexFreshPreflightAccepted:
        return _blocked(CodexRegistrationBlockReason.FRESH_PREFLIGHT_INVALID)
    return _marketplace_pending(state.request, state.journal)


def _advance_marketplace_add(
    state: CodexMarketplaceAddPending,
    result: object,
) -> CodexRegistrationReduction:
    validated = revalidate_marketplace_add_result(result, state.request)
    if isinstance(validated, CodexRegistrationPortValueRejected):
        return _compensate_untrusted_add(state.request, state.journal, CodexCommandTarget.MARKETPLACE_ADD, validated.reason)
    observation: CodexCommandObservation
    if isinstance(validated, CodexMarketplaceAddSucceeded):
        observation = validated.confirmed
    else:
        observation = validated.failure
    journal = _classify_add(observation, state.request, state.journal)
    if isinstance(journal, CodexRegistrationBlocked):
        return journal
    if isinstance(validated, CodexMarketplaceAddSucceeded):
        if validated.confirmed.already_added:
            return _blocked(CodexRegistrationBlockReason.MARKETPLACE_PREEXISTING)
        return _plugin_pending(state.request, journal, validated.observation)
    if isinstance(validated.failure, CodexPreStartFailure):
        return _blocked(CodexRegistrationBlockReason.MARKETPLACE_ADD_NOT_STARTED)
    return _compensation_required(state.request, journal)


def _advance_plugin_add(
    state: CodexPluginAddPending,
    result: object,
) -> CodexRegistrationReduction:
    validated = revalidate_plugin_add_result(result, state.request)
    if isinstance(validated, CodexRegistrationPortValueRejected):
        return _compensate_untrusted_add(state.request, state.journal, CodexCommandTarget.PLUGIN_ADD, validated.reason)
    observation: CodexCommandObservation
    if isinstance(validated, CodexPluginAddSucceeded):
        observation = validated.confirmed
    else:
        observation = validated.failure
    journal = _classify_add(observation, state.request, state.journal)
    if isinstance(journal, CodexRegistrationBlocked):
        return journal
    if isinstance(validated, CodexRegistrationCommandFailed):
        return _compensation_required(state.request, journal)
    return _proof_required(state, journal, validated.observation)


def _classify_add(
    observation: CodexCommandObservation,
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
) -> CodexRegistrationAttemptJournal | CodexRegistrationBlocked:
    classified = classify_command_attempt(observation, journal, request.preflight, request.attempt_id)
    if isinstance(classified, CodexCommandClassificationRejected):
        return _blocked(CodexRegistrationBlockReason.CLASSIFICATION_INVALID)
    return classified


def _compensate_untrusted_add(
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
    target: CodexCommandTarget,
    reason: CodexRegistrationPortValueRejectReason,
) -> CodexRegistrationReduction:
    failure_reason = (
        CodexStartedFailureReason.IDENTITY_MISMATCH
        if reason
        in (
            CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH,
            CodexRegistrationPortValueRejectReason.TARGET_MISMATCH,
            CodexRegistrationPortValueRejectReason.VERSION_MISMATCH,
        )
        else CodexStartedFailureReason.MALFORMED_RESPONSE
    )
    synthetic = CodexStartedFailure(
        target=target,
        reason=failure_reason,
        start_state=CodexCommandStartState.STARTED,
    )
    classified = _classify_add(synthetic, request, journal)
    if isinstance(classified, CodexRegistrationBlocked):
        return classified
    return _compensation_required(request, classified)


def _compensation_required(
    request: CodexRegistrationPortRequest,
    journal: CodexRegistrationAttemptJournal,
) -> CodexRegistrationReduction:
    plan = build_compensation_plan(journal, request.preflight, request.attempt_id)
    if type(plan) is not CodexCompensationPlan:
        return _blocked(CodexRegistrationBlockReason.COMPENSATION_PLAN_INVALID)
    return CodexRegistrationCompensationRequired(journal=journal, plan=plan)


def _proof_required(
    state: CodexPluginAddPending,
    journal: CodexRegistrationAttemptJournal,
    observation: CodexPluginAddObservation,
) -> CodexRegistrationReduction:
    try:
        exact_observation = CodexPluginAddObservation(
            plugin_id=CodexPluginId(value=state.request.expected_plugin_id.value),
            name=observation.name,
            marketplace_name=observation.marketplace_name,
            version=observation.version,
            installed_path=observation.installed_path,
            auth_policy=observation.auth_policy,
        )
        proof_request = CodexRegistrationProofRequest(
            preflight=state.request.preflight,
            version=state.request.expected_version,
            marketplace_observation=state.marketplace_observation,
            plugin_observation=exact_observation,
            source_locator=state.request.source_locator,
            installed_locator=state.request.installed_locator,
            digest=state.request.digest,
            expected_auth_policy=state.request.expected_auth_policy,
        )
    except (AttributeError, TypeError, ValidationError, ValueError):
        return _blocked(CodexRegistrationBlockReason.PROOF_REQUEST_INVALID)
    return CodexRegistrationProofRequired(journal=journal, proof_request=proof_request)


def _blocked(reason: CodexRegistrationBlockReason) -> CodexRegistrationBlocked:
    return CodexRegistrationBlocked(reason=reason)
