# ADR-20260823-018 — Immutable release tags validate their own declared payload

- Date: `2026-08-23 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260823-037` / `CHG-20260823-037`
- Affected specification: `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P`, Revision 05
- Amends: `ADR-20260823-015-dedicated-plugin-publication-repository.md`

## Context

ADR-015 correctly requires every publication ref to remain parentless and payload-only. Its
first verifier implementation accepted one `PublicationPayload` from the current development
candidate and compared that payload to every admitted remote ref.

F3 deliberately narrowed the Level 1 declaration. Ticket 08 then proved the consequence in a
fresh local fixture: `main=C` and `plugin-v0.4.11=C` pass, an injected development ref fails,
and exact restoration passes again. Adding the required immutable
`plugin-v0.4.10=b52215eb3ee5dfa101e65c189441e62c20ca45e6` instead returns `TREE_MISMATCH` with
104 extra paths and six changed blobs. The old tag is correct for its release; the current
declaration is correct for the new release. Requiring both to equal one declaration makes a
multi-release publication repository impossible without rewriting history.

## Decision

### 1. Preserve one ref grammar and parentless-history boundary

The only admitted refs remain `refs/heads/main` and lightweight
`refs/tags/plugin-v<semver>`. Every target must be a readable parentless commit; the default
branch remains exactly `main`; foreign refs, tag movement/collision, default-branch changes and
unreadable or malformed Git data remain named failures. This decision neither removes nor
weakens the clone-reachable object-graph boundary.

### 2. Keep the current release tied to the reviewed candidate

`main` is verified against the exact typed payload supplied by the current candidate, including
path and blob identity. The fresh release tag is also required to name that generated root and to
have a tag version equal to both manifests in that root. The self-referential marketplace carrier
continues to use the existing reversible normalizer: current source mode records the generated
root, while the published generated carrier is neutralised and healed only for this exact
candidate comparison.

### 3. Validate retained tags from their own immutable target

For each retained release tag, the closure reader obtains only target-commit blobs and builds a
frozen `PublicationReleaseDeclaration`: release semantic version, exact payload path declaration
and canonical generated pin-carrier record. It rejects a missing/malformed plugin declaration,
missing/malformed marketplace entry, a tag/plugin/marketplace version disagreement, an invalid
generated carrier, a missing declared path or an extra tree path. It does not consult the current
working manifest when judging the retained tag.

This means each retained tag's immutable target is its content provenance. The embedded payload
declaration can prove exact allowed paths, but it cannot independently compare the tag's declared
file blobs to present-day development blobs: the project has no separately retained historical
source checkout or signed per-file digest. The verifier must expose that distinction in its typed
contract and tests rather than describing a self-derived tree as an external blob proof.

### 4. Re-admit release effects only after a local contract closes

Ticket 12 implements and independently reverse-mutates this deterministic local contract. Until
it is integrated, Ticket 08 remains blocked. Its former CLOSURE_03 external-effect authority is
suspended; the local candidate and generated root are evidence, not a substitute authority. A
later effect attempt must bind a newly rebased candidate, generated root, current remote snapshot,
absent `plugin-v0.4.11`, correlation and all other Ticket 08 effects anew.

## Alternatives rejected

- **Move or delete `plugin-v0.4.10`.** Rejected: it violates immutable-release policy and
  destroys the historical public release it is meant to represent.
- **Force every retained tag to match the current F3 declaration.** Rejected: it recreates the
  impossible condition observed in CLOSURE_03 and makes any safe payload evolution incompatible
  with retained releases.
- **Drop retained tags and keep only `main`.** Rejected: versioned rollback/provenance would be
  lost and the external release policy would be weakened.
- **Pretend a tag can prove its blobs against its own tree.** Rejected: deriving expected blob
  IDs from the object being checked is not independent content proof. The actual historical trust
  basis is tag immutability plus the evidence recorded when that release was created.
- **Add a runner, queue, receipt or remote service.** Rejected: this is a deterministic local
  Git reading rule. No delivery bridge or release automation addresses the contract conflict.

## Consequences and recovery

- The verifier gains a typed target-commit declaration reader and distinct declaration/version
  failures. Current-release payload/blob comparison remains intact.
- Tests gain a two-release local fixture: historical `plugin-v0.4.10` and current
  `main`/`plugin-v0.4.11` may have different valid payloads, while a development ref, malformed
  tag declaration, tag-version disagreement or tree-shape divergence fails.
- A later release with changed bytes still requires a new version, root and immutable tag. No
  post-release recovery moves a tag; source descriptor/README rollback remains ADR-015's path.
