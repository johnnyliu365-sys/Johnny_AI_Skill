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
            with self.assertRaises(ValidationError):
                ReferenceRendererAdmissionRequest.model_validate(
                    {**_request().model_dump(), "request_ref": invalid_category_identifier}
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
        decision = admit_reference_renderer(
            _request(capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED)
        )
        self.assertIsInstance(decision, RendererWaitDecision)
        if isinstance(decision, RendererWaitDecision):
            self.assertEqual(RendererWaitReason.DESIGN_CAPABILITY_AUTHORITY_REQUIRED, decision.reason)
        self.assertNotIsInstance(decision, (AdmittedRenderedDecision, AdmittedArtifactDecision))

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

        any_target = admit_reference_renderer(
            _request(target=RendererTarget.ANY, actual_target=RendererTarget.TERMINAL, evidence=_rendered())
        )
        self.assertIsInstance(any_target, AdmittedRenderedDecision)

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
        state_mismatch = admit_reference_renderer(
            _request(requested_state=ReferenceRendererState.RENDERED_AVAILABLE, evidence=_artifact())
        )
        self.assertIsInstance(state_mismatch, RendererRefusedDecision)
        if isinstance(state_mismatch, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, state_mismatch.reason)

        duplicate = RenderedReferenceEvidence(
            binding=_binding(),
            desktop_screenshot_ref="samescreenshot",
            mobile_screenshot_ref="samescreenshot",
            desktop_digest=DESKTOP_DIGEST,
            mobile_digest=DESKTOP_DIGEST,
            renderer_observation_ref="rendererobservation",
        )
        duplicate_result = admit_reference_renderer(_request(evidence=duplicate))
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
        self.assertEqual(
            {
                "__future__",
                "enum",
                "typing",
                "unicodedata",
                "pydantic",
                "contracts",
                "ui_codesign_contracts",
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


if __name__ == "__main__":
    unittest.main()
