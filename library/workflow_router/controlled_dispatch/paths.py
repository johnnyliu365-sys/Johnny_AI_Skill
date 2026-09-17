"""Lexical relative paths and segment-aware path selectors."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata
from typing import NoReturn, TypeAlias

from .scalars import WireErrorCode, WireValidationError


def _reject(code: WireErrorCode) -> NoReturn:
    raise WireValidationError(code)


def _is_forbidden_code_point(character: str) -> bool:
    category = unicodedata.category(character)
    return category in {"Cc", "Cf", "Cs"}


def _validate_relative_path(value: object) -> str:
    if not isinstance(value, str) or type(value) is not str:
        _reject(WireErrorCode.TYPE_MISMATCH)
    try:
        byte_length = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        _reject(WireErrorCode.INVALID_PATH)
    if byte_length < 1 or byte_length > 1024:
        _reject(WireErrorCode.INVALID_PATH)
    if (
        "\\" in value
        or ":" in value
        or "\x00" in value
        or any(_is_forbidden_code_point(character) for character in value)
    ):
        _reject(WireErrorCode.INVALID_PATH)
    segments = value.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        _reject(WireErrorCode.INVALID_PATH)
    return value


@dataclass(frozen=True, slots=True)
class RelativePath:
    """A normalized-neither, forward-slash relative path."""

    value: str

    def __post_init__(self) -> None:
        _validate_relative_path(self.value)


@dataclass(frozen=True, slots=True)
class ExactPathSelector:
    """A selector matching one exact relative path."""

    path: RelativePath

    def __post_init__(self) -> None:
        if type(self.path) is not RelativePath:
            _reject(WireErrorCode.TYPE_MISMATCH)


@dataclass(frozen=True, slots=True)
class TreePathSelector:
    """A selector matching descendants below one complete path prefix."""

    prefix: RelativePath

    def __post_init__(self) -> None:
        if type(self.prefix) is not RelativePath:
            _reject(WireErrorCode.TYPE_MISMATCH)


PathSelector: TypeAlias = ExactPathSelector | TreePathSelector


def matches_path(selector: PathSelector, path: RelativePath) -> bool:
    """Match exact paths or descendants without sibling-prefix confusion."""

    if type(path) is not RelativePath or type(selector) not in {
        ExactPathSelector,
        TreePathSelector,
    }:
        _reject(WireErrorCode.TYPE_MISMATCH)
    if type(selector) is ExactPathSelector:
        return selector.path.value == path.value
    if type(selector) is TreePathSelector:
        return path.value.startswith(selector.prefix.value + "/")
    _reject(WireErrorCode.TYPE_MISMATCH)
