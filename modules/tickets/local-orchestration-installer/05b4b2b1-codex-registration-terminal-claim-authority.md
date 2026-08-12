# 05B4B2B1 — Codex Registration Settlement Claim Authority

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 settlement seam |
| State | `CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2B1-01` / C1-C8 |
| Dependency | 05B4B2B independently approved and integrated by `63e8a7b6825f1807b5810007edcc10744149182d` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; one new branch in the same worktree, no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

Wrap one exact factory-admitted B2B forward coordinator. Proxy its existing
begin, execute and recovery behavior without changing forward semantics,
except that an exact terminal proof-required decision becomes one proof claim,
and an exact terminal compensation-required decision or started-add recovery
becomes one compensation claim. Each process-local claim is non-transferable;
the matching admission consumes it exactly once and returns only a rebuilt
existing decision/recovery DTO. This ticket invokes no settlement effect.

## Frozen authority design

- Public `admit_codex_registration_settlement_authority(candidate: object)`
  accepts only an exact integrated B2B coordinator whose safe metadata proves
  live factory provenance. Invalid/null/container/trap/unregistered clones
  return metadata-only `SETTLEMENT_AUTHORITY_BLOCKED` before state or effect.
- Public coordinator construction rejects. Factory registration is
  closure-owned, synchronized, identity-only and weakly bounded under the
  ordinary-module threat boundary approved for CR-154. Module globals expose
  no mutable registry, insertion-ready record or arbitrary register callable.
- `begin` delegates to the exact stored B2B coordinator. `execute` delegates
  once. Ready/next-ready/transaction blocks and operation exceptions remain
  unchanged. Exact terminal proof/compensation decisions are intercepted;
  terminal blocked data creates no claim. `recovery` delegates once and turns
  only an exact `CodexRegistrationAddRecovery` into a compensation claim;
  blocked recovery remains unchanged.
- A claim is slotted, immutable, non-dataclass and rejects public construction,
  copy, deepcopy, pickle/reduce and structural serialization. Its metadata has
  only status, attempt ID, terminal phase, generation and claim kind—no request,
  plan, operation, path, receipt, Secret or token.
- `consume_codex_registration_proof_claim(value: object)` and
  `consume_codex_registration_compensation_claim(value: object)` atomically
  consume only the exact matching live claim. Proof consumption returns one
  recursively rebuilt `CodexRegistrationProofRequired`; compensation
  consumption returns one recursively rebuilt
  `CodexRegistrationCompensationRequired` or
  `CodexRegistrationAddRecovery`. Wrong kind, clone, metadata,
  stale/foreign/replayed claim returns finite `INVALID_CLAIM` before
  state/effect.
- The returned DTO is data, not reusable authority. Later B2C/B2D must consume
  the live claim inside their own single effect entry; they may not accept raw
  proof/compensation decision or add-recovery data as authority.
- The enforced boundary is untrusted object fabrication plus ordinary module
  attributes. Debugger, monkeypatch, closure-cell and arbitrary interpreter
  compromise remain trusted-runtime concerns outside this ticket.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `C1` | First red imports absent `codex_registration_settlement_authority` and fails with exact `ModuleNotFoundError`; production remains absent during red. |
| `C2` | Exact live B2B admission succeeds with zero operation calls. Invalid/null/container/trap/unregistered clones block before caller protocol, transaction or effect. Public construction and module-global registration injection are unavailable. |
| `C3` | Wrapper fresh/marketplace results remain exact next-ready data. Plugin success yields one proof claim; declared/invalid plugin outcomes yield exact compensation or blocked branches. Exact started-add recovery yields one compensation claim; blocked recovery remains exact. Forward order/count and exception behavior are unchanged. |
| `C4` | Claims contain finite metadata only, reject transfer/fabrication and bind exact owner/attempt/phase/generation/kind without caller equality/hash/repr/serialization. A compensation claim binds exactly one terminal compensation decision or add-recovery DTO. |
| `C5` | Matching consumption returns one rebuilt exact proof decision, compensation decision or add-recovery DTO and atomically tombstones the claim. Replay, wrong-kind, cross-owner, metadata-only and fabricated claims return `INVALID_CLAIM`. |
| `C6` | Synchronized duplicate consumption yields exactly one admitted decision and one replay block. Dropping unreachable unconsumed state reclaims closure records without an unbounded strong-reference registry. |
| `C7` | Source invokes no proof, compensation port/composition, oracle, process, filesystem, host, network or target-project effect; adds no `Any`, `type: ignore`, broad catch, optional/`None` port, dynamic lookup/signature or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `C8` | Independently reverse exact B2B provenance, terminal-kind classification, atomic tombstone, kind equality and closure ownership. Each named committed test turns red and exact blobs restore. Focused/full unittest, strict mypy, compile, scope/diff/ancestry and residue checks pass. |

## Exact source and return

1. New `library/local_orchestration/codex_registration_settlement_authority.py`.
2. New `tests/test_codex_registration_settlement_authority.py`.

All integrated source/tests and exports remain read-only. No numeric line limit
is an acceptance criterion. Return one exact two-path implementation commit,
then one `doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-242.

No B2C/B2D settlement effect, B2E/05C work, live Codex, process, filesystem,
host, network, target-project write, other Agent, review, integration, push,
release or deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2B1-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2b1_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2b1_20260812` / `rcpt_local_orchestration_install_05b4b2b1_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2b1-20260812` / `q-local-orchestration-install-05b4b2b1-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2b1-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-registration-terminal-claim-05b4b2b1` from the exact dispatch commit. |
| Return | Exact two-path implementation commit, then WPR-only PRG-20260812-242. |

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `594072f0bedead9d9f54553b31eed976b605ee02`; corrected C1-C8 including terminal and started-add recovery claims |
| Delivery authority | Project owner instruction `繼續 不要卡住`; `IMPLEMENTATION_DISPATCH_CONFIRMED` for this ticket only |
| Lane readback | Task is idle; existing `workflow-implementer-2` is clean at exact submitted HEAD `2fbe55f0cd8dc18788dd121ff1529d81d6b52409`; exactly three existing worktrees |
| Branch | Create only `codex/implementation-codex-registration-terminal-claim-05b4b2b1` from the exact dispatch-registry commit; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2b1_20260812`; `aln_local_orchestration_install_05b4b2b1_20260812`; `rcpt_local_orchestration_install_05b4b2b1_20260812`; `corr-local-orchestration-install-05b4b2b1-20260812`; `q-local-orchestration-install-05b4b2b1-20260812`; `scx-local-orchestration-install-05b4b2b1-20260812-01` |

### Path-scope correction continuation

The first implementation turn wrote one test to the similarly named but
unallocated `C:\Users\<user>\Desktop\AI控制工作\workflow-implementer-2` path.
The exact file was removed, the allocated worktree remained clean at the
dispatch baseline, and topology remained three worktrees. Resume this same
ticket/branch/allocation/receipt only after resolving the current Git top-level
to exact `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`. Every edit
path must be relative to that verified root; another mismatch is typed `HALT`.

This registry is the single dispatch. The implementation owner may work only
the exact two source/test paths and later the WPR-only PRG-20260812-242 return.

## Review correction record

Independent review of immutable return `a57dd0a -> ad2fc50` found CR-155, an
`IMPLEMENTATION_DEFECT` inside existing C4/C5. A live claim and its registry
record share one metadata object; in-place mutation preserves the current
identity check and the altered attempt/phase/generation binding is consumed.
The bounded correction must retain the same owner, worktree, branch,
allocation, receipt and correlation, add canonical authority-owned binding
comparison plus its named first-red/reversal, and use additive commits only.
