"""Closed staging adapter from the persisted oracle to the registration port."""

from __future__ import annotations

from enum import Enum
import ntpath
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.codex_command_attempts import (
    CodexCommandStartState,
    CodexCommandTarget,
    CodexMarketplaceAddConfirmed,
    CodexPluginAddConfirmed,
    CodexPreStartFailure,
    CodexPreStartFailureReason,
    CodexStartedFailure,
    CodexStartedFailureReason,
)
from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexMarketplaceAddObservation,
    CodexObservedAbsolutePath,
    CodexPluginAddObservation,
    CodexPluginId,
    CodexRegistrationProof,
    CodexRegistrationProofPortFailure,
    CodexRegistrationProofRequest,
)
from library.local_orchestration.codex_registration_port import (
    CodexFreshPreflightAccepted,
    CodexFreshPreflightRejected,
    CodexFreshPreflightResult,
    CodexMarketplaceAddResult,
    CodexMarketplaceAddSucceeded,
    CodexPluginAddResult,
    CodexPluginAddSucceeded,
    CodexRegistrationCommandFailed,
    CodexRegistrationPortRequest,
    CodexRegistrationPortValueRejected,
    revalidate_marketplace_add_result,
    revalidate_plugin_add_result,
    revalidate_registration_port_request,
)
from library.local_orchestration.contracts import CANONICAL_INSTALL_ROOT
from library.local_orchestration.host_contracts import (
    CodexBlockReason,
    CodexCliVersion,
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceName,
    CodexPluginEntry,
    CodexPluginList,
    CodexPluginName,
    CodexPreflightEligible,
)
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceAdd,
    CodexPluginAdd,
    CodexProtocolAccepted,
    CodexProtocolSurface,
    CodexVersionObservation,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    revalidate_lease,
)

from .contracts import OracleAction, OracleBlocked, OracleCommand, OracleCompleted, OracleIdentity, OracleRunResult
from .identity_binding import (
    FIXED_STAGING_LOGICAL_ROOT,
    OracleIdentityBound,
    bind_oracle_identity,
)
from .oracle import CodexLifecycleOracle


class _StrictModel(BaseModel):
    """Immutable metadata-only values at the adapter admission boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class OracleRegistrationAdapterRejectReason(str, Enum):
    """Finite reasons an adapter cannot be admitted before an oracle command."""

    INVALID_LEASE = "INVALID_LEASE"
    INVALID_ORACLE = "INVALID_ORACLE"
    INVALID_BINDING = "INVALID_BINDING"
    LOGICAL_ROOT_MISMATCH = "LOGICAL_ROOT_MISMATCH"


class OracleRegistrationAdapterRejected(_StrictModel):
    """Closed, metadata-only adapter admission rejection."""

    status: Literal["ORACLE_ADAPTER_BLOCKED"] = "ORACLE_ADAPTER_BLOCKED"
    reason: OracleRegistrationAdapterRejectReason


OracleRegistrationAdapterAdmission: TypeAlias = (
    "CodexRegistrationOracleAdapter | OracleRegistrationAdapterRejected"
)


def create_oracle_registration_adapter(
    lease: object,
    oracle: object,
    bound: object,
) -> OracleRegistrationAdapterAdmission:
    """Admit one exact live lease, oracle and E1 identity without side effects."""

    rebuilt_lease = _rebuild_lease(lease)
    if rebuilt_lease is None:
        return _rejected(OracleRegistrationAdapterRejectReason.INVALID_LEASE)
    if type(oracle) is not CodexLifecycleOracle:
        return _rejected(OracleRegistrationAdapterRejectReason.INVALID_ORACLE)
    rebuilt_bound = _rebuild_identity_bound(bound)
    if rebuilt_bound is None:
        return _rejected(OracleRegistrationAdapterRejectReason.INVALID_BINDING)
    if ntpath.expandvars(CANONICAL_INSTALL_ROOT) != FIXED_STAGING_LOGICAL_ROOT:
        return _rejected(OracleRegistrationAdapterRejectReason.LOGICAL_ROOT_MISMATCH)
    return CodexRegistrationOracleAdapter(rebuilt_lease, oracle, rebuilt_bound)


class CodexRegistrationOracleAdapter:
    """Four exact port operations backed only by fresh persisted oracle responses."""

    __slots__ = ("_lease", "_oracle", "_bound", "_marketplace", "_plugin")

    def __init__(
        self,
        lease: EnvironmentLease,
        oracle: CodexLifecycleOracle,
        bound: OracleIdentityBound,
    ) -> None:
        self._lease = lease
        self._oracle = oracle
        self._bound = bound
        self._marketplace: CodexMarketplaceAddSucceeded | None = None
        self._plugin: CodexPluginAddSucceeded | None = None

    def fresh_preflight(self, request: CodexRegistrationPortRequest) -> CodexFreshPreflightResult:
        """Read the persisted VERSION surface before reporting fresh eligibility."""

        current = self._exact_request(request)
        if current is None:
            return CodexFreshPreflightRejected(request=self._bound.request, reason=CodexBlockReason.INVALID_INPUT)
        response = self._run(OracleAction.VERSION)
        version = _exact_version_response(response)
        if version is None or version.value != current.expected_version.value:
            return CodexFreshPreflightRejected(request=current, reason=CodexBlockReason.UNSUPPORTED_CLI)
        return CodexFreshPreflightAccepted(request=current, eligible=CodexPreflightEligible(version=version))

    def add_marketplace(self, request: CodexRegistrationPortRequest) -> CodexMarketplaceAddResult:
        """Run only the current marketplace add and retain an exact accepted observation."""

        current, reason = self._request_or_failure(request)
        if current is None:
            return _pre_start_failure(self._bound.request, CodexCommandTarget.MARKETPLACE_ADD, reason)
        response = self._run(OracleAction.MARKETPLACE_ADD)
        payload = _exact_marketplace_add_response(response)
        if payload is None:
            return _started_failure(current, CodexCommandTarget.MARKETPLACE_ADD, CodexStartedFailureReason.MALFORMED_RESPONSE)
        if (
            payload.marketplaceName != self._bound.identity.marketplace_name
            or payload.installedRoot != self._bound.identity.marketplace_root
        ):
            return _started_failure(current, CodexCommandTarget.MARKETPLACE_ADD, CodexStartedFailureReason.IDENTITY_MISMATCH)
        candidate = CodexMarketplaceAddSucceeded(
            request=current,
            confirmed=CodexMarketplaceAddConfirmed(
                target=CodexCommandTarget.MARKETPLACE_ADD,
                start_state=CodexCommandStartState.STARTED,
                already_added=payload.alreadyAdded,
            ),
            observation=CodexMarketplaceAddObservation(
                marketplace_name=CodexMarketplaceName(value=payload.marketplaceName),
                installed_root=CodexObservedAbsolutePath(value=payload.installedRoot),
                already_added=payload.alreadyAdded,
            ),
        )
        validated = revalidate_marketplace_add_result(candidate, self._bound.request)
        if type(validated) is not CodexMarketplaceAddSucceeded:
            return _started_failure(current, CodexCommandTarget.MARKETPLACE_ADD, CodexStartedFailureReason.IDENTITY_MISMATCH)
        self._marketplace = validated
        return validated

    def add_plugin(self, request: CodexRegistrationPortRequest) -> CodexPluginAddResult:
        """Run plugin add only after this adapter retained the exact marketplace add."""

        current, reason = self._request_or_failure(request)
        if current is None:
            return _pre_start_failure(self._bound.request, CodexCommandTarget.PLUGIN_ADD, reason)
        if self._marketplace is None:
            return _pre_start_failure(
                current,
                CodexCommandTarget.PLUGIN_ADD,
                CodexPreStartFailureReason.INVALID_REQUEST,
            )
        response = self._run(OracleAction.PLUGIN_ADD)
        payload = _exact_plugin_add_response(response)
        if payload is None:
            return _started_failure(current, CodexCommandTarget.PLUGIN_ADD, CodexStartedFailureReason.MALFORMED_RESPONSE)
        if not _plugin_payload_matches_identity(payload, self._bound.identity):
            return _started_failure(current, CodexCommandTarget.PLUGIN_ADD, CodexStartedFailureReason.IDENTITY_MISMATCH)
        candidate = CodexPluginAddSucceeded(
            request=current,
            confirmed=CodexPluginAddConfirmed(
                target=CodexCommandTarget.PLUGIN_ADD,
                start_state=CodexCommandStartState.STARTED,
            ),
            observation=CodexPluginAddObservation(
                plugin_id=CodexPluginId(value=payload.pluginId),
                name=CodexPluginName(value=payload.name),
                marketplace_name=CodexMarketplaceName(value=payload.marketplaceName),
                version=CodexCliVersion(value=payload.version),
                installed_path=CodexObservedAbsolutePath(value=payload.installedPath),
                auth_policy=CodexAuthPolicy(value=payload.authPolicy),
            ),
        )
        validated = revalidate_plugin_add_result(candidate, self._bound.request)
        if type(validated) is not CodexPluginAddSucceeded:
            return _started_failure(current, CodexCommandTarget.PLUGIN_ADD, CodexStartedFailureReason.IDENTITY_MISMATCH)
        self._plugin = validated
        return validated

    def prove(self, request: CodexRegistrationProofRequest) -> CodexRegistrationProof:
        """Return a proof only after exact same-instance adds and fresh exact lists."""

        expected = self._proof_request()
        if expected is None or not _proof_requests_match(request, expected):
            raise CodexRegistrationProofPortFailure()
        marketplace_list = _exact_marketplace_list_response(self._run(OracleAction.MARKETPLACE_LIST))
        plugin_list = _exact_plugin_list_response(self._run(OracleAction.PLUGIN_LIST))
        if marketplace_list is None or plugin_list is None:
            raise CodexRegistrationProofPortFailure()
        if not _fresh_lists_match(marketplace_list, plugin_list, self._bound.identity):
            raise CodexRegistrationProofPortFailure()
        return CodexRegistrationProof(
            installation_id=expected.preflight.installation_id,
            root=expected.preflight.root,
            marketplace=expected.preflight.marketplace,
            plugin_id=expected.plugin_observation.plugin_id,
            plugin_name=expected.plugin_observation.name,
            version=expected.version,
            source_locator=expected.source_locator,
            installed_locator=expected.installed_locator,
            auth_policy=expected.expected_auth_policy,
            digest=expected.digest,
            observed_marketplace_root=expected.marketplace_observation.installed_root,
            observed_marketplace_already_added=expected.marketplace_observation.already_added,
            observed_plugin_path=expected.plugin_observation.installed_path,
        )

    def _exact_request(self, request: object) -> CodexRegistrationPortRequest | None:
        rebuilt = revalidate_registration_port_request(request)
        if type(rebuilt) is not CodexRegistrationPortRequest:
            return None
        if not _requests_match(rebuilt, self._bound.request):
            return None
        return rebuilt

    def _request_or_failure(
        self,
        request: object,
    ) -> tuple[CodexRegistrationPortRequest | None, CodexPreStartFailureReason]:
        rebuilt = revalidate_registration_port_request(request)
        if type(rebuilt) is not CodexRegistrationPortRequest:
            return None, CodexPreStartFailureReason.INVALID_REQUEST
        if not _requests_match(rebuilt, self._bound.request):
            return None, CodexPreStartFailureReason.REQUEST_MISMATCH
        return rebuilt, CodexPreStartFailureReason.INVALID_REQUEST

    def _run(self, action: OracleAction) -> OracleRunResult:
        return self._oracle.run(self._lease, OracleCommand(action=action, identity=self._bound.identity))

    def _proof_request(self) -> CodexRegistrationProofRequest | None:
        if self._marketplace is None or self._plugin is None:
            return None
        try:
            return CodexRegistrationProofRequest(
                preflight=self._bound.request.preflight,
                version=self._bound.request.expected_version,
                marketplace_observation=self._marketplace.observation,
                plugin_observation=self._plugin.observation,
                source_locator=self._bound.request.source_locator,
                installed_locator=self._bound.request.installed_locator,
                digest=self._bound.request.digest,
                expected_auth_policy=self._bound.request.expected_auth_policy,
            )
        except (TypeError, ValidationError, ValueError):
            return None


def _rebuild_lease(value: object) -> EnvironmentLease | None:
    if type(value) is not EnvironmentLease:
        return None
    rebuilt = revalidate_lease(value)
    if type(rebuilt) is not EnvironmentLease:
        return None
    return rebuilt


def _rebuild_identity_bound(value: object) -> OracleIdentityBound | None:
    if type(value) is not OracleIdentityBound:
        return None
    rebound = bind_oracle_identity(value.request)
    if type(rebound) is not OracleIdentityBound:
        return None
    if not _requests_match(rebound.request, value.request):
        return None
    if not _identities_match(rebound.identity, value.identity):
        return None
    return rebound


def _rejected(reason: OracleRegistrationAdapterRejectReason) -> OracleRegistrationAdapterRejected:
    return OracleRegistrationAdapterRejected(reason=reason)


def _requests_match(
    first: CodexRegistrationPortRequest,
    second: CodexRegistrationPortRequest,
) -> bool:
    return (
        first.preflight.installation_id.value == second.preflight.installation_id.value
        and first.preflight.root.value == second.preflight.root.value
        and first.preflight.marketplace.value == second.preflight.marketplace.value
        and first.preflight.plugin.value == second.preflight.plugin.value
        and first.preflight.marketplace_source.value == second.preflight.marketplace_source.value
        and first.attempt_id.value == second.attempt_id.value
        and first.expected_version.value == second.expected_version.value
        and first.source_locator.value == second.source_locator.value
        and first.installed_locator.value == second.installed_locator.value
        and first.digest.value == second.digest.value
        and first.expected_auth_policy.value == second.expected_auth_policy.value
        and first.expected_plugin_id.value == second.expected_plugin_id.value
    )


def _identities_match(first: OracleIdentity, second: OracleIdentity) -> bool:
    return (
        first.marketplace_name == second.marketplace_name
        and first.marketplace_root == second.marketplace_root
        and first.plugin_id == second.plugin_id
        and first.plugin_name == second.plugin_name
        and first.plugin_version == second.plugin_version
        and first.plugin_source == second.plugin_source
        and first.plugin_install_policy == second.plugin_install_policy
        and first.plugin_auth_policy == second.plugin_auth_policy
        and first.plugin_installed_path == second.plugin_installed_path
    )


def _pre_start_failure(
    request: CodexRegistrationPortRequest,
    target: CodexCommandTarget,
    reason: CodexPreStartFailureReason,
) -> CodexRegistrationCommandFailed:
    return CodexRegistrationCommandFailed(
        request=request,
        failure=CodexPreStartFailure(target=target, reason=reason, start_state=CodexCommandStartState.NOT_STARTED),
    )


def _started_failure(
    request: CodexRegistrationPortRequest,
    target: CodexCommandTarget,
    reason: CodexStartedFailureReason,
) -> CodexRegistrationCommandFailed:
    return CodexRegistrationCommandFailed(
        request=request,
        failure=CodexStartedFailure(target=target, reason=reason, start_state=CodexCommandStartState.STARTED),
    )


def _exact_version_response(value: OracleRunResult) -> CodexCliVersion | None:
    response = _rebuild_response(value, CodexProtocolSurface.VERSION, CodexVersionObservation)
    if response is None:
        return None
    payload = response.payload
    if type(payload) is not CodexVersionObservation:
        return None
    try:
        return CodexCliVersion(value=payload.version)
    except (TypeError, ValidationError, ValueError):
        return None


def _exact_marketplace_add_response(value: OracleRunResult) -> CodexMarketplaceAdd | None:
    response = _rebuild_response(value, CodexProtocolSurface.MARKETPLACE_ADD, CodexMarketplaceAdd)
    if response is None or type(response.payload) is not CodexMarketplaceAdd:
        return None
    return response.payload


def _exact_plugin_add_response(value: OracleRunResult) -> CodexPluginAdd | None:
    response = _rebuild_response(value, CodexProtocolSurface.PLUGIN_ADD, CodexPluginAdd)
    if response is None or type(response.payload) is not CodexPluginAdd:
        return None
    return response.payload


def _exact_marketplace_list_response(value: OracleRunResult) -> CodexMarketplaceList | None:
    response = _rebuild_response(value, CodexProtocolSurface.MARKETPLACE_LIST, CodexMarketplaceList)
    if response is None or type(response.payload) is not CodexMarketplaceList:
        return None
    return response.payload


def _exact_plugin_list_response(value: OracleRunResult) -> CodexPluginList | None:
    response = _rebuild_response(value, CodexProtocolSurface.PLUGIN_LIST, CodexPluginList)
    if response is None or type(response.payload) is not CodexPluginList:
        return None
    return response.payload


def _rebuild_response(
    value: OracleRunResult,
    surface: CodexProtocolSurface,
    payload_type: type[CodexVersionObservation]
    | type[CodexMarketplaceAdd]
    | type[CodexPluginAdd]
    | type[CodexMarketplaceList]
    | type[CodexPluginList],
) -> CodexProtocolAccepted | None:
    if type(value) is not OracleCompleted:
        return None
    response = value.response
    if type(response) is not CodexProtocolAccepted:
        return None
    try:
        rebuilt = CodexProtocolAccepted.model_validate_json(response.model_dump_json(warnings=False))
    except (AttributeError, TypeError, ValidationError, ValueError):
        return None
    if type(rebuilt) is not CodexProtocolAccepted or rebuilt.surface is not surface:
        return None
    if type(rebuilt.payload) is not payload_type:
        return None
    return rebuilt


def _plugin_payload_matches_identity(payload: CodexPluginAdd, identity: OracleIdentity) -> bool:
    return (
        payload.pluginId == identity.plugin_id
        and payload.name == identity.plugin_name
        and payload.marketplaceName == identity.marketplace_name
        and payload.version == identity.plugin_version
        and payload.installedPath == identity.plugin_installed_path
        and payload.authPolicy == identity.plugin_auth_policy
    )


def _proof_requests_match(value: object, expected: CodexRegistrationProofRequest) -> bool:
    if type(value) is not CodexRegistrationProofRequest:
        return False
    try:
        rebuilt = CodexRegistrationProofRequest.model_validate_json(value.model_dump_json(warnings=False))
    except (AttributeError, TypeError, ValidationError, ValueError):
        return False
    return (
        rebuilt.preflight == expected.preflight
        and rebuilt.version == expected.version
        and rebuilt.marketplace_observation == expected.marketplace_observation
        and rebuilt.plugin_observation == expected.plugin_observation
        and rebuilt.source_locator == expected.source_locator
        and rebuilt.installed_locator == expected.installed_locator
        and rebuilt.digest == expected.digest
        and rebuilt.expected_auth_policy == expected.expected_auth_policy
    )


def _fresh_lists_match(
    marketplaces: CodexMarketplaceList,
    plugins: CodexPluginList,
    identity: OracleIdentity,
) -> bool:
    if len(marketplaces.marketplaces) != 1 or len(plugins.installed) != 1 or plugins.available:
        return False
    marketplace = marketplaces.marketplaces[0]
    plugin = plugins.installed[0]
    return _marketplace_entry_matches(marketplace, identity) and _plugin_entry_matches(plugin, identity)


def _marketplace_entry_matches(value: object, identity: OracleIdentity) -> bool:
    if type(value) is not CodexMarketplaceEntry:
        return False
    return value.name == identity.marketplace_name and value.root == identity.marketplace_root


def _plugin_entry_matches(value: object, identity: OracleIdentity) -> bool:
    if type(value) is not CodexPluginEntry:
        return False
    return (
        value.pluginId == identity.plugin_id
        and value.name == identity.plugin_name
        and value.marketplaceName == identity.marketplace_name
        and value.version == identity.plugin_version
        and value.installed is True
        and value.enabled is True
        and value.source == identity.plugin_source
        and value.installPolicy == identity.plugin_install_policy
        and value.authPolicy == identity.plugin_auth_policy
    )
