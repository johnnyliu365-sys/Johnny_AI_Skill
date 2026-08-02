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

## Takeover flow

Follow this closed loop:

```text
INTAKE → WAYFINDER → ARCHITECTURE → GRILL → CONTEXT → SPEC → TICKETS
      → IMPLEMENT → SMOKE_TEST → REVIEW → HANDOFF
```

- A Wayfinder `NO-GO`, denied approval, invalid source, or missing required authority stops or suspends the loop.
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
