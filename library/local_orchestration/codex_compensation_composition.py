"""Thin exact composition of an admitted compensation port and pure reducer."""

from __future__ import annotations

from types import MethodType
from typing import cast

from pydantic import ValidationError

from .codex_compensation_port import (
    CodexCompensationPortCapability,
    CodexCompensationPortManifest,
    CodexCompensationPortRequest,
    CodexInstalledPathAbsenceProof,
    CodexMarketplaceRemovalProof,
    CodexPluginRemovalProof,
)
from .codex_compensation_reducer import (
    CodexCompensationBlocked,
    CodexCompensationBlockReason,
    CodexCompensationNoop,
    CodexCompensationObservation,
    CodexCompensationPlan,
    CodexCompensationResult,
    CodexCompensationStep,
    CodexInstalledLocationProof,
    CodexMarketplaceProof,
    CodexNoCompensationPlan,
    CodexPluginListsProof,
    CodexProofTruth,
    CodexRemovalConfirmed,
    CodexRemovalFailed,
    reduce_compensation,
)
from .codex_registration_contracts import CodexAuthPolicy, CodexPluginId
from .contracts import ArtifactDigest, InstallRoot, InstallationId, OwnedRelativePath
from .host_contracts import (
    CodexCliVersion,
    CodexMarketplaceEntry,
    CodexMarketplaceList,
    CodexMarketplaceName,
    CodexMarketplaceSource,
    CodexPluginEntry,
    CodexPluginList,
    CodexPluginName,
)


def compose_codex_compensation(
    capability: CodexCompensationPortCapability,
    request: CodexCompensationPortRequest,
    plan: CodexCompensationPlan | CodexNoCompensationPlan,
) -> CodexCompensationResult:
    """Validate all identities, execute the frozen plan, and return reducer truth."""

    if not _capability_is_exact(capability) or not _request_is_exact(request):
        return _plan_invalid()
    if type(plan) is not CodexCompensationPlan and type(plan) is not CodexNoCompensationPlan:
        return _plan_invalid()
    validated_plan = plan
    plan_preflight = reduce_compensation(validated_plan, ())
    if isinstance(plan_preflight, CodexCompensationNoop):
        if not _request_matches_plan(request, validated_plan):
            return _plan_invalid()
        return plan_preflight
    if (
        type(validated_plan) is not CodexCompensationPlan
        or not isinstance(plan_preflight, CodexCompensationBlocked)
        or plan_preflight.reason is not CodexCompensationBlockReason.OUTCOME_SEQUENCE_INVALID
        or not _request_matches_plan(request, validated_plan)
    ):
        return _plan_invalid()
    outcomes: list[CodexCompensationObservation] = []
    for step in validated_plan.steps:
        if step is CodexCompensationStep.REMOVE_PLUGIN:
            returned_plugin_removal: object = capability.remove_plugin(request)
            outcomes.append(_plugin_removal_observation(returned_plugin_removal, request))
        elif step is CodexCompensationStep.REMOVE_MARKETPLACE:
            returned_marketplace_removal: object = capability.remove_marketplace(request)
            outcomes.append(_marketplace_removal_observation(returned_marketplace_removal, request))
        elif step is CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT:
            returned_plugins: object = capability.list_plugins(request)
            outcomes.append(_plugin_list_observation(returned_plugins, request))
        elif step is CodexCompensationStep.PROVE_MARKETPLACE_ABSENT:
            returned_marketplaces: object = capability.list_marketplaces(request)
            outcomes.append(_marketplace_list_observation(returned_marketplaces, request))
        else:
            returned_path_proof: object = capability.prove_installed_path_absent(request)
            outcomes.append(_installed_path_observation(returned_path_proof, request))
    return reduce_compensation(validated_plan, tuple(outcomes))


def _plan_invalid() -> CodexCompensationBlocked:
    return CodexCompensationBlocked(
        status="COMPENSATION_BLOCKED",
        reason=CodexCompensationBlockReason.PLAN_INVALID,
    )


def _capability_is_exact(value: object) -> bool:
    if type(value) is not CodexCompensationPortCapability:
        return False
    capability = value
    try:
        return (
            type(capability.status) is str
            and capability.status == "ADMITTED"
            and type(capability.remove_plugin) is MethodType
            and type(capability.remove_marketplace) is MethodType
            and type(capability.list_plugins) is MethodType
            and type(capability.list_marketplaces) is MethodType
            and type(capability.prove_installed_path_absent) is MethodType
        )
    except AttributeError:
        return False


def _request_is_exact(value: object) -> bool:
    if type(value) is not CodexCompensationPortRequest:
        return False
    request = value
    try:
        current_manifest: object = request.manifest
    except AttributeError:
        return False
    if not _manifest_is_exact(current_manifest):
        return False
    try:
        CodexCompensationPortRequest(manifest=cast(CodexCompensationPortManifest, current_manifest))
    except (TypeError, ValidationError, ValueError):
        return False
    return True


def _manifest_is_exact(value: object) -> bool:
    if type(value) is not CodexCompensationPortManifest:
        return False
    current = value
    try:
        exact_shape = (
            type(current.installation_id) is InstallationId
            and type(current.installation_id.value) is str
            and type(current.root) is InstallRoot
            and type(current.root.value) is str
            and type(current.marketplace) is CodexMarketplaceName
            and type(current.marketplace.value) is str
            and type(current.marketplace_source) is OwnedRelativePath
            and type(current.marketplace_source.value) is str
            and type(current.plugin_id) is CodexPluginId
            and type(current.plugin_id.value) is str
            and type(current.plugin) is CodexPluginName
            and type(current.plugin.value) is str
            and type(current.version) is CodexCliVersion
            and type(current.version.value) is str
            and type(current.installed_locator) is OwnedRelativePath
            and type(current.installed_locator.value) is str
            and type(current.auth_policy) is CodexAuthPolicy
            and type(current.auth_policy.value) is str
            and type(current.digest) is ArtifactDigest
            and type(current.digest.value) is str
        )
        if not exact_shape:
            return False
        CodexCompensationPortManifest(
            installation_id=InstallationId(value=current.installation_id.value),
            root=InstallRoot(value=current.root.value),
            marketplace=CodexMarketplaceName(value=current.marketplace.value),
            marketplace_source=OwnedRelativePath(value=current.marketplace_source.value),
            plugin_id=CodexPluginId(value=current.plugin_id.value),
            plugin=CodexPluginName(value=current.plugin.value),
            version=CodexCliVersion(value=current.version.value),
            installed_locator=OwnedRelativePath(value=current.installed_locator.value),
            auth_policy=CodexAuthPolicy(value=current.auth_policy.value),
            digest=ArtifactDigest(value=current.digest.value),
        )
    except (AttributeError, TypeError, ValidationError, ValueError):
        return False
    return True


def _request_matches_plan(
    request: CodexCompensationPortRequest,
    plan: CodexCompensationPlan | CodexNoCompensationPlan,
) -> bool:
    current = request.manifest
    expected = plan.request
    return (
        current.installation_id.value == expected.installation_id.value
        and current.root.value == expected.root.value
        and current.marketplace.value == expected.marketplace.value
        and current.plugin.value == expected.plugin.value
        and current.marketplace_source.value == expected.marketplace_source.value
    )


def _manifests_match(
    returned: CodexCompensationPortManifest,
    expected: CodexCompensationPortManifest,
) -> bool:
    return (
        returned.installation_id.value == expected.installation_id.value
        and returned.root.value == expected.root.value
        and returned.marketplace.value == expected.marketplace.value
        and returned.marketplace_source.value == expected.marketplace_source.value
        and returned.plugin_id.value == expected.plugin_id.value
        and returned.plugin.value == expected.plugin.value
        and returned.version.value == expected.version.value
        and returned.installed_locator.value == expected.installed_locator.value
        and returned.auth_policy.value == expected.auth_policy.value
        and returned.digest.value == expected.digest.value
    )


def _plugin_removal_observation(
    value: object,
    request: CodexCompensationPortRequest,
) -> CodexRemovalConfirmed | CodexRemovalFailed:
    failed = CodexRemovalFailed(
        step=CodexCompensationStep.REMOVE_PLUGIN,
        status="DECLARED_FAILURE",
    )
    if type(value) is not CodexPluginRemovalProof:
        return failed
    proof = value
    try:
        returned_manifest: object = proof.manifest
        status: object = proof.status
    except AttributeError:
        return failed
    if (
        not _manifest_is_exact(returned_manifest)
        or type(status) is not str
        or status != "REMOVED"
        or not _manifests_match(cast(CodexCompensationPortManifest, returned_manifest), request.manifest)
    ):
        return failed
    return CodexRemovalConfirmed(
        step=CodexCompensationStep.REMOVE_PLUGIN,
        status="CONFIRMED",
    )


def _marketplace_removal_observation(
    value: object,
    request: CodexCompensationPortRequest,
) -> CodexRemovalConfirmed | CodexRemovalFailed:
    failed = CodexRemovalFailed(
        step=CodexCompensationStep.REMOVE_MARKETPLACE,
        status="DECLARED_FAILURE",
    )
    if type(value) is not CodexMarketplaceRemovalProof:
        return failed
    proof = value
    try:
        returned_manifest: object = proof.manifest
        status: object = proof.status
    except AttributeError:
        return failed
    if (
        not _manifest_is_exact(returned_manifest)
        or type(status) is not str
        or status != "REMOVED"
        or not _manifests_match(cast(CodexCompensationPortManifest, returned_manifest), request.manifest)
    ):
        return failed
    return CodexRemovalConfirmed(
        step=CodexCompensationStep.REMOVE_MARKETPLACE,
        status="CONFIRMED",
    )


def _plugin_list_observation(
    value: object,
    request: CodexCompensationPortRequest,
) -> CodexPluginListsProof:
    if not _plugin_list_is_exact(value):
        return CodexPluginListsProof(
            step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
            installed=CodexProofTruth.MALFORMED,
            available=CodexProofTruth.MALFORMED,
        )
    plugin_list = cast(CodexPluginList, value)
    return CodexPluginListsProof(
        step=CodexCompensationStep.PROVE_PLUGIN_LISTS_ABSENT,
        installed=_plugin_collection_truth(plugin_list.installed, request.manifest),
        available=_plugin_collection_truth(plugin_list.available, request.manifest),
    )


def _marketplace_list_observation(
    value: object,
    request: CodexCompensationPortRequest,
) -> CodexMarketplaceProof:
    if not _marketplace_list_is_exact(value):
        return CodexMarketplaceProof(
            step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
            truth=CodexProofTruth.MALFORMED,
        )
    marketplace_list = cast(CodexMarketplaceList, value)
    mismatch = False
    for entry in marketplace_list.marketplaces:
        if entry.name != request.manifest.marketplace.value:
            continue
        source = entry.marketplaceSource
        if source is not None and source.value == request.manifest.marketplace_source.value:
            return CodexMarketplaceProof(
                step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
                truth=CodexProofTruth.RESIDUE,
            )
        mismatch = True
    return CodexMarketplaceProof(
        step=CodexCompensationStep.PROVE_MARKETPLACE_ABSENT,
        truth=CodexProofTruth.MISMATCH if mismatch else CodexProofTruth.PROVED_ABSENT,
    )


def _installed_path_observation(
    value: object,
    request: CodexCompensationPortRequest,
) -> CodexInstalledLocationProof:
    if type(value) is not CodexInstalledPathAbsenceProof:
        return CodexInstalledLocationProof(
            step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
            truth=CodexProofTruth.MALFORMED,
        )
    proof = value
    try:
        returned_manifest: object = proof.manifest
        absent: object = proof.absent
    except AttributeError:
        return CodexInstalledLocationProof(
            step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
            truth=CodexProofTruth.MALFORMED,
        )
    if not _manifest_is_exact(returned_manifest) or type(absent) is not bool:
        truth = CodexProofTruth.MALFORMED
    elif not _manifests_match(cast(CodexCompensationPortManifest, returned_manifest), request.manifest):
        truth = CodexProofTruth.MISMATCH
    elif absent:
        truth = CodexProofTruth.PROVED_ABSENT
    else:
        truth = CodexProofTruth.RESIDUE
    return CodexInstalledLocationProof(
        step=CodexCompensationStep.PROVE_INSTALLED_LOCATION_ABSENT,
        truth=truth,
    )


def _plugin_list_is_exact(value: object) -> bool:
    if type(value) is not CodexPluginList:
        return False
    plugin_list = value
    try:
        return (
            type(plugin_list.installed) is tuple
            and type(plugin_list.available) is tuple
            and all(_plugin_entry_is_exact(entry) for entry in plugin_list.installed)
            and all(_plugin_entry_is_exact(entry) for entry in plugin_list.available)
        )
    except (AttributeError, TypeError):
        return False


def _plugin_entry_is_exact(value: object) -> bool:
    if type(value) is not CodexPluginEntry:
        return False
    entry = value
    try:
        if (
            type(entry.pluginId) is not str
            or type(entry.name) is not str
            or type(entry.marketplaceName) is not str
            or type(entry.version) is not str
            or type(entry.installed) is not bool
            or type(entry.enabled) is not bool
            or type(entry.source) is not str
            or type(entry.installPolicy) is not str
            or type(entry.authPolicy) is not str
        ):
            return False
        source: object = entry.marketplaceSource
        if source is not None and not _marketplace_source_is_exact(source):
            return False
        fields: dict[str, object] = {
            "pluginId": entry.pluginId,
            "name": entry.name,
            "marketplaceName": entry.marketplaceName,
            "version": entry.version,
            "installed": entry.installed,
            "enabled": entry.enabled,
            "source": entry.source,
            "installPolicy": entry.installPolicy,
            "authPolicy": entry.authPolicy,
        }
        if source is not None:
            fields["marketplaceSource"] = cast(CodexMarketplaceSource, source)
        CodexPluginEntry.model_validate(fields)
    except (AttributeError, TypeError, ValidationError, ValueError):
        return False
    return True


def _plugin_collection_truth(
    entries: tuple[CodexPluginEntry, ...],
    manifest: CodexCompensationPortManifest,
) -> CodexProofTruth:
    mismatch = False
    for entry in entries:
        if entry.pluginId != manifest.plugin_id.value:
            continue
        if (
            entry.name == manifest.plugin.value
            and entry.marketplaceName == manifest.marketplace.value
            and entry.version == manifest.version.value
            and entry.authPolicy == manifest.auth_policy.value
        ):
            return CodexProofTruth.RESIDUE
        mismatch = True
    return CodexProofTruth.MISMATCH if mismatch else CodexProofTruth.PROVED_ABSENT


def _marketplace_list_is_exact(value: object) -> bool:
    if type(value) is not CodexMarketplaceList:
        return False
    marketplace_list = value
    try:
        return (
            type(marketplace_list.marketplaces) is tuple
            and all(_marketplace_entry_is_exact(entry) for entry in marketplace_list.marketplaces)
        )
    except (AttributeError, TypeError):
        return False


def _marketplace_entry_is_exact(value: object) -> bool:
    if type(value) is not CodexMarketplaceEntry:
        return False
    entry = value
    try:
        if type(entry.name) is not str or type(entry.root) is not str:
            return False
        source: object = entry.marketplaceSource
        if source is not None and not _marketplace_source_is_exact(source):
            return False
        if source is None:
            CodexMarketplaceEntry(name=entry.name, root=entry.root)
        else:
            CodexMarketplaceEntry(
                name=entry.name,
                root=entry.root,
                marketplaceSource=cast(CodexMarketplaceSource, source),
            )
    except (AttributeError, TypeError, ValidationError, ValueError):
        return False
    return True


def _marketplace_source_is_exact(value: object) -> bool:
    if type(value) is not CodexMarketplaceSource:
        return False
    source = value
    try:
        if type(source.type) is not str or type(source.value) is not str:
            return False
        CodexMarketplaceSource(type=source.type, value=source.value)
    except (AttributeError, TypeError, ValidationError, ValueError):
        return False
    return True
