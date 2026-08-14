"""Acceptance tests for the bounded requirement-lineage gate."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactTreeChildRef,
    ArtifactTreeDecisionKind,
    ArtifactTreeFamily,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    ArtifactTreeNodeKind,
    ArtifactTreeResolutionRequest,
    RequirementArchiveBundle,
    RequirementArchiveId,
    RequirementChangeId,
    RequirementId,
    RequirementLineageDecisionKind,
    RequirementLineageGate,
    RequirementLineageInvalidReason,
    RequirementLineageRecord,
    RequirementLineageValidationDecision,
    RequirementLineageValidationRequest,
    RequirementLifecycle,
)


class RequirementLineageTests(unittest.TestCase):
    @staticmethod
    def _digest(character: str) -> str:
        return "sha256_" + character * 64

    @staticmethod
    def _path(
        *,
        prefix: str,
        family: ArtifactTreeFamily,
        root_ref: str | None = None,
        partition_ref: str | None = None,
        leaf_ref: str | None = None,
        leaf_lifecycle: ArtifactTreeLifecycle = ArtifactTreeLifecycle.ACTIVE,
        leaf_digest: str = "5",
        request_ref: str | None = None,
    ) -> tuple[ArtifactTreeResolutionRequest, tuple[ArtifactTreeNode, ...]]:
        selected_root_ref = root_ref or f"root-{prefix}"
        selected_partition_ref = partition_ref or f"partition-{prefix}"
        selected_leaf_ref = leaf_ref or f"leaf-{prefix}"
        root_revision = "rev-1111111111111111"
        partition_revision = "rev-2222222222222222"
        leaf_revision = "rev-3333333333333333"
        partition_digest = RequirementLineageTests._digest("b")
        leaf_content_digest = RequirementLineageTests._digest(leaf_digest)
        root = ArtifactTreeNode(
            node_ref=selected_root_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision="rev-aaaaaaaaaaaaaaaa",
            content_digest=RequirementLineageTests._digest("a"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=selected_partition_ref,
                    child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
                    child_revision=partition_revision,
                    child_digest=partition_digest,
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        partition = ArtifactTreeNode(
            node_ref=selected_partition_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision=partition_revision,
            content_digest=partition_digest,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=selected_leaf_ref,
                    child_kind=ArtifactTreeNodeKind.LEAF,
                    child_revision=leaf_revision,
                    child_digest=leaf_content_digest,
                    child_lifecycle=leaf_lifecycle,
                ),
            ),
        )
        leaf = ArtifactTreeNode(
            node_ref=selected_leaf_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision=leaf_revision,
            content_digest=leaf_content_digest,
            lifecycle=leaf_lifecycle,
            child_refs=(),
        )
        nodes = (root, partition, leaf)
        path = ArtifactTreeResolutionRequest(
            request_ref=request_ref or f"request-{prefix}",
            family=family,
            root_ref=selected_root_ref,
            explicit_path_refs=(selected_root_ref, selected_partition_ref, selected_leaf_ref),
            expected_leaf_ref=selected_leaf_ref,
            path_nodes=nodes,
        )
        return path, nodes

    @staticmethod
    def _path_from_nodes(
        *,
        request_ref: str,
        family: ArtifactTreeFamily,
        nodes: tuple[ArtifactTreeNode, ...],
        expected_leaf_ref: str,
    ) -> ArtifactTreeResolutionRequest:
        return ArtifactTreeResolutionRequest(
            request_ref=request_ref,
            family=family,
            root_ref=nodes[0].node_ref,
            explicit_path_refs=tuple(node.node_ref for node in nodes),
            expected_leaf_ref=expected_leaf_ref,
            path_nodes=nodes,
        )

    @staticmethod
    def _missing_path(path: ArtifactTreeResolutionRequest) -> ArtifactTreeResolutionRequest:
        root = path.path_nodes[0]
        missing_root = ArtifactTreeNode(
            node_ref=root.node_ref,
            family=root.family,
            node_kind=root.node_kind,
            revision=root.revision,
            content_digest=root.content_digest,
            lifecycle=root.lifecycle,
            child_refs=(),
        )
        return RequirementLineageTests._path_from_nodes(
            request_ref=f"{path.request_ref}-missing",
            family=path.family,
            nodes=(missing_root, path.path_nodes[1], path.path_nodes[2]),
            expected_leaf_ref=path.expected_leaf_ref,
        )

    def _active_request(
        self,
        *,
        prd_path: ArtifactTreeResolutionRequest | None = None,
        change_path: ArtifactTreeResolutionRequest | None = None,
        lineage: RequirementLineageRecord | None = None,
    ) -> RequirementLineageValidationRequest:
        default_prd, _ = self._path(
            prefix="active-prd",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            partition_ref="partition-active-pair",
            leaf_ref="leaf-active-pair",
        )
        default_change, _ = self._path(
            prefix="active-change",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref="root-active-change",
            partition_ref="partition-active-pair",
            leaf_ref="leaf-active-pair",
        )
        record = lineage or RequirementLineageRecord(
            lineage_ref="lineage-active-pair",
            prd_id="PRD-20260815-022",
            change_id="CHG-20260815-022",
            lifecycle=RequirementLifecycle.ACTIVE,
            active_leaf_ref="leaf-active-pair",
            archive_id=None,
            archive_leaf_ref=None,
            revision="rev-4444444444444444",
            content_digest=self._digest("4"),
        )
        return RequirementLineageValidationRequest(
            request_ref="request-active-pair",
            lineage=record,
            prd_root_ref=(prd_path or default_prd).root_ref,
            change_root_ref=(change_path or default_change).root_ref,
            prd_active_path=prd_path or default_prd,
            change_active_path=change_path or default_change,
            archive_root_ref=None,
            archive_path=None,
            archive_bundle=None,
        )

    def _retirement_request(
        self,
        *,
        prd_path: ArtifactTreeResolutionRequest | None = None,
        change_path: ArtifactTreeResolutionRequest | None = None,
        archive_path: ArtifactTreeResolutionRequest | None = None,
        bundle: RequirementArchiveBundle | None = None,
        lineage: RequirementLineageRecord | None = None,
    ) -> RequirementLineageValidationRequest:
        default_prd, _ = self._path(
            prefix="retired-prd",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            partition_ref="partition-retired-pair",
            leaf_ref="leaf-retired-pair",
        )
        default_change, _ = self._path(
            prefix="retired-change",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref="root-retired-change",
            partition_ref="partition-retired-pair",
            leaf_ref="leaf-retired-pair",
        )
        default_archive, _ = self._path(
            prefix="archive-leaf",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            leaf_ref="archive-leaf-retired-pair",
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            leaf_digest="6",
        )
        default_bundle = RequirementArchiveBundle(
            archive_id="ARCH-REQ-20260815-022",
            archive_leaf_ref="archive-leaf-retired-pair",
            retired_prd_id="PRD-20260815-022",
            retired_change_id="CHG-20260815-022",
            retired_leaf_ref="leaf-retired-pair",
            last_active_revision="rev-5555555555555555",
            retirement_reason_ref="reason-retirement-approved",
            replacement_prd_id=None,
            replacement_change_id=None,
            historical_source_commit="git_666666666666",
            content_digest=self._digest("6"),
        )
        record = lineage or RequirementLineageRecord(
            lineage_ref="lineage-retired-pair",
            prd_id="PRD-20260815-022",
            change_id="CHG-20260815-022",
            lifecycle=RequirementLifecycle.ARCHIVED,
            active_leaf_ref=None,
            archive_id="ARCH-REQ-20260815-022",
            archive_leaf_ref="archive-leaf-retired-pair",
            revision="rev-7777777777777777",
            content_digest=self._digest("7"),
        )
        selected_prd = prd_path or self._missing_path(default_prd)
        selected_change = change_path or self._missing_path(default_change)
        selected_archive = archive_path or default_archive
        selected_bundle = bundle or default_bundle
        return RequirementLineageValidationRequest(
            request_ref="request-retirement-pair",
            lineage=record,
            prd_root_ref=selected_prd.root_ref,
            change_root_ref=selected_change.root_ref,
            prd_active_path=selected_prd,
            change_active_path=selected_change,
            archive_root_ref=selected_archive.root_ref,
            archive_path=selected_archive,
            archive_bundle=selected_bundle,
        )

    @staticmethod
    def _assert_invalid(
        testcase: unittest.TestCase,
        request: RequirementLineageValidationRequest,
        reason: RequirementLineageInvalidReason,
    ) -> None:
        decision = RequirementLineageGate.validate(request)
        testcase.assertEqual(
            decision.decision,
            RequirementLineageDecisionKind.REQUIREMENT_LINEAGE_INVALID,
        )
        testcase.assertEqual(decision.invalid_reason, reason)
        testcase.assertIsNone(decision.resolved_lineage_leaf_ref)

    def test_first_red_reaches_missing_public_lineage_surface(self) -> None:
        request = self._active_request()
        decision = RequirementLineageGate.validate(request)
        self.assertEqual(
            decision.decision,
            RequirementLineageDecisionKind.ACTIVE_PAIR_VALID,
        )
        self.assertEqual(decision.resolved_lineage_leaf_ref, "leaf-active-pair")

    def test_public_contracts_round_trip_and_reject_invalid_shapes(self) -> None:
        active_request = self._active_request()
        retirement_request = self._retirement_request()
        active_decision = RequirementLineageGate.validate(active_request)
        retirement_decision = RequirementLineageGate.validate(retirement_request)
        for model in (
            active_request.lineage,
            retirement_request.lineage,
            retirement_request.archive_bundle,
            active_request,
            retirement_request,
            active_decision,
            retirement_decision,
        ):
            assert model is not None
            self.assertEqual(type(model).model_validate_json(model.model_dump_json()), model)

        invalid_ids = (
            {"prd_id": "PRD-2026-022", "change_id": "CHG-20260815-022"},
            {"archive_id": "ARCH-REQ-20260815-22"},
        )
        for payload in invalid_ids:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError):
                    RequirementLineageRecord(
                        lineage_ref="lineage-invalid-shape",
                        prd_id=payload.get("prd_id", "PRD-20260815-022"),
                        change_id=payload.get("change_id", "CHG-20260815-022"),
                        lifecycle=RequirementLifecycle.ACTIVE,
                        active_leaf_ref="leaf-invalid-shape",
                        archive_id=payload.get("archive_id"),
                        archive_leaf_ref=None,
                        revision="rev-8888888888888888",
                        content_digest=self._digest("8"),
                    )
        with self.assertRaises(ValidationError):
            RequirementArchiveBundle(
                archive_id="ARCH-REQ-20260815-022",
                archive_leaf_ref="archive-leaf-invalid",
                retired_prd_id="PRD-20260815-022",
                retired_change_id="CHG-20260815-022",
                retired_leaf_ref="leaf-invalid",
                last_active_revision="rev-0000000000000000",
                retirement_reason_ref="reason-invalid",
                replacement_prd_id=None,
                replacement_change_id=None,
                historical_source_commit="git_666666666666",
                content_digest=self._digest("6"),
            )
        with self.assertRaises(ValidationError):
            RequirementArchiveBundle(
                archive_id="ARCH-REQ-20260815-022",
                archive_leaf_ref="archive-leaf-invalid",
                retired_prd_id="PRD-20260815-022",
                retired_change_id="CHG-20260815-022",
                retired_leaf_ref="leaf-invalid",
                last_active_revision="rev-5555555555555555",
                retirement_reason_ref="reason-invalid",
                replacement_prd_id="PRD-20260815-023",
                replacement_change_id=None,
                historical_source_commit="git_666666666666",
                content_digest=self._digest("6"),
            )
        assert retirement_request.archive_bundle is not None
        archive_payload = retirement_request.archive_bundle.model_dump()
        with self.assertRaises(ValidationError):
            RequirementArchiveBundle.model_validate({**archive_payload, "body": "retired prose"})
        with self.assertRaises(ValidationError):
            RequirementLineageValidationDecision(
                request_ref="request-invalid-decision",
                lineage_ref="lineage-invalid-decision",
                decision=RequirementLineageDecisionKind.ACTIVE_PAIR_VALID,
                invalid_reason=RequirementLineageInvalidReason.IDENTIFIER_PAIR_MISMATCH,
                resolved_lineage_leaf_ref="leaf-invalid-decision",
            )

    def test_active_pair_resolves_one_exact_active_leaf(self) -> None:
        decision = RequirementLineageGate.validate(self._active_request())
        self.assertEqual(decision.decision, RequirementLineageDecisionKind.ACTIVE_PAIR_VALID)
        self.assertEqual(decision.resolved_lineage_leaf_ref, "leaf-active-pair")
        self.assertIsNone(decision.invalid_reason)

    def test_retirement_requires_absent_active_paths_and_exact_archive_leaf(self) -> None:
        decision = RequirementLineageGate.validate(self._retirement_request())
        self.assertEqual(decision.decision, RequirementLineageDecisionKind.RETIREMENT_VALID)
        self.assertEqual(decision.resolved_lineage_leaf_ref, "archive-leaf-retired-pair")
        self.assertIsNone(decision.invalid_reason)

    def test_request_binding_and_identifier_precedence_are_exact(self) -> None:
        active = self._active_request()
        mismatched_lineage = RequirementLineageRecord(
            lineage_ref="lineage-mismatched-id",
            prd_id="PRD-20260815-023",
            change_id="CHG-20260815-022",
            lifecycle=RequirementLifecycle.ACTIVE,
            active_leaf_ref="leaf-active-pair",
            archive_id=None,
            archive_leaf_ref=None,
            revision="rev-4444444444444444",
            content_digest=self._digest("4"),
        )
        invalid_identifier = self._active_request(lineage=mismatched_lineage)
        self._assert_invalid(
            self,
            invalid_identifier,
            RequirementLineageInvalidReason.IDENTIFIER_PAIR_MISMATCH,
        )
        wrong_root = RequirementLineageValidationRequest(
            request_ref="request-binding-mismatch",
            lineage=mismatched_lineage,
            prd_root_ref="root-binding-mismatch",
            change_root_ref=active.change_root_ref,
            prd_active_path=active.prd_active_path,
            change_active_path=active.change_active_path,
            archive_root_ref=None,
            archive_path=None,
            archive_bundle=None,
        )
        self._assert_invalid(
            self,
            wrong_root,
            RequirementLineageInvalidReason.REQUEST_BINDING_MISMATCH,
        )

    def test_active_path_and_leaf_failures_are_distinct(self) -> None:
        active = self._active_request()
        stale_edge = ArtifactTreeChildRef(
            child_ref="partition-active-pair",
            child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            child_revision="rev-9999999999999999",
            child_digest=self._digest("b"),
            child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
        )
        stale_root = ArtifactTreeNode(
            node_ref=active.prd_active_path.path_nodes[0].node_ref,
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision=active.prd_active_path.path_nodes[0].revision,
            content_digest=active.prd_active_path.path_nodes[0].content_digest,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(stale_edge,),
        )
        stale_path = self._path_from_nodes(
            request_ref="request-active-stale",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            nodes=(stale_root, active.prd_active_path.path_nodes[1], active.prd_active_path.path_nodes[2]),
            expected_leaf_ref="leaf-active-pair",
        )
        self._assert_invalid(
            self,
            self._active_request(prd_path=stale_path),
            RequirementLineageInvalidReason.ACTIVE_PATH_INVALID,
        )
        _, archived_nodes = self._path(
            prefix="active-archived-leaf",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref="root-active-archived",
            partition_ref="partition-active-pair",
            leaf_ref="leaf-active-pair",
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )
        archived_path = self._path_from_nodes(
            request_ref="request-active-archived-leaf",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            nodes=archived_nodes,
            expected_leaf_ref="leaf-active-pair",
        )
        self._assert_invalid(
            self,
            self._active_request(change_path=archived_path),
            RequirementLineageInvalidReason.ACTIVE_LEAF_MISMATCH,
        )

    def test_archive_bundle_and_replacement_pair_fail_closed(self) -> None:
        retirement = self._retirement_request()
        assert retirement.archive_bundle is not None
        bundle_payload = retirement.archive_bundle.model_dump()
        mismatched_bundle = RequirementArchiveBundle.model_validate(
            {**bundle_payload, "retired_change_id": "CHG-20260815-023"}
        )
        self._assert_invalid(
            self,
            self._retirement_request(bundle=mismatched_bundle),
            RequirementLineageInvalidReason.ARCHIVE_BUNDLE_MISMATCH,
        )
        replacement_bundle = RequirementArchiveBundle.model_validate(
            {
                **bundle_payload,
                "replacement_prd_id": "PRD-20260815-023",
                "replacement_change_id": "CHG-20260815-024",
            }
        )
        self._assert_invalid(
            self,
            self._retirement_request(bundle=replacement_bundle),
            RequirementLineageInvalidReason.REPLACEMENT_PAIR_MISMATCH,
        )

    def test_retirement_overlap_and_archive_path_failures_are_finite(self) -> None:
        retirement = self._retirement_request()
        active_path, _ = self._path(
            prefix="retired-active-overlap",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref=retirement.prd_root_ref,
            partition_ref="partition-retired-pair",
            leaf_ref="leaf-retired-pair",
        )
        self._assert_invalid(
            self,
            self._retirement_request(prd_path=active_path),
            RequirementLineageInvalidReason.RETIRED_PATH_STILL_ACTIVE,
        )
        stale_archive, archive_nodes = self._path(
            prefix="archive-stale",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            leaf_ref="archive-leaf-retired-pair",
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            leaf_digest="6",
        )
        stale_root = ArtifactTreeNode(
            node_ref=archive_nodes[0].node_ref,
            family=archive_nodes[0].family,
            node_kind=archive_nodes[0].node_kind,
            revision=archive_nodes[0].revision,
            content_digest=archive_nodes[0].content_digest,
            lifecycle=archive_nodes[0].lifecycle,
            child_refs=(
                ArtifactTreeChildRef(
                    child_ref=archive_nodes[1].node_ref,
                    child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
                    child_revision="rev-9999999999999999",
                    child_digest=archive_nodes[1].content_digest,
                    child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
                ),
            ),
        )
        stale_archive_path = self._path_from_nodes(
            request_ref="request-archive-stale",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            nodes=(stale_root, archive_nodes[1], archive_nodes[2]),
            expected_leaf_ref="archive-leaf-retired-pair",
        )
        self._assert_invalid(
            self,
            self._retirement_request(archive_path=stale_archive_path),
            RequirementLineageInvalidReason.ARCHIVE_PATH_INVALID,
        )
        self.assertEqual(stale_archive.expected_leaf_ref, "archive-leaf-retired-pair")

    def test_unselected_siblings_remain_opaque_and_untouched(self) -> None:
        active = self._active_request()
        root = active.prd_active_path.path_nodes[0]
        sibling_edge = ArtifactTreeChildRef(
            child_ref="partition-unselected-sibling",
            child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            child_revision="rev-9999999999999999",
            child_digest=self._digest("9"),
            child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
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
        path = self._path_from_nodes(
            request_ref="request-active-sibling",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            nodes=(root_with_sibling, active.prd_active_path.path_nodes[1], active.prd_active_path.path_nodes[2]),
            expected_leaf_ref="leaf-active-pair",
        )
        request = self._active_request(prd_path=path)
        decision = RequirementLineageGate.validate(request)
        self.assertEqual(decision.decision, RequirementLineageDecisionKind.ACTIVE_PAIR_VALID)

    def test_source_gate_is_strong_typed_and_effect_free(self) -> None:
        source_path = Path(__file__).parents[1] / "library" / "workflow_router" / "requirement_lineage.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_imports = {"inspect", "os", "pathlib", "requests", "socket", "subprocess"}
        forbidden_calls = {
            "eval",
            "exec",
            "getattr",
            "setattr",
        }
        forbidden_attributes = {"__dict__", "model_construct", "model_copy"}
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
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, forbidden_calls)
            if isinstance(node, ast.Attribute):
                self.assertNotIn(node.attr, forbidden_attributes)
            if isinstance(node, (ast.arg, ast.AnnAssign)):
                annotation = node.annotation if isinstance(node, ast.arg) else node.annotation
                if annotation is not None:
                    annotation_text = ast.unparse(annotation)
                    self.assertNotIn(annotation_text, {"Any", "object", "str"})
        self.assertNotIn("Any", source)
        self.assertNotIn("type: ignore", source)
        self.assertNotIn("typing.cast", source)
        self.assertIn("class RequirementLineageGate", source)
        self.assertIn("ArtifactTreeResolver.resolve", source)

    def test_bounded_reversals_require_suffix_overlap_and_archive_edge_guards(self) -> None:
        active = self._active_request()
        changed_ids = RequirementLineageRecord(
            lineage_ref="lineage-reversal-suffix",
            prd_id="PRD-20260815-023",
            change_id="CHG-20260815-022",
            lifecycle=RequirementLifecycle.ACTIVE,
            active_leaf_ref="leaf-active-pair",
            archive_id=None,
            archive_leaf_ref=None,
            revision="rev-4444444444444444",
            content_digest=self._digest("4"),
        )
        self._assert_invalid(
            self,
            self._active_request(lineage=changed_ids),
            RequirementLineageInvalidReason.IDENTIFIER_PAIR_MISMATCH,
        )
        active_path, _ = self._path(
            prefix="reversal-still-active",
            family=ArtifactTreeFamily.REQUIREMENT_CHANGE,
            root_ref=active.prd_root_ref,
            partition_ref="partition-retired-pair",
            leaf_ref="leaf-retired-pair",
        )
        self._assert_invalid(
            self,
            self._retirement_request(prd_path=active_path),
            RequirementLineageInvalidReason.RETIRED_PATH_STILL_ACTIVE,
        )
        stale_archive, _ = self._path(
            prefix="reversal-stale-archive",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            leaf_ref="archive-leaf-retired-pair",
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            leaf_digest="6",
        )
        stale_leaf = stale_archive.path_nodes[2]
        stale_partition = stale_archive.path_nodes[1]
        stale_root = stale_archive.path_nodes[0]
        stale_edge = ArtifactTreeChildRef(
            child_ref=stale_partition.node_ref,
            child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            child_revision="rev-9999999999999999",
            child_digest=stale_partition.content_digest,
            child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
        )
        stale_path = self._path_from_nodes(
            request_ref="request-reversal-stale-archive",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            nodes=(
                ArtifactTreeNode(
                    node_ref=stale_root.node_ref,
                    family=stale_root.family,
                    node_kind=stale_root.node_kind,
                    revision=stale_root.revision,
                    content_digest=stale_root.content_digest,
                    lifecycle=stale_root.lifecycle,
                    child_refs=(stale_edge,),
                ),
                stale_partition,
                stale_leaf,
            ),
            expected_leaf_ref=stale_leaf.node_ref,
        )
        self._assert_invalid(
            self,
            self._retirement_request(archive_path=stale_path),
            RequirementLineageInvalidReason.ARCHIVE_PATH_INVALID,
        )


if __name__ == "__main__":
    unittest.main()
