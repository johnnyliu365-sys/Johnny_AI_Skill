"""Executable lexical path and selector checks for controlled dispatch."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Callable
import unittest

from library.workflow_router.controlled_dispatch import (
    ExactPathSelector,
    RelativePath,
    TreePathSelector,
    WireErrorCode,
    WireValidationError,
    matches_path,
)


class _StringSubclass(str):
    pass


def _construct(constructor: Callable[..., object], value: object) -> object:
    return constructor(value)


def _invoke(function: Callable[..., object], first: object, second: object) -> object:
    return function(first, second)


class PathConstructorTests(unittest.TestCase):
    def assert_code(self, constructor: Callable[..., object], value: object, code: WireErrorCode) -> None:
        with self.assertRaises(WireValidationError) as raised:
            _construct(constructor, value)
        self.assertIs(raised.exception.code, code)

    def test_unicode_and_byte_endpoints_preserve_code_points(self) -> None:
        unicode_path = RelativePath("資料/é.txt")
        self.assertEqual(unicode_path.value, "資料/é.txt")
        self.assertEqual(len(RelativePath("é" * 512).value.encode("utf-8")), 1024)
        self.assert_code(RelativePath, "é" * 513, WireErrorCode.INVALID_PATH)

    def test_traversal_drive_unc_and_forbidden_code_points_refuse(self) -> None:
        invalid = (
            "",
            "/root",
            "root/",
            "root//child",
            ".",
            "root/./child",
            "root/../child",
            "C:/root",
            "\\\\server\\share",
            "root\\child",
            "root:name",
            "root\x00name",
            "root/\u200bname",
            "root/\nname",
            "\ud800",
        )
        for value in invalid:
            with self.subTest(value=repr(value)):
                self.assert_code(RelativePath, value, WireErrorCode.INVALID_PATH)

    def test_selectors_are_distinct_and_segment_aware(self) -> None:
        sql = RelativePath("sql")
        sql_file = RelativePath("sql/a")
        sibling = RelativePath("sql2/a")
        exact = ExactPathSelector(sql_file)
        tree = TreePathSelector(sql)
        self.assertTrue(matches_path(exact, sql_file))
        self.assertFalse(matches_path(exact, sql))
        self.assertTrue(matches_path(tree, sql_file))
        self.assertFalse(matches_path(tree, sql))
        self.assertFalse(matches_path(tree, sibling))
        self.assertIsNot(type(exact), type(tree))

    def test_path_and_selector_constructor_boundaries_and_immutability(self) -> None:
        self.assert_code(RelativePath, 7, WireErrorCode.TYPE_MISMATCH)
        self.assert_code(RelativePath, _StringSubclass("sql/a"), WireErrorCode.TYPE_MISMATCH)
        path = RelativePath("sql/a")
        exact = ExactPathSelector(path)
        tree = TreePathSelector(RelativePath("sql"))
        self.assertIs(exact.path, path)
        self.assertEqual(tree.prefix.value, "sql")
        frozen_values: tuple[tuple[object, str, object], ...] = (
            (path, "value", "sql/b"),
            (exact, "path", RelativePath("sql/b")),
            (tree, "prefix", RelativePath("other")),
        )
        for value, field, replacement in frozen_values:
            with self.subTest(field=field):
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, field, replacement)

    def test_selector_and_matching_type_boundaries_refuse_wrong_values(self) -> None:
        self.assert_code(ExactPathSelector, "sql/a", WireErrorCode.TYPE_MISMATCH)
        self.assert_code(TreePathSelector, "sql", WireErrorCode.TYPE_MISMATCH)
        with self.assertRaises(WireValidationError) as raised:
            _invoke(matches_path, ExactPathSelector(RelativePath("sql")), "sql")
        self.assertIs(raised.exception.code, WireErrorCode.TYPE_MISMATCH)
