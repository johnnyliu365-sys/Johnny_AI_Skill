# CVQ-01 | Pure qualification contracts and refusal admission

| Field | Value |
| --- | --- |
| Artifact ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01` / `IMPLEMENTATION_TICKET` / `03` |
| State / Acceptance Closure Set | `OWNER_APPROVED / TWO_PHASE_EXCEPTION_APPROVED / SCHEMA_PHASE_ADMITTED`; `CLOSURE-CVQ-01` revision `02`; behavior phase remains `PREFLIGHT_PENDING` |
| Change class / observable result | New behavior, not defect correction: one pure evaluator rejects untrusted qualification input and returns the exact tagged evaluation/report without executing work |
| Preparation authority | Owner's 2026-09-09 exact packet approval at `161c4e095697fff6e4693b8d9bfce866878277dd`, recorded at `cad0d2bca480f45c57d0598f4342636d35b1ecf2`; CVQ-01 preparation only |
| Approved SPEC | `SPEC-CONTROLLED-VERIFICATION-QUALIFICATION-20260909-01` revision `04`, LF SHA-256 `4cad6a88b9d151a05bf409f8b61bc97580e80303f58a2377cb0301815b999a1d`; behavior approved as revision 03, lifecycle-only revision 04 |
| SPEC cells | CVQ-AC01; pure comparisons/refusals of CVQ-AC02/03; report integrity/reduction of CVQ-AC09; typed roster coverage and WA-04 unavailable handling only, not native CVQ-AC04–08/10 proofs |
| PRD / CHG | `PRD-20260908-051` / `CHG-20260908-051`; current REQ-051 revision 08 LF SHA-256 `36d3f45ddd5b2453bf2c2d368567a0575c0048ec0954c42ee6e1d7c4e0b43fef`; reattachment does not add its pending CVE deltas to this qualification ticket |
| Sealed Context | `CTX-CONTROLLED-VERIFICATION-20260909-01` revision `02`, LF SHA-256 `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`; read/reference only |
| Source baseline | Original preparation `cad0d2bca480f45c57d0598f4342636d35b1ecf2`; current readmission parent `2b4903c1995b0b1a1b2cbafc90aca0daf0cea5de`. Dispatch pins this document's final control commit as the clean worktree baseline; no integration claimed |
| Control owner / reviewer | Current-session `SUPERVISOR_REVIEWER`, semantic profile `ticket-review`; human owner retains ticket approval and effects |
| Implementation allocation | Reused `cve_wire_implementer`, semantic profile `implementation-standard` (Luna/xhigh), reviewer `root`; new bounded view `cvq-01-schema-v01`; previous CVE-01A allocation released without changing its candidate |
| Worktree / branch binding | Repository-contained `.worktrees/cvq-01` / `codex/cvq-01`; reviewer creates from this revision's exact committed control SHA, then reads back containment, branch, HEAD and clean state before dispatch |
| Language / strict checker | Python 3.11, strict immutable Pydantic boundary; `mypy==2.3.0 --strict` from the committed development dependency plan |
| Delivery / resources | POC / HIGH_ASSURANCE inherited from approved workload; one implementer, one subsequent required reviewer-owned adversarial helper; no parallel implementation |
| Lifetime / return | Same-lifetime native dispatch plus `wait_agent`; bridge, runner, queue, receipt, descriptor and host workspace readback `NOT_REQUIRED`. Return `ImplementationReturn.COMPLETED`, `BLOCKED` or `CHANGE_DETECTED` |
| XSS / external effects | `XSS_NOT_APPLICABLE`: pure Python values and injected read ports, no renderer. No VM, host, process execution, provider, target adoption, policy write, integration, push, package publication or installation |

## Canonical inputs and bounded lookup

- [SPEC](../../spec/controlled-verification-qualification.md), sections 2–3 and 6–8 are the
  public contract; section 4 supplies limit semantics, not authority to run those experiments.
- [Sealed Context](../../../doc/context/controlled-verification/main.md),
  [architecture](../../../doc/context/controlled-verification/architecture-r01.md),
  [approval record](../../../doc/context/controlled-verification/grill-r01.md), and
  [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md).
- [Profile revision 03](../../../doc/runbooks/dispatch-model-profile.md),
  [ticket decomposition](../../../skills/johnny-project-takeover/references/ticket-decomposition.md),
  [type preflight](../../../skills/johnny-project-takeover/references/specification-ticketing.md),
  [review entry](../../../CodeReview.md), and
  [adversarial review](../../../skills/johnny-project-takeover/references/adversarial-review.md).
- [PITFALL D8](../PITFALL-REGISTER.md): finalize leaf, hash LF bytes, update parent/root, rehash.
  Historical UIX-02 collection/closure failures are not authority to manufacture baseline-red.

No entire Workflow/library/history load. Router remains the selected existing
`workflow-router-poc` at `b697738d009db37318ebc8762107ef8329e014db`; this ticket neither enlarges
its central contracts/router nor creates a competing workflow engine. Its opaque metadata grammar
is read from `library/workflow_router/contracts.py:14–20`, not guessed from a natural-language ID.
WA-04 is separately owned by the approved workflow-adoption SPEC. No WA-04 implementation ticket
is indexed in the inspected plugin-adoption partition at this baseline; missing adapter evidence
must stay unavailable, not trigger work on that feature.

## One closure, not a native executor

Given an independently resolved approved qualification manifest, requested serialized values,
and injected prerequisite/evidence observations, the public evaluator produces exactly one
`QualificationEvaluation`. A valid pure result may qualify its pure declared scope. A missing VM
does not block that pure result; dependent native/host results retain their refusal/unavailable
slots. Malformed, forged or incomplete evidence cannot qualify a broader scope.

This is a complete input → validation → comparison → report projection slice. It is not a
model-only layer waiting for tests later. Native execution, process supervision, attempt-ledger
storage, actual roster discovery, recovery settlement, CLI installation and final product
enforcement are explicitly outside it. The tests prove a pure admission boundary, not that an
unrestricted Agent cannot bypass the library or that an injected fake is protected at runtime.

Decomposition assessment: one effect-free decision boundary, one implementation owner and one
finite observable result. The internal responsibilities below share the same input/result contract
and are accepted together. `READY_LOW_MODEL` is the intended admission decision only after the
actual type/constructor/environment preflight; it is **not claimed by this draft**. The existing
HIGH_ASSURANCE review requirement does not silently change the implementation profile. A future
named capability gap returns for assessment instead of an automatic model elevation.

## Public seam and constituent ownership

Proposed ticket-level API, using the SPEC's closed contracts:

```text
evaluate_qualification(
    request_ref: OpaqueMetadataId,
    manifest_json: str,
    report_json: str,
    approved_manifest_port: ApprovedManifestPort,
    prerequisite_evidence_port: PrerequisiteEvidencePort,
    evidence_observation_port: EvidenceObservationPort,
) -> QualificationEvaluation
```

The three ports are explicitly injected into one invocation, with no service locator, ambient
configuration, callback discovery or executor dependency. The approved-manifest port is bound by
its composition owner to one expected approval/snapshot, not selected by the caller's PASS, hash
or correlation ID. `request_ref` remains correlation only. Port responses are typed, immutable
resolution alternatives; no `dict[str, Any]`, truthy string or exception-as-success protocol.

- `ApprovedManifestPort` resolves the expected source and owner-approved manifest or an
  unresolved/conflicting approval. A missing/conflicting approval maps to APPROVAL_UNRESOLVED;
  any requested source/manifest disagreement maps to SOURCE_MISMATCH. Compare the complete
  approved request binding, not just the self-reported digest. A manifest digest identifies the
  independently resolved approved artifact/snapshot; do not hash a self-referential DTO to mint
  authority or treat a candidate's computed hash as an approval record.
- `PrerequisiteEvidencePort` resolves the exact SPEC key to FOUND(binding), MISSING or CONFLICTING.
  Resolve the required key set from approved case kind first; an omitted required key in caller
  input cannot remove a guard. Check actual key/revision/digest/disposition against approved
  requirements. Do not accept another scope, latest observation, duplicate or first match.
- `EvidenceObservationPort` independently authenticates every required case/check/cleanup/roster
  evidence binding and supplies rejection-evidence references. It must not merely echo a caller's
  authenticity boolean. An unauthenticated or unresolvable evidence record cannot qualify.
  Port adapters own mapping operational failure into these finite resolution results; this ticket
  implements pure protocols/fakes, not production filesystem/cryptographic authenticity adapters.

The evaluator validates external JSON at entry; parse/schema failures produce the appropriate
MANIFEST_REFUSED or REPORT_REJECTED variant. It never creates a DTO through `model_construct`,
`model_copy(update=...)`, casts, assignment or reused invalid objects to obtain success. Tests
of hostile malformed values may use negative fixtures only and must not masquerade as positives.

Implement all SPEC section-2 alternatives through ordinary constructors and JSON round trips:
QualificationScope, CapabilityKey, QualificationPrerequisiteSet, QualificationCase,
QualificationManifest, PureContractBinding, NativePreLaunchBinding, LaunchObservation,
CapabilityObservation, CaseResult, QualificationReport and QualificationEvaluation, with their
constituent enums and records. SPEC section-6 roster contracts are independently typed. No
LaunchObservation is required before launch or invented for a pure/refused/absent case.

The public output follows the exact failure precedence in SPEC section 2. Structural report
failure is REPORT_REJECTED, not an accepted report with zero tests. An accepted report may still
be failed/incomplete/unavailable. Pure evidence never satisfies native capability aggregation;
discovery coverage never substitutes for post-enforcement coverage. No attempt state is advanced
and no production RecoveryRecord resolver is implemented by this ticket.

## Source responsibility map — proposed exact writable boundary

All paths below are new and restricted to this ticket. The SPEC's proposed two entry modules
remain facades; constituent files separate independent responsibilities, without a line-count
threshold. No module outside this table may be changed by implementation.

| File under `library/controlled_verification/` | Sole responsibility / permitted internal dependencies |
| --- | --- |
| `qualification_values.py` | Named strict primitive values and finite vocabulary; standard typing/enum plus Pydantic only |
| `binding_contracts.py` | Pure/native/prelaunch/postlaunch value shape; values only |
| `prerequisite_contracts.py` | Requirement/key/binding/resolution algebra; values only |
| `roster_contracts.py` | Exact host/category/entry/discovery/enforcement value shape; values only |
| `manifest_contracts.py` | Scope/cases/limits/ordered manifest; values, bindings, prerequisite and roster contracts |
| `report_contracts.py` | Case observation/cleanup/report/evaluation alternatives; values, bindings and roster contracts |
| `qualification_contracts.py` | Explicit public contract re-exports only; no validators/use cases/I/O |
| `qualification_ports.py` | Three read-only typed protocols and resolution values; contracts only |
| `prerequisite_admission.py` | Required-key selection and exact evidence comparison; contracts/ports only |
| `roster_admission.py` | Typed exact-set/key/observation coverage checks; contracts/ports only |
| `report_admission.py` | Exact expected-cell/check/evidence coverage and outcome reduction; contracts/ports, roster admission only |
| `qualification_admission.py` | Public decode/admit/compose entry; contracts/ports plus three admission units; no copies of their predicates |
| `__init__.py` | Explicit public exports only, no wildcard/initialization effects |

Test files: `tests/test_verification_qualification_contracts.py`,
`tests/test_verification_qualification_admission.py`,
`tests/test_verification_qualification_roster.py`,
`tests/test_verification_qualification_boundaries.py`, and
`tests/verification_qualification_fixtures.py` (ordinary immutable data/fakes only).
Tests must invoke actual public entry/constructors, not copied gate logic.

Ticket-scoped AST tests mechanically enforce that dependency DAG, forbid cycles/reverse imports,
facade logic/wildcards and runtime calls to filesystem/process/network/VM/configuration APIs.
Also reject `Any`, cast/bypass construction, dynamic import/eval/exec/getattr/setattr and hidden
module-level mutable service state. Static checks supplement—not replace—behavioral gate tests.
This checks this package's declared architecture; it is not a new generic responsibility validator
or a substitute for WA-04. Mechanical splitting that leaves reversed dependencies still fails.

An element reference may be created only after ticket approval at
`modules/element/python/controlled-verification/cvq-01/README.md`, with direct-child index rows in
`modules/element/python/controlled-verification/README.md` and `modules/element/python/README.md`.
It points to source/contracts/tests; it contains no production copy. The implementation owner may
write those exact element paths as its documentation boundary, but not shared Context, SPEC,
ticket, ticket registry, skills, publication manifests or global rules.

## Finite Acceptance Closure Set revision 02

Each row is an exact named test group. Enumerated subcases are separate subtests with their
variant/field in unreduced output; implementation cannot omit a listed case or add workload runs.
`CQ01` through `CQ12` are new-behavior cells: initial baseline-red is N/A, not a claimed import
error. Discriminating reviewer reverse mutations below remain mandatory.

| Cell / test name suffix | Exact observable predicate and bounded cases |
| --- | --- |
| CQ01 `test_public_constructor_roundtrips` | Ordinary constructors and JSON round trips for every public DTO and every enum/tag listed above; include mixed pure/native manifest, all four CaseResult tags, both EXECUTED observation tags, three cleanup tags, three evaluation tags and all four report outcomes. Pure/native/postlaunch fields remain disjoint. |
| CQ02 `test_strict_boundary_rejection` | Required-field omission/null and extra fields reject. Strict integers reject true, false, 1.0 and string 1; positive revision/capacity/duration fields reject zero/negative; nonnegative discovery counters admit zero and reject negative (unknown counts above zero cannot qualify discovery); explicit zero-only retry/container/build-worker controls admit exactly zero and reject nonzero. Empty/space/invalid-case/Unicode/separator opaque ID; illegal enum; duplicate case/key/check/entry/alias/category IDs; incompatible binding/kind, cleanup/pure and tag/payload combinations reject. Every public positive fixture tests each required-field omission and one undeclared field, with no transform-to-valid input. |
| CQ03 `test_approval_and_plan_drift` | Missing/conflicting approval; separately alter project, baseline, manifest revision/digest, fixture/executable/dependency identity, argv, cwd, environment, order/count/load, policy owner/revision, resource plan/scope, evidence owner/destination. Wrong binding is refused before any evidence-derived qualification; unchanged approved manifest is the control. Same run count with one-loaded → all-loaded also refuses. |
| CQ04 `test_prerequisite_exact_resolution` | Exact PROVEN result admits comparison; MISSING, CONFLICTING, wrong key kind/scope/capability/adapter, wrong observation revision/digest, FAILED and UNAVAILABLE produce the exact prerequisite refusal/detail. Conflicting later record cannot be masked by an earlier match. |
| CQ05 `test_case_kind_prerequisite_closure` | PURE_RULE works without lab; WA-04 SOURCE_PROPERTY requires WA04_ADAPTER; each native case kind has the exact SPEC prerequisite set. For each required kind independently omit it. REAL_HOST_PROPERTY needs discovery, not enforcement evidence; trusted discovery does not require its own result. Pure resource tests never become native proof. |
| CQ06 `test_report_coverage_rejection` | Missing/duplicate/extra case, wrong manifest/binding, missing/duplicate/extra expected check, unauthenticated observer/evidence and invalid shape return exact REPORT_REJECTED detail; every refused/unavailable/unrun case still occupies one expected slot. Empty collection is never a pass. |
| CQ07 `test_outcome_precedence` | Separately exercise failed check, source/approval refusal, cleanup/refusal RECOVERY_REQUIRED, each incomplete reason, each NOT_RUN reason, each unavailable reason and each prerequisite/resource/host refusal. Test every ordered pair of the four outcome classes to pin FAILED > INCOMPLETE > UNAVAILABLE > QUALIFIED; all-pass pure scope qualifies only pure rules. |
| CQ08 `test_launch_cleanup_time_order` | Pure/refused case has no launch identity; actual native execution requires bound launch observation and valid cleanup or recovery-required. Wrong attempt/binding/observer and invented future identity reject. Missing cleanup cannot be NO_LAUNCH; failed test plus confirmed cleanup stays failed. |
| CQ09 `test_roster_discovery_closure` | All seven categories each occur once; ABSENT has absence evidence but no invented entry/alias/disposition. PRESENT is nonempty, exact key and unique entry/alias set. Missing/extra/duplicate/wrong-key entry or alias, category omission, unknown>0, unobservable>0 or unauthenticated absence cannot qualify discovery. Include multiple present entries in one category and client-reachable channels. |
| CQ10 `test_roster_enforcement_separation` | Valid discovery alone does not prove enforcement. Each present entry needs actual same-key disposition/oracle observation; missing/failed/wrong-key observation refuses coverage. ABSENT requires no fake tool execution. CODEX_CLI, CODEX_DESKTOP and CLAUDE_CODE_CLI are not interchangeable. |
| CQ11 `test_architecture_dependency_gate` | Actual package AST obeys the responsibility DAG and prohibited effect/dynamic/bypass constructs; explicit facades only. A forbidden dependency remains rejected when moved into a helper. No source-size threshold or coupling-by-file-count heuristic. |
| CQ12 `test_public_entry_smoke_and_repeat` | Real public evaluator with ordinary fake ports: valid pure-only accepted; pure pass plus prerequisite-refused native slot accepted as CAPABILITY_UNAVAILABLE; malformed manifest refused; forged/incomplete report rejected. Repeat identical input gives identical value, no implicit retry/claim/launch/write. Fake observation resolves changed evidence explicitly rather than ambient state. |

First-red slots for all CQ cells: `NOT_APPLICABLE_NEW_BEHAVIOR`. Constructor/type preflight,
green commands, output digest/ref and restoration checks remain `NOT_RUN`, never inferred from
SPEC approval. No existing baseline can collect these not-yet-created tests; don't demand named
red on this source baseline or copy an old schema solely to simulate that claim.

## Reviewer counter-mutation plan

For each CQ predicate, name the actual candidate symbol/validator during preflight and retain its
exact bytes. At review run one bounded weaken → named red → exact restore → green sequence per
independent predicate; matrix loops have a finite count determined by the committed public field/
enum list, not model-selected repetitions. Missing symbol/cell mapping blocks that sequence.

| Mutation family | Required red |
| --- | --- |
| Remove ordinary-constructor variant validation or round-trip field preservation | CQ01/CQ02's affected variant/field |
| Skip one requested-versus-approved binding component (including loaded-slot identity) | CQ03's exact component |
| Ignore one prerequisite comparison/disposition or accept the first conflicting match | CQ04's affected tuple/detail |
| Remove one mandatory case-kind prerequisite or treat pure evidence as native | CQ05's affected kind |
| Remove one expected-set/evidence-authenticity/binding check | CQ06's affected case/check/evidence |
| Swap one neighboring reduction priority or collapse an incomplete/unavailable reason into pass | CQ07's corresponding pair/reason |
| Permit missing/wrong native launch or cleanup evidence | CQ08's affected time-order/cleanup cell |
| Skip one roster set/category/key/absence/unknown-count guard | CQ09's corresponding dimension |
| Substitute discovery for enforcement, omit an entry observation or alias two host surfaces | CQ10's affected entry/surface |
| Add a forbidden dependency through a renamed/re-exported helper; weaken the AST guard separately | CQ11 rejects the bad dependency; guard weakening makes that rejection assertion red |
| Short-circuit the public evaluator to accept caller output or cache a previous result | CQ12 and the corresponding CQ03/CQ06 path |

The reviewer must choose at least one entry path not used in the implementer's own examples and
record unreduced red/restored-green output against the exact candidate SHA. Zero red is a finding.
These are source mutations on the owned candidate/reviewer snapshot only, not resource stress.
An initial full-closure review plus one correction review is the limit; no automatic third loop.

## Verification and environment admission

Resolve one isolated approved development Python before dispatch, then use its exact path in all
recorded commands. `requirements-dev.txt` is the dependency source; no dependency bump or package
install is authorized by this proposal. The physical runtime Python inspected on 2026-09-09 was
`C:/Users/GameBoy/AppData/Local/JohnnyRouter/venv/Scripts/python.exe`; it reported no installed
`mypy` module. Do not alter the installed runtime to turn that check green. Qualified dev Python
and public-constructor preflight are presently `PENDING`, not architecture/VM blockers.

From the exact ticket worktree, with `$cvqPython` already resolved and recorded:

```powershell
& $cvqPython -B -m mypy --version
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_admission.py tests/test_verification_qualification_roster.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_admission tests.test_verification_qualification_roster tests.test_verification_qualification_boundaries
& $cvqPython -B -m unittest -v tests.test_workflow_intensity
git diff --check
```

The full CQ suite includes CQ12 smoke and CQ11 source/build-import checks. This is the complete
new-package suite plus the existing profile regression, not a claim that unrelated repository
tests or native capabilities passed. Record any integration-required whole-repository suite
separately before integration; it is not permission for containers/VM/CPU load from this ticket.
No new linter/formatter toolchain is introduced; AST boundary gate and diff validation are explicit.

Proposed source-verification schedule: one constructor/strict check, one complete CQ green suite,
one regression run, then the declared finite mutation sequences. One process at a time, zero
automatic retry; 60 seconds per source command, 1,200 seconds total for the initial validation
pass, no CPU burners, VM, containers or build workers. A timeout stops with preserved output;
it never enlarges timeout or converts the run to five stress iterations. Correction runs only
the changed closure plus smoke once; newly discovered workload needs a displayed amended plan.
These are limits on test invocation, not a claim of qualified OS-enforced CPU/disk containment.

## Adversarial helper, evidence and return

After implementation's immutable candidate exists, reviewer binds an `AdversarialReviewPlan` to
that SHA and CLOSURE-CVQ-01 revision 02, REQUIRED, NO_EXTERNAL_EFFECT. Select SPEC_GAP,
BOUNDARY_DATA, STATE_TRANSITION, ERROR_PARTIAL_FAILURE, AUTHORIZATION, CONSISTENCY, IDEMPOTENCY,
REGRESSION and OBSERVABILITY. Concurrency is in-process deterministic input comparison only;
native concurrent launch/recovery and deployment are outside this ticket. Isolation disposition
must be actually read back, never guessed from a read-only prompt. Required unavailable evidence
blocks approval. The helper supplies finite findings, not final approval and no code changes.

Use one exact-ticket native implementation owner. Reuse it for the allowed correction; do not
send another owner to implement the same work. Wait through `wait_agent`, never progress/status/
transcript polling. Parent reviewer independently checks code, runs counter-mutations and owns
the verdict. No reviewer self-implementation fallback. No sibling/reviewer source edits in the
implementation worktree outside an expressly bound review mutation and exact restoration.

On completion the implementation owner creates the candidate source/element commit in its own
worktree (after admission), then returns COMPLETED with candidate SHA, changed paths, CQ/type/
regression/smoke results and immutable evidence refs/digests. It never reports review/integration.
BLOCKED names the exact missing evidence/capability. CHANGE_DETECTED names the frozen contract
that cannot be implemented without an upstream decision; no hidden rewrite.

Reviewer-owned handoff/progress evidence will be a separate docs-only leaf under the existing
progress tree, rooted and hashed at actual creation; this proposal creates no empty report or
fabricated completion. Candidate commit, review plan/result, mutation results, restoration and
integration evidence are all `NOT_RUN / NOT_CREATED`. Source rollback is an additive reviewed
revert before product adoption, not reset/deletion; no persistent data or external recovery effect.
Publishing any changed shipped library remains a separately authorized release action.

## Revision-01 admission request — historical

Opening this leaf is `ACTION_COMPLETED` for docs-only ticket preparation. Architecture/Context/
SPEC approval is resolved; **this new exact ticket Closure revision 01 is not yet owner-approved**.
Do not allocate, dispatch, implement or integrate from a proposal.

One next owner confirmation may authorize this exact ticket, a bounded source-only schema/type
preflight and—only when that preflight succeeds—one same-lifetime implementation dispatch.
It must bind the committed ticket revision/digest, clean contained worktree/baseline and the
registered available profiles. A missing checker or failed constructor is a named prerequisite,
not grounds to invent a receipt/runner or to claim the ticket ready. Native operational authority
remains excluded. Revision-01 return was `WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING`.

## Actual owner approval and preflight — 2026-09-09

The human owner's next `核准` approved the exact revision-01 ticket at
`2d3b58156002cf52239dcc24c694d085edf7ce63`, LF SHA-256
`99dfd59f9baa44f026b3b25f0f95bb8c1ad8cc34c6d3b405cc10f08d7643a3d8`.
It authorized bounded environment/type preflight, followed **only on success** by one
implementation-standard same-lifetime dispatch and parent review. That confirmation is consumed
as approval, not reopened as an unanswered ticket question. It grants no VM/integration/push/
publication effect. The original approved source boundary and CQ01–CQ12 remain unchanged above.

All checks below ran on that clean candidate. Main remained
`b697738d009db37318ebc8762107ef8329e014db`; no implementation worktree or Agent was allocated.

| Check | Actual evidence / disposition |
| --- | --- |
| Ticket tree | Unique leaf/partition edges and LF hashes matched; ticket references matched the three exact SPEC/Context/REQ digests; all ticket local links resolved; exactly CQ01–CQ12 found |
| Development interpreter | `Get-Command python,py,mypy` and `py -0p` resolved `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe`; Python 3.11.9, mypy 2.3.0, Pydantic 2.13.4 |
| Isolation diagnostic | A read-only `-I -B` interpreter probe returned `isolated=1`; this proves Python isolated-mode flags only, not a qualified protected VM/OS lane or an isolated project dependency environment |
| Other installed runner | pytest 9.0.3 differs from requirements-dev.txt's 9.1.1. It was not used by these unittest checks; no full dev-environment conformance or repository-wide suite PASS is claimed |
| Tool changes | None. No install, dependency bump, runtime/host setting change, or download; the Router runtime Python was not modified |
| Existing regression | Exact development Python `-B -m unittest -v tests.test_workflow_intensity`: six tests passed; output read unreduced; existing profile behavior only, not CVQ proof |
| New contracts/tests | `Test-Path -LiteralPath` returned false for `library/controlled_verification` and all five declared CQ test/fixture files. No new constructor/schema/AST/mutation test exists on this baseline |
| Dispatch/type preflight | `HALT / TICKET_SCHEMA_INVALID`; not passed, not dispatched. The two control-plane findings below must be resolved first |

Existing regression's unreduced named result (no CVQ cell is included):

```text
test_assessment_requires_committed_evidence ... ok
test_every_signal_floor_is_exact ... ok
test_forged_assessment_cannot_derive_an_intensity ... ok
test_fully_clean_assessment_is_the_only_compact_shape ... ok
test_highest_floor_wins_over_any_clean_mix ... ok
test_normalized_goal_carries_an_optional_assessment ... ok
Ran 6 tests in 0.004s
OK
```

The names above are in `tests.test_workflow_intensity.WorkflowIntensityDerivationTests`.
This compact transcription indexes the directly read tool output; it is not a substitute for
future unreduced CQ red/green evidence.

### Batched preflight findings — parent owns the ticket defect

1. **CVQ-PF01 / CQ02 zero-value conflict.** Revision 01 line 175 puts integer zero in an
   unconditional rejection list. Approved SPEC revision 04 section 6 (lines 302–306) instead
   requires nonnegative unknown/unobservable counts and exactly zero for complete discovery;
   section 4 explicitly uses zero retries/containers/build workers. The predicate must distinguish
   positive capacity/revision fields from nonnegative counters and literal-zero controls. The
   ticket compiler overgeneralized the boundary row; this is not an implementation defect.
2. **CVQ-PF02 / new-contract pre-dispatch ordering.** The canonical
   [specification-ticketing reference](../../../skills/johnny-project-takeover/references/specification-ticketing.md),
   lines 63–77, requires every public constructor and gate mutation **before dispatch**. These
   new public contracts/gates are the implementation output and do not exist yet. The
   [role boundary](../../../skills/johnny-project-takeover/references/implementation-authority.md),
   lines 8–11, also forbids reviewer production-source/test implementation without a ticket-scoped
   owner override. A JSON/prose/schema copy would not prove the actual public constructor.
   Neither an import error nor an old unrelated DTO is a legal success substitute. Current
   same-lifetime runner/receipt/host-readback exemptions do not resolve this ordering defect.

PITFALL C14 was read: demanding named evidence where the named contract cannot exist/collect is
the same structural family. No missing runner, guest admin, host gateway or slow implementer is
the cause. No implementation correction cycle has been consumed and no helper review PASS exists.

## Historical revision-02 proposal — approved below, not a second active rule

This is a bounded proposal, not active permission and not a change to plugin reference prose.
It preserves all SPEC behaviors, the exact final CQ01–CQ12 closure and every final review gate.

A. Replace only CQ02's integer sentence with: strict integer fields reject booleans, floats and
strings; positive revision/capacity/duration fields reject zero and negative values; nonnegative
discovery counters admit zero as a valid constructor value and reject negatives; unknown counts
greater than zero cannot qualify discovery; explicitly zero-only retry/container/build-worker
controls admit exactly zero and reject nonzero values. Each class has its positive and negative
constructor fixtures. The remaining CQ02 dimensions are unchanged.

B. For **new CVQ-01 contracts only**, explicitly authorize this two-phase ordering instead of
claiming the universal pre-dispatch constructor rule has already passed:

1. Parent validates the frozen ticket/source references and resolves a separate exact development
   environment. Then allocate the one repository-contained CVQ-01 owner/worktree using the
   already selected implementation-standard profile. This is a restricted contract-construction
   phase, not admission to implement the evaluator or native effects.
2. The same implementation owner defines ordinary immutable contracts/protocols and their
   constructor/round-trip/strict-boundary/dependency tests within the existing declared files.
   No `*_admission.py` behavior, native executor, install or provider work. Return a committed
   schema candidate; parent waits through `wait_agent`, not status polling.
3. Parent runs the actual candidate's CQ01/CQ02 and applicable contract DAG checks, strict typing
   and bounded counter-mutations. This is a named schema preflight, not final code-review approval.
   Failure remains blocked and cannot unlock phase 2. No fabricated future-gate mutation is
   required; not-yet-implemented admission predicates stay explicitly pending.
4. Only after that real preflight passes, parent resumes **the same owner** for the evaluator,
   remaining behavior tests and element evidence. No second owner or new architectural decision.
   All original CQ01–CQ12, each behavior's reverse mutation, required adversarial helper and
   parent final review remain mandatory before any approval/integration. The normal one initial
   plus one correction review limit is unchanged.

Phase-1 writable production subset: `qualification_values.py`, `binding_contracts.py`,
`prerequisite_contracts.py`, `roster_contracts.py`, `manifest_contracts.py`, `report_contracts.py`,
`qualification_contracts.py`, `qualification_ports.py`, `__init__.py`, under the already declared
package. Its test subset is the declared contracts/boundaries/fixtures files. Other ticket paths
remain untouched until successful schema preflight. The package dependency graph stays the same.

No general waiver of strong types, provenance, boundary checks or review is proposed. No new
ticket/parallel contract owner, production behavior choice, line-count threshold, second workflow
engine or user-global instruction is introduced. No implementation or source mutation is
authorized until the human owner approves this exact closure/ordering exception.

Historical revision-02 return: `ACTION_COMPLETED` for approval/preflight documentation, then
`HALT / TICKET_SCHEMA_INVALID / TICKET_DEFECT`; owner decision is required only for the named
closure-02 two-phase exception, not a repeat of the approval already recorded above.

## Owner exception approval and current schema phase — 2026-09-18

The owner explicitly replied **「核准兩階段例外」** after the reviewer described contract/test
construction by Luna, actual parent preflight, then behavior by the same owner. The decision
resolves CVQ-PF02 for this ticket only. It was requested against control commit
`2b4903c1995b0b1a1b2cbafc90aca0daf0cea5de`, ticket document 02 LF SHA-256
`65716d9d45bfc99c8519d5ed1f06edc199cb3acc83eee6636b15ca3cf4c42431`.
The already-described CQ02 zero-domain repair is compiled from the approved SPEC's explicit
nonnegative/zero-only fields; it adds no product behavior or global exception. All final CQ01–CQ12
and review obligations remain. The pending CVE protocol SPEC is not approved by this decision.

Current action is SCHEMA_CONSTRUCTION only. Its production allowlist is exactly the nine files
listed in the phase-1 subset above; tests are exactly contracts, boundaries and fixtures.
No admission/use-case module or element index is created during this phase. Constructor value
invariants and protocol shape belong here; actual approved-source/prerequisite/evidence resolution,
report reduction and native effects remain outside phase 1. Facades export only existing
phase-1 contracts/protocols, not a fake evaluator or placeholder success implementation.

Read the current ticket contract sections, approved SPEC, bounded source grammar and applicable
implementation rules; historical preflight/review/conversation bodies are not work input. Close
the completed CVE-01A input view before using `cvq-01-schema-v01`. The prior source candidate
`d0c93111ee1ae6a7f98779cc64b8e8ba52a62d03` stays unchanged on its original branch. Reuse of the
Agent does not imply erasure of its memory or OS isolation; only this ticket's exact input is sent.

Fresh development readback: Python 3.11.9 at
`C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe`, mypy 2.3.0, Pydantic 2.13.4.
This is the separate existing development interpreter, not JohnnyRouter's runtime interpreter.
No dependency installation is performed; no full dependency-environment or OS confinement claim.
Stage-1 commands, from the bound worktree, use that executable as `$cvqPython`:

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_boundaries
git diff --check
```

Run only the existing phase-1 package/constructor/dependency checks; later admission files do not
have to exist or be imported for this phase. Preserve the ticket's one-process, 60-second command
and 1,200-second pass bounds, without unchanged-input retries, extra suites, stress or model
polling. Source fixes may be verified against their changed candidate; report the runs honestly.
Return committed candidate, exact changed paths, named CQ01/CQ02/contract-CQ11 checks and results,
findings/deviations and an explicit `SCHEMA_PHASE_ONLY` marker. COMPLETED here means this phase,
not ticket completion or permission to enter behavior.

Parent preflight uses ordinary constructors/JSON round trips, strict typing and bounded independent
mutations of the actually implemented contract predicates with exact restoration. Behavior
predicates remain NOT_IMPLEMENTED, not a false PASS. Only a recorded successful preflight admits
the same owner to phase 2; a failed one cannot. Final independent adversarial review remains later.
Typed route: APPROVAL_GRANTED -> AUTO_CONTINUE / SCHEMA_CONSTRUCTION under this exact exception;
no native/provider/installation/integration/release effect is added.
