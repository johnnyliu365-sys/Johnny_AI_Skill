# 05B3A — Codex Safe Compensation Port Capability

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-07 effect-boundary seam |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3A-02` / R1-R4 |
| Dependency | Integrated 05B1/05B2 at control baseline; ADR-20260811-004 |
| Control / implementation / reviewer | Current `main` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` / independent current `main` reviewer |
| Worktree / branch | Existing `workflow-implementation` / existing `codex/implementation-codex-safe-port-capability-05b3a`; additive correction only |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Given an untrusted adapter candidate, return either one frozen, fully typed
five-operation compensation capability or a finite `INVALID_PORT` rejection
without reading a dynamic descriptor, invoking an operation, running a command
or touching a filesystem. This ticket does not plan compensation, reduce
authority or execute a capability.

## Exact source boundary

Only these new paths may change:

1. `library/local_orchestration/codex_compensation_port.py`
2. `tests/test_codex_compensation_port.py`

All existing source/tests and root exports are read-only. The terminal 05B3
branch is evidence only: no copy, cherry-pick, import or source reuse.

## Public contract and architecture

- The sole dynamic entry is `admit_codex_compensation_port(candidate: object)`;
  `object` is validated immediately and never crosses the returned boundary.
- The result is a discriminated union of a frozen
  `CodexCompensationPortCapability` and a finite rejection with public status
  `INVALID_PORT` plus one unique internal reason.
- The five required names are `remove_plugin`, `remove_marketplace`,
  `list_plugins`, `list_marketplaces` and `prove_installed_path_absent`. Each
  must resolve in the concrete class MRO to an ordinary `FunctionType`
  instance method. Static/class methods, properties, custom descriptors,
  per-instance callable objects, built-ins and variadic or wrong-arity
  functions reject; unrelated class members do not affect admission.
- Lookup must bypass caller descriptors and equality: obtain the concrete class
  only with built-in `type(candidate)`. Capture the trusted `__mro__` and
  `__dict__` getset descriptors from immutable built-in `type.__dict__`, then
  invoke those raw descriptors to obtain the real MRO and raw class mappings.
  Do not use `object.__getattribute__` or `type.__getattribute__` for
  caller-owned class metadata. Built-in candidate exclusions and all exact
  class checks use identity (`is`) only. Runtime arity uses safe code/default
  metadata of the raw function only. Calling `inspect.signature()` or
  following `__signature__` / `__wrapped__` on caller-controlled data is
  forbidden.
- Raw functions are bound explicitly into the exact frozen capability. The
  factory never dynamically gets a candidate member and never calls one.
- Strong request/manifest and five operation return contracts are defined here
  for later 05B3C use; no raw output, exception text, receipt, absolute path or
  registration success enters admission results.

## Acceptance Closure Set — revision 02

| ID | Finite completion rule |
| --- | --- |
| `R1` | Replace the unsafe revision-01 primitives exactly as specified above. A valid plain-method adapter returns one frozen five-operation capability, while admission reads no caller descriptor, invokes no caller equality/operation and produces only metadata. |
| `R2` | Cross candidate `__class__`, metaclass `__mro__`, metaclass `__dict__` and metaclass `__eq__` traps with `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit`: all 16 cells remain unread and admission completes finitely. Preserve the revision-01 instance/member/callable trap table and all invalid-shape cells. |
| `R3` | Preserve every passing revision-01 A1-A5 behavior: exact five-name/arity admission, frozen typed binding, null/text/container rejection, unrelated-member neutrality, metadata-only serialization and propagation only from an explicitly invoked admitted operation. |
| `R4` | Independently reverse (a) candidate class acquisition to `object.__getattribute__`, (b) MRO or class-dictionary acquisition to `type.__getattribute__`, (c) an exact class identity check to equality/membership, (d) code-metadata arity to `inspect.signature`, and (e) one descriptor rejection to admission. Each isolated reverse must turn its named test red and be restored. |

## TDD design and CodeReview.md §2.1 mapping

- **Null/empty/container (class 2):** `None`, `''`, whitespace, tuple, list and
  dict all reject with zero observable reads/calls.
- **Error-code consistency (class 5):** table every A2 shape to fixed public
  `INVALID_PORT` and one finite internal reason; no exception text.
- **Exception propagation (class 6):** all four process/control traps cannot be
  reached during admission; the same four exceptions from an explicitly
  invoked valid bound operation propagate.
- **Path/token classes (1/4):** not applicable; this ticket accepts no path,
  URI, credential or token.
- **Authority bypass (class 3):** direct use of an unadmitted candidate is not
  part of the public capability API; copied/malformed capability construction
  cannot be accepted as an admission result.
- **Truthfulness (class 7 / CR):** the five independent R4 reversals are
  mandatory; the handoff must name each red test and restoration.

First red must be captured before production source exists. Focused/full
unittest, strict full-tree mypy with a removed external cache, in-memory
compile, source/diff/scope and zero-residue checks are required. One
implementation commit is followed by one WPR-only handoff commit. No live
Codex, target-project write, network, Secret, integration, push, release or
deployment is authorized.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3A-02` |
| Correction handoff | `hnd_local_orchestration_install_05b3a_r02_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b3a_20260811` / `rcpt_local_orchestration_install_05b3a_20260811` |
| Correlation / question | `corr-local-orchestration-install-05b3a-r02-20260812` / `q-local-orchestration-install-05b3a-r02-20260812` |
| Side context | `scx-local-orchestration-install-05b3a-20260812-02` |
| Authority | Owner instruction to continue parallel implementation; ADR-20260811-004 revision 02; review `14fda317538f6661573cf687468f5291ced84ff7` |
| Lane admission | Exact clean submitted HEAD `0275daf172ca3536f7ab6b9fff880bb54478d9af` on the existing branch/worktree. Do not create/switch/reset/rebase/merge/cherry-pick a branch or worktree. |
| Return | One additive exact-scope correction commit, then one `doc/WorkProgressReport.md`-only handoff reserved as unique `PRG-20260812-176`. |

## Initial review record

Review of implementation `1c3739d305e83c97dd1be723240456cb954ea6cd`
and handoff `0275daf172ca3536f7ab6b9fff880bb54478d9af` is
`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-137 through CR-139 are the
complete initial blocking batch. Revision 01 incorrectly prescribed lookup
primitives that still execute candidate/metaclass data descriptors; the
implementation also invokes caller metaclass equality and the committed
evidence omits those paths. Revision 02 above is the complete correction
contract for CR-137 through CR-139. No unrelated hardening, integration or
05B3C work is authorized.

## Revision 02 review record

Correction `a87af389835f481882dc9e18e69177e8d156278a` and docs-only handoff
`0378655864e4277d553558a40d5122702aa3d7d9` are `APPROVED /
READY_TO_MERGE`. Independent verification passed focused 6/6, full 236/236,
strict mypy and compile over 112 files, all 16 trap cells and all five isolated
R4 reversals. CR-137 through CR-139 are closed; no 05B3C dispatch occurs before
guarded integration and the 05B3B dependency is resolved.
