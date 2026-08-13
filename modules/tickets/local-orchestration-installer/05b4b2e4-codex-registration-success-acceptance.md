# 05B4B2E4 — Codex Registration Success Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `FROZEN / READY_FOR_DISPATCH` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E4-01` / S1-S8 |
| Dependency | E2 merge `d3d3c1d` plus integrated forward, settlement-authority and proof-settlement modules |
| Planned owner | Exact Local project/task for existing `workflow-implementation`; no new worktree |
| Control / reviewer | Current control task is both ticket author and independent reviewer; it must not implement source/tests |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

In one fresh 05S1 lease, compose the admitted E2 port with integrated forward,
claim and proof settlement. Prove exact command order, persisted owned state,
physical payload truth and one metadata-only registration receipt. Teardown is
environment cleanup only; compensation is not part of this success ticket.

## Frozen design

- Add only
  `tests/staging/codex_lifecycle_oracle/registration_success_acceptance.py`
  and `tests/test_codex_registration_success_acceptance.py`.
- A staging-only acceptance harness receives one exact lease, oracle and
  registration request. It binds E1 identity, creates/admit E2, creates the
  integrated forward coordinator and settlement authority, executes the exact
  fresh-preflight -> marketplace-add -> plugin-add sequence, consumes the exact
  proof claim through the same admitted port and returns a rebuilt finite result.
- Success carries only the existing `CodexRegistrationReceipt` plus typed
  acceptance metadata. It must not retain a live capability, claim, lease,
  oracle, raw response, diagnostic or path outside approved receipt/identity
  values. Failures use existing finite blocked/rejected values or one
  acceptance-specific metadata-only reason; no `None`, broad catch or exception
  text crosses the boundary.
- The success matrix runs in a dedicated child process with the fixed E1 logical
  `%LOCALAPPDATA%` and a unique process-owned temporary base. It may operate only
  inside the exact lease it creates. Parent environment bytes, sibling worktrees,
  target project and other staging roots are out of scope.
- The committed acceptance verifies oracle state and physical plugin payload
  only through exact locators derived from the owned lease and fixed identity.
  It never scans global staging roots. Finally teardown removes only the exact
  lease root and reads it back absent.
- Compensation, removal, E3/E5, staging push, installer/package behavior and
  live Codex are not part of this success ticket.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `S1` | First red is the missing staging success-acceptance module. The implementation commit changes exactly the two frozen paths. |
| `S2` | Exact lease/oracle/request under the fixed child logical environment admits E2, the forward coordinator and settlement authority; invalid/subclass/constructed/mismatched authority fails before oracle command or state mutation. |
| `S3` | The observable phase order is exactly VERSION -> marketplace add -> plugin add -> fresh marketplace/plugin lists for proof. Plugin add cannot precede the exact marketplace transition and proof cannot precede both exact adds. |
| `S4` | Final persisted oracle state contains exactly the owned marketplace and plugin identity while any seeded foreign records are unchanged; no caller-selected version/path/identity becomes success evidence. |
| `S5` | Exact owned marketplace metadata and plugin payload exist under the lease's fixed Codex home with the expected identity/digest; no target-project or sibling path is read or written. |
| `S6` | The one live proof claim settles through the same E2 capability into one exact `CodexRegistrationReceipt`. Replayed/fabricated/foreign claim, foreign port and mismatched proof cannot issue a receipt. |
| `S7` | Parent environment and all three Git worktrees retain byte/porcelain identity; teardown removes only the exact owned lease root and it is read back absent. No global cleanup or global absence inference is allowed. |
| `S8` | Independently reverse operation order, proof-claim same-port admission and physical-payload identity/digest verification. Each named acceptance test turns red and exact blobs restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix class: exact lease-derived paths only; test exact root plus
  prefix-similar, child, parent and foreign locators without global enumeration.
- Authority-bypass class: invalid port/forward/settlement claim and wrong-port
  settlement cannot reach receipt issuance; exact positive authority still works.
- Exception/error class: each dependency block returns finite failure; teardown
  remains a `finally`-owned environment action and cannot manufacture success.
- Test-truth class: S3, S5 and S6 each have a named reversal in S8.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, renderer, DOM, JavaScript or
  privileged bridge exists.
- Task/worktree class: product task root, filesystem identity and linked Git
  worktree metadata must match the permanent owner worktree before dispatch.

## Exact source, return and boundary

Return one exact two-path implementation commit, then one unique
`doc/WorkProgressReport.md`-only handoff. No numeric line limit is an acceptance
criterion. The lane may create/remove only its exact lease and unique child temp
base. No E3/E5/E6, live Codex, target-project write, Agent control, staging push,
package/build/install, release or deployment is authorized.
