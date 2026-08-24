"""PAI-04-T01 through T07 tests for high-collaboration evidence admission."""

from __future__ import annotations

import ast
import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from library.local_orchestration.project_authority.collaboration import (
    HighCollaborationAdmissionDecision,
    HighCollaborationAdmissionRequest,
    HighCollaborationAdmissionResult,
    ProviderEnforcementCapability,
    ProviderEnforcementEvidence,
    ProviderPolicyReadDisposition,
    ProviderPolicyReadPort,
    ProviderPolicyReadRequest,
    ProviderPolicyReadResult,
    PullRequestEvidence,
    PullRequestReadDisposition,
    PullRequestReadPort,
    PullRequestReadRequest,
    PullRequestReadResult,
    PullRequestState,
    admit_high_collaboration_evidence,
)
from library.local_orchestration.project_authority.contracts import (
    AuthorityLineRole,
    FullBranchRef,
    ProjectAuthorityContract,
    ProjectTopology,
    RemoteProviderKind,
    RemoteRepositoryId,
)


_CANDIDATE_SHA = "0123456789abcdef0123456789abcdef01234567"
_BASE_SHA = "fedcba9876543210fedcba9876543210fedcba98"
_OTHER_SHA = "abcdef0123456789abcdef0123456789abcdef01"
_UTC = datetime.timezone.utc
_VALID_FROM = datetime.datetime(2026, 8, 25, 9, 0, tzinfo=_UTC)
_OBSERVED_AT = datetime.datetime(2026, 8, 25, 10, 0, tzinfo=_UTC)
_DECISION_AT = datetime.datetime(2026, 8, 25, 11, 0, tzinfo=_UTC)


def _repository(repository_key: str = "org/project-authority") -> RemoteRepositoryId:
    return RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GITHUB,
        host="github.com",
        repository_key=repository_key,
        alias="origin",
    )


def _contract(
    topology: ProjectTopology = ProjectTopology.HIGH_COLLABORATION,
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
) -> ProjectAuthorityContract:
    return ProjectAuthorityContract(
        project_id="project-authority",
        topology=topology,
        authority_line_role=AuthorityLineRole.DEVELOPMENT,
        project_authority_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        remote_repository=repository or _repository(),
        declaration_artifact_ref="doc/adr/ADR-20260824-020",
        declaration_revision_sha=_BASE_SHA,
        gate_id="gate-project-authority",
        gate_revision=_BASE_SHA,
        effective_at=_VALID_FROM,
    )


def _request(
    topology: ProjectTopology = ProjectTopology.HIGH_COLLABORATION,
    ticket_id: str = "PAI-04-HIGH-COLLABORATION-EVIDENCE",
    candidate_sha: str = _CANDIDATE_SHA,
    pull_request_read_id: str = "pull-read-01",
    policy_read_id: str = "policy-read-01",
    valid_from: datetime.datetime = _VALID_FROM,
    decision_at: datetime.datetime = _DECISION_AT,
) -> HighCollaborationAdmissionRequest:
    return HighCollaborationAdmissionRequest(
        authority_contract=_contract(topology=topology),
        ticket_id=ticket_id,
        candidate_sha=candidate_sha,
        pull_request_read_id=pull_request_read_id,
        policy_read_id=policy_read_id,
        valid_from=valid_from,
        decision_at=decision_at,
    )


def _observed_pull(
    repository: RemoteRepositoryId | None = None,
    ticket_id: str = "PAI-04-HIGH-COLLABORATION-EVIDENCE",
    state: PullRequestState = PullRequestState.OPEN,
    head_ref: FullBranchRef | None = None,
    head_sha: str = _CANDIDATE_SHA,
    base_ref: FullBranchRef | None = None,
    approval_head_sha: str | None = _CANDIDATE_SHA,
    observer: str = "fake-pr-observer",
    method: str = "fake-pr-read",
    observed_at: datetime.datetime = _OBSERVED_AT,
    digest: str = "digest-pr-01",
) -> PullRequestReadResult:
    return PullRequestReadResult(
        disposition=PullRequestReadDisposition.OBSERVED,
        repository=repository or _repository(),
        ticket_id=ticket_id,
        pull_request_id="pull-01",
        state=state,
        head_ref=head_ref or FullBranchRef(value="refs/heads/feature"),
        head_sha=head_sha,
        base_ref=base_ref or FullBranchRef(value="refs/heads/main"),
        approval_head_sha=approval_head_sha,
        observer=observer,
        method=method,
        exit_status=0,
        observed_at=observed_at,
        normalized_evidence_digest=digest,
    )


def _unobserved_pull(disposition: PullRequestReadDisposition) -> PullRequestReadResult:
    return PullRequestReadResult(disposition=disposition)


def _observed_policy(
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
    gate_id: str = "gate-project-authority",
    gate_revision: str = _BASE_SHA,
    capability: ProviderEnforcementCapability = ProviderEnforcementCapability.PROVEN,
    ui_bypass_prevented: bool = True,
    stale_approval_invalidated: bool = True,
    policy_ids: tuple[str, ...] = ("policy-ui-bypass",),
    observer: str = "fake-policy-observer",
    method: str = "fake-policy-read",
    observed_at: datetime.datetime = _OBSERVED_AT,
    digest: str = "digest-policy-01",
) -> ProviderPolicyReadResult:
    return ProviderPolicyReadResult(
        disposition=ProviderPolicyReadDisposition.OBSERVED,
        repository=repository or _repository(),
        full_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        gate_id=gate_id,
        gate_revision=gate_revision,
        capability=capability,
        ui_bypass_prevented=ui_bypass_prevented,
        stale_approval_invalidated=stale_approval_invalidated,
        policy_ids=policy_ids,
        observer=observer,
        method=method,
        exit_status=0,
        observed_at=observed_at,
        normalized_evidence_digest=digest,
    )


def _unobserved_policy(disposition: ProviderPolicyReadDisposition) -> ProviderPolicyReadResult:
    return ProviderPolicyReadResult(disposition=disposition)


class _FakePullRequestPort:
    def __init__(self, result: PullRequestReadResult, events: list[str] | None = None) -> None:
        self.result = result
        self.calls = 0
        self.requests: list[PullRequestReadRequest] = []
        self.events = events if events is not None else []

    def read(self, request: PullRequestReadRequest, /) -> PullRequestReadResult:
        self.calls += 1
        self.requests.append(request)
        self.events.append("pull")
        return self.result


class _FakePolicyPort:
    def __init__(self, result: ProviderPolicyReadResult, events: list[str] | None = None) -> None:
        self.result = result
        self.calls = 0
        self.requests: list[ProviderPolicyReadRequest] = []
        self.events = events if events is not None else []

    def read(self, request: ProviderPolicyReadRequest, /) -> ProviderPolicyReadResult:
        self.calls += 1
        self.requests.append(request)
        self.events.append("policy")
        return self.result


class _UnexpectedPullRequestPort:
    def read(self, request: PullRequestReadRequest, /) -> PullRequestReadResult:
        raise RuntimeError("fake-pr-port-defect")


def _run(
    request: HighCollaborationAdmissionRequest,
    pull_result: PullRequestReadResult,
    policy_result: ProviderPolicyReadResult,
) -> tuple[HighCollaborationAdmissionResult, _FakePullRequestPort, _FakePolicyPort]:
    events: list[str] = []
    pull_port = _FakePullRequestPort(pull_result, events)
    policy_port = _FakePolicyPort(policy_result, events)
    result = admit_high_collaboration_evidence(request, pull_port, policy_port)
    return result, pull_port, policy_port


def test_admit_high_collaboration_evidence_accepts_one_matching_pair() -> None:
    request = _request()
    pull_result = _observed_pull()
    policy_result = _observed_policy()

    result, pull_port, policy_port = _run(request, pull_result, policy_result)

    assert result.decision is HighCollaborationAdmissionDecision.ACCEPTED
    assert result.failure is None
    assert result.pull_request_evidence == PullRequestEvidence(
        repository=_repository(),
        ticket_id=request.ticket_id,
        pull_request_id="pull-01",
        state=PullRequestState.OPEN,
        head_ref=FullBranchRef(value="refs/heads/feature"),
        head_sha=_CANDIDATE_SHA,
        base_ref=FullBranchRef(value="refs/heads/main"),
        approval_head_sha=_CANDIDATE_SHA,
        observer="fake-pr-observer",
        method="fake-pr-read",
        exit_status=0,
        observed_at=_OBSERVED_AT,
        normalized_evidence_digest="digest-pr-01",
    )
    assert result.provider_enforcement_evidence == ProviderEnforcementEvidence(
        repository=_repository(),
        full_ref=FullBranchRef(value="refs/heads/main"),
        gate_id="gate-project-authority",
        gate_revision=_BASE_SHA,
        capability=ProviderEnforcementCapability.PROVEN,
        ui_bypass_prevented=True,
        stale_approval_invalidated=True,
        policy_ids=("policy-ui-bypass",),
        observer="fake-policy-observer",
        method="fake-policy-read",
        exit_status=0,
        observed_at=_OBSERVED_AT,
        normalized_evidence_digest="digest-policy-01",
    )
    assert pull_port.calls == 1
    assert policy_port.calls == 1
    assert pull_port.requests[0].read_id == request.pull_request_read_id
    assert policy_port.requests[0].read_id == request.policy_read_id


def test_high_collaboration_public_models_are_strict_and_closed() -> None:
    for disposition in PullRequestReadDisposition:
        pull_result = _observed_pull() if disposition is PullRequestReadDisposition.OBSERVED else _unobserved_pull(disposition)
        assert pull_result.disposition is disposition
    for state in PullRequestState:
        assert _observed_pull(state=state).state is state
    for policy_disposition in ProviderPolicyReadDisposition:
        policy_result = _observed_policy() if policy_disposition is ProviderPolicyReadDisposition.OBSERVED else _unobserved_policy(policy_disposition)
        assert policy_result.disposition is policy_disposition
    for capability in ProviderEnforcementCapability:
        assert _observed_policy(capability=capability).capability is capability
    for decision in HighCollaborationAdmissionDecision:
        if decision is HighCollaborationAdmissionDecision.ACCEPTED:
            decision_result = HighCollaborationAdmissionResult(
                decision=decision,
                pull_request_evidence=PullRequestEvidence(
                    repository=_repository(),
                    ticket_id=_request().ticket_id,
                    pull_request_id="pull-01",
                    state=PullRequestState.OPEN,
                    head_ref=FullBranchRef(value="refs/heads/feature"),
                    head_sha=_CANDIDATE_SHA,
                    base_ref=FullBranchRef(value="refs/heads/main"),
                    approval_head_sha=_CANDIDATE_SHA,
                    observer="observer",
                    method="method",
                    exit_status=0,
                    observed_at=_OBSERVED_AT,
                    normalized_evidence_digest="digest",
                ),
                provider_enforcement_evidence=ProviderEnforcementEvidence(
                    repository=_repository(),
                    full_ref=FullBranchRef(value="refs/heads/main"),
                    gate_id="gate-project-authority",
                    gate_revision=_BASE_SHA,
                    capability=ProviderEnforcementCapability.PROVEN,
                    ui_bypass_prevented=True,
                    stale_approval_invalidated=True,
                    policy_ids=("policy",),
                    observer="observer",
                    method="method",
                    exit_status=0,
                    observed_at=_OBSERVED_AT,
                    normalized_evidence_digest="digest",
                ),
            )
        elif decision is HighCollaborationAdmissionDecision.NOT_APPLICABLE:
            decision_result = HighCollaborationAdmissionResult(decision=decision)
        else:
            decision_result = HighCollaborationAdmissionResult(decision=decision, failure=decision)
        assert decision_result.decision is decision

    request = _request()
    pull_port: PullRequestReadPort = _FakePullRequestPort(_observed_pull())
    policy_port: ProviderPolicyReadPort = _FakePolicyPort(_observed_policy())
    assert admit_high_collaboration_evidence(request, pull_port, policy_port).decision is HighCollaborationAdmissionDecision.ACCEPTED

    with pytest.raises(ValidationError):
        HighCollaborationAdmissionRequest.model_validate(
            {
                "authority_contract": _contract(),
                "ticket_id": None,
                "candidate_sha": _CANDIDATE_SHA,
                "pull_request_read_id": "pull",
                "policy_read_id": "policy",
                "valid_from": _VALID_FROM,
                "decision_at": _DECISION_AT,
            }
        )
    with pytest.raises(ValidationError):
        HighCollaborationAdmissionRequest.model_validate(
            {
                "authority_contract": _contract(),
                "ticket_id": "ticket",
                "candidate_sha": _CANDIDATE_SHA,
                "pull_request_read_id": "pull",
                "policy_read_id": "policy",
                "valid_from": _VALID_FROM,
                "decision_at": _DECISION_AT,
                "extra": "forbidden",
            }
        )
    with pytest.raises(ValidationError):
        _request(pull_request_read_id="same", policy_read_id="same")
    with pytest.raises(ValidationError):
        _request(candidate_sha="not-a-sha")
    with pytest.raises(ValidationError):
        _request(valid_from=datetime.datetime(2026, 8, 25, 9, 0), decision_at=_DECISION_AT)
    with pytest.raises(ValidationError):
        HighCollaborationAdmissionRequest.model_validate(
            {
                "authority_contract": _contract(),
                "ticket_id": "ticket",
                "candidate_sha": _CANDIDATE_SHA,
                "pull_request_read_id": "pull",
                "policy_read_id": "policy",
                "valid_from": _VALID_FROM.isoformat(),
                "decision_at": _DECISION_AT,
            }
        )
    with pytest.raises(ValidationError):
        PullRequestReadResult.model_validate({"disposition": "UNDECLARED"})
    with pytest.raises(ValidationError):
        ProviderPolicyReadResult.model_validate({"disposition": "UNDECLARED"})
    with pytest.raises(ValidationError):
        PullRequestReadResult(
            disposition=PullRequestReadDisposition.NOT_FOUND,
            ticket_id="ticket",
        )
    with pytest.raises(ValidationError):
        _observed_policy(policy_ids=("duplicate", "duplicate"))
    with pytest.raises(ValidationError):
        _observed_policy(gate_revision="not-a-sha")
    with pytest.raises(ValidationError):
        PullRequestReadRequest(
            authority_contract=_contract(),
            ticket_id="token=request-secret",
            read_id="pull",
            candidate_sha=_CANDIDATE_SHA,
            valid_from=_VALID_FROM,
            decision_at=_DECISION_AT,
        )
    with pytest.raises(ValidationError):
        ProviderPolicyReadRequest(
            authority_contract=_contract(),
            ticket_id="ticket",
            read_id="password=policy-secret",
            candidate_sha=_CANDIDATE_SHA,
            valid_from=_VALID_FROM,
            decision_at=_DECISION_AT,
        )
    with pytest.raises(ValidationError):
        HighCollaborationAdmissionRequest(
            authority_contract=_contract(
                repository=_repository("https://user:token@example.test/org/project")
            ),
            ticket_id="ticket",
            candidate_sha=_CANDIDATE_SHA,
            pull_request_read_id="pull",
            policy_read_id="policy",
            valid_from=_VALID_FROM,
            decision_at=_DECISION_AT,
        )
    with pytest.raises(ValidationError):
        PullRequestEvidence(
            repository=_repository("https://user:token@example.test/org/project"),
            ticket_id="ticket",
            pull_request_id="pull-01",
            state=PullRequestState.OPEN,
            head_ref=FullBranchRef(value="refs/heads/feature"),
            head_sha=_CANDIDATE_SHA,
            base_ref=FullBranchRef(value="refs/heads/main"),
            approval_head_sha=_CANDIDATE_SHA,
            observer="observer",
            method="method",
            exit_status=0,
            observed_at=_OBSERVED_AT,
            normalized_evidence_digest="digest",
        )
    with pytest.raises(ValidationError):
        ProviderEnforcementEvidence(
            repository=_repository("https://user:token@example.test/org/project"),
            full_ref=FullBranchRef(value="refs/heads/main"),
            gate_id="gate-project-authority",
            gate_revision=_BASE_SHA,
            capability=ProviderEnforcementCapability.PROVEN,
            ui_bypass_prevented=True,
            stale_approval_invalidated=True,
            policy_ids=("policy",),
            observer="observer",
            method="method",
            exit_status=0,
            observed_at=_OBSERVED_AT,
            normalized_evidence_digest="digest",
        )
    assert _observed_pull(observer="token=raw-port-secret").observer == "token=raw-port-secret"
    assert _observed_policy(method="password=raw-port-secret").method == "password=raw-port-secret"
    with pytest.raises(ValidationError):
        ProviderPolicyReadResult.model_validate(
            {
                "disposition": ProviderPolicyReadDisposition.OBSERVED,
                "repository": _repository(),
                "full_ref": FullBranchRef(value="refs/heads/main"),
                "gate_id": "gate",
                "gate_revision": _BASE_SHA,
                "capability": ProviderEnforcementCapability.PROVEN,
                "ui_bypass_prevented": True,
                "stale_approval_invalidated": True,
                "policy_ids": ["list-not-tuple"],
                "observer": "observer",
                "method": "method",
                "exit_status": 0,
                "observed_at": _OBSERVED_AT,
                "normalized_evidence_digest": "digest",
            }
        )
    with pytest.raises(ValidationError):
        HighCollaborationAdmissionResult(
            decision=HighCollaborationAdmissionDecision.ACCEPTED,
            failure=HighCollaborationAdmissionDecision.ACCEPTED,
        )


def test_profile_scaling_skips_ports_for_single_branch_and_orders_high_reads() -> None:
    events: list[str] = []
    pull_port = _FakePullRequestPort(_observed_pull(), events)
    policy_port = _FakePolicyPort(_observed_policy(), events)
    single_result = admit_high_collaboration_evidence(
        _request(topology=ProjectTopology.SINGLE_BRANCH), pull_port, policy_port
    )
    assert single_result.decision is HighCollaborationAdmissionDecision.NOT_APPLICABLE
    assert single_result.failure is None
    assert single_result.pull_request_evidence is None
    assert single_result.provider_enforcement_evidence is None
    assert pull_port.calls == 0
    assert policy_port.calls == 0

    high_result = admit_high_collaboration_evidence(_request(), pull_port, policy_port)
    assert high_result.decision is HighCollaborationAdmissionDecision.ACCEPTED
    assert events == ["pull", "policy"]


def test_pr_visibility_precedence_is_fail_closed_and_exceptions_remain_exceptions() -> None:
    cases = (
        (_unobserved_pull(PullRequestReadDisposition.NOT_FOUND), HighCollaborationAdmissionDecision.PR_REQUIRED),
        (_unobserved_pull(PullRequestReadDisposition.UNAVAILABLE), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_unobserved_pull(PullRequestReadDisposition.AMBIGUOUS), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_observed_pull(ticket_id="other-ticket"), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_observed_pull(state=PullRequestState.DRAFT), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_observed_pull(observed_at=_VALID_FROM - datetime.timedelta(minutes=1)), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_observed_pull(observed_at=_DECISION_AT + datetime.timedelta(minutes=1)), HighCollaborationAdmissionDecision.PR_NOT_REVIEWABLE),
        (_observed_pull(head_sha=_OTHER_SHA), HighCollaborationAdmissionDecision.PR_HEAD_SHA_MISMATCH),
        (_observed_pull(base_ref=FullBranchRef(value="refs/heads/release")), HighCollaborationAdmissionDecision.PR_BASE_REF_MISMATCH),
        (_observed_pull(approval_head_sha=_OTHER_SHA), HighCollaborationAdmissionDecision.PR_APPROVAL_STALE),
    )
    for pull_result, expected in cases:
        result, pull_port, policy_port = _run(_request(), pull_result, _observed_policy())
        assert result.decision is expected
        assert result.failure is expected
        assert result.pull_request_evidence is None
        assert result.provider_enforcement_evidence is None
        assert pull_port.calls == 1
        assert policy_port.calls == 0

    with pytest.raises(RuntimeError, match="fake-pr-port-defect"):
        admit_high_collaboration_evidence(
            _request(), _UnexpectedPullRequestPort(), _FakePolicyPort(_observed_policy())
        )


def test_provider_enforcement_precedence_requires_two_proofs() -> None:
    mismatches = (
        _observed_policy(repository=_repository("other/project")),
        _observed_policy(full_ref=FullBranchRef(value="refs/heads/release")),
        _observed_policy(gate_id="other-gate"),
        _observed_policy(gate_revision=_OTHER_SHA),
    )
    for policy_result in mismatches:
        result, pull_port, policy_port = _run(_request(), _observed_pull(), policy_result)
        assert result.decision is HighCollaborationAdmissionDecision.REMOTE_IDENTITY_MISMATCH
        assert pull_port.calls == 1
        assert policy_port.calls == 1

    for disposition in (
        ProviderPolicyReadDisposition.UNAVAILABLE,
        ProviderPolicyReadDisposition.AMBIGUOUS,
    ):
        result, _, _ = _run(_request(), _observed_pull(), _unobserved_policy(disposition))
        assert result.decision is HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN

    unproven_cases = (
        _observed_policy(capability=ProviderEnforcementCapability.UNPROVEN),
        _observed_policy(capability=ProviderEnforcementCapability.NOT_APPLICABLE),
        _observed_policy(ui_bypass_prevented=False),
        _observed_policy(stale_approval_invalidated=False),
        _observed_policy(policy_ids=()),
        _observed_policy(observed_at=_VALID_FROM - datetime.timedelta(minutes=1)),
        _observed_policy(observed_at=_DECISION_AT + datetime.timedelta(minutes=1)),
    )
    for policy_result in unproven_cases:
        result, _, _ = _run(_request(), _observed_pull(), policy_result)
        assert result.decision is HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNPROVEN

    unsupported, _, _ = _run(
        _request(),
        _observed_pull(),
        _observed_policy(capability=ProviderEnforcementCapability.UNSUPPORTED),
    )
    assert unsupported.decision is HighCollaborationAdmissionDecision.PROVIDER_ENFORCEMENT_UNSUPPORTED

    failed_pr, _, policy_port = _run(
        _request(),
        _observed_pull(head_sha=_OTHER_SHA),
        _observed_policy(),
    )
    assert failed_pr.decision is HighCollaborationAdmissionDecision.PR_HEAD_SHA_MISMATCH
    assert policy_port.calls == 0


def test_credential_metadata_is_rejected_without_copying_or_later_reads() -> None:
    credential_pr, pull_port, policy_port = _run(
        _request(),
        _observed_pull(observer="token=pr-secret"),
        _observed_policy(),
    )
    assert credential_pr.decision is HighCollaborationAdmissionDecision.SECRET_MATERIAL_DETECTED
    assert credential_pr.pull_request_evidence is None
    assert credential_pr.provider_enforcement_evidence is None
    assert "pr-secret" not in credential_pr.model_dump_json()
    assert pull_port.calls == 1
    assert policy_port.calls == 0

    credential_policy, pull_port, policy_port = _run(
        _request(),
        _observed_pull(),
        _observed_policy(method="password=policy-secret"),
    )
    assert credential_policy.decision is HighCollaborationAdmissionDecision.SECRET_MATERIAL_DETECTED
    assert credential_policy.pull_request_evidence is None
    assert credential_policy.provider_enforcement_evidence is None
    assert "policy-secret" not in credential_policy.model_dump_json()
    assert pull_port.calls == 1
    assert policy_port.calls == 1


def test_high_collaboration_ast_gate_targets_owned_production_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    collaboration_path = root / "library/local_orchestration/project_authority/collaboration.py"
    init_path = root / "library/local_orchestration/project_authority/__init__.py"
    collaboration_tree = ast.parse(collaboration_path.read_text(encoding="utf-8"))
    init_tree = ast.parse(init_path.read_text(encoding="utf-8"))
    collaboration_all = (
        "PullRequestReadDisposition",
        "PullRequestState",
        "PullRequestReadRequest",
        "PullRequestReadResult",
        "PullRequestEvidence",
        "PullRequestReadPort",
        "ProviderPolicyReadDisposition",
        "ProviderEnforcementCapability",
        "ProviderPolicyReadRequest",
        "ProviderPolicyReadResult",
        "ProviderEnforcementEvidence",
        "ProviderPolicyReadPort",
        "HighCollaborationAdmissionDecision",
        "HighCollaborationAdmissionRequest",
        "HighCollaborationAdmissionResult",
        "admit_high_collaboration_evidence",
    )
    frozen_init_all = (
        "AuthorityContractAdmission",
        "AuthorityContractAdmissionDecision",
        "AuthorityContractInput",
        "AuthorityIntegrationState",
        "AuthorityLineRole",
        "AuthorityObservationAdmission",
        "AuthorityObservationDecision",
        "BridgeCapability",
        "FullBranchRef",
        "GitObservation",
        "GitObservationSource",
        "PrePushLifecycleRequest",
        "PrePushLifecycleTransition",
        "ProjectAuthorityContract",
        "ProjectTopology",
        "RemoteProviderKind",
        "RemoteRepositoryId",
        "admit_authority_contract",
        "admit_authority_observation",
        "advance_pre_push_lifecycle",
    )
    observation_all = (
        "DirectRemoteObservationDecision",
        "DirectRemoteObservationPort",
        "DirectRemoteObservationRequest",
        "DirectRemoteObservationResult",
        "DirectRemoteReadDisposition",
        "DirectRemoteReadResult",
        "observe_declared_remote",
    )
    finalization_all = (
        "NonForcePushDisposition",
        "NonForcePushRequest",
        "NonForcePushResult",
        "NonForcePushPort",
        "AuthorityFinalizationFailure",
        "AuthorityFinalizationRequest",
        "AuthorityFinalizationResult",
        "finalize_authority_integration",
    )
    allowed_modules = {
        "__future__",
        "datetime",
        "enum",
        "re",
        "typing",
        "pydantic",
        "library.local_orchestration.project_authority.contracts",
        "contracts",
        "integration",
        "observation",
        "collaboration",
    }
    forbidden_names = {
        "Any",
        "cast",
        "getattr",
        "setattr",
        "__import__",
        "eval",
        "exec",
        "model_construct",
        "model_copy",
        "open",
        "os",
        "pathlib",
        "subprocess",
        "socket",
        "urllib",
        "http",
        "requests",
        "git",
        "shutil",
        "time",
        "Provider",
        "REMOTE_TRACKING_CACHE",
        "force",
        "retry",
        "poll",
        "fetch",
    }

    def literal_all(tree: ast.Module) -> tuple[str, ...]:
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            ):
                if not isinstance(node.value, (ast.Tuple, ast.List)):
                    raise AssertionError("__all__ must be literal")
                values: list[str] = []
                for element in node.value.elts:
                    if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                        raise AssertionError("__all__ must contain string literals")
                    values.append(element.value)
                return tuple(values)
        raise AssertionError("missing __all__")

    assert literal_all(collaboration_tree) == collaboration_all
    assert literal_all(init_tree) == frozen_init_all + observation_all + finalization_all + collaboration_all
    declarations = {
        node.name
        for node in collaboration_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }
    assert declarations == set(collaboration_all)
    public_assignments = {
        target.id
        for node in collaboration_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and not target.id.startswith("_")
    }
    public_assignments.update(
        node.target.id
        for node in collaboration_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and not node.target.id.startswith("_")
    )
    assert public_assignments == set()
    for tree in (collaboration_tree, init_tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id not in forbidden_names
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names
                if isinstance(node.value, ast.Name):
                    assert f"{node.value.id}.{node.attr}" not in {"datetime.now", "datetime.utcnow"}
            if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                raise AssertionError("collaboration boundary must not loop")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in allowed_modules
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed_modules
