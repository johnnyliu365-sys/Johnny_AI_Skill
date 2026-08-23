# Ticket 10 code review — installed-cache symbolic remote HEAD

| Field | Value |
| --- | --- |
| Ticket / closure | `claude-code-plugin-distribution/10-installed-cache-symbolic-remote-head` / `CLOSURE_01` |
| Reviewer profile | Terra / `xhigh` |
| Source baseline / cumulative candidate | `8c05102fbbbd8d282b80910d7a66eb27242a23a7` / `cc5c718db0569b7ceccccfb544554a1c09eba36d` |
| Candidate history | `3fd34100d47532145c62775e70123d652f3f4787` then additive `cc5c718db0569b7ceccccfb544554a1c09eba36d` |
| Verdict | `BLOCKED / CONVERGENCE_REVIEW_REQUIRED / IMPLEMENTATION_DEFECT` |

## Admission and scope

The cumulative candidate descends from the approved dispatch baseline, is clean, and changes
only `library/local_orchestration/claude_plugin_cache_closure.py` and
`tests/test_claude_plugin_cache_closure.py`, exactly as declared. The ticket's scope is a local,
read-only closure classifier; no XSS, provider, secret, user-cache, Claude CLI, remote, ref,
repository, tag or release effect applies.

## First review and correction

The first candidate admitted a normal `origin/HEAD -> origin/main` clone but trimmed a loose
symbolic target. Terra's independent fixture changed that target to include trailing whitespace
and observed a false `VERIFIED`. The owner added, without reset or amendment, the second commit
that makes this trailing-space form return `INSTALLED_REF_SET_INVALID`; byte-exact restoration
returns `VERIFIED`. Terra re-ran an independent `origin/HEAD -> origin/main/child` mutation and
recorded `VERIFIED -> INSTALLED_REF_SET_INVALID -> VERIFIED`.

## Final integration-review finding

The complete candidate still calls `Path.read_text()` on the loose symbolic-ref file. Universal
newline handling converts a raw CRLF line ending to LF before the adapter validates the one-LF
grammar. A fresh disposable fixture therefore produced:

```text
raw `ref: refs/remotes/origin/main\r\n` -> VERIFIED
byte-exact LF restoration -> VERIFIED
```

The first result must be `INSTALLED_REF_SET_INVALID`: Frozen Contract 2 and S3 require raw
symbolic-target grammar to be exact and forbid normalizing malformed target content. The missing
raw-byte CRLF regression leaves the production boundary unpinned.

## Supporting checks and routing

The candidate's focused installed-cache suite is green (`9 passed, 3 subtests`), strict mypy over
the changed module/test is clean, compileall and `git diff --check` are clean. Those checks do
not supersede the counter-mutation above. This is the second review result within one closure
revision, so CodeReview's bounded-convergence rule forbids a third automatic correction. No
candidate commit is integrated and Ticket 08 remains blocked; the required continuation is a
control-plane closure revision with an explicit raw-byte line-ending cell and a new owner
approval.
