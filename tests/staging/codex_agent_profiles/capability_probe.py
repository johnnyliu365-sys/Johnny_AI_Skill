"""Disposable, bounded, metadata-only Codex role-profile capability probe for Ticket 06A."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Protocol

from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionBlocked,
    ProvisionedEnvironment,
    TeardownBlockReason,
    TeardownResult,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import (
    AccessDeniedObservation,
    AbsoluteExecutable,
    BoundedTimeoutMilliseconds,
    ChildProcessRequest,
    EffectiveArgv,
    ExecutableUnavailableObservation,
    GenericLaunchFailureObservation,
    ImmutableArguments,
    NonzeroProcessObservation,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    TerminationFailedProcessObservation,
    TimedOutProcessObservation,
    WaitFailedAfterStartObservation,
)
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort

from .contracts import (
    AgentProfileLocator,
    AgentProfileSpec,
    CapabilityProbeStatus,
    CapabilityReadback,
    CapabilityReadbackPort,
    CapabilityReadbackStatus,
    CodexExecutableLocator,
    EffectiveCapabilityReadback,
    FrozenProfileReceipts,
    MetadataDigest,
    ProcessEvidenceKind,
    ProfileReceipt,
    RoleIsolationStatus,
    RoleProfileProbeResult,
    TeardownEvidence,
    UnavailableCapabilityReadback,
    frozen_role_profiles,
)


_OWNER_VALUE = "environment-owner-6a06a06a06a06a06"
_PROFILE_DIRECTORY_NAME = "agents"
_VERSION_ARGUMENTS = ImmutableArguments(values=("--version",))
_TIMEOUT = BoundedTimeoutMilliseconds(value=1_000)


class ProcessRunner(Protocol):
    """The 05S2 bounded runner surface required by this ticket."""

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        """Run exactly one request inside the leased disposable boundary."""


class NoCapabilityReadback:
    """The current 05S2 runner intentionally discards stdout, so no proof is available."""

    def read(
        self,
        profile_receipts: FrozenProfileReceipts,
        execution_digest: MetadataDigest,
        profile_bundle_digest: MetadataDigest,
    ) -> CapabilityReadback:
        del profile_receipts, execution_digest, profile_bundle_digest
        return UnavailableCapabilityReadback(status=CapabilityReadbackStatus.OUTPUT_UNAVAILABLE)


@dataclass(frozen=True)
class _PreparedProfiles:
    receipts: FrozenProfileReceipts
    profile_paths: tuple[Path, Path]
    bundle_digest: MetadataDigest


@dataclass(frozen=True)
class _ProbeCore:
    receipts: FrozenProfileReceipts
    profile_paths: tuple[Path, Path]
    bundle_digest: MetadataDigest
    process_evidence: ProcessEvidenceKind
    readback_status: CapabilityReadbackStatus
    role_isolation: RoleIsolationStatus


class CodexRoleProfileCapabilityProbe:
    """Writes only disposable profiles and rejects config-only success claims."""

    def __init__(
        self,
        allocator: DisposableEnvironmentAllocator,
        runner: ProcessRunner,
        executable: CodexExecutableLocator,
        readback_port: CapabilityReadbackPort,
    ) -> None:
        self._allocator = allocator
        self._runner = runner
        self._executable = CodexExecutableLocator.model_validate(executable.model_dump())
        self._readback_port = readback_port

    @classmethod
    def for_installed_codex(
        cls,
        allocator: DisposableEnvironmentAllocator,
        executable: CodexExecutableLocator,
    ) -> CodexRoleProfileCapabilityProbe:
        """Use the integrated 05S2 runner; it can only return a fail-closed result today."""

        return cls(
            allocator=allocator,
            runner=BoundedChildProcessRunner(SubprocessProcessPort()),
            executable=executable,
            readback_port=NoCapabilityReadback(),
        )

    def execute(self) -> RoleProfileProbeResult:
        provision = self._allocator.provision(EnvironmentOwnerId(value=_OWNER_VALUE))
        if isinstance(provision, ProvisionBlocked):
            return RoleProfileProbeResult(
                status=CapabilityProbeStatus.INSTALL_BLOCKED,
                role_isolation=RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN,
                profile_bundle_digest=_digest(b"provision-blocked"),
                process_evidence=ProcessEvidenceKind.GENERIC_LAUNCH_FAILURE,
                readback_status=CapabilityReadbackStatus.OUTPUT_UNAVAILABLE,
                teardown=TeardownEvidence(
                    status=TeardownStatus.ALREADY_ABSENT,
                    reason=TeardownBlockReason.NONE,
                    root_absent=True,
                    profile_files_absent=True,
                ),
            )
        return self._execute_provisioned(provision)

    def _execute_provisioned(self, provision: ProvisionedEnvironment) -> RoleProfileProbeResult:
        lease = provision.environment
        prepared = _planned_frozen_profiles(lease)
        try:
            _write_frozen_profiles(lease, prepared)
            core = self._run_core(lease, prepared)
        except OSError:
            core = _profile_write_failed(prepared)
        finally:
            teardown = self._teardown(lease, prepared.profile_paths)
        return RoleProfileProbeResult(
            status=(
                CapabilityProbeStatus.SUPPORTED
                if core.role_isolation is RoleIsolationStatus.PROVEN
                and teardown.status is TeardownStatus.REMOVED
                and teardown.root_absent
                and teardown.profile_files_absent
                else CapabilityProbeStatus.INSTALL_BLOCKED
            ),
            role_isolation=(
                RoleIsolationStatus.PROVEN
                if core.role_isolation is RoleIsolationStatus.PROVEN
                and teardown.status is TeardownStatus.REMOVED
                and teardown.root_absent
                and teardown.profile_files_absent
                else RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
            ),
            profile_bundle_digest=core.bundle_digest,
            process_evidence=core.process_evidence,
            readback_status=core.readback_status,
            teardown=teardown,
        )

    def _run_core(self, lease: EnvironmentLease, prepared: _PreparedProfiles) -> _ProbeCore:
        request = ChildProcessRequest(
            lease=lease,
            executable=AbsoluteExecutable(value=self._executable.value),
            arguments=_VERSION_ARGUMENTS,
            working_directory=lease.codex_home.absolute,
            overlay=lease.overlay,
            timeout=_TIMEOUT,
            termination_timeout=_TIMEOUT,
        )
        expected_invocation = ProcessInvocation(
            executable=request.executable,
            original_arguments=request.arguments,
            effective_argv=EffectiveArgv(values=(request.executable.value, *request.arguments.values)),
        )
        try:
            observation = self._runner.run(request)
        except (OSError, ValueError):
            process_evidence = ProcessEvidenceKind.GENERIC_LAUNCH_FAILURE
        else:
            process_evidence = _classify_observation(observation, expected_invocation)
        execution_digest = _digest(
            f"{prepared.bundle_digest.value}:{process_evidence.value}".encode("ascii")
        )
        readback = self._readback_port.read(prepared.receipts, execution_digest, prepared.bundle_digest)
        role_isolation = _role_isolation_status(readback, process_evidence, execution_digest, prepared.bundle_digest)
        return _ProbeCore(
            receipts=prepared.receipts,
            profile_paths=prepared.profile_paths,
            bundle_digest=prepared.bundle_digest,
            process_evidence=process_evidence,
            readback_status=readback.status,
            role_isolation=role_isolation,
        )

    def _teardown(self, lease: EnvironmentLease, profile_paths: tuple[Path, Path]) -> TeardownEvidence:
        result: TeardownResult = self._allocator.teardown(lease)
        return TeardownEvidence(
            status=result.status,
            reason=result.reason,
            root_absent=_path_absent(lease.root.path),
            profile_files_absent=all(_path_absent(path) for path in profile_paths),
        )


def _planned_frozen_profiles(lease: EnvironmentLease) -> _PreparedProfiles:
    profiles = frozen_role_profiles()
    profile_directory = lease.codex_home.absolute.path / _PROFILE_DIRECTORY_NAME
    reviewer_path = profile_directory / f"{profiles.reviewer.name.value}.toml"
    implementation_path = profile_directory / f"{profiles.implementation.name.value}.toml"
    reviewer_text = render_profile_toml(profiles.reviewer)
    implementation_text = render_profile_toml(profiles.implementation)
    receipts = FrozenProfileReceipts(
        reviewer=ProfileReceipt(
            role=profiles.reviewer.role,
            locator=AgentProfileLocator(value=f"agents/{reviewer_path.name}"),
            digest=_digest(reviewer_text.encode("utf-8")),
        ),
        implementation=ProfileReceipt(
            role=profiles.implementation.role,
            locator=AgentProfileLocator(value=f"agents/{implementation_path.name}"),
            digest=_digest(implementation_text.encode("utf-8")),
        ),
    )
    bundle_digest = _digest(
        f"{receipts.reviewer.digest.value}:{receipts.implementation.digest.value}".encode("ascii")
    )
    return _PreparedProfiles(
        receipts=receipts,
        profile_paths=(reviewer_path, implementation_path),
        bundle_digest=bundle_digest,
    )


def _write_frozen_profiles(lease: EnvironmentLease, prepared: _PreparedProfiles) -> None:
    profiles = frozen_role_profiles()
    profile_directory = lease.codex_home.absolute.path / _PROFILE_DIRECTORY_NAME
    profile_directory.mkdir()
    reviewer_text = render_profile_toml(profiles.reviewer)
    implementation_text = render_profile_toml(profiles.implementation)
    prepared.profile_paths[0].write_text(reviewer_text, encoding="utf-8", newline="\n")
    prepared.profile_paths[1].write_text(implementation_text, encoding="utf-8", newline="\n")


def _profile_write_failed(prepared: _PreparedProfiles) -> _ProbeCore:
    return _ProbeCore(
        receipts=prepared.receipts,
        profile_paths=prepared.profile_paths,
        bundle_digest=prepared.bundle_digest,
        process_evidence=ProcessEvidenceKind.GENERIC_LAUNCH_FAILURE,
        readback_status=CapabilityReadbackStatus.OUTPUT_UNAVAILABLE,
        role_isolation=RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN,
    )


def render_profile_toml(profile: AgentProfileSpec) -> str:
    """Serialize one strict profile; this output is never capability evidence by itself."""

    validated = AgentProfileSpec.model_validate(profile.model_dump())
    enabled = "true" if validated.tool_policy.agents_enabled else "false"
    return (
        f'name = "{_toml_text(validated.name.value)}"\n'
        f'description = "{_toml_text(validated.description.value)}"\n'
        f'developer_instructions = "{_toml_text(validated.developer_instructions.value)}"\n'
        "[agents]\n"
        f"enabled = {enabled}\n"
    )


def _toml_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _classify_observation(
    observation: ProcessObservation,
    expected_invocation: ProcessInvocation,
) -> ProcessEvidenceKind:
    if observation.invocation != expected_invocation:
        return ProcessEvidenceKind.MALFORMED_OBSERVATION
    if isinstance(observation, SuccessfulProcessObservation):
        return ProcessEvidenceKind.VERSION_OUTPUT_UNREADABLE
    if isinstance(observation, ExecutableUnavailableObservation):
        return ProcessEvidenceKind.EXECUTABLE_UNAVAILABLE
    if isinstance(observation, AccessDeniedObservation):
        return ProcessEvidenceKind.ACCESS_DENIED
    if isinstance(observation, TimedOutProcessObservation):
        return ProcessEvidenceKind.TIMEOUT
    if isinstance(observation, WaitFailedAfterStartObservation):
        return ProcessEvidenceKind.WAIT_FAILED
    if isinstance(observation, TerminationFailedProcessObservation):
        return ProcessEvidenceKind.TERMINATION_FAILED
    if isinstance(observation, NonzeroProcessObservation):
        return ProcessEvidenceKind.NONZERO_EXIT
    if isinstance(observation, GenericLaunchFailureObservation):
        return ProcessEvidenceKind.GENERIC_LAUNCH_FAILURE
    return ProcessEvidenceKind.MALFORMED_OBSERVATION


def _role_isolation_status(
    readback: CapabilityReadback,
    process_evidence: ProcessEvidenceKind,
    execution_digest: MetadataDigest,
    profile_bundle_digest: MetadataDigest,
) -> RoleIsolationStatus:
    if not isinstance(readback, EffectiveCapabilityReadback):
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    if process_evidence is not ProcessEvidenceKind.VERSION_OUTPUT_UNREADABLE:
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    if readback.execution_digest != execution_digest or readback.profile_bundle_digest != profile_bundle_digest:
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    if not readback.reviewer_direct.is_full_orchestration_surface:
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    if not readback.reviewer_indirect.is_full_orchestration_surface:
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    if not readback.implementation_direct.is_empty or not readback.implementation_indirect.is_empty:
        return RoleIsolationStatus.ROLE_ISOLATION_UNPROVEN
    return RoleIsolationStatus.PROVEN


def _digest(value: bytes) -> MetadataDigest:
    return MetadataDigest(value=hashlib.sha256(value).hexdigest())


def _path_absent(path: Path) -> bool:
    try:
        return not path.exists()
    except OSError:
        return False
