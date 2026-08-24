"""Pure high-collaboration evidence admission over two read-only fake ports."""

from __future__ import annotations

import datetime
import re
from enum import Enum
from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from library.local_orchestration.project_authority.contracts import (
    FullBranchRef,
    ProjectAuthorityContract,
    ProjectTopology,
    RemoteRepositoryId,
)

__all__ = (
    "PullRequestReadDisposition",
    "PullRequestState",
    "PullRequestReadRequest",
    "PullRequestReadResult",
    "PullRequestEvidence",
    "PullRequestReadPort",
    "ProviderPolicyReadDisposition",
    "ProviderEnforcementCapability",
    "ProviderPolicyReadRequest",
    "ProviderPolicyReadResult",
    "ProviderEnforcementEvidence",
    "ProviderPolicyReadPort",
    "HighCollaborationAdmissionDecision",
    "HighCollaborationAdmissionRequest",
    "HighCollaborationAdmissionResult",
    "admit_high_collaboration_evidence",
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class PullRequestReadDisposition(str, Enum):
    OBSERVED = "OBSERVED"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"


class PullRequestState(str, Enum):
    OPEN = "OPEN"
    DRAFT = "DRAFT"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


class ProviderPolicyReadDisposition(str, Enum):
    OBSERVED = "OBSERVED"
    UNAVAILABLE = "UNAVAILABLE"
    AMBIGUOUS = "AMBIGUOUS"


class ProviderEnforcementCapability(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PROVEN = "PROVEN"
    UNPROVEN = "UNPROVEN"
    UNSUPPORTED = "UNSUPPORTED"


class HighCollaborationAdmissionDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PR_REQUIRED = "PR_REQUIRED"
    PR_NOT_REVIEWABLE = "PR_NOT_REVIEWABLE"
    PR_HEAD_SHA_MISMATCH = "PR_HEAD_SHA_MISMATCH"
    PR_BASE_REF_MISMATCH = "PR_BASE_REF_MISMATCH"
    PR_APPROVAL_STALE = "PR_APPROVAL_STALE"
    PROVIDER_ENFORCEMENT_UNPROVEN = "PROVIDER_ENFORCEMENT_UNPROVEN"
    PROVIDER_ENFORCEMENT_UNSUPPORTED = "PROVIDER_ENFORCEMENT_UNSUPPORTED"
    REMOTE_IDENTITY_MISMATCH = "REMOTE_IDENTITY_MISMATCH"
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
    return _nonblank(value, field_name)


def _sha(value: str, field_name: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a full lower-case SHA")
    return value


def _aware(value: datetime.datetime, field_name: str) -> datetime.datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _credential(value: str | None) -> bool:
    return value is not None and _CREDENTIAL_MATERIAL.search(value) is not None


def _repository_has_credential(repository: RemoteRepositoryId | None) -> bool:
    return repository is not None and any(
        _credential(value)
        for value in (
            repository.host,
            repository.repository_key,
            repository.alias,
        )
    )


def _credential_free(value: str, field_name: str) -> str:
    value = _nonblank(value, field_name)
    if _credential(value):
        raise ValueError(f"{field_name} contains credential material")
    return value


def _contract_has_credential(contract: ProjectAuthorityContract) -> bool:
    return _repository_has_credential(contract.remote_repository) or any(
        _credential(value)
        for value in (
            contract.schema_id,
            contract.contract_id,
            contract.project_id,
            contract.declaration_artifact_ref,
            contract.gate_id,
        )
    )


class PullRequestReadRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    ticket_id: str = Field(min_length=1, max_length=512)
    read_id: str = Field(min_length=1, max_length=512)
    candidate_sha: str = Field(min_length=40, max_length=40)
    valid_from: datetime.datetime
    decision_at: datetime.datetime

    @field_validator("ticket_id", "read_id")
    @classmethod
    def _request_metadata(cls, value: str) -> str:
        return _credential_free(value, "pull request request metadata")

    @field_validator("candidate_sha")
    @classmethod
    def _candidate_sha(cls, value: str) -> str:
        return _sha(value, "candidate_sha")

    @field_validator("valid_from", "decision_at")
    @classmethod
    def _request_times(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "request time")

    @model_validator(mode="after")
    def _time_window(self) -> Self:
        if _contract_has_credential(self.authority_contract):
            raise ValueError("authority contract contains credential material")
        if self.valid_from > self.decision_at:
            raise ValueError("valid_from must be no later than decision_at")
        return self


class PullRequestReadResult(_StrictModel):
    disposition: PullRequestReadDisposition
    repository: RemoteRepositoryId | None = None
    ticket_id: str | None = None
    pull_request_id: str | None = None
    state: PullRequestState | None = None
    head_ref: FullBranchRef | None = None
    head_sha: str | None = None
    base_ref: FullBranchRef | None = None
    approval_head_sha: str | None = None
    observer: str | None = None
    method: str | None = None
    exit_status: int | None = Field(default=None, ge=0, le=255)
    observed_at: datetime.datetime | None = None
    normalized_evidence_digest: str | None = None

    @field_validator("ticket_id", "pull_request_id", "observer", "method", "normalized_evidence_digest")
    @classmethod
    def _result_metadata(cls, value: str | None) -> str | None:
        return None if value is None else _metadata(value, "pull request result metadata")

    @field_validator("head_sha", "approval_head_sha")
    @classmethod
    def _result_shas(cls, value: str | None) -> str | None:
        return None if value is None else _sha(value, "pull request result SHA")

    @field_validator("observed_at")
    @classmethod
    def _result_time(cls, value: datetime.datetime | None) -> datetime.datetime | None:
        return None if value is None else _aware(value, "pull request observed_at")

    @model_validator(mode="after")
    def _disposition_shape(self) -> Self:
        evidence = (
            self.repository,
            self.ticket_id,
            self.pull_request_id,
            self.state,
            self.head_ref,
            self.head_sha,
            self.base_ref,
            self.approval_head_sha,
            self.observer,
            self.method,
            self.exit_status,
            self.observed_at,
            self.normalized_evidence_digest,
        )
        if self.disposition is PullRequestReadDisposition.OBSERVED:
            if any(value is None for value in evidence[:7] + evidence[8:]):
                raise ValueError("observed pull request result requires complete evidence")
        elif any(value is not None for value in evidence):
            raise ValueError("non-observed pull request result cannot carry evidence")
        return self


class PullRequestEvidence(_StrictModel):
    repository: RemoteRepositoryId
    ticket_id: str = Field(min_length=1, max_length=512)
    pull_request_id: str = Field(min_length=1, max_length=512)
    state: PullRequestState
    head_ref: FullBranchRef
    head_sha: str = Field(min_length=40, max_length=40)
    base_ref: FullBranchRef
    approval_head_sha: str | None = None
    observer: str = Field(min_length=1, max_length=512)
    method: str = Field(min_length=1, max_length=512)
    exit_status: int = Field(ge=0, le=255)
    observed_at: datetime.datetime
    normalized_evidence_digest: str = Field(min_length=1, max_length=2048)

    @field_validator("ticket_id", "pull_request_id", "observer", "method", "normalized_evidence_digest")
    @classmethod
    def _evidence_metadata(cls, value: str) -> str:
        return _credential_free(value, "pull request evidence metadata")

    @field_validator("head_sha", "approval_head_sha")
    @classmethod
    def _evidence_shas(cls, value: str | None) -> str | None:
        return None if value is None else _sha(value, "pull request evidence SHA")

    @field_validator("observed_at")
    @classmethod
    def _evidence_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "pull request evidence observed_at")

    @model_validator(mode="after")
    def _credential_free_evidence(self) -> Self:
        if _repository_has_credential(self.repository):
            raise ValueError("pull request evidence contains credential material")
        return self


class PullRequestReadPort(Protocol):
    def read(self, request: PullRequestReadRequest, /) -> PullRequestReadResult:
        ...


class ProviderPolicyReadRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    ticket_id: str = Field(min_length=1, max_length=512)
    read_id: str = Field(min_length=1, max_length=512)
    candidate_sha: str = Field(min_length=40, max_length=40)
    valid_from: datetime.datetime
    decision_at: datetime.datetime

    @field_validator("ticket_id", "read_id")
    @classmethod
    def _request_metadata(cls, value: str) -> str:
        return _credential_free(value, "provider policy request metadata")

    @field_validator("candidate_sha")
    @classmethod
    def _candidate_sha(cls, value: str) -> str:
        return _sha(value, "candidate_sha")

    @field_validator("valid_from", "decision_at")
    @classmethod
    def _request_times(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "request time")

    @model_validator(mode="after")
    def _time_window(self) -> Self:
        if _contract_has_credential(self.authority_contract):
            raise ValueError("authority contract contains credential material")
        if self.valid_from > self.decision_at:
            raise ValueError("valid_from must be no later than decision_at")
        return self


class ProviderPolicyReadResult(_StrictModel):
    disposition: ProviderPolicyReadDisposition
    repository: RemoteRepositoryId | None = None
    full_ref: FullBranchRef | None = None
    gate_id: str | None = None
    gate_revision: str | None = None
    capability: ProviderEnforcementCapability | None = None
    ui_bypass_prevented: bool | None = None
    stale_approval_invalidated: bool | None = None
    policy_ids: tuple[str, ...] | None = None
    observer: str | None = None
    method: str | None = None
    exit_status: int | None = Field(default=None, ge=0, le=255)
    observed_at: datetime.datetime | None = None
    normalized_evidence_digest: str | None = None

    @field_validator("gate_id", "observer", "method", "normalized_evidence_digest")
    @classmethod
    def _result_metadata(cls, value: str | None) -> str | None:
        return None if value is None else _metadata(value, "provider policy result metadata")

    @field_validator("gate_revision")
    @classmethod
    def _gate_revision(cls, value: str | None) -> str | None:
        return None if value is None else _sha(value, "gate_revision")

    @field_validator("policy_ids")
    @classmethod
    def _policy_ids(cls, value: tuple[str, ...] | None) -> tuple[str, ...] | None:
        if value is None:
            return None
        if len(set(value)) != len(value):
            raise ValueError("policy_ids must not contain duplicates")
        return tuple(_metadata(item, "policy id") for item in value)

    @field_validator("observed_at")
    @classmethod
    def _result_time(cls, value: datetime.datetime | None) -> datetime.datetime | None:
        return None if value is None else _aware(value, "provider policy observed_at")

    @model_validator(mode="after")
    def _disposition_shape(self) -> Self:
        evidence = (
            self.repository,
            self.full_ref,
            self.gate_id,
            self.gate_revision,
            self.capability,
            self.ui_bypass_prevented,
            self.stale_approval_invalidated,
            self.policy_ids,
            self.observer,
            self.method,
            self.exit_status,
            self.observed_at,
            self.normalized_evidence_digest,
        )
        if self.disposition is ProviderPolicyReadDisposition.OBSERVED:
            if any(value is None for value in evidence):
                raise ValueError("observed provider policy result requires complete evidence")
        elif any(value is not None for value in evidence):
            raise ValueError("non-observed provider policy result cannot carry evidence")
        return self


class ProviderEnforcementEvidence(_StrictModel):
    repository: RemoteRepositoryId
    full_ref: FullBranchRef
    gate_id: str = Field(min_length=1, max_length=512)
    gate_revision: str = Field(min_length=40, max_length=40)
    capability: ProviderEnforcementCapability
    ui_bypass_prevented: bool
    stale_approval_invalidated: bool
    policy_ids: tuple[str, ...]
    observer: str = Field(min_length=1, max_length=512)
    method: str = Field(min_length=1, max_length=512)
    exit_status: int = Field(ge=0, le=255)
    observed_at: datetime.datetime
    normalized_evidence_digest: str = Field(min_length=1, max_length=2048)

    @field_validator("gate_id", "observer", "method", "normalized_evidence_digest")
    @classmethod
    def _evidence_metadata(cls, value: str) -> str:
        return _credential_free(value, "provider policy evidence metadata")

    @field_validator("gate_revision")
    @classmethod
    def _evidence_revision(cls, value: str) -> str:
        return _sha(value, "gate_revision")

    @field_validator("policy_ids")
    @classmethod
    def _evidence_policy_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("policy_ids must not contain duplicates")
        return tuple(_credential_free(item, "policy id") for item in value)

    @field_validator("observed_at")
    @classmethod
    def _evidence_time(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "provider policy evidence observed_at")

    @model_validator(mode="after")
    def _credential_free_evidence(self) -> Self:
        if _repository_has_credential(self.repository):
            raise ValueError("provider policy evidence contains credential material")
        return self


class ProviderPolicyReadPort(Protocol):
    def read(self, request: ProviderPolicyReadRequest, /) -> ProviderPolicyReadResult:
        ...


class HighCollaborationAdmissionRequest(_StrictModel):
    authority_contract: ProjectAuthorityContract
    ticket_id: str = Field(min_length=1, max_length=512)
    candidate_sha: str = Field(min_length=40, max_length=40)
    pull_request_read_id: str = Field(min_length=1, max_length=512)
    policy_read_id: str = Field(min_length=1, max_length=512)
    valid_from: datetime.datetime
    decision_at: datetime.datetime

    @field_validator("ticket_id", "pull_request_read_id", "policy_read_id")
    @classmethod
    def _request_metadata(cls, value: str) -> str:
        return _credential_free(value, "admission request metadata")

    @field_validator("candidate_sha")
    @classmethod
    def _candidate_sha(cls, value: str) -> str:
        return _sha(value, "candidate_sha")

    @field_validator("valid_from", "decision_at")
    @classmethod
    def _request_times(cls, value: datetime.datetime) -> datetime.datetime:
        return _aware(value, "request time")

    @model_validator(mode="after")
    def _request_shape(self) -> Self:
        if _contract_has_credential(self.authority_contract):
            raise ValueError("authority contract contains credential material")
        if self.valid_from > self.decision_at:
            raise ValueError("valid_from must be no later than decision_at")
        if self.pull_request_read_id == self.policy_read_id:
            raise ValueError("pull request and policy read IDs must be distinct")
        return self


class HighCollaborationAdmissionResult(_StrictModel):
    decision: HighCollaborationAdmissionDecision
    pull_request_evidence: PullRequestEvidence | None = None
    provider_enforcement_evidence: ProviderEnforcementEvidence | None = None
    failure: HighCollaborationAdmissionDecision | None = None

    @model_validator(mode="after")
    def _decision_shape(self) -> Self:
        if self.decision is HighCollaborationAdmissionDecision.ACCEPTED:
            if (
                self.pull_request_evidence is None
                or self.provider_enforcement_evidence is None
                or self.failure is not None
            ):
                raise ValueError("accepted admission requires both evidence and no failure")
        elif self.decision is HighCollaborationAdmissionDecision.NOT_APPLICABLE:
            if (
                self.pull_request_evidence is not None
                or self.provider_enforcement_evidence is not None
                or self.failure is not None
            ):
                raise ValueError("not-applicable admission carries no evidence or failure")
        elif (
            self.pull_request_evidence is not None
            or self.provider_enforcement_evidence is not None
            or self.failure is not self.decision
        ):
            raise ValueError("rejected admission carries only its identical finite failure")
        return self


def _failure(decision: HighCollaborationAdmissionDecision) -> HighCollaborationAdmissionResult:
    return HighCollaborationAdmissionResult(decision=decision, failure=decision)


def _pull_request_has_credentials(result: PullRequestReadResult) -> bool:
    return _repository_has_credential(result.repository) or any(
        _credential(value)
        for value in (
            result.ticket_id,
            result.pull_request_id,
            result.observer,
            result.method,
            result.normalized_evidence_digest,
        )
    )


def _policy_has_credentials(result: ProviderPolicyReadResult) -> bool:
    return _repository_has_credential(result.repository) or any(
        _credential(value)
        for value in (
            result.gate_id,
            result.observer,
            result.method,
            result.normalized_evidence_digest,
        )
    ) or (result.policy_ids is not None and any(_credential(value) for value in result.policy_ids))


def _pull_request_evidence(result: PullRequestReadResult) -> PullRequestEvidence:
    if (
        result.repository is None
        or result.ticket_id is None
        or result.pull_request_id is None
        or result.state is None
        or result.head_ref is None
        or result.head_sha is None
        or result.base_ref is None
        or result.observer is None
        or result.method is None
        or result.exit_status is None
        or result.observed_at is None
        or result.normalized_evidence_digest is None
    ):
        raise ValueError("observed pull request result is incomplete")
    return PullRequestEvidence(
        repository=result.repository,
        ticket_id=result.ticket_id,
        pull_request_id=result.pull_request_id,
        state=result.state,
        head_ref=result.head_ref,
        head_sha=result.head_sha,
        base_ref=result.base_ref,
        approval_head_sha=result.approval_head_sha,
        observer=result.observer,
        method=result.method,
        exit_status=result.exit_status,
        observed_at=result.observed_at,
        normalized_evidence_digest=result.normalized_evidence_digest,
    )


def _provider_enforcement_evidence(result: ProviderPolicyReadResult) -> ProviderEnforcementEvidence:
    if (
        result.repository is None
        or result.full_ref is None
        or result.gate_id is None
        or result.gate_revision is None
        or result.capability is None
        or result.ui_bypass_prevented is None
        or result.stale_approval_invalidated is None
        or result.policy_ids is None
        or result.observer is None
        or result.method is None
        or result.exit_status is None
        or result.observed_at is None
        or result.normalized_evidence_digest is None
    ):
        raise ValueError("observed provider policy result is incomplete")
    return ProviderEnforcementEvidence(
        repository=result.repository,
        full_ref=result.full_ref,
        gate_id=result.gate_id,
        gate_revision=result.gate_revision,
        capability=result.capability,
        ui_bypass_prevented=result.ui_bypass_prevented,
        stale_approval_invalidated=result.stale_approval_invalidated,
        policy_ids=result.policy_ids,
        observer=result.observer,
        method=result.method,
        exit_status=result.exit_status,
        observed_at=result.observed_at,
        normalized_evidence_digest=result.normalized_evidence_digest,
    )


def admit_high_collaboration_evidence(
    request: HighCollaborationAdmissionRequest,
    pull_request_port: PullRequestReadPort,
    policy_port: ProviderPolicyReadPort,
    /,
) -> HighCollaborationAdmissionResult:
    """Admit one bounded high-collaboration evidence pair without external effects."""

    if request.authority_contract.topology is ProjectTopology.SINGLE_BRANCH:
        return HighCollaborationAdmissionResult(
            decision=HighCollaborationAdmissionDecision.NOT_APPLICABLE,
        )

    pull_request = pull_request_port.read(
        PullRequestReadRequest(
            authority_contract=request.authority_contract,
            ticket_id=request.ticket_id,
            read_id=request.pull_request_read_id,
            candidate_sha=request.candidate_sha,
            valid_from=request.valid_from,
            decision_at=request.decision_at,
        )
    )
    if _pull_request_has_credentials(pull_request):
        return _failure(HighCollaborationAdmissionDecision.SECRET_MATERIAL_DETECTED)
    if pull_request.disposition is PullRequestReadDisposition.NOT_FOUND:
        return _failure(HighCollaborationAdmissionDecision.PR_REQUIRED)
    if pull_request.disposition is not PullRequestReadDisposition.OBSERVED:
        return _failure(HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE)
    if (
        pull_request.repository is None
        or pull_request.ticket_id is None
        or pull_request.state is None
        or pull_request.head_sha is None
        or pull_request.base_ref is None
        or pull_request.observed_at is None
    ):
        return _failure(HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE)
    if pull_request.repository != request.authority_contract.remote_repository:
        return _failure(HighCollaborationAdmissionDecision.REMOTE_IDENTITY_MISMATCH)
    if (
        pull_request.ticket_id != request.ticket_id
        or pull_request.state is not PullRequestState.OPEN
        or pull_request.observed_at < request.valid_from
        or pull_request.observed_at > request.decision_at
    ):
        return _failure(HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE)
    if pull_request.head_sha != request.candidate_sha:
        return _failure(HighCollaborationAdmissionDecision.PR_HEAD_SHA_MISMATCH)
    if pull_request.base_ref != request.authority_contract.project_authority_ref:
        return _failure(HighCollaborationAdmissionDecision.PR_BASE_REF_MISMATCH)
    if pull_request.approval_head_sha != pull_request.head_sha:
        return _failure(HighCollaborationAdmissionDecision.PR_APPROVAL_STALE)

    provider_policy = policy_port.read(
        ProviderPolicyReadRequest(
            authority_contract=request.authority_contract,
            ticket_id=request.ticket_id,
            read_id=request.policy_read_id,
            candidate_sha=request.candidate_sha,
            valid_from=request.valid_from,
            decision_at=request.decision_at,
        )
    )
    if _policy_has_credentials(provider_policy):
        return _failure(HighCollaborationAdmissionDecision.SECRET_MATERIAL_DETECTED)
    if (
        provider_policy.repository is None
        or provider_policy.full_ref is None
        or provider_policy.gate_id is None
        or provider_policy.gate_revision is None
        or provider_policy.capability is None
        or provider_policy.ui_bypass_prevented is None
        or provider_policy.stale_approval_invalidated is None
        or provider_policy.policy_ids is None
        or provider_policy.observed_at is None
    ):
        return _failure(HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN)
    if (
        provider_policy.disposition is ProviderPolicyReadDisposition.OBSERVED
        and (
            provider_policy.repository != request.authority_contract.remote_repository
            or provider_policy.full_ref != request.authority_contract.project_authority_ref
            or provider_policy.gate_id != request.authority_contract.gate_id
            or provider_policy.gate_revision != request.authority_contract.gate_revision
        )
    ):
        return _failure(HighCollaborationAdmissionDecision.REMOTE_IDENTITY_MISMATCH)
    if provider_policy.disposition is not ProviderPolicyReadDisposition.OBSERVED:
        return _failure(HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN)
    if (
        provider_policy.observed_at < request.valid_from
        or provider_policy.observed_at > request.decision_at
    ):
        return _failure(HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN)
    if provider_policy.capability is ProviderEnforcementCapability.UNSUPPORTED:
        return _failure(HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNSUPPORTED)
    if (
        provider_policy.capability is not ProviderEnforcementCapability.PROVEN
        or not provider_policy.ui_bypass_prevented
        or not provider_policy.stale_approval_invalidated
        or not provider_policy.policy_ids
    ):
        return _failure(HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN)
    return HighCollaborationAdmissionResult(
        decision=HighCollaborationAdmissionDecision.ACCEPTED,
        pull_request_evidence=_pull_request_evidence(pull_request),
        provider_enforcement_evidence=_provider_enforcement_evidence(provider_policy),
    )
