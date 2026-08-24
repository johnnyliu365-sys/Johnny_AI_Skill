"""Strict, effect-free contracts for declared project authority."""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = (
    "AuthorityContractAdmission",
    "AuthorityContractAdmissionDecision",
    "AuthorityContractInput",
    "AuthorityIntegrationState",
    "AuthorityLineRole",
    "AuthorityObservationAdmission",
    "AuthorityObservationDecision",
    "BridgeCapability",
    "FullBranchRef",
    "GitObservation",
    "GitObservationSource",
    "PrePushLifecycleRequest",
    "PrePushLifecycleTransition",
    "ProjectAuthorityContract",
    "ProjectTopology",
    "RemoteProviderKind",
    "RemoteRepositoryId",
    "admit_authority_contract",
    "admit_authority_observation",
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        revalidate_instances="always",
        strict=True,
        str_strip_whitespace=True,
    )


class ProjectTopology(str, Enum):
    SINGLE_BRANCH = "SINGLE_BRANCH"
    HIGH_COLLABORATION = "HIGH_COLLABORATION"


class AuthorityLineRole(str, Enum):
    SINGLE = "SINGLE"
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    RELEASE = "RELEASE"


class RemoteProviderKind(str, Enum):
    GIT_GENERIC = "GIT_GENERIC"
    GITHUB = "GITHUB"
    OTHER = "OTHER"


class AuthorityContractAdmissionDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    AUTHORITY_REF_INVALID = "AUTHORITY_REF_INVALID"
    SECRET_MATERIAL_DETECTED = "SECRET_MATERIAL_DETECTED"


class AuthorityObservationDecision(str, Enum):
    DIRECT_REMOTE_REF_ACCEPTED = "DIRECT_REMOTE_REF_ACCEPTED"
    DIRECT_REMOTE_READ_UNAVAILABLE = "DIRECT_REMOTE_READ_UNAVAILABLE"


class GitObservationSource(str, Enum):
    WORKTREE_HEAD = "WORKTREE_HEAD"
    LOCAL_AUTHORITY_REF = "LOCAL_AUTHORITY_REF"
    REMOTE_TRACKING_CACHE = "REMOTE_TRACKING_CACHE"
    DIRECT_REMOTE_REF = "DIRECT_REMOTE_REF"
    PROVIDER_PR_READBACK = "PROVIDER_PR_READBACK"
    PROVIDER_POLICY_READBACK = "PROVIDER_POLICY_READBACK"


class AuthorityIntegrationState(str, Enum):
    CANDIDATE = "CANDIDATE"
    REVIEW_ACCEPTED = "REVIEW_ACCEPTED"
    GATE_REJECTED = "GATE_REJECTED"
    LOCAL_INTEGRATED = "LOCAL_INTEGRATED"
    PUSH_UNCONFIRMED = "PUSH_UNCONFIRMED"
    AUTHORITY_INTEGRATED = "AUTHORITY_INTEGRATED"


class BridgeCapability(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"




class _LifecycleFailure(str, Enum):
    AUTHORITY_CONTRACT_MISSING = "AUTHORITY_CONTRACT_MISSING"
    AUTHORITY_CONTRACT_INVALID = "AUTHORITY_CONTRACT_INVALID"
    AUTHORITY_REF_INVALID = "AUTHORITY_REF_INVALID"
    REMOTE_IDENTITY_MISMATCH = "REMOTE_IDENTITY_MISMATCH"
    DIRECT_REMOTE_READ_UNAVAILABLE = "DIRECT_REMOTE_READ_UNAVAILABLE"
    REMOTE_REF_NOT_FOUND = "REMOTE_REF_NOT_FOUND"
    REMOTE_REF_AMBIGUOUS = "REMOTE_REF_AMBIGUOUS"
    AUTHORITY_REF_MOVED = "AUTHORITY_REF_MOVED"
    CANDIDATE_NOT_A_COMMIT = "CANDIDATE_NOT_A_COMMIT"
    CANDIDATE_SCOPE_MISMATCH = "CANDIDATE_SCOPE_MISMATCH"
    REVIEW_EVIDENCE_MISSING = "REVIEW_EVIDENCE_MISSING"
    COUNTER_MUTATION_EVIDENCE_MISSING = "COUNTER_MUTATION_EVIDENCE_MISSING"
    PR_REQUIRED = "PR_REQUIRED"
    PR_NOT_REVIEWABLE = "PR_NOT_REVIEWABLE"
    PR_HEAD_SHA_MISMATCH = "PR_HEAD_SHA_MISMATCH"
    PR_BASE_REF_MISMATCH = "PR_BASE_REF_MISMATCH"
    PR_APPROVAL_STALE = "PR_APPROVAL_STALE"
    PROVIDER_ENFORCEMENT_UNPROVEN = "PROVIDER_ENFORCEMENT_UNPROVEN"
    PROVIDER_ENFORCEMENT_UNSUPPORTED = "PROVIDER_ENFORCEMENT_UNSUPPORTED"
    GATE_REJECTED = "GATE_REJECTED"
    PUSH_REJECTED = "PUSH_REJECTED"
    PUSH_UNCONFIRMED = "PUSH_UNCONFIRMED"
    REMOTE_READBACK_SHA_MISMATCH = "REMOTE_READBACK_SHA_MISMATCH"
    SECRET_MATERIAL_DETECTED = "SECRET_MATERIAL_DETECTED"
    TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"


_FULL_SHA: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{40}\Z")
_FULL_BRANCH_REF: Final[re.Pattern[str]] = re.compile(
    r"refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]*\Z"
)
_CREDENTIAL_MATERIAL: Final[re.Pattern[str]] = re.compile(
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


def _sha(value: str, field_name: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a full lower-case SHA")
    return value


class FullBranchRef(_StrictModel):
    """An exact branch ref, never a tag, symbolic ref, abbreviation, or SHA."""

    value: str = Field(min_length=1, max_length=512)

    @field_validator("value")
    @classmethod
    def _exact_branch_ref(cls, value: str) -> str:
        if _FULL_BRANCH_REF.fullmatch(value) is None:
            raise ValueError("branch ref must be an exact refs/heads/... value")
        name = value.removeprefix("refs/heads/")
        if ".." in name or "@{" in name or name.endswith("/"):
            raise ValueError("branch ref contains a forbidden branch name")
        return value


class RemoteRepositoryId(_StrictModel):
    """Credential-free stable repository identity plus its local alias."""

    provider_kind: RemoteProviderKind
    host: str = Field(min_length=1, max_length=512)
    repository_key: str = Field(min_length=1, max_length=2048)
    alias: str = Field(min_length=1, max_length=256)

    @field_validator("host", "repository_key", "alias")
    @classmethod
    def _identity_text(cls, value: str, info: object) -> str:
        return _nonblank(value, "repository identity")


class ProjectAuthorityContract(_StrictModel):
    """The declared authority line and its immutable metadata."""

    schema_id: str = "project-authority-contract/revision-05"
    contract_id: str = "PAI-01-AUTHORITY-CONTRACT-LIFECYCLE"
    project_id: str = Field(min_length=1, max_length=512)
    topology: ProjectTopology
    authority_line_role: AuthorityLineRole
    project_authority_ref: FullBranchRef
    remote_repository: RemoteRepositoryId
    declaration_artifact_ref: str = Field(min_length=1, max_length=2048)
    declaration_revision_sha: str = Field(min_length=40, max_length=40)
    gate_id: str = Field(min_length=1, max_length=512)
    gate_revision: str = Field(min_length=40, max_length=40)
    effective_at: datetime

    @field_validator("project_id", "declaration_artifact_ref", "gate_id")
    @classmethod
    def _contract_text(cls, value: str, info: object) -> str:
        return _nonblank(value, "contract field")

    @field_validator("declaration_revision_sha", "gate_revision")
    @classmethod
    def _contract_sha(cls, value: str, info: object) -> str:
        return _sha(value, "contract revision")


class GitObservation(_StrictModel):
    """One normalized observation, with cache observations kept diagnostic."""

    observation_id: str = Field(min_length=1, max_length=512)
    source: GitObservationSource
    repository: RemoteRepositoryId
    full_ref: FullBranchRef
    sha: str = Field(min_length=40, max_length=40)
    observer: str = Field(min_length=1, max_length=512)
    method: str = Field(min_length=1, max_length=512)
    exit_status: int = Field(ge=0, le=255)
    observed_at: datetime
    normalized_evidence_digest: str = Field(min_length=1, max_length=2048)

    @field_validator("observation_id", "observer", "method", "normalized_evidence_digest")
    @classmethod
    def _observation_text(cls, value: str, info: object) -> str:
        return _nonblank(value, "observation field")

    @field_validator("sha")
    @classmethod
    def _observation_sha(cls, value: str) -> str:
        return _sha(value, "observation SHA")

class AuthorityContractInput(_StrictModel):
    """The sole raw input boundary for authority admission."""

    project_id: str = Field(min_length=1, max_length=512)
    topology: ProjectTopology
    authority_line_role: AuthorityLineRole
    project_authority_ref: str = Field(max_length=512)
    remote_provider_kind: RemoteProviderKind
    remote_host: str = Field(min_length=1, max_length=512)
    remote_repository_key: str = Field(min_length=1, max_length=2048)
    remote_alias: str = Field(min_length=1, max_length=256)
    declaration_artifact_ref: str = Field(min_length=1, max_length=2048)
    declaration_revision_sha: str = Field(min_length=40, max_length=40)
    gate_id: str = Field(min_length=1, max_length=512)
    gate_revision: str = Field(min_length=40, max_length=40)
    effective_at: datetime

    @field_validator(
        "project_id",
        "remote_host",
        "remote_repository_key",
        "remote_alias",
        "declaration_artifact_ref",
        "gate_id",
    )
    @classmethod
    def _input_text(cls, value: str, info: object) -> str:
        return _nonblank(value, "authority input field")

    @field_validator("declaration_revision_sha", "gate_revision")
    @classmethod
    def _input_sha(cls, value: str, info: object) -> str:
        return _sha(value, "authority input revision")


class AuthorityContractAdmission(_StrictModel):
    """Named domain decision with an optional immutable success contract."""

    decision: AuthorityContractAdmissionDecision
    contract: ProjectAuthorityContract | None = None
    failure: AuthorityContractAdmissionDecision | None = None

    @model_validator(mode="after")
    def _decision_shape(self) -> Self:
        if self.decision is AuthorityContractAdmissionDecision.ACCEPTED:
            if self.contract is None or self.failure is not None:
                raise ValueError("accepted admission requires one contract and no failure")
        elif self.contract is not None:
            raise ValueError("rejected admission cannot carry a contract")
        return self


class AuthorityObservationAdmission(_StrictModel):
    """Named direct-read decision with an optional immutable observation."""

    decision: AuthorityObservationDecision
    observation: GitObservation | None = None
    failure: AuthorityObservationDecision | None = None

    @model_validator(mode="after")
    def _decision_shape(self) -> Self:
        if self.decision is AuthorityObservationDecision.DIRECT_REMOTE_REF_ACCEPTED:
            if self.observation is None or self.failure is not None:
                raise ValueError("accepted observation requires one observation and no failure")
        elif self.observation is not None:
            raise ValueError("unavailable observation cannot carry an observation")
        return self


class PrePushLifecycleRequest(_StrictModel):
    """A requested state transition inside the local pre-push boundary."""

    current_state: AuthorityIntegrationState
    requested_state: AuthorityIntegrationState


class PrePushLifecycleTransition(_StrictModel):
    """The state and finite failure produced by the pure lifecycle reducer."""

    state: AuthorityIntegrationState
    failure: _LifecycleFailure | None = None


def _has_credential_material(value: AuthorityContractInput) -> bool:
    candidates: tuple[str, ...] = (
        value.remote_host,
        value.remote_repository_key,
        value.remote_alias,
    )
    return any(_CREDENTIAL_MATERIAL.search(candidate) is not None for candidate in candidates)


def _is_full_branch_ref(value: str) -> bool:
    if _FULL_BRANCH_REF.fullmatch(value) is None:
        return False
    name = value.removeprefix("refs/heads/")
    return ".." not in name and "@{" not in name and not name.endswith("/")


def admit_authority_contract(value: AuthorityContractInput) -> AuthorityContractAdmission:
    """Admit metadata only after ref and credential-free identity checks."""

    if _has_credential_material(value):
        return AuthorityContractAdmission(
            decision=AuthorityContractAdmissionDecision.SECRET_MATERIAL_DETECTED,
            failure=AuthorityContractAdmissionDecision.SECRET_MATERIAL_DETECTED,
        )
    if not _is_full_branch_ref(value.project_authority_ref):
        return AuthorityContractAdmission(
            decision=AuthorityContractAdmissionDecision.AUTHORITY_REF_INVALID,
            failure=AuthorityContractAdmissionDecision.AUTHORITY_REF_INVALID,
        )
    contract = ProjectAuthorityContract(
        project_id=value.project_id,
        topology=value.topology,
        authority_line_role=value.authority_line_role,
        project_authority_ref=FullBranchRef(value=value.project_authority_ref),
        remote_repository=RemoteRepositoryId(
            provider_kind=value.remote_provider_kind,
            host=value.remote_host,
            repository_key=value.remote_repository_key,
            alias=value.remote_alias,
        ),
        declaration_artifact_ref=value.declaration_artifact_ref,
        declaration_revision_sha=value.declaration_revision_sha,
        gate_id=value.gate_id,
        gate_revision=value.gate_revision,
        effective_at=value.effective_at,
    )
    return AuthorityContractAdmission(
        decision=AuthorityContractAdmissionDecision.ACCEPTED,
        contract=contract,
    )


def admit_authority_observation(
    observation: GitObservation,
) -> AuthorityObservationAdmission:
    """Accept only a direct remote-ref observation as authority evidence."""

    if observation.source is GitObservationSource.DIRECT_REMOTE_REF:
        return AuthorityObservationAdmission(
            decision=AuthorityObservationDecision.DIRECT_REMOTE_REF_ACCEPTED,
            observation=observation,
        )
    return AuthorityObservationAdmission(
        decision=AuthorityObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE,
        failure=AuthorityObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE,
    )
