"""Strict decoder for versioned local test-command data."""

from __future__ import annotations

import json
import re

from library.local_orchestration.test_dependency_inventory import DeclaredTestCommand

_MAX_PLAN_BYTES = 65_536
_MAX_COMMANDS = 32
_MAX_ARGV_ITEMS = 32
_COMMAND_REF = re.compile(r"[a-z][a-z0-9:-]{2,127}\Z")
_TARGET_COMPONENT = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*\Z")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _string_keyed_object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError("object keys must be strings")
        result[key] = item
    return result


def _valid_target(target: str) -> bool:
    if not target.startswith("tests/") or not target.endswith(".py") or "\\" in target:
        return False
    components = target.split("/")
    return all(
        component not in {"", ".", ".."} and _TARGET_COMPONENT.fullmatch(component)
        for component in components
    )


def read_command_plan(data: bytes) -> tuple[DeclaredTestCommand, ...]:
    """Decode the closed, local-only command plan; malformed bytes raise ValueError."""

    if not isinstance(data, bytes) or len(data) > _MAX_PLAN_BYTES:
        raise ValueError("command plan exceeds its byte limit")
    try:
        text = data.decode("utf-8", errors="strict")
        value: object = json.loads(text, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("command plan is not valid UTF-8 JSON") from error

    document = _string_keyed_object(value)
    if set(document) != {"schema_revision", "scope", "commands"}:
        raise ValueError("command plan keys do not match the schema")
    revision = document["schema_revision"]
    if type(revision) is not int or revision != 1:
        raise ValueError("unsupported command plan revision")
    if document["scope"] != "LOCAL_VERIFICATION_ONLY":
        raise ValueError("unsupported command plan scope")
    command_values = document["commands"]
    if not isinstance(command_values, list) or not command_values:
        raise ValueError("command plan must contain commands")
    if len(command_values) > _MAX_COMMANDS:
        raise ValueError("command plan contains too many commands")

    commands: list[DeclaredTestCommand] = []
    seen_refs: set[str] = set()
    for command_value in command_values:
        command = _string_keyed_object(command_value)
        if set(command) != {"command_ref", "argv"}:
            raise ValueError("command keys do not match the schema")
        command_ref = command["command_ref"]
        argv_value = command["argv"]
        if not isinstance(command_ref, str) or not _COMMAND_REF.fullmatch(command_ref):
            raise ValueError("command_ref is invalid")
        if command_ref in seen_refs:
            raise ValueError("command_ref values must be unique")
        if not isinstance(argv_value, list) or len(argv_value) > _MAX_ARGV_ITEMS:
            raise ValueError("argv must be a bounded array")
        if any(not isinstance(item, str) for item in argv_value):
            raise ValueError("argv items must be strings")
        argv = tuple(argv_value)
        if (
            len(argv) < 7
            or argv[:3] != ("python", "-m", "pytest")
            or argv[-3:] != ("-q", "-p", "no:cacheprovider")
        ):
            raise ValueError("argv is outside the local pytest grammar")
        targets = argv[3:-3]
        if not targets or len(targets) != len(set(targets)):
            raise ValueError("argv targets must be non-empty and unique")
        if any(not _valid_target(target) for target in targets):
            raise ValueError("argv target is not a repository test file")
        seen_refs.add(command_ref)
        commands.append(DeclaredTestCommand(command_ref=command_ref, argv=argv))
    return tuple(commands)


__all__ = ["read_command_plan"]
