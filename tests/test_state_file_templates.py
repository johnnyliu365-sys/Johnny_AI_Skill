"""Tests for the four state-file templates under template/ and the template README.

The expected key sets, field names and states are held here as data; no gate script is imported.
The two cross-checks (the receipt template filled in and read by the evidence gate, the configuration
template read by the integration script) run the script as a child process and skip, with a stated
reason, when the script is not present.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import NoReturn, Union

JsonValue = Union[None, bool, int, float, str, list["JsonValue"], dict[str, "JsonValue"]]

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "template"
GOVERNANCE_DIR = TEMPLATE_DIR / "doc" / "handoffs" / "governance"
README = TEMPLATE_DIR / "README.md"
TICKET_TEMPLATE = TEMPLATE_DIR / "modules" / "tickets" / "TEMPLATE.md"
QUEUE_TEMPLATE = GOVERNANCE_DIR / "MERGE-QUEUE.TEMPLATE.json"
CONFIG_TEMPLATE = GOVERNANCE_DIR / "integration.TEMPLATE.json"
RECEIPT_TEMPLATE = GOVERNANCE_DIR / "RECEIPT.TEMPLATE.md"
SCRIPTS_DIR = ROOT / "skills" / "johnny-project-takeover" / "scripts"
EVIDENCE_GATE = SCRIPTS_DIR / "evidence_gate.py"
INTEGRATE = SCRIPTS_DIR / "integrate.py"
GITATTRIBUTES = ROOT / ".gitattributes"

NEW_TEMPLATES = (QUEUE_TEMPLATE, CONFIG_TEMPLATE, RECEIPT_TEMPLATE)
ALL_TEMPLATES = (*NEW_TEMPLATES, TICKET_TEMPLATE, README)

# ----------------------------------------------------------------------------- expected data

QUEUE_BYTES = b'{"entries": []}\n'

CONFIG_KEYS = (
    "remote",
    "branch",
    "queue_branch",
    "queue_path",
    "spec_command",
    "invariant_command",
    "ci_status_command",
    "timeout_seconds",
)
STRING_KEYS = ("remote", "branch", "queue_branch", "queue_path")
ARGUMENT_LIST_KEYS = ("spec_command", "invariant_command", "ci_status_command")
SHA_TOKEN = "{sha}"
MAX_PATH_BYTES = 1024

RUN_FIELDS = ("cell", "candidate", "capture", "exit")
DIGEST_LABEL = "tool_digest:"
STATEMENT = "STATEMENT"
FENCE = "`" * 4

# every placeholder of the receipt template body and the value that replaces it in a filled receipt
RECEIPT_PLACEHOLDERS = (
    "<cell>",
    "<candidate-sha>",
    "<tool-path>",
    "<tool-sha256>",
    "<capture-path>",
    "<exit-codes>",
    "<capture-lines>",
    "<statement-text>",
)
PLACEHOLDER = re.compile(r"<[a-z0-9-]+>")

STATE_ROW_PREFIX = (
    "| 狀態 | `<STATE>`; dispatch=sha256:<64 lower-case hex of the dispatch file>; "
    "receipt `<repository-relative receipt path>`."
)
DISPATCH_PART = "dispatch=sha256:<64 lower-case hex of the dispatch file>"
RECEIPT_PART = "receipt `<repository-relative receipt path>`"
ALLOWED_STATES = frozenset(
    {
        "PLANNED",
        "IN_PROGRESS",
        "BLOCKED",
        "DONE",
        "SUPERSEDED",
        "REVIEW_APPROVED",
        "CONVERGENCE_REPLANNED",
    }
)
PENDING_SENTENCE = "The `dispatch=` and receipt parts are present while a dispatch is pending"
DIGEST_SENTENCE = "the sha256 of the dispatch file's bytes"

README_FILE_NAMES = (
    "MERGE-QUEUE.TEMPLATE.json",
    "integration.TEMPLATE.json",
    "RECEIPT.TEMPLATE.md",
    "modules/tickets/TEMPLATE.md",
)
README_QUEUE_BRANCH_SENTENCE = "The queue file lives on the queue branch, not on the integration branch"
README_STRUCTURE_QUEUE_COMMENT = "lives on the queue branch only"
README_ROW_QUEUE_PHRASE = "on the queue branch"
README_TICKET_COPY_TO = "`modules/tickets/<feature>/<ticket>.md`"
README_OLD_TICKET_COPY_TO = "`modules/tickets/<ticket>.md`"

GITATTRIBUTES_LINE = "template/doc/handoffs/governance/* text eol=lf"
GITATTRIBUTES_EXISTING_LINES = ("*.cmd text eol=crlf", "*.bat text eol=crlf")
CLONE_CHILD_ENV = "JAS_STATE_TEMPLATE_CLONE_CHILD"
CLONE_PATHS = ("template", "tests/test_state_file_templates.py", "skills/johnny-project-takeover/scripts")

# ----------------------------------------------------------------------------- helpers


class StrictJsonError(ValueError):
    """The text is not JSON this project accepts."""


def _refuse_constant(name: str) -> NoReturn:
    raise StrictJsonError(f"constant {name} is refused")


def _refuse_repeats(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    seen: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in seen:
            raise StrictJsonError(f"repeated key {key!r}")
        seen[key] = value
    return seen


def strict_loads(text: str) -> JsonValue:
    """json.loads with repeated keys, NaN, Infinity and a leading BOM refused."""
    if text.startswith("\ufeff"):
        raise StrictJsonError("byte order mark")
    value: JsonValue = json.loads(text, object_pairs_hook=_refuse_repeats, parse_constant=_refuse_constant)
    return value


def committed_bytes(path: Path) -> bytes:
    """The bytes of `path` as committed at HEAD, never the working copy.

    A checkout may rewrite line endings (core.autocrlf, a CRLF editor); every byte rule is judged on the
    blob, so a correct commit is green in any checkout. Git failing to serve the blob fails the test.
    """
    relative = path.relative_to(ROOT).as_posix()
    done = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", f"HEAD:./{relative}"],
        capture_output=True,
        env=clean_environment(),
    )
    if done.returncode != 0:
        raise AssertionError(f"the committed blob of {relative} cannot be read: {done.stderr.decode('utf-8', 'replace')}")
    return done.stdout


def committed_text(path: Path) -> str:
    return committed_bytes(path).decode("utf-8")


def normalised_text(path: Path) -> str:
    """The committed text of a file whose line ending no rule here governs, CRLF read as LF."""
    return committed_text(path).replace("\r\n", "\n")


def load_config() -> JsonValue:
    return strict_loads(committed_text(CONFIG_TEMPLATE))


def has_bad_text(text: str) -> bool:
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F or 0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def path_problem(path: str) -> str | None:
    """Why `path` is not a canonical repository-relative path, or None."""
    if not path:
        return "empty path"
    if has_bad_text(path):
        return "control character"
    if len(path.encode("utf-8")) > MAX_PATH_BYTES:
        return "too long"
    if "\\" in path:
        return "backslash"
    if path.startswith("/") or path.startswith(":") or re.match(r"[A-Za-z]:", path):
        return "absolute, drive letter or pathspec magic"
    for segment in path.split("/"):
        if segment in ("", ".", ".."):
            return f"segment {segment!r}"
    return None


def config_problems(value: JsonValue) -> list[str]:
    """Every way `value` departs from the integration configuration schema."""
    if not isinstance(value, dict):
        return ["not an object"]
    problems: list[str] = []
    for key in sorted(set(CONFIG_KEYS) - set(value)):
        problems.append(f"missing key {key}")
    for key in sorted(set(value) - set(CONFIG_KEYS)):
        problems.append(f"unknown key {key}")
    for key in STRING_KEYS:
        item = value.get(key)
        if key in value and (not isinstance(item, str) or not item or has_bad_text(item)):
            problems.append(f"{key} is not a non-empty clean string")
    if isinstance(value.get("branch"), str) and value.get("branch") == value.get("queue_branch"):
        problems.append("queue_branch equals branch (the queue must live on its own branch)")
    queue_path = value.get("queue_path")
    if isinstance(queue_path, str):
        why = path_problem(queue_path)
        if why is not None:
            problems.append(f"queue_path is not canonical: {why}")
    for key in ARGUMENT_LIST_KEYS:
        item = value.get(key)
        if key not in value:
            continue
        if not isinstance(item, list) or not item:
            problems.append(f"{key} is not a non-empty list")
        elif not all(isinstance(argument, str) and argument and not has_bad_text(argument) for argument in item):
            problems.append(f"{key} holds an argument that is not a non-empty clean string")
    status = value.get("ci_status_command")
    if isinstance(status, list):
        texts = [argument for argument in status if isinstance(argument, str)]
        occurrences = sum(argument.count(SHA_TOKEN) for argument in texts)
        if occurrences != 1 or texts.count(SHA_TOKEN) != 1:
            problems.append(f"ci_status_command holds {occurrences} {SHA_TOKEN} (exactly one argument must equal it)")
    timeout = value.get("timeout_seconds")
    if "timeout_seconds" in value and (isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0):
        problems.append("timeout_seconds is not a positive integer")
    return problems


def queue_problems(value: JsonValue) -> list[str]:
    if not isinstance(value, dict) or set(value) != {"entries"}:
        return ["queue is not an object with exactly the key entries"]
    if value["entries"] != []:
        return ["queue template holds an entry"]
    return []


def split_sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """The lines before the first `## ` heading, then each section as (heading, lines), fences respected."""
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in text.split("\n"):
        is_fence = line.rstrip() == FENCE
        if not in_fence and line.startswith("## ") and not is_fence:
            sections.append((line[3:].strip(), []))
            continue
        if is_fence:
            in_fence = not in_fence
        (sections[-1][1] if sections else preamble).append(line)
    return preamble, sections


def field_lines(lines: Sequence[str], name: str) -> list[str]:
    """The values of the lines `name: value` outside any fence."""
    values: list[str] = []
    in_fence = False
    for line in lines:
        if line.rstrip() == FENCE:
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith(f"{name}:"):
            values.append(line[len(name) + 1 :].strip())
    return values


def receipt_problems(text: str) -> list[str]:
    """Every way `text` departs from the receipt template shape."""
    problems: list[str] = []
    if "\r" in text:
        problems.append("holds a CR byte")
    if text.startswith("\ufeff"):
        problems.append("holds a byte order mark")
    _, sections = split_sections(text)
    runs = [item for item in sections if field_lines(item[1], "cell") != [STATEMENT]]
    statements = [item for item in sections if field_lines(item[1], "cell") == [STATEMENT]]
    if len(runs) != 1:
        problems.append(f"{len(runs)} run cells, expected 1")
    if len(statements) != 1:
        problems.append(f"{len(statements)} statement cells, expected 1")
    for heading, lines in runs:
        for name in RUN_FIELDS:
            values = field_lines(lines, name)
            if len(values) != 1 or not values[0]:
                problems.append(f"run cell {heading}: field {name} given {len(values)} times or empty")
        if field_lines(lines, "cell") != [heading]:
            problems.append(f"run cell {heading}: cell: line differs from the heading")
        labels = [line for line in lines if line.rstrip() == DIGEST_LABEL]
        if len(labels) != 1:
            problems.append(f"run cell {heading}: {len(labels)} tool_digest: labels")
        else:
            after = lines[lines.index(labels[0]) + 1 :]
            digest_lines: list[str] = []
            for line in after:
                if not line.startswith("- "):
                    break
                digest_lines.append(line)
            if len(digest_lines) != 1 or digest_lines[0].count("=") != 1:
                problems.append(f"run cell {heading}: expected one path=sha256 line")
        fences = [line for line in lines if line.rstrip() == FENCE]
        if len(fences) != 2:
            problems.append(f"run cell {heading}: {len(fences)} fence lines, expected 2")
    for heading, lines in statements:
        if any(field_lines(lines, name) for name in ("capture", "exit", DIGEST_LABEL.rstrip(":"))):
            problems.append(f"statement {heading} carries a run field")
        if any(line.rstrip() == FENCE for line in lines):
            problems.append(f"statement {heading} carries a fence")
    return problems


def state_row(text: str) -> str:
    rows = [line for line in text.split("\n") if line.startswith("| 狀態 |")]
    if len(rows) != 1:
        raise AssertionError(f"{len(rows)} state rows")
    return rows[0]


def state_row_problems(text: str) -> list[str]:
    problems: list[str] = []
    row = state_row(text)
    if not row.startswith(STATE_ROW_PREFIX):
        problems.append("state row does not start with the state, dispatch= and receipt parts")
    if row.count("dispatch=sha256:") != 1 or DISPATCH_PART not in row:
        problems.append("state row lacks the dispatch=sha256: part")
    if RECEIPT_PART not in row:
        problems.append("state row lacks the receipt part")
    states = re.search(r"is one of (.+?)\. The ", row)
    if states is None or set(re.findall(r"`([A-Z_]+)`", states.group(1))) != ALLOWED_STATES:
        problems.append("state row does not list exactly the allowed states")
    if PENDING_SENTENCE not in row:
        problems.append("state row does not say the parts are present while a dispatch is pending")
    if DIGEST_SENTENCE not in row:
        problems.append("state row does not say how the digest is computed")
    return problems


def remove_tree(path: Path) -> None:
    def make_writable(function: Callable[[str], object], name: str, _info: object) -> None:
        os.chmod(name, stat.S_IWRITE)
        function(name)

    shutil.rmtree(path, onerror=make_writable)


def clean_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["PYTHONUTF8"] = "1"
    return env


def run_git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=clean_environment(),
    )
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {done.stderr}")
    return done.stdout.strip()


def object_file_modes(repo: Path) -> dict[str, int]:
    """The mode bits of every loose object file and pack file of a repository, keyed by relative path."""
    objects = Path(run_git(repo, "rev-parse", "--path-format=absolute", "--git-path", "objects"))
    return {
        path.relative_to(objects).as_posix(): stat.S_IMODE(path.stat().st_mode)
        for path in objects.rglob("*")
        if path.is_file()
    }


def clone_without_hardlinks(source: Path, clone: Path) -> None:
    """A clone with no checkout and core.autocrlf=true, whose object files are copies, never links to the source's."""
    run_git(
        clone.parent,
        "clone", "-q", "--no-checkout", "--no-hardlinks", "-c", "core.autocrlf=true", str(source), str(clone),
    )


def git_available() -> bool:
    try:
        done = subprocess.run(["git", "--version"], capture_output=True, env=clean_environment())
    except OSError:
        return False
    return done.returncode == 0


# ----------------------------------------------------------------------------- the files themselves


class TemplateFileTests(unittest.TestCase):
    def test_every_template_exists_under_its_exact_name(self) -> None:
        for path in ALL_TEMPLATES:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), f"{path} is missing")
        self.assertEqual(
            sorted(item.name for item in GOVERNANCE_DIR.iterdir()),
            sorted(item.name for item in NEW_TEMPLATES),
            "the governance template directory holds exactly the three new templates",
        )

    def test_no_template_has_a_byte_order_mark_or_invalid_utf8(self) -> None:
        for path in ALL_TEMPLATES:
            with self.subTest(path=path.name):
                data = committed_bytes(path)
                self.assertFalse(data.startswith(b"\xef\xbb\xbf"), "BOM")
                data.decode("utf-8")

    def test_the_new_templates_are_lf_only_and_end_with_a_newline(self) -> None:
        for path in NEW_TEMPLATES:
            with self.subTest(path=path.name):
                data = committed_bytes(path)
                self.assertNotIn(b"\r", data)
                self.assertTrue(data.endswith(b"\n"))
                self.assertFalse(data.endswith(b"\n\n"))


class LineEndingPinTests(unittest.TestCase):
    def test_gitattributes_holds_the_pin_once_and_keeps_the_existing_lines(self) -> None:
        lines = committed_text(GITATTRIBUTES).split("\n")
        self.assertEqual(lines.count(GITATTRIBUTES_LINE), 1)
        for existing in GITATTRIBUTES_EXISTING_LINES:
            with self.subTest(existing=existing):
                self.assertIn(existing, lines)

    def test_git_reports_lf_for_each_of_the_three_templates(self) -> None:
        for path in NEW_TEMPLATES:
            relative = path.relative_to(ROOT).as_posix()
            with self.subTest(path=path.name):
                reported = run_git(ROOT, "check-attr", "--cached", "eol", "text", "--", relative).split("\n")
                self.assertEqual(
                    sorted(line.strip() for line in reported),
                    sorted([f"{relative}: eol: lf", f"{relative}: text: set"]),
                )


@unittest.skipIf(os.environ.get(CLONE_CHILD_ENV) == "1", "already inside a scratch clone run: no clone of a clone")
@unittest.skipUnless(git_available(), "git is absent: no scratch clone can be made")
class CrlfCheckoutTests(unittest.TestCase):
    """The byte rules and every other test of this file, run in a clone checked out with core.autocrlf=true."""

    modes_before: dict[str, int]

    @classmethod
    def setUpClass(cls) -> None:
        cls.modes_before = object_file_modes(ROOT)

    @classmethod
    def tearDownClass(cls) -> None:
        after = object_file_modes(ROOT)
        changed = sorted(name for name, mode in cls.modes_before.items() if name in after and after[name] != mode)
        if changed:
            raise AssertionError(f"{len(changed)} object file(s) of the repository under test changed mode, e.g. {changed[:3]}")

    def make_clone(self) -> Path:
        work = Path(tempfile.mkdtemp(prefix="state-template-clone-"))
        self.addCleanup(remove_tree, work)
        clone = work / "clone"
        head = run_git(ROOT, "rev-parse", "HEAD")
        clone_without_hardlinks(ROOT, clone)
        run_git(clone, "update-ref", "--no-deref", "HEAD", head)
        self.assertEqual(run_git(clone, "rev-parse", "HEAD"), head)
        self.assertEqual(run_git(clone, "config", "--local", "core.autocrlf"), "true")
        run_git(clone, "checkout", "-q", head, "--", ".gitattributes")
        run_git(clone, "checkout", "-q", head, "--", *CLONE_PATHS)
        return clone

    def run_file_in(self, clone: Path) -> None:
        env = clean_environment()
        env[CLONE_CHILD_ENV] = "1"
        done = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(clone / "tests" / "test_state_file_templates.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            cwd=clone,
        )
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("OK", done.stderr)

    def test_removing_the_clone_leaves_the_source_object_files_with_the_same_mode_bits(self) -> None:
        source = Path(tempfile.mkdtemp(prefix="state-template-source-"))
        self.addCleanup(remove_tree, source)
        run_git(source, "init", "-q")
        (source / "a.txt").write_bytes(b"content" + bytes([10]))
        run_git(source, "add", "a.txt")
        run_git(source, "commit", "-q", "-m", "one")
        object_files = [path for path in (source / ".git" / "objects").rglob("*") if path.is_file()]
        self.assertTrue(object_files)
        for path in object_files:
            os.chmod(path, stat.S_IREAD)
        before = object_file_modes(source)
        work = Path(tempfile.mkdtemp(prefix="state-template-clone-"))
        self.addCleanup(remove_tree, work)
        clone_without_hardlinks(source, work / "clone")
        self.assertTrue(any((work / "clone" / ".git" / "objects").rglob("*")))
        remove_tree(work / "clone")
        self.assertEqual(object_file_modes(source), before)

    def test_a_clone_with_autocrlf_true_keeps_the_three_templates_lf_and_is_green(self) -> None:
        clone = self.make_clone()
        for path in NEW_TEMPLATES:
            with self.subTest(path=path.name):
                self.assertNotIn(b"\r", (clone / path.relative_to(ROOT)).read_bytes())
        self.run_file_in(clone)

    def test_a_crlf_working_copy_of_a_correct_commit_is_green(self) -> None:
        clone = self.make_clone()
        for relative in (*(path.relative_to(ROOT) for path in ALL_TEMPLATES), Path(".gitattributes")):
            target = clone / relative
            data = target.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            target.write_bytes(data)
            with self.subTest(path=target.name):
                self.assertIn(b"\r\n", target.read_bytes(), "the scenario must hold CRLF bytes")
        self.run_file_in(clone)


class StrictJsonTests(unittest.TestCase):
    def test_repeated_keys_are_refused(self) -> None:
        with self.assertRaises(StrictJsonError):
            strict_loads('{"entries": [], "entries": []}')

    def test_nan_and_infinity_are_refused(self) -> None:
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), self.assertRaises(StrictJsonError):
                strict_loads(f'{{"timeout_seconds": {constant}}}')

    def test_a_byte_order_mark_is_refused(self) -> None:
        with self.assertRaises(StrictJsonError):
            strict_loads('\ufeff{"entries": []}')

    def test_both_json_templates_parse_strictly(self) -> None:
        for path in (QUEUE_TEMPLATE, CONFIG_TEMPLATE):
            with self.subTest(path=path.name):
                self.assertIsInstance(strict_loads(committed_text(path)), dict)


# ----------------------------------------------------------------------------- queue file


class QueueTemplateTests(unittest.TestCase):
    def test_the_queue_template_is_exactly_an_empty_entry_list_and_a_newline(self) -> None:
        self.assertEqual(committed_bytes(QUEUE_TEMPLATE), QUEUE_BYTES)
        self.assertEqual(strict_loads(committed_text(QUEUE_TEMPLATE)), {"entries": []})
        self.assertEqual(queue_problems(strict_loads(committed_text(QUEUE_TEMPLATE))), [])

    def test_a_queue_holding_an_entry_is_a_problem(self) -> None:
        self.assertTrue(queue_problems({"entries": [{"ticket": "x"}]}))

    def test_a_queue_with_another_key_or_a_non_list_is_a_problem(self) -> None:
        self.assertTrue(queue_problems({"entries": [], "extra": 1}))
        self.assertTrue(queue_problems({"entries": None}))
        self.assertTrue(queue_problems({}))
        self.assertTrue(queue_problems([]))


# ----------------------------------------------------------------------------- integration configuration


class ConfigTemplateTests(unittest.TestCase):
    def config(self) -> dict[str, JsonValue]:
        value = load_config()
        assert isinstance(value, dict)
        return value

    def test_the_configuration_holds_exactly_the_eight_keys(self) -> None:
        self.assertEqual(sorted(self.config()), sorted(CONFIG_KEYS))

    def test_the_configuration_has_no_problem(self) -> None:
        self.assertEqual(config_problems(self.config()), [])

    def test_each_value_has_the_right_json_type(self) -> None:
        config = self.config()
        for key in STRING_KEYS:
            with self.subTest(key=key):
                self.assertIsInstance(config[key], str)
        for key in ARGUMENT_LIST_KEYS:
            with self.subTest(key=key):
                value = config[key]
                assert isinstance(value, list)
                self.assertTrue(value, "no empty argument list")
                self.assertTrue(all(isinstance(argument, str) and argument for argument in value))
        timeout = config["timeout_seconds"]
        self.assertIsInstance(timeout, int)
        self.assertNotIsInstance(timeout, bool)
        assert isinstance(timeout, int)
        self.assertGreater(timeout, 0)

    def test_the_status_command_holds_exactly_one_sha_placeholder(self) -> None:
        value = self.config()["ci_status_command"]
        assert isinstance(value, list)
        self.assertEqual(value.count(SHA_TOKEN), 1)
        self.assertEqual(sum(str(argument).count(SHA_TOKEN) for argument in value), 1)

    def test_the_queue_branch_placeholder_differs_from_the_branch_placeholder(self) -> None:
        config = self.config()
        self.assertNotEqual(config["queue_branch"], config["branch"])

    def test_a_queue_branch_equal_to_the_branch_is_a_problem(self) -> None:
        config = self.config()
        config["queue_branch"] = config["branch"]
        self.assertTrue(config_problems(config))

    def test_the_queue_path_placeholder_is_a_canonical_repository_relative_path(self) -> None:
        value = self.config()["queue_path"]
        assert isinstance(value, str)
        self.assertIsNone(path_problem(value))

    def test_an_added_removed_or_renamed_key_is_a_problem(self) -> None:
        added = self.config()
        added["extra"] = "x"
        self.assertTrue(config_problems(added))
        for key in CONFIG_KEYS:
            with self.subTest(removed=key):
                removed = self.config()
                del removed[key]
                self.assertTrue(config_problems(removed))
            with self.subTest(renamed=key):
                renamed = self.config()
                renamed[key + "_x"] = renamed.pop(key)
                self.assertTrue(config_problems(renamed))

    def test_a_status_command_with_no_or_two_sha_placeholders_is_a_problem(self) -> None:
        for arguments in (["tool", "status"], ["tool", SHA_TOKEN, SHA_TOKEN], ["tool", f"--sha={SHA_TOKEN}"], [SHA_TOKEN, f"a{SHA_TOKEN}"]):
            with self.subTest(arguments=arguments):
                config = self.config()
                config["ci_status_command"] = list(arguments)
                self.assertTrue(config_problems(config))

    def test_an_empty_or_malformed_argument_list_is_a_problem(self) -> None:
        for key in ARGUMENT_LIST_KEYS:
            bad_lists: list[JsonValue] = [[], "tool", [""], [1], ["a", None]]
            for bad in bad_lists:
                with self.subTest(key=key, bad=bad):
                    config = self.config()
                    config[key] = bad
                    self.assertTrue(config_problems(config))

    def test_a_wrong_scalar_type_is_a_problem(self) -> None:
        for key in STRING_KEYS:
            bad_strings: list[JsonValue] = [1, None, "", ["x"], "bad" + chr(0) + "text"]
            for bad in bad_strings:
                with self.subTest(key=key, bad=bad):
                    config = self.config()
                    config[key] = bad
                    self.assertTrue(config_problems(config))
        bad_timeouts: list[JsonValue] = [0, -1, 1.5, "600", True, None]
        for bad in bad_timeouts:
            with self.subTest(timeout=bad):
                config = self.config()
                config["timeout_seconds"] = bad
                self.assertTrue(config_problems(config))

    def test_a_non_canonical_queue_path_is_a_problem(self) -> None:
        for bad in ("", "/abs/q.json", "a//q.json", "a/./q.json", "a/../q.json", "C:/q.json", "a\\q.json", "dir/", ":q.json", "./q.json"):
            with self.subTest(path=bad):
                config = self.config()
                config["queue_path"] = bad
                self.assertTrue(config_problems(config))

    def test_the_queue_path_prefix_cases_are_exact(self) -> None:
        for good in ("q.json", "a/q.json", "a/b.c/q.json", "Q.JSON"):
            with self.subTest(path=good):
                self.assertIsNone(path_problem(good))


# ----------------------------------------------------------------------------- receipt


class ReceiptTemplateTests(unittest.TestCase):
    def text(self) -> str:
        return committed_text(RECEIPT_TEMPLATE)

    def test_the_receipt_template_has_one_run_cell_and_one_statement_cell(self) -> None:
        self.assertEqual(receipt_problems(self.text()), [])

    def test_the_receipt_template_has_no_cr_byte(self) -> None:
        self.assertNotIn(b"\r", committed_bytes(RECEIPT_TEMPLATE))
        self.assertTrue(receipt_problems(self.text().replace("\n", "\r\n")))
        self.assertTrue(receipt_problems(self.text().replace("exit: ", "exit: \r")))

    def test_a_byte_order_mark_is_a_problem(self) -> None:
        self.assertTrue(receipt_problems("\ufeff" + self.text()))

    def test_a_missing_field_is_a_problem(self) -> None:
        for name in (*RUN_FIELDS, DIGEST_LABEL):
            with self.subTest(name=name):
                lines = [line for line in self.text().split("\n") if not line.startswith(name)]
                self.assertTrue(receipt_problems("\n".join(lines)))

    def test_a_repeated_field_or_second_cell_is_a_problem(self) -> None:
        for name in RUN_FIELDS:
            with self.subTest(name=name):
                lines = self.text().split("\n")
                index = next(i for i, line in enumerate(lines) if line.startswith(f"{name}:"))
                lines.insert(index, lines[index])
                self.assertTrue(receipt_problems("\n".join(lines)))
        body = self.text()
        self.assertTrue(receipt_problems(body + "\n" + body[body.index("## ") :]))

    def test_a_digest_line_without_a_hash_or_a_second_one_is_a_problem(self) -> None:
        lines = self.text().split("\n")
        index = lines.index(DIGEST_LABEL)
        without = lines[:]
        without[index + 1] = "- <tool-path>"
        self.assertTrue(receipt_problems("\n".join(without)))
        doubled = lines[:]
        doubled.insert(index + 1, lines[index + 1])
        self.assertTrue(receipt_problems("\n".join(doubled)))

    def test_a_statement_carrying_run_fields_is_a_problem(self) -> None:
        for extra in ("capture: x", "exit: 0", f"{FENCE}"):
            with self.subTest(extra=extra):
                self.assertTrue(receipt_problems(self.text() + extra + "\n"))

    def test_every_body_placeholder_is_listed_in_the_preamble_and_in_the_fill_data(self) -> None:
        preamble, sections = split_sections(self.text())
        body = "\n".join("\n".join(lines) for _, lines in sections) + "\n".join(heading for heading, _ in sections)
        in_body = set(PLACEHOLDER.findall(body))
        self.assertEqual(in_body, set(RECEIPT_PLACEHOLDERS))
        listed = set(PLACEHOLDER.findall("\n".join(line for line in preamble if line.startswith("| `<"))))
        self.assertEqual(listed, set(RECEIPT_PLACEHOLDERS), "the preamble names the placeholders a run replaces")


# ----------------------------------------------------------------------------- ticket state row and README


class StateRowTests(unittest.TestCase):
    def test_the_state_row_carries_the_dispatch_digest_and_receipt_parts(self) -> None:
        self.assertEqual(state_row_problems(normalised_text(TICKET_TEMPLATE)), [])

    def test_dropping_a_part_of_the_state_row_is_a_problem(self) -> None:
        text = normalised_text(TICKET_TEMPLATE)
        for dropped in (f"{DISPATCH_PART}; ", RECEIPT_PART, "dispatch=", "sha256:", PENDING_SENTENCE, DIGEST_SENTENCE):
            with self.subTest(dropped=dropped):
                self.assertIn(dropped, text)
                self.assertTrue(state_row_problems(text.replace(dropped, "", 1)))

    def test_a_missing_or_extra_state_is_a_problem(self) -> None:
        text = normalised_text(TICKET_TEMPLATE)
        for state in sorted(ALLOWED_STATES):
            with self.subTest(removed=state):
                self.assertTrue(state_row_problems(text.replace(f"`{state}`／", "").replace(f"／`{state}`", "")))
        self.assertTrue(state_row_problems(text.replace("／`DONE`", "／`DONE`／`ARCHIVED`")))

    def test_the_dispatch_token_is_compared_exactly(self) -> None:
        text = normalised_text(TICKET_TEMPLATE)
        for wrong in ("dispatch=sha1:", "dispatch: sha256:", "Dispatch=sha256:", "dispatch=sha256 "):
            with self.subTest(wrong=wrong):
                self.assertTrue(state_row_problems(text.replace("dispatch=sha256:", wrong, 1)))


class ReadmeTests(unittest.TestCase):
    def test_the_readme_lists_the_four_files(self) -> None:
        text = normalised_text(README)
        for name in README_FILE_NAMES:
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_the_readme_says_the_queue_file_lives_on_the_queue_branch(self) -> None:
        self.assertIn(README_QUEUE_BRANCH_SENTENCE, normalised_text(README))

    def test_the_structure_comment_for_the_queue_file_says_the_queue_branch(self) -> None:
        text = normalised_text(README)
        structure = text[text.index("## 固定結構") : text.index("## 建置順序")]
        lines = [line for line in structure.split("\n") if "MERGE-QUEUE.json" in line]
        self.assertEqual(len(lines), 1)
        self.assertIn(README_STRUCTURE_QUEUE_COMMENT, lines[0])
        self.assertNotIn("integration branch", lines[0])

    def state_files_rows(self) -> dict[str, list[str]]:
        text = normalised_text(README)
        section = text[text.index("## State files") :]
        rows: dict[str, list[str]] = {}
        for line in section.split("\n"):
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows[cells[0]] = cells
        return rows

    def test_the_state_files_row_for_the_queue_file_says_the_queue_branch(self) -> None:
        rows = self.state_files_rows()
        row = rows["`doc/handoffs/governance/MERGE-QUEUE.TEMPLATE.json`"]
        self.assertIn(README_ROW_QUEUE_PHRASE, row[1])
        self.assertNotIn("integration branch", " ".join(row))

    def test_the_state_files_row_for_the_ticket_copies_to_the_feature_path(self) -> None:
        rows = self.state_files_rows()
        self.assertEqual(rows["`modules/tickets/TEMPLATE.md`"][1], README_TICKET_COPY_TO)
        self.assertNotIn(README_OLD_TICKET_COPY_TO, normalised_text(README))

    def test_the_readme_puts_the_state_files_in_the_structure_and_the_build_order(self) -> None:
        text = normalised_text(README)
        structure = text[text.index("## 固定結構") : text.index("## 建置順序")]
        order = text[text.index("## 建置順序") : text.index("## State files")]
        for name in ("integration.json", "MERGE-QUEUE.json"):
            with self.subTest(name=name):
                self.assertIn(name, structure)
        self.assertIn("RECEIPT.TEMPLATE.md", structure)
        self.assertIn("State files", order)


# ----------------------------------------------------------------------------- cross-checks against the gate scripts


def fill_receipt(template: str, values: Mapping[str, str]) -> str:
    """The sections of the receipt template with every placeholder replaced; the preamble is dropped."""
    body = template[template.index("\n## ") + 1 :]
    for token, value in values.items():
        body = body.replace(token, value)
    return body


@unittest.skipUnless(
    EVIDENCE_GATE.is_file() and git_available(),
    "the evidence gate script or git is absent: the filled receipt cannot be read by it",
)
class EvidenceGateCrossCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.work = Path(tempfile.mkdtemp(prefix="state-template-"))
        self.addCleanup(remove_tree, self.work)
        self.repo = self.work / "repo"
        self.evidence = self.work / "evidence"
        (self.repo / "tools").mkdir(parents=True)
        self.evidence.mkdir()
        self.tool_path = "tools/probe.txt"
        self.tool_body = b"probe\n"
        (self.repo / self.tool_path).write_bytes(self.tool_body)
        run_git(self.repo, "init", "-q")
        run_git(self.repo, "add", self.tool_path)
        run_git(self.repo, "commit", "-q", "-m", "tool")
        self.sha = run_git(self.repo, "rev-parse", "HEAD")
        self.capture = "ok\nexit=0\n"
        (self.evidence / "C1.txt").write_bytes(self.capture.encode("utf-8"))

    def values(self, digest: str | None = None) -> dict[str, str]:
        return {
            "<cell>": "C1",
            "<candidate-sha>": self.sha,
            "<tool-path>": self.tool_path,
            "<tool-sha256>": digest if digest is not None else hashlib.sha256(self.tool_body).hexdigest(),
            "<capture-path>": "C1.txt",
            "<exit-codes>": "0",
            "<capture-lines>": self.capture.rstrip("\n"),
            "<statement-text>": "Nothing was left silent.",
        }

    def read(self, values: Mapping[str, str]) -> subprocess.CompletedProcess[str]:
        receipt = self.evidence / "RETURN.md"
        filled = fill_receipt(committed_text(RECEIPT_TEMPLATE), values)
        receipt.write_bytes(filled.encode("utf-8"))
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "-X",
                "utf8",
                str(EVIDENCE_GATE),
                str(receipt),
                "--repo",
                str(self.repo),
                "--candidate",
                self.sha,
                "--tool",
                self.tool_path,
                "--evidence-root",
                str(self.evidence),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=clean_environment(),
        )

    def test_the_filled_receipt_passes_the_evidence_gate(self) -> None:
        self.assertEqual(set(self.values()), set(RECEIPT_PLACEHOLDERS))
        done = self.read(self.values())
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("cells=1 defects=0", done.stdout)
        filled = fill_receipt(committed_text(RECEIPT_TEMPLATE), self.values())
        self.assertEqual(PLACEHOLDER.findall(filled), [])

    def test_the_gate_reads_the_filled_receipt_and_refuses_a_wrong_digest(self) -> None:
        done = self.read(self.values(digest="0" * 64))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("TOOL_DIGEST_STALE", done.stdout)


@unittest.skipUnless(
    INTEGRATE.is_file(),
    "the integration script is absent: its configuration parser cannot be run on the template",
)
class IntegrationConfigCrossCheck(unittest.TestCase):
    def test_the_configuration_with_placeholders_replaced_is_accepted(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="state-template-"))
        self.addCleanup(remove_tree, work)
        config = load_config()
        assert isinstance(config, dict)
        config["remote"] = str(work / "no-such-remote")
        config["branch"] = "main"
        config["queue_branch"] = "main-queue"
        config["queue_path"] = "doc/handoffs/2026/governance/MERGE-QUEUE.json"
        config["spec_command"] = ["spec-runner"]
        config["invariant_command"] = ["invariant-runner"]
        config["ci_status_command"] = ["status-tool", SHA_TOKEN]
        path = work / "integration.json"
        path.write_text(json.dumps(config), encoding="utf-8", newline="\n")
        done = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(INTEGRATE), "readback", "--config", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=clean_environment(),
            cwd=work,
        )
        # exit 3 is a usage or configuration error; the remote does not exist, so a served parse ends in 1 or 2
        self.assertNotEqual(done.returncode, 3, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
