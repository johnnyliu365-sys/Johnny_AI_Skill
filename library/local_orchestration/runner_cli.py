"""Runner, wake-inbox and wake-capability commands of the live CLI.

Every command prints exactly one typed JSON line. Nothing here starts a
supervision effect implicitly: `runner start` is the only command that spawns
the detached runner, and it reports the resolved wake channel truthfully so a
candidate-inbox degradation can never be mistaken for automatic wake.
"""

from __future__ import annotations

import json
from pathlib import Path

from library.workflow_router.contracts import ProjectId

from .event_runner import resolve_wake_channel, subscriptions_path
from .johnny_root_layout import JohnnyRootLayout
from .project_runner_registry import RunnerStarted, RunnerStopped
from .runner_lifecycle_port import (
    RealRunnerLifecyclePort,
    read_runner_state,
    runner_pid_path,
)
from .wake_candidate_inbox import read_candidates
from .wake_capability import WakeCapabilityStatus, probe_wake_capability

_PLACEHOLDER_PROJECT: ProjectId = "prj_0000000000000000"


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, sort_keys=True))


def _runner_start(layout: JohnnyRootLayout) -> int:
    if not subscriptions_path(layout).is_file():
        _emit({"status": "BLOCKED", "code": "NO_SUBSCRIPTIONS"})
        return 2
    channel = resolve_wake_channel(layout)
    result = RealRunnerLifecyclePort(layout).start(_PLACEHOLDER_PROJECT)
    if not isinstance(result, RunnerStarted):
        state = read_runner_state(layout)
        _emit(
            {
                "status": "BLOCKED",
                "code": "RUNNER_START_UNAVAILABLE",
                "runner_state": state,
                "wake_channel": channel.kind.value,
            }
        )
        return 2
    _emit(
        {
            "status": "RUNNING",
            "runner_ref": result.runner_ref,
            "wake_channel": channel.kind.value,
            "automatic_wake": channel.kind.value == "HOST_COMMAND",
        }
    )
    return 0


def _runner_stop(layout: JohnnyRootLayout) -> int:
    result = RealRunnerLifecyclePort(layout).stop(_PLACEHOLDER_PROJECT, "runner")
    if not isinstance(result, RunnerStopped):
        _emit({"status": "BLOCKED", "code": "RUNNER_STOP_UNAVAILABLE"})
        return 2
    _emit({"status": "STOPPED"})
    return 0


def _runner_status(layout: JohnnyRootLayout) -> int:
    state = read_runner_state(layout)
    running = (
        state is not None
        and state.get("status") == "RUNNING"
        and runner_pid_path(layout).is_file()
    )
    _emit(
        {
            "status": "RUNNING" if running else "NOT_RUNNING",
            "runner_state": state,
        }
    )
    return 0 if running else 3


def run_runner_command(
    command: str, arguments: tuple[str, ...], johnny_root: Path
) -> int:
    """Dispatch one runner-family command against the resolved Johnny root."""

    layout = JohnnyRootLayout(base=johnny_root)
    if command == "wake-capability":
        probe = probe_wake_capability(layout)
        _emit(
            {
                "status": probe.status.value,
                "channel": probe.channel.value,
                "failure": probe.failure.value if probe.failure else None,
                "automatic_wake": probe.status is WakeCapabilityStatus.PROVEN,
            }
        )
        return 0 if probe.status is WakeCapabilityStatus.PROVEN else 3
    if command == "wake-inbox":
        try:
            candidates = read_candidates(layout)
        except (OSError, ValueError):
            _emit({"status": "BLOCKED", "code": "INBOX_UNREADABLE"})
            return 2
        _emit(
            {
                "status": "OK",
                "candidate_count": len(candidates),
                "candidates": [
                    {
                        "attempt_id": record.attempt_id,
                        "reviewer_task_id": record.reviewer_task_id,
                        "payload_digest": record.payload_digest,
                        "payload_path": record.payload_path,
                    }
                    for record in candidates
                ],
            }
        )
        return 0
    subcommand = arguments[0] if arguments else "status"
    if subcommand == "start":
        return _runner_start(layout)
    if subcommand == "stop":
        return _runner_stop(layout)
    if subcommand == "status":
        return _runner_status(layout)
    _emit({"status": "CAPABILITY_UNAVAILABLE", "code": "UNKNOWN_SUBCOMMAND"})
    return 2


__all__ = ["run_runner_command"]
