# 05C2C1 — Codex Oracle Installed-Path Presence Evidence

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `01` |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C1-01` / P1-P8 |
| Dependency | 05C2B guarded merge `75eec43037c182772ca8bb2174de2ecd4e2943b6` |
| Profile / resource | `STANDARD`; one implementation owner, no helper; serial because 05C2C2 consumes this public staging contract |
| XSS | `XSS_NOT_APPLICABLE`: typed Python staging evidence only; no Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge |
| Implementation language | Python 3.11 with explicit dataclasses/Pydantic contracts and full-tree `mypy --strict` |

## Reserved observable outcome

Extend the disposable Codex lifecycle oracle with one exact, metadata-only
`OracleInstalledPathPresent` result. For `OracleAction.ABSENCE`, coherent exact
owned installed-plugin state plus its exact physical payload returns present;
coherent absence returns the existing absent result; incomplete, corrupt,
foreign-only, mismatched or unproved evidence remains finitely blocked.

## Frozen contract

- Add the exact frozen dataclass `OracleInstalledPathPresent` with only
  `action: OracleAction = OracleAction.ABSENCE`. Include it explicitly in
  `OracleRunResult` and `CodexOracleResponseAdmission`; no path, command,
  identity, payload, raw output or exception may be retained.
- The ABSENCE child path may emit the existing typed plugin-list protocol
  response while coherent owned state exists. It must not use a generic
  nonzero exit or `COMMAND_INVALID` as presence evidence.
- The parent oracle must re-read and exactly validate the command-bound owned
  plugin identity, logical installed path, plugin-list response and physical
  `plugins/<plugin-id>.json` payload before returning present. Exact owned
  plugin state and payload must be conjunctive.
- If both exact owned plugin state and exact physical plugin payload are absent,
  return the existing `OracleAbsent`, including a marketplace-only partial
  state; marketplace truth remains owned by the separate marketplace list.
- One-sided logical/physical residue, wrong identity/path/digest, malformed or
  extra/private state, reparse/topology anomalies, missing/tampered state and
  protocol mismatch must return an existing finite `OracleBlocked` reason.
  They must never become present or absent.
- Foreign and prefix-similar plugin/marketplace records and their payload bytes
  remain unchanged and do not count as exact owned presence. No foreign record
  may authorize a result for the owned installed path.
- `admit_codex_oracle_response` rebuilds an exact original
  `OracleInstalledPathPresent` only for `OracleAction.ABSENCE`. Subclasses,
  constructed/extra/private state, wrong action and cross-action use return the
  existing finite rejection types without inspecting hooks.
- Preserve all existing actions, response DTOs, logical/physical separation,
  fixed project-owned runtime root, bounded child behavior and exception
  policy. No `Any`, `type: ignore`, optional port, dynamic member lookup,
  broad clear/catch, historical source, live Codex/host or target-project effect
  is allowed.

## TDD closure

| ID | Required evidence |
| --- | --- |
| `P1` | First red proves `OracleInstalledPathPresent` and its union/admission path do not exist. |
| `P2` | A real initialized lease with exact marketplace/plugin registration and matching physical plugin payload returns exact present for ABSENCE. |
| `P3` | Fresh empty and marketplace-only partial states return exact absent; present and absent results retain only the fixed action. |
| `P4` | Logical-only and physical-only owned residue, wrong logical path/digest/identity, missing/tampered state and topology/reparse cells remain blocked. |
| `P5` | Foreign-only and prefix-similar records/payloads remain byte-identical, do not count as owned presence and do not authorize owned removal. |
| `P6` | Response admission accepts/rebuilds only exact present for ABSENCE and rejects wrong-action, subclass, constructed, extra/private and hook-trap matrices finitely. |
| `P7` | Reverse the logical+physical conjunct, command/action binding, foreign exclusion and exact admission-state guard; each named test turns red and exact bytes restore. |
| `P8` | Focused/full serial unittest, full-tree strict mypy, in-memory compile, source sentinel, exact scope/diff/ancestry, tracked/ignored/cache/runtime residue and three-worktree topology pass. |

CodeReview.md path-prefix, permission, null-equivalent, identity/token, finite
error, exception and test-truthfulness classes are applicable. Physical locators
remain fixed below the validated lease root; exact identity and topology checks
must precede affirmative evidence; mutation reversals prove test truth.

## Reserved writable scope

1. `tests/staging/codex_lifecycle_oracle/contracts.py`
2. `tests/staging/codex_lifecycle_oracle/oracle_child.py`
3. `tests/staging/codex_lifecycle_oracle/oracle.py`
4. `tests/staging/codex_lifecycle_oracle/response_admission.py`
5. `tests/test_codex_lifecycle_oracle.py`
6. `tests/test_codex_oracle_response_admission.py`

No library product source, package export, other source/test/document path,
live Codex/host/target-project effect, new worktree, helper Agent, branch fan-out,
push/staging publication, package/install, Secret, release or deployment is
authorized. There is no numeric line criterion.

## Planned binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2C1-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2c1_20260814_01` / `hnd_local_orchestration_install_05c2c1_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2c1_20260814` / `rcpt_local_orchestration_install_05c2c1_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2c1-20260814` / `q-local-orchestration-install-05c2c1-20260814` |
| Side context | `scx-local-orchestration-install-05c2c1-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

## Dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS` against exact freeze commit `c81c02ef4933a3d64b114103409117dc87e5aa18`: State, closure P1-P8, Python 3.11 explicit dataclass/Pydantic contracts plus full-tree `mypy --strict`, `STANDARD` one-owner/no-helper profile, `XSS_NOT_APPLICABLE`, exact six-path scope and all binding identities are explicit. |
| Authority / reviewer | Project-owner standing auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; no helper, subagent or second owner. |
| Released lane readback | Task idle; clean released 05C2B branch/head `codex/implementation-codex-receipt-removal-composition-05c2b` / `c4581e717dfe00af46af45bfa02f02bf56deea25`; exact top-level/linked git-dir, zero tracked/ignored/cache residue, exactly three worktrees and absent target branch verified. |
| Branch / baseline | In the same permanent worktree create only `codex/implementation-codex-oracle-installed-path-presence-05c2c1` at the exact control commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force or stash. |
| Binding | Workspace `wsb_local_orchestration_install_05c2c1_20260814_01`; handoff `hnd_local_orchestration_install_05c2c1_20260814`; allocation `aln_local_orchestration_install_05c2c1_20260814`; receipt `rcpt_local_orchestration_install_05c2c1_20260814`; correlation `corr-local-orchestration-install-05c2c1-20260814`; question `q-local-orchestration-install-05c2c1-20260814`; side context `scx-local-orchestration-install-05c2c1-20260814-01`. |
| Return | One implementation commit changing exactly the six frozen source/test paths, then append only reserved `PRG-20260814-404` in one WPR-only handoff commit. |

This receipt authorizes only P1-P8. The implementation owner must mechanically
re-read this exact ticket before first red and return
`HALT / TICKET_SCHEMA_INVALID` if any type, identity, scope or closure field is
missing or different. The owner may not self-review/integrate, orchestrate an
Agent, dispatch another ticket, push/publish staging, package/install, touch
live Codex/host/target project, release or deploy.

## Independent review

Implementation `8cb41e38dc7d9124a42c92a84d509a89dada0e51` and WPR-only
handoff `b625d3991a3d68b630d6a4c1a61c2cb8475eb7ae` satisfy P1-P8.
Reviewer-owned immutable-export verification passed focused `46/46`, full
serial `509/509`, strict mypy and in-memory compile over `148` Python files.
Exact owned logical state plus the physical plugin payload returned the named
presence result; coherent marketplace-only state returned exact absence;
identity mismatch remained blocked; exact response admission rejected
subclass, extra-state and cross-action values. Independently disabling the
physical conjunct and exact dataclass-state length guard made their governing
tests red, and exact commit blobs were restored. No blocking finding remains;
guarded integration is reviewer-owned.
