# CVQ-01A2 | Case and manifest admission review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A2` / `CODE_REVIEW` / `04` |
| Conclusion / round | `APPROVED / CLOSURE02_CORRECTION_REVIEW / NOT_INTEGRATED`; section8 is current; earlier rounds remain historical |
| Authority | [A2](../../../modules/tickets/controlled-verification/cvq-01a2-case-manifest-admission.md) document08 / closure02 at `6241b235aed9a4aebdb842ee395b1688cbfe6a65`, LF `a2053027ab11bfa0720dbecf393bd14022cc9d8b7938f97dae67ed79d2a51a65`; approved SPEC07 and wire03 unchanged |
| Source / candidate | `e6099dc5926087fe5afbbfaa387471f8e001835d` -> `ce49f735c6853c236a3504134d4a6959e7ca680f`; additive clean candidate, only the two admitted methods changed |
| Responsibility | Retained Luna/xhigh implementation owner; root ticket-review and sole verdict owner; retained Terra/xhigh evidence-only helper |
| Isolation | Root detached `.worktrees/cvq-01a2-review` at exact candidate; helper READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT; no provider, native runtime, target, integration, push or release |

## 1. Observed source and checks

Only the three declared test/fixture paths changed: domains, new manifests and shared fixtures.
No production source, schema, dependency, facade, public port or import-DAG change. The new
TestCase is explicitly imported into the compatibility domains entrypoint and collected once.
Root read the diff and relevant source, checked ancestry/cleanliness and ran strict checking
and the full focused suite. Python3.11.9 / Pydantic2.13.4 / mypy2.3.0 match the declared plan.

Every Python command below uses the existing bounded subprocess invocation, one foreground
process, timeout60 seconds, no automatic retry/load/background polling. Raw outputs below are
unreduced tool output; a green suite establishes collection, not closure completion.

## 2. Complete initial-review finding batch

Paths/lines refer to candidate95434d6. These are deficiencies against existing CM01–07,
preservation and return duties, not new product requirements. No product change is requested
where the existing predicate is already correct.

| ID / class | Existing obligation and observed location | Required correction |
| --- | --- | --- |
| A2-F01 EVIDENCE_DEFECT | Every semicolon alternative requires an independent named subcase. Manifests helpers79–97 and negative sequences121–159,192–243,245–310,357–369,371–525 have no per-cell subTest. A first failed assertion aborts remaining alternatives. R2 produces a real red without identifying the project_id cell. | Give each frozen alternative a stable literal subTest ID and separate execution. An outer method/group ID around a sequence that still aborts is insufficient. Keep the exact literal root/type/diagnostic or declared field exception. |
| A2-F02 EVIDENCE_DEFECT | CM02 legal kind/key alternatives and CA10 old assertion preservation. Positive list162–190 uses only one key per kind except discovery. Negatives202–215 change case kind, not the native binding kind while holding case kind fixed. SOURCE_PROPERTY-specific bypass R1 remains green. Earlier pure-binding->ADVERSARIAL, nonhost discovery->HOST_DISCOVERY and HOST_PROPERTY->GENERIC observations were not fully relocated. | Complete exactly SPEC11.1's applicable key alternatives and separately violate binding kind and subject variant for the frozen rows. Restore every prior observation/path, including those listed, with an actual old assertion -> new row map; method-family renaming is not that map. Preserve pure HOST_MEDIATION + NO_ROSTER as valid. Do not invent native prerequisites. |
| A2-F03 EVIDENCE_DEFECT | CM05's explicit distinct key/requirement positive control and direct QualificationPrerequisiteSet unique_ordered_keys. Lines416–425 exercise a duplicate pair but no ordinary two-distinct-requirement positive for that set. | Observe the named valid distinct pair before its one-invariant negatives, retaining ordered bijection and the exact-pair equivalent-guard exception. Rejecting all multiple-entry sets must not satisfy the test. |
| A2-F04 EVIDENCE_DEFECT | CM06 correct host pins -> missing, extra, duplicate plan. Lines427–475 test extra plans only on pure/native empty-plan manifests, not an already nonempty host plan set. R3 permits a strict superset for host plans and remains green. | Add the frozen nonempty-host extra-plan negative with the required host plan retained and a constructor-valid distinct extra plan. Keep empty-plan negatives, wrong key/ref/digest, duplicate and repeated-subject positive separately named. |
| A2-F05 EVIDENCE_DEFECT | Per-predicate exact temporary patch, command, raw output, row identity, restoration and historical reproducibility. Owner's M01–36 return and reference-only addendum describe tool batches/cell85, but root has not retrieved their raw streams. New named historical-red replay is explicitly NOT_RUN. Relocation map lists methods, not every old observation. | Return the already-required complete mapped evidence with unreduced output or exact retrievable references, and the per-observation relocation map. Keep original failed experiments and honest baseline green/red; no inferred chronology. Reuse existing captured output where authentic and retrievable, do not rerun merely for a narrative. Supply the schema-compatible named historical test patch/command and actual result. No new generic runner, helper script, unapproved write destination or resource expansion. |

For M21 the owner reports removal of referenced-case existence produces KeyError('case-missing').
That may expose a wrong-exception contract, but is not admission success or an intended
ValidationError diagnostic. Preserve the raw trace and label the evidence kind precisely;
do not turn that report into a claim of independent predicate acceptance. The CM04 redundant
membership and CM03/CM05 equivalent-guard exceptions remain exactly as written.

The helper's one bounded static return reported F01, binding-kind coverage in F02, and F03.
It did not execute tests, mutations or historical reproduction; those remain root's evidence
duties. Root independently confirms the gaps and owns this verdict. No fresh review seat,
parallel implementation or model elevation is required.

Root's mapped remainder is NOT_VERIFIED at this initial failing review, not silently passed.
One correction must return the entire frozen batch/evidence, not only R1/R3 counterexamples.
Do not weaken literal expectations to make an incidental error green.

## 3. Root checks and adversarial reproductions

### Check 1

Command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
exit $LASTEXITCODE
```

Exit 0, output:

```text
Success: no issues found in 16 source files
```

### Check 2

Command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
exit $LASTEXITCODE
```

Exit 0, output:

```text
test_alias_branch_counts_and_selector_negatives (tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives) ... ok
test_all_78_default_omission_null_and_wrong_constant_cells (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells) ... ok
test_all_81_direct_constructor_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_81_direct_constructor_and_json_rows) ... ok
test_all_result_proof_and_evidence_branches_roundtrip (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_result_proof_and_evidence_branches_roundtrip) ... ok
test_every_missing_direct_constructor_row_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_every_missing_direct_constructor_row_roundtrips) ... ok
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok
test_literal_enum_members_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows) ... ok
test_literal_wire_catalog_matches_source_ast (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast) ... ok
test_public_constructor_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_public_constructor_roundtrips) ... ok
test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... ok
test_roster_and_three_port_evidence_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_roster_and_three_port_evidence_roundtrips) ... ok
test_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok
test_approved_plan_pin_coverage (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok
test_capability_requirement_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok
test_case_and_scope_identity_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok
test_case_applicability_rows (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok
test_discovery_intent_and_property_membership (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok
test_manifest_and_prerequisite_duplicates (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok
test_prerequisite_applicability_and_order (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok
test_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok
test_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok
test_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok
test_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.361s

OK
```

### R1 — SOURCE_PROPERTY-specific kind/binding bypass (ZERO_RED)

QualificationCase.coherent_case: narrow one kind only. This differs from the owner's reported M12 whole kind/binding guard removal. All other checks stay live.

Path: `library/controlled_verification/manifest_contracts.py`. Exact temporary hunk:

```diff
-        if pure != (self.binding.kind is BindingKind.PURE_CONTRACT):
+        if pure != (self.binding.kind is BindingKind.PURE_CONTRACT) and self.kind is not CaseKind.SOURCE_PROPERTY:
```

Same control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

control, exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.016s

OK
```

mutated, exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
```

restored, exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.008s

OK
```

### R2 — project_id comparator removed (RED, no subcase ID)

QualificationManifest.unique_cases_and_requirements: only scope.project_id equality is bypassed. The output's method-level FAIL does not identify the alternative; subsequent alternatives in that sequence do not execute.

Path: `library/controlled_verification/manifest_contracts.py`. Exact temporary hunk:

```diff
-            if binding.project_id != self.scope.project_id:
+            if False:
```

Same control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

control, exit 0:

```text
test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.008s

OK
```

mutated, exit 1:

```text
test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... FAIL

======================================================================
FAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_manifests.py", line 159, in test_case_and_scope_identity_joins
    self._expect_manifest_error(payload, diagnostic)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_manifests.py", line 85, in _expect_manifest_error
    with self.assertRaises(ValidationError) as raised:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (failures=1)
```

restored, exit 0:

```text
test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.007s

OK
```

### R3 — permit extra host plans while retaining required coverage (ZERO_RED)

ApprovedManifestFound.roster_plan_coverage: permit a distinct strict superset only for nonempty expected host pins. Missing required pins, duplicates and any extra plan for empty expected pins remain rejected. Other membership predicates stay live.

Path: `library/controlled_verification/qualification_ports.py`. Exact temporary hunk:

```diff
-        if len(actual) != len(expected) or len(actual) != len(set(actual)) or any(
-            item not in expected for item in actual
+        if (len(expected) == 0 and len(actual) > 0) or len(actual) < len(expected) or len(actual) != len(set(actual)) or any(
+            item not in actual for item in expected
```

Same control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage
exit $LASTEXITCODE
```

control, exit 0:

```text
test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

mutated, exit 0:

```text
test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

restored, exit 0:

```text
test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.020s

OK
```

### Exact restoration and final regression

After each temporary mutation root restored only its own changed source path from95434d6.
Both final byte hashes equal their pristine snapshot, and git status/diff --check are empty:

- manifest_contracts.py: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
- qualification_ports.py: `0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d`.

Final same full-suite command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
exit $LASTEXITCODE
```

Exit 0, output:

```text
test_alias_branch_counts_and_selector_negatives (tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives) ... ok
test_all_78_default_omission_null_and_wrong_constant_cells (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells) ... ok
test_all_81_direct_constructor_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_81_direct_constructor_and_json_rows) ... ok
test_all_result_proof_and_evidence_branches_roundtrip (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_result_proof_and_evidence_branches_roundtrip) ... ok
test_every_missing_direct_constructor_row_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_every_missing_direct_constructor_row_roundtrips) ... ok
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok
test_literal_enum_members_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows) ... ok
test_literal_wire_catalog_matches_source_ast (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast) ... ok
test_public_constructor_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_public_constructor_roundtrips) ... ok
test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... ok
test_roster_and_three_port_evidence_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_roster_and_three_port_evidence_roundtrips) ... ok
test_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok
test_approved_plan_pin_coverage (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok
test_capability_requirement_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok
test_case_and_scope_identity_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok
test_case_applicability_rows (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok
test_discovery_intent_and_property_membership (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok
test_manifest_and_prerequisite_duplicates (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok
test_prerequisite_applicability_and_order (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok
test_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok
test_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok
test_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok
test_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.272s

OK
```

## 4. Bounded continuation

CHANGES_REQUESTED / EVIDENCE_DEFECT -> AUTO_CONTINUE / CORRECT under existing A2 closure01.
Root binds document04 and this exact review digest in the same control packet, closes the
previous view and uses `ctx-cvq-01a2-closure01-correction1`. Baseline95434d6, same owner,
worktree, profile, allowed symbols, no additional resource/mutation exception. One additive
correction only; a failed correction returns convergence, not another repair loop.

No change to accepted A1 source or evidence; A3/B remain dependency-pending. No main mutation,
integration, push, installation or publication is authorized. REQ-052's separate local
packaging/install checks remain NOT_RELEASED and do not satisfy this review.

## 5. Sole correction review — 2026-09-20

Current candidate `c2fa4cdda1a785a4a8e2c7924a337c2fdd836160` descends through
a4664f368fd332dbc38f27a04b2ad6176a288b86 from exact95434d6. One correction return comprises
those two commits, not two review cycles. The only changed path is manifests.py; source owner
and parent snapshot are clean. No product, schema, dependency, fixture owner or scope change.
Parent reused its clean detached review worktree at c2fa4cd and independently repeated strict,
focused suite, prior counterexamples and one different-door applicability mutation.

**CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED / NON_DISPATCHABLE.**
The closure01 initial + one batched correction allowance is exhausted. Do not send another
implementation follow-up, silently elevate the model or call this source approved.

| Finding | Correction disposition and evidence |
| --- | --- |
| A2-F01 | PARTIALLY_FIXED. Negative alternatives now have stable subTest IDs, and R1/R3 name their intended failing cells. CM03's separately required valid source-property/WA04 pair still constructs at manifests.py311–314 and asserts len(keys)==2 at345 outside a named cell; a positive-control defect is not attributed. |
| A2-F02 | PARTIALLY_FIXED. SOURCE_PROPERTY narrow bypass now turns its named cell red; lost subject/platform observations were restored. But lines226–249 still change only top-level case.kind in all three binding-labeled rows, not a constructor-valid opposite binding while retaining the case kind. Non-HOST family HostCapabilityKey alternatives remain absent. R4 below proves a legal-key rejection regression is invisible to CM02. |
| A2-F03 | CLOSED for the requested positive omission: lines476–481 now construct two distinct requirements under CM05.prerequisite_set.distinct_pair_positive. Root full suite passes; owner also returns a named duplicate-set mutation red. Complete matrix proof remains separate F05. |
| A2-F04 | CLOSED. The constructor-valid distinct extra Desktop plan is appended to the retained correct host plan at537–542. Parent R3 independently now fails CM06.host_subject.nonempty_extra_plan, then restores green. |
| A2-F05 | INCOMPLETE. Return supplies four correction-mutant red traces and expanded relocation mapping, but not the full M01–36 exact patch/command/control/raw-red/restored ledger. Commands in red traces are abbreviated with ellipses; family summaries and inaccessible earlier tool-cell descriptions are not authenticated raw evidence. It references genuine section14 historical probes, but does not establish the new named test extraction/collection on5d7789d. Existing historical evidence is retained, not disputed or retroactively relabeled as the missing current test proof. |

Required retained helper independently found the remaining CM03 control attribution, unchanged
case-kind-only direction and legal non-HOST host-key omission. It read immutable Git blobs only,
did not run checks/mutations, and did not assess F05. Root confirmed the source and owns the
conclusion; R4 was independently performed by root, not copied from a helper test result.
The remainder of parent predicate-matrix verification is NOT_VERIFIED after this concrete
failing review; no claim that all36 are green/red. Do not spend a full campaign to disguise
known missing rows, or infer a product defect from a test-coverage failure.

### Correction checks (raw)

Check 1, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
exit $LASTEXITCODE
```

```text
Success: no issues found in 16 source files
```

Check 2, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
exit $LASTEXITCODE
```

```text
test_alias_branch_counts_and_selector_negatives (tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives) ... ok
test_all_78_default_omission_null_and_wrong_constant_cells (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells) ... ok
test_all_81_direct_constructor_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_81_direct_constructor_and_json_rows) ... ok
test_all_result_proof_and_evidence_branches_roundtrip (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_result_proof_and_evidence_branches_roundtrip) ... ok
test_every_missing_direct_constructor_row_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_every_missing_direct_constructor_row_roundtrips) ... ok
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok
test_literal_enum_members_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows) ... ok
test_literal_wire_catalog_matches_source_ast (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast) ... ok
test_public_constructor_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_public_constructor_roundtrips) ... ok
test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... ok
test_roster_and_three_port_evidence_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_roster_and_three_port_evidence_roundtrips) ... ok
test_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok
test_approved_plan_pin_coverage (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok
test_capability_requirement_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok
test_case_and_scope_identity_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok
test_case_applicability_rows (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok
test_discovery_intent_and_property_membership (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok
test_manifest_and_prerequisite_duplicates (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok
test_prerequisite_applicability_and_order (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok
test_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok
test_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok
test_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok
test_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.328s

OK
```

### R1 repeated at correction — intended named red

Same exact SOURCE_PROPERTY-only guard hunk as section3 R1. Candidate c2fa4cd; no other predicate change.

control, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

mutated, exit 1:

Raw output encoded as a JSON string (including original trailing spaces and CRLF):

```json
"test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 249, in test_case_applicability_rows\r\n    self._expect_case_error(source_native, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 80, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nFAILED (failures=1)\r\n"
```

restored, exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

### R3 repeated at correction — intended named red

Same exact host-plan superset hunk as section3 R3. Candidate c2fa4cd; no other predicate change.

control, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage
exit $LASTEXITCODE
```

```text
test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

mutated, exit 1:

Raw output encoded as a JSON string (including original trailing spaces and CRLF):

```json
"test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... \r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 542, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(nonempty_extra, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 90, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nFAILED (failures=1)\r\n"
```

restored, exit 0:

```text
test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

### R4 — legal non-HOST family host-key branch rejected, CM02 still green

Frozen basis: approved SPEC11.1 lines435–443 and A2 CM02 require the legal key alternatives.
Ordinary HostCapabilityKey(PLAN_BINDING, WINDOWS, CODEX_CLI) cases for PURE_RULE,
SOURCE_PROPERTY, TRUSTED_NATIVE_DISCOVERY and ADVERSARIAL_WORKLOAD roundtrip on the
candidate. The inline control uses existing shared fixture functions, no new fixture owner,
file, generic mutation runner or policy.

An initial command used an invalid PowerShell here-string terminator, a root command-entry
mistake, exit1 with empty output both before/during the first mutant attempt. It executed no
Python/control and is **not evidence**. The named test was green throughout that attempt.
Corrected explicit command below is a separate diagnostic, not an automatic retry. Its valid
control actually executed before repeating this one mutant. No other campaign was repeated.

Invalid command (not counted), exit 1:

```powershell
$cm02Probe = @'
from library.controlled_verification import CapabilityFamily, CaseKind, HostCapabilityKey, HostSurface, NoRosterSubject, Platform, QualificationCase
from tests.verification_qualification_fixtures import qualification_case, native_case
key=HostCapabilityKey(family=CapabilityFamily.PLAN_BINDING, adapter_revision=1, platform=Platform.WINDOWS, host_surface=HostSurface.CODEX_CLI)
cases=(qualification_case("case-host-pure", key=key), qualification_case("case-host-source", kind=CaseKind.SOURCE_PROPERTY, key=key), native_case("case-host-probe", CaseKind.TRUSTED_NATIVE_DISCOVERY, key, NoRosterSubject()), native_case("case-host-attack", CaseKind.ADVERSARIAL_WORKLOAD, key, NoRosterSubject()))
for case in cases:
    assert QualificationCase.model_validate_json(case.model_dump_json()) == case
    print(case.case_id, case.kind.value, type(case.capability_key).__name__, case.capability_key.family.value, type(case.subject).__name__)
'
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cm02Probe
exit $LASTEXITCODE
```

```text
```

Corrected ordinary valid controls, exit 0:

```powershell
$cm02Probe = @'
from library.controlled_verification import CapabilityFamily, CaseKind, HostCapabilityKey, HostSurface, NoRosterSubject, Platform, QualificationCase
from tests.verification_qualification_fixtures import qualification_case, native_case
key=HostCapabilityKey(family=CapabilityFamily.PLAN_BINDING, adapter_revision=1, platform=Platform.WINDOWS, host_surface=HostSurface.CODEX_CLI)
cases=(qualification_case("case-host-pure", key=key), qualification_case("case-host-source", kind=CaseKind.SOURCE_PROPERTY, key=key), native_case("case-host-probe", CaseKind.TRUSTED_NATIVE_DISCOVERY, key, NoRosterSubject()), native_case("case-host-attack", CaseKind.ADVERSARIAL_WORKLOAD, key, NoRosterSubject()))
for case in cases:
    assert QualificationCase.model_validate_json(case.model_dump_json()) == case
    print(case.case_id, case.kind.value, type(case.capability_key).__name__, case.capability_key.family.value, type(case.subject).__name__)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cm02Probe
exit $LASTEXITCODE
```

```text
case-host-pure PURE_RULE HostCapabilityKey PLAN_BINDING NoRosterSubject
case-host-source SOURCE_PROPERTY HostCapabilityKey PLAN_BINDING NoRosterSubject
case-host-probe TRUSTED_NATIVE_DISCOVERY HostCapabilityKey PLAN_BINDING NoRosterSubject
case-host-attack ADVERSARIAL_WORKLOAD HostCapabilityKey PLAN_BINDING NoRosterSubject
```

Temporary patch, only QualificationCase.coherent_case in manifest_contracts.py:

```diff
     def coherent_case(self) -> QualificationCase:
+        if isinstance(self.capability_key, HostCapabilityKey) and self.capability_key.family is not CapabilityFamily.HOST_MEDIATION:
+            raise ValueError("host keys require host mediation")
         pure = self.kind in {CaseKind.PURE_RULE, CaseKind.SOURCE_PROPERTY}
```

This intentionally narrows an approved constructor domain. The probe's first formerly valid
case now rejects; the CM02 named method still passes. This is ZERO_RED for the required
matrix, not a candidate product defect and not a successful gate.
CM02 control, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

Mutated valid-control probe, exit 1:

```text
Traceback (most recent call last):
  File "<string>", line 4, in <module>
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\verification_qualification_fixtures.py", line 555, in qualification_case
    return QualificationCase(
           ^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase
  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'case-host-pu...1, case_output_bytes=1)}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
```

CM02 with mutation (ZERO_RED), exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

CM02 exact restored, exit 0:

```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

### Final restoration and bounds

Parent reviewed at exact c2fa4cd in its own detached snapshot; restored only its temporary
source paths. The final hashes match the pristine source bytes recorded in section3.
All executable review checks/mutations fell within the declared verification pass:
2026-09-20 06:27:41–06:30:49 UTC (188 seconds); no command timeout, retry loop, load or
background process. The malformed inline command is retained above, not counted as a test.
Restoration readback, exit 0:

```text
c2fa4cdda1a785a4a8e2c7924a337c2fdd836160
library/controlled_verification/manifest_contracts.py 00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
library/controlled_verification/qualification_ports.py 0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Final full regression, exit 0:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
exit $LASTEXITCODE
```

```text
test_alias_branch_counts_and_selector_negatives (tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives) ... ok
test_all_78_default_omission_null_and_wrong_constant_cells (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells) ... ok
test_all_81_direct_constructor_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_81_direct_constructor_and_json_rows) ... ok
test_all_result_proof_and_evidence_branches_roundtrip (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_result_proof_and_evidence_branches_roundtrip) ... ok
test_every_missing_direct_constructor_row_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_every_missing_direct_constructor_row_roundtrips) ... ok
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok
test_literal_enum_members_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows) ... ok
test_literal_wire_catalog_matches_source_ast (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast) ... ok
test_public_constructor_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_public_constructor_roundtrips) ... ok
test_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... ok
test_roster_and_three_port_evidence_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_roster_and_three_port_evidence_roundtrips) ... ok
test_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok
test_approved_plan_pin_coverage (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok
test_capability_requirement_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok
test_case_and_scope_identity_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok
test_case_applicability_rows (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok
test_discovery_intent_and_property_membership (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok
test_manifest_and_prerequisite_duplicates (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok
test_prerequisite_applicability_and_order (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok
test_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok
test_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok
test_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok
test_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok

----------------------------------------------------------------------
Ran 27 tests in 0.283s

OK
```

## 6. Exhaustion and convergence route

ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> CONVERGENCE_REVIEW_REQUIRED.
Close ctx-cvq-01a2-closure01-correction1. A1 remains approved; A3/B remain dependency-pending.
Keep all candidate/control refs unchanged, no integration/main write/push/release.

The remaining source work is small but the assignment still combines implementing a finite
test matrix, retaining old observations, and producing/reviewing a large raw mutation record.
Do not infer that raising model tier or asking the same request a third time fixes that
delivery boundary. [Convergence section23](cvq-01-convergence-proposal.md#23-a2-correction-exhausted-proposed-evidence-ownership-split--2026-09-20)
proposes applying A1's successful responsibility split to A2. It is a new owner decision,
not permission already inherited from A1. No new closure or evidence exception is dispatched.

## 7. Closure02 initial review — 2026-09-20

Root independently read the complete candidate delta, existing fixture identities and all
C02.K/B/P obligations. Strict checking passes16 source files; the declared focused suite
passes27 test methods. Those green checks are not acceptance. The exact commands and
unreduced output, including the independent Q18 control/mutant/restoration, are in
[case evidence revision02](cvq-01a2-closure02-case-evidence.md). Q18 fails at method level
before any named C02.K cell, proving the attribution defect rather than discharging Q18.
Remaining root-owned mutation/historical evidence is NOT_RUN, not assigned to the implementer.

One required retained Terra/xhigh helper examined immutable e6099dc against c2fa4cd,
bound to document07/closure02 and view audit-cvq01a2-c02-initial. It returned four static
findings for SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION, no commands/effects or verdict.
Root independently confirms those and the earlier C02.P masking constructor below.
This is one consolidated correction batch against existing obligations, not new acceptance.

| ID / class | Frozen obligation and observed candidate location | Correction within the two existing methods |
| --- | --- | --- |
| C02-F01 EVIDENCE_DEFECT | C02.K ordinary constructors must execute inside separately named controls. Lines193–211 eagerly construct all17 rows before subTest at212. Q18 aborts at195 with no cell ID. C02.P repeats the same defect: source_property_case at349 runs before its named control at352; original two-key assertion stays outside at395. | Construct each legal case inside its named subTest, then roundtrip and assert there. Do not build constructor-valid cases eagerly as table data. Put the C02.P constructor and preserved two-key/literal pair assertions inside its cell without an earlier identical constructor masking it. Preserve independently named negative rows; no new factory/helper/runner. |
| C02-F02 EVIDENCE_DEFECT | C02.B requires unchanged common identity. Lines276–285 replace the full binding from opposite case fixtures. Shared fixtures141–152 and181–211 set attempt-pure/scope-pure versus attempt-native/scope-native, so two common fields also change. | Keep all shared binding identity fields equal to the starting case, including attempt_key and evidence_scope_ref; construct and validate the opposite variant ordinarily, preserving case fields and native pins. Keep each fixed-kind diagnostic/root/type assertion. Do not edit shared fixtures or use bypass constructors. |
| C02-F03 EVIDENCE_DEFECT | C02.K PR/HR require the literal ordered APPROVED_SOURCE, WA04_ADAPTER pair. Rows209–210 only receive key/binding/subject assertions at212–218. C02.P's GENERIC platform row is not either WINDOWS PR/HR row. | Assert the literal ordered prerequisite pair on each of the two named PR/HR controls, preserving ordinary constructor and JSON paths. |
| C02-F04 EVIDENCE_DEFECT | The writable boundary preserves every prior assertion/value/path and GENERIC pure controls. The previous six positive roundtrip-equality assertions were replaced by four partial-field assertions; GENERIC qualification_case and source_property_case positives were removed from CM02. | Restore the GENERIC positives and full DTO roundtrip-equality observations. Reuse genuinely equivalent fixed rows for existing WINDOWS observations and identify their exact mapping; partial-field assertions are not equivalent to full equality. Preserve all other old negative and closed findings. |

No source/prompt contamination, production/schema/API/import-DAG change, extra helper or
new ownership boundary was observed. F03/F04 from closure01 remain unchanged regressions.
The entire changed surface and the helper's batch were considered together; unrun root proof
is explicitly incomplete and cannot later be represented as this candidate's approval.

ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / IMPLEMENT_CORRECTION.
Retain Luna/xhigh, codex/cvq-01 and its existing worktree. Additive correction baseline is
e6099dc; fresh view ctx-cvq-01a2-closure02-correction1 closes the initial view. This consumes
closure02's one correction, not another closure01 attempt. Root still owns all41 mutations,
five historical cells and preservation audit after the corrected candidate. No new owner
approval, source override, integration, main write, push, publication or installation effect.

## 8. Closure02 correction review — APPROVED, 2026-09-20

Root received the retained owner's typed COMPLETED for document08/closure02 and verified the
exact additive candidate ce49f735, clean owner/reviewer worktrees and two-method boundary.
No production, fixture, helper, schema, public API or import-DAG change occurs in the correction.
Source-content review found no prompt/work-order contamination. Constructor-local typed test
data only; no XSS, provider, native effect, secrets, host configuration or target mutation.

All four findings are closed:

- C02-F01: all17 K constructors/roundtrips execute inside named cells. Root's Q18 now yields
  the five HN cells and HR separately (six intended legal-domain rejections), then exact
  restoration returns green. C02.P's ordinary constructor and literal ordered-pair assertions
  are inside its cell; the pair assertion itself fixes cardinality2. Its payload is reused
  afterward, with no earlier masking constructor; the old len(keys)==2 assertion also remains.
- C02-F02: five B cells preserve the nine common binding fields and all case fields. Ordinary
  JSON validation admits each binding branch before the intended root join rejects it.
  Q12 exposes all five fixed-kind negatives; Q17 independently isolates SOURCE_PROPERTY.
- C02-F03: both WINDOWS PR/HR controls assert literal APPROVED_SOURCE,WA04_ADAPTER order in
  keys and requirements, plus ordinary construction and full DTO roundtrip equality.
- C02-F04: GENERIC pure/source full roundtrips restored, full equality in all17 K rows and
  old negatives retained. Root mapped each predecessor observation and replayed its six
  immutable old method bodies on this candidate, all green; no method-name-only audit.

Evidence is partitioned, captured unreduced and reviewed:

| Evidence leaf | Result |
| --- | --- |
| [Case evidence revision03](cvq-01a2-closure02-case-evidence.md) | Q01–21 each control0/mutant1/restored0; H01–04 old behavioral red/current green; final strict16/full27 green |
| [Manifest evidence revision02](cvq-01a2-closure02-manifest-evidence.md) | Q22–37 each named red/restored green; per-observation predecessor map and six-method replay |
| [Plan evidence revision02](cvq-01a2-closure02-plan-evidence.md) | Q38–41 each named red/restored green; H05 old extra-plan acceptance/current rejection |

Q22/Q23 are precisely diagnostic-change evidence, not admission success. Q31's additional
full-pair diagnostic red is separate from its distinct-pin acceptance red; Q32 tests the frozen
equivalent-guard pair. Q19/Q27 retain the exact approved isolation exceptions. Q18's six
ValidationErrors reject legal controls and are intended behavioral reds, not collection errors.
All41 mutation records restore exact original source-byte hashes and rerun the same command.
No zero-red, unexpected exception, skipped predicate or unrun historical cell is treated as pass.
These constructor checks prove no runtime/provider/native qualification or installation closure.

Required retained Terra/xhigh helper, view audit-cvq01a2-c02-correction1, returned NO_FINDINGS
on immutable ce49f735 versus e6099dc for SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION.
It performed no tests/mutations/effects and supplied no approval. Root independently performed
the recorded checks and alone issues this verdict.

ACTION_COMPLETED / REVIEW_APPROVED -> AUTO_CONTINUE / BIND_APPROVED_SUCCESSOR.
Close A2 correction view; retain the sequential implementation seat. A3 already has exact
owner approval; its predecessor metadata must now pin ce49f735 and this review before dispatch.
A1/A2 are APPROVED / NOT_INTEGRATED. A3/B and installation/publication remain unfinished.
No partial integration/main mutation/push/release is authorized by this verdict.
