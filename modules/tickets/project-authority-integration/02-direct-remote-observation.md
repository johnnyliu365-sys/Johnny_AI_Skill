# Ticket 02 — direct remote observation

| Field | Value |
| --- | --- |
| Ticket ID | PAI-02-DIRECT-REMOTE-OBSERVATION |
| State | COMPLETED / INTEGRATED at `9b8e82a48b0997fc63deaf04d931e93857d96246` |
| Acceptance Closure Set | PAI-02-ACS-REVISION-02 |
| Dependency | PAI-01 completed and integrated at 6df6885ea093f1e37899f5252f8e4a1cc4feadb9; its Revision-05 public contract remains frozen. |
| Source specification | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4, Revision 06, ticket order item 02 |
| Requirement / decision / Context | PRD-20260824-038 / CHG-20260824-038 / ADR-20260824-020 / doc/context/project-authority-integration/main.md |
| Source-specification provenance baseline | Specification Revision 06 at main 955d9efd6e0a1f9bf5b2504678ec23095d6d3ee1; provenance only, never an implementation-admission baseline. |
| Implementation admission baseline | Reviewer-established at same-lifetime dispatch: exact HEAD SHA of clean current integration main that already contains this approved ticket tree, recorded as `<implementation-admission-baseline>` in dispatch, return, and independent-review evidence. |
| Delivery profile | POC maturity unchanged; STANDARD intensity from the new shared direct-observation contract and moderate uncertainty; no external-effect signal. |
| Control owner | Current-session Terra / xhigh supervisor-reviewer; the sole Agent-to-Agent orchestrator. |
| Implementation owner | Luna / xhigh under `implementation-standard`; exactly one owner and no helper. |
| Independent reviewer | Terra / xhigh under `ticket-review`; reviewer capability rank must be at least the implementation profile rank. |
| Worktree / branch / task / correlation | Unissued until same-lifetime dispatch. The reviewer alone allocates a repository-contained worktree and branch from clean current integration main, validates Git metadata, binds task/worktree/branch/correlation, and records its exact HEAD as `<implementation-admission-baseline>`. Receipt, live descriptor, host gateway, and runner are NOT_REQUIRED for this same-lifetime lane; they are cross-lifetime-only controls. |
| XSS classification | N/A: no Browser, WebView, HTML/DOM renderer, JavaScript execution, Native bridge, or provider effect. |
| Environment | Local Python 3.11, deterministic in-memory fakes, and `mypy --strict` only. No remote/provider credential, remote/provider CLI, host, runner, process, shell, Git executable, network, environment, filesystem, or clock capability is a dependency. |
| Completion evidence | The integrated source candidate is `9b8e82a48b0997fc63deaf04d931e93857d96246`, a current-main ancestor. Its completion index record is `381a089a8519875134c0f597c1c20f1be51fdb4a`; the feature index records the same integrated commit. |

## One observable closure

Create the one pure direct-observation port boundary. Given a strict authority contract, a strict
observation request, and one supplied fake read result, `observe_declared_remote` classifies it
once into an accepted direct `GitObservation` or exactly one finite failure. It proves that cache
cannot substitute for direct remote truth, repository/ref identity is preserved, time and expected
SHA movement fail closed, and metadata credential material never reaches a public observation.

This is new behavior: named TDD cells record green evidence and restore-backed reverse mutations;
there is no ceremonial baseline-red claim. No real remote is read. Ticket 03 alone consumes this
result for gate/push/readback composition and alone can finalise `AUTHORITY_INTEGRATED`; this
ticket neither changes the frozen Ticket 01 public API nor imports, declares, receives, invokes,
or fakes a `NonForcePushPort`.

At later same-lifetime synchronous dispatch, the reviewer records the clean current integration
main HEAD as `<implementation-admission-baseline>` in dispatch, return, and review evidence. That
runtime-bound SHA, not `955d9efd6e0a1f9bf5b2504678ec23095d6d3ee1` or any ticket/SPEC provenance
SHA, is the source-diff and scope-command start point. Its dynamic binding prevents later
documents-only corrections from making a fixed implementation baseline stale.

## Exact writable boundary

The implementation may modify or create only these three paths:

1. modify `library/local_orchestration/project_authority/__init__.py`;
2. create `library/local_orchestration/project_authority/observation.py`;
3. create `tests/test_project_authority_observation.py`.

```johnny-boundary
modify = library/local_orchestration/project_authority/__init__.py
create = library/local_orchestration/project_authority/observation.py
create = tests/test_project_authority_observation.py
forbid = library/local_orchestration/project_authority/contracts.py
forbid = library/local_orchestration/project_authority/integration.py
forbid = library/local_orchestration/project_authority/collaboration.py
forbid = library/local_orchestration/project_authority/composition.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

No other path is admitted by `implementation-scope-evidence`, including any new untracked path.
The closure forbids a live adapter, production composition, provider, remote URL, credential,
shell/Git/process/network/environment/filesystem/clock access, fetch, retry, loop, polling,
fallback, target-project path, lifecycle finalisation, `AUTHORITY_INTEGRATED` result, receipt,
descriptor, gateway, queue, runner, or bridge machinery.

## Exact public contract and precedence

`observation.py` owns exactly these seven public names, which `__init__.py` re-exports while
preserving all frozen Ticket 01 exports:

| Public interface | Exact contract |
| --- | --- |
| DirectRemoteReadDisposition | Finite enum exactly `OBSERVED`, `UNAVAILABLE`, `NOT_FOUND`, `AMBIGUOUS`. |
| DirectRemoteObservationDecision | Finite enum exactly `ACCEPTED`, `DIRECT_REMOTE_READ_UNAVAILABLE`, `REMOTE_REF_NOT_FOUND`, `REMOTE_REF_AMBIGUOUS`, `REMOTE_IDENTITY_MISMATCH`, `DIRECT_REMOTE_OBSERVATION_STALE`, `AUTHORITY_REF_MOVED`, `SECRET_MATERIAL_DETECTED`. |
| DirectRemoteObservationRequest | Frozen, strict, extra-forbid, revalidating Pydantic model with non-null `authority_contract: ProjectAuthorityContract`, `observation_id: str`, timezone-aware `valid_from: datetime`, timezone-aware `decision_at: datetime`, and nullable `expected_sha: str | None = None`. Construction requires `valid_from <= decision_at`. Null `expected_sha` means initial observation; non-null is revalidated as one full lower-case SHA. |
| DirectRemoteReadResult | Frozen, strict, extra-forbid, revalidating Pydantic model with non-null `disposition: DirectRemoteReadDisposition`, `source: GitObservationSource`, `repository: RemoteRepositoryId`, `full_ref: FullBranchRef`, nullable `sha: str | None`, `observer: str`, `method: str`, `exit_status: int`, timezone-aware `observed_at: datetime`, and `normalized_evidence_digest: str`. `OBSERVED` requires exactly one SHA; every other disposition requires `sha is None`. |
| DirectRemoteObservationResult | Frozen, strict, extra-forbid, revalidating Pydantic model with `decision: DirectRemoteObservationDecision`, nullable `observation: GitObservation | None = None`, and nullable `failure: DirectRemoteObservationDecision | None = None`. `ACCEPTED` carries exactly one direct `GitObservation` and no failure; every failure carries no observation and its finite failure decision. |
| DirectRemoteObservationPort | `Protocol` with exactly `observe(self, request: DirectRemoteObservationRequest, /) -> DirectRemoteReadResult`; the request is positional-only. |
| observe_declared_remote | Pure function with exactly `observe_declared_remote(request: DirectRemoteObservationRequest, port: DirectRemoteObservationPort, /) -> DirectRemoteObservationResult`; it calls `port.observe(request)` exactly once. |

Ordinary model construction rejects null non-nullable values, wrong primitive types, coercion,
extra fields, unknown enum values, naive/inverted times, invalid expected SHA, and invalid
disposition/SHA shapes before it constructs a domain decision. It must not use `Any`, cast,
dynamic member lookup, bypass construction/copy, raw mappings after the boundary, or historical
mutable object reuse to establish a public result.

`observe_declared_remote` has only this fail-closed precedence:

1. strict request/read-result construction;
2. credential-bearing `observer`, `method`, or `normalized_evidence_digest`, yielding
   `SECRET_MATERIAL_DETECTED` without copying that material to a public observation;
3. response repository or full ref different from the request authority contract, yielding
   `REMOTE_IDENTITY_MISMATCH`;
4. `UNAVAILABLE`, `NOT_FOUND`, and `AMBIGUOUS`, mapping one-to-one to
   `DIRECT_REMOTE_READ_UNAVAILABLE`, `REMOTE_REF_NOT_FOUND`, and `REMOTE_REF_AMBIGUOUS`;
5. a source other than `DIRECT_REMOTE_REF`, including `REMOTE_TRACKING_CACHE`, yielding
   `DIRECT_REMOTE_READ_UNAVAILABLE`;
6. `valid_from <= observed_at <= decision_at`, else `DIRECT_REMOTE_OBSERVATION_STALE`;
7. non-null `expected_sha` unequal to observed SHA, yielding `AUTHORITY_REF_MOVED`;
8. only then construct one direct `GitObservation` and return `ACCEPTED`.

Normal unavailable/not-found/ambiguous outcomes are typed port result values, not exceptions.
Unexpected fake-port exceptions are defects and are not converted into a success or finite
authority decision. A fake result or successful process exit proves no live capability.

## TDD and strong-type preflight

| Cell | Category | Required assertion |
| --- | --- | --- |
| PAI-02-T01 | positive / error-code consistency | `test_observe_declared_remote_accepts_one_direct_fake_read` uses a deterministic fake direct result and asserts `ACCEPTED`, exact preserved repository/ref/SHA/observer/method/time/digest in one `GitObservation`, no failure, and exactly one port call. |
| PAI-02-T02 | strong-type preflight / missing values | `test_direct_remote_public_models_are_strict_and_closed` constructs every new enum member, request/read/result success and failure shapes, and a deterministic fake satisfying the Protocol; it rejects unknown enum, null, wrong primitive, coercion, extra field, naive/inverted time, non-full expected SHA, `OBSERVED` without SHA, and non-observed with SHA. |
| PAI-02-T03 | exception behavior / error-code consistency | `test_observe_declared_remote_maps_normal_dispositions_and_preserves_unexpected_exception` proves each of `UNAVAILABLE`, `NOT_FOUND`, and `AMBIGUOUS` maps one-to-one to the exact finite failure with no observation, and an unexpected fake exception is not converted into authority success or a finite decision. |
| PAI-02-T04 | cache boundary | `test_observe_declared_remote_rejects_tracking_cache` supplies `REMOTE_TRACKING_CACHE` and proves `DIRECT_REMOTE_READ_UNAVAILABLE` with no observation. |
| PAI-02-T05 | path identity | `test_observe_declared_remote_rejects_repository_or_ref_mismatch` supplies each mismatched repository/ref result and proves `REMOTE_IDENTITY_MISMATCH` before source/freshness/SHA success. |
| PAI-02-T06 | staleness / race | `test_observe_declared_remote_rejects_stale_or_moved_read` proves both out-of-window observed times return `DIRECT_REMOTE_OBSERVATION_STALE` and a non-null unequal expected SHA returns `AUTHORITY_REF_MOVED`. |
| PAI-02-T07 | security / metadata boundary | `test_observe_declared_remote_rejects_credential_metadata` puts credential-bearing material independently in observer, method, and digest, then proves `SECRET_MATERIAL_DETECTED`, no observation, and no credential copy into a public result. |
| PAI-02-T08 | test truthfulness / source boundary | `test_direct_remote_observation_ast_gate_targets_owned_production_modules` parses only real `__init__.py` and `observation.py`; it requires the exact seven new public names/re-exports, retains Ticket 01 exports, permits only the finite approved import roots, and rejects every forbidden effect/dynamic/bypass symbol including aliases. |

Before implementation and again before the first green run, construct through ordinary public
validators: every disposition and decision member; request values with both null and valid
non-null expected SHA; all valid `DirectRemoteReadResult` disposition shapes; accepted and every
failure `DirectRemoteObservationResult`; existing `ProjectAuthorityContract`,
`RemoteRepositoryId`, `FullBranchRef`, `GitObservationSource`, and `GitObservation`; plus a typed
in-memory fake for `DirectRemoteObservationPort`. The preflight fails closed as
`HALT / TICKET_SCHEMA_INVALID` if any bypass, coercion, unknown enum, nullability violation, or
invalid time/SHA/disposition shape succeeds.

The actual-source T08 gate permits only `__future__`, `datetime`, `enum`, `re`, `typing`,
`pydantic`, and `library.local_orchestration.project_authority.contracts` import roots in
`observation.py`, plus only the relative observation re-export added to existing `__init__.py`
imports. It rejects `Any`, `cast`, `getattr`, `setattr`, `__import__`, `eval`, `exec`,
`model_construct`, `model_copy`, `NonForcePushPort`, `open`, `os`, `pathlib`, `subprocess`,
`socket`, `urllib`, `http`, `requests`, `git`, `shutil`, `time`, `datetime.now`, and
`datetime.utcnow`, including aliases. It reads neither a fixture/copy nor `.git`, local refs,
`.worktrees`, `.claude/worktrees`, environment-dependent paths, or the surrounding checkout.
This C13 guard makes the focused result depend only on explicit model values, the frozen Ticket 01
contract, deterministic fakes, and the declared candidate source seam rather than worktree residue
or local repository facts.

## Required reverse mutations

Each mutation is made only in a disposable overlay of the candidate, must first turn the named
cell red with its expected failure, and must be byte-for-byte restored before the implementation
return:

| Mutation | Required red cell | Property pinned |
| --- | --- | --- |
| Make production call `port.observe` twice | PAI-02-T01 | Exactly one direct fake-port call occurs. |
| Relax a strict field, enum, expected-SHA, time, or disposition/SHA validator | PAI-02-T02 | Construction remains strongly typed and finite. |
| Collapse `UNAVAILABLE`, `NOT_FOUND`, or `AMBIGUOUS` into success, or swallow an unexpected fake exception | PAI-02-T03 | Ordinary failed reads are distinct typed outcomes and defects are not reclassified. |
| Admit `REMOTE_TRACKING_CACHE` as direct authority | PAI-02-T04 | Cache is never direct remote proof. |
| Remove repository/ref equality | PAI-02-T05 | The response must identify the declared authority repository and full ref. |
| Remove freshness or expected-SHA equality | PAI-02-T06 | Stale/moved observations cannot bind an authority base. |
| Remove credential-metadata rejection | PAI-02-T07 | Credential material never becomes public evidence. |
| Add an undeclared public export, forbidden import/call, or dynamic/bypass symbol to real `observation.py` | PAI-02-T08 | The source gate walks production paths and preserves the pure one-port boundary. |

The independent Terra reviewer must perform at least one different-path counter-mutation from the
implementer-reported set. A zero-red mutation is a finding, not completion.

## Verification commands and deterministic result

Run one command at a time in the reviewer-established same-lifetime implementation worktree:

    py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_authority_observation.py
    py -3.11 -m mypy --strict library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/observation.py tests/test_project_authority_observation.py
    py -3.11 -m compileall -q library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/observation.py
    git diff --check <implementation-admission-baseline>
    $committedScopePaths = @(git diff --name-only <implementation-admission-baseline> HEAD)
    $worktreeTrackedScopePaths = @(git diff --name-only <implementation-admission-baseline>)
    $untrackedScopePaths = @(git ls-files --others --exclude-standard)
    $implementationScopeEvidence = @(
        $committedScopePaths
        $worktreeTrackedScopePaths
        $untrackedScopePaths
    ) | Where-Object { $_ -ne "" } | Sort-Object -Unique
    $declaredScopePaths = @(
        "library/local_orchestration/project_authority/__init__.py"
        "library/local_orchestration/project_authority/observation.py"
        "tests/test_project_authority_observation.py"
    ) | Sort-Object
    $scopeDifference = @(Compare-Object -ReferenceObject $declaredScopePaths -DifferenceObject $implementationScopeEvidence)
    if ($scopeDifference.Count -ne 0) { $scopeDifference | Format-Table -AutoSize; throw "HALT / CANDIDATE_SCOPE_MISMATCH" }
    $implementationScopeEvidence

Each command exits zero only after the named green cells and restored mutations. Before either
diff command, the reviewer substitutes the actual runtime-bound SHA for
`<implementation-admission-baseline>`; the literal placeholder is never a source-diff value. The
sorted duplicate-free `implementation-scope-evidence` union combines committed-range paths,
working-tree tracked paths, and untracked paths, and must equal exactly the three declared paths
with no ticket document or other path. The committed range alone is insufficient while the
implementation owner is forbidden to commit; the working-tree tracked input covers the modified
`__init__.py`, while the untracked input covers new paths. Record all three inputs. No command
reads a real remote or performs a provider, repository, host, or other external effect.

## Completion, rollback, and return

The Luna implementation owner changes only the three declared paths and does not commit,
integrate, or push. It returns `ImplementationReturn.COMPLETED` with ticket ID, ACS revision, exact
runtime-bound `<implementation-admission-baseline>`, candidate-worktree identity, named
`implementation-scope-evidence` and its committed-range/working-tree-tracked/untracked inputs, changed paths, green
test/type/compile/diff results, and every mutation's red/restored-green evidence. `BLOCKED`
returns its exact finite reason without workaround. `CHANGE_DETECTED` emits
`REQUIREMENT_CHANGED` and stops source work.

The independent Terra reviewer validates that same runtime baseline and scope evidence, reruns the
declared checks, and records its own different-path counter-mutation. Only after approval, the
Terra reviewer writes the candidate commit and alone submits guarded integration. Rollback is an additive local forward correction or revert of the Ticket 02
candidate; never force-push, rewrite authority history, relabel local success as remote authority,
or create a remote effect. Same-lifetime allocation, wait, review, and guarded integration remain
bridge-free and do not require a receipt, descriptor, host gateway, or runner.
