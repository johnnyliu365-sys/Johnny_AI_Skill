"""Behaviour tests for pure local engagement eligibility and reward rules."""

from __future__ import annotations

import unittest

from library.功能集群.python.engagement_rules import (
    EngagementAction,
    EngagementEvaluationAccepted,
    EngagementEvaluationRejected,
    EngagementPolicy,
    EngagementPolicyCatalog,
    EngagementPolicyId,
    EngagementRejectionReason,
    EngagementState,
    EventId,
    EventKind,
    ProgressTarget,
    QualificationRequirement,
    RewardCap,
    UnknownEventCode,
    UnknownEngagementEvent,
    KnownEngagementEvent,
)


class EngagementRulesTests(unittest.TestCase):
    """Keep configurable eligibility, progress and reward rules fail closed."""

    def test_qualified_events_build_explainable_progress_then_permit_one_reward(
        self,
    ) -> None:
        policy = engagement_policy(policy_id="policy-normal", qualifications=2, target=2, cap=1)
        catalog = EngagementPolicyCatalog(policies=(policy,))
        state = EngagementState.initial(policy=policy)

        first_qualification = catalog.evaluate(
            policy_id=policy.policy_id,
            state=state,
            event=known_event("qualification-001", EventKind.QUALIFICATION),
        )
        self.assertIsInstance(first_qualification, EngagementEvaluationAccepted)
        assert isinstance(first_qualification, EngagementEvaluationAccepted)
        self.assertEqual(EngagementAction.QUALIFICATION_RECORDED, first_qualification.action)

        eligible = catalog.evaluate(
            policy_id=policy.policy_id,
            state=first_qualification.state,
            event=known_event("qualification-002", EventKind.QUALIFICATION),
        )
        self.assertIsInstance(eligible, EngagementEvaluationAccepted)
        assert isinstance(eligible, EngagementEvaluationAccepted)
        self.assertEqual(EngagementAction.RECOMMENDATION_ELIGIBLE, eligible.action)

        first_progress = catalog.evaluate(
            policy_id=policy.policy_id,
            state=eligible.state,
            event=known_event("progress-001", EventKind.PROGRESS),
        )
        self.assertIsInstance(first_progress, EngagementEvaluationAccepted)
        assert isinstance(first_progress, EngagementEvaluationAccepted)
        self.assertEqual(EngagementAction.PROGRESS_RECORDED, first_progress.action)

        target_reached = catalog.evaluate(
            policy_id=policy.policy_id,
            state=first_progress.state,
            event=known_event("progress-002", EventKind.PROGRESS),
        )
        self.assertIsInstance(target_reached, EngagementEvaluationAccepted)
        assert isinstance(target_reached, EngagementEvaluationAccepted)
        self.assertEqual(EngagementAction.PROGRESS_TARGET_REACHED, target_reached.action)

        reward = catalog.evaluate(
            policy_id=policy.policy_id,
            state=target_reached.state,
            event=known_event("reward-001", EventKind.REWARD_REQUEST),
        )
        self.assertIsInstance(reward, EngagementEvaluationAccepted)
        assert isinstance(reward, EngagementEvaluationAccepted)
        self.assertEqual(EngagementAction.REWARD_PERMITTED, reward.action)
        self.assertEqual(1, reward.state.rewards_permitted)

    def test_duplicate_event_does_not_duplicate_reward_and_cap_or_ineligible_states_reject(
        self,
    ) -> None:
        policy = engagement_policy(policy_id="policy-guard", qualifications=1, target=1, cap=1)
        catalog = EngagementPolicyCatalog(policies=(policy,))
        initial_state = EngagementState.initial(policy=policy)
        before_eligible = catalog.evaluate(
            policy_id=policy.policy_id,
            state=initial_state,
            event=known_event("early-progress", EventKind.PROGRESS),
        )
        self.assertIsInstance(before_eligible, EngagementEvaluationRejected)
        assert isinstance(before_eligible, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.NOT_RECOMMENDATION_ELIGIBLE, before_eligible.reason)

        qualified = accepted_state(
            catalog,
            policy,
            initial_state,
            known_event("guard-qualification", EventKind.QUALIFICATION),
        )
        target_reached = accepted_state(
            catalog,
            policy,
            qualified,
            known_event("guard-progress", EventKind.PROGRESS),
        )
        reward_event = known_event("guard-reward", EventKind.REWARD_REQUEST)
        rewarded = catalog.evaluate(
            policy_id=policy.policy_id,
            state=target_reached,
            event=reward_event,
        )
        self.assertIsInstance(rewarded, EngagementEvaluationAccepted)
        assert isinstance(rewarded, EngagementEvaluationAccepted)

        duplicate = catalog.evaluate(
            policy_id=policy.policy_id,
            state=rewarded.state,
            event=reward_event,
        )
        self.assertIsInstance(duplicate, EngagementEvaluationRejected)
        assert isinstance(duplicate, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.DUPLICATE_EVENT, duplicate.reason)
        self.assertEqual(1, duplicate.state.rewards_permitted)

        cap_reached = catalog.evaluate(
            policy_id=policy.policy_id,
            state=rewarded.state,
            event=known_event("second-reward", EventKind.REWARD_REQUEST),
        )
        self.assertIsInstance(cap_reached, EngagementEvaluationRejected)
        assert isinstance(cap_reached, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.REWARD_CAP_REACHED, cap_reached.reason)

    def test_unknown_policy_and_event_fail_closed(self) -> None:
        known_policy = engagement_policy(policy_id="known-policy", qualifications=1, target=1, cap=1)
        unknown_policy = engagement_policy(policy_id="unknown-policy", qualifications=1, target=1, cap=1)
        catalog = EngagementPolicyCatalog(policies=(known_policy,))
        unknown_policy_result = catalog.evaluate(
            policy_id=unknown_policy.policy_id,
            state=EngagementState.initial(policy=unknown_policy),
            event=known_event("known-event", EventKind.QUALIFICATION),
        )
        self.assertIsInstance(unknown_policy_result, EngagementEvaluationRejected)
        assert isinstance(unknown_policy_result, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.UNKNOWN_POLICY, unknown_policy_result.reason)

        unknown_event_result = catalog.evaluate(
            policy_id=known_policy.policy_id,
            state=EngagementState.initial(policy=known_policy),
            event=UnknownEngagementEvent(
                event_id=EventId(value="unknown-event"),
                code=UnknownEventCode(value="unsupported"),
            ),
        )
        self.assertIsInstance(unknown_event_result, EngagementEvaluationRejected)
        assert isinstance(unknown_event_result, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.UNKNOWN_EVENT, unknown_event_result.reason)

    def test_policy_rejects_an_externally_constructed_impossible_state(self) -> None:
        policy = engagement_policy(policy_id="policy-state", qualifications=2, target=2, cap=1)
        catalog = EngagementPolicyCatalog(policies=(policy,))
        impossible_state = EngagementState(
            policy_id=policy.policy_id,
            qualification_count=0,
            progress_count=1,
            rewards_permitted=0,
            processed_event_ids=frozenset(),
        )

        result = catalog.evaluate(
            policy_id=policy.policy_id,
            state=impossible_state,
            event=known_event("state-check", EventKind.QUALIFICATION),
        )

        self.assertIsInstance(result, EngagementEvaluationRejected)
        assert isinstance(result, EngagementEvaluationRejected)
        self.assertEqual(EngagementRejectionReason.INVALID_STATE, result.reason)


def engagement_policy(
    policy_id: str, qualifications: int, target: int, cap: int
) -> EngagementPolicy:
    """Build a generic local policy without user, health or reward-account fields."""
    return EngagementPolicy(
        policy_id=EngagementPolicyId(value=policy_id),
        qualification_requirement=QualificationRequirement(value=qualifications),
        progress_target=ProgressTarget(value=target),
        reward_cap=RewardCap(value=cap),
    )


def known_event(event_id: str, kind: EventKind) -> KnownEngagementEvent:
    """Build a typed generic input event without external payload."""
    return KnownEngagementEvent(event_id=EventId(value=event_id), kind=kind)


def accepted_state(
    catalog: EngagementPolicyCatalog,
    policy: EngagementPolicy,
    state: EngagementState,
    event: KnownEngagementEvent,
) -> EngagementState:
    """Advance only through an explicit accepted evaluation in a test sequence."""
    result = catalog.evaluate(policy_id=policy.policy_id, state=state, event=event)
    assert isinstance(result, EngagementEvaluationAccepted)
    return result.state


if __name__ == "__main__":
    unittest.main()
