"""Typed test-exemption change-class tests (CHG-20260818-029)."""

from __future__ import annotations

import unittest
from typing import cast

from library.workflow_router.contracts import (
    TEST_EXEMPT_CHANGE_CLASSES,
    ChangeClass,
    is_test_exempt,
)


class ChangeClassExemptionTests(unittest.TestCase):
    """Exemption is a closed typed set; everything else fails toward tests."""

    def test_production_behavior_always_requires_tests(self) -> None:
        self.assertFalse(is_test_exempt(ChangeClass.PRODUCTION_BEHAVIOR))
        self.assertNotIn(ChangeClass.PRODUCTION_BEHAVIOR, TEST_EXEMPT_CHANGE_CLASSES)

    def test_each_exempt_class_is_exact(self) -> None:
        for change_class in (
            ChangeClass.DOCS_ONLY,
            ChangeClass.COMMENT_ONLY,
            ChangeClass.SCHEMA_VALIDATED_CONFIG,
            ChangeClass.TYPE_CHECKED_RENAME,
        ):
            with self.subTest(change_class=change_class.value):
                self.assertTrue(is_test_exempt(change_class))
        self.assertEqual(len(TEST_EXEMPT_CHANGE_CLASSES), 4)

    def test_foreign_values_fail_toward_tests(self) -> None:
        for forged in ("docs_only", "vibes", None, 1):
            with self.subTest(forged=repr(forged)):
                self.assertFalse(is_test_exempt(cast(ChangeClass, forged)))


if __name__ == "__main__":
    unittest.main()
