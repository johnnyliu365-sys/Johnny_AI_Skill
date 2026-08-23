# 10｜Installed-cache symbolic remote HEAD closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-5 through AC-7; Ticket 06 installed-cache closure contract; Ticket 08 CLOSURE_02 L4 blocker record |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `APPROVED / DISPATCH_READY` / `CLOSURE_01` |
| Exact baseline | `0c2d71a311e4c2748082b61df6219d1d108e06db` |
| Dependency | Ticket 06 and Ticket 09 integrated; Ticket 08 CLOSURE_02 has an actual isolated-cache L4 failure. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket only, no helper |
| Delivery profile | `POC / STANDARD`: deterministic local Git cache fixtures and read-only closure classification. No Claude CLI, user-cache, remote, repository, ref, tag or release effect is permitted. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over the changed public module and focused test module |
| XSS classification | `N/A` |
| Worktree / branch | `.worktrees/claude-publication-10` / `implement/claude-publication-10-cache-symbolic-head` |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → review. No runner, queue, receipt or asynchronous wake is a precondition. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/claude_plugin_cache_closure.py
modify = tests/test_claude_plugin_cache_closure.py
forbid = .claude-plugin/
forbid = README.md
forbid = library/local_orchestration/plugin_publication.py
forbid = library/local_orchestration/publication_repository_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
forbid = install.ps1
forbid = johnny-install.cmd
```

This ticket corrects only the read-only installed-cache closure classifier. It must not invoke
Claude, contact a remote, create, move, delete or push a Git ref, modify a user cache, alter a
publication descriptor/pin, generate a publication root or integrate Ticket 08's candidate.

## Sole observable closure

An actual Claude clone's normal remote-default symbolic ref is admitted only when it is exactly
`refs/remotes/<remote>/HEAD -> refs/remotes/<remote>/main`, where the named remote and target
already satisfy the installed-cache ref grammar and resolve to the same declared parentless
payload root as `HEAD`. Every other symbolic ref remains a finite rejection. Direct refs,
reachable commits, tree/blob equality and development-sentinel rejection retain Ticket 06's
strict closure behavior.

The implementation may normalize the one admitted symbolic-ref shape at the Git boundary, but
must not erase it, infer a target, waive target existence, or reduce all invalid symbolic forms to
success. Domain results remain frozen typed values; no `Any`, raw Git error text or dynamic
mapping crosses the public result boundary.

## Frozen contract

1. A direct cache ref still passes only Ticket 06's existing allowlist and full-SHA validation.
2. A symbolic ref is admitted only under `refs/remotes/`, only at that remote's `HEAD` name, and
   only when its symbolic target is exactly the same remote's `main` ref.
3. The symbolic target must be present in the enumerated ref set and both its object target and
   cache `HEAD` must participate in the existing parentless, declared-payload tree checks.
4. A symbolic head/tag, a remote `HEAD` targeting another remote, a non-`main` branch, a missing
   target, a malformed remote name or a symbolic ref combined with a development ref returns the
   existing named non-success; none may yield `VERIFIED`.
5. This ticket changes no publication topology, generator normalization, pin-carrier behavior,
   promotion plan or external effect authority. Ticket 08 must re-run its entire L1–L6 proof from
   a fresh isolated configuration after this ticket is independently integrated.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| S1 normal clone ref | A disposable payload-only cache with direct `main`, `origin/main`, release tag and `origin/HEAD -> origin/main` returns `VERIFIED`; each unique target is parentless with zero path/blob difference. The implementer records this new expectation first red before the adapter change. |
| S2 target binding | The same symbolic remote HEAD is rejected when `origin/main` is absent, points at a different root, or does not equal the checked-out expected root. Exact restoration is green. |
| S3 grammar rejection | Symbolic heads/tags, `origin/HEAD` to `origin/release`, cross-remote targets, malformed remote names and malformed symbolic targets are named non-successes. |
| S4 closure retained | A reachable development ref/tree, parented commit, extra/missing/changing payload blob or sentinel remains red even when a syntactically normal remote HEAD is present. |
| S5 independent review mutation | Terra uses a fresh fixture: `VERIFIED →` one bounded forbidden symbolic-target or development-ref mutation `→` named red `→ VERIFIED` after exact restoration. A zero-red mutation blocks approval. |

## Verification and completion

Run the focused installed-cache closure tests, `tests/test_publication_repository_closure.py` and
`tests/test_plugin_payload_boundary.py`; then strict mypy over the changed module/test,
`compileall`, and `git diff --check`. The Terra reviewer independently repeats S5 and reads every
candidate path against this boundary.

`COMPLETED` returns `ACTION_COMPLETED`. A request for a real CLI probe, cache modification,
publication/source ref action, descriptor repin or Ticket 08 integration is `BLOCKED` or
`CHANGE_DETECTED`; it never becomes an implicit effect of this ticket. After owner approval and
successful source integration, the only continuation is Ticket 08 re-admission with fresh live
evidence.
