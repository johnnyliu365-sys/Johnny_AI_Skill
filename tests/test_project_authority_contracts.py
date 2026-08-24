"""T01-T07 focused tests for the pure project-authority boundary."""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from library.local_orchestration.project_authority.contracts import (
    AuthorityContractAdmission,
    AuthorityContractAdmissionDecision,
    AuthorityContractInput,
    AuthorityIntegrationState,
    AuthorityLineRole,
    AuthorityObservationAdmission,
    AuthorityObservationDecision,
    BridgeCapability,
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    ProjectTopology,
    RemoteProviderKind,
    RemoteRepositoryId,
    admit_authority_contract,
    admit_authority_observation,
)
from library.local_orchestration.project_authority.integration import (
    PrePushLifecycleRequest,
    PrePushLifecycleTransition,
    advance_pre_push_lifecycle,
)


_SHA = "0123456789abcdef0123456789abcdef01234567"
_EFFECTIVE_AT = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)


def _input(**overrides: object) -> AuthorityContractInput:
    values: dict[str, object] = {
        "project_id": "project-authority",
        "topology": ProjectTopology.SINGLE_BRANCH,
        "authority_line_role": AuthorityLineRole.SINGLE,
        "project_authority_ref": "refs/heads/main",
        "remote_provider_kind": RemoteProviderKind.GITHUB,
        "remote_host": "github.com",
        "remote_repository_key": "org/project-authority",
        "remote_alias": "origin",
        "declaration_artifact_ref": "doc/adr/ADR-20260824-020",
        "declaration_revision_sha": _SHA,
        "gate_id": "gate-project-authority",
        "gate_revision": _SHA,
        "effective_at": _EFFECTIVE_AT,
    }
    values.update(overrides)
    return AuthorityContractInput.model_validate(values)


def _repository() -> RemoteRepositoryId:
    return RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GITHUB,
        host="github.com",
        repository_key="org/project-authority",
        alias="origin",
    )


def _observation(source: GitObservationSource) -> GitObservation:
    return GitObservation(
        observation_id="observation-01",
        source=source,
        repository=_repository(),
        full_ref=FullBranchRef(value="refs/heads/main"),
        sha=_SHA,
        observer="direct-read-test",
        method="test-readback",
        exit_status=0,
        observed_at=_EFFECTIVE_AT,
        normalized_evidence_digest="digest-observation-01",
    )


def test_admit_authority_contract_accepts_strict_input() -> None:
    result = admit_authority_contract(_input())

    assert result.decision is AuthorityContractAdmissionDecision.ACCEPTED
    assert result.contract is not None
    assert result.failure is None
    assert result.contract.project_authority_ref.value == "refs/heads/main"
    assert result.contract.remote_repository.repository_key == "org/project-authority"


def test_authority_contract_input_separates_structural_and_domain_rejection() -> None:
    structural_values: tuple[dict[str, object], ...] = (
        {"project_id": None},
        {"project_id": 17},
        {"effective_at": _EFFECTIVE_AT.isoformat()},
        {"unexpected": "field"},
    )
    for override in structural_values:
        with pytest.raises(ValidationError):
            _input(**override)

    invalid_refs = ("", "   ", "refs/tags/v1", "HEAD", "main", _SHA)
    for invalid_ref in invalid_refs:
        result = admit_authority_contract(_input(project_authority_ref=invalid_ref))
        assert result.decision is AuthorityContractAdmissionDecision.AUTHORITY_REF_INVALID
        assert result.contract is None


def test_admit_authority_contract_rejects_credential_identity() -> None:
    result = admit_authority_contract(
        _input(remote_repository_key="https://user:token@example.test/org/repo")
    )

    assert result.decision is AuthorityContractAdmissionDecision.SECRET_MATERIAL_DETECTED
    assert result.contract is None
    assert result.failure is AuthorityContractAdmissionDecision.SECRET_MATERIAL_DETECTED


def test_public_enums_and_lifecycle_request_are_closed() -> None:
    assert set(ProjectTopology) == {
        ProjectTopology.SINGLE_BRANCH,
        ProjectTopology.HIGH_COLLABORATION,
    }
    assert set(AuthorityLineRole) == {
        AuthorityLineRole.SINGLE,
        AuthorityLineRole.DEVELOPMENT,
        AuthorityLineRole.STAGING,
        AuthorityLineRole.RELEASE,
    }
    assert set(RemoteProviderKind) == {
        RemoteProviderKind.GIT_GENERIC,
        RemoteProviderKind.GITHUB,
        RemoteProviderKind.OTHER,
    }
    assert set(AuthorityContractAdmissionDecision) == {
        AuthorityContractAdmissionDecision.ACCEPTED,
        AuthorityContractAdmissionDecision.AUTHORITY_REF_INVALID,
        AuthorityContractAdmissionDecision.SECRET_MATERIAL_DETECTED,
    }
    assert set(AuthorityObservationDecision) == {
        AuthorityObservationDecision.DIRECT_REMOTE_REF_ACCEPTED,
        AuthorityObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE,
    }
    assert AuthorityContractInput.model_fields["topology"].annotation is ProjectTopology
    assert AuthorityContractInput.model_fields["authority_line_role"].annotation is AuthorityLineRole
    assert AuthorityContractInput.model_fields["remote_provider_kind"].annotation is RemoteProviderKind
    assert AuthorityContractAdmission.model_fields["decision"].annotation is AuthorityContractAdmissionDecision
    assert AuthorityObservationAdmission.model_fields["decision"].annotation is AuthorityObservationDecision

    for topology in ProjectTopology:
        assert _input(topology=topology).topology is topology
    for role in AuthorityLineRole:
        assert _input(authority_line_role=role).authority_line_role is role
    for provider in RemoteProviderKind:
        assert _input(remote_provider_kind=provider).remote_provider_kind is provider

    accepted = admit_authority_contract(_input())
    assert accepted.contract is not None
    for contract_decision in AuthorityContractAdmissionDecision:
        if contract_decision is AuthorityContractAdmissionDecision.ACCEPTED:
            contract_result = AuthorityContractAdmission(
                decision=contract_decision, contract=accepted.contract
            )
        else:
            contract_result = AuthorityContractAdmission(decision=contract_decision)
        assert contract_result.decision is contract_decision

    direct = _observation(GitObservationSource.DIRECT_REMOTE_REF)
    for observation_decision in AuthorityObservationDecision:
        if observation_decision is AuthorityObservationDecision.DIRECT_REMOTE_REF_ACCEPTED:
            observation_result = AuthorityObservationAdmission(
                decision=observation_decision, observation=direct
            )
        else:
            observation_result = AuthorityObservationAdmission(decision=observation_decision)
        assert observation_result.decision is observation_decision

    for state in AuthorityIntegrationState:
        request = PrePushLifecycleRequest(current_state=state, requested_state=state)
        assert request.current_state is state
    for capability in BridgeCapability:
        assert BridgeCapability(capability.value) is capability

    with pytest.raises(ValidationError):
        _input(topology="UNDECLARED")
    with pytest.raises(ValidationError):
        _input(authority_line_role="UNDECLARED")
    with pytest.raises(ValidationError):
        _input(remote_provider_kind="UNDECLARED")
    with pytest.raises(ValidationError):
        AuthorityContractAdmission.model_validate({"decision": "UNDECLARED"})
    with pytest.raises(ValidationError):
        AuthorityObservationAdmission.model_validate({"decision": "UNDECLARED"})
    invalid_observation = _observation(GitObservationSource.DIRECT_REMOTE_REF).model_dump()
    invalid_observation["source"] = "UNDECLARED"
    with pytest.raises(ValidationError):
        GitObservation.model_validate(invalid_observation)
    with pytest.raises(ValidationError):
        PrePushLifecycleRequest.model_validate(
            {"current_state": "UNDECLARED", "requested_state": AuthorityIntegrationState.CANDIDATE}
        )
    with pytest.raises(ValueError):
        BridgeCapability("UNDECLARED")


def test_admit_authority_observation_rejects_tracking_cache() -> None:
    cache = admit_authority_observation(_observation(GitObservationSource.REMOTE_TRACKING_CACHE))
    direct = admit_authority_observation(_observation(GitObservationSource.DIRECT_REMOTE_REF))

    assert cache.decision is AuthorityObservationDecision.DIRECT_REMOTE_READ_UNAVAILABLE
    assert cache.observation is None
    assert direct.decision is AuthorityObservationDecision.DIRECT_REMOTE_REF_ACCEPTED
    assert direct.observation is not None


def test_advance_pre_push_lifecycle_rejects_local_to_authority_shortcut() -> None:
    request = PrePushLifecycleRequest(
        current_state=AuthorityIntegrationState.LOCAL_INTEGRATED,
        requested_state=AuthorityIntegrationState.AUTHORITY_INTEGRATED,
    )

    result = advance_pre_push_lifecycle(request)

    assert result.state is AuthorityIntegrationState.LOCAL_INTEGRATED
    assert result.failure is not None
    assert result.failure.value == "PUSH_UNCONFIRMED"
    assert result.state.value != "AUTHORITY_INTEGRATED"


def test_pure_boundary_ast_gate_targets_owned_production_modules() -> None:
    root = Path(__file__).resolve().parents[1]
    production_paths = (
        root / "library/local_orchestration/project_authority/contracts.py",
        root / "library/local_orchestration/project_authority/integration.py",
    )
    expected_classes = {
        "FullBranchRef",
        "RemoteRepositoryId",
        "ProjectAuthorityContract",
        "GitObservation",
        "GitObservationSource",
        "AuthorityIntegrationState",
        "BridgeCapability",
        "ProjectTopology",
        "AuthorityLineRole",
        "RemoteProviderKind",
        "AuthorityContractAdmissionDecision",
        "AuthorityObservationDecision",
        "AuthorityContractInput",
        "AuthorityContractAdmission",
        "AuthorityObservationAdmission",
        "PrePushLifecycleRequest",
        "PrePushLifecycleTransition",
    }
    expected_functions = {"admit_authority_contract", "admit_authority_observation"}
    expected_module_all: dict[str, tuple[str, ...]] = {
        "contracts.py": (
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
        ),
        "integration.py": (
            "PrePushLifecycleRequest",
            "PrePushLifecycleTransition",
            "advance_pre_push_lifecycle",
        ),
    }
    expected_module_declarations: dict[str, set[str]] = {
        "contracts.py": expected_classes | expected_functions,
        "integration.py": {"advance_pre_push_lifecycle"},
    }
    allowed_import_modules = {"__future__", "datetime", "enum", "re", "typing", "pydantic"}
    forbidden = {
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
    }
    seen_names: set[str] = set()
    for path in production_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        module_declarations: set[str] = set()
        module_all: tuple[str, ...] | None = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                seen_names.add(node.id)
            if isinstance(node, ast.Attribute):
                seen_names.add(node.attr)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in allowed_import_modules
            if isinstance(node, ast.ImportFrom):
                assert node.module is not None
                if node.module not in allowed_import_modules:
                    assert node.module == "library.local_orchestration.project_authority.contracts"

        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    module_declarations.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        module_declarations.add(target.id)
                if any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in node.targets
                ):
                    if not isinstance(node.value, (ast.Tuple, ast.List)):
                        raise AssertionError("__all__ must be a literal sequence")
                    values: list[str] = []
                    for element in node.value.elts:
                        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                            raise AssertionError("__all__ must contain only string literals")
                        values.append(element.value)
                    module_all = tuple(values)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
                    module_declarations.add(node.target.id)

        assert module_all is not None
        assert module_all == expected_module_all[path.name]
        assert module_declarations == expected_module_declarations[path.name]
    assert seen_names.isdisjoint(forbidden)
