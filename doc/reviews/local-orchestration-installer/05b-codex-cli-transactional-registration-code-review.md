# 05B Codex CLI Transactional Registration - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05b-codex-cli-transactional-registration` |
| Result | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |
| Reviewer | Codex / current `main` worktree |
| Reviewed branch | `codex/implementation-codex-cli-registration-05b` |
| Boundary | Initial dispatch/review `f68d9d6` / `f02704f`; revision-02 correction `1a269411`; docs-only handoff `ed74589` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B-02` / `B1..B5`, `M01..M18` |

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

## Terminal revision-02 correction review

This is the single correction review permitted for
`CLOSURE-LOCAL-INSTALL-T05B-02`. Commit ancestry and scope are valid:
`1a269411` is the direct child of `ef1cf42`, `ed74589` is its docs-only child,
and the implementation branch is clean with no ignored/cache residue.

### Independent verification

| Check | Result |
| --- | --- |
| Focused / full | PASS: committed focused suite `8/8`; full discovery `180/180`. |
| Strict typing / compile | PASS: `mypy --strict --no-incremental` over `83` files using a removed external cache; three changed source/test files compiled in memory. |
| Diff / isolation | PASS: `git diff --check`; committed existing/empty Git byte-plus-porcelain test passes. |
| Scope | PASS: correction changes only `host_contracts.py`, `codex_cli_adapter.py` and `test_codex_cli_registration.py`; handoff changes only `WorkProgressReport.md`. Numeric line counts are informational and were not used as a gate. |
| Adversarial transaction probes | FAIL: pre-command unavailable effects receive removal authority; absence verification short-circuits; retry retains resolved effects; foreign add path/auth values can still produce `REGISTRATION_VERIFIED` through the submitted manifest fake. |
| Matrix truth | FAIL: eight aggregate tests do not execute the finite cases claimed for M04–M16. |

### Batched terminal findings

1. **CR-98 — `TICKET_DEFECT`, scope metadata.** Numeric production/test line
   ceilings were introduced by the control plane, not requested by the owner.
   They are superseded as acceptance or quality gates. This finding does not
   reject implementation size; maintainability is reviewed from responsibility,
   readability, contracts and behavior.
2. **CR-99 — `IMPLEMENTATION_DEFECT`, B3 / M04 / M06.** The journal changes to
   `MAY_EXIST` before invoking add, but `FileNotFoundError` and
   `PermissionError` leave that state intact. Independent probes therefore ran
   marketplace removal when marketplace-add was unavailable, and plugin removal
   when plugin-add was unavailable. These are specified pre-command failures and
   grant no deletion authority.
3. **CR-100 — `IMPLEMENTATION_DEFECT`, B4 / M12–M16.** `_absent` performs the
   three required proofs in one short-circuiting `try`. A malformed first
   marketplace-absence response prevented both plugin absence and installed-path
   absence from running (`manifest absence calls = 0`). B4 requires every probe
   to run even when an earlier probe fails.
4. **CR-101 — `IMPLEMENTATION_DEFECT`, B4 / M12–M17.** Retry authority is
   calculated before compensation and never updated. When plugin removal proves
   success but marketplace removal proof fails, the returned retry still grants
   both `PLUGIN_OWNED` and `MARKETPLACE_OWNED`; it must contain only effects that
   remain unresolved after the complete proof pass.
5. **CR-102 — `IMPLEMENTATION_DEFECT`, B4 / M13.** Marketplace removal compares
   raw `installedRoot` directly to the request's relative source locator. The
   closure requires raw path verification through the same ephemeral path-proof
   boundary used for installation. The current port has no removal-proof input,
   so correct absolute output cannot be normalized and foreign path identity is
   not proven by that boundary.
6. **CR-103 — `EVIDENCE_DEFECT`, B5 / M04–M16.** The eight committed tests use
   aggregate names but omit most required cells: M04/M06 unavailable, access,
   nonzero and generic variants; M05/M07 empty/null/foreign variants; M08–M10
   negative list/manifest cells; and most M12–M16 removal/absence cells. Green
   `8/8` therefore cannot substantiate the handoff claim that M01–M18 are green.
7. **CR-104 — `EVIDENCE_DEFECT`, B2 / M07 / M10 / M11.** The submitted manifest
   fake records both add DTOs but derives its proof from the request rather than
   verifying observed `installedRoot`, `installedPath` and `authPolicy`.
   Supplying foreign values still returned `REGISTRATION_VERIFIED`. The typed
   port shape is improved, but the required observed-output proof has not been
   demonstrated.

### CodeReview.md mandatory checks

- **Path-prefix / case boundary:** FAIL evidence. The ticket declares class 1
  applicable, but the committed test does not enumerate the required equal,
  prefix-plus-character, slash, case, encoding, traversal and empty cases.
- **Authority bypass:** FAIL due CR-99 and CR-101; pre-command failure and stale
  retry paths grant authority not supported by current-attempt proof.
- **Test truthfulness:** FAIL due CR-103 and CR-104. Test names claim multiple
  matrix cells that their assertions do not execute.
- Strong typing, dependency scope, Secret isolation and target-project
  isolation independently pass.

### Terminal conclusion

`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. This correction review is
terminal for revision 02. Per Workflow §8.1, no automatic second correction may
be dispatched. Ticket 05B returns to control-plane architecture/ticket
decomposition; the implementation branch, commits, handoff, allocation and
receipt remain immutable inactive evidence. No integration, Ticket 05C/04,
push, deployment, live Codex mutation, target-project action or schedule is
authorized.
