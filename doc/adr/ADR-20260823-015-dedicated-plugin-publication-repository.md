# ADR-20260823-015 — Claude installs clone a dedicated payload-only repository

- Date: `2026-08-23 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260823-034` / `CHG-20260823-034`
- Affected specification: `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P`
- Corrects: F1 in `doc/reviews/claude-code-plugin-distribution/level-1-shipping-chain-cluster-code-review.md`

## Context

Tickets 02–05 made a publication commit whose checked-out tree is exactly the declared payload,
has no parent and is reachable through a remote ref. That proves the pin and checkout, but not
what Claude Code transfers before checkout.

An isolated live install with Claude Code CLI `2.1.231` on 2026-08-23 established the missing
boundary:

```text
installed checkout files                  243
installed refs/heads/main files           841
installed .git packed objects             989
installed .git bytes                      2,477,546
HEAD                                      c3cb81c4550e6493f9d8478c4be31ffdad642f87
refs/heads/main                            d35689a8f54c3c5481731026701f39621835510a
cat-file main:tests/test_plugin_publication.py   succeeds
```

The marketplace was added through the public raw `marketplace.json`, so its cache contained only
that descriptor. The plugin install nevertheless cloned the repository named by the descriptor's
`source.url`, retained `.git`, checked out the pin and left the cloned development `main` locally
reachable. Raw marketplace delivery fixes the first cache only. `git-subdir`, sparse checkout or
a different marketplace entry syntax still clone the same source repository and therefore cannot
fix the second cache.

The security and distribution boundary is consequently the source repository's reachable object
graph, not only the checkout tree.

## Decision

### 1. Split the control source from the publication source

The development repository remains:

```text
https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git
```

It owns the payload declaration, generator, tests, reviews, requirements, SPEC, tickets and the
public raw marketplace descriptor. It is never again a Claude plugin `source.url`.

The chosen Claude plugin source is a distinct public repository:

```text
https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git
```

It is a publication data plane, not a second development source. No generator, CI checkout,
ticket, test or hand-edited release tree originates there. The development repository produces
the commit; the publication repository only makes that already-verified object reachable.

### 2. Make every reachable publication history safe to clone

The publication repository admits only:

- `refs/heads/main`, naming the currently advertised release; and
- one immutable lightweight `refs/tags/plugin-v<semver>` per retained release.

Every admitted ref names a generator-produced parentless commit. Every such tree is exactly the
payload declared for that release, including blob identity; undeclared paths are absent. Because
each release is a root, tags do not connect releases into a history and no development parent can
enter transitively. Extra branches, tags, symbolic targets or a default branch other than `main`
are release-admission failures.

The plugin manifest and published payload may still contain operator documentation and runtime
library files because those are declared payload. “Payload-only” means exact agreement with the
declaration, not a hard-coded directory blacklist. `tests/`, `doc/` and `modules/` remain useful
sentinels but do not replace the declaration comparison.

### 3. Publish with a guarded, single-candidate transaction

Each release follows this order:

1. In one candidate branch, set the distinct source URL, increment the version and make all other
   release changes. Generate parentless commit `C`, neutralising the pin carrier as the existing
   generator requires.
2. Prove `C` path-for-path and blob-for-blob against the declaration; prove it has no parent.
3. Read the publication remote's default branch and complete ref set. For a first release it must
   be empty. For an update it must satisfy this ADR and `main` must equal the expected old SHA.
4. Push `C` to `main` with exact compare-and-swap semantics
   (`--force-with-lease=refs/heads/main:<expected-old-sha>`), because independent root commits
   cannot fast-forward. Create `plugin-v<semver>` only if absent; never move a version tag.
5. Read back the remote ref set, fetch into a clean repository, and repeat the parent and payload
   closure checks. Only then set the candidate marketplace SHA to `C`; regenerating from that
   candidate must reproduce `C`.
6. Expose the candidate descriptor through an immutable candidate commit URL and run the actual
   documented Claude marketplace-add/install sequence in an isolated `CLAUDE_CONFIG_DIR`.
7. Only a green closure result may enter the existing guarded integration. Source URL, version,
   pin and public instructions land together, so `main` never records a generator change with an
   old source or an unreachable pin.

The publication push is intentionally before development-repository integration: an unreferenced
payload in the publication remote is inert, while a descriptor on `main` that points at an absent
payload is a user-visible outage.

### 4. Test the installed Git boundary, not just its checkout

The Level 1 end-to-end verifier must use the real Claude CLI and the README commands. It proves:

1. the raw marketplace cache contains only the expected descriptor and no cloned development
   repository;
2. the installed visible paths and blob IDs equal the payload declaration;
3. the plugin cache's Git refs are enumerated, every commit reachable from every ref is
   enumerated, and `git ls-tree -r` for each commit has an empty payload difference;
4. every reachable commit is parentless, the installed pinned `HEAD`, publication `main` and the
   version tag resolve as declared, and known development-only sentinels cannot be read; and
5. a reviewer-owned reverse mutation that introduces a development ref/tree makes the verifier
   red before the real repository is accepted.

The assertion is not “there is no `.git`”. Claude owns that installation shape. The assertion is
“the `.git` object graph Claude retained contains no reachable tree outside the declared payload.”

### 5. Keep recovery one descriptor change away

The previous descriptor commit and immutable publication tag remain the rollback facts. If remote
publication or post-push installation readback fails, no new descriptor is integrated. If a fault
appears after integration, revert the development repository's descriptor/README candidate to the
last verified source URL, version and SHA; do not rewrite a version tag. Orphaned parentless
payload objects are harmless and may be collected later by the hosting provider.

Repository creation, visibility, default-branch setup and ref pushes are external effects. A
future ticket must name them and receive owner authority; this ADR does not execute them.

## Alternatives rejected

- **Change only README to a raw marketplace URL.** This avoids the marketplace repository clone
  but does not change the plugin repository cloned from `source.url`; the live probe disproved it.
- **Use `git-subdir`, sparse checkout or partial clone against the development repository.** The
  source object graph and reachable development refs remain the wrong trust boundary, and Claude
  controls the clone flags.
- **Delete `.git` after installation.** The project does not own Claude's cache lifecycle; a
  post-install scrub races updates and converts source isolation into an unproved cleanup task.
- **Publish payload commits as a branch in the development repository.** A clone also receives
  the development default branch, which is the observed defect.
- **Copy and commit a hand-maintained payload tree.** That creates a second source of truth and
  discards the generator/declaration binding already proved by tickets 02–05.

## Consequences

- The project gains one public repository and a guarded non-fast-forward publication operation.
- A release payload change requires a version increment, a new parentless commit and a new
  immutable tag; republishing different bytes under one version is forbidden.
- The existing generator remains authoritative and reusable. Its current root-commit property is
  now also the publication repository's history boundary.
- The Claude distribution Context and SPEC are stale until revised. No implementation ticket may
  use this ADR alone as source authority.
- The Level 1 cluster remains `CHANGES_REQUESTED`; tickets 02–05 stay approved within their own
  boundaries, while publication-source isolation and real-CLI closure remain to be ticketed.
