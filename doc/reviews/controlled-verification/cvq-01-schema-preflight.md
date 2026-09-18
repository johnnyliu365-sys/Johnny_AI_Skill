# CVQ-01 schema preflight

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01-SCHEMA` / `CODE_REVIEW` / `01` |
| Phase / conclusion | `SCHEMA_CONSTRUCTION / CHANGES_REQUESTED / BEHAVIOR_NOT_ADMITTED` |
| Ticket / closure | [CVQ-01](../../../modules/tickets/controlled-verification/cvq-01-qualification-admission.md), document 03, LF `008439aa4c50dae8a21fc12143af4890a958e9be234318bb7c4269edaba7866b`, `CLOSURE-CVQ-01` revision 02 |
| Approved source | [Qualification SPEC](../../../modules/spec/controlled-verification-qualification.md), revision 04, LF `4cad6a88b9d151a05bf409f8b61bc97580e80303f58a2377cb0301815b999a1d` |
| Baseline / candidate | `892c34b7f2ee0e1bad6c4b503f813188c6a26494` / `cd228a790b2f37bc2cad109978f8822ad5bb2da6` |
| Reviewer / implementation owner | `root` / reused `cve_wire_implementer`, implementation-standard, Luna/xhigh |
| Worktree / branch | Repository-contained `.worktrees/cvq-01` / `codex/cvq-01`; same owner and branch retained |
| Authority | Owner's exact two-phase exception, recorded in ticket document 03; this is its first schema preflight, not final ticket approval |
| Helper plan | REQUIRED, candidate above, closure 02, ticket-review; SPEC_GAP, BOUNDARY_DATA, CONSISTENCY, REGRESSION; READ_ONLY_INTENT_ONLY, NO_EXTERNAL_EFFECT |

## Readback and actual checks

Root read all 12 changed files and the applicable SPEC/ticket contracts. Candidate ancestry,
clean worktree and the exact nine production/three test-file allowlist were independently read
back. No admission module or element index was created. Main and direct `origin/main` remained
`b697738d009db37318ebc8762107ef8329e014db`; no integration, push, native/host/provider execution,
installation or release occurred. The initially missing return `status` was corrected as report
metadata only; it did not change the candidate or authorize phase 2.

Development interpreter: `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe`,
Python 3.11.9, mypy 2.3.0, Pydantic 2.13.4. From the immutable candidate, root executed:

```text
python -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py
Success: no issues found in 12 source files
python -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_boundaries
Ran 10 tests; OK
git diff --check
exit 0
```

Each Python command was bounded by `subprocess.run(..., timeout=60)` with inherited unfiltered
stdout/stderr, one process/test invocation at a time. No output reducer, stress, retry or extra
suite was used. These results are real but do not establish complete CQ01/CQ02/contract-CQ11.

## Batched findings against the frozen phase-1 closure

| ID / kind / closure | Exact defect and required correction |
| --- | --- |
| S1 / IMPLEMENTATION_DEFECT / CQ01–02 | SPEC section 2 prohibits correlated nullable payloads. `ExecutionObservation`, `CaseResult`, `QualificationEvaluation` and `HostCategoryCoverage` currently use those payloads and post-validators instead of closed tagged alternatives. Implement the ordinary typed variants and exact payloads. `REPORT_REJECTED` must retain the specified `EVIDENCE_INVALID` reason; EXECUTED must retain its observer binding. Do not add nullable placeholders for fields owned by another variant. |
| S2 / IMPLEMENTATION_DEFECT / CQ02 | `QualificationManifest.active_lanes: Literal[1]` accepts JSON `true` and `1.0`, normalizing them to integer 1 despite the strict-integer contract. `PREREQUISITE_UNPROVEN` accepts a missing finite detail. `HostEffectObservation.observation: BoundedText` admits arbitrary text (`banana` reproduced), not a finite observation. Freeze these existing domains mechanically, including all boolean/float/string vectors, rather than trusting model text. |
| S3 / IMPLEMENTATION_DEFECT / CQ01–02 | `CaseResult.tagged_shape` requires `cleanup_evidence_ref` for RECOVERY_REQUIRED, but SPEC says only confirmed cleanup carries its positive evidence. An ordinary recovery refusal with independent admission evidence and no positive cleanup ref is wrongly rejected. Preserve the recovery/uncertain-launch alternative without manufacturing a successful cleanup or future launch identity. |
| S4 / EVIDENCE_DEFECT / CQ01–02 | The committed positives omit native/prelaunch/postlaunch constructors, mixed manifests, three CaseResult tags, cleanup alternatives, most finite enum values and report outcomes. The negative tests omit the every-positive-fixture required-field/null/extra matrix and most frozen primitive/ID/enum/duplicate combinations. Complete the exact finite matrix, with named variant/field assertions; a single scope/resource fixture is not every public DTO. Tests must assert field preservation, not only configuration values or equality against the same defaults. |
| S5 / EVIDENCE_DEFECT / CQ02 | The only negative CaseResult test raises while constructing an invalid nested `ExecutionObservation(checks=())` before reaching CaseResult. Disabling CaseResult's entire shape predicate leaves all 10 tests green. Correct the overlapping fixture so its unaffected nested prerequisites are valid and the actual case-result boundary produces the named failure. This is PITFALL C16, not another product requirement. |
| S6 / EVIDENCE_DEFECT / CQ11 | Neither test module contains the required executable AST dependency/forbidden-effect/bypass/facade gate. Add the phase-1 graph gate and its finite forbidden-helper/reverse-import negative controls in the declared boundary test file. No general-purpose scanner, new test framework or size threshold. The shared fixtures file is currently unused while both test files duplicate its constructors; use the one fixture owner and keep assertions in their owning tests. |
| S7 / IMPLEMENTATION_DEFECT / CQ01 constituent completeness (required by CQ04–06/09–10 later) | Approved manifest/cases carry prerequisite keys but no reachable `PrerequisiteRequirement` revision/digest pins; only caller reports carry check tuples, while `expected_oracle_ref` has no resolver; approved/discovered roster and enforcement DTOs are disconnected from manifest/report/port results. Attach the already-specified immutable requirements, expected-check identity and roster subjects to the approved graph/existing typed results. Do not implement their admission predicates in phase 1 or introduce ambient lookup, a fourth port or a second authority store. Round-trip the connected graph; standalone exported classes are insufficient. |
| S8 / IMPLEMENTATION_DEFECT / CQ01 protocol completeness (required by CQ06/09–10 later) | `AuthenticatedEvidence` has only ref/digest and no independent case/check/cleanup/roster subject binding; `EvidenceObservationPort.resolve` takes only a ref; `MissingEvidence` cannot supply rejection evidence. Complete the existing typed protocol request/result alternatives so the future evaluator can compare the authenticated subject/observer/binding and return exact rejection evidence without trusting report assertions. This is pure data/protocol work, not an authenticity adapter or signing service. |
| S9 / IMPLEMENTATION_DEFECT / CQ11 | `report_contracts.py:10` imports `CapabilityKey` from prerequisite contracts, outside the frozen report dependency allowlist. The shared immutable capability value can reside in `qualification_values.py`, letting both records depend downward while preserving the public facade. Keep explicit facades and acyclic protocol/constituent layering. Do not allow the current prohibited edge by weakening the AST gate. |

The reused Terra/xhigh adversarial helper independently returned the CQ01/CQ02 omissions,
missing prerequisite detail, correlated-null shape and absent CQ11 gate. It ran no code and
owned no verdict. Root independently confirms those findings from source and the probes below.
No future admission predicate is represented as implemented or mutated.

The helper's finite follow-up traced those existing three ports and found S7/S8/S9. Root confirms
them directly against the declared fields and imports. Their correction does not require a new
owner decision: the required data meanings and module graph are already frozen. It is not
permission to choose new product behavior. If a concrete implementation cannot preserve that
closed contract within this boundary, return CHANGE_DETECTED before making that choice.

## Independent probes and reverse mutations

Root used a detached reviewer-owned snapshot at the exact candidate, located at
`.worktrees/cvq-01-schema-review`; repository containment and absence of reparse links were read
back. Implementation source and its branch were not modified. Full unfiltered commands, named
test output and tracebacks were read directly in this task's tool transcript.

The ordinary JSON constructor probe applied one field change at a time to an existing valid
manifest or used the exact refusal/observation payload below:

```text
QualificationManifest.model_validate_json(valid_manifest with active_lanes=true)
  ACCEPTED_INVALID -> active_lanes=1
QualificationManifest.model_validate_json(valid_manifest with active_lanes=1.0)
  ACCEPTED_INVALID -> active_lanes=1
CaseResult.model_validate_json(REFUSED, valid case/manifest/binding,
  cleanup=NO_LAUNCH, refusal_reason=PREREQUISITE_UNPROVEN,
  admission_evidence_ref=evidence-admit; prerequisite_detail omitted)
  ACCEPTED_INVALID -> prerequisite_detail=null
HostEffectObservation.model_validate_json(valid exact roster key, entry-shell,
  disposition=DENIED, oracle-shell, evidence-shell, observation=banana)
  ACCEPTED_INVALID -> observation=banana
CaseResult.model_validate_json(REFUSED, valid case/manifest/binding,
  cleanup=RECOVERY_REQUIRED, refusal_reason=RECOVERY_REQUIRED,
  admission_evidence_ref=evidence-admit; positive cleanup evidence omitted)
  REJECTED_VALID -> Value error, recovery cleanup requires evidence
```

No bypass-constructed object was offered as positive evidence.

| Mutation | Command / actual result | Restoration |
| --- | --- | --- |
| M1: insert immediate `return self` into actual `CaseResult.tagged_shape` | Full declared two-module unittest command above: all 10 tests still green, zero red. This is S5, not PASS; it enters the case validator rather than the nested failing constructor used by implementation's negative example. | Removed the one temporary line; original production blob restored. |
| M2: actual `PositiveInteger` constraint `gt=0` → `ge=0` | `python -B -m unittest -v tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_positive_and_zero_only_domains_are_distinct`: five named failures (`workload_duration_seconds`, `cpu_millicpu`, `memory_bytes`, `process_count`, `disk_bytes`), each `ValidationError not raised`; exit 1. | Restored `gt=0`; full two-module suite returned 10 green. |

Restoration readback: `git diff --exit-code` and clean status; Git blobs equal HEAD for
`report_contracts.py` (`0b371eeda081c902417b3b994a12706073436e98`) and
`qualification_values.py` (`eda822734d444d75630e2c71586d181747400026`). Checkout EOL formatting
was restored mechanically, then raw bytes were compared with `git cat-file --filters HEAD:<path>`:
report SHA-256 `01906be1b53e332b94c6d6ea58218957a242b0d7a6572265cf3c45c3f47b84ae`,
values SHA-256 `8a4ff0d9bbee9e25eef454f0defe7a00ab84abece35f3d03b6b88f12cd30bf68`.
Both exact filtered-byte comparisons passed. No persistent reviewer source change remains.

## Scope and continuation

This is a failed schema preflight, not a native capability failure. No VM, host readback, runner,
receipt or provider is needed to fix these pure-contract/evidence defects. XSS, production data,
deployment and concurrency effects are excluded by the unchanged phase-1 boundary. Type-check
success cannot override the constructor, variant and dependency findings.

The owner-approved two-phase exception remains valid. Phase 2 stays NOT_ADMITTED. The same
implementation owner may perform one additive schema correction only after the complete
committed review batch is rebound; no reset/amend, new owner, admission behavior or element
file is authorized. Keep the same exact 12-file allowlist, CQ01/CQ02/contract-CQ11, strict
checker and bounded commands. Return candidate, named checks, finding dispositions, deviations
and SCHEMA_PHASE_ONLY. Parent owns the correction preflight and final verdict. No automatic
third correction is authorized. Final ticket review/integration/release are still pending.
