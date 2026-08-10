"""Strong contracts for the bounded generic child-process runner."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
import stat
from typing import Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentLocator,
    EnvironmentMarker,
    EnvironmentOverlay,
)


class StrictModel(BaseModel):
    """Reject unchecked process-boundary values."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class AbsoluteExecutable(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def exact_absolute_executable(cls, value: str) -> str:
        path = Path(value)
        if not value or value != value.strip() or "\x00" in value or not path.is_absolute():
            raise ValueError("executable must be a NUL-free absolute locator")
        return str(path)

    @property
    def path(self) -> Path:
        return Path(self.value)


class ImmutableArguments(StrictModel):
    values: tuple[str, ...]

    @field_validator("values")
    @classmethod
    def exact_argument_vector(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        for value in values:
            if not value or value != value.strip() or "\x00" in value:
                raise ValueError("arguments must be nonblank NUL-free strings")
        return values


class EffectiveArgv(StrictModel):
    values: tuple[str, ...]

    @field_validator("values")
    @classmethod
    def exact_effective_vector(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if not values:
            raise ValueError("effective argv must contain an executable")
        return values


class BoundedTimeoutMilliseconds(StrictModel):
    value: int

    @field_validator("value")
    @classmethod
    def positive_bounded_timeout(cls, value: int) -> int:
        if value < 1 or value > 10_000:
            raise ValueError("timeout must be between one and ten thousand milliseconds")
        return value


class ChildProcessRequest(StrictModel):
    lease: EnvironmentLease
    executable: AbsoluteExecutable
    arguments: ImmutableArguments
    working_directory: EnvironmentLocator
    overlay: EnvironmentOverlay
    timeout: BoundedTimeoutMilliseconds
    termination_timeout: BoundedTimeoutMilliseconds

    @model_validator(mode="after")
    def exact_owned_process_boundary(self) -> ChildProcessRequest:
        if not _is_live_owned_boundary(self.lease, self.working_directory, self.overlay):
            raise ValueError("process boundary must be the exact live 05S1 lease")
        return self


class ProcessAdmissionRejected(StrictModel):
    reason: Literal["INVALID_OR_STALE_REQUEST"] = "INVALID_OR_STALE_REQUEST"


ProcessAdmission: TypeAlias = ChildProcessRequest | ProcessAdmissionRejected


def revalidate_process_admission(request: ChildProcessRequest) -> ProcessAdmission:
    """Recheck constructed requests immediately before the child can start."""

    try:
        return ChildProcessRequest.model_validate(request.model_dump())
    except (AttributeError, ValidationError, ValueError, OSError):
        return ProcessAdmissionRejected()


def _is_live_owned_boundary(
    lease: EnvironmentLease,
    working_directory: EnvironmentLocator,
    overlay: EnvironmentOverlay,
) -> bool:
    try:
        validated_lease = EnvironmentLease.model_validate(lease.model_dump())
        validated_overlay = EnvironmentOverlay.model_validate(overlay.model_dump())
    except (AttributeError, ValidationError, ValueError):
        return False
    root = validated_lease.root.path
    if "\x00" in validated_lease.root.value or not _is_plain_directory(root):
        return False
    if not _is_exact_marker(validated_lease):
        return False
    declared = (
        validated_lease.profile,
        validated_lease.local_app_data,
        validated_lease.roaming_app_data,
        validated_lease.temporary,
        validated_lease.codex_home,
    )
    expected_values = tuple(str(root / path.relative.value) for path in declared)
    declared_values = tuple(path.absolute.value for path in declared)
    if declared_values != expected_values:
        return False
    for path in declared:
        if "\x00" in path.absolute.value or not _is_plain_directory(path.absolute.path):
            return False
    expected_overlay_values = (
        validated_lease.profile.absolute.value,
        validated_lease.local_app_data.absolute.value,
        validated_lease.roaming_app_data.absolute.value,
        validated_lease.temporary.absolute.value,
        validated_lease.temporary.absolute.value,
        validated_lease.codex_home.absolute.value,
    )
    overlay_values = tuple(entry.path.value for entry in validated_overlay.entries)
    if overlay_values != expected_overlay_values:
        return False
    if any("\x00" in value for value in overlay_values):
        return False
    if working_directory.value not in declared_values:
        return False
    return _is_plain_directory(working_directory.path)


def _is_exact_marker(lease: EnvironmentLease) -> bool:
    marker_path = lease.marker_path
    if not _is_plain_file(marker_path):
        return False
    try:
        marker = EnvironmentMarker.model_validate_json(marker_path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return False
    return marker == lease.marker


def _is_plain_directory(path: Path) -> bool:
    if _is_reparse_point(path):
        return False
    try:
        return path.is_dir() and path.resolve(strict=True) == path
    except OSError:
        return False


def _is_plain_file(path: Path) -> bool:
    if _is_reparse_point(path):
        return False
    try:
        return path.is_file() and path.resolve(strict=True) == path
    except OSError:
        return False


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return True
    except OSError:
        return True
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


class ChildStartState(str, Enum):
    STARTED = "STARTED"
    NOT_STARTED = "NOT_STARTED"


class ChildTerminationState(str, Enum):
    CONFIRMED_TERMINATED = "CONFIRMED_TERMINATED"
    UNCONFIRMED = "UNCONFIRMED"


class ProcessResultKind(str, Enum):
    SUCCESS = "SUCCESS"
    NONZERO_EXIT = "NONZERO_EXIT"
    TIMEOUT_AFTER_START = "TIMEOUT_AFTER_START"
    WAIT_FAILED_AFTER_START = "WAIT_FAILED_AFTER_START"
    TERMINATION_FAILED = "TERMINATION_FAILED"
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    GENERIC_LAUNCH_FAILURE = "GENERIC_LAUNCH_FAILURE"


class TerminationFailureReason(str, Enum):
    KILL_OS_ERROR = "KILL_OS_ERROR"
    REAP_TIMEOUT = "REAP_TIMEOUT"
    REAP_OS_ERROR = "REAP_OS_ERROR"


class StartedChildTrigger(str, Enum):
    RUN_TIMEOUT = "RUN_TIMEOUT"
    RUN_WAIT_OS_ERROR = "RUN_WAIT_OS_ERROR"


class WaitFailureReason(str, Enum):
    WAIT_OS_ERROR = "WAIT_OS_ERROR"


class ProcessExitCode(StrictModel):
    value: int


class WindowsLaunchEvidence(StrictModel):
    winerror: int

    @field_validator("winerror")
    @classmethod
    def concrete_winerror(cls, value: int) -> int:
        if value < 0:
            raise ValueError("winerror must be nonnegative")
        return value


class ProcessInvocation(StrictModel):
    executable: AbsoluteExecutable
    original_arguments: ImmutableArguments
    effective_argv: EffectiveArgv

    @model_validator(mode="after")
    def argv_binds_exact_executable(self) -> ProcessInvocation:
        if self.effective_argv.values != (self.executable.value, *self.original_arguments.values):
            raise ValueError("effective argv must bind the exact executable and original arguments")
        return self


class SuccessfulProcessObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.SUCCESS] = ProcessResultKind.SUCCESS
    started: Literal[ChildStartState.STARTED] = ChildStartState.STARTED
    exit_code: ProcessExitCode

    @model_validator(mode="after")
    def exact_success_exit(self) -> SuccessfulProcessObservation:
        if self.exit_code.value != 0:
            raise ValueError("success must carry exit code zero")
        return self


class NonzeroProcessObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.NONZERO_EXIT] = ProcessResultKind.NONZERO_EXIT
    started: Literal[ChildStartState.STARTED] = ChildStartState.STARTED
    exit_code: ProcessExitCode

    @model_validator(mode="after")
    def exact_nonzero_exit(self) -> NonzeroProcessObservation:
        if self.exit_code.value == 0:
            raise ValueError("nonzero result must carry a nonzero exit code")
        return self


class TimedOutProcessObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.TIMEOUT_AFTER_START] = ProcessResultKind.TIMEOUT_AFTER_START
    started: Literal[ChildStartState.STARTED] = ChildStartState.STARTED
    exit_code: ProcessExitCode


class WaitFailedAfterStartObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.WAIT_FAILED_AFTER_START] = ProcessResultKind.WAIT_FAILED_AFTER_START
    started: Literal[ChildStartState.STARTED] = ChildStartState.STARTED
    child_state: Literal[ChildTerminationState.CONFIRMED_TERMINATED] = ChildTerminationState.CONFIRMED_TERMINATED
    reason: Literal[WaitFailureReason.WAIT_OS_ERROR] = WaitFailureReason.WAIT_OS_ERROR
    exit_code: ProcessExitCode


class TerminationFailedProcessObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.TERMINATION_FAILED] = ProcessResultKind.TERMINATION_FAILED
    started: Literal[ChildStartState.STARTED] = ChildStartState.STARTED
    child_state: Literal[ChildTerminationState.UNCONFIRMED] = ChildTerminationState.UNCONFIRMED
    trigger: StartedChildTrigger
    termination_reason: TerminationFailureReason


class ExecutableUnavailableObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.EXECUTABLE_UNAVAILABLE] = ProcessResultKind.EXECUTABLE_UNAVAILABLE
    started: Literal[ChildStartState.NOT_STARTED] = ChildStartState.NOT_STARTED
    launch: WindowsLaunchEvidence


class AccessDeniedObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.ACCESS_DENIED] = ProcessResultKind.ACCESS_DENIED
    started: Literal[ChildStartState.NOT_STARTED] = ChildStartState.NOT_STARTED
    launch: WindowsLaunchEvidence


class GenericLaunchFailureObservation(StrictModel):
    invocation: ProcessInvocation
    result: Literal[ProcessResultKind.GENERIC_LAUNCH_FAILURE] = ProcessResultKind.GENERIC_LAUNCH_FAILURE
    started: Literal[ChildStartState.NOT_STARTED] = ChildStartState.NOT_STARTED
    launch: WindowsLaunchEvidence


class StartedChildProcess(Protocol):
    """A started child that can only be waited, then killed and reaped."""

    def wait(self, timeout_seconds: float) -> int:
        """Return the child exit code or raise a concrete process exception."""

    def kill(self) -> None:
        """Request termination of this exact started child."""


class ProcessPort(Protocol):
    """Required process boundary; implementations never accept a command string."""

    def start(
        self,
        invocation: ProcessInvocation,
        working_directory: EnvironmentLocator,
        overlay: EnvironmentOverlay,
    ) -> StartedChildProcess:
        """Start the exact invocation with the exact owned execution boundary."""


ProcessObservation: TypeAlias = (
    SuccessfulProcessObservation
    | NonzeroProcessObservation
    | TimedOutProcessObservation
    | WaitFailedAfterStartObservation
    | TerminationFailedProcessObservation
    | ExecutableUnavailableObservation
    | AccessDeniedObservation
    | GenericLaunchFailureObservation
)
