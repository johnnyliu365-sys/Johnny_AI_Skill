# CVQ-01A2 closure02 | Case evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A2-C02-CASE` / `REVIEW_EVIDENCE` / `02` |
| State | `PARTIAL / INITIAL_Q18_FINDING / REMAINDER_NOT_RUN` |
| Baseline / initial candidate | `c2fa4cdda1a785a4a8e2c7924a337c2fdd836160` / `e6099dc5926087fe5afbbfaa387471f8e001835d`; no accepted final candidate |
| Owner / finite IDs | Root only; Q01–21 / H01–04 |
| Contract | [Reviewer evidence plan](cvq-01a2-closure02-evidence-plan.md), revision01; exact digest in direct parent index |

This indexed destination now contains the initial candidate's Q18 finding and fixed checks.
Exact closure02 approval is recorded by A2 document07 at f4ecfb1. Each record binds candidate,
original hashes, exact patch/command, control, full raw mutant output, intended cell, exact
restoration and same-command green. Missing evidence
remains NOT_RUN; no family-summary or claimed pass may replace it. No implementation-source
write authority is granted by this document.

## Initial candidate Q18 — attribution defect

Candidate `e6099dc5926087fe5afbbfaa387471f8e001835d`; root reviewer snapshot, no owner-worktree writes.
Q18 rejects the legal non-HOST_MEDIATION HostCapabilityKey branch. The intended narrowing
was reached, but an eagerly constructed tuple raises before entering any C02.K subTest.
Exit1 is method-level ERROR, not the required individually attributed legal-control evidence.
This is a finding, not a passed Q18. Other finite IDs and historical cells remain NOT_RUN.

Pristine `manifest_contracts.py` byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-    def coherent_case(self) -> QualificationCase:
-        pure = self.kind in {CaseKind.PURE_RULE, CaseKind.SOURCE_PROPERTY}
+    def coherent_case(self) -> QualificationCase:
+        if isinstance(self.capability_key, HostCapabilityKey) and self.capability_key.family is not CapabilityFamily.HOST_MEDIATION:
+            raise ValueError("host keys require host mediation")
+        pure = self.kind in {CaseKind.PURE_RULE, CaseKind.SOURCE_PROPERTY}
*** End Patch
```

Control/mutant/restored command:
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

### control (exit 0)
```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.016s

OK
```

### mutation (exit 1)
```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ERROR

======================================================================
ERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_manifests.py", line 195, in test_case_applicability_rows
    ("C02.K.pure_rule.HN", qualification_case("c02-k-pure-hn", CaseKind.PURE_RULE, host_key), BindingKind.PURE_CONTRACT, NoRosterSubject, "NO_ROSTER", host_key),
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\verification_qualification_fixtures.py", line 555, in qualification_case
    return QualificationCase(
           ^^^^^^^^^^^^^^^^^^
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase
  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-pure-h...1, case_output_bytes=1)}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (errors=1)
```

### restored (exit 0)
```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

Inverse apply_patch restored logical content but two edited CRLF lines became LF; this
intermediate state is not byte-exact restoration. Root checked there was no Git content
diff, then restored only its own temporary source path from the exact candidate:
```powershell
$ErrorActionPreference='Stop'
git diff --exit-code -- library/controlled_verification/manifest_contracts.py
if ($LASTEXITCODE -ne 0) {throw 'Unexpected non-format diff after inverse patch'}
git restore --source=e6099dc5926087fe5afbbfaa387471f8e001835d --worktree -- library/controlled_verification/manifest_contracts.py
if ($LASTEXITCODE -ne 0) {throw 'Exact snapshot restoration failed'}
$b=[IO.File]::ReadAllBytes((Join-Path (Get-Location).Path 'library/controlled_verification/manifest_contracts.py'))
$s=[Security.Cryptography.SHA256]::Create()
try {$h=[BitConverter]::ToString($s.ComputeHash($b)).Replace('-','').ToLowerInvariant()} finally {$s.Dispose()}
if ($h -ne '00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354') {throw 'Byte restoration mismatch'}
Write-Output $h
git status --porcelain
```
```text
warning: in the working copy of 'library/controlled_verification/manifest_contracts.py', LF will be replaced by CRLF the next time Git touches it
00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```
Same-command green after the byte-exact restoration:
```text
test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.016s

OK
```

### Independent ordinary checks
Command:
```powershell
$ErrorActionPreference='Stop'
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
if($LASTEXITCODE -ne 0){throw 'Strict failed'}
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
if($LASTEXITCODE -ne 0){throw 'Tests failed'}
git diff --check
```
Exit0; unreduced output:
```text
Success: no issues found in 16 source files
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
Ran 27 tests in 0.485s

OK
```
