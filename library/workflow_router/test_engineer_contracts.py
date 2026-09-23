"""Strict contracts for independently resolved test-engineer evidence."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Protocol, Self, TypeAlias

from pydantic import AfterValidator, ConfigDict, Field, TypeAdapter, model_validator

from .contracts import EvidenceDigest, OpaqueMetadataId, RouterModel


def _candidate_sha_is_not_reserved(value: str) -> str:
    """Reject the reserved all-zero candidate identity."""

    if value == "0" * 40:
        raise ValueError("candidate SHA must identify a real candidate")
    return value


CandidateSha: TypeAlias = Annotated[
    str,
    Field(pattern=r"^[0-9a-f]{40}$"),
    AfterValidator(_candidate_sha_is_not_reserved),
]


class _TestEngineerModel(RouterModel):
    """Immutable strict metadata for the independent evidence boundary."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=False,
        revalidate_instances="always",
    )


class TestVerdict(str, Enum):
    """The only report verdicts that an evidence adapter may resolve."""

    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    INCONCLUSIVE = "INCONCLUSIVE"


class TestCleanup(str, Enum):
    """The finite cleanup states attached to an independent report."""

    NOT_REQUIRED = "NOT_REQUIRED"
    CONFIRMED = "CONFIRMED"
    UNCONFIRMED = "UNCONFIRMED"


class TestEvidenceUnavailableReason(str, Enum):
    """Why an independent evidence report could not be resolved."""

    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNQUALIFIED = "UNQUALIFIED"


UnavailableTestEvidenceReason: TypeAlias = TestEvidenceUnavailableReason


class ReviewAdmissionReason(str, Enum):
    """Finite reasons why review evidence cannot be admitted."""

    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    RESOLVER_FAILURE = "RESOLVER_FAILURE"
    BINDING_MISMATCH = "BINDING_MISMATCH"
    REPORT_MISMATCH = "REPORT_MISMATCH"
    CELL_COVERAGE_MISMATCH = "CELL_COVERAGE_MISMATCH"
    VERDICT_MISMATCH = "VERDICT_MISMATCH"
    CLEANUP_INCOMPLETE = "CLEANUP_INCOMPLETE"
    TESTS_FAILED = "TESTS_FAILED"
    TESTS_BLOCKED = "TESTS_BLOCKED"
    TESTS_INCONCLUSIVE = "TESTS_INCONCLUSIVE"


class ReviewAdmissionStatus(str, Enum):
    """The finite result states of review-evidence admission."""

    ADMITTED = "ADMITTED"
    DENIED = "DENIED"


class TestBinding(_TestEngineerModel):
    """Identity binding shared by the authority and independently observed report."""

    scope_ref: OpaqueMetadataId
    project_ref: OpaqueMetadataId
    ticket_ref: OpaqueMetadataId
    candidate_sha: CandidateSha
    test_suite_digest: EvidenceDigest
    plan_digest: EvidenceDigest
    environment_digest: EvidenceDigest
    implementer_id: OpaqueMetadataId
    engineer_id: OpaqueMetadataId
    reviewer_id: OpaqueMetadataId

    @model_validator(mode="after")
    def actor_ids_are_distinct(self) -> Self:
        actors = (self.implementer_id, self.engineer_id, self.reviewer_id)
        if len(set(actors)) != len(actors):
            raise ValueError("implementer, engineer, and reviewer identities must be distinct")
        return self


class TestCellObservation(_TestEngineerModel):
    """One independently observed test cell and its bounded evidence references."""

    cell_id: OpaqueMetadataId
    verdict: TestVerdict
    evidence_ref: OpaqueMetadataId
    evidence_digest: EvidenceDigest
    reason_ref: OpaqueMetadataId | None

    @model_validator(mode="after")
    def reason_matches_verdict(self) -> Self:
        if self.verdict is TestVerdict.PASS and self.reason_ref is not None:
            raise ValueError("passing cells must not carry a failure reason")
        if self.verdict is not TestVerdict.PASS and self.reason_ref is None:
            raise ValueError("non-passing cells require a reason reference")
        return self


class TestReviewAuthority(_TestEngineerModel):
    """Active authority and exact expected cell set for one report attempt."""

    binding: TestBinding
    expected_report_ref: OpaqueMetadataId
    expected_cell_ids: tuple[OpaqueMetadataId, ...] = Field(min_length=1, max_length=512)
    cleanup_required: bool

    @model_validator(mode="after")
    def expected_cells_are_unique(self) -> Self:
        if len(self.expected_cell_ids) != len(set(self.expected_cell_ids)):
            raise ValueError("expected test cell identities must be unique")
        return self


class IndependentTestReport(_TestEngineerModel):
    """Immutable report data whose coverage is checked by the phase-2 gate."""

    report_ref: OpaqueMetadataId
    binding: TestBinding
    declared_verdict: TestVerdict
    cells: tuple[TestCellObservation, ...] = Field(max_length=512)
    cleanup: TestCleanup


class ResolvedTestEvidence(_TestEngineerModel):
    """Resolved evidence carrying its active authority and report."""

    status: Literal["FOUND"] = "FOUND"
    authority: TestReviewAuthority
    report: IndependentTestReport


class UnavailableTestEvidence(_TestEngineerModel):
    """Typed absence of independently qualified evidence."""

    status: Literal["UNAVAILABLE"] = "UNAVAILABLE"
    reason: TestEvidenceUnavailableReason


TestEvidenceResolution: TypeAlias = Annotated[
    ResolvedTestEvidence | UnavailableTestEvidence,
    Field(discriminator="status"),
]


class ReviewAdmissionRequest(_TestEngineerModel):
    """Metadata request identifying the report that a review transition needs."""

    project_ref: OpaqueMetadataId
    scope_ref: OpaqueMetadataId
    report_ref: OpaqueMetadataId


class ReviewAdmissionDecision(_TestEngineerModel):
    """Finite, self-consistent result of the phase-2 admission gate."""

    status: ReviewAdmissionStatus
    verdict: TestVerdict
    reason: ReviewAdmissionReason | None

    @model_validator(mode="after")
    def status_matches_verdict_and_reason(self) -> Self:
        if self.status is ReviewAdmissionStatus.ADMITTED:
            if self.verdict is not TestVerdict.PASS or self.reason is not None:
                raise ValueError("admitted decisions require PASS and no reason")
        elif self.verdict is TestVerdict.PASS or self.reason is None:
            raise ValueError("denied decisions require a non-PASS verdict and a reason")
        return self


class TestEvidenceResolver(Protocol):
    """Trusted control-plane port for one independently resolved report."""

    def resolve(self, *, request: ReviewAdmissionRequest) -> TestEvidenceResolution:
        """Resolve the active authority and report for a review request."""


_TEST_EVIDENCE_RESOLUTION_ADAPTER: TypeAdapter[TestEvidenceResolution] = TypeAdapter(
    TestEvidenceResolution
)


__all__ = (
    "CandidateSha",
    "IndependentTestReport",
    "ReviewAdmissionDecision",
    "ReviewAdmissionReason",
    "ReviewAdmissionRequest",
    "ReviewAdmissionStatus",
    "ResolvedTestEvidence",
    "TestBinding",
    "TestCellObservation",
    "TestCleanup",
    "TestEvidenceResolution",
    "TestEvidenceResolver",
    "TestEvidenceUnavailableReason",
    "TestReviewAuthority",
    "TestVerdict",
    "UnavailableTestEvidence",
    "UnavailableTestEvidenceReason",
)
