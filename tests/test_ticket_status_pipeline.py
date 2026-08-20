"""The ticket status pipeline: declared state only, and honest silence.

The two failures worth catching are opposites, and both are quiet. One is
inferring a status nobody declared. The other is dropping a ticket that meant
to be on the page because its block would not parse. Cells here assert the
distinction between "never opted in" and "opted in and broken", because a
pipeline that merges those two answers produces a page that looks calm while
work waits.
"""

from __future__ import annotations

import ast
import subprocess
import tempfile
import unittest
from pathlib import Path

from library.local_orchestration.ticket_status_pipeline import (
    build_document,
    discover_ticket_files,
    find_status_block,
    parse_status_block,
)

_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "library"
    / "local_orchestration"
    / "ticket_status_pipeline.py"
)

_GOOD_BLOCK = """id = V9
title = 測試用工單
state = NEEDS_OWNER
reason = 等你決定方向
stage = R1 | 樣張 | DONE
stage = R2 | 產生器 | OPEN
released_in = -
"""


def _ticket(body: str, *, block: str | None = _GOOD_BLOCK) -> str:
    text = f"# 測試工單\n\n{body}\n"
    if block is not None:
        text += f"\n```johnny-status\n{block}```\n"
    return text


def _repository(directory: Path) -> Path:
    """A real git repository: the pipeline's answers come from git itself."""

    subprocess.run(("git", "init", "-q", str(directory)), check=True)
    for name, value in (("user.email", "t@example.com"), ("user.name", "T")):
        subprocess.run(
            ("git", "-C", str(directory), "config", name, value), check=True
        )
    return directory


def _commit(root: Path, message: str) -> None:
    subprocess.run(("git", "-C", str(root), "add", "-A"), check=True)
    subprocess.run(
        ("git", "-C", str(root), "commit", "-q", "-m", message), check=True
    )


def _write_ticket(root: Path, module: str, name: str, text: str) -> Path:
    folder = root / "modules" / "tickets" / module
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


class BlockParsingTests(unittest.TestCase):
    """Declared facts are read exactly; anything else stops rather than guesses."""

    def test_a_complete_block_reads_every_declared_field(self) -> None:
        declared = parse_status_block(_GOOD_BLOCK)
        self.assertEqual(declared["id"], "V9")
        self.assertEqual(declared["state"], "NEEDS_OWNER")
        self.assertEqual(declared["reason"], "等你決定方向")
        self.assertEqual(
            declared["stages"],
            [
                {"ref": "R1", "label": "樣張", "state": "DONE"},
                {"ref": "R2", "label": "產生器", "state": "OPEN"},
            ],
        )
        self.assertIsNone(declared["released_in"])

    def test_a_mistyped_field_is_an_error_not_a_silent_drop(self) -> None:
        """`stat` instead of `state` would otherwise mean "nothing declared"."""

        with self.assertRaises(ValueError):
            parse_status_block("id = V9\ntitle = t\nstat = DONE\n")

    def test_a_duplicated_field_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_status_block("id = V9\ntitle = t\nstate = DONE\nstate = OPEN\n")

    def test_an_unknown_ticket_state_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_status_block("id = V9\ntitle = t\nstate = ALMOST\n")

    def test_an_unknown_stage_state_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_status_block(
                "id = V9\ntitle = t\nstate = DONE\nstage = R1 | x | NEARLY\n"
            )

    def test_needs_owner_without_a_reason_is_refused(self) -> None:
        """A row that says the owner is blocking without saying why is useless."""

        with self.assertRaises(ValueError):
            parse_status_block("id = V9\ntitle = t\nstate = NEEDS_OWNER\n")

    def test_a_reason_without_needs_owner_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_status_block(
                "id = V9\ntitle = t\nstate = DONE\nreason = 隨便\n"
            )

    def test_a_missing_required_field_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_status_block("title = t\nstate = DONE\n")

    def test_both_review_verdicts_are_declarable_states(self) -> None:
        """Finished and accepted are different answers, and both are states."""

        approved = parse_status_block("id = A\ntitle = t\nstate = APPROVED\n")
        self.assertEqual(approved["state"], "APPROVED")
        rejected = parse_status_block(
            "id = B\ntitle = t\nstate = REJECTED\nreason = 要補測試\n"
        )
        self.assertEqual(rejected["reason"], "要補測試")

    def test_rejected_without_a_reason_is_refused(self) -> None:
        """Work sent back without saying what to fix cannot be acted on."""

        with self.assertRaises(ValueError):
            parse_status_block("id = B\ntitle = t\nstate = REJECTED\n")

    def test_a_file_without_a_block_declares_nothing(self) -> None:
        self.assertIsNone(find_status_block("# 一般工單\n\n沒有宣告區塊。\n"))


class DocumentTests(unittest.TestCase):
    """Reading a real repository, with git as the source of "where"."""

    def test_a_declared_ticket_carries_its_commit_and_handoff_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            path = _write_ticket(root, "demo", "v9-demo.md", _ticket("內容"))
            _commit(root, "ticket: open V9")

            document = build_document(root)
            self.assertEqual(len(document["tickets"]), 1)
            ticket = document["tickets"][0]
            self.assertEqual(ticket["id"], "V9")
            self.assertEqual(ticket["module"], "demo")
            self.assertEqual(
                ticket["ticket_path"], "modules/tickets/demo/v9-demo.md"
            )
            self.assertIsNotNone(ticket["commit"])
            self.assertEqual(ticket["commit"]["subject"], "ticket: open V9")
            self.assertIn(ticket["commit"]["sha"], ticket["handoff_command"])
            self.assertIn(ticket["ticket_path"], ticket["handoff_command"])
            self.assertTrue(path.is_file())

    def test_a_ticket_that_never_opted_in_is_absent_not_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "plain.md", _ticket("內容", block=None))
            _commit(root, "ticket: plain")

            document = build_document(root)
            self.assertEqual(document["tickets"], [])
            self.assertEqual(document["unreadable"], [])

    def test_a_broken_block_is_reported_rather_than_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root, "demo", "broken.md", _ticket("內容", block="id = V9\nstat = x\n")
            )
            _commit(root, "ticket: broken")

            document = build_document(root)
            self.assertEqual(document["tickets"], [])
            self.assertEqual(len(document["unreadable"]), 1)
            self.assertEqual(
                document["unreadable"][0]["path"], "modules/tickets/demo/broken.md"
            )
            self.assertTrue(document["unreadable"][0]["reason"].strip())

    def test_one_broken_ticket_never_hides_the_readable_ones(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "good.md", _ticket("內容"))
            _write_ticket(
                root, "demo", "bad.md", _ticket("內容", block="id = V8\nstat = x\n")
            )
            _commit(root, "ticket: both")

            document = build_document(root)
            self.assertEqual(len(document["tickets"]), 1)
            self.assertEqual(len(document["unreadable"]), 1)

    def test_what_needs_the_owner_is_ordered_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "done.md",
                _ticket("內容", block="id = A1\ntitle = 完成\nstate = DONE\n"),
            )
            _write_ticket(root, "demo", "waiting.md", _ticket("內容"))
            _commit(root, "ticket: two")

            states = [item["state"] for item in build_document(root)["tickets"]]
            self.assertEqual(states, ["NEEDS_OWNER", "DONE"])

    def test_work_waiting_for_a_verdict_outranks_work_already_accepted(self) -> None:
        """Waiting for a review is a queue somebody has to clear; accepted is not."""

        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "a.md",
                _ticket("內容", block="id = A1\ntitle = 通過\nstate = APPROVED\n"),
            )
            _write_ticket(
                root,
                "demo",
                "b.md",
                _ticket("內容", block="id = B1\ntitle = 待審\nstate = DONE\n"),
            )
            _write_ticket(
                root,
                "demo",
                "c.md",
                _ticket(
                    "內容",
                    block=(
                        "id = C1\ntitle = 須修正\nstate = REJECTED\n"
                        "reason = 審查退回，要補回歸測試\n"
                    ),
                ),
            )
            _commit(root, "ticket: three verdicts")

            states = [i["state"] for i in build_document(root)["tickets"]]
            self.assertEqual(states, ["REJECTED", "DONE", "APPROVED"])

    def test_registries_and_templates_are_not_mistaken_for_tickets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "README.md", _ticket("登記表"))
            _write_ticket(root, "demo", "TEMPLATE.md", _ticket("樣板"))
            _commit(root, "ticket: registry")

            self.assertEqual(discover_ticket_files(root), ())
            self.assertEqual(build_document(root)["tickets"], [])

    def test_head_release_and_rollback_come_from_the_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "v9-demo.md", _ticket("內容"))
            _commit(root, "ticket: open V9")
            subprocess.run(("git", "-C", str(root), "tag", "v0.4.5"), check=True)
            subprocess.run(
                ("git", "-C", str(root), "tag", "rollback-pre-045"), check=True
            )

            document = build_document(root)
            self.assertTrue(document["head"]["commit"])
            self.assertEqual(document["release"]["version"], "v0.4.5")
            self.assertTrue(document["rollback"]["commit"])
            self.assertTrue(document["generated_at"])

    def test_a_repository_without_tags_reports_them_as_absent(self) -> None:
        """Null is a real answer here and must not become a fabricated one."""

        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "v9-demo.md", _ticket("內容"))
            _commit(root, "ticket: open V9")

            document = build_document(root)
            self.assertIsNone(document["release"])
            self.assertIsNone(document["rollback"])


class DeclaredCommitTests(unittest.TestCase):
    """Where the work stands is declared; editing the file is not doing work."""

    def test_a_declared_commit_outranks_the_files_last_touch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(root, "demo", "v9-demo.md", _ticket("內容"))
            _commit(root, "feat: the work itself")
            work = subprocess.run(
                ("git", "-C", str(root), "rev-parse", "--short", "HEAD"),
                capture_output=True, check=True,
            ).stdout.decode().strip()

            path = root / "modules" / "tickets" / "demo" / "v9-demo.md"
            path.write_text(
                _ticket("內容", block=_GOOD_BLOCK + f"commit = {work}\n"),
                encoding="utf-8",
            )
            _commit(root, "docs: only touch the status block")

            ticket = build_document(root)["tickets"][0]
            self.assertEqual(ticket["commit"]["sha"], work)
            self.assertEqual(ticket["commit"]["subject"], "feat: the work itself")
            self.assertIn(work, ticket["handoff_command"])

    def test_a_declared_commit_that_does_not_resolve_is_reported(self) -> None:
        """A typo must not become a handoff command that fails on use."""

        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "v9-demo.md",
                _ticket("內容", block=_GOOD_BLOCK + "commit = deadbee\n"),
            )
            _commit(root, "ticket: open V9")

            document = build_document(root)
            self.assertEqual(document["tickets"], [])
            self.assertEqual(len(document["unreadable"]), 1)
            self.assertIn("deadbee", document["unreadable"][0]["reason"])


class FieldRenameRegressionTests(unittest.TestCase):
    """V2-S4 item 2: the old field name must not survive anywhere it can be read.

    A rename that only touches the two production modules is not finished --
    a stray declaration left anywhere else Git tracks is a silent trap for
    the next file that copies it. This walks every tracked file rather than a
    fixed list, because a fixed list is exactly the kind of list that goes
    stale the day after it is written.
    """

    def test_no_tracked_file_still_declares_the_old_field(self) -> None:
        # Built rather than written so this assertion is never its own hit.
        old_field = "why" + "_waiting"
        repo_root = Path(__file__).resolve().parents[1]
        listing = subprocess.run(
            ("git", "ls-files"),
            cwd=str(repo_root),
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8").splitlines()

        offenders = []
        for relative in listing:
            path = repo_root / relative
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if old_field in text:
                offenders.append(relative)

        self.assertEqual(
            offenders,
            [],
            f"still reads the old field name {old_field!r} from: {offenders}",
        )


class DependencyTests(unittest.TestCase):
    """The runtime venv is hash-locked; this module may not widen it."""

    def test_the_module_imports_only_the_standard_library(self) -> None:
        allowed = {"__future__", "datetime", "pathlib", "re", "subprocess"}
        tree = ast.parse(_MODULE_PATH.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    with self.subTest(module=alias.name):
                        self.assertIn(alias.name.split(".")[0], allowed)
            elif isinstance(node, ast.ImportFrom) and not node.level:
                with self.subTest(module=node.module):
                    self.assertIn((node.module or "").split(".")[0], allowed)


if __name__ == "__main__":
    unittest.main()
