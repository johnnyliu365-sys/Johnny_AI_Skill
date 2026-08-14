"""Acceptance tests for the bounded workflow artifact-tree resolver."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactTreeChildRef,
    ArtifactTreeDecisionKind,
    ArtifactTreeFamily,
    ArtifactTreeInvalidReason,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    ArtifactTreeNodeKind,
    ArtifactTreeResolver,
    ArtifactTreeResolutionDecision,
    ArtifactTreeResolutionRequest,
)


class ArtifactTreeResolutionTests(unittest.TestCase):
    """Exercise the generic exact-path artifact-tree contract."""

    @staticmethod
    def _digest(character: str) -> str:
        return f"sha256_{character * 64}"

    def _branch(
        self,
        *,
        family: ArtifactTreeFamily = ArtifactTreeFamily.REQUIREMENT_CHANGE,
        prefix: str = "r02c1",
    ) -> tuple[
        ArtifactTreeResolutionRequest,
        ArtifactTreeNode,
        ArtifactTreeNode,
        ArtifactTreeNode,
    ]:
        root = ArtifactTreeNode(
            node_ref=f"root-{prefix}",
            family=family,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision="rev-0123456789abcdef",
            content_digest=self._digest("1"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=f"partition-{prefix}",
                    child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
                    child_revision="rev-1123456789abcdef",
                    child_digest=self._digest("2"),
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        partition = ArtifactTreeNode(
            node_ref=f"partition-{prefix}",
            family=family,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision="rev-1123456789abcdef",
            content_digest=self._digest("2"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=f"leaf-{prefix}",
                    child_kind=ArtifactTreeNodeKind.LEAF,
                    child_revision="rev-2123456789abcdef",
                    child_digest=self._digest("3"),
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        leaf = ArtifactTreeNode(
            node_ref=f"leaf-{prefix}",
            family=family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision="rev-2123456789abcdef",
            content_digest=self._digest("3"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(),
        )
        request = ArtifactTreeResolutionRequest(
            request_ref=f"request-{prefix}",
            family=family,
            root_ref=root.node_ref,
            explicit_path_refs=(root.node_ref, partition.node_ref, leaf.node_ref),
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, partition, leaf),
        )
        return request, root, partition, leaf

    def test_public_surface_resolves_one_exact_path(self) -> None:
        root = ArtifactTreeNode(
            node_ref="root-r02c1",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision="rev-0123456789abcdef",
            content_digest="sha256_" + "1" * 64,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref="partition-r02c1",
                    child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
                    child_revision="rev-1123456789abcdef",
                    child_digest="sha256_" + "2" * 64,
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        partition = ArtifactTreeNode(
            node_ref="partition-r02c1",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision="rev-1123456789abcdef",
            content_digest="sha256_" + "2" * 64,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref="leaf-r02c1",
                    child_kind=ArtifactTreeNodeKind.LEAF,
                    child_revision="rev-2123456789abcdef",
                    child_digest="sha256_" + "3" * 64,
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        leaf = ArtifactTreeNode(
            node_ref="leaf-r02c1",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision="rev-2123456789abcdef",
            content_digest="sha256_" + "3" * 64,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(),
        )
        request = ArtifactTreeResolutionRequest(
            request_ref="request-r02c1",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref=root.node_ref,
            explicit_path_refs=(root.node_ref, partition.node_ref, leaf.node_ref),
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, partition, leaf),
        )

        decision = ArtifactTreeResolver.resolve(request=request)

        self.assertEqual("resolved", decision.decision.value)
        self.assertEqual(leaf.node_ref, decision.resolved_leaf_ref)

    def _assert_reason(
        self,
        request: ArtifactTreeResolutionRequest,
        decision: ArtifactTreeDecisionKind,
        reason: ArtifactTreeInvalidReason,
    ) -> None:
        result = ArtifactTreeResolver.resolve(request)
        self.assertEqual(decision, result.decision)
        self.assertEqual(reason, result.invalid_reason)
        self.assertIsNone(result.resolved_leaf_ref)

    def test_all_families_resolve_and_round_trip_as_typed_metadata(self) -> None:
        for family in ArtifactTreeFamily:
            with self.subTest(family=family):
                request, root, partition, leaf = self._branch(
                    family=family,
                    prefix=f"family-{family.value.replace('_', '-')}",
                )
                decision = ArtifactTreeResolver.resolve(request)
                self.assertEqual(ArtifactTreeDecisionKind.RESOLVED, decision.decision)
                self.assertIsNone(decision.invalid_reason)
                self.assertEqual(leaf.node_ref, decision.resolved_leaf_ref)
                self.assertEqual(
                    request,
                    ArtifactTreeResolutionRequest.model_validate_json(request.model_dump_json()),
                )
                self.assertEqual(
                    root,
                    ArtifactTreeNode.model_validate_json(root.model_dump_json()),
                )
                self.assertEqual(
                    decision,
                    ArtifactTreeResolutionDecision.model_validate_json(decision.model_dump_json()),
                )

    def test_selected_path_resolves_without_traversing_an_unselected_sibling(self) -> None:
        request, root, partition, leaf = self._branch(prefix="multiple")
        sibling_partition = ArtifactTreeNode(
            node_ref="partition-multiple-sibling",
            family=root.family,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision="rev-3123456789abcdef",
            content_digest=self._digest("4"),
            lifecycle=ArtifactTreeLifecycle.CLOSED,
            child_refs=(),
        )
        sibling_edge = ArtifactTreeChildRef(
            child_ref=sibling_partition.node_ref,
            child_kind=sibling_partition.node_kind,
            child_revision=sibling_partition.revision,
            child_digest=sibling_partition.content_digest,
            child_lifecycle=sibling_partition.lifecycle,
        )
        root_with_sibling = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=root.child_refs + (sibling_edge,),
        )
        selected_request = ArtifactTreeResolutionRequest(
            request_ref=request.request_ref,
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=(root.node_ref, partition.node_ref, leaf.node_ref),
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root_with_sibling, partition, leaf),
        )

        decision = ArtifactTreeResolver.resolve(selected_request)

        self.assertEqual(ArtifactTreeDecisionKind.RESOLVED, decision.decision)
        self.assertEqual(leaf.node_ref, decision.resolved_leaf_ref)

    def test_contracts_reject_extra_null_wrong_and_reserved_metadata(self) -> None:
        request, root, _, leaf = self._branch(prefix="invalid")
        invalid_request_payloads = (
            {**request.model_dump(), "body": "raw"},
            {**request.model_dump(), "root_ref": None},
            {**request.model_dump(), "explicit_path_refs": (root.node_ref, leaf.node_ref)},
            {**request.model_dump(), "path_nodes": (root, leaf)},
            {**request.model_dump(), "family": "unknown"},
        )
        for payload in invalid_request_payloads:
            with self.subTest(invalid_request=payload):
                with self.assertRaises(ValidationError):
                    ArtifactTreeResolutionRequest.model_validate(payload)

        invalid_node_payloads = (
            {**root.model_dump(), "revision": "rev-" + "0" * 16},
            {**root.model_dump(), "content_digest": "sha256_" + "0" * 64},
            {**root.model_dump(), "payload": "raw"},
        )
        for payload in invalid_node_payloads:
            with self.subTest(invalid_node=payload):
                with self.assertRaises(ValidationError):
                    ArtifactTreeNode.model_validate(payload)

        invalid_child_payloads = (
            {**root.child_refs[0].model_dump(), "child_revision": "rev-" + "0" * 16},
            {**root.child_refs[0].model_dump(), "child_digest": "sha256_" + "0" * 64},
            {**root.child_refs[0].model_dump(), "source": "raw"},
        )
        for payload in invalid_child_payloads:
            with self.subTest(invalid_child=payload):
                with self.assertRaises(ValidationError):
                    ArtifactTreeChildRef.model_validate(payload)

        leaf_with_children = {
            **leaf.model_dump(),
            "child_refs": (root.child_refs[0].model_dump(),),
        }
        with self.assertRaises(ValidationError):
            ArtifactTreeNode.model_validate(leaf_with_children)

    def test_decision_result_reason_and_leaf_shapes_are_exact(self) -> None:
        request, _, _, leaf = self._branch(prefix="decisions")
        resolved = ArtifactTreeResolver.resolve(request)
        invalid = ArtifactTreeResolutionDecision(
            request_ref=request.request_ref,
            family=request.family,
            decision=ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            invalid_reason=ArtifactTreeInvalidReason.DUPLICATE_NODE,
            resolved_leaf_ref=None,
        )
        not_found = ArtifactTreeResolutionDecision(
            request_ref=request.request_ref,
            family=request.family,
            decision=ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND,
            invalid_reason=ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING,
            resolved_leaf_ref=None,
        )
        self.assertEqual(
            resolved,
            ArtifactTreeResolutionDecision.model_validate_json(resolved.model_dump_json()),
        )
        self.assertEqual(
            invalid,
            ArtifactTreeResolutionDecision.model_validate_json(invalid.model_dump_json()),
        )
        self.assertEqual(
            not_found,
            ArtifactTreeResolutionDecision.model_validate_json(not_found.model_dump_json()),
        )
        resolved_payload = resolved.model_dump(mode="json")
        invalid_payloads = (
            {**resolved_payload, "invalid_reason": ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING.value},
            {**resolved_payload, "resolved_leaf_ref": None},
            {
                **resolved_payload,
                "decision": ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID.value,
                "invalid_reason": None,
                "resolved_leaf_ref": None,
            },
            {
                **resolved_payload,
                "decision": ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID.value,
                "invalid_reason": ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING.value,
                "resolved_leaf_ref": None,
            },
            {
                **resolved_payload,
                "decision": ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND.value,
                "invalid_reason": ArtifactTreeInvalidReason.DUPLICATE_NODE.value,
                "resolved_leaf_ref": None,
            },
            {
                **resolved_payload,
                "decision": ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND.value,
                "invalid_reason": ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING.value,
                "resolved_leaf_ref": leaf.node_ref,
            },
        )
        for payload in invalid_payloads:
            with self.subTest(invalid_decision=payload):
                with self.assertRaises(ValidationError):
                    ArtifactTreeResolutionDecision.model_validate(payload)
                with self.assertRaises(ValidationError):
                    ArtifactTreeResolutionDecision.model_validate_json(json.dumps(payload))

    def test_request_binding_precedes_topology_classification(self) -> None:
        request, root, partition, leaf = self._branch(prefix="binding")
        other_leaf = ArtifactTreeNode(
            node_ref="leaf-binding-other",
            family=request.family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision="rev-3123456789abcdef",
            content_digest=self._digest("4"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(),
        )
        cases = (
            ArtifactTreeResolutionRequest(
                request_ref="request-binding-first",
                family=request.family,
                root_ref="root-binding-other",
                explicit_path_refs=request.explicit_path_refs,
                expected_leaf_ref=leaf.node_ref,
                path_nodes=request.path_nodes,
            ),
            ArtifactTreeResolutionRequest(
                request_ref="request-binding-last",
                family=request.family,
                root_ref=root.node_ref,
                explicit_path_refs=request.explicit_path_refs,
                expected_leaf_ref="leaf-binding-other",
                path_nodes=request.path_nodes,
            ),
            ArtifactTreeResolutionRequest(
                request_ref="request-binding-outside",
                family=request.family,
                root_ref=root.node_ref,
                explicit_path_refs=request.explicit_path_refs,
                expected_leaf_ref=leaf.node_ref,
                path_nodes=(root, partition, other_leaf),
            ),
            ArtifactTreeResolutionRequest(
                request_ref="request-binding-order",
                family=request.family,
                root_ref=root.node_ref,
                explicit_path_refs=request.explicit_path_refs,
                expected_leaf_ref=leaf.node_ref,
                path_nodes=(root, leaf, partition),
            ),
        )
        for invalid_request in cases:
            with self.subTest(request=invalid_request.request_ref):
                self._assert_reason(
                    invalid_request,
                    ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
                    ArtifactTreeInvalidReason.REQUEST_BINDING_MISMATCH,
                )

    def test_topology_failures_have_the_frozen_reason_precedence(self) -> None:
        request, root, partition, leaf = self._branch(prefix="topology")
        duplicate_node_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-duplicate-node",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, partition, partition, leaf),
        )
        cycle_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-cycle",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=(root.node_ref, partition.node_ref, partition.node_ref, leaf.node_ref),
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, partition, leaf),
        )
        partition_to_root = ArtifactTreeChildRef(
            child_ref=root.node_ref,
            child_kind=root.node_kind,
            child_revision=root.revision,
            child_digest=root.content_digest,
            child_lifecycle=root.lifecycle,
        )
        cycle_partition = ArtifactTreeNode(
            node_ref=partition.node_ref,
            family=partition.family,
            node_kind=partition.node_kind,
            revision=partition.revision,
            content_digest=partition.content_digest,
            lifecycle=partition.lifecycle,
            child_refs=partition.child_refs + (partition_to_root,),
        )
        edge_cycle_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-edge-cycle",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, cycle_partition, leaf),
        )
        dangling_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-dangling",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=(root.node_ref, partition.node_ref, "partition-topology-missing", leaf.node_ref),
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, partition, leaf),
        )
        wrong_kind_partition = ArtifactTreeNode(
            node_ref=partition.node_ref,
            family=partition.family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision=partition.revision,
            content_digest=partition.content_digest,
            lifecycle=partition.lifecycle,
            child_refs=(),
        )
        wrong_kind_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-kind",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, wrong_kind_partition, leaf),
        )
        family_mismatch_partition = ArtifactTreeNode(
            node_ref=partition.node_ref,
            family=ArtifactTreeFamily.SHARED_CONTEXT,
            node_kind=partition.node_kind,
            revision=partition.revision,
            content_digest=partition.content_digest,
            lifecycle=partition.lifecycle,
            child_refs=partition.child_refs,
        )
        family_mismatch_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-family",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(root, family_mismatch_partition, leaf),
        )
        duplicate_child_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-duplicate-child",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(
                ArtifactTreeNode(
                    node_ref=root.node_ref,
                    family=root.family,
                    node_kind=root.node_kind,
                    revision=root.revision,
                    content_digest=root.content_digest,
                    lifecycle=root.lifecycle,
                    child_refs=root.child_refs + (root.child_refs[0],),
                ),
                partition,
                leaf,
            ),
        )
        duplicate_parent_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=root.child_refs + (partition.child_refs[0],),
        )
        duplicate_parent_request = ArtifactTreeResolutionRequest(
            request_ref="request-topology-duplicate-parent",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(duplicate_parent_root, partition, leaf),
        )
        self._assert_reason(
            duplicate_node_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.DUPLICATE_NODE,
        )
        self._assert_reason(
            cycle_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.CYCLE,
        )
        self._assert_reason(
            edge_cycle_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.CYCLE,
        )
        self._assert_reason(
            dangling_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.DANGLING_PATH_NODE,
        )
        self._assert_reason(
            wrong_kind_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.KIND_TRANSITION,
        )
        self._assert_reason(
            family_mismatch_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.FAMILY_MISMATCH,
        )
        self._assert_reason(
            duplicate_child_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.DUPLICATE_CHILD,
        )
        self._assert_reason(
            duplicate_parent_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.DUPLICATE_PARENT,
        )

    def test_missing_segments_and_stale_edge_metadata_are_distinct(self) -> None:
        request, root, partition, leaf = self._branch(prefix="edges")
        missing_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref="partition-edges-other",
                    child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
                    child_revision=partition.revision,
                    child_digest=partition.content_digest,
                    child_lifecycle=partition.lifecycle,
                ),
            ),
        )
        missing_request = ArtifactTreeResolutionRequest(
            request_ref="request-edges-missing",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(missing_root, partition, leaf),
        )
        self._assert_reason(
            missing_request,
            ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND,
            ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING,
        )

        stale_edges = (
            ArtifactTreeChildRef(
                child_ref=partition.node_ref,
                child_kind=partition.node_kind,
                child_revision="rev-3123456789abcdef",
                child_digest=partition.content_digest,
                child_lifecycle=partition.lifecycle,
            ),
            ArtifactTreeChildRef(
                child_ref=partition.node_ref,
                child_kind=ArtifactTreeNodeKind.LEAF,
                child_revision=partition.revision,
                child_digest=partition.content_digest,
                child_lifecycle=partition.lifecycle,
            ),
            ArtifactTreeChildRef(
                child_ref=partition.node_ref,
                child_kind=partition.node_kind,
                child_revision=partition.revision,
                child_digest=self._digest("9"),
                child_lifecycle=partition.lifecycle,
            ),
            ArtifactTreeChildRef(
                child_ref=partition.node_ref,
                child_kind=partition.node_kind,
                child_revision=partition.revision,
                child_digest=partition.content_digest,
                child_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            ),
        )
        for index, stale_edge in enumerate(stale_edges, start=1):
            stale_root = ArtifactTreeNode(
                node_ref=root.node_ref,
                family=root.family,
                node_kind=root.node_kind,
                revision=root.revision,
                content_digest=root.content_digest,
                lifecycle=root.lifecycle,
                child_refs=(stale_edge,),
            )
            stale_request = ArtifactTreeResolutionRequest(
                request_ref=f"request-edges-stale-{index}",
                family=request.family,
                root_ref=root.node_ref,
                explicit_path_refs=request.explicit_path_refs,
                expected_leaf_ref=leaf.node_ref,
                path_nodes=(stale_root, partition, leaf),
            )
            with self.subTest(stale_edge=index):
                self._assert_reason(
                    stale_request,
                    ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
                    ArtifactTreeInvalidReason.EDGE_METADATA_MISMATCH,
                )

    def test_source_gate_is_strong_typed_and_effect_free(self) -> None:
        source_path = Path(__file__).parents[1] / "library" / "workflow_router" / "artifact_tree.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_imports = {"os", "pathlib", "socket", "subprocess", "inspect", "requests"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(
                    all(alias.name.split(".")[0] not in forbidden_imports for alias in node.names),
                    node,
                )
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, forbidden_imports)
            if isinstance(node, ast.ExceptHandler):
                self.assertIsNotNone(node.type)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {"getattr", "setattr", "eval", "exec"})
                if isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, {"model_construct", "model_copy", "__dict__"})
            if isinstance(node, ast.Attribute):
                self.assertNotEqual(node.attr, "__dict__")
        self.assertNotIn("Any", source)
        self.assertNotIn("type: ignore", source)
        self.assertNotIn("typing.cast", source)
        self.assertIn("def resolve(", source)
        self.assertIn("ArtifactTreeResolutionDecision", source)

    def test_bounded_reversals_require_edge_revision_parent_and_missing_segment_guards(self) -> None:
        request, root, partition, leaf = self._branch(prefix="reversal")
        stale_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=partition.node_ref,
                    child_kind=partition.node_kind,
                    child_revision="rev-3123456789abcdef",
                    child_digest=partition.content_digest,
                    child_lifecycle=partition.lifecycle,
                ),
            ),
        )
        stale_request = ArtifactTreeResolutionRequest(
            request_ref="request-reversal-edge-revision",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(stale_root, partition, leaf),
        )
        self._assert_reason(
            stale_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.EDGE_METADATA_MISMATCH,
        )

        duplicate_parent_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=root.child_refs + (partition.child_refs[0],),
        )
        duplicate_parent_request = ArtifactTreeResolutionRequest(
            request_ref="request-reversal-parent",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(duplicate_parent_root, partition, leaf),
        )
        self._assert_reason(
            duplicate_parent_request,
            ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID,
            ArtifactTreeInvalidReason.DUPLICATE_PARENT,
        )

        missing_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=(),
        )
        missing_request = ArtifactTreeResolutionRequest(
            request_ref="request-reversal-missing",
            family=request.family,
            root_ref=root.node_ref,
            explicit_path_refs=request.explicit_path_refs,
            expected_leaf_ref=leaf.node_ref,
            path_nodes=(missing_root, partition, leaf),
        )
        self._assert_reason(
            missing_request,
            ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND,
            ArtifactTreeInvalidReason.PATH_SEGMENT_MISSING,
        )


if __name__ == "__main__":
    unittest.main()
