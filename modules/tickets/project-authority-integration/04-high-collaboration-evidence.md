# Ticket 04 — high-collaboration evidence

| Field | Value |
| --- | --- |
| Ticket ID | PAI-04-HIGH-COLLABORATION-EVIDENCE |
| State | COMPLETED / INTEGRATED at `75d1ed9477c54312ed55d4d532e098b51d240928` |
| Acceptance Closure Set | ACS-PAI-04 Rev.01 |
| Dependencies | PAI-01 integrated at `6df6885ea093f1e37899f5252f8e4a1cc4feadb9`; PAI-02 integrated at `9b8e82a48b0997fc63deaf04d931e93857d96246`; PAI-03 integrated at `98bafbab01e51d2bd3edf6079cda981710651e80`. |
| Source specification | Project authority integration SPEC Revision 10, owner-selected provider-neutral admission seam. |
| Context / change / architecture | `doc/context/project-authority-integration/main.md`; `PRD-20260824-038` / `CHG-20260824-038`; `ADR-20260824-020`. |
| Planning baseline | main at `8db99208d6b363f7b34a731989a4a7085cb0da00`; the implementation-admission baseline is the clean current integration main recorded by the reviewer at dispatch. |
| Delivery / model | POC pure-source closure; Luna/xhigh implementation owner, Terra/xhigh supervisor-reviewer. The reviewer capability is not lower than the implementer capability. |
| Effect boundary | Deterministic in-memory fake `PullRequestReadPort` and `ProviderPolicyReadPort` only. No provider read, UI action, policy configuration, merge, remote mutation, credential, shell, Git executable, process, network, filesystem, environment, clock, runner, queue, receipt, descriptor, host gateway, or second integration gate. |
| Completion evidence | Terra review approved the five-path candidate after 29 focused tests, strict mypy, compileall, exact scope evidence, seven implementer reverse mutations, two corrective reverse mutations, and an independent base-ref source counter-mutation. `admit_document_mutation` integrated candidate `75d1ed9477c54312ed55d4d532e098b51d240928`; local, tracking, and direct `origin/main` readback matched it. |

## One observable closure

Implement the owner-selected single provider-neutral
`admit_high_collaboration_evidence(...)` API. It receives one strict request and two injected
read-only fake ports. For `HIGH_COLLABORATION`, it returns `ACCEPTED` only when one current,
reviewable ticket PR has the exact candidate head and declared authority base, its approval binds
that head, and one provider-policy read proves both UI-bypass prevention and stale-approval
invalidation. It is evidence admission only: neither a green PR nor an accepted result can
integrate, push, merge, change provider policy, or replace `finalize_authority_integration(...)`.

For `SINGLE_BRANCH`, the same API returns `NOT_APPLICABLE` before either port is called. This is
the explicit no-ceremony path; it neither treats an unavailable provider as a failure nor changes
the separate direct-base, guarded-integration, push, or direct-readback requirements.

This is new behavior. Record green evidence for every named cell and restore-backed reverse
mutations; do not claim ceremonial baseline-red evidence. No live provider capability is claimed
by a fake result.

## Exact writable boundary

```johnny-boundary
modify = library/local_orchestration/project_authority/__init__.py
create = library/local_orchestration/project_authority/collaboration.py
modify = tests/test_project_authority_observation.py
modify = tests/test_project_authority_finalization.py
create = tests/test_project_authority_collaboration.py
forbid = library/local_orchestration/project_authority/contracts.py
forbid = library/local_orchestration/project_authority/observation.py
forbid = library/local_orchestration/project_authority/integration.py
forbid = library/local_orchestration/project_authority/composition.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = modules/
forbid = doc/
forbid = skills/
```

At dispatch, the Terra reviewer records clean current integration main as
`<implementation-admission-baseline>`. The sorted duplicate-free
`implementation-scope-evidence` is exactly the union of:

```powershell
$committedScopePaths = @(git diff --name-only <implementation-admission-baseline> HEAD)
$worktreeTrackedScopePaths = @(git diff --name-only <implementation-admission-baseline>)
$untrackedScopePaths = @(git ls-files --others --exclude-standard)
$implementationScopeEvidence = @(
  $committedScopePaths + $worktreeTrackedScopePaths + $untrackedScopePaths |
    Where-Object { $_ -ne "" } |
    Sort-Object -Unique
)
$declaredScopePaths = @(
  "library/local_orchestration/project_authority/__init__.py"
  "library/local_orchestration/project_authority/collaboration.py"
  "tests/test_project_authority_observation.py"
  "tests/test_project_authority_finalization.py"
  "tests/test_project_authority_collaboration.py"
) | Sort-Object
$scopeDifference = @(Compare-Object -ReferenceObject $declaredScopePaths -DifferenceObject $implementationScopeEvidence)
if ($scopeDifference.Count -ne 0) { $scopeDifference | Format-Table -AutoSize; throw "HALT / CANDIDATE_SCOPE_MISMATCH" }
$implementationScopeEvidence
```

The committed range alone is insufficient while the implementation owner is forbidden to commit;
the working-tree and untracked inputs are mandatory. No ticket, specification, requirement,
architecture, governance, source outside this boundary, provider configuration, remote, or
runtime-root path is admitted.

## Exact public contract and precedence

`collaboration.py` owns exactly these public names. Every model is frozen, strict,
`extra="forbid"`, revalidates instances, rejects null for non-null fields, rejects wrong primitive
types/coercion/extra values, and uses only full lower-case SHAs and timezone-aware datetimes.
`__init__.py` re-exports these names after the frozen Ticket 01, Ticket 02, and Ticket 03 export
sequences, in the order below.

| Public interface | Exact contract |
| --- | --- |
| PullRequestReadDisposition | Finite enum exactly `OBSERVED`, `UNAVAILABLE`, `NOT_FOUND`, `AMBIGUOUS`. |
| PullRequestState | Finite enum exactly `OPEN`, `DRAFT`, `CLOSED`, `MERGED`. |
| PullRequestReadRequest | Non-null `authority_contract: ProjectAuthorityContract`, nonblank `ticket_id` and `read_id`, full lower-case `candidate_sha`, and timezone-aware `valid_from` / `decision_at`; construction requires `valid_from <= decision_at`. |
| PullRequestReadResult | Strict fake-port result with disposition; nullable repository, ticket/PR IDs, state, head ref/SHA, base ref, approval-head SHA, observer, method, bounded exit status, observed time, and normalized digest. `OBSERVED` requires every field except nullable `approval_head_sha`; each other disposition requires all evidence fields to be null. A non-null SHA is a full lower-case SHA, refs are `FullBranchRef`, and supplied metadata is nonblank and credential-free. |
| PullRequestEvidence | Normalized immutable ticket PR evidence: repository, ticket ID, PR ID, `PullRequestState`, head ref/SHA, base ref, nullable approval-head SHA, observer, method, exit status, observed time, and digest. It is constructed only from an `OBSERVED` matching result. |
| PullRequestReadPort | `Protocol` with exactly `read(self, request: PullRequestReadRequest, /) -> PullRequestReadResult`. |
| ProviderPolicyReadDisposition | Finite enum exactly `OBSERVED`, `UNAVAILABLE`, `AMBIGUOUS`. |
| ProviderEnforcementCapability | Finite enum exactly `NOT_APPLICABLE`, `PROVEN`, `UNPROVEN`, `UNSUPPORTED`. |
| ProviderPolicyReadRequest | Non-null `authority_contract: ProjectAuthorityContract`, nonblank `ticket_id` and `read_id`, full lower-case `candidate_sha`, and timezone-aware `valid_from` / `decision_at`; construction requires `valid_from <= decision_at`. |
| ProviderPolicyReadResult | Strict fake-port result with disposition; nullable repository, full ref, gate ID/revision, capability, UI-bypass boolean, stale-approval boolean, policy-ID tuple, observer, method, bounded exit status, observed time, and digest. `OBSERVED` requires all fields; each other disposition requires every evidence field to be null. `policy_ids` is a tuple of nonblank credential-free strings with no duplicates. |
| ProviderEnforcementEvidence | Normalized immutable evidence: repository, full ref, gate ID/revision, `ProviderEnforcementCapability`, both distinct booleans, policy IDs, observer, method, exit status, observed time, and digest. It is constructed only from an `OBSERVED` matching result. |
| ProviderPolicyReadPort | `Protocol` with exactly `read(self, request: ProviderPolicyReadRequest, /) -> ProviderPolicyReadResult`. |
| HighCollaborationAdmissionDecision | Finite enum exactly `ACCEPTED`, `NOT_APPLICABLE`, `PR_REQUIRED`, `PR_NOT_REVIEWABLE`, `PR_HEAD_SHA_MISMATCH`, `PR_BASE_REF_MISMATCH`, `PR_APPROVAL_STALE`, `PROVIDER_ENFORCEMENT_UNPROVEN`, `PROVIDER_ENFORCEMENT_UNSUPPORTED`, `REMOTE_IDENTITY_MISMATCH`, `SECRET_MATERIAL_DETECTED`. |
| HighCollaborationAdmissionRequest | Non-null `authority_contract: ProjectAuthorityContract`, nonblank `ticket_id`, full lower-case `candidate_sha`, nonblank distinct `pull_request_read_id` / `policy_read_id`, and timezone-aware `valid_from` / `decision_at`; construction requires `valid_from <= decision_at`. |
| HighCollaborationAdmissionResult | Strict result with decision, nullable `pull_request_evidence`, nullable `provider_enforcement_evidence`, and nullable failure of the same decision enum. `ACCEPTED` carries both evidence and no failure; `NOT_APPLICABLE` carries neither evidence nor failure; every other decision carries neither evidence and its identical finite failure. |
| admit_high_collaboration_evidence | Pure function exactly `admit_high_collaboration_evidence(request: HighCollaborationAdmissionRequest, pull_request_port: PullRequestReadPort, policy_port: ProviderPolicyReadPort, /) -> HighCollaborationAdmissionResult`. |

The function has this fixed fail-closed precedence:

1. strict request construction; `SINGLE_BRANCH` returns `NOT_APPLICABLE` without either port call;
2. one `pull_request_port.read(...)` call; credential-bearing result metadata yields
   `SECRET_MATERIAL_DETECTED` without copying it to a result;
3. PR repository different from the declared authority repository yields
   `REMOTE_IDENTITY_MISMATCH`; a missing PR maps `NOT_FOUND` to `PR_REQUIRED`, and
   `UNAVAILABLE` / `AMBIGUOUS` to `PR_NOT_REVIEWABLE`;
4. an observed PR must match ticket ID, be `OPEN`, and lie inside the request time window; failure
   is `PR_NOT_REVIEWABLE`; then its head SHA, base ref, and non-null approval-head SHA must equal
   respectively candidate SHA, declared authority ref, and observed head SHA, yielding
   `PR_HEAD_SHA_MISMATCH`, `PR_BASE_REF_MISMATCH`, or `PR_APPROVAL_STALE`;
5. one `policy_port.read(...)` call occurs only after the PR passes; credential metadata yields
   `SECRET_MATERIAL_DETECTED`; repository, full ref, gate ID, or gate revision mismatch yields
   `REMOTE_IDENTITY_MISMATCH`;
6. `UNAVAILABLE`, `AMBIGUOUS`, `UNPROVEN`, a false UI-bypass outcome, or a false stale-approval
   outcome yields `PROVIDER_ENFORCEMENT_UNPROVEN`; `UNSUPPORTED` yields
   `PROVIDER_ENFORCEMENT_UNSUPPORTED`; only `PROVEN` plus two true outcomes and at least one
   policy ID may produce `ACCEPTED`;
7. accepted evidence is metadata-only and does not call a document gate, integration reducer,
   push port, direct-observation port, provider SDK, UI, shell, Git, process, network,
   filesystem, environment, or clock.

Unexpected fake-port exceptions are defects and are not converted into a decision. There is no
retry, loop, polling, fallback, cache, provider inference, ambient lookup, or live capability
claim. A successful provider exit status, PR approval, PR mergeability, green CI, or policy
result cannot establish integration authority.

## TDD and strong-type preflight

Before implementation and again before the first green run, construct through ordinary public
validators every new enum member, all valid strict request/result/evidence/result shapes, both
Protocols through deterministic in-memory fakes, and every accepted/non-accepted decision shape.
Reject unknown enums, null/blank/extra/coercible values, invalid SHA/ref, duplicate policy IDs,
naive/inverted time, invalid disposition/evidence shape, and any credential-bearing metadata.
Any success through a bypass, dynamic object, `Any`, cast, historical object reuse,
`model_construct`, or `model_copy` is `HALT / TICKET_SCHEMA_INVALID`.

| Cell | Category | Required assertion |
| --- | --- | --- |
| PAI-04-T01 | positive / one-call composition | One matching `OPEN` fake PR and one matching `PROVEN` fake policy result return `ACCEPTED`, preserve exactly the normalized metadata-only evidence, call each port exactly once, and make no finalization or integration claim. |
| PAI-04-T02 | strong-type preflight / finite closure | Every public enum/member/model/Protocol constructs normally; malformed null, wrong primitive, coercion, extra, duplicate, invalid SHA/ref/time/disposition/evidence and unknown enum inputs fail ordinary validation. |
| PAI-04-T03 | profile scaling / no-ceremony path | `SINGLE_BRANCH` returns `NOT_APPLICABLE`, has no failure/evidence, and calls neither port; a HIGH_COLLABORATION request calls the PR port before any policy port. |
| PAI-04-T04 | PR visibility evidence | `NOT_FOUND` maps to `PR_REQUIRED`; unavailable/ambiguous, wrong ticket, non-OPEN or stale PR map to `PR_NOT_REVIEWABLE`; candidate-head, base-ref, and approval-head defects map one-to-one to their named failures; unexpected PR fake exceptions remain exceptions. |
| PAI-04-T05 | provider enforcement evidence | A mismatched repository/ref/gate maps to `REMOTE_IDENTITY_MISMATCH`; unavailable/ambiguous/unproven/false individual outcome maps to `PROVIDER_ENFORCEMENT_UNPROVEN`; unsupported maps to `PROVIDER_ENFORCEMENT_UNSUPPORTED`; no policy port call occurs after a failed PR. |
| PAI-04-T06 | security / metadata boundary | Credential-bearing PR or provider metadata returns `SECRET_MATERIAL_DETECTED`, carries no evidence, does not copy the secret into serialized result output, and does not call the later port. |
| PAI-04-T07 | test truthfulness / historical-surface preservation | Real-source AST gates parse the production `collaboration.py` and `__init__.py`, require exactly the sixteen collaboration exports and the complete prior export sequence plus those additions, retain unchanged Ticket 01/02/03 production assertions, and deny dynamic/bypass/effect/provider-implementation symbols and loops. |

## Required reverse mutations

Each mutation is made only in a disposable overlay of the candidate, must first turn the named
cell red with its expected failure, and must be byte-for-byte restored before return:

| Mutation | Required red cell | Property pinned |
| --- | --- | --- |
| Skip the policy-port call after a valid PR, or call either port twice | PAI-04-T01 | Accepted evidence requires exactly one complete PR/policy proof. |
| Relax one strict validator or add an undeclared enum/export | PAI-04-T02 / T07 | Public evidence is finite, typed, and closed. |
| Call a port for `SINGLE_BRANCH`, or call policy before successful PR evidence | PAI-04-T03 | Profile scaling and evidence order stay explicit. |
| Replace the PR head comparison with unconditional success | PAI-04-T04 | A PR head must equal the candidate SHA. |
| Treat either false provider outcome or `UNPROVEN` as proved | PAI-04-T05 | Both enforcement claims must be separately evidenced. |
| Remove credential metadata rejection or copy offending metadata into a result | PAI-04-T06 | Public evidence never persists secret material. |
| Add a forbidden import/call, dynamic/bypass symbol, loop, or undeclared export to real `collaboration.py` | PAI-04-T07 | The pure fake-port seam cannot grow an effect path. |

The Terra reviewer must perform at least one different-path counter-mutation from the
implementer-reported set. A zero-red mutation is a finding, not completion.

## Verification commands and deterministic result

Run one command at a time in the reviewer-established same-lifetime implementation worktree:

```powershell
py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_authority_contracts.py tests/test_project_authority_observation.py tests/test_project_authority_finalization.py tests/test_project_authority_collaboration.py
py -3.11 -m mypy --strict library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/observation.py library/local_orchestration/project_authority/integration.py library/local_orchestration/project_authority/collaboration.py tests/test_project_authority_observation.py tests/test_project_authority_finalization.py tests/test_project_authority_collaboration.py
py -3.11 -m compileall -q library/local_orchestration/project_authority
git diff --check <implementation-admission-baseline>
```

Then run the exact scope command above. Every command exits zero only after all named green cells
and restored mutations. No command reads a real remote or performs a provider, repository, host,
or other external effect.

## Completion, rollback, and return

The Luna implementation owner changes only the five declared paths and does not commit,
integrate, or push. It returns `ImplementationReturn.COMPLETED` with ticket ID, ACS revision,
exact runtime-bound `<implementation-admission-baseline>`, candidate-worktree identity, named
`implementation-scope-evidence` and its committed/working/untracked inputs, changed paths, green
test/type/compile/diff results, and every mutation's red/restored-green evidence. `BLOCKED`
returns the exact finite reason with no workaround. `CHANGE_DETECTED` emits
`REQUIREMENT_CHANGED` and stops source work.

The Terra reviewer validates that same runtime baseline and scope evidence, reruns the declared
checks, personally records a different-path counter-mutation, writes the candidate commit after
approval, and alone submits it to the document-mutation gate. Rollback is an additive local
forward correction or revert, never force-push, history rewrite, relabelled provider success, or
external effect. Same-lifetime allocation, wait, review, and guarded integration remain
bridge-free and do not require a receipt, descriptor, host gateway, or runner.
