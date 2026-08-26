# 16｜Installed-cache version-specific retained-tag closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 07, AC-2, AC-5 through AC-7 and AC-11; Revision-07 clauses 1–4 |
| PRD / CHG / Context / architecture | `PRD-20260823-037` / `CHG-20260823-037`; Context Revision 06 (`CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260826-06`, sealed blob `59363cf1309d8905e1064e76126dbe3fde9bd8e3`); ADR-018 Decision 3. |
| State / closure | `APPROVED_NOT_DISPATCHED / CLOSURE_01` |
| Exact baseline | The committed `origin/main` authority SHA containing this ticket, recorded at dispatch. |
| Dependency | Tickets 10, 12 and 13 are integrated. Ticket 15 is terminally blocked by its one-attempt rule; this ticket repairs its local verifier prerequisite only. |
| Control owner / reviewer | `ticket-review` profile — Terra / xhigh, capability verified at dispatch. |
| Implementation owner | `implementation-standard` profile — Luna / xhigh; one ticket, no helper lane. |
| Delivery profile | `POC / STANDARD`: deterministic disposable local Git/cache fixtures and read-only closure classification only. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over all declared production and test modules. |
| XSS classification | `N/A` — no Browser/WebView/HTML/DOM/JavaScript input or renderer. |
| Worktree / branch | Reviewer creates `.worktrees/claude-publication-16-installed-cache-tags` on `implement/claude-publication-16-installed-cache-tags` from the recorded authority baseline. |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → receive → Terra review. No runner, queue, receipt, live descriptor or workspace readback is a precondition. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/publication_repository_closure.py
modify = library/local_orchestration/claude_plugin_cache_closure.py
modify = tests/test_publication_repository_closure.py
modify = tests/test_claude_plugin_cache_closure.py
forbid = .claude-plugin/
forbid = .codex-plugin/
forbid = commands/
forbid = skills/
forbid = template/
forbid = README.md
forbid = library/local_orchestration/plugin_publication.py
forbid = library/local_orchestration/publication_promotion.py
forbid = modules/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

The implementation owner changes only the declared four files and does not commit. It must not
invoke a marketplace/agent CLI, contact a remote, create/move/delete/push a non-disposable Git
ref, modify a user cache, alter a descriptor/pin, generate a publication root or claim a release.
Terra commits only the reviewed candidate and alone submits it to `admit_document_mutation`.

## Sole observable closure

`verify_installed_plugin_cache()` accepts a normal clone containing a checked-out current root and
older immutable `plugin-v<semver>` tags only when the current root still satisfies the supplied
current path/blob payload and every older tag independently satisfies its target-commit release
declaration, generated carrier and tag/plugin/marketplace version. All admitted targets remain
parentless. The existing installed ref grammar, symbolic `origin/HEAD` binding, sentinel checks
and finite failure surface remain strict.

The implementation must expose one typed public, target-commit declaration reader from the
publication-closure boundary rather than duplicate JSON/path/carrier parsing or import a private
helper. The cache verifier maps a malformed historical declaration, version disagreement or tree
difference to its existing fail-closed installed-cache result; it must not invent a successful
fallback or retain unchecked dynamic JSON.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| T16-1 baseline red | A disposable normal-clone fixture has a current `main` / current tag and one older valid release tag with a different declared payload. The exact defective baseline returns `INSTALLED_TREE_MISMATCH`; record the test name and reason. |
| T16-2 retained-tag green | After the repair, the same fixture is `VERIFIED`; `HEAD` and current root retain exact current-payload blob comparison, while only the historical tag is judged by its own declaration. |
| T16-3 target failures | A historical missing/malformed declaration, malformed carrier, tag/plugin/marketplace version disagreement, missing path or extra path is fail-closed and never `VERIFIED`. |
| T16-4 boundary retention | A foreign ref remains `INSTALLED_REF_SET_INVALID`; a parented target remains `INSTALLED_HISTORY_INVALID`; a historical `tests/`, `doc/` or `modules/` path remains `SENTINEL_REACHABLE`. |
| T16-5 public reader contract | Ordinary constructors validate the exposed typed result/declaration. Invalid Git/JSON remains at the boundary; no private-helper import, `Any`, cast or unchecked mapping establishes success. |
| T16-6 reviewer reverse mutation | Terra independently corrupts an older tag’s embedded version or adds an undeclared target path in a fresh two-release cache fixture. The green closure turns red; byte-for-byte restoration returns green. |

## Strong-type preflight and verification

Before the first red, construct every newly public DTO/result through its normal validator. Run at
minimum:

```text
py -3.11 -m unittest discover -s tests -p test_claude_plugin_cache_closure.py -v
py -3.11 -m unittest discover -s tests -p test_publication_repository_closure.py -v
py -3.11 -m unittest discover -s tests -p test_plugin_payload_boundary.py -v
py -3.11 -m mypy --strict library/local_orchestration/publication_repository_closure.py library/local_orchestration/claude_plugin_cache_closure.py tests/test_publication_repository_closure.py tests/test_claude_plugin_cache_closure.py
py -3.11 -m compileall -q library/local_orchestration/publication_repository_closure.py library/local_orchestration/claude_plugin_cache_closure.py tests/test_publication_repository_closure.py tests/test_claude_plugin_cache_closure.py
git diff --check
```

The owner returns the uncommitted diff, baseline-red, T16 cells and command summaries. Terra
confirms scope/ancestry, runs T16-6 in a fresh fixture and commits/integrates only a green
candidate. No source-only success authorizes a release or installation effect.

## Completion and continuation

`ImplementationReturn.COMPLETED` becomes `ACTION_COMPLETED` only after Terra review, candidate
commit, `admit_document_mutation` and direct `origin/main` readback. It does not unblock or retry
Ticket 15. Ticket 17 is the only permitted continuation: it takes a fresh snapshot of the existing
`0.4.14` publication object and isolated Codex cache before it may request guarded development
authority integration. A no-clone/no-retained-payload objective is a later major-version
requirement, not a Ticket 16 correction.
