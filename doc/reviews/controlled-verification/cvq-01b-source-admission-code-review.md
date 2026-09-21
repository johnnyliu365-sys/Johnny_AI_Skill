# CVQ-01B | Source admission code review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B` / `CODE_REVIEW` / `03` |
| Conclusion / round | `B2_CHANGES_REQUESTED / B2_SINGLE_CORRECTION_ADMITTED / NOT_INTEGRATED`; section6 is current for B2; original B section5 remains exhausted history |
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

## 5. Sole correction review — 2026-09-20

Current conclusion: CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED / NON_DISPATCHABLE.
Correction candidate7171f41bdec15104fd653ecee6c8e06691055d16 descends additively from the initial
704f066. Exactly the same five support/test paths changed; production and the entire accepted
A1/A2/A3 surface remain unchanged. Root independently ran strict21 and focused43 (13.738s),
diff checks, original15 counterexamples, corpus-removal mutations and real-package inspection.
See [correction evidence](cvq-01b-correction-evidence.md), revision01.

Closed portions: original15 now all reject; negative/positive corpus removal now produces the
designated test failure (69!=0 and6!=0), then restoration is green; policy maps are immutable
snapshots; actual catalog names/bases are consulted; helper graph ownership moved to symbols;
multi-hop corpus data and location/ID metadata were added. Preserve these gains.

Remaining blockers are from the same frozen closure, not new requirements:

| Finding | Candidate location and independently verified result | Disposition |
| --- | --- | --- |
| B-F01 | symbols.py73–89 still truncates submodule suffixes. Appending `from .qualification_values.not_a_module import QualificationModel as ResolvedAlias` to the real binding source packet returns empty findings. The named module does not exist. | Exact path/origin resolution remains unproved. |
| B-F02 | gate.py200–208 still permits resolve on a listed port name in schema phase. Root temporarily inserted a correctly typed helper into the actual qualification_ports file, called only its existing port.resolve; the real architecture dependency test stayed green, as did control and byte-restored runs. | ZERO_RED / schema-phase call boundary unpinned. Not a merely unresolved/fake receiver case. |
| B-F03 | gate.py228 exempts every parameter named self, even a module helper;314–319 remains a small denylist. Root untyped module-self and attribute deletion packets returned empty findings; helper's module-scope for-loop counterexample was independently reproduced. | Exact typed helpers and closed, context-sensitive AST remain unproved; broad name/default success persists. |
| B-F04 | corpus.py95 still has direct import_module,102–103 direct Any/cast;132 only unknown-object model_dump. The required aliased-import, Any alias, typing.cast/aliased-cast and known-receiver schema negative alternatives remain missing. SGP06 names a catalog DTO but its packet does not declare/import QualificationModel and uses a repeated union branch, so its surrounding schema is not the specified valid minimum. | ID/count checks alone cannot establish the frozen alternative semantics. |
| B-F05 / P0 | symbols.py14–41 introduces SymbolOrigin.status, ImportBinding.status and NameBinding.kind/status as unrestricted str, then compares magic strings internally. Ticket2 requires closed resolution variants, not string conventions; strict typing green does not establish the finite domain. | Closed internal variants still required. No approval, regardless of line count. |

The retained Terra/xhigh helper returned FINDINGS on the same candidate under the original four
categories: B-F02 schema port call, B-F03 module for-loop and B-F04 missing alternatives.
Root validated those observations; helper supplied no verdict or external effect.
No work-order/prompt text was found in the source diff during semantic review; there is no
mechanical enforcement claim.

Owner reported baseline observations as summaries. Root's original and current unfiltered records
provide observable defect evidence; no missing initial history is invented. The root strict/focused
process briefly overlapped the original15 read-only probe before the pending session was read
back. This reviewer resource deviation is documented in the evidence, not attributed to owner.
Subsequent commands were serial. Temporary real-source mutation was byte-exact restored to
ports SHA2560c5d84194c130210222afcce9f86d541690330dfa7c17f5488dc44ac04b4423d; final
review worktree is clean.

Full twenty-rule mutation admission remains NOT_VERIFIED: spending that campaign on this already
failing candidate cannot yield approval. Root's real-package counter-mutation independently
establishes zero red. Initial plus sole correction are consumed. No third correction is authorized,
no stronger model is silently substituted, and no partial A/B integration occurs. Next action is
control-plane decomposition with exact owner-approved replacement closure, not a source retry.
See [B convergence proposal](cvq-01b-convergence-proposal.md), revision01.

## 6. B2 initial review and sole batched correction — 2026-09-21

Current B2 conclusion: CHANGES_REQUESTED / CORRECTION_ADMITTED / NOT_INTEGRATED.
This is the first review of the separately approved B2 closure01, not another correction of the
exhausted original B closure. B1 acceptance remains unchanged. Exact B2 authority: document05
at80e7d93f0743b0de85a601e30e778f0780f2c654, LF
9d28012a9f19bc93e9c0fe9e179ae665b87811b9e7ddb644e83fd1a59add5842.
Accepted B1a8340e2711540fd4ed05e4ef91c6877977f9d5db -> candidate
4f98243e2e50fe6dac359f2f78be0d10cf3238e8, additive, clean and exactly four existing paths.
Root read the complete diff and relevant existing scope implementation. Delta118add/8delete,
no product/A/policy/B1-owned row changes, new files, dependencies or source work-order prose.
[Unreduced root evidence](cvq-01b-correction-evidence.md), revision02, is current for this section.

Strict21 and focused45 pass independently. The correctly typed schema ports now reject, and
three known-port assertions on the exact accepted B1 checker fail as expected. That reproduction
occurred during review, not before implementation; the owner explicitly missed its required
baseline run. Green existing tests do not outweigh the following frozen-contract failures.

| ID / class | Exact observation at4f98243e and frozen obligation | One bounded correction |
| --- | --- | --- |
| B2-F01 IMPLEMENTATION_DEFECT / SCOPE_ORDER | symbols322–323 uses ast.walk ordinal as execution order;413–421 builds global name-only assignment aliases; gate191–210 chooses those before scoped binding. Ticket2 explicitly forbids both. Root's nested local helper followed by conditional deeper reassignment returns no SG17; an eval alias in an unrelated function assigns SG10 to another function's direct typed-helper call. Helper independently found parameter shadowing inherits global eval identity. | Resolve call aliases, bindings and prior assignments in actual lexical scope/source execution order. Add finite discriminators for deeper rebind, same-name alias in another scope and call-before-later assignment; do not add another resolver or change B1 origin/DAG contracts. |
| B2-F02 IMPLEMENTATION_DEFECT / RECEIVER_GUARD | symbols439–481 climbs to outer If and nested_control excludes If. A valid Mapping import plus guarded-positive control passes, while a call under a separate inner if flag also passes instead of SG16. Ticket2 requires immediate local true-branch, not inherited ancestor guard. | Require the correct immediate guard and unchanged receiver/guard identities. Preserve direct guarded positive and existing else/after/rebind cases. This is not permission to weaken schema-phase calls. |
| B2-F03 EVIDENCE_DEFECT / DISCRIMINATION_AND_IDENTITY | corpus172 loop row places call inside For. It remains green after only the loop-target reassignment predicate is removed because nested_control independently rejects it; root reproduced CONTROL0/MUTANT0/RESTORED0. C13 aliased-model-copy row uses model:object, not the required checked catalog-model bypass. | Make the loop-target cell discriminate its own guard rather than another SG16 door; preserve the inherited-loop negative separately where needed. Bind the aliased bypass to a real declared/imported catalog model. Retain all42 existing call IDs/alternatives except justified literal corrections, independently extend IDs/counts for the missing scope predicates; no calculated expected truth or new files. |
| B2-F04 EVIDENCE/RESOURCE_DEVIATION | Owner skipped required B1 baseline and supplied mutation summaries, not raw traces; default mypy cache conflicts with section9. Initial inventory caches have UNKNOWN origin. | Preserve omissions historically; do not fabricate initial red or delete caches. Root's exact-B1 reproduction is reviewer-time evidence. Capture genuine pre-fix failing assertions on4f98243e, exact commands/full outputs/durations, use -B and outside cache. Root owns final independent port and discriminating proof; no duplicate all20 campaign. |

The retained Terra/xhigh helper's two static findings were independently adjudicated; root owns
this verdict. One initial root probe lacked Mapping and therefore did not isolate SG16; it is
explicitly excluded from predicate proof and corrected with a real import and positive control.
No hidden failure is replaced by a summarized pass.

Correction preserves SPEC07/wire03, closure01, allowed four paths, A/B1 acceptance, existing
scalars/DTOs and schema-only phase. Product policy changes, B3 grammar, model elevation, new
frameworks or files are not authorized. The same Luna/xhigh owner receives exactly one additive
correction, not an amended closure or a third original-B retry. No need for new owner approval.

Resource lineage: prior B1195 remains; B2 initial owner650 is a conservative full-reservation
charge with actual known57.598 and remainder UNKNOWN, not observed650. Root/helper current
charges and closeout are retained; reserve180sec command-wall for this single correction and
the remaining B2 grant for independent final proof/docs. Same1200 total, max60/command, one
foreground process, no retries/load/polling. Do not count a model-thought duration as command time.
Root uses wait_agent, then independently checks final SHA and unchanged scope. Pass admits B3
binding under existing approval; remaining defect after this correction routes to convergence.
No partial integration, push, release or installation. ACTION_COMPLETED /
REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_B2_SINGLE_CORRECTION.
