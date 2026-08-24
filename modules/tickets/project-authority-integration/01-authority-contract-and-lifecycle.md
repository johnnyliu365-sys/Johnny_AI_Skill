# Ticket 01 — authority contract and lifecycle

| Field | Value |
| --- | --- |
| Ticket ID | PAI-01-AUTHORITY-CONTRACT-LIFECYCLE |
| State | READY_LOW_MODEL / NOT_DISPATCHED |
| Acceptance Closure Set | PAI-01-ACS-REVISION-01 |
| Source specification | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4, Revision 03 |
| Requirement / decision / Context | PRD-20260824-038 / CHG-20260824-038 / ADR-20260824-020 / doc/context/project-authority-integration/main.md |
| Baseline | main at a3c08309697f9fa9baa3dca442f35abdc39a6a0d |
| Delivery profile | POC maturity unchanged; STANDARD intensity, derived from a new shared contract and moderate uncertainty; no external-effect signal |
| Control owner | Current-session Terra / xhigh supervisor-reviewer; the sole Agent-to-Agent orchestrator |
| Owner override record | Project owner directive: the implementation owner does not commit; after independent review, the reviewer writes the candidate commit and alone submits it to the integration gate. |
| Implementation owner | Unassigned until receipt admission. Standard profile reference: implementation-standard (current profile data: Luna / xhigh); one owner and no helper. |
| Independent reviewer | Standard profile reference: ticket-review (current profile data: Terra / xhigh); verified capability rank must be at least the implementation profile rank. |
| Worktree / branch / task / receipt / correlation | Unissued. The admitted dispatch descriptor is the sole authority to populate them. |
| XSS classification | N/A: no Browser, WebView, HTML/DOM renderer, JavaScript execution, Native bridge, or provider effect |
| Environment | Local pure Python tests only. Claude/Codex credential, CLI, host execution, runner, and remote/provider capability are not dependencies of this ticket. |

## One observable closure

Create strict, metadata-only authority-contract values and the production pure lifecycle reducer.
The local observable result is that valid contract/state construction succeeds; non-canonical
refs, credential material, cache-as-authority, and a direct LOCAL_INTEGRATED to
AUTHORITY_INTEGRATED shortcut are rejected before any port or effect call.

## Exact writable boundary

The implementation may create or modify only these four paths:

1. library/local_orchestration/project_authority/__init__.py
2. library/local_orchestration/project_authority/contracts.py
3. library/local_orchestration/project_authority/integration.py
4. tests/test_project_authority_contracts.py

No adapter, composition root, observation port, provider-policy port, shell, Git command,
remote URL, credential, target-project path, NonForcePushPort declaration, import, invocation,
or receipt/runner/queue/bridge machinery belongs in this closure. The reducer in integration.py
is pure; Ticket 03 alone adds injected NonForcePushPort orchestration.

~~~johnny-boundary
modify = library/local_orchestration/project_authority/__init__.py
create = library/local_orchestration/project_authority/__init__.py
modify = library/local_orchestration/project_authority/contracts.py
create = library/local_orchestration/project_authority/contracts.py
modify = library/local_orchestration/project_authority/integration.py
create = library/local_orchestration/project_authority/integration.py
modify = tests/test_project_authority_contracts.py
create = tests/test_project_authority_contracts.py
forbid = library/local_orchestration/project_authority/observation.py
forbid = library/local_orchestration/project_authority/collaboration.py
forbid = library/local_orchestration/project_authority/composition.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
~~~

## Public contract and error boundary

Implement only the Revision-03 Ticket 01 subset of the approved contract surface:

| Value / state | Required result |
| --- | --- |
| FullBranchRef | Accept only a nonblank full refs/heads/name branch ref; reject null, blank, whitespace-only, tag, symbolic ref, abbreviated branch, raw SHA, coercible input, and extra fields with AUTHORITY_REF_INVALID. |
| RemoteRepositoryId | Require provider kind, host, credential-free stable repository key, and a non-identity local alias; reject credential-bearing URL or identity material with SECRET_MATERIAL_DETECTED. |
| ProjectAuthorityContract | Construct through the ordinary strict public validator with FullBranchRef, RemoteRepositoryId, topology, authority-line role, declaration/gate IDs and revisions, and effective time; no update, cast, historical-object reuse, or dynamic lookup bypass. |
| GitObservationSource | Preserve the approved finite enum. REMOTE_TRACKING_CACHE remains diagnostic and is rejected as authority proof with DIRECT_REMOTE_READ_UNAVAILABLE; only DIRECT_REMOTE_REF is eligible. |
| AuthorityIntegrationState / BridgeCapability | Construct and retain exactly the approved finite state sets. |
| Pure reducer | Exercise the real integration.py reducer. It may reach REVIEW_ACCEPTED and LOCAL_INTEGRATED through valid pure inputs, but must reject a direct LOCAL_INTEGRATED to AUTHORITY_INTEGRATED shortcut as PUSH_UNCONFIRMED because no non-force push and direct readback exist in this ticket. |

The strict schema gate uses immutable, extra-forbid, non-coercing public models/enums and these
allowlists: full refs/heads/name branch refs, approved finite enums, and DIRECT_REMOTE_REF as
the sole authority observation source. It denies Any, casts, dynamic member lookup, mutable
updates, raw mappings after the adapter boundary, credentials, URL-bearing remote identity, cache
authority, and any NonForcePushPort surface in the four-path closure.

## TDD and strong-type preflight

This is new behavior. Record green evidence for the named cells; do not claim a baseline-red or
ceremonial first-red result.

| Cell | Category | Required assertion |
| --- | --- | --- |
| PAI-01-T01 | path identity / positive | test_full_branch_ref_and_authority_contract_accept_exact_values constructs the valid public values through ordinary validators. |
| PAI-01-T02 | missing values / path identity | test_contract_rejects_noncanonical_missing_and_coercible_inputs rejects null, blank, whitespace, extra fields, coercion, tags, symbolic refs, abbreviations, and SHAs with the fixed invalid-ref shape. |
| PAI-01-T03 | security / error-code consistency | test_remote_repository_identity_rejects_credentials rejects credential-bearing identity before persistence with SECRET_MATERIAL_DETECTED. |
| PAI-01-T04 | finite-state boundary | test_finite_states_are_closed_and_complete constructs every AuthorityIntegrationState and BridgeCapability member and rejects undeclared values. |
| PAI-01-T05 | exception behavior / cache boundary | test_cache_observation_cannot_be_remote_authority rejects REMOTE_TRACKING_CACHE on the production validation path without a port call. |
| PAI-01-T06 | test truthfulness / reducer | test_pure_reducer_rejects_local_to_authority_shortcut enters the production integration.py reducer and observes PUSH_UNCONFIRMED rather than AUTHORITY_INTEGRATED. |
| PAI-01-T07 | source/schema gate | test_pure_boundary_has_no_dynamic_or_push_surface checks the real contracts.py and integration.py module surface for the declared denylist, including Any, cast, dynamic lookup, and NonForcePushPort. |

Before dispatch and again before implementation starts, construct every Ticket 01 success-path
DTO, enum, and reducer input through its normal public validator/round trip. The preflight fails
closed as HALT / TICKET_SCHEMA_INVALID if a bypass constructor, mutable update, Any, cast,
dynamic lookup, or unknown enum value succeeds.

## Required reverse mutations

Each mutation is made only in a disposable copy or overlay of the candidate, must turn the named
cell red, and must be restored byte-identically before the implementation result is returned.

| Mutation | Required red cell | Property pinned |
| --- | --- | --- |
| Admit refs/tags/v1 as FullBranchRef | PAI-01-T02 | Full branch-ref grammar is not a prefix/string convention. |
| Permit user:token@example.invalid/repository as remote identity | PAI-01-T03 | Credential material cannot enter durable contract data. |
| Treat REMOTE_TRACKING_CACHE as authority-eligible | PAI-01-T05 | Cache remains diagnostic rather than remote truth. |
| Collapse LOCAL_INTEGRATED directly to AUTHORITY_INTEGRATED | PAI-01-T06 | The real integration.py reducer cannot bypass push/readback. |
| Add a forbidden dynamic or NonForcePushPort surface | PAI-01-T07 | The Ticket 01 pure boundary remains strongly typed and effect-free. |

The independent Terra reviewer must perform at least one different-path counter-mutation during
review. A zero-red mutation is a finding, not completion.

## Verification commands and deterministic result

Run these exact Revision-03 commands one at a time in the assigned implementation worktree:

    py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_authority_contracts.py
    py -3.11 -m mypy --strict library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/integration.py tests/test_project_authority_contracts.py
    py -3.11 -m compileall -q library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/integration.py
    git diff --check <ticket-baseline> HEAD

Expected result: each command exits zero after the named green cells and restored reverse
mutations; the diff contains only the four declared paths. The focused pytest cell is the local
smoke path. No network, provider, repository, or host effect is part of any command.

## Completion, rollback, and return

The implementation owner modifies only the four paths and does not commit, integrate, or control
another Agent. It returns ImplementationReturn.COMPLETED with ticket ID, ACS revision,
baseline/candidate worktree identity, changed-path list, named test/type/compile/diff evidence,
and each mutation's red/restored-green result. The independent reviewer inspects that returned
worktree, writes the candidate commit after approval, and alone may submit it to the integration
gate. BLOCKED returns the exact finite reason with no workaround. CHANGE_DETECTED returns
REQUIREMENT_CHANGED and stops source work.

Rollback is a new local forward correction or revert of the Ticket 01 commit; never force-push,
rewrite authority history, relabel local state as remote authority, or create a remote effect.
This leaf neither authorizes nor requires cross-lifetime machinery. Same-lifetime reviewer wait,
review, and guarded integration remain bridge-free; cross-lifetime handling remains the separate
NOT_REQUIRED / AVAILABLE / UNAVAILABLE capability decision.
