# Claude-compatible plugin distribution Context — Revision 05

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Artifact | `CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260826-05` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-26 (Asia/Taipei) / `PRD-20260826-040` / `CHG-20260826-040` |
| Replaces | Revision 04 only for the installed-command continuation and successor-release facts below. Publication topology, generator ownership, immutable historical tags, and external-effect controls from Revisions 01–04 remain in force. |
| Shared baseline | `b56ac2d20068a4da7eb82950c64e471247c8fc61` |
| Architecture | `ADR-20260823-014`, `ADR-20260823-015`, `ADR-20260823-016`, `ADR-20260823-017`, and `ADR-20260823-018` |
| Delivery profile | `POC / STANDARD` for one deterministic instruction/test closure; `POC / HIGH_ASSURANCE` for the exact `0.4.14` publication, immutable tag, remote mutation and isolated Codex installed-cache verification. |

## Stable facts revised under CHG-20260826-040

- Codex native delegation is a same-lifetime reviewer action, not a Router runtime. After an
  admitted `AUTO_CONTINUE → IMPLEMENT` decision, the reviewer creates the one ticket-bound
  implementation owner through the host-native subagent capability, waits for its completion,
  personally reviews the returned candidate, and continues through the existing gate.
- The direct lane has no receipt, live descriptor, runner, queue, wake bridge, host gateway, or
  host task/workspace-readback precondition. Those controls retain their cross-lifetime scope.
- The host-specific source instruction must never substitute a generic model literal for the
  approved ticket/profile binding. The current ordinary ticket profile may choose the lower
  implementation capability; any elevation remains ticket-scoped and preserves the
  reviewer-at-least-as-capable invariant.
- The entry command must not end at narration when the Router has already declared this direct
  implementation action. It remains read-only at every other stage and halts honestly when the
  host lacks the capability or the required ticket binding.
- The successor is `0.4.14` and `plugin-v0.4.14`. Both are new-only values: no prior tag is
  moved, reused, or inferred. The generator remains the sole author of the parentless payload
  root and marketplace pin.
- Codex currently installs the same publication payload using `.claude-plugin/plugin.json`.
  The release acceptance therefore verifies the manifest version and the isolated cache contents
  instead of claiming that the stale development-only `.codex-plugin/` manifest was released.

## Seal and provenance

- Requirement lineage: `PRD-20260802-005` / `CHG-20260802-005`, amended by
  `PRD-20260823-034` through `PRD-20260823-037`, and `PRD-20260826-040` /
  `CHG-20260826-040`.
- Trigger evidence is the observed Codex session behavior described in the requirement, not a
  claim that a runner or cross-lifetime wake failed.
- This revision records no credential, user cache mutation, remote response, created task, or
  release result. Those are Ticket 15 reviewer-only effect evidence, if and only if readbacks
  admit them.
