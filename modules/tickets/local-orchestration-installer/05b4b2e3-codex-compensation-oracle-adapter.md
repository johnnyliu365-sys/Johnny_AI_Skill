# 05B4B2E3 — Codex Compensation Oracle Adapter

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-02, AC-07 and AC-08 |
| State | `FROZEN / IMPLEMENTATION_DISPATCH_CONFIRMED / IMPLEMENT_ACTIVE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3-01` / A1-A8 |
| Dependency | E1, E3A `b324f91`, E3B `dc07eec`, E3C `c042af1` and E3D `b5541e4` approved/integrated |
| Planned owner | Task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent `workflow-implementer-2`; no new worktree/helper |
| Profile / XSS | `STANDARD`; one implementation owner / `XSS_NOT_APPLICABLE` |

## Reserved responsibility

Implement only one staging adapter over one exact leased 05S4 oracle. It exposes
the already integrated five-operation compensation port: plugin remove,
marketplace remove, plugin list, marketplace list and installed-path absence.
Every call revalidates the exact bound request through E3C, executes one fixed
oracle action, and admits its result only through E3D. Removal and absence proof
must follow the exact admitted result; list data, including foreign state, is
returned unchanged after recursive rebuilding. The adapter owns no
registration, environment allocation, composition, receipt or end-to-end
lifecycle.

## Current refreeze decision

E3D is approved and integrated by `b5541e4`; the dependency wait is resolved.
The adapter must consume the public E3C request revalidator and E3D response
admission directly. It may not copy either validator or inspect raw Pydantic
state itself. This is the final thin E3 effect seam, not a new protocol layer.

## Frozen design

- Add factory `create_oracle_compensation_adapter(lease: object, oracle: object,
  request: object)`. It returns either one factory-only adapter or one closed
  metadata-only rejection. It accepts only a recursively rebuilt live
  `EnvironmentLease`, exact `CodexLifecycleOracle` and exact E3C-revalidated
  request; rejection invokes no oracle action.
- The adapter retains only rebuilt lease/request, exact oracle and a deterministic
  `OracleIdentity`. Identity is derived from the bound manifest and the already
  integrated staging constants/root rules; logical paths are joined below the
  fixed staging root. Root or identity mismatch rejects at factory admission.
- Each public operation first revalidates its request with
  `revalidate_codex_compensation_port_request` and compares every rebuilt
  manifest value to the retained request. Invalid/foreign input returns the
  integrated matching `REQUEST_INVALID` failure before any oracle action.
- Each admitted operation issues exactly one matching `OracleCommand` on the
  retained lease, then calls `admit_codex_oracle_response` with the same action.
  `DEPENDENCY_BLOCKED` maps only to the integrated `DEPENDENCY_BLOCKED` failure;
  every other rejection, surface/payload mismatch or identity mismatch maps to
  `EVIDENCE_INVALID`. No raw result, reason, exception, command, path or oracle
  state enters a port return.
- Exact plugin/marketplace remove payload identity yields the matching manifest-
  bound removal proof. Exact admitted plugin/marketplace lists return E3D's
  recursively rebuilt payload without filtering, deduplication or caller
  identity reuse. Exact admitted `OracleAbsent` yields the manifest-bound
  installed-path absence proof. No other value can manufacture success.
- The adapter methods must remain exact plain one-request instance methods so
  `admit_codex_compensation_port` admits all five without descriptor/dynamic
  lookup. No broad catch, `Any`, `type: ignore`, optional/`None` effect port,
  historical-source copy or duplicate request/response validator is permitted.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `A1` | First red is the missing adapter module. Factory admission accepts one exact live lease/oracle/request and the existing port factory admits exactly five operations; invalid lease/oracle/request/root returns finite metadata without an oracle call. |
| `A2` | Raw, null, container, subclass, recursively malformed, constructed-invalid, injected and foreign-manifest requests return the matching manifest-bound `REQUEST_INVALID` operation failure before the oracle call count changes. |
| `A3` | Exact plugin removal issues only `PLUGIN_REMOVE`; exact rebuilt payload identity returns a new `CodexPluginRemovalProof`. Wrong surface/payload/identity, malformed/blocked result returns only the matching finite failure. |
| `A4` | Exact marketplace removal applies the same one-action, exact-identity and finite-failure rules and returns only a new `CodexMarketplaceRemovalProof`. |
| `A5` | Exact plugin and marketplace list calls each issue only their named action and return E3D-rebuilt equal data without caller identity; duplicate and foreign entries remain unchanged. Invalid evidence never becomes an empty-list success. |
| `A6` | Exact `ABSENCE` plus admitted `OracleAbsent` returns only a new manifest-bound `CodexInstalledPathAbsenceProof(absent=True)`; completed/wrong/blocked/malformed evidence cannot prove absence. |
| `A7` | One exact `CodexLifecycleOracle` instance under deterministic class-level test substitution drives the five adapter calls in memory. The test proves fixed action order/count, rebuilt list preservation and terminal absence without process/filesystem/runtime allocation. The later E5 acceptance ticket exclusively owns the real project-owned disposable-runtime lifecycle. |
| `A8` | Independently reverse request-before-effect, action binding, removal identity, response admission and absence gate. Each named test turns red and exact bytes restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## Exact source and return

Writable implementation paths only:

1. `tests/staging/codex_lifecycle_oracle/compensation_adapter.py`
2. `tests/test_codex_compensation_oracle_adapter.py`

Return one implementation commit over exactly those paths, then one unique
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260814-350`.
No numeric line limit is an acceptance criterion.

No registration adapter/source, integrated port/composition/reducer,
environment/oracle implementation, live Codex, host/network/target-project,
other Agent, review/integration, staging publication, push, package, release or
deployment action is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `3a624854-bf2f-4aa8-9b04-5f73e9ab2a28` / `CLOSURE-LOCAL-INSTALL-T05B4B2E3-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2e3_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2e3_20260814` / `rcpt_local_orchestration_install_05b4b2e3_20260814` |
| Correlation / question | `corr-local-orchestration-install-05b4b2e3-20260814` / `q-local-orchestration-install-05b4b2e3-20260814` |
| Side context | `scx-local-orchestration-install-05b4b2e3-20260814-01` |
| Owner / lane | Existing task `019ffb0c-db88-7303-895c-aecfadde7c8d`; permanent owner2 worktree; create only `codex/implementation-codex-compensation-oracle-adapter-05b4b2e3` from the later exact dispatch registry commit. |

Freeze is not dispatch. Exact clean lane/readback, target-branch absence and a
second control commit carrying the dispatch registry are required before the
owner may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze / authority | Freeze `903b70f9dbdbcbfbc6037e4fcd1a808bb6f388d1`; project-owner standing auto-continue under `PRG-20260809-042`; this control commit is the reviewed dispatch handoff. |
| Exact lane readback | Permanent owner2 top-level and linked git-dir match; idle task `019ffb0c-db88-7303-895c-aecfadde7c8d`; clean branch `codex/implementation-codex-oracle-response-admission-05b4b2e3d` at `5fa24b5acceacf98cf101a0126e03388fa70e659`; zero tracked/ignored residue; exactly three worktrees; target branch absent. |
| Branch admission | From the clean owner2 worktree, create only `codex/implementation-codex-compensation-oracle-adapter-05b4b2e3` at the exact commit carrying this registry. Do not merge/copy/reuse E3D source as a baseline, create another worktree or alter another lane. |
| Binding | Workspace `wsb_local_orchestration_install_05b4b2e3_20260814_01`; handoff `hnd_local_orchestration_install_05b4b2e3_20260814`; allocation `aln_local_orchestration_install_05b4b2e3_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e3_20260814`; correlation `corr-local-orchestration-install-05b4b2e3-20260814`; question `q-local-orchestration-install-05b4b2e3-20260814`; side context `scx-local-orchestration-install-05b4b2e3-20260814-01`. |
| Writable return | Exactly the two frozen new paths, one implementation commit, then only PRG-350 in one WPR-only handoff commit. |

This one-use receipt authorizes only E3 A1-A8 on the exact owner2 task/worktree.
The owner cannot orchestrate another Agent, issue a review decision, dispatch a
next ticket or perform push/package/install/staging/release/deployment work.

## Same-closure scope correction

`TICKET_DEFECT / NON_HIGH_RISK`: the first dispatch wording assigned a real
disposable-runtime lifecycle to A7 even though E5 already owns that acceptance.
A7 is narrowed to deterministic in-memory orchestration around one exact oracle
instance; E5 retains all physical runtime/process/filesystem lifecycle proof.
Closure, owner, worktree, branch, allocation, receipt, correlation and the two
writable paths remain unchanged. The later WPR handoff number is moved from the
unused PRG-348 reservation to PRG-350 after this control record.
