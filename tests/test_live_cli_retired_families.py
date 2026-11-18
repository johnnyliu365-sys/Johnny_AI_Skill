"""The live CLI keeps `status` and `uninstall`; the retired bridge families are unknown (ticket 66)."""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from library.local_orchestration.johnny_live_cli import run_live_cli

_RETIRED_FAMILIES: tuple[str, ...] = (
    "dispatch",
    "review",
    "runner",
    "wake-inbox",
    "wake-capability",
)

_UNKNOWN_LINE = '{"status":"CAPABILITY_UNAVAILABLE","code":"UNKNOWN_COMMAND"}\n'


def _run(argv: tuple[str, ...], root: Path) -> tuple[int, str]:
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        code = run_live_cli(argv, johnny_root=root)
    return code, captured.getvalue()


def _variants(family: str) -> tuple[str, ...]:
    return (
        family,
        family.upper(),
        family.title(),
        family.swapcase(),
        family[:-1],
        family[:3],
        family + "x",
        family + " ",
        " " + family,
        family.replace("-", "_"),
    )


class RetiredFamiliesAreUnknownTests(unittest.TestCase):
    def test_each_retired_family_answers_unknown_command_exit_three(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for family in _RETIRED_FAMILIES:
                with self.subTest(family=family):
                    self.assertEqual(_run((family,), root), (3, _UNKNOWN_LINE))
                    self.assertEqual(
                        _run((family, "--anything", "x"), root), (3, _UNKNOWN_LINE)
                    )

    def test_no_case_variant_or_prefix_reaches_a_family(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for family in _RETIRED_FAMILIES:
                for spelling in _variants(family):
                    with self.subTest(family=family, spelling=spelling):
                        self.assertEqual(_run((spelling,), root), (3, _UNKNOWN_LINE))

    def test_the_unknown_line_is_one_json_object(self) -> None:
        with TemporaryDirectory() as temporary:
            code, out = _run(("runner",), Path(temporary).resolve())
        self.assertEqual(code, 3)
        self.assertEqual(len(out.splitlines()), 1)
        self.assertEqual(
            json.loads(out),
            {"status": "CAPABILITY_UNAVAILABLE", "code": "UNKNOWN_COMMAND"},
        )


class StatusIsUnchangedTests(unittest.TestCase):
    def test_no_argument_means_status(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            self.assertEqual(_run((), root), _run(("status",), root))
            code, out = _run((), root)
        self.assertEqual(code, 3)
        payload = json.loads(out)
        self.assertEqual(payload["status"], "CAPABILITY_UNAVAILABLE")
        self.assertIsNone(payload["plugin_version"])
        self.assertEqual(
            sorted(payload),
            [
                "launcher_present",
                "ledger_present",
                "plugin_version",
                "status",
                "venv_present",
            ],
        )

    def test_status_reads_an_installed_version(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "plugin").mkdir()
            (root / "plugin" / "payload-manifest.json").write_text(
                json.dumps({"plugin_version": "9.9.9"}), encoding="utf-8"
            )
            code, out = _run(("status",), root)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["plugin_version"], "9.9.9")


if __name__ == "__main__":
    unittest.main()
