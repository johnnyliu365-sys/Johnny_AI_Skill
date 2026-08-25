# Project authority integration — sealed Context

| Field | Value |
| --- | --- |
| Context state | `SEALED / CONTEXT_REVISION_03 / SPEC_REVISION_REQUIRED` |
| Router event | `REQUIREMENT_CHANGED → ARCHITECTURE / GRILL → CONTEXT → ACTION_COMPLETED` |
| Requirement change | `PRD-20260825-039` / `CHG-20260825-039` / `doc/requirements/active/2026/workflow-governance/REQ-20260825-039.md`; amends `PRD-20260824-038` / `CHG-20260824-038` delivery sequencing only |
| Architecture decision | `doc/adr/ADR-20260824-020-declared-project-authority-line-and-provider-enforcement.md`; `doc/adr/ADR-20260825-021-core-cluster-closure-and-deferred-operational-verification.md` |
| Baseline | `main@4df52d0df1fbe479cc9737d390df34d36e402b66` |
| Delivery scope | Workflow-governance control plane; no target-project, provider, GitHub-policy, push, release, deployment, or credential effect is authorized by this Context. |

## Confirmed facts and scope

1. A project authority line is declared data: a validated full `refs/heads/<name>` ref, a
   credential-free remote repository identity, topology, authority-line role and gate revision.
   `main`, `dev`, `staging`, current checkout, upstream configuration, `origin/HEAD`, a tag and a
   raw SHA are not authority by name alone.
2. Remote-tracking refs are caches. Direct remote observation must bind repository identity, full
   ref, SHA, read method, observer, observation time and normalized evidence digest. It is the
   only observation eligible to bind the integration base or prove remote completion.
3. The integration lifecycle is finite: `CANDIDATE → REVIEW_ACCEPTED → LOCAL_INTEGRATED →
   AUTHORITY_INTEGRATED`; rejection has its own `GATE_REJECTED` state, and any failed or unproved
   remote completion is `PUSH_UNCONFIRMED` with a specific finite failure. A successful process
   exit, local merge or CI status cannot skip those states.
4. `SINGLE_BRANCH` and `HIGH_COLLABORATION` are topology choices. The former may use one declared
   authority line. The latter requires an exact ticket PR (current head equals candidate; base
   equals the authority ref) and provider evidence that the UI cannot bypass the gate and that a
   changed head invalidates approval. PR and CI remain review evidence, not integration authority.
5. Maturity, assurance and topology are distinct. POC/COMPACT may use a single authority line and
   a meaningful reviewer counter-mutation; STANDARD and HIGH_ASSURANCE add review depth. High
   collaboration never claims enforcement until its provider capability is directly proved.
6. Same-lifetime dispatch remains `reviewer → wait → review → gate`; it does not read or require
   the bridge. Cross-lifetime delivery alone uses the exact `NOT_REQUIRED` / `AVAILABLE` /
   `UNAVAILABLE` capability set. `UNAVAILABLE` means owner-mediated artifact relay, not a wake.

## Architecture and test seams

```text
validated authority contract + reviewed candidate
  -> DirectRemoteObservationPort (read exact base)
  -> gate-local integration (LOCAL_INTEGRATED)
  -> NonForcePushPort (declared ref only)
  -> DirectRemoteObservationPort (read exact target)
  -> AUTHORITY_INTEGRATED | PUSH_UNCONFIRMED

HIGH_COLLABORATION additionally:
  PullRequestReadPort + ProviderPolicyReadPort
  -> current-head/current-base/approval + proved-enforcement evidence
  -> gate admission; never a second integration path
```

Pure contracts and reducers own ref grammar, repository identity, finite lifecycle, observations,
PR/policy evidence and failures. Port adapters own remote/provider I/O; a composition root injects
them. Tests replace every port with deterministic fakes. No pure contract imports a provider,
shell, local repository path, credential, Router transcript or target-project source.

## Required evidence boundaries

- Persist only opaque/project identifiers, full refs, commit SHAs, finite state/failure, bounded
  timestamps, provider-policy identifiers and normalized evidence digests. Reject rather than
  ambiguously redact credential-bearing URLs, headers, tokens, raw provider responses, prompts,
  source trees, unrestricted command output or uncommitted worktree contents.
- Counter-mutations must prove cache non-authority, remote movement, post-push missing/mismatched
  direct readback, stale PR approval, wrong PR base, CI-without-gate non-authority,
  UI-bypass/enforcement failure, credential rejection, and bridge-unavailable synchronous flow.
  A zero-red mutation is a finding, not a pass.
- Provider-policy readback, policy configuration, target-remote push, live provider command,
  release and deployment are distinct external effects. A later ticket requires exact owner
  authority for each; this Context authorizes only typed local source design and fake-port tests.

## Delivery reclassification

PAI-01 through PAI-05 are the reviewable local core. PAI-06 is a future per-project live
qualification and PAI-07 is a future shipped-governance verification; neither is admitted or
executed by this Context. PAI-08 may close only the local core with
`CORE_CLUSTER_CLOSED_WITH_DEFERRED_OPERATIONAL_VALIDATION`. That result explicitly leaves provider
enforcement, target-repository qualification, plugin publication, immutable tag, and CLI
installation verification unproved.

## Specification handoff

The next exact artifact is `modules/spec/project-authority-integration.md` Revision 11. It must preserve the
separate maturity/assurance/topology axes; declare the direct-observation freshness/race boundary;
make `PUSH_UNCONFIRMED` durable and recoverable without force push; define provider capability as
`PROVEN`, `UNPROVEN`, `UNSUPPORTED` or `NOT_APPLICABLE`; bind reviewer counter-mutations; and
separate pure source/test tickets from live provider-policy qualification and shipped skill release,
while making the latter two future verification records rather than predecessors to the core
closure.

No ticket is approved, no agent is dispatched, and no external effect is authorized until that
specification and its exact ticket are independently approved.
