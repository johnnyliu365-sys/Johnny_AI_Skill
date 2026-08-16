"""Injected durable metadata-store ports for live dispatch state."""

from __future__ import annotations

from typing import Protocol

from pydantic import ValidationError

from library.workflow_router.live_dispatch_contracts import (
    ApprovedDispatchArtifactReadRequest,
    ApprovedDispatchArtifactReadResult,
    ApprovedDispatchArtifactRegisterRequest,
    ApprovedDispatchArtifactRegisterResult,
    ArtifactReadFailure,
    ArtifactReadStatus,
    ArtifactRegistrationFailure,
    ArtifactRegistrationStatus,
    ReceiptIssueFailure,
    ReceiptIssueStatus,
    TicketReceiptIssueRequest,
    TicketReceiptIssueResult,
    TicketReceiptReadRequest,
    TicketReceiptReadResult,
    ReceiptReadFailure,
    ReceiptReadStatus,
)


class LiveDispatchMetadataBoundaryPort(Protocol):
    """Installer-owned journal/checkpoint boundary supplied by composition."""

    def register_artifact(
        self,
        request: ApprovedDispatchArtifactRegisterRequest,
    ) -> ApprovedDispatchArtifactRegisterResult: ...

    def read_artifact(
        self,
        request: ApprovedDispatchArtifactReadRequest,
    ) -> ApprovedDispatchArtifactReadResult: ...

    def issue_receipt(
        self,
        request: TicketReceiptIssueRequest,
    ) -> TicketReceiptIssueResult: ...

    def read_receipt(
        self,
        request: TicketReceiptReadRequest,
    ) -> TicketReceiptReadResult: ...


class LiveApprovedDispatchArtifactRegistryPort(Protocol):
    """Registry port for exact reviewed artifact registration and reads."""

    def register_artifact(
        self,
        request: ApprovedDispatchArtifactRegisterRequest,
    ) -> ApprovedDispatchArtifactRegisterResult: ...

    def read_artifact(
        self,
        request: ApprovedDispatchArtifactReadRequest,
    ) -> ApprovedDispatchArtifactReadResult: ...


class TicketReceiptStorePort(Protocol):
    """Receipt port for exact compare-and-swap issue and reads."""

    def issue_receipt(self, request: TicketReceiptIssueRequest) -> TicketReceiptIssueResult: ...

    def read_receipt(self, request: TicketReceiptReadRequest) -> TicketReceiptReadResult: ...


def _invalid_register_result() -> ApprovedDispatchArtifactRegisterResult:
    return ApprovedDispatchArtifactRegisterResult(
        status=ArtifactRegistrationStatus.STORAGE_UNAVAILABLE,
        failure=ArtifactRegistrationFailure.STORAGE_UNAVAILABLE,
    )


def _invalid_artifact_read_result() -> ApprovedDispatchArtifactReadResult:
    return ApprovedDispatchArtifactReadResult(
        status=ArtifactReadStatus.STORAGE_UNAVAILABLE,
        failure=ArtifactReadFailure.STORAGE_UNAVAILABLE,
    )


def _invalid_issue_result() -> TicketReceiptIssueResult:
    return TicketReceiptIssueResult(
        status=ReceiptIssueStatus.STORAGE_UNAVAILABLE,
        failure=ReceiptIssueFailure.STORAGE_UNAVAILABLE,
    )


def _invalid_receipt_read_result() -> TicketReceiptReadResult:
    return TicketReceiptReadResult(
        status=ReceiptReadStatus.STORAGE_UNAVAILABLE,
        failure=ReceiptReadFailure.STORAGE_UNAVAILABLE,
    )


class LiveDispatchMetadataStore(
    LiveApprovedDispatchArtifactRegistryPort,
    TicketReceiptStorePort,
):
    """Composition adapter over one injected installer-owned metadata boundary."""

    def __init__(self, boundary: LiveDispatchMetadataBoundaryPort) -> None:
        self._boundary = boundary

    def register_artifact(
        self,
        request: ApprovedDispatchArtifactRegisterRequest,
    ) -> ApprovedDispatchArtifactRegisterResult:
        if type(request) is not ApprovedDispatchArtifactRegisterRequest:
            return _invalid_register_result()
        try:
            result = self._boundary.register_artifact(request)
            if type(result) is not ApprovedDispatchArtifactRegisterResult:
                return _invalid_register_result()
            return ApprovedDispatchArtifactRegisterResult.model_validate(result)
        except ValidationError:
            return _invalid_register_result()

    def read_artifact(
        self,
        request: ApprovedDispatchArtifactReadRequest,
    ) -> ApprovedDispatchArtifactReadResult:
        if type(request) is not ApprovedDispatchArtifactReadRequest:
            return _invalid_artifact_read_result()
        try:
            result = self._boundary.read_artifact(request)
            if type(result) is not ApprovedDispatchArtifactReadResult:
                return _invalid_artifact_read_result()
            return ApprovedDispatchArtifactReadResult.model_validate(result)
        except ValidationError:
            return _invalid_artifact_read_result()

    def issue_receipt(self, request: TicketReceiptIssueRequest) -> TicketReceiptIssueResult:
        if type(request) is not TicketReceiptIssueRequest:
            return _invalid_issue_result()
        try:
            result = self._boundary.issue_receipt(request)
            if type(result) is not TicketReceiptIssueResult:
                return _invalid_issue_result()
            return TicketReceiptIssueResult.model_validate(result)
        except ValidationError:
            return _invalid_issue_result()

    def read_receipt(self, request: TicketReceiptReadRequest) -> TicketReceiptReadResult:
        if type(request) is not TicketReceiptReadRequest:
            return _invalid_receipt_read_result()
        try:
            result = self._boundary.read_receipt(request)
            if type(result) is not TicketReceiptReadResult:
                return _invalid_receipt_read_result()
            return TicketReceiptReadResult.model_validate(result)
        except ValidationError:
            return _invalid_receipt_read_result()


__all__ = [
    "LiveApprovedDispatchArtifactRegistryPort",
    "LiveDispatchMetadataBoundaryPort",
    "LiveDispatchMetadataStore",
    "TicketReceiptStorePort",
]
