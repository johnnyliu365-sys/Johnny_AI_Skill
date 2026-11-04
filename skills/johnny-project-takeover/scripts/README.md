# Gate scripts

Four stand-alone Python 3.11 scripts (`dispatch_lint.py`, `receipt_fence_check.py`,
`index_pins.py` and `contract_gate.py`) that decide a workflow transition mechanically.
They use only the standard library and carry no knowledge of any target project.

Exit codes are the same everywhere: `0` pass, `1` contract red, `2` tool fault, `3`
usage error. `dispatch_lint.py` reads one file and has no tool fault (`0`, `1`, `3`). In
`receipt_fence_check.py`, `index_pins.py` and `contract_gate.py` an unexpected error is
also a tool fault (`2`), never `1`. Each script prints a one-line `usage:` on stderr for exit `3`. A red is
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
