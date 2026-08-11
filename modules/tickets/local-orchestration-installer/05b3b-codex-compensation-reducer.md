# 05B3B — Pure Codex Compensation Planner and Reducer

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-07 compensation-state seam |
| State | `IN_PROGRESS / REVISION_02_CORRECTION_READY` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3B-02` / R1-R5 |
| Dependency | Integrated 05B1/05B2 at control baseline; ADR-20260811-004; no dependency on 05B3A source |
| Control / implementation / reviewer | Current `main` / task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / independent current `main` reviewer |
| Worktree / branch | Existing `workflow-implementer-2` / existing `codex/implementation-codex-compensation-reducer-05b3b`; additive correction only |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Given an exact integrated 05B1 current-attempt journal, derive one finite
ordered compensation plan; given that plan plus a complete ordered sequence of
normalized observations, return a deterministic result and only the authority
not proved absent. This ticket is pure: it accepts no adapter/callable and
performs no operation, command, path access or host effect.

## Exact source boundary

Only these new paths may change:

1. `library/local_orchestration/codex_compensation_reducer.py`
2. `tests/test_codex_compensation_reducer.py`

All existing source/tests and root exports are read-only. 05B3A is a parallel
contract and may not be read from another worktree or imported before reviewed
integration. Rejected 05B3 source is not an input.

## Public contract and architecture

- `build_compensation_plan()` consumes only an exact revalidated 05B1
  preflight/attempt/journal identity and returns either a finite block, a typed
  no-compensation plan, or an ordered tuple of finite `CodexCompensationStep`.
- Only `MAY_EXIST` and `OWNED` schedule removal. The exact complete step order
  is optional plugin removal, optional marketplace removal,
  `PROVE_PLUGIN_LISTS_ABSENT`, `PROVE_MARKETPLACE_ABSENT`, then
  `PROVE_INSTALLED_LOCATION_ABSENT`. No other order is valid.
- `reduce_compensation()` consumes the exact plan and one normalized outcome
  for every planned step in exact order. It cannot call a port or synthesize a
  missing observation.
- Normalized outcomes distinguish confirmed, declared failure, malformed,
  mismatch, residue, proved absence and unproved status without carrying raw
  command/output/path/exception data.
- Every completed result carries a recursively strict residual journal bound
  to the plan's exact `CodexPreflightRequest` and
  `CodexRegistrationAttemptId`. Its marketplace/plugin states begin as the
  exact original `NOT_ATTEMPTED`, `MAY_EXIST`, `OWNED` or `PREEXISTING`
  values. Marketplace authority changes to `NOT_ATTEMPTED` only on fresh exact
  marketplace absence. Plugin authority changes to `NOT_ATTEMPTED` only when
  both plugin-list locations and the exact installed path are freshly absent.
  `PREEXISTING` and `NOT_ATTEMPTED` remain unchanged. A removal failure remains
  a failure but does not retain authority once all corresponding absence proof
  succeeds. Any derived effect-only view must equal this journal and cannot
  replace it.

## Acceptance Closure Set — revision 02

| ID | Finite completion rule |
| --- | --- |
| `R1` | Preserve the complete revision-01 B1 admission matrix and freeze the exact step tuple named above for every reachable journal pair. No-authority/pre-existing states schedule no step. |
| `R2` | Every completed result contains the exact request/attempt-bound residual journal and exact original per-effect state unless its own fresh absence rule changes it to `NOT_ATTEMPTED`. Cross request/attempt, replay, substituted original state, effect-only collapse and stale/copy plan inputs block finitely. Serialization distinguishes original `MAY_EXIST` from `OWNED` whenever unresolved. |
| `R3` | Missing, extra, duplicate, reordered, wrong-step and wrong-plan outcomes reject finitely. Exact plan validation uses identity-only type checks. Cross a wrong-plan metaclass `__eq__` trap with `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit`; all four complete as `PLAN_INVALID` without invoking equality. |
| `R4` | Independently reverse pre-existing authority, exact proof order, complete-after-failure reduction, early authority clearing and stale-authority retention. Add an independent wrong-plan equality mutation. Each of the six isolated reversals must turn its named test red and be restored. |
| `R5` | Preserve all passing revision-01 truth tables, finite statuses/reasons, frozen metadata-only serialization and pure no-port/no-callable/no-effect behavior. Reduction still requires one normalized outcome for every planned step in exact order. |

## TDD design and CodeReview.md §2.1 mapping

- **Null/empty/container (class 2):** every plan/outcome field rejects null,
  blank and container substitutions; missing/extra sequence cells reject.
- **Authority bypass (class 3):** enumerate all journal pairs and direct/cross-
  request/replay paths; only B2 states schedule removal.
- **Error-code consistency (class 5):** every B1/B3 invalidity has one stable
  finite code and no raw diagnostic text.
- **Exception propagation (class 6):** not applicable to external effects;
  constructed malformed models must return finite blocks rather than raise.
- **Path/token classes (1/4):** no path, URI, credential or token is accepted.
- **Truthfulness (class 7 / CR):** all six R4 reversals are mandatory; the
  handoff must name each red test and restoration.

First red must be captured before production source exists. Focused/full
unittest, strict full-tree mypy with a removed external cache, in-memory
compile, source/diff/scope and zero-residue checks are required. One
implementation commit is followed by one WPR-only handoff commit. No port,
callable, live Codex, target-project write, network, Secret, integration, push,
release or deployment is authorized.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3B-02` |
| Correction handoff | `hnd_local_orchestration_install_05b3b_r02_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b3b_20260811` / `rcpt_local_orchestration_install_05b3b_20260811` |
| Correlation / question | `corr-local-orchestration-install-05b3b-r02-20260812` / `q-local-orchestration-install-05b3b-r02-20260812` |
| Side context | `scx-local-orchestration-install-05b3b-20260812-02` |
| Authority | Owner instruction to continue parallel implementation; ADR-20260811-004 revision 02; review `14fda317538f6661573cf687468f5291ced84ff7` |
| Lane admission | Exact clean submitted HEAD `aab7bf5df0c4501ba30e364fa4c76936412c4282` on the existing branch/worktree. Do not create/switch/reset/rebase/merge/cherry-pick a branch or worktree. |
| Return | One additive exact-scope correction commit, then one `doc/WorkProgressReport.md`-only handoff reserved as unique `PRG-20260812-177`. |

## Initial review record

Review of implementation `e7bdee5b1bcd21d5cbc589f7abed4da156d0fdc8`
and handoff `aab7bf5df0c4501ba30e364fa4c76936412c4282` is
`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-140 through CR-143 are the
complete initial blocking batch. Revision 01 did not freeze the exact proof
order or exact residual current-attempt identity/state; wrong-plan metaclass
equality escapes finite validation and only three of five required reverse
mutations were recorded. Revision 02 above is the complete correction contract
for CR-140 through CR-143. No unrelated hardening, integration or 05B3C work
is authorized.
