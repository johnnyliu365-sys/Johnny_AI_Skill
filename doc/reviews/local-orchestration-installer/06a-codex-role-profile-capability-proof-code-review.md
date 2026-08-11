# Ticket 06A Codex Role-profile Capability Proof Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `06a-codex-role-profile-capability-proof` / `CLOSURE-LOCAL-INSTALL-T06A-01` / P1-P4 |
| Reviewed baseline | `1f31accb115a022085a31499f5068227c4f951a0` |
| Implementation / handoff | `38e9a8ba85cf83fbccbcbe2c197f3bedf547a061` / `f6f186f2071035907e83577c58120e20442023c4` |
| Branch / owner | `codex/implementation-codex-role-profile-proof-06a` / task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` |
| Review result | `APPROVED / INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN / INTEGRATION_AUTHORIZED` |

The implementation changes exactly the four new ticket-authorized staging/test
paths, and the handoff changes only `doc/WorkProgressReport.md`. Review used a
fresh immutable ZIP export and did not write the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 11/11 focused and 206/206 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy and in-memory compile over 100 Python files. This reviewer evidence supersedes the handoff's tests-only 38-file mypy run for the full-tree check. |
| P1 profile contracts | PASS: frozen strict reviewer/implementation profiles emit only required fields and opposite finite `agents.enabled` policies. |
| P2 actual capability | FAIL-CLOSED as designed: independent installed-host execution reproduced `ACCESS_DENIED / OUTPUT_UNAVAILABLE`, projected only as `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN`. |
| P3 effective separation | NOT PROVEN on the actual host. Injected `_EffectiveReadback` reaches `SUPPORTED` only as a contract test and is not accepted as host evidence. |
| P4 isolation / teardown | PASS: a true same-name foreign `reviewer-06a.toml` sentinel outside the lease was preserved; owned profiles and disposable root read back absent; existing/empty representative repositories remained byte/porcelain invariant. |
| Scope / ancestry / residue | PASS: exact four-path source scope, one-file handoff, additive ancestry, source sentinel and diff checks. Review export and external cache were removed and read back absent. |

## Mandatory-check mapping

- **Clear strong types:** PASS. Frozen models and finite result/reason unions
  preserve nullability and host-capability distinctions.
- **Existing coding conventions:** PASS. The probe composes integrated 05S1
  and 05S2 boundaries without modifying production source.
- **Logic correctness:** PASS for truthful fail-closed projection. No config
  text or caller-synthesized readback can make the actual host `SUPPORTED`.
- **Edge cases:** PASS for locator variants, malformed/unsupported readback,
  foreign sentinel, cleanup failure and reversed policy regressions.
- **Security / performance:** PASS. Only disposable state was used; no live
  user Codex home, target project, model turn, network or Secret was touched.
- **Test coverage / smoke:** PASS. The independent actual-host probe and
  adversarial probes close the evidence gaps left by the synthetic success cell.
- **Dependency reasonableness:** PASS. No dependency or production source changed.
- **Project specification:** PASS as a capability proof whose allowed outcome
  includes a typed host block; product support itself remains unproven.

## Conclusion

No implementation defect blocks integration of the truthful capability
evidence. `APPROVED / INTEGRATION_AUTHORIZED` applies to the evidence
implementation only. The actual capability outcome is a concrete
`INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN / ACCESS_DENIED /
OUTPUT_UNAVAILABLE` NO-GO. Autonomous Ticket 04 and Tickets 06B/06C must not
be dispatched unless a separately authorized capability change produces new
real-host evidence. No push, release, deployment, live Codex mutation or
target-project write is authorized.

## Guarded integration

Merge `de4141e0d33b42813323587108b20131624ddc93` preserves control review
`62955ecab394534832a40e7bda16f1965b634eaa` as first parent and reviewed
handoff `f6f186f2071035907e83577c58120e20442023c4` as second parent. The
sole conflict was `doc/WorkProgressReport.md`; resolution retained all control
records and normalized the implementation lane's colliding PRG-141 return as
unique PRG-146 without amending the immutable handoff.

Post-merge focused 11/11, full 216/216, strict mypy and in-memory compile over
106 Python files, source sentinel, scope and diff checks passed with zero cache
residue. Ticket 06A is `COMPLETE / APPROVED_EVIDENCE / INSTALL_BLOCKED /
ROLE_ISOLATION_UNPROVEN / INTEGRATED`; its allocation is released and receipt
closed. Downstream capability dependents remain blocked.
