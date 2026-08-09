# 01 — Owned Install Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `IN_PROGRESS / REOPENED` |
| Language | Python 3.11, Pydantic strict models, standard-library temporary-directory fakes |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Single implementation branch | `codex/implementation-local-install-lifecycle-01` |
| Environment | Local test sandbox only; no real host, process, installer or target-project mutation |

## User-observable outcome

Given a valid staged fake payload, `install()` returns `INSTALLED` with one typed
ownership ledger and fake-host receipt. `uninstall()` removes exactly those owned
fake effects and returns `REMOVED`; repeating it returns `NOT_INSTALLED`.
Malformed, foreign or tampered ownership returns `INSTALL_BLOCKED` or
`UNINSTALL_BLOCKED` without deleting anything outside the fixed fake root.

## In scope

1. Strongly typed values for installation ID, fixed root, relative owned path,
   artifact digest, manifest, host receipt, ledger and finite public results.
2. One synchronous application service with constructor-injected filesystem,
   ledger, host and process ports.
3. Temporary-directory and in-memory fakes only.
4. Install, owned uninstall and idempotent repeat-uninstall behavior.
5. TDD, strict type checking and target-Git non-interference tests.

## Hard scope ceiling

The complete production surface is limited to these five files:

```text
library/local_orchestration/__init__.py
library/local_orchestration/contracts.py
library/local_orchestration/ports.py
library/local_orchestration/installation.py
library/local_orchestration/fakes.py
```

The complete Ticket-01 test surface is one file:

```text
tests/test_owned_install_lifecycle.py
```

- Production code must stay at or below 600 non-blank lines in total. The test
  file must stay at or below 500 non-blank lines. Generated files do not count
  because none are authorized.
- If the acceptance set cannot fit this ceiling, return `CHANGE_DETECTED`; do
  not add files, abstractions, phases or another branch.
- Do not reuse, copy, cherry-pick or reconstruct any deleted Ticket-01 branch.
  Implement only from this ticket, its SPEC and Context.

## Explicitly out of scope

- Crash recovery, replayable lifecycle phases, transition grants, causal proof
  frameworks, exhaustive fault products or a generic state-machine engine.
- Real Codex/Claude registration, subprocess execution, Router runtime, Git
  action, target-project write, Setup.exe, Inno Setup, networking, elevation,
  Secret/raw Context persistence or deployment.
- Ticket 02, 03 or 04 behavior.

## Public contract and simple lifecycle

The implementation must expose named request/result DTOs and a single service.
No public port returns an untyped object or dynamic dictionary.

Install:

1. Validate the complete request before the first port call.
2. Reject a foreign existing ledger or invalid path before effects.
3. Stage the fake payload, register the fake host, then atomically save the
   exact ledger containing the returned receipt.
4. Return `INSTALLED` only after ledger read-back matches.
5. A declared port failure returns `INSTALL_BLOCKED` and leaves no owned effect.

Uninstall:

1. Read and validate the exact ledger before mutation.
2. Reject missing/tampered/foreign ownership with `UNINSTALL_BLOCKED`.
3. Stop the fake process, remove the ledger-matched fake host receipt, remove
   only manifest paths below the fixed fake root, then remove the ledger.
4. Return `REMOVED` only after those exact fake effects are absent.
5. If owner, ledger and owned effects are already absent, return
   `NOT_INSTALLED`.

## Frozen acceptance set — `CLOSURE-LOCAL-INSTALL-T01-REOPEN-01`

This is the entire blocking set. Review may not add another Ticket-01 behavior.

| ID | Required executable evidence |
| --- | --- |
| `C1` | Valid request: first install returns `INSTALLED`; ledger and returned host receipt match the request. |
| `C2` | Normal uninstall returns `REMOVED`, removes only ledger-owned fake effects; repeat returns `NOT_INSTALLED`. |
| `C3` | Root cases: exact canonical root succeeds; extra suffix, trailing separator, casing change, encoded separator, `..` and empty root block before effects. |
| `C4` | For installation ID, manifest and owned path: `None`, omitted, empty string, whitespace and empty container are rejected at the boundary. |
| `C5` | Foreign installation ID, tampered ledger digest, foreign host receipt and indirect helper deletion all return blocked without deletion. |
| `C6` | Exactly four one-shot failures are covered: filesystem stage, host register, ledger save and host remove. Each returns the documented blocked result without an uncaught exception or unrelated deletion. No Cartesian fault matrix is required. |
| `C7` | Existing and empty temporary Git repositories remain byte-identical with unchanged `git status --porcelain` across one install success and one blocked uninstall. |
| `C8` | Source scan finds no `Any`, `type: ignore`, credential/token comparison, subprocess, network, Git mutation or target-project path access in this ticket surface. |

## Review and correction rule

- The reviewer runs `C1..C8` once and batches every finding in one report.
- A failed item may receive one additive correction commit on the same branch,
  worktree, allocation and receipt.
- No review result creates a new branch or worktree. A second failed review
  returns `CONVERGENCE_REVIEW_REQUIRED` and stops Ticket 01.

## Required evidence and return

1. Red test name and failure reason for `C1..C8` before production code.
2. `python -B -m unittest tests.test_owned_install_lifecycle`.
3. `python -B -m mypy --strict --no-incremental` over the five source files and
   one test file.
4. In-memory compile, source sentinel, fake install/uninstall smoke,
   `git diff --check` and clean status.
5. One ticket-only implementation commit and one separate docs-only handoff
   commit from the same implementation worktree and branch.

## Reopen handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_01_reopen_20260809` |
| Allocation | `aln_local_orchestration_install_01_reopen_20260809` |
| Existing receipt | `rcpt_local_orchestration_install_01_20260808` |
| Required baseline | The docs-only control commit containing this reopened ticket |
| Granted scope | Only this ticket's five source files, one test file, verification and implementation/docs-only commits |
| Not granted | Another worktree/branch, historical-source reuse, real effects, Ticket 02+, merge, push, deployment or schedule changes |
