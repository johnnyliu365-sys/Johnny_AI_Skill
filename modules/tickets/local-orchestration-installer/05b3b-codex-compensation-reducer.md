# 05B3B — Pure Codex Compensation Planner and Reducer

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-07 compensation-state seam |
| State | `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3B-01` / B1-B5 |
| Dependency | Integrated 05B1/05B2 at control baseline; ADR-20260811-004; no dependency on 05B3A source |
| Control / implementation / reviewer | Current `main` / task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / independent current `main` reviewer |
| Worktree / branch | Existing `workflow-implementer-2`; new ticket branch from reviewed handoff after owner removes its sole `.mypy_cache` residue |
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
- Only `MAY_EXIST` and `OWNED` schedule removal. Plugin removal precedes
  marketplace removal. Whenever any removal authority exists, the three proof
  steps follow in fixed order.
- `reduce_compensation()` consumes the exact plan and one normalized outcome
  for every planned step in exact order. It cannot call a port or synthesize a
  missing observation.
- Normalized outcomes distinguish confirmed, declared failure, malformed,
  mismatch, residue, proved absence and unproved status without carrying raw
  command/output/path/exception data.
- Marketplace authority clears only on fresh exact marketplace absence.
  Plugin authority clears only when both plugin-list locations and the exact
  installed path are freshly absent. A removal failure remains a failure but
  does not retain authority once all absence proof succeeds.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `B1` | All seven legal 05B1 journal pairs are tabled. The six states reachable from integrated 05B2 produce the exact no-compensation or ordered step tuple; the legal-but-unreachable `(OWNED, PREEXISTING)` pair, cross-request, replayed-attempt, malformed and all nine illegal state pairs reject finitely. |
| `B2` | No-authority and pre-existing states schedule no step. `MAY_EXIST`/`OWNED` schedule only their exact removals, plugin first, followed by all three proof steps. |
| `B3` | Missing, extra, duplicate, reordered, wrong-plan or wrong-step outcomes reject finitely. Every declared failure remains represented while the complete later observation sequence is still required. |
| `B4` | The complete plugin installed/available, marketplace and installed-path truth table clears only freshly proved absence and retains only unresolved current-attempt authority. Foreign/unrelated truth is never modeled as owned residue. |
| `B5` | Results are frozen `COMPENSATION_NOT_REQUIRED`, `COMPENSATED`, `COMPENSATION_FAILED` or pre-reduction `COMPENSATION_BLOCKED`, with ordered unique finite reasons and metadata-only serialization. |

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
- **Truthfulness (class 7 / CR):** independently reverse pre-existing
  authority, removal order, finite-failure completeness, early authority
  clearing and stale-authority retention; every reverse must turn red.

First red must be captured before production source exists. Focused/full
unittest, strict full-tree mypy with a removed external cache, in-memory
compile, source/diff/scope and zero-residue checks are required. One
implementation commit is followed by one WPR-only handoff commit. No port,
callable, live Codex, target-project write, network, Secret, integration, push,
release or deployment is authorized.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3B-01` |
| Handoff | `hnd_local_orchestration_install_05b3b_20260811` |
| Allocation / receipt | `aln_local_orchestration_install_05b3b_20260811` / `rcpt_local_orchestration_install_05b3b_20260811` |
| Correlation / question | `corr-local-orchestration-install-05b3b-20260811` / `q-local-orchestration-install-05b3b-20260811` |
| Side context | `scx-local-orchestration-install-05b3b-20260811-01` |
| Authority | Owner instruction to open and parallelize the independently safe tickets; ADR-20260811-004; convergence record `PRG-20260811-167` |
| Ticket-doc baseline | `f60d90ffba7a8cc2b3c7c7eb7a24fe06883b932d` |
| Expected lane admission | Preserve completed branch `codex/implementation-codex-role-profile-proof-06a` at `f6f186f2071035907e83577c58120e20442023c4`; after removing its sole `.mypy_cache` residue, create `codex/implementation-codex-compensation-reducer-05b3b` from the exact reviewed handoff commit in the same existing worktree. |
| Return | One exact-scope implementation commit, then one `doc/WorkProgressReport.md`-only handoff reserved as unique `PRG-20260811-171`. |

## Initial review record

Review of implementation `e7bdee5b1bcd21d5cbc589f7abed4da156d0fdc8`
and handoff `aab7bf5df0c4501ba30e364fa4c76936412c4282` is
`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-140 through CR-143 are the
complete initial blocking batch. Revision 01 did not freeze the exact proof
order or exact residual current-attempt identity/state; wrong-plan metaclass
equality escapes finite validation and only three of five required reverse
mutations were recorded. No correction or integration is authorized until the
control plane freezes revision 02.
