# CVQ-01A2 closure02 | Manifest evidence

## Predecessor per-observation preservation audit

Source: immutable8d6b8291:tests/test_verification_qualification_domains.py, six relocated
methods; candidate ce49f735. Rows below map individual assertions, not just method names.
Old cases changed one equality endpoint (binding versus scope); current CM01 sometimes changes
the other endpoint. Those exercise the same literal comparator but are not claimed byte-identical
fixtures. The exact old method bodies also ran unchanged in memory on the candidate, including
all their original values, paths, constructors and assertions; raw results follow.

| Old method / individual observation(s) | Current observed cell(s) / oracle |
| --- | --- |
| case_binding_identity_matrix: project_id=project-other, baseline_digest=f×64, manifest_revision=2, manifest_digest=f×64 | CM01.scope.project_id/baseline_digest/manifest_revision/manifest_digest; same binding/scope equality validators, literal diagnostics; Q08–11 |
| same: binding.case_id=case-other, fixture_digest=f×64 | CM01.binding.case_id/fixture_digest; Q01–02 |
| same: native executable_digest, dependency_digest, argv_digest, cwd_digest, environment_plan_digest each f×64 | CM01.native.<each five literal fields>; Q03–07 |
| kind_key_subject_applicability_matrix: pure HOST_MEDIATION -> NO_ROSTER positive | CM02.valid.pure_host_mediation_no_roster; unchanged JSON edits and subject equality; H04 |
| same: discovery subject CODEX_DESKTOP versus CLI; native key GENERIC | CM02.host_surface.discovery_mismatch; CM02.platform.native_discovery_generic; Q15/Q14 |
| same: pure manifest scope=NATIVE_PROBE | CM04.scope.case-pure; Q27 |
| same: source-property RESPONSIBILITY_ADMISSION without WA04 rejects, with ordered WA04 pair admits | CM03.wa04.source_property_missing; C02.P.wa04_control and C02.K.source_property.PR/HR; Q19 |
| same: pure binding + ADVERSARIAL_WORKLOAD rejects | CM02.binding_kind.pure_binding_adversarial; Q12 |
| same: nonhost discovery + HOST_DISCOVERY subject rejects | CM02.subject.nonhost_discovery_host_subject; Q13 |
| same: real-host property subject tag HOST_PROPERTY; same native case GENERIC rejects | C02.K.real_host_property.HM literal tag/class; CM02.platform.host_property_generic; Q14 |
| same: scope lacks capability-cvq; requirement key WINDOWS disagrees with GENERIC | CM04.case_capability.outside_scope; CM04.requirement_key.case_mismatch; Q22/Q26; old opposite-membership endpoint replay preserved below |
| same: duplicate prerequisite key/full requirement; prerequisite adapter_revision=2 | CM05.case.prerequisite_requirements.duplicate; CM03.order.requirement_key_changed; Q32/Q21 |
| same: one HOST_DISCOVERY requirement names case-host-one and case-host-two | CM04.host_discovery.multiple_case_ids; Q28 |
| approved_manifest_plan_coverage: pure roster_plans=() positive; extra plan rejects | CM06.pure_only.empty_plans / extra_plan; Q38/H05 |
| same: one host plan positive; wrong approved_roster_ref=roster-other; missing []; duplicate | CM06.host_subject.correct_unique_plan / approved_roster_ref_mismatch / missing_plan / duplicate_plan; Q38 |
| same: wrong roster host_surface=CODEX_DESKTOP; approved_roster_digest=e×64 | CM06.host_subject.roster_key_mismatch / approved_roster_digest_mismatch; Q38 |
| same: planned case-property positive; case-not-in-plan rejects | CM07.property.same_pin_membership_positive / same_pin_membership_removed; equivalent membership pair with literal old case ID replay below; Q40 |
| duplicate_collections_and_report_cells_reject: capability-cvq twice; dependency e×64 twice; same manifest case twice | CM05.scope.capability_ids_duplicate / case.dependency_digests.duplicate / manifest.case_ids_duplicate; Q29/Q30/Q35 |
| constructor_identity_and_applicability_joins: case capability-other; binding project-other; fixture f×64; case-missing; NATIVE_PROBE scope | CM04.case_capability.outside_scope; CM01.scope.project_id; CM01.binding.fixture_digest; CM04.requirement_case.missing; CM04.scope.case-pure; exact old containing-manifest paths replay below |
| all_five_case_kind_binding_subject_rows_roundtrip: generic pure, WINDOWS nonhost discovery, host discovery, WINDOWS adversarial, real-host property | CM02.valid.pure_rule_generic; C02.K.trusted_native_discovery.PN/HM; C02.K.adversarial_workload.PN; C02.K.real_host_property.HM; full DTO equality, not partial-field equality |

Closure02 preserves closure01's additional GENERIC source-property full roundtrip in
CM02.valid.source_property_generic, source-property host-key positive, platform-key forbidden
HOST_MEDIATION literal field error, closed F03 two-distinct prerequisite set and closed F04
nonempty-host extra plan. Other five test methods and shared fixtures are unchanged by
closure02; all old negative cells remain. The enlarged method is still a finite single
case-admission responsibility, with scenarios owned by existing shared fixtures; no new
helper, factory, runtime behavior, orchestration or prompt prose is introduced.

Exact predecessor extraction/replay command (no files written; only candidate library imported):

```powershell
$predecessorAudit = @'
import ast,subprocess,unittest
from pathlib import Path
source=subprocess.check_output(["git","show","8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc:tests/test_verification_qualification_domains.py"],text=True)
tree=ast.parse(source)
names={
"test_case_binding_identity_matrix",
"test_kind_key_subject_applicability_matrix",
"test_approved_manifest_plan_coverage",
"test_duplicate_collections_and_report_cells_reject",
"test_constructor_identity_and_applicability_joins",
"test_all_five_case_kind_binding_subject_rows_roundtrip",
}
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="QualificationDomainTests")
cls.body=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
assert {n.name for n in cls.body}==names
tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
namespace={"__name__":"predecessor_observations","__file__":str(Path.cwd()/"tests/test_verification_qualification_domains.py")}
exec(compile(ast.fix_missing_locations(tree),"8d6b8291:test_verification_qualification_domains.py","exec"),namespace)
suite=unittest.defaultTestLoader.loadTestsFromTestCase(namespace["QualificationDomainTests"])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $predecessorAudit
exit $LASTEXITCODE
```

Exit0, unreduced output:

```json
"test_all_five_case_kind_binding_subject_rows_roundtrip (predecessor_observations.QualificationDomainTests.test_all_five_case_kind_binding_subject_rows_roundtrip) ... ok\r\ntest_approved_manifest_plan_coverage (predecessor_observations.QualificationDomainTests.test_approved_manifest_plan_coverage) ... ok\r\ntest_case_binding_identity_matrix (predecessor_observations.QualificationDomainTests.test_case_binding_identity_matrix) ... ok\r\ntest_constructor_identity_and_applicability_joins (predecessor_observations.QualificationDomainTests.test_constructor_identity_and_applicability_joins) ... ok\r\ntest_duplicate_collections_and_report_cells_reject (predecessor_observations.QualificationDomainTests.test_duplicate_collections_and_report_cells_reject) ... ok\r\ntest_kind_key_subject_applicability_matrix (predecessor_observations.QualificationDomainTests.test_kind_key_subject_applicability_matrix) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 6 tests in 0.026s\r\n\r\nOK\r\n"
```


| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A2-C02-MANIFEST` / `REVIEW_EVIDENCE` / `02` |
| State | `COMPLETE / PREDICATE_EVIDENCE_VERIFIED` |
| Candidate | `ce49f735c6853c236a3504134d4a6959e7ca680f` |
| Owner / finite IDs | Root only; Q22–37 / predecessor observations |
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

### Q22 — LITERAL_DIAGNOSTIC_CHANGE

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.case_capability.outside_scope`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if case.capability_id not in self.scope.capability_ids:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.case_capability.outside_scope') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.case_capability.outside_scope')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 570, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"case capability must belong to scope\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 91, in _expect_manifest_error\r\n    self._assert_root_error(raised.exception, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 81, in _assert_root_error\r\n    self.assertIn(diagnostic, str(details[0][\"msg\"]))\r\nAssertionError: 'case capability must belong to scope' not found in 'Value error, requirement capability must match case'\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.024s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.024s\r\n\r\nOK\r\n"
  }
}
```

### Q23 — LITERAL_DIAGNOSTIC_CHANGE

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.requirement_capability.outside_scope`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-            if requirement.capability_id not in self.scope.capability_ids:
+            if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_capability.outside_scope') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_capability.outside_scope')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 575, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement capability must belong to scope\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 91, in _expect_manifest_error\r\n    self._assert_root_error(raised.exception, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 81, in _assert_root_error\r\n    self.assertIn(diagnostic, str(details[0][\"msg\"]))\r\nAssertionError: 'requirement capability must belong to scope' not found in 'Value error, requirement capability must match case'\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.019s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nOK\r\n"
  }
}
```

### Q24 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.requirement_case.missing`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                    raise ValueError("requirement case must exist in manifest")
+                    continue
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_case.missing') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_case.missing')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 580, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement case must exist in manifest\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.015s\r\n\r\nOK\r\n"
  }
}
```

### Q25 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.requirement_capability.case_mismatch`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if matched_case.capability_id != requirement.capability_id:
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.012s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_capability.case_mismatch') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_capability.case_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 595, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement capability must match case\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.017s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nOK\r\n"
  }
}
```

### Q26 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.requirement_key.case_mismatch`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if matched_case.capability_key != requirement.capability_key:
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_key.case_mismatch') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.requirement_key.case_mismatch')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 604, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement key must match case\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.016s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.021s\r\n\r\nOK\r\n"
  }
}
```

### Q27 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.scope.case-pure`, `CM04.scope.case-source-property`, `CM04.scope.case-native-probe`, `CM04.scope.case-host-discovery`, `CM04.scope.case-adversarial`, `CM04.scope.case-property`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if requirement.claim_scope is not derived_scope:
+                if False:
@@
-                if requirement.claim_scope is ClaimScope.PURE_RULE and not isinstance(matched_case.subject, NoRosterSubject):
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.013s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-pure', scope=<ClaimScope.PURE_RULE: 'PURE_RULE'>) ... FAIL\r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-source-property', scope=<ClaimScope.PURE_RULE: 'PURE_RULE'>) ... FAIL\r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-native-probe', scope=<ClaimScope.NATIVE_PROBE: 'NATIVE_PROBE'>) ... FAIL\r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-host-discovery', scope=<ClaimScope.HOST_DISCOVERY: 'HOST_DISCOVERY'>) ... FAIL\r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-adversarial', scope=<ClaimScope.NATIVE_PROPERTY: 'NATIVE_PROPERTY'>) ... FAIL\r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-property', scope=<ClaimScope.HOST_PROPERTY: 'HOST_PROPERTY'>) ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-pure', scope=<ClaimScope.PURE_RULE: 'PURE_RULE'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-source-property', scope=<ClaimScope.PURE_RULE: 'PURE_RULE'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-native-probe', scope=<ClaimScope.NATIVE_PROBE: 'NATIVE_PROBE'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-host-discovery', scope=<ClaimScope.HOST_DISCOVERY: 'HOST_DISCOVERY'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-adversarial', scope=<ClaimScope.NATIVE_PROPERTY: 'NATIVE_PROPERTY'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.scope.case-property', scope=<ClaimScope.HOST_PROPERTY: 'HOST_PROPERTY'>)\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 649, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"requirement scope must match case kind\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.017s\r\n\r\nFAILED (failures=6)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.015s\r\n\r\nOK\r\n"
  }
}
```

### Q28 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM04.host_discovery.multiple_case_ids`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-                if requirement.claim_scope is ClaimScope.HOST_DISCOVERY and len(requirement.case_ids) != 1:
+                if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... \r\n  test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.host_discovery.multiple_case_ids') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) (cell='CM04.host_discovery.multiple_case_ids')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 664, in test_capability_requirement_joins\r\n    self._expect_manifest_error(payload, \"host discovery requirement has one case\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.014s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_capability_requirement_joins (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_capability_requirement_joins) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.017s\r\n\r\nOK\r\n"
  }
}
```

### Q29 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.scope.capability_ids_duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.capability_ids) != len(set(self.capability_ids)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.scope.capability_ids_duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.scope.capability_ids_duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 670, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_direct_error(\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 99, in _expect_direct_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.010s\r\n\r\nOK\r\n"
  }
}
```

### Q30 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.case.dependency_digests.duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.dependency_digests) != len(set(self.dependency_digests)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.dependency_digests.duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.dependency_digests.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  }
}
```

### Q31 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.case.prerequisite_keys.duplicate`, `CM05.case.prerequisite_requirements.duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.prerequisite_keys) != len(set(self.prerequisite_keys)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_keys.duplicate') ... FAIL\r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_requirements.duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_keys.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_requirements.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 86, in _expect_case_error\r\n    self._assert_root_error(raised.exception, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 81, in _assert_root_error\r\n    self.assertIn(diagnostic, str(details[0][\"msg\"]))\r\nAssertionError: 'case prerequisite keys must be unique' not found in 'Value error, prerequisite requirements must be unique'\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.011s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  }
}
```

### Q32 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.case.prerequisite_keys.duplicate`, `CM05.case.prerequisite_requirements.duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.prerequisite_keys) != len(set(self.prerequisite_keys)):
+        if False:
@@
-        if len(self.prerequisite_requirements) != len(set(self.prerequisite_requirements)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_keys.duplicate') ... FAIL\r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_requirements.duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_keys.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.prerequisite_requirements.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nFAILED (failures=2)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nOK\r\n"
  }
}
```

### Q33 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.case.expected_check_ids.duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.expected_check_ids) != len(set(self.expected_check_ids)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.expected_check_ids.duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.case.expected_check_ids.duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 693, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_case_error(case, diagnostic)\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 84, in _expect_case_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q34 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.capability_requirement.case_ids_duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(self.case_ids) != len(set(self.case_ids)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.capability_requirement.case_ids_duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.capability_requirement.case_ids_duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 706, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_direct_error(\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 99, in _expect_direct_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nOK\r\n"
  }
}
```

### Q35 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.manifest.case_ids_duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(case_ids) != len(set(case_ids)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.manifest.case_ids_duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.manifest.case_ids_duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 714, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_manifest_error(duplicate_cases, \"manifest case identifiers must be unique\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.009s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q36 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/manifest_contracts.py`; pristine/restored byte SHA-256 `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.
Observed named cells: `CM05.manifest.requirement_ids_duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/manifest_contracts.py
@@
-        if len(requirement_ids) != len(set(requirement_ids)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.manifest.requirement_ids_duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.manifest.requirement_ids_duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 721, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_manifest_error(duplicate_requirements, \"capability requirement identifiers must be unique\")\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 89, in _expect_manifest_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.007s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```

### Q37 — NAMED_ASSERTION_RED

Candidate `ce49f735c6853c236a3504134d4a6959e7ca680f`; source `library/controlled_verification/prerequisite_contracts.py`; pristine/restored byte SHA-256 `8447770d211b4d0df622f30ff6d24812cc3549768c24c186ef5598ae95b35d8e`.
Observed named cells: `CM05.prerequisite_set.exact_pair_duplicate`.

Exact temporary patch:

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review/library/controlled_verification/prerequisite_contracts.py
@@
-        if len(keys) != len(set(keys)):
+        if False:
*** End Patch
```

Identical control/mutant/restored command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates
exit $LASTEXITCODE
```

Unreduced outputs, JSON strings preserve CRLF/trailing whitespace:

```json
{
  "control": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.006s\r\n\r\nOK\r\n"
  },
  "mutant": {
    "exit": 1,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... \r\n  test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.prerequisite_set.exact_pair_duplicate') ... FAIL\r\n\r\n======================================================================\r\nFAIL: test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) (cell='CM05.prerequisite_set.exact_pair_duplicate')\r\n----------------------------------------------------------------------\r\nTraceback (most recent call last):\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 730, in test_manifest_and_prerequisite_duplicates\r\n    self._expect_direct_error(\r\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a2-review\\tests\\test_verification_qualification_manifests.py\", line 99, in _expect_direct_error\r\n    with self.assertRaises(ValidationError) as raised:\r\nAssertionError: ValidationError not raised\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nFAILED (failures=1)\r\n"
  },
  "restoration": {
    "exit": 0,
    "output": "8447770d211b4d0df622f30ff6d24812cc3549768c24c186ef5598ae95b35d8e\r\n"
  },
  "restored": {
    "exit": 0,
    "output": "test_manifest_and_prerequisite_duplicates (tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.test_manifest_and_prerequisite_duplicates) ... ok\r\n\r\n----------------------------------------------------------------------\r\nRan 1 test in 0.008s\r\n\r\nOK\r\n"
  }
}
```
