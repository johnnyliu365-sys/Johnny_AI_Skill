"""E6 end-to-end event-runner qualification.

Gated by `JOHNNY_LIVE_QUAL=1`: it creates a real Git repository, spawns the
real detached runner process, commits a real handoff leaf to the exact watched
ref, and proves the wake actually reached the declared host command — then
stops the runner and proves zero residue.
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

from library.local_orchestration.event_runner import (
    RunnerSubscriptionFile,
    RunnerSubscriptionSpec,
    runner_state_path,
    subscriptions_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
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
from library.local_orchestration.wake_capability import (
    WakeCommandConfig,
    wake_config_path,
)
from library.workflow_router.role_supervision_contracts import (
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)
from library.workflow_router.supervision_policy import SupervisionClass
from library.workflow_router.supervision_runtime_contracts import (
    SupervisionPreparationRequest,
    SupervisionStartRequest,
)
from tests.staging.plugin_distribution_vita.harness import delete_disposable_tree
from tests.test_git_handoff_event_adapter import _admission, _registration_request
from tests.test_receipt_bound_supervision import _started
from tests.test_role_wake_composition import (
    _deadline_capability,
    _receipt,
    _wake_capability,
)
from tests.test_runner_receipt_seeding import _issue_receipt_fixture

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PROJECT = "prj_0123456789abcdef"
# The exact reserved leaf the registration fixture watches: a commit anywhere
# else is an ordinary source commit and must stay silent by design.
_RESERVED_LEAF = (
    "doc/handoffs/2026/vita-feature/ticket-vita-feature-001/"
    "handoff-vita-feature-001.json"
)


def _sealed_leaf(baseline: str, result_commit: str) -> str:
    """One real sealed terminal handoff matching the admission context."""

    body = HandoffLeafBody(
        handoff_id="handoff-vita-feature-001",
        schema_revision="handoff-leaf-v1",
        project_id=_PROJECT,
        spec_ref="spec-vita-feature",
        spec_revision="rev-1111111111111111",
        ticket_ref="ticket-vita-feature-001",
        ticket_revision="rev-2222222222222222",
        router_receipt_ref="receipt-vita-feature-001",
        source_role_ref="role-implementation-owner",
        source_task_ref="task-vita-implementation",
        target_role_ref="role-supervisor-reviewer",
        target_task_ref="task-vita-reviewer",
        worktree_ref="worktree-vitafeature-01",
        branch_ref="branch-vitafeature-01",
        baseline_commit=baseline,
        result_commit=result_commit,
        correlation_id="correlation-vita-feature-001",
        terminal_kind=ImplementationTerminalKind.COMPLETED,
        previous_handoff_ref=None,
        supersedes_ref=None,
        evidence_refs=("evidence-e6-runner-001",),
    )
    return seal_handoff_leaf(body).model_dump_json()


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        capture_output=True,
        shell=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout.decode("utf-8", errors="replace").strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "--all")
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "e6-runner",
            "GIT_AUTHOR_EMAIL": "e6@example.invalid",
            "GIT_COMMITTER_NAME": "e6-runner",
            "GIT_COMMITTER_EMAIL": "e6@example.invalid",
        }
    )
    completed = subprocess.run(
        ("git", "-C", str(root), "commit", "-m", message),
        capture_output=True,
        shell=False,
        timeout=60,
        env=environment,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", errors="replace"))
    return _git(root, "rev-parse", "HEAD")


@unittest.skipUnless(
    os.environ.get("JOHNNY_LIVE_QUAL") == "1",
    "JOHNNY_LIVE_QUAL not set: real process spawning is gated",
)
class EventRunnerQualificationTests(unittest.TestCase):
    """R1-R5: a real runner, a real ref event and an honest wake channel."""

    workspace: Path
    workspace_exists_after: bool
    start_result_ok: bool
    running_state: dict[str, object] | None
    wake_channel: str | None
    delivered_payload: str | None
    stop_result_ok: bool
    stopped_state: dict[str, object] | None
    pid_file_absent: bool
    runner_process_absent: bool
    runner_pid: int | None

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Path(mkdtemp(prefix="johnny-runner-qual-"))
        try:
            cls._run_pipeline()
        finally:
            delete_disposable_tree(cls.workspace)
            cls.workspace_exists_after = cls.workspace.exists()

    @classmethod
    def _run_pipeline(cls) -> None:
        repository = cls.workspace / "repo"
        repository.mkdir()
        _git(repository, "init", "-b", "main")
        _git(repository, "config", "user.name", "e6-runner")
        _git(repository, "config", "user.email", "e6@example.invalid")
        (repository / "seed.txt").write_text("seed\n", encoding="utf-8")
        baseline = _commit(repository, "seed")

        root = (cls.workspace / "jr").resolve()
        root.mkdir()
        layout = JohnnyRootLayout(base=root)
        layout.queue_root.mkdir(parents=True)

        # A declared, probeable wake command that records what it received:
        # this is the honest proof that the wake truly left the runner.
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
                reviewer_ref="role-supervisor-reviewer",
                timeout_seconds=60,
            ).model_dump_json(),
            encoding="utf-8",
        )

        receipt = _receipt().model_copy(update={"baseline_commit": baseline})
        # The qualification stands in for the authorized dispatcher: it issues
        # the receipt through the control-plane store fixture, exactly as the
        # 05B-series tests do, before the runner — which only ever verifies —
        # is started. No issuing capability exists in the runtime payload.
        metadata_root = layout.queue_root / "metadata"
        metadata_root.mkdir(parents=True, exist_ok=True)
        _issue_receipt_fixture(
            LiveDispatchMetadataBoundary(JohnnyMetadataRoot(metadata_root.resolve())),
            receipt,
        )
        specification = RunnerSubscriptionSpec(
            repository_root=str(repository),
            preparation=SupervisionPreparationRequest(
                receipt=receipt,
                registration_request=_registration_request(baseline),
                handoff_context=_admission(
                    baseline=baseline, observed_handoff_commit=baseline
                ),
                reviewer_ref="role-supervisor-reviewer",
                implementation_task_ref="task-vita-implementation",
                wake_capability=_wake_capability(receipt),
                deadline_capability=_deadline_capability(receipt),
            ),
            start=SupervisionStartRequest(
                subscription_id=_registration_request(baseline).subscription_id,
                lease_id="lease-e6-runner-001",
                supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
                execution_started=_started(baseline),
            ),
        )
        subscriptions_path(layout).write_text(
            RunnerSubscriptionFile(subscriptions=(specification,)).model_dump_json(),
            encoding="utf-8",
        )

        lifecycle = RealRunnerLifecyclePort(
            layout,
            python_executable=Path(sys.executable),
            plugin_root=_REPO_ROOT,
        )
        start_result = lifecycle.start(_PROJECT)
        cls.start_result_ok = isinstance(start_result, RunnerStarted)
        cls.running_state = read_runner_state(layout)
        cls.wake_channel = (
            str(cls.running_state.get("wake_channel"))
            if cls.running_state is not None
            else None
        )
        pid_text = (
            runner_pid_path(layout).read_text(encoding="utf-8")
            if runner_pid_path(layout).is_file()
            else ""
        )
        cls.runner_pid = int(pid_text) if pid_text.strip().isdigit() else None

        # R3: a real commit to the exact watched ref, carrying the reserved leaf.
        if cls.start_result_ok:
            (repository / "src.txt").write_text("work\n", encoding="utf-8")
            result_commit = _commit(repository, "implementation")
            leaf = repository.joinpath(*_RESERVED_LEAF.split("/"))
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_text(
                _sealed_leaf(baseline, result_commit), encoding="utf-8"
            )
            _commit(repository, "handoff")
            deadline_at = time.monotonic() + 60
            while time.monotonic() < deadline_at and not delivered.is_file():
                time.sleep(0.5)
        cls.delivered_payload = (
            delivered.read_text(encoding="utf-8") if delivered.is_file() else None
        )

        stop_result = lifecycle.stop(_PROJECT, "runner")
        cls.stop_result_ok = isinstance(stop_result, RunnerStopped)
        cls.stopped_state = read_runner_state(layout)
        cls.pid_file_absent = not runner_pid_path(layout).exists()
        cls.runner_process_absent = cls._process_absent(cls.runner_pid)
        # The runner state file is Johnny-owned bookkeeping, not a residue.
        runner_state_path(layout).unlink(missing_ok=True)

    @staticmethod
    def _process_absent(pid: int | None) -> bool:
        if pid is None:
            return True
        deadline_at = time.monotonic() + 30
        while time.monotonic() < deadline_at:
            completed = subprocess.run(
                ("tasklist", "/FI", f"PID eq {pid}", "/NH"),
                capture_output=True,
                shell=False,
                timeout=30,
            )
            listing = completed.stdout.decode("utf-8", errors="replace")
            if str(pid) not in listing:
                return True
            time.sleep(0.5)
        return False

    def test_r1_runner_starts_detached_and_records_its_channel(self) -> None:
        self.assertTrue(self.start_result_ok)
        self.assertIsNotNone(self.running_state)
        assert self.running_state is not None
        self.assertEqual(self.running_state.get("status"), "RUNNING")
        self.assertIsNotNone(self.runner_pid)

    def test_r2_proven_capability_resolves_the_command_channel(self) -> None:
        self.assertEqual(self.wake_channel, "HOST_COMMAND")

    def test_r3_exact_ref_commit_delivers_a_real_wake(self) -> None:
        """CR-E7-01: this must be the commit's wake, not the deadline's.

        The previous assertion was `"handoff" in payload`, which a
        `SUPERVISION_DEADLINE` payload also satisfies: it carries the field
        `handoff_id=-`. Combined with the fixture's `started_at_ms=1_000`,
        which puts the deadline permanently in the past, the cell passed on a
        deadline wake that would have fired with no commit at all. The
        assertion now names the action, so R3 proves what its title claims.
        """

        self.assertIsNotNone(self.delivered_payload)
        assert self.delivered_payload is not None
        action = next(
            (
                line.split("=", 1)[1]
                for line in self.delivered_payload.splitlines()
                if line.startswith("action=")
            ),
            "",
        )
        self.assertNotEqual(
            action,
            "SUPERVISION_DEADLINE",
            "the observed wake is the deadline, not the committed handoff",
        )
        self.assertIn("handoff", self.delivered_payload)

    def test_r4_stop_is_acknowledged_and_the_process_exits(self) -> None:
        self.assertTrue(self.stop_result_ok)
        self.assertIsNotNone(self.stopped_state)
        assert self.stopped_state is not None
        self.assertEqual(self.stopped_state.get("status"), "STOPPED")
        self.assertTrue(self.pid_file_absent)
        self.assertTrue(self.runner_process_absent)

    def test_r5_workspace_is_fully_removable(self) -> None:
        self.assertFalse(self.workspace_exists_after)


if __name__ == "__main__":
    unittest.main()
