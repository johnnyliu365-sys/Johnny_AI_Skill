"""Thin effect adapter from one exact 05S4 oracle to the compensation port."""

from __future__ import annotations

from enum import Enum
import ntpath
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.codex_compensation_port import (
    CodexCompensationPortFailureReason,
    CodexCompensationPortManifest,
    CodexCompensationPortOperation,
    CodexCompensationPortOperationFailed,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
    revalidate_codex_compensation_port_request,
)
from library.local_orchestration.contracts import CANONICAL_INSTALL_ROOT
from library.local_orchestration.host_contracts import (
    CodexMarketplaceList,
    CodexPluginList,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleAbsent,
    OracleAction,
    OracleCommand,
    OracleIdentity,
    OracleRunResult,
)
from tests.staging.codex_lifecycle_oracle.identity_binding import (
    FIXED_STAGING_LOGICAL_ROOT,
    STAGING_PLUGIN_INSTALL_POLICY,
    STAGING_PLUGIN_SOURCE,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.response_admission import (
    CodexOracleResponseAdmission,
    CodexOracleResponseRejectReason,
    CodexOracleResponseRejected,
    admit_codex_oracle_response,
)
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceRemove,
    CodexPluginRemove,
    CodexProtocolAccepted,
)
from tests.staging.environment_core.contracts import EnvironmentLease, revalidate_lease


class _StrictModel(BaseModel):
    """Closed metadata-only factory results."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class CodexCompensationOracleAdapterRejectReason(str, Enum):
    """Finite reasons for rejecting the effect adapter before an oracle call."""

    INVALID_LEASE = "INVALID_LEASE"
    INVALID_ORACLE = "INVALID_ORACLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    LOGICAL_ROOT_MISMATCH = "LOGICAL_ROOT_MISMATCH"
    INVALID_IDENTITY = "INVALID_IDENTITY"


class CodexCompensationOracleAdapterRejected(_StrictModel):
    """Metadata-only factory rejection without a request, oracle or path."""

    status: Literal["ORACLE_COMPENSATION_ADAPTER_BLOCKED"] = "ORACLE_COMPENSATION_ADAPTER_BLOCKED"
    reason: CodexCompensationOracleAdapterRejectReason


CodexCompensationOracleAdapterAdmission: TypeAlias = (
    "CodexCompensationOracleAdapter | CodexCompensationOracleAdapterRejected"
)


_ADAPTER_FACTORY_KEY: Final[object] = object()


def create_oracle_compensation_adapter(
    lease: object,
    oracle: object,
    request: object,
) -> CodexCompensationOracleAdapterAdmission:
    """Bind one rebuilt lease, exact oracle, request and deterministic identity."""

    rebuilt_lease = _rebuild_lease(lease)
    if rebuilt_lease is None:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.INVALID_LEASE)
    if type(oracle) is not CodexLifecycleOracle:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.INVALID_ORACLE)
    rebuilt_request = revalidate_codex_compensation_port_request(request)
    if type(rebuilt_request) is not CodexCompensationPortRequest:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.INVALID_REQUEST)
    if rebuilt_request.manifest.root.value != CANONICAL_INSTALL_ROOT:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.LOGICAL_ROOT_MISMATCH)
    if ntpath.expandvars(CANONICAL_INSTALL_ROOT) != FIXED_STAGING_LOGICAL_ROOT:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.LOGICAL_ROOT_MISMATCH)
    bound_identity = _identity_from_manifest(rebuilt_request.manifest)
    if bound_identity is None:
        return _factory_rejected(CodexCompensationOracleAdapterRejectReason.INVALID_IDENTITY)
    return CodexCompensationOracleAdapter(
        _ADAPTER_FACTORY_KEY,
        rebuilt_lease,
        oracle,
        rebuilt_request,
        bound_identity,
    )


class CodexCompensationOracleAdapter:
    """Five fixed plain methods over one retained oracle capability."""

    __slots__ = ("_lease", "_oracle", "_request", "_identity")

    def __init__(
        self,
        factory_key: object,
        lease: EnvironmentLease,
        oracle: CodexLifecycleOracle,
        request: CodexCompensationPortRequest,
        identity: OracleIdentity,
    ) -> None:
        if factory_key is not _ADAPTER_FACTORY_KEY:
            raise TypeError("adapter construction is factory-only")
        self._lease = lease
        self._oracle = oracle
        self._request = request
        self._identity = identity

    def remove_plugin(
        self,
        request: CodexCompensationPortRequest,
    ) -> CodexPluginRemovalProof | CodexCompensationPortOperationFailed:
        """Remove only the manifest-bound plugin after exact response admission."""

        current = self._request_or_failure(request, CodexCompensationPortOperation.REMOVE_PLUGIN)
        if type(current) is CodexCompensationPortOperationFailed:
            return current
        admitted = self._run(OracleAction.PLUGIN_REMOVE)
        if type(admitted) is CodexOracleResponseRejected:
            return self._response_failure(current.manifest, CodexCompensationPortOperation.REMOVE_PLUGIN, admitted)
        if type(admitted) is not CodexProtocolAccepted or type(admitted.payload) is not CodexPluginRemove:
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        payload = admitted.payload
        if not _plugin_removal_matches(payload, self._identity):
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.REMOVE_PLUGIN,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        return CodexPluginRemovalProof(manifest=current.manifest, status="REMOVED")

    def remove_marketplace(
        self,
        request: CodexCompensationPortRequest,
    ) -> CodexMarketplaceRemovalProof | CodexCompensationPortOperationFailed:
        """Remove only the manifest-bound marketplace after exact response admission."""

        current = self._request_or_failure(request, CodexCompensationPortOperation.REMOVE_MARKETPLACE)
        if type(current) is CodexCompensationPortOperationFailed:
            return current
        admitted = self._run(OracleAction.MARKETPLACE_REMOVE)
        if type(admitted) is CodexOracleResponseRejected:
            return self._response_failure(current.manifest, CodexCompensationPortOperation.REMOVE_MARKETPLACE, admitted)
        if type(admitted) is not CodexProtocolAccepted or type(admitted.payload) is not CodexMarketplaceRemove:
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        payload = admitted.payload
        if not _marketplace_removal_matches(payload, self._identity):
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.REMOVE_MARKETPLACE,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        return CodexMarketplaceRemovalProof(manifest=current.manifest, status="REMOVED")

    def list_plugins(
        self,
        request: CodexCompensationPortRequest,
    ) -> CodexPluginList | CodexCompensationPortOperationFailed:
        """Return the recursively rebuilt plugin list without filtering its data."""

        current = self._request_or_failure(request, CodexCompensationPortOperation.LIST_PLUGINS)
        if type(current) is CodexCompensationPortOperationFailed:
            return current
        admitted = self._run(OracleAction.PLUGIN_LIST)
        if type(admitted) is CodexOracleResponseRejected:
            return self._response_failure(current.manifest, CodexCompensationPortOperation.LIST_PLUGINS, admitted)
        if type(admitted) is not CodexProtocolAccepted or type(admitted.payload) is not CodexPluginList:
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.LIST_PLUGINS,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        return admitted.payload

    def list_marketplaces(
        self,
        request: CodexCompensationPortRequest,
    ) -> CodexMarketplaceList | CodexCompensationPortOperationFailed:
        """Return the recursively rebuilt marketplace list without filtering its data."""

        current = self._request_or_failure(request, CodexCompensationPortOperation.LIST_MARKETPLACES)
        if type(current) is CodexCompensationPortOperationFailed:
            return current
        admitted = self._run(OracleAction.MARKETPLACE_LIST)
        if type(admitted) is CodexOracleResponseRejected:
            return self._response_failure(current.manifest, CodexCompensationPortOperation.LIST_MARKETPLACES, admitted)
        if type(admitted) is not CodexProtocolAccepted or type(admitted.payload) is not CodexMarketplaceList:
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.LIST_MARKETPLACES,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        return admitted.payload

    def prove_installed_path_absent(
        self,
        request: CodexCompensationPortRequest,
    ) -> CodexInstalledPathAbsenceProof | CodexCompensationPortOperationFailed:
        """Prove absence only from the exact admitted OracleAbsent result."""

        current = self._request_or_failure(request, CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT)
        if type(current) is CodexCompensationPortOperationFailed:
            return current
        admitted = self._run(OracleAction.ABSENCE)
        if type(admitted) is CodexOracleResponseRejected:
            return self._response_failure(
                current.manifest,
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                admitted,
            )
        if type(admitted) is not OracleAbsent:
            return _operation_failure(
                current.manifest,
                CodexCompensationPortOperation.PROVE_INSTALLED_PATH_ABSENT,
                CodexCompensationPortFailureReason.EVIDENCE_INVALID,
            )
        return CodexInstalledPathAbsenceProof(manifest=current.manifest, absent=True)

    def _request_or_failure(
        self,
        request: object,
        operation: CodexCompensationPortOperation,
    ) -> CodexCompensationPortRequest | CodexCompensationPortOperationFailed:
        rebuilt = revalidate_codex_compensation_port_request(request)
        if type(rebuilt) is not CodexCompensationPortRequest or not _requests_match(rebuilt, self._request):
            return _operation_failure(
                self._request.manifest,
                operation,
                CodexCompensationPortFailureReason.REQUEST_INVALID,
            )
        return rebuilt

    def _run(self, action: OracleAction) -> CodexOracleResponseAdmission:
        command = OracleCommand(action=action, identity=self._identity)
        result: OracleRunResult = self._oracle.run(self._lease, command)
        return admit_codex_oracle_response(result, action)

    @staticmethod
    def _response_failure(
        manifest: CodexCompensationPortManifest,
        operation: CodexCompensationPortOperation,
        response: CodexOracleResponseRejected,
    ) -> CodexCompensationPortOperationFailed:
        reason = (
            CodexCompensationPortFailureReason.DEPENDENCY_BLOCKED
            if response.reason is CodexOracleResponseRejectReason.DEPENDENCY_BLOCKED
            else CodexCompensationPortFailureReason.EVIDENCE_INVALID
        )
        return _operation_failure(manifest, operation, reason)


def _rebuild_lease(value: object) -> EnvironmentLease | None:
    if type(value) is not EnvironmentLease:
        return None
    rebuilt = revalidate_lease(value)
    if type(rebuilt) is not EnvironmentLease:
        return None
    return rebuilt


def _identity_from_manifest(manifest: CodexCompensationPortManifest) -> OracleIdentity | None:
    try:
        return OracleIdentity(
            marketplace_name=manifest.marketplace.value,
            marketplace_root=ntpath.join(FIXED_STAGING_LOGICAL_ROOT, manifest.marketplace_source.value.replace("/", "\\")),
            plugin_id=manifest.plugin_id.value,
            plugin_name=manifest.plugin.value,
            plugin_version=manifest.version.value,
            plugin_source=STAGING_PLUGIN_SOURCE,
            plugin_install_policy=STAGING_PLUGIN_INSTALL_POLICY,
            plugin_auth_policy=manifest.auth_policy.value,
            plugin_installed_path=ntpath.join(FIXED_STAGING_LOGICAL_ROOT, manifest.installed_locator.value.replace("/", "\\")),
        )
    except (TypeError, ValidationError, ValueError):
        return None


def _requests_match(first: CodexCompensationPortRequest, second: CodexCompensationPortRequest) -> bool:
    first_manifest = first.manifest
    second_manifest = second.manifest
    return _manifests_match(first_manifest, second_manifest)


def _manifests_match(first: CodexCompensationPortManifest, second: CodexCompensationPortManifest) -> bool:
    return (
        first.installation_id.value == second.installation_id.value
        and first.root.value == second.root.value
        and first.marketplace.value == second.marketplace.value
        and first.marketplace_source.value == second.marketplace_source.value
        and first.plugin_id.value == second.plugin_id.value
        and first.plugin.value == second.plugin.value
        and first.version.value == second.version.value
        and first.installed_locator.value == second.installed_locator.value
        and first.auth_policy.value == second.auth_policy.value
        and first.digest.value == second.digest.value
    )


def _plugin_removal_matches(payload: CodexPluginRemove, identity: OracleIdentity) -> bool:
    return (
        payload.pluginId == identity.plugin_id
        and payload.name == identity.plugin_name
        and payload.marketplaceName == identity.marketplace_name
    )


def _marketplace_removal_matches(payload: CodexMarketplaceRemove, identity: OracleIdentity) -> bool:
    return payload.marketplaceName == identity.marketplace_name and payload.installedRoot == identity.marketplace_root


def _operation_failure(
    manifest: CodexCompensationPortManifest,
    operation: CodexCompensationPortOperation,
    reason: CodexCompensationPortFailureReason,
) -> CodexCompensationPortOperationFailed:
    return CodexCompensationPortOperationFailed(manifest=manifest, operation=operation, reason=reason)


def _factory_rejected(reason: CodexCompensationOracleAdapterRejectReason) -> CodexCompensationOracleAdapterRejected:
    return CodexCompensationOracleAdapterRejected(reason=reason)
