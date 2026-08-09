# 03 - Reversible Agent Host Capability Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `IN_PROGRESS / DISPATCHED` |
| Dependencies | Ticket 01 `491f98b`; Ticket 02 `92c58bf`; both closed |
| Language | Python 3.11, strict Pydantic models and recorded in-memory fakes |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Single implementation branch | `codex/implementation-host-capability-gate-03` |
| Environment | Recorded fake lifecycle only; no live host, subprocess, login, host configuration, target project, push or deployment |

## User-observable outcome

The local control plane reports Codex or Claude as `SUPPORTED` only when an
injected adapter supplies a complete exact-receipt lifecycle and proves its
registration absent after removal. No live adapter is authorized by this
ticket, so Codex and Claude remain `UNVERIFIED`; missing or foreign capability
returns a finite blocked report without process or host mutation.

## Smallest reusable-module selection

No catalog module is selected. `identity-resolution` is display/directory
logic, not installation authority; `workflow-router-poc` is unrelated to host
registration. Ticket 03 may reuse only the already integrated local feature's
public `InstallationId` value object. No historical host source exists.

## Hard scope ceiling

Production changes are limited to exactly these four files:

```text
library/local_orchestration/__init__.py
library/local_orchestration/host_contracts.py
library/local_orchestration/host_lifecycle.py
library/local_orchestration/host_fakes.py
```

The test surface is exactly:

```text
tests/test_reversible_agent_host_lifecycle.py
```

- Production changes must stay at or below 550 non-blank lines; the test file
  must stay at or below 450 non-blank lines.
- Do not modify Ticket-01/02 source or tests, `library/workflow_router`, host
  configuration, packaging, or another ticket.
- If the frozen closure cannot fit, return `CHANGE_DETECTED`; do not add files,
  phases, recovery engines, branches or worktrees.

## In scope and exclusions

In scope: strict host/registration/receipt/removal-proof/capability models; one
synchronous verification use case; typed lifecycle and command-result ports;
recorded fakes; exact ownership checks; metadata-only reports and public exports.

Out of scope: a production Codex/Claude adapter, real command execution,
subprocess/network/login, marketplace access, config/cache edits, model/thread
creation, live host mutation, target-project files, runtime/Git changes, setup
packaging and automatic host updates. A later request to claim a real host as
`SUPPORTED` requires explicit external test authority and change control.

## Frozen acceptance set - `CLOSURE-LOCAL-INSTALL-T03-01`

| ID | Required executable evidence |
| --- | --- |
| `H1` | A recorded exact lifecycle performs `detect -> register -> verify -> receipt -> unregister -> verify absent` once and returns `SUPPORTED`; the receipt/proof bind the same installation, host and registration key, and the fake ends absent. |
| `H2` | Public Codex and Claude capability queries without a live verified adapter return `UNVERIFIED` and invoke no command/lifecycle effect. No fake result may relabel them as production-supported. |
| `H3` | Exact registration-key matrix: canonical key is accepted; suffix, trailing separator, casing change, encoded separator, traversal and empty variants block before effects. |
| `H4` | For installation ID, host, registration key, command result and removal proof: `None`, omitted, empty, whitespace and empty-container shapes are rejected at the strict boundary. |
| `H5` | Direct removal and the verification use case both require the exact installation/host/receipt key. Foreign registration, cross-installation receipt and retry cannot remove or overwrite any effect. |
| `H6` | Exactly five recorded failures are covered: executable unavailable, access/policy denial, register failure, verify failure and removal/absence-proof failure. Each returns one finite blocked reason, no uncaught exception, no false receipt/support and no unrelated mutation. |
| `H7` | Capability reports, receipts and proofs contain only typed opaque metadata; raw command/source/path/URI/Secret/PII sentinels never appear. Existing and empty actual temporary Git repositories remain byte-identical with unchanged porcelain across one supported fake and one blocked fake. |
| `H8` | Source scan over the four production files finds no `Any`, `type: ignore`, credential/token comparison, subprocess/network, host-config/cache write, target-project write, real Codex/Claude command or dynamic raw object crossing an internal boundary. |

## Review and correction rule

- Reviewer executes H1..H8 once and batches every finding.
- One failed item may receive one additive correction on the same ticket branch,
  worktree, allocation and receipt.
- No review result creates another worktree or same-ticket branch. A failed
  correction review returns `CONVERGENCE_REVIEW_REQUIRED`.

## Required evidence and return

1. First red test and failure reason for H1..H8 before production code.
2. Exact unittest, strict mypy over the five files, in-memory compile, privacy
   sentinel, actual temporary-Git non-interference, H1..H8 reverse mutations,
   `git diff --check`, scope/line checks and clean status.
3. One implementation commit and one separate docs-only handoff commit.
4. No claim that Codex or Claude is live-supported. Discovery of a usable live
   lifecycle returns `CHANGE_DETECTED`; missing authority remains a typed halt,
   not a guessed command or hidden configuration edit.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_03_20260809` |
| Allocation | `aln_local_orchestration_install_03_20260809` |
| Receipt | `rcpt_local_orchestration_install_03_20260809` |
| Correlation / question | `corr-local-orchestration-install-03-20260809` / `q-local-orchestration-install-03-20260809` |
| Authority | Existing owner continuation `PRG-20260809-042`; Ticket-02 close `PRG-20260809-070` |
| Required baseline | The docs-only control commit containing this dispatch |
| Granted scope | Only four production files, one test, H1..H8 verification and implementation/docs-only commits |
| Not granted | Another worktree/branch, live host or command action, Ticket-01/02 change, packaging, merge, push, deployment or schedule action |
