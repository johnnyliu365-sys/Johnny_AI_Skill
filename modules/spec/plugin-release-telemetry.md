# Plugin Release 0.3.0 Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` |
| State | `APPROVED` |
| Owner | `root/main` |
| Context | `doc/context/plugin-release-telemetry/main.md` |
| Requirement archive | `ARCH-REQ-20260815-001` |
| Change | Retired pair `PRD-20260803-007` / `CHG-20260803-007` |

## Goal

Publish the current Johnny AI Skill source as a coherent Git marketplace plugin release containing the Router telemetry POC and the current TDD/Code Review standards.

## Scope

- Increase the Codex plugin manifest from `0.2.0` to `0.3.0`.
- Describe context-load telemetry in the Codex and Claude plugin metadata and the project-takeover skill.
- Update the public README release content while retaining user-scope installation and detach behavior.
- Retain current marketplace names, source URL, private-repository policy, and shared `skills/` directory.

## Non-goals

- No artifact archive, new registry, GitHub release, hook, MCP service, source copy into a target project, or automatic provider token collection.
- No global installation or local plugin cache mutation on this machine.

## Acceptance criteria

1. Codex manifest has version `0.3.0` and validates.
2. Claude metadata remains versionless and points to the same root plugin/skills source.
3. Both skill files are valid and instruct a user not to claim context reduction without telemetry evidence.
4. README accurately describes `0.3.0` capabilities and standard update flow.
5. Existing tests/type checks pass and the release does not add a runtime dependency to target projects.

## Approval

The project owner explicitly requested this packaging release on `2026-08-03`.
