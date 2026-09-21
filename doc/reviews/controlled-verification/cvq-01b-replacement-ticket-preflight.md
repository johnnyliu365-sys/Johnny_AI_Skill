# CVQ-01B replacement ticket preflight

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B-REPLACEMENT-PREFLIGHT` / `CODE_REVIEW` / `01` |
| State / scope | `PROPOSAL_SELF_REVIEW_COMPLETE / BOUNDED_HELPER_PENDING / NOT_DISPATCHABLE`; docs-only, not source approval |
| Authority | Owner approved convergence01 at797c15db0bcb39d1e015bb676f1722a9e138a6e7, LF0308388788c4a6a6c79ce4dd256b72bb5a231a498357a0038f305680e46f0f94 |
| Proposal objects | B1/B2/B3 document01/closure01 in this commit; exact LF digests are their direct ticket registry edges |
| Root / effect scope | Root sole conclusion owner; local read-only diagnosis plus scoped docs writes, NO_EXTERNAL_EFFECT |

## 1. Responsibility and authority preflight

Reviewed exact existing B06, code-review02, SPEC07 section11.3, wire03, sealed Context02,
current bundled profile01 and failed source7171f41. All upstream LF pins match. Main remains
b697738d009db37318ebc8762107ef8329e014db, clean; control branch before this action is797c15db.
Original B closure01 remains exhausted and unchanged. No mutation of shared Context, SPEC,
main, source worktree/candidate, installed plugin, authority remote or publication.

| Check | Result and bound limitation |
| --- | --- |
| Vertical closure | B1 import fact/admission; B2 call/receiver admission; B3 context grammar/final composition. Each includes owned tests, baseline and proof |
| Shared ownership | Same sequential implementation owner; five existing test/support owners; no new broad framework, extra lane or tests-later |
| P0 typing | B1 closes the existing unrestricted status/kind strings; later tickets preserve finite variants and immutable fixed seam |
| Known defects | B-F01/05 -> B1; B-F02 and call-alternative B-F04 -> B2; B-F03 and remaining B-F04 -> B3 |
| Full old coverage | SG01–08 B1; SG09–13/16–18 B2; SG19 recursion B2, other SG19 B3; SG14/15/20 B3. Six positive IDs retained |
| Resource/evidence | Existing one-process60s/command1200s/pass bounds retained; exact combined20-rule campaign only at final B3; accepted A campaigns not rerun |
| Runtime effects | None; packet parsing only, not Python sandbox/purity or host capability proof |
| Source-content | Reference forbids prompts/work-order prose in source/tests; this docs proposal creates no executable checker or hard-enforcement claim |
| Dependency admission | B1 seed7171f41 is explicitly unapproved; B2/B3 require future exact accepted SHA+review/index; no invented placeholder pass |
| Owner boundary | Decomposition approved, exact new closures pending. No implementation dispatch, third correction, merge, push or installation |

## 2. Baseline-red collectability, independently executed

On2026-09-21 root used detached review worktree `.worktrees/cvq-01a2-review`.
Readback HEAD7171f41bdec15104fd653ecee6c8e06691055d16, clean.
The command below reads nine production texts, forms five AST-only modified packets in memory,
and invokes the already-existing inspect_sources seam. It does not alter files or source guards.
No output reducer, source exec/import of packets, stress or retry. The analyzer/test support
itself is imported normally. All six named tests collect; five fail at the intended missing
finding and the original-package control passes. Thus this is not a missing-module/type red.

This is the concrete7171f41 starting evidence, not the unknown future B1/B2 acceptance SHA.
B2/B3 must rerun their test-only baseline assertions on that actual bound dependency. Already
green cases retain honest green and get a reverse mutation; no fabricated chronology.

Exact PowerShell command (Python -B suppresses bytecode writes):

```powershell
$cvqProbe = @'
import sys, unittest
from pathlib import Path
root = Path(r"C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review")
sys.path.insert(0, str(root / "tests"))
from verification_qualification_source_policy import SourceModule, SourceRule, SourceUnit
from verification_qualification_source_gate import inspect_sources
units = tuple(SourceUnit(m, (root / "library/controlled_verification" / m.value).read_text(encoding="utf-8")) for m in SourceModule)
def packet(module, extra):
    return tuple(SourceUnit(u.module, u.text + "\n" + extra) if u.module is module else u for u in units)
class ReplacementBaselineTests(unittest.TestCase):
    def test_control(self):
        self.assertEqual((), inspect_sources(units))
    def test_b1_exact_module_suffix(self):
        findings = inspect_sources(packet(SourceModule.BINDING_CONTRACTS, "from .qualification_values.not_a_module import QualificationModel as ResolvedAlias\n"))
        self.assertIn(SourceRule.SG01, tuple(x.rule for x in findings), findings)
    def test_b2_known_schema_port(self):
        findings = inspect_sources(packet(SourceModule.QUALIFICATION_PORTS, "def schema_port_invocation(port: EvidenceObservationPort, request: EvidenceObservationRequest) -> EvidenceResolution:\n    return port.resolve(request)\n"))
        self.assertIn(SourceRule.SG18, tuple(x.rule for x in findings), findings)
    def test_b3_module_self_annotation(self):
        findings = inspect_sources(packet(SourceModule.QUALIFICATION_VALUES, "def helper(self) -> object:\n    return self\n"))
        self.assertIn(SourceRule.SG19, tuple(x.rule for x in findings), findings)
    def test_b3_delete_attribute(self):
        findings = inspect_sources(packet(SourceModule.QUALIFICATION_VALUES, "def helper(value: object) -> None:\n    del value.field\n"))
        self.assertIn(SourceRule.UNSUPPORTED_SYNTAX, tuple(x.rule for x in findings), findings)
    def test_b3_module_for(self):
        findings = inspect_sources(packet(SourceModule.QUALIFICATION_VALUES, "for value in ():\n    pass\n"))
        self.assertIn(SourceRule.UNSUPPORTED_SYNTAX, tuple(x.rule for x in findings), findings)
unittest.main(verbosity=2)
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqProbe
```

Full process output; exit1 is the expected defect reproduction, not ticket completion:

```text
7171f41bdec15104fd653ecee6c8e06691055d16
test_b1_exact_module_suffix (__main__.ReplacementBaselineTests.test_b1_exact_module_suffix) ... FAIL
test_b2_known_schema_port (__main__.ReplacementBaselineTests.test_b2_known_schema_port) ... FAIL
test_b3_delete_attribute (__main__.ReplacementBaselineTests.test_b3_delete_attribute) ... FAIL
test_b3_module_for (__main__.ReplacementBaselineTests.test_b3_module_for) ... FAIL
test_b3_module_self_annotation (__main__.ReplacementBaselineTests.test_b3_module_self_annotation) ... FAIL
test_control (__main__.ReplacementBaselineTests.test_control) ... ok

======================================================================
FAIL: test_b1_exact_module_suffix (__main__.ReplacementBaselineTests.test_b1_exact_module_suffix)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 15, in test_b1_exact_module_suffix
AssertionError: <SourceRule.SG01: 'SG01'> not found in () : ()

======================================================================
FAIL: test_b2_known_schema_port (__main__.ReplacementBaselineTests.test_b2_known_schema_port)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 18, in test_b2_known_schema_port
AssertionError: <SourceRule.SG18: 'SG18'> not found in () : ()

======================================================================
FAIL: test_b3_delete_attribute (__main__.ReplacementBaselineTests.test_b3_delete_attribute)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 24, in test_b3_delete_attribute
AssertionError: <SourceRule.UNSUPPORTED_SYNTAX: 'UNSUPPORTED_SYNTAX'> not found in () : ()

======================================================================
FAIL: test_b3_module_for (__main__.ReplacementBaselineTests.test_b3_module_for)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 27, in test_b3_module_for
AssertionError: <SourceRule.UNSUPPORTED_SYNTAX: 'UNSUPPORTED_SYNTAX'> not found in () : ()

======================================================================
FAIL: test_b3_module_self_annotation (__main__.ReplacementBaselineTests.test_b3_module_self_annotation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 21, in test_b3_module_self_annotation
AssertionError: <SourceRule.SG19: 'SG19'> not found in () : ()

----------------------------------------------------------------------
Ran 6 tests in 13.342s

FAILED (failures=5)
```

The replacement production test methods will be test_source_namespace_admission,
test_source_call_admission and test_source_statement_admission in the existing driver.
Their baseline-facing packet assertions use this existing seam; tests of newly introduced enum
types are added only with those types, not misreported as baseline-red collection evidence.

## 3. Proposal audit disposition

A bounded read-only audit of the committed replacement proposals is pending; it will compare
their frozen semantics, scope and proof obligations with the approved decomposition/SPEC and
the observed existing seams. This is a control-plane proposal audit, not an implementation
review on unapproved ticket closures. No source run, mutation or repeated progress polling is
requested from the helper. Root will independently check its findings before requesting one
exact owner approval of the set. Until then, no source admission or helper verdict is claimed.
