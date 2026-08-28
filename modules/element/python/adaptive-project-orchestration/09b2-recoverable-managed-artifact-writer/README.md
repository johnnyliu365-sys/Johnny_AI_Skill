# R09B2 recoverable managed-artifact writer — element index

| Field | Binding |
| --- | --- |
| Ticket / closure | `TICKET-ADAPTIVE-R09B2-RECOVERABLE-MANAGED-ARTIFACT-WRITER` / `CLOSURE-ADAPTIVE-R09B2-RECOVERABLE-MANAGED-ARTIFACT-WRITER-01` |
| SPEC / requirement / context / ADR | Revision 11 / `PRD-20260828-044` / `CHG-20260828-044` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` / `ADR-20260828-032` |
| Source / test | `library/local_orchestration/target_document_management.py` / `tests/test_recoverable_managed_artifact_writer.py` |
| Frozen dependencies | R09A `ManagedArtifactPlan`; R09B1 `ManagedArtifactWriteResult` and `ManagedArtifactRecoveryResult`; canonical `ArtifactTreeResolver`; `exclusive-file-lock@6b5a7c1` |
| Ownership | This element indexes only the private local recoverable writer. It does not change the legacy writer, planner, resolver, result contracts, lock implementation, plugin/CLI trust boundary, target authority, host adapter, runner, queue, receipt, provider, publication, installation, release or deployment. |

The writer persists its record and raw snapshots only under the selected worktree's Git metadata
path. Snapshot bytes never appear in typed outcomes or any externally composable artifact. The lock
is advisory; target truth comes from independent pre-effect and post-effect compare-and-swap
validation. On unrecoverable settlement it retains a sanitized, opaque recovery identity and fails
closed until explicit recovery proves exact settlement.
