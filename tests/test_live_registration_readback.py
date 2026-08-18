"""L4 closure tests: the readback proves the real entry chain, end to end."""

from __future__ import annotations

import shutil
import sys
import unittest
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_root_layout import JohnnyRootLayout
from library.local_orchestration.registration_readback_port import (
    RealRegistrationReadbackPort,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ENTRY_SOURCE = (
    _REPO_ROOT / "library" / "local_orchestration" / "johnny_router_entry.py"
)
_LIVE_CLI_RELATIVE = "library/local_orchestration/johnny_live_cli.py"


def _assemble_runtime(layout: JohnnyRootLayout) -> None:
    """Assemble a minimal but real installed shape from the shipped sources."""

    layout.runtime_root.mkdir(parents=True)
    shutil.copyfile(_ENTRY_SOURCE, layout.runtime_entry)
    layout.launcher_root.mkdir(parents=True)
    (layout.launcher_root / "johnny-router.ps1").write_text(
        "# launcher\n", encoding="utf-8"
    )
    cli_target = layout.plugin_root.joinpath(*_LIVE_CLI_RELATIVE.split("/"))
    cli_target.parent.mkdir(parents=True)
    shutil.copyfile(_REPO_ROOT / _LIVE_CLI_RELATIVE, cli_target)
    (layout.plugin_root / "library" / "__init__.py").write_text(
        "", encoding="utf-8"
    )
    (
        layout.plugin_root / "library" / "local_orchestration" / "__init__.py"
    ).write_text("", encoding="utf-8")
    (layout.plugin_root / "payload-manifest.json").write_text(
        '{"plugin_version": "0.4.0"}', encoding="utf-8"
    )
    layout.venv_python.parent.mkdir(parents=True)
    layout.venv_python.write_bytes(b"stub")


class RealRegistrationReadbackPortTests(unittest.TestCase):
    def test_assembled_runtime_reads_back_true_through_the_real_chain(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            _assemble_runtime(layout)
            port = RealRegistrationReadbackPort(
                layout, python_executable=Path(sys.executable)
            )
            self.assertTrue(port.readback("attempt-l4-01"))

    def test_each_missing_piece_fails_the_readback(self) -> None:
        cases: tuple[tuple[str, Callable[[JohnnyRootLayout], None]], ...] = (
            ("runtime_entry", lambda layout: layout.runtime_entry.unlink()),
            (
                "launcher",
                lambda layout: (
                    layout.launcher_root / "johnny-router.ps1"
                ).unlink(),
            ),
            (
                "payload_manifest",
                lambda layout: (
                    layout.plugin_root / "payload-manifest.json"
                ).unlink(),
            ),
            (
                "live_cli",
                lambda layout: layout.plugin_root.joinpath(
                    *_LIVE_CLI_RELATIVE.split("/")
                ).unlink(),
            ),
            ("venv_python", lambda layout: layout.venv_python.unlink()),
        )
        for label, breaker in cases:
            with self.subTest(missing=label):
                with TemporaryDirectory() as temporary:
                    layout = JohnnyRootLayout(base=Path(temporary).resolve())
                    _assemble_runtime(layout)
                    breaker(layout)
                    port = RealRegistrationReadbackPort(
                        layout, python_executable=Path(sys.executable)
                    )
                    self.assertFalse(port.readback("attempt-l4-02"))

    def test_missing_interpreter_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            layout = JohnnyRootLayout(base=Path(temporary).resolve())
            _assemble_runtime(layout)
            port = RealRegistrationReadbackPort(
                layout,
                python_executable=Path(temporary) / "absent-python.exe",
            )
            self.assertFalse(port.readback("attempt-l4-03"))


if __name__ == "__main__":
    unittest.main()
