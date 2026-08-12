# 05B4B1 — Pure Codex Registration Forward Reducer

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 registration seam |
| State | `IN_PROGRESS / REVISION_02_CORRECTION_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B1-02` / R2-D1 through R2-D8 |
| Dependency | 05B4A1 approved and integrated by `3399cf934874f3304959ef0b6913548c0d767e01` |
| Owner / worktree | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; no new worktree |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Purely reduce one exact current registration attempt through fresh preflight,
marketplace add and plugin add. The only outputs are the next exact pending
phase, an exact proof request, an exact integrated compensation plan or a
metadata-only finite block. This ticket executes no operation and cannot emit
a receipt, final registration success or host truth.

## Frozen design

Create a closed discriminated state/result algebra in a new
`codex_registration_reducer` module:

- `begin_codex_registration` admits one exact
  `CodexRegistrationPortRequest`, constructs the only legal all-not-attempted
  current journal and returns `CodexFreshPreflightPending`.
- `advance_codex_registration` accepts only an exact current pending-state
  variant and one result for that exact phase. Pending variants are
  `CodexFreshPreflightPending`, `CodexMarketplaceAddPending` and
  `CodexPluginAddPending`.
- Terminal decisions are `CodexRegistrationProofRequired`,
  `CodexRegistrationCompensationRequired` and
  `CodexRegistrationBlocked`. One public closed type alias covers all pending
  and terminal variants; no optional port, callable or dynamic member lookup
  exists.
- Every request/result is rebuilt through the integrated 05B4A/A1 public
  validators. Every add outcome is classified through integrated 05B2. Every
  compensation decision contains the exact required plan returned by
  integrated 05B3B1. Do not duplicate those rules.
- Fresh rejection or malformed fresh truth blocks without compensation.
  Exact fresh acceptance is the only path to marketplace add.
- Exact new marketplace success records `OWNED` and advances to plugin add.
  `already_added=True` records `PREEXISTING` and blocks without removal.
  Exact pre-start marketplace failure blocks with no authority. Exact started
  failure, or an invalid/mismatched return after the marketplace operation was
  invoked, records `MAY_EXIST` and returns its exact compensation plan.
- Exact plugin success records plugin `OWNED` and returns one exact
  `CodexRegistrationProofRequest` constructed from the request plus both
  admitted observations. Plugin pre-start failure compensates the already
  owned marketplace. Plugin started failure, or an invalid/mismatched return
  after invocation, records plugin `MAY_EXIST` and returns the plugin-first
  exact compensation plan.
- A reducer decision is not an effect receipt. Proof execution, receipt issue,
  compensation execution, lifecycle-oracle verification and final success are
  exclusively future 05B4B2 responsibilities.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `D1` | First red imports the absent new production module and fails with `ModuleNotFoundError`; production is unchanged during this red. |
| `D2` | Beginning with the exact request returns one freshly rebuilt pending value and the legal `NOT_ATTEMPTED / NOT_ATTEMPTED` current journal. Missing, `None`, empty, whitespace, list, dict, plain object and constructed-invalid request shapes block finitely before caller equality, serialization or repr traps run. |
| `D3` | Cross exact fresh accepted/rejected, malformed, wrong-version and foreign-request envelopes. Only exact accepted advances to marketplace; every other cell is metadata-only blocked, with no add/compensation authority and no raw request or path leakage. |
| `D4` | Cross marketplace new success, pre-existing success, every integrated pre-start/started failure, malformed return, wrong target and foreign request. New success alone advances with marketplace `OWNED`; pre-existing and pre-start stop without removal; started or untrusted post-call returns produce marketplace `MAY_EXIST` plus the exact integrated compensation plan. |
| `D5` | Cross plugin success, every integrated pre-start/started failure, malformed return, wrong target, foreign request and foreign plugin ID. Exact success alone emits an exact proof request with journal `OWNED / OWNED`; every failure/untrusted post-call result emits the exact marketplace-only or plugin-first compensation plan and never proof/success. |
| `D6` | Phase order is closed: plugin cannot precede marketplace, one result cannot be replayed in another phase, terminal decisions cannot advance, and copied/stale/constructed-invalid state, request, journal or carried marketplace observation blocks before untrusted equality/serialization. Use the finite missing/`None`/empty/whitespace/list/dict/plain-object matrix at each reducer-owned nested seam. |
| `D7` | Independently reverse (a) pre-existing marketplace non-ownership, (b) plugin-before-marketplace rejection, (c) malformed add return conservative compensation and (d) exact expected plugin-ID proof binding. Each isolated reversal turns its named committed test red and is restored. No port method, proof port, compensation operation, process, filesystem, oracle, Codex, host, target-project or network effect runs. |
| `D8` | Focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff and tracked/ignored/cache readbacks pass. The implementation commit changes only the two authorized paths and the return commit changes only `doc/WorkProgressReport.md`. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_reducer.py`.
2. New `tests/test_codex_registration_reducer.py`.

All integrated source, tests and package exports are read-only. Rejected 05B
source is historical evidence only and must not be copied, imported,
cherry-picked or treated as a source. No numeric line count is an acceptance
criterion.

Return one exact two-path implementation commit followed by one
`doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-206. No
`Any`, `type: ignore`, broad catch, optional/`None` port, dynamic member or
signature lookup, new dependency, another Agent, review, integration, 05B4B2
or 05C work, live effect, push, release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B1-01` |
| Handoff | `hnd_local_orchestration_install_05b4b1_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b1_20260812` / `rcpt_local_orchestration_install_05b4b1_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b1-20260812` / `q-local-orchestration-install-05b4b1-20260812` |
| Side context | `scx-local-orchestration-install-05b4b1-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only branch `codex/implementation-codex-registration-reducer-05b4b1` from the exact dispatch-registry commit in the same worktree. |
| Return | Exact two-path implementation commit, then WPR-only PRG-20260812-206. |

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `53255ede9a05676d24db20a78feb0dbd6a39d658`; exact D1-D8 |
| Delivery confirmation | Owner instruction `開始吧`; question `q-local-orchestration-install-05b4b1-20260812` is answered positively for this ticket only |
| Lane admission | Existing idle, clean `workflow-implementer-2` at `30d6bcff91368c162664dc2eef7dee5a7c543950`; three-worktree topology unchanged |
| Required branch | Create only `codex/implementation-codex-registration-reducer-05b4b1` directly from the exact dispatch-registry commit in the same worktree; no merge, rebase, cherry-pick or new worktree |
| Authority | `hnd_local_orchestration_install_05b4b1_20260812`; `aln_local_orchestration_install_05b4b1_20260812`; `rcpt_local_orchestration_install_05b4b1_20260812`; `corr-local-orchestration-install-05b4b1-20260812`; `scx-local-orchestration-install-05b4b1-20260812-01` |

## Stop rule

The independent review after return is terminal for this closure. A blocking
finding stops at `CONVERGENCE_REVIEW_REQUIRED`; it does not automatically open
a correction, new branch/worktree or 05B4B2 dispatch.

## Terminal review — revision 01

Formal review
`doc/reviews/local-orchestration-installer/05b4b1-codex-registration-reducer-code-review.md`
records CR-148. The exact original pending object remains authorized after a
successful advance, so it can be replayed and accepted again. This violates D6.
Because a pure reducer with no authoritative current-generation input cannot
distinguish the first call from the same input replay, the finding is
`TICKET_DEFECT`, not an additive source correction. The submitted commits remain
immutable evidence; no merge, correction, new branch/worktree or 05B4B2 dispatch
is authorized before a reviewed refreeze.

## Convergence resolution — revision 02

CR-148 exposed a responsibility contradiction rather than a product requirement
change. Revision 02 keeps this module a deterministic stateless reducer and
removes reducer-owned Python object identity as an authority claim:

- pending and terminal variants are strict decision data only;
- an exact copied, deep-copied or serialization-round-tripped pending value is
  semantically the same input and reduces to the same metadata decision;
- repeating identical exact inputs is deterministic and never proves whether
  a transaction phase is current or already consumed;
- no B1 value contains or grants a lease, receipt, port or effect capability;
- invalid shapes, wrong phase/results and mismatched nested contracts still
  block finitely through the integrated validators;
- [05B4B2](05b4b2-codex-registration-transaction-coordinator.md) exclusively
  owns current generation, one-shot lease consumption, concurrent replay
  exclusion and effect admission.

This separation permits persistence/reconstruction without pretending that
`id(object)` is durable transaction authority.

## Acceptance Closure Set — revision 02

| ID | Finite completion rule |
| --- | --- |
| `R2-D1` | First red adds the revised pure-data boundary probes before production changes. Exact shallow/deep copy and model-dump reconstruction currently block instead of reducing like the exact original; the named test must fail for those cells. |
| `R2-D2` | Remove reducer-owned `_StateAuthority`, private identity fields and identity admission. No replacement registry, global consumed set, optional token, callable or port may be introduced. |
| `R2-D3` | Original, shallow copy, deep copy and exact model-dump reconstruction of each legal pending phase produce the same public decision data for the same exact result. Repeated exact calls are deterministic. |
| `R2-D4` | Every pending/terminal public dump and repr contains no authority, lease, generation, receipt, callable, raw output or secret. A copied B1 decision is data only and cannot invoke an effect in this module. |
| `R2-D5` | Retain revision-01 D2-D5 request/result, ownership, proof-request and exact compensation-plan matrices unchanged. |
| `R2-D6` | Retain wrong-phase, terminal, malformed, constructed-invalid, nested-trap and cross-request rejection. Remove only the impossible claim that B1 itself knows whether an otherwise exact value was already consumed. |
| `R2-D7` | Independently reverse (a) pure copied-state admission, (b) private identity removal, (c) pre-existing marketplace non-ownership, (d) malformed add conservative compensation and (e) exact expected plugin-ID proof binding. Each named test must turn red and be restored. |
| `R2-D8` | Focused/full serial unittest, strict full-tree mypy with external cache, in-memory compile, source/scope/diff, ancestry and tracked/ignored/cache readbacks pass. Implementation correction changes only the existing reducer and focused test; handoff changes WPR only. |

## Revision-02 allocation plan

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05b4b1_r02_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b1_r02_20260812` / `rcpt_local_orchestration_install_05b4b1_r02_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b1-r02-20260812` / `q-local-orchestration-install-05b4b1-r02-20260812` |
| Side context | `scx-local-orchestration-install-05b4b1-r02-20260812-01` |
| Owner / lane | Same task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`, existing `workflow-implementer-2`, existing branch `codex/implementation-codex-registration-reducer-05b4b1` at immutable handoff `658a8f7e10d955b10a28eeb89133ec7c6b3e05a2`; additive commits only. |
| Return | One exact two-path implementation correction commit, then WPR-only PRG-210. |

No new branch/worktree, reset, amend, force, merge, package/dependency edit,
05B4B2 implementation, another Agent, live effect, push, release or deployment
is authorized.

## Revision-02 dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `cd3e9b6789623bd2a12ff7c69db4d5fcadd1718f`; this ticket; `CLOSURE-LOCAL-INSTALL-T05B4B1-02`; exact R2-D1 through R2-D8 |
| Delivery confirmation | Project-owner instruction `開始` in the control task; applies only to this revision-02 correction |
| Handoff / allocation / receipt | `hnd_local_orchestration_install_05b4b1_r02_20260812` / `aln_local_orchestration_install_05b4b1_r02_20260812` / `rcpt_local_orchestration_install_05b4b1_r02_20260812` |
| Correlation / question / side context | `corr-local-orchestration-install-05b4b1-r02-20260812` / `q-local-orchestration-install-05b4b1-r02-20260812` / `scx-local-orchestration-install-05b4b1-r02-20260812-01` |
| Exact admission | Same task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; existing branch `codex/implementation-codex-registration-reducer-05b4b1`; exact clean submitted HEAD `658a8f7e10d955b10a28eeb89133ec7c6b3e05a2`; additive commits only |
| Exact implementation scope | `library/local_orchestration/codex_registration_reducer.py`; `tests/test_codex_registration_reducer.py` |
| Required return | One exact two-path implementation correction commit satisfying R2-D1 through R2-D8, followed by one WPR-only handoff at reserved `PRG-20260812-210` |

The owner must fail closed with a typed `HALT` or `CHANGE_DETECTED` if any
admission value differs. No new branch/worktree, reset, amend, force, merge,
package/dependency edit, B2 implementation, another Agent, live effect, review,
integration, push, release or deployment is part of this dispatch.
