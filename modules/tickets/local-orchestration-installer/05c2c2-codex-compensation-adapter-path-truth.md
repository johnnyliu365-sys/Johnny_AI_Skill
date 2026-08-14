# 05C2C2 — Codex Compensation Adapter Installed-Path Truth

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `01` |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C2-01` / M1-M7 |
| Dependency | 05C2C1 independently approved and integrated |
| Profile / resource | `STANDARD`; one implementation owner, no helper; serial consumer of the exact 05C2C1 result |
| XSS | `XSS_NOT_APPLICABLE`: typed Python staging adapter only; no renderer or JavaScript context |
| Implementation language | Python 3.11 with explicit Pydantic/dataclass contracts and full-tree `mypy --strict` |

## Reserved observable outcome

Project exact admitted `OracleAbsent` to
`CodexInstalledPathAbsenceProof(absent=True)` and exact admitted
`OracleInstalledPathPresent` to the same manifest-bound proof with
`absent=False`. Every blocked, rejected, malformed, foreign or mismatched value
remains a finite operation failure.

## Frozen contract pending dependency readback

- Change only the staging compensation adapter and its direct test.
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
| `M1` | First red proves the adapter cannot project the new exact present result. |
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
ticket will be refrozen against the integrated 05C2C1 API before dispatch.
