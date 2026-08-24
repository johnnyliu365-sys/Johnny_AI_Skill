"""PAI-03-T01 through T07 tests for pure finalization composition."""

from __future__ import annotations

import ast
import datetime
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from library.local_orchestration.project_authority.contracts import (
    AuthorityIntegrationState,
    AuthorityLineRole,
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    PrePushLifecycleRequest,
    PrePushLifecycleTransition,
    ProjectAuthorityContract,
    ProjectTopology,
    RemoteProviderKind,
    RemoteRepositoryId,
)
from library.local_orchestration.project_authority.integration import (
    AuthorityFinalizationFailure,
    AuthorityFinalizationRequest,
    AuthorityFinalizationResult,
    NonForcePushDisposition,
    NonForcePushPort,
    NonForcePushRequest,
    NonForcePushResult,
    advance_pre_push_lifecycle,
    finalize_authority_integration,
)
from library.local_orchestration.project_authority.observation import (
    DirectRemoteObservationDecision,
    DirectRemoteObservationPort,
    DirectRemoteObservationRequest,
    DirectRemoteReadDisposition,
    DirectRemoteReadResult,
)


_BASE_SHA = "0123456789abcdef0123456789abcdef01234567"
_LOCAL_SHA = "fedcba9876543210fedcba9876543210fedcba98"
_OTHER_SHA = "abcdef0123456789abcdef0123456789abcdef01"
_UTC = datetime.timezone.utc
_REQUESTED_AT = datetime.datetime(2026, 8, 25, 10, 0, tzinfo=_UTC)
_COMPLETED_AT = datetime.datetime(2026, 8, 25, 10, 1, tzinfo=_UTC)
_DECISION_AT = datetime.datetime(2026, 8, 25, 11, 0, tzinfo=_UTC)


def _repository(repository_key: str = "org/project-authority") -> RemoteRepositoryId:
    return RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GITHUB,
        host="github.com",
        repository_key=repository_key,
        alias="origin",
    )


def _contract(repository: RemoteRepositoryId | None = None) -> ProjectAuthorityContract:
    return ProjectAuthorityContract(
        project_id="project-authority",
        topology=ProjectTopology.SINGLE_BRANCH,
        authority_line_role=AuthorityLineRole.SINGLE,
        project_authority_ref=FullBranchRef(value="refs/heads/main"),
        remote_repository=repository or _repository(),
        declaration_artifact_ref="doc/adr/ADR-20260824-020",
        declaration_revision_sha=_BASE_SHA,
        gate_id="gate-project-authority",
        gate_revision=_BASE_SHA,
        effective_at=_REQUESTED_AT,
    )


def _observation(
    sha: str = _BASE_SHA,
    source: GitObservationSource = GitObservationSource.DIRECT_REMOTE_REF,
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
    observer: str = "direct-read-test",
    method: str = "fake-direct-read",
    observed_at: datetime.datetime = _COMPLETED_AT,
    digest: str = "digest-observation-01",
) -> GitObservation:
    return GitObservation(
        observation_id="observation-01",
        source=source,
        repository=repository or _repository(),
        full_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        sha=sha,
        observer=observer,
        method=method,
        exit_status=0,
        observed_at=observed_at,
        normalized_evidence_digest=digest,
    )


def _read_result(
    disposition: DirectRemoteReadDisposition = DirectRemoteReadDisposition.OBSERVED,
    source: GitObservationSource = GitObservationSource.DIRECT_REMOTE_REF,
    sha: str | None = _LOCAL_SHA,
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
    observer: str = "direct-read-test",
    method: str = "fake-direct-read",
    observed_at: datetime.datetime = _COMPLETED_AT,
    digest: str = "digest-readback-01",
) -> DirectRemoteReadResult:
    return DirectRemoteReadResult(
        disposition=disposition,
        source=source,
        repository=repository or _repository(),
        full_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        sha=sha,
        observer=observer,
        method=method,
        exit_status=0,
        observed_at=observed_at,
        normalized_evidence_digest=digest,
    )


def _push_result(
    disposition: NonForcePushDisposition = NonForcePushDisposition.ACCEPTED,
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
    attempt_id: str = "attempt-01",
    expected_base_sha: str = _BASE_SHA,
    requested_sha: str = _LOCAL_SHA,
    executor: str = "fake-push-executor",
    method: str = "fake-non-force-push",
    digest: str = "digest-push-01",
    completed_at: datetime.datetime = _COMPLETED_AT,
) -> NonForcePushResult:
    return NonForcePushResult(
        disposition=disposition,
        repository=repository or _repository(),
        full_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        attempt_id=attempt_id,
        expected_base_sha=expected_base_sha,
        requested_sha=requested_sha,
        executor=executor,
        method=method,
        normalized_evidence_digest=digest,
        exit_status=0,
        completed_at=completed_at,
    )


def _lifecycle() -> PrePushLifecycleTransition:
    return PrePushLifecycleTransition(state=AuthorityIntegrationState.LOCAL_INTEGRATED)


def _failed_lifecycle() -> PrePushLifecycleTransition:
    return advance_pre_push_lifecycle(
        PrePushLifecycleRequest(
            current_state=AuthorityIntegrationState.CANDIDATE,
            requested_state=AuthorityIntegrationState.CANDIDATE,
        )
    )


def _request(
    lifecycle: PrePushLifecycleTransition | None = None,
    pre_push: GitObservation | None = None,
    local_sha: str = _LOCAL_SHA,
    attempt_id: str = "attempt-01",
    post_id: str = "post-observation-01",
    requested_at: datetime.datetime = _REQUESTED_AT,
    decision_at: datetime.datetime = _DECISION_AT,
) -> AuthorityFinalizationRequest:
    return AuthorityFinalizationRequest(
        authority_contract=_contract(),
        local_lifecycle=lifecycle or _lifecycle(),
        local_integrated_sha=local_sha,
        pre_push_observation=pre_push or _observation(),
        attempt_id=attempt_id,
        post_push_observation_id=post_id,
        requested_at=requested_at,
        decision_at=decision_at,
    )


class _FakePushPort:
    def __init__(self, result: NonForcePushResult) -> None:
        self.result = result
        self.calls = 0
        self.requests: list[NonForcePushRequest] = []

    def push(self, request: NonForcePushRequest, /) -> NonForcePushResult:
        self.calls += 1
        self.requests.append(request)
        return self.result


class _FakeObservationPort:
    def __init__(self, result: DirectRemoteReadResult) -> None:
        self.result = result
        self.calls = 0
        self.requests: list[DirectRemoteObservationRequest] = []

    def observe(
        self,
        request: DirectRemoteObservationRequest,
        /,
    ) -> DirectRemoteReadResult:
        self.calls += 1
        self.requests.append(request)
        return self.result


def _run(
    request: AuthorityFinalizationRequest,
    push_result: NonForcePushResult,
    read_result: DirectRemoteReadResult,
) -> tuple[AuthorityFinalizationResult, _FakePushPort, _FakeObservationPort]:
    push_port = _FakePushPort(push_result)
    observation_port = _FakeObservationPort(read_result)
    result = finalize_authority_integration(request, push_port, observation_port)
    return result, push_port, observation_port


def test_finalize_authority_integration_accepts_one_push_and_matching_readback() -> None:
    result, push_port, observation_port = _run(
        _request(),
        _push_result(),
        _read_result(),
    )

    assert result.state is AuthorityIntegrationState.AUTHORITY_INTEGRATED
    assert result.failure is None
    assert result.push == _push_result()
    assert result.readback is not None
    assert result.readback.sha == _LOCAL_SHA
    assert result.readback.source is GitObservationSource.DIRECT_REMOTE_REF
    assert push_port.calls == 1
    assert observation_port.calls == 1
    assert push_port.requests[0].expected_remote_base.sha == _BASE_SHA
    assert push_port.requests[0].local_integrated_sha == _LOCAL_SHA
    assert observation_port.requests[0].valid_from == _COMPLETED_AT
    assert observation_port.requests[0].expected_sha is None


def test_finalization_public_models_are_strict_and_closed() -> None:
    assert set(NonForcePushDisposition) == {
        NonForcePushDisposition.ACCEPTED,
        NonForcePushDisposition.REJECTED,
        NonForcePushDisposition.UNCONFIRMED,
    }
    assert set(AuthorityFinalizationFailure) == {
        AuthorityFinalizationFailure.LOCAL_INTEGRATION_EVIDENCE_INVALID,
        AuthorityFinalizationFailure.PRE_PUSH_OBSERVATION_INVALID,
        AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH,
        AuthorityFinalizationFailure.AUTHORITY_REF_MOVED,
        AuthorityFinalizationFailure.PUSH_REJECTED,
        AuthorityFinalizationFailure.PUSH_UNCONFIRMED,
        AuthorityFinalizationFailure.DIRECT_REMOTE_READ_UNAVAILABLE,
        AuthorityFinalizationFailure.REMOTE_REF_NOT_FOUND,
        AuthorityFinalizationFailure.REMOTE_REF_AMBIGUOUS,
        AuthorityFinalizationFailure.DIRECT_REMOTE_OBSERVATION_STALE,
        AuthorityFinalizationFailure.REMOTE_READBACK_SHA_MISMATCH,
        AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED,
    }
    valid_request = NonForcePushRequest(
        authority_contract=_contract(),
        attempt_id="attempt-01",
        expected_remote_base=_observation(),
        local_integrated_sha=_LOCAL_SHA,
        requested_at=_REQUESTED_AT,
    )
    assert valid_request.expected_remote_base.source is GitObservationSource.DIRECT_REMOTE_REF
    for disposition in NonForcePushDisposition:
        assert _push_result(disposition=disposition).disposition is disposition
    fake_push: NonForcePushPort = _FakePushPort(_push_result())
    fake_observation: DirectRemoteObservationPort = _FakeObservationPort(_read_result())
    assert isinstance(fake_push, _FakePushPort)
    assert isinstance(fake_observation, _FakeObservationPort)
    assert list(inspect.signature(NonForcePushPort.push).parameters.values())[-1].kind is inspect.Parameter.POSITIONAL_ONLY
    finalization = _request()
    accepted = AuthorityFinalizationResult(
        state=AuthorityIntegrationState.AUTHORITY_INTEGRATED,
        push=_push_result(),
        readback=_observation(sha=_LOCAL_SHA),
    )
    assert accepted.state is AuthorityIntegrationState.AUTHORITY_INTEGRATED
    for failure in AuthorityFinalizationFailure:
        rejected = AuthorityFinalizationResult(
            state=AuthorityIntegrationState.PUSH_UNCONFIRMED,
            failure=failure,
        )
        assert rejected.failure is failure
    assert finalization.authority_contract == valid_request.authority_contract

    with pytest.raises(ValidationError):
        NonForcePushRequest(
            authority_contract=_contract(),
            attempt_id="attempt-01",
            expected_remote_base=_observation(source=GitObservationSource.REMOTE_TRACKING_CACHE),
            local_integrated_sha=_LOCAL_SHA,
            requested_at=_REQUESTED_AT,
        )
    with pytest.raises(ValidationError):
        NonForcePushRequest(
            authority_contract=_contract(),
            attempt_id="",
            expected_remote_base=_observation(),
            local_integrated_sha="short",
            requested_at=_REQUESTED_AT.replace(tzinfo=None),
        )
    with pytest.raises(ValidationError):
        _request(requested_at=_DECISION_AT, decision_at=_REQUESTED_AT)
    with pytest.raises(ValidationError):
        _push_result(executor="token:secret")
    with pytest.raises(ValidationError):
        AuthorityFinalizationResult(state=AuthorityIntegrationState.AUTHORITY_INTEGRATED)
    with pytest.raises(ValidationError):
        AuthorityFinalizationResult(
            state=AuthorityIntegrationState.PUSH_UNCONFIRMED,
            failure=AuthorityFinalizationFailure.PUSH_UNCONFIRMED,
            readback=_observation(source=GitObservationSource.REMOTE_TRACKING_CACHE),
        )
    with pytest.raises(ValidationError):
        AuthorityFinalizationRequest.model_validate(
            {
                "authority_contract": _contract(),
                "local_lifecycle": _lifecycle(),
                "local_integrated_sha": _LOCAL_SHA,
                "pre_push_observation": _observation(),
                "attempt_id": "attempt-01",
                "post_push_observation_id": "post-01",
                "requested_at": _REQUESTED_AT,
                "decision_at": _DECISION_AT,
                "extra": "forbidden",
            }
        )
    with pytest.raises(ValidationError):
        NonForcePushResult.model_validate(
            {
                "disposition": "UNDECLARED",
                "repository": _repository(),
                "full_ref": FullBranchRef(value="refs/heads/main"),
                "attempt_id": "attempt-01",
                "expected_base_sha": _BASE_SHA,
                "requested_sha": _LOCAL_SHA,
                "executor": "fake",
                "method": "fake",
                "normalized_evidence_digest": "digest",
                "exit_status": 0,
                "completed_at": _COMPLETED_AT,
            }
        )


def test_finalization_rejects_invalid_local_or_base_before_any_port_call() -> None:
    cases: tuple[tuple[AuthorityFinalizationRequest, AuthorityFinalizationFailure], ...] = (
        (_request(lifecycle=PrePushLifecycleTransition(state=AuthorityIntegrationState.REVIEW_ACCEPTED)), AuthorityFinalizationFailure.LOCAL_INTEGRATION_EVIDENCE_INVALID),
        (_request(lifecycle=_failed_lifecycle()), AuthorityFinalizationFailure.LOCAL_INTEGRATION_EVIDENCE_INVALID),
        (_request(pre_push=_observation(source=GitObservationSource.REMOTE_TRACKING_CACHE)), AuthorityFinalizationFailure.PRE_PUSH_OBSERVATION_INVALID),
        (_request(pre_push=_observation(repository=_repository("foreign/project"))), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_request(pre_push=_observation(full_ref=FullBranchRef(value="refs/heads/release"))), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_request(pre_push=_observation(observed_at=_COMPLETED_AT.replace(tzinfo=None))), AuthorityFinalizationFailure.PRE_PUSH_OBSERVATION_INVALID),
        (_request(pre_push=_observation(observer="token:secret")), AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED),
    )
    for request, expected_failure in cases:
        result, push_port, observation_port = _run(request, _push_result(), _read_result())
        assert result.failure is expected_failure
        assert result.state is AuthorityIntegrationState.PUSH_UNCONFIRMED
        assert push_port.calls == 0
        assert observation_port.calls == 0


def test_push_result_integrity_maps_failures_and_does_not_read_back() -> None:
    cases: tuple[tuple[NonForcePushResult, AuthorityFinalizationFailure], ...] = (
        (_push_result(repository=_repository("foreign/project")), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_push_result(full_ref=FullBranchRef(value="refs/heads/release")), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_push_result(attempt_id="wrong-attempt"), AuthorityFinalizationFailure.PUSH_UNCONFIRMED),
        (_push_result(expected_base_sha=_OTHER_SHA), AuthorityFinalizationFailure.AUTHORITY_REF_MOVED),
        (_push_result(requested_sha=_OTHER_SHA), AuthorityFinalizationFailure.PUSH_UNCONFIRMED),
        (_push_result(repository=_repository("https://user:token@example.test/org/project")), AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED),
        (_push_result(disposition=NonForcePushDisposition.REJECTED), AuthorityFinalizationFailure.PUSH_REJECTED),
        (_push_result(disposition=NonForcePushDisposition.UNCONFIRMED), AuthorityFinalizationFailure.PUSH_UNCONFIRMED),
    )
    for push_result, expected_failure in cases:
        result, push_port, observation_port = _run(_request(), push_result, _read_result())
        assert result.failure is expected_failure
        assert result.state is AuthorityIntegrationState.PUSH_UNCONFIRMED
        if expected_failure is AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED:
            assert result.push is None
            assert result.readback is None
        assert push_port.calls == 1
        assert observation_port.calls == 0


def test_post_push_readback_maps_each_unproved_direct_outcome() -> None:
    cases: tuple[tuple[DirectRemoteReadResult, AuthorityFinalizationFailure], ...] = (
        (_read_result(DirectRemoteReadDisposition.UNAVAILABLE, sha=None), AuthorityFinalizationFailure.DIRECT_REMOTE_READ_UNAVAILABLE),
        (_read_result(DirectRemoteReadDisposition.NOT_FOUND, sha=None), AuthorityFinalizationFailure.REMOTE_REF_NOT_FOUND),
        (_read_result(DirectRemoteReadDisposition.AMBIGUOUS, sha=None), AuthorityFinalizationFailure.REMOTE_REF_AMBIGUOUS),
        (_read_result(source=GitObservationSource.REMOTE_TRACKING_CACHE), AuthorityFinalizationFailure.DIRECT_REMOTE_READ_UNAVAILABLE),
        (_read_result(observed_at=_COMPLETED_AT - datetime.timedelta(minutes=1)), AuthorityFinalizationFailure.DIRECT_REMOTE_OBSERVATION_STALE),
        (_read_result(observed_at=_DECISION_AT + datetime.timedelta(minutes=1)), AuthorityFinalizationFailure.DIRECT_REMOTE_OBSERVATION_STALE),
        (_read_result(repository=_repository("foreign/project")), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_read_result(full_ref=FullBranchRef(value="refs/heads/release")), AuthorityFinalizationFailure.REMOTE_IDENTITY_MISMATCH),
        (_read_result(observer="token:secret"), AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED),
        (_read_result(method="authorization: bearer secret"), AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED),
        (_read_result(digest="password=secret"), AuthorityFinalizationFailure.SECRET_MATERIAL_DETECTED),
    )
    for read_result, expected_failure in cases:
        result, push_port, observation_port = _run(_request(), _push_result(), read_result)
        assert result.failure is expected_failure
        assert result.state is AuthorityIntegrationState.PUSH_UNCONFIRMED
        assert result.push == _push_result()
        assert push_port.calls == 1
        assert observation_port.calls == 1


def test_readback_sha_and_base_race_never_claim_authority() -> None:
    mismatch, _, observation_port = _run(
        _request(),
        _push_result(),
        _read_result(sha=_OTHER_SHA),
    )
    assert mismatch.failure is AuthorityFinalizationFailure.REMOTE_READBACK_SHA_MISMATCH
    assert mismatch.state is AuthorityIntegrationState.PUSH_UNCONFIRMED
    assert mismatch.readback is not None
    assert mismatch.readback.sha == _OTHER_SHA
    assert observation_port.calls == 1

    moved, _, moved_observation_port = _run(
        _request(),
        _push_result(expected_base_sha=_OTHER_SHA),
        _read_result(),
    )
    assert moved.failure is AuthorityFinalizationFailure.AUTHORITY_REF_MOVED
    assert moved.state is AuthorityIntegrationState.PUSH_UNCONFIRMED
    assert moved_observation_port.calls == 0


def test_finalization_ast_gate_targets_owned_production_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    integration_path = root / "library/local_orchestration/project_authority/integration.py"
    init_path = root / "library/local_orchestration/project_authority/__init__.py"
    integration_tree = ast.parse(integration_path.read_text(encoding="utf-8"))
    init_tree = ast.parse(init_path.read_text(encoding="utf-8"))
    integration_all = (
        "PrePushLifecycleRequest",
        "PrePushLifecycleTransition",
        "advance_pre_push_lifecycle",
        "NonForcePushDisposition",
        "NonForcePushRequest",
        "NonForcePushResult",
        "NonForcePushPort",
        "AuthorityFinalizationFailure",
        "AuthorityFinalizationRequest",
        "AuthorityFinalizationResult",
        "finalize_authority_integration",
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
        "library.local_orchestration.project_authority.observation",
        "contracts",
        "integration",
        "observation",
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

    assert literal_all(integration_tree) == integration_all
    assert literal_all(init_tree) == frozen_init_all + observation_all + finalization_all
    declarations = {
        node.name
        for node in integration_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }
    assert declarations == set(integration_all) - {
        "PrePushLifecycleRequest",
        "PrePushLifecycleTransition",
    }
    public_assignments = {
        target.id
        for node in integration_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and not target.id.startswith("_")
    }
    public_assignments.update(
        node.target.id
        for node in integration_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and not node.target.id.startswith("_")
    )
    assert public_assignments == set()
    for tree in (integration_tree, init_tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id not in forbidden_names
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names
                if isinstance(node.value, ast.Name):
                    assert f"{node.value.id}.{node.attr}" not in {"datetime.now", "datetime.utcnow"}
            if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                raise AssertionError("integration boundary must not loop")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in allowed_modules
            if isinstance(node, ast.ImportFrom):
                assert node.module in allowed_modules
                if node.module == "library.local_orchestration.project_authority.observation":
                    assert tuple(alias.name for alias in node.names) == (
                        "DirectRemoteObservationPort",
                        "DirectRemoteObservationRequest",
                        "DirectRemoteObservationResult",
                        "DirectRemoteObservationDecision",
                        "observe_declared_remote",
                    )
