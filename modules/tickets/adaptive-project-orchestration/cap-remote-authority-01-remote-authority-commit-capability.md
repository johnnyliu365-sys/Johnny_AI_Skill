# CAP-REMOTE-AUTHORITY-01 — prove Remote Authority Commit capability

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-CAP-REMOTE-AUTHORITY-01-REMOTE-AUTHORITY-COMMIT-CAPABILITY` / `CAPABILITY_INVESTIGATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 13 / AC-17R13 and TDD item 26 |
| Requirement / Context / ADR | `PRD-20260829-046` / `CHG-20260829-046` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260829-13` (`30890692e40212634a11db5b9d41477b1435aa4f087637f9c1a96795f395243d`) / `ADR-20260829-034` |
| State / closure | `OPEN / EXTERNAL_EFFECT_AUTHORITY_REQUIRED / NON_DISPATCHABLE`; one future closure is `PROVEN`, `UNPROVEN`, `UNSUPPORTED`, or `BLOCKED`, never an implicit writer admission. |
| Opening authority | Project owner, 2026-08-29 (Asia/Taipei): approved Revision 13 at `3453f3e5709502bff64647eb2b4d6ad0b829212a` and authorized opening this one capability investigation. That approval grants no source change, remote test, credential, provider, push, publication, installation, release, or deployment effect. |
| Existing declaration evidence | [PAI-06 evidence](../../../doc/reviews/project-authority-integration/06-live-provider-qualification-evidence.md) declares this development repository's credential-free identity as `https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git`, authority ref as `refs/heads/main`, and provider/method as `github.com` via Git HTTPS plus qualified GitHub readback. It is historical declaration/qualification evidence only; it is not reusable authority for this new remote mutation. |
| Control owner / reviewer | `ticket-review` semantic profile — Sol/high; sole orchestrator, final reviewer, sole control-plane integrator and direct remote readback verifier. |
| Investigation owner | `implementation-high-assurance` semantic profile — Terra/xhigh, once the exact external-effect authority below is recorded. The investigation is indivisible: a positive claim has concurrent-writer, remote-policy and remote-readback proof burden. |
| Delivery / language | `POC / HIGH_ASSURANCE / HIGH_ASSURANCE_REQUIRED`; Python 3.11 strict test-only harnesses plus actual isolated remote-provider evidence. No mock, local bare repository, API name, remote-tracking cache, or different remote can prove this capability. |
| XSS / effects | `XSS_NOT_APPLICABLE`. No effect is admissible at ticket opening. Host Git transport owns credentials; credentials, headers, tokens, URLs with userinfo, raw provider payloads and unrestricted command output are forbidden evidence. |

## Boundary declaration

```johnny-boundary
create = tests/test_remote_authority_commit_capability.py
modify = tests/test_remote_authority_commit_capability.py
create = modules/element/python/adaptive-project-orchestration/cap-remote-authority-01-remote-authority-commit-capability/
modify = modules/element/python/adaptive-project-orchestration/cap-remote-authority-01-remote-authority-commit-capability/
forbid = library/
forbid = tests/test_target_document_management.py
forbid = tests/test_managed_artifact_planning.py
forbid = tests/test_managed_artifact_recovery_contracts.py
forbid = tests/test_recoverable_managed_artifact_writer.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

This boundary admits evidence harnesses only. It never admits a production remote-commit writer,
local target-worktree/index/HEAD/ref mutation, a retry/rebase/merge/force/reset/delete fallback,
or repair of `f99d836`.

## Exact external-effect admission required before dispatch

The reviewer must first obtain and record one owner authorization that binds all of the following
without secret material:

1. the credential-free repository identity and the full declared production authority ref to be
   observed read-only; an observed `main`, local branch, upstream, tag, SHA or `origin/main` cache
   cannot substitute for the declaration;
2. one **new, isolated remote test ref or dedicated test repository**, its exact full name, provider
   environment, qualified actor identity/role, correlation ID, fresh direct baseline SHA and expiry;
3. the only allowed effects: create the isolated target from that baseline, configure/read back its
   test-only policy if needed, make two disposable candidates, attempt the bounded non-force race
   and the named refusal probes, directly read back results, then perform the owner-approved
   cleanup; and
4. explicit permission for any test-only protection-policy configure/remove and isolated-target
   delete cleanup. No command may target, create a commit on, update, force-update, delete or
   reconfigure the declared production authority ref.

The evidence in PAI-06 did not prove administrative bypass or stale-approval invalidation, and its
old disposable branch was deleted. It does not satisfy items 2–4. Until the new authorization is
recorded, the Router result is `WAIT_FOR_HUMAN / EXTERNAL_EFFECT_AUTHORITY_REQUIRED`; no worktree
dispatch, provider call, remote read, push or credential use occurs.

## One observable closure

On the actual declared authority **remote**, using only the owner-authorized isolated target, prove
or honestly refuse the Remote Authority Commit capability. The test begins from one fresh direct
remote observation of the isolated target. Two independent disposable candidates must each have
that observed SHA as their sole parent and carry distinct, complete canonical test trees.

Exactly one non-force, fast-forward-only transition may advance the isolated target. The other
attempt must neither retry nor alter a target and must return `STALE_AUTHORITY` or another finite
fail-closed outcome resolved by fresh direct remote readback. The winning full tree must remain
observable through a declared direct remote object/tree read method; remote-tracking data is not
that proof.

The same qualified actor/policy combination must also reject an ordinary bypass update, force
update and ref deletion of the isolated target. If any of those is unavailable, accepted, only
documentation-backed, ambiguous, credential-dependent without an authorized qualified identity,
or cannot be directly read back, the capability is `UNPROVEN` / `UNSUPPORTED` / `BLOCKED` with a
named finite reason. It is never upgraded to a writer admission.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `RAC1` | Strict test-only authority input accepts only one credential-free identity, canonical full refs, bounded correlation/expiry and an explicit allowed-effect set. Null, extra, symbolic/tag/SHA-like refs, credential-bearing identities and undeclared effects reject before host Git/provider invocation. |
| `RAC2` | A fresh direct remote observation binds exact repository, isolated full ref, SHA, time, observer and normalized bounded evidence digest. A fetched remote-tracking ref, local branch or prior observation fails closed as non-authority. |
| `RAC3` | Two independently created candidates have the same directly observed sole parent and distinct complete trees. Their bounded non-force race yields at most one direct authority transition; no loser rebase, merge, retry, force, local target mutation or silent compensation is possible. |
| `RAC4` | Fresh direct remote readback resolves every race result. A winner readback unequal to its candidate is `PUSH_UNCONFIRMED`; a losing readback that names the other candidate is `STALE_AUTHORITY`; unavailable, ambiguous or identity-mismatched readback is a finite fail-closed result. |
| `RAC5` | Actual provider/transport probes on the isolated target reject ordinary bypass update, force update and ref deletion for the qualified identity. Missing policy, actor ambiguity, unsupported API/transport or an accepted bypass produces `REMOTE_POLICY_REJECTED` / `UNPROVEN`, never success. |
| `RAC6` | Evidence preserves only typed finite outcomes, opaque evidence references, bounded metadata and candidate/observed SHAs. It contains no credential, raw token/header, unbounded provider response, production tree, local target path or Router transcript. |
| `RAC7` | Focused tests, strict type check, compile, exact boundary/index checks and reviewer-direct counter-mutation all pass. The result does not add or expose a production writer. |
| `RACM1` | Reverse-mutate a candidate to use any parent other than the fresh direct observation, or make the two candidates share a tree; `RAC3` turns red, then exact restoration returns green. |
| `RACM2` | Reverse-mutate the race path to retry/rebase/force after a refusal, or resolve the result from `origin/<ref>`; `RAC3`/`RAC4` turn red, then exact restoration returns green. |
| `RACM3` | Reverse-mutate policy admission to accept an untested force/delete/bypass path or documentation-only claim; `RAC5` turns red, then exact restoration returns green. |

## Required reviewer-owned adversarial evidence

After `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, the Sol/high reviewer binds the exact
candidate SHA and dispatches two isolated, read-only Terra/xhigh evidence lanes. Helpers cannot
modify, commit, push, configure a provider, approve, integrate or clean up a remote target.

1. **Concurrent-transition helper.** Reproduces the two-writer same-base race independently,
   attacks parent/tree completeness, and verifies the losing path has no target effect or retry.
2. **Policy and evidence helper.** Challenges force/delete/ordinary-bypass admission, direct versus
   cached readback, declared identity/ref matching, secret exclusion and cleanup evidence.

The reviewer independently reruns every result, performs one further counter-mutation through a
different door, and writes the review record. A `PROVEN` result authorizes neither source writer
nor deployment: a later approved architecture/SPEC ticket is still required.

## Verification and return

Investigation-owner commands, after external-effect admission only:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_remote_authority_commit_capability.py
py -3.11 -m mypy --strict tests/test_remote_authority_commit_capability.py
py -3.11 -m compileall -q tests/test_remote_authority_commit_capability.py
git diff --check <ticket-integrated-authority> HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with one typed capability
outcome and bounded evidence set; `BLOCKED -> HALT` naming the exact external authority or remote
capability missing; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` only for an actual AC-17R13
conflict. The investigation owner does not commit or push. Same-lifetime dispatch is
`reviewer -> wait_agent -> review -> gate`; no runner, queue, receipt, descriptor, host gateway or
workspace readback is created or required.
