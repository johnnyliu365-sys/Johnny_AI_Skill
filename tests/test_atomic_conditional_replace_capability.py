"""Executable capability evidence for atomic conditional target replacement.

This file is deliberately test-only.  It never exports an adapter and performs all
filesystem effects inside pytest-provided disposable directories.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ctypes
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import textwrap
import threading
from typing import Callable

import pytest

from library.local_orchestration.target_document_management import (
    TargetWorkspace,
    TransactionalTargetDocumentWriter,
)
from library.workflow_router.target_document_contracts import (
    ArtifactDocumentKind,
    DocumentMutationMode,
    DocumentWriteStatus,
    TargetDocumentMutation,
    TargetDocumentPlan,
    derive_document_digest,
)


_TICKET_AUTHORITY_BASELINE = "6953f1e49bc60e66a5f8a2ce9cfd879f0d606ece"
_ALLOWED_CANDIDATE_PATHS = frozenset(
    {"tests/test_atomic_conditional_replace_capability.py"}
)


class QualificationSubject(Enum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    PYTHON_FILESYSTEM_ABSTRACTION = "PYTHON_FILESYSTEM_ABSTRACTION"


class QualificationStatus(Enum):
    YES = "YES"
    NO = "NO"
    CONDITIONAL = "CONDITIONAL"


class NativePrimitive(Enum):
    NONE = "NONE"
    WINDOWS_MOVE_FILE_EXW = "MoveFileExW(MOVEFILE_REPLACE_EXISTING)"
    LINUX_RENAMEAT2_NOREPLACE = "renameat2(RENAME_NOREPLACE)"


class RaceModel(Enum):
    EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION = (
        "EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION"
    )


class FinalWindowObservation(Enum):
    EXTERNAL_BYTES_OVERWRITTEN = "EXTERNAL_BYTES_OVERWRITTEN"
    EXTERNAL_BYTES_PRESERVED = "EXTERNAL_BYTES_PRESERVED"
    PRIMITIVE_NOT_EXECUTED = "PRIMITIVE_NOT_EXECUTED"


class FailureSemantics(Enum):
    FINAL_WINDOW_NOT_CONDITIONAL = "FINAL_WINDOW_NOT_CONDITIONAL"
    PRECONDITION_MISMATCH_NO_EFFECT = "PRECONDITION_MISMATCH_NO_EFFECT"
    PRIMITIVE_UNAVAILABLE_NO_EFFECT = "PRIMITIVE_UNAVAILABLE_NO_EFFECT"


class RuntimeConstraint(Enum):
    EXACT_LINUX_KERNEL_AND_FILESYSTEM = "EXACT_LINUX_KERNEL_AND_FILESYSTEM"
    TARGET_ABSENT_AT_FINAL_MUTATION = "TARGET_ABSENT_AT_FINAL_MUTATION"


@dataclass(frozen=True, slots=True)
class PlatformBackendTuple:
    """A bounded identity rather than a host path or a raw platform report."""

    subject: QualificationSubject
    platform_identity: str
    filesystem_backend: str

    def __post_init__(self) -> None:
        if type(self.subject) is not QualificationSubject:
            raise TypeError("subject must be a qualification subject")
        _validate_bounded_platform_identity(self.platform_identity)
        _validate_bounded_label(self.filesystem_backend)


@dataclass(frozen=True, slots=True)
class OpaqueEvidenceRef:
    """A digest reference that deliberately cannot reveal fixture data or a path."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or re.fullmatch(
            r"sha256:[0-9a-f]{64}", self.value
        ) is None:
            raise ValueError("evidence reference must be an opaque sha256 digest")


@dataclass(frozen=True, slots=True)
class AtomicConditionalReplaceQualification:
    """The complete, finite result for exactly one capability subject."""

    subject: QualificationSubject
    status: QualificationStatus
    platform_backend: PlatformBackendTuple
    native_primitive: NativePrimitive
    race_model: RaceModel
    final_window_observation: FinalWindowObservation
    failure_semantics: FailureSemantics
    evidence_ref: OpaqueEvidenceRef
    runtime_constraints: tuple[RuntimeConstraint, ...] = ()

    def __post_init__(self) -> None:
        if type(self.subject) is not QualificationSubject:
            raise TypeError("qualification subject is required")
        if type(self.status) is not QualificationStatus:
            raise TypeError("qualification status is required")
        if type(self.platform_backend) is not PlatformBackendTuple:
            raise TypeError("platform/backend tuple is required")
        if self.platform_backend.subject is not self.subject:
            raise ValueError("platform/backend subject must match qualification subject")
        if type(self.native_primitive) is not NativePrimitive:
            raise TypeError("native primitive is required")
        if type(self.race_model) is not RaceModel:
            raise TypeError("bounded race model is required")
        if type(self.final_window_observation) is not FinalWindowObservation:
            raise TypeError("final-window observation is required")
        if type(self.failure_semantics) is not FailureSemantics:
            raise TypeError("finite failure semantics are required")
        if type(self.evidence_ref) is not OpaqueEvidenceRef:
            raise TypeError("opaque evidence reference is required")
        if type(self.runtime_constraints) is not tuple or any(
            type(constraint) is not RuntimeConstraint
            for constraint in self.runtime_constraints
        ):
            raise TypeError("runtime constraints must be a typed tuple")
        if self.native_primitive is NativePrimitive.NONE:
            if self.subject is not QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION:
                raise ValueError("NONE primitive belongs only to the Python abstraction")
        elif self.native_primitive is NativePrimitive.WINDOWS_MOVE_FILE_EXW:
            if self.subject is not QualificationSubject.WINDOWS:
                raise ValueError("MoveFileExW belongs only to the Windows subject")
        elif self.native_primitive is NativePrimitive.LINUX_RENAMEAT2_NOREPLACE:
            if self.subject is not QualificationSubject.LINUX:
                raise ValueError("renameat2 belongs only to the Linux subject")
        else:
            raise TypeError("native primitive is unsupported")

        if self.status is QualificationStatus.YES:
            if self.native_primitive is NativePrimitive.NONE:
                raise ValueError("YES requires a real native primitive")
            if self.runtime_constraints:
                raise ValueError("YES cannot advertise conditional constraints")
            if (
                self.final_window_observation
                is not FinalWindowObservation.EXTERNAL_BYTES_PRESERVED
                or self.failure_semantics
                is not FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT
            ):
                raise ValueError("YES requires preserved final-window mismatch semantics")
        elif self.status is QualificationStatus.CONDITIONAL:
            expected_constraints = (
                RuntimeConstraint.EXACT_LINUX_KERNEL_AND_FILESYSTEM,
                RuntimeConstraint.TARGET_ABSENT_AT_FINAL_MUTATION,
            )
            if self.subject is not QualificationSubject.LINUX:
                raise ValueError("CONDITIONAL belongs only to the Linux subject")
            if self.native_primitive is not NativePrimitive.LINUX_RENAMEAT2_NOREPLACE:
                raise ValueError("CONDITIONAL requires the Linux renameat2 primitive")
            if self.runtime_constraints != expected_constraints:
                raise ValueError("CONDITIONAL requires the exact Linux constraint tuple")
            if (
                self.final_window_observation
                is not FinalWindowObservation.EXTERNAL_BYTES_PRESERVED
                or self.failure_semantics
                is not FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT
            ):
                raise ValueError(
                    "CONDITIONAL requires preserved final-window mismatch semantics"
                )
        elif self.status is QualificationStatus.NO:
            if self.runtime_constraints:
                raise ValueError("NO cannot advertise a runtime capability")
            if (
                self.final_window_observation
                is FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN
                and self.failure_semantics
                is FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL
            ):
                return
            if (
                self.final_window_observation
                is FinalWindowObservation.PRIMITIVE_NOT_EXECUTED
                and self.failure_semantics
                is FailureSemantics.PRIMITIVE_UNAVAILABLE_NO_EFFECT
            ):
                return
            raise ValueError("NO has contradictory final-window failure semantics")
        else:
            raise TypeError("qualification status is unsupported")


@dataclass(frozen=True, slots=True)
class _FileIdentity:
    device: int
    inode: int
    size: int
    modified_ns: int


class _PlatformProofUnavailable(RuntimeError):
    def __init__(
        self,
        subject: QualificationSubject,
        missing_capability: str = "EXACT_PLATFORM_BACKEND",
    ) -> None:
        super().__init__(subject.value)
        self.subject = subject
        self.missing_capability = missing_capability


def _validate_bounded_label(value: str) -> None:
    if type(value) is not str or not value or len(value) > 160:
        raise ValueError("identity fields must be present and bounded")
    if re.fullmatch(r"[A-Za-z0-9._:+()=-]+", value) is None:
        raise ValueError("identity fields must not contain paths or raw bodies")


def _validate_bounded_platform_identity(value: str) -> None:
    if type(value) is not str or not value or len(value) > 160:
        raise ValueError("platform identity must be present and bounded")
    if re.fullmatch(r"[A-Za-z0-9._:+()=/-]+", value) is None:
        raise ValueError("platform identity must not contain raw bodies")
    mount_marker = ":mount:/mnt/"
    if mount_marker in value and re.search(r":mount:/mnt/[A-Za-z]$", value) is None:
        raise ValueError("platform identity must not disclose a worktree path")


def _opaque_evidence_ref(*parts: str) -> OpaqueEvidenceRef:
    for part in parts:
        _validate_bounded_label(part)
    digest = hashlib.sha256("|".join(parts).encode("ascii")).hexdigest()
    return OpaqueEvidenceRef(f"sha256:{digest}")


def _identity(path: Path) -> _FileIdentity:
    state = path.stat()
    return _FileIdentity(
        device=state.st_dev,
        inode=state.st_ino,
        size=state.st_size,
        modified_ns=state.st_mtime_ns,
    )


def _git(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise RuntimeError("disposable Git fixture setup failed")
    return completed.stdout.strip()


def _git_bytes(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=False,
        capture_output=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise RuntimeError("Git candidate-diff inspection failed")
    return completed.stdout


def _git_path_set(repository: Path, *arguments: str) -> frozenset[str]:
    return frozenset(
        item.decode("utf-8")
        for item in _git_bytes(repository, *arguments).split(b"\0")
        if item
    )


def _candidate_change_paths(repository: Path) -> frozenset[str]:
    ancestry = subprocess.run(
        (
            "git",
            "-C",
            str(repository),
            "merge-base",
            "--is-ancestor",
            _TICKET_AUTHORITY_BASELINE,
            "HEAD",
        ),
        check=False,
        capture_output=True,
        timeout=20,
    )
    if ancestry.returncode != 0:
        raise RuntimeError("ticket authority baseline is not an ancestor of candidate")
    committed = _git_path_set(
        repository,
        "diff",
        "--name-only",
        "-z",
        "--no-renames",
        _TICKET_AUTHORITY_BASELINE,
        "HEAD",
    )
    staged = _git_path_set(
        repository,
        "diff",
        "--cached",
        "--name-only",
        "-z",
        "--no-renames",
    )
    unstaged = _git_path_set(
        repository,
        "diff",
        "--name-only",
        "-z",
        "--no-renames",
    )
    untracked = _git_path_set(
        repository,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
    )
    return committed | staged | unstaged | untracked


def _assert_exact_candidate_boundary(repository: Path) -> None:
    assert _candidate_change_paths(repository) == _ALLOWED_CANDIDATE_PATHS


def _disposable_repository(root: Path) -> str:
    _git(root, "init")
    _git(root, "config", "user.email", "capability@example.invalid")
    _git(root, "config", "user.name", "Capability Probe")
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-m", "fixture")
    return _git(root, "rev-parse", "HEAD")


def _windows_filesystem_backend(directory: Path) -> str:
    if platform.system() != "Windows":
        raise _PlatformProofUnavailable(QualificationSubject.WINDOWS)
    root = directory.anchor
    if not root:
        raise _PlatformProofUnavailable(QualificationSubject.WINDOWS)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    filesystem_name = ctypes.create_unicode_buffer(260)
    volume_serial = ctypes.c_uint32()
    maximum_component_length = ctypes.c_uint32()
    filesystem_flags = ctypes.c_uint32()
    success = kernel32.GetVolumeInformationW(
        root,
        None,
        0,
        ctypes.byref(volume_serial),
        ctypes.byref(maximum_component_length),
        ctypes.byref(filesystem_flags),
        filesystem_name,
        len(filesystem_name),
    )
    if not success or not filesystem_name.value:
        raise _PlatformProofUnavailable(QualificationSubject.WINDOWS)
    return f"windows-fs:{filesystem_name.value.upper()}"


def _windows_platform_tuple(directory: Path) -> PlatformBackendTuple:
    if platform.system() != "Windows":
        raise _PlatformProofUnavailable(QualificationSubject.WINDOWS)
    release, version, _, _ = platform.win32_ver()
    version_identity = version or platform.version()
    return PlatformBackendTuple(
        subject=QualificationSubject.WINDOWS,
        platform_identity=f"windows:{release}:{version_identity}",
        filesystem_backend=_windows_filesystem_backend(directory),
    )


def _move_file_ex_replace(source: Path, destination: Path) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file_ex = kernel32.MoveFileExW
    move_file_ex.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    move_file_ex.restype = ctypes.c_int
    movefile_replace_existing = 0x00000001
    if not move_file_ex(str(source), str(destination), movefile_replace_existing):
        raise OSError(ctypes.get_last_error(), "MoveFileExW unavailable")


def _classify_final_window(
    observation: FinalWindowObservation,
) -> QualificationStatus:
    if observation is FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN:
        return QualificationStatus.NO
    raise AssertionError("only an overwrite observation is a NO proof")


def _qualify_windows_movefileex() -> AtomicConditionalReplaceQualification:
    if platform.system() != "Windows":
        raise _PlatformProofUnavailable(QualificationSubject.WINDOWS)
    with tempfile.TemporaryDirectory(prefix="cap-rww6-win-") as temporary_directory:
        root = Path(temporary_directory)
        platform_backend = _windows_platform_tuple(root)
        destination = root / "target.txt"
        candidate = root / "candidate.txt"
        external_candidate = root / "external.txt"
        destination.write_bytes(b"observed")
        candidate.write_bytes(b"candidate")
        external_candidate.write_bytes(b"external")
        observed_identity = _identity(destination)
        release_external = threading.Event()
        external_finished = threading.Event()

        def external_writer() -> None:
            if not release_external.wait(timeout=5):
                return
            os.replace(external_candidate, destination)
            external_finished.set()

        writer = threading.Thread(target=external_writer)
        writer.start()
        release_external.set()
        if not external_finished.wait(timeout=5):
            writer.join(timeout=5)
            raise RuntimeError("final-window external writer did not finish")
        external_identity = _identity(destination)
        if external_identity == observed_identity:
            writer.join(timeout=5)
            raise RuntimeError("external replacement did not change the observed identity")
        try:
            _move_file_ex_replace(candidate, destination)
        except OSError:
            writer.join(timeout=5)
            if writer.is_alive():
                raise RuntimeError("final-window external writer did not terminate")
            if destination.read_bytes() != b"external":
                raise RuntimeError("unavailable primitive changed disposable target")
            return AtomicConditionalReplaceQualification(
                subject=QualificationSubject.WINDOWS,
                status=QualificationStatus.NO,
                platform_backend=platform_backend,
                native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
                race_model=(
                    RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
                ),
                final_window_observation=FinalWindowObservation.PRIMITIVE_NOT_EXECUTED,
                failure_semantics=FailureSemantics.PRIMITIVE_UNAVAILABLE_NO_EFFECT,
                evidence_ref=_opaque_evidence_ref(
                    "windows",
                    "movefileexw",
                    "primitive-unavailable",
                ),
            )
        writer.join(timeout=5)
        if writer.is_alive():
            raise RuntimeError("final-window external writer did not terminate")
        if destination.read_bytes() != b"candidate":
            raise RuntimeError("MoveFileExW reproduction did not reach final mutation")
        observation = FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN
        return AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=_classify_final_window(observation),
            platform_backend=platform_backend,
            native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=observation,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=_opaque_evidence_ref(
                "windows",
                "movefileexw",
                "external-overwritten",
            ),
        )


def _linux_filesystem_backend(directory: Path) -> str:
    completed = subprocess.run(
        ("stat", "-f", "-c", "%T", str(directory)),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    filesystem = completed.stdout.strip().lower()
    if completed.returncode != 0 or not filesystem:
        raise _PlatformProofUnavailable(QualificationSubject.LINUX)
    return f"linux-fs:{filesystem}"


def _linux_platform_tuple(directory: Path) -> PlatformBackendTuple:
    if platform.system() != "Linux":
        raise _PlatformProofUnavailable(QualificationSubject.LINUX)
    return PlatformBackendTuple(
        subject=QualificationSubject.LINUX,
        platform_identity=f"linux:{platform.release()}",
        filesystem_backend=_linux_filesystem_backend(directory),
    )


def _renameat2_noreplace(source: Path, destination: Path) -> int:
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        renameat2 = libc.renameat2
    except AttributeError:
        return -1
    renameat2.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    renameat2.restype = ctypes.c_int
    at_fdcwd = -100
    rename_noreplace = 1
    result = renameat2(
        at_fdcwd,
        os.fsencode(source),
        at_fdcwd,
        os.fsencode(destination),
        rename_noreplace,
    )
    if result == 0:
        return 0
    return ctypes.get_errno() or -1


def _qualify_linux_renameat2() -> AtomicConditionalReplaceQualification:
    if platform.system() != "Linux":
        raise _PlatformProofUnavailable(QualificationSubject.LINUX)
    with tempfile.TemporaryDirectory(prefix="cap-rww6-linux-") as temporary_directory:
        root = Path(temporary_directory)
        platform_backend = _linux_platform_tuple(root)
        positive_source = root / "positive-source.txt"
        positive_target = root / "positive-target.txt"
        positive_source.write_bytes(b"candidate")
        positive_result = _renameat2_noreplace(positive_source, positive_target)
        if positive_result != 0 or positive_target.read_bytes() != b"candidate":
            return AtomicConditionalReplaceQualification(
                subject=QualificationSubject.LINUX,
                status=QualificationStatus.NO,
                platform_backend=platform_backend,
                native_primitive=NativePrimitive.LINUX_RENAMEAT2_NOREPLACE,
                race_model=(
                    RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
                ),
                final_window_observation=FinalWindowObservation.PRIMITIVE_NOT_EXECUTED,
                failure_semantics=FailureSemantics.PRIMITIVE_UNAVAILABLE_NO_EFFECT,
                evidence_ref=_opaque_evidence_ref(
                    "linux",
                    "renameat2",
                    "primitive-unavailable",
                ),
            )
        candidate = root / "candidate.txt"
        destination = root / "target.txt"
        external_candidate = root / "external.txt"
        candidate.write_bytes(b"candidate")
        external_candidate.write_bytes(b"external")
        if destination.exists():
            raise RuntimeError("disposable final-window target must begin absent")
        os.replace(external_candidate, destination)
        negative_result = _renameat2_noreplace(candidate, destination)
        if negative_result == 0 or destination.read_bytes() != b"external":
            raise RuntimeError("renameat2 did not fail closed on a final-window mismatch")
        return AtomicConditionalReplaceQualification(
            subject=QualificationSubject.LINUX,
            status=QualificationStatus.CONDITIONAL,
            platform_backend=platform_backend,
            native_primitive=NativePrimitive.LINUX_RENAMEAT2_NOREPLACE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT,
            evidence_ref=_opaque_evidence_ref(
                "linux",
                "renameat2",
                "target-absent-constraint",
            ),
            runtime_constraints=(
                RuntimeConstraint.EXACT_LINUX_KERNEL_AND_FILESYSTEM,
                RuntimeConstraint.TARGET_ABSENT_AT_FINAL_MUTATION,
            ),
        )


_WSL_LINUX_PROOF_SCRIPT = textwrap.dedent(
    r"""
    import ctypes
    import hashlib
    import json
    import os
    import platform
    import tempfile
    import threading

    RACE_MODEL = "EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION"

    def mount_identity() -> tuple[str, str]:
        current = os.path.realpath(os.getcwd())
        selected = None
        with open("/proc/self/mountinfo", "r", encoding="utf-8") as mountinfo:
            for line in mountinfo:
                before, separator, after = line.rstrip("\n").partition(" - ")
                if not separator:
                    continue
                fields = before.split()
                filesystem = after.split()
                if len(fields) < 5 or len(filesystem) < 2:
                    continue
                mountpoint = fields[4].replace("\\040", " ")
                if current == mountpoint or current.startswith(mountpoint.rstrip("/") + "/"):
                    if selected is None or len(mountpoint) > len(selected[0]):
                        selected = (mountpoint, filesystem[0], filesystem[1])
        if selected is None:
            raise RuntimeError("mount identity unavailable")
        mountpoint, filesystem_type, source = selected
        if mountpoint != "/mnt/c":
            raise RuntimeError("proof is not on the Windows worktree mount")
        return (
            "linux:" + platform.release() + ":mount:" + mountpoint,
            "linux-fs:" + filesystem_type + ":wsl-drvfs-mnt-c",
        )

    def evidence(*parts: str) -> str:
        return "sha256:" + hashlib.sha256("|".join(parts).encode("ascii")).hexdigest()

    def emit(
        status: str,
        primitive: str,
        observation: str,
        failure: str,
        constraints: list[str],
        platform_identity: str,
        filesystem_backend: str,
    ) -> None:
        payload = {
            "subject": "LINUX",
            "status": status,
            "platform_identity": platform_identity,
            "filesystem_backend": filesystem_backend,
            "native_primitive": primitive,
            "race_model": RACE_MODEL,
            "final_window_observation": observation,
            "failure_semantics": failure,
            "runtime_constraints": constraints,
            "evidence_ref": evidence("linux", primitive, observation, failure),
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    def renameat2_noreplace(source: str, destination: str) -> int:
        try:
            libc = ctypes.CDLL(None, use_errno=True)
            renameat2 = libc.renameat2
        except (AttributeError, OSError):
            return -1
        renameat2.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        result = renameat2(
            -100,
            os.fsencode(source),
            -100,
            os.fsencode(destination),
            1,
        )
        if result == 0:
            return 0
        return ctypes.get_errno() or -1

    if platform.system() != "Linux":
        raise RuntimeError("WSL Python is not Linux")
    platform_identity, filesystem_backend = mount_identity()
    with tempfile.TemporaryDirectory(prefix="cap-rww6-linux-", dir=os.getcwd()) as root:
        positive_source = os.path.join(root, "positive-source")
        positive_target = os.path.join(root, "positive-target")
        with open(positive_source, "wb") as output:
            output.write(b"candidate")
        if renameat2_noreplace(positive_source, positive_target) != 0:
            emit(
                "NO",
                "renameat2(RENAME_NOREPLACE)",
                "PRIMITIVE_NOT_EXECUTED",
                "PRIMITIVE_UNAVAILABLE_NO_EFFECT",
                [],
                platform_identity,
                filesystem_backend,
            )
        else:
            candidate = os.path.join(root, "candidate")
            destination = os.path.join(root, "target")
            external = os.path.join(root, "external")
            with open(candidate, "wb") as output:
                output.write(b"candidate")
            with open(external, "wb") as output:
                output.write(b"external")
            try:
                os.lstat(destination)
                raise RuntimeError("final target must begin absent")
            except FileNotFoundError:
                pass
            release_external = threading.Event()
            external_finished = threading.Event()
            def external_writer() -> None:
                if release_external.wait(timeout=5):
                    os.replace(external, destination)
                    external_finished.set()
            writer = threading.Thread(target=external_writer)
            writer.start()
            release_external.set()
            if not external_finished.wait(timeout=5):
                raise RuntimeError("external final-window actor unavailable")
            result = renameat2_noreplace(candidate, destination)
            writer.join(timeout=5)
            if writer.is_alive():
                raise RuntimeError("external final-window actor did not terminate")
            with open(destination, "rb") as observed:
                external_preserved = observed.read() == b"external"
            if result != 0 and external_preserved:
                emit(
                    "CONDITIONAL",
                    "renameat2(RENAME_NOREPLACE)",
                    "EXTERNAL_BYTES_PRESERVED",
                    "PRECONDITION_MISMATCH_NO_EFFECT",
                    [
                        "EXACT_LINUX_KERNEL_AND_FILESYSTEM",
                        "TARGET_ABSENT_AT_FINAL_MUTATION",
                    ],
                    platform_identity,
                    filesystem_backend,
                )
            else:
                emit(
                    "NO",
                    "renameat2(RENAME_NOREPLACE)",
                    "EXTERNAL_BYTES_OVERWRITTEN",
                    "FINAL_WINDOW_NOT_CONDITIONAL",
                    [],
                    platform_identity,
                    filesystem_backend,
                )
    """
)


def _json_object(raw: str) -> dict[str, object]:
    parsed: object = json.loads(raw)
    if type(parsed) is not dict:
        raise ValueError("WSL proof result must be an object")
    object_result: dict[str, object] = {}
    for key, value in parsed.items():
        if type(key) is not str:
            raise ValueError("WSL proof result keys must be strings")
        object_result[key] = value
    return object_result


def _json_string(payload: dict[str, object], field: str) -> str:
    value = payload.get(field)
    if type(value) is not str:
        raise ValueError("WSL proof result has an invalid scalar field")
    return value


def _wsl_linux_qualification(worktree: Path) -> AtomicConditionalReplaceQualification:
    if worktree.drive.upper() != "C:" or not worktree.is_absolute():
        raise _PlatformProofUnavailable(
            QualificationSubject.LINUX,
            "WSL_UBUNTU_DRVFS_WORKTREE",
        )
    wsl_worktree = "/mnt/c/" + "/".join(worktree.parts[1:])
    completed = subprocess.run(
        (
            "wsl.exe",
            "-d",
            "Ubuntu",
            "--cd",
            wsl_worktree,
            "--",
            "python3",
            "-c",
            _WSL_LINUX_PROOF_SCRIPT,
        ),
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )
    if completed.returncode != 0:
        raise _PlatformProofUnavailable(
            QualificationSubject.LINUX,
            "WSL_UBUNTU_PYTHON3_RENAMEAT2_EXECUTION",
        )
    try:
        payload = _json_object(completed.stdout.strip())
        expected_fields = {
            "subject",
            "status",
            "platform_identity",
            "filesystem_backend",
            "native_primitive",
            "race_model",
            "final_window_observation",
            "failure_semantics",
            "runtime_constraints",
            "evidence_ref",
        }
        if set(payload) != expected_fields:
            raise ValueError("WSL proof result has an invalid field set")
        raw_constraints = payload["runtime_constraints"]
        if type(raw_constraints) is not list:
            raise ValueError("WSL proof constraints must be a list")
        constraints = tuple(
            RuntimeConstraint(_json_list_string(raw_constraints, index))
            for index in range(len(raw_constraints))
        )
        return AtomicConditionalReplaceQualification(
            subject=QualificationSubject(_json_string(payload, "subject")),
            status=QualificationStatus(_json_string(payload, "status")),
            platform_backend=PlatformBackendTuple(
                subject=QualificationSubject(_json_string(payload, "subject")),
                platform_identity=_json_string(payload, "platform_identity"),
                filesystem_backend=_json_string(payload, "filesystem_backend"),
            ),
            native_primitive=NativePrimitive(_json_string(payload, "native_primitive")),
            race_model=RaceModel(_json_string(payload, "race_model")),
            final_window_observation=FinalWindowObservation(
                _json_string(payload, "final_window_observation")
            ),
            failure_semantics=FailureSemantics(
                _json_string(payload, "failure_semantics")
            ),
            evidence_ref=OpaqueEvidenceRef(_json_string(payload, "evidence_ref")),
            runtime_constraints=constraints,
        )
    except (TypeError, ValueError):
        raise _PlatformProofUnavailable(
            QualificationSubject.LINUX,
            "WSL_LINUX_PROOF_METADATA_VALIDATION",
        ) from None


def _json_list_string(values: list[object], index: int) -> str:
    value = values[index]
    if type(value) is not str:
        raise ValueError("WSL proof constraint must be a string")
    return value


def _qualify_exact_linux_subject(worktree: Path) -> AtomicConditionalReplaceQualification:
    if platform.system() == "Linux":
        return _qualify_linux_renameat2()
    if platform.system() == "Windows":
        return _wsl_linux_qualification(worktree)
    raise _PlatformProofUnavailable(QualificationSubject.LINUX, "LINUX_KERNEL")


def _current_python_platform_tuple(directory: Path) -> PlatformBackendTuple:
    if platform.system() == "Windows":
        backend = _windows_filesystem_backend(directory)
    elif platform.system() == "Linux":
        backend = _linux_filesystem_backend(directory)
    else:
        backend = f"device:{directory.stat().st_dev:x}"
    return PlatformBackendTuple(
        subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
        platform_identity=(
            f"cpython:{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ),
        filesystem_backend=backend,
    )


def _qualify_current_python_abstraction(repository: Path) -> AtomicConditionalReplaceQualification:
    baseline = _disposable_repository(repository)
    target = repository / "modules" / "probe.txt"
    external_candidate = repository / "external.txt"
    mutation = TargetDocumentMutation(
        path="modules/probe.txt",
        artifact_kind=ArtifactDocumentKind.HANDOFF_INDEX,
        mode=DocumentMutationMode.CREATE,
        expected_current_digest=None,
        content="candidate\n",
        content_digest=derive_document_digest("candidate\n"),
        sealed=False,
    )
    plan = TargetDocumentPlan(
        project_id="prj_0123456789abcdef",
        baseline_commit=baseline,
        mutations=(mutation,),
    )
    final_window_entered = threading.Event()

    def final_window_audit(event: str, arguments: tuple[object, ...]) -> None:
        if event != "os.rename" or final_window_entered.is_set():
            return
        if len(arguments) < 2 or type(arguments[1]) is not str:
            return
        if Path(arguments[1]) != target:
            return
        final_window_entered.set()
        external_candidate.write_bytes(b"external")
        os.replace(external_candidate, target)

    sys.addaudithook(final_window_audit)
    result = TransactionalTargetDocumentWriter(TargetWorkspace(repository)).apply(plan)
    if not final_window_entered.is_set():
        raise RuntimeError("ordinary replace did not expose its final mutation audit boundary")
    if result.status is not DocumentWriteStatus.APPLIED:
        raise RuntimeError("current abstraction did not complete disposable ordinary replace")
    if target.read_bytes() != b"candidate\n":
        raise RuntimeError("ordinary replace did not overwrite final-window external bytes")
    observation = FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN
    return AtomicConditionalReplaceQualification(
        subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
        status=_classify_final_window(observation),
        platform_backend=_current_python_platform_tuple(repository),
        native_primitive=NativePrimitive.NONE,
        race_model=(
            RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
        ),
        final_window_observation=observation,
        failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
        evidence_ref=_opaque_evidence_ref(
            "cpython",
            "ordinary-replace",
            "external-overwritten",
        ),
    )


def _destination_identity_at_final_decision(destination: Path) -> _FileIdentity | None:
    try:
        state = destination.lstat()
    except FileNotFoundError:
        return None
    return _FileIdentity(
        device=state.st_dev,
        inode=state.st_ino,
        size=state.st_size,
        modified_ns=state.st_mtime_ns,
    )


def _test_only_final_conditional_probe(
    runtime_constraints: tuple[RuntimeConstraint, ...],
    qualified_platform_backend: PlatformBackendTuple,
    observed_platform_backend: PlatformBackendTuple,
    destination: Path,
) -> bool:
    expected_constraints = (
        RuntimeConstraint.EXACT_LINUX_KERNEL_AND_FILESYSTEM,
        RuntimeConstraint.TARGET_ABSENT_AT_FINAL_MUTATION,
    )
    destination_identity = _destination_identity_at_final_decision(destination)
    if runtime_constraints != expected_constraints:
        return False
    if qualified_platform_backend.subject is not QualificationSubject.LINUX:
        return False
    if observed_platform_backend != qualified_platform_backend:
        return False
    if destination_identity is not None:
        return False
    return True


def _test_only_runtime_primitive(
    qualification: AtomicConditionalReplaceQualification,
) -> NativePrimitive:
    if qualification.status is QualificationStatus.NO:
        raise ValueError("NO is not a runtime capability")
    return qualification.native_primitive


def test_acr1_windows_movefileex_final_window_qualifies_no() -> None:
    qualification = _qualify_windows_movefileex()
    assert qualification.subject is QualificationSubject.WINDOWS
    assert qualification.status is QualificationStatus.NO
    assert qualification.native_primitive is NativePrimitive.WINDOWS_MOVE_FILE_EXW
    assert (
        qualification.final_window_observation
        is FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN
    )
    assert qualification.failure_semantics is FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL


def test_acr2_linux_requires_an_actual_linux_kernel_and_backend() -> None:
    worktree = Path(__file__).resolve().parents[1]
    qualification = _qualify_exact_linux_subject(worktree)
    assert qualification.subject is QualificationSubject.LINUX
    assert qualification.status in (
        QualificationStatus.NO,
        QualificationStatus.CONDITIONAL,
    )
    assert qualification.platform_backend.platform_identity.startswith("linux:")
    if platform.system() == "Windows":
        assert ":mount:/mnt/c" in qualification.platform_backend.platform_identity


def test_acr3_acm1_current_python_abstraction_final_window_qualifies_no(
    tmp_path: Path,
) -> None:
    qualification = _qualify_current_python_abstraction(tmp_path)
    assert qualification.subject is QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION
    assert qualification.status is QualificationStatus.NO
    assert qualification.native_primitive is NativePrimitive.NONE
    assert (
        qualification.final_window_observation
        is FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN
    )
    with pytest.raises(ValueError, match="not a runtime capability"):
        _test_only_runtime_primitive(qualification)


def test_acr4_acm2_typed_construction_rejects_incomplete_positive_claims() -> None:
    platform_backend = PlatformBackendTuple(
        subject=QualificationSubject.WINDOWS,
        platform_identity="windows:test-version",
        filesystem_backend="windows-fs:testfs",
    )
    python_platform_backend = PlatformBackendTuple(
        subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
        platform_identity="cpython:test-version",
        filesystem_backend="windows-fs:testfs",
    )
    evidence = _opaque_evidence_ref("validation", "typed", "fields")
    with pytest.raises(ValueError, match="real native primitive"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
            status=QualificationStatus.YES,
            platform_backend=python_platform_backend,
            native_primitive=NativePrimitive.NONE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="CONDITIONAL belongs only to the Linux subject"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.CONDITIONAL,
            platform_backend=platform_backend,
            native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError):
        QualificationStatus("UNSUPPORTED")
    constructor: Callable[..., AtomicConditionalReplaceQualification] = (
        AtomicConditionalReplaceQualification
    )
    with pytest.raises(TypeError):
        constructor()
    with pytest.raises(TypeError):
        constructor(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.NO,
            platform_backend=platform_backend,
            native_primitive=NativePrimitive.NONE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
            unexpected_field="forbidden",
        )
    with pytest.raises(TypeError, match="native primitive"):
        constructor(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.NO,
            platform_backend=platform_backend,
            native_primitive=None,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
        )


def test_acr5_acm3_conditional_tuple_and_destination_mismatches_have_no_effect(
    tmp_path: Path,
) -> None:
    runtime_constraints = (
        RuntimeConstraint.EXACT_LINUX_KERNEL_AND_FILESYSTEM,
        RuntimeConstraint.TARGET_ABSENT_AT_FINAL_MUTATION,
    )
    destination = tmp_path / "target.txt"
    qualified_platform_backend = PlatformBackendTuple(
        subject=QualificationSubject.LINUX,
        platform_identity="linux:kernel-a",
        filesystem_backend="linux-fs:backend-a",
    )
    different_kernel = PlatformBackendTuple(
        subject=QualificationSubject.LINUX,
        platform_identity="linux:kernel-b",
        filesystem_backend="linux-fs:backend-a",
    )
    different_filesystem = PlatformBackendTuple(
        subject=QualificationSubject.LINUX,
        platform_identity="linux:kernel-a",
        filesystem_backend="linux-fs:backend-b",
    )
    destination.write_bytes(b"external")
    assert not _test_only_final_conditional_probe(
        runtime_constraints,
        qualified_platform_backend,
        qualified_platform_backend,
        destination,
    )
    assert destination.read_bytes() == b"external"
    destination.unlink()
    assert not _test_only_final_conditional_probe(
        runtime_constraints,
        qualified_platform_backend,
        different_kernel,
        destination,
    )
    assert not destination.exists()
    assert not _test_only_final_conditional_probe(
        runtime_constraints,
        qualified_platform_backend,
        different_filesystem,
        destination,
    )
    assert not destination.exists()
    assert _test_only_final_conditional_probe(
        runtime_constraints,
        qualified_platform_backend,
        qualified_platform_backend,
        destination,
    )
    assert not destination.exists()
    parameters = inspect.signature(_test_only_final_conditional_probe).parameters
    assert "target_is_absent" not in parameters
    assert "source" not in parameters


def test_correction_qualification_rejects_cross_platform_and_contradictory_fields() -> None:
    evidence = _opaque_evidence_ref("correction", "invariant", "fields")
    windows = PlatformBackendTuple(
        subject=QualificationSubject.WINDOWS,
        platform_identity="windows:test-version",
        filesystem_backend="windows-fs:testfs",
    )
    linux = PlatformBackendTuple(
        subject=QualificationSubject.LINUX,
        platform_identity="linux:test-kernel",
        filesystem_backend="linux-fs:testfs",
    )
    python_abstraction = PlatformBackendTuple(
        subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
        platform_identity="cpython:test-version",
        filesystem_backend="windows-fs:testfs",
    )
    exact_linux_constraints = (
        RuntimeConstraint.EXACT_LINUX_KERNEL_AND_FILESYSTEM,
        RuntimeConstraint.TARGET_ABSENT_AT_FINAL_MUTATION,
    )
    with pytest.raises(ValueError, match="renameat2 belongs only to the Linux subject"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.NO,
            platform_backend=windows,
            native_primitive=NativePrimitive.LINUX_RENAMEAT2_NOREPLACE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="MoveFileExW belongs only to the Windows subject"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.LINUX,
            status=QualificationStatus.NO,
            platform_backend=linux,
            native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="NONE primitive belongs only to the Python abstraction"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.NO,
            platform_backend=windows,
            native_primitive=NativePrimitive.NONE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="YES requires preserved final-window mismatch semantics"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.YES,
            platform_backend=windows,
            native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="YES cannot advertise conditional constraints"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.WINDOWS,
            status=QualificationStatus.YES,
            platform_backend=windows,
            native_primitive=NativePrimitive.WINDOWS_MOVE_FILE_EXW,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT,
            evidence_ref=evidence,
            runtime_constraints=exact_linux_constraints,
        )
    with pytest.raises(
        ValueError,
        match="CONDITIONAL requires preserved final-window mismatch semantics",
    ):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.LINUX,
            status=QualificationStatus.CONDITIONAL,
            platform_backend=linux,
            native_primitive=NativePrimitive.LINUX_RENAMEAT2_NOREPLACE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
            runtime_constraints=exact_linux_constraints,
        )
    with pytest.raises(ValueError, match="NO has contradictory final-window failure semantics"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.PYTHON_FILESYSTEM_ABSTRACTION,
            status=QualificationStatus.NO,
            platform_backend=python_abstraction,
            native_primitive=NativePrimitive.NONE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_PRESERVED,
            failure_semantics=FailureSemantics.PRECONDITION_MISMATCH_NO_EFFECT,
            evidence_ref=evidence,
        )
    with pytest.raises(ValueError, match="NO cannot advertise a runtime capability"):
        AtomicConditionalReplaceQualification(
            subject=QualificationSubject.LINUX,
            status=QualificationStatus.NO,
            platform_backend=linux,
            native_primitive=NativePrimitive.LINUX_RENAMEAT2_NOREPLACE,
            race_model=(
                RaceModel.EXTERNAL_REPLACEMENT_AFTER_LAST_IDENTITY_BEFORE_FINAL_MUTATION
            ),
            final_window_observation=FinalWindowObservation.EXTERNAL_BYTES_OVERWRITTEN,
            failure_semantics=FailureSemantics.FINAL_WINDOW_NOT_CONDITIONAL,
            evidence_ref=evidence,
            runtime_constraints=exact_linux_constraints,
        )


def test_acr6_exact_test_only_boundary() -> None:
    repository = Path(__file__).resolve().parents[1]
    _assert_exact_candidate_boundary(repository)


def test_acr6_committed_candidate_diff_and_forbidden_paths(
    tmp_path: Path,
) -> None:
    source_repository = Path(__file__).resolve().parents[1]
    replica = tmp_path / "candidate-replica"
    cloned = subprocess.run(
        ("git", "clone", "--no-local", "--quiet", str(source_repository), str(replica)),
        check=False,
        capture_output=True,
        timeout=20,
    )
    assert cloned.returncode == 0
    _git(replica, "checkout", "--detach", _TICKET_AUTHORITY_BASELINE)
    _git(replica, "config", "user.email", "capability@example.invalid")
    _git(replica, "config", "user.name", "Capability Probe")
    candidate = replica / "tests" / "test_atomic_conditional_replace_capability.py"
    candidate.write_bytes(Path(__file__).read_bytes())
    _git(replica, "add", candidate.relative_to(replica).as_posix())
    _git(replica, "commit", "-m", "candidate evidence harness")
    _assert_exact_candidate_boundary(replica)

    forbidden_paths = (
        "library/forbidden-capability.py",
        "tests/test_target_document_management.py",
        "doc/forbidden-capability.md",
        "modules/tickets/forbidden-capability.md",
    )
    for forbidden_path in forbidden_paths:
        target = replica / forbidden_path
        original = target.read_bytes() if target.exists() else None
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"forbidden candidate mutation\n")
        assert forbidden_path in _candidate_change_paths(replica)
        with pytest.raises(AssertionError):
            _assert_exact_candidate_boundary(replica)
        if original is None:
            target.unlink()
        else:
            target.write_bytes(original)
    _assert_exact_candidate_boundary(replica)
