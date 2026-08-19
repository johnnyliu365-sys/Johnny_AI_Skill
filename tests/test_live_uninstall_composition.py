"""L6 closure tests: real receipt-owned uninstall over marker-proven state."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_root_layout import (
    FileUninstallLedgerStore,
    JohnnyRootLayout,
)
from library.local_orchestration.live_uninstall_composition import (
    run_live_uninstall,
)
from library.local_orchestration.plugin_uninstall_transaction import (
    OwnedStateKind,
    OwnedStateRecord,
    PluginUninstallLedger,
)

_RECEIPT = "receipt-live-20260819000000"

_KIND_RECEIPTS: tuple[tuple[OwnedStateKind, str], ...] = (
    (OwnedStateKind.PLUGIN_PAYLOAD, "plugin"),
    (OwnedStateKind.VENV, "venv"),
    (OwnedStateKind.LAUNCHER, "launcher"),
    (OwnedStateKind.QUEUE, "queue"),
    (OwnedStateKind.TELEMETRY, "telemetry"),
)


def _install_shape(layout: JohnnyRootLayout) -> None:
    for _, receipt in _KIND_RECEIPTS:
        owned_root = layout.base / receipt
        owned_root.mkdir(parents=True)
        (owned_root / ".johnny-owned").write_text(_RECEIPT, encoding="utf-8")
        (owned_root / "content.bin").write_bytes(b"payload")
    runtime_root = layout.base / "runtime"
    runtime_root.mkdir()
    # The launcher receipt owns runtime too, so install marks it as well.
    (runtime_root / ".johnny-owned").write_text(_RECEIPT, encoding="utf-8")
    (runtime_root / "johnny_router_entry.py").write_text(
        "# entry\n", encoding="utf-8"
    )
    layout.journal_path.write_text("", encoding="utf-8")
    ledger = PluginUninstallLedger(
        receipt_id=_RECEIPT,
        records=tuple(
            OwnedStateRecord(kind=kind, receipt=receipt)
            for kind, receipt in _KIND_RECEIPTS
        ),
    )
    assert FileUninstallLedgerStore(layout.ledger_path).write(ledger)


def _run(root: Path) -> tuple[int, dict[str, object]]:
    captured = io.StringIO()
    with redirect_stdout(captured):
        code = run_live_uninstall(root)
    lines = [line for line in captured.getvalue().splitlines() if line.strip()]
    return code, json.loads(lines[-1])


class LiveUninstallCompositionTests(unittest.TestCase):
    def test_complete_removal_reaches_zero_residue(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "jr"
            _install_shape(JohnnyRootLayout(base=root))

            code, payload = _run(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "REMOVED")
            self.assertEqual(payload["remaining"], [])
            self.assertTrue(payload["root_deleted"])
            self.assertFalse(root.exists())

    def test_foreign_marker_halts_everything_with_ledger_retained(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "jr"
            layout = JohnnyRootLayout(base=root)
            _install_shape(layout)
            (layout.base / "venv" / ".johnny-owned").write_text(
                "receipt-foreign-owner", encoding="utf-8"
            )

            code, payload = _run(root)

            self.assertEqual(code, 2)
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertEqual(payload["failure"], "FOREIGN_STATE_PRESENT")
            self.assertTrue((layout.base / "plugin" / "content.bin").exists())
            self.assertTrue(layout.ledger_path.exists())

    def test_foreign_directory_survives_and_root_stays(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "jr"
            layout = JohnnyRootLayout(base=root)
            _install_shape(layout)
            foreign = root / "user-notes"
            foreign.mkdir()
            (foreign / "keep.txt").write_text("keep", encoding="utf-8")

            code, payload = _run(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "REMOVED")
            self.assertFalse(payload["root_deleted"])
            self.assertTrue((foreign / "keep.txt").exists())
            self.assertFalse((root / "plugin").exists())
            self.assertFalse(layout.ledger_path.exists())

    def test_repeat_uninstall_is_not_installed(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "jr"
            _install_shape(JohnnyRootLayout(base=root))
            first_code, _ = _run(root)
            self.assertEqual(first_code, 0)

            code, payload = _run(root)

            self.assertEqual(code, 0)
            self.assertEqual(payload["status"], "NOT_INSTALLED")


if __name__ == "__main__":
    unittest.main()
