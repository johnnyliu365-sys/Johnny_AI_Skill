"""Behaviour tests for local payment contracts and append-only subscription ledger."""

from __future__ import annotations

from typing import cast
import unittest

from library.金流串接.python.payment_contracts import (
    CurrencyCode,
    EntitlementId,
    IdempotencyKey,
    Money,
    PaymentIntent,
    PaymentIntentId,
    PaymentStatus,
)
from library.金流串接.python.subscription_ledger import (
    EntitlementStatus,
    LedgerAccepted,
    LedgerEventKind,
    LedgerRejected,
    LedgerRejectionReason,
    SubscriptionLedger,
)


class PaymentContractsAndLedgerTests(unittest.TestCase):
    """Keep payment facts typed, idempotent and append-only without a provider."""

    def test_confirmation_grants_exactly_one_entitlement_for_one_key(self) -> None:
        pending_intent = payment_intent(intent_suffix="001", key_suffix="001")
        empty_ledger = SubscriptionLedger.empty()

        first_result = empty_ledger.confirm_payment(pending_intent)
        self.assertIsInstance(first_result, LedgerAccepted)
        assert isinstance(first_result, LedgerAccepted)
        assert first_result.payment_intent is not None
        duplicate_result = first_result.ledger.confirm_payment(pending_intent)

        self.assertEqual(PaymentStatus.CONFIRMED, first_result.payment_intent.status)
        self.assertIsNotNone(first_result.entitlement)
        assert first_result.entitlement is not None
        self.assertEqual(EntitlementStatus.ACTIVE, first_result.entitlement.status)
        self.assertEqual(
            (LedgerEventKind.PAYMENT_CONFIRMED, LedgerEventKind.SUBSCRIPTION_GRANTED),
            tuple(event.kind for event in first_result.ledger.events),
        )
        self.assertIsInstance(duplicate_result, LedgerRejected)
        assert isinstance(duplicate_result, LedgerRejected)
        self.assertEqual(
            LedgerRejectionReason.DUPLICATE_IDEMPOTENCY_KEY,
            duplicate_result.reason,
        )
        self.assertEqual(2, len(duplicate_result.ledger.events))

    def test_rejects_negative_float_and_unknown_currency_amounts(self) -> None:
        float_amount: object = 12.5
        unknown_currency: object = "BTC"

        with self.assertRaises(ValueError):
            Money(minor_units=-1, currency=CurrencyCode.TWD)
        with self.assertRaises(TypeError):
            Money(minor_units=cast(int, float_amount), currency=CurrencyCode.TWD)
        with self.assertRaises(TypeError):
            Money(minor_units=100, currency=cast(CurrencyCode, unknown_currency))

    def test_rejects_invalid_state_transition_and_duplicate_refund(self) -> None:
        pending_intent = payment_intent(intent_suffix="002", key_suffix="002")
        empty_ledger = SubscriptionLedger.empty()

        invalid_refund = empty_ledger.refund_payment(pending_intent)
        self.assertIsInstance(invalid_refund, LedgerRejected)
        assert isinstance(invalid_refund, LedgerRejected)
        self.assertEqual(
            LedgerRejectionReason.INVALID_STATUS_TRANSITION,
            invalid_refund.reason,
        )

        confirmation = empty_ledger.confirm_payment(pending_intent)
        self.assertIsInstance(confirmation, LedgerAccepted)
        assert isinstance(confirmation, LedgerAccepted)
        assert confirmation.payment_intent is not None
        stale_cancellation = confirmation.ledger.cancel_payment(pending_intent)
        refund = confirmation.ledger.refund_payment(confirmation.payment_intent)
        self.assertIsInstance(refund, LedgerAccepted)
        assert isinstance(refund, LedgerAccepted)
        assert refund.payment_intent is not None
        duplicate_refund = refund.ledger.refund_payment(confirmation.payment_intent)

        self.assertIsInstance(stale_cancellation, LedgerRejected)
        assert isinstance(stale_cancellation, LedgerRejected)
        self.assertEqual(
            LedgerRejectionReason.DUPLICATE_IDEMPOTENCY_KEY,
            stale_cancellation.reason,
        )
        self.assertEqual(PaymentStatus.REFUNDED, refund.payment_intent.status)
        self.assertIsInstance(duplicate_refund, LedgerRejected)
        assert isinstance(duplicate_refund, LedgerRejected)
        self.assertEqual(LedgerRejectionReason.DUPLICATE_REFUND, duplicate_refund.reason)

    def test_cancel_refund_and_expiry_are_distinct_append_only_events(self) -> None:
        cancellation = SubscriptionLedger.empty().cancel_payment(
            payment_intent(intent_suffix="003", key_suffix="003")
        )
        self.assertIsInstance(cancellation, LedgerAccepted)
        assert isinstance(cancellation, LedgerAccepted)

        confirmation = SubscriptionLedger.empty().confirm_payment(
            payment_intent(intent_suffix="004", key_suffix="004")
        )
        self.assertIsInstance(confirmation, LedgerAccepted)
        assert isinstance(confirmation, LedgerAccepted)
        assert confirmation.payment_intent is not None
        refund = confirmation.ledger.refund_payment(confirmation.payment_intent)
        self.assertIsInstance(refund, LedgerAccepted)
        assert isinstance(refund, LedgerAccepted)

        expiry_confirmation = SubscriptionLedger.empty().confirm_payment(
            payment_intent(intent_suffix="005", key_suffix="005")
        )
        self.assertIsInstance(expiry_confirmation, LedgerAccepted)
        assert isinstance(expiry_confirmation, LedgerAccepted)
        assert expiry_confirmation.entitlement is not None
        expiry = expiry_confirmation.ledger.expire_entitlement(
            expiry_confirmation.entitlement
        )
        self.assertIsInstance(expiry, LedgerAccepted)
        assert isinstance(expiry, LedgerAccepted)

        self.assertEqual(
            (LedgerEventKind.PAYMENT_CANCELLED,),
            tuple(event.kind for event in cancellation.ledger.events),
        )
        self.assertEqual(
            (
                LedgerEventKind.PAYMENT_CONFIRMED,
                LedgerEventKind.SUBSCRIPTION_GRANTED,
                LedgerEventKind.PAYMENT_REFUNDED,
            ),
            tuple(event.kind for event in refund.ledger.events),
        )
        self.assertEqual(
            (
                LedgerEventKind.PAYMENT_CONFIRMED,
                LedgerEventKind.SUBSCRIPTION_GRANTED,
                LedgerEventKind.SUBSCRIPTION_EXPIRED,
            ),
            tuple(event.kind for event in expiry.ledger.events),
        )
        self.assertIsNotNone(expiry.entitlement)
        assert expiry.entitlement is not None
        self.assertEqual(EntitlementStatus.EXPIRED, expiry.entitlement.status)


def payment_intent(intent_suffix: str, key_suffix: str) -> PaymentIntent:
    """Build a typed pending intent without exposing raw payment data."""
    return PaymentIntent(
        intent_id=PaymentIntentId(value=f"intent-{intent_suffix}"),
        idempotency_key=IdempotencyKey(value=f"key-{key_suffix}"),
        amount=Money(minor_units=1_990, currency=CurrencyCode.TWD),
        entitlement_id=EntitlementId(value=f"entitlement-{intent_suffix}"),
        status=PaymentStatus.PENDING,
    )


if __name__ == "__main__":
    unittest.main()
