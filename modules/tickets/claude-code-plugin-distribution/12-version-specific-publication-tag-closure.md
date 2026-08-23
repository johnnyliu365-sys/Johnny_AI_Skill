# 12｜Version-specific immutable publication-tag closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 05, AC-2, AC-3, AC-7 and AC-11 |
| PRD / CHG / Context | `PRD-20260823-037` / `CHG-20260823-037` / sealed Context Revision 04, blob `f175d6a6842ca1d24a3cfd85e3a24542e7d7b9a3` |
| State / closure | `OPEN / OWNER_APPROVED / DISPATCHABLE` / `CLOSURE_04` |
| Exact baseline | `475e01b96693c33251e77eed2bbff3116f2bc713` |
| Dependency | Tickets 06, 07, 09, 10 and 11 are integrated. Ticket 08 CLOSURE_03 is blocked on this ticket; it has no active effect authority. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket, no helper lane |
| Delivery profile | `POC / STANDARD`: deterministic disposable local Git fixtures and read-only closure classification only. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over both declared production and test modules |
| XSS classification | `N/A` — no Browser/WebView/HTML/DOM/JavaScript input or renderer |
| Worktree / branch | `.worktrees/claude-publication-12` / `implement/claude-publication-12-version-specific-tags` |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → receive → independent review. No runner, queue, receipt, live descriptor or workspace-binding readback is a precondition in this POC profile. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/publication_repository_closure.py
modify = tests/test_publication_repository_closure.py
forbid = .claude-plugin/plugin.json
forbid = .claude-plugin/marketplace.json
forbid = .codex-plugin/
forbid = README.md
forbid = library/local_orchestration/plugin_publication.py
forbid = library/local_orchestration/claude_plugin_cache_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = install.ps1
forbid = johnny-install.cmd
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
forbid = doc/
```

The implementation owner edits only the declared two files and does **not** commit. It must not
create/move/delete any ref outside disposable local test repositories, call a remote, run Claude,
repin a manifest, regenerate a publication root, edit a marketplace entry or make a release claim.
After review, Terra commits the exact reviewed worktree diff to the candidate branch and uses
`admit_document_mutation`; a changed contract or requested effect returns
`ImplementationReturn.CHANGE_DETECTED → REQUIREMENT_CHANGED`.

## Sole observable closure

Given a typed current `PublicationPayload`, publication snapshot and local Git repository,
`verify_publication_repository()` returns `VERIFIED` only when:

1. `main` is parentless and its full tree remains path-and-blob identical to that exact current
   payload, with the current candidate's reversible pin-carrier normalization;
2. a tag for the current candidate names that exact current generated root and its tag/plugin/
   marketplace versions agree; and
3. every retained historical `plugin-v<semver>` tag is parentless, has the exact path set declared
   by its own target's plugin manifest, has an admissible generated pin-carrier, and has matching
   tag/plugin/marketplace semantic versions.

An old release is not measured against today's candidate declaration. Its tag target is the
historical content provenance, so the historical rule does not claim external blob equality for
declared paths. It must still reject every undeclared/missing path, malformed declaration/carrier,
version mismatch, foreign ref, non-root commit and unreadable Git object with a finite named
result. No partial success, broad fallback or current-working-tree lookup is permitted.

## Frozen contract

Add only the named frozen DTO/enum/result surface needed to express an in-target release
declaration: semantic version, exact declared paths and generated carrier state. The target-blob
reader validates JSON and typed fields at the Git boundary. It may adapt the existing payload
declaration and carrier normalizer, but must not pass an unchecked `dict`, `Any`, cast, partial
SHA, raw string convention or exception text into the domain.

`PublicationClosureStatus` must distinguish malformed/unreadable release declaration from a
release-version mismatch and from an ordinary tree difference. A validator receives one current
payload for `main`; it must obtain historical declaration data solely from each tag target. The
status/result remains finite, frozen and compatible with Ticket 07's no-effect promotion input.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| T12-1 current release binding | A disposable bare repository with `main` and `plugin-v0.4.11` at one current parentless root verifies the current supplied payload path/blob comparison and exact tag/plugin/marketplace version agreement. A changed current blob remains red. |
| T12-2 retained older release | One fixture retains `plugin-v0.4.10` at a different parentless root whose own declaration has the older valid path set, while `main`/`plugin-v0.4.11` use the current path set. The complete allowed set verifies green without comparing the old tag to current working files. |
| T12-3 target-declaration failures | A missing/non-object/malformed target plugin declaration, malformed target marketplace entry, non-canonical generated carrier, missing declared path and extra tree path each return their distinct finite declaration/tree rejection. |
| T12-4 version binding | Tag semver disagreeing with the target plugin version or marketplace-entry version turns red. Exact restoration turns green. A current tag pointing at a different root also remains red. |
| T12-5 retained closure boundary | A foreign development head/tag, wrong default branch, symbolic/unknown ref, parented release target or unreadable tree stays rejected with the existing named finite result. |
| T12-6 reviewer reverse mutation | Terra independently adds one undeclared path or changes one tag's embedded version in a fresh two-release fixture. The otherwise-green closure must turn red and return green only after byte-for-byte restoration. A mutation that stays green is an evidence defect. |
| T12-7 typing and compatibility | Ordinary constructors validate every new public DTO/enum/result; bypass-built input is negative-only. Ticket 06/07 closure and promotion tests remain green, and no implementation path adds a remote, credential, retry or effect adapter. |

## Strong-type and verification preflight

Before the first red, construct all newly public DTOs and finite statuses through ordinary
validators. Negative cells may use malformed raw Git/JSON only at the boundary. Preserve P0:
no unchecked dynamic mapping, stringly status or source-text heuristic may cross into the result.

Run, at minimum:

```text
py -3.11 -m unittest discover -s tests -p test_publication_repository_closure.py -v
py -3.11 -m unittest discover -s tests -p test_publication_promotion.py -v
py -3.11 -m unittest discover -s tests -p test_plugin_payload_boundary.py -v
py -3.11 -m mypy --strict library/local_orchestration/publication_repository_closure.py tests/test_publication_repository_closure.py
py -3.11 -m compileall -q library/local_orchestration/publication_repository_closure.py tests/test_publication_repository_closure.py
git diff --check
```

The implementer returns the uncommitted diff, exact command summaries, all T12 cell outcomes and
the T12-2/T12-4 reverse-mutation evidence. Terra verifies clean ancestry and declared-path-only
scope, independently runs T12-6 from a fresh local fixture, then commits and integrates only a
passing candidate. A stale baseline, missing type preflight, zero-red reverse mutation or widened
scope is non-dispatchable/review-blocking evidence.

## Completion and continuation

`ImplementationReturn.COMPLETED` becomes `ACTION_COMPLETED` only after Terra's review,
candidate commit, `admit_document_mutation` and `origin/main` readback. It does not authorize
Ticket 08's CLOSURE_03 external effects. The Router next evaluates Ticket 08 against this
integrated contract; any later publication/cache/source action requires a fresh owner effect
authority bound to its then-current candidate and remote readback.
