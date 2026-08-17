"""Exact-ref registration, Git readback, race, and deduplication tests."""

from __future__ import annotations

from collections import deque
import ast
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from library.local_orchestration.git_handoff_event_adapter import (
    GitCliReadbackPort,
    NativeGitRefNotificationPort,
    ReceiptBoundGitEventAdapter,
)
from library.workflow_router.git_handoff_contracts import (
    GitAncestryResult,
    GitAncestryStatus,
    GitBlobReadResult,
    GitBlobReadStatus,
    GitEventAdapterDecisionKind,
    GitNativeRegistrationRequest,
    GitNativeRegistrationResult,
    GitNativeRegistrationStatus,
    GitPathChangeResult,
    GitPathChangeStatus,
    GitRefRegistrationRequest,
    GitRefSignal,
    GitRefSnapshotResult,
    GitRefSnapshotStatus,
)
from library.workflow_router.role_supervision_contracts import (
    HandoffAdmissionContext,
    HandoffLeaf,
    HandoffLeafBody,
    ImplementationTerminalKind,
    seal_handoff_leaf,
)


def _run_git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return completed.stdout.strip()


def _commit(root: Path, message: str) -> str:
    _run_git(root, "add", "--all")
    _run_git(root, "commit", "-m", message)
    return _run_git(root, "rev-parse", "HEAD")


def _admission(
    *,
    baseline: str,
    observed_handoff_commit: str,
    consumed_handoff_ids: tuple[str, ...] = (),
) -> HandoffAdmissionContext:
    return HandoffAdmissionContext(
        project_id="prj_0123456789abcdef",
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
        correlation_id="correlation-vita-feature-001",
        observed_handoff_commit=observed_handoff_commit,
        result_descends_from_baseline=True,
        handoff_descends_from_result=True,
        reserved_path_changed=True,
        consumed_handoff_ids=consumed_handoff_ids,
    )


def _registration_request(baseline: str) -> GitRefRegistrationRequest:
    return GitRefRegistrationRequest(
        event_source_ref="event-source-vita-feature-001",
        subscription_id="subscription-vita-feature-001",
        project_id="prj_0123456789abcdef",
        ticket_ref="ticket-vita-feature-001",
        router_receipt_ref="receipt-vita-feature-001",
        implementation_task_ref="task-vita-implementation",
        worktree_ref="worktree-vitafeature-01",
        branch_ref="branch-vitafeature-01",
        baseline_commit=baseline,
        correlation_id="correlation-vita-feature-001",
        exact_git_ref="refs/heads/main",
        reserved_handoff_ref=(
            "doc/handoffs/2026/vita-feature/ticket-vita-feature-001/"
            "handoff-vita-feature-001.json"
        ),
    )


class _RecordedNativePort(NativeGitRefNotificationPort):
    def __init__(self) -> None:
        self.requests: list[GitNativeRegistrationRequest] = []
        self.cancelled: list[str] = []

    def register(self, request: GitNativeRegistrationRequest) -> GitNativeRegistrationResult:
        self.requests.append(request)
        return GitNativeRegistrationResult(
            status=GitNativeRegistrationStatus.REGISTERED,
            event_source_ref=request.event_source_ref,
            subscription_id=request.subscription_id,
        )

    def cancel(self, subscription_id: str) -> bool:
        self.cancelled.append(subscription_id)
        return True


class _SequencedReadback:
    def __init__(self, snapshots: tuple[str, ...]) -> None:
        self._snapshots = deque(snapshots)
        self.snapshot_calls = 0

    def read_ref(self, exact_git_ref: str) -> GitRefSnapshotResult:
        self.snapshot_calls += 1
        return GitRefSnapshotResult(
            status=GitRefSnapshotStatus.FOUND,
            exact_git_ref=exact_git_ref,
            commit_id=self._snapshots.popleft(),
        )

    def path_changed(self, prior_commit: str, observed_commit: str, exact_path: str) -> GitPathChangeResult:
        return GitPathChangeResult(status=GitPathChangeStatus.UNCHANGED, changed=False)

    def read_blob(self, commit_id: str, exact_path: str) -> GitBlobReadResult:
        return GitBlobReadResult(status=GitBlobReadStatus.NOT_FOUND)

    def is_ancestor(self, ancestor: str, descendant: str) -> GitAncestryResult:
        return GitAncestryResult(status=GitAncestryStatus.IS_ANCESTOR, is_ancestor=True)


class GitRegistrationRaceTests(unittest.TestCase):
    def test_pre_and_post_registration_snapshots_close_the_completion_race(self) -> None:
        before = "1" * 40
        after = "2" * 40
        native = _RecordedNativePort()
        readback = _SequencedReadback((before, after))
        adapter = ReceiptBoundGitEventAdapter(readback, native)

        registered = adapter.register(_registration_request(before), _admission(
            baseline=before,
            observed_handoff_commit=after,
        ))

        self.assertEqual(2, readback.snapshot_calls)
        self.assertEqual(1, len(native.requests))
        self.assertEqual(GitEventAdapterDecisionKind.SOURCE_ADVANCED, registered.decision)
        self.assertIsNotNone(registered.registration)
        self.assertEqual(after, registered.registration.last_observed_commit if registered.registration else None)

    def test_duplicate_native_signal_and_unchanged_sha_are_silent(self) -> None:
        commit = "1" * 40
        native = _RecordedNativePort()
        readback = _SequencedReadback((commit, commit, commit, commit))
        adapter = ReceiptBoundGitEventAdapter(readback, native)
        registered = adapter.register(
            _registration_request(commit),
            _admission(baseline=commit, observed_handoff_commit=commit),
        )
        state = registered.registration
        if state is None:
            self.fail("registration did not produce state")
        signal = GitRefSignal(
            event_source_ref=state.event_source_ref,
            subscription_id=state.subscription_id,
        )
        first = adapter.observe_signal(state, signal, _admission(
            baseline=commit,
            observed_handoff_commit=commit,
        ))
        second = adapter.observe_signal(first.registration or state, signal, _admission(
            baseline=commit,
            observed_handoff_commit=commit,
        ))
        self.assertEqual(GitEventAdapterDecisionKind.SILENT, first.decision)
        self.assertEqual(GitEventAdapterDecisionKind.SILENT, second.decision)


class RealGitHandoffReadbackTests(unittest.TestCase):
    def test_source_commit_is_silent_but_committed_valid_handoff_is_accepted_once(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "router-test@example.invalid")
            _run_git(root, "config", "user.name", "Router Test")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")

            native = _RecordedNativePort()
            readback = GitCliReadbackPort(root)
            adapter = ReceiptBoundGitEventAdapter(readback, native)
            request = _registration_request(baseline)
            initial = adapter.register(
                request,
                _admission(baseline=baseline, observed_handoff_commit=baseline),
            )
            state = initial.registration
            if state is None:
                self.fail("registration did not produce state")

            (root / "source.txt").write_text("baseline\nimplementation\n", encoding="utf-8")
            result_commit = _commit(root, "implementation")
            source_signal = adapter.observe_signal(
                state,
                GitRefSignal(
                    event_source_ref=state.event_source_ref,
                    subscription_id=state.subscription_id,
                ),
                _admission(baseline=baseline, observed_handoff_commit=result_commit),
            )
            self.assertEqual(GitEventAdapterDecisionKind.SOURCE_ADVANCED, source_signal.decision)
            state = source_signal.registration or state

            leaf = seal_handoff_leaf(
                HandoffLeafBody(
                    handoff_id="handoff-vita-feature-001",
                    schema_revision="handoff-schema-v1",
                    project_id="prj_0123456789abcdef",
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
                    terminal_kind=ImplementationTerminalKind.COMPLETED,
                    previous_handoff_ref=None,
                    supersedes_ref=None,
                    evidence_refs=("evidence-tests-green",),
                    correlation_id="correlation-vita-feature-001",
                )
            )
            leaf_path = root / request.reserved_handoff_ref
            leaf_path.parent.mkdir(parents=True)
            leaf_path.write_text(leaf.model_dump_json(indent=2), encoding="utf-8")
            handoff_commit = _commit(root, "terminal handoff")
            accepted = adapter.observe_signal(
                state,
                GitRefSignal(
                    event_source_ref=state.event_source_ref,
                    subscription_id=state.subscription_id,
                ),
                _admission(baseline=baseline, observed_handoff_commit=handoff_commit),
            )
            self.assertEqual(GitEventAdapterDecisionKind.TERMINAL_HANDOFF_ACCEPTED, accepted.decision)
            self.assertEqual(leaf, accepted.handoff)
            state = accepted.registration or state

            replay = adapter.observe_signal(
                state,
                GitRefSignal(
                    event_source_ref=state.event_source_ref,
                    subscription_id=state.subscription_id,
                ),
                _admission(baseline=baseline, observed_handoff_commit=handoff_commit),
            )
            self.assertEqual(GitEventAdapterDecisionKind.SILENT, replay.decision)

            restarted = ReceiptBoundGitEventAdapter(readback, _RecordedNativePort()).register(
                request,
                _admission(
                    baseline=baseline,
                    observed_handoff_commit=handoff_commit,
                    consumed_handoff_ids=(leaf.handoff_id,),
                ),
            )
            self.assertEqual(GitEventAdapterDecisionKind.SILENT, restarted.decision)

    def test_invalid_reserved_handoff_emits_one_sanitized_fault_then_halts(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "router-test@example.invalid")
            _run_git(root, "config", "user.name", "Router Test")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            baseline = _commit(root, "baseline")
            native = _RecordedNativePort()
            adapter = ReceiptBoundGitEventAdapter(GitCliReadbackPort(root), native)
            request = _registration_request(baseline)
            initial = adapter.register(
                request,
                _admission(baseline=baseline, observed_handoff_commit=baseline),
            )
            state = initial.registration
            if state is None:
                self.fail("registration did not produce state")

            leaf_path = root / request.reserved_handoff_ref
            leaf_path.parent.mkdir(parents=True)
            leaf_path.write_text('{"prompt":"malicious"}', encoding="utf-8")
            invalid_commit = _commit(root, "invalid claimed handoff")
            signal = GitRefSignal(
                event_source_ref=state.event_source_ref,
                subscription_id=state.subscription_id,
            )
            fault = adapter.observe_signal(
                state,
                signal,
                _admission(baseline=baseline, observed_handoff_commit=invalid_commit),
            )
            self.assertEqual(GitEventAdapterDecisionKind.INVALID_HANDOFF_FAULT, fault.decision)
            self.assertIsNotNone(fault.fault)
            self.assertNotIn("malicious", fault.model_dump_json())
            halted = fault.registration
            if halted is None:
                self.fail("fault did not retain halted state")
            replay = adapter.observe_signal(
                halted,
                signal,
                _admission(baseline=baseline, observed_handoff_commit=invalid_commit),
            )
            self.assertEqual(GitEventAdapterDecisionKind.SILENT, replay.decision)
            self.assertEqual(1, len(native.cancelled))

    def test_cli_readback_supports_packed_refs_without_repository_scan(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            _run_git(root, "init", "-b", "main")
            _run_git(root, "config", "user.email", "router-test@example.invalid")
            _run_git(root, "config", "user.name", "Router Test")
            (root / "source.txt").write_text("baseline\n", encoding="utf-8")
            commit = _commit(root, "baseline")
            _run_git(root, "pack-refs", "--all")
            result = GitCliReadbackPort(root).read_ref("refs/heads/main")
            self.assertEqual(GitRefSnapshotStatus.FOUND, result.status)
            self.assertEqual(commit, result.commit_id)


class GitAdapterSourceGateTests(unittest.TestCase):
    def test_adapter_has_no_polling_sleep_or_repository_scan_command(self) -> None:
        source_path = (
            Path(__file__).resolve().parents[1]
            / "library"
            / "local_orchestration"
            / "git_handoff_event_adapter.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertNotIn("sleep(", source)
        self.assertNotIn("while True", source)
        self.assertNotIn("heartbeat", source.casefold())
        for forbidden_command in (
            "ls-files",
            "for-each-ref",
            "status --",
            "rev-list --all",
        ):
            self.assertNotIn(forbidden_command, source)
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertTrue(imported_roots.isdisjoint({"threading", "time", "watchdog"}))


if __name__ == "__main__":
    unittest.main()
