"""Acceptance tests for provider-neutral managed-artifact planning."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from library.workflow_router.artifact_tree import ArtifactTreeResolver
from library.workflow_router.contracts import (
    ArtifactTreeChildRef,
    ArtifactTreeFamily,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    ArtifactTreeNodeKind,
)
from library.workflow_router.managed_artifact_planning import plan_managed_artifact
from library.workflow_router.target_document_contracts import (
    ArtifactDocumentKind,
    ManagedArtifactAbsentNodeState,
    ManagedArtifactAction,
    ManagedArtifactArchiveRequest,
    ManagedArtifactCreateRequest,
    ManagedArtifactDeleteDocument,
    ManagedArtifactDocumentCreate,
    ManagedArtifactDocumentUpdate,
    ManagedArtifactNodeMutation,
    ManagedArtifactPathSnapshot,
    ManagedArtifactPathTransition,
    ManagedArtifactPlannedResult,
    ManagedArtifactPlanningDecision,
    ManagedArtifactPlanningResult,
    ManagedArtifactPresentNodeState,
    ManagedArtifactRejectedResult,
    ManagedArtifactReplaceRequest,
    ManagedArtifactReviseRequest,
    ManagedArtifactTerminalState,
    derive_document_digest,
)


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "library" / "workflow_router" / "managed_artifact_planning.py"
ELEMENT = ROOT / "modules" / "element" / "python" / "adaptive-project-orchestration" / "09a-managed-artifact-planning"


def _digest(character: str) -> str:
    return "sha256_" + character * 64


def _revision(character: str) -> str:
    return "rev-" + character + "123456789abcdef"


def _content(path: str, character: str) -> str:
    return f"# Managed artifact {path}\nrevision {character}\n"


def _planned(result: ManagedArtifactPlanningResult) -> ManagedArtifactPlannedResult:
    if not isinstance(result, ManagedArtifactPlannedResult):
        raise AssertionError(result)
    return result


def _rejected(result: ManagedArtifactPlanningResult) -> ManagedArtifactRejectedResult:
    if not isinstance(result, ManagedArtifactRejectedResult):
        raise AssertionError(result)
    return result


class ManagedArtifactPlanningTests(unittest.TestCase):
    """Exercise every action and the finite no-plan boundary."""

    @staticmethod
    def _child(
        child_ref: str,
        child_kind: ArtifactTreeNodeKind,
        revision: str,
        digest: str,
        lifecycle: ArtifactTreeLifecycle = ArtifactTreeLifecycle.ACTIVE,
    ) -> ArtifactTreeChildRef:
        return ArtifactTreeChildRef(
            child_ref=child_ref,
            child_kind=child_kind,
            child_revision=revision,
            child_digest=digest,
            child_lifecycle=lifecycle,
        )

    def _present(
        self,
        prefix: str,
        *,
        family: ArtifactTreeFamily = ArtifactTreeFamily.TICKET,
        revision_seed: str = "123",
        digest_seed: str = "123",
        lifecycle: ArtifactTreeLifecycle = ArtifactTreeLifecycle.ACTIVE,
    ) -> ManagedArtifactPathSnapshot:
        root_ref = f"root-{prefix}"
        partition_ref = f"partition-{prefix}"
        leaf_ref = f"leaf-{prefix}"
        root_revision = _revision(revision_seed[0])
        partition_revision = _revision(revision_seed[1])
        leaf_revision = _revision(revision_seed[2])
        root_digest = _digest(digest_seed[0])
        partition_digest = _digest(digest_seed[1])
        leaf_digest = _digest(digest_seed[2])
        leaf = ArtifactTreeNode(
            node_ref=leaf_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.LEAF,
            revision=leaf_revision,
            content_digest=leaf_digest,
            lifecycle=lifecycle,
        )
        partition = ArtifactTreeNode(
            node_ref=partition_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.PARTITION_INDEX,
            revision=partition_revision,
            content_digest=partition_digest,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                self._child(
                    leaf_ref,
                    ArtifactTreeNodeKind.LEAF,
                    leaf_revision,
                    leaf_digest,
                    lifecycle,
                ),
            ),
        )
        root = ArtifactTreeNode(
            node_ref=root_ref,
            family=family,
            node_kind=ArtifactTreeNodeKind.ROOT_INDEX,
            revision=root_revision,
            content_digest=root_digest,
            lifecycle=ArtifactTreeLifecycle.ACTIVE,
            child_refs=(
                self._child(
                    partition_ref,
                    ArtifactTreeNodeKind.PARTITION_INDEX,
                    partition_revision,
                    partition_digest,
                ),
            ),
        )
        return ManagedArtifactPathSnapshot(
            family=family,
            root_ref=root_ref,
            explicit_path_refs=(root_ref, partition_ref, leaf_ref),
            expected_leaf_ref=leaf_ref,
            terminal_state=ManagedArtifactTerminalState.PRESENT,
            path_nodes=(root, partition, leaf),
        )

    def _absent(
        self,
        prefix: str,
        *,
        family: ArtifactTreeFamily = ArtifactTreeFamily.TICKET,
        revision_seed: str = "123",
        digest_seed: str = "123",
    ) -> ManagedArtifactPathSnapshot:
        present = self._present(
            prefix,
            family=family,
            revision_seed=revision_seed,
            digest_seed=digest_seed,
        )
        root, partition, _leaf = present.path_nodes
        assert isinstance(root, ArtifactTreeNode)
        assert isinstance(partition, ArtifactTreeNode)
        return ManagedArtifactPathSnapshot(
            family=family,
            root_ref=present.root_ref,
            explicit_path_refs=present.explicit_path_refs,
            expected_leaf_ref=present.expected_leaf_ref,
            terminal_state=ManagedArtifactTerminalState.ABSENT,
            path_nodes=(
                root,
                partition.model_copy(update={"child_refs": ()}),
            ),
        )

    @staticmethod
    def _transition(
        current: ManagedArtifactPathSnapshot,
        candidate: ManagedArtifactPathSnapshot,
    ) -> ManagedArtifactPathTransition:
        return ManagedArtifactPathTransition(current=current, candidate=candidate)

    def _retarget_digests(
        self,
        snapshot: ManagedArtifactPathSnapshot,
        paths: tuple[str, ...],
        characters: tuple[str, ...],
    ) -> ManagedArtifactPathSnapshot:
        nodes = snapshot.path_nodes
        self.assertEqual(len(nodes), len(paths))
        self.assertEqual(len(nodes), len(characters))
        digests = tuple(
            derive_document_digest(_content(path, character))
            for path, character in zip(paths, characters)
        )
        updated = list(nodes)
        for node_index in range(len(nodes) - 1, -1, -1):
            node = updated[node_index]
            child = updated[node_index + 1] if node_index + 1 < len(updated) else None
            child_refs = tuple(
                edge.model_copy(
                    update={
                        "child_revision": child.revision,
                        "child_digest": digests[node_index + 1],
                        "child_lifecycle": child.lifecycle,
                    }
                )
                if child is not None and edge.child_ref == child.node_ref
                else edge
                for edge in node.child_refs
            )
            updated[node_index] = node.model_copy(
                update={"content_digest": digests[node_index], "child_refs": child_refs}
            )
        return snapshot.model_copy(update={"path_nodes": tuple(updated)})

    @staticmethod
    def _create_document(ref: str, path: str, character: str) -> ManagedArtifactDocumentCreate:
        content = _content(path, character)
        return ManagedArtifactDocumentCreate(
            artifact_ref=ref,
            path=path,
            kind=ArtifactDocumentKind.TICKET,
            content=content,
            content_digest=derive_document_digest(content),
            sealed=False,
        )

    @staticmethod
    def _update_document(
        ref: str,
        path: str,
        before_digest: str,
        character: str,
    ) -> ManagedArtifactDocumentUpdate:
        content = _content(path, character)
        return ManagedArtifactDocumentUpdate(
            artifact_ref=ref,
            path=path,
            kind=ArtifactDocumentKind.TICKET,
            expected_current_digest=before_digest,
            content=content,
            content_digest=derive_document_digest(content),
            sealed=False,
        )

    @staticmethod
    def _delete_document(ref: str, path: str, expected_digest: str) -> ManagedArtifactDeleteDocument:
        return ManagedArtifactDeleteDocument(
            artifact_ref=ref,
            path=path,
            kind=ArtifactDocumentKind.TICKET,
            expected_current_digest=expected_digest,
        )

    @staticmethod
    def _state(node: ArtifactTreeNode) -> ManagedArtifactPresentNodeState:
        return ManagedArtifactPresentNodeState(
            state="PRESENT",
            revision=node.revision,
            content_digest=node.content_digest,
            lifecycle=node.lifecycle,
        )

    @staticmethod
    def _absent_state() -> ManagedArtifactAbsentNodeState:
        return ManagedArtifactAbsentNodeState(state="ABSENT")

    def _mutations_for_create(
        self,
        current: ManagedArtifactPathSnapshot,
        candidate: ManagedArtifactPathSnapshot,
        *,
        paths: tuple[str, str, str] = (
            "modules/tickets/demo/root.md",
            "modules/tickets/demo/partition.md",
            "modules/tickets/demo/leaf.md",
        ),
    ) -> tuple[ManagedArtifactNodeMutation, ...]:
        current_nodes = current.path_nodes
        candidate_nodes = candidate.path_nodes
        assert len(current_nodes) == 2
        assert len(candidate_nodes) == 3
        return (
            ManagedArtifactNodeMutation(
                artifact_ref=current_nodes[0].node_ref,
                expected_state=self._state(current_nodes[0]),
                next_state=self._state(candidate_nodes[0]),
            ),
            ManagedArtifactNodeMutation(
                artifact_ref=current_nodes[1].node_ref,
                expected_state=self._state(current_nodes[1]),
                next_state=self._state(candidate_nodes[1]),
            ),
            ManagedArtifactNodeMutation(
                artifact_ref=candidate.expected_leaf_ref,
                expected_state=self._absent_state(),
                next_state=self._state(candidate_nodes[2]),
            ),
        )

    def _create_request(self) -> ManagedArtifactCreateRequest:
        current = self._absent("create", revision_seed="123", digest_seed="123")
        paths = (
            "modules/tickets/demo/root.md",
            "modules/tickets/demo/partition.md",
            "modules/tickets/demo/leaf.md",
        )
        candidate = self._retarget_digests(
            self._present("create", revision_seed="456", digest_seed="456"),
            paths,
            ("4", "5", "6"),
        )
        current_nodes = current.path_nodes
        candidate_nodes = candidate.path_nodes
        assert len(current_nodes) == 2
        assert len(candidate_nodes) == 3
        documents = (
            self._update_document(
                current_nodes[0].node_ref,
                paths[0],
                current_nodes[0].content_digest,
                "4",
            ),
            self._update_document(
                current_nodes[1].node_ref,
                paths[1],
                current_nodes[1].content_digest,
                "5",
            ),
            self._create_document(
                candidate_nodes[2].node_ref,
                paths[2],
                "6",
            ),
        )
        return ManagedArtifactCreateRequest(
            action="CREATE",
            request_ref="request-create",
            baseline_commit="a" * 40,
            destination_transition=self._transition(current, candidate),
            proposed_document_mutations=documents,
        )

    def test_map1_strict_contracts_round_trip_and_reject_shape_bypasses(self) -> None:
        request = self._create_request()
        self.assertEqual(
            request,
            type(request).model_validate_json(request.model_dump_json()),
        )
        result = plan_managed_artifact(request)
        self.assertEqual(
            result,
            type(result).model_validate_json(result.model_dump_json()),
        )
        with self.assertRaises(ValidationError):
            ManagedArtifactCreateRequest.model_validate(
                {**json.loads(request.model_dump_json()), "unexpected": "field"}
            )
        with self.assertRaises(ValidationError):
            ManagedArtifactPresentNodeState(
                state="PRESENT",
                revision="rev-" + "0" * 16,
                content_digest=_digest("1"),
                lifecycle=ArtifactTreeLifecycle.ACTIVE,
            )
        candidate = request.destination_transition.candidate
        candidate_nodes = candidate.path_nodes
        assert len(candidate_nodes) == 3
        invalid_partition = candidate_nodes[1].model_copy(
            update={"child_refs": ("bad-edge",)}
        )
        invalid_candidate = candidate.model_copy(
            update={
                "path_nodes": (
                    candidate_nodes[0],
                    invalid_partition,
                    candidate_nodes[2],
                )
            }
        )
        nested_invalid = request.model_copy(
            update={
                "destination_transition": self._transition(
                    request.destination_transition.current, invalid_candidate
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID,
            _rejected(plan_managed_artifact(nested_invalid)).decision,
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.ANCESTOR_CASCADE_INCOMPLETE,
            _rejected(plan_managed_artifact(
                request.model_copy(
                    update={
                        "destination_transition": self._transition(
                            self._absent("create-invalid-path"),
                            self._present("create-invalid-path"),
                        )
                    }
                )
            )).decision,
        )

    def test_map2_create_and_revise_are_planned_with_full_cascade(self) -> None:
        create = self._create_request()
        result = _planned(plan_managed_artifact(create))
        self.assertEqual("PLANNED", result.status)
        self.assertEqual(
            tuple(sorted(mutation.artifact_ref for mutation in result.plan.node_mutations)),
            tuple(mutation.artifact_ref for mutation in result.plan.node_mutations),
        )
        self.assertEqual(
            tuple(sorted(mutation.path for mutation in result.plan.document_mutations)),
            tuple(mutation.path for mutation in result.plan.document_mutations),
        )
        current = self._present("revise", revision_seed="123", digest_seed="123")
        revise_paths = (
            "modules/tickets/demo/revise-root.md",
            "modules/tickets/demo/revise-partition.md",
            "modules/tickets/demo/revise-leaf.md",
        )
        candidate = self._retarget_digests(
            self._present("revise", revision_seed="456", digest_seed="456"),
            revise_paths,
            ("4", "5", "6"),
        )
        current_nodes = current.path_nodes
        candidate_nodes = candidate.path_nodes
        assert len(current_nodes) == 3
        assert len(candidate_nodes) == 3
        request = ManagedArtifactReviseRequest(
            action="REVISE",
            request_ref="request-revise",
            baseline_commit="b" * 40,
            selected_transition=self._transition(current, candidate),
            proposed_document_mutations=(
                self._update_document(
                    current_nodes[0].node_ref,
                    revise_paths[0],
                    current_nodes[0].content_digest,
                    "4",
                ),
                self._update_document(
                    current_nodes[1].node_ref,
                    revise_paths[1],
                    current_nodes[1].content_digest,
                    "5",
                ),
                self._update_document(
                    current_nodes[2].node_ref,
                    revise_paths[2],
                    current_nodes[2].content_digest,
                    "6",
                ),
            ),
        )
        revised = _planned(plan_managed_artifact(request))
        self.assertEqual("PLANNED", revised.status)
        self.assertEqual(3, len(revised.plan.node_mutations))
        self.assertEqual(1, len(revised.plan.post_state_snapshots))

    def test_map2_revise_requires_a_changed_active_leaf(self) -> None:
        paths = (
            "modules/tickets/demo/revise-same-root.md",
            "modules/tickets/demo/revise-same-partition.md",
            "modules/tickets/demo/revise-same-leaf.md",
        )
        current = self._retarget_digests(
            self._present("revise-same", revision_seed="123", digest_seed="123"),
            paths,
            ("1", "2", "3"),
        )
        candidate_base = self._retarget_digests(
            self._present("revise-same", revision_seed="456", digest_seed="456"),
            paths,
            ("4", "5", "6"),
        )
        current_nodes = current.path_nodes
        candidate_nodes = candidate_base.path_nodes
        assert len(current_nodes) == 3
        assert len(candidate_nodes) == 3
        candidate_partition = candidate_nodes[1].model_copy(
            update={
                "child_refs": (
                    candidate_nodes[1].child_refs[0].model_copy(
                        update={
                            "child_revision": current_nodes[2].revision,
                            "child_digest": current_nodes[2].content_digest,
                            "child_lifecycle": current_nodes[2].lifecycle,
                        }
                    ),
                )
            }
        )
        candidate = candidate_base.model_copy(
            update={
                "path_nodes": (candidate_nodes[0], candidate_partition, current_nodes[2])
            }
        )
        request = ManagedArtifactReviseRequest(
            action="REVISE",
            request_ref="request-revise-same-leaf",
            baseline_commit="f" * 40,
            selected_transition=self._transition(current, candidate),
            proposed_document_mutations=(
                self._update_document(
                    current_nodes[0].node_ref,
                    paths[0],
                    current_nodes[0].content_digest,
                    "4",
                ),
                self._update_document(
                    current_nodes[1].node_ref,
                    paths[1],
                    current_nodes[1].content_digest,
                    "5",
                ),
                self._update_document(
                    current_nodes[2].node_ref,
                    paths[2],
                    current_nodes[2].content_digest,
                    "6",
                ),
            ),
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.UNRELATED_MUTATION,
            _rejected(plan_managed_artifact(request)).decision,
        )

    def test_map2_present_updates_change_revision_and_digest_together(self) -> None:
        paths = (
            "modules/tickets/demo/revise-pair-root.md",
            "modules/tickets/demo/revise-pair-partition.md",
            "modules/tickets/demo/revise-pair-leaf.md",
        )
        for mutation_kind in ("revision", "digest"):
            current = self._retarget_digests(
                self._present("revise-pair", revision_seed="123", digest_seed="123"),
                paths,
                ("1", "2", "3"),
            )
            candidate_base = self._retarget_digests(
                self._present("revise-pair", revision_seed="456", digest_seed="456"),
                paths,
                ("4", "5", "6"),
            )
            current_nodes = current.path_nodes
            candidate_nodes = candidate_base.path_nodes
            assert len(current_nodes) == 3
            assert len(candidate_nodes) == 3
            leaf = candidate_nodes[2]
            if mutation_kind == "revision":
                leaf = leaf.model_copy(
                    update={"content_digest": current_nodes[2].content_digest}
                )
            else:
                leaf = leaf.model_copy(update={"revision": current_nodes[2].revision})
            partition = candidate_nodes[1].model_copy(
                update={
                    "child_refs": (
                        candidate_nodes[1].child_refs[0].model_copy(
                            update={
                                "child_revision": leaf.revision,
                                "child_digest": leaf.content_digest,
                                "child_lifecycle": leaf.lifecycle,
                            }
                        ),
                    )
                }
            )
            candidate = candidate_base.model_copy(
                update={"path_nodes": (candidate_nodes[0], partition, leaf)}
            )
            leaf_character = "3" if mutation_kind == "revision" else "6"
            request = ManagedArtifactReviseRequest(
                action="REVISE",
                request_ref=f"request-revise-pair-{mutation_kind}",
                baseline_commit="3" * 40,
                selected_transition=self._transition(current, candidate),
                proposed_document_mutations=(
                    self._update_document(
                        current_nodes[0].node_ref,
                        paths[0],
                        current_nodes[0].content_digest,
                        "4",
                    ),
                    self._update_document(
                        current_nodes[1].node_ref,
                        paths[1],
                        current_nodes[1].content_digest,
                        "5",
                    ),
                    self._update_document(
                        current_nodes[2].node_ref,
                        paths[2],
                        current_nodes[2].content_digest,
                        leaf_character,
                    ),
                ),
            )
            self.assertEqual(
                ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
                _rejected(plan_managed_artifact(request)).decision,
            )

    def test_map3_replace_and_archive_have_single_shared_ancestor_updates(self) -> None:
        current = self._present("replace-old", revision_seed="123", digest_seed="123")
        old_paths = (
            "modules/tickets/demo/old-root.md",
            "modules/tickets/demo/old-part.md",
        )
        old_candidate = self._retarget_digests(
            self._absent("replace-old", revision_seed="456", digest_seed="456"),
            old_paths,
            ("4", "5"),
        )
        replacement_current = self._absent("replace-new", revision_seed="123", digest_seed="123")
        new_paths = (
            "modules/tickets/demo/new-root.md",
            "modules/tickets/demo/new-part.md",
            "modules/tickets/demo/new-leaf.md",
        )
        replacement_candidate = self._retarget_digests(
            self._present("replace-new", revision_seed="456", digest_seed="456"),
            new_paths,
            ("4", "5", "6"),
        )
        old_nodes = current.path_nodes
        new_nodes = replacement_candidate.path_nodes
        assert len(old_nodes) == 3
        assert len(new_nodes) == 3
        replace = ManagedArtifactReplaceRequest(
            action="REPLACE",
            request_ref="request-replace",
            baseline_commit="c" * 40,
            current_transition=self._transition(current, old_candidate),
            replacement_transition=self._transition(replacement_current, replacement_candidate),
            proposed_document_mutations=(
                self._update_document(old_nodes[0].node_ref, old_paths[0], current.path_nodes[0].content_digest, "4"),
                self._update_document(old_nodes[1].node_ref, old_paths[1], current.path_nodes[1].content_digest, "5"),
                self._delete_document(old_nodes[2].node_ref, "modules/tickets/demo/old-leaf.md", old_nodes[2].content_digest),
                self._update_document(new_nodes[0].node_ref, new_paths[0], replacement_current.path_nodes[0].content_digest, "4"),
                self._update_document(new_nodes[1].node_ref, new_paths[1], replacement_current.path_nodes[1].content_digest, "5"),
                self._create_document(new_nodes[2].node_ref, new_paths[2], "6"),
            ),
        )
        replacement = _planned(plan_managed_artifact(replace))
        self.assertEqual("PLANNED", replacement.status)
        self.assertEqual(6, len(replacement.plan.node_mutations))

        active = self._present("archive-active", revision_seed="123", digest_seed="123")
        inactive = self._retarget_digests(
            self._absent("archive-active", revision_seed="456", digest_seed="456"),
            ("modules/tickets/demo/active-root.md", "modules/tickets/demo/active-part.md"),
            ("4", "5"),
        )
        archive_current = self._absent(
            "archive-leaf",
            family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
            revision_seed="123",
            digest_seed="123",
        )
        archive_candidate = self._retarget_digests(
            self._present(
                "archive-leaf",
                family=ArtifactTreeFamily.ARCHIVE_LIBRARY,
                revision_seed="456",
                digest_seed="456",
                lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            ),
            (
                "modules/tickets/demo/archive-root.md",
                "modules/tickets/demo/archive-part.md",
                "modules/tickets/demo/archive-leaf.md",
            ),
            ("4", "5", "6"),
        )
        active_nodes = active.path_nodes
        archive_nodes = archive_candidate.path_nodes
        assert len(active_nodes) == 3
        assert len(archive_nodes) == 3
        archive = ManagedArtifactArchiveRequest(
            action="ARCHIVE",
            request_ref="request-archive",
            baseline_commit="d" * 40,
            active_transition=self._transition(active, inactive),
            archive_transition=self._transition(archive_current, archive_candidate),
            proposed_document_mutations=(
                self._update_document(active_nodes[0].node_ref, "modules/tickets/demo/active-root.md", active.path_nodes[0].content_digest, "4"),
                self._update_document(active_nodes[1].node_ref, "modules/tickets/demo/active-part.md", active.path_nodes[1].content_digest, "5"),
                self._delete_document(active_nodes[2].node_ref, "modules/tickets/demo/active-leaf.md", active_nodes[2].content_digest),
                self._update_document(archive_nodes[0].node_ref, "modules/tickets/demo/archive-root.md", archive_current.path_nodes[0].content_digest, "4"),
                self._update_document(archive_nodes[1].node_ref, "modules/tickets/demo/archive-part.md", archive_current.path_nodes[1].content_digest, "5"),
                self._create_document(archive_nodes[2].node_ref, "modules/tickets/demo/archive-leaf.md", "6"),
            ),
        )
        archived = _planned(plan_managed_artifact(archive))
        self.assertEqual("PLANNED", archived.status)
        self.assertEqual(6, len(archived.plan.node_mutations))

    def test_map4_path_tree_edge_and_lifecycle_errors_reject_without_plan(self) -> None:
        request = self._create_request()
        current = self._absent("bad-path")
        root = current.path_nodes[0]
        bad_current = ManagedArtifactPathSnapshot.model_construct(
            family=current.family,
            root_ref=current.root_ref,
            explicit_path_refs=current.explicit_path_refs,
            expected_leaf_ref=current.expected_leaf_ref,
            terminal_state=current.terminal_state,
            path_nodes=(root,),
        )
        rejected = _rejected(plan_managed_artifact(
            request.model_copy(
                update={
                    "destination_transition": ManagedArtifactPathTransition.model_construct(
                        current=bad_current,
                        candidate=self._present("bad-path", revision_seed="456", digest_seed="456"),
                    )
                }
            )
        ))
        self.assertEqual(
            ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID, rejected.decision
        )

        present = self._present("bad-terminal")
        absent_with_terminal_edge = self._absent("bad-terminal").model_copy(
            update={"path_nodes": present.path_nodes[:2]}
        )
        rejected = _rejected(plan_managed_artifact(
            request.model_copy(
                update={
                    "destination_transition": self._transition(
                        absent_with_terminal_edge,
                        present,
                    )
                }
            )
        ))
        self.assertEqual(ManagedArtifactPlanningDecision.PATH_INVALID, rejected.decision)

        wrong_kind = present.path_nodes[1].model_copy(
            update={"node_kind": ArtifactTreeNodeKind.LEAF, "child_refs": ()}
        )
        wrong_present = present.model_copy(
            update={"path_nodes": (present.path_nodes[0], wrong_kind, present.path_nodes[2])}
        )
        rejected = _rejected(plan_managed_artifact(
            request.model_copy(
                update={
                    "destination_transition": self._transition(
                        self._absent("wrong-kind"),
                        wrong_present.model_copy(
                            update={
                                "root_ref": "root-wrong-kind",
                                "explicit_path_refs": (
                                    "root-wrong-kind",
                                    "partition-wrong-kind",
                                    "leaf-wrong-kind",
                                ),
                                "expected_leaf_ref": "leaf-wrong-kind",
                            }
                        ),
                    )
                }
            )
        ))
        self.assertIn(
            rejected.decision,
            (ManagedArtifactPlanningDecision.PATH_INVALID, ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID),
        )

        lifecycle_candidate = self._present(
            "bad-lifecycle",
            revision_seed="456",
            digest_seed="456",
            lifecycle=ArtifactTreeLifecycle.CLOSED,
        )
        lifecycle_request = request.model_copy(
            update={
                "destination_transition": self._transition(
                    self._absent("bad-lifecycle"), lifecycle_candidate
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.LIFECYCLE_INVALID,
            _rejected(plan_managed_artifact(lifecycle_request)).decision,
        )

    def test_map4_revise_lifecycle_and_replace_source_must_remain_active(self) -> None:
        paths = (
            "modules/tickets/demo/revise-life-root.md",
            "modules/tickets/demo/revise-life-partition.md",
            "modules/tickets/demo/revise-life-leaf.md",
        )
        current = self._retarget_digests(
            self._present("revise-life", revision_seed="123", digest_seed="123"),
            paths,
            ("1", "2", "3"),
        )
        archived = self._retarget_digests(
            self._present(
                "revise-life",
                revision_seed="456",
                digest_seed="456",
                lifecycle=ArtifactTreeLifecycle.ARCHIVED,
            ),
            paths,
            ("4", "5", "6"),
        )
        current_nodes = current.path_nodes
        archived_nodes = archived.path_nodes
        assert len(current_nodes) == 3
        assert len(archived_nodes) == 3
        revise = ManagedArtifactReviseRequest(
            action="REVISE",
            request_ref="request-revise-life",
            baseline_commit="1" * 40,
            selected_transition=self._transition(current, archived),
            proposed_document_mutations=(
                self._update_document(
                    current_nodes[0].node_ref,
                    paths[0],
                    current_nodes[0].content_digest,
                    "4",
                ),
                self._update_document(
                    current_nodes[1].node_ref,
                    paths[1],
                    current_nodes[1].content_digest,
                    "5",
                ),
                self._update_document(
                    current_nodes[2].node_ref,
                    paths[2],
                    current_nodes[2].content_digest,
                    "6",
                ),
            ),
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.LIFECYCLE_INVALID,
            _rejected(plan_managed_artifact(revise)).decision,
        )

        old_paths = (
            "modules/tickets/demo/closed-old-root.md",
            "modules/tickets/demo/closed-old-partition.md",
            "modules/tickets/demo/closed-old-leaf.md",
        )
        closed_current = self._retarget_digests(
            self._present(
                "closed-old",
                revision_seed="123",
                digest_seed="123",
                lifecycle=ArtifactTreeLifecycle.CLOSED,
            ),
            old_paths,
            ("1", "2", "3"),
        )
        closed_candidate = self._retarget_digests(
            self._absent("closed-old", revision_seed="456", digest_seed="456"),
            old_paths[:2],
            ("4", "5"),
        )
        new_paths = (
            "modules/tickets/demo/closed-new-root.md",
            "modules/tickets/demo/closed-new-partition.md",
            "modules/tickets/demo/closed-new-leaf.md",
        )
        replacement_current = self._absent("closed-new", revision_seed="123", digest_seed="123")
        replacement_candidate = self._retarget_digests(
            self._present("closed-new", revision_seed="456", digest_seed="456"),
            new_paths,
            ("4", "5", "6"),
        )
        closed_nodes = closed_current.path_nodes
        replacement_nodes = replacement_candidate.path_nodes
        assert len(closed_nodes) == 3
        assert len(replacement_nodes) == 3
        replace = ManagedArtifactReplaceRequest(
            action="REPLACE",
            request_ref="request-replace-closed",
            baseline_commit="2" * 40,
            current_transition=self._transition(closed_current, closed_candidate),
            replacement_transition=self._transition(
                replacement_current, replacement_candidate
            ),
            proposed_document_mutations=(
                self._update_document(
                    closed_nodes[0].node_ref,
                    old_paths[0],
                    closed_nodes[0].content_digest,
                    "4",
                ),
                self._update_document(
                    closed_nodes[1].node_ref,
                    old_paths[1],
                    closed_nodes[1].content_digest,
                    "5",
                ),
                self._delete_document(
                    closed_nodes[2].node_ref,
                    old_paths[2],
                    closed_nodes[2].content_digest,
                ),
                self._update_document(
                    replacement_nodes[0].node_ref,
                    new_paths[0],
                    replacement_current.path_nodes[0].content_digest,
                    "4",
                ),
                self._update_document(
                    replacement_nodes[1].node_ref,
                    new_paths[1],
                    replacement_current.path_nodes[1].content_digest,
                    "5",
                ),
                self._create_document(replacement_nodes[2].node_ref, new_paths[2], "6"),
            ),
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.LIFECYCLE_INVALID,
            _rejected(plan_managed_artifact(replace)).decision,
        )

    def test_map5_cascade_and_unrelated_mutations_are_rejected(self) -> None:
        request = self._create_request()
        plan = plan_managed_artifact(request)
        self.assertEqual("PLANNED", plan.status)
        incomplete_candidate = self._present("create", revision_seed="123", digest_seed="123")
        incomplete = request.model_copy(
            update={
                "destination_transition": ManagedArtifactPathTransition.model_construct(
                    current=request.destination_transition.current,
                    candidate=incomplete_candidate,
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.ANCESTOR_CASCADE_INCOMPLETE,
            _rejected(plan_managed_artifact(incomplete)).decision,
        )
        unrelated = request.model_copy(
            update={
                "proposed_document_mutations": request.proposed_document_mutations
                + (self._create_document("sibling-create", "modules/tickets/demo/sibling.md", "7"),)
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.UNRELATED_MUTATION,
            _rejected(plan_managed_artifact(unrelated)).decision,
        )

    def test_map6_document_bindings_and_digest_modes_are_exact(self) -> None:
        request = self._create_request()
        missing = request.model_copy(
            update={"proposed_document_mutations": request.proposed_document_mutations[:2]}
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
            _rejected(plan_managed_artifact(missing)).decision,
        )
        duplicate = request.model_copy(
            update={
                "proposed_document_mutations": request.proposed_document_mutations
                + (request.proposed_document_mutations[0],)
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
            _rejected(plan_managed_artifact(duplicate)).decision,
        )
        candidate = request.destination_transition.candidate
        current = request.destination_transition.current
        candidate_nodes = candidate.path_nodes
        current_nodes = current.path_nodes
        assert len(candidate_nodes) == 3
        assert len(current_nodes) == 2
        shared_content = "same candidate bytes\n"
        shared_digest = derive_document_digest(shared_content)
        shared_root = candidate_nodes[0].model_copy(
            update={
                "content_digest": shared_digest,
                "child_refs": tuple(
                    edge.model_copy(update={"child_digest": shared_digest})
                    if edge.child_ref == candidate_nodes[1].node_ref
                    else edge
                    for edge in candidate_nodes[0].child_refs
                ),
            }
        )
        shared_partition = candidate_nodes[1].model_copy(
            update={"content_digest": shared_digest}
        )
        shared_candidate = candidate.model_copy(
            update={"path_nodes": (shared_root, shared_partition, candidate_nodes[2])}
        )
        duplicate_candidate_digest = request.model_copy(
            update={
                "destination_transition": self._transition(current, shared_candidate),
                "proposed_document_mutations": (
                    ManagedArtifactDocumentUpdate(
                        artifact_ref=current_nodes[0].node_ref,
                        path="modules/tickets/demo/root.md",
                        kind=ArtifactDocumentKind.TICKET,
                        expected_current_digest=current_nodes[0].content_digest,
                        content=shared_content,
                        content_digest=shared_digest,
                        sealed=False,
                    ),
                    ManagedArtifactDocumentUpdate(
                        artifact_ref=current_nodes[1].node_ref,
                        path="modules/tickets/demo/partition.md",
                        kind=ArtifactDocumentKind.TICKET,
                        expected_current_digest=current_nodes[1].content_digest,
                        content=shared_content,
                        content_digest=shared_digest,
                        sealed=False,
                    ),
                    request.proposed_document_mutations[2],
                ),
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
            _rejected(plan_managed_artifact(duplicate_candidate_digest)).decision,
        )
        with self.assertRaises(ValidationError):
            ManagedArtifactDocumentUpdate(
                artifact_ref="root-create",
                path="modules/tickets/demo/root.md",
                kind=ArtifactDocumentKind.TICKET,
                expected_current_digest=_digest("1"),
                content="bad\r\nnewline\n",
                content_digest=derive_document_digest("bad\nnewline\n"),
                sealed=False,
            )
        for bad_path in (
            "modules/tickets/demo//leaf.md",
            "modules/tickets/demo/",
        ):
            with self.assertRaises(ValidationError):
                ManagedArtifactDocumentCreate(
                    artifact_ref="bad-create-path",
                    path=bad_path,
                    kind=ArtifactDocumentKind.TICKET,
                    content="new\n",
                    content_digest=derive_document_digest("new\n"),
                    sealed=False,
                )
            with self.assertRaises(ValidationError):
                ManagedArtifactDocumentUpdate(
                    artifact_ref="bad-update-path",
                    path=bad_path,
                    kind=ArtifactDocumentKind.TICKET,
                    expected_current_digest=_digest("1"),
                    content="new\n",
                    content_digest=derive_document_digest("new\n"),
                    sealed=False,
                )
            with self.assertRaises(ValidationError):
                ManagedArtifactDeleteDocument(
                    artifact_ref="bad-delete-path",
                    path=bad_path,
                    kind=ArtifactDocumentKind.TICKET,
                    expected_current_digest=_digest("1"),
                )
        with self.assertRaises(ValidationError):
            ManagedArtifactDeleteDocument.model_validate(
                {
                    "artifact_ref": "leaf-create",
                    "path": "modules/tickets/demo/leaf.md",
                    "kind": "TICKET",
                    "expected_current_digest": _digest("1"),
                    "content": "must not exist",
                }
            )
        stale = request.model_copy(
            update={
                "proposed_document_mutations": (
                    self._update_document(
                        "root-create",
                        "modules/tickets/demo/root.md",
                        _digest("9"),
                        "4",
                    ),
                    request.proposed_document_mutations[1],
                    request.proposed_document_mutations[2],
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
            _rejected(plan_managed_artifact(stale)).decision,
        )

    def test_map7_source_and_package_boundaries_are_effect_free(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        entry_points = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "plan_managed_artifact"
        ]
        self.assertEqual(1, len(entry_points))
        self.assertEqual(1, len(entry_points[0].args.args))
        handlers = [node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)]
        for handler in handlers:
            if not isinstance(handler.type, ast.Name):
                raise AssertionError("boundary catches must name ValidationError exactly")
            self.assertEqual("ValidationError", handler.type.id)
        with patch(
            "library.workflow_router.managed_artifact_planning._transition_check",
            side_effect=TypeError("programming failure"),
        ):
            with self.assertRaises(TypeError):
                plan_managed_artifact(self._create_request())
        for forbidden in (
            "typing.Any",
            "object",
            "typing.cast",
            "dict",
            "import os",
            "from os",
            "subprocess",
            "socket",
            "requests",
            "import pathlib",
            "open(",
            "git",
            "filesystem",
            "network",
            "environment",
            "provider",
            "runner",
            "queue",
            "receipt",
            "hook",
            "write_text",
        ):
            self.assertNotIn(forbidden.casefold(), source.casefold(), forbidden)
        package_init = (ROOT / "library" / "workflow_router" / "__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("managed_artifact", package_init)
        self.assertIn("ArtifactTreeResolver.resolve", source)

    def test_map8_element_index_names_exact_authority_and_effect_boundary(self) -> None:
        index_files = tuple(sorted(ELEMENT.glob("*")))
        self.assertTrue(index_files)
        index = "\n".join(path.read_text(encoding="utf-8") for path in index_files if path.is_file()).casefold()
        for term in (
            "TICKET-ADAPTIVE-R09A-MANAGED-ARTIFACT-PLANNING",
            "SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION",
            "CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09",
            "managed_artifact_planning.py",
            "test_managed_artifact_planning.py",
            "planning is not persistence",
            "no authority",
        ):
            self.assertIn(term.casefold(), index)

    def test_mpm1_missing_prefix_never_becomes_terminal_absence(self) -> None:
        request = self._create_request()
        current = self._absent("mpm1")
        broken_root = current.path_nodes[0].model_copy(update={"child_refs": ()})
        broken = current.model_copy(update={"path_nodes": (broken_root, current.path_nodes[1])})
        result = _rejected(plan_managed_artifact(
            request.model_copy(
                update={
                    "destination_transition": self._transition(
                        broken,
                        self._present("mpm1", revision_seed="456", digest_seed="456"),
                    )
                }
            )
        ))
        self.assertEqual(ManagedArtifactPlanningDecision.PATH_INVALID, result.decision)

    def test_mpm2_omitting_one_cascade_document_is_not_planned(self) -> None:
        request = self._create_request()
        candidate = self._present("create", revision_seed="123", digest_seed="123")
        omitted = request.model_copy(
            update={
                "destination_transition": ManagedArtifactPathTransition.model_construct(
                    current=request.destination_transition.current,
                    candidate=candidate,
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.ANCESTOR_CASCADE_INCOMPLETE,
            _rejected(plan_managed_artifact(omitted)).decision,
        )

    def test_mpm3_delete_content_or_wrong_digest_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ManagedArtifactDeleteDocument.model_validate(
                {
                    "artifact_ref": "leaf-delete",
                    "path": "modules/tickets/demo/leaf.md",
                    "kind": "TICKET",
                    "expected_current_digest": _digest("1"),
                    "content_digest": _digest("2"),
                }
            )
        request = self._create_request()
        bad = request.model_copy(
            update={
                "proposed_document_mutations": (
                    self._update_document("root-create", "modules/tickets/demo/root.md", _digest("9"), "4"),
                    request.proposed_document_mutations[1],
                    request.proposed_document_mutations[2],
                )
            }
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH,
            _rejected(plan_managed_artifact(bad)).decision,
        )

    def test_mpm4_shared_ancestor_candidate_disagreement_is_tree_invalid(self) -> None:
        current = self._present("shared-old", revision_seed="123", digest_seed="123")
        first = self._absent("shared-old", revision_seed="456", digest_seed="456")
        replacement_current_base = self._absent(
            "shared-new", revision_seed="123", digest_seed="123"
        )
        replacement_current = replacement_current_base.model_copy(
            update={
                "root_ref": current.root_ref,
                "explicit_path_refs": (
                    current.root_ref,
                    current.path_nodes[1].node_ref,
                    "leaf-shared-new",
                ),
                "expected_leaf_ref": "leaf-shared-new",
                "path_nodes": (
                    current.path_nodes[0],
                    current.path_nodes[1].model_copy(update={"child_refs": ()}),
                ),
            }
        )
        candidate_base = self._present("shared-new", revision_seed="789", digest_seed="789")
        candidate_root = candidate_base.path_nodes[0].model_copy(
            update={
                "node_ref": current.root_ref,
                "child_refs": (
                    candidate_base.path_nodes[0].child_refs[0].model_copy(
                        update={"child_ref": current.path_nodes[1].node_ref}
                    ),
                ),
            }
        )
        candidate_partition = candidate_base.path_nodes[1].model_copy(
            update={"node_ref": current.path_nodes[1].node_ref}
        )
        second = candidate_base.model_copy(
            update={
                "root_ref": current.root_ref,
                "explicit_path_refs": (
                    current.root_ref,
                    current.path_nodes[1].node_ref,
                    "leaf-shared-new",
                ),
                "expected_leaf_ref": "leaf-shared-new",
                "path_nodes": (candidate_root, candidate_partition, candidate_base.path_nodes[2]),
            }
        )
        request = ManagedArtifactReplaceRequest(
            action="REPLACE",
            request_ref="request-mpm4",
            baseline_commit="e" * 40,
            current_transition=self._transition(current, first),
            replacement_transition=self._transition(replacement_current, second),
            proposed_document_mutations=(
                self._create_document("leaf-shared", "modules/tickets/demo/leaf.md", "6"),
            ),
        )
        self.assertEqual(
            ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID,
            _rejected(plan_managed_artifact(request)).decision,
        )

    def test_map7_never_calls_resolver_for_an_absent_snapshot_prefix(self) -> None:
        request = self._create_request()
        with patch.object(ArtifactTreeResolver, "resolve", wraps=ArtifactTreeResolver.resolve) as resolver:
            result = plan_managed_artifact(request)
        self.assertEqual("PLANNED", result.status)
        self.assertEqual(1, resolver.call_count)


if __name__ == "__main__":
    unittest.main()
