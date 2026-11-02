from __future__ import annotations

import sys

from pydantic import ValidationError

from .predictive_context_boundary import (
    BoundaryDecision,
    ContextBudgetAssessmentRequest,
    ContextBudgetAssessmentResult,
    ContextBudgetGuard,
)


_MAX_INPUT_BYTES = 65_536


def main() -> int:
    result = ContextBudgetAssessmentResult.invalid_request()
    if len(sys.argv) == 1:
        try:
            payload = sys.stdin.buffer.read(_MAX_INPUT_BYTES + 1)
        except (AttributeError, OSError):
            payload = b""
        if len(payload) <= _MAX_INPUT_BYTES:
            try:
                request = ContextBudgetAssessmentRequest.model_validate_json(payload)
            except (TypeError, ValueError, ValidationError):
                pass
            else:
                result = ContextBudgetGuard().assess(request)

    sys.stdout.write(result.model_dump_json() + "\n")
    if result.decision is BoundaryDecision.EXECUTE_WITHOUT_COMPACTION:
        return 0
    if result.decision is BoundaryDecision.INVALID_REQUEST:
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
