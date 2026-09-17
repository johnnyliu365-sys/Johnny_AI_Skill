"""Canonical-value, bounded-encoding and digest vectors."""

from __future__ import annotations

from typing import Callable
import hashlib
import unittest

from library.workflow_router.controlled_dispatch import (
    CanonicalArray,
    CanonicalBool,
    CanonicalInteger,
    CanonicalMember,
    CanonicalNull,
    CanonicalObject,
    CanonicalString,
    WireErrorCode,
    WireValidationError,
    canonical_json_bytes,
    dispatch_digest,
    raw_blob_digest,
    report_digest,
)


def _construct(constructor: Callable[..., object], value: object) -> object:
    return constructor(value)


def _construct_pair(constructor: Callable[..., object], first: object, second: object) -> object:
    return constructor(first, second)


def _invoke(function: Callable[..., object], value: object) -> object:
    return function(value)


class CanonicalTests(unittest.TestCase):
    def assert_code(self, constructor: Callable[..., object], value: object, code: WireErrorCode) -> None:
        with self.assertRaises(WireValidationError) as raised:
            _construct(constructor, value)
        self.assertIs(raised.exception.code, code)

    def test_all_ordinary_value_constructors_and_tuple_membership(self) -> None:
        null = CanonicalNull()
        boolean = CanonicalBool(True)
        integer = CanonicalInteger(2_147_483_647)
        string = CanonicalString("é")
        array = CanonicalArray((null, boolean, integer, string))
        member = CanonicalMember("payload", array)
        obj = CanonicalObject((member,))
        self.assertEqual(obj.members[0].value, array)
        self.assertEqual(array.items[2], integer)
        self.assertIsInstance(array.items, tuple)

    def test_scalar_and_collection_rejection_cells(self) -> None:
        self.assert_code(CanonicalBool, 1, WireErrorCode.TYPE_MISMATCH)
        self.assert_code(CanonicalInteger, True, WireErrorCode.TYPE_MISMATCH)
        self.assert_code(CanonicalInteger, -1, WireErrorCode.OUT_OF_RANGE)
        self.assert_code(CanonicalInteger, 2_147_483_648, WireErrorCode.OUT_OF_RANGE)
        self.assert_code(CanonicalString, "\x00", WireErrorCode.INVALID_TEXT)
        self.assert_code(CanonicalString, "é" * 2049, WireErrorCode.LIMIT_EXCEEDED)
        self.assert_code(CanonicalArray, [CanonicalNull()], WireErrorCode.TYPE_MISMATCH)
        self.assert_code(CanonicalArray, (None,), WireErrorCode.TYPE_MISMATCH)
        with self.assertRaises(WireValidationError) as member_shape:
            _construct_pair(CanonicalMember, 7, CanonicalNull())
        self.assertIs(member_shape.exception.code, WireErrorCode.TYPE_MISMATCH)
        with self.assertRaises(WireValidationError) as member_key:
            _construct_pair(CanonicalMember, "Bad", CanonicalNull())
        self.assertIs(member_key.exception.code, WireErrorCode.INVALID_KEY)
        self.assert_code(CanonicalObject, [CanonicalMember("a", CanonicalNull())], WireErrorCode.TYPE_MISMATCH)

    def test_object_members_are_unique_and_bounded(self) -> None:
        duplicate = (CanonicalMember("a", CanonicalNull()), CanonicalMember("a", CanonicalNull()))
        self.assert_code(CanonicalObject, duplicate, WireErrorCode.DUPLICATE_KEY)
        too_many = tuple(CanonicalMember(f"a{index}", CanonicalNull()) for index in range(257))
        self.assert_code(CanonicalObject, too_many, WireErrorCode.LIMIT_EXCEEDED)
        self.assertEqual(len(CanonicalObject(tuple(too_many[:1])).members), 1)

    def test_fixed_json_vectors_and_array_order(self) -> None:
        empty = CanonicalObject(())
        self.assertEqual(canonical_json_bytes(empty), b"{}")
        value = CanonicalObject(
            (
                CanonicalMember("z", CanonicalArray((CanonicalNull(), CanonicalBool(False), CanonicalInteger(0)))),
                CanonicalMember("a", CanonicalString("é")),
            )
        )
        self.assertEqual(canonical_json_bytes(value), b'{"a":"\\u00e9","z":[null,false,0]}')
        self.assertEqual(
            canonical_json_bytes(
                CanonicalObject((CanonicalMember("nested_key", CanonicalObject((CanonicalMember("a", CanonicalInteger(1)),))),))
            ),
            b'{"nested_key":{"a":1}}',
        )

    def test_depth_nodes_and_output_limits_reject_without_truncation(self) -> None:
        nested = CanonicalObject(())
        for _ in range(15):
            nested = CanonicalObject((CanonicalMember("child", nested),))
        self.assertEqual(canonical_json_bytes(nested)[:1], b"{")
        too_deep = CanonicalObject((CanonicalMember("child", nested),))
        with self.assertRaises(WireValidationError) as raised:
            canonical_json_bytes(too_deep)
        self.assertIs(raised.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        inner = CanonicalArray(tuple(CanonicalNull() for _ in range(16)))
        node_heavy = CanonicalObject((CanonicalMember("items", CanonicalArray(tuple(inner for _ in range(256)))),))
        with self.assertRaises(WireValidationError) as node_error:
            canonical_json_bytes(node_heavy)
        self.assertIs(node_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        output_heavy = CanonicalObject(
            tuple(CanonicalMember("k" + str(index), CanonicalString("x" * 4096)) for index in range(17))
        )
        with self.assertRaises(WireValidationError) as output_error:
            canonical_json_bytes(output_heavy)
        self.assertIs(output_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

    def test_domain_separated_digest_vectors_and_detached_raw_evidence(self) -> None:
        body = CanonicalObject(
            (
                CanonicalMember("b", CanonicalInteger(2)),
                CanonicalMember("a", CanonicalString("text")),
                CanonicalMember("nested", CanonicalObject((CanonicalMember("dispatch_digest", CanonicalString("kept")),))),
                CanonicalMember("dispatch_digest", CanonicalString("omitted")),
            )
        )
        body_bytes = b'{"a":"text","b":2,"nested":{"dispatch_digest":"kept"}}'
        expected_dispatch = hashlib.sha256(b"johnny.cve.dispatch.v1\x00" + body_bytes).hexdigest()
        expected_report = hashlib.sha256(b"johnny.cve.report.v1\x00" + b'{"a":"text","b":2,"dispatch_digest":"omitted","nested":{"dispatch_digest":"kept"}}').hexdigest()
        self.assertEqual(dispatch_digest(body).value, expected_dispatch)
        self.assertNotEqual(dispatch_digest(body).value, report_digest(body).value)
        self.assertEqual(raw_blob_digest(b"raw").value, hashlib.sha256(b"raw").hexdigest())
        self.assertEqual(raw_blob_digest(b""), raw_blob_digest(b""))
        self.assertEqual(len(raw_blob_digest(b"x" * 65_536).value), 64)
        self.assertEqual(expected_report, report_digest(body).value)
        forbidden = CanonicalObject((CanonicalMember("raw_sha256", CanonicalString("x")),))
        with self.assertRaises(WireValidationError) as forbidden_error:
            dispatch_digest(forbidden)
        self.assertIs(forbidden_error.exception.code, WireErrorCode.INVALID_KEY)

    def test_raw_input_limit_and_frozen_values(self) -> None:
        self.assert_code(raw_blob_digest, b"x" * 65_537, WireErrorCode.LIMIT_EXCEEDED)
        with self.assertRaises(WireValidationError) as wrong:
            _invoke(raw_blob_digest, bytearray(b"x"))
        self.assertIs(wrong.exception.code, WireErrorCode.TYPE_MISMATCH)
