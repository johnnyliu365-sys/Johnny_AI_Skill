# 05B4B2A — Codex Registration Transaction Authority

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 transaction seam |
| State | `CHANGES_REQUESTED / CR-150_CORRECTION_REQUIRED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2A-01` / T1 through T8 |
| Dependency | B1 revision 02 approved and integrated by `d7c59349b436d552f2fab457a297e2eac6958093` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Provide one process-local transaction authority that binds an exact B1 pending
decision to one attempt, phase, monotonically increasing generation and opaque
lease. Exactly one caller may atomically start and then complete that phase.
This ticket invokes no registration, proof, compensation, process, filesystem
or oracle operation.

## Frozen design

Create `codex_registration_transaction` as a stateful domain boundary over the
integrated pure B1 reducer:

- The public algebra is closed and strongly typed: phase enum
  `FRESH_PREFLIGHT`, `MARKETPLACE_ADD`, `PLUGIN_ADD`; finite block reasons
  `INVALID_REQUEST`, `DUPLICATE_ATTEMPT`, `INVALID_LEASE`, `REPLAYED`,
  `PHASE_MISMATCH`, `INVALID_RESULT`, `INVALID_STATE`; and distinct variants
  for ready lease, started phase, next ready phase, terminal B1 decision and
  add-phase recovery data. No optional field represents a variant.
- A coordinator instance owns one private `RLock` and its own private attempt
  registry. There is no module-global registry and no caller-supplied store,
  lock, callable or optional port.
- Beginning an exact `CodexRegistrationPortRequest` calls the integrated B1
  begin function, records one exact attempt and returns an opaque phase lease.
  Duplicate current or terminal attempt IDs block finitely.
- The lease is constructed only by the owning coordinator, is immutable and
  refuses shallow/deep copy, pickle/reduce and public construction. Its safe
  metadata exposes only attempt ID, finite phase, positive generation and
  status; metadata is never effect authority.
- `start` validates the exact owning coordinator, current lease, generation,
  phase and stored B1 decision under the lock, then records `STARTED` before it
  returns a started-phase variant containing only the rebuilt B1 pending
  decision plus safe lease metadata. A second, stale, copied, forged,
  cross-coordinator or cross-phase start blocks before caller continuation.
- `complete` is legal once for the exact started lease. It supplies the result
  to integrated `advance_codex_registration`; a next pending decision creates
  a distinct next-ready variant with the next generation lease, while
  proof/compensation/block decisions become a terminal variant with a retained
  attempt tombstone. Old leases remain stale.
- A started marketplace/plugin phase exposes an exact conservative recovery
  snapshot whose current phase is `MAY_EXIST`; fresh preflight carries no
  removal authority. This is data for later B2D composition, not execution.
- Storage lifetime is the coordinator instance lifetime. Terminal attempt IDs
  remain tombstoned until that whole instance is discarded; there is no broad
  clear/delete or per-attempt reopening in this POC ticket.
- B1 pending and terminal values remain reconstructable decision data. Only
  the opaque coordinator-owned lease and matching live registry record grant
  phase admission.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `T1` | First red imports the absent production module and fails with exact `ModuleNotFoundError`; production remains unchanged during that red. |
| `T2` | Exact begin creates generation 1 for fresh preflight and a distinct rebuilt B1 decision. Missing, `None`, empty, whitespace, list, dict, plain-object and constructed-invalid requests block without invoking equality, serialization, repr or effect traps. Duplicate attempt IDs block both while live and after terminal completion. |
| `T3` | One exact lease starts once. A synchronized two-thread duplicate start has exactly one `STARTED` result and one finite replay block; no uncaught exception, deadlock or second continuation occurs. The lock covers validation plus state transition. |
| `T4` | Exact complete advances fresh → marketplace → plugin with generations 1 → 2 → 3, then returns only the exact B1 proof, compensation or blocked terminal decision. Every old lease, repeated complete, wrong phase/result and terminal replay blocks finitely. |
| `T5` | Cross original, shallow/deep copy, pickle attempt, metadata reconstruction, forged object, another coordinator, case/prefix/unrelated attempt ID and generation ±1. Copy/pickle transfer fails synchronously with the declared finite `TypeError`; every fabricated or mismatched value blocks. Only the exact live opaque lease succeeds, and all public dump/repr/metadata contain no operation, callable, raw output, absolute path, Secret or receipt. |
| `T6` | Immediately after marketplace/plugin `start`, before any result is completed, the recovery view binds the exact request/attempt and marks only that current add phase `MAY_EXIST`; fresh preflight grants no removal authority. It is impossible to complete a never-started or already-completed lease. |
| `T7` | Independently reverse (a) atomic duplicate exclusion, (b) generation equality, (c) owning-coordinator identity, (d) terminal tombstone retention and (e) marketplace/plugin conservative recovery. Each named committed test turns red and is restored. |
| `T8` | Focused/full serial unittest, strict full-tree mypy with external no-incremental cache, in-memory compile, source/scope/diff/ancestry and tracked/ignored/cache readbacks pass. Implementation changes only the new module and focused test; handoff changes only WPR. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_transaction.py`.
2. New `tests/test_codex_registration_transaction.py`.

Integrated source/tests/package exports are read-only. Historical rejected 05B
source is immutable evidence only. No numeric line limit is an acceptance
criterion. Return one exact two-path implementation commit followed by one
`doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-218.

No `Any`, `type: ignore`, broad catch, optional/`None` port, dynamic member or
signature lookup, new dependency, another Agent, review/integration, B2B-B2E or
05C work, effect invocation, live Codex/host/target-project/network access,
package, push, release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2A-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2a_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2a_20260812` / `rcpt_local_orchestration_install_05b4b2a_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2a-20260812` / `q-local-orchestration-install-05b4b2a-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2a-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-registration-transaction-authority-05b4b2a` from the exact dispatch-registry commit in that same worktree. |
| Return | Exact two-path implementation commit, then WPR-only PRG-20260812-218. |

Freeze is not dispatch. The exact reviewed freeze commit and a later dispatch
registry commit must be recorded before the implementation lane may switch
branch or edit either authorized path.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `c896bf6f7f130e320eace8996caf4caf65c5de2c`; this ticket; exact T1-T8 |
| Delivery confirmation | Project-owner instruction `開始`; applies only to B2A |
| Lane admission | Idle clean task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; submitted B1 HEAD `918c9aff6333d46576a81c92390d2bdf0b0e9b31`; zero tracked/ignored/cache residue; three-worktree topology unchanged |
| Required branch | Create only `codex/implementation-codex-registration-transaction-authority-05b4b2a` from the commit carrying this dispatch registry in the same worktree; no new worktree, merge, rebase or cherry-pick |
| Authority | `hnd_local_orchestration_install_05b4b2a_20260812`; `aln_local_orchestration_install_05b4b2a_20260812`; `rcpt_local_orchestration_install_05b4b2a_20260812`; `corr-local-orchestration-install-05b4b2a-20260812`; `q-local-orchestration-install-05b4b2a-20260812`; `scx-local-orchestration-install-05b4b2a-20260812-01` |
| Required return | One exact two-path implementation commit satisfying T1-T8, followed by one WPR-only handoff at reserved PRG-20260812-218 |

Any admission mismatch returns typed `HALT` or `CHANGE_DETECTED`. No second
branch/worktree, source path, ticket, Agent, effect, review, integration, push,
release or deployment is admitted.

## Initial independent review

The formal review of implementation `6e05c8edfc1ed8db246052f3c19fd6a89539fdf3`
and handoff `312005e6091e088b225e8c53d39480264f860e19` is
`CHANGES_REQUESTED / IMPLEMENTATION_DEFECT / SAME_CLOSURE_CORRECTION`.
CR-150 maps to existing T5: constructed-invalid metadata can invoke a caller
comparison trap through `status` or a caller hashing trap through
`attempt_id.value` before finite `INVALID_LEASE`. All other T1-T8 review gates
passed. The correction retains this closure, owner, worktree, branch,
allocation, receipt and correlation; no new branch or worktree is allowed.
