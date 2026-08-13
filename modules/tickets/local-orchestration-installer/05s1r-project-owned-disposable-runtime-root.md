# 05S1R — Project-owned Disposable Runtime Root Migration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-13 |
| Requirement / ADR | `CHG-20260813-015` / `ADR-20260813-007` |
| State | `PLANNED / OWNER_DISPOSITION_WAIT / NOT_DISPATCHED` |
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
