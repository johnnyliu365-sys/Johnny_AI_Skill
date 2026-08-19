"""E1-E3 closure tests: capability probe, command wake port, candidate inbox."""

from __future__ import annotations

import sys
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.local_orchestration.command_role_wake_port import CommandRoleWakePort
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.wake_candidate_inbox import (
    WakeCandidateInboxPort,
    candidate_inbox_path,
    read_candidates,
)
from library.local_orchestration.wake_capability import (
    WakeCapabilityFailure,
    WakeCapabilityStatus,
    WakeChannelKind,
    WakeCommandConfig,
    probe_wake_capability,
    wake_config_path,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeCommand,
    RoleWakeEffectStatus,
)

_PAYLOAD = '{"handoff":"handoff-e1-001"}'
_ATTEMPT = "wake-attempt-e1-0001"
_TASK = "01a00eac-b464-7ee1-ac76-465477768e02"


def _command(attempt_id: str = _ATTEMPT) -> RoleWakeCommand:
    return RoleWakeCommand(
        attempt_id=attempt_id,
        reviewer_task_id=_TASK,
        reviewer_thread_id=_TASK,
        host_id="host-johnny-local",
        payload=_PAYLOAD,
        payload_digest="sha256_" + sha256(_PAYLOAD.encode("utf-8")).hexdigest(),
    )


def _config(
    command: tuple[str, ...] | None = None,
    probe_command: tuple[str, ...] | None = None,
    timeout_seconds: int = 60,
) -> WakeCommandConfig:
    return WakeCommandConfig(
        command=command
        if command is not None
        else (sys.executable, "-c", "import sys; sys.exit(0)", "{payload_file}"),
        probe_command=probe_command
        if probe_command is not None
        else (sys.executable, "-c", "import sys; sys.exit(0)"),
        reviewer_ref="role-supervisor-reviewer",
        timeout_seconds=timeout_seconds,
    )


class WakeCommandConfigTests(unittest.TestCase):
    def test_exactly_one_payload_placeholder_is_required(self) -> None:
        with self.subTest(case="none"):
            with self.assertRaises(ValidationError):
                _config(command=(sys.executable, "-c", "pass"))
        with self.subTest(case="two"):
            with self.assertRaises(ValidationError):
                _config(
                    command=(sys.executable, "{payload_file}", "{payload_file}")
                )
        with self.subTest(case="probe_may_not_reference_payload"):
            with self.assertRaises(ValidationError):
                _config(probe_command=(sys.executable, "{payload_file}"))

    def test_rendering_substitutes_only_declared_placeholders(self) -> None:
        config = _config(
            command=(sys.executable, "--to", "{payload_file}", "--id", "{attempt_id}")
        )
        rendered = config.rendered(Path("C:/jr/queue/p.json"), _ATTEMPT)
        self.assertEqual(
            rendered,
            (sys.executable, "--to", "C:\\jr\\queue\\p.json", "--id", _ATTEMPT),
        )


class ProbeWakeCapabilityTests(unittest.TestCase):
    def _layout(self, temporary: str) -> JohnnyRootLayout:
        layout = JohnnyRootLayout(base=Path(temporary).resolve())
        layout.base.mkdir(parents=True, exist_ok=True)
        return layout

    def test_absent_config_degrades_to_the_inbox_channel(self) -> None:
        with TemporaryDirectory() as temporary:
            result = probe_wake_capability(self._layout(temporary))
            self.assertIs(result.status, WakeCapabilityStatus.UNAVAILABLE)
            self.assertIs(result.channel, WakeChannelKind.CANDIDATE_INBOX)
            self.assertIs(result.failure, WakeCapabilityFailure.NOT_CONFIGURED)
            self.assertIsNone(result.config)

    def test_declared_and_passing_probe_is_proven(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = self._layout(temporary)
            wake_config_path(layout).write_text(
                _config().model_dump_json(), encoding="utf-8"
            )
            result = probe_wake_capability(layout)
            self.assertIs(result.status, WakeCapabilityStatus.PROVEN)
            self.assertIs(result.channel, WakeChannelKind.HOST_COMMAND)
            self.assertIsNotNone(result.config)

    def test_each_broken_declaration_stays_unavailable(self) -> None:
        cases: tuple[tuple[str, str, WakeCapabilityFailure], ...] = (
            ("malformed_json", "{not json", WakeCapabilityFailure.CONFIG_INVALID),
            (
                "missing_placeholder",
                '{"schema_version":1,"command":["x"],"probe_command":["y"],'
                '"reviewer_ref":"role-supervisor-reviewer","timeout_seconds":60}',
                WakeCapabilityFailure.CONFIG_INVALID,
            ),
            (
                "missing_executable",
                _config(
                    probe_command=("johnny-nonexistent-probe-binary",)
                ).model_dump_json(),
                WakeCapabilityFailure.EXECUTABLE_UNAVAILABLE,
            ),
            (
                "failing_probe",
                _config(
                    probe_command=(sys.executable, "-c", "import sys; sys.exit(7)")
                ).model_dump_json(),
                WakeCapabilityFailure.PROBE_FAILED,
            ),
        )
        for label, content, failure in cases:
            with self.subTest(case=label):
                with TemporaryDirectory() as temporary:
                    layout = self._layout(temporary)
                    wake_config_path(layout).write_text(content, encoding="utf-8")
                    result = probe_wake_capability(layout)
                    self.assertIs(result.status, WakeCapabilityStatus.UNAVAILABLE)
                    self.assertIs(result.failure, failure)
                    self.assertIsNone(result.config)

    def test_hanging_probe_times_out_without_claiming(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = self._layout(temporary)
            wake_config_path(layout).write_text(
                _config(
                    probe_command=(sys.executable, "-c", "import time; time.sleep(30)")
                ).model_dump_json(),
                encoding="utf-8",
            )
            result = probe_wake_capability(layout, timeout_seconds=2)
            self.assertIs(result.status, WakeCapabilityStatus.UNAVAILABLE)
            self.assertIs(result.failure, WakeCapabilityFailure.PROBE_TIMEOUT)


class CommandRoleWakePortTests(unittest.TestCase):
    def test_successful_command_accepts_with_a_delivery_reference(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            marker = layout.base / "delivered.txt"
            config = _config(
                command=(
                    sys.executable,
                    "-c",
                    "import pathlib,sys; "
                    f"pathlib.Path(r'{marker}').write_text("
                    "pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'), "
                    "encoding='utf-8')",
                    "{payload_file}",
                )
            )
            port = CommandRoleWakePort(layout, config)

            result = port.wake(_command())

            self.assertIs(result.status, RoleWakeEffectStatus.HOST_ACCEPTED)
            self.assertIsNotNone(result.delivery_reference)
            self.assertEqual(marker.read_text(encoding="utf-8"), _PAYLOAD)

    def test_failing_and_missing_commands_have_no_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            with self.subTest(case="nonzero_exit"):
                port = CommandRoleWakePort(
                    layout,
                    _config(
                        command=(
                            sys.executable,
                            "-c",
                            "import sys; sys.exit(4)",
                            "{payload_file}",
                        )
                    ),
                )
                result = port.wake(_command())
                self.assertIs(result.status, RoleWakeEffectStatus.NO_EFFECT)
                self.assertIsNone(result.delivery_reference)
            with self.subTest(case="missing_executable"):
                port = CommandRoleWakePort(
                    layout,
                    _config(command=("johnny-nonexistent-wake", "{payload_file}")),
                )
                result = port.wake(_command())
                self.assertIs(result.status, RoleWakeEffectStatus.NO_EFFECT)

    def test_timeout_after_start_is_terminally_uncertain(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = CommandRoleWakePort(
                layout,
                _config(
                    command=(
                        sys.executable,
                        "-c",
                        "import time; time.sleep(30)",
                        "{payload_file}",
                    ),
                    timeout_seconds=5,
                ),
            )
            result = port.wake(_command())
            self.assertIs(result.status, RoleWakeEffectStatus.EFFECT_UNCERTAIN)
            self.assertIsNone(result.delivery_reference)


class WakeCandidateInboxPortTests(unittest.TestCase):
    def test_recording_a_candidate_never_claims_a_wake(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = WakeCandidateInboxPort(layout)

            result = port.wake(_command())

            self.assertIs(result.status, RoleWakeEffectStatus.NO_EFFECT)
            self.assertIsNone(result.delivery_reference)
            records = read_candidates(layout)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].attempt_id, _ATTEMPT)
            self.assertEqual(
                Path(records[0].payload_path).read_text(encoding="utf-8"), _PAYLOAD
            )

    def test_repeat_attempts_are_deduplicated(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            port = WakeCandidateInboxPort(layout)
            port.wake(_command())
            port.wake(_command())
            port.wake(_command("wake-attempt-e1-0002"))
            records = read_candidates(layout)
            self.assertEqual(
                tuple(record.attempt_id for record in records),
                (_ATTEMPT, "wake-attempt-e1-0002"),
            )

    def test_corrupt_inbox_fails_closed_without_appending(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            inbox = candidate_inbox_path(layout)
            inbox.parent.mkdir(parents=True, exist_ok=True)
            inbox.write_text("not json\n", encoding="utf-8")
            port = WakeCandidateInboxPort(layout)

            result = port.wake(_command())

            self.assertIs(result.status, RoleWakeEffectStatus.NO_EFFECT)
            self.assertEqual(inbox.read_text(encoding="utf-8"), "not json\n")


if __name__ == "__main__":
    unittest.main()
