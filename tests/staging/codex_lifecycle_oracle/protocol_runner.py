"""Exact 05S3 runner substitution that invokes the persisted-oracle child."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from tests.staging.codex_protocol.contracts import CodexProtocolSurface
from tests.staging.codex_protocol.fixture import FIXTURE_CHILD
from tests.staging.process_runner.contracts import (
    ChildProcessRequest,
    EffectiveArgv,
    GenericLaunchFailureObservation,
    ProcessExitCode,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    NonzeroProcessObservation,
    WindowsLaunchEvidence,
)
from tests.staging.process_runner.runner import BoundedChildProcessRunner

from .contracts import OracleBlockReason, OracleChildExitCode


ORACLE_CHILD = Path(__file__).with_name("oracle_child.py")


class CodexLifecycleOracleRunner:
    """Provides one real oracle-child observation through the existing 05S3 port."""

    def __init__(self, bounded_runner: BoundedChildProcessRunner) -> None:
        self._bounded_runner = bounded_runner
        self._last_block_reason = OracleBlockReason.PROCESS_FAILED
        self._last_child_argv: tuple[str, ...] = ()

    @property
    def last_block_reason(self) -> OracleBlockReason:
        return self._last_block_reason

    @property
    def last_child_argv(self) -> tuple[str, ...]:
        return self._last_child_argv

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        validated = self._validate_request(request)
        if not isinstance(validated, ChildProcessRequest):
            self._last_block_reason = OracleBlockReason.COMMAND_INVALID
            return self._invalid_observation(request)
        oracle_request = ChildProcessRequest(
            lease=validated.lease,
            executable=validated.executable,
            arguments=validated.arguments.model_copy(update={"values": (str(ORACLE_CHILD), validated.arguments.values[1])}),
            working_directory=validated.working_directory,
            overlay=validated.overlay,
            timeout=validated.timeout,
            termination_timeout=validated.termination_timeout,
        )
        observation = self._bounded_runner.run(oracle_request)
        self._last_child_argv = observation.invocation.effective_argv.values
        self._last_block_reason = self._map_observation(observation)
        return observation

    @staticmethod
    def _validate_request(request: ChildProcessRequest) -> ChildProcessRequest | OracleBlockReason:
        try:
            validated = ChildProcessRequest.model_validate(request.model_dump())
        except (AttributeError, ValidationError, ValueError):
            return OracleBlockReason.COMMAND_INVALID
        arguments = validated.arguments.values
        if len(arguments) != 2 or arguments[0] != str(FIXTURE_CHILD):
            return OracleBlockReason.COMMAND_INVALID
        try:
            surface = CodexProtocolSurface(arguments[1])
        except ValueError:
            return OracleBlockReason.COMMAND_INVALID
        if arguments[1] != surface.value or validated.working_directory != validated.lease.temporary.absolute:
            return OracleBlockReason.COMMAND_INVALID
        if validated.overlay != validated.lease.overlay:
            return OracleBlockReason.COMMAND_INVALID
        return validated

    @staticmethod
    def _invalid_observation(request: ChildProcessRequest) -> ProcessObservation:
        invocation = ProcessInvocation(
            executable=request.executable,
            original_arguments=request.arguments,
            effective_argv=EffectiveArgv(values=(request.executable.value, *request.arguments.values)),
        )
        return GenericLaunchFailureObservation(invocation=invocation, launch=WindowsLaunchEvidence(winerror=0))

    @staticmethod
    def _map_observation(observation: ProcessObservation) -> OracleBlockReason:
        if isinstance(observation, SuccessfulProcessObservation):
            return OracleBlockReason.PROCESS_FAILED
        if isinstance(observation, NonzeroProcessObservation):
            try:
                code = OracleChildExitCode(observation.exit_code.value)
            except ValueError:
                return OracleBlockReason.PROCESS_FAILED
            return code.block_reason
        return OracleBlockReason.PROCESS_FAILED
