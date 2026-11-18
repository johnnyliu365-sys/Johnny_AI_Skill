"""The Wayfinder two-round information-gap rule as one standalone function.

Signature (stdlib and ``contracts.py`` only)::

    decide_wayfinder_gap(
        rounds: Sequence[WayfinderInfoRequest],
        *,
        owner_input_provided: bool = False,
    ) -> WayfinderGapDecision

Rules carried over from the retired RouterEngine profile:

* no round at all means no blocking gap, so Wayfinder advances;
* a round with its gaps is a declared owner wait (``SUSPEND`` /
  ``WAIT_FOR_HUMAN`` / ``WAYFINDER_INPUT_GAP``);
* committed owner input re-enters Wayfinder (``RETRY`` / ``AUTO_CONTINUE``);
  after the second round it may not ask again, so the next return is terminal;
* a third round, a round out of order, or a second round that asks a field the
  first round never listed is refused with ``ValueError``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .contracts import (
    ContinuationDirective,
    HumanWaitReason,
    RouterOutcome,
    WayfinderInfoRequest,
)

MAX_WAYFINDER_ROUNDS = 2


@dataclass(frozen=True, slots=True)
class WayfinderGapDecision:
    """The disposition after the rounds recorded so far."""

    outcome: RouterOutcome
    continuation: ContinuationDirective
    wait_reason: HumanWaitReason | None
    may_ask_again: bool


def decide_wayfinder_gap(
    rounds: Sequence[WayfinderInfoRequest],
    *,
    owner_input_provided: bool = False,
) -> WayfinderGapDecision:
    """Return the disposition for the recorded gap rounds, or refuse a third round."""

    if len(rounds) > MAX_WAYFINDER_ROUNDS:
        raise ValueError("a third Wayfinder question round is refused")
    for index, request in enumerate(rounds, start=1):
        if request.round_number != index:
            raise ValueError("Wayfinder rounds must be recorded in order from round 1")
    if len(rounds) == MAX_WAYFINDER_ROUNDS:
        first_fields = {gap.field for gap in rounds[0].gaps}
        second = rounds[1]
        if not set(second.answered_fields) <= first_fields:
            raise ValueError("a second round may only answer fields the first round asked")
        if any(gap.field not in first_fields for gap in second.gaps):
            raise ValueError("a second round may not ask a field the first round did not")
    if not rounds:
        return WayfinderGapDecision(
            RouterOutcome.ADVANCE, ContinuationDirective.AUTO_CONTINUE, None, True
        )
    may_ask_again = len(rounds) < MAX_WAYFINDER_ROUNDS
    if owner_input_provided:
        return WayfinderGapDecision(
            RouterOutcome.RETRY, ContinuationDirective.AUTO_CONTINUE, None, may_ask_again
        )
    return WayfinderGapDecision(
        RouterOutcome.SUSPEND,
        ContinuationDirective.WAIT_FOR_HUMAN,
        HumanWaitReason.WAYFINDER_INPUT_GAP,
        may_ask_again,
    )
