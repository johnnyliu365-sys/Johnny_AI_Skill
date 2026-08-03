# 01 — Package Current Skill Release

| Field | Value |
| --- | --- |
| Parent specification | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` |
| Owner | `root/main` |
| Context | `doc/context/plugin-release-telemetry/main.md` |
| Change | `CHG-20260803-007` |
| State | `READY_FOR_COMMIT` |
| Environment | `LOCAL` |
| In scope | Plugin manifests, README, shared skill release instruction, validation, review, and GitHub push. |
| Out of scope | Target-project modification, runtime telemetry interception, third-party release publishing, secrets, MCP, or hooks. |

## Acceptance steps

1. Update Codex manifest to `0.3.0` and retain shared `skills/` discovery.
2. Describe the Router telemetry evidence boundary in both platform metadata and the takeover skill.
3. Validate both manifests and both skills, then run repository test/type gates.
4. Commit and push the release with formal handoff evidence.

## Handoff

Static validation passed; feature commit pending.
