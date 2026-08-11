"""Closed, descriptor-free admission for a five-operation Codex compensation port."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import CodeType, FunctionType, MethodType
from typing import Callable, Final, Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict

from .codex_registration_contracts import CodexAuthPolicy, CodexPluginId
from .contracts import ArtifactDigest, InstallRoot, InstallationId, OwnedRelativePath
from .host_contracts import CodexCliVersion, CodexMarketplaceList, CodexMarketplaceName, CodexPluginList, CodexPluginName


class _StrictModel(BaseModel):
    """Frozen metadata-only values at the closed capability boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, revalidate_instances="always")


class CodexCompensationPortManifest(_StrictModel):
    """Exact authority that every later compensation operation must receive."""

    installation_id: InstallationId
    root: InstallRoot
    marketplace: CodexMarketplaceName
    marketplace_source: OwnedRelativePath
    plugin_id: CodexPluginId
    plugin: CodexPluginName
    version: CodexCliVersion
    installed_locator: OwnedRelativePath
    auth_policy: CodexAuthPolicy
    digest: ArtifactDigest


class CodexCompensationPortRequest(_StrictModel):
    """The single strongly typed argument for each admitted port operation."""

    manifest: CodexCompensationPortManifest


class CodexPluginRemovalProof(_StrictModel):
    """Typed plugin-removal result for later exact composition."""

    manifest: CodexCompensationPortManifest
    status: Literal["REMOVED"]


class CodexMarketplaceRemovalProof(_StrictModel):
    """Typed marketplace-removal result for later exact composition."""

    manifest: CodexCompensationPortManifest
    status: Literal["REMOVED"]


class CodexInstalledPathAbsenceProof(_StrictModel):
    """Typed path-absence result for later exact composition."""

    manifest: CodexCompensationPortManifest
    absent: Literal[True]


CodexRemovePluginOperation: TypeAlias = Callable[[CodexCompensationPortRequest], CodexPluginRemovalProof]
CodexRemoveMarketplaceOperation: TypeAlias = Callable[[CodexCompensationPortRequest], CodexMarketplaceRemovalProof]
CodexListPluginsOperation: TypeAlias = Callable[[CodexCompensationPortRequest], CodexPluginList]
CodexListMarketplacesOperation: TypeAlias = Callable[[CodexCompensationPortRequest], CodexMarketplaceList]
CodexProveInstalledPathAbsentOperation: TypeAlias = Callable[[CodexCompensationPortRequest], CodexInstalledPathAbsenceProof]


class CodexCompensationPortRejectReason(str, Enum):
    """Finite internal reasons; their public status remains uniformly INVALID_PORT."""

    INVALID_CANDIDATE = "INVALID_CANDIDATE"
    MISSING_OPERATION = "MISSING_OPERATION"
    NON_PLAIN_FUNCTION = "NON_PLAIN_FUNCTION"
    PROPERTY_OPERATION = "PROPERTY_OPERATION"
    STATIC_METHOD_OPERATION = "STATIC_METHOD_OPERATION"
    CLASS_METHOD_OPERATION = "CLASS_METHOD_OPERATION"
    ZERO_REQUEST_ARGUMENTS = "ZERO_REQUEST_ARGUMENTS"
    TWO_REQUEST_ARGUMENTS = "TWO_REQUEST_ARGUMENTS"
    VARIADIC_ARGUMENTS = "VARIADIC_ARGUMENTS"
    REQUIRED_KEYWORD_ARGUMENTS = "REQUIRED_KEYWORD_ARGUMENTS"
    DEFAULTED_ARGUMENTS = "DEFAULTED_ARGUMENTS"


class CodexCompensationPortRejected(_StrictModel):
    """Metadata-only result for every failed capability admission."""

    status: Literal["INVALID_PORT"]
    reason: CodexCompensationPortRejectReason


class CodexCompensationPortAdmitted(_StrictModel):
    """Safe serialization view; it never exposes raw adapter functions."""

    status: Literal["ADMITTED"]
    operation_count: Literal[5]


class _CapabilityToken:
    """Private constructor authority for a capability created by this factory only."""


_CAPABILITY_TOKEN: Final[_CapabilityToken] = _CapabilityToken()
_MISSING_OPERATION: Final[object] = object()
_FUNCTION_VARARGS_FLAG: Final[int] = 0x04
_FUNCTION_VARKWARGS_FLAG: Final[int] = 0x08


@dataclass(frozen=True, slots=True, init=False)
class CodexCompensationPortCapability:
    """Five explicitly bound operations admitted without resolving adapter members."""

    status: Literal["ADMITTED"]
    remove_plugin: CodexRemovePluginOperation
    remove_marketplace: CodexRemoveMarketplaceOperation
    list_plugins: CodexListPluginsOperation
    list_marketplaces: CodexListMarketplacesOperation
    prove_installed_path_absent: CodexProveInstalledPathAbsentOperation

    def __init__(
        self,
        token: _CapabilityToken,
        remove_plugin: CodexRemovePluginOperation,
        remove_marketplace: CodexRemoveMarketplaceOperation,
        list_plugins: CodexListPluginsOperation,
        list_marketplaces: CodexListMarketplacesOperation,
        prove_installed_path_absent: CodexProveInstalledPathAbsentOperation,
    ) -> None:
        if token is not _CAPABILITY_TOKEN:
            raise TypeError("capability construction requires factory authority")
        object.__setattr__(self, "status", "ADMITTED")
        object.__setattr__(self, "remove_plugin", remove_plugin)
        object.__setattr__(self, "remove_marketplace", remove_marketplace)
        object.__setattr__(self, "list_plugins", list_plugins)
        object.__setattr__(self, "list_marketplaces", list_marketplaces)
        object.__setattr__(self, "prove_installed_path_absent", prove_installed_path_absent)

    def metadata(self) -> CodexCompensationPortAdmitted:
        """Return only public admission metadata, never bound callable internals."""

        return CodexCompensationPortAdmitted(status="ADMITTED", operation_count=5)


CodexCompensationPortAdmission: TypeAlias = CodexCompensationPortCapability | CodexCompensationPortRejected


class _OperationName(str, Enum):
    REMOVE_PLUGIN = "remove_plugin"
    REMOVE_MARKETPLACE = "remove_marketplace"
    LIST_PLUGINS = "list_plugins"
    LIST_MARKETPLACES = "list_marketplaces"
    PROVE_INSTALLED_PATH_ABSENT = "prove_installed_path_absent"


def admit_codex_compensation_port(candidate: object) -> CodexCompensationPortAdmission:
    """Admit only exact plain class methods without dynamic candidate lookup or execution."""

    if candidate is None:
        return _rejected(CodexCompensationPortRejectReason.INVALID_CANDIDATE)
    candidate_class_value = object.__getattribute__(candidate, "__class__")
    if not isinstance(candidate_class_value, type):
        return _rejected(CodexCompensationPortRejectReason.INVALID_CANDIDATE)
    candidate_class = cast(type[object], candidate_class_value)
    if candidate_class in (str, tuple, list, dict):
        return _rejected(CodexCompensationPortRejectReason.INVALID_CANDIDATE)
    remove_plugin = _admit_operation(candidate_class, _OperationName.REMOVE_PLUGIN)
    if isinstance(remove_plugin, CodexCompensationPortRejected):
        return remove_plugin
    remove_marketplace = _admit_operation(candidate_class, _OperationName.REMOVE_MARKETPLACE)
    if isinstance(remove_marketplace, CodexCompensationPortRejected):
        return remove_marketplace
    list_plugins = _admit_operation(candidate_class, _OperationName.LIST_PLUGINS)
    if isinstance(list_plugins, CodexCompensationPortRejected):
        return list_plugins
    list_marketplaces = _admit_operation(candidate_class, _OperationName.LIST_MARKETPLACES)
    if isinstance(list_marketplaces, CodexCompensationPortRejected):
        return list_marketplaces
    prove_absent = _admit_operation(candidate_class, _OperationName.PROVE_INSTALLED_PATH_ABSENT)
    if isinstance(prove_absent, CodexCompensationPortRejected):
        return prove_absent
    return CodexCompensationPortCapability(
        _CAPABILITY_TOKEN,
        cast(CodexRemovePluginOperation, MethodType(remove_plugin, candidate)),
        cast(CodexRemoveMarketplaceOperation, MethodType(remove_marketplace, candidate)),
        cast(CodexListPluginsOperation, MethodType(list_plugins, candidate)),
        cast(CodexListMarketplacesOperation, MethodType(list_marketplaces, candidate)),
        cast(CodexProveInstalledPathAbsentOperation, MethodType(prove_absent, candidate)),
    )


def _admit_operation(
    candidate_class: type[object],
    operation: _OperationName,
) -> FunctionType | CodexCompensationPortRejected:
    """Locate exactly one raw class-dictionary function without descriptor resolution."""

    raw_member = _raw_member_from_mro(candidate_class, operation)
    if raw_member is _MISSING_OPERATION:
        return _rejected(CodexCompensationPortRejectReason.MISSING_OPERATION)
    if isinstance(raw_member, property):
        return _rejected(CodexCompensationPortRejectReason.PROPERTY_OPERATION)
    if isinstance(raw_member, staticmethod):
        return _rejected(CodexCompensationPortRejectReason.STATIC_METHOD_OPERATION)
    if isinstance(raw_member, classmethod):
        return _rejected(CodexCompensationPortRejectReason.CLASS_METHOD_OPERATION)
    if not isinstance(raw_member, FunctionType):
        return _rejected(CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION)
    shape_reason = _plain_function_shape_reason(raw_member)
    if shape_reason is not None:
        return _rejected(shape_reason)
    return raw_member


def _raw_member_from_mro(candidate_class: type[object], operation: _OperationName) -> object:
    """Read class dictionaries through built-ins so caller descriptors remain inert."""

    mro_value = type.__getattribute__(candidate_class, "__mro__")
    if not isinstance(mro_value, tuple):
        return _MISSING_OPERATION
    for owner_value in mro_value:
        if not isinstance(owner_value, type):
            return _MISSING_OPERATION
        owner = cast(type[object], owner_value)
        dictionary_value = type.__getattribute__(owner, "__dict__")
        if not isinstance(dictionary_value, Mapping):
            return _MISSING_OPERATION
        dictionary = cast(Mapping[str, object], dictionary_value)
        if operation.value in dictionary:
            return dictionary[operation.value]
    return _MISSING_OPERATION


def _plain_function_shape_reason(function: FunctionType) -> CodexCompensationPortRejectReason | None:
    """Use only immutable code/default metadata, never signature or wrapper metadata."""

    code_value = object.__getattribute__(function, "__code__")
    defaults_value = object.__getattribute__(function, "__defaults__")
    keyword_defaults_value = object.__getattribute__(function, "__kwdefaults__")
    if not isinstance(code_value, CodeType):
        return CodexCompensationPortRejectReason.NON_PLAIN_FUNCTION
    if defaults_value is not None or keyword_defaults_value is not None:
        return CodexCompensationPortRejectReason.DEFAULTED_ARGUMENTS
    if code_value.co_flags & (_FUNCTION_VARARGS_FLAG | _FUNCTION_VARKWARGS_FLAG):
        return CodexCompensationPortRejectReason.VARIADIC_ARGUMENTS
    if code_value.co_kwonlyargcount != 0:
        return CodexCompensationPortRejectReason.REQUIRED_KEYWORD_ARGUMENTS
    if code_value.co_argcount < 2:
        return CodexCompensationPortRejectReason.ZERO_REQUEST_ARGUMENTS
    if code_value.co_argcount > 2:
        return CodexCompensationPortRejectReason.TWO_REQUEST_ARGUMENTS
    return None


def _rejected(reason: CodexCompensationPortRejectReason) -> CodexCompensationPortRejected:
    return CodexCompensationPortRejected(status="INVALID_PORT", reason=reason)
