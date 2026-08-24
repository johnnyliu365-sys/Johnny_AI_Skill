# Project authority integration specification

| Field | Value |
| --- | --- |
| Specification ID | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4 |
| Status | APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED |
| Author / baseline | Architecture owner / main / 5d74f27d797e05cb9845d9ebf35dcb76cff22212 |
| Context | doc/context/project-authority-integration/main.md |
| Shared Context | CONTEXT.md revision 02 sealed by CHG-20260824-038 |
| PRD / change | PRD-20260824-038 / CHG-20260824-038 |
| Architecture decision | doc/adr/ADR-20260824-020-declared-project-authority-line-and-provider-enforcement.md |
| Implementation language | Python 3.11 with mypy --strict; Markdown is an artifact format, not a runtime |
| Maturity / intensity | Existing POC maturity is unchanged. Pure local source/fake-port tickets derive intensity from committed WorkloadAssessment; live remote, provider, policy, push and release effects are HIGH_ASSURANCE and require separate effect authority. |
| XSS classification | N/A: this boundary has no Browser, WebView, HTML/DOM renderer, JavaScript execution surface or Native bridge. |

## Problem and user result

A guarded merge can move one local checkout without proving that the intended remote authority line
now contains the reviewed candidate. The control plane must make that authority line explicit,
separate local from remote completion, and fail closed whenever direct remote or provider-
enforcement evidence is missing.

The observable result is a finite integration record. A reviewer can distinguish
LOCAL_INTEGRATED from AUTHORITY_INTEGRATED, diagnose PUSH_UNCONFIRMED, and prove that a selected
high-collaboration profile has the stated PR/provider controls or does not claim them.
Same-lifetime work remains usable when a cross-lifetime bridge is unavailable.

## Scope and exclusions

In scope:

- strict, metadata-only authority-line, direct-observation, PR and provider-enforcement contracts;
- pure validators/reducers, fake ports, deterministic race/staleness/counter-mutation tests;
- controlled local integration followed by injected non-force push and direct readback ports;
- profile-scaled review evidence and alignment of shipped governance wording that currently makes
  asynchronous mechanisms appear universal.

Out of scope until an exact later ticket has separate owner effect authority:

- target-project remote mutation, direct push, force push, branch deletion, history rewrite,
  release, tag move, deployment, provider invocation, GitHub policy configuration, credential
  access, GitHub App installation, UI merge, CI configuration, queue, receipt issuance, runner,
  polling, heartbeat or session restoration;
- inference of an authority line from main, dev, staging, current checkout, upstream
  configuration, origin/HEAD, a tag or provider UI defaults;
- a second integration gate based on PR state or CI status.

## Strong domain contracts

All public inputs/outputs are strict Pydantic models, finite enums, named value objects or
Protocol ports. Dynamic Git/provider/shell input is normalized at an adapter boundary. Any,
unvalidated mappings, string conventions, cast, bypass-built object or historical mutable model
cannot establish authority.

| Contract | Required meaning |
| --- | --- |
| FullBranchRef | Exact refs/heads/name; rejects tags, symbolic refs, abbreviated names and raw SHAs. |
| RemoteRepositoryId | Provider kind, host, credential-free stable repository key and local remote alias. The alias is not identity. |
| ProjectAuthorityContract | Schema and contract/project IDs; topology; authority-line role; FullBranchRef; remote identity; declaration ref/revision; gate ID/revision; effective time. |
| GitObservation | Observation ID; source; repository; full ref; SHA; observer; method; exit status; observed time; normalized evidence digest. |
| PullRequestEvidence | Provider repository, PR/ticket IDs, state, head ref/SHA, base ref, approval head SHA, observed time and normalized digest. |
| ProviderEnforcementEvidence | Repository/ref/gate identity; capability; UI-bypass and stale-approval outcomes; policy IDs; readback method/time; normalized digest. |
| IntegrationAttempt | Attempt/ticket/revision/profile IDs; authority contract; candidate SHA; direct base observation; review/counter-mutation evidence; optional PR/policy evidence; gate result; local SHA; push/readback result; state and finite failure. |

GitObservationSource contains WORKTREE_HEAD, LOCAL_AUTHORITY_REF, REMOTE_TRACKING_CACHE,
DIRECT_REMOTE_REF, PROVIDER_PR_READBACK and PROVIDER_POLICY_READBACK. Only DIRECT_REMOTE_REF is
remote authority proof; REMOTE_TRACKING_CACHE is diagnostic only even after fetch.

AuthorityIntegrationState is exactly CANDIDATE, REVIEW_ACCEPTED, GATE_REJECTED,
LOCAL_INTEGRATED, PUSH_UNCONFIRMED and AUTHORITY_INTEGRATED. BridgeCapability remains exactly
NOT_REQUIRED, AVAILABLE and UNAVAILABLE. ProviderEnforcementCapability is exactly
NOT_APPLICABLE, PROVEN, UNPROVEN and UNSUPPORTED.

The finite error surface includes:

- AUTHORITY_CONTRACT_MISSING, AUTHORITY_CONTRACT_INVALID and AUTHORITY_REF_INVALID;
- REMOTE_IDENTITY_MISMATCH, DIRECT_REMOTE_READ_UNAVAILABLE, REMOTE_REF_NOT_FOUND,
  REMOTE_REF_AMBIGUOUS and AUTHORITY_REF_MOVED;
- CANDIDATE_NOT_A_COMMIT, CANDIDATE_SCOPE_MISMATCH, REVIEW_EVIDENCE_MISSING and
  COUNTER_MUTATION_EVIDENCE_MISSING;
- PR_REQUIRED, PR_NOT_REVIEWABLE, PR_HEAD_SHA_MISMATCH, PR_BASE_REF_MISMATCH and
  PR_APPROVAL_STALE;
- PROVIDER_ENFORCEMENT_UNPROVEN, PROVIDER_ENFORCEMENT_UNSUPPORTED, GATE_REJECTED,
  PUSH_REJECTED, PUSH_UNCONFIRMED, REMOTE_READBACK_SHA_MISMATCH and SECRET_MATERIAL_DETECTED.

## Authority and integration flow

1. Validate the authority contract, full ref, credential-free repository identity and reviewed
   candidate closure.
2. Directly read the declared remote/ref and bind its SHA as expected remote base.
3. When HIGH_COLLABORATION is selected, validate current PR and provider-enforcement evidence.
4. Gate-local integration may record only LOCAL_INTEGRATED and its exact local SHA.
5. Invoke an injected non-force push to exactly the declared remote/ref.
6. Directly read the same remote/ref again. Exact equality to local SHA yields
   AUTHORITY_INTEGRATED; missing, failed, ambiguous or mismatched proof yields
   PUSH_UNCONFIRMED or a more specific finite failure.

Precedence is fixed: contract/ref structure; repository identity; direct remote observation;
candidate/review/counter-mutation closure; high-collaboration PR/provider evidence; gate;
non-force push; post-push direct readback. A stale pre-gate observation must be re-read inside
the attempt boundary. A remote move, rejected push or SHA mismatch is never repaired with force,
ref inference or relabelled local success.

SINGLE_BRANCH may declare refs/heads/main but grants that name no intrinsic authority.
HIGH_COLLABORATION requires one current ticket PR where head SHA equals candidate SHA, base ref
equals project_authority_ref and approval binds that head. It may be called enforced only when
provider readback proves both UI-bypass prevention and stale-approval dismissal. CI and PR state
are review evidence, never integration authority.

## Composition and ownership

- library/local_orchestration/project_authority/contracts.py owns pure value objects, states,
  failures and validators.
- library/local_orchestration/project_authority/observation.py owns DirectRemoteObservationPort
  and its validated adapter boundary.
- library/local_orchestration/project_authority/integration.py owns the pure transition reducer
  and injected NonForcePushPort orchestration.
- library/local_orchestration/project_authority/collaboration.py owns PullRequestReadPort and
  ProviderPolicyReadPort validation/profile admission.
- library/local_orchestration/project_authority/composition.py owns explicit port injection. It
  has no ambient environment, provider singleton or target path.

Pure tickets never instantiate production composition. Tests own deterministic fakes and
disposable repositories only. A future live adapter owns authenticated remote/provider I/O behind
these ports and cannot return credentials, raw responses, unrestricted command output or
uncommitted source. No public contract permits a caller-selected path, remote URL, policy
payload, credential, shell command or target-project root.

## Security, data and lifecycle boundary

Persisted evidence contains only normalized identifiers, full refs, SHAs, finite state/failure,
bounded times, provider-policy IDs and evidence digests. It rejects credential-bearing URLs,
authorization headers, cookies, tokens, prompts, chat text, source trees, raw provider payloads,
raw command output and uncommitted worktree data. Runtime credentials remain injected at the
provider boundary and never enter tickets, reports, errors or durable models.

Live remote read/push, GitHub policy read/configuration, real provider commands, release and
deployment are privileged/external effects. Each requires exact owner, action, target,
environment, receipt, baseline and correlation before effect and exact readback after it. A fake
port result never upgrades a real capability or enforcement claim.

The cross-lifetime bridge is a separate lifecycle mechanism. UNAVAILABLE means owner-mediated
artifact relay only. Same-lifetime reviewer -> wait -> review -> gate does not consult bridge,
runner, queue, receipt, descriptor, gateway or workspace/profile readback.

## Acceptance criteria

1. Full refs, remote identity, observations, PR/provider evidence and attempts reject null, blank,
   extra, coercible, tag, symbolic, abbreviated, SHA and credential-bearing inputs before any port
   or effect call.
2. REMOTE_TRACKING_CACHE cannot bind remote base or completion; a direct remote observation of
   the declared identity/ref is mandatory.
3. Gate acceptance records LOCAL_INTEGRATED only against exact direct base and reviewed candidate.
4. AUTHORITY_INTEGRATED requires non-force push plus post-push direct remote SHA equal to local
   integrated SHA. Missing or mismatch is durable PUSH_UNCONFIRMED.
5. A post-observation remote move rejects with no force, overwrite or false completion.
6. High collaboration rejects absent PR, head/candidate mismatch, wrong base, stale approval and
   unproved/unsupported enforcement. A correct PR or green CI without gate acceptance is unauthorized.
7. A declared single branch is admissible without PR/provider ceremony but never without direct
   base/readback and guarded integration.
8. UI-bypass prevention and stale-approval dismissal are separate provider-readback outcomes.
9. Durable models are metadata-only; every credential-bearing input is rejected before persistence.
10. BridgeCapability.UNAVAILABLE leaves same-lifetime implementation/review/gate available while
    cross-lifetime automatic handoff stays unavailable.
11. Ticket/review records bind authority-contract/context/spec revisions, candidate/base/integrated
    SHAs and independent counter-mutation. A zero-red mutation is a finding.
12. Changing skills to align governance prose triggers Level 1 regeneration, fresh immutable
    plugin release and real CLI verification; library-only work cannot claim a release.

## Verification and ticket order

The reviewer splits only along independently observable closures:

1. authority contract and pure lifecycle reducer;
2. direct remote observation and cache-staleness boundary;
3. gate/push/readback composition using fake non-force push;
4. high-collaboration PR/provider-policy evidence validation using fake ports;
5. profile-scaled counter-mutation and synchronous/bridge three-state alignment;
6. owner-authorized live provider/repository capability qualification;
7. governance-reference alignment, Level 1 regeneration and new plugin release;
8. independent cluster review and release-gate closure.

Every implementation ticket uses Python 3.11, mypy --strict, strong-type preflight, focused
verification and full-regression review. Pure tickets use the normal implementation profile unless
a committed hard-ticket assessment proves indivisible elevation; reviewer capability is at least
the implementer capability. Live provider/repository and release effects are HIGH_ASSURANCE and
can never be inferred from a pure-source success.

## Risks, compatibility and recovery

- Direct remote observations may race. Bind a fresh pre-gate base, use non-force push, then
  re-observe; do not hide a race behind tracking cache or force push.
- A local merge remains useful forensic evidence but not remote authority until direct readback.
  Preserve it as PUSH_UNCONFIRMED; use a new gated forward fix or revert, never rewrite history.
- Provider capability may be unsupported. Return its finite state; never label unsupported
  configuration as high-collaboration enforcement.
- Historical tickets are not retroactively upgraded. New admission binds this spec only after
  exact ticket approval.
- There is no target runtime dependency. Plugin rollback is a new immutable version/tag, never
  mutation of publication history.

## Approval record

- Architecture/Grill decisions: project owner accepted the declared-ref, completion,
  high-collaboration PR/enforcement and bridge-boundary decisions on 2026-08-24 (Asia/Taipei).
- Exact specification revision: owner-approved authority to begin this governed requirement after
  those decisions authorizes reviewer decomposition and ticket drafting.
- No target remote, GitHub policy, provider, push, release, deployment or credential effect is
  authorized. Each remains a later ticket-specific owner boundary.
