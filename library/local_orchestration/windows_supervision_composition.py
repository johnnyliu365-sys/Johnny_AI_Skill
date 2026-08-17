"""Windows composition root for receipt-bound supervision, without Router binding."""

from __future__ import annotations

from pathlib import Path

from .git_handoff_event_adapter import GitCliReadbackPort
from .one_shot_deadline import (
    MonotonicOneShotDeadlineFactory,
    SystemMonotonicClock,
)
from .receipt_bound_supervision import ReceiptBoundSupervisionController
from .role_wake_composition import RoleWakeCoordinator
from .windows_native_git_ref import WindowsNativeGitRefNotificationFactory


def build_windows_receipt_bound_supervision(
    repository_root: Path,
    wake_coordinator: RoleWakeCoordinator,
) -> ReceiptBoundSupervisionController:
    """Bind production local ports while leaving Router and host wake ports injected."""

    clock = SystemMonotonicClock()
    return ReceiptBoundSupervisionController(
        GitCliReadbackPort(repository_root),
        WindowsNativeGitRefNotificationFactory(repository_root),
        MonotonicOneShotDeadlineFactory(clock),
        wake_coordinator,
        clock,
    )


__all__ = ["build_windows_receipt_bound_supervision"]
