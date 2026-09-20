# CVQ-01A2 closure02 | Reviewer evidence plan

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-PLAN-CVQ-01A2-C02` / `CODE_REVIEW` / `01` |
| State | `PROPOSED / OWNER_EXACT_APPROVAL_PENDING`; no mutation campaign executed under this plan |
| Source baseline | `c2fa4cdda1a785a4a8e2c7924a337c2fdd836160`; final implementation candidate must be pinned before execution |
| Authority | Owner 「啟用」 adopts convergence section23 at `a4ad05066e7b52eedd83133dad89ce81d8f398f4`, LF `a21ccd9c68335e6b9a0e3deae249613ef2c5d9156794d3fdbbc04391a2af35c3`; preparation only until exact closure02 approval |
| Contract | [A2](../../../modules/tickets/controlled-verification/cvq-01a2-case-manifest-admission.md) document06 / closure02 proposal; approved SPEC07 and wire03 unchanged |
| Owner / effect | Root owns execution/capture/verdict. Retained helper is evidence-only, not implementer or co-reviewer. No native capability, provider, VM, target, integration/push/release effect |

## Evidence destinations and complete record

Root writes only its own control docs and temporary mutations in its clean detached review
snapshot. The implementation branch is never the mutation workspace. Persist candidate SHA,
pristine byte hashes, exact temporary patch, full command, expected named cell(s), observed exit
and unreduced stdout/stderr for ordinary control -> mutant -> exact restoration -> same green
command. Record malformed commands separately; no collection error or unrelated exception is a
valid red. JSON-string encoding may preserve raw trailing whitespace/CRLF without Git whitespace
errors. No output reduction, narrative-only receipts or inferred chronological first-red claim.

| Destination | IDs | Initial state |
| --- | --- | --- |
| [Case evidence](cvq-01a2-closure02-case-evidence.md) | Q01–21; H01–04 | NOT_RUN |
| [Manifest evidence](cvq-01a2-closure02-manifest-evidence.md) | Q22–37; predecessor per-observation relocation audit | NOT_RUN |
| [Plan evidence](cvq-01a2-closure02-plan-evidence.md) | Q38–41; H05 | NOT_RUN |

The leaf index owns digests; these links are not another flattened registry. Root captures,
reads and judges each stream before updating its status. A prior candidate's unchanged source
can support history, but cannot replace an unexecuted current-candidate test obligation.

## Fixed command map

Use Python `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe`,3.11.9 /
Pydantic2.13.4 / mypy2.3.0. Each command uses the existing bounded subprocess wrapper:

```powershell
& $cvqPython -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' $cvqPython -B -m unittest -v tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.<method>
```

| Code | Exact method |
| --- | --- |
| CM01 | test_case_and_scope_identity_joins |
| CM02 | test_case_applicability_rows |
| CM03 | test_prerequisite_applicability_and_order |
| CM04 | test_capability_requirement_joins |
| CM05 | test_manifest_and_prerequisite_duplicates |
| CM06 | test_approved_plan_pin_coverage |
| CM07 | test_discovery_intent_and_property_membership |

One foreground process;60s per command /1200s per declared verification pass;zero automatic
retry/load/container/background polling. One pass per evidence partition, not unbounded
restarts after failure. Each of41 finite mutants runs one named method control/mutant/restored;
multiple affected subcases are individually read, not counted as one undifferentiated red.
Run strict/full focused commands from the ticket once at the final restored candidate.
A zero red or new overlap is a finding, never permission to invent another campaign.

## Finite mutation ledger (41, reviewer-owned)

Symbols below are at baseline c2fa4cd. Paths: QualificationCase/Scope/Manifest and
CapabilityRequirement are manifest_contracts.py; QualificationPrerequisiteSet is
prerequisite_contracts.py; ApprovedManifestFound is qualification_ports.py, all under
library/controlled_verification. No alias/field/base/port changes or new production files.

| ID | Command | Exact predicate / temporary door | Required cell or evidence |
| --- | --- | --- | --- |
| Q01 | CM01 | QualificationCase.coherent_case: binding.case_id mismatch condition -> False | CM01.binding.case_id |
| Q02 | CM01 | coherent_case: binding.fixture_digest mismatch condition -> False | CM01.binding.fixture_digest |
| Q03 | CM01 | coherent_case: binding.executable_digest mismatch condition -> False | CM01.native.executable_digest |
| Q04 | CM01 | coherent_case: binding.dependency_digest mismatch condition -> False | CM01.native.dependency_digest |
| Q05 | CM01 | coherent_case: binding.argv_digest mismatch condition -> False | CM01.native.argv_digest |
| Q06 | CM01 | coherent_case: binding.cwd_digest mismatch condition -> False | CM01.native.cwd_digest |
| Q07 | CM01 | coherent_case: binding.environment_plan_digest mismatch condition -> False | CM01.native.environment_plan_digest |
| Q08 | CM01 | QualificationManifest.unique_cases_and_requirements: binding.project_id / scope mismatch condition -> False | CM01.scope.project_id |
| Q09 | CM01 | QualificationManifest.unique_cases_and_requirements: binding.baseline_digest / scope mismatch condition -> False | CM01.scope.baseline_digest |
| Q10 | CM01 | QualificationManifest.unique_cases_and_requirements: binding.manifest_revision / scope mismatch condition -> False | CM01.scope.manifest_revision |
| Q11 | CM01 | QualificationManifest.unique_cases_and_requirements: binding.manifest_digest / scope mismatch condition -> False | CM01.scope.manifest_digest |
| Q12 | CM02 | coherent_case: pure/binding-kind mismatch guard -> False | All five C02.B.<kind> opposite-binding negatives |
| Q13 | CM02 | coherent_case: expected_subject isinstance mismatch -> False | CM02.subject.host_discovery_no_roster / nonhost_discovery_host_subject / host_property_no_roster |
| Q14 | CM02 | coherent_case: native platform != WINDOWS -> False | CM02.platform.native_discovery_generic / host_property_generic |
| Q15 | CM02 | coherent_case: subject/key host_surface mismatch -> False | CM02.host_surface.discovery_mismatch |
| Q16 | CM02 | coherent_case: subject/key adapter_revision mismatch -> False | CM02.host_revision.discovery_mismatch |
| Q17 | CM02 | coherent_case: append and self.kind is not SOURCE_PROPERTY to pure/binding mismatch condition | C02.B.source_property; narrow different-kind door retained |
| Q18 | CM02 | coherent_case entry: reject HostCapabilityKey when family is not HOST_MEDIATION | C02.K.<kind>.HN legal positives; narrowing a legal domain must turn red |
| Q19 | CM03 | coherent_case: disable explicit missing-WA04 guard AND pure prerequisite-kind-set guard together; retain order | CM03.wa04.source_property_missing |
| Q20 | CM03 | coherent_case: pure prerequisite-kind-set mismatch -> False, explicit missing-WA04 stays live | CM03.wa04.pure_case_extra / prerequisite.approved_source_replaced |
| Q21 | CM03 | coherent_case: requirement_keys != prerequisite_keys -> False | CM03.order.requirements_swapped / requirement_key_changed |
| Q22 | CM04 | unique_cases_and_requirements: case.capability_id not in scope -> False | CM04.case_capability.outside_scope; diagnostic-change evidence for this fixture |
| Q23 | CM04 | unique_cases_and_requirements: requirement.capability_id not in scope -> False | CM04.requirement_capability.outside_scope; diagnostic-change evidence only |
| Q24 | CM04 | unique_cases_and_requirements: missing-case branch raises -> continue this case_id iteration | CM04.requirement_case.missing; fail-open branch exposes acceptance without accidental KeyError |
| Q25 | CM04 | unique_cases_and_requirements: matched_case / requirement capability_id mismatch -> False | CM04.requirement_capability.case_mismatch; two IDs stay in scope |
| Q26 | CM04 | unique_cases_and_requirements: matched_case / requirement capability_key mismatch -> False | CM04.requirement_key.case_mismatch |
| Q27 | CM04 | unique_cases_and_requirements: derived-scope mismatch AND final PURE_RULE/non-NoRoster redundant guard -> False | All six CM04.scope.<case_id> alternatives; see equivalent-guard qualification below |
| Q28 | CM04 | unique_cases_and_requirements: HOST_DISCOVERY cardinality !=1 -> False | CM04.host_discovery.multiple_case_ids |
| Q29 | CM05 | QualificationScope.unique_capabilities: uniqueness mismatch -> False | CM05.scope.capability_ids_duplicate |
| Q30 | CM05 | coherent_case: dependency_digests uniqueness mismatch -> False | CM05.case.dependency_digests.duplicate |
| Q31 | CM05 | coherent_case: prerequisite_keys uniqueness mismatch -> False only | CM05.case.prerequisite_keys.duplicate; distinct requirement pins |
| Q32 | CM05 | coherent_case: prerequisite_keys AND prerequisite_requirements uniqueness mismatch -> False; retain order | CM05.case.prerequisite_requirements.duplicate; exact repeated pair |
| Q33 | CM05 | coherent_case: expected_check_ids uniqueness mismatch -> False | CM05.case.expected_check_ids.duplicate |
| Q34 | CM05 | CapabilityRequirement.unique_cases: case_ids uniqueness mismatch -> False | CM05.capability_requirement.case_ids_duplicate |
| Q35 | CM05 | unique_cases_and_requirements: case_ids uniqueness mismatch -> False | CM05.manifest.case_ids_duplicate |
| Q36 | CM05 | unique_cases_and_requirements: observation IDs uniqueness mismatch -> False | CM05.manifest.requirement_ids_duplicate |
| Q37 | CM05 | QualificationPrerequisiteSet.unique_ordered_keys: keys uniqueness mismatch -> False | CM05.prerequisite_set.exact_pair_duplicate; distinct_pair_positive remains green |
| Q38 | CM06 | ApprovedManifestFound.roster_plan_coverage: entire exact-coverage if condition -> False | missing/extra/duplicate/wrong key/ref/digest, pure-only/native-only extra cells |
| Q39 | CM06 | roster_plan_coverage: replace exact-set predicate by the strict-superset predicate below | CM06.host_subject.nonempty_extra_plan; all other guards remain |
| Q40 | CM07 | roster_plan_coverage: case.case_id not in planned_case_refs -> False | CM07.property.same_pin_membership_removed / wrong_pin_membership_rejected |
| Q41 | CM07 | roster_plan_coverage: matching_plans three-part key/ref/digest filter -> True | CM07.property.wrong_pin_membership_rejected; exact coverage and membership remain |

Q19/Q32 retain the already-approved equivalent-guard exceptions. Q22/Q23 must show literal
diagnostic change, never falsely report admission success. Q22's existing fixture also reaches
the later requirement/case ID comparison after its first membership guard is removed; record
that exact diagnostic transition, not an unrelated exception as admission proof. Q23 retains
the existing logical-implication rule. Q25 supplies independent ID-join admission red with
both IDs in scope. These observations preserve, rather than weaken, the literal error contract.
Q24's exact fail-open branch is proposed here:
skip only the absent case ID rather than continuing into a guaranteed dictionary KeyError.
Existing-case processing is unchanged; KeyError is not used as the oracle.

Q27 explicitly groups two guards of the same frozen derived-scope fact. The six existing CM04
negatives change non-pure scope to PURE_RULE. For a host subject, the final pure/no-roster guard
would otherwise mask removal of the derived-scope comparison. Disable those two guards only;
retain QualificationCase's kind/subject predicate, referenced-case/key joins and cardinality.
This is a temporary evidence isolation exception requiring exact closure02 approval, not a
product weakening or an instruction to edit accepted CM04 test bodies.

Q39 exact predicate (instead of the original len/unique/coverage if condition):

```python
if (len(expected) == 0 and len(actual) > 0) or len(actual) < len(expected) or len(actual) != len(set(actual)) or any(
    item not in actual for item in expected
):
```

Q18 adds only a constructor-local rejection of HostCapabilityKey with family != HOST_MEDIATION,
using literal diagnostic `host keys require host mediation`; legal positive cells must fail.
It is the root's distinct narrowing door, not just repeating owner-reported guard deletion.
No runtime class/constructor bypass, fixture rewrite or test-oracle mutation is authorized.

## Historical evidence: five named current cells, no invented TDD history

H01/H02/H03 = CM01 argv_digest/cwd_digest/environment_plan_digest; H04 = CM02 pure
HOST_MEDIATION + NO_ROSTER; H05 = CM06 pure-only extra host plan. Reproduce on exact
`5d7789db6b950d317e7b500b757aa77a54d609ed` and the final candidate. Extract only the
schema-compatible current cells and needed imports, retain their literal assertions and
use that snapshot's existing shared fixtures. Record the exact in-memory extraction/source
patch and commands in the destination; do not require a new module that never existed in the
old tree. No persistent test/helper file, production edit or old-ref movement. The current
test source/row -> extracted named H cell mapping must be explicit.

Each H cell must collect on5d7789d and show its actual historical behavioral red, then current
candidate green. Retain section14's earlier immutable preflight as history, not new execution.
A malformed extraction/collection error is BLOCKED evidence, not the requested red.

Root also audits every relocated predecessor observation from approved8d6 to the final
candidate. Existing assertions remain, even where a new named control overlaps them.
Do not silently accept a method-name-only map.

## Proposal preflight (read-only, not closure execution)

On c2fa4cd the17 literal legal controls and5 opposite-binding negatives below executed
through ordinary construction/JSON. All succeeded with the expected root/type/literal
diagnostic. This proves constructibility and error reachability, not that the missing test
rows are implemented or that any of41 mutations passed. Clean snapshot; no source edits.

Command:

```powershell
$a2Preflight = @'
import json
from pydantic import ValidationError
from library.controlled_verification import CapabilityFamily as F, CaseKind as K, HostCapabilityKey, HostSurface, NoRosterSubject, Platform, PlatformCapabilityKey, QualificationCase, BindingKind
from tests.verification_qualification_fixtures import qualification_case,native_case,host_discovery_case,host_property_case,native_binding,pure_binding
keys=(
("platform-plan",PlatformCapabilityKey(family=F.PLAN_BINDING,adapter_revision=1,platform=Platform.WINDOWS)),
("host-plan",HostCapabilityKey(family=F.PLAN_BINDING,adapter_revision=1,platform=Platform.WINDOWS,host_surface=HostSurface.CODEX_CLI)),
("host-mediation",HostCapabilityKey(family=F.HOST_MEDIATION,adapter_revision=1,platform=Platform.WINDOWS,host_surface=HostSurface.CODEX_CLI)),
)
cases=[]
for kind in (K.PURE_RULE,K.SOURCE_PROPERTY,K.TRUSTED_NATIVE_DISCOVERY,K.ADVERSARIAL_WORKLOAD,K.REAL_HOST_PROPERTY):
    for key_label,key in keys:
        case_id="case-"+kind.value.lower().replace("_","-")+"-"+key_label
        if kind in (K.PURE_RULE,K.SOURCE_PROPERTY):
            case=qualification_case(case_id,kind=kind,key=key)
        else:
            subject=host_property_case().subject if kind is K.REAL_HOST_PROPERTY else host_discovery_case().subject if kind is K.TRUSTED_NATIVE_DISCOVERY and key.family is F.HOST_MEDIATION else NoRosterSubject()
            case=native_case(case_id,kind,key,subject)
        assert QualificationCase.model_validate_json(case.model_dump_json())==case
        cases.append(case)
        print("VALID",case_id,type(key).__name__,type(case.subject).__name__)
for tag,key in (
("platform-wa04",PlatformCapabilityKey(family=F.RESPONSIBILITY_ADMISSION,adapter_revision=1,platform=Platform.WINDOWS)),
("host-wa04",HostCapabilityKey(family=F.RESPONSIBILITY_ADMISSION,adapter_revision=1,platform=Platform.WINDOWS,host_surface=HostSurface.CODEX_CLI)),
):
    case=qualification_case("case-"+tag,kind=K.SOURCE_PROPERTY,key=key)
    assert len(case.prerequisite_keys)==2
    assert QualificationCase.model_validate_json(case.model_dump_json())==case
    print("VALID",tag,"ordered-prerequisites",len(case.prerequisite_keys))
for case in cases[::3]:
    payload=json.loads(case.model_dump_json())
    replacement=native_binding(case.case_id) if case.binding.kind is BindingKind.PURE_CONTRACT else pure_binding(case.case_id)
    payload["binding"]=json.loads(replacement.model_dump_json())
    assert payload["kind"]==case.kind.value
    try:
        QualificationCase.model_validate_json(json.dumps(payload))
    except ValidationError as error:
        detail=error.errors()[0]
        assert detail["loc"]==() and detail["type"]=="value_error"
        assert detail["msg"]=="Value error, case kind and binding kind must agree"
        print("REJECT",case.kind.value,replacement.kind.value,detail["loc"],detail["type"],detail["msg"])
    else:
        raise AssertionError(case.case_id)
print("17 legal controls; 5 opposite-binding root rejections")
'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $a2Preflight
exit $LASTEXITCODE
```

Exit 0; raw output:

```text
VALID case-pure-rule-platform-plan PlatformCapabilityKey NoRosterSubject
VALID case-pure-rule-host-plan HostCapabilityKey NoRosterSubject
VALID case-pure-rule-host-mediation HostCapabilityKey NoRosterSubject
VALID case-source-property-platform-plan PlatformCapabilityKey NoRosterSubject
VALID case-source-property-host-plan HostCapabilityKey NoRosterSubject
VALID case-source-property-host-mediation HostCapabilityKey NoRosterSubject
VALID case-trusted-native-discovery-platform-plan PlatformCapabilityKey NoRosterSubject
VALID case-trusted-native-discovery-host-plan HostCapabilityKey NoRosterSubject
VALID case-trusted-native-discovery-host-mediation HostCapabilityKey HostDiscoverySubject
VALID case-adversarial-workload-platform-plan PlatformCapabilityKey NoRosterSubject
VALID case-adversarial-workload-host-plan HostCapabilityKey NoRosterSubject
VALID case-adversarial-workload-host-mediation HostCapabilityKey NoRosterSubject
VALID case-real-host-property-platform-plan PlatformCapabilityKey HostPropertySubject
VALID case-real-host-property-host-plan HostCapabilityKey HostPropertySubject
VALID case-real-host-property-host-mediation HostCapabilityKey HostPropertySubject
VALID platform-wa04 ordered-prerequisites 2
VALID host-wa04 ordered-prerequisites 2
REJECT PURE_RULE WINDOWS_LAB () value_error Value error, case kind and binding kind must agree
REJECT SOURCE_PROPERTY WINDOWS_LAB () value_error Value error, case kind and binding kind must agree
REJECT TRUSTED_NATIVE_DISCOVERY PURE_CONTRACT () value_error Value error, case kind and binding kind must agree
REJECT ADVERSARIAL_WORKLOAD PURE_CONTRACT () value_error Value error, case kind and binding kind must agree
REJECT REAL_HOST_PROPERTY PURE_CONTRACT () value_error Value error, case kind and binding kind must agree
17 legal controls; 5 opposite-binding root rejections
```

No new authority for integration, push, release, install, host configuration or runtime effect.
ACTION_COMPLETED / EVIDENCE_PLAN_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.
