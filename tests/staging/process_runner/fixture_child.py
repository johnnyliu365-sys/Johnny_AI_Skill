"""Deterministic child used only by Ticket 05S2 process-runner tests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import os
import sys
import time


class FixtureMode(str, Enum):
    SUCCESS = "success"
    NONZERO = "nonzero"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class FixtureOverlayEntry:
    key: str
    value: str

    @classmethod
    def from_payload(cls, payload: object) -> FixtureOverlayEntry:
        if not isinstance(payload, dict):
            raise ValueError("fixture overlay entry must be an object")
        values: dict[str, object] = {}
        for key, value in payload.items():
            if not isinstance(key, str):
                raise ValueError("fixture overlay key must be text")
            values[key] = value
        if set(values) != {"key", "value"}:
            raise ValueError("fixture overlay entry has an unsupported shape")
        key = values["key"]
        value = values["value"]
        if not isinstance(key, str) or not isinstance(value, str) or not value or value != value.strip():
            raise ValueError("fixture overlay entry is invalid")
        return cls(key=key, value=value)


@dataclass(frozen=True)
class FixtureObservation:
    arguments: tuple[str, ...]
    working_directory: str
    overlay: tuple[FixtureOverlayEntry, ...]
    environment_keys: tuple[str, ...]

    def to_json(self) -> str:
        payload: dict[str, object] = {
            "arguments": list(self.arguments),
            "working_directory": self.working_directory,
            "overlay": [{"key": entry.key, "value": entry.value} for entry in self.overlay],
            "environment_keys": list(self.environment_keys),
        }
        return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> FixtureObservation:
        payload_object: object = json.loads(raw)
        if not isinstance(payload_object, dict):
            raise ValueError("fixture observation must be an object")
        payload: dict[str, object] = {}
        for key, value in payload_object.items():
            if not isinstance(key, str):
                raise ValueError("fixture observation key must be text")
            payload[key] = value
        if set(payload) != {"arguments", "working_directory", "overlay", "environment_keys"}:
            raise ValueError("fixture observation has an unsupported shape")
        arguments_object = payload["arguments"]
        if not isinstance(arguments_object, list):
            raise ValueError("fixture arguments must be a list")
        arguments: list[str] = []
        for argument in arguments_object:
            if not isinstance(argument, str):
                raise ValueError("fixture argument must be text")
            arguments.append(argument)
        working_directory = payload["working_directory"]
        overlay_object = payload["overlay"]
        if not isinstance(working_directory, str) or not working_directory or not isinstance(overlay_object, list):
            raise ValueError("fixture observation values are invalid")
        overlay = tuple(FixtureOverlayEntry.from_payload(entry) for entry in overlay_object)
        environment_keys_object = payload["environment_keys"]
        if not isinstance(environment_keys_object, list):
            raise ValueError("fixture environment keys must be a list")
        environment_keys: list[str] = []
        for key in environment_keys_object:
            if not isinstance(key, str):
                raise ValueError("fixture environment key must be text")
            environment_keys.append(key)
        return cls(
            arguments=tuple(arguments),
            working_directory=working_directory,
            overlay=overlay,
            environment_keys=tuple(environment_keys),
        )


_OVERLAY_KEYS = ("USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP", "CODEX_HOME")
LATE_WRITE_DELAY_SECONDS = 2.0


def _required_environment(key: str) -> str:
    value = os.environ.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError("fixture requires the exact owned overlay")
    return value


def _observation(arguments: tuple[str, ...]) -> FixtureObservation:
    overlay = tuple(FixtureOverlayEntry(key=key, value=_required_environment(key)) for key in _OVERLAY_KEYS)
    return FixtureObservation(
        arguments=arguments,
        working_directory=os.getcwd(),
        overlay=overlay,
        environment_keys=tuple(sorted(os.environ)),
    )


def _write_observation(name: str, observation: FixtureObservation) -> None:
    codex_home = Path(_required_environment("CODEX_HOME"))
    codex_home.joinpath(name).write_text(observation.to_json(), encoding="utf-8")


def main(arguments: tuple[str, ...]) -> int:
    if not arguments:
        return 64
    try:
        mode = FixtureMode(arguments[0])
        observation = _observation(arguments)
        _write_observation("fixture-started.json", observation)
    except (ValueError, OSError):
        return 64
    if mode is FixtureMode.TIMEOUT:
        time.sleep(LATE_WRITE_DELAY_SECONDS)
    _write_observation("fixture-complete.json", observation)
    if mode is FixtureMode.NONZERO:
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:])))
