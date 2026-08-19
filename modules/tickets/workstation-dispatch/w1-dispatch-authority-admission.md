# W1 — Dispatch Authority Admission

| Field | Value |
| --- | --- |
| State | `OPEN` |
| Baseline | `main` = `cf091c9` |
| Workload | `STANDARD`; issuance is the highest-authority effect in the system, reviewed at `HIGH_ASSURANCE` depth |
| Depends on | governance 02 (containment predicate), E8 closures (facade discipline), E11 (proves the downstream chain is worth feeding) |

## One outcome

Receipt issuance becomes a workstation-process entry with an admission gate,
instead of a test fixture. An owner runs

```text
johnny-router dispatch grant
johnny-router dispatch issue <request.json>
```

and gets a durable, journaled, readback-verified receipt — or a finite typed
refusal. The runner keeps holding only the wake-scoped facade; nothing about
its composition changes.

## Design, stated before implementation

1. **Issuance-scoped facade.** `IssuanceScopedDispatchBoundary` mirrors
   `WakeScopedDispatchBoundary`: it owns the full boundary privately and
   exposes exactly `register_artifact`, `issue_receipt`, `read_receipt`.
   Dispatch code holds this facade and nothing wider; the wake side keeps its
   three methods. Capability held = capability used, per facade.
2. **Owner grant.** A durable dispatch-authority grant in the Johnny root,
   created once by an explicit owner action (`dispatch grant`). Admission
   refuses without it (`DISPATCH_AUTHORITY_ABSENT`). Honesty requirement, in
   the CLOSURE-E8-03 tradition: the grant is an owner-intent marker and audit
   anchor on a single-user machine, **not** a cryptographic boundary — any
   same-process code could create one. The statement of what it does and does
   not guarantee lives in the module docstring, and the real principal
   separation remains this line's later work.
3. **Admission gate**, fail-closed, in order: grant present → request parses
   strictly → worktree containment (`verify_worktree_contained`, the gate
   governance 02's R3 anticipated: a dispatch whose worktree resolves outside
   the repository root is refused `WORKTREE_OUTSIDE_REPOSITORY_ROOT` before
   any effect) → register artifact → issue receipt (store CAS semantics
   untouched; `ALREADY_ISSUED` with an identical receipt is admitted as
   idempotent success, `RECEIPT_CONFLICT` refuses) → **readback**: the issued
   receipt must verify claimable through the read path, or the admission
   reports `ISSUANCE_NOT_READABLE`.
4. **Journal.** Every admission outcome appends one line to a dispatch
   journal in the Johnny root: grant id, host principal, receipt id, worktree
   path, outcome, UTC time. Local paths are admissible there (the install
   journal precedent); receipts and contracts stay metadata-only.
5. **Request shape.** The request reuses the frozen
   `ApprovedDispatchArtifactRecord` plus the issue-only fields
   (`receipt_id`, `correlation_id`, `dispatch_question_id`,
   `worktree_fingerprint`, `branch_fingerprint`) and the two host paths the
   containment gate needs. The `TicketReceiptIssueRequest` is derived from
   the artifact — descriptor fields cannot disagree by construction.
6. **Runner isolation regression.** The runner composition must not import
   the issuance facade or the admission module; pinned by module-surface
   test alongside the existing runtime-binding-identity cells.

## Authorized implementation scope

```text
library/local_orchestration/issuance_scoped_boundary.py
library/local_orchestration/dispatch_authority.py
library/local_orchestration/dispatch_cli.py
library/local_orchestration/johnny_live_cli.py       # one routing addition
tests/test_dispatch_authority.py
modules/tickets/workstation-dispatch/
modules/tickets/workflow-governance/README.md        # note: 02's dispatch gate now wired
```

Deliberately out of scope, recorded as follow-ups: root README documentation
(next release pass), upgrading the E7 runbook to use the real dispatch entry
instead of `_issue_receipt_fixture`, and OS-principal separation.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `W1-R1` | Without a grant, `dispatch issue` refuses `DISPATCH_AUTHORITY_ABSENT` and writes nothing to the checkpoint. `dispatch grant` is idempotent: second call reports `ALREADY_GRANTED` with the same grant id. |
| `W1-R2` | A worktree outside the repository root refuses `WORKTREE_OUTSIDE_REPOSITORY_ROOT` before any store effect; a junctioned path refuses identically (containment predicate reused, not restated). |
| `W1-R3` | A valid request issues: receipt readable, `verify_receipt_claimable` returns `CLAIMABLE`, journal carries the outcome. Re-issuing identically is idempotent (`ALREADY_ISSUED` admitted); a conflicting re-issue refuses without store mutation. |
| `W1-R4` | The full E9 path composes: a receipt issued through admission feeds `build_subscription` successfully — the fixture-free dispatch chain exists end to end. |
| `W1-R5` | Runner isolation: the runner composition binds no issuance-scoped object (module-surface pin plus the existing runtime-identity cells staying green). |
| `W1-R6` | Reverse mutations: removing the grant check turns R1 red; removing the containment call turns R2 red. |
| `W1-R7` | `mypy --strict` clean; full suite green; zero runtime residue. |
