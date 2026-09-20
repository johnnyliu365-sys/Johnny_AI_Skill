# CVQ-01A1 closure02 SW07-08 execution evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01A1-C02-SW07-08` / `REVIEW_EVIDENCE` / `01` |
| State | `CAPTURED / NOT_CLOSURE_APPROVAL`; M02 is a blocking ticket/evidence-plan defect |
| Authority | A1 document06 at `0aa0184e9db460be2aaaa513c30d6636f18ae2d1`; exact owner signature binds document05 at `1e50d2ef457a7a5de392fb8b34eb9fc2a8f51011`, LF `d25b6c3b3f873a95eccea88e0e8ab222848cb67b5a87ace23958b480a85d0bbf` |
| Candidate / executor | `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc` / root ticket-review |
| Execution workspace | `C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02`, detached candidate snapshot |
| Limits / effects | One foreground command; timeout60s; pass1200s; zero retries/load/containers/provider/target effects |
| Review | [A1 review](cvq-01a1-scalar-wire-admission-code-review.md), section 7; raw failure is not itself approval |

## Capture and interpretation

These are the complete returned process-output strings, with CRLF represented as LF in this
Markdown leaf. No grep/tail/filter removed output. stdout/stderr ordering is the command tool's
combined capture. Blocks containing trailing spaces are losslessly JSON-encoded so Git whitespace
checks do not require deleting captured bytes; decode the JSON string to recover the full output.
Other blocks are plain text. stdout/stderr ordering remains the command tool's
combined capture; this is not a claim of independently timestamped streams. Unittest's own
abbreviated assertion diffs remain verbatim. Commands, exact patches, exit codes, restore hashes
and green reruns are retained. No generic mutation runner was added to the repository.

The 35 planned rows ran once each. Root fully inspected the blocking M02 trace and M03 identity;
other rows' captured failure identities/summaries were inspected, but the complete repetitive
raw streams have NOT all received final reviewer read-through. They remain captured evidence,
not 34 independently approved predicates. No closure approval, integration or continuation to
A2/A3/B is inferred. M01 is explicitly an oracle probe, not production proof.

## M25

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:08.522Z`; finished `2026-09-20T04:25:12.508Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    workload_duration_seconds: PositiveInteger = Field(le=30)
+    workload_duration_seconds: PositiveInteger = Field(le=31)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `346`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='workload_duration_seconds', value=31) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='workload_duration_seconds', value=31)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 207, in test_every_resource_bound\n    _assert_direct_error(self, ResourceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.004s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M26

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:12.514Z`; finished `2026-09-20T04:25:17.716Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    cpu_millicpu: PositiveInteger = Field(le=1_000)
+    cpu_millicpu: PositiveInteger = Field(le=1_001)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `341`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='cpu_millicpu', value=1001) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='cpu_millicpu', value=1001)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 207, in test_every_resource_bound\n    _assert_direct_error(self, ResourceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.006s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M27

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:17.722Z`; finished `2026-09-20T04:25:21.814Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    memory_bytes: PositiveInteger = Field(le=536_870_912)
+    memory_bytes: PositiveInteger = Field(le=536_870_913)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `343`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='memory_bytes', value=536870913) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='memory_bytes', value=536870913)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 207, in test_every_resource_bound\n    _assert_direct_error(self, ResourceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.004s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M28

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:21.819Z`; finished `2026-09-20T04:25:27.350Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    process_count: PositiveInteger = Field(le=4)
+    process_count: PositiveInteger = Field(le=5)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `340`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='process_count', value=5) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='process_count', value=5)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 207, in test_every_resource_bound\n    _assert_direct_error(self, ResourceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.004s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M29

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:27.357Z`; finished `2026-09-20T04:25:31.179Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    disk_bytes: PositiveInteger = Field(le=67_108_864)
+    disk_bytes: PositiveInteger = Field(le=67_108_865)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `342`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='disk_bytes', value=67108865) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='ResourceBounds', field='disk_bytes', value=67108865)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 207, in test_every_resource_bound\n    _assert_direct_error(self, ResourceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.004s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.004s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M30

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:31.184Z`; finished `2026-09-20T04:25:35.132Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    cleanup_seconds: PositiveInteger = Field(le=10)
+    cleanup_seconds: PositiveInteger = Field(le=11)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `341`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='CleanupBounds', field='cleanup_seconds', value=11) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='CleanupBounds', field='cleanup_seconds', value=11)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 214, in test_every_resource_bound\n    _assert_direct_error(self, CleanupBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.004s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M31

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:42.766Z`; finished `2026-09-20T04:25:46.629Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    total_bytes: PositiveInteger = Field(le=33_554_432)
+    total_bytes: PositiveInteger = Field(le=33_554_433)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `342`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='EvidenceBounds', field='total_bytes', value=33554433) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='EvidenceBounds', field='total_bytes', value=33554433)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 223, in test_every_resource_bound\n    _assert_direct_error(self, EvidenceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.005s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M32

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:46.633Z`; finished `2026-09-20T04:25:50.730Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    case_output_bytes: PositiveInteger = Field(le=262_144)
+    case_output_bytes: PositiveInteger = Field(le=262_145)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `344`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='EvidenceBounds', field='case_output_bytes', value=262145) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='EvidenceBounds', field='case_output_bytes', value=262145)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 223, in test_every_resource_bound\n    _assert_direct_error(self, EvidenceBounds, invalid_payload, field, \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.005s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M33

Source: `library/controlled_verification/manifest_contracts.py`. Started `2026-09-20T04:25:50.736Z`; finished `2026-09-20T04:25:56.142Z`.
Pristine and exact-restored byte SHA-256: `00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/manifest_contracts.py
@@
-    total_budget_seconds: PositiveInteger = Field(le=1_200)
+    total_budget_seconds: PositiveInteger = Field(le=1_201)
*** End Patch
```

### mutated: test_every_resource_bound

Exit `1`; captured output tokens reported by command tool `355`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```json
"test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... \n  test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='QualificationManifest', field='total_budget_seconds', value=1201) ... FAIL\n\n======================================================================\nFAIL: test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) (model='QualificationManifest', field='total_budget_seconds', value=1201)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 231, in test_every_resource_bound\n    _assert_direct_error(self, QualificationManifest, invalid_manifest, \"total_budget_seconds\", \"less_than_equal\")\n  File \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\.worktrees\\cvq-01a1-review-c02\\tests\\test_verification_qualification_scalars.py\", line 42, in _assert_direct_error\n    with test.assertRaises(ValidationError) as captured:\nAssertionError: ValidationError not raised\n\n----------------------------------------------------------------------\nRan 1 test in 0.005s\n\nFAILED (failures=1)\n"
```

### restored: test_every_resource_bound

Exit `0`; captured output tokens reported by command tool `59`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound
exit $LASTEXITCODE
```

```text
test_every_resource_bound (tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/manifest_contracts.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=00e8bef4960d9e6add50145eda223969879514c93c6d0f5032d87a9aa1037354
```

## M34

Source: `library/controlled_verification/qualification_values.py`. Started `2026-09-20T04:25:56.148Z`; finished `2026-09-20T04:26:01.784Z`.
Pristine and exact-restored byte SHA-256: `f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/qualification_values.py
@@
-        frozen=True,
+        frozen=False,
*** End Patch
```

### mutated: test_immutable_contract_configuration

Exit `1`; captured output tokens reported by command tool `226`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration
exit $LASTEXITCODE
```

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... FAIL

======================================================================
FAIL: test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a1-review-c02\tests\test_verification_qualification_contracts.py", line 1124, in test_immutable_contract_configuration
    self.assertTrue(scope.model_config["frozen"])
AssertionError: False is not true

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

### restored: test_immutable_contract_configuration

Exit `0`; captured output tokens reported by command tool `66`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration
exit $LASTEXITCODE
```

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/qualification_values.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97
```

## M35

Source: `library/controlled_verification/qualification_values.py`. Started `2026-09-20T04:26:01.789Z`; finished `2026-09-20T04:26:05.741Z`.
Pristine and exact-restored byte SHA-256: `f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97`.

```diff
*** Begin Patch
*** Update File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a1-review-c02/library/controlled_verification/qualification_values.py
@@
-        revalidate_instances="always",
+        revalidate_instances="never",
*** End Patch
```

### mutated: test_immutable_contract_configuration

Exit `1`; captured output tokens reported by command tool `238`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration
exit $LASTEXITCODE
```

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... FAIL

======================================================================
FAIL: test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a1-review-c02\tests\test_verification_qualification_contracts.py", line 1128, in test_immutable_contract_configuration
    self.assertEqual(scope.model_config["revalidate_instances"], "always")
AssertionError: 'never' != 'always'
- never
+ always


----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)
```

### restored: test_immutable_contract_configuration

Exit `0`; captured output tokens reported by command tool `66`.

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration
exit $LASTEXITCODE
```

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

Restoration: `git restore --source=8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc --worktree -- library/controlled_verification/qualification_values.py`;
SHA-256 equality and clean Git status were checked before the green rerun (exit `0`).

```text
RESTORED_SHA256=f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97
```

## Final restored verification

Execution pass began `2026-09-20T04:16:30.054Z`;
final checks ended `2026-09-20T04:26:44.865Z`.
Elapsed `614.811` seconds, below1200.
All35 restoration hashes matched. Final `git diff --check 1270664213d71eb2da524ecf7bf1885f28ffc82f 8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc` and snapshot status were clean (exit0).

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
exit $LASTEXITCODE
```

Exit `0`.

```text
Success: no issues found in 15 source files
```

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
exit $LASTEXITCODE
```

Exit `0`.

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
test_all_five_case_kind_binding_subject_rows_roundtrip (tests.test_verification_qualification_domains.QualificationDomainTests.test_all_five_case_kind_binding_subject_rows_roundtrip) ... ok
test_approved_manifest_plan_coverage (tests.test_verification_qualification_domains.QualificationDomainTests.test_approved_manifest_plan_coverage) ... ok
test_case_binding_identity_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_case_binding_identity_matrix) ... ok
test_constructor_identity_and_applicability_joins (tests.test_verification_qualification_domains.QualificationDomainTests.test_constructor_identity_and_applicability_joins) ... ok
test_duplicate_collections_and_report_cells_reject (tests.test_verification_qualification_domains.QualificationDomainTests.test_duplicate_collections_and_report_cells_reject) ... ok
test_kind_key_subject_applicability_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_kind_key_subject_applicability_matrix) ... ok
test_local_result_and_evidence_consistency (tests.test_verification_qualification_domains.QualificationDomainTests.test_local_result_and_evidence_consistency) ... ok
test_refusal_proof_result_matrix (tests.test_verification_qualification_domains.QualificationDomainTests.test_refusal_proof_result_matrix) ... ok
test_roster_local_invariants (tests.test_verification_qualification_domains.QualificationDomainTests.test_roster_local_invariants) ... ok
test_strict_boundary_rejection (tests.test_verification_qualification_domains.QualificationDomainTests.test_strict_boundary_rejection) ... ok
test_union_and_constructor_boundaries (tests.test_verification_qualification_domains.QualificationDomainTests.test_union_and_constructor_boundaries) ... ok
test_every_resource_bound (test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound) ... ok
test_identifier_digest_text_domains (test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok
test_integer_domain_edges (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges) ... ok
test_integer_domains_are_strict (test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict) ... ok

----------------------------------------------------------------------
Ran 26 tests in 0.227s

OK
```
