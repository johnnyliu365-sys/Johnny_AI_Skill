"""Read test-consumer source text from one immutable Git commit."""

from __future__ import annotations

import math
import os
import re
import subprocess
import threading
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath, PureWindowsPath

from library.local_orchestration.test_dependency_inventory import (
    DeclaredTestCommand,
    PythonSource,
    PythonTestConsumerInventory,
    RetirementInventory,
)


class TestDependencySourceFailure(StrEnum):
    INVALID_REPOSITORY_ROOT = "INVALID_REPOSITORY_ROOT"
    INVALID_COMMIT_SHA = "INVALID_COMMIT_SHA"
    COMMIT_NOT_FOUND_OR_NOT_COMMIT = "COMMIT_NOT_FOUND_OR_NOT_COMMIT"
    GIT_COMMAND_FAILED = "GIT_COMMAND_FAILED"
    GIT_COMMAND_TIMEOUT = "GIT_COMMAND_TIMEOUT"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    INVALID_PATH = "INVALID_PATH"
    UNSUPPORTED_TREE_ENTRY = "UNSUPPORTED_TREE_ENTRY"
    INVALID_UTF8 = "INVALID_UTF8"


class TestDependencySourceError(RuntimeError):
    """A named, fail-closed error from the pinned Git source boundary."""

    def __init__(self, reason: TestDependencySourceFailure) -> None:
        self.reason = reason
        super().__init__(reason.value)


@dataclass(frozen=True, slots=True)
class GitPinnedTestDependencyInventory:
    """Inventory evidence bound to the exact commit read by the adapter."""

    commit_sha: str
    source_refs: tuple[str, ...]
    inventory: RetirementInventory


@dataclass(frozen=True, slots=True)
class _GitTreeEntry:
    mode: str
    object_type: str
    object_id: str
    path: str


class GitTestDependencySourceAdapter:
    """Load bounded Python blobs from a full commit SHA, without using the worktree."""

    _COMMIT_SHA_PATTERN = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})\Z")
    _MAX_TREE_LISTING_BYTES = 16 * 1024 * 1024
    _CAT_FILE_HEADER_BYTES_PER_OBJECT = 128

    def __init__(
        self,
        *,
        max_python_files: int = 4096,
        max_blob_bytes: int = 1024 * 1024,
        max_total_source_bytes: int = 16 * 1024 * 1024,
        timeout_seconds: float = 10.0,
    ) -> None:
        if max_python_files <= 0:
            raise ValueError("max_python_files must be positive")
        if max_blob_bytes <= 0:
            raise ValueError("max_blob_bytes must be positive")
        if max_total_source_bytes <= 0:
            raise ValueError("max_total_source_bytes must be positive")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        self._max_python_files = max_python_files
        self._max_blob_bytes = max_blob_bytes
        self._max_total_source_bytes = max_total_source_bytes
        self._timeout_seconds = timeout_seconds

    def read_inventory(
        self,
        repository_root: str | Path,
        commit_sha: str,
        test_ref: str,
        declared_commands: tuple[DeclaredTestCommand, ...] = (),
    ) -> GitPinnedTestDependencyInventory:
        """Inventory Python source committed at `commit_sha`; never inspect checkout files."""

        deadline = time.monotonic() + self._timeout_seconds
        root = self._validate_repository_root(repository_root, deadline)
        canonical_commit = self._validate_commit(root, commit_sha, deadline)
        entries = self._read_tree_entries(root, canonical_commit, deadline)
        sources = self._read_python_sources(root, entries, deadline)
        inventory = PythonTestConsumerInventory(
            sources=tuple(sources), declared_commands=declared_commands
        ).retirement_inventory(test_ref)
        return GitPinnedTestDependencyInventory(
            commit_sha=canonical_commit,
            source_refs=tuple(source.source_ref for source in sources),
            inventory=inventory,
        )

    def _validate_repository_root(
        self, repository_root: str | Path, deadline: float
    ) -> Path:
        try:
            root = Path(repository_root).expanduser().resolve(strict=True)
            if not root.is_dir():
                raise TestDependencySourceError(
                    TestDependencySourceFailure.INVALID_REPOSITORY_ROOT
                )
        except (OSError, RuntimeError, ValueError) as error:
            raise TestDependencySourceError(
                TestDependencySourceFailure.INVALID_REPOSITORY_ROOT
            ) from error

        try:
            top_level_output = self._run_git(
                root,
                ("rev-parse", "--show-toplevel"),
                max_stdout_bytes=64 * 1024,
                deadline=deadline,
            )
            top_level = Path(os.fsdecode(top_level_output.rstrip(b"\r\n"))).resolve(
                strict=True
            )
        except TestDependencySourceError as error:
            if error.reason is TestDependencySourceFailure.GIT_COMMAND_TIMEOUT:
                raise
            raise TestDependencySourceError(
                TestDependencySourceFailure.INVALID_REPOSITORY_ROOT
            ) from error
        except (OSError, RuntimeError, ValueError) as error:
            raise TestDependencySourceError(
                TestDependencySourceFailure.INVALID_REPOSITORY_ROOT
            ) from error

        if os.path.normcase(str(top_level)) != os.path.normcase(str(root)):
            raise TestDependencySourceError(
                TestDependencySourceFailure.INVALID_REPOSITORY_ROOT
            )
        return root

    def _validate_commit(self, root: Path, commit_sha: str, deadline: float) -> str:
        if not self._COMMIT_SHA_PATTERN.fullmatch(commit_sha):
            raise TestDependencySourceError(TestDependencySourceFailure.INVALID_COMMIT_SHA)

        try:
            resolved = self._run_git(
                root,
                ("rev-parse", "--verify", "--end-of-options", f"{commit_sha}^{{commit}}"),
                max_stdout_bytes=256,
                deadline=deadline,
            ).decode("ascii").strip().lower()
        except TestDependencySourceError as error:
            if error.reason is TestDependencySourceFailure.GIT_COMMAND_FAILED:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.COMMIT_NOT_FOUND_OR_NOT_COMMIT
                ) from error
            raise

        if resolved != commit_sha.lower():
            raise TestDependencySourceError(
                TestDependencySourceFailure.COMMIT_NOT_FOUND_OR_NOT_COMMIT
            )
        return resolved

    def _read_tree_entries(
        self, root: Path, commit_sha: str, deadline: float
    ) -> tuple[_GitTreeEntry, ...]:
        try:
            listing = self._run_git(
                root,
                (
                    "ls-tree",
                    "-r",
                    "-z",
                    "--full-tree",
                    commit_sha,
                ),
                max_stdout_bytes=self._MAX_TREE_LISTING_BYTES,
                deadline=deadline,
            )
        except TestDependencySourceError:
            raise

        records = listing.split(b"\0")
        if records and records[-1] == b"":
            records.pop()

        entries: list[_GitTreeEntry] = []
        seen_paths: set[str] = set()
        for record in records:
            header, separator, raw_path = record.partition(b"\t")
            fields = header.split(b" ")
            if not separator or len(fields) != 3:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            try:
                mode = fields[0].decode("ascii")
                object_type = fields[1].decode("ascii")
                object_id = fields[2].decode("ascii").lower()
            except UnicodeDecodeError as error:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                ) from error

            if mode not in {"100644", "100755"} or object_type != "blob":
                raise TestDependencySourceError(
                    TestDependencySourceFailure.UNSUPPORTED_TREE_ENTRY
                )
            if not raw_path.endswith(b".py"):
                continue
            if len(entries) >= self._max_python_files:
                raise TestDependencySourceError(TestDependencySourceFailure.LIMIT_EXCEEDED)
            try:
                path = raw_path.decode("utf-8", errors="strict")
            except UnicodeDecodeError as error:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.INVALID_PATH
                ) from error

            if not self._is_safe_relative_python_path(path):
                raise TestDependencySourceError(TestDependencySourceFailure.INVALID_PATH)
            if path in seen_paths:
                raise TestDependencySourceError(TestDependencySourceFailure.INVALID_PATH)
            seen_paths.add(path)
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", object_id):
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            entries.append(
                _GitTreeEntry(
                    mode=mode,
                    object_type=object_type,
                    object_id=object_id,
                    path=path,
                )
            )
        return tuple(entries)

    def _read_python_sources(
        self, root: Path, entries: tuple[_GitTreeEntry, ...], deadline: float
    ) -> list[PythonSource]:
        if not entries:
            return []

        object_ids = tuple(entry.object_id for entry in entries)
        batch_input = "".join(f"{object_id}\n" for object_id in object_ids).encode("ascii")
        output_limit = (
            self._max_total_source_bytes
            + self._max_python_files * self._CAT_FILE_HEADER_BYTES_PER_OBJECT
            + 1
        )
        batch_output = self._run_git(
            root,
            ("cat-file", "--batch"),
            max_stdout_bytes=output_limit,
            deadline=deadline,
            input_bytes=batch_input,
        )

        sources: list[PythonSource] = []
        offset = 0
        total_source_bytes = 0
        for entry in entries:
            header_end = batch_output.find(b"\n", offset)
            if header_end < 0:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            header = batch_output[offset:header_end].split(b" ")
            if len(header) != 3:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            try:
                returned_id = header[0].decode("ascii").lower()
                object_type = header[1].decode("ascii")
                blob_size = int(header[2].decode("ascii"))
            except (UnicodeDecodeError, ValueError) as error:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                ) from error

            if returned_id != entry.object_id or object_type != "blob" or blob_size < 0:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            if blob_size > self._max_blob_bytes:
                raise TestDependencySourceError(TestDependencySourceFailure.LIMIT_EXCEEDED)
            total_source_bytes += blob_size
            if total_source_bytes > self._max_total_source_bytes:
                raise TestDependencySourceError(TestDependencySourceFailure.LIMIT_EXCEEDED)

            blob_start = header_end + 1
            blob_end = blob_start + blob_size
            if blob_end >= len(batch_output) or batch_output[blob_end : blob_end + 1] != b"\n":
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )
            try:
                source_text = batch_output[blob_start:blob_end].decode("utf-8", errors="strict")
            except UnicodeDecodeError as error:
                raise TestDependencySourceError(
                    TestDependencySourceFailure.INVALID_UTF8
                ) from error
            sources.append(PythonSource(source_ref=entry.path, source_text=source_text))
            offset = blob_end + 1

        if offset != len(batch_output):
            raise TestDependencySourceError(TestDependencySourceFailure.GIT_COMMAND_FAILED)
        return sources

    @staticmethod
    def _is_safe_relative_python_path(path: str) -> bool:
        posix_path = PurePosixPath(path)
        windows_path = PureWindowsPath(path)
        if (
            not path
            or not path.endswith(".py")
            or path.startswith("/")
            or "\\" in path
            or posix_path.is_absolute()
            or windows_path.is_absolute()
            or bool(windows_path.drive)
            or any(part in {"", ".", ".."} for part in path.split("/"))
        ):
            return False
        if any(
            ord(character) < 32 or character in '<>:"|?*'
            for component in path.split("/")
            for character in component
        ):
            return False
        if any(component.endswith((".", " ")) for component in path.split("/")):
            return False
        return True

    @staticmethod
    def _run_git(
        root: Path,
        arguments: tuple[str, ...],
        *,
        max_stdout_bytes: int,
        deadline: float,
        input_bytes: bytes | None = None,
    ) -> bytes:
        if max_stdout_bytes <= 0:
            raise ValueError("max_stdout_bytes must be positive")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TestDependencySourceError(TestDependencySourceFailure.GIT_COMMAND_TIMEOUT)
        try:
            process: subprocess.Popen[bytes] = subprocess.Popen(
                ("git", "--no-replace-objects", "-C", str(root), *arguments),
                stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except OSError as error:
            raise TestDependencySourceError(
                TestDependencySourceFailure.GIT_COMMAND_FAILED
            ) from error

        stdout = process.stdout
        if stdout is None:
            process.kill()
            process.wait()
            raise TestDependencySourceError(TestDependencySourceFailure.GIT_COMMAND_FAILED)

        output_parts: list[bytes] = []
        output_size = [0]
        output_too_large = threading.Event()
        read_errors: list[OSError] = []
        write_errors: list[OSError] = []

        def drain_stdout() -> None:
            try:
                while True:
                    chunk = stdout.read(64 * 1024)
                    if not chunk:
                        return
                    next_size = output_size[0] + len(chunk)
                    if next_size > max_stdout_bytes:
                        output_too_large.set()
                        try:
                            process.kill()
                        except OSError:
                            pass
                        return
                    output_parts.append(chunk)
                    output_size[0] = next_size
            except OSError as error:
                read_errors.append(error)

        reader = threading.Thread(target=drain_stdout, daemon=True)
        reader.start()

        writer: threading.Thread | None = None
        if input_bytes is not None:
            stdin = process.stdin
            if stdin is None:
                process.kill()
                process.wait()
                raise TestDependencySourceError(
                    TestDependencySourceFailure.GIT_COMMAND_FAILED
                )

            def write_stdin() -> None:
                try:
                    stdin.write(input_bytes)
                    stdin.flush()
                except OSError as error:
                    write_errors.append(error)
                finally:
                    try:
                        stdin.close()
                    except OSError as error:
                        write_errors.append(error)

            writer = threading.Thread(target=write_stdin, daemon=True)
            writer.start()

        timed_out = False
        try:
            process.wait(timeout=max(0.001, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                process.kill()
            except OSError:
                pass
            process.wait()
        reader.join()
        if writer is not None:
            writer.join()
        stdout.close()

        if timed_out:
            raise TestDependencySourceError(TestDependencySourceFailure.GIT_COMMAND_TIMEOUT)
        if output_too_large.is_set():
            raise TestDependencySourceError(TestDependencySourceFailure.LIMIT_EXCEEDED)
        if read_errors or write_errors or process.returncode != 0:
            raise TestDependencySourceError(TestDependencySourceFailure.GIT_COMMAND_FAILED)
        return b"".join(output_parts)


__all__ = [
    "GitPinnedTestDependencyInventory",
    "GitTestDependencySourceAdapter",
    "TestDependencySourceError",
    "TestDependencySourceFailure",
]
