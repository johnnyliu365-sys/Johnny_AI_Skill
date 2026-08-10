# 05B Codex CLI Transactional Registration - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05b-codex-cli-transactional-registration` |
| Result | `BLOCKED / TICKET_DEFECT` |
| Reviewer | Codex / current `main` worktree |
| Reviewed branch | `codex/implementation-codex-cli-registration-05b` |
| Boundary | Dispatch `f68d9d6`; implementation `5e919069`; docs-only handoff `ef1cf42` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B-01` / `B1..B5` |

## Independent verification

The submitted branch is clean. Implementation `5e919069` is a direct child of
dispatch `f68d9d6`; handoff `ef1cf42` is a separate docs-only child. The
implementation changes only three authorized production files and the new
authorized registration test. No second worktree, merge, push, live Codex
mutation or target-project action was observed.

| Check | Result / evidence |
| --- | --- |
| Focused / full tests | PASS: focused `8/8`; full unittest discovery `180/180`. |
| Strict typing | PASS independently: `mypy --strict --no-incremental` over complete `library tests` passed `83` source files using a repository-external cache that was deleted and proved absent. The handoff's `34`-file result was a narrower command than the dispatched full-tree requirement. |
| Compile / sentinel / diff | PASS: five-file in-memory compile and AST parse; no `Any`, `type: ignore`, `shell=True`, broad clear/delete, cwd or Git-reset sentinel; `git diff --check` passed. |
| Scope / ceilings | PASS numerically: cumulative production `305/310`; tests `299/320`; only `host_contracts.py`, `codex_cli_adapter.py`, `__init__.py`, `test_codex_cli_registration.py`, then docs-only `WorkProgressReport.md` changed. |
| Worktree state | PASS: tracked and ignored readbacks are empty; no `.mypy_cache`, `.pytest_cache` or `__pycache__` remains. |
| Observed-output binding | FAIL: foreign `installedRoot`, `installedPath` and `authPolicy` values still return `REGISTRATION_VERIFIED`; the receipt contains none of those observed values and the manifest port never receives the marketplace-add response. |
| Current-attempt ownership | FAIL: `alreadyAdded=true` is rejected but then treated as an owned marketplace effect and removed. A plugin-add timeout never attempts plugin removal even though B3 explicitly treats timeout as an effect-may-exist boundary. |
| Admission identity | FAIL: one `CodexPreflightEligible` containing only a version can be reused with another installation ID and still return `REGISTRATION_VERIFIED`; no exact current request/collision admission is re-established immediately before mutation. |
| Evidence truth | FAIL: the eight committed tests do not enumerate the B5 command/parse/list/manifest/compensation fault cells, and the Git test compares non-`.git` bytes only while the handoff claims byte-plus-porcelain identity. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `B1` | FAIL | Command order and strict DTO shape parse pass, but `installedRoot`, `installedPath` and `authPolicy` are accepted as arbitrary nonblank text and never bound to the request/proof. |
| `B2` | FAIL | List and manifest fields are checked, but success ignores the add responses' observed root/path/auth fields and a cloned preflight result can authorize a different installation. `CodexManifestProof` is reused as the receipt instead of a receipt type that binds every required observed field. |
| `B3` | FAIL | Zero-exit parse failures journal effects, but timeout ambiguity skips the possibly-created plugin and `alreadyAdded` incorrectly becomes owned deletion authority. |
| `B4` | FAIL | Stale list and foreign digest probes block, but compensation can delete a pre-existing marketplace and can report the timeout path compensated without attempting exact plugin removal. |
| `B5` | FAIL | Green/type/compile/scope state reproduces. The required finite boundary matrix, truthful porcelain isolation and per-boundary failure evidence do not. Source is also compressed into multi-statement lines despite the P0 readability gate. |

## CodeReview.md verification

| Required check | Result |
| --- | --- |
| Clear strong types | FAIL. Named DTOs exist, but `CodexManifestProof` doubles as a receipt, tentative/confirmed/pre-existing effects are represented by one enum tuple, and core transaction logic is compressed into long multi-statement lines. |
| Logic and edge cases | FAIL. Foreign observed output can succeed; cloned admission can mutate; timeout and pre-existing-state compensation violate current-attempt ownership. |
| Safety / privacy | FAIL for ownership safety because an existing marketplace can be removed. PASS for no Secret, target-project or raw-output persistence. |
| Test coverage / smoke | FAIL closure despite green `180/180`; required B1–B5 cells are absent and the Git assertion overstates porcelain coverage. |
| Dependencies | PASS. No new dependency or prohibited rejected-branch ancestry was found. |
| Project specification | BLOCKED. The submitted ticket omitted the mandatory implementation-language field and used the non-finite phrase `before/after every effect/parse/proof boundary` without enumerating the actual cells. |

## Batched findings

1. **CR-92 — `TICKET_DEFECT`, B5 / Workflow §9.3.** The reviewed ticket has
   no implementation-language field even though the approved SPEC fixes Python
   3.11, and its fault requirement is not a finite matrix. Repair the ticket and
   re-freeze a numbered closure before any correction handoff. The correction
   design must also resolve whether the remaining `5` production and `21` test
   nonblank lines can satisfy P0 readability without further compression.
2. **CR-93 — `IMPLEMENTATION_DEFECT`, B1/B2.**
   `codex_cli_adapter.py:98-105,110-119` parses but does not bind
   `installedRoot`, `installedPath` or `authPolicy`; a foreign-root/path/auth
   probe returns `REGISTRATION_VERIFIED`. Both add DTOs must participate in an
   exact injected proof, and a distinct receipt type must bind the documented
   observed fields while persisting no absolute path.
3. **CR-94 — `IMPLEMENTATION_DEFECT`, B3/B4.**
   `codex_cli_adapter.py:98-103,121-143` conflates tentative and owned effects.
   `alreadyAdded=true` causes removal of a pre-existing marketplace, while a
   plugin-add timeout omits plugin removal. Model tentative/confirmed/
   pre-existing ownership explicitly and compensate plugin then marketplace for
   every exact effect that exists or may exist; never remove known foreign state.
4. **CR-95 — `IMPLEMENTATION_DEFECT`, B2/B3.**
   `codex_cli_adapter.py:91-105` accepts a version-only eligible object with any
   request. A cloned eligible probe registered a different installation ID.
   Re-establish exact source and collision admission for the current request
   immediately before mutation, or use an equally strong request-bound typed
   admission; a caller-constructed version value is not authority.
5. **CR-96 — `EVIDENCE_DEFECT`, B5.**
   `tests/test_codex_cli_registration.py:79-154` covers only eight aggregate
   cases. It omits the finite DTO empty/null cells and the marketplace-add,
   plugin-add, both post-add lists, manifest proof, both remove operations,
   both absence lists and installed-path absence failure cells. Lines 146-154
   never read porcelain, contradicting the handoff's byte-plus-porcelain claim.
6. **CR-97 — `IMPLEMENTATION_DEFECT`, B5 / P0 readability.**
   `codex_cli_adapter.py:91-143` uses semicolon-compressed assignments,
   conditions and transaction steps. The fix must use readable named state and
   one responsibility per statement; if the ceiling cannot accommodate that,
   return to ticket design rather than compressing further.

## Conclusion

`BLOCKED / TICKET_DEFECT`. This is the single initial review for closure
revision 01 and all discoverable blocking findings are batched above. No
correction handoff is created by this review: the control plane must first add
the mandated language, replace the unbounded B5 phrase with a finite matrix,
and decide a feasible readable ceiling or decomposition. The existing
implementation task, worktree, 05B branch, allocation and receipt remain
unchanged and inactive. No integration, Ticket 05C/04 work, push, deployment,
schedule, live Codex mutation or target-project action is authorized.
