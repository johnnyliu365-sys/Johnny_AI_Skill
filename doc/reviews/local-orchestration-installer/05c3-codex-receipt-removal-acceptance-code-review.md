# Ticket 05C3 Codex Receipt Removal Acceptance Code Review

## Initial decision

| Field | Evidence |
| --- | --- |
| Verdict | `CHANGES_REQUESTED`; CR-180 is an `IMPLEMENTATION_DEFECT`, and CR-181/CR-182 are `EVIDENCE_DEFECT` findings against the frozen A6-A8 closure. |
| Ticket / closure | `05c3-codex-receipt-removal-acceptance`; `CLOSURE-LOCAL-INSTALL-T05C3-01`; A1-A8 revision 03. |
| Reviewed chain | Exact dispatch `8ca7ded22c2812a541539e7852b142aa0ed6fea9`; implementation `78cd32da2490e999227f8409c4fcb52eed6e7e37`; WPR-only handoff `6f90e65c7206db21c80b03180c92c132b2b2659c` / PRG-430. Parentage and exact two-path/WPR-only scopes pass. |
| Immutable export | PASS. Unicode-safe ZIP SHA-256 `2E0295BE981254CF3D81D2827BD646BDE02BD8218C03593147C4B812D99C936F` was produced from the exact handoff commit without creating another worktree. |
| Independent verification | Focused `8/8`; full serial `525/525`; strict full-tree mypy `150` files; in-memory compile `150` files. Owner tracked/ignored porcelain is clean, the exact branch is bound to the permanent owner-1 worktree, and exactly three worktrees remain. |
| Adversarial readback | A constructed-receipt replacement turned six focused tests red and was restored exactly, so A2/A4 detect that shortcut. A reviewer mutation which changed external sentinel `.git/config` bytes while retaining clean Git porcelain left the governing A6 test green; the source was restored to exact blob `22aef119ded83c2ac25b5586bfd514dca095a291`. |
| XSS / effect boundary | `XSS_NOT_APPLICABLE`: typed Python disposable staging fixture and tests only; no Browser, WebView, HTML/DOM, JavaScript or privileged bridge. No live Codex/home/config, target-project, network, package/install, push, release or deployment effect was run. |

## Blocking findings

### CR-180 — internal helper retains the external dynamic type

- Classification: `IMPLEMENTATION_DEFECT` against A7.
- `receipt_removal_acceptance.py:199` declares internal `observed_run` parameter
  `command_value: object`. Revision-03 explicitly permits `object` only on the
  public `run_receipt_removal_acceptance` boundary and forbids retaining it in
  internal helpers.
- Independent AST admission reports
  `('observed_run', 'command_value', 199)` and exits non-zero even though strict
  mypy passes; therefore mypy alone does not enforce this domain rule.
- Correction: use the exact integrated `OracleCommand` type at this autospecced
  boundary and retain finite exact-type rejection without dynamic widening.

### CR-181 — external Git sentinel is not proven byte-identical

- Classification: `EVIDENCE_DEFECT` against A6 and A8.
- `test_a6_external_git_and_empty_sentinels_remain_untouched` checks only clean
  porcelain, an empty sibling directory, environment restoration and absence
  of sentinel path strings in selected DTOs/state.
- In the immutable review export, a bounded mutation appended bytes to
  `existing-git/.git/config` during the acceptance run. Git porcelain remained
  clean and the exact A6 test still passed. This proves the test does not cover
  the frozen byte-identical requirement.
- Correction: capture a deterministic relative-path/type/content snapshot of
  the complete Git sentinel tree, including `.git`, immediately before the
  acceptance call and immediately after it; require exact equality before any
  later diagnostic Git command. The same mutation must turn A6 red and then be
  restored byte-for-byte.

### CR-182 — A7 source gate does not enforce boundary-only `object`

- Classification: `EVIDENCE_DEFECT` against A7 and A8.
- The submitted source and all reported verification gates passed despite
  CR-180. No committed source test distinguishes the three authorized public
  `object` parameters from an unauthorized internal helper annotation.
- Correction: add a deterministic AST/source admission in the authorized test
  file which permits `object` only on the three public acceptance parameters
  and rejects internal `object`, `Any`, `type: ignore`, `model_construct`,
  `model_copy(update=...)`, dynamic member lookup and broad catches in the
  staging implementation. Prove the CR-180 form turns this test red, then
  restore exactly.

## CodeReview.md assessment

| Category | Result |
| --- | --- |
| Ticket dispatch schema gate | PASS. Revision 03 records state, closure, Python/strict mypy, STANDARD profile, XSS classification and exact owner/worktree/branch/baseline/allocation/receipt/correlation. |
| Functionality / specification | PASS for A1-A5. The actual integrated receipt reaches first removal `REMOVED`, replay `NOT_INSTALLED`, exact action order and foreign preservation. |
| Clarity / P0 typing | `CHANGES_REQUESTED` by CR-180/CR-182. Named models and public round trips otherwise pass. |
| Boundary / exceptions | PASS. Invalid public values fail finitely before oracle effect; catches are bounded to named validation/I/O failures. |
| Security / path-prefix / permission bypass | PASS for current closure. Prefix-similar foreign identities and bytes are preserved, exact identity binding is required and no alternate effect entrance was found. |
| Tests / truthfulness | `CHANGES_REQUESTED` by CR-181/CR-182. The full suite is green, but the frozen byte-isolation and boundary-only dynamic-type properties are not mutation-sensitive. |
| Task/worktree binding | PASS. Product task readback, normalized permanent root and Git worktree metadata match owner 1; prompt-only `cd` was not used as admission. |
| Profile / resource fit | PASS. `STANDARD`, one implementation owner and no helper are the minimum safe set; files and ownership do not justify fan-out. |
| POC/staging baseline | Not yet applicable as a post-POC promotion: 05C3 is still part of the first POC closure and performed only disposable staging effects. |
| Scope / residue | PASS. Two executable paths plus one WPR-only handoff; no cache/runtime/bytecode residue or fourth worktree. |

The correction must remain on the same ticket, owner, permanent worktree,
branch, allocation, receipt and closure revision. It may change only the two
already-authorized 05C3 files and append one new WPR-only handoff. Existing
implementation/handoff/review commits remain immutable; no reset, amend,
rebase, force, new branch or new worktree is authorized.

## Terminal correction review

| Field | Evidence |
| --- | --- |
| Verdict | `APPROVED / READY_TO_MERGE`; CR-180, CR-181 and CR-182 are closed. This is revision 03's single correction review. |
| Corrected chain | History-preserving merge `d9a6724292148ced85d53224dcb37e3c0906ad8c`; additive two-path correction `c090a3e5c6f3b6a8bf21ed30b20e940c1ea5e6c2`; WPR-only handoff `fc8709e4d26811072c6399a12252eafae2eae522` / PRG-433. Parentage and exact scopes pass. |
| Immutable export | Unicode-safe ZIP SHA-256 `710BB47FC022565B879BB7A51D3C96B50ACC229261FF4BD656C079E6EF80F0D2`. No review worktree was created. |
| Independent green evidence | Focused `9/9`; full serial `526/526`; strict full-tree mypy `150` files; in-memory compile `150` files; exact source scan permits only the public API's three `object` parameters. |
| CR-180 closure | PASS. `observed_run` uses exact `OracleCommand`. Reverting it to `object` made `test_a7_source_gate_limits_object_to_public_boundary` red with the unexpected `('observed_run', 'command_value')` tuple, then exact source was restored. |
| CR-181 closure | PASS. A6 snapshots relative path, node kind and file bytes for the complete external Git sentinel before/after acceptance. Appending bytes to `.git/config` made A6 red before its Git-status diagnostic, then exact source was restored. |
| CR-182 closure | PASS. The committed AST/source gate rejects unauthorized `object`, `Any`, `type: ignore`, construction/update bypasses, dynamic lookup, inspect, Optional/None-valued parameters, `typing.cast` and broad catches. The corrected source blob is `97b919b1b51b64c2da644b803da71a2da441e233`. |
| WPR / lane | PRG-430 through PRG-433 each occur once and PRG-433 is physical EOF. Owner-1 branch is clean at exact handoff, ignored readback is empty and exactly three worktrees remain. |
| Boundary | `XSS_NOT_APPLICABLE`; no live Codex/home/config, target-project, network, package/install, push, staging publication, release or deployment effect. |

No blocking finding remains. Reviewer-owned guarded integration of exact handoff
`fc8709e4d26811072c6399a12252eafae2eae522` is the only continuation.

## Guarded integration

| Field | Evidence |
| --- | --- |
| Exact merge | `d898d73fda650fc45d2028d1bbe71fab6111119c`; parents are terminal review `4b1b69ce3f877a3a98e86258ed15d137d7fb3f25` and exact handoff `fc8709e4d26811072c6399a12252eafae2eae522`. |
| Conflict handling | The predicted WPR-only overlap was the sole conflict. PRG-430 through PRG-434 were preserved in numeric event order; no source conflict, force, reset, rebase, amend or silent resolution occurred. |
| Post-merge verification | Focused `9/9`; strict full-tree mypy `150/150`; in-memory compile `150/150`; terminal-review full serial `526/526` remains bound to the exact integrated source blobs. Three worktrees, tracked/ignored porcelain and cache/bytecode readbacks are clean. |
| Final disposition | `APPROVED / COMPLETE / INTEGRATED`; no implementation correction or additional 05C3 dispatch remains. |
