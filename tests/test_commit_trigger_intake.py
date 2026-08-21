"""P7: does a real commit on a watched ref actually become queued work?

P6 walked the three legs on the real store and found the third one had no
foot: `WorkSource.COMMIT_TRIGGER` had no producer anywhere in the library,
`work_queue` had the constructor waiting, and the event runner and the queue
did not reference each other at all. These cells are about the wire, and they
are written so that removing it -- or making it lie -- turns something red.

Nothing here sleeps, arms a timer, or polls. Every cell drives the intake by
handing it the signal a native watcher would have handed it, which is exactly
the one moment the production path has to work with.

The convergence cells deliberately do not assert on a memo of seen commits,
because there is none: one commit is one origin, and `work_queue` already
refuses a repeat of a queued origin. The cell proves the outcome the ticket
asks for -- never two items for one commit -- through the rule that already
exists, so an implementation that grew its own second answer would still have
to keep this green through the queue's.
"""

from __future__ import annotations

import ast
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import event_runner
from library.local_orchestration.commit_trigger_intake import (
    CommitTriggerFailure,
    CommitTriggerIntake,
    CommitTriggerNotificationFactory,
    CommitTriggerSignalTee,
    CommitTriggerStatus,
    build_supervision_with_commit_trigger_intake,
    commit_trigger_failure_path,
    read_commit_trigger_failures,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.receipt_bound_supervision import (
    ReceiptBoundSupervisionController,
)
from library.local_orchestration.work_queue import (
    WorkEnqueueFailure,
    WorkItemLifecycle,
    WorkPullRequest,
    WorkQueueReadStatus,
    WorkSource,
    pull_work,
    queue_path,
    read_work_queue,
)
from library.workflow_router.git_handoff_contracts import (
    GitAncestryResult,
    GitAncestryStatus,
    GitBlobReadResult,
    GitBlobReadStatus,
    GitNativeFailureKind,
    GitNativeFailureSignal,
    GitNativeRegistrationRequest,
    GitNativeRegistrationResult,
    GitNativeRegistrationStatus,
    GitPathChangeResult,
    GitPathChangeStatus,
    GitRefSignal,
    GitRefSnapshotResult,
    GitRefSnapshotStatus,
)
from library.workflow_router.role_wake_contracts import (
    RoleWakeRequest,
    RoleWakeResult,
    RoleWakeStatus,
)
from tests.test_git_handoff_event_adapter import _registration_request
from tests.test_parallel_worker_dispatch import _HOST_NAMES

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_INTAKE_SOURCE = "library/local_orchestration/commit_trigger_intake.py"
_BASELINE = "a" * 40
_COMMIT = "b" * 40
_SECOND_COMMIT = "c" * 40

# The two names in this module that describe a clock. Both belong to the
# supervision deadline that existed before this ticket and are passed straight
# through to the controller; the commit-trigger path schedules nothing. The
# rule is not "no clock-shaped word" but "no clock this module operates".
_DEADLINE_PASSTHROUGH = (
    "MonotonicOneShotDeadlineFactory",
    "SystemMonotonicClock",
)


def _layout(temporary: str) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=Path(temporary).resolve())
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _signal() -> GitRefSignal:
    registration = _registration_request(_BASELINE)
    return GitRefSignal(
        event_source_ref=registration.event_source_ref,
        subscription_id=registration.subscription_id,
    )


class _Readback:
    """A readback whose answer for the watched ref is whatever a cell says.

    Only `read_ref` matters to the intake; the rest of the port exists so the
    object is the real shape rather than a mock that would accept anything.
    """

    def __init__(self, results: tuple[GitRefSnapshotResult, ...]) -> None:
        self._results = list(results)
        self.calls: list[str] = []

    def read_ref(self, exact_git_ref: str) -> GitRefSnapshotResult:
        self.calls.append(exact_git_ref)
        if len(self._results) > 1:
            return self._results.pop(0)
        return self._results[0]

    def path_changed(
        self, prior_commit: str, observed_commit: str, exact_path: str
    ) -> GitPathChangeResult:
        return GitPathChangeResult(status=GitPathChangeStatus.UNCHANGED, changed=False)

    def read_blob(self, commit_id: str, exact_path: str) -> GitBlobReadResult:
        return GitBlobReadResult(status=GitBlobReadStatus.NOT_FOUND)

    def is_ancestor(self, ancestor: str, descendant: str) -> GitAncestryResult:
        return GitAncestryResult(
            status=GitAncestryStatus.IS_ANCESTOR, is_ancestor=True
        )


def _found(commit: str) -> GitRefSnapshotResult:
    return GitRefSnapshotResult(
        status=GitRefSnapshotStatus.FOUND,
        exact_git_ref="refs/heads/main",
        commit_id=commit,
    )


def _intake(layout: JohnnyRootLayout, readback: _Readback) -> CommitTriggerIntake:
    return CommitTriggerIntake(layout, _registration_request(_BASELINE), readback)


class _RecordingSink:
    """The supervision controller's place in the chain, observed."""

    def __init__(self, log: list[str] | None = None) -> None:
        self.signals: list[GitRefSignal] = []
        self.failures: list[GitNativeFailureSignal] = []
        self._log = log

    def on_signal(self, signal: GitRefSignal) -> None:
        self.signals.append(signal)
        if self._log is not None:
            self._log.append("supervision")

    def on_failure(self, signal: GitNativeFailureSignal) -> None:
        self.failures.append(signal)


class _RecordingFactory:
    """A native factory that keeps whatever sink it was asked to serve."""

    def __init__(self) -> None:
        self.sinks: list[object] = []

    def create(self, sink: object) -> "_RecordingPort":
        self.sinks.append(sink)
        return _RecordingPort()


class _RecordingPort:
    def register(
        self, request: GitNativeRegistrationRequest
    ) -> GitNativeRegistrationResult:
        return GitNativeRegistrationResult(
            status=GitNativeRegistrationStatus.REGISTERED,
            event_source_ref=request.event_source_ref,
            subscription_id=request.subscription_id,
        )

    def cancel(self, subscription_id: str) -> bool:
        return True


class _RefusingWakeSubmission:
    def wake(self, request: RoleWakeRequest) -> RoleWakeResult:
        return RoleWakeResult(status=RoleWakeStatus.STORAGE_UNAVAILABLE)


class OneSignalOneItemTests(unittest.TestCase):
    """P7-R1: the observable result the owner signed off on."""

    def test_one_signal_puts_exactly_one_commit_trigger_on_the_queue(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            intake = _intake(layout, _Readback((_found(_COMMIT),)))

            result = intake.on_signal(_signal())

            self.assertIs(result.status, CommitTriggerStatus.ENQUEUED)
            self.assertEqual(result.origin_ref, "git_" + _COMMIT)
            queue = read_work_queue(layout)
            self.assertIs(queue.status, WorkQueueReadStatus.READ)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)
            item = queue.items[0]
            self.assertIs(item.source, WorkSource.COMMIT_TRIGGER)
            self.assertEqual(item.origin_ref, "git_" + _COMMIT)
            self.assertEqual(
                item.ticket_ref, _registration_request(_BASELINE).ticket_ref
            )
            self.assertIs(item.lifecycle, WorkItemLifecycle.PENDING)
            self.assertEqual(item.item_id, result.item_id)

    def test_the_origin_points_at_the_commit_the_ref_actually_carries(self) -> None:
        """The queued origin is read back from the ref, never from the signal.

        A `GitRefSignal` carries no commit and no authority, so an intake that
        invented one would be recording something nobody observed.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            readback = _Readback((_found(_SECOND_COMMIT),))

            result = _intake(layout, readback).on_signal(_signal())

            self.assertEqual(readback.calls, ["refs/heads/main"])
            self.assertEqual(result.origin_ref, "git_" + _SECOND_COMMIT)

    def test_a_later_commit_gets_its_own_item_in_admission_order(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            readback = _Readback((_found(_COMMIT), _found(_SECOND_COMMIT)))
            intake = _intake(layout, readback)

            first = intake.on_signal(_signal())
            second = intake.on_signal(_signal())

            self.assertIs(first.status, CommitTriggerStatus.ENQUEUED)
            self.assertIs(second.status, CommitTriggerStatus.ENQUEUED)
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(
                [item.origin_ref for item in queue.items],
                ["git_" + _COMMIT, "git_" + _SECOND_COMMIT],
            )


class RepeatedSignalTests(unittest.TestCase):
    """P7-R2: the native watch fires more than once; the queue must not."""

    def test_a_repeated_signal_for_one_commit_never_makes_a_second_item(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            intake = _intake(layout, _Readback((_found(_COMMIT),)))

            first = intake.on_signal(_signal())
            repeat = intake.on_signal(_signal())

            self.assertIs(first.status, CommitTriggerStatus.ENQUEUED)
            self.assertIs(repeat.status, CommitTriggerStatus.ALREADY_QUEUED)
            self.assertEqual(repeat.origin_ref, "git_" + _COMMIT)
            self.assertIsNone(repeat.item_id)
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)

    def test_convergence_is_not_a_failure_and_is_not_recorded_as_one(self) -> None:
        """A second hint about one commit is ordinary, not an incident.

        Recording it would fill the honest failure log with noise and hide the
        entries that mean something.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            intake = _intake(layout, _Readback((_found(_COMMIT),)))

            intake.on_signal(_signal())
            repeat = intake.on_signal(_signal())

            self.assertIsNone(repeat.failure)
            self.assertEqual(read_commit_trigger_failures(layout), ())

    def test_convergence_survives_the_item_being_taken(self) -> None:
        """One cause is one piece of work, before and after a consumer takes it."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            intake = _intake(layout, _Readback((_found(_COMMIT),)))
            intake.on_signal(_signal())

            pulled = pull_work(layout, WorkPullRequest(consumer_ref="consumer-p7-001"))
            repeat = intake.on_signal(_signal())

            self.assertIsNotNone(pulled.item)
            self.assertIs(repeat.status, CommitTriggerStatus.ALREADY_QUEUED)
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)


class HonestFailureTests(unittest.TestCase):
    """P7-R3: a commit that could not become work must not disappear."""

    def test_an_unwritable_queue_is_named_with_the_queue_s_own_reason(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            queue_path(layout).write_text("{not a queue", encoding="utf-8")
            intake = _intake(layout, _Readback((_found(_COMMIT),)))

            result = intake.on_signal(_signal())

            self.assertIs(result.status, CommitTriggerStatus.REFUSED)
            self.assertIs(result.failure, CommitTriggerFailure.ENQUEUE_REFUSED)
            self.assertIs(
                result.enqueue_failure, WorkEnqueueFailure.STORAGE_UNAVAILABLE
            )
            records = read_commit_trigger_failures(layout)
            self.assertEqual(len(records), 1)
            self.assertIs(records[0].failure, CommitTriggerFailure.ENQUEUE_REFUSED)
            self.assertIs(
                records[0].enqueue_failure, WorkEnqueueFailure.STORAGE_UNAVAILABLE
            )
            self.assertEqual(records[0].origin_ref, "git_" + _COMMIT)
            self.assertEqual(
                records[0].subscription_id,
                _registration_request(_BASELINE).subscription_id,
            )

    def test_an_unreadable_ref_is_not_reported_as_nothing_happening(self) -> None:
        """The admission-side shape of "unreadable is not empty"."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            unavailable = GitRefSnapshotResult(
                status=GitRefSnapshotStatus.UNAVAILABLE
            )

            result = _intake(layout, _Readback((unavailable,))).on_signal(_signal())

            self.assertIs(result.status, CommitTriggerStatus.REFUSED)
            self.assertIs(result.failure, CommitTriggerFailure.COMMIT_UNREADABLE)
            records = read_commit_trigger_failures(layout)
            self.assertEqual(len(records), 1)
            self.assertIs(records[0].failure, CommitTriggerFailure.COMMIT_UNREADABLE)
            self.assertIsNone(records[0].origin_ref)

    def test_an_absent_ref_and_an_unreadable_ref_are_different_facts(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            absent = GitRefSnapshotResult(status=GitRefSnapshotStatus.NOT_FOUND)

            result = _intake(layout, _Readback((absent,))).on_signal(_signal())

            self.assertIs(result.failure, CommitTriggerFailure.COMMIT_ABSENT)
            self.assertNotEqual(
                CommitTriggerFailure.COMMIT_ABSENT,
                CommitTriggerFailure.COMMIT_UNREADABLE,
            )

    def test_a_commit_too_short_to_be_an_origin_is_refused_by_name(self) -> None:
        """Empty-and-degenerate input: a seven-character identifier is not a digest.

        The queue owns that judgement, and its verdict is carried out rather
        than re-derived here, so both sides keep one definition of what a
        commit origin is.
        """

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)

            result = _intake(layout, _Readback((_found("abc1234"),))).on_signal(
                _signal()
            )

            self.assertIs(result.status, CommitTriggerStatus.REFUSED)
            self.assertIs(result.failure, CommitTriggerFailure.ENQUEUE_REFUSED)
            self.assertIs(
                result.enqueue_failure, WorkEnqueueFailure.ORIGIN_SOURCE_MISMATCH
            )
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(queue.items, ())

    def test_no_failure_is_ever_raised_out_of_the_callback(self) -> None:
        """Every refusal above returned; a raise here would end the watcher."""

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            queue_path(layout).write_text("{not a queue", encoding="utf-8")
            broken = _Readback((_found(_COMMIT),))

            for case in ("enqueue", "readback"):
                with self.subTest(case=case):
                    readback = (
                        broken
                        if case == "enqueue"
                        else _Readback(
                            (GitRefSnapshotResult(
                                status=GitRefSnapshotStatus.UNAVAILABLE
                            ),)
                        )
                    )
                    self.assertIs(
                        _intake(layout, readback).on_signal(_signal()).status,
                        CommitTriggerStatus.REFUSED,
                    )


class SignalBindingTests(unittest.TestCase):
    """Which signals are this intake's business, and which are not."""

    def test_a_signal_for_another_subscription_enqueues_nothing(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            foreign = GitRefSignal(
                event_source_ref="event-source-someone-else-001",
                subscription_id="subscription-someone-else-001",
            )

            result = _intake(layout, _Readback((_found(_COMMIT),))).on_signal(foreign)

            self.assertIs(result.status, CommitTriggerStatus.NOT_BOUND)
            self.assertIsNone(result.failure)
            self.assertEqual(read_commit_trigger_failures(layout), ())
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(queue.items, ())

    def test_a_signal_that_is_not_a_signal_is_refused_by_name(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)

            result = _intake(layout, _Readback((_found(_COMMIT),))).on_signal(
                "refs/heads/main"  # type: ignore[arg-type]
            )

            self.assertIs(result.status, CommitTriggerStatus.REFUSED)
            self.assertIs(result.failure, CommitTriggerFailure.SIGNAL_INVALID)


class SignalTeeTests(unittest.TestCase):
    """P7-R4: the wake path is first, unchanged, and never at this wire's mercy."""

    def test_supervision_sees_the_signal_before_the_queue_does(self) -> None:
        order: list[str] = []

        class _LoggingIntake(CommitTriggerIntake):
            def on_signal(self, signal: GitRefSignal) -> object:  # type: ignore[override]
                order.append("intake")
                return super().on_signal(signal)

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            sink = _RecordingSink(order)
            intake = _LoggingIntake(
                layout, _registration_request(_BASELINE), _Readback((_found(_COMMIT),))
            )

            CommitTriggerSignalTee(sink, intake).on_signal(_signal())

            self.assertEqual(order, ["supervision", "intake"])
            self.assertEqual(len(sink.signals), 1)

    def test_a_faulting_intake_neither_kills_the_callback_nor_vanishes(self) -> None:
        class _ExplodingIntake(CommitTriggerIntake):
            def on_signal(self, signal: GitRefSignal) -> object:  # type: ignore[override]
                raise RuntimeError("the intake contract was broken")

        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            sink = _RecordingSink()
            intake = _ExplodingIntake(
                layout, _registration_request(_BASELINE), _Readback((_found(_COMMIT),))
            )

            CommitTriggerSignalTee(sink, intake).on_signal(_signal())

            self.assertEqual(len(sink.signals), 1)
            records = read_commit_trigger_failures(layout)
            self.assertEqual(len(records), 1)
            self.assertIs(records[0].failure, CommitTriggerFailure.INTAKE_FAULTED)

    def test_a_native_capability_loss_reaches_supervision_untouched(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            sink = _RecordingSink()
            registration = _registration_request(_BASELINE)
            failure = GitNativeFailureSignal(
                event_source_ref=registration.event_source_ref,
                subscription_id=registration.subscription_id,
                failure=GitNativeFailureKind.NOTIFICATION_UNAVAILABLE,
            )

            CommitTriggerSignalTee(
                sink, _intake(layout, _Readback((_found(_COMMIT),)))
            ).on_failure(failure)

            self.assertEqual(sink.failures, [failure])
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(queue.items, ())
            self.assertFalse(commit_trigger_failure_path(layout).exists())


class CompositionTests(unittest.TestCase):
    """The seam: the intake joins the callback the controller already owns."""

    def test_the_factory_hands_the_controller_s_own_sink_to_the_tee(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(temporary)
            inner = _RecordingFactory()
            sink = _RecordingSink()
            intake = _intake(layout, _Readback((_found(_COMMIT),)))

            CommitTriggerNotificationFactory(inner, intake).create(sink)

            self.assertEqual(len(inner.sinks), 1)
            wrapper = inner.sinks[0]
            self.assertIsInstance(wrapper, CommitTriggerSignalTee)
            wrapper.on_signal(_signal())  # type: ignore[attr-defined]
            self.assertEqual(len(sink.signals), 1)
            queue = read_work_queue(layout)
            assert queue.items is not None
            self.assertEqual(len(queue.items), 1)

    def test_the_composition_builds_a_real_controller_over_a_real_repository(
        self,
    ) -> None:
        """Constructibility is the part a fake factory cannot prove."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            layout = _layout(str(base / "johnny"))
            repository = base / "repo"
            repository.mkdir()
            subprocess.run(
                ("git", "-C", str(repository), "init", "--quiet"),
                check=True,
                capture_output=True,
            )

            controller = build_supervision_with_commit_trigger_intake(
                repository,
                _RefusingWakeSubmission(),
                layout,
                _registration_request(_BASELINE),
            )

            self.assertIsInstance(controller, ReceiptBoundSupervisionController)


class RunnerWiringTests(unittest.TestCase):
    """The runner composes this wire, and composes it in exactly one place."""

    def test_the_runner_binds_the_commit_trigger_composition(self) -> None:
        self.assertTrue(
            hasattr(event_runner, "build_supervision_with_commit_trigger_intake")
        )

    def test_the_runner_no_longer_arms_supervision_without_the_wire(self) -> None:
        """A second, un-teed composition would silently detach the queue."""

        assert event_runner.__file__ is not None
        source = Path(event_runner.__file__).read_text(encoding="utf-8")
        self.assertNotIn("build_windows_supervision_without_review_batching", source)
        self.assertEqual(
            source.count("build_supervision_with_commit_trigger_intake("), 1
        )


class IntakeDesignPropertyTests(unittest.TestCase):
    """Properties this wire has to keep, written as cells rather than as habits."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (_REPOSITORY_ROOT / _INTAKE_SOURCE).read_text(encoding="utf-8")

    def test_the_wire_names_no_host_at_all(self) -> None:
        """The route stays universal only while nothing here knows the host.

        The canonical list is imported from the upstream cell rather than
        copied, because a copy is what stops being updated when a host is
        added.
        """

        folded = self.source.lower()
        for name in _HOST_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, folded)

    def test_the_wire_imports_nothing_that_could_schedule_it(self) -> None:
        tree = ast.parse(self.source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        for forbidden in ("time", "sched", "asyncio", "threading", "signal"):
            with self.subTest(module=forbidden):
                self.assertNotIn(forbidden, imported)

    def test_the_wire_operates_no_clock_of_its_own(self) -> None:
        """Only the pre-existing supervision deadline is named, and only passed on."""

        folded = self.source.lower()
        for marker in ("sleep(", "timer(", ".poll(", "while true", "interval"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, folded)
        for name in _DEADLINE_PASSTHROUGH:
            with self.subTest(name=name):
                self.assertIn(name, self.source)

    def test_the_wire_holds_no_issuance_or_assignment_capability(self) -> None:
        """Enqueueing is not a privileged act, and must not become one."""

        for forbidden in (
            "live_dispatch_metadata_store",
            "issuance_scoped_boundary",
            "dispatch_authority",
            "worker_assignment",
            "document_mutation_gate",
        ):
            with self.subTest(module=forbidden):
                self.assertNotIn(forbidden, self.source)


if __name__ == "__main__":
    unittest.main()
