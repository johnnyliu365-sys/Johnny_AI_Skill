# Gate scripts

Stand-alone Python 3.11 scripts that decide a workflow transition mechanically.
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

## repair_guard.py

    python repair_guard.py --repo <dir> --repair <commit> --dispatch <dispatch-file>

Checks that a tool-repair commit stays inside what its dispatch allows. The dispatch
carries two lines that start at column 0, each holding one JSON array of strings:

    repair_allowlist: ["<repository-relative path or directory/>", ...]
    protected_paths: ["<repository-relative path or directory/>", ...]

An entry ending in a slash covers that directory and everything under it, by whole path
segment; any other entry is one exact path. The directory this script lives in (the gate
scripts) is always protected, whether or not `protected_paths` names it.

History comes from raw objects, and the guard hashes every one of them itself. It resolves
the repair commit to its object id, then reads the repair commit, its first parent, both
root trees and every subtree it descends into raw through `git cat-file --batch` (the ids on
standard input, replace refs off) and computes each object's hash (the header `<type>
<size>`, a NUL byte, the body; SHA-1 or SHA-256 by the width of the ids). An object whose
hash differs from its id, whose type is not the expected one, or that the store cannot serve
is a fault naming the id, so a forged loose object, an object served through alternates or a
damaged store can never turn a forbidden change into a pass. The tree and the parents are the
ones the verified commit names, so a graft file, a replace ref, a shallow file or a
commit-graph cannot change which parent or which trees are compared. A merge is recognised
from its parent lines; a root commit is compared against the empty tree, which needs no
object; a first parent the object store cannot serve is a fault. The revision given to
`--repair` names a commit by id or by reference; a name with an ancestry or path operator
(a caret, a tilde, a colon or an at-brace) is a usage error, because git answers those
through the history that grafts rewrite. Entries are never decoded or normalised.

The changed paths come from the guard's own walk of the two root trees, not from `git
diff`: it compares them entry by entry, reads a subtree only when its two ids differ, and
reports every path whose entry differs in id or mode or exists on one side only. A
directory that exists on one side only, or that turns into a file (or the reverse), is
listed file by file; a rename is a deletion and an addition, so it counts on both sides. A
submodule pointer (mode 160000) is compared by id and never descended.

What counts, whatever the repository says:

- A moved submodule pointer always counts. The walk compares a pointer by id like any other
  entry, so no ignore setting (a tracked submodule list, a repository setting), external
  diff driver or text conversion can hide it.
- Replace refs are ignored. The environment variables that select a repository, history
  or settings (the git directory, the common directory, the work tree, the index file, the
  object directory, the alternate object directories, the namespace, the ceiling
  directories, the graft file, the shallow file, the replace ref base and every
  configuration variable) are removed from every git child, which runs with replace objects
  and lazy fetching switched off.

Case on Windows is compared in the direction that fails closed. An allowlist entry covers a
path when the two are equal ignoring ASCII case only; a non-ASCII character must match
exactly, so the allowlist never grows beyond what the file system treats as one name. A
protected entry and the gate script directory cover a path when the two are equal under
full Unicode case folding, so protection never shrinks (a path spelled with a German sharp
s is covered by a protected entry spelled with two letters s, and the other way round).
Elsewhere case matters.

The dispatch file is read as UTF-8 with surrogate escapes; one byte order mark at the very
start is removed first. An undecodable byte or a raw control character on a block line,
inside or outside a JSON string, is a `TEXT_VALUE_INVALID` red. The same on any other line
is ignored. A block line that is not one JSON array of strings for any other reason is a
usage error. A line ending in two carriage returns holds a raw control character and is a
text red. A block that holds a text defect has its entries cut off: none of them is used
(a defective allowlist judges no path as outside; a defective protected list protects
nothing but the gate scripts), while the other, clean block is used as usual. Every rule
that needs no entry still applies, so a change to a gate script is reported as
`PROTECTED_PATH_TOUCHED` next to the text red.

Output: one line per defect, `CODE 'subject'` with the subject escaped by Python `repr`
so a defect is always one line; on exit 0 only `paths=N defects=0`.

- `OUTSIDE_ALLOWLIST`: a changed path is covered by no allowlist entry.
- `PROTECTED_PATH_TOUCHED`: a changed path is covered by a protected entry or by the gate
  scripts, even when the allowlist also covers it. A path that is both outside the allowlist
  and protected is reported under both codes.
- `REPAIR_NOT_SINGLE_PARENT`: the repair commit is a merge or a root commit.
- `TEXT_VALUE_INVALID`: a string read from the dispatch file or from git (an entry, a
  block line, a changed path) holds a lone surrogate, an undecodable byte or a control
  character.

Red before fault: the guard reports every red it can find and exits 1 when there is one,
with any fault printed on one line on standard error; it exits 2 only when it found no red.
The paths are judged level by level while the walk goes down, as soon as the trees of a
level have been verified: a red at a level that did verify is reported beside a fault met
deeper (or beside a tree of the same level that did not verify), and the paths of a tree
that did not verify are never judged.
Exit 2: git cannot serve the check (unknown commit, `--repo` not a repository or not its
top level, a first parent the object store lacks as in a shallow clone, an object whose hash is
not its id, git missing), the
dispatch file is unreadable, an unexpected error, or standard output cannot be written
(then no verdict can be delivered, so this wins over a red), or standard error cannot be
written when there is no red. When every red reached standard output and only standard
error fails, the exit stays 1. git's message is printed on one line. Exit 3:
bad arguments (a control character or a lone surrogate in an argument is one of them), a
dispatch file that lacks either line or repeats one, a value that is not one JSON array of
strings (`null` included), or an entry that is empty, absolute, uses a backslash or holds
an empty, `.` or `..` segment. A text defect inside a file or in git output is exit 1, and a
usage error in the same dispatch outranks it.
