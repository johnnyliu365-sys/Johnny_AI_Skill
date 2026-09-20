# CVQ-01A3 closure02 | Roster and collection evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A3-C02-ROSTER` / `REVIEW_EVIDENCE` / `01` |
| Authority | A3 document06 / closure02 at dddd59df94804f45ad74cc2892e1fcdca70e8341; source correction review59f5962 |
| Candidate | `485d882f578f84dac1c975b32ced2a4ae6e7d43a` |
| Recorder | root / ticket-review; retained helper is evidence-only |
| Scope | 28 candidate-bound temporary mutation records; no committed product change, host qualification or integration |
| Result | Each recorded control/restoration exit0 and mutant exit1; interpreted below, not merely counted |

Commands ran one foreground bounded child, timeout60 seconds, no load or automatic retries.
Existing tool orchestration held this finite ledger; no repository runner/framework was added.
Unreduced command output follows. Only CRLF and trailing whitespace are normalized for Markdown;
no diagnostic or traceback line is omitted. Unittest's own abbreviated assertion diffs remain.
Every mutation restores the exact candidate bytes, checks the recorded SHA-256 and reruns green.
These are reverse-mutation experiments after implementation, not fabricated initial TDD reds.

## Coverage interpretation

L01–06 and O01–06 independently expose each planned/observed entry and category guard.
G01/G02 and H01/H02 distinguish duplicate category from missing coverage; G03–05/H03–05
separate global entry, alias and case identities. H06–08 expose the remaining distinct-ID guards.
I01–03 remove each imported TestCase separately while leaving the local collection witness.

G01/H01's original named tests duplicate a PRESENT category: after the category guard is
weakened, the remaining global-entry guard rejects and the exact diagnostic assertion turns red.
These are diagnostic-contract reds, not claims that the invalid input was otherwise accepted.
Root separately composed seven valid ABSENT categories plus one duplicate ABSENT category.
No entry/alias/case identity exists in that packet, so the same one-clause mutation produces
ValidationError-not-raised for the category predicate alone. Those two separately labelled
independent probes and exact source are below; no unrelated guard was disabled, no test or
fixture source was changed, and no new product rule was introduced.

## Mutation index

| Operator | Cell | Method | Control / mutant / restored |
| --- | --- | --- | --- |
| L01 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| L02 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| L03 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| L04 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| L05 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| L06 | ER05 | test_planned_entry_and_category_rules | 0 / 1 / 0 |
| O01 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| O02 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| O03 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| O04 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| O05 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| O06 | ER07 | test_observed_entry_and_category_rules | 0 / 1 / 0 |
| G01 | ER06 | test_plan_global_coverage_and_uniqueness | 0 / 1 / 0 |
| G02 | ER06 | test_plan_global_coverage_and_uniqueness | 0 / 1 / 0 |
| G03 | ER06 | test_plan_global_coverage_and_uniqueness | 0 / 1 / 0 |
| G04 | ER06 | test_plan_global_coverage_and_uniqueness | 0 / 1 / 0 |
| G05 | ER06 | test_plan_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H01 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H02 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H03 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H04 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H05 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H06 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H07 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| H08 | ER08 | test_observed_global_coverage_and_uniqueness | 0 / 1 / 0 |
| I01 | ER16 | test_collection_retains_split_cases | 0 / 1 / 0 |
| I02 | ER16 | test_collection_retains_split_cases | 0 / 1 / 0 |
| I03 | ER16 | test_collection_retains_split_cases | 0 / 1 / 0 |

## L01 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.alias_ids) != len(set(self.alias_ids)):
-            raise ValueError("planned aliases must be unique")
+        if False:
+            raise ValueError("planned aliases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned aliases must be unique') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned aliases must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 442, in test_planned_entry_and_category_rules
    self._assert_value_error(partial(planned_host_entry, planned_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## L02 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if self.alias_ids != tuple(sorted(self.alias_ids)):
-            raise ValueError("planned aliases must be sorted")
+        if False:
+            raise ValueError("planned aliases must be sorted")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned aliases must be sorted') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned aliases must be sorted')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 442, in test_planned_entry_and_category_rules
    self._assert_value_error(partial(planned_host_entry, planned_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## L03 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.planned_enforcement_case_refs) != len(
-            set(self.planned_enforcement_case_refs)
-        ):
-            raise ValueError("planned enforcement cases must be unique")
+        if False:
+            raise ValueError("planned enforcement cases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned enforcement cases must be unique') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PlannedHostEffectEntry', invariant='planned enforcement cases must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 442, in test_planned_entry_and_category_rules
    self._assert_value_error(partial(planned_host_entry, planned_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## L04 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if any(entry.category is not self.category for entry in self.entries):
-            raise ValueError("planned entries must match the covered category")
+        if False:
+            raise ValueError("planned entries must match the covered category")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='category') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 446, in test_planned_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## L05 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(entry_ids) != len(set(entry_ids)):
-            raise ValueError("planned entries must be unique")
+        if False:
+            raise ValueError("planned entries must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='planned entries must be unique') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='planned entries must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 453, in test_planned_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## L06 — ER05

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(aliases) != len(set(aliases)):
-            raise ValueError("planned aliases must be unique")
+        if False:
+            raise ValueError("planned aliases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ...
  test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='planned aliases must be unique') ... FAIL

======================================================================
FAIL: test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) (cell='ER05', model='PresentHostCategoryPlan', invariant='planned aliases must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 460, in test_planned_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_planned_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_planned_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## O01 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.alias_ids) != len(set(self.alias_ids)):
-            raise ValueError("effect aliases must be unique")
+        if False:
+            raise ValueError("effect aliases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='effect aliases must be unique') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='effect aliases must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 525, in test_observed_entry_and_category_rules
    self._assert_value_error(partial(host_entry, planned_enforcement_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## O02 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if self.alias_ids != tuple(sorted(self.alias_ids)):
-            raise ValueError("effect aliases must be sorted")
+        if False:
+            raise ValueError("effect aliases must be sorted")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='effect aliases must be sorted') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='effect aliases must be sorted')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 525, in test_observed_entry_and_category_rules
    self._assert_value_error(partial(host_entry, planned_enforcement_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## O03 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.planned_enforcement_case_refs) != len(
-            set(self.planned_enforcement_case_refs)
-        ):
-            raise ValueError("enforcement case references must be unique")
+        if False:
+            raise ValueError("enforcement case references must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='enforcement case references must be unique') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='HostEffectEntry', invariant='enforcement case references must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 525, in test_observed_entry_and_category_rules
    self._assert_value_error(partial(host_entry, planned_enforcement_case_refs=cases, alias_ids=aliases, dispatch_entry_id="entry-a"), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## O04 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if any(entry.category is not self.category for entry in self.entries):
-            raise ValueError("present entries must match the covered category")
+        if False:
+            raise ValueError("present entries must match the covered category")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='category') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 529, in test_observed_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## O05 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(entry_ids) != len(set(entry_ids)):
-            raise ValueError("present entries must be unique")
+        if False:
+            raise ValueError("present entries must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='present entries must be unique') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='present entries must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 536, in test_observed_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## O06 — ER07

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(aliases) != len(set(aliases)):
-            raise ValueError("present aliases must be unique")
+        if False:
+            raise ValueError("present aliases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ...
  test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='present aliases must be unique') ... FAIL

======================================================================
FAIL: test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) (cell='ER07', model='PresentHostCategoryCoverage', invariant='present aliases must be unique')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 543, in test_observed_entry_and_category_rules
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_entry_and_category_rules (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_entry_and_category_rules) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## G01 — ER06

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster plan must contain each category exactly once")
+        if set(categories) != set(required):
+            raise ValueError("roster plan must contain each category exactly once")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant, exit 1:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ...
  test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='duplicate_category') ... FAIL

======================================================================
FAIL: test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='duplicate_category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 475, in test_plan_global_coverage_and_uniqueness
    self._assert_value_error(partial(ApprovedHostRosterPlan.model_validate_json, json.dumps(duplicate_category)), "roster plan must contain each category exactly once")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 97, in _assert_value_error
    self.assertIn(message, details[0]["msg"])
AssertionError: 'roster plan must contain each category exactly once' not found in 'Value error, planned entry identifiers must be globally unique'

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## G02 — ER06

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster plan must contain each category exactly once")
+        if len(categories) != len(set(categories)):
+            raise ValueError("roster plan must contain each category exactly once")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant, exit 1:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ...
  test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='missing_category') ... FAIL

======================================================================
FAIL: test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='missing_category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 470, in test_plan_global_coverage_and_uniqueness
    self._assert_value_error(partial(ApprovedHostRosterPlan.model_validate_json, json.dumps(omitted)), "roster plan must contain each category exactly once")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## G03 — ER06

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(entry_ids) != len(set(entry_ids)):
-            raise ValueError("planned entry identifiers must be globally unique")
+        if False:
+            raise ValueError("planned entry identifiers must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant, exit 1:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ...
  test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_entry_id') ... FAIL

======================================================================
FAIL: test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_entry_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 493, in test_plan_global_coverage_and_uniqueness
    self._assert_value_error(partial(ApprovedHostRosterPlan.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## G04 — ER06

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(aliases) != len(set(aliases)):
-            raise ValueError("planned aliases must be globally unique")
+        if False:
+            raise ValueError("planned aliases must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant, exit 1:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ...
  test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_alias_id') ... FAIL

======================================================================
FAIL: test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_alias_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 493, in test_plan_global_coverage_and_uniqueness
    self._assert_value_error(partial(ApprovedHostRosterPlan.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## G05 — ER06

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(case_refs) != len(set(case_refs)):
-            raise ValueError("planned enforcement case references must be globally unique")
+        if False:
+            raise ValueError("planned enforcement case references must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Mutant, exit 1:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ...
  test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_case_ref') ... FAIL

======================================================================
FAIL: test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) (cell='ER06', invariant='global_case_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 493, in test_plan_global_coverage_and_uniqueness
    self._assert_value_error(partial(ApprovedHostRosterPlan.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_plan_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_plan_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

## H01 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster coverage must contain each category exactly once")
+        if set(categories) != set(required):
+            raise ValueError("roster coverage must contain each category exactly once")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='duplicate_category') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='duplicate_category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 557, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(partial(HostRosterDiscoveryCoverage.model_validate_json, json.dumps(duplicate_category)), "roster coverage must contain each category exactly once")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 97, in _assert_value_error
    self.assertIn(message, details[0]["msg"])
AssertionError: 'roster coverage must contain each category exactly once' not found in 'Value error, observed entry identifiers must be globally unique'

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## H02 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster coverage must contain each category exactly once")
+        if len(categories) != len(set(categories)):
+            raise ValueError("roster coverage must contain each category exactly once")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='missing_category') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='missing_category')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 553, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(partial(HostRosterDiscoveryCoverage.model_validate_json, json.dumps(omitted)), "roster coverage must contain each category exactly once")
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H03 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(entry_ids) != len(set(entry_ids)):
-            raise ValueError("observed entry identifiers must be globally unique")
+        if False:
+            raise ValueError("observed entry identifiers must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_entry_id') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_entry_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 575, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(partial(HostRosterDiscoveryCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## H04 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(aliases) != len(set(aliases)):
-            raise ValueError("observed aliases must be globally unique")
+        if False:
+            raise ValueError("observed aliases must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_alias_id') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_alias_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 575, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(partial(HostRosterDiscoveryCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H05 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(case_refs) != len(set(case_refs)):
-            raise ValueError("observed enforcement case references must be globally unique")
+        if False:
+            raise ValueError("observed enforcement case references must be globally unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_case_ref') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', invariant='global_case_ref')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 575, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(partial(HostRosterDiscoveryCoverage.model_validate_json, json.dumps(payload)), message)
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.005s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H06 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.dispatch_entry_ids) != len(set(self.dispatch_entry_ids)):
-            raise ValueError("discovered entries must be unique")
+        if False:
+            raise ValueError("discovered entries must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='DiscoveredEffectSet', invariant='dispatch_entry_id') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='DiscoveredEffectSet', invariant='dispatch_entry_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 578, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H07 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(self.alias_ids) != len(set(self.alias_ids)):
-            raise ValueError("discovered aliases must be unique")
+        if False:
+            raise ValueError("discovered aliases must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='DiscoveredEffectSet', invariant='alias_id') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='DiscoveredEffectSet', invariant='alias_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 591, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.004s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H08 — ER08

Path: `library/controlled_verification/roster_contracts.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(ids) != len(set(ids)):
-            raise ValueError("enforcement observations must be unique")
+        if False:
+            raise ValueError("enforcement observations must be unique")
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Mutant, exit 1:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ...
  test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='PresentHostEnforcementCoverage', invariant='observation_dispatch_entry_id') ... FAIL

======================================================================
FAIL: test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) (cell='ER08', model='PresentHostEnforcementCoverage', invariant='observation_dispatch_entry_id')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 614, in test_observed_global_coverage_and_uniqueness
    self._assert_value_error(
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_evidence.py", line 92, in _assert_value_error
    with self.assertRaises(ValidationError) as captured:
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
2c672dba7998344343001623d1bb3b1fece12993a8bf88abbfcbbeeab3bf12db
```

Restored control, exit 0:
```text
test_observed_global_coverage_and_uniqueness (tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.test_observed_global_coverage_and_uniqueness) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

## I01 — ER16

Path: `tests/test_verification_qualification_domains.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_scalars import QualificationScalarTests
+
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
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
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Restored control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## I02 — ER16

Path: `tests/test_verification_qualification_domains.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_manifests import QualificationManifestAdmissionTests
+
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
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
Ran 1 test in 0.002s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Restored control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## I03 — ER16

Path: `tests/test_verification_qualification_domains.py`. Candidate: `485d882f578f84dac1c975b32ced2a4ae6e7d43a`.

Exact temporary patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/tests/test_verification_qualification_domains.py
@@
-from test_verification_qualification_evidence import QualificationEvidenceAdmissionTests
+
*** End Patch
```

Command (control, mutant and restored):
```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases
exit $LASTEXITCODE
```

Control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Mutant, exit 1:
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
Ran 1 test in 0.009s

FAILED (failures=1)
```

Byte restoration, exit 0:
```text
8318827b7273b7a1879412d84f3fd02732c5735f9e8cb3fc78e6e7492b9640b9
```

Restored control, exit 0:
```text
test_collection_retains_split_cases (tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## G01-independent — independent no-ID category input

Exact command:
```powershell
$cvqIndependent = @'
import json,unittest
from pydantic import ValidationError
from library.controlled_verification import ApprovedHostRosterPlan,HostRosterDiscoveryCoverage,EffectCategory
from tests.verification_qualification_fixtures import approved_roster_plan,discovery_coverage
class IndependentCategoryPredicateProbe(unittest.TestCase):
 def test_duplicate_category_without_duplicate_ids(self):
  rows=(
   ("ER06",ApprovedHostRosterPlan,approved_roster_plan().model_dump(mode="json"),[{"tag":"ABSENT","category":x.value} for x in EffectCategory],"roster plan must contain each category exactly once"),
   ("ER08",HostRosterDiscoveryCoverage,discovery_coverage().model_dump(mode="json"),[{"tag":"ABSENT","category":x.value,"discovery_surface_ref":"surface-cvq","absence_evidence_ref":"absence-"+x.value.lower().replace("_","-")} for x in EffectCategory],"roster coverage must contain each category exactly once"))
  for cell,model,payload,categories,message in rows:
   with self.subTest(cell=cell,invariant="duplicate_absent_category_without_ids"):
    payload["categories"]=categories
    self.assertEqual(len(model.model_validate_json(json.dumps(payload)).categories),7)
    payload["categories"]=[*categories,categories[-1]]
    with self.assertRaises(ValidationError) as caught:
     model.model_validate_json(json.dumps(payload))
    self.assertEqual(caught.exception.errors()[0]["loc"],())
    self.assertEqual(caught.exception.errors()[0]["type"],"value_error")
    self.assertIn(message,caught.exception.errors()[0]["msg"])
unittest.main(verbosity=2)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:],timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqIndependent
exit $LASTEXITCODE
```

Exact temporary source patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster plan must contain each category exactly once")
+        if set(categories) != set(required):
+            raise ValueError("roster plan must contain each category exactly once")
*** End Patch
```

control, exit 0:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

mutant, exit 1:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ...
  test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) (cell='ER06', invariant='duplicate_absent_category_without_ids') ... FAIL

======================================================================
FAIL: test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) (cell='ER06', invariant='duplicate_absent_category_without_ids')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 15, in test_duplicate_category_without_duplicate_ids
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

restore, exit 0:
```text

```

restored, exit 0:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

## H01-independent — independent no-ID category input

Exact command:
```powershell
$cvqIndependent = @'
import json,unittest
from pydantic import ValidationError
from library.controlled_verification import ApprovedHostRosterPlan,HostRosterDiscoveryCoverage,EffectCategory
from tests.verification_qualification_fixtures import approved_roster_plan,discovery_coverage
class IndependentCategoryPredicateProbe(unittest.TestCase):
 def test_duplicate_category_without_duplicate_ids(self):
  rows=(
   ("ER06",ApprovedHostRosterPlan,approved_roster_plan().model_dump(mode="json"),[{"tag":"ABSENT","category":x.value} for x in EffectCategory],"roster plan must contain each category exactly once"),
   ("ER08",HostRosterDiscoveryCoverage,discovery_coverage().model_dump(mode="json"),[{"tag":"ABSENT","category":x.value,"discovery_surface_ref":"surface-cvq","absence_evidence_ref":"absence-"+x.value.lower().replace("_","-")} for x in EffectCategory],"roster coverage must contain each category exactly once"))
  for cell,model,payload,categories,message in rows:
   with self.subTest(cell=cell,invariant="duplicate_absent_category_without_ids"):
    payload["categories"]=categories
    self.assertEqual(len(model.model_validate_json(json.dumps(payload)).categories),7)
    payload["categories"]=[*categories,categories[-1]]
    with self.assertRaises(ValidationError) as caught:
     model.model_validate_json(json.dumps(payload))
    self.assertEqual(caught.exception.errors()[0]["loc"],())
    self.assertEqual(caught.exception.errors()[0]["type"],"value_error")
    self.assertIn(message,caught.exception.errors()[0]["msg"])
unittest.main(verbosity=2)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:],timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqIndependent
exit $LASTEXITCODE
```

Exact temporary source patch:
```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/roster_contracts.py
@@
-        if len(categories) != len(set(categories)) or set(categories) != set(required):
-            raise ValueError("roster coverage must contain each category exactly once")
+        if set(categories) != set(required):
+            raise ValueError("roster coverage must contain each category exactly once")
*** End Patch
```

control, exit 0:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

mutant, exit 1:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ...
  test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) (cell='ER08', invariant='duplicate_absent_category_without_ids') ... FAIL

======================================================================
FAIL: test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) (cell='ER08', invariant='duplicate_absent_category_without_ids')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 15, in test_duplicate_category_without_duplicate_ids
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

restore, exit 0:
```text

```

restored, exit 0:
```text
test_duplicate_category_without_duplicate_ids (__main__.IndependentCategoryPredicateProbe.test_duplicate_category_without_duplicate_ids) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Final byte hash after both independent restores is recorded in join evidence's final checks.

