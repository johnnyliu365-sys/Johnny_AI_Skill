"""Fail-closed closure checks for the payload-only publication repository.

The publication repository is intentionally treated as an object graph rather
than as a checkout.  Every admitted ref is read, every target is required to
be a parentless commit, and every tree is compared path-for-path and blob-for-
blob with one typed payload declaration.
"""

from __future__ import annotations

import json
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Final, Mapping, Self
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from . import plugin_publication
from .plugin_publication import declared_blob_ids, load_payload_declaration
from .runtime_contracts import CorrelationId

__all__ = [
    "InstallPayload",
    "PublicationClosureResult",
    "PublicationClosureStatus",
    "PublicationCommit",
    "PublicationGeneratedPinCarrier",
    "PublicationReleaseDeclaration",
    "PublicationReleaseDeclarationRead",
    "PublicationPayload",
    "PublicationPromotionRequest",
    "PublicationRef",
    "PublicationRefKind",
    "PublicationRemoteSnapshot",
    "PublicationRepositoryRef",
    "PublicationTreeDifference",
    "PublicationVersion",
    "check_publication_repository",
    "inspect_publication_repository",
    "payload_from_manifest",
    "read_publication_release_declaration",
    "verify_publication_repository",
]

_FULL_SHA: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{40}\Z")
_SEMVER: Final[re.Pattern[str]] = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z"
)
_TAG_PREFIX: Final[str] = "refs/tags/plugin-v"
_MAIN_REF: Final[str] = "refs/heads/main"
_PLUGIN_MANIFEST_PATH: Final[str] = ".claude-plugin/plugin.json"
_MARKETPLACE_MANIFEST_PATH: Final[str] = ".claude-plugin/marketplace.json"
_UNPINNABLE_SHA: Final[str] = "0" * 40
_FORBIDDEN_PAYLOAD_PREFIXES: Final[tuple[tuple[str, ...], ...]] = (
    ("tests",),
    ("doc",),
    ("modules", "tickets"),
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )


class PublicationRepositoryRef(_StrictModel):
    """The publication repository identity, never inferred from a checkout."""

    value: str = Field(min_length=1, max_length=2048)

    @field_validator("value")
    @classmethod
    def _https_git_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or not parsed.path
            or any(ch.isspace() for ch in value)
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("publication repository must be an HTTPS URL")
        return value


class PublicationCommit(_StrictModel):
    """A complete lower-case Git commit object id."""

    value: str = Field(min_length=40, max_length=40)

    @field_validator("value")
    @classmethod
    def _full_sha(cls, value: str) -> str:
        if _FULL_SHA.fullmatch(value) is None:
            raise ValueError("publication commit must be a full lower-case SHA")
        return value


class PublicationVersion(_StrictModel):
    """A release semantic version used by the immutable publication tag."""

    value: str = Field(min_length=5, max_length=128)

    @field_validator("value")
    @classmethod
    def _semver(cls, value: str) -> str:
        if _SEMVER.fullmatch(value) is None:
            raise ValueError("publication version must be semantic versioning")
        return value

    @property
    def tag_name(self) -> str:
        return f"plugin-v{self.value}"

    @property
    def ref_name(self) -> str:
        return f"{_TAG_PREFIX}{self.value}"


class PublicationRefKind(str, Enum):
    MAIN = "MAIN"
    RELEASE_TAG = "RELEASE_TAG"


class PublicationRef(_StrictModel):
    """One admitted publication ref and the commit it resolves to."""

    kind: PublicationRefKind
    name: str = Field(min_length=1, max_length=512)
    target: PublicationCommit

    @model_validator(mode="after")
    def _matches_kind(self) -> Self:
        if self.kind is PublicationRefKind.MAIN and self.name != _MAIN_REF:
            raise ValueError("MAIN must be refs/heads/main")
        if self.kind is PublicationRefKind.RELEASE_TAG:
            if not self.name.startswith(_TAG_PREFIX) or _SEMVER.fullmatch(
                self.name.removeprefix(_TAG_PREFIX)
            ) is None:
                raise ValueError("release tag must be plugin-v<semver>")
        return self


def _relative_path(value: str) -> str:
    if (
        not value
        or value.startswith("/")
        or "\\" in value
        or "\x00" in value
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise ValueError("payload paths must be clean repository-relative POSIX paths")
    return value


class PublicationTreeDifference(_StrictModel):
    """Exact path classes that differ between a tree and the declared payload."""

    missing: tuple[str, ...] = ()
    extra: tuple[str, ...] = ()
    content_mismatch: tuple[str, ...] = ()

    @field_validator("missing", "extra", "content_mismatch")
    @classmethod
    def _paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted(values))
        if len(set(normalized)) != len(normalized):
            raise ValueError("difference paths must be unique")
        return tuple(_relative_path(value) for value in normalized)

    @property
    def is_empty(self) -> bool:
        return not (self.missing or self.extra or self.content_mismatch)


class PublicationPayload(_StrictModel):
    """Validated payload paths and the blob ids expected at those paths."""

    paths: tuple[str, ...] = Field(min_length=1)
    blob_ids: tuple[tuple[str, str], ...] = Field(min_length=1)

    @field_validator("paths")
    @classmethod
    def _paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted(values))
        if len(set(normalized)) != len(normalized):
            raise ValueError("payload paths must be unique")
        return tuple(_relative_path(value) for value in normalized)

    @field_validator("blob_ids")
    @classmethod
    def _blobs(cls, values: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
        normalized = tuple(sorted(values))
        if len(set(path for path, _ in normalized)) != len(normalized):
            raise ValueError("payload blob paths must be unique")
        for path, blob in normalized:
            _relative_path(path)
            if _FULL_SHA.fullmatch(blob) is None:
                raise ValueError("payload blob ids must be complete lower-case SHA values")
        return normalized

    @model_validator(mode="after")
    def _paths_match_blobs(self) -> Self:
        if self.paths != tuple(path for path, _ in self.blob_ids):
            raise ValueError("payload paths and blob ids must describe the same files")
        return self


InstallPayload = PublicationPayload


class PublicationGeneratedPinCarrier(_StrictModel):
    """Typed state of the canonical generated marketplace pin carrier."""

    pin_carrier: str = Field(min_length=1, max_length=512)
    recorded_sha: str = Field(min_length=40, max_length=40)

    @field_validator("pin_carrier")
    @classmethod
    def _path(cls, value: str) -> str:
        return _relative_path(value)

    @field_validator("recorded_sha")
    @classmethod
    def _placeholder(cls, value: str) -> str:
        if value != _UNPINNABLE_SHA:
            raise ValueError("generated carrier must record the unpinnable SHA")
        return value


class PublicationReleaseDeclaration(_StrictModel):
    """The immutable declaration read from one release-tag target."""

    version: PublicationVersion
    paths: tuple[str, ...] = Field(min_length=1)
    carrier: PublicationGeneratedPinCarrier

    @field_validator("paths")
    @classmethod
    def _paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted(values))
        if len(set(normalized)) != len(normalized):
            raise ValueError("release declaration paths must be unique")
        return tuple(_relative_path(value) for value in normalized)

    @model_validator(mode="after")
    def _generated_carrier_is_declared(self) -> Self:
        if self.carrier.pin_carrier != _MARKETPLACE_MANIFEST_PATH:
            raise ValueError("release declaration carrier must be marketplace.json")
        if self.carrier.pin_carrier not in self.paths:
            raise ValueError("release declaration carrier must be declared")
        return self


class _TargetPayloadDeclaration(_StrictModel):
    trees: tuple[str, ...] = Field(min_length=1)
    files: tuple[str, ...] = Field(min_length=1)
    excluded_segments: tuple[str, ...] = ()
    excluded_suffixes: tuple[str, ...] = ()

    @field_validator("trees", "files")
    @classmethod
    def _entries(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted(values))
        if len(set(normalized)) != len(normalized):
            raise ValueError("payload entries must be unique")
        for value in normalized:
            if value != value.strip():
                raise ValueError("payload entries must not be whitespace padded")
            _relative_path(value)
            if any(
                tuple(value.split("/"))[: len(prefix)] == prefix
                for prefix in _FORBIDDEN_PAYLOAD_PREFIXES
            ):
                raise ValueError("payload entry is forbidden")
        return normalized

    @field_validator("excluded_segments", "excluded_suffixes")
    @classmethod
    def _string_lists(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(values)
        if len(set(normalized)) != len(normalized):
            raise ValueError("payload exclusions must be unique")
        return normalized

    @model_validator(mode="after")
    def _trees_do_not_overlap(self) -> Self:
        tree_parts = tuple(tuple(tree.split("/")) for tree in self.trees)
        for index, left in enumerate(tree_parts):
            for right in tree_parts[index + 1 :]:
                if left[: len(right)] == right or right[: len(left)] == left:
                    raise ValueError("payload trees must not overlap by prefix")
        return self


class PublicationRemoteSnapshot(_StrictModel):
    """Normalized readback of the publication repository's allowed refs."""

    repository: PublicationRepositoryRef
    default_branch: str = Field(min_length=1, max_length=512)
    refs: tuple[PublicationRef, ...] = ()

    @model_validator(mode="after")
    def _unique_refs(self) -> Self:
        names = tuple(ref.name for ref in self.refs)
        if len(set(names)) != len(names):
            raise ValueError("remote refs must be unique")
        return self


class PublicationClosureStatus(str, Enum):
    VERIFIED = "VERIFIED"
    REMOTE_UNREACHABLE = "REMOTE_UNREACHABLE"
    REMOTE_NOT_EMPTY = "REMOTE_NOT_EMPTY"
    DEFAULT_BRANCH_INVALID = "DEFAULT_BRANCH_INVALID"
    REF_SET_INVALID = "REF_SET_INVALID"
    MAIN_MISSING = "MAIN_MISSING"
    TAG_COLLISION = "TAG_COLLISION"
    STALE_MAIN = "STALE_MAIN"
    COMMIT_NOT_ROOT = "COMMIT_NOT_ROOT"
    TREE_MISMATCH = "TREE_MISMATCH"
    PIN_MISMATCH = "PIN_MISMATCH"
    RELEASE_DECLARATION_INVALID = "RELEASE_DECLARATION_INVALID"
    RELEASE_VERSION_MISMATCH = "RELEASE_VERSION_MISMATCH"
    READBACK_MISMATCH = "READBACK_MISMATCH"


class PublicationPromotionRequest(_StrictModel):
    """Typed metadata consumed by the later compare-and-swap ticket."""

    repository: PublicationRepositoryRef
    expected_main: PublicationCommit | None = None
    candidate: PublicationCommit
    version: PublicationVersion
    correlation: CorrelationId


class PublicationClosureResult(_StrictModel):
    """Finite closure result; no Git exception text is part of the domain."""

    status: PublicationClosureStatus
    snapshot: PublicationRemoteSnapshot | None = None
    difference: PublicationTreeDifference | None = None

    @model_validator(mode="after")
    def _verified_has_empty_difference(self) -> Self:
        if self.status is PublicationClosureStatus.VERIFIED:
            if self.snapshot is None or self.difference is None or not self.difference.is_empty:
                raise ValueError("VERIFIED requires a complete empty closure difference")
        return self


class _GitReadFailure(Exception):
    pass


class _SnapshotRead(_StrictModel):
    snapshot: PublicationRemoteSnapshot | None = None
    failure: PublicationClosureStatus | None = None


class PublicationReleaseDeclarationRead(_StrictModel):
    """Typed target-commit release declaration read at the Git boundary."""

    declaration: PublicationReleaseDeclaration | None = None
    difference: PublicationTreeDifference | None = None
    failure: PublicationClosureStatus | None = None

    @model_validator(mode="after")
    def _complete_success_or_failure(self) -> Self:
        if self.failure is None:
            if self.declaration is None or self.difference is None:
                raise ValueError("successful declaration read requires declaration and difference")
        elif self.declaration is not None or self.difference is not None:
            raise ValueError("failed declaration read cannot carry success evidence")
        return self


def _git(root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=str(root),
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise _GitReadFailure from error
    if completed.returncode != 0:
        raise _GitReadFailure
    return completed.stdout.decode("utf-8", errors="replace")


def _json_object(text: str) -> dict[str, object] | None:
    try:
        parsed: object = json.loads(text)
    except (TypeError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    result: dict[str, object] = {}
    for key, value in parsed.items():
        if not isinstance(key, str):
            return None
        result[key] = value
    return result


def _string_list(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return tuple(item for item in value if isinstance(item, str))


def _target_payload_declaration(document: Mapping[str, object]) -> _TargetPayloadDeclaration | None:
    payload_value = document.get("payload")
    if not isinstance(payload_value, dict):
        return None
    trees = _string_list(payload_value.get("trees"))
    files = _string_list(payload_value.get("files"))
    excluded_segments = _string_list(payload_value.get("excludedSegments", []))
    excluded_suffixes = _string_list(payload_value.get("excludedSuffixes", []))
    if trees is None or files is None or excluded_segments is None or excluded_suffixes is None:
        return None
    try:
        return _TargetPayloadDeclaration(
            trees=trees,
            files=files,
            excluded_segments=excluded_segments,
            excluded_suffixes=excluded_suffixes,
        )
    except ValueError:
        return None


def _target_path_is_declared(
    path: str, declaration: _TargetPayloadDeclaration
) -> bool:
    parts = tuple(path.split("/"))
    if any(part in declaration.excluded_segments for part in parts):
        return False
    if any(path.endswith(suffix) for suffix in declaration.excluded_suffixes):
        return False
    return any(
        parts[: len(tuple(tree.split("/")))] == tuple(tree.split("/"))
        for tree in declaration.trees
    )


def _target_payload_paths(
    actual: tuple[tuple[str, str], ...], declaration: _TargetPayloadDeclaration
) -> tuple[tuple[str, ...], PublicationTreeDifference]:
    actual_paths = {path for path, _ in actual}
    expected: set[str] = set(declaration.files)
    missing: set[str] = {path for path in declaration.files if path not in actual_paths}
    for tree in declaration.trees:
        prefix = f"{tree}/"
        descendants = tuple(
            path
            for path in sorted(actual_paths)
            if path.startswith(prefix) and _target_path_is_declared(path, declaration)
        )
        if not descendants:
            missing.add(tree)
        expected.update(descendants)
    extra = actual_paths - expected
    paths = tuple(sorted(expected | missing))
    return paths, PublicationTreeDifference(
        missing=tuple(sorted(missing)), extra=tuple(sorted(extra))
    )


def _target_blob(root: Path, commit: PublicationCommit, path: str) -> str | None:
    try:
        return _git(root, "cat-file", "blob", f"{commit.value}:{path}")
    except _GitReadFailure:
        return None


def _release_version(document: Mapping[str, object]) -> PublicationVersion | None:
    value = document.get("version")
    if not isinstance(value, str):
        return None
    try:
        return PublicationVersion(value=value)
    except ValueError:
        return None


def _read_publication_release_declaration_from_tree(
    root: Path,
    commit: PublicationCommit,
    tag_version: PublicationVersion,
    actual: tuple[tuple[str, str], ...],
) -> PublicationReleaseDeclarationRead:
    plugin_text = _target_blob(root, commit, _PLUGIN_MANIFEST_PATH)
    marketplace_text = _target_blob(root, commit, _MARKETPLACE_MANIFEST_PATH)
    if plugin_text is None or marketplace_text is None:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    plugin_document = _json_object(plugin_text)
    marketplace_document = _json_object(marketplace_text)
    if plugin_document is None or marketplace_document is None:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    plugin_version = _release_version(plugin_document)
    payload = _target_payload_declaration(plugin_document)
    if plugin_version is None or payload is None:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    marketplace_plugins = marketplace_document.get("plugins")
    if not isinstance(marketplace_plugins, list) or len(marketplace_plugins) != 1:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    marketplace_entry = marketplace_plugins[0]
    if not isinstance(marketplace_entry, dict):
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    marketplace_version = _release_version(marketplace_entry)
    marketplace_source = marketplace_entry.get("source")
    if not isinstance(marketplace_source, dict):
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    if marketplace_version is None:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    if plugin_version != tag_version or marketplace_version != tag_version:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_VERSION_MISMATCH
        )
    try:
        normalized_carrier = plugin_publication.normalize_pin_carrier(
            marketplace_text,
            _MARKETPLACE_MANIFEST_PATH,
            mode=plugin_publication.PinCarrierMode.GENERATED,
        )
        carrier = PublicationGeneratedPinCarrier(
            pin_carrier=normalized_carrier.pin_carrier,
            recorded_sha=normalized_carrier.recorded_sha,
        )
        paths, difference = _target_payload_paths(actual, payload)
        declaration = PublicationReleaseDeclaration(
            version=tag_version,
            paths=paths,
            carrier=carrier,
        )
    except (ValueError, plugin_publication.PublicationError):
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    return PublicationReleaseDeclarationRead(declaration=declaration, difference=difference)


def read_publication_release_declaration(
    root: Path,
    commit: PublicationCommit,
    tag_version: PublicationVersion,
) -> PublicationReleaseDeclarationRead:
    actual = _tree_blobs(root, commit)
    if actual is None:
        return PublicationReleaseDeclarationRead(
            failure=PublicationClosureStatus.RELEASE_DECLARATION_INVALID
        )
    return _read_publication_release_declaration_from_tree(
        root, commit, tag_version, actual
    )


def payload_from_manifest(root: Path, manifest_path: Path) -> PublicationPayload:
    """Create the typed payload boundary from the existing declaration/generator."""

    declaration = load_payload_declaration(manifest_path)
    blobs = declared_blob_ids(root, declaration)
    entries = tuple(sorted((str(path), str(blob)) for path, blob in blobs.items()))
    return PublicationPayload(
        paths=tuple(path for path, _ in entries),
        blob_ids=entries,
    )


def _ref_kind(name: str) -> PublicationRefKind | None:
    if name == _MAIN_REF:
        return PublicationRefKind.MAIN
    if name.startswith(_TAG_PREFIX) and _SEMVER.fullmatch(
        name.removeprefix(_TAG_PREFIX)
    ) is not None:
        return PublicationRefKind.RELEASE_TAG
    return None


def _parse_refs(raw: str) -> tuple[PublicationRef, ...] | None:
    refs: list[PublicationRef] = []
    for record in raw.splitlines():
        if not record:
            continue
        values = record.split("\t")
        if len(values) != 3:
            return None
        name, target, symref = values
        if symref:
            return None
        kind = _ref_kind(name)
        if kind is None:
            return None
        try:
            refs.append(PublicationRef(kind=kind, name=name, target=PublicationCommit(value=target)))
        except ValueError:
            return None
    names = tuple(ref.name for ref in refs)
    if len(set(names)) != len(names):
        return None
    return tuple(sorted(refs, key=lambda ref: ref.name))


def _read_snapshot(root: Path, repository: PublicationRepositoryRef) -> _SnapshotRead:
    try:
        default_branch = _git(root, "symbolic-ref", "--quiet", "HEAD").strip()
        raw = _git(
            root,
            "for-each-ref",
            "--format=%(refname)\t%(objectname)\t%(symref)",
            "refs",
        )
    except _GitReadFailure:
        return _SnapshotRead(failure=PublicationClosureStatus.REMOTE_UNREACHABLE)
    if not default_branch:
        return _SnapshotRead(failure=PublicationClosureStatus.DEFAULT_BRANCH_INVALID)
    refs = _parse_refs(raw)
    if refs is None:
        return _SnapshotRead(failure=PublicationClosureStatus.REF_SET_INVALID)
    try:
        snapshot = PublicationRemoteSnapshot(
            repository=repository,
            default_branch=default_branch,
            refs=refs,
        )
    except ValueError:
        return _SnapshotRead(failure=PublicationClosureStatus.READBACK_MISMATCH)
    return _SnapshotRead(snapshot=snapshot)


def _difference(
    expected: tuple[tuple[str, str], ...], actual: tuple[tuple[str, str], ...]
) -> PublicationTreeDifference:
    expected_paths = {path for path, _ in expected}
    actual_paths = {path for path, _ in actual}
    expected_by_path = dict(expected)
    actual_by_path = dict(actual)
    return PublicationTreeDifference(
        missing=tuple(sorted(expected_paths - actual_paths)),
        extra=tuple(sorted(actual_paths - expected_paths)),
        content_mismatch=tuple(
            sorted(
                path
                for path in expected_paths & actual_paths
                if expected_by_path[path] != actual_by_path[path]
            )
        ),
    )


def _tree_blobs(root: Path, commit: PublicationCommit) -> tuple[tuple[str, str], ...] | None:
    try:
        raw = _git(root, "ls-tree", "-r", "-z", commit.value)
    except _GitReadFailure:
        return None
    entries: list[tuple[str, str]] = []
    for record in raw.split("\0"):
        if not record:
            continue
        try:
            metadata, path = record.split("\t", 1)
            _mode, kind, blob = metadata.split(" ", 2)
        except ValueError:
            return None
        if (
            kind != "blob"
            or _mode not in ("100644", "100755", "120000")
            or _FULL_SHA.fullmatch(blob) is None
        ):
            return None
        try:
            path = _relative_path(path)
        except ValueError:
            return None
        entries.append((path, blob))
    entries.sort()
    if len({path for path, _ in entries}) != len(entries):
        return None
    return tuple(entries)


def _is_root_commit(root: Path, commit: PublicationCommit) -> bool:
    try:
        object_type = _git(root, "cat-file", "-t", commit.value).strip()
        parents = _git(root, "rev-list", "--parents", "-n", "1", commit.value).split()
    except _GitReadFailure:
        return False
    return object_type == "commit" and parents == [commit.value]


def payload_tree_difference(
    root: Path, payload: PublicationPayload, commit: PublicationCommit
) -> PublicationTreeDifference | None:
    """Return a typed tree difference, or ``None`` when Git cannot be read."""

    payload = PublicationPayload.model_validate(payload)
    actual = _tree_blobs(root, PublicationCommit.model_validate(commit))
    if actual is None:
        return None
    return _difference(payload.blob_ids, actual)


def _pin_carrier_matches(
    root: Path,
    commit: PublicationCommit,
    pin_carrier: str,
    expected_pin: PublicationCommit,
) -> bool:
    """Prove the only permitted difference is one reversible carrier pin."""

    actual = _tree_blobs(root, commit)
    if actual is None:
        return False
    carried = dict(actual).get(pin_carrier)
    if carried is None:
        return False
    try:
        published = _git(root, "cat-file", "blob", carried)
        working = (root / pin_carrier).read_text(encoding="utf-8")
        source = plugin_publication.normalize_pin_carrier(
            working,
            pin_carrier,
            mode=plugin_publication.PinCarrierMode.SOURCE,
        )
        if source.recorded_sha != expected_pin.value:
            return False
        generated = plugin_publication.normalize_pin_carrier(
            published,
            pin_carrier,
            mode=plugin_publication.PinCarrierMode.GENERATED,
        )
        healed = plugin_publication.heal_pin_carrier(generated, expected_pin.value)
    except (
        OSError,
        UnicodeDecodeError,
        ValueError,
        _GitReadFailure,
    ):
        return False
    return healed.replace("\r\n", "\n") == working.replace("\r\n", "\n")


def verify_publication_repository(
    root: Path,
    payload: PublicationPayload,
    repository: PublicationRepositoryRef,
    expected_main: PublicationCommit | None = None,
    *,
    pin_carrier: str | None = None,
    expected_pin: PublicationCommit | None = None,
) -> PublicationClosureResult:
    """Verify every admitted publication ref without creating or moving refs."""

    try:
        payload = PublicationPayload.model_validate(payload)
        repository = PublicationRepositoryRef.model_validate(repository)
        expected = None if expected_main is None else PublicationCommit.model_validate(expected_main)
        carrier = pin_carrier
        pin = None if expected_pin is None else PublicationCommit.model_validate(expected_pin)
    except ValueError:
        return PublicationClosureResult(status=PublicationClosureStatus.READBACK_MISMATCH)
    if carrier is None:
        if expected_pin is not None:
            return PublicationClosureResult(status=PublicationClosureStatus.READBACK_MISMATCH)
        carrier_pin: PublicationCommit | None = None
    else:
        carrier_pin = pin if pin is not None else expected
        if carrier_pin is None:
            return PublicationClosureResult(status=PublicationClosureStatus.READBACK_MISMATCH)
    if carrier is not None and (not isinstance(carrier, str) or carrier not in payload.paths):
        return PublicationClosureResult(status=PublicationClosureStatus.READBACK_MISMATCH)

    read = _read_snapshot(root, repository)
    if read.failure is not None:
        return PublicationClosureResult(status=read.failure)
    assert read.snapshot is not None
    snapshot = read.snapshot
    if snapshot.default_branch != _MAIN_REF:
        return PublicationClosureResult(
            status=PublicationClosureStatus.DEFAULT_BRANCH_INVALID,
            snapshot=snapshot,
        )
    if not snapshot.refs:
        return PublicationClosureResult(
            status=PublicationClosureStatus.MAIN_MISSING,
            snapshot=snapshot,
        )
    main_refs = tuple(ref for ref in snapshot.refs if ref.kind is PublicationRefKind.MAIN)
    if len(main_refs) != 1:
        return PublicationClosureResult(
            status=PublicationClosureStatus.MAIN_MISSING,
            snapshot=snapshot,
        )
    main = main_refs[0].target
    if expected is not None and main != expected:
        return PublicationClosureResult(
            status=PublicationClosureStatus.STALE_MAIN,
            snapshot=snapshot,
        )
    versioned = (
        _MARKETPLACE_MANIFEST_PATH in payload.paths
        or carrier == _MARKETPLACE_MANIFEST_PATH
    )
    if not versioned:
        # Ticket 06/09 fixtures may deliberately use a non-marketplace carrier.
        # They retain the original single-payload closure contract; the
        # version-specific declaration contract is selected only by the real
        # marketplace payload surface.
        for ref in snapshot.refs:
            if not _is_root_commit(root, ref.target):
                return PublicationClosureResult(
                    status=PublicationClosureStatus.COMMIT_NOT_ROOT,
                    snapshot=snapshot,
                )
            difference = payload_tree_difference(root, payload, ref.target)
            if difference is None:
                return PublicationClosureResult(
                    status=PublicationClosureStatus.REMOTE_UNREACHABLE,
                    snapshot=snapshot,
                )
            if carrier is not None and carrier_pin is not None:
                if not _pin_carrier_matches(root, ref.target, carrier, carrier_pin):
                    return PublicationClosureResult(
                        status=PublicationClosureStatus.TREE_MISMATCH,
                        snapshot=snapshot,
                        difference=difference,
                    )
                difference = PublicationTreeDifference(
                    missing=difference.missing,
                    extra=difference.extra,
                    content_mismatch=tuple(
                        path for path in difference.content_mismatch if path != carrier
                    ),
                )
            if not difference.is_empty:
                return PublicationClosureResult(
                    status=PublicationClosureStatus.TREE_MISMATCH,
                    snapshot=snapshot,
                    difference=difference,
                )
    else:
        release_carrier = _MARKETPLACE_MANIFEST_PATH
        release_pin = carrier_pin if carrier_pin is not None else main
        prove_live_carrier = carrier is not None or expected_pin is not None
        current_version: PublicationVersion | None = None
        main_plugin_text = _target_blob(root, main, _PLUGIN_MANIFEST_PATH)
        if main_plugin_text is not None:
            main_plugin_document = _json_object(main_plugin_text)
            if main_plugin_document is not None:
                current_version = _release_version(main_plugin_document)
        if current_version is None:
            return PublicationClosureResult(
                status=PublicationClosureStatus.RELEASE_DECLARATION_INVALID,
                snapshot=snapshot,
            )
        current_tag_count = 0
        for ref in snapshot.refs:
            if not _is_root_commit(root, ref.target):
                return PublicationClosureResult(
                    status=PublicationClosureStatus.COMMIT_NOT_ROOT,
                    snapshot=snapshot,
                )
            actual = _tree_blobs(root, ref.target)
            if actual is None:
                return PublicationClosureResult(
                    status=PublicationClosureStatus.REMOTE_UNREACHABLE,
                    snapshot=snapshot,
                )
            if ref.kind is PublicationRefKind.MAIN:
                difference = _difference(payload.blob_ids, actual)
                if prove_live_carrier and not _pin_carrier_matches(
                    root, ref.target, release_carrier, release_pin
                ):
                    return PublicationClosureResult(
                        status=PublicationClosureStatus.TREE_MISMATCH,
                        snapshot=snapshot,
                        difference=difference,
                    )
                if prove_live_carrier:
                    difference = PublicationTreeDifference(
                        missing=difference.missing,
                        extra=difference.extra,
                        content_mismatch=tuple(
                            path
                            for path in difference.content_mismatch
                            if path != release_carrier
                        ),
                    )
            else:
                tag_version = PublicationVersion(
                    value=ref.name.removeprefix(_TAG_PREFIX)
                )
                if tag_version == current_version:
                    if ref.target != main:
                        return PublicationClosureResult(
                            status=PublicationClosureStatus.PIN_MISMATCH,
                            snapshot=snapshot,
                        )
                    current_tag_count += 1
                declaration_read = _read_publication_release_declaration_from_tree(
                    root, ref.target, tag_version, actual
                )
                if declaration_read.failure is not None:
                    return PublicationClosureResult(
                        status=declaration_read.failure,
                        snapshot=snapshot,
                    )
                declaration_difference = declaration_read.difference
                if declaration_difference is None:
                    return PublicationClosureResult(
                        status=PublicationClosureStatus.RELEASE_DECLARATION_INVALID,
                        snapshot=snapshot,
                    )
                if not declaration_difference.is_empty:
                    return PublicationClosureResult(
                        status=PublicationClosureStatus.TREE_MISMATCH,
                        snapshot=snapshot,
                        difference=declaration_difference,
                    )
                if ref.target == main:
                    difference = _difference(payload.blob_ids, actual)
                    if prove_live_carrier and not _pin_carrier_matches(
                        root, ref.target, release_carrier, release_pin
                    ):
                        return PublicationClosureResult(
                            status=PublicationClosureStatus.TREE_MISMATCH,
                            snapshot=snapshot,
                            difference=difference,
                        )
                    if prove_live_carrier:
                        difference = PublicationTreeDifference(
                            missing=difference.missing,
                            extra=difference.extra,
                            content_mismatch=tuple(
                                path
                                for path in difference.content_mismatch
                                if path != release_carrier
                            ),
                        )
                else:
                    difference = PublicationTreeDifference()
            if not difference.is_empty:
                return PublicationClosureResult(
                    status=PublicationClosureStatus.TREE_MISMATCH,
                    snapshot=snapshot,
                    difference=difference,
                )
        if current_tag_count != 1:
            return PublicationClosureResult(
                status=PublicationClosureStatus.RELEASE_VERSION_MISMATCH,
                snapshot=snapshot,
            )
    return PublicationClosureResult(
        status=PublicationClosureStatus.VERIFIED,
        snapshot=snapshot,
        difference=PublicationTreeDifference(),
    )


check_publication_repository = verify_publication_repository
inspect_publication_repository = verify_publication_repository
