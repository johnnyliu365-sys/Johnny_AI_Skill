# 05S — Codex Lifecycle Contract Staging

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07, AC-08 and Test seams 2, 3, 5, 6 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011`; verification-architecture revision approved by the owner on 2026-08-10 |
| State | `IN_PROGRESS / DISPATCH_PREPARED` |
| Dependency | Ticket 05A independently approved and integrated by `b22c6c4` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Implementation language | Python 3.11 with strict typing |
| Environment | Disposable test-owned process/filesystem sandbox only; no live Codex CLI state, Windows package installation, user profile/configuration, target project, network, login, Secret, push or deployment |

## User-observable outcome

A reviewer can run one bounded command that provisions a disposable Codex CLI
contract environment, executes a real child process against persisted sandbox
state, observes exact marketplace/plugin add, list, remove and absence results,
then destroys the sandbox. A post-effect failure leaves observable residue until
an explicit matching removal is performed. Unrelated state and two synthetic Git
repositories remain unchanged.

This ticket creates the missing verification environment; it does not repair or
integrate Ticket 05B. After 05S is independently approved and integrated, the
control plane must refreeze 05B, 05C and Ticket 04 against its evidence. A full
Windows user-profile sandbox remains a separate Ticket-04 packaging gate.

## Architecture and truth boundary

- The sandbox owns one unique OS-temporary root outside both repository
  worktrees. It contains a test-only executable shim, strict persisted state,
  source/installed payload copies and unrelated sentinels.
- Commands cross a real `subprocess` boundary. A test-only command port replaces
  only the executable token with the exact sandbox shim; it never invokes the
  host `codex` executable and never edits global `PATH`, `%LOCALAPPDATA%`, Codex
  configuration or registry state.
- List, add, remove and absence results are reconstructed from freshly loaded,
  recursively validated persisted state. Success/absence proof must not be
  generated from the caller request, queued response or stale snapshot.
- Finite fault injection is a strict enum recorded in sandbox state. A
  post-effect fault is applied only after the state/file effect is durably
  observable; a pre-effect fault produces no state authority.
- The operator-facing evidence projection contains only scenario/result enums,
  command identifiers, relative owned locators, digests and presence booleans.
  It contains no absolute path, raw prompt, target-project data, Secret or PII.

## Scope

Production `library/local_orchestration` source is read-only for this ticket.
Implementation is limited to the following new test-support surface plus the
separate docs-only handoff:

```text
tests/staging/__init__.py
tests/staging/codex_lifecycle/__init__.py
tests/staging/codex_lifecycle/contracts.py
tests/staging/codex_lifecycle/sandbox.py
tests/staging/codex_lifecycle/shim.py
tests/test_codex_lifecycle_staging.py
doc/WorkProgressReport.md
```

No hard line-count limit applies. Scope is controlled by the named behavior,
files, strong types and finite closure. Do not add `Any`, `type: ignore`,
optional/`None` effect ports, shell command strings, broad clear/delete,
Docker/VM/Windows-Sandbox provisioning, product-adapter changes, historical
Ticket-05 source, a second worktree or a live host mutation.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `S1` — disposable provision | Provisioning creates one unique external temporary root, a test-only executable and recursively strict empty state. The root is not beneath either repository worktree and no global environment/configuration value is changed. Invalid/relative/reused roots fail before process or filesystem effects. |
| `S2` — stateful successful lifecycle | A real child-process sequence observes empty lists, adds the exact marketplace, adds the exact plugin/payload, observes both installed, removes plugin before marketplace, then freshly observes plugin, marketplace and installed path absent. Outputs match the documented structured field surface used by 05A/05B/05C. |
| `S3` — independent truth | After every effect, fresh list/absence results come from reloaded state and actual sandbox files. Mutating the request or a previous response cannot change observed truth. Corrupt, missing, extra, null, foreign or stale state blocks rather than fabricating success/absence. |
| `S4` — effect timing | A finite pre-effect failure creates no state. A finite post-marketplace or post-plugin failure leaves exactly the effected state observable. Matching explicit removal clears only that state; a removal failure leaves residue visible for retry. |
| `S5` — foreign-state isolation | Pre-seeded unrelated marketplace/plugin entries and sentinel files remain byte/value identical through success, failure, compensation and retry. Same-name foreign ownership is never silently overwritten or removed. |
| `S6` — target and host isolation | Existing and empty synthetic Git repositories remain byte-plus-porcelain identical. The test records the exact child executable and proves it is the sandbox shim; the live `codex` executable, user Codex state and real target projects receive no call or write. |
| `S7` — teardown and evidence truth | Teardown validates the exact sandbox root and removes it; final readback proves absence. Focused/full tests, strict full-tree mypy with repository-external removed cache, in-memory compile, source sentinel, `git diff --check`, reverse mutations and tracked/ignored/cache readback all pass. Claims report exact commands/counts and do not invent retroactive first-red evidence. |

## Finite scenario matrix

| Cell | Scenario and terminal assertion |
| --- | --- |
| `E01` | Clean full lifecycle: exact add/list/remove/absence order and final root teardown. |
| `E02` | Marketplace pre-effect versus post-effect failure: respectively no entry versus one freshly listable owned entry. |
| `E03` | Plugin pre-effect versus post-effect failure: respectively no plugin versus one freshly listable installed plugin/path. |
| `E04` | Plugin-removal and marketplace-removal failure independently retain only their actual residue and permit bounded retry. |
| `E05` | Corrupt/missing/extra/null/stale persisted state and file/state disagreement never report installed or absent success. |
| `E06` | Unrelated and same-name foreign entries are preserved; exact owned identity alone can mutate. |
| `E07` | Request/response mutation after an effect does not alter fresh list or path truth. |
| `E08` | Synthetic Git bytes/porcelain, live-host call sentinel, global environment and both repository worktrees remain invariant; exact teardown removes only the sandbox root. |

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s_20260810` |
| Allocation | `aln_local_orchestration_install_05s_20260810` |
| Receipt | `rcpt_local_orchestration_install_05s_20260810` |
| Correlation / question | `corr-local-orchestration-install-05s-20260810` / `q-local-orchestration-install-05s-20260810` |
| Authority | Owner instruction to establish the isolated test environment before refreezing downstream tickets; continuing program authority `PRG-20260809-042` |
| Required baseline | The control-plane docs commit that adds this ticket and verification-architecture revision |
| Branch/worktree rule | Preserve the inactive 05B branch and submitted SHAs as immutable evidence. In the same sole implementation worktree, create exactly one new-ticket branch `codex/implementation-codex-lifecycle-staging-05s` from the exact required baseline. No additional worktree or concurrent branch. |
| Required return | One implementation commit containing only the authorized test-support files, complete S1–S7/E01–E08 evidence, clean worktree, then one separate docs-only handoff commit. No review, integration or downstream-ticket decision. |

## Review and continuation

The reviewer executes S1–S7/E01–E08 once and batches all findings under
`CodeReview.md`. One additive correction at most may remain on the same branch;
no same-ticket replacement branch/worktree is permitted. Only `APPROVED` plus a
safe guarded integration permits 05B/05C/04 refreeze. This staging evidence is
not proof that a packaged installer works in a clean Windows user profile.
