# 07｜Publication promotion compare-and-swap contract

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-1 through AC-4 |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `APPROVED / NOT_DISPATCHED / CONVERGENCE_REFROZEN` / `CLOSURE_02` |
| Baseline | `46ad6d391f27294bd42c35eef47479529472b5c6` |
| Dependency | Ticket 06 integrated at the exact baseline above. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh, capability readback required at dispatch |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket only, no helper |
| Delivery profile | `POC / STANDARD`: the contract plans and verifies deterministic local fixture transactions; it does not create or mutate a real remote. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over every new public module and focused test module |
| XSS classification | `N/A` |
| Worktree / branch | `.worktrees/claude-publication-07` / `implement/claude-publication-07-cas-promotion` |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/publication_promotion.py
create = tests/test_publication_promotion.py
modify = .claude-plugin/marketplace.json
forbid = .claude-plugin/plugin.json
forbid = .codex-plugin/
forbid = README.md
forbid = library/local_orchestration/publication_repository_closure.py
forbid = library/local_orchestration/claude_plugin_cache_closure.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
```

Ticket 06's closure modules are read-only inputs. The owner changes only the new promotion
module/tests. The reviewer may generate the required marketplace pin after source review; neither
role may create a GitHub repository, call `git push` against a non-disposable remote, create a
real tag or repin `main` by hand.

## Closure 01 convergence and Closure 02 refreeze

`CLOSURE_01` submitted `9ffedeb` and its sole additive correction `2ca8743`. The final Terra
review found `EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED`: P5 exercised a bypass-built partial
SHA but did not preserve direct regressions for a malformed version, malformed ref, or null and
missing-field snapshots. The runtime fails closed for those inputs, but a reviewer probe is not a
replacement for the frozen TDD matrix. These commits are retained, unintegrated evidence; they
are not merge authority.

`CLOSURE_02` changes no SPEC, topology, public contract, profile or boundary. It reuses the same
worktree/branch and one Luna/xhigh implementer, but permits exactly one additive test correction
inside `tests/test_publication_promotion.py`. That correction must add the four direct P5 cases,
then re-run P1–P6, ticket 06 closure tests and the payload boundary. The source module is read-only
in this refreeze unless a newly added P5 test demonstrates a finite-result defect. A fresh Terra
review is required before any reviewer pin generation or guarded integration.

## Sole observable closure

Given a validated publication snapshot, expected old `main`, generated candidate SHA and semantic
version, produce one immutable promotion plan only when the ref set/default branch/root/tree
closure is admissible. Otherwise return one finite failure before an effect can be requested. A
plan contains exact old/new `main`, new immutable `plugin-v<semver>` tag, candidate/source
identities and correlation metadata; it cannot be reconstructed from prose or a partial SHA.

The contract may exercise `git` only against disposable local bare fixtures. It does not contain a
default remote URI, read credentials, call a hosting API, discover a repository, execute a real
push or treat a local tracking ref as current remote truth.

## Frozen contracts and transaction order

Use the approved `PublicationPromotionRequest`, `PublicationRemoteSnapshot`,
`PublicationClosureResult` and finite `PublicationClosureStatus`. Add only typed promotion-plan
and readback-result types necessary to express these steps without booleans or free-form status:

1. read and verify the exact pre-effect snapshot;
2. reject unexpected/non-empty first-release state, stale expected `main`, unexpected ref,
   wrong default branch, non-root candidate, tree difference or tag collision;
3. emit an exact CAS request for `main` and an absent-only immutable tag request; and
4. compare a subsequent snapshot to the exact plan and return verified readback or a named
   mismatch.

The future effect adapter must use `--force-with-lease=refs/heads/main:<expected-old-sha>` only
when the plan says an existing `main` changes between independent roots. This ticket does not
execute that adapter. No promotion plan permits tag movement, version reuse, implicit retry or a
descriptor repin before readback.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| P1 first release | Empty fixture produces a plan with candidate `main` and absent-only `plugin-v0.4.10`; no expected old main is invented. |
| P2 update CAS | A valid prior `main` produces a plan bound to that exact SHA; replacing it in the fixture requires that exact old SHA. |
| P3 pre-effect rejection | Stale expected main, foreign ref, wrong default branch, non-root candidate, payload difference and tag collision each return distinct finite rejection and no effect request. |
| P4 readback | Exact post-effect snapshot verifies; wrong `main`, absent/moved tag, extra ref, changed candidate tree or missing candidate produces named readback failure. |
| P5 input typing | Partial/malformed SHA, malformed version/ref, null/missing snapshot fields and bypass-built DTOs cannot create a plan. |
| P6 no hidden effect | The injected local fixture port records no call until a valid plan is supplied; no source path contains a hard-coded GitHub URL, credential lookup or unbounded retry. |

This is new behavior: report green tests and use reviewer reverse mutation. The reviewer must
change the plan's expected-old SHA or tag target after planning; P2/P4 must turn red, then return
green after exact restoration. If the plan still verifies, classify it as an evidence defect.

## Verification and completion

Run focused tests, ticket 06's closure tests, `tests/test_plugin_payload_boundary.py`, strict
type checking and `git diff --check`. The reviewer performs the independent mutation, verifies
all error/result names against the SPEC and runs the focused suites from a fresh clone. The owner
commits only source/tests; the reviewer performs generated pin refresh and guarded integration as
ticket 06 describes.

`COMPLETED` returns `ACTION_COMPLETED`. A requested real push/repository/tag, absent ticket-06
contract, new ref policy or version decision is `BLOCKED` or `CHANGE_DETECTED`; it does not become
an effect through this ticket.
