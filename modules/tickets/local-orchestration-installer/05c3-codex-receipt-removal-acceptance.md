# 05C3 — Codex Receipt Removal Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Revision | `03` |
| State | `IN_PROGRESS / CORRECTION_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C3-01` / A1-A8 |
| Dependency | 05C1, 05C2A, 05C2B, 05C2C1, 05C2C2, 05C2C2A and 05C2C3 are independently approved and integrated; 05C2C3 merge is `1e6872acac7df28b5d5bd44991348354a1cd9779` |
| Profile / XSS | `STANDARD`; one implementation owner, no helper / `XSS_NOT_APPLICABLE` |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## Revision-03 frozen responsibility A1-A8

05C3 is an acceptance-only composition over integrated components. It may not
add product behavior, weaken an upstream result or emulate any successful
observation.

| ID | Frozen behavior |
| --- | --- |
| A1 — exact boundary admission | Admit only the exact live disposable lease, oracle and removal request through their integrated public validators. Invalid, subclassed, constructed-invalid, stale or mutually mismatched values halt before every removal or oracle effect. |
| A2 — actual receipt chain | Produce one actual registration-success receipt in the same disposable lease, rebuild the exact removal request through 05C1, and use the real admitted oracle adapter. A fake, copied, historical or separately constructed receipt/request/oracle is forbidden. |
| A3 — remove and replay | First receipt removal returns `REMOVED` and proves every manifest-bound owned plugin, marketplace, logical path and physical payload absent. Replaying the same request returns `NOT_INSTALLED`, performs zero removal actions and leaves oracle state/payload bytes unchanged. |
| A4 — exact action order | The actual effect trace must match the integrated plan exactly, including plugin removal before marketplace removal. Deleted, duplicated, swapped or extra actions must independently turn the governing test red. |
| A5 — foreign preservation | Seed prefix-similar foreign plugin/marketplace records and payload bytes. Registration, removal and replay preserve every foreign identity and byte exactly. |
| A6 — external sentinels | Create two sentinels outside the disposable lease: one existing Git repository and one empty directory. Both remain byte-identical and Git-clean. Sentinel paths must never enter an API, DTO, effect request, overlay or oracle state. |
| A7 — P0 strong type | Every new/changed variable, parameter, return and fixture uses a named explicit type; dynamic boundary values are immediately validated and converted. Ordinary public constructors and public round trips must succeed for valid values. Source forbids `Any`, `type: ignore`, implicit widening, `model_construct`, `model_copy(update=...)`, optional/`None` ports, dynamic member lookup and catch-all exception handling. Test-only malformed bypass is permitted only to prove rejection and may not enter a success path. Full-tree strict mypy is blocking. |
| A8 — truthful red and reversals | The counted first red must reach the real registered-receipt removal behavior; module-import failure is bootstrap evidence only. Independently reverse receipt binding, action order, each owned-absence conjunct, replay zero-removal, foreign isolation, both sentinel isolation gates and every A7 admission gate; each governing test must turn red before exact restoration. |

## Exact acceptance API

```python
def run_receipt_removal_acceptance(
    lease: object,
    oracle: object,
    request: object,
) -> ReceiptRemovalAcceptanceResult: ...
```

`object` is allowed only at this external acceptance boundary. The function
must immediately revalidate and normalize each value into its exact integrated
named type before any property read, comparison, serialization or effect.
Internal variables and helpers may not retain `object` or another dynamic
contract.

## Exact writable scope

- `tests/staging/codex_lifecycle_oracle/receipt_removal_acceptance.py`
- `tests/test_codex_receipt_removal_acceptance.py`

The implementation commit changes exactly those two new files. No production
`library/` path, existing staging fixture, export, document, target project or
other test is writable. There is no line-count ceiling; correctness, explicit
contracts, readable decomposition and complete evidence determine completion.

## First red and mandatory verification

- A missing-module import may document bootstrap only and is not the counted
  first red. The counted red must execute the actual integrated registration
  receipt chain and fail one frozen A1-A8 behavior.
- Focused tests, the full serial suite, full-tree `mypy --strict
  --explicit-package-bases --no-incremental`, in-memory compile and source
  sentinels must pass.
- Each A8 reversal family must turn its named governing test red and then be
  restored byte-for-byte.
- Both external sentinels must be read back unchanged and their exact paths
  absent from every API/DTO/effect/overlay/oracle value.
- Exact two-path implementation scope, ancestry, diff check, three-worktree
  topology and zero tracked/ignored/cache/runtime/bytecode residue are
  mandatory. One implementation commit is followed by one WPR-only handoff.

## Binding reservation

| Field | Value |
| --- | --- |
| Workspace / handoff | `wsb_local_orchestration_install_05c3_r03_20260814_01` / `hnd_local_orchestration_install_05c3_r03_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c3_r03_20260814` / `rcpt_local_orchestration_install_05c3_r03_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c3-r03-20260814` / `q-local-orchestration-install-05c3-r03-20260814` |
| Side context | `scx-local-orchestration-install-05c3-r03-20260814-01` |
| Authority | Standing project-owner auto-continue `PRG-20260809-042`; this reservation is not dispatch authority. |

## Exact dispatch registry

| Field | Value |
| --- | --- |
| Ticket schema gate | `PASS`: revision-03 freezes A1-A8, exact two-path scope, behavior-level first red, explicit ordinary-constructor/P0 type gate, full verification, one owner/no helper, `XSS_NOT_APPLICABLE` and one unique binding. |
| Authority / reviewer | Standing project-owner auto-continue `PRG-20260809-042`; sole reviewer/orchestrator task `019fb935-bbe1-7f71-8b4b-58ba20c81626`. |
| Exact implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; new branch `codex/implementation-codex-receipt-removal-acceptance-05c3` in that same worktree; no helper/subagent/second owner. |
| Lane readback | Idle clean lane at `codex/implementation-codex-compensation-adapter-path-truth-05c2c2` / `9ba22b3f8328ba7fffc5ec767488bcfdab125608`; tracked and ignored porcelain empty; zero repository-local cache/runtime residue; exactly three worktrees. That head is an exact ancestor of the dispatch baseline and the target branch does not exist. |
| Baseline admission | From the exact control commit carrying this registry, create the named branch in the same permanent worktree. Do not merge/copy a historical implementation branch or create another worktree; never reset, rebase, amend, force or stash. Any mismatch returns typed `HALT` before mutation. |
| Binding | Workspace `wsb_local_orchestration_install_05c3_r03_20260814_01`; handoff `hnd_local_orchestration_install_05c3_r03_20260814`; allocation `aln_local_orchestration_install_05c3_r03_20260814`; receipt `rcpt_local_orchestration_install_05c3_r03_20260814`; correlation `corr-local-orchestration-install-05c3-r03-20260814`; question `q-local-orchestration-install-05c3-r03-20260814`; side context `scx-local-orchestration-install-05c3-r03-20260814-01`. |
| Pre-red type gate | Before source mutation, mechanically prove ordinary valid construction and public round-trip for the integrated `EnvironmentLease`, `CodexReceiptRemovalReady`, registration-success receipt and manifest-bound absence proof values used by A1-A3; prove built-in booleans remain `bool`. Any failure is `HALT / TICKET_SCHEMA_INVALID`; no bypass, widening, cast or coercion is allowed. |
| Writable implementation scope | Exactly `tests/staging/codex_lifecycle_oracle/receipt_removal_acceptance.py` and `tests/test_codex_receipt_removal_acceptance.py`. No other implementation path is writable. |
| Return | One implementation commit changing exactly the two frozen paths, then append only reserved `PRG-20260814-430` at physical WPR EOF in one WPR-only handoff commit. Independent review and integration remain reviewer-owned. |

This registry converts the reservation into implementation authority for A1-A8
only. It grants no authority to self-review, integrate, dispatch a next ticket
or invoke a live host/target-project effect.

## Initial review result and same-ticket correction boundary

Initial review of implementation `78cd32da2490e999227f8409c4fcb52eed6e7e37`
and handoff `6f90e65c7206db21c80b03180c92c132b2b2659c` is
`CHANGES_REQUESTED` under the unchanged A1-A8 closure:

- CR-180 (`IMPLEMENTATION_DEFECT`, A7): internal `observed_run` retains
  `object` although only the public acceptance boundary may use it.
- CR-181 (`EVIDENCE_DEFECT`, A6/A8): mutating external sentinel
  `.git/config` bytes keeps the current A6 test green.
- CR-182 (`EVIDENCE_DEFECT`, A7/A8): the committed source gate does not reject
  unauthorized internal `object` or mechanically distinguish the three
  authorized public parameters.

The sole correction keeps revision 03, the same owner/worktree/branch,
allocation, receipt, correlation and exact two-path scope. It must type the
internal command as `OracleCommand`, snapshot the complete external Git
sentinel tree byte-for-byte, and add the bounded AST/source admission described
by the formal review. One additive implementation correction commit is followed
by one appended WPR-only handoff; no other change is authorized.

## CR-180 through CR-182 correction dispatch registry

| Field | Value |
| --- | --- |
| Exact review baseline | `209fd3f7f929aee6cd59ed0fb88e40a15e99c78c`; formal initial review and PRG-431. |
| Lane readback | Exact owner task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; same branch `codex/implementation-codex-receipt-removal-acceptance-05c3`; clean head `6f90e65c7206db21c80b03180c92c132b2b2659c`; exactly three worktrees and zero ignored residue. |
| History-preserving admission | Merge the exact control commit carrying this registry into the same branch. Resolve only the predicted append-only WPR overlap, preserving PRG-430, PRG-431, PRG-432 and all earlier records exactly once in numeric order. No reset, rebase, amend, force, stash, source copy or silent conflict resolution. |
| Exact correction | Change only the two already-authorized 05C3 paths. Type internal `observed_run` with `OracleCommand`; add complete deterministic Git-sentinel tree-byte snapshot before/after acceptance; add committed AST/source admission enforcing the exact three public `object` parameters and all A7 forbidden constructs. |
| Required red / green | Before correction, the AST gate must fail on internal `command_value: object`, and the reviewer `.git/config` mutation must leave the old A6 test green. After correction, the same internal-object reversal and the same Git-config byte mutation must each turn its governing test red, then exact source must pass focused/full serial/strict mypy/compile/source/scope/residue gates. |
| Binding retained | Same workspace, handoff, allocation, receipt, correlation, question and side-context from revision 03; closure A1-A8 unchanged; one owner and no helper. |
| Return | One additive implementation correction commit, then append only reserved `PRG-20260814-433` at physical WPR EOF in one WPR-only handoff. Independent correction review and integration remain reviewer-owned. |

This is the single correction review cycle permitted for revision 03. A second
failure must return `CONVERGENCE_REVIEW_REQUIRED`; it may not trigger another
automatic implementation correction.

## Forbidden effects

No branch or source mutation exists before an exact reviewer-owned dispatch
registry and lane readback. No helper/subagent, new worktree, live Codex/home/
config, target-project, network, push/staging publication, package/build/
install, Secret, release or deployment effect is authorized.
