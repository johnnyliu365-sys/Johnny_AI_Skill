"""No tracked path is longer than 120 characters.

Ticket 61 flattened a `files/` tree because a tracked path of 153 characters broke the Windows
checkout in CI. 120 is the longest path tracked when this test was written, so the cap admits the
current tree and refuses the next longer one before CI does.

The length is counted in characters of the decoded path, never in bytes. `git ls-files -z` gives raw
bytes: a path that is not valid UTF-8 is reported on its own line, never raised. Outside a Git work
tree the test over the real tree is skipped with its reason; inside one, a failing `git ls-files` is
a test failure, not a skip.
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_PATH_CHARACTERS = 120


class GitListError(Exception):
    """`git ls-files` failed inside a Git work tree."""


def clean_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["PYTHONUTF8"] = "1"
    return env


def remove_tree(path: Path) -> None:
    def make_writable(function: Callable[[str], object], name: str, _info: object) -> None:
        os.chmod(name, stat.S_IWRITE)
        function(name)

    shutil.rmtree(path, onerror=make_writable)


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.longpaths=true", "-C", str(repo), *args],
        capture_output=True,
        env=clean_environment(),
    )


def is_git_work_tree(repo: Path) -> bool:
    """True when `repo` is inside a Git work tree; False when git is absent or says it is not."""
    try:
        done = run_git(repo, "rev-parse", "--is-inside-work-tree")
    except OSError:
        return False
    return done.returncode == 0 and done.stdout.strip() == b"true"


def tracked_paths(repo: Path) -> list[bytes]:
    """The raw tracked paths of the work tree at `repo`; a failing git is a GitListError."""
    try:
        done = run_git(repo, "ls-files", "-z")
    except OSError as error:
        raise GitListError(f"git cannot be run: {error}") from error
    if done.returncode != 0:
        raise GitListError(f"git ls-files exited {done.returncode}: {done.stderr.decode('utf-8', 'replace')}")
    return [item for item in done.stdout.split(b"\0") if item]


def path_length(path: str) -> int:
    """The length of a decoded path in characters."""
    return len(path)


def escaped(raw: bytes) -> str:
    """One line naming `raw`: every byte outside printable ASCII, and the backslash, written as \\xNN."""
    return "".join(chr(byte) if 0x20 <= byte < 0x7F and byte != 0x5C else f"\\x{byte:02x}" for byte in raw)


def escaped_text(path: str) -> str:
    return escaped(path.encode("utf-8"))


def offences(paths: Sequence[bytes], cap: int = MAX_PATH_CHARACTERS) -> list[str]:
    """One escaped line per path that is longer than `cap` characters or is not valid UTF-8."""
    lines: list[str] = []
    for raw in paths:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            lines.append(f"not valid UTF-8: {escaped(raw)}")
            continue
        length = path_length(text)
        if length > cap:
            lines.append(f"{length} characters, cap {cap}: {escaped_text(text)}")
    return lines


class FixtureRepository(unittest.TestCase):
    """A scratch Git work tree whose index holds the paths a test names; no commit is needed."""

    def make_repo(self, *names: str) -> Path:
        work = Path(tempfile.mkdtemp(prefix="path-length-"))
        self.addCleanup(remove_tree, work)
        done = run_git(work, "init", "-q")
        self.assertEqual(done.returncode, 0, done.stderr)
        for name in names:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"x\n")
            added = run_git(work, "add", "--", name)
            self.assertEqual(added.returncode, 0, added.stderr)
        return work


class CapTests(unittest.TestCase):
    def test_the_cap_is_120_characters(self) -> None:
        self.assertEqual(MAX_PATH_CHARACTERS, 120)

    def test_a_path_of_exactly_the_cap_passes_and_one_character_more_fails(self) -> None:
        at_cap = ("a" * (MAX_PATH_CHARACTERS - 3)) + ".md"
        over = "b" + at_cap
        self.assertEqual(len(at_cap), MAX_PATH_CHARACTERS)
        self.assertEqual(offences([at_cap.encode("utf-8")]), [])
        found = offences([over.encode("utf-8")])
        self.assertEqual(len(found), 1)
        self.assertIn(over, found[0])

    def test_the_length_is_counted_in_characters_not_bytes(self) -> None:
        # 120 characters, 3 bytes each for the CJK ones: 240 bytes, still within the cap
        wide = "字" * (MAX_PATH_CHARACTERS - 3) + ".md"
        self.assertEqual(len(wide), MAX_PATH_CHARACTERS)
        self.assertGreater(len(wide.encode("utf-8")), MAX_PATH_CHARACTERS)
        self.assertEqual(offences([wide.encode("utf-8")]), [])
        accented = "é" * (MAX_PATH_CHARACTERS - 3) + ".md"
        self.assertEqual(offences([accented.encode("utf-8")]), [])
        too_wide = "字" + wide
        self.assertEqual(len(offences([too_wide.encode("utf-8")])), 1)

    def test_an_offender_is_named_on_one_escaped_line(self) -> None:
        name = "dir/" + "é" * 120 + "\n" + "\\"
        found = offences([name.encode("utf-8")])
        self.assertEqual(len(found), 1)
        self.assertNotIn("\n", found[0])
        self.assertNotIn("é", found[0])
        self.assertIn("\\xc3\\xa9", found[0])
        self.assertIn("\\x0a", found[0])
        self.assertIn("\\x5c", found[0])

    def test_an_undecodable_path_is_reported_not_raised(self) -> None:
        found = offences([b"ok.md", b"bad-\xff-name.md"])
        self.assertEqual(found, ["not valid UTF-8: bad-\\xff-name.md"])

    def test_an_undecodable_path_is_reported_even_when_short(self) -> None:
        self.assertEqual(len(offences([b"\xff"])), 1)

    def test_an_empty_list_has_no_offence(self) -> None:
        self.assertEqual(offences([]), [])


class FixtureTreeTests(FixtureRepository):
    def test_a_tree_with_a_121_character_tracked_path_fails_and_names_it(self) -> None:
        long_name = "d/" + "n" * (MAX_PATH_CHARACTERS + 1 - len("d/") - 3) + ".md"
        self.assertEqual(len(long_name), MAX_PATH_CHARACTERS + 1)
        repo = self.make_repo("short.md", long_name)
        found = offences(tracked_paths(repo))
        self.assertEqual(len(found), 1)
        self.assertIn(long_name, found[0])

    def test_a_tree_with_a_120_character_tracked_path_passes(self) -> None:
        name = "d/" + "n" * (MAX_PATH_CHARACTERS - len("d/") - 3) + ".md"
        self.assertEqual(len(name), MAX_PATH_CHARACTERS)
        repo = self.make_repo(name)
        self.assertEqual(offences(tracked_paths(repo)), [])

    def test_a_non_ascii_tracked_path_is_counted_in_characters(self) -> None:
        name = "字" * (MAX_PATH_CHARACTERS - 3) + ".md"
        repo = self.make_repo(name)
        paths = tracked_paths(repo)
        self.assertEqual(len(paths), 1)
        self.assertGreater(len(paths[0]), MAX_PATH_CHARACTERS)
        self.assertEqual(offences(paths), [])
        over = "字" * (MAX_PATH_CHARACTERS - 2) + ".md"
        repo_over = self.make_repo(over)
        self.assertEqual(len(offences(tracked_paths(repo_over))), 1)

    def test_a_failing_git_ls_files_inside_a_work_tree_is_a_failure_not_a_skip(self) -> None:
        repo = self.make_repo("a.md")
        self.assertTrue(is_git_work_tree(repo))
        (repo / ".git" / "index").write_bytes(b"not an index file\n")
        with self.assertRaises(GitListError):
            tracked_paths(repo)

    def test_a_directory_that_is_not_a_work_tree_is_recognised(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="path-length-bare-"))
        self.addCleanup(remove_tree, work)
        self.assertFalse(is_git_work_tree(work))


class RealTreeTests(unittest.TestCase):
    def test_no_tracked_path_of_this_repository_is_longer_than_the_cap(self) -> None:
        if not is_git_work_tree(ROOT):
            self.skipTest(f"{ROOT} is not a Git work tree (or git is absent): there is no tracked path list to measure")
        found = offences(tracked_paths(ROOT))
        self.assertEqual(found, [], "\n" + "\n".join(found))


if __name__ == "__main__":
    unittest.main()
