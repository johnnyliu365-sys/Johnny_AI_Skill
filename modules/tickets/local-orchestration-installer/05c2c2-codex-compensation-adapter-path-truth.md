# 05C2C2 — Codex Compensation Adapter Installed-Path Truth

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `02` |
| State | `PLANNED / DISPATCH_PENDING` |
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
