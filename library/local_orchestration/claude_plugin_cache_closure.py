"""Closure checks for the Git object graph retained in a Claude plugin cache."""

from __future__ import annotations

import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from .publication_repository_closure import (
    PublicationCommit,
    PublicationPayload,
    PublicationTreeDifference,
    payload_tree_difference,
)

__all__ = [
    "InstallClosureResult",
    "InstallClosureStatus",
    "check_installed_plugin_cache",
    "inspect_installed_plugin_cache",
    "verify_installed_plugin_cache",
]

_FULL_SHA: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{40}\Z")
_TAG_PREFIX: Final[str] = "refs/tags/plugin-v"
_REMOTE_PREFIX: Final[str] = "refs/remotes/"
_MAIN_REF: Final[str] = "refs/heads/main"
_SENTINELS: Final[tuple[str, ...]] = ("tests/", "doc/", "modules/")
_SEMVER: Final[re.Pattern[str]] = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z"
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )


class InstallClosureStatus(str, Enum):
    VERIFIED = "VERIFIED"
    CLI_UNAVAILABLE = "CLI_UNAVAILABLE"
    MARKETPLACE_CACHE_MISMATCH = "MARKETPLACE_CACHE_MISMATCH"
    PLUGIN_CHECKOUT_MISMATCH = "PLUGIN_CHECKOUT_MISMATCH"
    INSTALLED_REF_SET_INVALID = "INSTALLED_REF_SET_INVALID"
    INSTALLED_HISTORY_INVALID = "INSTALLED_HISTORY_INVALID"
    INSTALLED_TREE_MISMATCH = "INSTALLED_TREE_MISMATCH"
    SENTINEL_REACHABLE = "SENTINEL_REACHABLE"


class InstallClosureResult(_StrictModel):
    """Finite installed-cache result with no command or exception text."""

    status: InstallClosureStatus
    difference: PublicationTreeDifference | None = None
    reachable_refs: tuple[str, ...] = ()
    reachable_commits: tuple[PublicationCommit, ...] = ()


class _GitFailure(Exception):
    pass


def _git(root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=str(root),
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise _GitFailure from error
    if completed.returncode != 0:
        raise _GitFailure
    return completed.stdout.decode("utf-8", errors="replace")


def _valid_installed_ref(name: str) -> bool:
    if name == _MAIN_REF:
        return True
    if name.startswith(_TAG_PREFIX):
        return _SEMVER.fullmatch(name.removeprefix(_TAG_PREFIX)) is not None
    if name.startswith(_REMOTE_PREFIX):
        remainder = name.removeprefix(_REMOTE_PREFIX)
        if "/" not in remainder:
            return False
        remote, branch = remainder.split("/", 1)
        if (
            not remote
            or remote in (".", "..")
            or "\\" in remote
            or any(part in ("", ".", "..") for part in remote.split("/"))
        ):
            return False
        if branch == "main":
            return True
        return branch.startswith("plugin-v") and _SEMVER.fullmatch(
            branch.removeprefix("plugin-v")
        ) is not None
    return False


def _symbolic_remote_head_target(name: str) -> str | None:
    if not name.startswith(_REMOTE_PREFIX):
        return None
    remainder = name.removeprefix(_REMOTE_PREFIX)
    if "/" not in remainder:
        return None
    remote, branch = remainder.split("/", 1)
    if (
        branch != "HEAD"
        or not remote
        or remote in (".", "..")
        or "\\" in remote
        or any(part in ("", ".", "..") for part in remote.split("/"))
    ):
        return None
    return f"{_REMOTE_PREFIX}{remote}/main"


def _loose_symbolic_remote_heads(
    root: Path,
) -> tuple[tuple[str, str], ...] | None:
    try:
        raw_path = _git(root, "rev-parse", "--git-path", "refs/remotes").strip()
    except _GitFailure:
        return None
    if not raw_path:
        return None
    refs_root = Path(raw_path)
    if not refs_root.is_absolute():
        refs_root = Path(root) / refs_root
    if not refs_root.exists():
        return ()
    symbols: list[tuple[str, str]] = []
    try:
        remote_directories = tuple(refs_root.iterdir())
        for remote_directory in remote_directories:
            head = remote_directory / "HEAD"
            if not head.is_file():
                continue
            raw_target = head.read_bytes()
            if (
                not raw_target.startswith(b"ref: ")
                or not raw_target.endswith(b"\n")
                or raw_target.count(b"\n") != 1
            ):
                return None
            try:
                target = raw_target.removeprefix(b"ref: ").removesuffix(b"\n").decode(
                    "ascii"
                )
            except UnicodeDecodeError:
                return None
            symbols.append(
                (
                    f"{_REMOTE_PREFIX}{remote_directory.name}/HEAD",
                    target,
                )
            )
    except (OSError, UnicodeError):
        return None
    return tuple(sorted(symbols))


def _read_refs(root: Path) -> tuple[tuple[str, PublicationCommit], ...] | None:
    try:
        raw = _git(
            root,
            "for-each-ref",
            "--format=%(refname)\t%(objectname)\t%(symref)",
            "refs",
        )
    except _GitFailure:
        return None
    refs: list[tuple[str, PublicationCommit]] = []
    symbolic_targets: dict[str, str] = {}
    symbolic_objects: dict[str, PublicationCommit] = {}
    for line in raw.splitlines():
        fields = line.split("\t")
        if len(fields) != 3:
            return None
        name, object_name, symbolic_target = fields
        if _FULL_SHA.fullmatch(object_name) is None:
            return None
        try:
            commit = PublicationCommit(value=object_name)
        except ValueError:
            return None
        if symbolic_target:
            target = _symbolic_remote_head_target(name)
            if target is None or symbolic_target != target:
                return None
            symbolic_targets[name] = target
            symbolic_objects[name] = commit
        elif _valid_installed_ref(name):
            refs.append((name, commit))
        else:
            return None
    loose_symbols = _loose_symbolic_remote_heads(root)
    if loose_symbols is None:
        return None
    for name, target in loose_symbols:
        expected_target = _symbolic_remote_head_target(name)
        if expected_target is None or target != expected_target:
            return None
        if name in symbolic_targets and symbolic_targets[name] != target:
            return None
        symbolic_targets[name] = target
    direct = dict(refs)
    symbolic: list[tuple[str, str, PublicationCommit]] = []
    for name, target in symbolic_targets.items():
        resolved_commit: PublicationCommit | None = direct.get(target)
        if resolved_commit is None or (
            name in symbolic_objects and symbolic_objects[name] != resolved_commit
        ):
            return None
        symbolic.append((name, target, resolved_commit))
    for name, target, commit in symbolic:
        if direct.get(target) != commit:
            return None
        refs.append((name, commit))
    if len({name for name, _ in refs}) != len(refs):
        return None
    return tuple(sorted(refs))


def _head(root: Path) -> PublicationCommit | None:
    try:
        value = _git(root, "rev-parse", "--verify", "HEAD").strip()
        return PublicationCommit(value=value)
    except (_GitFailure, ValueError):
        return None


def _root_commit(root: Path, commit: PublicationCommit) -> bool:
    try:
        object_type = _git(root, "cat-file", "-t", commit.value).strip()
        parents = _git(root, "rev-list", "--parents", "-n", "1", commit.value).split()
    except _GitFailure:
        return False
    return object_type == "commit" and parents == [commit.value]


def _tree_contains_sentinel(root: Path, commit: PublicationCommit) -> bool | None:
    try:
        raw = _git(root, "ls-tree", "-r", "--name-only", commit.value)
    except _GitFailure:
        return None
    paths = raw.splitlines()
    if any(
        not path
        or path.startswith("/")
        or "\\" in path
        or "\x00" in path
        or any(part in ("", ".", "..") for part in path.split("/"))
        for path in paths
    ):
        return None
    return any(path.startswith(prefix) for path in paths for prefix in _SENTINELS)


def verify_installed_plugin_cache(
    root: Path,
    payload: PublicationPayload,
    expected_head: PublicationCommit | None = None,
) -> InstallClosureResult:
    """Enumerate every installed ref and reachable root without modifying Git."""

    try:
        payload = PublicationPayload.model_validate(payload)
        expected = None if expected_head is None else PublicationCommit.model_validate(expected_head)
    except ValueError:
        return InstallClosureResult(status=InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)

    head = _head(root)
    if head is None:
        return InstallClosureResult(status=InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)
    if expected is not None and head != expected:
        return InstallClosureResult(status=InstallClosureStatus.PLUGIN_CHECKOUT_MISMATCH)
    refs = _read_refs(root)
    if refs is None:
        return InstallClosureResult(status=InstallClosureStatus.INSTALLED_REF_SET_INVALID)
    try:
        symbolic_head = _git(root, "symbolic-ref", "--quiet", "HEAD").strip()
    except _GitFailure:
        symbolic_head = ""
    if symbolic_head and not _valid_installed_ref(symbolic_head):
        return InstallClosureResult(status=InstallClosureStatus.INSTALLED_REF_SET_INVALID)
    if any(
        _symbolic_remote_head_target(name) is not None and target != head
        for name, target in refs
    ):
        return InstallClosureResult(status=InstallClosureStatus.INSTALLED_REF_SET_INVALID)

    targets: list[PublicationCommit] = [head]
    for _name, target in refs:
        if target not in targets:
            targets.append(target)
    for commit in targets:
        sentinel = _tree_contains_sentinel(root, commit)
        if sentinel is None:
            return InstallClosureResult(
                status=InstallClosureStatus.INSTALLED_TREE_MISMATCH,
                reachable_refs=tuple(name for name, _ in refs),
                reachable_commits=tuple(targets),
            )
        if sentinel:
            return InstallClosureResult(
                status=InstallClosureStatus.SENTINEL_REACHABLE,
                reachable_refs=tuple(name for name, _ in refs),
                reachable_commits=tuple(targets),
            )
        if not _root_commit(root, commit):
            return InstallClosureResult(
                status=InstallClosureStatus.INSTALLED_HISTORY_INVALID,
                reachable_refs=tuple(name for name, _ in refs),
                reachable_commits=tuple(targets),
            )
        difference = payload_tree_difference(root, payload, commit)
        if difference is None:
            return InstallClosureResult(
                status=InstallClosureStatus.INSTALLED_TREE_MISMATCH,
                reachable_refs=tuple(name for name, _ in refs),
                reachable_commits=tuple(targets),
            )
        if not difference.is_empty:
            return InstallClosureResult(
                status=InstallClosureStatus.INSTALLED_TREE_MISMATCH,
                difference=difference,
                reachable_refs=tuple(name for name, _ in refs),
                reachable_commits=tuple(targets),
            )
    return InstallClosureResult(
        status=InstallClosureStatus.VERIFIED,
        reachable_refs=tuple(name for name, _ in refs),
        reachable_commits=tuple(targets),
    )


check_installed_plugin_cache = verify_installed_plugin_cache
inspect_installed_plugin_cache = verify_installed_plugin_cache
