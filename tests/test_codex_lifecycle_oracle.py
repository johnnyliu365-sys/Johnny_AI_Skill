"""O1-O6 closure for the persisted, child-backed Codex lifecycle oracle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TypeVar
import unittest

from library.local_orchestration.host_contracts import CodexMarketplaceList, CodexPluginList
from tests.staging.codex_lifecycle_oracle.contracts import (
    ORACLE_COMMAND_FILE_NAME,
    ORACLE_STATE_FILE_NAME,
    OracleAction,
    OracleBlockReason,
    OracleBlocked,
    OracleCommand,
    OracleCompleted,
    OracleForeignSeeded,
    OracleIdentity,
    OracleMarketplaceRecord,
    OraclePluginRecord,
    OracleRunResult,
    OracleAbsent,
)
from tests.staging.codex_lifecycle_oracle.oracle import CodexLifecycleOracle
from tests.staging.codex_lifecycle_oracle.protocol_runner import CodexLifecycleOracleRunner, ORACLE_CHILD
from tests.staging.codex_protocol.contracts import (
    CodexProtocolAccepted,
    CodexMarketplaceAdd,
    CodexMarketplaceRemove,
    CodexPluginAdd,
    CodexPluginRemove,
    CodexProtocolRejected,
    CodexProtocolSurface,
    ExactResponseFilePort,
)
from tests.staging.codex_protocol.fixture import CodexProtocolFixture
from tests.staging.environment_core.contracts import (
    EnvironmentLease,
    EnvironmentLocator,
    EnvironmentOverlay,
    EnvironmentOwnerId,
    ProvisionedEnvironment,
    TeardownStatus,
)
from tests.staging.environment_core.environment import DisposableEnvironmentAllocator
from tests.staging.process_runner.contracts import ProcessInvocation, StartedChildProcess
from tests.staging.process_runner.runner import BoundedChildProcessRunner, SubprocessProcessPort

LOGICAL_INSTALLED_PATH = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\owned-plugin"

IDENTITY = OracleIdentity(
    marketplace_name="owned-market",
    marketplace_root="owned-root",
    plugin_id="owned-plugin",
    plugin_name="owned-plugin-name",
    plugin_version="release_candidate",
    plugin_source="owned-source",
    plugin_install_policy="owned-install-policy",
    plugin_auth_policy="owned-auth-policy",
    plugin_installed_path=LOGICAL_INSTALLED_PATH,
)

PayloadType = TypeVar("PayloadType")


class FailingProcessPort:
    """A required typed process port that deterministically fails before child start."""

    def start(
        self,
        invocation: ProcessInvocation,
        working_directory: EnvironmentLocator,
        overlay: EnvironmentOverlay,
    ) -> StartedChildProcess:
        raise OSError("injected process failure")


class OrdinaryFixtureFailure(CodexProtocolFixture):
    """Raises only an ordinary dependency error after the command file is written."""

    def __init__(self, runner: CodexLifecycleOracleRunner) -> None:
        super().__init__(runner, ExactResponseFilePort())

    def run(
        self,
        lease: EnvironmentLease,
        surface: CodexProtocolSurface,
    ) -> CodexProtocolAccepted | CodexProtocolRejected:
        raise OSError("injected fixture dependency failure")


class CleanupFailureFixture(CodexProtocolFixture):
    """Makes only the fixed command locator non-ordinary before failing."""

    def __init__(self, runner: CodexLifecycleOracleRunner) -> None:
        super().__init__(runner, ExactResponseFilePort())

    def run(
        self,
        lease: EnvironmentLease,
        surface: CodexProtocolSurface,
    ) -> CodexProtocolAccepted | CodexProtocolRejected:
        command_path = lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME
        command_path.unlink()
        command_path.mkdir()
        raise OSError("injected fixture dependency failure")


class FixtureFailureOracle(CodexLifecycleOracle):
    """Uses a typed fixture failure without changing the production composition."""

    def __init__(self, runner: CodexLifecycleOracleRunner, fixture: CodexProtocolFixture) -> None:
        super().__init__(runner)
        self._fixture = fixture


class CodexLifecycleOracleTests(unittest.TestCase):
    def test_e0_logical_installed_path_is_a_required_identity_contract(self) -> None:
        identity = OracleIdentity(
            marketplace_name="owned-market",
            marketplace_root="owned-root",
            plugin_id="owned-plugin",
            plugin_name="owned-plugin-name",
            plugin_version="release_candidate",
            plugin_source="owned-source",
            plugin_install_policy="owned-install-policy",
            plugin_auth_policy="owned-auth-policy",
            plugin_installed_path=LOGICAL_INSTALLED_PATH,
        )
        self.assertEqual(LOGICAL_INSTALLED_PATH, identity.plugin_installed_path)

    def test_e0_logical_installed_path_round_trips_response_state_digest_and_physical_locator(self) -> None:
        allocator, lease, oracle = self._ready("0000000000000070")
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
            plugin = self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_ADD), CodexPluginAdd)
            state = json.loads(oracle.state_path(lease).read_text(encoding="utf-8"))
            record = state["plugins"][0]
            payload_path = oracle.payload_root(lease) / "plugins" / f"{IDENTITY.plugin_id}.json"
            payload = payload_path.read_bytes()
            self.assertEqual(IDENTITY.plugin_installed_path, plugin.installedPath)
            self.assertEqual(IDENTITY.plugin_installed_path, record["installed_path"])
            self.assertEqual(f"plugins/{IDENTITY.plugin_id}.json", record["locator"])
            self.assertEqual("plugins/owned-plugin.json", payload_path.relative_to(oracle.payload_root(lease)).as_posix())
            self.assertIn(IDENTITY.plugin_installed_path.encode("utf-8"), payload)
            self.assertEqual(record["digest"], hashlib.sha256(payload).hexdigest())
        finally:
            self._teardown(allocator, lease)

    def test_e0_invalid_logical_paths_are_rejected_before_oracle_mutation(self) -> None:
        invalid_paths = (
            r"plugins\owned-plugin",
            "file:///C:/Users/oracle/plugin",
            r"C:\Users\oracle\%2Fplugin",
            r"C:\Users\oracle\%2e%2e\plugin",
            r"C:\Users\oracle\..\plugin",
            "C:/Users/oracle/plugin",
            r"C:\Users\oracle\plugin" + "\\",
            r"\Users\oracle\plugin",
            "C:\\Users\\oracle\\plugin\x00",
        )
        for index, value in enumerate(invalid_paths, start=71):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    OracleIdentity(
                        marketplace_name=IDENTITY.marketplace_name,
                        marketplace_root=IDENTITY.marketplace_root,
                        plugin_id=IDENTITY.plugin_id,
                        plugin_name=IDENTITY.plugin_name,
                        plugin_version=IDENTITY.plugin_version,
                        plugin_source=IDENTITY.plugin_source,
                        plugin_install_policy=IDENTITY.plugin_install_policy,
                        plugin_auth_policy=IDENTITY.plugin_auth_policy,
                        plugin_installed_path=value,
                    )
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    state_before = oracle.state_path(lease).read_bytes()
                    payload_before = tuple(oracle.payload_root(lease).rglob("*"))
                    unsafe_identity = IDENTITY.model_copy(update={"plugin_installed_path": value})
                    unsafe_command = OracleCommand.model_construct(action=OracleAction.PLUGIN_ADD, identity=unsafe_identity)
                    self._assert_blocked(oracle.run(lease, unsafe_command), OracleBlockReason.COMMAND_INVALID)
                    self.assertEqual(state_before, oracle.state_path(lease).read_bytes())
                    self.assertEqual(payload_before, tuple(oracle.payload_root(lease).rglob("*")))
                    self.assertFalse((lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME).exists())
                finally:
                    self._teardown(allocator, lease)

    def test_e0_persisted_logical_path_old_schema_extra_and_tamper_fail_closed(self) -> None:
        cells = (
            ("old-schema", OracleBlockReason.STATE_INVALID),
            ("extra-field", OracleBlockReason.STATE_INVALID),
            ("malformed", OracleBlockReason.STATE_INVALID),
            ("state-path-tamper", OracleBlockReason.DIGEST_MISMATCH),
            ("payload-path-tamper", OracleBlockReason.DIGEST_MISMATCH),
        )
        for index, (cell, expected) in enumerate(cells, start=80):
            with self.subTest(cell=cell):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
                    self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_ADD), CodexPluginAdd)
                    state_path = oracle.state_path(lease)
                    payload_path = oracle.payload_root(lease) / "plugins" / f"{IDENTITY.plugin_id}.json"
                    if cell == "payload-path-tamper":
                        payload_path.write_bytes(payload_path.read_bytes().replace(IDENTITY.plugin_installed_path.encode("utf-8"), b"C:\\Foreign\\plugin"))
                    else:
                        state = json.loads(state_path.read_text(encoding="utf-8"))
                        record = state["plugins"][0]
                        if cell == "old-schema":
                            del record["installed_path"]
                        if cell == "extra-field":
                            record["extra"] = "forbidden"
                        if cell == "malformed":
                            record["installed_path"] = "plugins/owned-plugin.json"
                        if cell == "state-path-tamper":
                            record["installed_path"] = r"C:\Users\oracle\AppData\Local\JohnnyAIWorkflow\plugins\other-plugin"
                        state_path.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
                    self._assert_blocked(self._run(oracle, lease, OracleAction.PLUGIN_LIST), expected)
                finally:
                    self._teardown(allocator, lease)

    def test_o1_serial_owned_lifecycle_uses_fresh_child_lists(self) -> None:
        allocator, lease, oracle = self._ready("0000000000000001")
        try:
            initialized = oracle.initialize(lease)
            self._assert_completed(initialized, CodexMarketplaceList)
            marketplace_add = self._run(oracle, lease, OracleAction.MARKETPLACE_ADD)
            marketplace = self._assert_completed(marketplace_add, CodexMarketplaceAdd)
            self.assertEqual(IDENTITY.marketplace_name, marketplace.marketplaceName)
            plugin_add = self._run(oracle, lease, OracleAction.PLUGIN_ADD)
            plugin = self._assert_completed(plugin_add, CodexPluginAdd)
            self.assertEqual(IDENTITY.plugin_id, plugin.pluginId)
            self.assertEqual(IDENTITY.plugin_installed_path, plugin.installedPath)
            markets = self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_LIST), CodexMarketplaceList)
            plugins = self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_LIST), CodexPluginList)
            self.assertEqual((IDENTITY.marketplace_name,), tuple(entry.name for entry in markets.marketplaces))
            self.assertEqual((IDENTITY.plugin_id,), tuple(entry.pluginId for entry in plugins.installed))
            self.assertEqual((), tuple(plugins.available))
        finally:
            self._teardown(allocator, lease)

    def test_o2_exact_removal_precedes_fresh_physical_absence(self) -> None:
        allocator, lease, oracle = self._ready("0000000000000002")
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
            self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_ADD), CodexPluginAdd)
            plugin_remove = self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_REMOVE), CodexPluginRemove)
            self.assertEqual(IDENTITY.plugin_id, plugin_remove.pluginId)
            marketplace_remove = self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_REMOVE), CodexMarketplaceRemove)
            self.assertEqual(IDENTITY.marketplace_name, marketplace_remove.marketplaceName)
            absent = self._run(oracle, lease, OracleAction.ABSENCE)
            self.assertIsInstance(absent, OracleAbsent)
            self.assertFalse(oracle.state_path(lease).exists())
            self.assertFalse((oracle.payload_root(lease) / "marketplaces" / "owned-market.json").exists())
            self.assertFalse((oracle.payload_root(lease) / "plugins" / "owned-plugin.json").exists())
        finally:
            self._teardown(allocator, lease)

    def test_o3_foreign_records_are_preserved_and_never_authorize_owned_removal(self) -> None:
        allocator, lease, oracle = self._ready("0000000000000003")
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            foreign_marketplace = self._foreign_marketplace("foreign-market", "foreign-root")
            foreign_plugin = self._foreign_plugin("foreign-plugin", IDENTITY.plugin_name, "foreign-market")
            self.assertIsInstance(oracle.seed_foreign_marketplace(lease, foreign_marketplace), OracleForeignSeeded)
            self.assertIsInstance(oracle.seed_foreign_plugin(lease, foreign_plugin), OracleForeignSeeded)
            foreign_market_bytes = (oracle.payload_root(lease) / foreign_marketplace.locator).read_bytes()
            foreign_plugin_bytes = (oracle.payload_root(lease) / foreign_plugin.locator).read_bytes()
            self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
            self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_ADD), CodexPluginAdd)
            plugins = self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_LIST), CodexPluginList)
            self.assertEqual({IDENTITY.plugin_id, foreign_plugin.plugin_id}, {entry.pluginId for entry in plugins.installed})
            self._assert_completed(self._run(oracle, lease, OracleAction.PLUGIN_REMOVE), CodexPluginRemove)
            self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_REMOVE), CodexMarketplaceRemove)
            self.assertEqual(foreign_market_bytes, (oracle.payload_root(lease) / foreign_marketplace.locator).read_bytes())
            self.assertEqual(foreign_plugin_bytes, (oracle.payload_root(lease) / foreign_plugin.locator).read_bytes())
            foreign_state = json.loads(oracle.state_path(lease).read_text(encoding="utf-8"))
            self.assertEqual(foreign_plugin.installed_path, foreign_state["foreign_plugins"][0]["installed_path"])
            self.assertEqual(f"plugins/{foreign_plugin.plugin_id}.json", foreign_state["foreign_plugins"][0]["locator"])
            self.assertFalse((oracle.payload_root(lease) / "plugins" / "owned-plugin.json").exists())
        finally:
            self._teardown(allocator, lease)

    def test_cr126_duplicate_foreign_identities_are_blocked_before_fresh_child_list(self) -> None:
        cells: tuple[
            tuple[
                str,
                OracleMarketplaceRecord | OraclePluginRecord,
                str,
            ],
            ...,
        ] = (
            ("foreign-marketplace", self._foreign_marketplace("foreign-duplicate-market", "foreign-root"), "marketplace"),
            ("foreign-plugin", self._foreign_plugin("foreign-duplicate-plugin", "foreign-name", "foreign-market"), "plugin"),
        )
        for index, (label, record, collection) in enumerate(cells, start=50):
            with self.subTest(collection=label):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    if collection == "marketplace":
                        if not isinstance(record, OracleMarketplaceRecord):
                            raise AssertionError("marketplace test record type mismatch")
                        self.assertIsInstance(oracle.seed_foreign_marketplace(lease, record), OracleForeignSeeded)
                        duplicate = oracle.seed_foreign_marketplace(lease, record)
                        self._assert_foreign_seed_blocked(duplicate, OracleBlockReason.STATE_INVALID)
                        response = self._run(oracle, lease, OracleAction.MARKETPLACE_LIST)
                        marketplaces = self._assert_completed(response, CodexMarketplaceList)
                        self.assertEqual((record.name,), tuple(entry.name for entry in marketplaces.marketplaces))
                    else:
                        if not isinstance(record, OraclePluginRecord):
                            raise AssertionError("plugin test record type mismatch")
                        self.assertIsInstance(oracle.seed_foreign_plugin(lease, record), OracleForeignSeeded)
                        duplicate = oracle.seed_foreign_plugin(lease, record)
                        self._assert_foreign_seed_blocked(duplicate, OracleBlockReason.STATE_INVALID)
                        response = self._run(oracle, lease, OracleAction.PLUGIN_LIST)
                        plugins = self._assert_completed(response, CodexPluginList)
                        self.assertEqual((record.plugin_id,), tuple(entry.pluginId for entry in plugins.installed))
                finally:
                    self._teardown(allocator, lease)

    def test_cr126_tampered_foreign_duplicates_are_rejected_by_the_fresh_child(self) -> None:
        cells: tuple[tuple[str, OracleAction, str, OracleMarketplaceRecord | OraclePluginRecord], ...] = (
            (
                "foreign-marketplace",
                OracleAction.MARKETPLACE_LIST,
                "foreign_marketplaces",
                self._foreign_marketplace("foreign-child-market", "foreign-root"),
            ),
            (
                "foreign-plugin",
                OracleAction.PLUGIN_LIST,
                "foreign_plugins",
                self._foreign_plugin("foreign-child-plugin", "foreign-name", "foreign-market"),
            ),
        )
        for index, (label, action, collection, record) in enumerate(cells, start=60):
            with self.subTest(collection=label):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    if isinstance(record, OracleMarketplaceRecord):
                        self.assertIsInstance(oracle.seed_foreign_marketplace(lease, record), OracleForeignSeeded)
                    else:
                        self.assertIsInstance(oracle.seed_foreign_plugin(lease, record), OracleForeignSeeded)
                    state_path = oracle.state_path(lease)
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                    state[collection].append(dict(state[collection][0]))
                    state_path.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
                    self._assert_blocked(self._run(oracle, lease, action), OracleBlockReason.STATE_INVALID)
                finally:
                    self._teardown(allocator, lease)

    def test_o4_invalid_state_and_topology_cells_are_finite_before_false_results(self) -> None:
        cells = (
            ("missing-state", OracleBlockReason.STATE_MISSING),
            ("top-level-extra", OracleBlockReason.STATE_INVALID),
            ("null-collection", OracleBlockReason.STATE_INVALID),
            ("duplicate-owned", OracleBlockReason.STATE_INVALID),
            ("state-present-file-absent", OracleBlockReason.TOPOLOGY_INVALID),
            ("file-present-state-absent", OracleBlockReason.TOPOLOGY_INVALID),
            ("stale-digest", OracleBlockReason.DIGEST_MISMATCH),
            ("wrong-file-kind", OracleBlockReason.TOPOLOGY_INVALID),
        )
        for index, (cell, expected) in enumerate(cells, start=4):
            with self.subTest(cell=cell):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
                    state_path = oracle.state_path(lease)
                    payload_path = oracle.payload_root(lease) / "marketplaces" / "owned-market.json"
                    if cell == "missing-state":
                        state_path.unlink()
                    else:
                        state = json.loads(state_path.read_text(encoding="utf-8"))
                        if cell == "top-level-extra":
                            state["extra"] = "forbidden"
                        if cell == "null-collection":
                            state["marketplaces"] = None
                        if cell == "duplicate-owned":
                            state["marketplaces"].append(dict(state["marketplaces"][0]))
                        if cell == "file-present-state-absent":
                            state["marketplaces"] = []
                        if cell == "stale-digest":
                            state["marketplaces"][0]["digest"] = "0" * 64
                        state_path.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
                    if cell == "state-present-file-absent":
                        payload_path.unlink()
                    if cell == "wrong-file-kind":
                        payload_path.unlink()
                        payload_path.mkdir()
                    result = self._run(oracle, lease, OracleAction.MARKETPLACE_LIST)
                    self._assert_blocked(result, expected)
                finally:
                    self._teardown(allocator, lease)
        invalid_locators = (
            "marketplaces/owned-market.jsonx",
            "marketplaces/owned-market.json/",
            "Marketplaces/owned-market.json",
            "marketplaces%2Fowned-market.json",
            "../marketplaces/owned-market.json",
            "",
        )
        for index, locator in enumerate(invalid_locators, start=20):
            with self.subTest(locator=locator):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
                    state_path = oracle.state_path(lease)
                    state = json.loads(state_path.read_text(encoding="utf-8"))
                    state["marketplaces"][0]["locator"] = locator
                    state_path.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
                    self._assert_blocked(self._run(oracle, lease, OracleAction.MARKETPLACE_LIST), OracleBlockReason.STATE_INVALID)
                finally:
                    self._teardown(allocator, lease)
        invalid_command_values: tuple[object, ...] = (None, "", " ", [], {})
        for index, value in enumerate(invalid_command_values, start=30):
            with self.subTest(command_value=repr(value)):
                allocator, lease, oracle = self._ready(f"00000000000000{index:02x}")
                try:
                    self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                    unsafe_identity = OracleIdentity.model_construct(
                        marketplace_name=value,
                        marketplace_root=IDENTITY.marketplace_root,
                        plugin_id=IDENTITY.plugin_id,
                        plugin_name=IDENTITY.plugin_name,
                        plugin_version=IDENTITY.plugin_version,
                        plugin_source=IDENTITY.plugin_source,
                        plugin_install_policy=IDENTITY.plugin_install_policy,
                        plugin_auth_policy=IDENTITY.plugin_auth_policy,
                        plugin_installed_path=IDENTITY.plugin_installed_path,
                    )
                    unsafe_command = OracleCommand.model_construct(action=OracleAction.MARKETPLACE_LIST, identity=unsafe_identity)
                    self._assert_blocked(oracle.run(lease, unsafe_command), OracleBlockReason.COMMAND_INVALID)
                    self.assertFalse((lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME).exists())
                finally:
                    self._teardown(allocator, lease)

    def test_o5_protocol_runner_cannot_synthesize_or_queue_a_response(self) -> None:
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        provisioned = allocator.provision(EnvironmentOwnerId(value="environment-owner-000000000000000c"))
        if not isinstance(provisioned, ProvisionedEnvironment):
            raise AssertionError("failed to provision owned environment")
        lease = provisioned.environment
        runner = CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
        oracle = CodexLifecycleOracle(runner)
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            self._assert_completed(self._run(oracle, lease, OracleAction.MARKETPLACE_ADD), CodexMarketplaceAdd)
            result = self._run(oracle, lease, OracleAction.MARKETPLACE_LIST)
            markets = self._assert_completed(result, CodexMarketplaceList)
            self.assertEqual((IDENTITY.marketplace_name,), tuple(entry.name for entry in markets.marketplaces))
            self.assertEqual(
                (str(Path(sys.executable).resolve(strict=True)), str(ORACLE_CHILD), CodexProtocolSurface.MARKETPLACE_LIST.value),
                runner.last_child_argv,
            )
            self.assertFalse((lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME).exists())
            self.assertFalse((lease.temporary.absolute.path / ".johnny-05s3-response.json").exists())
        finally:
            self._teardown(allocator, lease)

    def test_o6_failures_remain_finite_and_leave_no_command_or_response_residue(self) -> None:
        allocator, lease, oracle = self._ready("000000000000000d")
        failing_oracle = CodexLifecycleOracle(CodexLifecycleOracleRunner(BoundedChildProcessRunner(FailingProcessPort())))
        with tempfile.TemporaryDirectory(prefix="oracle-git-existing-") as existing_text, tempfile.TemporaryDirectory(prefix="oracle-git-empty-") as empty_text:
            existing = Path(existing_text)
            empty = Path(empty_text)
            self._initialize_git(existing, with_file=True)
            self._initialize_git(empty, with_file=False)
            existing_snapshot = self._git_snapshot(existing)
            empty_snapshot = self._git_snapshot(empty)
            try:
                self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
                result = failing_oracle.run(lease, self._command(OracleAction.MARKETPLACE_LIST))
                self._assert_blocked(result, OracleBlockReason.PROCESS_FAILED)
                command_path = lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME
                response_path = lease.temporary.absolute.path / ".johnny-05s3-response.json"
                self.assertFalse(command_path.exists())
                self.assertFalse(response_path.exists())
                command_path.mkdir()
                blocked = self._run(oracle, lease, OracleAction.MARKETPLACE_LIST)
                self._assert_blocked(blocked, OracleBlockReason.COMMAND_INVALID)
                command_path.rmdir()
                self.assertEqual(existing_snapshot, self._git_snapshot(existing))
                self.assertEqual(empty_snapshot, self._git_snapshot(empty))
            finally:
                self._teardown(allocator, lease)

    def test_cr127_ordinary_fixture_error_removes_the_exact_command_file(self) -> None:
        allocator, lease, oracle = self._ready("000000000000003c")
        runner = CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
        failing_oracle = FixtureFailureOracle(runner, OrdinaryFixtureFailure(runner))
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            result = failing_oracle.run(lease, self._command(OracleAction.MARKETPLACE_LIST))
            self._assert_blocked(result, OracleBlockReason.PROCESS_FAILED)
            self.assertFalse((lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME).exists())
        finally:
            self._teardown(allocator, lease)

    def test_cr127_failed_exact_command_cleanup_is_finite(self) -> None:
        allocator, lease, oracle = self._ready("000000000000003d")
        runner = CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
        failing_oracle = FixtureFailureOracle(runner, CleanupFailureFixture(runner))
        command_path = lease.temporary.absolute.path / ORACLE_COMMAND_FILE_NAME
        try:
            self._assert_completed(oracle.initialize(lease), CodexMarketplaceList)
            result = failing_oracle.run(lease, self._command(OracleAction.MARKETPLACE_LIST))
            self._assert_blocked(result, OracleBlockReason.COMMAND_CLEANUP_FAILED)
            self.assertTrue(command_path.is_dir())
            command_path.rmdir()
        finally:
            self._teardown(allocator, lease)

    @staticmethod
    def _command(action: OracleAction) -> OracleCommand:
        return OracleCommand(action=action, identity=IDENTITY)

    def _run(self, oracle: CodexLifecycleOracle, lease: EnvironmentLease, action: OracleAction) -> OracleRunResult:
        return oracle.run(lease, self._command(action))

    @staticmethod
    def _assert_completed(result: OracleRunResult, payload_type: type[PayloadType]) -> PayloadType:
        if not isinstance(result, OracleCompleted):
            raise AssertionError(f"expected completion, received {result}")
        if not isinstance(result.response.payload, payload_type):
            raise AssertionError("response payload type mismatch")
        return result.response.payload

    @staticmethod
    def _assert_blocked(result: OracleRunResult, expected: OracleBlockReason) -> None:
        if not isinstance(result, OracleBlocked):
            raise AssertionError(f"expected blocked result, received {result}")
        if result.reason is not expected:
            raise AssertionError(f"expected {expected}, received {result.reason}")

    @staticmethod
    def _assert_foreign_seed_blocked(
        result: OracleForeignSeeded | OracleBlocked,
        expected: OracleBlockReason,
    ) -> None:
        if not isinstance(result, OracleBlocked):
            raise AssertionError(f"expected blocked foreign seed, received {result}")
        if result.reason is not expected:
            raise AssertionError(f"expected {expected}, received {result.reason}")

    @staticmethod
    def _ready(owner_suffix: str) -> tuple[DisposableEnvironmentAllocator, EnvironmentLease, CodexLifecycleOracle]:
        allocator = DisposableEnvironmentAllocator.from_system_temp()
        provisioned = allocator.provision(EnvironmentOwnerId(value=f"environment-owner-{owner_suffix}"))
        if not isinstance(provisioned, ProvisionedEnvironment):
            raise AssertionError("failed to provision owned environment")
        runner = CodexLifecycleOracleRunner(BoundedChildProcessRunner(SubprocessProcessPort()))
        return allocator, provisioned.environment, CodexLifecycleOracle(runner)

    @staticmethod
    def _teardown(allocator: DisposableEnvironmentAllocator, lease: EnvironmentLease) -> None:
        result = allocator.teardown(lease)
        if result.status is not TeardownStatus.REMOVED:
            raise AssertionError("owned environment teardown did not remove the root")
        if lease.root.path.exists():
            raise AssertionError("owned environment root remains")

    @staticmethod
    def _foreign_marketplace(name: str, root: str) -> OracleMarketplaceRecord:
        digest = hashlib.sha256(f"marketplace|{name}|{root}".encode("utf-8")).hexdigest()
        return OracleMarketplaceRecord(name=name, root=root, locator=f"marketplaces/{name}.json", digest=digest)

    @staticmethod
    def _foreign_plugin(plugin_id: str, name: str, marketplace_name: str) -> OraclePluginRecord:
        installed_path = rf"C:\Foreign\Codex\plugins\{plugin_id}"
        values = (
            plugin_id,
            name,
            marketplace_name,
            "foreign-version",
            "foreign-source",
            "foreign-policy",
            "foreign-auth",
            installed_path,
        )
        digest = hashlib.sha256(("plugin|" + "|".join(values)).encode("utf-8")).hexdigest()
        return OraclePluginRecord(
            plugin_id=plugin_id,
            name=name,
            marketplace_name=marketplace_name,
            version="foreign-version",
            source="foreign-source",
            install_policy="foreign-policy",
            auth_policy="foreign-auth",
            installed_path=installed_path,
            locator=f"plugins/{plugin_id}.json",
            digest=digest,
        )

    @staticmethod
    def _initialize_git(path: Path, with_file: bool) -> None:
        subprocess.run(("git", "init", "-q", str(path)), check=True, shell=False, timeout=5)
        if with_file:
            path.joinpath("sentinel.txt").write_bytes(b"external-sentinel")

    @staticmethod
    def _git_snapshot(path: Path) -> tuple[bytes, bytes]:
        file_value = path.joinpath("sentinel.txt").read_bytes() if path.joinpath("sentinel.txt").exists() else b""
        status = subprocess.run(
            ("git", "-C", str(path), "status", "--porcelain"),
            check=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).stdout
        return file_value, status


if __name__ == "__main__":
    unittest.main()
