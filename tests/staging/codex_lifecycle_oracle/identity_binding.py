"""Pure request-to-oracle identity binding for the E1 staging seam."""

from __future__ import annotations

from enum import Enum
import ntpath
from typing import Literal, TypeAlias, cast

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

_REQUEST_STATE_FIELDS: tuple[str, ...] = (
    "preflight",
    "attempt_id",
    "expected_version",
    "source_locator",
    "installed_locator",
    "digest",
    "expected_auth_policy",
    "expected_plugin_id",
)
_PREFLIGHT_STATE_FIELDS: tuple[str, ...] = (
    "installation_id",
    "root",
    "marketplace",
    "plugin",
    "marketplace_source",
)
_VALUE_STATE_FIELDS: tuple[str, ...] = ("value",)


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
    if type(value) is not CodexRegistrationPortRequest:
        return _rejected(OracleIdentityBindingRejectReason.INVALID_REQUEST)
    if not _has_exact_original_request_state(value):
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


def _has_exact_original_request_state(value: CodexRegistrationPortRequest) -> bool:
    """Prove every original exact Pydantic node has only its fixed declared state."""

    preflight = value.preflight
    return (
        _has_exact_model_state(value, _REQUEST_STATE_FIELDS)
        and _has_exact_model_state(preflight, _PREFLIGHT_STATE_FIELDS)
        and _has_exact_model_state(preflight.installation_id, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(preflight.root, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(preflight.marketplace, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(preflight.plugin, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(preflight.marketplace_source, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.attempt_id, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.expected_version, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.source_locator, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.installed_locator, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.digest, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.expected_auth_policy, _VALUE_STATE_FIELDS)
        and _has_exact_model_state(value.expected_plugin_id, _VALUE_STATE_FIELDS)
    )


def _has_exact_model_state(value: BaseModel, expected_fields: tuple[str, ...]) -> bool:
    """Read fixed Pydantic storage without inspecting caller-defined members."""

    state: object = object.__getattribute__(value, "__dict__")
    extras: object = object.__getattribute__(value, "__pydantic_extra__")
    private: object = object.__getattribute__(value, "__pydantic_private__")
    fields_set: object = object.__getattribute__(value, "__pydantic_fields_set__")
    if type(state) is not dict or extras is not None or private is not None or type(fields_set) is not set:
        return False
    return _has_exact_dict_keys(cast(dict[object, object], state), expected_fields) and _has_exact_set_keys(
        cast(set[object], fields_set),
        expected_fields,
    )


def _has_exact_dict_keys(values: dict[object, object], expected_fields: tuple[str, ...]) -> bool:
    """Check a built-in state mapping after rejecting all non-string caller keys."""

    if len(values) != len(expected_fields):
        return False
    for key in values:
        if type(key) is not str:
            return False
    for expected in expected_fields:
        if expected not in values:
            return False
    return True


def _has_exact_set_keys(values: set[object], expected_fields: tuple[str, ...]) -> bool:
    """Check the fixed Pydantic field-set with no caller equality or hash protocol."""

    if len(values) != len(expected_fields):
        return False
    for key in values:
        if type(key) is not str:
            return False
    for expected in expected_fields:
        if expected not in values:
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
