# Claude Code Plugin Distribution Context

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Worktree | `root/main` |
| State | `SEALED / REVISION_06 / SPEC_REVISION_07_APPROVED` |
| Current change | `PRD-20260823-034` / `CHG-20260823-034`, amended through `PRD-20260823-037` / `CHG-20260823-037` and `PRD-20260826-040` / `CHG-20260826-040`; `ADR-20260823-015` and `ADR-20260823-018` |
| In scope | Public raw marketplace entry, dedicated payload-only publication repository, shared skills, operator instructions, and static plus real-CLI repository-closure validation. |
| Out of scope | Installing into a company repository, copying skills into a target project, hooks, MCP servers, runtime code, or secrets. |

## Basis and decision

- The owner explicitly requires the existing detachable workflow skill to work in Claude Code as well as Codex.
- The same `skills/` directory remains the sole skill source. `.claude-plugin/` supplies only Claude Code discovery and marketplace metadata.
- Installation is user-scoped and external to the project being taken over. Detachment removes only the plugin from that user's agent environment.
- The development repository is the only editable source. Its public raw
  `.claude-plugin/marketplace.json` is the marketplace entry, but its plugin `source.url` must name
  the separate `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git` repository.
- The publication repository is not a source fork. Its `main` and immutable
  `plugin-v<semver>` tags may reach only generator-produced, parentless commits whose trees and
  blobs exactly equal the declared payload.
- Source URL, version, generated root and pin form one publication candidate. Remote CAS push and
  readback plus an isolated real-CLI install complete before guarded integration, so development
  `main` never advertises an absent or unverified plugin source.

## Context references

| Source | State | Reuse decision |
| --- | --- | --- |
| `modules/spec/plugin-distribution.md` | `APPROVED` | Reuse the detachable-plugin boundary and GitHub-private distribution rules. |
| `skills/johnny-project-takeover/SKILL.md` | `READY` | Reuse unchanged as the shared project-takeover skill. |
| `skills/apply-reusable-modules/SKILL.md` | `READY` | Reuse unchanged as the shared module-selection skill. |
| `modules/spec/claude-code-plugin-distribution.md` | `STALE / REVISION_REQUIRED` | Preserve the user-scope/shared-source goal, but replace the development-repository source contract with `CHG-20260823-034` and `ADR-20260823-015`. |
| `doc/reviews/claude-code-plugin-distribution/level-1-shipping-chain-cluster-code-review.md` | `CHANGES_REQUESTED / REVISION_01` | F1 now requires a dedicated publication repository; F2 must inspect installed reachable Git trees, not only visible files. |

## Verification boundary

- Existing ticket-level tests prove the declaration, generated checkout tree, pin and remote
  reachability, but not what the source clone retains in `.git`.
- Claude Code CLI `2.1.231` was executed in an isolated `CLAUDE_CONFIG_DIR` on 2026-08-23. The
  installed checkout had the expected 243 files, while its plugin cache retained the development
  `main` (841 files), 989 packed objects and 2,477,546 bytes of Git metadata. A development-only
  test file was readable through that ref. This is the baseline-red evidence for the change.
- Closure requires both caches: raw marketplace delivery must not clone the development repo, and
  the plugin cache may contain Git metadata only for exact payload trees in the independent
  publication repo. Visible-file equality alone cannot approve release.

## Owner-backlink status

Original feature implementation committed as `d662993` (`feat: add Claude Code plugin
distribution`). The Level 1 chain through tickets 02–05 remains approved within each ticket, but
the cluster returned `CHANGES_REQUESTED`. `CHG-20260823-034` reopens Context/SPEC/ticket routing;
no replacement ticket exists yet by owner instruction.

## Revision record

| Date | Revision | Summary |
| --- | --- | --- |
| 2026-08-23 | `REVISION_01` | Live CLI evidence corrected the boundary from checkout-only to source object-graph closure and selected the dedicated publication-repository topology in `ADR-20260823-015`. |
| 2026-08-23 | `REVISION_01 / SEALED` | Project owner approved this exact Context revision together with Claude distribution SPEC Revision 02; later stages are read/reference-only. |
| 2026-08-26 | `REVISION_06 / SEALED` | `claude-code-plugin-distribution-r06-installed-cache-version-specific-tags.md` aligns installed-cache treatment of retained release tags with ADR-018. |
