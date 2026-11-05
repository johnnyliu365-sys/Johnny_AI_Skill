"""Ticket 59: the registered-failure checker, the real list and the workflow's static locks."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "ci" / "check_registered_failures.py"
REAL_LIST = REPO / "ci" / "registered-failures.json"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"


def row(test: str, reason: str = "the runner lacks a capability", follow_up: str = "environment") -> dict[str, str]:
    return {"test": test, "reason": reason, "follow_up": follow_up}


def case(classname: str, name: str, outcome: str | None = None) -> str:
    inner = {
        None: "",
        "failure": '<failure message="x">boom</failure>',
        "error": '<error message="x">boom</error>',
        "skipped": '<skipped message="s"/>',
    }[outcome]
    return f'<testcase classname="{classname}" name="{name}" time="0.001">{inner}</testcase>'


def report(*cases: str) -> str:
    body = "".join(cases)
    return f'<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest">{body}</testsuite></testsuites>'


class CheckerBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def run_checker(
        self,
        xml: str | bytes | None,
        registered: object,
        operating_system: str = "linux",
        raw_list: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        list_path = self.dir / "list.json"
        junit_path = self.dir / "junit.xml"
        if raw_list is not None:
            list_path.write_text(raw_list, encoding="utf-8")
        elif registered is not None:
            list_path.write_text(json.dumps(registered), encoding="utf-8")
        if xml is not None:
            junit_path.write_bytes(xml.encode("utf-8") if isinstance(xml, str) else xml)
        return subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(CHECKER), "--os", operating_system,
             "--junit", str(junit_path), "--list", str(list_path)],
            capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
        )


class NormalBehaviourTests(CheckerBase):
    def test_failures_equal_to_the_registered_set_exit_0(self) -> None:
        xml = report(case("tests.test_a", "test_one", "failure"), case("tests.test_a", "test_two"))
        result = self.run_checker(xml, {"linux": [row("tests/test_a.py::test_one")], "windows": []})
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_empty_report_and_empty_list_exit_0(self) -> None:
        result = self.run_checker(report(), {"linux": [], "windows": []})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_other_operating_systems_list_is_not_used(self) -> None:
        xml = report(case("tests.test_a", "test_one", "failure"))
        registered = {"linux": [], "windows": [row("tests/test_a.py::test_one")]}
        self.assertEqual(self.run_checker(xml, registered, "windows").returncode, 0)
        result = self.run_checker(xml, registered, "linux")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines(), ["UNREGISTERED_FAILURE tests/test_a.py::test_one"])

    def test_skipped_tests_are_not_failures(self) -> None:
        xml = report(case("tests.test_a", "test_one", "skipped"))
        self.assertEqual(self.run_checker(xml, {"linux": [], "windows": []}).returncode, 0)


class RuleViolationTests(CheckerBase):
    def test_an_unregistered_failure_is_named(self) -> None:
        xml = report(case("tests.test_a", "test_one", "failure"))
        result = self.run_checker(xml, {"linux": [], "windows": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines(), ["UNREGISTERED_FAILURE tests/test_a.py::test_one"])

    def test_a_registered_test_that_passed_is_named(self) -> None:
        xml = report(case("tests.test_a", "test_one"))
        result = self.run_checker(xml, {"linux": [row("tests/test_a.py::test_one")], "windows": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines(), ["REGISTERED_NOW_PASSING tests/test_a.py::test_one"])

    def test_an_error_counts_as_a_failure(self) -> None:
        xml = report(case("tests.test_a", "test_one", "error"))
        unregistered = self.run_checker(xml, {"linux": [], "windows": []})
        self.assertEqual(unregistered.returncode, 1)
        self.assertEqual(unregistered.stdout.splitlines(), ["UNREGISTERED_FAILURE tests/test_a.py::test_one"])
        registered = self.run_checker(xml, {"linux": [row("tests/test_a.py::test_one")], "windows": []})
        self.assertEqual(registered.returncode, 0)

    def test_a_registered_test_that_is_skipped_or_absent_is_not_a_pass_and_not_accepted(self) -> None:
        listed = {"linux": [row("tests/test_a.py::test_one")], "windows": []}
        skipped = self.run_checker(report(case("tests.test_a", "test_one", "skipped")), listed)
        self.assertEqual(skipped.returncode, 1)
        self.assertEqual(skipped.stdout.splitlines(), ["REGISTERED_NOT_FAILING tests/test_a.py::test_one"])
        absent = self.run_checker(report(), listed)
        self.assertEqual(absent.stdout.splitlines(), ["REGISTERED_NOT_FAILING tests/test_a.py::test_one"])

    def test_ids_are_compared_exactly_not_by_prefix(self) -> None:
        xml = report(case("tests.test_a", "test_one_more", "failure"))
        result = self.run_checker(xml, {"linux": [row("tests/test_a.py::test_one")], "windows": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout.splitlines(),
            ["UNREGISTERED_FAILURE tests/test_a.py::test_one_more",
             "REGISTERED_NOT_FAILING tests/test_a.py::test_one"],
        )

    def test_a_registered_prefix_of_a_failing_parametrised_id_does_not_cover_it(self) -> None:
        xml = report(case("tests.test_a", "test_p[b]", "failure"), case("tests.test_a", "test_p[a]", "failure"))
        result = self.run_checker(xml, {"linux": [row("tests/test_a.py::test_p[a]")], "windows": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines(), ["UNREGISTERED_FAILURE tests/test_a.py::test_p[b]"])
        both = self.run_checker(
            xml, {"linux": [row("tests/test_a.py::test_p[a]"), row("tests/test_a.py::test_p[b]")], "windows": []}
        )
        self.assertEqual(both.returncode, 0)

    def test_class_qualified_ids_are_built_from_the_classname(self) -> None:
        xml = report(case("tests.test_a.Outer.Inner", "test_one", "failure"))
        result = self.run_checker(xml, {"linux": [row("tests/test_a.py::Outer::Inner::test_one")], "windows": []})
        self.assertEqual(result.returncode, 0, result.stdout)
        short = self.run_checker(xml, {"linux": [row("tests/test_a.py::Outer::test_one")], "windows": []})
        self.assertEqual(short.returncode, 1)

    def test_a_collection_error_is_the_module_file(self) -> None:
        xml = (
            '<testsuites><testsuite><testcase classname="" name="tests.test_broken" time="0">'
            '<error message="collection failure">x</error></testcase></testsuite></testsuites>'
        )
        result = self.run_checker(xml, {"linux": [row("tests/test_broken.py")], "windows": []})
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_a_subject_with_a_newline_is_printed_on_one_line(self) -> None:
        xml = report(case("tests.test_a", "test_p[a&#10;INJECTED_LINE]", "failure"))
        result = self.run_checker(xml, {"linux": [], "windows": []})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertIn("\\n", result.stdout)

    def test_a_non_ascii_subject_is_escaped(self) -> None:
        xml = report(case("tests.test_a", "test_p[&#233;display]", "failure"))
        result = self.run_checker(xml, {"linux": [], "windows": []})
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertTrue(result.stdout.isascii())
        self.assertIn("\\xe9", result.stdout)


class SchemaAndInputTests(CheckerBase):
    def assert_exit_2(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(len(result.stderr.splitlines()), 1, result.stderr)

    def listed(self, **extra: object) -> dict[str, object]:
        value: dict[str, object] = dict(row("tests/test_a.py::test_one"))
        value.update(extra)
        return {"linux": [value], "windows": []}

    def test_a_row_without_a_reason_is_exit_2(self) -> None:
        without = {"test": "tests/test_a.py::test_one", "follow_up": "environment"}
        self.assert_exit_2(self.run_checker(report(), {"linux": [without], "windows": []}))

    def test_an_empty_or_blank_reason_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), self.listed(reason="")))
        self.assert_exit_2(self.run_checker(report(), self.listed(reason="   ")))

    def test_an_empty_follow_up_or_test_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), self.listed(follow_up="")))
        self.assert_exit_2(self.run_checker(report(), self.listed(test="")))

    def test_a_non_string_field_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), self.listed(reason=7)))

    def test_an_extra_field_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), self.listed(note="x")))

    def test_a_repeated_test_id_is_exit_2(self) -> None:
        duplicated = {"linux": [row("tests/test_a.py::test_one"), row("tests/test_a.py::test_one")], "windows": []}
        self.assert_exit_2(self.run_checker(report(), duplicated))

    def test_the_same_id_on_both_operating_systems_is_allowed(self) -> None:
        both = {"linux": [row("tests/test_a.py::test_one")], "windows": [row("tests/test_a.py::test_one")]}
        self.assertEqual(self.run_checker(report(case("tests.test_a", "test_one", "failure")), both).returncode, 0)

    def test_an_unknown_operating_system_key_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), {"linux": [], "windows": [], "macos": []}))

    def test_a_missing_operating_system_key_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), {"linux": []}))

    def test_a_list_that_is_not_an_object_or_not_an_array_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), []))
        self.assert_exit_2(self.run_checker(report(), {"linux": {}, "windows": []}))
        self.assert_exit_2(self.run_checker(report(), {"linux": ["tests/test_a.py::test_one"], "windows": []}))

    def test_a_list_that_is_not_json_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), None, raw_list="{not json"))
        self.assert_exit_2(self.run_checker(report(), None, raw_list=""))

    def test_a_missing_list_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(report(), None))

    def test_a_missing_report_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker(None, {"linux": [], "windows": []}))

    def test_a_malformed_report_is_exit_2(self) -> None:
        empty: dict[str, list[object]] = {"linux": [], "windows": []}
        self.assert_exit_2(self.run_checker("<testsuites><testsuite>", empty))
        self.assert_exit_2(self.run_checker("", empty))
        self.assert_exit_2(self.run_checker(b"\xff\xfe\x00garbage", empty))

    def test_a_report_with_the_wrong_root_or_a_doctype_is_exit_2(self) -> None:
        empty: dict[str, list[object]] = {"linux": [], "windows": []}
        self.assert_exit_2(self.run_checker("<html><testcase classname='a' name='b'/></html>", empty))
        self.assert_exit_2(self.run_checker('<!DOCTYPE x [<!ENTITY a "b">]><testsuites/>', empty))

    def test_a_testcase_without_a_name_is_exit_2(self) -> None:
        self.assert_exit_2(self.run_checker("<testsuites><testsuite><testcase classname='tests.test_a'/></testsuite></testsuites>",
                                            {"linux": [], "windows": []}))

    def test_bad_arguments_are_exit_3(self) -> None:
        def call(*arguments: str) -> int:
            return subprocess.run([sys.executable, "-I", "-X", "utf8", str(CHECKER), *arguments],
                                  capture_output=True, text=True, check=False, timeout=60).returncode
        self.assertEqual(call(), 3)
        self.assertEqual(call("--os", "linux"), 3)
        self.assertEqual(call("--junit", "x.xml"), 3)
        self.assertEqual(call("--os", "macos", "--junit", "x.xml"), 3)
        self.assertEqual(call("--os", "linux", "--junit", "x.xml", "--surprise"), 3)


class RealListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(REAL_LIST.read_text(encoding="utf-8"))

    def test_the_real_list_has_exactly_the_two_operating_systems(self) -> None:
        self.assertEqual(sorted(self.document), ["linux", "windows"])

    def test_every_row_has_a_cause_and_a_follow_up(self) -> None:
        for name, rows in self.document.items():
            seen: set[str] = set()
            for entry in rows:
                self.assertEqual(sorted(entry), ["follow_up", "reason", "test"], (name, entry))
                for key in ("test", "reason", "follow_up"):
                    self.assertTrue(isinstance(entry[key], str) and entry[key].strip(), (name, key, entry))
                self.assertNotIn("flaky", entry["reason"].lower(), (name, entry["test"]))
                self.assertRegex(entry["test"], r"^tests/test_[A-Za-z0-9_]+\.py(::|$)", (name, entry["test"]))
                self.assertNotIn(entry["test"], seen)
                seen.add(entry["test"])

    def test_the_real_list_passes_the_checker_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            junit = Path(tmp) / "junit.xml"
            junit.write_text(report(), encoding="utf-8")
            for name, rows in self.document.items():
                result = subprocess.run(
                    [sys.executable, "-I", "-X", "utf8", str(CHECKER), "--os", name, "--junit", str(junit),
                     "--list", str(REAL_LIST)],
                    capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
                )
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertEqual(len(result.stdout.splitlines()), len(rows))


class WorkflowLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_every_third_party_action_is_pinned_to_a_full_sha_with_a_version_comment(self) -> None:
        lines = self.text.splitlines()
        uses = [(i, line) for i, line in enumerate(lines) if re.match(r"^\s*-?\s*uses:", line)]
        self.assertTrue(uses)
        for index, line in uses:
            self.assertRegex(line, r"uses:\s+[\w.-]+/[\w./-]+@[0-9a-f]{40}\s*$", line)
            self.assertRegex(lines[index - 1], r"#\s*\S+\s+v\d+\.\d+\.\d+", lines[index - 1])

    def test_the_token_is_read_only_and_no_secret_is_read(self) -> None:
        lines = self.text.splitlines()
        blocks = [i for i, line in enumerate(lines) if re.match(r"^\s*permissions:", line)]
        self.assertEqual(blocks, [lines.index("permissions:")])
        entries: list[str] = []
        for line in lines[blocks[0] + 1:]:
            if not line.startswith(" "):
                break
            entries.append(line)
        self.assertEqual(entries, ["  contents: read"])
        for forbidden in ("secrets.", "GITHUB_TOKEN", "github.token", "id-token"):
            self.assertNotIn(forbidden, self.text)

    def test_the_matrix_triggers_and_steps_are_as_the_ticket_states(self) -> None:
        for needle in ("ubuntu-latest", "windows-latest", 'python-version: "3.11"', "fetch-depth: 0",
                       'PYTHONUTF8: "1"', "pip install -r requirements-dev.txt",
                       "python -m pytest tests -q -p no:cacheprovider -rf --junitxml=",
                       "--continue-on-collection-errors",
                       "python ci/check_registered_failures.py --os ${{ matrix.os_name }} --junit"):
            self.assertIn(needle, self.text)
        self.assertRegex(self.text, r"(?m)^on:\n  push:\n    branches: \[\"\*\*\"\]\n  pull_request:\n")

    def test_the_pytest_exit_is_not_the_job_result(self) -> None:
        pytest_line = next(line for line in self.text.splitlines() if "python -m pytest" in line)
        self.assertIn("||", pytest_line)

    def test_the_checker_step_exit_is_the_job_result(self) -> None:
        lines = self.text.splitlines()
        self.assertNotIn("continue-on-error", self.text)
        checkers = [i for i, line in enumerate(lines) if "ci/check_registered_failures.py" in line]
        self.assertEqual(len(checkers), 1)
        command = lines[checkers[0]]
        self.assertRegex(command, r'^\s+python ci/check_registered_failures\.py --os \$\{\{ matrix\.os_name \}\} --junit "\$RUNNER_TEMP/junit\.xml"$')
        for operator in ("||", ";", "|", "&", ">", "`", "$("):
            self.assertNotIn(operator, command.split("--junit", 1)[1].replace("$RUNNER_TEMP", ""))
        self.assertNotIn("||", command)
        self.assertEqual([line for line in lines[checkers[0] + 1:] if line.strip()], [])
        self.assertEqual(lines[checkers[0] - 1].strip(), "run: |")
        self.assertEqual(lines[checkers[0] - 2].strip(), "- name: Compare failures with the registered list")


if __name__ == "__main__":
    unittest.main()
