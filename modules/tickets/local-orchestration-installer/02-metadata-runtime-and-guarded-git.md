# 02 — Metadata Runtime and Guarded Git Decision

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-04, AC-05, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `IN_PROGRESS / DISPATCHED` |
| Required dependency | Ticket 01 integrated at `491f98b` and closed at `24387c2` |
| Language | Python 3.11, strict Pydantic models and standard-library fakes |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / existing `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Single implementation branch | `codex/implementation-local-metadata-git-02` |
| Environment | Metadata-only in-memory store and temporary-repository fakes; no company project, host configuration, push or deployment |

## User-observable outcome

An unseen, installation-bound metadata event is claimed once and returns one
finite runtime status. Replay, malformed identity, raw content or a Router/port
failure returns `HALTED` without a Git decision. A registered temporary project
receives `FAST_FORWARD_ALLOWED` only when its opaque project identity, exact
canonical registry entry, clean expected base and exclusive lock all match;
otherwise it returns a stable blocked result without mutation.

## Smallest reusable-module selection

```text
selected: workflow-router-poc@24387c2
why: reuse the public strict ProjectId and finite Router event/status vocabulary
read: library/workflow_router/README.md → __init__.py → contracts.py → profile.py → guarded_integration.py
dependency: Pydantic; existing optional Router dependencies remain unchanged
boundary: do not import GuardedIntegrationCoordinator, fake integration effects, raw ContextPacket or any real Git capability
```

Rejected as unnecessary: the complete Router engine, telemetry, Temporal,
policy-response, audit coordinator and previous Ticket-01 lifecycle history.

## Hard scope ceiling

The complete Ticket-02 production diff is limited to these five files:

```text
library/local_orchestration/__init__.py
library/local_orchestration/runtime_contracts.py
library/local_orchestration/runtime.py
library/local_orchestration/project_registry.py
library/local_orchestration/guarded_git.py
```

The complete Ticket-02 test surface is one file:

```text
tests/test_metadata_runtime_and_guarded_git.py
```

- Ticket-02 production additions/changes must stay at or below 650 non-blank
  lines; the test file must stay at or below 500 non-blank lines.
- Do not modify Ticket-01 contracts, ports, lifecycle, fakes or tests.
- If the frozen closure cannot fit, return `CHANGE_DETECTED`; do not add files,
  phases, recovery engines, branches or worktrees.

## In scope

1. Strict metadata event, checkpoint, registry request, repository snapshot and
   finite runtime/Git-decision models.
2. One synchronous `ResumeOrchestration` use case with injected event store,
   Router, registry, lock and guarded-decision ports.
3. One in-memory metadata store and deterministic temporary-repository fakes.
4. Exact registration/base/lock admission and fast-forward-only decision. The
   decision does not execute Git.
5. Public exports, TDD, strict typing and actual temporary-Git
   non-interference verification.

## Explicitly out of scope

- Real Git commands/subprocesses, merge/reset/commit/push, filesystem mutation
  inside a target project, background worker, crash recovery or retry engine.
- Raw Context/source/prompt/project locator persistence, credentials, tokens,
  Secret/PII, network, database, Temporal, MCP, host lifecycle or installer UI.
- Tickets 03–04 behavior or changes to `library/workflow_router`.

## Frozen acceptance set — `CLOSURE-LOCAL-INSTALL-T02-01`

This is the complete blocking set; review may not add Ticket-02 behavior.

| ID | Required executable evidence |
| --- | --- |
| `D1` | First valid metadata event is claimed once and returns `COMPLETED`; replay returns `HALTED / REPLAYED` with no second Router or Git call. |
| `D2` | A valid event whose Router needs a human returns `NEEDS_USER_ACTION` and performs no Git decision. |
| `D3` | Registry root matrix: exact canonical temporary root is accepted; extra suffix, trailing separator, casing change, encoded separator, `..` and empty locator block before registry/Git effects. |
| `D4` | For event ID, installation ID, project ID, expected base, correlation ID and registry locator: `None`, omitted, empty string, whitespace and empty container are rejected at the strict boundary. |
| `D5` | A direct decision request and the indirect runtime path both require the same installation ID, registered `ProjectId`, exact root, clean expected base and acquired lock. Cross-installation/project, dirty, stale, non-fast-forward and contended cases return stable blocked reasons with zero mutation. |
| `D6` | Exactly four one-shot failures are covered: event claim, Router resume, registry resolve and guarded-decision port. Each returns `HALTED` with one unique internal reason, no uncaught exception and no Git mutation. No Cartesian matrix is required. |
| `D7` | Persisted metadata contains only typed opaque IDs, finite status and revision/evidence digests. Raw source, Context, prompt, locator/path/URI, Secret and PII sentinels never appear. Existing and empty actual temporary Git repositories remain byte-identical with unchanged porcelain across one allowed and one blocked decision. |
| `D8` | Source scan over the five production files finds no `Any`, `type: ignore`, credential/token comparison, subprocess/network/Git command, target-project write or dynamic raw object crossing an internal boundary. |

## Review and correction rule

- Reviewer runs D1..D8 once and batches all findings.
- One failed item may receive one additive correction commit on the same ticket
  branch/worktree/allocation/receipt.
- No review result creates another worktree or another branch for this ticket.
  A second failed review returns `CONVERGENCE_REVIEW_REQUIRED`.

## Required evidence and return

1. First red test name and failure reason for D1..D8 before production code.
2. Exact unittest for `tests.test_metadata_runtime_and_guarded_git`.
3. Strict mypy over the five production files and one test file.
4. In-memory compile, privacy/source sentinel, runtime smoke, actual temporary-Git
   non-interference, D1..D8 reverse-mutation evidence, `git diff --check`,
   scope/line checks and clean status.
5. One Ticket-02 implementation commit and one separate docs-only handoff commit.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_02_20260809` |
| Allocation | `aln_local_orchestration_install_02_20260809` |
| Receipt | `rcpt_local_orchestration_install_02_20260809` |
| Correlation / question | `corr-local-orchestration-install-02-20260809` / `q-local-orchestration-install-02-20260809` |
| Authority | Existing bounded owner continuation `PRG-20260809-042`; Ticket 01 completion `PRG-20260809-066` |
| Required baseline | The docs-only control commit containing this dispatch |
| Granted scope | Only the five production files, one test, D1..D8 verification and implementation/docs-only commits |
| Not granted | Another worktree or Ticket-02 branch, Ticket-01 modification, real Git/host/project effects, Ticket 03+, merge, push, deployment or schedule action |
