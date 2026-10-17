"""Focused service-level checks; public-entry behavior remains in router tests."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router.contracts import (
    AuthorityState,
    EvidenceDigest,
    OpaqueMetadataId,
    ProcessStage,
    RevisionDigest,
    SharedContextAccessDecision,
    SharedContextAccessRequest,
    SharedContextActorRole,
    SharedContextContentManifest,
    SharedContextLifecycle,
    SharedContextMutationDecision,
    SharedContextOperation,
    SharedContextState,
)
from library.workflow_router.profile import ProjectWorkflowProfile, build_router_poc_profile
from library.workflow_router.shared_context_service import SharedContextAccessService


class SharedContextAccessServiceTests(unittest.TestCase):
    _revision = "rev-973a99e6b2ce604f"
    _digest = "sha256_973a99e6b2ce604f31560f8e193440b3f18baa8845e97b8363d144e95feb85ef"

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.service = SharedContextAccessService()
        self.manifest = SharedContextContentManifest(
            revision="rev-0123456789abcdef",
            content_digest=(
                "sha256_0123456789abcdef0123456789abcdef"
                "0123456789abcdef0123456789abcdef"
            ),
            stable_fact_refs=("fact-current",),
        )

    def _manifest(
        self,
        *,
        revision: RevisionDigest = "rev-0123456789abcdef",
        content_digest: EvidenceDigest = (
            "sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        ),
        suffix: str = "one",
    ) -> SharedContextContentManifest:
        return SharedContextContentManifest(
            revision=revision,
            content_digest=content_digest,
            stable_fact_refs=(f"fact-{suffix}",),
            invariant_boundary_refs=(f"boundary-{suffix}",),
            artifact_index_refs=(f"artifact-{suffix}",),
        )

    def _state(
        self,
        lifecycle: SharedContextLifecycle,
        *,
        revision: RevisionDigest | None = None,
        content_digest: EvidenceDigest | None = None,
    ) -> SharedContextState:
        return SharedContextState(
            context_ref="ctx-shared-project",
            lifecycle=lifecycle,
            revision=revision,
            content_digest=content_digest,
        )

    def _request(
        self,
        operation: SharedContextOperation,
        process_stage: ProcessStage,
        *,
        actor_role: SharedContextActorRole = SharedContextActorRole.ARCHITECTURE_OWNER,
        actor_capability_ref: OpaqueMetadataId = "cap-architecture-owner",
        expected_current_revision: RevisionDigest | None = None,
        candidate_manifest: SharedContextContentManifest | None = None,
        change_authority_state: AuthorityState = AuthorityState.NOT_REQUIRED,
        approved_change_ref: OpaqueMetadataId | None = None,
    ) -> SharedContextAccessRequest:
        return SharedContextAccessRequest(
            request_ref="request-shared-context",
            context_ref="ctx-shared-project",
            operation=operation,
            process_stage=process_stage,
            actor_role=actor_role,
            actor_capability_ref=actor_capability_ref,
            expected_current_revision=expected_current_revision,
            candidate_manifest=candidate_manifest,
            change_authority_state=change_authority_state,
            approved_change_ref=approved_change_ref,
        )

    def test_shared_context_contracts_round_trip_and_reject_operation_matrix(self) -> None:
        manifest = self._manifest()
        absent = self._state(SharedContextLifecycle.ABSENT)
        create = self._request(
            operation=SharedContextOperation.CREATE_DRAFT,
            process_stage=ProcessStage.ARCHITECTURE,
            candidate_manifest=manifest,
        )
        decision = SharedContextAccessDecision(
            request_ref=create.request_ref,
            context_ref=create.context_ref,
            operation=create.operation,
            decision=SharedContextMutationDecision.ALLOW,
            resulting_state=absent,
        )
        self.assertEqual(
            manifest,
            SharedContextContentManifest.model_validate_json(manifest.model_dump_json()),
        )
        self.assertEqual(
            absent,
            SharedContextState.model_validate_json(absent.model_dump_json()),
        )
        self.assertEqual(
            create,
            SharedContextAccessRequest.model_validate_json(create.model_dump_json()),
        )
        self.assertEqual(
            decision,
            SharedContextAccessDecision.model_validate_json(decision.model_dump_json()),
        )

        operation_payloads = {
            SharedContextOperation.CREATE_DRAFT: create.model_dump(),
            SharedContextOperation.REVISE_DRAFT: self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=self._manifest(
                    revision="rev-1123456789abcdef",
                    content_digest=(
                        "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
                    ),
                    suffix="two",
                ),
            ).model_dump(),
            SharedContextOperation.SEAL: self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
            ).model_dump(),
            SharedContextOperation.READ_REFERENCE: self._request(
                operation=SharedContextOperation.READ_REFERENCE,
                process_stage=ProcessStage.REVIEW,
                expected_current_revision=manifest.revision,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
            ).model_dump(),
        }
        for operation, payload in operation_payloads.items():
            with self.subTest(operation=operation, invalid="missing"):
                missing = dict(payload)
                missing.pop("candidate_manifest", None)
                missing.pop("expected_current_revision", None)
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(missing)
            with self.subTest(operation=operation, invalid="extra"):
                extra = dict(payload)
                extra["progress_refs"] = ("progress-ref",)
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(extra)
            with self.subTest(operation=operation, invalid="wrong_operation"):
                wrong_operation = dict(payload)
                wrong_operation["operation"] = "unsupported"
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(wrong_operation)

        create_wrong = create.model_dump()
        create_wrong["expected_current_revision"] = manifest.revision
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(create_wrong)
        create_wrong = create.model_dump()
        create_wrong["change_authority_state"] = AuthorityState.APPROVED
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(create_wrong)
        revise_payload = operation_payloads[SharedContextOperation.REVISE_DRAFT]
        revise_wrong = dict(revise_payload)
        revise_wrong["candidate_manifest"] = None
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(revise_wrong)
        seal_payload = operation_payloads[SharedContextOperation.SEAL]
        seal_wrong = dict(seal_payload)
        seal_wrong["candidate_manifest"] = manifest
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(seal_wrong)
        read_wrong = dict(operation_payloads[SharedContextOperation.READ_REFERENCE])
        read_wrong["approved_change_ref"] = "change-approved"
        with self.assertRaises(ValidationError):
            SharedContextAccessRequest.model_validate(read_wrong)

    def test_shared_context_manifest_and_state_are_metadata_only(self) -> None:
        manifest = self._manifest()
        invalid_manifests = (
            {"revision": self._revision, "content_digest": self._digest},
            {
                **manifest.model_dump(),
                "revision": "rev-0000000000000000",
            },
            {
                **manifest.model_dump(),
                "content_digest": "sha256_0000000000000000000000000000000000000000000000000000000000000000",
            },
            {
                **manifest.model_dump(),
                "artifact_index_refs": manifest.stable_fact_refs,
            },
            {
                **manifest.model_dump(),
                "progress_refs": ("progress-ref",),
            },
            {
                **manifest.model_dump(),
                "raw_text": "not metadata",
            },
            {
                **manifest.model_dump(),
                "uri": "file://outside",
            },
            {
                **manifest.model_dump(),
                "stable_fact_refs": ("prompt-ref",),
            },
            {
                **manifest.model_dump(),
                "stable_fact_refs": ("secret-ref",),
            },
        )
        for payload in invalid_manifests:
            with self.assertRaises(ValidationError):
                SharedContextContentManifest.model_validate(payload)

        with self.assertRaises(ValidationError):
            self._state(
                lifecycle=SharedContextLifecycle.ABSENT,
                revision=manifest.revision,
            )
        with self.assertRaises(ValidationError):
            self._state(
                lifecycle=SharedContextLifecycle.ARCHITECTURE_DRAFT,
                content_digest=manifest.content_digest,
            )
        with self.assertRaises(ValidationError):
            SharedContextState.model_validate(
                {
                    "context_ref": "ctx-shared-project",
                    "lifecycle": SharedContextLifecycle.SEALED,
                    "revision": "rev-0000000000000000",
                    "content_digest": manifest.content_digest,
                }
            )

    def test_shared_context_profile_accepts_distinct_project_metadata(self) -> None:
        profile = build_router_poc_profile()
        alternate = ProjectWorkflowProfile.model_validate(
            {
                **profile.model_dump(),
                "shared_context_ref": "ctx-profile-project",
                "architecture_owner_capability_ref": "cap-profile-architecture-owner",
            }
        )
        self.assertEqual("ctx-profile-project", alternate.shared_context_ref)
        self.assertEqual(
            "cap-profile-architecture-owner",
            alternate.architecture_owner_capability_ref,
        )

    def test_shared_context_manifest_accepts_semantic_tree_reference_ids(self) -> None:
        manifest = SharedContextContentManifest(
            revision="rev-0123456789abcdef",
            content_digest=(
                "sha256_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
            ),
            stable_fact_refs=("fact-requirement-current",),
            invariant_boundary_refs=("boundary-invariant-current",),
            artifact_index_refs=("idx-ticket-current",),
        )
        self.assertEqual(("idx-ticket-current",), manifest.artifact_index_refs)

    def test_shared_context_rejects_reserved_expected_revision(self) -> None:
        manifest = self._manifest()
        revised_manifest = self._manifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef1123456789abcdef1123456789abcdef"
            ),
            suffix="two",
        )
        valid_requests = (
            self._request(
                operation=SharedContextOperation.REVISE_DRAFT,
                process_stage=ProcessStage.GRILL,
                expected_current_revision=manifest.revision,
                candidate_manifest=revised_manifest,
            ),
            self._request(
                operation=SharedContextOperation.SEAL,
                process_stage=ProcessStage.CONTEXT,
                expected_current_revision=manifest.revision,
            ),
            self._request(
                operation=SharedContextOperation.READ_REFERENCE,
                process_stage=ProcessStage.REVIEW,
                expected_current_revision=manifest.revision,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
            ),
        )
        for request in valid_requests:
            with self.subTest(operation=request.operation):
                payload = request.model_dump()
                payload["expected_current_revision"] = "rev-0000000000000000"
                with self.assertRaises(ValidationError):
                    SharedContextAccessRequest.model_validate(payload)

    def test_create_binds_candidate_state_and_rejects_wrong_writer(self) -> None:
        absent = self._state(SharedContextLifecycle.ABSENT)
        request = self._request(
            SharedContextOperation.CREATE_DRAFT,
            ProcessStage.ARCHITECTURE,
            candidate_manifest=self.manifest,
        )
        allowed = self.service.decide_access(
            request=request,
            state=absent,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, allowed.decision)
        self.assertEqual(self.manifest.revision, allowed.resulting_state.revision)
        self.assertEqual(self.manifest.content_digest, allowed.resulting_state.content_digest)

        unauthorized = self._request(
            SharedContextOperation.CREATE_DRAFT,
            ProcessStage.ARCHITECTURE,
            actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
            actor_capability_ref="cap-reviewer",
            candidate_manifest=self.manifest,
        )
        denied = self.service.decide_access(
            request=unauthorized,
            state=absent,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.FORBID_ROLE_OR_STAGE, denied.decision)
        self.assertEqual(absent, denied.resulting_state)

    def test_read_requires_sealed_state_and_supported_stage(self) -> None:
        sealed = self._state(
            SharedContextLifecycle.SEALED,
            revision=self.manifest.revision,
            content_digest=self.manifest.content_digest,
        )
        readable = self.service.decide_access(
            request=self._request(
                SharedContextOperation.READ_REFERENCE,
                ProcessStage.REVIEW,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
                expected_current_revision=self.manifest.revision,
            ),
            state=sealed,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, readable.decision)
        self.assertEqual(sealed, readable.resulting_state)

        draft = self._state(
            SharedContextLifecycle.ARCHITECTURE_DRAFT,
            revision=self.manifest.revision,
            content_digest=self.manifest.content_digest,
        )
        blocked = self.service.decide_access(
            request=self._request(
                SharedContextOperation.READ_REFERENCE,
                ProcessStage.REVIEW,
                actor_role=SharedContextActorRole.SUPERVISOR_REVIEWER,
                actor_capability_ref="cap-reviewer",
                expected_current_revision=self.manifest.revision,
            ),
            state=draft,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.FORBID_ROLE_OR_STAGE, blocked.decision)
        self.assertEqual(draft, blocked.resulting_state)

    def test_sealed_revision_needs_approved_change_and_seal_keeps_identity(self) -> None:
        sealed = self._state(
            SharedContextLifecycle.SEALED,
            revision=self.manifest.revision,
            content_digest=self.manifest.content_digest,
        )
        next_manifest = SharedContextContentManifest(
            revision="rev-1123456789abcdef",
            content_digest=(
                "sha256_1123456789abcdef1123456789abcdef"
                "1123456789abcdef1123456789abcdef"
            ),
            stable_fact_refs=("fact-next",),
        )
        request = self._request(
            SharedContextOperation.REVISE_DRAFT,
            ProcessStage.ARCHITECTURE,
            expected_current_revision=self.manifest.revision,
            candidate_manifest=next_manifest,
        )
        blocked = self.service.decide_access(
            request=request,
            state=sealed,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.REQUIRE_CHANGE_CONTROL, blocked.decision)
        self.assertEqual(sealed, blocked.resulting_state)

        approved = self.service.decide_access(
            request=self._request(
                SharedContextOperation.REVISE_DRAFT,
                ProcessStage.ARCHITECTURE,
                expected_current_revision=self.manifest.revision,
                candidate_manifest=next_manifest,
                change_authority_state=AuthorityState.APPROVED,
                approved_change_ref="change-approved",
            ),
            state=sealed,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, approved.decision)
        self.assertEqual(next_manifest.revision, approved.resulting_state.revision)

        draft = self._state(
            SharedContextLifecycle.ARCHITECTURE_DRAFT,
            revision=next_manifest.revision,
            content_digest=next_manifest.content_digest,
        )
        sealed_again = self.service.decide_access(
            request=self._request(
                SharedContextOperation.SEAL,
                ProcessStage.CONTEXT,
                expected_current_revision=next_manifest.revision,
            ),
            state=draft,
            profile=self.profile,
        )
        self.assertEqual(SharedContextMutationDecision.ALLOW, sealed_again.decision)
        self.assertEqual(SharedContextLifecycle.SEALED, sealed_again.resulting_state.lifecycle)
        self.assertEqual(draft.revision, sealed_again.resulting_state.revision)
        self.assertEqual(draft.content_digest, sealed_again.resulting_state.content_digest)


if __name__ == "__main__":
    unittest.main()
