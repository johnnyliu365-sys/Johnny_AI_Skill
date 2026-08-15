# Router R02C3 Bounded Archive and Reusable-library Selection Gate Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `02c3-bounded-library-selection` / `CLOSURE-ADAPTIVE-ROUTER-R02C3-01` ACX1-ACX7 revision `r02c3-01` |
| Dispatch registry | `1e292e2f1524b99fa91f36cb845f718b54087cad` / `PRG-20260815-498` |
| Implementation / handoff | `7f9c678406936e01709165e95d88431857a5aa77` / `e62192514132342cd49d2c0fbfcd1fd69de70df5` (`PRG-20260815-499`) |
| Branch / owner | `codex/implementation-router-library-selection-r02c3` / task `019ffb0c-db88-7303-895c-aecfadde7c8d` |
| Review result | `CHANGES_REQUESTED / EVIDENCE_DEFECT / SAME_BRANCH_CORRECTION` |

Submitted behavior, receipt binding, source scope and type surface are valid. Approval is withheld because ACX6 requires three bounded in-memory semantic reversals to be rejected by the committed source gate; the current source gate accepts all three altered source texts. This is an evidence defect, not a request for new behavior, architecture or a new ticket.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Receipt / ancestry / scope | PASS: `1e292e2` is an ancestor of the WPR handoff; implementation changes exactly four authorized source/test paths and handoff only WPR; three-worktree topology remains. |
| Focused regression | PASS: independently ran library-selection, artifact-tree and Router suites `81/81`. |
| Strict typing / compile | PASS: independent strict mypy `156/156` with external temporary cache removed; in-memory compile `156/156`. |
| Full serial suite | INCONCLUSIVE: independent discovery produced no failure output but reached the 64-second tool limit before an aggregate count; submitted `595/595` is not replayed review evidence. |
| Scope / residue | PASS: `git diff --check`, clean tracked/ignored porcelain and no implementation-worktree cache/runtime/bytecode residue. |

## Mandatory review checks

- **Clear strong types:** PASS for finite kind/family/lifecycle/result models and strict `RouterModel` boundaries.
- **Existing conventions:** PASS for the existing `ArtifactTreeResolver` seam and public exports.
- **Logic / edge behavior:** PASS for archive/reusable happy paths, finite failures and opaque omitted sibling data.
- **Security / performance:** PASS: metadata-only, no body/source loading, dynamic lookup, broad catch, filesystem, Git, Agent, host, network or renderer capability. `XSS_NOT_APPLICABLE`.
- **Test truthfulness:** FAIL for ACX6 semantic-reversal proof.
- **Dependencies / scope:** PASS. No dependency change or out-of-scope implementation path.
- **Specification conformity:** PASS ACX1-ACX5 and ordinary ACX7 checks; FAIL ACX6 until the source gate rejects all three required semantic reversals.

## Finding

**CR-R02C3-001 — `EVIDENCE_DEFECT`, blocking.**

`tests/test_workflow_library_selection.py::_assert_module_source_policy` verifies generic typing/effect tokens but not the frozen semantic predicates. The reviewer mutated `library_selection.py` text only in memory and called the committed source gate:

| Required reversal | Exact source mutation | Current gate result |
| --- | --- | --- |
| Kind/family binding bypass | `if path.family is not expected_family:` → `if False:` | **ACCEPTED** |
| ARCHIVED reusable leaf acceptance | reusable mapping `ACTIVE` → `ARCHIVED` | **ACCEPTED** |
| Unselected-sibling/path binding bypass | `or path.explicit_path_refs != expected_refs` → `or False` | **ACCEPTED** |

The existing `test_acx6_reversal_*` functions submit invalid runtime data to canonical source. They demonstrate normal behavior but do not prove that the committed source gate rejects these altered source forms. No mutated source was written or executed during review.

## Required same-branch correction

Keep ticket, owner, permanent worktree, branch, allocation and receipt. Change only `tests/test_workflow_library_selection.py`, then make one WPR-only handoff. Extend the bounded source gate to assert the exact family rejection predicate, `REUSABLE_MODULE -> ACTIVE` mapping and explicit three-ref/path-node binding predicate. Create those three variants in memory and prove each is rejected without writing or executing mutated source. Retain the generic typing/effect and public-contract checks.

No production-source change, new ticket/branch/worktree, helper, next-ticket work, external effect, push, package/install, Secret, release or deployment is authorized. Re-run the frozen verification matrix; a behavior or scope change is `CHANGE_DETECTED`.

## Correction terminal recheck

| Field | Result / evidence |
| --- | --- |
| Returned correction | Test-only `360b556d29d4f10906dfdd0542a6b772722aff6f`; WPR-only `3f8a1fbc5861acd51122204aadea9542c7d04b66`. Production R02C3 blobs remain unchanged from `7f9c678`. |
| Independent replay | PASS: library-selection/artifact-tree/Router `82/82`; strict mypy `156/156`; in-memory compile `156/156`; each exact review mutation rejects in memory without write or execution. |
| Scope / residue | PASS: correction changes only `tests/test_workflow_library_selection.py`; handoff changes only WPR; diff/ancestry/porcelain/topology/cache readback pass. Submitted serial full evidence is `596/596`. |
| CR-R02C3-001 | CLOSED. The committed source gate binds the frozen family predicate, reusable ACTIVE mapping and explicit path predicate, and dedicated in-memory mutations prove each rejection. |
| Review result | `APPROVED / GUARDED_INTEGRATION_AUTHORIZED` |

Integrate only handoff `3f8a1fbc5861acd51122204aadea9542c7d04b66`. A read-only merge-tree must show no source/test conflict; only an append-only WPR overlap may be resolved by retaining each distinct evidence record once and in order. No push, release, deployment, package/install, target-project, external or Secret effect is authorized.
