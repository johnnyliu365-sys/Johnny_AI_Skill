# Ticket 05C2B Codex Receipt Removal Composition Code Review

## Initial review

| Field | Evidence |
| --- | --- |
| Verdict | `CHANGES_REQUESTED` |
| Ticket / closure | `05c2b-codex-receipt-removal-composition`; `CLOSURE-LOCAL-INSTALL-T05C2B-01`; B1-B9 revision 02 |
| Reviewed handoff | Implementation `49fbeafda7e02b01be99eab229fb5f83d86cd972`; WPR-only handoff `2067f6ce7b76c8bc4635695a6f902a7f9330fef2` / PRG-397 |
| Immutable export | PASS. Exact handoff ZIP archive SHA-256 `E6BE75FE99AA468E4ABBF5E9A977D1205748D724E0C6A6CC3DD4867EA9901C30`; dynamic verification ran from a fresh reviewer-owned `%TEMP%` export that was removed after readback. |
| Independent verification | Focused `16/16`; full serial `499/499`; strict `mypy --strict --explicit-package-bases --no-incremental` over `148` files; in-memory compile `148` files. Exact ancestry and three-path implementation / WPR-only handoff scope pass. |
| Adversarial probes | PASS for `19` cells: valid invocation with hook trap rejected as `INVALID_PORT` without inspection; invalid receipt and receipt mismatch precede port admission; one request identity spans all eight calls; foreign-only post-state proves owned absence; plugin/marketplace/path `MISMATCH` and `UNPROVED` all block before removal; adapter exceptions at calls 1 through 8 propagate and stop the sequence. |
| Reverse evidence | PASS for seven runtime reversals: removal order, installed/available/marketplace/path post-absence conjuncts, replay zero-removal and plugin-failure short-circuit each made its governing committed test red. Exact runtime bindings restored and focused returned `16/16`. |
| XSS / effect boundary | `XSS_NOT_APPLICABLE`. The diff adds typed Python composition only and no Browser, WebView, HTML/DOM, JavaScript, bridge, filesystem, process, network, live Codex, host or target-project effect. |

## CodeReview.md assessment

| Category | Result |
| --- | --- |
| Functionality / specification | PASS for the submitted runtime behavior under the independent matrices. Exact pre-proof, ordered removal, post-proof, replay and exception behavior match B1-B7. |
| Clarity / P0 typing | **FAIL — CR-175.** The private `_observe` helper receives the already rebuilt `CodexCompensationPortRequest` but annotates it as `object`, widening a validated internal domain value after the external boundary. `mypy` remains green because `object` is legal Python, but AGENTS P0 requires the internal contract itself to remain explicit. |
| Security / identity / permissions | PASS. Request construction precedes capability admission; foreign entries create no authority; exact identity and finite block reasons are preserved. |
| Boundary / exceptions | PASS in independent behavior probes, including all eight exception positions and the complete call-count sequences. |
| Tests / truthfulness | **FAIL — CR-176.** B3 explicitly requires declared-failure, malformed, mismatch and unproved coordinator matrices, but the direct test contains no plugin/marketplace/path `MISMATCH` or `UNPROVED` response cells. B7 requires invalid invocation/receipt/identity/capability zero-operation and no-hook matrices; only invalid invocation directly asserts the trap is untouched. Independent probes pass, but they cannot replace committed regression evidence. |
| Compatibility / maintainability | PASS subject to the bounded correction. No public name, status, enum or effect order needs to change. |
| Scope / resource fit | PASS. Exactly the three frozen implementation paths and one WPR-only handoff were committed; `STANDARD`, one owner and no helper remain appropriate. |

## Findings

1. **CR-175 — `IMPLEMENTATION_DEFECT`, AGENTS P0 / B9.**
   `library/local_orchestration/codex_receipt_removal_composition.py:185` uses
   `request: object` in the private `_observe` helper after 05C1 has already
   rebuilt a `CodexCompensationPortRequest`. Import and retain that exact named
   type at the internal boundary. The public `invocation: object` and
   `port_candidate: object` boundary remains unchanged.
2. **CR-176 — `EVIDENCE_DEFECT`, B3/B7/B8.**
   `tests/test_codex_receipt_removal_composition.py:111-269` does not commit
   the required actual-observer mismatch/unproved matrices or complete
   zero-operation/no-hook admission matrix. Add bounded table-driven direct
   tests using public response DTOs and the integrated 05C2A observer; do not
   replace it with a monkeypatch or duplicate its normalizer.

## Required bounded correction

Keep the same ticket, implementation owner, permanent worktree, branch,
allocation and receipt. Do not reset, amend, rebase, force, create a branch or
create a worktree.

1. Change only the composition source and its direct test. Package exports must
   remain byte-identical to implementation `49fbeaf`.
2. Type the private `_observe` request parameter as
   `CodexCompensationPortRequest`; retain the two public dynamic-boundary
   parameters exactly as frozen.
3. Add actual-response B3 cells for plugin collections, marketplace and
   installed path `MISMATCH` and `UNPROVED`; every cell must make exactly the
   three pre-proof calls, return `PRE_REMOVAL_EVIDENCE_INVALID`, and make zero
   removal calls.
4. Add B7 cells proving invalid receipt, receipt identity mismatch and invalid
   capability perform zero operations and do not invoke candidate descriptor,
   equality, representation or serialization hooks. Preserve the existing
   invalid-invocation trap.
5. Independently reverse the new mismatch/unproved and no-hook gates, require
   their named tests to turn red, restore exact bytes, then rerun B9. Return one
   additive correction commit and reserved PRG-400 in one WPR-only handoff.

No requirement/public-contract change, helper Agent, new effect, live host
mutation, push, staging publication, package/install, release or deployment is
authorized.
