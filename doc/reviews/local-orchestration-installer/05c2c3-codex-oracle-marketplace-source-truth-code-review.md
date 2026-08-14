# Ticket 05C2C3 Codex Oracle Marketplace-Source Truth Code Review

## Initial decision

| Field | Evidence |
| --- | --- |
| Verdict | `CHANGES_REQUESTED / EVIDENCE_DEFECT`; implementation and tests are approved, but the handoff is not append-only. |
| Ticket / closure | `05c2c3-codex-oracle-marketplace-source-truth`; `CLOSURE-LOCAL-INSTALL-T05C2C3-01`; S1-S7 revision 01 |
| Reviewed handoff | Implementation `8de9e60a59645fdf4fc7e6b298be3bcd70b06789`; WPR-only handoff `ff71ce25a2d82b89ceb8eb42c7c16607ca062198` / PRG-423 |
| Immutable export | PASS. Exact handoff ZIP SHA-256 `0F9998CD8C41327179D3267C148C0AFB64FDAED061941C3CC8B7BEE2F4AC3A92`; implementation parent is exact dispatch `3ffdb74eed7ca0dc4fe213a8571e662edd408521`, and implementation scope is exactly the two frozen paths. |
| Blob identity | PASS. Git blobs are `86edacbbb43a36475071c5494b8c4e0cc2b81f60` for `oracle_child.py` and `d897552e65c506e49132b82e1eaccdf8f4004d37` for its direct test. Canonical Git-byte SHA-256 values are `B302119B6A24A3A97CB0B71C8F6C439C6D09CCF165ADFC2A6C9CB72F1772A5B1` and `635247606863A4E950B6CDC005ED29C39D296AA95010262F4DFFEB704987D98E`. PRG-423 separately labels the checked-out Windows byte frame. |
| Independent verification | Focused lifecycle `34/34`; full serial `517/517`; strict `mypy --strict --explicit-package-bases --no-incremental` over `148` files; in-memory compile `148` files; exact ancestry, two-path implementation scope, WPR-only handoff scope, clean owner lane and exactly three-worktree topology pass. |
| Integrated disposable probe | PASS. Real registration returned `REGISTRATION_SUCCESS_ACCEPTED`; exact receipt conversion and oracle adapter admission succeeded; receipt removal returned `REMOVED`; replay returned `NOT_INSTALLED`; owned state and payload were absent; exact lease teardown returned `REMOVED`. |
| Reverse evidence | PASS. Replacing relative source derivation with the old hard-coded value made S1 red; filtering prefix-similar foreign state made S2 red. Restored source passed all 34 focused tests. |
| Review-environment readback | The first Windows TAR extraction omitted two Unicode directories and produced a false full-suite failure. Their tree OIDs matched the control tree; a Unicode-safe ZIP export then passed strict mypy and compile. Reviewer-created junctions, caches, exports and archives were removed and read back absent. |
| XSS / effect boundary | `XSS_NOT_APPLICABLE`. Typed Python staging fixture and tests only; no Browser, WebView, HTML/DOM, JavaScript, bridge, live Codex/host, target-project, network, package/install, push, release or deployment effect. |

## Finding

### CR-179 — handoff evidence was inserted into historical WPR content

- Classification: `EVIDENCE_DEFECT` against S7 and the append-only WPR rule.
- PRG-423 appears before PRG-413 even though PRG-413 through PRG-422 already
  existed at the dispatch baseline. It is therefore not an appended handoff.
- The content of PRG-423 is otherwise truthful and its commit is WPR-only.
- Correction is additive only: retain PRG-423 unchanged and append a new
  canonical handoff at physical EOF, explicitly superseding only PRG-423's
  placement as the integration handoff.

## CodeReview.md assessment

| Category | Result |
| --- | --- |
| Functionality / specification | PASS. Every validated marketplace derives its source from its own persisted relative locator; the exact lifecycle now closes register/remove/replay. |
| Clarity / P0 typing | PASS. The new helper has explicit `dict[str, object] -> dict[str, str]` typing, validates dynamic state at the child boundary and introduces no `Any`, `type: ignore`, optional port or dynamic member lookup. |
| Security / identity / paths | PASS. Exact canonical name/locator equality rejects prefix, suffix, casing, encoded and traversal variants. Foreign state is preserved and never authorizes the owned identity. |
| Boundary / exceptions | PASS. Invalid persisted state maps finitely to `STATE_INVALID` before partial output; no new broad catch, silent clear or effect widening exists. |
| Tests / truthfulness | `CHANGES_REQUESTED`. Executable evidence is strong and independently reproduced; only the non-append-only placement of the submitted handoff prevents closure. |
| Compatibility / maintainability | PASS. Protocol discriminators, DTOs, action order and product `library/` code remain unchanged. |
| Scope / resource fit | PASS. Exactly two frozen implementation paths and one WPR-only handoff; one owner and no helper were appropriate. |

No source or test correction is authorized. The sole continuation is a
same-ticket, same-branch, WPR-only additive evidence correction; prior commits
and PRG-423 remain immutable.

## CR-179 terminal correction review

| Field | Evidence |
| --- | --- |
| Verdict | `APPROVED / READY_TO_MERGE`; CR-179 is closed. |
| Corrected handoff | History-preserving control merge `605b2545c68268a39f1662e2ee518e58e13d96c1`; WPR-only PRG-426 commit `cd43b4570fe720962eca8aeb2cdf821938a27075`. |
| Scope / identity | Correction commit changes only `doc/WorkProgressReport.md`. Executable blobs remain `86edacbbb43a36475071c5494b8c4e0cc2b81f60` and `d897552e65c506e49132b82e1eaccdf8f4004d37`. |
| Evidence preservation | Canonical Git-content comparison gives identical PRG-423 section SHA-256 `484E91014292EACCAD50B2CEAFEA6764748B35C5150C887BCAF4D234ADE5A754` before and after correction. A checkout-only LF/CRLF frame difference is not a content change. |
| Append-only closure | PRG-423, PRG-424, PRG-425 and PRG-426 each occur once; PRG-426 is the last WPR heading and physical final record. It supersedes only PRG-423's placement as the canonical integration handoff. |
| Lane / residue | Owner tracked and ignored porcelain are clean, exactly three worktrees remain, and cache/runtime/bytecode residue is absent. No executable suite was rerun because executable blobs are immutable. |

No blocking finding remains. Reviewer-owned guarded integration of exact
handoff `cd43b4570fe720962eca8aeb2cdf821938a27075` is the only continuation.
