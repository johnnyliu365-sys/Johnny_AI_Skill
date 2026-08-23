# 08｜Isolated publication live cutover

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-1 through AC-9 |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `BLOCKED / TICKET_DEFECT / UPSTREAM_CLOSURE_CONTRACT` / `CLOSURE_01` |
| Dependency | Tickets 06 and 07 integrated and independently reviewed; exact baseline then recorded before dispatch. |
| Exact development baseline | `2f458316ccfe191cdc5548344f2e323df20ae215` |
| Authorized candidate branch / temporary raw ref | `implement/claude-publication-08-live-cutover` / `refs/heads/verify/claude-publication-08-live-cutover` |
| Effect correlation | `claude-publication-08-20260823` |
| Delivery profile | `POC / HIGH_ASSURANCE`: public repository provisioning, non-fast-forward ref publication, public release metadata and real user-scope installation are named external effects. |
| Model selection | Reassess exact closure after 06/07. Default implementation remains Luna / xhigh with Terra / xhigh review; Terra elevation is allowed only upon a ticket-bound `HardTicketAssessment` proving this closure cannot be further decomposed and exceeds Luna. |
| XSS classification | `N/A` |
| Proposed worktree / branch | `.worktrees/claude-publication-08` / `implement/claude-publication-08-live-cutover` |

## Required owner effect authority before dispatch

The owner must authorize one exact candidate against one exact baseline, naming all of:

1. create/configure public `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`,
   with default branch `main` and no foreign refs;
2. publish one generated root to the repository, creating `plugin-v0.4.10` only if absent and
   updating `main` through the ticket-07 CAS plan/readback;
3. publish one temporary development candidate ref solely to make its immutable raw descriptor
   testable, then remove that temporary ref only after the candidate is integrated or abandoned;
4. integrate and push source URL, Claude version `0.4.10`, generated SHA and README together;
   and
5. run the documented Claude CLI commands in a disposable isolated `CLAUDE_CONFIG_DIR`.

Without this authority the only legal outcome is `WAIT_FOR_HUMAN / OWNER_EFFECT_AUTHORITY_REQUIRED`.
No implementation/review approval substitutes for it.

## Owner authority record — 2026-08-23

The owner approved all five effects above for exactly this source baseline, candidate branch,
temporary raw ref and correlation. The authorized destinations are development repository
`https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git` and publication repository
`https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`; the release is public,
uses default branch `main`, version `0.4.10`, and may create only `plugin-v0.4.10` if absent.

Before every remote mutation, the Terra reviewer must bind the reviewed candidate commit, the
generated publication root `C`, its exact generated SHA, and the fresh remote readback to this
record. The preflight on 2026-08-23 found the publication repository absent and the temporary
development ref absent. A changed remote, non-empty or foreign publication ref set, candidate
branch divergence, missing CLI or a failed generated/readback binding remains a named blocker;
this authority does not permit fallback, tag movement, hand-edited SHA, or a broader push.

## CLOSURE 01 blocker

The reviewer created the authorized public repository and confirmed it was empty, then generated
parentless root `758a7187f6cee5dbb231cd85fe2c4f5d3e03f4b3`; regeneration and generator
verification reproduced that exact root. It committed the permitted generated marketplace pin as
candidate commit `1a536fb781644d79a5b34735839f48a1c5e8c1fa`.

Ticket 06's required local closure proof then returned `TREE_MISMATCH` with only
`.claude-plugin/marketplace.json` in `content_mismatch`. The generator intentionally neutralizes
the self-referential pin carrier while producing `C`, but the repository-closure verifier derives
its expected blob from the live, newly pinned marketplace manifest and has no matching carrier
exception. This is an upstream closure-contract defect, not an admissible Ticket 08 change.

No publication payload, `main`, tag or temporary development ref was pushed. No Claude CLI/cache
operation, source integration or source-main push occurred. The newly created publication
repository remains empty. [Ticket 09](09-pin-carrier-closure-normalization.md) is required before
this ticket may be re-admitted; this ticket must not bypass, hand-edit or weaken the L2 proof.

## Boundary declaration

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = README.md
modify = tests/test_plugin_publication.py
modify = tests/test_publication_repository_closure.py
modify = tests/test_claude_plugin_cache_closure.py
forbid = .codex-plugin/
forbid = library/local_orchestration/plugin_publication.py
forbid = library/local_orchestration/publication_repository_closure.py
forbid = library/local_orchestration/claude_plugin_cache_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = install.ps1
forbid = johnny-install.cmd
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
```

The source candidate updates only Claude distribution metadata, README and the already-owned
test seams. `.codex-plugin` and the Level 2 bundle/wrapper remain unchanged: this is a Claude
publication-source release, not a Codex bundle release. The SHA is generated, never hand-edited.

## Sole observable closure

The exact README commands, run through the real Claude CLI in an isolated config root, install
`johnny-ai-skill@johnny-ai-skill` from the independent publication repository at the generated
`0.4.10` SHA. The raw marketplace cache contains only the descriptor; the plugin cache checkout,
refs and every reachable tree contain only declared payload. The plugin cache may retain `.git`;
it may not retain a reachable development repository tree/object graph.

## Required candidate sequence

1. From the candidate branch set the marketplace `source.url` to the publication repository,
   update Claude manifest/marketplace version to `0.4.10`, and prepare README's raw marketplace
   URL. Generate parentless payload root `C` with the ticket-07 contract.
2. Verify `C` is an exact payload root. Provision/read the publication remote and execute only the
   approved CAS/tag plan. Fetch into a fresh clone and use ticket 06 to prove its full ref/tree
   closure before any development-repository pin changes.
3. Repin the candidate marketplace descriptor to `C`; regeneration must reproduce `C`.
4. Push the candidate ref, use its immutable raw descriptor URL with the actual README command
   form in a disposable `CLAUDE_CONFIG_DIR`, and run ticket-06 installed-cache closure checks.
5. Only if all checks are `VERIFIED` may one candidate integrate through
   `admit_document_mutation` and push development `main`. Re-read the raw main descriptor and
   repeat the isolated install check. If any check fails, leave main at its prior pin; the remote
   payload is inert and is not a reason to bypass the gate.

## TDD, adversarial verification and review

| Cell | Required proof |
| --- | --- |
| L1 metadata/pin | Claude manifest/marketplace JSON validate, use the publication URL, contain version `0.4.10` and full generated SHA; source/pin/tree regeneration agrees. |
| L2 repository closure | Fresh publication clone has only allowed `main`/version-tag refs and parentless declared-payload trees. |
| L3 real marketplace cache | README raw URL adds a descriptor-only marketplace cache; owner/repo marketplace form is not documented as the Level 1 entry. |
| L4 real plugin cache | Actual isolated install has path/blob equality, all reachable refs/commits/trees accepted by ticket 06, and development sentinels unreadable. |
| L5 negative paths | Wrong publication URL, stale pin, extra development ref/tree, changed blob, moved/colliding tag and missing CLI/cache data return a named failure; none is reported as installed/verified. |
| L6 rollback | Failure before integration leaves development main unchanged; a post-integration defect is recoverable by one descriptor/README revert to the previous verified source/version/SHA without moving a tag. |

The Terra reviewer independently adds a reachable development ref/tree to the publication test
fixture or cache after an otherwise green candidate. L2 or L4 must become red; exact restoration
must return green. It also reruns the real CLI proof from a fresh isolated config root rather than
reusing the implementer's cache. Zero-red mutation is a blocking evidence defect.

## Completion

This ticket cannot start until owner effect authority is recorded. Once authorized, all external
commands bind exact target, baseline, candidate SHA, expected old SHA, version tag and correlation,
then capture sanitized readback. The reviewer—not the implementation owner—executes the named
remote/publication effects and guarded integration. A live CLI, remote readback, full suite,
strict type results and cluster review evidence are required before the feature cluster can move
from `CHANGES_REQUESTED`.
