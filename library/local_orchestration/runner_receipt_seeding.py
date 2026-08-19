"""Seed the durable boundary with a subscription's receipt before arming.

`claim_role_wake_attempt` admits a wake only for a canonical `TicketReceipt`
that already exists in the durable checkpoint as `ACTIVE` with a matching
digest. A runner that arms supervision without seeding therefore reaches the
wake stage and halts with `ROLE_WAKE_UNAVAILABLE` — the defect recorded as
CR-E6-01. Seeding is derived entirely from the receipt the subscription
already carries, and it is proven by reading the receipt back.
"""

from __future__ import annotations

from enum import Enum

from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    ReceiptIssueStatus,
    ReceiptLifecycle,
    TicketReceipt,
    TicketReceiptIssueRequest,
    TicketReceiptReadRequest,
    ReceiptReadStatus,
)

from .live_dispatch_metadata_boundary import LiveDispatchMetadataBoundary
from .live_dispatch_metadata_store import LiveDispatchMetadataStore


class ReceiptSeedStatus(str, Enum):
    """Finite outcomes of one seeding attempt."""

    SEEDED = "SEEDED"
    ALREADY_PRESENT = "ALREADY_PRESENT"
    BLOCKED = "BLOCKED"


class ReceiptSeedFailure(str, Enum):
    """Finite reasons a receipt cannot be made claimable."""

    ARTIFACT_REGISTRATION_FAILED = "ARTIFACT_REGISTRATION_FAILED"
    RECEIPT_ISSUE_FAILED = "RECEIPT_ISSUE_FAILED"
    READBACK_FAILED = "READBACK_FAILED"
    RECEIPT_MISMATCH = "RECEIPT_MISMATCH"


def _artifact_of(receipt: TicketReceipt) -> ApprovedDispatchArtifactRecord:
    return ApprovedDispatchArtifactRecord(
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


def _read_back(
    boundary: LiveDispatchMetadataBoundary, receipt: TicketReceipt
) -> ReceiptSeedFailure | None:
    """Prove the seeded receipt is the exact active one a wake claim needs."""

    read = boundary.read_receipt(
        TicketReceiptReadRequest(
            project_id=receipt.project_id,
            ticket_reference=receipt.ticket_reference,
            ticket_revision=receipt.ticket_revision,
        )
    )
    if read.status is not ReceiptReadStatus.FOUND or read.receipt is None:
        return ReceiptSeedFailure.READBACK_FAILED
    stored = read.receipt
    if (
        stored.receipt_id != receipt.receipt_id
        or stored.lifecycle is not ReceiptLifecycle.ACTIVE
        or stored != receipt
    ):
        return ReceiptSeedFailure.RECEIPT_MISMATCH
    return None


def seed_receipt(
    boundary: LiveDispatchMetadataBoundary, receipt: TicketReceipt
) -> tuple[ReceiptSeedStatus, ReceiptSeedFailure | None]:
    """Make one subscription's receipt claimable, or report exactly why not."""

    already = _read_back(boundary, receipt)
    if already is None:
        return ReceiptSeedStatus.ALREADY_PRESENT, None

    store = LiveDispatchMetadataStore(boundary)
    artifact = _artifact_of(receipt)
    try:
        store.register_artifact(
            ApprovedDispatchArtifactRegisterRequest(artifact=artifact)
        )
    except Exception:
        return ReceiptSeedStatus.BLOCKED, (
            ReceiptSeedFailure.ARTIFACT_REGISTRATION_FAILED
        )
    try:
        issued = store.issue_receipt(
            TicketReceiptIssueRequest(
                artifact_identity=artifact.identity,
                ticket_revision=receipt.ticket_revision,
                ticket_digest=receipt.ticket_digest,
                ticket_document_commit=receipt.ticket_document_commit,
                handoff_revision=receipt.handoff_revision,
                handoff_digest=receipt.handoff_digest,
                handoff_document_commit=receipt.handoff_document_commit,
                baseline_commit=receipt.baseline_commit,
                receipt_id=receipt.receipt_id,
                expected_return=receipt.expected_return,
                descriptor_binding=receipt.descriptor_binding,
                correlation_id=receipt.correlation_id,
                dispatch_question_id=receipt.dispatch_question_id,
                worktree_fingerprint=receipt.worktree_fingerprint,
                branch_fingerprint=receipt.branch_fingerprint,
            )
        )
    except Exception:
        return ReceiptSeedStatus.BLOCKED, ReceiptSeedFailure.RECEIPT_ISSUE_FAILED
    if issued.status not in (
        ReceiptIssueStatus.ISSUED,
        ReceiptIssueStatus.ALREADY_ISSUED,
    ):
        return ReceiptSeedStatus.BLOCKED, ReceiptSeedFailure.RECEIPT_ISSUE_FAILED

    proven = _read_back(boundary, receipt)
    if proven is not None:
        return ReceiptSeedStatus.BLOCKED, proven
    return ReceiptSeedStatus.SEEDED, None


__all__ = ["ReceiptSeedFailure", "ReceiptSeedStatus", "seed_receipt"]
