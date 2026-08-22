"""TDD cells for canonical provider-neutral executor routing."""

from __future__ import annotations

import ast
from pathlib import Path
from unittest import TestCase

from pydantic import ValidationError

from library.local_orchestration.executor_routing import (
    AssessmentFreshness,
    AssessmentProvenance,
    AssessmentVerification,
    AttemptState,
    EffortTier,
    ExecutorProfile,
    ExecutorProfileRef,
    ExecutorProfileRegistry,
    ExecutorRoutingResolver,
    ExecutorRoutingTable,
    HardTicketAssessment,
    ModelRole,
    OwnerOverrideRecord,
    ProfileAvailability,
    ResolutionStatus,
    RouteEntry,
    RouteRequest,
    RoutingKey,
    RoutingEntry,
    RoutingPurpose,
    VerifiedCapabilityRank,
)


_SOURCE = Path(__file__).resolve().parents[1] / "library/local_orchestration/executor_routing.py"


def _ref(value: str) -> ExecutorProfileRef:
    return ExecutorProfileRef(value=value)


def _profile(
    value: str,
    rank: VerifiedCapabilityRank = VerifiedCapabilityRank.TIER_2,
    availability: ProfileAvailability = ProfileAvailability.AVAILABLE,
    provider: str = "provider-alpha",
    model: str = "model-alpha",
) -> ExecutorProfile:
    return ExecutorProfile(
        ref=_ref(value),
        provider=provider,
        model=model,
        effort=EffortTier.XHIGH,
        verified_capability_rank=rank,
        availability=availability,
        availability_evidence=f"evidence-{value}",
    )


def _key(purpose: RoutingPurpose, role: ModelRole) -> RoutingKey:
    return RoutingKey(role=role, purpose=purpose)


def _entry(
    purpose: RoutingPurpose,
    profile: str,
    role: ModelRole = ModelRole.SUPERVISOR_REVIEWER,
) -> RouteEntry:
    return RouteEntry(key=_key(purpose, role), profile_ref=_ref(profile))


def _table(*entries: RouteEntry) -> ExecutorRoutingTable:
    return ExecutorRoutingTable(routes=entries)


def _resolver(
    table: ExecutorRoutingTable,
    *profiles: ExecutorProfile,
) -> ExecutorRoutingResolver:
    return ExecutorRoutingResolver(table, ExecutorProfileRegistry(profiles=profiles))


def _verification(
    *,
    provenance: AssessmentProvenance = AssessmentProvenance.INDEPENDENTLY_VERIFIED,
    freshness: AssessmentFreshness = AssessmentFreshness.CURRENT,
    ticket: str = "ticket-main",
    closure: str = "closure-main",
    record: str | None = "evidence-verification",
) -> AssessmentVerification:
    return AssessmentVerification(
        provenance=provenance,
        freshness=freshness,
        verified_ticket=ticket,
        verified_closure_revision=closure,
        verification_record=record,
    )


def _assessment(
    ticket: str = "ticket-main",
    closure: str = "closure-main",
    verification: AssessmentVerification | None = None,
    no_further: str = "evidence-decompose",
    exceeds: str = "evidence-capability",
) -> HardTicketAssessment:
    return HardTicketAssessment(
        ticket=ticket,
        closure_revision=closure,
        no_further_decomposition=no_further,
        exceeds_standard_implementation=exceeds,
        verification=verification or _verification(ticket=ticket, closure=closure),
    )


def _request(
    purpose: RoutingPurpose,
    role: ModelRole = ModelRole.SUPERVISOR_REVIEWER,
    ticket: str = "ticket-main",
    closure: str = "closure-main",
    hard_ticket_assessment: HardTicketAssessment | None = None,
    owner_override: OwnerOverrideRecord | None = None,
    owner_override_requested: bool = False,
    attempt_state: AttemptState = AttemptState.INITIAL,
    failed_cycle_count: int = 0,
) -> RouteRequest:
    return RouteRequest(
        key=_key(purpose, role),
        ticket=ticket,
        closure_revision=closure,
        hard_ticket_assessment=hard_ticket_assessment,
        owner_override=owner_override,
        owner_override_requested=owner_override_requested,
        attempt_state=attempt_state,
        failed_cycle_count=failed_cycle_count,
    )


class ExecutorRoutingSelectionTests(TestCase):
    def test_same_semantic_table_selects_two_fictitious_providers(self) -> None:
        table = _table(
            _entry(RoutingPurpose.PROJECT_INITIAL_REVIEW, "profile-alpha"),
            _entry(RoutingPurpose.TICKET_OPENING, "profile-beta"),
        )
        resolver = _resolver(
            table,
            _profile("profile-alpha", provider="provider-alpha", model="model-alpha"),
            _profile("profile-beta", provider="provider-beta", model="model-beta"),
        )

        alpha = resolver.resolve(_request(RoutingPurpose.PROJECT_INITIAL_REVIEW))
        beta = resolver.resolve(_request(RoutingPurpose.TICKET_OPENING))

        self.assertIs(alpha.status, ResolutionStatus.SELECTED)
        self.assertEqual(alpha.selected_profile, _ref("profile-alpha"))
        self.assertIs(beta.status, ResolutionStatus.SELECTED)
        self.assertEqual(beta.selected_profile, _ref("profile-beta"))
        source = _SOURCE.read_text(encoding="utf-8").casefold()
        self.assertNotIn("provider-alpha", source)
        self.assertNotIn("model-alpha", source)

    def test_review_purposes_use_only_their_configured_semantic_routes(self) -> None:
        table = _table(
            _entry(RoutingPurpose.PROJECT_INITIAL_REVIEW, "profile-project"),
            _entry(
                RoutingPurpose.REQUIREMENT_CHANGE_COMPLEX_DECISION_REVIEW,
                "profile-change",
            ),
            _entry(RoutingPurpose.TICKET_OPENING, "profile-opening"),
            _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-independent"),
        )
        resolver = _resolver(
            table,
            _profile("profile-project"),
            _profile("profile-change"),
            _profile("profile-opening"),
            _profile("profile-independent"),
        )

        for purpose, expected in (
            (RoutingPurpose.PROJECT_INITIAL_REVIEW, "profile-project"),
            (
                RoutingPurpose.REQUIREMENT_CHANGE_COMPLEX_DECISION_REVIEW,
                "profile-change",
            ),
            (RoutingPurpose.TICKET_OPENING, "profile-opening"),
            (RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-independent"),
        ):
            result = resolver.resolve(_request(purpose))
            self.assertIs(result.status, ResolutionStatus.SELECTED)
            self.assertEqual(result.selected_profile, _ref(expected))

    def test_normal_implementation_binds_a_no_weaker_reviewer(self) -> None:
        resolver = _resolver(
            _table(
                _entry(
                    RoutingPurpose.IMPLEMENTATION,
                    "profile-implementation",
                    ModelRole.IMPLEMENTATION_OWNER,
                ),
                _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-reviewer"),
            ),
            _profile("profile-implementation", rank=VerifiedCapabilityRank.TIER_2),
            _profile("profile-reviewer", rank=VerifiedCapabilityRank.TIER_2),
        )

        result = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
            )
        )

        self.assertIs(result.status, ResolutionStatus.SELECTED)
        self.assertEqual(result.selected_profile, _ref("profile-implementation"))
        self.assertIsNotNone(result.review_binding)
        assert result.review_binding is not None
        self.assertEqual(result.review_binding.reviewer_profile, _ref("profile-reviewer"))

    def test_elevated_implementation_requires_typed_current_independent_assessment(self) -> None:
        resolver = _resolver(
            _table(
                _entry(
                    RoutingPurpose.IMPLEMENTATION,
                    "profile-elevated",
                    ModelRole.IMPLEMENTATION_OWNER,
                ),
                _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-reviewer"),
            ),
            _profile("profile-elevated", rank=VerifiedCapabilityRank.TIER_3),
            _profile("profile-reviewer", rank=VerifiedCapabilityRank.TIER_3),
        )

        result = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
                hard_ticket_assessment=_assessment(),
            )
        )

        self.assertIs(result.status, ResolutionStatus.SELECTED)
        self.assertIsNotNone(result.review_binding)
        assert result.review_binding is not None
        self.assertEqual(result.review_binding.ticket, "ticket-main")
        self.assertEqual(result.review_binding.closure_revision, "closure-main")


class ExecutorRoutingAdmissionTests(TestCase):
    def test_empty_or_unknown_route_fails_closed_without_a_default(self) -> None:
        resolver = _resolver(
            _table(_entry(RoutingPurpose.TICKET_OPENING, "profile-only")),
            _profile("profile-only"),
        )

        result = resolver.resolve(_request(RoutingPurpose.PROJECT_INITIAL_REVIEW))

        self.assertIs(result.status, ResolutionStatus.ROUTE_NOT_FOUND)
        self.assertIsNone(result.selected_profile)

    def test_missing_profile_is_distinct_from_a_missing_route(self) -> None:
        resolver = _resolver(_table(_entry(RoutingPurpose.TICKET_OPENING, "profile-missing")))

        result = resolver.resolve(_request(RoutingPurpose.TICKET_OPENING))

        self.assertIs(result.status, ResolutionStatus.PROFILE_NOT_FOUND)

    def test_duplicate_table_and_registry_data_is_rejected_by_ordinary_validation(self) -> None:
        route = _entry(RoutingPurpose.TICKET_OPENING, "profile-one")
        with self.assertRaises(ValidationError):
            ExecutorRoutingTable(routes=(route, route))
        with self.assertRaises(ValidationError):
            ExecutorProfileRegistry(
                profiles=(_profile("profile-one"), _profile("profile-one"))
            )

    def test_bypassed_duplicate_table_returns_table_invalid(self) -> None:
        route = _entry(RoutingPurpose.TICKET_OPENING, "profile-one")
        table = ExecutorRoutingTable.model_construct(routes=(route, route))
        resolver = _resolver(table, _profile("profile-one"))

        result = resolver.resolve(_request(RoutingPurpose.TICKET_OPENING))

        self.assertIs(result.status, ResolutionStatus.ROUTING_TABLE_INVALID)

    def test_bypassed_nested_route_returns_table_invalid_before_registry_lookup(self) -> None:
        route = RoutingEntry.model_construct(
            key=_key(RoutingPurpose.TICKET_OPENING, ModelRole.SUPERVISOR_REVIEWER),
            profile_ref=None,
        )
        table = ExecutorRoutingTable.model_construct(routes=(route,))
        malformed_profile = ExecutorProfile.model_construct(
            ref=_ref("profile-one"),
            provider="provider-one",
            model="model-one",
            effort=EffortTier.XHIGH,
            verified_capability_rank=VerifiedCapabilityRank.TIER_2,
            availability=ProfileAvailability.AVAILABLE,
            availability_evidence=None,
        )
        registry = ExecutorProfileRegistry.model_construct(profiles=(malformed_profile,))

        result = ExecutorRoutingResolver(table, registry).resolve(
            _request(RoutingPurpose.TICKET_OPENING)
        )

        self.assertIs(result.status, ResolutionStatus.ROUTING_TABLE_INVALID)

    def test_bypassed_nested_profile_returns_registry_invalid_without_selection(self) -> None:
        route = _entry(RoutingPurpose.TICKET_OPENING, "profile-one")
        table = _table(route)
        malformed_profile = ExecutorProfile.model_construct(
            ref=_ref("profile-one"),
            provider="provider-one",
            model="model-one",
            effort=EffortTier.XHIGH,
            verified_capability_rank=VerifiedCapabilityRank.TIER_2,
            availability=ProfileAvailability.AVAILABLE,
            availability_evidence=None,
        )
        registry = ExecutorProfileRegistry.model_construct(profiles=(malformed_profile,))

        result = ExecutorRoutingResolver(table, registry).resolve(
            _request(RoutingPurpose.TICKET_OPENING)
        )

        self.assertIs(result.status, ResolutionStatus.PROFILE_REGISTRY_INVALID)
        self.assertIsNone(result.selected_profile)

    def test_model_copy_bypass_is_rejected_by_canonical_registry_admission(self) -> None:
        route = _entry(RoutingPurpose.TICKET_OPENING, "profile-one")
        malformed_profile = _profile("profile-one").model_copy(
            update={"availability_evidence": None}
        )
        registry = ExecutorProfileRegistry.model_construct(profiles=(malformed_profile,))

        result = ExecutorRoutingResolver(
            _table(route), registry
        ).resolve(_request(RoutingPurpose.TICKET_OPENING))

        self.assertIs(result.status, ResolutionStatus.PROFILE_REGISTRY_INVALID)

    def test_table_invalid_precedes_registry_invalid(self) -> None:
        route = _entry(RoutingPurpose.TICKET_OPENING, "profile-one")
        malformed_route = RoutingEntry.model_construct(key=route.key, profile_ref=None)
        table = ExecutorRoutingTable.model_construct(routes=(malformed_route,))
        malformed_profile = ExecutorProfile.model_construct(
            ref=_ref("profile-one"),
            provider="provider-one",
            model="model-one",
            effort=EffortTier.XHIGH,
            verified_capability_rank=VerifiedCapabilityRank.TIER_2,
            availability=ProfileAvailability.AVAILABLE,
            availability_evidence=None,
        )
        registry = ExecutorProfileRegistry.model_construct(profiles=(malformed_profile,))

        result = ExecutorRoutingResolver(table, registry).resolve(
            _request(RoutingPurpose.TICKET_OPENING)
        )

        self.assertIs(result.status, ResolutionStatus.ROUTING_TABLE_INVALID)

    def test_unavailable_stale_and_unknown_profiles_do_not_switch_implicitly(self) -> None:
        for availability in (
            ProfileAvailability.UNAVAILABLE,
            ProfileAvailability.STALE,
            ProfileAvailability.UNKNOWN,
        ):
            resolver = _resolver(
                _table(_entry(RoutingPurpose.TICKET_OPENING, "profile-selected")),
                _profile("profile-selected", availability=availability),
                _profile("profile-fallback", provider="provider-beta", model="model-beta"),
            )
            result = resolver.resolve(_request(RoutingPurpose.TICKET_OPENING))
            self.assertIs(result.status, ResolutionStatus.PROFILE_UNAVAILABLE)


class ExecutorRoutingAssessmentTests(TestCase):
    def _resolver_for_elevated(self) -> ExecutorRoutingResolver:
        return _resolver(
            _table(
                _entry(
                    RoutingPurpose.IMPLEMENTATION,
                    "profile-elevated",
                    ModelRole.IMPLEMENTATION_OWNER,
                ),
                _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-reviewer"),
            ),
            _profile("profile-elevated", rank=VerifiedCapabilityRank.TIER_3),
            _profile("profile-reviewer", rank=VerifiedCapabilityRank.TIER_3),
        )

    def test_missing_and_cross_bound_assessment_reject(self) -> None:
        resolver = self._resolver_for_elevated()
        missing = resolver.resolve(
            _request(RoutingPurpose.IMPLEMENTATION, role=ModelRole.IMPLEMENTATION_OWNER)
        )
        cross_ticket = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
                hard_ticket_assessment=_assessment(ticket="ticket-other"),
            )
        )
        wrong_closure = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
                hard_ticket_assessment=_assessment(closure="closure-other"),
            )
        )

        self.assertIs(missing.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_MISSING)
        self.assertIs(cross_ticket.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_INVALID)
        self.assertIs(wrong_closure.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_INVALID)

    def test_verification_provenance_freshness_and_record_are_typed_facts(self) -> None:
        resolver = self._resolver_for_elevated()
        invalid_verifications = (
            _verification(provenance=AssessmentProvenance.SELF_ASSERTED),
            _verification(provenance=AssessmentProvenance.UNVERIFIED),
            _verification(freshness=AssessmentFreshness.STALE),
            _verification(freshness=AssessmentFreshness.UNKNOWN),
            _verification(record=None),
            _verification(ticket="ticket-other"),
            _verification(closure="closure-other"),
            _verification(record="evidence-decompose"),
        )

        for verification in invalid_verifications:
            result = resolver.resolve(
                _request(
                    RoutingPurpose.IMPLEMENTATION,
                    role=ModelRole.IMPLEMENTATION_OWNER,
                    hard_ticket_assessment=_assessment(verification=verification),
                )
            )
            self.assertIs(result.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_INVALID)

    def test_string_contents_do_not_replace_typed_verification_facts(self) -> None:
        resolver = self._resolver_for_elevated()
        assessment = _assessment(
            no_further="self-asserted-evidence",
            exceeds="unverified-capability",
            verification=_verification(record="stale-looking-record"),
        )

        result = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
                hard_ticket_assessment=assessment,
            )
        )

        self.assertIs(result.status, ResolutionStatus.SELECTED)

    def test_bypass_built_verification_is_rejected_by_resolver(self) -> None:
        verification = AssessmentVerification.model_construct(
            provenance=AssessmentProvenance.INDEPENDENTLY_VERIFIED,
            freshness=AssessmentFreshness.CURRENT,
            verified_ticket="ticket-main",
            verified_closure_revision="closure-main",
            verification_record=None,
        )
        assessment = HardTicketAssessment.model_construct(
            ticket="ticket-main",
            closure_revision="closure-main",
            no_further_decomposition="evidence-decompose",
            exceeds_standard_implementation="evidence-capability",
            verification=verification,
        )

        result = self._resolver_for_elevated().resolve(
            RouteRequest.model_construct(
                key=_key(RoutingPurpose.IMPLEMENTATION, ModelRole.IMPLEMENTATION_OWNER),
                ticket="ticket-main",
                closure_revision="closure-main",
                hard_ticket_assessment=assessment,
            )
        )

        self.assertIs(result.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_INVALID)

    def test_bypass_built_assessment_without_verification_is_rejected_by_resolver(self) -> None:
        assessment = HardTicketAssessment.model_construct(
            ticket="ticket-main",
            closure_revision="closure-main",
            no_further_decomposition="evidence-decompose",
            exceeds_standard_implementation="evidence-capability",
        )

        result = self._resolver_for_elevated().resolve(
            RouteRequest.model_construct(
                key=_key(RoutingPurpose.IMPLEMENTATION, ModelRole.IMPLEMENTATION_OWNER),
                ticket="ticket-main",
                closure_revision="closure-main",
                hard_ticket_assessment=assessment,
            )
        )

        self.assertIs(result.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_INVALID)


class ExecutorRoutingRejectionTests(TestCase):
    def test_lower_rank_reviewer_is_a_named_rejection(self) -> None:
        resolver = _resolver(
            _table(
                _entry(
                    RoutingPurpose.IMPLEMENTATION,
                    "profile-implementation",
                    ModelRole.IMPLEMENTATION_OWNER,
                ),
                _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-reviewer"),
            ),
            _profile("profile-implementation", rank=VerifiedCapabilityRank.TIER_2),
            _profile("profile-reviewer", rank=VerifiedCapabilityRank.TIER_1),
        )

        result = resolver.resolve(
            _request(RoutingPurpose.IMPLEMENTATION, role=ModelRole.IMPLEMENTATION_OWNER)
        )

        self.assertIs(result.status, ResolutionStatus.REVIEWER_CAPABILITY_INSUFFICIENT)

    def test_owner_override_missing_unknown_unavailable_and_valid(self) -> None:
        table = _table(_entry(RoutingPurpose.TICKET_OPENING, "profile-base"))
        resolver = _resolver(
            table,
            _profile("profile-base"),
            _profile("profile-valid", provider="provider-beta", model="model-beta"),
            _profile(
                "profile-unavailable",
                availability=ProfileAvailability.UNAVAILABLE,
                provider="provider-beta",
                model="model-unavailable",
            ),
        )
        missing = resolver.resolve(
            _request(RoutingPurpose.TICKET_OPENING, owner_override_requested=True)
        )
        unknown = resolver.resolve(
            _request(
                RoutingPurpose.TICKET_OPENING,
                owner_override_requested=True,
                owner_override=OwnerOverrideRecord(
                    decision="decision-one",
                    selected_profile=_ref("profile-unknown"),
                    reason="owner-approved",
                ),
            )
        )
        unavailable = resolver.resolve(
            _request(
                RoutingPurpose.TICKET_OPENING,
                owner_override_requested=True,
                owner_override=OwnerOverrideRecord(
                    decision="decision-one",
                    selected_profile=_ref("profile-unavailable"),
                    reason="owner-approved",
                ),
            )
        )
        valid = resolver.resolve(
            _request(
                RoutingPurpose.TICKET_OPENING,
                owner_override_requested=True,
                owner_override=OwnerOverrideRecord(
                    decision="decision-one",
                    selected_profile=_ref("profile-valid"),
                    reason="owner-approved",
                ),
            )
        )

        self.assertIs(missing.status, ResolutionStatus.OVERRIDE_RECORD_MISSING)
        self.assertIs(unknown.status, ResolutionStatus.OVERRIDE_PROFILE_INVALID)
        self.assertIs(unavailable.status, ResolutionStatus.OVERRIDE_PROFILE_INVALID)
        self.assertIs(valid.status, ResolutionStatus.SELECTED)
        self.assertEqual(valid.selected_profile, _ref("profile-valid"))

    def test_override_cannot_bypass_elevated_assessment(self) -> None:
        resolver = _resolver(
            _table(
                _entry(
                    RoutingPurpose.IMPLEMENTATION,
                    "profile-elevated",
                    ModelRole.IMPLEMENTATION_OWNER,
                ),
                _entry(RoutingPurpose.INDEPENDENT_TICKET_REVIEW, "profile-reviewer"),
            ),
            _profile("profile-elevated", rank=VerifiedCapabilityRank.TIER_3),
            _profile("profile-lower", rank=VerifiedCapabilityRank.TIER_2),
            _profile("profile-reviewer", rank=VerifiedCapabilityRank.TIER_3),
        )

        result = resolver.resolve(
            _request(
                RoutingPurpose.IMPLEMENTATION,
                role=ModelRole.IMPLEMENTATION_OWNER,
                owner_override_requested=True,
                owner_override=OwnerOverrideRecord(
                    decision="decision-one",
                    selected_profile=_ref("profile-lower"),
                    reason="owner-approved",
                ),
            )
        )

        self.assertIs(result.status, ResolutionStatus.HARD_TICKET_ASSESSMENT_MISSING)

    def test_bounded_failed_cycle_never_selects_a_fallback(self) -> None:
        resolver = _resolver(
            _table(_entry(RoutingPurpose.TICKET_OPENING, "profile-one")),
            _profile("profile-one"),
        )
        failed = resolver.resolve(
            _request(
                RoutingPurpose.TICKET_OPENING,
                attempt_state=AttemptState.FAILED_ONCE,
                failed_cycle_count=1,
            )
        )
        exhausted = resolver.resolve(
            _request(
                RoutingPurpose.TICKET_OPENING,
                attempt_state=AttemptState.BOUNDED_FAILURE,
                failed_cycle_count=2,
            )
        )

        self.assertIs(failed.status, ResolutionStatus.MODEL_CAPABILITY_INSUFFICIENT)
        self.assertIs(exhausted.status, ResolutionStatus.ARCHITECTURE_OWNER_REQUIRED)


class ExecutorRoutingBoundaryTests(TestCase):
    def test_public_models_reject_unknown_null_and_bypass_success_forms(self) -> None:
        with self.assertRaises(ValidationError):
            ExecutorProfileRef(value=None)  # type: ignore[arg-type]
        with self.assertRaises(ValidationError):
            ExecutorProfileRef(  # type: ignore[call-arg]
                value="profile-one", extra_field="unexpected"
            )
        with self.assertRaises(ValidationError):
            RouteRequest(
                key=None,  # type: ignore[arg-type]
                ticket="ticket-main",
                closure_revision="closure-main",
            )
        with self.assertRaises(ValidationError):
            AssessmentVerification(
                provenance="CURRENT",  # type: ignore[arg-type]
                freshness=AssessmentFreshness.CURRENT,
                verified_ticket="ticket-main",
                verified_closure_revision="closure-main",
            )

    def test_resolver_namespace_has_no_effectful_orchestration_imports(self) -> None:
        tree = ast.parse(_SOURCE.read_text(encoding="utf-8"))
        forbidden_parts = (
            "dispatch",
            "receipt",
            "host",
            "credential",
            "process",
            "runner",
        )
        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.append(node.module)
        self.assertFalse(
            any(
                any(part in module.casefold() for part in forbidden_parts)
                for module in imported_modules
            )
        )

    def test_resolver_source_has_no_provider_or_model_literals(self) -> None:
        source = _SOURCE.read_text(encoding="utf-8").casefold()
        for literal in (
            "provider-alpha",
            "provider-beta",
            "model-alpha",
            "model-beta",
            "luna/xhigh",
            "terra/xhigh",
            "sol/high",
        ):
            self.assertNotIn(literal, source)


if __name__ == "__main__":
    import unittest

    unittest.main()
