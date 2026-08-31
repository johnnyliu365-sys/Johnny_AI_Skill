"""Acceptance and reverse-mutation tests for UIX-01 co-design contracts."""

from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path
from typing import get_args
import unittest

from pydantic import TypeAdapter, ValidationError

from library.workflow_router.ui_codesign_contracts import (
    AccessibilityContract,
    AdmitImplementationEvent,
    ApproveBriefEvent,
    ArtifactDirectionEvidence,
    BriefApprovedArtifact,
    CompileFeatureContractEvent,
    CompleteReviewEvent,
    ContextSealedEvent,
    DesignCapabilityState,
    DesignSourceKind,
    DirectionsReadyArtifact,
    FeatureContractArtifact,
    ImplementationArtifact,
    OfflineDisposition,
    OwnerAcceptEvent,
    OwnerAcceptanceArtifact,
    OwnerSelectionArtifact,
    ProduceDirectionsEvent,
    ReferenceRendererState,
    RegimeCandidateArtifact,
    RenderedDirectionEvidence,
    RequestOwnerSelectionEvent,
    RequestVisualReviewEvent,
    ResponsiveBreakpoint,
    SealedRegimeArtifact,
    SealedUIRegimeRef,
    SelectDirectionEvent,
    UIArtifact,
    UICodesignAdvanceDecision,
    UICodesignDecision,
    UICodesignEvent,
    UICodesignRefusalReason,
    UICodesignRefuseDecision,
    UICodesignSnapshot,
    UICodesignState,
    UICodesignWaitDecision,
    UICodesignWaitReason,
    UIDesignBrief,
    UIBriefApprovedSnapshot,
    UIBriefDraftSnapshot,
    UIDirectionsReadySnapshot,
    UIFeatureContractReadySnapshot,
    UIImplementationReadySnapshot,
    UIOwnerAcceptanceRequiredSnapshot,
    UIOwnerSelectionRequiredSnapshot,
    UICompleteSnapshot,
    UIRegimeCandidateSelectedSnapshot,
    UIRegimeSealedSnapshot,
    UIVisualReviewRequiredSnapshot,
    UIFeatureState,
    UIFeatureStateContract,
    UIImplementationContract,
    UIRegimeCandidate,
    VisualDirectionCandidate,
    VisualEvidenceCell,
    VisualFinding,
    VisualFindingSeverity,
    VisualReviewArtifact,
    VisualReviewReport,
    VisualReviewRequestedArtifact,
    VisualVerificationState,
    ViewportKind,
    reduce_ui_codesign,
)


DIGEST = "a" * 64
CONTEXT_DIGEST = "b" * 64


def _brief() -> UIDesignBrief:
    return UIDesignBrief(
        brief_id="brief-ui-dashboard",
        product="A calm operations dashboard",
        audience="Small support teams",
        job="Resolve the next customer issue",
        brand_personality="Clear, warm and focused",
        brand_anti_goals=("No noisy gamification", "No ornamental density"),
        target_platform="Responsive web application",
        content_hierarchy="Queue first, issue details second, actions last",
        information_density="Moderate density with deliberate breathing room",
        accessibility_baseline="Keyboard complete, semantic landmarks and WCAG AA contrast",
        locale="en-US",
        content_constraints="Keep labels short and preserve customer-entered Unicode",
        required_states=tuple(UIFeatureState),
        offline_disposition=OfflineDisposition.NOT_APPLICABLE,
        design_source=DesignSourceKind.NONE,
        content_digest=DIGEST,
    )


def _direction(
    candidate_id: str,
    *,
    colour: str = "Blue semantic actions",
    rendered: bool = False,
    macrostructure: str = "Split queue and detail panels on desktop",
    digest: str = DIGEST,
) -> VisualDirectionCandidate:
    evidence = (
        RenderedDirectionEvidence(
            desktop_evidence_ref=f"desktop-{candidate_id}",
            mobile_evidence_ref=f"mobile-{candidate_id}",
        )
        if rendered
        else ArtifactDirectionEvidence(
            desktop_artifact_ref=f"desktop-{candidate_id}",
            mobile_artifact_ref=f"mobile-{candidate_id}",
            owner_manual_open_acknowledgement=True,
        )
    )
    return VisualDirectionCandidate(
        candidate_id=candidate_id,
        rationale=f"Rationale for {candidate_id}",
        hierarchy="Queue dominates the first viewport",
        typography="Humanist sans with a compact numeric scale",
        density="Moderate rows with grouped metadata",
        component_language="Quiet cards and explicit action buttons",
        spacing="Eight-point rhythm with generous section gaps",
        semantic_colour=colour,
        motion_character="Short, interruptible transitions",
        macrostructure=macrostructure,
        accessibility_notes="Visible focus and reduced-motion fallback",
        approved_content_digest=digest,
        evidence=evidence,
    )


def _sealed(candidate_id: str = "direction-a", *, digest: str = CONTEXT_DIGEST) -> SealedUIRegimeRef:
    return SealedUIRegimeRef(
        context_artifact_id="context-ui-regime",
        context_revision="revision-ui-regime",
        context_digest=digest,
        selected_candidate_id=candidate_id,
        owner_approval_ref="owner-approval-ui-regime",
    )


def _contract(sealed: SealedUIRegimeRef | None = None) -> UIImplementationContract:
    exact_sealed = _sealed() if sealed is None else sealed
    return UIImplementationContract(
        contract_id="contract-support-queue",
        sealed_regime_ref=exact_sealed,
        component_boundary="Support queue owns list, details and explicit action events",
        inputs=("ticket collection", "selected ticket identity"),
        outputs=("ticket selected", "ticket action requested"),
        feature_states=tuple(
            UIFeatureStateContract(state=state, behavior=f"Visible {state.value.lower()} behavior")
            for state in UIFeatureState
        ),
        responsive_breakpoints=(
            ResponsiveBreakpoint(
                breakpoint_id="breakpoint-mobile",
                viewport=ViewportKind.MOBILE,
                layout_behavior="Stack queue above details",
            ),
            ResponsiveBreakpoint(
                breakpoint_id="breakpoint-desktop",
                viewport=ViewportKind.DESKTOP,
                layout_behavior="Keep queue and details side by side",
            ),
        ),
        accessibility=AccessibilityContract(
            keyboard_behavior="Every action is keyboard reachable",
            focus_behavior="Focus moves to the opened ticket heading",
            semantic_roles=("main", "list", "status"),
            contrast_requirements="Text and actions meet WCAG AA contrast",
            reduced_motion_behavior="Disable non-essential movement",
        ),
        asset_boundaries=("avatar asset references are opaque",),
        interaction_boundaries=("selection and action events cross the component boundary",),
        offline_disposition=OfflineDisposition.NOT_APPLICABLE,
    )


def _report(
    implementation_ref: str = "ticket-support-queue",
    screenshot_refs: tuple[str, str] = (
        "screenshot-mobile-success",
        "screenshot-desktop-success",
    ),
) -> VisualReviewReport:
    return VisualReviewReport(
        report_id="report-support-queue",
        implementation_ref=implementation_ref,
        screenshot_refs=screenshot_refs,
        breakpoint_state_matrix=(
            VisualEvidenceCell(
                breakpoint_id="breakpoint-mobile",
                state=UIFeatureState.SUCCESS,
                screenshot_ref=screenshot_refs[0],
                evidence_digest="c" * 64,
            ),
            VisualEvidenceCell(
                breakpoint_id="breakpoint-desktop",
                state=UIFeatureState.SUCCESS,
                screenshot_ref=screenshot_refs[1],
                evidence_digest="d" * 64,
            ),
        ),
        findings=(
            VisualFinding(
                finding_id="finding-focus-ring",
                severity=VisualFindingSeverity.POLISH,
                dimension="focus visibility",
                description="Focus ring remains visible on the selected action",
                evidence_refs=(screenshot_refs[0],),
            ),
        ),
        evidence_digests=("c" * 64, "d" * 64),
    )


def _advance(result: UICodesignDecision) -> UICodesignAdvanceDecision:
    if not isinstance(result, UICodesignAdvanceDecision):
        raise AssertionError(f"expected ADVANCE, got {result!r}")
    return result


class UIX01CodesignContractTests(unittest.TestCase):
    def test_ui1_public_models_events_artifacts_decisions_round_trip(self) -> None:
        brief = _brief()
        candidate_a = _direction("direction-a")
        candidate_b = _direction("direction-b", colour="Amber semantic actions")
        sealed = _sealed()
        contract = _contract(sealed)
        report = _report()
        snapshot = UIBriefDraftSnapshot(brief=brief)
        models = (
            brief,
            ArtifactDirectionEvidence(
                desktop_artifact_ref="desktop-direction-a",
                mobile_artifact_ref="mobile-direction-a",
                owner_manual_open_acknowledgement=True,
            ),
            RenderedDirectionEvidence(
                desktop_evidence_ref="desktop-direction-a",
                mobile_evidence_ref="mobile-direction-a",
            ),
            candidate_a,
            sealed,
            _contract(),
            contract,
            VisualEvidenceCell(
                breakpoint_id="breakpoint-mobile",
                state=UIFeatureState.SUCCESS,
                screenshot_ref="screenshot-mobile-success",
                evidence_digest="c" * 64,
            ),
            VisualFinding(
                finding_id="finding-focus-ring",
                severity=VisualFindingSeverity.POLISH,
                dimension="focus visibility",
                description="Focus remains visible",
                evidence_refs=("screenshot-mobile-success",),
            ),
            report,
            snapshot,
        )
        for model in models:
            rebuilt = type(model).model_validate_json(model.model_dump_json())
            self.assertEqual(model, rebuilt)
        snapshot_adapter: TypeAdapter[UICodesignSnapshot] = TypeAdapter(UICodesignSnapshot)
        self.assertEqual(snapshot, snapshot_adapter.validate_json(snapshot.model_dump_json()))

        events: tuple[UICodesignEvent, ...] = (
            ApproveBriefEvent(exact_brief_id=brief.brief_id),
            ProduceDirectionsEvent(
                candidates=(candidate_a, candidate_b),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            ),
            RequestOwnerSelectionEvent(),
            SelectDirectionEvent(exact_candidate_id="direction-a", owner_decision_ref="owner-direction-a"),
            ContextSealedEvent(exact_sealed_regime_ref=sealed),
            CompileFeatureContractEvent(exact_contract=contract),
            AdmitImplementationEvent(exact_ticket_ref="ticket-support-queue"),
            RequestVisualReviewEvent(
                verification_state=VisualVerificationState.AVAILABLE,
                evidence_refs=("evidence-review",),
            ),
            CompleteReviewEvent(exact_report=report),
            OwnerAcceptEvent(exact_report_id=report.report_id, owner_decision_ref="owner-acceptance"),
        )
        event_adapter: TypeAdapter[UICodesignEvent] = TypeAdapter(UICodesignEvent)
        for event in events:
            self.assertEqual(event, event_adapter.validate_json(event.model_dump_json()))

        artifacts: tuple[UIArtifact, ...] = (
            BriefApprovedArtifact(brief_id=brief.brief_id, approved_content_digest=DIGEST),
            DirectionsReadyArtifact(
                candidate_ids=("direction-a", "direction-b"),
                approved_content_digest=DIGEST,
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            ),
            OwnerSelectionArtifact(),
            RegimeCandidateArtifact(
                regime_candidate_id="regime-direction-a",
                selected_candidate_id="direction-a",
                owner_decision_ref="owner-direction-a",
            ),
            SealedRegimeArtifact(sealed_regime_ref=sealed),
            FeatureContractArtifact(contract_id=contract.contract_id),
            ImplementationArtifact(ticket_ref="ticket-support-queue"),
            VisualReviewRequestedArtifact(evidence_refs=("evidence-review",)),
            VisualReviewArtifact(report_id=report.report_id),
            OwnerAcceptanceArtifact(report_id=report.report_id, owner_decision_ref="owner-acceptance"),
        )
        artifact_adapter: TypeAdapter[UIArtifact] = TypeAdapter(UIArtifact)
        for artifact in artifacts:
            self.assertEqual(artifact, artifact_adapter.validate_json(artifact.model_dump_json()))

        decisions: tuple[UICodesignDecision, ...] = (
            UICodesignAdvanceDecision(
                next_snapshot=UIBriefApprovedSnapshot(
                    brief=brief,
                    approved_brief_id=brief.brief_id,
                    approved_content_digest=DIGEST,
                ),
                artifact=BriefApprovedArtifact(
                    brief_id=brief.brief_id,
                    approved_content_digest=DIGEST,
                ),
            ),
            UICodesignWaitDecision(snapshot=snapshot, reason=UICodesignWaitReason.UI_REFERENCE_RENDERER_REQUIRED),
            UICodesignRefuseDecision(snapshot=snapshot, reason=UICodesignRefusalReason.INVALID_TRANSITION),
        )
        decision_adapter: TypeAdapter[UICodesignDecision] = TypeAdapter(UICodesignDecision)
        for decision in decisions:
            self.assertEqual(decision, decision_adapter.validate_json(decision.model_dump_json()))

        for enum_type in (
            UICodesignState,
            DesignSourceKind,
            DesignCapabilityState,
            ReferenceRendererState,
            VisualVerificationState,
            VisualFindingSeverity,
            UIFeatureState,
            OfflineDisposition,
            ViewportKind,
            UICodesignWaitReason,
            UICodesignRefusalReason,
        ):
            for member in enum_type:
                self.assertEqual(member, enum_type(member.value))

    def test_ui1_strict_boundaries_reject_unsafe_and_contradictory_values(self) -> None:
        with self.assertRaises(ValidationError):
            UIDesignBrief.model_validate({**_brief().model_dump(), "brief_id": "https://bad.invalid"})
        with self.assertRaises(ValidationError):
            UIDesignBrief.model_validate({**_brief().model_dump(), "required_states": tuple(UIFeatureState)[:-1]})
        with self.assertRaises(ValidationError):
            VisualReviewReport.model_validate({**_report().model_dump(), "owner_acceptance_ref": "owner-acceptance"})
        with self.assertRaises(ValidationError):
            UIImplementationContract.model_validate(
                {
                    **_contract().model_dump(),
                    "feature_states": _contract().feature_states[:-1],
                }
            )
        long_unicode = "界面😀" * 120
        brief = UIDesignBrief(
            **{
                **_brief().model_dump(),
                "content_constraints": long_unicode,
            }
        )
        self.assertEqual(long_unicode, brief.content_constraints)

    def test_uix_snapshot_variants_have_no_action_dependent_nullable_stage_fields(self) -> None:
        variants = (
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
        )
        for variant in variants:
            for field_name, field in variant.model_fields.items():
                self.assertTrue(field.is_required() or field_name == "state")
                self.assertNotIn(type(None), get_args(field.annotation))

        with self.assertRaises(ValidationError):
            UIBriefApprovedSnapshot.model_validate(
                {
                    "brief": _brief().model_dump(),
                    "approved_brief_id": "brief-ui-dashboard",
                    "approved_content_digest": DIGEST,
                    "directions": (),
                }
            )

    def test_ui2_approval_and_structural_distinctness(self) -> None:
        brief = _brief()
        initial = UIBriefDraftSnapshot(brief=brief)
        approved = _advance(reduce_ui_codesign(initial, ApproveBriefEvent(exact_brief_id=brief.brief_id)))
        self.assertEqual(UICodesignState.BRIEF_APPROVED, approved.next_snapshot.state)
        distinct = _advance(
            reduce_ui_codesign(
                approved.next_snapshot,
                ProduceDirectionsEvent(
                    candidates=(
                        _direction("direction-a"),
                        _direction(
                            "direction-b",
                            colour="Amber actions",
                            macrostructure="Focus one ticket at a time with a persistent action rail",
                        ),
                    ),
                    renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
                ),
            )
        )
        self.assertEqual(UICodesignState.DIRECTIONS_READY, distinct.next_snapshot.state)

        palette_only = reduce_ui_codesign(
            approved.next_snapshot,
            ProduceDirectionsEvent(
                candidates=(_direction("direction-a"), _direction("direction-b", colour="Green actions")),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            ),
        )
        self.assertIsInstance(palette_only, UICodesignRefuseDecision)
        if isinstance(palette_only, UICodesignRefuseDecision):
            self.assertEqual(UICodesignRefusalReason.DISTINCT_DIRECTION_REQUIRED, palette_only.reason)

    def test_ui3_renderer_evidence_and_waits(self) -> None:
        brief = _brief()
        approved = _advance(
            reduce_ui_codesign(
                UIBriefDraftSnapshot(brief=brief),
                ApproveBriefEvent(exact_brief_id=brief.brief_id),
            )
        ).next_snapshot
        wait = reduce_ui_codesign(
            approved,
            ProduceDirectionsEvent(renderer_state=ReferenceRendererState.UNAVAILABLE),
        )
        self.assertIsInstance(wait, UICodesignWaitDecision)
        if isinstance(wait, UICodesignWaitDecision):
            self.assertEqual(UICodesignWaitReason.UI_REFERENCE_RENDERER_REQUIRED, wait.reason)
            self.assertEqual(approved, wait.snapshot)
        rendered = reduce_ui_codesign(
            approved,
            ProduceDirectionsEvent(
                candidates=(
                    _direction("direction-a", rendered=True),
                    _direction(
                        "direction-b",
                        rendered=True,
                        colour="Amber",
                        macrostructure="Focus one ticket at a time with a persistent action rail",
                    ),
                ),
                renderer_state=ReferenceRendererState.RENDERED_AVAILABLE,
            ),
        )
        self.assertIsInstance(rendered, UICodesignAdvanceDecision)
        with self.assertRaises(ValidationError):
            ProduceDirectionsEvent(
                candidates=(_direction("direction-a"), _direction("direction-b")),
                renderer_state=ReferenceRendererState.RENDERED_AVAILABLE,
            )
        with self.assertRaises(ValidationError):
            ProduceDirectionsEvent(
                candidates=(_direction("direction-a"), _direction("direction-b")),
                renderer_state=ReferenceRendererState.UNAVAILABLE,
            )

    def test_uix_deserialized_direction_snapshots_reject_forged_invariants(self) -> None:
        brief = _brief()
        approved = UIBriefApprovedSnapshot(
            brief=brief,
            approved_brief_id=brief.brief_id,
            approved_content_digest=brief.content_digest,
        )
        candidate_a = _direction("direction-a")

        with self.assertRaises(ValidationError):
            UIDirectionsReadySnapshot(
                brief=brief,
                approved_brief_id=approved.approved_brief_id,
                approved_content_digest=approved.approved_content_digest,
                directions=(candidate_a, _direction("direction-a", colour="Amber")),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            )
        with self.assertRaises(ValidationError):
            UIDirectionsReadySnapshot(
                brief=brief,
                approved_brief_id=approved.approved_brief_id,
                approved_content_digest=approved.approved_content_digest,
                directions=(candidate_a, _direction("direction-b", digest="e" * 64)),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            )
        with self.assertRaises(ValidationError):
            UIDirectionsReadySnapshot(
                brief=brief,
                approved_brief_id=approved.approved_brief_id,
                approved_content_digest=approved.approved_content_digest,
                directions=(candidate_a, _direction("direction-b", rendered=True, macrostructure="Focus one ticket")),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            )
        with self.assertRaises(ValidationError):
            UIDirectionsReadySnapshot(
                brief=brief,
                approved_brief_id=approved.approved_brief_id,
                approved_content_digest=approved.approved_content_digest,
                directions=(candidate_a, _direction("direction-b", colour="Green")),
                renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
            )

    def test_ui4_selection_and_context_sealing_are_separate(self) -> None:
        brief = _brief()
        approved = _advance(
            reduce_ui_codesign(
                UIBriefDraftSnapshot(brief=brief),
                ApproveBriefEvent(exact_brief_id=brief.brief_id),
            )
        ).next_snapshot
        directions = _advance(
            reduce_ui_codesign(
                approved,
                ProduceDirectionsEvent(
                    candidates=(
                        _direction("direction-a"),
                        _direction(
                            "direction-b",
                            colour="Amber",
                            macrostructure="Focus one ticket at a time with a persistent action rail",
                        ),
                    ),
                    renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
                ),
            )
        ).next_snapshot
        selection_wait = _advance(reduce_ui_codesign(directions, RequestOwnerSelectionEvent())).next_snapshot
        forged = reduce_ui_codesign(
            selection_wait,
            SelectDirectionEvent(exact_candidate_id="direction-forged", owner_decision_ref="owner-direction"),
        )
        self.assertIsInstance(forged, UICodesignRefuseDecision)
        selected = _advance(
            reduce_ui_codesign(
                selection_wait,
                SelectDirectionEvent(exact_candidate_id="direction-a", owner_decision_ref="owner-direction"),
            )
        ).next_snapshot
        self.assertEqual(UICodesignState.REGIME_CANDIDATE_SELECTED, selected.state)
        direct_seal = reduce_ui_codesign(selected, SelectDirectionEvent(exact_candidate_id="direction-a", owner_decision_ref="owner-direction"))
        self.assertIsInstance(direct_seal, UICodesignRefuseDecision)
        sealed = _advance(reduce_ui_codesign(selected, ContextSealedEvent(exact_sealed_regime_ref=_sealed()))).next_snapshot
        self.assertEqual(UICodesignState.REGIME_SEALED, sealed.state)
        stale = reduce_ui_codesign(
            selected,
            ContextSealedEvent(
                exact_sealed_regime_ref=SealedUIRegimeRef(
                    context_artifact_id="context-ui-regime",
                    context_revision="revision-ui-regime",
                    context_digest="e" * 64,
                    selected_candidate_id="direction-forged",
                    owner_approval_ref="owner-approval-ui-regime",
                )
            ),
        )
        self.assertIsInstance(stale, UICodesignRefuseDecision)
        if isinstance(stale, UICodesignRefuseDecision):
            self.assertEqual(UICodesignRefusalReason.CONTEXT_SEAL_REQUIRED, stale.reason)

    def test_ui5_feature_contract_requires_exact_sealed_regime_and_finite_states(self) -> None:
        sealed = _sealed()
        contract = _contract(sealed)
        self.assertEqual(set(UIFeatureState), {item.state for item in contract.feature_states})
        brief = _brief()
        initial = UIBriefDraftSnapshot(brief=brief)
        approved = _advance(reduce_ui_codesign(initial, ApproveBriefEvent(exact_brief_id=brief.brief_id))).next_snapshot
        directions = _advance(
            reduce_ui_codesign(
                approved,
                ProduceDirectionsEvent(
                    candidates=(
                        _direction("direction-a"),
                        _direction(
                            "direction-b",
                            colour="Amber",
                            macrostructure="Focus one ticket at a time with a persistent action rail",
                        ),
                    ),
                    renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
                ),
            )
        ).next_snapshot
        selected = _advance(reduce_ui_codesign(_advance(reduce_ui_codesign(directions, RequestOwnerSelectionEvent())).next_snapshot, SelectDirectionEvent(exact_candidate_id="direction-a", owner_decision_ref="owner-direction"))).next_snapshot
        sealed_snapshot = _advance(reduce_ui_codesign(selected, ContextSealedEvent(exact_sealed_regime_ref=sealed))).next_snapshot
        mismatch = reduce_ui_codesign(sealed_snapshot, CompileFeatureContractEvent(exact_contract=_contract(_sealed(digest="e" * 64))))
        self.assertIsInstance(mismatch, UICodesignRefuseDecision)
        if isinstance(mismatch, UICodesignRefuseDecision):
            self.assertEqual(UICodesignRefusalReason.CONTEXT_SEAL_REQUIRED, mismatch.reason)
        ready = _advance(reduce_ui_codesign(sealed_snapshot, CompileFeatureContractEvent(exact_contract=contract))).next_snapshot
        self.assertEqual(UICodesignState.FEATURE_CONTRACT_READY, ready.state)

    def test_ui6_visual_review_cannot_self_accept_and_unavailable_waits(self) -> None:
        brief = _brief()
        initial = UIBriefDraftSnapshot(brief=brief)
        approved = _advance(reduce_ui_codesign(initial, ApproveBriefEvent(exact_brief_id=brief.brief_id))).next_snapshot
        directions = _advance(
            reduce_ui_codesign(
                approved,
                ProduceDirectionsEvent(
                    candidates=(
                        _direction("direction-a"),
                        _direction(
                            "direction-b",
                            colour="Amber",
                            macrostructure="Focus one ticket at a time with a persistent action rail",
                        ),
                    ),
                    renderer_state=ReferenceRendererState.ARTIFACT_ONLY,
                ),
            )
        ).next_snapshot
        selected = _advance(reduce_ui_codesign(_advance(reduce_ui_codesign(directions, RequestOwnerSelectionEvent())).next_snapshot, SelectDirectionEvent(exact_candidate_id="direction-a", owner_decision_ref="owner-direction"))).next_snapshot
        sealed = _advance(reduce_ui_codesign(selected, ContextSealedEvent(exact_sealed_regime_ref=_sealed()))).next_snapshot
        contract_ready = _advance(reduce_ui_codesign(sealed, CompileFeatureContractEvent(exact_contract=_contract()))).next_snapshot
        implementation = _advance(reduce_ui_codesign(contract_ready, AdmitImplementationEvent(exact_ticket_ref="ticket-support-queue"))).next_snapshot
        unavailable = reduce_ui_codesign(
            implementation,
            RequestVisualReviewEvent(verification_state=VisualVerificationState.UNAVAILABLE),
        )
        self.assertIsInstance(unavailable, UICodesignWaitDecision)
        if isinstance(unavailable, UICodesignWaitDecision):
            self.assertEqual(UICodesignWaitReason.VISUAL_VERIFICATION_REQUIRED, unavailable.reason)
        review_required = _advance(
            reduce_ui_codesign(
                implementation,
                RequestVisualReviewEvent(
                    verification_state=VisualVerificationState.AVAILABLE,
                    evidence_refs=("screenshot-mobile-success", "screenshot-desktop-success"),
                ),
            )
        ).next_snapshot
        wrong_report = reduce_ui_codesign(review_required, CompleteReviewEvent(exact_report=_report("other-ticket")))
        self.assertIsInstance(wrong_report, UICodesignRefuseDecision)
        evidence_mismatch = reduce_ui_codesign(
            review_required,
            CompleteReviewEvent(
                exact_report=_report(
                    screenshot_refs=("screenshot-other-mobile", "screenshot-other-desktop")
                )
            ),
        )
        self.assertIsInstance(evidence_mismatch, UICodesignRefuseDecision)
        if isinstance(evidence_mismatch, UICodesignRefuseDecision):
            self.assertEqual(UICodesignRefusalReason.EVIDENCE_MISMATCH, evidence_mismatch.reason)
        owner_wait = _advance(reduce_ui_codesign(review_required, CompleteReviewEvent(exact_report=_report()))).next_snapshot
        self.assertEqual(UICodesignState.OWNER_ACCEPTANCE_REQUIRED, owner_wait.state)
        self.assertIsInstance(reduce_ui_codesign(owner_wait, OwnerAcceptEvent(exact_report_id="other-report", owner_decision_ref="owner")), UICodesignRefuseDecision)
        complete = _advance(reduce_ui_codesign(owner_wait, OwnerAcceptEvent(exact_report_id="report-support-queue", owner_decision_ref="owner-acceptance"))).next_snapshot
        self.assertEqual(UICodesignState.COMPLETE, complete.state)

    def test_uix_visual_report_evidence_is_closed_over_declared_sets(self) -> None:
        report = _report()
        matrix = list(report.breakpoint_state_matrix)
        outside_screenshot = matrix[0].model_copy(update={"screenshot_ref": "screenshot-outside"})
        with self.assertRaises(ValidationError):
            VisualReviewReport.model_validate(
                {**report.model_dump(), "breakpoint_state_matrix": (outside_screenshot, matrix[1])}
            )

        outside_finding = VisualFinding(
            finding_id="finding-outside",
            severity=VisualFindingSeverity.MATERIAL,
            dimension="contrast",
            description="Contrast needs review",
            evidence_refs=("screenshot-outside",),
        )
        with self.assertRaises(ValidationError):
            VisualReviewReport.model_validate(
                {**report.model_dump(), "findings": (outside_finding,)}
            )

        outside_digest = matrix[0].model_copy(update={"evidence_digest": "e" * 64})
        with self.assertRaises(ValidationError):
            VisualReviewReport.model_validate(
                {**report.model_dump(), "breakpoint_state_matrix": (outside_digest, matrix[1])}
            )

    def test_ui7_ast_proves_private_no_effect_module(self) -> None:
        import library.workflow_router as package
        import library.workflow_router.ui_codesign_contracts as module

        self.assertNotIn("ui_codesign_contracts", package.__all__)
        package_init = Path(package.__file__).read_bytes() if package.__file__ is not None else b""
        self.assertNotIn(b"ui_codesign_contracts", package_init)
        source = inspect.getsource(module)
        tree = ast.parse(source)
        reducers = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "reduce_ui_codesign"
        ]
        self.assertEqual(1, len(reducers))
        imported = {
            alias.name.split(".", maxsplit=1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            (node.module or "").split(".", maxsplit=1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            if node.module is not None
        )
        self.assertEqual(
            {
                "__future__",
                "re",
                "enum",
                "hashlib",
                "typing",
                "pydantic",
                "contracts",
            },
            imported,
        )
        forbidden_modules = {
            "os", "pathlib", "shutil", "tempfile", "glob", "io", "subprocess", "multiprocessing",
            "socket", "requests", "httpx", "urllib", "http", "ssl", "websocket", "platform", "dotenv",
            "openai", "anthropic", "boto3", "google", "azure", "figma", "imagegen", "browser", "selenium",
            "playwright", "codex", "claude", "git", "dulwich", "importlib", "builtins",
        }
        self.assertTrue(imported.isdisjoint(forbidden_modules))
        forbidden_names = {
            "Any", "cast", "dict", "Mapping", "MutableMapping", "defaultdict", "open", "eval", "exec",
            "getattr", "setattr", "delattr", "globals", "locals", "vars", "spawn_agent", "send_message",
            "wait_agent", "interrupt_agent", "provider", "host_cli", "dynamic_lookup", "raw_mapping",
        }
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue(names.isdisjoint(forbidden_names))
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(calls.isdisjoint(forbidden_names))
        forbidden_attributes = {
            "open", "getattr", "setattr", "subprocess", "socket", "request", "spawn_agent", "send_message",
        }
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        self.assertTrue(attributes.isdisjoint(forbidden_attributes))


if __name__ == "__main__":
    unittest.main()
