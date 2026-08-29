# Workflow activation and admission Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` / `REVISION_01` |
| State | `ARCHITECTURE_DRAFT / OWNER_EXACT_APPROVAL_PENDING` |
| Requirement / ADR | `PRD-20260829-048` / `CHG-20260829-048` / `ADR-20260829-036` |
| Authority | Project owner reported installed-project default-behavior failures on 2026-08-29 (Asia/Taipei). This draft grants no implementation or target effect. |

## Confirmed facts

- The installed Johnny package provides discoverable skills, but a rule inside a skill is not
  available to a session before that skill is selected.
- The current package's Codex manifest exposes skills and default prompts; it does not expose a
  repository admission or built-in file-write interception surface.
- Adaptive Revision 09 already specifies procedural document/index co-mutation. R09A planning is
  complete; the repository-admission, host adapter and installed-qualification closures are not.
- Git candidate shape can prove document/source facts but cannot prove who invoked a native
  subagent. A caller can forge branch, author and narrative evidence.
- Same-lifetime delegation remains reviewer-owned native dispatch plus one completion wait. It has
  no runner/receipt/descriptor requirement.

## Stable architecture facts

- Project activation is opt-in, project-scoped and target-owned. It names the installed skill but
  copies no governance body into the target.
- Activation, repository admission and host dispatch evidence are independent finite states.
- Managed-document admission derives the affected exact paths from the candidate and requires
  every selected direct-ancestor edge through the declared root.
- Code responsibility is expressed by a ticket-owned responsibility/dependency contract and
  language-specific strict/AST/source checks, not by size heuristics.
- Native dispatch is `HOST_PROVEN` only with non-forgeable host readback; otherwise the live
  reviewer's observation remains explicitly lower-rank.

## Data and effect flow

```text
owner-approved adoption request
  -> pure activation plan
  -> host-specific target instruction mutation + digest readback
  -> later session auto-loads target instruction
  -> takeover skill routes exact stage
  -> candidate document/source diff
  -> topology admission + responsibility admission
  -> existing authority-line integration gate
```

The activation block is the only target mutation in adoption. Admission reads ticket/candidate
state and either refuses without integration effect or passes a bounded result to the existing
gate. It stores no prompt, source body, secret or host transcript.

## Boundary

This draft is not sealed. It authorizes no target bootstrap, implementation, subagent dispatch,
publication, installation or release.
