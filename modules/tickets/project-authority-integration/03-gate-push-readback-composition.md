# Ticket 03 — gate, push, and readback composition

| Field | Value |
| --- | --- |
| Ticket ID | PAI-03-GATE-PUSH-READBACK-COMPOSITION |
| State | COMPLETED / INTEGRATED at `98bafbab01e51d2bd3edf6079cda981710651e80` |
| Acceptance Closure Set | ACS-PAI-03 Rev.01 |
| Dependencies | PAI-01 integrated at `6df6885ea093f1e37899f5252f8e4a1cc4feadb9`; PAI-02 integrated at `9b8e82a48b0997fc63deaf04d931e93857d96246` |
| Source specification | Project authority integration SPEC Revision 09, Ticket 03 seam and complete historical-gate correction |
| Context / change / architecture | `doc/context/project-authority-integration/main.md`; `PRD-20260824-038` / `CHG-20260824-038`; `ADR-20260824-020` |
| Planning baseline | main at `381a089a8519875134c0f597c1c20f1be51fdb4a`; the implementation-admission baseline is the clean current integration main recorded by the reviewer at dispatch. |
| Delivery / model | POC pure-source closure; Luna/xhigh implementation owner, Terra/xhigh supervisor-reviewer. The reviewer capability is not lower than the implementer capability. |
| Effect boundary | Deterministic fake `NonForcePushPort` and fake `DirectRemoteObservationPort` only. No target remote mutation, push, force, credential, provider, shell, Git executable, process, network, filesystem, environment or clock access. |
| Completion evidence | The integrated source candidate is `98bafbab01e51d2bd3edf6079cda981710651e80`, a current-main ancestor. Its ticket-closure and completion-index records are `01d28c8f5f83ee31f61bf00053a575945e1b29e1` and `8db99208d6b363f7b34a731989a4a7085cb0da00`; the feature index records the same integrated commit. |

## One observable closure

The owner-selected public boundary is one provider-neutral
`finalize_authority_integration(...)` API. Given a validated `LOCAL_INTEGRATED` lifecycle
record, one direct pre-push observation, and injected fakes, it may return
`AUTHORITY_INTEGRATED` only after exactly one accepted non-force push and exactly one post-push
direct readback whose SHA exactly equals `local_integrated_sha`. Every other outcome is
`PUSH_UNCONFIRMED` with one finite failure. A push result, local merge, cache, CI, PR state, or
exit status alone is never remote authority.

This is new behavior. Record green evidence for the named cells and restore-backed reverse
mutations; do not claim ceremonial baseline-red evidence. It is a same-lifetime pure closure:
no runner, queue, receipt, descriptor, gateway, workspace readback, host task, or bridge
mechanism is required or authorized.

## Exact writable boundary

```johnny-boundary
modify = library/local_orchestration/project_authority/__init__.py
modify = library/local_orchestration/project_authority/integration.py
create = tests/test_project_authority_finalization.py
modify = tests/test_project_authority_contracts.py
modify = tests/test_project_authority_observation.py
forbid = library/local_orchestration/project_authority/contracts.py
forbid = library/local_orchestration/project_authority/observation.py
forbid = library/local_orchestration/project_authority/collaboration.py
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
    Sort-Object -Unique
)
$declaredScopePaths = @(
  "library/local_orchestration/project_authority/__init__.py"
  "library/local_orchestration/project_authority/integration.py"
  "tests/test_project_authority_contracts.py"
  "tests/test_project_authority_observation.py"
  "tests/test_project_authority_finalization.py"
) | Sort-Object
$scopeDifference = @(Compare-Object -ReferenceObject $declaredScopePaths -DifferenceObject $implementationScopeEvidence)
if ($scopeDifference.Count -ne 0) { $scopeDifference | Format-Table -AutoSize; throw "HALT / CANDIDATE_SCOPE_MISMATCH" }
```

It must equal exactly the five declared paths, including an uncommitted new test file. No ticket,
SPEC, Context, review, worktree metadata, copied source, provider or untracked path is admitted.
The implementation owner does not commit, integrate, push, create a branch, or dispatch.

## Exact public contract and precedence

`integration.py` defines and `__init__.py` re-exports only the eight Revision-07 public names:
`NonForcePushDisposition`, `NonForcePushRequest`, `NonForcePushResult`, `NonForcePushPort`,
`AuthorityFinalizationFailure`, `AuthorityFinalizationRequest`, `AuthorityFinalizationResult`,
and `finalize_authority_integration`, plus the existing frozen Ticket 01/02 exports. Their exact
types and field shapes are those in SPEC Revision 07. All new models are strict, frozen,
`extra="forbid"`, non-coercing and revalidate instances. Every SHA is a full lower-case SHA;
every time is timezone-aware; nonblank strings reject blank values; all durable values remain
credential-free metadata.

The Ticket 01 test `test_pure_boundary_ast_gate_targets_owned_production_modules` is in scope
only to extend its `integration.py` expected `__all__` and declaration allowlists from the exact
three frozen Ticket 01 names to those three names plus the eight Revision-07 names; permit only
`DirectRemoteObservationPort`, `DirectRemoteObservationRequest`,
`DirectRemoteObservationResult`, `DirectRemoteObservationDecision`, and
`observe_declared_remote` from the observation import root; and replace only its historical
`NonForcePushPort` deny with the exact new declaration/import allowlist. Its `contracts.py`
allowlist, all other negative
assertions, and the equality (not subset) property remain unchanged. Any other change to that
historical test is out of scope.

The Ticket 02 test `test_direct_remote_observation_ast_gate_targets_owned_production_modules` is
in scope only to retain its exact seven-name `observation.py` export/declaration assertion and to
extend its package `__init__.py` expected sequence from frozen Ticket-01 base plus seven
observation names to that same sequence plus the eight Revision-07 names. Its historical
`NonForcePushPort` deny is replaced only by this exact new surface; all other deny/import/source
assertions remain unchanged. Any other change to that historical test is out of scope.

The function takes positional-only `request`, `push_port`, and `observation_port`. It may call
`push_port.push` once and only after validated local lifecycle/pre-push identity. `REJECTED`
maps to `PUSH_REJECTED`; `UNCONFIRMED` maps to `PUSH_UNCONFIRMED`; both make zero post-push reads.
For an accepted push, it calls the real `observe_declared_remote` exactly once using
`completed_at` as the lower freshness bound and no expected SHA. It then compares the accepted
direct readback SHA to `local_integrated_sha` itself. Equality is the sole authority-success
condition; inequality is `REMOTE_READBACK_SHA_MISMATCH`. The function does not use
`REMOTE_TRACKING_CACHE`, retry, loop, fallback, force, compose a real adapter, call a clock or
interpret a nonzero/zero exit status as remote truth.

## TDD and strong-type preflight

Before dispatch and again before implementation starts, construct each new enum member and every
public model/Protocol through ordinary constructors and a deterministic in-memory fake. Construct
both accepted and each rejected `AuthorityFinalizationResult` shape, reject unknown enum values,
null non-nullable fields, coercion, extras, naive datetimes, bad SHAs, blank identifiers,
credential-bearing metadata, non-direct pre-push observations, and inconsistent result shapes.
No `Any`, `cast`, dynamic lookup, bypass constructor, model copy/construct, raw dict, cache, or
historical object may substitute for an ordinary public contract path.

| Cell | Case | Required proof |
| --- | --- | --- |
| PAI-03-T01 | happy vertical closure | A local `LOCAL_INTEGRATED` record, identity-bound direct base, accepted fake push and matching post-push direct read returns `AUTHORITY_INTEGRATED`, no failure, and exactly one call to each port. |
| PAI-03-T02 | strict public surface | Constructs every finite enum/model and both Protocol fakes; rejects structural invalid values, unknown enums and inconsistent accepted/rejected result shapes. |
| PAI-03-T03 | local/base admission | A non-local lifecycle, lifecycle failure, cache/non-direct base, foreign repository/ref, or credential-bearing pre-push metadata returns the named failure before any push/read call. |
| PAI-03-T04 | push integrity | A fake push result with foreign repository/ref, wrong attempt, expected base or requested SHA fails closed. `REJECTED` gives `PUSH_REJECTED`; `UNCONFIRMED` gives `PUSH_UNCONFIRMED`; each performs zero readbacks. |
| PAI-03-T05 | post-push readback | Unavailable, missing, ambiguous, stale, identity-mismatched and credential-bearing direct readbacks map to finite failures and remain `PUSH_UNCONFIRMED`; no cache source may become authority. |
| PAI-03-T06 | equality/race | A direct post-push SHA unequal to `local_integrated_sha` returns `REMOTE_READBACK_SHA_MISMATCH`; a base mismatch returns `AUTHORITY_REF_MOVED`; neither returns authority success or retries/forces. |
| PAI-03-T07 | actual-source gate | Extends the existing Ticket 01 gate to retain its original exact `contracts.py` surface and require the exact three frozen plus eight Revision-07 `integration.py` exports; extends the Ticket 02 gate to retain its seven-name `observation.py` surface while requiring the exact package base + seven observation + eight finalization exports. The focused finalization test parses actual `integration.py` and `__init__.py`, pins the same full public surface/imports and rejects `Any`, `cast`, `getattr`, `setattr`, `__import__`, `eval`, `exec`, `model_construct`, `model_copy`, `open`, `os`, `pathlib`, `subprocess`, `socket`, `urllib`, `http`, `requests`, `git`, `shutil`, `time`, `datetime.now`, `datetime.utcnow`, loops/retries, force operations, Provider branches and cache fallback. |

## Required reverse mutations

| Mutation in real source | Cell turned red | Meaning |
| --- | --- | --- |
| Replace the exact accepted-readback SHA comparison with unconditional `AUTHORITY_INTEGRATED` success | PAI-03-T06 | A matching push exit or arbitrary direct read cannot be relabelled as remote authority. |
| Accept `REMOTE_TRACKING_CACHE` as a post-push source | PAI-03-T05 | Cache can never substitute for direct remote proof. |
| Add an undeclared public top-level symbol or a `subprocess` import to `integration.py` | PAI-03-T07 | Both historical gates and the focused gate pin the actual pure fake-port boundary. |

The Terra reviewer performs at least one different-path source counter-mutation, observes its
named focused test turn red, restores byte-identically, and records the evidence. A zero-red
mutation is a finding, not completion.

## Verification commands and deterministic result

```powershell
python -m pytest -q tests/test_project_authority_contracts.py tests/test_project_authority_observation.py tests/test_project_authority_finalization.py
python -m mypy --strict library/local_orchestration/project_authority/contracts.py library/local_orchestration/project_authority/observation.py library/local_orchestration/project_authority/integration.py
python -m compileall -q library/local_orchestration/project_authority
git diff --check <implementation-admission-baseline> HEAD
```

All commands exit zero. The source-scope union is exactly the declared boundary. No test invokes a
real remote or external command.

## Completion, rollback, and return

The implementation owner returns `ImplementationReturn.COMPLETED` with the exact ticket,
implementation-admission baseline, scope evidence, focused test/type/compile/diff evidence and
no commit SHA. The Terra reviewer reads the exact candidate, independently runs the named
counter-mutation, commits the candidate only after approval, and passes it through
`admit_document_mutation`. A rejected candidate leaves `main` unchanged. Rollback is a new
guarded forward fix or revert; no force push, history rewrite, remote write, credential or
Provider effect is authorized by this ticket.
