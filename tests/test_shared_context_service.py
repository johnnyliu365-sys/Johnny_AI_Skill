"""Focused service-level checks; public-entry behavior remains in router tests."""

from __future__ import annotations

import unittest

from library.workflow_router.contracts import (
    AuthorityState,
    EvidenceDigest,
    OpaqueMetadataId,
    ProcessStage,
    RevisionDigest,
    SharedContextAccessRequest,
    SharedContextActorRole,
    SharedContextContentManifest,
    SharedContextLifecycle,
    SharedContextMutationDecision,
    SharedContextOperation,
    SharedContextState,
)
from library.workflow_router.profile import build_router_poc_profile
from library.workflow_router.shared_context_service import SharedContextAccessService


class SharedContextAccessServiceTests(unittest.TestCase):
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
