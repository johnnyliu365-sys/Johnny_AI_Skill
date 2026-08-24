# Ticket 01 — authority contract and lifecycle

| Field | Value |
| --- | --- |
| Ticket ID | PAI-01-AUTHORITY-CONTRACT-LIFECYCLE |
| State | READY_LOW_MODEL / NOT_DISPATCHED |
| Acceptance Closure Set | PAI-01-ACS-REVISION-02 |
| Source specification | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4, Revision 04 |
| Requirement / decision / Context | PRD-20260824-038 / CHG-20260824-038 / ADR-20260824-020 / doc/context/project-authority-integration/main.md |
| Baseline | main at ecbee4319ff6f7ceab878a3ddce5471154571890 |
| Delivery profile | POC maturity unchanged; STANDARD intensity, derived from a new shared contract and moderate uncertainty; no external-effect signal |
| Control owner | Current-session Terra / xhigh supervisor-reviewer; the sole Agent-to-Agent orchestrator |
| Owner override record | Project owner directive: the implementation owner does not commit; after independent review, the reviewer writes the candidate commit and alone submits it to the integration gate. |
| Implementation owner | Unassigned until reviewer-established same-lifetime allocation. Standard profile reference: implementation-standard (current profile data: Luna / xhigh); one owner and no helper. |
| Independent reviewer | Standard profile reference: ticket-review (current profile data: Terra / xhigh); verified capability rank must be at least the implementation profile rank. |
| Worktree / branch / task / correlation | Unissued until synchronous dispatch. The reviewer establishes the exact ticket/worktree/branch/task/correlation binding from the committed ticket and Git metadata. Receipt, live descriptor, and host gateway are NOT_REQUIRED for this same-lifetime lane; they remain cross-lifetime-only controls. |
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

Implement exactly the Revision-04 public, pure API. `AuthorityContractInput` is the sole raw
boundary model: it carries project ID, topology, authority-line role, a
`project_authority_ref` string, remote provider/host/repository-key/alias strings, declaration
artifact ref/revision SHA, gate ID/revision, and effective datetime. Ordinary strict model
construction rejects null, wrong primitive type, coercion, and extra fields *before* domain
admission; those structural failures must not be relabelled as domain decisions.

| Public interface | Required result |
| --- | --- |
| AuthorityContractInput | Strict input model described above. It is constructed through its normal public validator only. |
| AuthorityContractAdmission | Strict result model with the finite `ACCEPTED`, `AUTHORITY_REF_INVALID`, and `SECRET_MATERIAL_DETECTED` decisions. An accepted result carries exactly one `ProjectAuthorityContract` and no failure; a rejected result carries no contract and its named decision. |
| admit_authority_contract | Accepts `AuthorityContractInput` and returns `AuthorityContractAdmission`. A syntactically well-formed but noncanonical branch string yields `AUTHORITY_REF_INVALID`; credential-bearing repository identity yields `SECRET_MATERIAL_DETECTED`; the function makes no port or effect call. |
| AuthorityObservationAdmission | Strict result model with the finite `DIRECT_REMOTE_REF_ACCEPTED` and `DIRECT_REMOTE_READ_UNAVAILABLE` decisions. An accepted result carries exactly one `GitObservation`; a rejected result carries none. |
| admit_authority_observation | Accepts a validated `GitObservation` and returns `AuthorityObservationAdmission`. `DIRECT_REMOTE_REF` is accepted; `REMOTE_TRACKING_CACHE` returns `DIRECT_REMOTE_READ_UNAVAILABLE`; it makes no port or effect call. |
| PrePushLifecycleRequest / PrePushLifecycleTransition | Strict request carries current and requested `AuthorityIntegrationState`; strict transition result carries a state and optional finite failure. Ticket 01 admits only `CANDIDATE → REVIEW_ACCEPTED` and `REVIEW_ACCEPTED → LOCAL_INTEGRATED`. |
| advance_pre_push_lifecycle | The real pure function in `integration.py` over `PrePushLifecycleRequest`, returning `PrePushLifecycleTransition`. `LOCAL_INTEGRATED → AUTHORITY_INTEGRATED` returns `PUSH_UNCONFIRMED` and remains `LOCAL_INTEGRATED`; it has no `NonForcePushPort` parameter, import, ambient state, or effect. |

`FullBranchRef`, `RemoteRepositoryId`, `ProjectAuthorityContract`, `GitObservation`,
`GitObservationSource`, `AuthorityIntegrationState`, and `BridgeCapability` remain the strict
supporting value/enum surface. `REMOTE_TRACKING_CACHE` is diagnostic only. No update, cast,
historical-object reuse, raw mapping after the boundary, or dynamic lookup bypass may establish
any public result. Ticket 03 alone adds the separately validated injected push/readback
finalization that can produce `AUTHORITY_INTEGRATED`.

The strict source gate parses the actual production `contracts.py` and `integration.py` paths,
not test text, fixtures, or a copied representation. Its finite public-surface allowlist is
`FullBranchRef`, `RemoteRepositoryId`, `ProjectAuthorityContract`, `GitObservation`,
`GitObservationSource`, `AuthorityIntegrationState`, `BridgeCapability`,
`AuthorityContractInput`, `AuthorityContractAdmission`, `AuthorityObservationAdmission`,
`admit_authority_contract`, `admit_authority_observation`, `PrePushLifecycleRequest`,
`PrePushLifecycleTransition`, and `advance_pre_push_lifecycle`; underscored helpers are not
public. Its AST import allowlist admits only `__future__`, `datetime`, `enum`, `re`, `typing`,
`pydantic`, and the explicit `library.local_orchestration.project_authority.contracts` import
from `integration.py`; every other import is denied. It also denies the exact names/calls `Any`,
`cast`, `getattr`, `setattr`, `__import__`, `eval`, `exec`, `model_construct`, `model_copy`, and
`NonForcePushPort`.

## TDD and strong-type preflight

This is new behavior. Record green evidence for the named cells; do not claim a baseline-red or
ceremonial first-red result.

| Cell | Category | Required assertion |
| --- | --- | --- |
| PAI-01-T01 | positive / error-code consistency | `test_admit_authority_contract_accepts_strict_input` constructs a valid `AuthorityContractInput`, calls `admit_authority_contract`, and asserts the accepted `AuthorityContractAdmission` carries exactly one contract and no failure. |
| PAI-01-T02 | missing values / path identity | `test_authority_contract_input_separates_structural_and_domain_rejection` proves null, wrong primitive, coercion, and extra fields fail strict `AuthorityContractInput` construction, while a well-formed blank/whitespace, tag, symbolic, abbreviated, or SHA-like ref reaches `admit_authority_contract` and returns `AUTHORITY_REF_INVALID`. |
| PAI-01-T03 | security / error-code consistency | `test_admit_authority_contract_rejects_credential_identity` passes structurally valid credential-bearing identity through `AuthorityContractInput` and observes `SECRET_MATERIAL_DETECTED` from `admit_authority_contract` before persistence. |
| PAI-01-T04 | finite-state boundary | `test_public_enums_and_lifecycle_request_are_closed` constructs every declared `AuthorityIntegrationState`, `BridgeCapability`, and admission decision member through ordinary validators and rejects undeclared values. |
| PAI-01-T05 | exception behavior / cache boundary | `test_admit_authority_observation_rejects_tracking_cache` calls the real `admit_authority_observation` with a validated cache observation and observes `DIRECT_REMOTE_READ_UNAVAILABLE`, while a direct observation returns `DIRECT_REMOTE_REF_ACCEPTED`, without a port call. |
| PAI-01-T06 | test truthfulness / reducer | `test_advance_pre_push_lifecycle_rejects_local_to_authority_shortcut` calls the production `integration.py` `advance_pre_push_lifecycle` with `PrePushLifecycleRequest` and observes preserved `LOCAL_INTEGRATED` plus `PUSH_UNCONFIRMED`, never `AUTHORITY_INTEGRATED`. |
| PAI-01-T07 | AST/source gate | `test_pure_boundary_ast_gate_targets_owned_production_modules` parses the real `contracts.py` and `integration.py` files and enforces the stated finite public-surface allowlist and forbidden-name/import/call denylist; it must not inspect a fixture, copied text, or only the test module. |

Before dispatch and again before implementation starts, construct every Ticket 01 success-path
DTO, enum, request, result, and reducer input through its normal public validator/round trip:
`AuthorityContractInput`, accepted `AuthorityContractAdmission`, validated `GitObservation`,
accepted `AuthorityObservationAdmission`, `PrePushLifecycleRequest`, and an admitted
`PrePushLifecycleTransition`, plus their supporting value objects and finite enums. The preflight
fails closed as HALT / TICKET_SCHEMA_INVALID if a bypass constructor, mutable update, Any, cast,
dynamic lookup, or unknown enum value succeeds.

## Required reverse mutations

Each mutation is made only in a disposable copy or overlay of the candidate, must turn the named
cell red, and must be restored byte-identically before the implementation result is returned.

| Mutation | Required red cell | Property pinned |
| --- | --- | --- |
| Relax `AuthorityContractInput` strict construction for a wrong primitive or extra field | PAI-01-T02 | Structural rejection is distinct from named domain failure. |
| Make `admit_authority_contract` accept a noncanonical blank/whitespace/tag/symbolic/abbreviated/SHA-like ref | PAI-01-T02 | The real admission API returns `AUTHORITY_REF_INVALID` for a well-formed but invalid ref. |
| Make `admit_authority_contract` accept credential-bearing repository identity | PAI-01-T03 | Credential material cannot enter durable contract data. |
| Add an undeclared lifecycle or bridge enum member | PAI-01-T04 | The public finite enums remain closed. |
| Make `admit_authority_observation` accept `REMOTE_TRACKING_CACHE` | PAI-01-T05 | Cache remains diagnostic rather than remote truth on the real public API. |
| Make `advance_pre_push_lifecycle` turn `LOCAL_INTEGRATED` directly into `AUTHORITY_INTEGRATED` | PAI-01-T06 | The real `integration.py` reducer cannot bypass push/readback. |
| Insert `getattr` or a `NonForcePushPort` import into the actual owned production module | PAI-01-T07 | The AST gate pins the real pure boundary, not a text copy or fixture. |

The independent Terra reviewer must perform at least one different-path counter-mutation during
review. A zero-red mutation is a finding, not completion.

## Verification commands and deterministic result

Run these exact Revision-04 commands one at a time in the reviewer-established same-lifetime
implementation worktree:

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
This leaf neither authorizes nor requires cross-lifetime machinery. Same-lifetime reviewer
allocation, wait, review, and guarded integration remain bridge-free and do not require a
receipt, live descriptor, or host gateway; cross-lifetime handling remains the separate
NOT_REQUIRED / AVAILABLE / UNAVAILABLE capability decision.
