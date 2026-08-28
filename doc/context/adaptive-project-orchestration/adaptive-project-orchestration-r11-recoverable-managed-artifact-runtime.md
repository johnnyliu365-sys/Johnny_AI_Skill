# Adaptive Project Orchestration Context — Revision 11

| Field | Value |
| --- | --- |
| Feature cluster | `adaptive-project-orchestration` |
| Artifact | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED / SPEC_REVISION_11_REQUIRED` |
| Authority / change | Project owner architecture decisions, 2026-08-28 (Asia/Taipei) / `PRD-20260828-044` / `CHG-20260828-044` / `ADR-20260828-032` |
| Replaces | Revision 09 only for R09B runtime recovery, trust-boundary and resolver facts. Revision 09 remains historical authority for managed-artifact planning and behavior-adapter facts. |
| Accepted baseline | `5e351ce9d57af321dfb14c6b102e9749da7efc25` |
| Responsibility boundary | Stable facts for a recoverable, runtime-owned local transaction; no target authority, plugin behavior adapter, provider, runner, queue, receipt, publication, installation or deployment behavior. |

## Sealed facts

- Runtime, not Plugin/CLI, independently revalidates every transaction safety invariant from the
  exact typed plan and observed workspace state. The plugin/CLI is an untrusted intent boundary.
- The runtime records snapshots and recovery metadata before target mutation in private per-worktree
  Git metadata, behind an advisory cooperating-runtime lock. The exact target document tree and
  Git commit graph remain unchanged by the recovery record itself.
- Every effect uses a fresh compare-and-swap observation. If external bytes differ from the runtime
  candidate during rollback/recovery, runtime preserves them and enters `RECOVERY_REQUIRED`; no
  later apply may mutate the workspace until recovery has been proved.
- Recovery and temporary cleanup have exactly two attempts. Only a proof of every original
  byte/absence and zero temporary residue clears the active recovery record. Settled evidence is
  metadata-only; private raw snapshots are then removed.
- Post-state identity uses the existing exact `ArtifactTreeResolver` tuple. R09B adds no shorthand
  or sibling discovery. Any future declared shorthand has an explicit canonical namespace and must
  reject zero or multiple candidates rather than selecting one.
- Expected resolver decisions remain finite. A narrowly classified resolver-boundary runtime
  invariant failure is sanitized as `RUNTIME_INVARIANT_FAILED` after successful recovery; no broad
  exception normalizer is authorized.

## Reusable-module selection

```text
selected: exclusive-file-lock@6b5a7c1
why: serializes cooperating runtime instances around one per-worktree recovery record.
read: module card -> library/local_orchestration/file_lock.py -> tests/test_file_lock.py.
dependency: none.
boundary: advisory only; uncooperative file writes remain possible and are contained by runtime
          compare-and-swap/recovery checks. No telemetry, provider, host or target authority crosses it.
```

## Provenance and downstream binding

- Source review evidence: `REVIEW-ADAPTIVE-R09B-MANAGED-ARTIFACT-TRANSACTION-01` at authority
  commit `5e351ce9d57af321dfb14c6b102e9749da7efc25`.
- Architecture decision: `doc/adr/ADR-20260828-032-recoverable-managed-artifact-runtime.md`.
- The effective SPEC identity remains the existing Adaptive Project Orchestration SPEC. Revision 11
  must amend only the R09B closure; no ticket may be opened until its exact revision is owner-approved.
- Old R09B candidates are non-authoritative evidence. A successor ticket starts from the approved
  authority baseline and must not rebase or amend their historical commits.
