"""Deterministic lease and model-policy tests without timers or host effects."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest

from pydantic import ValidationError

from library.workflow_router.supervision_policy import (
    ExecutionStartedEvidence,
    LeaseEvent,
    LeaseEventKind,
    LeaseKind,
    LeaseLifecycle,
    ModelOverrideLifecycle,
    ModelOverrideState,
    SupervisionClass,
    SupervisionDecisionKind,
    TicketRepairDecisionKind,
    TicketSplitDimension,
    TicketSplitEvidence,
    reduce_supervision_lease,
    resolve_ticket_repair,
    start_supervision_lease,
)


def _started(started_at: int = 1_000) -> ExecutionStartedEvidence:
    return ExecutionStartedEvidence(
        project_id="prj_0123456789abcdef",
        ticket_ref="ticket-feature-one-001",
        router_receipt_ref="receipt-feature-one-001",
        task_ref="task-implementation-one",
        worktree_ref="worktree-featureone-01",
        branch_ref="branch-featureone-01",
        baseline_commit="1" * 40,
        started_at_ms=started_at,
        host_readback_refs=("evidence-host-readback",),
        exact_ticket_received=True,
        task_active=True,
        ticket_executable=True,
        sole_active_receipt=True,
        binding_fresh=True,
    )


class SupervisionLeasePolicyTests(unittest.TestCase):
    def test_no_lease_exists_before_complete_execution_start_readback(self) -> None:
        evidence = _started().model_copy(update={"task_active": False})
        result = start_supervision_lease(
            "lease-feature-one-001",
            SupervisionClass.LUNA_XHIGH_DEFAULT,
            evidence,
        )
        self.assertEqual(SupervisionDecisionKind.EXECUTION_START_REJECTED, result.decision)
        self.assertIsNone(result.lease)

    def test_luna_has_exact_non_resettable_thirty_minute_total_ceiling(self) -> None:
        started = _started()
        created = start_supervision_lease(
            "lease-feature-one-001",
            SupervisionClass.LUNA_XHIGH_DEFAULT,
            started,
        )
        lease = created.lease
        self.assertIsNotNone(lease)
        if lease is None:
            self.fail("Luna lease was not created")
        self.assertEqual(LeaseKind.TOTAL_EXECUTION, lease.lease_kind)
        self.assertEqual(1_800_000, lease.duration_ms)
        self.assertEqual(started.started_at_ms + 1_800_000, lease.deadline_ms)

        ref_advance = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.EXACT_REF_ADVANCED, occurred_at_ms=10_000),
        )
        self.assertEqual(SupervisionDecisionKind.SILENT_ACTIVITY_RECORDED, ref_advance.decision)
        self.assertEqual(lease.deadline_ms, ref_advance.lease.deadline_ms if ref_advance.lease else None)
        self.assertEqual(0, ref_advance.lease.reset_count if ref_advance.lease else -1)

        before = reduce_supervision_lease(
            lease,
            LeaseEvent(
                kind=LeaseEventKind.DEADLINE_FIRED,
                occurred_at_ms=lease.deadline_ms - 1,
            ),
        )
        self.assertEqual(SupervisionDecisionKind.EVENT_REJECTED, before.decision)

        expired = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.DEADLINE_FIRED, occurred_at_ms=lease.deadline_ms),
        )
        self.assertEqual(
            SupervisionDecisionKind.TICKET_DEFECT_COMPLEXITY_EXCEEDED,
            expired.decision,
        )
        self.assertEqual(LeaseLifecycle.CLOSED, expired.lease.lifecycle if expired.lease else None)

    def test_luna_stopped_incomplete_never_receives_continue(self) -> None:
        lease = start_supervision_lease(
            "lease-feature-one-001",
            SupervisionClass.LUNA_XHIGH_DEFAULT,
            _started(),
        ).lease
        if lease is None:
            self.fail("Luna lease was not created")
        stopped = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.TASK_STOPPED_INCOMPLETE, occurred_at_ms=2_000),
        )
        self.assertEqual(
            SupervisionDecisionKind.TICKET_DEFECT_COMPLEXITY_EXCEEDED,
            stopped.decision,
        )
        self.assertNotEqual(SupervisionDecisionKind.CONTINUE_IMPLEMENTATION, stopped.decision)

    def test_terra_ref_activity_resets_silently_then_allows_one_continue(self) -> None:
        created = start_supervision_lease(
            "lease-feature-one-001",
            SupervisionClass.TERRA_OR_HIGHER,
            _started(),
        )
        lease = created.lease
        if lease is None:
            self.fail("Terra lease was not created")
        self.assertEqual(LeaseKind.INACTIVITY, lease.lease_kind)
        self.assertEqual(7_200_000, lease.duration_ms)

        activity_at = 50_000
        advanced = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.EXACT_REF_ADVANCED, occurred_at_ms=activity_at),
        )
        active = advanced.lease
        if active is None:
            self.fail("Terra activity did not retain the lease")
        self.assertEqual(SupervisionDecisionKind.SILENT_ACTIVITY_RECORDED, advanced.decision)
        self.assertEqual(activity_at + 7_200_000, active.deadline_ms)
        self.assertEqual(1, active.reset_count)

        wake = reduce_supervision_lease(
            active,
            LeaseEvent(kind=LeaseEventKind.DEADLINE_FIRED, occurred_at_ms=active.deadline_ms),
        )
        pending = wake.lease
        if pending is None:
            self.fail("deadline did not retain diagnostic state")
        self.assertEqual(SupervisionDecisionKind.WAKE_REVIEWER_DIAGNOSIS, wake.decision)
        self.assertEqual(LeaseLifecycle.DIAGNOSIS_PENDING, pending.lifecycle)

        continued = reduce_supervision_lease(
            pending,
            LeaseEvent(
                kind=LeaseEventKind.DIAGNOSIS_STOPPED_INCOMPLETE,
                occurred_at_ms=pending.deadline_ms + 10,
            ),
        )
        final_lease = continued.lease
        if final_lease is None:
            self.fail("one Terra continuation did not retain a final lease")
        self.assertEqual(SupervisionDecisionKind.CONTINUE_IMPLEMENTATION, continued.decision)
        self.assertEqual(1, final_lease.continue_count)
        self.assertEqual(LeaseLifecycle.ACTIVE, final_lease.lifecycle)

        second_wake = reduce_supervision_lease(
            final_lease,
            LeaseEvent(
                kind=LeaseEventKind.DEADLINE_FIRED,
                occurred_at_ms=final_lease.deadline_ms,
            ),
        )
        second_pending = second_wake.lease
        if second_pending is None:
            self.fail("second deadline did not retain diagnostic state")
        exhausted = reduce_supervision_lease(
            second_pending,
            LeaseEvent(
                kind=LeaseEventKind.DIAGNOSIS_STOPPED_INCOMPLETE,
                occurred_at_ms=second_pending.deadline_ms + 1,
            ),
        )
        self.assertEqual(
            SupervisionDecisionKind.MODEL_CAPABILITY_INSUFFICIENT,
            exhausted.decision,
        )
        self.assertEqual(LeaseLifecycle.CLOSED, exhausted.lease.lifecycle if exhausted.lease else None)

    def test_terminal_handoff_closes_lease_and_expires_one_ticket_override(self) -> None:
        lease = start_supervision_lease(
            "lease-feature-one-001",
            SupervisionClass.TERRA_OR_HIGHER,
            _started(),
        ).lease
        if lease is None:
            self.fail("Terra lease was not created")
        override = ModelOverrideState(
            ticket_ref=lease.ticket_ref,
            lifecycle=ModelOverrideLifecycle.ACTIVE,
            from_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
            to_class=SupervisionClass.TERRA_OR_HIGHER,
        )
        terminal = reduce_supervision_lease(
            lease,
            LeaseEvent(kind=LeaseEventKind.TERMINAL_HANDOFF, occurred_at_ms=2_000),
            override,
        )
        self.assertEqual(SupervisionDecisionKind.LEASE_CLOSED, terminal.decision)
        self.assertEqual(LeaseLifecycle.CLOSED, terminal.lease.lifecycle if terminal.lease else None)
        self.assertEqual(
            ModelOverrideLifecycle.EXPIRED,
            terminal.model_override.lifecycle if terminal.model_override else None,
        )


class TicketRepairPolicyTests(unittest.TestCase):
    def test_independent_vertical_closures_split_and_horizontal_splits_fail(self) -> None:
        for dimension in (
            TicketSplitDimension.OBSERVABLE_BEHAVIOR_STATE,
            TicketSplitDimension.EXTERNAL_EFFECT,
            TicketSplitDimension.OWNERSHIP_COMPOSITION_ROOT,
            TicketSplitDimension.VERIFICATION_BOUNDARY,
        ):
            decision = resolve_ticket_repair(
                TicketSplitEvidence(
                    ticket_ref="ticket-feature-one-001",
                    dimension=dimension,
                    independently_observable_closure=True,
                )
            )
            self.assertEqual(TicketRepairDecisionKind.SPLIT_FOR_LUNA, decision.decision)

        for dimension in (
            TicketSplitDimension.FILE_BOUNDARY,
            TicketSplitDimension.LINE_COUNT,
            TicketSplitDimension.HORIZONTAL_LAYER,
        ):
            decision = resolve_ticket_repair(
                TicketSplitEvidence(
                    ticket_ref="ticket-feature-one-001",
                    dimension=dimension,
                    independently_observable_closure=True,
                )
            )
            self.assertEqual(TicketRepairDecisionKind.REJECT_ILLEGAL_SPLIT, decision.decision)

    def test_no_legal_split_produces_one_ticket_terra_high_override(self) -> None:
        decision = resolve_ticket_repair(
            TicketSplitEvidence(
                ticket_ref="ticket-feature-one-001",
                dimension=TicketSplitDimension.OBSERVABLE_BEHAVIOR_STATE,
                independently_observable_closure=False,
            )
        )
        self.assertEqual(TicketRepairDecisionKind.REPLACE_WITH_TERRA_HIGH, decision.decision)
        self.assertIsNotNone(decision.model_override)
        self.assertEqual(
            ModelOverrideLifecycle.ACTIVE,
            decision.model_override.lifecycle if decision.model_override else None,
        )


class SupervisionPolicyStrictnessTests(unittest.TestCase):
    def test_models_reject_extra_fields_and_coercion(self) -> None:
        payload = _started().model_dump(mode="json")
        payload["started_at_ms"] = "1000"
        with self.assertRaises(ValidationError):
            ExecutionStartedEvidence.model_validate(payload, strict=True)

    def test_policy_is_pure_and_has_no_wait_or_recurring_runtime_dependency(self) -> None:
        source_path = (
            Path(__file__).resolve().parents[1]
            / "library"
            / "workflow_router"
            / "supervision_policy.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_roots.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        self.assertTrue(
            imported_roots.isdisjoint(
                {"asyncio", "subprocess", "threading", "time", "watchdog"}
            )
        )
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(
            called_names.isdisjoint(
                {"sleep", "wait", "setInterval", "setTimeout", "schedule"}
            )
        )

        payload = _started().model_dump(mode="json")
        payload["heartbeat_interval"] = 60
        with self.assertRaises(ValidationError):
            ExecutionStartedEvidence.model_validate(payload, strict=True)


if __name__ == "__main__":
    unittest.main()
