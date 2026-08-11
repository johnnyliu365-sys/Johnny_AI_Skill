# 05B2 — Codex Mutation Command-Attempt Classification

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 registration seam |
| Parent evidence | Terminal 05B review `24227ac`, especially CR-99/CR-103; rejected parent source remains historical evidence only |
| State | `COMPLETE / APPROVED / INTEGRATED` |
| Dependency | 05B1 independently approved and integrated by `bbc7de5` / `b2525ec` |
| Implementation owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation` worktree and branch only |
| Acceptance owner | Independent control-plane reviewer; no implementation writes |
| Language | Python 3.11, strict Pydantic and mypy |

## One outcome

Provide one pure production classifier that converts exact Codex marketplace-
add or plugin-add command-start truth into a recursively validated 05B1
current-attempt journal transition. A failure proved to occur before child
start grants no new removal authority. A started but failed or untrusted result
grants only `MAY_EXIST`. Only an exact confirmed add grants `OWNED`; marketplace
`already_added=true` becomes `PREEXISTING` and grants none.

This ticket performs no command, process, parse, filesystem, registration,
removal, list, absence, compensation, receipt, live Codex, target-project or
network effect. It does not compose the final transaction.

## Exact source boundary

Only these paths may change:

1. `library/local_orchestration/codex_command_attempts.py` — new strict
   observation and transition contracts plus pure classifier.
2. `tests/test_codex_command_attempts.py` — new finite TDD matrix.
3. `library/local_orchestration/__init__.py` — export only the new public
   contract surface.

Integrated 05B1 source is read-only and must be consumed, not duplicated.
05S2 is test-owned staging evidence and must not be imported by production.
Rejected Ticket-05/05B source may be inspected only through formal findings;
it may not be copied, cherry-picked or imported. No numeric line target is an
acceptance criterion.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05B2-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `C1` — finite command-start truth | Use distinct frozen models, not nullable fields or a generic action string: pre-start failure is exactly `EXECUTABLE_UNAVAILABLE`, `ACCESS_DENIED` or `GENERIC_LAUNCH_FAILURE` with `NOT_STARTED`; attempted/ambiguous failure is exactly `TIMEOUT_AFTER_START`, `NONZERO_EXIT`, `WAIT_FAILED_AFTER_START`, `TERMINATION_FAILED`, `MALFORMED_RESPONSE` or `IDENTITY_MISMATCH` with `STARTED`; confirmed marketplace add carries strict `already_added`; confirmed plugin add has its own model. Marketplace and plugin command targets are named finite values. Missing, extra, null, blank, container, wrong enum/literal and constructed shapes fail recursive validation. |
| `C2` — exact transition admission | Revalidate the supplied 05B1 journal against the exact `CodexPreflightRequest` and `CodexRegistrationAttemptId` before classification. Marketplace add is admissible only from `(NOT_ATTEMPTED, NOT_ATTEMPTED)`; plugin add only from `(OWNED, NOT_ATTEMPTED)`. Every other command/current-journal pair returns finite `INVALID_SEQUENCE` and no journal. Malformed, replayed or cross-request journal inputs retain distinct finite rejection reasons. |
| `C3` — authority-preserving transition | All three pre-start reasons leave the admitted journal byte/value-equivalent and grant no new authority. Every attempted/ambiguous reason changes only the target effect to `MAY_EXIST`. Confirmed fresh marketplace becomes `(OWNED, NOT_ATTEMPTED)`; confirmed pre-existing marketplace becomes `(PREEXISTING, NOT_ATTEMPTED)`; confirmed plugin becomes `(OWNED, OWNED)`. Every emitted journal is recursively reconstructed through the integrated 05B1 legal matrix; `PREEXISTING`/`NOT_ATTEMPTED` never gain removal authority. |
| `C4` — no manufactured final authority | The classifier emits only a 05B1 journal or a finite classification rejection. It cannot emit a registration receipt, compensation result or success status, and stores no raw command, stdout/stderr, absolute path or exception text. Later 05B4 must supply observations from its exact injected execution boundary; this ticket does not claim that a caller-created observation proves a real host effect. Known validation failures map finitely; unexpected `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` propagate rather than being broadly caught. |

## Required TDD and review matrix

| Cell | Exact assertion |
| --- | --- |
| `T1 / C1` | Table every finite observation member and all missing/extra/null/blank/container/wrong-literal/constructed cells. Assert pre-start and started literals cannot be swapped. |
| `T2 / C2` | Cross product both command targets with all seven legal 05B1 journal pairs: only the two named admission pairs succeed; the other twelve reject. Add malformed, cross-request and replayed-attempt cases with distinct reasons. |
| `T3 / C3` | Table all three pre-start reasons, all six ambiguous reasons and all three confirmations. Assert exact before/after pair and `unresolved_removal_order()` for every row; pre-start input stays value-equivalent and zero-authority where applicable. |
| `T4 / C4` | Assert result unions contain no receipt/final-success/raw-output/path/exception field. Inject known malformed observation plus unexpected/process-control failures and assert the frozen finite-versus-propagating behavior. Reverse independently: treat access denied as attempted, leave one started failure unchanged, and map marketplace `already_added=true` to owned; each target test must red, then restore. |

CodeReview.md classes 2, 3, 5, 6 and 7 apply. Path-prefix and token
classes are not applicable because this ticket accepts no path or credential.
No `Any`, `type: ignore`, optional/`None` effect port, raw dict contract,
generic action string, broad catch/clear, caller-synthesized final success or
compressed multi-statement production line is allowed.

## Verification, non-goals and return

Run focused/full unittest, strict full-tree mypy with a validated external
cache removed afterward, in-memory compile, source/scope/diff and
tracked/ignored zero-residue readback. Record truthful first-red/green and the
three isolated reverse mutations.

Return one implementation commit containing exactly the three authorized
paths, then one docs-only commit changing only `doc/WorkProgressReport.md`.
The implementation owner works alone and makes no review, integration,
downstream dispatch or Agent-control decision. No new branch/worktree, reset,
rebase, amend, force, merge, cherry-pick, stash, push, release or deployment.

## Same-closure correction handoff — CR-133 and CR-134

The initial independent review at
`4aa85e6900da974e92e51cdc6b66c80b5b550707` found the complete blocking
batch for `CLOSURE-LOCAL-INSTALL-T05B2-01`. C2-C4 and their reverse
mutations are closed; this correction may change only C1/T1 behavior and
evidence:

1. Every field declared by all four observation models is required at their
   validation boundary. Removing any one target, reason, start-state or
   `already_added` field must raise validation failure; a fixed literal must
   be supplied and checked, not manufactured by a default.
2. Recursive observation validation must preserve strict Python enum/literal
   types. A `model_construct` object containing correctly spelled raw strings
   for enum/literal fields must return finite `INVALID_OBSERVATION`; JSON
   round-trip coercion may not upgrade those strings into trusted members.
3. Commit a four-model table that removes every field one at a time, plus
   null, blank, container, wrong nonblank literal, swapped start-state/target
   and constructed raw-string cells. Each accepted cell named in CR-133 must
   be captured red before the correction and green afterward.
4. Preserve all C2-C4 behavior, public result algebra, no-effect boundary and
   the three existing reverse-mutation protections exactly.

This is the one permitted same-closure correction. It stays on task
`019fcc9c-f34f-7d53-a313-c70c90bf3245`, the existing
`workflow-implementation` worktree and branch
`codex/implementation-codex-protocol-fixture-05s3`, starting at exact clean
HEAD `d3bb4ade4f420e2a2bb38b779db0263d0a90f10a`. Preserve allocation
`aln_local_orchestration_install_05b2_20260811` and receipt
`rcpt_local_orchestration_install_05b2_20260811`; correction handoff
`hnd_local_orchestration_install_05b2_r01_20260811`, correlation
`corr-local-orchestration-install-05b2-r01-20260811`, question
`q-local-orchestration-install-05b2-r01-20260811` and side-context
`scx-local-orchestration-install-05b2-20260811-02` are exact. Return one
additive three-path implementation commit, then a WPR-only handoff using
unique `PRG-20260811-158`. A remaining blocker at final correction review
routes to `CONVERGENCE_REVIEW_REQUIRED`; no further implementation correction
is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / ticket | `prj-local-orchestration-installer-poc-20260808` / `05b2-codex-command-attempt-classification` |
| Handoff | `hnd_local_orchestration_install_05b2_20260811` |
| Allocation / receipt | `aln_local_orchestration_install_05b2_20260811` / `rcpt_local_orchestration_install_05b2_20260811` |
| Correlation / question | `corr-local-orchestration-install-05b2-20260811` / `q-local-orchestration-install-05b2-20260811` |
| Side context | `scx-local-orchestration-install-05b2-20260811-01` |
| Authority | Owner instruction to continue under the approved workflow; program authority `PRG-20260809-042`; integrated dependency `b2525ec` |
| Ticket-doc baseline | `c6ba7713160f04b56a4982fd6dae4d1d4d34f026` |
| Expected lane admission | Existing branch `codex/implementation-codex-protocol-fixture-05s3` at exact clean HEAD `1df30ae6ed9a87b4b9fe35b64ea09ccc107cccee`, then normal `--ff-only` to the reviewed handoff commit. |
