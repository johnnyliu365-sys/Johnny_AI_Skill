"""P1: does the issuance gate hold when several workers are dispatched at once?

Everything the Router needs to keep books for parallel workers already exists —
`admit_dispatch` gates on owner authority, worktree containment, artifact
identity and a CAS issue, and journals every attempt. What has never been
exercised is more than one dispatch happening at the same time, which is the
shape this whole line depends on.

These cells use real processes rather than threads. A thread would share the
interpreter's file handles and could pass while two genuine processes race and
lose, which is exactly the false green this project has paid for before: W5
found the newer components carrying no cross-process lock at all while the
older ones did, and only a multi-process test could see it.

The host-agnostic cell (P1-R5) is here rather than in a lint config because it
is a design property, not a style rule. The owner's route is universal — Codex
has subagents too — and the moment the Router learns what a subagent is, it is
bound to one host and the property is gone.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionStatus,
    admit_dispatch,
    create_dispatch_grant,
    journal_path,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
)
from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionRequest,
)
from tests.test_dispatch_authority import _layout, _repository, _request
from tests.test_role_wake_composition import _receipt

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# Names that would bind the Router to one host. The route is universal, so the
# bookkeeping side must never learn how a worker is spawned.
_HOST_NAMES = ("subagent", "claude", "codex", "antigravity", "gemini")
# The behavioural boundary: this module decides who may dispatch and whether
# an issuance stands, and none of that may depend on which host spawned the
# worker.
_BOOKKEEPING_SOURCE = "library/local_orchestration/dispatch_authority.py"

# Containment is the documented exception, and the exception is narrow.
# It holds a list of directories that hosts create -- `.claude/worktrees` is
# chosen by the Claude Code harness, not by us -- so it cannot avoid naming
# them. That is data, and a second host only adds a row. What it must never
# hold is a host name in its logic, which is what the cell below pins.
_CONTAINMENT_SOURCE = "library/local_orchestration/worktree_containment.py"

_CHILD = '''\
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])

from library.local_orchestration.dispatch_authority import admit_dispatch
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.dispatch_authority import DispatchAdmissionRequest

layout = JohnnyRootLayout(base=Path(sys.argv[2]))
request = DispatchAdmissionRequest.model_validate_json(
    Path(sys.argv[3]).read_text(encoding="utf-8")
)
result = admit_dispatch(layout, request)
print(
    json.dumps(
        {
            "status": result.status.value,
            "failure": None if result.failure is None else result.failure.value,
            "receipt_id": None if result.receipt is None else result.receipt.receipt_id,
        }
    )
)
'''


def _run_child(script: Path, layout: JohnnyRootLayout, request_file: Path) -> dict:
    completed = subprocess.run(
        (
            sys.executable,
            str(script),
            str(_REPOSITORY_ROOT),
            str(layout.base),
            str(request_file),
        ),
        capture_output=True,
        timeout=180,
    )
    body = completed.stdout.decode("utf-8", errors="replace").strip()
    if not body:
        raise AssertionError(
            "child produced no verdict: " + completed.stderr.decode(errors="replace")
        )
    return json.loads(body.splitlines()[-1])


def _seed(base: Path) -> tuple[JohnnyRootLayout, Path, Path]:
    layout = _layout(base)
    repository = _repository(base)
    create_dispatch_grant(layout)
    script = base / "child.py"
    script.write_text(_CHILD, encoding="utf-8")
    return layout, repository, script


def _distinct_request(repository: Path, tag: str) -> DispatchAdmissionRequest:
    """Build a request for a genuinely different ticket, not a renamed one.

    Reusing the shared fixture and only swapping `receipt_id` produces two
    receipts for one ticket, which the gate correctly refuses. Two workers on
    two tickets means two identities all the way down.
    """

    receipt = _receipt().model_copy(
        update={
            "receipt_id": f"receipt-parallel-{tag}",
            "ticket_reference": f"ticket-parallel-{tag}",
            "handoff_reference": f"handoff-parallel-{tag}",
            "correlation_id": f"correlation-parallel-{tag}",
            "dispatch_question_id": f"question-parallel-{tag}",
            "worktree_fingerprint": f"worktree-parallel{tag}-01",
            "branch_fingerprint": f"branch-parallel{tag}-01",
        }
    )
    artifact = ApprovedDispatchArtifactRecord(
        project_id=receipt.project_id,
        ticket_reference=receipt.ticket_reference,
        ticket_revision=receipt.ticket_revision,
        ticket_digest=receipt.ticket_digest,
        ticket_document_commit=receipt.ticket_document_commit,
        handoff_reference=receipt.handoff_reference,
        handoff_revision=receipt.handoff_revision,
        handoff_digest=receipt.handoff_digest,
        handoff_document_commit=receipt.handoff_document_commit,
        baseline_commit=receipt.baseline_commit,
        implementation_owner_id=receipt.implementation_owner_id,
        expected_return=receipt.expected_return,
        descriptor_binding=receipt.descriptor_binding,
    )
    return DispatchAdmissionRequest(
        artifact=artifact,
        receipt_id=receipt.receipt_id,
        correlation_id=receipt.correlation_id,
        dispatch_question_id=receipt.dispatch_question_id,
        worktree_fingerprint=receipt.worktree_fingerprint,
        branch_fingerprint=receipt.branch_fingerprint,
        repository_root=str(repository),
        host_worktree_path=str(repository / ".worktrees" / f"w-{tag}"),
    )


def _write_request(base: Path, name: str, request) -> Path:
    path = base / f"{name}.json"
    path.write_text(request.model_dump_json(), encoding="utf-8")
    return path


class ParallelIssuanceTests(unittest.TestCase):
    """Two workers at once, from two real processes."""

    def test_two_different_tickets_each_receive_their_own_receipt(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository, script = _seed(base)
            (repository / ".worktrees" / "w-aaa").mkdir(parents=True)
            (repository / ".worktrees" / "w-bbb").mkdir(parents=True)
            first = _write_request(base, "a", _distinct_request(repository, "aaa"))
            second = _write_request(base, "b", _distinct_request(repository, "bbb"))

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(
                    pool.map(
                        lambda path: _run_child(script, layout, path),
                        (first, second),
                    )
                )

            for result in results:
                with self.subTest(receipt=result["receipt_id"]):
                    self.assertEqual(
                        result["status"],
                        DispatchAdmissionStatus.DISPATCHED.value,
                        result["failure"],
                    )
            self.assertEqual(
                {result["receipt_id"] for result in results},
                {"receipt-parallel-aaa", "receipt-parallel-bbb"},
            )

    def test_one_ticket_dispatched_twice_at_once_yields_one_receipt(self) -> None:
        """The property the whole line rests on: a ticket cannot go to two workers."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository, script = _seed(base)
            (repository / ".worktrees" / "w-same").mkdir(parents=True)
            request = _distinct_request(repository, "same")
            first = _write_request(base, "same-a", request)
            second = _write_request(base, "same-b", request)

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(
                    pool.map(
                        lambda path: _run_child(script, layout, path),
                        (first, second),
                    )
                )

            dispatched = [
                result
                for result in results
                if result["status"] == DispatchAdmissionStatus.DISPATCHED.value
            ]
            self.assertEqual(
                len(results), 2, "both children must have produced a verdict"
            )
            self.assertGreaterEqual(len(dispatched), 1)
            self.assertEqual(
                {result["receipt_id"] for result in dispatched},
                {"receipt-parallel-same"},
                "the same ticket must never resolve to two different receipts",
            )


class ContainmentTests(unittest.TestCase):
    """A worktree outside the repository root issues nothing at all."""

    def test_an_outside_worktree_is_refused_and_issues_no_receipt(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository, _ = _seed(base)
            outside = base / "elsewhere" / "w9"
            outside.mkdir(parents=True)
            request = _request(repository).model_copy(
                update={"host_worktree_path": str(outside)}
            )

            result = admit_dispatch(layout, request)
            self.assertIs(result.status, DispatchAdmissionStatus.REFUSED)
            self.assertIsNone(result.receipt)

            metadata = layout.queue_root / "metadata"
            issued = list(metadata.rglob("*")) if metadata.is_dir() else []
            self.assertEqual(
                [path for path in issued if path.is_file()],
                [],
                "a refusal must leave no issuance behind",
            )


class JournalTests(unittest.TestCase):
    """Every attempt is recorded, refusals included."""

    def test_a_refused_attempt_still_reaches_the_journal(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository, _ = _seed(base)
            outside = base / "elsewhere" / "w9"
            outside.mkdir(parents=True)
            admit_dispatch(
                layout,
                _request(repository).model_copy(
                    update={"host_worktree_path": str(outside)}
                ),
            )

            path = journal_path(layout)
            self.assertTrue(path.is_file(), "the journal must exist after an attempt")
            lines = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertTrue(lines)
            self.assertTrue(
                any(
                    "WORKTREE_OUTSIDE_REPOSITORY_ROOT" in json.dumps(entry)
                    for entry in lines
                ),
                "the refusal reason must be recorded, not just the refusal",
            )


class HostAgnosticTests(unittest.TestCase):
    """The bookkeeping side must not know how a worker is spawned.

    Codex has subagents and so does Claude; the route only stays universal
    while the Router refuses to learn the difference. Written as a test rather
    than a convention because a convention is what gets broken by whoever adds
    the next host in a hurry.
    """

    def test_the_dispatch_gate_names_no_host_at_all(self) -> None:
        body = (_REPOSITORY_ROOT / _BOOKKEEPING_SOURCE).read_text(
            encoding="utf-8"
        ).lower()
        for name in _HOST_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, body)

    def test_containment_names_hosts_only_in_its_path_allowlist(self) -> None:
        """The narrow exception, held to its width.

        Containment cannot avoid naming directories that hosts create, so the
        rule is not "no host names" but "no host name outside the allowlist".
        A host name reaching an `if` in this module would mean the Router had
        started behaving differently depending on who spawned the worker.
        """

        lines = (
            (_REPOSITORY_ROOT / _CONTAINMENT_SOURCE)
            .read_text(encoding="utf-8")
            .lower()
            .splitlines()
        )
        for number, line in enumerate(lines, start=1):
            if not any(name in line for name in _HOST_NAMES):
                continue
            stripped = line.strip()
            with self.subTest(line=number):
                self.assertTrue(
                    stripped.startswith("#") or "worktrees" in stripped,
                    f"a host name escaped the allowlist at line {number}: {stripped}",
                )


if __name__ == "__main__":
    unittest.main()
