"""Strong-contract tests for receipt-bound handoff artifacts."""

from __future__ import annotations

import json
import unittest

from pydantic import ValidationError

from library.workflow_router.role_supervision_contracts import (
    ArtifactKind,
    ArtifactLifecycle,
    HandoffAdmissionContext,
    HandoffChildRef,
    HandoffIndex,
    HandoffLeaf,
    HandoffLeafBody,
    HandoffRootManifest,
    HandoffValidationFailure,
    HandoffValidationStatus,
    ImplementationTerminalKind,
    ObservedControlPlaneState,
    seal_handoff_leaf,
    validate_handoff_leaf,
    validate_handoff_leaf_json,
)


_DIGEST_A = "sha256_" + ("a" * 64)
_DIGEST_B = "sha256_" + ("b" * 64)


def _body(**changes: str | None) -> HandoffLeafBody:
    values: dict[str, str | None | tuple[str, ...] | ImplementationTerminalKind] = {
        "handoff_id": "handoff-ticket-001-completed",
        "schema_revision": "handoff-schema-v1",
        "project_id": "prj_0123456789abcdef",
        "spec_ref": "spec-feature-one",
        "spec_revision": "rev-1111111111111111",
        "ticket_ref": "ticket-feature-one-001",
        "ticket_revision": "rev-2222222222222222",
        "router_receipt_ref": "receipt-feature-one-001",
        "source_role_ref": "role-implementation-owner",
        "source_task_ref": "task-implementation-one",
        "target_role_ref": "role-supervisor-reviewer",
        "target_task_ref": "task-reviewer-one",
        "worktree_ref": "worktree-featureone-01",
        "branch_ref": "branch-featureone-01",
        "baseline_commit": "1111111111111111111111111111111111111111",
        "result_commit": "2222222222222222222222222222222222222222",
        "terminal_kind": ImplementationTerminalKind.COMPLETED,
        "previous_handoff_ref": None,
        "supersedes_ref": None,
        "evidence_refs": ("evidence-tests-green", "evidence-mypy-green"),
        "correlation_id": "correlation-feature-one-001",
    }
    values.update(changes)
    return HandoffLeafBody.model_validate(values, strict=True)


def _context(
    leaf: HandoffLeaf,
    **changes: str | bool | tuple[str, ...] | None,
) -> HandoffAdmissionContext:
    values: dict[str, str | bool | None | tuple[str, ...]] = {
        "project_id": leaf.project_id,
        "spec_ref": leaf.spec_ref,
        "spec_revision": leaf.spec_revision,
        "ticket_ref": leaf.ticket_ref,
        "ticket_revision": leaf.ticket_revision,
        "router_receipt_ref": leaf.router_receipt_ref,
        "source_role_ref": leaf.source_role_ref,
        "source_task_ref": leaf.source_task_ref,
        "target_role_ref": leaf.target_role_ref,
        "target_task_ref": leaf.target_task_ref,
        "worktree_ref": leaf.worktree_ref,
        "branch_ref": leaf.branch_ref,
        "baseline_commit": leaf.baseline_commit,
        "correlation_id": leaf.correlation_id,
        "observed_handoff_commit": "3333333333333333333333333333333333333333",
        "result_descends_from_baseline": True,
        "handoff_descends_from_result": True,
        "reserved_path_changed": True,
        "consumed_handoff_ids": (),
    }
    values.update(changes)
    return HandoffAdmissionContext.model_validate(values, strict=True)


class HandoffLeafContractTests(unittest.TestCase):
    def test_sealed_leaf_round_trips_and_rejects_digest_or_extra_field(self) -> None:
        leaf = seal_handoff_leaf(_body())
        round_trip = HandoffLeaf.model_validate_json(leaf.model_dump_json(), strict=True)
        self.assertEqual(leaf, round_trip)

        wrong_digest = json.loads(leaf.model_dump_json())
        wrong_digest["content_digest"] = _DIGEST_A
        with self.assertRaises(ValidationError):
            HandoffLeaf.model_validate(wrong_digest, strict=True)

        extra = json.loads(leaf.model_dump_json())
        extra["prompt"] = "untrusted body"
        with self.assertRaises(ValidationError):
            HandoffLeaf.model_validate(extra, strict=True)

    def test_null_empty_coercion_and_bypass_construction_fail_closed(self) -> None:
        payload = json.loads(seal_handoff_leaf(_body()).model_dump_json())
        for field, value in (
            ("handoff_id", ""),
            ("project_id", None),
            ("terminal_kind", "done"),
            ("evidence_refs", []),
            ("target_task_ref", 7),
        ):
            with self.subTest(field=field):
                mutated = dict(payload)
                mutated[field] = value
                with self.assertRaises(ValidationError):
                    HandoffLeaf.model_validate(mutated, strict=True)

        payload["content_digest"] = _DIGEST_A
        bypassed = HandoffLeaf.model_construct(**payload)
        result = validate_handoff_leaf(bypassed, _context(seal_handoff_leaf(_body())))
        self.assertEqual(HandoffValidationStatus.REJECTED, result.status)
        self.assertEqual(HandoffValidationFailure.INVALID_CONTRACT, result.failure)

    def test_admission_checks_every_receipt_bound_identity_and_ancestry(self) -> None:
        leaf = seal_handoff_leaf(_body())
        accepted = validate_handoff_leaf(leaf, _context(leaf))
        self.assertEqual(HandoffValidationStatus.ACCEPTED, accepted.status)
        self.assertEqual(leaf, accepted.leaf)

        cases = (
            ("project_id", "prj_fedcba9876543210", HandoffValidationFailure.PROJECT_MISMATCH),
            ("spec_ref", "spec-wrong", HandoffValidationFailure.SPEC_MISMATCH),
            ("ticket_ref", "ticket-wrong", HandoffValidationFailure.TICKET_MISMATCH),
            ("router_receipt_ref", "receipt-wrong", HandoffValidationFailure.RECEIPT_MISMATCH),
            ("source_task_ref", "task-wrong", HandoffValidationFailure.SOURCE_TASK_MISMATCH),
            ("worktree_ref", "worktree-wrong-02", HandoffValidationFailure.WORKTREE_MISMATCH),
            ("branch_ref", "branch-wrong-02", HandoffValidationFailure.BRANCH_MISMATCH),
            ("baseline_commit", "a" * 40, HandoffValidationFailure.BASELINE_MISMATCH),
            ("correlation_id", "correlation-wrong", HandoffValidationFailure.CORRELATION_MISMATCH),
            ("result_descends_from_baseline", False, HandoffValidationFailure.RESULT_ANCESTRY_INVALID),
            ("handoff_descends_from_result", False, HandoffValidationFailure.HANDOFF_ANCESTRY_INVALID),
            ("reserved_path_changed", False, HandoffValidationFailure.RESERVED_PATH_NOT_CHANGED),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                result = validate_handoff_leaf(leaf, _context(leaf, **{field: value}))
                self.assertEqual(HandoffValidationStatus.REJECTED, result.status)
                self.assertEqual(expected, result.failure)

        replay = validate_handoff_leaf(
            leaf,
            _context(leaf, consumed_handoff_ids=(leaf.handoff_id,)),
        )
        self.assertEqual(HandoffValidationFailure.REPLAY, replay.failure)

    def test_dynamic_json_is_normalized_at_the_boundary(self) -> None:
        leaf = seal_handoff_leaf(_body())
        accepted = validate_handoff_leaf_json(leaf.model_dump_json(), _context(leaf))
        self.assertEqual(HandoffValidationStatus.ACCEPTED, accepted.status)

        for payload in ("[]", "{", '{"handoff_id": 1}'):
            with self.subTest(payload=payload):
                rejected = validate_handoff_leaf_json(payload, _context(leaf))
                self.assertEqual(HandoffValidationStatus.REJECTED, rejected.status)
                self.assertEqual(HandoffValidationFailure.INVALID_CONTRACT, rejected.failure)


class HandoffIndexAndManifestTests(unittest.TestCase):
    def test_index_allows_only_unique_direct_children(self) -> None:
        child = HandoffChildRef(
            child_id="partition-2026",
            child_kind=ArtifactKind.PARTITION_INDEX,
            revision="rev-3333333333333333",
            content_digest=_DIGEST_A,
            lifecycle=ArtifactLifecycle.ACTIVE,
            target_ref="doc/handoffs/2026/index.json",
        )
        index = HandoffIndex(
            index_id="handoff-root-index",
            index_ref="doc/handoffs/index.json",
            revision="rev-4444444444444444",
            direct_child_refs=(child,),
        )
        self.assertEqual((child,), index.direct_child_refs)

        with self.assertRaises(ValidationError):
            HandoffIndex(
                index_id="handoff-root-index",
                index_ref="doc/handoffs/index.json",
                revision="rev-4444444444444444",
                direct_child_refs=(child, child),
            )
        with self.assertRaises(ValidationError):
            HandoffIndex(
                index_id="handoff-root-index",
                index_ref="doc/handoffs/index.json",
                revision="rev-4444444444444444",
                direct_child_refs=(
                    child.model_copy(
                        update={
                            "child_id": "leaf-too-deep",
                            "target_ref": "doc/handoffs/2026/feature/ticket/leaf.json",
                        }
                    ),
                ),
            )

    def test_manifest_is_plugin_neutral_metadata_only(self) -> None:
        partition = HandoffChildRef(
            child_id="partition-2026",
            child_kind=ArtifactKind.PARTITION_INDEX,
            revision="rev-3333333333333333",
            content_digest=_DIGEST_A,
            lifecycle=ArtifactLifecycle.ACTIVE,
            target_ref="doc/handoffs/2026/index.json",
        )
        active_leaf = HandoffChildRef(
            child_id="handoff-ticket-001-completed",
            child_kind=ArtifactKind.HANDOFF_LEAF,
            revision="rev-5555555555555555",
            content_digest=_DIGEST_B,
            lifecycle=ArtifactLifecycle.ACTIVE,
            target_ref="doc/handoffs/2026/feature/ticket/handoff-ticket-001-completed.json",
        )
        manifest = HandoffRootManifest(
            project_id="prj_0123456789abcdef",
            handoff_protocol_id="protocol-receipt-bound-handoff",
            schema_revision="handoff-manifest-v1",
            minimum_compatible_revision="compatibility-v1",
            manifest_revision="rev-6666666666666666",
            direct_child_refs=(partition,),
            active_leaf_refs=(active_leaf,),
            minimum_adoption_capabilities=(
                "capability-git-ref-event",
                "capability-role-wake",
            ),
            last_observed_control_plane_state=ObservedControlPlaneState.ATTACHED,
            last_observation_revision="rev-7777777777777777",
            last_non_replayable_receipt_ref="receipt-feature-one-001",
        )
        serialized = manifest.model_dump_json()
        self.assertNotIn("johnny", serialized.casefold())
        self.assertNotIn("prompt", serialized.casefold())
        self.assertNotIn("C:\\", serialized)
        self.assertEqual(manifest, HandoffRootManifest.model_validate_json(serialized, strict=True))


if __name__ == "__main__":
    unittest.main()
