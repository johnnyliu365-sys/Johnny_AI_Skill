# CVQ-01B1 | Exact namespace and import admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B1` / `IMPLEMENTATION_TICKET` / `10` |
| State / closure | `OWNER_APPROVED / ONE_FIXTURE_EXCEPTION_ADMITTED / NOT_INTEGRATED`; `CLOSURE-CVQ-01B1/02`; section14 is current; prior exhaustion retained |
| Preparation authority | Owner's 2026-09-21 approval of [B convergence01](../../../doc/reviews/controlled-verification/cvq-01b-convergence-proposal.md) at797c15db, LF0308388788c4a6a6c79ce4dd256b72bb5a231a498357a0038f305680e46f0f94; drafting only |
| Observable result / change class | Complete, exact import origins and finite typed resolution; `PRODUCTION_BEHAVIOR / DEFECT_CORRECTION`, not test-exempt |
| Baseline | `7171f41bdec15104fd653ecee6c8e06691055d16`, unapproved B correction; preserve immutable history, never call it accepted |
| Owner / reviewer / workspace | Retained `cve_wire_implementer` / `root`; proposed same `.worktrees/cvq-01`, `codex/cvq-01`, new view `ctx-cvq-01b1-closure01` |
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

## 2. Responsibility, scope and exact resolver contract

This closes B-F01 and B-F05's open resolution variants. Call/receiver/body grammar remains
NOT_ADMITTED for B2/B3, not silently accepted. All production files and accepted A tests/catalog/
fixtures are READ_ONLY. Writable paths (and only these existing owners):

| Path under tests/ | Writable responsibility |
| --- | --- |
| verification_qualification_source_policy.py | Existing immutable policy/records and finite resolution/binding discriminants; no new allowed import/call |
| verification_qualification_source_symbols.py | Exact import targets, entries, scope/export origins and module graph; no verdict, I/O or execution |
| verification_qualification_source_gate.py | Import/cycle predicates and thin typed-enum consumer adaptation only; no new call/body behavior |
| verification_qualification_source_corpus.py | B1 rows, SGP01–03, their complete minimum packet prerequisites and independent ID/count/location literals |
| test_verification_qualification_boundaries.py | B1 assertions and real-package reader/invocation; no duplicated resolver policy |

No new support file, dependency, framework or arbitrary line cap. Keep symbols facts/graphs
separate from gate verdicts. B1 public test seam below stays frozen for B2/B3.
Replace unrestricted status/kind fields with named finite enums: ResolutionStatus values
RESOLVED/EXTERNAL/UNKNOWN/AMBIGUOUS/UNSUPPORTED; BindingKind
FUNCTION/CLASS/PARAMETER/ASSIGNMENT/IMPORT/AMBIGUOUS. These type the existing internal records;
they do not introduce an external input port. Only RESOLVED exact internal origins or EXTERNAL
members from the closed allowlist can qualify. UNKNOWN/AMBIGUOUS/UNSUPPORTED never succeed.
Consumers use enum members, not open str conventions or cast. Name/path strings remain data.

Resolve Python3.11 package-relative levels against `library.controlled_verification`, never
truncate a dotted suffix or invent a filesystem lookup. Match whole case-sensitive module and
symbol identities. Resolve every entry, including later entries after an allowed one, nested
unused function/class imports and explicit re-export chains. Nested local imports must not
become module exports. Competing incompatible exports are ambiguous, not first/last-match.
Check the declared consumer edge and every edge of the resolved export path to its final origin;
do not require the final constituent to appear as a direct edge in the consumer's row.
Thus __init__ -> qualification_contracts -> qualification_values is a permitted explicit
re-export path, while any forbidden edge anywhere in that path rejects. A facade cannot
launder a forbidden constituent. Preserve this distinction in SGP01 through __init__ as well.
Unknown module/symbol and cyclic/unsupported traversal reject; graph traversal is finite.

| Module | Permitted direct internal targets |
| --- | --- |
| qualification_values | none |
| binding_contracts / prerequisite_contracts / roster_contracts | qualification_values |
| manifest_contracts | qualification_values, binding_contracts, prerequisite_contracts, roster_contracts |
| report_contracts | qualification_values, binding_contracts, roster_contracts |
| qualification_ports | qualification_values, manifest_contracts, prerequisite_contracts, roster_contracts, report_contracts |
| qualification_contracts | all seven preceding constituents, explicit re-exports only |
| __init__ | qualification_contracts, explicit re-exports only |

External symbol set is exactly SPEC11.3's schema row (not behavior TypeAdapter/ValidationError).
Recognizing an external module does not admit all its symbols. Preserve forbidden origins for
B2 diagnostics even though imports reject. Module and helper graphs are distinct.

Diagnostic resolution is not import admission: for `import typing as type_ns`, retain the
Import AST, local binding type_ns and exact external module identity typing with UNSUPPORTED
admission status. This module-form import rejects SG09; it is not a new permitted external
surface. B2 can still identify type_ns.cast at the call node and emit SG12. Do not erase the
origin, stop analysis after SG09, or use a string sentinel as a substitute for the typed AST
binding kind. Add `B1-rejected-namespace-origin` at the symbols seam to pin those facts.

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

## 3. Finite closure and test map

Each semicolon-delimited alternative below is a separate stable corpus ID, with literal
expected rule and import-node location. Existing IDs keep their meaning; fix a mislabeled packet,
do not redefine the requirement to match its label. Negative packets include valid definitions
for every unrelated referenced symbol. Additional named findings are allowed; named-rule absence
still fails even if another rule rejects. Positive packets are complete nine-unit literal data.

| Cell | Executable predicate / required separate alternatives |
| --- | --- |
| B1-I01 / SG01 | Relative forbidden edge: direct; normalized parent-relative. Exactness: SG01-module-suffix uses .qualification_values.not_a_module; SG01-missing-symbol from allowed exact module. Both reject SG01, not success via prefix |
| B1-I02 / SG02 | Fully qualified reverse edge; absolute nonexistent suffix must reject SG02 |
| B1-I03 / SG03 | From-package module; package alias attribute. An allowed first entry plus forbidden second still rejects; no first-entry-only resolution |
| B1-I04 / SG04 | Forbidden origin under local alias; actual re-exported symbol alias (not another direct-import duplicate) |
| B1-I05 / SG05 | Unused typed function forbidden import; class-method forbidden import; nested bindings do not leak into exports |
| B1-I06 / SG06 | Indirect forbidden re-export; multi-hop __init__/facade; incompatible same-name origins reject, no laundering or successful ambiguity |
| B1-I07 / SG07 | Relative wildcard; external wildcard |
| B1-I08 / SG08 | Two-module cycle; self import; alias/facade cycle; all scopes, including unused definitions |
| B1-TYPE | Construct/consume each finite resolver/kind variant through ordinary typed constructors; strict checker plus independent record-annotation assertion reject open str fields |
| B1-POS | SGP01 explicit facade, SGP02 permitted import alias, SGP03 approved DAG; unchanged actual nine-file package remains green |
| B1-SET | Missing/duplicate/extra file and syntax failure remain named rejection; immutable policy snapshots and deterministic result order preserved |

Existing aggregate methods remain: test_source_negative_corpus, test_source_positive_corpus,
test_source_set_and_parse_fail_closed, test_source_result_is_deterministic,
test_architecture_dependency_gate. Add `test_source_namespace_admission` for the B1 owned
rows/types only; IDs/counts are authored independently of the selected table, so dropping every
owned row cannot pass. No copied checker oracle. B2/B3 rows must not be weakened/deleted.

## 4. Genuine baseline and reviewer allocation

Before repair, add only assertions/fixture data at the existing inspect_sources seam on7171f41.
Run `test_source_namespace_admission`: the exact suffix case must fail because SG01 is absent,
not because a new enum/helper cannot import. Keep baseline-facing assertions independent of
new types until their implementation exists. Source-set, parser and current package collect.
Root preflight reproduced this exact baseline in
[replacement preflight](../../../doc/reviews/controlled-verification/cvq-01b-replacement-ticket-preflight.md).
A cell already green keeps its result and receives a reverse mutation, never an invented red.

For slice acceptance, root independently weakens exact-target admission and requires
SG01-module-suffix red/restored-green; separately enters through a later import entry rather than
the implementer's suffix door. Full SG01–20 campaign is reserved for final B3, not repeated here.
Every B1 cell still needs mapped discriminating evidence in the final combined candidate.
One finite helper audits SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION on the exact candidate,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT; evidence/findings only, root alone concludes.

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

## 6. Dependency and continuation

Exact owner approval of this document02/closure01 is pending. Then root commits the signature,
fresh clean/containment/Git/ancestor readback, binds this ticket/profile/view and dispatches the
same owner synchronously. Runner/receipt/descriptor/host readback are NOT_REQUIRED; wait_agent,
receive and review. Drafting approval alone is not this source admission.

B1 APPROVED only satisfies B2's dependency. No partial A/B integration. Root then binds the
actual accepted SHA and exact review/index to B2 before its admission; a changed closure returns
to owner, an already-approved sequential dependency binding does not need another ceremony.
ACTION_COMPLETED / TICKET_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.

## 7. Exact set approval and current route — 2026-09-21

Owner **「核准」** approves B1/B2/B3 document02/closure01 together at
`6ff3e127ca7d9bfeb2d4f9932bb1ec60f1d2d7a3`. This ticket's approved LF digest is
`804bed686e6d67f223c3d4ec5b4ee83b81cdca8f530706a30abff798b7ebf79e`. Document03 changes signature/status/allocation only;
sections1–6's predicates, writable symbols, tests and budgets are unchanged. Earlier pending
approval prose is historical. Original B closure01 remains exhausted; this is a new admitted
responsibility closure, not a third correction. No partial integration/push/release/install grant.

Root fresh readback: exact retained owner root
C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01, branch codex/cvq-01,
HEAD7171f41bdec15104fd653ecee6c8e06691055d16, clean; .git pointer resolves to the registered
cvq-01 linked worktree and common repository .git. Repository/root/.worktrees/owner roots have
no reparse attribute; accepted A485d882f is an ancestor. Existing public SourceUnit/SourceViolation
constructors, all9 SourceModule/all23 SourceRule variants and frozen records pass; actual9-file
package control returns no findings. This is seam admission, not approval of the defective
internal resolution strings being repaired. Python3.11.9/mypy2.3.0/Pydantic2.13.4 read back exactly.

Close ctx-cvq-01b-closure01; bind ctx-cvq-01b1-closure01 to the same retained implementation-standard
owner (gpt-5.6-luna/xhigh), root sole reviewer, profile defaults01 at797c15db with its exact LF pin.
The native capability offers that model/effort and the existing owner is completed/available.
Use the existing owner's followup continuation, not a new seat; same-lifetime receipt/descriptor/
runner/host readback NOT_REQUIRED. Task ownership, source baseline and new ticket view are exact.
Only B1 is active. Await its finite return with wait_agent; root then runs the declared review and
adversarial evidence. ACTION_COMPLETED / EXACT_APPROVAL_AND_B1_BINDING_RECORDED ->
AUTO_CONTINUE / IMPLEMENT_CVQ01B1.

## 8. Initial review and same-owner correction — 2026-09-21

Root reviewed candidate1a1b6eb3af4c5a7e31de0d102eaf20b461c49f98; exact7171f41 ancestry,
same admitted owner/worktree/branch clean and exactly five writable paths changed. Strict21 and
focused44 green; independent probes/mutations expose B1-F01–F04. The complete batch is
[review01](../../../doc/reviews/controlled-verification/cvq-01b1-namespace-import-code-review.md)
and [evidence01](../../../doc/reviews/controlled-verification/cvq-01b1-initial-evidence.md),
resolved together by this document's registry commit. Closure01 and original authority unchanged.
Retain cve_wire_implementer, Luna/xhigh, ctx-cvq-01b1-closure01, codex/cvq-01 and its admitted
worktree. Additive correction baseline is1a1b6eb, never reset/amend or a third original-B repair.
Use the existing ticket scope/budget/commands; no B2/B3 work, new dependency or other effects.
Root awaits completion and performs the sole correction review; second failure returns convergence.
ACTION_COMPLETED / CVQ01B1_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_ADDITIVE_CORRECTION.

## 9. Correction exhausted — 2026-09-21

Same-owner additive8dc22904921cb6b0c56a88d7e224ca66828f8c14 was reviewed under closure01.
[Review02 section5](../../../doc/reviews/controlled-verification/cvq-01b1-namespace-import-code-review.md#5-correction-review--2026-09-21)
and [correction evidence01](../../../doc/reviews/controlled-verification/cvq-01b1-correction-evidence.md)
resolve in this registry commit. Strict21/focused44 and eight prior probes pass, but the
first-entry mutant still has zero red, import-form normalization remains incomplete, and relative
__future__ is accepted. Closure01 initial+correction limit is exhausted, not reset by this revision.
The previous section8 correction admission is consumed. No source mutation/third correction is
admitted. Preserve exact candidate, accepted A and closed B1-F02/F03 implementation evidence.
B2/B3 remain dependency-pending. See convergence05 section6 for a proposal only; owner decides
the bounded replan before a new exact closure can be admitted.
ACTION_COMPLETED / CVQ01B1_CORRECTION_REVIEW_COMPLETE ->
WAIT_FOR_HUMAN / CONVERGENCE_REPLAN_DECISION_REQUIRED.

## 10. Approved replan; exact residual closure02 proposal — 2026-09-21

Owner approved convergence05 section6 at `cafb4f571b80d969c28844e8a5a949b1225e3328`, LF
`9b7cd0c290b7243ec8170aece8050db2f02d172ef4677a993c59121e5bb5e553`, and added REQ-051 D8.
This transcribes that drafting grant, not a third closure01 correction. Section1's immutable
SPEC/wire/Context/profile/public seam pins remain valid; REQ-051 revision12 D8 resolves at
`1ea589b3ff416e637b2456464d49b73feae53c21`, LF
`a8d04409a8397b73bb351ac2fe3bfd85de3c49589c0e1397cc66220e7481b709`.
Source baseline is `8dc22904921cb6b0c56a88d7e224ca66828f8c14`, unapproved and preserved.

### Exact residual work and acceptance

| Cell | AST shape and independent expected observation |
| --- | --- |
| B1-R01 | In binding_contracts, `from . import qualification_values as values`, `from ..controlled_verification import qualification_values as values` and `from library.controlled_verification import qualification_values as values` all identify the same allowed internal module. Each complete nine-unit packet returns no findings, not merely identical rejection. Retain the three equivalent symbol-import forms and exact suffix/case/edge negatives. |
| B1-R02 | Only level0 `from __future__ import annotations` is external/allowed. `from .__future__ import annotations` and its normalized parent-relative spelling target a nonexistent internal module and require SG01 at the import node. Absolute unknown internal names remain SG02. Other external imports still use the closed SPEC allowlist. |
| B1-R03 | One ImportFrom contains `CapabilityFamily, Missing` from the exact allowed values module. Define CapabilityFamily; deliberately leave Missing absent. Require SG01 at that single node. The existing first-entry-only mutant must make this named assertion fail; two separate import statements cannot substitute. |
| B1-R04 | Repair the already-required direct/absolute/aliased forbidden-edge rows with reachable valid symbol definitions. Re-export fixture is acyclic and fully resolved: init -> contracts -> report -> manifest -> values, final CapabilityFamily defined in values; report -> manifest is the forbidden edge. Require SG06 on the re-export consumer and assert resolved origin, not UNKNOWN/cycle red. Keep separate original cell IDs/locations. |
| B1-R05 | Persist the exact previously observed legal six-module chain init -> contracts -> ports -> manifest -> binding -> values, final CapabilityFamily defined in values. All edges allowed; complete packet and reversed packet both return no findings. Retain ambiguity, nested-export isolation and nested-cycle regression rows unchanged. |

Reuse the existing literal corpus/MINIMUM_PACKET/replace_unit, immutable SourceUnit/SourceViolation,
symbols resolver, gate and QualificationBoundaryTests. Add rows/assertions in the existing
namespace/positive methods, not a second resolver, runner or new utility file. Independent
literal expected IDs/rules/locations remain required; gate output cannot author its own oracle.
B1-F02 and actual F03 implementation remain preserved; B2/B3 and accepted A remain untouched.

### Exact envelope and cumulative budget

`modify` is exactly the five existing paths under tests/ in section2's table; `create`, `delete`,
`rename`, new dependencies and screenshots are empty. Every other path is forbidden to the
implementer, including product source, documents, accepted A and unrelated B2/B3 behavior.
Keep technical comments/test data, never owner prompts or work-order narrative in source.
Expected residual deltas: product0; tests about0–150 net lines across those owners; implementer
documents0; screenshots0. Root appends about140 document lines to this existing ticket/convergence,
correction evidence and their existing indexes, not a new report set. Estimates trigger review,
not compression.

Budget lineage is the existing CVQ-01/B work, not a new ticket budget. Prior committed five-path
delta from accepted A485d882f to8dc2290 is 1667 additions /272 deletions, all test support; retain
that baseline accounting and previous failed attempts. Prior aggregate model/command consumption
was not completely measured and remains UNKNOWN, never zero. The D8 control edit already added
158/deleted19 document lines and ran30 existing path tests; it is not erased by this replan.
Proposed remaining execution allowance is1200 command-wall seconds shared by implementer/root,
initial/correction/review/mutations together, max60 per command, one foreground process, zero
automatic retry/load/polling. This is an explicit additional allowance for the same lineage,
not a claim that the historical total fits1200 or a fresh allowance on correction. Exhaustion
stops; unavailable host/token controls cannot be described as enforced hard caps.

All temporary outputs use a temporary directory outside the worktree, including mypy's cache
via its existing `--cache-dir` option. Existing section5 strict/focused/smoke commands otherwise
remain fixed. Root retains exact commands and unreduced results only in the existing B1 review
and correction-evidence leaves, with their existing indexes; no new evidence/screenshot files.

### Proof and continuation

Existing correction-evidence's three collected exact-form failures at8dc2290 are the real
baseline for R01/R02. Run the repaired namespace assertions against that baseline before the
guard fix; an import/collection error is not red. R04's replan preflight in correction-evidence02
observes a resolved acyclic path with only SG01, no SG06; repair the predicate as well as the data.
That printed probe is not yet a named-test red. Already-green R03/R05 properties use reviewer
mutations/retained same-SHA evidence, not fabricated baseline failures. Replay the existing
first-entry, prefix and nested-edge counter-mutations from initial/correction evidence; require
named red plus exact restore-green. Root additionally restores the relative-future bypass and
breaks package-form normalization, checking R02/R01 discrimination. No full SG01–20/A campaign.

Exact approval must bind this document06/closure02 before source dispatch. Then fresh source/
containment/profile readback, retain cve_wire_implementer Luna/xhigh and root reviewer; one
bounded retained evidence-only helper, no new seat. Direct dispatch -> wait_agent -> root review.
One initial plus one correction maximum, same envelope/remaining allowance; failure returns
convergence, not automatic expansion. Combined B1 approval is required before B2's already-approved
dependency binding. No partial integration/push/release/install or host effect.
ACTION_COMPLETED / B1_RESIDUAL_CLOSURE_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.

## 11. Exact closure02 approval and retained-owner admission — 2026-09-21

Owner **「核准」** accepts document06/closure02 at
`26fb2ad537341dd86410839ec7c829ca13a77554`, LF
`8a3d84978ae3faffaf00ed290d8b13e499b6f6efd40d8c468a3058ec20a7ae7e`.
This document07 adds only approval/allocation metadata; section10's five cells, five-path scope,
no-creation boundary, preservation and total1200-command-second allowance are unchanged.

Fresh readback: retained cve_wire_implementer is completed/available; admitted owner worktree
.worktrees/cvq-01, branch codex/cvq-01, clean HEAD8dc22904921cb6b0c56a88d7e224ca66828f8c14.
Its .git pointer/common repository agree; repository/.worktrees/owner roots have no reparse
attribute; accepted A485d882f is an ancestor. Exact ticket/SPEC/wire/Context/profile LF pins match.
Public ordinary SourceUnit/SourceViolation constructors cover all9 modules/all23 rules with frozen
records; actual-package architecture and source-set/parse tests2/2 green. Python3.11.9,
mypy2.3.0/Pydantic2.13.4 match. This is unchanged-seam preflight, not approval of remaining defects.

Close ctx-cvq-01b1-closure01 and bind ctx-cvq-01b1-closure02 to the same Luna/xhigh implementation
owner and root reviewer, profile defaults01 at797c15db. Same-lifetime bridge/receipt/descriptor/
host readback NOT_REQUIRED; reuse followup then wait_agent. No replacement owner or new worktree.
Reserve at most600 command-wall seconds of the same1200 pool for this owner attempt; root keeps
the balance for admission/review/any approved correction. Charge startup conservatively60sec,
retain observed subsequent durations, and return actual or bounded-upper usage. Unobservable
historical/model usage remains UNKNOWN. A correction receives only remaining capacity, no reset.
No model/read-only/write-interception enforcement is inferred from this allocation.
ACTION_COMPLETED / EXACT_CLOSURE02_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT_CVQ01B1.

## 12. Closure02 single correction admission — 2026-09-21

Initial candidate93273927af52246abee4f0c1972b4cb3e16944cf is not approved. Review03 section6
contains the complete F06/F07 batch under unchanged R01: missing absolute-symbol positive and
case-sensitive negative discriminators. Root reproduced both weakening mutants as ZERO_RED.
Strict21/focused44 green and repaired R02–R05 evidence remain valid, not a substitute for R01.
Retain cve_wire_implementer Luna/xhigh, same clean worktree/branch and additive baseline9327392.
Modify only the existing five-file envelope; create/delete/rename/dependencies remain empty.
Expected correction delta: product0, tests0–45 lines, documents0, screenshots0; signal not cap.
Reuse existing corpus and assertion methods; no new infrastructure. Same1200 pool, correction
reservation90 command-wall seconds, max60 each, measured duration return; no budget reset.
This is closure02's only correction. Root reruns the two discriminators, affected strict/focused
checks and retained helper review before verdict. Failure returns convergence, not more correction.
No partial integration/push/release/install. B2/B3 stay dependency-pending until B1 approval.
ACTION_COMPLETED / CORRECTION_BATCH_RECORDED -> AUTO_CONTINUE / SAME_OWNER_ADDITIVE_CORRECTION.

## 13. Closure02 correction exhausted — 2026-09-21

Candidate0e080257f923870ef504905d3ef56358d43bc94b remains unapproved. Review04 independently
closes F06 but proves F07 still ZERO_RED because CapabilityFamily is absent from the new row's
values unit. This is the same complete-prerequisite obligation, no new acceptance criterion.
Root's in-memory diagnostic proves the exact one-fixture remedy, not a delivered source change.
Closure02 initial plus correction are exhausted; B2/B3 stay dependency-pending.
Convergence08 section9 proposes one explicit exception, pending owner approval. No source
mutation, new seat/closure/budget reset, integration/push/release/installation is admitted.
ACTION_COMPLETED / B1_CLOSURE02_REVIEW_COMPLETE -> WAIT_FOR_HUMAN / OWNER_SINGLE_FIXTURE_EXCEPTION_PENDING.

## 14. Exact one-fixture exception approved — 2026-09-21

Owner approves convergence08 section9 and document09 at4c5ffac4b0a9bc236ecff43eda24d058147513fd,
LF117ca1db5ff1ed4bf1cc6d55701688fcee732bc97b75e8c2dc2ab7b37f6b8269 and
0a3ed73501003b93b244f72c45392bae6350c5e8fd60ed81616b3d9078ba0f7a respectively.
This is one explicit additional correction, not a new closure or budget. Modify only existing
tests/verification_qualification_source_corpus.py: supply the exact approved CapabilityFamily
definition to the B1-R01-mixed-case-module packet via existing _row_with_replacements. All other
source and create/delete/rename/dependency grants are empty. Preserve all row IDs/rules/locations.
Retain cve_wire_implementer Luna/xhigh/root; clean baseline0e080257f923870ef504905d3ef56358d43bc94b,
codex/cvq-01 in .worktrees/cvq-01; containment/.git/common-dir verified, no reparse attributes.
Rebind same-ticket view ctx-cvq-01b1-closure02-exception01. Bridge NOT_REQUIRED; followup/wait_agent.
Same remaining80 command-wall seconds includes startup, owner, root/helper review and closeout;
owner allocation15, max60/command, no retries or reset. Owner runs existing two methods/strict21;
root runs case-fold named red/restored-green and focused44 once. Temp outside worktree. No source
prompt/work-order narrative, new files/framework, partial integration/push/release/install.
ACTION_COMPLETED / EXACT_EXCEPTION_APPROVAL_RECORDED -> AUTO_CONTINUE / ONE_FIXTURE_CORRECTION.
