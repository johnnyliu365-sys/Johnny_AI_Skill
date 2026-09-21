# CVQ-01B1 namespace/import review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01B1` / `CODE_REVIEW` / `01` |
| Conclusion / iteration | `CHANGES_REQUESTED` / initial review of closure01; one additive correction remains |
| Candidate / baseline | 1a1b6eb3af4c5a7e31de0d102eaf20b461c49f98 / 7171f41bdec15104fd653ecee6c8e06691055d16 |
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
