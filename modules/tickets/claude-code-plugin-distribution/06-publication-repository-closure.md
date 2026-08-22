# 06｜Publication repository reachable-tree closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-2, AC-5, AC-6 and AC-7 |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `APPROVED / NOT_DISPATCHED` / `CLOSURE_01` |
| Baseline | `9be8ee4b6e713e858dfb4909de1ef4a940c05594` |
| Control owner / reviewer | `ticket-review` — Terra / xhigh, capability readback required at dispatch |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket only, no helper |
| Delivery profile | `POC / STANDARD`: deterministic local Git fixtures and read-only closure classification; no remote, host, credential, repository or user-installation effect. This ticket is prerequisite evidence for the feature's later high-assurance cutover. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over every new public module and focused test module |
| XSS classification | `N/A` — no Browser/WebView/HTML/DOM/JavaScript input or renderer |
| Worktree / branch | `.worktrees/claude-publication-06` / `implement/claude-publication-06-repository-closure` |
| Dispatch mode | Same-lifetime reviewer dispatch → wait → review. No runner, queue or asynchronous receipt-bound wake is a precondition. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/publication_repository_closure.py
modify = library/local_orchestration/claude_plugin_cache_closure.py
modify = tests/test_publication_repository_closure.py
modify = tests/test_claude_plugin_cache_closure.py
modify = .claude-plugin/marketplace.json
forbid = .claude-plugin/plugin.json
forbid = .codex-plugin/
forbid = README.md
forbid = library/local_orchestration/plugin_publication.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
```

The implementation owner may change only the two new Python modules and their direct tests.
`library/local_orchestration/plugin_publication.py` is a read-only dependency supplying the
declared-payload/tree primitives. The reviewer may run the existing generator after source review;
the resulting `.claude-plugin/marketplace.json` pin is generated output, never hand-edited source.

## Sole observable closure

Given a typed local Git repository/cache snapshot, return a finite closure result that is
`VERIFIED` only when every admitted ref resolves to a parentless commit whose `git ls-tree -r`
paths and blob IDs equal one declared payload. Any development ref/tree, unexpected ref/default
branch, non-root commit, malformed Git result or unreadable tree returns a distinct non-success
status. A correct checkout alone cannot yield `VERIFIED` while a reachable development tree
remains in `.git`.

The closure is read-only: it creates only disposable local test repositories, never invokes
`claude`, contacts a remote, creates a remote ref, modifies a user's plugin cache or makes a
publication decision.

## Frozen contracts

Implement the Revision 02 typed contracts as frozen, validated Python values. At minimum the
public surface must expose typed repository/ref/commit inputs, `PublicationTreeDifference`,
`PublicationClosureStatus`, `PublicationRemoteSnapshot`, `PublicationClosureResult`, and the
installed-cache counterpart `InstallClosureStatus`. Inputs received from Git are normalized at
the boundary; no `dict[str, object]`, `Any`, partial SHA, inferred ref/default branch or exception
text may cross into the domain result.

Allowed publication refs are exactly `refs/heads/main` and lightweight
`refs/tags/plugin-v<semver>`. A valid release tag and `main` may name the same parentless commit.
Every other head/tag, a symbolic/default branch mismatch, a parent, duplicate/inconsistent target,
missing payload path, extra path or different blob is a named rejection. The installed-cache
checker applies the same condition to every ref and every commit reachable from it; known
development-only sentinels are supplementary negative evidence, not the primary allowlist.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| C1 positive repository closure | A disposable bare repository with `main` and `plugin-v1.2.3` both naming one generated root returns `VERIFIED`; every tree has empty path/blob difference. |
| C2 ref/default failures | Foreign branch/tag, missing `main`, non-`main` default branch and inconsistent tag target each return their named finite failure. No broad “invalid” success fallback. |
| C3 history/tree failures | A commit with a parent, an undeclared development path, a missing declared path and a changed blob each turn closure red and identify the relevant difference/failure. |
| C4 installed-cache shape | A fixture with correct detached payload `HEAD` but reachable development `main` is rejected; a payload-only fixture is accepted. Every reachable commit/ref is enumerated rather than only `HEAD`. |
| C5 malformed boundary | Bad ref name, malformed/full-but-absent SHA, unreadable `for-each-ref`/`ls-tree` output and non-commit object fail closed with named error/result. |
| C6 regression | Existing payload declaration, pin/tree and fetchability tests remain green; no existing public function changes behavior. |

For this new behavior, record green cells rather than a ceremonial first-red. The reviewer must
perform an independent reverse mutation from a different door: add a reachable development ref
to an otherwise valid cache/repository fixture. At least C4 must become red, and exact restoration
must return it green. A reverse mutation that leaves all cells green is an evidence defect.

## Verification and completion

1. Run focused two-module tests, `tests/test_plugin_payload_boundary.py`, and
   `tests/test_plugin_publication.py` with a bounded command/result capture.
2. Run `mypy --strict` over both new modules and direct tests; run JSON parsing of plugin manifests
   and `git diff --check`.
3. Before integration, the Terra reviewer independently reads the candidate diff, recomputes each
   AC-to-cell mapping, runs C4's reverse mutation, runs the focused suite in a fresh local clone,
   and records every red/green result.
4. The implementation owner commits source/test changes only. After review, the reviewer runs the
   existing generator in the same candidate, verifies its pin/tree binding, commits only the
   generated marketplace pin, and uses `admit_document_mutation` for integration.

Completion return is `ImplementationReturn.COMPLETED → ACTION_COMPLETED`; an absent type,
ambiguous result, changed publication topology or effect request is
`CHANGE_DETECTED → REQUIREMENT_CHANGED`. No remote/publication effect is permitted in this ticket.
