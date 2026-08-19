"""W1: receipt issuance is a granted, gated, journaled workstation entry."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration import event_runner
from library.local_orchestration.dispatch_authority import (
    DispatchAdmissionFailure,
    DispatchAdmissionRequest,
    DispatchAdmissionStatus,
    DispatchGrantStatus,
    admit_dispatch,
    create_dispatch_grant,
    journal_path,
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
