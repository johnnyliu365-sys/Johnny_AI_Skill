"""Pure authority finalization over injected non-force push and readback ports."""

from __future__ import annotations

import datetime
import re
from enum import Enum
from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from library.local_orchestration.project_authority.contracts import (
    AuthorityIntegrationState,
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    PrePushLifecycleRequest,
    PrePushLifecycleTransition,
    ProjectAuthorityContract,
    RemoteRepositoryId,
    _LifecycleFailure,
)
from library.local_orchestration.project_authority.observation import (
    DirectRemoteObservationPort,
    DirectRemoteObservationRequest,
    DirectRemoteObservationResult,
    DirectRemoteObservationDecision,
    observe_declared_remote,
)

__all__ = (
    "PrePushLifecycleRequest",
    "PrePushLifecycleTransition",
    "advance_pre_push_lifecycle",
    "NonForcePushDisposition",
    "NonForcePushRequest",
    "NonForcePushResult",
    "NonForcePushPort",
    "AuthorityFinalizationFailure",
    "AuthorityFinalizationRequest",
    "AuthorityFinalizationResult",
    "finalize_authority_integration",
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class NonForcePushDisposition(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNCONFIRMED = "UNCONFIRMED"


class AuthorityFinalizationFailure(str, Enum):
    LOCAL_INTEGRATION_EVIDENCE_INVALID = "LOCAL_INTEGRATION_EVIDENCE_INVALID"
    PRE_PUSH_OBSERVATION_INVALID = "PRE_PUSH_OBSERVATION_INVALID"
    REMOTE_IDENTITY_MISMATCH = "REMOTE_IDENTITY_MISMATCH"
    AUTHORITY_REF_MOVED = "AUTHORITY_REF_MOVED"
    PUSH_REJECTED = "PUSH_REJECTED"
    PUSH_UNCONFIRMED = "PUSH_UNCONFIRMED"
    DIRECT_REMOTE_READ_UNAVAILABLE = "DIRECT_REMOTE_READ_UNAVAILABLE"
    REMOTE_REF_NOT_FOUND = "REMOTE_REF_NOT_FOUND"
    REMOTE_REF_AMBIGUOUS = "REMOTE_REF_AMBIGUOUS"
    DIRECT_REMOTE_OBSERVATION_STALE = "DIRECT_REMOTE_OBSERVATION_STALE"
    REMOTE_READBACK_SHA_MISMATCH = "REMOTE_READBACK_SHA_MISMATCH"
    SECRET_MATERIAL_DETECTED = "SECRET_MATERIAL_DETECTED"


_FULL_SHA: re.Pattern[str] = re.compile(r"[0-9a-f]{40}\Z")
_CREDENTIAL_MATERIAL: re.Pattern[str] = re.compile(
    r"(?:^|[^A-Za-z])(?:token|secret|password|passwd|authorization|bearer)"
    r"\s*[:=]"
    r"|://[^\s/@]+(?::[^\s/@]*)?@"
    r"|[^\s/@:]+:[^\s/@]+@"
    r"|\b(?:ssh|git)://[^\s/@]+@",
    re.IGNORECASE,
)


def _nonblank(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} must not be blank")
    return value


def _metadata(value: str, field_name: str) -> str:
    value = _nonblank(value, field_name)
    if _CREDENTIAL_MATERIAL.search(value) is not None:
        raise ValueError(f"{field_name} contains credential material")
    return value


def _sha(value: str, field_name: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a full lower-case SHA")
    return value


def _aware(value: datetime.datetime, field_name: str) -> datetime.datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


class NonForcePushRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    attempt_id: str = Field(min_length=1, max_length=512)
    expected_remote_base: GitObservation
    local_integrated_sha: str = Field(min_length=40, max_length=40)
    requested_at: datetime.datetime

    @field_validator("attempt_id")
    @classmethod
    def _attempt_text(cls, value: str) -> str:
        return _metadata(value, "attempt_id")

    @field_validator("local_integrated_sha")
    @classmethod
    def _local_sha(cls, value: str) -> str:
        return _sha(value, "local_integrated_sha")

    @field_validator("requested_at")
    @classmethod
    def _request_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "requested_at")

    @model_validator(mode="after")
    def _base_identity(self) -> Self:
        if self.expected_remote_base.source is not GitObservationSource.DIRECT_REMOTE_REF:
            raise ValueError("expected remote base must be a direct remote observation")
        if self.expected_remote_base.repository != self.authority_contract.remote_repository:
            raise ValueError("expected remote base repository does not match authority")
        if self.expected_remote_base.full_ref != self.authority_contract.project_authority_ref:
            raise ValueError("expected remote base ref does not match authority")
        return self


class NonForcePushResult(_StrictModel):
    disposition: NonForcePushDisposition
    repository: RemoteRepositoryId
    full_ref: FullBranchRef
    attempt_id: str = Field(min_length=1, max_length=512)
    expected_base_sha: str = Field(min_length=40, max_length=40)
    requested_sha: str = Field(min_length=40, max_length=40)
    executor: str = Field(min_length=1, max_length=512)
    method: str = Field(min_length=1, max_length=512)
    normalized_evidence_digest: str = Field(min_length=1, max_length=2048)
    exit_status: int = Field(ge=0, le=255)
    completed_at: datetime.datetime

    @field_validator("attempt_id", "executor", "method", "normalized_evidence_digest")
    @classmethod
    def _result_metadata(cls, value: str) -> str:
        return _metadata(value, "push result metadata")

    @field_validator("expected_base_sha", "requested_sha")
    @classmethod
    def _result_shas(cls, value: str) -> str:
        return _sha(value, "push result SHA")

    @field_validator("completed_at")
    @classmethod
    def _completion_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "completed_at")


class NonForcePushPort(Protocol):
    def push(self, request: NonForcePushRequest, /) -> NonForcePushResult:
        ...


class AuthorityFinalizationRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    local_lifecycle: PrePushLifecycleTransition
    local_integrated_sha: str = Field(min_length=40, max_length=40)
    pre_push_observation: GitObservation
    attempt_id: str = Field(min_length=1, max_length=512)
    post_push_observation_id: str = Field(min_length=1, max_length=512)
    requested_at: datetime.datetime
    decision_at: datetime.datetime

    @field_validator("local_integrated_sha")
    @classmethod
    def _integrated_sha(cls, value: str) -> str:
        return _sha(value, "local_integrated_sha")

    @field_validator("attempt_id", "post_push_observation_id")
    @classmethod
    def _request_metadata(cls, value: str) -> str:
        return _metadata(value, "finalization identifier")

    @field_validator("requested_at", "decision_at")
    @classmethod
    def _finalization_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "finalization time")

    @model_validator(mode="after")
    def _decision_window(self) -> Self:
        if self.requested_at > self.decision_at:
            raise ValueError("requested_at must be no later than decision_at")
        return self


class AuthorityFinalizationResult(_StrictModel):
    state: AuthorityIntegrationState
    failure: AuthorityFinalizationFailure | None = None
    push: NonForcePushResult | None = None
    readback: GitObservation | None = None

    @model_validator(mode="after")
    def _result_shape(self) -> Self:
        if self.state is AuthorityIntegrationState.AUTHORITY_INTEGRATED:
            if (
                self.failure is not None
                or self.push is None
                or self.push.disposition is not NonForcePushDisposition.ACCEPTED
                or self.readback is None
                or self.readback.source is not GitObservationSource.DIRECT_REMOTE_REF
            ):
                raise ValueError("authority integration requires accepted push and direct readback")
            return self
        if self.state is not AuthorityIntegrationState.PUSH_UNCONFIRMED:
            raise ValueError("finalization failures must remain PUSH_UNCONFIRMED")
        if self.failure is None:
            raise ValueError("unconfirmed result requires one finite failure")
        if self.readback is not None and self.readback.source is not GitObservationSource.DIRECT_REMOTE_REF:
            raise ValueError("failure readback cannot use a non-direct source")
        return self


def _failure(
    failure: AuthorityFinalizationFailure,
    push: NonForcePushResult | None = None,
    readback: GitObservation | None = None,
) -> AuthorityFinalizationResult:
    return AuthorityFinalizationResult(
        state=AuthorityIntegrationState.PUSH_UNCONFIRMED,
        failure=failure,
        push=push,
        readback=readback,
    )


def _has_credential_observation(observation: GitObservation) -> bool:
    values: tuple[str, ...] = (
        observation.observation_id,
        observation.repository.host,
        observation.repository.repository_key,
        observation.repository.alias,
        observation.observer,
        observation.method,
        observation.normalized_evidence_digest,
    )
    return any(_CREDENTIAL_MATERIAL.search(value) is not None for value in values)


def _has_credential_push_result(result: NonForcePushResult) -> bool:
    values: tuple[str, ...] = (
        result.attempt_id,
        result.repository.host,
        result.repository.repository_key,
        result.repository.alias,
        result.executor,
        result.method,
        result.normalized_evidence_digest,
    )
    return any(_CREDENTIAL_MATERIAL.search(value) is not None for value in values)


def _map_observation_failure(
    result: DirectRemoteObservationResult,
) -> AuthorityFinalizationFailure:
    if result.failure is DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE:
        return AuthorityFinalizationFailure.DIRECT_REMOTE_READ_UNAVAILABLE
    if result.failure is DirectRemoteObservationDecision.REMOTE_REF_NOT_FOUND:
        return AuthorityFinalizationFailure.REMOTE_REF_NOT_FOUND
    if result.failure is DirectRemoteObservationDecision.REMOTE_REF_AMBIGUOUS:
        return AuthorityFinalizationFailure.REMOTE_REF_AMBIGUOUS
    if result.failure is DirectRemoteObservationDecision.REMOTE_IDENTITY_MISMATCH:
        return AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH
    if result.failure is DirectRemoteObservationDecision.DIRECT_REMOTE_OBSERVATION_STALE:
        return AuthorityFinalizationFailure.DIRECT_REMOTE_OBSERVATION_STALE
    if result.failure is DirectRemoteObservationDecision.AUTHORITY_REF_MOVED:
        return AuthorityFinalizationFailure.AUTHORITY_REF_MOVED
    if result.failure is DirectRemoteObservationDecision.SECRET_MATERIAL_DETECTED:
        return AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED
    raise ValueError("accepted observation cannot be mapped as a failure")


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


def finalize_authority_integration(
    request: AuthorityFinalizationRequest,
    push_port: NonForcePushPort,
    observation_port: DirectRemoteObservationPort,
    /,
) -> AuthorityFinalizationResult:
    """Finalize local integration only after one accepted push and direct readback."""

    if (
        request.local_lifecycle.state is not AuthorityIntegrationState.LOCAL_INTEGRATED
        or request.local_lifecycle.failure is not None
    ):
        return _failure(AuthorityFinalizationFailure.LOCAL_INTEGRATION_EVIDENCE_INVALID)

    pre_push = request.pre_push_observation
    if _has_credential_observation(pre_push):
        return _failure(AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED)
    if pre_push.observed_at.tzinfo is None or pre_push.observed_at.utcoffset() is None:
        return _failure(AuthorityFinalizationFailure.PRE_PUSH_OBSERVATION_INVALID)
    if pre_push.source is not GitObservationSource.DIRECT_REMOTE_REF:
        return _failure(AuthorityFinalizationFailure.PRE_PUSH_OBSERVATION_INVALID)
    if pre_push.repository != request.authority_contract.remote_repository:
        return _failure(AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH)
    if pre_push.full_ref != request.authority_contract.project_authority_ref:
        return _failure(AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH)

    push_request = NonForcePushRequest(
        authority_contract=request.authority_contract,
        attempt_id=request.attempt_id,
        expected_remote_base=pre_push,
        local_integrated_sha=request.local_integrated_sha,
        requested_at=request.requested_at,
    )
    push_result = push_port.push(push_request)
    if _has_credential_push_result(push_result):
        return _failure(AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED)
    if push_result.repository != request.authority_contract.remote_repository:
        return _failure(AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH, push_result)
    if push_result.full_ref != request.authority_contract.project_authority_ref:
        return _failure(AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH, push_result)
    if push_result.attempt_id != request.attempt_id:
        return _failure(AuthorityFinalizationFailure.PUSH_UNCONFIRMED, push_result)
    if push_result.expected_base_sha != pre_push.sha:
        return _failure(AuthorityFinalizationFailure.AUTHORITY_REF_MOVED, push_result)
    if push_result.requested_sha != request.local_integrated_sha:
        return _failure(AuthorityFinalizationFailure.PUSH_UNCONFIRMED, push_result)
    if push_result.disposition is NonForcePushDisposition.REJECTED:
        return _failure(AuthorityFinalizationFailure.PUSH_REJECTED, push_result)
    if push_result.disposition is NonForcePushDisposition.UNCONFIRMED:
        return _failure(AuthorityFinalizationFailure.PUSH_UNCONFIRMED, push_result)
    if push_result.completed_at > request.decision_at:
        return _failure(AuthorityFinalizationFailure.DIRECT_REMOTE_OBSERVATION_STALE, push_result)

    observation_request = DirectRemoteObservationRequest(
        authority_contract=request.authority_contract,
        observation_id=request.post_push_observation_id,
        valid_from=push_result.completed_at,
        decision_at=request.decision_at,
        expected_sha=None,
    )
    observation_result = observe_declared_remote(observation_request, observation_port)
    if observation_result.failure is not None:
        return _failure(_map_observation_failure(observation_result), push_result)
    if observation_result.observation is None:
        return _failure(AuthorityFinalizationFailure.DIRECT_REMOTE_READ_UNAVAILABLE, push_result)
    readback = observation_result.observation
    if readback.sha != request.local_integrated_sha:
        return _failure(
            AuthorityFinalizationFailure.REMOTE_READBACK_SHA_MISMATCH,
            push_result,
            readback,
        )
    return AuthorityFinalizationResult(
        state=AuthorityIntegrationState.AUTHORITY_INTEGRATED,
        push=push_result,
        readback=readback,
    )
