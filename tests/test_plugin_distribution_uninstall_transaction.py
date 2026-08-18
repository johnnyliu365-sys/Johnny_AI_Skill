"""Receipt-owned uninstall transaction closure tests for CLOSURE-PD-12-R03-01."""

from __future__ import annotations

import unittest
from typing import cast

from library.local_orchestration.plugin_uninstall_transaction import (
    OwnedStateKind,
    OwnedStateRecord,
    PluginUninstallFailure,
    PluginUninstallLedger,
    PluginUninstallPorts,
    PluginUninstallRequest,
    PluginUninstallStatus,
    PluginUninstallTransaction,
    UninstallLedgerReadResult,
    UninstallLedgerReadStatus,
    UninstallOwnershipProbe,
)

_RECEIPT = "receipt-pd12-primary-01"
_FOREIGN_ENTRY = "foreign-user-state-untouchable"

_ALL_KINDS = (
    OwnedStateKind.PLUGIN_PAYLOAD,
    OwnedStateKind.VENV,
    OwnedStateKind.LAUNCHER,
    OwnedStateKind.QUEUE,
    OwnedStateKind.TELEMETRY,
)


def _ledger() -> PluginUninstallLedger:
    return PluginUninstallLedger(
        receipt_id=_RECEIPT,
        records=tuple(
            OwnedStateRecord(kind=kind, receipt=f"owned-{kind.value.lower()}-01")
            for kind in _ALL_KINDS
        ),
    )


class _FakeLedgerStore:
    def __init__(
        self,
        log: list[str],
        ledger: PluginUninstallLedger | None,
        remove_ok: bool = True,
    ) -> None:
        self._log = log
        self.ledger = ledger
        self._remove_ok = remove_ok

    def read(self) -> UninstallLedgerReadResult:
        self._log.append("ledger.read")
        if self.ledger is None:
            return UninstallLedgerReadResult(
                status=UninstallLedgerReadStatus.ABSENT, ledger=None
            )
        return UninstallLedgerReadResult(
            status=UninstallLedgerReadStatus.PRESENT, ledger=self.ledger
        )

    def remove(self, receipt_id: str) -> bool:
        self._log.append("ledger.remove")
        if not self._remove_ok:
            return False
        self.ledger = None
        return True


class _FakeWorkAdmission:
    def __init__(self, log: list[str], block_ok: bool = True) -> None:
        self._log = log
        self._block_ok = block_ok

    def block(self, receipt_id: str) -> bool:
        self._log.append("work.block")
        return self._block_ok


class _FakeSubscriptionShutdown:
    def __init__(self, log: list[str], cancel_ok: bool = True) -> None:
        self._log = log
        self._cancel_ok = cancel_ok

    def cancel_all(self, receipt_id: str) -> bool:
        self._log.append("subscriptions.cancel")
        return self._cancel_ok


class _FakeRunnerShutdown:
    def __init__(self, log: list[str], stop_ok: bool = True) -> None:
        self._log = log
        self._stop_ok = stop_ok

    def stop_all(self, receipt_id: str) -> bool:
        self._log.append("runners.stop")
        return self._stop_ok


class _FakeOwnedState:
    def __init__(
        self,
        log: list[str],
        foreign_kinds: frozenset[OwnedStateKind] = frozenset(),
        fail_remove_kinds: frozenset[OwnedStateKind] = frozenset(),
    ) -> None:
        self._log = log
        self._foreign_kinds = foreign_kinds
        self._fail_remove_kinds = fail_remove_kinds
        self.entries: dict[str, str] = {_FOREIGN_ENTRY: "foreign"}
        for kind in _ALL_KINDS:
            self.entries[f"owned-{kind.value.lower()}-01"] = "owned"

    def probe(self, record: OwnedStateRecord) -> UninstallOwnershipProbe:
        self._log.append(f"state.probe:{record.kind.value}")
        if record.kind in self._foreign_kinds:
            return UninstallOwnershipProbe.FOREIGN
        return UninstallOwnershipProbe.OWNED

    def remove(self, record: OwnedStateRecord) -> bool:
        self._log.append(f"state.remove:{record.kind.value}")
        if record.kind in self._fail_remove_kinds:
            return False
        self.entries.pop(record.receipt, None)
        return True

    def has_owned_state(self, receipt_id: str) -> bool:
        self._log.append("state.residue")
        return any(owner == "owned" for owner in self.entries.values())


class _FakeAbsence:
    def __init__(
        self,
        log: list[str],
        state: _FakeOwnedState,
        fail_kinds: frozenset[OwnedStateKind] = frozenset(),
    ) -> None:
        self._log = log
        self._state = state
        self._fail_kinds = fail_kinds

    def verify_absent(self, record: OwnedStateRecord) -> bool:
        self._log.append(f"absence.verify:{record.kind.value}")
        if record.kind in self._fail_kinds:
            return False
        return record.receipt not in self._state.entries


class _Fixture:
    def __init__(
        self,
        ledger: PluginUninstallLedger | None = None,
        ledger_present: bool = True,
        ledger_remove_ok: bool = True,
        block_ok: bool = True,
        cancel_ok: bool = True,
        stop_ok: bool = True,
        foreign_kinds: frozenset[OwnedStateKind] = frozenset(),
        fail_remove_kinds: frozenset[OwnedStateKind] = frozenset(),
        absence_fail_kinds: frozenset[OwnedStateKind] = frozenset(),
    ) -> None:
        self.log: list[str] = []
        resolved = ledger if ledger is not None else _ledger()
        self.ledger_store = _FakeLedgerStore(
            self.log,
            resolved if ledger_present else None,
            remove_ok=ledger_remove_ok,
        )
        self.state = _FakeOwnedState(
            self.log,
            foreign_kinds=foreign_kinds,
            fail_remove_kinds=fail_remove_kinds,
        )
        self.absence = _FakeAbsence(
            self.log, self.state, fail_kinds=absence_fail_kinds
        )
        self.transaction = PluginUninstallTransaction(
            PluginUninstallPorts(
                ledger=self.ledger_store,
                work_admission=_FakeWorkAdmission(self.log, block_ok=block_ok),
                subscriptions=_FakeSubscriptionShutdown(self.log, cancel_ok=cancel_ok),
                runners=_FakeRunnerShutdown(self.log, stop_ok=stop_ok),
                owned_state=self.state,
                absence=self.absence,
            )
        )

    def remove_calls(self) -> list[str]:
        return [entry for entry in self.log if entry.startswith("state.remove")]

    def owned_entries(self) -> list[str]:
        return [
            receipt
            for receipt, owner in self.state.entries.items()
            if owner == "owned"
        ]


def _request() -> PluginUninstallRequest:
    return PluginUninstallRequest(receipt_id=_RECEIPT)


class PluginUninstallTransactionTests(unittest.TestCase):
    """U1-U5 closure cells for the receipt-owned uninstall transaction."""

    def test_ordered_owned_removal_and_ledger_close(self) -> None:
        """U1+U4: owned state removes in exact order, absence proves, ledger last."""

        fixture = _Fixture()
        result = fixture.transaction.run(_request())

        self.assertIs(result.status, PluginUninstallStatus.REMOVED)
        self.assertIsNone(result.failure)
        self.assertEqual(result.removed, _ALL_KINDS)
        self.assertEqual(result.remaining, ())
        self.assertFalse(result.ledger_retained)
        expected_order = (
            ["ledger.read", "work.block", "subscriptions.cancel", "runners.stop"]
            + [f"state.probe:{kind.value}" for kind in _ALL_KINDS]
            + [f"state.remove:{kind.value}" for kind in _ALL_KINDS]
            + [f"absence.verify:{kind.value}" for kind in _ALL_KINDS]
            + ["ledger.remove"]
        )
        self.assertEqual(fixture.log, expected_order)
        self.assertEqual(fixture.owned_entries(), [])
        self.assertIn(_FOREIGN_ENTRY, fixture.state.entries)
        self.assertIsNone(fixture.ledger_store.ledger)

    def test_foreign_path_halts_before_any_delete(self) -> None:
        """U2: one foreign-owned location halts the whole removal untouched."""

        fixture = _Fixture(
            foreign_kinds=frozenset({OwnedStateKind.VENV}),
        )
        result = fixture.transaction.run(_request())

        self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
        self.assertIs(result.failure, PluginUninstallFailure.FOREIGN_STATE_PRESENT)
        self.assertEqual(result.removed, ())
        self.assertEqual(result.remaining, _ALL_KINDS)
        self.assertTrue(result.ledger_retained)
        self.assertEqual(fixture.remove_calls(), [])
        self.assertEqual(len(fixture.owned_entries()), len(_ALL_KINDS))
        self.assertIn(_FOREIGN_ENTRY, fixture.state.entries)
        self.assertIsNotNone(fixture.ledger_store.ledger)
        self.assertNotIn("ledger.remove", fixture.log)

    def test_failed_shutdown_halts_with_ledger(self) -> None:
        """U3: block/cancel/stop failures halt before deletes with ledger intact."""

        cases: tuple[tuple[str, _Fixture, PluginUninstallFailure], ...] = (
            (
                "work_block_failed",
                _Fixture(block_ok=False),
                PluginUninstallFailure.WORK_BLOCK_FAILED,
            ),
            (
                "subscription_close_failed",
                _Fixture(cancel_ok=False),
                PluginUninstallFailure.SUBSCRIPTION_CLOSE_FAILED,
            ),
            (
                "runner_stop_failed",
                _Fixture(stop_ok=False),
                PluginUninstallFailure.RUNNER_STOP_FAILED,
            ),
        )
        for label, fixture, failure in cases:
            with self.subTest(case=label):
                result = fixture.transaction.run(_request())
                self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
                self.assertIs(result.failure, failure)
                self.assertTrue(result.ledger_retained)
                self.assertEqual(fixture.remove_calls(), [])
                self.assertIsNotNone(fixture.ledger_store.ledger)
                self.assertEqual(len(fixture.owned_entries()), len(_ALL_KINDS))

    def test_removal_and_readback_failures_retain_ledger(self) -> None:
        """U3/U4: failed removal or absence readback halts and keeps the ledger."""

        with self.subTest(case="removal_failed_mid_sequence"):
            fixture = _Fixture(
                fail_remove_kinds=frozenset({OwnedStateKind.LAUNCHER}),
            )
            result = fixture.transaction.run(_request())
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginUninstallFailure.REMOVAL_FAILED)
            self.assertEqual(
                result.removed,
                (OwnedStateKind.PLUGIN_PAYLOAD, OwnedStateKind.VENV),
            )
            self.assertEqual(
                result.remaining,
                (
                    OwnedStateKind.LAUNCHER,
                    OwnedStateKind.QUEUE,
                    OwnedStateKind.TELEMETRY,
                ),
            )
            self.assertTrue(result.ledger_retained)
            self.assertIsNotNone(fixture.ledger_store.ledger)
            self.assertNotIn("ledger.remove", fixture.log)

        with self.subTest(case="absence_readback_failed"):
            fixture = _Fixture(
                absence_fail_kinds=frozenset({OwnedStateKind.QUEUE}),
            )
            result = fixture.transaction.run(_request())
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(
                result.failure, PluginUninstallFailure.ABSENCE_READBACK_FAILED
            )
            self.assertTrue(result.ledger_retained)
            self.assertIsNotNone(fixture.ledger_store.ledger)
            self.assertNotIn("ledger.remove", fixture.log)

        with self.subTest(case="ledger_remove_failed"):
            fixture = _Fixture(ledger_remove_ok=False)
            result = fixture.transaction.run(_request())
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginUninstallFailure.LEDGER_REMOVE_FAILED)
            self.assertTrue(result.ledger_retained)
            self.assertIsNotNone(fixture.ledger_store.ledger)

    def test_foreign_ledger_and_invalid_request_halt(self) -> None:
        """Foreign receipt identity and foreign request objects halt untouched."""

        with self.subTest(case="foreign_ledger_receipt"):
            fixture = _Fixture(
                ledger=PluginUninstallLedger(
                    receipt_id="receipt-pd12-other-99",
                    records=_ledger().records,
                )
            )
            result = fixture.transaction.run(_request())
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginUninstallFailure.LEDGER_FOREIGN)
            self.assertTrue(result.ledger_retained)
            self.assertEqual(fixture.remove_calls(), [])

        with self.subTest(case="foreign_request_object"):
            fixture = _Fixture()
            result = fixture.transaction.run(
                cast(PluginUninstallRequest, object())
            )
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(result.failure, PluginUninstallFailure.REQUEST_INVALID)
            self.assertEqual(fixture.remove_calls(), [])

    def test_repeat_uninstall_is_idempotent(self) -> None:
        """U5: after complete removal a repeat returns NOT_INSTALLED; residue blocks."""

        with self.subTest(case="second_run_after_success"):
            fixture = _Fixture()
            first = fixture.transaction.run(_request())
            self.assertIs(first.status, PluginUninstallStatus.REMOVED)
            second = fixture.transaction.run(_request())
            self.assertIs(second.status, PluginUninstallStatus.NOT_INSTALLED)
            self.assertIsNone(second.failure)
            self.assertFalse(second.ledger_retained)
            self.assertIn(_FOREIGN_ENTRY, fixture.state.entries)

        with self.subTest(case="ledger_absent_with_owned_residue"):
            fixture = _Fixture(ledger_present=False)
            result = fixture.transaction.run(_request())
            self.assertIs(result.status, PluginUninstallStatus.BLOCKED)
            self.assertIs(
                result.failure, PluginUninstallFailure.RESIDUAL_OWNED_STATE
            )
            self.assertEqual(fixture.remove_calls(), [])
            self.assertEqual(len(fixture.owned_entries()), len(_ALL_KINDS))


if __name__ == "__main__":
    unittest.main()
