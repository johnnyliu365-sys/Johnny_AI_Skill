# Claude Code plugin distribution — Revision 03 publication isolation and payload topology

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| Status | `APPROVED / REVISION_03 / REVIEWER_DECOMPOSITION_AUTHORIZED` |
| Author / baseline | Architecture owner / `control/claude-plugin-payload-topology-r03` / `1caa2f2355638c75610dc848b5bd23d8f97d0bcb` |
| Feature Context | `doc/context/claude-code-plugin-distribution/claude-code-plugin-distribution-r02-payload-topology.md`, sealed `REVISION_02`, blob `f53b2a7dedf055e50ad44804e590f22991a3d5c9` |
| PRD / change | `PRD-20260802-005` / `CHG-20260802-005`, amended by `PRD-20260823-034` / `CHG-20260823-034` and `PRD-20260823-035` / `CHG-20260823-035` |
| Architecture | `ADR-20260823-015-dedicated-plugin-publication-repository.md`; `ADR-20260823-017-level-one-payload-topology.md` |
| Delivery stage / profile | `POC / STANDARD` for F3's local declaration closure; `POC / HIGH_ASSURANCE` remains mandatory for repository creation, remote ref mutation, release publication and a user-installed supply-chain boundary. |
| Implementation language | Python 3.11 for publication verification/promotion contracts; frozen Pydantic DTOs, finite enums and `mypy --strict`. Manifests remain JSON validated at their boundary. |
| XSS classification | `N/A`: this feature accepts no Browser/WebView/HTML/DOM/JavaScript input or renderer. |

## Problem, goal and non-goals

The existing payload generator makes a parentless commit whose checked-out tree is correct, but
Claude Code clones the repository named by marketplace `source.url` before checking out that pin.
The development repository therefore reaches the installed plugin cache even when the visible
checkout contains exactly the 243 declared files. A live isolated Claude CLI 2.1.231 probe found
989 packed objects, a 2,477,546-byte `.git`, the 841-file development `main` ref and a readable
development-only test file in the cache.

The goal is that an ordinary user installs the same detachable skill from the documented Claude
commands without receiving the development repository's reachable Git object graph. Git metadata
owned by Claude may remain; every reachable tree inside it must be an exact declared payload.
The declared payload itself must exclude host-local publication/cache/installer tooling, so a
repair to that tooling cannot continually change the release root it is trying to verify.

In scope:

- a distinct public publication repository at
  `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`;
- a typed, fail-closed remote closure and promotion contract for generator-produced payload roots;
- marketplace source URL, semantic version and SHA repinning as one release candidate;
- a raw development-repository marketplace descriptor at
  `https://raw.githubusercontent.com/johnnyliu365-sys/Johnny_AI_Skill/main/.claude-plugin/marketplace.json`;
- a segment-exact Level 1 reusable-source topology that excludes
  `library/local_orchestration/` and standalone host installer entrypoints;
- real Claude CLI closure evidence in an isolated `CLAUDE_CONFIG_DIR`; and
- README installation, update and rollback instructions that name only verified behavior.

Out of scope:

- copying skills, runtime code, configuration or dependencies into a company project;
- replacing the existing payload declaration/generator with a hand-maintained release tree;
- deleting or modifying Claude-owned cache metadata after installation;
- a package registry, service, runner, queue, webhook, hook, MCP server, secret or automatic
  release mechanism; and
- changing Codex plugin distribution, target-project workflow semantics or the user's detach
  guarantee.

## User flow, error flow and external-effect boundary

The supported user path is:

```text
raw marketplace descriptor → claude plugin marketplace add <raw URL>
                           → claude plugin install johnny-ai-skill@johnny-ai-skill --scope user
                           → plugin cache clone of the publication repository at an exact SHA
```

The raw URL addresses only marketplace-descriptor caching. The descriptor's `source.url` addresses
the plugin clone. The two controls are both required: a raw descriptor plus a development
`source.url` remains a failure, and a publication `source.url` plus owner/repo marketplace add
still clones the development repository into the marketplace cache.

All external effects are explicit, owner-bound and read back:

| Effect | Required authority and result |
| --- | --- |
| Create/configure the public publication repository | Exact owner, repository URL, public visibility, default branch `main`, empty expected ref set and post-create readback. |
| Push a publication root or update `main` | Exact expected-old SHA, candidate SHA, correlation and remote ref/tree readback; a mismatch fails closed. |
| Create a release tag | Exact `plugin-v<semver>` name and candidate SHA; it must be absent before the push and equal the candidate afterwards. |
| Push a development candidate / integrate it into main | Exact baseline, candidate SHA, descriptor SHA and guarded document mutation evidence. |
| Run a real user-scope install | Disposable isolated `CLAUDE_CONFIG_DIR`, exact CLI path/version and sanitized closure result; no user configuration is altered. |

No ticket, test pass or review approval authorizes any listed effect by itself. Credentials are
never copied into source, output, tickets, evidence or prompts; an authenticated Git/CLI host may
be used only through its already-authorized session and returns sanitized identifiers/results.

## Architecture, domain model and responsibility boundaries

### Repository topology

```text
development repository
  ├─ authoritative payload declaration, generator, tests, Context/SPEC/tickets/reviews
  ├─ public raw .claude-plugin/marketplace.json
  └─ never used as Claude plugin source.url

publication repository
  ├─ refs/heads/main → current parentless generated payload root
  ├─ refs/tags/plugin-v<semver> → immutable same root for each retained release
  └─ no development ref, parent, tree, blob or hand-authored source
```

`main` and lightweight `plugin-v<semver>` tags are the only allowed publication refs. Every
reachable commit is parentless and has a tree whose paths and blob IDs exactly equal the payload
declared by the same candidate. An unknown ref, a non-`main` default branch, a parent, an
undeclared/missing/different blob, a moved tag or a stale `main` is a named rejection, never a
warning or automatic cleanup.

The existing generator remains the only payload author. It neutralizes the self-referential
marketplace SHA inside the generated payload; after the remote root is proved reachable, the
development candidate's marketplace descriptor records that root. Regenerating from the repinned
candidate must reproduce the same root. No publication repository file is hand edited.

### Typed contract

Production implementation must use named, frozen types; the notation below defines the finite
domain and does not authorize dynamic mappings or string conventions inside the boundary.

```text
struct PublicationRepositoryRef { HttpsGitUrl value; }
struct PublicationCommit { FullGitSha value; }
struct PublicationVersion { SemVer value; }
enum PublicationRefKind { MAIN, RELEASE_TAG }
struct PublicationRef {
  PublicationRefKind kind;
  NonEmptyGitRefName name;
  PublicationCommit target;
}
struct PublicationTreeDifference {
  tuple<RelativePayloadPath> missing;
  tuple<RelativePayloadPath> extra;
  tuple<RelativePayloadPath> content_mismatch;
}
enum PublicationClosureStatus {
  VERIFIED, REMOTE_UNREACHABLE, REMOTE_NOT_EMPTY, DEFAULT_BRANCH_INVALID,
  REF_SET_INVALID, MAIN_MISSING, TAG_COLLISION, STALE_MAIN,
  COMMIT_NOT_ROOT, TREE_MISMATCH, PIN_MISMATCH, READBACK_MISMATCH
}
struct PublicationRemoteSnapshot {
  PublicationRepositoryRef repository;
  GitRefName default_branch;
  tuple<PublicationRef> refs;
}
struct PublicationPromotionRequest {
  PublicationRepositoryRef repository;
  optional<PublicationCommit> expected_main;
  PublicationCommit candidate;
  PublicationVersion version;
  CorrelationId correlation;
}
struct PublicationClosureResult {
  PublicationClosureStatus status;
  optional<PublicationRemoteSnapshot> snapshot;
  optional<PublicationTreeDifference> difference;
}
enum InstallClosureStatus {
  VERIFIED, CLI_UNAVAILABLE, MARKETPLACE_CACHE_MISMATCH,
  PLUGIN_CHECKOUT_MISMATCH, INSTALLED_REF_SET_INVALID,
  INSTALLED_HISTORY_INVALID, INSTALLED_TREE_MISMATCH, SENTINEL_REACHABLE
}
```

### Level 1 payload topology

The payload declaration is an allowlist of the following directory trees:

```text
.claude-plugin/                 commands/                 skills/                 template/
library/NLP/                    library/功能集群/          library/金流串接/
library/catalog/                library/workflow_router/
```

It additionally names exact `library/__init__.py` and `library/MODULE_CATALOG.md` files and the
existing root skill-governance documents. Tree membership is a clean, segment-exact relative-path
prefix; it never arises from merely sharing the top-level `library` segment. The declaration must
not name `library/`, `library/local_orchestration/`, `install.ps1` or `johnny-install.cmd`.

`library/local_orchestration/` contains host-local installation, publication, cache and runner
tools. It is not a Level 1 Claude runtime and its catalog entry is not `READY` in the installed
payload. `AGENTS.md` still defines repository-contained worktree policy directly. Level 2 keeps
its separately owned payload declaration untouched.

All source input is normalized at the Git/CLI boundary. Full SHAs, version strings, ref names,
paths, command results and JSON are validated before they enter these contracts. `Any`, casts,
unvalidated JSON/dicts, partial SHAs, inferred default branches and source-text heuristics cannot
establish `VERIFIED`.

### Promotion transaction and recovery

For one candidate, in this exact order:

1. Update the development candidate's publication URL, version and release material; generate
   parentless commit `C` and prove `C` against its payload declaration.
2. Read the publication repository. A first release requires an empty repository; an update
   requires the allowed ref set and exact expected `main` SHA.
3. Push `C` to `main` using exact compare-and-swap semantics. Independent roots require
   `--force-with-lease=refs/heads/main:<expected-old-sha>` on updates. Create the immutable
   `plugin-v<semver>` tag only when it is absent.
4. Read back the remote and fetch it into a clean repository. Repeat allowed-ref, root-parent and
   path/blob closure checks. Only then repin the development candidate to `C`; regeneration must
   still yield `C`.
5. Publish the candidate descriptor at an immutable candidate commit URL and run the real CLI
   closure verifier. Only `VERIFIED` can enter guarded integration; source URL, version, SHA and
   README land in the same development-repository candidate.

If a check before integration fails, development `main` remains unchanged. A new, unreferenced
parentless publication object is inert. If a defect is discovered after integration, revert the
development descriptor and README to the last verified source URL/version/SHA; never move or
reuse a release tag. A stale main, ref collision, failed readback or failed CLI proof is a
forward-fix/revert decision for the owner, not an automatic retry.

## Acceptance criteria

1. The marketplace descriptor is delivered from the documented raw development-repository URL,
   while its one plugin entry names the exact publication repository URL and a full 40-hex
   publication SHA; it never names the development repository as `source.url`.
2. The publication repository's default branch is exactly `main`; its complete remote ref set is
   only `main` plus zero or more immutable `plugin-v<semver>` tags. Every ref resolves to a
   parentless generator-produced commit whose tree has zero payload difference.
3. A fresh release creates a new versioned root and immutable tag. A changed payload cannot reuse
   a version/tag. A stale expected `main`, unexpected remote ref, moved/colliding tag, missing
   root, wrong default branch or tree difference is rejected before repinning development main.
4. The promotion contract performs no implicit remote effect. Its tests use disposable local Git
   fixtures; a real repository creation/push requires a ticket-bound owner authority and exact
   readback.
5. A real Claude CLI run uses the README commands and an isolated `CLAUDE_CONFIG_DIR`. Its raw
   marketplace cache contains only the expected descriptor; its visible plugin checkout's paths
   and blobs equal the payload declaration.
6. The same real install enumerates every installed plugin-cache ref and each reachable commit.
   Every commit is parentless and every `git ls-tree -r` result has zero payload difference.
   Development-only `tests/`, `doc/` and `modules/` sentinels are unreachable; a visible
   checkout that is correct while a development ref remains reachable is a failure.
7. The verifier has a reviewer-run reverse mutation that adds a development ref/tree to a
   publication fixture and turns the closure red. Byte-for-byte restoration returns it green.
8. README tells users the exact add/install/update/removal commands, does not claim that Claude
   performs no Git clone, does not require a development-repository clone, and states that
   publication creation/promotion is an owner-controlled release operation.
9. JSON validation, payload/publication tests, strict typing and the full project suite pass in a
   clean clone. The feature-cluster review remains `CHANGES_REQUESTED` until the live cutover
   evidence is independently reviewed.
10. F3's source candidate proves that every declared nested tree is clean and segment-exact; no
    `library/local_orchestration/` path or standalone installer enters Level 1. A reviewer-owned
    reverse mutation adds one such forbidden declaration/path and turns the topology proof red;
    byte-for-byte restoration returns it green. Removing a retained catalog/router surface path
    also turns the closure red. No Level 2 payload-list change is admitted.

## Test seams, TDD and verification

- Unit seams accept a typed `PublicationRemoteSnapshot` and an injected Git boundary; they prove
  empty-first-release, valid update, unknown ref, wrong default branch, non-root commit, payload
  difference, stale main, tag collision and readback mismatch without a network effect.
- A disposable bare local repository supplies positive and negative publication fixtures. Its
  negative fixture adds a development branch/tree; the verifier must return a finite failure.
- F3's declaration tests use a manifest fixture with nested tree paths, an undeclared
  `library/local_orchestration/` probe and a retained catalog/router closure probe. They prove
  nested-path validation once in the generator and use its same membership rules in the release
  tree and closure scanner.
- The real-CLI seam receives an explicit executable path, isolated config root, raw descriptor
  URI, publication URL and expected SHA. It does not discover credentials, alter the user's
  configured marketplaces or substitute a mock for acceptance evidence.
- Before dispatch and before an implementer's first red, strong-type preflight constructs every
  public DTO/enum/result through ordinary validators; bypass-built inputs are negative-only.
- `mypy --strict`, project JSON/skill validators, scoped unit tests, payload/publication tests and
  a clean-clone full suite are required. The final cutover ticket adds the real CLI proof and
  reviewer-owned reverse mutation.

## Compatibility, security and deployment prerequisites

- Existing installed version `0.4.9` remains usable from its current source until a complete new
  candidate is published and verified. `plugin-v0.4.10` is immutable. F3 deliberately chooses no
  successor version; a changed F3 payload requires an owner-selected new version/tag before the
  Ticket 08 release path can resume.
- Company projects receive no files or configuration. Removing the plugin remains user-scoped.
- The publication repository is public read and least-privilege write. No token, SSH private key,
  cookie, authorization header or credential diagnostic becomes project evidence.
- There is no deployment. Public repository provisioning, remote ref publication and the release
  README are the external effects; each requires explicit target, action, owner, baseline,
  correlation and post-effect readback.

## Implementation handoff and lineage

- `ImplementationHandoff` may record only approved SPEC/ticket/Context/AC identifiers,
  revisions, role bindings and evidence digests. It may not carry raw context, paths, URIs,
  prompts, CLI output, credentials or PII.
- `ImplementationReturn.COMPLETED` emits `ACTION_COMPLETED`; `BLOCKED` halts; and
  `CHANGE_DETECTED` emits `REQUIREMENT_CHANGED` and returns to change control. An implementer
  cannot alter repository topology, effect authority, release acceptance or public contract.
- Sealed Context binding: `doc/context/claude-code-plugin-distribution/claude-code-plugin-distribution-r02-payload-topology.md`
  Revision 02, blob `f53b2a7dedf055e50ad44804e590f22991a3d5c9`.
- Active requirement leaves: `PRD-20260823-034` / `CHG-20260823-034` and
  `PRD-20260823-035` / `CHG-20260823-035` at
  `doc/requirements/active/2026/distribution/`.
- No shared Context may be amended from the ticket/implementation/review lanes. Any topology,
  ownership, capability or acceptance change is `REQUIREMENT_CHANGED`.

## Revision signatures and approval record

| Date | Authority / baseline | Decision |
| --- | --- | --- |
| 2026-08-02 | Project owner | Approved the original private-development-repository Claude distribution POC. |
| 2026-08-23 | Architecture-owner draft / `295de85297b9d2e7720b6aa592aac3418490595b` | Drafted Revision 02 under `CHG-20260823-034` and `ADR-20260823-015`; owner approval is pending. |
| 2026-08-23 | Project owner / exact draft `f3af1736b0f292476fb555a553a1c40d6416c3e2` | Approved Revision 02 and sealed Context Revision 01; reviewer decomposition is authorized. |
| 2026-08-23 | Project owner / `PRD-20260823-035` / `CHG-20260823-035` | Approved Revision 03 and sealed Context Revision 02: Level 1 names only the reachable reusable-source surface; host-local control tooling and installer entrypoints are excluded before a successor version is chosen. |

The approval applies to the exact draft named above. This candidate changes only lifecycle and
approval metadata, binds the resulting sealed Context blob, and opens the `TICKETS` stage; it does
not authorize repository creation, remote ref mutation, release publication or user installation.
