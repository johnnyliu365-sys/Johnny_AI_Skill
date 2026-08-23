# Claude Code Plugin Distribution Context — Revision 04

| Field | Value |
| --- | --- |
| Feature | `claude-code-plugin-distribution` |
| Artifact | `CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260823-04` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-23 (Asia/Taipei) / `PRD-20260823-037` / `CHG-20260823-037` |
| Replaces | Context Revision 03 only for multi-release publication-tag verification. Its F3 topology, successor-version, public-repository and external-effect facts remain in force. |
| Shared baseline | `475e01b96693c33251e77eed2bbff3116f2bc713` |
| Architecture | `ADR-20260823-015`, `ADR-20260823-017` and `ADR-20260823-018` |
| Delivery profile | `POC / STANDARD` for Ticket 12's deterministic local closure contract. Ticket 08 remains `POC / HIGH_ASSURANCE` and blocked. |

## Stable facts revised under CHG-20260823-037

- `refs/heads/main` remains the current-release assertion. It is compared path-for-path and
  blob-for-blob to the supplied current candidate payload and, during Ticket 08, to its exact
  generated root `C`.
- A retained immutable `refs/tags/plugin-v<semver>` is not compared to the current development
  candidate. The verifier reads that tag commit's own `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`, validates the two embedded versions equal the tag semver,
  validates the generated pin-carrier shape, and admits only the exact path set declared by that
  tag's own payload declaration. A parent, foreign ref, missing/extra declared path, malformed
  declaration or version disagreement remains a named failure.
- The historical tag's immutable target is its content provenance. Because a retained release has
  no retained development-source checkout or external per-file digest, a self-declaration check
  must not falsely claim comparison of its blobs to the current working tree. Blob-for-blob
  equality remains mandatory for current `main` and the newly created `plugin-v0.4.11` root,
  which have the exact supplied candidate payload.
- `plugin-v0.4.10` stays immutable at
  `b52215eb3ee5dfa101e65c189441e62c20ca45e6`. A fresh Ticket 08 candidate may create only
  `plugin-v0.4.11` after Ticket 12 closes and a new exact effect authority is recorded. It may
  not delete, move, rewrite or use `plugin-v0.4.10` as the current root.
- The prior Ticket 08 CLOSURE_03 authority is suspended. Candidate
  `73a421d827794f7cf059b74c096d041471b6044f` and root
  `08330633ef31acdc54e8fa8c38414476faed598a` are local review evidence only. This Context
  neither resumes that authority nor permits a remote, source push, tag, cache or Claude CLI
  operation.

## Seal and provenance

- Requirement lineage: `PRD-20260802-005` / `CHG-20260802-005`, amended by
  `PRD-20260823-034` / `CHG-20260823-034`, `PRD-20260823-035` / `CHG-20260823-035`,
  `PRD-20260823-036` / `CHG-20260823-036` and `PRD-20260823-037` /
  `CHG-20260823-037`.
- Trigger: Ticket 08 CLOSURE_03 showed that F3 intentionally changes the current payload while
  the immutable `plugin-v0.4.10` tag must remain reachable. Its old one-payload-for-every-ref
  contract is therefore structurally unsatisfiable for a multi-release repository.
- This revision records no new candidate, payload root, remote response, credential, task,
  worktree receipt or external effect.
