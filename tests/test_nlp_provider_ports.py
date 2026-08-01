"""Behaviour tests for the provider-free NLP analysis port boundary."""

from __future__ import annotations

import unittest

from library.NLP.python.provider_ports import (
    ConfidenceBasisPoints,
    FakeAnalysisProvider,
    FakeProviderScenario,
    ProviderFailure,
    ProviderFailureKind,
    ProviderPayloadValidator,
    ProviderRequestId,
    ProviderRetryability,
    ProviderSuccess,
    TextAnalysisRequest,
)
from library.NLP.python.text_contracts import (
    NormalizationAccepted,
    NormalizedText,
    TextInput,
    TextInputOrigin,
    TextLabel,
    normalize_text,
)


class ProviderPortTests(unittest.TestCase):
    """Ensure fake provider outcomes remain strongly typed and fail closed."""

    def setUp(self) -> None:
        self.request: TextAnalysisRequest = TextAnalysisRequest(
            request_id=ProviderRequestId(value="request-001"),
            input_text=normalized_text("安排接送"),
            allowed_labels=(
                TextLabel(value="ride_request"),
                TextLabel(value="other"),
            ),
        )

    def test_fake_provider_returns_a_validated_success_dto(self) -> None:
        provider = FakeAnalysisProvider(
            scenario=FakeProviderScenario.SUCCESS,
            success_label=TextLabel(value="ride_request"),
            success_confidence=ConfidenceBasisPoints(value=9_300),
        )

        result = provider.analyze(self.request)

        self.assertIsInstance(result, ProviderSuccess)
        assert isinstance(result, ProviderSuccess)
        self.assertEqual("ride_request", result.output.classification.label.value)
        self.assertEqual(9_300, result.output.confidence.value)
        self.assertEqual(self.request.input_text, result.output.classification.normalized_text)

    def test_fake_provider_classifies_external_failures_explicitly(self) -> None:
        cases: tuple[
            tuple[FakeProviderScenario, ProviderFailureKind, ProviderRetryability], ...
        ] = (
            (
                FakeProviderScenario.TRANSIENT_FAILURE,
                ProviderFailureKind.TRANSIENT,
                ProviderRetryability.RETRYABLE,
            ),
            (
                FakeProviderScenario.PERMANENT_FAILURE,
                ProviderFailureKind.PERMANENT,
                ProviderRetryability.NOT_RETRYABLE,
            ),
            (
                FakeProviderScenario.TIMEOUT,
                ProviderFailureKind.TIMEOUT,
                ProviderRetryability.RETRYABLE,
            ),
            (
                FakeProviderScenario.AUTH_FAILURE,
                ProviderFailureKind.AUTHENTICATION,
                ProviderRetryability.NOT_RETRYABLE,
            ),
            (
                FakeProviderScenario.RATE_LIMIT,
                ProviderFailureKind.RATE_LIMIT,
                ProviderRetryability.RETRYABLE,
            ),
        )

        for scenario, expected_kind, expected_retryability in cases:
            with self.subTest(scenario=scenario):
                result = FakeAnalysisProvider(scenario=scenario).analyze(self.request)
                self.assertIsInstance(result, ProviderFailure)
                assert isinstance(result, ProviderFailure)
                self.assertEqual(expected_kind, result.kind)
                self.assertEqual(expected_retryability, result.retryability)
                self.assertEqual(self.request.request_id, result.request_id)

    def test_validator_accepts_only_known_complete_structure(self) -> None:
        raw_payload: object = {
            "label": "ride_request",
            "confidence_basis_points": 8_750,
        }

        result = ProviderPayloadValidator().validate(raw_payload, self.request)

        self.assertIsInstance(result, ProviderSuccess)
        assert isinstance(result, ProviderSuccess)
        self.assertEqual("ride_request", result.output.classification.label.value)
        self.assertEqual(8_750, result.output.confidence.value)

    def test_validator_rejects_unknown_or_invalid_dynamic_payloads(self) -> None:
        invalid_payloads: tuple[object, ...] = (
            object(),
            {"label": "ride_request"},
            {"label": "unknown_label", "confidence_basis_points": 8_000},
            {"label": "ride_request", "confidence_basis_points": True},
            {
                "label": "ride_request",
                "confidence_basis_points": 8_000,
                "unexpected": "value",
            },
        )

        for raw_payload in invalid_payloads:
            with self.subTest(raw_payload_type=type(raw_payload).__name__):
                result = ProviderPayloadValidator().validate(raw_payload, self.request)
                self.assertIsInstance(result, ProviderFailure)
                assert isinstance(result, ProviderFailure)
                self.assertEqual(ProviderFailureKind.INVALID_STRUCTURE, result.kind)
                self.assertEqual(ProviderRetryability.NOT_RETRYABLE, result.retryability)


def normalized_text(value: str) -> NormalizedText:
    """Create test text through the existing typed validation boundary."""
    normalization_result = normalize_text(
        TextInput(raw_text=value, origin=TextInputOrigin.LOCAL_VALIDATED)
    )
    assert isinstance(normalization_result, NormalizationAccepted)
    return normalization_result.normalized_text


if __name__ == "__main__":
    unittest.main()
