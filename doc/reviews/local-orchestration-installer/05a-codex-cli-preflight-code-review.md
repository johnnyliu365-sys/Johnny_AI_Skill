# 05A Codex CLI Contract and Ownership Preflight - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05a-codex-cli-preflight-contract` |
| Result | `CHANGES_REQUESTED` |
| Reviewer | Codex / current `main` worktree |
| Reviewed branch | `codex/implementation-codex-cli-preflight-05a` |
| Boundary | Baseline `d90b69e`; implementation `88f7aae`; docs-only handoff `67dc1db` |
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
