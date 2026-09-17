"""Immutable closed canonical-value algebra for controlled-dispatch packets."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import NoReturn, TypeAlias, TypeGuard

from .scalars import WireErrorCode, WireValidationError


MAX_COLLECTION_ITEMS = 256
MAX_INTEGER = 2_147_483_647
MAX_STRING_BYTES = 4_096


def _reject(code: WireErrorCode) -> NoReturn:
    raise WireValidationError(code)


def _is_valid_text(value: object) -> bool:
    if not isinstance(value, str) or type(value) is not str:
        _reject(WireErrorCode.TYPE_MISMATCH)
    try:
        encoded_length = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        _reject(WireErrorCode.INVALID_TEXT)
    if encoded_length > MAX_STRING_BYTES:
        _reject(WireErrorCode.LIMIT_EXCEEDED)
    if "\x00" in value or any(0xD800 <= ord(character) <= 0xDFFF for character in value):
        _reject(WireErrorCode.INVALID_TEXT)
    return True


@dataclass(frozen=True, slots=True)
class CanonicalNull:
    """The one canonical null value."""


@dataclass(frozen=True, slots=True)
class CanonicalBool:
    """A canonical Boolean, distinct from integers."""

    value: bool

    def __post_init__(self) -> None:
        if type(self.value) is not bool:
            _reject(WireErrorCode.TYPE_MISMATCH)


@dataclass(frozen=True, slots=True)
class CanonicalInteger:
    """A bounded non-negative canonical integer."""

    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int:
            _reject(WireErrorCode.TYPE_MISMATCH)
        if not 0 <= self.value <= MAX_INTEGER:
            _reject(WireErrorCode.OUT_OF_RANGE)


@dataclass(frozen=True, slots=True)
class CanonicalString:
    """A canonical string retaining every accepted code point exactly."""

    value: str

    def __post_init__(self) -> None:
        _is_valid_text(self.value)


@dataclass(frozen=True, slots=True)
class CanonicalArray:
    """An ordered tuple of canonical values."""

    items: tuple[CanonicalValue, ...]

    def __post_init__(self) -> None:
        if type(self.items) is not tuple:
            _reject(WireErrorCode.TYPE_MISMATCH)
        if len(self.items) > MAX_COLLECTION_ITEMS:
            _reject(WireErrorCode.LIMIT_EXCEEDED)
        for item in self.items:
            if not _is_canonical_value(item):
                _reject(WireErrorCode.TYPE_MISMATCH)


@dataclass(frozen=True, slots=True)
class CanonicalMember:
    """One ASCII schema key and its canonical value."""

    key: str
    value: CanonicalValue

    def __post_init__(self) -> None:
        if type(self.key) is not str:
            _reject(WireErrorCode.TYPE_MISMATCH)
        if re.fullmatch(r"[a-z][a-z0-9_]{0,63}\Z", self.key) is None:
            _reject(WireErrorCode.INVALID_KEY)
        if not _is_canonical_value(self.value):
            _reject(WireErrorCode.TYPE_MISMATCH)


@dataclass(frozen=True, slots=True)
class CanonicalObject:
    """An immutable unique-key object."""

    members: tuple[CanonicalMember, ...]

    def __post_init__(self) -> None:
        if type(self.members) is not tuple:
            _reject(WireErrorCode.TYPE_MISMATCH)
        if len(self.members) > MAX_COLLECTION_ITEMS:
            _reject(WireErrorCode.LIMIT_EXCEEDED)
        keys: set[str] = set()
        for member in self.members:
            if type(member) is not CanonicalMember:
                _reject(WireErrorCode.TYPE_MISMATCH)
            if member.key in keys:
                _reject(WireErrorCode.DUPLICATE_KEY)
            keys.add(member.key)


CanonicalValue: TypeAlias = (
    CanonicalNull
    | CanonicalBool
    | CanonicalInteger
    | CanonicalString
    | CanonicalArray
    | CanonicalObject
)


def _is_canonical_value(value: object) -> TypeGuard[CanonicalValue]:
    return type(value) in {
        CanonicalNull,
        CanonicalBool,
        CanonicalInteger,
        CanonicalString,
        CanonicalArray,
        CanonicalObject,
    }
