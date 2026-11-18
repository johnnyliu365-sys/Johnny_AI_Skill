"""Wayfinder bounded information-gap rule and the removed-name guard (ticket 65).

Carries over every case of the retired ``test_wayfinder_info_gap.py`` (W1-W4 on the
typed request, W5-W6 on the wait and the re-entry, now asked of
``decide_wayfinder_gap`` instead of the RouterEngine) and adds the refusal of a
third round, the empty cases, and the assertion that no removed module or name
is reachable from either package.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from pydantic import ValidationError

import library.local_orchestration as local_orchestration
import library.workflow_router as workflow_router
from library.workflow_router.contracts import (
    ContinuationDirective,
    HumanWaitReason,
    ProcessStage,
    RouterEventKind,
    RouterOutcome,
    WayfinderBlockKind,
    WayfinderInfoRequest,
    WayfinderInputField,
    WayfinderInputGap,
)
from library.workflow_router.wayfinder_gap import (
    WayfinderGapDecision,
    decide_wayfinder_gap,
)

_ROOT = Path(__file__).resolve().parents[1]

_REMOVED_MODULES: tuple[str, ...] = (
    "library.workflow_router.graph",
    "library.workflow_router.router",
    "library.workflow_router.temporal_runtime",
    "library.workflow_router.integrations",
    "library.workflow_router.collaboration",
    "library.workflow_router.guarded_integration",
    "library.workflow_router.private_router",
    "library.workflow_router.policy_response",
    "library.workflow_router.telemetry_provisioning_contracts",
    "library.workflow_router.review_admission",
    "library.workflow_router.profile",
    "library.workflow_router.telemetry",
    "library.workflow_router.telemetry_cli",
    "library.workflow_router.context_load_report",
    "library.workflow_router.model_role_readiness",
    "library.local_orchestration.johnny_router_cli",
    "library.local_orchestration.johnny_router_composition",
    "library.local_orchestration.telemetry_storage",
    "library.local_orchestration.telemetry_storage.composition",
    "library.local_orchestration.telemetry_storage.contracts",
    "library.local_orchestration.telemetry_storage.johnny_owned_adapter",
    "library.local_orchestration.telemetry_storage.local_lock_adapter",
    "library.local_orchestration.telemetry_storage.ownership_ledger",
)

_REMOVED_NAMES: tuple[str, ...] = (
    "AgentUsage",
    "ApprovedDispatchArtifact",
    "ApprovedDispatchArtifactRegistry",
    "AuditDecision",
    "AuditDeliveryState",
    "AuditDisposition",
    "AuditRequest",
    "AutomaticContinuationRunner",
    "CitationLedger",
    "CollaborationTopologyResolver",
    "CommittedDispatchArtifacts",
    "ContextLoadComparison",
    "ContextLoadMeasurement",
    "ContextLoadValidationReport",
    "ContextResolver",
    "ContextSourceUsage",
    "ContextUsageRecord",
    "ContextUsageValidator",
    "ContinuationMode",
    "CoordinatorOutcome",
    "CorrectionRoute",
    "DependentProposal",
    "DispatchResponseFormatter",
    "EntitlementGrant",
    "EntitlementMode",
    "FakeEntitlementProvider",
    "FakePrivateRouterService",
    "FixedDispatchResponse",
    "GuardedIntegrationCoordinator",
    "GuardedIntegrationDecision",
    "GuardedIntegrationError",
    "GuardedIntegrationRouterAdapter",
    "ImplementationReturnEvent",
    "InMemorySourceGateway",
    "IntegrationResult",
    "IntegrationStatus",
    "JsonlContextUsageStore",
    "LocalContextGate",
    "LocalMetadataNormalizer",
    "MainSnapshot",
    "ModelRoleReadinessGate",
    "PendingAudit",
    "PolicyDocumentMetadata",
    "PolicyDocumentResult",
    "PolicyReadError",
    "PolicyReadOutcome",
    "PrivateRouterClient",
    "ProductActionLabel",
    "ProposalState",
    "RedactedSummary",
    "RenderError",
    "RenderOutcome",
    "RenderedDispatchResponse",
    "ReviewAdmissionGate",
    "RouterEngine",
    "RouterRequestEnvelope",
    "RouterResponseEnvelope",
    "RouterServiceErrorCode",
    "RunAcceptance",
    "StaticApprovedDispatchArtifactRegistry",
    "TelemetryIssueCode",
    "TelemetryMode",
    "build_router_graph",
    "build_router_poc_profile",
    "read_policy_document",
    "render_dispatch_response",
    "resolve_approved_dispatch_artifact",
)


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


def _round_one() -> WayfinderInfoRequest:
    return WayfinderInfoRequest(
        round_number=1,
        gaps=(_gap(), _gap(WayfinderInputField.COST_CEILING)),
    )


def _round_two() -> WayfinderInfoRequest:
    return WayfinderInfoRequest(
        round_number=2,
        gaps=(_gap(WayfinderInputField.COST_CEILING),),
        answered_fields=(WayfinderInputField.PRODUCT_CORE_PROBLEM,),
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


class WayfinderGapDecisionTests(unittest.TestCase):
    """The function declares the wait and the bounded re-entry."""

    def test_a_blocking_gap_is_a_declared_owner_wait(self) -> None:
        """W5: the gap round suspends with an exact declared wait reason."""

        decision = decide_wayfinder_gap((_round_one(),))
        self.assertIs(decision.outcome, RouterOutcome.SUSPEND)
        self.assertIs(decision.continuation, ContinuationDirective.WAIT_FOR_HUMAN)
        self.assertIs(decision.wait_reason, HumanWaitReason.WAYFINDER_INPUT_GAP)
        self.assertTrue(decision.may_ask_again)

    def test_a_blocking_gap_leaves_the_stage_unchanged(self) -> None:
        """W5: the gap round declares no next stage and waits for the owner's input."""

        for rounds in ((_round_one(),), (_round_one(), _round_two())):
            with self.subTest(rounds=len(rounds)):
                decision = decide_wayfinder_gap(rounds)
                self.assertIsNone(decision.next_stage)
                self.assertEqual(
                    decision.expected_return_events,
                    (RouterEventKind.OWNER_INPUT_PROVIDED,),
                )

    def test_owner_input_reenters_wayfinder(self) -> None:
        """W6: committed answers re-enter Wayfinder with an automatic continuation."""

        decision = decide_wayfinder_gap((_round_one(),), owner_input_provided=True)
        self.assertIs(decision.outcome, RouterOutcome.RETRY)
        self.assertIs(decision.continuation, ContinuationDirective.AUTO_CONTINUE)
        self.assertIsNone(decision.wait_reason)
        self.assertTrue(decision.may_ask_again)

    def test_owner_input_reenters_exactly_the_wayfinder_stage(self) -> None:
        """W6: no other stage is reachable, and exactly three returns are expected."""

        for rounds in ((_round_one(),), (_round_one(), _round_two())):
            with self.subTest(rounds=len(rounds)):
                decision = decide_wayfinder_gap(rounds, owner_input_provided=True)
                self.assertIs(decision.next_stage, ProcessStage.WAYFINDER)
                self.assertEqual(
                    decision.expected_return_events,
                    (
                        RouterEventKind.WAYFINDER_GO,
                        RouterEventKind.WAYFINDER_NO_GO,
                        RouterEventKind.WAYFINDER_INFO_REQUIRED,
                    ),
                )

    def test_after_the_second_round_wayfinder_may_not_ask_again(self) -> None:
        waiting = decide_wayfinder_gap((_round_one(), _round_two()))
        self.assertIs(waiting.outcome, RouterOutcome.SUSPEND)
        self.assertFalse(waiting.may_ask_again)
        answered = decide_wayfinder_gap(
            (_round_one(), _round_two()), owner_input_provided=True
        )
        self.assertIs(answered.outcome, RouterOutcome.RETRY)
        self.assertFalse(answered.may_ask_again)

    def test_no_rounds_means_no_blocking_gap(self) -> None:
        for owner_input in (False, True):
            with self.subTest(owner_input_provided=owner_input):
                decision = decide_wayfinder_gap((), owner_input_provided=owner_input)
                self.assertEqual(
                    decision,
                    WayfinderGapDecision(
                        RouterOutcome.ADVANCE,
                        ContinuationDirective.AUTO_CONTINUE,
                        None,
                        True,
                    ),
                )

    def test_a_third_round_is_refused(self) -> None:
        third = WayfinderInfoRequest.model_construct(
            round_number=3,
            gaps=(_gap(WayfinderInputField.COST_CEILING),),
            answered_fields=(WayfinderInputField.PRODUCT_CORE_PROBLEM,),
        )
        with self.assertRaises(ValueError):
            decide_wayfinder_gap((_round_one(), _round_two(), third))
        with self.assertRaises(ValueError):
            decide_wayfinder_gap((_round_one(), _round_two(), _round_two()))

    def test_rounds_out_of_order_or_widening_are_refused(self) -> None:
        with self.subTest(case="round_two_first"):
            with self.assertRaises(ValueError):
                decide_wayfinder_gap((_round_two(),))
        with self.subTest(case="round_one_twice"):
            with self.assertRaises(ValueError):
                decide_wayfinder_gap((_round_one(), _round_one()))
        with self.subTest(case="second_round_asks_a_new_field"):
            widening = WayfinderInfoRequest(
                round_number=2,
                gaps=(_gap(WayfinderInputField.TECH_LIMITS),),
                answered_fields=(WayfinderInputField.PRODUCT_CORE_PROBLEM,),
            )
            with self.assertRaises(ValueError):
                decide_wayfinder_gap((_round_one(), widening))
        with self.subTest(case="second_round_answers_a_field_never_asked"):
            foreign = WayfinderInfoRequest(
                round_number=2,
                gaps=(_gap(WayfinderInputField.COST_CEILING),),
                answered_fields=(WayfinderInputField.TECH_LIMITS,),
            )
            with self.assertRaises(ValueError):
                decide_wayfinder_gap((_round_one(), foreign))


class RemovedRouterLibraryTests(unittest.TestCase):
    """No removed module is importable and no removed name is exported."""

    def test_removed_modules_raise_module_not_found(self) -> None:
        for name in _REMOVED_MODULES:
            with self.subTest(module=name):
                with self.assertRaises(ModuleNotFoundError) as caught:
                    importlib.import_module(name)
                # The error must be about this module, or about a removed parent
                # package of it; a restored file whose own import of another
                # removed module fails is not "absent".
                allowed = {
                    parent
                    for parent in _REMOVED_MODULES
                    if name == parent or name.startswith(parent + ".")
                }
                self.assertIn(caught.exception.name, allowed)

    def test_no_removed_name_is_in_either_all(self) -> None:
        for package in (workflow_router, local_orchestration):
            exported = set(package.__all__)
            for name in _REMOVED_NAMES:
                with self.subTest(package=package.__name__, name=name):
                    self.assertNotIn(name, exported)
                    self.assertFalse(hasattr(package, name))
            for name in package.__all__:
                with self.subTest(package=package.__name__, exported=name):
                    self.assertTrue(hasattr(package, name))

    def test_importing_either_package_loads_no_removed_module(self) -> None:
        probe = (
            "import json, sys\n"
            f"sys.path.insert(0, {str(_ROOT)!r})\n"
            "import library.workflow_router, library.local_orchestration\n"
            f"removed = {list(_REMOVED_MODULES)!r}\n"
            "print(json.dumps([m for m in removed if m in sys.modules]))\n"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", "-c", probe],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            cwd=_ROOT,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), [])

    def test_removed_files_are_absent(self) -> None:
        for name in _REMOVED_MODULES:
            relative = Path(*name.split("."))
            with self.subTest(module=name):
                self.assertFalse((_ROOT / relative.with_suffix(".py")).exists())
                self.assertFalse((_ROOT / relative).exists())


if __name__ == "__main__":
    unittest.main()
