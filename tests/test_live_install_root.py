"""L1 closure tests: Johnny root layout and durable bookkeeping stores."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from library.local_orchestration.johnny_root_layout import (
    FileInstallAttemptJournal,
    FileUninstallLedgerStore,
    JohnnyRootLayout,
)
from library.local_orchestration.plugin_install_transaction import (
    InstallEffectKind,
    InstallEffectRecord,
    InstallJournalOpenStatus,
)
from library.local_orchestration.plugin_uninstall_transaction import (
    OwnedStateKind,
    OwnedStateRecord,
    PluginUninstallLedger,
    UninstallLedgerReadStatus,
)

_ATTEMPT = "attempt-live-install-01"


def _ledger(receipt_id: str = "receipt-live-install-01") -> PluginUninstallLedger:
    return PluginUninstallLedger(
        receipt_id=receipt_id,
        records=tuple(
            OwnedStateRecord(kind=kind, receipt=kind.value.lower().replace("_payload", ""))
            for kind in OwnedStateKind
        ),
    )


class JohnnyRootLayoutTests(unittest.TestCase):
    def test_override_and_default_resolution(self) -> None:
        with self.subTest(source="override"):
            layout = JohnnyRootLayout.resolve(
                {"JOHNNY_ROOT": "C:\\disposable\\jr", "LOCALAPPDATA": "C:\\x"}
            )
            self.assertEqual(layout.base, Path("C:/disposable/jr"))
        with self.subTest(source="default"):
            layout = JohnnyRootLayout.resolve({"LOCALAPPDATA": "C:\\Users\\u\\AppData\\Local"})
            self.assertEqual(
                layout.base, Path("C:/Users/u/AppData/Local/JohnnyRouter")
            )
        with self.subTest(source="missing_localappdata"):
            with self.assertRaises(ValueError):
                JohnnyRootLayout.resolve({})

    def test_every_owned_path_derives_from_base(self) -> None:
        layout = JohnnyRootLayout(base=Path("C:/disposable/jr"))
        derived = (
            layout.plugin_root,
            layout.venv_root,
            layout.launcher_root,
            layout.queue_root,
            layout.telemetry_root,
            layout.runtime_root,
            layout.venv_python,
            layout.runtime_entry,
            layout.journal_path,
            layout.ledger_path,
        )
        for path in derived:
            with self.subTest(path=str(path)):
                self.assertTrue(str(path).startswith(str(layout.base)))
        self.assertEqual(layout.owned_receipt_path("plugin"), layout.plugin_root)
        with self.assertRaises(ValueError):
            layout.owned_receipt_path("..\\escape")

    def test_relative_base_is_untypable(self) -> None:
        with self.assertRaises(ValidationError):
            JohnnyRootLayout(base=Path("relative/root"))


class FileInstallAttemptJournalTests(unittest.TestCase):
    def test_open_record_seal_lifecycle(self) -> None:
        with TemporaryDirectory() as temporary:
            journal = FileInstallAttemptJournal(Path(temporary) / "journal.jsonl")
            self.assertIs(
                journal.open(_ATTEMPT).status, InstallJournalOpenStatus.OPENED
            )
            record = InstallEffectRecord(kind=InstallEffectKind.VENV, receipt="venv")
            self.assertTrue(journal.record(_ATTEMPT, record))
            self.assertTrue(journal.seal(_ATTEMPT))
            self.assertIs(
                journal.open(_ATTEMPT).status, InstallJournalOpenStatus.CONFLICT
            )
            self.assertIs(
                journal.open("attempt-live-install-02").status,
                InstallJournalOpenStatus.OPENED,
            )

    def test_unsealed_attempt_blocks_every_new_open(self) -> None:
        with TemporaryDirectory() as temporary:
            journal = FileInstallAttemptJournal(Path(temporary) / "journal.jsonl")
            self.assertIs(
                journal.open(_ATTEMPT).status, InstallJournalOpenStatus.OPENED
            )
            self.assertIs(
                journal.open("attempt-live-install-02").status,
                InstallJournalOpenStatus.CONFLICT,
            )

    def test_record_and_seal_require_an_open_attempt(self) -> None:
        with TemporaryDirectory() as temporary:
            journal = FileInstallAttemptJournal(Path(temporary) / "journal.jsonl")
            record = InstallEffectRecord(kind=InstallEffectKind.VENV, receipt="venv")
            self.assertFalse(journal.record(_ATTEMPT, record))
            self.assertFalse(journal.seal(_ATTEMPT))

    def test_corrupt_journal_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "journal.jsonl"
            path.write_text("not json\n", encoding="utf-8")
            journal = FileInstallAttemptJournal(path)
            self.assertIs(
                journal.open(_ATTEMPT).status, InstallJournalOpenStatus.UNAVAILABLE
            )
            record = InstallEffectRecord(kind=InstallEffectKind.VENV, receipt="venv")
            self.assertFalse(journal.record(_ATTEMPT, record))
            self.assertFalse(journal.seal(_ATTEMPT))


class FileUninstallLedgerStoreTests(unittest.TestCase):
    def test_roundtrip_and_removal(self) -> None:
        with TemporaryDirectory() as temporary:
            store = FileUninstallLedgerStore(Path(temporary) / "ledger.json")
            self.assertIs(store.read().status, UninstallLedgerReadStatus.ABSENT)
            ledger = _ledger()
            self.assertTrue(store.write(ledger))
            read_back = store.read()
            self.assertIs(read_back.status, UninstallLedgerReadStatus.PRESENT)
            self.assertEqual(read_back.ledger, ledger)
            with self.subTest(case="foreign_receipt_refused"):
                self.assertFalse(store.remove("receipt-live-install-99"))
                self.assertIs(
                    store.read().status, UninstallLedgerReadStatus.PRESENT
                )
            with self.subTest(case="owning_receipt_removes"):
                self.assertTrue(store.remove("receipt-live-install-01"))
                self.assertIs(store.read().status, UninstallLedgerReadStatus.ABSENT)
            with self.subTest(case="repeat_removal_is_idempotent"):
                self.assertTrue(store.remove("receipt-live-install-01"))

    def test_corrupt_ledger_raises_for_the_transaction_guard(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.json"
            path.write_text("{broken", encoding="utf-8")
            store = FileUninstallLedgerStore(path)
            with self.assertRaises(Exception):
                store.read()
            self.assertFalse(store.remove("receipt-live-install-01"))


if __name__ == "__main__":
    unittest.main()
