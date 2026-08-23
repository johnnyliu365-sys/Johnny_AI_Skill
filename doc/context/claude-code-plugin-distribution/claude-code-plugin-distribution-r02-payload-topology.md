# Claude Code Plugin Distribution Context — Revision 02

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Artifact | `CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260823-02` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-23 (Asia/Taipei) / `PRD-20260823-035` / `CHG-20260823-035` |
| Replaces | Context Revision 01 for the Level 1 payload topology only; its publication-repository and external-effect facts remain in force. |
| Shared baseline | `1caa2f2355638c75610dc848b5bd23d8f97d0bcb` |
| Architecture | `ADR-20260823-015` plus `ADR-20260823-017` |
| Delivery profile | `POC / STANDARD` for F3's deterministic local source/declaration closure. A later Ticket 08 re-admission remains `POC / HIGH_ASSURANCE`. |

## Stable facts revised under CHG-20260823-035

- Level 1 is a detached Claude Code skill payload, not a copy of the local host/control runtime.
  Its reusable `library` surface is exactly the declared catalog, NLP, capability, payment and
  workflow-router paths, together with the root package and catalog files they need.
- The Level 1 declaration must use clean, segment-exact nested directory paths. It must not name
  `library/` wholesale. `library/local_orchestration/` and the Windows bundle entrypoints are not
  Level 1 paths; a new development/host child remains outside the publication tree by default.
- Worktree containment is a plugin policy: every agent worktree is under repository
  `.worktrees/<ticket-id>` (or the Claude-owned `.claude/worktrees/` location). Its enforcement
  helper is host-side development material, not a detached plugin runtime API.
- The reusable-module selector remains available for delivered library partitions. It must not
  select `local-orchestration` through the installed Claude payload. Host registration, runner,
  receipt, installer, publication, cache-inspection and external-effect capabilities remain
  separately provisioned and never follow from a plugin install.
- F3 changes no source URL, public repository, ref, SHA, tag, release version, user cache, Claude
  CLI setup, or target-project source. `plugin-v0.4.10` remains immutable; successor-version
  selection is deliberately deferred until F3's source integration and independent review.

## Evidence and downstream artifacts

- F3 originates in the accepted review finding F3 at source commit `1caa2f2`: source-control
  verification tooling was inside the Level 1 payload and changed the root it verified.
- `modules/spec/claude-code-plugin-distribution.md` Revision 03 must bind this Context and make
  the topology’s exact declared paths, forbidden host surface and reverse mutations ticket
  authority before any F3 implementation dispatch.
- Ticket 08 remains `BLOCKED / REQUIREMENT_CHANGED`; it has no current successor version, tag or
  remote-effect authority. A new version decision follows F3, not vice versa.
- Context Revision 01 remains sealed evidence for the dedicated publication-repository topology.
  This file replaces only the changed payload-topology facts and does not append ticket state,
  worktree output, raw CLI text, source code, credentials or prompts.

## Seal and provenance

- Requirement lineage: `PRD-20260802-005` / `CHG-20260802-005`, amended by
  `PRD-20260823-034` / `CHG-20260823-034` and `PRD-20260823-035` / `CHG-20260823-035`.
- Review source: `doc/reviews/claude-code-plugin-distribution/level-1-shipping-chain-cluster-code-review.md`,
  F3, at `1caa2f2`.
- This revision leaves `skills/` as the sole shared-skill source and preserves the target-owned,
  user-scoped detach boundary.
