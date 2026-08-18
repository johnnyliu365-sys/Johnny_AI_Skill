"""Johnny Router composition-root closure tests for CLOSURE-PD-10-R04-01."""

from __future__ import annotations

import unittest
from dataclasses import fields
from typing import cast

from library.local_orchestration.git_handoff_event_adapter import (
    GitReadbackPort,
    NativeGitRefNotificationPort,
    ReceiptBoundGitEventAdapter,
)
from library.local_orchestration.johnny_router_composition import (
    JohnnyRouterComposition,
    JohnnyRouterCompositionFailure,
    JohnnyRouterCompositionPorts,
    JohnnyRouterCompositionResult,
    JohnnyRouterCompositionStatus,
    build_johnny_router,
)
from library.local_orchestration.plugin_bundle_builder import PluginBundleBuilder
from library.local_orchestration.project_runner_registry import (
    ProjectRunnerRegistry,
    RunnerLifecyclePort,
    RunnerStartResult,
    RunnerStopResult,
)
from library.local_orchestration.project_subscription_runtime import (
    ProjectSubscriptionRuntime,
)
from library.local_orchestration.role_wake_composition import (
    RoleWakeAttemptBoundaryPort,
    RoleWakeCoordinator,
    RoleWakePort,
)
from library.local_orchestration.runtime_dependency_lock import (
    RuntimeDependencyLock,
    build_approved_runtime_lock,
)
from library.local_orchestration.senior_review_inbox import (
    ReviewClusterBindingResolverPort,
    SeniorReviewInboxCoordinator,
    SeniorReviewInboxStorePort,
)
from library.workflow_router.contracts import OpaqueMetadataId, ProjectId
from library.workflow_router.git_handoff_contracts import (
    GitAncestryResult,
    GitBlobReadResult,
    GitNativeRegistrationRequest,
    GitNativeRegistrationResult,
    GitPathChangeResult,
    GitRefSnapshotResult,
    SubscriptionId,
)
from library.workflow_router.profile import (
    ProjectWorkflowProfile,
    build_plugin_distribution_profile,
)
from library.workflow_router.review_inbox_contracts import (
    CommittedReviewTicketEvent,
    ReviewBatchClaimRequest,
    ReviewBatchClaimResult,
    ReviewBatchDecisionRequest,
    ReviewBatchDecisionResult,
    ReviewEventResolutionRequest,
    ReviewEventResolutionResult,
    ReviewInboxAdmissionResult,
    ReviewInspectionRequest,
    ReviewInspectionResult,
    ReviewWakeSettlementRequest,
    ReviewWakeSettlementResult,
    SeniorReviewInboxState,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeAttemptClaimRequest,
    RoleWakeAttemptClaimResult,
    RoleWakeAttemptSettleRequest,
    RoleWakeAttemptSettleResult,
    RoleWakeCommand,
    RoleWakeEffectResult,
)

_PORT_EFFECT = "an injected port must not be invoked during ordinary composition"


class _CountingRunnerLifecycle(RunnerLifecyclePort):
    """Counting runner lifecycle fake; every invocation is a closure violation."""

    def __init__(self) -> None:
        self.calls = 0

    def start(self, project_ref: ProjectId) -> RunnerStartResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def stop(
        self,
        project_ref: ProjectId,
        runner_ref: OpaqueMetadataId,
    ) -> RunnerStopResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingGitReadback(GitReadbackPort):
    """Counting Git readback fake behind the real receipt-bound adapter."""

    def __init__(self) -> None:
        self.calls = 0

    def read_ref(self, exact_git_ref: str) -> GitRefSnapshotResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def path_changed(
        self,
        prior_commit: str,
        observed_commit: str,
        exact_path: str,
    ) -> GitPathChangeResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def read_blob(self, commit_id: str, exact_path: str) -> GitBlobReadResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def is_ancestor(self, ancestor: str, descendant: str) -> GitAncestryResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingNativeGitRef(NativeGitRefNotificationPort):
    """Counting native ref-notification fake behind the real adapter."""

    def __init__(self) -> None:
        self.calls = 0

    def register(
        self,
        request: GitNativeRegistrationRequest,
    ) -> GitNativeRegistrationResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def cancel(self, subscription_id: SubscriptionId) -> bool:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingReviewStore(SeniorReviewInboxStorePort):
    """Counting Senior review inbox store fake."""

    def __init__(self) -> None:
        self.calls = 0

    def admit_event(
        self,
        event: CommittedReviewTicketEvent,
    ) -> ReviewInboxAdmissionResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def settle_wake(
        self,
        request: ReviewWakeSettlementRequest,
    ) -> ReviewWakeSettlementResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def claim_batch(self, request: ReviewBatchClaimRequest) -> ReviewBatchClaimResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def record_inspection(
        self,
        request: ReviewInspectionRequest,
    ) -> ReviewInspectionResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def decide_batch(
        self,
        request: ReviewBatchDecisionRequest,
    ) -> ReviewBatchDecisionResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def read_state(
        self,
        project_id: str,
        reviewer_ref: str,
    ) -> SeniorReviewInboxState | None:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingReviewResolver(ReviewClusterBindingResolverPort):
    """Counting review cluster binding resolver fake."""

    def __init__(self) -> None:
        self.calls = 0

    def resolve(
        self,
        request: ReviewEventResolutionRequest,
    ) -> ReviewEventResolutionResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingWakeAttemptBoundary(RoleWakeAttemptBoundaryPort):
    """Counting durable wake-attempt boundary fake."""

    def __init__(self) -> None:
        self.calls = 0

    def claim_role_wake_attempt(
        self,
        request: RoleWakeAttemptClaimRequest,
    ) -> RoleWakeAttemptClaimResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)

    def settle_role_wake_attempt(
        self,
        request: RoleWakeAttemptSettleRequest,
    ) -> RoleWakeAttemptSettleResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _CountingHostWakePort(RoleWakePort):
    """Counting host wake bridge fake."""

    def __init__(self) -> None:
        self.calls = 0

    def wake(self, command: RoleWakeCommand) -> RoleWakeEffectResult:
        self.calls += 1
        raise AssertionError(_PORT_EFFECT)


class _PortFixture:
    """One complete set of counting fakes plus the assembled ports value."""

    def __init__(self) -> None:
        self.runner_lifecycle = _CountingRunnerLifecycle()
        self.git_readback = _CountingGitReadback()
        self.native_git_ref = _CountingNativeGitRef()
        self.git_adapter = ReceiptBoundGitEventAdapter(
            self.git_readback,
            self.native_git_ref,
        )
        self.review_store = _CountingReviewStore()
        self.review_resolver = _CountingReviewResolver()
        self.wake_attempt_boundary = _CountingWakeAttemptBoundary()
        self.host_wake_port = _CountingHostWakePort()

    def ports(self, **overrides: object) -> JohnnyRouterCompositionPorts:
        values: dict[str, object | None] = {
            "runner_lifecycle": self.runner_lifecycle,
            "git_adapter": self.git_adapter,
            "review_store": self.review_store,
            "review_resolver": self.review_resolver,
            "wake_attempt_boundary": self.wake_attempt_boundary,
            "host_wake_port": self.host_wake_port,
        }
        values.update(overrides)
        return JohnnyRouterCompositionPorts(
            runner_lifecycle=cast(
                "RunnerLifecyclePort | None", values["runner_lifecycle"]
            ),
            git_adapter=cast(
                "ReceiptBoundGitEventAdapter | None", values["git_adapter"]
            ),
            review_store=cast(
                "SeniorReviewInboxStorePort | None", values["review_store"]
            ),
            review_resolver=cast(
                "ReviewClusterBindingResolverPort | None", values["review_resolver"]
            ),
            wake_attempt_boundary=cast(
                "RoleWakeAttemptBoundaryPort | None", values["wake_attempt_boundary"]
            ),
            host_wake_port=cast("RoleWakePort | None", values["host_wake_port"]),
        )

    def injected_ports(self) -> tuple[object, ...]:
        return (
            self.runner_lifecycle,
            self.git_adapter,
            self.review_store,
            self.review_resolver,
            self.wake_attempt_boundary,
            self.host_wake_port,
        )

    def total_calls(self) -> int:
        return (
            self.runner_lifecycle.calls
            + self.git_readback.calls
            + self.native_git_ref.calls
            + self.review_store.calls
            + self.review_resolver.calls
            + self.wake_attempt_boundary.calls
            + self.host_wake_port.calls
        )


def _approved_inputs() -> tuple[ProjectWorkflowProfile, RuntimeDependencyLock]:
    return build_plugin_distribution_profile(), build_approved_runtime_lock()


class JohnnyRouterCompositionTests(unittest.TestCase):
    """J1-J5 closure cells for the Johnny Router composition root."""

    def _assert_blocked(
        self,
        result: JohnnyRouterCompositionResult,
        failure: JohnnyRouterCompositionFailure,
        fixture: _PortFixture,
    ) -> None:
        self.assertIs(result.status, JohnnyRouterCompositionStatus.BLOCKED)
        self.assertIs(result.failure, failure)
        self.assertIsNone(result.composition)
        self.assertEqual(fixture.total_calls(), 0)

    def test_builds_bound_components_without_port_effects(self) -> None:
        """J1+J2: exact inputs compose every component and invoke no port."""

        profile, lock = _approved_inputs()
        fixture = _PortFixture()

        result = build_johnny_router(profile, lock, fixture.ports())

        self.assertIs(result.status, JohnnyRouterCompositionStatus.COMPOSED)
        self.assertIsNone(result.failure)
        composition = result.composition
        self.assertIsNotNone(composition)
        assert composition is not None
        self.assertIs(type(composition), JohnnyRouterComposition)
        self.assertIs(type(composition.runner_registry), ProjectRunnerRegistry)
        self.assertIs(
            type(composition.subscription_runtime), ProjectSubscriptionRuntime
        )
        self.assertIs(type(composition.review_inbox), SeniorReviewInboxCoordinator)
        self.assertIs(type(composition.role_wake), RoleWakeCoordinator)
        self.assertIs(type(composition.bundle_builder), PluginBundleBuilder)
        self.assertEqual(composition.profile, profile)
        self.assertEqual(composition.runtime_lock, lock)
        self.assertEqual(fixture.total_calls(), 0)

    def test_profile_and_lock_mismatch_block_before_ports(self) -> None:
        """J3: non-approved Profile or lock values block without port effects."""

        profile, lock = _approved_inputs()

        with self.subTest(input="modified_profile"):
            fixture = _PortFixture()
            foreign_profile = profile.model_copy(
                update={"profile_version": "v999-unapproved"}
            )
            result = build_johnny_router(foreign_profile, lock, fixture.ports())
            self._assert_blocked(
                result, JohnnyRouterCompositionFailure.PROFILE_MISMATCH, fixture
            )

        with self.subTest(input="foreign_profile_object"):
            fixture = _PortFixture()
            result = build_johnny_router(
                cast(ProjectWorkflowProfile, object()), lock, fixture.ports()
            )
            self._assert_blocked(
                result, JohnnyRouterCompositionFailure.PROFILE_MISMATCH, fixture
            )

        with self.subTest(input="modified_lock"):
            fixture = _PortFixture()
            foreign_lock = lock.model_copy(update={"lock_digest": "0" * 64})
            result = build_johnny_router(profile, foreign_lock, fixture.ports())
            self._assert_blocked(
                result, JohnnyRouterCompositionFailure.RUNTIME_LOCK_MISMATCH, fixture
            )

        with self.subTest(input="foreign_lock_object"):
            fixture = _PortFixture()
            result = build_johnny_router(
                profile, cast(RuntimeDependencyLock, object()), fixture.ports()
            )
            self._assert_blocked(
                result, JohnnyRouterCompositionFailure.RUNTIME_LOCK_MISMATCH, fixture
            )

    def test_each_missing_port_blocks_with_exact_failure(self) -> None:
        """J3: each missing injected dependency returns only its own failure."""

        profile, lock = _approved_inputs()
        expected: tuple[tuple[str, JohnnyRouterCompositionFailure], ...] = (
            ("runner_lifecycle", JohnnyRouterCompositionFailure.RUNNER_PORT_UNAVAILABLE),
            ("git_adapter", JohnnyRouterCompositionFailure.GIT_ADAPTER_UNAVAILABLE),
            ("review_store", JohnnyRouterCompositionFailure.REVIEW_STORE_UNAVAILABLE),
            (
                "review_resolver",
                JohnnyRouterCompositionFailure.REVIEW_RESOLVER_UNAVAILABLE,
            ),
            (
                "wake_attempt_boundary",
                JohnnyRouterCompositionFailure.WAKE_ATTEMPT_BOUNDARY_UNAVAILABLE,
            ),
            (
                "host_wake_port",
                JohnnyRouterCompositionFailure.HOST_WAKE_PORT_UNAVAILABLE,
            ),
        )
        for field_name, failure in expected:
            with self.subTest(missing=field_name):
                fixture = _PortFixture()
                result = build_johnny_router(
                    profile, lock, fixture.ports(**{field_name: None})
                )
                self._assert_blocked(result, failure, fixture)

    def test_malformed_ports_reject_before_components(self) -> None:
        """J4: foreign or malformed dynamic inputs reject before construction."""

        profile, lock = _approved_inputs()

        class _MissingStopLifecycle:
            def start(self, project_ref: ProjectId) -> RunnerStartResult:
                raise AssertionError(_PORT_EFFECT)

        class _ForeignGitAdapter(ReceiptBoundGitEventAdapter):
            """A subtype is not the exact receipt-bound adapter value."""

        class _MissingDecideBatchStore:
            def admit_event(
                self,
                event: CommittedReviewTicketEvent,
            ) -> ReviewInboxAdmissionResult:
                raise AssertionError(_PORT_EFFECT)

        class _NonCallableResolver:
            resolve = "not-callable"

        class _MissingSettleBoundary:
            def claim_role_wake_attempt(
                self,
                request: RoleWakeAttemptClaimRequest,
            ) -> RoleWakeAttemptClaimResult:
                raise AssertionError(_PORT_EFFECT)

        class _NonCallableWake:
            wake = "not-callable"

        malformed: tuple[tuple[str, object, JohnnyRouterCompositionFailure], ...] = (
            (
                "runner_lifecycle",
                _MissingStopLifecycle(),
                JohnnyRouterCompositionFailure.RUNNER_PORT_UNAVAILABLE,
            ),
            (
                "git_adapter",
                _ForeignGitAdapter(_CountingGitReadback(), _CountingNativeGitRef()),
                JohnnyRouterCompositionFailure.GIT_ADAPTER_UNAVAILABLE,
            ),
            (
                "review_store",
                _MissingDecideBatchStore(),
                JohnnyRouterCompositionFailure.REVIEW_STORE_UNAVAILABLE,
            ),
            (
                "review_resolver",
                _NonCallableResolver(),
                JohnnyRouterCompositionFailure.REVIEW_RESOLVER_UNAVAILABLE,
            ),
            (
                "wake_attempt_boundary",
                _MissingSettleBoundary(),
                JohnnyRouterCompositionFailure.WAKE_ATTEMPT_BOUNDARY_UNAVAILABLE,
            ),
            (
                "host_wake_port",
                _NonCallableWake(),
                JohnnyRouterCompositionFailure.HOST_WAKE_PORT_UNAVAILABLE,
            ),
        )
        for field_name, foreign_value, failure in malformed:
            with self.subTest(malformed=field_name):
                fixture = _PortFixture()
                result = build_johnny_router(
                    profile, lock, fixture.ports(**{field_name: foreign_value})
                )
                self._assert_blocked(result, failure, fixture)

        with self.subTest(malformed="ports_container"):
            fixture = _PortFixture()
            result = build_johnny_router(
                profile, lock, cast(JohnnyRouterCompositionPorts, object())
            )
            self._assert_blocked(
                result,
                JohnnyRouterCompositionFailure.RUNNER_PORT_UNAVAILABLE,
                fixture,
            )

        with self.subTest(invariant="no_raw_port_exposed"):
            fixture = _PortFixture()
            result = build_johnny_router(profile, lock, fixture.ports())
            composition = result.composition
            self.assertIsNotNone(composition)
            assert composition is not None
            for composition_field in fields(composition):
                value = getattr(composition, composition_field.name)
                for injected in fixture.injected_ports():
                    self.assertIsNot(value, injected)

    def test_unavailable_host_wake_port_blocks_before_binding(self) -> None:
        """J5: an unavailable host wake port binds no subscription or inbox."""

        profile, lock = _approved_inputs()
        fixture = _PortFixture()

        result = build_johnny_router(
            profile, lock, fixture.ports(host_wake_port=None)
        )

        self._assert_blocked(
            result, JohnnyRouterCompositionFailure.HOST_WAKE_PORT_UNAVAILABLE, fixture
        )
        self.assertEqual(fixture.review_store.calls, 0)
        self.assertEqual(fixture.wake_attempt_boundary.calls, 0)
        self.assertEqual(fixture.git_readback.calls, 0)
        self.assertEqual(fixture.native_git_ref.calls, 0)


if __name__ == "__main__":
    unittest.main()
