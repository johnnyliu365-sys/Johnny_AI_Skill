# Ticket 05B4B2E2A Codex Oracle Version Observation Code Review

## Review decision

`APPROVED / READY_TO_MERGE`

The exact handoff adds one child-backed, caller-independent VERSION observation
to the staging oracle. It does not implement E2, call a host Codex installation
or create a new executable/path authority.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e2a-codex-oracle-version-observation`; `CLOSURE-LOCAL-INSTALL-T05B4B2E2A-01`; V1-V8 |
| Owner / branch | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; `codex/implementation-codex-oracle-version-observation-05b4b2e2a` |
| Chain | Dispatch `a51adfb3412e38bfb108f950f5628cea7bfc24af` -> implementation `e273515e6e5b4cfd9b9869342a20b2eed5d1d605` -> docs-only handoff `6a752f4d79fcb8e7af47ad9d00c05a3484fd4505` |
| Scope | Implementation changes exactly the seven authorized staging protocol/oracle and focused-test paths; handoff changes only `doc/WorkProgressReport.md`. The submitted worktree is clean and the three-worktree topology is unchanged. |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| V1 first red | PASS: the submitted evidence records missing `CodexVersionObservation` and `ORACLE_STAGING_CODEX_VERSION` before staging source changed. |
| V2 protocol | PASS: VERSION has one exact strict payload; missing, extra, duplicate, malformed and cross-surface payloads reject through existing finite protocol reasons. |
| V3-V4 source authority | PASS: `initialize` writes the named `ORACLE_STAGING_CODEX_VERSION`; the child reads it from exact persisted state. A deliberately different `identity.plugin_version` cannot select the result. |
| V5 failure boundary | PASS: missing, extra, blank and constructed-invalid version state fail as `STATE_INVALID` without response success or command/response residue. Existing lease, topology, process and cleanup finite mappings remain covered. |
| V6 zero mutation | PASS: VERSION leaves exact state bytes, owned/foreign collections and the complete payload byte tree unchanged. |
| V7 source discipline | PASS: no `Any`, `type: ignore`, broad catch, caller-selected executable/path, live Codex, target-project effect or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| V8 evidence | PASS: discriminator, caller-source and state-write reversals independently turned the named tests red and exact blobs were restored. |
| CodeReview.md §2.1 | Path/authority, null/constructed-invalid, finite exception/result, evidence-truthfulness and source-boundary checks pass. XSS class 8 is not applicable because there is no Browser, WebView, DOM/HTML renderer, JavaScript context or privileged bridge. |

## Independent verification

- Unicode-safe, repository-external snapshot of exact handoff: focused protocol
  and oracle suites 27/27; serial full discovery 374/374 in a unique external
  runtime temp root; strict mypy 132 files; in-memory compile 132 files.
- The first full run shared the host `%TEMP%` with the concurrently running E3A
  implementation and produced two cross-suite `johnny-stage-env-*` snapshot
  collisions. A repository-local temp attempt correctly failed its outside-repo
  invariant. Re-running in a unique external temp root passed 374/374. This is
  test-harness concurrency evidence, not an E2A functional failure.
- `git diff --check`, exact seven-file implementation scope, WPR-only handoff,
  dispatch ancestry, source/XSS sentinels and clean submitted lane pass.

## Disposition

`APPROVED / READY_TO_MERGE`. Guarded integration may merge only exact handoff
`6a752f4d79fcb8e7af47ad9d00c05a3484fd4505`, preserving this approval in the
first-parent control history. No staging push, package, release, deployment or
target-project action is authorized.
