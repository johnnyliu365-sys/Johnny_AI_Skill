# 派工模型 Profile — canonical reference

Revision: `2026-09-20 / REVISION_04` (reference relocation only).

The model registry and selection rules now have one shipped canonical location:
[Bundled dispatch model profile](../../skills/johnny-project-takeover/references/dispatch-model-profile.md),
`JOHNNY-DISPATCH-DEFAULTS` revision `01`. Read that entire reference when assigning a model.
This runbook intentionally carries no second model table.

The owner requested an installed default on 2026-09-20. The former revision-03 registry lived
under the development-only documentation tree and was absent from the 0.4.14 installed payload.
Moving it under the already-allowlisted skill tree repairs delivery without shipping development
history or changing the publication allowlist. Existing development links may keep this pointer;
shipped readers link directly to the canonical reference.

The Codex semantic values, one-ticket escalation and reviewer-strength rules are preserved.
Claude host mappings still require approved data and observed capability; old superseded tuples
are not revived. The source correction does not prove publication, installation or a host effect.

Historical lineage remains `PRD/CHG-20260822-030`, `REQ-20260824-038` and
`ADR-20260824-020` decision 8. Exact revision-03 bytes remain in Git. A ticket that pins those
bytes must read its pinned commit; do not silently reinterpret its profile through this pointer.
