# Gate scripts

Seven stand-alone Python 3.11 scripts (`dispatch_lint.py`, `receipt_fence_check.py`, `index_pins.py`, `evidence_gate.py`, `requirement_snapshot.py`, `contract_gate.py` and `coverage_map.py`) that decide a workflow transition or keep a versioned record mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault, `3`
usage error. `dispatch_lint.py` reads one file and has no tool fault (`0`, `1`, `3`). In
`receipt_fence_check.py`, `index_pins.py`, `evidence_gate.py`, `requirement_snapshot.py`, `contract_gate.py` and `coverage_map.py` an unexpected error is also a tool fault
(`2`), never `1`. Each script prints a one-line `usage:` on stderr for exit `3`. A red is
never reported as a tool fault and a tool fault is never reported as a red; the wave-2 gates
report every red they can find even when a fault was met on the way (see each section). The console
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
the blob at `<candidate>:<path>` in `--repo`. `--evidence-root` defaults to the receipt's
directory. The receipt's own CRLF line endings are normalised; captures are not.

Exit 0 prints `cells=N defects=0`. Exit 1 prints one line `<code> <section>: <detail>` per
defect, then `cells=N defects=M`; a tool fault met on the way is printed on standard error, one
line each, beside the reds (red before fault: the gate reports every red it can find and exits `2`
only when it found none). Defect codes: `NO_CELLS`, `NOT_RUN` (a section without a
`cell:` line, or a `--require-cell` name with no run cell), `CELL_FIELD_MISSING`,
`STATEMENT_HAS_RUN_FIELDS`, `DUPLICATE_CELL`, `CANDIDATE_MISMATCH`, `TOOL_DIGEST_MISSING`,
`TOOL_DIGEST_STALE`, `CAPTURE_MISSING` (also a path that escapes the evidence root: an
absolute path, a drive letter, `..` leaving the root, a trailing slash), `CAPTURE_CR`,
`BLOCK_MISMATCH` (the lines between the fences joined with LF plus a final LF must equal the
capture byte for byte), `EXIT_MISMATCH` (the `exit:` list must equal the lines of the capture
that consist of `exit=N` alone, in order; `exit=N` inside a longer line does not count),
`FIELD_REPEATED` (a run cell holds a second `cell:`, `candidate:`, `tool_digest:`, `capture:`
or `exit:` line, or a second fence) and `CELL_NAME_MISMATCH` (the `cell:` value differs from
the `## ` heading). A `tool_digest` path is judged in two steps, and neither can turn a red into a tool fault.
First its form: a canonical path is non-empty, at most 1024 bytes in UTF-8, holds no control
character (U+0000 to U+001F, U+007F) or lone surrogate, uses only the forward slash as
separator (no backslash), does not start with a slash or a colon, has no drive letter and no
empty, `.` or `..` segment; any other path is `TOOL_DIGEST_STALE` and git is never asked about
it. Then one literal lookup from the repository root: the line `<candidate>:<path>` is
written to the standard input of `git cat-file --batch-check` (and, for a blob, of
`git cat-file --batch`), never passed to git as a pathspec or on its command line, so
existence and content come from the same lookup. A missing object, or one that is not a blob
(a tree, a submodule entry), is `TOOL_DIGEST_STALE`; a symbolic link is a blob and is read as
stored. A `missing` answer is told apart from an object the store cannot serve: the parent tree
is read through the same standard input, and an entry that tree names as a blob is a tool fault
(`2` when no red was found), while a path the tree does not name is `TOOL_DIGEST_STALE`. The listed values are judged before the lookup and whatever its outcome, because they need no git: a value
that is not 64 lower-case hex digits, and two different values listed for one path, are each
`TOOL_DIGEST_STALE` beside a fault on that lookup. Every
git child runs with `--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1` and `GIT_NO_LAZY_FETCH=1`,
with the repository-selecting `GIT_*` variables and the `GIT_CONFIG_*` variables removed, so a
replace ref never redirects a lookup and a lookup never fetches; `git` is started from the `PATH`
entries that are absolute directories, never from the current directory. The repository root is found from `--repo`, so it may be any directory inside the
repository. A string in the
receipt that holds a lone surrogate or a control character is a red (a capture reference is
`CAPTURE_MISSING`, a section or cell name is `NOT_RUN`), never a fault, and every printed
subject is escaped so one defect is always one line. Exit 2 (no red found): the receipt or a capture cannot be read, the evidence root is
not a directory, `git` cannot start, `--repo` is not a repository, the candidate cannot be
resolved, a blob the candidate names is missing from the
object store, `git cat-file` exits non-zero or answers outside its documented format (a failing
lookup is never read as an absent path), or an unexpected error; each fault message is escaped
to one line. A receipt that cannot be read ends the run at once, because no red can be found
without it. A `--tool` path that is not a blob at the candidate is a tool fault
on standard error and, because no receipt can list a digest for it, a `TOOL_DIGEST_MISSING` red in
every run cell, so it produces exit 1 and never exit 2 alone. Exit 3: a missing or unknown
argument, no `--tool`, a blank `--tool` or `--require-cell`, a `--tool` path that is not canonical, a `--candidate` that is not a
full 40-character lower-case sha. Output uses LF line endings.

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

JSON input: a repeated key in an object (a row or the top level) is `ROW_FIELD_TYPE`, and so are the
non-JSON constants `NaN`, `Infinity` and `-Infinity` anywhere in a file, as for other non-JSON input. Version
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

## contract_gate.py

    python contract_gate.py --repo DIR --snapshot FILE --specs DIR

Checks that every requirement has a spec and every spec is bound and honest. The
snapshot is a requirement snapshot file (a JSON object with a `rows` list whose rows
carry `requirement_id` and `status`, `active` or `retired`). A `requirement_id` is 1 to
128 characters from letters, digits, dot, underscore, colon, hyphen and slash, compared
exactly and never stripped. A key repeated in any object of the snapshot makes it not a
snapshot. `--repo` must be the top level of a git work tree: a subdirectory of one, or a
plain directory, is a tool fault. Every git child runs without the variables that pick a
repository, a work tree or an object store (the git directory, work tree, index file,
object directory, alternate object directories, namespace, ceiling directories, common
directory and prefix variables) and without the git configuration variables, so an
inherited one never changes the result. Every git child also ignores replace refs (the
no-replace-objects option and its variable) and never fetches lazily (the no-lazy-fetch
variable): a replace ref never redirects a lookup and a lookup never uses the network. The specs are
every file named `test_*.py` (case-sensitive) under `--specs`, a directory inside `--repo`;
symbolic links and Windows junctions under it are not followed. A spec declares its
contract in its first comment block, the leading run of lines that start with `#` (it ends
at the first line that does not):

    # requirement: <id>                          one or more, compared exactly
    # source: <repository path> sha256:<hex>    one or more, 64 lower-case hex
    # mutation: <name>                           one or more

Only the lower-case keys `requirement`, `source` and `mutation` are declarations; every
other comment line (`# Note: ...`, `# SPDX-License-Identifier: ...`, `# Requirement: ...`)
is free text and is ignored. Of a declared value only the spaces and tabs around it are
removed. A value that holds a control character (the C0 range or DEL) or a lone surrogate
is a red with the code of its key: `RETIRED_REQUIREMENT_BOUND` for a requirement,
`SOURCE_MISSING` for a source, `NO_MUTATION` for a mutation, each naming the line.

A spec is decoded the way Python decodes source: its coding declaration or UTF-8, with a
byte order mark honoured. The decoded text is what is parsed, analysed and quoted, so
offsets and text always agree. Everything derived from a spec's bytes (decoding, reading
the declarations, parsing, walking the tree, rendering a detail) runs inside one per-spec
guard: whatever exception it raises, it is a red of that spec, `LITERAL_EXPECTED` with a
detail saying the spec cannot be analysed and why. Only reading a file from disk and
running git can be a tool fault.

A source is repository-relative and must be canonical: backslashes are read as slashes and
one leading dot-slash is dropped, after which the path is not empty, is at most 1024 bytes
in UTF-8, holds no control character, has no leading slash or colon and no drive letter,
and has no empty, dot or dot-dot segment. A path that is not canonical is `SOURCE_MISSING`
naming the line. `HEAD` is resolved once, at the start of the run, to a full commit id, and
every lookup of the run is a line on the standard input of one `cat-file --batch` process
that asks for a full object id: a declared source is never a
pathspec, never an object name and never on a command line, so glob and pathspec-magic
characters match only themselves, the run reads one commit even if another lands while it
runs, and the digest is the same on every host whatever its line-ending settings. The gate
reads the commit, takes the root tree from its `tree` line, walks the trees from the root by
object id and reads the entry of a source from its parent tree. A tree
that does not name the path, or names a directory in its place, makes it `SOURCE_MISSING`
(names match exactly, including case); so does an entry that is a symbolic link or a
submodule, because a contract cites the content of a file and a link can keep pointing at
a path whose content changes ("not a regular file"). A file entry, executable or not, is
digested over its blob. An object that a tree names and the object store cannot serve (a
pruned blob or tree, a partial clone that is missing a blob; nothing is fetched) is not a
red but a fault, reported as `SOURCE_UNSERVABLE` for a source and as a tool fault otherwise.

Every object the gate reads is hashed by the gate against the id it asked for: the header
`<type> <size>`, a NUL byte and the body, with SHA-1 or SHA-256 chosen by the width of the id.
An object that does not hash to its id (a forged or damaged loose object, an object served
through alternates) is a tool fault naming the id: it is never a red and never a pass, and
the object store is not used again in the run. A repository whose ids are SHA-256 is read the
same way.

Defects, one line `<code> <spec or requirement>: <detail>` each on stdout, the subject and
the detail escaped so that a line break, a control character, U+2028 or a lone surrogate
cannot split or forge a line:
`NO_SPEC_FOR_REQUIREMENT` (an active requirement no spec declares), `SOURCE_MISSING`
(a source that is not canonical, not a regular file at `HEAD`, or not named by its parent
tree, a declaration line that is unusable, or a spec that declares a requirement but no
source), `SOURCE_DIGEST_MISMATCH` (sha256 of the blob differs), `RETIRED_REQUIREMENT_BOUND`
(a spec declares a requirement that is retired or absent from the snapshot, or an empty
`requirement:`), `LITERAL_EXPECTED` (an `assert` comparing with a number, string, bytes or
a display of such constants, on either side of any comparison of a chain, also inside `and`,
`or`, `not`; a signed number counts, a signed `True` does not; `None`, `True` and `False` do
not count; also a spec that does not parse or cannot be decoded, and an assertion the gate
cannot analyse within its limits, such as a very deep nesting; the detail is the source text
of the assertion, cut to 120 characters) and `NO_MUTATION` (a spec that declares a
requirement has no mutation, or an empty `mutation:`).

The rule is red before fault. The gate reports every red it can find and exits 1 if there is one: the
defect lines go to stdout, each fault goes to stderr on one line (`SOURCE_UNSERVABLE` for a
URL source or a source the object store cannot serve, a tool fault line for the rest), and
the summary comes last on stderr. A fault never drops a red and a red never hides a fault.
It exits 2 only when it found no red, and it prints no summary then. A source that is a URL
cannot be verified offline: it is a fault, and the rest of its spec is still checked. A
spec that cannot be read is a fault; since it may declare any requirement, no requirement
is then called unbound (`NO_SPEC_FOR_REQUIREMENT` is withheld). After a failure of git the
remaining lookups are skipped, with one fault line, and everything that needs no lookup is
still reported. A fault that leaves nothing to check ends the run at once with exit 2 and no summary: the
snapshot cannot be read, `--specs` or `--repo` is not a directory, `--repo` is not the top
level of a git work tree, or git cannot be run to ask that. Git failing to resolve `HEAD`
(no commit) is collected like the others, and its fault names the cause (`HEAD does not name
a commit`).

Exit 0 prints `requirements=N specs=M defects=0` on stdout (N counts snapshot rows). Exit 1
prints the defect lines on stdout, then each fault line and the same summary on stderr. Exit
2 (no red found): the snapshot, a spec or a directory cannot be read, `--specs` or `--repo`
is not a directory, `--repo` is not the top level of a git work tree, git cannot serve a
query (git missing, no commit at `HEAD`, a failure, an answer outside its format, no answer
within the time limit), a source is a URL or cannot be served, or an unexpected error. A red
is never reported as a fault and a fault is never reported as a red. Exit 3: bad arguments,
`--specs` outside `--repo`, or a snapshot argument that is not a snapshot (not JSON, a
repeated key, no `rows`, a row whose `requirement_id` is outside the character set above or
with a `status` other than `active` or `retired`, a repeated `requirement_id`); a usage error
prints the usage banner and one escaped error line. Fault and usage messages are escaped to
one line as well.

## coverage_map.py

    python coverage_map.py --repo DIR --base COMMIT --candidate COMMIT --map PATH --specs DIR

Checks that no test function leaves a spec file without a map row. It lists every test
present in a spec file under `--specs` at `--base` and absent at `--candidate`, and requires
each to have a row in the map file at `--candidate`. The map is read as the blob of the
candidate commit (git `ls-tree` finds the entry, `cat-file` reads it), never from the working
tree.

`--repo` must be the top level of a git work tree: a plain directory, or a subdirectory of a
work tree, is exit 2. `--specs` must name a directory at `--base`, at `--candidate`, or at
both; a path that names no directory at either commit (a typo, a file, a case variant) is
a fault naming the path and both commits, because a guard that checks nothing must not pass.
A directory present at one commit only is read as empty at the other, and a present
directory that holds no spec file is exit 0. Directories are listed, not inferred from the
files below them: git is asked for the tree entries themselves, so an empty tree object at
`--specs` is a present, empty directory.

A spec file is a regular file (git mode 100644 or 100755) named `test_*.py` below `--specs`,
matched by path component (a sibling directory whose name only begins like `specs` is not
below it). A symbolic link or a submodule entry is not a spec file and is never parsed; a
spec file that becomes a link at the candidate has all its tests removed. Paths from git are
decoded as UTF-8 with surrogateescape, so a path that is not UTF-8 is still a test id,
compared byte for byte and printed escaped, never a tool fault. A test is a function, sync or
async, whose name starts with `test`, at module level or inside a class (nested classes
included), also inside the `if`, `else`, `try`, `except`, `finally`, `with`, `for`, `while`
and `match` blocks of those levels, never inside another function. Its id is `<path>::<name>`,
`<path>::<Class>::<name>` or `<path>::<Outer>::<Inner>::<name>`. A test that moved to another
file or was renamed is removed under its old id. Specs are parsed with the standard `ast`
module and the grammar of the interpreter that runs the guard (Python 3.11); a spec written
with later syntax does not parse and is exit 2.

Map file, UTF-8 JSON:

    {"rows": [{"assertion": "<id>", "disposition": "carried" | "dropped" | "escalated",
               "carried_to": "<id or empty>", "reason": "<text or empty>", "ticket": "<text or empty>"}]}

Every string in a row is valid Unicode without lone surrogates and without control
characters (U+0000 to U+001F, U+007F); a row that breaks this is `MAP_ROW_INVALID`, so a map
cannot name a test whose path is not UTF-8 and such a removal is `UNMAPPED_REMOVAL`.

Defect codes (exit 1): `UNMAPPED_REMOVAL` (a removed id has no valid row; also every removed
id when the map is absent at the candidate), `CARRIED_TARGET_MISSING` (`carried_to` empty or
naming no test at the candidate), `DROPPED_WITHOUT_REASON` (`dropped` with an empty or
whitespace-only `reason`), `ESCALATED_WITHOUT_TICKET` (`escalated` with an empty or
whitespace-only `ticket`), `MAP_ROW_INVALID` (an unknown disposition, a missing or non-string
field, a string with a control character or lone surrogate, an assertion that is empty or has
surrounding whitespace, or a duplicate assertion; a row that is invalid or duplicated covers
nothing, so the removed id it names also gets `UNMAPPED_REMOVAL`). The subject of a
`MAP_ROW_INVALID` line is `rows[N]` (the zero-based position of the row) for a row defect, or the map
path for a defect of the file: a map file that is not UTF-8 JSON of the required shape, or a
map path that names a directory (an empty tree object included), a submodule entry or a link. A
key given twice in any object of the map file is `MAP_ROW_INVALID` as well: for the row
(`rows[N]`, which then covers nothing) when a row holds it, for the map path when the top level
or anything beside `rows` does. A map absent at the candidate is
not itself a defect. A row's disposition is judged only when its assertion is a removed id;
every row is shape-checked.

Output is one line per defect (`CODE "<subject>" <detail>`, subjects JSON-quoted with ASCII
escapes), then `removed=N defects=M`; exit 0 only when `defects=0`. A defect or a fault is
always one line: stderr messages are escaped to printable ASCII, so an argument, a path or a
parser message that holds a newline is never echoed raw. Exit 2, only when no red was found:
`git` cannot be started, `--repo` is not a work-tree top level, a commit, tree or blob cannot
be served (git's stderr is printed escaped), `--specs` names no directory at either commit, a
spec does not parse at either commit (the message names the commit and the path), or an
unexpected error. Red before fault: the guard reports every red it can find and exits 1 when
there is one, printing each fault it met on stderr, one line each; a spec file it cannot read
is judged by nothing, so a fault never invents a red. Every git child runs without the
variables that select another repository (git directory, work tree, index file, object
directory, alternate object directories, namespace, ceiling directories, common directory,
prefix) and without the `GIT_CONFIG_*` variables, so an exporting hook cannot point the guard
elsewhere; it also runs with `--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1` and
`GIT_NO_LAZY_FETCH=1`, so a replace ref never changes the blob read at a commit and a lookup
never fetches over the network; `GIT_GRAFT_FILE` names a path that does not exist (an
inherited value is dropped first), so neither `info/grafts` nor an inherited graft file moves a
parent and `--base main^` means what the commit objects say. Exit 3: a
missing or unknown option, an empty value, an argument that holds a lone surrogate or a
control character, an absolute `--map` or `--specs`, a `..` segment, or a revision that
starts with `-`. `--specs` and `--map` accept forward or back slashes and a trailing slash;
`--specs .` selects the whole repository.
