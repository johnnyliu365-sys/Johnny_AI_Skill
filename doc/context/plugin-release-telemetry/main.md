# Plugin Release 0.3.0 Context

| Field | Value |
| --- | --- |
| Feature | `plugin-release-telemetry` |
| Worktree | `root/main` |
| State | `DONE` |
| In scope | Release the current shared skills, Router telemetry, TDD/Code Review rules, and templates through the existing Codex and Claude Code plugin metadata. |
| Out of scope | A ZIP artifact, a new marketplace, a runtime service, plugin installation in a target project, hooks, MCP, secrets, or external release publishing. |

## Confirmed release boundary

- This repository is the versioned plugin source. The new Codex manifest version is `0.3.0`; Claude Code identifies the update by Git commit SHA because its manifest intentionally has no version field.
- Codex and Claude Code continue to discover the same root `skills/` directory. No copied or platform-forked skill is introduced.
- The release exposes Router telemetry as an optional local validation capability. It does not claim automatic token interception by Codex or Claude Code.
- Existing marketplace identity and GitHub source remain unchanged: `johnny-ai-skill` from `johnnyliu365-sys/Johnny_AI_Skill` on `main`.

## Release acceptance

- Plugin manifests parse and the Codex plugin validator passes.
- Both skills pass validation after their release guidance is updated.
- Router tests, strict type checking, and diff checks remain green.
- README documents the new release content and update path without implying a company-project dependency.

## Owner-backlink status

Feature commit: `368d513` (`release: package plugin version 0.3.0`).
