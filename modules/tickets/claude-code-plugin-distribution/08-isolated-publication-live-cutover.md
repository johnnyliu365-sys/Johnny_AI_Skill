# 08｜Isolated publication live cutover

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 05, AC-1 through AC-11 |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034`, amended by `PRD-20260823-035` / `CHG-20260823-035`, `PRD-20260823-036` / `CHG-20260823-036` and `PRD-20260823-037` / `CHG-20260823-037` / sealed Context Revision 04, blob `f175d6a6842ca1d24a3cfd85e3a24542e7d7b9a3` |
| State / closure | `CONVERGENCE_REVIEW_REQUIRED / OWNER_EFFECT_AUTHORITY_RECORDED / REVISION_06` |
| Dependency | Tickets 06, 07, 09, 10, 11 and 12 are integrated. Ticket 12 closed the version-specific retained-tag contract at `9a244db4a9c4342476b2a1f59d49b9c15abc59e7`; the fresh CLOSURE_04 authority below replaces the suspended CLOSURE_03 authority. The CLOSURE_03 source candidate remains review evidence only. |
| Historical 0.4.10 development baseline | `f099ff7f5c7472c38fd0353e31556e06d4016e27` |
| Historical 0.4.10 candidate branch / temporary raw ref | `implement/claude-publication-08-live-cutover` / `refs/heads/verify/claude-publication-08-live-cutover` |
| Historical effect correlation | `claude-publication-08-20260823` |
| Delivery profile | `POC / HIGH_ASSURANCE`: public repository provisioning, non-fast-forward ref publication, public release metadata and real user-scope installation are named external effects. |
| Model selection | Reassess exact closure after 06/07. Default implementation remains Luna / xhigh with Terra / xhigh review; Terra elevation is allowed only upon a ticket-bound `HardTicketAssessment` proving this closure cannot be further decomposed and exceeds Luna. |
| XSS classification | `N/A` |
| Future worktree / branch | Record only with fresh owner effect authority; historical branch/ref cannot be advanced as a `0.4.11` candidate. |

## Current authority boundary — 2026-08-23

All text below that names version `0.4.10`, its tag, its former candidate or its external-effect
record is historical evidence only. `plugin-v0.4.10` already exists and is immutable. It neither
authorizes F3 nor a new generated root, descriptor pin, remote mutation, temporary ref, Claude
CLI run, source integration or public release.

F3 is integrated and independently reviewed at `7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7`.
The owner selected successor version `0.4.11`. That selection is not a release authorization:
Ticket 12 is integrated. This ticket remains blocked until the owner records a fresh exact effect
authority for one rebased candidate, remote snapshot, expected-old SHA and correlation. It must
not reuse `0.4.10`, hand-edit a SHA, or advance its historical candidate.

## CLOSURE 04 fresh owner effect authority — 2026-08-24

The project owner authorized this one `0.4.11` live-cutover attempt after P8R-R04 closure. This
record replaces, and does not revive, CLOSURE_03. It authorizes no effect until the Terra reviewer
has committed and bound the fresh candidate described below.

| Binding | Authorized value |
| --- | --- |
| Development baseline | `2fd6908eb0c304ce0dbc48f52ab6268d6d6b204f`, plus this authority record once integrated |
| Candidate worktree / branch | `.worktrees/claude-publication-08-v0411-r02` / `implement/claude-publication-08-v0411-r02` |
| Temporary raw-descriptor ref | `refs/heads/verify/claude-publication-08-v0411-r02-live-cutover` |
| Correlation | `claude-publication-08-v0411-r02-20260824` |
| Publication target / version | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git` / `0.4.11` |
| Read-only remote snapshot | default `main`; `main` = `b52215eb3ee5dfa101e65c189441e62c20ca45e6`; immutable `plugin-v0.4.10` = the same SHA; `plugin-v0.4.11` absent (read 2026-08-24) |

Before every external mutation, Terra must re-read that publication remote and halt unless its
default branch, expected-old `main`, retained tag and absent `plugin-v0.4.11` exactly match this
record. It must bind the reviewer-written candidate SHA, its generator-produced parentless root
`C`, and the exact version/tag/correlation to that fresh readback; a local implementer commit,
historical candidate/root, copied SHA or changed ref set is not authority.

Subject to the preceding source review, reviewer commit, local generator/reachability proof and
fresh readback, this record authorizes Terra only to: (1) publish `C` from the stated expected-old
`main` through Ticket 07's CAS plan and create absent-only `plugin-v0.4.11` at `C`; (2) push the
named development temporary ref solely for the immutable raw-descriptor check, then remove it
only after guarded source integration or owner-directed abandonment; (3) run Ticket 08's actual
README commands in a disposable isolated `CLAUDE_CONFIG_DIR`; and (4) only after verified L1--L6,
integrate and push that same reviewed development candidate. No tag movement, retry on changed
readback, provider invocation, runner/wake claim, user-profile installation, credential output,
other remote mutation or use of CLOSURE_03 is authorized.

## Revision 06 convergence replan — L3 raw-descriptor exclusivity

The revision-05 correction review found an `EVIDENCE_DEFECT`: it rejected a publication-repository
`main` raw URL but accepted an added suspended historical
`verify/claude-publication-08-v0411-live-cutover` URL beside the authorized r02 route. This is
already within L3's approved requirement that the real install use one current development raw
descriptor; no product, version, target, authority or external-effect boundary changes.

The one remaining source correction is limited to `tests/test_plugin_publication.py`. It must pin
the exact two allowed README marketplace-add commands: the authorized r02 candidate raw descriptor
and the post-integration development `main` raw descriptor. Adding either the suspended r01 raw
route or a publication-repository `main` raw route alongside valid text must make the named L3
test red; exact restoration must return green. The reviewer must independently perform at least
one of those additions. The current uncommitted source diff is not a candidate or merge source;
it must be rebound to this revision before one Luna/xhigh correction and a new Terra/xhigh review.

The CLOSURE_04 remote snapshot, expected target, version, temporary r02 ref and correlation remain
binding. Generator execution, publication promotion, temporary-ref push, Claude CLI/cache proof,
source integration and every L1--L6 external effect remain forbidden until this new source closure
is approved and the reviewer writes its candidate commit.

## CLOSURE 03 historical owner effect authority — suspended

The project owner authorizes this exact `0.4.11` Ticket 08 attempt:

| Binding | Authorized value |
| --- | --- |
| Development baseline | `cf2c96ffc4401b493f7a59213a46f80f2b013c45` |
| Candidate worktree / branch | `.worktrees/claude-publication-08-v0411` / `implement/claude-publication-08-v0411` |
| Temporary raw-descriptor ref | `refs/heads/verify/claude-publication-08-v0411-live-cutover` |
| Correlation | `claude-publication-08-v0411-20260823` |
| Publication target | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git` (public, default branch `main`) |
| Read-only pre-authority snapshot | `main` / `HEAD` = `b52215eb3ee5dfa101e65c189441e62c20ca45e6`; `plugin-v0.4.10` = the same SHA; `plugin-v0.4.11` is absent. |

The implementation owner may create and commit only the ticket's source candidate in its declared
worktree. Before every external mutation, Terra must re-read the publication remote and bind the
reviewed candidate SHA, the generator-produced root `C`, the exact current `main` SHA and an
absent `plugin-v0.4.11` to this correlation. A changed/default-branch-invalid/foreign-ref/tag-
present/expected-old mismatch is a named halt; it does not inherit this authority.

Subject to that fresh preflight and the full L1–L6 review evidence, the owner authorizes Terra
only to:

1. update publication `main` from the fresh expected-old SHA to `C` through Ticket 07's guarded
   CAS plan and create immutable `plugin-v0.4.11` at exactly `C` if, and only if, it is absent;
2. push the exact reviewed development candidate to the named temporary ref solely for the
   immutable raw-descriptor test, then remove that temporary ref only after guarded source
   integration or an owner-directed abandonment;
3. run the documented Claude commands using a disposable isolated `CLAUDE_CONFIG_DIR` and read
   only sanitized closure results; and
4. on `VERIFIED` L1–L6 evidence, integrate that same reviewed candidate through
   `admit_document_mutation` and push development `main`.

No other ref, tag, branch, repository, source URL, version, user configuration, credential,
cache, release, deletion or retry is authorized. Credentials remain in the already authenticated
host session and are never read, printed or persisted. A candidate commit/root discovered after
this record is an assertion to bind and re-read before effect, not permission to substitute a
different branch or baseline.

## CLOSURE 03 blocker — immutable historical tag versus current declaration

Luna's local source candidate `73a421d827794f7cf059b74c096d041471b6044f` regenerated the
parentless `0.4.11` root `08330633ef31acdc54e8fa8c38414476faed598a`; it changed only the six
declared paths and performed no external effect. Terra independently verified the candidate,
root, L1/L3/L5 fixtures, focused tests, strict type and compile gates.

On a fresh local publication fixture, `main=C` and `plugin-v0.4.11=C` verify green. A reviewer
development ref correctly returns `REF_SET_INVALID` and restores green after exact deletion. The
authority-required retained `plugin-v0.4.10=b52215eb3ee5dfa101e65c189441e62c20ca45e6`, however,
returns `TREE_MISMATCH`: it has 104 extra paths and six content mismatches against F3's current
declaration, including both Claude manifests and `AGENTS.md`.

The cause is structural: the current L2 verifier evaluates every retained release tag against one
new candidate declaration, while ADR-015 requires immutable historical tags to remain reachable.
F3 intentionally changed that declaration. The two rules cannot both hold for `0.4.10` and
`0.4.11`; moving/deleting the old tag would violate the ticket, ADR and CLOSURE_03 authority.

No publication CAS, new tag, temporary raw ref, Claude CLI/cache operation, source integration
or source-main push occurred. L3–L6 are unexecuted, not passed or waived. This is
`ImplementationReturn.CHANGE_DETECTED -> REQUIREMENT_CHANGED`; CLOSURE_03 authority is suspended
and cannot be reused after the required contract decision.

## CLOSURE 03 resolution — version-specific tag declarations

The owner selected `PRD-20260823-037` / `CHG-20260823-037` and ADR-018. `main` and the fresh
`plugin-v0.4.11` root must remain exact path/blob matches for the reviewed current candidate.
Each retained immutable `plugin-v<semver>` tag instead must be checked against the payload
declaration, generated carrier form and plugin/marketplace version embedded in that tag target.
This preserves strict ref/parent/tree-shape/version closure while truthfully not claiming that an
old target's declared blobs were compared to today's working tree.

Ticket 12 integrated at `9a244db4a9c4342476b2a1f59d49b9c15abc59e7`; it closes L2 with current
candidate path/blob binding and retained-tag own-declaration/version/carrier closure. The prior
CLOSURE_03 effect authority remains suspended. Its candidate/root may not be rebased, published,
pinned, pushed, installed or otherwise advanced under this record; a new authority must bind a
fresh candidate and fresh remote readback.

## Historical owner-effect authority template — not current authority

The following historical record describes the fields a later authority must bind. It is not a
current effect permission: CLOSURE_03 is suspended by the Ticket 12 dependency above.

The owner must authorize one exact candidate against one exact baseline, naming all of:

1. re-read/configure public `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`,
   with default branch `main` and no foreign refs;
2. publish one generated root to the repository, creating `plugin-v0.4.11` only if absent and
   updating `main` through the ticket-07 CAS plan/readback using the fresh expected-old SHA;
3. publish one temporary development candidate ref solely to make its immutable raw descriptor
   testable, then remove that temporary ref only after the candidate is integrated or abandoned;
4. integrate and push source URL, Claude version `0.4.11`, generated SHA and README together;
   and
5. run the documented Claude CLI commands in a disposable isolated `CLAUDE_CONFIG_DIR`.

Without this authority the only legal outcome is `WAIT_FOR_HUMAN / OWNER_EFFECT_AUTHORITY_REQUIRED`.
No implementation/review approval substitutes for it.

## Historical owner authority record — 0.4.10 only

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

## Post-Ticket-10 requirement change — F3 resolution and successor selection

Ticket 10 is now integrated and changes
`library/local_orchestration/claude_plugin_cache_closure.py`. The old Level 1 declaration names
the whole `library/` tree, so rebasing this Ticket 08 candidate and regenerating its payload would
produce a root different from the already published
`b52215eb3ee5dfa101e65c189441e62c20ca45e6`. The public publication repository already has that
root on `main` and immutable `plugin-v0.4.10`.

The old authority permits only version `0.4.10` and creating that tag when absent; it forbids
moving a tag, hand-editing a SHA and a broader push. F3 (`CHG-20260823-035`) reduced the payload
to its reachable reusable surface and integrated at `7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7`.
The owner then selected `0.4.11` under `CHG-20260823-036`. Neither descriptor repinning nor
Ticket 08 re-admission is legal until a fresh exact external-effect record is added.

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
`0.4.11` SHA. The raw marketplace cache contains only the descriptor; the plugin cache checkout,
refs and every reachable tree contain only declared payload. The plugin cache may retain `.git`;
it may not retain a reachable development repository tree/object graph.

## Required candidate sequence

1. From the candidate branch set the marketplace `source.url` to the publication repository,
   update Claude manifest/marketplace version to `0.4.11`, and prepare README's raw marketplace
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
| L1 metadata/pin | Claude manifest/marketplace JSON validate, use the publication URL, contain version `0.4.11` and full generated SHA; source/pin/tree regeneration agrees. |
| L2 repository closure | Fresh publication clone has only allowed `main`/version-tag refs and parentless trees. Current `main`/`plugin-v0.4.11` match the exact current candidate payload; retained tags match only their own in-target declaration, carrier and versions. |
| L3 real marketplace cache | README raw URL adds a descriptor-only marketplace cache; owner/repo marketplace form is not documented as the Level 1 entry. |
| L4 real plugin cache | Actual isolated install has path/blob equality, all reachable refs/commits/trees accepted by ticket 06, and development sentinels unreadable. |
| L5 negative paths | Wrong publication URL, stale pin, extra development ref/tree, changed blob, moved/colliding tag and missing CLI/cache data return a named failure; none is reported as installed/verified. |
| L6 rollback | Failure before integration leaves development main unchanged; a post-integration defect is recoverable by one descriptor/README revert to the previous verified source/version/SHA without moving a tag. |

The Terra reviewer independently adds a reachable development ref/tree to the publication test
fixture or cache after an otherwise green candidate. L2 or L4 must become red; exact restoration
must return green. It also reruns the real CLI proof from a fresh isolated config root rather than
reusing the implementer's cache. Zero-red mutation is a blocking evidence defect.

## Completion

This ticket cannot start until a new exact owner effect authority is recorded. Once authorized, all external
commands bind exact target, baseline, candidate SHA, expected old SHA, version tag and correlation,
then capture sanitized readback. The reviewer—not the implementation owner—executes the named
remote/publication effects and guarded integration. A live CLI, remote readback, full suite,
strict type results and cluster review evidence are required before the feature cluster can move
from `CHANGES_REQUESTED`.
