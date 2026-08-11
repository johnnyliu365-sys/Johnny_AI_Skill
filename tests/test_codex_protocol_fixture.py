"""T1-T4 closure for the isolated Codex protocol fixture."""

from __future__ import annotations

from enum import Enum
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

from library.local_orchestration.host_contracts import CodexMarketplaceList, CodexPluginList
from pydantic import ValidationError
from tests.staging.codex_protocol.contracts import (
    CodexMarketplaceAdd,
    CodexMarketplaceRemove,
    CodexPluginAdd,
    CodexPluginRemove,
    CodexProtocolAccepted,
    CodexProtocolRejectReason,
    CodexProtocolRejected,
    CodexProtocolSurface,
    ExactResponseFilePort,
    MAX_RESPONSE_BYTES,
    RESPONSE_FILE_NAME,
    ResponseFileInspection,
    ResponseFileRead,
    ResponseFileRemoval,
    parse_codex_protocol_payload,
)
from tests.staging.codex_protocol.fixture import CodexProtocolFixture
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import (
    AbsoluteExecutable,
    ChildProcessRequest,
    EffectiveArgv,
    GenericLaunchFailureObservation,
    ProcessExitCode,
    ProcessInvocation,
    ProcessObservation,
    SuccessfulProcessObservation,
    WindowsLaunchEvidence,
)
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort


FIXTURE_CHILD = Path(__file__).resolve().parent / "staging" / "codex_protocol" / "fixture_child.py"
ENVIRONMENT_PREFIX = "johnny-stage-env-"


class InjectedResponseShape(str, Enum):
    OVERSIZE = "OVERSIZE"
    DIRECTORY = "DIRECTORY"
    INVALID_UTF8 = "INVALID_UTF8"
    MALFORMED_JSON = "MALFORMED_JSON"
    SCHEMA_INVALID = "SCHEMA_INVALID"


class RecordingRunner:
    """Preserves the concrete runner while exposing only its exact child arguments."""

    def __init__(self) -> None:
        self._runner = BoundedChildProcessRunner(SubprocessProcessPort())
        self.arguments: list[tuple[str, ...]] = []

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.arguments.append(request.arguments.values)
        return self._runner.run(request)


class InjectedSuccessRunner:
    """Creates one exact temporary response topology after typed runner admission."""

    def __init__(self, shape: InjectedResponseShape) -> None:
        self._shape = shape
        self.call_count = 0

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.call_count += 1
        response = request.working_directory.path / RESPONSE_FILE_NAME
        if self._shape is InjectedResponseShape.OVERSIZE:
            response.write_bytes(b"x" * 65_537)
        elif self._shape is InjectedResponseShape.DIRECTORY:
            response.mkdir()
        elif self._shape is InjectedResponseShape.INVALID_UTF8:
            response.write_bytes(b"\xff")
        elif self._shape is InjectedResponseShape.MALFORMED_JSON:
            response.write_bytes(b"{")
        else:
            response.write_bytes(b"{}")
        return _successful_observation(request)


class MissingResponseRunner:
    """A strict successful process port that deliberately writes no response file."""

    def __init__(self) -> None:
        self.call_count = 0

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.call_count += 1
        return _successful_observation(request)


class FailedProcessRunner:
    """A typed failed process observation with no response side effect."""

    def __init__(self) -> None:
        self.call_count = 0

    def run(self, request: ChildProcessRequest) -> ProcessObservation:
        self.call_count += 1
        invocation = _invocation(request)
        return GenericLaunchFailureObservation(invocation=invocation, launch=WindowsLaunchEvidence(winerror=206))


class CleanupFailureResponsePort:
    """A strict response port that exposes only the declared cleanup fault."""

    def __init__(self) -> None:
        self._delegate = ExactResponseFilePort()

    def inspect(self, lease: EnvironmentLease) -> ResponseFileInspection:
        return self._delegate.inspect(lease)

    def read(self, lease: EnvironmentLease) -> ResponseFileRead:
        return self._delegate.read(lease)

    def remove(self, lease: EnvironmentLease) -> ResponseFileRemoval:
        del lease
        return ResponseFileRemoval.FAILED


class ReadFailureResponsePort:
    """A strict response port that exposes only the declared read fault."""

    def __init__(self) -> None:
        self._delegate = ExactResponseFilePort()

    def inspect(self, lease: EnvironmentLease) -> ResponseFileInspection:
        return self._delegate.inspect(lease)

    def read(self, lease: EnvironmentLease) -> ResponseFileRead:
        del lease
        raise OSError("deterministic response read failure")

    def remove(self, lease: EnvironmentLease) -> ResponseFileRemoval:
        return self._delegate.remove(lease)


class CodexProtocolFixtureTests(unittest.TestCase):
    def test_t1_frozen_payloads_are_strict_and_surface_bound(self) -> None:
        expected_types = {
            CodexProtocolSurface.MARKETPLACE_ADD: CodexMarketplaceAdd,
            CodexProtocolSurface.MARKETPLACE_LIST: CodexMarketplaceList,
            CodexProtocolSurface.MARKETPLACE_REMOVE: CodexMarketplaceRemove,
            CodexProtocolSurface.PLUGIN_ADD: CodexPluginAdd,
            CodexProtocolSurface.PLUGIN_LIST: CodexPluginList,
            CodexProtocolSurface.PLUGIN_REMOVE: CodexPluginRemove,
        }
        for surface in CodexProtocolSurface:
            with self.subTest(surface=surface.value):
                parsed = parse_codex_protocol_payload(surface, _json_bytes(_canonical_payload(surface)))
                self.assertNotIsInstance(parsed, CodexProtocolRejectReason)
                self.assertIsInstance(parsed, expected_types[surface])
                if surface is CodexProtocolSurface.PLUGIN_ADD:
                    assert isinstance(parsed, CodexPluginAdd)
                    self.assertEqual("release_candidate", parsed.version)
                if surface is CodexProtocolSurface.MARKETPLACE_LIST:
                    assert isinstance(parsed, CodexMarketplaceList)
                    self.assertEqual(2, len(parsed.marketplaces))
                    self.assertIsNotNone(parsed.marketplaces[0].marketplaceSource)
                    self.assertIsNone(parsed.marketplaces[1].marketplaceSource)
                if surface is CodexProtocolSurface.PLUGIN_LIST:
                    assert isinstance(parsed, CodexPluginList)
                    self.assertIsNotNone(parsed.installed[0].marketplaceSource)
                    self.assertIsNone(parsed.available[0].marketplaceSource)
        marketplace_payload = parse_codex_protocol_payload(
            CodexProtocolSurface.MARKETPLACE_ADD,
            _json_bytes(_canonical_payload(CodexProtocolSurface.MARKETPLACE_ADD)),
        )
        assert isinstance(marketplace_payload, CodexMarketplaceAdd)
        with self.assertRaises(ValidationError):
            CodexProtocolAccepted(surface=CodexProtocolSurface.PLUGIN_ADD, payload=marketplace_payload)

    def test_t2_every_surface_rejects_frozen_schema_boundary_cells(self) -> None:
        required = {
            CodexProtocolSurface.MARKETPLACE_ADD: ("marketplaceName", "installedRoot", "alreadyAdded"),
            CodexProtocolSurface.MARKETPLACE_LIST: ("marketplaces",),
            CodexProtocolSurface.MARKETPLACE_REMOVE: ("marketplaceName", "installedRoot"),
            CodexProtocolSurface.PLUGIN_ADD: (
                "pluginId",
                "name",
                "marketplaceName",
                "version",
                "installedPath",
                "authPolicy",
            ),
            CodexProtocolSurface.PLUGIN_LIST: ("installed", "available"),
            CodexProtocolSurface.PLUGIN_REMOVE: ("pluginId", "name", "marketplaceName"),
        }
        text_fields = {
            CodexProtocolSurface.MARKETPLACE_ADD: ("marketplaceName", "installedRoot"),
            CodexProtocolSurface.MARKETPLACE_LIST: (),
            CodexProtocolSurface.MARKETPLACE_REMOVE: ("marketplaceName", "installedRoot"),
            CodexProtocolSurface.PLUGIN_ADD: (
                "pluginId",
                "name",
                "marketplaceName",
                "version",
                "installedPath",
                "authPolicy",
            ),
            CodexProtocolSurface.PLUGIN_LIST: (),
            CodexProtocolSurface.PLUGIN_REMOVE: ("pluginId", "name", "marketplaceName"),
        }
        for surface in CodexProtocolSurface:
            payload = _canonical_payload(surface)
            with self.subTest(surface=surface.value, cell="empty"):
                self._assert_rejected(surface, b"{}")
            with self.subTest(surface=surface.value, cell="extra"):
                altered = dict(payload)
                altered["invented"] = "no"
                self._assert_rejected(surface, _json_bytes(altered))
            for field in required[surface]:
                with self.subTest(surface=surface.value, field=field, cell="missing"):
                    altered = dict(payload)
                    del altered[field]
                    self._assert_rejected(surface, _json_bytes(altered))
                with self.subTest(surface=surface.value, field=field, cell="null"):
                    altered = dict(payload)
                    altered[field] = None
                    self._assert_rejected(surface, _json_bytes(altered))
                with self.subTest(surface=surface.value, field=field, cell="wrong"):
                    altered = dict(payload)
                    altered[field] = 1
                    self._assert_rejected(surface, _json_bytes(altered))
            for field in text_fields[surface]:
                with self.subTest(surface=surface.value, field=field, cell="blank"):
                    altered = dict(payload)
                    altered[field] = " "
                    self._assert_rejected(surface, _json_bytes(altered))
            with self.subTest(surface=surface.value, cell="malformed"):
                self._assert_rejected(surface, b"{")
            with self.subTest(surface=surface.value, cell="utf8"):
                self._assert_rejected(surface, b"\xff")
        self._assert_reason(
            CodexProtocolSurface.MARKETPLACE_ADD,
            b'{"marketplaceName":"first","marketplaceName":"second","installedRoot":"root","alreadyAdded":false}',
            CodexProtocolRejectReason.DUPLICATE_KEY,
        )
        self._assert_rejected(
            CodexProtocolSurface.MARKETPLACE_LIST,
            _json_bytes({"marketplaces": [{"name": "m", "root": "r", "marketplaceSource": None}]}),
        )
        self._assert_rejected(
            CodexProtocolSurface.PLUGIN_LIST,
            _json_bytes(
                {
                    "installed": [
                        {
                            "pluginId": "id",
                            "name": "name",
                            "marketplaceName": "market",
                            "version": "v",
                            "installed": 1,
                            "enabled": True,
                            "source": "source",
                            "installPolicy": "policy",
                            "authPolicy": "auth",
                        }
                    ],
                    "available": [],
                }
            ),
        )
        self._assert_list_entry_rejections(
            CodexProtocolSurface.MARKETPLACE_LIST,
            "marketplaces",
            ("name", "root"),
            ("name", "root"),
        )
        self._assert_list_entry_rejections(
            CodexProtocolSurface.PLUGIN_LIST,
            "installed",
            (
                "pluginId",
                "name",
                "marketplaceName",
                "version",
                "installed",
                "enabled",
                "source",
                "installPolicy",
                "authPolicy",
            ),
            ("pluginId", "name", "marketplaceName", "version", "source", "installPolicy", "authPolicy"),
        )
        self._assert_source_rejections(CodexProtocolSurface.MARKETPLACE_LIST, "marketplaces")
        self._assert_source_rejections(CodexProtocolSurface.PLUGIN_LIST, "installed")
        self._assert_list_entry_rejections(
            CodexProtocolSurface.PLUGIN_LIST,
            "available",
            (
                "pluginId",
                "name",
                "marketplaceName",
                "version",
                "installed",
                "enabled",
                "source",
                "installPolicy",
                "authPolicy",
            ),
            ("pluginId", "name", "marketplaceName", "version", "source", "installPolicy", "authPolicy"),
        )

    def test_r02_cr125_deep_array_maps_recursion_error_to_malformed_json(self) -> None:
        raw = b"[" * 1_500 + b"]" * 1_500

        self.assertLess(len(raw), MAX_RESPONSE_BYTES)
        self._assert_reason(
            CodexProtocolSurface.MARKETPLACE_ADD,
            raw,
            CodexProtocolRejectReason.MALFORMED_JSON,
        )

    def test_r02_cr125_large_integer_maps_value_error_to_malformed_json(self) -> None:
        raw = b'{"value":' + b"9" * 5_000 + b"}"

        self.assertLess(len(raw), MAX_RESPONSE_BYTES)
        self._assert_reason(
            CodexProtocolSurface.MARKETPLACE_ADD,
            raw,
            CodexProtocolRejectReason.MALFORMED_JSON,
        )

    def test_t3_real_child_proves_all_six_payloads_are_not_parent_synthesized(self) -> None:
        allocator, lease = self._lease("environment-owner-3333444455556666")
        overlay_keys = tuple(entry.key.value for entry in lease.overlay.entries)
        parent_environment = {key: os.environ.get(key) for key in overlay_keys}
        with tempfile.NamedTemporaryFile(prefix="codex-protocol-sibling-", delete=False) as sibling:
            sibling.write(b"outside")
            sibling_path = Path(sibling.name)
        try:
            runner = RecordingRunner()
            fixture = CodexProtocolFixture(runner, ExactResponseFilePort())
            for surface in CodexProtocolSurface:
                with self.subTest(surface=surface.value):
                    result = fixture.run(lease, surface)
                    self.assertIsInstance(result, CodexProtocolAccepted)
                    assert isinstance(result, CodexProtocolAccepted)
                    self.assertEqual(surface, result.surface)
                    self.assertEqual((str(FIXTURE_CHILD), surface.value), runner.arguments[-1])
                    self.assertNotIn("child-only", runner.arguments[-1])
                    self.assertFalse(self._response_path(lease).exists())
            self.assertEqual(b"outside", sibling_path.read_bytes())
            self.assertEqual(parent_environment, {key: os.environ.get(key) for key in parent_environment})
        finally:
            sibling_path.unlink()
            self._teardown(allocator, lease)

    def test_t4_collision_faults_and_response_topology_are_finite_and_exact(self) -> None:
        allocator, lease = self._lease("environment-owner-4444555566667777")
        response = self._response_path(lease)
        overlay_keys = tuple(entry.key.value for entry in lease.overlay.entries)
        parent_environment = {key: os.environ.get(key) for key in overlay_keys}
        with tempfile.NamedTemporaryFile(prefix="codex-protocol-fault-sibling-", delete=False) as sibling:
            sibling.write(b"outside")
            sibling_path = Path(sibling.name)
        try:
            collision_runner = RecordingRunner()
            response.write_bytes(b"foreign")
            collision = CodexProtocolFixture(collision_runner, ExactResponseFilePort()).run(
                lease,
                CodexProtocolSurface.MARKETPLACE_ADD,
            )
            self._assert_rejection(collision, CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID)
            self.assertEqual([], collision_runner.arguments)
            self.assertEqual(b"foreign", response.read_bytes())
            response.unlink()

            target = Path(tempfile.mkdtemp(prefix="codex-protocol-response-target-"))
            try:
                created = subprocess.run(
                    ("cmd.exe", "/d", "/c", "mklink", "/J", str(response), str(target)),
                    check=False,
                    shell=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                self.assertEqual(0, created.returncode)
                self.assertNotEqual(0, response.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
                reparse_runner = RecordingRunner()
                reparse = CodexProtocolFixture(reparse_runner, ExactResponseFilePort()).run(
                    lease,
                    CodexProtocolSurface.MARKETPLACE_ADD,
                )
                self._assert_rejection(reparse, CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID)
                self.assertEqual([], reparse_runner.arguments)
                self.assertEqual((), tuple(target.iterdir()))
            finally:
                if response.exists():
                    response.rmdir()
                target.rmdir()

            for shape, expected in (
                (InjectedResponseShape.OVERSIZE, CodexProtocolRejectReason.RESPONSE_TOO_LARGE),
                (InjectedResponseShape.DIRECTORY, CodexProtocolRejectReason.CLEANUP_FAILED),
                (InjectedResponseShape.INVALID_UTF8, CodexProtocolRejectReason.INVALID_UTF8),
                (InjectedResponseShape.MALFORMED_JSON, CodexProtocolRejectReason.MALFORMED_JSON),
                (InjectedResponseShape.SCHEMA_INVALID, CodexProtocolRejectReason.SCHEMA_INVALID),
            ):
                with self.subTest(shape=shape.value):
                    runner = InjectedSuccessRunner(shape)
                    result = CodexProtocolFixture(runner, ExactResponseFilePort()).run(
                        lease,
                        CodexProtocolSurface.PLUGIN_ADD,
                    )
                    self._assert_rejection(result, expected)
                    self.assertEqual(1, runner.call_count)
                    if response.is_dir():
                        response.rmdir()
                    self.assertFalse(response.exists())

            missing = CodexProtocolFixture(MissingResponseRunner(), ExactResponseFilePort()).run(
                lease,
                CodexProtocolSurface.PLUGIN_LIST,
            )
            self._assert_rejection(missing, CodexProtocolRejectReason.RESPONSE_MISSING)
            failed = CodexProtocolFixture(FailedProcessRunner(), ExactResponseFilePort()).run(
                lease,
                CodexProtocolSurface.PLUGIN_REMOVE,
            )
            self._assert_rejection(failed, CodexProtocolRejectReason.PROCESS_FAILED)

            read_failure = CodexProtocolFixture(RecordingRunner(), ReadFailureResponsePort()).run(
                lease,
                CodexProtocolSurface.PLUGIN_LIST,
            )
            self._assert_rejection(read_failure, CodexProtocolRejectReason.RESPONSE_BOUNDARY_INVALID)
            self.assertFalse(response.exists())

            cleanup_failure = CodexProtocolFixture(RecordingRunner(), CleanupFailureResponsePort()).run(
                lease,
                CodexProtocolSurface.MARKETPLACE_REMOVE,
            )
            self._assert_rejection(cleanup_failure, CodexProtocolRejectReason.CLEANUP_FAILED)
            self.assertTrue(response.is_file())
            response.unlink()
            self.assertEqual(b"outside", sibling_path.read_bytes())
            self.assertEqual(parent_environment, {key: os.environ.get(key) for key in parent_environment})
        finally:
            sibling_path.unlink()
            self._teardown(allocator, lease)
        self.assertEqual(set(), self._owned_environment_roots())

    def _assert_rejected(self, surface: CodexProtocolSurface, raw: bytes) -> None:
        parsed = parse_codex_protocol_payload(surface, raw)
        self.assertIsInstance(parsed, CodexProtocolRejectReason)

    def _assert_list_entry_rejections(
        self,
        surface: CodexProtocolSurface,
        container: str,
        required: tuple[str, ...],
        text_fields: tuple[str, ...],
    ) -> None:
        payload = _canonical_payload(surface)
        entries = payload[container]
        assert isinstance(entries, list)
        entry = entries[0]
        assert isinstance(entry, dict)
        for field in required:
            for cell, value in (("null", None), ("wrong", 1)):
                with self.subTest(surface=surface.value, container=container, field=field, cell=cell):
                    altered_entry = dict(entry)
                    altered_entry[field] = value
                    altered = dict(payload)
                    altered[container] = [altered_entry]
                    if surface is CodexProtocolSurface.PLUGIN_LIST and container == "installed":
                        altered["available"] = []
                    self._assert_rejected(surface, _json_bytes(altered))
            with self.subTest(surface=surface.value, container=container, field=field, cell="missing"):
                altered_entry = dict(entry)
                del altered_entry[field]
                altered = dict(payload)
                altered[container] = [altered_entry]
                if surface is CodexProtocolSurface.PLUGIN_LIST and container == "installed":
                    altered["available"] = []
                self._assert_rejected(surface, _json_bytes(altered))
        for field in text_fields:
            with self.subTest(surface=surface.value, container=container, field=field, cell="blank"):
                altered_entry = dict(entry)
                altered_entry[field] = " "
                altered = dict(payload)
                altered[container] = [altered_entry]
                if surface is CodexProtocolSurface.PLUGIN_LIST and container == "installed":
                    altered["available"] = []
                self._assert_rejected(surface, _json_bytes(altered))
        with self.subTest(surface=surface.value, container=container, cell="nested-extra"):
            altered_entry = dict(entry)
            altered_entry["invented"] = "no"
            altered = dict(payload)
            altered[container] = [altered_entry]
            if surface is CodexProtocolSurface.PLUGIN_LIST and container == "installed":
                altered["available"] = []
            self._assert_rejected(surface, _json_bytes(altered))

    def _assert_source_rejections(self, surface: CodexProtocolSurface, container: str) -> None:
        payload = _canonical_payload(surface)
        entries = payload[container]
        assert isinstance(entries, list)
        entry = entries[0]
        assert isinstance(entry, dict)
        source = entry["marketplaceSource"]
        assert isinstance(source, dict)
        for field in ("type", "value"):
            for cell, value in (("null", None), ("wrong", 1), ("blank", " ")):
                with self.subTest(surface=surface.value, field=field, cell=cell):
                    altered_source = dict(source)
                    altered_source[field] = value
                    self._assert_source_payload_rejected(surface, container, entry, altered_source)
            with self.subTest(surface=surface.value, field=field, cell="missing"):
                altered_source = dict(source)
                del altered_source[field]
                self._assert_source_payload_rejected(surface, container, entry, altered_source)
        altered_source = dict(source)
        altered_source["invented"] = "no"
        self._assert_source_payload_rejected(surface, container, entry, altered_source)

    def _assert_source_payload_rejected(
        self,
        surface: CodexProtocolSurface,
        container: str,
        entry: dict[object, object],
        source: dict[object, object],
    ) -> None:
        altered_entry = dict(entry)
        altered_entry["marketplaceSource"] = source
        payload = _canonical_payload(surface)
        payload[container] = [altered_entry]
        if surface is CodexProtocolSurface.PLUGIN_LIST and container == "installed":
            payload["available"] = []
        self._assert_rejected(surface, _json_bytes(payload))

    def _assert_reason(self, surface: CodexProtocolSurface, raw: bytes, expected: CodexProtocolRejectReason) -> None:
        self.assertEqual(expected, parse_codex_protocol_payload(surface, raw))

    def _assert_rejection(self, result: CodexProtocolAccepted | CodexProtocolRejected, expected: CodexProtocolRejectReason) -> None:
        self.assertIsInstance(result, CodexProtocolRejected)
        assert isinstance(result, CodexProtocolRejected)
        self.assertEqual(expected, result.reason)

    @staticmethod
    def _response_path(lease: EnvironmentLease) -> Path:
        return lease.temporary.absolute.path / RESPONSE_FILE_NAME

    def _lease(self, owner: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease]:
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        provisioned = allocator.provision(EnvironmentOwnerId(value=owner))
        self.assertIsInstance(provisioned, ProvisionedEnvironment)
        assert isinstance(provisioned, ProvisionedEnvironment)
        return allocator, provisioned.environment

    def _teardown(self, allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
        result = allocator.teardown(lease)
        self.assertEqual(TeardownStatus.REMOVED, result.status)

    @staticmethod
    def _owned_environment_roots() -> set[Path]:
        temporary_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        return {
            child
            for child in temporary_parent.iterdir()
            if child.is_dir() and child.name.startswith(ENVIRONMENT_PREFIX)
        }


def _invocation(request: ChildProcessRequest) -> ProcessInvocation:
    return ProcessInvocation(
        executable=request.executable,
        original_arguments=request.arguments,
        effective_argv=EffectiveArgv(values=(request.executable.value, *request.arguments.values)),
    )


def _successful_observation(request: ChildProcessRequest) -> SuccessfulProcessObservation:
    return SuccessfulProcessObservation(invocation=_invocation(request), exit_code=ProcessExitCode(value=0))


def _json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def _canonical_payload(surface: CodexProtocolSurface) -> dict[str, object]:
    source = {"type": "local", "value": "child-only-source"}
    marketplace_entry = {"name": "child-market", "root": "child-root", "marketplaceSource": source}
    marketplace_without_source = {"name": "child-market-absent", "root": "child-root-absent"}
    plugin_entry = {
        "pluginId": "child-plugin-id",
        "name": "child-plugin",
        "marketplaceName": "child-market",
        "version": "release_candidate",
        "installed": True,
        "enabled": True,
        "source": "child-source",
        "installPolicy": "child-install-policy",
        "authPolicy": "child-auth-policy",
        "marketplaceSource": source,
    }
    plugin_without_source = dict(plugin_entry)
    plugin_without_source["pluginId"] = "child-plugin-available"
    del plugin_without_source["marketplaceSource"]
    if surface is CodexProtocolSurface.MARKETPLACE_ADD:
        return {"marketplaceName": "child-market", "installedRoot": "child-root", "alreadyAdded": False}
    if surface is CodexProtocolSurface.MARKETPLACE_LIST:
        return {"marketplaces": [marketplace_entry, marketplace_without_source]}
    if surface is CodexProtocolSurface.MARKETPLACE_REMOVE:
        return {"marketplaceName": "child-market", "installedRoot": "child-root"}
    if surface is CodexProtocolSurface.PLUGIN_ADD:
        return {
            "pluginId": "child-plugin-id",
            "name": "child-plugin",
            "marketplaceName": "child-market",
            "version": "release_candidate",
            "installedPath": "child-installed-path",
            "authPolicy": "child-auth-policy",
        }
    if surface is CodexProtocolSurface.PLUGIN_LIST:
        return {"installed": [plugin_entry], "available": [plugin_without_source]}
    return {"pluginId": "child-plugin-id", "name": "child-plugin", "marketplaceName": "child-market"}


if __name__ == "__main__":
    unittest.main()
