from __future__ import annotations

from unittest import TestCase

from library.workflow_router.contracts import ModelRole, RoleActivityState
from library.workflow_router.profile import (
    build_plugin_distribution_profile,
    build_router_poc_profile,
)


class PluginDistributionProfileTests(TestCase):
    def test_profile_binds_exact_rows_and_preserves_base_contracts(self) -> None:
        base = build_router_poc_profile()
        profile = build_plugin_distribution_profile()

        self.assertEqual(profile.delivery_stage, base.delivery_stage)
        self.assertEqual(profile.router_control_reference, base.router_control_reference)
        self.assertEqual(profile.halt_return_contract, base.halt_return_contract)
        self.assertEqual(profile.transition_rules, base.transition_rules)
        self.assertEqual(profile.profile_id, "plugin-distribution-poc-r02")
        self.assertEqual(profile.profile_version, "2")
        self.assertEqual(profile.shared_context_ref, "ctx-plugin-distribution-r02")
        self.assertEqual(
            profile.architecture_owner_capability_ref,
            "cap-plugin-distribution-architecture-owner-r02",
        )

        assignments = {assignment.role: assignment for assignment in profile.model_role_assignments}
        self.assertEqual(
            assignments[ModelRole.ARCHITECTURE_OWNER].model_ref,
            "model-gpt-5-6-sol-xhigh-architecture-r02",
        )
        self.assertEqual(
            assignments[ModelRole.ARCHITECTURE_OWNER].capability_refs,
            ("cap-plugin-distribution-architecture-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.ARCHITECTURE_OWNER].evidence_refs,
            ("evidence-owner-approved-plugin-architecture-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.ARCHITECTURE_OWNER].activity_state,
            RoleActivityState.ACTIVE,
        )
        self.assertEqual(
            assignments[ModelRole.SUPERVISOR_REVIEWER].model_ref,
            "model-gpt-5-6-terra-high-senior-r02",
        )
        self.assertEqual(
            assignments[ModelRole.SUPERVISOR_REVIEWER].capability_refs,
            ("cap-plugin-distribution-ticket-review-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.SUPERVISOR_REVIEWER].evidence_refs,
            ("evidence-owner-approved-terra-senior-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.SUPERVISOR_REVIEWER].activity_state,
            RoleActivityState.ACTIVE,
        )
        self.assertEqual(
            assignments[ModelRole.IMPLEMENTATION_OWNER].model_ref,
            "model-gpt-5-6-luna-xhigh-implementer-r02",
        )
        self.assertEqual(
            assignments[ModelRole.IMPLEMENTATION_OWNER].capability_refs,
            ("cap-plugin-distribution-implementation-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.IMPLEMENTATION_OWNER].evidence_refs,
            ("evidence-owner-approved-luna-implementer-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.IMPLEMENTATION_OWNER].activity_state,
            RoleActivityState.SLEEPING,
        )
        self.assertEqual(
            assignments[ModelRole.RESEARCH_HELPER].model_ref,
            "model-gpt-5-6-luna-readonly-helper-r02",
        )
        self.assertEqual(
            assignments[ModelRole.RESEARCH_HELPER].capability_refs,
            ("cap-plugin-distribution-readonly-research-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.RESEARCH_HELPER].evidence_refs,
            ("evidence-reviewer-owned-helper-policy-r02",),
        )
        self.assertEqual(
            assignments[ModelRole.RESEARCH_HELPER].activity_state,
            RoleActivityState.SLEEPING,
        )
