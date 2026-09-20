# CVQ-01A3 | Evidence admission review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A3` / `CODE_REVIEW` / `03` |
| Conclusion / round | `CHANGES_REQUESTED / CLOSURE02_INITIAL_REVIEW / NOT_INTEGRATED`; section6 is current; sections1–5 preserve closure01 history |
| Authority | [A3](../../../modules/tickets/controlled-verification/cvq-01a3-evidence-admission.md) document04 / closure01 at `da5d7ffba902ace013eb16a125194975996b6aae`, LF `b24a734a4565dd84a17292e5883538f82c98a856ea7acc5252d4dc483b5a95cd`; approved ER01–16 unchanged |
| Baseline / candidate | `ce2d750af68642f1f2bd014f38e535df564c4f88` -> `af7fc42837c6bd068b3babdc4227ce46c4335ff3` |
| Roles | Retained Luna/xhigh implementation owner; root sole ticket-review verdict; retained Terra/xhigh evidence-only helper |
| Isolation | Clean exact candidate, two admitted test paths only; root detached review snapshot, no provider/native/target/integration/push/release effect |

## 1. Observed return and independent checks

Owner changed only tests/test_verification_qualification_domains.py and the new
tests/test_verification_qualification_evidence.py. No production library changes.
Root verified the exact parent, paths, clean owner worktree, diff whitespace and independently
ran the declared strict command (17 source files) and focused suite (38 tests). These establish
a green starting seam and collection, not completion of each frozen predicate.

The owner explicitly returned `mutation_evidence=NOT_RUN_BY_OWNER`, claiming the ticket
assigned the full campaign to root. That claim contradicts this A3 ticket's Evidence and bounded
execution / return clauses: owner per-predicate evidence and parent's independent evidence are
both required. A2's separately approved root-owned campaign cannot silently transfer to A3.
Existing genuine historical evidence remains valid; this return did not supply the required
row-specific collectable historical replay/reference mapping. No missing-module error counts.

## 2. Batched findings

All lines below refer to ce2d750's new evidence test unless otherwise stated. This batch repairs
already-approved obligations, not new product behavior, extra test profiles or broader scope.

| Finding | Frozen requirement and concrete evidence | Required additive correction |
| --- | --- | --- |
| A3-F01 IMPLEMENTATION_DEFECT / RESPONSIBILITY_BOUNDARY | CA10 assigns compatible scenario composition solely to verification_qualification_fixtures.py. Lines109–168 add independent _capability, _planned and _observed builders in the assertion TestCase; _planned/_observed repeat the existing planned_host_entry/host_entry owners. | Reuse or compatibly extend the admitted fixture owner and remove duplicate scenario builders from the assertion owner. Keep test-specific negative edits and assertions in evidence tests. Preserve A1/A2 methods and fixture defaults. Technical docstrings should describe behavior, not A3 work-order ownership. No arbitrary line-count split or new helper file. |
| A3-F02 EVIDENCE_DEFECT / POSITIVE_CONTROL_GAP | ER02 lines201–270 never positively exercises PURE_RULE/FAILED and does not pair every nonpure measured scope with both PROVEN/FAILED. R04 rejects valid PURE_RULE/FAILED yet this method stays green. ER04 lines434–441 preserves nonproven+NONE only for HOST_DISCOVERY, omitting HOST_PROPERTY, including an old accepted negative-host observation; R05 wrongly requires enforcement evidence for every HOST_PROPERTY result yet ER04 stays green. ER05/07 entry negatives have no separately observed sorted-distinct multi-alias/case-ref control and category negatives no valid distinct-entry category control. | Supply the frozen positive alternatives and pair each relevant negative with an observed valid ordinary control. Nonpure proven host controls carry the already-required compatible link. Preserve both host scopes' FAILED/UNAVAILABLE/NOT_RUN+NONE alternatives. Name each positive/negative subcase; don't create eager validated scenario rows outside their subcase. Complete existing ER06/08 cross-category controls without adding new invariants. |
| A3-F03 EVIDENCE_DEFECT / ALIAS_POSITIVE_MISSING | ER09 lines596–638 checks ZERO_PRESENT_ENTRIES only by reading an ordinary object's tag (line629), not through HostRosterEnforcementCoverage. The explicitly approved union-branch-removal R03 stays green. Other declared allowed shapes need the specified ordinary and applicable alias round trips, not just fixture existence. | Exercise ZERO_PRESENT_ENTRIES through the actual declared alias and preserve each frozen allowed shape with its applicable round trip. Run the six already-enumerated temporary counterfactuals with named failures and exact restoration; do not commit schema restrictions. |
| A3-F04 EVIDENCE_DEFECT / RESULT_MATRIX_INCOMPLETE | ER11 lines689–693 checks cleanup=CLEANUP_CONFIRMED rejection only for ExecutedNativeRecoveryCaseResult, not the explicitly listed RefusedRecoveryCaseResult. Its unknown/null selector alternatives also reuse an identical subTest ID. | Complete the explicitly named RefusedRecoveryCaseResult cleanup cell and independently identify selector alternatives. Keep ordinary branch positives. Retain the A1 exact closed error algebra and link shared omission/null/unknown wire evidence and regression; do not invent broader errors, duplicate the entire A1 matrix unnecessarily, modify frozen fields/defaults/tags or claim another semantic guard. |
| A3-F05 EVIDENCE_DEFECT / MASKED_IDENTITY_NEGATIVE | ER15's 'order' input is two IDs against a one-ID payload, not a permutation (line840); R01 replaces ordered equality with set equality yet the entire named method stays green. Lines829–833 change subject PLATFORM->HOST and host_surface together against a PLATFORM payload; R02 ignores host_surface and still stays green. HOST key alternatives/components are not independently matched controls. | Begin with valid equal two-ID subject/payload, then permute exactly those IDs in subject only; keep content mismatch separate. Build an ordinary matched HOST/HOST control before changing each legal HOST component only, retain PLATFORM controls and whole-variant mismatch. Use only legal values under the frozen key schema; no unrelated nested rejection or imaginary field. |
| A3-F06 EVIDENCE_DEFECT / EVIDENCE_RETURN_INCOMPLETE | Owner's NOT_RUN campaign, no complete predicate-to-patch/raw-output/restore ledger, historical replay omitted, and broad old-method-to-row map do not satisfy the existing evidence/return contract. Root R01–05 are zero-red findings, not passes; only R06–08 prove ER16. | Return the already-required complete mapped evidence with candidate SHA, exact expression/patch, command, unreduced output, row ID and exact restoration. Preserve authentic prior observations; do not invent chronology or substitute collection errors. Include per-observation old assertion relocation, honest starting behavior and named historical evidence. Do not borrow A2's root-only allocation, add a runner, background work, load or retries. |

Root's remainder is NOT_VERIFIED at this failing initial review. Eight bounded probes below
are not presented as a completed all-predicate campaign. ER16 itself is verified: each of its
three class-import deletions leaves the local witness collected and red, then returns green.
Unittest's own assertion-diff abbreviation is retained verbatim; no tool stream was filtered.

## 3. Root execution evidence

Every Python command used the existing subprocess timeout60 wrapper, one foreground process,
within the existing pass budget; no retry, load or new launcher. Temporary edits touched only
root's clean detached review snapshot and were restored to exact candidate bytes after each.

### Declared final commands

```powershell
$ErrorActionPreference='Stop'
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_evidence.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
if($LASTEXITCODE -ne 0){throw 'Strict failed'}
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
if($LASTEXITCODE -ne 0){throw 'Tests failed'}
git diff --check
```

Exit 0; complete output:

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
Ran 38 tests in 0.452s

OK
```

### A3-R01 / ER15

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `library/controlled_verification/qualification_ports.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.case_ids != self.subject.case_ids
+            or set(self.payload.case_ids) != set(self.subject.case_ids)
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

Mutant exit 0; ZERO_RED / FINDING:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.017s

OK
```

Exact-byte restore exit 0; SHA-256 readback:

```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Same named command after restore, exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.016s

OK
```

### A3-R02 / ER15

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `library/controlled_verification/qualification_ports.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.capability_key != self.subject.capability_key
+            or self.payload.capability_key.model_dump(exclude={"host_surface"}) != self.subject.capability_key.model_dump(exclude={"host_surface"})
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

Mutant exit 0; ZERO_RED / FINDING:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Exact-byte restore exit 0; SHA-256 readback:

```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Same named command after restore, exit 0:

```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

### A3-R03 / ER09

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `library/controlled_verification/roster_contracts.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-    Union[PresentHostEnforcementCoverage, ZeroPresentHostEnforcementCoverage],
+    PresentHostEnforcementCoverage,
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable
exit $LASTEXITCODE
```

Control exit 0:

```text
test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

Mutant exit 0; ZERO_RED / FINDING:

```text
test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

Exact-byte restore exit 0; SHA-256 readback:

```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Same named command after restore, exit 0:

```text
test_negative_and_zero_roster_shapes_remain_representable (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_negative_and_zero_roster_shapes_remain_representable) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.020s

OK
```

### A3-R04 / ER02

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `library/controlled_verification/report_contracts.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/report_contracts.py
@@
-            if self.claim_scope is not ClaimScope.PURE_RULE or not terminal_result:
+            if self.claim_scope is not ClaimScope.PURE_RULE or self.result is not Observation.PROVEN:
*** End Patch
```

Named command:

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

Mutant exit 0; ZERO_RED / FINDING:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Exact-byte restore exit 0; SHA-256 readback:

```text
93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
```

Same named command after restore, exit 0:

```text
test_other_proof_scope_result_pairs (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_other_proof_scope_result_pairs) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

### A3-R05 / ER04

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `library/controlled_verification/report_contracts.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/report_contracts.py
@@
-        elif self.result is Observation.PROVEN and not isinstance(self.roster_evidence, EnforcementEvidenceLink):
+        elif not isinstance(self.roster_evidence, EnforcementEvidenceLink):
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result
exit $LASTEXITCODE
```

Control exit 0:

```text
test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant exit 0; ZERO_RED / FINDING:

```text
test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Exact-byte restore exit 0; SHA-256 readback:

```text
93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
```

Same named command after restore, exit 0:

```text
test_roster_link_scope_and_result (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_roster_link_scope_and_result) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

### A3-R06 / ER16

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `tests/test_verification_qualification_domains.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_evidence import QualificationEvidenceAdmissionTests
+
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant exit 1; NAMED_COLLECTION_WITNESS_RED:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... FAIL

======================================================================
FAIL: test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_domains.py", line 57, in test_collection_retains_split_cases
    self.assertEqual(sorted(actual), sorted(expected))
AssertionError: Lists differ: ['tes[24 chars]tion_manifests.QualificationManifestAdmissionT[1259 chars]ses'] != ['tes[24 chars]tion_evidence.QualificationEvidenceAdmissionTe[3057 chars]ses']

First differing element 0:
'test[23 chars]tion_manifests.QualificationManifestAdmissionT[32 chars]rage'
'test[23 chars]tion_evidence.QualificationEvidenceAdmissionTe[44 chars]oins'

Second list contains 15 additional elements.
First extra element 12:
'test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_required_proof_references'

Diff is 3344 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 1 test in 0.011s

FAILED (failures=1)
```

Exact-byte restore exit 0; SHA-256 readback:

```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Same named command after restore, exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

### A3-R07 / ER16

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `tests/test_verification_qualification_domains.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_manifests import QualificationManifestAdmissionTests
+
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant exit 1; NAMED_COLLECTION_WITNESS_RED:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... FAIL

======================================================================
FAIL: test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_domains.py", line 57, in test_collection_retains_split_cases
    self.assertEqual(sorted(actual), sorted(expected))
AssertionError: Lists differ: ['tes[1822 chars]tion_scalars.QualificationScalarTests.test_eve[432 chars]ses'] != ['tes[1822 chars]tion_manifests.QualificationManifestAdmissionT[1259 chars]ses']

First differing element 15:
'test[23 chars]tion_scalars.QualificationScalarTests.test_eve[13 chars]ound'
'test[23 chars]tion_manifests.QualificationManifestAdmissionT[32 chars]rage'

Second list contains 7 additional elements.
First extra element 20:
'test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates'

Diff is 3218 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Exact-byte restore exit 0; SHA-256 readback:

```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Same named command after restore, exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

### A3-R08 / ER16

Exact candidate: `ce2d750af68642f1f2bd014f38e535df564c4f88`. Target `tests/test_verification_qualification_domains.py`.
Temporary patch (snapshot path in patch identifies root's review tree, not owner source):

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_scalars import QualificationScalarTests
+
*** End Patch
```

Named command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant exit 1; NAMED_COLLECTION_WITNESS_RED:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... FAIL

======================================================================
FAIL: test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_domains.py", line 57, in test_collection_retains_split_cases
    self.assertEqual(sorted(actual), sorted(expected))
AssertionError: Lists differ: ['tes[2621 chars]'tests.test_verification_qualification_domains[68 chars]ses'] != ['tes[2621 chars]'test_verification_qualification_scalars.Quali[460 chars]ses']

First differing element 22:
'tests.test_verification_qualification_domains[67 chars]ases'
'test_verification_qualification_scalars.Quali[41 chars]ound'

Second list contains 4 additional elements.
First extra element 23:
'test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains'

Diff is 3218 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Exact-byte restore exit 0; SHA-256 readback:

```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Same named command after restore, exit 0:

```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## 4. Independent helper disposition and bounded continuation

Retained Terra/xhigh returned one READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT findings packet
for this exact candidate. Its ER02 positive, ER09 alias, ER11 recovery and fixture-ownership
observations confirm F02/F03/F04/F01. It ran no tests or mutations. Root independently verified
those source locations and owns the conclusion; helper is not another reviewer.

The helper additionally flagged the removed old Unavailable CaseResult adapter positive and
uncovered two executed branches in ER11's local filter. Root checked the unchanged
QualificationContractTests.test_alias_branch_counts_and_selector_negatives, lines517–563:
its literal ALIASES catalog round-trips all eight CaseResult branches, including the exact
all_direct_rows Unavailable fixture. test_all_result_proof_and_evidence_branches_roundtrip
lines948–967 also retains the valid Unavailable alias assertion. Both independently ran green
above. Therefore no redundant all-eight matrix is demanded as a new blocker; F06 requires
the explicit preserved-observation mapping to those existing witnesses. This does not waive
the separately enumerated RefusedRecovery cleanup cell in F04.

Disposition: CHANGES_REQUESTED / EVIDENCE_AND_RESPONSIBILITY_CORRECTION_REQUIRED.
The same Luna/xhigh owner receives ONE additive correction against ce2d750, same closure01,
same worktree/branch/profile and bounded commands. No reset/amend/force, production behavior
change merely to suit tests, new file/helper framework, model elevation or parallel owner.
All F01–F06 and the already-approved finite closure/evidence duties form the one batch.
Root will review the return with the retained evidence-only helper. A second unresolved
implementation/evidence defect goes to CONVERGENCE_REVIEW_REQUIRED, not a third correction.
No A3/B admission, combined A approval, integration, push or publication has occurred.
ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_CORRECTION.

## 5. Correction review — convergence required, 2026-09-20

The retained owner returned af7fc428, changing only the evidence assertion module and admitted
fixture owner. Root verified its exact parent, clean owner tree, declared path delta and diff
whitespace. Production is unchanged. Independent strict17 and focused38 both pass. Actual
commands, six temporary patches, unreduced outputs and exact byte restoration are retained in
[correction evidence01](cvq-01a3-correction-evidence.md), not inferred from the owner's return.

### Closed findings and preserved progress

- F01: duplicated _capability/_planned/_observed functions are removed; compatible reusable
  scenario builders now live in the existing fixture owner. Prior builder defaults and A1/A2
  regressions remain green. No new production/helper file, dependency or API.
- F03: the ZERO_PRESENT_ENTRIES alias path is actually exercised. Root R03 now produces the
  intended named ER09 union-tag error and returns green after exact restoration.
- F04: RefusedRecovery cleanup negative and separate unknown/null subTest identities are
  present. Shared A1 wire evidence remains the declared regression basis; no duplicate full
  all-eight matrix was required.
- F05: valid two-ID content/order and matched HOST/HOST controls now isolate their predicates.
  Root R01 and R02 produce the exact order and host_surface assertion failures, restored green.
- ER04's missing HOST_PROPERTY nonproven positives are present; R05 produces three named
  ER04/FAILED, UNAVAILABLE and NOT_RUN errors, then restored green.

### Remaining blocking findings, same frozen closure

| Existing item / classification | Correction evidence and disposition |
| --- | --- |
| F02 / ER02 / EVIDENCE_DEFECT | While adding measured nonpure PROVEN/FAILED controls, the correction removed the initial candidate's MEASURED_NATIVE + PURE_RULE negative. At lines161–198 the eight positive pairs and terminal negatives remain, but no measured scope rejection. Root R09 deletes only `self.claim_scope is ClaimScope.PURE_RULE or` from its guard; named ER02 stays green (exit0), as does its clean control/restoration. This is an actual regression against the existing scope clause, not a new requirement. |
| F02 / attribution / EVIDENCE_DEFECT | PURE_RULE controls144–147, host positive observations338–376, and planned/observed positive constructors400–409/472–481 still execute before their subTest. Root R04 raises at `pure_failed = capability_observation(...)` outside a subTest and aborts the method. It proves an outer behavioral red, not the claimed ER02/FAILED named cell. This is the same explicit F02 attribution duty, not a new formatting preference. |
| F06 / EVIDENCE_DEFECT | Owner clarification explicitly confirms no captured/retrievable complete ledger for ER01; ER02 beyond R04; ER04 beyond R05; ER05–08; ER10; ER12–14; ER15 beyond R01/R02. ER16 is root-only prior evidence, not owner execution. Historical observations are linked but no owner replay/raw output retained. Relocation remains broad method-family mapping. Original COMPLETED and summaries cannot replace these frozen obligations. Root's limited correction probes do not claim the unrun remainder. |

The owner was asked only to identify already-captured evidence, with an explicit prohibition
on edits, reruns, refs or a third correction. Its read-only clarification performed no extra
work and corrected the R04 attribution. Root's independent trace confirms that correction.
Its production identity strings are Git object IDs, not SHA-256 byte hashes; actual restored
byte hashes are in the evidence leaf. No hash algorithm equivalence is inferred.

Retained Terra/xhigh returned one read-only correction packet confirming measured-scope loss,
eager constructor attribution and incomplete evidence, and static closure of F01/F03/F04/F05.
It performed no execution and did not own the verdict. Root alone concludes CHANGES_REQUESTED.
The whole focused suite was run; a complete remaining mutation campaign is NOT_VERIFIED and is
not wastefully repeated as if it could fix the missing source row or substitute new authority.

Closure01's initial + sole correction is exhausted. Preserve af7fc428 and prior refs; close
both implementation views. No third implementation dispatch, automatic model elevation,
implicit evidence transfer, combined A admission or B dispatch. Proposed control-plane
disposition is in [convergence section28](cvq-01-convergence-proposal.md#28-a3-correction-exhausted--owner-decision-pending-2026-09-20).
ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> WAIT_FOR_HUMAN / CONVERGENCE_REVIEW_REQUIRED.

## 6. Closure02 initial source review and sole correction — 2026-09-20

Current authority is A3 document06 / closure02 at
dddd59df94804f45ad74cc2892e1fcdca70e8341, LF
97b140dc424ef1efc7f3075eca62e17b405db8700a57295f5a261cf34a08df22.
The owner-approved split replaces the prior allocation of evidence duties. Root owns the
complete evidence campaign; its absence from Luna's return is not a finding in this closure.
Source candidate 844d1866c7eb665df0937ded4baa57fb30e39fc3 descends directly from af7fc428,
changes only the admitted evidence test file, and is clean. Root independently obtained
strict17/focused38 green, then named R04/ER02 PURE_RULE FAILED and R09/ER02 measured PURE_RULE
reds with exact restoration and green reruns. These are bounded probes, not complete closure.

Retained evidence-only helper found, and root read back, one remaining F02 attribution defect:
ER05 lines444–446 and ER07 lines521–523 construct first/second_same_id/second_same_alias before
the named category and duplicate cells. Constructor failure there aborts the method without
the intended cell identity. Document06's finite delta explicitly forbids prerequisite validated
scenario objects outside the cell. Positive controls and ER02/ER04 fixes are otherwise retained.

CHANGES_REQUESTED: use closure02's one additive correction, same owner/worktree/branch/profile.
Only test_planned_entry_and_category_rules and test_observed_entry_and_category_rules need
correction: build each negative category/duplicate cell's prerequisites inside that cell, using
existing fixture functions. Loop metadata outside cells may be literal IDs/messages, not
constructed validated scenario rows. Preserve all positives, diagnostics and negative cases;
no new helper, product or fixture changes. Run the already frozen focused/type commands and
return one additive commit with complete outputs. Do not repeat root's mutation campaign.

This review commit is the correction handoff; no new requirement or repeat owner approval.
Source return is not approval. Root reviews the corrected immutable candidate and completes
its evidence allocation. Another unresolved defect follows the declared convergence route.
ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_CORRECTION.
