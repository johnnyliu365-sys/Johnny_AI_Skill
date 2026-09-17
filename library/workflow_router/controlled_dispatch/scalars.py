"""Strict scalar values used by the controlled-dispatch wire boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Final, NoReturn, Pattern


class WireErrorCode(str, Enum):
    """Closed error vocabulary for wire-value construction."""

    TYPE_MISMATCH = "type_mismatch"
    INVALID_ID = "invalid_id"
    INVALID_DIGEST = "invalid_digest"
    INVALID_GIT_ID = "invalid_git_id"
    INVALID_PATH = "invalid_path"
    INVALID_KEY = "invalid_key"
    DUPLICATE_KEY = "duplicate_key"
    OUT_OF_RANGE = "out_of_range"
    LIMIT_EXCEEDED = "limit_exceeded"
    INVALID_TEXT = "invalid_text"


class WireValidationError(ValueError):
    """A non-sensitive, typed validation failure at the wire boundary."""

    code: WireErrorCode

    def __init__(self, code: WireErrorCode) -> None:
        self.code = code
        super().__init__(code.value)


def _reject(code: WireErrorCode) -> NoReturn:
    raise WireValidationError(code)


_EXTERNAL_ID: Final[Pattern[str]] = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}\Z")
_INTERNAL_ID: Final[Pattern[str]] = re.compile(r"[a-z][a-z0-9-]{2,127}\Z")
_DIGEST: Final[Pattern[str]] = re.compile(r"[0-9a-f]{64}\Z")


def _require_text(value: object, pattern: Pattern[str], code: WireErrorCode) -> str:
    """Validate an exact string and return it without normalization."""

    if type(value) is not str:
        _reject(WireErrorCode.TYPE_MISMATCH)
    if pattern.fullmatch(value) is None:
        _reject(code)
    return value


@dataclass(frozen=True, slots=True)
class ExternalId:
    """An externally supplied identifier whose code points are preserved."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, _EXTERNAL_ID, WireErrorCode.INVALID_ID)


@dataclass(frozen=True, slots=True)
class InternalId:
    """An opaque internal identifier; no external-to-internal mapping is implied."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, _INTERNAL_ID, WireErrorCode.INVALID_ID)


@dataclass(frozen=True, slots=True)
class Digest:
    """A lowercase SHA-256 hexadecimal digest."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, _DIGEST, WireErrorCode.INVALID_DIGEST)


class GitAlgorithm(str, Enum):
    """Git object hash algorithms supported by the wire contract."""

    SHA1 = "sha1"
    SHA256 = "sha256"


@dataclass(frozen=True, slots=True)
class GitObjectId:
    """A shape-validated Git object identifier, not an existence assertion."""

    algorithm: GitAlgorithm
    hex: str

    def __post_init__(self) -> None:
        if type(self.algorithm) is not GitAlgorithm:
            _reject(WireErrorCode.TYPE_MISMATCH)
        if type(self.hex) is not str:
            _reject(WireErrorCode.TYPE_MISMATCH)
        required_length = 40 if self.algorithm is GitAlgorithm.SHA1 else 64
        if len(self.hex) != required_length or re.fullmatch(r"[0-9a-f]+\Z", self.hex) is None:
            _reject(WireErrorCode.INVALID_GIT_ID)
