---
description: Take over or resume a project through Johnny's governed workflow
argument-hint: [this session's objective]
---

Load the `johnny-project-takeover` skill and follow it for this project.

The owner's objective for this session: $ARGUMENTS

Before proposing any action, read the target project's own governing files
(`AGENTS.md`, `CLAUDE.md`, `Workflow.md`, contributing and security policy,
whatever exists). Those rules outrank this plugin's workflow. Johnny's
Workflow is the fallback only where the target project has established none.

Read the smallest relevant requirement/SPEC, existing ticket, implementation and
test sources before asking about current behavior. Apply the skill's discovery
reference: a fact available in those sources is not an owner decision.

Resolve and execute the next already-authorized action; do not stop after
describing it. Before ticket admission, this may be bounded source inspection or
control-plane preparation allowed by the current authority, never product
implementation by the reviewer. Missing admission is not permission to invent
a PRD, SPEC revision, extra test file, clone or receipt. Reuse the existing
requirement and ticket; new behavior still requires its normal change authority.

After each return, re-enter the Router and continue independently eligible work
in this turn. A plan, ticket draft or progress response does not finish an
approved work package. End only on verified completion, concrete blockers for
all remaining work, or an execution-environment limit. State the actual blocker
and preserved evidence, not a promise to do the next action later.
Do not activate Goals, Stop hooks, heartbeats or background wake-ups implicitly.

Product implementation requires an admitted ticket; only already-authorized
source inspection and control preparation may precede it. When the Router has
declared an exact ticket-bound same-lifetime `AUTO_CONTINUE → IMPLEMENT` action,
the current-session reviewer owns
the continuation: after checking the exact ticket, reviewer-created worktree,
branch, baseline, selected ticket/profile capability and direct same-lifetime
lane, invoke Codex's native `collaboration.spawn_agent` for exactly one
ticket-bound implementation owner. Read the selected model and effort from the
ticket/profile; do not author provider or model literals here. Wait for that
owner with `wait_agent` and no activity or status polling, then review the
returned `ImplementationReturn` and perform the declared review gates.

If native delegation or the selected ticket/profile capability is unavailable,
return only `HALT / CODEX_NATIVE_DELEGATION_UNAVAILABLE`. This direct lane has
no receipt, runner, queue or descriptor prerequisite and must not fabricate a
bridge or fall back to reviewer implementation.
