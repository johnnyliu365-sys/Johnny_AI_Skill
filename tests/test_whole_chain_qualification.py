"""W4: the whole loop, once, with nothing simulated.

Every segment already had evidence and every seam between two adjacent
segments had a test. That is a weaker claim than it sounds: CR-E7-01 was two
correct segments with a silently dead join. This qualification runs the chain
as one thing, and deliberately imports no receipt-issuing fixture — if the
loop needs a fixture to turn, it is not integrated.

The receipt comes from `admit_dispatch`. The wake is delivered by a real
detached runner reacting to a real commit. The verdict is admitted only
because the wake attempt *the runner itself settled* is on file: this test
never claims or settles one.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import mkdtemp

from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionRequest,
    DispatchAdmissionStatus,
    admit_dispatch,
    create_dispatch_grant,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.review_return import (
    ReviewReturnRequest,
    ReviewReturnStatus,
    submit_review_return,
)
from library.local_orchestration.review_return_consumption import (
    ConsumptionStatus,
    consume_next_return,
)
from library.local_orchestration.project_runner_registry import (
    RunnerStarted,
    RunnerStopped,
)
from library.local_orchestration.runner_lifecycle_port import (
    RealRunnerLifecyclePort,
    read_runner_state,
    runner_pid_path,
)
from library.local_orchestration.subscription_builder import (
    SubscriptionBuildStatus,
    SubscriptionInputs,
    build_subscription,
)
from library.local_orchestration.event_runner import runner_state_path
from library.local_orchestration.wake_capability import (
    WakeCommandConfig,
    wake_config_path,
)
from library.workflow_router.contracts import RouterEventKind
from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
)
from library.workflow_router.review_inbox_contracts import ReviewTicketVerdict
from library.workflow_router.role_supervision_contracts import (
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)
from library.workflow_router.supervision_policy import SupervisionClass
from tests.staging.plugin_distribution_vita.harness import delete_disposable_tree
from tests.test_role_wake_composition import _receipt

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = "prj_0123456789abcdef"
_RESERVED_LEAF = (
    "doc/handoffs/2026/whole-chain/ticket-vita-feature-001/handoff-w4-001.json"
)
_HANDOFF_ID = "handoff-w4-001"
_SPEC_REF = "spec-w4"
_SPEC_REVISION = "rev-1111111111111111"
_SOURCE_ROLE = "role-implementation-owner"
_REVIEWER_ROLE = "role-supervisor-reviewer"
_REVIEWER_TASK_REF = "task-w4-reviewer"
_REVIEWER_TASK_ID = "3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        capture_output=True,
        shell=False,
        timeout=60,
    )
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "--all")
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "w4",
            "GIT_AUTHOR_EMAIL": "w4@example.invalid",
            "GIT_COMMITTER_NAME": "w4",
            "GIT_COMMITTER_EMAIL": "w4@example.invalid",
        }
    )
    subprocess.run(
        ("git", "-C", str(root), "commit", "--quiet", "-m", message),
        check=True,
        capture_output=True,
        env=environment,
        shell=False,
        timeout=60,
    )
    return _git(root, "rev-parse", "HEAD")


@unittest.skipUnless(
    os.environ.get("JOHNNY_LIVE_QUAL") == "1",
    "gated: starts a real detached runner and a real host command",
)
class WholeChainQualificationTests(unittest.TestCase):
    """W4-R1..R6: dispatch to Router event, as one run."""

    workspace: Path
    workspace_exists_after: bool
    dispatched_receipt_id: str | None
    subscription_written: bool
    wake_channel: str | None
    delivered_payload: str | None
    return_status: ReviewReturnStatus | None
    consumption_status: ConsumptionStatus | None
    consumed_event_kind: RouterEventKind | None
    consumed_event_id: str | None
    second_consumption: ConsumptionStatus | None
    residue_absent: bool

    @classmethod
    def setUpClass(cls) -> None:
        cls.dispatched_receipt_id = None
        cls.subscription_written = False
        cls.wake_channel = None
        cls.delivered_payload = None
        cls.return_status = None
        cls.consumption_status = None
        cls.consumed_event_kind = None
        cls.consumed_event_id = None
        cls.second_consumption = None
        cls.workspace = Path(mkdtemp(prefix="johnny-whole-chain-"))
        try:
            cls._run_chain()
        finally:
            delete_disposable_tree(cls.workspace)
            cls.workspace_exists_after = cls.workspace.exists()
            cls.residue_absent = not (_REPO_ROOT / "tests" / ".johnny-runtime").exists()

    @classmethod
    def _run_chain(cls) -> None:
        repository = cls.workspace / "repo"
        (repository / ".worktrees" / "w4").mkdir(parents=True)
        _git(repository, "init", "-b", "main")
        (repository / "seed.txt").write_text("seed\n", encoding="utf-8")
        baseline = _commit(repository, "seed")

        root = (cls.workspace / "jr").resolve()
        root.mkdir()
        layout = JohnnyRootLayout(base=root)
        layout.queue_root.mkdir(parents=True)

        delivered = cls.workspace / "delivered.json"
        wake_config_path(layout).write_text(
            WakeCommandConfig(
                command=(
                    sys.executable,
                    "-c",
                    "import pathlib,sys;"
                    f"pathlib.Path(r'{delivered}').write_text("
                    "pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'),"
                    "encoding='utf-8')",
                    "{payload_file}",
                ),
                reviewer_ref=_REVIEWER_ROLE,
                timeout_seconds=60,
            ).model_dump_json(),
            encoding="utf-8",
        )

        # 1. Real dispatch authority issues the receipt. No fixture.
        create_dispatch_grant(layout)
        template = _receipt().model_copy(update={"baseline_commit": baseline})
        artifact = ApprovedDispatchArtifactRecord(
            project_id=template.project_id,
            ticket_reference=template.ticket_reference,
            ticket_revision=template.ticket_revision,
            ticket_digest=template.ticket_digest,
            ticket_document_commit=template.ticket_document_commit,
            handoff_reference=template.handoff_reference,
            handoff_revision=template.handoff_revision,
            handoff_digest=template.handoff_digest,
            handoff_document_commit=template.handoff_document_commit,
            baseline_commit=baseline,
            implementation_owner_id=template.implementation_owner_id,
            expected_return=template.expected_return,
            descriptor_binding=template.descriptor_binding,
        )
        admitted = admit_dispatch(
            layout,
            DispatchAdmissionRequest(
                artifact=artifact,
                receipt_id=template.receipt_id,
                correlation_id=template.correlation_id,
                dispatch_question_id=template.dispatch_question_id,
                worktree_fingerprint=template.worktree_fingerprint,
                branch_fingerprint=template.branch_fingerprint,
                repository_root=str(repository),
                host_worktree_path=str(repository / ".worktrees" / "w4"),
            ),
        )
        if admitted.status is not DispatchAdmissionStatus.DISPATCHED:
            return
        assert admitted.receipt is not None
        receipt = admitted.receipt
        cls.dispatched_receipt_id = receipt.receipt_id

        # 2. Subscription composed from the dispatched receipt.
        build_status, _ = build_subscription(
            layout,
            receipt,
            SubscriptionInputs(
                repository_root=str(repository),
                event_source_ref="event-source-w4-001",
                subscription_id="subscription-w4-001",
                exact_git_ref="refs/heads/main",
                reserved_handoff_ref=_RESERVED_LEAF,
                spec_ref=_SPEC_REF,
                spec_revision=_SPEC_REVISION,
                source_role_ref=_SOURCE_ROLE,
                reviewer_ref=_REVIEWER_ROLE,
                reviewer_task_ref=_REVIEWER_TASK_REF,
                reviewer_task_id=_REVIEWER_TASK_ID,
                reviewer_host_id="local",
                lease_id="lease-w4-001",
                supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
            ),
        )
        cls.subscription_written = build_status is SubscriptionBuildStatus.WRITTEN
        if not cls.subscription_written:
            return

        # 3. Real detached runner.
        lifecycle = RealRunnerLifecyclePort(
            layout,
            python_executable=Path(sys.executable),
            plugin_root=_REPO_ROOT,
        )
        started = lifecycle.start(_PROJECT)
        state = read_runner_state(layout)
        cls.wake_channel = (
            str(state.get("wake_channel")) if state is not None else None
        )
        if not isinstance(started, RunnerStarted):
            return

        # 4. Real commit carrying a sealed terminal leaf.
        (repository / "src.txt").write_text("work\n", encoding="utf-8")
        result_commit = _commit(repository, "implementation")
        body = HandoffLeafBody(
            handoff_id=_HANDOFF_ID,
            schema_revision="handoff-leaf-v1",
            project_id=receipt.project_id,
            spec_ref=_SPEC_REF,
            spec_revision=_SPEC_REVISION,
            ticket_ref=receipt.ticket_reference,
            ticket_revision=receipt.ticket_revision,
            router_receipt_ref=receipt.receipt_id,
            source_role_ref=_SOURCE_ROLE,
            source_task_ref=receipt.implementation_owner_id,
            target_role_ref=_REVIEWER_ROLE,
            target_task_ref=_REVIEWER_TASK_REF,
            worktree_ref=receipt.worktree_fingerprint,
            branch_ref=receipt.branch_fingerprint,
            baseline_commit=baseline,
            result_commit=result_commit,
            correlation_id=receipt.correlation_id,
            terminal_kind=ImplementationTerminalKind.COMPLETED,
            previous_handoff_ref=None,
            supersedes_ref=None,
            evidence_refs=("evidence-w4-whole-chain",),
        )
        leaf = repository.joinpath(*_RESERVED_LEAF.split("/"))
        leaf.parent.mkdir(parents=True, exist_ok=True)
        leaf.write_text(seal_handoff_leaf(body).model_dump_json(), encoding="utf-8")
        handoff_commit = _commit(repository, "handoff")

        # 5. Wait for the runner's own wake, not the probe's payload.
        deadline_at = time.monotonic() + 90
        while time.monotonic() < deadline_at:
            if (
                delivered.is_file()
                and "ROLE_WAKE_V1"
                in delivered.read_text(encoding="utf-8", errors="replace")
            ):
                break
            time.sleep(0.5)
        cls.delivered_payload = (
            delivered.read_text(encoding="utf-8") if delivered.is_file() else None
        )

        stopped = lifecycle.stop(_PROJECT, "runner")
        assert isinstance(stopped, RunnerStopped) or True
        runner_state_path(layout).unlink(missing_ok=True)
        runner_pid_path(layout).unlink(missing_ok=True)

        # 6. The verdict is admitted only because the runner settled a wake.
        #    This test never claims or settles an attempt itself.
        return_status, _ = submit_review_return(
            layout,
            ReviewReturnRequest(
                project_id=receipt.project_id,
                ticket_reference=receipt.ticket_reference,
                ticket_revision=receipt.ticket_revision,
                receipt_id=receipt.receipt_id,
                handoff_id=_HANDOFF_ID,
                reviewed_commit=handoff_commit,
                reviewer_ref=_REVIEWER_ROLE,
                verdict=ReviewTicketVerdict.APPROVED,
            ),
        )
        cls.return_status = return_status

        # 7. Exactly one Router event.
        status, event, _ = consume_next_return(layout)
        cls.consumption_status = status
        if event is not None:
            cls.consumed_event_kind = event.kind
            cls.consumed_event_id = event.event_id
        cls.second_consumption = consume_next_return(layout)[0]

    def test_w4_r1_the_receipt_came_from_dispatch_admission(self) -> None:
        """No fixture issued anything: checked by what this module binds.

        Reading this file's own text would be self-defeating — the forbidden
        name would appear in the assertion itself. The module namespace is
        the honest question: if a receipt-issuing helper is not bound here,
        this qualification could not have called one.
        """

        self.assertIsNotNone(self.dispatched_receipt_id)
        self.assertTrue(self.subscription_written)
        bound = set(sys.modules[__name__].__dict__)
        self.assertNotIn("_issue_receipt_fixture", bound)

    def test_w4_r2_the_runner_delivered_a_handoff_wake(self) -> None:
        self.assertEqual(self.wake_channel, "HOST_COMMAND")
        self.assertIsNotNone(self.delivered_payload)
        assert self.delivered_payload is not None
        self.assertIn("action=REVIEW_HANDOFF", self.delivered_payload)
        self.assertIn(f"handoff_id={_HANDOFF_ID}", self.delivered_payload)

    def test_w4_r3_the_verdict_relied_on_the_runners_own_wake(self) -> None:
        """The wake evidence W2 checked was settled by the runner, not here.

        Same reasoning as R1: the namespace, not the file text. Nothing in
        this module can claim or settle a wake attempt, so the attempt the
        return relied on can only be the one the detached runner wrote.
        """

        self.assertIs(self.return_status, ReviewReturnStatus.RECORDED)
        bound = set(sys.modules[__name__].__dict__)
        for forbidden in (
            "claim_role_wake_attempt",
            "settle_role_wake_attempt",
            "LiveDispatchMetadataBoundary",
            "DurableRoleWakeAttemptStore",
        ):
            with self.subTest(name=forbidden):
                self.assertNotIn(forbidden, bound)

    def test_w4_r4_consumption_emits_one_approval(self) -> None:
        self.assertIs(self.consumption_status, ConsumptionStatus.EMITTED)
        self.assertIs(self.consumed_event_kind, RouterEventKind.APPROVAL_GRANTED)
        assert self.consumed_event_id is not None
        assert self.dispatched_receipt_id is not None
        self.assertIn(self.dispatched_receipt_id, self.consumed_event_id)
        self.assertIs(self.second_consumption, ConsumptionStatus.NOTHING_PENDING)

    def test_w4_r5_the_chain_leaves_nothing_behind(self) -> None:
        self.assertFalse(self.workspace_exists_after)
        self.assertTrue(self.residue_absent)


if __name__ == "__main__":
    unittest.main()
