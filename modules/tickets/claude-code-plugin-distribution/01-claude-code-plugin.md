# 01 — Claude Code Plugin Entry

| Field | Value |
| --- | --- |
| Parent specification | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| Owner | `root/main` |
| Context | `doc/context/claude-code-plugin-distribution/main.md` |
| Change | `CHG-20260802-005` |
| State | `DONE` |
| Environment | `LOCAL` |
| In scope | Claude manifest, marketplace catalog, README, and compatible Codex manifest update. |
| Out of scope | Target-project changes, global installation, external runtime services, secrets, MCP, and hooks. |

## Implementation steps

1. Add the root `.claude-plugin/plugin.json` with the shared plugin identity and no `version` field.
2. Add `.claude-plugin/marketplace.json` with a root-relative `./` source.
3. Rework the root README into a platform-by-platform guide that distinguishes user installation from target-project use.
4. Verify all JSON and existing skill/plugin checks, plus project test and type-check gates.
5. Record the missing `claude` executable as an unexecuted external smoke test rather than claiming it passed.

## Verification

- `claude plugin validate .` is an operator command only in this workspace because `claude` is absent.
- Static repository gates must pass before review and commit.

## Handoff

Static repository gates passed. `PENDING_FEATURE_COMMIT`: update this ticket and its review after the feature commit is created.
