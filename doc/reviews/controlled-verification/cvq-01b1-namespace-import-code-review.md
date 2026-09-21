# CVQ-01B1 namespace/import review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B1` / `CODE_REVIEW` / `02` |
| Conclusion / iteration | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` / closure01 initial plus correction exhausted; section5 is current |
| Candidate / baseline | 8dc22904921cb6b0c56a88d7e224ca66828f8c14 / 1a1b6eb3af4c5a7e31de0d102eaf20b461c49f98 |
| Authority | [B1](../../../modules/tickets/controlled-verification/cvq-01b1-namespace-import-admission.md) document03 / closure01 at6266cfcfb46956213b71042ec4035ae73a5442f6, LF b6fde644de900e054875d85488a610380efe9f01341c7037a78139023842280f |
| Reviewer / evidence | root; [unreduced commands, probes and mutations](cvq-01b1-initial-evidence.md) |
| Source owner | retained cve_wire_implementer, Luna/xhigh, .worktrees/cvq-01 / codex/cvq-01 |
| Profile / effects | POC / HIGH_ASSURANCE; AST-only; no integration/push/release/install/native effects |

## 1. Admission and verified scope

Root independently read back exact candidate, clean owner/root review worktrees, baseline ancestry,
five-path allowlist, unchanged A/production paths and clean diff check. Full strict check21 passes;
focused44 passes including actual nine-file architecture smoke. Source changes add finite enums
and preserve the frozen entry. Technical comments/data only; no owner prompt/work-order prose
was found by semantic inspection. That is review evidence, not a qualified content-enforcement claim.

Read CodeReview, review-checks, adversarial-review and source-content-boundary. Current exact
SPEC07 section11.3 and section12 control schema admission; behavior/call/body work remains B2/B3.
XSS/browser/SQL/production data/secret/native deployment are not present. Same-lifetime worktree
and task identity is bound; runner/receipt/host readback NOT_REQUIRED. This test-support grammar
does not become a sandbox or repository authority. Original B's exhausted review is historical.

## 2. One complete batch of blocking findings

| ID / classification | Frozen closure | Evidence and bounded correction |
| --- | --- | --- |
| B1-F01 IMPLEMENTATION_DEFECT | section2, B1-I01/I08/POS | symbols.py:74–79 rejects every level except1. Legal `from ..controlled_verification.qualification_values import CapabilityFamily` wrongly gets SG01; a normalized parent-relative cycle lacks SG08. Implement exact Python package-level normalization against library.controlled_verification, whole identity and finite graph; out-of-package/too-deep paths stay rejected. Pin allowed normalized edge and normalized forbidden/cycle cases, not just blanket parent rejection. |
| B1-F02 IMPLEMENTATION_DEFECT | section2, B1-I06 | gate.py:139–140 validates each incoming origin but not the incompatible same-name export result. With both real source symbols defined, two permitted origins exported under the same name return no findings. Reject actual incompatible export ambiguity, no first/last wins; assert the typed AMBIGUOUS fact and named SG06 with complete unrelated prerequisites. |
| B1-F03 IMPLEMENTATION_DEFECT | section2, B1-I06/POS/SET | symbols.py:193–201 folds a previous iteration's UNKNOWN and the later resolved state of the same declaration into permanent AMBIGUOUS. All-allowed values→binding→manifest→ports→facade→init re-export rejects; reversing packet input changes findings. Distinguish unresolved traversal progress from distinct declarations; resolve finite paths consistently and accept the full allowed chain in either input order. No requirement that final origin be a direct consumer edge. |
| B1-F04 EVIDENCE_DEFECT | section3 and B1-I03/I04/I05/I06/I08 | Corpus still lacks required complete source definitions; alias/re-export uses non-existent qualification_admission, alleged ambiguity is unknown-symbol red. Later-entry uses two statements, not two entries; no committed nested-cycle sensitivity or explicit nested-export isolation assertion. Repair within the frozen alternatives, keep separate stable IDs/locations and independently literal roster/count. Root's first-entry and top-level-only-cycle mutations both yield zero red. Add correct discriminating fixtures so those precise mutations turn the corresponding cells red/restored-green. |

All findings cite the approved closure; no added hardening, model elevation or expanded file scope.
This is one correction batch, not successive one-finding-at-a-time rounds. Preserve accepted A,
B2/B3 rows, exact public seam and finite policy. No line cap or generic framework request.

## 3. Mandatory adversarial helper and root adjudication

Plan: exact1a1b6eb candidate, closure01, REQUIRED, SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION,
READ_ONLY_INTENT_ONLY, NO_EXTERNAL_EFFECT. Reused profile_delivery_audit (retained Terra/xhigh).
Immutable git-object static review only, no test execution/mutation/effect, no verdict authority.

Helper returned FINDINGS: first-entry coverage gap (corpus163), masked alias/ambiguity
(corpus165–190, symbols139–143/191–194), missing unused-scope cycle fixture (corpus225–249).
Root verified the source and independently reproduced the first-entry and nested-cycle zero-red,
the genuine ambiguity bypass and the broken legal multi-hop path. Findings accepted into B1-F02/F04.
The helper did not discover or approve unrelated B2/B3 changes.

## 4. Evidence disposition and continuation

Owner first-red was the real suffix assertion on7171f41, not a missing-new-type collection error.
Root independently weakened exact-target to prefix: named suffix red, exact function restoration
green. Root's different door, per-statement first-entry admission, stayed green; nested graph
weakening also stayed green. Both are defects, not passes. Raw output is indexed in evidence01.
Root's namespace probes6:3fail/3pass; legal multi-hop probes2:2fail. Complete focused44/strict21
green is retained but cannot overrule these named contradictions.

Per approved sequential grant, retain ticket/closure/owner/worktree and correct additively from
1a1b6eb. Root review owns the verdict and the final B3 full20-rule campaign; do not duplicate
accepted A campaigns or widen into B2/B3. Original B exhausted history remains unchanged.
Root will re-run this finite batch, affected strict/focused checks and an exact-candidate helper.
A second failing B1 review returns CONVERGENCE_REVIEW_REQUIRED, never a third correction.
ACTION_COMPLETED / CVQ01B1_CHANGES_REQUESTED -> AUTO_CONTINUE / SAME_OWNER_ADDITIVE_CORRECTION.

## 5. Correction review — 2026-09-21

Exact correction8dc22904921cb6b0c56a88d7e224ca66828f8c14 descends from1a1b6eb.
Root read back the same retained clean owner/worktree; four allowed paths changed, no production/A
or policy change. Review tree detached at8dc2290 is clean. Strict21 and focused44 pass (16.982sec).
[Correction evidence01](cvq-01b1-correction-evidence.md) retains exact commands and unreduced outputs.

| Finding | Current disposition at8dc2290 |
| --- | --- |
| B1-F01 | PARTIALLY_FIXED. Original normalized symbol import/cycle pass. Equivalent parent-relative and absolute package-module alias forms still reject (SG01/SG09) while direct form accepts. Whole exact module-form normalization remains incomplete. |
| B1-F02 | IMPLEMENTATION_FIXED. The complete two-origin ambiguity probe now rejects, typed AMBIGUOUS assertion exists. |
| B1-F03 | IMPLEMENTATION_FIXED / EVIDENCE_PARTIAL. Root's exact six-module allowed chain passes in both orders. The committed positive matrix only retains a short facade chain, so it does not pin the prior longer-path failure. Do not call the actual current resolver failing merely because the committed fixture is absent. |
| B1-F04 | PARTIALLY_FIXED. Nested export isolation and nested-cycle sensitivity repaired; root nested graph mutant now produces the named SG08 red/restored-green. First-entry-only mutation remains ZERO_RED, with two statements still substituting for two entries. Several prerequisite packets remain empty; indirect origin fixture is a cycle/unknown, not a resolved constituent path. |
| B1-F05 IMPLEMENTATION_DEFECT | Section2 exact namespace/external allowlist and B1-I01: `from .__future__ import annotations` is accepted with no finding because the external future shortcut ignores relative level. The relative internal target does not exist. Root reproduces this bypass; accepting it is not a new external surface allowed by the ticket. |

B1-F05 and the equivalent package forms were missed in root's first batch; root records that
review coverage gap, not a scope expansion or implementer-only blame. They derive from the
already-frozen whole-identity/normalization requirement. Source packets were AST-only, never executed.

Mandatory exact-candidate helper reused profile_delivery_audit with the same REQUIRED categories,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT plan. It returned FINDINGS: the long positive path is
not committed (corpus324/boundaries135), and per-statement later aliases remain absent (corpus167).
Root adjudication: accept as EVIDENCE_DEFECT under B1-F03/F04. Root's independent eight prior probes
pass, so the first helper finding is a missing regression guard, not evidence of a current
long-chain implementation failure. The first-entry counter-mutation independently confirms the
second. No helper verdict was accepted; no new seat or external/native effect.

This exhausts closure01's initial plus one correction review. Conclusion CHANGES_REQUESTED /
CONVERGENCE_REVIEW_REQUIRED; do not dispatch a third correction. Candidate/history stay immutable.
B2/B3 remain approved but DEPENDENCY_PENDING, not dispatchable. No partial integration, push,
release or installation. Root routes the remaining normalization and evidence obligations to
[convergence05 section6](cvq-01b-convergence-proposal.md#6-b1-correction-exhaustion-and-bounded-replan--2026-09-21).
ACTION_COMPLETED / CVQ01B1_CORRECTION_REVIEW_COMPLETE ->
WAIT_FOR_HUMAN / CONVERGENCE_REPLAN_DECISION_REQUIRED.
