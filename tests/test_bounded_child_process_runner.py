"""Executable P1-P4 closure for the bounded child-process runner."""

from __future__ import annotations

from enum import Enum
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import unittest

from pydantic import ValidationError

from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentId,
    EnvironmentLocator,
    EnvironmentOverlay,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import (
    AbsoluteExecutable,
    AccessDeniedObservation,
    BoundedTimeoutMilliseconds,
    ChildStartState,
    ChildProcessRequest,
    ChildTerminationState,
    ExecutableUnavailableObservation,
    GenericLaunchFailureObservation,
    ImmutableArguments,
    NonzeroProcessObservation,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    StartedChildTrigger,
    TerminationFailedProcessObservation,
    TerminationFailureReason,
    TimedOutProcessObservation,
    WaitFailedAfterStartObservation,
    WaitFailureReason,
)
from tests.staging.process_runner.fixture_child import (
    LATE_WRITE_DELAY_SECONDS,
    FixtureObservation,
    FixtureOverlayEntry,
)
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_CHILD = Path(__file__).resolve().parent / "staging" / "process_runner" / "fixture_child.py"
OVERLAY_KEYS = ("USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", "CODEX_HOME")
ENVIRONMENT_PREFIX = "johnny-stage-env-"


class TerminationScenario(str, Enum):
    """Named deterministic child failures used only after a real timeout."""

    NONE = "NONE"
    KILL_OS_ERROR = "KILL_OS_ERROR"
    REAP_TIMEOUT = "REAP_TIMEOUT"
    REAP_OS_ERROR = "REAP_OS_ERROR"


class TimeoutChildPort:
    """A strict child whose first wait always reaches timeout handling."""

    def __init__(self, trigger: StartedChildTrigger, scenario: TerminationScenario) -> None:
        self._trigger = trigger
        self._scenario = scenario
        self._wait_count = 0
        self.kill_count = 0
        self.wait_timeouts: list[float] = []

    def wait(self, timeout_seconds: float) -> int:
        self._wait_count += 1
        self.wait_timeouts.append(timeout_seconds)
        if self._wait_count == 1:
            if self._trigger is StartedChildTrigger.RUN_TIMEOUT:
                raise subprocess.TimeoutExpired(("fixture",), timeout_seconds)
            raise OSError("deterministic first wait error")
        if self._scenario is TerminationScenario.REAP_TIMEOUT:
            raise subprocess.TimeoutExpired(("fixture",), timeout_seconds)
        if self._scenario is TerminationScenario.REAP_OS_ERROR:
            raise OSError("deterministic reap error")
        return 137

    def kill(self) -> None:
        self.kill_count += 1
        if self._scenario is TerminationScenario.KILL_OS_ERROR:
            raise OSError("deterministic kill error")


class TimeoutProcessPort:
    """Typed in-memory port limited to nondeterministic kill/reap failure tests."""

    def __init__(self, trigger: StartedChildTrigger, scenario: TerminationScenario) -> None:
        self.child = TimeoutChildPort(trigger, scenario)
        self.start_count = 0

    def start(
        self,
        invocation: ProcessInvocation,
        working_directory: EnvironmentLocator,
        overlay: EnvironmentOverlay,
    ) -> TimeoutChildPort:
        del invocation
        del working_directory
        del overlay
        self.start_count += 1
        return self.child


class BoundedChildProcessRunnerTests(unittest.TestCase):
    def test_t1_strict_request_boundary_rejects_before_child_effects(self) -> None:
        allocator, lease = self._lease("environment-owner-0123456789abcdef")
        before = self._fixture_artifacts(lease)
        try:
            with self.assertRaises(ValidationError):
                AbsoluteExecutable(value="python")
            with self.assertRaises(ValidationError):
                AbsoluteExecutable(value=str(self._python_executable().path) + "\x00.exe")
            with self.assertRaises(ValidationError):
                ImmutableArguments.model_validate({"values": "fixture success"})
            with self.assertRaises(ValidationError):
                ImmutableArguments(values=(str(FIXTURE_CHILD), ""))
            with self.assertRaises(ValidationError):
                ImmutableArguments(values=(str(FIXTURE_CHILD), "bad\x00argument"))
            with self.assertRaises(ValidationError):
                self._request_with(
                    lease,
                    self._python_executable(),
                    (str(FIXTURE_CHILD), "success"),
                    EnvironmentLocator(value=str(REPOSITORY_ROOT)),
                    500,
                )
            non_exact_overlay = lease.overlay.model_copy(update={"entries": tuple(reversed(lease.overlay.entries))})
            with self.assertRaises(ValidationError):
                ChildProcessRequest(
                    lease=lease,
                    executable=self._python_executable(),
                    arguments=ImmutableArguments(values=(str(FIXTURE_CHILD), "success")),
                    working_directory=lease.profile.absolute,
                    overlay=non_exact_overlay,
                    timeout=BoundedTimeoutMilliseconds(value=500),
                    termination_timeout=BoundedTimeoutMilliseconds(value=500),
                )
            with self.assertRaises(ValidationError):
                BoundedTimeoutMilliseconds(value=0)
            with self.assertRaises(ValidationError):
                self._request(lease, arguments=(str(FIXTURE_CHILD), "success"), timeout=0)
            with self.assertRaises(ValidationError):
                self._request(lease, arguments=(str(FIXTURE_CHILD), "success"), termination_timeout=0)
            valid = self._request(lease, arguments=(str(FIXTURE_CHILD), "success", "unchanged"))
            self.assertEqual((str(FIXTURE_CHILD), "success", "unchanged"), valid.arguments.values)
            self.assertEqual(before, self._fixture_artifacts(lease))
        finally:
            self._teardown(allocator, lease)

    def test_t2_real_fixture_receives_exact_argv_cwd_and_owned_overlay(self) -> None:
        allocator, lease = self._lease("environment-owner-1111222233334444")
        parent_snapshot = {key: os.environ.get(key) for key in OVERLAY_KEYS}
        with tempfile.NamedTemporaryFile(prefix="process-runner-sibling-", delete=False) as sibling:
            sibling.write(b"outside root")
            sibling.flush()
            sibling_path = Path(sibling.name)
        try:
            arguments = (str(FIXTURE_CHILD), "success", "alpha", "beta")
            observation = self._runner().run(self._request(lease, arguments=arguments))
            self.assertIsInstance(observation, SuccessfulProcessObservation)
            assert isinstance(observation, SuccessfulProcessObservation)
            self.assertEqual(arguments, observation.invocation.original_arguments.values)
            self.assertEqual((self._python_executable().value, *arguments), observation.invocation.effective_argv.values)
            complete = self._fixture_path(lease, "fixture-complete.json")
            evidence = FixtureObservation.from_json(complete.read_text(encoding="utf-8"))
            self.assertEqual(("success", "alpha", "beta"), evidence.arguments)
            self.assertEqual(lease.profile.absolute.value, evidence.working_directory)
            expected_overlay = tuple(
                FixtureOverlayEntry(key=entry.key.value, value=entry.path.value) for entry in lease.overlay.entries
            )
            self.assertEqual(expected_overlay, evidence.overlay)
            self.assertEqual(tuple(sorted(OVERLAY_KEYS)), evidence.environment_keys)
            self.assertEqual(parent_snapshot, {key: os.environ.get(key) for key in OVERLAY_KEYS})
            self.assertEqual(b"outside root", sibling_path.read_bytes())
        finally:
            sibling_path.unlink()
            self._teardown(allocator, lease)

    def test_t3_success_nonzero_and_timeout_are_distinct_and_timeout_has_no_late_completion(self) -> None:
        runner = self._runner()
        success_allocator, success_lease = self._lease("environment-owner-2222333344445555")
        nonzero_allocator, nonzero_lease = self._lease("environment-owner-3333444455556666")
        timeout_allocator, timeout_lease = self._lease("environment-owner-4444555566667777")
        try:
            success = runner.run(self._request(success_lease, arguments=(str(FIXTURE_CHILD), "success")))
            nonzero = runner.run(self._request(nonzero_lease, arguments=(str(FIXTURE_CHILD), "nonzero")))
            timeout = runner.run(
                self._request(timeout_lease, arguments=(str(FIXTURE_CHILD), "timeout"), timeout=500)
            )
            self.assertIsInstance(success, SuccessfulProcessObservation)
            self.assertIsInstance(nonzero, NonzeroProcessObservation)
            self.assertIsInstance(timeout, TimedOutProcessObservation)
            assert isinstance(nonzero, NonzeroProcessObservation)
            self.assertEqual(7, nonzero.exit_code.value)
            self.assertTrue(self._fixture_path(timeout_lease, "fixture-started.json").exists())
            time.sleep(LATE_WRITE_DELAY_SECONDS + 0.2)
            self.assertFalse(self._fixture_path(timeout_lease, "fixture-complete.json").exists())
        finally:
            self._teardown(success_allocator, success_lease)
            self._teardown(nonzero_allocator, nonzero_lease)
            self._teardown(timeout_allocator, timeout_lease)

    def test_t3_windows_launch_errors_use_winerror_not_exception_class(self) -> None:
        runner = self._runner()
        missing_allocator, missing_lease = self._lease("environment-owner-5555666677778888")
        denied_allocator, denied_lease = self._lease("environment-owner-6666777788889999")
        generic_allocator, generic_lease = self._lease("environment-owner-777788889999aaaa")
        try:
            missing = runner.run(
                self._request_with(
                    missing_lease,
                    AbsoluteExecutable(value=str(missing_lease.root.path / "missing.exe")),
                    (),
                    missing_lease.profile.absolute,
                    500,
                )
            )
            denied = runner.run(
                self._request_with(
                    denied_lease,
                    AbsoluteExecutable(value=denied_lease.profile.absolute.value),
                    (),
                    denied_lease.profile.absolute,
                    500,
                )
            )
            oversized = "x" * 40_000
            generic = runner.run(
                self._request(generic_lease, arguments=(str(FIXTURE_CHILD), "success", oversized))
            )
            self.assertIsInstance(missing, ExecutableUnavailableObservation)
            self.assertIsInstance(denied, AccessDeniedObservation)
            self.assertIsInstance(generic, GenericLaunchFailureObservation)
            assert isinstance(missing, ExecutableUnavailableObservation)
            assert isinstance(denied, AccessDeniedObservation)
            assert isinstance(generic, GenericLaunchFailureObservation)
            self.assertIn(missing.launch.winerror, (2, 3))
            self.assertEqual(5, denied.launch.winerror)
            self.assertEqual(206, generic.launch.winerror)
        finally:
            self._teardown(missing_allocator, missing_lease)
            self._teardown(denied_allocator, denied_lease)
            self._teardown(generic_allocator, generic_lease)

    def test_t4_every_outcome_has_exact_invocation_and_no_raw_output(self) -> None:
        outcomes = self._all_real_outcomes()
        for observation in outcomes:
            with self.subTest(result=observation.result.value):
                self.assertTrue(observation.invocation.executable.path.is_absolute())
                self.assertEqual(
                    (observation.invocation.executable.value, *observation.invocation.original_arguments.values),
                    observation.invocation.effective_argv.values,
                )
                serialized = observation.model_dump()
                self.assertNotIn("stdout", serialized)
                self.assertNotIn("stderr", serialized)
        self.assertEqual(set(), self._owned_environment_roots())

    def test_r02_t2_live_cwd_junction_after_request_construction_blocks_before_child_start(self) -> None:
        allocator, lease = self._lease("environment-owner-0123456789abcdef")
        request = self._request(lease, arguments=(str(FIXTURE_CHILD), "success"))
        target = Path(tempfile.mkdtemp(prefix="process-runner-junction-target-"))
        source = lease.profile.absolute.path
        try:
            source.rmdir()
            self._make_junction(source, target)
            observation = self._runner().run(request)
            self.assertIsInstance(observation, GenericLaunchFailureObservation)
            self.assertFalse(self._fixture_path(lease, "fixture-started.json").exists())
            self.assertEqual((), tuple(target.iterdir()))
        finally:
            self._restore_child_junction(source, target)
            self._teardown(allocator, lease)

    def test_r02_t2_live_root_junction_is_rejected_before_process_port(self) -> None:
        allocator, lease = self._lease("environment-owner-abcdaaaa11112222")
        root = lease.root.path
        runtime_parent = root.parent
        target = Path(tempfile.mkdtemp(prefix="process-runner-junction-target-"))
        child_names = ("profile", "local-app-data", "roaming-app-data", "temp", "codex-home")
        try:
            self._teardown(allocator, lease)
            runtime_parent.mkdir()
            for name in child_names:
                (target / name).mkdir()
            (target / ".johnny-stage-env-owner.json").write_text(
                lease.marker.model_dump_json(warnings=False),
                encoding="utf-8",
            )
            self._make_junction(root, target)
            with self.assertRaises(ValidationError):
                self._request(lease, arguments=(str(FIXTURE_CHILD), "success"))
        finally:
            if root.exists():
                attributes = root.lstat().st_file_attributes
                self.assertNotEqual(0, attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
                root.rmdir()
            marker = target / ".johnny-stage-env-owner.json"
            if marker.exists():
                marker.unlink()
            for name in child_names:
                child = target / name
                if child.exists():
                    child.rmdir()
            self.assertEqual((), tuple(target.iterdir()))
            target.rmdir()
            if runtime_parent.exists():
                self.assertEqual((), tuple(runtime_parent.iterdir()))
                runtime_parent.rmdir()

    def test_r02_t2_live_marker_tamper_after_request_construction_blocks_before_child_start(self) -> None:
        allocator, lease = self._lease("environment-owner-bbbb111122223333")
        request = self._request(lease, arguments=(str(FIXTURE_CHILD), "success"))
        foreign_marker = lease.marker.model_copy(
            update={"environment_id": EnvironmentId(value="environment-0123456789abcdef0123456789abcdef")}
        )
        try:
            lease.marker_path.write_text(foreign_marker.model_dump_json(warnings=False), encoding="utf-8")
            observation = self._runner().run(request)
            self.assertIsInstance(observation, GenericLaunchFailureObservation)
            self.assertFalse(self._fixture_path(lease, "fixture-started.json").exists())
        finally:
            lease.marker_path.write_text(lease.marker.model_dump_json(warnings=False), encoding="utf-8")
            self._teardown(allocator, lease)

    def test_r02_t2_live_each_owned_child_and_overlay_path_rejects_a_junction(self) -> None:
        allocator, lease = self._lease("environment-owner-1111222233334444")
        declared_children = (
            lease.profile.absolute.path,
            lease.local_app_data.absolute.path,
            lease.roaming_app_data.absolute.path,
            lease.temporary.absolute.path,
            lease.codex_home.absolute.path,
        )
        try:
            for source in declared_children:
                with self.subTest(child=source.name):
                    request = self._request(lease, arguments=(str(FIXTURE_CHILD), "success"))
                    target = Path(tempfile.mkdtemp(prefix="process-runner-junction-target-"))
                    try:
                        self._remove_fixture_artifacts(source)
                        source.rmdir()
                        self._make_junction(source, target)
                        observation = self._runner().run(request)
                        self.assertIsInstance(observation, GenericLaunchFailureObservation)
                        self.assertEqual((), tuple(target.iterdir()))
                    finally:
                        self._restore_child_junction(source, target)
        finally:
            self._teardown(allocator, lease)

    def test_r02_t3_injected_port_maps_all_termination_failures_without_exception(self) -> None:
        allocator, lease = self._lease("environment-owner-2222333344445555")
        expected_outcomes = {
            TerminationScenario.KILL_OS_ERROR: (TerminationFailureReason.KILL_OS_ERROR, (0.05,)),
            TerminationScenario.REAP_TIMEOUT: (TerminationFailureReason.REAP_TIMEOUT, (0.05, 0.5)),
            TerminationScenario.REAP_OS_ERROR: (TerminationFailureReason.REAP_OS_ERROR, (0.05, 0.5)),
        }
        try:
            for scenario, expected in expected_outcomes.items():
                with self.subTest(scenario=scenario.value):
                    expected_reason, expected_waits = expected
                    port = TimeoutProcessPort(StartedChildTrigger.RUN_TIMEOUT, scenario)
                    runner = BoundedChildProcessRunner(port)
                    observation = runner.run(
                        self._request(lease, arguments=(str(FIXTURE_CHILD), "timeout"), timeout=50)
                    )
                    self.assertIsInstance(observation, TerminationFailedProcessObservation)
                    assert isinstance(observation, TerminationFailedProcessObservation)
                    self.assertEqual(TerminationFailureReason, type(observation.termination_reason))
                    self.assertEqual(ChildStartState.STARTED, observation.started)
                    self.assertEqual(
                        (self._python_executable().value, str(FIXTURE_CHILD), "timeout"),
                        observation.invocation.effective_argv.values,
                    )
                    self.assertEqual(1, port.start_count)
                    self.assertEqual(1, port.child.kill_count)
                    self.assertEqual(expected_reason, observation.termination_reason)
                    self.assertEqual(StartedChildTrigger.RUN_TIMEOUT, observation.trigger)
                    self.assertEqual(ChildTerminationState.UNCONFIRMED, observation.child_state)
                    self.assertEqual(expected_waits, tuple(port.child.wait_timeouts))
                    self.assertNotIn("stdout", observation.model_dump())
                    self.assertNotIn("stderr", observation.model_dump())
        finally:
            self._teardown(allocator, lease)

    def test_r03_t3_run_wait_os_error_is_not_a_confirmed_timeout(self) -> None:
        allocator, lease = self._lease("environment-owner-3333444455556666")
        try:
            port = TimeoutProcessPort(StartedChildTrigger.RUN_WAIT_OS_ERROR, TerminationScenario.NONE)
            observation = BoundedChildProcessRunner(port).run(
                self._request(lease, arguments=(str(FIXTURE_CHILD), "timeout"), timeout=50)
            )
            self.assertIsInstance(observation, WaitFailedAfterStartObservation)
            assert isinstance(observation, WaitFailedAfterStartObservation)
            self.assertEqual(ChildStartState.STARTED, observation.started)
            self.assertEqual(ChildTerminationState.CONFIRMED_TERMINATED, observation.child_state)
            self.assertEqual(WaitFailureReason.WAIT_OS_ERROR, observation.reason)
            self.assertEqual(137, observation.exit_code.value)
            self.assertEqual(1, port.start_count)
            self.assertEqual(1, port.child.kill_count)
            self.assertEqual((0.05, 0.5), tuple(port.child.wait_timeouts))
        finally:
            self._teardown(allocator, lease)

    def test_r03_t3_every_unconfirmed_cleanup_failure_carries_its_first_wait_trigger(self) -> None:
        allocator, lease = self._lease("environment-owner-4444555566667777")
        expected_reasons = {
            TerminationScenario.KILL_OS_ERROR: "KILL_OS_ERROR",
            TerminationScenario.REAP_TIMEOUT: "REAP_TIMEOUT",
            TerminationScenario.REAP_OS_ERROR: "REAP_OS_ERROR",
        }
        try:
            for trigger in StartedChildTrigger:
                for scenario, expected_reason in expected_reasons.items():
                    with self.subTest(trigger=trigger.value, scenario=scenario.value):
                        port = TimeoutProcessPort(trigger, scenario)
                        observation = BoundedChildProcessRunner(port).run(
                            self._request(lease, arguments=(str(FIXTURE_CHILD), "timeout"), timeout=50)
                        )
                        self.assertIsInstance(observation, TerminationFailedProcessObservation)
                        assert isinstance(observation, TerminationFailedProcessObservation)
                        self.assertEqual(expected_reason, observation.termination_reason.value)
                        self.assertEqual(trigger, observation.trigger)
                        self.assertEqual(ChildTerminationState.UNCONFIRMED, observation.child_state)
                        self.assertEqual(1, port.child.kill_count)
        finally:
            self._teardown(allocator, lease)

    def _all_real_outcomes(self) -> tuple[ProcessObservation, ...]:
        runner = self._runner()
        definitions = (
            ("environment-owner-88889999aaaabbbb", "success"),
            ("environment-owner-9999aaaabbbbcccc", "nonzero"),
            ("environment-owner-aaaabbbbccccdddd", "timeout"),
        )
        outcomes: list[ProcessObservation] = []
        active: list[tuple[DisposableEnvironmentAllocator, EnvironmentLease]] = []
        try:
            for owner, mode in definitions:
                allocator, lease = self._lease(owner)
                active.append((allocator, lease))
                timeout = 50 if mode == "timeout" else 500
                outcomes.append(runner.run(self._request(lease, arguments=(str(FIXTURE_CHILD), mode), timeout=timeout)))
            missing_allocator, missing_lease = self._lease("environment-owner-bbbbccccddddeeee")
            active.append((missing_allocator, missing_lease))
            outcomes.append(
                runner.run(
                    self._request_with(
                        missing_lease,
                        AbsoluteExecutable(value=str(missing_lease.root.path / "missing.exe")),
                        (),
                        missing_lease.profile.absolute,
                        500,
                    )
                )
            )
            denied_allocator, denied_lease = self._lease("environment-owner-ccccddddeeeeffff")
            active.append((denied_allocator, denied_lease))
            outcomes.append(
                runner.run(
                    self._request_with(
                        denied_lease,
                        AbsoluteExecutable(value=denied_lease.profile.absolute.value),
                        (),
                        denied_lease.profile.absolute,
                        500,
                    )
                )
            )
            generic_allocator, generic_lease = self._lease("environment-owner-ddddeeeeffff0000")
            active.append((generic_allocator, generic_lease))
            oversized = "x" * 40_000
            outcomes.append(
                runner.run(self._request(generic_lease, arguments=(str(FIXTURE_CHILD), "success", oversized)))
            )
            return tuple(outcomes)
        finally:
            for allocator, lease in active:
                self._teardown(allocator, lease)

    @staticmethod
    def _python_executable() -> AbsoluteExecutable:
        return AbsoluteExecutable(value=str(Path(sys.executable).resolve(strict=True)))

    def _request(
        self,
        lease: EnvironmentLease,
        arguments: tuple[str, ...] = (),
        timeout: int = 500,
        termination_timeout: int = 500,
    ) -> ChildProcessRequest:
        return self._request_with(
            lease,
            self._python_executable(),
            arguments,
            lease.profile.absolute,
            timeout,
            termination_timeout,
        )

    @staticmethod
    def _request_with(
        lease: EnvironmentLease,
        executable: AbsoluteExecutable,
        arguments: tuple[str, ...],
        working_directory: EnvironmentLocator,
        timeout: int,
        termination_timeout: int = 500,
    ) -> ChildProcessRequest:
        return ChildProcessRequest(
            lease=lease,
            executable=executable,
            arguments=ImmutableArguments(values=arguments),
            working_directory=working_directory,
            overlay=lease.overlay,
            timeout=BoundedTimeoutMilliseconds(value=timeout),
            termination_timeout=BoundedTimeoutMilliseconds(value=termination_timeout),
        )

    @staticmethod
    def _runner() -> BoundedChildProcessRunner:
        return BoundedChildProcessRunner(SubprocessProcessPort())

    def _lease(self, owner: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease]:
        allocator = DisposableEnvironmentAllocator.from_project_runtime()
        provisioned = allocator.provision(EnvironmentOwnerId(value=owner))
        self.assertIsInstance(provisioned, ProvisionedEnvironment)
        assert isinstance(provisioned, ProvisionedEnvironment)
        return allocator, provisioned.environment

    def _teardown(self, allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
        result = allocator.teardown(lease)
        self.assertEqual(TeardownStatus.REMOVED, result.status)

    def _make_junction(self, source: Path, target: Path) -> None:
        result = subprocess.run(
            ("cmd.exe", "/d", "/c", "mklink", "/J", str(source), str(target)),
            shell=False,
            check=False,
            capture_output=True,
            timeout=5,
        )
        stderr = (result.stderr or b"").decode("utf-8", errors="replace")
        self.assertEqual(0, result.returncode, stderr)
        attributes = source.lstat().st_file_attributes
        self.assertNotEqual(0, attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

    def _restore_child_junction(self, source: Path, target: Path) -> None:
        if source.exists():
            attributes = source.lstat().st_file_attributes
            if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                source.rmdir()
                source.mkdir()
        else:
            source.mkdir()
        self._remove_fixture_artifacts(target)
        self.assertEqual((), tuple(target.iterdir()))
        target.rmdir()

    @staticmethod
    def _remove_fixture_artifacts(directory: Path) -> None:
        for name in ("fixture-started.json", "fixture-complete.json"):
            artifact = directory / name
            if artifact.exists():
                artifact.unlink()

    @staticmethod
    def _fixture_path(lease: EnvironmentLease, name: str) -> Path:
        return lease.codex_home.absolute.path / name

    def _fixture_artifacts(self, lease: EnvironmentLease) -> set[Path]:
        return {
            path
            for path in lease.codex_home.absolute.path.iterdir()
            if path.name in {"fixture-started.json", "fixture-complete.json"}
        }

    @staticmethod
    def _owned_environment_roots() -> set[Path]:
        temporary_parent = (REPOSITORY_ROOT / "tests" / ".johnny-runtime").resolve()
        if not temporary_parent.exists():
            return set()
        return {
            child
            for child in temporary_parent.iterdir()
            if child.is_dir() and child.name.startswith(ENVIRONMENT_PREFIX)
        }


if __name__ == "__main__":
    unittest.main()
