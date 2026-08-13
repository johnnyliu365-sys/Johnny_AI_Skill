# 05C1 — Codex Receipt Removal Request

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03 and AC-07 |
| State | `FROZEN / READY_FOR_LANE_ADMISSION` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C1-01` / R1-R7 |
| Dependency | 05A/05B and E0-E6 integrated; parent 05C decomposition recorded |
| Profile / XSS | `STANDARD`; one implementation owner, no helper / `XSS_NOT_APPLICABLE` |

## One observable outcome

Purely convert one exact persisted `CodexRegistrationReceipt` plus the expected
installation ID and canonical root into one exact
`CodexCompensationPortRequest`. Invalid or mismatched input returns a finite
`UNINSTALL_BLOCKED` reason before any effect boundary exists.

## Frozen design

- Add `library/local_orchestration/codex_receipt_removal_request.py` and its
  direct `tests/test_codex_receipt_removal_request.py`; export only the new
  public contracts from `library/local_orchestration/__init__.py`.
- Public input is one exact `CodexReceiptRemovalInvocation` containing expected
  `InstallationId`, exact `InstallRoot` and exact `CodexRegistrationReceipt`.
  It contains no host, host key, absolute path, callable, port or raw data.
- Public `build_codex_receipt_removal_request(object)` recursively admits only
  the exact invocation and exact receipt/nested value types with fixed declared
  Pydantic state. Rebuild before equality; caller descriptors, equality and
  serialization hooks are never executed.
- Require invocation installation/root to equal the receipt. Map receipt fields
  exactly: `source_locator -> marketplace_source` and
  `plugin_name -> plugin`; every other field maps one-to-one into
  `CodexCompensationPortManifest`, then into `CodexCompensationPortRequest`.
- Success returns one typed `CodexReceiptRemovalReady` containing the rebuilt
  receipt and request. Failure returns `CodexReceiptRemovalBlocked` with status
  `UNINSTALL_BLOCKED` and only `INVALID_INVOCATION`, `INVALID_RECEIPT` or
  `RECEIPT_MISMATCH`.
- A valid serialize/reload round trip is accepted as the persisted metadata
  identity. Subclass, `model_construct`, missing/extra/private state, `None`,
  scalar/container substitution, invalid path/digest/version/auth and
  installation/root mismatch are finite zero-effect failures.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | First red is the missing new module; exact integrated receipt produces exact ready receipt/request values. |
| `R2` | Every receipt field maps once and exactly; source/plugin rename mappings are explicitly tested. |
| `R3` | Invocation installation/root mismatch returns `RECEIPT_MISMATCH`. |
| `R4` | Null/scalar/container, missing/extra, subclass, constructed and extra/private-state matrices return finite invalid results. |
| `R5` | Trap descriptors/equality/serialization are not invoked before exact type/state admission. |
| `R6` | Independently reverse receipt identity gate, source mapping and plugin mapping; each named test turns red and exact bytes restore. |
| `R7` | Focused/full serial unittest, strict full-tree mypy, in-memory compile, source/scope/diff and tracked/ignored/cache readback pass. |

## Exact source and return

Writable implementation paths only:

1. `library/local_orchestration/codex_receipt_removal_request.py`
2. `tests/test_codex_receipt_removal_request.py`
3. export-only `library/local_orchestration/__init__.py`

Return one implementation commit, then one WPR-only handoff commit. No other
source/test/document path, live effect, branch fan-out or numeric line criterion
is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C1-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c1_20260814_01` / `hnd_local_orchestration_install_05c1_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c1_20260814` / `rcpt_local_orchestration_install_05c1_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c1-20260814` / `q-local-orchestration-install-05c1-20260814` |
| Side context | `scx-local-orchestration-install-05c1-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

The reviewer must first admit one exact clean existing implementation lane and
record a second control commit carrying the branch/baseline/owner registry.
