# Claude Code Plugin Distribution POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| State | `APPROVED` |
| Owner | `root/main` |
| Context | `doc/context/claude-code-plugin-distribution/main.md` |
| PRD reference | `PRD.md §9` |
| Change | `CHG-20260802-005` |

## Goal

Allow the existing Johnny AI Skill workflow plugin to be installed from the private GitHub repository in Claude Code, without duplicating skills or altering a company project.

## Scope

- Add `.claude-plugin/plugin.json` at this repository root.
- Add `.claude-plugin/marketplace.json` that exposes this root plugin through `source: "./"`.
- Reuse the existing root `skills/` directory without copies, symlinks, or platform forks.
- Explain user-scope install, invocation, update, test, and removal for both Codex and Claude Code.
- Keep the existing Codex plugin compatible and increment its manifest version for the shared-platform release.

## Non-goals

- Do not install anything in a target company repository.
- Do not add a runtime library, build step, hook, MCP server, secret, service, or package dependency.
- Do not alter shared skill content merely to create a second platform entry.

## Contracts

| Contract | Requirement |
| --- | --- |
| Claude plugin manifest | `.claude-plugin/plugin.json` identifies `johnny-ai-skill` and leaves `version` absent so Git commit SHA can represent the installed revision. |
| Claude marketplace | `.claude-plugin/marketplace.json` contains one `johnny-ai-skill` entry whose source is exactly `./`. |
| Shared skills | Both platforms discover the existing `skills/johnny-project-takeover/SKILL.md` and `skills/apply-reusable-modules/SKILL.md`. |
| Isolation | A company project receives no copied files, imports, runtime dependencies, or configuration. |
| Names | Codex invokes `$johnny-project-takeover`; Claude Code invokes `/johnny-ai-skill:johnny-project-takeover`. |

## Acceptance criteria

1. Both Claude JSON manifests parse as JSON and contain the stated plugin name and root source.
2. Existing shared skills continue to pass the skill validator; the Codex manifest continues to pass the plugin validator.
3. The README gives an exact private-repository installation and removal path for both Codex and Claude Code, and states the detach guarantee.
4. Project Python tests and strict type checks remain green.
5. The unavailable local Claude executable is never presented as validated. The README documents `claude plugin validate .` as the one-time operator smoke test after cloning.

## Risks and controls

| Risk | Control |
| --- | --- |
| A user mistakes a workflow plugin for a project dependency. | README and skill boundaries state user-scope installation and no target-project writes. |
| Platform-specific skills drift. | Both platforms discover the single root `skills/` directory. |
| Private-repository authentication encourages token leakage. | Documentation requires existing Git/SSH authentication and prohibits embedding a token. |
| Claude Code is unavailable in this workspace. | Keep live CLI validation explicitly deferred to the user's Claude Code environment. |

## Approval

- Approved by explicit owner request on `2026-08-02` to make the detachable workflow usable from Claude Code.
- Implementation is limited to this POC specification and its ticket.
