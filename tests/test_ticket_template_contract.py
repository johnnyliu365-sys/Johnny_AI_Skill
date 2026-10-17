"""Static checks for the reusable ticket template, not dispatch admission.

These checks do not validate existing ticket instances or prove host dispatch
enforcement. They keep the template's authoring slots available for one fixed
frontend scenario and its requirement-change stop condition.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pytest


_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATE_PATH = _ROOT / "modules" / "tickets" / "TEMPLATE.md"

_REQUIRED_SLOTS = {
    "approved_contract_source_revision": "@ `<approved revision>`",
    "approved_expected": "核准 Expected（使用者可觀察結果）",
    "typed_input_output_state_error": "具名輸入 → 輸出／有限狀態與錯誤／nullability / types and ports",
    "dependency_and_status": "直接依賴與狀態：`<dependency reference / readiness status / required evidence>`",
    "normal_failure_boundary_acceptance": "正常／失敗／邊界驗收：`<observable acceptance for each case>`",
    "stop_condition": "if implementation requires a new or unapproved business decision, stop and return CHANGE_DETECTED → REQUIREMENT_CHANGED; do not invent Expected",
    "reviewer": "reviewer：`<independent AI／worktree>`",
    "implementation_return": "- `ImplementationReturn`（typed）：",
    "modify_boundary": "modify =",
    "create_boundary": "create =",
    "delete_boundary": "delete =",
    "forbid_boundary": "forbid = <明確禁止的路徑",
    "requirement_identity_reuse": "需求身分重用：",
}

_FIXED_FRONTEND_SCENARIO: dict[str, tuple[str, str]] = {
    "approved_contract_source_revision": (
        "@ `<approved revision>`",
        "approved specification revision with an exact acceptance criterion",
    ),
    "approved_expected": (
        "核准 Expected（使用者可觀察結果）",
        "the user sees the approved result for a valid input",
    ),
    "typed_input_output_state_error": (
        "具名輸入 → 輸出／有限狀態與錯誤",
        "named input produces a named output with finite loading and failure states",
    ),
    "normal_failure_boundary_acceptance": (
        "正常／失敗／邊界驗收：",
        "normal result, failed dependency, and empty-input boundary are observable",
    ),
    "reviewer": (
        "- reviewer：",
        "a reviewer assigned separately from the implementation owner",
    ),
}


def _assert_template_contract(markdown: str) -> None:
    missing = [
        cell for cell, marker in _REQUIRED_SLOTS.items() if marker not in markdown
    ]
    assert not missing, f"ticket template is missing contract cells: {missing}"


@dataclass(frozen=True)
class MissingDecisionSourceScenario:
    approved_source_available: bool
    requires_new_business_decision: bool
    expected_return: Literal["CHANGE_DETECTED"]


def test_template_slots_support_the_fixed_frontend_scenario() -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")

    _assert_template_contract(markdown)
    for cell, (marker, scenario_value) in _FIXED_FRONTEND_SCENARIO.items():
        assert marker in markdown, f"frontend scenario cell {cell} has no template slot"
        assert scenario_value.strip(), f"frontend scenario cell {cell} has no value"


@pytest.mark.parametrize(
    ("cell", "marker"),
    tuple(_REQUIRED_SLOTS.items()),
    ids=tuple(_REQUIRED_SLOTS),
)
def test_removing_each_named_contract_slot_fails(
    cell: str, marker: str
) -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    assert marker in markdown, f"negative cell {cell} cannot find its mutation target"

    mutated = markdown.replace(marker, "", 1)
    with pytest.raises(AssertionError, match="missing contract cells"):
        _assert_template_contract(mutated)


def test_template_routes_unapproved_business_decision_to_change_detected() -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    scenario = MissingDecisionSourceScenario(
        approved_source_available=False,
        requires_new_business_decision=True,
        expected_return="CHANGE_DETECTED",
    )

    assert not scenario.approved_source_available
    assert scenario.requires_new_business_decision
    assert f"{scenario.expected_return} → REQUIREMENT_CHANGED" in markdown
    assert "不得自行填" in markdown or "do not invent Expected" in markdown
