"""TDD cells for the pure publication promotion CAS planner."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from typing import Final
from unittest.mock import patch

from library.local_orchestration.publication_repository_closure import (
    PublicationClosureResult,
    PublicationClosureStatus,
    PublicationCommit,
    PublicationPromotionRequest,
    PublicationRef,
    PublicationRefKind,
    PublicationRemoteSnapshot,
    PublicationRepositoryRef,
    PublicationTreeDifference,
    PublicationVersion,
)
from library.local_orchestration.publication_promotion import (
    PublicationMainUpdate,
    PublicationMainUpdateMode,
    PublicationPromotionPlan,
    PublicationPromotionPlanResult,
    plan_publication_promotion,
    verify_publication_promotion_readback,
)
from library.local_orchestration.runtime_contracts import CorrelationId


_REPO: Final[PublicationRepositoryRef] = PublicationRepositoryRef(
    value="https://example.invalid/johnny-publication.git"
)
_OLD: Final[PublicationCommit] = PublicationCommit(value="1" * 40)
_CANDIDATE: Final[PublicationCommit] = PublicationCommit(value="2" * 40)
_OTHER: Final[PublicationCommit] = PublicationCommit(value="3" * 40)
_VERSION: Final[PublicationVersion] = PublicationVersion(value="0.4.10")
_OLD_VERSION: Final[PublicationVersion] = PublicationVersion(value="0.4.9")


def _ref(name: str, target: PublicationCommit) -> PublicationRef:
    kind = (
        PublicationRefKind.MAIN
        if name == "refs/heads/main"
        else PublicationRefKind.RELEASE_TAG
    )
    return PublicationRef(kind=kind, name=name, target=target)


def _snapshot(*refs: PublicationRef, repository: PublicationRepositoryRef = _REPO) -> PublicationRemoteSnapshot:
    return PublicationRemoteSnapshot(
        repository=repository,
        default_branch="refs/heads/main",
        refs=tuple(refs),
    )


def _request(
    *, expected_main: PublicationCommit | None, candidate: PublicationCommit = _CANDIDATE,
    version: PublicationVersion = _VERSION,
) -> PublicationPromotionRequest:
    return PublicationPromotionRequest(
        repository=_REPO,
        expected_main=expected_main,
        candidate=candidate,
        version=version,
        correlation=CorrelationId(value="promotion-test-01"),
    )


def _candidate_closure(
    candidate: PublicationCommit = _CANDIDATE,
    *,
    status: PublicationClosureStatus = PublicationClosureStatus.VERIFIED,
) -> PublicationClosureResult:
    snapshot = _snapshot(_ref("refs/heads/main", candidate))
    return PublicationClosureResult(
        status=status,
        snapshot=snapshot if status is PublicationClosureStatus.VERIFIED else None,
        difference=PublicationTreeDifference()
        if status is PublicationClosureStatus.VERIFIED
        else None,
    )


def _post_closure(
    snapshot: PublicationRemoteSnapshot,
    *,
    status: PublicationClosureStatus = PublicationClosureStatus.VERIFIED,
    difference: PublicationTreeDifference | None = None,
) -> PublicationClosureResult:
    return PublicationClosureResult(
        status=status,
        snapshot=snapshot,
        difference=(
            PublicationTreeDifference()
            if status is PublicationClosureStatus.VERIFIED
            else difference
        ),
    )


class PublicationPromotionPlanTests(unittest.TestCase):
    def test_p1_first_release_plans_create_main_and_absent_tag(self) -> None:
        result = plan_publication_promotion(
            _request(expected_main=None), _snapshot(), _candidate_closure()
        )
        self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)
        self.assertIsNotNone(result.plan)
        assert result.plan is not None
        self.assertEqual(result.plan.main.mode, PublicationMainUpdateMode.CREATE)
        self.assertIsNone(result.plan.main.old_target)
        self.assertIsNone(result.plan.main.lease)
        self.assertEqual(result.plan.tag.ref_name, "refs/tags/plugin-v0.4.10")
        self.assertEqual(result.plan.tag.target, _CANDIDATE)

    def test_p2_update_binds_exact_old_main_and_force_with_lease(self) -> None:
        pre = _snapshot(_ref("refs/heads/main", _OLD), _ref("refs/tags/plugin-v0.4.9", _OLD))
        result = plan_publication_promotion(
            _request(expected_main=_OLD), pre, _candidate_closure()
        )
        self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)
        assert result.plan is not None
        self.assertEqual(result.plan.main.mode, PublicationMainUpdateMode.FORCE_WITH_LEASE)
        self.assertEqual(result.plan.main.old_target, _OLD)
        self.assertEqual(result.plan.main.lease, f"refs/heads/main:{_OLD.value}")

    def test_p2_mutating_planned_old_sha_turns_readback_red_then_restores(self) -> None:
        result = plan_publication_promotion(
            _request(expected_main=_OLD),
            _snapshot(_ref("refs/heads/main", _OLD)),
            _candidate_closure(),
        )
        assert result.plan is not None
        plan = result.plan
        post = _snapshot(
            _ref("refs/heads/main", _CANDIDATE),
            _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
        )
        mutated_main = PublicationMainUpdate(
            ref_name="refs/heads/main",
            old_target=_OTHER,
            new_target=_CANDIDATE,
            mode=PublicationMainUpdateMode.FORCE_WITH_LEASE,
            lease=f"refs/heads/main:{_OTHER.value}",
        )
        mutated_plan = PublicationPromotionPlan.model_construct(
            request=plan.request,
            pre_effect_snapshot=plan.pre_effect_snapshot,
            main=mutated_main,
            tag=plan.tag,
        )
        mutated = verify_publication_promotion_readback(
            mutated_plan, _post_closure(post)
        )
        self.assertEqual(mutated.status, PublicationClosureStatus.READBACK_MISMATCH)
        restored = verify_publication_promotion_readback(plan, _post_closure(post))
        self.assertEqual(restored.status, PublicationClosureStatus.VERIFIED)

    def test_p3_pre_effect_failures_are_finite_and_planless(self) -> None:
        stale = plan_publication_promotion(
            _request(expected_main=_OTHER),
            _snapshot(_ref("refs/heads/main", _OLD)),
            _candidate_closure(),
        )
        self.assertEqual(stale.status, PublicationClosureStatus.STALE_MAIN)
        self.assertIsNone(stale.plan)

        foreign_ref = PublicationRef.model_construct(
            kind=PublicationRefKind.MAIN,
            name="refs/heads/development",
            target=_OLD,
        )
        foreign = plan_publication_promotion(
            _request(expected_main=_OLD),
            PublicationRemoteSnapshot.model_construct(
                repository=_REPO,
                default_branch="refs/heads/main",
                refs=(foreign_ref,),
            ),
            _candidate_closure(),
        )
        self.assertEqual(foreign.status, PublicationClosureStatus.REF_SET_INVALID)
        self.assertIsNone(foreign.plan)

        wrong_default = PublicationRemoteSnapshot(
            repository=_REPO,
            default_branch="refs/heads/release",
            refs=(),
        )
        wrong = plan_publication_promotion(
            _request(expected_main=None), wrong_default, _candidate_closure()
        )
        self.assertEqual(wrong.status, PublicationClosureStatus.DEFAULT_BRANCH_INVALID)

        non_root = plan_publication_promotion(
            _request(expected_main=None), _snapshot(),
            _candidate_closure(status=PublicationClosureStatus.COMMIT_NOT_ROOT),
        )
        self.assertEqual(non_root.status, PublicationClosureStatus.COMMIT_NOT_ROOT)

        tree_mismatch = plan_publication_promotion(
            _request(expected_main=None), _snapshot(),
            _candidate_closure(status=PublicationClosureStatus.TREE_MISMATCH),
        )
        self.assertEqual(tree_mismatch.status, PublicationClosureStatus.TREE_MISMATCH)

        collision = plan_publication_promotion(
            _request(expected_main=_OLD),
            _snapshot(
                _ref("refs/heads/main", _OLD),
                _ref("refs/tags/plugin-v0.4.10", _OTHER),
            ),
            _candidate_closure(),
        )
        self.assertEqual(collision.status, PublicationClosureStatus.TAG_COLLISION)

    def test_p4_exact_readback_is_verified_and_mutations_turn_red(self) -> None:
        result = plan_publication_promotion(
            _request(expected_main=_OLD),
            _snapshot(_ref("refs/heads/main", _OLD)),
            _candidate_closure(),
        )
        assert result.plan is not None
        plan = result.plan
        post = _snapshot(
            _ref("refs/heads/main", _CANDIDATE),
            _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
        )
        verified = verify_publication_promotion_readback(plan, _post_closure(post))
        self.assertEqual(verified.status, PublicationClosureStatus.VERIFIED)

        wrong_main = verify_publication_promotion_readback(
            plan,
            _post_closure(
                _snapshot(
                    _ref("refs/heads/main", _OTHER),
                    _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
                )
            ),
        )
        self.assertEqual(wrong_main.status, PublicationClosureStatus.PIN_MISMATCH)

        absent_tag = verify_publication_promotion_readback(
            plan, _post_closure(_snapshot(_ref("refs/heads/main", _CANDIDATE)))
        )
        self.assertEqual(absent_tag.status, PublicationClosureStatus.READBACK_MISMATCH)

        moved_tag = verify_publication_promotion_readback(
            plan,
            _post_closure(
                _snapshot(
                    _ref("refs/heads/main", _CANDIDATE),
                    _ref("refs/tags/plugin-v0.4.10", _OTHER),
                )
            ),
        )
        self.assertEqual(moved_tag.status, PublicationClosureStatus.TAG_COLLISION)

        extra_result = verify_publication_promotion_readback(
            plan,
            _post_closure(
                _snapshot(
                    _ref("refs/heads/main", _CANDIDATE),
                    _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
                    _ref("refs/tags/plugin-v0.4.11", _CANDIDATE),
                )
            ),
        )
        self.assertEqual(extra_result.status, PublicationClosureStatus.REF_SET_INVALID)

        changed_tree = verify_publication_promotion_readback(
            plan,
            _post_closure(
                post,
                status=PublicationClosureStatus.TREE_MISMATCH,
                difference=PublicationTreeDifference(content_mismatch=("payload.txt",)),
            ),
        )
        self.assertEqual(changed_tree.status, PublicationClosureStatus.TREE_MISMATCH)

        missing_candidate = verify_publication_promotion_readback(
            plan,
            _post_closure(
                _snapshot(_ref("refs/heads/main", _OLD)),
                status=PublicationClosureStatus.PIN_MISMATCH,
            ),
        )
        self.assertEqual(missing_candidate.status, PublicationClosureStatus.PIN_MISMATCH)

    def test_p4_retains_admitted_tags_but_rejects_extra_allowed_tag(self) -> None:
        pre = _snapshot(
            _ref("refs/heads/main", _OLD),
            _ref("refs/tags/plugin-v0.4.9", _OLD),
        )
        result = plan_publication_promotion(
            _request(expected_main=_OLD), pre, _candidate_closure()
        )
        assert result.plan is not None
        plan = result.plan
        retained = _snapshot(
            _ref("refs/heads/main", _CANDIDATE),
            _ref("refs/tags/plugin-v0.4.9", _OLD),
            _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
        )
        self.assertEqual(
            verify_publication_promotion_readback(plan, _post_closure(retained)).status,
            PublicationClosureStatus.VERIFIED,
        )
        extra = _snapshot(
            _ref("refs/heads/main", _CANDIDATE),
            _ref("refs/tags/plugin-v0.4.9", _OLD),
            _ref("refs/tags/plugin-v0.4.10", _CANDIDATE),
            _ref("refs/tags/plugin-v0.4.11", _OTHER),
        )
        self.assertEqual(
            verify_publication_promotion_readback(plan, _post_closure(extra)).status,
            PublicationClosureStatus.REF_SET_INVALID,
        )

    def test_p5_bypass_built_inputs_cannot_create_a_plan(self) -> None:
        malformed_request = PublicationPromotionRequest.model_construct(
            repository=_REPO,
            expected_main=None,
            candidate=PublicationCommit.model_construct(value="partial"),
            version=_VERSION,
            correlation=CorrelationId(value="promotion-test-01"),
        )
        result = plan_publication_promotion(
            malformed_request, _snapshot(), _candidate_closure()
        )
        self.assertEqual(result.status, PublicationClosureStatus.READBACK_MISMATCH)
        self.assertIsNone(result.plan)

        malformed_plan = PublicationPromotionPlan.model_construct(
            request=malformed_request,
            main=None,
            tag=None,
        )
        readback = verify_publication_promotion_readback(
            malformed_plan, _post_closure(_snapshot())
        )
        self.assertEqual(readback.status, PublicationClosureStatus.READBACK_MISMATCH)

    def test_p6_planner_is_pure_and_never_calls_a_process_or_effect(self) -> None:
        with patch.object(subprocess, "run", side_effect=AssertionError("effect")):
            result = plan_publication_promotion(
                _request(expected_main=None), _snapshot(), _candidate_closure()
            )
        self.assertEqual(result.status, PublicationClosureStatus.VERIFIED)


if __name__ == "__main__":
    unittest.main()
