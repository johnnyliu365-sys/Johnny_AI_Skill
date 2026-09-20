# CVQ-01A3 | Correction review execution evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A3-CORRECTION` / `REVIEW_EVIDENCE` / `01` |
| Candidate | `af7fc42837c6bd068b3babdc4227ce46c4335ff3`, parent `ce2d750af68642f1f2bd014f38e535df564c4f88` |
| Authority | A3 document04 / closure01 at `da5d7ffba902ace013eb16a125194975996b6aae`, LF `b24a734a4565dd84a17292e5883538f82c98a856ea7acc5252d4dc483b5a95cd` |
| Executor / result | root, detached review snapshot; strict17 / focused38 green; R01/R02/R03/R05 named red/restored green, R04 outer-constructor error, R09 ZERO_RED |
| Limits | Existing one foreground process / 60s per command / 1200s pass, no load/retry/background/new launcher; source bytes restored after each patch |

This leaf records actual complete command outputs, not a full predicate-coverage claim.
Mutant stdout is losslessly JSON-encoded to retain terminal trailing spaces and CRLF without
introducing Markdown trailing-whitespace defects; decode the output string for exact stdout.
R04 is a behavioral outer construction error, NOT the per-alternative subTest claimed in the
owner's original return. R09 removes the measured-proof PURE_RULE scope guard while retaining
the terminal-result guard; its named ER02 method remains green. No full-suite mutant run is
claimed. The 38-test success below is the clean unmutated candidate.

## Final-command independent replay

```powershell
$ErrorActionPreference='Stop'
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_evidence.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
if($LASTEXITCODE -ne 0){throw 'Strict failed'}
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
if($LASTEXITCODE -ne 0){throw 'Tests failed'}
git diff --check
```

Exit 0; unreduced output:

```text
Success: no issues found in 17 source files
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
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok
test_authenticated_capability_identity_joins (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok
test_authenticated_discovered_identity_joins (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok
test_authenticated_discovery_identity_joins (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok
test_authenticated_enforcement_identity_joins (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ... ok
test_every_refusal_reason_result_pair (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_every_refusal_reason_result_pair) ... ok
test_local_report_duplicates (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_local_report_duplicates) ... ok
test_negative_and_zero_roster_shapes_remain_representable (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok
test_observed_entry_and_category_rules (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok
test_observed_global_coverage_and_uniqueness (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok
test_other_proof_scope_result_pairs (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok
test_plan_global_coverage_and_uniqueness (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok
test_planned_entry_and_category_rules (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok
test_required_proof_references (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_required_proof_references) ... ok
test_result_shape_boundaries (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_result_shape_boundaries) ... ok
test_roster_link_scope_and_result (test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok
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
Ran 38 tests in 0.755s

OK
```

## A3-R01 / ER15

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/qualification_ports.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.case_ids != self.subject.case_ids
+            or set(self.payload.case_ids) != set(self.subject.case_ids)
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.022s

OK
```

Mutant exit 1; classification:
NAMED_RED / COUNTEREXAMPLE_DETECTED.

```json
{
  "output": "test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... \r\n  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 873, in test_authenticated_capability_identity_joins\r\n    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), \"capability payload must match subject\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 92, in _assert_value_error\r\n    with self.assertRaises(ValidationError) as captured:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nFAILED (failures=1)\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored replay exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.021s

OK
```

## A3-R02 / ER15

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/qualification_ports.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.capability_key != self.subject.capability_key
+            or self.payload.capability_key.model_dump(exclude={"host_surface"}) != self.subject.capability_key.model_dump(exclude={"host_surface"})
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

Mutant exit 1; classification:
NAMED_RED / COUNTEREXAMPLE_DETECTED.

```json
{
  "output": "test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... \r\n  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 909, in test_authenticated_capability_identity_joins\r\n    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), \"capability payload must match subject\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 92, in _assert_value_error\r\n    with self.assertRaises(ValidationError) as captured:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.015s\r\n\r\nFAILED (failures=1)\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored replay exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.014s

OK
```

## A3-R03 / ER09

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/roster_contracts.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-    Union[PresentHostEnforcementCoverage, ZeroPresentHostEnforcementCoverage],
+    PresentHostEnforcementCoverage,
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable
exit $LASTEXITCODE
```

Control exit 0:

```text
test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

Mutant exit 1; classification:
NAMED_RED / COUNTEREXAMPLE_DETECTED.

```json
{
  "output": "test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... \r\n  test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) (cell='ER09', shape='ZERO_PRESENT_ENTRIES') ... ERROR\r\n\r\n======================================================================\r\nERROR: test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) (cell='ER09', shape='ZERO_PRESENT_ENTRIES')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 632, in test_negative_and_zero_roster_shapes_remain_representable\r\n    self.assertEqual(enforcement_adapter.validate_json(enforcement_adapter.dump_json(zero_present)), zero_present)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\type_adapter.py\", line 492, in validate_json\r\n    return self.validator.validate_json(\r\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for tagged-union[function-after[unique_observations(), PresentHostEnforcementCoverage]]\r\n  Input tag 'ZERO_PRESENT_ENTRIES' found using 'tag' does not match any of the expected tags: 'PRESENT_ENTRIES' [type=union_tag_invalid, input_value={'tag': 'ZERO_PRESENT_ENT...eeeeeeeeeeeeeeeeeeeeee'}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/union_tag_invalid\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.016s\r\n\r\nFAILED (errors=1)\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored replay exit 0:

```text
test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

## A3-R04 / ER02

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/report_contracts.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/report_contracts.py
@@
-            if self.claim_scope is not ClaimScope.PURE_RULE or not terminal_result:
+            if self.claim_scope is not ClaimScope.PURE_RULE or self.result is not Observation.PROVEN:
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs
exit $LASTEXITCODE
```

Control exit 0:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant exit 1; classification:
OUTER_CONSTRUCTOR_ERROR / NAMED_CELL_ATTRIBUTION_MISSING.

```json
{
  "output": "test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ERROR\r\n\r\n======================================================================\r\nERROR: test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 146, in test_other_proof_scope_result_pairs\r\n    pure_failed = capability_observation(PureRuleProof(), result=Observation.FAILED)\r\n                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 285, in capability_observation\r\n    return CapabilityObservation(\r\n           ^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation\r\n  Value error, pure proof requires a pure terminal claim [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nFAILED (errors=1)\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
```

Restored replay exit 0:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## A3-R05 / ER04

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/report_contracts.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/report_contracts.py
@@
-        elif self.result is Observation.PROVEN and not isinstance(self.roster_evidence, EnforcementEvidenceLink):
+        elif not isinstance(self.roster_evidence, EnforcementEvidenceLink):
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result
exit $LASTEXITCODE
```

Control exit 0:

```text
test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant exit 1; classification:
NAMED_RED / COUNTEREXAMPLE_DETECTED.

```json
{
  "output": "test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... \r\n  test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='FAILED', link='NONE') ... ERROR\r\n  test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='UNAVAILABLE', link='NONE') ... ERROR\r\n  test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='NOT_RUN', link='NONE') ... ERROR\r\n\r\n======================================================================\r\nERROR: test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='FAILED', link='NONE')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 396, in test_roster_link_scope_and_result\r\n    valid = capability_observation(proof, scope=host_scope, result=result, roster_evidence=NoObservedRoster())\r\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 285, in capability_observation\r\n    return CapabilityObservation(\r\n           ^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation\r\n  Value error, proven host property requires enforcement evidence [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='UNAVAILABLE', link='NONE')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 396, in test_roster_link_scope_and_result\r\n    valid = capability_observation(proof, scope=host_scope, result=result, roster_evidence=NoObservedRoster())\r\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 285, in capability_observation\r\n    return CapabilityObservation(\r\n           ^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation\r\n  Value error, proven host property requires enforcement evidence [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n======================================================================\r\nERROR: test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) (cell='ER04', scope='HOST_PROPERTY', result='NOT_RUN', link='NONE')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_evidence.py\", line 396, in test_roster_link_scope_and_result\r\n    valid = capability_observation(proof, scope=host_scope, result=result, roster_evidence=NoObservedRoster())\r\n            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\verification_qualification_fixtures.py\", line 285, in capability_observation\r\n    return CapabilityObservation(\r\n           ^^^^^^^^^^^^^^^^^^^^^^\r\n  File \"C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\pydantic\\main.py\", line 263, in __init__\r\n    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)\r\n                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\r\npydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation\r\n  Value error, proven host property requires enforcement evidence [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]\r\n    For further information visit https://errors.pydantic.dev/2.13/v/value_error\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nFAILED (errors=3)\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
```

Restored replay exit 0:

```text
test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## A3-R09 / ER02

Candidate `af7fc42837c6bd068b3babdc4227ce46c4335ff3`; target `library/controlled_verification/report_contracts.py`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/report_contracts.py
@@
-            if self.claim_scope is ClaimScope.PURE_RULE or not terminal_result:
+            if not terminal_result:
*** End Patch
```

Command, identical for control, mutant and restored replay:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs
exit $LASTEXITCODE
```

Control exit 0:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant exit 0; classification:
ZERO_RED / REGRESSION_FINDING.

```json
{
  "output": "test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.004s\r\n\r\nOK\r\n"
}
```

Exact-byte restoration exit 0, SHA-256 readback:

```text
93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
```

Restored replay exit 0:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```
