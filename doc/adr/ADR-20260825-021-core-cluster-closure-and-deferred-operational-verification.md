# ADR-20260825-021 — Core closure and deferred operational verification

- Date: `2026-08-25 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and Terra supervisor reviewer
- Related change: `PRD-20260825-039` / `CHG-20260825-039`
- Amends: delivery sequencing in `ADR-20260824-020`; it does not weaken that decision's
  authority-line, direct-readback, or provider-enforcement evidence requirements.

## Context

PAI-01 through PAI-05 are pure local source or deterministic fake-port closures. PAI-06 and
PAI-07 were drafted as live provider/repository qualification and publication work. Those effects
are deliberately unapproved, yet their former sequencing prevented an independent assessment of
the already-complete core and encouraged a false choice between fabricating an external effect or
leaving the whole cluster permanently open.

## Decision

1. The core feature is PAI-01 through PAI-05. Its closure evaluates typed authority contracts,
   direct-observation boundaries, guarded push/readback composition, provider-neutral
   high-collaboration evidence, and the three-state bridge distinction.
2. PAI-06 becomes a future, per-project operational qualification. It is needed before a named
   `HIGH_COLLABORATION` project can claim provider enforcement, never as a retroactive global
   capability claim.
3. PAI-07 becomes a future shipped-governance verification. It is needed before a named plugin
   release can claim that its installed payload carries the aligned governance wording.
4. PAI-08 may close the core only with the finite result
   `CORE_CLUSTER_CLOSED_WITH_DEFERRED_OPERATIONAL_VALIDATION`. It is not a release approval and
   does not prove provider enforcement, remote qualification, publication, tag immutability, or
   CLI installation.

## Consequences

The two future tickets retain their precise external-effect admission requirements. No fake port,
local branch, cached remote-tracking ref, chat assertion, or core-cluster review may substitute
for their future live evidence. The independent PAI-08 review gains a truthful completion path
for the local feature while preserving a visible operational backlog rather than an implicit
exception.

## Recovery

If a later PAI-06 or PAI-07 admission lacks its exact owner authority, it remains deferred. A
failed live qualification or publication is reported with its finite failure and never changes
the completed core result. Any change to the authority contract, release process, payload scope,
or external effect restarts change control.
