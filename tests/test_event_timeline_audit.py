"""Behaviour tests for deterministic local event timeline replay and audit."""

from __future__ import annotations

import unittest

from library.功能集群.python.event_timeline_audit import (
    KnownTimelineEvent,
    TimelineAuditOutcome,
    TimelineAuditReason,
    TimelineConfiguration,
    TimelineEventId,
    TimelineEventKind,
    TimelineState,
    UnknownEventCode,
    UnknownTimelineEvent,
    replay_timeline,
)


class EventTimelineAuditTests(unittest.TestCase):
    """Ensure event replay is explicit, immutable and deterministic."""

    def test_legal_events_transition_state_and_leave_applied_audit(self) -> None:
        replay = replay_timeline(
            configuration=TimelineConfiguration(initial_state=TimelineState.NOT_STARTED),
            events=(
                known_event("001", TimelineEventKind.START),
                known_event("002", TimelineEventKind.ADVANCE),
                known_event("003", TimelineEventKind.FINISH),
            ),
        )

        self.assertEqual(TimelineState.FINISHED, replay.final_state)
        self.assertEqual(3, replay.summary.applied_count)
        self.assertEqual(0, replay.summary.unresolved_count)
        self.assertEqual(0, replay.summary.conflict_count)
        self.assertEqual(
            (
                TimelineAuditOutcome.APPLIED,
                TimelineAuditOutcome.APPLIED,
                TimelineAuditOutcome.APPLIED,
            ),
            tuple(entry.outcome for entry in replay.audit_entries),
        )

    def test_unknown_event_stays_unresolved_and_illegal_order_becomes_conflict(self) -> None:
        replay = replay_timeline(
            configuration=TimelineConfiguration(initial_state=TimelineState.NOT_STARTED),
            events=(
                UnknownTimelineEvent(
                    event_id=TimelineEventId(value="event-unknown"),
                    code=UnknownEventCode(value="unsupported-transition"),
                ),
                known_event("event-finish", TimelineEventKind.FINISH),
            ),
        )

        self.assertEqual(TimelineState.NOT_STARTED, replay.final_state)
        self.assertEqual(TimelineAuditOutcome.UNRESOLVED, replay.audit_entries[0].outcome)
        self.assertEqual(TimelineAuditReason.UNKNOWN_EVENT, replay.audit_entries[0].reason)
        self.assertEqual(TimelineAuditOutcome.CONFLICT, replay.audit_entries[1].outcome)
        self.assertEqual(
            TimelineAuditReason.INVALID_TRANSITION,
            replay.audit_entries[1].reason,
        )
        self.assertEqual(1, replay.summary.unresolved_count)
        self.assertEqual(1, replay.summary.conflict_count)

    def test_same_input_and_configuration_produce_identical_audit_summary_and_hash(
        self,
    ) -> None:
        configuration = TimelineConfiguration(initial_state=TimelineState.NOT_STARTED)
        events = (
            known_event("repeat-001", TimelineEventKind.START),
            known_event("repeat-002", TimelineEventKind.ADVANCE),
            known_event("repeat-003", TimelineEventKind.FINISH),
        )

        first = replay_timeline(configuration=configuration, events=events)
        second = replay_timeline(configuration=configuration, events=events)

        self.assertEqual(first.final_state, second.final_state)
        self.assertEqual(first.audit_entries, second.audit_entries)
        self.assertEqual(first.summary, second.summary)
        self.assertEqual(first.output_hash, second.output_hash)
        self.assertEqual(64, len(first.output_hash.value))

    def test_event_identifiers_reject_raw_content_shapes(self) -> None:
        with self.assertRaises(ValueError):
            UnknownEventCode(value="raw event detail")
        with self.assertRaises(ValueError):
            TimelineEventId(value="event/with/slashes")


def known_event(event_suffix: str, kind: TimelineEventKind) -> KnownTimelineEvent:
    """Build a known event without raw payload or project-specific fields."""
    return KnownTimelineEvent(
        event_id=TimelineEventId(value=event_suffix),
        kind=kind,
    )


if __name__ == "__main__":
    unittest.main()
