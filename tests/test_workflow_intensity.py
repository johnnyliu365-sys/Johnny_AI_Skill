"""Adaptive workflow-intensity derivation tests (CHG-20260818-028)."""

from __future__ import annotations

import unittest
import warnings

from pydantic import ValidationError

from library.workflow_router.contracts import (
    ChangeSurface,
    ExternalEffectSurface,
    IntakeMode,
    NormalizedGoal,
    ProductKind,
    RecoveryDifficulty,
    SecuritySurface,
    UncertaintyLevel,
    WorkflowIntensity,
    WorkloadAssessment,
    derive_workflow_intensity,
)

_CLEAN = {
    "change_surface": ChangeSurface.SINGLE_FILE,
    "uncertainty": UncertaintyLevel.ESTABLISHED_PATTERN,
    "recovery": RecoveryDifficulty.REVERSIBLE,
    "security_surface": SecuritySurface.NONE,
    "external_effects": ExternalEffectSurface.NONE,
}


def _assessment(**overrides: object) -> WorkloadAssessment:
    payload: dict[str, object] = dict(_CLEAN)
    payload.update(overrides)
    payload.setdefault("evidence_refs", ("evidence-intake-001",))
    return WorkloadAssessment.model_validate(payload)


class WorkflowIntensityDerivationTests(unittest.TestCase):
    """Intensity is a deterministic maximum over evidence-backed signal floors."""

    def test_fully_clean_assessment_is_the_only_compact_shape(self) -> None:
        self.assertIs(
            derive_workflow_intensity(_assessment()), WorkflowIntensity.COMPACT
        )
        self.assertIs(
            derive_workflow_intensity(
                _assessment(change_surface=ChangeSurface.SINGLE_COMPONENT)
            ),
            WorkflowIntensity.COMPACT,
        )

    def test_every_signal_floor_is_exact(self) -> None:
        cases: tuple[tuple[str, object, WorkflowIntensity], ...] = (
            (
                "change_surface",
                ChangeSurface.MULTI_COMPONENT,
                WorkflowIntensity.STANDARD,
            ),
            (
                "change_surface",
                ChangeSurface.CROSS_BOUNDARY,
                WorkflowIntensity.HIGH_ASSURANCE,
            ),
            ("uncertainty", UncertaintyLevel.KNOWN_DOMAIN, WorkflowIntensity.STANDARD),
            ("uncertainty", UncertaintyLevel.NOVEL, WorkflowIntensity.HIGH_ASSURANCE),
            ("recovery", RecoveryDifficulty.RECOVERABLE, WorkflowIntensity.STANDARD),
            (
                "recovery",
                RecoveryDifficulty.IRREVERSIBLE,
                WorkflowIntensity.HIGH_ASSURANCE,
            ),
            (
                "security_surface",
                SecuritySurface.UNTRUSTED_INPUT,
                WorkflowIntensity.STANDARD,
            ),
            (
                "security_surface",
                SecuritySurface.PRIVILEGED,
                WorkflowIntensity.HIGH_ASSURANCE,
            ),
            (
                "external_effects",
                ExternalEffectSurface.LOCAL_HOST,
                WorkflowIntensity.STANDARD,
            ),
            (
                "external_effects",
                ExternalEffectSurface.NETWORK_OR_RELEASE,
                WorkflowIntensity.HIGH_ASSURANCE,
            ),
        )
        for field, value, expected in cases:
            with self.subTest(signal=f"{field}={getattr(value, 'value', value)}"):
                self.assertIs(
                    derive_workflow_intensity(_assessment(**{field: value})),
                    expected,
                )

    def test_highest_floor_wins_over_any_clean_mix(self) -> None:
        mixed = _assessment(
            uncertainty=UncertaintyLevel.KNOWN_DOMAIN,
            security_surface=SecuritySurface.PRIVILEGED,
        )
        self.assertIs(
            derive_workflow_intensity(mixed), WorkflowIntensity.HIGH_ASSURANCE
        )

    def test_assessment_requires_committed_evidence(self) -> None:
        with self.assertRaises(ValidationError):
            WorkloadAssessment.model_validate(dict(_CLEAN) | {"evidence_refs": ()})

    def test_forged_assessment_cannot_derive_an_intensity(self) -> None:
        forged = WorkloadAssessment.model_construct(
            change_surface="tiny",
            uncertainty=UncertaintyLevel.ESTABLISHED_PATTERN,
            recovery=RecoveryDifficulty.REVERSIBLE,
            security_surface=SecuritySurface.NONE,
            external_effects=ExternalEffectSurface.NONE,
            evidence_refs=("evidence-intake-001",),
        )
        with warnings.catch_warnings():
            # The forged value warns during the pre-validation dump; the
            # rejection below is the behavior under test.
            warnings.simplefilter("ignore", UserWarning)
            with self.assertRaises(ValidationError):
                derive_workflow_intensity(forged)

    def test_normalized_goal_carries_an_optional_assessment(self) -> None:
        goal = NormalizedGoal(
            intake_mode=IntakeMode.GREENFIELD,
            product_kind=ProductKind.CLI,
            goal_statement="Ship one bounded fix.",
            workload=_assessment(),
        )
        assert goal.workload is not None
        self.assertIs(
            derive_workflow_intensity(goal.workload), WorkflowIntensity.COMPACT
        )
        bare = NormalizedGoal(
            intake_mode=IntakeMode.GREENFIELD,
            product_kind=ProductKind.CLI,
            goal_statement="Ship one bounded fix.",
        )
        self.assertIsNone(bare.workload)


if __name__ == "__main__":
    unittest.main()
