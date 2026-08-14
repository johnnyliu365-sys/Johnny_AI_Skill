# Johnny AI Skill project shared Context

> State: `SEALED` by `CHG-20260815-020`. This artifact is architecture-owned.
> Later stages bind its revision and exact source spans; they do not append to it.

## Stable project facts and boundaries

- Johnny is an external, detachable control plane. Target-owned requirements, Context, SPEC,
  tickets, tests, reviews and product source remain in the user's repository; this plugin is
  not its runtime, CI, build or deployment dependency.
- Authorized historical source repositories (`SourceProjectA`, `來源專案B`, 來源專案C
  `來源專案C`, `來源專案D`) are read-only references. No source repository is
  modified, and no Secret, PII, operational data or domain-specific business rule is copied.
- The current product direction is a local, removable, metadata-only multi-Agent workflow
  control plane. Historical SaaS/payment/entitlement work is evidence, not a current product
  commitment.
- Only the ticket's named reviewer may orchestrate an implementation Agent. Every source,
  workspace, Git or host effect remains role-, receipt-, baseline- and correlation-bound.
- Shared Context lifecycle and content admission are defined only by
  `skills/johnny-project-takeover/references/context-routing.md`. Ticket, dispatch,
  implementation, monitoring and review lanes are read/reference-only.

## Metadata-only feature index

Status, handoff, commits, tests and findings live in each feature's SPEC, Context, ticket, WPR
or review. This index records identity and location only.

| Feature | SPEC ID / path | Feature Context |
| --- | --- | --- |
| Reusable module library | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP` / `modules/spec/reusable-module-library.md` | `doc/context/reusable-module-library/main.md` |
| Router framework | `SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H` / `modules/spec/router-framework.md` | `doc/context/router-framework/main.md` |
| Module application skill | `SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H` / `modules/spec/module-application-skill.md` | `doc/context/module-application-skill/main.md` |
| Plugin distribution | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1X3Z5B7C9D1F3H` / `modules/spec/plugin-distribution.md` | `doc/context/plugin-distribution/main.md` |
| Claude plugin distribution | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` / `modules/spec/claude-code-plugin-distribution.md` | `doc/context/claude-code-plugin-distribution/main.md` |
| Context telemetry | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` / `modules/spec/context-load-telemetry.md` | `doc/context/context-load-telemetry/main.md` |
| Plugin release telemetry | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` / `modules/spec/plugin-release-telemetry.md` | `doc/context/plugin-release-telemetry/main.md` |
| Private Router POC | `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` / `modules/spec/private-router-saas.md` | `doc/context/private-router-saas/main.md` |
| Workflow governance | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` / `modules/spec/workflow-governance.md` | `doc/context/workflow-governance/main.md` |
| Collaboration audit | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / `modules/spec/autonomous-collaboration-audit.md` | `doc/context/autonomous-collaboration-audit/main.md` |
| Local orchestration installer | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / `modules/spec/local-orchestration-installer.md` | `doc/context/local-orchestration-installer/main.md` |
| Adaptive project orchestration | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` / `modules/spec/adaptive-project-orchestration.md` | `doc/context/adaptive-project-orchestration/main.md` |
