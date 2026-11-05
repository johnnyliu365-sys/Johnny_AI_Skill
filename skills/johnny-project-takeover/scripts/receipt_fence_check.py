"""Verify receipt fences against their captured evidence.

Usage:
  receipt_fence_check.py <receipt> <heading> <evidence-root> [--no-moving-ref]
                         [--self-note] [--authority-root PATH] [--legacy-allowlist FILE]
  receipt_fence_check.py --scan <dir> [--authority-root PATH] [--legacy-allowlist FILE]

Exit codes: 0 pass, 1 contract red, 2 tool fault (the evidence or scan root is not a
readable directory, or any other unexpected error), 3 usage error (`--help`, an unknown option
such as `--require-cmd`, extra positional arguments after `--scan <dir>`, a wrong number of
positional arguments). The console encoding never changes an exit code: stdout and stderr keep
the host encoding but escape what it cannot encode.

A run that checked nothing is never a pass (exit 1): NO_FENCES (a section holds no fenced block),
SCAN_NO_RECEIPTS (the scanned directory holds no receipt) and SCAN_NOTHING_CHECKED (receipts
exist but no section with a capture line was checked). Every printed subject (heading, path,
capture name, command excerpt) is escaped to one line.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import NoReturn

ELISIONS = ("(empty)", "<snip>", "…", "...")
_UNPRINTABLE = re.compile(r"[\x00-\x1f\x7f-\x9f  ]")


def one_line(text: str) -> str:
    """`text` with every control character and line separator written as an escape: one printed line."""
    return _UNPRINTABLE.sub(
        lambda match: f"\\x{ord(match.group()):02x}" if ord(match.group()) < 256 else f"\\u{ord(match.group()):04x}",
        text,
    )


def say(text: str) -> None:
    print(one_line(text))

PLACEHOLDER = re.compile(r"<[A-Za-z][^<>]*>")
MOVING_REF = re.compile(r"(?<![\w/.-])(HEAD|@\{u\}|@\{upstream\}|origin/\w+|github/\w+|refs/heads/\w+)(?![\w/.-])")

# A section-scoped `EVD=<dir>` line before the cmd: line lets $EVD/, ${EVD}/, $env:EVD/ and
# %EVD%\ prefixes on a redirect target resolve through the declared directory.
_EVD_DECL = re.compile(r"^EVD=(\S+)$")
_EVD_PREFIXES = ("$EVD/", "${EVD}/", "$env:EVD/", "%EVD%\\")

# A section-scoped `authority_root=<absolute path>` line (or the --authority-root option)
# maps that absolute prefix onto the current scan root. The value may contain spaces.
_AUTHORITY_DECL = re.compile(r"^authority_root=(.+)$")

# Receipts may be written on one OS and checked on another: every target is put into
# forward-slash form and a drive-letter prefix counts as absolute on every host.
_DRIVE_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


def _normalize_target(value: str) -> str:
    return value.replace("\\", "/")


def _target_is_absolute(value: str) -> bool:
    return bool(_DRIVE_ABSOLUTE.match(value)) or Path(value).is_absolute()


def _find_declaration(lines: list[str], before_index: int, pattern: re.Pattern[str]) -> str | None:
    """Return group(1) of the last match on a stripped line strictly before before_index."""
    value = None
    for idx in range(max(0, before_index)):
        match = pattern.match(lines[idx].strip())
        if match:
            value = match.group(1)
    return value


def _resolve_evd_dir(declared: str | None, evidence: Path, command_cwd: Path | None) -> Path | None:
    """Resolve an EVD= declaration; None when absent, absolute, escaping, or outside the evidence root."""
    if declared is None:
        return None
    if Path(declared).is_absolute() or ".." in Path(declared).parts:
        return None
    base = command_cwd or Path.cwd()
    candidate = (base / declared).resolve()
    evidence_resolved = evidence.resolve()
    if candidate != evidence_resolved and evidence_resolved not in candidate.parents:
        return None
    return candidate


def _strip_evd_prefix(target: str) -> tuple[bool, str]:
    for prefix in _EVD_PREFIXES:
        if target.startswith(prefix):
            remainder = _normalize_target(target[len(prefix):])
            if any(part == ".." for part in Path(remainder).parts):
                return False, target
            return True, remainder
    return False, target


def sections(text: str) -> Iterator[tuple[str, int, list[str]]]:
    lines = text.replace("\r\n", "\n").splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        yield lines[start].strip(), start, lines[start:end]


def capture_path(name: str, evidence: Path) -> Path | None:
    candidate = (evidence / _normalize_target(name)).resolve()
    try:
        candidate.relative_to(evidence.resolve())
    except ValueError:
        return None
    return candidate


def _strip_outer_backticks(command: str) -> str:
    command = command.strip()
    if len(command) >= 2 and command[0] == "`" and command[-1] == "`":
        return command[1:-1].strip()
    return command


_CMD_WRAPPER = re.compile(r"^\s*cmd(?:\.exe)?(?:\s+/[ds]){0,2}\s+/c\s+(.*)$", re.I | re.S)
_SET_PREFIX = re.compile(r"^\s*set\s+[A-Za-z_][A-Za-z0-9_]*=[^&]*&&\s*(.*)$", re.I | re.S)


def _unwrap_quoted_payload(text: str) -> str | None:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1]
    return None


def _strip_command_wrappers(statement: str) -> str:
    """Strip a cmd.exe wrapper and/or a leading `set NAME=value&&` chain from one statement."""
    statement = statement.strip()
    wrapper = _CMD_WRAPPER.match(statement)
    if wrapper:
        payload = _unwrap_quoted_payload(wrapper.group(1))
        if payload is not None:
            statement = payload.strip()
    set_prefix = _SET_PREFIX.match(statement)
    if set_prefix:
        statement = set_prefix.group(1).strip()
    return statement


def _split_statements(command: str) -> list[str]:
    """Split a command on unquoted `;`, `&&` and `||`.

Splitting on `&&` and `||` keeps an exit echo chained after the main command its own
statement, so its redirect target is checked separately."""
    statements, current = [], []
    quote = None
    i = 0
    length = len(command)
    while i < length:
        char = command[i]
        if char == "\\" and quote == '"':
            current.append(char)
            i += 1
        elif quote:
            current.append(char)
            if char == quote:
                quote = None
            i += 1
        elif char in ("'", '"'):
            quote = char
            current.append(char)
            i += 1
        elif char == ";":
            statements.append("".join(current).strip())
            current = []
            i += 1
        elif command.startswith("&&", i) or command.startswith("||", i):
            statements.append("".join(current).strip())
            current = []
            i += 2
        else:
            current.append(char)
            i += 1
    statements.append("".join(current).strip())
    return [statement for statement in statements if statement]


def _statements_with_wrappers(command: str) -> list[str]:
    """Split into statements, then unwrap each one; unwrapped payloads are split again."""
    command = _strip_outer_backticks(command)
    result = []
    for raw in _split_statements(command):
        unwrapped = _strip_command_wrappers(raw)
        if unwrapped != raw.strip():
            result.extend(_statements_with_wrappers(unwrapped))
        else:
            result.append(raw)
    return result


def _shell_tokens(statement: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    quote: str | None = None
    i = 0
    operators = ("2>&1", "2>>", "2>", "*>", ">>", ">")
    while i < len(statement):
        char = statement[i]
        if quote:
            if char == quote:
                quote = None
            else:
                current.append(char)
            i += 1
        elif char in ("'", '"'):
            quote = char
            i += 1
        elif char.isspace():
            if current:
                tokens.append("".join(current))
                current = []
            i += 1
        else:
            operator = next((item for item in operators if statement.startswith(item, i)), None)
            if operator:
                if current:
                    tokens.append("".join(current))
                    current = []
                tokens.append(operator)
                i += len(operator)
            else:
                current.append(char)
                i += 1
    if current:
        tokens.append("".join(current))
    return tokens


# Fixed, space-free stand-in substituted for a declared authority root before tokenizing,
# so an unquoted absolute path containing a space is not split into two tokens.
_AUTHORITY_PLACEHOLDER = "Z:\\__RF_AUTHORITY_ROOT_PLACEHOLDER__"


def _resolve_authority_placeholder(text: str, command_cwd: Path | None, authority_root: str | None) -> str:
    """Resolve a leading placeholder back to the current root; unchanged otherwise.

Resolves only when an authority root is in force, so a command that hardcodes the
internal placeholder text without a declaration is never accepted. Comparison is done
after backslash-to-slash normalization."""
    normalized = _normalize_target(text)
    placeholder = _normalize_target(_AUTHORITY_PLACEHOLDER)
    if authority_root and normalized.startswith(placeholder):
        return str(command_cwd or Path.cwd()) + normalized[len(placeholder):]
    return text


def _map_authority_root(candidate: Path, authority_root: str, evidence: Path, capture: str, command_cwd: Path | None) -> bool:
    """Whether candidate sits under authority_root and maps onto the capture.

The authority_root prefix is replaced by the current scan root and the remaining
relative path is compared with the capture. False when the prefix does not match or
the remainder contains `..`. Text is normalized to forward slashes first."""
    text = _normalize_target(str(candidate))
    declared = _normalize_target(authority_root.rstrip("\\/"))
    placeholder = _normalize_target(_AUTHORITY_PLACEHOLDER)
    remainder = None
    for prefix in (declared, placeholder):
        if text == prefix:
            remainder = ""
            break
        if text.startswith(prefix + "/"):
            remainder = text[len(prefix) + 1:]
            break
    if remainder is None:
        return False
    if any(part == ".." for part in Path(remainder).parts):
        return False
    base = command_cwd or Path.cwd()
    expected = (evidence / _normalize_target(capture)).resolve()
    return (base / remainder).resolve() == expected


def _bounded_base_resolution(
    candidate_str: str, expected: Path, evidence: Path, command_cwd: Path | None
) -> tuple[bool, bool]:
    """Resolve a slash-containing relative target against three bounded bases.

The bases are the scan cwd, the receipt directory and the evidence root. Returns
(matched, ambiguous): matched when exactly one base resolves to the capture and no other
base resolves to a different existing file; ambiguous when two or more bases resolve to
different existing files. A `..` segment never resolves."""
    candidate_str = _normalize_target(candidate_str)
    if any(part == ".." for part in Path(candidate_str).parts):
        return False, False
    bases = (command_cwd or Path.cwd(), evidence.parent, evidence)
    resolved = [(base / candidate_str).resolve() for base in bases]
    hits_capture = sum(1 for r in resolved if r == expected)
    other_existing = {r for r in resolved if r != expected and r.is_file()}
    if hits_capture == 1:
        return (True, False) if not other_existing else (False, True)
    return False, len(other_existing) >= 2


def _same_capture_target(
    target: str,
    capture: str,
    evidence: Path,
    command_cwd: Path | None = None,
    evd_dir: Path | None = None,
    authority_root: str | None = None,
) -> bool:
    expected = (evidence / _normalize_target(capture)).resolve()
    is_evd, remainder = _strip_evd_prefix(target)
    if is_evd:
        if evd_dir is None:
            return False
        return (evd_dir / remainder).resolve() == expected
    normalized_target = _normalize_target(target)
    candidate = Path(normalized_target)
    if _target_is_absolute(normalized_target):
        candidate = Path(_resolve_authority_placeholder(normalized_target, command_cwd, authority_root))
        if candidate.resolve() == expected:
            return True
        if authority_root:
            return _map_authority_root(candidate, authority_root, evidence, capture, command_cwd)
        return False
    if "/" in normalized_target:
        matched, _ = _bounded_base_resolution(normalized_target, expected, evidence, command_cwd)
        return matched
    return (evidence / Path(capture).parent / candidate).resolve() == expected


_EXIT_ECHO_COMMANDS = {"echo", "write-output", "printf"}


def _has_exit_output(tokens: list[str], statement: str = "") -> bool:
    if not tokens:
        return False
    command_word = tokens[0].rsplit("\\", 1)[-1].rsplit("/", 1)[-1].lower()
    is_bare_literal = statement.strip()[:1] in ("'", '"')
    if command_word not in _EXIT_ECHO_COMMANDS and not is_bare_literal:
        return False
    return bool(re.search(r"(?i)(?:^|[^A-Za-z0-9_$])exit=", " ".join(tokens)))


def _exit_only_output_targets_capture(
    exit_statements: list[list[tuple[str, str]]],
    capture: str,
    evidence: Path,
    command_cwd: Path | None,
    evd_dir: Path | None = None,
    matcher: Callable[[str], bool] | None = None,
    authority_root: str | None = None,
) -> bool:
    target_ok = matcher or (
        lambda target: _same_capture_target(target, capture, evidence, command_cwd, evd_dir, authority_root)
    )
    return bool(exit_statements) and all(
        any(
            operator == ">"
            and target_ok(target)
            for operator, target in redirections
        )
        for redirections in exit_statements
    )


def _resolve_plain_target(
    value: str, evidence: Path, command_cwd: Path | None, evd_dir: Path | None, authority_root: str | None = None
) -> Path:
    """Canonical resolved path used by the produced/reachable-chain bookkeeping.

Absolute values pass through the placeholder resolution first so a chain built from the
same declared-root-prefixed text as the capture compares in one coordinate space."""
    is_evd, remainder = _strip_evd_prefix(value)
    if is_evd and evd_dir is not None:
        return (evd_dir / remainder).resolve()
    normalized_value = _normalize_target(value)
    candidate = Path(normalized_value)
    if _target_is_absolute(normalized_value):
        return Path(_resolve_authority_placeholder(normalized_value, command_cwd, authority_root)).resolve()
    return ((command_cwd or Path.cwd()) / candidate).resolve()


_FILTER_COMMANDS = {
    "tail", "head", "cat", "type", "get-content", "select-string",
    "select-object", "findstr", "grep",
}


def _filter_input_file(arg_tokens: list[str]) -> str | None:
    """Best-effort extraction of the file a filter command reads.

An explicit -LiteralPath/-Path value wins, else the last non-flag positional token of the
first pipeline stage."""
    for index, token in enumerate(arg_tokens):
        if token.lower() in ("-literalpath", "-path") and index + 1 < len(arg_tokens):
            return arg_tokens[index + 1]
    first_stage = arg_tokens[:arg_tokens.index("|")] if "|" in arg_tokens else arg_tokens
    candidates = [
        token for token in first_stage
        if not token.startswith("-") and token.lower() not in _FILTER_COMMANDS
    ]
    return candidates[-1] if candidates else None


_LOOP_OPENER = re.compile(r"^(for|while|until)\b")
_LOOP_CLOSER = re.compile(r"^done\b")


def _statement_redirects(tokens: list[str]) -> list[tuple[str, str]]:
    return [
        (tokens[index], tokens[index + 1])
        for index in range(len(tokens) - 1)
        if tokens[index] in (">", ">>", "*>", "2>", "2>>")
    ]


def _loop_redirect_for_index(statements: list[str]) -> dict[int, list[tuple[str, str]]]:
    """Map bare exit-echo statements inside a for/while/until loop to the loop redirect.

Only a statement strictly between the opener and its `done` closer, with no redirect of
its own, is attributed; the closer must carry a redirect."""
    attributed: dict[int, list[tuple[str, str]]] = {}
    closer_idx = next((i for i, s in enumerate(statements) if _LOOP_CLOSER.match(s.strip())), None)
    if closer_idx is None:
        return attributed
    opener_idx = next(
        (i for i in range(closer_idx - 1, -1, -1) if _LOOP_OPENER.match(statements[i].strip())),
        None,
    )
    if opener_idx is None:
        return attributed
    closer_redirects = _statement_redirects(_shell_tokens(statements[closer_idx]))
    if not closer_redirects:
        return attributed
    normalized = [("2>>" if operator == "2>" else ">>", target) for operator, target in closer_redirects]
    for body_idx in range(opener_idx + 1, closer_idx):
        body_tokens = _shell_tokens(statements[body_idx])
        if _has_exit_output(body_tokens, statements[body_idx]) and not _statement_redirects(body_tokens):
            attributed[body_idx] = normalized
    return attributed


def _copy_item_source_and_dest(tokens: list[str]) -> tuple[str | None, str | None]:
    lower = [token.lower() for token in tokens]
    source_index = next((i + 1 for i, t in enumerate(lower[:-1]) if t in ("-literalpath", "-path")), None)
    dest_index = next((i + 1 for i, t in enumerate(lower[:-1]) if t == "-destination"), None)
    claimed = {i for i in (source_index, dest_index) if i is not None}
    positionals = [
        tokens[i] for i, t in enumerate(tokens)
        if i not in claimed and not t.startswith("-") and t.lower() != "copy-item"
    ]
    source = tokens[source_index] if source_index is not None else (positionals[0] if positionals else None)
    rest = positionals if source_index is not None else positionals[1:]
    dest = tokens[dest_index] if dest_index is not None else (rest[0] if rest else None)
    return source, dest


def _capture_command_targets_capture(
    command: str,
    capture: str,
    evidence: Path,
    command_cwd: Path | None = None,
    evd_dir: Path | None = None,
    authority_root: str | None = None,
) -> str | None:
    """Return None when the command targets the capture, else a failure code (CMD_NO_REDIRECT or AMBIGUOUS_TARGET)."""
    if authority_root and " " in authority_root and authority_root in command:
        command = command.replace(authority_root, _AUTHORITY_PLACEHOLDER)
    capture_expected = (evidence / _normalize_target(capture)).resolve()
    targets = []
    exit_statements, append_statements, copy_statements = [], [], []
    produced: set[Path] = set()
    rewritten: set[Path] = set()
    filter_read_index: dict[Path, int] = {}

    def resolve(value: str) -> Path:
        return _resolve_plain_target(value, evidence, command_cwd, evd_dir, authority_root)

    statements = _statements_with_wrappers(command)
    loop_redirects = _loop_redirect_for_index(statements)

    for statement_index, statement in enumerate(statements):
        tokens = _shell_tokens(statement)
        redirections = []
        first_redirect_index = len(tokens)
        for index, token in enumerate(tokens[:-1]):
            if token in (">", ">>", "*>", "2>", "2>>"):
                redirections.append((token, tokens[index + 1]))
                first_redirect_index = min(first_redirect_index, index)
        arg_tokens = tokens[:first_redirect_index]
        is_add_content = any(token.lower() == "add-content" for token in tokens)
        is_copy_item = any(token.lower() == "copy-item" for token in tokens)
        is_filter = bool(redirections) and any(token.lower() in _FILTER_COMMANDS for token in arg_tokens)
        has_exit_output = _has_exit_output(tokens, statement)

        if is_add_content:
            append_statements.append(tokens)
            path_index = next(
                (i + 1 for i, t in enumerate(tokens[:-1]) if t.lower() in ("-literalpath", "-path")),
                None,
            )
            if path_index is not None:
                produced.add(resolve(tokens[path_index]))
        elif is_copy_item:
            source, dest = _copy_item_source_and_dest(tokens)
            if source is not None and dest is not None:
                source_resolved, dest_resolved = resolve(source), resolve(dest)
                produced_ok = source_resolved in produced and source_resolved not in rewritten
                if dest_resolved in produced:
                    rewritten.add(dest_resolved)
                copy_statements.append((source_resolved, dest_resolved, produced_ok))
                if produced_ok:
                    produced.add(dest_resolved)
        elif is_filter:
            source = _filter_input_file(arg_tokens)
            dest = redirections[-1][1] if redirections else None
            if dest is not None:
                filter_dest = resolve(dest)
                targets.append(dest)
                if filter_dest in produced:
                    rewritten.add(filter_dest)
                produced.add(filter_dest)
            if source is not None and dest is not None:
                source_resolved = resolve(source)
                filter_read_index[source_resolved] = statement_index
                produced_ok = source_resolved in produced and source_resolved not in rewritten
                filter_dest = resolve(dest)
                copy_statements.append((source_resolved, filter_dest, produced_ok))
                if produced_ok:
                    produced.add(filter_dest)
        elif has_exit_output:
            effective_redirections = redirections or loop_redirects.get(statement_index, redirections)
            exit_statements.append((effective_redirections, statement_index))
            for _, target in effective_redirections:
                produced.add(resolve(target))
        else:
            targets.extend(target for _, target in redirections)
            for operator, target in redirections:
                target_resolved = resolve(target)
                if operator == ">" and target_resolved in produced:
                    rewritten.add(target_resolved)
                produced.add(target_resolved)

    valid_copy_edges = [(source, dest) for source, dest, produced_ok in copy_statements if produced_ok]
    reachable_to_capture: set[Path] = {capture_expected}
    copy_reaches_capture = False
    changed = True
    while changed:
        changed = False
        for source_resolved, dest_resolved in valid_copy_edges:
            if dest_resolved in reachable_to_capture and source_resolved not in reachable_to_capture:
                reachable_to_capture.add(source_resolved)
                changed = True
            if dest_resolved == capture_expected:
                copy_reaches_capture = True
    copy_reachable_extra = reachable_to_capture - {capture_expected}

    ambiguous_seen = False

    def matches_capture_or_chain(raw: str) -> bool:
        nonlocal ambiguous_seen
        if _same_capture_target(raw, capture, evidence, command_cwd, evd_dir, authority_root):
            return True
        is_evd, _ = _strip_evd_prefix(raw)
        normalized_raw = _normalize_target(raw)
        if not is_evd and not _target_is_absolute(normalized_raw) and "/" in normalized_raw:
            _, ambiguous = _bounded_base_resolution(raw, capture_expected, evidence, command_cwd)
            ambiguous_seen = ambiguous_seen or ambiguous
        if not copy_reachable_extra:
            return False
        if not is_evd and not _target_is_absolute(normalized_raw) and "/" not in normalized_raw:
            return False  # bare target: _same_capture_target already gave the answer
        return resolve(raw) in copy_reachable_extra

    reached_by_other_means = bool(targets and any(matches_capture_or_chain(target) for target in targets)) or copy_reaches_capture

    def exit_append_precedes_any_filter_read(target: str, statement_index: int) -> bool:
        """An exit append only counts against a filter read of the same path if the read happens later (or never)."""
        resolved = resolve(target)
        read_index = filter_read_index.get(resolved)
        return read_index is None or statement_index < read_index

    def exit_statements_ok() -> bool:
        if not exit_statements:
            return True
        if reached_by_other_means:
            return all(
                any(
                    operator in (">>", "2>>")
                    and matches_capture_or_chain(target)
                    and exit_append_precedes_any_filter_read(target, statement_index)
                    for operator, target in redirections
                )
                for redirections, statement_index in exit_statements
            )
        return _exit_only_output_targets_capture(
            [redirections for redirections, _ in exit_statements],
            capture, evidence, command_cwd, evd_dir, matches_capture_or_chain,
        )

    if not exit_statements_ok():
        return "AMBIGUOUS_TARGET" if ambiguous_seen else "CMD_NO_REDIRECT"
    if not reached_by_other_means and not exit_statements:
        return "AMBIGUOUS_TARGET" if ambiguous_seen else "CMD_NO_REDIRECT"
    for tokens in append_statements:
        path_index = next(
            (index + 1 for index, token in enumerate(tokens[:-1]) if token.lower() in ("-literalpath", "-path")),
            None,
        )
        if path_index is None or not matches_capture_or_chain(tokens[path_index]):
            return "AMBIGUOUS_TARGET" if ambiguous_seen else "CMD_NO_REDIRECT"
    return None


# A capture whose last line is a bare exit=N while its cmd: never mentions exit= has no
# command-side backing for that claim; it fails unless on the optional allowlist.
_EXIT_LINE = re.compile(r"^exit=\d+$")


def _command_has_exit_statement(command: str) -> bool:
    """Whether the command text mentions exit= in any form.

Deliberately lenient: a capture that legitimately records its own exit code always has
such text somewhere in the command."""
    return bool(re.search(r"(?i)exit=", command))


def load_legacy_allowlist(path: Path | None) -> set[tuple[str, str, str]]:
    """Read tab-separated (receipt, heading, capture-basename) rows; `#` starts a comment."""
    allowed: set[tuple[str, str, str]] = set()
    if path is None:
        return allowed
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            allowed.add((parts[0], parts[1], parts[2]))
    return allowed


def _is_local_self_note(command: str, receipt: Path, heading: str) -> bool:
    for statement in _statements_with_wrappers(command):
        tokens = _shell_tokens(statement)
        script_index = next(
            (index for index, token in enumerate(tokens) if token.replace("\\", "/").rsplit("/", 1)[-1].lower() == "receipt_fence_check.py"),
            None,
        )
        if script_index is None or "--self-note" not in tokens[script_index + 1:]:
            continue
        args = [token for token in tokens[script_index + 1:] if token != "--self-note"]
        if len(args) >= 2 and Path(args[0]).resolve() == receipt.resolve() and args[1].strip() == heading.strip():
            return True
    return False


def check_section(
    lines: list[str], evidence: Path, section_line: int, require_cmd: bool = True, no_moving_ref: bool = False,
    command_cwd: Path | None = None,
    legacy_allowlist: set[tuple[str, str, str]] | None = None,
    legacy_counter: list[int] | None = None,
    legacy_receipt_path: str | None = None,
    legacy_heading: str | None = None,
    legacy_candidates: list[tuple[str, str, str]] | None = None,
    default_authority_root: str | None = None,
) -> tuple[int, list[str]]:
    failures, fences = [], 0
    i = 0
    while i < len(lines):
        if not lines[i].startswith("```"):
            i += 1
            continue
        fences += 1
        opening = i
        j = i + 1
        while j < len(lines) and not lines[j].startswith("```"):
            j += 1
        if j == len(lines):
            failures.append(f"FAIL UNCLOSED_FENCE at section line {section_line + opening + 1}")
        body = "\n".join(lines[i + 1:j])
        cap = None
        for back in range(i - 1, max(-1, i - 4), -1):
            match = re.match(r"^capture:\s*(\S+)\s*$", lines[back].strip())
            if match:
                cap = match.group(1)
                cap_line = back
                break
        if cap is None:
            failures.append(f"FAIL FENCE_CAPTURE_MISSING at section line {section_line + opening + 1}")
        else:
            command = None
            authority_root = None
            if require_cmd:
                prev = lines[cap_line - 1].strip() if cap_line else ""
                if not re.match(r"^cmd:\s*\S", prev):
                    failures.append(f"FAIL CMD_MISSING at section line {section_line + cap_line + 1}: capture {cap}")
                else:
                    command = prev[4:].strip()
                    evd_declared = _find_declaration(lines, cap_line - 1, _EVD_DECL)
                    evd_dir = _resolve_evd_dir(evd_declared, evidence, command_cwd)
                    authority_declared = (
                        _find_declaration(lines, cap_line - 1, _AUTHORITY_DECL) or default_authority_root
                    )
                    authority_root = (
                        authority_declared
                        if authority_declared and _target_is_absolute(_normalize_target(authority_declared))
                        else None
                    )
                    if PLACEHOLDER.search(command):
                        failures.append(f"FAIL CMD_PLACEHOLDER at section line {section_line + cap_line + 1}: {command[:120]}")
                    no_redirect_reason = _capture_command_targets_capture(command, cap, evidence, command_cwd, evd_dir, authority_root)
                    if no_redirect_reason:
                        failures.append(f"FAIL {no_redirect_reason} at section line {section_line + cap_line + 1}: {cap}")
                    if no_moving_ref and MOVING_REF.search(command):
                        failures.append(f"FAIL CMD_MOVING_REF at section line {section_line + cap_line + 1}: {command[:120]}")
            path = capture_path(cap, evidence)
            if path is None:
                failures.append(f"FAIL CAPTURE_OUTSIDE_EVIDENCE at section line {section_line + opening + 1}: {cap}")
            elif not path.is_file():
                failures.append(f"FAIL CAPTURE_MISSING at section line {section_line + opening + 1}: {path}")
            else:
                raw = path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n").rstrip("\n")
                if raw != body.rstrip("\n"):
                    failures.append(f"FAIL BODY_MISMATCH at section line {section_line + opening + 1}: {cap}")
                for token in ELISIONS:
                    if token in body and token not in raw:
                        failures.append(f"FAIL ELISION_MISSING at section line {section_line + opening + 1}: {token!r}")
                if require_cmd and command is not None:
                    last_line = raw.splitlines()[-1] if raw else ""
                    if _EXIT_LINE.match(last_line.strip()) and not _command_has_exit_statement(command):
                        if legacy_counter is not None:
                            legacy_counter[0] += 1
                        key = (legacy_receipt_path or "", legacy_heading or "", Path(cap).name)
                        if legacy_candidates is not None:
                            legacy_candidates.append(key)
                        if legacy_allowlist is None or key not in legacy_allowlist:
                            failures.append(f"FAIL LEGACY_UNCLAIMED_EXIT at section line {section_line + opening + 1}: {cap}")
        i = j + 1
    return fences, failures


USAGE = (
    "usage: receipt_fence_check.py <receipt> <heading> <evidence-root> "
    "[--no-moving-ref] [--self-note] [--authority-root PATH] [--legacy-allowlist FILE] "
    "| --scan <dir> [--authority-root PATH] [--legacy-allowlist FILE]"
)


def _evidence_root_readable(path: Path) -> bool:
    try:
        return path.is_dir() and os.access(path, os.R_OK | os.X_OK)
    except OSError:
        return False


def explicit(
    receipt: Path,
    heading: str,
    evidence: Path,
    no_moving_ref: bool = False,
    *,
    self_note: bool = False,
    authority_root: str | None = None,
    legacy_allowlist: set[tuple[str, str, str]] | None = None,
) -> int:
    if not _evidence_root_readable(evidence):
        say(f"FAIL EVIDENCE_ROOT_UNREADABLE: {evidence}")
        return 2
    try:
        text = receipt.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeDecodeError) as exc:
        say(f"FAIL receipt unreadable: {receipt}: {exc}")
        return 3
    found = next(((start, lines) for title, start, lines in sections(text) if title == heading.strip()), None)
    if found is None:
        say(f"FAIL section heading not found: {heading}")
        return 3
    start, lines = found
    allowlist = legacy_allowlist if legacy_allowlist is not None else set()
    counter = [0]
    fences, failures = check_section(
        lines, evidence, start, True, no_moving_ref,
        legacy_allowlist=allowlist, legacy_counter=counter,
        legacy_receipt_path=receipt.as_posix(), legacy_heading=heading.strip(),
        default_authority_root=authority_root,
    )
    if fences == 0:
        failures.append(f"FAIL NO_FENCES: the section {heading.strip()} holds no fenced block, so nothing was checked")
    for failure in failures:
        say(failure)
    legacy_suffix = f" legacy_unclaimed_exit={counter[0]}" if counter[0] else ""
    if self_note:
        say(f"fences={max(0, fences - 1)} (excluding this run's own capture fence) failures={len(failures)}{legacy_suffix}")
    else:
        say(f"fences={fences} failures={len(failures)}{legacy_suffix}")
    return 1 if failures else 0


def scan(
    root: Path,
    *,
    authority_root: str | None = None,
    legacy_allowlist: set[tuple[str, str, str]] | None = None,
) -> int:
    if not _evidence_root_readable(root):
        say(f"FAIL SCAN_ROOT_UNREADABLE: {root}")
        return 2
    receipts = section_count = skipped = fences = failures = legacy_cmd = legacy_ref = 0
    legacy_unclaimed_exit = 0
    allowlist = legacy_allowlist if legacy_allowlist is not None else set()
    for receipt in sorted(root.rglob("*.md")):
        receipts += 1
        text = receipt.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        evidence_root = receipt.parent / "evidence"
        for title, start, lines in sections(text):
            capture_matches = [re.match(r"^capture:\s*(\S+)\s*$", line.strip()) for line in lines]
            captures = [m.group(1) for m in capture_matches if m]
            if not captures:
                skipped += 1
                continue
            section_count += 1
            has_cmd = any(line.strip().startswith("cmd:") for line in lines)
            if not has_cmd:
                legacy_cmd += 1
            moving = any(line.strip() == "rules: cmd_exact moving_ref" for line in lines)
            if not moving:
                legacy_ref += 1
            # A capture name must match exactly one file under the receipt's evidence tree.
            resolved_lines = list(lines)
            for name in captures:
                matches = list(evidence_root.rglob(Path(name).name)) if evidence_root.exists() else []
                if len(matches) != 1:
                    failures += 1
                    say(f"FAIL SCAN_CAPTURE_{'MISSING' if not matches else 'AMBIGUOUS'} {receipt}:{title}: {name} matches={len(matches)}")
                else:
                    rel = matches[0].relative_to(evidence_root).as_posix()
                    for pos, line in enumerate(resolved_lines):
                        if line.strip() == f"capture: {name}":
                            resolved_lines[pos] = f"capture: {rel}"
            legacy_counter = [0]
            # The allowlist key uses the receipt path exactly as the walk discovered it,
            # which equals the path given on the command line for the same receipt.
            receipt_key = receipt.as_posix()
            section_fences, section_failures = check_section(
                resolved_lines, evidence_root, start, has_cmd, moving,
                legacy_allowlist=allowlist, legacy_counter=legacy_counter,
                legacy_receipt_path=receipt_key, legacy_heading=title,
                default_authority_root=authority_root,
            )
            legacy_unclaimed_exit += legacy_counter[0]
            if section_fences == 0:
                section_failures.append("FAIL NO_FENCES: the section holds no fenced block, so nothing was checked")
            self_note_captures = []
            for capture_index, line in enumerate(lines):
                match = re.match(r"^capture:\s*(\S+)\s*$", line.strip())
                if not match or capture_index == 0:
                    continue
                command_line = lines[capture_index - 1].strip()
                if command_line.startswith("cmd:") and _is_local_self_note(command_line[4:].strip(), receipt, title):
                    self_note_captures.append(capture_index)
            if self_note_captures:
                final_capture = max((i for i, line in enumerate(lines) if line.strip().startswith("capture:")), default=-1)
                later_fences = [i for i, line in enumerate(lines) if i > final_capture and line.startswith("```")]
                if self_note_captures != [final_capture] or final_capture < 0 or len(later_fences) != 2 or later_fences[-1] != len(lines) - 1:
                    section_failures.append("FAIL SELF_NOTE_NOT_FINAL: self-note capture must be the final fence")
                elif len(captures) < 1:
                    section_failures.append("FAIL SELF_NOTE_CAPTURE_MISSING")
                else:
                    match = re.search(r"fences=(\d+) \(excluding this run's own capture fence\) failures=(\d+)", "\n".join(lines[final_capture + 1:]))
                    if not match or int(match.group(1)) != section_fences - 1:
                        section_failures.append("FAIL SELF_NOTE_COUNT_MISMATCH")
            fences += section_fences
            failures += len(section_failures)
            for failure in section_failures:
                say(f"{receipt}:{title}: {failure}")
    if receipts == 0:
        say(f"FAIL SCAN_NO_RECEIPTS: no receipt (*.md) under {root}, so nothing was checked")
        failures += 1
    elif section_count == 0 or fences == 0:
        say(f"FAIL SCAN_NOTHING_CHECKED: {receipts} receipt(s) under {root} but no section with a capture line and a fence was checked")
        failures += 1
    legacy_suffix = f" legacy_unclaimed_exit={legacy_unclaimed_exit}" if legacy_unclaimed_exit else ""
    say(f"receipts={receipts} sections={section_count} skipped={skipped} fences={fences} failures={failures} legacy_cmd={legacy_cmd} legacy_ref={legacy_ref}{legacy_suffix}")
    return 1 if failures else 0


def _harden_streams() -> None:
    """Keep the host's encoding but never let an unencodable character raise on output."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(errors="backslashreplace")
            except (OSError, ValueError):
                pass


class _UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _UsageError(message)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the gate; every unexpected error is a tool fault (exit 2), never a red (exit 1)."""
    _harden_streams()
    try:
        return _run(argv)
    except Exception as exc:  # noqa: BLE001 - an uncaught error must never reach the caller as exit 1
        print(f"receipt_fence_check.py: tool fault: {one_line(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 2


def _run(argv: Sequence[str] | None) -> int:
    parser = _Parser(prog="receipt_fence_check.py", usage=USAGE, add_help=False)
    parser.add_argument("--scan", metavar="ROOT")
    parser.add_argument("--no-moving-ref", action="store_true")
    parser.add_argument("--self-note", action="store_true")
    parser.add_argument("--authority-root", metavar="PATH")
    parser.add_argument("--legacy-allowlist", metavar="FILE")
    parser.add_argument("args", nargs="*")
    try:
        ns = parser.parse_args(argv)
    except _UsageError as exc:
        print(USAGE, file=sys.stderr)
        print(f"receipt_fence_check.py: error: {one_line(str(exc))}", file=sys.stderr)
        return 3
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) and exc.code != 0 else 3
    allowlist: set[tuple[str, str, str]] = set()
    if ns.legacy_allowlist:
        try:
            allowlist = load_legacy_allowlist(Path(ns.legacy_allowlist))
        except (OSError, UnicodeDecodeError) as exc:
            print(USAGE, file=sys.stderr)
            print(f"receipt_fence_check.py: error: allowlist unreadable: {one_line(str(exc))}", file=sys.stderr)
            return 3
    if ns.scan:
        if ns.args:
            print(USAGE, file=sys.stderr)
            print(f"receipt_fence_check.py: error: --scan takes one directory and no other argument: {one_line(' '.join(ns.args))}", file=sys.stderr)
            return 3
        return scan(Path(ns.scan), authority_root=ns.authority_root, legacy_allowlist=allowlist)
    if len(ns.args) != 3:
        print(USAGE, file=sys.stderr)
        return 3
    return explicit(
        Path(ns.args[0]), ns.args[1], Path(ns.args[2]), ns.no_moving_ref,
        self_note=ns.self_note, authority_root=ns.authority_root, legacy_allowlist=allowlist,
    )


if __name__ == "__main__":
    sys.exit(main())
