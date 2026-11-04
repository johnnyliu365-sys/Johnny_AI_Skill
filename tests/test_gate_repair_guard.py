"""Behavioural tests for the tool-repair guard (exit codes 0/1/2/3).

Every fixture is generated in a temporary directory, including the git repositories the
guard reads. Expected values are derived from what a fixture wrote or from what the tool
printed, never copied from the script.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zlib
from collections.abc import Sequence
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "johnny-project-takeover" / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import repair_guard  # noqa: E402

SCRIPT = _SCRIPTS / "repair_guard.py"
PY = sys.executable
GATE_DIR = "skills/johnny-project-takeover/scripts"
GATE_FILE = GATE_DIR + "/dispatch_lint.py"
ON_WINDOWS = sys.platform == "win32"
NON_CP950 = chr(0x0E01)  # outside code page 950
LINE_SEPARATOR = chr(0x2028)
NEXT_LINE = chr(0x85)
SURROGATE_ESCAPE = "\\ud800"  # a JSON escape that decodes to a lone surrogate


def git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test",
    )
    done = subprocess.run(
        ["git", "-c", "core.quotepath=true", "-c", "core.autocrlf=false", "-C", str(repo), *args],
        capture_output=True, env=env, check=False,
    )
    if done.returncode != 0:
        raise AssertionError(f"git {args} failed: {done.stderr.decode('utf-8', 'replace')}")
    return done.stdout.decode("utf-8", "replace").strip()


def git_raw(repo: Path, args: list[str], data: bytes) -> str:
    """Run git with `data` on standard input and return its standard output."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test",
    )
    done = subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, env=env, check=False)
    if done.returncode != 0:
        raise AssertionError(f"git {args} failed: {done.stderr.decode('utf-8', 'replace')}")
    return done.stdout.decode("utf-8", "replace").strip()


def dispatch_text(allow: object, protect: object, newline: str = "\n") -> str:
    return newline.join(
        ["title: x", f"repair_allowlist: {json.dumps(allow)}", f"protected_paths: {json.dumps(protect)}", ""]
    )


class Result:
    def __init__(self, code: int, out: str, err: str) -> None:
        self.code, self.out, self.err = code, out, err

    @property
    def lines(self) -> list[str]:
        return self.out.split("\n")[:-1] if self.out else []


class Fixture(unittest.TestCase):
    """A temporary repository whose single repair commit is built by each test."""

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        self.dispatch = self.root / "dispatch.yaml"

    def write(self, rel: str, content: str = "x\n") -> None:
        target = self.repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8"))

    def commit(self, message: str = "c") -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def base(self, *files: str) -> None:
        for rel in files:
            self.write(rel, "base\n")
        self.commit("base")

    def set_dispatch(self, allow: object, protect: object) -> None:
        self.dispatch.write_bytes(dispatch_text(allow, protect).encode("utf-8"))

    def run_guard(
        self, repair: str | None = None, *, repo: object = None, dispatch: object = None,
        extra: tuple[str, ...] = (), env: dict[str, str] | None = None,
    ) -> Result:
        args = [
            "--repo", str(self.repo if repo is None else repo),
            "--repair", repair if repair is not None else "HEAD",
            "--dispatch", str(self.dispatch if dispatch is None else dispatch),
            *extra,
        ]
        return run_cli(args, env)

    def defect_codes(self, result: Result) -> list[str]:
        return [line.split(" ", 1)[0] for line in result.lines]


def run_cli(args: list[str], env: dict[str, str] | None = None) -> Result:
    full_env = dict(os.environ)
    full_env["PYTHONUTF8"] = "1"
    if env:
        full_env.update(env)
    done = subprocess.run([PY, str(SCRIPT), *args], capture_output=True, env=full_env, check=False)
    return Result(
        done.returncode,
        done.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
        done.stderr.decode("utf-8", "replace").replace("\r\n", "\n"),
    )


class PassTests(Fixture):
    def test_a_change_to_an_allowlisted_tool_file_passes(self) -> None:
        self.base("tools/runner.py", "src/app.py")
        self.write("tools/runner.py", "fixed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["src/"])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"))
        self.assertEqual(result.err, "")

    def test_an_exact_path_entry_passes_only_that_path(self) -> None:
        self.base("tools/a.py", "tools/b.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.set_dispatch(["tools/a.py"], [])
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_the_summary_counts_every_changed_path(self) -> None:
        self.base("tools/a.py", "tools/b.py")
        self.write("tools/a.py", "1\n")
        self.write("tools/b.py", "2\n")
        self.write("tools/c.py", "3\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard(sha).out, "paths=3 defects=0\n")

    def test_an_empty_commit_passes_with_zero_paths(self) -> None:
        self.base("a.txt")
        sha = self.commit("empty")
        self.set_dispatch([], [])
        self.assertEqual(self.run_guard(sha).out, "paths=0 defects=0\n")

    def test_the_commit_may_be_named_by_a_ref(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard("main").code, 0)

    def test_crlf_and_bom_dispatch_files_parse_like_lf(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        text = dispatch_text(["tools/"], [], newline="\r\n")
        self.dispatch.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_the_blocks_are_found_among_other_dispatch_lines(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        text = "ticket: x\nsummary: y\n" + dispatch_text(["tools/"], []) + "tail: z\n"
        self.dispatch.write_bytes(text.encode("utf-8"))
        self.assertEqual(self.run_guard(sha).code, 0)


class DefectCodeTests(Fixture):
    def test_a_path_outside_the_allowlist_is_reported(self) -> None:
        self.base("tools/a.py", "src/app.py")
        self.write("src/app.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(result.lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} {'src/app.py'!r}"])
        self.assertEqual(result.err, "")

    def test_a_protected_path_is_reported_even_inside_the_allowlist(self) -> None:
        self.base("tools/a.py", "tools/secret.py")
        self.write("tools/secret.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["tools/secret.py"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.PROTECTED_PATH_TOUCHED])
        self.assertIn("'tools/secret.py'", result.lines[0])

    def test_a_protected_directory_entry_covers_everything_under_it(self) -> None:
        self.base("tools/a.py", "tools/deep/x/y.py")
        self.write("tools/deep/x/y.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["tools/deep/"])
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.PROTECTED_PATH_TOUCHED])

    def test_a_protected_path_outside_the_allowlist_reports_both_codes(self) -> None:
        self.base("src/app.py")
        self.write("src/app.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["src/"])
        self.assertEqual(
            self.defect_codes(self.run_guard(sha)),
            [repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED],
        )

    def test_a_merge_commit_is_not_a_single_parent_repair(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "checkout", "-q", "-b", "side")
        self.write("tools/b.py", "side\n")
        self.commit("side")
        git(self.repo, "checkout", "-q", "main")
        self.write("tools/c.py", "main\n")
        self.commit("main")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD")
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.REPAIR_NOT_SINGLE_PARENT])
        self.assertIn("2 parents", result.lines[0])

    def test_a_merge_is_still_checked_against_its_first_parent(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "checkout", "-q", "-b", "side")
        self.write("src/b.py", "side\n")
        self.commit("side")
        git(self.repo, "checkout", "-q", "main")
        self.write("tools/c.py", "main\n")
        self.commit("main")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
        self.set_dispatch(["tools/"], [])
        self.assertEqual(
            self.defect_codes(self.run_guard("HEAD")),
            [repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.OUTSIDE_ALLOWLIST],
        )

    def test_a_root_commit_is_not_a_single_parent_repair_and_its_paths_are_checked(self) -> None:
        self.write("tools/a.py")
        self.write("src/b.py")
        sha = self.commit("root")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(
            self.defect_codes(result),
            [repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.OUTSIDE_ALLOWLIST],
        )
        self.assertIn("root commit", result.lines[0])

    def test_a_rename_from_an_allowlisted_path_to_a_protected_one_is_reported(self) -> None:
        self.base("tools/a.py", "src/keep.py")
        (self.repo / "src").mkdir(exist_ok=True)
        git(self.repo, "mv", "tools/a.py", "src/a.py")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["src/"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertIn(
            f"{repair_guard.PROTECTED_PATH_TOUCHED} 'src/a.py'", "\n".join(result.lines),
        )
        self.assertNotIn("'tools/a.py'", "\n".join(result.lines))

    def test_a_rename_into_the_allowlist_from_a_protected_path_is_reported_on_its_old_side(self) -> None:
        self.base("src/a.py", "tools/keep.py")
        git(self.repo, "mv", "src/a.py", "tools/a.py")
        sha = self.commit()
        self.set_dispatch(["tools/"], ["src/"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED])
        self.assertTrue(all("'src/a.py'" in line for line in result.lines))

    def test_a_rename_between_two_outside_paths_reports_both_sides(self) -> None:
        self.base("src/a.py")
        git(self.repo, "mv", "src/a.py", "lib_a.py")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        joined = "\n".join(result.lines)
        self.assertEqual(result.code, 1)
        self.assertIn("'src/a.py'", joined)
        self.assertIn("'lib_a.py'", joined)

    def test_a_deletion_outside_the_allowlist_is_reported(self) -> None:
        self.base("tools/a.py", "src/app.py")
        git(self.repo, "rm", "-q", "src/app.py")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(result.lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'src/app.py'"])

    def test_an_addition_outside_the_allowlist_is_reported(self) -> None:
        self.base("tools/a.py")
        self.write("src/new.py")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.OUTSIDE_ALLOWLIST])

    def test_one_defect_is_one_line_and_the_three_codes_are_distinct(self) -> None:
        codes = {repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED, repair_guard.REPAIR_NOT_SINGLE_PARENT}
        self.assertEqual(len(codes), 3)
        self.base("src/a.py", "src/b.py")
        self.write("src/a.py", "1\n")
        self.write("src/b.py", "2\n")
        sha = self.commit()
        self.set_dispatch([], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(len(result.lines), 2)
        self.assertEqual(result.out.count("\n"), 2)


class GateScriptProtectionTests(Fixture):
    def test_a_gate_script_inside_the_allowlist_is_still_red(self) -> None:
        self.base(GATE_FILE)
        self.write(GATE_FILE, "changed\n")
        sha = self.commit()
        self.set_dispatch([GATE_DIR + "/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.PROTECTED_PATH_TOUCHED])

    def test_a_gate_script_is_protected_when_the_protected_list_is_empty(self) -> None:
        self.base(GATE_FILE)
        self.write(GATE_FILE, "changed\n")
        sha = self.commit()
        self.set_dispatch(["skills/"], [])
        self.assertEqual(self.run_guard(sha).code, 1)

    def test_a_new_file_in_the_gate_directory_is_red(self) -> None:
        self.base("tools/a.py")
        self.write(GATE_DIR + "/brand_new_gate.py")
        sha = self.commit()
        self.set_dispatch([GATE_DIR + "/"], [])
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.PROTECTED_PATH_TOUCHED])

    def test_a_rename_that_moves_a_protected_file_out_of_its_directory_is_red_on_its_old_side(self) -> None:
        self.base(GATE_FILE)
        git(self.repo, "mv", GATE_FILE, "tools_copy.py")
        sha = self.commit()
        self.set_dispatch(["tools_copy.py"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        joined = "\n".join(result.lines)
        self.assertIn(f"{repair_guard.PROTECTED_PATH_TOUCHED} {GATE_FILE!r}", joined)
        self.assertNotIn("'tools_copy.py'", joined)

    def test_a_deletion_of_a_gate_script_is_red(self) -> None:
        self.base(GATE_FILE)
        git(self.repo, "rm", "-q", GATE_FILE)
        sha = self.commit()
        self.set_dispatch([GATE_DIR + "/"], [])
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.PROTECTED_PATH_TOUCHED])

    def test_a_sibling_directory_of_the_gate_directory_is_not_protected(self) -> None:
        self.base("skills/johnny-project-takeover/scripts2/x.py")
        self.write("skills/johnny-project-takeover/scripts2/x.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["skills/johnny-project-takeover/scripts2/"], [])
        self.assertEqual(self.run_guard(sha).code, 0)


class UsageTests(Fixture):
    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_dispatch_without_the_allowlist_is_a_usage_error(self) -> None:
        sha = self.committed()
        self.dispatch.write_text('title: x\nprotected_paths: []\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual(result.code, 3)
        self.assertEqual(result.out, "")
        self.assertIn("repair_allowlist", result.err)
        self.assertIn("usage:", result.err)

    def test_a_dispatch_without_the_protected_list_is_a_usage_error(self) -> None:
        sha = self.committed()
        self.dispatch.write_text('title: x\nrepair_allowlist: ["tools/"]\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual(result.code, 3)
        self.assertIn("protected_paths", result.err)

    def test_a_dispatch_with_neither_block_is_a_usage_error(self) -> None:
        sha = self.committed()
        self.dispatch.write_text("title: x\n", encoding="utf-8")
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_an_indented_block_does_not_count(self) -> None:
        sha = self.committed()
        self.dispatch.write_text('  repair_allowlist: ["tools/"]\nprotected_paths: []\n', encoding="utf-8")
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_a_repeated_block_is_a_usage_error(self) -> None:
        sha = self.committed()
        self.dispatch.write_text(
            'repair_allowlist: ["tools/"]\nrepair_allowlist: ["src/"]\nprotected_paths: []\n', encoding="utf-8"
        )
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_null_values_are_usage_errors(self) -> None:
        sha = self.committed()
        for allow, protect in (("null", "[]"), ("[]", "null"), ('["tools/", null]', "[]"), ("[]", '[null]')):
            with self.subTest(allow=allow, protect=protect):
                self.dispatch.write_text(f"repair_allowlist: {allow}\nprotected_paths: {protect}\n", encoding="utf-8")
                self.assertEqual(self.run_guard(sha).code, 3)

    def test_values_that_are_not_an_array_of_strings_are_usage_errors(self) -> None:
        sha = self.committed()
        for value in ('"tools/"', "{}", "5", "[1]", '[["tools/"]]', "[", "tools/", "", "true", "NaN"):
            with self.subTest(value=value):
                self.dispatch.write_text(f"repair_allowlist: {value}\nprotected_paths: []\n", encoding="utf-8")
                self.assertEqual(self.run_guard(sha).code, 3)

    def test_an_empty_entry_is_refused(self) -> None:
        sha = self.committed()
        for entry in ("", " ", "   "):
            with self.subTest(entry=entry):
                self.set_dispatch([entry], [])
                self.assertEqual(self.run_guard(sha).code, 3)
        self.set_dispatch([], [""])
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_an_entry_with_a_dot_dot_segment_is_refused(self) -> None:
        sha = self.committed()
        for entry in ("../tools/", "tools/../src/", "tools/..", "..", "tools/../"):
            with self.subTest(entry=entry):
                self.set_dispatch([entry], [])
                self.assertEqual(self.run_guard(sha).code, 3)
                self.set_dispatch(["tools/"], [entry])
                self.assertEqual(self.run_guard(sha).code, 3)

    def test_a_dot_dot_inside_a_name_is_not_a_traversal(self) -> None:
        self.base("tools/a..b")
        self.write("tools/a..b", "fixed\n")
        sha = self.commit()
        self.set_dispatch(["tools/a..b"], [])
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_entries_that_are_not_normalised_relative_paths_are_refused(self) -> None:
        sha = self.committed()
        for entry in ("/tools/", "/", "C:/tools/", "tools\\", "tools//x", "./tools/", "tools/./x", "//"):
            with self.subTest(entry=entry):
                self.set_dispatch([entry], [])
                self.assertEqual(self.run_guard(sha).code, 3)

    def test_arguments_are_validated(self) -> None:
        sha = self.committed()
        self.set_dispatch(["tools/"], [])
        base = ["--repo", str(self.repo), "--repair", sha, "--dispatch", str(self.dispatch)]
        cases: dict[str, list[str]] = {
            "none": [],
            "missing repo": base[2:],
            "missing repair": base[:2] + base[4:],
            "missing dispatch": base[:4],
            "missing value": base[:5],
            "unknown option": [*base, "--other"],
            "stray positional": [*base, "extra"],
            "repeated option": [*base, "--repo", str(self.repo)],
            "equals form": ["--repo=" + str(self.repo), *base[2:]],
            "empty repo": ["--repo", "", *base[2:]],
            "blank repair": [*base[:2], "--repair", " ", *base[4:]],
            "option as commit": [*base[:2], "--repair", "--all", *base[4:]],
        }
        for name, args in cases.items():
            with self.subTest(name):
                result = run_cli(args)
                self.assertEqual(result.code, 3, result.err)
                self.assertEqual(result.out, "")
                self.assertTrue(result.err.startswith("usage:"))

    def test_a_control_character_in_an_argument_is_a_usage_error(self) -> None:
        sha = self.committed()
        self.set_dispatch(["tools/"], [])
        for bad in ("a\nb", "a\tb", "a\x00b", "a\x7fb"):
            with self.subTest(bad=repr(bad)):
                args = ["--repo", str(self.repo), "--repair", sha + bad, "--dispatch", str(self.dispatch)]
                if "\x00" in bad:
                    with self.assertRaises(repair_guard.UsageError):
                        repair_guard.parse_arguments(args)
                    continue
                result = run_cli(args)
                self.assertEqual(result.code, 3)
                self.assertEqual(result.out, "")
                self.assertEqual(result.err.count("\n"), 2, result.err)

    def test_a_lone_surrogate_in_an_argument_is_a_usage_error(self) -> None:
        with self.assertRaises(repair_guard.UsageError):
            repair_guard.parse_arguments(["--repo", "r", "--repair", "\udc80", "--dispatch", "d"])

class FaultTests(Fixture):
    def test_an_unknown_commit_is_a_tool_fault_carrying_gits_message(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(result.code, 2)
        self.assertEqual(result.out, "")
        self.assertIn("tool fault", result.err)
        self.assertIn("fatal", result.err)
        self.assertNotIn("Traceback", result.err)
        self.assertEqual(result.err.count("\n"), 1)

    def test_a_ref_that_names_no_commit_is_a_tool_fault(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard("no-such-ref").code, 2)

    def test_a_directory_that_is_not_a_repository_is_a_tool_fault(self) -> None:
        self.set_dispatch(["tools/"], [])
        plain = self.root / "plain"
        plain.mkdir()
        result = self.run_guard("HEAD", repo=plain, env={"GIT_CEILING_DIRECTORIES": str(self.root)})
        self.assertEqual(result.code, 2)
        self.assertIn("tool fault", result.err)
        self.assertNotIn("Traceback", result.err)

    def test_a_missing_repo_directory_is_a_tool_fault(self) -> None:
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", repo=self.root / "absent")
        self.assertEqual(result.code, 2)

    def test_a_subdirectory_of_a_repository_is_not_accepted_as_the_repository(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", repo=self.repo / "tools")
        self.assertEqual(result.code, 2)
        self.assertIn("top level", result.err)

    def test_an_unreadable_dispatch_is_a_tool_fault(self) -> None:
        self.base("tools/a.py")
        result = self.run_guard("HEAD", dispatch=self.root / "absent.yaml")
        self.assertEqual(result.code, 2)
        self.assertNotIn("Traceback", result.err)
        directory = self.root / "adir"
        directory.mkdir()
        self.assertEqual(self.run_guard("HEAD", dispatch=directory).code, 2)

    def test_git_that_cannot_be_started_is_a_tool_fault_not_a_red(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", env={"PATH": str(self.root)})
        self.assertEqual(result.code, 2)
        self.assertNotIn("Traceback", result.err)

    def test_an_unexpected_error_is_a_tool_fault_without_a_traceback(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(repair_guard, "require_repository_top", side_effect=RuntimeError("boom")):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = repair_guard.main(
                    ["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)]
                )
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("RuntimeError", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_a_shallow_boundary_commit_is_a_fault_not_a_root_red(self) -> None:
        self.base("a.txt")
        self.write("tools/a.py")
        self.commit("second")
        clone = self.root / "clone"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", self.repo.as_uri(), str(clone)],
            capture_output=True, check=True,
        )
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", repo=clone)
        self.assertEqual(result.code, 2)
        self.assertIn("shallow", result.err)

    def test_a_malformed_tree_body_is_a_tool_fault(self) -> None:
        oid = "0" * 40
        raw = b"\x11" * 20
        for body in (
            b"100644 a",
            b"100644 a\0" + raw[:-1],
            b"100644 a\0" + raw + b"x",
            b"100644a\0" + raw,
            b"10x644 a\0" + raw,
            b"100644 \0" + raw,
            b"100644 a/b\0" + raw,
            b"100644 .\0" + raw,
            b"100644 ..\0" + raw,
            b"100644 a\0" + raw + b"100644 a\0" + raw,
            b"12345678 a\0" + raw,
            b" a\0" + raw,
        ):
            with self.subTest(body=body):
                with self.assertRaises(repair_guard.ToolFault):
                    repair_guard.parse_tree(oid, body)
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.parse_tree("0" * 41, b"")

    def test_a_red_never_exits_two_and_a_fault_never_exits_one(self) -> None:
        self.base("tools/a.py", "src/b.py")
        self.write("src/b.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard(sha).code, 1)
        self.assertEqual(self.run_guard("no-such-ref").code, 2)
        self.assertEqual(self.run_guard(sha, dispatch=self.root / "absent.yaml").code, 2)


class PathMatchingTests(Fixture):
    def covers(self, entry: str, path: str, case_insensitive: bool = False) -> bool:
        return repair_guard.make_rule(entry, "t").covers(path, case_insensitive)

    def test_a_directory_entry_matches_by_segment_not_by_prefix(self) -> None:
        self.assertTrue(self.covers("tools/", "tools/x"))
        self.assertTrue(self.covers("tools/", "tools/deep/er/x"))
        self.assertFalse(self.covers("tools/", "tools2/x"))
        self.assertFalse(self.covers("tools/", "toolsx"))
        self.assertFalse(self.covers("tools/", "my/tools/x"))

    def test_a_path_equal_to_a_directory_entry_without_the_slash_is_not_covered(self) -> None:
        self.assertFalse(self.covers("tools/", "tools"))
        self.assertFalse(self.covers("tools/", "tools/"))

    def test_an_exact_entry_covers_only_that_path(self) -> None:
        self.assertTrue(self.covers("tools/a.py", "tools/a.py"))
        self.assertFalse(self.covers("tools/a.py", "tools/a.py2"))
        self.assertFalse(self.covers("tools", "tools/a.py"))
        self.assertFalse(self.covers("tools/a.p", "tools/a.py"))

    def test_url_encoded_text_is_not_decoded(self) -> None:
        self.assertFalse(self.covers("tools/", "%74ools/x"))
        self.assertFalse(self.covers("tools%2fa.py", "tools/a.py"))
        self.assertFalse(self.covers("tools/a%2epy", "tools/a.py"))
        self.assertTrue(self.covers("tools/a%2epy", "tools/a%2epy"))

    def test_case_is_compared_per_platform_rule(self) -> None:
        self.assertTrue(self.covers("Tools/", "tools/x", case_insensitive=True))
        self.assertTrue(self.covers("tools/A.py", "TOOLS/a.PY", case_insensitive=True))
        self.assertFalse(self.covers("Tools/", "tools/x", case_insensitive=False))
        self.assertFalse(self.covers("tools/A.py", "tools/a.py", case_insensitive=False))

    def test_the_cli_uses_the_platform_case_rule(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.set_dispatch(["Tools/"], [])
        expected = 0 if ON_WINDOWS else 1
        self.assertEqual(self.run_guard(sha).code, expected)

    def test_a_case_variant_of_a_protected_entry_is_protected_on_windows(self) -> None:
        defects = repair_guard.check_paths(["Src/a.py"], [repair_guard.make_rule("Src/", "t")], [repair_guard.make_rule("src/", "t")], True)
        self.assertEqual([d.code for d in defects], [repair_guard.PROTECTED_PATH_TOUCHED])

    def test_a_non_ascii_path_is_matched_unquoted(self) -> None:
        name = "tools/\u5de5\u5177/\u00e9\u0e01.py"
        self.base(name, "other.txt")
        self.write(name, "fixed\n")
        sha = self.commit()
        self.set_dispatch(["tools/\u5de5\u5177/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"))
        self.set_dispatch(["tools/\u5de5\u5177/"], [name])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertNotIn("\\3", result.out)
        self.assertIn(repr(name), result.out)

    def test_a_non_ascii_path_outside_the_allowlist_is_reported_with_its_real_name(self) -> None:
        name = "src/\u5de5.py"
        self.base(name)
        self.write(name, "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} {name!r}"])

    def test_the_empty_allowlist_makes_every_change_outside(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.set_dispatch([], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.OUTSIDE_ALLOWLIST]))

    def test_an_empty_protected_list_protects_nothing_but_the_gate_scripts(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_tree_parsing_reads_mode_name_and_id_exactly(self) -> None:
        first, second = bytes(range(20)), bytes(range(20, 40))
        body = b"100644 old name.py\0" + first + b"40000 new\xe5\xb7\xa5\0" + second + b"160000 sub\0" + first
        entries = repair_guard.parse_tree("0" * 40, body)
        self.assertEqual(sorted(entries), [b"new\xe5\xb7\xa5", b"old name.py", b"sub"])
        self.assertEqual(entries[b"old name.py"], repair_guard.TreeEntry("100644", first.hex()))
        self.assertEqual(entries[b"new\xe5\xb7\xa5"], repair_guard.TreeEntry("40000", second.hex()))
        self.assertTrue(entries[b"new\xe5\xb7\xa5"].is_tree)
        self.assertFalse(entries[b"sub"].is_tree)
        self.assertFalse(entries[b"old name.py"].is_tree)
        wide = repair_guard.parse_tree("0" * 64, b"100644 a\0" + bytes(range(32)))
        self.assertEqual(wide[b"a"].oid, bytes(range(32)).hex())

    def test_a_git_path_with_invalid_utf8_becomes_a_text_red_not_a_fault(self) -> None:
        self.base("tools/a.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        blob = git(self.repo, "rev-parse", "HEAD:tools/a.py")
        tree = git_raw(self.repo, ["hash-object", "-w", "-t", "tree", "--stdin"], b"100644 bad\xff.py\0" + bytes.fromhex(blob))
        sha = git(self.repo, "commit-tree", tree, "-p", parent, "-m", "odd name")
        self.set_dispatch(["bad/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1, result.err)
        self.assertIn(repair_guard.TEXT_VALUE_INVALID, self.defect_codes(result))
        self.assertEqual(result.err, "")


class TextValueTests(Fixture):
    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_lone_surrogate_in_an_entry_of_the_dispatch_is_a_red_not_a_fault(self) -> None:
        sha = self.committed()
        for block in ("repair_allowlist", "protected_paths"):
            with self.subTest(block=block):
                # the clean block is used (revision04): its allowlist covers the changed path
                other = "protected_paths: []" if block == "repair_allowlist" else 'repair_allowlist: ["tools/"]'
                self.dispatch.write_text(
                    f'{block}: ["tools/{SURROGATE_ESCAPE}"]\n{other}\n', encoding="utf-8"
                )
                result = self.run_guard(sha)
                self.assertEqual(result.code, 1)
                self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID])
                self.assertIn("lone surrogate", result.lines[0])
                self.assertEqual(result.err, "")

    def test_a_control_character_in_an_entry_of_the_dispatch_is_a_red(self) -> None:
        sha = self.committed()
        for escape in ("\\u0000", "\\u0001", "\\u001f", "\\u007f", "\\n", "\\t", "\\r"):
            with self.subTest(escape=escape):
                self.dispatch.write_text(
                    f'repair_allowlist: ["tools/{escape}x/"]\nprotected_paths: []\n', encoding="utf-8"
                )
                result = self.run_guard(sha)
                self.assertEqual(result.code, 1)
                self.assertEqual(len(result.lines), 1)
                self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID])

    def test_a_raw_control_character_in_a_block_line_is_a_red(self) -> None:
        sha = self.committed()
        self.dispatch.write_bytes(b'repair_allowlist: [\t"tools/"]\nprotected_paths: []\n')
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))

    def test_a_raw_encoded_surrogate_in_a_block_line_is_a_red(self) -> None:
        sha = self.committed()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/\xed\xa0\x80"]\nprotected_paths: []\n')
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(set(self.defect_codes(result)), {repair_guard.TEXT_VALUE_INVALID})
        self.assertEqual(result.err, "")

    def test_a_structure_error_outranks_a_text_red(self) -> None:
        sha = self.committed()
        self.dispatch.write_text(
            f'repair_allowlist: ["a{SURROGATE_ESCAPE}"]\nprotected_paths: ["../x"]\n', encoding="utf-8"
        )
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_a_text_red_is_reported_and_a_git_fault_after_it_goes_to_stderr(self) -> None:
        self.committed()
        self.dispatch.write_text(f'repair_allowlist: ["a{SURROGATE_ESCAPE}"]\nprotected_paths: []\n', encoding="utf-8")
        result = self.run_guard("no-such-ref")
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID])
        self.assertIn("tool fault", result.err)
        self.assertEqual(result.err.count("\n"), 1)

    def test_the_text_red_line_is_one_escaped_line(self) -> None:
        sha = self.committed()
        self.dispatch.write_text(
            'repair_allowlist: ["a\\nOUTSIDE_ALLOWLIST forged\\u2028b"]\nprotected_paths: []\n', encoding="utf-8"
        )
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(len(result.lines), 1)
        self.assertNotIn(LINE_SEPARATOR, result.out)
        self.assertFalse(result.out.startswith(repair_guard.OUTSIDE_ALLOWLIST))

    def test_a_changed_path_with_a_control_character_is_one_escaped_red_line(self) -> None:
        paths = ["tools/a\nOUTSIDE_ALLOWLIST 'forged'", "tools/b\x07", f"tools/c{LINE_SEPARATOR}{NEXT_LINE}"]
        defects = repair_guard.check_paths(paths, [repair_guard.make_rule("tools/", "t")], [], False)
        self.assertTrue(defects)
        for defect in defects:
            self.assertNotIn("\n", defect.line())
            self.assertNotIn(LINE_SEPARATOR, defect.line())
            self.assertNotIn(NEXT_LINE, defect.line())
        self.assertEqual([d.code for d in defects], [repair_guard.TEXT_VALUE_INVALID] * 2 + [])

    def test_a_forged_second_line_cannot_be_made_from_a_path(self) -> None:
        paths = ["x\n" + repair_guard.PROTECTED_PATH_TOUCHED + " 'forged'"]
        defects = repair_guard.check_paths(paths, [], [], False)
        for defect in defects:
            self.assertEqual(len(defect.line().splitlines()), 1)

    def test_a_git_failure_message_is_one_line_on_stderr(self) -> None:
        self.base("tools/a.py")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("bad\x01ref")
        self.assertEqual(result.code, 3)
        result = self.run_guard("bad\nref^{x}")
        self.assertEqual(result.code, 3)
        result = self.run_guard("bad ref with spaces")
        self.assertEqual(result.code, 2)
        self.assertEqual(result.err.count("\n"), 1)

    def test_a_name_that_cp950_cannot_encode_still_exits_per_the_contract(self) -> None:
        name = f"src/{NON_CP950}.py"
        self.base(name)
        self.write(name, "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha, env={"PYTHONUTF8": "0", "PYTHONIOENCODING": "cp950"})
        self.assertEqual(result.code, 1)
        self.assertEqual(len(result.lines), 1)
        self.assertTrue(result.out.startswith(repair_guard.OUTSIDE_ALLOWLIST))


class SubmodulePointerTests(Fixture):
    """S56-01: a moved submodule pointer always counts, whatever the repository says about ignoring it."""

    def pointer_repair(self, gitmodules_ignore: bool = False) -> str:
        self.base("tools/a.py")
        first = git(self.repo, "rev-parse", "HEAD")
        self.write("tools/b.py")
        second = self.commit("two")
        if gitmodules_ignore:
            self.write(
                ".gitmodules",
                '[submodule "vendor/lib"]\n\tpath = vendor/lib\n\turl = ./lib\n\tignore = all\n',
            )
            git(self.repo, "add", ".gitmodules")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{first},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "pointer")
        git(self.repo, "update-index", "--cacheinfo", f"160000,{second},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "bump")
        return git(self.repo, "rev-parse", "HEAD")

    def assert_outside(self, sha: str) -> None:
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(result.lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'vendor/lib'"])

    def test_a_pointer_bump_outside_the_allowlist_is_red(self) -> None:
        self.assert_outside(self.pointer_repair())

    def test_a_tracked_submodule_list_with_ignore_all_does_not_hide_the_bump(self) -> None:
        self.assert_outside(self.pointer_repair(gitmodules_ignore=True))

    def test_the_repository_setting_ignore_submodules_all_does_not_hide_the_bump(self) -> None:
        sha = self.pointer_repair()
        git(self.repo, "config", "diff.ignoreSubmodules", "all")
        self.assert_outside(sha)

    def test_both_the_tracked_list_and_the_repository_setting_together_do_not_hide_the_bump(self) -> None:
        sha = self.pointer_repair(gitmodules_ignore=True)
        git(self.repo, "config", "diff.ignoreSubmodules", "all")
        self.assert_outside(sha)

    def test_a_per_submodule_setting_in_the_repository_configuration_does_not_hide_the_bump(self) -> None:
        sha = self.pointer_repair()
        git(self.repo, "config", "submodule.vendor/lib.ignore", "all")
        self.assert_outside(sha)

    def test_a_pointer_under_a_protected_directory_is_protected_with_ignore_all(self) -> None:
        sha = self.pointer_repair(gitmodules_ignore=True)
        self.set_dispatch(["vendor/lib"], ["vendor/"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(result.lines, [f"{repair_guard.PROTECTED_PATH_TOUCHED} 'vendor/lib': covered by 'vendor/'"])

    def test_an_allowlisted_pointer_passes_and_is_counted_with_ignore_all(self) -> None:
        sha = self.pointer_repair(gitmodules_ignore=True)
        self.set_dispatch(["vendor/lib"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"))

    def test_an_external_diff_driver_and_a_text_conversion_do_not_change_the_result(self) -> None:
        sha = self.pointer_repair(gitmodules_ignore=True)
        git(self.repo, "config", "diff.external", "no-such-diff-driver")
        git(self.repo, "config", "diff.ignoreSubmodules", "all")
        self.assert_outside(sha)


class DispatchBytesTests(Fixture):
    """S56-02 and S56-03: a bad byte or raw control character matters on a block line and only there."""

    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_raw_control_character_inside_a_json_string_is_a_red(self) -> None:
        sha = self.committed()
        for raw in (b"\x01", b"\x1f", b"\t", b"\x7f", b"\x0b", b"\r"):
            for block in ("repair_allowlist", "protected_paths"):
                with self.subTest(raw=raw, block=block):
                    # the clean block is used (revision04): its allowlist covers the changed path
                    other = "protected_paths: []" if block == "repair_allowlist" else 'repair_allowlist: ["tools/"]'
                    self.dispatch.write_bytes(
                        f'{block}: ["tools/'.encode() + raw + b'x/"]\n' + f"{other}\n".encode()
                    )
                    result = self.run_guard(sha)
                    self.assertEqual(result.code, 1, result.err)
                    self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID])
                    self.assertEqual(result.err, "")

    def test_a_raw_control_character_outside_a_json_string_is_a_red(self) -> None:
        sha = self.committed()
        for raw in (b"\x0b", b"\x0c", b"\x00", b"\x7f", b"\x1c"):
            with self.subTest(raw=raw):
                self.dispatch.write_bytes(b'repair_allowlist: [' + raw + b'"tools/"]\nprotected_paths: []\n')
                result = self.run_guard(sha)
                self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))

    def test_an_undecodable_byte_on_a_block_line_is_a_red_inside_or_outside_a_string(self) -> None:
        sha = self.committed()
        for line in (
            b'repair_allowlist: ["\xff"]\nprotected_paths: []\n',
            b'repair_allowlist: ["tools/"]\nprotected_paths: ["a\xc3"]\n',
            b'repair_allowlist: [\xff"tools/"]\nprotected_paths: []\n',
            b'repair_allowlist: ["tools/"]\xfe\nprotected_paths: []\n',
        ):
            with self.subTest(line=line):
                self.dispatch.write_bytes(line)
                result = self.run_guard(sha)
                self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))
                self.assertEqual(result.err, "")
                self.assertEqual(len(result.lines), 1)

    def test_an_undecodable_byte_or_control_character_on_another_line_is_ignored(self) -> None:
        sha = self.committed()
        for noise in (b"\xff\xfe", b"\x01\x02", b"a\x00b", b"\xed\xa0\x80", b"a\x0bb", b"a\rb"):
            with self.subTest(noise=noise):
                self.dispatch.write_bytes(
                    b"title: " + noise + b'\nrepair_allowlist: ["tools/"]\nprotected_paths: []\nnote: ' + noise + b"\n"
                )
                result = self.run_guard(sha)
                self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_a_structure_error_outranks_a_bad_byte(self) -> None:
        sha = self.committed()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/\xff", 5]\nprotected_paths: []\n')
        self.assertEqual(self.run_guard(sha).code, 3)
        self.dispatch.write_bytes(b'repair_allowlist: [\xff"tools/"\nprotected_paths: []\n')
        self.assertEqual(self.run_guard(sha).code, 3)

    def test_a_bad_byte_in_a_line_that_is_only_a_prefix_of_a_block_key_is_ignored(self) -> None:
        sha = self.committed()
        self.dispatch.write_bytes(
            b'  repair_allowlist: [\xff]\nrepair_allowlist: ["tools/"]\nprotected_paths: []\n'
        )
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_a_bad_byte_in_the_dispatch_is_still_a_red_when_git_cannot_answer(self) -> None:
        self.committed()
        self.dispatch.write_bytes(b'repair_allowlist: ["\xff"]\nprotected_paths: []\n')
        result = self.run_guard("no-such-ref")
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))
        self.assertIn("tool fault", result.err)


class RedBeforeFaultTests(Fixture):
    def test_a_red_found_before_git_fails_is_reported_and_the_exit_is_one(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "checkout", "-q", "-b", "side")
        self.write("tools/b.py", "side\n")
        self.commit("side")
        git(self.repo, "checkout", "-q", "main")
        self.write("tools/c.py", "main\n")
        self.commit("main")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
        self.set_dispatch(["tools/"], [])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(repair_guard, "diff_trees", side_effect=repair_guard.ToolFault("boom")):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual(code, 1)
        self.assertEqual([line.split(" ", 1)[0] for line in out.getvalue().splitlines()], [repair_guard.REPAIR_NOT_SINGLE_PARENT])
        self.assertEqual(err.getvalue(), "repair_guard.py: tool fault: boom\n")

    def test_a_fault_with_no_red_is_still_exit_two(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.set_dispatch(["tools/"], [])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(repair_guard, "diff_trees", side_effect=repair_guard.ToolFault("boom")):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("boom", err.getvalue())

    def test_a_root_commit_red_survives_an_unreadable_tree_walk(self) -> None:
        self.write("tools/a.py")
        self.commit("root")
        self.set_dispatch(["tools/"], [])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(repair_guard, "diff_trees", side_effect=RuntimeError("odd")):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual(code, 1)
        self.assertIn(repair_guard.REPAIR_NOT_SINGLE_PARENT, out.getvalue())
        self.assertIn("RuntimeError", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())


class UnwritableStreamTests(Fixture):
    """S56-05: output that cannot be written is exit 2, never Python's 120 and never a silent success."""

    def ready(self, red: bool) -> list[str]:
        self.base("tools/a.py", "src/b.py")
        self.write("src/b.py" if red else "tools/a.py", "changed\n")
        sha = self.commit()
        self.set_dispatch(["tools/"], [])
        return ["--repo", str(self.repo), "--repair", sha, "--dispatch", str(self.dispatch)]

    def run_with_dead_stream(self, args: list[str], dead: str) -> subprocess.CompletedProcess[bytes]:
        reader, writer = os.pipe()
        os.close(reader)
        env = dict(os.environ, PYTHONUTF8="1")
        try:
            if dead == "stdout":
                return subprocess.run([PY, str(SCRIPT), *args], stdout=writer, stderr=subprocess.PIPE, env=env, check=False)
            return subprocess.run([PY, str(SCRIPT), *args], stdout=subprocess.PIPE, stderr=writer, env=env, check=False)
        finally:
            os.close(writer)

    def test_a_pass_whose_stdout_is_dead_is_exit_two(self) -> None:
        done = self.run_with_dead_stream(self.ready(red=False), "stdout")
        self.assertEqual(done.returncode, 2)

    def test_a_red_whose_stdout_is_dead_is_exit_two(self) -> None:
        done = self.run_with_dead_stream(self.ready(red=True), "stdout")
        self.assertEqual(done.returncode, 2)

    def test_a_usage_error_whose_stderr_is_dead_is_exit_two(self) -> None:
        self.ready(red=False)
        done = self.run_with_dead_stream(["--repo"], "stderr")
        self.assertEqual(done.returncode, 2)

    def test_a_fault_whose_stderr_is_dead_is_exit_two_and_prints_nothing_else(self) -> None:
        args = self.ready(red=False)
        args[3] = "no-such-ref"
        done = self.run_with_dead_stream(args, "stderr")
        self.assertEqual((done.returncode, done.stdout), (2, b""))

    def test_a_working_stdout_with_a_dead_stderr_still_passes(self) -> None:
        done = self.run_with_dead_stream(self.ready(red=False), "stderr")
        self.assertEqual((done.returncode, done.stdout.replace(b"\r", b"")), (0, b"paths=1 defects=0\n"))

    def test_streams_that_raise_or_do_not_exist_are_exit_two_in_process(self) -> None:
        args = self.ready(red=False)

        class Dead(io.StringIO):
            def __init__(self, fail_on: str) -> None:
                super().__init__()
                self.fail_on = fail_on

            def write(self, text: str) -> int:
                if self.fail_on == "write":
                    raise OSError(32, "broken pipe")
                return super().write(text)

            def flush(self) -> None:
                if self.fail_on == "flush":
                    raise ValueError("I/O operation on closed file")

        for name, make in (
            ("write", lambda: Dead("write")),
            ("flush", lambda: Dead("flush")),
            ("none", lambda: None),
        ):
            with self.subTest(stream=name):
                with mock.patch.object(sys, "stdout", make()):
                    code = repair_guard.main(args)
                self.assertEqual(code, 2)


class CaseRuleTests(Fixture):
    """S56-04: on Windows the allowlist never widens and protection never narrows."""

    STRASSE = "straße"
    KELVIN = "K"

    def rule(self, entry: str) -> repair_guard.PathRule:
        return repair_guard.make_rule(entry, "t")

    def test_an_allowlist_entry_ignores_ascii_case_only(self) -> None:
        self.assertTrue(self.rule("Tools/").covers("tools/x", True))
        self.assertTrue(self.rule("tools/A.py").covers("TOOLS/a.PY", True))
        self.assertTrue(self.rule(self.STRASSE + "/").covers("STRAßE/x", True))
        self.assertFalse(self.rule("strasse/").covers(self.STRASSE + "/a.py", True))
        self.assertFalse(self.rule(self.STRASSE + "/").covers("strasse/a.py", True))
        self.assertFalse(self.rule("kit/").covers(self.KELVIN + "it/a.py", True))
        self.assertFalse(self.rule("café/").covers("CAFÉ/x", True))
        self.assertFalse(self.rule("tools/").covers("Tools/x", False))

    def test_a_protected_entry_folds_case_fully(self) -> None:
        allow = [self.rule("strasse/"), self.rule(self.STRASSE + "/"), self.rule("kit/"), self.rule(self.KELVIN + "it/")]
        for protected, path in (
            (self.STRASSE + "/", "strasse/x"),
            ("strasse/", self.STRASSE + "/x"),
            ("kit/", self.KELVIN + "it/x"),
            (self.KELVIN + "it/", "KIT/x"),
            ("Tools/a.py", "tools/A.PY"),
        ):
            with self.subTest(protected=protected, path=path):
                defects = repair_guard.check_paths([path], allow + [self.rule("tools/")], [self.rule(protected)], True)
                self.assertIn(repair_guard.PROTECTED_PATH_TOUCHED, [d.code for d in defects])

    def test_a_protected_entry_does_not_fold_when_case_matters(self) -> None:
        defects = repair_guard.check_paths(
            ["strasse/x"], [self.rule("strasse/")], [self.rule(self.STRASSE + "/")], False
        )
        self.assertEqual(defects, [])

    def test_the_gate_directory_is_protected_under_full_folding(self) -> None:
        for path in (
            "Skills/Johnny-Project-Takeover/Scripts/x.py",
            "SKILLS/JOHNNY-PROJECT-TAKEOVER/SCRIPTS/dispatch_lint.py",
            "skills/johnny-project-ta" + self.KELVIN + "eover/scripts/x.py",
        ):
            with self.subTest(path=path):
                defects = repair_guard.check_paths([path], [self.rule(path)], [], True)
                self.assertEqual([d.code for d in defects], [repair_guard.PROTECTED_PATH_TOUCHED])
                self.assertEqual(repair_guard.check_paths([path], [self.rule(path)], [], False), [])

    def test_the_cli_protects_a_case_variant_of_the_gate_directory_on_windows_only(self) -> None:
        variant = "Skills/Johnny-Project-Takeover/Scripts/dispatch_lint.py"
        self.base("tools/a.py")
        self.write(variant)
        sha = self.commit()
        self.set_dispatch(["Skills/"], [])
        result = self.run_guard(sha)
        if ON_WINDOWS:
            self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.PROTECTED_PATH_TOUCHED]))
        else:
            self.assertEqual(result.code, 0)

    def test_the_cli_does_not_widen_the_allowlist_to_a_sharp_s_path_on_windows(self) -> None:
        name = f"{self.STRASSE}/a.py"
        self.base("tools/a.py")
        self.write(name)
        sha = self.commit()
        self.set_dispatch(["strasse/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.OUTSIDE_ALLOWLIST]))


class EnvironmentAndObjectTests(Fixture):
    """S56-06: the repository is the one --repo names, as git stores it, whatever the host says."""

    SELECTORS = (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
        "GIT_CEILING_DIRECTORIES",
    )

    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_replace_ref_does_not_hide_a_protected_change(self) -> None:
        self.base("tools/a.py", "src/app.py")
        base = git(self.repo, "rev-parse", "HEAD")
        self.write("src/app.py", "changed\n")
        sha = self.commit("repair")
        harmless = git(self.repo, "commit-tree", f"{base}^{{tree}}", "-p", base, "-m", "harmless")
        git(self.repo, "replace", "-f", sha, harmless)
        self.assertEqual(git(self.repo, "diff", "--name-only", base, sha), "")  # the replacement works for plain git
        self.set_dispatch(["tools/"], ["src/"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(
            self.defect_codes(result), [repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED]
        )

    def test_the_selecting_variables_are_removed_from_every_git_child(self) -> None:
        values = {name: "x" for name in self.SELECTORS}
        with mock.patch.dict(os.environ, values):
            environment = repair_guard._git_environment()
        for name in self.SELECTORS:
            with self.subTest(name=name):
                self.assertNotIn(name, environment)

    def test_git_object_directory_in_the_environment_changes_nothing(self) -> None:
        sha = self.committed()
        empty = self.root / "empty-objects"
        empty.mkdir()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha, env={"GIT_OBJECT_DIRECTORY": str(empty)})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_git_work_tree_in_the_environment_changes_nothing(self) -> None:
        sha = self.committed()
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha, env={"GIT_WORK_TREE": str(elsewhere)})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_git_alternate_object_directories_do_not_supply_a_commit(self) -> None:
        self.committed()
        other = self.root / "other"
        other.mkdir()
        git(other, "init", "-q", "-b", "main")
        (other / "z.txt").write_text("z\n", encoding="utf-8")
        git(other, "add", "-A")
        git(other, "commit", "-q", "-m", "elsewhere")
        foreign = git(other, "rev-parse", "HEAD")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(foreign, env={"GIT_ALTERNATE_OBJECT_DIRECTORIES": str(other / ".git" / "objects")})
        self.assertEqual(result.code, 2)

    def test_git_namespace_in_the_environment_changes_nothing(self) -> None:
        self.committed()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", env={"GIT_NAMESPACE": "ns"})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_git_index_file_in_the_environment_changes_nothing(self) -> None:
        self.committed()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", env={"GIT_INDEX_FILE": str(self.root / "no-such-index")})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_a_git_error_of_many_lines_is_one_line_on_stderr(self) -> None:
        sha = self.committed()
        loose = self.repo / ".git" / "objects" / sha[:2] / sha[2:]
        os.chmod(loose, 0o666)
        loose.write_bytes(b"garbage")
        self.set_dispatch(["tools/"], [])
        reference = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "--verify", f"{sha}^{{commit}}"], capture_output=True, check=False
        )
        self.assertGreater(len(reference.stderr.decode("utf-8", "replace").strip().splitlines()), 1)
        result = self.run_guard(sha)
        self.assertEqual(result.code, 2)
        self.assertEqual(result.err.count("\n"), 1, result.err)
        self.assertTrue(result.err.startswith("repair_guard.py: tool fault:"))

    def test_a_multi_line_git_message_is_quoted_into_one_line(self) -> None:
        stderr = b"error: first\nOUTSIDE_ALLOWLIST 'forged'\r\nfatal: last\n"
        done = subprocess.CompletedProcess(["git"], 128, stdout=b"", stderr=stderr)
        with mock.patch.object(repair_guard.subprocess, "run", return_value=done):
            with self.assertRaises(repair_guard.ToolFault) as caught:
                repair_guard.run_git("anywhere", ["rev-parse", "x"])
        self.assertEqual(str(caught.exception).splitlines(), [str(caught.exception)])
        self.assertIn("forged", str(caught.exception))

    def test_a_root_commit_in_a_sha256_repository_is_compared_with_that_formats_empty_tree(self) -> None:
        repo = self.root / "repo256"
        repo.mkdir()
        probe = subprocess.run(["git", "-C", str(repo), "init", "-q", "--object-format=sha256", "-b", "main"], capture_output=True, check=False)
        if probe.returncode != 0:
            self.skipTest("this git cannot create a SHA-256 repository: " + probe.stderr.decode("utf-8", "replace").strip())
        git(repo, "config", "user.name", "t")
        (repo / "tools").mkdir()
        (repo / "tools" / "a.py").write_text("x\n", encoding="utf-8")
        (repo / "b.py").write_text("x\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "root")
        self.assertEqual(len(git(repo, "rev-parse", "HEAD")), 64)
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", repo=repo)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(
            self.defect_codes(result), [repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.OUTSIDE_ALLOWLIST]
        )
        self.assertIn("'b.py'", result.lines[1])


class RawHistoryTests(Fixture):
    """S56-09 and S56-10: parents and trees come from raw commit objects, whatever git is told about history."""

    def plain_parents(self, sha: str, repo: Path | None = None, env: dict[str, str] | None = None) -> list[str]:
        """The parents plain git reports (grafts and replace refs applied)."""
        full = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        full.update(env or {})
        done = subprocess.run(
            ["git", "-C", str(repo or self.repo), "rev-list", "--parents", "-n", "1", sha],
            capture_output=True, env=full, check=False,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout.decode("utf-8", "replace").split()[1:]

    def twin_of(self, sha: str) -> str:
        """A root commit with exactly the tree of `sha`."""
        return git(self.repo, "commit-tree", f"{sha}^{{tree}}", "-m", "twin")

    def repair_of(self, kind: str) -> str:
        """A repair that changes a gate script, as a single-parent, a merge or a root commit."""
        if kind == "single":
            self.base(GATE_FILE, "tools/a.py")
            self.write(GATE_FILE, "changed\n")
            return self.commit("repair")
        if kind == "merge":
            self.base(GATE_FILE, "tools/a.py")
            git(self.repo, "checkout", "-q", "-b", "side")
            self.write(GATE_FILE, "side\n")
            self.commit("side")
            git(self.repo, "checkout", "-q", "main")
            self.write("tools/c.py", "main\n")
            self.commit("main")
            git(self.repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
            return git(self.repo, "rev-parse", "HEAD")
        self.write(GATE_FILE, "root\n")
        return self.commit("root")

    EXPECTED = {
        "single": [repair_guard.PROTECTED_PATH_TOUCHED],
        "merge": [repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.PROTECTED_PATH_TOUCHED],
        "root": [repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.PROTECTED_PATH_TOUCHED],
    }

    def graft_case(self, kind: str, where: str) -> None:
        sha = self.repair_of(kind)
        self.set_dispatch([GATE_DIR + "/"], [])
        repo = self.repo
        if where == "linked":
            repo = self.root / "linked"
            git(self.repo, "worktree", "add", "-q", "--detach", str(repo), sha)
        before = self.run_guard(sha, repo=repo)
        self.assertEqual(before.code, 1, before.err)
        self.assertEqual(self.defect_codes(before), self.EXPECTED[kind])
        twin = self.twin_of(sha)
        env: dict[str, str] | None = None
        if where == "environment":
            graft_file = self.root / "graft-file.txt"
            graft_file.write_text(f"{sha} {twin}\n", encoding="utf-8")
            env = {"GIT_GRAFT_FILE": str(graft_file)}
        else:  # the repository's own file, which a linked work tree reads from the common directory
            (self.repo / ".git" / "info" / "grafts").write_text(f"{sha} {twin}\n", encoding="utf-8")
        # The graft is in force for plain git: it sees the twin as the only parent, so a naive
        # reading of history would compare the repair with a commit that has its own tree.
        self.assertEqual(self.plain_parents(sha, repo, env), [twin])
        after = self.run_guard(sha, repo=repo, env=env)
        self.assertEqual((after.code, after.out), (before.code, before.out), after.err)

    def test_a_graft_file_in_the_repository_does_not_re_parent_a_single_parent_repair(self) -> None:
        self.graft_case("single", "repository")

    def test_a_graft_file_in_the_repository_does_not_re_parent_a_merge(self) -> None:
        self.graft_case("merge", "repository")

    def test_a_graft_file_in_the_repository_does_not_re_parent_a_root_commit(self) -> None:
        self.graft_case("root", "repository")

    def test_a_graft_file_in_the_common_directory_of_a_linked_work_tree_does_not_re_parent_a_single_parent_repair(self) -> None:
        self.graft_case("single", "linked")

    def test_a_graft_file_in_the_common_directory_of_a_linked_work_tree_does_not_re_parent_a_merge(self) -> None:
        self.graft_case("merge", "linked")

    def test_a_graft_file_in_the_common_directory_of_a_linked_work_tree_does_not_re_parent_a_root_commit(self) -> None:
        self.graft_case("root", "linked")

    def test_a_graft_file_named_by_the_environment_does_not_re_parent_a_single_parent_repair(self) -> None:
        self.graft_case("single", "environment")

    def test_a_graft_file_named_by_the_environment_does_not_re_parent_a_merge(self) -> None:
        self.graft_case("merge", "environment")

    def test_a_graft_file_named_by_the_environment_does_not_re_parent_a_root_commit(self) -> None:
        self.graft_case("root", "environment")

    def shallow_case(self, where: str) -> None:
        sha = self.repair_of("single")
        self.set_dispatch([GATE_DIR + "/"], [])
        before = self.run_guard(sha)
        self.assertEqual((before.code, self.defect_codes(before)), (1, self.EXPECTED["single"]))
        env: dict[str, str] | None = None
        if where == "environment":
            shallow_file = self.root / "shallow-file.txt"
            shallow_file.write_text(sha + "\n", encoding="utf-8")
            env = {"GIT_SHALLOW_FILE": str(shallow_file)}
        else:
            (self.repo / ".git" / "shallow").write_text(sha + "\n", encoding="utf-8")
        self.assertEqual(self.plain_parents(sha, env=env), [])  # plain git sees a boundary commit
        after = self.run_guard(sha, env=env)
        self.assertEqual((after.code, after.out), (before.code, before.out), after.err)

    def test_a_shallow_file_in_the_repository_does_not_turn_the_repair_into_a_root_commit(self) -> None:
        self.shallow_case("repository")

    def test_a_shallow_file_named_by_the_environment_does_not_turn_the_repair_into_a_root_commit(self) -> None:
        self.shallow_case("environment")

    def test_a_replacement_commit_whose_parent_has_the_repairs_tree_does_not_hide_the_change(self) -> None:
        self.base("tools/a.py", "src/app.py")
        self.write("src/app.py", "changed\n")
        sha = self.commit("repair")
        twin = self.twin_of(sha)
        harmless = git(self.repo, "commit-tree", f"{sha}^{{tree}}", "-p", twin, "-m", "harmless")
        git(self.repo, "replace", "-f", sha, harmless)
        self.assertEqual(self.plain_parents(sha), [twin])  # for plain git the repair now follows a twin
        self.set_dispatch(["tools/"], ["src/"])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(
            self.defect_codes(result), [repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED]
        )

    def test_a_replacement_of_the_first_parent_does_not_hide_the_change(self) -> None:
        self.base("tools/a.py", "src/app.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        self.write("src/app.py", "changed\n")
        sha = self.commit("repair")
        impostor = git(self.repo, "commit-tree", f"{sha}^{{tree}}", "-m", "impostor")
        git(self.repo, "replace", "-f", parent, impostor)
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.OUTSIDE_ALLOWLIST]))

    def test_a_replacement_of_a_merge_does_not_hide_that_it_is_a_merge(self) -> None:
        sha = self.repair_of("merge")
        single = git(self.repo, "commit-tree", f"{sha}^{{tree}}", "-p", f"{sha}^1", "-m", "single")
        git(self.repo, "replace", "-f", sha, single)
        self.set_dispatch([GATE_DIR + "/"], [])
        result = self.run_guard(sha)
        self.assertEqual(self.defect_codes(result), self.EXPECTED["merge"])

    def test_the_git_command_line_switches_replace_objects_off(self) -> None:
        seen: list[list[str]] = []

        def capture(command: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
            seen.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

        with mock.patch.object(repair_guard.subprocess, "run", side_effect=capture):
            repair_guard.run_git("anywhere", ["cat-file", "--batch"])
        self.assertEqual(len(seen), 1)
        self.assertIn("--no-replace-objects", seen[0][:3])

    def test_the_git_environment_switches_replace_objects_and_lazy_fetch_off(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_NO_REPLACE_OBJECTS": "0", "GIT_NO_LAZY_FETCH": "0"}):
            environment = repair_guard._git_environment()
        self.assertEqual(environment["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(environment["GIT_NO_LAZY_FETCH"], "1")
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GIT_NO_REPLACE_OBJECTS", None)
            os.environ.pop("GIT_NO_LAZY_FETCH", None)
            environment = repair_guard._git_environment()
        self.assertEqual(environment["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(environment["GIT_NO_LAZY_FETCH"], "1")

    def test_a_first_parent_the_store_cannot_serve_is_a_fault_after_the_merge_red(self) -> None:
        sha = self.repair_of("merge")
        first = git(self.repo, "rev-parse", f"{sha}^1")
        loose = self.repo / ".git" / "objects" / first[:2] / first[2:]
        os.chmod(loose, 0o666)
        loose.unlink()
        self.set_dispatch([GATE_DIR + "/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertEqual(self.defect_codes(result), [repair_guard.REPAIR_NOT_SINGLE_PARENT])
        self.assertIn("tool fault", result.err)
        self.assertEqual(result.err.count("\n"), 1)

    def test_a_first_parent_the_store_cannot_serve_is_exit_two_without_a_red(self) -> None:
        self.base("tools/a.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        loose = self.repo / ".git" / "objects" / parent[:2] / parent[2:]
        os.chmod(loose, 0o666)
        loose.unlink()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (2, ""))
        self.assertIn("cannot be read from the object store", result.err)

    def test_an_object_that_is_not_a_commit_is_a_fault(self) -> None:
        self.base("tools/a.py")
        tree = git(self.repo, "rev-parse", "HEAD^{tree}")
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.read_commit(str(self.repo), tree)
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.read_commit(str(self.repo), "0" * 40)

    def test_the_parents_are_the_parent_lines_that_follow_the_tree_line(self) -> None:
        tree, first, second, late = "1" * 40, "2" * 40, "3" * 40, "4" * 40
        body = (
            f"tree {tree}\nparent {first}\nparent {second}\nauthor a <a@x> 1 +0000\n"
            f"parent {late}\ncommitter a <a@x> 1 +0000\ngpgsig -----BEGIN\n parent {late}\n\nparent {late}\n"
        ).encode("ascii")
        commit = repair_guard.parse_commit("0" * 40, body)
        self.assertEqual((commit.tree, commit.parents), (tree, (first, second)))
        root = repair_guard.parse_commit("0" * 40, f"tree {tree}\nauthor a\n\nmessage\n".encode("ascii"))
        self.assertEqual(root.parents, ())

    def test_a_commit_header_that_is_not_an_object_id_is_a_fault(self) -> None:
        good = "a" * 40
        for body in (
            b"",
            b"author a\n\nm\n",
            f"tree {good[:-1]}\n\n".encode("ascii"),
            f"tree {good}\nparent xyz\n\n".encode("ascii"),
            f"tree {good.upper()}\n\n".encode("ascii"),
            f"tree {'1' * 64}\n\n".encode("ascii"),
        ):
            with self.subTest(body=body):
                with self.assertRaises(repair_guard.ToolFault):
                    repair_guard.parse_commit("0" * 40, body)

    def test_a_revision_that_goes_through_ancestry_or_a_path_is_a_usage_error(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.set_dispatch(["tools/"], [])
        for name in ("HEAD~1", "HEAD^", "HEAD^1", "main^{commit}", "HEAD:tools/a.py", "main@{1}", "HEAD~"):
            with self.subTest(name=name):
                result = self.run_guard(name)
                self.assertEqual((result.code, result.out), (3, ""))
                self.assertTrue(result.err.startswith("usage:"))
        self.assertEqual(self.run_guard("main").code, 0)
        self.assertEqual(self.run_guard("HEAD").code, 0)

    def test_a_bare_repository_gives_a_verdict(self) -> None:
        self.base("tools/a.py", "src/b.py")
        self.write("tools/a.py", "fixed\n")
        inside = self.commit("inside")
        self.write("src/b.py", "changed\n")
        outside = self.commit("outside")
        bare = self.root / "bare.git"
        git(self.root, "clone", "-q", "--bare", str(self.repo), str(bare))
        self.set_dispatch(["tools/"], [])
        passed = self.run_guard(inside, repo=bare)
        self.assertEqual((passed.code, passed.out), (0, "paths=1 defects=0\n"), passed.err)
        red = self.run_guard(outside, repo=bare)
        self.assertEqual((red.code, red.lines), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'src/b.py'"]), red.err)


class ScrubbedEnvironmentTests(Fixture):
    """S56-09, S56-11: variables that would change the history, the common directory or the settings git reads."""

    SCRUBBED = (
        "GIT_COMMON_DIR",
        "GIT_PREFIX",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_GRAFT_FILE",
        "GIT_SHALLOW_FILE",
        "GIT_REPLACE_REF_BASE",
        "GIT_CONFIG",
        "GIT_CONFIG_GLOBAL",
        "GIT_CONFIG_SYSTEM",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_KEY_0",
        "GIT_CONFIG_VALUE_0",
        "GIT_CONFIG_PARAMETERS",
    )

    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_the_variables_are_removed_from_every_git_child(self) -> None:
        with mock.patch.dict(os.environ, {name: "x" for name in self.SCRUBBED}):
            environment = repair_guard._git_environment()
        for name in self.SCRUBBED:
            with self.subTest(name=name):
                self.assertNotIn(name, environment)

    def test_a_variable_that_is_not_one_of_them_is_kept(self) -> None:
        with mock.patch.dict(os.environ, {"GIT_AUTHOR_NAME": "kept", "GIT_CONFIGURED": "kept too"}):
            environment = repair_guard._git_environment()
        self.assertEqual(environment.get("GIT_AUTHOR_NAME"), "kept")
        self.assertEqual(environment.get("GIT_CONFIGURED"), "kept too")

    def test_git_common_dir_in_the_environment_changes_nothing(self) -> None:
        sha = self.committed()
        other = self.root / "other"
        other.mkdir()
        git(other, "init", "-q", "-b", "main")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha, env={"GIT_COMMON_DIR": str(other / ".git")})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_a_broken_global_configuration_named_by_the_environment_changes_nothing(self) -> None:
        sha = self.committed()
        broken = self.root / "broken-config"
        broken.write_text("[core\n", encoding="utf-8")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha, env={"GIT_CONFIG_GLOBAL": str(broken), "GIT_CONFIG_SYSTEM": str(broken)})
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)

    def test_a_configuration_given_through_the_environment_changes_nothing(self) -> None:
        sha = self.committed()
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(
            sha, env={"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "no-dot-in-this-key", "GIT_CONFIG_VALUE_0": "x"}
        )
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)


class StreamPrecedenceTests(Fixture):
    """S56-12: red before fault decides the exit unless the reds could not be delivered."""

    ready = UnwritableStreamTests.ready
    run_with_dead_stream = UnwritableStreamTests.run_with_dead_stream

    def ready_with_red_and_fault(self) -> list[str]:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.dispatch.write_text(f'repair_allowlist: ["a{SURROGATE_ESCAPE}"]\nprotected_paths: []\n', encoding="utf-8")
        return ["--repo", str(self.repo), "--repair", "no-such-ref", "--dispatch", str(self.dispatch)]

    def test_a_red_with_a_fault_and_a_dead_stderr_is_exit_one_with_the_red_on_stdout(self) -> None:
        done = self.run_with_dead_stream(self.ready_with_red_and_fault(), "stderr")
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stdout.decode("utf-8", "replace").startswith(repair_guard.TEXT_VALUE_INVALID))

    def test_a_red_with_a_fault_and_a_dead_stdout_is_exit_two(self) -> None:
        done = self.run_with_dead_stream(self.ready_with_red_and_fault(), "stdout")
        self.assertEqual(done.returncode, 2)

    def test_a_red_without_a_fault_and_a_dead_stderr_is_exit_one(self) -> None:
        done = self.run_with_dead_stream(self.ready(red=True), "stderr")
        self.assertEqual(done.returncode, 1)
        self.assertIn(repair_guard.OUTSIDE_ALLOWLIST, done.stdout.decode("utf-8", "replace"))

    def test_a_fault_with_no_red_and_a_dead_stderr_is_still_exit_two(self) -> None:
        args = self.ready(red=False)
        args[3] = "no-such-ref"
        self.assertEqual(self.run_with_dead_stream(args, "stderr").returncode, 2)

    def test_in_process_a_stderr_that_raises_does_not_change_a_red_exit(self) -> None:
        args = self.ready_with_red_and_fault()

        class Dead(io.StringIO):
            def write(self, text: str) -> int:
                raise OSError(32, "broken pipe")

        out = io.StringIO()
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", Dead()):
            code = repair_guard.main(args)
        self.assertEqual(code, 1)
        self.assertTrue(out.getvalue().startswith(repair_guard.TEXT_VALUE_INVALID))

    def test_in_process_a_stdout_that_raises_is_exit_two_even_with_a_red(self) -> None:
        args = self.ready_with_red_and_fault()

        class Dead(io.StringIO):
            def write(self, text: str) -> int:
                raise OSError(32, "broken pipe")

        with mock.patch.object(sys, "stdout", Dead()), mock.patch.object(sys, "stderr", io.StringIO()):
            self.assertEqual(repair_guard.main(args), 2)


class TextDefectiveDispatchTests(Fixture):
    """S56-13: a dispatch with a text defect still has its gate scripts protected."""

    def gate_change(self) -> str:
        self.base(GATE_FILE, "tools/a.py")
        self.write(GATE_FILE, "changed\n")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_gate_script_change_is_reported_next_to_the_text_red(self) -> None:
        sha = self.gate_change()
        # Under revision04 only the defective block loses its entries, so the clean block
        # is used as well: the expected codes are those of the clean block plus the gate rule.
        expected = {
            "repair_allowlist": [repair_guard.TEXT_VALUE_INVALID, repair_guard.PROTECTED_PATH_TOUCHED, repair_guard.PROTECTED_PATH_TOUCHED],
            "protected_paths": [repair_guard.TEXT_VALUE_INVALID, repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED],
        }
        for block in ("repair_allowlist", "protected_paths"):
            with self.subTest(block=block):
                other = "protected_paths" if block == "repair_allowlist" else "repair_allowlist"
                self.dispatch.write_text(
                    f'{block}: ["tools/{SURROGATE_ESCAPE}"]\n{other}: ["tools/"]\n', encoding="utf-8"
                )
                result = self.run_guard(sha)
                self.assertEqual(result.code, 1)
                self.assertEqual(self.defect_codes(result), expected[block])
                self.assertTrue(any(repr(GATE_FILE) in line and line.startswith(repair_guard.PROTECTED_PATH_TOUCHED) for line in result.lines))
                self.assertEqual(result.err, "")

    def test_a_raw_bad_byte_on_a_block_line_does_not_stop_the_gate_script_rule(self) -> None:
        sha = self.gate_change()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/\xff"]\nprotected_paths: []\n')
        result = self.run_guard(sha)
        self.assertEqual(
            (result.code, self.defect_codes(result)),
            (1, [repair_guard.TEXT_VALUE_INVALID, repair_guard.PROTECTED_PATH_TOUCHED]),
        )

    def test_the_defective_allowlist_is_not_used_and_a_path_outside_it_is_not_reported(self) -> None:
        self.base("tools/a.py")
        self.write("lib/other.py")
        sha = self.commit()
        self.dispatch.write_text(f'repair_allowlist: ["tools/{SURROGATE_ESCAPE}"]\nprotected_paths: ["src/"]\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))

    def test_the_single_parent_rule_and_the_gate_rule_apply_to_a_root_commit_with_a_text_red(self) -> None:
        self.write(GATE_FILE)
        sha = self.commit("root")
        self.dispatch.write_text(f'repair_allowlist: ["a{SURROGATE_ESCAPE}"]\nprotected_paths: []\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual(
            self.defect_codes(result),
            [repair_guard.TEXT_VALUE_INVALID, repair_guard.REPAIR_NOT_SINGLE_PARENT, repair_guard.PROTECTED_PATH_TOUCHED],
        )

    def test_check_paths_without_rules_protects_only_the_gate_directory(self) -> None:
        protected = [repair_guard.make_rule("src/", "t")]
        defects = repair_guard.check_paths([GATE_FILE, "src/x.py", "tools/y.py"], [], protected, False, False, False)
        self.assertEqual([(d.code, d.subject) for d in defects], [(repair_guard.PROTECTED_PATH_TOUCHED, repr(GATE_FILE))])


class LineEndingAndLetterTests(Fixture):
    """S56-11: a block line ending in two carriage returns, and every ASCII table letter."""

    def test_a_block_line_that_ends_in_two_carriage_returns_is_a_text_red(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/"]\r\r\nprotected_paths: []\r\n')
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/"]\r\nprotected_paths: []\r\r\r\n')
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID]))

    def test_one_carriage_return_before_the_line_feed_is_still_a_line_ending(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        sha = self.commit()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/"]\r\nprotected_paths: []\r\n')
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_every_ascii_letter_of_an_allowlist_entry_ignores_case(self) -> None:
        for code in range(ord("A"), ord("Z") + 1):
            upper, lower = chr(code), chr(code + 32)
            with self.subTest(letter=upper):
                self.assertTrue(repair_guard.make_rule(f"{upper}x/", "t").covers(f"{lower}x/y", True))
                self.assertTrue(repair_guard.make_rule(f"{lower}x/", "t").covers(f"{upper}X/y", True))
                self.assertTrue(repair_guard.make_rule(f"a{upper}", "t").covers(f"A{lower}", True))
                self.assertFalse(repair_guard.make_rule(f"{upper}x/", "t").covers(f"{lower}x/y", False))

    def test_an_upper_case_z_in_an_allowlist_entry_covers_its_lower_case_path_on_windows_rules(self) -> None:
        self.assertTrue(repair_guard.make_rule("ZONE/", "t").covers("zone/a.py", True))
        self.assertTrue(repair_guard.make_rule("zone/", "t").covers("ZONE/A.PY", True))
        self.assertTrue(repair_guard.make_rule("Zz.py", "t").covers("zZ.PY", True))

    def test_the_characters_next_to_the_letters_are_not_folded(self) -> None:
        for upper, other in (("@", "`"), ("[", "{")):
            with self.subTest(character=upper):
                self.assertFalse(repair_guard.make_rule(f"{upper}x/", "t").covers(f"{other}x/y", True))
                self.assertFalse(repair_guard.make_rule(f"{other}x/", "t").covers(f"{upper}x/y", True))

    def test_the_table_maps_exactly_the_twenty_six_capitals(self) -> None:
        self.assertEqual(repair_guard.ascii_lower("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(repair_guard.ascii_lower("abcdefghijklmnopqrstuvwxyz@[`{"), "abcdefghijklmnopqrstuvwxyz@[`{")
        self.assertEqual(len(repair_guard.ASCII_LOWER), 26)


class InProcessTests(Fixture):
    def test_main_returns_the_exit_code_and_prints_the_summary(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.set_dispatch(["tools/"], [])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual((code, out.getvalue()), (0, "paths=1 defects=0\n"))

    def test_the_script_runs_as_a_program_from_any_directory(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        self.set_dispatch(["tools/"], [])
        done = subprocess.run(
            [PY, str(SCRIPT), "--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)],
            capture_output=True, cwd=str(self.root), check=False,
        )
        self.assertEqual(done.returncode, 0)

    def test_the_repo_is_selected_by_the_argument_not_by_the_environment(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.commit()
        other = self.root / "other"
        other.mkdir()
        git(other, "init", "-q")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard("HEAD", env={"GIT_DIR": str(other / ".git")})
        self.assertEqual(result.code, 0)


class ObjectFixture(Fixture):
    """Helpers that forge objects in a repository's store, to prove the guard hashes what it reads."""

    def committed_gate_change(self) -> tuple[str, str]:
        """(first parent, repair): the repair changes a gate script and a tools file."""
        self.base(GATE_FILE, "tools/a.py", "src/app.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        self.write(GATE_FILE, "changed\n")
        self.write("tools/a.py", "fixed\n")
        return parent, self.commit("repair")

    def object_path(self, oid: str, repo: Path | None = None) -> Path:
        return (repo or self.repo) / ".git" / "objects" / oid[:2] / oid[2:]

    def raw_body(self, oid: str, kind: str, repo: Path | None = None) -> bytes:
        done = subprocess.run(
            ["git", "-C", str(repo or self.repo), "cat-file", kind, oid], capture_output=True, check=False
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def write_loose(self, path: Path, kind: str, body: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            os.chmod(path, 0o666)
        path.write_bytes(zlib.compress(f"{kind} {len(body)}".encode("ascii") + b"\0" + body))

    def use_alternate(self, alternate: Path) -> None:
        """Make the repository read objects from the store `alternate` as well (LF line, no CR)."""
        info = self.repo / ".git" / "objects" / "info"
        info.mkdir(parents=True, exist_ok=True)
        (info / "alternates").write_bytes((str(alternate).replace("\\", "/") + "\n").encode("utf-8"))

    def forged_commit_body(self, tree: str) -> bytes:
        return f"tree {tree}\nauthor t <t@example.test> 1 +0000\ncommitter t <t@example.test> 1 +0000\n\nforged\n".encode("ascii")

    def plain_diff(self, left: str, right: str, repo: Path | None = None) -> str:
        return git(repo or self.repo, "diff", "--name-only", left, right)

    def expect_forged_is_a_fault(self, sha: str, forged: str, repo: Path | None = None) -> None:
        self.set_dispatch([GATE_DIR + "/", "tools/"], [])
        result = self.run_guard(sha, repo=repo)
        self.assertEqual((result.code, result.out), (2, ""), result.err)
        self.assertIn(forged, result.err)
        self.assertIn("hash", result.err)
        self.assertNotIn("Traceback", result.err)
        self.assertEqual(result.err.count("\n"), 1, result.err)

    def baseline(self, sha: str, repo: Path | None = None) -> Result:
        self.set_dispatch([GATE_DIR + "/", "tools/"], [])
        result = self.run_guard(sha, repo=repo)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.PROTECTED_PATH_TOUCHED]), result.err)
        return result


class ForgedObjectTests(ObjectFixture):
    """S56-15 and S56-16: the guard trusts no object it has not hashed itself."""

    def test_a_forged_loose_first_parent_is_a_fault_and_never_a_pass(self) -> None:
        parent, sha = self.committed_gate_change()
        self.baseline(sha)
        tree = git(self.repo, "rev-parse", f"{sha}^{{tree}}")
        self.write_loose(self.object_path(parent), "commit", self.forged_commit_body(tree))
        self.assertEqual(git(self.repo, "cat-file", "-p", parent).splitlines()[0], f"tree {tree}")  # the forgery is in force
        self.assertEqual(self.plain_diff(parent, sha), "")  # plain git now sees no change at all
        self.expect_forged_is_a_fault(sha, parent)

    def test_a_forged_first_parent_served_through_alternates_is_a_fault_and_never_a_pass(self) -> None:
        parent, sha = self.committed_gate_change()
        tree = git(self.repo, "rev-parse", f"{sha}^{{tree}}")
        alternate = self.root / "alternate-store"
        self.write_loose(alternate / parent[:2] / parent[2:], "commit", self.forged_commit_body(tree))
        os.chmod(self.object_path(parent), 0o666)
        self.object_path(parent).unlink()
        self.use_alternate(alternate)
        self.assertEqual(git(self.repo, "cat-file", "-p", parent).splitlines()[0], f"tree {tree}")
        self.assertEqual(self.plain_diff(parent, sha), "")
        self.expect_forged_is_a_fault(sha, parent)

    def test_a_genuine_first_parent_served_through_alternates_is_accepted(self) -> None:
        parent, sha = self.committed_gate_change()
        alternate = self.root / "alternate-store"
        target = alternate / parent[:2] / parent[2:]
        target.parent.mkdir(parents=True)
        target.write_bytes(self.object_path(parent).read_bytes())
        os.chmod(self.object_path(parent), 0o666)
        self.object_path(parent).unlink()
        self.use_alternate(alternate)
        self.baseline(sha)

    def test_a_forged_repair_commit_is_a_fault(self) -> None:
        parent, sha = self.committed_gate_change()
        parent_tree = git(self.repo, "rev-parse", f"{parent}^{{tree}}")
        original = self.raw_body(sha, "commit")
        forged = original.replace(git(self.repo, "rev-parse", f"{sha}^{{tree}}").encode("ascii"), parent_tree.encode("ascii"))
        self.assertNotEqual(forged, original)
        self.write_loose(self.object_path(sha), "commit", forged)
        self.expect_forged_is_a_fault(sha, sha)

    def test_a_forged_tree_of_the_repair_at_every_depth_is_a_fault_and_never_a_pass(self) -> None:
        parent, sha = self.committed_gate_change()
        depths = ["", "skills", "skills/johnny-project-takeover", GATE_DIR]
        for depth in depths:
            with self.subTest(depth=depth or "root"):
                repair_spec = f"{sha}:{depth}" if depth else f"{sha}^{{tree}}"
                base_spec = f"{parent}:{depth}" if depth else f"{parent}^{{tree}}"
                repair_tree = git(self.repo, "rev-parse", repair_spec)
                base_tree = git(self.repo, "rev-parse", base_spec)
                self.assertNotEqual(repair_tree, base_tree)
                path = self.object_path(repair_tree)
                original = path.read_bytes()
                try:
                    self.write_loose(path, "tree", self.raw_body(base_tree, "tree"))
                    self.expect_forged_is_a_fault(sha, repair_tree)
                finally:
                    os.chmod(path, 0o666)
                    path.write_bytes(original)
        self.baseline(sha)

    def test_a_forged_tree_of_the_first_parent_at_every_depth_is_a_fault_and_never_a_pass(self) -> None:
        """S56-21: the first parent's trees are hashed too; each forgery copies the repair's content."""
        parent, sha = self.committed_gate_change()
        for depth in ["", "skills", "skills/johnny-project-takeover", GATE_DIR]:
            with self.subTest(depth=depth or "root"):
                repair_spec = f"{sha}:{depth}" if depth else f"{sha}^{{tree}}"
                base_spec = f"{parent}:{depth}" if depth else f"{parent}^{{tree}}"
                repair_tree = git(self.repo, "rev-parse", repair_spec)
                base_tree = git(self.repo, "rev-parse", base_spec)
                self.assertNotEqual(repair_tree, base_tree)
                path = self.object_path(base_tree)
                original = path.read_bytes()
                try:
                    self.write_loose(path, "tree", self.raw_body(repair_tree, "tree"))
                    # the forgery is in force: the store serves the repair's content under the parent's id
                    self.assertEqual(self.raw_body(base_tree, "tree"), self.raw_body(repair_tree, "tree"))
                    self.expect_forged_is_a_fault(sha, base_tree)
                finally:
                    os.chmod(path, 0o666)
                    path.write_bytes(original)
        self.baseline(sha)

    def test_a_forged_first_parent_root_tree_that_copies_the_repair_is_never_exit_zero(self) -> None:
        parent, sha = self.committed_gate_change()
        base_tree = git(self.repo, "rev-parse", f"{parent}^{{tree}}")
        repair_tree = git(self.repo, "rev-parse", f"{sha}^{{tree}}")
        self.write_loose(self.object_path(base_tree), "tree", self.raw_body(repair_tree, "tree"))
        self.set_dispatch([GATE_DIR + "/", "tools/"], [GATE_DIR + "/"])
        result = self.run_guard(sha)
        self.assertNotEqual(result.code, 0, result.out)
        self.assertEqual((result.code, result.out), (2, ""), result.err)
        self.assertIn(base_tree, result.err)

    def test_the_forged_repair_subtree_hides_the_change_from_plain_git(self) -> None:
        parent, sha = self.committed_gate_change()
        scripts = git(self.repo, "rev-parse", f"{sha}:{GATE_DIR}")
        base_scripts = git(self.repo, "rev-parse", f"{parent}:{GATE_DIR}")
        self.write_loose(self.object_path(scripts), "tree", self.raw_body(base_scripts, "tree"))
        self.assertEqual(git(self.repo, "diff", "--name-only", f"{parent}^{{tree}}", f"{sha}^{{tree}}"), "tools/a.py")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 2, result.out)
        self.assertEqual(result.out, "")

    def test_a_subtree_whose_two_ids_are_equal_is_never_read(self) -> None:
        parent, sha = self.committed_gate_change()
        shared = git(self.repo, "rev-parse", f"{sha}:src")
        self.assertEqual(shared, git(self.repo, "rev-parse", f"{parent}:src"))
        self.write_loose(self.object_path(shared), "tree", b"garbage that is no tree")
        self.baseline(sha)
        os.chmod(self.object_path(shared), 0o666)
        self.object_path(shared).unlink()
        self.baseline(sha)

    def test_a_tree_the_store_cannot_serve_is_a_fault_naming_it(self) -> None:
        parent, sha = self.committed_gate_change()
        scripts = git(self.repo, "rev-parse", f"{sha}:{GATE_DIR}")
        os.chmod(self.object_path(scripts), 0o666)
        self.object_path(scripts).unlink()
        self.set_dispatch([GATE_DIR + "/", "tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (2, ""))
        self.assertIn(scripts, result.err)
        self.assertIn("cannot be read from the object store", result.err)
        # S56-22: a red found at a level that did verify stands beside the fault
        self.set_dispatch([GATE_DIR + "/"], [])
        beside = self.run_guard(sha)
        self.assertEqual((beside.code, beside.lines), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'tools/a.py'"]))
        self.assertIn(scripts, beside.err)

    def test_a_forged_tree_is_a_fault_after_a_red_that_was_already_found(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "checkout", "-q", "-b", "side")
        self.write("tools/b.py", "side\n")
        self.commit("side")
        git(self.repo, "checkout", "-q", "main")
        self.write("tools/c.py", "main\n")
        self.commit("main")
        git(self.repo, "merge", "-q", "--no-ff", "-m", "merge", "side")
        merge = git(self.repo, "rev-parse", "HEAD")
        tools = git(self.repo, "rev-parse", f"{merge}:tools")
        self.write_loose(self.object_path(tools), "tree", b"")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(merge)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.REPAIR_NOT_SINGLE_PARENT]))
        self.assertIn(tools, result.err)

    def test_a_forged_object_in_a_sha256_repository_is_a_fault_and_a_genuine_one_is_verified_with_sha256(self) -> None:
        repo = self.root / "repo256"
        repo.mkdir()
        probe = subprocess.run(
            ["git", "-C", str(repo), "init", "-q", "--object-format=sha256", "-b", "main"], capture_output=True, check=False
        )
        if probe.returncode != 0:
            self.skipTest("this git cannot create a SHA-256 repository: " + probe.stderr.decode("utf-8", "replace").strip())
        for rel, text in ((GATE_FILE, "base\n"), ("tools/a.py", "base\n")):
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        parent = git(repo, "rev-parse", "HEAD")
        (repo / GATE_FILE).write_text("changed\n", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "repair")
        sha = git(repo, "rev-parse", "HEAD")
        self.assertEqual(len(sha), 64)
        self.baseline(sha, repo)
        tree = git(repo, "rev-parse", f"{sha}^{{tree}}")
        self.write_loose(self.object_path(parent, repo), "commit", self.forged_commit_body(tree))
        self.assertEqual(self.plain_diff(parent, sha, repo), "")
        self.expect_forged_is_a_fault(sha, parent, repo)

    def test_the_guard_never_asks_git_for_a_diff_or_for_history(self) -> None:
        parent, sha = self.committed_gate_change()
        self.set_dispatch([GATE_DIR + "/"], [])
        calls: list[list[str]] = []
        real = repair_guard.run_git

        def recording(repo: str, args: Sequence[str], stdin: bytes = b"", options: Sequence[str] = ()) -> bytes:
            calls.append(list(args))
            return real(repo, args, stdin, options)

        out = io.StringIO()
        with mock.patch.object(repair_guard, "run_git", side_effect=recording), contextlib.redirect_stdout(out):
            code = repair_guard.main(["--repo", str(self.repo), "--repair", sha, "--dispatch", str(self.dispatch)])
        self.assertEqual(code, 1)
        self.assertTrue(calls)
        self.assertTrue({call[0] for call in calls} <= {"rev-parse", "cat-file"}, calls)
        for call in calls:
            if call[0] == "cat-file":
                self.assertEqual(call, ["cat-file", "--batch"])


class CommitGraphTests(ObjectFixture):
    """S56-17: a commit-graph that gives the repair the base tree changes nothing the guard reads."""

    def forge_graph(self, commit: str, tree: str) -> None:
        git(self.repo, "commit-graph", "write", "--reachable")
        path = self.repo / ".git" / "objects" / "info" / "commit-graph"
        os.chmod(path, 0o666)
        data = bytearray(path.read_bytes())
        chunk_count = data[6]
        table = [
            (bytes(data[8 + 12 * index:12 + 12 * index]), int.from_bytes(data[12 + 12 * index:20 + 12 * index], "big"))
            for index in range(chunk_count + 1)
        ]
        offsets = {name: (start, table[index + 1][1]) for index, (name, start) in enumerate(table[:-1])}
        oid_start, oid_end = offsets[b"OIDL"]
        ids = [bytes(data[oid_start + 20 * i:oid_start + 20 * i + 20]).hex() for i in range((oid_end - oid_start) // 20)]
        position = ids.index(commit)
        data_start = offsets[b"CDAT"][0] + 36 * position
        data[data_start:data_start + 20] = bytes.fromhex(tree)
        data[-20:] = hashlib.sha1(bytes(data[:-20])).digest()
        path.write_bytes(bytes(data))

    def test_a_commit_graph_giving_the_repair_the_base_tree_does_not_hide_the_change(self) -> None:
        parent, sha = self.committed_gate_change()
        base_tree = git(self.repo, "rev-parse", f"{parent}^{{tree}}")
        self.assertNotEqual(git(self.repo, "rev-parse", f"{sha}^{{tree}}"), base_tree)
        self.forge_graph(sha, base_tree)
        self.assertEqual(self.plain_diff(parent, sha), "")  # the graph is in force: plain git sees no change
        self.baseline(sha)
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1)
        self.assertIn(repr(GATE_FILE), "\n".join(result.lines))


class TreeWalkTests(Fixture):
    """S56-16: the guard's own walk of the two trees reports every path whose entry differs."""

    def gate_dispatch(self, allow: object) -> None:
        self.set_dispatch(allow, [])

    def test_a_mode_only_change_is_a_changed_path(self) -> None:
        self.base("tools/a.py", "tools/b.py")
        git(self.repo, "update-index", "--chmod=+x", "tools/a.py")
        git(self.repo, "commit", "-q", "-m", "mode")
        self.set_dispatch(["tools/b.py"], [])
        result = self.run_guard()
        self.assertEqual((result.code, result.lines), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'tools/a.py'"]))
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard().out, "paths=1 defects=0\n")

    def test_a_type_change_to_a_symbolic_link_is_a_changed_path(self) -> None:
        self.base("tools/a.py", "src/b.py")
        blob = git(self.repo, "rev-parse", "HEAD:tools/a.py")
        git(self.repo, "update-index", "--cacheinfo", f"120000,{blob},src/b.py")
        git(self.repo, "commit", "-q", "-m", "link")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard()
        self.assertEqual((result.code, result.lines), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'src/b.py'"]))

    def test_a_removed_directory_lists_every_file_under_it_and_not_the_directory(self) -> None:
        self.base("src/x/a.py", "src/x/y/b.py", "src/keep.py", "tools/a.py")
        git(self.repo, "rm", "-q", "-r", "src/x")
        git(self.repo, "commit", "-q", "-m", "gone")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard()
        self.assertEqual(
            result.lines,
            [f"{repair_guard.OUTSIDE_ALLOWLIST} 'src/x/a.py'", f"{repair_guard.OUTSIDE_ALLOWLIST} 'src/x/y/b.py'"],
        )

    def test_an_added_directory_lists_every_file_under_it_and_not_the_directory(self) -> None:
        self.base("tools/a.py")
        self.write("lib/p/q.py")
        self.write("lib/r.py")
        self.commit("added")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard()
        self.assertEqual(
            result.lines,
            [f"{repair_guard.OUTSIDE_ALLOWLIST} 'lib/p/q.py'", f"{repair_guard.OUTSIDE_ALLOWLIST} 'lib/r.py'"],
        )

    def test_a_file_that_becomes_a_directory_reports_the_path_and_what_lies_under_it(self) -> None:
        self.base("tools/a", "tools/keep.py")
        git(self.repo, "rm", "-q", "tools/a")
        self.write("tools/a/b.py")
        self.commit("turn")
        self.set_dispatch(["tools/a/"], [])
        result = self.run_guard()
        self.assertEqual(result.lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'tools/a'"])
        self.assertEqual(self.run_guard().code, 1)
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard().out, "paths=2 defects=0\n")

    def test_a_directory_that_becomes_a_file_reports_the_path_and_what_lay_under_it(self) -> None:
        self.base("tools/a/b.py", "tools/keep.py")
        git(self.repo, "rm", "-q", "-r", "tools/a")
        self.write("tools/a", "now a file\n")
        self.commit("turn")
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard().out, "paths=2 defects=0\n")
        self.set_dispatch(["tools/a"], [])
        self.assertEqual(self.run_guard().lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'tools/a/b.py'"])

    def test_a_submodule_pointer_is_compared_by_id_and_never_descended(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "pointer")
        git(self.repo, "update-index", "--cacheinfo", f"160000,{'2' * 40},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "bump")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard()
        self.assertEqual((result.code, result.lines, result.err), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'vendor/lib'"], ""))

    def test_a_pointer_that_turns_into_a_file_and_back_is_a_changed_path(self) -> None:
        self.base("tools/a.py")
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "pointer")
        blob = git(self.repo, "rev-parse", "HEAD:tools/a.py")
        git(self.repo, "update-index", "--cacheinfo", f"100644,{blob},vendor/lib")
        git(self.repo, "commit", "-q", "-m", "file")
        self.set_dispatch(["tools/"], [])
        self.assertEqual(self.run_guard().lines, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'vendor/lib'"])

    def test_an_empty_subtree_that_exists_on_one_side_only_is_a_changed_path(self) -> None:
        self.base("tools/a.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        empty = git_raw(self.repo, ["hash-object", "-t", "tree", "--stdin"], b"")
        body = subprocess.run(
            ["git", "-C", str(self.repo), "cat-file", "tree", "HEAD^{tree}"], capture_output=True, check=True
        ).stdout
        tree = git_raw(
            self.repo, ["hash-object", "-w", "-t", "tree", "--stdin"], body + b"40000 zempty\0" + bytes.fromhex(empty)
        )
        sha = git(self.repo, "commit-tree", tree, "-p", parent, "-m", "empty directory")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines, result.err), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'zempty'"], ""))

    def test_a_directory_mode_spelled_differently_with_the_same_id_is_a_changed_path(self) -> None:
        self.base("tools/a.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        inner = git(self.repo, "rev-parse", "HEAD:tools")
        raw = git_raw(
            self.repo, ["hash-object", "--literally", "-w", "-t", "tree", "--stdin"], b"040000 tools\0" + bytes.fromhex(inner)
        )
        sha = git(self.repo, "commit-tree", raw, "-p", parent, "-m", "spelling")
        self.set_dispatch(["tools/x"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines, result.err), (1, [f"{repair_guard.OUTSIDE_ALLOWLIST} 'tools'"], ""))

    def test_an_unchanged_commit_has_no_changed_path_and_reads_no_tree(self) -> None:
        self.base("tools/a.py")
        sha = self.commit("empty")
        self.set_dispatch([], [])
        reads: list[str] = []
        real = repair_guard.read_objects

        def recording(repo: str, ids: Sequence[str], kind: str) -> dict[str, bytes]:
            reads.append(kind)
            return real(repo, ids, kind)

        out = io.StringIO()
        with mock.patch.object(repair_guard, "read_objects", side_effect=recording), contextlib.redirect_stdout(out):
            code = repair_guard.main(["--repo", str(self.repo), "--repair", sha, "--dispatch", str(self.dispatch)])
        self.assertEqual((code, out.getvalue()), (0, "paths=0 defects=0\n"))
        self.assertEqual(reads, ["commit", "commit"])

    def test_changed_paths_are_listed_in_byte_order_of_their_names(self) -> None:
        self.base("b/z.py", "a.py", "c.py", "b.py")
        for rel in ("b/z.py", "a.py", "c.py", "b.py"):
            self.write(rel, "changed\n")
        self.commit("all")
        self.set_dispatch([], [])
        result = self.run_guard()
        self.assertEqual([line.split(" ", 1)[1] for line in result.lines], ["'a.py'", "'b.py'", "'b/z.py'", "'c.py'"])


class ObjectReadingTests(Fixture):
    """S56-15: what read_objects accepts, one answer at a time."""

    def real_objects(self) -> tuple[str, str, bytes, bytes]:
        self.base("tools/a.py")
        commit = git(self.repo, "rev-parse", "HEAD")
        tree = git(self.repo, "rev-parse", "HEAD^{tree}")
        commit_body = subprocess.run(["git", "-C", str(self.repo), "cat-file", "commit", commit], capture_output=True, check=True).stdout
        tree_body = subprocess.run(["git", "-C", str(self.repo), "cat-file", "tree", tree], capture_output=True, check=True).stdout
        return commit, tree, commit_body, tree_body

    def serve(self, data: bytes, oid: str, kind: str) -> dict[str, bytes]:
        with mock.patch.object(repair_guard, "run_git", return_value=data):
            return repair_guard.read_objects("anywhere", [oid], kind)

    def test_a_genuine_answer_is_returned(self) -> None:
        commit, tree, commit_body, tree_body = self.real_objects()
        good = f"{commit} commit {len(commit_body)}\n".encode() + commit_body + b"\n"
        self.assertEqual(self.serve(good, commit, "commit"), {commit: commit_body})
        real = repair_guard.read_objects(str(self.repo), [commit], "commit")
        self.assertEqual(real, {commit: commit_body})
        self.assertEqual(repair_guard.read_objects(str(self.repo), [tree, tree], "tree"), {tree: tree_body})
        self.assertEqual(repair_guard.read_objects(str(self.repo), [], "tree"), {})

    def test_the_hash_of_an_object_is_what_git_gives_it(self) -> None:
        data = b"some content\n"
        expected = git_raw(self.repo, ["hash-object", "--stdin"], data)
        self.assertEqual(repair_guard.object_hash("blob", data, 40), expected)
        empty = git_raw(self.repo, ["hash-object", "-t", "tree", "--stdin"], b"")
        self.assertEqual(repair_guard.object_hash("tree", b"", 40), empty)
        self.assertNotEqual(repair_guard.object_hash("blob", data, 64), expected)
        self.assertEqual(len(repair_guard.object_hash("blob", data, 64)), 64)
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.object_hash("blob", data, 41)

    def test_the_hash_of_an_object_in_a_sha256_repository_is_what_git_gives_it(self) -> None:
        repo = self.root / "repo256"
        repo.mkdir()
        probe = subprocess.run(["git", "-C", str(repo), "init", "-q", "--object-format=sha256"], capture_output=True, check=False)
        if probe.returncode != 0:
            self.skipTest("this git cannot create a SHA-256 repository: " + probe.stderr.decode("utf-8", "replace").strip())
        data = b"some content\n"
        self.assertEqual(repair_guard.object_hash("blob", data, 64), git_raw(repo, ["hash-object", "--stdin"], data))

    def test_every_way_an_answer_can_be_wrong_is_a_fault_naming_the_id(self) -> None:
        commit, tree, commit_body, tree_body = self.real_objects()
        good = f"{commit} commit {len(commit_body)}\n".encode() + commit_body + b"\n"
        other = "f" * 40
        said: dict[str, str] = {
            "the wrong type": "not a commit",
            "a size too large": "bytes",
            "a size too small": "hash",
            "a changed body": "hash",
            "no final newline": "bytes",
            "a different id answered": "header",
            "a missing object": "object store",
        }
        cases: dict[str, tuple[bytes, str, str]] = {
            "a different id answered": (good.replace(commit.encode(), other.encode(), 1), commit, "commit"),
            "the wrong type": (f"{tree} tree {len(tree_body)}\n".encode() + tree_body + b"\n", tree, "commit"),
            "a size too large": (f"{commit} commit {len(commit_body) + 1}\n".encode() + commit_body + b"\n", commit, "commit"),
            "a size too small": (f"{commit} commit {len(commit_body) - 1}\n".encode() + commit_body + b"\n", commit, "commit"),
            "a changed body": (f"{commit} commit {len(commit_body)}\n".encode() + commit_body.replace(b"base", b"BASE") + b"\n", commit, "commit"),
            "no final newline": (good[:-1], commit, "commit"),
            "trailing data": (good + b"extra", commit, "commit"),
            "a header that is not three words": (f"{commit} commit\n".encode() + commit_body + b"\n", commit, "commit"),
            "a size that is not a number": (f"{commit} commit x\n".encode() + commit_body + b"\n", commit, "commit"),
            "nothing": (b"", commit, "commit"),
            "a missing object": (f"{commit} missing\n".encode(), commit, "commit"),
        }
        for name, (data, oid, kind) in cases.items():
            with self.subTest(name):
                with self.assertRaises(repair_guard.ToolFault) as caught:
                    self.serve(data, oid, kind)
                self.assertEqual(str(caught.exception).splitlines(), [str(caught.exception)])
                if name not in ("nothing", "trailing data"):
                    self.assertIn(oid, str(caught.exception))
                if name in said:
                    self.assertIn(said[name], str(caught.exception))

    def test_an_id_that_is_not_an_object_id_is_refused_before_git_is_asked(self) -> None:
        with mock.patch.object(repair_guard, "run_git", side_effect=AssertionError("git must not be asked")):
            for bad in ("HEAD", "abc", "g" * 40, "A" * 40, "1" * 41):
                with self.subTest(bad=bad):
                    with self.assertRaises(repair_guard.ToolFault):
                        repair_guard.read_objects("anywhere", [bad], "commit")

    def test_the_ids_go_to_git_on_standard_input_and_not_on_the_command_line(self) -> None:
        commit, _tree, commit_body, _tree_body = self.real_objects()
        seen: list[tuple[list[str], bytes]] = []

        def fake(repo: str, args: Sequence[str], stdin: bytes = b"", options: Sequence[str] = ()) -> bytes:
            seen.append((list(args), stdin))
            return f"{commit} commit {len(commit_body)}\n".encode() + commit_body + b"\n"

        with mock.patch.object(repair_guard, "run_git", side_effect=fake):
            repair_guard.read_objects("anywhere", [commit, commit], "commit")
        self.assertEqual(seen, [(["cat-file", "--batch"], (commit + "\n").encode("ascii"))])


class DefectiveBlockTests(Fixture):
    """S56-18: only the block that holds a text defect loses its entries."""

    def changed_outside_both(self) -> str:
        self.base("tools/a.py", "src/b.py")
        self.write("src/b.py", "changed\n")
        return self.commit()

    def test_a_defective_allowlist_leaves_the_protected_entries_in_force(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_text(f'repair_allowlist: ["tools/{SURROGATE_ESCAPE}"]\nprotected_paths: ["src/"]\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual(
            (result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID, repair_guard.PROTECTED_PATH_TOUCHED])
        )
        self.assertIn("'src/b.py'", result.lines[1])

    def test_a_defective_protected_list_leaves_the_allowlist_in_force(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_text(f'repair_allowlist: ["tools/"]\nprotected_paths: ["src/{SURROGATE_ESCAPE}"]\n', encoding="utf-8")
        result = self.run_guard(sha)
        self.assertEqual(
            (result.code, self.defect_codes(result)), (1, [repair_guard.TEXT_VALUE_INVALID, repair_guard.OUTSIDE_ALLOWLIST])
        )
        self.assertIn("'src/b.py'", result.lines[1])

    def test_a_defective_allowlist_alone_judges_no_path_as_outside(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_text(f'repair_allowlist: ["tools/{SURROGATE_ESCAPE}"]\nprotected_paths: []\n', encoding="utf-8")
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.TEXT_VALUE_INVALID])

    def test_a_defective_protected_list_alone_protects_only_the_gate_scripts(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_text(f'repair_allowlist: ["src/"]\nprotected_paths: ["src/{SURROGATE_ESCAPE}"]\n', encoding="utf-8")
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.TEXT_VALUE_INVALID])

    def test_a_raw_bad_byte_on_a_block_line_makes_that_block_defective_per_side(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/\xff"]\nprotected_paths: ["src/"]\n')
        result = self.run_guard(sha)
        self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID, repair_guard.PROTECTED_PATH_TOUCHED])
        self.dispatch.write_bytes(b'repair_allowlist: ["tools/"]\nprotected_paths: ["src/\xff"]\n')
        result = self.run_guard(sha)
        self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID, repair_guard.OUTSIDE_ALLOWLIST])

    def test_the_clean_entries_of_a_defective_block_are_not_used_either(self) -> None:
        sha = self.changed_outside_both()
        self.dispatch.write_text(f'repair_allowlist: ["src/", "x{SURROGATE_ESCAPE}"]\nprotected_paths: []\n', encoding="utf-8")
        rules = repair_guard.parse_dispatch(self.dispatch.read_text(encoding="utf-8"))
        self.assertEqual((rules.allowlist, rules.allowlist_defective, rules.protected_defective), ((), True, False))
        self.dispatch.write_text(f'repair_allowlist: []\nprotected_paths: ["src/", "x{SURROGATE_ESCAPE}"]\n', encoding="utf-8")
        rules = repair_guard.parse_dispatch(self.dispatch.read_text(encoding="utf-8"))
        self.assertEqual((rules.protected, rules.allowlist_defective, rules.protected_defective), ((), False, True))
        self.assertEqual(self.defect_codes(self.run_guard(sha)), [repair_guard.TEXT_VALUE_INVALID, repair_guard.OUTSIDE_ALLOWLIST])

    def test_a_clean_dispatch_has_no_defective_block(self) -> None:
        rules = repair_guard.parse_dispatch(dispatch_text(["tools/"], ["src/"]))
        self.assertEqual((rules.allowlist_defective, rules.protected_defective, rules.text_defects), (False, False, ()))
        self.assertEqual(len(rules.allowlist), 1)
        self.assertEqual(len(rules.protected), 1)

    def test_check_paths_judges_each_side_on_its_own(self) -> None:
        allow, protect = [repair_guard.make_rule("tools/", "t")], [repair_guard.make_rule("src/", "t")]
        both = repair_guard.check_paths(["src/x"], allow, protect, False, True, True)
        self.assertEqual([d.code for d in both], [repair_guard.OUTSIDE_ALLOWLIST, repair_guard.PROTECTED_PATH_TOUCHED])
        only_protected = repair_guard.check_paths(["src/x"], allow, protect, False, False, True)
        self.assertEqual([d.code for d in only_protected], [repair_guard.PROTECTED_PATH_TOUCHED])
        only_allow = repair_guard.check_paths(["src/x"], allow, protect, False, True, False)
        self.assertEqual([d.code for d in only_allow], [repair_guard.OUTSIDE_ALLOWLIST])
        neither = repair_guard.check_paths(["src/x"], allow, protect, False, False, False)
        self.assertEqual(neither, [])


class SurrogateAndBomTests(Fixture):
    """S56-19: the edges of the lone-surrogate range, and a byte order mark at the start of the dispatch."""

    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_the_whole_surrogate_range_and_nothing_next_to_it_is_a_text_defect(self) -> None:
        for code in (0xD800, 0xD801, 0xDBFF, 0xDC00, 0xDFFE, 0xDFFF):
            with self.subTest(code=hex(code)):
                self.assertIsNotNone(repair_guard.bad_character("a" + chr(code) + "b"))
        for code in (0xD7FF, 0xE000, 0x41, 0x20, 0x7E, 0x80, 0x9F, 0x10FFFF):
            with self.subTest(code=hex(code)):
                self.assertIsNone(repair_guard.bad_character("a" + chr(code) + "b"))
        for code in (0x00, 0x1F, 0x7F):
            with self.subTest(code=hex(code)):
                self.assertIsNotNone(repair_guard.bad_character(chr(code)))
        for code in (0x20, 0x7E, 0x80):
            self.assertIsNone(repair_guard.bad_character(chr(code)))

    def test_a_surrogate_at_the_top_of_the_range_in_an_entry_is_a_red_and_one_below_it_is_not(self) -> None:
        sha = self.committed()
        for escape, code in (("\\udfff", 1), ("\\ud800", 1), ("\\udbff", 1), ("\\ud7ff", 0), ("\\ue000", 0)):
            for block in ("repair_allowlist", "protected_paths"):
                with self.subTest(escape=escape, block=block):
                    entry = f'"x{escape}"'
                    allow = f'["tools/", {entry}]' if block == "repair_allowlist" else '["tools/"]'
                    protect = f"[{entry}]" if block == "protected_paths" else "[]"
                    self.dispatch.write_text(f"repair_allowlist: {allow}\nprotected_paths: {protect}\n", encoding="utf-8")
                    result = self.run_guard(sha)
                    self.assertEqual(result.code, code, result.out)
                    if code:
                        self.assertEqual(self.defect_codes(result), [repair_guard.TEXT_VALUE_INVALID])
                        self.assertIn("lone surrogate", result.lines[0])

    def test_a_surrogate_at_the_top_of_the_range_in_an_argument_is_a_usage_error_and_one_below_it_is_not(self) -> None:
        for bad in ("\udfff", "\udc80", "\ud800"):
            with self.subTest(bad=hex(ord(bad))):
                with self.assertRaises(repair_guard.UsageError):
                    repair_guard.parse_arguments(["--repo", "r", "--repair", "x" + bad, "--dispatch", "d"])
        for fine in ("퟿", ""):
            with self.subTest(fine=hex(ord(fine))):
                parsed = repair_guard.parse_arguments(["--repo", "r", "--repair", "x" + fine, "--dispatch", "d"])
                self.assertEqual(parsed.repair, "x" + fine)

    def test_a_surrogate_at_the_top_of_the_range_in_a_changed_path_is_a_text_defect(self) -> None:
        defects = repair_guard.check_paths(["tools/a\udfffb"], [repair_guard.make_rule("tools/", "t")], [], False)
        self.assertEqual([d.code for d in defects], [repair_guard.TEXT_VALUE_INVALID])
        self.assertEqual(repair_guard.check_paths(["tools/a퟿b"], [repair_guard.make_rule("tools/", "t")], [], False), [])

    def test_a_byte_order_mark_at_the_start_of_the_dispatch_is_removed(self) -> None:
        sha = self.committed()
        body = b'repair_allowlist: ["tools/"]\nprotected_paths: []\n'
        self.dispatch.write_bytes(b"\xef\xbb\xbf" + body)
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (0, "paths=1 defects=0\n"), result.err)
        self.dispatch.write_bytes(b"\xef\xbb\xbf" + b'protected_paths: []\nrepair_allowlist: ["tools/"]\n')
        self.assertEqual(self.run_guard(sha).code, 0)
        self.assertEqual(repair_guard.read_dispatch(str(self.dispatch)).startswith("﻿"), False)

    def test_only_one_byte_order_mark_at_the_very_start_is_removed(self) -> None:
        sha = self.committed()
        body = b'repair_allowlist: ["tools/"]\nprotected_paths: []\n'
        self.dispatch.write_bytes(b"\xef\xbb\xbf\xef\xbb\xbf" + body)
        self.assertEqual(self.run_guard(sha).code, 3)
        self.dispatch.write_bytes(b'title: x\n\xef\xbb\xbfrepair_allowlist: ["tools/"]\nprotected_paths: []\n')
        self.assertEqual(self.run_guard(sha).code, 3)
        self.dispatch.write_bytes(b'title: x\nrepair_allowlist: ["tools/"]\nprotected_paths: []\n')
        self.assertEqual(self.run_guard(sha).code, 0)

    def test_a_byte_order_mark_inside_a_block_value_is_a_text_value_not_a_removal(self) -> None:
        sha = self.committed()
        self.dispatch.write_bytes('repair_allowlist: ["tools/", "﻿t/"]\nprotected_paths: []\n'.encode("utf-8"))
        self.assertEqual(self.run_guard(sha).code, 0)
        self.dispatch.write_bytes('repair_allowlist: ["﻿tools/"]\nprotected_paths: []\n'.encode("utf-8"))
        result = self.run_guard(sha)
        self.assertEqual((result.code, self.defect_codes(result)), (1, [repair_guard.OUTSIDE_ALLOWLIST]))


if __name__ == "__main__":
    unittest.main()


class LevelJudgingTests(ObjectFixture):
    """S56-22: paths are judged level by level as each tree is verified (red before fault)."""

    LAYOUT = ("README.md", "src/x.py", "docs/d.py", "tools/a.py", "deep/one/two/three.py")

    def layout_change(self) -> tuple[str, str]:
        """(first parent, repair): the repair changes a file in every directory of LAYOUT."""
        self.base(*self.LAYOUT)
        parent = git(self.repo, "rev-parse", "HEAD")
        for rel in self.LAYOUT:
            self.write(rel, "fixed\n")
        return parent, self.commit("repair")

    def forge(self, commit: str, donor: str, depth: str) -> str:
        """Overwrite the tree of `commit` at `depth` with the content of the one of `donor`; return its id."""
        victim = git(self.repo, "rev-parse", f"{commit}:{depth}")
        copy = git(self.repo, "rev-parse", f"{donor}:{depth}")
        self.assertNotEqual(victim, copy)
        self.write_loose(self.object_path(victim), "tree", self.raw_body(copy, "tree"))
        return victim

    def outside(self, *paths: str) -> list[str]:
        return [f"{repair_guard.OUTSIDE_ALLOWLIST} {path!r}" for path in paths]

    def test_a_red_at_a_verified_level_is_reported_beside_a_forged_deep_subtree(self) -> None:
        parent, sha = self.layout_change()
        forged = self.forge(sha, parent, "deep/one/two")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual(result.code, 1, result.err)
        self.assertEqual(result.lines, self.outside("README.md", "docs/d.py", "src/x.py"))
        self.assertIn(forged, result.err)
        self.assertIn("hash", result.err)
        self.assertEqual(result.err.count("\n"), 1, result.err)

    def test_a_root_file_outside_the_allowlist_and_a_forged_gate_directory_give_exit_one(self) -> None:
        self.base("README.md", GATE_FILE, "tools/a.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        for rel in ("README.md", GATE_FILE, "tools/a.py"):
            self.write(rel, "fixed\n")
        sha = self.commit("repair")
        forged = self.forge(sha, parent, GATE_DIR)
        self.set_dispatch([GATE_DIR + "/", "tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines), (1, self.outside("README.md")), result.err)
        self.assertIn(forged, result.err)

    def test_reds_of_two_verified_levels_are_reported_in_path_order_beside_the_fault(self) -> None:
        parent, sha = self.layout_change()
        self.forge(sha, parent, "deep/one/two")
        self.set_dispatch(["tools/", "docs/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines), (1, self.outside("README.md", "src/x.py")), result.err)

    def test_a_forged_sibling_at_the_same_level_does_not_hide_the_reds_of_a_verified_one(self) -> None:
        parent, sha = self.layout_change()
        forged = self.forge(sha, parent, "docs")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines), (1, self.outside("README.md", "src/x.py")), result.err)
        self.assertIn(forged, result.err)
        self.assertNotIn("docs", result.out)

    def test_a_forged_first_parent_sibling_does_not_hide_the_reds_of_a_verified_one(self) -> None:
        parent, sha = self.layout_change()
        forged = self.forge(parent, sha, "src")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.lines), (1, self.outside("README.md", "docs/d.py")), result.err)
        self.assertIn(forged, result.err)

    def test_a_forged_root_tree_leaves_nothing_to_judge_and_is_exit_two(self) -> None:
        parent, sha = self.layout_change()
        tree = git(self.repo, "rev-parse", f"{sha}^{{tree}}")
        self.write_loose(self.object_path(tree), "tree", self.raw_body(git(self.repo, "rev-parse", f"{parent}^{{tree}}"), "tree"))
        self.set_dispatch([], [])
        result = self.run_guard(sha)
        self.assertEqual((result.code, result.out), (2, ""), result.err)
        self.assertIn(tree, result.err)

    def test_a_sibling_tree_that_cannot_be_parsed_does_not_hide_the_reds_of_a_verified_one(self) -> None:
        self.base("README.md", "src/x.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        self.write("README.md", "fixed\n")
        self.write("src/x.py", "fixed\n")
        sha = self.commit("repair")
        bad = git_raw(self.repo, ["hash-object", "--literally", "-w", "-t", "tree", "--stdin"], b"100644 a/b\0" + bytes(20))
        root = self.raw_body(git(self.repo, "rev-parse", f"{sha}^{{tree}}"), "tree")
        tree = git_raw(self.repo, ["hash-object", "--literally", "-w", "-t", "tree", "--stdin"], root + b"40000 bad\0" + bytes.fromhex(bad))
        broken = git(self.repo, "commit-tree", tree, "-p", parent, "-m", "repair with a tree that cannot be parsed")
        self.set_dispatch(["tools/"], [])
        result = self.run_guard(broken)
        self.assertEqual((result.code, result.lines), (1, self.outside("README.md", "src/x.py")), result.err)
        self.assertIn(bad, result.err)

    def test_the_walk_hands_over_each_level_before_it_reads_the_next(self) -> None:
        self.base("README.md", "src/x.py", "src/inner/y.py")
        parent = git(self.repo, "rev-parse", "HEAD")
        for rel in ("README.md", "src/x.py", "src/inner/y.py"):
            self.write(rel, "fixed\n")
        sha = self.commit("repair")
        events: list[tuple[str, tuple[str, ...]]] = []
        real = repair_guard.read_objects

        def recording(repo: str, ids: Sequence[str], kind: str) -> dict[str, bytes]:
            events.append(("read", ()))
            return real(repo, ids, kind)

        def handed(level: Sequence[str]) -> None:
            events.append(("judge", tuple(level)))

        with mock.patch.object(repair_guard, "read_objects", side_effect=recording):
            paths = repair_guard.diff_trees(
                str(self.repo), git(self.repo, "rev-parse", f"{parent}^{{tree}}"), git(self.repo, "rev-parse", f"{sha}^{{tree}}"), handed
            )
        self.assertEqual(
            events,
            [
                ("read", ()), ("judge", ("README.md",)),
                ("read", ()), ("judge", ("src/x.py",)),
                ("read", ()), ("judge", ("src/inner/y.py",)),
            ],
        )
        self.assertEqual(paths, ["README.md", "src/inner/y.py", "src/x.py"])

    def test_every_path_a_walk_returns_is_judged_even_when_it_never_handed_a_level_over(self) -> None:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        self.write("lib/b.py")
        self.commit("repair")
        self.set_dispatch(["tools/"], [])
        out = io.StringIO()
        with mock.patch.object(repair_guard, "diff_trees", return_value=["lib/b.py", "tools/a.py"]):
            with contextlib.redirect_stdout(out):
                code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual((code, out.getvalue()), (1, f"{repair_guard.OUTSIDE_ALLOWLIST} 'lib/b.py'\n"))

    def test_a_clean_walk_lists_reds_in_path_order_whatever_the_level(self) -> None:
        parent, sha = self.layout_change()
        self.set_dispatch([], [])
        result = self.run_guard(sha)
        self.assertEqual(
            result.lines,
            self.outside("README.md", "deep/one/two/three.py", "docs/d.py", "src/x.py", "tools/a.py"),
        )
        self.assertEqual(result.err, "")
