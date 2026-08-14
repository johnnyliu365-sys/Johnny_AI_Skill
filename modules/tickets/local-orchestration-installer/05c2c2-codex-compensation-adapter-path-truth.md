# 05C2C2 — Codex Compensation Adapter Installed-Path Truth

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `02` |
| State | `BLOCKED / TICKET_DEFECT / DEPENDENCY_WAIT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C2-01` / M1-M7 |
| Dependency | 05C2C1 review `90dac00e92911f8c49049cf4915373374945332a`; guarded merge `fffbc616ee1870b69845cbcecf37a98e842106d3` |
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
- `OracleAbsent` remains `absent=True`; `OracleInstalledPathPresent` becomes
  `absent=False`; every response rejection retains the existing finite failure
  mapping and no proof.
- Results retain no oracle, callable, request, path, raw output or diagnostic.
  No `Any`, `type: ignore`, optional port, dynamic lookup or broad catch/clear.

## TDD closure

| ID | Required evidence |
| --- | --- |
| `M1` | First red proves exact `OracleInstalledPathPresent` currently reaches the adapter but is rejected as `EVIDENCE_INVALID` instead of producing a false proof. |
| `M2` | Exact admitted absent/present map to true/false with the same rebuilt manifest and one ABSENCE action. |
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

## Planned binding

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

## Dispatch registry

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
