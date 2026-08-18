"""Typed live CLI running inside the installed Johnny runtime venv.

`status` reads back the installed state; `uninstall` composes the real
receipt-owned uninstall transaction (wired in the live-install line's L6
ticket). Unknown commands return a typed capability result and no effect.
"""

from __future__ import annotations

import json
from pathlib import Path


def _status_payload(johnny_root: Path) -> dict[str, object]:
    plugin_manifest = johnny_root / "plugin" / "payload-manifest.json"
    version = None
    if plugin_manifest.is_file():
        try:
            recorded = json.loads(plugin_manifest.read_text(encoding="utf-8"))
            candidate = recorded.get("plugin_version")
            version = candidate if type(candidate) is str else None
        except (OSError, ValueError):
            version = None
    return {
        "status": "OK" if version is not None else "CAPABILITY_UNAVAILABLE",
        "plugin_version": version,
        "venv_present": (johnny_root / "venv" / "Scripts" / "python.exe").is_file(),
        "launcher_present": (
            johnny_root / "launcher" / "johnny-router.ps1"
        ).is_file(),
        "ledger_present": (johnny_root / "ledger.json").is_file(),
    }


def run_live_cli(argv: tuple[str, ...], johnny_root: Path) -> int:
    """Dispatch one command; every path prints exactly one typed JSON line."""

    command = argv[0] if argv else "status"
    if command == "status":
        payload = _status_payload(johnny_root)
        print(json.dumps(payload, sort_keys=True))
        return 0 if payload["status"] == "OK" else 3
    if command == "uninstall":
        # Wired by the live-install line's L6 ticket; until then this stays a
        # typed block rather than a silent no-op.
        print('{"status":"CAPABILITY_UNAVAILABLE","code":"LIVE_UNINSTALL_NOT_WIRED"}')
        return 3
    print('{"status":"CAPABILITY_UNAVAILABLE","code":"UNKNOWN_COMMAND"}')
    return 2


__all__ = ["run_live_cli"]
