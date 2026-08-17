from __future__ import annotations

from unittest import TestCase

from pydantic import TypeAdapter, ValidationError

from library.local_orchestration.project_runner_registry import (
    ProjectRunnerRegistry,
    ProjectRunnerRegistryDecision,
    ProjectRunnerRegistryResult,
    RunnerStartCapabilityUnavailable,
    RunnerStartResult,
    RunnerStarted,
    RunnerStopCapabilityUnavailable,
    RunnerStopResult,
    RunnerStopped,
)
from library.workflow_router.contracts import OpaqueMetadataId, ProjectId


_PROJECT_ALPHA: ProjectId = "prj_aaaaaaaaaaaaaaaa"
_PROJECT_BETA: ProjectId = "prj_bbbbbbbbbbbbbbbb"


class _RecordingLifecycle:
    def __init__(
        self,
        start_result: RunnerStartResult | None = None,
        stop_result: RunnerStopResult | None = None,
    ) -> None:
        self.starts: list[ProjectId] = []
        self.stops: list[tuple[ProjectId, str]] = []
        self.start_result: RunnerStartResult = start_result or RunnerStarted(
            runner_ref="runner-alpha"
        )
        self.stop_result: RunnerStopResult = stop_result or RunnerStopped()

    def start(self, project_ref: ProjectId) -> RunnerStartResult:
        self.starts.append(project_ref)
        return self.start_result

    def stop(
        self,
        project_ref: ProjectId,
        runner_ref: OpaqueMetadataId,
    ) -> RunnerStopResult:
        self.stops.append((project_ref, runner_ref))
        return self.stop_result


class ProjectRunnerRegistryTests(TestCase):
    def test_project_id_is_required_and_receipt_compatible(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        accepted = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")

        self.assertEqual(accepted.project_ref, _PROJECT_ALPHA)
        with self.assertRaises(ValidationError):
            registry.register_subscription("project-alpha", "subscription-invalid")
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])

    def test_first_subscription_starts_once_and_binds_runner(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        result = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")

        self.assertEqual(result.decision, ProjectRunnerRegistryDecision.SUBSCRIBED)
        self.assertEqual(result.project_ref, _PROJECT_ALPHA)
        self.assertEqual(result.subscription_id, "subscription-one")
        self.assertEqual(result.runner_ref, "runner-alpha")
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])
        self.assertEqual(lifecycle.stops, [])

    def test_second_runner_for_same_project_is_rejected_before_start(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        first = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        second = registry.register_subscription(_PROJECT_ALPHA, "subscription-two")

        self.assertEqual(first.decision, ProjectRunnerRegistryDecision.SUBSCRIBED)
        self.assertEqual(second.decision, ProjectRunnerRegistryDecision.REUSED)
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])
        self.assertEqual(lifecycle.stops, [])

    def test_duplicate_and_foreign_subscriptions_do_not_mutate_peers(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        duplicate = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        foreign = registry.register_subscription(_PROJECT_BETA, "subscription-one")

        self.assertEqual(
            duplicate.decision,
            ProjectRunnerRegistryDecision.DUPLICATE_SUBSCRIPTION,
        )
        self.assertEqual(
            foreign.decision,
            ProjectRunnerRegistryDecision.FOREIGN_SUBSCRIPTION,
        )
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])
        self.assertEqual(lifecycle.stops, [])
        foreign_removal = registry.remove_subscription(_PROJECT_BETA, "subscription-one")
        self.assertEqual(
            foreign_removal.decision,
            ProjectRunnerRegistryDecision.FOREIGN_SUBSCRIPTION,
        )
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])
        self.assertEqual(lifecycle.stops, [])
        retained_duplicate = registry.register_subscription(
            _PROJECT_ALPHA, "subscription-one"
        )
        self.assertEqual(
            retained_duplicate.decision,
            ProjectRunnerRegistryDecision.DUPLICATE_SUBSCRIPTION,
        )
        self.assertEqual(retained_duplicate.runner_ref, "runner-alpha")
        retained = registry.register_subscription(_PROJECT_ALPHA, "subscription-two")
        self.assertEqual(retained.decision, ProjectRunnerRegistryDecision.REUSED)
        self.assertEqual(retained.runner_ref, "runner-alpha")
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA])

    def test_unavailable_start_retains_no_state(self) -> None:
        lifecycle = _RecordingLifecycle(start_result=RunnerStartCapabilityUnavailable())
        registry = ProjectRunnerRegistry(lifecycle)

        blocked = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")

        self.assertEqual(
            blocked.decision,
            ProjectRunnerRegistryDecision.RUNNER_START_UNAVAILABLE,
        )
        self.assertIsNone(blocked.subscription_id)
        self.assertIsNone(blocked.runner_ref)
        lifecycle.start_result = RunnerStarted(runner_ref="runner-alpha")
        retried = registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        self.assertEqual(retried.decision, ProjectRunnerRegistryDecision.SUBSCRIBED)
        self.assertEqual(lifecycle.starts, [_PROJECT_ALPHA, _PROJECT_ALPHA])

    def test_nonfinal_and_final_removal_have_distinct_stop_effects(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)
        registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        registry.register_subscription(_PROJECT_ALPHA, "subscription-two")

        nonfinal = registry.remove_subscription(_PROJECT_ALPHA, "subscription-one")
        self.assertEqual(nonfinal.decision, ProjectRunnerRegistryDecision.REMOVED)
        self.assertEqual(lifecycle.stops, [])

        final = registry.remove_subscription(_PROJECT_ALPHA, "subscription-two")
        self.assertEqual(final.decision, ProjectRunnerRegistryDecision.REMOVED)
        self.assertEqual(lifecycle.stops, [(_PROJECT_ALPHA, "runner-alpha")])
        missing = registry.remove_subscription(_PROJECT_ALPHA, "subscription-two")
        self.assertEqual(missing.decision, ProjectRunnerRegistryDecision.NOT_FOUND)
        self.assertEqual(lifecycle.stops, [(_PROJECT_ALPHA, "runner-alpha")])

    def test_detach_and_uninstall_stop_only_their_project(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)
        registry.register_subscription(_PROJECT_ALPHA, "subscription-one")

        detached = registry.detach_project(_PROJECT_ALPHA)

        self.assertEqual(detached.decision, ProjectRunnerRegistryDecision.DETACHED)
        self.assertEqual(lifecycle.stops, [(_PROJECT_ALPHA, "runner-alpha")])
        missing = registry.detach_project(_PROJECT_ALPHA)
        self.assertEqual(missing.decision, ProjectRunnerRegistryDecision.NOT_FOUND)
        registry.register_subscription(_PROJECT_BETA, "subscription-two")
        uninstalled = registry.uninstall_project(_PROJECT_BETA)
        self.assertEqual(uninstalled.decision, ProjectRunnerRegistryDecision.UNINSTALLED)
        self.assertEqual(
            lifecycle.stops,
            [(_PROJECT_ALPHA, "runner-alpha"), (_PROJECT_BETA, "runner-alpha")],
        )

    def test_unavailable_stop_retains_project_and_preserves_peer(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)
        registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        registry.register_subscription(_PROJECT_BETA, "subscription-two")
        lifecycle.stop_result = RunnerStopCapabilityUnavailable()

        blocked = registry.detach_project(_PROJECT_ALPHA)

        self.assertEqual(
            blocked.decision,
            ProjectRunnerRegistryDecision.RUNNER_STOP_UNAVAILABLE,
        )
        self.assertEqual(lifecycle.stops, [(_PROJECT_ALPHA, "runner-alpha")])
        lifecycle.stop_result = RunnerStopped()
        removed_peer = registry.remove_subscription(_PROJECT_BETA, "subscription-two")
        self.assertEqual(removed_peer.decision, ProjectRunnerRegistryDecision.REMOVED)
        self.assertEqual(
            lifecycle.stops,
            [
                (_PROJECT_ALPHA, "runner-alpha"),
                (_PROJECT_BETA, "runner-alpha"),
            ],
        )
        retained = registry.remove_subscription(_PROJECT_ALPHA, "subscription-one")
        self.assertEqual(retained.decision, ProjectRunnerRegistryDecision.REMOVED)

    def test_fresh_registry_has_no_lifecycle_effect_or_recovery_api(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        self.assertEqual(lifecycle.starts, [])
        self.assertEqual(lifecycle.stops, [])
        missing = registry.uninstall_project(_PROJECT_ALPHA)
        self.assertEqual(missing.decision, ProjectRunnerRegistryDecision.NOT_FOUND)
        self.assertEqual(lifecycle.starts, [])
        self.assertEqual(lifecycle.stops, [])
        self.assertFalse(hasattr(registry, "recover_runner"))

    def test_public_values_round_trip_and_bypassed_values_reject(self) -> None:
        start = RunnerStarted(runner_ref="runner-alpha")
        start_round_trip = RunnerStarted.model_validate_json(start.model_dump_json())
        unavailable = RunnerStartCapabilityUnavailable()
        unavailable_round_trip = RunnerStartCapabilityUnavailable.model_validate_json(
            unavailable.model_dump_json()
        )
        stop = RunnerStopped()
        stop_round_trip = RunnerStopped.model_validate_json(stop.model_dump_json())
        stop_unavailable = RunnerStopCapabilityUnavailable()
        stop_unavailable_round_trip = RunnerStopCapabilityUnavailable.model_validate_json(
            stop_unavailable.model_dump_json()
        )
        result = ProjectRunnerRegistryResult(
            decision=ProjectRunnerRegistryDecision.SUBSCRIBED,
            project_ref=_PROJECT_ALPHA,
            subscription_id="subscription-one",
            runner_ref="runner-alpha",
        )
        result_round_trip = ProjectRunnerRegistryResult.model_validate_json(
            result.model_dump_json()
        )

        self.assertEqual(start_round_trip, start)
        self.assertEqual(unavailable_round_trip, unavailable)
        self.assertEqual(stop_round_trip, stop)
        self.assertEqual(stop_unavailable_round_trip, stop_unavailable)
        self.assertEqual(result_round_trip, result)
        self.assertEqual(
            TypeAdapter(RunnerStartResult).validate_json(start.model_dump_json()),
            start,
        )
        self.assertEqual(
            TypeAdapter(RunnerStopResult).validate_json(stop.model_dump_json()),
            stop,
        )

        malformed_start = RunnerStarted.model_construct(runner_ref="not valid")
        malformed_lifecycle = _RecordingLifecycle(start_result=malformed_start)
        with self.assertRaises(ValidationError):
            ProjectRunnerRegistry(malformed_lifecycle).register_subscription(
                _PROJECT_ALPHA, "subscription-one"
            )
        malformed_stop = RunnerStopped.model_construct(status="BROKEN")
        malformed_stop_lifecycle = _RecordingLifecycle(stop_result=malformed_stop)
        malformed_stop_registry = ProjectRunnerRegistry(malformed_stop_lifecycle)
        malformed_stop_registry.register_subscription(_PROJECT_ALPHA, "subscription-one")
        with self.assertRaises(ValidationError):
            malformed_stop_registry.remove_subscription(_PROJECT_ALPHA, "subscription-one")
        with self.assertRaises(ValidationError):
            RunnerStartCapabilityUnavailable(runner_ref="runner-alpha")
        with self.assertRaises(ValidationError):
            ProjectRunnerRegistryResult(
                decision=ProjectRunnerRegistryDecision.RUNNER_START_UNAVAILABLE,
                project_ref=_PROJECT_ALPHA,
                subscription_id="subscription-one",
                runner_ref=None,
            )
        bypassed_result = ProjectRunnerRegistryResult.model_construct(
            decision=ProjectRunnerRegistryDecision.SUBSCRIBED,
            project_ref="not valid",
            subscription_id=None,
            runner_ref=None,
        )
        with self.assertRaises(ValidationError):
            ProjectRunnerRegistryResult.model_validate(bypassed_result, strict=True)

    def test_invalid_public_ids_are_rejected_before_lifecycle_call(self) -> None:
        lifecycle = _RecordingLifecycle()
        registry = ProjectRunnerRegistry(lifecycle)

        with self.assertRaises(ValidationError):
            registry.register_subscription("", "subscription-one")
        with self.assertRaises(ValidationError):
            registry.register_subscription("project-alpha", " ")
        with self.assertRaises(ValidationError):
            registry.detach_project("PROJECT-ALPHA")
        self.assertEqual(lifecycle.starts, [])
        self.assertEqual(lifecycle.stops, [])
