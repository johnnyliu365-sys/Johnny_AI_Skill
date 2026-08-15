from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path
from typing import Final

from pydantic import ValidationError

from library.workflow_router import (
    ArtifactTreeChildRef,
    ArtifactTreeFamily,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    ArtifactTreeNodeKind,
    ArtifactTreeResolutionRequest,
    LibrarySelectionDecision,
    LibrarySelectionDecisionKind,
    LibrarySelectionGate,
    LibrarySelectionInvalidReason,
    LibrarySelectionKind,
    LibrarySelectionRecord,
    LibrarySelectionRequest,
)


_ARCHIVE_FAMILY: Final[ArtifactTreeFamily] = ArtifactTreeFamily.ARCHIVE_LIBRARY
_MODULE_FAMILY: Final[ArtifactTreeFamily] = ArtifactTreeFamily.REUSABLE_MODULE


class LibrarySelectionGateTests(unittest.TestCase):
    """Exercise the bounded, caller-selected library path contract."""

    @staticmethod
    def _digest(character: str) -> str:
        return f"sha256_{character * 64}"

    @classmethod
    def _path(
        cls,
        *,
        prefix: str,
        family: ArtifactTreeFamily,
        leaf_lifecycle: ArtifactTreeLifecycle,
        connect_path: bool = True,
        include_sibling: bool = False,
    ) -> ArtifactTreeResolutionRequest:
        root_ref = f"root-{prefix}"
        partition_ref = f"partition-{prefix}"
        leaf_ref = f"leaf-{prefix}"
        selected_partition_edge = ArtifactTreeChildRef(
            child_ref=partition_ref,
            child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            child_revision="rev-2222222222222222",
            child_digest=cls._digest("b"),
            child_lifecycle=ArtifactTreeLifecycle.ACTIVE,
        )
        sibling_edge = ArtifactTreeChildRef(
            child_ref=f"partition-{prefix}-sibling",
            child_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            child_revision="rev-4444444444444444",
            child_digest=cls._digest("d"),
            child_lifecycle=ArtifactTreeLifecycle.CLOSED,
        )
        root_children: tuple[ArtifactTreeChildRef, ...] = (selected_partition_edge,)
        if include_sibling:
            root_children += (sibling_edge,)
        root = ArtifactTreeNode(
            node_ref=root_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision="rev-1111111111111111",
            content_digest=cls._digest("a"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=root_children,
        )
        leaf_edge = ArtifactTreeChildRef(
            child_ref=leaf_ref,
            child_kind=ArtifactTreeNodeKind.LEAF,
            child_revision="rev-3333333333333333",
            child_digest=cls._digest("c"),
            child_lifecycle=leaf_lifecycle,
        )
        partition_children = (leaf_edge,) if connect_path else ()
        partition = ArtifactTreeNode(
            node_ref=partition_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision="rev-2222222222222222",
            content_digest=cls._digest("b"),
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=partition_children,
        )
        leaf = ArtifactTreeNode(
            node_ref=leaf_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision="rev-3333333333333333",
            content_digest=cls._digest("c"),
            lifecycle=leaf_lifecycle,
            child_refs=(),
        )
        return ArtifactTreeResolutionRequest(
            request_ref=f"request-{prefix}",
            family=family,
            root_ref=root_ref,
            explicit_path_refs=(root_ref, partition_ref, leaf_ref),
            expected_leaf_ref=leaf_ref,
            path_nodes=(root, partition, leaf),
        )

    @classmethod
    def _request(
        cls,
        *,
        prefix: str,
        kind: LibrarySelectionKind,
        family: ArtifactTreeFamily,
        leaf_lifecycle: ArtifactTreeLifecycle,
        selection_lifecycle: ArtifactTreeLifecycle | None = None,
        selection_digest: str | None = None,
        connect_path: bool = True,
        include_sibling: bool = False,
    ) -> LibrarySelectionRequest:
        path = cls._path(
            prefix=prefix,
            family=family,
            leaf_lifecycle=leaf_lifecycle,
            connect_path=connect_path,
            include_sibling=include_sibling,
        )
        leaf = path.path_nodes[-1]
        selected_lifecycle = leaf.lifecycle if selection_lifecycle is None else selection_lifecycle
        selected_digest = leaf.content_digest if selection_digest is None else selection_digest
        selection = LibrarySelectionRecord(
            selection_ref=f"selection-{prefix}",
            kind=kind,
            root_ref=path.root_ref,
            partition_ref=path.path_nodes[1].node_ref,
            leaf_ref=path.expected_leaf_ref,
            leaf_lifecycle=selected_lifecycle,
            leaf_digest=selected_digest,
        )
        return LibrarySelectionRequest(
            request_ref=f"request-selection-{prefix}",
            selection=selection,
            path=path,
        )

    def test_acx1_exact_contracts_round_trip_as_strong_metadata(self) -> None:
        request = self._request(
            prefix="archive-round-trip",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )
        selected = LibrarySelectionGate.validate(request)
        invalid = LibrarySelectionDecision(
            request_ref=request.request_ref,
            selection_ref=request.selection.selection_ref,
            decision=LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID,
            invalid_reason=LibrarySelectionInvalidReason.PATH_INVALID,
            selected_leaf_ref=None,
        )

        self.assertEqual(
            request,
            LibrarySelectionRequest.model_validate_json(request.model_dump_json()),
        )
        self.assertEqual(
            request.selection,
            LibrarySelectionRecord.model_validate_json(request.selection.model_dump_json()),
        )
        self.assertEqual(
            selected,
            LibrarySelectionDecision.model_validate_json(selected.model_dump_json()),
        )
        self.assertEqual(
            invalid,
            LibrarySelectionDecision.model_validate_json(invalid.model_dump_json()),
        )
        self.assertEqual(
            {
                "selection_ref",
                "kind",
                "root_ref",
                "partition_ref",
                "leaf_ref",
                "leaf_lifecycle",
                "leaf_digest",
            },
            set(LibrarySelectionRecord.model_fields),
        )
        self.assertEqual(
            {"request_ref", "selection", "path"},
            set(LibrarySelectionRequest.model_fields),
        )
        self.assertEqual(
            {
                "request_ref",
                "selection_ref",
                "decision",
                "invalid_reason",
                "selected_leaf_ref",
            },
            set(LibrarySelectionDecision.model_fields),
        )

    def test_acx1_contracts_reject_extra_null_wrong_raw_and_reserved_values(self) -> None:
        request = self._request(
            prefix="contract-rejections",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )
        record_payload = request.selection.model_dump(mode="json")
        request_payload = request.model_dump(mode="json")
        decision_payload = LibrarySelectionGate.validate(request).model_dump(mode="json")
        invalid_record_payloads = (
            {**record_payload, "body": "copied artifact body"},
            {**record_payload, "source": "filesystem/path"},
            {**record_payload, "leaf_digest": self._digest("0")},
            {**record_payload, "kind": 1},
            {**record_payload, "leaf_lifecycle": None},
            {**record_payload, "leaf_digest": None},
        )
        for payload in invalid_record_payloads:
            with self.subTest(record_payload=payload):
                with self.assertRaises(ValidationError):
                    LibrarySelectionRecord.model_validate(payload)

        invalid_request_payloads = (
            {**request_payload, "title": "unbounded prose"},
            {**request_payload, "selection": None},
            {**request_payload, "path": None},
            {**request_payload, "request_ref": 4},
        )
        for payload in invalid_request_payloads:
            with self.subTest(request_payload=payload):
                with self.assertRaises(ValidationError):
                    LibrarySelectionRequest.model_validate(payload)

        invalid_decision_payloads = (
            {**decision_payload, "body": "raw response"},
            {**decision_payload, "decision": "unknown"},
            {**decision_payload, "invalid_reason": LibrarySelectionInvalidReason.PATH_INVALID.value},
            {**decision_payload, "selected_leaf_ref": None},
        )
        for payload in invalid_decision_payloads:
            with self.subTest(decision_payload=payload):
                with self.assertRaises(ValidationError):
                    LibrarySelectionDecision.model_validate(payload)

    def test_acx1_request_rejects_non_exact_ref_count_and_order(self) -> None:
        request = self._request(
            prefix="request-shape",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )
        path = request.path
        root, partition, leaf = path.path_nodes
        invalid_paths = (
            ArtifactTreeResolutionRequest(
                request_ref=path.request_ref,
                family=path.family,
                root_ref="root-other-shape",
                explicit_path_refs=path.explicit_path_refs,
                expected_leaf_ref=path.expected_leaf_ref,
                path_nodes=path.path_nodes,
            ),
            ArtifactTreeResolutionRequest(
                request_ref=path.request_ref,
                family=path.family,
                root_ref=path.root_ref,
                explicit_path_refs=(root.node_ref, leaf.node_ref, partition.node_ref),
                expected_leaf_ref=path.expected_leaf_ref,
                path_nodes=path.path_nodes,
            ),
            ArtifactTreeResolutionRequest(
                request_ref=path.request_ref,
                family=path.family,
                root_ref=path.root_ref,
                explicit_path_refs=path.explicit_path_refs + ("leaf-extra-shape",),
                expected_leaf_ref=path.expected_leaf_ref,
                path_nodes=path.path_nodes,
            ),
        )
        for invalid_path in invalid_paths:
            with self.subTest(invalid_path=invalid_path):
                with self.assertRaises(ValidationError):
                    LibrarySelectionRequest(
                        request_ref=request.request_ref,
                        selection=request.selection,
                        path=invalid_path,
                    )

        binding_paths = (
            invalid_paths[0],
            ArtifactTreeResolutionRequest(
                request_ref=path.request_ref,
                family=path.family,
                root_ref=path.root_ref,
                explicit_path_refs=(root.node_ref, "partition-other-shape", leaf.node_ref),
                expected_leaf_ref=path.expected_leaf_ref,
                path_nodes=path.path_nodes,
            ),
            ArtifactTreeResolutionRequest(
                request_ref=path.request_ref,
                family=path.family,
                root_ref=path.root_ref,
                explicit_path_refs=path.explicit_path_refs,
                expected_leaf_ref="leaf-other-shape",
                path_nodes=path.path_nodes,
            ),
            invalid_paths[1],
            invalid_paths[2],
        )
        for malformed_path in binding_paths:
            malformed_request = LibrarySelectionRequest.model_construct(
                request_ref=request.request_ref,
                selection=request.selection,
                path=malformed_path,
            )
            decision = LibrarySelectionGate.validate(malformed_request)
            with self.subTest(malformed_path=malformed_path):
                self.assertEqual(
                    LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID,
                    decision.decision,
                )
                self.assertEqual(
                    LibrarySelectionInvalidReason.REQUEST_BINDING_MISMATCH,
                    decision.invalid_reason,
                )

    def test_acx1_decision_shape_requires_one_finite_result_form(self) -> None:
        request = self._request(
            prefix="decision-shape",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )
        selected_payload = LibrarySelectionGate.validate(request).model_dump(mode="json")
        invalid_shapes = (
            {**selected_payload, "invalid_reason": LibrarySelectionInvalidReason.PATH_INVALID.value},
            {**selected_payload, "selected_leaf_ref": None},
            {
                **selected_payload,
                "decision": LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID.value,
                "invalid_reason": None,
                "selected_leaf_ref": None,
            },
            {
                **selected_payload,
                "decision": LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID.value,
                "invalid_reason": LibrarySelectionInvalidReason.PATH_INVALID.value,
                "selected_leaf_ref": request.selection.leaf_ref,
            },
        )
        for payload in invalid_shapes:
            with self.subTest(decision_shape=payload):
                with self.assertRaises(ValidationError):
                    LibrarySelectionDecision.model_validate(payload)
                with self.assertRaises(ValidationError):
                    LibrarySelectionDecision.model_validate_json(json.dumps(payload))

    def test_acx2_exact_archive_leaf_is_selected(self) -> None:
        request = self._request(
            prefix="archive-selected",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionDecisionKind.SELECTED, decision.decision)
        self.assertEqual(request.selection.leaf_ref, decision.selected_leaf_ref)
        self.assertIsNone(decision.invalid_reason)

    def test_acx2_exact_reusable_module_leaf_is_selected(self) -> None:
        request = self._request(
            prefix="module-selected",
            kind=LibrarySelectionKind.REUSABLE_MODULE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ACTIVE,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionDecisionKind.SELECTED, decision.decision)
        self.assertEqual(request.selection.leaf_ref, decision.selected_leaf_ref)
        self.assertIsNone(decision.invalid_reason)

    def test_acx3_wrong_family_is_finitely_invalid_before_path_resolution(self) -> None:
        request = self._request(
            prefix="family-invalid",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID,
            decision.decision,
        )
        self.assertEqual(LibrarySelectionInvalidReason.FAMILY_MISMATCH, decision.invalid_reason)
        self.assertIsNone(decision.selected_leaf_ref)

    def test_acx3_reusable_module_requires_an_active_leaf(self) -> None:
        request = self._request(
            prefix="lifecycle-invalid",
            kind=LibrarySelectionKind.REUSABLE_MODULE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            LibrarySelectionInvalidReason.LEAF_LIFECYCLE_MISMATCH,
            decision.invalid_reason,
        )
        self.assertIsNone(decision.selected_leaf_ref)

    def test_acx3_record_lifecycle_mismatch_is_finitely_invalid(self) -> None:
        request = self._request(
            prefix="record-lifecycle-invalid",
            kind=LibrarySelectionKind.REUSABLE_MODULE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ACTIVE,
            selection_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            LibrarySelectionInvalidReason.LEAF_LIFECYCLE_MISMATCH,
            decision.invalid_reason,
        )
        self.assertIsNone(decision.selected_leaf_ref)

    def test_acx3_invalid_topology_is_finitely_path_invalid(self) -> None:
        request = self._request(
            prefix="topology-invalid",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            connect_path=False,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionInvalidReason.PATH_INVALID, decision.invalid_reason)
        self.assertIsNone(decision.selected_leaf_ref)

    def test_acx3_leaf_digest_mismatch_is_finitely_invalid(self) -> None:
        request = self._request(
            prefix="metadata-invalid",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            selection_digest=self._digest("e"),
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            LibrarySelectionInvalidReason.LEAF_METADATA_MISMATCH,
            decision.invalid_reason,
        )
        self.assertIsNone(decision.selected_leaf_ref)

    def test_acx4_only_supplied_selected_branch_is_resolved(self) -> None:
        request = self._request(
            prefix="selected-branch",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            include_sibling=True,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionDecisionKind.SELECTED, decision.decision)
        self.assertEqual(
            ("root-selected-branch", "partition-selected-branch", "leaf-selected-branch"),
            tuple(node.node_ref for node in request.path.path_nodes),
        )
        self.assertNotIn(
            "partition-selected-branch-sibling",
            tuple(node.node_ref for node in request.path.path_nodes),
        )

    def test_acx5_public_result_contains_only_metadata_and_no_effect_port(self) -> None:
        request = self._request(
            prefix="metadata-only",
            kind=LibrarySelectionKind.REUSABLE_MODULE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ACTIVE,
        )
        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            {
                "request_ref",
                "selection_ref",
                "decision",
                "invalid_reason",
                "selected_leaf_ref",
            },
            set(decision.model_dump()),
        )
        self.assertNotIn("body", decision.model_dump())
        self.assertNotIn("source", decision.model_dump())
        self.assertNotIn("filesystem_path", decision.model_dump())

    @staticmethod
    def _assert_selection_source_semantics(source: str) -> None:
        """Require the exact frozen admission predicates in the pure gate."""

        tree = ast.parse(source)
        gate_nodes = [
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "LibrarySelectionGate"
        ]
        if len(gate_nodes) != 1:
            raise AssertionError("library selection gate class is not unique")
        gate_node = gate_nodes[0]
        method_names = {
            node.name
            for node in gate_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        if not {"validate", "_kind_contract"}.issubset(method_names):
            raise AssertionError("library selection gate methods are incomplete")

        comparisons = {
            ast.unparse(node)
            for node in ast.walk(gate_node)
            if isinstance(node, ast.Compare)
        }
        required_comparisons = {
            "len(path.explicit_path_refs) != 3",
            "len(path.path_nodes) != 3",
            "path.root_ref != selection.root_ref",
            "path.expected_leaf_ref != selection.leaf_ref",
            "path.explicit_path_refs != expected_refs",
            "supplied_node_refs != expected_refs",
            "path.family is not expected_family",
        }
        if not required_comparisons.issubset(comparisons):
            raise AssertionError("canonical library selection predicates are incomplete")

        return_values = {
            ast.unparse(node.value)
            for node in ast.walk(gate_node)
            if isinstance(node, ast.Return) and node.value is not None
        }
        if (
            "(ArtifactTreeFamily.REUSABLE_MODULE, ArtifactTreeLifecycle.ACTIVE)"
            not in return_values
        ):
            raise AssertionError("reusable-module lifecycle mapping is not canonical")

    @staticmethod
    def _assert_module_source_policy(source: str) -> None:
        tree = ast.parse(source)
        forbidden_imports = {
            "importlib",
            "inspect",
            "os",
            "pathlib",
            "requests",
            "shutil",
            "socket",
            "subprocess",
            "sys",
            "tempfile",
            "urllib",
        }
        forbidden_calls = {"eval", "exec", "getattr", "hasattr", "setattr"}
        forbidden_attributes = {"__class__", "__dict__", "model_construct", "model_copy"}
        forbidden_tokens = (
            "Any",
            "object",
            "cast(",
            "typing.cast",
            "type: ignore",
            "Optional[",
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden_imports:
                        raise AssertionError(f"forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                if node.module.split(".")[0] in forbidden_imports:
                    raise AssertionError(f"forbidden import: {node.module}")
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                raise AssertionError("broad exception handler")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    raise AssertionError(f"forbidden call: {node.func.id}")
            elif isinstance(node, ast.Attribute) and node.attr in forbidden_attributes:
                raise AssertionError(f"forbidden attribute: {node.attr}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns is None:
                    raise AssertionError(f"untyped return: {node.name}")
                arguments = (
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                )
                for argument in arguments:
                    if argument.arg != "self" and argument.annotation is None:
                        raise AssertionError(f"untyped argument: {argument.arg}")
                    if (
                        argument.arg != "self"
                        and argument.annotation is not None
                        and ast.unparse(argument.annotation) == "str"
                    ):
                        raise AssertionError(f"raw string domain argument: {argument.arg}")
        for token in forbidden_tokens:
            if token in source:
                raise AssertionError(f"forbidden token: {token}")
        if "ArtifactTreeResolver.resolve" not in source:
            raise AssertionError("integrated resolver is not used")
        LibrarySelectionGateTests._assert_selection_source_semantics(source)

    @staticmethod
    def _assert_contract_surface(source: str) -> None:
        tree = ast.parse(source)
        enum_members = {
            "LibrarySelectionKind": {"ARCHIVE": "archive", "REUSABLE_MODULE": "reusable_module"},
            "LibrarySelectionDecisionKind": {
                "SELECTED": "selected",
                "LIBRARY_SELECTION_INVALID": "library_selection_invalid",
            },
            "LibrarySelectionInvalidReason": {
                "REQUEST_BINDING_MISMATCH": "request_binding_mismatch",
                "FAMILY_MISMATCH": "family_mismatch",
                "PATH_INVALID": "path_invalid",
                "LEAF_LIFECYCLE_MISMATCH": "leaf_lifecycle_mismatch",
                "LEAF_METADATA_MISMATCH": "leaf_metadata_mismatch",
            },
        }
        model_fields = {
            "LibrarySelectionRecord": {
                "selection_ref": "OpaqueMetadataId",
                "kind": "LibrarySelectionKind",
                "root_ref": "OpaqueMetadataId",
                "partition_ref": "OpaqueMetadataId",
                "leaf_ref": "OpaqueMetadataId",
                "leaf_lifecycle": "ArtifactTreeLifecycle",
                "leaf_digest": "EvidenceDigest",
            },
            "LibrarySelectionRequest": {
                "request_ref": "OpaqueMetadataId",
                "selection": "LibrarySelectionRecord",
                "path": "ArtifactTreeResolutionRequest",
            },
            "LibrarySelectionDecision": {
                "request_ref": "OpaqueMetadataId",
                "selection_ref": "OpaqueMetadataId",
                "decision": "LibrarySelectionDecisionKind",
                "invalid_reason": "LibrarySelectionInvalidReason | None",
                "selected_leaf_ref": "OpaqueMetadataId | None",
            },
        }
        class_names = set(enum_members) | set(model_fields)
        classes = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name in class_names
        }
        if set(classes) != class_names:
            raise AssertionError("public contract classes are incomplete")
        for class_name, class_node in classes.items():
            class_source = ast.unparse(class_node)
            for token in ("Any", "object", "cast(", "model_construct", "model_copy", "type: ignore"):
                if token in class_source:
                    raise AssertionError(f"forbidden contract token: {token}")
            if class_name in enum_members:
                assignments = {
                    statement.targets[0].id: statement.value.value
                    for statement in class_node.body
                    if isinstance(statement, ast.Assign)
                    and len(statement.targets) == 1
                    and isinstance(statement.targets[0], ast.Name)
                    and isinstance(statement.value, ast.Constant)
                }
                if assignments != enum_members[class_name]:
                    raise AssertionError(f"enum surface changed: {class_name}")
            else:
                if "RouterModel" not in {ast.unparse(base) for base in class_node.bases}:
                    raise AssertionError(f"model is not a RouterModel: {class_name}")
                fields = {
                    statement.target.id: ast.unparse(statement.annotation)
                    for statement in class_node.body
                    if isinstance(statement, ast.AnnAssign)
                    and isinstance(statement.target, ast.Name)
                    and statement.annotation is not None
                }
                if fields != model_fields[class_name]:
                    raise AssertionError(f"model surface changed: {class_name}")

    def test_acx6_static_source_gate_is_strong_typed_and_effect_free(self) -> None:
        repository_root = Path(__file__).parents[1]
        module_path = repository_root / "library" / "workflow_router" / "library_selection.py"
        contracts_path = repository_root / "library" / "workflow_router" / "contracts.py"
        package_path = repository_root / "library" / "workflow_router" / "__init__.py"
        module_source = module_path.read_text(encoding="utf-8")
        contracts_source = contracts_path.read_text(encoding="utf-8")
        package_source = package_path.read_text(encoding="utf-8")

        self._assert_module_source_policy(module_source)
        self._assert_contract_surface(contracts_source)
        for public_name in (
            "LibrarySelectionDecision",
            "LibrarySelectionDecisionKind",
            "LibrarySelectionGate",
            "LibrarySelectionInvalidReason",
            "LibrarySelectionKind",
            "LibrarySelectionRecord",
            "LibrarySelectionRequest",
        ):
            self.assertIn(f'"{public_name}"', package_source)
        self.assertIn("from .library_selection import LibrarySelectionGate", package_source)

    def test_acx6_static_source_gate_rejects_in_memory_policy_mutations(self) -> None:
        repository_root = Path(__file__).parents[1]
        module_path = repository_root / "library" / "workflow_router" / "library_selection.py"
        contracts_path = repository_root / "library" / "workflow_router" / "contracts.py"
        module_source = module_path.read_text(encoding="utf-8")
        contracts_source = contracts_path.read_text(encoding="utf-8")
        mutations = (
            module_source.replace("from .artifact_tree", "import os\nfrom .artifact_tree", 1),
            module_source.replace(
                "request: LibrarySelectionRequest",
                "request: object",
                1,
            ),
            module_source.replace(
                "return LibrarySelectionGate._invalid(",
                "return LibrarySelectionGate._invalid(  # type: ignore",
                1,
            ),
        )
        for mutated_source in mutations:
            with self.subTest(mutated_source=mutated_source):
                with self.assertRaises(AssertionError):
                    self._assert_module_source_policy(mutated_source)
        with self.assertRaises(AssertionError):
            self._assert_contract_surface(
                contracts_source.replace(
                    "selection_ref: OpaqueMetadataId",
                    "selection_ref: str",
                    1,
                )
            )

    def test_acx6_semantic_source_gate_rejects_exact_review_mutations_without_execution(
        self,
    ) -> None:
        repository_root = Path(__file__).parents[1]
        module_path = repository_root / "library" / "workflow_router" / "library_selection.py"
        module_source = module_path.read_text(encoding="utf-8")
        mutations = (
            (
                "family binding bypass",
                module_source.replace(
                    "if path.family is not expected_family:",
                    "if False:",
                    1,
                ),
            ),
            (
                "archived reusable leaf acceptance",
                module_source.replace(
                    "return ArtifactTreeFamily.REUSABLE_MODULE, ArtifactTreeLifecycle.ACTIVE",
                    "return ArtifactTreeFamily.REUSABLE_MODULE, ArtifactTreeLifecycle.ARCHIVED",
                    1,
                ),
            ),
            (
                "explicit path binding bypass",
                module_source.replace(
                    "or path.explicit_path_refs != expected_refs",
                    "or False",
                    1,
                ),
            ),
        )
        for mutation_name, mutated_source in mutations:
            with self.subTest(mutation=mutation_name):
                self.assertNotEqual(module_source, mutated_source)
                with self.assertRaises(AssertionError):
                    self._assert_module_source_policy(mutated_source)

    def test_acx6_reversal_kind_family_binding_remains_fail_closed(self) -> None:
        request = self._request(
            prefix="reversal-family",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionInvalidReason.FAMILY_MISMATCH, decision.invalid_reason)
        self.assertEqual(LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID, decision.decision)

    def test_acx6_reversal_archived_reusable_leaf_remains_fail_closed(self) -> None:
        request = self._request(
            prefix="reversal-lifecycle",
            kind=LibrarySelectionKind.REUSABLE_MODULE,
            family=_MODULE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(
            LibrarySelectionInvalidReason.LEAF_LIFECYCLE_MISMATCH,
            decision.invalid_reason,
        )
        self.assertEqual(LibrarySelectionDecisionKind.LIBRARY_SELECTION_INVALID, decision.decision)

    def test_acx6_reversal_unselected_sibling_remains_opaque(self) -> None:
        request = self._request(
            prefix="reversal-sibling",
            kind=LibrarySelectionKind.ARCHIVE,
            family=_ARCHIVE_FAMILY,
            leaf_lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            include_sibling=True,
        )

        decision = LibrarySelectionGate.validate(request)

        self.assertEqual(LibrarySelectionDecisionKind.SELECTED, decision.decision)
        self.assertEqual("leaf-reversal-sibling", decision.selected_leaf_ref)


if __name__ == "__main__":
    unittest.main()
