# CVQ-01B2 | Schema call and receiver admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B2` / `IMPLEMENTATION_TICKET` / `09` |
| State / closure | `CHANGES_REQUESTED / CORRECTION_PENDING_RESOURCE / NOT_INTEGRATED`; `CLOSURE-CVQ-01B2/02`; section13 is current; closure01 exhausted |
| Preparation authority | Owner's 2026-09-21 approval of [B convergence01](../../../doc/reviews/controlled-verification/cvq-01b-convergence-proposal.md) at797c15db, LF0308388788c4a6a6c79ce4dd256b72bb5a231a498357a0038f305680e46f0f94; drafting only |
| Observable result / change class | Schema calls admit only exact permitted static binding and guarded receiver; `PRODUCTION_BEHAVIOR / DEFECT_CORRECTION` |
| Dependency / baseline | [B1](cvq-01b1-namespace-import-admission.md) document02/closure01 in this proposal commit; actual APPROVED candidate SHA and review/index must be bound before dispatch; never substitute7171f41 as accepted B1 |
| Owner / reviewer / workspace | Retained `cve_wire_implementer` / `root`; sequential same `.worktrees/cvq-01`, `codex/cvq-01`; new view `ctx-cvq-01b2-closure01` |
| Profile / language | POC / HIGH_ASSURANCE; one implementer, one bounded evidence-only helper; Python3.11 / strict mypy |
| XSS / effects | XSS_NOT_APPLICABLE: AST-only local test support; no browser/UI/SQL/secret/provider/host/native effect; no source execution, integration, push, release or installation |

## 1. Exact authority and immutable input

- [SPEC](../../spec/controlled-verification-qualification.md) revision07, section11.3,
  LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`.
- [Wire inventory](../../spec/controlled-verification-qualification-wire.md) revision03,
  LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`.
- `PRD/CHG-20260908-051`; [REQ](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md)
  revision11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`.
- [Sealed Context](../../../doc/context/controlled-verification/main.md) revision02,
  LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`; READ_REFERENCE only.
- Above bytes resolve at control commit `797c15db0bcb39d1e015bb676f1722a9e138a6e7`.
  [Bundled model profile](../../../skills/johnny-project-takeover/references/dispatch-model-profile.md)
  `JOHNNY-DISPATCH-DEFAULTS/01` at that commit, LF
  `8bcac03837177959cc680e31985ea280693bb333360314b40e43cf7b39b67cc4`.
  Retained Luna/xhigh implementation-standard; root sole ticket-review; retained
  Terra/xhigh evidence-only helper. No automatic elevation, replacement seat or delegation by owner.
- Accepted A1/A2/A3 source `485d882f578f84dac1c975b32ced2a4ae6e7d43a`;
  [A3 review04 section7](../../../doc/reviews/controlled-verification/cvq-01a3-evidence-admission-code-review.md#7-closure02-final-review-and-combined-a-admission--2026-09-20)
  at `fc0dd2e1402fbc7b4bc6f51bebcda8e62925ba21`, LF
  `6271409116dc700e01deab1946eb027f43a65cdaffc2671669173baa8bc9412d`.
  Preserve this acceptance; do not rerun its completed mutation campaigns.

## 2. Single responsibility, scope and call contract

B1's import/DAG/exact-origin/finite-type contracts and all accepted A contracts are preserved.
This closes B-F02 and the SG09/12/18 alternatives in B-F04. B3 owns statements/classes,
annotations and remaining corpus composition; passing B2 does not approve that grammar.

| Writable path under tests/ | Allowed symbols/responsibility |
| --- | --- |
| verification_qualification_source_symbols.py | Scope/name binding order, callable aliases, receiver guard facts and helper graph only; preserve B1 import/export/module graph semantics and finite enums |
| verification_qualification_source_gate.py | _check_calls and call/recursion/callable-return parts of _check_functions, thin wiring only; no body/class/module/facade expansion |
| verification_qualification_source_corpus.py | SG09–13/16–18 and SG19 recursion rows, SGP04/05 and necessary valid surrounding literal declarations; independent IDs/counts/locations |
| test_verification_qualification_boundaries.py | B2 assertions through existing gate plus preservation calls; no duplicate policy/resolver |

Policy module is READ_ONLY. All production, A tests/catalog/fixtures and B1 owned row semantics
are READ_ONLY; no new support owner/framework/dependency. Internal refactoring cannot change
accepted B1 meaning. A required out-of-scope contract change is CHANGE_DETECTED.

Only SPEC11.3 schema builtins, listed schema constructors/decorators, exact catalog DTO/enum
constructors and directly bound typed acyclic module-local helpers may be called. Schema phase
has **no** model_validate/model_validate_json/model_dump/model_dump_json or port.resolve calls,
even with a real catalog class or one of the three correctly typed port parameters.
Behavior-phase imports/calls and receiver-positive controls remain forbidden in this closure.

This is the already-approved **schema phase**, not a denial of SPEC's later behavior surface:
SPEC07 section12 requires schema preflight before behavior, and original B05 sections2–3
explicitly excludes behavior-phase calls/positive controls. The analyzer has no caller-selected
phase switch. A future behavior ticket must separately admit that surface; this ticket does not.

Callee resolution uses lexical scope and statement order, not global name spelling or ast.walk
ordinal as execution order. Resolve imported aliases back to B1 origins. Parameter/local
shadowing and callable assignment/return cannot inherit allowed identity. Helper graph includes
unused bodies and detects direct/mutual recursion without executing source.

Mapping.get requires the actual unshadowed typing.Mapping and builtin isinstance, exact same
receiver binding, immediate local true-branch guard, and no intervening reassignment on the path.
Else, after-branch, unrelated guard, inherited ancestor guard and same-name methods do not prove
this. Same-line, unpacking/loop assignment targets and local shadowed guard names are not escapes.
Validators/discriminator functions undergo the same checks, never a trusted-name exemption.

### Fixed analysis seam

`SourceUnit(module: SourceModule, text: str)` and
`SourceViolation(module: SourceModule, line: int, column: int, rule: SourceRule)`
are immutable. `inspect_sources(tuple[SourceUnit, ...]) -> tuple[SourceViolation, ...]`
is the real test entry, not a caller-supplied resolver/policy. SourceModule is the exact nine
constituents in SPEC's approved package; SourceRule remains SOURCE_SET, SYNTAX_INVALID,
UNSUPPORTED_SYNTAX and SG01–20. Missing/duplicate units reject SOURCE_SET; driver rejects
extra files; parsing rejects SYNTAX_INVALID. Findings sort by module/line/column/rule.
Accumulate every applicable named finding unless source-set/parse prevents analysis.
An empty tuple is grammar acceptance only, never execution/review/authority.

All source packets remain AST data, never imported, evaluated or compiled for execution.
Corpus is literal independent input/expected rule/location; it cannot import gate/symbols.
No bypass constructors, Any/cast, introspected expected inventory or unvalidated dynamic state.
Source comments/docstrings/literals contain technical explanation or scoped synthetic test data,
never owner instructions, dispatch prompts or ticket/correction narratives.

## 3. Finite closure and owned alternatives

Every semicolon-separated alternative is a distinct ID and literal expected rule/location.
The negative packet must reach that named predicate; another rejection does not discharge it.
Retain existing direct cases as regressions when adding their missing alias alternatives.
Complete nine-unit literal packets; minimal catalog definitions/imports are independently authored.

Exact attribute-cast discriminator packet: place the following source in qualification_values
of a complete minimum packet (other eight units unchanged). Expect SG12 at line4/column11;
SG09 at the import may coexist. Keep the import namespace origin as specified by B1, without
making the import allowed. Removing only the SG12 call predicate must lose that designated
finding and turn this assertion red even while SG09 remains.

```python
import typing as type_ns

def helper(value: object) -> object:
    return type_ns.cast(object, value)
```

The distinct imported-member alternative is `from typing import cast as checked_cast` followed
by `checked_cast(object, value)` in that same helper/location. It also needs the call-site SG12;
an import-site rejection alone is not its proof. These are synthetic AST data, never executed.

| Cell / rule | Required alternatives / observable assertion |
| --- | --- |
| B2-C09 / SG09 | __import__; importlib.import_module imported under a different local name, call at the alias site rejects SG09 (not just import rejection) |
| B2-C10 / SG10 | Renamed eval; renamed exec, each call rejects SG10 |
| B2-C11 / SG11 | getattr; setattr; aliased reflective call |
| B2-C12 / SG12 | Any annotation imported as another name; typing.cast attribute call; cast imported as another name and called. Name-only direct fixtures do not cover these |
| B2-C13 / SG13 | model_construct; model_copy(update=...); aliased checked-model bypass |
| B2-C16 / SG16 | No guard; reassigned after guard (ordinary, same-line, unpacking separately); else; after branch; unrelated isinstance elsewhere in condition; same-name non-Mapping method; shadowed Mapping or isinstance |
| B2-C17 / SG17 | Parameter shadows permitted callee; constant local rebind; function-valued assignment alias; callable parameter; callable return. Each is distinct, not renamed copies |
| B2-C18 / SG18 | Unknown model_validate; unknown resolve; computed call target; exact checked model model_validate, model_validate_json, model_dump and model_dump_json (four distinct cases); correctly typed ApprovedManifestPort.resolve, PrerequisiteEvidencePort.resolve and EvidenceObservationPort.resolve (three distinct cases). No object.model_dump standing in for known model/port identity |
| B2-C19 / SG19 | Direct recursion; unused two-helper mutual recursion. B3 owns every other SG19 alternative |
| B2-POS | SGP04 unchanged guarded Mapping.get; SGP05 typed acyclic helpers; allowed builtin/schema/catalog constructor and alias paths in actual package remain green |
| B2-PRESERVE | B1 namespace/type/ID predicates, source-set/parser/determinism and unchanged accepted A full focused suite |

Add `test_source_call_admission` for this owned set; explicit independent expected IDs/counts
prevent omission. Existing aggregate tests continue collecting all cases; no narrowing global
assertions to get green. Existing B1 `test_source_namespace_admission` remains in the suite.

## 4. Baseline and proof allocation

Historical7171f41 evidence is diagnostic, not B2's future exact baseline. Root preflight already
proved known typed port call reaches inspect_sources and wrongly returns no findings
([preflight](../../../doc/reviews/controlled-verification/cvq-01b-replacement-ticket-preflight.md)).
After B1 acceptance, first add only B2 test/packet assertions at that same existing seam, run
`test_source_call_admission` on the actually bound B1 SHA and capture the known-port SG18 absence.
If B1 incidentally rejects it, retain real green and use exact guard reverse mutation; never
fabricate a red or treat missing new symbols/collection failure as defect evidence.
No old implementation-time chronology is claimed.

Root independently mutates the schema-call decision to allow known port.resolve: the named
known-port assertion must turn red and byte-restored green. Root's different-door probe puts
a correctly typed helper call into the real qualification_ports source in the detached review
snapshot, requires test_architecture_dependency_gate red, restores exact bytes and observes green.
No provider/port implementation is called. Own receiver, callee and recursion behaviors retain
their named discriminating evidence; B3 alone owns final full20-rule campaign.
One finite retained helper audits SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION on exact candidate,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. Root owns verdict, not the helper.

## 5. Commands, bounded evidence and return

Python `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe` (`$cvqPython`);
Python3.11.9 / mypy2.3.0 / Pydantic2.13.4, read back versions, no installation.
One foreground process;60 seconds/command,1200 seconds/pass;zero automatic retry, load,
background polling or new repository-wide/native suite. Budget exhaustion returns BLOCKED.
Run commands directly, retain unreduced output and exact SHA. Do not hide baseline failures.

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_evidence.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py tests/verification_qualification_source_policy.py tests/verification_qualification_source_symbols.py tests/verification_qualification_source_gate.py tests/verification_qualification_source_corpus.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains tests.test_verification_qualification_boundaries
git diff --check
```

Strict/test imports are the build check; `QualificationBoundaryTests.test_architecture_dependency_gate`
inspecting the real nine files is the smoke. For each mutation run the named fully qualified
method under `tests.test_verification_qualification_boundaries.QualificationBoundaryTests`,
then byte-exact restore and rerun. Every owned behavior has named reverse-red/restore-green
evidence; root owns independent checks, not a duplicate implementer-wide campaign.
No result from another SHA silently covers a changed guard. Zero red is a finding.

Return `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED` with ticket/closure/control
refs, baseline and additive candidate SHA, changed files/symbols, per-cell baseline/green/mutation
commands and output, findings and scope deviations. Commit source only in the admitted owner
worktree. Root records evidence/docs separately; no amendment/reset/force, docs writes by
implementer, cross-Agent control or approval claim. Initial review plus one batched correction
review maximum; exhaustion returns convergence. Schema/type/predicate change returns
CHANGE_DETECTED, not a broader fallback.

## 6. Admission and sequential continuation

Owner exact approval and B1 accepted candidate/review/index binding are pending. Same approved
ticket set permits root to fill the future dependency SHA with fresh clean, containment, branch
and ancestry evidence; it is not a guessed hash and grants nothing before B1 acceptance.
Close B1 view, bind this new view, dispatch same owner, wait_agent, review. Same-lifetime bridge/
runner/receipt/descriptor/host readback are NOT_REQUIRED. No additional source lane.

B2 APPROVED only permits B3 dependency binding under that same exact ticket approval. No partial
A/B integration or behavior-phase qualification. Changed closure needs owner decision; unchanged
metadata binding does not. ACTION_COMPLETED / TICKET_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING; then DEPENDENCY_PENDING, never an automatic third B correction.

## 7. Exact set approval and current route — 2026-09-21

Owner **「核准」** approves B1/B2/B3 document02/closure01 together at
`6ff3e127ca7d9bfeb2d4f9932bb1ec60f1d2d7a3`. This ticket's approved LF digest is
`45c503dd50970265cc1cf3184514814e32c3f38909b8901d130503175cdff553`. Document03 changes signature/status/allocation only;
sections1–6's predicates, writable symbols, tests and budgets are unchanged. Earlier pending
approval prose is historical. Original B closure01 remains exhausted; this is a new admitted
responsibility closure, not a third correction. No partial integration/push/release/install grant.

This approves sequential dependency binding, not source mutation before B1 acceptance.
Root will append the actual accepted source SHA and exact review/index identity after the prior
closure passes, verify clean workspace/containment/ancestry, close the prior view and bind this
one. That ordinary metadata binding requires no second owner approval. Any changed predicate,
scope or failed reference still halts; no fabricated accepted baseline. ACTION_COMPLETED /
EXACT_SET_APPROVAL_RECORDED -> DEPENDENCY_PENDING, then the already-declared AUTO_CONTINUE route.

## 8. Accepted dependency bound; cumulative resource decision — 2026-09-21

B1 is APPROVED at sourcea8340e2711540fd4ed05e4ef91c6877977f9d5db. Exact root review05,
LF1930708387c4ab3fdfef4a55a2601d571b4ef63526eb2b9946aad75cd0332f8c, and review index45,
LF85e6aaee2f14268bc387bb29113cbb6b1d949046881c8fcdb09cfbf6086b680f, resolve at
628b8d48bae81381ee3aa14c606ad017c5c5e66b. This is the real B2 baseline, not7171f41.
The retained owner tree is clean on codex/cvq-01; no implementation of B2 is admitted yet.

REQ-051 revision12 D8 requires split descendants to retain this round's consumption. Original
section5's1200-seconds/pass cannot silently reset the depleted common allowance. B1's exception
used less than its80-second remainder, including a conservative full15sec owner charge; total
historical model usage remains UNKNOWN. The residual is insufficient for B2 implementation/review.
Closeout ledger charges75 of the last80sec (including startup/readback, owner15, helper3.2,
root mutation7.901, focused/strict21.435 and conservative document closeout reserve). Together
with prior1120 charged/reserved seconds, total1195 leaves5. This is conservative resource
accounting, not a claim that every command was observed or a runtime hard cap was enforced.
Keep the unused balance, all prior charges and finite60sec command limit; do not start a knowingly
underfunded lane or describe this as missing runner/model capability.

Proposed owner resource decision: add2400 command-wall seconds to the same lineage, shared by
B2/B3 implementation, one correction each, root review, helpers and document closeout. It is not
2400 per ticket/pass or a token/wall-clock promise. Existing source predicates/closure and Luna/
root ownership remain unchanged; no extra file/framework/host effect is implied. This proposal
has not been approved or consumed. After approval, perform D8 envelope/preflight and rebind the
single-ticket ContextView before dispatch. Source approval already stands; do not re-ask for it.
ACTION_COMPLETED / B2_DEPENDENCY_BOUND -> WAIT_FOR_HUMAN / CUMULATIVE_BUDGET_EXTENSION_REQUIRED.

## 9. Corrected continuation and retained-owner admission — 2026-09-21

Section8's additional-budget approval gate and2400sec proposal are SUPERSEDED, not granted:
root incorrectly treated B1's exception allowance as cancellation of B2's existing section5/7
approved resource grant. Owner requests immediate continuation under that existing authority.
The original1200sec grant is verified in the approved ticket at6ff3e127. Apply it once across
B2 implementation, root/helper review and any single correction, not anew on each pass.
Keep the same CVQ-01/B lineage: prior1195 charged/reserved remains recorded, prior unknown model/
command history remains UNKNOWN; B2 use appends to that ledger. No spending is erased or invented.
Reserve650sec for the owner initially; root/helper/closeout and correction share the balance.
Max60sec/command, one foreground process, no automatic retries/load/background polling.

Fresh source baselinea8340e2711540fd4ed05e4ef91c6877977f9d5db is clean on codex/cvq-01 at
.worktrees/cvq-01. .git/common-dir and repository containment match; no reparse attributes.
Exact SPEC07/wire03/sealed Context02/profile01/current B1 review05 pins match. Python3.11.9,
mypy2.3.0/Pydantic2.13.4 match. Ordinary SourceUnit/SourceViolation constructors cover all9 modules
and23 rules; existing actual-package architecture and source-set/parse methods2/2 pass (10.338sec).
B1's unchanged-seam committed reverse proofs remain bound through its accepted SHA; no new DTOs.
REQ-051 D8 at1ea589b3ff416e637b2456464d49b73feae53c21, LF
a8d04409a8397b73bb351ac2fe3bfd85de3c49589c0e1397cc66220e7481b709, governs the following envelope.

Modify exactly these existing paths; create/delete/rename/dependency grants are empty:
- tests/verification_qualification_source_symbols.py
- tests/verification_qualification_source_gate.py
- tests/verification_qualification_source_corpus.py
- tests/test_verification_qualification_boundaries.py

Reuse inspected scope_for/build_scope_bindings/resolve_name, guarded_mapping_get/helper_cycles,
_check_calls/_check_functions, _row_with_replacements/MINIMUM_PACKET and QualificationBoundaryTests.
Symbols observes scope/binding facts; gate makes finite verdicts; corpus holds independent literal
fixtures; boundary methods assert behavior. No duplicate resolver/runner or browser/mock/PNG/pixel
utilities (no visual/network surface). Product0, tests about0–300 net lines, owner documents0,
screenshots0; estimates are review signals, not compression quotas. Preserve B1/A exactly.
All temporary outputs, including mypy --cache-dir, are outside worktrees. Root retains necessary
proof once in existing cvq-01b-correction-evidence.md and verdict in cvq-01b-source-admission-code-review.md,
with existing indexes; no new report/script file. Root document estimate150 lines plus mandatory raw
evidence; no automatic complete-report regeneration. Actual Git diff and untracked/ignored artifact
inventory are checked against the declared boundary; observations do not imply write interception.

Close ctx-cvq-01b1-closure02-exception01 and bind ctx-cvq-01b2-closure01-doc05 to retained
cve_wire_implementer Luna/xhigh and root sole reviewer. Read only this exact ticket's current
closure/direct sources; no inherited B1 raw context as authority. Existing B2 predicates and
proof allocation are unchanged. Followup -> wait_agent -> root review; bridge NOT_REQUIRED.
No partial integration/push/release/install. ACTION_COMPLETED / B2_ADMITTED -> AUTO_CONTINUE / IMPLEMENT_CVQ01B2.

## 10. Initial review and single correction admission — 2026-09-21

Candidate4f98243e2e50fe6dac359f2f78be0d10cf3238e8 is additive/clean with exactly four allowed
existing files changed; source118add/8delete, no new files/dependencies/product/A/B1-owned row
changes. Root independently ran strict21/focused45 green, then reproduced three scope/guard
defects and a masked loop-target mutation. Existing closure01 remains unchanged.

Root [review03 section6](../../../doc/reviews/controlled-verification/cvq-01b-source-admission-code-review.md#6-b2-initial-review-and-sole-batched-correction--2026-09-21),
LFf24904c8d2f9dffbb2f8aa311023455ebea591c83ea15777241306b1b6db5736, and
[evidence02](../../../doc/reviews/controlled-verification/cvq-01b-correction-evidence.md),
LF57efdf75c23485fe6f3df39e3b7221b7f68c1bffaaa1287f6edf102f5c68c2bb, at this control commit bind B2-F01–04.
Review index46 LF25c40b71ec55135a96051e4c62cc964abf5351dc7dbeb6d70cde4bba6e88c0b7.
Same retained owner/worktree/model, new view ctx-cvq-01b2-closure01-correction01; no replacement
seat or permission expansion. Correct scoped order/aliases, immediate receiver guard and precise
existing fixture predicates; preserve accepted code and all original B2 alternatives.

One180sec owner correction reservation comes from the SAME1200sec B2 grant. Initial650sec is
a conservative reservation charge (known57.598sec, other command time UNKNOWN); root/helpers
charged/reserved120sec through admission, including helper6sec. Remaining250sec is reserved
for root final verification/docs; unused reserves are not measured use and never reset history.
Earlier B1195 remains. One foreground command,60sec cap, no retries/load/polling, outside caches.
Owner records full timed command outputs and genuine4f98243e pre-fix reds; missing earlier
baseline chronology stays missing. No source cleanup outside the allowlist.

ACTION_COMPLETED / B2_INITIAL_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_SINGLE_CORRECTION.
After return root reviews; pass binds B3 directly, a remaining defect routes to convergence.
No partial integration/push/release/installation or new owner decision is requested.

## 11. Sole correction reviewed; convergence required — 2026-09-22

Current state: BLOCKED / CONVERGENCE_REVIEW_REQUIRED / NON_DISPATCHABLE / NOT_INTEGRATED.
Closure01 initial review and its one correction are consumed. Document07 records the result,
not a new implementation approval. Retained owner candidate
f2b3fb8dab7cae2554eb0ab24b9ee7dfc6d77092 additively descends from4f98243e2e50fe6dac359f2f78be0d10cf3238e8;
exactly three of the four allowed existing files changed, no product/policy/A changes.
Owner and root detached review worktrees read back clean.

Root [review04 sections7–8](../../../doc/reviews/controlled-verification/cvq-01b-source-admission-code-review.md#7-b2-sole-correction-final-review--2026-09-22),
LF ff950a550f75f847d3c69d607ceeb5af4267ef493f1f6cc0e2c87801b828e844, and
[evidence03](../../../doc/reviews/controlled-verification/cvq-01b-correction-evidence.md#b2-sole-correction-review-and-convergence-evidence--2026-09-22),
LF cf4ebf0ab11c5037782b4e339aa09a2d1d8742b34db239caadc6c494b66f95f2, bind this result in the same control commit/index tree.
Strict21/focused45 pass. Root's four independent cases produce one pass/three failures:
later function-local binding wrongly inherits a builtin; forward module-helper call wrongly
rejects; generic membership condition bypasses the immediate-guard rule. Enforcing the actual
frozen immediate rule makes unchanged report_contracts.py279:21 fail SG16, then restoration
returns green. Section2's immediate rule and real-package preservation are contradictory.
This is a ticket/preflight defect as well as remaining implementation/evidence work, not a
reason to broaden owner scope or ask the owner to retry the same frozen instruction.

The review's section8 recommendation is OWNER_EXACT_APPROVAL_PENDING: same-function structurally
guarded true region, exact unchanged receiver/guard binding, nested admitted conditionals/finite
iteration do not erase evidence, and no generic in-operator exception. It changes the old
same-function ancestor rejection and must be decided by the project owner before a new exact
closure is compiled/preflighted. SPEC07, sealed Context02, accepted A/B1 and all current source
remain unchanged. Do not silently mark a proposal approved or reinterpret historical reds.

Retain the cumulative section10 ledger and unknown observations; no extra grant or reset.
Final B2 port/mutation proof remains NOT_VERIFIED; B3's full20-rule campaign was not started.
Root alone owns the conclusion; retained helper findings were independently reproduced.
No third correction, source write, new agent, B3 dispatch, partial integration, push, release,
installation or native effect is admitted. ACTION_COMPLETED / B2_CORRECTION_REVIEW_BLOCKED ->
WAIT_FOR_HUMAN / OWNER_GUARD_CONTRACT_DECISION_REQUIRED.

## 12. Owner approval and closure02 admission — 2026-09-23

Owner **「核准」** approves review04 section8 at
6fd76324133ef93fbc70122c7881b48777d0b495, LF
ff950a550f75f847d3c69d607ceeb5af4267ef493f1f6cc0e2c87801b828e844.
This is the exact selected same-function guard convergence, not approval of the alternative
product rewrite. Document08 compiles that decision into CLOSURE-CVQ-01B2/02; closure01 remains
exhausted history. Sections2–5 remain effective except the explicit replacements below.
SPEC07/wire03/Context02/profile01 are unchanged and retain section1/9 pins.

### Effective bounded contract and closure

Replace section2's immediate-ancestor restriction with review04 section8 rules1–5 verbatim in
meaning: the exact unshadowed builtin isinstance guard must establish the same receiver as
typing.Mapping; the call stays structurally in that guard's true body and in the same function.
Nested ordinary If true/else and already-admitted finite For branches preserve that evidence;
operator spelling does not grant an exception. The Mapping guard's own else, after-branch,
cross-function/class boundary, unsupported control, wrong receiver, shadowed guard and changed
receiver/guard-name binding do not prove access. No general control-flow engine or source execution.
This supersedes the same-function ancestor negative only, not the cross-function negative.

| Closure02 cell | Exact required observation through inspect_sources |
| --- | --- |
| B2-R2-GUARD-POS | Direct guarded access; nested flag; nested membership; inner-If else; finite For with unchanged receiver; unchanged real report_contracts discriminator all accept. These are separate literal packets/controls; the real package still passes test_architecture_dependency_gate. |
| B2-R2-GUARD-NEG | Existing wrong receiver, no guard, Mapping-guard else/after, ordinary/same-line/unpacking/loop-target rebind, shadowed Mapping/isinstance and cross-function inherited guard remain designated SG16 negatives. Include guard-name reassignment after the true guard and before access; identity cannot be inferred from spelling. |
| B2-R2-LOCAL | A function-local assignment anywhere, including later/unreachable assignment, cannot inherit an outer helper/builtin identity: designated SG17 at that call. Parameter, callable alias/return and cross-scope isolation regressions remain. The former B2-POS-call-before-later-binding is a rejection now. |
| B2-R2-FORWARD | Typed acyclic module-local helper defined after the calling function accepts in its deferred body. A module-level call before its helper definition is not that case and remains SG18. Direct/mutual recursion and unknown calls still reject. |
| B2-R2-PRESERVE | Original B2 alternatives, B1 origin/type/ID behavior, source-set/parser/determinism and accepted A focused suite remain; no schema model/port behavior call. |

Use existing corpus/expected IDs/counts and driver methods. Move only the superseded same-function
ancestor row to positive; keep historical evidence untouched. Do not change expected IDs merely
to hide a missing alternative. Ordinary constructors and finite enums remain unchanged; no new
public DTO, enum, policy switch or injectable resolver. Source symbols owns scope/guard facts,
gate owns finite decisions, corpus owns literal packets, driver owns assertions.

### Retained admission and resource allocation

Baseline f2b3fb8dab7cae2554eb0ab24b9ee7dfc6d77092 is clean in .worktrees/cvq-01 on codex/cvq-01,
with repository common-dir and no reparse attributes. Root review snapshot pins the same SHA.
Fresh remote main and local main both equal b697738d009db37318ebc8762107ef8329e014db.
Policy/source were read from the candidate snapshot, not the control tree (which has no such
unintegrated support file). The control-tree missing-file probe did not provide authority.

Same Luna/xhigh owner cve_wire_implementer, root sole reviewer, existing Terra/xhigh evidence-only
helper. Close ctx-cvq-01b2-closure01-correction01; bind ctx-cvq-01b2-closure02-doc08.
Modify exactly section9's four existing test/support paths; create/delete/rename/dependencies,
product/policy/documents/screenshots grants remain empty. Reuse the existing scope/guard/corpus
seams; no framework or new source file. Expected test-support delta0–120 lines is a signal, not
a compression quota. Root docs/evidence remain in the same existing indexed leaves.

No new1200sec grant or reset: original B1195 and B2 initial650/root120/owner180 reservations remain.
Allocate the existing root-final250 reserve as150 conservative closeout charge/reserve,50 for
this retained-owner migration,40 root/helper verification and10 document closeout. These are
resource reservations, not a claim that every historical command was measured; unknown history
stays UNKNOWN. Count all new commands with elapsed time; stop on allocation exhaustion. One
foreground process, max60sec/command, zero automatic retry/load/polling. Reallocation within the
existing finite grant does not manufacture additional budget. The parent retains the timer;
no runtime hard-enforcement claim is made.

Owner captures baseline-red for changed named cells on f2b3fb8, then strict/focused commands from
section5 with -B and outside --cache-dir. Return actual unreduced output, commands and durations,
not "all45 passed" prose. One bounded migration plus at most one batched correction review under
the same remaining allocation; budget exhaustion halts instead of a new implicit allowance.
Root owns the independent reverse campaign; owner need not duplicate it. Root tests each new
guard/local/forward decision with a discriminating predicate removal, restores green, and retains
section4's known-port/different-door actual-package proof. Existing other B2 alternatives still
need designated rule coverage; B3 alone owns full20-rule completion. Preserve A/B1 proofs.

### Readiness evidence and continuation

The unchanged public test seam was revalidated at the exact baseline with ordinary SourceUnit,
SourceViolation, NameBinding, SymbolOrigin and ImportBinding construction over all finite enum
states; the minimum packet is accepted and missing source rejects SOURCE_SET. Root's baseline
observations of nested flag/future-local/forward-helper reach inspect_sources and retain genuine
defects rather than collection errors. Command and unreduced output:

```powershell
$b2Preflight = @'
import ast,sys,time
sys.path.insert(0,"tests")
from verification_qualification_source_policy import SourceModule,SourceRule,SourceUnit,SourceViolation,BindingKind,ResolutionStatus
from verification_qualification_source_symbols import NameBinding,SymbolOrigin,ImportBinding
from verification_qualification_source_corpus import MINIMUM_PACKET
from verification_qualification_source_gate import inspect_sources
start=time.perf_counter()
units=tuple(SourceUnit(m,"") for m in SourceModule)
violations=tuple(SourceViolation(m,1,0,r) for m in SourceModule for r in SourceRule)
node=ast.parse("from typing import Mapping")
for kind in BindingKind:
    for status in ResolutionStatus:
        NameBinding("value",kind,node,status=status)
for status in ResolutionStatus:
    SymbolOrigin("typing","Mapping",status)
    ImportBinding("Mapping","typing","Mapping",1,0,False,node.body[0],node,0,status,None)
assert len(units)==9 and len(violations)==207
assert inspect_sources(MINIMUM_PACKET)==()
assert any(v.rule is SourceRule.SOURCE_SET for v in inspect_sources(MINIMUM_PACKET[:-1]))
print("ORDINARY_CONSTRUCTORS: modules9/rules23/kinds6/statuses5 PASS")
packets=(
("nested_flag","from typing import Mapping\ndef helper(value:Mapping[str,str],flag:bool)->str:\n    if isinstance(value,Mapping):\n        if flag:\n            return value.get('x')\n    return ''\n"),
("future_local","def probe()->object:\n    result=len(())\n    len=0\n    return result\n"),
("forward_helper","def probe()->int:\n    return later()\ndef later()->int:\n    return 1\n"))
for name,text in packets:
    packet=tuple(SourceUnit(u.module,text) if u.module is SourceModule.QUALIFICATION_VALUES else u for u in MINIMUM_PACKET)
    print(name,inspect_sources(packet))
print("ELAPSED",round(time.perf_counter()-start,3))
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $b2Preflight
```

```text
ORDINARY_CONSTRUCTORS: modules9/rules23/kinds6/statuses5 PASS
nested_flag (SourceViolation(module=<SourceModule.QUALIFICATION_VALUES: 'qualification_values.py'>, line=5, column=19, rule=<SourceRule.SG16: 'SG16'>),)
future_local ()
forward_helper (SourceViolation(module=<SourceModule.QUALIFICATION_VALUES: 'qualification_values.py'>, line=2, column=11, rule=<SourceRule.SG18: 'SG18'>),)
ELAPSED 0.016
```

Existing identical public-contract preflight/reverse evidence remains bound via accepted B1.
New behavior negatives above are baseline observations, not a claim that migration is already green.
After committing this leaf and verifying both index edges, ACTION_COMPLETED /
B2_CLOSURE02_OWNER_APPROVAL_RECORDED -> AUTO_CONTINUE / RETAINED_OWNER_IMPLEMENT.
Bridge/runner/receipt/descriptor/host readback are NOT_REQUIRED. Followup then wait_agent,
no progress polling; root receives and reviews without asking the owner to relay the result.
No product/source outside the four paths, partial integration, push, release, install or native
effect is authorized. Approval of the semantic choice is not re-asked as a metadata ceremony.

## 13. Closure02 initial return and correction resource gate — 2026-09-23

Current: CHANGES_REQUESTED / CORRECTION_PENDING_RESOURCE / NOT_INTEGRATED.
Source5b3a432715163657c8d829d683fb0482fac8ba94 is an additive clean three-path candidate from
f2b3fb8. Semantic approval in section12 stands; this section does not reopen that owner choice.
[Review06 section10](../../../doc/reviews/controlled-verification/cvq-01b-source-admission-code-review.md#10-closure02-initial-review-one-batched-correction--2026-09-23),
LF 309341694c0b74c05f7fe53ae97d45f3b581df8cc892078c67723ee663eb3125, and
[evidence04](../../../doc/reviews/controlled-verification/cvq-01b-correction-evidence.md#b2-closure02-initial-independent-review--2026-09-23),
LF f5c9298b44dd4d85c9ce5242096e13ca7eb1c1f1371826a81968b05ade855913, bind four finite existing-closure defects:
unrelated inner-isinstance else handling; future local-function identity; unsupported-control
guard attestation; missing forward-positive discrimination and unreliable supplied trace.
Root reproduced the helper findings; one initial review is consumed and one correction remains.

Same four-path modify-only boundary, owner, profile, no new files/product/policy effects and
closure02 remain. Proposed additional120 command-wall seconds is resource authority PENDING,
not an automatic reset. Original B2 grant/reservations and unknowns remain; section12 migration50
is conservatively charged, root/helper10 and document10 charged/reserved, leaving30. With owner
approval only,30+120 allocates correction60, root/helper70, closeout20. No larger model, new
closure or extra correction cycle. Until funded, do not dispatch an underfunded correction.
On approval record that exact resource decision and directly follow up the retained owner using
this committed correction reference; no second scope/semantic approval. Otherwise remain blocked.
ACTION_COMPLETED / CLOSURE02_INITIAL_CHANGES_REQUESTED -> WAIT_FOR_HUMAN /
CUMULATIVE_VERIFICATION_BUDGET_REQUIRED. No integration, push, release, installation or native effect.
