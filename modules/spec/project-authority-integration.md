# Project authority integration specification

| Field | Value |
| --- | --- |
| Specification ID | SPEC-AI-WORKFLOW-PROJECT-AUTHORITY-INTEGRATION-20260824-01M2A4C6E8G0I2K4M6O8Q0S2U4 |
| Status | APPROVED / REVISION_06 / REVIEWER_DECOMPOSITION_AUTHORIZED |
| Author / baseline | Project-owner-approved Sol decision / Terra supervisor reviewer / specification provenance main at 6df6885ea093f1e37899f5252f8e4a1cc4feadb9; not an implementation-admission baseline |
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

## Revision 04 — public validation and pre-push lifecycle API

Ticket 01 uses these exact public, pure interfaces. They remove the distinction that revision 03
left implicit: malformed structure is rejected by strict model construction, while semantically
well-formed string input receives a finite domain result.

| Interface | Exact contract |
| --- | --- |
| AuthorityContractInput | Strict input model with project_id, ProjectTopology, AuthorityLineRole, project_authority_ref string, RemoteProviderKind, remote host/repository key/alias strings, declaration artifact ref/revision SHA, gate ID/revision and effective datetime. Null, wrong primitive type, coercion and extra fields fail ordinary strict model validation before domain admission. |
| AuthorityContractAdmission | Strict result model: decision is ACCEPTED, AUTHORITY_REF_INVALID, or SECRET_MATERIAL_DETECTED; accepted result carries exactly one ProjectAuthorityContract and no failure; rejected result carries no contract and its finite decision. |
| admit_authority_contract | Accepts AuthorityContractInput and returns AuthorityContractAdmission. A syntactically valid but noncanonical branch string returns AUTHORITY_REF_INVALID; credential-bearing repository identity returns SECRET_MATERIAL_DETECTED. It makes no port or effect call. |
| AuthorityObservationAdmission | Strict result model: decision is DIRECT_REMOTE_REF_ACCEPTED or DIRECT_REMOTE_READ_UNAVAILABLE; accepted result carries exactly one GitObservation and rejected result carries none. |
| admit_authority_observation | Accepts a validated GitObservation and returns AuthorityObservationAdmission. DIRECT_REMOTE_REF is accepted; REMOTE_TRACKING_CACHE returns DIRECT_REMOTE_READ_UNAVAILABLE. It makes no port or effect call. |
| PrePushLifecycleRequest / PrePushLifecycleTransition | Strict request carries current and requested AuthorityIntegrationState. The transition result carries state and optional finite failure. Only CANDIDATE to REVIEW_ACCEPTED and REVIEW_ACCEPTED to LOCAL_INTEGRATED are admitted in Ticket 01. A request for LOCAL_INTEGRATED to AUTHORITY_INTEGRATED returns PUSH_UNCONFIRMED and remains LOCAL_INTEGRATED. |
| advance_pre_push_lifecycle | Pure function over PrePushLifecycleRequest returning PrePushLifecycleTransition. It has no NonForcePushPort parameter, import, ambient state or effect. Ticket 03 alone adds the separately validated push/readback finalization path. |

Pydantic structural validation failures are not reported as a false domain decision. Ticket 01
tests them as strict construction rejection. The three result models above are the only source of
the named finite decisions that Ticket 01 asserts.

## Revision 05 — finite public enum closure

The following named enums are part of the exact Ticket 01 public surface; strings may enter only
at the strict boundary model and are normalized to these values before a result is constructed.

| Enum | Exact members |
| --- | --- |
| ProjectTopology | SINGLE_BRANCH, HIGH_COLLABORATION |
| AuthorityLineRole | SINGLE, DEVELOPMENT, STAGING, RELEASE |
| RemoteProviderKind | GIT_GENERIC, GITHUB, OTHER |
| AuthorityContractAdmissionDecision | ACCEPTED, AUTHORITY_REF_INVALID, SECRET_MATERIAL_DETECTED |
| AuthorityObservationDecision | DIRECT_REMOTE_REF_ACCEPTED, DIRECT_REMOTE_READ_UNAVAILABLE |

AuthorityContractInput uses ProjectTopology, AuthorityLineRole and RemoteProviderKind rather than
unconstrained strings for those fields. AuthorityContractAdmission uses
AuthorityContractAdmissionDecision, and AuthorityObservationAdmission uses
AuthorityObservationDecision. Every member must construct through its ordinary validator and every
unknown value must be rejected. The source AST allowlist and strong-type preflight must include all
five named enums; a gate that omits them has not pinned the public surface.

AuthorityIntegrationState is exactly CANDIDATE, REVIEW_ACCEPTED, GATE_REJECTED,
LOCAL_INTEGRATED, PUSH_UNCONFIRMED and AUTHORITY_INTEGRATED. BridgeCapability remains exactly
NOT_REQUIRED, AVAILABLE and UNAVAILABLE. ProviderEnforcementCapability is exactly
NOT_APPLICABLE, PROVEN, UNPROVEN and UNSUPPORTED.

The finite error surface includes:

- AUTHORITY_CONTRACT_MISSING, AUTHORITY_CONTRACT_INVALID and AUTHORITY_REF_INVALID;
- REMOTE_IDENTITY_MISMATCH, DIRECT_REMOTE_READ_UNAVAILABLE, REMOTE_REF_NOT_FOUND,
  REMOTE_REF_AMBIGUOUS, DIRECT_REMOTE_OBSERVATION_STALE and AUTHORITY_REF_MOVED;
- CANDIDATE_NOT_A_COMMIT, CANDIDATE_SCOPE_MISMATCH, REVIEW_EVIDENCE_MISSING and
  COUNTER_MUTATION_EVIDENCE_MISSING;
- PR_REQUIRED, PR_NOT_REVIEWABLE, PR_HEAD_SHA_MISMATCH, PR_BASE_REF_MISMATCH and
  PR_APPROVAL_STALE;
- PROVIDER_ENFORCEMENT_UNPROVEN, PROVIDER_ENFORCEMENT_UNSUPPORTED, GATE_REJECTED,
  PUSH_REJECTED, PUSH_UNCONFIRMED, REMOTE_READBACK_SHA_MISMATCH and SECRET_MATERIAL_DETECTED.

## Revision 06 — direct remote observation contract and Ticket 02 seam

The owner-approved direct-observation closure is Ticket 02 in the declared ticket order. It is a
pure, fake-port closure: it validates and classifies one supplied direct-read result, without a
live remote, provider, shell, Git executable, process, network, environment, filesystem or clock
lookup. It neither changes the frozen Ticket 01 API nor consumes an observation to push or finalise
integration; Ticket 03 alone owns that consumption, injected non-force push, post-push readback,
and every transition to `AUTHORITY_INTEGRATED`.

`library/local_orchestration/project_authority/observation.py` owns exactly these new public types
and function. Each named model below is a strict Pydantic model: frozen, `extra="forbid"`, strict,
and revalidating instances. Ordinary construction rejects null where the annotation is non-null,
wrong primitive types, coercion and extra fields before a domain decision is constructed.

| Interface | Exact contract |
| --- | --- |
| DirectRemoteReadDisposition | Finite enum exactly `OBSERVED`, `UNAVAILABLE`, `NOT_FOUND`, `AMBIGUOUS`. |
| DirectRemoteObservationDecision | Finite enum exactly `ACCEPTED`, `DIRECT_REMOTE_READ_UNAVAILABLE`, `REMOTE_REF_NOT_FOUND`, `REMOTE_REF_AMBIGUOUS`, `REMOTE_IDENTITY_MISMATCH`, `DIRECT_REMOTE_OBSERVATION_STALE`, `AUTHORITY_REF_MOVED`, `SECRET_MATERIAL_DETECTED`. |
| DirectRemoteObservationRequest | Strict request with non-null `authority_contract: ProjectAuthorityContract`, `observation_id: str`, timezone-aware `valid_from: datetime`, timezone-aware `decision_at: datetime`, and nullable `expected_sha: str | None = None`. `valid_from <= decision_at` is mandatory. A null `expected_sha` denotes an initial observation; a non-null value is revalidated as one full lower-case SHA. |
| DirectRemoteReadResult | Strict port result with non-null `disposition: DirectRemoteReadDisposition`, `source: GitObservationSource`, `repository: RemoteRepositoryId`, `full_ref: FullBranchRef`, nullable `sha: str | None`, `observer: str`, `method: str`, `exit_status: int`, timezone-aware `observed_at: datetime`, and `normalized_evidence_digest: str`. `OBSERVED` requires exactly one SHA; each other disposition requires `sha is None`. |
| DirectRemoteObservationResult | Strict result with `decision: DirectRemoteObservationDecision`, nullable `observation: GitObservation | None = None`, and nullable `failure: DirectRemoteObservationDecision | None = None`. `ACCEPTED` carries exactly one direct `GitObservation` and no failure. Every failure carries no observation and its finite failure decision. |
| DirectRemoteObservationPort | A `Protocol` with exactly `observe(self, request: DirectRemoteObservationRequest, /) -> DirectRemoteReadResult`. Its input is positional-only at the public boundary. |
| observe_declared_remote | Pure function with exactly `observe_declared_remote(request: DirectRemoteObservationRequest, port: DirectRemoteObservationPort, /) -> DirectRemoteObservationResult`. It calls `port.observe(request)` exactly once. |

`observe_declared_remote` has this exact, fail-closed precedence:

1. strict request/read-result construction;
2. credential-bearing `observer`, `method`, or `normalized_evidence_digest` metadata, yielding
   `SECRET_MATERIAL_DETECTED` without copying that material to a public observation;
3. read-result repository or full ref differing from the request's authority contract, yielding
   `REMOTE_IDENTITY_MISMATCH`;
4. `UNAVAILABLE`, `NOT_FOUND`, and `AMBIGUOUS`, mapping one-to-one to
   `DIRECT_REMOTE_READ_UNAVAILABLE`, `REMOTE_REF_NOT_FOUND`, and `REMOTE_REF_AMBIGUOUS`;
5. a source other than `DIRECT_REMOTE_REF`, including `REMOTE_TRACKING_CACHE`, yielding
   `DIRECT_REMOTE_READ_UNAVAILABLE`;
6. freshness: `valid_from <= observed_at <= decision_at`, else
   `DIRECT_REMOTE_OBSERVATION_STALE`;
7. a non-null `expected_sha` unequal to the observed SHA, yielding `AUTHORITY_REF_MOVED`;
8. only then construct a `GitObservation` with `DIRECT_REMOTE_REF` and return `ACCEPTED`.

Normal unavailable/not-found/ambiguous outcomes are typed port result values, not exceptions.
Unexpected port exceptions are defects and are not converted into an authority decision. There is
no retry, loop, polling, fetch, clock fallback, cache fallback, provider fallback or implicit
effect. In particular, a fake result or a successful process exit cannot claim a live capability.

The complete recommended Ticket 02 source/test boundary is exactly:

- modify `library/local_orchestration/project_authority/__init__.py` to export only the new public
  observation contract;
- create `library/local_orchestration/project_authority/observation.py`;
- create `tests/test_project_authority_observation.py`.

Ticket 02 must forbid changes to `library/local_orchestration/project_authority/contracts.py` and
`library/local_orchestration/project_authority/integration.py`. It cannot introduce
`NonForcePushPort`, production composition, a live adapter, lifecycle finalisation, or an
`AUTHORITY_INTEGRATED` result.

Its strong-type preflight constructs every `DirectRemoteReadDisposition` and
`DirectRemoteObservationDecision` member, each public request/read/result shape, and the Protocol
through a deterministic in-memory fake. It rejects unknown enum values, null non-nullable fields,
extra/coercible fields, naive or inverted decision times, non-full expected SHAs, an `OBSERVED`
result without a SHA, and a non-observed result with one. This is new behaviour: record named green
cells, not a ceremonial baseline-red claim.

| Cell | Category | Required assertion |
| --- | --- | --- |
| PAI-02-T01 | positive / error-code consistency | A valid direct fake response produces `ACCEPTED`, preserves the declared repository/ref/SHA/observer/method/time/digest in one `GitObservation`, has no failure, and calls `observe` exactly once. |
| PAI-02-T02 | strong-type preflight / missing values | Every new enum member and ordinary public model/Protocol construction succeeds; unknown enum, null, wrong primitive, coercion, extra field, naive/inverted time, invalid expected SHA, and invalid disposition/SHA shape fail ordinary validation. |
| PAI-02-T03 | exception behavior / error-code consistency | Each of `UNAVAILABLE`, `NOT_FOUND`, and `AMBIGUOUS` maps one-to-one to its declared finite failure and no observation; an unexpected fake-port exception is not converted into a success or finite authority decision. |
| PAI-02-T04 | cache boundary | `REMOTE_TRACKING_CACHE` cannot substitute for `DIRECT_REMOTE_REF` and returns `DIRECT_REMOTE_READ_UNAVAILABLE` with no observation. |
| PAI-02-T05 | path identity | A fake response with repository or full ref different from `authority_contract` returns `REMOTE_IDENTITY_MISMATCH` before source/freshness/SHA success. |
| PAI-02-T06 | staleness / race | `observed_at` before `valid_from` or after `decision_at` returns `DIRECT_REMOTE_OBSERVATION_STALE`; a non-null unequal expected SHA returns `AUTHORITY_REF_MOVED`. |
| PAI-02-T07 | security / metadata boundary | Credential-bearing `observer`, `method`, or digest returns `SECRET_MATERIAL_DETECTED`, carries no observation, and does not copy the credential-bearing string into a public result. |
| PAI-02-T08 | test truthfulness / source boundary | An actual-source AST gate parses only the declared `__init__.py` and `observation.py`, confirms the observation module declares exactly the seven approved public names and that `__init__.py` retains the frozen Ticket 01 exports while importing/exporting exactly those seven additions. It denies `Any`, `cast`, `getattr`, `setattr`, `__import__`, `eval`, `exec`, `model_construct`, `model_copy`, `NonForcePushPort`, `open`, `os`, `pathlib`, `subprocess`, `socket`, `urllib`, `http`, `requests`, `git`, `shutil`, `time`, `datetime.now`, and `datetime.utcnow`, including aliases. |

The source gate permits only the finite production import roots `__future__`, `datetime`, `enum`,
`re`, `typing`, `pydantic`, and
`library.local_orchestration.project_authority.contracts` in `observation.py`; it may add only the
relative observation re-export to the existing `__init__.py` imports. It never reads a copied
fixture or test representation.

The TDD cells must use only in-memory deterministic fakes and must not inspect `.git`, local refs,
`.worktrees`, `.claude/worktrees`, environment-dependent paths, or the surrounding checkout. This
is the C13 independence rule: a green result depends on explicit request/read-result values and
the declared production sources, not on worktree residue or local repository facts.

Every following reverse mutation is performed in a disposable overlay, must make its named cell
red, and must be byte-for-byte restored before return:

- mutate production to call the fake port twice (`PAI-02-T01` red);
- relax a strict field/enum/disposition validator (`PAI-02-T02` red);
- collapse `UNAVAILABLE`, `NOT_FOUND`, or `AMBIGUOUS` into success, or swallow an unexpected port
  exception (`PAI-02-T03` red);
- admit `REMOTE_TRACKING_CACHE` as direct authority (`PAI-02-T04` red);
- remove repository/ref equality (`PAI-02-T05` red);
- remove freshness comparison or expected-SHA equality (`PAI-02-T06` red);
- remove credential-metadata rejection (`PAI-02-T07` red);
- add a forbidden effect import/call or dynamic/bypass symbol to the real `observation.py`, or
  add an undeclared public export (`PAI-02-T08` red).

Ticket 02's deterministic local commands are:

    py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_authority_observation.py
    py -3.11 -m mypy --strict library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/observation.py tests/test_project_authority_observation.py
    py -3.11 -m compileall -q library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/observation.py
    git diff --check <implementation-admission-baseline> HEAD
    $trackedScopePaths = @(git diff --name-only <implementation-admission-baseline> HEAD)
    $untrackedScopePaths = @(git ls-files --others --exclude-standard)
    $implementationScopeEvidence = @(
        $trackedScopePaths
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

The reviewer establishes the exact clean-current-integration-main SHA at same-lifetime dispatch as
`<implementation-admission-baseline>`; neither this SPEC provenance SHA nor a ticket SHA may be
substituted. The sorted duplicate-free `implementation-scope-evidence` union must equal exactly
the three declared paths, including an uncommitted creation. Same-lifetime reviewer allocation,
wait, review, and guarded integration remain bridge-free: no receipt, descriptor, gateway, or
runner is required or authorized by this pure closure.

## Revision 07 — owner-selected single finalization boundary and Ticket 03 seam

The owner selected one provider-neutral finalization boundary rather than separate public push
and readback APIs. `integration.py` owns that one boundary. It receives a validated record that
gate-local integration has already reached `LOCAL_INTEGRATED`, invokes one injected fake
non-force push port, then invokes the existing injected direct-observation port exactly once
after an accepted push. It is the only Ticket 03 path that can return
`AUTHORITY_INTEGRATED`; it neither invokes the document-mutation gate nor performs real I/O.

`library/local_orchestration/project_authority/integration.py` owns exactly these new public
names. Every named model is strict, frozen, `extra="forbid"`, non-coercing, and revalidating;
every SHA is full lower-case and every timestamp timezone-aware:

| Interface | Exact contract |
| --- | --- |
| NonForcePushDisposition | Finite enum exactly `ACCEPTED`, `REJECTED`, `UNCONFIRMED`. `ACCEPTED` is a port claim only; it never itself proves remote completion. |
| NonForcePushRequest | `authority_contract: ProjectAuthorityContract`; nonblank `attempt_id`; `expected_remote_base: GitObservation`; full lower-case `local_integrated_sha`; `requested_at: datetime`. The base must be `DIRECT_REMOTE_REF` and match the contract repository/ref. |
| NonForcePushResult | `disposition`; `repository: RemoteRepositoryId`; `full_ref: FullBranchRef`; nonblank `attempt_id`; full lower-case `expected_base_sha` and `requested_sha`; nonblank `executor`, `method`, and evidence digest; bounded integer exit status; `completed_at: datetime`. It rejects credential-bearing executor, method, or digest. Identity, attempt, expected base and requested SHA must echo the request before disposition is trusted. |
| NonForcePushPort | `push(self, request: NonForcePushRequest, /) -> NonForcePushResult`. It is injected; Ticket 03 supplies deterministic fakes only. |
| AuthorityFinalizationFailure | Finite enum exactly `LOCAL_INTEGRATION_EVIDENCE_INVALID`, `PRE_PUSH_OBSERVATION_INVALID`, `REMOTE_IDENTITY_MISMATCH`, `AUTHORITY_REF_MOVED`, `PUSH_REJECTED`, `PUSH_UNCONFIRMED`, `DIRECT_REMOTE_READ_UNAVAILABLE`, `REMOTE_REF_NOT_FOUND`, `REMOTE_REF_AMBIGUOUS`, `DIRECT_REMOTE_OBSERVATION_STALE`, `REMOTE_READBACK_SHA_MISMATCH`, `SECRET_MATERIAL_DETECTED`. |
| AuthorityFinalizationRequest | `authority_contract: ProjectAuthorityContract`; `local_lifecycle: PrePushLifecycleTransition`; full lower-case `local_integrated_sha`; `pre_push_observation: GitObservation`; nonblank `attempt_id` and `post_push_observation_id`; `requested_at: datetime`; `decision_at: datetime`. Construction requires `requested_at <= decision_at`; finalization requires `LOCAL_INTEGRATED` with no lifecycle failure and a direct pre-push observation matching the contract. |
| AuthorityFinalizationResult | `state: AuthorityIntegrationState`; nullable `failure: AuthorityFinalizationFailure | None`; nullable `push: NonForcePushResult | None`; nullable `readback: GitObservation | None`. `AUTHORITY_INTEGRATED` carries accepted push and one direct readback equal to `local_integrated_sha`, with no failure. Every failure is exactly `PUSH_UNCONFIRMED`, carries one finite failure, and never carries nonmatching or non-direct readback as authority proof. |
| finalize_authority_integration | `finalize_authority_integration(request: AuthorityFinalizationRequest, push_port: NonForcePushPort, observation_port: DirectRemoteObservationPort, /) -> AuthorityFinalizationResult`. It has no retry, loop, fallback, ambient lookup, shell, Git executable, network, filesystem, clock, or provider call. |

Fixed precedence is: strict construction; local lifecycle and direct pre-push identity; one push
result credential/identity/attempt/base/requested-SHA validation; rejected or unconfirmed push;
one post-push direct observation; exact SHA equality. A base mismatch is
`AUTHORITY_REF_MOVED`; a post-push direct SHA different from the local integrated SHA is
`REMOTE_READBACK_SHA_MISMATCH`; unproved direct readback remains `PUSH_UNCONFIRMED`. The
post-push observation window starts at `completed_at`, has no cache fallback, and never trusts a
push exit status as authority.

Ticket 03 modifies only package `__init__.py` and `integration.py`, and creates
`tests/test_project_authority_finalization.py`. It does not change the frozen Ticket 01/02
contracts, document gate, composition root, Provider adapter, remote, credential path, runner,
receipt, descriptor, queue, or bridge. Its actual-source reverse mutation replaces the exact
post-readback SHA comparison with unconditional authority success; the mismatch test must turn
red and be restored byte-identically.

## Revision 08 — Ticket 03 frozen-gate allowlist correction

Revision 07's owner-selected public boundary adds eight names to `integration.py`, while the
historical Ticket 01 actual-source gate correctly pinned that module to its then-complete three
exports. The new names cannot satisfy both statements unless Ticket 03 owns the minimal test
allowlist extension. Ticket 03 may therefore modify only
`tests/test_project_authority_contracts.py` in addition to its Revision-07 three paths. That
change retains every Ticket 01 `contracts.py` assertion and requires the `integration.py`
allowlist to equal exactly the original three names plus the eight Revision-07 names; it may not
weaken the test into a subset or open-ended check. It replaces exactly two historical
Ticket-01-only restrictions in `integration.py`: `NonForcePushPort` is no longer a forbidden
undeclared name, and the existing observation import root is allowed only for
`DirectRemoteObservationPort`, `DirectRemoteObservationRequest`,
`DirectRemoteObservationResult`, `DirectRemoteObservationDecision`, and
`observe_declared_remote`. The focused Ticket 03 AST gate pins both exceptions to the full exact
export/import surface. This is a test-scope correction only: the Revision-07 public
contract, authority topology, effect boundary, frozen Ticket 01 contracts and frozen Ticket 02
observation contract are unchanged.

## Revision 09 — complete historical package-surface gate correction

A complete search of the committed PAI-01/02 source tests finds exactly two tests that parse the
package public surface: the Ticket-01 contracts gate and the Ticket-02 observation gate. The
latter correctly pins `__init__.py` to the then-complete base plus seven observation exports, and
also contains the historical Ticket-01-only `NonForcePushPort` deny. Revision 09 gives Ticket 03
the minimal fifth writable path, `tests/test_project_authority_observation.py`, so both gates
require the same exact package export sequence: the frozen Ticket-01 base exports, the unchanged
seven Ticket-02 observation exports, then the eight Revision-07 finalization exports. The
observation module's own exact seven-name export/declaration assertion remains unchanged. The
historical `NonForcePushPort` deny is replaced only by the exact Revision-07 allowlist; every
other deny/import/source assertion remains. No additional test in the committed suite references
this package surface. This fixes ticket closure only and changes no public meaning, requirement,
architecture, authority, effect, frozen Ticket-01 contract, or frozen Ticket-02 observation
contract.

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

## Revision 03 — exact first-ticket seam

Ticket 01 creates one complete, independently observable typed-contract closure and no adapter,
remote, provider, process, Git or target-project effect. Its complete writable boundary is exactly:

- library/local_orchestration/project_authority/__init__.py;
- library/local_orchestration/project_authority/contracts.py;
- library/local_orchestration/project_authority/integration.py;
- tests/test_project_authority_contracts.py.

The new test file is the one focused seam. It must contain named cells for: valid full-ref and
authority-contract construction; tag/symbolic/abbreviated/SHA and null/blank/extra/coercion
rejection; credential-bearing repository identity rejection; exact finite integration and bridge
state construction; cache observation being rejected as remote authority; and the forbidden
LOCAL_INTEGRATED to AUTHORITY_INTEGRATED shortcut. New behavior records green tests, not a
ceremonial first-red claim. Each named property has a reverse mutation: admit a tag ref, permit a
credential-bearing identity, treat REMOTE_TRACKING_CACHE as direct authority, and collapse the
local-to-remote transition. Each mutation must turn its named cell red and restore byte-identical.
The shortcut mutation must enter the production reducer in integration.py, not a fixture or a
re-derived test transition. In this ticket that file contains only the pure state reducer; it must
not declare, invoke or receive a NonForcePushPort. The later push/readback ticket alone extends
the same module with its injected effect orchestration.

Ticket 01 commands are deterministic and fixed:

    py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_authority_contracts.py
    py -3.11 -m mypy --strict library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/integration.py tests/test_project_authority_contracts.py
    py -3.11 -m compileall -q library/local_orchestration/project_authority/__init__.py library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/integration.py
    git diff --check <ticket-baseline> HEAD

This closure applies the required missing-value, path-identity, error-code-consistency, exception
behavior and test-truthfulness review categories. Authorization, token parsing, task/worktree,
staging, XSS and provider-effect categories are N/A for Ticket 01 with its pure boundary; the
later ticket that crosses each boundary must reclassify it rather than inherit that N/A claim.

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
13. Ticket 01 creates only the four Revision-03 seam paths, executes the four fixed commands,
    and supplies a discriminating reverse mutation for every named typed-contract property.

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

## Revision signatures

| Date | Actor / baseline | Summary |
| --- | --- | --- |
| 2026-08-24 | Architecture owner / main / 926c2b75ce9933d181220a3a48ec1aae9c38ab0a | Ticket opening returned UPSTREAM_DECISION_REQUIRED because revision 01 named no focused test creation seam or deterministic command. Revision 02 adds only that already-required executable detail; the requirement, architecture, authority, effects and ticket order are unchanged. |
| 2026-08-24 | Architecture owner / main / 926c2b75ce9933d181220a3a48ec1aae9c38ab0a | Revision-02 review found its local-to-remote shortcut mutation could not reach the production reducer because integration.py was omitted from the ticket boundary. Revision 03 adds that pure reducer only, keeps all ports/effects out, and extends the fixed type/compile commands. |
| 2026-08-24 | Architecture owner / main / a3c08309697f9fa9baa3dca442f35abdc39a6a0d | Ticket-tree review found revision 03 left the public distinction between strict structural rejection and named domain failure implicit. Revision 04 names the pure input/result/transition interfaces and confines AUTHORITY_INTEGRATED finalization to the later validated push/readback closure. |
| 2026-08-24 | Architecture owner / main / ecbee4319ff6f7ceab878a3ddce5471154571890 | Ticket-tree admission review found Revision 04 referenced topology, authority-line role, provider kind and admission decisions without naming their finite enum types, leaving the public/AST surface incomplete. Revision 05 names and closes those enums only. |
| 2026-08-24 | Project owner-approved Sol decision / Terra supervisor reviewer / main / 6df6885ea093f1e37899f5252f8e4a1cc4feadb9 | Revision 06 closes the previously undefined Ticket 02 direct-observation public contract: strict request/read/result shapes, finite disposition and decision enums, one-call fake-port semantics, fail-closed precedence, C13-independent seam, exact three-path boundary, deterministic commands, and restore-backed reverse mutations. It changes neither Ticket 01's frozen API nor Ticket 03's push/readback finalization, requirement, architecture authority, or effect authority. |
| 2026-08-25 | Project owner / Terra supervisor reviewer / main / 381a089a8519875134c0f597c1c20f1be51fdb4a | Revision 07 records the owner-selected single provider-neutral Ticket 03 finalization boundary. It closes the fake non-force push/result, one-call direct-readback, final result, finite failure and exact three-path seam without changing requirement, authority topology, external-effect authority, or frozen Ticket 01/02 contracts. |
| 2026-08-25 | Terra supervisor reviewer / main / 28d484179576b80d7583ea3b5601850042dfabda | Revision 08 repairs only a Ticket 03 admission omission found before source mutation: the existing Ticket 01 actual-source test otherwise makes Revision-07's explicitly approved eight new `integration.py` exports impossible. Ticket 03 may extend that precise test allowlist while retaining every original frozen assertion; no public meaning, requirement, architecture, authority, effect or acceptance criterion changes. |
| 2026-08-25 | Terra supervisor reviewer / main / c99add58297d71d8e9d6d5b85978f2a68980d45c | Revision 09 completes the same pre-mutation ticket-closure correction after enumerating every committed project-authority package-surface gate. It adds only the Ticket 02 observation test, which must retain its immutable observation-module checks while extending `__init__.py` to the exact already-approved Revision-07 surface. No public meaning or external boundary changes. |
