# CVQ-01A2 closure02 | Plan evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A2-C02-PLAN` / `REVIEW_EVIDENCE` / `02` |
| State | `COMPLETE / PREDICATE_EVIDENCE_VERIFIED` |
| Candidate | `ce49f735c6853c236a3504134d4a6959e7ca680f` |
| Owner / finite IDs | Root only; Q38–41 / H05 |
| Contract | [Evidence plan](cvq-01a2-closure02-evidence-plan.md) revision01, approved by ticket document07 at f4ecfb1; latest ticket document08 |


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

### Q38 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/qualification_ports.py`; pristine/restored byte SHA-256 `0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d`.
Observed named cells: `CM06.host_subject.missing_plan`, `CM06.host_subject.duplicate_plan`, `CM06.host_subject.nonempty_extra_plan`, `CM06.host_subject.approved_roster_ref_mismatch`, `CM06.host_subject.approved_roster_digest_mismatch`, `CM06.host_subject.roster_key_mismatch`, `CM06.pure_only.extra_plan`, `CM06.native_primitive_only.extra_plan`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if len(actual) != len(expected) or len(actual) != len(set(actual)) or any(
-            item not in expected for item in actual
-        ):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... \r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.missing_plan') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.duplicate_plan') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.approved_roster_ref_mismatch') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.approved_roster_digest_mismatch') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.roster_key_mismatch') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.pure_only.extra_plan') ... FAIL\r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.native_primitive_only.extra_plan') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.missing_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 750, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(missing, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.duplicate_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 754, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(duplicate, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 761, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(nonempty_extra, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.approved_roster_ref_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 770, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(payload, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.approved_roster_digest_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 770, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(payload, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.roster_key_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 775, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(wrong_key, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.pure_only.extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 796, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(extra_pure, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.native_primitive_only.extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 800, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(extra_native, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.017s\r\n\r\nFAILED (failures=8)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.018s\r\n\r\nOK\r\n"
  }
}
```

### Q39 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/qualification_ports.py`; pristine/restored byte SHA-256 `0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d`.
Observed named cells: `CM06.host_subject.nonempty_extra_plan`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-        if len(actual) != len(expected) or len(actual) != len(set(actual)) or any(
-            item not in expected for item in actual
-        ):
+        if (len(expected) == 0 and len(actual) > 0) or len(actual) < len(expected) or len(actual) != len(set(actual)) or any(
+            item not in actual for item in expected
+        ):
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.012s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... \r\n  test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) (cell='CM06.host_subject.nonempty_extra_plan')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 761, in test_approved_plan_pin_coverage\r\n    self._expect_port_error(nonempty_extra, \"approved roster plans must exactly cover host case subjects\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_approved_plan_pin_coverage (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_approved_plan_pin_coverage) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.017s\r\n\r\nOK\r\n"
  }
}
```

### Q40 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/qualification_ports.py`; pristine/restored byte SHA-256 `0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d`.
Observed named cells: `CM07.property.same_pin_membership_removed`, `CM07.property.wrong_pin_membership_rejected`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-            if case.case_id not in planned_case_refs:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... \r\n  test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.same_pin_membership_removed') ... FAIL\r\n  test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.wrong_pin_membership_rejected') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.same_pin_membership_removed')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 826, in test_discovery_intent_and_property_membership\r\n    self._expect_port_error(replaced, \"host property case must be named by its roster plan\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.wrong_pin_membership_rejected')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 854, in test_discovery_intent_and_property_membership\r\n    self._expect_port_error(cross_payload, \"host property case must be named by its roster plan\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.011s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  }
}
```

### Q41 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/qualification_ports.py`; pristine/restored byte SHA-256 `0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d`.
Observed named cells: `CM07.property.wrong_pin_membership_rejected`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/qualification_ports.py
@@
-                if plan.roster_key == case.subject.roster_key
-                and plan.approved_roster_ref == case.subject.approved_roster_ref
-                and plan.approved_roster_digest == case.subject.approved_roster_digest
+                if True
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... \r\n  test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.wrong_pin_membership_rejected') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) (cell='CM07.property.wrong_pin_membership_rejected')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 854, in test_discovery_intent_and_property_membership\r\n    self._expect_port_error(cross_payload, \"host property case must be named by its roster plan\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 94, in _expect_port_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "0c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_discovery_intent_and_property_membership (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_discovery_intent_and_property_membership) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nOK\r\n"
  }
}
```

## H05 historical evidence

The shared H01–05 extraction, exact command and full old/current streams are stored once in
[case evidence](cvq-01a2-closure02-case-evidence.md#historical-reproduction-h0105).
H05 names CM06.pure_only.extra_plan: old5d7789d accepts the extra plan (assertion red), current
ce49f735 rejects it (green). This reference is evidence reuse, not a second execution claim.
