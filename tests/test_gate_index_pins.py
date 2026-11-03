"""Behavioural tests for the index_pins gate script (exit codes 0/1/2/3).

Each case builds a throwaway git repository in a temporary directory; every expected
revision and digest is computed from that repository with git and hashlib.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import index_pins  # noqa: E402

SCRIPT = _SCRIPTS / "index_pins.py"
HEADER = "| id | kind | state | revision | digest | leaf |\n| --- | --- | --- | --- | --- | --- |\n"


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
    return done.stdout


def sha256_of_committed(repo: Path, commit: str, path: str) -> str:
    shown = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo, capture_output=True)
    return hashlib.sha256(shown.stdout).hexdigest()


class Repo:
    """A temporary repository with one leaf and room for an index."""

    def __init__(self, leaf_body: str = "first body\n") -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="idxpin-")
        self.dir = Path(self.tmp.name)
        git(self.dir, "init", "-q", "-b", "main")
        # Normalise on add only, so the worktree keeps CRLF while the repository stores LF
        # on every host; the digest must follow the repository bytes.
        git(self.dir, "config", "core.autocrlf", "input")
        self.write_leaf(leaf_body, newline="\r\n")
        self.commit("leaf")

    def close(self) -> None:
        self.tmp.cleanup()

    def write_leaf(self, body: str, newline: str = "\n", name: str = "leaf.md") -> None:
        (self.dir / name).parent.mkdir(parents=True, exist_ok=True)
        with open(self.dir / name, "w", encoding="utf-8", newline=newline) as handle:
            handle.write(body)

    def commit(self, message: str) -> str:
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "--allow-empty", "-m", message)
        return git(self.dir, "rev-parse", "HEAD").strip()

    def last_commit(self, path: str = "leaf.md") -> str:
        return git(self.dir, "log", "-1", "--format=%H", "--", path).strip()

    def digest(self, path: str = "leaf.md") -> str:
        return sha256_of_committed(self.dir, self.last_commit(path), path)

    def write_index(self, rows: str, newline: str = "\n", header: str = HEADER, name: str = "INDEX.md") -> Path:
        text = (header + rows).replace("\n", newline)
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return path

    def row(self, rev: str, digest: str, state: str = "open", leaf: str = "leaf.md", ident: str = "a1") -> str:
        return f"| {ident} | spec | {state} | `git:{rev}` | `sha256:{digest}` | {leaf} |\n"

    def run(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        # An index named relative to the repository is passed as an absolute path,
        # because the script resolves index arguments against the working directory.
        named = [str(self.dir / arg) if arg.endswith(".md") and not Path(arg).is_absolute() else arg for arg in args]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = index_pins.main(["--root", str(self.dir), *named])
        return code, out.getvalue(), err.getvalue()


class PinCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()
        self.addCleanup(self.repo.close)


class DigestAlgorithmTests(PinCase):
    def test_digest_is_of_the_repository_bytes_not_the_worktree_bytes(self) -> None:
        worktree_digest = hashlib.sha256((self.repo.dir / "leaf.md").read_bytes()).hexdigest()
        repository = index_pins.Repo(self.repo.dir)
        computed = repository.blob_sha256_at(self.repo.last_commit(), "leaf.md")
        self.assertEqual(computed, self.repo.digest())
        self.assertNotEqual(computed, worktree_digest)

    def test_digest_is_not_the_git_blob_hash_and_revision_is_a_commit(self) -> None:
        commit = self.repo.last_commit()
        blob = git(self.repo.dir, "rev-parse", f"{commit}:leaf.md").strip()
        repository = index_pins.Repo(self.repo.dir)
        self.assertNotEqual(repository.blob_sha256_at(commit, "leaf.md"), blob)
        self.assertEqual(repository.current_commit_for("leaf.md"), commit)
        self.assertEqual(git(self.repo.dir, "cat-file", "-t", commit).strip(), "commit")

    def test_untracked_and_unknown_leaves_have_no_pin(self) -> None:
        repository = index_pins.Repo(self.repo.dir)
        self.assertIsNone(repository.current_commit_for("never-added.md"))
        self.assertIsNone(repository.blob_sha256_at(self.repo.last_commit(), "never-added.md"))


class CheckAndWriteTests(PinCase):
    def test_current_pins_pass_check_with_exit_0(self) -> None:
        self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        code, out, _ = self.repo.run("--check", "INDEX.md")
        self.assertEqual(code, 0, out)
        self.assertIn("drift=0", out)

    def test_wrong_digest_alone_is_red(self) -> None:
        wrong = hashlib.sha256(b"something else").hexdigest()
        self.assertNotEqual(wrong, self.repo.digest())
        self.repo.write_index(self.repo.row(self.repo.last_commit(), wrong))
        self.repo.commit("index")
        code, out, _ = self.repo.run("--check", "INDEX.md")
        self.assertEqual(code, 1)
        self.assertIn("STALE INDEX.md:3 leaf.md", out)
        self.assertIn("drift=1", out)

    def test_blob_hash_in_the_revision_cell_is_red(self) -> None:
        commit = self.repo.last_commit()
        blob = git(self.repo.dir, "rev-parse", f"{commit}:leaf.md").strip()
        self.repo.write_index(self.repo.row(blob, self.repo.digest()))
        self.repo.commit("index")
        code, _, _ = self.repo.run("--check", "INDEX.md")
        self.assertEqual(code, 1)

    def test_pin_to_an_older_commit_is_red_after_the_leaf_advances(self) -> None:
        old_commit, old_digest = self.repo.last_commit(), self.repo.digest()
        self.repo.write_index(self.repo.row(old_commit, old_digest))
        self.repo.commit("index")
        self.repo.write_leaf("second body\n")
        new_commit = self.repo.commit("advance")
        self.assertEqual(self.repo.last_commit(), new_commit)
        code, out, _ = self.repo.run("--check", "INDEX.md")
        self.assertEqual(code, 1)
        self.assertIn("drift=1", out)

    def test_write_repins_and_a_following_check_is_green(self) -> None:
        path = self.repo.write_index(self.repo.row("0" * 40, "f" * 64))
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 1)
        code, out, _ = self.repo.run("--write", "INDEX.md")
        self.assertEqual(code, 0, out)
        text = path.read_text(encoding="utf-8")
        self.assertIn(f"`git:{self.repo.last_commit()}`", text)
        self.assertIn(f"`sha256:{self.repo.digest()}`", text)
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 0)

    def test_write_keeps_other_cells_other_lines_and_the_line_endings(self) -> None:
        prose_before, prose_after = "intro text stays\r\n", "\r\ntrailing text stays\r\n"
        rows = self.repo.row("0" * 40, "f" * 64, state="open", ident="keep-me")
        path = self.repo.dir / "INDEX.md"
        original = prose_before + (HEADER + rows).replace("\n", "\r\n") + prose_after
        path.write_bytes(original.encode("utf-8"))
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--write", "INDEX.md")[0], 0)
        rewritten = path.read_bytes().decode("utf-8")
        expected = original.replace("0" * 40, self.repo.last_commit()).replace("f" * 64, self.repo.digest())
        self.assertEqual(rewritten, expected)
        self.assertEqual(rewritten.count("\r\n"), original.count("\r\n"))

    def test_write_preserves_bare_hash_spelling_without_backticks(self) -> None:
        rows = f"| a1 | spec | open | git:{'0' * 40} | sha256:{'f' * 64} | leaf.md |\n"
        path = self.repo.write_index(rows)
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--write", "INDEX.md")[0], 0)
        self.assertIn(f"| git:{self.repo.last_commit()} | sha256:{self.repo.digest()} |", path.read_text(encoding="utf-8"))

    def test_only_the_digest_cell_changes_when_only_the_digest_is_wrong(self) -> None:
        commit = self.repo.last_commit()
        path = self.repo.write_index(self.repo.row(commit, "a" * 64))
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--write", "INDEX.md")[0], 0)
        self.assertEqual(path.read_text(encoding="utf-8"), HEADER + self.repo.row(commit, self.repo.digest()))

    def test_malformed_length_hash_is_replaced_in_place_keeping_its_prefix(self) -> None:
        rows = f"| a1 | spec | open | git:{self.repo.last_commit()} | sha256:{'e' * 65} | leaf.md |\n"
        path = self.repo.write_index(rows)
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--write", "INDEX.md")[0], 0)
        self.assertIn(f"sha256:{self.repo.digest()} |", path.read_text(encoding="utf-8"))

    def test_indexes_are_discovered_when_no_file_is_named(self) -> None:
        self.repo.write_index(self.repo.row("0" * 40, "f" * 64))
        self.repo.commit("index")
        code, out, _ = self.repo.run("--check")
        self.assertEqual(code, 1)
        self.assertIn("indexes=1", out)

    def test_json_report_lists_every_finding(self) -> None:
        self.repo.write_index(self.repo.row("0" * 40, "f" * 64))
        self.repo.commit("index")
        report = self.repo.dir.parent / (self.repo.dir.name + "-report.json")
        self.addCleanup(lambda: report.unlink(missing_ok=True))
        self.repo.run("--check", "--json", str(report), "INDEX.md")
        findings = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual([item["status"] for item in findings], ["DRIFT"])
        self.assertEqual(findings[0]["new_rev"], self.repo.last_commit())
        self.assertEqual(findings[0]["new_digest"], self.repo.digest())

    def test_multiple_pin_groups_in_one_row_are_each_checked(self) -> None:
        self.repo.write_leaf("other leaf\n", name="other.md")
        self.repo.commit("other")
        header = (
            "| id | state | spec revision | spec digest | spec leaf | code revision | code digest | code leaf |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        )
        good = (self.repo.last_commit("leaf.md"), self.repo.digest("leaf.md"))
        other = (self.repo.last_commit("other.md"), self.repo.digest("other.md"))
        row = (
            f"| r1 | open | `git:{good[0]}` | `sha256:{good[1]}` | leaf.md "
            f"| `git:{other[0]}` | `sha256:{'0' * 64}` | other.md |\n"
        )
        self.repo.write_index(row, header=header)
        self.repo.commit("index")
        code, out, _ = self.repo.run("--check", "INDEX.md")
        self.assertEqual(code, 1)
        self.assertEqual(out.count("STALE"), 1)
        self.assertIn("other.md", out)


class SealedRowTests(PinCase):
    def test_sealed_row_is_not_repinned_when_the_leaf_advances(self) -> None:
        sealed_commit, sealed_digest = self.repo.last_commit(), self.repo.digest()
        row = self.repo.row(sealed_commit, sealed_digest, state="SEALED")
        path = self.repo.write_index(row)
        self.repo.commit("index")
        self.repo.write_leaf("advanced body\n")
        self.repo.commit("advance")
        self.assertNotEqual(self.repo.last_commit(), sealed_commit)
        code, out, _ = self.repo.run("--write", "INDEX.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(path.read_text(encoding="utf-8"), HEADER + row)

    def test_sealed_row_with_a_digest_that_does_not_verify_is_a_defect_and_stays_unchanged(self) -> None:
        row = self.repo.row(self.repo.last_commit(), "0" * 64, state="SEALED")
        path = self.repo.write_index(row)
        self.repo.commit("index")
        for mode in ("--check", "--write"):
            with self.subTest(mode):
                code, out, _ = self.repo.run(mode, "INDEX.md")
                self.assertEqual(code, 1)
                self.assertIn("SEALED_PIN_INVALID", out)
        self.assertEqual(path.read_text(encoding="utf-8"), HEADER + row)

    def test_sealed_word_is_configurable(self) -> None:
        row = self.repo.row(self.repo.last_commit(), "0" * 64, state="FROZEN")
        self.repo.write_index(row)
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 1)
        code, out, _ = self.repo.run("--check", "--sealed-state", "FROZEN", "INDEX.md")
        self.assertEqual(code, 1)
        self.assertIn("SEALED_PIN_INVALID", out)


    def test_sealed_pin_missing_when_a_sealed_row_lacks_its_revision_or_digest(self) -> None:
        digest, commit = self.repo.digest(), self.repo.last_commit()
        rows = {
            "revision cell without a hash": f"| a1 | spec | SEALED | n/a | `sha256:{digest}` | leaf.md |\n",
            "digest cell without a hash": f"| a1 | spec | SEALED | `git:{commit}` | n/a | leaf.md |\n",
        }
        for label, row in rows.items():
            path = self.repo.write_index(row)
            self.repo.commit("index " + label)
            for mode in ("--check", "--write"):
                with self.subTest(label, mode=mode):
                    code, out, _ = self.repo.run(mode, "INDEX.md")
                    self.assertEqual(code, 1, out)
                    self.assertIn("SEALED_PIN_MISSING", out)
                    self.assertEqual(path.read_text(encoding="utf-8"), HEADER + row)

    def test_sealed_word_matches_the_whole_state_cell_never_a_substring(self) -> None:
        row = self.repo.row(self.repo.last_commit(), self.repo.digest(), state="FROZEN")
        self.repo.write_index(row)
        self.repo.commit("index")
        self.repo.write_leaf("advanced body\n")
        self.repo.commit("advance")
        # Unsealed under the default word: the pin is behind the leaf, so the row is stale.
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 1)
        for word in ("FROZEN", "frozen", "  Frozen  "):
            with self.subTest(sealed=word):
                code, out, _ = self.repo.run("--check", "--sealed-state", word, "INDEX.md")
                self.assertEqual(code, 0, out)
        for word in ("o", "froz", "ZEN", "FROZEN-X", "FROZEN FROZEN"):
            with self.subTest(substring=word):
                code, out, _ = self.repo.run("--check", "--sealed-state", word, "INDEX.md")
                self.assertEqual(code, 1, out)
                self.assertIn("STALE INDEX.md:3 leaf.md", out)

    def test_state_cell_is_compared_after_stripping_padding(self) -> None:
        row = self.repo.row(self.repo.last_commit(), self.repo.digest(), state="  SEALED  ")
        self.repo.write_index(row)
        self.repo.commit("index")
        self.repo.write_leaf("advanced body\n")
        self.repo.commit("advance")
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 0)

    def test_empty_or_blank_sealed_state_is_a_usage_error_not_a_pass(self) -> None:
        row = self.repo.row(self.repo.last_commit(), "0" * 64, state="SEALED")
        self.repo.write_index(row)
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 1)
        for word in ("", " ", "\t"):
            with self.subTest(repr(word)):
                code, out, err = self.repo.run("--check", "--sealed-state", word, "INDEX.md")
                self.assertEqual(code, 3, out + err)
                self.assertEqual(out, "")
                self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)


class DefectTests(PinCase):
    def check_defect(self, text: str, status: str) -> None:
        (self.repo.dir / "INDEX.md").write_text(text, encoding="utf-8", newline="\n")
        self.repo.commit("index")
        for mode in ("--check", "--write"):
            with self.subTest(mode, status=status):
                code, out, _ = self.repo.run(mode, "INDEX.md")
                self.assertEqual(code, 1, out)
                self.assertIn(status, out)

    def good_row(self) -> str:
        return self.repo.row(self.repo.last_commit(), self.repo.digest())

    def test_row_with_a_different_column_count_is_a_defect(self) -> None:
        self.check_defect(HEADER + self.good_row().rstrip("\n|") + " | extra |\n", "ROW_SHAPE_MISMATCH")

    def test_pinned_row_outside_any_table_is_a_defect(self) -> None:
        self.check_defect(HEADER + self.good_row() + "\n" + self.good_row(), "ORPHAN_PINNED_ROW")

    def test_leaf_that_is_not_tracked_is_a_defect(self) -> None:
        self.check_defect(HEADER + self.repo.row("0" * 40, "f" * 64, leaf="missing.md"), "SKIP_UNRESOLVED")

    def test_leaf_cell_without_a_path_is_a_defect(self) -> None:
        self.check_defect(HEADER + self.repo.row("0" * 40, "f" * 64, leaf="see the notes"), "SKIP_NO_PATH_IN_CELL")

    def test_stale_cell_without_any_hash_is_a_defect(self) -> None:
        row = "| a1 | spec | open | n/a | `sha256:" + "f" * 64 + "` | leaf.md |\n"
        self.check_defect(HEADER + row, "SKIP_NO_HASH_IN_CELL")

    def test_pinned_shape_negatives_are_not_pins(self) -> None:
        sha40, sha64 = "a" * 40, "b" * 64
        negatives = {
            "bare 40-hex and 64-hex": [sha40, sha64],
            "bare 40-hex with a prefixed digest": [sha40, f"sha256:{sha64}"],
            "prefixed revision with a bare 64-hex": [f"git:{sha40}", sha64],
            "sha256= form": [f"git:{sha40}", f"sha256={sha64}"],
            "only the revision side": [f"git:{sha40}", "none"],
            "only the digest side": ["none", f"sha256:{sha64}"],
        }
        self.assertTrue(index_pins._looks_pinned([f"git:{sha40}", f"sha256:{sha64}"]))
        for label, cells in negatives.items():
            with self.subTest(label):
                self.assertFalse(index_pins._looks_pinned(cells))
                text = "| " + " | ".join(["a1", "spec", *cells, "leaf.md"]) + " |\n"
                (self.repo.dir / "INDEX.md").write_text(text, encoding="utf-8", newline="\n")
                self.repo.commit("index " + label)
                code, out, _ = self.repo.run("--check", "INDEX.md")
                self.assertEqual(code, 0, out)
                self.assertNotIn("ORPHAN_PINNED_ROW", out)

    def test_malformed_pin_orphan_canary_reports_each_of_three_rows(self) -> None:
        sha40, sha64 = "a" * 40, "b" * 64
        rows = [
            f"| a1 | spec | open | `git:{sha40[:-1]}` | `sha256:{sha64}` | leaf.md |",
            f"| a2 | spec | open | `git:{sha40}` | `sha256:{sha64[:-1]}` | leaf.md |",
            f"| a3 | spec | open | `git:{sha40.upper()}` | `sha256:{sha64}` | leaf.md |",
        ]
        text = "\n".join(rows) + "\n"
        (self.repo.dir / "INDEX.md").write_text(text, encoding="utf-8", newline="\n")
        self.repo.commit("index")
        for mode in ("--check", "--write"):
            with self.subTest(mode):
                code, out, _ = self.repo.run(mode, "INDEX.md")
                self.assertEqual(code, 1, out)
                self.assertIn("defects=3", out)
                for number in (1, 2, 3):
                    line = next((item for item in out.splitlines() if f"INDEX.md:{number} " in item), "")
                    self.assertIn("ORPHAN_PINNED_ROW", line)
                    self.assertIn("MALFORMED_PIN", line)
                self.assertEqual((self.repo.dir / "INDEX.md").read_text(encoding="utf-8"), text)

    def test_parent_relative_leaf_resolves_against_the_index_directory(self) -> None:
        self.repo.write_leaf("root body\n", name="x.md")
        self.repo.write_leaf("nested body\n", name="a/x.md")
        self.repo.commit("two leaves named x.md")
        self.assertNotEqual(self.repo.digest("x.md"), self.repo.digest("a/x.md"))
        for spelling in ("../x.md", "./../x.md"):
            good = self.repo.row(self.repo.last_commit("a/x.md"), self.repo.digest("a/x.md"), leaf=spelling)
            self.repo.write_index(good, name="a/b/INDEX.md")
            self.repo.commit("index " + spelling)
            with self.subTest(spelling):
                code, out, _ = self.repo.run("--check", "a/b/INDEX.md")
                self.assertEqual(code, 0, out)
                self.assertNotIn("SKIP_UNRESOLVED", out)
            stale = self.repo.row(self.repo.last_commit("a/x.md"), "0" * 64, leaf=spelling)
            self.repo.write_index(stale, name="a/b/INDEX.md")
            self.repo.commit("stale " + spelling)
            with self.subTest(spelling, stale=True):
                code, out, _ = self.repo.run("--check", "a/b/INDEX.md")
                self.assertEqual(code, 1, out)
                self.assertIn("STALE a/b/INDEX.md:3 a/x.md", out)

    def test_hex_text_inside_a_table_that_is_not_an_index_is_not_flagged(self) -> None:
        text = (
            "| name | note |\n| --- | --- |\n"
            f"| sample | commit {'a' * 40} and sha256={'b' * 64} |\n\n" + HEADER + self.good_row()
        )
        (self.repo.dir / "INDEX.md").write_text(text, encoding="utf-8", newline="\n")
        self.repo.commit("index")
        self.assertEqual(self.repo.run("--check", "INDEX.md")[0], 0)


class ShallowHistoryTests(unittest.TestCase):
    def test_a_shallow_clone_refuses_to_pin_to_its_boundary(self) -> None:
        source = Repo()
        self.addCleanup(source.close)
        source.write_leaf("a second commit\n", name="unrelated.md")
        source.commit("second")
        with tempfile.TemporaryDirectory(prefix="idxpin-shallow-") as temp:
            clone = Path(temp) / "clone"
            git(Path(temp), "clone", "-q", "--depth", "1", source.dir.as_uri(), str(clone))
            git(clone, "config", "core.autocrlf", "input")
            index = clone / "INDEX.md"
            row = f"| a1 | spec | open | `git:{'0' * 40}` | `sha256:{'f' * 64}` | leaf.md |\n"
            index.write_text(HEADER + row, encoding="utf-8", newline="\n")
            git(clone, "add", "INDEX.md")
            git(clone, "commit", "-q", "-m", "index")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = index_pins.main(["--root", str(clone), "--check", str(index)])
            self.assertEqual(code, 2)
            self.assertIn("SHALLOW_HISTORY", out.getvalue())
            self.assertIn("leaf.md", out.getvalue())
            self.assertEqual(index.read_text(encoding="utf-8"), HEADER + row)

    def test_a_shallow_clone_also_refuses_write_and_leaves_the_index_unchanged(self) -> None:
        source = Repo()
        self.addCleanup(source.close)
        source.write_leaf("a second commit\n", name="unrelated.md")
        source.commit("second")
        with tempfile.TemporaryDirectory(prefix="idxpin-shallow-") as temp:
            clone = Path(temp) / "clone"
            git(Path(temp), "clone", "-q", "--depth", "1", source.dir.as_uri(), str(clone))
            git(clone, "config", "core.autocrlf", "input")
            index = clone / "INDEX.md"
            row = f"| a1 | spec | open | `git:{'0' * 40}` | `sha256:{'f' * 64}` | leaf.md |\n"
            index.write_text(HEADER + row, encoding="utf-8", newline="\n")
            git(clone, "add", "INDEX.md")
            git(clone, "commit", "-q", "-m", "index")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = index_pins.main(["--root", str(clone), "--write", str(index)])
            self.assertEqual(code, 2)
            self.assertEqual(index.read_text(encoding="utf-8"), HEADER + row)


class UsageTests(PinCase):
    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = index_pins.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_every_usage_error_exits_3_with_one_usage_line(self) -> None:
        self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        root = str(self.repo.dir)
        with tempfile.TemporaryDirectory(prefix="idxpin-norepo-") as outside:
            cases = {
                "no mode": ["--root", root],
                "both modes": ["--root", root, "--check", "--write"],
                "unknown option": ["--root", root, "--check", "--bogus"],
                "option without value": ["--root", root, "--check", "--json"],
                "missing index file": ["--root", root, "--check", str(self.repo.dir / "absent.md")],
                "index outside the repository": ["--root", root, "--check", str(Path(outside) / "x.md")],
                "index argument is a directory": ["--root", root, "--check", str(self.repo.dir)],
                "root is not a directory": ["--root", str(Path(outside) / "absent"), "--check"],
                "empty sealed state": ["--root", root, "--check", "--sealed-state", ""],
                "blank sealed state": ["--root", root, "--check", "--sealed-state", "  "],
            }
            for label, argv in cases.items():
                with self.subTest(label):
                    code, out, err = self.run_main(argv)
                    self.assertEqual(code, 3, out + err)
                    self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)

    def test_index_that_is_not_utf8_exits_3_not_1(self) -> None:
        bad = self.repo.dir / "BAD.md"
        bad.write_bytes(b"\xff\xfe| x |\n")
        self.repo.commit("bad index")
        for mode in ("--check", "--write"):
            with self.subTest(mode):
                code, out, err = self.repo.run(mode, "BAD.md")
                self.assertEqual(code, 3, out + err)
                self.assertEqual(len([line for line in err.splitlines() if line.startswith("usage:")]), 1, err)
                self.assertNotIn("Traceback", err)

    def test_no_arguments_prints_only_the_usage_line(self) -> None:
        code, out, err = self.run_main([])
        self.assertEqual(code, 3)
        self.assertEqual(out, "")
        self.assertEqual(len(err.strip().splitlines()), 1, err)

    def test_script_exit_codes_as_a_process(self) -> None:
        good = self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        expected = {("--check", str(good)): 0, ("--check", "--write"): 3, (): 3}
        for args, code in expected.items():
            with self.subTest(args=args):
                done = subprocess.run(
                    [sys.executable, "-I", str(SCRIPT), "--root", str(self.repo.dir), *args],
                    capture_output=True, text=True, encoding="utf-8",
                )
                self.assertEqual(done.returncode, code, done.stdout + done.stderr)
        self.repo.write_index(self.repo.row("0" * 40, "f" * 64))
        self.repo.commit("drift")
        done = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--root", str(self.repo.dir), "--check", str(good)],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)


class ToolFaultTests(PinCase):
    """Exit 2: the gate could not decide; never reported as a red (1) and never as usage (3)."""

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = index_pins.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_not_inside_a_git_repository_exits_2(self) -> None:
        with tempfile.TemporaryDirectory(prefix="idxpin-norepo-") as outside:
            for mode in ("--check", "--write"):
                with self.subTest(mode):
                    code, out, err = self.run_main(["--root", outside, mode])
                    self.assertEqual(code, 2, out + err)
                    self.assertIn("not inside a git repository", err)
                    self.assertEqual(out, "")

    def test_git_that_cannot_be_started_exits_2(self) -> None:
        self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        with mock.patch.object(index_pins.subprocess, "run", side_effect=FileNotFoundError("git")):
            code, out, err = self.run_main(["--root", str(self.repo.dir), "--check", str(self.repo.dir / "INDEX.md")])
        self.assertEqual(code, 2, out + err)
        self.assertIn("git cannot be started", err)

    def test_unwritable_json_path_exits_2_even_when_the_index_has_drift(self) -> None:
        path = self.repo.write_index(self.repo.row("0" * 40, "f" * 64))
        self.repo.commit("index")
        original = path.read_text(encoding="utf-8")
        missing = self.repo.dir / "no-such-dir" / "report.json"
        for mode in ("--check", "--write"):
            with self.subTest(mode):
                code, out, err = self.repo.run(mode, "--json", str(missing), "INDEX.md")
                self.assertEqual(code, 2, out + err)
                self.assertIn("tool fault", err)
                self.assertFalse(missing.exists())
                self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_json_path_that_is_a_directory_exits_2(self) -> None:
        self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        code, out, err = self.repo.run("--check", "--json", str(self.repo.dir), "INDEX.md")
        self.assertEqual(code, 2, out + err)

    def test_an_unexpected_error_exits_2_never_1(self) -> None:
        self.repo.write_index(self.repo.row(self.repo.last_commit(), self.repo.digest()))
        self.repo.commit("index")
        with mock.patch.object(index_pins, "scan", side_effect=RuntimeError("boom")):
            code, out, err = self.run_main(["--root", str(self.repo.dir), "--check", str(self.repo.dir / "INDEX.md")])
        self.assertEqual(code, 2, out + err)
        self.assertIn("tool fault", err)
        self.assertIn("boom", err)

    def test_not_a_repository_exits_2_as_a_process(self) -> None:
        with tempfile.TemporaryDirectory(prefix="idxpin-norepo-") as outside:
            done = subprocess.run(
                [sys.executable, "-I", str(SCRIPT), "--root", outside, "--check"],
                capture_output=True, text=True, encoding="utf-8",
            )
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)


class ParsingHelperTests(unittest.TestCase):
    def test_extract_path_forms(self) -> None:
        self.assertEqual(index_pins.extract_path("[title](docs/a.md)"), "docs/a.md")
        self.assertEqual(index_pins.extract_path("`docs/b.json`"), "docs/b.json")
        self.assertEqual(index_pins.extract_path(" docs/c.md "), "docs/c.md")
        self.assertIsNone(index_pins.extract_path("no path here"))

    def test_classify_columns_groups_by_prefix_and_drops_incomplete_groups(self) -> None:
        cells = [" id ", " Revision ", " Digest ", " Leaf ", " Spec Leaf "]
        groups = index_pins.classify_columns(cells)
        self.assertEqual(groups, {"": {"rev": 1, "digest": 2, "leaf": 3}})
        state_cells = [" State ", " revision ", " digest ", " leaf "]
        self.assertEqual(index_pins.classify_columns(state_cells)[""]["state"], 0)

    def test_rewrite_cell_replaces_only_the_hash(self) -> None:
        old, new = "a" * 64, "b" * 64
        self.assertEqual(index_pins.rewrite_cell(f" `sha256:{old}` ", index_pins._HEX64, new), f" `sha256:{new}` ")
        self.assertIsNone(index_pins.rewrite_cell(" none ", index_pins._HEX64, new))

    def test_strict_pattern_does_not_bite_into_a_longer_hex_run(self) -> None:
        self.assertIsNone(index_pins._HEX64.search("c" * 65))
        self.assertIsNotNone(index_pins._HEX64.search("c" * 64))


if __name__ == "__main__":
    unittest.main()
