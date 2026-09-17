"""Deterministic canonical JSON bytes and domain-separated fingerprints."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import NoReturn, TypeAlias, TypeGuard

from .scalars import Digest, WireErrorCode, WireValidationError
from .values import (
    CanonicalArray,
    CanonicalBool,
    CanonicalInteger,
    CanonicalMember,
    CanonicalNull,
    CanonicalObject,
    CanonicalString,
    CanonicalValue,
)


MAX_DEPTH = 16
MAX_NODES = 4_096
MAX_OUTPUT_BYTES = 65_536
MAX_RAW_BYTES = 65_536


JsonValue: TypeAlias = (
    None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]
)


def _reject(code: WireErrorCode) -> NoReturn:
    raise WireValidationError(code)


def _is_canonical_object(value: object) -> TypeGuard[CanonicalObject]:
    return type(value) is CanonicalObject


@dataclass
class _TraversalState:
    nodes: int = 0

    def count_value(self) -> None:
        self.nodes += 1
        if self.nodes > MAX_NODES:
            _reject(WireErrorCode.LIMIT_EXCEEDED)

    def count_key(self) -> None:
        self.nodes += 1
        if self.nodes > MAX_NODES:
            _reject(WireErrorCode.LIMIT_EXCEEDED)


def _project(value: CanonicalValue, depth: int, state: _TraversalState) -> JsonValue:
    state.count_value()
    if isinstance(value, CanonicalNull):
        return None
    if isinstance(value, CanonicalBool):
        return value.value
    if isinstance(value, CanonicalInteger):
        return value.value
    if isinstance(value, CanonicalString):
        return value.value
    if isinstance(value, CanonicalArray):
        if depth > MAX_DEPTH:
            _reject(WireErrorCode.LIMIT_EXCEEDED)
        return [_project(item, depth + 1, state) for item in value.items]
    if isinstance(value, CanonicalObject):
        if depth > MAX_DEPTH:
            _reject(WireErrorCode.LIMIT_EXCEEDED)
        projected: dict[str, JsonValue] = {}
        for member in value.members:
            state.count_key()
            projected[member.key] = _project(member.value, depth + 1, state)
        return projected
    _reject(WireErrorCode.TYPE_MISMATCH)


def canonical_json_bytes(value: CanonicalObject) -> bytes:
    """Encode one canonical object with bounded traversal and output size."""

    if not _is_canonical_object(value):
        _reject(WireErrorCode.TYPE_MISMATCH)
    projected = _project(value, 1, _TraversalState())
    encoded = json.dumps(
        projected,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    if len(encoded) > MAX_OUTPUT_BYTES:
        _reject(WireErrorCode.LIMIT_EXCEEDED)
    return encoded


def _digest_without_top_level_key(value: CanonicalObject, self_key: str, domain: bytes) -> Digest:
    if not _is_canonical_object(value):
        _reject(WireErrorCode.TYPE_MISMATCH)
    for member in value.members:
        if member.key in {"raw_sha256", "source_blob_digest"}:
            _reject(WireErrorCode.INVALID_KEY)
    body = CanonicalObject(tuple(member for member in value.members if member.key != self_key))
    payload = domain + canonical_json_bytes(body)
    return Digest(hashlib.sha256(payload).hexdigest())


def dispatch_digest(value: CanonicalObject) -> Digest:
    """Hash the canonical packet body under the dispatch domain."""

    return _digest_without_top_level_key(
        value,
        "dispatch_digest",
        b"johnny.cve.dispatch.v1\x00",
    )


def report_digest(value: CanonicalObject) -> Digest:
    """Hash the canonical report body under the report domain."""

    return _digest_without_top_level_key(
        value,
        "report_digest",
        b"johnny.cve.report.v1\x00",
    )


def raw_blob_digest(data: bytes) -> Digest:
    """Hash detached raw evidence, bounded before hashing."""

    if type(data) is not bytes:
        _reject(WireErrorCode.TYPE_MISMATCH)
    if len(data) > MAX_RAW_BYTES:
        _reject(WireErrorCode.LIMIT_EXCEEDED)
    return Digest(hashlib.sha256(data).hexdigest())
