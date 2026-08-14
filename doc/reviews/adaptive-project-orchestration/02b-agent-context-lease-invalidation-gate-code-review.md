# Router R02B Agent Context Lease Invalidation Gate Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `02b-agent-context-lease-invalidation-gate` / `CLOSURE-ADAPTIVE-ROUTER-R02B-01` ACX1-ACX8 revision `r02b-01` |
| Dispatch registry | `0280eb5b0d55494475ce18c97670ea1c37a23417` / `PRG-20260815-471` |
| Implementation | `251f72b1c2dc880fd6d99c516d43bc2e24687360` |
| Docs-only handoff | `1833506c1e5cdbe992114cff7a0b7a05b211d98d` / `PRG-20260815-472` |
| Branch / owner | `codex/implementation-router-agent-context-r02b` / task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Review result | `CHANGES_REQUESTED / SAME_TICKET_ADDITIVE_CORRECTION` |

The submitted chain has exact four-path implementation scope, a separate WPR-only handoff,
exact registry ancestry, a clean permanent implementation worktree and the required first-red,
green and reversal evidence. The pure five-operation transition table is correct. Two public
contract-boundary defects remain blocking: one rejects legitimate tree-index identifiers by
semantic word, and one permits contradictory decision payloads to be constructed outside the
Router method.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Immutable review checkout | PASS: repository-external detached clone at exact handoff, removed and read back absent; no permanent worktree was mutated. |
| Focused / six-module / full | PASS: `51/51`, `118/118`, `554/554`. |
| Strict typing / compile | PASS: strict mypy with `--explicit-package-bases` over `150/150`; in-memory compile `150/150`; external cache removed. |
| Transition adversarial matrix | PASS: 43 reviewer-owned cells cover all five admitted operations, expected-binding mismatches, stable/fresh correction and switch identities, stale states and upstream precedence. |
| Semantic opaque-ID probe | **FAIL:** five valid tree/ticket/return identifiers containing `source`, `prompt`, `resume`, `path` or `text` are rejected solely by their semantic token. |
| Decision-forgery probe | **FAIL:** five contradictory public decisions construct, including `ALLOW/OPEN` without an active lease, rejected outcomes with an active lease, `ALLOW/CLOSE` with an active lease and `ALLOW/REBIND_CORRECTION` whose prior lease remains active. |
| Scope / ancestry / residue | PASS: implementation exactly four authorized paths, handoff WPR-only, exact registry ancestry, diff check, three-worktree topology, clean submitted lane and zero submitted residue. |

## Mandatory review checks

- **Clear strong types:** PASS for the public enum/model/method annotations; FAIL the incomplete
  semantic consistency validator on the public decision result.
- **Existing conventions:** PASS immutable strict Pydantic contracts and public exports; FAIL
  because `RouterDecision`-style finite result consistency is not applied to the new decision.
- **Logic correctness:** PASS the Router transition and lifecycle precedence table; FAIL the two
  boundary findings below.
- **Edge cases:** PASS the 43-cell independent transition matrix; FAIL valid semantic leaf IDs
  and contradictory public decision construction.
- **Security / performance:** no effect, filesystem, Git, Agent, host, network, renderer or broad
  exception path was introduced; decision forgery remains an authority-boundary concern.
- **Test coverage / smoke:** submitted reversals and full regression pass, but the positive
  semantic-ID and negative decision-shape matrices are missing.
- **Dependencies:** PASS. No dependency changed.
- **Specification:** FAIL ACX1, ACX2 and ACX6 until both boundary corrections are proven.

## Findings

**CR-R02B-001 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/contracts.py:31-60` treats raw-content category words as globally
forbidden tokens inside every `OpaqueMetadataId`. R02B defines artifact refs as opaque exact-leaf
identifiers and rejects attempted raw/content fields through strict schema boundaries; it does
not make semantic words illegal inside a typed identifier. The current validator therefore
rejects valid tree and workflow identities such as `artifact-source-index`,
`ticket-prompt-hardening`, `return-resume-review`, `artifact-path-policy` and
`artifact-text-contract`. Preserve structural locator/content-field rejection, strict extras,
duplicates and all-zero revisions, but make value validation boundary-aware so semantic leaf IDs
remain portable. Add all five positive cells beside explicit negative locator/raw-field cases.

**CR-R02B-002 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/contracts.py:426-448` checks only that `active_lease`, when present, is
active. It accepts contradictory public results such as `ALLOW/OPEN` without an active lease,
`AGENT_CONTEXT_BINDING_MISMATCH` or `UPSTREAM_DECISION_REQUIRED` with an active replacement,
`ALLOW/CLOSE` with an active replacement and `ALLOW/REBIND_CORRECTION` with an active rather than
invalidated prior lease. Enforce the exact finite result shape: every non-`ALLOW` outcome has no
active replacement; each allowed operation has its frozen prior/active lifecycle pair; resume
keeps the same typed active lease; correction/switch/close cannot expose a usable prior packet.
Add the complete constructor and JSON negative matrix plus a bounded reversal of this guard.

## Correction boundary

`CHANGES_REQUESTED`. Retain the exact ticket, implementation task, permanent worktree, branch,
allocation and receipt. Synchronize this review commit into the same branch with an additive
merge; only the expected append-only WPR overlap may be resolved by retaining every unique PRG
record once and in order. Correct only `library/workflow_router/contracts.py` and
`tests/test_workflow_router.py`, then create one WPR-only correction handoff. Preserve the 43-cell
transition behavior and all ACX1-ACX8 evidence. Re-run focused, six-module, full serial, strict
mypy, compile, source/scope/diff/topology/residue gates, the original three reversals and one
decision-shape reversal.

No ticket refreeze, new branch/worktree, Router method change, R02C-R06, 06G0P, package/install,
live host/model/network, target-project, push, release, deployment or Secret effect is authorized.
`XSS_NOT_APPLICABLE`.

## Revision-02 terminal review

| Field | Result / evidence |
| --- | --- |
| Submitted correction | Same-branch merge `8e75a2f5ae5ceff301585d9d247c6900c6d76cf9`; implementation `ec2cdb8721967781e4865c3cb6eeabf99c07684a`; WPR-only handoff `744d8d7a52713c641f17306782b050f5e1415bdc` / `PRG-20260815-475`. |
| Review result | `APPROVED / GUARDED_INTEGRATION_AUTHORIZED`; `CR-R02B-001` and `CR-R02B-002` are closed. |
| Immutable checkout | PASS: a repository-external detached clone at the exact handoff was used for review, returned clean after verification, then was removed and read back absent. |
| Focused / six-module / full | PASS: R02B `10/10`; six-module Router regression `120/120`; explicit serial full suite `556/556` across `48` test files. |
| Strict typing / compile | PASS: strict mypy with `--explicit-package-bases` over `150/150`; in-memory compile `150/150`; generated cache was removed and the clone was residue-free before deletion. |
| Reviewer adversarial matrix | PASS: `43/43` independently constructed cells cover five valid Router operations, five semantic leaf IDs, seven locator/raw-field negatives and twenty-six contradictory decision shapes. |
| Scope / ancestry | PASS: correction implementation changes only `contracts.py` and `test_workflow_router.py`; handoff is WPR-only; exact registry ancestry, diff check, three-worktree topology and clean permanent implementation lane pass. |
| Security / effects | PASS: no source body, callable, optional effect port, dynamic lookup, constructor bypass, broad exception, filesystem, Git, Agent, host, network or renderer capability was introduced. `XSS_NOT_APPLICABLE`. |

All eight mandatory review dimensions pass: clear strong types, existing conventions, logic,
edge cases, security/performance, test coverage/smoke, dependencies and specification closure.
Semantic words remain legal inside opaque exact-leaf IDs while locator syntax and undeclared raw
fields fail closed. Public decisions now enforce the exact allowed-operation lifecycle algebra,
and every rejected decision omits an active replacement.

Guarded integration may merge only exact handoff
`744d8d7a52713c641f17306782b050f5e1415bdc`. Any conflict beyond the expected append-only
`doc/WorkProgressReport.md` overlap must halt without resolution. R02C-R06, 06G0P, package,
push, release, deployment, target-project, live host/model/network and Secret effects remain out
of scope.
