# UIX-02 closure revision 05 evidence

Authority: registry/main `117346cf44fbbc75a08aca5677f223c38df0fb00`; ticket revision 15;
baseline `b419954bc57777661d7522247ffc26977f668ca7`; candidate under review
`448ea232761a7fbd0152efe7279bcea0a7c442e3`; branch
`implement/plugin-adoption-quality-uix-02`.

This correction changes only this evidence leaf and its direct README index. The production
source and focused tests are unchanged. Production source was byte-exact to baseline before and
after every temporary mutation: SHA-256
`6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917`.

## R05 finite acceptance evidence

### UIR7 — closed production-source grammar

The test-owned `_production_source_policy_violations(tree: ast.Module)` uses literal policy data
for the exact import forms/members/relative levels. It rejects aliases, star imports, unlisted
modules/symbols and wrong levels; loaded double-underscore names/attributes (including
`__builtins__`), unknown/qualified/dynamic call targets, call-result attributes, starred args and
unpacked keywords. `__all__` assignment is explicitly allowed. Hostile snippets are parsed only,
never executed, and cover module-alias `Any`, aliased `cast`, multiple ordinary `Any` aliases,
direct/indirect builtins, call-result attributes, star imports, unlisted forms, wrong levels,
aliases, starred/unpacked calls and unknown callees.

Exact production mutation applied with `apply_patch`:

```diff
 _SHA256_PATTERN = r"^[0-9a-f]{64}$"
+
+if False:
+    __import__("os").system("never-executed")
```

Direct named red command and complete output:

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
======================================================================
FAIL: test_uir7_ast_proves_private_no_effect_boundary (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 892, in test_uir7_ast_proves_private_no_effect_boundary
    self.assertEqual((), _production_source_policy_violations(tree))
AssertionError: Tuples differ: () != ("unlisted call target: __import__('os').s[83 chars]t__')

Second tuple contains 3 additional elements.
First extra element 0:
"unlisted call target: __import__('os').system"

- ()
+ ("unlisted call target: __import__('os').system",
+  'unlisted call target: __import__',
+  'double-underscore name loaded: __import__')

----------------------------------------------------------------------
Ran 1 test in 0.024s

FAILED (failures=1)
```

Exact restoration removed those three added lines. Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
----------------------------------------------------------------------
Ran 1 test in 0.027s

OK
```

### UIR6 — independent observation uniqueness

The focused test contains separately named `rendered-desktop-observation-reference` and
`rendered-mobile-observation-reference` collisions, with all other screenshot refs and digests
unique.

Exact production mutation changed the rendered duplicate set from
`{desktop_screenshot_ref, mobile_screenshot_ref, renderer_observation_ref}` / size `3` to
`{desktop_screenshot_ref, mobile_screenshot_ref}` / size `2`.

Direct named red command and complete output:

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
======================================================================
FAIL: test_uir6_state_duplicate_and_identity_mismatch_refuse (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse) (duplicate_dimension='rendered-desktop-observation-reference')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 806, in test_uir6_state_duplicate_and_identity_mismatch_refuse
    self.assertIsInstance(duplicate_result, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='rendererobservation', mobile_screenshot_ref='screenshotmobile', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>

======================================================================
FAIL: test_uir6_state_duplicate_and_identity_mismatch_refuse (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse) (duplicate_dimension='rendered-mobile-observation-reference')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 806, in test_uir6_state_duplicate_and_identity_mismatch_refuse
    self.assertIsInstance(duplicate_result, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='screenshotdesktop', mobile_screenshot_ref='rendererobservation', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.007s

FAILED (failures=2)
```

Exact restoration restored the three-member set. Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

### UIR4 — strict acknowledgement at the named seam

UIR4 directly and through nested request validation covers missing, `False`, `None`, `1`, `1.0`
and `"true"`, with all other artifact fields valid. UNAVAILABLE and DECLINED fallback admissions
assert the acknowledgement is the literal `True`.

Exact production mutation added `= True` to
`owner_manual_open_acknowledgement: Literal[True]`.

Direct named red command and complete output:

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback
======================================================================
FAIL: test_uir4_absence_or_decline_uses_artifact_fallback (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback) (acknowledgement='missing-direct')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 567, in test_uir4_absence_or_decline_uses_artifact_fallback
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir4_absence_or_decline_uses_artifact_fallback (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback) (acknowledgement='missing-nested')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 575, in test_uir4_absence_or_decline_uses_artifact_fallback
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (failures=2)
```

Exact restoration removed `= True`. Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

## Retained UIRM1–UIRM6 evidence

Each mutation below was applied with `apply_patch` to the exact production line, run through the
direct named unittest cell, then exactly restored. Every restore reported source SHA-256
`6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917` before the green command.

### UIRM1 — authority branch bypass

Mutation: replace
`if trusted_request.capability_state is RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED:`
with `if False:`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission
======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (evidence='rendered')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 490, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.STATE_EVIDENCE_MISMATCH: 'STATE_EVIDENCE_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (evidence='artifact')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 490, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: AdmittedArtifactDecision(kind='ADMITTED_ARTIFACT', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.ARTIFACT_ONLY: 'ARTIFACT_ONLY'>, evidence=ArtifactReferenceEvidence(kind='ARTIFACT_ONLY', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_artifact_ref='artifactdesktop', mobile_artifact_ref='artifactmobile', artifact_set_digest='dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd', owner_manual_open_acknowledgement=True)) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (evidence='unavailable')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 490, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.STATE_EVIDENCE_MISMATCH: 'STATE_EVIDENCE_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (ordering='binding-before-authority')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 549, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.CONTENT_BINDING_MISMATCH: 'CONTENT_BINDING_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (ordering='duplicate-before-authority')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 549, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.DUPLICATE_EVIDENCE: 'DUPLICATE_EVIDENCE'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (ordering='target-before-authority')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 549, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (ordering='state-before-authority')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 549, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.STATE_EVIDENCE_MISMATCH: 'STATE_EVIDENCE_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.005s

FAILED (failures=7)
```

Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission
----------------------------------------------------------------------
Ran 1 test in 0.003s

OK
```

### UIRM2 — always-match target

Mutation: replace `_target_matches` return expression with `return True`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target
======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 628, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(mismatch, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='screenshotdesktop', mobile_screenshot_ref='screenshotmobile', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>
----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (failures=1)
```

Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target
----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

### UIRM3 — default acknowledgement

Mutation: add `= True` to `owner_manual_open_acknowledgement: Literal[True]`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback
======================================================================
FAIL: test_uir4_absence_or_decline_uses_artifact_fallback (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback) (acknowledgement='missing-direct')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 567, in test_uir4_absence_or_decline_uses_artifact_fallback
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir4_absence_or_decline_uses_artifact_fallback (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback) (acknowledgement='missing-nested')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 575, in test_uir4_absence_or_decline_uses_artifact_fallback
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (failures=2)
```

Exact restoration removed `= True`. Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

### UIRM4 — omit brief binding comparison

Mutation: replace only `and binding.brief_id == request.brief_id` with `and True`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
======================================================================
FAIL: test_uir6_state_duplicate_and_identity_mismatch_refuse (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 862, in test_uir6_state_duplicate_and_identity_mismatch_refuse
    self.assertIsInstance(changed_brief_result, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefother', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='screenshotdesktop', mobile_screenshot_ref='screenshotmobile', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>
----------------------------------------------------------------------
Ran 1 test in 0.008s

FAILED (failures=1)
```

Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

### UIRM5 — allow punctuation category

Mutation: change the category allowlist from `("L", "N")` to `("L", "N", "P")`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='abc-def')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='abc_def')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='abc.def')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='abc@example')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='mailto:owner@example.test')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 390, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='javascript:alert(1)')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 390, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='authorization:bearer-token')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 390, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='C:drive-relative')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 390, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.025s

FAILED (failures=8)
```

Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
----------------------------------------------------------------------
Ran 1 test in 0.019s

OK
```

### UIRM6 — allow combining-mark category

Mutation: change the category allowlist from `("L", "N")` to `("L", "M", "N")`.

```text
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='\\u034f\\u034f\\u034f')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='\\ufe0f\\ufe0f\\ufe0f')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='e\\u0301e')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 348, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.020s

FAILED (failures=3)
```

Restored command/output:

```text
sha256=6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917
py -3.11 -B -m unittest -q tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
----------------------------------------------------------------------
Ran 1 test in 0.019s

OK
```

## Final gates

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py
7 passed, 84 subtests passed

py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_codesign_contracts.py tests/test_workflow_router.py
68 passed, 216 subtests passed
Combined: 75 passed, 300 subtests passed

py -3.11 -B -m mypy --strict --no-incremental library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
Success: no issues found in 2 source files

py -3.11 -B -m compileall -q library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
exit 0

git diff --check
clean
```
