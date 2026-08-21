"""Durability and fail-closed tests for live-dispatch metadata."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from library.local_orchestration import (
    ApprovedDispatchArtifactReadRequest,
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    ArtifactReadStatus,
    ArtifactRegistrationStatus,
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    LiveDispatchMetadataStore,
    ReceiptIssueStatus,
    ReceiptLifecycle,
    ReceiptReadStatus,
    TicketReceiptIssueRequest,
    TicketReceiptIssueResult,
    TicketReceiptReadRequest,
)
from library.local_orchestration.live_dispatch_metadata_boundary import (
    ReceiptRevokeFailure,
    ReceiptRevokeStatus,
    TicketReceiptRevokeRequest,
)


_ROOT = Path(__file__).resolve().parents[1]
_DIGEST = "sha256_" + ("a" * 64)
_CHECKPOINT_NAME = "live-dispatch-metadata-v1.json"
_TEMP_GLOB = ".live-dispatch-metadata-v1-*.tmp"


def _artifact(
    ticket_reference: str = "ticket-live-dispatch-r03-01",
    handoff_reference: str = "handoff-live-dispatch-r03-01",
    descriptor_binding: str = "descriptor-live-dispatch-r03-01",
) -> ApprovedDispatchArtifactRecord:
    return ApprovedDispatchArtifactRecord(
        project_id="prj_0123456789abcdef",
        ticket_reference=ticket_reference,
        ticket_revision="rev-0123456789abcdef",
        ticket_digest=_DIGEST,
        ticket_document_commit="0123456789abcdef",
        handoff_reference=handoff_reference,
        handoff_revision="rev-fedcba9876543210",
        handoff_digest=_DIGEST,
        handoff_document_commit="fedcba9876543210",
        baseline_commit="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        implementation_owner_id="role-implementation-owner-1",
        expected_return="return-implementation-completed",
        descriptor_binding=descriptor_binding,
    )


def _issue_request(
    record: ApprovedDispatchArtifactRecord,
    receipt_id: str = "receipt-live-dispatch-r03-01",
) -> TicketReceiptIssueRequest:
    return TicketReceiptIssueRequest(
        artifact_identity=record.identity,
        ticket_revision=record.ticket_revision,
        ticket_digest=record.ticket_digest,
        ticket_document_commit=record.ticket_document_commit,
        handoff_revision=record.handoff_revision,
        handoff_digest=record.handoff_digest,
        handoff_document_commit=record.handoff_document_commit,
        baseline_commit=record.baseline_commit,
        receipt_id=receipt_id,
        expected_return=record.expected_return,
        descriptor_binding=record.descriptor_binding,
        correlation_id="corr-live-dispatch-r03-01",
        dispatch_question_id="question-live-dispatch-r03-01",
        worktree_fingerprint="worktree-implementation-01",
        branch_fingerprint="branch-livedispatch-01",
    )


def _store(root: Path) -> LiveDispatchMetadataStore:
    metadata_root = JohnnyMetadataRoot(root.resolve(strict=True))
    return LiveDispatchMetadataStore(LiveDispatchMetadataBoundary(metadata_root))


def _run_child(script: str, root: Path, *payloads: str) -> tuple[str, ...]:
    completed = subprocess.run(
        (sys.executable, "-B", "-c", script, str(root), *payloads),
        cwd=_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return tuple(line for line in completed.stdout.splitlines() if line)


_WRITE_SCRIPT = """
from pathlib import Path
import sys
from library.local_orchestration import (
    ApprovedDispatchArtifactRegisterRequest,
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    LiveDispatchMetadataStore,
    TicketReceiptIssueRequest,
)
store = LiveDispatchMetadataStore(
    LiveDispatchMetadataBoundary(JohnnyMetadataRoot(Path(sys.argv[1]).resolve(strict=True)))
)
registration = store.register_artifact(
    ApprovedDispatchArtifactRegisterRequest.model_validate_json(sys.argv[2], strict=True)
)
issuance = store.issue_receipt(
    TicketReceiptIssueRequest.model_validate_json(sys.argv[3], strict=True)
)
print(registration.model_dump_json())
print(issuance.model_dump_json())
"""


_READ_SCRIPT = """
from pathlib import Path
import sys
from library.local_orchestration import (
    ApprovedDispatchArtifactReadRequest,
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    LiveDispatchMetadataStore,
    TicketReceiptReadRequest,
)
store = LiveDispatchMetadataStore(
    LiveDispatchMetadataBoundary(JohnnyMetadataRoot(Path(sys.argv[1]).resolve(strict=True)))
)
artifact = store.read_artifact(
    ApprovedDispatchArtifactReadRequest.model_validate_json(sys.argv[2], strict=True)
)
receipt = store.read_receipt(
    TicketReceiptReadRequest.model_validate_json(sys.argv[3], strict=True)
)
print(artifact.model_dump_json())
print(receipt.model_dump_json())
"""


_RACE_SCRIPT = """
from pathlib import Path
import sys
from library.local_orchestration import (
    JohnnyMetadataRoot,
    LiveDispatchMetadataBoundary,
    LiveDispatchMetadataStore,
    TicketReceiptIssueRequest,
)
store = LiveDispatchMetadataStore(
    LiveDispatchMetadataBoundary(JohnnyMetadataRoot(Path(sys.argv[1]).resolve(strict=True)))
)
request = TicketReceiptIssueRequest.model_validate_json(sys.argv[2], strict=True)
sys.stdin.read(1)
print(store.issue_receipt(request).model_dump_json())
"""


class DurableLiveDispatchBoundaryTests(unittest.TestCase):
    def test_state_survives_process_exit_and_identical_restarts_are_byte_idempotent(self) -> None:
        record = _artifact()
        register_request = ApprovedDispatchArtifactRegisterRequest(artifact=record)
        issue_request = _issue_request(record)
        artifact_read = ApprovedDispatchArtifactReadRequest(
            identity=record.identity,
            ticket_revision=record.ticket_revision,
            handoff_revision=record.handoff_revision,
        )
        receipt_read = TicketReceiptReadRequest(
            project_id=record.project_id,
            ticket_reference=record.ticket_reference,
            ticket_revision=record.ticket_revision,
        )

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            write_lines = _run_child(
                _WRITE_SCRIPT,
                root,
                register_request.model_dump_json(),
                issue_request.model_dump_json(),
            )
            self.assertEqual(2, len(write_lines))
            self.assertIn('"status":"REGISTERED"', write_lines[0])
            issued = TicketReceiptIssueResult.model_validate_json(write_lines[1], strict=True)
            self.assertEqual(ReceiptIssueStatus.ISSUED, issued.status)

            checkpoint_path = root / _CHECKPOINT_NAME
            first_checkpoint = checkpoint_path.read_bytes()
            restarted = _store(root)
            repeated_registration = restarted.register_artifact(register_request)
            repeated_issuance = restarted.issue_receipt(issue_request)
            self.assertEqual(
                ArtifactRegistrationStatus.ALREADY_REGISTERED,
                repeated_registration.status,
            )
            self.assertEqual(ReceiptIssueStatus.ALREADY_ISSUED, repeated_issuance.status)
            self.assertEqual(issued.receipt, repeated_issuance.receipt)
            self.assertEqual(first_checkpoint, checkpoint_path.read_bytes())

            read_lines = _run_child(
                _READ_SCRIPT,
                root,
                artifact_read.model_dump_json(),
                receipt_read.model_dump_json(),
            )
            self.assertEqual(2, len(read_lines))
            self.assertIn('"status":"FOUND"', read_lines[0])
            self.assertIn('"status":"FOUND"', read_lines[1])
            self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))

            serialized = checkpoint_path.read_bytes()
            self.assertNotIn(str(root).encode("utf-8"), serialized)
            for forbidden_value in (
                b"C:\\repository\\raw-source",
                b"user prompt contents",
                b"shared Context contents",
                b"secret-token-value",
                b"person@example.invalid",
            ):
                self.assertNotIn(forbidden_value, serialized)

    def test_two_processes_create_one_canonical_receipt(self) -> None:
        record = _artifact()
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            store = _store(root)
            registered = store.register_artifact(
                ApprovedDispatchArtifactRegisterRequest(artifact=record)
            )
            self.assertEqual(ArtifactRegistrationStatus.REGISTERED, registered.status)

            commands = tuple(
                (
                    sys.executable,
                    "-B",
                    "-c",
                    _RACE_SCRIPT,
                    str(root),
                    _issue_request(record, receipt_id).model_dump_json(),
                )
                for receipt_id in ("receipt-race-first", "receipt-race-second")
            )
            processes = tuple(
                subprocess.Popen(
                    command,
                    cwd=_ROOT,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for command in commands
            )
            for process in processes:
                if process.stdin is None:
                    self.fail("race child has no standard input")
                process.stdin.write("1")
                process.stdin.flush()

            results: list[TicketReceiptIssueResult] = []
            for process in processes:
                process.wait(timeout=20)
                if process.stdout is None or process.stderr is None:
                    self.fail("race child pipes are unavailable")
                output = process.stdout.read().strip()
                error = process.stderr.read().strip()
                if process.stdin is not None:
                    process.stdin.close()
                process.stdout.close()
                process.stderr.close()
                if process.returncode != 0:
                    self.fail(error)
                results.append(TicketReceiptIssueResult.model_validate_json(output, strict=True))

            self.assertEqual(
                {ReceiptIssueStatus.ISSUED, ReceiptIssueStatus.RECEIPT_CONFLICT},
                {result.status for result in results},
            )
            final = store.read_receipt(
                TicketReceiptReadRequest(
                    project_id=record.project_id,
                    ticket_reference=record.ticket_reference,
                    ticket_revision=record.ticket_revision,
                )
            )
            self.assertEqual(ReceiptReadStatus.FOUND, final.status)
            self.assertIsNotNone(final.receipt)
            if final.receipt is None:
                self.fail("canonical receipt is missing")
            self.assertIn(
                final.receipt.receipt_id,
                ("receipt-race-first", "receipt-race-second"),
            )
            checkpoint = (root / _CHECKPOINT_NAME).read_text(encoding="utf-8")
            self.assertEqual(1, checkpoint.count('"lifecycle":"ACTIVE"'))
            self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))

    def test_interrupted_atomic_replace_preserves_previous_checkpoint(self) -> None:
        record = _artifact()
        second = _artifact(
            ticket_reference="ticket-live-dispatch-r03-02",
            handoff_reference="handoff-live-dispatch-r03-02",
            descriptor_binding="descriptor-live-dispatch-r03-02",
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            store = _store(root)
            store.register_artifact(ApprovedDispatchArtifactRegisterRequest(artifact=record))
            store.issue_receipt(_issue_request(record))
            checkpoint_path = root / _CHECKPOINT_NAME
            before = checkpoint_path.read_bytes()

            with patch(
                "library.local_orchestration.live_dispatch_metadata_boundary.os.replace",
                side_effect=OSError("injected atomic replace interruption"),
            ):
                interrupted = store.register_artifact(
                    ApprovedDispatchArtifactRegisterRequest(artifact=second)
                )

            self.assertEqual(
                ArtifactRegistrationStatus.STORAGE_UNAVAILABLE,
                interrupted.status,
            )
            self.assertEqual(before, checkpoint_path.read_bytes())
            self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))
            prior = _store(root).read_receipt(
                TicketReceiptReadRequest(
                    project_id=record.project_id,
                    ticket_reference=record.ticket_reference,
                    ticket_revision=record.ticket_revision,
                )
            )
            self.assertEqual(ReceiptReadStatus.FOUND, prior.status)

    def test_invalid_checkpoints_fail_closed_without_repair_or_replacement(self) -> None:
        record = _artifact()
        register_request = ApprovedDispatchArtifactRegisterRequest(artifact=record)
        artifact_read = ApprovedDispatchArtifactReadRequest(
            identity=record.identity,
            ticket_revision=record.ticket_revision,
            handoff_revision=record.handoff_revision,
        )
        receipt_read = TicketReceiptReadRequest(
            project_id=record.project_id,
            ticket_reference=record.ticket_reference,
            ticket_revision=record.ticket_revision,
        )
        corrupted_payloads = (
            ("truncated", b'{"schema_revision":'),
            ("invalid-shape", b"[]"),
            (
                "unknown-revision",
                b'{"schema_revision":"live-dispatch-metadata-v2",'
                b'"generation":0,"artifacts":[],"receipts":[]}',
            ),
            (
                "coerced-generation",
                b'{"schema_revision":"live-dispatch-metadata-v1",'
                b'"generation":"1","artifacts":[],"receipts":[]}',
            ),
        )

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            checkpoint_path = root / _CHECKPOINT_NAME
            for label, payload in corrupted_payloads:
                with self.subTest(label=label):
                    checkpoint_path.write_bytes(payload)
                    store = _store(root)
                    self.assertEqual(
                        ArtifactReadStatus.STORAGE_UNAVAILABLE,
                        store.read_artifact(artifact_read).status,
                    )
                    self.assertEqual(payload, checkpoint_path.read_bytes())
                    self.assertEqual(
                        ReceiptReadStatus.STORAGE_UNAVAILABLE,
                        store.read_receipt(receipt_read).status,
                    )
                    self.assertEqual(payload, checkpoint_path.read_bytes())
                    self.assertEqual(
                        ArtifactRegistrationStatus.STORAGE_UNAVAILABLE,
                        store.register_artifact(register_request).status,
                    )
                    self.assertEqual(payload, checkpoint_path.read_bytes())
                    self.assertEqual(
                        ReceiptIssueStatus.STORAGE_UNAVAILABLE,
                        store.issue_receipt(_issue_request(record)).status,
                    )
                    self.assertEqual(payload, checkpoint_path.read_bytes())
                    self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))


class ReceiptRevocationBoundaryTests(unittest.TestCase):
    """P5-R1: the terminal lifecycles finally have a writer, and only one.

    Every reader in the tree already knew what `REVOKED` meant. Nothing could
    produce it, so a receipt outlived its own dead dispatch and kept the
    (project, ticket) key for good. These cells pin the CAS half of ending
    one: what it frees, what it refuses, and what it writes when it refuses,
    which is nothing.
    """

    def _seed(self, root: Path) -> ApprovedDispatchArtifactRecord:
        record = _artifact()
        store = _store(root)
        store.register_artifact(
            ApprovedDispatchArtifactRegisterRequest(artifact=record)
        )
        issued = store.issue_receipt(_issue_request(record))
        self.assertEqual(ReceiptIssueStatus.ISSUED, issued.status)
        return record

    def _revoke_request(
        self,
        record: ApprovedDispatchArtifactRecord,
        receipt_id: str = "receipt-live-dispatch-r03-01",
    ) -> TicketReceiptRevokeRequest:
        return TicketReceiptRevokeRequest(
            project_id=record.project_id,
            ticket_reference=record.ticket_reference,
            receipt_id=receipt_id,
        )

    def _read_request(
        self, record: ApprovedDispatchArtifactRecord
    ) -> TicketReceiptReadRequest:
        return TicketReceiptReadRequest(
            project_id=record.project_id,
            ticket_reference=record.ticket_reference,
            ticket_revision=record.ticket_revision,
        )

    def test_a_revoked_receipt_frees_the_key_for_a_successor(self) -> None:
        """The whole point: the key is released, and a successor may be issued."""

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))

            revoked = boundary.revoke_receipt(self._revoke_request(record))

            self.assertEqual(ReceiptRevokeStatus.REVOKED, revoked.status)
            self.assertIsNotNone(revoked.receipt)
            if revoked.receipt is None:
                self.fail("a revocation must carry the receipt it ended")
            self.assertIs(revoked.receipt.lifecycle, ReceiptLifecycle.REVOKED)
            self.assertEqual(
                "receipt-live-dispatch-r03-01", revoked.receipt.receipt_id
            )

            store = _store(root)
            self.assertEqual(
                ReceiptReadStatus.CLOSED,
                store.read_receipt(self._read_request(record)).status,
            )

            successor = store.issue_receipt(
                _issue_request(record, "receipt-live-dispatch-r03-02")
            )
            self.assertEqual(ReceiptIssueStatus.ISSUED, successor.status)
            reread = store.read_receipt(self._read_request(record))
            self.assertEqual(ReceiptReadStatus.FOUND, reread.status)
            if reread.receipt is None:
                self.fail("the successor must be the canonical receipt")
            self.assertEqual("receipt-live-dispatch-r03-02", reread.receipt.receipt_id)
            checkpoint = (root / _CHECKPOINT_NAME).read_text(encoding="utf-8")
            self.assertEqual(1, checkpoint.count('"lifecycle":"ACTIVE"'))
            self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))

    def test_a_live_receipt_still_holds_the_key_against_every_successor(self) -> None:
        """The property being preserved, not the one being added."""

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)

            conflicting = _store(root).issue_receipt(
                _issue_request(record, "receipt-live-dispatch-r03-02")
            )

            self.assertEqual(ReceiptIssueStatus.RECEIPT_CONFLICT, conflicting.status)

    def test_a_revoked_receipt_id_is_spent_and_cannot_be_reissued(self) -> None:
        """Otherwise a replay of the original request would undo the revocation."""

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            boundary.revoke_receipt(self._revoke_request(record))

            replayed = _store(root).issue_receipt(_issue_request(record))

            self.assertEqual(ReceiptIssueStatus.RECEIPT_CONFLICT, replayed.status)
            self.assertEqual(
                ReceiptReadStatus.CLOSED,
                _store(root).read_receipt(self._read_request(record)).status,
            )

    def test_revoking_twice_converges_and_writes_nothing_the_second_time(self) -> None:
        """Convergence is what makes an interrupted redispatch resumable."""

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            first = boundary.revoke_receipt(self._revoke_request(record))
            self.assertEqual(ReceiptRevokeStatus.REVOKED, first.status)
            after_first = (root / _CHECKPOINT_NAME).read_bytes()

            second = boundary.revoke_receipt(self._revoke_request(record))

            self.assertEqual(ReceiptRevokeStatus.ALREADY_REVOKED, second.status)
            self.assertEqual(first.receipt, second.receipt)
            self.assertEqual(after_first, (root / _CHECKPOINT_NAME).read_bytes())

    def test_revoking_by_the_wrong_receipt_id_refuses_and_the_receipt_stands(
        self,
    ) -> None:
        """A stale request must never end whichever receipt holds the key now."""

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            before = (root / _CHECKPOINT_NAME).read_bytes()

            refused = boundary.revoke_receipt(
                self._revoke_request(record, "receipt-live-dispatch-r03-09")
            )

            self.assertEqual(ReceiptRevokeStatus.RECEIPT_MISMATCH, refused.status)
            self.assertIs(refused.failure, ReceiptRevokeFailure.RECEIPT_MISMATCH)
            self.assertIsNone(refused.receipt)
            self.assertEqual(before, (root / _CHECKPOINT_NAME).read_bytes())
            self.assertEqual(
                ReceiptReadStatus.FOUND,
                _store(root).read_receipt(self._read_request(record)).status,
            )

    def test_revoking_a_ticket_that_holds_no_receipt_is_named_not_found(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = _artifact()
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))

            refused = boundary.revoke_receipt(self._revoke_request(record))

            self.assertEqual(ReceiptRevokeStatus.NOT_FOUND, refused.status)
            self.assertIs(refused.failure, ReceiptRevokeFailure.NOT_FOUND)
            self.assertIsNot(
                refused.failure,
                ReceiptRevokeFailure.RECEIPT_MISMATCH,
                "no receipt at all and the wrong receipt are different facts",
            )

    def test_a_foreign_request_is_refused_without_touching_the_store(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            before = (root / _CHECKPOINT_NAME).read_bytes()

            refused = boundary.revoke_receipt(object())  # type: ignore[arg-type]

            self.assertEqual(ReceiptRevokeStatus.STORAGE_UNAVAILABLE, refused.status)
            self.assertEqual(before, (root / _CHECKPOINT_NAME).read_bytes())
            self.assertEqual(
                ReceiptReadStatus.FOUND,
                _store(root).read_receipt(self._read_request(record)).status,
            )

    def test_an_interrupted_revocation_preserves_the_previous_checkpoint(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            before = (root / _CHECKPOINT_NAME).read_bytes()

            with patch(
                "library.local_orchestration.live_dispatch_metadata_boundary.os.replace",
                side_effect=OSError("injected atomic replace interruption"),
            ):
                interrupted = boundary.revoke_receipt(self._revoke_request(record))

            self.assertEqual(
                ReceiptRevokeStatus.STORAGE_UNAVAILABLE, interrupted.status
            )
            self.assertEqual(before, (root / _CHECKPOINT_NAME).read_bytes())
            self.assertEqual((), tuple(root.glob(_TEMP_GLOB)))
            self.assertEqual(
                ReceiptReadStatus.FOUND,
                _store(root).read_receipt(self._read_request(record)).status,
            )

    def test_an_unreadable_checkpoint_refuses_the_revocation_without_repair(
        self,
    ) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = _artifact()
            payload = b'{"schema_revision":'
            (root / _CHECKPOINT_NAME).write_bytes(payload)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))

            refused = boundary.revoke_receipt(self._revoke_request(record))

            self.assertEqual(ReceiptRevokeStatus.STORAGE_UNAVAILABLE, refused.status)
            self.assertIsNot(
                refused.failure,
                ReceiptRevokeFailure.NOT_FOUND,
                "an unreadable checkpoint must never look like an absent receipt",
            )
            self.assertEqual(payload, (root / _CHECKPOINT_NAME).read_bytes())

    def test_the_persisted_schema_revision_is_unchanged_by_the_new_route(self) -> None:
        """No field was added and no shape changed, so the revision holds.

        `REVOKED` was already a representable lifecycle in this schema; what
        was missing was a writer, not a place to write. A checkpoint carrying
        a revoked receipt is a valid v1 checkpoint and an older build reads it
        without misreading anything — it simply refuses the successor that
        this build admits, which is the stricter direction and safe. So the
        revision stays where it is, pinned here so that a future change which
        *does* alter the shape has to move it deliberately.
        """

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            record = self._seed(root)
            boundary = LiveDispatchMetadataBoundary(JohnnyMetadataRoot(root))
            boundary.revoke_receipt(self._revoke_request(record))

            stored = json.loads(
                (root / _CHECKPOINT_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual("live-dispatch-metadata-v1", stored["schema_revision"])
            self.assertEqual(
                ["REVOKED"], [item["lifecycle"] for item in stored["receipts"]]
            )
            reopened = _store(root)
            self.assertEqual(
                ReceiptReadStatus.CLOSED,
                reopened.read_receipt(self._read_request(record)).status,
            )


class DurableLiveDispatchSourceGateTests(unittest.TestCase):
    def test_boundary_is_strict_and_has_no_unrelated_runtime_capabilities(self) -> None:
        source_path = (
            _ROOT
            / "library"
            / "local_orchestration"
            / "live_dispatch_metadata_boundary.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_tokens = (
            "Any",
            "object",
            "cast(",
            "model_construct",
            "model_copy(",
            "type: ignore",
            "getattr(",
            "except Exception",
        )
        self.assertFalse(any(token in source for token in forbidden_tokens))
        imported_roots = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_roots.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        self.assertTrue(
            imported_roots.isdisjoint(
                {"requests", "socket", "sqlite3", "subprocess", "threading", "time"}
            )
        )

    def test_metadata_root_requires_existing_absolute_resolved_directory(self) -> None:
        with self.assertRaises(ValueError):
            JohnnyMetadataRoot(Path("relative-metadata-root"))
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory).resolve(strict=True)
            self.assertEqual(root, JohnnyMetadataRoot(root).root)


if __name__ == "__main__":
    unittest.main()
