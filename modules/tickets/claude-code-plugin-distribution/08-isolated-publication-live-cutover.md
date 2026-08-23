# 08｜Isolated publication live cutover

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-1 through AC-9 |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `BLOCKED / REQUIREMENT_CHANGED / VERSION_TAG_COLLISION` / `CLOSURE_02` |
| Dependency | Tickets 06, 07 and 09 integrated and independently reviewed; exact baseline then recorded before effect admission. |
| Exact development baseline | `f099ff7f5c7472c38fd0353e31556e06d4016e27` |
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

## CLOSURE 02 re-admission — 2026-08-23

Ticket 09 was independently approved and integrated at
`ca9e988b5b93492de42f604ccf6ef76221111501`; its control-plane closure landed at this ticket's
baseline `f099ff7f5c7472c38fd0353e31556e06d4016e27`. Its shared carrier proof repairs the sole
`CLOSURE_01` L2 contract defect without weakening the ref/tree closure. The earlier candidate,
root and pin remain historical evidence only: they must not be reused as a current source
candidate, publication root or remote plan.

The owner reconfirmed all five already-enumerated effects for this exact new development baseline,
the same candidate branch, temporary raw ref, public repositories, version `0.4.10` and
correlation `claude-publication-08-20260823`. This is a fresh authority binding, not permission to
reuse the old remote readback. Before any mutation, the Terra reviewer must rebase the candidate,
generate and verify one new `C`, bind it to a fresh remote ref-set/default-branch readback and
execute only the ticket-07 plan for that exact `C`. Every L1–L6 proof, including the isolated
Claude install, remains required.

No source boundary, version, tag policy, effect target or rollback rule changed in `CLOSURE_02`.
The previous empty-repository observation and the previously created empty public repository are
facts to re-read, not assumptions or additional authority.

## CLOSURE 02 blocker — installed-cache symbolic remote HEAD

The required fresh, isolated Claude CLI install completed from the immutable candidate raw
descriptor. Its visible plugin checkout resolved to generated root
`b52215eb3ee5dfa101e65c189441e62c20ca45e6`, with `main`,
`origin/main` and `plugin-v0.4.10` naming that root. Claude's ordinary clone also created the
normal symbolic remote-default ref `refs/remotes/origin/HEAD` pointing to
`refs/remotes/origin/main`.

`verify_installed_plugin_cache()` returned the named non-success
`INSTALLED_REF_SET_INVALID` before it could enumerate the otherwise payload-only reachable
commit. Its current ref parser rejects every symbolic ref, including that normal clone ref. L4
requires the actual installed cache's complete ref/commit graph to be accepted; it cannot be
claimed from the visible checkout alone.

This is a second upstream closure-contract defect. It is not repairable in this ticket because
the admitted boundary forbids `library/local_orchestration/claude_plugin_cache_closure.py`.
Accordingly, no development-source integration or development-`main` push occurred. The
authorized publication repository currently has its independently read-back payload root on
`main` and immutable `plugin-v0.4.10`; the temporary candidate source ref remains present for
the unintegrated candidate. Neither ref is moved or removed by this blocker record. A separate
ticket must make the installed-cache checker distinguish an admitted normal remote-default
symbolic ref from a foreign/default-branch mismatch, with actual-cache and reverse-mutation
evidence, before Ticket 08 can be re-admitted.

## Post-Ticket-10 requirement change — payload version/tag collision

Ticket 10 is now integrated and changes
`library/local_orchestration/claude_plugin_cache_closure.py`. `library/` is an enumerated Level 1
publication payload tree, so rebasing this Ticket 08 candidate and regenerating its payload would
produce a root different from the already published
`b52215eb3ee5dfa101e65c189441e62c20ca45e6`. The public publication repository already has that
root on `main` and immutable `plugin-v0.4.10`.

This ticket authorizes only version `0.4.10` and creating that tag when absent; it forbids moving
a tag, hand-editing a SHA and a broader push. Therefore no fresh Ticket 08 candidate can both
contain the integrated cache-closure repair and satisfy its current version/tag authority. The
next action is `ImplementationReturn.CHANGE_DETECTED -> REQUIREMENT_CHANGED`: the architecture
owner must decide the successor release/version and its publication/migration authority, then
update the requirement lineage, SPEC and tickets. Neither descriptor repinning nor Ticket 08
re-admission is legal until that decision is recorded.

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
