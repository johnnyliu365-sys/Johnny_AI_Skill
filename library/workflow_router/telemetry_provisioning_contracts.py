"""Private Router authorization contracts for telemetry provisioning."""

from __future__ import annotations

from hashlib import sha256
from enum import Enum

from pydantic import model_validator

from library.workflow_router.contracts import (
    OpaqueMetadataId,
    ProjectId,
    ReviewedCommitReference,
    RouterModel,
)
from library.workflow_router.policy_response import (
    ApprovedDispatchArtifactRegistry,
    resolve_approved_dispatch_artifact,
)


class RouterTelemetryProvisioningDecision(str, Enum):
    """Finite outcomes of one Router-owned provisioning authorization check."""

    AUTHORIZED = "AUTHORIZED"
    AUTHORITY_MISMATCH = "AUTHORITY_MISMATCH"


class RouterTelemetryProvisioningRequest(RouterModel):
    """Exact metadata coordinates supplied by the Router authorization boundary."""

    request_ref: OpaqueMetadataId
    project_id: ProjectId
    ticket_reference: OpaqueMetadataId
    handoff_reference: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    ticket_docs_commit: ReviewedCommitReference
    handoff_docs_commit: ReviewedCommitReference


class RouterTelemetryProvisioningAuthorized(RouterModel):
    """Finite grant carrying only the validated opaque dispatch identity."""

    decision: RouterTelemetryProvisioningDecision = RouterTelemetryProvisioningDecision.AUTHORIZED
    request_ref: OpaqueMetadataId
    project_id: ProjectId
    ticket_reference: OpaqueMetadataId
    handoff_reference: OpaqueMetadataId
    implementation_owner_id: OpaqueMetadataId
    provisioning_authority_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def decision_is_authorized(self) -> "RouterTelemetryProvisioningAuthorized":
        if self.decision is not RouterTelemetryProvisioningDecision.AUTHORIZED:
            raise ValueError("authorized result requires AUTHORIZED")
        return self


class RouterTelemetryProvisioningAuthorityMismatch(RouterModel):
    """Finite denial carrying no approved identity or durable authority."""

    decision: RouterTelemetryProvisioningDecision = RouterTelemetryProvisioningDecision.AUTHORITY_MISMATCH
    request_ref: OpaqueMetadataId
    denial_ref: OpaqueMetadataId

    @model_validator(mode="after")
    def decision_is_mismatch(self) -> "RouterTelemetryProvisioningAuthorityMismatch":
        if self.decision is not RouterTelemetryProvisioningDecision.AUTHORITY_MISMATCH:
            raise ValueError("mismatch result requires AUTHORITY_MISMATCH")
        return self


RouterTelemetryProvisioningResult = (
    RouterTelemetryProvisioningAuthorized
    | RouterTelemetryProvisioningAuthorityMismatch
)


_AUTHORITY_DOMAIN = "router-telemetry-provisioning-authority-v1"
_DENIAL_DOMAIN = "router-telemetry-provisioning-denial-v1"


def _dispatch_material(request: RouterTelemetryProvisioningRequest) -> tuple[str, ...]:
    return (
        request.project_id,
        request.ticket_reference,
        request.handoff_reference,
        request.implementation_owner_id,
        request.ticket_docs_commit,
        request.handoff_docs_commit,
    )


def _denial_material(request: RouterTelemetryProvisioningRequest) -> tuple[str, ...]:
    return (request.request_ref, *_dispatch_material(request))


def _opaque_digest(domain: str, values: tuple[str, ...]) -> str:
    material = "\0".join((domain, *values))
    return sha256(material.encode("utf-8")).hexdigest()


def _denial(request: RouterTelemetryProvisioningRequest) -> RouterTelemetryProvisioningAuthorityMismatch:
    return RouterTelemetryProvisioningAuthorityMismatch(
        request_ref=request.request_ref,
        denial_ref=f"provision-denial-{_opaque_digest(_DENIAL_DOMAIN, _denial_material(request))}",
    )


def authorize_router_telemetry_provisioning(
    registry: ApprovedDispatchArtifactRegistry,
    request: RouterTelemetryProvisioningRequest,
) -> RouterTelemetryProvisioningResult:
    """Return one ephemeral grant only for an exact registry and commit match."""

    try:
        artifact = resolve_approved_dispatch_artifact(
            registry,
            project_id=request.project_id,
            ticket_reference=request.ticket_reference,
            handoff_reference=request.handoff_reference,
            implementation_owner_id=request.implementation_owner_id,
            ticket_docs_commit=request.ticket_docs_commit,
            handoff_docs_commit=request.handoff_docs_commit,
        )
    except Exception:
        return _denial(request)
    if artifact is None:
        return _denial(request)
    return RouterTelemetryProvisioningAuthorized(
        request_ref=request.request_ref,
        project_id=artifact.project_id,
        ticket_reference=artifact.ticket_reference,
        handoff_reference=artifact.handoff_reference,
        implementation_owner_id=artifact.implementation_owner_id,
        provisioning_authority_ref=(
            "provision-authority-"
            + _opaque_digest(_AUTHORITY_DOMAIN, _dispatch_material(request))
        ),
    )


__all__ = (
    "RouterTelemetryProvisioningDecision",
    "RouterTelemetryProvisioningRequest",
    "RouterTelemetryProvisioningAuthorized",
    "RouterTelemetryProvisioningAuthorityMismatch",
    "RouterTelemetryProvisioningResult",
    "authorize_router_telemetry_provisioning",
)
