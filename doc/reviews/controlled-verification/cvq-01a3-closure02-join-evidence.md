# CVQ-01A3 closure02 | Joins, history and preservation evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A3-C02-JOIN` / `REVIEW_EVIDENCE` / `01` |
| Authority | A3 document06 / closure02 at dddd59df94804f45ad74cc2892e1fcdca70e8341; source correction review59f5962 |
| Candidate | `485d882f578f84dac1c975b32ced2a4ae6e7d43a` |
| Recorder | root / ticket-review; retained helper is evidence-only |
| Scope | 17 candidate-bound temporary mutation records; no committed product change, host qualification or integration |
| Result | Each recorded control/restoration exit0 and mutant exit1; interpreted below, not merely counted |

Commands ran one foreground bounded child, timeout60 seconds, no load or automatic retries.
Existing tool orchestration held this finite ledger; no repository runner/framework was added.
Unreduced command output follows. Only CRLF and trailing whitespace are normalized for Markdown;
no diagnostic or traceback line is omitted. Unittest's own abbreviated assertion diffs remain.
Every mutation restores the exact candidate bytes, checks the recorded SHA-256 and reruns green.
These are reverse-mutation experiments after implementation, not fabricated initial TDD reds.

## Observation relocation, not deletion

All five QualificationDomainTests methods from accepted A2 ce49f735 were loaded verbatim from
Git into an in-memory namespace and run against this candidate. All five pass. This is an
independent preservation replay, not five additional committed tests or a new test framework.
A2 production and manifest assertions are Git-byte-identical; A1 wire owners are unchanged.

| Old method / individual observation at ce49f735 | Current owner / exact cell family |
| --- | --- |
| refusal_proof_result_matrix: three FAILED reason controls and UNAVAILABLE rejection each | ER01 reason/result/wrong_result |
| same: three UNAVAILABLE reason controls and FAILED rejection each | ER01 reason/result/wrong_result |
| same: PURE positive and native-scope rejection | ER02 PURE_RULE positive/scope |
| same: MEASURED native FAILED and PURE rejection | ER02 MEASURED_NATIVE result/scope |
| same: UNAVAILABLE_PROBE control and PROVEN rejection | ER02 UNAVAILABLE_PROBE result |
| same: NOT_COMPLETED control and FAILED rejection | ER02 NOT_COMPLETED result |
| roster_local_invariants: seven categories and all-ABSENT acceptance | ER06 coverage; ER09 all_absent_plan; independent category positive explicitly asserts seven |
| same: ZERO_PRESENT_ENTRIES and MISMATCH positives | ER09 named shape cells |
| same: unsorted planned aliases | ER05 planned aliases must be sorted |
| same: wrong observed category | ER07 category |
| same: cross-category duplicate planned entry/alias | ER06 global_entry_id/global_alias_id, now isolated separately |
| same: cross-category planned case refs | ER06 global_case_ref |
| same: observed entry/alias duplicates | ER08 global_entry_id/global_alias_id |
| same: observed case-ref duplicates | ER08 global_case_ref |
| same: observed alias sorting | ER07 effect aliases must be sorted |
| local_result_and_evidence_consistency: discovered roster host_version | ER12 roster_key/host_version |
| same: discovery approved_roster_ref | ER13 approved_roster_ref |
| same: enforcement discovery_coverage_ref | ER14 both payload variants/reference |
| same: capability observation_id | ER15 observation_id |
| same: capability outer observer_ref | ER15 observer_ref |
| same: discovered outer evidence_ref | ER12 evidence_ref |
| same: discovery subject approved_roster_digest | ER13 approved_roster_digest |
| same: enforcement subject discovery_coverage_digest | ER14 both payload variants/digest |
| same: report result case IDs and claim observation IDs | ER10 separate report cells |
| same: execution check IDs | ER10 CompleteExecutionObservation/check_id |
| same: CapabilityRequirement case-ID duplicate | Unchanged A2 test_manifest_and_prerequisite_duplicates / CM05.capability_requirement.case_ids_duplicate |
| same: pure result extra launch observation | ER11 ExecutedPureCaseResult/launch_observation/extra |
| same: native recovery cleanup literal | ER11 ExecutedNativeRecoveryCaseResult/cleanup/literal |
| same: proven host property cannot omit roster | ER04 HOST_PROPERTY/PROVEN/NoObservedRoster |
| same: failed host property may have NONE | ER04 HOST_PROPERTY/FAILED/NONE |
| strict_boundary_rejection: boolean/float/string manifest_revision | Unchanged A1 test_integer_domains_are_strict / QualificationScope manifest_revision |
| same: six invalid project IDs | Unchanged A1 test_identifier_digest_text_domains / project_id |
| union_and_constructor_boundaries: PURE binding with ADVERSARIAL_WORKLOAD kind | Unchanged A2 test_case_applicability_rows; full old method replay |
| same: duplicated manifest case | Unchanged A2 CM05.manifest.case_ids_duplicate |
| same: Unavailable CaseResult alias round trip | Unchanged A1 all-eight alias/roundtrip tests plus current ER11 Unavailable positive |

ER12 J01–03 and ER13 K01–03 map every roster-key component and outer/reference comparison.
ER14 E01/E02 each expose both PRESENT_ENTRIES and ZERO_PRESENT_ENTRIES.
ER15 C01–07 expose each subject/outer comparison, key components/variants and case-ID content/
order; R01 and R02 are independent order-only and HOST host_surface-only doors.
Historical BR03/BR04 below reproduce old behavioral failures, not collection/import failures.

## Mutation index

| Operator | Cell | Method | Control / mutant / restored |
| --- | --- | --- | --- |
| J01 | ER12 | test_authenticated_discovered_identity_joins | 0 / 1 / 0 |
| J02 | ER12 | test_authenticated_discovered_identity_joins | 0 / 1 / 0 |
| J03 | ER12 | test_authenticated_discovered_identity_joins | 0 / 1 / 0 |
| K01 | ER13 | test_authenticated_discovery_identity_joins | 0 / 1 / 0 |
| K02 | ER13 | test_authenticated_discovery_identity_joins | 0 / 1 / 0 |
| K03 | ER13 | test_authenticated_discovery_identity_joins | 0 / 1 / 0 |
| E01 | ER14 | test_authenticated_enforcement_identity_joins | 0 / 1 / 0 |
| E02 | ER14 | test_authenticated_enforcement_identity_joins | 0 / 1 / 0 |
| C01 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C02 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C03 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C04 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C05 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C06 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| C07 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| A3-R01 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |
| A3-R02 | ER15 | test_authenticated_capability_identity_joins | 0 / 1 / 0 |

## J01 — ER12

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.roster_key != self.subject.roster_key:
-            raise ValueError("discovered payload roster must match subject")
+        if False:
+            raise ValueError("discovered payload roster must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ...
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='host_surface') ... FAIL
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='host_version') ... FAIL
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='binary_digest') ... FAIL
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='configuration_digest') ... FAIL
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='enrollment_digest') ... FAIL
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='adapter_revision') ... FAIL

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='host_surface')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='host_version')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='binary_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='configuration_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='enrollment_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='roster_key', component='adapter_revision')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 790, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), "discovered payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=6)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

## J02 — ER12

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.observer_ref != self.observer_ref:
-            raise ValueError("discovered payload observer must match evidence observer")
+        if False:
+            raise ValueError("discovered payload observer must match evidence observer")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ...
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='observer_ref') ... FAIL

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='observer_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 801, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.011s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

## J03 — ER12

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.evidence_ref != self.evidence_ref:
-            raise ValueError("discovered payload evidence must match evidence reference")
+        if False:
+            raise ValueError("discovered payload evidence must match evidence reference")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ...
  test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='evidence_ref') ... FAIL

======================================================================
FAIL: test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) (cell='ER12', equality='evidence_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 801, in test_authenticated_discovered_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveredSet.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.011s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovered_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovered_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

## K01 — ER13

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.roster_key != self.subject.roster_key:
-            raise ValueError("coverage payload roster must match subject")
+        if False:
+            raise ValueError("coverage payload roster must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ...
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='host_surface') ... FAIL
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='host_version') ... FAIL
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='binary_digest') ... FAIL
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='configuration_digest') ... FAIL
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='enrollment_digest') ... FAIL
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='adapter_revision') ... FAIL

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='host_surface')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='host_version')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='binary_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='configuration_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='enrollment_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='roster_key', component='adapter_revision')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 816, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), "coverage payload roster must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.013s

FAILED (failures=6)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

## K02 — ER13

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.approved_roster_ref != self.subject.approved_roster_ref:
-            raise ValueError("coverage payload roster reference must match subject")
+        if False:
+            raise ValueError("coverage payload roster reference must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.014s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ...
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='approved_roster_ref') ... FAIL

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='approved_roster_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 824, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

## K03 — ER13

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.approved_roster_digest != self.subject.approved_roster_digest:
-            raise ValueError("coverage payload roster digest must match subject")
+        if False:
+            raise ValueError("coverage payload roster digest must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

Mutant, exit 1:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ...
  test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='approved_roster_digest') ... FAIL

======================================================================
FAIL: test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) (cell='ER13', equality='approved_roster_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 824, in test_authenticated_discovery_identity_joins
    self._assert_value_error(partial(AuthenticatedDiscoveryCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.013s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_discovery_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_discovery_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

## E01 — ER14

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.discovery_coverage_ref != self.subject.discovery_coverage_ref:
-            raise ValueError("enforcement payload coverage reference must match subject")
+        if False:
+            raise ValueError("enforcement payload coverage reference must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

Mutant, exit 1:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ...
  test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='PRESENT_ENTRIES', equality='discovery_coverage_ref') ... FAIL
  test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='ZERO_PRESENT_ENTRIES', equality='discovery_coverage_ref') ... FAIL

======================================================================
FAIL: test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='PRESENT_ENTRIES', equality='discovery_coverage_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 847, in test_authenticated_enforcement_identity_joins
    self._assert_value_error(partial(AuthenticatedEnforcementCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='ZERO_PRESENT_ENTRIES', equality='discovery_coverage_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 847, in test_authenticated_enforcement_identity_joins
    self._assert_value_error(partial(AuthenticatedEnforcementCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=2)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

## E02 — ER14

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.discovery_coverage_digest != self.subject.discovery_coverage_digest:
-            raise ValueError("enforcement payload coverage digest must match subject")
+        if False:
+            raise ValueError("enforcement payload coverage digest must match subject")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.010s

OK
```

Mutant, exit 1:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ...
  test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='PRESENT_ENTRIES', equality='discovery_coverage_digest') ... FAIL
  test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='ZERO_PRESENT_ENTRIES', equality='discovery_coverage_digest') ... FAIL

======================================================================
FAIL: test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='PRESENT_ENTRIES', equality='discovery_coverage_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 847, in test_authenticated_enforcement_identity_joins
    self._assert_value_error(partial(AuthenticatedEnforcementCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) (cell='ER14', payload_tag='ZERO_PRESENT_ENTRIES', equality='discovery_coverage_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 847, in test_authenticated_enforcement_identity_joins
    self._assert_value_error(partial(AuthenticatedEnforcementCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.011s

FAILED (failures=2)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_enforcement_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_enforcement_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

## C01 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            self.payload.observation_id != self.subject.observation_id
+            False
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='observation_id') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='observation_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 865, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.018s

OK
```

## C02 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.capability_id != self.subject.capability_id
+            or False
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_id') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 865, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.013s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

## C03 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.capability_key != self.subject.capability_key
+            or False
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='family') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='adapter_revision') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='platform') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='host_surface') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='family') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='adapter_revision') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='platform') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 865, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='family')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 875, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='adapter_revision')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 875, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='platform')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 875, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='capability_key', component='host_surface')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 880, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(host_key_payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='family')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 944, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='adapter_revision')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 944, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='platform')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 944, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 944, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.018s

FAILED (failures=9)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

## C04 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.claim_scope is not self.subject.claim_scope
+            or False
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='claim_scope') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='claim_scope')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 865, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.013s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

## C05 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.case_ids != self.subject.case_ids
+            or False
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='content') ... FAIL
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='content')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 904, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 908, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.015s

FAILED (failures=2)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.025s

OK
```

## C06 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.observer_ref != self.observer_ref:
-            raise ValueError("capability payload observer must match evidence observer")
+        if False:
+            raise ValueError("capability payload observer must match evidence observer")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='observer_ref') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='observer_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 953, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

## C07 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if self.payload.evidence_ref != self.evidence_ref:
-            raise ValueError("capability payload evidence must match evidence reference")
+        if False:
+            raise ValueError("capability payload evidence must match evidence reference")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='evidence_ref') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='evidence_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 953, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.014s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

## A3-R01 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.case_ids != self.subject.case_ids
+            or set(self.payload.case_ids) != set(self.subject.case_ids)
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.011s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='case_ids', mismatch='order')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 908, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.012s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

## A3-R02 — ER15

Path: `library/controlled_verification/qualification_ports.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            or self.payload.capability_key != self.subject.capability_key
+            or self.payload.capability_key.model_dump(exclude={"host_surface"}) != self.subject.capability_key.model_dump(exclude={"host_surface"})
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.013s

OK
```

Mutant, exit 1:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ...
  test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface') ... FAIL

======================================================================
FAIL: test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) (cell='ER15', equality='host_capability_key', component='host_surface')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 944, in test_authenticated_capability_identity_joins
    self._assert_value_error(partial(AuthenticatedCapabilityObservation.model_validate_json, json.dumps(payload)), "capability payload must match subject")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.013s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
```

Restored control, exit 0:
```text
test_authenticated_capability_identity_joins (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_authenticated_capability_identity_joins) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

## Historical BR03 / BR04 replay

Same command, unchanged observations:
```powershell
$cvqProbe = @'
import json,unittest
from pydantic import ValidationError
from library.controlled_verification import CapabilityObservation,CaseRefusalReason,ClaimScope,NoObservedRoster,Observation,PlannedHostEffectEntry,RefusedClaimProof
from tests.verification_qualification_fixtures import capability_key,planned_host_entry
class BaselinePredicateProbe(unittest.TestCase):
 def test_BR03_refused_unavailable_positive(self):
  for reason in (CaseRefusalReason.PREREQUISITE_UNPROVEN,CaseRefusalReason.RESOURCE_ENFORCEMENT_UNAVAILABLE,CaseRefusalReason.HOST_ROSTER_UNQUALIFIED):
   with self.subTest(reason=reason.value):
    value=CapabilityObservation(observation_id="observation-cvq",capability_id="capability-cvq",capability_key=capability_key(),claim_scope=ClaimScope.PURE_RULE,case_ids=("case-pure",),observer_ref="observer-cvq",evidence_ref="evidence-cvq",result=Observation.UNAVAILABLE,proof=RefusedClaimProof(reason=reason,admission_evidence_ref="admission-cvq"),roster_evidence=NoObservedRoster())
    self.assertEqual(value.result,Observation.UNAVAILABLE)
 def test_BR04_planned_sorting(self):
  payload=json.loads(planned_host_entry().model_dump_json()); payload["alias_ids"]=["alias-z","alias-a"]
  with self.assertRaises(ValidationError): PlannedHostEffectEntry.model_validate_json(json.dumps(payload))
unittest.main(verbosity=2)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqProbe
exit $LASTEXITCODE
```

Snapshot cvq-01-schema-review-closure03-correction; readback:
```text
5d7789db6b950d317e7b500b757aa77a54d609ed
```

Exit 1:
```text
test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) ...
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='PREREQUISITE_UNPROVEN') ... ERROR
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='RESOURCE_ENFORCEMENT_UNAVAILABLE') ... ERROR
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='HOST_ROSTER_UNQUALIFIED') ... ERROR
test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting) ... FAIL

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='PREREQUISITE_UNPROVEN')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 9, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='RESOURCE_ENFORCEMENT_UNAVAILABLE')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 9, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='HOST_ROSTER_UNQUALIFIED')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 9, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
FAIL: test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 13, in test_BR04_planned_sorting
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 2 tests in 0.003s

FAILED (failures=1, errors=3)
```

Snapshot cvq-01a2-review; readback:
```text
485d882f578f84dac1c975b32ced2a4ae6e7d43a
```

Exit 0:
```text
test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) ... ok
test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
```

## Verbatim predecessor-method replay

```powershell
$cvqPreservation = @'
import subprocess,sys,unittest
from pathlib import Path
source=subprocess.check_output(["git","show","ce49f735c6853c236a3504134d4a6959e7ca680f:tests/test_verification_qualification_domains.py"],text=True,encoding="utf-8")
namespace={"__name__":"preserved_A2_domain_tests","__file__":str(Path("tests/test_verification_qualification_domains.py").resolve())}
exec(compile(source,"ce49f735:tests/test_verification_qualification_domains.py","exec"),namespace)
suite=unittest.defaultTestLoader.loadTestsFromTestCase(namespace["QualificationDomainTests"])
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:],timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqPreservation
exit $LASTEXITCODE
```

Exit 0:
```text
test_local_result_and_evidence_consistency (preserved_A2_domain_tests.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (preserved_A2_domain_tests.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (preserved_A2_domain_tests.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (preserved_A2_domain_tests.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (preserved_A2_domain_tests.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.022s

OK
```

## Shared-source identity readback

```text
A1 wire owners and A2 production/manifest evidence byte-identical in Git
tests/test_verification_qualification_scalars.py:69:            payload["project_id"] = value
tests/test_verification_qualification_scalars.py:73:            payload["project_id"] = value
tests/test_verification_qualification_scalars.py:74:            with self.subTest(field="project_id", value=value):
tests/test_verification_qualification_scalars.py:75:                _assert_json_error(self, QualificationScope, payload, "project_id", "string_pattern_mismatch")
tests/test_verification_qualification_scalars.py:121:            (QualificationScope, qualification_scope().model_dump(), ("manifest_revision",)),
tests/test_verification_qualification_manifests.py:157:            ("project_id", "project-other", "case project must match scope"),
tests/test_verification_qualification_manifests.py:159:            ("manifest_revision", 2, "case manifest revision must match scope"),
tests/test_verification_qualification_manifests.py:397:            "project_id",
tests/test_verification_qualification_manifests.py:399:            "manifest_revision",
tests/test_verification_qualification_manifests.py:579:            _object(_array(payload["capability_requirements"])[0])["case_ids"] = ["case-missing"]
tests/test_verification_qualification_manifests.py:593:        with self.subTest(cell="CM04.requirement_capability.case_mismatch"):
tests/test_verification_qualification_manifests.py:595:            self._expect_manifest_error(payload, "requirement capability must match case")
tests/test_verification_qualification_manifests.py:662:        with self.subTest(cell="CM04.host_discovery.multiple_case_ids"):
tests/test_verification_qualification_manifests.py:663:            _object(_array(payload["capability_requirements"])[0])["case_ids"] = ["case-host-one", "case-host-two"]
tests/test_verification_qualification_manifests.py:704:        _array(_object(requirement_payload)["case_ids"]).append("case-pure")
tests/test_verification_qualification_manifests.py:705:        with self.subTest(cell="CM05.capability_requirement.case_ids_duplicate"):
tests/test_verification_qualification_manifests.py:708:                "capability case identifiers must be unique",
tests/test_verification_qualification_manifests.py:713:        with self.subTest(cell="CM05.manifest.case_ids_duplicate"):
```

## Final strict / focused / restoration check

Exact commands are ticket document06 Fixed final commands, each Python invocation bounded60s.
Git diff against 485d882f578f84dac1c975b32ced2a4ae6e7d43a and status were empty. All four temporarily mutated file
byte hashes follow the unreduced output; no snapshot mutation remains.

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
Ran 38 tests in 0.307s

OK
library/controlled_verification/qualification_ports.py 0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d
library/controlled_verification/roster_contracts.py 2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
library/controlled_verification/report_contracts.py 93d33ef8ff54e7352aa721884c2d62109b50b8802b8c80eeaed1e45ae668e432
tests/test_verification_qualification_domains.py 8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

