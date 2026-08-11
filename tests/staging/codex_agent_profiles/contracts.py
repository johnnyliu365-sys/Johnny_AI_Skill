"""Strict metadata-only contracts for Ticket 06A role-profile capability proof."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
import re
from typing import Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from tests.staging.environment_core.contracts import TeardownBlockReason, TeardownStatus


class StrictModel(BaseModel):
    """Reject dynamic values before they reach the disposable Codex boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class AgentRole(str, Enum):
    REVIEWER = "REVIEWER"
    IMPLEMENTATION = "IMPLEMENTATION"


class AgentToolPolicy(str, Enum):
    REVIEWER_ENABLED = "REVIEWER_ENABLED"
    IMPLEMENTATION_DISABLED = "IMPLEMENTATION_DISABLED"

    @property
    def agents_enabled(self) -> bool:
        return self is AgentToolPolicy.REVIEWER_ENABLED


class AgentProfileName(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def canonical_profile_name(cls, value: str) -> str:
        if re.fullmatch(r"[a-z][a-z0-9-]{2,63}", value) is None:
            raise ValueError("profile name must be one canonical lowercase identifier")
        return value


class ProfileDescription(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def bounded_single_line_description(cls, value: str) -> str:
        if not value or value != value.strip() or "\n" in value or "\r" in value or len(value) > 160:
            raise ValueError("profile description must be one bounded nonblank line")
        return value


class DeveloperInstructions(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def bounded_instruction_text(cls, value: str) -> str:
        if not value or value != value.strip() or "\x00" in value or len(value) > 1_024:
            raise ValueError("developer instructions must be bounded nonblank text")
        return value


class AgentProfileSpec(StrictModel):
    """The three frozen official fields plus a finite agents.enabled policy."""

    role: AgentRole
    name: AgentProfileName
    description: ProfileDescription
    developer_instructions: DeveloperInstructions
    tool_policy: AgentToolPolicy

    @model_validator(mode="after")
    def exact_role_policy(self) -> AgentProfileSpec:
        expected = (
            AgentToolPolicy.REVIEWER_ENABLED
            if self.role is AgentRole.REVIEWER
            else AgentToolPolicy.IMPLEMENTATION_DISABLED
        )
        if self.tool_policy is not expected:
            raise ValueError("role must use the frozen multi-agent policy")
        return self


class FrozenRoleProfiles(StrictModel):
    reviewer: AgentProfileSpec
    implementation: AgentProfileSpec

    @model_validator(mode="after")
    def exact_roles(self) -> FrozenRoleProfiles:
        if self.reviewer.role is not AgentRole.REVIEWER or self.implementation.role is not AgentRole.IMPLEMENTATION:
            raise ValueError("frozen profiles must bind reviewer and implementation roles")
        return self


def frozen_role_profiles() -> FrozenRoleProfiles:
    """Return the only profile pair Ticket 06A may materialize."""

    return FrozenRoleProfiles(
        reviewer=AgentProfileSpec(
            role=AgentRole.REVIEWER,
            name=AgentProfileName(value="reviewer-06a"),
            description=ProfileDescription(value="Ticket 06A reviewer orchestration profile"),
            developer_instructions=DeveloperInstructions(
                value="Review the assigned ticket and use only receipt-bound reviewer orchestration."
            ),
            tool_policy=AgentToolPolicy.REVIEWER_ENABLED,
        ),
        implementation=AgentProfileSpec(
            role=AgentRole.IMPLEMENTATION,
            name=AgentProfileName(value="implementation-06a"),
            description=ProfileDescription(value="Ticket 06A implementation profile"),
            developer_instructions=DeveloperInstructions(
                value="Implement only the assigned ticket and never control another agent or task."
            ),
            tool_policy=AgentToolPolicy.IMPLEMENTATION_DISABLED,
        ),
    )


class CodexExecutableLocator(StrictModel):
    """One explicit executable, never a PATH scan or wildcard fallback."""

    value: str

    @field_validator("value")
    @classmethod
    def exact_codex_executable(cls, value: str) -> str:
        path = Path(value)
        if (
            not value
            or value != value.strip()
            or "\x00" in value
            or "*" in value
            or "?" in value
            or "%" in value
            or ".." in path.parts
            or not path.is_absolute()
            or path.name != "codex.exe"
        ):
            raise ValueError("executable locator must be one exact lowercase codex.exe path")
        return str(path)

    @property
    def path(self) -> Path:
        return Path(self.value)


class AgentProfileLocator(StrictModel):
    """A profile locator may name only one generated agents/<name>.toml file."""

    value: str

    @field_validator("value")
    @classmethod
    def exact_profile_locator(cls, value: str) -> str:
        if re.fullmatch(r"agents/[a-z][a-z0-9-]{2,63}\.toml", value) is None:
            raise ValueError("profile locator must be one canonical agents TOML path")
        return value


class MetadataDigest(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def sha256_hex(cls, value: str) -> str:
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError("metadata digest must be lowercase SHA-256 hex")
        return value


class ProfileReceipt(StrictModel):
    role: AgentRole
    locator: AgentProfileLocator
    digest: MetadataDigest


class FrozenProfileReceipts(StrictModel):
    reviewer: ProfileReceipt
    implementation: ProfileReceipt

    @model_validator(mode="after")
    def exact_receipt_roles(self) -> FrozenProfileReceipts:
        if self.reviewer.role is not AgentRole.REVIEWER or self.implementation.role is not AgentRole.IMPLEMENTATION:
            raise ValueError("profile receipts must retain their named roles")
        return self


class OrchestrationTool(str, Enum):
    CREATE = "CREATE"
    SPAWN = "SPAWN"
    FORK = "FORK"
    DISPATCH = "DISPATCH"
    FOLLOW_UP = "FOLLOW_UP"
    STEER = "STEER"
    WAIT = "WAIT"
    INTERRUPT = "INTERRUPT"
    CLOSE = "CLOSE"


_ORCHESTRATION_TOOLS: tuple[OrchestrationTool, ...] = tuple(OrchestrationTool)


class ToolSurface(StrictModel):
    tools: tuple[OrchestrationTool, ...]

    @field_validator("tools")
    @classmethod
    def canonical_distinct_tools(cls, tools: tuple[OrchestrationTool, ...]) -> tuple[OrchestrationTool, ...]:
        expected_order = tuple(tool for tool in _ORCHESTRATION_TOOLS if tool in tools)
        if len(set(tools)) != len(tools) or tools != expected_order:
            raise ValueError("tool surface must be distinct and canonical")
        return tools

    @property
    def is_full_orchestration_surface(self) -> bool:
        return self.tools == _ORCHESTRATION_TOOLS

    @property
    def is_empty(self) -> bool:
        return not self.tools


class CapabilityReadbackStatus(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    UNSUPPORTED_CONFIG = "UNSUPPORTED_CONFIG"
    ACCESS_DENIED = "ACCESS_DENIED"
    TIMEOUT = "TIMEOUT"
    MALFORMED_OUTPUT = "MALFORMED_OUTPUT"
    OUTPUT_UNAVAILABLE = "OUTPUT_UNAVAILABLE"


class EffectiveCapabilityReadback(StrictModel):
    """Metadata-only evidence from a host command, never a config parser assertion."""

    status: CapabilityReadbackStatus = CapabilityReadbackStatus.EFFECTIVE
    version_digest: MetadataDigest
    capability_digest: MetadataDigest
    execution_digest: MetadataDigest
    profile_bundle_digest: MetadataDigest
    reviewer_direct: ToolSurface
    reviewer_indirect: ToolSurface
    implementation_direct: ToolSurface
    implementation_indirect: ToolSurface


class UnavailableCapabilityReadback(StrictModel):
    status: CapabilityReadbackStatus

    @model_validator(mode="after")
    def not_effective(self) -> UnavailableCapabilityReadback:
        if self.status is CapabilityReadbackStatus.EFFECTIVE:
            raise ValueError("unavailable readback cannot claim effective evidence")
        return self


CapabilityReadback: TypeAlias = EffectiveCapabilityReadback | UnavailableCapabilityReadback


class CapabilityReadbackPort(Protocol):
    """A future host adapter may provide readback; 06A never parses config into success."""

    def read(
        self,
        profile_receipts: FrozenProfileReceipts,
        execution_digest: MetadataDigest,
        profile_bundle_digest: MetadataDigest,
    ) -> CapabilityReadback:
        """Return finite metadata only after a bounded local host observation."""


class ProcessEvidenceKind(str, Enum):
    VERSION_OUTPUT_UNREADABLE = "VERSION_OUTPUT_UNREADABLE"
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    TIMEOUT = "TIMEOUT"
    WAIT_FAILED = "WAIT_FAILED"
    TERMINATION_FAILED = "TERMINATION_FAILED"
    NONZERO_EXIT = "NONZERO_EXIT"
    GENERIC_LAUNCH_FAILURE = "GENERIC_LAUNCH_FAILURE"
    MALFORMED_OBSERVATION = "MALFORMED_OBSERVATION"


class CapabilityProbeStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    INSTALL_BLOCKED = "INSTALL_BLOCKED"


class RoleIsolationStatus(str, Enum):
    PROVEN = "PROVEN"
    ROLE_ISOLATION_UNPROVEN = "ROLE_ISOLATION_UNPROVEN"


class TeardownEvidence(StrictModel):
    status: TeardownStatus
    reason: TeardownBlockReason
    root_absent: bool
    profile_files_absent: bool

    @model_validator(mode="after")
    def removed_state_requires_physical_absence(self) -> TeardownEvidence:
        if self.status is TeardownStatus.REMOVED and not (self.root_absent and self.profile_files_absent):
            raise ValueError("a removed environment requires root and profile absence proof")
        return self


class RoleProfileProbeResult(StrictModel):
    status: CapabilityProbeStatus
    role_isolation: RoleIsolationStatus
    profile_bundle_digest: MetadataDigest
    process_evidence: ProcessEvidenceKind
    readback_status: CapabilityReadbackStatus
    teardown: TeardownEvidence

    @model_validator(mode="after")
    def supported_requires_effective_proof(self) -> RoleProfileProbeResult:
        if self.status is CapabilityProbeStatus.SUPPORTED:
            if self.role_isolation is not RoleIsolationStatus.PROVEN:
                raise ValueError("supported result requires proven role isolation")
            if self.readback_status is not CapabilityReadbackStatus.EFFECTIVE:
                raise ValueError("supported result requires effective readback")
        if self.status is CapabilityProbeStatus.INSTALL_BLOCKED and self.role_isolation is RoleIsolationStatus.PROVEN:
            raise ValueError("blocked result cannot claim proven role isolation")
        return self
