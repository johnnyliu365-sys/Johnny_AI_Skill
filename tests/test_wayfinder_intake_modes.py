"""NormalizedGoal intake-mode contract tests (CHG-20260818-027)."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from library.workflow_router.contracts import (
    IntakeMode,
    NormalizedGoal,
    ProductKind,
)

_BASELINE = "private-target-repo@8aee42f662a652115c28a6d08d26c617f45a63e0"


def _goal(
    intake_mode: IntakeMode,
    *,
    product_kind: ProductKind = ProductKind.SERVICE,
    baseline_reference: str | None = None,
    delta_scope: tuple[str, ...] = (),
) -> NormalizedGoal:
    return NormalizedGoal(
        intake_mode=intake_mode,
        product_kind=product_kind,
        goal_statement="Add one governed dispatch capability to the target.",
        baseline_reference=baseline_reference,
        delta_scope=delta_scope,
    )


class NormalizedGoalTests(unittest.TestCase):
    """The intake contract makes each mode's required bindings untypable to skip."""

    def test_each_mode_constructs_with_its_exact_shape(self) -> None:
        greenfield = _goal(IntakeMode.GREENFIELD, product_kind=ProductKind.USER_FACING)
        self.assertIsNone(greenfield.baseline_reference)
        takeover = _goal(IntakeMode.TAKEOVER, baseline_reference=_BASELINE)
        self.assertEqual(takeover.baseline_reference, _BASELINE)
        delta = _goal(
            IntakeMode.DELTA,
            baseline_reference=_BASELINE,
            delta_scope=("dispatch-notification-slice",),
        )
        self.assertEqual(delta.delta_scope, ("dispatch-notification-slice",))

    def test_mode_bindings_are_exact(self) -> None:
        with self.subTest(case="greenfield_rejects_baseline"):
            with self.assertRaises(ValidationError):
                _goal(IntakeMode.GREENFIELD, baseline_reference=_BASELINE)
        with self.subTest(case="greenfield_rejects_delta_scope"):
            with self.assertRaises(ValidationError):
                _goal(IntakeMode.GREENFIELD, delta_scope=("slice-a",))
        with self.subTest(case="takeover_requires_baseline"):
            with self.assertRaises(ValidationError):
                _goal(IntakeMode.TAKEOVER)
        with self.subTest(case="takeover_rejects_delta_scope"):
            with self.assertRaises(ValidationError):
                _goal(
                    IntakeMode.TAKEOVER,
                    baseline_reference=_BASELINE,
                    delta_scope=("slice-a",),
                )
        with self.subTest(case="delta_requires_scope"):
            with self.assertRaises(ValidationError):
                _goal(IntakeMode.DELTA, baseline_reference=_BASELINE)
        with self.subTest(case="delta_requires_baseline"):
            with self.assertRaises(ValidationError):
                _goal(IntakeMode.DELTA, delta_scope=("slice-a",))

    def test_baseline_reference_refuses_paths_and_uris(self) -> None:
        for forged in (
            "C:/Users/someone/repo",
            "https://github.com/org/repo.git",
            "..\\..\\escape",
            "repo with spaces@" + "a" * 40,
            "repo-without-commit",
        ):
            with self.subTest(baseline=forged):
                with self.assertRaises(ValidationError):
                    _goal(IntakeMode.TAKEOVER, baseline_reference=forged)

    def test_foreign_mode_and_kind_are_untypable(self) -> None:
        payload = _goal(
            IntakeMode.TAKEOVER, baseline_reference=_BASELINE
        ).model_dump()
        with self.subTest(field="intake_mode"):
            with self.assertRaises(ValidationError):
                NormalizedGoal.model_validate(payload | {"intake_mode": "vibes"})
        with self.subTest(field="product_kind"):
            with self.assertRaises(ValidationError):
                NormalizedGoal.model_validate(payload | {"product_kind": "metaverse"})


if __name__ == "__main__":
    unittest.main()
