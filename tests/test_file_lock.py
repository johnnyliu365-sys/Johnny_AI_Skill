"""Governance 20: the same four properties, now on two platforms.

The lock's contract was written down in W5 and is not up for renegotiation
here: OS-visible rather than in-process, blocking rather than failing,
released when the handle closes, and advisory between cooperating processes.
This file pins each of those four directly on the primitive, so that a future
change to the platform branch cannot quietly demote one of them.

Every exclusion cell uses real processes. Threads share this interpreter's
file handles, so a threaded version of the race below would go green against
an implementation holding nothing but a `threading.Lock` — the lesson W5 paid
for, and the reason the true acceptance for this ticket lives in
`test_worker_assignment.py`, `test_work_queue.py` and `test_dispatch_session.py`,
which this file supplements rather than replaces.

Two cells observe an absence — a waiter that must *not* get in — and an
absence can only be observed over a window. That window is deliberately far
shorter than the ten seconds `msvcrt.LK_LOCK` will retry before it gives up,
so a blocked waiter here is still a waiting one and never an expired one.
"""

from __future__ import annotations

import ast
import errno
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import (
    file_lock,
    live_dispatch_metadata_boundary,
    review_return,
    review_return_consumption,
    windows_senior_review_inbox_store,
    work_queue,
    worker_assignment,
)
from library.local_orchestration.file_lock import (
    ExclusiveFileLock,
    ExclusiveWindowsFileLock,
)

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# Long enough that a genuinely blocked waiter cannot be mistaken for a slow
# one; short enough that the Windows primitive is still retrying rather than
# already exhausted.
_BLOCKED_WINDOW_SECONDS = 3.0

# The positive direction never needs a long wait unless something is wrong, and
# when something is wrong a bounded wait is the difference between a red test
# and a hung suite.
_VERDICT_TIMEOUT_SECONDS = 180


_RACE_CHILD = '''\
import os
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.file_lock import ExclusiveFileLock

lock_path = Path(sys.argv[2])
counter_path = Path(sys.argv[3])
occupant_path = Path(sys.argv[4])
marker = sys.argv[5]

# Pay the import cost, say so, then block until released. Without this gate
# each child starts whenever its own interpreter finished importing, and that
# spread is tens of milliseconds while the unprotected window is one or two:
# the race would be decided by startup jitter instead of by the lock.
print("ready", flush=True)
sys.stdin.readline()

verdict = "ok"
try:
    with ExclusiveFileLock(lock_path):
        if occupant_path.read_text(encoding="utf-8"):
            verdict = "occupied-on-entry"
        occupant_path.write_text(marker, encoding="utf-8")

        value = int(counter_path.read_text(encoding="utf-8"))
        # A real disk flush inside the critical section. The read above and the
        # write below are the lost-update window, and widening it to a flush
        # means a lock that does not cross the process boundary loses updates
        # on every run rather than one run in fifty.
        with counter_path.open("w", encoding="utf-8") as handle:
            handle.write(str(value + 1))
            handle.flush()
            os.fsync(handle.fileno())

        if occupant_path.read_text(encoding="utf-8") != marker:
            verdict = "displaced-inside"
        occupant_path.write_text("", encoding="utf-8")
except Exception as error:
    verdict = "error:" + type(error).__name__ + ":" + str(error)

print(verdict, flush=True)
'''


_HOLDER_CHILD = '''\
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.file_lock import ExclusiveFileLock

with ExclusiveFileLock(Path(sys.argv[2])):
    print("held", flush=True)
    sys.stdin.readline()
print("released", flush=True)
'''


_WAITER_CHILD = '''\
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.file_lock import ExclusiveFileLock

witness_path = Path(sys.argv[3])

print("ready", flush=True)
sys.stdin.readline()

with ExclusiveFileLock(Path(sys.argv[2])):
    witness_path.write_text("acquired", encoding="utf-8")
    print("acquired", flush=True)
'''


def _start_child(script: Path, *arguments: str) -> subprocess.Popen[str]:
    """Run a child rooted in the temporary tree, never inside the checkout.

    Governance 03 recorded that a concurrent process standing in the checkout
    can block a runtime lease teardown on Windows and poison later runs.
    """

    return subprocess.Popen(
        (sys.executable, str(script), str(_REPOSITORY_ROOT), *arguments),
        cwd=str(script.parent),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )


def _await_line(process: subprocess.Popen[str], expected: str) -> None:
    assert process.stdout is not None
    line = process.stdout.readline().strip()
    if line != expected:
        # stdout at EOF means the child is gone, so stderr reads without waiting.
        errors = process.stderr.read() if process.stderr else ""
        raise AssertionError(f"child never said {expected!r}, said {line!r}: {errors}")


def _release_child(process: subprocess.Popen[str]) -> None:
    assert process.stdin is not None
    process.stdin.write("go\n")
    process.stdin.flush()


def _reap(*processes: subprocess.Popen[str]) -> None:
    for process in processes:
        if process.poll() is None:
            process.kill()
        process.wait()


class CrossProcessExclusionTests(unittest.TestCase):
    """Property 1: OS-visible. The one an in-process lock cannot fake."""

    def test_four_processes_under_one_lock_lose_no_update(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            script = base / "race_child.py"
            script.write_text(_RACE_CHILD, encoding="utf-8")
            lock_path = base / "the.lock"
            counter_path = base / "counter.txt"
            occupant_path = base / "occupant.txt"
            counter_path.write_text("0", encoding="utf-8")
            occupant_path.write_text("", encoding="utf-8")

            processes = [
                _start_child(
                    script,
                    str(lock_path),
                    str(counter_path),
                    str(occupant_path),
                    marker,
                )
                for marker in ("race-a", "race-b", "race-c", "race-d")
            ]
            try:
                for process in processes:
                    _await_line(process, "ready")
                for process in processes:
                    _release_child(process)
                verdicts = []
                for process in processes:
                    body, errors = process.communicate(
                        timeout=_VERDICT_TIMEOUT_SECONDS
                    )
                    lines = [line for line in body.splitlines() if line.strip()]
                    if not lines:
                        raise AssertionError("child produced no verdict: " + errors)
                    verdicts.append(lines[-1])
            finally:
                _reap(*processes)

            for verdict in verdicts:
                with self.subTest(verdict=verdict):
                    self.assertEqual(
                        verdict,
                        "ok",
                        "no process may find another one inside the section",
                    )
            self.assertEqual(
                counter_path.read_text(encoding="utf-8"),
                "4",
                f"every increment must survive: {verdicts}",
            )
            self.assertEqual(occupant_path.read_text(encoding="utf-8"), "")


class BlockingAcquisitionTests(unittest.TestCase):
    """Properties 2 and 3: a second taker waits, and gets in on release."""

    def test_a_waiter_is_held_out_and_then_let_in_rather_than_refused(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            holder_script = base / "holder_child.py"
            holder_script.write_text(_HOLDER_CHILD, encoding="utf-8")
            waiter_script = base / "waiter_child.py"
            waiter_script.write_text(_WAITER_CHILD, encoding="utf-8")
            lock_path = base / "the.lock"
            witness_path = base / "witness.txt"

            holder = _start_child(holder_script, str(lock_path))
            waiter = _start_child(
                waiter_script, str(lock_path), str(witness_path)
            )
            try:
                _await_line(holder, "held")
                _await_line(waiter, "ready")
                _release_child(waiter)
                assert waiter.stdin is not None
                waiter.stdin.close()

                try:
                    body, errors = waiter.communicate(
                        timeout=_BLOCKED_WINDOW_SECONDS
                    )
                except subprocess.TimeoutExpired:
                    pass
                else:
                    self.fail(
                        "a waiter must block while the lock is held, not finish: "
                        f"stdout={body!r} stderr={errors!r}"
                    )
                self.assertFalse(
                    witness_path.exists(),
                    "nobody may be inside while the holder is inside",
                )

                _release_child(holder)
                _await_line(holder, "released")
                self.assertEqual(holder.wait(timeout=_VERDICT_TIMEOUT_SECONDS), 0)

                body, errors = waiter.communicate(timeout=_VERDICT_TIMEOUT_SECONDS)
            finally:
                _reap(holder, waiter)

            self.assertEqual(waiter.returncode, 0, f"{body!r} {errors!r}")
            self.assertIn(
                "acquired",
                body,
                f"a released lock must be taken by the waiter: {errors!r}",
            )
            self.assertEqual(witness_path.read_text(encoding="utf-8"), "acquired")


class AbandonedHolderTests(unittest.TestCase):
    """Property 3, the hard half: a holder that never got to clean up."""

    def test_a_killed_holder_leaves_the_lock_takeable(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            holder_script = base / "holder_child.py"
            holder_script.write_text(_HOLDER_CHILD, encoding="utf-8")
            waiter_script = base / "waiter_child.py"
            waiter_script.write_text(_WAITER_CHILD, encoding="utf-8")
            lock_path = base / "the.lock"
            witness_path = base / "witness.txt"

            holder = _start_child(holder_script, str(lock_path))
            waiter = None
            try:
                _await_line(holder, "held")
                holder.kill()
                holder.wait(timeout=_VERDICT_TIMEOUT_SECONDS)

                # A separate process, so a lock left stuck fails this cell
                # instead of hanging the suite.
                waiter = _start_child(
                    waiter_script, str(lock_path), str(witness_path)
                )
                _await_line(waiter, "ready")
                _release_child(waiter)
                body, errors = waiter.communicate(timeout=_VERDICT_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                self.fail("a lock held by a killed process was never released")
            finally:
                _reap(*(item for item in (holder, waiter) if item is not None))

            self.assertEqual(waiter.returncode, 0, f"{body!r} {errors!r}")
            self.assertIn("acquired", body, f"{errors!r}")
            self.assertEqual(witness_path.read_text(encoding="utf-8"), "acquired")


class SequentialReuseTests(unittest.TestCase):
    """Release is a thing that happens, not a thing that is assumed."""

    def test_the_lock_is_takeable_again_by_the_process_that_released_it(self) -> None:
        with TemporaryDirectory() as temporary:
            lock_path = Path(temporary).resolve() / "the.lock"

            for _ in range(3):
                lock = ExclusiveFileLock(lock_path)
                with lock:
                    self.assertIsNotNone(lock._handle)
                self.assertIsNone(
                    lock._handle, "leaving the section must drop the handle"
                )

    def test_leaving_the_section_releases_the_lock_not_just_the_bookkeeping(
        self,
    ) -> None:
        """Ask the operating system, with the safety net taken away.

        All six consumers build the lock inline inside the `with`, so the
        temporary loses its last reference the instant the section ends and
        CPython closes the handle whether or not `__exit__` did anything at
        all. Holding the object here removes that accident, so what is being
        observed is the release rather than the garbage collector.
        """

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            waiter_script = base / "waiter_child.py"
            waiter_script.write_text(_WAITER_CHILD, encoding="utf-8")
            lock_path = base / "the.lock"
            witness_path = base / "witness.txt"

            released = ExclusiveFileLock(lock_path)
            with released:
                pass

            waiter = _start_child(waiter_script, str(lock_path), str(witness_path))
            try:
                _await_line(waiter, "ready")
                _release_child(waiter)
                body, errors = waiter.communicate(timeout=_VERDICT_TIMEOUT_SECONDS)
            finally:
                _reap(waiter)

            self.assertIsNone(released._handle, "the object outlived its section")
            self.assertEqual(waiter.returncode, 0, f"{body!r} {errors!r}")
            self.assertIn(
                "acquired",
                body,
                f"a released lock must be takeable by anyone else: {errors!r}",
            )
            self.assertEqual(witness_path.read_text(encoding="utf-8"), "acquired")

    def test_the_lock_file_is_a_sentinel_that_outlives_the_section(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            lock_path = base / "the.lock"

            with ExclusiveFileLock(lock_path):
                pass

            self.assertTrue(lock_path.is_file(), "the lock file is not deleted")
            self.assertGreaterEqual(lock_path.stat().st_size, 1)
            self.assertEqual(
                [path.name for path in base.iterdir()],
                ["the.lock"],
                "the lock uses the path it was given and creates nothing else",
            )


class AdvisorySemanticsTests(unittest.TestCase):
    """Property 4: the lock binds the takers, never the guarded bytes."""

    def test_a_held_lock_never_freezes_the_state_it_guards(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            holder_script = base / "holder_child.py"
            holder_script.write_text(_HOLDER_CHILD, encoding="utf-8")
            lock_path = base / "the.lock"
            state_path = base / "ledger.json"
            state_path.write_text("{}", encoding="utf-8")

            holder = _start_child(holder_script, str(lock_path))
            try:
                _await_line(holder, "held")

                # Advisory: a process that does not take the lock is not stopped
                # by the operating system. Exclusion is a promise between the
                # participants, which is why every consumer takes it.
                state_path.write_text('{"written": true}', encoding="utf-8")
                self.assertEqual(
                    state_path.read_text(encoding="utf-8"), '{"written": true}'
                )

                _release_child(holder)
                _await_line(holder, "released")
                self.assertEqual(holder.wait(timeout=_VERDICT_TIMEOUT_SECONDS), 0)
            finally:
                _reap(holder)


class UnusableLockPathTests(unittest.TestCase):
    """A lock that cannot be taken must say so, not pretend it was taken."""

    def test_a_missing_parent_directory_fails_by_name_and_admits_nobody(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            absent = base / "absent"
            lock = ExclusiveFileLock(absent / "the.lock")

            with self.assertRaises(FileNotFoundError) as caught:
                with lock:
                    self.fail("an unusable lock path must not admit anybody")

            self.assertEqual(caught.exception.errno, errno.ENOENT)
            self.assertFalse(absent.exists(), "a refused lock creates no directory")
            self.assertIsNone(
                lock._handle, "a failed acquisition may not retain a handle"
            )

    def test_an_empty_path_fails_by_name_and_admits_nobody(self) -> None:
        lock = ExclusiveFileLock(Path(""))

        with self.assertRaises(OSError):
            with lock:
                self.fail("an empty lock path must not admit anybody")

        self.assertIsNone(
            lock._handle, "a failed acquisition may not retain a handle"
        )


class NamingTests(unittest.TestCase):
    """One class, two names, and nothing that could drift into two classes."""

    def test_the_windows_name_is_the_portable_class_itself(self) -> None:
        self.assertIs(ExclusiveWindowsFileLock, ExclusiveFileLock)
        self.assertIs(file_lock.ExclusiveWindowsFileLock, file_lock.ExclusiveFileLock)

    def test_every_consumer_holds_that_same_object(self) -> None:
        for module, attribute in (
            (live_dispatch_metadata_boundary, "_ExclusiveWindowsFileLock"),
            (review_return, "ExclusiveWindowsFileLock"),
            (review_return_consumption, "ExclusiveWindowsFileLock"),
            (windows_senior_review_inbox_store, "_ExclusiveWindowsFileLock"),
            (work_queue, "ExclusiveWindowsFileLock"),
            (worker_assignment, "ExclusiveWindowsFileLock"),
        ):
            with self.subTest(module=module.__name__):
                self.assertIs(getattr(module, attribute), ExclusiveFileLock)

    def test_both_names_are_exported(self) -> None:
        self.assertEqual(
            sorted(file_lock.__all__),
            ["ExclusiveFileLock", "ExclusiveWindowsFileLock"],
        )


class PlatformBindingTests(unittest.TestCase):
    """The branch is taken once, at import, and never again."""

    def setUp(self) -> None:
        self.source = Path(file_lock.__file__).read_text(encoding="utf-8")

    def test_only_this_platforms_primitive_was_ever_imported(self) -> None:
        held = (hasattr(file_lock, "msvcrt"), hasattr(file_lock, "fcntl"))
        self.assertIn(
            held,
            ((True, False), (False, True)),
            "exactly one platform primitive may be bound",
        )
        if sys.platform == "win32":
            self.assertEqual(held, (True, False))
        else:
            self.assertEqual(held, (False, True))

    def test_the_lock_object_names_no_platform(self) -> None:
        body = self.source[self.source.index("class ExclusiveFileLock") :]
        for token in ("sys.platform", "msvcrt", "fcntl", "win32", "if sys"):
            with self.subTest(token=token):
                self.assertNotIn(
                    token, body, "the platform is chosen at import, not per lock"
                )

    def test_acquisition_reaches_the_primitive_through_one_bound_name(self) -> None:
        for method in (ExclusiveFileLock.__enter__, ExclusiveFileLock.__exit__):
            with self.subTest(method=method.__name__):
                names = method.__code__.co_names
                self.assertTrue(
                    {"_acquire", "_release"} & set(names),
                    f"{method.__name__} must call the bound primitive: {names}",
                )
                for token in ("msvcrt", "fcntl", "platform"):
                    self.assertNotIn(token, names)


class PosixBranchSourceGuardTests(unittest.TestCase):
    """A source-level guard on the branch this machine never runs. Not a behaviour test.

    Every other cell in this file proves something by making it happen. These
    cannot, and do not claim to: there is no POSIX machine here, so the `fcntl`
    branch is never imported, never executed, and never observed. Until one
    exists, that branch is guarded by code review alone — and code review is a
    person who has to notice.

    The gap this closes is narrow and specific. `LOCK_EX` to `LOCK_SH` is a
    one-token edit that leaves a valid attribute of a real module in a
    correctly typed call, so `mypy --strict --platform linux` reports success
    on it. It also deletes mutual exclusion outright: shared locks do not
    exclude each other, and four processes walk into the critical section
    together. Nothing automated on this machine objected to that edit, which is
    the same shape as governance 14 — a protection that only lives where nobody
    runs it.

    So these cells read the source rather than the behaviour, and pin the two
    calls in the POSIX branch to the exact constants that make them exclusive
    and blocking. A source guard cannot tell you the lock works. It can tell
    you nobody quietly changed what was asked for, which is the failure that
    actually threatens an unexecuted branch. The behavioural half of this
    remains owed, and is owed to a POSIX machine.
    """

    def setUp(self) -> None:
        source = Path(file_lock.__file__).read_text(encoding="utf-8")
        self.branch = self._platform_branch(ast.parse(source))

    @staticmethod
    def _platform_branch(tree: ast.Module) -> ast.If:
        for node in tree.body:
            if isinstance(node, ast.If):
                test = ast.unparse(node.test).replace('"', "'")
                if test == "sys.platform == 'win32'":
                    return node
        raise AssertionError(
            "the platform is no longer chosen by a module-level "
            "`if sys.platform == \"win32\":`, so this guard cannot find the "
            "POSIX branch; a ticket that restructures the branch must "
            "restructure this guard with it"
        )

    def _posix_flock_call(self, function_name: str) -> ast.Call:
        for node in self.branch.orelse:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                calls = [
                    item
                    for item in ast.walk(node)
                    if isinstance(item, ast.Call)
                    and ast.unparse(item.func) == "fcntl.flock"
                ]
                self.assertEqual(
                    len(calls),
                    1,
                    f"POSIX {function_name} must make exactly one flock call",
                )
                return calls[0]
        raise AssertionError(f"the POSIX branch no longer defines {function_name}")

    def _assert_flock_operation(self, call: ast.Call, expected: str) -> None:
        self.assertEqual(len(call.args), 2, "flock takes a descriptor and one flag")
        self.assertEqual(ast.unparse(call.args[0]), "handle.fileno()")
        self.assertIsInstance(
            call.args[1],
            ast.Attribute,
            "the flag must be one named constant: an expression here is how "
            "LOCK_NB gets combined in and the lock stops blocking",
        )
        self.assertEqual(
            ast.unparse(call.args[1]),
            expected,
            f"the POSIX branch must ask for {expected} and nothing else",
        )

    def test_the_posix_acquisition_asks_for_an_exclusive_blocking_lock(self) -> None:
        self._assert_flock_operation(
            self._posix_flock_call("_acquire"), "fcntl.LOCK_EX"
        )

    def test_the_posix_release_drops_the_lock_it_took(self) -> None:
        self._assert_flock_operation(
            self._posix_flock_call("_release"), "fcntl.LOCK_UN"
        )

    def test_the_posix_branch_holds_the_two_primitives_and_nothing_else(self) -> None:
        imported = [
            alias.name
            for node in self.branch.orelse
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        self.assertEqual(imported, ["fcntl"], "the POSIX branch imports one module")
        self.assertEqual(
            [
                node.name
                for node in self.branch.orelse
                if isinstance(node, ast.FunctionDef)
            ],
            ["_acquire", "_release"],
        )
        self.assertEqual(
            [type(node).__name__ for node in self.branch.orelse],
            ["Import", "FunctionDef", "FunctionDef"],
            "nothing may hide in the branch nobody on this machine executes",
        )


if __name__ == "__main__":
    unittest.main()
