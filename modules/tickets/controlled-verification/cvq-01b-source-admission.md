# CVQ-01B | Closed qualification source admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B` / `IMPLEMENTATION_TICKET_PROPOSAL` / `01` |
| State / closure | `OWNER_EXACT_APPROVAL_PENDING / DEPENDENCY_PENDING / NON_DISPATCHABLE`; `CLOSURE-CVQ-01B` revision `01` |
| Preparation authority | Owner's adoption of convergence proposal revision 05 at `dc45f31f6c56983613665f276bf15207419274e3`, LF `6ad63ea17bf1750549d1f5087138e9bb447b477bcd8d683cac7405bed1262847`; exact source resumption is not yet approved |
| Observable result / change class | An in-process package-scoped AST gate accepts the approved source grammar and rejects the finite forbidden syntax/dependency corpus; `PRODUCTION_BEHAVIOR`, defect correction and not test-exempt or runtime confinement |
| SPEC | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, section 11.3; [wire appendix](../../spec/controlled-verification-qualification-wire.md) revision 03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222` supplies exact declaration inventory |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE |
| Upstream dependency / baseline | [CVQ-01A](cvq-01a-contract-admission.md) closure 01 APPROVED candidate, exact SHA NOT_YET_AVAILABLE; must be an additive descendant of `5d7789db6b950d317e7b500b757aa77a54d609ed`, pinned in a committed parent admission record before B dispatch, never resolved by latest branch HEAD |
| Owner / reviewer | Same retained `cve_wire_implementer` / implementation-standard; `root` / ticket-review; [profile](../../../doc/runbooks/dispatch-model-profile.md) REVISION_03, no elevation or parallel implementation |
| Workspace / allocation | Same `.worktrees/cvq-01` / `codex/cvq-01`; close A's view, new `ctx-cvq-01b-closure01`; fresh clean, containment and Git readback at the exact approved A SHA |
| Delivery / resources | POC / HIGH_ASSURANCE; one implementation owner then one mandatory evidence-only adversarial helper; finite commands below |
| Language / environment | Python 3.11.9, mypy 2.3.0, Pydantic 2.13.4; no dependency installation or new tooling |
| XSS / effects | XSS_NOT_APPLICABLE; no target-source execution by the gate, VM/host/provider effects, plugin hook, runtime sandbox, integration, push, release or installation |

## 1. Scope and dependency lock

This separately proves CQ11's verification responsibility. It does not decide arbitrary Python
purity, inspect dependency internals, qualify WA-04, or enforce host tool access. Approved
SPEC 11.3 is the only source grammar; neither the existing checker nor its green output defines
what is allowed. The prior failed [review](../../../doc/reviews/controlled-verification/cvq-01-schema-preflight.md)
revision 04 supplies mandatory regression counterexamples. All original twenty negative
families and six positive controls remain; the table below expands alternatives explicitly.

A freezes contract semantics first. B may make only the declared source-form conformance changes
and must rerun A unchanged. Any contract behavior/schema change returns CHANGE_DETECTED, not a
correction hidden in the source-analysis ticket. No phase-2 `*_admission.py` may be added.

## 2. Exact owners, seam and dependency policy

New support modules belong under `tests/`, not production or a second reusable library:

| Exact path | Sole responsibility / permitted support dependencies |
| --- | --- |
| `tests/verification_qualification_source_policy.py` | Frozen immutable module/symbol/rule vocabulary and typed records; literal public inventory references the existing catalog, no introspection or checker-derived oracle |
| `tests/verification_qualification_source_symbols.py` | AST-only import/name/alias/facade resolution and directed module/helper graphs; policy only; no grammar verdict or file/process I/O |
| `tests/verification_qualification_source_gate.py` | Closed syntax, call, receiver-flow, class, module-state and facade predicates plus combined findings; symbols/policy only, no source import/exec/I/O |
| `tests/verification_qualification_source_corpus.py` | Literal good/bad source packets and exact expected cell/rule/location data; policy records only, never import gate/symbol resolver or derive expectations from their results |
| `tests/test_verification_qualification_boundaries.py` | Reads the nine exact production files, invokes gate and asserts source/corpus/mutation results; imports the four support owners, never duplicates their policy or builds expected results by running them |

`verification_qualification_catalog.py`, fixtures, contracts tests and domains tests are READ_ONLY
for B. The policy imports only literal names from catalog; corpus has no production import. The
test driver is the sole bounded filesystem reader, never an executor for its source packets.
All support modules are strict-checked; stdlib ast/enum/dataclasses/typing are test support,
not additions to the inspected package's approved external import allowlist.

Internal test seam (no installed/public product API):

```text
SourceUnit(module: SourceModule, text: str)                         # immutable
SourceViolation(module: SourceModule, line: int, column: int, rule: SourceRule)
inspect_sources(units: tuple[SourceUnit, ...]) -> tuple[SourceViolation, ...]
```

SourceModule is exactly the nine filenames in the table below; SourceRule is SOURCE_SET,
SYNTAX_INVALID, UNSUPPORTED_SYNTAX, plus SG01–SG20. Missing/duplicate modules fail SOURCE_SET;
syntax errors fail SYNTAX_INVALID. Input is a typed tuple, not caller policy/configuration.
The test driver rejects an extra production `.py` file before forming the tuple. Findings are
deterministically ordered by module/line/column/rule; empty tuple alone means grammar accepted,
not reviewed, authentic or authorized. Internal helpers have named typed inputs/returns and
closed symbol-resolution variants, not Any, casts, dynamic object maps or swallowed exceptions.

This ticket makes the old map's phrase "contracts only" explicit: ports depend on contract
**constituents**, not the terminal qualification_contracts facade. The latter may re-export
ports without a cycle. This is the exact proposed edge table, subject to this ticket's approval;
the observed candidate table by itself is not authority.

| Source module | Permitted direct internal imports |
| --- | --- |
| `qualification_values` | none |
| `binding_contracts` | qualification_values |
| `prerequisite_contracts` | qualification_values |
| `roster_contracts` | qualification_values |
| `manifest_contracts` | qualification_values, binding_contracts, prerequisite_contracts, roster_contracts |
| `report_contracts` | qualification_values, binding_contracts, roster_contracts |
| `qualification_ports` | qualification_values, manifest_contracts, prerequisite_contracts, roster_contracts, report_contracts |
| `qualification_contracts` | the seven preceding constituents, explicit re-exports only |
| `__init__` | qualification_contracts, explicit re-exports only |

Normalize imports in every scope; both the syntactic module edge and resolved symbol origin
must be allowed. Facade traversal does not launder a forbidden edge. Module graph and helper
call graph are distinct and both acyclic, including unused definitions. Module helpers require
explicit parameter/return annotations. Model validators/discriminator callbacks get the same
whole-body checks, not a trusted-name exemption. Guarded Mapping.get is admitted only in the
true branch where the exact receiver is proven Mapping and remains unassigned; no inherited
ancestor guard, false branch or name coincidence suffices. Unsupported resolution rejects.

Nine production files under `library/controlled_verification/` may receive source-form-only
adjustments: the seven named constituents above, qualification_contracts.py and __init__.py.
Allowed symbols: existing imports/aliases/explicit exports, existing validator/discriminator
helpers' annotations and equivalent expression/control-flow forms. No DTO/enum/field/default/
constraint/predicate/signature changes, moved type owners or additional base class. Each such
diff needs an equivalence explanation and the unchanged full A suite. If a valid existing
predicate cannot be expressed in approved grammar, stop; do not broaden policy or weaken it.
All other paths, source analyzer features, effects and docs writes are forbidden to implementer.

## 3. Finite acceptance and discriminating corpus

Each listed subcase has a stable ID `SGnn-name`, one allowed control and an independently
authored forbidden packet. Other rules must be satisfied so removal of the named check causes
its rejection assertion to fail rather than being hidden by another gate. Source packets are
AST data only, never evaluated. No generic arbitrary-code execution or fuzz campaign.

| Rule / original family | Required separately named negative subcases |
| --- | --- |
| SG01 relative reverse import | direct; parent-relative normalized reverse edge |
| SG02 absolute reverse import | fully qualified constituent reverse edge |
| SG03 package-form reverse import | from-package module import; package alias then attribute reference |
| SG04 renamed import | forbidden origin hidden behind local alias; re-exported symbol alias |
| SG05 nested unused helper | forbidden import inside unused typed function; inside class method |
| SG06 facade reachability | indirect forbidden re-export; multi-hop __init__/facade resolution |
| SG07 wildcard | relative and external wildcard imports |
| SG08 module cycle | two-module cycle; self import; cycle hidden by alias/facade |
| SG09 dynamic import | __import__; aliased importlib import_module |
| SG10 eval/exec | renamed eval; renamed exec |
| SG11 reflection | getattr; setattr; aliased reflective call |
| SG12 Any/cast | Any annotation alias; typing.cast; aliased cast |
| SG13 model bypass | model_construct; model_copy(update=...); aliased checked-model bypass |
| SG14 facade logic | function; class; initialization call; computed __all__ including frozenset call; other executable expression |
| SG15 mutable module state | list; dict; set; mutable service instance; global write; nonlocal write |
| SG16 Mapping receiver | no guard; receiver reassigned after guard; guard's else; call after branch; unrelated isinstance elsewhere in condition; same-name non-Mapping method |
| SG17 callee binding | parameter shadow; local rebind; function-valued assignment alias; callable parameter; callable return |
| SG18 unresolved receiver | same-name model_validate on unknown receiver; same-name resolve on unknown receiver; unresolved computed call target; behavior-only model/port calls in schema phase |
| SG19 function/control effects | direct recursion; two-function mutual recursion unused; untyped parameter; missing return annotation; while; async def; await; yield; yield from; with; async with |
| SG20 class/write hooks | unapproved decorator; extra base; metaclass; magic method; descriptor/property; attribute write; subscript write |

The rules above own *named* findings; a blanket all-source rejection cannot pass the controls.
Except SOURCE_SET or SYNTAX_INVALID preventing analysis, inspect all rule families and accumulate
applicable findings instead of stopping at the first denial. Preserve symbol origins for forbidden
imports without importing them. Each corpus row asserts its designated rule/location is present,
not merely that some rejection happened. Where two prohibitions overlap (e.g. aliased cast),
removing one must make that rule-specific assertion fail even if the other finding remains.
No fake allowed import, weakened policy input or caller-forged resolver output is used to isolate
the test. Parse-invalid fixtures cannot prove a call/body rule. This finite diagnostic contract
makes reverse mutations distinguish overlapping guards rather than counting masked rejection.

Six positive controls, each in a complete nine-SourceUnit literal packet with valid minimum
surrounding declarations: `SGP01-explicit-facade`, `SGP02-permitted-import-alias`,
`SGP03-approved-DAG-edge`, `SGP04-unchanged-guarded-Mapping-get`,
`SGP05-typed-acyclic-local-helpers`, `SGP06-approved-validator-and-discriminator`.
Names/base classes come from the wire catalog, not a newly invented production class. The
contract suite separately owns complete public field inventory; these packets isolate grammar.
Behavior-phase receiver/port positive controls are not admitted in this schema closure.

| Test method in QualificationBoundaryTests | Required result |
| --- | --- |
| `test_architecture_dependency_gate` | inspect all nine real files at the exact final candidate, no source omissions/import execution; zero violations |
| `test_source_negative_corpus` | all SG01–SG20 named subcases reject with expected rule and source location; compare expected IDs as well as count |
| `test_source_positive_corpus` | all six SGP controls accepted, not merely no exception |
| `test_source_set_and_parse_fail_closed` | missing/duplicate/extra module, syntax-invalid source and unsupported AST/resolution produce named failures; never success-on-exception |
| `test_source_result_is_deterministic` | same packet twice yields same ordered typed findings, no subprocess/network/config lookup |

Reviewer mutates each rule owner separately and requires its intended corpus assertion red,
then byte-exact restores and observes green. Mandatory regression doors: mutual recursion,
rebound receiver, else/after-branch escape, missing helper annotation, computed facade __all__.
Additionally put an unused renamed forbidden import into the real package: real-package test
must reject; restore package, weaken the matching checker rule: corpus assertion must turn red.
At least one parent mutation differs from implementer. Zero red is a finding, not strength.

## 4. Baseline, commands, evidence and finite return

Before new analyzer work, add the mutual-recursion/rebound/computed-facade assertions against
the existing checker seam and run on the exact A candidate to capture real baseline reds.
Do not report absence of new support modules, collection failures or only the old 5d7789d
diagnostic as the new baseline evidence. Extracting the old checker for test access may not
fix it before its red; retain an exact patch/source binding for that access-only preparation.

The A candidate SHA, its APPROVED review/registry commit and this ticket's exact approval must
all be read back before dispatch. They are not supplied by arbitrary request strings. If A's
contract already fixes a named source regression, retain the green and use its reverse mutation;
do not fabricate a red. This limited evidence exception does not waive any final corpus cell.

Use the same interpreter path as A, after read-only version checks. One foreground process,
60 seconds per command, 1200 seconds per pass, zero automatic retry/stress/background polls.
The full focused suite is the three modules below; no repository-wide/native suite is invented.
Each mutation runs its corresponding fully qualified unittest method directly, then again after
restoration. Stop on budget exhaustion with BLOCKED rather than changing counts/timeouts.

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py tests/verification_qualification_source_policy.py tests/verification_qualification_source_symbols.py tests/verification_qualification_source_gate.py tests/verification_qualification_source_corpus.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains tests.test_verification_qualification_boundaries
git diff --check
```

Type checking/test imports are the source build check, real package inspection is the primary
smoke. No separate new lint/formatter dependency. Full unfiltered output must identify cell,
rule and traceback; reduced summaries alone are not mutation evidence. Required reviewer-owned
helper: exact candidate/closure, SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION,
READ_ONLY_INTENT_ONLY, NO_EXTERNAL_EFFECT; one finite evidence-only return. Parent owns verdict.

Return ImplementationReturn COMPLETED / BLOCKED / CHANGE_DETECTED, ticket/closure/control refs,
exact A baseline, additive candidate SHA, changed files/symbols, conformance-equivalence notes,
commands/results, baseline and mutation/restore evidence, findings and deviations. Owner may
commit only its source; no docs/effects/approval. Initial plus one batched correction at most;
exhaustion returns convergence, not an automatic stronger model or third attempt.

## 5. Combined admission is not integration

B is complete only with actual package gate, independent positive/negative corpus, strict typing,
unchanged A contract tests and reviewer-owned mutations green together at one exact SHA. Parent
may then record combined schema preflight for CVQ-01; later evaluator behavior still needs its
own admitted finite closure. No partial package merge, full-dispatch claim, publication or install.
Keep original and A candidates immutable; rollback is additive. Current action is docs-only
proposal, with A completion/SHA and exact ticket approval still pending.
