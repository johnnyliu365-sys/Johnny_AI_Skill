# R03-01A — Durable live-dispatch metadata boundary correction

## Binding

| Field | Value |
| --- | --- |
| Approved requirement | `modules/spec/receipt-bound-role-supervision.md` AC-01, AC-05, AC-11, AC-13, AC-19 and lines 459–462 |
| Defective implementation baseline | `224b0242df876f6a41fd1b7e8f139195e9f40e42` |
| Owner | Implementer-1 task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Worktree / branch | `AI控制工作workflow-implementation` / `codex/implementation-r03-01-live-receipt-registry` |
| Model for this ticket | `gpt-5.6-terra` / `high`; return to the configured Luna xhigh default after completion |

## Defect and observable completion

`LiveDispatchMetadataStore` currently forwards to an injected Protocol, while its restart test
reuses one in-memory fake. It therefore proves adapter recreation, not durable behavior. Correct
this without changing the approved SPEC: provide one production Johnny-owned metadata boundary
that preserves approved-artifact and canonical `TicketReceipt` state across adapter recreation
and a new Python process.

Two independent writers racing to issue the same project/ticket receipt must produce exactly one
canonical stored receipt. An identical request is idempotent; different bytes conflict. A torn,
truncated, unknown-revision or invalid checkpoint fails closed as `STORAGE_UNAVAILABLE` and is
never silently replaced, repaired or treated as empty.

## Writable scope

Only production source and tests are writable:

```text
library/local_orchestration/live_dispatch_metadata_boundary.py
library/local_orchestration/live_dispatch_metadata_store.py
library/local_orchestration/__init__.py
library/workflow_router/live_dispatch_contracts.py
tests/test_live_dispatch_metadata_boundary.py
tests/test_live_dispatch_metadata_store.py
```

Do not add or modify SPEC, Workflow, AGENTS, README, Context, progress, handoff, review, ADR,
requirement or telemetry files. Do not create a WPR-only commit.

## Implementation contract

- The composition supplies an already resolved, validated Johnny-owned storage root through a
  named type. The boundary must not derive a target-project path, read environment variables or
  persist raw source paths, prompts, Context, Secrets or PII.
- Persist one versioned, strict, deterministic checkpoint containing only the approved artifact
  records, canonical receipts and the minimum generation/schema metadata.
- Serialize every value through the existing strict contracts; reject unknown/extra/coerced
  values and unknown schema revisions.
- Protect read-modify-write with an OS-visible exclusive lock that works across independent
  processes on Windows. Commit by same-directory temporary write, flush, file sync and atomic
  replace; leave no temporary file after success.
- Never hold authority only in a module dictionary, singleton or test fake. An in-memory fake may
  exist only inside tests.
- Registration and issuance preserve the finite result algebra already exposed by
  `LiveDispatchMetadataStore`; filesystem/lock/parse/write failures map to
  `STORAGE_UNAVAILABLE` without leaking host details.
- No polling, heartbeat, scheduler, recurring timer, network/database/service, Git/thread/task
  call or target-project mutation.
- Keep strict named types and `mypy --strict`; no `Any`, implicit `any`, `object`, cast,
  `type: ignore`, bypass constructors, dynamic attribute lookup or broad exception catch.

## Executable acceptance

1. First red proves a new boundary instance in a new Python process cannot read state written by
   the current implementation.
2. A real temporary Johnny-owned root proves register → issue → process exit → new process read,
   with byte-identical record and receipt.
3. Two independent processes race with different receipt bytes for one project/ticket: exactly
   one succeeds and the other returns conflict; the final checkpoint contains one active receipt.
4. Repeating identical registration and issuance across process restarts returns the exact prior
   record/receipt without adding another authority record.
5. Injected write interruption before atomic replace leaves the previous checkpoint readable.
   Truncated/invalid/unknown-revision checkpoints return only `STORAGE_UNAVAILABLE` and remain
   byte-for-byte unchanged.
6. Tests prove serialized state contains no repository/worktree path, prompt, Context, Secret or
   PII and leaves no lock/temp/cache/runtime residue after teardown.
7. Existing `tests.test_live_dispatch_metadata_store` remains green.

Run the focused tests, full serial unittest discovery, full-tree strict mypy with an external
removable cache, in-memory compile, `git diff --check`, exact-scope check and final clean-status
readback. Commit only the code/test correction. Return `ACTION_COMPLETED / COMPLETED` with the
implementation commit and exact test counts; do not perform review, merge, dispatch or docs work.
