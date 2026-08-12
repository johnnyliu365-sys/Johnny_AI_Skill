# ADR-20260812-005: Registration transaction authority before effects

- Date: `2026-08-12` (Asia/Taipei)
- Status: `ACCEPTED`
- Decision maker: Project owner through continued POC authorization
- Related specification: `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X`
- Related finding: `CR-148 / TICKET_DEFECT` (closed by B1 revision 02)

## Problem

The integrated B1 reducer intentionally treats copied and reconstructed values
as equivalent decision data. It therefore cannot distinguish first use from
replay. The former B2 placeholder tried to add transaction concurrency,
forward effects, proof/receipt, compensation and lifecycle acceptance in one
ticket, recreating the monolithic review surface that caused earlier loops.

## Decision

1. B2A introduces one process-local, coordinator-owned transaction authority.
   It binds attempt, finite phase and monotonically increasing generation to a
   non-transferable one-shot lease and performs atomic start/complete state
   transitions under a private lock. It executes no effects.
2. B2B alone receives the registration capability and performs the three
   forward operations through B2A admission.
3. B2C and B2D separately settle the proof/receipt and compensation paths.
   After B2B is integrated, those two tickets may use the two existing
   implementation worktrees in parallel.
4. B2E proves the complete behavior only in the disposable lifecycle oracle.
   Production code must not import staging-test oracle modules.

The B2A registry and terminal tombstones live for one coordinator instance.
There is no global store or per-attempt clear in the POC. Durable crash recovery
and multi-process coordination require a future requirement/change decision;
they are not silently simulated by Python object identity.

## Consequences

- Atomic duplicate exclusion can be reviewed without any host mutation.
- A started add has conservative `MAY_EXIST` recovery data before caller
  continuation, while fresh preflight grants no removal authority.
- The first two children remain serial; proof and compensation can later be
  parallelized without sharing uncommitted state.
- Rejected 05B source remains historical evidence and is never an input.
- No target project, live Codex state, package, push, release or deployment is
  authorized by this ADR.
