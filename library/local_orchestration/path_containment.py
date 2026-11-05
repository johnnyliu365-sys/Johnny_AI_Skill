"""The one containment predicate every host-side port shares.

A second implementation of this rule is how a reparse-point evasion gets
reintroduced: the reviewed version already carries a base self-resolution
precheck that a fresh rewrite would omit. Import this; do not restate it.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _long_name(path: Path) -> Path | None:
    """Return the long-name spelling of a path, or None when it cannot be had.

    On Windows an 8.3 short-name component (``RUNNER~1``) is an alias of the
    same directory, not a redirect. ``GetLongPathNameW`` expands those aliases
    and, unlike ``Path.resolve``, does not follow junctions, symlinks or other
    reparse points. A failed lookup is reported as None so the caller refuses.
    Elsewhere there is no such alias and the path is returned unchanged.
    """

    if sys.platform != "win32":
        return path
    import ctypes
    from ctypes import wintypes

    get_long_path_name = ctypes.windll.kernel32.GetLongPathNameW
    get_long_path_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    get_long_path_name.restype = wintypes.DWORD
    size = 1024
    for _ in range(2):
        buffer = ctypes.create_unicode_buffer(size)
        needed = int(get_long_path_name(str(path), buffer, size))
        if needed == 0:
            return None
        if needed < size:
            return Path(buffer.value)
        size = needed + 1
    return None


def _is_same_directory_alias(base: Path, resolved_base: Path) -> bool:
    """True only when ``base`` differs from its resolution by short names alone."""

    if ".." in base.parts:
        return False
    long_base = _long_name(base)
    if long_base is None:
        return False
    return os.path.normcase(str(long_base)) == os.path.normcase(str(resolved_base))


def resolves_within_root(target: Path, base: Path) -> bool:
    """Reject a target whose own path or any ancestor redirects elsewhere.

    Checking only an existing leaf misses two cases: a not-yet-created leaf
    under a redirected parent, and a redirected ancestor above it. The nearest
    existing ancestor is therefore resolved and required to stay inside the
    resolved base, with the unresolved remainder appended unchanged.
    """

    try:
        resolved_base = base.resolve()
        if resolved_base != base and not _is_same_directory_alias(base, resolved_base):
            # The base itself redirects somewhere else; a containment check
            # anchored to the redirected location would be circular. A Windows
            # 8.3 short-name spelling of the same directory is not a redirect.
            return False
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
