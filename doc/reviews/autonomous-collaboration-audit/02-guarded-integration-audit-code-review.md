# Code Review｜02 — Guarded Main Integration, Event Wake, and Grill Audit

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `afa6da8` (`feat: add guarded integration audit coordinator`) |
| Docs-only handoff | `fd17efa` (`docs: hand off guarded integration audit`) |
| Reviewed branch / owner | `codex/implementation-guarded-integration-audit-02` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/02-guarded-integration-audit.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-6 through AC-8, AC-11 |
| Review baseline | `ad70448` on control-plane `main` |
| Review date | `2026-08-07 (Asia/Taipei)` |

## Scope and evidence reviewed

- Only committed artifacts were reviewed: implementation `afa6da8`, docs-only handoff `fd17efa`, the approved ticket/SPEC, ADR-20260805-002, current Context, and existing tests.
- The submitted branch merge-base is exactly `ad70448`; its submitted range contains only `afa6da8` and `fd17efa`. The implementation worktree was clean before and after review. No implementation file was modified, staged, merged or used from an uncommitted state.
- `afa6da8` adds a typed fake-port coordinator and tests, but passing checks do not override the authorization, pending-audit isolation, Router-composition, and TDD-coverage failures below.

## Independent verification

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | Passed: `80` tests. |
| `python -m mypy --strict --no-incremental library tests` | Passed: `60` source files. |
| In-memory compile of `library/workflow_router/*.py` | Passed: `11` modules. |
| `git diff --check ad70448 afa6da8` | Passed. |
| Direct replay: constructed completed return for an unregistered owner/worktree | Incorrectly integrated and created an audit request. |
| Cross-ticket replay while first integration is `PENDING_AUDIT` | Incorrectly performed a second integration and created a second audit request. |
| Profile probe | Legacy `TICKETS + APPROVAL_GRANTED → IMPLEMENT` remains; required Ticket-01 dispatch/return events are absent. |

## Findings

### CR-12 — A constructed completed return can invoke integration without a dispatched ticket-lane grant

**Impact:** `GuardedIntegrationCoordinator.handle_return()` accepts any shape-valid `ImplementationReturnEvent`. It compares only the event's claimed main revision with `MainSnapshot`; no Router-owned dispatch receipt, reviewed handoff, ticket-lane state, owner, reviewer, branch, worktree or correlation grant is supplied to the coordinator for comparison. An unregistered caller can therefore create a `COMPLETED` event naming the snapshot revision and cause the injected integration port to run. This is a direct authorization bypass of SPEC AC-4 and AC-6, and of the ticket's requirement that integration is only for the matching clean ticket lane.

**Independent reproduction:** A fresh coordinator with no registered receipt/owner/worktree received a constructed event with `implementation_owner_id=unregistered-owner`, `worktree_fingerprint=unregistered-worktree`, a matching revision, and valid metadata shape. It returned `PENDING_AUDIT`; the integration and audit fakes each recorded one call.

**Evidence:** `guarded_integration.py:326-343` receives only a main snapshot and dependent proposals; `:357-430` validates event shape then invokes integration without a trusted lane descriptor. `IntegrationRequest` copies the caller-provided owner, worktree and branch fields. `tests/test_guarded_integration_audit.py` constructs the same kind of return directly and has no forged/unregistered-lane regression.

**Required correction:** Inject or load a Router-owned, receipt-bound ticket-lane descriptor produced by reviewed Ticket 01 contracts. Before any side effect, require an exact match for ticket, positive dispatch receipt/handoff reference, owner, reviewer, worktree, branch, correlation, expected-main revision and lane Context/event identity. A missing, forged, replayed or mismatched value must halt with no proposal wake, integration or audit. Add direct and injected-source bypass tests.

### CR-13 — `PENDING_AUDIT` is ticket-local, so a second ticket can integrate before the first audit resolves

**Impact:** The coordinator blocks an active pending audit only when its ticket equals the new event's ticket. A second ticket with the same old main revision is therefore accepted while the first main revision is still `PENDING_AUDIT`. The second result overwrites `_pending_audit`; the first audit can no longer be consumed. This violates the ticket's one-active-`PENDING_AUDIT` guard and the ADR rule that local `main` must not advance to another dependent operation before audit/review resolution.

**Independent reproduction:** Against one coordinator, a valid event for `ticket-a` returned `PENDING_AUDIT`. Before auditing it, a shape-valid event for `ticket-b` with the same old expected main revision also returned `PENDING_AUDIT`; the fake integration and audit ports each recorded two operations.

**Evidence:** `guarded_integration.py:363-366` checks `self._pending_audit.ticket_reference == event.ticket_reference` instead of rejecting any active audit. `:427` replaces the sole pending record. The main snapshot is never advanced to `integrated_main_revision`, allowing the old revision to remain acceptable after an audit is consumed. `tests/test_guarded_integration_audit.py:192-211` checks only a second return for the same ticket.

**Required correction:** Treat any active `PENDING_AUDIT` as a global local-main integration lock; retain its correlation until the matching audit resolves. Advance the trusted main snapshot to the integrated revision at the defined integration boundary, and require later returns to name that revision. Add tests proving another ticket cannot integrate or overwrite the pending audit, and that old revisions halt after a completed integration.

### CR-14 — The coordinator is not composed with the reviewed Ticket-01 Router contracts or Profile transitions

**Impact:** Ticket 02 explicitly owns profile transitions and a typed implementation-return wake-up. The submitted code adds a separate coordinator but does not change `RouterEventKind`, `RouterState`, `ProjectWorkflowProfile`, `RouterEngine`, or `build_router_poc_profile()`. The actual Profile still advances `TICKETS + APPROVAL_GRANTED` to `IMPLEMENT`, and it has no Ticket-01 dispatch/return events. `CODE_REVIEW` is therefore merely a local enum result, not a Router decision; dependent proposals are marked `WOKEN` but never re-evaluated through the planning lane. The approved two-lane architecture is not executable as one composed POC.

**Evidence:** `profile.py` is unchanged in `afa6da8`; its `TICKETS + APPROVAL_GRANTED → IMPLEMENT` rule remains. `contracts.py` has no `TICKET_DISPATCH_REQUIRED`, `IMPLEMENTATION_DISPATCH_CONFIRMED`, `IMPLEMENTATION_RETURNED`, `INTEGRATION_COMPLETED`, or `AUDIT_COMPLETED` event kind. The independent probe against the submitted branch prints the legacy transition and confirms the dispatch/return event members are absent. `guarded_integration.py:451-462` returns local `CODE_REVIEW`/`CORRECTION` values without a Profile/Router transition.

**Required correction:** Compose the correction against a named reviewed source baseline that actually contains Ticket-01 public contracts; do not merely cite `67b049a` in documentation. Route the validated return, integration result and audit result through the Profile/Router so the planning and ticket lanes preserve their distinct state and no legacy approval route remains. Add an end-to-end fake-port test covering receipt-bound dispatch → return → one `PENDING_AUDIT` → audit → Router `REVIEW` or correction route.

### CR-15 — Required ticket TDD and CodeReview boundary evidence is incomplete

**Impact:** The ticket lists seven forbidden locator forms, null/empty inputs, direct/indirect merge bypass, external/internal error mapping and revision/lock mutation proof. The committed tests cover one Windows-like path string and one raw-context extra field. They do not exercise the seven forms, null/empty variants, constructed-return authorization bypass, cross-ticket pending audit, each adapter result mapping, or a committed reverse/mutation proof. This left CR-12 and CR-13 undetected despite a green suite.

**Evidence:** `tests/test_guarded_integration_audit.py:303-321` contains only `C:/repo/.git` and one extra-field rejection. The seven ticket-mandated forms, blank/container variants and an indirect integration route are absent. The docs-only handoff asserts a temporary mutation result but provides no committed test that independently guards the revisions or global pending-audit invariant.

**Required correction:** Add the TDD cases enumerated in the approved ticket, retain behaviour-specific red evidence, and add reverse/mutation regressions for receipt/lane binding, global pending audit, expected-main revision and lock acquisition/release. Do not weaken the ticket; missing cases are a ticket-evidence correction, not a reason to bypass the guard.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | Models are explicit, but caller-claimed lane metadata is not bound to trusted Router state. |
| Coding and architecture rules | `CHANGES_REQUESTED` | A standalone coordinator bypasses the Profile/Router composition required by the ticket and ADR. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-12 permits an unregistered completed return to start integration. |
| Boundary / exception handling | `CHANGES_REQUESTED` | CR-13 permits a second ticket to overwrite a live pending audit; required failure forms are missing. |
| Security / privacy | `CHANGES_REQUESTED` | Metadata-only fields are preserved, but their provenance is not enforced before integration. |
| Tests / smoke | `CHANGES_REQUESTED` | General regression passes; ticket-specific direct/indirect authorization and isolation behaviour is not proven. |
| Dependencies | `APPROVED` | No dependency change was introduced. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | CR-12 through CR-15 conflict with AC-4 through AC-8, AC-11, the ticket and ADR-20260805-002. |
| CodeReview §2.1 path-prefix CR | `CHANGES_REQUESTED` | One locator string is not the ticket-required seven-form boundary coverage. |
| CodeReview §2.1 authority-bypass CR | `CHANGES_REQUESTED` | The direct constructed-return replay reaches the integration port. |
| CodeReview §2.1 test-coverage CR | `CHANGES_REQUESTED` | The passing tests omit required direct/indirect and mutation evidence. |

## Return and continuation

`afa6da8` and `fd17efa` must not be merged into `main`. Ticket 02 remains `IN_PROGRESS` and automatically returns to its named implementation owner for CR-12 through CR-15. This is `CHANGES_REQUESTED → IMPLEMENT`, not `REQUIREMENT_CHANGED`: the approved scope already requires receipt-bound integration, one global pending audit, Router/Profile composition and the listed TDD evidence.

The correction must use a reviewed source baseline containing Ticket-01 contracts, remain in its own worktree, record new red evidence, rerun regression/type/compile/smoke/diff checks and submit a new implementation plus docs-only handoff. No merge, push, deployment, handoff completion or dependent implementation is authorized. Ticket 03 remains queued and cannot start while Ticket 02 correction is active.
