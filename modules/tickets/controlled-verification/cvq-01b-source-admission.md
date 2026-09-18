# CVQ-01B | Closed qualification source admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B` / `IMPLEMENTATION_TICKET` / `04` |
| State / closure | `OWNER_APPROVED / DEPENDENCY_PENDING / NON_DISPATCHABLE`; `CLOSURE-CVQ-01B` revision `01` unchanged; section 7 amendment approved by section 8 |
| Preparation authority | Owner's adoption of convergence proposal revision 05 at `dc45f31f6c56983613665f276bf15207419274e3`, LF `6ad63ea17bf1750549d1f5087138e9bb447b477bcd8d683cac7405bed1262847`; exact source resumption is not yet approved |
| Observable result / change class | An in-process package-scoped AST gate accepts the approved source grammar and rejects the finite forbidden syntax/dependency corpus; `PRODUCTION_BEHAVIOR`, defect correction and not test-exempt or runtime confinement |
| SPEC | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, section 11.3; [wire appendix](../../spec/controlled-verification-qualification-wire.md) revision 03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222` supplies exact declaration inventory |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE |
| Upstream dependency / baseline | Proposed replacement: combined APPROVED [A1](cvq-01a1-scalar-wire-admission.md), [A2](cvq-01a2-case-manifest-admission.md), [A3](cvq-01a3-evidence-admission.md) at one exact candidate SHA NOT_YET_AVAILABLE; additive descendant of `070039b6227205f7bb4592f203a4fd7455311f31`, pinned in a committed parent admission record before B dispatch, never latest HEAD. Original A closure01 is exhausted |
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

`verification_qualification_catalog.py`, fixtures, contracts tests, domains compatibility aggregate,
and `test_verification_qualification_scalars.py`, `test_verification_qualification_manifests.py`,
`test_verification_qualification_evidence.py` are READ_ONLY for B. The policy imports only literal
names from catalog; corpus has no production import. The
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
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_evidence.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py tests/verification_qualification_source_policy.py tests/verification_qualification_source_symbols.py tests/verification_qualification_source_gate.py tests/verification_qualification_source_corpus.py
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

## 6. Exact approval; dependency still pending — 2026-09-18

Owner **「核准」** approves B document 01 at
`6b49847fcab325442520b04f37d950ed31992149`, LF
`94a54d8cb1b39f90976684dd195b064c3044564704c89b693e002b03c7368c05`, together with A document 01
LF `ef7509f139c2cd4d94a6ebac38fbb974ab452a625765f8a94c5aa1d3726b9eb6`.
Document 02 records that signature only; sections 1–5's boundary/closure/finite edge table are
unchanged, and earlier approval-pending wording is historical. Approval is not A completion.

Only CVQ-01A is currently admitted. B stays NON_DISPATCHABLE until parent records A's actual
APPROVED candidate SHA and exact review/registry identity, verifies unchanged closure/upstream
pins and clean worktree, closes A's view and binds `ctx-cvq-01b-closure01` to the retained owner.
That metadata binding is within this approved sequential plan and needs no repeated ceremonial
approval; a changed predicate/schema/boundary is not. No source grant before the dependency.

## 7. Dependency replacement proposal — 2026-09-19

Owner adopted convergence revision 08 at `058b8256bb1b2601fabc30c21a42ecc48c831875`,
LF `24021ef0467d56c1bc3924e98b15d2f993e0dc720228dec44177da2132c50392`.
It authorizes drafting three finer contract closures, not another correction of exhausted A.
Document 03 proposes replacing B's impossible dependency on A closure01 approval with combined
A1/A2/A3 approval at one source SHA, and naming their read-only tests in the strict command.
References to the "A candidate/suite/view" in sections 1–5 mean that combined accepted contract
candidate/suite and the last A3 view if this amendment is approved. Section 6's original admission
route is historical; it cannot authorize further A closure01 source writes.

No change to B closure01's SG01–SG20, six controls, source grammar, API, writable scope or
resource budget. The full unittest command remains contracts + domains + boundaries: domains
explicitly collects all three split TestCases once, not by copying assertions. B must preserve
their exact accepted predicate coverage; newly readable test paths are not new write permission.

Exact owner approval of this document03 dependency amendment is pending with the three tickets.
After it is approved, root records their actual combined APPROVED SHA/review/index commit and
clean identity before B dispatch. That later SHA binding is metadata, not another design approval.
No merge/push/release/evaluator grant. ACTION_COMPLETED / DEPENDENCY_AMENDMENT_PROPOSED ->
WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING; B remains NON_DISPATCHABLE.

## 8. Exact dependency amendment approval — 2026-09-19

Owner **「核准」** approves document03 at `b12dd7262606f7b951271cd51e336747f0638c38`,
LF `b37cf26e6e1fa35f623026128fac551433ed22e87d4627032db33efd57dc6489`.
Document04 is signature/status only. The approved base source closure and section7 dependency/
read-only-path amendment are unchanged. B awaits actual combined A1/A2/A3 review approval and
its committed exact candidate/view binding, not another owner approval. No source dispatch now.
ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> DEPENDENCY_PENDING. No integration/push/release.
