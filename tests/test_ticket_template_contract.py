"""Static checks for the reusable ticket template, not dispatch admission.

The checks bind a filled frontend example to active template sections. They do
not validate existing ticket instances or prove host dispatch enforcement.
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pytest


_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATE_PATH = _ROOT / "modules" / "tickets" / "TEMPLATE.md"
_SCAFFOLD_TEMPLATE_PATH = _ROOT / "template" / "modules" / "tickets" / "TEMPLATE.md"
_OUTCOME_SECTION = "## 使用者拍板與可觀察結果"
_IMPLEMENTATION_SECTION = "## 實作範圍、依賴與 ticket elements"
_COMPLETION_SECTION = "## 完成回寫"
_BOUNDARY_BLOCK = "johnny-boundary"
_WORKFLOW_PATH = _ROOT / "Workflow.md"
_RETIRED_WORKPROGRESS_BULLET = "- WorkProgress：`PRG-YYYYMMDD-NNN`"
_SOURCE_ROW = "<source-row>"
_REUSE_LABEL = "共用件查重與依賴方向"
_NEW_FILE_LABEL = "新增檔案責任"
_BUDGET_LABEL = "預期增量與原票預算"
_ARTIFACT_LABEL = "驗證產物與源碼內容"
_PRESERVE_LABEL = "保留已核准行為"
_COMPLETION_FIELDS = (
    ("功能", ("精確行為", "核准 AC", "可觀察結果")),
    ("新測試", ("精確測試位置", "反向突變紅→還原綠", "N/A")),
    ("產品拆分", ("產品責任 source → target seam", "候選行為測試位置", "N/A")),
    ("埋點", ("事件／指標", "精確位置", "N/A")),
    ("證據", ("精確產物路徑／引用", "commit 或 digest", "N/A")),
    ("未驗證項", ("NOT_VERIFIED", "原因", "不得填 PASS")),
    ("下一步", ("未解缺口", "具名下一動作", "N/A")),
)

_FRONTEND_SLOT_VALUES = (
    ("@ `<approved revision>`", "@ `revision r1`"),
    ("<completion-feature>", "AC-SEARCH-001: SearchInput(\"maple\") renders the approved SearchResult at SearchRoute"),
    ("<completion-tests>", "tests/test_search_route.py::test_search_history green; mutation red, restored green"),
    ("<completion-split>", "SearchRoute → SearchService; candidate behavior test tests/test_search_route.py::test_search_history"),
    ("<completion-instrumentation>", "search.unavailable at src/search/SearchService.py; asserted by tests/test_search_route.py"),
    ("<completion-evidence>", "doc/evidence/search-7.md@sha256:abc; candidate commit abc123"),
    ("<completion-unverified>", "NOT_VERIFIED: paid API isolation unavailable in local host"),
    ("<completion-next>", "Validate paid API isolation; Root owner records host admission evidence"),
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
    (
        "<可新增的路徑；不寫就是一個都不准新增>",
        "src/search/",
    ),
    (
        "<已查找並重用的生產模組、測試 harness／fixture（精確路徑或 ID、revision 與依賴方向）；若無可重用項，填查找範圍與具體理由>",
        "Reused src/search/SearchService.py@r1 and tests/support/http_fake.py@r2; SearchRoute → SearchService → SearchPort",
    ),
    (
        "<對 johnny-boundary create 所授權的每個程式／腳本檔，逐一列出精確路徑、單一責任、直接消費者、對應驗收 ID、依賴方向；即使 create 使用目錄或 pattern，也不得只列目錄／pattern；沒有新增時填 N/A reason>",
        "src/search/SearchIndex.py: single responsibility, query index; consumer, SearchService; acceptance, AC-SEARCH-002; dependency, SearchService → SearchIndex; src/search/SearchIndexValidation.py: single responsibility, query validation; consumer, SearchIndex; acceptance, AC-SEARCH-003; dependency, SearchIndex → SearchIndexValidation",
    ),
    (
        "<分列既有／新增產品碼、測試／腳本、文件、證據產物的預期數量與估計行數；修正沿用同一票預算；行數或數量只觸發結構審查，不自動拆檔、壓縮、拒收或放行>",
        "Existing/new: product 1/2 files +8/+24 lines; tests/scripts 1/0 +12/0; docs 1/0 +3/0; evidence 1/0 +4/0; correction uses this ticket's remaining budget",
    ),
    (
        "<預設使用 Git worktree 外的作業系統暫存目錄，且不得污染 Git worktree；正式樹中唯一必要且具名的證據產物；源碼／腳本僅保留必要技術註解，不含 owner prompt 或工單敘事>",
        f"Temporary output: {Path(tempfile.gettempdir()).resolve() / 'johnny-ticket-7'} (outside the repository worktree); persist only doc/evidence/search-7.md; code and scripts contain technical comments only, no owner prompt or ticket narrative",
    ),
    (
        "<本票不應改動的既有功能、介面與來源基準；如契約內確需變更，列明授權來源、精確路徑與回歸驗收>",
        "Preserve SearchHistory and public SearchQuery v1 at baseline abc123; any authorized change must cite its source, exact path, and regression case",
    ),
)


_GENERIC_SLOT_OVERRIDES: dict[str, str] = {
    "<completion-feature>": "AC-TEMPLATE-001: the contract checker reports missing required completion fields",
    "<completion-tests>": "tests/test_ticket_template_contract.py::test_mutating_a_named_template_policy_breaks_its_contract_cell green",
    "<completion-split>": "N/A: this fictional change touches only a script and test helper; no product responsibility moves",
    "<completion-instrumentation>": "N/A: the script-only example adds no product event or metric",
    "<completion-evidence>": "tests/test_ticket_template_contract.py@candidate commit abc123",
    "<completion-unverified>": "NOT_VERIFIED: host admission behavior was not exercised by this format-only example",
    "<completion-next>": "Gap: host admission evidence; next action: run the host admission check",
    "<observable result for the named input, bound to the approved source above>": 'For `LookupQuery("birch")`, the result returns matching `LookupEntry` values.',
    "<observable acceptance for each case>": "A valid query returns entries; an unavailable provider returns an error result; an empty query returns the empty result.",
    "<具名輸入 → 輸出／有限狀態與錯誤／nullability / types and ports>": "LookupQuery(term: NonEmptyText) → LookupResult(entries: ImmutableList<LookupEntry>); states Ready / Empty / Unavailable; error LookupUnavailable",
    "<可新增的路徑；不寫就是一個都不准新增>": "src/lookup/",
    "<已查找並重用的生產模組、測試 harness／fixture（精確路徑或 ID、revision 與依賴方向）；若無可重用項，填查找範圍與具體理由>": "Reused src/common/TermNormalizer.py@r1 and tests/support/lookup_fake.py@r2; LookupEndpoint → LookupService → LookupPort",
    "<對 johnny-boundary create 所授權的每個程式／腳本檔，逐一列出精確路徑、單一責任、直接消費者、對應驗收 ID、依賴方向；即使 create 使用目錄或 pattern，也不得只列目錄／pattern；沒有新增時填 N/A reason>": "src/lookup/LookupIndex.py: one responsibility, index entries; consumer LookupService; acceptance AC-LOOKUP-002; dependency LookupService → LookupIndex",
    "<預設使用 Git worktree 外的作業系統暫存目錄，且不得污染 Git worktree；正式樹中唯一必要且具名的證據產物；源碼／腳本僅保留必要技術註解，不含 owner prompt 或工單敘事>": f"Temporary output: {Path(tempfile.gettempdir()).resolve() / 'ticket-example'} (outside the repository worktree); persist only doc/evidence/ticket-example.md; code and scripts contain technical comments only, no owner prompt or ticket narrative",
    "<本票不應改動的既有功能、介面與來源基準；如契約內確需變更，列明授權來源、精確路徑與回歸驗收>": "Preserve the existing public lookup behavior at approved baseline revision 1; authorized changes must cite their source, exact path, and regression case",
}
_GENERIC_SLOT_VALUES = tuple(
    (placeholder, _GENERIC_SLOT_OVERRIDES.get(placeholder, value))
    for placeholder, value in _FRONTEND_SLOT_VALUES
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
    _SlotMutation("reuse_contract_removed", _IMPLEMENTATION_SECTION, _REUSE_LABEL, "delete"),
    _SlotMutation("reuse_contract_commented", _IMPLEMENTATION_SECTION, _REUSE_LABEL, "comment"),
    _SlotMutation("reuse_contract_moved", _IMPLEMENTATION_SECTION, _REUSE_LABEL, "move"),
    _SlotMutation("new_file_responsibility_removed", _IMPLEMENTATION_SECTION, _NEW_FILE_LABEL, "delete"),
    _SlotMutation("new_file_responsibility_commented", _IMPLEMENTATION_SECTION, _NEW_FILE_LABEL, "comment"),
    _SlotMutation("new_file_responsibility_moved", _IMPLEMENTATION_SECTION, _NEW_FILE_LABEL, "move"),
    _SlotMutation("change_budget_removed", _IMPLEMENTATION_SECTION, _BUDGET_LABEL, "delete"),
    _SlotMutation("change_budget_commented", _IMPLEMENTATION_SECTION, _BUDGET_LABEL, "comment"),
    _SlotMutation("change_budget_moved", _IMPLEMENTATION_SECTION, _BUDGET_LABEL, "move"),
    _SlotMutation("artifact_policy_removed", _IMPLEMENTATION_SECTION, _ARTIFACT_LABEL, "delete"),
    _SlotMutation("artifact_policy_commented", _IMPLEMENTATION_SECTION, _ARTIFACT_LABEL, "comment"),
    _SlotMutation("artifact_policy_moved", _IMPLEMENTATION_SECTION, _ARTIFACT_LABEL, "move"),
    _SlotMutation("preserve_contract_removed", _IMPLEMENTATION_SECTION, _PRESERVE_LABEL, "delete"),
    _SlotMutation("preserve_contract_commented", _IMPLEMENTATION_SECTION, _PRESERVE_LABEL, "comment"),
    _SlotMutation("preserve_contract_moved", _IMPLEMENTATION_SECTION, _PRESERVE_LABEL, "move"),
    *(
        _SlotMutation(f"completion_{label}_removed", _COMPLETION_SECTION, label, "delete")
        for label, _ in _COMPLETION_FIELDS
    ),
)

_SCAFFOLD_NEGATIVE_CELLS = (
    _SlotMutation("scaffold_expected_removed", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "delete"),
    _SlotMutation("scaffold_expected_moved", _OUTCOME_SECTION, "核准 Expected（使用者可觀察結果）", "move"),
    _SlotMutation("scaffold_stop_condition_removed", _OUTCOME_SECTION, "停止條件", "delete"),
    _SlotMutation("scaffold_stop_condition_moved", _OUTCOME_SECTION, "停止條件", "move"),
    _SlotMutation("scaffold_reuse_removed", _IMPLEMENTATION_SECTION, _REUSE_LABEL, "delete"),
    _SlotMutation("scaffold_reuse_moved", _IMPLEMENTATION_SECTION, _REUSE_LABEL, "move"),
    _SlotMutation("scaffold_new_file_responsibility_removed", _IMPLEMENTATION_SECTION, _NEW_FILE_LABEL, "delete"),
    _SlotMutation("scaffold_new_file_responsibility_moved", _IMPLEMENTATION_SECTION, _NEW_FILE_LABEL, "move"),
    *(
        _SlotMutation(f"scaffold_completion_{label}_removed", _COMPLETION_SECTION, label, "delete")
        for label, _ in _COMPLETION_FIELDS
    ),
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
    reuse = _active_bullet(implementation, _REUSE_LABEL)
    new_file = _active_bullet(implementation, _NEW_FILE_LABEL)
    budget = _active_bullet(implementation, _BUDGET_LABEL)
    artifact = _active_bullet(implementation, _ARTIFACT_LABEL)
    preserve = _active_bullet(implementation, _PRESERVE_LABEL)
    assert "具名輸入 → 輸出／有限狀態與錯誤" in contract
    assert "readiness status" in dependency and "required evidence" in dependency
    assert "independent AI／worktree" in reviewer
    assert "不得與 implementation owner 共用 worktree" in reviewer
    assert "測試 harness／fixture" in reuse and "依賴方向" in reuse
    assert all(term in new_file for term in ("每個程式／腳本檔", "精確路徑", "單一責任", "直接消費者", "驗收 ID"))
    assert "即使 create 使用目錄或 pattern" in new_file
    assert all(term in budget for term in ("既有／新增產品碼", "測試／腳本", "文件", "證據產物"))
    assert "修正沿用同一票預算" in budget and "不自動拆檔" in budget
    assert all(term in artifact for term in ("作業系統暫存目錄", "Git worktree 外", "不得污染 Git worktree", "正式樹", "owner prompt", "工單敘事"))
    assert all(term in preserve for term in ("既有功能、介面", "授權來源", "回歸驗收"))
    assert all(
        item in returned
        for item in ("COMPLETED → ACTION_COMPLETED", "BLOCKED → HALT", "CHANGE_DETECTED → REQUIREMENT_CHANGED")
    )

    completion = _section(active, _COMPLETION_SECTION)
    actual_files = _active_bullet(completion, "實際檔案")
    commit = _active_bullet(completion, "commit")
    assert "<paths>" in actual_files
    assert "<SHA>" in commit
    for label, requirements in _COMPLETION_FIELDS:
        field = _active_bullet(completion, label)
        assert all(requirement in field for requirement in requirements), (
            f"completion field {label!r} is missing its required reporting contract"
        )
    assert not re.search(r"WorkProgress|PRG-YYYYMMDD-NNN", completion), (
        "retired WorkProgress output must not be active in the completion section"
    )

    workflow_policy = " ".join(_WORKFLOW_PATH.read_text(encoding="utf-8").split())
    assert "`WorkProgressReport.md`" in workflow_policy
    assert "return target" in workflow_policy
    assert "typed event" in workflow_policy
    assert "exact commit" in workflow_policy
    assert "artifact identifiers" in workflow_policy

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


def _fill_ticket(template: str, slot_values: tuple[tuple[str, str], ...]) -> str:
    filled = template
    for placeholder, value in slot_values:
        assert filled.count(placeholder) == 1, (
            f"expected one fillable template slot for {placeholder!r}"
        )
        filled = filled.replace(placeholder, value, 1)
    return filled


def _fill_frontend_ticket(template: str) -> str:
    return _fill_ticket(template, _FRONTEND_SLOT_VALUES)


def _fill_generic_ticket(template: str) -> str:
    return _fill_ticket(template, _GENERIC_SLOT_VALUES)


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
    ticket_completion = _section(filled_ticket, _COMPLETION_SECTION)

    expected_revision = "| 對應規格 ID |"
    expected_label = "核准 Expected（使用者可觀察結果）"
    contract_label = "公開契約／資料模型"
    acceptance_label = "正常／失敗／邊界驗收"
    stop_label = "停止條件"
    reviewer_label = "reviewer"
    reuse_label = _REUSE_LABEL
    new_file_label = _NEW_FILE_LABEL
    budget_label = _BUDGET_LABEL
    artifact_label = _ARTIFACT_LABEL
    preserve_label = _PRESERVE_LABEL
    revision_rows = [
        line for line in filled_ticket.splitlines() if line.startswith(expected_revision)
    ]
    assert len(revision_rows) == 1 and "revision r1" in revision_rows[0]

    expected = _filled_value(ticket_outcome, expected_label)
    contract = _filled_value(ticket_implementation, contract_label)
    acceptance = _filled_value(ticket_outcome, acceptance_label)
    stop = _filled_value(ticket_outcome, stop_label)
    reviewer = _filled_value(ticket_implementation, reviewer_label)
    reuse = _filled_value(ticket_implementation, reuse_label)
    new_file = _filled_value(ticket_implementation, new_file_label)
    budget = _filled_value(ticket_implementation, budget_label)
    artifact = _filled_value(ticket_implementation, artifact_label)
    preserve = _filled_value(ticket_implementation, preserve_label)
    split = _active_bullet(ticket_completion, "產品拆分")
    assert "SearchResult" in expected
    assert all(
        item in contract
        for item in ("SearchInput", "SearchResult", "Loading", "Empty", "Failure", "SearchUnavailable")
    )
    assert all(case in acceptance for case in ("valid query", "unavailable service", "empty query"))
    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in stop
    assert "do not invent Expected" in stop
    assert "independent from implementation owner" in reviewer
    assert all(item in reuse for item in ("SearchService.py@r1", "http_fake.py@r2", "SearchRoute → SearchService"))
    assert all(item in new_file for item in (
        "src/search/SearchIndex.py",
        "src/search/SearchIndexValidation.py",
        "SearchService",
        "AC-SEARCH-002",
        "AC-SEARCH-003",
    ))
    assert "create = src/search/" in _boundary_body(filled_ticket)
    assert all(item in budget for item in ("product 1/2", "tests/scripts 1/0", "this ticket's remaining budget"))
    assert new_file.count("src/search/") == 2
    temp_path_text = (
        artifact.partition("; persist only")[0]
        .strip("`")
        .removeprefix("Temporary output: ")
        .split(" (outside", 1)[0]
    )
    temp_path = Path(temp_path_text).resolve()
    assert not temp_path.is_relative_to(_ROOT.resolve())
    assert "doc/evidence/search-7.md" in artifact
    assert "no owner prompt or ticket narrative" in artifact
    assert "Preserve SearchHistory" in preserve and "public SearchQuery v1" in preserve
    assert "SearchRoute → SearchService" in split
    assert "candidate behavior test tests/test_search_route.py::test_search_history" in split
    assert "tests/test_search_route.py::test_search_history green" in _active_bullet(ticket_completion, "新測試")


def test_scaffold_template_slots_bind_to_a_filled_example_ticket() -> None:
    template = _SCAFFOLD_TEMPLATE_PATH.read_text(encoding="utf-8")
    _assert_template_contract(template)
    filled_ticket = _fill_generic_ticket(template)

    outcome = _section(filled_ticket, _OUTCOME_SECTION)
    implementation = _section(filled_ticket, _IMPLEMENTATION_SECTION)
    assert "LookupEntry" in _filled_value(outcome, "核准 Expected（使用者可觀察結果）")
    assert all(
        case in _filled_value(outcome, "正常／失敗／邊界驗收")
        for case in ("valid query", "unavailable provider", "empty query")
    )
    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in _filled_value(outcome, "停止條件")
    assert "TermNormalizer.py@r1" in _filled_value(implementation, _REUSE_LABEL)
    assert "src/lookup/LookupIndex.py" in _filled_value(implementation, _NEW_FILE_LABEL)
    assert "create = src/lookup/" in _boundary_body(filled_ticket)

    completion = _section(filled_ticket, _COMPLETION_SECTION)
    assert "N/A: this fictional change touches only a script and test helper" in _active_bullet(completion, "產品拆分")
    assert "NOT_VERIFIED: host admission behavior was not exercised" in _active_bullet(completion, "未驗證項")
    assert "Gap: host admission evidence; next action: run the host admission check" in _active_bullet(completion, "下一步")

    assert "library/" not in template
    assert "模板本身不執行或攔截寫入" in template
    assert "由 host/reviewer admission" in template
    assert "不要求安裝協作插件或其 runtime" in template


@pytest.mark.parametrize(
    "mutation",
    _NEGATIVE_CELLS,
    ids=tuple(mutation.cell for mutation in _NEGATIVE_CELLS),
)
def test_mutating_a_named_template_policy_breaks_its_contract_cell(
    mutation: _SlotMutation,
) -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    _assert_template_contract(markdown)
    mutated = _apply_bullet_mutation(markdown, mutation)

    with pytest.raises(AssertionError):
        _assert_template_contract(mutated)

    # The mutation is in-memory only; the exact source is still present and green.
    restored = _TEMPLATE_PATH.read_text(encoding="utf-8")
    assert restored == markdown
    _assert_template_contract(restored)


@pytest.mark.parametrize(
    "mutation",
    _SCAFFOLD_NEGATIVE_CELLS,
    ids=tuple(mutation.cell for mutation in _SCAFFOLD_NEGATIVE_CELLS),
)
def test_scaffold_reverse_mutations_break_and_restore_the_contract_cell(
    mutation: _SlotMutation,
) -> None:
    markdown = _SCAFFOLD_TEMPLATE_PATH.read_text(encoding="utf-8")
    _assert_template_contract(markdown)
    mutated = _apply_bullet_mutation(markdown, mutation)

    with pytest.raises(AssertionError):
        _assert_template_contract(mutated)

    restored = _SCAFFOLD_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert restored == markdown
    _assert_template_contract(restored)


@pytest.mark.parametrize(
    "template_path",
    (_TEMPLATE_PATH, _SCAFFOLD_TEMPLATE_PATH),
    ids=("ticket_template", "scaffold_template"),
)
def test_returned_retired_workprogress_bullet_breaks_and_restores_contract(
    template_path: Path,
) -> None:
    markdown = template_path.read_text(encoding="utf-8")
    _assert_template_contract(markdown)

    completion = _section(markdown, _COMPLETION_SECTION)
    commit = _active_bullet(completion, "commit")
    mutated = markdown.replace(
        commit,
        f"{commit}\n{_RETIRED_WORKPROGRESS_BULLET}",
        1,
    )
    with pytest.raises(AssertionError, match="retired WorkProgress output"):
        _assert_template_contract(mutated)

    restored = template_path.read_text(encoding="utf-8")
    assert restored == markdown
    _assert_template_contract(restored)


def test_unapproved_business_decision_uses_the_active_stop_bullet() -> None:
    markdown = _TEMPLATE_PATH.read_text(encoding="utf-8")
    outcome = _section(markdown, _OUTCOME_SECTION)
    stop = _active_bullet(outcome, "停止條件")

    assert "CHANGE_DETECTED → REQUIREMENT_CHANGED" in stop
    assert "do not invent Expected" in stop
