"""Application boundary that binds a real 05S2 child to one fixed response file."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Protocol

from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease
from tests.staging.process_runner.contracts import (
    AbsoluteExecutable,
    BoundedTimeoutMilliseconds,
    ChildProcessRequest,
    ImmutableArguments,
    ProcessObservation,
    SuccessfulProcessObservation,
)

from .contracts import (
    CodexProtocolAccepted,
    CodexProtocolRejectReason,
    CodexProtocolRejected,
    CodexProtocolSurface,
    ExactResponseFilePort,
    ResponseFileBoundaryInvalid,
    ResponseFileBytes,
    ResponseFileInspection,
    ResponseFilePort,
    ResponseFileRemoval,
    ResponseFileTooLarge,
    parse_codex_protocol_payload,
)


FIXTURE_CHILD = Path(__file__).with_name("fixture_child.py")


class ProcessRunnerPort(Protocol):
    """Required integrated 05S2 runner boundary."""

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        """Run the exact bounded child request."""


class CodexProtocolFixture:
    """Runs a selected protocol surface without accepting any response values from the parent."""

    def __init__(self, process_runner: ProcessRunnerPort, response_files: ResponseFilePort) -> None:
        self._process_runner = process_runner
        self._response_files = response_files

    @classmethod
    def with_concrete_response_file(cls, process_runner: ProcessRunnerPort) -> CodexProtocolFixture:
        return cls(process_runner, ExactResponseFilePort())

    def run(
        self,
        lease: EnvironmentLease,
        surface: CodexProtocolSurface,
    ) -> CodexProtocolAccepted | CodexProtocolRejected:
        if not isinstance(revalidate_lease(lease), EnvironmentLease):
            return self._rejected(surface, CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID, lease)
        if self._inspect(lease) is not ResponseFileInspection.ABSENT:
            return CodexProtocolRejected(surface=surface, reason=CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID)
        try:
            observation = self._process_runner.run(self._request(lease, surface))
        except (OSError, ValueError):
            return self._rejected(surface, CodexProtocolRejectReason.PROCESS_FAILED, lease)
        if not isinstance(observation, SuccessfulProcessObservation):
            return self._rejected(surface, CodexProtocolRejectReason.PROCESS_FAILED, lease)
        inspection = self._inspect(lease)
        if inspection is ResponseFileInspection.ABSENT:
            return self._rejected(surface, CodexProtocolRejectReason.RESPONSE_MISSING, lease)
        if inspection is ResponseFileInspection.BOUNDARY_INVALID:
            return self._rejected(surface, CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID, lease)
        response = self._read(lease)
        if isinstance(response, ResponseFileTooLarge):
            return self._rejected(surface, response.reason, lease)
        if isinstance(response, ResponseFileBoundaryInvalid):
            return self._rejected(surface, response.reason, lease)
        payload = parse_codex_protocol_payload(surface, response.value)
        if isinstance(payload, CodexProtocolRejectReason):
            return self._rejected(surface, payload, lease)
        if self._remove(lease) is ResponseFileRemoval.FAILED:
            return CodexProtocolRejected(surface=surface, reason=CodexProtocolRejectReason.CLEANUP_FAILED)
        return CodexProtocolAccepted(surface=surface, payload=payload)

    def _request(self, lease: EnvironmentLease, surface: CodexProtocolSurface) -> ChildProcessRequest:
        executable = AbsoluteExecutable(value=str(Path(sys.executable).resolve(strict=True)))
        return ChildProcessRequest(
            lease=lease,
            executable=executable,
            arguments=ImmutableArguments(values=(str(FIXTURE_CHILD), surface.value)),
            working_directory=lease.temporary.absolute,
            overlay=lease.overlay,
            timeout=BoundedTimeoutMilliseconds(value=1_000),
            termination_timeout=BoundedTimeoutMilliseconds(value=1_000),
        )

    def _rejected(
        self,
        surface: CodexProtocolSurface,
        reason: CodexProtocolRejectReason,
        lease: EnvironmentLease,
    ) -> CodexProtocolRejected:
        if self._remove(lease) is ResponseFileRemoval.FAILED:
            return CodexProtocolRejected(surface=surface, reason=CodexProtocolRejectReason.CLEANUP_FAILED)
        return CodexProtocolRejected(surface=surface, reason=reason)

    def _inspect(self, lease: EnvironmentLease) -> ResponseFileInspection:
        try:
            return self._response_files.inspect(lease)
        except (OSError, ValueError):
            return ResponseFileInspection.BOUNDARY_INVALID

    def _read(self, lease: EnvironmentLease) -> ResponseFileBytes | ResponseFileTooLarge | ResponseFileBoundaryInvalid:
        try:
            return self._response_files.read(lease)
        except (OSError, ValueError):
            return ResponseFileBoundaryInvalid()

    def _remove(self, lease: EnvironmentLease) -> ResponseFileRemoval:
        try:
            return self._response_files.remove(lease)
        except (OSError, ValueError):
            return ResponseFileRemoval.FAILED
