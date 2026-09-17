"""Executable constructor and grammar checks for controlled-dispatch scalars."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Callable
import unittest

from library.workflow_router.controlled_dispatch import (
    Digest,
    ExternalId,
    GitAlgorithm,
    GitObjectId,
    InternalId,
    WireErrorCode,
    WireValidationError,
)


class _StringSubclass(str):
    pass


def _construct(constructor: Callable[..., object], value: object) -> object:
    """Typed object boundary used only for malformed-input rejection cells."""

    return constructor(value)


def _construct_pair(constructor: Callable[..., object], first: object, second: object) -> object:
    return constructor(first, second)


class ScalarConstructorTests(unittest.TestCase):
    def assert_code(self, constructor: Callable[..., object], value: object, code: WireErrorCode) -> None:
        with self.assertRaises(WireValidationError) as raised:
            _construct(constructor, value)
        self.assertIs(raised.exception.code, code)

    def test_valid_ordinary_constructors_preserve_exact_values(self) -> None:
        external = ExternalId("TICKET_01.A")
        internal = InternalId("ticket-01")
        digest = Digest("a" * 64)
        sha1 = GitObjectId(GitAlgorithm.SHA1, "b" * 40)
        sha256 = GitObjectId(GitAlgorithm.SHA256, "c" * 64)
        self.assertEqual(external.value, "TICKET_01.A")
        self.assertEqual(internal.value, "ticket-01")
        self.assertEqual(digest.value, "a" * 64)
        self.assertEqual(sha1.hex, "b" * 40)
        self.assertEqual(sha256.hex, "c" * 64)

    def test_identifier_endpoints_and_invalid_forms(self) -> None:
        self.assertEqual(ExternalId("A").value, "A")
        self.assertEqual(len(ExternalId("A" + "b" * 127).value), 128)
        self.assert_code(ExternalId, "", WireErrorCode.INVALID_ID)
        self.assertEqual(len(InternalId("a" + "b" * 127).value), 128)
        self.assertEqual(InternalId("abc").value, "abc")
        self.assert_code(InternalId, "", WireErrorCode.INVALID_ID)
        self.assert_code(ExternalId, "A" + "b" * 128, WireErrorCode.INVALID_ID)
        self.assert_code(InternalId, "ab", WireErrorCode.INVALID_ID)
        self.assert_code(InternalId, "a" + "b" * 128, WireErrorCode.INVALID_ID)
        self.assert_code(ExternalId, "1bad", WireErrorCode.INVALID_ID)
        self.assert_code(InternalId, "Ticket-01", WireErrorCode.INVALID_ID)
        self.assert_code(ExternalId, " TICKET", WireErrorCode.INVALID_ID)
        self.assert_code(InternalId, "ticket-01 ", WireErrorCode.INVALID_ID)

    def test_digest_and_git_grammars_are_exact(self) -> None:
        self.assertEqual(Digest("0" * 64).value, "0" * 64)
        self.assert_code(Digest, "", WireErrorCode.INVALID_DIGEST)
        self.assert_code(Digest, "A" * 64, WireErrorCode.INVALID_DIGEST)
        self.assert_code(Digest, "a" * 63, WireErrorCode.INVALID_DIGEST)
        self.assert_code(Digest, "a" * 65, WireErrorCode.INVALID_DIGEST)
        with self.assertRaises(WireValidationError) as sha1_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA1, "a" * 39)
        self.assertIs(sha1_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        self.assertEqual(GitObjectId(GitAlgorithm.SHA1, "a" * 40).hex, "a" * 40)
        with self.assertRaises(WireValidationError) as sha1_empty_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA1, "")
        self.assertIs(sha1_empty_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        with self.assertRaises(WireValidationError) as sha1_long_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA1, "a" * 41)
        self.assertIs(sha1_long_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        with self.assertRaises(WireValidationError) as sha256_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA256, "a" * 63)
        self.assertIs(sha256_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        self.assertEqual(GitObjectId(GitAlgorithm.SHA256, "a" * 64).hex, "a" * 64)
        with self.assertRaises(WireValidationError) as sha256_empty_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA256, "")
        self.assertIs(sha256_empty_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        with self.assertRaises(WireValidationError) as sha256_long_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA256, "a" * 65)
        self.assertIs(sha256_long_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        with self.assertRaises(WireValidationError) as uppercase_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA1, "A" * 40)
        self.assertIs(uppercase_error.exception.code, WireErrorCode.INVALID_GIT_ID)
        with self.assertRaises(WireValidationError) as nonhex_error:
            _construct_pair(GitObjectId, GitAlgorithm.SHA256, "g" * 64)
        self.assertIs(nonhex_error.exception.code, WireErrorCode.INVALID_GIT_ID)

    def test_wrong_primitive_types_and_subclasses_are_rejected(self) -> None:
        for constructor in (ExternalId, InternalId, Digest):
            with self.subTest(constructor=constructor.__name__):
                self.assert_code(constructor, 7, WireErrorCode.TYPE_MISMATCH)
                self.assert_code(constructor, _StringSubclass("valid-looking"), WireErrorCode.TYPE_MISMATCH)
        with self.assertRaises(WireValidationError) as wrong_algorithm:
            _construct_pair(GitObjectId, "sha1", "a" * 40)
        self.assertIs(wrong_algorithm.exception.code, WireErrorCode.TYPE_MISMATCH)
        with self.assertRaises(WireValidationError) as wrong_hex:
            _construct_pair(GitObjectId, GitAlgorithm.SHA1, 7)
        self.assertIs(wrong_hex.exception.code, WireErrorCode.TYPE_MISMATCH)

    def test_frozen_values_and_non_sensitive_errors(self) -> None:
        frozen_values: tuple[tuple[object, str, object], ...] = (
            (ExternalId("TICKET-secret"), "value", "other"),
            (InternalId("ticket-secret"), "value", "other"),
            (Digest("a" * 64), "value", "b" * 64),
            (GitObjectId(GitAlgorithm.SHA1, "c" * 40), "algorithm", GitAlgorithm.SHA256),
            (GitObjectId(GitAlgorithm.SHA1, "c" * 40), "hex", "d" * 40),
        )
        for value, field, replacement in frozen_values:
            with self.subTest(field=field):
                with self.assertRaises(FrozenInstanceError):
                    setattr(value, field, replacement)
        with self.assertRaises(WireValidationError) as raised:
            ExternalId("TICKET-secret!")
        self.assertNotIn("TICKET-secret", str(raised.exception))
