# Gate scripts

Four stand-alone Python 3.11 scripts that decide a workflow transition mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault, `3`
usage error. `dispatch_lint.py` reads one file and has no tool fault (`0`, `1`, `3`). In
`receipt_fence_check.py`, `index_pins.py` and `evidence_gate.py` an unexpected error is also a tool fault
(`2`), never `1`. Each script prints a one-line `usage:` on stderr for exit `3`. A red is
never reported as a tool fault and a tool fault is never reported as a red. The console
encoding never changes an exit code: each script keeps the encoding the host chose for
stdout and stderr but escapes any character it cannot encode as a backslash sequence, so a red whose
text holds such a character still exits `1` under a cp950 console.

## dispatch_lint.py

    python dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]]

Checks that a dispatch is machine-form. Rules: R1 first line is a field; R2 every line
outside a code fence is a field, list item, table row or indented continuation; R3 no
chat word outside quotes or backticks; R4 no full-width sentence terminator outside
quotes or backticks; R5 no line over 400 characters. Prints one line per violation,
then `LINT PASS` (exit 0) or `LINT FAIL (n)` (exit 1). The default chat-word list is
Chinese politeness and filler words; replace it with `--chat-words`, which needs at
least one non-blank word. Exit 3: missing or extra argument, unknown option, a file that
cannot be read or is not UTF-8, an empty or blank `--chat-words` list.

## receipt_fence_check.py

    python receipt_fence_check.py <receipt> <heading> <evidence-root> [--no-moving-ref]
        [--self-note] [--authority-root PATH] [--legacy-allowlist FILE]
    python receipt_fence_check.py --scan <dir> [--authority-root PATH] [--legacy-allowlist FILE]

Verifies that each code fence in a receipt section is backed by a capture file. A fence
needs a `capture: <file>` line within three lines above it, normally preceded by a
`cmd: <command>` line whose redirect targets that capture. Failure codes include
`FENCE_CAPTURE_MISSING`, `CMD_MISSING`, `CMD_PLACEHOLDER`, `CMD_NO_REDIRECT`,
`AMBIGUOUS_TARGET`, `CMD_MOVING_REF`, `CAPTURE_MISSING`, `CAPTURE_OUTSIDE_EVIDENCE`,
`BODY_MISMATCH`, `ELISION_MISSING`, `UNCLOSED_FENCE` and `LEGACY_UNCLAIMED_EXIT`. The
last line is `fences=N failures=M`; exit 0 only when `failures=0`.

- `--authority-root PATH`: an absolute path prefix under which the receipt was
  recorded; it is mapped onto the current working directory when comparing redirect
  targets. A section may also declare `authority_root=<path>` on its own line.
- `--legacy-allowlist FILE`: tab-separated `receipt<TAB>heading<TAB>capture-basename`
  rows (`#` starts a comment) that may end with a bare `exit=N` line although the
  `cmd:` line never mentions `exit=`.
- A section may declare `EVD=<dir>` on its own line; a redirect target that starts with
  the EVD variable (shell, braced, PowerShell environment or percent-delimited
  spelling) then resolves through that directory.
- Exit 2: the evidence root (or the scan root) is not a readable directory, or an
  unexpected error. Exit 3: bad arguments, a heading that names no section, or an
  unreadable receipt or allowlist.

## index_pins.py

    python index_pins.py (--check | --write) [--root DIR] [--json PATH]
        [--sealed-state WORD] [<index.md> ...]

Recomputes and checks the pins of Markdown index rows. A row pins a leaf with a
revision (`git log -1 -- <leaf>`) and a digest (sha256 of `git show <revision>:<leaf>`):

    | id | kind | state | revision    | digest         | leaf    |
    | -- | ---- | ----- | ----------- | -------------- | ------- |
    | a1 | spec | open  | git:<sha>   | sha256:<hex>   | path.md |

`--check` reports stale rows (`STALE <index>:<line> <leaf>`) and exits 1; `--write`
rewrites only the two pin cells in place and keeps line endings and spelling. Rows whose
state cell, stripped, equals the sealed word (default `SEALED`, case-insensitive) are
verified, never rewritten; `--sealed-state` must not be empty or blank. With no index
argument every tracked Markdown file that has a `revision` and `digest` header is
scanned. Structural defects (rows with the wrong column count, pinned rows outside a
table, unresolved or untracked leaves, cells without a hash) exit 1.
A git failure that stems from the environment (`git log -1 -- <leaf>`,
`git ls-files`, the single shallow-boundary `git rev-parse`, or `git show <revision>:<leaf>`
failing although the revision and its tree check out) is a tool fault, exit 2 with git's
message, never `SKIP_UNTRACKED`. A failure that stems from an index row or the work tree is
a red, exit 1: the script checks that the recorded revision is a commit and that its tree
lists the leaf before it reads the blob, so a sealed row failing either check is
`SEALED_PIN_INVALID` and an open row whose tracked leaf is absent from the tree of its last
commit is `SKIP_NO_BLOB`. The recorded revision of a sealed row that is missing in a shallow
repository is `SHALLOW_HISTORY` (exit 2), read through the common git directory so a linked
work tree of a shallow clone raises it too, while in a complete repository it stays
`SEALED_PIN_INVALID`. An open row never needs its recorded revision object: a stale open row
whose recorded revision predates the boundary is still `STALE` (exit 1) and `--write` repairs
it; only an open row whose leaf's current revision lies beyond the boundary is
`SHALLOW_HISTORY`. Exit 2: a shallow clone whose history would pin the boundary
commit (`SHALLOW_HISTORY`), `git` cannot be started, not inside a git repository, `--root`
is missing or not a directory, an environment git query fails as above, the `--json` path
cannot be written, or an unexpected error. Exit 3: bad option, missing mode, empty
`--sealed-state`, an index argument that is not a file, or an index file that is not UTF-8.

## evidence_gate.py

    python evidence_gate.py <receipt> --repo DIR --candidate SHA --tool PATH [--tool PATH ...]
        [--require-cell NAME ...] [--evidence-root DIR]

Checks that a receipt proves every run cell. A run cell is a `## <name>` section with the
lines `cell: <name>`, `candidate: <full sha>`, `tool_digest:` followed by
`- <repository-relative path>=<sha256>` lines, `capture: <path relative to the evidence
root>` and `exit: <comma-separated exit codes in capture order>`, then the capture in one
four-backtick fence. A section with `cell: STATEMENT` is informational and has no
`capture:`, `exit:` or fence. `--candidate` is the full lower-case commit sha every cell must
name; each `--tool` path must be listed in every run cell with the sha256 of
`git show <candidate>:<path>` in `--repo`. `--evidence-root` defaults to the receipt's
directory. The receipt's own CRLF line endings are normalised; captures are not.

Exit 0 prints `cells=N defects=0`. Exit 1 prints one line `<code> <section>: <detail>` per
defect, then `cells=N defects=M`. Defect codes: `NO_CELLS`, `NOT_RUN` (a section without a
`cell:` line, or a `--require-cell` name with no run cell), `CELL_FIELD_MISSING`,
`STATEMENT_HAS_RUN_FIELDS`, `DUPLICATE_CELL`, `CANDIDATE_MISMATCH`, `TOOL_DIGEST_MISSING`,
`TOOL_DIGEST_STALE`, `CAPTURE_MISSING` (also a path that escapes the evidence root: an
absolute path, a drive letter, `..` leaving the root, a trailing slash), `CAPTURE_CR`,
`BLOCK_MISMATCH` (the lines between the fences joined with LF plus a final LF must equal the
capture byte for byte), `EXIT_MISMATCH` (the `exit:` list must equal the lines of the capture
that consist of `exit=N` alone, in order; `exit=N` inside a longer line does not count),
`FIELD_REPEATED` (a run cell holds a second `cell:`, `candidate:`, `tool_digest:`, `capture:`
or `exit:` line, or a second fence) and `CELL_NAME_MISMATCH` (the `cell:` value differs from
the `## ` heading). A `tool_digest` path is checked for form before git is asked: an absolute
path, a drive letter, a `..` segment, a leading `:` (pathspec magic), an empty path or a path
with a control character is `TOOL_DIGEST_STALE`; a well-formed path is read from the
repository root, so `--repo` may be any directory inside the repository. A string in the
receipt that holds a lone surrogate or a control character is a red (a capture reference is
`CAPTURE_MISSING`, a section or cell name is `NOT_RUN`), never a fault, and every printed
subject is escaped so one defect is always one line. Exit 2: the receipt or a capture cannot be read, the evidence root is
not a directory, `git` cannot start, `--repo` is not a repository, the candidate or a
`--tool` path cannot be read from it, or an unexpected error. Exit 3: a missing or unknown
argument, no `--tool`, a blank `--tool` or `--require-cell`, a `--candidate` that is not a
full 40-character lower-case sha. Output uses LF line endings.
