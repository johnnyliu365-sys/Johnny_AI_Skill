# CVQ-01A1 | Scalar and wire admission review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A1` / `CODE_REVIEW` / `03` |
| Conclusion / round | `BLOCKED / TICKET_DEFECT / EVIDENCE_AMENDMENT_PENDING`; section 7 is current; closure01 remains exhausted |
| Current authority | [A1](../../../modules/tickets/controlled-verification/cvq-01a1-scalar-wire-admission.md) document06 / closure02 at `0aa0184e9db460be2aaaa513c30d6636f18ae2d1`; exact signature and LF digests in section7; sections1–6 preserve closure01 history |
| Source / candidate | Current `1270664213d71eb2da524ecf7bf1885f28ffc82f` -> `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc`; previous `070039b6227205f7bb4592f203a4fd7455311f31` -> `b1aa3fafaf03a7c47a869210b3934399124df933` -> `1270664213d71eb2da524ecf7bf1885f28ffc82f` preserved |
| Owner / reviewer | Retained `cve_wire_implementer`, implementation-standard; root, ticket-review and sole verdict owner |
| Isolation / effects | Current parent detached `.worktrees/cvq-01a1-review-c02`; earlier snapshots preserved; helper `READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT`; constructor-local tests only, no host/provider/target/VM/runtime effect |

## 1. Identity and observed checks

Parent read the exact ticket, wire, candidate diff and relevant methods, verified ancestry and
clean owner worktree. Exactly three declared paths changed: domains, scalars and fixtures.
Production source is unchanged. No new dependency, suppression, public schema or evaluator is
introduced. Scalar tests are explicitly imported into the existing domains entrypoint; all four
new methods execute once in the complete 26-method suite. No separate scalar input is passed to
that full-suite command. Non-scalar domain methods remain unchanged.

Parent used Python 3.11.9, Pydantic 2.13.4 and mypy 2.3.0. Each Python command is bounded by
`python -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)'`
followed by the exact Python executable and arguments. One foreground process, no load/retries,
no output-reducing wrapper. Full outputs were read before assigning results.

```text
python -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
Success: no issues found in 15 source files (exit 0)
python -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
Ran 26 tests in 0.236s; OK (exit 0)
git diff --check 070039b6227205f7bb4592f203a4fd7455311f31 b1aa3fafaf03a7c47a869210b3934399124df933
exit 0
```

These checks establish collection/type availability, not completion of SW01-08. Catalog totals
remain the independently recounted 81/413/335/78/751; do not revive the superseded 333/747 claim.

## 2. Complete initial-review finding batch

All paths below are relative to candidate b1aa3faf. All findings concern already-frozen A1
requirements; none grants a schema, validator, scope, resource or architecture change.

| ID / class | Existing closure and location | Gap and required correction |
| --- | --- | --- |
| F01 `EVIDENCE_DEFECT` | SW01/SW03, finite catalog; contracts `:211-290`, catalog `:11-252` | The inventory compares field names/defaults but never field annotations; Protocols/QualificationModel are skipped without independent expected inventories for the three ports/bases. Actual alias membership is not compared: source substring presence and successful expected branches do not exclude extras. Complete literal expected types, closed alias and port/base inventories and compare actual observations to them. Keep expected data in the catalog, ordinary fixture/TypeAdapter controls, and all current counts. Do not derive expected values from production. No new production mutation permission is inferred by this finding. |
| F02 `EVIDENCE_DEFECT` | SW02/SW03; contracts `:327-396`, `:419-429`, `:472-480`, `:514-525` | Required-null rows use broad field-name family alternatives (enum/literal, model/dict), not the literal expected error tuple for each field. They have no per-cell subTest ID. Default null/wrong and selector negatives merely catch ValidationError or TypeError/ValueError without the required exact type/location or declared callable-selector form. Supply literal finite per-row expectations and named cells; unrelated rejection cannot count. Preserve the integer-vs-Literal default distinction and the CaseResult/EvidenceResolution exceptions specified by the ticket. |
| F03 `EVIDENCE_DEFECT` | SW04 / CA10 preservation; scalars `:65-107`, `:159-178`; baseline domains `test_scalar_domains_and_all_bounds` | Relocation drops `a_case` and `a.case` negatives. Parent M2 proves accepting both is invisible to the named method. Baseline JSON negative-counter and Lane 0/2 rows are replaced by constructor-only edge rows, not fully preserved as recorded. Restore all predecessor values/path-specific assertions and provide the actual old-method -> new subTest row map. The return's three additional old method names do not occur in this baseline; correct the mapping, do not invent history. |
| F04 `EVIDENCE_DEFECT` | SW08; contracts `:907-910` | Only frozen/extra flags are asserted. The named method does not assert strict/validate_assignment/revalidate_instances, ordinary assignment's frozen_instance location, or tuple-array/scalar/null behavior. Parent M1 changes revalidate always to never and leaves both the named method and all 26 tests green. Complete exactly the frozen SW08 observations and its two independent mutation doors. |
| F05 `EVIDENCE_DEFECT` | Ticket evidence/return; SW01-08 | The completion return gives mutation-family summaries, not the pinned per-predicate patch/command/exit/cell/restoration map. SW08 reports frozen only, and SW01 does not distinguish the required row-removal and real-default experiments. Parent has not authenticated the missing transcript outputs and marks them NOT_VERIFIED, not failed runs. Supply the already-required complete evidence with exact retrievable output references or unreduced output, distinguish honest baseline green from red, and do not call a zero-red experiment success. Preserve source/fixture responsibility and bounded execution; no new helper script or generic mutation framework. |

SW05-07's new methods execute and visibly contain the strict-domain, edge and nine-bound rows.
Their full mutation matrix remains NOT_VERIFIED by the parent at this initial failing review;
it is not silently passed. The one correction must return all frozen evidence together, not only
the two counterexamples below. SW01/03 existing positive and enum tests must be preserved.

## 3. Parent independent counterexamples

Both experiments changed only the parent's clean, candidate-bound snapshot, never the owner's
worktree. Both enter through doors absent from the implementer's reported frozen/whole-pattern
examples. Patches were restored before subsequent runs. Git object for qualification_values.py
after restoration is `64dfe86ceab3d22ac859723437d1e99dc05cd209`; pristine checked-out bytes
SHA-256 `f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97` matches before/after M2.

M1 patch, QualificationModel.model_config:

```diff
-        revalidate_instances="always",
+        revalidate_instances="never",
```

Command: `python -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration`.
Unreduced output, exit0 (the defect is ZERO_RED):

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

The full two-module suite also remained exit0, 26 OK, 0.201s; parent read every method line.
After exact-source restoration the same named command was exit0, 1 OK, 0.000s. This is not
red/green proof and is recorded as F04.

M2 patch, OpaqueMetadataId pattern:

```diff
-    StringConstraints(pattern=r"^[a-z][a-z0-9-]{2,127}$"),
+    StringConstraints(pattern=r"^[a-z][a-z0-9._-]{2,127}$"),
```

Command: `python -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains`.
Unreduced output, exit0 (ZERO_RED):

```text
test_identifier_digest_text_domains (tests.test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

After byte restoration the same named command was exit0, 1 OK, 0.003s; clean git status. This
is F03, not evidence that accepting separators is permitted. Temporary CRLF restoration was
resolved inside the reviewer snapshot from the exact candidate; no owner file was overwritten.

## 4. Bounded adversarial evidence and applicability

Retained helper returned four static FINDINGS at this exact candidate: catalog closure,
dropped separator rows, broad errors and incomplete configuration checks. Parent independently
read the implicated source; M1/M2 validate the latter and dropped-row defects behaviorally.
The helper's suggested alias/field-type mutations were NOT_RUN and exceed the ticket's named
read-only-symbol exceptions; they are not permission to perform them. F01 rests on the actual
missing assertions and frozen catalog requirement, not invented experimental evidence.

The helper initially misreported an unavailable method reference. A bounded reference-only
addendum resolved the complete candidate blob `8c8d9a2839fedf69c87ddbcb98f004fad1578ac0` for
skills/johnny-project-takeover/references/adversarial-review.md, retained its four findings and
reported no remaining scope deviation. No second code audit, tests or mutations were requested
from it. Parent owns the conclusion; the helper has no approval authority.

REQUIRED / SPEC_GAP, BOUNDARY_DATA, CONSISTENCY, REGRESSION /
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. No UI/XSS, migration, dependency update, privileged
capability or production deployment exists in this three-test-file patch; those effect-specific
checks are NOT_APPLICABLE here, not runtime readiness claims. Same-lifetime reviewer orchestration
requires no runner/receipt/descriptor. No main/staging/push/release effect is authorized.

## 5. Return and continuation

ACTION_COMPLETED / CHANGES_REQUESTED -> AUTO_CONTINUE / one additive A1 correction on
codex/cvq-01 from b1aa3faf, same owner/profile/worktree and closure01, binding A1 document03
and this review at their committed control revision. No reset/amend/force or model elevation.
A2/A3/B remain dependency-pending. Correction review is the final review for closure01; remaining
blocking defects return CONVERGENCE_REVIEW_REQUIRED, not a third correction.

Host incident is separate: a parent-session request received HTTP400 unsupported_parameter for
access_programs.cyber. Its parameter-injection source is unproven. No account/plugin/config
change was made. Native owner reuse ultimately returned the candidate through wait_agent;
the failed duplicate-name spawn created no new seat. The repository's evidence gaps above are
independent of that transient host failure.

## 6. Final correction review — 2026-09-19

Authority: A1 document03 / unchanged closure01 at
`c21201a0ede84bed8bf2fe564f68fc979285bd4b`, LF
`d26bc6466159bf51beb92adb6c7fcf6f1ef7cbe10ef0b8d8636b4edb542f8e98`, and review revision01
LF `820dd1ad30fcfea456f85e83d654ed2d1da3733cab1d2d8c65eac43ddc1e0463` at the same commit.
Candidate `1270664213d71eb2da524ecf7bf1885f28ffc82f` is an additive descendant of b1aa3faf.
The retained owner returned it directly; no owner relay or replacement seat was needed.

Parent verified clean owner HEAD, ancestry, exact three-path correction diff (contracts,
scalars, catalog), unchanged production source and diff check. In a new reviewer-owned detached
`.worktrees/cvq-01a1-review-correction`, the section-1 strict command returned exit0, 15 files;
the exact complete suite returned exit0, 26 OK in 0.349s. Final restored rerun was exit0,
26 OK in 0.238s. All 26 method names were read, without an output-reducing wrapper.

### Disposition of the original batch

| Finding | Parent disposition | Evidence / residual |
| --- | --- | --- |
| F01 | Static correction present; no remaining missing-inventory finding in this review | contracts `:218-402` now compares literal annotations, aliases, ports and schema bases. Data remains in catalog. This does not claim every possible future AST attack was run. |
| F02 | **OPEN / EVIDENCE_DEFECT** | contracts `:447-469` still runs 670 omission/null and 81 extra checks without any per-cell subTest ID. Selector checks `:554-619` identify alias/branch only, not the missing/null/unknown alternative. Literal error types/locations are improved, but the ticket's explicit one-in-process-ID-per-alternative rule and initial F02 remain unmet. Parent R0 below fails without the required DTO.field/cell identity. |
| F03 | Closed for the recorded relocation loss | underscore/dot and JSON counter/Lane rows restored in scalars; parent R2 gives two distinct named failures, restoration green. No additional nonexistent predecessor method is credited. |
| F04 | Closed | all five base configuration assertions, ordinary frozen assignment and tuple JSON boundaries are present; parent R1 gives the intended revalidation assertion red and restoration green. |
| F05 | **OPEN / NOT_FULLY_VERIFIED** | Return again provides family summaries, not the complete pinned patch/command/cell/unreduced-output map or retrievable transcript references. Its discriminator summary explicitly reports PydanticUserError, which is not the required collected behavioral red. It also describes a QualificationScope.project_id optional mutation, whereas the temporary read-only-symbol grant names LaunchObservation.observation_revision; without the patch/output, neither compliance nor the alleged run is independently established. Parent ran the authorized door instead. Remaining unobserved matrix rows stay NOT_VERIFIED, not fabricated failures or passes. |

The retained required adversarial helper independently returned F02-RESIDUAL for the same
candidate and exact lines. It fully read the candidate's method reference, supplied static
evidence only and reported tests/mutations NOT_RUN. Parent reproduced the residual attribution
problem behaviorally and alone owns this conclusion. Its F01/F03/F04 static observations agree
with the parent's actual diff and counterexamples.

### Parent correction-round experiments

All named commands use the section-1 bounded invocation, exact candidate snapshot, ordinary
fixtures and existing unittest entrypoints. No new runner/test script/framework was created.
Temporary edits were restored before the next experiment; clean Git status and exact checked-out
SHA-256 were read back: qualification_values.py
`f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97`, binding_contracts.py
`5e8f1a73977f4ac8b29cfb919548d21b33c2eb63e2f277dc3aa2b7fb7c88fd8b`.

| ID | Exact temporary change | Named method (prefix below) | Observed mutation -> restoration |
| --- | --- | --- | --- |
| R0 | binding_contracts.LaunchObservation.observation_revision: `PositiveInteger` -> `PositiveInteger = 1` | contracts.test_required_null_and_extra_json_matrix | exit1, one collected failure `ValidationError not raised`; exit0, 1 OK, 0.111s after restore. Unlike the implementer summary's Scope field, this is the explicitly authorized SW02 surface. |
| R1 | QualificationModel.model_config revalidate_instances: `always` -> `never` | contracts.test_immutable_contract_configuration | exit1 at exact `never != always` assertion; exit0, 1 OK, 0.001s after restore |
| R2 | OpaqueMetadataId alphabet: `[a-z0-9-]` -> `[a-z0-9._-]`, same length anchors | scalars.test_identifier_digest_text_domains | exit1, exactly two subTest failures identifying project_id/a_case and project_id/a.case; exit0, 1 OK, 0.002s after restore |
| R3 | binding_contracts.AttemptBinding: `Field(discriminator="kind")` -> `Field()` | contracts.test_alias_branch_counts_and_selector_negatives | exit1 with three collected assertions, not import failure; the missing-kind control is accepted and fails `ValidationError not raised`. Exit0, 1 OK, 0.055s after restore |

Command prefixes: contracts =
`python -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.`;
scalars = `python -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.`.
Append the exact method above. Full process stdout/stderr was read for every run. Unittest itself
abbreviated two large tuple diffs in R3; those abbreviations are not claimed as a full error-location
inventory. Its third complete missing-selector failure supplies the behavioral counterexample.
R0 is an independent door, different from the implementer's reported optional Scope field.

R0's complete unittest output (absolute file prefix is the snapshot above):

```text
test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... FAIL

======================================================================
FAIL: test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a1-review-correction\tests\test_verification_qualification_contracts.py", line 460, in test_required_null_and_extra_json_matrix
    reject(payload, type(row), field, ("missing",))
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a1-review-correction\tests\test_verification_qualification_contracts.py", line 440, in reject
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.019s

FAILED (failures=1)
```

This is a real behavioral red, but its output cannot distinguish the required DTO/field/cell;
the mutation patch supplies that identity externally. The closure expressly requires the cell
itself to be identified in-process, so this is not a waiver of F02. No additional source edit
or third correction is authorized by the reviewer's ability to describe the missing ID.

### Current return

ACTION_COMPLETED / CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED -> WAIT_FOR_HUMAN /
OWNER_CONVERGENCE_DECISION_REQUIRED. Close ctx-cvq-01a1-closure01; preserve both candidates and
the source branch. A1 document04 is BLOCKED/NON_DISPATCHABLE; A2/A3/B remain dependency-pending.
Do not disguise a third correction as a renamed ticket, reopen old exhausted closures, elevate
the model or waive evidence. A new convergence decision must explicitly address the remaining
cell-identification/evidence-production gap before any new closure or exception is admitted.
No main integration, push, release, installation, VM or provider effect occurred.

## 7. Closure02 initial review — 2026-09-20

Authority: document06 at `0aa0184e9db460be2aaaa513c30d6636f18ae2d1`, LF
`dd3d3e7ec24c9045f5bdf20dd686557212eb05f6b75865efc7368eda5bb0d0cb`; owner explicitly approved
document05 at `1e50d2ef457a7a5de392fb8b34eb9fc2a8f51011`, LF
`d25b6c3b3f873a95eccea88e0e8ab222848cb67b5a87ace23958b480a85d0bbf`.
Candidate `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc` descends directly from 12706642.
Root read its complete one-file diff: only the three permitted methods change, 92 insertions /
35 deletions of subTest attribution/nesting, no production or fixture change. All prior values,
assertions, error tuples and counts remain. Owner worktree and root detached review snapshot
were clean. No prompt/work-order material was added to source.

### Scoped results and custody

The retained implementation seat returned natively, then supplied its exact-candidate M03
experiment from `.worktrees/cvq-01a1-owner-example-c02`. A reference-only raw-output addendum
filled its initially abbreviated return without rerunning the test. Root independently ran
M03, which now identifies LaunchObservation/observation_revision/json/missing. This resolves
the old F02 attribution defect within the current source boundary.

Root ran all 35 finite experiments in `.worktrees/cvq-01a1-review-c02`; every mutated command
returned exit1 and every restoration returned exit0 with pristine source-byte hashes. This is
execution, not blanket approval: M02 C3 is the wrong reason, and remaining repetitive raw
streams are retained but not all fully read through for a final predicate-by-predicate verdict.
No missing output is replaced by a hash or a family-summary claim.

- [SW01–03 complete captures and owner M03](cvq-01a1-closure02-sw01-03-evidence.md).
- [SW04–06 complete captures](cvq-01a1-closure02-sw04-06-evidence.md), including root M18's
  independent NonNegativeInteger strictness door, distinct from owner M03.
- [SW07–08 complete captures and final commands](cvq-01a1-closure02-sw07-08-evidence.md).

Final exact strict command: exit0, 15 source files. Complete contracts+domains suite: exit0,
26 tests in 0.227s. No duplicate scalar entry, extra suite, retry, load or new runner. Diff
check and restored status are clean. These greens do not waive the M02 defect.

Required adversarial helper, retained `profile_delivery_audit`, returned `NO_FINDINGS` for the
exact candidate's narrow static patch only. It checked independent subTest nesting and preserved
counts/selector behavior at contracts lines460–515,568–668,706–740. Its tests/mutations were
NOT_RUN; root alone owns the verdict. Plan: REQUIRED / SPEC_GAP, BOUNDARY_DATA, CONSISTENCY,
REGRESSION / READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. No deployment/VM/provider effect.

### C02-F01 — TICKET_DEFECT (root-authored M02 plan)

The frozen M02 changes ResourceBounds.automatic_retry_count's default from0 to1. C1 correctly
detects the changed source default. But C3 begins with `all_direct_rows()` (contracts:479).
The ordinary resource_bounds fixture omits automatic_retry_count (fixtures:477–484), so
QualificationCase's nested revalidation rejects the mutated1 before the named omission cell.
Full trace: `resource_bounds.automatic_retry_count / less_than_equal / input_value=1`.

The required observation was a collected named omission assertion comparing1 with literal0.
An early fixture ValidationError does not satisfy it. The approved source change allowed only
subTest attribution/nesting and explicitly forbade fixture changes; this cannot be assigned as
an in-boundary implementer correction. The same earlier-gate masking family is already recorded
in PITFALL-REGISTER C16. Root should have checked fixture reachability before freezing this ledger.

Document07 proposes one temporary reviewer-fixture keyword `automatic_retry_count=0`, retaining
the real-default mutation and all validation guards. It is pending exact owner approval, not
executed or represented as proven. No product/default fix is requested. The initial source
implementation is retained; the closure02 correction allowance is not spent on a control defect.

ACTION_COMPLETED / TICKET_DEFECT -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING for the
bounded evidence exception. A1 is not approved; A2/A3/B remain dependency-pending. Do not
repeat the full campaign, demand a third closure01 correction, integrate, push or release.
