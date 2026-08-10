"""Bounded generic child-process execution for Ticket 05S2."""

from __future__ import annotations

import subprocess

from .contracts import (
    AccessDeniedObservation,
    ChildProcessRequest,
    EffectiveArgv,
    ExecutableUnavailableObservation,
    GenericLaunchFailureObservation,
    NonzeroProcessObservation,
    ProcessAdmissionRejected,
    ProcessExitCode,
    ProcessInvocation,
    ProcessObservation,
    ProcessPort,
    StartedChildProcess,
    StartedChildTrigger,
    SuccessfulProcessObservation,
    TerminationFailedProcessObservation,
    TerminationFailureReason,
    TimedOutProcessObservation,
    WaitFailedAfterStartObservation,
    WindowsLaunchEvidence,
    revalidate_process_admission,
)
from tests.staging.environment_core.contracts import EnvironmentLocator, EnvironmentOverlay


class SubprocessStartedChild:
    """Concrete handle for exactly one subprocess child."""

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self._process = process

    def wait(self, timeout_seconds: float) -> int:
        return self._process.wait(timeout=timeout_seconds)

    def kill(self) -> None:
        self._process.kill()


class SubprocessProcessPort:
    """The concrete shell-free subprocess implementation of the required port."""

    def start(
        self,
        invocation: ProcessInvocation,
        working_directory: EnvironmentLocator,
        overlay: EnvironmentOverlay,
    ) -> StartedChildProcess:
        environment = {entry.key.value: entry.path.value for entry in overlay.entries}
        process: subprocess.Popen[bytes] = subprocess.Popen(
            invocation.effective_argv.values,
            cwd=working_directory.value,
            env=environment,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return SubprocessStartedChild(process)


class BoundedChildProcessRunner:
    """Runs only an exact argv inside an explicit owned 05S1 environment."""

    def __init__(self, process_port: ProcessPort) -> None:
        self._process_port = process_port

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        invocation = ProcessInvocation(
            executable=request.executable,
            original_arguments=request.arguments,
            effective_argv=EffectiveArgv(values=(request.executable.value, *request.arguments.values)),
        )
        admission = revalidate_process_admission(request)
        if isinstance(admission, ProcessAdmissionRejected):
            return GenericLaunchFailureObservation(invocation=invocation, launch=WindowsLaunchEvidence(winerror=0))
        try:
            child = self._process_port.start(
                invocation,
                admission.working_directory,
                admission.overlay,
            )
        except (OSError, ValueError) as error:
            return self._launch_failure(invocation, error)
        try:
            exit_code = child.wait(admission.timeout.value / 1_000)
        except subprocess.TimeoutExpired:
            return self._terminate_after_first_wait(
                child,
                admission,
                invocation,
                StartedChildTrigger.RUN_TIMEOUT,
            )
        except OSError:
            return self._terminate_after_first_wait(
                child,
                admission,
                invocation,
                StartedChildTrigger.RUN_WAIT_OS_ERROR,
            )
        if exit_code == 0:
            return SuccessfulProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))
        return NonzeroProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))

    @staticmethod
    def _terminate_after_first_wait(
        child: StartedChildProcess,
        request: ChildProcessRequest,
        invocation: ProcessInvocation,
        trigger: StartedChildTrigger,
    ) -> ProcessObservation:
        try:
            child.kill()
        except OSError:
            return TerminationFailedProcessObservation(
                invocation=invocation,
                trigger=trigger,
                termination_reason=TerminationFailureReason.KILL_OS_ERROR,
            )
        try:
            exit_code = child.wait(request.termination_timeout.value / 1_000)
        except subprocess.TimeoutExpired:
            return TerminationFailedProcessObservation(
                invocation=invocation,
                trigger=trigger,
                termination_reason=TerminationFailureReason.REAP_TIMEOUT,
            )
        except OSError:
            return TerminationFailedProcessObservation(
                invocation=invocation,
                trigger=trigger,
                termination_reason=TerminationFailureReason.REAP_OS_ERROR,
            )
        if trigger is StartedChildTrigger.RUN_TIMEOUT:
            return TimedOutProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))
        return WaitFailedAfterStartObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))

    @staticmethod
    def _launch_failure(invocation: ProcessInvocation, error: OSError | ValueError) -> ProcessObservation:
        winerror = error.winerror if isinstance(error, OSError) and isinstance(error.winerror, int) else 0
        evidence = WindowsLaunchEvidence(winerror=winerror)
        if evidence.winerror in (2, 3):
            return ExecutableUnavailableObservation(invocation=invocation, launch=evidence)
        if evidence.winerror == 5:
            return AccessDeniedObservation(invocation=invocation, launch=evidence)
        return GenericLaunchFailureObservation(invocation=invocation, launch=evidence)
