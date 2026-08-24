# 04 — Revision 03 Telemetry Architecture Admission

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TAD-TELEMETRY-R03-ARCHITECTURE-01` / `TICKET_ADMISSION_DECISION` |
| Authority | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 03 / `ADR-20260824-019` |
| Requirement / Context | `PRD-20260803-006` / `CHG-20260803-006` / `doc/context/context-load-telemetry/main.md` Revision 03 |
| Baseline | `1849515f911d1376d800fe1b19e0e07b5227028b` |
| Decision | `DECOMPOSITION_AUTHORIZED` |
| State | `CLOSED / NO_EFFECT`; this is an architecture-admission artifact, not an implementation ticket |
| XSS / effects | `XSS_NOT_APPLICABLE`; no Browser/WebView/DOM/JavaScript or provider/host/filesystem/target/network effect is authorized here. |

## Resolution of the Revision 02 blocker

The original immutable `TAD-TELEMETRY-R02-STORAGE-01` remains at SHA-256
`d62904fe00f4cb54fa75f2db1c60d58833ef92d1b3f5d49827a6d3ee9cdd7115`. Its three missing
architecture contracts are now fixed by Revision 03:

1. `TelemetryStorageRef` is opaque; the ownership ledger and composition root are the only
   resolver. Validation order is identity/payload, ownership, lifecycle, containment, then record.
2. The named `TelemetryStoragePort.execute(request) -> response` has strict discriminated
   request/response members. Its injected Johnny-owned adapter is the only code allowed to use
   the legacy raw-path JSONL codec; the `READ` member returns a complete immutable tuple of
   metadata-only validated `ContextUsageRecord` values, while no public surface contains a path.
3. `APPEND`, `READ`, `VALIDATE`, `DETACH`, and `UNINSTALL` have one exact `ACTIVE` precondition,
   a finite payload matrix, exact result-field presence, and terminal detached/removed behavior.

For every successful result, `storage_revision`, `lifecycle`, and `record_count` are required.
`validation_report_ref` is required only for successful `VALIDATE`; `failure_ref` is required only
for a failed finite decision. Failures echo the request's expected revision only and expose no
current revision, resolved path, raw diagnostics, record, prompt, source or credential.

## Provider-usage boundary

The new provider-neutral evidence port does not grant a real Provider invocation. It may first be
implemented only with typed fake terminal events. Missing, malformed, replayed, mismatched or
extra-field events return a named failure before append. `OBSERVED_USAGE` reports a single actual
host count and can never state a saving. Only `MATCHED_REDUCTION` may report provider input-token
reduction, and only after the frozen isolated-pair conditions in Revision 03 pass.

## Authorized ticket decomposition order

The reviewer may create serial vertical tickets with the following boundaries:

1. opaque storage identity/request/result contracts, including the complete strict result matrix
   and `TelemetryStoragePort` protocol;
2. Johnny-owned storage adapter, lifecycle and sanitized aggregate-report seam, using only a
   disposable Johnny-root test fixture;
3. provider-usage terminal-event admission with a fake port and no host/provider invocation;
4. one host-specific `HIGH_ASSURANCE` capability probe, only after the owner separately grants a
   one-attempt external-effect authority; and
5. one isolated matched-pair experiment ticket, only after the host-specific probe is proven.

The fourth and fifth closures are not dispatchable from this decision. Cost or billing conversion
requires a separate requirement change. No ticket may write a target repository telemetry path,
capture raw content, or convert an unavailable host field into an estimate or zero.

## Router return

`ACTION_COMPLETED / DECOMPOSITION_AUTHORIZED`. The next legal action is reviewer-owned creation of
the first pure no-effect storage-contract ticket against the sealed Revision 03 baseline.
