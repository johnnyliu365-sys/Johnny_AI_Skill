"""Acceptance and reverse-mutation tests for UIX-02 evidence admission."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
import unittest

from pydantic import TypeAdapter, ValidationError

from library.workflow_router.ui_codesign_contracts import ContentDigest, ReferenceRendererState
from library.workflow_router.ui_reference_renderer_admission import (
    AdmittedArtifactDecision,
    AdmittedRenderedDecision,
    ArtifactReferenceEvidence,
    ReferenceEvidenceBinding,
    ReferenceRendererAdmissionDecision,
    ReferenceRendererAdmissionRequest,
    ReferenceRendererEvidence,
    RenderedReferenceEvidence,
    RendererCapabilityState,
    RendererRefusalReason,
    RendererRefusedDecision,
    RendererTarget,
    RendererWaitDecision,
    RendererWaitReason,
    UnavailableReferenceEvidence,
    admit_reference_renderer,
)


DIGEST = "a" * 64
DESKTOP_DIGEST = "b" * 64
MOBILE_DIGEST = "c" * 64
ARTIFACT_SET_DIGEST = "d" * 64


def _binding() -> ReferenceEvidenceBinding:
    return ReferenceEvidenceBinding(
        request_ref="requestuiref",
        brief_id="briefuidashboard",
        approved_content_digest=DIGEST,
    )


def _rendered() -> RenderedReferenceEvidence:
    return RenderedReferenceEvidence(
        binding=_binding(),
        desktop_screenshot_ref="screenshotdesktop",
        mobile_screenshot_ref="screenshotmobile",
        desktop_digest=DESKTOP_DIGEST,
        mobile_digest=MOBILE_DIGEST,
        renderer_observation_ref="rendererobservation",
    )


def _artifact() -> ArtifactReferenceEvidence:
    return ArtifactReferenceEvidence(
        binding=_binding(),
        desktop_artifact_ref="artifactdesktop",
        mobile_artifact_ref="artifactmobile",
        artifact_set_digest=ARTIFACT_SET_DIGEST,
        owner_manual_open_acknowledgement=True,
    )


def _request(
    *,
    capability: RendererCapabilityState = RendererCapabilityState.AVAILABLE_AUTHORIZED,
    target: RendererTarget = RendererTarget.DOM,
    actual_target: RendererTarget = RendererTarget.DOM,
    requested_state: ReferenceRendererState = ReferenceRendererState.RENDERED_AVAILABLE,
    evidence: ReferenceRendererEvidence | None = None,
) -> ReferenceRendererAdmissionRequest:
    if evidence is None:
        evidence = _rendered()
    return ReferenceRendererAdmissionRequest(
        request_ref="requestuiref",
        brief_id="briefuidashboard",
        approved_content_digest=DIGEST,
        capability_state=capability,
        renderer_target=target,
        actual_target=actual_target,
        requested_renderer_state=requested_state,
        evidence=evidence,
    )


def _decision_adapter() -> TypeAdapter[ReferenceRendererAdmissionDecision]:
    return TypeAdapter(ReferenceRendererAdmissionDecision)


_ALLOWED_IMPORTS: dict[tuple[int, str], tuple[str, ...]] = {
    (0, "__future__"): ("annotations",),
    (0, "enum"): ("Enum",),
    (0, "typing"): ("Annotated", "Literal", "Self", "TypeAlias", "Union"),
    (0, "pydantic"): (
        "AfterValidator",
        "ConfigDict",
        "Field",
        "TypeAdapter",
        "field_validator",
        "model_validator",
    ),
    (1, "contracts"): ("RouterModel",),
    (1, "ui_codesign_contracts"): ("ContentDigest", "ReferenceRendererState"),
}
_ALLOWED_CALL_TARGETS = frozenset(
    {
        "AdmittedArtifactDecision",
        "AdmittedRenderedDecision",
        "AfterValidator",
        "ConfigDict",
        "Field",
        "RendererRefusedDecision",
        "RendererWaitDecision",
        "TypeAdapter",
        "ValueError",
        "_evidence_binding_matches_request",
        "_evidence_is_duplicate",
        "_evidence_matches_requested_state",
        "_refuse",
        "_target_matches",
        "_wait",
        "all",
        "any",
        "field_validator",
        "isinstance",
        "len",
        "model_validator",
        "ord",
        "type",
        "_REQUEST_ADAPTER.validate_python",
        "unicodedata.category",
        "value.strip",
    }
)


def _production_source_policy_violations(tree: ast.Module) -> tuple[str, ...]:
    """Validate the closed import/name/call grammar for the production module source."""

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if len(node.names) != 1:
                violations.append("import statement must contain exactly one member")
                continue
            imported = node.names[0]
            if imported.name != "unicodedata" or imported.asname is not None:
                violations.append(f"unlisted or aliased import: {ast.unparse(node)}")
        elif isinstance(node, ast.ImportFrom):
            expected = _ALLOWED_IMPORTS.get((node.level, node.module or ""))
            actual = tuple(alias.name for alias in node.names)
            if expected is None:
                violations.append(f"unlisted import form: {ast.unparse(node)}")
            elif actual != expected or any(alias.asname is not None for alias in node.names):
                violations.append(f"wrong import members or alias: {ast.unparse(node)}")

        if isinstance(node, ast.Name) and node.id.startswith("__"):
            if not (node.id == "__all__" and isinstance(node.ctx, ast.Store)):
                violations.append(f"double-underscore name loaded: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            violations.append(f"double-underscore attribute loaded: {node.attr}")

        if isinstance(node, ast.Call):
            if any(isinstance(argument, ast.Starred) for argument in node.args):
                violations.append("starred call argument")
            if any(keyword.arg is None for keyword in node.keywords):
                violations.append("unpacked call keyword")
            target: str | None = None
            if isinstance(node.func, ast.Name):
                target = node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                target = f"{node.func.value.id}.{node.func.attr}"
            if target not in _ALLOWED_CALL_TARGETS:
                violations.append(f"unlisted call target: {ast.unparse(node.func)}")
    return tuple(violations)


class UIReferenceRendererAdmissionTests(unittest.TestCase):
    def test_uir1_public_variants_strictly_round_trip(self) -> None:
        requests = (
            _request(evidence=_rendered()),
            _request(requested_state=ReferenceRendererState.ARTIFACT_ONLY, evidence=_artifact()),
            _request(
                capability=RendererCapabilityState.UNAVAILABLE,
                requested_state=ReferenceRendererState.UNAVAILABLE,
                evidence=UnavailableReferenceEvidence(binding=_binding()),
            ),
        )
        for request in requests:
            rebuilt = ReferenceRendererAdmissionRequest.model_validate_json(request.model_dump_json())
            self.assertEqual(request, rebuilt)

        decisions: tuple[ReferenceRendererAdmissionDecision, ...] = (
            admit_reference_renderer(_request(evidence=_rendered())),
            admit_reference_renderer(
                _request(
                    capability=RendererCapabilityState.UNAVAILABLE,
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=_artifact(),
                )
            ),
            admit_reference_renderer(
                _request(
                    capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                    evidence=_rendered(),
                )
            ),
            admit_reference_renderer(
                _request(
                    capability=RendererCapabilityState.UNAVAILABLE,
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=UnavailableReferenceEvidence(binding=_binding()),
                )
            ),
            admit_reference_renderer(
                _request(
                    capability=RendererCapabilityState.AVAILABLE_AUTHORIZED,
                    target=RendererTarget.DOM,
                    actual_target=RendererTarget.NATIVE_ENGINE,
                    evidence=_rendered(),
                )
            ),
            RendererRefusedDecision(
                request_ref="requestuiref",
                brief_id="briefuidashboard",
                approved_content_digest=DIGEST,
                reason=RendererRefusalReason.STATE_EVIDENCE_MISMATCH,
            ),
            RendererRefusedDecision(
                request_ref="requestuiref",
                brief_id="briefuidashboard",
                approved_content_digest=DIGEST,
                reason=RendererRefusalReason.CONTENT_BINDING_MISMATCH,
            ),
            RendererRefusedDecision(
                request_ref="requestuiref",
                brief_id="briefuidashboard",
                approved_content_digest=DIGEST,
                reason=RendererRefusalReason.DUPLICATE_EVIDENCE,
            ),
        )
        adapter = _decision_adapter()
        for decision in decisions:
            self.assertEqual(decision, adapter.validate_json(decision.model_dump_json()))

        for capability in RendererCapabilityState:
            self.assertEqual(capability, RendererCapabilityState(capability.value))
        for target in RendererTarget:
            self.assertEqual(target, RendererTarget(target.value))
        for renderer_state in ReferenceRendererState:
            self.assertEqual(renderer_state, ReferenceRendererState(renderer_state.value))
        for wait_reason in RendererWaitReason:
            self.assertEqual(wait_reason, RendererWaitReason(wait_reason.value))
        for refusal_reason in RendererRefusalReason:
            self.assertEqual(refusal_reason, RendererRefusalReason(refusal_reason.value))

        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {
                    **_request(evidence=_rendered()).model_dump(),
                    "evidence": {"kind": "RENDERED_AVAILABLE", "desktop_screenshot_ref": "bad"},
                }
            )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request(evidence=_rendered()).model_dump(), "password=secret": "bad"}
            )
        with self.assertRaises(ValidationError):
            ArtifactReferenceEvidence.model_validate(
                {**_artifact().model_dump(), "owner_manual_open_acknowledgement": False}
            )
        for invalid_acknowledgement in (None, 1, 1.0, "true"):
            with self.subTest(acknowledgement=repr(invalid_acknowledgement)):
                with self.assertRaises(ValidationError):
                    ArtifactReferenceEvidence.model_validate(
                        {
                            **_artifact().model_dump(),
                            "owner_manual_open_acknowledgement": invalid_acknowledgement,
                        }
                    )
        missing_acknowledgement = _artifact().model_dump()
        del missing_acknowledgement["owner_manual_open_acknowledgement"]
        with self.assertRaises(ValidationError):
            ArtifactReferenceEvidence.model_validate(missing_acknowledgement)
        nested_missing_acknowledgement = _request(
            requested_state=ReferenceRendererState.ARTIFACT_ONLY,
            evidence=_artifact(),
        ).model_dump()
        del nested_missing_acknowledgement["evidence"]["owner_manual_open_acknowledgement"]
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(nested_missing_acknowledgement)
        for invalid_nested_acknowledgement in (False, None, 1, 1.0, "true"):
            with self.subTest(nested_acknowledgement=repr(invalid_nested_acknowledgement)):
                nested_acknowledgement = _request(
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=_artifact(),
                ).model_dump()
                nested_acknowledgement["evidence"]["owner_manual_open_acknowledgement"] = (
                    invalid_nested_acknowledgement
                )
                with self.assertRaises(ValidationError):
                    ReferenceRendererAdmissionRequest.model_validate(nested_acknowledgement)
        with self.assertRaises(ValidationError):
            _request(actual_target=RendererTarget.ANY)

        unicode_identifier = "éab"
        unicode_request = ReferenceRendererAdmissionRequest(
            request_ref=unicode_identifier,
            brief_id="briefuidashboard",
            approved_content_digest=DIGEST,
            capability_state=RendererCapabilityState.AVAILABLE_AUTHORIZED,
            renderer_target=RendererTarget.DOM,
            actual_target=RendererTarget.DOM,
            requested_renderer_state=ReferenceRendererState.RENDERED_AVAILABLE,
            evidence=RenderedReferenceEvidence(
                binding=ReferenceEvidenceBinding(
                    request_ref=unicode_identifier,
                    brief_id="briefuidashboard",
                    approved_content_digest=DIGEST,
                ),
                desktop_screenshot_ref="screenshotdesktop",
                mobile_screenshot_ref="screenshotmobile",
                desktop_digest=DESKTOP_DIGEST,
                mobile_digest=MOBILE_DIGEST,
                renderer_observation_ref="rendererobservation",
            ),
        )
        self.assertEqual(
            unicode_request,
            ReferenceRendererAdmissionRequest.model_validate_json(unicode_request.model_dump_json()),
        )
        self.assertEqual(unicode_identifier, unicode_request.request_ref)
        self.assertEqual((0xE9, 0x61, 0x62), tuple(map(ord, unicode_request.request_ref)))
        for invalid_category_identifier in (
            "\u034f" * 3,
            "\ufe0f" * 3,
            "e\u0301e",
            "abc-def",
            "abc_def",
            "abc.def",
            "abc@example",
        ):
            with self.subTest(identifier=invalid_category_identifier.encode("unicode_escape").decode()):
                with self.assertRaises(ValidationError):
                    ReferenceRendererAdmissionRequest.model_validate(
                        {**_request().model_dump(), "request_ref": invalid_category_identifier}
                    )
        for short_identifier in ("a", "ab"):
            with self.subTest(identifier=short_identifier):
                with self.assertRaises(ValidationError):
                    ReferenceRendererAdmissionRequest.model_validate(
                        {**_request().model_dump(), "request_ref": short_identifier}
                    )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request().model_dump(), "request_ref": "requestuiref "}
            )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request().model_dump(), "request_ref": None}
            )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request().model_dump(), "request_ref": 17}
            )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request().model_dump(), "request_ref": "request-\nref"}
            )
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request().model_dump(), "request_ref": "x" * 129}
            )
        for unsafe_value in (
            "mailto:owner@example.test",
            "javascript:alert(1)",
            "authorization:bearer-token",
            "prompt injection",
            "C:drive-relative",
            "access_token=abc",
            "Authorization Bearer abc",
            "api-key=abc",
            "ignore previous instructions",
        ):
            with self.subTest(identifier=unsafe_value):
                with self.assertRaises(ValidationError):
                    ReferenceRendererAdmissionRequest.model_validate(
                        {**_request().model_dump(), "request_ref": unsafe_value}
                    )
        alias_payload = _request().model_dump()
        del alias_payload["renderer_target"]
        alias_payload["declared_renderer_target"] = RendererTarget.DOM
        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(alias_payload)
        acknowledgement_alias = _artifact().model_dump()
        del acknowledgement_alias["owner_manual_open_acknowledgement"]
        acknowledgement_alias["owner_manual_open_acknowledged"] = True
        with self.assertRaises(ValidationError):
            ArtifactReferenceEvidence.model_validate(acknowledgement_alias)

        self.assertEqual(_binding(), ReferenceEvidenceBinding.model_validate_json(_binding().model_dump_json()))
        for evidence in (_rendered(), _artifact(), UnavailableReferenceEvidence(binding=_binding())):
            self.assertEqual(evidence, type(evidence).model_validate_json(evidence.model_dump_json()))

        for field_name in (
            "desktop_screenshot_ref",
            "mobile_screenshot_ref",
            "desktop_digest",
            "mobile_digest",
            "renderer_observation_ref",
        ):
            with self.subTest(missing_rendered_field=field_name):
                rendered_payload = _rendered().model_dump()
                del rendered_payload[field_name]
                with self.assertRaises(ValidationError):
                    RenderedReferenceEvidence.model_validate(rendered_payload)
        for field_name in (
            "desktop_artifact_ref",
            "mobile_artifact_ref",
            "artifact_set_digest",
            "owner_manual_open_acknowledgement",
        ):
            with self.subTest(missing_artifact_field=field_name):
                artifact_payload = _artifact().model_dump()
                del artifact_payload[field_name]
                with self.assertRaises(ValidationError):
                    ArtifactReferenceEvidence.model_validate(artifact_payload)

    def test_uir2_authorized_matching_rendered_evidence_is_admitted(self) -> None:
        decision = admit_reference_renderer(_request(evidence=_rendered()))
        self.assertIsInstance(decision, AdmittedRenderedDecision)
        self.assertNotIsInstance(decision, AdmittedArtifactDecision)

        authorized_artifact = admit_reference_renderer(
            _request(
                requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                evidence=_artifact(),
            )
        )
        self.assertIsInstance(authorized_artifact, RendererRefusedDecision)
        if isinstance(authorized_artifact, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, authorized_artifact.reason)

        with self.assertRaises(ValidationError):
            RenderedReferenceEvidence.model_validate(
                {**_rendered().model_dump(), "desktop_digest": "not-a-digest"}
            )

        authorized_unavailable = admit_reference_renderer(
            _request(
                requested_state=ReferenceRendererState.UNAVAILABLE,
                evidence=UnavailableReferenceEvidence(binding=_binding()),
            )
        )
        self.assertIsInstance(authorized_unavailable, RendererRefusedDecision)
        if isinstance(authorized_unavailable, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, authorized_unavailable.reason)

    def test_uir3_unauthorized_capability_waits_without_admission(self) -> None:
        evidence_cases = (
            (
                "rendered",
                ReferenceRendererState.RENDERED_AVAILABLE,
                _rendered(),
            ),
            (
                "artifact",
                ReferenceRendererState.ARTIFACT_ONLY,
                _artifact(),
            ),
            (
                "unavailable",
                ReferenceRendererState.UNAVAILABLE,
                UnavailableReferenceEvidence(binding=_binding()),
            ),
        )
        for label, requested_state, evidence in evidence_cases:
            with self.subTest(evidence=label):
                decision = admit_reference_renderer(
                    _request(
                        capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                        requested_state=requested_state,
                        evidence=evidence,
                    )
                )
                self.assertIsInstance(decision, RendererWaitDecision)
                if isinstance(decision, RendererWaitDecision):
                    self.assertEqual(RendererWaitReason.DESIGN_CAPABILITY_AUTHORITY_REQUIRED, decision.reason)
                self.assertNotIsInstance(decision, (AdmittedRenderedDecision, AdmittedArtifactDecision))

        authority_order_cases = (
            (
                "binding-before-authority",
                _request(
                    capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                    evidence=RenderedReferenceEvidence(
                        binding=ReferenceEvidenceBinding(
                            request_ref="requestother",
                            brief_id="briefuidashboard",
                            approved_content_digest=DIGEST,
                        ),
                        desktop_screenshot_ref="screenshotdesktop",
                        mobile_screenshot_ref="screenshotmobile",
                        desktop_digest=DESKTOP_DIGEST,
                        mobile_digest=MOBILE_DIGEST,
                        renderer_observation_ref="rendererobservation",
                    ),
                ),
            ),
            (
                "duplicate-before-authority",
                _request(
                    capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                    evidence=RenderedReferenceEvidence(
                        binding=_binding(),
                        desktop_screenshot_ref="samescreenshot",
                        mobile_screenshot_ref="samescreenshot",
                        desktop_digest=DESKTOP_DIGEST,
                        mobile_digest=MOBILE_DIGEST,
                        renderer_observation_ref="rendererobservation",
                    ),
                ),
            ),
            (
                "target-before-authority",
                _request(
                    capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                    target=RendererTarget.DOM,
                    actual_target=RendererTarget.NATIVE_ENGINE,
                    evidence=_rendered(),
                ),
            ),
            (
                "state-before-authority",
                _request(
                    capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED,
                    requested_state=ReferenceRendererState.RENDERED_AVAILABLE,
                    evidence=_artifact(),
                ),
            ),
        )
        for label, request in authority_order_cases:
            with self.subTest(ordering=label):
                decision = admit_reference_renderer(request)
                self.assertIsInstance(decision, RendererWaitDecision)
                if isinstance(decision, RendererWaitDecision):
                    self.assertEqual(RendererWaitReason.DESIGN_CAPABILITY_AUTHORITY_REQUIRED, decision.reason)

    def test_uir4_absence_or_decline_uses_artifact_fallback(self) -> None:
        authorized_artifact = admit_reference_renderer(
            _request(
                requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                evidence=_artifact(),
            )
        )
        self.assertIsInstance(authorized_artifact, RendererRefusedDecision)
        if isinstance(authorized_artifact, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, authorized_artifact.reason)

        missing_acknowledgement = _artifact().model_dump()
        del missing_acknowledgement["owner_manual_open_acknowledgement"]
        with self.subTest(acknowledgement="missing-direct"):
            with self.assertRaises(ValidationError):
                ArtifactReferenceEvidence.model_validate(missing_acknowledgement)
        nested_missing_acknowledgement = _request(
            requested_state=ReferenceRendererState.ARTIFACT_ONLY,
            evidence=_artifact(),
        ).model_dump()
        del nested_missing_acknowledgement["evidence"]["owner_manual_open_acknowledgement"]
        with self.subTest(acknowledgement="missing-nested"):
            with self.assertRaises(ValidationError):
                ReferenceRendererAdmissionRequest.model_validate(nested_missing_acknowledgement)
        for invalid_acknowledgement in (False, None, 1, 1.0, "true"):
            with self.subTest(acknowledgement=repr(invalid_acknowledgement)):
                invalid_payload = _artifact().model_dump()
                invalid_payload["owner_manual_open_acknowledgement"] = invalid_acknowledgement
                with self.assertRaises(ValidationError):
                    ArtifactReferenceEvidence.model_validate(invalid_payload)

                nested_invalid_payload = _request(
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=_artifact(),
                ).model_dump()
                nested_invalid_payload["evidence"]["owner_manual_open_acknowledgement"] = (
                    invalid_acknowledgement
                )
                with self.assertRaises(ValidationError):
                    ReferenceRendererAdmissionRequest.model_validate(nested_invalid_payload)

        for capability in (
            RendererCapabilityState.UNAVAILABLE,
            RendererCapabilityState.DECLINED,
        ):
            decision = admit_reference_renderer(
                _request(
                    capability=capability,
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=_artifact(),
                )
            )
            self.assertIsInstance(decision, AdmittedArtifactDecision)
            if isinstance(decision, AdmittedArtifactDecision):
                self.assertIs(decision.evidence.owner_manual_open_acknowledgement, True)

            wait = admit_reference_renderer(
                _request(
                    capability=capability,
                    requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                    evidence=UnavailableReferenceEvidence(binding=_binding()),
                )
            )
            self.assertIsInstance(wait, RendererWaitDecision)
            if isinstance(wait, RendererWaitDecision):
                self.assertEqual(RendererWaitReason.UI_REFERENCE_RENDERER_REQUIRED, wait.reason)

    def test_uir5_target_mismatch_and_any_target(self) -> None:
        mismatch = admit_reference_renderer(
            _request(
                target=RendererTarget.DOM,
                actual_target=RendererTarget.NATIVE_ENGINE,
                evidence=_rendered(),
            )
        )
        self.assertIsInstance(mismatch, RendererRefusedDecision)
        if isinstance(mismatch, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.TARGET_MISMATCH, mismatch.reason)
        artifact_mismatch = admit_reference_renderer(
            _request(
                capability=RendererCapabilityState.UNAVAILABLE,
                requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                target=RendererTarget.DOM,
                actual_target=RendererTarget.NATIVE_MOBILE,
                evidence=_artifact(),
            )
        )
        self.assertIsInstance(artifact_mismatch, RendererRefusedDecision)
        if isinstance(artifact_mismatch, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.TARGET_MISMATCH, artifact_mismatch.reason)

        finite_targets = (
            RendererTarget.DOM,
            RendererTarget.NATIVE_ENGINE,
            RendererTarget.NATIVE_MOBILE,
            RendererTarget.TERMINAL,
        )
        for actual_target in finite_targets:
            with self.subTest(rendered_any_target=actual_target):
                any_target = admit_reference_renderer(
                    _request(target=RendererTarget.ANY, actual_target=actual_target, evidence=_rendered())
                )
                self.assertIsInstance(any_target, AdmittedRenderedDecision)

        for actual_target in finite_targets:
            with self.subTest(artifact_any_target=actual_target):
                any_artifact = admit_reference_renderer(
                    _request(
                        capability=RendererCapabilityState.UNAVAILABLE,
                        target=RendererTarget.ANY,
                        actual_target=actual_target,
                        requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                        evidence=_artifact(),
                    )
                )
                self.assertIsInstance(any_artifact, AdmittedArtifactDecision)

        unavailable_target = admit_reference_renderer(
            _request(
                capability=RendererCapabilityState.UNAVAILABLE,
                target=RendererTarget.DOM,
                actual_target=RendererTarget.NATIVE_ENGINE,
                requested_state=ReferenceRendererState.UNAVAILABLE,
                evidence=UnavailableReferenceEvidence(binding=_binding()),
            )
        )
        self.assertIsInstance(unavailable_target, RendererWaitDecision)

        authorized_artifact_wait = admit_reference_renderer(
            _request(
                requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                evidence=UnavailableReferenceEvidence(binding=_binding()),
            )
        )
        self.assertIsInstance(authorized_artifact_wait, RendererRefusedDecision)
        if isinstance(authorized_artifact_wait, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, authorized_artifact_wait.reason)

    def test_uir6_state_duplicate_and_identity_mismatch_refuse(self) -> None:
        state_mismatch_cases = (
            (
                "rendered-request-artifact-evidence",
                _request(requested_state=ReferenceRendererState.RENDERED_AVAILABLE, evidence=_artifact()),
            ),
            (
                "rendered-request-unavailable-evidence",
                _request(
                    requested_state=ReferenceRendererState.RENDERED_AVAILABLE,
                    evidence=UnavailableReferenceEvidence(binding=_binding()),
                ),
            ),
            (
                "artifact-request-rendered-evidence",
                _request(requested_state=ReferenceRendererState.ARTIFACT_ONLY, evidence=_rendered()),
            ),
            (
                "unavailable-request-rendered-evidence",
                _request(requested_state=ReferenceRendererState.UNAVAILABLE, evidence=_rendered()),
            ),
            (
                "unavailable-request-artifact-evidence",
                _request(requested_state=ReferenceRendererState.UNAVAILABLE, evidence=_artifact()),
            ),
        )
        for label, request in state_mismatch_cases:
            with self.subTest(state_pair=label):
                state_mismatch = admit_reference_renderer(request)
                self.assertIsInstance(state_mismatch, RendererRefusedDecision)
                if isinstance(state_mismatch, RendererRefusedDecision):
                    self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, state_mismatch.reason)

        artifact_unavailable_wait = admit_reference_renderer(
            _request(
                capability=RendererCapabilityState.UNAVAILABLE,
                requested_state=ReferenceRendererState.ARTIFACT_ONLY,
                evidence=UnavailableReferenceEvidence(binding=_binding()),
            )
        )
        self.assertIsInstance(artifact_unavailable_wait, RendererWaitDecision)

        duplicate_cases = (
            (
                "rendered-screenshot-reference",
                RenderedReferenceEvidence(
                    binding=_binding(),
                    desktop_screenshot_ref="samescreenshot",
                    mobile_screenshot_ref="samescreenshot",
                    desktop_digest=DESKTOP_DIGEST,
                    mobile_digest=MOBILE_DIGEST,
                    renderer_observation_ref="rendererobservation",
                ),
            ),
            (
                "rendered-digest",
                RenderedReferenceEvidence(
                    binding=_binding(),
                    desktop_screenshot_ref="screenshotdesktop",
                    mobile_screenshot_ref="screenshotmobile",
                    desktop_digest=DESKTOP_DIGEST,
                    mobile_digest=DESKTOP_DIGEST,
                    renderer_observation_ref="rendererobservation",
                ),
            ),
            (
                "rendered-desktop-observation-reference",
                RenderedReferenceEvidence(
                    binding=_binding(),
                    desktop_screenshot_ref="rendererobservation",
                    mobile_screenshot_ref="screenshotmobile",
                    desktop_digest=DESKTOP_DIGEST,
                    mobile_digest=MOBILE_DIGEST,
                    renderer_observation_ref="rendererobservation",
                ),
            ),
            (
                "rendered-mobile-observation-reference",
                RenderedReferenceEvidence(
                    binding=_binding(),
                    desktop_screenshot_ref="screenshotdesktop",
                    mobile_screenshot_ref="rendererobservation",
                    desktop_digest=DESKTOP_DIGEST,
                    mobile_digest=MOBILE_DIGEST,
                    renderer_observation_ref="rendererobservation",
                ),
            ),
            (
                "artifact-reference",
                ArtifactReferenceEvidence(
                    binding=_binding(),
                    desktop_artifact_ref="samescreenshot",
                    mobile_artifact_ref="samescreenshot",
                    artifact_set_digest=ARTIFACT_SET_DIGEST,
                    owner_manual_open_acknowledgement=True,
                ),
            ),
        )
        for label, duplicate in duplicate_cases:
            with self.subTest(duplicate_dimension=label):
                duplicate_result = admit_reference_renderer(
                    _request(
                        requested_state=(
                            ReferenceRendererState.ARTIFACT_ONLY
                            if isinstance(duplicate, ArtifactReferenceEvidence)
                            else ReferenceRendererState.RENDERED_AVAILABLE
                        ),
                        capability=(
                            RendererCapabilityState.UNAVAILABLE
                            if isinstance(duplicate, ArtifactReferenceEvidence)
                            else RendererCapabilityState.AVAILABLE_AUTHORIZED
                        ),
                        evidence=duplicate,
                    )
                )
                self.assertIsInstance(duplicate_result, RendererRefusedDecision)
                if isinstance(duplicate_result, RendererRefusedDecision):
                    self.assertEqual(RendererRefusalReason.DUPLICATE_EVIDENCE, duplicate_result.reason)

        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request(evidence=_rendered()).model_dump(), "approved_content_digest": "bad"}
            )

        mismatched_binding = RenderedReferenceEvidence(
            binding=ReferenceEvidenceBinding(
                request_ref="requestother",
                brief_id="briefuidashboard",
                approved_content_digest=DIGEST,
            ),
            desktop_screenshot_ref="screenshotdesktop",
            mobile_screenshot_ref="screenshotmobile",
            desktop_digest=DESKTOP_DIGEST,
            mobile_digest=MOBILE_DIGEST,
            renderer_observation_ref="rendererobservation",
        )
        binding_result = admit_reference_renderer(_request(evidence=mismatched_binding))
        self.assertIsInstance(binding_result, RendererRefusedDecision)
        if isinstance(binding_result, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.CONTENT_BINDING_MISMATCH, binding_result.reason)

        changed_digest = RenderedReferenceEvidence(
            binding=ReferenceEvidenceBinding(
                request_ref="requestuiref",
                brief_id="briefuidashboard",
                approved_content_digest="e" * 64,
            ),
            desktop_screenshot_ref="screenshotdesktop",
            mobile_screenshot_ref="screenshotmobile",
            desktop_digest=DESKTOP_DIGEST,
            mobile_digest=MOBILE_DIGEST,
            renderer_observation_ref="rendererobservation",
        )
        changed_digest_result = admit_reference_renderer(_request(evidence=changed_digest))
        self.assertIsInstance(changed_digest_result, RendererRefusedDecision)
        if isinstance(changed_digest_result, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.CONTENT_BINDING_MISMATCH, changed_digest_result.reason)

        changed_brief = RenderedReferenceEvidence(
            binding=ReferenceEvidenceBinding(
                request_ref="requestuiref",
                brief_id="briefother",
                approved_content_digest=DIGEST,
            ),
            desktop_screenshot_ref="screenshotdesktop",
            mobile_screenshot_ref="screenshotmobile",
            desktop_digest=DESKTOP_DIGEST,
            mobile_digest=MOBILE_DIGEST,
            renderer_observation_ref="rendererobservation",
        )
        changed_brief_result = admit_reference_renderer(_request(evidence=changed_brief))
        self.assertIsInstance(changed_brief_result, RendererRefusedDecision)
        if isinstance(changed_brief_result, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.CONTENT_BINDING_MISMATCH, changed_brief_result.reason)

    def test_uir7_ast_proves_private_no_effect_boundary(self) -> None:
        import library.workflow_router as package
        import library.workflow_router.ui_reference_renderer_admission as module

        self.assertNotIn("ui_reference_renderer_admission", package.__all__)
        package_init = Path(package.__file__).read_bytes() if package.__file__ is not None else b""
        self.assertNotIn(b"ui_reference_renderer_admission", package_init)
        tree = ast.parse(inspect.getsource(module))
        reducers = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "admit_reference_renderer"
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
        self.assertEqual((), _production_source_policy_violations(tree))
        forbidden_modules = {
            "os", "pathlib", "shutil", "tempfile", "glob", "io", "subprocess", "multiprocessing",
            "socket", "requests", "httpx", "urllib", "http", "ssl", "websocket", "platform", "dotenv",
            "openai", "anthropic", "boto3", "google", "azure", "figma", "imagegen", "browser", "selenium",
            "playwright", "codex", "claude", "git", "dulwich", "importlib", "builtins",
        }
        self.assertTrue(imported.isdisjoint(forbidden_modules))
        forbidden_names = {
            "Any", "cast", "dict", "Mapping", "MutableMapping", "defaultdict", "open", "eval", "exec",
            "__import__", "getattr", "setattr", "delattr", "globals", "locals", "vars", "spawn_agent", "send_message",
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
        dynamic_calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if isinstance(function, ast.Name) and function.id in forbidden_names:
                dynamic_calls.append(ast.unparse(function))
            elif isinstance(function, ast.Attribute) and function.attr in forbidden_names:
                dynamic_calls.append(ast.unparse(function))
            elif isinstance(function, ast.Attribute) and isinstance(function.value, ast.Call):
                dynamic_calls.append(ast.unparse(function))
        self.assertEqual([], dynamic_calls)

        hostile_snippets = (
            (
                "typing-module-alias",
                "import typing as typing_alias\ntyping_alias.Any(\"opaque\")",
            ),
            (
                "aliased-typing-cast",
                "from typing import cast as unchecked_cast\nunchecked_cast(\"opaque\")",
            ),
            (
                "ordinary-any-alias",
                "from typing import Any as UnsafeAny\nvalue: UnsafeAny",
            ),
            (
                "ordinary-any-second-alias",
                "from typing import Any as A\nfrom typing import Any as AnotherAny\nvalue: A",
            ),
            (
                "ordinary-any",
                "from typing import Any\nvalue: Any",
            ),
            (
                "direct-builtins-import",
                '__builtins__["__import__"]("os")',
            ),
            (
                "indirect-builtins-import",
                'import builtins as runtime\nruntime.__import__("os")',
            ),
            (
                "attribute-on-call-result",
                'factory().run("opaque")',
            ),
            (
                "star-import",
                "from typing import *",
            ),
            (
                "unlisted-module",
                "import pathlib",
            ),
            (
                "unlisted-symbol",
                "from typing import cast",
            ),
            (
                "wrong-relative-level",
                "from ..contracts import RouterModel",
            ),
            (
                "aliased-unicodedata",
                "import unicodedata as unicode_data",
            ),
            (
                "starred-call-argument",
                "len(*values)",
            ),
            (
                "unpacked-call-keyword",
                "ValueError(**details)",
            ),
            (
                "unknown-callee",
                'mystery("opaque")',
            ),
        )
        for label, snippet in hostile_snippets:
            with self.subTest(hostile_source=label):
                violations = _production_source_policy_violations(ast.parse(snippet))
                self.assertNotEqual((), violations)
        self.assertEqual((), _production_source_policy_violations(ast.parse("__all__ = ['private']")))


if __name__ == "__main__":
    unittest.main()
