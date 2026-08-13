# 05C1 — Codex Receipt Removal Request

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03 and AC-07 |
| Revision | `02` — non-high-risk ticket correction before independent review |
| State | `IN_REVIEW / REVISION_02_REFROZEN` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C1-01` / R1-R7 |
| Dependency | 05A/05B and E0-E6 integrated; parent 05C decomposition recorded |
| Profile / XSS | `STANDARD`; one implementation owner, no helper / `XSS_NOT_APPLICABLE` |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

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
- Recursively rebuild the invocation installation ID and root before comparing
  identity. Require the valid installation ID to equal the receipt; the root
  must independently rebuild as the one canonical `InstallRoot`, so a
  noncanonical or constructed-invalid invocation root is `INVALID_INVOCATION`,
  not `RECEIPT_MISMATCH`. Map receipt fields
  exactly: `source_locator -> marketplace_source` and
  `plugin_name -> plugin`; every other field maps one-to-one into
  `CodexCompensationPortManifest`, then into `CodexCompensationPortRequest`.
- Success returns one typed `CodexReceiptRemovalReady` containing the rebuilt
  receipt and request. Failure returns `CodexReceiptRemovalBlocked` with status
  `UNINSTALL_BLOCKED` and only `INVALID_INVOCATION`, `INVALID_RECEIPT` or
  `RECEIPT_MISMATCH`.
- A valid serialize/reload round trip is accepted as the persisted metadata
  identity. A fully valid exact data object is not rejected merely because its
  origin is indistinguishable after construction. Subclass, constructed-invalid
  or missing/extra/private state, `None`, scalar/container substitution,
  invalid path/digest/version/auth and installation mismatch are finite
  zero-effect failures.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | First red is the missing new module; exact integrated receipt produces exact ready receipt/request values. |
| `R2` | Every receipt field maps once and exactly; source/plugin rename mappings are explicitly tested. |
| `R3` | A valid invocation installation ID differing from the valid receipt installation ID returns `RECEIPT_MISMATCH`. There is no second valid `InstallRoot` value. |
| `R4` | Null/scalar/container, missing/extra, subclass, constructed-invalid and extra/private-state matrices return finite invalid results. A noncanonical invocation root is `INVALID_INVOCATION`; an invalid receipt root is `INVALID_RECEIPT`. |
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

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `5c231c51f80d93217c4d775fadd57e6979c5873f`; project-owner standing auto-continue `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact owner | Existing implementer-2 task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; reviewer task remains sole orchestrator. |
| Exact lane readback | Task idle; clean branch `codex/implementation-codex-target-project-isolation-05b4b2e6b` at integrated handoff `183313ec6c43b0ece57df699c0eb17d5fd3413b4`; tracked/ignored porcelain empty; linked git-dir/top-level exact; exactly three worktrees; target 05C1 branch absent. |
| Branch admission | In the same permanent worktree create only `codex/implementation-codex-receipt-removal-request-05c1` at the exact control commit carrying this registry. Do not merge/copy a historical branch, create another worktree, reset, rebase, amend, force, stash or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05c1_20260814_01`; handoff `hnd_local_orchestration_install_05c1_20260814`; allocation `aln_local_orchestration_install_05c1_20260814`; receipt `rcpt_local_orchestration_install_05c1_20260814`; correlation `corr-local-orchestration-install-05c1-20260814`; question `q-local-orchestration-install-05c1-20260814`; side context `scx-local-orchestration-install-05c1-20260814-01`. |
| Return | One implementation commit changing exactly the three frozen paths, then only PRG-20260814-380 in one WPR-only handoff commit. |

This one-use receipt authorizes only R1-R7. The owner cannot orchestrate another
Agent, review/integrate its work, dispatch a next ticket, push/publish staging,
or perform package/build/install/release/deployment work.

## Revision-02 control correction

The revision-01 ticket omitted the mandatory implementation-language field and
asked for a valid root mismatch even though `InstallRoot` admits only the
canonical installer root. Revision 02 records the already-fixed Python 3.11
language and makes root handling reachable and fail-closed: invalid invocation
root is `INVALID_INVOCATION`; invalid receipt root is `INVALID_RECEIPT`;
`RECEIPT_MISMATCH` is reserved for two valid unequal installation IDs. SPEC,
public success mapping, owner, branch, allocation, receipt and correlation are
unchanged. Independent review applies this corrected R1-R7 closure.
