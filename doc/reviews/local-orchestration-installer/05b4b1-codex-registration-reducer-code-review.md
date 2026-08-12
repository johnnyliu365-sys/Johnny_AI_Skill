# Ticket 05B4B1 Codex Registration Reducer Code Review

## Review decision

`CHANGES_REQUESTED / TICKET_DEFECT / CONVERGENCE_REVIEW_REQUIRED`

The submitted reducer passes its focused and full suites, strict typing,
compile, scope and residue gates, but closure D6 is not satisfied. An exact
pending state remains valid after a successful advance, so the same stale
state/result pair can be accepted repeatedly.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / owner | `05b4b1-codex-registration-reducer`; task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; branch `codex/implementation-codex-registration-reducer-05b4b1` |
| Dispatch baseline | `1ca86f73a63f4c4494508b7c6ea1beb6248e7404` |
| Implementation | `2eb2264e97d4e41f529a8c232da6a2552e78c619`; exactly the new reducer and focused test |
| Docs-only handoff | `658a8f7e10d955b10a28eeb89133ec7c6b3e05a2`; only `doc/WorkProgressReport.md`, unique PRG-20260812-206 |
| Binding | `hnd_local_orchestration_install_05b4b1_20260812`; `aln_local_orchestration_install_05b4b1_20260812`; `rcpt_local_orchestration_install_05b4b1_20260812`; `corr-local-orchestration-install-05b4b1-20260812` |

## CodeReview.md verification

| Gate | Result |
| --- | --- |
| Exact ancestry / scope | PASS: `1ca86f7 -> 2eb2264 -> 658a8f7`; implementation changes exactly the two authorized paths and handoff changes WPR only. Submitted lane is clean and the three-worktree topology is unchanged. |
| D1-D5 functional matrix | PASS: exact first-red evidence is consistent with the additive diff. Fresh, marketplace and plugin matrices preserve the declared ownership, proof-request and compensation-plan outcomes without executing a port or effect. |
| D6 state authority | **FAIL — CR-148 / TICKET_DEFECT:** `_has_current_authority` validates only the permanent private authority reference and `id(state)`. `advance_codex_registration` never consumes or invalidates an accepted state. An independent probe advanced one exact fresh state twice; both calls returned `CodexMarketplaceAddPending`, and the assertion that the second call must be `CodexRegistrationBlocked` failed. The same replay succeeds for marketplace and plugin pending states. |
| D6 copy / shape guards | PASS within the submitted boundary: shallow copy, deep copy, Pydantic copy and serialized reconstruction block; nested malformed/trap values block without invoking traps. These checks do not close stale replay of the original authorized object. |
| Focused / regression | PASS on an immutable ZIP export: focused 10/10 and serial full discovery 279/279. |
| Strict type / compile | PASS: `mypy --strict --explicit-package-bases --no-incremental` and in-memory compile passed all 120 Python files. |
| Source / effect boundary | PASS: no port operation, receipt, final success, `Any`, `type: ignore`, dynamic member/signature lookup, historical-source reuse or live Codex/host/filesystem/target-project/network effect was added or run. |
| Diff / residue | PASS: exact commit scopes, source/test blobs, `git diff --check`, submitted-lane tracked/ignored/cache readbacks and worktree topology are clean. Review execution stayed in a repository-external immutable export. |

## Finding disposition

CR-148 is `TICKET_DEFECT`, not a bounded implementation correction. D6 requires
the reducer to reject a previously consumed stale state, while the frozen
design also requires a pure reducer whose public inputs contain no current
generation, lease, owner registry or other authoritative consumption fact.
For identical `(state, result)` inputs, that design has no fact with which to
distinguish the first call from replay. Adding a hidden mutable consumption
registry would change the declared pure lifecycle and introduce concurrency,
cleanup and ownership requirements; treating it as a small source patch would
silently change the ticket.

The recommended refreeze keeps 05B4B1 deterministic and moves single-use
phase/attempt replay protection into 05B4B2's exact transaction coordinator,
where current generation and effect ownership already belong. D6 should then
retain cross-phase, terminal, copied and constructed-state rejection here, and
give stale/current-generation rejection an explicit B2 closure. The alternative
is to refreeze B1 as a stateful single-use authority service with explicit
concurrency and cleanup semantics; it must not remain described as pure.

## Terminal disposition

Per the ticket stop rule, this review is terminal for revision 01. Do not merge
`658a8f7e10d955b10a28eeb89133ec7c6b3e05a2`, do not dispatch 05B4B2 and do not
open a correction branch or worktree. The immutable implementation and handoff
remain evidence. Further work requires control-plane convergence and a reviewed
ticket refreeze; no push, release, deployment, live Codex mutation or target-
project write is authorized.

## Revision-02 review

### Decision

`CHANGES_REQUESTED / IMPLEMENTATION_DEFECT / SAME_CLOSURE_CORRECTION`

| Gate | Result |
| --- | --- |
| Reviewed return | Implementation correction `aa315b385cf994c5991d44810e4b3a9cceb87ca3`; WPR-only handoff `8ae77343ca455e51a6f3addbcc3e8f1aff29ed2a`; closure `CLOSURE-LOCAL-INSTALL-T05B4B1-02` |
| Ancestry / scope / residue | PASS: `658a8f7 -> aa315b3 -> 8ae7734`; implementation changes exactly reducer/test, handoff changes WPR only, submitted lane tracked/ignored/cache readbacks are clean. |
| CR-148 / R2-D1 through R2-D5 | PASS: original, shallow copy, deep copy, exact dump reconstruction, JSON reconstruction and Pydantic deep copy all reduce to identical public decisions; repeated calls are deterministic; private identity authority is absent and B1 remains effect-free. |
| Standard verification | PASS in repository-external immutable export: focused 13/13, serial full 282/282, strict mypy 120 files and in-memory compile 120 files. |
| Adversarial value/source boundary | PASS: three phases × five reconstruction variants, repeated exact calls, two nested malformed cells, public-data leakage sentinel and AST/source effect sentinel all pass. |
| Constructed-invalid pending status | **FAIL — CR-149 / IMPLEMENTATION_DEFECT:** removing `status` from each exact pending variant causes `advance_codex_registration` to raise `AttributeError` at direct status access instead of returning `CodexRegistrationBlocked(INVALID_STATE)`. |

CR-149 is a bounded implementation defect, not a ticket defect or requirement
change. R2-D6 already requires finite rejection for constructed-invalid pending
values. The same branch may add one three-variant first-red test and guard the
required status read before phase comparison. No new state authority, B2 logic,
branch, worktree or broader hardening is authorized.

## CR-149 final correction review

### Decision

`APPROVED / READY_TO_MERGE`

| Gate | Result |
| --- | --- |
| Reviewed return | Correction `64e9e0ae2dba88b4be98438eef3b0639a78d6601`; WPR-only handoff `918c9aff6333d46576a81c92390d2bdf0b0e9b31`; closure `CLOSURE-LOCAL-INSTALL-T05B4B1-02` |
| Ancestry / scope / residue | PASS: `8ae7734 -> 64e9e0a -> 918c9af`; correction changes exactly reducer/test, handoff changes WPR only, and the submitted lane is clean with unchanged three-worktree topology. |
| CR-149 | PASS: fresh, marketplace and plugin constructed-invalid pending values with `status` removed each return `CodexRegistrationBlocked(INVALID_STATE)` instead of raising. The correction adds no authority, port, callable or effect. |
| Independent standard verification | PASS in a repository-external immutable export: focused 14/14, serial full 283/283, strict mypy 120 files and in-memory compile 120 files. |
| Independent adversarial verification | PASS: three phases, five reconstruction forms, three repeated reductions, missing `status`, missing nested journal, public-data absence and AST/source effect-boundary probes all passed. |
| Evidence truthfulness | PASS: the new guard-bypass mutation restored all three `AttributeError` failures before exact restoration; the five retained revision-02 reversals were rerun by the implementation owner and remain represented by committed tests. |

CR-148 and CR-149 are closed. No blocking finding remains for revision 02.
Guarded integration of the exact reviewed handoff is authorized; 05B4B2 must
still be refrozen from the integrated baseline before any implementation
dispatch.

Guarded integration completed at `d7c59349b436d552f2fab457a297e2eac6958093`,
preserving this approval as first parent and reviewed handoff `918c9af` as
second parent. Product source/tests matched the reviewed handoff exactly; the
sole WPR conflict retained PRG-206 through PRG-214 once. Post-merge focused
14/14, full 283/283, strict mypy and compile over 120 files passed with zero
cache residue.
