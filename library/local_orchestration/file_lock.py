"""The one OS-visible exclusive file lock every shared-state component uses.

Extracted under W5. Two identical private copies already existed (the live
dispatch metadata boundary and the Senior review inbox store), and the review
return path had none at all — which is how the exactly-once guarantee held
within a process and silently failed across two. A second implementation of a
mutual-exclusion primitive is how a subtle divergence gets reintroduced:
import this one.

The lock is a one-byte `msvcrt` region lock on a dedicated lock file. It is
advisory between cooperating processes, blocking, and released on file-handle
close, so an abnormally terminated holder cannot leave it stuck.
"""

from __future__ import annotations

import msvcrt
import os
from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Self


class ExclusiveWindowsFileLock:
    """One-byte OS-visible exclusive lock shared by independent processes."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._handle: BinaryIO | None = None

    def __enter__(self) -> Self:
        handle = self._path.open("a+b")
        try:
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\x00")
                handle.flush()
                os.fsync(handle.fileno())
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        except OSError:
            handle.close()
            raise
        self._handle = handle
        return self

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
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            handle.close()


__all__ = ["ExclusiveWindowsFileLock"]
