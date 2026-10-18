"""Ticket 30A committed-source fixture and constructor coverage."""

import hashlib
import json
import os
import shutil
import stat
import subprocess
import time
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import TracebackType
from typing import Callable

import pytest
from pydantic import ValidationError

from library.local_orchestration.mainline_source import (
    MainlineSourceFailure,
    MainlineSourceRequest,
    MainlineSourceResult,
    MainlineSourceScope,
    RawGitBlobReadResult,
    TargetRelativePath,
    project_committed_mainline,
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


def _observation(
    source: GitObservationSource = GitObservationSource.WORKTREE_HEAD,
    sha: str = "0123456789abcdef0123456789abcdef01234567",
    repository_key: str = "fixture/project",
    full_ref: str = "refs/heads/main",
) -> GitObservation:
    repository = RemoteRepositoryId(
        provider_kind=RemoteProviderKind.GIT_GENERIC,
        host="fixture.invalid",
        repository_key=repository_key,
        alias="origin",
    )
    return GitObservation(
        observation_id="synthetic-observation",
        source=source,
        repository=repository,
        full_ref=FullBranchRef(value=full_ref),
        sha=sha,
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


_PROJECT_ID = "prj_0123456789abcdef"
_FEATURE = "workflow-governance"
_INDEX_PATH = f"modules/tickets/{_FEATURE}/README.md"
_RAW_SOURCE_SENTINEL = "RAW_MARKDOWN_BODY_SENTINEL_30A"
_REVISION_A = "rev-0123456789abcdef"
_REVISION_B = "rev-fedcba9876543210"


@dataclass(frozen=True)
class _FixtureTicket:
    ticket_ref: str
    ticket_revision: str = _REVISION_A
    status: str = "planned"
    required: bool = True
    depends_on: tuple[str, ...] = ()
    admission_ref: str | None = None
    evidence_refs: tuple[str, ...] = ()
    leaf_ticket_ref: str | None = None
    leaf_ticket_revision: str | None = None
    leaf_status: str | None = None
    leaf_depends_on: tuple[str, ...] | None = None
    index_leaf_ref: str | None = None
    index_leaf_digest: str | None = None


@dataclass
class _FixtureGitRepository:
    root: Path
    owner: str
    test_id: str
    session_started_at: float
    session_ttl: timedelta
    environment: dict[str, str]
    commands: list[tuple[str, ...]]
    closed: bool = False

    def run(self, *arguments: str) -> subprocess.CompletedProcess[bytes]:
        if self.closed or time.monotonic() - self.session_started_at >= self.session_ttl.total_seconds():
            raise RuntimeError("fixture Git session expired")
        command = ("git", *arguments)
        self.commands.append(command)
        try:
            return subprocess.run(
                command,
                cwd=self.root,
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=20,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("fixture Git command exceeded its 20 second timeout") from error

    def require_success(self, *arguments: str) -> bytes:
        result = self.run(*arguments)
        if result.returncode != 0:
            raise RuntimeError("fixture Git setup command failed")
        return result.stdout

    def observation(self) -> GitObservation:
        sha = self.require_success("rev-parse", "HEAD").decode("ascii").strip()
        return _observation(sha=sha)

    def write_files(self, files: dict[str, bytes]) -> None:
        root = self.root.resolve(strict=True)
        for relative_path, payload in files.items():
            path_parts = relative_path.split("/")
            if any(part in ("", ".", "..") for part in path_parts):
                raise RuntimeError("fixture file path is not a safe relative path")
            destination = self.root.joinpath(*path_parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.resolve().is_relative_to(root):
                raise RuntimeError("fixture file escaped its temporary repository")
            destination.write_bytes(payload)

    def commit_files(self, files: dict[str, bytes]) -> GitObservation:
        self.write_files(files)
        self.require_success("add", "--all")
        self.require_success("commit", "--quiet", "-m", "ticket30a isolated fixture")
        return self.observation()


@dataclass
class _FixtureGitBlobPort:
    repository: _FixtureGitRepository
    bound_observation: GitObservation
    read_calls: list[tuple[str, str]]
    unavailable_paths: set[str]

    def read_blob(
        self,
        observation: GitObservation,
        artifact_ref: TargetRelativePath,
    ) -> RawGitBlobReadResult:
        self.read_calls.append((observation.sha, artifact_ref.value))
        if observation != self.bound_observation:
            return RawGitBlobReadResult(status=GitBlobReadStatus.UNAVAILABLE)
        if artifact_ref.value in self.unavailable_paths:
            return RawGitBlobReadResult(status=GitBlobReadStatus.UNAVAILABLE)
        try:
            result = self.repository.run(
                "--no-replace-objects",
                "show",
                f"{observation.sha}:{artifact_ref.value}",
            )
        except RuntimeError:
            return RawGitBlobReadResult(status=GitBlobReadStatus.UNAVAILABLE)
        if result.returncode != 0:
            return RawGitBlobReadResult(status=GitBlobReadStatus.NOT_FOUND)
        return RawGitBlobReadResult(status=GitBlobReadStatus.FOUND, payload=result.stdout)


@pytest.fixture
def fixture_git_repository(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> Iterator[_FixtureGitRepository]:
    root = tmp_path / "ticket30a-fixture-repository"
    root.mkdir()
    fixture_environment = os.environ.copy()
    fixture_environment["GIT_TERMINAL_PROMPT"] = "0"
    fixture_environment["GIT_CONFIG_NOSYSTEM"] = "1"
    repository = _FixtureGitRepository(
        root=root,
        owner="ticket30a-fixture-implementer",
        test_id=request.node.nodeid,
        session_started_at=time.monotonic(),
        session_ttl=timedelta(minutes=5),
        environment=fixture_environment,
        commands=[],
    )
    try:
        repository.require_success("init", "--quiet")
        repository.require_success("config", "user.name", "Ticket 30A Fixture")
        repository.require_success("config", "user.email", "ticket30a-fixture@example.invalid")
        repository.require_success("commit", "--quiet", "--allow-empty", "-m", "fixture bootstrap")
        yield repository
    finally:
        repository.closed = True
        if root.exists():
            resolved_temp = tmp_path.resolve(strict=True)
            resolved_root = root.resolve(strict=True)
            if root.is_symlink() or resolved_root.parent != resolved_temp:
                raise RuntimeError("refusing to remove a fixture repository outside its test temp directory")
            shutil.rmtree(resolved_root, onerror=_remove_readonly)


def _leaf_path(ticket_ref: str) -> str:
    return f"modules/tickets/{_FEATURE}/{ticket_ref}.md"


def _markdown_contract(heading: str, json_text: str, title: str) -> bytes:
    return (
        f"# {title}\n\n{_RAW_SOURCE_SENTINEL}\n\n"
        f"{heading}\n\n```json\n{json_text}\n```\n"
    ).encode("utf-8")


def _leaf_json(ticket: _FixtureTicket) -> str:
    leaf = {
        "schema_id": "mainline-ticket/revision-01",
        "ticket_ref": ticket.ticket_ref if ticket.leaf_ticket_ref is None else ticket.leaf_ticket_ref,
        "ticket_revision": (
            ticket.ticket_revision
            if ticket.leaf_ticket_revision is None
            else ticket.leaf_ticket_revision
        ),
        "status": ticket.status if ticket.leaf_status is None else ticket.leaf_status,
        "depends_on": list(
            ticket.depends_on if ticket.leaf_depends_on is None else ticket.leaf_depends_on
        ),
        "admission_ref": ticket.admission_ref,
        "evidence_refs": list(ticket.evidence_refs),
    }
    return json.dumps(leaf, separators=(",", ":"))


def _index_json(tickets: tuple[_FixtureTicket, ...], leaf_bytes: dict[str, bytes]) -> str:
    index_tickets: list[dict[str, object]] = []
    for ticket in tickets:
        leaf_ref = ticket.index_leaf_ref or _leaf_path(ticket.ticket_ref)
        leaf_payload = leaf_bytes[_leaf_path(ticket.ticket_ref)]
        index_tickets.append(
            {
                "ticket_ref": ticket.ticket_ref,
                "ticket_revision": ticket.ticket_revision,
                "leaf_ref": leaf_ref,
                "leaf_digest": (
                    ticket.index_leaf_digest
                    if ticket.index_leaf_digest is not None
                    else "sha256_" + hashlib.sha256(leaf_payload).hexdigest()
                ),
                "required": ticket.required,
                "status": ticket.status,
                "depends_on": list(ticket.depends_on),
                "admission_ref": ticket.admission_ref,
                "evidence_refs": list(ticket.evidence_refs),
            }
        )
    index: dict[str, object] = {
        "schema_id": "mainline-index/revision-01",
        "project_id": _PROJECT_ID,
        "feature": _FEATURE,
        "mainline_ref": "workflow-mainline",
        "objective_ref": "objective-workflow-governance",
        "owner_ref": "owner-root",
        "handoff_ref": "handoff-ticket-30a",
        "bindings": [
            {
                "kind": "context",
                "identity": "context-workflow-governance",
                "artifact_ref": "CONTEXT.md",
                "revision_sha": "a" * 40,
            },
            {
                "kind": "prd",
                "identity": "PRD-20260805-009",
                "artifact_ref": "PRD.md",
                "revision_sha": "b" * 40,
            },
            {
                "kind": "change",
                "identity": "CHG-20260805-009",
                "artifact_ref": "doc/requirements/REQ-20260805-009.md",
                "revision_sha": "c" * 40,
            },
            {
                "kind": "spec",
                "identity": "spec-workflow-governance",
                "artifact_ref": "modules/spec/workflow-governance.md",
                "revision_sha": "d" * 40,
            },
        ],
        "tickets": index_tickets,
    }
    return json.dumps(index, separators=(",", ":"))


def _fixture_source_files(
    tickets: tuple[_FixtureTicket, ...],
    *,
    leaf_json_transform: Callable[[str], str] | None = None,
    index_json_transform: Callable[[str], str] | None = None,
    leaf_payload_transform: Callable[[str, bytes], bytes] | None = None,
    index_payload_override: bytes | None = None,
    index_suffix: bytes = b"",
    leaf_suffix: bytes = b"",
) -> dict[str, bytes]:
    leaf_bytes: dict[str, bytes] = {}
    for ticket in tickets:
        leaf_json = _leaf_json(ticket)
        if leaf_json_transform is not None:
            leaf_json = leaf_json_transform(leaf_json)
        leaf_payload = _markdown_contract(
            "## Mainline ticket contract",
            leaf_json,
            f"Ticket {ticket.ticket_ref}",
        ) + leaf_suffix
        if leaf_payload_transform is not None:
            leaf_payload = leaf_payload_transform(_leaf_path(ticket.ticket_ref), leaf_payload)
        leaf_bytes[_leaf_path(ticket.ticket_ref)] = leaf_payload

    index_json = _index_json(tickets, leaf_bytes)
    if index_json_transform is not None:
        index_json = index_json_transform(index_json)
    index_payload = (
        index_payload_override
        if index_payload_override is not None
        else _markdown_contract("## Mainline source contract", index_json, "Workflow ticket status")
        + index_suffix
    )
    files = {_INDEX_PATH: index_payload}
    files.update(leaf_bytes)
    return files


def _port(repository: _FixtureGitRepository, observation: GitObservation) -> _FixtureGitBlobPort:
    return _FixtureGitBlobPort(
        repository=repository,
        bound_observation=observation,
        read_calls=[],
        unavailable_paths=set(),
    )


def _request(observation: GitObservation) -> MainlineSourceRequest:
    return MainlineSourceRequest(
        project_id=_PROJECT_ID,
        feature=_FEATURE,
        observation=observation,
    )


def _assert_failure(result: MainlineSourceResult, failure: MainlineSourceFailure) -> None:
    assert result.scope is MainlineSourceScope.FIXTURE_ONLY
    assert result.projection is None
    assert result.failure is failure


def _remove_readonly(
    function: Callable[..., object],
    path: str,
    error: tuple[type[BaseException], BaseException, TracebackType | None],
) -> None:
    _ = error
    os.chmod(path, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    function(path)


def _rewrite_json_fence(markdown: bytes, transform: Callable[[str], str]) -> bytes:
    text = markdown.decode("utf-8")
    opening = "```json\n"
    start = text.index(opening) + len(opening)
    end = text.index("\n```", start)
    json_text = text[start:end]
    return (text[:start] + transform(json_text) + text[end:]).encode("utf-8")


def _duplicate_json_key(json_text: str) -> str:
    return json_text[:-1] + ',"schema_id":"mainline-index/revision-01"}'


def test_committed_mainline_keeps_precise_wait_and_open_required_work_after_independent_completion(
    fixture_git_repository: _FixtureGitRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ticket_a = _FixtureTicket("ticket-alpha", status="waiting")
    ticket_b = _FixtureTicket("ticket-beta")
    ticket_c = _FixtureTicket("ticket-gamma", depends_on=("ticket-alpha",))
    initial_files = _fixture_source_files((ticket_a, ticket_b, ticket_c))
    initial_observation = fixture_git_repository.commit_files(initial_files)
    initial_port = _port(fixture_git_repository, initial_observation)

    initial_result = project_committed_mainline(_request(initial_observation), initial_port)

    assert initial_result.failure is None
    assert initial_result.projection is not None
    assert initial_result.projection.ready_for_recheck == ("ticket-beta",)
    assert initial_result.projection.waiting == ("ticket-alpha", "ticket-gamma")
    assert initial_result.projection.incomplete_required == (
        "ticket-alpha",
        "ticket-beta",
        "ticket-gamma",
    )
    assert not initial_result.projection.closure_candidate
    assert Counter(initial_port.read_calls) == Counter(
        {
            (initial_observation.sha, _INDEX_PATH): 1,
            (initial_observation.sha, _leaf_path("ticket-alpha")): 1,
            (initial_observation.sha, _leaf_path("ticket-beta")): 1,
            (initial_observation.sha, _leaf_path("ticket-gamma")): 1,
        }
    )
    assert _RAW_SOURCE_SENTINEL not in repr(initial_result)
    assert _RAW_SOURCE_SENTINEL not in caplog.text
    assert fixture_git_repository.require_success("remote", "-v") == b""

    completed_b = _FixtureTicket(
        "ticket-beta",
        ticket_revision=_REVISION_B,
        status="completed",
        admission_ref="admission-beta",
        evidence_refs=("evidence-beta",),
    )
    updated_files = _fixture_source_files((ticket_a, completed_b, ticket_c))
    fixture_git_repository.write_files(updated_files)

    working_copy_result = project_committed_mainline(
        _request(initial_observation),
        _port(fixture_git_repository, initial_observation),
    )
    assert working_copy_result.projection == initial_result.projection

    updated_observation = fixture_git_repository.commit_files(updated_files)
    old_commit_result = project_committed_mainline(
        _request(initial_observation),
        _port(fixture_git_repository, initial_observation),
    )
    updated_port = _port(fixture_git_repository, updated_observation)
    updated_result = project_committed_mainline(_request(updated_observation), updated_port)

    assert old_commit_result.projection == initial_result.projection
    assert updated_result.failure is None
    assert updated_result.projection is not None
    assert updated_result.projection.ready_for_recheck == ()
    assert updated_result.projection.waiting == ("ticket-alpha", "ticket-gamma")
    assert updated_result.projection.incomplete_required == ("ticket-alpha", "ticket-gamma")
    assert not updated_result.projection.closure_candidate
    assert updated_result.projection.source_revision == f"rev-{updated_observation.sha}"
    assert Counter(updated_port.read_calls) == Counter(
        {
            (updated_observation.sha, _INDEX_PATH): 1,
            (updated_observation.sha, _leaf_path("ticket-alpha")): 1,
            (updated_observation.sha, _leaf_path("ticket-beta")): 1,
            (updated_observation.sha, _leaf_path("ticket-gamma")): 1,
        }
    )


def test_missing_index_returns_one_finite_failure_without_leaf_reads(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    observation = fixture_git_repository.observation()
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_NOT_FOUND)
    assert port.read_calls == [(observation.sha, _INDEX_PATH)]


def test_unavailable_index_read_returns_one_finite_failure(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    observation = fixture_git_repository.commit_files(
        _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    )
    port = _port(fixture_git_repository, observation)
    port.unavailable_paths.add(_INDEX_PATH)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_READ_UNAVAILABLE)
    assert port.read_calls == [(observation.sha, _INDEX_PATH)]


@pytest.mark.parametrize(
    "case",
    ("duplicate-key", "duplicate-fence", "duplicate-heading", "unknown-field", "missing-field", "bad-status", "invalid-utf8"),
)
def test_malformed_index_fails_closed_before_reading_leaves(
    fixture_git_repository: _FixtureGitRepository,
    case: str,
) -> None:
    files = _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    if case == "duplicate-key":
        files[_INDEX_PATH] = _rewrite_json_fence(files[_INDEX_PATH], _duplicate_json_key)
    elif case == "duplicate-fence":
        files[_INDEX_PATH] += b"\n## Extra\n\n```json\n{}\n```\n"
    elif case == "duplicate-heading":
        files[_INDEX_PATH] += b"\n## Mainline source contract\n"
    elif case == "unknown-field":
        files[_INDEX_PATH] = _rewrite_json_fence(
            files[_INDEX_PATH],
            lambda value: value[:-1] + ',"unknown_field":true}',
        )
    elif case == "missing-field":
        files[_INDEX_PATH] = _rewrite_json_fence(
            files[_INDEX_PATH],
            lambda value: value.replace('"owner_ref":"owner-root",', "", 1),
        )
    elif case == "bad-status":
        files[_INDEX_PATH] = _rewrite_json_fence(
            files[_INDEX_PATH],
            lambda value: value.replace('"status":"planned"', '"status":"unknown"', 1),
        )
    else:
        files[_INDEX_PATH] = b"\xff\xfeinvalid UTF-8"

    observation = fixture_git_repository.commit_files(files)
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_SCHEMA_INVALID)
    assert port.read_calls == [(observation.sha, _INDEX_PATH)]


@pytest.mark.parametrize(
    "case",
    ("duplicate-key", "duplicate-fence", "unknown-field", "missing-field", "invalid-utf8"),
)
def test_malformed_committed_leaf_fails_closed_without_projection(
    fixture_git_repository: _FixtureGitRepository,
    case: str,
) -> None:
    def add_unknown_field(value: str) -> str:
        return value[:-1] + ',"unknown_field":true}'

    def remove_required_field(value: str) -> str:
        return value.replace('"status":"planned",', "", 1)

    def append_duplicate_fence(path: str, payload: bytes) -> bytes:
        _ = path
        return payload + b"\n## Mainline ticket contract\n\n```json\n{}\n```\n"

    def invalid_utf8(path: str, payload: bytes) -> bytes:
        _ = path
        return b"\xff" + payload

    if case == "duplicate-key":
        files = _fixture_source_files(
            (_FixtureTicket("ticket-alpha"),),
            leaf_json_transform=_duplicate_json_key,
        )
    elif case == "unknown-field":
        files = _fixture_source_files(
            (_FixtureTicket("ticket-alpha"),),
            leaf_json_transform=add_unknown_field,
        )
    elif case == "missing-field":
        files = _fixture_source_files(
            (_FixtureTicket("ticket-alpha"),),
            leaf_json_transform=remove_required_field,
        )
    elif case == "duplicate-fence":
        files = _fixture_source_files(
            (_FixtureTicket("ticket-alpha"),),
            leaf_payload_transform=append_duplicate_fence,
        )
    else:
        files = _fixture_source_files(
            (_FixtureTicket("ticket-alpha"),),
            leaf_payload_transform=invalid_utf8,
        )

    observation = fixture_git_repository.commit_files(files)
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.PROJECTION_INVALID)
    assert Counter(port.read_calls) == Counter(
        {
            (observation.sha, _INDEX_PATH): 1,
            (observation.sha, _leaf_path("ticket-alpha")): 1,
        }
    )


@pytest.mark.parametrize(
    "record,failure",
    (
        (
            _FixtureTicket("ticket-alpha", index_leaf_digest="sha256_" + "0" * 64),
            MainlineSourceFailure.LEAF_DIGEST_MISMATCH,
        ),
        (
            _FixtureTicket("ticket-alpha", leaf_ticket_revision=_REVISION_B),
            MainlineSourceFailure.INDEX_BINDING_MISMATCH,
        ),
        (
            _FixtureTicket("ticket-alpha", leaf_status="waiting"),
            MainlineSourceFailure.INDEX_BINDING_MISMATCH,
        ),
        (
            _FixtureTicket("ticket-alpha", leaf_depends_on=("ticket-other",)),
            MainlineSourceFailure.INDEX_BINDING_MISMATCH,
        ),
    ),
)
def test_leaf_digest_and_index_leaf_bindings_return_finite_failures(
    fixture_git_repository: _FixtureGitRepository,
    record: _FixtureTicket,
    failure: MainlineSourceFailure,
) -> None:
    observation = fixture_git_repository.commit_files(_fixture_source_files((record,)))
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, failure)
    assert Counter(port.read_calls) == Counter(
        {
            (observation.sha, _INDEX_PATH): 1,
            (observation.sha, _leaf_path("ticket-alpha")): 1,
        }
    )


def test_missing_leaf_returns_finite_failure_and_does_not_retry(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    record = _FixtureTicket(
        "ticket-alpha",
        index_leaf_ref=f"modules/tickets/{_FEATURE}/missing-ticket.md",
    )
    observation = fixture_git_repository.commit_files(_fixture_source_files((record,)))
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.LEAF_NOT_FOUND)
    assert port.read_calls == [
        (observation.sha, _INDEX_PATH),
        (observation.sha, f"modules/tickets/{_FEATURE}/missing-ticket.md"),
    ]


def test_unavailable_leaf_returns_finite_failure_without_cache_fallback(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    observation = fixture_git_repository.commit_files(
        _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    )
    leaf_ref = _leaf_path("ticket-alpha")
    port = _port(fixture_git_repository, observation)
    port.unavailable_paths.add(leaf_ref)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.LEAF_READ_UNAVAILABLE)
    assert port.read_calls == [
        (observation.sha, _INDEX_PATH),
        (observation.sha, leaf_ref),
    ]


@pytest.mark.parametrize(
    "leaf_ref",
    (
        "modules/tickets/other-feature/ticket-alpha.md",
        f"modules/tickets/{_FEATURE}/../outside.md",
        f"modules/tickets/{_FEATURE}/not-markdown.txt",
    ),
)
def test_cross_feature_traversal_and_non_markdown_leaf_refs_are_rejected_before_read(
    fixture_git_repository: _FixtureGitRepository,
    leaf_ref: str,
) -> None:
    record = _FixtureTicket("ticket-alpha", index_leaf_ref=leaf_ref)
    observation = fixture_git_repository.commit_files(_fixture_source_files((record,)))
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_SCHEMA_INVALID)
    assert port.read_calls == [(observation.sha, _INDEX_PATH)]


@pytest.mark.parametrize(
    "records",
    (
        (_FixtureTicket("ticket-alpha"), _FixtureTicket("ticket-alpha")),
        (
            _FixtureTicket("ticket-alpha"),
            _FixtureTicket(
                "ticket-beta",
                index_leaf_ref=_leaf_path("ticket-alpha"),
            ),
        ),
    ),
)
def test_duplicate_ticket_or_leaf_references_are_rejected_before_leaf_reads(
    fixture_git_repository: _FixtureGitRepository,
    records: tuple[_FixtureTicket, ...],
) -> None:
    observation = fixture_git_repository.commit_files(_fixture_source_files(records))
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_SCHEMA_INVALID)
    assert port.read_calls == [(observation.sha, _INDEX_PATH)]


@pytest.mark.parametrize(
    "records",
    (
        (_FixtureTicket("ticket-alpha", depends_on=("ticket-unknown",)),),
        (_FixtureTicket("ticket-alpha", depends_on=("ticket-alpha", "ticket-alpha")),),
        (
            _FixtureTicket("ticket-alpha", depends_on=("ticket-beta",)),
            _FixtureTicket("ticket-beta", depends_on=("ticket-alpha",)),
        ),
    ),
)
def test_unknown_or_cyclic_dependencies_return_no_projection(
    fixture_git_repository: _FixtureGitRepository,
    records: tuple[_FixtureTicket, ...],
) -> None:
    observation = fixture_git_repository.commit_files(_fixture_source_files(records))
    port = _port(fixture_git_repository, observation)

    result = project_committed_mainline(_request(observation), port)

    _assert_failure(result, MainlineSourceFailure.PROJECTION_INVALID)
    assert len(port.read_calls) == len(records) + 1
    assert all(sha == observation.sha for sha, _ in port.read_calls)
    assert len(Counter(port.read_calls)) == len(port.read_calls)


@pytest.mark.parametrize("forged_field", ("sha", "repository", "ref"))
def test_caller_observation_must_match_the_fixture_port_binding(
    fixture_git_repository: _FixtureGitRepository,
    forged_field: str,
) -> None:
    observation = fixture_git_repository.commit_files(
        _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    )
    port = _port(fixture_git_repository, observation)
    if forged_field == "sha":
        caller_asserted_observation = _observation(
            sha="fedcba9876543210fedcba9876543210fedcba98"
        )
    elif forged_field == "repository":
        caller_asserted_observation = _observation(
            sha=observation.sha,
            repository_key="caller/selected-project",
        )
    else:
        caller_asserted_observation = _observation(
            sha=observation.sha,
            full_ref="refs/heads/caller-selected-branch",
        )

    result = project_committed_mainline(_request(caller_asserted_observation), port)

    _assert_failure(result, MainlineSourceFailure.INDEX_READ_UNAVAILABLE)
    assert port.read_calls == [(caller_asserted_observation.sha, _INDEX_PATH)]
    assert not any("show" in command for command in fixture_git_repository.commands)


@pytest.mark.parametrize("mismatch", ("request-project", "request-feature", "index-project", "index-feature"))
def test_caller_or_index_project_metadata_cannot_override_the_source_binding(
    fixture_git_repository: _FixtureGitRepository,
    mismatch: str,
) -> None:
    files = _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    project_id = _PROJECT_ID
    feature = _FEATURE
    if mismatch == "request-project":
        project_id = "prj_fedcba9876543210"
    elif mismatch == "request-feature":
        feature = "other-feature"
        files[f"modules/tickets/{feature}/README.md"] = files[_INDEX_PATH]
    elif mismatch == "index-project":
        files[_INDEX_PATH] = _rewrite_json_fence(
            files[_INDEX_PATH],
            lambda value: value.replace(_PROJECT_ID, "prj_fedcba9876543210", 1),
        )
    else:
        files[_INDEX_PATH] = _rewrite_json_fence(
            files[_INDEX_PATH],
            lambda value: value.replace('"feature":"workflow-governance"', '"feature":"other-feature"', 1),
        )

    observation = fixture_git_repository.commit_files(files)
    port = _port(fixture_git_repository, observation)
    request = MainlineSourceRequest(
        project_id=project_id,
        feature=feature,
        observation=observation,
    )

    result = project_committed_mainline(request, port)

    _assert_failure(result, MainlineSourceFailure.INDEX_BINDING_MISMATCH)
    assert port.read_calls == [(observation.sha, f"modules/tickets/{feature}/README.md")]


def test_source_result_and_imports_do_not_expose_effect_capabilities(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    import ast

    from library.local_orchestration import mainline_source

    observation = fixture_git_repository.commit_files(
        _fixture_source_files((_FixtureTicket("ticket-alpha"),))
    )
    result = project_committed_mainline(
        _request(observation),
        _port(fixture_git_repository, observation),
    )
    source_path = Path(mainline_source.__file__ or "")
    module_tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden_modules = {
        "library.local_orchestration.dispatch_authority",
        "library.local_orchestration.dispatch_session",
        "library.local_orchestration.live_dispatch_metadata_store",
        "library.workflow_router.telemetry",
    }
    forbidden_names = {
        "admit_dispatch",
        "spawn_agent",
        "spawn_worker",
        "issue_receipt",
        "TicketReceiptStorePort",
        "JsonlReceiptUsageEvidenceStore",
    }

    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    called_names: set[str] = set()
    for node in ast.walk(module_tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Call):
            function: ast.expr = node.func
            while isinstance(function, ast.Attribute):
                called_names.add(function.attr)
                function = function.value
            if isinstance(function, ast.Name):
                called_names.add(function.id)

    assert imported_modules.isdisjoint(forbidden_modules)
    assert imported_names.isdisjoint(forbidden_names)
    assert called_names.isdisjoint(forbidden_names)
    assert _RAW_SOURCE_SENTINEL not in repr(result)
    assert result.scope is MainlineSourceScope.FIXTURE_ONLY


def test_fixture_metadata_is_bounded_and_temp_repository_has_no_remote(
    fixture_git_repository: _FixtureGitRepository,
) -> None:
    assert fixture_git_repository.owner == "ticket30a-fixture-implementer"
    assert fixture_git_repository.test_id
    assert fixture_git_repository.session_ttl == timedelta(minutes=5)
    assert fixture_git_repository.require_success("remote", "-v") == b""
