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

_EVIDENCE_BLOCK = """id = E27
title = 證據連結狀態
state = IN_PROGRESS
stage = IMPLEMENT | 實作 | DONE | REQUIRED | test:implementation
stage = REVIEW | 獨審 | NOT_VERIFIED | REQUIRED | -
stage = LOCAL | 本機驗證 | OPEN | REQUIRED | -
stage = DEVICE | 實機驗收 | NOT_VERIFIED | OPTIONAL | -
stage = RELEASE | 發布 | OPEN | OPTIONAL | -
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
        self.assertEqual(declared["children"], [])
        self.assertEqual(declared["findings"], [])
        self.assertEqual(
            declared["stages"],
            [
                {"ref": "R1", "label": "樣張", "state": "DONE"},
                {"ref": "R2", "label": "產生器", "state": "OPEN"},
            ],
        )
        self.assertIsNone(declared["released_in"])

    def test_five_column_stages_keep_requirement_and_evidence_metadata(self) -> None:
        declared = parse_status_block(_EVIDENCE_BLOCK)
        stages = declared["stages"]
        self.assertEqual(
            stages[0],
            {
                "ref": "IMPLEMENT",
                "label": "實作",
                "state": "DONE",
                "requirement": "REQUIRED",
                "evidence_ref": "test:implementation",
            },
        )
        self.assertEqual(stages[1]["state"], "NOT_VERIFIED")
        self.assertIsNone(stages[1]["evidence_ref"])
        self.assertEqual(stages[3]["requirement"], "OPTIONAL")

    def test_child_and_finding_metadata_are_optional_and_typed(self) -> None:
        declared = parse_status_block(
            "id = P1\ntitle = parent\nstate = IN_PROGRESS\n"
            "child = A1 | REQUIRED\n"
            "child = B1 | OPTIONAL\n"
            "finding = F1 | owner-a | OPEN | -\n"
            "finding = F2 | owner-b | CLOSED | review:F2-resolved\n"
        )
        self.assertEqual(
            declared["children"],
            [
                {"id": "A1", "requirement": "REQUIRED"},
                {"id": "B1", "requirement": "OPTIONAL"},
            ],
        )
        self.assertEqual(
            declared["findings"],
            [
                {
                    "id": "F1",
                    "owner": "owner-a",
                    "state": "OPEN",
                    "disposition_ref": None,
                },
                {
                    "id": "F2",
                    "owner": "owner-b",
                    "state": "CLOSED",
                    "disposition_ref": "review:F2-resolved",
                },
            ],
        )

    def test_child_ids_are_exact_and_must_not_repeat(self) -> None:
        with self.assertRaisesRegex(ValueError, "不可重複"):
            parse_status_block(
                "id = P1\ntitle = parent\nstate = DONE\n"
                "child = A1 | REQUIRED\nchild = A1 | OPTIONAL\n"
            )
        with self.assertRaises(ValueError):
            parse_status_block(
                "id = P1\ntitle = parent\nstate = DONE\nchild = A/1 | REQUIRED\n"
            )

    def test_findings_require_owner_and_closed_findings_require_bounded_ref(self) -> None:
        invalid_blocks = (
            "finding = F1 | - | OPEN | -",
            "finding = F1 | owner | OPEN | review:closed",
            "finding = F1 | owner | CLOSED | bad reference",
            "finding = F1 | owner | CLOSED | -",
            "finding = F1 | owner | OPEN | -\nfinding = F1 | owner | CLOSED | review:F1",
        )
        for finding in invalid_blocks:
            with self.subTest(finding=finding):
                with self.assertRaises(ValueError):
                    parse_status_block(
                        "id = P1\ntitle = parent\nstate = DONE\n" + finding + "\n"
                    )

    def test_a_mixed_legacy_and_evidence_stage_block_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "不可混用"):
            parse_status_block(
                "id = V9\ntitle = t\nstate = DONE\n"
                "stage = R1 | x | DONE\n"
                "stage = R2 | y | DONE | REQUIRED | test:ok\n"
            )

    def test_done_evidence_reference_is_bounded_and_required(self) -> None:
        for evidence_ref in ("-", "", "bad value", "x" * 129):
            with self.subTest(evidence_ref=evidence_ref):
                with self.assertRaises(ValueError):
                    parse_status_block(
                        "id = V9\ntitle = t\nstate = DONE\n"
                        f"stage = R1 | x | DONE | REQUIRED | {evidence_ref}\n"
                    )

    def test_unfinished_evidence_stage_requires_dash(self) -> None:
        with self.assertRaisesRegex(ValueError, "必須是 '-'"):
            parse_status_block(
                "id = V9\ntitle = t\nstate = DONE\n"
                "stage = R1 | x | OPEN | REQUIRED | test:pending\n"
            )

    def test_five_column_refs_are_unique_and_requirements_are_finite(self) -> None:
        duplicate = (
            "id = V9\ntitle = t\nstate = DONE\n"
            "stage = R1 | x | DONE | REQUIRED | test:one\n"
            "stage = R1 | y | OPEN | OPTIONAL | -\n"
        )
        with self.assertRaisesRegex(ValueError, "不可重複"):
            parse_status_block(duplicate)
        with self.assertRaises(ValueError):
            parse_status_block(
                "id = V9\ntitle = t\nstate = DONE\n"
                "stage = R1 | x | OPEN | SOMETIMES | -\n"
            )

    def test_approved_rejects_required_open_or_unverified_stages(self) -> None:
        for stage_state in ("OPEN", "NOT_VERIFIED"):
            with self.subTest(stage_state=stage_state):
                with self.assertRaisesRegex(ValueError, "未完成的 REQUIRED"):
                    parse_status_block(
                        "id = V9\ntitle = t\nstate = APPROVED\n"
                        f"stage = R1 | x | {stage_state} | REQUIRED | -\n"
                    )

    def test_approved_allows_optional_open_and_unverified_stages(self) -> None:
        declared = parse_status_block(
            "id = V9\ntitle = t\nstate = APPROVED\n"
            "stage = REVIEW | 獨審 | DONE | REQUIRED | review:approved\n"
            "stage = DEVICE | 實機驗收 | NOT_VERIFIED | OPTIONAL | -\n"
            "stage = RELEASE | 發布 | OPEN | OPTIONAL | -\n"
        )
        self.assertEqual(declared["state"], "APPROVED")
        self.assertEqual(declared["stages"][1]["state"], "NOT_VERIFIED")
        self.assertEqual(declared["stages"][2]["state"], "OPEN")

    def test_done_work_remains_done_without_an_explicit_review_verdict(self) -> None:
        declared = parse_status_block(
            "id = V9\ntitle = t\nstate = DONE\n"
            "stage = IMPLEMENT | 實作 | DONE | REQUIRED | test:implementation\n"
            "stage = REVIEW | 獨審 | OPEN | REQUIRED | -\n"
        )
        self.assertEqual(declared["state"], "DONE")

    def test_invalid_approved_block_remains_visible_as_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "evidence.md",
                _ticket(
                    "內容",
                    block=(
                        "id = E27\ntitle = 假綠\nstate = APPROVED\n"
                        "stage = LOCAL | 本機驗證 | NOT_VERIFIED | REQUIRED | -\n"
                    ),
                ),
            )
            _commit(root, "ticket with invalid projected approval")

            document = build_document(root)

            self.assertEqual(document["tickets"], [])
            self.assertEqual(len(document["unreadable"]), 1)
            self.assertEqual(
                document["unreadable"][0]["path"],
                "modules/tickets/demo/evidence.md",
            )

    def test_fixed_delivery_stages_do_not_invent_unapplied_completion(self) -> None:
        declared = parse_status_block(_EVIDENCE_BLOCK)
        self.assertEqual(
            [stage["ref"] for stage in declared["stages"]],
            ["IMPLEMENT", "REVIEW", "LOCAL", "DEVICE", "RELEASE"],
        )
        self.assertEqual(
            [stage["state"] for stage in declared["stages"]],
            ["DONE", "NOT_VERIFIED", "OPEN", "NOT_VERIFIED", "OPEN"],
        )

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


class ParentFindingProjectionTests(unittest.TestCase):
    @staticmethod
    def _status(ticket_id: str, state: str, *metadata: str) -> str:
        lines = [f"id = {ticket_id}", f"title = ticket {ticket_id}", f"state = {state}"]
        lines.extend(metadata)
        return "\n".join(lines) + "\n"

    def test_required_unverified_child_cannot_leave_parent_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "a.md",
                _ticket(
                    "A",
                    block=self._status(
                        "A",
                        "IN_PROGRESS",
                        "stage = TEST | 測試 | NOT_VERIFIED | REQUIRED | -",
                    ),
                ),
            )
            _write_ticket(
                root, "demo", "b.md", _ticket("B", block=self._status("B", "APPROVED"))
            )
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status(
                        "P",
                        "APPROVED",
                        "child = A | REQUIRED",
                        "child = B | REQUIRED",
                    ),
                ),
            )
            _write_ticket(
                root, "demo", "unrelated.md", _ticket("C", block=self._status("C", "DONE"))
            )
            _commit(root, "tickets: required child projection")

            document = build_document(root)
            visible_ids = {ticket["id"] for ticket in document["tickets"]}
            self.assertEqual(visible_ids, {"A", "B", "C"})
            parent_error = next(
                source
                for source in document["unreadable"]
                if source["path"] == "modules/tickets/demo/parent.md"
            )
            self.assertIn("必要子票 A", parent_error["reason"])
            self.assertNotIn("P", visible_ids)

    def test_optional_unfinished_child_is_visible_without_blocking_parent_or_peer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root, "demo", "b.md", _ticket("B", block=self._status("B", "DONE"))
            )
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status(
                        "P",
                        "APPROVED",
                        "child = B | OPTIONAL",
                        "finding = F9 | owner-z | CLOSED | review:F9-resolved",
                    ),
                ),
            )
            _write_ticket(
                root, "demo", "unrelated.md", _ticket("C", block=self._status("C", "IN_PROGRESS"))
            )
            _commit(root, "tickets: optional child projection")

            document = build_document(root)
            projected = {ticket["id"]: ticket for ticket in document["tickets"]}
            self.assertEqual(set(projected), {"B", "P", "C"})
            self.assertEqual(projected["P"]["state"], "APPROVED")
            self.assertEqual(projected["P"]["findings"][0]["state"], "CLOSED")
            self.assertEqual(
                projected["P"]["findings"][0]["disposition_ref"],
                "review:F9-resolved",
            )
            self.assertEqual(
                projected["P"]["children"],
                [
                    {
                        "id": "B",
                        "requirement": "OPTIONAL",
                        "state": "DONE",
                        "title": "ticket B",
                        "ticket_path": "modules/tickets/demo/b.md",
                    }
                ],
            )
            self.assertEqual(document["unreadable"], [])

    def test_unknown_required_child_only_marks_its_parent_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status("P", "APPROVED", "child = MISSING | REQUIRED"),
                ),
            )
            _write_ticket(
                root, "demo", "unrelated.md", _ticket("C", block=self._status("C", "DONE"))
            )
            _commit(root, "tickets: unknown required child")

            document = build_document(root)
            self.assertEqual([ticket["id"] for ticket in document["tickets"]], ["C"])
            self.assertEqual(len(document["unreadable"]), 1)
            self.assertIn("MISSING", document["unreadable"][0]["reason"])

    def test_optional_unknown_child_remains_explicit_and_does_not_invent_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status("P", "APPROVED", "child = MISSING | OPTIONAL"),
                ),
            )
            _commit(root, "tickets: unknown optional child")

            parent = build_document(root)["tickets"][0]
            self.assertEqual(parent["state"], "APPROVED")
            self.assertEqual(parent["children"][0]["state"], "UNKNOWN")

    def test_self_reference_and_cycles_are_unreadable_without_hiding_unrelated_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "a.md",
                _ticket("A", block=self._status("A", "APPROVED", "child = B | OPTIONAL")),
            )
            _write_ticket(
                root,
                "demo",
                "b.md",
                _ticket("B", block=self._status("B", "APPROVED", "child = A | OPTIONAL")),
            )
            _write_ticket(
                root,
                "demo",
                "self.md",
                _ticket("S", block=self._status("S", "DONE", "child = S | OPTIONAL")),
            )
            _write_ticket(
                root, "demo", "unrelated.md", _ticket("C", block=self._status("C", "DONE"))
            )
            _commit(root, "tickets: cyclic child projection")

            document = build_document(root)
            self.assertEqual([ticket["id"] for ticket in document["tickets"]], ["C"])
            reasons = {source["path"]: source["reason"] for source in document["unreadable"]}
            self.assertIn("循環", reasons["modules/tickets/demo/a.md"])
            self.assertIn("循環", reasons["modules/tickets/demo/b.md"])
            self.assertIn("自己", reasons["modules/tickets/demo/self.md"])

    def test_ambiguous_required_child_id_is_not_first_match_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root, "one", "a.md", _ticket("A1", block=self._status("A", "APPROVED"))
            )
            _write_ticket(
                root, "two", "a.md", _ticket("A2", block=self._status("A", "APPROVED"))
            )
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status("P", "APPROVED", "child = A | REQUIRED"),
                ),
            )
            _commit(root, "tickets: ambiguous child id")

            document = build_document(root)
            self.assertNotIn("P", {ticket["id"] for ticket in document["tickets"]})
            self.assertTrue(
                any("多筆工單" in source["reason"] for source in document["unreadable"])
            )

    def test_duplicate_declared_ticket_ids_are_unreadable_but_unrelated_ticket_remains(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "one",
                "parent.md",
                _ticket(
                    "First parent",
                    block=self._status("P", "APPROVED", "child = B | REQUIRED"),
                ),
            )
            _write_ticket(
                root,
                "two",
                "parent.md",
                _ticket(
                    "Second parent",
                    block=self._status("P", "APPROVED", "child = B | REQUIRED"),
                ),
            )
            _write_ticket(
                root,
                "demo",
                "child.md",
                _ticket("Child", block=self._status("B", "APPROVED")),
            )
            _write_ticket(
                root,
                "demo",
                "unrelated.md",
                _ticket("Unrelated", block=self._status("C", "DONE")),
            )
            _commit(root, "tickets: duplicate declared ids")

            document = build_document(root)
            self.assertEqual(
                {ticket["id"] for ticket in document["tickets"]},
                {"B", "C"},
            )
            unreadable_by_path = {
                source["path"]: source["reason"] for source in document["unreadable"]
            }
            self.assertEqual(
                set(unreadable_by_path),
                {
                    "modules/tickets/one/parent.md",
                    "modules/tickets/two/parent.md",
                },
            )
            self.assertTrue(
                all("重複" in reason for reason in unreadable_by_path.values())
            )

    def test_open_finding_invalidates_approved_parent_but_keeps_owner_when_open(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = _repository(Path(temporary))
            _write_ticket(
                root,
                "demo",
                "parent.md",
                _ticket(
                    "Parent",
                    block=self._status(
                        "P", "APPROVED", "finding = F1 | owner-x | OPEN | -"
                    ),
                ),
            )
            _write_ticket(
                root,
                "demo",
                "working.md",
                _ticket(
                    "Working",
                    block=self._status(
                        "W", "IN_PROGRESS", "finding = F2 | owner-y | OPEN | -"
                    ),
                ),
            )
            _commit(root, "tickets: finding closure projection")

            document = build_document(root)
            visible = {ticket["id"]: ticket for ticket in document["tickets"]}
            self.assertNotIn("P", visible)
            self.assertIn("OPEN Finding", document["unreadable"][0]["reason"])
            self.assertEqual(
                visible["W"]["findings"],
                [
                    {
                        "id": "F2",
                        "owner": "owner-y",
                        "state": "OPEN",
                        "disposition_ref": None,
                    }
                ],
            )


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
