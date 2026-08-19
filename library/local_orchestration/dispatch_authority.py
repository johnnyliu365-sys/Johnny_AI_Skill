"""Dispatch authority admission: the workstation entry that may issue receipts.

This is the phase-C landing the E8 closures deferred: receipt issuance stops
being a test fixture and becomes an explicit workstation entry with an
admission gate. The gate runs fail-closed and in a fixed order — owner grant,
strict request validation, worktree containment, artifact registration,
CAS issuance (the store's reviewed semantics untouched), and a readback that
proves the issued receipt is claimable through the same read path the runner
uses. Every outcome is journaled with the host principal.

**What the grant is, honestly.** The dispatch-authority grant is an owner
intent marker and audit anchor on a single-user machine. It is *not* a
cryptographic boundary: any code in the same process could create one. The
real principal separation — issuance as an OS-level process privilege —
remains this line's later work, exactly as CLOSURE-E8-02 recorded. What the
grant does buy today: no accidental issuance (the entry refuses until the
owner has explicitly said "this machine dispatches"), and every issuance
tied to a grant id and principal in the journal.
"""

from __future__ import annotations

import getpass
import json
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactRecord,
    ApprovedDispatchArtifactRegisterRequest,
    ArtifactRegistrationStatus,
    ReceiptIssueStatus,
    TicketReceipt,
    TicketReceiptIssueRequest,
)

from .issuance_scoped_boundary import IssuanceScopedDispatchBoundary
from .johnny_root_layout import JohnnyRootLayout
from .runner_receipt_seeding import (
    ReceiptVerificationStatus,
    verify_receipt_claimable,
)
from .worktree_containment import (
    WorktreeContainmentStatus,
    verify_worktree_contained,
)

_GRANT_FILE_NAME = "dispatch-authority.json"
_JOURNAL_FILE_NAME = "dispatch-journal.jsonl"
_OPAQUE = r"^[a-z][a-z0-9-]{2,127}$"
_WORKTREE = r"^worktree-[a-z0-9]+-[0-9]{2}$"
_BRANCH = r"^branch-[a-z0-9]+-[0-9]{2}$"


class DispatchGrantStatus(str, Enum):
    """Finite outcomes of one grant creation."""

    GRANTED = "GRANTED"
    ALREADY_GRANTED = "ALREADY_GRANTED"
    REFUSED = "REFUSED"


class DispatchAdmissionStatus(str, Enum):
    """Finite outcomes of one dispatch admission."""

    DISPATCHED = "DISPATCHED"
    REFUSED = "REFUSED"


class DispatchAdmissionFailure(str, Enum):
    """Finite reasons an admission is refused."""

    DISPATCH_AUTHORITY_ABSENT = "DISPATCH_AUTHORITY_ABSENT"
    REQUEST_INVALID = "REQUEST_INVALID"
    WORKTREE_OUTSIDE_REPOSITORY_ROOT = "WORKTREE_OUTSIDE_REPOSITORY_ROOT"
    ARTIFACT_CONFLICT = "ARTIFACT_CONFLICT"
    RECEIPT_CONFLICT = "RECEIPT_CONFLICT"
    ISSUANCE_NOT_READABLE = "ISSUANCE_NOT_READABLE"
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"


class DispatchGrant(BaseModel):
    """The durable owner grant this workstation dispatches under."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: int = Field(default=1, ge=1, le=1)
    grant_id: str = Field(min_length=8, max_length=64)
    granted_by: str = Field(min_length=1, max_length=128)
    granted_at_utc: str = Field(min_length=1, max_length=64)


class DispatchAdmissionRequest(BaseModel):
    """One issuance request: the reviewed artifact plus issue-only identity.

    The `TicketReceiptIssueRequest` is derived from the artifact, so the
    descriptor fields cannot disagree by construction. The two host paths
    exist only for the containment gate and never enter the receipt.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: int = Field(default=1, ge=1, le=1)
    artifact: ApprovedDispatchArtifactRecord
    receipt_id: str = Field(pattern=_OPAQUE)
    correlation_id: str = Field(pattern=_OPAQUE)
    dispatch_question_id: str = Field(pattern=_OPAQUE)
    worktree_fingerprint: str = Field(pattern=_WORKTREE)
    branch_fingerprint: str = Field(pattern=_BRANCH)
    repository_root: str = Field(min_length=1, max_length=512)
    host_worktree_path: str = Field(min_length=1, max_length=512)


class DispatchAdmissionResult(BaseModel):
    """Exactly one dispatched receipt or one finite refusal."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    status: DispatchAdmissionStatus
    receipt: TicketReceipt | None = None
    failure: DispatchAdmissionFailure | None = None

    @classmethod
    def refused(cls, failure: DispatchAdmissionFailure) -> Self:
        return cls(status=DispatchAdmissionStatus.REFUSED, failure=failure)


def grant_path(layout: JohnnyRootLayout) -> Path:
    return layout.base / _GRANT_FILE_NAME


def journal_path(layout: JohnnyRootLayout) -> Path:
    return layout.queue_root / _JOURNAL_FILE_NAME


def create_dispatch_grant(
    layout: JohnnyRootLayout,
) -> tuple[DispatchGrantStatus, DispatchGrant | None]:
    """Record the owner's explicit decision that this machine dispatches."""

    path = grant_path(layout)
    existing = read_dispatch_grant(layout)
    if existing is not None:
        return DispatchGrantStatus.ALREADY_GRANTED, existing
    grant = DispatchGrant(
        grant_id=uuid.uuid4().hex,
        granted_by=getpass.getuser(),
        granted_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(grant.model_dump_json(), encoding="utf-8")
        os.replace(temporary, path)
    except OSError:
        return DispatchGrantStatus.REFUSED, None
    return DispatchGrantStatus.GRANTED, grant


def read_dispatch_grant(layout: JohnnyRootLayout) -> DispatchGrant | None:
    """The current grant, or None when this machine has never been granted."""

    path = grant_path(layout)
    if not path.is_file():
        return None
    try:
        return DispatchGrant.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None


def _issue_request(request: DispatchAdmissionRequest) -> TicketReceiptIssueRequest:
    artifact = request.artifact
    return TicketReceiptIssueRequest(
        artifact_identity=artifact.identity,
        ticket_revision=artifact.ticket_revision,
        ticket_digest=artifact.ticket_digest,
        ticket_document_commit=artifact.ticket_document_commit,
        handoff_revision=artifact.handoff_revision,
        handoff_digest=artifact.handoff_digest,
        handoff_document_commit=artifact.handoff_document_commit,
        baseline_commit=artifact.baseline_commit,
        receipt_id=request.receipt_id,
        expected_return=artifact.expected_return,
        descriptor_binding=artifact.descriptor_binding,
        correlation_id=request.correlation_id,
        dispatch_question_id=request.dispatch_question_id,
        worktree_fingerprint=request.worktree_fingerprint,
        branch_fingerprint=request.branch_fingerprint,
    )


def _journal(
    layout: JohnnyRootLayout,
    grant: DispatchGrant | None,
    request: DispatchAdmissionRequest | None,
    outcome: str,
) -> None:
    """Append one audit line; journaling failure never blocks the outcome."""

    entry = {
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "principal": getpass.getuser(),
        "grant_id": grant.grant_id if grant is not None else None,
        "receipt_id": request.receipt_id if request is not None else None,
        "ticket_reference": (
            request.artifact.ticket_reference if request is not None else None
        ),
        "host_worktree_path": (
            request.host_worktree_path if request is not None else None
        ),
        "outcome": outcome,
    }
    try:
        path = journal_path(layout)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
    except OSError:
        pass


def admit_dispatch(
    layout: JohnnyRootLayout, request: DispatchAdmissionRequest
) -> DispatchAdmissionResult:
    """Admit one issuance through the full gate, or refuse finitely."""

    grant = read_dispatch_grant(layout)
    if grant is None:
        _journal(layout, None, None, "DISPATCH_AUTHORITY_ABSENT")
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure.DISPATCH_AUTHORITY_ABSENT
        )
    if type(request) is not DispatchAdmissionRequest:
        _journal(layout, grant, None, "REQUEST_INVALID")
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure.REQUEST_INVALID
        )

    containment, _ = verify_worktree_contained(
        Path(request.repository_root), Path(request.host_worktree_path)
    )
    if containment is not WorktreeContainmentStatus.CONTAINED:
        _journal(layout, grant, request, "WORKTREE_OUTSIDE_REPOSITORY_ROOT")
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure.WORKTREE_OUTSIDE_REPOSITORY_ROOT
        )

    metadata_root = layout.queue_root / "metadata"
    try:
        metadata_root.mkdir(parents=True, exist_ok=True)
        boundary = IssuanceScopedDispatchBoundary(metadata_root)
    except OSError:
        _journal(layout, grant, request, "STORAGE_UNAVAILABLE")
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure.STORAGE_UNAVAILABLE
        )

    registered = boundary.register_artifact(
        ApprovedDispatchArtifactRegisterRequest(artifact=request.artifact)
    )
    if registered.status not in (
        ArtifactRegistrationStatus.REGISTERED,
        ArtifactRegistrationStatus.ALREADY_REGISTERED,
    ):
        outcome = (
            "ARTIFACT_CONFLICT"
            if registered.status is ArtifactRegistrationStatus.IDENTITY_CONFLICT
            else "STORAGE_UNAVAILABLE"
        )
        _journal(layout, grant, request, outcome)
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure[outcome]
        )

    issued = boundary.issue_receipt(_issue_request(request))
    if issued.status not in (
        ReceiptIssueStatus.ISSUED,
        ReceiptIssueStatus.ALREADY_ISSUED,
    ) or issued.receipt is None:
        outcome = (
            "STORAGE_UNAVAILABLE"
            if issued.status is ReceiptIssueStatus.STORAGE_UNAVAILABLE
            else "RECEIPT_CONFLICT"
        )
        _journal(layout, grant, request, outcome)
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure[outcome]
        )

    verification, _ = verify_receipt_claimable(boundary, issued.receipt)
    if verification is not ReceiptVerificationStatus.CLAIMABLE:
        _journal(layout, grant, request, "ISSUANCE_NOT_READABLE")
        return DispatchAdmissionResult.refused(
            DispatchAdmissionFailure.ISSUANCE_NOT_READABLE
        )

    _journal(layout, grant, request, "DISPATCHED")
    return DispatchAdmissionResult(
        status=DispatchAdmissionStatus.DISPATCHED,
        receipt=issued.receipt,
    )


__all__ = [
    "DispatchAdmissionFailure",
    "DispatchAdmissionRequest",
    "DispatchAdmissionResult",
    "DispatchAdmissionStatus",
    "DispatchGrant",
    "DispatchGrantStatus",
    "admit_dispatch",
    "create_dispatch_grant",
    "grant_path",
    "journal_path",
    "read_dispatch_grant",
]
