"""Declared project-authority contracts and pure lifecycle seam."""

from .contracts import (
    AuthorityContractAdmission,
    AuthorityContractAdmissionDecision,
    AuthorityContractInput,
    AuthorityIntegrationState,
    AuthorityLineRole,
    AuthorityObservationAdmission,
    AuthorityObservationDecision,
    BridgeCapability,
    FullBranchRef,
    GitObservation,
    GitObservationSource,
    ProjectAuthorityContract,
    ProjectTopology,
    RemoteProviderKind,
    RemoteRepositoryId,
    admit_authority_contract,
    admit_authority_observation,
)
from .integration import (
    PrePushLifecycleRequest,
    PrePushLifecycleTransition,
    advance_pre_push_lifecycle,
)

__all__ = (
    "AuthorityContractAdmission",
    "AuthorityContractAdmissionDecision",
    "AuthorityContractInput",
    "AuthorityIntegrationState",
    "AuthorityLineRole",
    "AuthorityObservationAdmission",
    "AuthorityObservationDecision",
    "BridgeCapability",
    "FullBranchRef",
    "GitObservation",
    "GitObservationSource",
    "PrePushLifecycleRequest",
    "PrePushLifecycleTransition",
    "ProjectAuthorityContract",
    "ProjectTopology",
    "RemoteProviderKind",
    "RemoteRepositoryId",
    "admit_authority_contract",
    "admit_authority_observation",
    "advance_pre_push_lifecycle",
)
