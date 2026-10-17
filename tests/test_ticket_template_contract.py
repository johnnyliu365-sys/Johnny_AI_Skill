"""Static checks for the reusable ticket template, not dispatch admission.

The checks bind a filled frontend example to active template sections. They do
not validate existing ticket instances or prove host dispatch enforcement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pytest


_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATE_PATH = _ROOT / "modules" / "tickets" / "TEMPLATE.md"
_OUTCOME_SECTION = "## 使用者拍板與可觀察結果"
_IMPLEMENTATION_SECTION = "## 實作範圍、依賴與 ticket elements"
_BOUNDARY_BLOCK = "johnny-boundary"
_SOURCE_ROW = "<source-row>"

_FRONTEND_SLOT_VALUES = (
    ("@ `<approved revision>`", "@ `revision r1`"),
    (
        "<observable result for the named input, bound to the approved source above>",
        'For `SearchInput("maple")`, the view renders the approved `SearchResult`.',
    ),
    (
        "<observable acceptance for each case>",
        "A valid query renders results; an unavailable service renders failure; an empty query renders the empty state.",
    ),
    (
        "<if implementation requires a new or unapproved business decision, stop and return CHANGE_DETECTED → REQUIREMENT_CHANGED; do not invent Expected>",
        "If an additional business decision lacks an approved source, stop and return CHANGE_DETECTED → REQUIREMENT_CHANGED; do not invent Expected.",
    ),
    (
        "<independent AI／worktree>",
        "ReviewSeat / review worktree; independent from implementation owner",
    ),
    (
        "<具名輸入 → 輸出／有限狀態與錯誤／nullability / types and ports>",
        "SearchInput(query: NonEmptyText) → SearchResult(items: ReadonlyArray<SearchItem>); states Loading / Empty / Failure; error SearchUnavailable",
    ),
)


@dataclass(frozen=True)
class _SlotMutation:
    cell: str
    section: str
    label: str
    action: Literal["delete", "comment", "fence", "indent", "move"]


_NEGATIVE_CELLS = (
    _SlotMutation("approved_revision_removed", _SOURCE_ROW, "@ `<approved revision>`", "delete"),
    _SlotMutation("expected_removed", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "delete"),
    _SlotMutation("expected_commented_out", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "comment"),
    _SlotMutation("expected_fenced_example", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "fence"),
    _SlotMutation("expected_indented_code", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "indent"),
    _SlotMutation("expected_moved_out_of_section", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "move"),
    _SlotMutation("acceptance_removed", _OUTCOME_SECTION, "正常／失敗／邊界驗收", "delete"),
    _SlotMutation("stop_condition_removed", _OUTCOME_SECTION, "停止條件", "delete"),
    _SlotMutation("stop_condition_commented_out", _OUTCOME_SECTION, "停止條件", "comment"),
    _SlotMutation("requirement_identity_reuse_removed", _OUTCOME_SECTION, "需求身分重用", "delete"),
    _SlotMutation("typed_contract_removed", _IMPLEMENTATION_SECTION, "公開契約／資料模型", "delete"),
    _SlotMutation("dependency_readiness_removed", _IMPLEMENTATION_SECTION, "直接依賴與狀態", "delete"),
    _SlotMutation("reviewer_removed", _IMPLEMENTATION_SECTION, "reviewer", "delete"),
    _SlotMutation("implementation_return_removed", _IMPLEMENTATION_SECTION, "`ImplementationReturn`", "delete"),
    _SlotMutation("modify_boundary_removed", _BOUNDARY_BLOCK, "modify", "delete"),
    _SlotMutation("create_boundary_removed", _BOUNDARY_BLOCK, "create", "delete"),
    _SlotMutation("delete_boundary_removed", _BOUNDARY_BLOCK, "delete", "delete"),
    _SlotMutation("forbid_boundary_removed", _BOUNDARY_BLOCK, "forbid", "delete"),
)


def _without_html_comments(markdown: str) -> str:
    return re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)


def _without_fenced_code(markdown: str) -> str:
    visible: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in markdown.splitlines():
        marker = re.match(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_character is None:
            if marker is None:
                visible.append(line)
            else:
                fence = marker.group(1)
                fence_character = fence[0]
                fence_length = len(fence)
            continue

        closing = re.match(r"^[ ]{0,3}(`+|~+)[ \t]*$", line)
        if (
            closing is not None
            and closing.group(1)[0] == fence_character
            and len(closing.group(1)) >= fence_length
        ):
            fence_character = None
            fence_length = 0
    return "\n".join(visible)


def _section(markdown: str, heading: str) -> str:
    visible = _without_fenced_code(_without_html_comments(markdown))
    lines = visible.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line.strip() == heading),
        None,
    )
    assert start is not None, f"missing active section: {heading}"
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("## ")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end])


def _active_bullet(section: str, label: str) -> str:
    matching = [
        line
        for line in section.splitlines()
        if line.startswith("- ") and line[2:].startswith(label)
    ]
    assert len(matching) == 1, f"expected one active bullet for {label!r}, got {matching}"
    return matching[0]


def _boundary_body(markdown: str) -> str:
    match = re.search(
        rf"(?ms)^```{re.escape(_BOUNDARY_BLOCK)}\s*\n(.*?)^```\s*$",
        _without_html_comments(markdown),
    )
    assert match is not None, "missing active johnny-boundary block"
    return match.group(1)


def _assert_template_contract(markdown: str) -> None:
    active = _without_fenced_code(_without_html_comments(markdown))
    source_rows = [
        line for line in active.splitlines() if line.startswith("| 對應規格 ID |")
    ]
    assert len(source_rows) == 1 and "<approved revision>" in source_rows[0], (
        "ticket template needs one approved SPEC source and revision row"
    )
    assert "§x" in source_rows[0] and "AC-y" in source_rows[0]

    outcome = _section(active, _OUTCOME_SECTION)
    expected = _active_bullet(outcome, "核准 Expected（使用者可觀察結果）")
    acceptance = _active_bullet(outcome, "正常／失敗／邊界驗收")
    stop = _active_bullet(outcome, "停止條件")
    identity = _active_bullet(outcome, "需求身分重用")
    assert "observable result" in expected and "approved source above" in expected
    assert "observable acceptance for each case" in acceptance
    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in stop
    assert "do not invent Expected" in stop
    assert "不自行建立第二份 PRD" in identity
    assert "Requirement Change" in identity and "不得核准自身變更" in identity

    implementation = _section(active, _IMPLEMENTATION_SECTION)
    contract = _active_bullet(implementation, "公開契約／資料模型")
    dependency = _active_bullet(implementation, "直接依賴與狀態")
    reviewer = _active_bullet(implementation, "reviewer")
    returned = _active_bullet(implementation, "`ImplementationReturn`")
    assert "具名輸入 → 輸出／有限狀態與錯誤" in contract
    assert "readiness status" in dependency and "required evidence" in dependency
    assert "independent AI／worktree" in reviewer
    assert "不得與 implementation owner 共用 worktree" in reviewer
    assert all(
        item in returned
        for item in ("COMPLETED → ACTION_COMPLETED", "BLOCKED → HALT", "CHANGE_DETECTED → REQUIREMENT_CHANGED")
    )

    boundary = _boundary_body(markdown)
    for action in ("modify", "create", "delete", "forbid"):
        assert re.search(rf"(?m)^{action}\s*=", boundary), (
            f"missing {action} declaration in johnny-boundary"
        )


def _apply_bullet_mutation(markdown: str, mutation: _SlotMutation) -> str:
    if mutation.section == _SOURCE_ROW:
        target = mutation.label
    elif mutation.section == _BOUNDARY_BLOCK:
        boundary = _boundary_body(markdown)
        line = next(
            line
            for line in boundary.splitlines()
            if line.startswith(f"{mutation.label} =")
        )
        target = line
    else:
        target = _active_bullet(_section(markdown, mutation.section), mutation.label)
    if mutation.action == "delete":
        replacement = ""
    elif mutation.action == "comment":
        replacement = f"<!-- {target} -->"
    elif mutation.action == "fence":
        replacement = f"```markdown\n{target}\n```"
    elif mutation.action == "indent":
        replacement = f"    {target}"
    else:
        return markdown.replace(target, "", 1) + f"\n{target}\n"
    return markdown.replace(target, replacement, 1)


def _fill_frontend_ticket(template: str) -> str:
    filled = template
    for placeholder, value in _FRONTEND_SLOT_VALUES:
        assert filled.count(placeholder) == 1, (
            f"expected one fillable template slot for {placeholder!r}"
        )
        filled = filled.replace(placeholder, value, 1)
    return filled


def _filled_value(section: str, label: str) -> str:
    bullet = _active_bullet(section, label)
    _, separator, value = bullet.partition("：")
    assert separator and value.strip(), f"filled ticket has no value for {label!r}"
    assert not value.strip().startswith("<"), f"filled ticket left {label!r} as a placeholder"
    return value.strip()


def test_template_slots_bind_to_a_filled_frontend_ticket() -> None:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    _assert_template_contract(template)
    filled_ticket = _fill_frontend_ticket(template)

    ticket_outcome = _section(filled_ticket, _OUTCOME_SECTION)
    ticket_implementation = _section(filled_ticket, _IMPLEMENTATION_SECTION)

    expected_revision = "| 對應規格 ID |"
    expected_label = "核准 Expected（使用者可觀察結果）"
    contract_label = "公開契約／資料模型"
    acceptance_label = "正常／失敗／邊界驗收"
    stop_label = "停止條件"
    reviewer_label = "reviewer"
    revision_rows = [
        line for line in filled_ticket.splitlines() if line.startswith(expected_revision)
    ]
    assert len(revision_rows) == 1 and "revision r1" in revision_rows[0]

    expected = _filled_value(ticket_outcome, expected_label)
    contract = _filled_value(ticket_implementation, contract_label)
    acceptance = _filled_value(ticket_outcome, acceptance_label)
    stop = _filled_value(ticket_outcome, stop_label)
    reviewer = _filled_value(ticket_implementation, reviewer_label)
    assert "SearchResult" in expected
    assert all(
        item in contract
        for item in ("SearchInput", "SearchResult", "Loading", "Empty", "Failure", "SearchUnavailable")
    )
    assert all(case in acceptance for case in ("valid query", "unavailable service", "empty query"))
    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in stop
    assert "do not invent Expected" in stop
    assert "independent from implementation owner" in reviewer


@pytest.mark.parametrize(
    "mutation",
    _NEGATIVE_CELLS,
    ids=tuple(mutation.cell for mutation in _NEGATIVE_CELLS),
)
def test_removing_or_commenting_a_named_slot_breaks_the_template(
    mutation: _SlotMutation,
) -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    mutated = _apply_bullet_mutation(markdown, mutation)

    with pytest.raises(AssertionError):
        _assert_template_contract(mutated)


def test_unapproved_business_decision_uses_the_active_stop_bullet() -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    outcome = _section(markdown, _OUTCOME_SECTION)
    stop = _active_bullet(outcome, "停止條件")

    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in stop
    assert "do not invent Expected" in stop
