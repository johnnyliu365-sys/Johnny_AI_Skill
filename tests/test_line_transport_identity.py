"""Behaviour tests for local fake message transport and identity resolution."""

from __future__ import annotations

from dataclasses import fields
import unittest

from library.功能集群.python.identity_resolution import (
    DisplayLabel,
    IdentityDirectory,
    IdentityEnrollmentAccepted,
    IdentityEnrollmentRejected,
    IdentityEnrollmentRejectionReason,
    IdentityUnknown,
    ResolvedIdentity,
    StableIdentityId,
)
from library.功能集群.python.line_transport import (
    FakeLineTransport,
    FakeTransportScenario,
    MessageContent,
    MessageRequestId,
    MessageScopeId,
    OutboundMessageRequest,
    TransportFailure,
    TransportFailureKind,
    TransportSuccess,
)


class LineTransportIdentityTests(unittest.TestCase):
    """Keep message work explicit, fake-only and identity-safe."""

    def test_fake_transport_succeeds_for_an_explicit_scoped_stable_identity(self) -> None:
        request = local_message_request(suffix="success")
        transport = FakeLineTransport(scenario=FakeTransportScenario.SUCCESS)

        result = transport.send(request)

        self.assertIsInstance(result, TransportSuccess)
        assert isinstance(result, TransportSuccess)
        self.assertEqual(request.request_id, result.request_id)
        self.assertEqual(1, transport.delivery_attempt_count)

    def test_fake_provider_failure_is_classified_without_provider_detail(self) -> None:
        request = local_message_request(suffix="failure")
        transport = FakeLineTransport(scenario=FakeTransportScenario.PROVIDER_FAILURE)

        result = transport.send(request)

        self.assertIsInstance(result, TransportFailure)
        assert isinstance(result, TransportFailure)
        self.assertEqual(TransportFailureKind.PROVIDER_UNAVAILABLE, result.kind)
        self.assertEqual(request.request_id, result.request_id)
        self.assertEqual(1, transport.delivery_attempt_count)
        self.assertEqual(("request_id", "kind"), tuple(field.name for field in fields(result)))

    def test_message_request_has_no_token_or_implicit_identity_authorization(self) -> None:
        field_names = tuple(field.name for field in fields(OutboundMessageRequest))

        self.assertEqual(
            ("request_id", "scope_id", "recipient_identity", "content"),
            field_names,
        )
        self.assertNotIn("token", field_names)
        self.assertNotIn("authorization", field_names)
        self.assertNotIn("display_label", field_names)
        self.assertNotIn("tenant", field_names)

    def test_stable_identity_is_not_overwritten_by_display_label_and_unknown_fails_closed(
        self,
    ) -> None:
        stable_identity = StableIdentityId(value="identity-001")
        directory = IdentityDirectory.empty()
        enrolled = directory.enroll(
            identity_id=stable_identity,
            display_label=DisplayLabel(value="Primary label"),
        )
        self.assertIsInstance(enrolled, IdentityEnrollmentAccepted)
        assert isinstance(enrolled, IdentityEnrollmentAccepted)

        duplicate = enrolled.directory.enroll(
            identity_id=stable_identity,
            display_label=DisplayLabel(value="Replacement label"),
        )
        self.assertIsInstance(duplicate, IdentityEnrollmentRejected)
        assert isinstance(duplicate, IdentityEnrollmentRejected)
        self.assertEqual(
            IdentityEnrollmentRejectionReason.STABLE_ID_ALREADY_REGISTERED,
            duplicate.reason,
        )
        resolved = duplicate.directory.resolve(identity_id=stable_identity)
        self.assertIsInstance(resolved, ResolvedIdentity)
        assert isinstance(resolved, ResolvedIdentity)
        self.assertEqual(stable_identity, resolved.identity_id)
        self.assertEqual("Primary label", resolved.display_label.value)

        fallback_identity = StableIdentityId(value="identity-fallback")
        fallback_enrolled = duplicate.directory.enroll(
            identity_id=fallback_identity,
            display_label=None,
        )
        self.assertIsInstance(fallback_enrolled, IdentityEnrollmentAccepted)
        assert isinstance(fallback_enrolled, IdentityEnrollmentAccepted)
        fallback_resolved = fallback_enrolled.directory.resolve(
            identity_id=fallback_identity
        )
        self.assertIsInstance(fallback_resolved, ResolvedIdentity)
        assert isinstance(fallback_resolved, ResolvedIdentity)
        self.assertEqual("Unknown", fallback_resolved.display_label.value)

        unknown = fallback_enrolled.directory.resolve(
            identity_id=StableIdentityId(value="identity-unknown")
        )
        self.assertIsInstance(unknown, IdentityUnknown)


def local_message_request(suffix: str) -> OutboundMessageRequest:
    """Build an explicit local request with no credentials or implicit authority."""
    return OutboundMessageRequest(
        request_id=MessageRequestId(value=f"request-{suffix}"),
        scope_id=MessageScopeId(value="local-sandbox"),
        recipient_identity=StableIdentityId(value=f"identity-{suffix}"),
        content=MessageContent(value="local test message"),
    )


if __name__ == "__main__":
    unittest.main()
