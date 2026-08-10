"""Executable P1-P4 closure for the bounded child-process runner."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

from pydantic import ValidationError

from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentLocator,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import (
    AbsoluteExecutable,
    AccessDeniedObservation,
    BoundedTimeoutMilliseconds,
    ChildProcessRequest,
    ExecutableUnavailableObservation,
    GenericLaunchFailureObservation,
    ImmutableArguments,
    NonzeroProcessObservation,
    ProcessObservation,
    SuccessfulProcessObservation,
    TimedOutProcessObservation,
)
from tests.staging.process_runner.fixture_child import FixtureObservation, FixtureOverlayEntry
from tests.staging.process_runner.runner import BoundedChildProcessRunner


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_CHILD = Path(__file__).resolve().parent / "staging" / "process_runner" / "fixture_child.py"
OVERLAY_KEYS = ("USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", "CODEX_HOME")
ENVIRONMENT_PREFIX = "johnny-stage-env-"


class BoundedChildProcessRunnerTests(unittest.TestCase):
    def test_t1_strict_request_boundary_rejects_before_child_effects(self) -> None:
        allocator, lease = self._lease("environment-owner-0123456789abcdef")
        before = self._fixture_artifacts(lease)
        try:
            with self.assertRaises(ValidationError):
                AbsoluteExecutable(value="python")
            with self.assertRaises(ValidationError):
                ImmutableArguments.model_validate({"values": "fixture success"})
            with self.assertRaises(ValidationError):
                ImmutableArguments(values=(str(FIXTURE_CHILD), ""))
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
                )
            with self.assertRaises(ValidationError):
                BoundedTimeoutMilliseconds(value=0)
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
            observation = BoundedChildProcessRunner().run(self._request(lease, arguments=arguments))
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
        runner = BoundedChildProcessRunner()
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
            time.sleep(0.2)
            self.assertFalse(self._fixture_path(timeout_lease, "fixture-complete.json").exists())
        finally:
            self._teardown(success_allocator, success_lease)
            self._teardown(nonzero_allocator, nonzero_lease)
            self._teardown(timeout_allocator, timeout_lease)

    def test_t3_windows_launch_errors_use_winerror_not_exception_class(self) -> None:
        runner = BoundedChildProcessRunner()
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

    def _all_real_outcomes(self) -> tuple[ProcessObservation, ...]:
        runner = BoundedChildProcessRunner()
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
    ) -> ChildProcessRequest:
        return self._request_with(lease, self._python_executable(), arguments, lease.profile.absolute, timeout)

    @staticmethod
    def _request_with(
        lease: EnvironmentLease,
        executable: AbsoluteExecutable,
        arguments: tuple[str, ...],
        working_directory: EnvironmentLocator,
        timeout: int,
    ) -> ChildProcessRequest:
        return ChildProcessRequest(
            lease=lease,
            executable=executable,
            arguments=ImmutableArguments(values=arguments),
            working_directory=working_directory,
            overlay=lease.overlay,
            timeout=BoundedTimeoutMilliseconds(value=timeout),
        )

    def _lease(self, owner: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease]:
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        provisioned = allocator.provision(EnvironmentOwnerId(value=owner))
        self.assertIsInstance(provisioned, ProvisionedEnvironment)
        assert isinstance(provisioned, ProvisionedEnvironment)
        return allocator, provisioned.environment

    def _teardown(self, allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
        result = allocator.teardown(lease)
        self.assertEqual(TeardownStatus.REMOVED, result.status)

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
        temporary_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        return {
            child
            for child in temporary_parent.iterdir()
            if child.is_dir() and child.name.startswith(ENVIRONMENT_PREFIX)
        }


if __name__ == "__main__":
    unittest.main()
