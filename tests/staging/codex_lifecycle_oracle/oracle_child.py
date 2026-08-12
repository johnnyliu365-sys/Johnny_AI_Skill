"""Real child that freshly validates persisted 05S4 oracle state and payloads."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys


COMMAND_FILE_NAME = ".johnny-05s4-command.json"
STATE_FILE_NAME = ".johnny-05s4-state.json"
RESPONSE_FILE_NAME = ".johnny-05s3-response.json"
PAYLOAD_DIRECTORY_NAME = "oracle-payloads"

SUCCESS = 0
COMMAND_INVALID = 64
STATE_MISSING = 65
STATE_INVALID = 66
TOPOLOGY_INVALID = 67
DIGEST_MISMATCH = 68
IO_FAILED = 69

_COMMAND_ACTIONS = {
    "MARKETPLACE_ADD": "MARKETPLACE_ADD",
    "MARKETPLACE_LIST": "MARKETPLACE_LIST",
    "MARKETPLACE_REMOVE": "MARKETPLACE_REMOVE",
    "PLUGIN_ADD": "PLUGIN_ADD",
    "PLUGIN_LIST": "PLUGIN_LIST",
    "PLUGIN_REMOVE": "PLUGIN_REMOVE",
    "VERSION": "VERSION",
    "ABSENCE": "PLUGIN_LIST",
}
_IDENTITY_FIELDS = (
    "marketplace_name",
    "marketplace_root",
    "plugin_id",
    "plugin_name",
    "plugin_version",
    "plugin_source",
    "plugin_install_policy",
    "plugin_auth_policy",
    "plugin_installed_path",
)
_MARKETPLACE_FIELDS = ("name", "root", "locator", "digest")
_PLUGIN_FIELDS = (
    "plugin_id",
    "name",
    "marketplace_name",
    "version",
    "source",
    "install_policy",
    "auth_policy",
    "installed_path",
    "locator",
    "digest",
)


class OracleFailure(ValueError):
    """A finite child failure code with no outward exception detail."""

    def __init__(self, code: int) -> None:
        super().__init__(str(code))
        self.code = code


def main(arguments: tuple[str, ...]) -> int:
    if len(arguments) != 1:
        return COMMAND_INVALID
    try:
        codex_home_text = os.environ.get("CODEX_HOME")
        if not isinstance(codex_home_text, str) or not codex_home_text:
            return IO_FAILED
        codex_home = Path(codex_home_text)
        command = _load_command(Path.cwd() / COMMAND_FILE_NAME, arguments[0])
        state_path = codex_home / STATE_FILE_NAME
        state = _load_state(state_path, codex_home)
        _validate_physical_state(state, codex_home)
        payload = _apply(command, state, state_path, codex_home)
        _write_response(Path.cwd() / RESPONSE_FILE_NAME, payload)
    except OracleFailure as failure:
        return failure.code
    except (OSError, ValueError):
        return IO_FAILED
    return SUCCESS


def _load_command(path: Path, selected_surface: str) -> dict[str, object]:
    raw = _load_object(path, COMMAND_INVALID)
    if tuple(raw) != ("action", "identity"):
        raise OracleFailure(COMMAND_INVALID)
    action = raw["action"]
    identity = raw["identity"]
    if not isinstance(action, str) or _COMMAND_ACTIONS.get(action) != selected_surface:
        raise OracleFailure(COMMAND_INVALID)
    if not isinstance(identity, dict) or tuple(identity) != _IDENTITY_FIELDS:
        raise OracleFailure(COMMAND_INVALID)
    for field in _IDENTITY_FIELDS:
        if not _is_nonblank_text(identity[field]):
            raise OracleFailure(COMMAND_INVALID)
    for canonical in (identity["marketplace_name"], identity["plugin_id"]):
        if not _is_canonical_segment(canonical):
            raise OracleFailure(COMMAND_INVALID)
    if not _is_logical_installed_path(identity["plugin_installed_path"]):
        raise OracleFailure(COMMAND_INVALID)
    return raw


def _load_state(path: Path, codex_home: Path) -> dict[str, object]:
    if not _is_plain_file(path):
        if path.exists():
            raise OracleFailure(TOPOLOGY_INVALID)
        raise OracleFailure(STATE_MISSING)
    state = _load_object(path, STATE_INVALID)
    expected = (
        "owner",
        "environment_id",
        "codex_version",
        "marketplaces",
        "plugins",
        "foreign_marketplaces",
        "foreign_plugins",
    )
    if tuple(state) != expected:
        raise OracleFailure(STATE_INVALID)
    _validate_state_identity(state, codex_home)
    if not _is_nonblank_text(state["codex_version"]):
        raise OracleFailure(STATE_INVALID)
    for collection in ("marketplaces", "plugins", "foreign_marketplaces", "foreign_plugins"):
        if not isinstance(state[collection], list):
            raise OracleFailure(STATE_INVALID)
    _validate_records(state)
    return state


def _load_object(path: Path, code: int) -> dict[str, object]:
    if not _is_plain_file(path):
        raise OracleFailure(code)
    try:
        decoded = path.read_text(encoding="utf-8")
        value = json.loads(decoded, object_pairs_hook=_unique_object)
    except (_DuplicateKey, UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError, OSError):
        raise OracleFailure(code) from None
    if not isinstance(value, dict):
        raise OracleFailure(code)
    return value


def _validate_state_identity(state: dict[str, object], codex_home: Path) -> None:
    marker_path = codex_home.parent / ".johnny-stage-env-owner.json"
    marker = _load_object(marker_path, STATE_INVALID)
    owner = state["owner"]
    environment_id = state["environment_id"]
    if not isinstance(owner, dict) or not isinstance(environment_id, dict):
        raise OracleFailure(STATE_INVALID)
    if owner != marker.get("owner") or environment_id != marker.get("environment_id"):
        raise OracleFailure(STATE_INVALID)


def _validate_records(state: dict[str, object]) -> None:
    for collection in ("marketplaces", "foreign_marketplaces"):
        marketplace_names: set[str] = set()
        value = state[collection]
        assert isinstance(value, list)
        for record in value:
            _validate_marketplace_record(record)
            assert isinstance(record, dict)
            name = record["name"]
            assert isinstance(name, str)
            if name in marketplace_names:
                raise OracleFailure(STATE_INVALID)
            marketplace_names.add(name)
    for collection in ("plugins", "foreign_plugins"):
        plugin_ids: set[str] = set()
        value = state[collection]
        assert isinstance(value, list)
        for record in value:
            _validate_plugin_record(record)
            assert isinstance(record, dict)
            plugin_id = record["plugin_id"]
            assert isinstance(plugin_id, str)
            if plugin_id in plugin_ids:
                raise OracleFailure(STATE_INVALID)
            plugin_ids.add(plugin_id)


def _validate_marketplace_record(record: object) -> None:
    if not isinstance(record, dict) or tuple(record) != _MARKETPLACE_FIELDS:
        raise OracleFailure(STATE_INVALID)
    if not all(_is_nonblank_text(record[field]) for field in _MARKETPLACE_FIELDS):
        raise OracleFailure(STATE_INVALID)
    name = record["name"]
    locator = record["locator"]
    digest = record["digest"]
    if not isinstance(name, str) or not isinstance(locator, str) or not isinstance(digest, str):
        raise OracleFailure(STATE_INVALID)
    if not _is_canonical_segment(name) or locator != f"marketplaces/{name}.json" or not _is_digest(digest):
        raise OracleFailure(STATE_INVALID)


def _validate_plugin_record(record: object) -> None:
    if not isinstance(record, dict) or tuple(record) != _PLUGIN_FIELDS:
        raise OracleFailure(STATE_INVALID)
    if not all(_is_nonblank_text(record[field]) for field in _PLUGIN_FIELDS):
        raise OracleFailure(STATE_INVALID)
    plugin_id = record["plugin_id"]
    installed_path = record["installed_path"]
    locator = record["locator"]
    digest = record["digest"]
    if not isinstance(plugin_id, str) or not isinstance(installed_path, str) or not isinstance(locator, str) or not isinstance(digest, str):
        raise OracleFailure(STATE_INVALID)
    if not _is_canonical_segment(plugin_id) or not _is_logical_installed_path(installed_path) or locator != f"plugins/{plugin_id}.json" or not _is_digest(digest):
        raise OracleFailure(STATE_INVALID)


def _validate_physical_state(state: dict[str, object], codex_home: Path) -> None:
    payload_root = codex_home / PAYLOAD_DIRECTORY_NAME
    if not _is_plain_directory(codex_home):
        raise OracleFailure(TOPOLOGY_INVALID)
    for collection in ("marketplaces", "foreign_marketplaces"):
        records = state[collection]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            _validate_exact_payload(payload_root, record, _marketplace_payload(record))
    for collection in ("plugins", "foreign_plugins"):
        records = state[collection]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            _validate_exact_payload(payload_root, record, _plugin_payload(record))
    expected_locators = _state_locators(state)
    if payload_root.exists() and not _is_plain_directory(payload_root):
        raise OracleFailure(TOPOLOGY_INVALID)
    for category in ("marketplaces", "plugins"):
        directory = payload_root / category
        if not directory.exists():
            continue
        if not _is_plain_directory(directory):
            raise OracleFailure(TOPOLOGY_INVALID)
        for child in directory.iterdir():
            if not _is_plain_file(child) or f"{category}/{child.name}" not in expected_locators:
                raise OracleFailure(TOPOLOGY_INVALID)


def _state_locators(state: dict[str, object]) -> set[str]:
    locators: set[str] = set()
    for collection in ("marketplaces", "plugins", "foreign_marketplaces", "foreign_plugins"):
        records = state[collection]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            locator = record["locator"]
            assert isinstance(locator, str)
            locators.add(locator)
    return locators


def _validate_exact_payload(payload_root: Path, record: dict[str, object], expected: bytes) -> None:
    locator = record["locator"]
    digest = record["digest"]
    if not isinstance(locator, str) or not isinstance(digest, str):
        raise OracleFailure(STATE_INVALID)
    path = payload_root / locator
    if path.parent.parent != payload_root or not _is_plain_file(path):
        raise OracleFailure(TOPOLOGY_INVALID)
    try:
        actual = path.read_bytes()
    except OSError:
        raise OracleFailure(TOPOLOGY_INVALID) from None
    if actual != expected or _digest(actual) != digest:
        raise OracleFailure(DIGEST_MISMATCH)


def _apply(command: dict[str, object], state: dict[str, object], state_path: Path, codex_home: Path) -> dict[str, object]:
    action = command["action"]
    identity = command["identity"]
    assert isinstance(action, str)
    assert isinstance(identity, dict)
    if action == "VERSION":
        return _version(state)
    if action == "MARKETPLACE_ADD":
        return _marketplace_add(state, state_path, codex_home, identity)
    if action == "MARKETPLACE_LIST":
        return _marketplace_list(state)
    if action == "MARKETPLACE_REMOVE":
        return _marketplace_remove(state, state_path, codex_home, identity)
    if action == "PLUGIN_ADD":
        return _plugin_add(state, state_path, codex_home, identity)
    if action == "PLUGIN_LIST":
        return _plugin_list(state)
    if action == "PLUGIN_REMOVE":
        return _plugin_remove(state, state_path, codex_home, identity)
    return _absence(state, state_path, codex_home, identity)


def _version(state: dict[str, object]) -> dict[str, object]:
    """Return only the version freshly read from exact persisted oracle state."""

    version = state["codex_version"]
    if not isinstance(version, str):
        raise OracleFailure(STATE_INVALID)
    return {"version": version}


def _marketplace_add(state: dict[str, object], state_path: Path, codex_home: Path, identity: dict[str, object]) -> dict[str, object]:
    marketplaces = state["marketplaces"]
    assert isinstance(marketplaces, list)
    if any(record.get("name") == identity["marketplace_name"] for record in marketplaces if isinstance(record, dict)):
        raise OracleFailure(COMMAND_INVALID)
    record = _marketplace_record(identity)
    _write_payload(codex_home, record, _marketplace_payload(record))
    marketplaces.append(record)
    _write_state(state_path, state)
    return {"marketplaceName": record["name"], "installedRoot": record["root"], "alreadyAdded": False}


def _marketplace_list(state: dict[str, object]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for collection in ("marketplaces", "foreign_marketplaces"):
        records = state[collection]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            entries.append({"name": record["name"], "root": record["root"], "marketplaceSource": {"type": "local", "value": "oracle-source"}})
    return {"marketplaces": entries}


def _marketplace_remove(state: dict[str, object], state_path: Path, codex_home: Path, identity: dict[str, object]) -> dict[str, object]:
    record = _exact_marketplace(state, identity)
    plugins = state["plugins"]
    assert isinstance(plugins, list)
    if any(item.get("marketplace_name") == record["name"] for item in plugins if isinstance(item, dict)):
        raise OracleFailure(COMMAND_INVALID)
    _remove_payload(codex_home, record)
    marketplaces = state["marketplaces"]
    assert isinstance(marketplaces, list)
    marketplaces.remove(record)
    _write_state(state_path, state)
    return {"marketplaceName": record["name"], "installedRoot": record["root"]}


def _plugin_add(state: dict[str, object], state_path: Path, codex_home: Path, identity: dict[str, object]) -> dict[str, object]:
    _exact_marketplace(state, identity)
    plugins = state["plugins"]
    assert isinstance(plugins, list)
    if any(record.get("plugin_id") == identity["plugin_id"] for record in plugins if isinstance(record, dict)):
        raise OracleFailure(COMMAND_INVALID)
    record = _plugin_record(identity)
    _write_payload(codex_home, record, _plugin_payload(record))
    plugins.append(record)
    _write_state(state_path, state)
    return {
        "pluginId": record["plugin_id"],
        "name": record["name"],
        "marketplaceName": record["marketplace_name"],
        "version": record["version"],
        "installedPath": record["installed_path"],
        "authPolicy": record["auth_policy"],
    }


def _plugin_list(state: dict[str, object]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for collection in ("plugins", "foreign_plugins"):
        records = state[collection]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            entries.append(
                {
                    "pluginId": record["plugin_id"],
                    "name": record["name"],
                    "marketplaceName": record["marketplace_name"],
                    "version": record["version"],
                    "installed": True,
                    "enabled": True,
                    "source": record["source"],
                    "installPolicy": record["install_policy"],
                    "authPolicy": record["auth_policy"],
                    "marketplaceSource": {"type": "local", "value": "oracle-source"},
                }
            )
    return {"installed": entries, "available": []}


def _plugin_remove(state: dict[str, object], state_path: Path, codex_home: Path, identity: dict[str, object]) -> dict[str, object]:
    record = _exact_plugin(state, identity)
    _remove_payload(codex_home, record)
    plugins = state["plugins"]
    assert isinstance(plugins, list)
    plugins.remove(record)
    _write_state(state_path, state)
    return {"pluginId": record["plugin_id"], "name": record["name"], "marketplaceName": record["marketplace_name"]}


def _absence(state: dict[str, object], state_path: Path, codex_home: Path, identity: dict[str, object]) -> dict[str, object]:
    marketplaces = state["marketplaces"]
    plugins = state["plugins"]
    assert isinstance(marketplaces, list) and isinstance(plugins, list)
    if marketplaces or plugins:
        raise OracleFailure(COMMAND_INVALID)
    payload_root = codex_home / PAYLOAD_DIRECTORY_NAME
    for locator in (f"marketplaces/{identity['marketplace_name']}.json", f"plugins/{identity['plugin_id']}.json"):
        candidate = payload_root / locator
        if candidate.exists() or _is_reparse(candidate):
            raise OracleFailure(TOPOLOGY_INVALID)
    return _plugin_list(state)


def _exact_marketplace(state: dict[str, object], identity: dict[str, object]) -> dict[str, object]:
    records = state["marketplaces"]
    assert isinstance(records, list)
    for record in records:
        if isinstance(record, dict) and record.get("name") == identity["marketplace_name"] and record.get("root") == identity["marketplace_root"]:
            return record
    raise OracleFailure(COMMAND_INVALID)


def _exact_plugin(state: dict[str, object], identity: dict[str, object]) -> dict[str, object]:
    records = state["plugins"]
    assert isinstance(records, list)
    expected = {
        "plugin_id": identity["plugin_id"],
        "name": identity["plugin_name"],
        "marketplace_name": identity["marketplace_name"],
        "version": identity["plugin_version"],
        "source": identity["plugin_source"],
        "install_policy": identity["plugin_install_policy"],
        "auth_policy": identity["plugin_auth_policy"],
        "installed_path": identity["plugin_installed_path"],
    }
    for record in records:
        if isinstance(record, dict) and all(record.get(key) == value for key, value in expected.items()):
            return record
    raise OracleFailure(COMMAND_INVALID)


def _marketplace_record(identity: dict[str, object]) -> dict[str, object]:
    name = identity["marketplace_name"]
    root = identity["marketplace_root"]
    assert isinstance(name, str) and isinstance(root, str)
    locator = f"marketplaces/{name}.json"
    record: dict[str, object] = {"name": name, "root": root, "locator": locator, "digest": "0" * 64}
    record["digest"] = _digest(_marketplace_payload(record))
    return record


def _plugin_record(identity: dict[str, object]) -> dict[str, object]:
    plugin_id = identity["plugin_id"]
    assert isinstance(plugin_id, str)
    record: dict[str, object] = {
        "plugin_id": plugin_id,
        "name": identity["plugin_name"],
        "marketplace_name": identity["marketplace_name"],
        "version": identity["plugin_version"],
        "source": identity["plugin_source"],
        "install_policy": identity["plugin_install_policy"],
        "auth_policy": identity["plugin_auth_policy"],
        "installed_path": identity["plugin_installed_path"],
        "locator": f"plugins/{plugin_id}.json",
        "digest": "0" * 64,
    }
    record["digest"] = _digest(_plugin_payload(record))
    return record


def _marketplace_payload(record: dict[str, object]) -> bytes:
    return f"marketplace|{record['name']}|{record['root']}".encode("utf-8")


def _plugin_payload(record: dict[str, object]) -> bytes:
    return (
        f"plugin|{record['plugin_id']}|{record['name']}|{record['marketplace_name']}|{record['version']}|"
        f"{record['source']}|{record['install_policy']}|{record['auth_policy']}|{record['installed_path']}"
    ).encode("utf-8")


def _write_payload(codex_home: Path, record: dict[str, object], content: bytes) -> None:
    locator = record["locator"]
    assert isinstance(locator, str)
    path = codex_home / PAYLOAD_DIRECTORY_NAME / locator
    path.parent.mkdir(parents=True, exist_ok=True)
    if not _is_plain_directory(path.parent):
        raise OracleFailure(TOPOLOGY_INVALID)
    path.write_bytes(content)


def _remove_payload(codex_home: Path, record: dict[str, object]) -> None:
    locator = record["locator"]
    assert isinstance(locator, str)
    path = codex_home / PAYLOAD_DIRECTORY_NAME / locator
    if not _is_plain_file(path):
        raise OracleFailure(TOPOLOGY_INVALID)
    path.unlink()


def _write_state(path: Path, state: dict[str, object]) -> None:
    temporary = path.with_suffix(".next")
    temporary.write_text(json.dumps(state, ensure_ascii=True, separators=(",", ":")), encoding="utf-8")
    temporary.replace(path)


def _write_response(path: Path, payload: dict[str, object]) -> None:
    if path.exists() or _is_reparse(path):
        raise OracleFailure(TOPOLOGY_INVALID)
    path.write_bytes(json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8"))


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_nonblank_text(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip() and "\x00" not in value


def _is_logical_installed_path(value: object) -> bool:
    if not _is_nonblank_text(value) or not isinstance(value, str):
        return False
    if "/" in value or "%2e" in value.lower() or "%2f" in value.lower() or "%5c" in value.lower():
        return False
    if re.fullmatch(r'[A-Za-z]:\\(?:[^\\/:?*"<>|]+\\)*[^\\/:?*"<>|]+', value) is None:
        return False
    return all(
        segment not in (".", "..") and not segment.endswith((" ", "."))
        for segment in value.split("\\")
    )


def _is_canonical_segment(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]*", value) is not None


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


class _DuplicateKey(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey()
        result[key] = value
    return result


def _is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return False
    except OSError:
        return True
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _is_plain_file(path: Path) -> bool:
    if _is_reparse(path):
        return False
    try:
        return path.is_file() and path.resolve(strict=True) == path
    except OSError:
        return False


def _is_plain_directory(path: Path) -> bool:
    if _is_reparse(path):
        return False
    try:
        return path.is_dir() and path.resolve(strict=True) == path
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:])))
