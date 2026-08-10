"""Strong contracts for the bounded generic child-process runner."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from tests.staging.environment_core.contracts import EnvironmentLease, EnvironmentLocator, EnvironmentOverlay


class StrictModel(BaseModel):
    """Reject unchecked process-boundary values."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class AbsoluteExecutable(StrictModel):
    value: str

    @field_validator("value")
    @classmethod
    def exact_absolute_executable(cls, value: str) -> str:
        path = Path(value)
        if not value or value != value.strip() or not path.is_absolute():
            raise ValueError("executable must be an absolute locator")
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

    @model_validator(mode="after")
    def exact_owned_process_boundary(self) -> ChildProcessRequest:
        try:
            lease = EnvironmentLease.model_validate(self.lease.model_dump())
        except (AttributeError, ValidationError, ValueError) as error:
            raise ValueError("lease must be a strict 05S1 environment") from error
        if self.overlay != lease.overlay:
            raise ValueError("process overlay must exactly equal the supplied 05S1 overlay")
        owned_directories = (
            lease.profile.absolute.path,
            lease.local_app_data.absolute.path,
            lease.roaming_app_data.absolute.path,
            lease.temporary.absolute.path,
            lease.codex_home.absolute.path,
        )
        if self.working_directory.path not in owned_directories or not self.working_directory.path.is_dir():
            raise ValueError("working directory must be one exact existing 05S1 child")
        return self


class ChildStartState(str, Enum):
    STARTED = "STARTED"
    NOT_STARTED = "NOT_STARTED"


class ProcessResultKind(str, Enum):
    SUCCESS = "SUCCESS"
    NONZERO_EXIT = "NONZERO_EXIT"
    TIMEOUT_AFTER_START = "TIMEOUT_AFTER_START"
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    GENERIC_LAUNCH_FAILURE = "GENERIC_LAUNCH_FAILURE"


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


ProcessObservation: TypeAlias = (
    SuccessfulProcessObservation
    | NonzeroProcessObservation
    | TimedOutProcessObservation
    | ExecutableUnavailableObservation
    | AccessDeniedObservation
    | GenericLaunchFailureObservation
)
