# R03-01 bootstrap implementation review

| Field | Value |
| --- | --- |
| ID / revision / lifecycle | `CR-R03-01-001` / `r01` / `SEALED` |
| Decision | `CHANGES_REQUESTED / TICKET_DEFECT / NON_INTEGRABLE` |
| Ticket / authority | `R03-01-live-artifact-registry-ticket-receipt-store` / `R03-01-CS-01`; Revision 03 AC-24, AC-25, AC-29; Revision 04 bootstrap route |
| Bootstrap provenance | `BDG-R03-01-20260816-001` / `BDA-R03-01-20260816-001` / `BDR-R03-01-20260816-001` |
| Implementation binding | `224b0242df876f6a41fd1b7e8f139195e9f40e42` on `codex/implementation-r03-01-live-receipt-registry`, reviewed against `f84b9e451d0d9840b8cfd10454f789291f4da0d0` |
| Scope readback | `library/workflow_router/live_dispatch_contracts.py`; `library/local_orchestration/live_dispatch_metadata_store.py`; `library/local_orchestration/__init__.py`; `tests/test_live_dispatch_metadata_store.py` |
| XSS / external effect | `XSS_N/A`; no Browser/WebView/JS path; no provider, network, target-project, push, release, or deployment effect reviewed |

## Independent evidence

- Focused `python -B -m unittest tests.test_live_dispatch_metadata_store`: `5/5` passed.
- The ticket's required `python -m mypy --strict library tests` failed before checking the
  changed modules: `tests/staging/environment_core/contracts.py` is discovered as both
  `environment_core.contracts` and `tests.staging.environment_core.contracts`. That file is
  outside the ticket scope and existed at the baseline, so the frozen ticket command cannot be
  satisfied by an implementation limited to this ticket.
- A post-call fail-closed probe supplied a boundary whose `register_artifact` raises `OSError`.
  `LiveDispatchMetadataStore.register_artifact` propagated that exception instead of returning
  `STORAGE_UNAVAILABLE`.
- `git diff --check` passed for the implementation commit. The implementation worktree is now
  dirty only because this independent review accidentally created ignored `.mypy_cache/` and
  `tests/.johnny-runtime/`; this is reviewer-side contamination, not an implementer finding, and
  the control reviewer must not clean another owner's worktree.

## Findings

### CR-R03-01-001 — claimed durable store is only an unchecked delegated boundary

`live_dispatch_metadata_store.py` defines a `Protocol` and forwards all registry and receipt
operations to it. The only boundary exercised by the test is the in-memory `_Boundary` defined
inside the test file. No production installer-owned journal/checkpoint implementation, atomic
write rule, restart persistence, or interruption recovery exists in the authorized production
scope. The test named “survives restart” reconstructs only a second adapter over the same
in-memory fake.

Classification: `IMPLEMENTATION_DEFECT` and `EVIDENCE_DEFECT`. The required observable durable
storage closure is absent; a protocol plus fake is not the closure.

### CR-R03-01-002 — dependency storage failure escapes rather than failing closed

At `live_dispatch_metadata_store.py:118-124` (and equivalent three methods), only
`ValidationError` is converted to a finite rejection. An owned boundary `OSError` escapes at
line 119. This violates the ticket's finite `STORAGE_UNAVAILABLE` contract and its dependency
failure TDD obligation. A correct repair needs a named, finite boundary-failure algebra rather
than a broad catch.

Classification: `IMPLEMENTATION_DEFECT`.

### CR-R03-01-003 — frozen strict-type verification command is not runnable on this baseline

The exact ticket command fails on an unchanged staging fixture before it can verify the ticket's
typed closure. The ticket authorizes neither the required package-base configuration nor the
unrelated fixture correction. It therefore cannot supply its promised strict-mypy evidence under
its own scope.

Classification: `TICKET_DEFECT`.

### CR-R03-01-004 — one Luna ticket combines three separately observable closures

The ticket jointly requires (1) public contract/algebra validation, (2) durable approved-artifact
registry behavior, and (3) durable TicketReceipt CAS behavior. Each has separate state, failure
matrix, persistence proof, composition responsibility, and test seam. They should not have been
treated as one indivisible vertical closure merely because they share metadata. This conclusion
does not depend on file or line count.

Classification: `TICKET_DEFECT`.

## Required re-decomposition route

Do not amend, reset, or reuse this consumed bootstrap grant for a correction. The next admitted
sequence must split the work into these independently observable closures:

1. `R03-01A`: strict public contracts, named IDs, finite status/nullability algebra, and boundary
   serialization validation only.
2. `R03-01B`: installer-owned approved-artifact registry with atomic/restart/interruption proof,
   depending on `R03-01A`.
3. `R03-01C`: installer-owned TicketReceipt issue/read CAS store with one-live-receipt proof,
   depending on `R03-01A` and the reviewed registry identity.

Revision-04 AC-31 allowlists only the immutable R03-01/R03-02/R03-03 revisions. These new IDs or
a revised R03-01 closure cannot be dispatched from this review: they require an Architecture /
CHG revision that explicitly reopens the bootstrap allowlist, updates dependencies, and grants a
new owner-approved bootstrap grant. R03-02 and R03-03 remain blocked.

## Disposition

No integration, receipt issue, normal Router activation, correction dispatch, branch reset,
worktree mutation by the reviewer, push, release, or deployment is authorized. The next Router
event is `TICKET_DEFECT -> ARCHITECTURE / CHANGE_CONTROL` with this exact review leaf.
