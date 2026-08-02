# Claude Code Plugin Distribution Context

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Worktree | `root/main` |
| State | `DONE` |
| In scope | Claude Code private-Git marketplace entry, shared skills, operator instructions, and static validation. |
| Out of scope | Installing into a company repository, copying skills into a target project, hooks, MCP servers, runtime code, or secrets. |

## Basis and decision

- The owner explicitly requires the existing detachable workflow skill to work in Claude Code as well as Codex.
- The same `skills/` directory remains the sole skill source. `.claude-plugin/` supplies only Claude Code discovery and marketplace metadata.
- Installation is user-scoped and external to the project being taken over. Detachment removes only the plugin from that user's agent environment.
- Claude Code source layout follows its official plugin and marketplace conventions: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `source: "./"`, and root-level `skills/` discovery.

## Context references

| Source | State | Reuse decision |
| --- | --- | --- |
| `modules/spec/plugin-distribution.md` | `APPROVED` | Reuse the detachable-plugin boundary and GitHub-private distribution rules. |
| `skills/johnny-project-takeover/SKILL.md` | `READY` | Reuse unchanged as the shared project-takeover skill. |
| `skills/apply-reusable-modules/SKILL.md` | `READY` | Reuse unchanged as the shared module-selection skill. |
| `modules/spec/claude-code-plugin-distribution.md` | `APPROVED` | Implement the Claude Code-specific metadata and usage guidance. |

## Verification boundary

- Static validation passed in this workspace: JSON parsing, both shared-skill validators, the Codex manifest validator, `git diff --check`, 48 Python unit tests, and strict type checking across 54 source files.
- The `claude` executable is not installed in this workspace. `claude plugin validate .` and a user-scope install are deliberately documented as an operator smoke test, not falsely recorded as executed.

## Owner-backlink status

Feature implementation committed as `d662993` (`feat: add Claude Code plugin distribution`).
