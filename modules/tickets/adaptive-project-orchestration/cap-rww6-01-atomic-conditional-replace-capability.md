# CAP-RWW6-01 — prove Atomic Conditional Replace capability

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-CAP-RWW6-01-ATOMIC-CONDITIONAL-REPLACE-CAPABILITY` / `CAPABILITY_INVESTIGATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 12 / AC-17R12 and TDD item 25 |
| Requirement / Context / ADR | `PRD-20260828-045` / `CHG-20260828-045` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-12` (`6fa4736f8bb6faae11da93774d432bbc2493c67742f36adc4f0f4dc8b210df93`) / `ADR-20260828-033` |
| State / closure | `OPEN / APPROVED / DISPATCH_REQUIRED`; `CLOSURE-ADAPTIVE-CAP-RWW6-01-ATOMIC-CONDITIONAL-REPLACE-CAPABILITY-01` |
| Opening authority | Project owner, 2026-08-28 (Asia/Taipei): retained RWW6 unchanged and authorized this one capability investigation before any further R09B2 implementation. Decision baseline `db37da8ccfc23a63f90e12444c74ba6fec24633b`; no R09B2 repair, runtime write capability, integration, publication, installation, release or deployment authority is granted. |
| Source baseline / subject | `db37da8ccfc23a63f90e12444c74ba6fec24633b`; read-only subject `library/local_orchestration/target_document_management.py` and the current Python filesystem abstraction. Non-integrated R09B2 candidates `269a911226ba6b849bf304a46829481916b0d97f` and `f99d8369363e1b4f4a230749133c69f81078a428` are adversarial evidence only. |
| Control owner / reviewer | `ticket-review` semantic profile — Sol/high; sole orchestrator, final reviewer and sole integrator. |
| Investigation owner | `implementation-high-assurance` semantic profile — Terra/xhigh. This indivisible investigation crosses Windows native semantics, Linux native semantics and the current abstraction's final-mutation behavior; a `YES` claim has a concurrency/security proof burden. |
| Agent Context / worktree / branch | Allocate `SIDE-CONTEXT-ADAPTIVE-CAP-RWW6-01-20260828-01` in `.worktrees/cap-rww6-01-atomic-conditional-replace-capability`, branch `implement/cap-rww6-01-atomic-conditional-replace-capability`, only after this ticket is integrated. Same-lifetime direct reviewer dispatch and one finite `wait_agent` return; no runner, queue, receipt, descriptor, gateway or host-workspace readback is required or created. |
| Delivery / language | `POC / HIGH_ASSURANCE / HIGH_ASSURANCE_REQUIRED`; Python 3.11 strict typed test-only harnesses, real disposable local repositories/filesystems, `mypy --strict` and no mock-success proof. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This is an evidence-only disposable-filesystem investigation. It must not invoke R09B2 production write paths, mutate a real target, create a plugin/CLI capability, call a provider or make release/deployment effects. |

## Boundary declaration

```johnny-boundary
create = tests/test_atomic_conditional_replace_capability.py
modify = tests/test_atomic_conditional_replace_capability.py
create = modules/element/python/adaptive-project-orchestration/cap-rww6-01-atomic-conditional-replace-capability/
modify = modules/element/python/adaptive-project-orchestration/cap-rww6-01-atomic-conditional-replace-capability/
forbid = library/
forbid = tests/test_target_document_management.py
forbid = tests/test_managed_artifact_planning.py
forbid = tests/test_workflow_artifact_tree.py
forbid = tests/test_managed_artifact_recovery_contracts.py
forbid = tests/test_recoverable_managed_artifact_writer.py
forbid = tests/test_file_lock.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Produce one typed, evidence-only `AtomicConditionalReplaceQualification` for each of these exact
subjects:

1. **Windows** — exact OS/version, filesystem backend and candidate native primitive(s).
2. **Linux** — exact kernel/filesystem backend and candidate native primitive(s).
3. **Current filesystem abstraction** — the existing Python-level operation path used by
   `target_document_management.py`.

Each result is exactly `YES`, `NO` or `CONDITIONAL`, and carries only a bounded platform/backend
identity, native primitive (or `NONE`), race model, finite failure semantics and opaque evidence
reference. `YES` proves that the final replacement or unlink is atomically conditional on the
target still holding the last observed identity. `CONDITIONAL` additionally names all runtime-
detectable constraints and proves that a nonmatching tuple fails closed. `NO` is the required result
for a primitive that cannot meet the final-mutation condition; unavailable test environments are
not silently treated as `YES`, `NO` or a skip—they return `BLOCKED -> HALT /
PLATFORM_PROOF_ENVIRONMENT_UNAVAILABLE` with the exact missing subject.

The current abstraction is expected to be challenged directly: check-then-`os.replace`, `rename`
or `unlink` is not a capability. The test harness may evaluate native primitives only in disposable
repositories/directories. It must never turn a qualified result into a production runtime adapter,
change the R09B2 writer, or treat API documentation as execution proof.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `ACR1` | On an actual Windows tuple, enumerate only the named candidate native primitive(s), record their exact final-mutation condition and prove `YES`, `NO` or `CONDITIONAL` by a disposable real-filesystem reproduction. |
| `ACR2` | On an actual Linux tuple, perform the equivalent kernel/filesystem-specific qualification. A Windows result is never copied to Linux, and vice versa. |
| `ACR3` | The current Python filesystem abstraction receives a final-window adversarial reproduction that acts strictly after the final observed-identity read and before the final replace/unlink. It must qualify `NO` unless a real proved atomic primitive is actually used. |
| `ACR4` | Every positive claim records native primitive, exact backend identity, race model, finite failure semantics and opaque evidence reference; typed construction rejects missing/null/extra fields, unsupported status, a `YES` without a primitive, or a conditional result without runtime-detectable constraints. |
| `ACR5` | A `CONDITIONAL` result's negative environment probe fails closed with no disposable target mutation. A `NO` result cannot be used as a runtime capability. |
| `ACR6` | Focused test, strict type check, compile and exact boundary/index checks pass; no production source or existing regression test changes. |
| `ACM1` | Reverse-mutate the classification guard to call digest-check-plus-ordinary replace/unlink `YES`; `ACR3` turns red, then exact restoration returns green. |
| `ACM2` | Reverse-mutate the `YES` evidence guard to omit the final-window reproduction or native primitive; `ACR4` turns red, then exact restoration returns green. |
| `ACM3` | Reverse-mutate the conditional environment guard to proceed when its backend constraint does not match; `ACR5` turns red, then exact restoration returns green. |

Only a real platform/backend execution may produce a qualification. The investigation owner may use
small, explicit test-only native bindings or helper programs in the disposable test directory where
the exact host supports them; they are not repository runtime source. It must not mock the final
operation, mutate a real workspace, use bypass constructors, casts or dynamic unvalidated maps to
manufacture a `YES` result.

## Required reviewer-owned adversarial evidence

After `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, and after binding the exact candidate
SHA and Closure revision, the Sol/high reviewer dispatches both isolated, read-only Terra/xhigh
evidence lanes. Neither helper may modify, commit, push, dispatch, approve, integrate or execute a
real target/provider/release/deployment effect.

1. **Race proof helper.** Independently attacks the claimed final-mutation boundary: it schedules a
   disposable lock-ignoring mutation after the last observed identity and verifies that an alleged
   `YES` never overwrites or deletes the external bytes.
2. **Platform/security helper.** Independently validates exact platform/backend identity, native
   primitive availability, junction/symlink constraints, `CONDITIONAL` detection and evidence
   provenance; it rejects documentation-only or cross-platform inference.

The reviewer independently reproduces every finding, runs all closure checks, then performs one
additional pre-integration counter-mutation through a door unused by the investigation owner and
helpers. Missing platform proof is a `BLOCKED` investigation result, never an approval to repair
R09B2.

## Verification and return

Investigation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_atomic_conditional_replace_capability.py
py -3.11 -m mypy --strict tests/test_atomic_conditional_replace_capability.py
py -3.11 -m compileall -q tests/test_atomic_conditional_replace_capability.py
git diff --check <ticket-integrated-authority> HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with one typed
qualification/evidence set per executed subject; `BLOCKED -> HALT` naming an unavailable exact
platform/backend proof; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` only for an actual conflict in
AC-17R12. The investigation owner does not commit or push. The reviewer alone commits the exact
candidate, runs the two adversarial lanes, performs the independent counter-mutation and routes the
evidence. No CAP result by itself resumes R09B2; a separate architecture/SPEC decision binds any
future qualified runtime tuple.
