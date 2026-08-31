"""Strict, effect-free contracts for project-scoped Johnny activation.

This module deliberately stops at planning.  It does not read or write a target
document, inspect a host, or claim that a host gate is enforced.  The adapters
and evidence-qualified host classification belong to later tickets.
"""

from __future__ import annotations

import re
from enum import Enum
from hashlib import sha256
from typing import Annotated, Literal, Self, TypeAlias, Union

from pydantic import ConfigDict, Field, ValidationError, field_validator, model_validator

from .contracts import RouterModel


_METADATA_IDENTIFIER_PATTERN = r"^[a-z][a-z0-9-]{2,127}$"
_PLUGIN_IDENTIFIER_PATTERN = r"^[a-z0-9][a-z0-9-]{0,63}$"
_SKILL_PATTERN = r"^[a-z0-9][a-z0-9-]{0,63}:[a-z0-9][a-z0-9-]{0,63}$"
_VERSION_PATTERN = r"^[0-9]+(?:\.[0-9]+){2}(?:-[a-z0-9.-]+)?$"
_DIGEST_PATTERN = r"^[0-9a-f]{64}$"
_FIELD_IDENTIFIER_PATTERN = r"^[a-z][a-z0-9_]{0,63}$"

CanonicalRepositoryId: TypeAlias = Annotated[
    str,
    Field(pattern=_METADATA_IDENTIFIER_PATTERN),
]
TargetDocumentId: TypeAlias = Annotated[
    str,
    Field(pattern=_METADATA_IDENTIFIER_PATTERN),
]
PluginId: TypeAlias = Annotated[str, Field(pattern=_PLUGIN_IDENTIFIER_PATTERN)]
PluginVersion: TypeAlias = Annotated[str, Field(pattern=_VERSION_PATTERN)]
TakeoverSkillId: TypeAlias = Annotated[str, Field(pattern=_SKILL_PATTERN)]
Sha256Digest: TypeAlias = Annotated[str, Field(pattern=_DIGEST_PATTERN)]
BoundedFieldIdentifier: TypeAlias = Annotated[
    str,
    Field(pattern=_FIELD_IDENTIFIER_PATTERN),
]


class _AdoptionModel(RouterModel):
    """RouterModel with no whitespace normalization at this boundary."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=False,
        revalidate_instances="always",
    )


class SupportedHost(str, Enum):
    """Host surfaces that have a distinct project instruction document."""

    CODEX = "CODEX"
    CLAUDE_CODE = "CLAUDE_CODE"


class HostInstructionKind(str, Enum):
    """The only instruction documents supported by the activation planner."""

    CODEX_AGENTS = "CODEX_AGENTS"
    CLAUDE_PROJECT_INSTRUCTION = "CLAUDE_PROJECT_INSTRUCTION"


class ActivationState(str, Enum):
    """Finite adoption state used by host adapters and qualification."""

    ACTIVE = "ACTIVE"
    ABSENT = "ABSENT"
    STALE = "STALE"
    HOST_SURFACE_UNAVAILABLE = "HOST_SURFACE_UNAVAILABLE"


class ActivationAction(str, Enum):
    """The finite plan action for one managed activation block."""

    CREATE_BLOCK = "CREATE_BLOCK"
    UPDATE_BLOCK = "UPDATE_BLOCK"
    NO_CHANGE = "NO_CHANGE"


class HostBehaviorGateState(str, Enum):
    """Host interception strength; instruction text alone is not enforcement."""

    HOST_GATE_ENFORCED = "HOST_GATE_ENFORCED"
    INSTRUCTION_ONLY = "INSTRUCTION_ONLY"
    UNAVAILABLE = "UNAVAILABLE"


class ActivationRefusalReason(str, Enum):
    """Finite, sanitized reasons why activation planning refuses a request."""

    STALE_PRESTATE = "STALE_PRESTATE"
    HOST_KIND_MISMATCH = "HOST_KIND_MISMATCH"
    BLOCK_DUPLICATED = "BLOCK_DUPLICATED"
    BLOCK_MALFORMED = "BLOCK_MALFORMED"
    INPUT_INVALID = "INPUT_INVALID"


# The aliases keep the domain vocabulary discoverable without creating a second
# enum or a competing contract family.
ProjectActivationRefusalReason: TypeAlias = ActivationRefusalReason
HostGateState: TypeAlias = HostBehaviorGateState


class HostBehaviorGateClassification(_AdoptionModel):
    """A finite host-gate classification supplied by a qualified adapter.

    This value is intentionally not accepted by the activation planner.  A
    caller may construct the finite value for a later evidence boundary, but
    this module never infers it from instructions, manifests, or plan output.
    """

    host: SupportedHost
    state: HostBehaviorGateState


class ProjectActivationRequest(_AdoptionModel):
    """All ephemeral input required to plan one project activation."""

    request_ref: Annotated[str, Field(pattern=_METADATA_IDENTIFIER_PATTERN)]
    repository_id: CanonicalRepositoryId
    host: SupportedHost
    instruction_kind: HostInstructionKind
    target_document_id: TargetDocumentId
    expected_current_digest: Sha256Digest
    current_document_text: str
    installed_plugin_id: PluginId
    installed_plugin_version: PluginVersion
    takeover_skill_id: TakeoverSkillId

    @field_validator("current_document_text")
    @classmethod
    def current_document_is_utf8_encodable(cls, value: str) -> str:
        """Reject text that cannot be represented by the digest byte contract."""

        try:
            value.encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError("current document text must be UTF-8 encodable") from error
        return value


class _BlockPlanBase(_AdoptionModel):
    """Shared exact digest fields for a replacing plan."""

    expected_current_digest: Sha256Digest
    expected_post_digest: Sha256Digest
    proposed_text: str = Field(min_length=1)

    @property
    def expected_pre_digest(self) -> Sha256Digest:
        """Read-only wording alias for the compare-and-swap precondition."""

        return self.expected_current_digest

    @property
    def proposed_target_text(self) -> str:
        """Read-only wording alias for the complete proposed document text."""

        return self.proposed_text

    @model_validator(mode="after")
    def post_digest_matches_text(self) -> Self:
        if _document_digest(self.proposed_text) != self.expected_post_digest:
            raise ValueError("activation proposed text must match its expected post-digest")
        if self.proposed_text == "":
            raise ValueError("activation proposed text cannot be empty")
        return self


class CreateBlockPlan(_BlockPlanBase):
    """Plan for adding the canonical block to a document without one."""

    action: Literal["CREATE_BLOCK"] = "CREATE_BLOCK"


class UpdateBlockPlan(_BlockPlanBase):
    """Plan for replacing exactly one existing canonical-marker block."""

    action: Literal["UPDATE_BLOCK"] = "UPDATE_BLOCK"


class NoChangePlan(_AdoptionModel):
    """Verified current content already carries the requested activation."""

    action: Literal["NO_CHANGE"] = "NO_CHANGE"
    verified_existing_digest: Sha256Digest

    @property
    def verified_digest(self) -> Sha256Digest:
        """Read-only short spelling for the verified current document digest."""

        return self.verified_existing_digest


ProjectActivationPlan: TypeAlias = Annotated[
    Union[CreateBlockPlan, UpdateBlockPlan, NoChangePlan],
    Field(discriminator="action"),
]


class ProjectActivationPlannedResult(_AdoptionModel):
    """Tagged success envelope containing exactly one action-specific plan."""

    status: Literal["PLANNED"] = "PLANNED"
    request_ref: Annotated[str, Field(pattern=_METADATA_IDENTIFIER_PATTERN)]
    plan: ProjectActivationPlan

    @property
    def action(self) -> ActivationAction:
        """Expose the finite action without duplicating it in the envelope."""

        return ActivationAction(self.plan.action)


class ProjectActivationRefusedResult(_AdoptionModel):
    """Tagged refusal envelope with metadata-only bounded failure details."""

    status: Literal["REFUSED"] = "REFUSED"
    request_ref: Annotated[str, Field(pattern=_METADATA_IDENTIFIER_PATTERN)]
    reason: ActivationRefusalReason
    field_identifier: BoundedFieldIdentifier

    @property
    def field_id(self) -> BoundedFieldIdentifier:
        """Compatibility spelling for the bounded field identifier."""

        return self.field_identifier

    @property
    def refusal_reason(self) -> ActivationRefusalReason:
        """Read-only wording alias for the finite refusal reason."""

        return self.reason


ProjectActivationResult: TypeAlias = Annotated[
    Union[ProjectActivationPlannedResult, ProjectActivationRefusedResult],
    Field(discriminator="status"),
]


# Version 1 is intentionally fixed and small.  Only the three bounded identity
# values are interpolated; governance/reference bodies never enter the block.
ACTIVATION_BEGIN_MARKER = "<!-- johnny-ai-skill:project-adoption:v1:begin -->"
ACTIVATION_END_MARKER = "<!-- johnny-ai-skill:project-adoption:v1:end -->"
ACTIVATION_BLOCK_VERSION = "v1"
_MARKER_FINGERPRINT = "johnny-ai-skill:project-adoption:v1:"
_PROJECT_MARKER_FINGERPRINT = "johnny-ai-skill:project-adoption:"
_PROJECT_MARKER_COMMENT_RE = re.compile(
    rf"<!--[^\r\n]*{re.escape(_PROJECT_MARKER_FINGERPRINT)}[^\r\n]*(?:-->|(?=\r?$))",
    re.MULTILINE,
)
_CANONICAL_BLOCK_RE = re.compile(
    rf"{re.escape(ACTIVATION_BEGIN_MARKER)}\n"
    rf"For software-change work in this repository, load and follow the installed\n"
    rf"`(?P<skill_id>{_SKILL_PATTERN[1:-1]})` skill from plugin "
    rf"`(?P<plugin_id>{_PLUGIN_IDENTIFIER_PATTERN[1:-1]})` version "
    rf"`(?P<plugin_version>{_VERSION_PATTERN[1:-1]})` as the entry route\.\n"
    rf"Load only the stage/reference it routes\. If that installed identity is absent or stale,\n"
    rf"stop before governed mutation and report the mismatch; do not copy plugin governance here\.\n"
    rf"{re.escape(ACTIVATION_END_MARKER)}"
)


def _document_digest(content: str) -> str:
    """Hash exact UTF-8 document bytes; line endings are never normalized."""

    return sha256(content.encode("utf-8")).hexdigest()


def _canonical_block(request: ProjectActivationRequest, newline: str) -> str:
    """Build only the fixed v1 block from validated bounded identities."""

    block = (
        f"{ACTIVATION_BEGIN_MARKER}\n"
        "For software-change work in this repository, load and follow the installed\n"
        f"`{request.takeover_skill_id}` skill from plugin `{request.installed_plugin_id}` "
        f"version `{request.installed_plugin_version}` as the entry route.\n"
        "Load only the stage/reference it routes. If that installed identity is absent or stale,\n"
        "stop before governed mutation and report the mismatch; do not copy plugin governance here.\n"
        f"{ACTIVATION_END_MARKER}"
    )
    return block.replace("\n", newline)


def _newline_after(content: str, position: int) -> str | None:
    """Return one exact newline sequence beginning at *position*, if present."""

    if content.startswith("\r\n", position):
        return "\r\n"
    if content.startswith("\n", position):
        return "\n"
    if content.startswith("\r", position):
        return "\r"
    return None


def _document_newline(content: str) -> str:
    """Choose the newline convention nearest the insertion boundary."""

    last_newline: str | None = None
    position = 0
    while position < len(content):
        if content.startswith("\r\n", position):
            last_newline = "\r\n"
            position += 2
        elif content[position] == "\r":
            last_newline = "\r"
            position += 1
        elif content[position] == "\n":
            last_newline = "\n"
            position += 1
        else:
            position += 1
    return "\n" if last_newline is None else last_newline


def _standalone_begin(content: str, position: int) -> bool:
    """Require a begin marker to occupy a complete line."""

    before_is_line_start = position == 0 or content[position - 1] in "\r\n"
    after = position + len(ACTIVATION_BEGIN_MARKER)
    return before_is_line_start and _newline_after(content, after) is not None


def _standalone_end(content: str, position: int) -> bool:
    """Require an end marker to occupy a complete line."""

    before_is_line_start = position == 0 or content[position - 1] in "\r\n"
    after = position + len(ACTIVATION_END_MARKER)
    return before_is_line_start and (after == len(content) or content[after] in "\r\n")


def _normalize_newlines(content: str) -> str:
    """Normalize only a bounded candidate block for grammar matching."""

    return content.replace("\r\n", "\n").replace("\r", "\n")


def _block_newline_style(content: str) -> str | None:
    """Return one homogeneous newline style, rejecting mixed block grammar."""

    if "\r\n" in content:
        remainder = content.replace("\r\n", "")
        return "\r\n" if "\r" not in remainder and "\n" not in remainder else None
    if "\r" in content:
        return "\r" if "\n" not in content else None
    return "\n" if "\n" in content else None


def _contains_partial_marker(content: str) -> bool:
    """Reject marker-shaped fragments instead of allowing partial activation."""

    project_marker = _PROJECT_MARKER_COMMENT_RE.search(content)
    if project_marker is not None and project_marker.group(0) not in (
        ACTIVATION_BEGIN_MARKER,
        ACTIVATION_END_MARKER,
    ):
        return True
    fingerprint_position = content.find(_MARKER_FINGERPRINT)
    if fingerprint_position < 0:
        return False
    begin_count = content.count(ACTIVATION_BEGIN_MARKER)
    end_count = content.count(ACTIVATION_END_MARKER)
    return begin_count + end_count == 0 or not (
        _MARKER_FINGERPRINT in ACTIVATION_BEGIN_MARKER
        and _MARKER_FINGERPRINT in ACTIVATION_END_MARKER
        and content.count(_MARKER_FINGERPRINT) == begin_count + end_count
    )


def _refusal(
    request_ref: str,
    reason: ActivationRefusalReason,
    field_identifier: str,
) -> ProjectActivationRefusedResult:
    """Create the only refusal envelope; it contains no proposed target text."""

    return ProjectActivationRefusedResult(
        request_ref=request_ref,
        reason=reason,
        field_identifier=field_identifier,
    )


def _create_plan(
    request: ProjectActivationRequest,
    block: str,
) -> ProjectActivationPlannedResult:
    """Compose a create plan at the document's end without altering old bytes."""

    document = request.current_document_text
    if not document:
        proposed = block
    elif document.endswith(("\r", "\n")):
        proposed = document + block
    else:
        proposed = document + _document_newline(document) + block
    return ProjectActivationPlannedResult(
        request_ref=request.request_ref,
        plan=CreateBlockPlan(
            expected_current_digest=request.expected_current_digest,
            expected_post_digest=_document_digest(proposed),
            proposed_text=proposed,
        ),
    )


def _existing_block_bounds(document: str) -> tuple[int, int] | ActivationRefusalReason:
    """Resolve exactly one well-formed marker block or return its finite refusal."""

    begin_count = document.count(ACTIVATION_BEGIN_MARKER)
    end_count = document.count(ACTIVATION_END_MARKER)
    if begin_count > 1 or end_count > 1:
        return ActivationRefusalReason.BLOCK_DUPLICATED
    if _contains_partial_marker(document):
        return ActivationRefusalReason.BLOCK_MALFORMED
    if begin_count == 0 and end_count == 0:
        return (-1, -1)
    if begin_count != 1 or end_count != 1:
        return ActivationRefusalReason.BLOCK_MALFORMED

    begin = document.find(ACTIVATION_BEGIN_MARKER)
    end = document.find(ACTIVATION_END_MARKER)
    if begin < 0 or end < 0 or end < begin:
        return ActivationRefusalReason.BLOCK_MALFORMED
    if not _standalone_begin(document, begin) or not _standalone_end(document, end):
        return ActivationRefusalReason.BLOCK_MALFORMED
    end_after = end + len(ACTIVATION_END_MARKER)
    block = document[begin:end_after]
    if _block_newline_style(block) is None:
        return ActivationRefusalReason.BLOCK_MALFORMED
    normalized = _normalize_newlines(block)
    if _CANONICAL_BLOCK_RE.fullmatch(normalized) is None:
        return ActivationRefusalReason.BLOCK_MALFORMED
    return begin, end_after


def plan_project_activation(request: ProjectActivationRequest) -> ProjectActivationResult:
    """Plan one deterministic activation-block create, update, or no-op.

    The current digest is checked before any marker interpretation.  All
    returned target text is ephemeral and remains inside the result only.
    """

    # The public signature is strict; this guard keeps a bypass-constructed or
    # foreign object from becoming a successful plan.
    if type(request) is not ProjectActivationRequest:
        return _refusal("invalid-request", ActivationRefusalReason.INPUT_INVALID, "request")
    try:
        request = ProjectActivationRequest.model_validate(request)
    except ValidationError:
        return _refusal("invalid-request", ActivationRefusalReason.INPUT_INVALID, "request")

    actual_digest = _document_digest(request.current_document_text)
    if actual_digest != request.expected_current_digest:
        return _refusal(request.request_ref, ActivationRefusalReason.STALE_PRESTATE, "expected_current_digest")

    if (
        request.host is SupportedHost.CODEX
        and request.instruction_kind is not HostInstructionKind.CODEX_AGENTS
    ) or (
        request.host is SupportedHost.CLAUDE_CODE
        and request.instruction_kind is not HostInstructionKind.CLAUDE_PROJECT_INSTRUCTION
    ):
        return _refusal(request.request_ref, ActivationRefusalReason.HOST_KIND_MISMATCH, "instruction_kind")

    skill_namespace = request.takeover_skill_id.split(":", maxsplit=1)[0]
    if skill_namespace != request.installed_plugin_id:
        return _refusal(
            request.request_ref,
            ActivationRefusalReason.INPUT_INVALID,
            "installed_plugin_id",
        )

    bounds = _existing_block_bounds(request.current_document_text)
    if isinstance(bounds, ActivationRefusalReason):
        return _refusal(request.request_ref, bounds, "current_document_text")
    block_start, block_end = bounds
    newline = _document_newline(request.current_document_text)
    if block_start < 0:
        return _create_plan(request, _canonical_block(request, newline))

    existing = request.current_document_text[block_start:block_end]
    block_newline = "\r\n" if "\r\n" in existing else "\r" if "\r" in existing else "\n"
    replacement = _canonical_block(request, block_newline)
    if existing == replacement:
        return ProjectActivationPlannedResult(
            request_ref=request.request_ref,
            plan=NoChangePlan(verified_existing_digest=actual_digest),
        )
    proposed = (
        request.current_document_text[:block_start]
        + replacement
        + request.current_document_text[block_end:]
    )
    return ProjectActivationPlannedResult(
        request_ref=request.request_ref,
        plan=UpdateBlockPlan(
            expected_current_digest=request.expected_current_digest,
            expected_post_digest=_document_digest(proposed),
            proposed_text=proposed,
        ),
    )


__all__ = [
    "ACTIVATION_BEGIN_MARKER",
    "ACTIVATION_BLOCK_VERSION",
    "ACTIVATION_END_MARKER",
    "ActivationAction",
    "ActivationRefusalReason",
    "ActivationState",
    "BoundedFieldIdentifier",
    "CanonicalRepositoryId",
    "CreateBlockPlan",
    "HostBehaviorGateClassification",
    "HostBehaviorGateState",
    "HostGateState",
    "HostInstructionKind",
    "NoChangePlan",
    "PluginId",
    "PluginVersion",
    "ProjectActivationPlan",
    "ProjectActivationPlannedResult",
    "ProjectActivationRefusalReason",
    "ProjectActivationRefusedResult",
    "ProjectActivationRequest",
    "ProjectActivationResult",
    "Sha256Digest",
    "SupportedHost",
    "TakeoverSkillId",
    "TargetDocumentId",
    "UpdateBlockPlan",
    "plan_project_activation",
]
