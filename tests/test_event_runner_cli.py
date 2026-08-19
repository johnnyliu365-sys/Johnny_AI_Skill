"""E4-E5 closure tests: runner gates, lifecycle honesty and CLI dispatch."""

from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.event_runner import (
    resolve_wake_channel,
    run_event_runner,
    runner_state_path,
    subscriptions_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
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
                    probe_command=(sys.executable, "-c", "pass"),
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


if __name__ == "__main__":
    unittest.main()
