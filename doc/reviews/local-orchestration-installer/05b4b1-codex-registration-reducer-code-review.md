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
