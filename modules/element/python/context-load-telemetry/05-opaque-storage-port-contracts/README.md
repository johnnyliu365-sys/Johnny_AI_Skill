# Opaque storage port contracts

This element owns the pure contract module at
`library/local_orchestration/telemetry_storage/contracts.py` and its focused test at
`tests/test_telemetry_storage_contracts.py`.

It implements Ticket 05, closure `CLOSURE-CONTEXT-TELEMETRY-05-STORAGE-CONTRACTS`, revision 04.
The models reuse `OpaqueMetadataId`, `ProjectId`, `RevisionDigest`, `RouterModel`,
`ContextUsageRecord`, and `NonNegativeCount` from the existing workflow-router contracts.

The boundary is metadata-only and has no storage layout, path, filesystem, process, Git, network,
provider, host, runner, or dispatch effect. A later Johnny-owned adapter may implement the typed
`TelemetryStoragePort`; this element does not.
