"""The one containment predicate every host-side port shares.

A second implementation of this rule is how a reparse-point evasion gets
reintroduced: the reviewed version already carries a base self-resolution
precheck that a fresh rewrite would omit. Import this; do not restate it.

A redirect is decided from the file system, never from a spelling comparison.
Case folding, in particular, is not the file system's identity: a directory
with per-directory case sensitivity keeps ``A`` and ``a`` distinct, and a
junction can be named so that its name folds to its target's name. So every
existing component of the base is examined with ``os.lstat`` first.
"""

from __future__ import annotations

import os
import stat
import sys
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_INITIAL_BUFFER_CHARACTERS = 1024



class _LookupState(threading.local):
    """The Windows error code of the last long-name lookup, kept per thread."""

    error: int = 0


_lookup_state = _LookupState()

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    # Loaded once, with the last-error slot kept per thread, and the argument
    # and return types declared once instead of on every call.
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _get_long_path_name = _kernel32.GetLongPathNameW
    _get_long_path_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _get_long_path_name.restype = wintypes.DWORD

    def _windows_long_name(path: Path) -> Path | None:
        """The ``GetLongPathNameW`` lookup, with the buffer-size retry (Windows only)."""

        size = _INITIAL_BUFFER_CHARACTERS
        for _ in range(2):
            buffer = ctypes.create_unicode_buffer(size)
            ctypes.set_last_error(0)
            needed = int(_get_long_path_name(str(path), buffer, size))
            if needed == 0:
                _lookup_state.error = int(ctypes.get_last_error())
                return None
            if needed < size:
                return Path(buffer.value)
            size = needed + 1
        _lookup_state.error = -1
        return None


def _long_name(path: Path) -> Path | None:
    """Return the long-name spelling of a path, or None when it cannot be had.

    On Windows an 8.3 short-name component (``RUNNER~1``) is an alias of the
    same directory, not a redirect. ``GetLongPathNameW`` expands those aliases
    and, unlike ``Path.resolve``, does not follow junctions, symlinks or other
    reparse points. A failed lookup is reported as None so the caller refuses;
    the Windows error code of the failure is kept for the refusal reason.
    Elsewhere there is no such alias and the path is returned unchanged.
    """

    _lookup_state.error = 0
    if sys.platform == "win32":
        return _windows_long_name(path)
    return path


def _last_lookup_error() -> int:
    """The Windows error code of the most recent failed long-name lookup."""

    return _lookup_state.error


def _is_same_directory_alias(base: Path, resolved_base: Path) -> bool:
    """True only when ``base`` differs from its resolution by short names alone.

    This runs only after the base has been shown to hold no redirect, so it
    decides spelling and nothing else.
    """

    if ".." in base.parts:
        return False
    long_base = _long_name(base)
    if long_base is None:
        return False
    return os.path.normcase(str(long_base)) == os.path.normcase(str(resolved_base))


class _Component(Enum):
    """What examining one existing path component found."""

    PASS = "pass"
    REFUSE = "refuse"
    MISSING = "missing"


@dataclass(frozen=True)
class _ComponentResult:
    """The state of one component; ``reason`` is diagnostic text for REFUSE only."""

    state: _Component
    reason: str | None = None


_PASSED = _ComponentResult(_Component.PASS)
_MISSING = _ComponentResult(_Component.MISSING)


def _examine_component(component: Path) -> _ComponentResult:
    """Examine one path component with ``lstat``, which does not follow links."""

    try:
        status = os.lstat(component)
    except (FileNotFoundError, NotADirectoryError):
        return _MISSING
    except OSError as error:
        reason = f"component {component} cannot be examined ({error})"
        return _ComponentResult(_Component.REFUSE, reason)
    if stat.S_ISLNK(status.st_mode):
        reason = f"component {component} is a symbolic link"
        return _ComponentResult(_Component.REFUSE, reason)
    if sys.platform == "win32":
        if status.st_file_attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
            reason = f"component {component} is a reparse point"
            return _ComponentResult(_Component.REFUSE, reason)
    return _PASSED


def _redirected_component(base: Path) -> str | None:
    """The first redirect among the existing components of ``base``, if any.

    Every existing component from the root of the volume down to the base is
    examined with ``lstat``, which does not follow links, so the answer comes
    from the file system and not from comparing two spellings. A component
    that cannot be examined is reported, never skipped. Components that do not
    exist are not examined; nothing below a missing component exists either.
    """

    parts = base.parts
    for count in range(1, len(parts) + 1):
        result = _examine_component(Path(*parts[:count]))
        if result.state is _Component.MISSING:
            return None
        if result.state is _Component.REFUSE:
            if result.reason is None:
                return f"component {Path(*parts[:count])} is refused"
            return result.reason
    return None


@dataclass(frozen=True)
class _Anchor:
    """A base that was checked and resolved exactly once."""

    resolved: Path


@dataclass(frozen=True)
class _Refusal:
    """A base that cannot anchor a containment check."""

    reason: str


def _anchor_for(base: Path) -> _Anchor | _Refusal:
    """Check ``base`` and return the one resolution that was checked.

    The base is resolved once. The components of the given spelling and of the
    resolved path are both examined after that resolution, so a component
    swapped for a redirect before or during it is seen, and the anchor of the
    containment check is the very path that was examined.
    """

    if not base.is_absolute():
        return _Refusal(f"base {base} is not an absolute path")
    try:
        resolved_base = base.resolve()
    except OSError as error:
        return _Refusal(f"base {base} cannot be resolved ({error})")
    for spelling in (base, resolved_base):
        redirect = _redirected_component(spelling)
        if redirect is not None:
            return _Refusal(redirect)
    if resolved_base == base:
        return _Anchor(resolved_base)
    if _is_same_directory_alias(base, resolved_base):
        return _Anchor(resolved_base)
    if sys.platform == "win32" and _long_name(base) is None:
        return _Refusal(
            f"the long-name lookup of base {base} failed "
            f"(Windows error {_last_lookup_error()})"
        )
    return _Refusal(f"base {base} resolves to {resolved_base}, which is not the same spelling")


def _base_refusal_reason(base: Path) -> str | None:
    """Why ``base`` cannot anchor a containment check, or None when it can."""

    outcome = _anchor_for(base)
    return outcome.reason if isinstance(outcome, _Refusal) else None


def resolves_within_root(target: Path, base: Path) -> bool:
    """Reject a target whose own path or any ancestor redirects elsewhere.

    Checking only an existing leaf misses two cases: a not-yet-created leaf
    under a redirected parent, and a redirected ancestor above it. The nearest
    existing ancestor is therefore resolved and required to stay inside the
    resolved base, with the unresolved remainder appended unchanged.
    """

    try:
        outcome = _anchor_for(base)
        if isinstance(outcome, _Refusal):
            # The base itself redirects somewhere else; a containment check
            # anchored to the redirected location would be circular. A Windows
            # 8.3 short-name spelling of the same directory is not a redirect.
            return False
        resolved_base = outcome.resolved
        existing = target
        remainder: list[str] = []
        while not existing.exists():
            if existing.parent == existing:
                return False
            remainder.append(existing.name)
            existing = existing.parent
        resolved = existing.resolve().joinpath(*reversed(remainder))
        return resolved == resolved_base or resolved_base in resolved.parents
    except OSError:
        return False


__all__ = ["resolves_within_root"]
