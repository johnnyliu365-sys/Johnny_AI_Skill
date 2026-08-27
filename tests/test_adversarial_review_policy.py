"""Executable policy contracts for reviewer-owned adversarial assurance."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_ADVERSARIAL = _ROOT / "skills" / "johnny-project-takeover" / "references" / "adversarial-review.md"
_CODE_REVIEW = _ROOT / "CodeReview.md"
_REVIEW_CHECKS = _ROOT / "skills" / "johnny-project-takeover" / "references" / "review-checks.md"
_DELIVERY_PROFILE = _ROOT / "skills" / "johnny-project-takeover" / "references" / "delivery-profile.md"
_MODEL_ROLES = _ROOT / "skills" / "johnny-project-takeover" / "references" / "model-role-routing.md"
_PROFILE = _ROOT / "library" / "workflow_router" / "profile.py"
_PROFILE_TEST = _ROOT / "tests" / "test_workflow_router.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_terms(test: unittest.TestCase, document: str, terms: tuple[str, ...]) -> None:
    for term in terms:
        with test.subTest(term=term):
            test.assertIn(term, document)


class AdversarialReviewPolicyTests(unittest.TestCase):
    """TARA1-TARA7 pin the policy and its control-plane boundary."""

    def test_tara1_code_review_indexes_reference_and_retains_reviewer_verdict(self) -> None:
        document = _read(_CODE_REVIEW)
        _assert_terms(
            self,
            document,
            (
                "adversarial-review.md",
                "reviewer alone owns the final review conclusion",
                "reviewer alone owns integration",
            ),
        )

    def test_tara2_audit_is_direct_same_lifetime_and_finite(self) -> None:
        document = _read(_ADVERSARIAL)
        _assert_terms(
            self,
            document,
            (
                "RESEARCH_HELPER",
                "same-lifetime",
                "direct",
                "finite return",
                "FINDINGS",
                "NO_FINDINGS",
                "BLOCKED",
                "UNAVAILABLE",
                "NOT_APPLICABLE",
                "runner",
                "queue",
                "receipt",
                "live descriptor",
                "host readback",
                "NOT_REQUIRED",
            ),
        )

    def test_tara3_requiredness_scales_and_unavailable_required_evidence_blocks(self) -> None:
        adversarial = " ".join(_read(_ADVERSARIAL).split())
        delivery = " ".join(_read(_DELIVERY_PROFILE).split())
        model_roles = " ".join(_read(_MODEL_ROLES).split())

        self.assertIn(
            "The audit is optional for `COMPACT` and `STANDARD` unless an approved ticket matrix requires it.",
            adversarial,
        )
        self.assertIn(
            "It is mandatory for `HIGH_ASSURANCE` and before a proposed release/deployment.",
            adversarial,
        )
        self.assertIn(
            "If a mandatory audit or required isolation/evidence capability is unavailable, the reviewer returns `BLOCKED`;",
            adversarial,
        )
        self.assertIn(
            "| Research helper | Not admitted for ordinary research; exactly one optional reviewer-owned `AdversarialReviewPlan` audit | One optional ordinary read-only helper; a required `AdversarialReviewPlan` consumes one | One optional ordinary read-only helper; the mandatory `AdversarialReviewPlan` audit consumes one |",
            delivery,
        )
        self.assertIn(
            "An ordinary research helper is not admitted for `COMPACT`; `STANDARD` may use one optional ordinary read-only helper.",
            delivery,
        )
        self.assertIn(
            "exactly one optional reviewer-owned `AdversarialReviewPlan` audit may be used at `COMPACT` and `STANDARD` unless the approved ticket matrix makes it required.",
            delivery,
        )
        self.assertIn(
            "It is mandatory for `HIGH_ASSURANCE` and before any proposed release/deployment; that required `AdversarialReviewPlan` consumes one reviewer-owned `RESEARCH_HELPER`.",
            delivery,
        )
        self.assertIn(
            "An ordinary research helper is not admitted for `COMPACT`; `STANDARD` may use one optional ordinary read-only helper.",
            model_roles,
        )
        self.assertIn(
            "A reviewer-owned `AdversarialReviewPlan` may consume exactly one helper at `COMPACT`/`STANDARD` when optional, and must consume one at `HIGH_ASSURANCE` or before a proposed release/deployment;",
            model_roles,
        )

    def test_tara4_attack_and_deployment_vectors_have_finite_evidence_states(self) -> None:
        document = _read(_ADVERSARIAL)
        _assert_terms(
            self,
            document,
            (
                "SPEC_GAP",
                "BOUNDARY_DATA",
                "STATE_TRANSITION",
                "CONCURRENCY",
                "ERROR_PARTIAL_FAILURE",
                "AUTHORIZATION",
                "CONSISTENCY",
                "IDEMPOTENCY",
                "REGRESSION",
                "OBSERVABILITY",
                "DEPLOYMENT_READINESS",
                "SQL migration",
                "production-history compatibility",
                "case/encoding/locale",
                "schema compatibility",
                "old-app/new-DB",
                "new-app/old-DB",
                "rollback compatibility",
                "environment/configuration/secret-alias",
                "permission differences",
                "staging/production drift",
                "DB lock",
                "large-table update/alter",
                "index creation",
                "connection pool",
                "worker/cron/queue/cache",
                "deployment/migration interruption",
                "backup/restore",
                "authorized real-account sampling",
                "`NOT_APPLICABLE` requires evidence",
                "and `NOT_AUTHORIZED` remain visible",
                "NOT_APPLICABLE",
                "NOT_AUTHORIZED",
            ),
        )

    def test_tara5_audit_evidence_never_grants_review_or_external_effect_authority(self) -> None:
        document = _read(_ADVERSARIAL)
        _assert_terms(
            self,
            document,
            (
                "cannot approve",
                "cannot integrate",
                "cannot commit",
                "cannot push",
                "cannot obtain secrets",
                "production data",
                "production account",
                "migration",
                "release",
                "deployment",
                "separate",
                "NOT_AUTHORIZED",
            ),
        )

    def test_tara6_review_checks_distinguishes_lifetimes(self) -> None:
        document = _read(_REVIEW_CHECKS)
        _assert_terms(
            self,
            document,
            (
                "same-lifetime",
                "cross-lifetime",
                "direct",
                "receipt",
                "live descriptor",
                "NOT_REQUIRED",
            ),
        )
        self.assertNotIn(
            "The reviewer positive path must bind one live descriptor and receipt.",
            document,
        )

    def test_tara7_review_checks_digest_is_repeated_at_both_policy_pins(self) -> None:
        normalized = _REVIEW_CHECKS.read_bytes().replace(b"\r\n", b"\n")
        digest = "sha256_" + hashlib.sha256(normalized).hexdigest()
        for path in (_PROFILE, _PROFILE_TEST):
            with self.subTest(path=path):
                document = _read(path)
                self.assertIn('"review-checks"', document)
                self.assertIn(digest, document)


if __name__ == "__main__":
    unittest.main()
