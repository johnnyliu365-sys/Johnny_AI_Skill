# Gate scripts

Three stand-alone Python 3.11 scripts that decide a workflow transition mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault (only
`receipt_fence_check.py`: the evidence root is not a readable directory), `3` usage
error. Each script prints a one-line `usage:` on stderr for exit `3`. A red is never
reported as a tool fault and a tool fault is never reported as a red.

## dispatch_lint.py

    python dispatch_lint.py <dispatch-file> [--chat-words WORD[,WORD...]]

Checks that a dispatch is machine-form. Rules: R1 first line is a field; R2 every line
outside a code fence is a field, list item, table row or indented continuation; R3 no
chat word outside quotes or backticks; R4 no full-width sentence terminator outside
quotes or backticks; R5 no line over 400 characters. Prints one line per violation,
then `LINT PASS` (exit 0) or `LINT FAIL (n)` (exit 1). The default chat-word list is
Chinese politeness and filler words; replace it with `--chat-words`.

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
- Exit 2: the evidence root (or the scan root) is not a readable directory. Exit 3: bad
  arguments, a heading that names no section, or an unreadable receipt or allowlist.

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
state contains the sealed word (default `SEALED`) are verified, never rewritten. With no
index argument every tracked Markdown file that has a `revision` and `digest` header is
scanned. Structural defects (rows with the wrong column count, pinned rows outside a
table, unresolved or untracked leaves, cells without a hash, a shallow clone whose
history would pin the boundary commit) exit 1. Exit 3: bad option, unreadable index
file, or not inside a git repository.
