# CVQ-01B | Source admission code review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B` / `CODE_REVIEW` / `06` |
| Conclusion / round | `CHANGES_REQUESTED / CORRECTION_PENDING_RESOURCE / NOT_INTEGRATED`; section10 is current for B2 closure02; sections1–9 remain history |
| Current B2 authority / candidate | Document08/closure02 at 24ebb24be4d9f8219b1de7aee07d0c7ec6d3f5c2; candidate 5b3a432715163657c8d829d683fb0482fac8ba94 |
| Historical original-B authority | [B](../../../modules/tickets/controlled-verification/cvq-01b-source-admission.md) document05 / closure01 at b96aaaa6e385dc518389fc680cabbcf7251b01b2; LF 01530c75d2525ea86cabc018ea8808afa836f52bdfb5ca4b121530055d6e5093; SPEC07 section11.3 and wire03 unchanged |
| Historical original-B baseline / candidate | 485d882f578f84dac1c975b32ced2a4ae6e7d43a -> 406e853 -> 704f066c881dc36e7176d8564edadd439a443a09 |
| Owner / reviewer / helper | Retained cve_wire_implementer / Luna xhigh; root sole verdict; retained profile_delivery_audit / Terra xhigh, evidence only |
| Isolation and effects | Clean candidate and root detached review snapshot; READ_ONLY_INTENT_ONLY helper; NO_EXTERNAL_EFFECT; no package import/exec by source gate, native/VM/provider/target/integration/push/release/installation effect |
| Evidence | [Correction evidence](cvq-01b-correction-evidence.md) revision04 is current; [initial evidence](cvq-01b-initial-evidence.md) revision01 remains history |

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

## 7. B2 sole correction final review — 2026-09-22

Conclusion: **BLOCKED / CONVERGENCE_REVIEW_REQUIRED / NON_DISPATCHABLE / NOT_INTEGRATED**.
Exact authority is B2 document06/closure01 atf30e1a39c716bec007ef419bea6e6cec0550d2c3,
LFe5a52eb1e3108ff25a488773e9c7451ed891e0ae1a99ee867c2c42c82aea896d. The sole additive
correction is f2b3fb8dab7cae2554eb0ab24b9ee7dfc6d77092 from4f98243e. Root verified clean owner
and detached review trees, ancestry, exact three-path scope and118add/63delete. No new file,
product/policy/A change, dependency or source work-order prose appears in the diff. A/B1
acceptance is preserved; this is not an authorization to integrate the combined branch.

[Correction evidence revision03](cvq-01b-correction-evidence.md#b2-sole-correction-review-and-convergence-evidence--2026-09-22)
retains root's exact commands and unreduced output. Strict21/focused45 and real-package control
are green, but independent four-cell review yields one pass and three failures:

| Finding / disposition | Exact correction observation | Frozen obligation / root assessment |
| --- | --- | --- |
| B2-R01 IMPLEMENTATION_DEFECT / LEXICAL_BINDING | symbols403–406 skips a function's later local binding and inherits outer/builtin identity. The packet calling len before local len=0 returns no findings instead of SG17. corpus528–531 additionally encodes an unreachable later helper=0 as a positive. | Ticket2 lexical scope and local shadowing / B2-C17: a function-local assignment binds the name for that whole function; textual ordering cannot turn it into an outer/builtin call. Section6's call-before-later discriminator did not specify this adequately, and root owns that review ambiguity; the positive fixture cannot overrule the contract. |
| B2-R02 IMPLEMENTATION_DEFECT / MODULE_HELPER | The same skip rejects a typed acyclic module-local helper when its definition is later in the module: probe returns later(); later returns1. The gate returns SG18 at2:11. | Ticket2 direct statically bound typed local helpers and B2-POS: a deferred function body is not a top-level invocation at module evaluation time. Preserve forward helper identity without making future function-local assignments valid callees. No source packet was executed. |
| B2-R03 TICKET_DEFECT / GUARD_CONTRADICTION | symbols459–462 skips any inner comparison containing ast.In. Unrelated flag-in-labels under an ancestor Mapping guard returns no SG16, contradicting ticket2. Removing only that exception makes the real dependency-gate test reject unchanged report_contracts.py279:21. Control and restored runs pass. | Ticket2 simultaneously forbids inherited ancestor guards, requires the real package green and makes that product READ_ONLY. SPEC07 section11.3 only says local true branch/unchanged receiver; it does not impose immediate adjacency. The stricter ticket and section6 correction were not preflighted against accepted product. Root owns this convergence defect; another implementer retry cannot settle it. |

The retained Terra/xhigh evidence-only helper found the future-local fallback and membership
exception statically; root reproduced their predicates independently and added the converse
forward-helper test. Root alone owns this verdict. The old loop target now participates in the
same binding scan and the bypass fixture now names QualificationModel, but their final
discriminating mutation proof is NOT_VERIFIED; source improvement is not proof completion.
Known-port independent proof and original B2 alternative coverage likewise remain necessary
before approval. The owner-reported omitted earlier baseline is not retroactively repaired by
asserting chronology; prior root baseline evidence remains historical.

No new claim of browser/XSS, production SQL, provider, host, UI, deployment, installed-plugin
enforcement, privileged capability or general Python purity arises: only AST test support changed.
No actual native effect/concurrency surface is introduced. HIGH_ASSURANCE helper participation
is satisfied, not review approval. Current failures are collected together, not dripped into
new corrections. Initial plus sole correction under closure01 are exhausted. CodeReview section5
and ticket-decomposition route to UPSTREAM_DECISION_REQUIRED; no automatic third pass,
model elevation, B3 dispatch or partial integration.

## 8. Proposed B2 guard convergence — owner decision pending

Status: **OWNER_EXACT_APPROVAL_PENDING**. This is a proposal for the next closure, not an
approved change to closure01, SPEC, policy or source. Do not silently reinterpret the failing
SG16 assertion above as a pass.

Recommended decision: align the ticket with SPEC07's same-function guarded region and preserve
the accepted product. Replace ticket2's immediate-ancestor ban with this finite rule:

1. A Mapping.get receiver must resolve to the same exact binding as an actual unshadowed builtin
   isinstance(receiver, typing.Mapping) guard. Spelling alone, a same-name method or a compound
   condition merely containing such a call is insufficient.
2. The guard and call must be in the same function. The call must remain structurally inside
   that guard's true body. Nested ordinary If branches (true or else) and finite For branches
   already admitted by the schema grammar do not discard that evidence. A nested condition may
   be flag or membership: operator spelling grants no exemption. Crossing a function/class
   boundary, entering the Mapping guard's own else, leaving its true body, or encountering an
   unsupported control form cannot prove this rule. Other grammar checks stay independent.
3. The receiver and guard-name bindings must remain unchanged on the admitted path. Existing
   ordinary/same-line/unpacking/loop-target reassignment negatives remain; no source execution,
   general control-flow framework or relaxation of schema-only calls is authorized.
4. Under this proposed rule same-function flag/membership, nested-If-else and finite-loop
   unchanged-receiver examples are positive controls, including the real report_contracts
   discriminator. Cross-function inherited guard stays negative. Wrong receiver, shadowed
   guard, Mapping-guard else/after branch and rebind remain distinct SG16 negatives. Only owner
   approval may supersede the old same-function-ancestor negative; keep this review's actual
   failures as history. Each rebind fixture must discriminate its actual binding predicate,
   not remain red merely because another control-form rejection masks it.
5. Existing lexical-binding obligations remain unchanged: function-local assignment anywhere
   must not inherit an outer callable; directly bound acyclic module helpers may be forward
   references in deferred function bodies. The false-positive corpus row must become a named
   rejection; neither case is permission for callable aliases or unknown calls.

Alternative: retain immediate adjacency and explicitly widen the product change boundary to
rewrite accepted product source. That affects already accepted code for the checker's sake;
it is not recommended and is not authorized.

After owner decides, the control plane must compile the approved choice into an exact new
closure, preserve the historical candidate, preflight the real product plus these discriminators
together, bind the same cumulative resource ledger and only then admit the retained owner.
Use the existing four support/test files and existing evidence/review leaves; no new files,
framework, duplicate parser, product change, source prompt or twenty-rule owner campaign.
The focused expected reversals are guard evidence removal -> positive/control red, guard or
binding bypass -> designated negative red, and exact restore -> green. Root's different-door
real-package/known-port proof still applies. Unknown history is not zero and a new closure does
not reset the budget. No pre-approved or self-declared extra allowance is implied.

ACTION_COMPLETED / B2_CORRECTION_REVIEW_BLOCKED -> WAIT_FOR_HUMAN /
OWNER_GUARD_CONTRACT_DECISION_REQUIRED. WAKE_REQUIRED is a state, not a claim of delivery;
the decision is presented directly to the owner in this session. A/B1 remain accepted,
B3 remains dependency-pending, and no source/target/provider/integration/push/release/install
effect occurs in this control-plane closeout.

## 9. Owner decision recorded — 2026-09-23

Owner **「核准」** approves section8's recommended guard convergence at
6fd76324133ef93fbc70122c7881b48777d0b495, review04 LF
ff950a550f75f847d3c69d607ceeb5af4267ef493f1f6cc0e2c87801b828e844.
The historical candidate/closure01 verdict stays BLOCKED; this is not review approval.
B2 document08 section12 compiles CLOSURE-CVQ-01B2/02 and binds the unchanged source baseline,
profile, scope and remaining cumulative allocation. Section8's decision wait is now satisfied.
AUTO_CONTINUE / RETAINED_OWNER_IMPLEMENT follows committed ticket/index admission; no third
retry of closure01, source change by root, partial integration, push, release or installation.

## 10. Closure02 initial review; one batched correction — 2026-09-23

Conclusion: CHANGES_REQUESTED / CORRECTION_PENDING_RESOURCE / NOT_INTEGRATED.
B2 document08/closure02 at24ebb24be4d9f8219b1de7aee07d0c7ec6d3f5c2 governs candidate
5b3a432715163657c8d829d683fb0482fac8ba94 fromf2b3fb8. Root read the entire73add/26delete diff:
three existing allowed support files only, clean owner/review trees, no product/policy/A changes.
Root's call/positive drivers pass; owner reports strict21/focused45. Recovered owner text has
test-identity inconsistencies and is not accepted as an authentic unfiltered trace. Direct
root counterexamples/mutation output is retained in [evidence04](cvq-01b-correction-evidence.md#b2-closure02-initial-independent-review--2026-09-23).

| ID / class | Existing closure02 obligation and observed failure | Single correction |
| --- | --- | --- |
| B2-R2-F01 IMPLEMENTATION_DEFECT | GUARD-POS requires inner-If else to preserve a valid outer guard. symbols482 tests every isinstance-shaped inner If's else before establishing that this is the receiver's Mapping guard. An inner isinstance(other,int) or isinstance(other,Mapping) else returns SG16 at7:19 although the call remains in outer value's Mapping-true region. | Classify the exact receiver/Mapping guard before applying its own-else refusal; do not treat unrelated isinstance as that guard. Preserve the own-else negative and nested true/else positives. |
| B2-R2-F02 IMPLEMENTATION_DEFECT | FORWARD permits module-local helpers in deferred bodies, not an unbound nested-function name. gate204 passes allow_future for every non-module scope and symbols402–421 admits a future FUNCTION in that same local scope. Root and helper's future nested definition packet returns no finding. | Limit forward admission to the actual module binding reached from a deferred body; future local definitions/imports may not borrow module/builtin identity. Preserve legal forward module helper, ordinary prior local/helper binding, later local assignment negative and top-level forward-call negative. Use existing SG17/SG18 classifications, no new policy enum or resolver. |
| B2-R2-F03 IMPLEMENTATION_DEFECT | Effective guard contract excludes unsupported control ancestry. symbols505's ancestry test is an incomplete negative list; Try is accepted as guarded. Root sees only UNSUPPORTED_SYNTAX, not required guard refusal at the get. This is masked guard proof, not a claimed whole-gate acceptance. | Admit only the closed ordinary control/structural ancestry from section12; unsupported statement ancestry cannot attest a guard. Add a designated SG16 assertion so another rule cannot mask its removal. No expansion into B3 grammar ownership. |
| B2-R2-F04 EVIDENCE_DEFECT | FORWARD positive is absent in the committed corpus. Replacing only _check_calls allow_future with False leaves both call/positive tests green, restored also green. Owner's reconstructed-looking trace also disagrees with unchanged test identities. | Add the actual module-forward positive plus paired local/module negatives; retain fixed independent IDs/counts. Removing that admission must fail its positive assertion. Return actual commands/output; if raw output unavailable say MISSING, never compose a plausible trace. |

The finite retained helper found F02/F03 statically (1.86sec); root independently reproduced
them and F01/F04. Root owns all dispositions. Re-guarding a newly assigned receiver is not
reported as a defect: it has a new valid guard. Unsupported Try's global rejection is preserved
and accurately distinguished from the missing named guard evidence. No optional hardening,
new public contract, file, framework or requirement is added.

This is the initial review of closure02. One batched correction remains, same owner/worktree/
profile, subject to available resource admission; it is not another closure01 retry. No need
for another semantic approval. Preserve actual gains and existing rule proofs. Root does not
run the final complete proof on this already failing candidate and does not treat zero red
as success. B3 remains blocked on B2; no partial integration/push/release/install.

Resource decision requested, not granted: append120 command-wall seconds to the same B2 ledger
solely for this correction and final independent proof. Preserve prior reservations/unknowns;
charge the migration's50sec reservation conservatively (known40.128, remainder UNKNOWN), charge/
reserve10 of root40 for initial review/helper/readback, and retain document10. Existing30 plus
proposed120 would allocate60 owner,70 root/helper,20 closeout; no extra correction cycle,
higher model, new file or stress test. Do not start a correction whose full required commands
are knowingly underfunded. No claim of exact historical total or runtime budget enforcement.
ACTION_COMPLETED / CLOSURE02_INITIAL_CHANGES_REQUESTED -> WAIT_FOR_HUMAN /
CUMULATIVE_VERIFICATION_BUDGET_REQUIRED; approval resumes same-owner correction directly after
the exact committed resource binding, not another scope vote.
