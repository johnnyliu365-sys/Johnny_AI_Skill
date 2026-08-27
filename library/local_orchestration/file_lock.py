"""The one OS-visible exclusive file lock every shared-state component uses.

Extracted under W5. Two identical private copies already existed (the live
dispatch metadata boundary and the Senior review inbox store), and the review
return path had none at all — which is how the exactly-once guarantee held
within a process and silently failed across two. A second implementation of a
mutual-exclusion primitive is how a subtle divergence gets reintroduced:
import this one.

The lock is a one-byte region lock on a dedicated lock file. It is advisory
between cooperating processes, blocking, and released on file-handle close, so
an abnormally terminated holder cannot leave it stuck.

Governance 20 made the primitive portable without moving any of those four
properties. The platform is decided once, at import time, and bound to
``_acquire`` and ``_release``; the lock object itself names no platform and
takes no branch per acquisition.

Windows keeps ``msvcrt``, byte for byte what W5 shipped. POSIX uses
``fcntl.flock`` rather than ``fcntl.lockf``, and the reason is ownership. A
``flock`` lock belongs to the open file description, exactly as the ``msvcrt``
region lock belongs to the handle, so on both platforms the lock is held and
dropped through the one handle this object opened and nothing else. ``lockf``
locks belong to the *process*: closing any unrelated descriptor for the same
path anywhere in the process would silently drop a lock still believed held,
and a second acquisition inside one process would succeed on POSIX while
blocking on Windows. Those are exactly the subtle divergences the extraction
exists to prevent — one primitive, one meaning, two platforms.

``ExclusiveWindowsFileLock`` survives as an alias because six modules import
it under that name and this ticket may not touch them. The new name is the
true one; retiring the alias is a later ticket's work.
"""

from __future__ import annotations

import errno
import os
import sys
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Self


class FileLockAcquireDecision(str, Enum):
    """The finite outcomes of one nonblocking lock attempt."""

    ACQUIRED = "acquired"
    CONTENDED = "contended"


if sys.platform == "win32":
    import msvcrt

    def _acquire(handle: BinaryIO) -> None:
        """Block until the one-byte region at offset zero is ours."""

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)

    def _release(handle: BinaryIO) -> None:
        """Drop the region lock the matching acquisition took."""

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

    def _try_acquire(handle: BinaryIO) -> FileLockAcquireDecision:
        """Attempt the Windows one-byte region lock without waiting."""

        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            if error.errno == errno.EACCES:
                return FileLockAcquireDecision.CONTENDED
            raise
        return FileLockAcquireDecision.ACQUIRED

else:
    import fcntl

    def _acquire(handle: BinaryIO) -> None:
        """Block until this open file description owns the file exclusively."""

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)

    def _release(handle: BinaryIO) -> None:
        """Drop the exclusive lock the matching acquisition took."""

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _try_acquire(handle: BinaryIO) -> FileLockAcquireDecision:
        """Attempt the POSIX one-byte file lock without waiting."""

        handle.seek(0)
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            if error.errno in (errno.EACCES, errno.EAGAIN):
                return FileLockAcquireDecision.CONTENDED
            raise
        return FileLockAcquireDecision.ACQUIRED


class ExclusiveFileLock:
    """One-byte OS-visible exclusive lock shared by independent processes."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: BinaryIO | None = None

    def _open_handle(self) -> BinaryIO:
        handle = self._path.open("a+b")
        try:
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\x00")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError:
            handle.close()
            raise
        return handle

    def __enter__(self) -> Self:
        handle = self._open_handle()
        try:
            _acquire(handle)
        except OSError:
            handle.close()
            raise
        self._handle = handle
        return self

    def try_acquire(self) -> FileLockAcquireDecision:
        """Attempt one nonblocking acquisition on this lock instance."""

        if self._handle is not None:
            raise RuntimeError("try_acquire requires an idle lock")
        handle = self._open_handle()
        try:
            decision = _try_acquire(handle)
        except OSError:
            handle.close()
            raise
        if decision is FileLockAcquireDecision.CONTENDED:
            handle.close()
            return decision
        self._handle = handle
        return decision

    def release(self) -> None:
        """Release an explicitly acquired lock and close its retained handle."""

        handle = self._handle
        if handle is None:
            raise RuntimeError("release requires an acquired lock")
        self._handle = None
        try:
            _release(handle)
        finally:
            handle.close()

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exception_type, exception, traceback
        handle = self._handle
        self._handle = None
        if handle is None:
            return
        try:
            _release(handle)
        finally:
            handle.close()


# The name six importers still use. Same object, not a subclass and not a
# wrapper: a second class here would be a second implementation.
ExclusiveWindowsFileLock = ExclusiveFileLock


__all__ = [
    "ExclusiveFileLock",
    "ExclusiveWindowsFileLock",
    "FileLockAcquireDecision",
]
