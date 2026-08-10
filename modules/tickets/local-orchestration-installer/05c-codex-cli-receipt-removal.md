# 05C — Codex CLI Receipt-Bound Removal and Replay

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED / DEPENDENCY_WAIT / REFREEZE_REQUIRED` |
| Dependency | Tickets 05A and 05B independently approved and integrated |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, current model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree after a future unique dispatch |
| Implementation language | Python 3.11, as fixed by the approved SPEC |
| Environment | Windows user scope; recorded command/filesystem ports only; no live registration, target project, login, Secret, network, packaging, deployment or schedule |

## User-observable outcome

Given the exact receipt from integrated Ticket 05B, one removal invocation
removes the exact plugin before the exact marketplace and reports `REMOVED`
only after plugin, marketplace and installed path are all absent. Replay reports
`NOT_INSTALLED` only for the same receipt-bound identity and performs no
unrelated effect. A copied, foreign, tampered or partial receipt returns
`UNINSTALL_BLOCKED`. The completed adapter can be projected as `SUPPORTED` only
after the full register/remove lifecycle is independently verified.

## Scope and future ceiling gate

Authorized production files are the four 05A/05B production files. The only new
test file is `tests/test_codex_cli_removal.py`.

- The former parent-wide `400 / 450` ceiling is historical and no longer an
  implementation limit: Ticket 05B review proved that it conflicts with P0
  readability and finite fault evidence.
- After 05B is approved and integrated, the control plane must measure that
  exact baseline and refreeze 05C with its own finite matrix and incremental
  production/test ceiling before dispatch. This planning file grants no line,
  source or test expansion now.
- Use only independently integrated 05A/05B contracts. Rejected parent Ticket-05
  source/tests remain historical evidence and may not be copied or cherry-picked.
- No broad clear/cache deletion, optional port, `Any`, `type: ignore`, hidden
  config edit, target-project access, packaging or additional production file.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05C-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `C1` — exact receipt admission | Recursively strict-revalidate the 05B receipt and require exact installation, host, `HostRegistrationKey`, canonical root, source/installed relative locators, marketplace, plugin, observed version and manifest digest. `None`, missing/extra, copied, foreign, tampered, prefix/suffix/case, traversal and stale values block before effects. |
| `C2` — official remove order | Invoke exact plugin remove before marketplace remove. Plugin-remove output requires documented `pluginId`, `name`, `marketplaceName`; marketplace-remove output requires `marketplaceName`, `installedRoot`. Reject `{}`, missing/extra/invented fields, identity mismatch, timeout, nonzero, malformed output and port exceptions as finite blocked reasons. |
| `C3` — conjunctive terminal absence | `REMOVED` or `NOT_INSTALLED` requires exact plugin absence, exact marketplace absence and exact receipt-owned installed-path absence from fresh structured list/filesystem proofs. A retry after plugin removal must finish marketplace removal or block; it cannot return early absence. |
| `C4` — replay and isolation | Exact replay with all three states absent is idempotent and mutation-free. Foreign receipt, another marketplace/plugin, same name under another owner, stale list, foreign root/proof or any residue blocks without removing unrelated entries. Existing marketplace/plugin lists and representative target repositories remain byte/value/Git invariant. |
| `C5` — lifecycle and evidence truth | Preserve first-red names/reasons for C1–C4; independently run `detect → preflight → register → verify → receipt → unregister → verify absent` against recorded ports before projecting `SUPPORTED`. Run focused/full tests, strict mypy, no-bytecode compile, final cumulative line/scope/source checks, byte+porcelain Git isolation and reverse mutations for receipt admission, remove DTO/order, all three absence conjuncts and replay. No second live registration is permitted. |

## TDD defect classification

- Path-prefix/case boundary: C1/C3/C4 (`CodeReview.md` §2.1 class 1).
- `None`/empty equivalence: C1/C2 (`§2.1` class 2).
- Authority bypass: C1/C4 (`§2.1` class 3).
- Stable error and exception behavior: C2/C3/C5 (`§2.1` classes 5 and 6).
- Test truthfulness: C5 (`§2.1` class 7).
- Token comparison is not applicable; the source sentinel must prove no
  credential/token field or comparison was introduced.

## Completion and rollback boundary

Completion requires one ticket-only implementation commit, C1–C5 red/green and
reverse evidence, focused/full regression, strict typing, compile, final cluster
scope/line checks, byte+porcelain Git isolation, clean status and a separate
docs-only handoff. Recovery is a bounded retry with the same exact receipt; any
foreign proof or residual state remains `UNINSTALL_BLOCKED`. No cache clear,
manual target-project cleanup or live repair is authorized.

## Review and future handoff boundary

Ticket 05C remains `PLANNED` until 05A and 05B are integrated. Its future
handoff must create a new ticket-bound receipt and exactly one active branch in
the same sole implementation worktree. No current implementation authority is
granted by this planning document.
