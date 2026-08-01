"""Behaviour tests for the reusable NLP text contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from library.NLP.python.text_contracts import (
    ExtractedTextField,
    FieldExtractionResult,
    NormalizationAccepted,
    NormalizationRejected,
    RejectionReason,
    TextClassificationResult,
    TextFieldName,
    TextInput,
    TextInputOrigin,
    TextLabel,
    normalize_text,
)


class TextContractTests(unittest.TestCase):
    """Keep external text at a typed, fail-closed boundary."""

    def test_normalizes_chinese_and_ascii_text_stably(self) -> None:
        text_input = TextInput(
            raw_text="  預約   Taxi  123  ",
            origin=TextInputOrigin.LOCAL_VALIDATED,
        )

        first_result = normalize_text(text_input)
        self.assertIsInstance(first_result, NormalizationAccepted)
        assert isinstance(first_result, NormalizationAccepted)

        second_result = normalize_text(
            TextInput(
                raw_text=first_result.normalized_text.value,
                origin=TextInputOrigin.LOCAL_VALIDATED,
            )
        )
        self.assertIsInstance(second_result, NormalizationAccepted)
        assert isinstance(second_result, NormalizationAccepted)
        self.assertEqual("預約 Taxi 123", first_result.normalized_text.value)
        self.assertEqual(first_result.normalized_text, second_result.normalized_text)

    def test_rejects_blank_control_too_long_and_unvalidated_external_input(self) -> None:
        cases = (
            (
                TextInput(raw_text="   ", origin=TextInputOrigin.LOCAL_VALIDATED),
                RejectionReason.BLANK,
            ),
            (
                TextInput(raw_text="hello\u0000world", origin=TextInputOrigin.LOCAL_VALIDATED),
                RejectionReason.CONTROL_CHARACTER,
            ),
            (
                TextInput(raw_text="x" * 2_001, origin=TextInputOrigin.LOCAL_VALIDATED),
                RejectionReason.TOO_LONG,
            ),
            (
                TextInput(raw_text="外部訊息", origin=TextInputOrigin.EXTERNAL_UNVALIDATED),
                RejectionReason.UNVALIDATED_ORIGIN,
            ),
        )

        for text_input, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                result = normalize_text(text_input)
                self.assertIsInstance(result, NormalizationRejected)
                assert isinstance(result, NormalizationRejected)
                self.assertEqual(expected_reason, result.reason)

    def test_classification_and_extraction_use_named_immutable_dtos(self) -> None:
        normalized_result = normalize_text(
            TextInput(raw_text="安排接送", origin=TextInputOrigin.LOCAL_VALIDATED)
        )
        self.assertIsInstance(normalized_result, NormalizationAccepted)
        assert isinstance(normalized_result, NormalizationAccepted)

        classification = TextClassificationResult(
            label=TextLabel(value="ride_request"),
            normalized_text=normalized_result.normalized_text,
        )
        extracted_field = ExtractedTextField(
            name=TextFieldName(value="pickup_note"),
            value=normalized_result.normalized_text,
        )
        extraction = FieldExtractionResult(
            normalized_text=normalized_result.normalized_text,
            fields=(extracted_field,),
        )

        self.assertEqual("ride_request", classification.label.value)
        self.assertEqual("pickup_note", extraction.fields[0].name.value)
        with self.assertRaises(FrozenInstanceError):
            setattr(classification, "label", TextLabel(value="mutated"))


if __name__ == "__main__":
    unittest.main()
