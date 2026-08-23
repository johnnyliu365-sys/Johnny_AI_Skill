# 13｜Installed-cache lossless quoted-path closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 05, AC-5 through AC-7; Ticket 06 installed-cache closure contract; Ticket 08 L4 actual-cache evidence |
| PRD / CHG / Context | `PRD-20260823-037` / `CHG-20260823-037` / sealed Context Revision 04, blob `f175d6a6842ca1d24a3cfd85e3a24542e7d7b9a3` |
| State / closure | `DONE / APPROVED / INTEGRATED / CLOSURE_01` |
| Integration | `admit_document_mutation` → `7a7000ba0affd8573ba5a646bfffe3ec46ca0ebf` |
| Exact defective baseline | `2101c02bcf1e53380146f9c95dea689703dca1ee` |
| Dependency | Tickets 06, 09, 10, 11 and 12 are integrated. Ticket 08's actual isolated 0.4.11 cache returns `INSTALLED_TREE_MISMATCH` before its live L4 closure. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket, no helper lane |
| Delivery profile | `POC / STANDARD`: deterministic local Git cache fixtures and read-only closure classification only. No Claude CLI, user-cache, remote, repository, ref, tag or release effect is permitted. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over the two declared modules |
| XSS classification | `N/A` — no Browser/WebView/HTML/DOM/JavaScript input or renderer |
| Worktree / branch | `.worktrees/claude-publication-13` / `implement/claude-publication-13-quoted-paths` |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → receive → independent review. No runner, queue, receipt, live descriptor or workspace-binding readback is a precondition in this POC profile. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/claude_plugin_cache_closure.py
modify = tests/test_claude_plugin_cache_closure.py
forbid = .claude-plugin/
forbid = .codex-plugin/
forbid = README.md
forbid = library/local_orchestration/plugin_publication.py
forbid = library/local_orchestration/publication_repository_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

The implementation owner edits only the declared two files and does **not** commit. It must not
invoke Claude, contact a remote, create, move, delete or push a Git ref outside disposable local
test repositories, modify a user cache, alter a descriptor/pin, regenerate a publication root or
claim a release. Terra writes the reviewed candidate commit and is the only role permitted to
submit it to `admit_document_mutation`.

## Sole observable closure

A reachable parentless installed-cache payload containing valid UTF-8 non-ASCII paths is read
from Git's lossless NUL-delimited path form and returns `VERIFIED` when its paths/blobs match the
declared payload. Git's display quoting is never parsed as an object path. Malformed path bytes
remain `INSTALLED_TREE_MISMATCH`; reachable development sentinels under `tests/`, `doc/` or
`modules/` remain `SENTINEL_REACHABLE`.

The fix is limited to the sentinel adapter. It preserves the existing typed result/status surface,
ref grammar, parentless-history and exact path/blob checks. It must not use replacement decoding,
silently strip bytes, loosen the path grammar or treat a parser failure as safe.

## Frozen contract

1. `_tree_contains_sentinel()` consumes `git ls-tree -r -z --name-only` output as NUL-delimited
   raw bytes, and decodes every path strictly as UTF-8 before applying the existing path grammar.
2. Valid non-ASCII paths, including `library/功能集群/...`, are ordinary payload paths: they must
   neither become quoted display text nor cause a green cache to return `INSTALLED_TREE_MISMATCH`.
3. Missing terminal NUL, empty entry, invalid UTF-8, absolute path, backslash, NUL, empty
   component, dot or traversal component is a finite `INSTALLED_TREE_MISMATCH` result.
4. A valid non-ASCII path under any existing sentinel prefix remains a named
   `SENTINEL_REACHABLE` result; the Unicode adapter must not suppress development-tree evidence.
5. This ticket changes no payload declaration, pin carrier, publication topology, promotion plan,
   model profile or Ticket 08 external-effect authority. Ticket 08 must rebind and repeat its
   complete live L1–L6 proof after this ticket is independently integrated.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| T13-1 authentic baseline red | A fresh normal-clone cache fixture with declared `library/功能集群/...` and `core.quotePath=true` returns `INSTALLED_TREE_MISMATCH` at the exact defective baseline; its intended result is `VERIFIED`. Record the test name and failure before the adapter change. |
| T13-2 lossless green | The same fixture returns `VERIFIED` after the change, retaining exact parentless-root, direct/ref/symbolic and path/blob assertions. |
| T13-3 fail-closed bytes | Invalid UTF-8, missing terminal NUL, empty/malformed path, absolute path, backslash or traversal component each return `INSTALLED_TREE_MISMATCH`; no byte replacement or coercion is accepted. |
| T13-4 sentinel retained | A valid CJK tree listing containing reachable `tests/功能.py`, `doc/功能.md` or `modules/功能.md` returns `SENTINEL_REACHABLE`, never `VERIFIED`. |
| T13-5 reviewer counter-mutation | Terra uses a fresh green detached CJK fixture, adds a reachable `refs/heads/main` parentless development tree containing `modules/審閱.py`, observes `SENTINEL_REACHABLE`, deletes only that fixture ref and verifies byte-exact restoration to `VERIFIED`. A zero-red mutation blocks approval. |

## Strong-type preflight and verification

The existing public DTOs, enums and result types are unchanged; construct the ordinary
`PublicationCommit`, `PublicationPayload` and `InstallClosureResult` success path before the
first-red test. Invalid raw Git bytes exist only in named negative fixtures. P0 applies: no
unchecked mapping, `Any`, raw error text or stringly status crosses the adapter boundary.

Run at minimum:

```text
py -3.11 -m unittest discover -s tests -p test_claude_plugin_cache_closure.py -v
py -3.11 -m unittest discover -s tests -p test_publication_repository_closure.py -v
py -3.11 -m unittest discover -s tests -p test_plugin_payload_boundary.py -v
py -3.11 -m mypy --strict library/local_orchestration/claude_plugin_cache_closure.py tests/test_claude_plugin_cache_closure.py
py -3.11 -m compileall -q library/local_orchestration/claude_plugin_cache_closure.py tests/test_claude_plugin_cache_closure.py
git diff --check
```

The implementer returns the uncommitted diff, exact command summaries, T13 cell outcomes and the
baseline-red evidence. Terra independently verifies clean ancestry and scope, performs T13-5 in a
fresh fixture and writes the candidate commit only after all gates pass.

## Completion and continuation

`ImplementationReturn.COMPLETED` becomes `ACTION_COMPLETED` only after Terra review, its
candidate commit, `admit_document_mutation` and `origin/main` readback. It authorizes no Claude
CLI, release or user installation. The only continuation is Ticket 08 CLOSURE_05 re-admission,
fresh source binding and fresh isolated L1–L6 proof; a changed requirement or external effect
request returns `CHANGE_DETECTED → REQUIREMENT_CHANGED`.

## Completion evidence

The actual 0.4.11 isolated Claude cache proved the defect against the exact baseline: its
path/blob difference was empty, all named refs targeted parentless
`5c1cb9aec837a2fc8c76634404bccd393a0b9281`, yet display-form CJK path quoting made the prior
sentinel adapter return `INSTALLED_TREE_MISMATCH`. Luna/xhigh changed only the two declared
files, recorded the deterministic `core.quotePath=true` baseline-red cell, and returned its
uncommitted candidate. Terra/xhigh required and then approved explicit dot/empty-component
negative cells, independently repeated the reachable `modules/審閱.py` mutation
`VERIFIED → SENTINEL_REACHABLE → VERIFIED`, and confirmed exact fixture ref/HEAD/tree
restoration.

The reviewer reran 15 installed-cache tests, 15 publication-closure tests and 41 payload-boundary
tests; strict mypy, compileall and `git diff --check` passed. The reviewer committed the exact
candidate at the integration SHA above; the source mutation gate admitted it and `origin/main`
read back that same SHA. No Claude CLI, user cache, remote publication ref/tag, descriptor,
generation or release effect occurred in Ticket 13.
