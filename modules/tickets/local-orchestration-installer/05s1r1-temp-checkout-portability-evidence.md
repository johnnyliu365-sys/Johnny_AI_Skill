# 05S1R1 — TEMP-checkout Portability Evidence

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-13 |
| Parent / finding | 05S1R terminal correction review `42cfbd65988649d0b1c4b03be4724007afc7de4b` / CR-169 only |
| State | `COMPLETE / APPROVED / INTEGRATED` — merge `d399364` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05S1R1-01` / P1-P4 |
| Dependency | Exact parent handoff `ef69fb8c459309891d53523fc63be33e574b25eb`; CR-167/168 closed |
| Language / profile / XSS | Python 3.11 strict / `COMPACT`, one implementer, no helper / `XSS_NOT_APPLICABLE` |

## One outcome

Make the remaining T1 evidence location-independent and failure-clean so the
exact 05S1R submitted chain passes when the whole plugin checkout is beneath
the system TEMP directory. This ticket changes no allocator or contract
behavior.

## Frozen responsibility

- In `test_t1_two_distinct_owners_provision_unique_direct_project_roots_and_reject_replay`,
  register exact cleanup for both successfully provisioned leases immediately
  after their types are admitted and before any assertion that can fail.
- Replace the broad assertion that the lease is not anywhere beneath
  `tempfile.gettempdir()` with the actual AC-13 condition: its direct parent is
  the checkout-derived `tests/.johnny-runtime`, not the OS-global TEMP root.
- Preserve distinct-owner, replay, malformed-owner, exact overlay and final
  absence evidence. Cleanup may invoke only the allocator's exact marker-bound
  teardown; no direct or broad filesystem delete is added.
- Do not change CR-167/168 production behavior, other tests, source contracts,
  the target project, OS-global staging state or another worktree.

## Authorized implementation scope

```text
tests/test_disposable_environment_core.py
doc/WorkProgressReport.md  # separate PRG-20260813-333 handoff only
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `P1` | First red/source sentinel identifies the remaining broad T1 `is_relative_to(Path(tempfile.gettempdir()).resolve())` assertion at parent handoff `ef69fb8c`; no source mutation precedes it. |
| `P2` | Both exact leases receive cleanup registration before the first post-provision assertion; cleanup uses only the typed allocator teardown and verifies the runtime parent is absent after the final cleanup. |
| `P3` | T1 asserts the exact checkout-derived runtime parent and rejects only a direct OS-global TEMP staging parent. Distinct owners, replay and malformed-owner evidence remain unchanged. |
| `P4` | Focused `10/10` and six-suite `79/79` pass in the implementation worktree with clean runtime/cache/porcelain readback. Independent reviewer then requires fresh checkout-under-TEMP core `10/10`, six-suite `79/79`, full serial, strict typing, compile and final runtime absence before parent integration. |

## TDD / Code Review matrix

- Path-prefix: distinguish `TEMP/johnny-stage-env-*` from
  `TEMP/<checkout>/tests/.johnny-runtime/johnny-stage-env-*`; only the former is
  the forbidden OS-global staging shape.
- Error/exception: an assertion failure after either provision must still run
  exact typed teardown; no cleanup exception may be hidden.
- Test truth: test names claim only direct-parent and exact cleanup behavior;
  reviewer owns the physical checkout-under-TEMP portability proof.
- Scope/XSS/role: one test path only, no Agent control, renderer, DOM,
  JavaScript context or privileged bridge.

## Dispatch registry

| Field | Value |
| --- | --- |
| Delivery authority | Project owner's standing instruction to continue the approved POC workflow plus explicit request for a dispatchable new ticket; `IMPLEMENTATION_DISPATCH_CONFIRMED` for 05S1R1 only. |
| Product binding | Project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05s1r1_20260813_01`; permanent worktree `wtr_workflow_implementation_20260813_01`; readback digest `8a40fd0a9b65bb7c6f08efdd04be22ec8892eb5e11d398ed61cd201f165066d6`. |
| Binding | `hnd_local_orchestration_install_05s1r1_20260813`; `aln_local_orchestration_install_05s1r1_20260813`; `rcpt_local_orchestration_install_05s1r1_20260813`; `corr-local-orchestration-install-05s1r1-20260813`; `q-local-orchestration-install-05s1r1-20260813`; `scx-local-orchestration-install-05s1r1-20260813-01`. |
| Exact source base | Clean parent handoff `ef69fb8c459309891d53523fc63be33e574b25eb`; control registry is the commit carrying this ticket. |
| Branch | Create only `codex/implementation-temp-checkout-portability-05s1r1` from exact parent handoff `ef69fb8c` in the same permanent implementation worktree. No new worktree. |

The receipt cannot authorize production changes, OS-global staging cleanup,
E3D/E4, another owner/task, helper Agent, package/build/install, push, release or
deployment. The implementation owner cannot control another Agent.

## Independent review

Review `doc/reviews/local-orchestration-installer/05s1r1-temp-checkout-portability-evidence-code-review.md`
approves exact implementation `d024e69a6c3ba06a0a2697a37bb19fbde1e657ea`
and WPR-only handoff `3488efea3f431cd0215b3be1fd79c4c533c9932e`.
A fresh physical checkout beneath system TEMP passed core `10/10`, six-suite
`79/79`, full `414/414`, strict mypy and compile `134/134`; a forced
post-admission assertion failure left the project runtime absent. Guarded
integration of the complete parent-plus-child branch is the only continuation.
