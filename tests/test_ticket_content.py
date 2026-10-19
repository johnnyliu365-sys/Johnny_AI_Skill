from __future__ import annotations

import pytest
from pydantic import ValidationError

from library.local_orchestration.ticket_content import (
    TicketContentField,
    TicketContentIssue,
    TicketContentReason,
    inspect_ticket_content,
)


_OUTCOME = "## 使用者拍板與可觀察結果"
_IMPLEMENTATION = "## 實作範圍、依賴與 ticket elements"
_EXPECTED_LINE = "- 核准 Expected（使用者可觀察結果）：For Input(\"ok\"), view shows Result<Item>."
_BOUNDARY = "```johnny-boundary\nmodify = library/local_orchestration/ticket_content.py\ncreate = src/new.py\nforbid = doc/\n```"
_TICKET = f"""# Fictional ticket

{_OUTCOME}

{_EXPECTED_LINE}
- 正常／失敗／邊界驗收：valid input returns entries; invalid input yields an error.
- 停止條件：Stop when approval is missing and return a change request.

{_IMPLEMENTATION}

### Nested heading does not close the section
- implementation owner：AuthorSeat
- reviewer：ReviewSeat
- 公開契約／資料模型：Input<Item> -> Result<Item, Error>; states Ready / Failure.
- 直接依賴與狀態：local parser revision 1 is ready; no external effect.
- 新增檔案責任：src/new.py: parser; consumer local; acceptance AC1.

{_BOUNDARY}
"""
_FIELDS = (
    (TicketContentField.EXPECTED, "核准 Expected（使用者可觀察結果）"),
    (TicketContentField.ACCEPTANCE, "正常／失敗／邊界驗收"),
    (TicketContentField.STOP, "停止條件"),
    (TicketContentField.IMPLEMENTER, "implementation owner"),
    (TicketContentField.REVIEWER, "reviewer"),
    (TicketContentField.CONTRACT, "公開契約／資料模型"),
    (TicketContentField.DEPENDENCIES, "直接依賴與狀態"),
    (TicketContentField.NEW_FILES, "新增檔案責任"),
)


def test_issue_constructor_is_strict_and_frozen() -> None:
    issue = TicketContentIssue(
        field=TicketContentField.EXPECTED,
        reason=TicketContentReason.MISSING,
    )
    assert issue.field is TicketContentField.EXPECTED
    with pytest.raises(ValidationError):
        issue.reason = TicketContentReason.PLACEHOLDER
    with pytest.raises(ValidationError):
        TicketContentIssue(field="EXPECTED", reason=TicketContentReason.MISSING)
    with pytest.raises(ValidationError):
        TicketContentIssue(field=TicketContentField.EXPECTED, reason="MISSING")
    with pytest.raises(ValidationError):
        TicketContentIssue(field="UNKNOWN", reason=TicketContentReason.MISSING)


@pytest.mark.parametrize(
    "payload",
    (None, "ticket", bytearray(b"ticket"), b"", b"\xff", b"x" * 131073),
    ids=("none", "string", "bytearray", "empty", "invalid_utf8", "oversized"),
)
def test_invalid_primitives_stop_before_content_parsing(payload: object) -> None:
    assert inspect_ticket_content(payload) == (
        TicketContentIssue(
            field=TicketContentField.DOCUMENT,
            reason=TicketContentReason.INVALID_INPUT,
        ),
    )


def _field_line(label: str, value: str) -> str:
    return f"- {label}：{value}"


def _change_field(ticket: str, field: tuple[TicketContentField, str], state: str) -> str:
    _, label = field
    line = next(
        current for current in ticket.splitlines() if current.startswith(f"- {label}：")
    )
    if state == "missing":
        return ticket.replace(line + "\n", "", 1)
    if state == "empty":
        return ticket.replace(line, _field_line(label, ""), 1)
    if state == "placeholder":
        return ticket.replace(line, _field_line(label, "<fill this field>"), 1)
    if state == "duplicate":
        return ticket.replace(line, line + "\n" + line, 1)
    if state == "moved":
        return ticket.replace(line + "\n", "", 1) + f"\n## Elsewhere\n\n{line}\n"
    if state == "comment":
        return ticket.replace(line, f"<!--\n{line}\n-->", 1)
    if state == "fence":
        return ticket.replace(line, f"~~~~text\n{line}\n~~~~", 1)
    return ticket.replace(line, "    " + line, 1)


@pytest.mark.parametrize("field", _FIELDS, ids=tuple(row[0].value for row in _FIELDS))
@pytest.mark.parametrize(
    "state,reason",
    (("missing", TicketContentReason.MISSING), ("empty", TicketContentReason.MISSING),
     ("placeholder", TicketContentReason.PLACEHOLDER), ("duplicate", TicketContentReason.DUPLICATE),
     ("moved", TicketContentReason.MISSING), ("comment", TicketContentReason.MISSING),
     ("fence", TicketContentReason.MISSING), ("indent", TicketContentReason.MISSING)),
    ids=("missing", "empty", "placeholder", "duplicate", "moved", "comment", "fence", "indent"),
)
def test_each_required_field_requires_one_active_filled_bullet(field, state, reason) -> None:
    changed = _change_field(_TICKET, field, state)
    issues = inspect_ticket_content(changed.encode("utf-8"))
    assert TicketContentIssue(field=field[0], reason=reason) in issues


def test_filled_ticket_and_no_create_ticket_are_valid_shape() -> None:
    assert inspect_ticket_content(_TICKET.encode("utf-8")) == ()
    no_create = _TICKET.replace("create = src/new.py\n", "")
    no_create = no_create.replace(
        "- 新增檔案責任：src/new.py: parser; consumer local; acceptance AC1.",
        "- 新增檔案責任：N/A: this ticket creates no files.",
    )
    assert inspect_ticket_content(no_create.encode("utf-8")) == ()


def test_generic_type_angles_are_not_scaffold_placeholders() -> None:
    assert inspect_ticket_content(_TICKET.encode("utf-8")) == ()


def test_duplicate_required_section_is_diagnosed() -> None:
    changed = _TICKET + f"\n{_OUTCOME}\n"
    assert TicketContentIssue(
        field=TicketContentField.DOCUMENT, reason=TicketContentReason.DUPLICATE
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_same_reviewer_is_rejected_after_trimming_backticks() -> None:
    changed = _TICKET.replace("- reviewer：ReviewSeat", "- reviewer：` AuthorSeat `")
    assert TicketContentIssue(
        field=TicketContentField.REVIEWER, reason=TicketContentReason.SAME_REVIEWER
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_invalid_hidden_and_duplicate_boundaries_have_finite_results() -> None:
    hidden = _TICKET.replace(_BOUNDARY, f"<!--\n{_BOUNDARY}\n-->")
    example = _TICKET.replace(_BOUNDARY, f"````text\n{_BOUNDARY}\n````")
    duplicate = _TICKET + "\n" + _BOUNDARY
    invalid = _TICKET.replace("forbid = doc/", "forbid = ../secret")
    assert TicketContentIssue(field=TicketContentField.BOUNDARY, reason=TicketContentReason.MISSING) in inspect_ticket_content(hidden.encode())
    assert TicketContentIssue(field=TicketContentField.BOUNDARY, reason=TicketContentReason.MISSING) in inspect_ticket_content(example.encode())
    assert TicketContentIssue(field=TicketContentField.BOUNDARY, reason=TicketContentReason.DUPLICATE) in inspect_ticket_content(duplicate.encode())
    assert TicketContentIssue(field=TicketContentField.BOUNDARY, reason=TicketContentReason.INVALID_BOUNDARY) in inspect_ticket_content(invalid.encode())


def test_unclosed_active_boundary_is_invalid() -> None:
    changed = _TICKET.replace(_BOUNDARY, _BOUNDARY.rsplit("```", 1)[0])
    assert TicketContentIssue(
        field=TicketContentField.BOUNDARY, reason=TicketContentReason.INVALID_BOUNDARY
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_create_paths_need_exact_file_declarations() -> None:
    missing = _TICKET.replace(
        "- 新增檔案責任：src/new.py: parser; consumer local; acceptance AC1.",
        "- 新增檔案責任：src/other.py: parser; consumer local; acceptance AC1.",
    )
    directory = _TICKET.replace("create = src/new.py", "create = src/")
    for changed in (missing, directory):
        assert TicketContentIssue(
            field=TicketContentField.NEW_FILES,
            reason=TicketContentReason.MISSING_FILE_DECLARATION,
        ) in inspect_ticket_content(changed.encode("utf-8"))


def test_new_files_need_an_n_a_reason_when_no_create_is_declared() -> None:
    changed = _TICKET.replace("create = src/new.py\n", "")
    changed = changed.replace("新增檔案責任：src/new.py: parser; consumer local; acceptance AC1.",
                              "新增檔案責任：N/A")
    assert TicketContentIssue(
        field=TicketContentField.NEW_FILES,
        reason=TicketContentReason.MISSING_FILE_DECLARATION,
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_n_a_reason_requires_a_delimited_nonempty_reason() -> None:
    changed = _TICKET.replace("新增檔案責任：src/new.py", "新增檔案責任：N/ABC")
    changed = changed.replace("create = src/new.py\n", "")
    assert TicketContentIssue(
        field=TicketContentField.NEW_FILES,
        reason=TicketContentReason.MISSING_FILE_DECLARATION,
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_issue_order_is_finite_and_duplicate_pairs_are_collapsed() -> None:
    changed = _TICKET.replace(_EXPECTED_LINE + "\n", "", 1)
    changed = changed.replace(
        "- 正常／失敗／邊界驗收：valid input returns entries; invalid input yields an error.\n", "", 1
    )
    changed = changed.replace("forbid = doc/", "forbid = ../secret")
    issues = inspect_ticket_content(changed.encode("utf-8"))
    assert tuple((issue.field, issue.reason) for issue in issues) == (
        (TicketContentField.BOUNDARY, TicketContentReason.INVALID_BOUNDARY),
        (TicketContentField.EXPECTED, TicketContentReason.MISSING),
        (TicketContentField.ACCEPTANCE, TicketContentReason.MISSING),
    )
    assert len(issues) == len(set(issues))


def test_expected_hidden_in_comment_is_not_active() -> None:
    changed = _change_field(_TICKET, _FIELDS[0], "comment")
    assert TicketContentIssue(
        field=TicketContentField.EXPECTED, reason=TicketContentReason.MISSING
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_created_file_must_be_named() -> None:
    changed = _TICKET.replace("新增檔案責任：src/new.py", "新增檔案責任：src/other.py")
    assert TicketContentIssue(
        field=TicketContentField.NEW_FILES,
        reason=TicketContentReason.MISSING_FILE_DECLARATION,
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_scaffold_after_plain_word_is_not_generic_type_syntax() -> None:
    changed = _TICKET.replace(
        _EXPECTED_LINE,
        "- 核准 Expected（使用者可觀察結果）：Use <placeholder>.",
    )
    assert TicketContentIssue(
        field=TicketContentField.EXPECTED, reason=TicketContentReason.PLACEHOLDER
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_only_backticks_are_an_empty_field() -> None:
    changed = _TICKET.replace(
        _EXPECTED_LINE,
        f"- 核准 Expected（使用者可觀察結果）：{chr(96) * 2}",
    )
    assert TicketContentIssue(
        field=TicketContentField.EXPECTED, reason=TicketContentReason.MISSING
    ) in inspect_ticket_content(changed.encode("utf-8"))


def test_h1_heading_ends_the_required_section() -> None:
    changed = _TICKET.replace(_EXPECTED_LINE + "\n", "", 1)
    changed = changed.replace(
        _IMPLEMENTATION + "\n",
        f"# Outside\n{_EXPECTED_LINE}\n\n{_IMPLEMENTATION}\n",
        1,
    )
    assert TicketContentIssue(
        field=TicketContentField.EXPECTED, reason=TicketContentReason.MISSING
    ) in inspect_ticket_content(changed.encode("utf-8"))
