"""Explicit telemetry report closure tests for CLOSURE-PD-13-R03-01."""

from __future__ import annotations

import csv
import io
import json
import unittest
from typing import cast

from pydantic import ValidationError

from library.workflow_router.telemetry import (
    ModelPriceSnapshot,
    ReasoningLevel,
    ReceiptUsageEvidenceSource,
    RoleModelUsageEvidence,
    TelemetryReport,
    TelemetryReportFailure,
    TelemetryReportRequest,
    TelemetryReportStatus,
    TelemetryRole,
    generate_telemetry_report,
    render_report_csv,
    render_report_json,
    render_report_table,
    report_bar_chart_data,
)

_RECEIPT = "receipt-pd13-primary-01"
_PRICE = ModelPriceSnapshot(
    currency="USD",
    input_price_per_million="3.000000",
    cached_input_price_per_million="0.300000",
    output_price_per_million="15.000000",
)


def _evidence(
    receipt_ref: str = _RECEIPT,
    role: TelemetryRole = TelemetryRole.IMPLEMENTATION_OWNER,
    model: str = "luna-standard",
    reasoning_level: ReasoningLevel = ReasoningLevel.XHIGH,
    input_tokens: int = 1000,
    cached_input_tokens: int = 400,
    output_tokens: int = 250,
    price: ModelPriceSnapshot = _PRICE,
) -> RoleModelUsageEvidence:
    return RoleModelUsageEvidence(
        receipt_ref=receipt_ref,
        evidence_commit="a" * 40,
        role=role,
        provider="provider-one",
        model=model,
        reasoning_level=reasoning_level,
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens,
        price=price,
    )


class _FakeEvidenceSource:
    """Receipt-indexed committed evidence fake."""

    def __init__(
        self,
        records: dict[str, tuple[RoleModelUsageEvidence, ...]],
        raise_on: frozenset[str] = frozenset(),
    ) -> None:
        self._records = records
        self._raise_on = raise_on
        self.resolved: list[str] = []

    def resolve(
        self, receipt_ref: str
    ) -> tuple[RoleModelUsageEvidence, ...] | None:
        self.resolved.append(receipt_ref)
        if receipt_ref in self._raise_on:
            raise OSError("evidence storage unavailable")
        return self._records.get(receipt_ref)


def _request(*receipts: str) -> TelemetryReportRequest:
    return TelemetryReportRequest(
        receipt_refs=tuple(receipts) if receipts else (_RECEIPT,),
        explicit_user_request=True,
    )


class TelemetryReportTests(unittest.TestCase):
    """T1-T6 closure cells for the explicit telemetry report."""

    def test_report_keeps_cached_input_separate_from_input_tokens(self) -> None:
        """T1: input, cached-input and output counts never merge."""

        source = _FakeEvidenceSource(
            {
                _RECEIPT: (
                    _evidence(input_tokens=1000, cached_input_tokens=400,
                              output_tokens=250),
                    _evidence(input_tokens=200, cached_input_tokens=100,
                              output_tokens=50),
                )
            }
        )
        report = generate_telemetry_report(_request(), source)

        self.assertIs(report.status, TelemetryReportStatus.GENERATED)
        self.assertIsNone(report.failure)
        self.assertEqual(len(report.groups), 1)
        group = report.groups[0]
        self.assertEqual(group.input_tokens, 1200)
        self.assertEqual(group.cached_input_tokens, 500)
        self.assertEqual(group.output_tokens, 300)
        self.assertEqual(group.input_cost, "0.003600")
        self.assertEqual(group.cached_input_cost, "0.000150")
        self.assertEqual(group.output_cost, "0.004500")
        self.assertEqual(group.total_cost, "0.008250")
        self.assertEqual(group.currency, "USD")

    def test_groups_separate_role_model_reasoning_and_currency(self) -> None:
        """T2: distinct role/model/reasoning/currency evidence never merges."""

        twd_price = ModelPriceSnapshot(
            currency="TWD",
            input_price_per_million="95.000000",
            cached_input_price_per_million="9.500000",
            output_price_per_million="475.000000",
        )
        source = _FakeEvidenceSource(
            {
                _RECEIPT: (
                    _evidence(),
                    _evidence(
                        role=TelemetryRole.SUPERVISOR_REVIEWER,
                        model="terra-standard",
                        reasoning_level=ReasoningLevel.HIGH,
                    ),
                    _evidence(model="luna-mini"),
                    _evidence(reasoning_level=ReasoningLevel.HIGH),
                    _evidence(price=twd_price),
                )
            }
        )
        report = generate_telemetry_report(_request(), source)

        self.assertIs(report.status, TelemetryReportStatus.GENERATED)
        keys = tuple(
            (
                group.role,
                group.model,
                group.reasoning_level,
                group.currency,
            )
            for group in report.groups
        )
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(report.groups), 5)

    def test_four_export_formats_agree(self) -> None:
        """T3: JSON, CSV, table and bar-chart data expose identical numbers."""

        source = _FakeEvidenceSource(
            {
                _RECEIPT: (
                    _evidence(),
                    _evidence(
                        role=TelemetryRole.SUPERVISOR_REVIEWER,
                        model="terra-standard",
                        reasoning_level=ReasoningLevel.HIGH,
                    ),
                )
            }
        )
        report = generate_telemetry_report(_request(), source)
        self.assertIs(report.status, TelemetryReportStatus.GENERATED)

        json_groups = json.loads(render_report_json(report))["groups"]
        csv_rows = list(csv.DictReader(io.StringIO(render_report_csv(report))))
        table_lines = [
            line
            for line in render_report_table(report).splitlines()
            if line and not line.startswith(("role", "-"))
        ]
        bars = report_bar_chart_data(report)

        self.assertEqual(len(json_groups), len(report.groups))
        self.assertEqual(len(csv_rows), len(report.groups))
        self.assertEqual(len(table_lines), len(report.groups))
        self.assertEqual(len(bars), 3 * len(report.groups))
        for index, group in enumerate(report.groups):
            self.assertEqual(json_groups[index]["input_tokens"], group.input_tokens)
            self.assertEqual(
                json_groups[index]["cached_input_tokens"], group.cached_input_tokens
            )
            self.assertEqual(json_groups[index]["output_tokens"], group.output_tokens)
            self.assertEqual(int(csv_rows[index]["input_tokens"]), group.input_tokens)
            self.assertEqual(
                int(csv_rows[index]["cached_input_tokens"]),
                group.cached_input_tokens,
            )
            self.assertEqual(
                int(csv_rows[index]["output_tokens"]), group.output_tokens
            )
            cells = table_lines[index].split()
            self.assertIn(str(group.input_tokens), cells)
            self.assertIn(str(group.cached_input_tokens), cells)
            self.assertIn(str(group.output_tokens), cells)
            group_bars = [datum for datum in bars if datum.group_index == index]
            by_class = {datum.token_class: datum.value for datum in group_bars}
            self.assertEqual(by_class["input"], group.input_tokens)
            self.assertEqual(by_class["cached_input"], group.cached_input_tokens)
            self.assertEqual(by_class["output"], group.output_tokens)

    def test_missing_receipt_returns_finite_failure(self) -> None:
        """T4: an unknown or unavailable receipt blocks with a finite failure."""

        with self.subTest(case="receipt_not_found"):
            source = _FakeEvidenceSource({})
            report = generate_telemetry_report(_request(), source)
            self.assertIs(report.status, TelemetryReportStatus.BLOCKED)
            self.assertIs(report.failure, TelemetryReportFailure.RECEIPT_NOT_FOUND)
            self.assertEqual(report.groups, ())

        with self.subTest(case="evidence_unavailable"):
            source = _FakeEvidenceSource({}, raise_on=frozenset({_RECEIPT}))
            report = generate_telemetry_report(_request(), source)
            self.assertIs(report.status, TelemetryReportStatus.BLOCKED)
            self.assertIs(
                report.failure, TelemetryReportFailure.EVIDENCE_UNAVAILABLE
            )

        with self.subTest(case="price_snapshot_conflict"):
            conflicting = _PRICE.model_copy(
                update={"input_price_per_million": "4.000000"}
            )
            source = _FakeEvidenceSource(
                {_RECEIPT: (_evidence(), _evidence(price=conflicting))}
            )
            report = generate_telemetry_report(_request(), source)
            self.assertIs(report.status, TelemetryReportStatus.BLOCKED)
            self.assertIs(
                report.failure, TelemetryReportFailure.PRICE_SNAPSHOT_CONFLICT
            )

    def test_raw_content_is_rejected(self) -> None:
        """T5: forged evidence carrying raw content never enters a report."""

        with self.subTest(case="typed_fields_refuse_raw_content"):
            for field, value in (
                ("receipt_ref", "C:/Users/someone/secret-context.txt"),
                ("provider", "https://provider.example/api?key=abc"),
                ("model", "model with raw prompt text"),
                ("evidence_commit", "not-a-commit\nSecret: hunter2"),
            ):
                with self.assertRaises(ValidationError):
                    _evidence().model_copy(update={field: value}).model_validate(
                        _evidence().model_dump() | {field: value}
                    )

        with self.subTest(case="forged_record_blocked_at_report_time"):
            forged = RoleModelUsageEvidence.model_construct(
                receipt_ref=_RECEIPT,
                evidence_commit="a" * 40,
                role=TelemetryRole.IMPLEMENTATION_OWNER,
                provider="provider-one",
                model="raw prompt: 請幫我把這段公司程式碼重構…",
                reasoning_level=ReasoningLevel.XHIGH,
                input_tokens=1,
                cached_input_tokens=0,
                output_tokens=1,
                price=_PRICE,
            )
            source = _FakeEvidenceSource({_RECEIPT: (forged,)})
            report = generate_telemetry_report(_request(), source)
            self.assertIs(report.status, TelemetryReportStatus.BLOCKED)
            self.assertIs(
                report.failure, TelemetryReportFailure.RAW_CONTENT_REJECTED
            )
            self.assertEqual(report.groups, ())

    def test_no_implicit_run_is_possible(self) -> None:
        """T6: only an explicit typed user request generates a report."""

        with self.subTest(case="request_requires_explicit_flag"):
            with self.assertRaises(ValidationError):
                TelemetryReportRequest.model_validate(
                    {"receipt_refs": (_RECEIPT,), "explicit_user_request": False}
                )

        with self.subTest(case="foreign_request_object_blocked"):
            source = _FakeEvidenceSource({_RECEIPT: (_evidence(),)})
            report = generate_telemetry_report(
                cast(TelemetryReportRequest, object()), source
            )
            self.assertIs(report.status, TelemetryReportStatus.BLOCKED)
            self.assertIs(report.failure, TelemetryReportFailure.REQUEST_INVALID)
            self.assertEqual(source.resolved, [])

        with self.subTest(case="source_untouched_without_request"):
            source = _FakeEvidenceSource({_RECEIPT: (_evidence(),)})
            self.assertEqual(source.resolved, [])

    def test_report_result_shape_is_exact(self) -> None:
        """A generated report has no failure; a blocked report has no groups."""

        protocol_source: ReceiptUsageEvidenceSource = _FakeEvidenceSource(
            {_RECEIPT: (_evidence(),)}
        )
        report = generate_telemetry_report(_request(), protocol_source)
        self.assertIs(type(report), TelemetryReport)
        self.assertIsNone(report.failure)
        with self.assertRaises(ValidationError):
            TelemetryReport(
                status=TelemetryReportStatus.GENERATED,
                failure=TelemetryReportFailure.RECEIPT_NOT_FOUND,
                groups=(),
            )
        with self.assertRaises(ValidationError):
            TelemetryReport(
                status=TelemetryReportStatus.BLOCKED,
                failure=None,
                groups=(),
            )


if __name__ == "__main__":
    unittest.main()
