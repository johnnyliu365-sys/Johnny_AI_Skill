# Gate scripts

Four stand-alone Python 3.11 scripts that decide a workflow transition or keep a versioned record mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault, `3`
usage error. `dispatch_lint.py` reads one file and has no tool fault (`0`, `1`, `3`). In
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

## requirement_snapshot.py

    python requirement_snapshot.py take --source NAME --input ROWS.json [--root DIR] [--taken-at ISO-8601-UTC]
    python requirement_snapshot.py verify SNAPSHOT.json
    python requirement_snapshot.py diff --source NAME VA VB [--root DIR]

Keeps versioned requirement snapshots, one JSON file per source and version,
`<root>/<source>/<date>-v<n>.json` (default root `doc/requirements/snapshots`). A file holds
`source`, `taken_at`, `source_sha256` (sha256 of the canonical JSON of the rows: keys sorted,
separators `,` and `:`, UTF-8, rows sorted by `requirement_id`; `taken_at` is not part of it)
and `rows`. A row has `requirement_id` (unique; 1 to 128 characters from letters, digits,
dot, underscore, colon, hyphen and slash), `page_id`, `title`, `type`,
`source_ref` (URL or repository-relative path, never a host absolute path), `source_sha256`
(64 lower-case hex), `status` (`active` | `retired`) and `version` (integer >= 1). The file is
written with LF and a final LF.

- `take` reads `{"rows": [...]}` and writes the next version (the highest published version plus
  one, whatever the date); when the rows equal the latest
  version's rows it writes nothing and prints `<path> unchanged`. A snapshot file is never
  overwritten or edited: it is written to a temporary name in its own directory and then created
  exclusively under its final name, so a write failure leaves no partial file and a race exits 2.
  `--taken-at` must be a UTC instant; it defaults to now.
- `verify` checks the shape of one file and that `source_sha256` matches its rows.
- `diff` prints `added`, `removed` and `changed` requirement ids, one per line, from version `VA`
  to version `VB` (`v1` or `1`); exit 0.

Version numbers and claim files: a version number is unique per source whatever the date. Before it
publishes, `take` claims the number by creating `<root>/<source>/.v<n>.claim` exclusively,
re-scans the published files, and if a published file already carries version `n` or higher it
removes its claim and exits 2 (another writer won); otherwise it publishes `<date>-v<n>.json`
exclusively and removes the claim. A claim it cannot create, and any claim file left behind by a
crash, are exit 2 naming the claim file; the owner removes a stale claim by hand once no `take`
runs. **Target projects must ignore `.v*.claim` (for example in `.gitignore`); claim files are
never committed.**

Text values: every string read from an input is valid Unicode without lone surrogates and without
control characters (U+0000 to U+001F, U+007F). A string that breaks this is a red of the input
(`ROW_FIELD_TYPE`, exit 1), never a tool fault. Every subject printed in a defect line, and every
id printed by `diff`, is escaped (Python `repr`) unless it is plain, so one defect is one line.
A raw value echoed in a defect detail is escaped the same way. A top-level `source` or
`source_sha256` that breaks the rule is `ROW_FIELD_TYPE` as well as its format code, as for row
fields.

JSON input: a repeated key in an object (a row or the top level) is `ROW_FIELD_TYPE`. Version
numbers in file names, claim file names and arguments are ASCII digits only. A version argument
with more digits than a file name can hold names no stored version: `diff` reports that the
requested version does not exist (exit 2 unless a red was found), never a raw exception text.

Printed lines: every line the tool prints, the usage line and the success and `unchanged` lines
included, is escaped to one line like defect and fault lines: a control or line-break character is
shown as a backslash escape. Repeated-key collection is linear in the number of keys.

Red before fault: a command checks everything it can before it decides the exit. If it found any
red it prints every red on stdout and exits 1; a fault met on the way is printed on stderr, on one
line, and does not change the exit. It exits 2 only when it found no red and a fault stopped it.
So `diff` of a damaged version and a missing version prints the digest mismatch and exits 1, with
the missing version on stderr. The same holds for `take` and `verify`. Check order in `take` and
`diff`: argument grammar (exit 3), then the name rules on `--source`, then version lookups (an
over-long version argument in either position is a version that does not exist), then reading and
checking the stored files.

Defect codes, printed one per line as `<code> <requirement_id or field>: <detail>`:

- `ROW_FIELD_MISSING`.
- `ROW_FIELD_TYPE`: a field of the wrong type, an unexpected field, a blank `requirement_id`, a
  `requirement_id` that is not 1 to 128 characters from letters, digits, dot, underscore, colon, hyphen and slash, a string that
  breaks the text-value rule, input that is not JSON or has no `rows` list.
- `DUPLICATE_REQUIREMENT`, `STATUS_UNKNOWN`, `DIGEST_FORMAT`.
- `SOURCE_REF_ABSOLUTE`: a `source_ref` that is empty, starts with a slash, a backslash or `~`, carries
  a drive letter or `file:`, or has a `..` segment; a URL with a scheme is allowed.
- `SNAPSHOT_DIGEST_MISMATCH`: a stored version whose `source_sha256` does not match its rows.
  `verify` reports it, and `take` and `diff` report it whenever they read that version (exit 1).
- `NAME_INVALID`: a source name with a path separator, `..`, a character outside
  `[A-Za-z0-9._-]`, a trailing dot, a Windows reserved device name (`CON`, `PRN`, `AUX`, `NUL`,
  `COM1` to `COM9`, `LPT1` to `LPT9`, with or without an extension), or a case variant of an
  existing source directory: an existing entry collides with the source name only when the entry is
  ASCII and equal to the name ignoring ASCII letter case, and a non-ASCII entry never collides (the
  file system keeps it distinct). `take` and `diff` apply every name rule, the case-variant rule
  included, because they know the root. `verify` takes a single file and applies the name rules to
  the file's `source` value only: not the case-variant rule, and no comparison with the directory
  the file sits in.

A red exits 1 and `take` then writes nothing. Exit 2, only when no red was found: the root cannot be created or written, the
input or a snapshot cannot be read, a requested version does not exist, a version exists twice, a
claim file exists or a version was published by another writer while `take` was working, a target
appeared while writing, or a programming error no input can produce. Exit 3: bad arguments.

Errors that may still end the run at once with exit 2: a file system error, a missing or duplicated
version, a lost version race or a stale claim, and a programming error that no input can produce.
A failure derived from the bytes of an input or of a stored version, nesting too deep for the JSON
parser included, is never one of them: it is a red of that file, `ROW_FIELD_TYPE`, with the code a
non-JSON file gets.
