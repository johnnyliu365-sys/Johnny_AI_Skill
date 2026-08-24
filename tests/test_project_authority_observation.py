"""T01-T08 focused tests for the pure direct-observation seam."""

from __future__ import annotations

import ast
import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from library.local_orchestration.project_authority.contracts import (
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    AuthorityLineRole,
    ProjectTopology,
    ProjectAuthorityContract,
    RemoteProviderKind,
    RemoteRepositoryId,
)
from library.local_orchestration.project_authority.observation import (
    DirectRemoteObservationDecision,
    DirectRemoteObservationPort,
    DirectRemoteObservationRequest,
    DirectRemoteObservationResult,
    DirectRemoteReadDisposition,
    DirectRemoteReadResult,
    observe_declared_remote,
)


_SHA = "0123456789abcdef0123456789abcdef01234567"
_OTHER_SHA = "fedcba9876543210fedcba9876543210fedcba98"
_UTC = datetime.timezone.utc
_VALID_FROM = datetime.datetime(2026, 8, 24, 10, 0, tzinfo=_UTC)
_OBSERVED_AT = datetime.datetime(2026, 8, 24, 11, 0, tzinfo=_UTC)
_DECISION_AT = datetime.datetime(2026, 8, 24, 12, 0, tzinfo=_UTC)


def _repository(repository_key: str = "org/project-authority") -> RemoteRepositoryId:
    return RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GITHUB,
        host="github.com",
        repository_key=repository_key,
        alias="origin",
    )


def _contract(
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
) -> ProjectAuthorityContract:
    return ProjectAuthorityContract(
        project_id="project-authority",
        topology=ProjectTopology.SINGLE_BRANCH,
        authority_line_role=AuthorityLineRole.SINGLE,
        project_authority_ref=full_ref or FullBranchRef(value="refs/heads/main"),
        remote_repository=repository or _repository(),
        declaration_artifact_ref="doc/adr/ADR-20260824-020",
        declaration_revision_sha=_SHA,
        gate_id="gate-project-authority",
        gate_revision=_SHA,
        effective_at=_VALID_FROM,
    )


def _request(expected_sha: str | None = None) -> DirectRemoteObservationRequest:
    return DirectRemoteObservationRequest(
        authority_contract=_contract(),
        observation_id="observation-01",
        valid_from=_VALID_FROM,
        decision_at=_DECISION_AT,
        expected_sha=expected_sha,
    )


def _read_result(
    disposition: DirectRemoteReadDisposition = DirectRemoteReadDisposition.OBSERVED,
    source: GitObservationSource = GitObservationSource.DIRECT_REMOTE_REF,
    repository: RemoteRepositoryId | None = None,
    full_ref: FullBranchRef | None = None,
    sha: str | None = _SHA,
    observer: str = "direct-read-test",
    method: str = "fake-direct-read",
    observed_at: datetime.datetime = _OBSERVED_AT,
    normalized_evidence_digest: str = "digest-observation-01",
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
        normalized_evidence_digest=normalized_evidence_digest,
    )


class _FakeDirectReadPort:
    def __init__(self, result: DirectRemoteReadResult) -> None:
        self.result = result
        self.calls = 0

    def observe(self, request: DirectRemoteObservationRequest, /) -> DirectRemoteReadResult:
        self.calls += 1
        return self.result


class _UnexpectedExceptionPort:
    def __init__(self) -> None:
        self.calls = 0

    def observe(self, request: DirectRemoteObservationRequest, /) -> DirectRemoteReadResult:
        self.calls += 1
        raise RuntimeError("fake-port-defect")


def _direct_observation(
    source: GitObservationSource = GitObservationSource.DIRECT_REMOTE_REF,
) -> GitObservation:
    return GitObservation(
        observation_id="observation-01",
        source=source,
        repository=_repository(),
        full_ref=FullBranchRef(value="refs/heads/main"),
        sha=_SHA,
        observer="direct-read-test",
        method="fake-direct-read",
        exit_status=0,
        observed_at=_OBSERVED_AT,
        normalized_evidence_digest="digest-observation-01",
    )


def test_observe_declared_remote_accepts_one_direct_fake_read() -> None:
    request = _request()
    port = _FakeDirectReadPort(_read_result())

    result = observe_declared_remote(request, port)

    assert result.decision is DirectRemoteObservationDecision.ACCEPTED
    assert result.failure is None
    assert result.observation == _direct_observation()
    assert result.observation is not None
    assert result.observation.repository == request.authority_contract.remote_repository
    assert result.observation.full_ref == request.authority_contract.project_authority_ref
    assert result.observation.sha == _SHA
    assert result.observation.observer == "direct-read-test"
    assert result.observation.method == "fake-direct-read"
    assert result.observation.observed_at == _OBSERVED_AT
    assert result.observation.normalized_evidence_digest == "digest-observation-01"
    assert port.calls == 1


def test_direct_remote_public_models_are_strict_and_closed() -> None:
    for disposition in DirectRemoteReadDisposition:
        sha = _SHA if disposition is DirectRemoteReadDisposition.OBSERVED else None
        read_result = _read_result(disposition=disposition, sha=sha)
        assert read_result.disposition is disposition
    for decision in DirectRemoteObservationDecision:
        if decision is DirectRemoteObservationDecision.ACCEPTED:
            result = DirectRemoteObservationResult(
                decision=decision,
                observation=_direct_observation(),
            )
        else:
            result = DirectRemoteObservationResult(decision=decision, failure=decision)
        assert result.decision is decision
    with pytest.raises(ValidationError):
        DirectRemoteObservationResult(
            decision=DirectRemoteObservationDecision.ACCEPTED,
            observation=_direct_observation(GitObservationSource.REMOTE_TRACKING_CACHE),
        )

    assert DirectRemoteObservationRequest.model_validate(
        {
            "authority_contract": _contract(),
            "observation_id": "observation-null-sha",
            "valid_from": _VALID_FROM,
            "decision_at": _DECISION_AT,
            "expected_sha": None,
        }
    ).expected_sha is None
    assert _request(expected_sha=_SHA).expected_sha == _SHA
    fake: DirectRemoteObservationPort = _FakeDirectReadPort(_read_result())
    assert observe_declared_remote(_request(), fake).decision is DirectRemoteObservationDecision.ACCEPTED

    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest.model_validate(
            {
                "authority_contract": _contract(),
                "observation_id": None,
                "valid_from": _VALID_FROM,
                "decision_at": _DECISION_AT,
            }
        )
    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest.model_validate(
            {
                "authority_contract": _contract(),
                "observation_id": 7,
                "valid_from": _VALID_FROM,
                "decision_at": _DECISION_AT,
            }
        )
    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest.model_validate(
            {
                "authority_contract": _contract(),
                "observation_id": "observation-extra",
                "valid_from": _VALID_FROM,
                "decision_at": _DECISION_AT,
                "extra": "forbidden",
            }
        )
    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest.model_validate(
            {
                "authority_contract": _contract(),
                "observation_id": "observation-coercion",
                "valid_from": _VALID_FROM.isoformat(),
                "decision_at": _DECISION_AT,
            }
        )
    with pytest.raises(ValidationError):
        _request(expected_sha="abbreviated")
    with pytest.raises(ValidationError):
        _request(expected_sha="A" * 40)
    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest(
            authority_contract=_contract(),
            observation_id="observation-naive",
            valid_from=datetime.datetime(2026, 8, 24, 10, 0),
            decision_at=_DECISION_AT,
        )
    with pytest.raises(ValidationError):
        DirectRemoteObservationRequest(
            authority_contract=_contract(),
            observation_id="observation-inverted",
            valid_from=_DECISION_AT,
            decision_at=_VALID_FROM,
        )

    with pytest.raises(ValidationError):
        DirectRemoteReadResult.model_validate(
            {
                "disposition": "UNDECLARED",
                "source": GitObservationSource.DIRECT_REMOTE_REF,
                "repository": _repository(),
                "full_ref": FullBranchRef(value="refs/heads/main"),
                "sha": _SHA,
                "observer": "observer",
                "method": "method",
                "exit_status": 0,
                "observed_at": _OBSERVED_AT,
                "normalized_evidence_digest": "digest",
            }
        )
    with pytest.raises(ValidationError):
        DirectRemoteReadResult.model_validate(
            {
                "disposition": DirectRemoteReadDisposition.OBSERVED,
                "source": "UNDECLARED",
                "repository": _repository(),
                "full_ref": FullBranchRef(value="refs/heads/main"),
                "sha": _SHA,
                "observer": "observer",
                "method": "method",
                "exit_status": 0,
                "observed_at": _OBSERVED_AT,
                "normalized_evidence_digest": "digest",
            }
        )
    with pytest.raises(ValidationError):
        _read_result(disposition=DirectRemoteReadDisposition.OBSERVED, sha=None)
    with pytest.raises(ValidationError):
        _read_result(disposition=DirectRemoteReadDisposition.NOT_FOUND, sha=_SHA)
    with pytest.raises(ValidationError):
        _read_result(observed_at=datetime.datetime(2026, 8, 24, 11, 0))
    with pytest.raises(ValidationError):
        DirectRemoteObservationResult.model_validate(
            {"decision": "UNDECLARED", "failure": "UNDECLARED"}
        )


def test_observe_declared_remote_maps_normal_dispositions_and_preserves_unexpected_exception() -> None:
    expected = {
        DirectRemoteReadDisposition.UNAVAILABLE: DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE,
        DirectRemoteReadDisposition.NOT_FOUND: DirectRemoteObservationDecision.REMOTE_REF_NOT_FOUND,
        DirectRemoteReadDisposition.AMBIGUOUS: DirectRemoteObservationDecision.REMOTE_REF_AMBIGUOUS,
    }
    for disposition, decision in expected.items():
        port = _FakeDirectReadPort(_read_result(disposition=disposition, sha=None))
        result = observe_declared_remote(_request(), port)
        assert result.decision is decision
        assert result.failure is decision
        assert result.observation is None
        assert port.calls == 1

    unexpected_port = _UnexpectedExceptionPort()
    with pytest.raises(RuntimeError, match="fake-port-defect"):
        observe_declared_remote(_request(), unexpected_port)
    assert unexpected_port.calls == 1


def test_observe_declared_remote_rejects_tracking_cache() -> None:
    port = _FakeDirectReadPort(
        _read_result(source=GitObservationSource.REMOTE_TRACKING_CACHE)
    )

    result = observe_declared_remote(_request(), port)

    assert result.decision is DirectRemoteObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE
    assert result.observation is None
    assert port.calls == 1


def test_observe_declared_remote_rejects_repository_or_ref_mismatch() -> None:
    repository_mismatch = _FakeDirectReadPort(
        _read_result(
            source=GitObservationSource.REMOTE_TRACKING_CACHE,
            repository=_repository("other/project"),
            observed_at=datetime.datetime(2026, 8, 24, 1, 0, tzinfo=_UTC),
        )
    )
    ref_mismatch = _FakeDirectReadPort(
        _read_result(
            source=GitObservationSource.REMOTE_TRACKING_CACHE,
            full_ref=FullBranchRef(value="refs/heads/develop"),
            observed_at=datetime.datetime(2026, 8, 24, 1, 0, tzinfo=_UTC),
        )
    )

    repository_result = observe_declared_remote(_request(), repository_mismatch)
    ref_result = observe_declared_remote(_request(), ref_mismatch)

    assert repository_result.decision is DirectRemoteObservationDecision.REMOTE_IDENTITY_MISMATCH
    assert ref_result.decision is DirectRemoteObservationDecision.REMOTE_IDENTITY_MISMATCH
    assert repository_result.observation is None
    assert ref_result.observation is None


def test_observe_declared_remote_rejects_stale_or_moved_read() -> None:
    before = _FakeDirectReadPort(
        _read_result(
            observed_at=datetime.datetime(2026, 8, 24, 9, 59, tzinfo=_UTC)
        )
    )
    after = _FakeDirectReadPort(
        _read_result(
            observed_at=datetime.datetime(2026, 8, 24, 12, 1, tzinfo=_UTC)
        )
    )
    moved = _FakeDirectReadPort(_read_result())

    before_result = observe_declared_remote(_request(), before)
    after_result = observe_declared_remote(_request(), after)
    moved_result = observe_declared_remote(_request(expected_sha=_OTHER_SHA), moved)

    assert before_result.decision is DirectRemoteObservationDecision.DIRECT_REMOTE_OBSERVATION_STALE
    assert after_result.decision is DirectRemoteObservationDecision.DIRECT_REMOTE_OBSERVATION_STALE
    assert moved_result.decision is DirectRemoteObservationDecision.AUTHORITY_REF_MOVED
    assert before_result.observation is None
    assert after_result.observation is None
    assert moved_result.observation is None


def test_observe_declared_remote_rejects_credential_metadata() -> None:
    credential_cases = (
        _read_result(observer="token=observer-secret"),
        _read_result(method="password=method-secret"),
        _read_result(normalized_evidence_digest="authorization=digest-secret"),
    )
    for read_result in credential_cases:
        port = _FakeDirectReadPort(read_result)
        result = observe_declared_remote(_request(), port)
        assert result.decision is DirectRemoteObservationDecision.SECRET_MATERIAL_DETECTED
        assert result.observation is None
        assert result.failure is DirectRemoteObservationDecision.SECRET_MATERIAL_DETECTED
        assert "secret" not in result.model_dump_json()
        assert port.calls == 1


def test_direct_remote_observation_ast_gate_targets_owned_production_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    observation_path = root / "library/local_orchestration/project_authority/observation.py"
    init_path = root / "library/local_orchestration/project_authority/__init__.py"
    observation_tree = ast.parse(observation_path.read_text(encoding="utf-8"))
    init_tree = ast.parse(init_path.read_text(encoding="utf-8"))
    observation_all = (
        "DirectRemoteObservationDecision",
        "DirectRemoteObservationPort",
        "DirectRemoteObservationRequest",
        "DirectRemoteObservationResult",
        "DirectRemoteReadDisposition",
        "DirectRemoteReadResult",
        "observe_declared_remote",
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
    init_all = frozen_init_all + observation_all
    allowed_modules = {
        "__future__",
        "datetime",
        "enum",
        "re",
        "typing",
        "pydantic",
        "library.local_orchestration.project_authority.contracts",
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
        "NonForcePushPort",
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
    }

    def literal_all(tree: ast.Module) -> tuple[str, ...]:
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in node.targets
                ):
                    if not isinstance(node.value, (ast.Tuple, ast.List)):
                        raise AssertionError("__all__ must be a literal sequence")
                    values: list[str] = []
                    for element in node.value.elts:
                        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                            raise AssertionError("__all__ must contain strings")
                        values.append(element.value)
                    return tuple(values)
        raise AssertionError("missing __all__")

    assert literal_all(observation_tree) == observation_all
    assert literal_all(init_tree) == init_all
    observation_public_declarations = {
        node.name
        for node in observation_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }
    assert observation_public_declarations == set(observation_all)
    observation_public_assignments = {
        target.id
        for node in observation_tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and not target.id.startswith("_")
    }
    observation_public_assignments.update(
        node.target.id
        for node in observation_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and not node.target.id.startswith("_")
    )
    assert observation_public_assignments == set()

    for tree in (observation_tree, init_tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id not in forbidden_names
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden_names
                if isinstance(node.value, ast.Name):
                    assert f"{node.value.id}.{node.attr}" not in {"datetime.now", "datetime.utcnow"}
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in allowed_modules
            if isinstance(node, ast.ImportFrom):
                assert node.module is not None
                if node.module not in allowed_modules:
                    assert node.module in {
                        "contracts",
                        "integration",
                        "observation",
                        "library.local_orchestration.project_authority.observation",
                    }
