#!/usr/bin/env python3
"""Recompute and check the (revision, digest) pins of Markdown index tables.

Usage: index_pins.py (--check | --write) [--root DIR] [--json PATH]
                     [--sealed-state WORD] [<index.md> ...]

An index row pins a leaf file with two cells that carry no human judgement:

    revision = the commit that last changed the leaf   (git log -1 -- <leaf>)
    digest   = sha256 of the leaf bytes at that commit (git show <revision>:<leaf>)

Row format (header cell names are case-insensitive; a prefix before `revision`,
`digest` and `leaf` groups several pins in one row):

    | id | kind | state | revision    | digest        | leaf      |
    | -- | ---- | ----- | ----------- | ------------- | --------- |
    | a1 | spec | open  | git:<40hex> | sha256:<64hex> | path.md  |

Behaviour:
  --check  report only; exit 1 when any row drifted or is defective
  --write  recompute the two cells in place; exit 1 when defective rows remain

Only the two pin cells of existing rows are rewritten. Rows are never added or
removed, other cells, other lines and the line endings are left untouched, and the
existing `git:` / `sha256:` prefix and backtick spelling of each cell is kept. Rows
whose state cell contains the sealed word (default SEALED) are never repinned; their
digest must verify under the recorded revision or the row is a defect.

Defects (all exit 1): ROW_SHAPE_MISMATCH, ORPHAN_PINNED_ROW, SEALED_PIN_INVALID,
SEALED_PIN_MISSING, SKIP_UNRESOLVED, SKIP_UNTRACKED, SKIP_NO_PATH_IN_CELL,
SKIP_NO_HASH_IN_CELL, SKIP_NO_BLOB, SHALLOW_HISTORY.

Exit codes: 0 all pins current, 1 drift or defect, 3 usage error (bad option,
unreadable index file, not inside a git repository).
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

USAGE = "usage: index_pins.py (--check | --write) [--root DIR] [--json PATH] [--sealed-state WORD] [<index.md> ...]"

LEAF_COLUMN_SUFFIXES = ("leaf",)
DEFAULT_SEALED_STATE = "SEALED"

_SHA40 = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
_HEX64 = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
# Loose match so a hash of the wrong length is still found and replaced in place
# instead of falling back to a whole-cell rewrite that would lose its prefix.
_LOOSE_HEX = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{20,}(?![0-9a-fA-F])")
# A cell counts as a pin only with a prefix and a fixed-length hex; bare hex,
# `sha256=` and commit ids mentioned in prose are text, not pins.
_PIN_GIT = re.compile(r"git:[0-9a-f]{40}(?![0-9a-fA-F])")
_PIN_SHA256 = re.compile(r"sha256:[0-9a-f]{64}(?![0-9a-fA-F])")
_PIN_PREFIX_HEX = re.compile(r"(git:|sha256:)([0-9a-fA-F]+)")
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_BACKTICKED = re.compile(r"`([^`]+)`")

DEFECTS = (
    "ROW_SHAPE_MISMATCH", "ORPHAN_PINNED_ROW", "SEALED_PIN_INVALID", "SEALED_PIN_MISSING",
    "SKIP_UNRESOLVED", "SKIP_UNTRACKED", "SKIP_NO_PATH_IN_CELL", "SKIP_NO_HASH_IN_CELL",
    "SKIP_NO_BLOB", "SHALLOW_HISTORY",
)


@dataclass
class Finding:
    index: str
    line: int
    prefix: str
    status: str
    leaf_raw: str | None = None
    leaf: str | None = None
    old_rev: str | None = None
    old_digest: str | None = None
    new_rev: str | None = None
    new_digest: str | None = None
    detail: str | None = None
    malformed: list[str] = field(default_factory=list)


class Repo:
    """A git work tree and the cached git queries the pins are computed from."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._commits: dict[str, str | None] = {}
        self._digests: dict[tuple[str, str], str | None] = {}

    def git_text(self, *args: str) -> tuple[int, str]:
        done = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        return done.returncode, done.stdout or ""

    def current_commit_for(self, leaf: str) -> str | None:
        """The commit that last changed the leaf; None when untracked or without history."""
        if leaf not in self._commits:
            code, out = self.git_text("log", "-1", "--format=%H", "--", leaf)
            sha = out.strip()
            self._commits[leaf] = sha if code == 0 and len(sha) == 40 else None
        return self._commits[leaf]

    def blob_sha256_at(self, commit: str, leaf: str) -> str | None:
        """sha256 of `git show <commit>:<leaf>` (repository bytes, not a git blob hash).

        Computed on raw bytes so a working-tree CRLF conversion can never change it.
        """
        key = (commit, leaf)
        if key not in self._digests:
            done = subprocess.run(["git", "show", f"{commit}:{leaf}"], cwd=self.root, capture_output=True)
            self._digests[key] = hashlib.sha256(done.stdout).hexdigest() if done.returncode == 0 else None
        return self._digests[key]

    def tracked_files(self) -> set[str]:
        code, out = self.git_text("ls-files")
        return set(out.splitlines()) if code == 0 else set()

    def shallow_boundary(self) -> set[str]:
        """Boundary commits of a shallow clone (their parents are not available locally).

        For every leaf last changed at or before the boundary, `git log -1` reports the
        boundary commit: right content, wrong revision. Such pins must not be produced.
        """
        code, out = self.git_text("rev-parse", "--is-shallow-repository")
        if code != 0 or out.strip() != "true":
            return set()
        code, gitdir = self.git_text("rev-parse", "--git-dir")
        if code != 0:
            return set()
        shallow_file = self.root / gitdir.strip() / "shallow"
        if not shallow_file.exists():
            return set()
        with io.open(shallow_file, encoding="utf-8") as handle:
            return {line.strip() for line in handle if line.strip()}


# ------------------------------------------------------------- table parsing


def split_row(line: str) -> list[str]:
    """Split `| a | b |` into cells, keeping each cell's raw text including padding."""
    stripped = line.rstrip("\r\n")
    if not stripped.lstrip().startswith("|"):
        return []
    body = stripped.strip()
    if body.endswith("|"):
        body = body[:-1]
    return body[1:].split("|")


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r"\s*:?-{2,}:?\s*", cell) for cell in cells)


def classify_columns(header_cells: list[str]) -> dict[str, dict[str, int]]:
    """Group header cells into {prefix: {"rev": i, "digest": j, "leaf": k}}.

    The state column (`state`, also `lifecycle`) belongs to the empty prefix. A group
    without all three of revision, digest and leaf is dropped.
    """
    groups: dict[str, dict[str, int]] = {}
    for position, raw in enumerate(header_cells):
        name = raw.strip().strip("`").lower()
        role: str | None = None
        prefix = ""
        if name.endswith("revision"):
            role, prefix = "rev", name[: -len("revision")].strip()
        elif name.endswith("digest"):
            role, prefix = "digest", name[: -len("digest")].strip()
        elif name in ("state", "lifecycle"):
            role, prefix = "state", ""
        else:
            for suffix in LEAF_COLUMN_SUFFIXES:
                if name == suffix or name.endswith(" " + suffix):
                    role, prefix = "leaf", name[: -len(suffix)].strip()
                    break
        if role:
            groups.setdefault(prefix, {})[role] = position
    return {prefix: group for prefix, group in groups.items() if {"rev", "digest", "leaf"} <= group.keys()}


def extract_path(cell: str) -> str | None:
    """Take a Markdown or JSON path from a leaf cell: link, backticks, then bare text."""
    suffixes = (".md", ".json")
    for pattern in (_MD_LINK, _BACKTICKED):
        match = pattern.search(cell)
        if match:
            candidate = match.group(1).strip()
            if candidate.lower().endswith(suffixes):
                return candidate
    match = re.search(r"(?:^|\s)([A-Za-z0-9_./-]+\.(?:md|json))(?:\s|$)", cell.strip(), re.IGNORECASE)
    return match.group(1) if match else None


def resolve_leaf(root: Path, index_file: Path, raw_path: str, tracked: set[str]) -> str | None:
    """Resolve a cell path to a tracked repo-relative path, repo-relative or index-relative."""
    # Strip `./` one prefix at a time: a character-set strip would turn `../x.md` into `x.md`.
    while raw_path.startswith("./"):
        raw_path = raw_path[2:]
    if raw_path.startswith(".."):
        relative = (index_file.parent / raw_path).resolve()
        try:
            posix = relative.relative_to(root).as_posix()
        except ValueError:
            return None
        return posix if posix in tracked else None
    if raw_path in tracked:
        return raw_path
    relative = (index_file.parent / raw_path).resolve()
    try:
        posix = relative.relative_to(root).as_posix()
    except ValueError:
        return None
    return posix if posix in tracked else None


def rewrite_cell(cell: str, strict: re.Pattern[str], new_value: str) -> str | None:
    """Replace only the hash inside a cell; None when the cell holds no hash at all."""
    match = strict.search(cell) or _LOOSE_HEX.search(cell)
    if match is None:
        return None
    return cell[: match.start()] + new_value + cell[match.end():]


# ------------------------------------------------------------------- scanning


def _looks_pinned(cells: list[str]) -> bool:
    return any(_PIN_GIT.search(cell) for cell in cells) and any(_PIN_SHA256.search(cell) for cell in cells)


def _malformed_pin_cells(cells: list[str]) -> list[str]:
    """Prefixed hex cells whose length or letter case is wrong for their prefix."""
    malformed: list[str] = []
    for number, cell in enumerate(cells, 1):
        for match in _PIN_PREFIX_HEX.finditer(cell):
            prefix, value = match.groups()
            expected = 40 if prefix == "git:" else 64
            if len(value) != expected or value != value.lower():
                malformed.append(f"cell {number} {prefix}{value}")
    return malformed


def scan(repo: Repo, index_file: Path, tracked: set[str], sealed_state: str = DEFAULT_SEALED_STATE) -> tuple[list[str], list[Finding]]:
    """Return (corrected lines, findings). Line endings and non-table text are untouched."""
    with io.open(index_file, encoding="utf-8", newline="") as handle:
        text = handle.read()
    lines = text.splitlines(keepends=True)
    root = repo.root
    rel_index = index_file.resolve().relative_to(root).as_posix()

    out = list(lines)
    findings: list[Finding] = []
    table_valid = False
    header_needs_separator = False
    groups: dict[str, dict[str, int]] = {}
    ncols = 0

    def add(
        lineno: int, status: str, prefix: str = "-", *,
        leaf_raw: str | None = None, leaf: str | None = None,
        old_rev: str | None = None, old_digest: str | None = None,
        new_rev: str | None = None, new_digest: str | None = None,
        detail: str | None = None,
    ) -> Finding:
        finding = Finding(
            index=rel_index, line=lineno + 1, prefix=prefix or "-", status=status,
            leaf_raw=leaf_raw, leaf=leaf, old_rev=old_rev, old_digest=old_digest,
            new_rev=new_rev, new_digest=new_digest, detail=detail,
        )
        findings.append(finding)
        return finding

    for lineno, line in enumerate(lines):
        cells = split_row(line)
        if not cells:
            groups, ncols = {}, 0
            table_valid, header_needs_separator = False, False
            continue
        if is_separator(line):
            if header_needs_separator:
                table_valid, header_needs_separator = True, False
            elif table_valid and groups:
                add(lineno, "ROW_SHAPE_MISMATCH",
                    detail=f"stray separator inside an index table body (header {ncols} columns, row {len(cells)})")
            continue
        next_is_separator = lineno + 1 < len(lines) and is_separator(lines[lineno + 1])
        if next_is_separator and (not groups or (not _looks_pinned(cells) and not _malformed_pin_cells(cells))):
            # A valid table starts at a header row, also when adjacent to another table.
            table_valid = False
            groups, ncols = classify_columns(cells), len(cells)
            header_needs_separator = True
            continue
        if not table_valid:
            if _looks_pinned(cells):
                add(lineno, "ORPHAN_PINNED_ROW", detail="pinned row outside a valid table")
            malformed = _malformed_pin_cells(cells)
            if malformed:
                add(lineno, "ORPHAN_PINNED_ROW", detail="MALFORMED_PIN: " + "; ".join(malformed))
            continue
        if not groups:
            continue
        if len(cells) != ncols:
            # Never skip silently: re-pinning a misplaced row would only lock the misplacement in.
            add(lineno, "ROW_SHAPE_MISMATCH", detail=f"header {ncols} columns, row {len(cells)}")
            continue

        state_col = groups.get("", {}).get("state")
        sealed_row = (
            state_col is not None and state_col < len(cells)
            and sealed_state.upper() in cells[state_col].upper()
        )

        for prefix, group in groups.items():
            if max(group.values()) >= len(cells):
                continue
            leaf_raw = extract_path(cells[group["leaf"]])
            if not leaf_raw:
                cell = cells[group["leaf"]].strip()
                if cell and cell not in {"-", "—", "–", "N/A", "n/a", "TBD"}:
                    add(lineno, "SKIP_NO_PATH_IN_CELL", prefix, leaf_raw=cell[:80])
                continue
            leaf = resolve_leaf(root, index_file, leaf_raw, tracked)
            match_rev = _SHA40.search(cells[group["rev"]])
            match_dig = _HEX64.search(cells[group["digest"]])
            old_rev = match_rev.group(0) if match_rev else None
            old_digest = match_dig.group(0) if match_dig else None
            if leaf is None:
                add(lineno, "SKIP_UNRESOLVED", prefix, leaf_raw=leaf_raw, old_rev=old_rev, old_digest=old_digest)
                continue
            if sealed_row:
                # A sealed pin stays at the sealing point: only verify, never rewrite.
                if old_rev is None or old_digest is None:
                    add(lineno, "SEALED_PIN_MISSING", prefix, leaf_raw=leaf_raw, leaf=leaf,
                        old_rev=old_rev, old_digest=old_digest)
                    continue
                actual = repo.blob_sha256_at(old_rev, leaf)
                if actual != old_digest:
                    add(lineno, "SEALED_PIN_INVALID", prefix, leaf_raw=leaf_raw, leaf=leaf,
                        old_rev=old_rev, old_digest=old_digest,
                        detail=f"sha256(git show {old_rev[:12]}:{leaf}) = {(actual or 'N/A')[:12]} differs from the recorded value")
                continue

            new_rev = repo.current_commit_for(leaf)
            if new_rev is None:
                add(lineno, "SKIP_UNTRACKED", prefix, leaf_raw=leaf_raw, leaf=leaf, old_rev=old_rev, old_digest=old_digest)
                continue
            new_digest = repo.blob_sha256_at(new_rev, leaf)
            if new_digest is None:
                add(lineno, "SKIP_NO_BLOB", prefix, leaf_raw=leaf_raw, leaf=leaf, old_rev=old_rev, old_digest=old_digest)
                continue
            if old_rev == new_rev and old_digest == new_digest:
                continue
            drift = add(lineno, "DRIFT", prefix, leaf_raw=leaf_raw, leaf=leaf, old_rev=old_rev,
                        old_digest=old_digest, new_rev=new_rev, new_digest=new_digest)

            for role, strict, label in (("rev", _SHA40, "git"), ("digest", _HEX64, "sha256")):
                raw = cells[group[role]]
                loose = _LOOSE_HEX.search(raw)
                if strict.search(raw) is None and loose is not None:
                    drift.malformed.append(f"{label} cell has an invalid length: {loose.group(0)[:70]}")

            rewritten_rev = rewrite_cell(cells[group["rev"]], _SHA40, new_rev)
            rewritten_digest = rewrite_cell(cells[group["digest"]], _HEX64, new_digest)
            if rewritten_rev is None or rewritten_digest is None:
                # The drift stays reported; the cell defect is a separate finding.
                add(lineno, "SKIP_NO_HASH_IN_CELL", prefix, leaf_raw=leaf_raw, leaf=leaf,
                    old_rev=old_rev, old_digest=old_digest)
                continue
            cells[group["rev"]], cells[group["digest"]] = rewritten_rev, rewritten_digest

        eol = "\r\n" if line.endswith("\r\n") else ("\n" if line.endswith("\n") else "")
        out[lineno] = "|" + "|".join(cells) + "|" + eol

    return out, findings


def index_candidates(root: Path, tracked: set[str]) -> list[Path]:
    """Tracked Markdown files with a header row that has revision and digest cells."""
    found: list[Path] = []
    for rel in sorted(tracked):
        if not rel.endswith(".md"):
            continue
        path = root / rel
        try:
            with io.open(path, encoding="utf-8", errors="replace") as handle:
                lines = handle.read().splitlines()
        except OSError:
            continue
        for position, line in enumerate(lines[:-1]):
            header = split_row(line)
            if not header or not is_separator(lines[position + 1]):
                continue
            names = {cell.strip().strip("`").strip().lower() for cell in header}
            if "revision" in names and "digest" in names:
                found.append(path)
                break
    return found


# ------------------------------------------------------------------------ CLI


def _usage_error(message: str | None = None) -> int:
    print(USAGE, file=sys.stderr)
    if message:
        print(f"index_pins.py: error: {message}", file=sys.stderr)
    return 3


def _toplevel(cwd: Path) -> Path | None:
    try:
        done = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
    except OSError:
        return None
    top = done.stdout.strip()
    return Path(top) if done.returncode == 0 and top else None


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return _usage_error()
    mode: str | None = None
    root_arg: str | None = None
    json_path: str | None = None
    sealed_state = DEFAULT_SEALED_STATE
    positional: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("--check", "--write"):
            if mode is not None and mode != arg:
                return _usage_error("--check and --write are mutually exclusive")
            mode = arg
            index += 1
        elif arg in ("--root", "--json", "--sealed-state"):
            if index + 1 >= len(args):
                return _usage_error(f"{arg} needs a value")
            if arg == "--root":
                root_arg = args[index + 1]
            elif arg == "--json":
                json_path = args[index + 1]
            else:
                sealed_state = args[index + 1]
            index += 2
        elif arg.startswith("-"):
            return _usage_error(f"unknown option {arg}")
        else:
            positional.append(arg)
            index += 1
    if mode is None:
        return _usage_error("one of --check or --write is required")
    root = _toplevel(Path(root_arg) if root_arg else Path.cwd())
    if root is None:
        return _usage_error("not inside a git repository")
    repo = Repo(root)
    tracked = repo.tracked_files()
    if not tracked:
        return _usage_error("git ls-files is empty: nothing is tracked")

    candidates: list[Path] = []
    for name in positional:
        path = Path(name).resolve()
        try:
            path.relative_to(repo.root)
        except ValueError:
            return _usage_error(f"{name} is outside the repository root")
        if not path.is_file():
            return _usage_error(f"cannot read {name}")
        candidates.append(path)
    if not positional:
        candidates = index_candidates(repo.root, tracked)

    all_findings: list[Finding] = []
    pending: list[tuple[Path, str]] = []
    for candidate in candidates:
        out, findings = scan(repo, candidate, tracked, sealed_state)
        all_findings.extend(findings)
        if any(finding.status == "DRIFT" for finding in findings):
            pending.append((candidate, "".join(out)))

    boundary = repo.shallow_boundary()
    grafted = sorted({
        finding.leaf for finding in all_findings
        if finding.new_rev in boundary and finding.leaf
    })
    if grafted:
        print("SHALLOW_HISTORY: these leaves would be pinned to the shallow boundary commit:")
        for leaf in grafted[:10]:
            print("    " + leaf)
        print(f"    ({len(grafted)} in total; fetch the full history and run again)")
        return 1

    changed_files: list[str] = []
    if mode == "--write":
        for candidate, text in pending:
            with io.open(candidate, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            changed_files.append(candidate.relative_to(repo.root).as_posix())

    drift = [finding for finding in all_findings if finding.status == "DRIFT"]
    defects = [finding for finding in all_findings if finding.status in DEFECTS]

    by_file: dict[str, int] = {}
    for finding in drift:
        by_file[finding.index] = by_file.get(finding.index, 0) + 1
    for name, count in sorted(by_file.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {count:3d}  {name}")
    for finding in drift:
        print(f"STALE {finding.index}:{finding.line} {finding.leaf}")
    print(f"drift={len(drift)} files={len(by_file)} defects={len(defects)} indexes={len(candidates)}")

    if defects:
        print(f"defects need manual repair ({len(defects)} rows):")
        for finding in defects[:40]:
            print(f"    {finding.index}:{finding.line}  {finding.status}  {finding.detail or finding.leaf_raw or ''}")
        if any(finding.status == "ROW_SHAPE_MISMATCH" for finding in defects):
            print("   Rows with a broken shape must be fixed first: re-pinning would lock the misplacement in.")

    if json_path:
        with io.open(json_path, "w", encoding="utf-8") as handle:
            handle.write(json.dumps([asdict(finding) for finding in all_findings], ensure_ascii=False, indent=2))

    if mode == "--write":
        print(f"rewrote={len(changed_files)}")
        return 1 if defects else 0
    return 1 if (defects or drift) else 0


if __name__ == "__main__":
    sys.exit(main())
