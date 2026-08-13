"""Executable P1-P4 closure for Ticket 06A."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
import subprocess
import tempfile
from typing import Final
import unittest

from pydantic import ValidationError

from tests.staging.codex_agent_profiles.capability_probe import (
    CodexRoleProfileCapabilityProbe,
    ProcessRunner,
    render_profile_toml,
)
from tests.staging.codex_agent_profiles.contracts import (
    AgentProfileLocator,
    AgentProfileName,
    AgentProfileSpec,
    AgentRole,
    AgentToolPolicy,
    CapabilityProbeStatus,
    CapabilityReadback,
    CapabilityReadbackPort,
    CapabilityReadbackStatus,
    CodexExecutableLocator,
    DeveloperInstructions,
    EffectiveCapabilityReadback,
    FrozenProfileReceipts,
    MetadataDigest,
    OrchestrationTool,
    ProcessEvidenceKind,
    ProfileDescription,
    RoleIsolationStatus,
    RoleProfileProbeResult,
    ToolSurface,
    UnavailableCapabilityReadback,
    frozen_role_profiles,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionResult,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import (
    AccessDeniedObservation,
    ChildProcessRequest,
    EffectiveArgv,
    ExecutableUnavailableObservation,
    ProcessExitCode,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    TimedOutProcessObservation,
    WindowsLaunchEvidence,
)


_DIGEST_A: Final[MetadataDigest] = MetadataDigest(value="a" * 64)
_DIGEST_B: Final[MetadataDigest] = MetadataDigest(value="b" * 64)
_ALL_TOOLS: Final[ToolSurface] = ToolSurface(tools=tuple(OrchestrationTool))
_NO_TOOLS: Final[ToolSurface] = ToolSurface(tools=())


class _RunnerOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    ACCESS_DENIED = "ACCESS_DENIED"
    EXECUTABLE_UNAVAILABLE = "EXECUTABLE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"


class _ObservationRunner(ProcessRunner):
    """A typed runner double whose observations bind the request exact argv."""

    def __init__(self, outcome: _RunnerOutcome) -> None:
        self._outcome = outcome
        self.requests: list[ChildProcessRequest] = []

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.requests.append(request)
        invocation = ProcessInvocation(
            executable=request.executable,
            original_arguments=request.arguments,
            effective_argv=EffectiveArgv(values=(request.executable.value, *request.arguments.values)),
        )
        if self._outcome is _RunnerOutcome.SUCCESS:
            return SuccessfulProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=0))
        if self._outcome is _RunnerOutcome.ACCESS_DENIED:
            return AccessDeniedObservation(invocation=invocation, launch=WindowsLaunchEvidence(winerror=5))
        if self._outcome is _RunnerOutcome.EXECUTABLE_UNAVAILABLE:
            return ExecutableUnavailableObservation(invocation=invocation, launch=WindowsLaunchEvidence(winerror=2))
        return TimedOutProcessObservation(invocation=invocation, exit_code=ProcessExitCode(value=-9))


class _MarkerRemovingRunner(_ObservationRunner):
    """Simulate one owned cleanup fault while retaining the lease for recovery."""

    def __init__(self) -> None:
        super().__init__(_RunnerOutcome.SUCCESS)
        self.lease: EnvironmentLease | None = None

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.lease = request.lease
        request.lease.marker_path.unlink()
        return super().run(request)


class _ProfileDirectoryConflictAllocator(DisposableEnvironmentAllocator):
    """Make the owned profile directory unavailable before the probe can write it."""

    def provision(self, owner: EnvironmentOwnerId) -> ProvisionResult:
        result = super().provision(owner)
        if isinstance(result, ProvisionedEnvironment):
            (result.environment.codex_home.absolute.path / "agents").write_bytes(b"owned-conflict")
        return result


class _UnavailableReadback(CapabilityReadbackPort):
    def __init__(self, status: CapabilityReadbackStatus) -> None:
        self._status = status

    def read(
        self,
        profile_receipts: FrozenProfileReceipts,
        execution_digest: MetadataDigest,
        profile_bundle_digest: MetadataDigest,
    ) -> CapabilityReadback:
        del profile_receipts, execution_digest, profile_bundle_digest
        return UnavailableCapabilityReadback(status=self._status)


class _EffectiveReadback(CapabilityReadbackPort):
    """A controlled host-readback double; it binds the current process and profile metadata."""

    def __init__(
        self,
        reviewer_direct: ToolSurface,
        reviewer_indirect: ToolSurface,
        implementation_direct: ToolSurface,
        implementation_indirect: ToolSurface,
        bind_metadata: bool,
    ) -> None:
        self._reviewer_direct = reviewer_direct
        self._reviewer_indirect = reviewer_indirect
        self._implementation_direct = implementation_direct
        self._implementation_indirect = implementation_indirect
        self._bind_metadata = bind_metadata

    def read(
        self,
        profile_receipts: FrozenProfileReceipts,
        execution_digest: MetadataDigest,
        profile_bundle_digest: MetadataDigest,
    ) -> CapabilityReadback:
        del profile_receipts
        binding = execution_digest if self._bind_metadata else _DIGEST_A
        bundle = profile_bundle_digest if self._bind_metadata else _DIGEST_B
        return EffectiveCapabilityReadback(
            version_digest=_DIGEST_A,
            capability_digest=_DIGEST_B,
            execution_digest=binding,
            profile_bundle_digest=bundle,
            reviewer_direct=self._reviewer_direct,
            reviewer_indirect=self._reviewer_indirect,
            implementation_direct=self._implementation_direct,
            implementation_indirect=self._implementation_indirect,
        )


class CodexAgentProfileCapabilityTests(unittest.TestCase):
    """The frozen 06A closure covers only disposable test support."""

    def test_p1_frozen_profiles_use_official_fields_and_opposite_policies(self) -> None:
        profiles = frozen_role_profiles()

        reviewer_toml = render_profile_toml(profiles.reviewer)
        implementation_toml = render_profile_toml(profiles.implementation)

        self.assertEqual(profiles.reviewer.role, AgentRole.REVIEWER)
        self.assertEqual(profiles.reviewer.tool_policy, AgentToolPolicy.REVIEWER_ENABLED)
        self.assertEqual(profiles.implementation.role, AgentRole.IMPLEMENTATION)
        self.assertEqual(profiles.implementation.tool_policy, AgentToolPolicy.IMPLEMENTATION_DISABLED)
        for field in ("name", "description", "developer_instructions"):
            self.assertIn(f"{field} = ", reviewer_toml)
            self.assertIn(f"{field} = ", implementation_toml)
        self.assertIn("[agents]\nenabled = true", reviewer_toml)
        self.assertIn("[agents]\nenabled = false", implementation_toml)

    def test_p1_rejects_reversed_and_dynamic_profile_config_values(self) -> None:
        profiles = frozen_role_profiles()
        reversed_spec = {
            "role": AgentRole.IMPLEMENTATION,
            "name": profiles.implementation.name,
            "description": profiles.implementation.description,
            "developer_instructions": profiles.implementation.developer_instructions,
            "tool_policy": AgentToolPolicy.REVIEWER_ENABLED,
        }

        with self.assertRaises(ValidationError):
            AgentProfileSpec.model_validate(reversed_spec)
        invalid_names: tuple[str, ...] = ("", " reviewer-06a", "reviewer-06a/extra", "reviewer%2d06a")
        for invalid_name in invalid_names:
            with self.subTest(invalid_name=invalid_name), self.assertRaises(ValidationError):
                AgentProfileName(value=invalid_name)
        dynamic_values: tuple[object, ...] = (None, "", " ", [], {})
        for dynamic_value in dynamic_values:
            with self.subTest(dynamic_value=repr(dynamic_value)), self.assertRaises(ValidationError):
                AgentProfileSpec.model_validate(
                    {
                        "role": AgentRole.REVIEWER,
                        "name": profiles.reviewer.name,
                        "description": dynamic_value,
                        "developer_instructions": profiles.reviewer.developer_instructions,
                        "tool_policy": AgentToolPolicy.REVIEWER_ENABLED,
                    }
                )

    def test_p2_rejects_wildcard_suffix_case_encoded_traversal_and_empty_locators(self) -> None:
        invalid_executables: tuple[str, ...] = (
            "",
            r"C:\probe\codex.exe.bak",
            r"C:\probe\CODEX.EXE",
            r"C:\probe\codex%2Eexe",
            r"C:\probe\..\codex.exe",
            r"C:\probe\*.exe",
        )
        for invalid_executable in invalid_executables:
            with self.subTest(invalid_executable=invalid_executable), self.assertRaises(ValidationError):
                CodexExecutableLocator(value=invalid_executable)
        invalid_profiles: tuple[str, ...] = (
            "",
            "agents/reviewer-06a.toml/suffix",
            "agents/Reviewer-06a.toml",
            "agents/reviewer%2d06a.toml",
            "agents/../reviewer-06a.toml",
        )
        for invalid_profile in invalid_profiles:
            with self.subTest(invalid_profile=invalid_profile), self.assertRaises(ValidationError):
                AgentProfileLocator(value=invalid_profile)

    def test_p2_successful_version_exit_without_readback_is_install_blocked(self) -> None:
        runner = _ObservationRunner(_RunnerOutcome.SUCCESS)
        result = self._probe(runner=runner, readback=_UnavailableReadback(CapabilityReadbackStatus.OUTPUT_UNAVAILABLE))

        self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
        self.assertEqual(result.role_isolation, RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN)
        self.assertEqual(result.process_evidence, ProcessEvidenceKind.VERSION_OUTPUT_UNREADABLE)
        self.assertEqual(result.readback_status, CapabilityReadbackStatus.OUTPUT_UNAVAILABLE)
        self.assertEqual(len(runner.requests), 1)
        self.assertEqual(runner.requests[0].arguments.values, ("--version",))
        self.assertEqual(runner.requests[0].working_directory, runner.requests[0].lease.codex_home.absolute)

    def test_p2_access_denied_unavailable_and_timeout_are_finite_unproven_results(self) -> None:
        cases: tuple[tuple[_RunnerOutcome, ProcessEvidenceKind], ...] = (
            (_RunnerOutcome.ACCESS_DENIED, ProcessEvidenceKind.ACCESS_DENIED),
            (_RunnerOutcome.EXECUTABLE_UNAVAILABLE, ProcessEvidenceKind.EXECUTABLE_UNAVAILABLE),
            (_RunnerOutcome.TIMEOUT, ProcessEvidenceKind.TIMEOUT),
        )
        for outcome, expected_evidence in cases:
            with self.subTest(outcome=outcome):
                result = self._probe(
                    runner=_ObservationRunner(outcome),
                    readback=_UnavailableReadback(CapabilityReadbackStatus.UNSUPPORTED_CONFIG),
                )
                self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
                self.assertEqual(result.role_isolation, RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN)
                self.assertEqual(result.process_evidence, expected_evidence)

    def test_p3_effective_direct_and_indirect_readback_can_prove_only_the_frozen_split(self) -> None:
        result = self._probe(
            runner=_ObservationRunner(_RunnerOutcome.SUCCESS),
            readback=_EffectiveReadback(_ALL_TOOLS, _ALL_TOOLS, _NO_TOOLS, _NO_TOOLS, bind_metadata=True),
        )

        self.assertEqual(result.status, CapabilityProbeStatus.SUPPORTED)
        self.assertEqual(result.role_isolation, RoleIsolationStatus.PROVEN)
        self.assertEqual(result.readback_status, CapabilityReadbackStatus.EFFECTIVE)

    def test_p3_config_only_reversed_or_forged_readback_never_projects_supported(self) -> None:
        missing_reviewer_tool = ToolSurface(tools=tuple(tool for tool in OrchestrationTool if tool is not OrchestrationTool.CLOSE))
        cases: tuple[CapabilityReadbackPort, ...] = (
            _UnavailableReadback(CapabilityReadbackStatus.OUTPUT_UNAVAILABLE),
            _EffectiveReadback(missing_reviewer_tool, _ALL_TOOLS, _NO_TOOLS, _NO_TOOLS, bind_metadata=True),
            _EffectiveReadback(_ALL_TOOLS, _ALL_TOOLS, _ALL_TOOLS, _NO_TOOLS, bind_metadata=True),
            _EffectiveReadback(_ALL_TOOLS, _ALL_TOOLS, _NO_TOOLS, _ALL_TOOLS, bind_metadata=True),
            _EffectiveReadback(_ALL_TOOLS, _ALL_TOOLS, _NO_TOOLS, _NO_TOOLS, bind_metadata=False),
        )
        for readback in cases:
            with self.subTest(readback=type(readback).__name__):
                result = self._probe(runner=_ObservationRunner(_RunnerOutcome.SUCCESS), readback=readback)
                self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
                self.assertEqual(result.role_isolation, RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN)

    def test_p3_malformed_capability_readback_is_not_a_supported_result(self) -> None:
        result = self._probe(
            runner=_ObservationRunner(_RunnerOutcome.SUCCESS),
            readback=_UnavailableReadback(CapabilityReadbackStatus.MALFORMED_OUTPUT),
        )

        self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
        self.assertEqual(result.readback_status, CapabilityReadbackStatus.MALFORMED_OUTPUT)

    def test_p4_teardown_removes_disposable_profiles_and_preserves_foreign_and_target_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            foreign_sentinel = temporary_root / "foreign-reviewer-06a.toml"
            foreign_sentinel.write_bytes(b"foreign-profile-sentinel")
            existing_repository = temporary_root / "existing-target"
            empty_repository = temporary_root / "empty-target"
            self._initialize_repository(existing_repository)
            self._initialize_repository(empty_repository)
            existing_payload = existing_repository / "payload.bin"
            existing_payload.write_bytes(b"target-bytes")
            before_foreign = foreign_sentinel.read_bytes()
            before_existing = self._repository_snapshot(existing_repository, existing_payload)
            before_empty = self._repository_snapshot(empty_repository, None)

            result = self._probe(
                runner=_ObservationRunner(_RunnerOutcome.SUCCESS),
                readback=_UnavailableReadback(CapabilityReadbackStatus.OUTPUT_UNAVAILABLE),
            )

            self.assertEqual(result.teardown.status, TeardownStatus.REMOVED)
            self.assertTrue(result.teardown.root_absent)
            self.assertTrue(result.teardown.profile_files_absent)
            self.assertEqual(foreign_sentinel.read_bytes(), before_foreign)
            self.assertEqual(self._repository_snapshot(existing_repository, existing_payload), before_existing)
            self.assertEqual(self._repository_snapshot(empty_repository, None), before_empty)

    def test_p4_cleanup_failure_is_blocked_and_can_be_recovered_only_from_the_owned_lease(self) -> None:
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        runner = _MarkerRemovingRunner()
        probe = CodexRoleProfileCapabilityProbe(
            allocator=allocator,
            runner=runner,
            executable=CodexExecutableLocator(value=r"C:\probe\codex.exe"),
            readback_port=_UnavailableReadback(CapabilityReadbackStatus.OUTPUT_UNAVAILABLE),
        )

        result = probe.execute()

        self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
        self.assertEqual(result.teardown.status, TeardownStatus.BLOCKED)
        self.assertFalse(result.teardown.root_absent)
        self.assertIsNotNone(runner.lease)
        if runner.lease is None:
            self.fail("the marker-removing runner must retain its exact lease for test-only cleanup")
        runner.lease.marker_path.write_text(runner.lease.marker.model_dump_json(warnings=False), encoding="utf-8")
        recovered = allocator.teardown(runner.lease)
        self.assertEqual(recovered.status, TeardownStatus.REMOVED)
        self.assertFalse(runner.lease.root.path.exists())

    def test_p4_profile_write_failure_still_removes_the_owned_disposable_root(self) -> None:
        allocator = _ProfileDirectoryConflictAllocator.from_project_runtime()
        runner = _ObservationRunner(_RunnerOutcome.SUCCESS)
        probe = CodexRoleProfileCapabilityProbe(
            allocator=allocator,
            runner=runner,
            executable=CodexExecutableLocator(value=r"C:\probe\codex.exe"),
            readback_port=_UnavailableReadback(CapabilityReadbackStatus.OUTPUT_UNAVAILABLE),
        )

        result = probe.execute()

        self.assertEqual(result.status, CapabilityProbeStatus.INSTALL_BLOCKED)
        self.assertEqual(result.process_evidence, ProcessEvidenceKind.GENERIC_LAUNCH_FAILURE)
        self.assertEqual(result.teardown.status, TeardownStatus.REMOVED)
        self.assertTrue(result.teardown.root_absent)
        self.assertTrue(result.teardown.profile_files_absent)
        self.assertEqual(runner.requests, [])

    @staticmethod
    def _probe(runner: ProcessRunner, readback: CapabilityReadbackPort) -> RoleProfileProbeResult:
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        probe = CodexRoleProfileCapabilityProbe(
            allocator=allocator,
            runner=runner,
            executable=CodexExecutableLocator(value=r"C:\probe\codex.exe"),
            readback_port=readback,
        )
        return probe.execute()

    @staticmethod
    def _initialize_repository(path: Path) -> None:
        path.mkdir()
        subprocess.run(
            ("git", "init", "--quiet", str(path)),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @staticmethod
    def _repository_snapshot(repository: Path, payload: Path | None) -> tuple[bytes, bytes]:
        payload_bytes = b"" if payload is None else payload.read_bytes()
        status = subprocess.run(
            ("git", "-C", str(repository), "status", "--porcelain=v1"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return payload_bytes, status.stdout
