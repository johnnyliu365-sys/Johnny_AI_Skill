# Claude-compatible plugin distribution Context — Revision 06

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Artifact | `CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260826-06` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-26 (Asia/Taipei): repair the small installed-cache verifier defect before continuing the already-created `0.4.14` release evidence. |
| Replaces | Revision 05 only for installed-cache closure semantics and the blocked-release continuation. All publication topology, Level 1 boundary, immutable-tag and same-lifetime-delegation facts remain in force. |
| Shared baseline | `53fd19fab45783aaa31f224fdf699760621a4664` |
| Architecture | `ADR-20260823-015`, `ADR-20260823-017` and `ADR-20260823-018` |
| Delivery profile | `POC / STANDARD` for the deterministic verifier repair; `POC / HIGH_ASSURANCE` only for the separately ticketed, fresh readback of the existing `0.4.14` release object and development-authority integration. |

## Stable facts revised under the existing version-specific-tag decision

- A normal Git clone may retain immutable `plugin-v<semver>` tags in its local object graph. This
  is not development history and is not a defect by itself: every retained release tag must be
  a parentless payload root and validate against its own in-target declaration, canonical
  generated carrier and matching tag/plugin/marketplace version.
- The installed checkout (`HEAD`), its local `main`, and any current-release tag that resolves to
  that root remain bound to the exact current typed payload and expected release root. Historical
  release tags never receive a false comparison against present-day payload blobs.
- Unknown refs, a parented target, malformed target declaration, malformed carrier, version
  disagreement, undeclared path, development sentinel (`tests/`, `doc/` or `modules/`) or an
  unreadable Git object remain fail-closed. A valid historical tag with an older declared
  payload cannot conceal any of those conditions.
- The existing `0.4.14` publication root and immutable tag are not authority to integrate the
  development candidate after the prior verifier failure. Ticket 16 repairs only the local
  verifier. A later ticket must take a fresh remote/cache snapshot and re-admit development
  integration without moving, deleting or reusing a tag.
- A future major-version requirement may choose archive/snapshot installation so that no prior
  release payload exists in an install cache. That is explicitly outside this corrective scope:
  it requires a new requirement/architecture decision and must not be simulated by deleting
  host-owned Git metadata or weakening closure checks.

## Seal and provenance

- Requirement lineage: `PRD-20260802-005` / `CHG-20260802-005`, amended by
  `PRD-20260823-034` through `PRD-20260823-037` and `PRD-20260826-040`.
- The repair applies ADR-018 Decision 3 to the installed-cache verifier; it does not create a
  new product rule, provider, host runtime, cache mutation or publication topology.
- The prior actual Codex isolated cache supplied the bounded trigger: its allowed ref grammar
  reached valid historical release tags, but the installed-cache verifier compared them to the
  current `0.4.14` payload and returned `INSTALLED_TREE_MISMATCH`.
