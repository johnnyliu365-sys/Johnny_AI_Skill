"""A1-A8 acceptance tests for the integrated receipt-removal transaction."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from typing import Literal

from library.local_orchestration.codex_registration_contracts import (
    CodexAuthPolicy,
    CodexPluginId,
    CodexRegistrationAttemptId,
)
from library.local_orchestration.codex_registration_port import CodexRegistrationPortRequest
from library.local_orchestration.codex_receipt_removal_request import (
    CodexReceiptRemovalInvocation,
    CodexReceiptRemovalReady,
    build_codex_receipt_removal_request,
)
from library.local_orchestration.codex_compensation_port import CodexInstalledPathAbsenceProof
from library.local_orchestration.contracts import ArtifactDigest, InstallRoot, InstallationId, OwnedRelativePath
from library.local_orchestration.host_contracts import (
    CodexCliVersion,
    CodexMarketplaceName,
    CodexPluginName,
    CodexPreflightRequest,
)
from tests.staging.codex_lifecycle_oracle.contracts import (
    OracleCompleted,
    OracleForeignSeeded,
    OracleMarketplaceRecord,
    OraclePluginRecord,
    OracleState,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner
from tests.staging.codex_lifecycle_oracle.receipt_removal_acceptance import (
    ReceiptRemovalAcceptanceAccepted,
    ReceiptRemovalAcceptancePhase,
    ReceiptRemovalAcceptanceRejectReason,
    ReceiptRemovalAcceptanceRejected,
    run_receipt_removal_acceptance,
)
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


def _request() -> CodexRegistrationPortRequest:
    return CodexRegistrationPortRequest(
        preflight=CodexPreflightRequest(
            installation_id=InstallationId(value="installation-000000000000c3a1"),
            root=InstallRoot(value=r"%LOCALAPPDATA%\JohnnyAIWorkflow"),
            marketplace=CodexMarketplaceName(value="acceptance-market"),
            plugin=CodexPluginName(value="acceptance-plugin"),
            marketplace_source=OwnedRelativePath(value="marketplaces/acceptance-market"),
        ),
        attempt_id=CodexRegistrationAttemptId(value="attempt-000000000000c3a1"),
        expected_version=CodexCliVersion(value="oracle-staging-version"),
        source_locator=OwnedRelativePath(value="marketplaces/acceptance-market"),
        installed_locator=OwnedRelativePath(value="plugins/acceptance-plugin"),
        digest=ArtifactDigest(value="c" * 64),
        expected_auth_policy=CodexAuthPolicy(value="trusted-local"),
        expected_plugin_id=CodexPluginId(value="acceptance-plugin"),
    )


def _ready() -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
    allocator = DisposableEnvironmentAllocator.from_project_runtime()
    provisioned = allocator.provision(EnvironmentOwnerId(value="environment-owner-000000000000c3a1"))
    if type(provisioned) is not ProvisionedEnvironment:
        raise AssertionError("failed to provision the acceptance lease")
    oracle = CodexLifecycleOracle(
        CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
    )
    if type(oracle.initialize(provisioned.environment)) is not OracleCompleted:
        raise AssertionError("failed to initialize the acceptance oracle")
    return allocator, provisioned.environment, oracle


def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
    root = lease.root.path
    result = allocator.teardown(lease)
    if result.status is not TeardownStatus.REMOVED or root.exists():
        raise AssertionError("acceptance lease did not tear down")


@dataclass(frozen=True)
class _ForeignSnapshot:
    marketplaces: tuple[OracleMarketplaceRecord, ...]
    plugins: tuple[OraclePluginRecord, ...]
    payloads: tuple[tuple[str, bytes], ...]


@dataclass(frozen=True)
class _SentinelTreeEntry:
    relative_path: str
    node_type: Literal["directory", "file"]
    content: bytes


def _foreign_marketplace() -> OracleMarketplaceRecord:
    name = "acceptance-market-foreign"
    root = "foreign-acceptance-market-root"
    payload = f"marketplace|{name}|{root}".encode("utf-8")
    return OracleMarketplaceRecord(
        name=name,
        root=root,
        locator=f"marketplaces/{name}.json",
        digest=hashlib.sha256(payload).hexdigest(),
    )


def _foreign_plugin() -> OraclePluginRecord:
    plugin_id = "acceptance-plugin-foreign"
    marketplace = "acceptance-market-foreign"
    installed_path = rf"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\{plugin_id}"
    payload = (
        f"plugin|{plugin_id}|foreign-acceptance-plugin|{marketplace}|foreign-v1|"
        f"foreign-acceptance-source|foreign-acceptance-policy|foreign-acceptance-auth|{installed_path}"
    ).encode("utf-8")
    return OraclePluginRecord(
        plugin_id=plugin_id,
        name="foreign-acceptance-plugin",
        marketplace_name=marketplace,
        version="foreign-v1",
        source="foreign-acceptance-source",
        install_policy="foreign-acceptance-policy",
        auth_policy="foreign-acceptance-auth",
        installed_path=installed_path,
        locator=f"plugins/{plugin_id}.json",
        digest=hashlib.sha256(payload).hexdigest(),
    )


def _seed_foreign(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> None:
    marketplace = oracle.seed_foreign_marketplace(lease, _foreign_marketplace())
    plugin = oracle.seed_foreign_plugin(lease, _foreign_plugin())
    if type(marketplace) is not OracleForeignSeeded or type(plugin) is not OracleForeignSeeded:
        raise AssertionError("foreign seed was not admitted")


def _foreign_snapshot(lease: EnvironmentLease, oracle: CodexLifecycleOracle) -> _ForeignSnapshot:
    state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
    payloads: list[tuple[str, bytes]] = []
    for marketplace_record in state.foreign_marketplaces:
        path = oracle.payload_root(lease) / marketplace_record.locator
        if not path.is_file():
            raise AssertionError("foreign payload is absent")
        payloads.append((marketplace_record.locator, path.read_bytes()))
    for plugin_record in state.foreign_plugins:
        path = oracle.payload_root(lease) / plugin_record.locator
        if not path.is_file():
            raise AssertionError("foreign payload is absent")
        payloads.append((plugin_record.locator, path.read_bytes()))
    return _ForeignSnapshot(
        marketplaces=state.foreign_marketplaces,
        plugins=state.foreign_plugins,
        payloads=tuple(payloads),
    )


def _sentinel_tree_snapshot(root: Path) -> tuple[_SentinelTreeEntry, ...]:
    entries: list[_SentinelTreeEntry] = []
    paths = sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix())
    for path in paths:
        relative_path = path.relative_to(root).as_posix()
        if path.is_dir():
            entries.append(_SentinelTreeEntry(relative_path, "directory", b""))
        elif path.is_file():
            entries.append(_SentinelTreeEntry(relative_path, "file", path.read_bytes()))
        else:
            raise AssertionError("sentinel tree contains an unsupported node")
    return tuple(entries)


class CodexReceiptRemovalAcceptanceTests(unittest.TestCase):
    def test_a2_actual_registration_receipt_reaches_removal_acceptance(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                result = run_receipt_removal_acceptance(lease, oracle, _request())
            self.assertIs(type(result), ReceiptRemovalAcceptanceAccepted)
        finally:
            _teardown(allocator, lease)

    def test_a1_boundary_rejections_do_not_call_oracle(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            calls: list[object] = []

            def trap(current_lease: EnvironmentLease, command: object) -> object:
                calls.append((current_lease, command))
                raise AssertionError("invalid input reached the oracle")

            invalid_lease = run_receipt_removal_acceptance(object(), oracle, _request())
            self.assertIs(type(invalid_lease), ReceiptRemovalAcceptanceRejected)
            if type(invalid_lease) is not ReceiptRemovalAcceptanceRejected:
                raise AssertionError("invalid lease was not rejected")
            self.assertIs(invalid_lease.reason, ReceiptRemovalAcceptanceRejectReason.INVALID_LEASE)

            invalid_oracle = run_receipt_removal_acceptance(lease, object(), _request())
            self.assertIs(type(invalid_oracle), ReceiptRemovalAcceptanceRejected)
            if type(invalid_oracle) is not ReceiptRemovalAcceptanceRejected:
                raise AssertionError("invalid oracle was not rejected")
            self.assertIs(invalid_oracle.reason, ReceiptRemovalAcceptanceRejectReason.INVALID_ORACLE)

            with patch.object(oracle, "run", side_effect=trap):
                invalid_request = run_receipt_removal_acceptance(lease, oracle, object())
                self.assertIs(type(invalid_request), ReceiptRemovalAcceptanceRejected)
                if type(invalid_request) is not ReceiptRemovalAcceptanceRejected:
                    raise AssertionError("invalid request was not rejected")
                self.assertIs(invalid_request.reason, ReceiptRemovalAcceptanceRejectReason.INVALID_REQUEST)
            self.assertEqual([], calls)
        finally:
            _teardown(allocator, lease)

    def test_a1_subclass_constructed_and_identity_mismatch_are_finite(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            class _LeaseSubclass(EnvironmentLease):
                pass

            class _RequestSubclass(CodexRegistrationPortRequest):
                pass

            subclass_lease = object.__new__(_LeaseSubclass)
            subclass = object.__new__(_RequestSubclass)
            constructed = CodexRegistrationPortRequest.model_construct()
            mismatched = _request().model_copy(update={"expected_plugin_id": CodexPluginId(value="other-plugin")})
            invalid_subclass_lease = run_receipt_removal_acceptance(subclass_lease, oracle, _request())
            self.assertIs(type(invalid_subclass_lease), ReceiptRemovalAcceptanceRejected)
            if type(invalid_subclass_lease) is not ReceiptRemovalAcceptanceRejected:
                raise AssertionError("lease subclass was not rejected")
            self.assertIs(invalid_subclass_lease.reason, ReceiptRemovalAcceptanceRejectReason.INVALID_LEASE)
            for value, reason in (
                (subclass, ReceiptRemovalAcceptanceRejectReason.INVALID_REQUEST),
                (constructed, ReceiptRemovalAcceptanceRejectReason.INVALID_REQUEST),
                (mismatched, ReceiptRemovalAcceptanceRejectReason.INVALID_IDENTITY),
            ):
                result = run_receipt_removal_acceptance(lease, oracle, value)
                self.assertIs(type(result), ReceiptRemovalAcceptanceRejected)
                if type(result) is not ReceiptRemovalAcceptanceRejected:
                    raise AssertionError("invalid request did not produce a finite rejection")
                self.assertIs(result.reason, reason)
        finally:
            _teardown(allocator, lease)

    def test_a3_first_removal_and_replay_prove_owned_absence(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                result = run_receipt_removal_acceptance(lease, oracle, _request())
            if type(result) is not ReceiptRemovalAcceptanceAccepted:
                raise AssertionError(f"receipt removal did not accept: {result}")
            self.assertEqual("REMOVED", result.first_removal)
            self.assertEqual("NOT_INSTALLED", result.replay)
            self.assertTrue(result.owned_state_absent)
            self.assertTrue(result.owned_payload_absent)
            self.assertTrue(result.replay_zero_removals)
            state = OracleState.model_validate_json(oracle.state_path(lease).read_bytes())
            self.assertEqual((), state.marketplaces)
            self.assertEqual((), state.plugins)
            self.assertFalse((oracle.payload_root(lease) / "marketplaces/acceptance-market.json").exists())
            self.assertFalse((oracle.payload_root(lease) / "plugins/acceptance-plugin.json").exists())
        finally:
            _teardown(allocator, lease)

    def test_a4_trace_is_exact_and_plugin_removal_precedes_marketplace(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                result = run_receipt_removal_acceptance(lease, oracle, _request())
            if type(result) is not ReceiptRemovalAcceptanceAccepted:
                raise AssertionError("receipt removal did not accept")
            self.assertEqual(
                (
                    ReceiptRemovalAcceptancePhase.VERSION,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_ADD,
                    ReceiptRemovalAcceptancePhase.PLUGIN_ADD,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
                    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
                    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
                    ReceiptRemovalAcceptancePhase.ABSENCE,
                    ReceiptRemovalAcceptancePhase.PLUGIN_REMOVE,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_REMOVE,
                    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
                    ReceiptRemovalAcceptancePhase.ABSENCE,
                    ReceiptRemovalAcceptancePhase.PLUGIN_LIST,
                    ReceiptRemovalAcceptancePhase.MARKETPLACE_LIST,
                    ReceiptRemovalAcceptancePhase.ABSENCE,
                ),
                result.phases,
            )
            self.assertLess(
                result.phases.index(ReceiptRemovalAcceptancePhase.PLUGIN_REMOVE),
                result.phases.index(ReceiptRemovalAcceptancePhase.MARKETPLACE_REMOVE),
            )
        finally:
            _teardown(allocator, lease)

    def test_a5_foreign_records_and_payload_bytes_are_preserved(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            _seed_foreign(lease, oracle)
            before = _foreign_snapshot(lease, oracle)
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                result = run_receipt_removal_acceptance(lease, oracle, _request())
            if type(result) is not ReceiptRemovalAcceptanceAccepted:
                raise AssertionError("foreign-state receipt removal did not accept")
            self.assertTrue(result.foreign_preserved)
            self.assertEqual(before, _foreign_snapshot(lease, oracle))
        finally:
            _teardown(allocator, lease)

    def test_a6_external_git_and_empty_sentinels_remain_untouched(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            with tempfile.TemporaryDirectory(prefix="c3-sentinels-") as temporary_text:
                root = Path(temporary_text)
                git_sentinel = root / "existing-git"
                empty_sentinel = root / "empty"
                git_sentinel.mkdir()
                empty_sentinel.mkdir()
                subprocess.run(("git", "init", "--quiet", str(git_sentinel)), check=True, shell=False)
                before_environment = tuple(sorted(os.environ.items()))
                before_git_tree = _sentinel_tree_snapshot(git_sentinel)
                with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                    result = run_receipt_removal_acceptance(lease, oracle, _request())
                    after_git_tree = _sentinel_tree_snapshot(git_sentinel)
                self.assertEqual(before_git_tree, after_git_tree)
                if type(result) is not ReceiptRemovalAcceptanceAccepted:
                    raise AssertionError("sentinel receipt removal did not accept")
                status = subprocess.run(
                    ("git", "-C", str(git_sentinel), "status", "--porcelain"),
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=False,
                )
                self.assertEqual(0, status.returncode)
                self.assertEqual("", status.stdout)
                self.assertEqual((), tuple(empty_sentinel.iterdir()))
                self.assertEqual(before_environment, tuple(sorted(os.environ.items())))
                state_text = oracle.state_path(lease).read_text(encoding="utf-8")
                self.assertNotIn(str(git_sentinel), state_text)
                self.assertNotIn(str(empty_sentinel), state_text)
                self.assertNotIn(str(git_sentinel), lease.model_dump_json(warnings=False))
                self.assertNotIn(str(empty_sentinel), lease.overlay.model_dump_json(warnings=False))
                self.assertNotIn(str(git_sentinel), _request().model_dump_json(warnings=False))
                self.assertNotIn(str(empty_sentinel), result.model_dump_json(warnings=False))
        finally:
            _teardown(allocator, lease)

    def test_a7_source_gate_limits_object_to_public_boundary(self) -> None:
        source_path = Path(__file__).parent / "staging" / "codex_lifecycle_oracle" / "receipt_removal_acceptance.py"
        source_text = source_path.read_text(encoding="utf-8")
        syntax = ast.parse(source_text, filename=str(source_path))
        expected_object_parameters = {
            ("run_receipt_removal_acceptance", "lease"),
            ("run_receipt_removal_acceptance", "oracle"),
            ("run_receipt_removal_acceptance", "request"),
        }
        object_annotations: set[tuple[str, str]] = set()
        forbidden_nodes: list[tuple[str, int]] = []
        authorized_object_nodes: set[int] = set()
        inspect_bindings = {"inspect"}
        for node in ast.walk(syntax):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "inspect":
                        inspect_bindings.add(alias.asname or "inspect")
            if isinstance(node, ast.ImportFrom) and node.module == "inspect":
                for alias in node.names:
                    inspect_bindings.add(alias.asname or alias.name)
        for node in ast.walk(syntax):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                arguments = list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs)
                if node.args.vararg is not None:
                    arguments.append(node.args.vararg)
                if node.args.kwarg is not None:
                    arguments.append(node.args.kwarg)
                for argument in arguments:
                    annotation_nodes = () if argument.annotation is None else tuple(ast.walk(argument.annotation))
                    if any(
                        isinstance(candidate, ast.Name) and candidate.id == "object"
                        for candidate in annotation_nodes
                    ):
                        object_annotations.add((node.name, argument.arg))
                        if (node.name, argument.arg) in expected_object_parameters:
                            authorized_object_nodes.update(
                                id(candidate)
                                for candidate in annotation_nodes
                                if isinstance(candidate, ast.Name) and candidate.id == "object"
                            )
                    if any(
                        (isinstance(candidate, ast.Name) and candidate.id == "Optional")
                        or (isinstance(candidate, ast.Attribute) and candidate.attr == "Optional")
                        or (isinstance(candidate, ast.Constant) and candidate.value is None)
                        for candidate in annotation_nodes
                    ):
                        forbidden_nodes.append(("optional parameter", argument.lineno))
                if node.returns is not None and any(
                    isinstance(candidate, ast.Name) and candidate.id == "object"
                    for candidate in ast.walk(node.returns)
                ):
                    object_annotations.add((node.name, "<return>"))
            if isinstance(node, ast.Import) and any(alias.name == "inspect" for alias in node.names):
                forbidden_nodes.append(("inspect", node.lineno))
            if isinstance(node, ast.ImportFrom) and node.module == "inspect":
                forbidden_nodes.append(("inspect", node.lineno))
            if isinstance(node, ast.Name) and node.id in inspect_bindings:
                forbidden_nodes.append(("inspect", node.lineno))
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in inspect_bindings:
                forbidden_nodes.append(("inspect", node.lineno))
            if isinstance(node, ast.Name) and node.id == "Any":
                forbidden_nodes.append(("Any", node.lineno))
            if isinstance(node, ast.Name) and node.id == "object" and id(node) not in authorized_object_nodes:
                forbidden_nodes.append(("object outside public boundary", node.lineno))
            if isinstance(node, ast.Attribute) and node.attr == "Any":
                forbidden_nodes.append(("Any", node.lineno))
            if isinstance(node, ast.ImportFrom) and node.module == "typing" and any(
                alias.name == "cast" for alias in node.names
            ):
                forbidden_nodes.append(("typing.cast", node.lineno))
            if isinstance(node, ast.Call) and (
                (isinstance(node.func, ast.Name) and node.func.id == "cast")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "cast")
            ):
                forbidden_nodes.append(("typing.cast", node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "model_construct":
                    forbidden_nodes.append(("model_construct", node.lineno))
                if node.func.attr == "model_copy" and any(keyword.arg == "update" for keyword in node.keywords):
                    forbidden_nodes.append(("model_copy(update=...)", node.lineno))
                if node.func.attr in {"__getattribute__", "__getattr__"}:
                    forbidden_nodes.append(("dynamic member lookup", node.lineno))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {
                "getattr",
                "hasattr",
                "setattr",
            }:
                forbidden_nodes.append(("dynamic member lookup", node.lineno))
            if isinstance(node, ast.Attribute) and node.attr in {"__dict__", "__getattribute__", "__getattr__"}:
                forbidden_nodes.append(("dynamic member lookup", node.lineno))
            if isinstance(node, ast.ExceptHandler) and (
                node.type is None
                or (isinstance(node.type, ast.Name) and node.type.id in {"BaseException", "Exception"})
            ):
                forbidden_nodes.append(("broad catch", node.lineno))
        self.assertEqual(expected_object_parameters, object_annotations)
        self.assertEqual([], forbidden_nodes)
        self.assertNotIn("# type: ignore", source_text.lower())

    def test_a7_public_constructors_and_round_trips_keep_strong_types(self) -> None:
        allocator, lease, oracle = _ready()
        try:
            with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\oracle\AppData\Local"}):
                result = run_receipt_removal_acceptance(lease, oracle, _request())
            if type(result) is not ReceiptRemovalAcceptanceAccepted:
                raise AssertionError("type-gate fixture did not produce a receipt")
            lease_round_trip = EnvironmentLease.model_validate_json(lease.model_dump_json(warnings=False))
            receipt_round_trip = result.receipt.model_validate_json(result.receipt.model_dump_json(warnings=False))
            invocation = CodexReceiptRemovalInvocation(
                installation_id=result.receipt.installation_id,
                root=result.receipt.root,
                receipt=result.receipt,
            )
            ready = build_codex_receipt_removal_request(invocation)
            if type(ready) is not CodexReceiptRemovalReady:
                raise AssertionError("receipt removal request was not ready")
            ready_round_trip = CodexReceiptRemovalReady.model_validate_json(ready.model_dump_json(warnings=False))
            proof_true = CodexInstalledPathAbsenceProof(manifest=ready.request.manifest, absent=True)
            proof_false = CodexInstalledPathAbsenceProof(manifest=ready.request.manifest, absent=False)
            proof_true_round_trip = CodexInstalledPathAbsenceProof.model_validate_json(
                proof_true.model_dump_json(warnings=False)
            )
            proof_false_round_trip = CodexInstalledPathAbsenceProof.model_validate_json(
                proof_false.model_dump_json(warnings=False)
            )
            self.assertEqual(lease, lease_round_trip)
            self.assertEqual(result.receipt, receipt_round_trip)
            self.assertEqual(ready, ready_round_trip)
            self.assertIs(type(proof_true_round_trip.absent), bool)
            self.assertIs(type(proof_false_round_trip.absent), bool)
            self.assertTrue(proof_true_round_trip.absent)
            self.assertFalse(proof_false_round_trip.absent)
        finally:
            _teardown(allocator, lease)


if __name__ == "__main__":
    unittest.main()
