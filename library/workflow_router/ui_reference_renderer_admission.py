"""Strict, effect-free admission of renderer-qualified UI reference evidence."""

from __future__ import annotations

from enum import Enum
import unicodedata
from typing import Annotated, Literal, Self, TypeAlias, Union

from pydantic import AfterValidator, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from .contracts import RouterModel
from .ui_codesign_contracts import ContentDigest, ReferenceRendererState


_SHA256_PATTERN = r"^[0-9a-f]{64}$"


def _identifier_uses_allowed_categories(value: str) -> str:
    if not all(unicodedata.category(character)[0] in ("L", "N") for character in value):
        raise ValueError("renderer identifiers require only Unicode letters and numbers")
    return value


RendererIdentifier: TypeAlias = Annotated[
    str,
    Field(min_length=3, max_length=128),
    AfterValidator(_identifier_uses_allowed_categories),
]
Sha256Digest: TypeAlias = Annotated[str, Field(pattern=_SHA256_PATTERN)]


class _RendererAdmissionModel(RouterModel):
    """Immutable strict metadata that cannot carry renderer or provider payloads."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=False,
        revalidate_instances="always",
    )

    @field_validator("*")
    @classmethod
    def metadata_is_bounded(cls, value: object) -> object:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError("renderer admission metadata must not be blank")
            if value != value.strip():
                raise ValueError("renderer admission metadata must not have edge whitespace")
            if any(ord(character) < 0x20 or 0x7F <= ord(character) <= 0x9F for character in value):
                raise ValueError("renderer admission metadata must not contain control characters")
        return value


class RendererCapabilityState(str, Enum):
    AVAILABLE_AUTHORIZED = "AVAILABLE_AUTHORIZED"
    AVAILABLE_NOT_AUTHORIZED = "AVAILABLE_NOT_AUTHORIZED"
    UNAVAILABLE = "UNAVAILABLE"
    DECLINED = "DECLINED"


class RendererTarget(str, Enum):
    DOM = "DOM"
    NATIVE_ENGINE = "NATIVE_ENGINE"
    NATIVE_MOBILE = "NATIVE_MOBILE"
    TERMINAL = "TERMINAL"
    ANY = "ANY"


class ReferenceEvidenceBinding(_RendererAdmissionModel):
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest


class RenderedReferenceEvidence(_RendererAdmissionModel):
    kind: Literal["RENDERED_AVAILABLE"] = "RENDERED_AVAILABLE"
    binding: ReferenceEvidenceBinding
    desktop_screenshot_ref: RendererIdentifier
    mobile_screenshot_ref: RendererIdentifier
    desktop_digest: Sha256Digest
    mobile_digest: Sha256Digest
    renderer_observation_ref: RendererIdentifier


class ArtifactReferenceEvidence(_RendererAdmissionModel):
    kind: Literal["ARTIFACT_ONLY"] = "ARTIFACT_ONLY"
    binding: ReferenceEvidenceBinding
    desktop_artifact_ref: RendererIdentifier
    mobile_artifact_ref: RendererIdentifier
    artifact_set_digest: Sha256Digest
    owner_manual_open_acknowledgement: Literal[True]

    @field_validator("owner_manual_open_acknowledgement", mode="before")
    @classmethod
    def acknowledgement_is_strict_true(cls, value: object) -> object:
        if type(value) is not bool or value is not True:
            raise ValueError("owner manual open acknowledgement must be the literal true")
        return value


class UnavailableReferenceEvidence(_RendererAdmissionModel):
    kind: Literal["UNAVAILABLE"] = "UNAVAILABLE"
    binding: ReferenceEvidenceBinding


ReferenceRendererEvidence: TypeAlias = Annotated[
    Union[
        RenderedReferenceEvidence,
        ArtifactReferenceEvidence,
        UnavailableReferenceEvidence,
    ],
    Field(discriminator="kind"),
]


class ReferenceRendererAdmissionRequest(_RendererAdmissionModel):
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest
    capability_state: RendererCapabilityState
    renderer_target: RendererTarget
    actual_target: RendererTarget
    requested_renderer_state: ReferenceRendererState
    evidence: ReferenceRendererEvidence

    @model_validator(mode="after")
    def actual_target_is_finite(self) -> Self:
        if self.actual_target is RendererTarget.ANY:
            raise ValueError("actual renderer target must be finite")
        return self


class RendererWaitReason(str, Enum):
    DESIGN_CAPABILITY_AUTHORITY_REQUIRED = "DESIGN_CAPABILITY_AUTHORITY_REQUIRED"
    UI_REFERENCE_RENDERER_REQUIRED = "UI_REFERENCE_RENDERER_REQUIRED"


class RendererRefusalReason(str, Enum):
    TARGET_MISMATCH = "TARGET_MISMATCH"
    STATE_EVIDENCE_MISMATCH = "STATE_EVIDENCE_MISMATCH"
    CONTENT_BINDING_MISMATCH = "CONTENT_BINDING_MISMATCH"
    DUPLICATE_EVIDENCE = "DUPLICATE_EVIDENCE"


class AdmittedRenderedDecision(_RendererAdmissionModel):
    kind: Literal["ADMITTED_RENDERED"] = "ADMITTED_RENDERED"
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest
    renderer_state: Literal[ReferenceRendererState.RENDERED_AVAILABLE] = ReferenceRendererState.RENDERED_AVAILABLE
    evidence: RenderedReferenceEvidence


class AdmittedArtifactDecision(_RendererAdmissionModel):
    kind: Literal["ADMITTED_ARTIFACT"] = "ADMITTED_ARTIFACT"
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest
    renderer_state: Literal[ReferenceRendererState.ARTIFACT_ONLY] = ReferenceRendererState.ARTIFACT_ONLY
    evidence: ArtifactReferenceEvidence


class RendererWaitDecision(_RendererAdmissionModel):
    kind: Literal["WAIT"] = "WAIT"
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest
    reason: RendererWaitReason


class RendererRefusedDecision(_RendererAdmissionModel):
    kind: Literal["REFUSED"] = "REFUSED"
    request_ref: RendererIdentifier
    brief_id: RendererIdentifier
    approved_content_digest: ContentDigest
    reason: RendererRefusalReason


ReferenceRendererAdmissionDecision: TypeAlias = Annotated[
    Union[
        AdmittedRenderedDecision,
        AdmittedArtifactDecision,
        RendererWaitDecision,
        RendererRefusedDecision,
    ],
    Field(discriminator="kind"),
]


_REQUEST_ADAPTER: TypeAdapter[ReferenceRendererAdmissionRequest] = TypeAdapter(
    ReferenceRendererAdmissionRequest
)


def _wait(
    request: ReferenceRendererAdmissionRequest,
    reason: RendererWaitReason,
) -> RendererWaitDecision:
    return RendererWaitDecision(
        request_ref=request.request_ref,
        brief_id=request.brief_id,
        approved_content_digest=request.approved_content_digest,
        reason=reason,
    )


def _refuse(
    request: ReferenceRendererAdmissionRequest,
    reason: RendererRefusalReason,
) -> RendererRefusedDecision:
    return RendererRefusedDecision(
        request_ref=request.request_ref,
        brief_id=request.brief_id,
        approved_content_digest=request.approved_content_digest,
        reason=reason,
    )


def _evidence_is_duplicate(evidence: ReferenceRendererEvidence) -> bool:
    if isinstance(evidence, RenderedReferenceEvidence):
        return (
            len(
                {
                    evidence.desktop_screenshot_ref,
                    evidence.mobile_screenshot_ref,
                    evidence.renderer_observation_ref,
                }
            )
            != 3
            or len({evidence.desktop_digest, evidence.mobile_digest}) != 2
        )
    if isinstance(evidence, ArtifactReferenceEvidence):
        return len({evidence.desktop_artifact_ref, evidence.mobile_artifact_ref}) != 2
    return False


def _target_matches(request: ReferenceRendererAdmissionRequest) -> bool:
    return request.renderer_target is RendererTarget.ANY or request.renderer_target is request.actual_target


def _evidence_binding_matches_request(request: ReferenceRendererAdmissionRequest) -> bool:
    binding = request.evidence.binding
    return (
        binding.request_ref == request.request_ref
        and binding.brief_id == request.brief_id
        and binding.approved_content_digest == request.approved_content_digest
    )


def _evidence_matches_requested_state(request: ReferenceRendererAdmissionRequest) -> bool:
    if request.requested_renderer_state is ReferenceRendererState.RENDERED_AVAILABLE:
        return isinstance(request.evidence, RenderedReferenceEvidence)
    if request.requested_renderer_state is ReferenceRendererState.ARTIFACT_ONLY:
        return isinstance(request.evidence, ArtifactReferenceEvidence)
    return isinstance(request.evidence, UnavailableReferenceEvidence)


def admit_reference_renderer(
    request: ReferenceRendererAdmissionRequest,
) -> ReferenceRendererAdmissionDecision:
    """Admit only evidence supported by the declared capability and target."""

    trusted_request = _REQUEST_ADAPTER.validate_python(request)
    if trusted_request.capability_state is RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED:
        return _wait(trusted_request, RendererWaitReason.DESIGN_CAPABILITY_AUTHORITY_REQUIRED)
    if not _evidence_binding_matches_request(trusted_request):
        return _refuse(trusted_request, RendererRefusalReason.CONTENT_BINDING_MISMATCH)
    if _evidence_is_duplicate(trusted_request.evidence):
        return _refuse(trusted_request, RendererRefusalReason.DUPLICATE_EVIDENCE)
    if isinstance(trusted_request.evidence, (RenderedReferenceEvidence, ArtifactReferenceEvidence)):
        if not _target_matches(trusted_request):
            return _refuse(trusted_request, RendererRefusalReason.TARGET_MISMATCH)

    if trusted_request.requested_renderer_state is ReferenceRendererState.UNAVAILABLE:
        if isinstance(trusted_request.evidence, UnavailableReferenceEvidence):
            if trusted_request.capability_state in (
                RendererCapabilityState.UNAVAILABLE,
                RendererCapabilityState.DECLINED,
            ):
                return _wait(trusted_request, RendererWaitReason.UI_REFERENCE_RENDERER_REQUIRED)
            return _refuse(trusted_request, RendererRefusalReason.STATE_EVIDENCE_MISMATCH)
        return _refuse(trusted_request, RendererRefusalReason.STATE_EVIDENCE_MISMATCH)

    if not _evidence_matches_requested_state(trusted_request):
        if (
            trusted_request.requested_renderer_state is ReferenceRendererState.ARTIFACT_ONLY
            and isinstance(trusted_request.evidence, UnavailableReferenceEvidence)
            and trusted_request.capability_state
            in (RendererCapabilityState.UNAVAILABLE, RendererCapabilityState.DECLINED)
        ):
            return _wait(trusted_request, RendererWaitReason.UI_REFERENCE_RENDERER_REQUIRED)
        return _refuse(trusted_request, RendererRefusalReason.STATE_EVIDENCE_MISMATCH)

    if isinstance(trusted_request.evidence, RenderedReferenceEvidence):
        if trusted_request.capability_state is not RendererCapabilityState.AVAILABLE_AUTHORIZED:
            return _refuse(trusted_request, RendererRefusalReason.STATE_EVIDENCE_MISMATCH)
        return AdmittedRenderedDecision(
            request_ref=trusted_request.request_ref,
            brief_id=trusted_request.brief_id,
            approved_content_digest=trusted_request.approved_content_digest,
            evidence=trusted_request.evidence,
        )

    if isinstance(trusted_request.evidence, ArtifactReferenceEvidence):
        if trusted_request.capability_state is RendererCapabilityState.AVAILABLE_AUTHORIZED:
            return _refuse(trusted_request, RendererRefusalReason.STATE_EVIDENCE_MISMATCH)
        return AdmittedArtifactDecision(
            request_ref=trusted_request.request_ref,
            brief_id=trusted_request.brief_id,
            approved_content_digest=trusted_request.approved_content_digest,
            evidence=trusted_request.evidence,
        )

    return _wait(trusted_request, RendererWaitReason.UI_REFERENCE_RENDERER_REQUIRED)


__all__ = [
    "AdmittedArtifactDecision",
    "AdmittedRenderedDecision",
    "ArtifactReferenceEvidence",
    "ReferenceEvidenceBinding",
    "ReferenceRendererAdmissionDecision",
    "ReferenceRendererAdmissionRequest",
    "ReferenceRendererEvidence",
    "ReferenceRendererState",
    "RenderedReferenceEvidence",
    "RendererCapabilityState",
    "RendererIdentifier",
    "RendererRefusalReason",
    "RendererRefusedDecision",
    "RendererTarget",
    "RendererWaitDecision",
    "RendererWaitReason",
    "Sha256Digest",
    "UnavailableReferenceEvidence",
    "admit_reference_renderer",
]
