# ADR-20260824-020 — Declared project authority line and provider-enforcement evidence

- Date: `2026-08-24 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260824-038` / `CHG-20260824-038`
- Narrows: historical hard-coded-`main` language in integration descriptions; it does not replace
  `ADR-20260823-014` or `ADR-20260823-016`.

## Context

A local fast-forward merge answers only that one checkout moved. A local `origin/<branch>` is a
remote-tracking cache, not a read of the remote at the moment of the decision. A green CI run, PR
state, browser screen, receipt, runner, or successful push exit status also fails to prove that an
exact reviewed candidate is now the remote authority line. Cross-machine work exposed this gap:
two valid-looking local histories gave different answers because no contract said which remote ref
was authoritative or when integration had actually completed.

Separately, ADR-014 and ADR-016 establish that same-lifetime work is synchronous:
`reviewer → wait → review → guarded integration`. The runner and receipt-bound wake path bridge
different lifetimes only. Requiring that optional mechanism before same-lifetime dispatch both
blocks work and misreports a missing bridge as a delivery failure.

## Decision

1. **A versioned authority-line contract is the integration source of truth.** It declares a
   credential-free remote repository identity, `project_authority_ref` as a validated full branch
   ref, topology (`SINGLE_BRANCH` or `HIGH_COLLABORATION`), authority-line role, gate identity and
   revision. No branch name, including `main`, has inherent authority.
2. **Remote truth is directly observed.** A direct remote protocol or qualified provider readback
   records the repository, full ref, SHA, method, observer, time and normalized evidence digest.
   Local branch state and `origin/<ref>` remain useful diagnostics but are never admission or
   completion proof.
3. **Integration has two completed-looking but non-equivalent states.** Gate success yields
   `LOCAL_INTEGRATED`. Only a non-force push to the declared ref followed by exact direct remote
   SHA readback yields `AUTHORITY_INTEGRATED`. A missing, failed, ambiguous, stale or mismatched
   readback yields `PUSH_UNCONFIRMED`; no process exit code upgrades it.
4. **Topology is declared rather than prescribed.** A single-worker project may declare one
   authority line such as `refs/heads/main`. High-collaboration projects may declare independent
   development, staging and release lines; those names and promotion links are project data.
5. **High collaboration separates visibility from authority.** It requires one current ticket PR
   (`head_sha == candidate_sha`, `base_ref == project_authority_ref`) and approval bound to that
   head. PR review and CI are evidence only; the gate remains the sole integration authority.
6. **Provider enforcement is evidence-qualified.** Before a high-collaboration project claims
   enforcement, a provider readback must prove that ordinary UI actors cannot merge/update the
   declared authority line around the gate and that a changed PR head invalidates prior approval.
   The exact GitHub mechanism is deliberately not assumed. Unsupported or unreadable capability is
   `PROVIDER_ENFORCEMENT_UNSUPPORTED` or `PROVIDER_ENFORCEMENT_UNPROVEN`, not a weaker success.
7. **Profile scales ceremony, not truthfulness.** A POC/COMPACT project may use a declared single
   branch and an independent meaningful counter-mutation. STANDARD and HIGH_ASSURANCE add review
   depth appropriate to risk. High collaboration requires its PR/provider proof at every
   assurance level. Maturity, assurance and collaboration topology stay distinct fields.
8. **Synchronous dispatch remains bridge-free.** Same-lifetime dispatch may not be blocked for
   absent runner, queue, receipt, descriptor, host gateway, or workspace/profile readback.
   Cross-lifetime delivery preserves exactly `NOT_REQUIRED`, `AVAILABLE`, and `UNAVAILABLE`; the
   last state means an owner relays an artifact, never that a wake occurred.

## Consequences and implementation boundary

The future pure contracts must expose finite failures at least for a missing/invalid authority
contract or ref, remote identity mismatch, unavailable/ambiguous direct read, remote movement,
candidate/review/counter-mutation mismatch, PR requirement/head/base/stale approval failures,
unproved or unsupported provider enforcement, rejected push, unconfirmed push, remote SHA
mismatch, and detected Secret material.

Implementation is deliberately staged: pure authority state and validators; direct-remote and
staleness port; gate/push/readback composition; PR/policy readback schema; separately authorized
provider qualification; profile-scaled review closure; and finally the shipped governance-text
alignment. The last stage changes `skills/`, an enumerated Level 1 payload tree, so it must follow
the normal regenerated-root, new-version, immutable-tag and real CLI verification release path.

No ticket created by this ADR may mutate a target repository, configure GitHub, invoke a provider,
push, release, deploy, or use credentials unless a later exact ticket receives scope-bound owner
effect authority. Persisted evidence is metadata-only and credential-free.

## Alternatives rejected

- **Always use `dev`/`staging`/`main`.** It imposes collaboration ceremony on a one-line project
  and mistakes a recommended topology for authority.
- **Trust `origin/<ref>` after fetch.** A refreshed cache is still not a direct proof that the
  remote accepted the later candidate.
- **Treat a successful local merge or push exit as completion.** Both leave a distinct,
  consequential state unrepresented.
- **Let CI or PR merge state authorize integration.** That creates a second gate and makes a
  provider UI action capable of bypassing the documented boundary.
- **Build bridge infrastructure before synchronous dispatch.** It conflicts with ADR-014 and
  ADR-016, consumes effort, and fabricates a prerequisite where none exists.

## Recovery

When direct remote proof fails, preserve the local attempt as `PUSH_UNCONFIRMED`, diagnose
read-only, and use a new gated forward fix or revert if needed. Never force-push an authority line
or rewrite its history. Provider-policy rollback is another explicitly authorized external effect
with before/after direct readback. A missing cross-lifetime bridge remains `UNAVAILABLE`; normal
synchronous work continues without it.
