"""No tracked path is longer than 120 characters, and no component of one is longer than 255 bytes.

Ticket 61 flattened a `files/` tree because a tracked path of 153 characters broke the Windows
checkout in CI. 120 is the longest path tracked when this test was written, so the cap admits the
current tree and refuses the next longer one before CI does. A Linux checkout also refuses any path
component of more than 255 UTF-8 bytes, which a short path of wide characters can carry, so each
component is held to that limit too.

The length is counted in characters of the decoded path, never in bytes. `git ls-files -z` gives raw
bytes: a path that is not valid UTF-8 is reported on its own line, never raised. The test over the
real tree is skipped, with its reason, only when neither the repository root nor any parent holds a
`.git` entry. Otherwise `git ls-files` runs unconditionally, so a git failure inside a work tree, an
unreadable configuration included, is a test failure and never a skip.
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
MAX_COMPONENT_BYTES = 255


class GitListError(Exception):
    """`git ls-files` failed inside a Git work tree."""


class NotAWorkTree(Exception):
    """Neither the root nor any parent holds a `.git` entry."""


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


def has_git_entry(root: Path) -> bool:
    """True when `root` or any parent holds a `.git` entry (a directory, or the file a linked work tree has).

    Decided without running git, so a broken git cannot turn into "not a work tree".
    """
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


def tracked_paths(repo: Path) -> list[bytes]:
    """The raw tracked paths of the work tree at `repo`; a failing git is a GitListError."""
    try:
        done = run_git(repo, "ls-files", "-z")
    except OSError as error:
        raise GitListError(f"git cannot be run: {error}") from error
    if done.returncode != 0:
        raise GitListError(f"git ls-files exited {done.returncode}: {done.stderr.decode('utf-8', 'replace')}")
    return [item for item in done.stdout.split(b"\0") if item]


def real_tree_offences(root: Path) -> list[str]:
    """The offences of the tracked paths under `root`.

    NotAWorkTree is the only skip. Inside a work tree a failing git is a GitListError, never a skip.
    """
    if not has_git_entry(root):
        raise NotAWorkTree(f"{root} and its parents hold no .git entry")
    return offences(tracked_paths(root))


def path_length(path: str) -> int:
    """The length of a decoded path in characters."""
    return len(path)


def escaped(raw: bytes) -> str:
    """One line naming `raw`: every byte outside printable ASCII, and the backslash, written as \\xNN."""
    return "".join(chr(byte) if 0x20 <= byte < 0x7F and byte != 0x5C else f"\\x{byte:02x}" for byte in raw)


def escaped_text(path: str) -> str:
    return escaped(path.encode("utf-8"))


def offences(paths: Sequence[bytes], cap: int = MAX_PATH_CHARACTERS) -> list[str]:
    """One escaped line per fault: a path longer than `cap` characters, a component longer than 255 bytes, or not UTF-8."""
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
        widest = max(len(component.encode("utf-8")) for component in text.split("/"))
        if widest > MAX_COMPONENT_BYTES:
            lines.append(f"component of {widest} bytes, cap {MAX_COMPONENT_BYTES}: {escaped_text(text)}")
    return lines


def spread(filler: str, total: int) -> str:
    """A path of exactly `total` characters made of `filler` in directories of at most 50 characters and a `.md` leaf.

    A file name is limited to 255 bytes on Linux, so a wide path is split into several short segments.
    """
    body = total - len(".md")
    segments: list[str] = []
    while body > 0:
        take = min(body, 50)
        segments.append(filler * (take - 1 if body - take > 0 else take))
        body -= take
    return "/".join(segments) + ".md"


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
        wide = spread("字", MAX_PATH_CHARACTERS)
        self.assertEqual(len(wide), MAX_PATH_CHARACTERS)
        self.assertGreater(len(wide.encode("utf-8")), MAX_PATH_CHARACTERS)
        self.assertEqual(offences([wide.encode("utf-8")]), [])
        accented = "é" * (MAX_PATH_CHARACTERS - 3) + ".md"
        self.assertEqual(offences([accented.encode("utf-8")]), [])
        too_wide = spread("字", MAX_PATH_CHARACTERS + 1)
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

    def test_every_offender_is_named_not_only_the_first(self) -> None:
        first = "a" * MAX_PATH_CHARACTERS + "1.md"
        second = "b" * MAX_PATH_CHARACTERS + "2.md"
        third = b"c-\xff-3.md"
        found = offences([first.encode("utf-8"), b"fine.md", second.encode("utf-8"), third])
        self.assertEqual(len(found), 3)
        self.assertIn(first, found[0])
        self.assertIn(second, found[1])
        self.assertEqual(found[2], "not valid UTF-8: c-\\xff-3.md")

    def test_a_component_of_273_bytes_in_a_short_path_is_reported(self) -> None:
        name = "doc/" + "字" * 90 + ".md"
        self.assertLess(len(name), MAX_PATH_CHARACTERS)
        self.assertEqual(len(name.split("/")[1].encode("utf-8")), 273)
        found = offences([name.encode("utf-8")])
        self.assertEqual(len(found), 1)
        self.assertIn("273 bytes", found[0])
        self.assertNotIn("\n", found[0])

    def test_a_component_of_exactly_255_bytes_passes_and_256_fails(self) -> None:
        at_limit = "doc/" + "字" * 84 + ".md"
        self.assertEqual(len(at_limit.split("/")[1].encode("utf-8")), MAX_COMPONENT_BYTES)
        self.assertEqual(offences([at_limit.encode("utf-8")]), [])
        over = "doc/" + "字" * 84 + "a.md"
        self.assertEqual(len(offences([over.encode("utf-8")])), 1)

    def test_the_component_limit_is_counted_per_component_not_for_the_path(self) -> None:
        two_components = "x/" + "字" * 40 + "/" + "字" * 40 + ".md"
        self.assertEqual(offences([two_components.encode("utf-8")]), [])


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
        name = spread("字", MAX_PATH_CHARACTERS)
        self.assertEqual(len(name), MAX_PATH_CHARACTERS)
        repo = self.make_repo(name)
        paths = tracked_paths(repo)
        self.assertEqual(len(paths), 1)
        self.assertGreater(len(paths[0]), MAX_PATH_CHARACTERS)
        self.assertEqual(offences(paths), [])
        over = spread("字", MAX_PATH_CHARACTERS + 1)
        repo_over = self.make_repo(over)
        self.assertEqual(len(offences(tracked_paths(repo_over))), 1)

    def test_a_failing_git_ls_files_inside_a_work_tree_is_a_failure_not_a_skip(self) -> None:
        repo = self.make_repo("a.md")
        (repo / ".git" / "index").write_bytes(b"not an index file\n")
        with self.assertRaises(GitListError):
            tracked_paths(repo)

    def test_a_broken_git_config_makes_the_real_tree_check_fail_not_skip(self) -> None:
        repo = self.make_repo("a.md")
        self.assertEqual(real_tree_offences(repo), [])
        config = repo / ".git" / "config"
        config.write_bytes(config.read_bytes() + b"[core\n")
        # git can no longer parse its configuration: both `rev-parse` and `ls-files` exit 128
        self.assertNotEqual(run_git(repo, "rev-parse", "--is-inside-work-tree").returncode, 0)
        with self.assertRaises(GitListError):
            real_tree_offences(repo)

    def test_a_directory_with_no_git_entry_anywhere_is_the_only_skip(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="path-length-bare-"))
        self.addCleanup(remove_tree, work)
        self.assertFalse(has_git_entry(work))
        with self.assertRaises(NotAWorkTree):
            real_tree_offences(work)
        self.assertTrue(has_git_entry(self.make_repo("a.md")))

    def test_a_tree_with_three_offending_paths_names_all_three(self) -> None:
        names = [f"d/{'n' * (MAX_PATH_CHARACTERS - 4)}{suffix}.md" for suffix in ("1", "22", "333")]
        repo = self.make_repo(names[0], "short.md", names[1], names[2])
        found = real_tree_offences(repo)
        self.assertEqual(len(found), 3, found)
        for name in names:
            with self.subTest(name=name):
                self.assertEqual(sum(1 for line in found if name in line), 1)


class RealTreeTests(unittest.TestCase):
    def test_no_tracked_path_of_this_repository_is_longer_than_the_cap(self) -> None:
        try:
            found = real_tree_offences(ROOT)
        except NotAWorkTree as error:
            self.skipTest(f"not a Git work tree: {error}")
        self.assertEqual(found, [], "\n" + "\n".join(found))


if __name__ == "__main__":
    unittest.main()
