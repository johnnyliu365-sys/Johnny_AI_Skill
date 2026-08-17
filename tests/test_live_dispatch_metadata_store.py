"""Acceptance tests for the durable live-dispatch metadata boundary."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest

from pydantic import ValidationError

from library.local_orchestration import (
    ApprovedArtifactLifecycle,
    ApprovedDispatchArtifactIdentity,
    ApprovedDispatchArtifactReadRequest,
    ApprovedDispatchArtifactReadResult,
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    ApprovedDispatchArtifactRegisterResult,
    ArtifactReadFailure,
    ArtifactReadStatus,
    ArtifactRegistrationFailure,
    ArtifactRegistrationStatus,
    LiveDispatchMetadataStore,
    ReceiptIssueFailure,
    ReceiptIssueStatus,
    ReceiptLifecycle,
    ReceiptReadFailure,
    ReceiptReadStatus,
    TicketReceipt,
    TicketReceiptIssueRequest,
    TicketReceiptIssueResult,
    TicketReceiptReadRequest,
    TicketReceiptReadResult,
    to_legacy_ticket_dispatch_receipt,
)
from library.workflow_router import TicketDispatchReceipt


_ROOT = Path(__file__).resolve().parents[1]
_DIGEST = "sha256_" + ("a" * 64)


def _artifact() -> ApprovedDispatchArtifactRecord:
    return ApprovedDispatchArtifactRecord(
        project_id="prj_0123456789abcdef",
        ticket_reference="ticket-live-dispatch-r03-01",
        ticket_revision="rev-0123456789abcdef",
        ticket_digest=_DIGEST,
        ticket_document_commit="0123456789abcdef",
        handoff_reference="handoff-live-dispatch-r03-01",
        handoff_revision="rev-fedcba9876543210",
        handoff_digest=_DIGEST,
        handoff_document_commit="fedcba9876543210",
        baseline_commit="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        implementation_owner_id="role-implementation-owner-1",
        expected_return="return-implementation-completed",
        descriptor_binding="descriptor-live-dispatch-r03-01",
    )


def _issue_request(record: ApprovedDispatchArtifactRecord) -> TicketReceiptIssueRequest:
    return TicketReceiptIssueRequest(
        artifact_identity=record.identity,
        ticket_revision=record.ticket_revision,
        ticket_digest=record.ticket_digest,
        ticket_document_commit=record.ticket_document_commit,
        handoff_revision=record.handoff_revision,
        handoff_digest=record.handoff_digest,
        handoff_document_commit=record.handoff_document_commit,
        baseline_commit=record.baseline_commit,
        receipt_id="receipt-live-dispatch-r03-01",
        expected_return=record.expected_return,
        descriptor_binding=record.descriptor_binding,
        correlation_id="corr-live-dispatch-r03-01",
        dispatch_question_id="question-live-dispatch-r03-01",
        worktree_fingerprint="worktree-implementation-01",
        branch_fingerprint="branch-livedispatch-01",
    )


class _Boundary:
    """A test-only journal/checkpoint adapter with atomic in-memory behavior."""

    def __init__(self) -> None:
        self.artifacts: dict[tuple[str, str, str, str], ApprovedDispatchArtifactRecord] = {}
        self.receipts: dict[tuple[str, str], TicketReceipt] = {}
        self.unavailable = False
        self.register_calls = 0
        self.read_artifact_calls = 0
        self.issue_calls = 0
        self.read_receipt_calls = 0

    def register_artifact(
        self,
        request: ApprovedDispatchArtifactRegisterRequest,
    ) -> ApprovedDispatchArtifactRegisterResult:
        self.register_calls += 1
        if self.unavailable:
            return ApprovedDispatchArtifactRegisterResult(
                status=ArtifactRegistrationStatus.STORAGE_UNAVAILABLE,
                failure=ArtifactRegistrationFailure.STORAGE_UNAVAILABLE,
            )
        record = request.artifact
        key = (
            record.project_id,
            record.ticket_reference,
            record.handoff_reference,
            record.implementation_owner_id,
        )
        existing = self.artifacts.get(key)
        if existing is None:
            self.artifacts[key] = record
            return ApprovedDispatchArtifactRegisterResult(
                status=ArtifactRegistrationStatus.REGISTERED,
                record=record,
            )
        if existing == record:
            return ApprovedDispatchArtifactRegisterResult(
                status=ArtifactRegistrationStatus.ALREADY_REGISTERED,
                record=existing,
            )
        return ApprovedDispatchArtifactRegisterResult(
            status=ArtifactRegistrationStatus.IDENTITY_CONFLICT,
            failure=ArtifactRegistrationFailure.IDENTITY_CONFLICT,
        )

    def read_artifact(
        self,
        request: ApprovedDispatchArtifactReadRequest,
    ) -> ApprovedDispatchArtifactReadResult:
        self.read_artifact_calls += 1
        if self.unavailable:
            return ApprovedDispatchArtifactReadResult(
                status=ArtifactReadStatus.STORAGE_UNAVAILABLE,
                failure=ArtifactReadFailure.STORAGE_UNAVAILABLE,
            )
        identity = request.identity
        key = (
            identity.project_id,
            identity.ticket_reference,
            identity.handoff_reference,
            identity.implementation_owner_id,
        )
        record = self.artifacts.get(key)
        if record is None:
            return ApprovedDispatchArtifactReadResult(
                status=ArtifactReadStatus.NOT_FOUND,
                failure=ArtifactReadFailure.NOT_FOUND,
            )
        if record.lifecycle is ApprovedArtifactLifecycle.CLOSED:
            return ApprovedDispatchArtifactReadResult(
                status=ArtifactReadStatus.CLOSED,
                failure=ArtifactReadFailure.CLOSED,
            )
        if (
            record.ticket_revision != request.ticket_revision
            or record.handoff_revision != request.handoff_revision
        ):
            return ApprovedDispatchArtifactReadResult(
                status=ArtifactReadStatus.STALE_REVISION,
                failure=ArtifactReadFailure.STALE_REVISION,
            )
        return ApprovedDispatchArtifactReadResult(status=ArtifactReadStatus.FOUND, record=record)

    def issue_receipt(self, request: TicketReceiptIssueRequest) -> TicketReceiptIssueResult:
        self.issue_calls += 1
        if self.unavailable:
            return TicketReceiptIssueResult(
                status=ReceiptIssueStatus.STORAGE_UNAVAILABLE,
                failure=ReceiptIssueFailure.STORAGE_UNAVAILABLE,
            )
        identity = request.artifact_identity
        key = (
            identity.project_id,
            identity.ticket_reference,
            identity.handoff_reference,
            identity.implementation_owner_id,
        )
        record = self.artifacts.get(key)
        if record is None or record.lifecycle is ApprovedArtifactLifecycle.CLOSED:
            return TicketReceiptIssueResult(
                status=ReceiptIssueStatus.ARTIFACT_NOT_APPROVED,
                failure=ReceiptIssueFailure.ARTIFACT_NOT_APPROVED,
            )
        if (
            record.ticket_revision != request.ticket_revision
            or record.ticket_digest != request.ticket_digest
            or record.ticket_document_commit != request.ticket_document_commit
            or record.handoff_revision != request.handoff_revision
            or record.handoff_digest != request.handoff_digest
            or record.handoff_document_commit != request.handoff_document_commit
            or record.baseline_commit != request.baseline_commit
            or record.expected_return != request.expected_return
            or record.descriptor_binding != request.descriptor_binding
        ):
            return TicketReceiptIssueResult(
                status=ReceiptIssueStatus.PENDING_DESCRIPTOR_MISMATCH,
                failure=ReceiptIssueFailure.PENDING_DESCRIPTOR_MISMATCH,
            )
        receipt_key = (identity.project_id, identity.ticket_reference)
        existing = self.receipts.get(receipt_key)
        if existing is not None:
            if (
                existing.lifecycle in (ReceiptLifecycle.ACTIVE, ReceiptLifecycle.QUARANTINED)
                and existing == _receipt_from_request(request)
            ):
                return TicketReceiptIssueResult(
                    status=ReceiptIssueStatus.ALREADY_ISSUED,
                    receipt=existing,
                )
            return TicketReceiptIssueResult(
                status=ReceiptIssueStatus.RECEIPT_CONFLICT,
                failure=ReceiptIssueFailure.RECEIPT_CONFLICT,
            )
        receipt = _receipt_from_request(request)
        self.receipts[receipt_key] = receipt
        return TicketReceiptIssueResult(status=ReceiptIssueStatus.ISSUED, receipt=receipt)

    def read_receipt(self, request: TicketReceiptReadRequest) -> TicketReceiptReadResult:
        self.read_receipt_calls += 1
        if self.unavailable:
            return TicketReceiptReadResult(
                status=ReceiptReadStatus.STORAGE_UNAVAILABLE,
                failure=ReceiptReadFailure.STORAGE_UNAVAILABLE,
            )
        receipt = self.receipts.get((request.project_id, request.ticket_reference))
        if receipt is None:
            return TicketReceiptReadResult(
                status=ReceiptReadStatus.NOT_FOUND,
                failure=ReceiptReadFailure.NOT_FOUND,
            )
        if receipt.ticket_revision != request.ticket_revision:
            return TicketReceiptReadResult(
                status=ReceiptReadStatus.STALE_REVISION,
                failure=ReceiptReadFailure.STALE_REVISION,
            )
        if receipt.lifecycle in (ReceiptLifecycle.CLOSED, ReceiptLifecycle.REVOKED):
            return TicketReceiptReadResult(
                status=ReceiptReadStatus.CLOSED,
                failure=ReceiptReadFailure.CLOSED,
            )
        return TicketReceiptReadResult(status=ReceiptReadStatus.FOUND, receipt=receipt)


def _receipt_from_request(request: TicketReceiptIssueRequest) -> TicketReceipt:
    identity = request.artifact_identity
    return TicketReceipt(
        project_id=identity.project_id,
        receipt_id=request.receipt_id,
        ticket_reference=identity.ticket_reference,
        ticket_revision=request.ticket_revision,
        ticket_digest=request.ticket_digest,
        ticket_document_commit=request.ticket_document_commit,
        handoff_reference=identity.handoff_reference,
        handoff_revision=request.handoff_revision,
        handoff_digest=request.handoff_digest,
        handoff_document_commit=request.handoff_document_commit,
        baseline_commit=request.baseline_commit,
        implementation_owner_id=identity.implementation_owner_id,
        expected_return=request.expected_return,
        descriptor_binding=request.descriptor_binding,
        correlation_id=request.correlation_id,
        dispatch_question_id=request.dispatch_question_id,
        worktree_fingerprint=request.worktree_fingerprint,
        branch_fingerprint=request.branch_fingerprint,
    )


class LiveTicketReceiptContractTests(unittest.TestCase):
    def test_public_ticket_receipt_round_trip_rejects_legacy_projection_and_second_live_receipt(self) -> None:
        record = _artifact()
        receipt = _receipt_from_request(_issue_request(record))
        self.assertEqual(receipt, TicketReceipt.model_validate_json(receipt.model_dump_json()))
        legacy = to_legacy_ticket_dispatch_receipt(receipt)
        self.assertIs(type(legacy), TicketDispatchReceipt)
        with self.assertRaises(ValidationError):
            TicketReceipt.model_validate(legacy.model_dump())
        boundary = _Boundary()
        store = LiveDispatchMetadataStore(boundary)
        self.assertEqual(
            ArtifactRegistrationStatus.REGISTERED,
            store.register_artifact(ApprovedDispatchArtifactRegisterRequest(artifact=record)).status,
        )
        self.assertEqual(ReceiptIssueStatus.ISSUED, store.issue_receipt(_issue_request(record)).status)
        changed = _issue_request(record).model_copy(update={"receipt_id": "receipt-second-live"})
        conflict = store.issue_receipt(changed)
        self.assertEqual(ReceiptIssueStatus.RECEIPT_CONFLICT, conflict.status)
        self.assertIsNone(conflict.receipt)


class LiveArtifactRegistryTests(unittest.TestCase):
    def test_identical_registration_is_idempotent_and_identity_byte_collision_fails_closed(self) -> None:
        boundary = _Boundary()
        store = LiveDispatchMetadataStore(boundary)
        record = _artifact()
        request = ApprovedDispatchArtifactRegisterRequest(artifact=record)
        first = store.register_artifact(request)
        second = store.register_artifact(request)
        self.assertEqual(ArtifactRegistrationStatus.REGISTERED, first.status)
        self.assertEqual(ArtifactRegistrationStatus.ALREADY_REGISTERED, second.status)
        collision = record.model_copy(update={"ticket_document_commit": "abcdef0123456789"})
        result = store.register_artifact(ApprovedDispatchArtifactRegisterRequest(artifact=collision))
        self.assertEqual(ArtifactRegistrationStatus.IDENTITY_CONFLICT, result.status)
        self.assertIsNone(result.record)
        self.assertEqual(3, boundary.register_calls)

    def test_artifact_reads_are_finite_for_missing_stale_closed_and_storage_failure(self) -> None:
        boundary = _Boundary()
        store = LiveDispatchMetadataStore(boundary)
        record = _artifact()
        self.assertEqual(
            ArtifactReadStatus.NOT_FOUND,
            store.read_artifact(
                ApprovedDispatchArtifactReadRequest(
                    identity=record.identity,
                    ticket_revision=record.ticket_revision,
                    handoff_revision=record.handoff_revision,
                )
            ).status,
        )
        store.register_artifact(ApprovedDispatchArtifactRegisterRequest(artifact=record))
        stale = store.read_artifact(
            ApprovedDispatchArtifactReadRequest(
                identity=record.identity,
                ticket_revision="rev-0000000000000000",
                handoff_revision=record.handoff_revision,
            )
        )
        self.assertEqual(ArtifactReadStatus.STALE_REVISION, stale.status)
        boundary.artifacts[
            (
                record.project_id,
                record.ticket_reference,
                record.handoff_reference,
                record.implementation_owner_id,
            )
        ] = record.model_copy(update={"lifecycle": ApprovedArtifactLifecycle.CLOSED})
        closed = store.read_artifact(
            ApprovedDispatchArtifactReadRequest(
                identity=record.identity,
                ticket_revision=record.ticket_revision,
                handoff_revision=record.handoff_revision,
            )
        )
        self.assertEqual(ArtifactReadStatus.CLOSED, closed.status)
        boundary.unavailable = True
        unavailable = store.read_artifact(
            ApprovedDispatchArtifactReadRequest(
                identity=record.identity,
                ticket_revision=record.ticket_revision,
                handoff_revision=record.handoff_revision,
            )
        )
        self.assertEqual(ArtifactReadStatus.STORAGE_UNAVAILABLE, unavailable.status)


class LiveTicketReceiptStoreTests(unittest.TestCase):
    def test_issue_exact_is_compare_and_swap_on_pending_descriptor_and_survives_restart(self) -> None:
        boundary = _Boundary()
        record = _artifact()
        request = _issue_request(record)
        first_store = LiveDispatchMetadataStore(boundary)
        first_store.register_artifact(ApprovedDispatchArtifactRegisterRequest(artifact=record))
        issued = first_store.issue_receipt(request)
        self.assertEqual(ReceiptIssueStatus.ISSUED, issued.status)
        second_store = LiveDispatchMetadataStore(boundary)
        repeated = second_store.issue_receipt(request)
        self.assertEqual(ReceiptIssueStatus.ALREADY_ISSUED, repeated.status)
        self.assertEqual(issued.receipt, repeated.receipt)
        mismatch = request.model_copy(update={"descriptor_binding": "descriptor-other-r03-01"})
        self.assertEqual(
            ReceiptIssueStatus.PENDING_DESCRIPTOR_MISMATCH,
            second_store.issue_receipt(mismatch).status,
        )
        read = second_store.read_receipt(
            TicketReceiptReadRequest(
                project_id=record.project_id,
                ticket_reference=record.ticket_reference,
                ticket_revision=record.ticket_revision,
            )
        )
        self.assertEqual(ReceiptReadStatus.FOUND, read.status)
        self.assertEqual(issued.receipt, read.receipt)
        boundary.unavailable = True
        self.assertEqual(ReceiptReadStatus.STORAGE_UNAVAILABLE, second_store.read_receipt(
            TicketReceiptReadRequest(
                project_id=record.project_id,
                ticket_reference=record.ticket_reference,
                ticket_revision=record.ticket_revision,
            )
        ).status)


class LiveDispatchMetadataSourceGateTests(unittest.TestCase):
    def test_contract_and_store_are_strict_typed_and_owned_metadata_only(self) -> None:
        record = _artifact()
        with self.assertRaises(ValidationError):
            ApprovedDispatchArtifactRecord.model_validate(
                {**record.model_dump(), "project_id": 17}
            )
        with self.assertRaises(ValidationError):
            ApprovedDispatchArtifactRecord.model_validate(
                {**record.model_dump(), "extra_metadata": "forbidden"}
            )
        with self.assertRaises(ValidationError):
            ApprovedDispatchArtifactRecord.model_validate(
                {**record.model_dump(), "ticket_reference": "C:\\raw\\source"}
            )
        source_paths = (
            _ROOT / "library" / "workflow_router" / "live_dispatch_contracts.py",
            _ROOT / "library" / "local_orchestration" / "live_dispatch_metadata_store.py",
        )
        for source_path in source_paths:
            source = source_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            forbidden = ("Any", "object", "cast", "model_construct", "model_copy(update")
            self.assertFalse(any(token in source for token in forbidden), source_path.as_posix())
            self.assertFalse("except Exception" in source, source_path.as_posix())
            self.assertFalse("import os" in source or "import pathlib" in source, source_path.as_posix())
            self.assertGreater(len(tree.body), 1)


if __name__ == "__main__":
    unittest.main()
