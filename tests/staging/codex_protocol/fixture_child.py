"""Deterministic child that writes one documented Codex protocol response."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Literal, TypeAlias


RESPONSE_FILE_NAME = ".johnny-05s3-response.json"


FixtureSurfaceValue: TypeAlias = Literal[
    "MARKETPLACE_ADD",
    "MARKETPLACE_LIST",
    "MARKETPLACE_REMOVE",
    "PLUGIN_ADD",
    "PLUGIN_LIST",
    "PLUGIN_REMOVE",
]


def main(arguments: tuple[str, ...]) -> int:
    if len(arguments) != 1:
        return 64
    try:
        surface = _fixture_surface(arguments[0])
        encoded = json.dumps(_payload(surface), ensure_ascii=True, separators=(",", ":")).encode("utf-8")
        Path.cwd().joinpath(RESPONSE_FILE_NAME).write_bytes(encoded)
    except (OSError, ValueError):
        return 64
    return 0


def _fixture_surface(value: str) -> FixtureSurfaceValue:
    if value == "MARKETPLACE_ADD":
        return "MARKETPLACE_ADD"
    if value == "MARKETPLACE_LIST":
        return "MARKETPLACE_LIST"
    if value == "MARKETPLACE_REMOVE":
        return "MARKETPLACE_REMOVE"
    if value == "PLUGIN_ADD":
        return "PLUGIN_ADD"
    if value == "PLUGIN_LIST":
        return "PLUGIN_LIST"
    if value == "PLUGIN_REMOVE":
        return "PLUGIN_REMOVE"
    raise ValueError("unsupported protocol surface")


def _payload(surface: FixtureSurfaceValue) -> dict[str, object]:
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
    if surface == "MARKETPLACE_ADD":
        return {"marketplaceName": "child-market", "installedRoot": "child-root", "alreadyAdded": False}
    if surface == "MARKETPLACE_LIST":
        return {"marketplaces": [marketplace_entry, marketplace_without_source]}
    if surface == "MARKETPLACE_REMOVE":
        return {"marketplaceName": "child-market", "installedRoot": "child-root"}
    if surface == "PLUGIN_ADD":
        return {
            "pluginId": "child-plugin-id",
            "name": "child-plugin",
            "marketplaceName": "child-market",
            "version": "release_candidate",
            "installedPath": "child-installed-path",
            "authPolicy": "child-auth-policy",
        }
    if surface == "PLUGIN_LIST":
        return {"installed": [plugin_entry], "available": [plugin_without_source]}
    return {"pluginId": "child-plugin-id", "name": "child-plugin", "marketplaceName": "child-market"}


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:])))
