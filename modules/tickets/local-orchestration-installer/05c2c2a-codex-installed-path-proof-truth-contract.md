# 05C2C2A — Codex Installed-Path Proof Truth Contract

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `01` |
| State | `PLANNED / DISPATCH_PENDING` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2C2A-01` / T1-T7 |
| Dependency | 05C2C1 guarded merge `fffbc616ee1870b69845cbcecf37a98e842106d3`; 05C2C2 revision-02 typed HALT at dispatch `41564b2e1087ede7bc156c68ec4aec715f3fe8bd` |
| Profile / resource | `STANDARD`; one implementation owner, no helper; serial prerequisite for 05C2C2 revision 03 |
| XSS | `XSS_NOT_APPLICABLE`: typed Python proof contract and direct tests only; no renderer or JavaScript context |
| Implementation language | Python 3.11 with strict Pydantic/domain contracts and full-tree `mypy --strict` |

## Reserved observable outcome

Make the existing manifest-bound absence predicate truthful for both exact
states: `CodexInstalledPathAbsenceProof(absent=True)` means proved absent and
`CodexInstalledPathAbsenceProof(absent=False)` means proved present/residue.
Both are ordinary validated Pydantic construction; no consumer may use
`model_construct` to create a valid truth result.

## Frozen contract

- Change only `CodexInstalledPathAbsenceProof.absent` from `Literal[True]` to
  strict `bool`. Preserve the class name, manifest field, exact Pydantic model
  configuration, five-operation port surface and all existing public names.
- Exact built-in `True` and `False` are the only accepted values. Integers,
  strings, null-equivalent values, collections, subclasses, constructed,
  missing, extra or private state do not become validated proof values.
- Preserve the existing semantic consumer mapping: exact true is
  `PROVED_ABSENT`; exact false is `RESIDUE`; mismatched manifest is `MISMATCH`;
  malformed or declared failure remains finite and non-authorizing.
- Replace only the existing valid-truth `model_construct` shortcuts in the
  direct compensation and receipt-removal composition tests with ordinary
  validated constructors. Keep `model_construct` only where a test explicitly
  creates malformed/adversarial state.
- Do not modify either composition implementation, adapter, oracle, package
  export or any effect boundary. No `Any`, `type: ignore`, internal `object`
  widening, optional port, dynamic lookup or broad catch/clear is allowed.

## TDD closure

| ID | Required evidence |
| --- | --- |
| `T1` | First red proves ordinary construction with `absent=False` fails under the current `Literal[True]` contract. |
| `T2` | Ordinary exact construction accepts built-in true and false, retains an exact rebuilt manifest and serializes the exact bool. |
| `T3` | Strict cells for `0`, `1`, strings, `None`, containers and malformed/extra/private state fail validation or consumer admission without hooks. |
| `T4` | Direct compensation composition maps ordinary true to `PROVED_ABSENT` and ordinary false to `RESIDUE`; manifest mismatch and malformed cells remain exact. |
| `T5` | Direct receipt-removal composition uses ordinary validated true/false proofs for replay, path-only residue and combined residue; ordered removal behavior remains unchanged. |
| `T6` | Reverse the bool contract to the original true-only literal and reverse each consumer's false/residue mapping; governing named tests turn red and exact bytes restore. |
| `T7` | Focused/full serial unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry, residue and three-worktree topology pass. |

CodeReview.md null-equivalent, error consistency, exception, permission,
path/identity and committed-test truthfulness classes apply. This is an exact
contract repair, not a new platform capability.

## Reserved writable scope

1. `library/local_orchestration/codex_compensation_port.py`
2. `tests/test_codex_compensation_port.py`
3. `tests/test_codex_compensation_composition.py`
4. `tests/test_codex_receipt_removal_composition.py`

No other source/test/document path, live Codex/host/target-project effect, new
worktree, helper Agent, branch fan-out, push/staging publication,
package/install, Secret, release or deployment is authorized. There is no
numeric line criterion.

## Planned binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2C2A-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2c2a_20260814_01` / `hnd_local_orchestration_install_05c2c2a_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2c2a_20260814` / `rcpt_local_orchestration_install_05c2c2a_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2c2a-20260814` / `q-local-orchestration-install-05c2c2a-20260814` |
| Side context | `scx-local-orchestration-install-05c2c2a-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

Return one implementation commit changing exactly the four frozen paths,
followed by one WPR-only handoff with the reviewer-reserved progress identifier.
The implementation owner may not self-review/integrate, orchestrate another
Agent, create a worktree, push/publish staging, package/install, release or
deploy.
