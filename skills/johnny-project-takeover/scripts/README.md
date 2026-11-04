# Gate scripts

Four stand-alone Python 3.11 scripts that decide a workflow transition mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault, `3`
usage error. `dispatch_lint.py` reads one file and has no tool fault (`0`, `1`, `3`).
`preflight.py` has no red (`0`, `2`, `3`). In
`receipt_fence_check.py` and `index_pins.py` an unexpected error is also a tool fault
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

## preflight.py

    python preflight.py <dispatch-file> [--timeout SECONDS]

Checks that every tool a dispatch names starts and serves before any product edit. The
dispatch file carries one `preflight:` block: the key starts at column 0 and the block
ends at the next line that starts at column 0. Each item is four lines, and every value is
one JSON value on its own line (a JSON string for `tool` and `expect`, a JSON array of
strings for `start` and `probe`):

    preflight:
      - tool: "<name>"
        start: ["<argv0>", "<arg>", ...]
        probe: ["<argv0>", "<arg>", ...]
        expect: "<substring>"

`start` runs to completion first, `probe` runs after it. Both run without a shell, with an
empty stdin and the dispatch file's directory as working directory, each bounded by
`--timeout` (default 120 seconds, above 0 and at most 86400); a command that exceeds it is
killed together with the processes it started. Tools that start and exit are supported;
long-running servers are not. A tool is served when `start` exits 0 and `probe` exits 0
with `expect` in its output (stdout and stderr, decoded with replacement, compared exactly
and case-sensitively). Every tool is tried and every failing tool is reported.

Exit 0 prints `tools=N served=N`. Exit 2 prints one line `TOOL_UNSERVED <tool>: <cause>` per
failing tool; the causes are `start cannot be launched`, `start exited with code N`,
`start timed out`, `probe cannot be launched`, `probe exited with code N`, `probe timed
out` and `probe output does not contain the expected text`. Exit 2 is also an unreadable
dispatch file or an unexpected error. Exit 3: bad arguments, no `preflight:` block, a block
that does not follow the grammar (a missing, repeated or unknown key, a key at the wrong
indent, a value that is not one JSON value of the right type, an empty argument array, an
empty `tool` or `expect`), a file that is not UTF-8, or a string that holds a lone
surrogate or a control character. Every printed subject is escaped so one defect is one
line.
