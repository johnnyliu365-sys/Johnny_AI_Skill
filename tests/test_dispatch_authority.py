"""W1: receipt issuance is a granted, gated, journaled workstation entry."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import dispatch_authority, event_runner
from library.local_orchestration import worker_assignment
from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionFailure,
    DispatchAdmissionRequest,
    DispatchAdmissionStatus,
    DispatchGrantStatus,
    ReceiptRevocationFailure,
    ReceiptRevocationRequest,
    ReceiptRevocationStatus,
    admit_dispatch,
    create_dispatch_grant,
    journal_path,
    revoke_dispatch_receipt,
)
from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.runner_receipt_seeding import (
    ReceiptVerificationStatus,
    verify_receipt_claimable,
)
from library.local_orchestration.subscription_builder import (
    SubscriptionBuildStatus,
    SubscriptionInputs,
    build_subscription,
)
from library.local_orchestration.wake_capability import wake_config_path
from library.local_orchestration.wake_scoped_boundary import (
    WakeScopedDispatchBoundary,
)
from library.local_orchestration.worker_assignment import (
    WorkerClaimRequest,
    WorkerClaimStatus,
    WorkerSettlementRequest,
    WorkerSettlementStatus,
    claim_worker_assignment,
    ledger_path,
    settle_worker_assignment,
)
from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
)
from library.workflow_router.supervision_policy import SupervisionClass
from tests.test_role_wake_composition import _receipt


def _layout(base: Path) -> JohnnyRootLayout:
    layout = JohnnyRootLayout(base=(base / "johnny").resolve())
    layout.queue_root.mkdir(parents=True, exist_ok=True)
    return layout


def _repository(base: Path) -> Path:
    repository = base / "repo"
    (repository / ".worktrees" / "w1").mkdir(parents=True)
    return repository


def _request(repository: Path, receipt_id: str | None = None) -> DispatchAdmissionRequest:
    receipt = _receipt()
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
        receipt_id=receipt_id if receipt_id is not None else receipt.receipt_id,
        correlation_id=receipt.correlation_id,
        dispatch_question_id=receipt.dispatch_question_id,
        worktree_fingerprint=receipt.worktree_fingerprint,
        branch_fingerprint=receipt.branch_fingerprint,
        repository_root=str(repository),
        host_worktree_path=str(repository / ".worktrees" / "w1"),
    )


def _make_junction(link: Path, target: Path) -> bool:
    completed = subprocess.run(
        ("cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)),
        check=False,
        capture_output=True,
        shell=False,
        timeout=30,
    )
    return completed.returncode == 0


class GrantTests(unittest.TestCase):
    """W1-R1: no grant, no issuance; granting is explicit and idempotent."""

    def test_admission_without_a_grant_refuses_and_writes_no_receipt(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            result = admit_dispatch(layout, _request(_repository(base)))
            self.assertIs(result.status, DispatchAdmissionStatus.REFUSED)
            self.assertIs(
                result.failure, DispatchAdmissionFailure.DISPATCH_AUTHORITY_ABSENT
            )
            metadata_root = layout.queue_root / "metadata"
            checkpoint_files = (
                [p for p in metadata_root.rglob("*") if p.is_file()]
                if metadata_root.exists()
                else []
            )
            self.assertEqual(checkpoint_files, [])

    def test_granting_twice_returns_the_same_grant(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = _layout(Path(temporary))
            first_status, first = create_dispatch_grant(layout)
            second_status, second = create_dispatch_grant(layout)
            self.assertIs(first_status, DispatchGrantStatus.GRANTED)
            self.assertIs(second_status, DispatchGrantStatus.ALREADY_GRANTED)
            assert first is not None and second is not None
            self.assertEqual(first.grant_id, second.grant_id)


class ContainmentGateTests(unittest.TestCase):
    """W1-R2: governance 02's dispatch gate, wired and fail-closed."""

    def test_a_sibling_worktree_refuses_before_any_store_effect(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            sibling = base / "repo-w1"
            sibling.mkdir()
            request = _request(repository).model_copy(
                update={"host_worktree_path": str(sibling)}
            )
            result = admit_dispatch(layout, request)
            self.assertIs(result.status, DispatchAdmissionStatus.REFUSED)
            self.assertIs(
                result.failure,
                DispatchAdmissionFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT,
            )
            metadata_root = layout.queue_root / "metadata"
            checkpoint_files = (
                [p for p in metadata_root.rglob("*") if p.is_file()]
                if metadata_root.exists()
                else []
            )
            self.assertEqual(checkpoint_files, [])

    def test_a_junctioned_worktree_refuses_identically(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            outside = base / "outside"
            outside.mkdir()
            link = repository / ".worktrees" / "w1-linked"
            if not _make_junction(link, outside):
                self.skipTest("junction creation unavailable on this host")
            request = _request(repository).model_copy(
                update={"host_worktree_path": str(link)}
            )
            result = admit_dispatch(layout, request)
            self.assertIs(result.status, DispatchAdmissionStatus.REFUSED)
            self.assertIs(
                result.failure,
                DispatchAdmissionFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT,
            )


class AdmissionTests(unittest.TestCase):
    """W1-R3: issue, readback, journal; idempotent repeat; conflict refusal."""

    def test_a_valid_request_dispatches_and_reads_back_claimable(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            _, grant = create_dispatch_grant(layout)
            assert grant is not None
            result = admit_dispatch(layout, _request(_repository(base)))
            self.assertIs(result.status, DispatchAdmissionStatus.DISPATCHED, f"{result.failure}")
            assert result.receipt is not None

            boundary = WakeScopedDispatchBoundary(layout.queue_root / "metadata")
            verification, _ = verify_receipt_claimable(boundary, result.receipt)
            self.assertIs(verification, ReceiptVerificationStatus.CLAIMABLE)

            lines = journal_path(layout).read_text(encoding="utf-8").splitlines()
            last = json.loads(lines[-1])
            self.assertEqual(last["outcome"], "DISPATCHED")
            self.assertEqual(last["grant_id"], grant.grant_id)
            self.assertEqual(last["receipt_id"], result.receipt.receipt_id)
            self.assertTrue(last["principal"])

    def test_an_identical_repeat_is_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            first = admit_dispatch(layout, _request(repository))
            second = admit_dispatch(layout, _request(repository))
            self.assertIs(first.status, DispatchAdmissionStatus.DISPATCHED)
            self.assertIs(second.status, DispatchAdmissionStatus.DISPATCHED)
            assert first.receipt is not None and second.receipt is not None
            self.assertEqual(first.receipt, second.receipt)

    def test_a_conflicting_receipt_id_refuses_without_replacing(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            first = admit_dispatch(layout, _request(repository))
            assert first.receipt is not None
            conflicting = admit_dispatch(
                layout, _request(repository, receipt_id="receipt-vita-feature-999")
            )
            self.assertIs(conflicting.status, DispatchAdmissionStatus.REFUSED)
            self.assertIs(
                conflicting.failure, DispatchAdmissionFailure.RECEIPT_CONFLICT
            )
            boundary = WakeScopedDispatchBoundary(layout.queue_root / "metadata")
            verification, _ = verify_receipt_claimable(boundary, first.receipt)
            self.assertIs(verification, ReceiptVerificationStatus.CLAIMABLE)


class ReceiptRevocationTests(unittest.TestCase):
    """P5-R2: reopening the books is granted, proved, journaled — or refused.

    The gate that ends a receipt is deliberately shaped like the gate that
    makes one, and it carries one check issuance does not: the assignment
    ledger has to show the claim actually came home. That check is the reason
    the redispatch route cannot become a second door onto the same ticket.
    """

    def _granted(self, base: Path) -> tuple[JohnnyRootLayout, Path]:
        layout = _layout(base)
        create_dispatch_grant(layout)
        return layout, _repository(base)

    def _admitted(self, layout: JohnnyRootLayout, repository: Path) -> str:
        admitted = admit_dispatch(layout, _request(repository))
        self.assertIs(
            admitted.status, DispatchAdmissionStatus.DISPATCHED, f"{admitted.failure}"
        )
        assert admitted.receipt is not None
        return admitted.receipt.receipt_id

    def _claim(
        self, layout: JohnnyRootLayout, repository: Path, receipt_ref: str
    ) -> str:
        claimed = claim_worker_assignment(
            layout,
            WorkerClaimRequest(
                receipt_ref=receipt_ref,
                worker_ref="worker-p5-cell-01",
                worktree_ref="worktree-vitafeature-01",
                branch_ref="branch-vitafeature-01",
                repository_root=str(repository),
                host_worktree_path=str(repository / ".worktrees" / "w1"),
            ),
        )
        self.assertIs(claimed.status, WorkerClaimStatus.CLAIMED, f"{claimed.failure}")
        assert claimed.assignment is not None
        return claimed.assignment.claim_id

    def _compensate(
        self, layout: JohnnyRootLayout, claim_id: str, receipt_ref: str
    ) -> None:
        settled = settle_worker_assignment(
            layout,
            WorkerSettlementRequest(claim_id=claim_id, receipt_ref=receipt_ref),
        )
        self.assertIs(settled.status, WorkerSettlementStatus.SETTLED)

    def _compensated(self, base: Path) -> tuple[JohnnyRootLayout, Path, str]:
        """A granted layout whose one receipt was claimed and then settled."""

        layout, repository = self._granted(base)
        receipt_ref = self._admitted(layout, repository)
        self._compensate(layout, self._claim(layout, repository, receipt_ref), receipt_ref)
        return layout, repository, receipt_ref

    def _revocation(
        self, receipt_ref: str, replacement: str = "receipt-vita-feature-002"
    ) -> ReceiptRevocationRequest:
        return ReceiptRevocationRequest(
            project_id="prj_0123456789abcdef",
            ticket_reference="ticket-vita-feature-001",
            receipt_id=receipt_ref,
            replacement_receipt_id=replacement,
        )

    def _last_line(self, layout: JohnnyRootLayout) -> dict:
        lines = journal_path(layout).read_text(encoding="utf-8").splitlines()
        return json.loads(lines[-1])

    def _metadata_bytes(self, layout: JohnnyRootLayout) -> list[bytes]:
        metadata = layout.queue_root / "metadata"
        if not metadata.exists():
            return []
        return sorted(path.read_bytes() for path in metadata.rglob("*") if path.is_file())

    def test_a_compensated_receipt_is_revoked_and_journaled_with_both_receipts(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, receipt_ref = self._compensated(base)
            _, grant = create_dispatch_grant(layout)
            assert grant is not None

            result = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(result.status, ReceiptRevocationStatus.REVOKED, f"{result.failure}")
            assert result.receipt is not None
            self.assertEqual(receipt_ref, result.receipt.receipt_id)

            last = self._last_line(layout)
            self.assertEqual("REVOCATION_REVOKED", last["outcome"])
            self.assertEqual(receipt_ref, last["receipt_id"])
            self.assertEqual(
                "receipt-vita-feature-002", last["superseded_by_receipt_id"]
            )
            self.assertEqual("ticket-vita-feature-001", last["ticket_reference"])
            self.assertEqual(grant.grant_id, last["grant_id"])
            self.assertTrue(last["principal"])
            self.assertTrue(last["at_utc"])

    def test_an_admission_line_names_no_superseded_receipt(self) -> None:
        """One key set on every line, so absence never has to be interpreted."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository = self._granted(base)
            self._admitted(layout, repository)

            last = self._last_line(layout)
            self.assertEqual("DISPATCHED", last["outcome"])
            self.assertIn("superseded_by_receipt_id", last)
            self.assertIsNone(last["superseded_by_receipt_id"])

    def test_an_open_claim_refuses_the_revocation_and_the_receipt_stands(self) -> None:
        """The exactly-once guard: an uncompensated ticket is never reopened."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository = self._granted(base)
            receipt_ref = self._admitted(layout, repository)
            self._claim(layout, repository, receipt_ref)
            before = self._metadata_bytes(layout)

            result = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(result.failure, ReceiptRevocationFailure.CLAIM_STILL_OPEN)
            self.assertIsNone(result.receipt)
            self.assertEqual(before, self._metadata_bytes(layout))
            self.assertEqual(
                "REVOCATION_CLAIM_STILL_OPEN", self._last_line(layout)["outcome"]
            )

    def test_a_never_claimed_receipt_is_refused_as_assignment_absent(self) -> None:
        """No claim is not a settled claim.

        Ending a receipt nobody ever claimed would leave it hand-claimable
        beside its successor, because the ledger row that permanently blocks a
        second claim on it would not exist.
        """

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository = self._granted(base)
            receipt_ref = self._admitted(layout, repository)

            result = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(result.failure, ReceiptRevocationFailure.ASSIGNMENT_ABSENT)
            boundary = WakeScopedDispatchBoundary(layout.queue_root / "metadata")
            admitted = admit_dispatch(layout, _request(repository))
            assert admitted.receipt is not None
            verification, _ = verify_receipt_claimable(boundary, admitted.receipt)
            self.assertIs(verification, ReceiptVerificationStatus.CLAIMABLE)

    def test_an_unreadable_ledger_never_reads_as_a_settled_claim(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, receipt_ref = self._compensated(base)
            ledger_path(layout).write_text("{not json at all", encoding="utf-8")
            before = self._metadata_bytes(layout)

            result = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(
                result.failure,
                ReceiptRevocationFailure.ASSIGNMENT_LEDGER_UNAVAILABLE,
            )
            self.assertIsNot(
                result.failure,
                ReceiptRevocationFailure.ASSIGNMENT_ABSENT,
                "an unreadable ledger must never look like an absent claim",
            )
            self.assertEqual(before, self._metadata_bytes(layout))

    def test_a_successor_equal_to_the_receipt_refuses_before_anything_closes(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, receipt_ref = self._compensated(base)
            before = self._metadata_bytes(layout)

            result = revoke_dispatch_receipt(
                layout, self._revocation(receipt_ref, replacement=receipt_ref)
            )

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(
                result.failure, ReceiptRevocationFailure.REPLACEMENT_NOT_DISTINCT
            )
            self.assertEqual(before, self._metadata_bytes(layout))

    def test_revocation_without_a_grant_refuses_and_writes_no_store_effect(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, receipt_ref = self._compensated(base)
            grant_file = layout.base / "dispatch-authority.json"
            grant_file.unlink()
            before = self._metadata_bytes(layout)

            result = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(
                result.failure,
                ReceiptRevocationFailure.DISPATCH_AUTHORITY_ABSENT,
            )
            self.assertEqual(before, self._metadata_bytes(layout))
            self.assertEqual(
                "REVOCATION_DISPATCH_AUTHORITY_ABSENT",
                self._last_line(layout)["outcome"],
            )

    def test_a_refusal_is_journaled_even_when_the_journal_does_not_exist_yet(
        self,
    ) -> None:
        """The empty-journal case: a refusal still leaves a named line."""

        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            self.assertFalse(journal_path(layout).exists())

            result = revoke_dispatch_receipt(
                layout, self._revocation("receipt-vita-feature-001")
            )

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            lines = journal_path(layout).read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(lines))
            self.assertEqual(
                "REVOCATION_DISPATCH_AUTHORITY_ABSENT",
                json.loads(lines[0])["outcome"],
            )

    def test_a_receipt_the_store_does_not_hold_is_named_apart_from_a_mismatch(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository = self._granted(base)
            # A settled ledger row for a receipt the metadata store never held.
            self._compensate(
                layout,
                self._claim(layout, repository, "receipt-vita-feature-777"),
                "receipt-vita-feature-777",
            )

            result = revoke_dispatch_receipt(
                layout, self._revocation("receipt-vita-feature-777")
            )

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(result.failure, ReceiptRevocationFailure.RECEIPT_NOT_FOUND)

    def test_a_stale_receipt_reference_is_refused_as_a_mismatch(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, repository = self._granted(base)
            self._admitted(layout, repository)
            self._compensate(
                layout,
                self._claim(layout, repository, "receipt-vita-feature-777"),
                "receipt-vita-feature-777",
            )

            result = revoke_dispatch_receipt(
                layout, self._revocation("receipt-vita-feature-777")
            )

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(result.failure, ReceiptRevocationFailure.RECEIPT_MISMATCH)

    def test_revoking_an_already_revoked_receipt_converges(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, receipt_ref = self._compensated(base)
            first = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))
            self.assertIs(first.status, ReceiptRevocationStatus.REVOKED)

            second = revoke_dispatch_receipt(layout, self._revocation(receipt_ref))

            self.assertIs(second.status, ReceiptRevocationStatus.ALREADY_REVOKED)
            self.assertEqual(first.receipt, second.receipt)
            self.assertEqual(
                "REVOCATION_ALREADY_REVOKED", self._last_line(layout)["outcome"]
            )

    def test_a_foreign_request_is_refused_as_invalid(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout, _, _ = self._compensated(base)

            result = revoke_dispatch_receipt(layout, object())  # type: ignore[arg-type]

            self.assertIs(result.status, ReceiptRevocationStatus.REFUSED)
            self.assertIs(result.failure, ReceiptRevocationFailure.REQUEST_INVALID)

    def test_every_revocation_refusal_carries_its_own_name(self) -> None:
        """Seven induced refusals, seven different codes: the anti-folding pin."""

        codes: list[ReceiptRevocationFailure] = []
        for induce in (
            "no-grant",
            "foreign-request",
            "successor-not-distinct",
            "ledger-unreadable",
            "claim-open",
            "claim-absent",
            "receipt-absent",
        ):
            with self.subTest(induce=induce):
                with TemporaryDirectory() as temporary:
                    base = Path(temporary)
                    layout, repository = self._granted(base)
                    receipt_ref = self._admitted(layout, repository)
                    request = self._revocation(receipt_ref)
                    if induce == "no-grant":
                        (layout.base / "dispatch-authority.json").unlink()
                    elif induce == "successor-not-distinct":
                        request = self._revocation(receipt_ref, replacement=receipt_ref)
                    elif induce == "ledger-unreadable":
                        ledger_path(layout).write_text("{broken", encoding="utf-8")
                    elif induce == "claim-open":
                        self._claim(layout, repository, receipt_ref)
                    elif induce == "receipt-absent":
                        request = self._revocation("receipt-vita-feature-777")
                        self._compensate(
                            layout,
                            self._claim(
                                layout, repository, "receipt-vita-feature-777"
                            ),
                            "receipt-vita-feature-777",
                        )
                    if induce == "foreign-request":
                        result = revoke_dispatch_receipt(layout, object())  # type: ignore[arg-type]
                    else:
                        result = revoke_dispatch_receipt(layout, request)
                    self.assertIs(
                        result.status, ReceiptRevocationStatus.REFUSED, msg=induce
                    )
                    assert result.failure is not None
                    codes.append(result.failure)
        self.assertEqual(len(set(codes)), len(codes), msg=f"{codes}")


class RevocationCapabilityTests(unittest.TestCase):
    """P5-R3: the authority may read who holds a ticket and may never change it.

    Taking the compensation proof here rather than accepting one from the
    caller is what makes it unforgeable, and it costs a new dependency on the
    bookkeeping module. The dependency is bounded by identity, not by
    docstring: the read entry is the bookkeeping module's own, and no entry
    that could claim or settle anything is reachable from this namespace.
    """

    def test_the_read_entry_is_the_bookkeeping_module_own(self) -> None:
        self.assertIs(
            dispatch_authority.read_worker_assignments,
            worker_assignment.read_worker_assignments,
        )

    def test_no_name_here_can_write_the_assignment_ledger(self) -> None:
        forbidden = {
            id(worker_assignment.claim_worker_assignment),
            id(worker_assignment.settle_worker_assignment),
        }
        for name in dir(dispatch_authority):
            with self.subTest(name=name):
                self.assertNotIn(
                    id(getattr(dispatch_authority, name)),
                    forbidden,
                    "the issuance authority must not be able to move a claim",
                )

    def test_the_full_metadata_boundary_is_not_part_of_this_surface(self) -> None:
        """Revocation holds one method, exactly as issuance holds three."""

        for name in (
            "LiveDispatchMetadataBoundary",
            "JohnnyMetadataRoot",
            "claim_worker_assignment",
            "settle_worker_assignment",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(dispatch_authority, name))
        scoped = dispatch_authority._RevocationScopedDispatchBoundary
        exposed = {
            name for name in vars(scoped) if not name.startswith("_")
        }
        self.assertEqual({"revoke_receipt"}, exposed)


class FixtureFreeChainTests(unittest.TestCase):
    """W1-R4: admission feeds the E9 builder with no test fixture anywhere."""

    def test_an_admitted_receipt_composes_a_subscription(self) -> None:
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            layout = _layout(base)
            create_dispatch_grant(layout)
            repository = _repository(base)
            subprocess.run(
                ("git", "-C", str(repository), "init", "--quiet"),
                check=True,
                capture_output=True,
            )
            wake_config_path(layout).parent.mkdir(parents=True, exist_ok=True)
            wake_config_path(layout).write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "command": [
                            sys.executable,
                            "-c",
                            "import sys; sys.exit(0)",
                            "{payload_file}",
                        ],
                        "reviewer_ref": "role-supervisor-reviewer",
                        "timeout_seconds": 30,
                    }
                ),
                encoding="utf-8",
            )
            admitted = admit_dispatch(layout, _request(repository))
            self.assertIs(admitted.status, DispatchAdmissionStatus.DISPATCHED)
            assert admitted.receipt is not None

            status, failure = build_subscription(
                layout,
                admitted.receipt,
                SubscriptionInputs(
                    repository_root=str(repository),
                    event_source_ref="event-source-w1-001",
                    subscription_id="subscription-w1-001",
                    exact_git_ref="refs/heads/main",
                    reserved_handoff_ref="doc/handoffs/w1/handoff-w1-001.json",
                    spec_ref="spec-w1",
                    spec_revision="rev-1111111111111111",
                    source_role_ref="role-implementation-owner",
                    reviewer_ref="role-supervisor-reviewer",
                    reviewer_task_ref="task-w1-reviewer",
                    reviewer_task_id="3f2b1c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d",
                    reviewer_host_id="local",
                    lease_id="lease-w1-001",
                    supervision_class=SupervisionClass.LUNA_XHIGH_DEFAULT,
                ),
            )
            self.assertIs(status, SubscriptionBuildStatus.WRITTEN, f"{failure}")


class RunnerIsolationTests(unittest.TestCase):
    """W1-R5: the issuance surface never enters the runner composition.

    Supplementary namespace pins; the discriminating cell remains the
    runtime-binding-identity test in the review-correction regressions.
    """

    def test_the_runner_module_holds_no_issuance_name(self) -> None:
        for forbidden in (
            "IssuanceScopedDispatchBoundary",
            "admit_dispatch",
            "create_dispatch_grant",
            "issue_receipt",
            "register_artifact",
        ):
            with self.subTest(name=forbidden):
                self.assertFalse(hasattr(event_runner, forbidden))

    def test_the_runner_source_never_imports_the_dispatch_modules(self) -> None:
        source = Path(event_runner.__file__).read_text(encoding="utf-8")
        for forbidden in ("dispatch_authority", "issuance_scoped_boundary"):
            with self.subTest(module=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
