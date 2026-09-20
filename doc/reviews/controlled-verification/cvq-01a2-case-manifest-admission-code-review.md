# CVQ-01A2 | Case and manifest admission review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A2` / `CODE_REVIEW` / `01` |
| Conclusion / round | `CHANGES_REQUESTED / NOT_INTEGRATED`; closure01 initial review, one complete correction batch below |
| Authority | [A2](../../../modules/tickets/controlled-verification/cvq-01a2-case-manifest-admission.md) document03 / closure01 at `04cc47a367d9aa073c3a905e61ee59ea8a34ce47`, LF `ba105f4d21d13e9c9659a019d688fbda28c66142861b7e23c32f1c7bfdfe1815`; approved SPEC07 and wire03 unchanged |
| Source / candidate | `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc` -> `95434d64a4538270ebc4b4b785ae74337379f61e`; exact parent, clean owner worktree |
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

