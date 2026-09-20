# CVQ-01B | Source admission code review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B` / `CODE_REVIEW` / `01` |
| Conclusion / round | `CHANGES_REQUESTED / INITIAL_REVIEW / NOT_INTEGRATED` |
| Authority | [B](../../../modules/tickets/controlled-verification/cvq-01b-source-admission.md) document05 / closure01 at b96aaaa6e385dc518389fc680cabbcf7251b01b2; LF 01530c75d2525ea86cabc018ea8808afa836f52bdfb5ca4b121530055d6e5093; SPEC07 section11.3 and wire03 unchanged |
| Baseline / candidate | 485d882f578f84dac1c975b32ced2a4ae6e7d43a -> 406e853 -> 704f066c881dc36e7176d8564edadd439a443a09 |
| Owner / reviewer / helper | Retained cve_wire_implementer / Luna xhigh; root sole verdict; retained profile_delivery_audit / Terra xhigh, evidence only |
| Isolation and effects | Clean candidate and root detached review snapshot; READ_ONLY_INTENT_ONLY helper; NO_EXTERNAL_EFFECT; no package import/exec by source gate, native/VM/provider/target/integration/push/release/installation effect |
| Evidence | [Root commands and unreduced output](cvq-01b-initial-evidence.md), EVIDENCE-CVQ-01B-INITIAL revision01 |

## 1. Admission and observed checks

Root read exact ticket/SPEC grammar and all five changed files, verified ancestry, clean owner
and review snapshot, and exact five-path diff. Production and A1/A2/A3 read-only tests/catalog/
fixtures are byte-identical to the accepted A baseline. Root independently ran strict checking:
21 files green; focused three-module suite:43 tests green; diff whitespace clean.

Those checks do not prove source admission. Fifteen independently authored, AST-only forbidden
packets all returned an empty findings tuple. Root also removed each entire corpus in memory:
negative and positive test methods both remained green, then their original tables were restored.
No fixture source was executed. The reviewer-owned final all-rule mutation campaign is
NOT_VERIFIED at this failing candidate; it will be run on the corrected candidate, not wastefully
claimed as complete now.

## 2. One batched correction against the frozen closure

Locations refer to candidate704f066. These repair already-approved obligations; no new grammar,
schema behavior, write boundary, dependency, verification profile or broader effect is authorized.

| Finding / class | Existing obligation and evidence | Required correction |
| --- | --- | --- |
| B-F01 IMPLEMENTATION_DEFECT / SYMBOL_RESOLUTION | Ticket2 all-scope normalized imports, actual symbol origin and distinct module/helper graphs; SG01–08. symbols.py30–42 ignores level/owner and selects only names[0]; gate.py105–116 accepts unlisted external symbols and any name from an allowed module. Root B01–03 and unresolved-export/Callable probes return no findings. No facade-origin traversal exists; module_edges scans only tree.body. | Resolve each imported entry, actual package-relative level, scoped aliases and explicit re-export origin through the declared DAG; unsupported/missing/ambiguous origins must not succeed. Inspect nested imports and distinguish module cycles from helper cycles. External module recognition is not symbol admission. Keep resolver/graphs in symbols, predicates in gate. No source execution or fake caller-supplied resolver. |
| B-F02 IMPLEMENTATION_DEFECT / CALL_AND_RECEIVER_BINDING | Ticket2 unchanged exact Mapping receiver; SG16–18 and schema-only boundary. gate.py167–180 uses line intervals and shallow targets, global name sets at184–218 lose scope/binding; line238 trusts substring Port; lines228–241 allow behavior calls. B04–09 admit constant callee rebind, same-line and destructuring receiver rebind, shadowed Mapping, FakePort.resolve and a known model's model_validate. | Validate scoped binding identity and statement order, including assignment targets, rather than names/line-number coincidence. Admit only the frozen schema call surface; no model/port behavior calls in this closure. Preserve guarded Mapping positive, typed acyclic helper positive and approved import aliases. |
| B-F03 IMPLEMENTATION_DEFECT / CLOSED_GRAMMAR | SPEC11.3 exact checked class inventory/bases, immutable module state and unsupported AST fail-closed; SG14/15/19/20. gate.py304–322 accepts arbitrary classes and combinations of recognized bases and exempts __init__;325–357 checks immediate module assignments and only three unsupported nodes; function-only loop/effect checks miss module scope. B10–15 admit unlisted class, multiple bases, custom initializer, conditional module mutable state, top-level while and unlisted try. | Use immutable literal catalog identities and exact base combinations; validate permitted AST forms by context across all scopes. Unsupported forms cannot fall through. No arbitrary class or imported-symbol constructor admission. Preserve the existing nine real source files unchanged unless an explicitly permitted, explained source-form equivalent is necessary. |
| B-F04 EVIDENCE_DEFECT / CORPUS_COMPLETENESS_AND_VACUITY | Ticket3 requires each enumerated alternative, fixed expected IDs/count and six complete, valid, independently authored controls. Driver44–45 fills eight empty modules; SG06 uses two direct imports instead of multi-hop packets; SG09 import_module is not aliased; SG12 lacks required alias/attribute alternatives; SG17 local-rebind duplicates alias; SG18 phase check only uses unknown receiver. SGP06 invents Value and lacks discriminator. Driver52–77 never pins IDs/count: deleting all negatives or positives remains green. Cycle rows lack designated location. | Provide literal complete nine-unit packets with valid minimum declarations/catalog names; represent every frozen alternative and exact expected rule/location, including real multi-hop origins. Pin independent expected IDs and counts so omission/duplication cannot pass. Six stable SGP IDs include both validator and discriminator. Do not derive expected truth from the checker, widen grammar for a fixture, or accept another rule as the designated cell. Cover driver extra-file rejection at its existing bounded seam. |
| B-F05 IMPLEMENTATION_DEFECT / RESPONSIBILITY_AND_POLICY | Ticket2 assigns frozen immutable policy and graph ownership. policy.py68/75 are mutable dictionaries and omit the required catalog vocabulary; gate.py250–301 implements helper graph resolution itself. Root policy-control rejects SG01, changing exported dictionary accepts the same packet, restoring rejects again. | Keep policy records immutable and reference the existing literal catalog without introspection; scope/symbol/helper-graph resolution belongs to symbols and grammar verdicts to gate. Keep the five declared owners; no giant merged checker, second framework, additional file or policy injection port. |
| B-F06 EVIDENCE_DEFECT / BASELINE_RETURN | Ticket4 requires genuine exact-A baseline evidence. Owner explicitly reported all three histories/access-only patch NOT_CAPTURED and returned a summarized unittest line, not raw output. | Preserve that historical omission honestly. Root has now reproduced all three exact-A assertion failures through an access-only AST extraction, with source hash and raw output in the evidence leaf. Do not claim implementation-time capture. For this additive correction capture genuine current-candidate failing assertions before each repair, and return exact commands/raw output and candidate/path identities. The final twenty-rule campaign remains root-owned; no duplicate owner campaign or fabricated chronology. |

## 3. Independent helper and root disposition

The mandatory finite helper inspected this exact candidate under SPEC_GAP, BOUNDARY_DATA,
CONSISTENCY and REGRESSION, read-only/no effects. It returned FINDINGS: mutable policy, escaping
parent-relative import, unsupported imported symbol, unlisted external name, same-line receiver
rebind, fake Port annotation, missing SG06/SG12/SG18 alternatives and SGP06 discriminator.

Root independently read the cited source, reproduced the shared issues and separately ran
unsupported-export, Callable and mutable-policy checks. All findings are retained in B-F01–05;
the helper does not own the verdict. Its source packet strings were not executed. This review
does not claim general Python purity, runtime sandboxing, external-provider qualification or
host enforcement. XSS/UI/SQL/production-data/concurrency/privileged-host effect are not applicable:
the diff is a local AST checker and literal tests; installed plugin and real native gates are not
touched or qualified.

## 4. Router continuation

ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / one additive correction by
the same owner in .worktrees/cvq-01 on codex/cvq-01 from704f066c881dc36e7176d8564edadd439a443a09.
Bind this committed review and its exact index digest before dispatch. Ticket05/closure01 and
all upstream pins, A preservation, five-path scope, one foreground process,60 seconds per
command,1200 seconds per pass, zero retry/load/polling remain unchanged. Initial review has now
been consumed; exactly one correction review remains. Do not integrate partial A/B.

Root then independently checks the return, the frozen corpus and complete rule-owner mutation/
restoration evidence. A defect remaining after that correction routes to convergence, not an
automatic third pass, stronger model or release. The separate local installation result stays
LOCAL_VERIFIED / PUBLICATION_INCOMPLETE; it is not blocked on B for already-completed evidence
and is not upgraded into publication authority.
