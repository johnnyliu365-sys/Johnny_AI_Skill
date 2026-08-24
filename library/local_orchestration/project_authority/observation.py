"""Pure direct-remote observation contracts and one-call reducer."""

from __future__ import annotations

import datetime
import re
from enum import Enum
from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from library.local_orchestration.project_authority.contracts import (
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    ProjectAuthorityContract,
    RemoteRepositoryId,
)

__all__ = (
    "DirectRemoteObservationDecision",
    "DirectRemoteObservationPort",
    "DirectRemoteObservationRequest",
    "DirectRemoteObservationResult",
    "DirectRemoteReadDisposition",
    "DirectRemoteReadResult",
    "observe_declared_remote",
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class DirectRemoteReadDisposition(str, Enum):
    OBSERVED = "OBSERVED"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"


class DirectRemoteObservationDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    DIRECT_REMOTE_READ_UNAVAILABLE = "DIRECT_REMOTE_READ_UNAVAILABLE"
    REMOTE_REF_NOT_FOUND = "REMOTE_REF_NOT_FOUND"
    REMOTE_REF_AMBIGUOUS = "REMOTE_REF_AMBIGUOUS"
    REMOTE_IDENTITY_MISMATCH = "REMOTE_IDENTITY_MISMATCH"
    DIRECT_REMOTE_OBSERVATION_STALE = "DIRECT_REMOTE_OBSERVATION_STALE"
    AUTHORITY_REF_MOVED = "AUTHORITY_REF_MOVED"
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


def _aware(value: datetime.datetime, field_name: str) -> datetime.datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _sha(value: str, field_name: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a full lower-case SHA")
    return value


class DirectRemoteObservationRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    observation_id: str = Field(min_length=1, max_length=512)
    valid_from: datetime.datetime
    decision_at: datetime.datetime
    expected_sha: str | None = None

    @field_validator("observation_id")
    @classmethod
    def _observation_text(cls, value: str) -> str:
        return _nonblank(value, "observation_id")

    @field_validator("valid_from", "decision_at")
    @classmethod
    def _request_times(cls, value: datetime.datetime, info: object) -> datetime.datetime:
        return _aware(value, "request time")

    @field_validator("expected_sha")
    @classmethod
    def _expected_sha(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _sha(value, "expected_sha")

    @model_validator(mode="after")
    def _time_window(self) -> Self:
        if self.valid_from > self.decision_at:
            raise ValueError("valid_from must be no later than decision_at")
        return self


class DirectRemoteReadResult(_StrictModel):
    disposition: DirectRemoteReadDisposition
    source: GitObservationSource
    repository: RemoteRepositoryId
    full_ref: FullBranchRef
    sha: str | None = None
    observer: str = Field(min_length=1, max_length=2048)
    method: str = Field(min_length=1, max_length=2048)
    exit_status: int = Field(ge=0, le=255)
    observed_at: datetime.datetime
    normalized_evidence_digest: str = Field(min_length=1, max_length=4096)

    @field_validator("observer", "method", "normalized_evidence_digest")
    @classmethod
    def _read_text(cls, value: str, info: object) -> str:
        return _nonblank(value, "read result field")

    @field_validator("observed_at")
    @classmethod
    def _observed_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "observed_at")

    @field_validator("sha")
    @classmethod
    def _observed_sha(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _sha(value, "sha")

    @model_validator(mode="after")
    def _disposition_shape(self) -> Self:
        if self.disposition is DirectRemoteReadDisposition.OBSERVED:
            if self.sha is None:
                raise ValueError("OBSERVED requires one SHA")
        elif self.sha is not None:
            raise ValueError("non-observed disposition cannot carry a SHA")
        return self


class DirectRemoteObservationResult(_StrictModel):
    decision: DirectRemoteObservationDecision
    observation: GitObservation | None = None
    failure: DirectRemoteObservationDecision | None = None

    @model_validator(mode="after")
    def _decision_shape(self) -> Self:
        if self.decision is DirectRemoteObservationDecision.ACCEPTED:
            if self.observation is None or self.failure is not None:
                raise ValueError("accepted result requires one observation and no failure")
            if self.observation.source is not GitObservationSource.DIRECT_REMOTE_REF:
                raise ValueError("accepted result requires a direct remote observation")
        elif self.observation is not None or self.failure is not self.decision:
            raise ValueError("failure result must carry only its named failure")
        return self


class DirectRemoteObservationPort(Protocol):
    def observe(
        self,
        request: DirectRemoteObservationRequest,
        /,
    ) -> DirectRemoteReadResult:
        ...


def _credential_metadata(result: DirectRemoteReadResult) -> bool:
    values: tuple[str, ...] = (result.observer, result.method, result.normalized_evidence_digest)
    return any(_CREDENTIAL_MATERIAL.search(value) is not None for value in values)


def _failure(decision: DirectRemoteObservationDecision) -> DirectRemoteObservationResult:
    return DirectRemoteObservationResult(decision=decision, failure=decision)


def observe_declared_remote(
    request: DirectRemoteObservationRequest,
    port: DirectRemoteObservationPort,
    /,
) -> DirectRemoteObservationResult:
    """Classify exactly one validated fake read without performing I/O."""

    read_result = port.observe(request)
    if _credential_metadata(read_result):
        return _failure(DirectRemoteObservationDecision.SECRET_MATERIAL_DETECTED)
    if read_result.repository != request.authority_contract.remote_repository:
        return _failure(DirectRemoteObservationDecision.REMOTE_IDENTITY_MISMATCH)
    if read_result.full_ref != request.authority_contract.project_authority_ref:
        return _failure(DirectRemoteObservationDecision.REMOTE_IDENTITY_MISMATCH)
    if read_result.disposition is DirectRemoteReadDisposition.UNAVAILABLE:
        return _failure(DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE)
    if read_result.disposition is DirectRemoteReadDisposition.NOT_FOUND:
        return _failure(DirectRemoteObservationDecision.REMOTE_REF_NOT_FOUND)
    if read_result.disposition is DirectRemoteReadDisposition.AMBIGUOUS:
        return _failure(DirectRemoteObservationDecision.REMOTE_REF_AMBIGUOUS)
    if read_result.source is not GitObservationSource.DIRECT_REMOTE_REF:
        return _failure(DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE)
    if not request.valid_from <= read_result.observed_at <= request.decision_at:
        return _failure(DirectRemoteObservationDecision.DIRECT_REMOTE_OBSERVATION_STALE)
    if request.expected_sha is not None and read_result.sha != request.expected_sha:
        return _failure(DirectRemoteObservationDecision.AUTHORITY_REF_MOVED)
    if read_result.sha is None:
        return _failure(DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE)
    observation = GitObservation(
        observation_id=request.observation_id,
        source=read_result.source,
        repository=read_result.repository,
        full_ref=read_result.full_ref,
        sha=read_result.sha,
        observer=read_result.observer,
        method=read_result.method,
        exit_status=read_result.exit_status,
        observed_at=read_result.observed_at,
        normalized_evidence_digest=read_result.normalized_evidence_digest,
    )
    return DirectRemoteObservationResult(
        decision=DirectRemoteObservationDecision.ACCEPTED,
        observation=observation,
    )
