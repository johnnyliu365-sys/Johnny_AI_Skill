"""The one containment predicate every host-side port shares.

A second implementation of this rule is how a reparse-point evasion gets
reintroduced: the reviewed version already carries a base self-resolution
precheck that a fresh rewrite would omit. Import this; do not restate it.

A redirect is decided from the file system, never from a spelling comparison.
Case folding, in particular, is not the file system's identity: a directory
with per-directory case sensitivity keeps ``A`` and ``a`` distinct, and a
junction can be named so that its name folds to its target's name. So every
existing component of the base is examined with ``os.lstat`` first.

No containment decision folds case. Two spellings name one directory only when
``(st_dev, st_ino)`` from ``os.stat`` agrees, and the final test is an exact,
component-by-component prefix of the two resolved paths.
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


def _identity(path: Path) -> tuple[int, int, int] | None:
    """The file identity of ``path``, or of its nearest existing ancestor.

    The result is ``(st_dev, st_ino, missing)``, where ``missing`` counts the
    trailing components that do not exist yet. None means the identity cannot
    be read, and the caller refuses. No spelling is compared.
    """

    current = path
    missing = 0
    while True:
        try:
            status = os.stat(current)
        except (FileNotFoundError, NotADirectoryError):
            parent = current.parent
            if os.fspath(parent) == os.fspath(current):
                return None
            current = parent
            missing += 1
            continue
        except OSError:
            return None
        return (int(status.st_dev), int(status.st_ino), missing)


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
        try:
            attributes = status.st_file_attributes
        except AttributeError:
            reason = f"component {component} has no file attributes to examine"
            return _ComponentResult(_Component.REFUSE, reason)
        if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
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

    The file identity of the base is taken before anything else. The base is
    then resolved once, and the components of the given spelling and of the
    resolved path are both examined. The identity is read again afterwards: if
    the base changed meanwhile, or if the resolution is not the directory the
    base names (a case-twin junction that was in place at the resolve and is
    gone at the walk, which no spelling comparison can tell), the base is
    refused. Only a redirect that is still in place when it is examined is seen
    by the walk; a swap that leaves the base the same directory by identity is
    not a change of the anchor, and the anchor is the very path examined. A
    spelling that differs (a short name) must also have a long-name lookup
    that succeeds and names the same directory. Nothing here folds case.
    """

    if not base.is_absolute():
        return _Refusal(f"base {base} is not an absolute path")
    before = _identity(base)
    if before is None:
        return _Refusal(f"the identity of base {base} cannot be read")
    try:
        resolved_base = base.resolve()
    except OSError as error:
        return _Refusal(f"base {base} cannot be resolved ({error})")
    for spelling in (base, resolved_base):
        redirect = _redirected_component(spelling)
        if redirect is not None:
            return _Refusal(redirect)
    after = _identity(base)
    if after is None or after != before:
        return _Refusal(f"base {base} changed while it was being checked")
    if _identity(resolved_base) != after:
        return _Refusal(f"base {base} resolves to {resolved_base}, which is not the same directory")
    if os.fspath(base) == os.fspath(resolved_base):
        return _Anchor(resolved_base)
    if ".." in base.parts:
        return _Refusal(f"base {base} holds a parent-directory component")
    long_base = _long_name(base)
    if long_base is None:
        return _Refusal(
            f"the long-name lookup of base {base} failed "
            f"(Windows error {_last_lookup_error()})"
        )
    if _identity(long_base) != after:
        return _Refusal(f"the long name {long_base} of base {base} is not the same directory")
    return _Anchor(resolved_base)


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
            if os.fspath(existing.parent) == os.fspath(existing):
                return False
            remainder.append(existing.name)
            existing = existing.parent
        resolved = existing.resolve().joinpath(*reversed(remainder))
        # Both paths come from ``resolve()`` and carry the on-disk spelling, so
        # containment is an exact prefix of components; no case folding.
        count = len(resolved_base.parts)
        return resolved.parts[:count] == resolved_base.parts
    except OSError:
        return False


__all__ = ["resolves_within_root"]
