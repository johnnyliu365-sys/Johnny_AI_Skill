"""Wayfinder bounded information-gap protocol tests (CHG-20260818-025)."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router.contracts import (
    ArtifactKind,
    ArtifactRef,
    AuthorityState,
    ContinuationDirective,
    DeliveryStage,
    HumanWaitReason,
    ProcessStage,
    RouterEvent,
    RouterEventKind,
    RouterOutcome,
    RouterState,
    WayfinderBlockKind,
    WayfinderInfoRequest,
    WayfinderInputField,
    WayfinderInputGap,
)
from library.workflow_router.profile import build_router_poc_profile
from library.workflow_router.router import RouterEngine


def _gap(
    field: WayfinderInputField = WayfinderInputField.PRODUCT_CORE_PROBLEM,
    feature_id: str | None = None,
) -> WayfinderInputGap:
    return WayfinderInputGap(
        field=field,
        feature_id=feature_id,
        block_kind=WayfinderBlockKind.OUTPUT_FIELD,
        block_reference="product.core_problem",
        question="What single user problem must the MVP solve first?",
    )


class WayfinderInfoRequestContractTests(unittest.TestCase):
    """The typed request itself carries the convergence guarantees."""

    def test_round_counter_is_closed_at_two(self) -> None:
        """W1: a third question round is untypable."""

        WayfinderInfoRequest(round_number=1, gaps=(_gap(),))
        WayfinderInfoRequest(
            round_number=2,
            gaps=(_gap(WayfinderInputField.COST_CEILING),),
            answered_fields=(WayfinderInputField.PRODUCT_CORE_PROBLEM,),
        )
        with self.assertRaises(ValidationError):
            WayfinderInfoRequest.model_validate(
                {"round_number": 3, "gaps": (_gap().model_dump(),)}
            )

    def test_each_round_lists_one_gap_per_field_and_feature(self) -> None:
        """W2: duplicated gap identities reject; distinct features may repeat a field."""

        with self.assertRaises(ValidationError):
            WayfinderInfoRequest(round_number=1, gaps=(_gap(), _gap()))
        request = WayfinderInfoRequest(
            round_number=1,
            gaps=(
                _gap(WayfinderInputField.SLICE_STATES, feature_id="feature-a"),
                _gap(WayfinderInputField.SLICE_STATES, feature_id="feature-b"),
            ),
        )
        self.assertEqual(len(request.gaps), 2)

    def test_rounds_shrink_and_never_reask(self) -> None:
        """W3: answered fields are frozen; round bookkeeping is exact."""

        with self.subTest(case="round_one_has_no_answered_fields"):
            with self.assertRaises(ValidationError):
                WayfinderInfoRequest(
                    round_number=1,
                    gaps=(_gap(),),
                    answered_fields=(WayfinderInputField.COST_CEILING,),
                )
        with self.subTest(case="round_two_names_answered_fields"):
            with self.assertRaises(ValidationError):
                WayfinderInfoRequest(
                    round_number=2,
                    gaps=(_gap(),),
                )
        with self.subTest(case="answered_field_never_reasked"):
            with self.assertRaises(ValidationError):
                WayfinderInfoRequest(
                    round_number=2,
                    gaps=(_gap(WayfinderInputField.PRODUCT_CORE_PROBLEM),),
                    answered_fields=(WayfinderInputField.PRODUCT_CORE_PROBLEM,),
                )

    def test_every_question_names_what_it_unblocks(self) -> None:
        """W4: gaps without a block target or with foreign fields are untypable."""

        with self.subTest(case="blank_block_reference"):
            with self.assertRaises(ValidationError):
                WayfinderInputGap(
                    field=WayfinderInputField.BUSINESS_MODEL,
                    feature_id=None,
                    block_kind=WayfinderBlockKind.STRICT_VETO,
                    block_reference="",
                    question="How does this product earn?",
                )
        with self.subTest(case="empty_gap_list"):
            with self.assertRaises(ValidationError):
                WayfinderInfoRequest(round_number=1, gaps=())
        with self.subTest(case="foreign_field_name"):
            with self.assertRaises(ValidationError):
                WayfinderInputGap.model_validate(
                    {
                        "field": "favorite_color",
                        "feature_id": None,
                        "block_kind": "output_field",
                        "block_reference": "product.core_problem",
                        "question": "?",
                    }
                )


class WayfinderInfoRoutingTests(unittest.TestCase):
    """The Router profile declares the wait and the bounded re-entry."""

    def setUp(self) -> None:
        self.profile = build_router_poc_profile()
        self.engine = RouterEngine()
        self.info_request_artifact = ArtifactRef(
            kind=ArtifactKind.WAYFINDER_INFO_REQUEST,
            identifier="wayfinder-info-request-001",
            uri="context://router-framework/wayfinder-info-request",
            revision="1",
        )
        self.goal = ArtifactRef(
            kind=ArtifactKind.PROJECT_GOAL,
            identifier="router-framework-goal",
            uri="project://router-framework/goal",
            revision="2",
        )

    def _state(self, artifact: ArtifactRef) -> RouterState:
        return RouterState(
            project_id="router-framework-poc",
            stage=ProcessStage.WAYFINDER,
            authority_state=AuthorityState.APPROVED,
            delivery_stage=DeliveryStage.POC,
            artifact_refs=(artifact,),
        )

    def test_info_required_is_a_declared_owner_wait(self) -> None:
        """W5: the gap round suspends with an exact declared wait reason."""

        rule = self.profile.rule_for(
            current_stage=ProcessStage.WAYFINDER,
            event_kind=RouterEventKind.WAYFINDER_INFO_REQUIRED,
        )
        self.assertIsNotNone(rule)
        assert rule is not None
        self.assertIs(rule.outcome, RouterOutcome.SUSPEND)
        self.assertTrue(rule.requires_human_approval)
        self.assertIs(rule.wait_reason, HumanWaitReason.WAYFINDER_INPUT_GAP)
        self.assertIsNone(rule.next_stage)

        decision = self.engine.decide(
            state=self._state(self.info_request_artifact),
            event=RouterEvent(
                event_id="evt-wayfinder-gap-001",
                kind=RouterEventKind.WAYFINDER_INFO_REQUIRED,
            ),
            profile=self.profile,
        )
        self.assertIs(decision.outcome, RouterOutcome.SUSPEND)
        self.assertIs(decision.continuation, ContinuationDirective.WAIT_FOR_HUMAN)
        self.assertIs(decision.wait_reason, HumanWaitReason.WAYFINDER_INPUT_GAP)

    def test_owner_input_reenters_wayfinder_exactly(self) -> None:
        """W6: committed answers re-enter WAYFINDER; no other stage is reachable."""

        rule = self.profile.rule_for(
            current_stage=ProcessStage.WAYFINDER,
            event_kind=RouterEventKind.OWNER_INPUT_PROVIDED,
        )
        self.assertIsNotNone(rule)
        assert rule is not None
        self.assertIs(rule.outcome, RouterOutcome.RETRY)
        self.assertIs(rule.next_stage, ProcessStage.WAYFINDER)
        self.assertEqual(
            rule.expected_return.router_events,
            (
                RouterEventKind.WAYFINDER_GO,
                RouterEventKind.WAYFINDER_NO_GO,
                RouterEventKind.WAYFINDER_INFO_REQUIRED,
            ),
        )

        decision = self.engine.decide(
            state=self._state(self.goal),
            event=RouterEvent(
                event_id="evt-owner-input-001",
                kind=RouterEventKind.OWNER_INPUT_PROVIDED,
            ),
            profile=self.profile,
        )
        self.assertIs(decision.outcome, RouterOutcome.RETRY)
        self.assertIs(decision.continuation, ContinuationDirective.AUTO_CONTINUE)
        self.assertIs(decision.next_stage, ProcessStage.WAYFINDER)


if __name__ == "__main__":
    unittest.main()
