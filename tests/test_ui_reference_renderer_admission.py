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


def _rendered() -> RenderedReferenceEvidence:
    return RenderedReferenceEvidence(
        desktop_screenshot_ref="screenshot-desktop",
        mobile_screenshot_ref="screenshot-mobile",
        desktop_digest=DESKTOP_DIGEST,
        mobile_digest=MOBILE_DIGEST,
        renderer_observation_ref="renderer-observation",
    )


def _artifact() -> ArtifactReferenceEvidence:
    return ArtifactReferenceEvidence(
        desktop_artifact_ref="artifact-desktop",
        mobile_artifact_ref="artifact-mobile",
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
        request_ref="request-ui-reference",
        brief_id="brief-ui-dashboard",
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
                evidence=UnavailableReferenceEvidence(),
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
                    evidence=UnavailableReferenceEvidence(),
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
        )
        adapter = _decision_adapter()
        for decision in decisions:
            self.assertEqual(decision, adapter.validate_json(decision.model_dump_json()))

        for capability in RendererCapabilityState:
            self.assertEqual(capability, RendererCapabilityState(capability.value))
        for target in RendererTarget:
            self.assertEqual(target, RendererTarget(target.value))

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

    def test_uir2_authorized_matching_rendered_evidence_is_admitted(self) -> None:
        decision = admit_reference_renderer(_request(evidence=_rendered()))
        self.assertIsInstance(decision, AdmittedRenderedDecision)
        self.assertNotIsInstance(decision, AdmittedArtifactDecision)

        with self.assertRaises(ValidationError):
            RenderedReferenceEvidence.model_validate(
                {**_rendered().model_dump(), "desktop_digest": "not-a-digest"}
            )

    def test_uir3_unauthorized_capability_waits_without_admission(self) -> None:
        decision = admit_reference_renderer(
            _request(capability=RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED)
        )
        self.assertIsInstance(decision, RendererWaitDecision)
        if isinstance(decision, RendererWaitDecision):
            self.assertEqual(RendererWaitReason.DESIGN_CAPABILITY_AUTHORITY_REQUIRED, decision.reason)
        self.assertNotIsInstance(decision, (AdmittedRenderedDecision, AdmittedArtifactDecision))

    def test_uir4_absence_or_decline_uses_artifact_fallback(self) -> None:
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
                    evidence=UnavailableReferenceEvidence(),
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

    def test_uir6_state_duplicate_and_identity_mismatch_refuse(self) -> None:
        state_mismatch = admit_reference_renderer(
            _request(requested_state=ReferenceRendererState.RENDERED_AVAILABLE, evidence=_artifact())
        )
        self.assertIsInstance(state_mismatch, RendererRefusedDecision)
        if isinstance(state_mismatch, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.STATE_EVIDENCE_MISMATCH, state_mismatch.reason)

        duplicate = RenderedReferenceEvidence(
            desktop_screenshot_ref="same-screenshot",
            mobile_screenshot_ref="same-screenshot",
            desktop_digest=DESKTOP_DIGEST,
            mobile_digest=DESKTOP_DIGEST,
            renderer_observation_ref="renderer-observation",
        )
        duplicate_result = admit_reference_renderer(_request(evidence=duplicate))
        self.assertIsInstance(duplicate_result, RendererRefusedDecision)
        if isinstance(duplicate_result, RendererRefusedDecision):
            self.assertEqual(RendererRefusalReason.DUPLICATE_EVIDENCE, duplicate_result.reason)

        with self.assertRaises(ValidationError):
            ReferenceRendererAdmissionRequest.model_validate(
                {**_request(evidence=_rendered()).model_dump(), "approved_content_digest": "bad"}
            )

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
            {"__future__", "enum", "typing", "pydantic", "contracts", "ui_codesign_contracts"},
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
