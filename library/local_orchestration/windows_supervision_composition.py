"""Windows composition root for receipt-bound supervision, without Router binding."""

from __future__ import annotations

from pathlib import Path

from .git_handoff_event_adapter import GitCliReadbackPort
from .one_shot_deadline import (
    MonotonicOneShotDeadlineFactory,
    SystemMonotonicClock,
)
from .receipt_bound_supervision import ReceiptBoundSupervisionController
from .senior_review_inbox import (
    ReviewWakeSubmissionPort,
    SeniorReviewInboxCoordinator,
)
from .windows_native_git_ref import WindowsNativeGitRefNotificationFactory


def build_windows_receipt_bound_supervision(
    repository_root: Path,
    wake_coordinator: SeniorReviewInboxCoordinator,
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


def build_windows_supervision_without_review_batching(
    repository_root: Path,
    wake_submission: ReviewWakeSubmissionPort,
) -> ReceiptBoundSupervisionController:
    """Compose supervision with a bare wake submission and NO FIFO batching.

    The canonical builder above requires the Senior review inbox coordinator,
    which owns FIFO batching and the "wake once per new batch" rule. This
    variant deliberately omits that layer and is admitted only where no
    committed review-cluster resolver exists yet, such as the 0.4.x event
    runner. It wakes once per validated handoff instead of once per batch, so
    a reviewer can receive more wakes than the batching policy would send.
    Callers must not present it as the batched supervision path.
    """

    clock = SystemMonotonicClock()
    return ReceiptBoundSupervisionController(
        GitCliReadbackPort(repository_root),
        WindowsNativeGitRefNotificationFactory(repository_root),
        MonotonicOneShotDeadlineFactory(clock),
        wake_submission,
        clock,
    )


__all__ = [
    "build_windows_receipt_bound_supervision",
    "build_windows_supervision_without_review_batching",
]
