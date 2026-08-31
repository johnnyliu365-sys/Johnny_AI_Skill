"""Strict, effect-free contracts for the designerless UI co-design lifecycle."""

from __future__ import annotations

import re
from enum import Enum
from hashlib import sha256
from typing import Annotated, Literal, Self, TypeAlias, Union

from pydantic import AliasChoices, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from .contracts import RouterModel


_ID_PATTERN = r"^[a-z][a-z0-9-]{2,127}$"
_DIGEST_PATTERN = r"^(?:[0-9a-f]{64}|sha256_[0-9a-f]{64})$"
_TEXT_MAX_LENGTH = 512
_DIRECTION_TEXT_MAX_LENGTH = 256
_BOUNDARY_TEXT_MAX_LENGTH = 192
_UNSAFE_TEXT_MARKERS = ("://", "api_key", "password=", "secret=", "<script", "prompt:")


UIIdentifier: TypeAlias = Annotated[str, Field(pattern=_ID_PATTERN)]
ContentDigest: TypeAlias = Annotated[str, Field(pattern=_DIGEST_PATTERN)]
BoundedText: TypeAlias = Annotated[str, Field(min_length=1, max_length=_TEXT_MAX_LENGTH)]
DirectionText: TypeAlias = Annotated[
    str,
    Field(min_length=1, max_length=_DIRECTION_TEXT_MAX_LENGTH),
]
BoundaryText: TypeAlias = Annotated[
    str,
    Field(min_length=1, max_length=_BOUNDARY_TEXT_MAX_LENGTH),
]


class _UICodesignModel(RouterModel):
    """Immutable strict model that preserves authored text exactly."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=False,
        revalidate_instances="always",
        populate_by_name=True,
    )

    @field_validator("*")
    @classmethod
    def text_is_nonblank_and_safe(cls, value: object) -> object:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError("UI co-design text must not be blank")
            lowered = value.casefold()
            if any(marker in lowered for marker in _UNSAFE_TEXT_MARKERS):
                raise ValueError("UI co-design text must remain bounded metadata or authored prose")
        return value


class UICodesignState(str, Enum):
    BRIEF_DRAFT = "BRIEF_DRAFT"
    BRIEF_APPROVED = "BRIEF_APPROVED"
    DIRECTIONS_READY = "DIRECTIONS_READY"
    OWNER_SELECTION_REQUIRED = "OWNER_SELECTION_REQUIRED"
    REGIME_CANDIDATE_SELECTED = "REGIME_CANDIDATE_SELECTED"
    REGIME_SEALED = "REGIME_SEALED"
    FEATURE_CONTRACT_READY = "FEATURE_CONTRACT_READY"
    IMPLEMENTATION_READY = "IMPLEMENTATION_READY"
    VISUAL_REVIEW_REQUIRED = "VISUAL_REVIEW_REQUIRED"
    OWNER_ACCEPTANCE_REQUIRED = "OWNER_ACCEPTANCE_REQUIRED"
    COMPLETE = "COMPLETE"


class DesignSourceKind(str, Enum):
    FIGMA = "FIGMA"
    SCREENSHOT = "SCREENSHOT"
    DESIGN_BRIEF = "DESIGN_BRIEF"
    EXISTING_DESIGN_SYSTEM = "EXISTING_DESIGN_SYSTEM"
    NONE = "NONE"


class DesignCapabilityState(str, Enum):
    AVAILABLE_AUTHORIZED = "AVAILABLE_AUTHORIZED"
    AVAILABLE_NOT_AUTHORIZED = "AVAILABLE_NOT_AUTHORIZED"
    UNAVAILABLE = "UNAVAILABLE"
    DECLINED = "DECLINED"


class ReferenceRendererState(str, Enum):
    RENDERED_AVAILABLE = "RENDERED_AVAILABLE"
    ARTIFACT_ONLY = "ARTIFACT_ONLY"
    UNAVAILABLE = "UNAVAILABLE"


class VisualVerificationState(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class VisualFindingSeverity(str, Enum):
    BLOCKING = "BLOCKING"
    MATERIAL = "MATERIAL"
    POLISH = "POLISH"


class UIFeatureState(str, Enum):
    LOADING = "LOADING"
    EMPTY = "EMPTY"
    SUCCESS = "SUCCESS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    PERMISSION_DISABLED = "PERMISSION_DISABLED"


class OfflineDisposition(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ViewportKind(str, Enum):
    MOBILE = "MOBILE"
    DESKTOP = "DESKTOP"


class UICodesignWaitReason(str, Enum):
    OWNER_SELECTION_REQUIRED = "OWNER_SELECTION_REQUIRED"
    UI_REFERENCE_RENDERER_REQUIRED = "UI_REFERENCE_RENDERER_REQUIRED"
    VISUAL_VERIFICATION_REQUIRED = "VISUAL_VERIFICATION_REQUIRED"
    OWNER_ACCEPTANCE_REQUIRED = "OWNER_ACCEPTANCE_REQUIRED"


class UICodesignRefusalReason(str, Enum):
    INVALID_TRANSITION = "INVALID_TRANSITION"
    DISTINCT_DIRECTION_REQUIRED = "DISTINCT_DIRECTION_REQUIRED"
    CONTEXT_SEAL_REQUIRED = "CONTEXT_SEAL_REQUIRED"
    REQUIRED_STATE_MISSING = "REQUIRED_STATE_MISSING"
    EVIDENCE_MISMATCH = "EVIDENCE_MISMATCH"


class UIDesignBrief(_UICodesignModel):
    """Bounded product facts and visual constraints for one co-design loop."""

    brief_id: UIIdentifier
    product: BoundedText
    audience: BoundedText
    job: BoundedText
    brand_personality: BoundedText
    brand_anti_goals: tuple[BoundedText, ...] = Field(min_length=1)
    target_platform: BoundedText
    content_hierarchy: BoundedText
    information_density: BoundedText
    accessibility_baseline: BoundedText
    locale: BoundedText
    content_constraints: BoundedText
    required_states: tuple[UIFeatureState, ...] = Field(min_length=6)
    offline_disposition: OfflineDisposition
    design_source: DesignSourceKind
    reference_ids: tuple[UIIdentifier, ...] = ()
    content_digest: ContentDigest

    @property
    def user_job(self) -> BoundedText:
        return self.job

    @model_validator(mode="after")
    def required_state_set_is_exact(self) -> Self:
        required = tuple(UIFeatureState)
        if len(self.required_states) != len(set(self.required_states)):
            raise ValueError("required UI feature states must be unique")
        if set(self.required_states) != set(required):
            raise ValueError("required UI feature states must cover the finite state set")
        if len(self.reference_ids) != len(set(self.reference_ids)):
            raise ValueError("brief reference IDs must be unique")
        if self.design_source is DesignSourceKind.NONE and self.reference_ids:
            raise ValueError("a NONE design source cannot carry reference IDs")
        return self


class ArtifactDirectionEvidence(_UICodesignModel):
    """Target-owned artifact evidence for renderer-free direction comparison."""

    kind: Literal["ARTIFACT_ONLY"] = "ARTIFACT_ONLY"
    desktop_artifact_ref: UIIdentifier
    mobile_artifact_ref: UIIdentifier
    owner_manual_open_acknowledgement: Literal[True] = Field(
        validation_alias=AliasChoices(
            "owner_manual_open_acknowledgement",
            "owner_manual_open_acknowledged",
        )
    )


class RenderedDirectionEvidence(_UICodesignModel):
    """Renderer-qualified desktop and mobile evidence for one direction."""

    kind: Literal["RENDERED_AVAILABLE"] = "RENDERED_AVAILABLE"
    desktop_evidence_ref: UIIdentifier = Field(
        validation_alias=AliasChoices("desktop_evidence_ref", "desktop_screenshot_ref")
    )
    mobile_evidence_ref: UIIdentifier = Field(
        validation_alias=AliasChoices("mobile_evidence_ref", "mobile_screenshot_ref")
    )


DirectionEvidence: TypeAlias = Annotated[
    Union[ArtifactDirectionEvidence, RenderedDirectionEvidence],
    Field(discriminator="kind"),
]


class VisualDirectionCandidate(_UICodesignModel):
    """One proposed visual direction with evidence matching its renderer tier."""

    candidate_id: UIIdentifier
    rationale: DirectionText
    hierarchy: DirectionText = Field(
        validation_alias=AliasChoices("hierarchy", "information_hierarchy")
    )
    typography: DirectionText
    density: DirectionText
    component_language: DirectionText
    spacing: DirectionText
    semantic_colour: DirectionText = Field(
        validation_alias=AliasChoices("semantic_colour", "semantic_color", "colour")
    )
    motion_character: DirectionText = Field(
        validation_alias=AliasChoices("motion_character", "motion")
    )
    macrostructure: DirectionText
    accessibility_notes: DirectionText
    approved_content_digest: ContentDigest
    evidence: DirectionEvidence

    @property
    def structural_signature(self) -> tuple[str, ...]:
        """Return all direction choices except palette, rationale and identity."""

        return (
            self.hierarchy,
            self.typography,
            self.density,
            self.component_language,
            self.spacing,
            self.motion_character,
            self.macrostructure,
            self.accessibility_notes,
        )

    @property
    def candidate_digest(self) -> ContentDigest:
        """Derive a stable digest from the bounded structural direction contract."""

        payload = "\x1f".join((self.candidate_id, self.approved_content_digest, *self.structural_signature))
        return sha256(payload.encode("utf-8")).hexdigest()


def _direction_evidence_is_valid(
    candidates: tuple[VisualDirectionCandidate, ...],
    renderer_state: ReferenceRendererState,
    approved_content_digest: ContentDigest,
) -> bool:
    if renderer_state is ReferenceRendererState.UNAVAILABLE:
        return False
    if len(candidates) < 2 or len({candidate.candidate_id for candidate in candidates}) != len(candidates):
        return False
    if any(candidate.approved_content_digest != approved_content_digest for candidate in candidates):
        return False
    if renderer_state is ReferenceRendererState.RENDERED_AVAILABLE and any(
        not isinstance(candidate.evidence, RenderedDirectionEvidence) for candidate in candidates
    ):
        return False
    if renderer_state is ReferenceRendererState.ARTIFACT_ONLY and any(
        not isinstance(candidate.evidence, ArtifactDirectionEvidence) for candidate in candidates
    ):
        return False
    signatures = tuple(candidate.structural_signature for candidate in candidates)
    return len(signatures) == len(set(signatures))


class UIRegimeCandidate(_UICodesignModel):
    """Owner-selected candidate awaiting canonical CONTEXT sealing."""

    regime_candidate_id: UIIdentifier
    brief_id: UIIdentifier
    selected_candidate_id: UIIdentifier
    selected_candidate_digest: ContentDigest
    approved_content_digest: ContentDigest
    owner_decision_ref: UIIdentifier


class SealedUIRegimeRef(_UICodesignModel):
    """The exact target-owned CONTEXT identity approved for feature contracts."""

    context_artifact_id: UIIdentifier
    context_revision: UIIdentifier
    context_digest: ContentDigest
    selected_candidate_id: UIIdentifier
    owner_approval_ref: UIIdentifier


UIRegime: TypeAlias = SealedUIRegimeRef


class UIFeatureStateContract(_UICodesignModel):
    """Behavior and copy contract for one required finite feature state."""

    state: UIFeatureState
    behavior: BoundaryText


class ResponsiveBreakpoint(_UICodesignModel):
    """One named responsive viewport contract."""

    breakpoint_id: UIIdentifier
    viewport: ViewportKind
    layout_behavior: BoundaryText = Field(
        validation_alias=AliasChoices("layout_behavior", "behavior")
    )


class AccessibilityContract(_UICodesignModel):
    """Keyboard, focus, semantic, contrast and motion accessibility obligations."""

    keyboard_behavior: BoundaryText
    focus_behavior: BoundaryText
    semantic_roles: tuple[BoundaryText, ...] = Field(min_length=1)
    contrast_requirements: BoundaryText
    reduced_motion_behavior: BoundaryText


class UIImplementationContract(_UICodesignModel):
    """One feature implementation contract consuming an exact sealed regime."""

    contract_id: UIIdentifier
    sealed_regime_ref: SealedUIRegimeRef
    component_boundary: BoundaryText
    inputs: tuple[BoundaryText, ...] = Field(min_length=1)
    outputs: tuple[BoundaryText, ...] = Field(min_length=1)
    feature_states: tuple[UIFeatureStateContract, ...] = Field(min_length=6)
    responsive_breakpoints: tuple[ResponsiveBreakpoint, ...] = Field(min_length=2)
    accessibility: AccessibilityContract
    asset_boundaries: tuple[BoundaryText, ...] = Field(min_length=1)
    interaction_boundaries: tuple[BoundaryText, ...] = Field(min_length=1)
    offline_disposition: OfflineDisposition

    @model_validator(mode="after")
    def contract_covers_required_behavior(self) -> Self:
        state_names = tuple(item.state for item in self.feature_states)
        if len(state_names) != len(set(state_names)):
            raise ValueError("feature state contracts must be unique")
        if set(state_names) != set(UIFeatureState):
            raise ValueError("feature contract must cover every finite UI state")
        viewports = tuple(item.viewport for item in self.responsive_breakpoints)
        if len(viewports) != len(set(viewports)) or set(viewports) != set(ViewportKind):
            raise ValueError("feature contract must cover mobile and desktop breakpoints")
        return self


class VisualEvidenceCell(_UICodesignModel):
    """One actual-output evidence cell at a breakpoint and finite UI state."""

    breakpoint_id: UIIdentifier
    state: UIFeatureState
    screenshot_ref: UIIdentifier
    evidence_digest: ContentDigest


class VisualFinding(_UICodesignModel):
    """A reviewer finding with evidence and bounded prose only."""

    finding_id: UIIdentifier
    severity: VisualFindingSeverity
    dimension: BoundaryText
    description: BoundaryText
    evidence_refs: tuple[UIIdentifier, ...] = Field(min_length=1)


class VisualReviewReport(_UICodesignModel):
    """Actual-output visual evidence and findings, without acceptance authority."""

    report_id: UIIdentifier
    implementation_ref: UIIdentifier = Field(
        validation_alias=AliasChoices("implementation_ref", "implementation_ticket_ref")
    )
    screenshot_refs: tuple[UIIdentifier, ...] = Field(min_length=1)
    breakpoint_state_matrix: tuple[VisualEvidenceCell, ...] = Field(min_length=2)
    findings: tuple[VisualFinding, ...] = ()
    evidence_digests: tuple[ContentDigest, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def evidence_ids_are_unique(self) -> Self:
        if len(self.screenshot_refs) != len(set(self.screenshot_refs)):
            raise ValueError("visual screenshot references must be unique")
        if len(self.evidence_digests) != len(set(self.evidence_digests)):
            raise ValueError("visual evidence digests must be unique")
        screenshot_refs = set(self.screenshot_refs)
        if any(
            cell.screenshot_ref not in screenshot_refs
            for cell in self.breakpoint_state_matrix
        ):
            raise ValueError("visual matrix cells must cite report screenshots")
        if any(
            evidence_ref not in screenshot_refs
            for finding in self.findings
            for evidence_ref in finding.evidence_refs
        ):
            raise ValueError("visual findings must cite report screenshots")
        evidence_digests = set(self.evidence_digests)
        if any(
            cell.evidence_digest not in evidence_digests
            for cell in self.breakpoint_state_matrix
        ):
            raise ValueError("visual matrix cells must cite report evidence digests")
        return self


class _UIBriefSnapshot(_UICodesignModel):
    brief: UIDesignBrief


class UIBriefDraftSnapshot(_UIBriefSnapshot):
    state: Literal[UICodesignState.BRIEF_DRAFT] = UICodesignState.BRIEF_DRAFT


class _UIApprovedSnapshot(_UIBriefSnapshot):
    approved_brief_id: UIIdentifier
    approved_content_digest: ContentDigest

    @model_validator(mode="after")
    def approved_identity_is_exact(self) -> Self:
        if self.approved_brief_id != self.brief.brief_id:
            raise ValueError("approved brief identity must match the brief")
        if self.approved_content_digest != self.brief.content_digest:
            raise ValueError("approved content digest must match the brief")
        return self


class UIBriefApprovedSnapshot(_UIApprovedSnapshot):
    state: Literal[UICodesignState.BRIEF_APPROVED] = UICodesignState.BRIEF_APPROVED


class _UIDirectionsSnapshot(_UIApprovedSnapshot):
    directions: tuple[VisualDirectionCandidate, ...] = Field(min_length=2)
    renderer_state: ReferenceRendererState

    @model_validator(mode="after")
    def directions_are_valid(self) -> Self:
        if not _direction_evidence_is_valid(
            self.directions,
            self.renderer_state,
            self.approved_content_digest,
        ):
            raise ValueError("snapshot directions must be distinct and renderer-qualified")
        return self


class UIDirectionsReadySnapshot(_UIDirectionsSnapshot):
    state: Literal[UICodesignState.DIRECTIONS_READY] = UICodesignState.DIRECTIONS_READY


class UIOwnerSelectionRequiredSnapshot(_UIDirectionsSnapshot):
    state: Literal[UICodesignState.OWNER_SELECTION_REQUIRED] = UICodesignState.OWNER_SELECTION_REQUIRED


class _UIRegimeCandidateSnapshot(_UIDirectionsSnapshot):
    regime_candidate: UIRegimeCandidate

    @model_validator(mode="after")
    def selected_direction_is_exact(self) -> Self:
        if self.regime_candidate.brief_id != self.brief.brief_id:
            raise ValueError("regime candidate must retain the brief identity")
        if self.regime_candidate.approved_content_digest != self.approved_content_digest:
            raise ValueError("regime candidate must retain the approved content")
        selected = next(
            (
                candidate
                for candidate in self.directions
                if candidate.candidate_id == self.regime_candidate.selected_candidate_id
            ),
            None,
        )
        if selected is None or selected.candidate_digest != self.regime_candidate.selected_candidate_digest:
            raise ValueError("regime candidate must retain the selected direction digest")
        return self


class UIRegimeCandidateSelectedSnapshot(_UIRegimeCandidateSnapshot):
    state: Literal[UICodesignState.REGIME_CANDIDATE_SELECTED] = UICodesignState.REGIME_CANDIDATE_SELECTED


class _UISealedSnapshot(_UIRegimeCandidateSnapshot):
    sealed_regime: SealedUIRegimeRef

    @model_validator(mode="after")
    def sealed_regime_is_exact(self) -> Self:
        if self.sealed_regime.selected_candidate_id != self.regime_candidate.selected_candidate_id:
            raise ValueError("sealed regime must retain the selected candidate")
        return self


class UIRegimeSealedSnapshot(_UISealedSnapshot):
    state: Literal[UICodesignState.REGIME_SEALED] = UICodesignState.REGIME_SEALED


class _UIFeatureContractSnapshot(_UISealedSnapshot):
    feature_contract: UIImplementationContract

    @model_validator(mode="after")
    def feature_contract_is_exact(self) -> Self:
        if self.feature_contract.sealed_regime_ref != self.sealed_regime:
            raise ValueError("feature contract must consume the exact sealed regime")
        return self


class UIFeatureContractReadySnapshot(_UIFeatureContractSnapshot):
    state: Literal[UICodesignState.FEATURE_CONTRACT_READY] = UICodesignState.FEATURE_CONTRACT_READY


class _UIImplementationSnapshot(_UIFeatureContractSnapshot):
    implementation_ticket_ref: UIIdentifier


class UIImplementationReadySnapshot(_UIImplementationSnapshot):
    state: Literal[UICodesignState.IMPLEMENTATION_READY] = UICodesignState.IMPLEMENTATION_READY


class _UIVisualReviewSnapshot(_UIImplementationSnapshot):
    visual_evidence_refs: tuple[UIIdentifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def visual_evidence_is_unique(self) -> Self:
        if len(self.visual_evidence_refs) != len(set(self.visual_evidence_refs)):
            raise ValueError("visual evidence references must be unique")
        return self


class UIVisualReviewRequiredSnapshot(_UIVisualReviewSnapshot):
    state: Literal[UICodesignState.VISUAL_REVIEW_REQUIRED] = UICodesignState.VISUAL_REVIEW_REQUIRED


class _UIOwnerAcceptanceSnapshot(_UIVisualReviewSnapshot):
    visual_report: VisualReviewReport

    @model_validator(mode="after")
    def report_implementation_is_exact(self) -> Self:
        if self.visual_report.implementation_ref != self.implementation_ticket_ref:
            raise ValueError("visual report must retain the implementation identity")
        if set(self.visual_report.screenshot_refs) != set(self.visual_evidence_refs):
            raise ValueError("visual report evidence must match admitted visual evidence")
        return self


class UIOwnerAcceptanceRequiredSnapshot(_UIOwnerAcceptanceSnapshot):
    state: Literal[UICodesignState.OWNER_ACCEPTANCE_REQUIRED] = UICodesignState.OWNER_ACCEPTANCE_REQUIRED


class UICompleteSnapshot(_UIOwnerAcceptanceSnapshot):
    state: Literal[UICodesignState.COMPLETE] = UICodesignState.COMPLETE
    owner_acceptance_ref: UIIdentifier


UICodesignSnapshot: TypeAlias = Annotated[
    Union[
        UIBriefDraftSnapshot,
        UIBriefApprovedSnapshot,
        UIDirectionsReadySnapshot,
        UIOwnerSelectionRequiredSnapshot,
        UIRegimeCandidateSelectedSnapshot,
        UIRegimeSealedSnapshot,
        UIFeatureContractReadySnapshot,
        UIImplementationReadySnapshot,
        UIVisualReviewRequiredSnapshot,
        UIOwnerAcceptanceRequiredSnapshot,
        UICompleteSnapshot,
    ],
    Field(discriminator="state"),
]


_SNAPSHOT_ADAPTER: TypeAdapter[UICodesignSnapshot] = TypeAdapter(UICodesignSnapshot)


class ApproveBriefEvent(_UICodesignModel):
    kind: Literal["APPROVE_BRIEF"] = "APPROVE_BRIEF"
    exact_brief_id: UIIdentifier


class ProduceDirectionsEvent(_UICodesignModel):
    kind: Literal["PRODUCE_DIRECTIONS"] = "PRODUCE_DIRECTIONS"
    candidates: tuple[VisualDirectionCandidate, ...] = ()
    renderer_state: ReferenceRendererState

    @model_validator(mode="after")
    def available_renderer_requires_candidates(self) -> Self:
        if self.renderer_state is ReferenceRendererState.UNAVAILABLE and self.candidates:
            raise ValueError("unavailable renderer cannot carry direction candidates")
        if self.renderer_state is not ReferenceRendererState.UNAVAILABLE and len(self.candidates) < 2:
            raise ValueError("available renderer direction production requires two candidates")
        if self.renderer_state is ReferenceRendererState.RENDERED_AVAILABLE and any(
            not isinstance(candidate.evidence, RenderedDirectionEvidence)
            for candidate in self.candidates
        ):
            raise ValueError("rendered direction production requires rendered evidence")
        if self.renderer_state is ReferenceRendererState.ARTIFACT_ONLY and any(
            not isinstance(candidate.evidence, ArtifactDirectionEvidence)
            for candidate in self.candidates
        ):
            raise ValueError("artifact-only direction production requires artifact evidence")
        return self


class RequestOwnerSelectionEvent(_UICodesignModel):
    kind: Literal["REQUEST_OWNER_SELECTION"] = "REQUEST_OWNER_SELECTION"


class SelectDirectionEvent(_UICodesignModel):
    kind: Literal["SELECT_DIRECTION"] = "SELECT_DIRECTION"
    exact_candidate_id: UIIdentifier
    owner_decision_ref: UIIdentifier


class ContextSealedEvent(_UICodesignModel):
    kind: Literal["CONTEXT_SEALED"] = "CONTEXT_SEALED"
    exact_sealed_regime_ref: SealedUIRegimeRef


class CompileFeatureContractEvent(_UICodesignModel):
    kind: Literal["COMPILE_FEATURE_CONTRACT"] = "COMPILE_FEATURE_CONTRACT"
    exact_contract: UIImplementationContract


class AdmitImplementationEvent(_UICodesignModel):
    kind: Literal["ADMIT_IMPLEMENTATION"] = "ADMIT_IMPLEMENTATION"
    exact_ticket_ref: UIIdentifier


class RequestVisualReviewEvent(_UICodesignModel):
    kind: Literal["REQUEST_VISUAL_REVIEW"] = "REQUEST_VISUAL_REVIEW"
    verification_state: VisualVerificationState
    evidence_refs: tuple[UIIdentifier, ...] = ()

    @model_validator(mode="after")
    def evidence_shape_matches_verification(self) -> Self:
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("visual verification evidence references must be unique")
        if self.verification_state is VisualVerificationState.AVAILABLE and not self.evidence_refs:
            raise ValueError("available visual verification requires evidence refs")
        if self.verification_state is VisualVerificationState.UNAVAILABLE and self.evidence_refs:
            raise ValueError("unavailable visual verification cannot invent evidence refs")
        return self


class CompleteReviewEvent(_UICodesignModel):
    kind: Literal["COMPLETE_REVIEW"] = "COMPLETE_REVIEW"
    exact_report: VisualReviewReport


class OwnerAcceptEvent(_UICodesignModel):
    kind: Literal["OWNER_ACCEPT"] = "OWNER_ACCEPT"
    exact_report_id: UIIdentifier
    owner_decision_ref: UIIdentifier


UICodesignEvent: TypeAlias = Annotated[
    Union[
        ApproveBriefEvent,
        ProduceDirectionsEvent,
        RequestOwnerSelectionEvent,
        SelectDirectionEvent,
        ContextSealedEvent,
        CompileFeatureContractEvent,
        AdmitImplementationEvent,
        RequestVisualReviewEvent,
        CompleteReviewEvent,
        OwnerAcceptEvent,
    ],
    Field(discriminator="kind"),
]


class BriefApprovedArtifact(_UICodesignModel):
    kind: Literal["BRIEF_APPROVED"] = "BRIEF_APPROVED"
    brief_id: UIIdentifier
    approved_content_digest: ContentDigest


class DirectionsReadyArtifact(_UICodesignModel):
    kind: Literal["DIRECTIONS_READY"] = "DIRECTIONS_READY"
    candidate_ids: tuple[UIIdentifier, ...] = Field(min_length=2)
    approved_content_digest: ContentDigest
    renderer_state: ReferenceRendererState


class OwnerSelectionArtifact(_UICodesignModel):
    kind: Literal["OWNER_SELECTION_REQUIRED"] = "OWNER_SELECTION_REQUIRED"


class RegimeCandidateArtifact(_UICodesignModel):
    kind: Literal["REGIME_CANDIDATE_SELECTED"] = "REGIME_CANDIDATE_SELECTED"
    regime_candidate_id: UIIdentifier
    selected_candidate_id: UIIdentifier
    owner_decision_ref: UIIdentifier


class SealedRegimeArtifact(_UICodesignModel):
    kind: Literal["REGIME_SEALED"] = "REGIME_SEALED"
    sealed_regime_ref: SealedUIRegimeRef


class FeatureContractArtifact(_UICodesignModel):
    kind: Literal["FEATURE_CONTRACT_READY"] = "FEATURE_CONTRACT_READY"
    contract_id: UIIdentifier


class ImplementationArtifact(_UICodesignModel):
    kind: Literal["IMPLEMENTATION_READY"] = "IMPLEMENTATION_READY"
    ticket_ref: UIIdentifier


class VisualReviewRequestedArtifact(_UICodesignModel):
    kind: Literal["VISUAL_REVIEW_REQUIRED"] = "VISUAL_REVIEW_REQUIRED"
    evidence_refs: tuple[UIIdentifier, ...] = Field(min_length=1)


class VisualReviewArtifact(_UICodesignModel):
    kind: Literal["OWNER_ACCEPTANCE_REQUIRED"] = "OWNER_ACCEPTANCE_REQUIRED"
    report_id: UIIdentifier


class OwnerAcceptanceArtifact(_UICodesignModel):
    kind: Literal["COMPLETE"] = "COMPLETE"
    report_id: UIIdentifier
    owner_decision_ref: UIIdentifier


UIArtifact: TypeAlias = Annotated[
    Union[
        BriefApprovedArtifact,
        DirectionsReadyArtifact,
        OwnerSelectionArtifact,
        RegimeCandidateArtifact,
        SealedRegimeArtifact,
        FeatureContractArtifact,
        ImplementationArtifact,
        VisualReviewRequestedArtifact,
        VisualReviewArtifact,
        OwnerAcceptanceArtifact,
    ],
    Field(discriminator="kind"),
]


class UICodesignAdvanceDecision(_UICodesignModel):
    kind: Literal["ADVANCE"] = "ADVANCE"
    next_snapshot: UICodesignSnapshot
    artifact: UIArtifact


class UICodesignWaitDecision(_UICodesignModel):
    kind: Literal["WAIT"] = "WAIT"
    snapshot: UICodesignSnapshot
    reason: UICodesignWaitReason

    @property
    def next_snapshot(self) -> UICodesignSnapshot:
        return self.snapshot


class UICodesignRefuseDecision(_UICodesignModel):
    kind: Literal["REFUSE"] = "REFUSE"
    snapshot: UICodesignSnapshot
    reason: UICodesignRefusalReason

    @property
    def next_snapshot(self) -> UICodesignSnapshot:
        return self.snapshot


UICodesignDecision: TypeAlias = Annotated[
    Union[UICodesignAdvanceDecision, UICodesignWaitDecision, UICodesignRefuseDecision],
    Field(discriminator="kind"),
]


AdvanceDecision: TypeAlias = UICodesignAdvanceDecision
WaitDecision: TypeAlias = UICodesignWaitDecision
RefuseDecision: TypeAlias = UICodesignRefuseDecision


_EVENT_ADAPTER: TypeAdapter[UICodesignEvent] = TypeAdapter(UICodesignEvent)


def _approved_snapshot(source: UICodesignSnapshot) -> UIBriefApprovedSnapshot:
    return UIBriefApprovedSnapshot(
        brief=source.brief,
        approved_brief_id=source.brief.brief_id,
        approved_content_digest=source.brief.content_digest,
    )


def _directions_snapshot(
    source: UICodesignSnapshot,
    candidates: tuple[VisualDirectionCandidate, ...],
    renderer_state: ReferenceRendererState,
) -> UIDirectionsReadySnapshot:
    if not isinstance(source, _UIApprovedSnapshot):
        raise ValueError("directions transition requires an approved snapshot")
    return UIDirectionsReadySnapshot(
        brief=source.brief,
        approved_brief_id=source.brief.brief_id,
        approved_content_digest=source.brief.content_digest,
        directions=candidates,
        renderer_state=renderer_state,
    )


def _owner_selection_snapshot(source: UICodesignSnapshot) -> UIOwnerSelectionRequiredSnapshot:
    if not isinstance(source, _UIDirectionsSnapshot):
        raise ValueError("owner-selection transition requires directions")
    return UIOwnerSelectionRequiredSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
    )


def _candidate_snapshot(
    source: UICodesignSnapshot,
    regime_candidate: UIRegimeCandidate,
) -> UIRegimeCandidateSelectedSnapshot:
    if not isinstance(source, _UIDirectionsSnapshot):
        raise ValueError("candidate transition requires directions")
    return UIRegimeCandidateSelectedSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=regime_candidate,
    )


def _sealed_snapshot(
    source: UICodesignSnapshot,
    sealed_regime: SealedUIRegimeRef,
) -> UIRegimeSealedSnapshot:
    if not isinstance(source, _UIRegimeCandidateSnapshot):
        raise ValueError("sealed transition requires a regime candidate")
    return UIRegimeSealedSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=sealed_regime,
    )


def _feature_contract_snapshot(
    source: UICodesignSnapshot,
    feature_contract: UIImplementationContract,
) -> UIFeatureContractReadySnapshot:
    if not isinstance(source, _UISealedSnapshot):
        raise ValueError("feature transition requires a sealed regime")
    return UIFeatureContractReadySnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=source.sealed_regime,
        feature_contract=feature_contract,
    )


def _implementation_snapshot(
    source: UICodesignSnapshot,
    ticket_ref: UIIdentifier,
) -> UIImplementationReadySnapshot:
    if not isinstance(source, _UIFeatureContractSnapshot):
        raise ValueError("implementation transition requires a feature contract")
    return UIImplementationReadySnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=source.sealed_regime,
        feature_contract=source.feature_contract,
        implementation_ticket_ref=ticket_ref,
    )


def _visual_review_snapshot(
    source: UICodesignSnapshot,
    evidence_refs: tuple[UIIdentifier, ...],
) -> UIVisualReviewRequiredSnapshot:
    if not isinstance(source, _UIImplementationSnapshot):
        raise ValueError("visual-review transition requires implementation")
    return UIVisualReviewRequiredSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=source.sealed_regime,
        feature_contract=source.feature_contract,
        implementation_ticket_ref=source.implementation_ticket_ref,
        visual_evidence_refs=evidence_refs,
    )


def _owner_acceptance_snapshot(
    source: UICodesignSnapshot,
    report: VisualReviewReport,
) -> UIOwnerAcceptanceRequiredSnapshot:
    if not isinstance(source, _UIVisualReviewSnapshot):
        raise ValueError("owner-acceptance transition requires visual evidence")
    return UIOwnerAcceptanceRequiredSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=source.sealed_regime,
        feature_contract=source.feature_contract,
        implementation_ticket_ref=source.implementation_ticket_ref,
        visual_evidence_refs=source.visual_evidence_refs,
        visual_report=report,
    )


def _complete_snapshot(
    source: UICodesignSnapshot,
    owner_acceptance_ref: UIIdentifier,
) -> UICompleteSnapshot:
    if not isinstance(source, UIOwnerAcceptanceRequiredSnapshot):
        raise ValueError("complete transition requires owner-acceptance state")
    return UICompleteSnapshot(
        brief=source.brief,
        approved_brief_id=source.approved_brief_id,
        approved_content_digest=source.approved_content_digest,
        directions=source.directions,
        renderer_state=source.renderer_state,
        regime_candidate=source.regime_candidate,
        sealed_regime=source.sealed_regime,
        feature_contract=source.feature_contract,
        implementation_ticket_ref=source.implementation_ticket_ref,
        visual_evidence_refs=source.visual_evidence_refs,
        visual_report=source.visual_report,
        owner_acceptance_ref=owner_acceptance_ref,
    )


def _refuse(snapshot: UICodesignSnapshot, reason: UICodesignRefusalReason) -> UICodesignRefuseDecision:
    return UICodesignRefuseDecision(snapshot=snapshot, reason=reason)


def _wait(snapshot: UICodesignSnapshot, reason: UICodesignWaitReason) -> UICodesignWaitDecision:
    return UICodesignWaitDecision(snapshot=snapshot, reason=reason)


def _advance(
    snapshot: UICodesignSnapshot,
    artifact: UIArtifact,
) -> UICodesignAdvanceDecision:
    return UICodesignAdvanceDecision(next_snapshot=snapshot, artifact=artifact)


def reduce_ui_codesign(
    state: UICodesignSnapshot,
    event: UICodesignEvent,
) -> UICodesignDecision:
    """Apply exactly one legal UI co-design lifecycle event without side effects."""

    trusted_state = _SNAPSHOT_ADAPTER.validate_python(state)
    try:
        trusted_event = _EVENT_ADAPTER.validate_python(event)
    except ValueError:
        return _refuse(trusted_state, UICodesignRefusalReason.INVALID_TRANSITION)
    next_snapshot: UICodesignSnapshot

    if (
        isinstance(trusted_state, UIBriefDraftSnapshot)
        and isinstance(trusted_event, ApproveBriefEvent)
    ):
        if trusted_event.exact_brief_id != trusted_state.brief.brief_id:
            return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
        next_snapshot = _approved_snapshot(trusted_state)
        return _advance(
            next_snapshot,
            BriefApprovedArtifact(
                brief_id=trusted_state.brief.brief_id,
                approved_content_digest=trusted_state.brief.content_digest,
            ),
        )

    if (
        isinstance(trusted_state, UIBriefApprovedSnapshot)
        and isinstance(trusted_event, ProduceDirectionsEvent)
    ):
        if trusted_event.renderer_state is ReferenceRendererState.UNAVAILABLE:
            return _wait(trusted_state, UICodesignWaitReason.UI_REFERENCE_RENDERER_REQUIRED)
        approved_content_digest = trusted_state.approved_content_digest
        if not _direction_evidence_is_valid(
            trusted_event.candidates,
            trusted_event.renderer_state,
            approved_content_digest,
        ):
            if trusted_event.candidates and any(
                candidate.approved_content_digest != approved_content_digest
                for candidate in trusted_event.candidates
            ):
                return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
            return _refuse(trusted_state, UICodesignRefusalReason.DISTINCT_DIRECTION_REQUIRED)
        next_snapshot = _directions_snapshot(
            trusted_state,
            trusted_event.candidates,
            trusted_event.renderer_state,
        )
        return _advance(
            next_snapshot,
            DirectionsReadyArtifact(
                candidate_ids=tuple(candidate.candidate_id for candidate in trusted_event.candidates),
                approved_content_digest=approved_content_digest,
                renderer_state=trusted_event.renderer_state,
            ),
        )

    if isinstance(trusted_state, UIDirectionsReadySnapshot) and isinstance(
        trusted_event, RequestOwnerSelectionEvent
    ):
        next_snapshot = _owner_selection_snapshot(trusted_state)
        return _advance(next_snapshot, OwnerSelectionArtifact())

    if isinstance(trusted_state, UIOwnerSelectionRequiredSnapshot) and isinstance(
        trusted_event, SelectDirectionEvent
    ):
        selected = next(
            (candidate for candidate in trusted_state.directions if candidate.candidate_id == trusted_event.exact_candidate_id),
            None,
        )
        if selected is None:
            return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
        regime_candidate = UIRegimeCandidate(
            regime_candidate_id=f"regime-{selected.candidate_id}",
            brief_id=trusted_state.brief.brief_id,
            selected_candidate_id=selected.candidate_id,
            selected_candidate_digest=selected.candidate_digest,
            approved_content_digest=selected.approved_content_digest,
            owner_decision_ref=trusted_event.owner_decision_ref,
        )
        next_snapshot = _candidate_snapshot(trusted_state, regime_candidate)
        return _advance(
            next_snapshot,
            RegimeCandidateArtifact(
                regime_candidate_id=regime_candidate.regime_candidate_id,
                selected_candidate_id=regime_candidate.selected_candidate_id,
                owner_decision_ref=regime_candidate.owner_decision_ref,
            ),
        )

    if isinstance(trusted_state, UIRegimeCandidateSelectedSnapshot) and isinstance(
        trusted_event, ContextSealedEvent
    ):
        selected_regime_candidate = trusted_state.regime_candidate
        if (
            trusted_event.exact_sealed_regime_ref.selected_candidate_id
            != selected_regime_candidate.selected_candidate_id
        ):
            return _refuse(trusted_state, UICodesignRefusalReason.CONTEXT_SEAL_REQUIRED)
        next_snapshot = _sealed_snapshot(trusted_state, trusted_event.exact_sealed_regime_ref)
        return _advance(next_snapshot, SealedRegimeArtifact(sealed_regime_ref=trusted_event.exact_sealed_regime_ref))

    if isinstance(trusted_state, UIRegimeSealedSnapshot) and isinstance(
        trusted_event, CompileFeatureContractEvent
    ):
        if trusted_event.exact_contract.sealed_regime_ref != trusted_state.sealed_regime:
            return _refuse(trusted_state, UICodesignRefusalReason.CONTEXT_SEAL_REQUIRED)
        next_snapshot = _feature_contract_snapshot(trusted_state, trusted_event.exact_contract)
        return _advance(next_snapshot, FeatureContractArtifact(contract_id=trusted_event.exact_contract.contract_id))

    if isinstance(trusted_state, UIFeatureContractReadySnapshot) and isinstance(
        trusted_event, AdmitImplementationEvent
    ):
        next_snapshot = _implementation_snapshot(trusted_state, trusted_event.exact_ticket_ref)
        return _advance(next_snapshot, ImplementationArtifact(ticket_ref=trusted_event.exact_ticket_ref))

    if isinstance(trusted_state, UIImplementationReadySnapshot) and isinstance(
        trusted_event, RequestVisualReviewEvent
    ):
        if trusted_event.verification_state is VisualVerificationState.UNAVAILABLE:
            return _wait(trusted_state, UICodesignWaitReason.VISUAL_VERIFICATION_REQUIRED)
        next_snapshot = _visual_review_snapshot(trusted_state, trusted_event.evidence_refs)
        return _advance(
            next_snapshot,
            VisualReviewRequestedArtifact(evidence_refs=trusted_event.evidence_refs),
        )

    if isinstance(trusted_state, UIVisualReviewRequiredSnapshot) and isinstance(
        trusted_event, CompleteReviewEvent
    ):
        if trusted_event.exact_report.implementation_ref != trusted_state.implementation_ticket_ref:
            return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
        if set(trusted_event.exact_report.screenshot_refs) != set(trusted_state.visual_evidence_refs):
            return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
        next_snapshot = _owner_acceptance_snapshot(trusted_state, trusted_event.exact_report)
        return _advance(next_snapshot, VisualReviewArtifact(report_id=trusted_event.exact_report.report_id))

    if isinstance(trusted_state, UIOwnerAcceptanceRequiredSnapshot) and isinstance(
        trusted_event, OwnerAcceptEvent
    ):
        visual_report = trusted_state.visual_report
        if trusted_event.exact_report_id != visual_report.report_id:
            return _refuse(trusted_state, UICodesignRefusalReason.EVIDENCE_MISMATCH)
        next_snapshot = _complete_snapshot(trusted_state, trusted_event.owner_decision_ref)
        return _advance(
            next_snapshot,
            OwnerAcceptanceArtifact(
                report_id=trusted_event.exact_report_id,
                owner_decision_ref=trusted_event.owner_decision_ref,
            ),
        )

    return _refuse(trusted_state, UICodesignRefusalReason.INVALID_TRANSITION)


__all__ = [
    "AccessibilityContract",
    "AdmitImplementationEvent",
    "AdvanceDecision",
    "ArtifactDirectionEvidence",
    "BriefApprovedArtifact",
    "CompileFeatureContractEvent",
    "CompleteReviewEvent",
    "ContentDigest",
    "ContextSealedEvent",
    "DesignCapabilityState",
    "DesignSourceKind",
    "DirectionsReadyArtifact",
    "DirectionEvidence",
    "FeatureContractArtifact",
    "ImplementationArtifact",
    "OfflineDisposition",
    "OwnerAcceptEvent",
    "OwnerAcceptanceArtifact",
    "OwnerSelectionArtifact",
    "ProduceDirectionsEvent",
    "ReferenceRendererState",
    "RefuseDecision",
    "RegimeCandidateArtifact",
    "RequestOwnerSelectionEvent",
    "RequestVisualReviewEvent",
    "ResponsiveBreakpoint",
    "SealedRegimeArtifact",
    "SealedUIRegimeRef",
    "SelectDirectionEvent",
    "UIArtifact",
    "UIBriefApprovedSnapshot",
    "UIBriefDraftSnapshot",
    "UICompleteSnapshot",
    "UICodesignAdvanceDecision",
    "UICodesignDecision",
    "UICodesignEvent",
    "UICodesignRefusalReason",
    "UICodesignRefuseDecision",
    "UICodesignSnapshot",
    "UICodesignState",
    "UICodesignWaitDecision",
    "UICodesignWaitReason",
    "UIDesignBrief",
    "UIDirectionsReadySnapshot",
    "UIFeatureContractReadySnapshot",
    "UIFeatureState",
    "UIFeatureStateContract",
    "UIImplementationReadySnapshot",
    "UIImplementationContract",
    "UIIdentifier",
    "UIOwnerAcceptanceRequiredSnapshot",
    "UIOwnerSelectionRequiredSnapshot",
    "UIRegime",
    "UIRegimeCandidate",
    "UIRegimeCandidateSelectedSnapshot",
    "UIRegimeSealedSnapshot",
    "VisualDirectionCandidate",
    "VisualEvidenceCell",
    "VisualFinding",
    "VisualFindingSeverity",
    "VisualReviewArtifact",
    "VisualReviewReport",
    "VisualReviewRequestedArtifact",
    "UIVisualReviewRequiredSnapshot",
    "VisualVerificationState",
    "ViewportKind",
    "WaitDecision",
    "reduce_ui_codesign",
]
