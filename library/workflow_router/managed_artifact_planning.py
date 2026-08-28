"""Pure semantic planning for one managed artifact-tree operation."""

from __future__ import annotations

from typing import NamedTuple

from pydantic import TypeAdapter, ValidationError

from .artifact_tree import ArtifactTreeResolver
from .contracts import (
    ArtifactTreeChildRef,
    ArtifactTreeDecisionKind,
    ArtifactTreeInvalidReason,
    ArtifactTreeLifecycle,
    ArtifactTreeNode,
    ArtifactTreeNodeKind,
    ArtifactTreeResolutionRequest,
    OpaqueMetadataId,
    ReviewedCommitReference,
)

from .target_document_contracts import (
    ManagedArtifactAction,
    ManagedArtifactArchivePlan,
    ManagedArtifactArchiveRequest,
    ManagedArtifactAbsentNodeState,
    ManagedArtifactCreatePlan,
    ManagedArtifactCreateRequest,
    ManagedArtifactDeleteDocument,
    ManagedArtifactDocumentCreate,
    ManagedArtifactDocumentMutation,
    ManagedArtifactDocumentUpdate,
    ManagedArtifactNodeMutation,
    ManagedArtifactNodeState,
    ManagedArtifactPathSnapshot,
    ManagedArtifactPathTransition,
    ManagedArtifactPlan,
    ManagedArtifactPlannedResult,
    ManagedArtifactPlanningDecision,
    ManagedArtifactPlanningResult,
    ManagedArtifactPresentNodeState,
    ManagedArtifactRejectedResult,
    ManagedArtifactReplacePlan,
    ManagedArtifactReplaceRequest,
    ManagedArtifactRequest,
    ManagedArtifactRevisePlan,
    ManagedArtifactReviseRequest,
    ManagedArtifactTerminalState,
)


_REQUEST_ADAPTER: TypeAdapter[ManagedArtifactRequest] = TypeAdapter(ManagedArtifactRequest)


class _NodeStateRecord(NamedTuple):
    """One explicit artifact reference and its state."""

    artifact_ref: OpaqueMetadataId
    state: ManagedArtifactNodeState


class _SnapshotCheck(NamedTuple):
    """Validated snapshot records or one finite rejection."""

    records: tuple[_NodeStateRecord, ...]
    failure: ManagedArtifactPlanningDecision | None


class _TransitionCheck(NamedTuple):
    """A validated current/candidate transition and its state records."""

    transition: ManagedArtifactPathTransition
    current_records: tuple[_NodeStateRecord, ...]
    candidate_records: tuple[_NodeStateRecord, ...]


class _TransitionCheckResult(NamedTuple):
    """A validated transition or its exact path/tree failure."""

    check: _TransitionCheck | None
    failure: ManagedArtifactPlanningDecision | None


class _RequestDetails(NamedTuple):
    """Action slots and proposed byte mutations selected by one request."""

    action: ManagedArtifactAction
    baseline_commit: ReviewedCommitReference
    transitions: tuple[ManagedArtifactPathTransition, ...]
    documents: tuple[ManagedArtifactDocumentMutation, ...]


class _MergeCheck(NamedTuple):
    """Merged same-direction states or one conflicting-tree rejection."""

    records: tuple[_NodeStateRecord, ...]
    failure: ManagedArtifactPlanningDecision | None


def _invalid(failure: ManagedArtifactPlanningDecision) -> _SnapshotCheck:
    return _SnapshotCheck(records=(), failure=failure)


def _node_kind_is_expected(
    nodes: tuple[ArtifactTreeNode, ...], terminal_state: ManagedArtifactTerminalState
) -> bool:
    """Require root, partition and optional leaf roles in path order."""

    for node_index, node in enumerate(nodes):
        expected_kind = (
            ArtifactTreeNodeKind.ROOT_INDEX
            if node_index == 0
            else (
                ArtifactTreeNodeKind.LEAF
                if terminal_state is ManagedArtifactTerminalState.PRESENT
                and node_index == len(nodes) - 1
                else ArtifactTreeNodeKind.PARTITION_INDEX
            )
        )
        if node.node_kind is not expected_kind:
            return False
    return True


def _matching_edges(
    parent: ArtifactTreeNode, child_ref: OpaqueMetadataId
) -> tuple[ArtifactTreeChildRef, ...]:
    """Select direct edges for one explicit child without discovering siblings."""

    return tuple(edge for edge in parent.child_refs if edge.child_ref == child_ref)


def _edge_matches(parent: ArtifactTreeNode, child: ArtifactTreeNode) -> tuple[bool, bool]:
    """Return whether one selected edge exists and whether its metadata is exact."""

    matches = _matching_edges(parent, child.node_ref)
    if len(matches) != 1:
        return (bool(matches), False)
    edge = matches[0]
    return (
        True,
        edge.child_kind is child.node_kind
        and edge.child_revision == child.revision
        and edge.child_digest == child.content_digest
        and edge.child_lifecycle is child.lifecycle,
    )


def _has_repeated_child_refs(node: ArtifactTreeNode) -> bool:
    child_refs = tuple(edge.child_ref for edge in node.child_refs)
    return len(child_refs) != len(set(child_refs))


def _has_path_cycle(nodes: tuple[ArtifactTreeNode, ...]) -> bool:
    prior_refs: tuple[OpaqueMetadataId, ...] = ()
    for node in nodes:
        if any(edge.child_ref in prior_refs or edge.child_ref == node.node_ref for edge in node.child_refs):
            return True
        prior_refs += (node.node_ref,)
    return False


def _present_records(nodes: tuple[ArtifactTreeNode, ...]) -> tuple[_NodeStateRecord, ...]:
    return tuple(
        _NodeStateRecord(
            artifact_ref=node.node_ref,
            state=ManagedArtifactPresentNodeState(
                state="PRESENT",
                revision=node.revision,
                content_digest=node.content_digest,
                lifecycle=node.lifecycle,
            ),
        )
        for node in nodes
    )


def _revalidate_child_ref(edge: ArtifactTreeChildRef) -> ArtifactTreeChildRef | None:
    """Reconstruct one historical edge so nested RouterModel values are strict again."""

    if not {
        "child_ref",
        "child_kind",
        "child_revision",
        "child_digest",
        "child_lifecycle",
    }.issubset(edge.__pydantic_fields_set__):
        return None
    try:
        return ArtifactTreeChildRef(
            child_ref=edge.child_ref,
            child_kind=edge.child_kind,
            child_revision=edge.child_revision,
            child_digest=edge.child_digest,
            child_lifecycle=edge.child_lifecycle,
        )
    except ValidationError:
        return None


def _revalidate_node(node: ArtifactTreeNode) -> ArtifactTreeNode | None:
    """Reconstruct one node and every edge to close the historical-instance gap."""

    if not {
        "node_ref",
        "family",
        "node_kind",
        "revision",
        "content_digest",
        "lifecycle",
    }.issubset(node.__pydantic_fields_set__):
        return None
    child_refs = node.child_refs
    if not isinstance(child_refs, tuple):
        return None
    validated_edges: tuple[ArtifactTreeChildRef, ...] = ()
    for edge in child_refs:
        if not isinstance(edge, ArtifactTreeChildRef):
            return None
        validated_edge = _revalidate_child_ref(edge)
        if validated_edge is None:
            return None
        validated_edges += (validated_edge,)
    try:
        return ArtifactTreeNode(
            node_ref=node.node_ref,
            family=node.family,
            node_kind=node.node_kind,
            revision=node.revision,
            content_digest=node.content_digest,
            lifecycle=node.lifecycle,
            child_refs=validated_edges,
        )
    except ValidationError:
        return None


def _snapshot_records(snapshot: ManagedArtifactPathSnapshot) -> _SnapshotCheck:
    """Validate one complete present path or one complete absent prefix."""

    refs = snapshot.explicit_path_refs
    nodes = snapshot.path_nodes
    if len(refs) < 3 or len(refs) != len(set(refs)):
        return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
    if refs[0] != snapshot.root_ref or refs[-1] != snapshot.expected_leaf_ref:
        return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
    if any(not isinstance(node, ArtifactTreeNode) for node in nodes):
        return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    revalidated_nodes: tuple[ArtifactTreeNode, ...] = ()
    for node in nodes:
        if not isinstance(node, ArtifactTreeNode):
            return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
        revalidated_node = _revalidate_node(node)
        if revalidated_node is None:
            return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
        revalidated_nodes += (revalidated_node,)
    nodes = revalidated_nodes
    if not isinstance(snapshot.terminal_state, ManagedArtifactTerminalState):
        return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
    node_refs = tuple(node.node_ref for node in nodes)
    expected_node_count = (
        len(refs)
        if snapshot.terminal_state is ManagedArtifactTerminalState.PRESENT
        else len(refs) - 1
    )
    if len(nodes) != expected_node_count or node_refs != refs[:expected_node_count]:
        return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
    if len(node_refs) != len(set(node_refs)):
        return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    if not _node_kind_is_expected(nodes, snapshot.terminal_state):
        return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    if any(node.family is not snapshot.family for node in nodes):
        return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    if any(_has_repeated_child_refs(node) for node in nodes) or _has_path_cycle(nodes):
        return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)

    if snapshot.terminal_state is ManagedArtifactTerminalState.PRESENT:
        resolution = ArtifactTreeResolver.resolve(
            ArtifactTreeResolutionRequest(
                request_ref="r09a-path-check",
                family=snapshot.family,
                root_ref=snapshot.root_ref,
                explicit_path_refs=refs,
                expected_leaf_ref=snapshot.expected_leaf_ref,
                path_nodes=nodes,
            )
        )
        if resolution.decision is ArtifactTreeDecisionKind.ARTIFACT_PATH_NOT_FOUND:
            return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
        if resolution.decision is ArtifactTreeDecisionKind.ARTIFACT_TREE_INVALID:
            if resolution.invalid_reason is ArtifactTreeInvalidReason.EDGE_METADATA_MISMATCH:
                return _invalid(ManagedArtifactPlanningDecision.EDGE_INVALID)
            return _invalid(ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
        return _SnapshotCheck(records=_present_records(nodes), failure=None)

    for parent, child in zip(nodes, nodes[1:]):
        exists, exact = _edge_matches(parent, child)
        if not exists:
            return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
        if not exact:
            return _invalid(ManagedArtifactPlanningDecision.EDGE_INVALID)
    terminal_edges = _matching_edges(nodes[-1], snapshot.expected_leaf_ref)
    if terminal_edges:
        return _invalid(ManagedArtifactPlanningDecision.PATH_INVALID)
    return _SnapshotCheck(
        records=_present_records(nodes)
        + (
            _NodeStateRecord(
                artifact_ref=snapshot.expected_leaf_ref,
                state=ManagedArtifactAbsentNodeState(state="ABSENT"),
            ),
        ),
        failure=None,
    )


def _same_path(left: ManagedArtifactPathSnapshot, right: ManagedArtifactPathSnapshot) -> bool:
    return (
        left.family is right.family
        and left.root_ref == right.root_ref
        and left.explicit_path_refs == right.explicit_path_refs
        and left.expected_leaf_ref == right.expected_leaf_ref
    )


def _unselected_edges_are_preserved(transition: _TransitionCheck) -> bool:
    """Require candidate snapshots to preserve every edge outside the selected path."""

    current_nodes = transition.transition.current.path_nodes
    candidate_nodes = transition.transition.candidate.path_nodes
    path_refs = transition.transition.current.explicit_path_refs
    for node_index, (current_node, candidate_node) in enumerate(
        zip(current_nodes, candidate_nodes)
    ):
        selected_ref = path_refs[node_index + 1] if node_index + 1 < len(path_refs) else None
        current_unselected = tuple(
            edge for edge in current_node.child_refs if edge.child_ref != selected_ref
        )
        candidate_unselected = tuple(
            edge for edge in candidate_node.child_refs if edge.child_ref != selected_ref
        )
        if current_unselected != candidate_unselected:
            return False
    return True


def _node_metadata_is_consistent(
    checks: tuple[_TransitionCheck, ...], candidate: bool
) -> bool:
    """Reject competing full node metadata for one repeated artifact reference."""

    seen: tuple[tuple[OpaqueMetadataId, ArtifactTreeNode], ...] = ()
    for check in checks:
        nodes = (
            check.transition.candidate.path_nodes
            if candidate
            else check.transition.current.path_nodes
        )
        for node in nodes:
            previous = next(
                (known for ref, known in seen if ref == node.node_ref),
                None,
            )
            if previous is None:
                seen += ((node.node_ref, node),)
            elif previous != node:
                return False
    return True


def _transition_check(transition: ManagedArtifactPathTransition) -> _TransitionCheckResult:
    current = _snapshot_records(transition.current)
    if current.failure is not None:
        return _TransitionCheckResult(check=None, failure=current.failure)
    candidate = _snapshot_records(transition.candidate)
    if candidate.failure is not None:
        return _TransitionCheckResult(check=None, failure=candidate.failure)
    if not _same_path(transition.current, transition.candidate):
        return _TransitionCheckResult(
            check=None,
            failure=ManagedArtifactPlanningDecision.PATH_INVALID,
        )
    return _TransitionCheckResult(
        check=_TransitionCheck(
            transition=transition,
            current_records=current.records,
            candidate_records=candidate.records,
        ),
        failure=None,
    )


def _find_state(
    records: tuple[_NodeStateRecord, ...], artifact_ref: OpaqueMetadataId
) -> ManagedArtifactNodeState | None:
    for record in records:
        if record.artifact_ref == artifact_ref:
            return record.state
    return None


def _state_or_absent(
    records: tuple[_NodeStateRecord, ...], artifact_ref: OpaqueMetadataId
) -> ManagedArtifactNodeState:
    found = _find_state(records, artifact_ref)
    if found is not None:
        return found
    return ManagedArtifactAbsentNodeState(state="ABSENT")


def _merge(records_groups: tuple[tuple[_NodeStateRecord, ...], ...]) -> _MergeCheck:
    merged: tuple[_NodeStateRecord, ...] = ()
    for group in records_groups:
        for record in group:
            previous = _find_state(merged, record.artifact_ref)
            if previous is None:
                merged += (record,)
            elif previous != record.state:
                return _MergeCheck(
                    records=(),
                    failure=ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID,
                )
    return _MergeCheck(records=merged, failure=None)


def _details(request: ManagedArtifactRequest) -> _RequestDetails:
    if isinstance(request, ManagedArtifactCreateRequest):
        return _RequestDetails(
            action=ManagedArtifactAction.CREATE,
            baseline_commit=request.baseline_commit,
            transitions=(request.destination_transition,),
            documents=request.proposed_document_mutations,
        )
    if isinstance(request, ManagedArtifactReviseRequest):
        return _RequestDetails(
            action=ManagedArtifactAction.REVISE,
            baseline_commit=request.baseline_commit,
            transitions=(request.selected_transition,),
            documents=request.proposed_document_mutations,
        )
    if isinstance(request, ManagedArtifactReplaceRequest):
        return _RequestDetails(
            action=ManagedArtifactAction.REPLACE,
            baseline_commit=request.baseline_commit,
            transitions=(request.current_transition, request.replacement_transition),
            documents=request.proposed_document_mutations,
        )
    return _RequestDetails(
        action=ManagedArtifactAction.ARCHIVE,
        baseline_commit=request.baseline_commit,
        transitions=(request.active_transition, request.archive_transition),
        documents=request.proposed_document_mutations,
    )


def _terminal_state(
    transition: _TransitionCheck, candidate: bool
) -> ManagedArtifactNodeState:
    records = transition.candidate_records if candidate else transition.current_records
    return _state_or_absent(records, transition.transition.current.expected_leaf_ref)


def _is_present(state: ManagedArtifactNodeState) -> bool:
    return isinstance(state, ManagedArtifactPresentNodeState)


def _is_absent(state: ManagedArtifactNodeState) -> bool:
    return isinstance(state, ManagedArtifactAbsentNodeState)


def _valid_action_shape(
    action: ManagedArtifactAction, transitions: tuple[_TransitionCheck, ...]
) -> ManagedArtifactPlanningDecision | None:
    first = transitions[0]
    first_current = _terminal_state(first, candidate=False)
    first_candidate = _terminal_state(first, candidate=True)
    if action is ManagedArtifactAction.CREATE:
        if not (_is_absent(first_current) and _is_present(first_candidate)):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if not isinstance(first_candidate, ManagedArtifactPresentNodeState):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if first_candidate.lifecycle is not ArtifactTreeLifecycle.ACTIVE:
            return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
    elif action is ManagedArtifactAction.REVISE:
        if not (_is_present(first_current) and _is_present(first_candidate)):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if not isinstance(first_current, ManagedArtifactPresentNodeState) or not isinstance(
            first_candidate, ManagedArtifactPresentNodeState
        ):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if (
            first_current.lifecycle is not ArtifactTreeLifecycle.ACTIVE
            or first_candidate.lifecycle is not ArtifactTreeLifecycle.ACTIVE
        ):
            return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
        if first_current == first_candidate:
            return ManagedArtifactPlanningDecision.UNRELATED_MUTATION
    else:
        second = transitions[1]
        second_current = _terminal_state(second, candidate=False)
        second_candidate = _terminal_state(second, candidate=True)
        if not (_is_present(first_current) and _is_absent(first_candidate)):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if not (_is_absent(second_current) and _is_present(second_candidate)):
            return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
        if action is ManagedArtifactAction.REPLACE:
            if not isinstance(first_current, ManagedArtifactPresentNodeState):
                return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
            if first_current.lifecycle is not ArtifactTreeLifecycle.ACTIVE:
                return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
            if not isinstance(second_candidate, ManagedArtifactPresentNodeState):
                return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
            if second_candidate.lifecycle is not ArtifactTreeLifecycle.ACTIVE:
                return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
        if (
            first.transition.current.expected_leaf_ref
            == second.transition.current.expected_leaf_ref
        ):
            return ManagedArtifactPlanningDecision.PATH_INVALID
        if action is ManagedArtifactAction.ARCHIVE:
            archive_candidate = second_candidate
            if second.transition.candidate.family.value != "archive_library":
                return ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID
            if not isinstance(archive_candidate, ManagedArtifactPresentNodeState):
                return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
            if archive_candidate.lifecycle is not ArtifactTreeLifecycle.ARCHIVED:
                return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
            if not isinstance(first_current, ManagedArtifactPresentNodeState):
                return ManagedArtifactPlanningDecision.TERMINAL_STATE_MISMATCH
            if first_current.lifecycle is not ArtifactTreeLifecycle.ACTIVE:
                return ManagedArtifactPlanningDecision.LIFECYCLE_INVALID
    return None


def _all_refs(
    current: tuple[_NodeStateRecord, ...], candidate: tuple[_NodeStateRecord, ...]
) -> tuple[OpaqueMetadataId, ...]:
    return tuple(sorted({record.artifact_ref for record in current + candidate}))


def _changed_refs(
    current: tuple[_NodeStateRecord, ...], candidate: tuple[_NodeStateRecord, ...]
) -> tuple[OpaqueMetadataId, ...]:
    return tuple(
        artifact_ref
        for artifact_ref in _all_refs(current, candidate)
        if _state_or_absent(current, artifact_ref) != _state_or_absent(candidate, artifact_ref)
    )


def _present_updates_are_complete(
    current: tuple[_NodeStateRecord, ...], candidate: tuple[_NodeStateRecord, ...]
) -> bool:
    """Require revision and content identity to move together for present updates."""

    for artifact_ref in _all_refs(current, candidate):
        before = _state_or_absent(current, artifact_ref)
        after = _state_or_absent(candidate, artifact_ref)
        if not (
            isinstance(before, ManagedArtifactPresentNodeState)
            and isinstance(after, ManagedArtifactPresentNodeState)
        ):
            continue
        revision_changed = before.revision != after.revision
        digest_changed = before.content_digest != after.content_digest
        if before != after and not (revision_changed and digest_changed):
            return False
    return True


def _cascade_is_complete(
    transitions: tuple[_TransitionCheck, ...],
    current: tuple[_NodeStateRecord, ...],
    candidate: tuple[_NodeStateRecord, ...],
) -> bool:
    for transition in transitions:
        leaf_ref = transition.transition.candidate.expected_leaf_ref
        if _state_or_absent(current, leaf_ref) == _state_or_absent(candidate, leaf_ref):
            continue
        for ancestor_ref in transition.transition.candidate.explicit_path_refs[:-1]:
            if _state_or_absent(current, ancestor_ref) == _state_or_absent(
                candidate, ancestor_ref
            ):
                return False
    return True


def _build_node_mutations(
    current: tuple[_NodeStateRecord, ...], candidate: tuple[_NodeStateRecord, ...]
) -> tuple[ManagedArtifactNodeMutation, ...]:
    return tuple(
        ManagedArtifactNodeMutation(
            artifact_ref=artifact_ref,
            expected_state=_state_or_absent(current, artifact_ref),
            next_state=_state_or_absent(candidate, artifact_ref),
        )
        for artifact_ref in _changed_refs(current, candidate)
    )


def _document_matches(
    document: ManagedArtifactDocumentMutation,
    current: tuple[_NodeStateRecord, ...],
    candidate: tuple[_NodeStateRecord, ...],
    changed_refs: tuple[OpaqueMetadataId, ...],
) -> bool:
    if document.artifact_ref not in changed_refs:
        return False
    current_state = _state_or_absent(current, document.artifact_ref)
    next_state = _state_or_absent(candidate, document.artifact_ref)
    if isinstance(document, ManagedArtifactDocumentCreate):
        return (
            _is_absent(current_state)
            and isinstance(next_state, ManagedArtifactPresentNodeState)
            and document.content_digest == next_state.content_digest
        )
    if isinstance(document, ManagedArtifactDocumentUpdate):
        return (
            isinstance(current_state, ManagedArtifactPresentNodeState)
            and isinstance(next_state, ManagedArtifactPresentNodeState)
            and document.expected_current_digest == current_state.content_digest
            and document.content_digest == next_state.content_digest
        )
    return (
        isinstance(current_state, ManagedArtifactPresentNodeState)
        and _is_absent(next_state)
        and document.expected_current_digest == current_state.content_digest
    )


def _validate_documents(
    documents: tuple[ManagedArtifactDocumentMutation, ...],
    current: tuple[_NodeStateRecord, ...],
    candidate: tuple[_NodeStateRecord, ...],
    changed_refs: tuple[OpaqueMetadataId, ...],
) -> ManagedArtifactPlanningDecision | None:
    refs = tuple(document.artifact_ref for document in documents)
    paths = tuple(document.path for document in documents)
    if len(refs) != len(set(refs)) or len(paths) != len(set(paths)):
        return ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH
    candidate_digests = tuple(
        document.content_digest
        for document in documents
        if isinstance(document, (ManagedArtifactDocumentCreate, ManagedArtifactDocumentUpdate))
    )
    if len(candidate_digests) != len(set(candidate_digests)):
        return ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH
    if any(document.artifact_ref not in changed_refs for document in documents):
        return ManagedArtifactPlanningDecision.UNRELATED_MUTATION
    if len(documents) != len(changed_refs):
        return ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH
    if any(
        not _document_matches(document, current, candidate, changed_refs)
        for document in documents
    ):
        return ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH
    return None


def _plan_for_action(
    details: _RequestDetails,
    transitions: tuple[_TransitionCheck, ...],
    node_mutations: tuple[ManagedArtifactNodeMutation, ...],
    document_mutations: tuple[ManagedArtifactDocumentMutation, ...],
) -> ManagedArtifactPlan:
    post_states = tuple(transition.transition.candidate for transition in transitions)
    ordered_documents = tuple(
        sorted(document_mutations, key=lambda document: document.path)
    )
    if details.action is ManagedArtifactAction.CREATE:
        return ManagedArtifactCreatePlan(
            action="CREATE",
            destination_transition=transitions[0].transition,
            baseline_commit=details.baseline_commit,
            node_mutations=node_mutations,
            document_mutations=ordered_documents,
            post_state_snapshots=post_states,
        )
    if details.action is ManagedArtifactAction.REVISE:
        return ManagedArtifactRevisePlan(
            action="REVISE",
            selected_transition=transitions[0].transition,
            baseline_commit=details.baseline_commit,
            node_mutations=node_mutations,
            document_mutations=ordered_documents,
            post_state_snapshots=post_states,
        )
    if details.action is ManagedArtifactAction.REPLACE:
        return ManagedArtifactReplacePlan(
            action="REPLACE",
            current_transition=transitions[0].transition,
            replacement_transition=transitions[1].transition,
            baseline_commit=details.baseline_commit,
            node_mutations=node_mutations,
            document_mutations=ordered_documents,
            post_state_snapshots=post_states,
        )
    return ManagedArtifactArchivePlan(
        action="ARCHIVE",
        active_transition=transitions[0].transition,
        archive_transition=transitions[1].transition,
        baseline_commit=details.baseline_commit,
        node_mutations=node_mutations,
        document_mutations=ordered_documents,
        post_state_snapshots=post_states,
    )


def _reject(
    request: ManagedArtifactRequest, decision: ManagedArtifactPlanningDecision
) -> ManagedArtifactPlanningResult:
    return ManagedArtifactRejectedResult(
        request_ref=request.request_ref,
        decision=decision,
    )


def plan_managed_artifact(request: ManagedArtifactRequest) -> ManagedArtifactPlanningResult:
    """Return one deterministic in-memory plan or one finite rejection."""

    try:
        validated_request = _REQUEST_ADAPTER.validate_python(request)
    except ValidationError:
        return _reject(request, ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    details = _details(validated_request)
    checks: tuple[_TransitionCheck, ...] = ()
    for transition in details.transitions:
        checked = _transition_check(transition)
        if checked.check is None:
            failure = checked.failure or ManagedArtifactPlanningDecision.PATH_INVALID
            return _reject(request, failure)
        checks += (checked.check,)
    action_failure = _valid_action_shape(details.action, checks)
    if action_failure is not None:
        return _reject(request, action_failure)
    if any(not _unselected_edges_are_preserved(check) for check in checks):
        return _reject(request, ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    if not _node_metadata_is_consistent(checks, candidate=False):
        return _reject(request, ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)
    if not _node_metadata_is_consistent(checks, candidate=True):
        return _reject(request, ManagedArtifactPlanningDecision.ARTIFACT_TREE_INVALID)

    current_merge = _merge(tuple(check.current_records for check in checks))
    if current_merge.failure is not None:
        return _reject(request, current_merge.failure)
    candidate_merge = _merge(tuple(check.candidate_records for check in checks))
    if candidate_merge.failure is not None:
        return _reject(request, candidate_merge.failure)
    current = current_merge.records
    candidate = candidate_merge.records
    if not _present_updates_are_complete(current, candidate):
        return _reject(request, ManagedArtifactPlanningDecision.DOCUMENT_MUTATION_MISMATCH)
    changed_refs = _changed_refs(current, candidate)
    if not changed_refs:
        return _reject(request, ManagedArtifactPlanningDecision.UNRELATED_MUTATION)
    if not _cascade_is_complete(checks, current, candidate):
        return _reject(request, ManagedArtifactPlanningDecision.ANCESTOR_CASCADE_INCOMPLETE)
    document_failure = _validate_documents(details.documents, current, candidate, changed_refs)
    if document_failure is not None:
        return _reject(request, document_failure)
    return ManagedArtifactPlannedResult(
        request_ref=request.request_ref,
        plan=_plan_for_action(
            details,
            checks,
            _build_node_mutations(current, candidate),
            details.documents,
        ),
    )
