"""Finite, local diagnostics for the content shape of one ticket document."""

from __future__ import annotations

from enum import Enum
import re

from pydantic import BaseModel, ConfigDict

from .document_mutation_gate import BoundaryReadStatus, DocumentBoundary, read_boundary


class TicketContentField(str, Enum):
    DOCUMENT = "DOCUMENT"
    BOUNDARY = "BOUNDARY"
    EXPECTED = "EXPECTED"
    ACCEPTANCE = "ACCEPTANCE"
    STOP = "STOP"
    IMPLEMENTER = "IMPLEMENTER"
    REVIEWER = "REVIEWER"
    CONTRACT = "CONTRACT"
    DEPENDENCIES = "DEPENDENCIES"
    NEW_FILES = "NEW_FILES"


class TicketContentReason(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    MISSING = "MISSING"
    DUPLICATE = "DUPLICATE"
    PLACEHOLDER = "PLACEHOLDER"
    INVALID_BOUNDARY = "INVALID_BOUNDARY"
    SAME_REVIEWER = "SAME_REVIEWER"
    MISSING_FILE_DECLARATION = "MISSING_FILE_DECLARATION"


class TicketContentIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    field: TicketContentField
    reason: TicketContentReason


_MAX_PAYLOAD_BYTES = 131072
_EXPECTED_SECTION = "使用者拍板與可觀察結果"
_IMPLEMENTATION_SECTION = "實作範圍、依賴與 ticket elements"
_FIELD_SPECS: tuple[tuple[TicketContentField, str, str], ...] = (
    (TicketContentField.EXPECTED, _EXPECTED_SECTION, "核准 Expected（使用者可觀察結果）"),
    (TicketContentField.ACCEPTANCE, _EXPECTED_SECTION, "正常／失敗／邊界驗收"),
    (TicketContentField.STOP, _EXPECTED_SECTION, "停止條件"),
    (TicketContentField.IMPLEMENTER, _IMPLEMENTATION_SECTION, "implementation owner"),
    (TicketContentField.REVIEWER, _IMPLEMENTATION_SECTION, "reviewer"),
    (TicketContentField.CONTRACT, _IMPLEMENTATION_SECTION, "公開契約／資料模型"),
    (TicketContentField.DEPENDENCIES, _IMPLEMENTATION_SECTION, "直接依賴與狀態"),
    (TicketContentField.NEW_FILES, _IMPLEMENTATION_SECTION, "新增檔案責任"),
)
_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
_HEADING = re.compile(r"^##(?!#)[ \t]+(.*?)[ \t]*#*[ \t]*$")
_BULLET = re.compile(r"^- (.+?)[：:](.*)$")
_ANGLE = re.compile(r"<([^<>\n]+)>")
_GENERIC_ARGUMENTS = re.compile(
    r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\s*[,|&]\s*[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)*"
)
_PATH_PATTERN = re.compile(r"[*?\[]")
_FIELD_ORDER = {field: index for index, field in enumerate(TicketContentField)}
_REASON_ORDER = {reason: index for index, reason in enumerate(TicketContentReason)}


def _add_issue(
    issues: set[tuple[TicketContentField, TicketContentReason]],
    field: TicketContentField,
    reason: TicketContentReason,
) -> None:
    issues.add((field, reason))


def _active_lines_and_boundaries(markdown: str) -> tuple[list[str], list[str]]:
    visible: list[str] = []
    boundaries: list[str] = []
    in_comment = False
    fence_char = ""
    fence_size = 0
    fence_info = ""
    fence_open = ""
    fence_body: list[str] = []
    for line in markdown.splitlines():
        if fence_char:
            close = _FENCE_CLOSE.fullmatch(line)
            if close and close.group(1)[0] == fence_char and len(close.group(1)) >= fence_size:
                if fence_info == "johnny-boundary":
                    boundaries.append("\n".join((fence_open, *fence_body, line)))
                fence_char = ""
                fence_size = 0
                fence_info = ""
                fence_body = []
            elif fence_info == "johnny-boundary":
                fence_body.append(line)
            continue

        clean: list[str] = []
        position = 0
        while position < len(line):
            if in_comment:
                end = line.find("-->", position)
                if end < 0:
                    position = len(line)
                else:
                    in_comment = False
                    position = end + 3
            else:
                start = line.find("<!--", position)
                if start < 0:
                    clean.append(line[position:])
                    position = len(line)
                else:
                    clean.append(line[position:start])
                    in_comment = True
                    position = start + 4
        active = "".join(clean)
        opening = _FENCE_OPEN.fullmatch(active)
        if opening:
            marker = opening.group(1)
            fence_char = marker[0]
            fence_size = len(marker)
            fence_info = opening.group(2).strip()
            fence_open = active
            fence_body = []
            continue
        visible.append(active)
    if fence_char and fence_info == "johnny-boundary":
        boundaries.append("\n".join((fence_open, *fence_body)))
    return visible, boundaries


def _section_lines(lines: list[str], title: str) -> tuple[int, list[str]]:
    count = 0
    active = False
    content: list[str] = []
    for line in lines:
        heading = _HEADING.fullmatch(line)
        if heading:
            heading_title = heading.group(1).strip().rstrip("# ").strip()
            active = heading_title == title
            if active:
                count += 1
        elif active:
            content.append(line)
    return count, content


def _field_values(lines: list[str], label: str) -> list[str]:
    values: list[str] = []
    for line in lines:
        bullet = _BULLET.fullmatch(line)
        if bullet and bullet.group(1).strip().strip("`").strip() == label:
            values.append(bullet.group(2).strip())
    return values


def _has_scaffold(value: str) -> bool:
    for match in _ANGLE.finditer(value):
        prefix = value[: match.start()].rstrip()
        name = re.search(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$", prefix)
        if name and _GENERIC_ARGUMENTS.fullmatch(match.group(1).strip()):
            continue
        return True
    return False


def _same_visible_value(value: str) -> str:
    result = value.strip()
    while len(result) >= 2 and result[0] == "`" and result[-1] == "`":
        result = result[1:-1].strip()
    return result


def _is_n_a_reason(value: str) -> bool:
    return re.match(r"(?i)^N/A(?:\s*[:：—-]\s*|\s+)\S", value) is not None


def _path_is_declared(path: str, value: str) -> bool:
    pattern = rf"(?<![\w./-]){re.escape(path)}(?![\w./-])"
    return re.search(pattern, value) is not None


def inspect_ticket_content(payload: bytes) -> tuple[TicketContentIssue, ...]:
    """Return shape diagnostics; valid shape says nothing about admission or truth."""

    if type(payload) is not bytes or not payload or len(payload) > _MAX_PAYLOAD_BYTES:
        return (
            TicketContentIssue(
                field=TicketContentField.DOCUMENT,
                reason=TicketContentReason.INVALID_INPUT,
            ),
        )
    try:
        markdown = payload.decode("utf-8")
    except UnicodeDecodeError:
        return (
            TicketContentIssue(
                field=TicketContentField.DOCUMENT,
                reason=TicketContentReason.INVALID_INPUT,
            ),
        )
    issues: set[tuple[TicketContentField, TicketContentReason]] = set()
    active_lines, boundary_blocks = _active_lines_and_boundaries(markdown)
    outcome_count, outcome_lines = _section_lines(active_lines, _EXPECTED_SECTION)
    implementation_count, implementation_lines = _section_lines(
        active_lines, _IMPLEMENTATION_SECTION
    )
    if outcome_count > 1 or implementation_count > 1:
        _add_issue(issues, TicketContentField.DOCUMENT, TicketContentReason.DUPLICATE)
    sections = {
        _EXPECTED_SECTION: outcome_lines,
        _IMPLEMENTATION_SECTION: implementation_lines,
    }
    values: dict[TicketContentField, str] = {}
    for field, section, label in _FIELD_SPECS:
        found = _field_values(sections[section], label)
        if not found:
            _add_issue(issues, field, TicketContentReason.MISSING)
        elif len(found) > 1:
            _add_issue(issues, field, TicketContentReason.DUPLICATE)
        elif not found[0]:
            _add_issue(issues, field, TicketContentReason.MISSING)
        elif _has_scaffold(found[0]):
            _add_issue(issues, field, TicketContentReason.PLACEHOLDER)
        else:
            values[field] = found[0]

    if TicketContentField.IMPLEMENTER in values and TicketContentField.REVIEWER in values:
        if _same_visible_value(values[TicketContentField.IMPLEMENTER]) == _same_visible_value(
            values[TicketContentField.REVIEWER]
        ):
            _add_issue(issues, TicketContentField.REVIEWER, TicketContentReason.SAME_REVIEWER)

    boundary: DocumentBoundary | None = None
    if not boundary_blocks:
        _add_issue(issues, TicketContentField.BOUNDARY, TicketContentReason.MISSING)
    elif len(boundary_blocks) > 1:
        _add_issue(issues, TicketContentField.BOUNDARY, TicketContentReason.DUPLICATE)
    else:
        status, parsed_boundary, _detail = read_boundary(boundary_blocks[0])
        if status is not BoundaryReadStatus.DECLARED or parsed_boundary is None:
            _add_issue(issues, TicketContentField.BOUNDARY, TicketContentReason.INVALID_BOUNDARY)
        else:
            boundary = parsed_boundary

    new_files = values.get(TicketContentField.NEW_FILES)
    if boundary is not None and new_files is not None:
        if not boundary.create:
            if not _is_n_a_reason(new_files):
                _add_issue(
                    issues,
                    TicketContentField.NEW_FILES,
                    TicketContentReason.MISSING_FILE_DECLARATION,
                )
        elif any(
            path.endswith("/") or _PATH_PATTERN.search(path) is not None
            for path in boundary.create
        ) or any(not _path_is_declared(path, new_files) for path in boundary.create):
            _add_issue(
                issues,
                TicketContentField.NEW_FILES,
                TicketContentReason.MISSING_FILE_DECLARATION,
            )

    ordered = sorted(
        issues,
        key=lambda item: (_FIELD_ORDER[item[0]], _REASON_ORDER[item[1]]),
    )
    return tuple(TicketContentIssue(field=field, reason=reason) for field, reason in ordered)
