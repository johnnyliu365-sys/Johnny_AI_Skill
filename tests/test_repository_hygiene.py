"""Pin the `.gitignore` rules that keep in-tree venvs and suite logs untracked.

Governance 15: the root `.gitignore` never had an entry for `.venv/` or
`suite.log`, so both were plain untracked paths as far as `git status` and
`git add -A` were concerned. Two sightings on 2026-08-21 made this concrete:

1. Governance 14's ticket required building `.venv/` inside a worktree for
   acceptance; the implementer reported it back as an "unignored untracked
   directory" that `git add -A` would sweep in.
2. Later the same day, a stray venv created by a swallowed backslash (783
   files, ~270k lines) actually rode a wrap-up `add -A` into a fast-forwarded
   commit on `main`; it took two resets to remove. `origin` was never
   touched.

The process-level fix (spell exact paths in wrap-up commits) only binds
whoever remembers it happened; an ignore entry binds everyone. Because a
tracked `.gitignore` is checked out fresh into every worktree, and gitignore
anchoring (a leading `/`) is always relative to wherever that file sits, a
root-anchored `/.venv/` and `/suite.log` cover a worktree's own root in
`.worktrees/<id>/` or `.claude/worktrees/<id>/` the same way they cover the
main checkout -- no separate entry per worktree is needed.

Attribution, not just outcome (correction after first review round)
---------------------------------------------------------------------
The first version of this suite pinned each pre-existing line by asserting
only `git check-ignore`'s exit code (0 = ignored). Review caught the gap by
mutating a line this ticket never touched: deleting the pre-existing
`__pycache__/` line left `14 passed, 0 red`, because the probe path
`__pycache__/foo.pyc` is also covered by `*.py[cod]` (a bare-basename suffix
pattern with no directory component of its own). Exit code 0 answers "is
this path ignored by some rule"; it does not answer "is this line still the
one deciding it" -- and only the latter is what a per-line regression test
is supposed to prove.

The fix: every line-pinning probe below uses `git check-ignore -v` and
asserts the matched pattern text equals the exact pinned line, parsed from
the documented `-v` format `<source>:<linenum>:<pattern><TAB><path>`. This
is mechanical rather than probe-path cleverness -- it holds regardless of
whether some other, unrelated rule happens to also cover the same path, now
or after a future `.gitignore` edit, because the assertion names the
deciding rule instead of merely observing an outcome that rule could share
with another.

This module does not create real `.venv/` or `suite.log` paths on disk:
`git check-ignore` matches gitignore patterns against a pathname's directory
components, not against `lstat` results (confirmed directly by the
`__pycache__/foo.pyc` case above, which resolves to a decisive match
without existing anywhere on disk).

Per the cp950-console pitfall on this host (subprocess `text=True` against
non-ASCII output can raise a `UnicodeDecodeError` instead of decoding), git
output is captured as bytes and decoded with `errors="replace"` only for
parsing/diagnostics; every ignored-vs-not decision is made on the integer
`returncode`, and every line-attribution decision on the parsed pattern
text -- neither depends on the console's own encoding.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from typing import NamedTuple

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _require_git(git_executable: str | None) -> str:
    """Return the resolved git executable, or skip rather than assume a result.

    Fail-closed contract for this suite (ticket TDD design item 3): an
    environment without a `git` on PATH must never be silently read as
    "the path is not ignored" (a false green). It must skip instead.
    """

    if git_executable is None:
        raise unittest.SkipTest("git executable not found on PATH")
    return git_executable


class _IgnoreProbe(NamedTuple):
    """One `git check-ignore -v` outcome, decoded for assertions.

    `matched_pattern` is the exact pattern text of the `.gitignore` line
    that decided the outcome (e.g. "__pycache__/"), or `None` when nothing
    matched (`returncode == 1`). `source` is the ignore-source file git
    attributed the match to (expected to always be ".gitignore" for this
    suite); it is `None` alongside `matched_pattern` when nothing matched.
    """

    returncode: int
    source: str | None
    matched_pattern: str | None
    raw_stdout: str
    raw_stderr: str


def _probe(path: str) -> _IgnoreProbe:
    """Run `git check-ignore -v` for `path` against the repo-root `.gitignore`.

    Parses the documented `-v` output line
    `<source>:<linenum>:<pattern><TAB><path>` so a caller can assert exactly
    which line decided the outcome, not merely that some line did.
    """

    git_bin = _require_git(shutil.which("git"))
    result = subprocess.run(
        [git_bin, "check-ignore", "-v", path],
        cwd=_REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    if result.returncode != 0:
        return _IgnoreProbe(result.returncode, None, None, stdout, stderr)
    first_line = stdout.splitlines()[0]
    meta, _, _matched_path = first_line.rpartition("\t")
    source, _, remainder = meta.partition(":")
    _linenum, _, pattern = remainder.partition(":")
    return _IgnoreProbe(result.returncode, source, pattern, stdout, stderr)


class RepositoryHygieneIgnoreRulesTests(unittest.TestCase):
    """`.gitignore` behavior for the two new entries plus every prior line."""

    def _assert_line_decides(self, path: str, expected_pattern: str) -> None:
        """Assert `path` is ignored, and specifically by `expected_pattern`."""

        probe = _probe(path)
        self.assertEqual(
            probe.returncode,
            0,
            f"expected {path!r} to be git-ignored; "
            f"stdout={probe.raw_stdout!r} stderr={probe.raw_stderr!r}",
        )
        self.assertEqual(probe.source, ".gitignore")
        self.assertEqual(
            probe.matched_pattern,
            expected_pattern,
            f"{path!r} is ignored, but by {probe.matched_pattern!r}, not the "
            f"pinned {expected_pattern!r} -- another rule has taken over "
            f"attribution (raw: {probe.raw_stdout!r})",
        )

    def _assert_not_ignored(self, path: str) -> None:
        probe = _probe(path)
        self.assertEqual(
            probe.returncode,
            1,
            f"expected {path!r} to NOT be git-ignored (prefix-lookalike must "
            f"stay tracked); matched {probe.matched_pattern!r} "
            f"(raw: {probe.raw_stdout!r})",
        )
        self.assertIsNone(probe.matched_pattern)

    # -- new behavior (ticket TDD design item 1) -------------------------

    def test_venv_directory_at_worktree_root_is_ignored(self) -> None:
        self._assert_line_decides(".venv/x", "/.venv/")

    def test_file_nested_inside_venv_directory_is_ignored(self) -> None:
        self._assert_line_decides(".venv/lib/site-packages/foo.py", "/.venv/")

    def test_suite_log_at_worktree_root_is_ignored(self) -> None:
        self._assert_line_decides("suite.log", "/suite.log")

    # -- path-prefix lookalikes must stay tracked (defect class 1) ------

    def test_venv_prefixed_filename_is_not_swept_in(self) -> None:
        self._assert_not_ignored(".venv-notes.md")

    def test_suite_log_prefixed_filename_is_not_swept_in(self) -> None:
        self._assert_not_ignored("suite.log.py")

    # -- regression: each of the 7 pre-existing non-blank lines, one at a
    # -- time, not just the two newly added ones. Attribution (not just
    # -- exit code) is asserted for every real pattern line, because a path
    # -- covered by two rules keeps returning exit 0 after either rule
    # -- alone is deleted -- see module docstring, "Attribution, not just
    # -- outcome". -------------------------------------------------------

    def test_existing_rule_johnny_runtime_root_still_ignored(self) -> None:
        self._assert_line_decides(
            "tests/.johnny-runtime/somefile", "/tests/.johnny-runtime/"
        )

    def test_existing_rule_worktrees_dir_still_ignored(self) -> None:
        self._assert_line_decides(".worktrees/some-ticket/marker", "/.worktrees/")

    def test_existing_rule_claude_worktrees_dir_still_ignored(self) -> None:
        self._assert_line_decides(
            ".claude/worktrees/some-ticket/marker", "/.claude/worktrees/"
        )

    def test_existing_rule_pycache_dir_still_ignored_at_any_depth(self) -> None:
        # Both probes below also carry a `.pyc` suffix, which `*.py[cod]`
        # (the very next line) independently matches too. Asserting the
        # matched pattern text -- not just the exit code -- is what proves
        # the `__pycache__/` line itself is still doing the work: deleting
        # it leaves these paths ignored regardless (attributed to
        # `*.py[cod]` instead), so an exit-code-only check cannot tell the
        # two apart. This is the exact gap review's mutation exposed.
        self._assert_line_decides("__pycache__/foo.pyc", "__pycache__/")
        self._assert_line_decides(
            "modules/foo/__pycache__/bar.pyc", "__pycache__/"
        )

    def test_existing_rule_compiled_python_suffixes_still_ignored(self) -> None:
        for suffix in ("pyc", "pyo", "pyd"):
            with self.subTest(suffix=suffix):
                self._assert_line_decides(f"module.{suffix}", "*.py[cod]")

    def test_existing_rule_dist_dir_still_ignored(self) -> None:
        self._assert_line_decides("dist/bundle.zip", "/dist/")

    def test_existing_comment_line_is_preserved(self) -> None:
        content = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(
            "發行產物：建置輸出，不進版控（閘門要求整合工作區乾淨）",
            content,
        )


class CheckIgnoreGitAvailabilityTests(unittest.TestCase):
    """Fail-closed contract for `_require_git` (defect class 6)."""

    def test_require_git_skips_when_no_executable_is_resolved(self) -> None:
        with self.assertRaises(unittest.SkipTest):
            _require_git(None)

    def test_require_git_passes_through_a_resolved_executable(self) -> None:
        self.assertEqual(_require_git("C:/fake/git.exe"), "C:/fake/git.exe")


if __name__ == "__main__":
    unittest.main()
