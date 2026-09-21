# CVQ-01B1 initial independent evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01B1-INITIAL` / `REVIEW_EVIDENCE` / `01` |
| Candidate / baseline | `1a1b6eb3af4c5a7e31de0d102eaf20b461c49f98` / `7171f41bdec15104fd653ecee6c8e06691055d16` |
| Authority | [B1](../../../modules/tickets/controlled-verification/cvq-01b1-namespace-import-admission.md) document03 / closure01 at6266cfcfb46956213b71042ec4035ae73a5442f6; LF b6fde644de900e054875d85488a610380efe9f01341c7037a78139023842280f |
| Reviewer / scope | root; AST-only, same lifetime, no provider/native/installation effect |
| Review worktree | C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01a2-review; detached exact candidate |

## Identity and bounded validation

Owner root .worktrees/cvq-01, branch codex/cvq-01 read back at the exact candidate, clean.
7171f41 is an ancestor; exactly the five B1 paths changed; git diff --check baseline..candidate
is clean. Accepted A/production files did not change. Root review worktree was clean before
detached checkout and after all checks. No source files were mutated: counter-mutations below
replace the real imported checker functions for the scope of unittest.mock.patch and restore
those exact function objects; identity assertions verify restoration. AST packets are never executed.
One foreground process at a time; each command below60sec; no stress/retry/background poll.

Strict command is the full21-file B1 section5 command, run directly without output filter:

```text
Success: no issues found in 21 source files
```

Focused command:

```powershell
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains tests.test_verification_qualification_boundaries
```

Unreduced output (exit0):

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
test_architecture_dependency_gate (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_architecture_dependency_gate) ... ok
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok
test_source_negative_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_negative_corpus) ... ok
test_source_positive_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_positive_corpus) ... ok
test_source_result_is_deterministic (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_result_is_deterministic) ... ok
test_source_set_and_parse_fail_closed (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_set_and_parse_fail_closed) ... ok

----------------------------------------------------------------------
Ran 44 tests in 16.464s

OK
```

## Independent namespace and boundary probes

Run in the root detached review worktree at the exact candidate; Python3.11.9, `-B`.

```powershell
@'
import ast
import unittest
import sys
sys.path.insert(0, "tests")
from verification_qualification_source_corpus import MINIMUM_PACKET, POSITIVE_ROWS, replace_unit
from verification_qualification_source_gate import inspect_sources
from verification_qualification_source_policy import SourceModule as M, SourceRule as R, SourceUnit
from verification_qualification_source_symbols import export_origins, ResolutionStatus

def packet(*parts):
    units = MINIMUM_PACKET
    for mod, text in parts:
        units = replace_unit(units, SourceUnit(mod, text))
    return units

definition = "from enum import Enum\nclass CapabilityFamily(str, Enum):\n    PLAN_BINDING = 'PLAN_BINDING'\n"

class ReviewNamespaces(unittest.TestCase):
    def test_normalized_parent_relative_allowed(self):
        units = packet((M.QUALIFICATION_VALUES, definition),
                       (M.BINDING_CONTRACTS, "from ..controlled_verification.qualification_values import CapabilityFamily\n"))
        self.assertEqual((), inspect_sources(units))
    def test_normalized_parent_relative_cycle(self):
        units = packet((M.QUALIFICATION_VALUES, "from ..controlled_verification.binding_contracts import name\n"),
                       (M.BINDING_CONTRACTS, "from ..controlled_verification.qualification_values import name\n"))
        self.assertIn(R.SG08, tuple(item.rule for item in inspect_sources(units)))
    def test_single_statement_later_missing_symbol(self):
        units = packet((M.QUALIFICATION_VALUES, definition),
                       (M.BINDING_CONTRACTS, "from .qualification_values import CapabilityFamily, Missing\n"))
        self.assertIn((M.BINDING_CONTRACTS, 1, 0, R.SG01),
                      tuple((x.module,x.line,x.column,x.rule) for x in inspect_sources(units)))
    def test_complete_ambiguous_facade_rejects(self):
        units = packet((M.QUALIFICATION_VALUES, "value: int = 1\n"),
                       (M.BINDING_CONTRACTS, "value: int = 2\n"),
                       (M.QUALIFICATION_CONTRACTS, "from .qualification_values import value\nfrom .binding_contracts import value\n"))
        self.assertIn(R.SG06, tuple(item.rule for item in inspect_sources(units)))
    def test_nested_local_is_not_export(self):
        trees = {"qualification_values": ast.parse("def helper(value: object) -> object:\n    from typing import Mapping\n    return value\n")}
        self.assertNotIn("Mapping", export_origins(trees)["qualification_values"])
    def test_positive_facade_is_input_order_independent(self):
        units = POSITIVE_ROWS[0].units
        self.assertEqual((), inspect_sources(tuple(reversed(units))))

unittest.main(verbosity=2)

'@ | & 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -
```

Unreduced command output:

```text
test_complete_ambiguous_facade_rejects (__main__.ReviewNamespaces.test_complete_ambiguous_facade_rejects) ... FAIL
test_nested_local_is_not_export (__main__.ReviewNamespaces.test_nested_local_is_not_export) ... ok
test_normalized_parent_relative_allowed (__main__.ReviewNamespaces.test_normalized_parent_relative_allowed) ... FAIL
test_normalized_parent_relative_cycle (__main__.ReviewNamespaces.test_normalized_parent_relative_cycle) ... FAIL
test_positive_facade_is_input_order_independent (__main__.ReviewNamespaces.test_positive_facade_is_input_order_independent) ... ok
test_single_statement_later_missing_symbol (__main__.ReviewNamespaces.test_single_statement_later_missing_symbol) ... ok

======================================================================
FAIL: test_complete_ambiguous_facade_rejects (__main__.ReviewNamespaces.test_complete_ambiguous_facade_rejects)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 36, in test_complete_ambiguous_facade_rejects
AssertionError: <SourceRule.SG06: 'SG06'> not found in ()

======================================================================
FAIL: test_normalized_parent_relative_allowed (__main__.ReviewNamespaces.test_normalized_parent_relative_allowed)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 22, in test_normalized_parent_relative_allowed
AssertionError: Tuples differ: () != (SourceViolation(module=<SourceModule.BIND[86 chars]'>),)

Second tuple contains 1 additional elements.
First extra element 0:
SourceViolation(module=<SourceModule.BINDING_CONTRACTS: 'binding_contracts.py'>, line=1, column=0, rule=<SourceRule.SG01: 'SG01'>)

- ()
+ (SourceViolation(module=<SourceModule.BINDING_CONTRACTS: 'binding_contracts.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG01: 'SG01'>),)

======================================================================
FAIL: test_normalized_parent_relative_cycle (__main__.ReviewNamespaces.test_normalized_parent_relative_cycle)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 26, in test_normalized_parent_relative_cycle
AssertionError: <SourceRule.SG08: 'SG08'> not found in (<SourceRule.SG01: 'SG01'>, <SourceRule.SG01: 'SG01'>)

----------------------------------------------------------------------
Ran 6 tests in 0.021s

FAILED (failures=3)

```

Result: six collect; three fail for named expected behavior, three pass. Complete ambiguous
facade returns no findings; normalized legal parent-relative import wrongly rejects; normalized
parent-relative cycle has no SG08. These are B1-I01/I06/I08 and section2, not B2/B3 work.

## Allowed re-export path probes

Run in the root detached review worktree at the exact candidate; Python3.11.9, `-B`.

```powershell
@'
import sys, unittest
sys.path.insert(0, "tests")
from verification_qualification_source_corpus import MINIMUM_PACKET, replace_unit
from verification_qualification_source_gate import inspect_sources
from verification_qualification_source_policy import SourceModule as M, SourceRule as R, SourceUnit
parts = (
(M.QUALIFICATION_VALUES, "from enum import Enum\nclass CapabilityFamily(str, Enum):\n    PLAN_BINDING = 'PLAN_BINDING'\n"),
(M.BINDING_CONTRACTS, "from .qualification_values import CapabilityFamily\n"),
(M.MANIFEST_CONTRACTS, "from .binding_contracts import CapabilityFamily\n"),
(M.QUALIFICATION_PORTS, "from .manifest_contracts import CapabilityFamily\n"),
(M.QUALIFICATION_CONTRACTS, "from .qualification_ports import CapabilityFamily\n__all__ = ('CapabilityFamily',)\n"),
(M.INIT, "from .qualification_contracts import CapabilityFamily\n__all__ = ('CapabilityFamily',)\n"),
)
units = MINIMUM_PACKET
for module,text in parts:
    units = replace_unit(units, SourceUnit(module,text))
class ReviewExportPaths(unittest.TestCase):
    def test_allowed_multihop_reexport(self):
        self.assertEqual((), inspect_sources(units))
    def test_allowed_multihop_reexport_reverse_input(self):
        self.assertEqual((), inspect_sources(tuple(reversed(units))))
unittest.main(verbosity=2)

'@ | & 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -
```

Unreduced command output:

```text
test_allowed_multihop_reexport (__main__.ReviewExportPaths.test_allowed_multihop_reexport) ... FAIL
test_allowed_multihop_reexport_reverse_input (__main__.ReviewExportPaths.test_allowed_multihop_reexport_reverse_input) ... FAIL

======================================================================
FAIL: test_allowed_multihop_reexport (__main__.ReviewExportPaths.test_allowed_multihop_reexport)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 19, in test_allowed_multihop_reexport
AssertionError: Tuples differ: () != (SourceViolation(module=<SourceModule.INIT[64 chars]'>),)

Second tuple contains 1 additional elements.
First extra element 0:
SourceViolation(module=<SourceModule.INIT: '__init__.py'>, line=1, column=0, rule=<SourceRule.SG06: 'SG06'>)

- ()
+ (SourceViolation(module=<SourceModule.INIT: '__init__.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG06: 'SG06'>),)

======================================================================
FAIL: test_allowed_multihop_reexport_reverse_input (__main__.ReviewExportPaths.test_allowed_multihop_reexport_reverse_input)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 21, in test_allowed_multihop_reexport_reverse_input
AssertionError: Tuples differ: () != (SourceViolation(module=<SourceModule.INIT[343 chars]1'>))

Second tuple contains 3 additional elements.
First extra element 0:
SourceViolation(module=<SourceModule.INIT: '__init__.py'>, line=1, column=0, rule=<SourceRule.SG06: 'SG06'>)

- ()
+ (SourceViolation(module=<SourceModule.INIT: '__init__.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG06: 'SG06'>),
+  SourceViolation(module=<SourceModule.QUALIFICATION_CONTRACTS: 'qualification_contracts.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG06: 'SG06'>),
+  SourceViolation(module=<SourceModule.QUALIFICATION_PORTS: 'qualification_ports.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG01: 'SG01'>))

----------------------------------------------------------------------
Ran 2 tests in 0.008s

FAILED (failures=2)

```

Result: both fail. Every direct edge is explicitly allowed in B1's DAG. A transient UNKNOWN
from one resolver iteration becomes permanent AMBIGUOUS when the same import later resolves;
this is not competing declarations. A legal path is rejected, and input permutation changes
findings. This violates section2/B1-I06/POS/SET, not a new external import allowance.

## Root counter-mutations and exact restoration

Run in the root detached review worktree at the exact candidate; Python3.11.9, `-B`.

```powershell
@'
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, "tests")
import verification_qualification_source_symbols as symbols
import verification_qualification_source_gate as gate
from tests.test_verification_qualification_boundaries import QualificationBoundaryTests

original_target = symbols._relative_target
def prefix_target(node, name):
    target = original_target(node, name)
    return target.split(".", 1)[0] if target is not None else None

original_bindings = gate.resolve_import_bindings
def first_entry_only(*args, **kwargs):
    seen = set()
    result = []
    for binding in original_bindings(*args, **kwargs):
        if id(binding.node) not in seen:
            seen.add(id(binding.node))
            result.append(binding)
    return tuple(result)

def run(label):
    print(label, flush=True)
    return unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([QualificationBoundaryTests("test_source_namespace_admission")]))

with patch.object(symbols, "_relative_target", prefix_target):
    suffix = run("MUTATION exact-target -> prefix-target")
suffix_restore = run("RESTORE exact-target")
original_check = gate._check_imports
def first_entry_check(*args, **kwargs):
    with patch.object(gate, "resolve_import_bindings", first_entry_only):
        return original_check(*args, **kwargs)
with patch.object(gate, "_check_imports", first_entry_check):
    later = run("MUTATION import-admission -> first entry of each statement")
later_restore = run("RESTORE all entries")
print("suffix_mutant_success", suffix.wasSuccessful(),
      "suffix_restore_success", suffix_restore.wasSuccessful(),
      "later_entry_mutant_success", later.wasSuccessful(),
      "later_entry_restore_success", later_restore.wasSuccessful(), flush=True)
assert symbols._relative_target is original_target
assert gate._check_imports is original_check
assert gate.resolve_import_bindings is original_bindings
assert suffix_restore.wasSuccessful() and later_restore.wasSuccessful()
if suffix.wasSuccessful() or later.wasSuccessful():
    raise SystemExit(2)

'@ | & 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -
```

Unreduced command output:

```text
MUTATION exact-target -> prefix-target
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... FAIL

======================================================================
FAIL: test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_boundaries.py", line 102, in test_source_namespace_admission
    self.assertIn(SourceRule.SG01, tuple(finding.rule for finding in suffix_findings), suffix_findings)
AssertionError: <SourceRule.SG01: 'SG01'> not found in () : ()

----------------------------------------------------------------------
Ran 1 test in 2.659s

FAILED (failures=1)
RESTORE exact-target
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

----------------------------------------------------------------------
Ran 1 test in 2.568s

OK
MUTATION import-admission -> first entry of each statement
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok
RESTORE all entries

----------------------------------------------------------------------
Ran 1 test in 2.526s

OK
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

----------------------------------------------------------------------
Ran 1 test in 2.606s

OK
suffix_mutant_success False suffix_restore_success True later_entry_mutant_success True later_entry_restore_success True

```

Result: prefix mutation produces the expected named SG01 suffix red; restored green.
The separate first-entry-only import-admission mutation produces ZERO RED; restored green.
This independent door is a finding, not a pass. The existing later-entry row has two statements,
not two aliases within one import statement, so it does not pin the per-entry guard.
The process exits nonzero for this missing sensitivity; it is not collection/import failure.
No source file modification or history rewrite occurred.

## Corpus/source audit

NAMESPACE_ROWS uses the otherwise-empty MINIMUM_PACKET. Its direct/renamed forbidden rows
reference QualificationReport without defining it. The supposed complete ambiguity row likewise
never defines QualificationModel/QualificationReport; its SG06 is missing-symbol rejection, not
proven ambiguity. Genuine complete ambiguity above passes. Re-export alias/indirect rows point
to qualification_admission.evaluate, which is outside the exact nine-module set, so they do not
exercise a fully resolved forbidden constituent. Section3 explicitly requires complete unrelated
prerequisites. Symbols excludes local imports from module exports by tree.body; the independent
local export probe passes, but the committed B1 method has no direct assertion pinning that fact.

Helper evidence and root adjudication are in the linked initial review. This leaf records observed
facts, not approval. Full SG01–20 final campaign remains reserved for B3; no prior A campaign rerun.


## Nested-scope cycle sensitivity

Helper's static nested-cycle coverage finding was independently checked by root. The real
checker detects a cycle through an unused typed function, but removing nested graph edges does
not turn the committed B1 method red. This is an evidence gap, not a claim that the current
cycle walker already accepts nested cycles.

```powershell
@'
import ast, sys, unittest
from unittest.mock import patch
sys.path.insert(0, "tests")
import verification_qualification_source_gate as gate
from verification_qualification_source_corpus import MINIMUM_PACKET, replace_unit
from verification_qualification_source_policy import SourceModule as M, SourceRule as R, SourceUnit
from verification_qualification_source_symbols import import_target_for_alias
from tests.test_verification_qualification_boundaries import QualificationBoundaryTests

units = replace_unit(MINIMUM_PACKET, SourceUnit(M.QUALIFICATION_VALUES,
    "def helper(value: object) -> object:\n    from .binding_contracts import helper\n    return value\n"))
units = replace_unit(units, SourceUnit(M.BINDING_CONTRACTS,
    "from .qualification_values import helper\n"))
assert any(x.rule is R.SG08 for x in gate.inspect_sources(units))
print("CONTROL nested unused-function cycle SG08 present", flush=True)

original_edges = gate.module_edges
def top_level_edges(packet):
    available = {unit.module.stem for unit in packet}
    edges = []
    for unit in packet:
        try:
            tree = ast.parse(unit.text)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    target = import_target_for_alias(node, alias.name)
                    if target in available:
                        edges.append((unit.module.stem, target))
    return tuple(edges)
def run(label):
    print(label, flush=True)
    return unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([QualificationBoundaryTests("test_source_namespace_admission")]))
with patch.object(gate, "module_edges", top_level_edges):
    assert not any(x.rule is R.SG08 for x in gate.inspect_sources(units))
    mutant = run("MUTATION module cycle graph -> top-level imports only")
restored = run("RESTORE all scopes")
assert gate.module_edges is original_edges
print("mutant_success", mutant.wasSuccessful(), "restore_success", restored.wasSuccessful(), flush=True)
assert restored.wasSuccessful()
raise SystemExit(2 if mutant.wasSuccessful() else 0)

'@ | & 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -
```

Unreduced output:

```text
CONTROL nested unused-function cycle SG08 present
MUTATION module cycle graph -> top-level imports only
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

----------------------------------------------------------------------
Ran 1 test in 2.896s

OK
RESTORE all scopes
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

----------------------------------------------------------------------
Ran 1 test in 3.149s

OK
mutant_success True restore_success True
```
