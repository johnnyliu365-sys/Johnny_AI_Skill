# 05B4B2E4 — Codex Registration Success Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `APPROVED / READY_TO_MERGE / REVISION_03` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E4-02` / S1-S8 |
| Dependency | E2 merge `d3d3c1d` plus integrated forward, settlement-authority and proof-settlement modules |
| Planned owner | Local project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `wtr_workflow_implementation_20260813_01` |
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
- The success matrix runs from an initially clean, dedicated child lease with
  the fixed E1 logical `%LOCALAPPDATA%` and a unique process-owned temporary
  base. It may operate only inside the exact lease it creates. Parent
  environment bytes, sibling worktrees, target project and other staging roots
  are out of scope. Pre-existing foreign registration is not a success fixture:
  AC-02 classifies it as `INSTALL_BLOCKED`, and E5 owns compensation evidence.
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
| `S4` | Starting from the exact initialized clean lease, final persisted oracle state contains exactly one owned marketplace and one owned plugin identity, with zero foreign records; no caller-selected version/path/identity becomes success evidence. Post-success foreign seeding is not evidence for E4. |
| `S5` | Exact owned marketplace metadata and plugin payload exist under the lease's fixed Codex home with the expected identity/digest; no target-project or sibling path is read or written. |
| `S6` | The one live proof claim settles through the same E2 capability into one exact `CodexRegistrationReceipt`. Replayed/fabricated/foreign claim, foreign port and mismatched proof cannot issue a receipt. |
| `S7` | The committed child test proves parent environment preservation, unique child-temp absence and exact owned lease-root teardown/readback. Independent reviewer before/after manifests prove all three Git worktrees retain byte/porcelain identity. No implementation test may scan sibling worktrees, perform global cleanup or infer global absence. |
| `S8` | Independently reverse operation order, proof-claim same-port admission and physical-payload identity/digest verification. Each accurately named acceptance test turns red and exact blobs restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix class: exact lease-derived paths only; test exact root plus
  prefix-similar, child, parent and foreign locators without global enumeration.
- Authority-bypass class: invalid port/forward/settlement claim and wrong-port
  settlement cannot reach receipt issuance; exact positive authority still works.
- Exception/error class: each dependency block returns finite failure; teardown
  remains a `finally`-owned environment action and cannot manufacture success.
- Test-truth class: S3, S5 and S6 each have a named reversal in S8; the
  clean-success test name may claim only the assertions it actually executes.
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

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed ticket / handoff | Ticket freeze `4c70988596e783a5e73199ec8327230e29f685c7`; reviewed handoff is the control commit carrying this registry. |
| Delivery authority | Project-owner standing instruction to resume and continue the approved automated workflow; `IMPLEMENTATION_DISPATCH_CONFIRMED` for E4 only. |
| Product binding | Project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05b4b2e4_20260813_01`; worktree `wtr_workflow_implementation_20260813_01`; readback digest `9701416a93ba7a75700cade957aa81ed2181ca0e731ce9efbb8ec238dce4be65`. |
| Binding | `hnd_local_orchestration_install_05b4b2e4_r01_20260813`; `aln_local_orchestration_install_05b4b2e4_r01_20260813`; `rcpt_local_orchestration_install_05b4b2e4_r01_20260813`; `corr-local-orchestration-install-05b4b2e4-r01-20260813`; `q-local-orchestration-install-05b4b2e4-r01-20260813`; `scx-local-orchestration-install-05b4b2e4-r01-20260813-01`. |
| Branch | Create only `codex/implementation-codex-registration-success-acceptance-05b4b2e4` from the exact registry commit in the same permanent worktree; no new worktree. |
| Writable paths | The two frozen implementation paths, followed by a unique `PRG-20260813-316` WPR-only handoff. |

This is the single E4 dispatch. The receipt is one-use and cannot authorize E5,
another ticket, another owner or another task.

## Revision-02 correction freeze and registry

Independent review `7c6b46a98d5aaf9130eec9d40d29956a33d3bd08`
returned `CHANGES_REQUESTED` with CR-165 `TICKET_DEFECT` and CR-166
`EVIDENCE_DEFECT`. This revision corrects the ticket; it does not rewrite the
immutable implementation `33752375a5dace8e06547a7732bbd08d4c3deb45` or
handoff `5cf2235ad755bd1f5935f7139789bfa6f9a4c970`.

The same owner must add one bounded correction commit on the existing branch,
then one unique WPR-only handoff:

1. In `tests/test_codex_registration_success_acceptance.py`, remove the
   post-receipt foreign seeding/list sequence and any helpers/imports used only
   by that sequence. The clean child must assert exactly one owned marketplace,
   one owned plugin and zero foreign records.
2. Rename the S3/S4/S5/S7 test so it claims only clean child success, exact
   order/payload, parent-environment preservation and exact lease teardown. It
   must not claim to inspect sibling worktrees.
3. Do not change production/staging source behavior, add a foreign-success path,
   implement compensation, scan worktrees/global staging roots, or weaken the
   exact payload/proof gates.
4. Rerun focused/full serial unittest, strict mypy, in-memory compile and the
   three existing S8 reverse mutations. Reviewer alone reruns the external
   three-worktree before/after manifests.

| Field | Value |
| --- | --- |
| Reviewed correction authority | Revision-02 freeze is the control commit carrying this registry; prior review `7c6b46a98d5aaf9130eec9d40d29956a33d3bd08`. |
| Product binding | Retain project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05b4b2e4_20260813_01`; permanent worktree `wtr_workflow_implementation_20260813_01`. |
| Correction binding | New handoff `hnd_local_orchestration_install_05b4b2e4_cr165_166_20260813`; retain allocation `aln_local_orchestration_install_05b4b2e4_r01_20260813` and valid receipt `rcpt_local_orchestration_install_05b4b2e4_r01_20260813`; new correlation `corr-local-orchestration-install-05b4b2e4-cr165-166-20260813`, question `q-local-orchestration-install-05b4b2e4-cr165-166-20260813` and side context `scx-local-orchestration-install-05b4b2e4-cr165-166-20260813-01`. |
| Branch / baseline | Continue additively from exact handoff `5cf2235ad755bd1f5935f7139789bfa6f9a4c970` on existing branch `codex/implementation-codex-registration-success-acceptance-05b4b2e4`; no new branch/worktree, reset, amend, rebase or force. |
| Writable paths | Correction only in `tests/test_codex_registration_success_acceptance.py`, followed by unique `PRG-20260813-321` WPR-only handoff. |

The correction was dispatched only after registry commit
`f4d1598d5d76312e3cf7185441f0626de72c6e30` and exact product
task/worktree/branch/HEAD readback at the immutable handoff.

## Requirement-change disposition

The project owner changed the 05S1 root location through
`CHG-20260813-015` while the revision-02 correction was running. Owner1 stopped
at a safe boundary with no new commit or PRG-321 handoff. Only
`tests/test_codex_registration_success_acceptance.py` is modified and
uncommitted; focused 5/5 plus the order and same-port reversals passed before
the steer. E4 must not resume, commit or enter review until 05S1R is approved
and integrated and this ticket is refrozen against the new foundation.

## Revision-03 correction refreeze and dispatch registry

The project owner authorized discarding the interrupted revision-02 test edit;
the permanent owner worktree is now clean. Immutable implementation `3375237`
and handoff `5cf2235` remain the evidence base on the existing E4 branch.
05S1R/05S1R1 are approved and integrated by `d399364`, so CR-165/CR-166 may
resume as one additive same-branch correction.

| Field | Value |
| --- | --- |
| Reviewed authority | This control commit is the reviewed correction handoff; prior review `7c6b46a`; foundation merge `d399364`; completion record `2c8376f`; unchanged revision-02 correction closure. |
| Product binding | Project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05b4b2e4_20260814_03`; worktree `wtr_workflow_implementation_20260813_01`; readback digest `3ecd6d16b3052ac40a6a88d5ad7e738421bc96f9cd99551f5e7556d73fb59041`. |
| Binding | `hnd_local_orchestration_install_05b4b2e4_cr165_166_r03_20260814`; `aln_local_orchestration_install_05b4b2e4_r03_20260814`; `rcpt_local_orchestration_install_05b4b2e4_r03_20260814`; `corr-local-orchestration-install-05b4b2e4-cr165-166-r03-20260814`; `q-local-orchestration-install-05b4b2e4-cr165-166-r03-20260814`; `scx-local-orchestration-install-05b4b2e4-cr165-166-r03-20260814-01`. |
| Baseline admission | Switch the clean permanent worktree to the existing E4 branch at exact handoff `5cf2235`, then history-preserving merge the exact control registry commit. Resolve only the predicted WPR append conflict by retaining every unique PRG exactly once. Any other conflict is typed `HALT`; no reset, amend, rebase, force, new branch or worktree. |
| Writable paths | Correction only in `tests/test_codex_registration_success_acceptance.py`, followed by unique `PRG-20260814-338` WPR-only handoff. |

The revision-03 receipt is one-use. The source module and immutable prior commits
must not be rewritten; reviewer alone performs external three-worktree manifests.

## Revision-03 terminal review disposition

Correction `dc909da63cbd1aaedf73877d47bbceaa5d7e2952` and WPR-only
handoff `63b84949b2a9c7dd27872a6c0f56aa02207ed65b` are independently
`APPROVED / READY_TO_MERGE`. CR-165 and CR-166 are closed; formal evidence is
recorded in the ticket review file. Integration must preserve the complete
two-parent branch history beginning at merge `55a12fd`.
