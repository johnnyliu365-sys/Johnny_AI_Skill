# CVQ-01A2 closure02 | Case evidence

## Final restored candidate checks

Candidate ce49f735; no remaining temporary source diff; owner worktree also clean at this SHA.
Strict16 source files and focused27 test methods pass independently of the owner's return.

```powershell
$ErrorActionPreference='Stop'
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
if($LASTEXITCODE -ne 0){throw 'Strict failed'}
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
if($LASTEXITCODE -ne 0){throw 'Tests failed'}
git diff --check
```

Exit0; unreduced output:

```json
"Success: no issues found in 16 source files\r\ntest_alias_branch_counts_and_selector_negatives (tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives) ... ok\r\ntest_all_78_default_omission_null_and_wrong_constant_cells (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells) ... ok\r\ntest_all_81_direct_constructor_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_81_direct_constructor_and_json_rows) ... ok\r\ntest_all_result_proof_and_evidence_branches_roundtrip (tests.test_verification_qualification_contracts.QualificationContractTests.test_all_result_proof_and_evidence_branches_roundtrip) ... ok\r\ntest_every_missing_direct_constructor_row_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_every_missing_direct_constructor_row_roundtrips) ... ok\r\ntest_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok\r\ntest_literal_enum_members_and_json_rows (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows) ... ok\r\ntest_literal_wire_catalog_matches_source_ast (tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast) ... ok\r\ntest_public_constructor_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_public_constructor_roundtrips) ... ok\r\ntest_required_null_and_extra_json_matrix (tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix) ... ok\r\ntest_roster_and_three_port_evidence_roundtrips (tests.test_verification_qualification_contracts.QualificationContractTests.test_roster_and_three_port_evidence_roundtrips) ... ok\r\ntest_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok\r\ntest_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok\r\ntest_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok\r\ntest_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok\r\ntest_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok\r\ntest_approved_plan_pin_coverage (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok\r\ntest_capability_requirement_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\ntest_case_and_scope_identity_joins (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\ntest_case_applicability_rows (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\ntest_discovery_intent_and_property_membership (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok\r\ntest_manifest_and_prerequisite_duplicates (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\ntest_prerequisite_applicability_and_order (test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\ntest_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok\r\ntest_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok\r\ntest_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok\r\ntest_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 27 tests in 0.423s\r\n\r\nOK\r\n"
```


| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A2-C02-CASE` / `REVIEW_EVIDENCE` / `03` |
| State | `COMPLETE / Q01_21_VERIFIED / H01_04_REPRODUCED` |
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
## Corrected candidate predicate campaign

Pinned candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`, authority document08/closure02 at6241b235.
Root ran one finite pass per partition with one foreground process,60s/command,
zero retries, load, containers or background polling. No tool output reducer was used.
After each mutation only its exact source path was restored with
`git restore --source=ce49f735c6853c236a3504134d4a6959e7ca680f --worktree -- <recorded path>`;
byte hash equals the pristine hash and Git status is empty before the restored green run.
These restorations remove only root's own temporary review mutations.
Q22/Q23 prove diagnostic change only; Q31's extra full-pair red is diagnostic change,
while its intended distinct-pin row proves missing rejection. Q18 is legal-domain narrowing.

### Q01 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.binding.case_id`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if self.binding.case_id != self.case_id:
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.binding.case_id') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.binding.case_id')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 130, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  }
}
```

### Q02 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.binding.fixture_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if self.binding.fixture_digest != self.fixture_digest:
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.binding.fixture_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.binding.fixture_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 130, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  }
}
```

### Q03 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.native.executable_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.binding.executable_digest != self.executable_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.executable_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.executable_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 154, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  }
}
```

### Q04 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.native.dependency_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.binding.dependency_digest != self.dependency_digests[0]:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.dependency_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.dependency_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 154, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  }
}
```

### Q05 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.native.argv_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.binding.argv_digest != self.argv_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.argv_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.argv_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 154, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nOK\r\n"
  }
}
```

### Q06 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.native.cwd_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.binding.cwd_digest != self.cwd_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.cwd_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.cwd_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 154, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nOK\r\n"
  }
}
```

### Q07 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.native.environment_plan_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.binding.environment_plan_digest != self.environment_plan_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.environment_plan_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.native.environment_plan_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 154, in test_case_and_scope_identity_joins\r\n    self._expect_case_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.011s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.011s\r\n\r\nOK\r\n"
  }
}
```

### Q08 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.scope.project_id`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if binding.project_id != self.scope.project_id:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.project_id') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.project_id')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 166, in test_case_and_scope_identity_joins\r\n    self._expect_manifest_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q09 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.scope.baseline_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if binding.baseline_digest != self.scope.baseline_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.baseline_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.baseline_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 166, in test_case_and_scope_identity_joins\r\n    self._expect_manifest_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.015s\r\n\r\nOK\r\n"
  }
}
```

### Q10 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.scope.manifest_revision`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if binding.manifest_revision != self.scope.manifest_revision:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.manifest_revision') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.manifest_revision')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 166, in test_case_and_scope_identity_joins\r\n    self._expect_manifest_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q11 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM01.scope.manifest_digest`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if binding.manifest_digest != self.scope.manifest_digest:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... \r\n  test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.manifest_digest') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) (cell='CM01.scope.manifest_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 166, in test_case_and_scope_identity_joins\r\n    self._expect_manifest_error(payload, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_and_scope_identity_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_and_scope_identity_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q12 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.binding_kind.pure_rule_native_binding`, `CM02.binding_kind.pure_binding_adversarial`, `CM02.binding_kind.source_property_native_binding`, `C02.B.pure_rule`, `C02.B.source_property`, `C02.B.trusted_native_discovery`, `C02.B.adversarial_workload`, `C02.B.real_host_property`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if pure != (self.binding.kind is BindingKind.PURE_CONTRACT):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.024s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.pure_rule_native_binding') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.pure_binding_adversarial') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.pure_rule') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.source_property') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.trusted_native_discovery') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.adversarial_workload') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.real_host_property') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.pure_rule_native_binding')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 373, in test_case_applicability_rows\r\n    self._expect_case_error(native, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.pure_binding_adversarial')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 378, in test_case_applicability_rows\r\n    self._expect_case_error(pure_binding, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 394, in test_case_applicability_rows\r\n    self._expect_case_error(source_native, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.pure_rule')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 416, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.source_property')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 426, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.trusted_native_discovery')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 436, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.adversarial_workload')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 446, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.real_host_property')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 456, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.033s\r\n\r\nFAILED (failures=8)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.024s\r\n\r\nOK\r\n"
  }
}
```

### Q13 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.subject.host_discovery_no_roster`, `CM02.subject.nonhost_discovery_host_subject`, `CM02.subject.host_property_no_roster`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if not isinstance(self.subject, expected_subject):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.018s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.host_discovery_no_roster') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.nonhost_discovery_host_subject') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.host_property_no_roster') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.host_discovery_no_roster')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 461, in test_case_applicability_rows\r\n    self._expect_case_error(host, \"case kind and subject must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.nonhost_discovery_host_subject')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 477, in test_case_applicability_rows\r\n    self._expect_case_error(nonhost, \"case kind and subject must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.subject.host_property_no_roster')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 482, in test_case_applicability_rows\r\n    self._expect_case_error(property_subject, \"case kind and subject must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.022s\r\n\r\nFAILED (failures=3)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.030s\r\n\r\nOK\r\n"
  }
}
```

### Q14 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.platform.native_discovery_generic`, `CM02.platform.host_property_generic`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if self.capability_key.platform is not Platform.WINDOWS:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.018s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.platform.native_discovery_generic') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.platform.host_property_generic') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.platform.native_discovery_generic')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 498, in test_case_applicability_rows\r\n    self._expect_case_error(native_platform, \"native cases require Windows platform\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.platform.host_property_generic')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 503, in test_case_applicability_rows\r\n    self._expect_case_error(host_property_platform, \"native cases require Windows platform\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.021s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.026s\r\n\r\nOK\r\n"
  }
}
```

### Q15 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.host_surface.discovery_mismatch`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if self.subject.roster_key.host_surface is not self.capability_key.host_surface:
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.018s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.host_surface.discovery_mismatch') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.host_surface.discovery_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 508, in test_case_applicability_rows\r\n    self._expect_case_error(host_surface, \"host surface must match capability key\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.020s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.022s\r\n\r\nOK\r\n"
  }
}
```

### Q16 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.host_revision.discovery_mismatch`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if self.subject.roster_key.adapter_revision != self.capability_key.adapter_revision:
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.019s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.host_revision.discovery_mismatch') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.host_revision.discovery_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 512, in test_case_applicability_rows\r\n    self._expect_case_error(host_revision, \"host adapter revision must match capability key\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.020s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.025s\r\n\r\nOK\r\n"
  }
}
```

### Q17 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM02.binding_kind.source_property_native_binding`, `C02.B.source_property`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if pure != (self.binding.kind is BindingKind.PURE_CONTRACT):
+        if pure != (self.binding.kind is BindingKind.PURE_CONTRACT) and self.kind is not CaseKind.SOURCE_PROPERTY:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.019s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding') ... FAIL\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.source_property') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='CM02.binding_kind.source_property_native_binding')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 394, in test_case_applicability_rows\r\n    self._expect_case_error(source_native, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.B.source_property')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 426, in test_case_applicability_rows\r\n    self._expect_case_error(payload, \"case kind and binding kind must agree\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.021s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.018s\r\n\r\nOK\r\n"
  }
}
```

### Q18 — NAMED_LEGAL_DOMAIN_REJECTION

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `C02.K.pure_rule.HN`, `C02.K.source_property.HN`, `C02.K.trusted_native_discovery.HN`, `C02.K.adversarial_workload.HN`, `C02.K.real_host_property.HN`, `C02.K.source_property.HR`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-    def coherent_case(self) -> QualificationCase:
+    def coherent_case(self) -> QualificationCase:
+        if isinstance(self.capability_key, HostCapabilityKey) and self.capability_key.family is not CapabilityFamily.HOST_MEDIATION:
+            raise ValueError("host keys require host mediation")
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.021s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... \r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.pure_rule.HN') ... ERROR\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.source_property.HN') ... ERROR\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.trusted_native_discovery.HN') ... ERROR\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.adversarial_workload.HN') ... ERROR\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.real_host_property.HN') ... ERROR\r\n  test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.source_property.HR') ... ERROR\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.pure_rule.HN')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 201, in test_case_applicability_rows\r\n    row = qualification_case(\"c02-k-pure-hn\", CaseKind.PURE_RULE, host_key)\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 555, in qualification_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-pure-h...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.source_property.HN')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 225, in test_case_applicability_rows\r\n    row = qualification_case(\"c02-k-source-hn\", CaseKind.SOURCE_PROPERTY, host_key)\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 555, in qualification_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-source...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.trusted_native_discovery.HN')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 249, in test_case_applicability_rows\r\n    row = native_case(\"c02-k-native-hn\", CaseKind.TRUSTED_NATIVE_DISCOVERY, host_key, NoRosterSubject())\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 321, in native_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-native...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.adversarial_workload.HN')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 273, in test_case_applicability_rows\r\n    row = native_case(\"c02-k-adversarial-hn\", CaseKind.ADVERSARIAL_WORKLOAD, host_key, NoRosterSubject())\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 321, in native_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-advers...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.real_host_property.HN')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 297, in test_case_applicability_rows\r\n    row = native_case(\"c02-k-property-hn\", CaseKind.REAL_HOST_PROPERTY, host_key, host_property_case().subject)\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 321, in native_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-proper...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) (cell='C02.K.source_property.HR')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 323, in test_case_applicability_rows\r\n    row = qualification_case(\"c02-k-source-hr\", CaseKind.SOURCE_PROPERTY, host_responsibility_key)\r\n          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 555, in qualification_case\r\n    return QualificationCase(\r\n           ^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host keys require host mediation [type=value_error, input_value={'case_id': 'c02-k-source...1, case_output_bytes=1)}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.029s\r\n\r\nFAILED (errors=6)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_case_applicability_rows (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_case_applicability_rows) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.023s\r\n\r\nOK\r\n"
  }
}
```

### Q19 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM03.wa04.source_property_missing`, `CM03.wa04.pure_case_extra`, `CM03.prerequisite.approved_source_replaced`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if (
-            self.kind is CaseKind.SOURCE_PROPERTY
-            and self.capability_key.family is CapabilityFamily.RESPONSIBILITY_ADMISSION
-            and not any(key.kind is PrerequisiteKind.WA04_ADAPTER for key in self.prerequisite_keys)
-        ):
+        if False:
@@
-            if {key.kind for key in self.prerequisite_keys} != set(required_pure_kinds):
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... \r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.source_property_missing') ... FAIL\r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.pure_case_extra') ... FAIL\r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.prerequisite.approved_source_replaced') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.source_property_missing')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 537, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(missing_wa04, \"WA-04 source property requires the WA04 adapter prerequisite\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.pure_case_extra')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 546, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(ordinary, \"pure case prerequisites must use the approved source contract\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.prerequisite.approved_source_replaced')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 552, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(replaced, \"pure case prerequisites must use the approved source contract\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nFAILED (failures=3)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nOK\r\n"
  }
}
```

### Q20 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM03.wa04.pure_case_extra`, `CM03.prerequisite.approved_source_replaced`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if {key.kind for key in self.prerequisite_keys} != set(required_pure_kinds):
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... \r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.pure_case_extra') ... FAIL\r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.prerequisite.approved_source_replaced') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.wa04.pure_case_extra')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 546, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(ordinary, \"pure case prerequisites must use the approved source contract\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.prerequisite.approved_source_replaced')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 552, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(replaced, \"pure case prerequisites must use the approved source contract\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  }
}
```

### Q21 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM03.order.requirements_swapped`, `CM03.order.requirement_key_changed`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if requirement_keys != self.prerequisite_keys:
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... \r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.order.requirements_swapped') ... FAIL\r\n  test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.order.requirement_key_changed') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.order.requirements_swapped')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 557, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(swapped, \"prerequisite requirements must pin the case keys in order\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) (cell='CM03.order.requirement_key_changed')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 562, in test_prerequisite_applicability_and_order\r\n    self._expect_case_error(changed, \"prerequisite requirements must pin the case keys in order\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_prerequisite_applicability_and_order (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_prerequisite_applicability_and_order) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nOK\r\n"
  }
}
```

## Historical reproduction H01–05

Current extracted source is pinned to `ce49f735c6853c236a3504134d4a6959e7ca680f`. Old snapshot is clean detached
`5d7789db6b950d317e7b500b757aa77a54d609ed`. Neither snapshot/ref was mutated.
H01/02/03 retain CM01.native argv/cwd/environment field mutations and literal root/type/error
assertions. H04 retains CM02.valid.pure_host_mediation_no_roster. H05 retains CM06.pure_only.extra_plan;
its setup uses the snapshot's no-argument approved_roster_plan fixture, not a newer incompatible
fixture signature. Bodies are extracted with AST; no persistent test/helper file or bypass.

Exact extraction command (authoring only, exit0):

```powershell
$extractCells = @'
import ast,copy,subprocess
source=subprocess.check_output(["git","show","ce49f735c6853c236a3504134d4a6959e7ca680f:tests/test_verification_qualification_manifests.py"],text=True)
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="QualificationManifestAdmissionTests")
methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {"_payload","_object","_array"}]
class_helpers=[methods[n] for n in ("_assert_root_error","_expect_case_error","_expect_port_error")]
identity=methods["test_case_and_scope_identity_joins"]
native=next(n for n in identity.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=="native")
loop=next(n for n in identity.body if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and [x.id for x in n.target.elts]==["field","diagnostic"])
body=[]
for number,field in enumerate(("argv_digest","cwd_digest","environment_plan_digest"),1):
    selected=copy.deepcopy(loop)
    selected.iter.elts=[n for n in selected.iter.elts if n.elts[0].value==field]
    method=copy.deepcopy(identity)
    method.name="test_H0"+str(number)+"_"+field
    method.body=[copy.deepcopy(native),selected]
    body.append(method)
def cell(method,name):
    return next(n for n in methods[method].body if isinstance(n,ast.With) and any(k.arg=="cell" and isinstance(k.value,ast.Constant) and k.value.value==name for k in n.items[0].context_expr.keywords))
h4=copy.deepcopy(identity)
h4.name="test_H04_pure_host_mediation_no_roster"
h4.body=[copy.deepcopy(cell("test_case_applicability_rows","CM02.valid.pure_host_mediation_no_roster"))]
body.append(h4)
planmethod=methods["test_approved_plan_pin_coverage"]
h5=copy.deepcopy(identity)
h5.name="test_H05_pure_only_extra_plan"
h5.body=[ast.parse("plan = approved_roster_plan()").body[0],copy.deepcopy(next(n for n in planmethod.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=="extra_pure")),copy.deepcopy(cell("test_approved_plan_pin_coverage","CM06.pure_only.extra_plan"))]
body.append(h5)
newcls=copy.deepcopy(cls)
newcls.name="HistoricalCells"
newcls.body=copy.deepcopy(class_helpers)+body
prefix="""from __future__ import annotations
import json,unittest,sys
from pathlib import Path
from pydantic import ValidationError
sys.path.insert(0,str(Path.cwd()/"tests"))
from library.controlled_verification import QualificationCase,ApprovedManifestFound,PlatformCapabilityKey,CapabilityFamily,Platform,CaseKind,NoRosterSubject
from verification_qualification_fixtures import native_case,qualification_case,qualification_manifest,approved_roster_plan,host_capability_key
"""
program=prefix+"\n"+"\n\n".join(ast.unparse(ast.fix_missing_locations(n)) for n in helpers+[newcls])+"\nunittest.main(verbosity=2)\n"
print(program)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $extractCells
exit $LASTEXITCODE
```

Exact in-memory test command, executed once in each worktree below:

```powershell
$historicalCells = @'
from __future__ import annotations
import json,unittest,sys
from pathlib import Path
from pydantic import ValidationError
sys.path.insert(0,str(Path.cwd()/"tests"))
from library.controlled_verification import QualificationCase,ApprovedManifestFound,PlatformCapabilityKey,CapabilityFamily,Platform,CaseKind,NoRosterSubject
from verification_qualification_fixtures import native_case,qualification_case,qualification_manifest,approved_roster_plan,host_capability_key

def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(f'expected object, got {type(value)!r}')
    return value

def _array(value: object) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError(f'expected array, got {type(value)!r}')
    return value

def _payload(model: QualificationModel) -> dict[str, object]:
    value = json.loads(model.model_dump_json())
    return _object(value)

class HistoricalCells(unittest.TestCase):

    def _assert_root_error(self, error: ValidationError, diagnostic: str) -> None:
        details = error.errors()
        self.assertTrue(details)
        self.assertEqual(details[0]['loc'], ())
        self.assertEqual(details[0]['type'], 'value_error')
        self.assertIn(diagnostic, str(details[0]['msg']))

    def _expect_case_error(self, payload: dict[str, object], diagnostic: str) -> None:
        with self.assertRaises(ValidationError) as raised:
            QualificationCase.model_validate_json(json.dumps(payload))
        self._assert_root_error(raised.exception, diagnostic)

    def _expect_port_error(self, payload: dict[str, object], diagnostic: str) -> None:
        with self.assertRaises(ValidationError) as raised:
            ApprovedManifestFound.model_validate_json(json.dumps(payload))
        self._assert_root_error(raised.exception, diagnostic)

    def test_H01_argv_digest(self) -> None:
        native = _payload(native_case('case-native', CaseKind.TRUSTED_NATIVE_DISCOVERY, PlatformCapabilityKey(family=CapabilityFamily.PLAN_BINDING, adapter_revision=1, platform=Platform.WINDOWS), NoRosterSubject()))
        for field, diagnostic in (('argv_digest', 'binding argv must match case argv'),):
            with self.subTest(cell=f'CM01.native.{field}'):
                payload = json.loads(json.dumps(native))
                _object(payload['binding'])[field] = 'f' * 64
                self._expect_case_error(payload, diagnostic)

    def test_H02_cwd_digest(self) -> None:
        native = _payload(native_case('case-native', CaseKind.TRUSTED_NATIVE_DISCOVERY, PlatformCapabilityKey(family=CapabilityFamily.PLAN_BINDING, adapter_revision=1, platform=Platform.WINDOWS), NoRosterSubject()))
        for field, diagnostic in (('cwd_digest', 'binding cwd must match case cwd'),):
            with self.subTest(cell=f'CM01.native.{field}'):
                payload = json.loads(json.dumps(native))
                _object(payload['binding'])[field] = 'f' * 64
                self._expect_case_error(payload, diagnostic)

    def test_H03_environment_plan_digest(self) -> None:
        native = _payload(native_case('case-native', CaseKind.TRUSTED_NATIVE_DISCOVERY, PlatformCapabilityKey(family=CapabilityFamily.PLAN_BINDING, adapter_revision=1, platform=Platform.WINDOWS), NoRosterSubject()))
        for field, diagnostic in (('environment_plan_digest', 'binding environment plan must match case environment plan'),):
            with self.subTest(cell=f'CM01.native.{field}'):
                payload = json.loads(json.dumps(native))
                _object(payload['binding'])[field] = 'f' * 64
                self._expect_case_error(payload, diagnostic)

    def test_H04_pure_host_mediation_no_roster(self) -> None:
        with self.subTest(cell='CM02.valid.pure_host_mediation_no_roster'):
            pure_host = _payload(qualification_case())
            host_key_payload = host_capability_key().model_dump(mode='json')
            pure_host['capability_key'] = host_key_payload
            _object(_array(pure_host['prerequisite_keys'])[0])['capability_key'] = host_key_payload
            _object(_object(_array(pure_host['prerequisite_requirements'])[0])['key'])['capability_key'] = host_key_payload
            self.assertEqual(QualificationCase.model_validate_json(json.dumps(pure_host)).subject, NoRosterSubject())

    def test_H05_pure_only_extra_plan(self) -> None:
        plan = approved_roster_plan()
        extra_pure = _payload(ApprovedManifestFound(manifest=qualification_manifest(), roster_plans=()))
        with self.subTest(cell='CM06.pure_only.extra_plan'):
            extra_pure['roster_plans'] = [plan.model_dump(mode='json')]
            self._expect_port_error(extra_pure, 'approved roster plans must exactly cover host case subjects')
unittest.main(verbosity=2)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $historicalCells
exit $LASTEXITCODE
```

Worktree `C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01-schema-review-closure03-correction`, exit1; unreduced output:

```json
"test_H01_argv_digest (__main__.HistoricalCells.test_H01_argv_digest) ... \r\n  test_H01_argv_digest (__main__.HistoricalCells.test_H01_argv_digest) (cell='CM01.native.argv_digest') ... FAIL\r\ntest_H02_cwd_digest (__main__.HistoricalCells.test_H02_cwd_digest) ... \r\n  test_H02_cwd_digest (__main__.HistoricalCells.test_H02_cwd_digest) (cell='CM01.native.cwd_digest') ... FAIL\r\ntest_H03_environment_plan_digest (__main__.HistoricalCells.test_H03_environment_plan_digest) ... \r\n  test_H03_environment_plan_digest (__main__.HistoricalCells.test_H03_environment_plan_digest) (cell='CM01.native.environment_plan_digest') ... FAIL\r\ntest_H04_pure_host_mediation_no_roster (__main__.HistoricalCells.test_H04_pure_host_mediation_no_roster) ... \r\n  test_H04_pure_host_mediation_no_roster (__main__.HistoricalCells.test_H04_pure_host_mediation_no_roster) (cell='CM02.valid.pure_host_mediation_no_roster') ... ERROR\r\ntest_H05_pure_only_extra_plan (__main__.HistoricalCells.test_H05_pure_only_extra_plan) ... \r\n  test_H05_pure_only_extra_plan (__main__.HistoricalCells.test_H05_pure_only_extra_plan) (cell='CM06.pure_only.extra_plan') ... FAIL\r\n\r\n======================================================================\r\nERROR: test_H04_pure_host_mediation_no_roster (__main__.HistoricalCells.test_H04_pure_host_mediation_no_roster) (cell='CM02.valid.pure_host_mediation_no_roster')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"<string>\", line 73, in test_H04_pure_host_mediation_no_roster\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 782, in model_validate_json\r\n    return cls.__pydantic_validator__.validate_json(\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase\r\n  Value error, host mediation requires a host subject [type=value_error, input_value={'case_id': 'case-pure', ...'case_output_bytes': 1}}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nFAIL: test_H01_argv_digest (__main__.HistoricalCells.test_H01_argv_digest) (cell='CM01.native.argv_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"<string>\", line 48, in test_H01_argv_digest\r\n  File \"<string>\", line 33, in _expect_case_error\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_H02_cwd_digest (__main__.HistoricalCells.test_H02_cwd_digest) (cell='CM01.native.cwd_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"<string>\", line 56, in test_H02_cwd_digest\r\n  File \"<string>\", line 33, in _expect_case_error\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_H03_environment_plan_digest (__main__.HistoricalCells.test_H03_environment_plan_digest) (cell='CM01.native.environment_plan_digest')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"<string>\", line 64, in test_H03_environment_plan_digest\r\n  File \"<string>\", line 33, in _expect_case_error\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_H05_pure_only_extra_plan (__main__.HistoricalCells.test_H05_pure_only_extra_plan) (cell='CM06.pure_only.extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"<string>\", line 80, in test_H05_pure_only_extra_plan\r\n  File \"<string>\", line 38, in _expect_port_error\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 5 tests in 0.010s\r\n\r\nFAILED (failures=4, errors=1)\r\n"
```

Worktree `C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review`, exit0; unreduced output:

```json
"test_H01_argv_digest (__main__.HistoricalCells.test_H01_argv_digest) ... ok\r\ntest_H02_cwd_digest (__main__.HistoricalCells.test_H02_cwd_digest) ... ok\r\ntest_H03_environment_plan_digest (__main__.HistoricalCells.test_H03_environment_plan_digest) ... ok\r\ntest_H04_pure_host_mediation_no_roster (__main__.HistoricalCells.test_H04_pure_host_mediation_no_roster) ... ok\r\ntest_H05_pure_only_extra_plan (__main__.HistoricalCells.test_H05_pure_only_extra_plan) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 5 tests in 0.008s\r\n\r\nOK\r\n"
```

Old H01/02/03/05 are named AssertionError (missing rejection); H04 is the intended named
ValidationError rejecting a legal host key, not collection failure. Current five all pass.
This is reproducible historical evidence, not a fabricated claim of original TDD chronology.
