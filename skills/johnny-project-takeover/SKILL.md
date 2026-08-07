---
name: johnny-project-takeover
description: Guide a new, inherited, or in-progress software project through the Johnny AI Skill router, Wayfinder, Grill, specification, ticket, implementation, review, and handoff workflow. Use when the user asks to take over a project, establish a POC/MVP/commercial delivery path, select the minimum reusable modules, or resume work under this workflow without adding a runtime dependency to the target project.
---

# Johnny Project Takeover

Treat this plugin as an external control plane. It supplies workflow guidance and reusable-module selection; it is never a target project's runtime dependency.

## Start safely

1. Read the target project's own `AGENTS.md` and governing workflow before writing, staging, or executing project tools. Do not overwrite, copy, or enable this repository's `AGENTS.md` in the target project automatically.
2. Read `../../Workflow.md` to locate the router stage, then the applicable complete section. For `WAYFINDER`, read `../../Defined_wayfinder.md` as the detailed work standard.
3. Treat the delivery stage as `POC` unless an approved target-project artifact establishes `MVP` or `COMMERCIAL`. Do not upgrade stages from chat inference alone.
4. Resolve only the current stage's required sources and capabilities. Keep shared Context small; use the router's side-context reference rules for a bounded, traceable source-span read.
5. When the user asks whether routing reduced context load, follow `../../library/workflow_router/README.md`. Record only metadata in a local ignored JSONL file and do not claim reduction unless matched baseline/router runs contain provider-reported input-token usage and pass the telemetry validator.

## Safe automatic continuation

After each completed action, classify the next Router decision before replying. Do not stop merely because one stage has completed.

An implementation or docs-only commit returns through the typed `ACTION_COMPLETED` / `ImplementationReturn` contract. A `CHANGE_DETECTED` return emits `REQUIREMENT_CHANGED` and re-enters Grill; it is never silently patched in place.

1. **`AUTO_CONTINUE`** — when the required evidence is present, the next stage is declared, exactly one capability is selected, and no new human authority is needed, immediately read only that next stage's minimum sources and continue the workflow in the same task. Complete one legal action at a time, emit its new event, and re-evaluate. Do not ask the user for a ceremonial “continue?” confirmation.
2. **`WAIT_FOR_HUMAN`** — pause only at a Profile-declared approval or user-decision gate, or before an irreversible external side effect. State the precise approval or decision required; do not describe it as a generic block.
3. **`HALT`** — invalid or missing source, unavailable capability, denied authority, validation failure, security/privacy issue, failed external boundary, or an undeclared transition stops the routed path. Do not guess a next stage, reuse a local fallback Profile, or wait indefinitely.

This skill can guide a currently active Codex or Claude task to continue through safe stages. It cannot independently create a new model turn, bypass the host's approval system, or prevent users from disabling the plugin. The local Router runner's safety ceiling remains authoritative.

## Plugin policy and fixed dispatch response

At plugin application or takeover, ask exactly `可用 coding Agent 數量為 1 或 2？` and record only the typed topology. Do not create a host turn, choose a model, or grant implementation access from that answer.

After committed ticket and handoff artifacts exist, use this fixed metadata-only response and then ask the one named dispatch question:

```text
工單 ready
- commit：<ticket docs commit>
- 工單：<ticket reference>

文件交接
- commit：<handoff docs commit>
- implementation owner：<named owner>
- 工單 <ticket reference> 是否已交付給 implementation owner <named owner>？
```

Before that confirmation, no branch, worktree, source, Context or implementation capability may be granted. `AUTO_CONTINUE` covers only declared safe transitions; `WAIT_FOR_HUMAN` names this exact delivery decision; malformed, unavailable, replayed or unauthorized input is `HALT`. Commercial or SaaS Router material is historical POC context only, not active product direction.

## Role boundary and frontend handoff

This skill's control-plane Agent owns Wayfinder, Grill, Context, SPEC, ticket drafting, implementation handoff, review, and handoff. It does not implement approved ticket source, tests, migrations, deployment, or implementation commits unless the project owner explicitly reassigns that ticket.

Every ticket must name a separate implementation owner. That owner follows the approved ticket; it must return ambiguous requirements, architecture, public-contract, or acceptance changes to this control-plane Agent for `grill-with-docs → to-spec → to-tickets`.

The control-plane handoff records an `ImplementationHandoff` containing only approved artifact references, source revision/span metadata, side-context IDs, consumer fingerprints, and evidence digests. The implementation owner returns `ImplementationReturn`: `COMPLETED` emits `ACTION_COMPLETED`, `BLOCKED` halts fail-closed, and `CHANGE_DETECTED` emits `REQUIREMENT_CHANGED` for Grill. Neither record may contain raw ContextPacket text, source text, prompts, paths, URIs, secrets, or PII.

For any formal frontend ticket, require composition-first design and dependency injection before implementation: name the screen/layout/component boundaries, Composition Root, scoped interfaces and bindings, production dependencies, test fakes, and loading/empty/error/accessibility acceptance. A component must not instantiate a global singleton, read environment configuration, or access an external service implicitly.

## Takeover flow

Follow this closed loop:

```text
INTAKE → WAYFINDER → ARCHITECTURE → GRILL → CONTEXT → SPEC → TICKETS
      → IMPLEMENT → SMOKE_TEST → REVIEW → HANDOFF
```

- A Wayfinder `NO-GO`, denied approval, invalid source, unavailable capability, or missing required authority halts the loop. Only an explicitly declared approval gate waits for a human.
- A requirement change returns the work to change control and the relevant earlier gate; it does not patch an already-approved ticket in place.
- Read only the section and capability selected by the router. Do not load the full library, every module, or unrelated skill into shared Context.

## Reuse a module without coupling the project to this plugin

1. Invoke `$apply-reusable-modules` and select only a `READY` card from `../../library/MODULE_CATALOG.md`.
2. Record the selected module ID, repository revision, public contract, and rejected candidates in the target project's approved Context or ticket.
3. Do not create a symlink, Git submodule, relative import, package dependency, CI dependency, hook, or runtime path to this plugin's cache or checkout.
4. If an approved ticket adopts behaviour from a module, make the resulting implementation target-owned, versioned, tested, and committed in the target project. The plugin remains a read-only reference and can then be removed without breaking that project.

## Detach

Removing or disabling this plugin removes only its skills, workflow references, and module catalog access. It must not remove target-project source, configuration, CI, data, or formal artifacts.

Before detaching, ensure any approved target-project work is committed and its verification command passes. Future agents then follow the target project's own guidance; they no longer receive Johnny AI Skill routing or module-selection instructions.
