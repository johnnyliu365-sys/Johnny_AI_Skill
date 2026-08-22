"""Pure compare-and-swap planning for publication repository promotion.

This module deliberately stops at an immutable plan and readback comparison.  It
does not discover a remote, invoke Git, push a ref, create a tag, or repin a
descriptor.  Ticket 08 owns those effects after this plan has been reviewed.
"""

from __future__ import annotations

from enum import Enum
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .publication_repository_closure import (
    PublicationClosureResult,
    PublicationClosureStatus,
    PublicationCommit,
    PublicationPromotionRequest,
    PublicationRefKind,
    PublicationRemoteSnapshot,
    PublicationTreeDifference,
    PublicationVersion,
)

__all__ = [
    "PublicationMainUpdate",
    "PublicationMainUpdateMode",
    "PublicationPromotionPlan",
    "PublicationPromotionPlanResult",
    "PublicationPromotionReadbackResult",
    "PublicationTagUpdate",
    "build_publication_promotion_plan",
    "plan_publication_promotion",
    "verify_promotion_readback",
    "verify_publication_promotion_readback",
]

_MAIN_REF: Final[str] = "refs/heads/main"


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        revalidate_instances="always",
    )


class PublicationMainUpdateMode(str, Enum):
    CREATE = "CREATE"
    FORCE_WITH_LEASE = "FORCE_WITH_LEASE"


class PublicationMainUpdate(_StrictModel):
    """The exact main write, including its compare-and-swap lease."""

    ref_name: str = Field(min_length=1, max_length=64)
    old_target: PublicationCommit | None = None
    new_target: PublicationCommit
    mode: PublicationMainUpdateMode
    lease: str | None = None

    @field_validator("ref_name")
    @classmethod
    def _main_ref(cls, value: str) -> str:
        if value != _MAIN_REF:
            raise ValueError("the promotion main update must target refs/heads/main")
        return value

    @model_validator(mode="after")
    def _lease_matches_mode(self) -> Self:
        if self.mode is PublicationMainUpdateMode.CREATE:
            if self.old_target is not None or self.lease is not None:
                raise ValueError("CREATE cannot carry an old target or lease")
        else:
            if self.old_target is None:
                raise ValueError("FORCE_WITH_LEASE requires an old target")
            expected = f"{_MAIN_REF}:{self.old_target.value}"
            if self.lease != expected:
                raise ValueError("the main lease must bind the exact old SHA")
        return self


class PublicationTagUpdate(_StrictModel):
    """An absent-only immutable release-tag creation request."""

    ref_name: str = Field(min_length=1, max_length=256)
    target: PublicationCommit

    @field_validator("ref_name")
    @classmethod
    def _immutable_tag_ref(cls, value: str) -> str:
        if not value.startswith("refs/tags/plugin-v"):
            raise ValueError("promotion tags must use refs/tags/plugin-v<semver>")
        PublicationVersion(value=value.removeprefix("refs/tags/plugin-v"))
        return value


class PublicationPromotionPlan(_StrictModel):
    """One exact main CAS and one absent-only tag creation."""

    request: PublicationPromotionRequest
    main: PublicationMainUpdate
    tag: PublicationTagUpdate

    @model_validator(mode="after")
    def _plan_matches_request(self) -> Self:
        expected_mode = (
            PublicationMainUpdateMode.CREATE
            if self.request.expected_main is None
            else PublicationMainUpdateMode.FORCE_WITH_LEASE
        )
        if (
            self.main.new_target != self.request.candidate
            or self.main.mode is not expected_mode
            or self.main.old_target != self.request.expected_main
            or self.tag.target != self.request.candidate
            or self.tag.ref_name != f"refs/tags/{self.request.version.tag_name}"
        ):
            raise ValueError("promotion plan does not match its request")
        return self


class PublicationPromotionPlanResult(_StrictModel):
    """A finite refusal or one complete immutable plan."""

    status: PublicationClosureStatus
    plan: PublicationPromotionPlan | None = None

    @model_validator(mode="after")
    def _plan_status_pair(self) -> Self:
        if (self.status is PublicationClosureStatus.VERIFIED) != (self.plan is not None):
            raise ValueError("VERIFIED requires exactly one promotion plan")
        return self


PublicationPromotionReadbackResult = PublicationClosureResult


def _has_main(snapshot: PublicationRemoteSnapshot) -> PublicationCommit | None:
    mains = tuple(ref for ref in snapshot.refs if ref.kind is PublicationRefKind.MAIN)
    if len(mains) != 1:
        return None
    return mains[0].target


def _candidate_is_proven(
    request: PublicationPromotionRequest, candidate_closure: PublicationClosureResult
) -> PublicationClosureStatus | None:
    if candidate_closure.status is not PublicationClosureStatus.VERIFIED:
        return candidate_closure.status
    candidate_snapshot = candidate_closure.snapshot
    if candidate_snapshot is None or candidate_snapshot.default_branch != _MAIN_REF:
        return PublicationClosureStatus.PIN_MISMATCH
    if candidate_snapshot.repository != request.repository:
        return PublicationClosureStatus.PIN_MISMATCH
    if _has_main(candidate_snapshot) != request.candidate:
        return PublicationClosureStatus.PIN_MISMATCH
    return None


def plan_publication_promotion(
    request: PublicationPromotionRequest,
    snapshot: PublicationRemoteSnapshot,
    candidate_closure: PublicationClosureResult,
) -> PublicationPromotionPlanResult:
    """Return a pure CAS/tag plan, or one finite pre-effect refusal."""

    try:
        request = PublicationPromotionRequest.model_validate(request)
    except ValueError:
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.READBACK_MISMATCH
        )
    try:
        snapshot = PublicationRemoteSnapshot.model_validate(snapshot)
    except ValueError:
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.REF_SET_INVALID
        )
    try:
        candidate_closure = PublicationClosureResult.model_validate(candidate_closure)
    except ValueError:
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.PIN_MISMATCH
        )
    if snapshot.repository != request.repository:
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.READBACK_MISMATCH
        )
    if snapshot.default_branch != _MAIN_REF:
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.DEFAULT_BRANCH_INVALID
        )
    proven_status = _candidate_is_proven(request, candidate_closure)
    if proven_status is not None:
        return PublicationPromotionPlanResult(status=proven_status)

    main_target = _has_main(snapshot)
    if request.expected_main is None:
        if snapshot.refs:
            return PublicationPromotionPlanResult(
                status=PublicationClosureStatus.REMOTE_NOT_EMPTY
            )
        mode = PublicationMainUpdateMode.CREATE
    else:
        if main_target is None:
            return PublicationPromotionPlanResult(
                status=PublicationClosureStatus.MAIN_MISSING
            )
        if main_target != request.expected_main:
            return PublicationPromotionPlanResult(
                status=PublicationClosureStatus.STALE_MAIN
            )
        mode = PublicationMainUpdateMode.FORCE_WITH_LEASE

    tag_name = f"refs/tags/{request.version.tag_name}"
    if any(ref.name == tag_name for ref in snapshot.refs):
        return PublicationPromotionPlanResult(
            status=PublicationClosureStatus.TAG_COLLISION
        )

    old_target = request.expected_main
    main = PublicationMainUpdate(
        ref_name=_MAIN_REF,
        old_target=old_target,
        new_target=request.candidate,
        mode=mode,
        lease=None if old_target is None else f"{_MAIN_REF}:{old_target.value}",
    )
    tag = PublicationTagUpdate(ref_name=tag_name, target=request.candidate)
    return PublicationPromotionPlanResult(
        status=PublicationClosureStatus.VERIFIED,
        plan=PublicationPromotionPlan(request=request, main=main, tag=tag),
    )


build_publication_promotion_plan = plan_publication_promotion


def verify_publication_promotion_readback(
    plan: PublicationPromotionPlan,
    snapshot: PublicationRemoteSnapshot,
) -> PublicationClosureResult:
    """Compare exact post-effect refs to a plan without performing an effect."""

    def result(
        status: PublicationClosureStatus,
        readback: PublicationRemoteSnapshot | None = None,
    ) -> PublicationClosureResult:
        return PublicationClosureResult(
            status=status,
            snapshot=readback,
            difference=PublicationTreeDifference()
            if status is PublicationClosureStatus.VERIFIED
            else None,
        )

    try:
        plan = PublicationPromotionPlan.model_validate(plan)
    except ValueError:
        return result(PublicationClosureStatus.READBACK_MISMATCH)
    try:
        snapshot = PublicationRemoteSnapshot.model_validate(snapshot)
    except ValueError:
        return result(PublicationClosureStatus.REF_SET_INVALID)
    if snapshot.repository != plan.request.repository:
        return result(PublicationClosureStatus.READBACK_MISMATCH, snapshot)
    if snapshot.default_branch != _MAIN_REF:
        return result(PublicationClosureStatus.DEFAULT_BRANCH_INVALID, snapshot)
    main_target = _has_main(snapshot)
    if main_target is None:
        return result(PublicationClosureStatus.MAIN_MISSING, snapshot)
    if main_target != plan.request.candidate:
        return result(PublicationClosureStatus.PIN_MISMATCH, snapshot)
    tags = tuple(ref for ref in snapshot.refs if ref.name == plan.tag.ref_name)
    if not tags:
        return result(PublicationClosureStatus.READBACK_MISMATCH, snapshot)
    if tags[0].target != plan.tag.target:
        return result(PublicationClosureStatus.TAG_COLLISION, snapshot)
    return result(PublicationClosureStatus.VERIFIED, snapshot)


verify_promotion_readback = verify_publication_promotion_readback
