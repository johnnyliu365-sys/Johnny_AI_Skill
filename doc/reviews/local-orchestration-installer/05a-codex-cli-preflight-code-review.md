# 05A Codex CLI Contract and Ownership Preflight - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05a-codex-cli-preflight-contract` |
| Result | `BLOCKED / SUPERSEDE_REQUIRED` after terminal owner-overridden review |
| Reviewer | Codex / current `main` worktree |
| Reviewed branch | `codex/implementation-codex-cli-preflight-05a` |
| Boundary | Baseline `d90b69e`; final implementation `97ab31c`; final docs-only handoff `4fc81a5`; terminal control baseline `83e34c3` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05A-01` / `A1..A5` |

## Independent verification

The implementation branch is a clean two-commit descendant of the exact
decomposition baseline. The implementation commit changes only the three
authorized production files and the one authorized test; the second commit is
docs-only. No rejected Ticket-05 implementation commit is an ancestor of this
branch, and no second worktree or concurrent child branch was created.

| Check | Result / evidence |
| --- | --- |
| Submitted green suite | PASS: focused unittest `9/9`; full discovery `165/165`; strict mypy `82` files; four-file in-memory compile; source sentinel; `git diff --check`. |
| Scope / ceiling | PASS: independent diff measurement is `164` added and `2` removed production non-blank lines, net `162 / 170`; the test is `128 / 180` non-blank lines. |
| Git isolation | PASS for the committed test: existing and empty temporary Git repositories compare non-`.git` bytes plus porcelain before and after a missing-executable probe. |
| Public CLI DTO probe | FAIL: the current official [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli) documents optional `marketplaceSource` on marketplace-list and plugin-list entries. Both documented shapes are rejected as `extra_forbidden`; the implementation instead declares an undocumented marketplace field named `source` and omits the plugin field. |
| Version probe | FAIL: arbitrary text `not-codex warning 9.9.9 trailing` is accepted as CLI version `9.9.9`; A1/A4 require the supported plain Codex version surface, not a semver substring in arbitrary output. |
| Canonical-source probe | FAIL: a recursively valid proof claiming canonical `root` but carrying `absolute_path=C:\\FOREIGN\\marketplaces\\probe-market` is constructed and the preflight returns `ELIGIBLE`. The absolute path is only suffix-matched and is not bound to `CANONICAL_INSTALL_ROOT`. |
| Collision probe | FAIL: a valid same-name plugin in the required `available` collection under another marketplace returns `ELIGIBLE`; only `installed` is examined. |
| Host safety | PASS for reviewer execution: all probes use recorded ports, invoke no mutation command, and do not access a target project, host configuration, network, login or Secret. The implementation worktree remained clean. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `A1` | FAIL | Required official optional `marketplaceSource` fields are rejected; unsupported arbitrary version text containing a semver is accepted. |
| `A2` | FAIL | Installation/root/locator objects are compared, but the resolved absolute proof path is not derived from or exactly bound to the canonical root. A foreign root with the exact suffix authorizes `ELIGIBLE`. |
| `A3` | FAIL | Marketplace and installed-plugin name collisions block, including case variants, but same-name entries in the required `available` collection do not. |
| `A4` | PASS | The independent and committed probes map missing executable, access denial, real `subprocess.TimeoutExpired`, invalid timeout, command/filesystem `OSError`, malformed output, invalid UTF-8 and unsupported no-version output to finite blocked results. |
| `A5` | FAIL | Green/type/compile/diff/Git claims reproduce, but the committed official fixtures omit `marketplaceSource`, the root/collision matrices omit the failing cells above, and the docs-only handoff falsely states that official DTOs and exact root proofs passed. No reproducible per-guard reverse-mutation commands/results are recorded. |

## CodeReview.md verification

| Required check | Result |
| --- | --- |
| Types and separation | FAIL. Strict named models and required typed ports exist, but the public boundary type is not the documented schema and the proof type permits contradictory root/path evidence. |
| Logic and edge cases | FAIL. Foreign-root authorization, ignored available-plugin collisions and broad version substring admission make reachable success states incorrect. |
| Test structure / smoke | FAIL closure despite green suite. Tests are isolated and readable, but omit the exact official optional-field, foreign-root-with-correct-suffix, available-collision and strict-version cells. |
| Dependencies / reusable source | PASS. No new dependency, broad framework or objective Git ancestry evidence of rejected-branch reuse was found. |
| UI / interaction | N/A. Ticket 05A has no UI surface. |
| Security / privacy | FAIL. A foreign filesystem path can be presented as installer-owned and authorize eligibility. No raw output, target-project data or Secret was persisted. |
| Logs / sensitive data | PASS. No logging or telemetry surface was added. |
| Legacy / dead logic | FAIL. The required `available` collection is parsed but discarded, while the undocumented marketplace `source` field is never needed by collision logic. |

## Batched findings

1. **CR-86 — `IMPLEMENTATION_DEFECT`, A1/A4.**
   `host_contracts.py:244-269` and `codex_cli_adapter.py:48-52` do not model the
   current public list/version boundary. Add one strict typed
   `marketplaceSource` value carrying the documented source type/value and use
   it as the optional field on both marketplace and plugin list entries; remove
   the undocumented marketplace `source`. Admit only the supported plain Codex
   version form and block arbitrary text containing a semver. Add official
   present/absent optional-field fixtures plus wrong-type/extra-field and strict
   version probes.
2. **CR-87 — `IMPLEMENTATION_DEFECT`, A2.**
   `host_contracts.py:291-302` proves only that `absolute_path` is syntactically
   absolute and ends with the relative locator. Bind the resolved proof path to
   the exact case-sensitive expansion of `CANONICAL_INSTALL_ROOT` plus the
   exact normalized locator, and reject foreign root, root-prefix/suffix,
   trailing separator, casing, encoded separator, traversal and nominally
   constructed variants before either list command.
3. **CR-88 — `IMPLEMENTATION_DEFECT`, A3.**
   `codex_cli_adapter.py:39-42` discards `CodexPluginList.available`. Collision
   eligibility must require the requested plugin name to be absent from both
   `installed` and `available`, including same-name entries under every other
   marketplace and case variants, without mutating either collection.
4. **CR-89 — `EVIDENCE_DEFECT`, A5.**
   `tests/test_codex_cli_preflight.py:82-136` and handoff `67dc1db` do not prove
   the frozen official DTO/root/collision matrix and overstate its green result.
   Add the missing cells above and record executable reverse mutations with the
   exact failing test names/reasons for schema admission, canonical-root
   matching, both collision collections and exception mapping. Preserve the
   existing first-red history as-is; do not invent retroactive red evidence.

## Conclusion and correction route

`CHANGES_REQUESTED`. This is the single initial review permitted by the 05A
convergence rule, and all findings are batched here. There is no
`REQUIREMENT_CHANGED`, unsafe worktree contamination or branch/baseline
conflict, so there is no `FRESH_BRANCH_REQUIRED` evidence. Keep the same ticket,
implementation task, worktree, branch, allocation and valid receipt. Exactly
one additive implementation correction and one following docs-only handoff are
permitted. The correction must remain within the frozen `170 / 180` cumulative
non-blank ceilings; if the complete A1..A5 closure cannot fit, return typed
`BLOCKED / TICKET_DEFECT` rather than compressing away a contract or expanding
scope. Ticket 05B, 05C, Ticket 04 and integration remain blocked.

## Correction review

### Correction boundary

The single permitted additive correction consists of implementation
`b6594b9f9acf1cd2d905b0614ddce23db268510c` and docs-only handoff
`59c3f96762d65cdc5e39f53cecffdea0428fbc16`, both descending from the original
handoff `67dc1db` on the same branch and worktree. The submitted worktree is
clean. No branch/worktree creation, merge, push, live Codex mutation or target
project access occurred.

### Independent correction verification

| Check | Result / evidence |
| --- | --- |
| Green suite | PASS: focused unittest `13/13`; full discovery `169/169`; strict mypy `82` files; in-memory compile; source sentinel; `git diff --check`. |
| Scope / ceiling | PASS: independent cumulative measurement is `169` added / `2` removed production non-blank lines, net `167 / 170`; test `158 / 180`. |
| CR-88 collision | CLOSED: the exact `plugin list --available --json` command is used and both `installed` and `available` participate in case-folded same-name collision blocking. |
| CR-86 null admission | FAIL: both official DTOs accept an explicitly present `marketplaceSource: null`, although A1 and CodeReview.md §2.1 class 2 require `None` to be rejected while permitting the optional field to be absent. An empty object is correctly rejected. |
| CR-86 parsed version | FAIL: `codex-cli 0.144.0-alpha.4` produces `CodexCliVersion.value == "codex-cli 0.144.0-alpha.4"`; the parser validates the product prefix but returns the full command text (`match.group(0)`) rather than the parsed semantic version capture. |
| CR-87 absolute canonical root | FAIL: with `LOCALAPPDATA=relative`, `CodexSourceProof.absolute_path="relative\\JohnnyAIWorkflow\\marketplaces\\probe-market"` constructs successfully and the preflight returns `ELIGIBLE`. Equality to the expanded macro is not proof that the expansion is an absolute Windows canonical root. |
| Evidence truth | FAIL: handoff `59c3f96` claims the optional and exact-root matrices are complete, but contains no explicit-null or non-absolute expansion cell and therefore overstates A1/A2/A5. |

### Corrected closure mapping

| Item | Result | Correction result |
| --- | --- | --- |
| `A1` | FAIL | Official present/absent object fixtures pass, but explicit JSON `null` is accepted and the typed version value retains the command prefix. |
| `A2` | FAIL | Normal-environment foreign/prefix/suffix/case/encoded/traversal probes block, but a relative expansion of the canonical macro authorizes a relative proof. |
| `A3` | PASS | Marketplace, installed-plugin and available-plugin collisions, including case variants and foreign marketplaces, block without mutation. |
| `A4` | PASS | Declared process/filesystem/timeout/encoding/malformed-output failures remain finite. |
| `A5` | FAIL | Green/type/compile/scope/Git and the submitted reverse probes reproduce, but the remaining A1/A2 cells make the evidence claim incomplete and false. |

### Correction conclusion

`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. CR-86, CR-87 and CR-89 are
not closed; CR-88 is closed. The explicit-null and relative-expansion failures
are direct cells of frozen A1/A2 and the correction made those exact official
field/root paths newly reachable. The version normalization regression was
introduced by the correction's switch from a semver search to a prefixed
full-match. These are not optional hardening.

This is the correction review allowed by the ticket. The same ticket must not
receive another automatic correction, branch or worktree, and the rejected
implementation must not be integrated. Ticket 05B, 05C and Ticket 04 remain
dependency-blocked. A control-plane convergence decision is required before any
new implementation authority: either the owner explicitly changes the
one-correction rule for one final same-branch additive repair, or the control
plane supersedes/decomposes 05A under a new reviewed ticket architecture.

## Owner convergence decision and independent reconfirmation

The owner subsequently instructed the control plane to inspect this exact return
and re-dispatch according to the result. A fresh independent execution reproduced
focused `13/13`, full `169/169`, strict mypy across `82` files, in-memory compile
and clean diff/status. Direct probes again observed:

- explicit `marketplaceSource: null` accepted by both official entry DTOs;
- `CodexCliVersion.value == "codex-cli 0.144.0-alpha.4"` instead of the semantic
  version capture;
- `LOCALAPPDATA=relative` yielding a relative proof and `ELIGIBLE`.

The review conclusion remains `CHANGES_REQUESTED`; nothing is approved or
integrated. The owner's re-dispatch instruction is recorded as the explicit
single-use convergence override allowed by the conclusion above. Exactly one
final additive repair may run on the same ticket/task/worktree/branch, with the
same allocation and receipt and current implementer model `gpt-5.6-terra` at
`xhigh`. The ticket production ceiling is revised from `170` to `180` non-blank
lines so named validation is not compressed; its test ceiling remains `180` and
the parent `400 / 450` cluster ceiling is unchanged. The next independent review
is terminal: pass to approval or stop as `BLOCKED / SUPERSEDE_REQUIRED`.

## Terminal owner-overridden final review

### Final boundary and independent verification

The final additive implementation `97ab31c694db97363f61fa6f437b6decf22a1a41`
and docs-only handoff `4fc81a5f74977f4b7b732a51d66e562431a5bcb6`
are descendants of correction handoff `59c3f96` on the same sole branch and
worktree. Both Git worktrees are porcelain-clean, the implementation task is
idle, and no new branch/worktree, merge, push, deployment or live Codex action
was created. Rejected parent commits `0c2ab95`, `c2ea3f8`, `3f6c41a` and
`13d02de` are not ancestors of the final implementation.

| Check | Terminal-review evidence |
| --- | --- |
| Green suite | PASS: focused unittest `16/16`; full discovery `172/172`; strict mypy `82` files; five-file in-memory compile; source sentinel and `git diff --check`. |
| Scope / ceiling | PASS: cumulative production `179` added / `2` removed non-blank lines, net `177 / 180`; test `171 / 180`. Final implementation changes only `host_contracts.py`, `codex_cli_adapter.py` and the authorized preflight test; final handoff changes only `doc/WorkProgressReport.md`. |
| A1 public boundary | PASS: absent optional sources remain valid; explicitly present null is rejected on both official entry DTOs; strict object form passes; version admission remains full-form-only and exposes semantic capture `0.144.0-alpha.4`. |
| A2 source proof | PASS: exact source succeeds. Foreign, prefix, suffix, trailing separator, case, encoded separator, traversal, relative, drive-relative, empty and constructed root/ID/locator variants recursively block before either list command. |
| A3 collision | PASS: marketplace plus installed/available plugin collisions, including case variants and foreign marketplaces, return finite `COLLISION` without mutation. |
| A4 finite failures | PASS: prior declared process/filesystem/timeout/encoding/malformed-output paths remain green; missing executable retains `EXECUTABLE_UNAVAILABLE`. |
| Reverse truth | PASS for executable behavior: isolated commit-archive mutations of explicit-null rejection, version capture, Windows-absolute admission, available collision and executable mapping each made its named test exit nonzero; restoration returned focused `16/16`. |
| Git isolation | PASS: the existing and empty temporary Git byte/porcelain test passed inside the full suite. Reviewer probes used recorded ports only. |
| Hidden-state boundary | **FAIL**: ignored `.mypy_cache` files in the implementation worktree were rewritten at `2026-08-09T17:17:37Z` and `17:18:44Z`, inside the implementation turn `17:15:44Z` through `17:19:44Z`. This violates the ticket's no-hidden-config/cache rule and contradicts the final handoff's no-hidden-state-write claim. The reviewer did not delete or alter the implementation worktree. |
| Handoff ledger identity | **FAIL**: final branch handoff heading `PRG-20260810-087` collides with the canonical control-plane `PRG-20260810-087` correction-review record already present in control baseline `83e34c3`. Commit SHA and handoff ID remain immutable evidence, but the submitted docs-only record cannot enter the unique progress ledger unchanged. |

### Final closure and CodeReview.md mapping

| Item | Result | Terminal result |
| --- | --- | --- |
| `A1` | PASS | Exact public DTO null/absence and semantic-version cells pass. |
| `A2` | PASS | Exact absolute Windows canonical proof and complete path/bypass matrix pass. |
| `A3` | PASS | Installed and available collision closure remains complete and effect-free. |
| `A4` | PASS | Declared failures remain finite with stable named reasons. |
| `A5` | FAIL | Tests are mutation-sensitive and all executable checks pass, but hidden cache writes make the isolation claim false and the final handoff reuses a canonical progress-record ID. |

- CodeReview.md class 1 path-prefix matrix: PASS, with exact equality and all
  seven mandatory variants mapped to committed tests plus independent probes.
- CodeReview.md class 3 authority bypass: PASS, with public request,
  recursively reconstructed filesystem proof and constructed nested values all
  converging on the same exact-owner/source checks.
- CodeReview.md class 7 test truth: FAIL for the delivery evidence, despite all
  five reverse mutations detecting their intended executable regressions.

### Terminal findings and conclusion

1. **CR-90 — `EVIDENCE_DEFECT`, A5.** The implementation turn rewrote ignored
   `.mypy_cache` state in the assigned worktree while the ticket prohibited
   hidden config/cache edits. The docs-only handoff then states that no hidden
   state write occurred. Git porcelain cleanliness does not make this claim
   true.
2. **CR-91 — `EVIDENCE_DEFECT`, A5.** The final docs-only handoff reuses
   `PRG-20260810-087`, which already identifies the canonical correction review
   in the control ledger. The handoff commit is immutable, but its record ID is
   not safe to integrate as submitted.

`BLOCKED / SUPERSEDE_REQUIRED`. The production behavior closes A1 through A4,
but A5 and the required truthful docs-only handoff do not pass. The ticket's
terminal rule authorizes no further same-ticket correction, implementation
dispatch, branch or worktree. Ticket 05B, 05C and Ticket 04 remain dependency
blocked. No integration, cleanup of the implementation worktree, push,
deployment, schedule, live Codex mutation or target-project action was
performed.
