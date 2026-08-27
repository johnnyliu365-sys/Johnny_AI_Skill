# 11｜Per-stream ownership-ledger readiness

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-11-PER-STREAM-OWNERSHIP-LEDGER-READINESS` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 08 / AC-16 through AC-18 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 08 / `ADR-20260827-025` and `ADR-20260827-026` |
| State / closure | `OPEN / HIGH_ASSURANCE_REQUIRED`; `CLOSURE-CONTEXT-TELEMETRY-11-PER-STREAM-OWNERSHIP-LEDGER-READINESS`, revision 01 |
| Document revision | `01` |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): Revision 07 authorizes architecture-conformant private ledger/CAS and transaction decomposition. Revision 08 / `ADR-20260827-026` closes this representation correction; no public behavior or new external effect is introduced. |
| Source baseline / dependency | `88ddf04bfc8751b6ad27b6727c61af6f4ab37d49`; candidate must descend from the committed ticket authority. Ticket 09 (`096d471`) supplies the exact lock port; Ticket 10 (`a06c0fd`) supplies the private ledger seam. Ticket 06 remains `SUPERSEDED` and non-integrable. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; one synchronous owner lane and no helper. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-11-per-stream-ownership-ledger-readiness` on `implement/context-load-telemetry-11-per-stream-ownership-ledger-readiness` from committed `main` that descends from the source baseline, then binds its exact ticket revision and baseline. This same-lifetime lane needs no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11, complete annotations, strict finite DTOs, `mypy --strict`, adversarial mutation evidence and full review. Durable ownership state raises assurance; the one private seam is fully closed, so Luna/xhigh implementation plus Terra/xhigh review remains sufficient. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Only disposable test roots may contain pre-provisioned private entries. No telemetry stream/journal, provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, publication, release or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/telemetry_storage/ownership_ledger.py
modify = tests/test_telemetry_ownership_ledger.py
create = modules/element/python/context-load-telemetry/11-per-stream-ownership-ledger-readiness/
modify = modules/element/python/context-load-telemetry/11-per-stream-ownership-ledger-readiness/
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/telemetry_storage/local_lock_adapter.py
forbid = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
forbid = library/local_orchestration/telemetry_storage/composition.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = library/local_orchestration/path_containment.py
forbid = library/local_orchestration/file_lock.py
forbid = library/workflow_router/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

`LocalTelemetryOwnershipLedger` retains its private direct-module port and all existing finite
decisions, but replaces the aggregate `ownership-ledger/ledger.json` document with one canonical
private document per exact immutable storage identity:

```text
telemetry_root/
  ownership-ledger/
    entries/
      <sha256("johnny-telemetry-ownership-ledger-v1" + NUL + storage_ref + NUL +
              project_id + NUL + stream_id + NUL + ownership_ledger_ref)>.json
```

The per-entry document is strict, schema-versioned and contains exactly one complete already
pre-provisioned `TelemetryOwnershipLedgerEntry`. The digest and every filesystem path are
internally derived; no result serializes a path. Every derived root, entry directory, entry file,
temporary file and legacy aggregate location passes containment before effect. An existing
`ownership-ledger/ledger.json` is an unrecognized legacy shape: every private lookup/CAS returns
sanitized `BOUNDARY_REJECTED`, creates or migrates nothing, and leaves all bytes unchanged.

The existing `resolve` and `compare_and_swap` retain their semantics. Normal resolve still
requires the caller's exact expected revision and returns `CLOSED` for a detached/removed entry.
Add only a private `resolve_current` recovery lookup: it matches the four immutable coordinates,
intentionally ignores the caller-provided storage revision, returns the current entry even when
closed, and performs no lifecycle admission, provisioning or mutation. The future transaction
adapter may call it only after acquiring the exact lock and before ordinary final admission.
No public export, public DTO, provisioning API, lock behavior or composition binding changes.

`TicketDecompositionDecision = HIGH_ASSURANCE_REQUIRED`: this corrects durable ownership state
whose representation must agree with the exact lock boundary. It is one independently observable
private ledger seam: no stream codec, transaction journal, public response mapping or
composition is included. The later adapter ticket may not start until this closure is integrated.

## Frozen implementation rules

Modify only `ownership_ledger.py` and its focused test module. Preserve strict immutable Pydantic
models, named finite results, containment rejection, no path exposure, same-directory temporary
write + flush/fsync + owned replacement, and no retry/sleep/poll/self-lock behavior. The private
per-entry document must reject extra fields, duplicate/invalid data, malformed JSON and a stored
entry whose immutable identity does not equal the digest-derived request identity.

`resolve_current` may not be a public package export and may not take a caller path, root,
lifecycle or next revision. It ignores only the candidate `storage_revision`; malformed identity,
unknown entry, mismatched stored immutable fields, containment failure, legacy aggregate file,
filesystem failure or validation failure remains a finite private non-success with no effect.
`compare_and_swap` must still reject an old expected revision as `CONFLICT` and must never use
the recovery lookup to bypass ordinary revision/lifecycle admission.

The tests may seed exact private entry documents inside a disposable root, including two distinct
identities. Production code must not acquire a lock itself: the later adapter owns the lock
lifetime. A spawned independent-process fixture may call the private CAS seam only against
test-seeded entries; it must not create production provisioning behavior.

Create `modules/element/python/context-load-telemetry/11-per-stream-ownership-ledger-readiness/README.md`
as a target-owned index to this ticket, the exact private module, focused tests,
`path-containment@cf9e126`, Ticket 10 and `ADR-20260827-026`. It copies no production source and
claims neither transaction, stream, provisioning nor composition behavior.

### Reusable-module selection record

```text
selected: path-containment@cf9e126
why: reject every derived root/entry/legacy location whose base or existing ancestor redirects
     outside the injected Johnny telemetry root before lookup or replacement.
read: path-containment README -> public import -> worktree-containment behavior evidence.
dependency: standard library only.
rejected: exclusive-file-lock@60d2ab0 (the later adapter owns lock lifetime);
          JsonlContextUsageStore; Ticket 06's superseded candidate; provider/host/runner paths.
gap: no ownership-ledger reusable card exists; this is target-owned private infrastructure.
boundary: no stream, transaction, provider, host, target, publication, release or deployment.
```

## High-assurance adversarial matrix

| Risk | Required ticket evidence | Excluded follow-on concern |
| --- | --- | --- |
| Two stream locks serialize different entries only | LRA4/LRM1 prove independent processes advancing distinct streams preserve both post-states. | Actual lock acquisition and journal recovery. |
| Recovery trusts a stale caller revision | LRA3/LRM2 prove `resolve_current` finds only the current immutable entry while ordinary resolve/CAS still rejects stale revision. | Transaction phase choice. |
| Legacy aggregate data is silently treated as owned | LRA5/LRM3 prove named rejection with zero migration/repair effect. | A separately authorized migration. |
| Derived location escapes the private root | LRA5/LRM4 prove containment rejection before effect. | Lock-held stream access. |

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| LRA1 | A disposable fixture seeds one strict per-entry document. Exact normal lookup returns `FOUND` with matching entry and no path; normal CAS advances only its lifecycle/revision through owned atomic replacement. |
| LRA2 | Missing entry and malformed/cross-coordinate identity return a finite non-success with no file creation. Normal lookup uses the expected revision; a stale normal lookup is `OWNERSHIP_MISMATCH` and stale CAS is `CONFLICT`, with bytes unchanged. |
| LRA3 | After a fixture advances an entry, `resolve_current` returns its current revision and lifecycle even when the candidate reference carries an old revision or the current lifecycle is closed. It changes no bytes; normal resolve/CAS retain revision and closed admission. |
| LRA4 | Two spawned independent processes start from two test-seeded distinct exact identities, each CASes only its own entry, and both return `FOUND`. Both per-entry documents retain their own requested post-state; no aggregate file exists. |
| LRA5 | Aggregate legacy `ownership-ledger/ledger.json`, malformed/extra-field entry document, stored-coordinate/digest mismatch, redirected root/entry ancestor and injected replacement failure return `BOUNDARY_REJECTED` with no migration, auto-create, external write or path/error leakage. |
| LRA6 | AST/source gates prove a domain-separated digest includes all four immutable coordinates; no aggregate writer, public export, create/provision/register/repair API, lock/codec/provider/host import, raw-path input/output, dynamic mapping/`Any`/cast, retry/sleep/polling, or mutation outside CAS is introduced. |
| LRA7 | Focused tests, strict type check and compilation pass. Test seeding and spawned process helpers are test-local; candidate diff and clean worktree remain reviewer evidence, not persisted test assertions. |
| LRM1 | Reverse-mutate the per-entry derivation so two distinct streams select one location; LRA4 turns red, then byte-exact restoration returns green. |
| LRM2 | Reverse-mutate `resolve_current` to check caller revision; LRA3 turns red, then byte-exact restoration returns green. |
| LRM3 | Reverse-mutate legacy aggregate detection to accept/ignore it; LRA5 turns red, then byte-exact restoration returns green. |
| LRM4 | Reverse-mutate containment rejection for an entry/ancestor; LRA5 turns red, then byte-exact restoration returns green. |

Strong-type preflight constructs every new or retained private success/failure DTO through ordinary
constructors and validates finite decision, lifecycle, revision, nullability, identity and
per-entry document forms. No cast, `Any`, bypass constructor, dynamic lookup, mock or caller
path is success evidence. The LRM cells are required reverse evidence; this correction has no
baseline-red claim.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_ownership_ledger.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/ownership_ledger.py tests/test_telemetry_ownership_ledger.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/ownership_ledger.py
git diff --check 88ddf04bfc8751b6ad27b6727c61af6f4ab37d49 HEAD
git status --short
```

The Terra/xhigh reviewer validates the ticket blob/baseline/boundary, all four-coordinate digest
inputs, source directions and no-auto-repair rule; reruns focused/type/compile gates; independently
forces a cross-stream preservation failure and a forged revision recovery failure; verifies
legacy rejection does not hide data; then runs the full suite in the candidate and records any
baseline-equivalent failures with complete output. Review must prove no Ticket 11 source reaches
legacy codec, public composition, stream/journal or target/Git behavior.

Return exactly one `ImplementationReturn`: `COMPLETED` with command/evidence references,
`BLOCKED` with the named blocker and zero uncommitted scope expansion, or `CHANGE_DETECTED` for
a contradiction in the exact committed authority. The implementation owner does not commit,
push, run `admit_document_mutation`, edit this ticket or open another worktree. The reviewer
alone reviews, commits the candidate, admits document mutation, pushes and directly reads back
the authority ref.
