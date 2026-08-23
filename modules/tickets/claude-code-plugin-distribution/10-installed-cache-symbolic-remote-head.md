# 10｜Installed-cache symbolic remote HEAD closure

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-5 through AC-7; Ticket 06 installed-cache closure contract; Ticket 08 CLOSURE_02 L4 blocker record |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `APPROVED / DISPATCH_READY` / `CLOSURE_02` |
| Exact baseline | `bb14e9623292dce65d8f1bfe00f2a869fb43c1ea` |
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
   only when its raw loose-ref bytes are exactly ASCII `ref: refs/remotes/<remote>/main\n` and
   its symbolic target is exactly the same remote's `main` ref. CRLF, trailing whitespace, extra
   newline, non-ASCII and every other byte variation are finite rejections.
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
| S3 grammar rejection | Symbolic heads/tags, `origin/HEAD` to `origin/release`, cross-remote targets, malformed remote names and malformed symbolic targets are named non-successes. A raw CRLF loose target and a raw target with trailing whitespace must each return the named non-success; byte-exact LF restoration is green. |
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

## CLOSURE 01 convergence blocker

The implementation owner first returned `3fd34100d47532145c62775e70123d652f3f4787`. Terra
found an S3 bypass: trailing whitespace in a loose `origin/HEAD` target was erased by broad
string trimming. The owner preserved that commit and added correction
`cc5c718db0569b7ceccccfb544554a1c09eba36d`; Terra's correction review confirmed the trailing
space now rejected and its independent non-`main` target mutation turned red then restored green.

The integration reviewer then performed a different raw-file counter-mutation against the
complete candidate. `ref: refs/remotes/origin/main\r\n` returned `VERIFIED` because
`Path.read_text()` applies universal-newline translation before the adapter's single-LF check.
That silently normalizes a malformed raw symbolic ref and violates Frozen Contract 2 and S3.
The nine focused installed-cache tests, strict mypy, compileall and diff check are green but do
not close this observable defect.

This is the second review outcome in `CLOSURE_01`. Per the bounded-convergence rule, no third
automatic correction may be dispatched. The unintegrated candidate commits remain review
evidence only. A control-plane convergence decision must revise the closure with an exact
raw-byte line-ending regression and obtain owner approval before any additional implementation
cycle; no Ticket 08 re-admission or external effect follows from this record.

## CLOSURE 02 convergence decision — 2026-08-23

The owner approved one new bounded cycle for the existing, unintegrated Ticket 10 branch. This
revision makes the raw-byte LF requirement explicit in Frozen Contract 2 and S3; it does not
change the observable closure, source boundary, profiles, external-effect prohibition or Ticket
08 dependency. The implementation owner must first rebase the preserved candidate commits onto
this control-plane commit, then add exactly one correction commit within the same two-file
boundary. The Terra reviewer must independently prove both raw CRLF and one different forbidden
symbolic-target mutation red before approval. A further defect in `CLOSURE_02` returns to control
plane again; it is not an automatic third correction.
