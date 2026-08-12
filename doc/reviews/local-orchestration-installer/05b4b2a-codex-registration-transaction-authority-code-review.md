# Ticket 05B4B2A Codex Registration Transaction Authority Code Review

## Review decision

`APPROVED / READY_TO_MERGE`

The immutable correction closes CR-150 without widening the ticket. Exact plain
metadata types are now established before comparison, hashing or registry
lookup, so constructed-invalid caller protocols return finite `INVALID_LEASE`
without invocation. All T1-T8 gates pass.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2a-codex-registration-transaction-authority`; `CLOSURE-LOCAL-INSTALL-T05B4B2A-01`; T1-T8 |
| Owner / branch | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; `codex/implementation-codex-registration-transaction-authority-05b4b2a` |
| Dispatch baseline | `73f3b8da12a513da5bfb26bcde4fa635423b0ba7` |
| Implementation | `6e05c8edfc1ed8db246052f3c19fd6a89539fdf3`; exactly the new transaction module and focused test |
| Docs-only handoff | `312005e6091e088b225e8c53d39480264f860e19`; only `doc/WorkProgressReport.md`, unique PRG-20260812-218 |
| Binding | `hnd_local_orchestration_install_05b4b2a_20260812`; `aln_local_orchestration_install_05b4b2a_20260812`; `rcpt_local_orchestration_install_05b4b2a_20260812`; `corr-local-orchestration-install-05b4b2a-20260812` |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| Ancestry / scope / residue | PASS: `73f3b8d -> 6e05c8e -> 312005e`; implementation adds exactly the two authorized paths, handoff changes WPR only, submitted lane is clean, and three-worktree topology is unchanged. |
| T1 first red | PASS: WPR records exact absent-module `ModuleNotFoundError` before production creation; the additive commit shape and task event sequence are consistent with the record. |
| T2 begin / duplicates | PASS: exact requests rebuild distinct B1 decision data; missing, null, empty, whitespace, container, plain trap and constructed-invalid inputs block without effects. Live and terminal attempt IDs remain duplicate-blocked. |
| T3 atomic start | PASS: synchronized duplicate start yields exactly one `STARTED` and one `REPLAYED`; the private per-coordinator `RLock` covers admission and `READY -> STARTED`. An independent rerun passed. |
| T4 completion | PASS: exact phases advance at generations 1, 2 and 3; stale, repeated, cross-phase and never-started completions block finitely. Exact proof and B1 blocked terminal outcomes are retained. An independent concurrent-complete probe yielded one next-ready result and one replay block. |
| T5 lease authority | **FAIL — CR-150 / IMPLEMENTATION_DEFECT:** `_admit_live_lease` compares `metadata.status != "PHASE_LEASE"` before proving an exact plain string and performs dictionary lookup using `metadata.attempt_id.value` before proving an exact plain string. A constructed-invalid status carrying `PlainTrap.__eq__` raises `RuntimeError("caller trap invoked")`; a constructed-invalid attempt value carrying `HashTrap.__hash__` raises `RuntimeError("hash trap")`. Both occur before finite `INVALID_LEASE`, violating T5's fabricated-input rule. Exact lease identity, owner, token, generation, phase, record identity, copy/deepcopy/pickle refusal and metadata reconstruction otherwise pass. |
| T6 recovery | PASS: fresh recovery grants no removal authority; started marketplace/plugin recovery binds exact request/attempt and marks only the current add `MAY_EXIST`. |
| T7 evidence truthfulness | PASS for the five frozen reversals: atomic exclusion, generation equality, coordinator identity, tombstone retention and conservative recovery each turned its named test red and were restored to the submitted blobs. CR-150 requires one additional bounded first-red regression within existing T5, not a new closure item. |
| T8 standard verification | PASS in a repository-external immutable ZIP export: focused 10/10, full serial 293/293, strict mypy 122 files, in-memory compile 122 files, source sentinel and diff/scope checks passed. |
| Clear/type/effect boundary | PASS: no broad clear, optional/`None` port, `Any`, `type: ignore`, broad catch, dynamic member/signature lookup, historical-source reuse, module-global registry, operation invocation or live host/target/network effect. |
| CodeReview §2.1 class 1 | PASS / applicable attempt-ID prefix boundary: case, valid-prefix-plus-extra and unrelated identifiers are tested and exact registry/lease identity prevents prefix authorization. No filesystem path routing is added. |
| CodeReview §2.1 class 3 | PASS except CR-150's finite-failure gap: all public transaction entry points reach the same private lease admission; metadata, forged and cross-coordinator paths cannot reach continuation. No alternate effect path exists in this ticket. |
| CodeReview §2.1 class 7 | PASS except the T5 gap identified by CR-150: committed assertions and the five reverse mutations verify their descriptions; the existing fabricated tests did not cover caller-defined status comparison or attempt-key hashing. |
| CodeReview §2.1 class 8 | `XSS_NOT_APPLICABLE`: the reviewed paths create no Browser, WebView, HTML/DOM renderer, JavaScript execution context, Native Bridge, IPC or Extension API. |

## CR-150 bounded correction

CR-150 is an `IMPLEMENTATION_DEFECT` under existing T5, not a ticket defect or
requirement change. In the same branch and allocation, add one focused test
whose constructed-invalid exact metadata carries (a) a status comparison trap
and (b) an attempt-ID value hashing trap. Both must return
`CodexRegistrationTransactionBlocked(INVALID_LEASE)` with zero trap invocation.
Then change admission ordering so exact built-in field types and finite values
are established before equality, hashing, serialization, representation or any
other caller-controlled protocol can run.

The correction must remain additive and change only the existing transaction
module, focused test and a later WPR-only handoff. It must rerun the affected
focused/full suites, strict full-tree mypy, compile, source sentinel and the T5
guard-bypass reverse mutation. No new branch/worktree, public contract, port,
effect, B2B-B2E/05C work, package, push, release or deployment is authorized.

## Final correction review

| Gate | Result |
| --- | --- |
| Immutable return | PASS: `312005e -> 4e6924b -> e4841ab`; correction changes only the existing transaction module/test and the handoff changes only `doc/WorkProgressReport.md` as PRG-20260812-221. |
| CR-150 behavior | PASS: exact `str`/closed value-object/`int` gates precede literal comparison, numeric ordering and dictionary lookup. Constructed-invalid status comparison and attempt-key hashing traps both return `INVALID_LEASE` with invocation count zero. |
| Independent verification | PASS: immutable ZIP export named CR-150 1/1, focused 11/11 and full 294/294; strict mypy and in-memory compile pass all 122 Python files. No `Any`, `type: ignore`, broad exception catch or residue is present. |
| Evidence truthfulness | PASS: the committed two-cell regression represents both original failures; the isolated guard-bypass reversal restored both caller `RuntimeError` failures and exact correction blobs were restored. Existing T1-T8 behavior remains green. |
| XSS review | `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript execution context or privileged JavaScript bridge/API is introduced. |

## Disposition

`APPROVED / READY_TO_MERGE`. CR-150 is closed. Guarded integration may merge
only exact handoff `e4841abfd8caf8e262fa451055da94f5acc754a8`, preserving this
review commit as first-parent control history and the submitted handoff as the
second parent. B2B-B2E remain unallocated until integration completes.
