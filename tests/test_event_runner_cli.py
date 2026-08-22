"""E4-E5 closure tests: runner gates, lifecycle honesty and CLI dispatch."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from library.local_orchestration import runner_cli, windows_native_git_ref
from library.local_orchestration.event_runner import (
    RunnerSubscriptionFile,
    resolve_wake_channel,
    run_event_runner,
    runner_state_path,
    subscriptions_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.live_dispatch_metadata_boundary import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
)
from library.local_orchestration.project_runner_registry import (
    RunnerStartCapabilityUnavailable,
)
from library.local_orchestration.runner_cli import run_runner_command
from library.local_orchestration.runner_lifecycle_port import (
    RealRunnerLifecyclePort,
    runner_pid_path,
)
from library.local_orchestration.wake_capability import (
    WakeChannelKind,
    WakeCommandConfig,
    wake_config_path,
)
from library.local_orchestration.wake_scoped_boundary import WakeScopedDispatchBoundary
from library.local_orchestration.work_queue import read_work_queue
from library.workflow_router.supervision_policy import SupervisionClass
from tests.test_role_wake_composition import _receipt
from tests.test_runner_receipt_seeding import _issue_receipt_fixture

_SIMULATED_NATIVE_IMPORT_ERROR = "simulated: pywin32 did not import (ticket 21 test)"

_PROJECT = "prj_0123456789abcdef"


def _layout(temporary: str) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=Path(temporary).resolve())
    layout.base.mkdir(parents=True, exist_ok=True)
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _capture(command: str, arguments: tuple[str, ...], root: Path) -> tuple[int, dict[str, object]]:
    captured = io.StringIO()
    with redirect_stdout(captured):
        code = run_runner_command(command, arguments, root)
    lines = [line for line in captured.getvalue().splitlines() if line.strip()]
    return code, json.loads(lines[-1])


def _declare_wake_command(layout: JohnnyRootLayout) -> None:
    """A real host command that succeeds, so the probe has something to prove."""

    wake_config_path(layout).write_text(
        WakeCommandConfig(
            command=(sys.executable, "-c", "pass", "{payload_file}"),
            reviewer_ref="role-supervisor-reviewer",
        ).model_dump_json(),
        encoding="utf-8",
    )


def _repository(base: Path) -> Path:
    repository = base / "repo"
    repository.mkdir(parents=True)
    subprocess.run(
        ("git", "-C", str(repository), "init", "--quiet"),
        check=True,
        capture_output=True,
    )
    return repository


def _repository_with_baseline_commit(base: Path) -> Path:
    """A repo whose `refs/heads/main` actually resolves.

    `_repository` above is deliberately commit-less: the existing subscribe
    tests only exercise input validation and never reach Git registration.
    The ticket-21 tests below need `exact_git_ref` to resolve so a run is
    blocked by ref-watch capability specifically, not by an unrelated
    `REF_UNAVAILABLE` that would be true regardless of that capability.
    """

    repository = base / "repo-with-commit"
    repository.mkdir(parents=True)

    def _run(*arguments: str) -> None:
        subprocess.run(
            ("git", "-C", str(repository), *arguments),
            check=True,
            capture_output=True,
        )

    _run("init", "--quiet", "-b", "main")
    _run("config", "user.email", "ref-watch-capability@example.invalid")
    _run("config", "user.name", "Ref Watch Capability")
    (repository / "source.txt").write_text("baseline\n", encoding="utf-8")
    _run("add", "source.txt")
    _run("commit", "--quiet", "-m", "baseline")
    return repository


def _receipt_locator_payload() -> dict[str, object]:
    receipt = _receipt()
    return {
        "project_id": receipt.project_id,
        "ticket_reference": receipt.ticket_reference,
        "ticket_revision": receipt.ticket_revision,
    }


def _subscription_inputs_payload(repository: Path) -> dict[str, object]:
    return {
        "repository_root": str(repository),
        "event_source_ref": "event-source-e13-001",
        "subscription_id": "subscription-e13-001",
        "exact_git_ref": "refs/heads/main",
        "reserved_handoff_ref": (
            "doc/handoffs/2026/e13/ticket-e13-001/handoff-e13-001.json"
        ),
        "spec_ref": "spec-e13",
        "spec_revision": "rev-1111111111111111",
        "source_role_ref": "role-implementation-owner",
        "reviewer_ref": "role-supervisor-reviewer",
        "reviewer_task_ref": "task-e13-reviewer",
        "reviewer_task_id": "3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
        "reviewer_host_id": "local",
        "lease_id": "lease-e13-001",
        "supervision_class": "LUNA_XHIGH_DEFAULT",
    }


def _write_inputs_file(path: Path, receipt_locator: object, inputs: object) -> None:
    path.write_text(
        json.dumps({"receipt_locator": receipt_locator, "inputs": inputs}),
        encoding="utf-8",
    )


def _seed_receipt(layout: JohnnyRootLayout) -> None:
    metadata_root = layout.queue_root / "metadata"
    metadata_root.mkdir(parents=True, exist_ok=True)
    _issue_receipt_fixture(
        LiveDispatchMetadataBoundary(JohnnyMetadataRoot(metadata_root.resolve())),
        _receipt(),
    )


class ResolveWakeChannelTests(unittest.TestCase):
    def test_unproven_capability_resolves_to_the_inbox(self) -> None:
        with TemporaryDirectory() as temporary:
            channel = resolve_wake_channel(_layout(temporary))
            self.assertIs(channel.kind, WakeChannelKind.CANDIDATE_INBOX)

    def test_proven_capability_resolves_to_the_command_channel(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            wake_config_path(layout).write_text(
                WakeCommandConfig(
                    command=(sys.executable, "-c", "pass", "{payload_file}"),
                    reviewer_ref="role-supervisor-reviewer",
                ).model_dump_json(),
                encoding="utf-8",
            )
            channel = resolve_wake_channel(layout)
            self.assertIs(channel.kind, WakeChannelKind.HOST_COMMAND)


class RunEventRunnerGateTests(unittest.TestCase):
    def test_absent_subscriptions_block_before_arming(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            self.assertEqual(run_event_runner(layout), 2)
            recorded = json.loads(
                runner_state_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(recorded["code"], "NO_SUBSCRIPTIONS")

    def test_invalid_subscriptions_block_before_arming(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            subscriptions_path(layout).write_text("{broken", encoding="utf-8")
            self.assertEqual(run_event_runner(layout), 2)
            recorded = json.loads(
                runner_state_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(recorded["code"], "SUBSCRIPTIONS_INVALID")

    def test_a_gate_failure_still_names_the_real_ref_watch_capability(self) -> None:
        """Ticket 21 TDD-1: normal behaviour.

        This machine really is Windows with `pywin32` present, so the probe
        used here is unmocked -- the gate write happens before any
        subscription is touched, and the capability fact is additive, so it
        must show up even this early.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            self.assertEqual(run_event_runner(layout), 2)
            recorded = json.loads(
                runner_state_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(recorded["commit_trigger_capability"], "AVAILABLE")
            self.assertIsNone(recorded["commit_trigger_failure"])

    def test_a_gate_failure_names_capability_unavailable_when_forced(self) -> None:
        """Ticket 21 TDD-3: the fail-closed leg, simulated on this machine.

        Forcing the underlying import flag off must not change the gate's
        own behaviour (still `NO_SUBSCRIPTIONS`, still exit code 2) -- only
        add the honest capability fact. That is the "only increases, never
        changes existing field semantics" regression rule from the ticket.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            with mock.patch.object(
                windows_native_git_ref,
                "_NATIVE_IMPORT_ERROR",
                _SIMULATED_NATIVE_IMPORT_ERROR,
            ):
                code = run_event_runner(layout)
            self.assertEqual(code, 2)
            recorded = json.loads(
                runner_state_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(recorded["code"], "NO_SUBSCRIPTIONS")
            self.assertEqual(recorded["commit_trigger_capability"], "UNAVAILABLE")
            self.assertEqual(
                recorded["commit_trigger_failure"], "NATIVE_BINDING_UNAVAILABLE"
            )


class RefWatchCapabilityNeverInferredFromAnEmptyQueueTests(unittest.TestCase):
    """Ticket 21 completion evidence.

    The runner never fakes a trigger, and its state distinguishes "no
    watcher" from "a watcher with nothing to report" -- the defect-class-2
    case named in the ticket. What must differ between the scenarios below
    is the named capability fact, never something inferred from the queue
    being empty, which is equally true either way.
    """

    def _armed_inputs_path(
        self, layout: JohnnyRootLayout, base: Path, repository: Path
    ) -> Path:
        _declare_wake_command(layout)
        _seed_receipt(layout)
        inputs_path = base / "inputs.json"
        _write_inputs_file(
            inputs_path,
            _receipt_locator_payload(),
            _subscription_inputs_payload(repository),
        )
        return inputs_path

    def test_real_and_forced_unavailable_capability_are_told_apart(self) -> None:
        """Both ends land on the same `REGISTRATION_REJECTED`-flavoured

        `SUBSCRIPTION_REJECTED` -- this repository has no commit, so
        `refs/heads/main` never resolves and native registration is never
        even attempted, on either side of the comparison. That is
        deliberate: it isolates the one thing that must differ, the named
        capability fact, from an unrelated reason both sides would fail for
        anyway, and it keeps this test from ever reaching a state where the
        runner could enter its blocking wait.
        """

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            repository = _repository(base)
            inputs_path = self._armed_inputs_path(layout, base, repository)
            subscribe_code, subscribe_payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertEqual(subscribe_code, 0, subscribe_payload)

            with self.subTest(capability="real (this machine has pywin32)"):
                code = run_event_runner(layout)
                self.assertEqual(code, 2)
                recorded = json.loads(
                    runner_state_path(layout).read_text(encoding="utf-8")
                )
                self.assertEqual(recorded["code"], "SUBSCRIPTION_REJECTED")
                self.assertEqual(recorded["commit_trigger_capability"], "AVAILABLE")
                self.assertIsNone(recorded["commit_trigger_failure"])
                queue = read_work_queue(layout)
                self.assertEqual(queue.items, ())

            with self.subTest(capability="forced unavailable"):
                with mock.patch.object(
                    windows_native_git_ref,
                    "_NATIVE_IMPORT_ERROR",
                    _SIMULATED_NATIVE_IMPORT_ERROR,
                ):
                    code = run_event_runner(layout)
                self.assertEqual(code, 2)
                recorded = json.loads(
                    runner_state_path(layout).read_text(encoding="utf-8")
                )
                self.assertEqual(recorded["code"], "SUBSCRIPTION_REJECTED")
                self.assertEqual(recorded["commit_trigger_capability"], "UNAVAILABLE")
                self.assertEqual(
                    recorded["commit_trigger_failure"], "NATIVE_BINDING_UNAVAILABLE"
                )
                queue = read_work_queue(layout)
                self.assertEqual(queue.items, ())

    def test_forced_unavailable_never_lets_a_real_commit_reach_the_queue(self) -> None:
        """Property 4, end to end, with a ref that actually resolves.

        This repository does carry a commit, so it is specifically the
        forced-unavailable capability -- not an unrelated `REF_UNAVAILABLE`
        -- that keeps `run_event_runner` from ever getting past a degraded
        registration to arm any watcher that could have reported it. The
        capability is forced unavailable for the whole call, so this never
        risks reaching a state where the runner could enter its blocking
        wait either.
        """

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            repository = _repository_with_baseline_commit(base)
            inputs_path = self._armed_inputs_path(layout, base, repository)
            _capture("runner", ("subscribe", str(inputs_path)), layout.base)

            with mock.patch.object(
                windows_native_git_ref,
                "_NATIVE_IMPORT_ERROR",
                _SIMULATED_NATIVE_IMPORT_ERROR,
            ):
                code = run_event_runner(layout)

            self.assertEqual(code, 2)
            recorded = json.loads(
                runner_state_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(recorded["status"], "BLOCKED")
            self.assertEqual(recorded["code"], "SUBSCRIPTION_REJECTED")
            self.assertEqual(recorded["commit_trigger_capability"], "UNAVAILABLE")
            queue = read_work_queue(layout)
            self.assertEqual(queue.items, ())


class RealRunnerLifecyclePortTests(unittest.TestCase):
    def test_missing_runtime_cannot_start(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            port = RealRunnerLifecyclePort(layout)
            result = port.start(_PROJECT)
            self.assertIsInstance(result, RunnerStartCapabilityUnavailable)
            self.assertFalse(runner_pid_path(layout).exists())

    def test_existing_pid_blocks_a_second_runner(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            layout.venv_python.parent.mkdir(parents=True)
            layout.venv_python.write_bytes(b"stub")
            layout.plugin_root.mkdir(parents=True)
            runner_pid_path(layout).write_text("4242", encoding="utf-8")
            result = RealRunnerLifecyclePort(layout).start(_PROJECT)
            self.assertIsInstance(result, RunnerStartCapabilityUnavailable)


class RunnerCliTests(unittest.TestCase):
    def test_wake_capability_reports_unavailable_without_claiming(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            code, payload = _capture("wake-capability", (), layout.base)
            self.assertEqual(code, 3)
            self.assertEqual(payload["status"], "UNAVAILABLE")
            self.assertEqual(payload["channel"], "CANDIDATE_INBOX")
            self.assertIs(payload["automatic_wake"], False)

    def test_wake_inbox_lists_recorded_candidates(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            with self.subTest(case="empty"):
                code, payload = _capture("wake-inbox", (), layout.base)
                self.assertEqual(code, 0)
                self.assertEqual(payload["candidate_count"], 0)
            with self.subTest(case="corrupt"):
                (layout.queue_root / "wake-candidates.jsonl").write_text(
                    "not json\n", encoding="utf-8"
                )
                code, payload = _capture("wake-inbox", (), layout.base)
                self.assertEqual(code, 2)
                self.assertEqual(payload["code"], "INBOX_UNREADABLE")

    def test_runner_status_and_start_gates(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            with self.subTest(case="status_not_running"):
                code, payload = _capture("runner", ("status",), layout.base)
                self.assertEqual(code, 3)
                self.assertEqual(payload["status"], "NOT_RUNNING")
            with self.subTest(case="start_without_subscriptions"):
                code, payload = _capture("runner", ("start",), layout.base)
                self.assertEqual(code, 2)
                self.assertEqual(payload["code"], "NO_SUBSCRIPTIONS")
            with self.subTest(case="unknown_subcommand"):
                code, payload = _capture("runner", ("frobnicate",), layout.base)
                self.assertEqual(code, 2)
                self.assertEqual(payload["code"], "UNKNOWN_SUBCOMMAND")


class RunnerSubscribeCliTests(unittest.TestCase):
    """E13: `runner subscribe <inputs.json>` reaches the subscription builder."""

    def test_a_dispatched_receipt_writes_one_typed_line(self) -> None:
        """E13-R1."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            _declare_wake_command(layout)
            repository = _repository(base)
            _seed_receipt(layout)
            inputs_path = base / "inputs.json"
            _write_inputs_file(
                inputs_path,
                _receipt_locator_payload(),
                _subscription_inputs_payload(repository),
            )
            code, payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertEqual(code, 0)
            self.assertEqual(payload, {"status": "WRITTEN"})
            parsed = RunnerSubscriptionFile.model_validate_json(
                subscriptions_path(layout).read_text(encoding="utf-8")
            )
            self.assertEqual(len(parsed.subscriptions), 1)

    def test_an_undispatched_receipt_is_refused_before_any_write(self) -> None:
        """E13-R2."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            _declare_wake_command(layout)
            repository = _repository(base)
            inputs_path = base / "inputs.json"
            _write_inputs_file(
                inputs_path,
                _receipt_locator_payload(),
                _subscription_inputs_payload(repository),
            )
            code, payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["failure"], "RECEIPT_NOT_DISPATCHED")
            self.assertFalse(subscriptions_path(layout).exists())

    def test_a_missing_inputs_file_is_refused_and_names_the_file(self) -> None:
        """E13-R3."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            missing = Path(temporary) / "does-not-exist.json"
            code, payload = _capture(
                "runner", ("subscribe", str(missing)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["section"], "file")
            self.assertFalse(subscriptions_path(layout).exists())

    def test_malformed_json_is_refused_and_names_the_file(self) -> None:
        """E13-R3."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            broken = Path(temporary) / "inputs.json"
            broken.write_text("{not json", encoding="utf-8")
            code, payload = _capture(
                "runner", ("subscribe", str(broken)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["section"], "file")

    def test_an_invalid_receipt_locator_names_that_section(self) -> None:
        """E13-R3."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            repository = _repository(base)
            inputs_path = base / "inputs.json"
            _write_inputs_file(
                inputs_path,
                {},
                _subscription_inputs_payload(repository),
            )
            code, payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["section"], "receipt_locator")
            self.assertFalse(subscriptions_path(layout).exists())

    def test_an_invalid_subscription_inputs_section_names_that_section(self) -> None:
        """E13-R3."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            inputs_path = base / "inputs.json"
            _write_inputs_file(inputs_path, _receipt_locator_payload(), {})
            code, payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["section"], "inputs")
            self.assertFalse(subscriptions_path(layout).exists())

    def test_an_unreadable_inputs_argument_names_the_file(self) -> None:
        """E13-R3: no path argument at all is treated the same as unreadable."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            code, payload = _capture("runner", ("subscribe",), layout.base)
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["section"], "file")

    def test_an_unprovable_wake_capability_is_refused(self) -> None:
        """E13-R4: no wake command is declared in this test layout."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(str(base / "johnny"))
            repository = _repository(base)
            _seed_receipt(layout)
            inputs_path = base / "inputs.json"
            _write_inputs_file(
                inputs_path,
                _receipt_locator_payload(),
                _subscription_inputs_payload(repository),
            )
            code, payload = _capture(
                "runner", ("subscribe", str(inputs_path)), layout.base
            )
            self.assertNotEqual(code, 0)
            self.assertEqual(payload["status"], "REFUSED")
            self.assertEqual(payload["failure"], "WAKE_CAPABILITY_UNAVAILABLE")
            self.assertFalse(subscriptions_path(layout).exists())


class RunnerSubscribeIsolationTests(unittest.TestCase):
    """E13-R5: no issuance-capable object flows through the subscribe path."""

    def test_the_cli_module_holds_no_issuance_capable_name(self) -> None:
        for forbidden in (
            "LiveDispatchMetadataStore",
            "LiveDispatchMetadataBoundary",
            "JohnnyMetadataRoot",
            "IssuanceScopedDispatchBoundary",
            "TicketReceiptIssueRequest",
            "ApprovedDispatchArtifactRegisterRequest",
            "admit_dispatch",
            "create_dispatch_grant",
            "issue_receipt",
            "register_artifact",
        ):
            with self.subTest(name=forbidden):
                self.assertFalse(hasattr(runner_cli, forbidden))

    def test_the_cli_source_never_imports_the_issuance_modules(self) -> None:
        assert runner_cli.__file__ is not None
        source = Path(runner_cli.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "live_dispatch_metadata_store",
            "issuance_scoped_boundary",
            "dispatch_authority",
        ):
            with self.subTest(module=forbidden):
                self.assertNotIn(forbidden, source)

    def test_the_subscribe_path_binds_only_the_wake_scoped_boundary(self) -> None:
        recorded: list[WakeScopedDispatchBoundary] = []

        def _recording_boundary(metadata_root: Path) -> WakeScopedDispatchBoundary:
            instance = WakeScopedDispatchBoundary(metadata_root)
            recorded.append(instance)
            return instance

        original = getattr(runner_cli, "WakeScopedDispatchBoundary")
        setattr(runner_cli, "WakeScopedDispatchBoundary", _recording_boundary)
        try:
            with TemporaryDirectory() as temporary:
                base = Path(temporary)
                layout = _layout(str(base / "johnny"))
                repository = _repository(base)
                inputs_path = base / "inputs.json"
                _write_inputs_file(
                    inputs_path,
                    _receipt_locator_payload(),
                    _subscription_inputs_payload(repository),
                )
                _capture("runner", ("subscribe", str(inputs_path)), layout.base)
        finally:
            setattr(runner_cli, "WakeScopedDispatchBoundary", original)

        self.assertGreaterEqual(len(recorded), 1)
        for bound in recorded:
            self.assertIs(type(bound), original)
            for forbidden in ("issue_receipt", "register_artifact"):
                self.assertFalse(hasattr(bound, forbidden))


if __name__ == "__main__":
    unittest.main()
