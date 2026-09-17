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

    def test_f1_hard_coded_endpoint_pairs_are_discriminating(self) -> None:
        node_4096 = CanonicalObject(
            (
                CanonicalMember(
                    "items",
                    CanonicalArray(
                        (
                            CanonicalArray(tuple(CanonicalNull() for _ in range(28))),
                            *(CanonicalArray(tuple(CanonicalNull() for _ in range(15))) for _ in range(254)),
                        )
                    ),
                ),
            )
        )
        node_4097 = CanonicalObject(
            (
                CanonicalMember(
                    "items",
                    CanonicalArray(
                        (
                            CanonicalArray(tuple(CanonicalNull() for _ in range(29))),
                            *(CanonicalArray(tuple(CanonicalNull() for _ in range(15))) for _ in range(254)),
                        )
                    ),
                ),
            )
        )
        self.assertIsInstance(canonical_json_bytes(node_4096), bytes)
        with self.assertRaises(WireValidationError) as node_error:
            canonical_json_bytes(node_4097)
        self.assertIs(node_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        output_65536 = CanonicalObject(
            tuple(
                CanonicalMember(
                    f"a{index}", CanonicalString("x" * (4096 if index < 15 else 3961))
                )
                for index in range(16)
            )
        )
        output_65537 = CanonicalObject(
            tuple(
                CanonicalMember(
                    f"a{index}", CanonicalString("x" * (4096 if index < 15 else 3962))
                )
                for index in range(16)
            )
        )
        self.assertEqual(len(canonical_json_bytes(output_65536)), 65_536)
        with self.assertRaises(WireValidationError) as output_error:
            canonical_json_bytes(output_65537)
        self.assertIs(output_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        array_256 = CanonicalArray(tuple(CanonicalNull() for _ in range(256)))
        self.assertEqual(len(array_256.items), 256)
        with self.assertRaises(WireValidationError) as array_error:
            CanonicalArray(tuple(CanonicalNull() for _ in range(257)))
        self.assertIs(array_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        object_256 = CanonicalObject(
            tuple(CanonicalMember(f"k{index}", CanonicalNull()) for index in range(256))
        )
        self.assertEqual(len(object_256.members), 256)
        with self.assertRaises(WireValidationError) as object_error:
            CanonicalObject(
                tuple(CanonicalMember(f"k{index}", CanonicalNull()) for index in range(257))
            )
        self.assertIs(object_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

        self.assertEqual(len(CanonicalString("é" * 2048).value.encode("utf-8")), 4_096)
        with self.assertRaises(WireValidationError) as string_error:
            CanonicalString("é" * 2048 + "x")
        self.assertIs(string_error.exception.code, WireErrorCode.LIMIT_EXCEEDED)

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

    def test_f2_each_self_field_is_omitted_only_at_its_top_level(self) -> None:
        nested = CanonicalObject(
            (
                CanonicalMember("dispatch_digest", CanonicalString("nested-dispatch")),
                CanonicalMember("report_digest", CanonicalString("nested-report")),
            )
        )
        packet = CanonicalObject(
            (
                CanonicalMember("report_digest", CanonicalString("top-report")),
                CanonicalMember("nested", nested),
                CanonicalMember("dispatch_digest", CanonicalString("top-dispatch")),
            )
        )
        dispatch_body = b'{"nested":{"dispatch_digest":"nested-dispatch","report_digest":"nested-report"},"report_digest":"top-report"}'
        report_body = b'{"dispatch_digest":"top-dispatch","nested":{"dispatch_digest":"nested-dispatch","report_digest":"nested-report"}}'
        expected_dispatch = hashlib.sha256(b"johnny.cve.dispatch.v1\x00" + dispatch_body).hexdigest()
        expected_report = hashlib.sha256(b"johnny.cve.report.v1\x00" + report_body).hexdigest()
        self.assertEqual(dispatch_digest(packet).value, expected_dispatch)
        self.assertEqual(report_digest(packet).value, expected_report)

        reversed_packet = CanonicalObject(tuple(reversed(packet.members)))
        self.assertEqual(dispatch_digest(packet), dispatch_digest(reversed_packet))
        self.assertEqual(report_digest(packet), report_digest(reversed_packet))

        changed = CanonicalObject(
            (
                CanonicalMember("report_digest", CanonicalString("top-report")),
                CanonicalMember(
                    "nested",
                    CanonicalObject(
                        (
                            CanonicalMember("dispatch_digest", CanonicalString("nested-dispatch")),
                            CanonicalMember("report_digest", CanonicalString("changed")),
                        )
                    ),
                ),
                CanonicalMember("dispatch_digest", CanonicalString("top-dispatch")),
            )
        )
        self.assertNotEqual(dispatch_digest(packet), dispatch_digest(changed))
        self.assertNotEqual(report_digest(packet), report_digest(changed))

        for key in ("raw_sha256", "source_blob_digest"):
            top_level_forbidden = CanonicalObject((CanonicalMember(key, CanonicalString("raw")),))
            for digest_function in (dispatch_digest, report_digest):
                with self.subTest(key=key, digest_function=digest_function.__name__):
                    with self.assertRaises(WireValidationError) as forbidden_error:
                        digest_function(top_level_forbidden)
                    self.assertIs(forbidden_error.exception.code, WireErrorCode.INVALID_KEY)

        nested_raw = CanonicalObject(
            (
                CanonicalMember(
                    "nested",
                    CanonicalObject(
                        (
                            CanonicalMember("raw_sha256", CanonicalString("nested-raw")),
                            CanonicalMember("source_blob_digest", CanonicalString("nested-source")),
                        )
                    ),
                ),
            )
        )
        nested_raw_body = b'{"nested":{"raw_sha256":"nested-raw","source_blob_digest":"nested-source"}}'
        self.assertEqual(
            dispatch_digest(nested_raw).value,
            hashlib.sha256(b"johnny.cve.dispatch.v1\x00" + nested_raw_body).hexdigest(),
        )
        self.assertEqual(
            report_digest(nested_raw).value,
            hashlib.sha256(b"johnny.cve.report.v1\x00" + nested_raw_body).hexdigest(),
        )

    def test_raw_input_limit_and_frozen_values(self) -> None:
        self.assert_code(raw_blob_digest, b"x" * 65_537, WireErrorCode.LIMIT_EXCEEDED)
        with self.assertRaises(WireValidationError) as wrong:
            _invoke(raw_blob_digest, bytearray(b"x"))
        self.assertIs(wrong.exception.code, WireErrorCode.TYPE_MISMATCH)
