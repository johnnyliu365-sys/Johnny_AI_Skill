"""Behaviour tests for the reusable deterministic field rule parser."""

from __future__ import annotations

import unittest

from library.NLP.python.rule_parser import (
    FieldRule,
    LiteralDelimiter,
    ParseReason,
    ParseStatus,
    RuleSet,
    RuleToken,
    parse_fields,
)
from library.NLP.python.text_contracts import (
    NormalizationAccepted,
    NormalizedText,
    TextFieldName,
    TextInput,
    TextInputOrigin,
    normalize_text,
)


class RuleParserTests(unittest.TestCase):
    """Ensure fixed rules never invent or combine values across frames."""

    def setUp(self) -> None:
        self.rule_set: RuleSet = RuleSet(
            field_rules=(
                FieldRule(
                    field_name=TextFieldName(value="pickup"),
                    token=RuleToken(value="pickup="),
                ),
                FieldRule(
                    field_name=TextFieldName(value="dropoff"),
                    token=RuleToken(value="dropoff="),
                ),
            ),
            field_delimiter=LiteralDelimiter(value=";"),
            frame_delimiter=LiteralDelimiter(value="|"),
        )

    def test_extracts_marked_fields_from_one_complete_frame(self) -> None:
        result = parse_fields(
            normalized_text("pickup=Home;dropoff=Station"), self.rule_set
        )

        self.assertEqual(ParseStatus.COMPLETE, result.status)
        self.assertEqual(ParseReason.COMPLETE_FRAME, result.rationale.reason)
        self.assertIsNotNone(result.extraction)
        assert result.extraction is not None
        self.assertEqual("pickup", result.extraction.fields[0].name.value)
        self.assertEqual("Home", result.extraction.fields[0].value.value)
        self.assertEqual("dropoff", result.extraction.fields[1].name.value)
        self.assertEqual("Station", result.extraction.fields[1].value.value)

    def test_returns_incomplete_when_a_required_field_is_missing(self) -> None:
        result = parse_fields(normalized_text("pickup=Home"), self.rule_set)

        self.assertEqual(ParseStatus.INCOMPLETE, result.status)
        self.assertEqual(ParseReason.MISSING_REQUIRED_FIELD, result.rationale.reason)
        self.assertIsNotNone(result.extraction)
        assert result.extraction is not None
        self.assertEqual(("pickup",), tuple(field.name.value for field in result.extraction.fields))

    def test_returns_ambiguous_when_a_field_is_repeated_in_one_frame(self) -> None:
        result = parse_fields(
            normalized_text("pickup=Home;pickup=Office;dropoff=Station"), self.rule_set
        )

        self.assertEqual(ParseStatus.AMBIGUOUS, result.status)
        self.assertEqual(ParseReason.DUPLICATE_FIELD, result.rationale.reason)
        self.assertIsNone(result.extraction)

    def test_does_not_borrow_values_across_frames(self) -> None:
        result = parse_fields(
            normalized_text("pickup=Home|dropoff=Station"), self.rule_set
        )

        self.assertEqual(ParseStatus.INCOMPLETE, result.status)
        self.assertEqual(ParseReason.SPLIT_ACROSS_FRAMES, result.rationale.reason)
        self.assertIsNone(result.extraction)

    def test_rejects_an_empty_marked_field_value(self) -> None:
        result = parse_fields(normalized_text("pickup=;dropoff=Station"), self.rule_set)

        self.assertEqual(ParseStatus.REJECTED, result.status)
        self.assertEqual(ParseReason.EMPTY_FIELD_VALUE, result.rationale.reason)
        self.assertIsNone(result.extraction)

    def test_returns_ambiguous_when_two_frames_are_complete(self) -> None:
        result = parse_fields(
            normalized_text(
                "pickup=Home;dropoff=Station|pickup=Office;dropoff=Airport"
            ),
            self.rule_set,
        )

        self.assertEqual(ParseStatus.AMBIGUOUS, result.status)
        self.assertEqual(ParseReason.MULTIPLE_COMPLETE_FRAMES, result.rationale.reason)
        self.assertIsNone(result.extraction)

    def test_rejects_unknown_content_and_is_deterministic(self) -> None:
        unknown_result = parse_fields(normalized_text("unstructured request"), self.rule_set)
        first_result = parse_fields(
            normalized_text("pickup=Home;dropoff=Station"), self.rule_set
        )
        second_result = parse_fields(
            normalized_text("pickup=Home;dropoff=Station"), self.rule_set
        )

        self.assertEqual(ParseStatus.REJECTED, unknown_result.status)
        self.assertEqual(ParseReason.NO_RECOGNIZED_FIELD, unknown_result.rationale.reason)
        self.assertEqual(first_result, second_result)


def normalized_text(value: str) -> NormalizedText:
    """Create test input through the public text-validation boundary."""
    normalization_result = normalize_text(
        TextInput(raw_text=value, origin=TextInputOrigin.LOCAL_VALIDATED)
    )
    assert isinstance(normalization_result, NormalizationAccepted)
    return normalization_result.normalized_text


if __name__ == "__main__":
    unittest.main()
