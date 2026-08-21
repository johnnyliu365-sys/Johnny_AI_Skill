"""E12: the wake command rediscovers its endpoint and sends exactly once.

Every cell drives a fake `agentapi.bat` — the real client's actual shape, so
the `cmd.exe /d /c <bat>` invocation is exercised faithfully — and no real
conversation is ever created, so these tests cost no quota and need no IDE.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from library.local_orchestration.antigravity_wake_command import (
    LanguageServerCandidate,
    WakeSendFailure,
    WakeSendStatus,
    default_agentapi_path,
    discover_language_server,
    main,
    probe_candidate,
    send_wake,
)
from library.local_orchestration.command_role_wake_port import CommandRoleWakePort
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.wake_capability import WakeCommandConfig
from library.workflow_router.role_wake_contracts import (
    RoleWakeCommand,
    RoleWakeEffectStatus,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GOOD_TOKEN = "015657dd-21d9-4b11-8830-e35378f41d83"
_GOOD_ADDRESS = "127.0.0.1:61164"


_STUB_PYTHON_ENV_KEY = "JOHNNY_TEST_STUB_PYTHON"
_STUB_RECORDER_ENV_KEY = "JOHNNY_TEST_STUB_RECORDER"


def _fake_agentapi(directory: Path, *, send_exit: int = 0) -> Path:
    """A fake client that records its argv and answers the discovery probe.

    Authentication is honoured: the probe answer depends on the environment
    variables the module is responsible for setting, so a cell that forgot
    them would not pass by accident.
    """

    recorder = directory / "recorder.py"
    recorder.write_text(
        "import json, os, sys\n"
        "record = {\n"
        "    'argv': sys.argv[1:],\n"
        "    'address': os.environ.get('ANTIGRAVITY_LS_ADDRESS'),\n"
        "    'token': os.environ.get('ANTIGRAVITY_CSRF_TOKEN'),\n"
        "}\n"
        "log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calls.jsonl')\n"
        "with open(log, 'a', encoding='utf-8') as handle:\n"
        "    handle.write(json.dumps(record) + '\\n')\n"
        "command = sys.argv[1] if len(sys.argv) > 1 else ''\n"
        "authenticated = (\n"
        f"    record['address'] == {_GOOD_ADDRESS!r}\n"
        f"    and record['token'] == {_GOOD_TOKEN!r}\n"
        ")\n"
        "if command == 'get-conversation-metadata':\n"
        "    if authenticated:\n"
        "        print(json.dumps({'error': 'trajectory not found: probe'}))\n"
        "    else:\n"
        "        print(json.dumps({'error': 'connection error'}))\n"
        "    sys.exit(0)\n"
        "if command == 'send-message':\n"
        f"    sys.exit({send_exit})\n"
        "sys.exit(9)\n",
        encoding="utf-8",
    )
    client = directory / "agentapi.bat"
    # `sys.executable` and `recorder` both live under this checkout's own
    # (possibly non-ASCII) path when the venv is built in-tree, or under a
    # temp directory that could in principle be non-ASCII too. `cmd.exe`
    # decodes a batch file's bytes through its active console code page
    # before re-encoding for `CreateProcess`, and that round trip cannot be
    # trusted for arbitrary Unicode -- Windows 8.3 "short" names don't help
    # either, since they stay non-ASCII whenever the OEM code page can
    # represent the source characters (true for this host's cp950 console).
    # `library.local_orchestration.antigravity_wake_command._invoke` merges
    # the current `os.environ` into the child's environment block, so
    # routing both paths through environment variables sidesteps the file's
    # byte encoding entirely: `cmd.exe` resolves `%VAR%` from the
    # already-Unicode environment, and the script body itself never has to
    # carry anything but fixed ASCII text.
    os.environ[_STUB_PYTHON_ENV_KEY] = sys.executable
    os.environ[_STUB_RECORDER_ENV_KEY] = str(recorder)
    client.write_bytes(
        (
            "@echo off\r\n"
            f'"%{_STUB_PYTHON_ENV_KEY}%" "%{_STUB_RECORDER_ENV_KEY}%" %*\r\n'
        ).encode("ascii")
    )
    return client


@dataclass(frozen=True)
class _RecordedCall:
    """One fake-client invocation, as the recorder saw it."""

    argv: tuple[str, ...]
    address: str | None
    token: str | None

    @property
    def command(self) -> str:
        return self.argv[0] if self.argv else ""

    @property
    def rendered(self) -> str:
        return " ".join(self.argv)


def _calls(directory: Path) -> tuple[_RecordedCall, ...]:
    log = directory / "calls.jsonl"
    if not log.is_file():
        return ()
    recorded: list[_RecordedCall] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        recorded.append(
            _RecordedCall(
                argv=tuple(str(item) for item in entry["argv"]),
                address=entry["address"],
                token=entry["token"],
            )
        )
    return tuple(recorded)


def _payload(directory: Path) -> Path:
    path = directory / "wake-payload.txt"
    path.write_text(
        "protocol=ROLE_WAKE_V1\naction=REVIEW_HANDOFF\n"
        "receipt_id=receipt-vita-feature-001\n",
        encoding="utf-8",
    )
    return path


def _good() -> LanguageServerCandidate:
    return LanguageServerCandidate(_GOOD_ADDRESS, _GOOD_TOKEN)


def _wrong_port() -> LanguageServerCandidate:
    return LanguageServerCandidate("127.0.0.1:1", _GOOD_TOKEN)


class DiscoveryTests(unittest.TestCase):
    """E12-R1: the authenticated endpoint is selected by probing, not guessing."""

    def test_the_probe_separates_the_authenticated_endpoint(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            self.assertFalse(probe_candidate(client, _wrong_port()))
            self.assertTrue(probe_candidate(client, _good()))

    def test_discovery_returns_the_first_proven_candidate(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            found = discover_language_server(
                client, (_wrong_port(), _good(), _wrong_port())
            )
            self.assertEqual(found, _good())

    def test_no_reachable_server_refuses_and_sends_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            status, failure = send_wake(
                "conversation-1",
                _payload(directory),
                agentapi_path=client,
                candidates=(_wrong_port(),),
            )
            self.assertIs(status, WakeSendStatus.REFUSED)
            self.assertIs(failure, WakeSendFailure.NO_LANGUAGE_SERVER)
            sends = [c for c in _calls(directory) if c.command == "send-message"]
            self.assertEqual(sends, [])

    def test_discovery_is_read_only(self) -> None:
        """The probe may only ever ask for metadata."""

        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            discover_language_server(client, (_wrong_port(), _good()))
            for call in _calls(directory):
                with self.subTest(argv=call.argv):
                    self.assertEqual(call.command, "get-conversation-metadata")


class SendTests(unittest.TestCase):
    """E12-R2: exactly one send, carrying the conversation and payload path."""

    def test_a_successful_send_happens_exactly_once(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            payload = _payload(directory)
            status, failure = send_wake(
                "conversation-alpha",
                payload,
                agentapi_path=client,
                candidates=(_good(),),
            )
            self.assertIs(status, WakeSendStatus.SENT)
            self.assertIsNone(failure)

            sends = [c for c in _calls(directory) if c.command == "send-message"]
            self.assertEqual(len(sends), 1)
            self.assertIn("conversation-alpha", sends[0].argv)
            self.assertTrue(
                any(str(payload) in item for item in sends[0].argv),
                f"payload path missing from {sends[0].argv}",
            )
            self.assertEqual(sends[0].address, _GOOD_ADDRESS)
            self.assertEqual(sends[0].token, _GOOD_TOKEN)

    def test_the_message_never_carries_the_payload_body(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            payload = _payload(directory)
            send_wake(
                "conversation-alpha",
                payload,
                agentapi_path=client,
                candidates=(_good(),),
            )
            sends = [c for c in _calls(directory) if c.command == "send-message"]
            rendered = sends[0].rendered
            self.assertNotIn("protocol=ROLE_WAKE_V1", rendered)
            self.assertNotIn("receipt_id=receipt-vita-feature-001", rendered)

    def test_a_failing_send_is_a_typed_refusal(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory, send_exit=3)
            status, failure = send_wake(
                "conversation-alpha",
                _payload(directory),
                agentapi_path=client,
                candidates=(_good(),),
            )
            self.assertIs(status, WakeSendStatus.REFUSED)
            self.assertIs(failure, WakeSendFailure.SEND_FAILED)

    def test_an_absent_payload_refuses_before_discovery(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            status, failure = send_wake(
                "conversation-alpha",
                directory / "missing.txt",
                agentapi_path=client,
                candidates=(_good(),),
            )
            self.assertIs(status, WakeSendStatus.REFUSED)
            self.assertIs(failure, WakeSendFailure.PAYLOAD_UNREADABLE)
            self.assertEqual(_calls(directory), ())

    def test_an_absent_client_refuses(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            status, failure = send_wake(
                "conversation-alpha",
                _payload(directory),
                agentapi_path=directory / "absent.bat",
                candidates=(_good(),),
            )
            self.assertIs(status, WakeSendStatus.REFUSED)
            self.assertIs(failure, WakeSendFailure.AGENTAPI_UNAVAILABLE)


class CommandLineTests(unittest.TestCase):
    def test_missing_arguments_are_refused(self) -> None:
        self.assertEqual(main(()), 2)
        self.assertEqual(main(("--conversation", "c1")), 2)

    def test_the_default_client_path_is_the_real_one(self) -> None:
        self.assertEqual(default_agentapi_path().name, "agentapi.bat")
        self.assertIn("antigravity-ide", default_agentapi_path().parts)


class WakePortIntegrationTests(unittest.TestCase):
    """E12-R3/R4: the module is declarable as a real wake command."""

    def _config(self, client: Path) -> WakeCommandConfig:
        return WakeCommandConfig(
            command=(
                sys.executable,
                "-m",
                "library.local_orchestration.antigravity_wake_command",
                "--conversation",
                "conversation-alpha",
                "--agentapi",
                str(client),
                "{payload_file}",
            ),
            reviewer_ref="role-supervisor-reviewer",
            timeout_seconds=120,
        )

    def _command(self) -> RoleWakeCommand:
        payload = "protocol=ROLE_WAKE_V1\naction=REVIEW_HANDOFF\n"
        import hashlib

        return RoleWakeCommand(
            attempt_id="attempt-e12-wake-001",
            reviewer_task_id="3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            reviewer_thread_id="3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
            host_id="local",
            payload=payload,
            payload_digest="sha256_"
            + hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        )

    def _run(self, directory: Path, client: Path) -> RoleWakeEffectStatus:
        layout = JohnnyRootLayout(base=(directory / "johnny").resolve())
        layout.queue_root.mkdir(parents=True, exist_ok=True)
        environment = dict(os.environ)
        environment["JOHNNY_ANTIGRAVITY_ENDPOINT"] = _GOOD_ADDRESS
        environment["JOHNNY_ANTIGRAVITY_TOKEN"] = _GOOD_TOKEN
        environment["PYTHONPATH"] = str(_REPO_ROOT)
        previous = dict(os.environ)
        os.environ.update(environment)
        try:
            port = CommandRoleWakePort(layout, self._config(client))
            return port.wake(self._command()).status
        finally:
            os.environ.clear()
            os.environ.update(previous)

    def test_the_port_reports_host_accepted_when_the_send_succeeds(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory)
            self.assertIs(
                self._run(directory, client), RoleWakeEffectStatus.HOST_ACCEPTED
            )
            sends = [c for c in _calls(directory) if c.command == "send-message"]
            self.assertEqual(len(sends), 1)
            self.assertIn("attempt-e12-wake-001", sends[0].rendered)

    def test_the_port_reports_no_effect_when_the_send_fails(self) -> None:
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            client = _fake_agentapi(directory, send_exit=3)
            self.assertIs(
                self._run(directory, client), RoleWakeEffectStatus.NO_EFFECT
            )


class EnumerationShapeTests(unittest.TestCase):
    """The real enumerator must never raise, whatever the host looks like."""

    def test_enumeration_is_total(self) -> None:
        from library.local_orchestration.antigravity_wake_command import (
            enumerate_candidates,
        )

        for candidate in enumerate_candidates():
            with self.subTest(address=candidate.address):
                self.assertTrue(candidate.address.startswith("127.0.0.1:"))
                self.assertTrue(candidate.token)


class ShimEncodingTests(unittest.TestCase):
    """The written client script must stay ASCII no matter the host paths.

    Every other cell in this file only sees the non-ASCII-path defect when
    actually run from an in-tree venv built under this repository's own
    (non-ASCII) checkout path -- so a regression here would pass every
    ASCII-path venv run and only resurface the next time someone builds a
    venv inside the tree. Patching `sys.executable` and writing into a
    directory whose own name is non-ASCII makes the defect
    environment-independent: this cell must turn red on the pre-fix code no
    matter where it runs.
    """

    def test_non_ascii_executable_and_recorder_paths_still_produce_an_ascii_client(
        self,
    ) -> None:
        fake_python = (
            r"C:\Users\測試使用者\AI控制工作workflow\.venv\Scripts\python.exe"
        )
        with TemporaryDirectory() as temporary:
            directory = Path(temporary) / "測試目錄"
            directory.mkdir()
            with mock.patch.object(sys, "executable", fake_python), mock.patch.dict(
                os.environ, {}
            ):
                client = _fake_agentapi(directory)
                carried_python = os.environ[_STUB_PYTHON_ENV_KEY]
                carried_recorder = os.environ[_STUB_RECORDER_ENV_KEY]

                # (a) reaching this line at all means _fake_agentapi did not
                #     raise for either non-ASCII path.
                # (b) the client's own bytes are plain ASCII.
                decoded = client.read_bytes().decode("ascii")
                self.assertIn(f"%{_STUB_PYTHON_ENV_KEY}%", decoded)
                self.assertIn(f"%{_STUB_RECORDER_ENV_KEY}%", decoded)
                # (c) both environment variables carried their exact
                #     non-ASCII values, unmangled.
                self.assertEqual(carried_python, fake_python)
                self.assertEqual(carried_recorder, str(directory / "recorder.py"))

        # mock.patch.dict restored os.environ on exiting the `with` above;
        # neither fake value leaked into any later cell's subprocess env.
        self.assertNotEqual(os.environ.get(_STUB_PYTHON_ENV_KEY), fake_python)
        self.assertNotEqual(
            os.environ.get(_STUB_RECORDER_ENV_KEY), str(directory / "recorder.py")
        )


if __name__ == "__main__":
    unittest.main()
