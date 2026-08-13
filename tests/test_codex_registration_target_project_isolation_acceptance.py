"""B1-B8 acceptance evidence for target-project repository isolation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from typing import Final, TypeAlias
from unittest.mock import patch

from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_port import CodexRegistrationPortRequest
from library.local_orchestration.contracts import (
    ArtifactDigest,
    InstallRoot,
    InstallationId,
    OwnedRelativePath,
)
from library.local_orchestration.host_contracts import (
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightRequest,
)
from tests.staging.codex_lifecycle_oracle.contracts import OracleCompleted
from tests.staging.codex_lifecycle_oracle.identity_binding import FIXED_STAGING_LOGICAL_ROOT
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.registration_compensation_acceptance import (
    RegistrationCompensationAccepted,
    RegistrationCompensationPhase,
    run_registration_compensation_acceptance,
)
from tests.staging.codex_lifecycle_oracle.registration_success_acceptance import (
    RegistrationSuccessAccepted,
    RegistrationSuccessPhase,
    run_registration_success_acceptance,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


_FileBytes: TypeAlias = tuple[str, bytes]
_RepositoryPair: TypeAlias = tuple[Path, Path]
_SnapshotPair: TypeAlias = tuple["_RepositorySnapshot", "_RepositorySnapshot"]

_SUCCESS_PHASES: Final[tuple[RegistrationSuccessPhase, ...]] = (
    RegistrationSuccessPhase.VERSION,
    RegistrationSuccessPhase.MARKETPLACE_ADD,
    RegistrationSuccessPhase.PLUGIN_ADD,
    RegistrationSuccessPhase.MARKETPLACE_LIST,
    RegistrationSuccessPhase.PLUGIN_LIST,
)
_COMPENSATION_PHASES: Final[tuple[RegistrationCompensationPhase, ...]] = (
    RegistrationCompensationPhase.VERSION,
    RegistrationCompensationPhase.MARKETPLACE_ADD,
    RegistrationCompensationPhase.PLUGIN_ADD,
    RegistrationCompensationPhase.PLUGIN_REMOVE,
    RegistrationCompensationPhase.MARKETPLACE_REMOVE,
    RegistrationCompensationPhase.PLUGIN_LIST,
    RegistrationCompensationPhase.MARKETPLACE_LIST,
    RegistrationCompensationPhase.ABSENCE,
)


@dataclass(frozen=True)
class _RepositorySnapshot:
    """Complete readback of one synthetic repository and its Git metadata."""

    root: str
    git_root: str
    head: str
    tree: str
    index_digest: str
    directories: tuple[str, ...]
    files: tuple[_FileBytes, ...]
    git_metadata: tuple[_FileBytes, ...]
    tracked_files: tuple[_FileBytes, ...]
    tracked_porcelain: str
    ignored_porcelain: str
    lock_paths: tuple[str, ...]
    nested_git_paths: tuple[str, ...]


def _git(repo: Path, arguments: tuple[str, ...], read_only: bool = False) -> str:
    """Run one explicit Git argv with shell execution disabled."""

    prefix = ("git", "--no-optional-locks") if read_only else ("git",)
    result = subprocess.run(
        prefix + arguments,
        cwd=repo,
        capture_output=True,
        check=False,
        encoding="utf-8",
        shell=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"git command failed: {arguments!r}: {result.stderr}")
    return result.stdout


def _request() -> CodexRegistrationPortRequest:
    """Build the logical request; it contains no synthetic repository path."""

    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000e6b0"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value="acceptance-market"),
            plugin=CodexPluginName(value="acceptance-plugin"),
            marketplace_source=OwnedRelativePath(value="marketplaces/acceptance-market"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000e6b0"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value="marketplaces/acceptance-market"),
        installed_locator=OwnedRelativePath(value="plugins/acceptance-plugin"),
        digest=ArtifactDigest(value="a" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value="acceptance-plugin"),
    )


def _ready_environment(
    owner_suffix: str,
) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
    allocator = DisposableEnvironmentAllocator.from_project_runtime()
    provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("the exact project-owned lease was not provisioned")
    oracle = CodexLifecycleOracle(
        CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
    )
    return allocator, provisioned.environment, oracle


def _initialize(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    if type(oracle.initialize(lease)) is not OracleCompleted:
        raise AssertionError("oracle initialization failed")


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    root = lease.root.path
    result = allocator.teardown(lease)
    if result.status is not TeardownStatus.REMOVED or root.exists():
        raise AssertionError("the exact oracle lease did not tear down")


def _create_repository(parent: Path, name: str, label: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, ("-c", "init.defaultBranch=main", "init"))
    (repo / "sentinel.txt").write_bytes(f"{label} text sentinel\n".encode("utf-8"))
    (repo / "sentinel.bin").write_bytes(
        bytes(range(32)) + label.encode("utf-8") + bytes(reversed(range(32)))
    )
    _git(repo, ("add", "--", "sentinel.txt", "sentinel.bin"))
    _git(
        repo,
        (
            "-c",
            "user.name=E6B Synthetic Sentinel",
            "-c",
            "user.email=e6b-synthetic@example.invalid",
            "commit",
            "--quiet",
            "-m",
            f"commit {label} sentinel",
        ),
    )
    return repo


def _create_repository_pair(parent: Path) -> _RepositoryPair:
    repos = (
        _create_repository(parent, "repo-alpha", "alpha"),
        _create_repository(parent, "repo-beta", "beta"),
    )
    if tuple(sorted(path.name for path in parent.iterdir())) != ("repo-alpha", "repo-beta"):
        raise AssertionError("the parent must contain exactly two synthetic repositories")
    return repos


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _filesystem_entries(root: Path) -> tuple[tuple[str, ...], tuple[_FileBytes, ...]]:
    directories: list[str] = []
    files: list[_FileBytes] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            raise AssertionError(f"synthetic repository contains an unexpected symlink: {path}")
        relative = _relative(root, path)
        if path.is_dir():
            directories.append(relative)
        elif path.is_file():
            files.append((relative, path.read_bytes()))
        else:
            raise AssertionError(f"synthetic repository contains an unsupported entry: {path}")
    return tuple(directories), tuple(files)


def _tracked_files(repo: Path) -> tuple[_FileBytes, ...]:
    raw_paths = _git(repo, ("ls-files", "-z"), read_only=True)
    paths = tuple(sorted(path for path in raw_paths.split("\x00") if path))
    return tuple((path, (repo / Path(path)).read_bytes()) for path in paths)


def _git_root(repo: Path) -> Path:
    raw_git_root = Path(_git(repo, ("rev-parse", "--git-dir"), read_only=True).strip())
    return (raw_git_root if raw_git_root.is_absolute() else repo / raw_git_root).resolve(strict=True)


def _index_path(repo: Path) -> Path:
    raw_index = Path(_git(repo, ("rev-parse", "--git-path", "index"), read_only=True).strip())
    return (raw_index if raw_index.is_absolute() else repo / raw_index).resolve(strict=True)


def _snapshot(repo: Path) -> _RepositorySnapshot:
    canonical_root = repo.resolve(strict=True)
    git_root = _git_root(canonical_root)
    directories, files = _filesystem_entries(canonical_root)
    tracked = _tracked_files(canonical_root)
    git_metadata = tuple(record for record in files if record[0] == ".git" or record[0].startswith(".git/"))
    lock_paths = tuple(path for path, _ in files if path.endswith(".lock"))
    nested_git_paths = tuple(
        path for path in (*directories, *(path for path, _ in files)) if Path(path).name == ".git" and path != ".git"
    )
    return _RepositorySnapshot(
        root=str(canonical_root),
        git_root=str(git_root),
        head=_git(canonical_root, ("rev-parse", "HEAD"), read_only=True).strip(),
        tree=_git(canonical_root, ("rev-parse", "HEAD^{tree}"), read_only=True).strip(),
        index_digest=hashlib.sha256(_index_path(canonical_root).read_bytes()).hexdigest(),
        directories=directories,
        files=files,
        git_metadata=git_metadata,
        tracked_files=tracked,
        tracked_porcelain=_git(
            canonical_root,
            ("--no-optional-locks", "status", "--porcelain=v1", "--untracked-files=all"),
            read_only=False,
        ),
        ignored_porcelain=_git(
            canonical_root,
            (
                "--no-optional-locks",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--ignored=matching",
            ),
            read_only=False,
        ),
        lock_paths=lock_paths,
        nested_git_paths=nested_git_paths,
    )


def _snapshot_pair(repos: _RepositoryPair) -> _SnapshotPair:
    return (_snapshot(repos[0]), _snapshot(repos[1]))


def _require_unchanged(expected: _RepositorySnapshot, actual: _RepositorySnapshot) -> None:
    if expected.root != actual.root or expected.git_root != actual.git_root:
        raise AssertionError("canonical repository roots changed")
    if expected.head != actual.head or expected.tree != actual.tree:
        raise AssertionError("HEAD or tree identity changed")
    if expected.index_digest != actual.index_digest:
        raise AssertionError("index identity changed")
    if expected.tracked_files != actual.tracked_files:
        raise AssertionError("tracked paths or bytes changed")
    if expected.tracked_porcelain != actual.tracked_porcelain:
        raise AssertionError("tracked porcelain changed")
    if expected.ignored_porcelain != actual.ignored_porcelain:
        raise AssertionError("ignored porcelain changed")
    if expected.files != actual.files or expected.directories != actual.directories:
        raise AssertionError("repository filesystem snapshot changed")
    if expected.git_metadata != actual.git_metadata:
        raise AssertionError("Git config, refs, index or lock metadata changed")
    if actual.lock_paths or actual.nested_git_paths:
        raise AssertionError("repository contains a lock or nested repository")


def _require_pair_unchanged(expected: _SnapshotPair, actual: _SnapshotPair) -> None:
    if len(expected) != 2 or len(actual) != 2:
        raise AssertionError("the isolation gate must cover exactly two repositories")
    _require_unchanged(expected[0], actual[0])
    _require_unchanged(expected[1], actual[1])


def _assert_request_isolated(
    request: CodexRegistrationPortRequest,
    parent: Path,
    repos: _RepositoryPair,
) -> None:
    serialized = request.model_dump_json()
    for path in (parent, repos[0], repos[1]):
        if str(path) in serialized or str(path).replace("\\", "/") in serialized:
            raise AssertionError("oracle request references a synthetic target repository")


class CodexRegistrationTargetProjectIsolationAcceptanceTests(unittest.TestCase):
    def test_b1_acceptance_module_is_available(self) -> None:
        self.assertTrue(callable(run_registration_success_acceptance))
        self.assertTrue(callable(run_registration_compensation_acceptance))

    def test_b2_parent_owns_exactly_two_committed_text_binary_sentinel_repositories(self) -> None:
        parent_path: Path
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent_path = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent_path)
            self.assertEqual(2, len(repos))
            for repo in repos:
                self.assertEqual(parent_path, repo.parent.resolve(strict=True))
                snapshot = _snapshot(repo)
                self.assertEqual(("sentinel.bin", "sentinel.txt"), tuple(path for path, _ in snapshot.tracked_files))
                self.assertEqual("", snapshot.tracked_porcelain)
                self.assertEqual("", snapshot.ignored_porcelain)
                self.assertEqual((), snapshot.lock_paths)
                self.assertEqual((), snapshot.nested_git_paths)
        self.assertFalse(parent_path.exists())

    def test_b3_snapshots_cover_roots_head_tree_index_tracked_bytes_and_both_porcelain_views(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baselines = _snapshot_pair(repos)
            for baseline in baselines:
                self.assertTrue(Path(baseline.root).is_absolute())
                self.assertTrue(Path(baseline.git_root).is_absolute())
                self.assertEqual(40, len(baseline.head))
                self.assertEqual(40, len(baseline.tree))
                self.assertEqual(64, len(baseline.index_digest))
                self.assertTrue(baseline.tracked_files)
                self.assertEqual("", baseline.tracked_porcelain)
                self.assertEqual("", baseline.ignored_porcelain)

    def test_b4_success_acceptance_preserves_both_external_repository_snapshots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            request = _request()
            _assert_request_isolated(request, parent, repos)
            allocator, lease, oracle = _ready_environment("000000000000e6b4")
            try:
                _initialize(lease, oracle)
                with patch(
                    "tests.staging.codex_lifecycle_oracle.registration_adapter.ntpath.expandvars",
                    return_value=FIXED_STAGING_LOGICAL_ROOT,
                ):
                    result = run_registration_success_acceptance(lease, oracle, request)
                self.assertIs(type(result), RegistrationSuccessAccepted)
                if type(result) is not RegistrationSuccessAccepted:
                    raise AssertionError(f"success acceptance failed: {result}")
                self.assertEqual(_SUCCESS_PHASES, result.metadata.phases)
                _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                _teardown(allocator, lease)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b5_compensation_acceptance_preserves_both_external_repository_snapshots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            request = _request()
            _assert_request_isolated(request, parent, repos)
            allocator, lease, oracle = _ready_environment("000000000000e6b5")
            try:
                _initialize(lease, oracle)
                with (
                    patch(
                        "tests.staging.codex_lifecycle_oracle.registration_adapter.ntpath.expandvars",
                        return_value=FIXED_STAGING_LOGICAL_ROOT,
                    ),
                    patch(
                        "tests.staging.codex_lifecycle_oracle.compensation_adapter.ntpath.expandvars",
                        return_value=FIXED_STAGING_LOGICAL_ROOT,
                    ),
                ):
                    result = run_registration_compensation_acceptance(lease, oracle, request)
                self.assertIs(type(result), RegistrationCompensationAccepted)
                if type(result) is not RegistrationCompensationAccepted:
                    raise AssertionError(f"compensation acceptance failed: {result}")
                self.assertEqual(_COMPENSATION_PHASES, result.phases)
                self.assertTrue(result.replay_blocked)
                _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                _teardown(allocator, lease)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b6_final_readback_has_no_untracked_ignored_lock_config_ref_index_or_nested_repository(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            current = _snapshot_pair(repos)
            _require_pair_unchanged(baseline, current)
            for snapshot in current:
                self.assertEqual("", snapshot.tracked_porcelain)
                self.assertEqual("", snapshot.ignored_porcelain)
                self.assertEqual((), snapshot.lock_paths)
                self.assertEqual((), snapshot.nested_git_paths)

    def test_b7_git_setup_uses_command_scoped_identity_and_exact_temp_teardown(self) -> None:
        parent_path: Path
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent_path = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent_path)
            for repo in repos:
                author = _git(repo, ("show", "-s", "--format=%an <%ae>", "HEAD"), read_only=True).strip()
                self.assertEqual("E6B Synthetic Sentinel <e6b-synthetic@example.invalid>", author)
        self.assertFalse(parent_path.exists())

    def test_b8_reverse_success_bytes_gate_turns_red_and_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            sentinel = repos[0] / "sentinel.txt"
            original = sentinel.read_bytes()
            sentinel.write_bytes(original + b"mutation")
            try:
                with self.assertRaises(AssertionError):
                    _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                sentinel.write_bytes(original)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b8_reverse_success_porcelain_gate_turns_red_and_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            untracked = repos[0] / "temporary-success-untracked.txt"
            untracked.write_bytes(b"untracked mutation")
            try:
                with self.assertRaises(AssertionError):
                    _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                untracked.unlink()
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b8_reverse_compensation_bytes_gate_turns_red_and_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            sentinel = repos[1] / "sentinel.bin"
            original = sentinel.read_bytes()
            sentinel.write_bytes(original + b"compensation mutation")
            try:
                with self.assertRaises(AssertionError):
                    _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                sentinel.write_bytes(original)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b8_reverse_compensation_porcelain_gate_turns_red_and_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            exclude = repos[1] / ".git" / "info" / "exclude"
            original_exclude = exclude.read_bytes()
            ignored = repos[1] / "temporary-compensation-ignored.bin"
            exclude.write_bytes(original_exclude + b"\ntemporary-compensation-ignored.bin\n")
            ignored.write_bytes(b"ignored mutation")
            try:
                with self.assertRaises(AssertionError):
                    _require_pair_unchanged(baseline, _snapshot_pair(repos))
            finally:
                ignored.unlink()
                exclude.write_bytes(original_exclude)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))

    def test_b8_reverse_two_repository_coverage_gate_turns_red_and_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e6b-target-isolation-") as temporary_text:
            parent = Path(temporary_text).resolve(strict=True)
            repos = _create_repository_pair(parent)
            baseline = _snapshot_pair(repos)
            sentinel = repos[1] / "sentinel.txt"
            original = sentinel.read_bytes()
            sentinel.write_bytes(original + b"second-repository mutation")
            try:
                with self.assertRaises(AssertionError):
                    _require_pair_unchanged(baseline, (_snapshot(repos[0]), _snapshot(repos[1])))
            finally:
                sentinel.write_bytes(original)
            _require_pair_unchanged(baseline, _snapshot_pair(repos))


if __name__ == "__main__":
    unittest.main()
