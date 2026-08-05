# 03 — Plugin Policy and Fixed Dispatch Response

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-1, AC-3, AC-9, AC-10 |
| Context / change | `doc/context/autonomous-collaboration-audit/main.md` / `CHG-20260805-010` |
| State | `PLANNED` — depends on ticket 01 event names and separate ticket approval |
| Language | Markdown, policy contract tests, and any approved Python formatter contract |
| Baseline | Ticket 01 approved public contract |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Pending owner-selected topology; required before approval |
| Environment | Local plugin/skill source only; no host configuration, target-project file, remote service or deployment |

## User-observable outcome

The shared Codex/Claude guidance asks the topology question at plugin application, describes only declared human waits, and after committed ticket/handoff artifacts emits the exact `工單 ready` and `文件交接` response shape followed by the named dispatch-confirmation question.

## Scope and boundary

In scope: `Workflow.md`, `AGENTS.md` indexes only, shared skill guidance, templates, README terminology, fixture/contract tests and retirement of active commercial wording. Out of scope: changing host settings, installing plugins, company repository files, runtime service, payment, entitlement, model selection, source/project data or deployment.

Frontend composition / DI: `N/A` — documentation and deterministic formatter policy only.

## Handoff and role assignment

- Control-plane owner: Codex/current `main` worktree.
- Implementation owner / reviewer: pending user topology selection and separate ticket approval.
- Owner override: `N/A`.
- Handoff/return follow the approved metadata-only contracts. This ticket may not silently rename an event introduced by ticket 01; a contract change returns to Grill.

## TDD and defect checks

1. Red: required topology prompt and fixed Chinese response fields are absent/misordered; green asserts ticket docs commit, ticket reference, handoff docs commit, named owner and exact dispatch question.
2. Red: policy describes a generic wait or implementation-before-dispatch path; green checks each wait/HALT/auto-continue rule against the approved contract.
3. Red: commercial wording is still presented as active direction; green differentiates historical POC references from active objective.
4. CodeReview §2.1: path/URI leakage in generated response uses seven boundary forms; null/empty field formats; direct/indirect response bypass; token N/A scan; stable formatting error; file/formatter exception; mutation proof of required labels/fields.

## Completion evidence

- Required: red evidence, document/skill contract tests, full regression/type/compile/privacy sentinel/smoke/diff evidence, review report and WorkProgress docs-only commit.
