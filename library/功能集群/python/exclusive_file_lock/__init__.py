"""Public exclusive-file-lock contracts."""

from .file_lock import (
    ExclusiveFileLock,
    ExclusiveWindowsFileLock,
    FileLockAcquireDecision,
)

__all__ = [
    "ExclusiveFileLock",
    "ExclusiveWindowsFileLock",
    "FileLockAcquireDecision",
]
