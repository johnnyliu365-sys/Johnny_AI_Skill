# CVQ-01B3 | Context-sensitive grammar and combined source admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B3` / `IMPLEMENTATION_TICKET` / `02` |
| State / closure | `PROPOSED / OWNER_EXACT_APPROVAL_PENDING / DEPENDENCY_PENDING / NON_DISPATCHABLE`; `CLOSURE-CVQ-01B3/01` |
| Preparation authority | Owner's 2026-09-21 approval of [B convergence01](../../../doc/reviews/controlled-verification/cvq-01b-convergence-proposal.md) at797c15db, LF0308388788c4a6a6c79ce4dd256b72bb5a231a498357a0038f305680e46f0f94; drafting only |
| Observable result / change class | Closed syntax by context plus one fully verified original B closure; `PRODUCTION_BEHAVIOR / DEFECT_CORRECTION` |
| Dependency / baseline | [B2](cvq-01b2-call-receiver-admission.md) document02/closure01 in this proposal commit, including accepted B1; actual APPROVED combined SHA and review/index must be bound before dispatch |
| Owner / reviewer / workspace | Retained `cve_wire_implementer` / `root`; sequential same `.worktrees/cvq-01`, `codex/cvq-01`; new view `ctx-cvq-01b3-closure01` |
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

## 2. Grammar ownership and writable boundary

This closes B-F03 and remaining B-F04 packet composition. It cannot change B1 import/resolution/
module-graph contracts or B2 callee/receiver/helper-cycle contracts. No source-form adjustment of
production is granted by this narrower replacement ticket. All nine production files, A tests,
literal catalog and fixtures are READ_ONLY. Inability to express their approved schema in SPEC
grammar returns CHANGE_DETECTED, not a checker exception or production edit.

| Writable path under tests/ | Allowed responsibility |
| --- | --- |
| verification_qualification_source_policy.py | A finite SourceContext enum (MODULE/FACADE/SCHEMA_CLASS/PROTOCOL_METHOD/HELPER) and immutable context vocabulary if needed; existing DAG/origins/builtins/schema-call/catalog contents remain READ_ONLY |
| verification_qualification_source_gate.py | Explicit statement/expression context traversal, class/base/module-state/facade predicates, annotation checks within _check_functions and orchestration; B1/B2 predicates may only be wired unchanged |
| verification_qualification_source_corpus.py | SG14/15/20, non-recursion SG19 and unsupported-context rows, valid SGP06, final independent ID/count/location tables; do not weaken B1/B2 rows |
| test_verification_qualification_boundaries.py | Grammar assertions, real source reader and final composition/corpus-presence assertions; no checker policy copy |

symbols.py is READ_ONLY. No new analyzer file, generic visitor framework, dependency or file-size
proxy. Typed context and closed predicates live in gate; policy owns only immutable vocabulary.
No broad try/except success, name exemption or accepted-by-default AST traversal.

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

### Context rules compiled from SPEC11.3

The following is a positive context contract, not an expanding denylist. Each statement kind
must be admitted in its actual enclosing context; traversing its children alone is insufficient.
Ast metadata (arguments/arg/keyword/comprehension/operator/context) is checked as a component of
its owning expression/statement, never treated as an independent permitted effect.

| Context | Admitted form and constraint |
| --- | --- |
| Non-facade module | Docstring, admitted import, immutable literal/tuple assignment, checked TypeAlias/schema declarations, typed module-local FunctionDef and exact catalog ClassDef. No executable module If/For/While/With/Try or free call/expression statement |
| Facade | Docstring, future import, explicit B1-validated re-export, assignment of literal tuple of strings to __all__; nothing computed, even frozenset(tuple) |
| Checked class | Correct module-owned catalog identity and exact base tuple; schema field annotations/defaults, enum literal members, ordinary typed validator/method bodies, docstring/pass, common QualificationModel's literal ConfigDict only. No arbitrary extra class/base, metaclass, class decorator, magic method or descriptor |
| Protocol method | Only one of the three catalog resolve signatures, typed non-receiver parameters/return, docstring and ellipsis/pass declaration body; declaration is not permission to invoke resolve in schema phase |
| Helper / validator / discriminator | Typed parameters/return, docstring, local Assign/AnnAssign to Name or destructuring local names, If, finite-collection For (Continue only within that loop), Return, Raise of the listed exceptions; body expressions from the next row only. Method receiver may omit annotation only in its actual admitted class/method position; module helper named self is not exempt |
| Expressions | Constant, Name, Attribute/Subscript in Load context, Tuple/Set, UnaryOp/BinOp/BoolOp/Compare, IfExp, finite synchronous ListComp/SetComp/DictComp/GeneratorExp, and Call independently admitted by B2. Starred local collection expansion is only part of an admitted collection/assignment, not a separate effect. Type annotations/aliases may use their checked subscripts/union expressions. List/Dict containers and keywords needed by exact schema declarations are limited to that context, not ambient state |
| Rejection | Every other AST form or unresolved construct yields UNSUPPORTED_SYNTAX, plus applicable named SG rule. In particular Delete, module For, Lambda, Match, NamedExpr, Try/TryStar and unlisted context forms cannot fall through |

No arbitrary expression/type checker is promised. Existing approved source forms are checked
against these SPEC predicates, not made legal merely because they appear in a green candidate.
The scalar operators are closed: UnaryOp UAdd/USub/Not/Invert; BinOp
Add/Sub/Mult/Div/FloorDiv/Mod/Pow/LShift/RShift/BitOr/BitXor/BitAnd; BoolOp And/Or;
Compare Eq/NotEq/Lt/LtE/Gt/GtE/Is/IsNot/In/NotIn. MatMult and unlisted node/operator
kinds do not qualify by a generic base-class match. Comprehensions require is_async=0 and
local-name targets; recursively check iterable/filter/body with the same context predicates.
B2 checks every nested call in an allowed expression. Store/Del targets are not attribute reads;
writes to attribute/subscript reject SG20, unsupported Delete also rejects UNSUPPORTED_SYNTAX.
Only local assignments are allowed in helpers; global/nonlocal state rejects SG15.
Async/generator functions, while and context managers retain SG19 findings irrespective of
UNSUPPORTED_SYNTAX. Finite comprehension expressions are not permission for yield/yield-from.
All function kinds, including validators/discriminators, receive full body checks.

## 3. Finite closure and final corpus

Every alternative is a distinct stable ID with literal designated rule/location. A packet is
complete nine-unit literal data with valid minimum surrounding catalog declarations/imports;
do not execute it. Overlapping rejection does not substitute for the designated rule.

| Cell / rule | Required alternatives |
| --- | --- |
| B3-G14 / SG14 | Facade function; class; initialization call; computed __all__ including frozenset; other executable expression |
| B3-G15 / SG15 | Module list; dict; set; mutable service instance; global; nonlocal. Conditional module mutable state still receives its state finding in addition to context rejection |
| B3-G19 / SG19 | Untyped parameter (including module helper named self); missing return; while; async def; await; yield; yield from; with; async with. B2 owns direct/mutual recursion and remains unchanged |
| B3-G20 / SG20 | Unapproved decorator; extra base; metaclass; magic method; descriptor/property; attribute write; subscript write. Exact catalog identity/module/base binding, not recognized spelling only |
| B3-CONTEXT / UNSUPPORTED_SYNTAX | Module For; helper Delete of attribute; Lambda; Match; NamedExpr; Try; TryStar. Each parseable AST is rejected at its own unsupported node; no blanket acceptance for unlisted kinds |
| B3-POS | Valid SGP06 approved validator **and** discriminator: declare/import QualificationModel, two distinct real catalog branches and a real catalog alias with discriminator/Tag binding; never repeated identical union branch, invented alias or unknown base. SGP01–05 remain accepted; the real-package control preserves finite-loop Continue, collection expansion and synchronous comprehensions |
| B3-COMPOSE | Every SG01–20 alternative from B1/B2/this ticket remains collected; all six exact SGP IDs; missing/duplicate/extra/syntax/unsupported/deterministic and actual nine-source checks; unchanged A full focused suite |
| B3-NONVACUOUS | Removing all negative rows or all positive rows causes its designated aggregate test to fail; restore green. IDs, counts and expected rule/locations are independently authored, not derived from the gate or enumerated actual rows |

Add `test_source_statement_admission`; it owns non-recursive grammar rows and SGP06. Existing
test_source_namespace_admission/test_source_call_admission remain independent preserved slice
tests. Aggregate test_source_negative_corpus and test_source_positive_corpus check the complete
finite union (no skipped known gap or dynamically reduced expected roster).
Positive packet validity is reviewed against wire catalog; production strict/A tests remain a
separate contract oracle. No new class name invented to make a fixture convenient.

## 4. Actual baseline and one final reviewer campaign

On the bound accepted B2 SHA, first add grammar assertions/packets only at inspect_sources and run
test_source_statement_admission: module-self annotation, helper attribute Delete and module For
must produce their specified missing-rule failures before repair. These seams already collect
at7171f41, root's five-red/control-green preflight is retained
[here](../../../doc/reviews/controlled-verification/cvq-01b-replacement-ticket-preflight.md).
Rerun on the actual B2 baseline; honest existing green plus reverse mutation is valid if an
earlier accepted change already rejects it. Collection errors/new absent types are never reds.

Root owns one final campaign at the exact combined candidate:
- One separate rule-owner reverse mutation for each SG01–20, designated owned corpus assertion
  red, byte-exact restore, same command green. Do not run this entire campaign at B1/B2 or ask
  implementer to duplicate it.
- Named mandatory doors: mutual recursion (SG19), rebound receiver and else/after-branch escapes
  (SG16), missing helper annotation (SG19), computed facade __all__ (SG14). Reuse a final-SHA
  campaign run when it proves that same door; add only the otherwise-uncovered doors.
- Put an unused renamed forbidden import into actual package: real gate red; restore bytes;
  weaken matching checker rule: designated corpus assertion red; restore green. A same final-SHA
  SG04/05 campaign entry can supply that latter proof. At least one root mutation differs from
  implementer's reported door.
- Grammar baseline corrections and corpus-removal assertions also require discriminating
  reverse-red/restored-green evidence. Bind all results to final SHA; earlier slice evidence is
  not substituted for changed code. Zero red blocks approval.

The mandatory retained helper audits exact combined candidate under SPEC_GAP/BOUNDARY_DATA/
CONSISTENCY/REGRESSION, READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. One finite evidence return;
root independently verifies findings and owns sole verdict. No separate test-execution reviewer.

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

## 6. Completion, dependency and no partial integration

Owner exact approval and combined B1/B2 accepted SHA/review/index binding are pending. After
approval of this sequential ticket set, root may record that actual SHA with clean/containment/
branch/ancestry evidence, close B2 view, bind this view and dispatch same owner; use wait_agent,
not progress polling. Same-lifetime runner/receipt/descriptor/host readback are NOT_REQUIRED.

B3 is APPROVED only when grammar/corpus, all original B alternatives, unchanged accepted A,
strict/focused suite and root's final candidate campaign pass together. Root then records the
combined schema preflight at one exact SHA and returns to Router. No partial A/B merge, no
behavior-phase implementation, native qualification, integration/push/release/installation grant.
ACTION_COMPLETED / TICKET_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING; future
combined approval is SCHEMA_PREFLIGHT_COMPLETE, not automatic publication.
