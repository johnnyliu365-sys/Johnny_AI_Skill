"""Acceptance tests for the model-role specification readiness gate."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from pydantic import ValidationError

from library.workflow_router import (
    ModelRole,
    ModelRoleAssignment,
    ModelRoleReadinessGate,
    RoleActivityState,
    SpecificationClosureEvidence,
    SpecificationClosureKind,
    SpecificationReadinessAssessment,
    SpecificationReadinessBlocker,
    SpecificationReadinessDecision,
    SpecificationReadinessRequest,
    SpecificationWakeReason,
    build_router_poc_profile,
)


_SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "library"
    / "workflow_router"
    / "model_role_readiness.py"
)

_BLOCKER_REASONS: tuple[SpecificationWakeReason, ...] = (
    SpecificationWakeReason.SPEC_AMBIGUOUS,
    SpecificationWakeReason.SPEC_CONTRADICTORY,
    SpecificationWakeReason.PUBLIC_CONTRACT_UNDEFINED,
    SpecificationWakeReason.ACCEPTANCE_UNPROVABLE,
    SpecificationWakeReason.ARCHITECTURE_CONFLICT,
    SpecificationWakeReason.CROSS_TICKET_DESIGN_CONFLICT,
    SpecificationWakeReason.REQUIREMENT_CHANGED,
    SpecificationWakeReason.NEW_EXTERNAL_PRIVILEGED_BOUNDARY,
    SpecificationWakeReason.HIGH_ASSURANCE_TRIGGER,
    SpecificationWakeReason.MODEL_CAPABILITY_INSUFFICIENT,
)


def _closures() -> tuple[SpecificationClosureEvidence, ...]:
    return tuple(
        SpecificationClosureEvidence(
            kind=kind,
            evidence_ref=f"closure-evidence-{index:02d}",
        )
        for index, kind in enumerate(SpecificationClosureKind)
    )


def _request(
    profile_ref: str = "router-framework-poc",
    profile_version: str = "2",
    *,
    owner_approval_ref: str | None = "approval-spec-01",
    closure_evidence: tuple[SpecificationClosureEvidence, ...] | None = None,
    open_design_decision_refs: tuple[str, ...] = (),
    blockers: tuple[SpecificationReadinessBlocker, ...] = (),
) -> SpecificationReadinessRequest:
    return SpecificationReadinessRequest(
        project_profile_ref=profile_ref,
        project_profile_version=profile_version,
        specification_ref="spec-adaptive-router-r03",
        specification_revision="rev-0123456789abcdef",
        owner_approval_ref=owner_approval_ref,
        closure_evidence=_closures() if closure_evidence is None else closure_evidence,
        open_design_decision_refs=open_design_decision_refs,
        blockers=blockers,
    )


def _blocker(reason: SpecificationWakeReason, suffix: str = "01") -> SpecificationReadinessBlocker:
    return SpecificationReadinessBlocker(
        reason=reason,
        evidence_ref=f"blocker-evidence-{reason.value.replace('_', '-')}-{suffix}",
    )


def _assignments(
    *,
    supervisor_state: RoleActivityState = RoleActivityState.ACTIVE,
) -> tuple[ModelRoleAssignment, ...]:
    return (
        ModelRoleAssignment(
            project_profile_ref="router-framework-poc",
            role=ModelRole.ARCHITECTURE_OWNER,
            model_ref="model-architecture-owner",
            capability_refs=("cap-architecture-owner",),
            activity_state=RoleActivityState.ACTIVE,
            evidence_refs=("evidence-architecture-owner",),
        ),
        ModelRoleAssignment(
            project_profile_ref="router-framework-poc",
            role=ModelRole.SUPERVISOR_REVIEWER,
            model_ref="model-supervisor-reviewer",
            capability_refs=("cap-supervisor-reviewer",),
            activity_state=supervisor_state,
            evidence_refs=("evidence-supervisor-reviewer",),
        ),
        ModelRoleAssignment(
            project_profile_ref="router-framework-poc",
            role=ModelRole.IMPLEMENTATION_OWNER,
            model_ref="model-implementation-owner",
            capability_refs=("cap-implementation-owner",),
            activity_state=RoleActivityState.ACTIVE,
            evidence_refs=("evidence-implementation-owner",),
        ),
        ModelRoleAssignment(
            project_profile_ref="router-framework-poc",
            role=ModelRole.RESEARCH_HELPER,
            model_ref="model-research-helper",
            capability_refs=("cap-research-helper",),
            activity_state=RoleActivityState.SLEEPING,
            evidence_refs=("evidence-research-helper",),
        ),
    )


def _source_has_attribute(nodes: tuple[ast.AST, ...], owner: str, attribute: str) -> bool:
    return any(
        isinstance(node, ast.Attribute)
        and node.attr == attribute
        and isinstance(node.value, ast.Name)
        and node.value.id == owner
        for node in nodes
    )


def _source_gate(source: str) -> bool:
    tree = ast.parse(source)
    forbidden_modules = ("inspect", "pathlib", "subprocess", "socket", "urllib")
    forbidden_names = {"Any", "Callable", "Optional", "object", "Path"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".", 1)[0] in forbidden_modules for alias in node.names):
                return False
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.module.split(".", 1)[0] in forbidden_modules:
                return False
        if isinstance(node, ast.Name) and node.id in forbidden_names:
            return False
        if isinstance(node, ast.arg) and isinstance(node.annotation, ast.Name):
            if node.annotation.id in forbidden_names:
                return False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "type: ignore" in node.value:
                return False
        if isinstance(node, ast.ExceptHandler):
            if isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
                return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "cast",
                "getattr",
                "hasattr",
                "setattr",
            }:
                return False
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "model_construct",
                "model_copy",
            }:
                return False

    gate_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ModelRoleReadinessGate"
        ),
        None,
    )
    if gate_class is None:
        return False
    assess = next(
        (
            node
            for node in gate_class.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "assess"
        ),
        None,
    )
    if assess is None:
        return False
    nodes = tuple(ast.walk(assess))
    owner_branch = False
    blocker_branch = False
    closure_branch = False
    open_decision_branch = False
    supervisor_branch = False
    for node in nodes:
        if not isinstance(node, ast.If):
            continue
        if (
            isinstance(node.test, ast.Compare)
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.Is)
            and isinstance(node.test.left, ast.Attribute)
            and isinstance(node.test.left.value, ast.Name)
            and node.test.left.value.id == "request"
            and node.test.left.attr == "owner_approval_ref"
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Constant)
            and node.test.comparators[0].value is None
            and _source_has_attribute(tuple(ast.walk(node)), "SpecificationReadinessDecision", "OWNER_APPROVAL_REQUIRED")
        ):
            owner_branch = True
        if (
            isinstance(node.test, ast.Attribute)
            and isinstance(node.test.value, ast.Name)
            and node.test.value.id == "request"
            and node.test.attr == "blockers"
            and _source_has_attribute(tuple(ast.walk(node)), "SpecificationReadinessDecision", "ARCHITECTURE_OWNER_REQUIRED")
        ):
            blocker_branch = True
        if (
            isinstance(node.test, ast.Compare)
            and len(node.test.ops) == 1
            and isinstance(node.test.ops[0], ast.NotEq)
            and isinstance(node.test.left, ast.Name)
            and node.test.left.id == "closure_kinds"
            and len(node.test.comparators) == 1
            and isinstance(node.test.comparators[0], ast.Name)
            and node.test.comparators[0].id == "expected_closure_kinds"
            and _source_has_attribute(tuple(ast.walk(node)), "SpecificationReadinessDecision", "ARCHITECTURE_OWNER_REQUIRED")
            and _source_has_attribute(tuple(ast.walk(node)), "SpecificationWakeReason", "CLOSURE_INCOMPLETE")
        ):
            closure_branch = True
        if (
            isinstance(node.test, ast.Attribute)
            and isinstance(node.test.value, ast.Name)
            and node.test.value.id == "request"
            and node.test.attr == "open_design_decision_refs"
            and _source_has_attribute(tuple(ast.walk(node)), "SpecificationWakeReason", "OPEN_DESIGN_DECISION")
        ):
            open_decision_branch = True
        if any(
            isinstance(candidate, ast.Compare)
            and len(candidate.ops) == 1
            and isinstance(candidate.ops[0], ast.Is)
            and isinstance(candidate.left, ast.Attribute)
            and isinstance(candidate.left.value, ast.Name)
            and candidate.left.value.id == "supervisor"
            and candidate.left.attr == "activity_state"
            and len(candidate.comparators) == 1
            and isinstance(candidate.comparators[0], ast.Attribute)
            and isinstance(candidate.comparators[0].value, ast.Name)
            and candidate.comparators[0].value.id == "RoleActivityState"
            and candidate.comparators[0].attr == "ACTIVE"
            for candidate in ast.walk(node.test)
        ):
            supervisor_branch = True
    return all((owner_branch, blocker_branch, closure_branch, open_decision_branch, supervisor_branch))


class ModelRoleReadinessAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = build_router_poc_profile()

    def test_contracts_round_trip_and_default_profile_has_four_roles(self) -> None:
        self.assertEqual(
            {
                ModelRole.ARCHITECTURE_OWNER,
                ModelRole.SUPERVISOR_REVIEWER,
                ModelRole.IMPLEMENTATION_OWNER,
                ModelRole.RESEARCH_HELPER,
            },
            {assignment.role for assignment in self.profile.model_role_assignments},
        )
        request = _request()
        rebuilt = SpecificationReadinessRequest.model_validate_json(request.model_dump_json())
        self.assertEqual(request, rebuilt)
        assessment = SpecificationReadinessAssessment(
            project_profile_ref=self.profile.profile_id,
            project_profile_version=self.profile.profile_version,
            specification_ref=request.specification_ref,
            specification_revision=request.specification_revision,
            decision=SpecificationReadinessDecision.READY_FOR_SUPERVISION,
            wake_reason=None,
        )
        self.assertEqual(
            assessment,
            SpecificationReadinessAssessment.model_validate_json(assessment.model_dump_json()),
        )

    def test_assignment_and_request_invalid_shapes_fail_closed(self) -> None:
        assignment = self.profile.model_role_assignments[0]
        invalid_assignments = (
            {**assignment.model_dump(), "capability_refs": ()},
            {**assignment.model_dump(), "evidence_refs": ("evidence-architecture-owner",) * 2},
            {
                **assignment.model_dump(),
                "capability_refs": ("shared-ref",),
                "evidence_refs": ("shared-ref",),
            },
        )
        for payload in invalid_assignments:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError):
                    ModelRoleAssignment.model_validate(payload)
        mismatched_profile = self.profile.model_dump()
        mismatched_profile["model_role_assignments"] = tuple(
            assignment.model_dump()
            if assignment.role is not ModelRole.ARCHITECTURE_OWNER
            else {**assignment.model_dump(), "project_profile_ref": "other-profile"}
            for assignment in self.profile.model_role_assignments
        )
        with self.assertRaises(ValidationError):
            type(self.profile).model_validate(mismatched_profile)
        duplicate_role_reference = self.profile.model_dump()
        duplicate_role_reference["model_role_assignments"] = tuple(
            assignment.model_dump()
            if assignment.role is not ModelRole.SUPERVISOR_REVIEWER
            else {
                **assignment.model_dump(),
                "model_ref": self.profile.model_role_assignments[0].model_ref,
            }
            for assignment in self.profile.model_role_assignments
        )
        with self.assertRaises(ValidationError):
            type(self.profile).model_validate(duplicate_role_reference)
        request = _request()
        with self.assertRaises(ValidationError):
            SpecificationReadinessRequest.model_validate(
                {**request.model_dump(), "blockers": (_blocker(_BLOCKER_REASONS[0]),) * 2}
            )
        with self.assertRaises(ValidationError):
            SpecificationReadinessRequest.model_validate(
                {
                    **request.model_dump(),
                    "closure_evidence": request.closure_evidence + (request.closure_evidence[0],),
                }
            )
        with self.assertRaises(ValidationError):
            SpecificationReadinessRequest.model_validate(
                {**request.model_dump(), "specification_ref": "C:/specification"}
            )

    def test_missing_owner_approval_has_precedence_over_every_other_blocker(self) -> None:
        request = _request(
            owner_approval_ref=None,
            closure_evidence=_closures()[:-1],
            open_design_decision_refs=("decision-open-01",),
            blockers=(_blocker(SpecificationWakeReason.ARCHITECTURE_CONFLICT),),
        )
        result = ModelRoleReadinessGate.assess(self.profile, request)
        self.assertEqual(SpecificationReadinessDecision.OWNER_APPROVAL_REQUIRED, result.decision)
        self.assertIsNone(result.wake_reason)

    def test_each_blocker_and_lowest_declaration_order_reason_is_selected(self) -> None:
        for reason in _BLOCKER_REASONS:
            with self.subTest(reason=reason):
                result = ModelRoleReadinessGate.assess(
                    self.profile,
                    _request(blockers=(_blocker(reason),)),
                )
                self.assertEqual(SpecificationReadinessDecision.ARCHITECTURE_OWNER_REQUIRED, result.decision)
                self.assertEqual(reason, result.wake_reason)
        result = ModelRoleReadinessGate.assess(
            self.profile,
            _request(
                blockers=(
                    _blocker(SpecificationWakeReason.MODEL_CAPABILITY_INSUFFICIENT),
                    _blocker(SpecificationWakeReason.SPEC_AMBIGUOUS),
                )
            ),
        )
        self.assertEqual(SpecificationWakeReason.SPEC_AMBIGUOUS, result.wake_reason)

    def test_incomplete_closure_and_open_design_decision_are_ordered(self) -> None:
        for index in range(len(SpecificationClosureKind)):
            evidence = _closures()[:index] + _closures()[index + 1 :]
            with self.subTest(index=index):
                result = ModelRoleReadinessGate.assess(
                    self.profile,
                    _request(closure_evidence=evidence),
                )
                self.assertEqual(SpecificationReadinessDecision.ARCHITECTURE_OWNER_REQUIRED, result.decision)
                self.assertEqual(SpecificationWakeReason.CLOSURE_INCOMPLETE, result.wake_reason)
        result = ModelRoleReadinessGate.assess(
            self.profile,
            _request(open_design_decision_refs=("decision-open-01",)),
        )
        self.assertEqual(SpecificationWakeReason.OPEN_DESIGN_DECISION, result.wake_reason)

    def test_ready_requires_active_supervisor_and_complete_approved_request(self) -> None:
        ready = ModelRoleReadinessGate.assess(self.profile, _request())
        self.assertEqual(SpecificationReadinessDecision.READY_FOR_SUPERVISION, ready.decision)
        self.assertIsNone(ready.wake_reason)
        for state in (RoleActivityState.SLEEPING, RoleActivityState.WAKE_REQUIRED):
            with self.subTest(state=state):
                profile = self.profile.model_validate(
                    {
                        **self.profile.model_dump(),
                        "model_role_assignments": tuple(
                            assignment.model_dump()
                            if assignment.role is not ModelRole.SUPERVISOR_REVIEWER
                            else {**assignment.model_dump(), "activity_state": state}
                            for assignment in self.profile.model_role_assignments
                        ),
                    }
                )
                result = ModelRoleReadinessGate.assess(profile, _request())
                self.assertEqual(SpecificationWakeReason.SUPERVISOR_CAPABILITY_UNAVAILABLE, result.wake_reason)

    def test_profile_binding_and_assessment_shape_are_exact(self) -> None:
        request = _request(profile_ref="other-profile")
        with self.assertRaises(ValueError):
            ModelRoleReadinessGate.assess(self.profile, request)
        with self.assertRaises(ValidationError):
            SpecificationReadinessAssessment(
                project_profile_ref=self.profile.profile_id,
                project_profile_version=self.profile.profile_version,
                specification_ref=request.specification_ref,
                specification_revision=request.specification_revision,
                decision=SpecificationReadinessDecision.READY_FOR_SUPERVISION,
                wake_reason=SpecificationWakeReason.OPEN_DESIGN_DECISION,
            )

    def test_committed_source_gate_and_each_semantic_reversal(self) -> None:
        source = _SOURCE_PATH.read_text(encoding="utf-8")
        self.assertTrue(_source_gate(source))
        mutations = (
            ("owner-approval-precedence", "request.owner_approval_ref is None", "request.owner_approval_ref is not None"),
            ("blocker-wake-bypass", "if request.blockers:", "if False:"),
            ("closure-completeness-bypass", "if closure_kinds != expected_closure_kinds", "if True"),
            ("open-decision-bypass", "if request.open_design_decision_refs:", "if False:"),
            ("supervisor-activity-bypass", "RoleActivityState.ACTIVE", "RoleActivityState.SLEEPING"),
        )
        for label, original, replacement in mutations:
            with self.subTest(label=label):
                self.assertIn(original, source)
                mutated = source.replace(original, replacement, 1)
                self.assertFalse(_source_gate(mutated))

    def test_committed_source_gate_rejects_reviewed_exact_bypasses(self) -> None:
        source = _SOURCE_PATH.read_text(encoding="utf-8")
        reviewed_mutations = (
            (
                "closure-subset-bypass",
                "closure_kinds != expected_closure_kinds",
                "closure_kinds <= expected_closure_kinds",
            ),
            (
                "closure-superset-bypass",
                "closure_kinds != expected_closure_kinds",
                "closure_kinds >= expected_closure_kinds",
            ),
            (
                "supervisor-inverse-bypass",
                "supervisor.activity_state is RoleActivityState.ACTIVE",
                "supervisor.activity_state is not RoleActivityState.ACTIVE",
            ),
            (
                "blocker-compound-bypass",
                "if request.blockers:",
                "if request.blockers and False:",
            ),
        )
        for label, original, replacement in reviewed_mutations:
            with self.subTest(label=label):
                self.assertIn(original, source)
                mutated = source.replace(original, replacement, 1)
                self.assertFalse(_source_gate(mutated))


if __name__ == "__main__":
    unittest.main()
