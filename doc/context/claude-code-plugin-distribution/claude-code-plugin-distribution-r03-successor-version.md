# Claude Code Plugin Distribution Context — Revision 03

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Artifact | `CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260823-03` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-23 (Asia/Taipei) / `PRD-20260823-036` / `CHG-20260823-036` |
| Replaces | Context Revision 02 only for the successor-version fact; its F3 payload topology and all earlier publication boundary facts remain in force. |
| Shared baseline | `7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7` |
| Architecture | `ADR-20260823-015` plus `ADR-20260823-017` |

## Stable facts revised under CHG-20260823-036

- The chosen next Claude publication version is `0.4.11`. `plugin-v0.4.10` remains immutable at
  `b52215eb3ee5dfa101e65c189441e62c20ca45e6`; it cannot be moved, reused or used as a current
  generated root.
- F3 is integrated. The next payload is generated only from a fresh Ticket 08 candidate that
  includes its narrower Level 1 declaration and the then-current approved source. The version is
  one candidate field with the manifest versions, distinct publication URL and generated SHA.
- Version selection is not external-effect authority. The public publication repository, its
  current refs, any expected-old `main` SHA, temporary source ref, candidate commit, correlation,
  remote CAS, `plugin-v0.4.11` creation, source integration and isolated Claude CLI proof each
  require fresh Ticket 08 owner authority and readback.
- Ticket 08 retains its full L1–L6 real closure and rollback obligations. Its F3 prerequisite is
  satisfied, but it remains blocked until the separate effect-authority decision. No runner,
  receipt, host gateway or background wake is introduced by this release decision.

## Seal and provenance

- Requirement lineage: `PRD-20260802-005` / `CHG-20260802-005`, amended by
  `PRD-20260823-034` / `CHG-20260823-034`, `PRD-20260823-035` / `CHG-20260823-035` and
  `PRD-20260823-036` / `CHG-20260823-036`.
- F3 integration: `7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7`, admitted from Ticket 11 with
  independent Terra reverse-mutation review.
- This revision records no candidate source, raw output, remote response, credential, task,
  worktree, receipt or external effect.
