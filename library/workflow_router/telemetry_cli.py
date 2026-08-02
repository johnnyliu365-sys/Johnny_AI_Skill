"""Command-line validation for a local metadata-only Router telemetry JSONL file."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .telemetry import ContextUsageValidator, JsonlContextUsageStore


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one JSONL file and return nonzero unless the reduction claim is verified."""

    parser = argparse.ArgumentParser(
        description="Validate metadata-only Router context-load telemetry."
    )
    parser.add_argument("path", type=Path, help="Ignored local router-usage.jsonl path")
    parser.add_argument(
        "--minimum-reduction-bps",
        type=int,
        default=1,
        help="Required median reduction in basis points; 5000 means 50%%.",
    )
    arguments = parser.parse_args(argv)
    if arguments.minimum_reduction_bps < 0:
        parser.error("--minimum-reduction-bps must be zero or greater")
    records = JsonlContextUsageStore.read(path=arguments.path)
    report = ContextUsageValidator().validate(
        records=records,
        minimum_reduction_basis_points=arguments.minimum_reduction_bps,
    )
    print(report.model_dump_json(indent=2))
    return 0 if report.reduction_verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
