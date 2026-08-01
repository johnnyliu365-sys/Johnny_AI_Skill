"""Behaviour tests for fake payment provider outcomes and reconciliation."""

from __future__ import annotations

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
from library.金流串接.python.provider_ports import (
    FakePaymentProvider,
    FakeProviderScenario,
    ProviderAuthorizationSuccess,
    ProviderEvent,
    ProviderEventId,
    ProviderEventSuccess,
    ProviderFailure,
    ProviderFailureKind,
    ProviderFinalState,
    ProviderTransactionId,
)
from library.金流串接.python.reconciliation import (
    ReconciliationAlreadyProcessed,
    ReconciliationApplied,
    ReconciliationJournal,
    ReconciliationManualReview,
    ReconciliationManualReviewReason,
    reconcile_provider_event,
)
from library.金流串接.python.subscription_ledger import SubscriptionLedger


class PaymentProviderReconciliationTests(unittest.TestCase):
    """Keep provider results fake, replay-safe and fail closed."""

    def test_fake_authorize_confirm_and_refund_reconcile_to_typed_facts(self) -> None:
        pending_intent = payment_intent("001")
        provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-001"),
            scenario=FakeProviderScenario.SUCCESS,
        )

        authorization_result = provider.authorize(pending_intent)
        self.assertIsInstance(authorization_result, ProviderAuthorizationSuccess)
        assert isinstance(authorization_result, ProviderAuthorizationSuccess)
        confirmation_result = provider.confirm(authorization_result.authorization)
        confirmation = reconcile_provider_event(
            provider_result=confirmation_result,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )
        self.assertIsInstance(confirmation, ReconciliationApplied)
        assert isinstance(confirmation, ReconciliationApplied)

        refund_result = provider.refund(authorization_result.authorization)
        refund = reconcile_provider_event(
            provider_result=refund_result,
            payment_intent=confirmation.payment_intent,
            ledger=confirmation.ledger,
            journal=confirmation.journal,
        )
        self.assertIsInstance(refund, ReconciliationApplied)
        assert isinstance(refund, ReconciliationApplied)

        self.assertEqual(PaymentStatus.CONFIRMED, confirmation.payment_intent.status)
        self.assertEqual(PaymentStatus.REFUNDED, refund.payment_intent.status)
        self.assertEqual(3, len(refund.ledger.events))
        self.assertEqual(2, len(refund.journal.records))

    def test_replayed_provider_event_does_not_grant_a_second_entitlement(self) -> None:
        pending_intent = payment_intent("002")
        provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-002"),
            scenario=FakeProviderScenario.SUCCESS,
        )
        authorization_result = provider.authorize(pending_intent)
        self.assertIsInstance(authorization_result, ProviderAuthorizationSuccess)
        assert isinstance(authorization_result, ProviderAuthorizationSuccess)
        confirmation_result = provider.confirm(authorization_result.authorization)
        first_result = reconcile_provider_event(
            provider_result=confirmation_result,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )
        self.assertIsInstance(first_result, ReconciliationApplied)
        assert isinstance(first_result, ReconciliationApplied)
        replay_result = reconcile_provider_event(
            provider_result=confirmation_result,
            payment_intent=pending_intent,
            ledger=first_result.ledger,
            journal=first_result.journal,
        )

        self.assertIsInstance(replay_result, ReconciliationAlreadyProcessed)
        assert isinstance(replay_result, ReconciliationAlreadyProcessed)
        self.assertEqual(2, len(replay_result.ledger.events))
        self.assertEqual(1, len(replay_result.journal.records))

    def test_reconciliation_checks_existing_ledger_when_journal_is_missing(self) -> None:
        pending_intent = payment_intent("ledger-check")
        provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-ledger-check"),
            scenario=FakeProviderScenario.SUCCESS,
        )
        authorization_result = provider.authorize(pending_intent)
        self.assertIsInstance(authorization_result, ProviderAuthorizationSuccess)
        assert isinstance(authorization_result, ProviderAuthorizationSuccess)
        first_event_result = provider.confirm(authorization_result.authorization)
        first_result = reconcile_provider_event(
            provider_result=first_event_result,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )
        self.assertIsInstance(first_result, ReconciliationApplied)
        assert isinstance(first_result, ReconciliationApplied)

        unjournaled_duplicate_event = ProviderEvent(
            event_id=ProviderEventId(value="event-unjournaled-duplicate"),
            transaction_id=authorization_result.authorization.transaction_id,
            payment_intent_id=pending_intent.intent_id,
            idempotency_key=pending_intent.idempotency_key,
            final_state=ProviderFinalState.CONFIRMED,
        )
        result = reconcile_provider_event(
            provider_result=ProviderEventSuccess(event=unjournaled_duplicate_event),
            payment_intent=pending_intent,
            ledger=first_result.ledger,
            journal=ReconciliationJournal.empty(),
        )

        self.assertIsInstance(result, ReconciliationManualReview)
        assert isinstance(result, ReconciliationManualReview)
        self.assertEqual(ReconciliationManualReviewReason.LEDGER_REJECTED, result.reason)
        self.assertEqual(2, len(result.ledger.events))

    def test_timeout_and_unknown_transaction_require_manual_review(self) -> None:
        pending_intent = payment_intent("003")
        timeout_provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-003"),
            scenario=FakeProviderScenario.TIMEOUT,
        )
        unknown_provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-004"),
            scenario=FakeProviderScenario.UNKNOWN_TRANSACTION,
        )
        timeout_authorization = timeout_provider.authorize(pending_intent)
        unknown_authorization = unknown_provider.authorize(pending_intent)

        self.assertIsInstance(timeout_authorization, ProviderFailure)
        assert isinstance(timeout_authorization, ProviderFailure)
        self.assertEqual(ProviderFailureKind.TIMEOUT, timeout_authorization.kind)
        self.assertIsInstance(unknown_authorization, ProviderFailure)
        assert isinstance(unknown_authorization, ProviderFailure)
        self.assertEqual(ProviderFailureKind.UNKNOWN_TRANSACTION, unknown_authorization.kind)

        timeout_review = reconcile_provider_event(
            provider_result=timeout_authorization,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )
        unknown_review = reconcile_provider_event(
            provider_result=unknown_authorization,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )

        self.assertIsInstance(timeout_review, ReconciliationManualReview)
        assert isinstance(timeout_review, ReconciliationManualReview)
        self.assertEqual(
            ReconciliationManualReviewReason.PROVIDER_TIMEOUT,
            timeout_review.reason,
        )
        self.assertIsInstance(unknown_review, ReconciliationManualReview)
        assert isinstance(unknown_review, ReconciliationManualReview)
        self.assertEqual(
            ReconciliationManualReviewReason.UNKNOWN_TRANSACTION,
            unknown_review.reason,
        )

    def test_conflicting_final_state_requires_manual_review(self) -> None:
        pending_intent = payment_intent("005")
        provider = FakePaymentProvider(
            transaction_id=ProviderTransactionId(value="transaction-005"),
            scenario=FakeProviderScenario.SUCCESS,
        )
        authorization_result = provider.authorize(pending_intent)
        self.assertIsInstance(authorization_result, ProviderAuthorizationSuccess)
        assert isinstance(authorization_result, ProviderAuthorizationSuccess)
        confirmation_result = provider.confirm(authorization_result.authorization)
        confirmation = reconcile_provider_event(
            provider_result=confirmation_result,
            payment_intent=pending_intent,
            ledger=SubscriptionLedger.empty(),
            journal=ReconciliationJournal.empty(),
        )
        self.assertIsInstance(confirmation, ReconciliationApplied)
        assert isinstance(confirmation, ReconciliationApplied)
        refund_result = provider.refund(authorization_result.authorization)
        refund = reconcile_provider_event(
            provider_result=refund_result,
            payment_intent=confirmation.payment_intent,
            ledger=confirmation.ledger,
            journal=confirmation.journal,
        )
        self.assertIsInstance(refund, ReconciliationApplied)
        assert isinstance(refund, ReconciliationApplied)

        conflicting_event = ProviderEvent(
            event_id=ProviderEventId(value="event-conflict-005"),
            transaction_id=authorization_result.authorization.transaction_id,
            payment_intent_id=pending_intent.intent_id,
            idempotency_key=pending_intent.idempotency_key,
            final_state=ProviderFinalState.CONFIRMED,
        )
        conflict_result = reconcile_provider_event(
            provider_result=ProviderEventSuccess(event=conflicting_event),
            payment_intent=refund.payment_intent,
            ledger=refund.ledger,
            journal=refund.journal,
        )

        self.assertIsInstance(conflict_result, ReconciliationManualReview)
        assert isinstance(conflict_result, ReconciliationManualReview)
        self.assertEqual(
            ReconciliationManualReviewReason.CONFLICTING_FINAL_STATE,
            conflict_result.reason,
        )
        self.assertEqual(3, len(conflict_result.ledger.events))
        self.assertEqual(2, len(conflict_result.journal.records))


def payment_intent(suffix: str) -> PaymentIntent:
    """Build a strongly typed pending payment intent for local fake scenarios."""
    return PaymentIntent(
        intent_id=PaymentIntentId(value=f"intent-{suffix}"),
        idempotency_key=IdempotencyKey(value=f"key-{suffix}"),
        amount=Money(minor_units=1_990, currency=CurrencyCode.TWD),
        entitlement_id=EntitlementId(value=f"entitlement-{suffix}"),
        status=PaymentStatus.PENDING,
    )


if __name__ == "__main__":
    unittest.main()
