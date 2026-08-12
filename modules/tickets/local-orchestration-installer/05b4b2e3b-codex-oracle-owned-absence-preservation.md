# 05B4B2E3B — Codex Oracle Owned-Absence Preservation

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `COMPLETED / APPROVED / INTEGRATED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3B-01` / A1-A7 |
| Dependency | 05S4, E1 and E3A integrated |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect basis

The fresh `ABSENCE` action currently deletes the whole oracle state file after
owned removal. That file also owns the persisted foreign-record evidence, so
the action cannot prove E3/E6 foreign preservation. Environment teardown, not
the absence observer, owns deletion of the disposable environment.

## One observable outcome

`ABSENCE` proves only the exact owned marketplace/plugin payloads and records
are absent. It retains the strict oracle state and every foreign record/payload
byte unchanged, returns the fresh foreign plugin-list observation, and only
then yields `OracleAbsent` after parent-side revalidation.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `A1` | First red reproduces state deletion or foreign-evidence loss on an accepted absence run. |
| `A2` | Child absence requires owned collections empty and owned payload paths absent, does not unlink state, and emits the fresh plugin list including foreign records. |
| `A3` | Parent accepts absence only after strict state reload proves owned collections empty and exact owned payload paths absent. |
| `A4` | With no foreign records, state remains valid until ordinary environment teardown; teardown still removes the disposable root completely. |
| `A5` | With foreign marketplace/plugin records, state bytes and both foreign payload bytes are identical before and after absence. |
| `A6` | Missing/tampered state, owned residue, reparse/topology, wrong surface, malformed response or process/cleanup failure returns the existing finite block and never `OracleAbsent`. |
| `A7` | Reverse state retention, foreign-list truth and parent revalidation independently, restore exact blobs, then pass focused/full unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks. |

## Exact source and return

Writable implementation paths only:

1. `tests/staging/codex_lifecycle_oracle/oracle.py`
2. `tests/staging/codex_lifecycle_oracle/oracle_child.py`
3. `tests/test_codex_lifecycle_oracle.py`

No numeric line limit is an acceptance criterion. Return one implementation
commit over exactly those paths, then one `doc/WorkProgressReport.md`-only
handoff reserved as `PRG-20260813-292`.

No adapter/registration/compensation production source, live Codex,
host/network/target-project, other Agent, review/integration, staging push,
package, release or deployment action is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2E3B-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e3b_20260813` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e3b_20260813` / `rcpt_local_orchestration_install_05b4b2e3b_20260813` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e3b-20260813` / `q-local-orchestration-install-05b4b2e3b-20260813` |
| Side context | `scx-local-orchestration-install-05b4b2e3b-20260813-01` |
| Owner / lane | Existing task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-owned-absence-05b4b2e3b` from the exact dispatch commit in the same worktree. |

Freeze is not dispatch. Exact lane/readback and a dispatch registry commit are
required before the implementation owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `7812775067643e803c007d385e249b55d760b006`; exact A1-A7; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner instruction to continue approved small-ticket work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E3B only |
| Lane readback | Idle task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2` clean at submitted HEAD `5e3b3ccca6357ec485376009eecf06f3c4a4dbb7`; zero tracked/ignored/cache residue; exactly three worktrees; target branch absent |
| Branch | Create only `codex/implementation-codex-owned-absence-05b4b2e3b` from the exact commit carrying this registry in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2e3b_20260813`; `aln_local_orchestration_install_05b4b2e3b_20260813`; `rcpt_local_orchestration_install_05b4b2e3b_20260813`; `corr-local-orchestration-install-05b4b2e3b-20260813`; `q-local-orchestration-install-05b4b2e3b-20260813`; `scx-local-orchestration-install-05b4b2e3b-20260813-01` |

This is the single dispatch. Only the three exact implementation paths and a
later WPR-only `PRG-20260813-292` are writable in this lane.
