# Router R02A Shared Context Lifecycle Gate Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `02a-shared-context-lifecycle-gate` / `CLOSURE-ADAPTIVE-ROUTER-R02A-01` SC1-SC8 revision `r02a-01` |
| Dispatch baseline | `e1880400d5bf3b41c27cc2acdff35329d9f12efa` / `PRG-20260815-460` |
| Implementation | `191135405e2e57f211a9432ed7893dc611221477` |
| Docs-only handoff | `373cf6296312fe83b0029322b8adb5abd33b446d` / `PRG-20260815-461` |
| Branch / owner | `codex/implementation-router-shared-context-r02a` / task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Review result | `CHANGES_REQUESTED / SAME_TICKET_ADDITIVE_CORRECTION` |

The implementation and handoff commits have exact authorized path isolation, additive ancestry
from the dispatch registry, a clean implementation worktree and the required first-red and
reverse-mutation evidence. The finite lifecycle table is otherwise implemented correctly.
Three boundary-validation defects remain and are blocking because they either reject valid
tree/profile metadata or admit a reserved non-revision value.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Immutable review checkout | PASS: repository-external detached clone at exact handoff, removed after verification; the three permanent worktrees were not mutated. |
| Focused / six-module / full | PASS: `40/40`, `107/107`, `543/543`. |
| Strict typing / compile | PASS: strict mypy `150/150`; in-memory compile `150/150`. |
| Decision-table adversarial matrix | PASS: 39 reviewer-owned cells cover context/prior/candidate staleness, supervisor write, sealed change control, every allowed read role/stage, extra-field and duplicate-ref rejection. |
| Profile portability probe | **FAIL:** valid distinct `ctx-another-project` / `cap-another-architecture-owner` metadata is rejected. |
| Tree-index metadata probe | **FAIL:** valid `OpaqueMetadataId` `idx-ticket-current` is rejected solely because it contains `ticket`. |
| Reserved revision probe | **FAIL:** `rev-0000000000000000` is accepted as `expected_current_revision`. |
| Scope / ancestry / residue | PASS: five-path implementation, WPR-only handoff, clean submitted lane, exact registry ancestry, diff check, three-worktree topology and zero submitted residue. |

## Mandatory review checks

- **Clear strong types:** PASS for public enums, models, method parameters and Profile fields.
- **Existing conventions:** PASS for immutable strict Pydantic contracts and public exports.
- **Logic correctness:** PASS for the frozen transition table and precedence; FAIL the three
  metadata-boundary findings below.
- **Edge cases:** PASS for the 39-cell lifecycle matrix; FAIL valid alternate project/profile
  identity and semantically named artifact-index identity.
- **Security / performance:** PASS. The gate is pure and metadata-only with no effect port,
  renderer, subprocess, filesystem, Git, network or broad exception handling.
- **Test coverage / smoke:** PASS submitted reversals and full regression, but the positive
  metadata-equivalence and reserved expected-revision cases are missing.
- **Dependencies:** PASS. No dependency changed.
- **Specification:** FAIL SC1, SC2 and SC6 until the boundary corrections below are proven.

## Findings

**CR-R02A-001 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/profile.py:117-123` promotes the POC builder defaults into global
`ProjectWorkflowProfile` invariants. This rejects every other valid project Context/capability
pair even though the model is the reusable project-specific policy surface. Keep the exact
`ctx-shared-project` / `cap-architecture-owner` values in `build_router_poc_profile()`, but the
model validator must accept any distinct metadata-only pair and reject missing, equal,
locator/file-like, prompt-like and Secret-like values. Add a positive alternate-project pair
beside the existing negative SC2 matrix.

**CR-R02A-002 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/contracts.py:304-328` rejects opaque reference values containing
`raw`, `progress`, `ticket`, `commit`, `test`, `review`, `branch` or `worktree`. The ticket
requires those as forbidden extra fields, not forbidden substrings inside a typed reference;
the schema gate therefore prevents legitimate tree leaves such as `idx-ticket-current` from
appearing in `artifact_index_refs`. Preserve locator/path and prompt/Secret value rejection,
duplicate rejection and strict extra-field rejection, but remove semantic-category substring
filtering. Add positive opaque refs for representative requirement/ticket/review/archive index
identities while retaining the attempted-field matrix.

**CR-R02A-003 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/contracts.py:359-400` validates operation shape but accepts the reserved
all-zero `RevisionDigest` in `expected_current_revision`. The Router advertises already-validated
metadata and manifest/state models reject the same reserved identity, so this malformed value
must fail ordinary request construction for `REVISE_DRAFT`, `SEAL` and `READ_REFERENCE` rather
than entering runtime as `STALE_REVISION`. Add the exact constructor/JSON negative matrix.

## Correction boundary

`CHANGES_REQUESTED`. Retain the exact ticket, implementation task, permanent worktree, branch,
allocation and receipt. Synchronize the new control review baseline into the same branch with
an additive merge; only the expected append-only WPR overlap may be resolved by retaining every
unique PRG record exactly once. Correct only `contracts.py`, `profile.py` and
`test_workflow_router.py`, then one WPR-only handoff. Preserve all existing SC1-SC8 behavior and
re-run focused, six-module, full, strict mypy, compile, source/scope/diff/topology/residue gates
plus three bounded reversals for the corrected profile, tree-ref and all-zero-revision guards.

No ticket refreeze, new branch/worktree, R02B/R02C, 06G0P, package/install, live host, network,
target-project, push, release, deployment or Secret effect is authorized. `XSS_NOT_APPLICABLE`.

## Revision-02 terminal review

| Field | Value |
| --- | --- |
| Guarded sync / correction / handoff | `b361c17b788ce04840ebf164098ea0477a8eeca6` / `f38c212d51b9ebfb9cdcd28742ce316f04a0a771` / `f3ef5a412de84431c0dd0c6e689bd1fec1c535cc` |
| Scope / ancestry | PASS: the predicted WPR-only conflict retained PRG-461..463 once; correction is exactly `contracts.py`, `profile.py`, `test_workflow_router.py`; handoff is WPR-only; lane clean. |
| Implementer evidence | PASS: focused `43/43`, six-module `110/110`, full serial `546/546`, strict mypy `150`, compile `150`, three reversals and zero residue. |
| Terminal result | `CHANGES_REQUESTED / CR-R02A-001_BOUNDARY_CORRECTION` |

CR-R02A-002 and CR-R02A-003 are closed. CR-R02A-001 remains blocking because the revised
Profile validator uses substring marker `"file"`. A valid, distinct metadata-only pair
`ctx-profile-project` / `cap-profile-architecture-owner` is rejected only because `profile`
contains those four letters. The correction must distinguish a hyphen-delimited locator token
(`file-ref`, `ctx-file-uri`) from an ordinary word (`profile`).

Retain the same ticket/lane/bindings. The final additive correction is limited to
`library/workflow_router/profile.py`, `tests/test_workflow_router.py` and one WPR-only handoff.
First-red a positive `profile` pair while retaining negative `file-ref` and `ctx-file-uri`
cases; use boundary-aware typed metadata validation, then reverse that exact guard and rerun all
R02A gates. No other validation, route or lifecycle behavior may change.
