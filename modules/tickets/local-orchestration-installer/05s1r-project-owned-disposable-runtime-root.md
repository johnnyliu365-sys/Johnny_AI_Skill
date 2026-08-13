# 05S1R — Project-owned Disposable Runtime Root Migration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-13 |
| Requirement / ADR | `CHG-20260813-015` / `ADR-20260813-007` |
| State | `CONVERGENCE_REVIEW_REQUIRED / CHILD_DECOMPOSITION_REQUIRED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05S1R-01` / R1-R8 |
| Dependency | Integrated 05S1-05S4; exact current control freeze; one clean permanent implementation worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One outcome

Migrate the integrated 05S1 test environment from the globally shared OS TEMP
namespace to the exact current plugin checkout's
`tests/.johnny-runtime/` namespace, update every integrated direct caller, and
prove no `%TEMP%/johnny-stage-env-*` root is created.

## Frozen responsibility

- The allocator derives one exact runtime parent from its own checked-out test
  package location. It does not accept a caller path, ambient project path,
  target-project path or serialized absolute locator.
- Each lease remains a unique marker-bound direct child of that parent. All six
  overlay values remain beneath the lease.
- Remove `from_system_temp`; there is no compatibility or fallback route.
- Provision fails finitely before creating a new lease when an unclaimed
  runtime child, unexpected sibling, reparse point or ownership mismatch exists.
  It never deletes that residue.
- Exact teardown may delete only its revalidated lease. It may remove the
  runtime parent afterward only when that parent is empty and exact.
- Add only the exact `/tests/.johnny-runtime/` ignore rule. Final validation
  reads both tracked and ignored porcelain and requires the namespace absent.
- No target project, live Codex, installed user profile, package, global TEMP
  cleanup, network, push, release or deployment is in scope.

## Authorized implementation scope

```text
.gitignore
tests/staging/environment_core/environment.py
tests/test_disposable_environment_core.py
tests/test_bounded_child_process_runner.py
tests/test_codex_agent_profile_capability.py
tests/test_codex_lifecycle_oracle.py
tests/test_codex_protocol_fixture.py
tests/test_codex_registration_oracle_adapter.py
doc/WorkProgressReport.md       # separate docs-only handoff only
```

No other source/test/docs path is writable. In-flight E3D/E4 files remain
separate preserved evidence and may not be copied into this ticket.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | First red proves the current allocator still exposes `from_system_temp` and does not create the project-owned runtime parent. Implementation scope is exactly the frozen paths. |
| `R2` | The allocator derives exactly `<current checkout>/tests/.johnny-runtime` from trusted module location; a caller cannot select or inject another root. The path is inside the plugin checkout and outside every target-project fixture. |
| `R3` | Two distinct owners receive distinct direct lease children beneath that exact runtime parent. Every overlay path is an exact lease descendant and the parent process environment is unchanged. |
| `R4` | No success, failure or fault case creates a `%TEMP%/johnny-stage-env-*` root. An OS-TEMP sentinel manifest remains byte-identical without enumeration-based deletion. |
| `R5` | Exact marker-bound teardown removes only its lease; replay is finite. The runtime parent is removed only when empty. Root/child reparse, marker mismatch and escape still block before external read-through or deletion. |
| `R6` | A pre-existing unclaimed lease, unexpected sibling or malformed runtime parent blocks provisioning and remains byte-identical. No startup cleanup, broad clear or global absence inference exists. |
| `R7` | All integrated direct callers use the project-owned factory and the old factory/symbol is absent from source. Focused dependent suites and the full serial suite pass with final tracked/ignored/runtime readback clean. |
| `R8` | Independently reverse trusted-root derivation, stale-residue admission, exact empty-parent removal and the no-OS-TEMP gate. Each named test turns red and exact blobs restore; strict mypy, in-memory compile, source/XSS/scope/diff/ancestry/topology checks pass. |

## TDD / Code Review matrix

- Path-prefix: exact resolved parents/children only; prefix-similar, parent,
  sibling, traversal, alternate checkout and target-project paths reject.
- Null/equivalent: missing/empty/constructed locator and marker states reject
  finitely; no `None` effect port or optional ownership authority.
- Permission/ownership: only the exact current lease marker grants teardown;
  residue from another owner never grants cleanup authority.
- Error/exception: permission, path length, reparse and delete failures return
  finite results without exception text or false absence.
- Test truth: OS TEMP and target-repository sentinels are measured before/after;
  test names may claim only executed assertions. Ignored residue is explicitly
  read back.
- XSS: `XSS_NOT_APPLICABLE`; no renderer, DOM, JavaScript or privileged bridge.

## Dispatch hold

No owner, allocation, receipt, branch or implementation authority exists yet.
Owner1 currently preserves one uncommitted E4 test correction; owner2 preserves
two uncommitted E3D paths plus Python cache residue. At least one permanent
implementation worktree must be returned to an explicitly owner-authorized
clean state before this ticket can receive a unique dispatch registry. No new
worktree is authorized.

## Owner disposition and dispatch registry

The project owner explicitly approved discarding only owner1's uncommitted E4
test correction and preserving owner2's E3D work. Owner1 performed one
path-scoped restore and returned a clean exact worktree; no folder, branch,
worktree, commit, TEMP or owner2 state changed.

| Field | Value |
| --- | --- |
| Reviewed ticket / handoff | Ticket freeze `9278a75ab2be66fb6fcf610148d639e7ccf30d7f`; reviewed handoff is the control commit carrying this registry. |
| Delivery authority | Project-owner approval of the recommended minimum-waste disposition plus standing instruction to continue the approved workflow; `IMPLEMENTATION_DISPATCH_CONFIRMED` for 05S1R only. |
| Product binding | Project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05s1r_20260813_01`; permanent worktree `wtr_workflow_implementation_20260813_01`; readback digest `89c0158be7376419b4010c7a0de455588013c4c3075bf31423a75a5a7d57d4a1`. |
| Binding | `hnd_local_orchestration_install_05s1r_20260813`; `aln_local_orchestration_install_05s1r_20260813`; `rcpt_local_orchestration_install_05s1r_20260813`; `corr-local-orchestration-install-05s1r-20260813`; `q-local-orchestration-install-05s1r-20260813`; `scx-local-orchestration-install-05s1r-20260813-01`. |
| Branch | Create only `codex/implementation-project-owned-disposable-runtime-05s1r` from the exact registry commit in the same permanent owner1 worktree; no new worktree. |
| Writable paths / handoff | The eight frozen implementation paths plus `.gitignore`, followed by unique `PRG-20260813-325` WPR-only handoff. |

This receipt is one-use and cannot authorize E3D, E4, another owner/task or any
cleanup of owner2/OS TEMP. The implementation owner cannot control an Agent.

## Initial independent review

The exact submitted chain is `fceba609 -> 46dda341 -> b33314ca`; implementation
scope and the WPR-only handoff scope are exact, and the implementation worktree
is clean. Independent verification from an immutable export outside OS TEMP
passed focused `77/77`, full serial `412/412`, strict mypy `134` files and
in-memory compile `134` files. Three frozen-matrix defects remain:

- `CR-167 / IMPLEMENTATION_DEFECT / R5,R8`: a prefix-similar direct child such
  as `johnny-stage-env-prefix-similar` is admitted as an exact owned lease and
  deleted because root admission checks only `startswith`.
- `CR-168 / IMPLEMENTATION_DEFECT / R5,R8`: an exact teardown delete or
  permission failure escapes as `PermissionError` instead of returning a
  finite typed result while preserving the remaining tree.
- `CR-169 / IMPLEMENTATION_DEFECT / R2,R4,R7,R8`: the committed test rejects a
  valid checkout located beneath OS TEMP and performs its first cleanup only
  after that assertion. The resulting test-owned residue causes the remaining
  focused matrix to fail closed, so the test does not prove the location-
  independent checkout-derived contract.

Formal evidence is recorded in
`doc/reviews/local-orchestration-installer/05s1r-project-owned-disposable-runtime-root-code-review.md`.
The review itself creates no integration approval.

## Revision 02 correction freeze and registry

Control review `416e43113b204e8f62da7a63eec5646ba7985bba` authorizes one
additive correction on the same ticket, owner, permanent worktree, branch,
allocation, receipt and correlation. No original implementation or review
commit may be amended, reset, rebased or replaced.

| Field | Value |
| --- | --- |
| Correction handoff | `hnd_local_orchestration_install_05s1r_cr167_169_20260813` |
| Retained binding | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05s1r_20260813_01`; worktree `wtr_workflow_implementation_20260813_01`; branch `codex/implementation-project-owned-disposable-runtime-05s1r`; allocation `aln_local_orchestration_install_05s1r_20260813`; receipt `rcpt_local_orchestration_install_05s1r_20260813`; correlation `corr-local-orchestration-install-05s1r-20260813`. |
| Exact correction base | Clean handoff `b33314ca927532a3c0f74508117b3fd378c90d6a`; review authority `416e43113b204e8f62da7a63eec5646ba7985bba`. |
| Writable implementation paths | `tests/staging/environment_core/contracts.py`, `tests/staging/environment_core/environment.py`, `tests/test_disposable_environment_core.py`; then `doc/WorkProgressReport.md` only in a separate PRG-20260813-330 handoff commit. |

Correction requirements are only the stable finding identifiers:

- `CR-167`: enforce the exact generated direct-child name shape
  `johnny-stage-env-` plus 32 lowercase hexadecimal characters; prefix-similar,
  short, long, non-hex and case-variant names must block before marker read or
  deletion.
- `CR-168`: add the narrow finite `DELETE_FAILED` teardown reason and convert
  exact filesystem cleanup failures into truthful typed results. Do not pop the
  live claim or report absence while any root remains. Provision/fault rollback
  cleanup failures must also remain finite and leave residue fail-closed.
- `CR-169`: remove the invalid assumption that a checkout can never reside
  beneath OS TEMP. Assert only the exact checkout-derived parent and absence of
  a direct OS-global staging child. Register exact teardown before any assertion
  that can fail so a test failure cannot poison later suites.

Run the focused matrix, full serial suite, strict full-tree mypy with external
cache, in-memory compile, exact scope/diff/ancestry/topology/residue checks and
bounded reverse tests for CR-167/168. The independent reviewer alone will run
the final immutable-export checkout-under-TEMP portability probe. No broad
cleanup, OS-global staging enumeration, sibling worktree scan/write, helper
Agent, target-project effect, package/build/install, staging push, release or
deployment is authorized.

## Revision 02 terminal correction review

The exact additive chain is `b33314ca -> 0cca9dee -> ef69fb8c`. Correction
implementation scope is exactly the three authorized paths and the handoff is
WPR-only. An immutable export outside OS TEMP passes the focused matrix
`79/79`, targeted strict mypy `3/3`, compile `134/134`, source/XSS, scope,
ancestry, topology and residue checks. CR-167 and CR-168 are closed.

CR-169 remains open. In a fresh exact checkout below OS TEMP,
`test_t1_two_distinct_owners_provision_unique_direct_project_roots_and_reject_replay`
still fails at its broad `is_relative_to(tempfile.gettempdir())` assertion.
Because both provisioned leases are not registered for cleanup before that
assertion, their residue causes the later physical-junction test and dependent
child-process suites to fail closed. Fresh core result is `8/10` with one
failure and one residue-induced error; the six-suite matrix is `64/79` with
fourteen failures and one error.

Per Workflow section 8.1, the one correction review is terminal. No third
same-ticket correction is permitted. Formal correction evidence is appended to
`doc/reviews/local-orchestration-installer/05s1r-project-owned-disposable-runtime-root-code-review.md`.
The parent must converge through a finite child ticket for CR-169 only.
