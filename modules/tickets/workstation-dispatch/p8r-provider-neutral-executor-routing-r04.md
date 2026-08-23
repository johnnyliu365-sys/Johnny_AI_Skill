# P8R-R04｜Canonical provider-neutral executor routing

| Field | Value |
| --- | --- |
| Artifact / closure | `P8R-EXECUTOR-ROUTING-04` / `CLOSURE-EXECUTOR-ROUTING-P8R-03` revision `03` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` revision `03` / AC-01 through AC-11 |
| PRD / change | `PRD-20260822-030` / `CHG-20260822-030`, amended by `PRD-20260822-032` / `CHG-20260822-032` and `PRD-20260823-033` / `CHG-20260823-033` |
| Sealed Context / baseline | `CTX-EXECUTOR-ROUTING-20260823-03` / `doc/context/executor-routing/codex-provider-neutral-executor-routing-r03.md` / `de7a935546a4229add2439bfdc37f40e1f22f30f` |
| State | `DONE / APPROVED / INTEGRATED / REVISION_05` |
| Replaces | `P8R-EXECUTOR-ROUTING-03`, `BLOCKED / REQUIREMENT_CHANGED / CHG-20260823-033`; its uncommitted source is not a baseline or merge source. |
| Control owner / reviewer | Current-session Codex reviewer; semantic `ticket-review` profile, Terra/xhigh. |
| Implementation owner | One current-session implementation owner; semantic `implementation-standard` profile, Luna/xhigh. |
| Decomposition / elevation | `READY_LOW_MODEL`; one pure resolver closure, frozen contract, finite TDD matrix, no external effect, and no unresolved design choice. Elevation is not authorized. |
| Delivery stage / profile | `POC` / `STANDARD`; one lane, zero helpers. The reviewer binds the candidate to the ticket manually; no host workspace/profile/rank, receipt delivery, runner, or wake claim is permitted. |
| Worktree / branch | Reviewer creates only `.worktrees/p8r-provider-neutral-executor-routing-r04` at this ticket's committed `main` baseline on `implement/p8r-provider-neutral-executor-routing-r04`. |
| Known host gap | `KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`; it is not task/workspace/profile/rank, receipt-delivery, runner, or wake evidence. |
| Language / checker | Python 3.11; frozen Pydantic contracts, complete annotations, finite enums; `mypy --strict`. |
| XSS / effects | `N/A`; the implementation boundary has no Browser/WebView/HTML/DOM/JavaScript, host, process, credential, provider, receipt, task, worktree-control, runner, network, or Git effect. The reviewer-only publication transaction is an integration artifact, not resolver behavior. |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/executor_routing.py
create = tests/test_executor_routing.py
modify = .claude-plugin/marketplace.json
forbid = library/local_orchestration/dispatch_session.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

## Observable closure and composition

Create one pure `ExecutorRoutingResolver`. It receives injected `ExecutorRoutingTable`,
`ExecutorProfileRegistry`, and `RouteRequest` objects and returns either exactly one selected
semantic profile plus exact reviewer binding or one finite named rejection. The explicit caller is
the Composition Root and supplies test fakes only; it holds no host client, credential, global
singleton, configuration reader, provider adapter, effect port, or historical-object cache.

Before normal lookup, the resolver reconstructs canonical frozen snapshots through ordinary strict
validation in this fixed order: routing table, profile registry, then any request assessment
verification consumed by an implementation route. A malformed table returns
`ROUTING_TABLE_INVALID`; malformed registry data returns `PROFILE_REGISTRY_INVALID`; malformed or
bypass-built assessment verification returns `HARD_TICKET_ASSESSMENT_INVALID`. No validation
exception may escape `resolve()` and no bypass-created object can return `SELECTED`.

The implementation defines the revision-03 public contracts exactly: `RoutingPurpose`,
`ProfileAvailability`, `VerifiedCapabilityRank`, `AssessmentProvenance`, `AssessmentFreshness`,
`ResolutionStatus`, `ExecutorProfileRef`, `ExecutorProfile`, `RoutingKey`,
`AssessmentVerification`, `HardTicketAssessment`, `ReviewBinding`, `OwnerOverrideRecord`,
`RouteRequest`, `RouteResolution`, `ExecutorRoutingTable`, and `ExecutorProfileRegistry`.
`IndependentVerificationEvidenceRef` is a named opaque type. No provenance, freshness, forgery,
or authority rule may inspect string contents.

## Reviewer-only publication binding

`library/` is a declared plugin payload tree. Therefore, after the reviewer has accepted the
source/test diff and written the candidate source commit, but before
`admit_document_mutation`, the reviewer alone must run the committed publication generator on the
same candidate worktree:

```text
py -3.11 -m library.local_orchestration.plugin_publication --repo . --manifest .claude-plugin/plugin.json --marketplace .claude-plugin/marketplace.json --ref refs/heads/publication-0.4.9
py -3.11 -m library.local_orchestration.plugin_publication --repo . --manifest .claude-plugin/plugin.json --marketplace .claude-plugin/marketplace.json --ref refs/heads/publication-0.4.9 --verify-only
```

The first command creates the declared payload tree commit, updates the local pushable publication
anchor, and changes only the marketplace pin through the generator. Hand-editing the SHA is
forbidden. The reviewer commits that generated marketplace change on the same candidate branch as
the resolver source, then reruns the pin/tree/reachability checks. The implementation owner must
not invoke the generator, alter the pin, or modify `.claude-plugin/marketplace.json`.

This is local publication-integrity evidence only. It does not authorize a remote publication-ref
push, a plugin release, marketplace publication, provider invocation, or automatic wake claim.

## TDD, preflight and verification

| Cell | Required executable behavior / finite outcome |
| --- | --- |
| T1 | The same semantic routing table selects configured profiles for at least two fictitious providers without resolver source edits or real provider/model literals. |
| T2 | Project-initial/complex-change review and normal ticket opening/independent review select only their configured semantic references. |
| T3 | Normal implementation selects its configured profile and one reviewer binding of equal-or-higher verified rank. |
| T4 | A bypass-built/malformed table, including a malformed nested route DTO, returns `ROUTING_TABLE_INVALID` before registry lookup and never throws. Empty/unmatched ordinary tables remain `ROUTE_NOT_FOUND`; no default route exists. |
| T5 | A bypass-built/malformed registry, including `ExecutorProfile.model_construct(availability=AVAILABLE, availability_evidence=None)` inside a bypass-built registry with a valid ticket-opening route, returns `PROFILE_REGISTRY_INVALID`, never `SELECTED` or an exception. Ordinary unavailable/stale/unknown selected profiles return `PROFILE_UNAVAILABLE` and never switch. |
| T6 | Canonical valid table/registry snapshots retain ordinary positive behavior. The current strict table contract classifies duplicate route keys as `ROUTING_TABLE_INVALID`; `ROUTE_AMBIGUOUS` remains a finite reserved status, not an implicit default. |
| T7 | A hard-ticket assessment selects an elevated configured implementation/reviewer pair only when `AssessmentVerification` is `INDEPENDENTLY_VERIFIED`, `CURRENT`, has a non-null distinct verification record, and exactly binds the assessment/request ticket and closure. `SELF_ASSERTED`, `UNVERIFIED`, `STALE`, `UNKNOWN`, missing record, cross-ticket, wrong-closure, duplicate-evidence, and bypass-built verification cases return `HARD_TICKET_ASSESSMENT_INVALID` without a string heuristic. |
| T8 | A lower-rank reviewer binding returns `REVIEWER_CAPABILITY_INSUFFICIENT`. Missing/unknown/unavailable owner overrides reject; a valid override remains auditable and cannot weaken review or bypass T7. |
| T9 | A bounded failed implementation/review cycle returns `MODEL_CAPABILITY_INSUFFICIENT` then `ARCHITECTURE_OWNER_REQUIRED`, never an inferred fallback. |
| T10 | Source-boundary checks reject any dispatch, receipt, host-launch, credential, process, runner, provider/model literal, or effectful callable exposure. |
| T11 | Every public DTO and enum is constructed through its ordinary validator on a success path, and rejects wrong primitive, nullability, extra field, malformed opaque reference, and bypass success forms. `model_construct`, `model_copy`, casts, `Any`, dynamic member lookup, and historical-object reuse are negative-only test inputs. |
| T12 | After the reviewer-only generator transaction, the marketplace pin names a declared payload commit containing the candidate resolver module and reachable from local `refs/heads/publication-0.4.9`; the candidate test remains development-only, and the publication pin/tree/reachability tests are green. |
| M1 | Add a default route/fallback: T4/T6 turns red; restore byte-for-byte and return green. |
| M2 | Skip canonical table validation: T4 turns red; restore and return green. |
| M3 | Skip canonical registry validation: T5 turns red; restore and return green. |
| M4 | Accept a non-current/non-independent/bypass-built assessment verification or restore string-content inference: T7 turns red; restore and return green. |
| M5 | Reverse the reviewer-rank comparison: T8 turns red; restore and return green. |
| M6 | Accept an unavailable override profile: T8 turns red; restore and return green. |
| M7 | Add a real provider/model literal to resolver source: T1/T10 turn red; restore and return green. |
| RM1 | Reviewer independently bypasses canonical registry validation for an ordinarily selected profile (not an owner-override branch): T5 turns red; restore byte-for-byte and return green. |

Strong-type preflight runs before source implementation and before review. It constructs every
success-path DTO through ordinary validators and proves exact enum, nullability, primitive,
extra-field, malformed-reference, nested-invalid, and bypass rejection. The negative-input checks
must exercise the resolver, not merely a DTO constructor. New behavior has no legacy
baseline-red claim; M1-M7 and RM1 are the authentic red evidence for test discrimination.

Run from the admitted worktree:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_executor_routing.py
py -3.11 -m mypy --strict library/local_orchestration/executor_routing.py tests/test_executor_routing.py
py -3.11 -m compileall -q library/local_orchestration/executor_routing.py
```

The reviewer re-runs the focused commands, full regression suite, strict DTO preflight, declared
boundary diff, M1-M7, RM1, and T12. A zero-red mutation is a finding; restore every mutation byte
for byte before recording green evidence.

## POC manual admission, ownership and return

The reviewer may allocate the declared contained worktree and manually give the implementation
owner identifier-only references to this committed ticket, its baseline, the revision-03 SPEC, and
the sealed Context. This is not a host task binding and does not create a
`PendingDispatchDescriptor`, issue or consume a receipt, or claim automatic delivery/wake. The
known host gap is recorded exactly above.

The implementation owner modifies only the two resolver/test files and does not commit, integrate,
push, control another Agent, create a worktree/task, invoke the publication generator, or alter
the marketplace pin. After its return, the Terra/xhigh reviewer inspects the worktree, runs review
evidence and RM1, writes the candidate source commit on the declared branch, performs the
reviewer-only publication transaction, commits the generated marketplace pin on that same branch,
then invokes `admit_document_mutation` from `main`. The ticket must already be on `main`; the gate
and reviewer counter-mutation are the POC integration evidence.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with named test/type/mutation
evidence, `BLOCKED -> HALT` with the failed cell, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes provider invocation/login, runner start, merge, push, release, or deployment.

## Completion record

- The historical candidate was independently approved and gate-integrated as source commit
  `a23861e7cba3ccadca720c028cef815e3a9d602b` plus reviewer-generated pin commit
  `e86dbae946de355f94fcadd9eefe8b5b241567cc`. The committed review is
  `doc/reviews/workstation-dispatch/04-canonical-executor-routing-code-review.md`.
- Current `main` contains the rebased, boundary-equivalent history
  `df419c27ddf263af40175abab1331238e7db9278` then
  `e2d58e720b3d126d93e2e94537a03974eb1a1e8c`; its cumulative diff is exactly
  `.claude-plugin/marketplace.json`, `library/local_orchestration/executor_routing.py`, and
  `tests/test_executor_routing.py`. `git diff --check` is clean.
- Terra/xhigh independently re-ran the focused suite (25 passed), strict `mypy`, `compileall`,
  and the payload-boundary suite (41 passed, 204 subtests). M1--M7 and the distinct RM1
  counter-mutation each produced its named failure in a disposable clone and were restored
  byte-for-byte.
- The reviewer also re-read the historical T12 transaction: its parentless payload root contains
  the resolver, has no missing or extra declared path, no non-carrier blob mismatch, and its
  carrier healing reaches the generated pin commit.
- The later Level 1 payload-topology change deliberately leaves the current `0.4.9` anchor stale
  against the new declaration. That is a current-release integrity defect owned by Ticket 08; it
  does not retroactively alter this transaction-specific P8R closure and is not claimed green here.
  No host binding, receipt delivery, runner activation, automatic wake, provider invocation, push,
  release, or deployment is asserted by this ticket.

```johnny-status
id = P8R-EXECUTOR-ROUTING-04
title = Canonical provider-neutral executor routing
state = DONE
stage = D | canonical typed route/profile resolver | DONE
stage = E | invalid-input/verification/rank/override gates | DONE
stage = M | seven implementer and one reviewer reverse mutation | DONE
stage = P | reviewer-only generated publication pin / local reachability | DONE
```
