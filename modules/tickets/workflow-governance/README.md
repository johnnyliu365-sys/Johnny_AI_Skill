# Continuous Workflow Governance POC — Ticket Set

> Approved specification: [workflow-governance.md](../../spec/workflow-governance.md) (`SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`). This ticket set creates no implementation authority by itself.

## Delivery objective

Deliver one control-plane policy vertical slice: completion evidence must re-enter the Router, safe stages continue in the active task, declared authority gates wait precisely, unsafe conditions halt, and implementation work returns its evidence or a requirement-change event to the control plane. The slice applies the same rules to formal frontend handoff without adding a target-project runtime dependency.

## Ticket status

| Ticket | User-observable capability | State | Required authority |
| --- | --- | --- | --- |
| [01-enforce-continuation-and-handoff](01-enforce-continuation-and-handoff.md) | Post-commit Router continuation, typed implementation return, and policy/template enforcement | `DONE` | Review approved; integrated into `main` by merge `2f545c8` (the ticket file records the closure; this row had gone stale) |
| [02-repo-contained-worktree-layout](02-repo-contained-worktree-layout.md) | Every agent's worktree lives under the repository root, proven host-side | `CLOSED` | Owner-executed 2026-08-19; R1-R6 green, reverse mutation proven. The dispatch-admission gate its R3 anticipated is now wired by workstation-dispatch W1 |
| [03-suite-order-fragility](03-suite-order-fragility.md) | A poisoned shared runtime root is reported once, with its cause and remedy, instead of eighty misleading failures | `CLOSED` | Real cause found: per-process claim map versus a shared on-disk root, orphaned by concurrent pytest processes. The opening diagnosis was wrong and is corrected in place |
| [04-skill-implies-a-runtime-that-may-not-exist](04-skill-implies-a-runtime-that-may-not-exist.md) | The skill no longer narrates wakes nothing performs; agents must verify automation readiness before claiming any automatic effect | `CLOSED` | Found by the owner watching a false wake narrative on a real project; ships as 0.4.4 |
| [24-independent-admitted-ticket-continuation](24-independent-admitted-ticket-continuation.md) | A waiting ticket cannot freeze an unrelated admitted ticket or transfer its authority | `OWNER_WAIT_SLICE_LOCAL_INTEGRATED` | `af24945f` gated and another seat verified exact blob parity; B full closure preserved in Ticket 30 |
| [25-refactor-test-seam-transfer](25-refactor-test-seam-transfer.md) | A responsibility split moves behavior tests and mutation targets with the production seam before the next split | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `970b99cc`; checklist 04 closed by Tickets 33–34 |
| [26-active-writer-worktree-branch-uniqueness](26-active-writer-worktree-branch-uniqueness.md) | The existing worker-claim ledger rejects two active writers on one worktree or branch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `9cedb55f`; generic prewrite protection still open |
| [27-evidence-linked-ticket-status-projection](27-evidence-linked-ticket-status-projection.md) | Opt-in evidence-bearing stage projection rejects false APPROVED with required work unverified | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `3196712d`; parent/finding projection added by Ticket 35, formal closure still open |
| [28-minimal-complete-dispatch-ticket](28-minimal-complete-dispatch-ticket.md) | One ticket template carries sourced Expected, I/O, failure/boundary acceptance and stop/review conditions | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review approved; `cfa46704`; Host dispatch admission still open |
| [29-mainline-ticket-projection](29-mainline-ticket-projection.md) | Separate the work mainline from a single ticket; recommend next recheck without granting dispatch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `2fa4ca6f`; trusted source and formal closure remain open |
| [30-trusted-independent-ticket-continuation](30-trusted-independent-ticket-continuation.md) | Proposed source-bound candidate projection for independent B, without Host or closure authority | `30A_PROPOSED / UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE` | Preliminary review blocked `76f6f32771e80add10c499db2c7479377b079c0c`: no ticket-scoped Grant or approved generic index/leaf declaration and readback contract; current index is not asserted migrated, and qualified Host admission remains separate |
| [31-semantic-model-profile-boundary](31-semantic-model-profile-boundary.md) | Keep universal Skill model-neutral while the current verified Profile selects capability | `SLICE_LOCAL_INTEGRATED` | Independent review and control gate passed at `68a10057`; paid test isolation/reporting remain separate |
| [32-test-consumer-inventory](32-test-consumer-inventory.md) | Find direct and indirect test consumers before test retirement | `SLICE_LOCAL_INTEGRATED` | Independent review and control gate passed at `2a19406d`; Host/CI retirement admission open |
| [33-shared-context-service-seam](33-shared-context-service-seam.md) | TEST→A transfers actual Shared Context behavior from Router to one service | `A_LOCAL_INTEGRATED` | Independent review approved; `ac369235`; B test seam/retirement still open |
| [34-shared-context-test-seam-transfer](34-shared-context-test-seam-transfer.md) | Move five contract-only cells while keeping public Router behavior cells mutation-sensitive | `B_LOCAL_INTEGRATED` | Independent review approved; `b4a7dbe6`; checklist 04 complete locally |
| [35-parent-finding-status-closure](35-parent-finding-status-closure.md) | Show required child and Finding closure without a false APPROVED parent | `SLICE_LOCAL_INTEGRATED` | Independent review approved correction; `215a599f`; projection only, formal Review authority still open |
| [36-git-pinned-test-source-inventory](36-git-pinned-test-source-inventory.md) | Read test consumers from an exact Git commit instead of caller-supplied working-copy text | `SLICE_LOCAL_INTEGRATED` | Independent review approved correction; `e1ca2d4b`; CI commands and retirement authority still open |
| [37-retired-wpr-commit-conflict](37-retired-wpr-commit-conflict.md) | Remove the obsolete standalone WPR commit completion obligation and keep its policy pins aligned | `SLICE_LOCAL_INTEGRATED` | Initial review found a timing defect; same-ticket correction approved and locally gated at `2f1c29cb` |
| [38-reuse-and-responsibility-dispatch-contract](38-reuse-and-responsibility-dispatch-contract.md) | A dispatch ticket names reused modules, separate code/test/script responsibilities and bounded growth evidence before implementation | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review and document gate approved at `3557bc20`; Host admission and semantic structural review remain separate gaps |
| [39-literal-suite-consumer-inventory](39-literal-suite-consumer-inventory.md) | Trace literal SUITES registry references through Python wrappers before test retirement | `INVENTORY_SLICE_LOCAL_INTEGRATED` | Independent review approved correction and local gate integrated `e9177f80`; real CI command source and retirement authority stay open |
| [40-scaffold-ticket-template-parity](40-scaffold-ticket-template-parity.md) | Keep the shipped new-project ticket scaffold aligned with current single-ticket fields | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review approved candidate `91ee17c3`; exact-blob replay passed document gate at `5776139a`; Host admission remains open |
| [41-bounded-spec-correction-integration](41-bounded-spec-correction-integration.md) | Integrate the two owner-authorized bounded corrections into the original SPEC design baselines | `DESIGN_LOCAL_INTEGRATED / CLEANUP_BLOCKED` | Original design replay `76d1f942`; independently reviewed state-binding correction `cca2db71`; isolated journal teardown remains; runtime/Host activation separate |

## Shared baseline

- Specification: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`)
- Change: `CHG-20260805-009`
- Context: [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md)
- Documentation baseline: `04146af` (`docs: draft continuous workflow governance`)
- Delivery environment: local Python workflow-router POC plus detached Codex/Claude guidance source. No hosted service, background worker, target-project dependency, or external provider is in scope.

## Authority and handoff

Codex/current worktree is the control-plane owner and reviewer. The implementation owner is the separate `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree on branch `codex/implementation-private-router-saas-01`. It is currently based on `7769710` and must fast-forward to `main` before the first red test. The project owner approved this ticket on `2026-08-05`; source/test work is authorised only in that assigned worktree.

The implementation handoff consists of the approved specification, this ticket, Context references, TDD cuts, exact target paths, and the return-event rules. A completion returns evidence for review; a requirement, architecture, public-contract, frontend composition/DI, or acceptance change returns `REQUIREMENT_CHANGED` to Grill.
