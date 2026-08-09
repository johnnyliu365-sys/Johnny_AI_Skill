from __future__ import annotations

from enum import Enum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from .contracts import InstallationId


CANONICAL_HOST_REGISTRATION_KEY = "JohnnyAIWorkflow/AgentHost"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def _valid_installation(installation_id: InstallationId) -> None:
    value = installation_id.value
    prefix = "installation-"
    suffix = value[len(prefix) :] if value.startswith(prefix) else ""
    if len(suffix) != 16 or any(character not in "0123456789abcdef" for character in suffix):
        raise ValueError("installation id must be opaque lowercase metadata")


class AgentHost(str, Enum):
    CODEX = "CODEX"
    CLAUDE = "CLAUDE"
    RECORDED = "RECORDED"


class HostRegistrationKey(_StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def exact_key(cls, value: str) -> str:
        if value != CANONICAL_HOST_REGISTRATION_KEY:
            raise ValueError("registration key must match the canonical key exactly")
        return value


class HostEvidenceId(_StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def opaque_id(cls, value: str) -> str:
        prefix = "evidence-"
        suffix = value[len(prefix) :] if value.startswith(prefix) else ""
        if len(suffix) != 16 or any(character not in "0123456789abcdef" for character in suffix):
            raise ValueError("host evidence id must be opaque lowercase metadata")
        return value


class HostCommandStatus(str, Enum):
    DETECTED = "DETECTED"
    REGISTERED = "REGISTERED"
    VERIFIED = "VERIFIED"
    ABSENT = "ABSENT"


class HostFailureCode(str, Enum):
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    REGISTER_FAILED = "REGISTER_FAILED"
    VERIFY_FAILED = "VERIFY_FAILED"
    REMOVAL_PROOF_FAILED = "REMOVAL_PROOF_FAILED"
    FOREIGN_REGISTRATION = "FOREIGN_REGISTRATION"


class HostBlockReason(str, Enum):
    UNVERIFIED_HOST = "UNVERIFIED_HOST"
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    REGISTER_FAILED = "REGISTER_FAILED"
    VERIFY_FAILED = "VERIFY_FAILED"
    REMOVAL_PROOF_FAILED = "REMOVAL_PROOF_FAILED"
    FOREIGN_REGISTRATION = "FOREIGN_REGISTRATION"
    COMMAND_RESULT_MISMATCH = "COMMAND_RESULT_MISMATCH"
    RECEIPT_MISMATCH = "RECEIPT_MISMATCH"
    REMOVAL_PROOF_MISMATCH = "REMOVAL_PROOF_MISMATCH"


class HostPortError(Exception):
    def __init__(self, code: HostFailureCode) -> None:
        super().__init__(code.value)
        self.code = code


class HostCapabilityRequest(_StrictModel):
    installation_id: InstallationId
    host: AgentHost
    registration_key: HostRegistrationKey

    @model_validator(mode="after")
    def recorded_only(self) -> Self:
        _valid_installation(self.installation_id)
        if self.host is not AgentHost.RECORDED:
            raise ValueError("recorded verification cannot identify a public host")
        return self


class HostCommandResult(_StrictModel):
    installation_id: InstallationId
    host: AgentHost
    registration_key: HostRegistrationKey
    status: HostCommandStatus
    evidence_id: HostEvidenceId

    @model_validator(mode="after")
    def opaque_installation(self) -> Self:
        _valid_installation(self.installation_id)
        return self


class AgentHostReceipt(_StrictModel):
    installation_id: InstallationId
    host: AgentHost
    registration_key: HostRegistrationKey
    evidence_id: HostEvidenceId

    @model_validator(mode="after")
    def opaque_installation(self) -> Self:
        _valid_installation(self.installation_id)
        return self


class AgentHostRemovalProof(_StrictModel):
    installation_id: InstallationId
    host: AgentHost
    registration_key: HostRegistrationKey
    evidence_id: HostEvidenceId

    @model_validator(mode="after")
    def opaque_installation(self) -> Self:
        _valid_installation(self.installation_id)
        return self


class HostRemovalRequest(_StrictModel):
    installation_id: InstallationId
    host: AgentHost
    registration_key: HostRegistrationKey
    receipt: AgentHostReceipt

    @model_validator(mode="after")
    def exact_receipt(self) -> Self:
        _valid_installation(self.installation_id)
        if self.host is not AgentHost.RECORDED:
            raise ValueError("only a recorded registration can use the recorded lifecycle")
        if (
            self.installation_id != self.receipt.installation_id
            or self.host != self.receipt.host
            or self.registration_key != self.receipt.registration_key
        ):
            raise ValueError("removal request must bind the exact receipt")
        return self

    @classmethod
    def from_receipt(cls, receipt: AgentHostReceipt) -> HostRemovalRequest:
        return cls(
            installation_id=receipt.installation_id,
            host=receipt.host,
            registration_key=receipt.registration_key,
            receipt=receipt,
        )


class HostCapabilitySupported(_StrictModel):
    status: Literal["SUPPORTED"] = "SUPPORTED"
    host: AgentHost
    receipt: AgentHostReceipt
    removal_proof: AgentHostRemovalProof

    @model_validator(mode="after")
    def exact_proof(self) -> Self:
        if self.host is not AgentHost.RECORDED or self.receipt.host != self.host or (
            self.receipt.installation_id != self.removal_proof.installation_id
            or self.receipt.host != self.removal_proof.host
            or self.receipt.registration_key != self.removal_proof.registration_key
        ):
            raise ValueError("support requires exact recorded removal proof")
        return self


class HostCapabilityUnverified(_StrictModel):
    status: Literal["UNVERIFIED"] = "UNVERIFIED"
    host: AgentHost

    @model_validator(mode="after")
    def public_only(self) -> Self:
        if self.host not in (AgentHost.CODEX, AgentHost.CLAUDE):
            raise ValueError("unverified report is reserved for public hosts")
        return self


class HostCapabilityBlocked(_StrictModel):
    status: Literal["BLOCKED"] = "BLOCKED"
    host: AgentHost
    reason: HostBlockReason


HostCapabilityReport = HostCapabilitySupported | HostCapabilityUnverified | HostCapabilityBlocked


class HostRemovalSucceeded(_StrictModel):
    status: Literal["REMOVED"] = "REMOVED"
    proof: AgentHostRemovalProof


class HostRemovalBlocked(_StrictModel):
    status: Literal["BLOCKED"] = "BLOCKED"
    reason: HostBlockReason


HostRemovalResult = HostRemovalSucceeded | HostRemovalBlocked
