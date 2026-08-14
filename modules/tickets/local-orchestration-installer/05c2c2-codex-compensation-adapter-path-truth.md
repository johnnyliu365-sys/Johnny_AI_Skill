# 05C2C2 — Codex Compensation Adapter Installed-Path Truth

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `03` |
| State | `COMPLETE / APPROVED / READY_FOR_GUARDED_INTEGRATION` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C2-01` / M1-M7 |
| Dependency | 05C2C1 guarded merge `fffbc616ee1870b69845cbcecf37a98e842106d3`; 05C2C2A approval `6cca1210b51e6d5d5e8105876c993540a12eea21` and guarded merge `1f6532a069fade0bfcf526ad0d49de7a88b281bb` |
| Profile / resource | `STANDARD`; one implementation owner, no helper; serial consumer of the exact 05C2C1 result |
| XSS | `XSS_NOT_APPLICABLE`: typed Python staging adapter only; no renderer or JavaScript context |
| Implementation language | Python 3.11 with explicit Pydantic/dataclass contracts and full-tree `mypy --strict` |

## Reserved observable outcome

Project exact admitted `OracleAbsent` to
`CodexInstalledPathAbsenceProof(absent=True)` and exact admitted
`OracleInstalledPathPresent` to the same manifest-bound proof with
`absent=False`. Every blocked, rejected, malformed, foreign or mismatched value
remains a finite operation failure.

## Frozen contract

- Change only the staging compensation adapter and its direct test.
- Import the exact integrated frozen dataclass
  `OracleInstalledPathPresent(action=OracleAction.ABSENCE)` from 05C2C1; do
  not duplicate, wrap, widen or reinterpret it. The admitted absence/presence
  union is owned by `admit_codex_oracle_response` and remains the only response
  boundary.
- Preserve request revalidation, exact retained request/manifest identity and
  action binding before invoking the oracle.
- Only exact 05C2C1 response admission may create `absent=False`; never infer
  presence from `OracleBlocked`, child exit codes, raw output or generic errors.
- Use the integrated 05C2C2A ordinary strict constructor. The result field is
  exact built-in `bool`; no `model_construct`, cast, coercion, untyped object or
  alternate DTO may bypass the manifest-bound proof contract.
- `OracleAbsent` remains `absent=True`; `OracleInstalledPathPresent` becomes
  `absent=False`; every response rejection retains the existing finite failure
  mapping and no proof.
- Results retain no oracle, callable, request, path, raw output or diagnostic.
  No `Any`, `type: ignore`, optional port, dynamic lookup or broad catch/clear.

## TDD closure

| ID | Required evidence |
| --- | --- |
| `M1` | First red proves exact `OracleInstalledPathPresent` currently reaches the adapter but is rejected as `EVIDENCE_INVALID` instead of producing a false proof. |
| `M2` | Exact admitted absent/present map through the ordinary strict proof constructor to built-in true/false with the same rebuilt manifest and one ABSENCE action; no model bypass is used. |
| `M3` | Blocked/rejected/malformed/wrong-action/subclass/constructed/extra/private matrices remain finite failures. |
| `M4` | Invalid or mismatched request performs zero oracle calls and cannot invoke candidate hooks. |
| `M5` | Exact adapter exceptions preserve the frozen propagation/short-circuit policy. |
| `M6` | Reverse true/false mapping, response admission and request-before-effect; each named test turns red and restores. |
| `M7` | Focused/full serial unittest, strict mypy, compile, source/scope/diff/ancestry, residue and topology pass. |

## Reserved writable scope

1. `tests/staging/codex_lifecycle_oracle/compensation_adapter.py`
2. `tests/test_codex_compensation_oracle_adapter.py`

No other source/test/document path or external effect is authorized. This
ticket is frozen against guarded merge
`fffbc616ee1870b69845cbcecf37a98e842106d3`. There is no numeric line
criterion.

## Revision-02 planned binding (closed)

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2C2-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2c2_20260814_01` / `hnd_local_orchestration_install_05c2c2_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2c2_20260814` / `rcpt_local_orchestration_install_05c2c2_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2c2-20260814` / `q-local-orchestration-install-05c2c2-20260814` |
| Side context | `scx-local-orchestration-install-05c2c2-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

The implementation owner must return one implementation commit changing
exactly the two frozen paths, followed by one WPR-only handoff carrying the
reviewer-reserved progress identifier. It may not self-review/integrate,
orchestrate another Agent, create a worktree, touch live Codex/host/target
project, push/publish staging, package/install, release or deploy.

## Revision-02 dispatch registry (closed)

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS` against exact revision-02 freeze `bb37376ef7bfb3a2615ba68a9e8f0d5e4533ad44`: State, M1-M7, Python 3.11 explicit Pydantic/dataclass contracts plus full-tree `mypy --strict`, `STANDARD` one-owner/no-helper profile, `XSS_NOT_APPLICABLE`, exact two-path scope and all binding identities are explicit. |
| Authority / reviewer | Project-owner standing auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; no helper, subagent or second owner. |
| Released lane readback | Task idle; clean released 05C2C1 branch/head `codex/implementation-codex-oracle-installed-path-presence-05c2c1` / `b625d3991a3d68b630d6a4c1a61c2cb8475eb7ae`; exact top-level/linked git-dir, zero tracked/ignored/cache residue, exactly three worktrees and absent target branch verified. |
| Branch / baseline | In the same permanent worktree create only `codex/implementation-codex-compensation-adapter-path-truth-05c2c2` at the exact control commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force or stash. |
| Binding | Workspace `wsb_local_orchestration_install_05c2c2_20260814_01`; handoff `hnd_local_orchestration_install_05c2c2_20260814`; allocation `aln_local_orchestration_install_05c2c2_20260814`; receipt `rcpt_local_orchestration_install_05c2c2_20260814`; correlation `corr-local-orchestration-install-05c2c2-20260814`; question `q-local-orchestration-install-05c2c2-20260814`; side context `scx-local-orchestration-install-05c2c2-20260814-01`. |
| Return | One implementation commit changing exactly the two frozen source/test paths, then append only reserved `PRG-20260814-408` in one WPR-only handoff commit. |

This receipt authorizes only M1-M7. The implementation owner must mechanically
re-read this exact ticket before first red and return
`HALT / TICKET_SCHEMA_INVALID` if any type, identity, scope or closure field is
missing or different.

## Revision-02 typed HALT

The exact first red reached the integrated `OracleInstalledPathPresent`, but
the requested `CodexInstalledPathAbsenceProof(absent=False)` cannot be
constructed: the existing contract fixes `absent` as `Literal[True]` in
`library/local_orchestration/codex_compensation_port.py`, outside this ticket's
two-path scope. The implementation owner correctly returned
`HALT / TICKET_DEFECT`, created no implementation or PRG-408 handoff commit,
and was instructed to remove only its two-file uncommitted WIP by explicit
reverse patch.

No adapter implementation may resume until child 05C2C2A makes the already
consumed absence predicate truthfully constructible as an exact strict bool,
updates its direct consumers away from `model_construct`, and is independently
approved and integrated. This ticket will then be refrozen as revision 03
against that exact API; its revision-02 receipt is closed and cannot be replayed.

## Revision-03 refreeze

The integrated upstream proof now accepts exact built-in `True` and `False`
through ordinary strict Pydantic construction. The first red remains the
current adapter's exact admitted `OracleInstalledPathPresent` mapping to
`EVIDENCE_INVALID`; it must become a manifest-bound false proof without
changing response admission, request-before-effect ordering or failure policy.

Before implementation, the owner must mechanically prove that
`CodexInstalledPathAbsenceProof(manifest=..., absent=False)` constructs through
the public validator and retains `type(absent) is bool`. A mismatch is a typed
`HALT / TICKET_SCHEMA_INVALID`, not permission to widen types or resurrect
`model_construct`. M1-M7 and the two-path scope remain otherwise unchanged.

### Revision-03 binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2C2-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2c2_r03_20260814_01` / `hnd_local_orchestration_install_05c2c2_r03_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2c2_r03_20260814` / `rcpt_local_orchestration_install_05c2c2_r03_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2c2-r03-20260814` / `q-local-orchestration-install-05c2c2-r03-20260814` |
| Side context | `scx-local-orchestration-install-05c2c2-r03-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; refreeze is not dispatch. |

Revision-02's receipt and reserved PRG-408 remain closed historical evidence.
Revision 03 will receive a fresh exact dispatch registry and reserved handoff;
no identifier from revision 02 may authorize implementation.

### Revision-03 dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS` against exact revision-03 refreeze `08734370f9682496d013e9e38032ec23de421006`: M1-M7, integrated ordinary strict-bool constructor, Python 3.11 explicit Pydantic/dataclass contracts plus full-tree `mypy --strict`, `STANDARD` one-owner/no-helper, `XSS_NOT_APPLICABLE`, exact two-path scope and all fresh binding identities are explicit. |
| Authority / reviewer | Project-owner standing auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; same existing 05C2C2 branch, no helper/subagent/second owner. |
| Lane readback | Task idle; branch/head `codex/implementation-codex-compensation-adapter-path-truth-05c2c2` / `41564b2e1087ede7bc156c68ec4aec715f3fe8bd`; invalid-ticket WIP removed, tracked/ignored/cache/runtime residue zero, exactly three worktrees. The branch head is an exact ancestor of the refreeze. |
| Baseline admission | Fast-forward only the same branch to the exact control commit carrying this registry. Do not merge/copy a historical implementation branch, create another branch/worktree, reset, rebase, amend, force or stash. |
| Binding | Workspace `wsb_local_orchestration_install_05c2c2_r03_20260814_01`; handoff `hnd_local_orchestration_install_05c2c2_r03_20260814`; allocation `aln_local_orchestration_install_05c2c2_r03_20260814`; receipt `rcpt_local_orchestration_install_05c2c2_r03_20260814`; correlation `corr-local-orchestration-install-05c2c2-r03-20260814`; question `q-local-orchestration-install-05c2c2-r03-20260814`; side context `scx-local-orchestration-install-05c2c2-r03-20260814-01`. |
| Return | One implementation commit changing exactly the two frozen source/test paths, then append only reserved `PRG-20260814-416` in one WPR-only handoff commit. |

This receipt authorizes only revision-03 M1-M7. Mechanically re-read the exact
ticket and constructor before the first red; any mismatch returns typed
`HALT / TICKET_SCHEMA_INVALID` without source/test mutation.

### Initial review correction — CR-178

All M1-M7 runtime/type/evidence gates pass. CR-178 is one bounded
`IMPLEMENTATION_DEFECT`: the changed method still documents the old
absence-only contract and its final failure-call indentation is malformed.
Keep the same ticket, revision-03 owner/worktree/branch and binding. Change only
`tests/staging/codex_lifecycle_oracle/compensation_adapter.py`: replace the
false docstring with exact admitted absence/presence path-truth wording and
align the final failure return. No executable token, import, test or other file
may change. Return one additive source-only commit, then reserved
PRG-20260814-419 in one WPR-only handoff commit.

#### CR-178 correction dispatch registry

| Field | Value |
| --- | --- |
| Review / authority | Exact review baseline `2f3ba13ee12529cb4d35615073685032f72e5ea6`; standing project-owner auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact lane | Existing owner task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; same branch `codex/implementation-codex-compensation-adapter-path-truth-05c2c2`; clean head `019e287d860d37c646e85c7bbbdd5d7bfc9f6e34`; exactly three worktrees. |
| Merge admission | Merge the exact control commit carrying this registry into the same branch. The only predicted overlap is append-only `doc/WorkProgressReport.md`; preserve PRG-416 through PRG-418 exactly once. Never reset, rebase, amend, force, stash, create another branch/worktree or silently resolve any other conflict. |
| Frozen correction | Change only `tests/staging/codex_lifecycle_oracle/compensation_adapter.py`. Replace the stale absence-only docstring with exact admitted absence/presence path-truth wording and align the final `_operation_failure(...)` argument indentation. No executable token, import, behavior, type, test or other file may change. |
| Immutable proof | Direct-test blob must remain `9c9b24f34fd8145e05ac559f8e4edb8d673ffaab`. Pre-correction source blob is `6ce010db944e30afbd8db291f9c02d6fbdda8219`. Rerun focused `15/15`, strict mypy and in-memory compile; full-suite rerun is optional because the correction is byte-audited non-executable text/whitespace only. |
| Binding / return | Retain revision-03 workspace, handoff, allocation, receipt, correlation, question and side-context without substitution. Return one additive source-only correction commit, then append only reserved `PRG-20260814-419` in one WPR-only handoff commit. |
| Boundary | No helper/subagent, live Codex/host/target-project effect, push/staging publication, package/build/install, Secret, release or deployment. |

### Final correction review

CR-178 is closed by source-only correction
`e801646c4d32401f90aa65784635a2c66445973e` and WPR-only handoff
`9ba22b3f8328ba7fffc5ec767488bcfdab125608`. Independent focused `15/15`,
strict mypy `148`, in-memory compile `148`, direct-test blob identity, exact
diff/scope, clean lane and three-worktree topology pass. Revision-03 M1-M7 are
approved for guarded integration; the receipt grants no other effect.
