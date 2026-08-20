"""The Claude branch wake dispatcher: routing, auth gating, and probe honesty.

Every cell drives the real subprocess path through a stub executable rather
than patching the module's internals, because the defect this dispatcher must
not have is "the command shape drifted from what the CLI accepts" -- and a
mocked runner cannot see that. The stub records the exact argv it received.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from library.local_orchestration.claude_wake_command import (
    ClaudeBranch,
    ClaudeWakeFailure,
    ClaudeWakeStatus,
    default_claude_executable,
    is_capability_probe,
    load_routes,
    main,
    parse_identifiers,
    resolve_branch,
    wake,
)

_PROBE_BODY = '{"probe":true,"note":"johnny wake capability probe"}'

_STUB_SOURCE = '''\
import json
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
config = json.loads((here / "stub-config.json").read_text(encoding="utf-8"))
argv = sys.argv[1:]
with (here / "stub-argv.jsonl").open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(argv) + "\\n")

if argv[:2] == ["auth", "status"]:
    print(json.dumps({"loggedIn": config["logged_in"], "authMethod": "token"}))
    raise SystemExit(0)

print(config["drive_stdout"])
raise SystemExit(config["drive_returncode"])
'''


def _write_stub(
    directory: Path,
    logged_in: bool = True,
    drive_stdout: str = "JOHNNY_PROBE_OK",
    drive_returncode: int = 0,
) -> Path:
    """Build a stub CLI that answers `auth status` and records every argv."""

    (directory / "stub.py").write_text(_STUB_SOURCE, encoding="utf-8")
    (directory / "stub-config.json").write_text(
        json.dumps(
            {
                "logged_in": logged_in,
                "drive_stdout": drive_stdout,
                "drive_returncode": drive_returncode,
            }
        ),
        encoding="utf-8",
    )
    shim = directory / "claude.cmd"
    shim.write_bytes(
        ('@echo off\r\n"%s" "%%~dp0stub.py" %%*\r\n' % sys.executable).encode("ascii")
    )
    return shim


def _recorded(directory: Path) -> list[list[str]]:
    log = directory / "stub-argv.jsonl"
    if not log.is_file():
        return []
    return [
        json.loads(line)
        for line in log.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _routes(directory: Path, entries: list[dict[str, object]]) -> Path:
    path = directory / "claude-branch-routes.json"
    path.write_text(json.dumps({"routes": entries}), encoding="utf-8")
    return path


def _payload(directory: Path, reviewer_ref: str, project_id: str = "SourceProjectA") -> Path:
    path = directory / "wake.json"
    path.write_text(
        "protocol=ROLE_WAKE_V1\n"
        "action=REVIEW_HANDOFF\n"
        f"project_id={project_id}\n"
        f"reviewer_ref={reviewer_ref}\n"
        "receipt_id=receipt-0001\n",
        encoding="utf-8",
    )
    return path


class ExecutableDiscoveryTests(unittest.TestCase):
    """The CLI installs off PATH under a versioned directory."""

    def test_highest_version_wins_and_non_versions_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            roaming = Path(temporary)
            root = roaming / "Claude" / "claude-code"
            for name in ("2.1.229", "2.1.234", "10.0.1", "nightly"):
                directory = root / name
                directory.mkdir(parents=True)
                (directory / "claude.exe").write_bytes(b"")
            found = default_claude_executable({"APPDATA": str(roaming)})
            self.assertIsNotNone(found)
            assert found is not None
            self.assertEqual(found.parent.name, "10.0.1")

    def test_missing_install_root_reports_nothing_rather_than_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIsNone(default_claude_executable({"APPDATA": temporary}))

    def test_environment_override_wins_when_it_is_a_real_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            override = Path(temporary) / "claude.exe"
            override.write_bytes(b"")
            found = default_claude_executable(
                {"JOHNNY_CLAUDE_EXECUTABLE": str(override), "APPDATA": temporary}
            )
            self.assertEqual(found, override)


class PayloadReadingTests(unittest.TestCase):
    """The probe payload and a wake payload must never be confused."""

    def test_probe_payload_is_recognised(self) -> None:
        self.assertTrue(is_capability_probe(_PROBE_BODY))

    def test_wake_payload_is_not_mistaken_for_a_probe(self) -> None:
        body = "protocol=ROLE_WAKE_V1\nreviewer_ref=reviewer-a\n"
        self.assertFalse(is_capability_probe(body))

    def test_json_without_the_probe_flag_is_not_a_probe(self) -> None:
        self.assertFalse(is_capability_probe('{"probe":false}'))
        self.assertFalse(is_capability_probe('{"note":"something"}'))

    def test_identifiers_keep_values_that_contain_equals_signs(self) -> None:
        parsed = parse_identifiers("chain_digest=sha256_a=b\nreviewer_ref=r1\n")
        self.assertEqual(parsed["chain_digest"], "sha256_a=b")
        self.assertEqual(parsed["reviewer_ref"], "r1")


class RouteTableTests(unittest.TestCase):
    """A reviewer reaches its own branch, or the wake is refused by name."""

    def test_distinct_reviewers_resolve_to_distinct_branches(self) -> None:
        branches = (
            ClaudeBranch("reviewer-a", "11111111-1111-4111-8111-111111111111", None),
            ClaudeBranch("reviewer-b", "22222222-2222-4222-8222-222222222222", None),
        )
        first = resolve_branch(branches, "reviewer-a", "SourceProjectA")
        second = resolve_branch(branches, "reviewer-b", "SourceProjectA")
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None and second is not None
        self.assertNotEqual(first.session_id, second.session_id)

    def test_project_scoped_route_outranks_the_agnostic_one(self) -> None:
        branches = (
            ClaudeBranch("reviewer-a", "11111111-1111-4111-8111-111111111111", None),
            ClaudeBranch(
                "reviewer-a", "22222222-2222-4222-8222-222222222222", "SourceProjectA"
            ),
        )
        scoped = resolve_branch(branches, "reviewer-a", "SourceProjectA")
        assert scoped is not None
        self.assertEqual(scoped.session_id, "22222222-2222-4222-8222-222222222222")

    def test_unknown_reviewer_resolves_to_nothing(self) -> None:
        branches = (
            ClaudeBranch("reviewer-a", "11111111-1111-4111-8111-111111111111", None),
        )
        self.assertIsNone(resolve_branch(branches, "reviewer-z", "SourceProjectA"))

    def test_a_non_uuid_session_id_is_refused_rather_than_passed_through(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = _routes(
                Path(temporary),
                [{"reviewer_ref": "reviewer-a", "session_id": "not-a-uuid"}],
            )
            with self.assertRaises(ValueError):
                load_routes(path)

    def test_one_reviewer_may_not_hold_two_branches_in_one_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = _routes(
                Path(temporary),
                [
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "11111111-1111-4111-8111-111111111111",
                    },
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "22222222-2222-4222-8222-222222222222",
                    },
                ],
            )
            with self.assertRaises(ValueError):
                load_routes(path)

    def test_an_absent_routes_file_reads_as_unreadable_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIsNone(load_routes(Path(temporary) / "absent.json"))


class AuthenticationGateTests(unittest.TestCase):
    """An unauthenticated CLI must refuse before it spends a turn."""

    def test_unauthenticated_host_refuses_and_never_drives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory, logged_in=False)
            status, failure = wake(
                _payload(directory, "reviewer-a"),
                executable=shim,
                routes_file=_routes(
                    directory,
                    [
                        {
                            "reviewer_ref": "reviewer-a",
                            "session_id": "11111111-1111-4111-8111-111111111111",
                        }
                    ],
                ),
            )
            self.assertIs(status, ClaudeWakeStatus.REFUSED)
            self.assertIs(failure, ClaudeWakeFailure.NOT_AUTHENTICATED)
            calls = _recorded(directory)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][:2], ["auth", "status"])


class ProbeHonestyTests(unittest.TestCase):
    """A probe that trusts the exit code alone proves nothing worth claiming."""

    def test_probe_drives_a_throwaway_branch_and_reports_capability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory, drive_stdout="JOHNNY_PROBE_OK")
            probe_payload = directory / "probe.json"
            probe_payload.write_text(_PROBE_BODY, encoding="utf-8")

            status, failure = wake(probe_payload, executable=shim)
            self.assertIs(status, ClaudeWakeStatus.CAPABILITY_PROVEN)
            self.assertIsNone(failure)

            drive = _recorded(directory)[-1]
            self.assertEqual(drive[0], "-p")
            self.assertIn("--session-id", drive)
            self.assertNotIn("--resume", drive)

    def test_probe_budget_fits_inside_the_runtime_probe_cap(self) -> None:
        """The runtime kills the probe at 30s; our worst case must land first.

        Bound to the runtime constant rather than to a copied number, so
        raising either dispatcher timeout turns this red instead of shipping
        a host that probes correctly and is killed for being slow.
        """

        from library.local_orchestration import claude_wake_command as module
        from library.local_orchestration.wake_capability import (
            _PROBE_TIMEOUT_SECONDS,
        )

        worst_case = (
            module._AUTH_TIMEOUT_SECONDS + module._PROBE_DRIVE_TIMEOUT_SECONDS
        )
        self.assertLess(worst_case, _PROBE_TIMEOUT_SECONDS)
        self.assertLess(module._PROBE_BUDGET_SECONDS, _PROBE_TIMEOUT_SECONDS)

    def test_exit_zero_without_a_completed_turn_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(
                directory, drive_stdout="something else entirely", drive_returncode=0
            )
            probe_payload = directory / "probe.json"
            probe_payload.write_text(_PROBE_BODY, encoding="utf-8")

            status, failure = wake(probe_payload, executable=shim)
            self.assertIs(status, ClaudeWakeStatus.REFUSED)
            self.assertIs(failure, ClaudeWakeFailure.PROBE_NOT_COMPLETED)


class DeliveryTests(unittest.TestCase):
    """The delivered command resumes the reviewer's own branch by name."""

    def test_wake_resumes_the_mapped_branch_and_names_only_the_payload_path(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory, drive_stdout="done")
            payload = _payload(directory, "reviewer-b")
            routes = _routes(
                directory,
                [
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "11111111-1111-4111-8111-111111111111",
                    },
                    {
                        "reviewer_ref": "reviewer-b",
                        "session_id": "22222222-2222-4222-8222-222222222222",
                    },
                ],
            )

            status, failure = wake(payload, executable=shim, routes_file=routes)
            self.assertIs(status, ClaudeWakeStatus.DELIVERED)
            self.assertIsNone(failure)

            drive = _recorded(directory)[-1]
            self.assertEqual(drive[0], "-p")
            self.assertEqual(drive[1], "--resume")
            self.assertEqual(drive[2], "22222222-2222-4222-8222-222222222222")

            message = drive[3]
            self.assertIn(str(payload), message)
            self.assertNotIn("receipt-0001", message)
            self.assertNotIn("REVIEW_HANDOFF", message)

    def test_two_reviewers_reach_two_different_branches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory, drive_stdout="done")
            routes = _routes(
                directory,
                [
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "11111111-1111-4111-8111-111111111111",
                    },
                    {
                        "reviewer_ref": "reviewer-b",
                        "session_id": "22222222-2222-4222-8222-222222222222",
                    },
                ],
            )
            first = directory / "first.json"
            first.write_text(
                "protocol=ROLE_WAKE_V1\nproject_id=p\nreviewer_ref=reviewer-a\n",
                encoding="utf-8",
            )
            second = directory / "second.json"
            second.write_text(
                "protocol=ROLE_WAKE_V1\nproject_id=p\nreviewer_ref=reviewer-b\n",
                encoding="utf-8",
            )

            self.assertIs(
                wake(first, executable=shim, routes_file=routes)[0],
                ClaudeWakeStatus.DELIVERED,
            )
            self.assertIs(
                wake(second, executable=shim, routes_file=routes)[0],
                ClaudeWakeStatus.DELIVERED,
            )

            drives = [call for call in _recorded(directory) if call[0] == "-p"]
            self.assertEqual(len(drives), 2)
            self.assertNotEqual(drives[0][2], drives[1][2])

    def test_unmapped_reviewer_is_refused_by_name_not_delivered_elsewhere(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory)
            routes = _routes(
                directory,
                [
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "11111111-1111-4111-8111-111111111111",
                    }
                ],
            )
            status, failure = wake(
                _payload(directory, "reviewer-z"), executable=shim, routes_file=routes
            )
            self.assertIs(status, ClaudeWakeStatus.REFUSED)
            self.assertIs(failure, ClaudeWakeFailure.REVIEWER_NOT_MAPPED)
            self.assertEqual(
                [call for call in _recorded(directory) if call[0] == "-p"], []
            )

    def test_a_payload_without_the_protocol_line_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory)
            payload = directory / "wake.json"
            payload.write_text("reviewer_ref=reviewer-a\n", encoding="utf-8")
            status, failure = wake(payload, executable=shim)
            self.assertIs(status, ClaudeWakeStatus.REFUSED)
            self.assertIs(failure, ClaudeWakeFailure.PAYLOAD_MALFORMED)


class CommandEntryTests(unittest.TestCase):
    """The runner reads one typed JSON line and an exit code, nothing else."""

    def test_missing_payload_argument_refuses_with_one_line(self) -> None:
        code = main(())
        self.assertEqual(code, 2)

    def test_delivered_wake_exits_zero_through_the_module_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            shim = _write_stub(directory, drive_stdout="done")
            payload = _payload(directory, "reviewer-a")
            routes = _routes(
                directory,
                [
                    {
                        "reviewer_ref": "reviewer-a",
                        "session_id": "11111111-1111-4111-8111-111111111111",
                    }
                ],
            )
            completed = subprocess.run(
                (
                    sys.executable,
                    "-m",
                    "library.local_orchestration.claude_wake_command",
                    str(payload),
                    "--executable",
                    str(shim),
                    "--routes",
                    str(routes),
                ),
                capture_output=True,
                cwd=str(Path(__file__).resolve().parents[1]),
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            lines = [
                line
                for line in completed.stdout.decode("utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(lines), 1)
            self.assertEqual(
                json.loads(lines[0]), {"status": ClaudeWakeStatus.DELIVERED.value}
            )


if __name__ == "__main__":
    unittest.main()
