"""Constructor coverage for the Ticket 30A type-only construction cut."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from library.local_orchestration.mainline_source import (
    MainlineSourceFailure,
    MainlineSourceRequest,
    MainlineSourceResult,
    MainlineSourceScope,
    RawGitBlobReadResult,
    TargetRelativePath,
)
from library.local_orchestration.project_authority.contracts import (
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    RemoteProviderKind,
    RemoteRepositoryId,
)
from library.workflow_router.git_handoff_contracts import GitBlobReadStatus
from library.workflow_router.mainline_projection import MainlineProjection


def _observation(source: GitObservationSource = GitObservationSource.WORKTREE_HEAD) -> GitObservation:
    repository = RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GIT_GENERIC,
        host="fixture.invalid",
        repository_key="fixture/project",
        alias="origin",
    )
    return GitObservation(
        observation_id="synthetic-observation",
        source=source,
        repository=repository,
        full_ref=FullBranchRef(value="refs/heads/main"),
        sha="0123456789abcdef0123456789abcdef01234567",
        observer="ticket30a-test",
        method="synthetic fixture observation",
        exit_status=0,
        observed_at=datetime(2026, 10, 18, tzinfo=timezone.utc),
        normalized_evidence_digest="fixture-observation-digest",
    )


def _projection() -> MainlineProjection:
    return MainlineProjection(
        project_id="prj_0123456789abcdef",
        mainline_ref="mainline-alpha",
        source_revision="rev-0123456789abcdef",
        ready_for_recheck=("ticket-alpha",),
        waiting=(),
        incomplete_required=("ticket-alpha",),
        closure_candidate=False,
    )


def test_target_relative_path_accepts_canonical_relative_path() -> None:
    path = TargetRelativePath("modules/tickets/workflow-governance/README.md")

    assert path.value == "modules/tickets/workflow-governance/README.md"


@pytest.mark.parametrize(
    "value",
    (
        "",
        "/modules/tickets/feature/README.md",
        "C:/modules/tickets/feature/README.md",
        "C:\\modules\\tickets\\feature\\README.md",
        "modules//tickets/feature/README.md",
        "modules/./tickets/feature/README.md",
        "modules/tickets/../feature/README.md",
        "modules/tickets/feature/README.md/",
        "modules/tickets/feature/README.md\n",
    ),
)
def test_target_relative_path_rejects_noncanonical_values(value: str) -> None:
    with pytest.raises((TypeError, ValueError)):
        TargetRelativePath(value)


@pytest.mark.parametrize("value", (None, 1, True, b"modules/tickets/feature/README.md"))
def test_target_relative_path_rejects_non_string_primitives(value: object) -> None:
    with pytest.raises(TypeError):
        TargetRelativePath(value)  # type: ignore[arg-type]


def test_raw_git_blob_read_result_accepts_exact_raw_bytes_and_round_trips() -> None:
    result = RawGitBlobReadResult(status=GitBlobReadStatus.FOUND, payload=b"\xff\x00raw")

    assert RawGitBlobReadResult.model_validate(result.model_dump()) == result


@pytest.mark.parametrize(
    "status,payload",
    (
        (GitBlobReadStatus.FOUND, None),
        (GitBlobReadStatus.NOT_FOUND, b"unexpected"),
        (GitBlobReadStatus.UNAVAILABLE, b"unexpected"),
        ("FOUND", b"raw bytes"),
        (GitBlobReadStatus.FOUND, "decoded text"),
    ),
)
def test_raw_git_blob_read_result_rejects_invalid_payload_shapes(
    status: object,
    payload: object,
) -> None:
    with pytest.raises(ValidationError):
        RawGitBlobReadResult(status=status, payload=payload)  # type: ignore[arg-type]


def test_mainline_source_request_accepts_worktree_observation_and_round_trips() -> None:
    request = MainlineSourceRequest(
        project_id="prj_0123456789abcdef",
        feature="workflow-governance",
        observation=_observation(),
    )

    assert MainlineSourceRequest.model_validate_json(request.model_dump_json()) == request


@pytest.mark.parametrize(
    "source",
    (
        GitObservationSource.LOCAL_AUTHORITY_REF,
        GitObservationSource.REMOTE_TRACKING_CACHE,
        GitObservationSource.DIRECT_REMOTE_REF,
        GitObservationSource.PROVIDER_PR_READBACK,
        GitObservationSource.PROVIDER_POLICY_READBACK,
    ),
)
def test_mainline_source_request_rejects_non_synthetic_observations(
    source: GitObservationSource,
) -> None:
    with pytest.raises(ValidationError):
        MainlineSourceRequest(
            project_id="prj_0123456789abcdef",
            feature="workflow-governance",
            observation=_observation(source),
        )


def test_mainline_source_request_rejects_invalid_project_and_feature_primitives() -> None:
    with pytest.raises(ValidationError):
        MainlineSourceRequest(
            project_id="project",
            feature="workflow-governance",
            observation=_observation(),
        )
    with pytest.raises(ValidationError):
        MainlineSourceRequest(
            project_id="prj_0123456789abcdef",
            feature="Workflow Governance",
            observation=_observation(),
        )


@pytest.mark.parametrize(
    "kwargs",
    (
        {"projection": None, "failure": None},
        {"projection": _projection(), "failure": MainlineSourceFailure.INDEX_NOT_FOUND},
        {"projection": _projection(), "failure": None, "payload": b"raw source"},
        {"projection": None, "failure": "UNKNOWN_FAILURE"},
    ),
)
def test_mainline_source_result_rejects_invalid_outcome_or_raw_payload(
    kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        MainlineSourceResult(**kwargs)  # type: ignore[arg-type]


def test_mainline_source_result_accepts_projection_or_failure_and_round_trips() -> None:
    success = MainlineSourceResult(projection=_projection())
    failure = MainlineSourceResult(failure=MainlineSourceFailure.INDEX_NOT_FOUND)

    assert success.scope is MainlineSourceScope.FIXTURE_ONLY
    assert MainlineSourceResult.model_validate_json(success.model_dump_json()) == success
    assert MainlineSourceResult.model_validate_json(failure.model_dump_json()) == failure
