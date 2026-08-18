"""Attempt-owned install transaction closure tests for CLOSURE-PD-11-R03-01."""

from __future__ import annotations

import unittest
from typing import cast

from library.local_orchestration.johnny_router_contracts import PreflightProbe
from library.local_orchestration.plugin_install_transaction import (
    InstallDependencyPlan,
    InstallDependencyPlanEntry,
    InstallEffectKind,
    InstallEffectOutcome,
    InstallEffectOutcomeStatus,
    InstallEffectRecord,
    InstallJournalOpenResult,
    InstallJournalOpenStatus,
    PluginInstallFailure,
    PluginInstallPorts,
    PluginInstallRequest,
    PluginInstallResult,
    PluginInstallStatus,
    PluginInstallTransaction,
    ApprovedBundleReference,
)
from library.local_orchestration.runtime_dependency_lock import (
    RuntimeDependencyLock,
    build_approved_runtime_lock,
)
from library.local_orchestration.windows_package_manifest import (
    PayloadManifest,
    PayloadManifestEntry,
)

_ATTEMPT = "attempt-pd11-primary-01"
_FOREIGN_RECEIPT = "foreign-effect-untouchable-01"
_ARCHIVE_SHA256 = "1" * 64


def _approved_manifest() -> PayloadManifest:
    lock = build_approved_runtime_lock()
    return PayloadManifest(
        plugin_id="johnny-ai-skill",
        plugin_version="0.4.0",
        source_commit="a" * 40,
        dependency_lock_digest=lock.lock_digest,
        entries=(
            PayloadManifestEntry(
                archive_relative_path="AGENTS.md",
                sha256="2" * 64,
                byte_length=10,
            ),
        ),
    )


def _approved_request() -> PluginInstallRequest:
    manifest = _approved_manifest()
    return PluginInstallRequest(
        attempt_id=_ATTEMPT,
        bundle=ApprovedBundleReference(
            archive_sha256=_ARCHIVE_SHA256,
            manifest_digest=manifest.canonical_digest(),
        ),
        manifest=manifest,
        runtime_lock=build_approved_runtime_lock(),
    )


class _FakeHostProbe:
    def __init__(self, log: list[str], probe: PreflightProbe) -> None:
        self._log = log
        self._probe = probe

    def probe(self) -> PreflightProbe:
        self._log.append("host.probe")
        return self._probe


class _FakeArchive:
    def __init__(self, log: list[str], digest: str) -> None:
        self._log = log
        self._digest = digest

    def read_archive_sha256(self) -> str:
        self._log.append("archive.read")
        return self._digest


class _FakeJournal:
    def __init__(
        self,
        log: list[str],
        open_status: InstallJournalOpenStatus = InstallJournalOpenStatus.OPENED,
        record_ok: bool = True,
        seal_ok: bool = True,
    ) -> None:
        self._log = log
        self._open_status = open_status
        self._record_ok = record_ok
        self._seal_ok = seal_ok
        self.records: list[InstallEffectRecord] = []

    def open(self, attempt_id: str) -> InstallJournalOpenResult:
        self._log.append("journal.open")
        return InstallJournalOpenResult(status=self._open_status)

    def record(self, attempt_id: str, record: InstallEffectRecord) -> bool:
        self._log.append(f"journal.record:{record.kind.value}")
        if self._record_ok:
            self.records.append(record)
        return self._record_ok

    def seal(self, attempt_id: str) -> bool:
        self._log.append("journal.seal")
        return self._seal_ok


class _FakeEffectStore:
    """One owned/foreign effect surface shared by an effect port fake."""

    def __init__(self) -> None:
        self.entries: dict[str, str] = {_FOREIGN_RECEIPT: "foreign"}


class _FakeVenv:
    def __init__(
        self,
        log: list[str],
        store: _FakeEffectStore,
        outcome_status: InstallEffectOutcomeStatus = (
            InstallEffectOutcomeStatus.COMPLETED
        ),
        raise_on_create: bool = False,
        remove_ok: bool = True,
    ) -> None:
        self._log = log
        self.store = store
        self._outcome_status = outcome_status
        self._raise_on_create = raise_on_create
        self._remove_ok = remove_ok

    def create(
        self, attempt_id: str, plan: InstallDependencyPlan
    ) -> InstallEffectOutcome:
        self._log.append("venv.create")
        if self._raise_on_create:
            raise OSError("interrupted while creating the environment")
        if self._outcome_status is not InstallEffectOutcomeStatus.COMPLETED:
            return InstallEffectOutcome(status=self._outcome_status, receipt=None)
        receipt = f"venv-owned-{attempt_id}"
        self.store.entries[receipt] = "owned"
        return InstallEffectOutcome(
            status=InstallEffectOutcomeStatus.COMPLETED, receipt=receipt
        )

    def remove(self, receipt: str) -> bool:
        self._log.append("venv.remove")
        if not self._remove_ok:
            return False
        self.store.entries.pop(receipt, None)
        return True


class _FakePluginPayload:
    def __init__(
        self,
        log: list[str],
        store: _FakeEffectStore,
        outcome_status: InstallEffectOutcomeStatus = (
            InstallEffectOutcomeStatus.COMPLETED
        ),
        raise_on_install: bool = False,
    ) -> None:
        self._log = log
        self.store = store
        self._outcome_status = outcome_status
        self._raise_on_install = raise_on_install

    def install(
        self, attempt_id: str, manifest: PayloadManifest
    ) -> InstallEffectOutcome:
        self._log.append("plugin.install")
        if self._raise_on_install:
            raise OSError("interrupted while writing payload")
        if self._outcome_status is not InstallEffectOutcomeStatus.COMPLETED:
            return InstallEffectOutcome(status=self._outcome_status, receipt=None)
        receipt = f"plugin-owned-{attempt_id}"
        self.store.entries[receipt] = "owned"
        return InstallEffectOutcome(
            status=InstallEffectOutcomeStatus.COMPLETED, receipt=receipt
        )

    def remove(self, receipt: str) -> bool:
        self._log.append("plugin.remove")
        self.store.entries.pop(receipt, None)
        return True


class _FakeLauncher:
    def __init__(
        self,
        log: list[str],
        store: _FakeEffectStore,
        raise_on_create: bool = False,
    ) -> None:
        self._log = log
        self.store = store
        self._raise_on_create = raise_on_create

    def create(self, attempt_id: str) -> InstallEffectOutcome:
        self._log.append("launcher.create")
        if self._raise_on_create:
            raise OSError("interrupted while creating launcher")
        receipt = f"launcher-owned-{attempt_id}"
        self.store.entries[receipt] = "owned"
        return InstallEffectOutcome(
            status=InstallEffectOutcomeStatus.COMPLETED, receipt=receipt
        )

    def remove(self, receipt: str) -> bool:
        self._log.append("launcher.remove")
        self.store.entries.pop(receipt, None)
        return True


class _FakeRegistration:
    def __init__(self, log: list[str], readback_ok: bool = True) -> None:
        self._log = log
        self._readback_ok = readback_ok

    def readback(self, attempt_id: str) -> bool:
        self._log.append("registration.readback")
        return self._readback_ok


class _Fixture:
    def __init__(
        self,
        probe: PreflightProbe | None = None,
        archive_digest: str = _ARCHIVE_SHA256,
        journal: _FakeJournal | None = None,
        venv: _FakeVenv | None = None,
        plugin_payload: _FakePluginPayload | None = None,
        launcher: _FakeLauncher | None = None,
        registration: _FakeRegistration | None = None,
    ) -> None:
        self.log: list[str] = []
        self.store = _FakeEffectStore()
        self.journal = journal if journal is not None else _FakeJournal(self.log)
        self.venv = venv if venv is not None else _FakeVenv(self.log, self.store)
        self.plugin_payload = (
            plugin_payload
            if plugin_payload is not None
            else _FakePluginPayload(self.log, self.store)
        )
        self.launcher = (
            launcher if launcher is not None else _FakeLauncher(self.log, self.store)
        )
        self.registration = (
            registration if registration is not None else _FakeRegistration(self.log)
        )
        self.transaction = PluginInstallTransaction(
            PluginInstallPorts(
                host_probe=_FakeHostProbe(
                    self.log,
                    probe
                    if probe is not None
                    else PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                ),
                archive=_FakeArchive(self.log, archive_digest),
                journal=self.journal,
                venv=self.venv,
                plugin_payload=self.plugin_payload,
                launcher=self.launcher,
                registration=self.registration,
            )
        )

    def effect_calls(self) -> list[str]:
        return [
            entry
            for entry in self.log
            if entry.startswith(("venv.", "plugin.", "launcher."))
        ]


class PluginInstallTransactionTests(unittest.TestCase):
    """I1-I5 closure cells for the attempt-owned install transaction."""

    def test_verified_plan_presents_exact_dependency_plan(self) -> None:
        """I1: approved inputs install and present the lock-derived plan."""

        fixture = _Fixture()
        result = fixture.transaction.run(_approved_request())

        self.assertIs(result.status, PluginInstallStatus.INSTALLED)
        self.assertIsNone(result.failure)
        lock = build_approved_runtime_lock()
        expected_plan = InstallDependencyPlan(
            python_constraint=lock.python_constraint,
            entries=tuple(
                InstallDependencyPlanEntry(
                    name=dependency.normalized_name,
                    version=dependency.exact_version,
                    artifact_sha256s=tuple(
                        artifact.sha256 for artifact in dependency.artifacts
                    ),
                )
                for dependency in lock.dependencies
            ),
        )
        self.assertEqual(result.plan, expected_plan)
        self.assertEqual(
            tuple(record.kind for record in result.effects),
            (
                InstallEffectKind.VENV,
                InstallEffectKind.PLUGIN_PAYLOAD,
                InstallEffectKind.LAUNCHER,
            ),
        )
        self.assertEqual(result.compensated, ())
        self.assertEqual(result.uncompensated, ())

    def test_effect_order_and_registration_readback(self) -> None:
        """I2: effects run in exact order, each recorded, then readback and seal."""

        fixture = _Fixture()
        result = fixture.transaction.run(_approved_request())

        self.assertIs(result.status, PluginInstallStatus.INSTALLED)
        self.assertEqual(
            fixture.log,
            [
                "archive.read",
                "host.probe",
                "journal.open",
                "venv.create",
                "journal.record:VENV",
                "plugin.install",
                "journal.record:PLUGIN_PAYLOAD",
                "launcher.create",
                "journal.record:LAUNCHER",
                "registration.readback",
                "journal.seal",
            ],
        )

    def test_hash_mismatch_compensates_only_attempt_owned_effects(self) -> None:
        """I3: a dependency hash failure removes only this attempt's effects."""

        fixture = _Fixture()
        fixture.plugin_payload = _FakePluginPayload(
            fixture.log,
            fixture.store,
            outcome_status=InstallEffectOutcomeStatus.HASH_MISMATCH,
        )
        fixture.transaction = PluginInstallTransaction(
            PluginInstallPorts(
                host_probe=_FakeHostProbe(
                    fixture.log,
                    PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                ),
                archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                journal=fixture.journal,
                venv=fixture.venv,
                plugin_payload=fixture.plugin_payload,
                launcher=fixture.launcher,
                registration=fixture.registration,
            )
        )

        result = fixture.transaction.run(_approved_request())

        self.assertIs(result.status, PluginInstallStatus.COMPENSATED)
        self.assertIs(result.failure, PluginInstallFailure.DEPENDENCY_HASH_MISMATCH)
        self.assertEqual(result.compensated, (InstallEffectKind.VENV,))
        self.assertEqual(result.uncompensated, ())
        self.assertNotIn("launcher.create", fixture.log)
        self.assertNotIn("registration.readback", fixture.log)
        self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)
        owned_left = [
            receipt
            for receipt, owner in fixture.store.entries.items()
            if owner == "owned"
        ]
        self.assertEqual(owned_left, [])

    def test_finite_failures_block_before_any_effect(self) -> None:
        """AC-05: pre-effect failures return finite results with zero effects."""

        request = _approved_request()
        cases: tuple[tuple[str, _Fixture, PluginInstallRequest, PluginInstallFailure], ...] = (
            (
                "missing_git",
                _Fixture(
                    probe=PreflightProbe(
                        git_available=False, python_version=(3, 11, 9)
                    )
                ),
                request,
                PluginInstallFailure.GIT_UNAVAILABLE,
            ),
            (
                "missing_python",
                _Fixture(
                    probe=PreflightProbe(git_available=True, python_version=None)
                ),
                request,
                PluginInstallFailure.PYTHON_UNAVAILABLE,
            ),
            (
                "incompatible_python",
                _Fixture(
                    probe=PreflightProbe(
                        git_available=True, python_version=(3, 10, 11)
                    )
                ),
                request,
                PluginInstallFailure.PYTHON_INCOMPATIBLE,
            ),
            (
                "newer_incompatible_python",
                _Fixture(
                    probe=PreflightProbe(
                        git_available=True, python_version=(3, 14, 0)
                    )
                ),
                request,
                PluginInstallFailure.PYTHON_INCOMPATIBLE,
            ),
            (
                "archive_hash_mismatch",
                _Fixture(archive_digest="f" * 64),
                request,
                PluginInstallFailure.ARCHIVE_HASH_MISMATCH,
            ),
            (
                "foreign_request",
                _Fixture(),
                cast(PluginInstallRequest, object()),
                PluginInstallFailure.REQUEST_INVALID,
            ),
        )
        for label, fixture, case_request, failure in cases:
            with self.subTest(case=label):
                result = fixture.transaction.run(case_request)
                self.assertIs(result.status, PluginInstallStatus.BLOCKED)
                self.assertIs(result.failure, failure)
                self.assertEqual(result.effects, ())
                self.assertEqual(result.compensated, ())
                self.assertEqual(fixture.effect_calls(), [])
                self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)

        with self.subTest(case="forged_lock_rejected_as_invalid_request"):
            fixture = _Fixture()
            lock = build_approved_runtime_lock()
            forged_lock = RuntimeDependencyLock.model_construct(
                schema_version=1,
                python_constraint=lock.python_constraint,
                dependencies=lock.dependencies,
                lock_digest="3" * 64,
            )
            manifest = _approved_manifest()
            forged_request = PluginInstallRequest.model_construct(
                attempt_id=_ATTEMPT,
                bundle=ApprovedBundleReference(
                    archive_sha256=_ARCHIVE_SHA256,
                    manifest_digest=manifest.canonical_digest(),
                ),
                manifest=manifest,
                runtime_lock=forged_lock,
            )
            result = fixture.transaction.run(forged_request)
            self.assertIs(result.status, PluginInstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginInstallFailure.REQUEST_INVALID)
            self.assertEqual(fixture.effect_calls(), [])

        with self.subTest(case="lock_digest_mismatch"):
            fixture = _Fixture()
            lock = build_approved_runtime_lock()
            manifest = _approved_manifest().model_copy(
                update={"dependency_lock_digest": "3" * 64}
            )
            mismatched_request = PluginInstallRequest(
                attempt_id=_ATTEMPT,
                bundle=ApprovedBundleReference(
                    archive_sha256=_ARCHIVE_SHA256,
                    manifest_digest=manifest.canonical_digest(),
                ),
                manifest=manifest,
                runtime_lock=lock,
            )
            result = fixture.transaction.run(mismatched_request)
            self.assertIs(result.status, PluginInstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginInstallFailure.LOCK_DIGEST_MISMATCH)
            self.assertEqual(fixture.effect_calls(), [])

        with self.subTest(case="manifest_digest_mismatch"):
            fixture = _Fixture()
            manifest = _approved_manifest()
            mismatched = PluginInstallRequest(
                attempt_id=_ATTEMPT,
                bundle=ApprovedBundleReference(
                    archive_sha256=_ARCHIVE_SHA256,
                    manifest_digest="4" * 64,
                ),
                manifest=manifest,
                runtime_lock=build_approved_runtime_lock(),
            )
            result = fixture.transaction.run(mismatched)
            self.assertIs(result.status, PluginInstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginInstallFailure.MANIFEST_DIGEST_MISMATCH)
            self.assertEqual(fixture.effect_calls(), [])

    def test_interruption_and_readback_failures_compensate_in_reverse(self) -> None:
        """I3: interruption and readback failure compensate recorded effects."""

        with self.subTest(case="first_effect_interrupted"):
            fixture = _Fixture()
            fixture.venv = _FakeVenv(fixture.log, fixture.store, raise_on_create=True)
            fixture.transaction = PluginInstallTransaction(
                PluginInstallPorts(
                    host_probe=_FakeHostProbe(
                        fixture.log,
                        PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                    ),
                    archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                    journal=fixture.journal,
                    venv=fixture.venv,
                    plugin_payload=fixture.plugin_payload,
                    launcher=fixture.launcher,
                    registration=fixture.registration,
                )
            )
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginInstallFailure.EFFECT_INTERRUPTED)
            self.assertEqual(result.effects, ())
            self.assertEqual(result.compensated, ())

        with self.subTest(case="launcher_interrupted_after_two_effects"):
            fixture = _Fixture()
            fixture.launcher = _FakeLauncher(
                fixture.log, fixture.store, raise_on_create=True
            )
            fixture.transaction = PluginInstallTransaction(
                PluginInstallPorts(
                    host_probe=_FakeHostProbe(
                        fixture.log,
                        PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                    ),
                    archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                    journal=fixture.journal,
                    venv=fixture.venv,
                    plugin_payload=fixture.plugin_payload,
                    launcher=fixture.launcher,
                    registration=fixture.registration,
                )
            )
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.COMPENSATED)
            self.assertIs(result.failure, PluginInstallFailure.EFFECT_INTERRUPTED)
            self.assertEqual(
                result.compensated,
                (InstallEffectKind.PLUGIN_PAYLOAD, InstallEffectKind.VENV),
            )
            self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)

        with self.subTest(case="registration_readback_failed"):
            fixture = _Fixture(registration=None)
            fixture.registration = _FakeRegistration(fixture.log, readback_ok=False)
            fixture.transaction = PluginInstallTransaction(
                PluginInstallPorts(
                    host_probe=_FakeHostProbe(
                        fixture.log,
                        PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                    ),
                    archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                    journal=fixture.journal,
                    venv=fixture.venv,
                    plugin_payload=fixture.plugin_payload,
                    launcher=fixture.launcher,
                    registration=fixture.registration,
                )
            )
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.COMPENSATED)
            self.assertIs(
                result.failure, PluginInstallFailure.REGISTRATION_READBACK_FAILED
            )
            self.assertEqual(
                result.compensated,
                (
                    InstallEffectKind.LAUNCHER,
                    InstallEffectKind.PLUGIN_PAYLOAD,
                    InstallEffectKind.VENV,
                ),
            )

        with self.subTest(case="compensation_incomplete_records_remainder"):
            fixture = _Fixture()
            fixture.venv = _FakeVenv(fixture.log, fixture.store, remove_ok=False)
            fixture.registration = _FakeRegistration(fixture.log, readback_ok=False)
            fixture.transaction = PluginInstallTransaction(
                PluginInstallPorts(
                    host_probe=_FakeHostProbe(
                        fixture.log,
                        PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                    ),
                    archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                    journal=fixture.journal,
                    venv=fixture.venv,
                    plugin_payload=fixture.plugin_payload,
                    launcher=fixture.launcher,
                    registration=fixture.registration,
                )
            )
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.COMPENSATION_INCOMPLETE)
            self.assertIs(
                result.failure, PluginInstallFailure.REGISTRATION_READBACK_FAILED
            )
            self.assertEqual(
                result.compensated,
                (InstallEffectKind.LAUNCHER, InstallEffectKind.PLUGIN_PAYLOAD),
            )
            self.assertEqual(result.uncompensated, (InstallEffectKind.VENV,))

    def test_foreign_and_orphan_effects_preserved(self) -> None:
        """I4: foreign and orphan effects survive success and compensation."""

        with self.subTest(path="success"):
            fixture = _Fixture()
            orphan = "venv-owned-orphan-from-lost-attempt"
            fixture.store.entries[orphan] = "orphan"
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.INSTALLED)
            self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)
            self.assertIn(orphan, fixture.store.entries)

        with self.subTest(path="compensation"):
            fixture = _Fixture()
            orphan = "plugin-owned-orphan-from-lost-attempt"
            fixture.store.entries[orphan] = "orphan"
            fixture.registration = _FakeRegistration(fixture.log, readback_ok=False)
            fixture.transaction = PluginInstallTransaction(
                PluginInstallPorts(
                    host_probe=_FakeHostProbe(
                        fixture.log,
                        PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                    ),
                    archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                    journal=fixture.journal,
                    venv=fixture.venv,
                    plugin_payload=fixture.plugin_payload,
                    launcher=fixture.launcher,
                    registration=fixture.registration,
                )
            )
            result = fixture.transaction.run(_approved_request())
            self.assertIs(result.status, PluginInstallStatus.COMPENSATED)
            self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)
            self.assertIn(orphan, fixture.store.entries)

    def test_repeated_attempt_conflicts_before_any_effect(self) -> None:
        """I5: a repeated or still-open attempt conflicts with zero effects."""

        fixture = _Fixture(
            journal=None,
        )
        fixture.journal = _FakeJournal(
            fixture.log, open_status=InstallJournalOpenStatus.CONFLICT
        )
        fixture.transaction = PluginInstallTransaction(
            PluginInstallPorts(
                host_probe=_FakeHostProbe(
                    fixture.log,
                    PreflightProbe(git_available=True, python_version=(3, 11, 9)),
                ),
                archive=_FakeArchive(fixture.log, _ARCHIVE_SHA256),
                journal=fixture.journal,
                venv=fixture.venv,
                plugin_payload=fixture.plugin_payload,
                launcher=fixture.launcher,
                registration=fixture.registration,
            )
        )

        result = fixture.transaction.run(_approved_request())

        self.assertIs(result.status, PluginInstallStatus.BLOCKED)
        self.assertIs(result.failure, PluginInstallFailure.ATTEMPT_CONFLICT)
        self.assertEqual(result.effects, ())
        self.assertEqual(fixture.effect_calls(), [])
        self.assertIn(_FOREIGN_RECEIPT, fixture.store.entries)


def _unused_result_reference() -> type[PluginInstallResult]:
    return PluginInstallResult


if __name__ == "__main__":
    unittest.main()
