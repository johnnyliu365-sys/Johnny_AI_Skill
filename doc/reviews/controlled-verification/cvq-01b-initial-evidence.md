# CVQ-01B | Initial review execution evidence

| Field | Value |
| --- | --- |
| ID / kind / revision | `EVIDENCE-CVQ-01B-INITIAL` / `REVIEW_EVIDENCE` / `01` |
| Candidate / baseline | `704f066c881dc36e7176d8564edadd439a443a09` / `485d882f578f84dac1c975b32ced2a4ae6e7d43a` |
| Ticket binding | CVQ-01B document05 / closure01 at b96aaaa6e385dc518389fc680cabbcf7251b01b2; LF 01530c75d2525ea86cabc018ea8808afa836f52bdfb5ca4b121530055d6e5093 |
| Executor / scope | root; clean detached `.worktrees/cvq-01a2-review`; foreground, no new dependency, background workload, native/provider/target effect or source fixture execution |
| Interpretation | Green declared suite is not admission: all fifteen forbidden packets produce empty findings; removing the negative or positive corpus leaves its test green. Historical baseline fails all three named assertions as genuine assertion failures, not missing-module errors. |

Commands and outputs below are unfiltered. AST packets are strings inspected by the gate, never executed. The access-only historical harness compiles the immutable repository's existing checker definitions, not a fixture; it retains the checker's AST without changing its predicates. It is a retrospective reproduction conducted by root after the owner reported NOT_CAPTURED, not evidence of the implementer's first-red chronology. In-memory corpus substitutions are restored by patch context exits; no source file was written. The full final rule-owner campaign remains NOT_VERIFIED pending correction; these experiments do not claim it completed.

## Declared strict and focused checks

```powershell
$checks = @'
import subprocess,sys,json
checks=json.loads("[[\"-B\",\"-m\",\"mypy\",\"--strict\",\"--follow-imports=silent\",\"library/controlled_verification\",\"tests/test_verification_qualification_contracts.py\",\"tests/test_verification_qualification_domains.py\",\"tests/test_verification_qualification_scalars.py\",\"tests/test_verification_qualification_manifests.py\",\"tests/test_verification_qualification_evidence.py\",\"tests/test_verification_qualification_boundaries.py\",\"tests/verification_qualification_fixtures.py\",\"tests/verification_qualification_catalog.py\",\"tests/verification_qualification_source_policy.py\",\"tests/verification_qualification_source_symbols.py\",\"tests/verification_qualification_source_gate.py\",\"tests/verification_qualification_source_corpus.py\"],[\"-B\",\"-m\",\"unittest\",\"-v\",\"tests.test_verification_qualification_contracts\",\"tests.test_verification_qualification_domains\",\"tests.test_verification_qualification_boundaries\"]]")
for args in checks:
 print("COMMAND "+json.dumps([sys.executable,*args]),flush=True)
 result=subprocess.run([sys.executable,*args],timeout=60,check=False)
 print("EXIT "+str(result.returncode),flush=True)
 if result.returncode:sys.exit(result.returncode)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $checks
git diff --check
```

Process exit 0; embedded HISTORICAL_EXIT 1 reports the baseline's three expected failures (the diagnostic process itself exits 0).

```text
COMMAND ["C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "-B", "-m", "mypy", "--strict", "--follow-imports=silent", "library/controlled_verification", "tests/test_verification_qualification_contracts.py", "tests/test_verification_qualification_domains.py", "tests/test_verification_qualification_scalars.py", "tests/test_verification_qualification_manifests.py", "tests/test_verification_qualification_evidence.py", "tests/test_verification_qualification_boundaries.py", "tests/verification_qualification_fixtures.py", "tests/verification_qualification_catalog.py", "tests/verification_qualification_source_policy.py", "tests/verification_qualification_source_symbols.py", "tests/verification_qualification_source_gate.py", "tests/verification_qualification_source_corpus.py"]
Success: no issues found in 21 source files
EXIT 0
COMMAND ["C:\\Users\\GameBoy\\AppData\\Local\\Programs\\Python\\Python311\\python.exe", "-B", "-m", "unittest", "-v", "tests.test_verification_qualification_contracts", "tests.test_verification_qualification_domains", "tests.test_verification_qualification_boundaries"]
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
test_source_negative_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_negative_corpus) ... ok
test_source_positive_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_positive_corpus) ... ok
test_source_result_is_deterministic (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_result_is_deterministic) ... ok
test_source_set_and_parse_fail_closed (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_set_and_parse_fail_closed) ... ok

----------------------------------------------------------------------
Ran 43 tests in 1.769s

OK
EXIT 0

```

## Fifteen AST-only forbidden packets

```powershell
$probe = @'
import json, sys
sys.path.insert(0, "tests")
from verification_qualification_source_policy import SourceModule as M, SourceUnit as U
from verification_qualification_source_gate import inspect_sources
cases = (
 ("B01-external-unlisted", M.QUALIFICATION_VALUES, "from pydantic import TypeAdapter\ndef helper() -> object:\n    return TypeAdapter(int)\n"),
 ("B02-parent-escape", M.BINDING_CONTRACTS, "from ..qualification_values import Arbitrary\n"),
 ("B03-second-import", M.BINDING_CONTRACTS, "from . import qualification_values, report_contracts\n"),
 ("B04-rebound-callee", M.QUALIFICATION_VALUES, "def helper() -> int:\n    return 1\ndef outer() -> int:\n    helper = 0\n    return helper()\n"),
 ("B05-same-line-receiver", M.QUALIFICATION_VALUES, "from typing import Mapping\ndef helper(value: object) -> object:\n    if isinstance(value, Mapping):\n        value = 0; return value.get('x')\n    return None\n"),
 ("B06-destructure-receiver", M.QUALIFICATION_VALUES, "from typing import Mapping\ndef helper(value: object) -> object:\n    if isinstance(value, Mapping):\n        value, other = (0, 1)\n        return value.get('x')\n    return None\n"),
 ("B07-shadowed-Mapping", M.QUALIFICATION_VALUES, "from typing import Mapping\ndef helper(value: object, Mapping: type) -> object:\n    if isinstance(value, Mapping):\n        return value.get('x')\n    return None\n"),
 ("B08-forged-Port", M.QUALIFICATION_VALUES, "def helper(value: FakePort) -> object:\n    return value.resolve('x')\n"),
 ("B09-schema-model-method", M.QUALIFICATION_VALUES, "from pydantic import BaseModel\nclass QualificationModel(BaseModel):\n    pass\ndef helper(value: object) -> object:\n    return QualificationModel.model_validate(value)\n"),
 ("B10-unlisted-class", M.QUALIFICATION_VALUES, "from pydantic import BaseModel\nclass Arbitrary(BaseModel):\n    pass\n"),
 ("B11-multiple-allowed-bases", M.QUALIFICATION_VALUES, "from pydantic import BaseModel\nfrom typing import Protocol\nclass Arbitrary(BaseModel, Protocol):\n    pass\n"),
 ("B12-init-hook", M.QUALIFICATION_VALUES, "from pydantic import BaseModel\nclass Arbitrary(BaseModel):\n    def __init__(self):\n        pass\n"),
 ("B13-nested-module-mutable", M.QUALIFICATION_VALUES, "if True:\n    values = []\n"),
 ("B14-top-level-while", M.QUALIFICATION_VALUES, "while True:\n    pass\n"),
 ("B15-unlisted-try", M.QUALIFICATION_VALUES, "def helper() -> int:\n    try:\n        return 1\n    except ValueError:\n        return 0\n"),
)
for name, module, source in cases:
 packet = tuple(U(item, source if item is module else "") for item in M)
 result = inspect_sources(packet)
 print(json.dumps({"case":name, "source":source,"findings":[(f.module.value,f.line,f.column,f.rule.value) for f in result]}, ensure_ascii=False))

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $probe
```

Process exit 0; embedded HISTORICAL_EXIT 1 reports the baseline's three expected failures (the diagnostic process itself exits 0).

```text
{"case": "B01-external-unlisted", "source": "from pydantic import TypeAdapter\ndef helper() -> object:\n    return TypeAdapter(int)\n", "findings": []}
{"case": "B02-parent-escape", "source": "from ..qualification_values import Arbitrary\n", "findings": []}
{"case": "B03-second-import", "source": "from . import qualification_values, report_contracts\n", "findings": []}
{"case": "B04-rebound-callee", "source": "def helper() -> int:\n    return 1\ndef outer() -> int:\n    helper = 0\n    return helper()\n", "findings": []}
{"case": "B05-same-line-receiver", "source": "from typing import Mapping\ndef helper(value: object) -> object:\n    if isinstance(value, Mapping):\n        value = 0; return value.get('x')\n    return None\n", "findings": []}
{"case": "B06-destructure-receiver", "source": "from typing import Mapping\ndef helper(value: object) -> object:\n    if isinstance(value, Mapping):\n        value, other = (0, 1)\n        return value.get('x')\n    return None\n", "findings": []}
{"case": "B07-shadowed-Mapping", "source": "from typing import Mapping\ndef helper(value: object, Mapping: type) -> object:\n    if isinstance(value, Mapping):\n        return value.get('x')\n    return None\n", "findings": []}
{"case": "B08-forged-Port", "source": "def helper(value: FakePort) -> object:\n    return value.resolve('x')\n", "findings": []}
{"case": "B09-schema-model-method", "source": "from pydantic import BaseModel\nclass QualificationModel(BaseModel):\n    pass\ndef helper(value: object) -> object:\n    return QualificationModel.model_validate(value)\n", "findings": []}
{"case": "B10-unlisted-class", "source": "from pydantic import BaseModel\nclass Arbitrary(BaseModel):\n    pass\n", "findings": []}
{"case": "B11-multiple-allowed-bases", "source": "from pydantic import BaseModel\nfrom typing import Protocol\nclass Arbitrary(BaseModel, Protocol):\n    pass\n", "findings": []}
{"case": "B12-init-hook", "source": "from pydantic import BaseModel\nclass Arbitrary(BaseModel):\n    def __init__(self):\n        pass\n", "findings": []}
{"case": "B13-nested-module-mutable", "source": "if True:\n    values = []\n", "findings": []}
{"case": "B14-top-level-while", "source": "while True:\n    pass\n", "findings": []}
{"case": "B15-unlisted-try", "source": "def helper() -> int:\n    try:\n        return 1\n    except ValueError:\n        return 0\n", "findings": []}

```

## Corpus removal counter-mutations

```powershell
$probe = @'
import sys,unittest
from unittest.mock import patch
from tests import test_verification_qualification_boundaries as target
def run(label,name):
 print(label,flush=True)
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([target.QualificationBoundaryTests(name)]))
 print("EXIT "+str(0 if result.wasSuccessful() else 1),flush=True)
run("CONTROL negatives","test_source_negative_corpus")
with patch.object(target,"NEGATIVE_ROWS",()), patch.object(target,"GRAPH_CYCLE_ROWS",()):
 run("MUTANT remove complete negative corpus","test_source_negative_corpus")
run("RESTORED negatives","test_source_negative_corpus")
run("CONTROL positives","test_source_positive_corpus")
with patch.object(target,"POSITIVE_ROWS",()):
 run("MUTANT remove all six positive controls","test_source_positive_corpus")
run("RESTORED positives","test_source_positive_corpus")

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $probe
```

Process exit 0; embedded HISTORICAL_EXIT 1 reports the baseline's three expected failures (the diagnostic process itself exits 0).

```text
CONTROL negatives
test_source_negative_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_negative_corpus) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.065s

OK
EXIT 0
MUTANT remove complete negative corpus
test_source_negative_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_negative_corpus) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
EXIT 0
RESTORED negatives
test_source_negative_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_negative_corpus) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.059s

OK
EXIT 0
CONTROL positives
test_source_positive_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_positive_corpus) ... ok
EXIT 0

----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
MUTANT remove all six positive controls
test_source_positive_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_positive_corpus) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s
EXIT 0

OK
RESTORED positives
test_source_positive_corpus (tests.test_verification_qualification_boundaries.QualificationBoundaryTests.test_source_positive_corpus) ... ok
EXIT 0

----------------------------------------------------------------------
Ran 1 test in 0.006s

OK

```

## Retrospective exact-A baseline (not an implementation-time first-red claim)

```powershell
$probe = @'
import ast,copy,hashlib,subprocess,unittest
from pathlib import Path
baseline="485d882f578f84dac1c975b32ced2a4ae6e7d43a"
raw=subprocess.run(["git","show",baseline+":tests/test_verification_qualification_boundaries.py"],check=True,capture_output=True,timeout=60).stdout
text=raw.decode("utf-8")
tree=ast.parse(text)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="test_architecture_dependency_gate")
prefix=[]
for statement in method.body:
 if isinstance(statement,ast.For):break
 prefix.append(copy.deepcopy(statement))
assert isinstance(prefix[-1],ast.FunctionDef) and prefix[-1].name=="check_graph"
extract=ast.FunctionDef(name="extract_checker",args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=prefix+[ast.Return(value=ast.Name(id="check_source",ctx=ast.Load()))],decorator_list=[])
prepared=ast.fix_missing_locations(ast.Module(body=[extract],type_ignores=[]))
print("BASELINE",baseline,flush=True)
print("SOURCE LF SHA256",hashlib.sha256(raw.replace(b"\r\n",b"\n")).hexdigest(),flush=True)
print("ACCESS_ONLY: copy original method statements through check_graph; remove outer self and all harness loops; append return check_source. Checker function AST unchanged.",flush=True)
namespace={"ast":ast,"Path":Path,"__file__":str(Path("tests/test_verification_qualification_boundaries.py").resolve())}
exec(compile(prepared,"baseline-access-only","exec"),namespace)
checker=namespace["extract_checker"]()
class HistoricalRegression(unittest.TestCase):
 def test_mutual_recursion(self):
  with self.assertRaises(AssertionError):
   checker("def one(value: int) -> int:\n    return two(value)\ndef two(value: int) -> int:\n    return one(value)\n","qualification_values")
 def test_rebound_receiver(self):
  with self.assertRaises(AssertionError):
   checker("from typing import Mapping\ndef helper(value: object) -> object:\n    if isinstance(value, Mapping):\n        value = {}\n        return value.get('x')\n    return None\n","qualification_values")
 def test_computed_facade_all(self):
  with self.assertRaises(AssertionError):
   checker("__all__ = frozenset(('Value',))\n","qualification_contracts")
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HistoricalRegression))
print("HISTORICAL_EXIT",0 if result.wasSuccessful() else 1,flush=True)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $probe
```

Process exit 0; embedded HISTORICAL_EXIT 1 reports the baseline's three expected failures (the diagnostic process itself exits 0).

```text
BASELINE 485d882f578f84dac1c975b32ced2a4ae6e7d43a
SOURCE LF SHA256 599e814b13930cc13dff3be1f7ca47487a2622dd2a7b681d5a5d964129a4f625
ACCESS_ONLY: copy original method statements through check_graph; remove outer self and all harness loops; append return check_source. Checker function AST unchanged.
test_computed_facade_all (__main__.HistoricalRegression.test_computed_facade_all) ... FAIL
test_mutual_recursion (__main__.HistoricalRegression.test_mutual_recursion) ... FAIL
test_rebound_receiver (__main__.HistoricalRegression.test_rebound_receiver) ... FAIL

======================================================================
FAIL: test_computed_facade_all (__main__.HistoricalRegression.test_computed_facade_all)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 30, in test_computed_facade_all
AssertionError: AssertionError not raised

======================================================================
FAIL: test_mutual_recursion (__main__.HistoricalRegression.test_mutual_recursion)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 24, in test_mutual_recursion
AssertionError: AssertionError not raised

======================================================================
FAIL: test_rebound_receiver (__main__.HistoricalRegression.test_rebound_receiver)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 27, in test_rebound_receiver
AssertionError: AssertionError not raised

----------------------------------------------------------------------
Ran 3 tests in 0.002s

FAILED (failures=3)
HISTORICAL_EXIT 1

```

## Independent helper finding validation

Shared receiver/import/behavior findings are independently reproduced in the fifteen packets above. This additional finite command checks unsupported exports/imports and mutable policy. Dictionary state is restored in finally; this is a policy-immutability finding, not a runtime-sandbox claim.

```powershell
$probe = @'
import json,sys
sys.path.insert(0,"tests")
from verification_qualification_source_gate import inspect_sources
from verification_qualification_source_policy import SourceModule as M,SourceUnit as U,INTERNAL_DEPENDENCIES
def packet(module,source):
 return tuple(U(item,source if item is module else "") for item in M)
def show(label,units):
 print(json.dumps({"probe":label,"findings":[(f.module.value,f.line,f.column,f.rule.value) for f in inspect_sources(units)]}))
show("unresolved-export",packet(M.MANIFEST_CONTRACTS,"from .binding_contracts import NotActuallyExported\n"))
show("unlisted-typing-name",packet(M.QUALIFICATION_VALUES,"from typing import Callable\n"))
units=packet(M.QUALIFICATION_VALUES,"from .report_contracts import QualificationReport\n")
show("policy-control",units)
original=INTERNAL_DEPENDENCIES["qualification_values"]
try:
 INTERNAL_DEPENDENCIES["qualification_values"]=frozenset({"report_contracts"})
 show("mutable-policy-bypass",units)
finally:
 INTERNAL_DEPENDENCIES["qualification_values"]=original
show("policy-restored",units)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $probe
```

```text
{"probe": "unresolved-export", "findings": []}
{"probe": "unlisted-typing-name", "findings": []}
{"probe": "policy-control", "findings": [["qualification_values.py", 1, 0, "SG01"]]}
{"probe": "mutable-policy-bypass", "findings": []}
{"probe": "policy-restored", "findings": [["qualification_values.py", 1, 0, "SG01"]]}

```
