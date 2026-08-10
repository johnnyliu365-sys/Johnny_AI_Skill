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
    ProcessExitCode,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    TimedOutProcessObservation,
    WindowsLaunchEvidence,
)


class BoundedChildProcessRunner:
    """Runs only an exact argv inside an explicit owned 05S1 environment."""

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        validated_request = ChildProcessRequest.model_validate(request.model_dump())
        invocation = ProcessInvocation(
            executable=validated_request.executable,
            original_arguments=validated_request.arguments,
            effective_argv=EffectiveArgv(
                values=(validated_request.executable.value, *validated_request.arguments.values)
            ),
        )
        try:
            process = subprocess.Popen(
                invocation.effective_argv.values,
                cwd=str(validated_request.working_directory.path),
                env=self._overlay_environment(validated_request),
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as error:
            return self._launch_failure(invocation, error)
        try:
            exit_code = process.wait(timeout=validated_request.timeout.value / 1_000)
        except subprocess.TimeoutExpired:
            process.kill()
            exit_code = process.wait()
            return TimedOutProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))
        if exit_code == 0:
            return SuccessfulProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))
        return NonzeroProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=exit_code))

    @staticmethod
    def _overlay_environment(request: ChildProcessRequest) -> dict[str, str]:
        return {entry.key.value: entry.path.value for entry in request.overlay.entries}

    @staticmethod
    def _launch_failure(invocation: ProcessInvocation, error: OSError) -> ProcessObservation:
        winerror = error.winerror
        evidence = WindowsLaunchEvidence(winerror=winerror if isinstance(winerror, int) else 0)
        if evidence.winerror in (2, 3):
            return ExecutableUnavailableObservation(invocation=invocation, launch=evidence)
        if evidence.winerror == 5:
            return AccessDeniedObservation(invocation=invocation, launch=evidence)
        return GenericLaunchFailureObservation(invocation=invocation, launch=evidence)
