# 05B4B2B — Codex Registration Forward Composition

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 forward-registration seam |
| State | `CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2B-01` / F1-F8 |
| Dependency | 05B4B2A independently approved and integrated by `494aaca201de5a6ee001233b03bccb41de21f7fa` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; one new ticket branch from the later dispatch-registry commit; no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

Create one forward-registration coordinator from an exact admitted 05B4A
capability. It owns a private integrated B2A transaction coordinator, begins
one request, atomically consumes each opaque lease before invoking exactly one
fresh-preflight, marketplace-add or plugin-add operation, and completes that
lease with the returned value. It returns only existing B2A next-ready,
terminal or finite blocked data. It never invokes proof, creates a receipt,
executes compensation or touches the lifecycle oracle.

## Frozen composition design

- Public factory `admit_codex_registration_forward(capability: object)` returns
  either one non-transferable `CodexRegistrationForwardCoordinator` or a
  metadata-only `FORWARD_BLOCKED / INVALID_PORT`. The coordinator exposes only
  `begin(value)`, `execute(lease)` and metadata-only `recovery(lease)`; it does
  not expose B2A `start` or `complete`.
- Admission accepts only the exact integrated
  `CodexRegistrationPortCapability`. Before any transaction state or effect it
  verifies exact safe metadata, exact `MethodType` operation fields, one common
  bound owner and exact raw functions by re-running the public 05B4A admission
  on that owner. The coordinator stores and later executes only this fresh
  rebuilt capability, never caller-substituted operation objects. Dynamic
  member lookup, descriptors, annotations, `inspect.signature`, equality,
  hashing, representation and caller serialization are forbidden.
- The forward coordinator privately creates and owns one
  `CodexRegistrationTransactionCoordinator`. `begin` delegates the exact input
  to B2A. `execute` first calls B2A `start`; any transaction block returns
  immediately with zero operation calls. Only an exact started pending variant
  dispatches: fresh to `fresh_preflight`, marketplace to `add_marketplace`, and
  plugin to `add_plugin`, always with the rebuilt pending request.
- B2A must record `STARTED` before the operation is invoked. Therefore a
  concurrent or re-entrant execution of the same lease returns the existing
  finite replay block and cannot invoke a second operation. A stale, foreign,
  wrong-phase, copied, metadata-only or fabricated lease likewise cannot reach
  an operation.
- A normally returned operation value is passed exactly once to B2A
  `complete`; only B1/B2A decides next-ready, proof-required,
  compensation-required or blocked terminal truth. Wrong, foreign and
  recursively malformed returns are not repaired by this composer. The
  capability's `prove` operation is never called.
- `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` raised by
  an admitted forward operation propagate unchanged. B2A remains `STARTED`, so
  retrying that lease cannot invoke the operation again; marketplace/plugin
  recovery exposes the existing exact conservative `MAY_EXIST` data. No broad
  catch, retry, clear or guessed completion is allowed.
- The coordinator is slotted, non-dataclass and refuses shallow/deep copy,
  pickle/reduce and public construction. Its public metadata and repr contain
  only finite status/count data and no bound operation, adapter, request,
  absolute path, raw output, Secret, receipt or authority token.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `F1` | First red imports the absent `codex_registration_forward` production module and fails with exact `ModuleNotFoundError`; production remains unchanged during that red. |
| `F2` | One exact integrated capability admits with zero operations and metadata-only output. Null/text/container/plain-object, forged-empty, invalid authority/status, substituted operation, cross-owner and non-`MethodType` cells return `INVALID_PORT` before transaction/effect or caller protocol invocation. Structural dataclass serialization, shallow/deep copy and pickle cannot export or retain operations or usable coordinator authority. |
| `F3` | One exact request advances fresh → marketplace → plugin at generations 1 → 2 → 3. Call order is exactly `fresh_preflight`, `add_marketplace`, `add_plugin`; each receives its exact rebuilt pending request; final plugin success returns the exact existing proof-required terminal decision. `prove` remains zero-call. |
| `F4` | For each of the three phases, a synchronized duplicate and a re-entrant execution prove B2A is `STARTED` before invocation: exactly one operation call occurs and every competing call returns finite `REPLAYED`. Stale, foreign-coordinator, wrong-phase, metadata and fabricated leases remain zero-call. |
| `F5` | Each operation's exact accepted/success and declared failure returns pass once through B2A/B1. Wrong type, wrong request/attempt/target/version/plugin identity/path/auth and recursively malformed returned envelopes terminate in the exact existing finite blocked/compensation data without invoking a later operation. Raw diagnostics never enter results. |
| `F6` | Cross all three forward operations with `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit`: all 12 exceptions propagate unchanged, the failing operation is called once, retry is replay-blocked, no later operation runs, and marketplace/plugin recovery reports only the current exact add as `MAY_EXIST`. |
| `F7` | Constructed-invalid begin/lease/capability fields, caller equality/hash/repr/descriptor traps and public metadata/repr are finite and trap-free before effect. Source contains no proof/receipt/compensation/oracle/process/filesystem/host/network/target-project effect, `Any`, `type: ignore`, broad catch, optional/`None` port, dynamic member/signature lookup or historical rejected-source reuse. XSS is `XSS_NOT_APPLICABLE` because no Browser/WebView/HTML/DOM/JavaScript context exists. |
| `F8` | Independently reverse (a) rebuilt-capability use, (b) start-before-effect ordering, (c) exact phase dispatch, (d) returned-value completion and (e) exception stop/replay/recovery. Each named committed test turns red and exact blobs are restored. Focused/full unittest, strict full-tree mypy with external no-incremental cache, in-memory compile, source/scope/diff/ancestry and tracked/ignored/cache readbacks pass. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_forward.py`.
2. New `tests/test_codex_registration_forward.py`.

All integrated source/tests and package exports remain read-only. Historical
rejected 05B source is immutable evidence only. No numeric line limit is an
acceptance criterion. Return one exact two-path implementation commit followed
by one `doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-226.

No new dependency, package export, other Agent, B2C-B2E/05C work, live Codex,
process, filesystem, host, target-project or network effect, review,
integration, push, release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2B-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2b_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2b_20260812` / `rcpt_local_orchestration_install_05b4b2b_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2b-20260812` / `q-local-orchestration-install-05b4b2b-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2b-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-registration-forward-05b4b2b` from the exact dispatch-registry commit in that same worktree. |
| Return | Exact two-path implementation commit, then WPR-only PRG-20260812-226. |

Freeze is not dispatch. The reviewed freeze commit and a later dispatch
registry must exist before the implementation lane may switch branch or edit.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `45afa50204bf8bb8dcdcfc0be0a45cf07bcf6da0`; this ticket; exact F1-F8; `XSS_NOT_APPLICABLE` |
| Delivery confirmation | Project-owner standing instruction `按照規範繼續工作`; applies to the next approved ticket after guarded integration |
| Lane admission | Idle clean task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; submitted 05B4B2A HEAD `e4841abfd8caf8e262fa451055da94f5acc754a8`; zero tracked/ignored/cache residue; unchanged three-worktree topology |
| Required branch | From this dispatch-registry commit, switch the existing worktree only to new branch `codex/implementation-codex-registration-forward-05b4b2b`; no new worktree, merge, rebase or cherry-pick |
| Authority | `hnd_local_orchestration_install_05b4b2b_20260812`; `aln_local_orchestration_install_05b4b2b_20260812`; `rcpt_local_orchestration_install_05b4b2b_20260812`; `corr-local-orchestration-install-05b4b2b-20260812`; `q-local-orchestration-install-05b4b2b-20260812`; `scx-local-orchestration-install-05b4b2b-20260812-01` |
| Required return | One exact two-path implementation commit satisfying F1-F8, followed by one WPR-only handoff at reserved PRG-20260812-226 |

Any mismatch returns typed `HALT` or `CHANGE_DETECTED`. No second worktree,
source path, ticket, Agent, proof/receipt/compensation/oracle effect, review,
integration, push, release or deployment is admitted.

## Review correction record

Independent review of immutable return `b6349d5 -> 031c2ff` found CR-151 and
CR-152, both `IMPLEMENTATION_DEFECT` inside existing F2/F7. CR-151 requires the
same exact coordinator-authority gate before `begin`, `execute` and `recovery`
can mutate transaction state or invoke an operation. CR-152 requires
`__reduce_ex__` to reject without inspecting or converting its caller-supplied
protocol. The same ticket, owner, worktree, branch, allocation, receipt and
correlation remain valid; correction commits must be additive.

### Correction dispatch registry

| Field | Value |
| --- | --- |
| Control review | `cd26d22970409a5a066943e2301b16a58b7f267e`; CR-151 and CR-152; same F2/F7 closure |
| Correction handoff | `hnd_local_orchestration_install_05b4b2b_cr151_cr152_20260812` |
| Retained authority | `aln_local_orchestration_install_05b4b2b_20260812`; `rcpt_local_orchestration_install_05b4b2b_20260812`; `corr-local-orchestration-install-05b4b2b-20260812`; `scx-local-orchestration-install-05b4b2b-20260812-01` |
| Lane | Same task, existing `workflow-implementer-2`, existing `codex/implementation-codex-registration-forward-05b4b2b`, exact clean submitted HEAD `031c2ff0585b59510d1ee5746fd9acc60a837eaf`; additive commits only |
| Correction return | Existing forward module/test only, then WPR-only handoff reserved as PRG-20260812-229 |

No reset, amend, rebase, merge, new branch/worktree, public API change or
out-of-scope hardening is admitted by this correction registry.
