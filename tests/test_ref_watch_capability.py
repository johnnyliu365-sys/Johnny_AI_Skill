"""Ticket 21: the native ref-watch capability is reported by value, never faked.

`windows_native_git_ref.py` is the only file in `library/` that imports
`pywin32` (confirmed here structurally, not just asserted). Importing it, and
everything that imports it, must succeed on every platform; whether a native
exact-ref watch can actually be armed is answered by `probe_ref_watch_capability`
-- a bounded result naming `AVAILABLE` or exactly one reason it is not, in the
same shape `wake_capability.probe_wake_capability` already uses for a
different capability.

Two things this module can never observe for real on this machine: running
without Windows itself, and running on Windows with `pywin32` genuinely
absent (`requirements-dev.txt` installs it here). Both are exercised through
explicit simulation -- a monkeypatched `sys.platform`, a monkeypatched import
flag, or a genuine `ImportError` forced in a subprocess by blanking the
native modules out of `sys.modules` before this module is ever imported.
Nothing here claims to have been verified on a real non-Windows host.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from pydantic import ValidationError

from library.local_orchestration import windows_native_git_ref
from library.local_orchestration.windows_native_git_ref import (
    RefWatchCapabilityFailure,
    RefWatchCapabilityResult,
    RefWatchCapabilityStatus,
    WindowsNativeGitRefNotificationPort,
    probe_ref_watch_capability,
)
from library.workflow_router.git_handoff_contracts import (
    GitNativeFailureSignal,
    GitNativeRegistrationRequest,
    GitNativeRegistrationStatus,
    GitRefSignal,
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_NATIVE_MODULE_NAMES = ("pywintypes", "win32con", "win32event", "win32file")


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


def _repository_with_one_commit(root: Path) -> None:
    _run_git(root, "init", "-b", "main")
    _run_git(root, "config", "user.email", "ref-watch-capability@example.invalid")
    _run_git(root, "config", "user.name", "Ref Watch Capability")
    (root / "source.txt").write_text("baseline\n", encoding="utf-8")
    _run_git(root, "add", "source.txt")
    _run_git(root, "commit", "-m", "baseline")


def _run_isolated_import_script(script: str) -> subprocess.CompletedProcess[str]:
    """Run `script` in a fresh interpreter with the native modules blanked out.

    `sys.modules[name] = None` is the documented way to force the import
    system to raise `ImportError` for that name -- a real failure, not a
    simulated return value -- and running it in a subprocess means the
    blanking can never leak into this test process's own module cache.
    """

    preamble = "\n".join(
        f"import sys; sys.modules[{name!r}] = None" for name in _NATIVE_MODULE_NAMES
    )
    return subprocess.run(
        (sys.executable, "-X", "utf8", "-c", preamble + "\n" + script),
        cwd=_REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


class _Sink:
    def __init__(self) -> None:
        self.signals: list[GitRefSignal] = []
        self.failures: list[GitNativeFailureSignal] = []

    def on_signal(self, signal: GitRefSignal) -> None:
        self.signals.append(signal)

    def on_failure(self, signal: GitNativeFailureSignal) -> None:
        self.failures.append(signal)


class StructuralClaimTests(unittest.TestCase):
    """The premise the whole ticket rests on, checked rather than trusted."""

    def test_windows_native_git_ref_is_the_only_file_importing_pywin32(self) -> None:
        library_root = _REPOSITORY_ROOT / "library"
        offenders: list[str] = []
        for path in library_root.rglob("*.py"):
            if path.name == "windows_native_git_ref.py":
                continue
            text = path.read_text(encoding="utf-8")
            for name in _NATIVE_MODULE_NAMES:
                if f"import {name}" in text:
                    offenders.append(f"{path}: import {name}")
        self.assertEqual(offenders, [])


class ResultShapeTests(unittest.TestCase):
    """Defect class 2: AVAILABLE and UNAVAILABLE must stay mutually exclusive.

    This is the reverse-mutation target for "let 'no watcher' and 'queue
    empty' collapse into the same result": removing this validator would let
    an UNAVAILABLE result carry no reason (indistinguishable from any other
    empty-handed answer) or an AVAILABLE one carry a stray failure.
    """

    def test_an_available_result_accepts_no_failure(self) -> None:
        result = RefWatchCapabilityResult(status=RefWatchCapabilityStatus.AVAILABLE)
        self.assertIsNone(result.failure)

    def test_an_available_result_rejects_a_failure(self) -> None:
        with self.assertRaises(ValidationError):
            RefWatchCapabilityResult(
                status=RefWatchCapabilityStatus.AVAILABLE,
                failure=RefWatchCapabilityFailure.PLATFORM_UNSUPPORTED,
            )

    def test_an_unavailable_result_requires_a_named_failure(self) -> None:
        with self.assertRaises(ValidationError):
            RefWatchCapabilityResult(status=RefWatchCapabilityStatus.UNAVAILABLE)

    def test_an_unavailable_result_with_a_name_is_accepted(self) -> None:
        result = RefWatchCapabilityResult(
            status=RefWatchCapabilityStatus.UNAVAILABLE,
            failure=RefWatchCapabilityFailure.NATIVE_BINDING_UNAVAILABLE,
        )
        self.assertIs(result.failure, RefWatchCapabilityFailure.NATIVE_BINDING_UNAVAILABLE)


class RealProbeOnThisMachineTests(unittest.TestCase):
    """TDD-1: normal behaviour. This machine is genuinely Windows + pywin32."""

    def test_this_windows_machine_reports_available(self) -> None:
        result = probe_ref_watch_capability()
        self.assertIs(result.status, RefWatchCapabilityStatus.AVAILABLE)
        self.assertIsNone(result.failure)

    def test_the_probe_takes_no_argument_a_caller_could_use_to_claim_capability(self) -> None:
        """PITFALL A3: capability is proven, never accepted as a claim."""

        import inspect

        signature = inspect.signature(probe_ref_watch_capability)
        self.assertEqual(list(signature.parameters), [])


class SimulatedDegradationTests(unittest.TestCase):
    """TDD-3 (fail-closed leg): platform and binding absence, simulated.

    Neither can be produced for real on this machine, so both are forced
    through the same seams production code reads -- `sys.platform` and this
    module's own import-outcome flag -- and restored immediately after.
    """

    def test_a_non_windows_platform_is_named(self) -> None:
        with mock.patch.object(sys, "platform", "linux"):
            result = probe_ref_watch_capability()
        self.assertIs(result.status, RefWatchCapabilityStatus.UNAVAILABLE)
        self.assertIs(result.failure, RefWatchCapabilityFailure.PLATFORM_UNSUPPORTED)

    def test_windows_without_the_native_binding_is_named_differently(self) -> None:
        with mock.patch.object(
            windows_native_git_ref,
            "_NATIVE_IMPORT_ERROR",
            "simulated: pywin32 did not import",
        ):
            result = probe_ref_watch_capability()
        self.assertIs(result.status, RefWatchCapabilityStatus.UNAVAILABLE)
        self.assertIs(result.failure, RefWatchCapabilityFailure.NATIVE_BINDING_UNAVAILABLE)

    def test_the_two_unavailable_reasons_are_not_the_same_fact(self) -> None:
        self.assertNotEqual(
            RefWatchCapabilityFailure.PLATFORM_UNSUPPORTED,
            RefWatchCapabilityFailure.NATIVE_BINDING_UNAVAILABLE,
        )


class ImportSafetyTests(unittest.TestCase):
    """TDD-3 / non-negotiable property 1, proven with a genuine ImportError.

    `sys.modules[name] = None` makes the import system raise `ImportError`
    for that name for real; running it in a subprocess means the blanking
    can only ever affect that one throwaway interpreter.
    """

    def test_the_module_itself_imports_cleanly_without_pywin32(self) -> None:
        script = (
            "from library.local_orchestration.windows_native_git_ref import ("
            "probe_ref_watch_capability, RefWatchCapabilityStatus, "
            "RefWatchCapabilityFailure)\n"
            "result = probe_ref_watch_capability()\n"
            "assert result.status is RefWatchCapabilityStatus.UNAVAILABLE, result\n"
            "assert result.failure is RefWatchCapabilityFailure.NATIVE_BINDING_UNAVAILABLE, result\n"
            "print('IMPORT_OK')\n"
        )
        completed = _run_isolated_import_script(script)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("IMPORT_OK", completed.stdout)

    def test_the_runner_and_its_full_import_chain_survive_without_pywin32(self) -> None:
        """The dramatic case: today this takes the entire runner CLI down.

        `event_runner` imports `commit_trigger_intake`, which imports
        `windows_native_git_ref` unconditionally -- so before this ticket,
        losing `pywin32` broke `runner status`, `wake-capability` and
        `wake-inbox` too, none of which have anything to do with Git.
        """

        script = (
            "import library.local_orchestration.event_runner as event_runner\n"
            "import library.local_orchestration.runner_cli as runner_cli\n"
            "assert callable(event_runner.run_event_runner)\n"
            "assert callable(runner_cli.run_runner_command)\n"
            "print('IMPORT_OK')\n"
        )
        completed = _run_isolated_import_script(script)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("IMPORT_OK", completed.stdout)

    def test_reverse_mutation_an_unguarded_import_does_crash(self) -> None:
        """The mutation this whole file guards against, run for real.

        This is the reverse-mutation evidence for non-negotiable property 1:
        take the guard away (import the four native modules unconditionally,
        exactly as the module did before this ticket) and confirm the same
        blanked-module trick now fails with `ImportError` instead of the
        typed `UNAVAILABLE` result above.
        """

        script = "import pywintypes\nprint('UNREACHABLE')\n"
        completed = _run_isolated_import_script(script)
        self.assertNotEqual(completed.returncode, 0)
        self.assertNotIn("UNREACHABLE", completed.stdout)
        # `sys.modules[name] = None` is documented to raise
        # `ModuleNotFoundError`, a subclass of `ImportError` -- either name
        # is acceptable evidence of the crash this ticket's guard prevents.
        self.assertTrue(
            "ImportError" in completed.stderr or "ModuleNotFoundError" in completed.stderr,
            completed.stderr,
        )


class RegistrationDegradesWithoutFakingTests(unittest.TestCase):
    """TDD-3 / non-negotiable properties 3 and 4, at the native port itself.

    `WindowsNativeGitRefNotificationPort.__init__` never touches `pywin32`
    (it only shells out to `git rev-parse`), so construction is unaffected;
    only `.register()` must degrade cleanly instead of raising or pretending.
    """

    def test_register_reports_unavailable_without_touching_native_apis(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(strict=True)
            _repository_with_one_commit(root)
            sink = _Sink()
            port = WindowsNativeGitRefNotificationPort(root, sink)
            request = GitNativeRegistrationRequest(
                event_source_ref="event-source-ref-watch-001",
                subscription_id="subscription-ref-watch-001",
                exact_git_ref="refs/heads/main",
            )
            with mock.patch.object(
                windows_native_git_ref,
                "_NATIVE_IMPORT_ERROR",
                "simulated: pywin32 did not import",
            ):
                result = port.register(request)
            self.assertIs(result.status, GitNativeRegistrationStatus.UNAVAILABLE)
            self.assertIsNone(result.event_source_ref)
            self.assertIsNone(result.subscription_id)
            # No watcher thread exists to cancel; cancellation of an unknown
            # subscription id is defined as a harmless no-op, not a crash.
            self.assertTrue(port.cancel(request.subscription_id))

    def test_no_signal_or_failure_ever_reaches_the_sink_when_unavailable(self) -> None:
        """Property 4: without a watcher, nothing may act as if one exists.

        A commit lands on the watched ref after the degraded `.register()`
        call; because no watch was ever armed, the sink -- and therefore the
        `CommitTriggerSignalTee` a real runner would wrap it in -- never
        hears about it at all.
        """

        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(strict=True)
            _repository_with_one_commit(root)
            sink = _Sink()
            port = WindowsNativeGitRefNotificationPort(root, sink)
            request = GitNativeRegistrationRequest(
                event_source_ref="event-source-ref-watch-002",
                subscription_id="subscription-ref-watch-002",
                exact_git_ref="refs/heads/main",
            )
            with mock.patch.object(
                windows_native_git_ref,
                "_NATIVE_IMPORT_ERROR",
                "simulated: pywin32 did not import",
            ):
                registered = port.register(request)
            self.assertIs(registered.status, GitNativeRegistrationStatus.UNAVAILABLE)

            (root / "source.txt").write_text("baseline\nchange\n", encoding="utf-8")
            _run_git(root, "add", "source.txt")
            _run_git(root, "commit", "-m", "change after degraded registration")

            self.assertEqual(sink.signals, [])
            self.assertEqual(sink.failures, [])


if __name__ == "__main__":
    unittest.main()
