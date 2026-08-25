# Ticket 07 — deferred shipped-governance verification

| Field | Value |
| --- | --- |
| Ticket ID | PAI-07-DEFERRED-SHIPPED-GOVERNANCE-VERIFICATION |
| State | ACTIVATED / OWNER_RELEASE_AUTHORITY_GRANTED (2026-08-25, Asia/Taipei) |
| Dependencies | PAI-01 through PAI-05 accepted; PAI-06 is not a release prerequisite. Exact owner release authority is required only when this verification is activated. |
| Source specification | Project authority integration SPEC Revision 11, ticket order item 07 |
| Planning baseline | main at 4df52d0df1fbe479cc9737d390df34d36e402b66 |
| Required future effect | Governance wording alignment followed by regenerated Level 1 publication root, new version, immutable tag, real installation/reload, and CLI readback. |

## Activation — exact bindings (2026-08-25)

| Binding | Value |
| --- | --- |
| Owner release authority | Owner instruction, 2026-08-25: "你來跑06-07,跑完重安裝" |
| Source paths | `skills/johnny-project-takeover/references/router-control.md`, `skills/johnny-project-takeover/references/implementation-authority.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `tests/test_plugin_publication.py` (release-version pin only) |
| Governance decisions carried | `ADR-20260824-020` decisions 1–6 (declared authority line, direct remote observation, `LOCAL_INTEGRATED` vs `AUTHORITY_INTEGRATED`, declared topology, high-collaboration PR evidence, provider enforcement qualification) |
| Generator | `write_publication_commit` at the candidate's own revision |
| Version / tag | `0.4.13` / `plugin-v0.4.13`, create-only; existing tags immutable |
| Release target | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`, `main` compare-and-swap plus absent-only tag |
| Installation target | Owner's User workstation Claude CLI, user scope, raw-descriptor marketplace |
| Pre baselines | development `main` at candidate creation; publication `main = 3b84c5f0f7df0582bd2459e83c6067ed45fb7613`, retained tags `plugin-v0.4.10/11/12` |
| Correlation | `pai07-governance-release-20260825` |
| Rollback | Forward-fix only; a defective release gets a successor version, never a moved tag |

```johnny-boundary
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/implementation-authority.md
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = tests/test_plugin_publication.py
forbid = .codex-plugin/
forbid = commands/
forbid = library/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

## Vertical closure reserved

When an owner authorizes a release, align the named governance source files with the approved
bridge and authority-line decisions, regenerate the exact Level 1 payload, assign a new version,
create an immutable tag, install or reload the named target, and verify the actual CLI-visible
payload/version. The later exact ticket must bind source paths, generator revision, payload tree,
release target, version, tag, installation target, pre/post baselines, correlation, readback and
rollback/forward-fix evidence.

This is a future verification contract, not a current PAI-08 predecessor and not a release grant.
It creates no payload change, version, tag, CLI command, provider use, publication, deployment,
receipt, descriptor, runner, or dispatch. PAI-08 may record only its deferred state; it may not
claim that the installed plugin already conveys this governance update.
