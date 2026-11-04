"""Behavioural tests for the tool-repair guard (exit codes 0/1/2/3).

Every fixture is generated in a temporary directory, including the git repositories the
guard reads. Expected values are derived from what a fixture wrote or from what the tool
printed, never copied from the script.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
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

    def test_a_malformed_name_status_stream_is_a_tool_fault(self) -> None:
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.parse_name_status(b"R100\0only-one-path\0")
        with self.assertRaises(repair_guard.ToolFault):
            repair_guard.parse_name_status(b"M\0")

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

    def test_name_status_parsing_keeps_both_sides_of_a_rename(self) -> None:
        data = b"M\0a.py\0R087\0old name.py\0new\xe5\xb7\xa5.py\0D\0gone.py\0"
        self.assertEqual(repair_guard.parse_name_status(data), ["a.py", "old name.py", "new\u5de5.py", "gone.py"])

    def test_a_git_path_with_invalid_utf8_becomes_a_text_red_not_a_fault(self) -> None:
        paths = repair_guard.parse_name_status(b"M\0bad\xff.py\0")
        defects = repair_guard.check_paths(paths, [repair_guard.make_rule("bad/", "t")], [], False)
        self.assertIn(repair_guard.TEXT_VALUE_INVALID, [d.code for d in defects])


class TextValueTests(Fixture):
    def committed(self) -> str:
        self.base("tools/a.py")
        self.write("tools/a.py", "fixed\n")
        return self.commit()

    def test_a_lone_surrogate_in_an_entry_of_the_dispatch_is_a_red_not_a_fault(self) -> None:
        sha = self.committed()
        for block in ("repair_allowlist", "protected_paths"):
            with self.subTest(block=block):
                other = "protected_paths" if block == "repair_allowlist" else "repair_allowlist"
                self.dispatch.write_text(
                    f'{block}: ["tools/{SURROGATE_ESCAPE}"]\n{other}: []\n', encoding="utf-8"
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
                    other = "protected_paths" if block == "repair_allowlist" else "repair_allowlist"
                    self.dispatch.write_bytes(
                        f'{block}: ["tools/'.encode() + raw + b'x/"]\n' + f"{other}: []\n".encode()
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
        with mock.patch.object(repair_guard, "parse_name_status", side_effect=repair_guard.ToolFault("boom")):
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
        with mock.patch.object(repair_guard, "parse_name_status", side_effect=repair_guard.ToolFault("boom")):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = repair_guard.main(["--repo", str(self.repo), "--repair", "HEAD", "--dispatch", str(self.dispatch)])
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("boom", err.getvalue())

    def test_a_root_commit_red_survives_an_unreadable_name_status(self) -> None:
        self.write("tools/a.py")
        self.commit("root")
        self.set_dispatch(["tools/"], [])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(repair_guard, "parse_name_status", side_effect=RuntimeError("odd")):
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


if __name__ == "__main__":
    unittest.main()
