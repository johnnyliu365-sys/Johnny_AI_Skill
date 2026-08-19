"""Scripted SourceProjectA qualification closure tests for CLOSURE-PD-14-R03-01."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from library.local_orchestration.johnny_router_composition import (
    JohnnyRouterCompositionStatus,
    build_johnny_router,
)
from library.local_orchestration.plugin_bundle_builder import (
    PluginBundleBuilder,
    PluginBundleBuildRequest,
    PluginBundleBuildStatus,
)
from library.local_orchestration.plugin_uninstall_transaction import (
    PluginUninstallRequest,
    PluginUninstallStatus,
    PluginUninstallTransaction,
)
from library.local_orchestration.project_subscription_runtime import (
    ProjectSubscriptionDecision,
    ProjectSubscriptionFailure,
)
from library.local_orchestration.runtime_dependency_lock import (
    build_approved_runtime_lock,
)
from library.local_orchestration.senior_review_inbox import (
    SeniorReviewInboxCoordinator,
    WindowsSeniorReviewInboxStore,
)
from library.workflow_router.profile import build_plugin_distribution_profile
from library.workflow_router.review_inbox_contracts import (
    ReviewBatchClaimRequest,
    ReviewDependencyNode,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeCapabilityState,
    RoleWakeChainFailure,
    RoleWakeChainStatus,
    RoleWakeStatus,
    preflight_role_wake_chain,
)
from tests.staging.plugin_distribution_vita.harness import (
    build_disposable_target,
    build_uninstall_ports,
    delete_disposable_tree,
    read_git_identity,
    resolve_original_root,
    scripted_install,
    tree_digest,
)
from tests.test_plugin_distribution_bundle import (
    _create_repository,
    _manifest,
    _template_manifest,
)
from tests.test_plugin_distribution_git_subscription import (
    _FakeGitAdapter as SubscriptionGitAdapter,
)
from tests.test_plugin_distribution_git_subscription import (
    _PROJECT_BETA as SUBSCRIPTION_FOREIGN_PROJECT,
)
from tests.test_plugin_distribution_git_subscription import (
    _request as subscription_request,
)
from tests.test_plugin_distribution_git_subscription import (
    _runtime as subscription_runtime,
)
from tests.test_plugin_distribution_router_composition import _PortFixture
from tests.test_role_wake_composition import _preflight_request
from tests.test_senior_review_inbox import _COMMIT_A, _COMMIT_B
from tests.test_senior_review_inbox import _PROJECT as REVIEW_PROJECT
from tests.test_senior_review_inbox import _REVIEWER as REVIEW_REVIEWER
from tests.test_senior_review_inbox import _Resolver as ReviewResolver
from tests.test_senior_review_inbox import _Wake as ReviewHostWake
from tests.test_senior_review_inbox import _event as review_event
from tests.test_senior_review_inbox import _request as review_wake_request

_ORIGINAL = resolve_original_root()
_CANDIDATE_ZIP = "johnny-ai-skill-0.4.2.zip"


@unittest.skipIf(
    _ORIGINAL is None,
    "VITA_ORIGINAL_UNAVAILABLE: no readable original Vita repository on this host",
)
class VitaScriptedQualificationTests(unittest.TestCase):
    """V1-V6 closure cells; the whole pipeline runs once against disposables."""

    identity_before: object
    identity_after: object
    workspace: Path
    workspace_exists_after: bool
    copied_count: int
    target_digest_initial: str
    target_digest_after_install: str
    target_digest_final: str
    bundle_status: PluginBundleBuildStatus
    extracted: tuple[str, ...]
    manifest_paths: frozenset[str]
    johnny_paths_in_target: tuple[str, ...]
    compose_status: JohnnyRouterCompositionStatus
    wake_status: RoleWakeChainStatus
    wake_failure: RoleWakeChainFailure | None
    valid_subscription: ProjectSubscriptionDecision
    invalid_subscription: ProjectSubscriptionDecision
    invalid_subscription_failure: ProjectSubscriptionFailure | None
    wake_flow_statuses: tuple[RoleWakeStatus, ...]
    fifo_clusters: tuple[str, ...]
    uninstall_status: PluginUninstallStatus
    repeat_uninstall_status: PluginUninstallStatus
    residue_entries: tuple[str, ...]

    @classmethod
    def setUpClass(cls) -> None:
        assert _ORIGINAL is not None
        original = _ORIGINAL
        cls.identity_before = read_git_identity(original)
        cls.workspace = Path(tempfile.mkdtemp(prefix="johnny-vita-qual-"))
        try:
            cls._run_pipeline(original)
        finally:
            delete_disposable_tree(cls.workspace)
            cls.workspace_exists_after = cls.workspace.exists()
        cls.identity_after = read_git_identity(original)

    @classmethod
    def _run_pipeline(cls, original: Path) -> None:
        target_copy = cls.workspace / "target"
        cls.copied_count = build_disposable_target(original, target_copy)
        cls.target_digest_initial = tree_digest(target_copy)

        template = _template_manifest()
        fixture_root, source_commit = _create_repository(
            cls.workspace, "candidate", template
        )
        manifest = _manifest(fixture_root, source_commit)
        cls.manifest_paths = frozenset(
            entry.archive_relative_path for entry in manifest.entries
        )
        output_root = cls.workspace / "dist"
        output_root.mkdir()
        build_result = PluginBundleBuilder().build(
            PluginBundleBuildRequest(
                repository_root=fixture_root,
                output_root=output_root,
                manifest=manifest,
            )
        )
        cls.bundle_status = build_result.status

        johnny_root = cls.workspace / "johnny-root"
        johnny_root.mkdir()
        foreign_dir = johnny_root / "foreign-user-dir"
        foreign_dir.mkdir()
        (foreign_dir / "keep.txt").write_text("foreign", encoding="utf-8")
        ledger, extracted = scripted_install(
            output_root / _CANDIDATE_ZIP, johnny_root, manifest
        )
        cls.extracted = extracted
        cls.target_digest_after_install = tree_digest(target_copy)
        cls.johnny_paths_in_target = tuple(
            str(path)
            for path in target_copy.rglob("*")
            if ".johnny" in path.name or "johnny-router" in path.name
        )

        compose = build_johnny_router(
            build_plugin_distribution_profile(),
            build_approved_runtime_lock(),
            _PortFixture().ports(),
        )
        cls.compose_status = compose.status

        unavailable = _preflight_request().model_copy(
            update={
                "wake_capability": _preflight_request().wake_capability.model_copy(
                    update={"state": RoleWakeCapabilityState.UNAVAILABLE}
                )
            }
        )
        wake_result = preflight_role_wake_chain(unavailable)
        cls.wake_status = wake_result.status
        cls.wake_failure = wake_result.failure

        runtime, _ = subscription_runtime(SubscriptionGitAdapter())
        valid = runtime.register(subscription_request())
        cls.valid_subscription = valid.decision
        foreign_runtime, _ = subscription_runtime(SubscriptionGitAdapter())
        invalid = foreign_runtime.register(
            subscription_request(project_id=SUBSCRIPTION_FOREIGN_PROJECT)
        )
        cls.invalid_subscription = invalid.decision
        cls.invalid_subscription_failure = invalid.failure

        store_root = cls.workspace / "review-store"
        store_root.mkdir()
        store = WindowsSeniorReviewInboxStore(store_root.resolve())
        events = {
            ticket: review_event(
                ticket_ref=ticket,
                receipt_ref="receipt-" + ticket[-1],
                task_ref="task-" + ticket[-1],
                handoff_id="handoff-" + ticket[-1],
                commit=commit,
                cluster_id="cluster-" + ticket[-1],
                cluster_revision=revision,
                graph=(ReviewDependencyNode(ticket_ref=ticket, depends_on=()),),
            )
            for ticket, commit, revision in (
                ("ticket-a", _COMMIT_A, "rev-1010101010101010"),
                ("ticket-b", _COMMIT_B, "rev-2020202020202020"),
            )
        }
        inbox = SeniorReviewInboxCoordinator(
            store, ReviewResolver(events), ReviewHostWake()
        )
        first_wake = inbox.wake(
            review_wake_request(
                ticket_ref="ticket-a",
                receipt_ref="receipt-a",
                task_ref="task-a",
                handoff_id="handoff-a",
                commit=_COMMIT_A,
            )
        )
        second_wake = inbox.wake(
            review_wake_request(
                ticket_ref="ticket-b",
                receipt_ref="receipt-b",
                task_ref="task-b",
                handoff_id="handoff-b",
                commit=_COMMIT_B,
            )
        )
        cls.wake_flow_statuses = (first_wake.status, second_wake.status)
        claimed = store.claim_batch(
            ReviewBatchClaimRequest(
                project_id=REVIEW_PROJECT, reviewer_ref=REVIEW_REVIEWER
            )
        )
        cls.fifo_clusters = (
            tuple(item.cluster_id for item in claimed.batch.clusters)
            if claimed.batch is not None
            else ()
        )

        transaction = PluginUninstallTransaction(
            build_uninstall_ports(johnny_root, ledger.receipt_id)
        )
        uninstall_request = PluginUninstallRequest(receipt_id=ledger.receipt_id)
        cls.uninstall_status = transaction.run(uninstall_request).status
        cls.repeat_uninstall_status = transaction.run(uninstall_request).status
        cls.residue_entries = tuple(
            sorted(entry.name for entry in johnny_root.iterdir())
        )
        cls.target_digest_final = tree_digest(target_copy)

    def test_qualification_preserves_original_vita_head_and_status(self) -> None:
        """V2: the original repository identity is untouched by the whole run."""

        self.assertEqual(self.identity_before, self.identity_after)

    def test_candidate_installs_only_into_johnny_root(self) -> None:
        """V1: the deterministic bundle lands only inside the Johnny-owned root."""

        self.assertIs(self.bundle_status, PluginBundleBuildStatus.BUNDLED)
        self.assertGreater(self.copied_count, 0)
        allowed = self.manifest_paths | {"payload-manifest.json"}
        self.assertTrue(set(self.extracted).issubset(allowed))
        self.assertIn("payload-manifest.json", self.extracted)
        self.assertEqual(self.target_digest_initial, self.target_digest_after_install)
        self.assertEqual(self.johnny_paths_in_target, ())

    def test_router_and_role_matrix_accepts_valid_chain(self) -> None:
        """V3: composition, valid subscription and admissions pass exactly."""

        self.assertIs(self.compose_status, JohnnyRouterCompositionStatus.COMPOSED)
        self.assertIs(self.valid_subscription, ProjectSubscriptionDecision.REGISTERED)
        self.assertEqual(
            self.wake_flow_statuses,
            (RoleWakeStatus.HOST_ACCEPTED, RoleWakeStatus.QUEUED_NO_WAKE),
        )

    def test_invalid_bindings_and_missing_host_wake_stay_rejected(self) -> None:
        """V4: foreign bindings reject and missing host wake stays non-binding."""

        self.assertIs(self.invalid_subscription, ProjectSubscriptionDecision.REJECTED)
        self.assertIs(
            self.invalid_subscription_failure,
            ProjectSubscriptionFailure.INVALID_BINDING,
        )
        self.assertIs(self.wake_status, RoleWakeChainStatus.REJECTED)
        self.assertIs(
            self.wake_failure,
            RoleWakeChainFailure.HOST_WAKE_CAPABILITY_UNAVAILABLE,
        )

    def test_fifo_batch_and_cluster_binding_are_deterministic(self) -> None:
        """V5: the claimed batch preserves admission order and cluster identity."""

        self.assertEqual(self.fifo_clusters, ("cluster-a", "cluster-b"))

    def test_uninstall_removes_owned_state_with_zero_residue(self) -> None:
        """V6: uninstall is complete and idempotent; only foreign state remains."""

        self.assertIs(self.uninstall_status, PluginUninstallStatus.REMOVED)
        self.assertIs(
            self.repeat_uninstall_status, PluginUninstallStatus.NOT_INSTALLED
        )
        self.assertEqual(self.residue_entries, ("foreign-user-dir",))
        self.assertEqual(self.target_digest_initial, self.target_digest_final)
        self.assertFalse(self.workspace_exists_after)


if __name__ == "__main__":
    unittest.main()
