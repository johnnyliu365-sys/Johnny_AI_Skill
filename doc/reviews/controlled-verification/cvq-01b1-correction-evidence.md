# CVQ-01B1 correction evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01B1-CORRECTION` / `REVIEW_EVIDENCE` / `01` |
| Candidate / correction baseline | 8dc22904921cb6b0c56a88d7e224ca66828f8c14 / 1a1b6eb3af4c5a7e31de0d102eaf20b461c49f98 |
| Authority | B1 document04/closure01 at596dc08ed1d3fcac898b1536360854355cf2e623, LF ec19bfe0eaf9d161e6fb99079b95fa6bc9e41d2f6b1c169f2c461eefa51cb6bd |
| Root review tree | .worktrees/cvq-01a2-review; detached exact candidate, clean before/after |
| Scope | Root-owned AST probes and temporary imported-function mutations; no source writes, native/provider/push/installation effects |

## Identity and controls

Owner .worktrees/cvq-01/codex/cvq-01 read back clean at8dc2290; initial1a1b6eb is an ancestor.
Four existing allowlisted files changed, no production/A/policy/catalog changes. Both candidate
range and worktree diff checks clean. One foreground process per command, every command below60sec;
no automatic retry, stress or poll. Restorations assert original function identity; files unchanged.

Commands/scripts below execute in the root review tree with Python3.11.9 -B.
For the initial namespace/path/mutation scripts, the exact reusable command text is in
[initial evidence01](cvq-01b1-initial-evidence.md) at596dc08, LF
af6db4e889b7099d175552c9f73568419d4e041f5125d313bc4447edac7b1cdd.
They were rerun unchanged against8dc2290, not inferred from earlier green results.

## Strict and focused regression

Full B1 section5 strict command output (exit0):

```text
Success: no issues found in 21 source files
```

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
Ran 44 tests in 16.982s

OK
```

## Prior namespace and allowed-path failures rerun

Same initial-evidence namespace script (exit0):

```text
test_complete_ambiguous_facade_rejects (__main__.ReviewNamespaces.test_complete_ambiguous_facade_rejects) ... ok
test_nested_local_is_not_export (__main__.ReviewNamespaces.test_nested_local_is_not_export) ... ok
test_normalized_parent_relative_allowed (__main__.ReviewNamespaces.test_normalized_parent_relative_allowed) ... ok
test_normalized_parent_relative_cycle (__main__.ReviewNamespaces.test_normalized_parent_relative_cycle) ... ok
test_positive_facade_is_input_order_independent (__main__.ReviewNamespaces.test_positive_facade_is_input_order_independent) ... ok
test_single_statement_later_missing_symbol (__main__.ReviewNamespaces.test_single_statement_later_missing_symbol) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.016s

OK
```

Same initial-evidence legal re-export path script (exit0):

```text
test_allowed_multihop_reexport (__main__.ReviewExportPaths.test_allowed_multihop_reexport) ... ok
test_allowed_multihop_reexport_reverse_input (__main__.ReviewExportPaths.test_allowed_multihop_reexport_reverse_input) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.012s

OK
```

The exact prior ambiguity and transient-resolution implementation defects are fixed in these
named probes; eight assertions now pass. That does not discharge unexecuted normalization forms.

## Counter-mutations and restore

Same initial-evidence suffix and first-entry script, unreduced output:

```text
MUTATION exact-target -> prefix-target
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... FAIL
RESTORE exact-target

======================================================================
FAIL: test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_boundaries.py", line 104, in test_source_namespace_admission
    self.assertIn(SourceRule.SG01, tuple(finding.rule for finding in suffix_findings), suffix_findings)
AssertionError: <SourceRule.SG01: 'SG01'> not found in () : ()

----------------------------------------------------------------------
Ran 1 test in 2.578s

FAILED (failures=1)
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok
MUTATION import-admission -> first entry of each statement

----------------------------------------------------------------------
Ran 1 test in 2.460s

OK
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

----------------------------------------------------------------------
Ran 1 test in 2.527s

OK
RESTORE all entries
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok

suffix_mutant_success False suffix_restore_success True later_entry_mutant_success True later_entry_restore_success True
----------------------------------------------------------------------
Ran 1 test in 2.497s

OK
```

Suffix red/restored-green remains valid. First-entry-only mutation still yields ZERO RED;
the command exits nonzero to record that failure. The returned implementer evidence
"B1-I03-first-entry-removed []" removed the second whole statement, not later aliases within
one statement; it is not the same property.

Same nested-cycle script, unreduced output (exit0):

```text
CONTROL nested unused-function cycle SG08 present
MUTATION module cycle graph -> top-level imports only
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... 
  test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) (row='SG08-unused-nested-cycle') ... FAIL

======================================================================
FAIL: test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) (row='SG08-unused-nested-cycle')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\cvq-01a2-review\tests\test_verification_qualification_boundaries.py", line 142, in test_source_namespace_admission
    self.assertIn(
AssertionError: (<SourceModule.BINDING_CONTRACTS: 'binding_contracts.py'>, 7, 4) not found in []

----------------------------------------------------------------------
Ran 1 test in 2.730s

FAILED (failures=1)
RESTORE all scopes
test_source_namespace_admission (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_namespace_admission) ... ok
mutant_success False restore_success True

----------------------------------------------------------------------
Ran 1 test in 2.743s

OK
```

The new SG08-unused-nested-cycle assertion now correctly fails under the graph weakening;
restore is green. That portion of B1-F04 is closed.

## Additional exact-form probes

These are the same frozen section2/B1-I01/I03 normalization obligation, not a new dependency.
Root omitted these equivalent package forms from the first batch and records that review gap.
An unqualified external __future__ special-case also admits a relative internal spelling that
cannot resolve in the exact nine-module namespace. This is not execution of that source.

```powershell
@'
import sys, unittest
sys.path.insert(0, "tests")
from verification_qualification_source_corpus import MINIMUM_PACKET, replace_unit
from verification_qualification_source_gate import inspect_sources
from verification_qualification_source_policy import SourceModule as M, SourceUnit

class ReviewExactModuleForms(unittest.TestCase):
    def test_relative_future_is_not_external_future(self):
        units = replace_unit(MINIMUM_PACKET, SourceUnit(M.BINDING_CONTRACTS,
            "from .__future__ import annotations\n"))
        self.assertNotEqual((), inspect_sources(units))
    def test_parent_relative_package_alias_matches_direct_form(self):
        direct = replace_unit(MINIMUM_PACKET, SourceUnit(M.BINDING_CONTRACTS,
            "from . import qualification_values as values\n"))
        normalized = replace_unit(MINIMUM_PACKET, SourceUnit(M.BINDING_CONTRACTS,
            "from ..controlled_verification import qualification_values as values\n"))
        self.assertEqual((), inspect_sources(direct))
        self.assertEqual(inspect_sources(direct), inspect_sources(normalized))
    def test_absolute_package_alias_matches_direct_form(self):
        direct = replace_unit(MINIMUM_PACKET, SourceUnit(M.BINDING_CONTRACTS,
            "from . import qualification_values as values\n"))
        absolute = replace_unit(MINIMUM_PACKET, SourceUnit(M.BINDING_CONTRACTS,
            "from library.controlled_verification import qualification_values as values\n"))
        self.assertEqual((), inspect_sources(direct))
        self.assertEqual(inspect_sources(direct), inspect_sources(absolute))
unittest.main(verbosity=2)

'@ | & 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -
```

Unreduced output (exit1):

```text
test_absolute_package_alias_matches_direct_form (__main__.ReviewExactModuleForms.test_absolute_package_alias_matches_direct_form) ... FAIL
test_parent_relative_package_alias_matches_direct_form (__main__.ReviewExactModuleForms.test_parent_relative_package_alias_matches_direct_form) ... FAIL
test_relative_future_is_not_external_future (__main__.ReviewExactModuleForms.test_relative_future_is_not_external_future) ... FAIL

======================================================================
FAIL: test_absolute_package_alias_matches_direct_form (__main__.ReviewExactModuleForms.test_absolute_package_alias_matches_direct_form)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 25, in test_absolute_package_alias_matches_direct_form
AssertionError: Tuples differ: () != (SourceViolation(module=<SourceModule.BIND[86 chars]'>),)

Second tuple contains 1 additional elements.
First extra element 0:
SourceViolation(module=<SourceModule.BINDING_CONTRACTS: 'binding_contracts.py'>, line=1, column=0, rule=<SourceRule.SG09: 'SG09'>)

- ()
+ (SourceViolation(module=<SourceModule.BINDING_CONTRACTS: 'binding_contracts.py'>,
+                  line=1,
+                  column=0,
+                  rule=<SourceRule.SG09: 'SG09'>),)

======================================================================
FAIL: test_parent_relative_package_alias_matches_direct_form (__main__.ReviewExactModuleForms.test_parent_relative_package_alias_matches_direct_form)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 18, in test_parent_relative_package_alias_matches_direct_form
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
FAIL: test_relative_future_is_not_external_future (__main__.ReviewExactModuleForms.test_relative_future_is_not_external_future)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<stdin>", line 11, in test_relative_future_is_not_external_future
AssertionError: () == ()

----------------------------------------------------------------------
Ran 3 tests in 0.019s

FAILED (failures=3)
```

Result: three collected/named assertion failures. Direct package form is accepted, equivalent
parent/absolute forms are rejected, and relative __future__ yields no finding. No real import,
source execution, file mutation or external effect occurred.

## Remaining corpus observation

The correction's B1-I03-later-forbidden-entry still has two separate statements, so its changed
prerequisite definitions do not close the tested first-alias bypass sensitivity.
Direct forbidden/renamed/absolute rows still call _row over empty referenced modules.
The new indirect-forbidden-reexport fixture links contracts and init back to one another,
without either defining/exporting the final CapabilityFamily; it now tests a cycle/unknown
origin, not the required resolved origin chain. A symbol defined in a disconnected values unit
is not a definition reachable by that import path. These are residual B1-F04 issues.

Final conclusion/helper adjudication is in review02. No full20-rule B3 campaign or accepted-A
mutation repetition was triggered on this failing intermediate candidate.
