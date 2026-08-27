"""High-assurance tests for the private Router telemetry authorization boundary."""

from __future__ import annotations

import ast
import hashlib
import unittest
from pathlib import Path

from library.workflow_router.policy_response import (
    ApprovedDispatchArtifact,
    StaticApprovedDispatchArtifactRegistry,
)
from library.workflow_router.telemetry_provisioning_contracts import (
    RouterTelemetryProvisioningAuthorized,
    RouterTelemetryProvisioningAuthorityMismatch,
    RouterTelemetryProvisioningDecision,
    RouterTelemetryProvisioningRequest,
    authorize_router_telemetry_provisioning,
)


_ROOT = Path(__file__).resolve().parents[1]
_SOURCE = _ROOT / "library" / "workflow_router" / "telemetry_provisioning_contracts.py"
_INDEX = (
    _ROOT
    / "modules"
    / "element"
    / "python"
    / "context-load-telemetry"
    / "14-router-owned-provisioning-delegation-contracts"
    / "README.md"
)
_PROJECT = "prj_0123456789abcdef"
_REQUEST = "request-alpha"
_TICKET = "ticket-alpha"
_HANDOFF = "handoff-alpha"
_OWNER = "owner-alpha"
_TICKET_COMMIT = "abcdef1"
_HANDOFF_COMMIT = "1234567"
_AUTHORITY_DOMAIN = "router-telemetry-provisioning-authority-v1"
_DENIAL_DOMAIN = "router-telemetry-provisioning-denial-v1"


def _artifact(
    *,
    project_id: str = _PROJECT,
    ticket_reference: str = _TICKET,
    handoff_reference: str = _HANDOFF,
    implementation_owner_id: str = _OWNER,
    ticket_docs_commit: str = _TICKET_COMMIT,
    handoff_docs_commit: str = _HANDOFF_COMMIT,
) -> ApprovedDispatchArtifact:
    return ApprovedDispatchArtifact(
        project_id=project_id,
        ticket_reference=ticket_reference,
        handoff_reference=handoff_reference,
        implementation_owner_id=implementation_owner_id,
        ticket_docs_commit=ticket_docs_commit,
        handoff_docs_commit=handoff_docs_commit,
    )


def _registry() -> StaticApprovedDispatchArtifactRegistry:
    return StaticApprovedDispatchArtifactRegistry(records=(_artifact(),))


def _request(
    *,
    request_ref: str = _REQUEST,
    project_id: str = _PROJECT,
    ticket_reference: str = _TICKET,
    handoff_reference: str = _HANDOFF,
    implementation_owner_id: str = _OWNER,
    ticket_docs_commit: str = _TICKET_COMMIT,
    handoff_docs_commit: str = _HANDOFF_COMMIT,
) -> RouterTelemetryProvisioningRequest:
    return RouterTelemetryProvisioningRequest(
        request_ref=request_ref,
        project_id=project_id,
        ticket_reference=ticket_reference,
        handoff_reference=handoff_reference,
        implementation_owner_id=implementation_owner_id,
        ticket_docs_commit=ticket_docs_commit,
        handoff_docs_commit=handoff_docs_commit,
    )


def _digest(
    domain: str,
    request: RouterTelemetryProvisioningRequest,
    *,
    include_request_ref: bool,
) -> str:
    coordinates = (
        request.project_id,
        request.ticket_reference,
        request.handoff_reference,
        request.implementation_owner_id,
        request.ticket_docs_commit,
        request.handoff_docs_commit,
    )
    values = (request.request_ref, *coordinates) if include_request_ref else coordinates
    material = "\0".join((domain, *values))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class TelemetryProvisioningBehaviorTests(unittest.TestCase):
    """TPA1-TPA3: exact grant/denial behavior and strict finite DTOs."""

    def test_tpa1_exact_match_authorizes_with_deterministic_opaque_result(self) -> None:
        registry = _registry()
        request = _request()
        artifact_before = registry.resolve(
            project_id=request.project_id,
            ticket_reference=request.ticket_reference,
            handoff_reference=request.handoff_reference,
            implementation_owner_id=request.implementation_owner_id,
        )
        result = authorize_router_telemetry_provisioning(registry, request)
        self.assertIsInstance(result, RouterTelemetryProvisioningAuthorized)
        assert isinstance(result, RouterTelemetryProvisioningAuthorized)
        self.assertEqual(result.decision, RouterTelemetryProvisioningDecision.AUTHORIZED)
        self.assertEqual(result.request_ref, request.request_ref)
        self.assertEqual(result.project_id, request.project_id)
        self.assertEqual(result.ticket_reference, request.ticket_reference)
        self.assertEqual(result.handoff_reference, request.handoff_reference)
        self.assertEqual(result.implementation_owner_id, request.implementation_owner_id)
        self.assertEqual(
            result.provisioning_authority_ref,
            f"provision-authority-{_digest(_AUTHORITY_DOMAIN, request, include_request_ref=False)}",
        )
        self.assertEqual(
            set(result.model_dump(mode="json")),
            {
                "decision",
                "request_ref",
                "project_id",
                "ticket_reference",
                "handoff_reference",
                "implementation_owner_id",
                "provisioning_authority_ref",
            },
        )
        repeated = authorize_router_telemetry_provisioning(registry, request)
        self.assertEqual(result.model_dump_json(), repeated.model_dump_json())
        request_variant = _request(request_ref="request-beta")
        variant = authorize_router_telemetry_provisioning(registry, request_variant)
        self.assertIsInstance(variant, RouterTelemetryProvisioningAuthorized)
        assert isinstance(variant, RouterTelemetryProvisioningAuthorized)
        self.assertEqual(variant.request_ref, request_variant.request_ref)
        self.assertEqual(
            result.provisioning_authority_ref,
            variant.provisioning_authority_ref,
        )
        artifact_after = registry.resolve(
            project_id=request.project_id,
            ticket_reference=request.ticket_reference,
            handoff_reference=request.handoff_reference,
            implementation_owner_id=request.implementation_owner_id,
        )
        self.assertIs(artifact_before, artifact_after)
        self.assertEqual(artifact_before, _artifact())

    def test_tpa2_each_changed_coordinate_denies_without_identity_fields(self) -> None:
        registry = _registry()
        cases = (
            ("project_id", _request(project_id="prj_fedcba9876543210")),
            ("ticket_reference", _request(ticket_reference="ticket-beta")),
            ("handoff_reference", _request(handoff_reference="handoff-beta")),
            ("implementation_owner_id", _request(implementation_owner_id="owner-beta")),
            ("ticket_docs_commit", _request(ticket_docs_commit="7654321")),
            ("handoff_docs_commit", _request(handoff_docs_commit="fedcba9")),
        )
        for name, request in cases:
            with self.subTest(coordinate=name):
                result = authorize_router_telemetry_provisioning(registry, request)
                self.assertIsInstance(result, RouterTelemetryProvisioningAuthorityMismatch)
                assert isinstance(result, RouterTelemetryProvisioningAuthorityMismatch)
                self.assertEqual(
                    result.decision,
                    RouterTelemetryProvisioningDecision.AUTHORITY_MISMATCH,
                )
                self.assertEqual(result.request_ref, request.request_ref)
                self.assertEqual(
                    result.denial_ref,
                    f"provision-denial-{_digest(_DENIAL_DOMAIN, request, include_request_ref=True)}",
                )
                self.assertEqual(
                    set(result.model_dump(mode="json")),
                    {"decision", "request_ref", "denial_ref"},
                )

    def test_tpa3_strict_construction_rejects_invalid_and_contradictory_values(self) -> None:
        invalid_requests = (
            {"project_id": "project/path"},
            {"ticket_docs_commit": "git_not-a-reviewed-commit"},
            {"handoff_docs_commit": None},
            {"stream_locator": "streams/alpha.jsonl"},
            {"root": "C:/Johnny"},
        )
        for update in invalid_requests:
            with self.subTest(update=update):
                values = _request().model_dump(mode="python")
                values.update(update)
                with self.assertRaises(ValueError):
                    RouterTelemetryProvisioningRequest.model_validate(values)
        with self.assertRaises(ValueError):
            RouterTelemetryProvisioningRequest.model_validate(
                {**_request().model_dump(mode="python"), "unexpected": "value"}
            )
        with self.assertRaises(ValueError):
            RouterTelemetryProvisioningAuthorized(
                decision=RouterTelemetryProvisioningDecision.AUTHORITY_MISMATCH,
                request_ref=_REQUEST,
                project_id=_PROJECT,
                ticket_reference=_TICKET,
                handoff_reference=_HANDOFF,
                implementation_owner_id=_OWNER,
                provisioning_authority_ref="provision-authority-abcdef1234567890",
            )
        with self.assertRaises(ValueError):
            RouterTelemetryProvisioningAuthorityMismatch(
                decision=RouterTelemetryProvisioningDecision.AUTHORIZED,
                request_ref=_REQUEST,
                denial_ref="provision-denial-abcdef1234567890",
            )


class TelemetryProvisioningSourceTests(unittest.TestCase):
    """TPA4-TPA5: exact private source direction and target-owned index."""

    def test_tpa4_source_is_typed_deterministic_and_effect_free(self) -> None:
        source = _SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            (node.module, tuple(alias.name for alias in node.names))
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.module != "__future__"
        }
        self.assertEqual(
            imports,
            {
                ("hashlib", ("sha256",)),
                ("enum", ("Enum",)),
                ("pydantic", ("model_validator",)),
                (
                    "library.workflow_router.contracts",
                    (
                        "OpaqueMetadataId",
                        "ProjectId",
                        "ReviewedCommitReference",
                        "RouterModel",
                    ),
                ),
                (
                    "library.workflow_router.policy_response",
                    (
                        "ApprovedDispatchArtifactRegistry",
                        "resolve_approved_dispatch_artifact",
                    ),
                ),
            },
        )
        public_functions = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]
        self.assertEqual(
            [node.name for node in public_functions],
            ["authorize_router_telemetry_provisioning"],
        )
        entrypoint = public_functions[0]
        self.assertEqual(
            tuple(argument.arg for argument in entrypoint.args.args),
            ("registry", "request"),
        )
        self.assertIn("resolve_approved_dispatch_artifact", source)
        self.assertIn("sha256(", source)
        self.assertIn(_AUTHORITY_DOMAIN, source)
        self.assertIn(_DENIAL_DOMAIN, source)
        for forbidden in (
            "TelemetryStorage",
            "JohnnyRootLayout",
            "Path",
            "filesystem",
            "storage",
            "root",
            "locator",
            "os.",
            "environ",
            "provider",
            "host",
            "process",
            "network",
            "RouterEngine",
            "__init__",
            "Any",
            "cast(",
            "dict",
            "mapping",
            "getattr(",
            "setattr(",
            "callback",
            "singleton",
            "cache",
            "retry",
            "sleep",
            "poll",
            "queue",
            "runner",
            "raise Exception",
        ):
            self.assertNotIn(forbidden.casefold(), source.casefold())
        package_init = (_ROOT / "library" / "workflow_router" / "__init__.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("telemetry_provisioning", package_init)

    def test_tpa5_element_index_names_private_no_bootstrap_boundary(self) -> None:
        body = _INDEX.read_text(encoding="utf-8")
        for required in (
            "14-router-owned-provisioning-delegation-contracts.md",
            "telemetry_provisioning_contracts.py",
            "test_telemetry_provisioning_contracts.py",
            "ApprovedDispatchArtifactRegistry",
            "resolve_approved_dispatch_artifact",
            "ADR-20260827-029",
        ):
            self.assertIn(required, body)
        self.assertIn("neither Host Bootstrap", body)
        self.assertIn("durable telemetry provisioning", body)


if __name__ == "__main__":
    unittest.main()
