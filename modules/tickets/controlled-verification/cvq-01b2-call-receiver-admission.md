# CVQ-01B2 | Schema call and receiver admission

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01B2` / `IMPLEMENTATION_TICKET` / `03` |
| State / closure | `OWNER_APPROVED / DEPENDENCY_PENDING / NON_DISPATCHABLE`; `CLOSURE-CVQ-01B2/01`; section7 is current |
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
