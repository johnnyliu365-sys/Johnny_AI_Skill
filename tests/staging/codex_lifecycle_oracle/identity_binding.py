"""Pure request-to-oracle identity binding for the E1 staging seam."""

from __future__ import annotations

from enum import Enum
import ntpath
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, ValidationError

from library.local_orchestration.codex_registration_port import (
    CodexRegistrationPortRequest,
    CodexRegistrationPortValueRejected,
    CodexRegistrationPortValueRejectReason,
    revalidate_registration_port_request,
)
from library.local_orchestration.contracts import OwnedRelativePath
from tests.staging.codex_lifecycle_oracle.contracts import OracleIdentity


FIXED_STAGING_LOGICAL_ROOT = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow"
STAGING_PLUGIN_SOURCE = "staging-fixture-source"
STAGING_PLUGIN_INSTALL_POLICY = "staging-fixture-install-policy"

_PATH_VALIDATION_MARKETPLACE = "oracle-validation-market"
_PATH_VALIDATION_PLUGIN_ID = "oracle-validation-plugin"
_PATH_VALIDATION_PLUGIN_NAME = "oracle-validation-plugin-name"
_PATH_VALIDATION_VERSION = "0.0.0"
_PATH_VALIDATION_AUTH_POLICY = "staging-validation-policy"


class _StrictModel(BaseModel):
    """Immutable, closed results at the staging-only identity boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class OracleIdentityBindingRejectReason(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    REQUEST_MISMATCH = "REQUEST_MISMATCH"
    LOGICAL_IDENTITY_INVALID = "LOGICAL_IDENTITY_INVALID"


class OracleIdentityBindingRejected(_StrictModel):
    status: Literal["ORACLE_IDENTITY_REJECTED"] = "ORACLE_IDENTITY_REJECTED"
    reason: OracleIdentityBindingRejectReason


class OracleIdentityBound(_StrictModel):
    status: Literal["ORACLE_IDENTITY_BOUND"] = "ORACLE_IDENTITY_BOUND"
    request: CodexRegistrationPortRequest
    identity: OracleIdentity


OracleIdentityBindingResult: TypeAlias = OracleIdentityBound | OracleIdentityBindingRejected


def bind_oracle_identity(value: object) -> OracleIdentityBindingResult:
    """Rebuild one exact request and derive its deterministic staging identity."""

    rebuilt = revalidate_registration_port_request(value)
    if isinstance(rebuilt, CodexRegistrationPortValueRejected):
        return _rejected_request(rebuilt.reason)
    if type(rebuilt) is not CodexRegistrationPortRequest:
        return _rejected(OracleIdentityBindingRejectReason.INVALID_REQUEST)
    if not _has_no_extra_request_state(value):
        return _rejected(OracleIdentityBindingRejectReason.INVALID_REQUEST)

    marketplace_root = _logical_path(rebuilt.source_locator)
    plugin_installed_path = _logical_path(rebuilt.installed_locator)
    if not _is_e0_logical_path(marketplace_root) or not _is_e0_logical_path(plugin_installed_path):
        return _rejected(OracleIdentityBindingRejectReason.LOGICAL_IDENTITY_INVALID)
    try:
        identity = OracleIdentity(
            marketplace_name=rebuilt.preflight.marketplace.value,
            marketplace_root=marketplace_root,
            plugin_id=rebuilt.expected_plugin_id.value,
            plugin_name=rebuilt.preflight.plugin.value,
            plugin_version=rebuilt.expected_version.value,
            plugin_source=STAGING_PLUGIN_SOURCE,
            plugin_install_policy=STAGING_PLUGIN_INSTALL_POLICY,
            plugin_auth_policy=rebuilt.expected_auth_policy.value,
            plugin_installed_path=plugin_installed_path,
        )
        return OracleIdentityBound(request=rebuilt, identity=identity)
    except (ValidationError, ValueError):
        return _rejected(OracleIdentityBindingRejectReason.LOGICAL_IDENTITY_INVALID)


def _logical_path(locator: OwnedRelativePath) -> str:
    """Join only a revalidated owned locator to the fixed logical staging root."""

    return ntpath.join(FIXED_STAGING_LOGICAL_ROOT, locator.value.replace("/", "\\"))


def _has_no_extra_request_state(value: object) -> bool:
    """Use strict Pydantic revalidation to reject injected undeclared request state."""

    try:
        CodexRegistrationPortRequest.model_validate(value)
    except (AttributeError, ValidationError, ValueError):
        return False
    return True


def _is_e0_logical_path(value: str) -> bool:
    """Use the public E0 identity contract to validate one logical path."""

    try:
        OracleIdentity(
            marketplace_name=_PATH_VALIDATION_MARKETPLACE,
            marketplace_root=FIXED_STAGING_LOGICAL_ROOT,
            plugin_id=_PATH_VALIDATION_PLUGIN_ID,
            plugin_name=_PATH_VALIDATION_PLUGIN_NAME,
            plugin_version=_PATH_VALIDATION_VERSION,
            plugin_source=STAGING_PLUGIN_SOURCE,
            plugin_install_policy=STAGING_PLUGIN_INSTALL_POLICY,
            plugin_auth_policy=_PATH_VALIDATION_AUTH_POLICY,
            plugin_installed_path=value,
        )
    except (ValidationError, ValueError):
        return False
    return True


def _rejected_request(
    reason: CodexRegistrationPortValueRejectReason,
) -> OracleIdentityBindingRejected:
    if reason is CodexRegistrationPortValueRejectReason.REQUEST_MISMATCH:
        return _rejected(OracleIdentityBindingRejectReason.REQUEST_MISMATCH)
    return _rejected(OracleIdentityBindingRejectReason.INVALID_REQUEST)


def _rejected(reason: OracleIdentityBindingRejectReason) -> OracleIdentityBindingRejected:
    return OracleIdentityBindingRejected(reason=reason)
