# Ticket 05 code review — reachability measures the wrong thing

| Field | Value |
| --- | --- |
| Ticket | `claude-code-plugin-distribution/05-reachability-measures-the-wrong-thing` |
| Reviewer | Terra / `xhigh` |
| Closure revision | Revision 02 |
| Verdict | `CHANGES_REQUESTED / EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED` |
| Integrated source change | None |
| Remote effect | None |

## Evidence reviewed

| Phase | Commit | Result |
| --- | --- | --- |
| Initial implementation | `539133fb8f63c32ed02e99ab0236bdc1e49bcca4` | Typed local/remote reachability contract and focused tests. |
| Reviewer-generated payload pin | `8d2821683c424e784a6655508a9ba7096d7ad9c4` | Generated payload and marketplace pin on the candidate branch; never a hand-edited SHA. |
| First correction | `b7e17ece51d2780ef8c9cda011ad8ce9a1065d4a` | Candidate worktree suite was green, but a true fresh clone exposed two failures. |
| Post-cap evidence only | `e890c25c7e95ec4161c6e934e336aff0c2580faf` | Repairs the temporary-anchor construction from the verified pin SHA; fresh-clone evidence reports 52 passed / 279 subtests. It is not an approved merge source. |

## Verification and finding

The focused candidate suite after `b7e17ec` passed 52 tests. A reviewer then created a
temporary bare remote and a true fresh clone—the delivery shape the ticket claims to support.
Two real-pin cells failed because the helper itself sourced the publication commit from
`refs/heads/publication-0.4.9`. A normal clone does not have that local branch. The proof was
therefore coupled to worktree-only state and could not establish the clean-clone claim.

This is an **evidence defect** under C13: the implementation may describe the intended contract,
but the required delivery-shaped proof was invalid. Reverse mutations and strict checks do not
close that gap when their positive control relies on the same unavailable local ref.

`e890c25` changes the helper to push the already-validated full pin SHA into the temporary bare
remote, and the implementer independently reproduced 52 passed / 279 subtests in a true fresh
clone. That repair arrived after the one permitted correction review in this closure had itself
found a defect. `CodeReview.md` therefore requires `CONVERGENCE_REVIEW_REQUIRED`; it cannot be
treated as a third automatic correction or as review approval.

## Required continuation

Revision 03 creates a new candidate branch and review closure. Reapply the retained source/test
evidence only, run a new Terra initial review including the reverse mutations and true fresh-clone
proof, then generate and verify the publication pin on that same candidate branch. No existing
commit is reset, amended, deleted, or presented as integrated.

## Revision 03 closure

| Field | Result |
| --- | --- |
| Reviewer / outcome | Terra / `xhigh` — `APPROVED / INTEGRATED` |
| Source/test commits | `b6989c6`, `d4ea78c`, `d7bb1c6`, `92ac317` |
| Generated payload pin | `c3cb81c4550e6493f9d8478c4be31ffdad642f87` |
| Integration | `admit_document_mutation` → `7458e8d26f015215dcb2f503704a2feaf33c2a97` |
| Candidate boundary suite | `53 passed, 283 subtests passed` |
| True fresh-clone boundary suite | `53 passed, 283 subtests passed` |
| Full candidate suite | `1676 passed, 22 skipped, 3996 subtests passed`; three unrelated baseline failures below |
| Remote effect | None; no actual origin push or ref update |

The one permitted Revision 03 correction fixed a P0 boundary defect: non-string `ref` values had
reached `startswith` before validation. `None`, empty, malformed local, and malformed remote
values now raise `PublicationRefError`. Focused reachability tests, `mypy --strict`, and
`compileall` passed.

Reviewer reverse mutations all made their named tests fail, then were restored byte-for-byte:

1. Removing `refs/remotes` from the ref query made the clean-clone last-fetch state test fail.
2. Accepting a local branch as fetchability evidence made the local-only rejection test fail.
3. Collapsing remote state to `NOT_PUSHED` made the clean-clone remote-state test fail.

The full candidate suite's three failures are pre-existing environment failures. The same three
individual cells were run against unintegrated main with identical results: two expect machine-
readable stdout through Windows `cmd.exe` but receive the console prompt/encoding output, and the
active pytest is `9.0.3` while `requirements-dev.txt` declares `9.1.1`. None shares a modified
path with ticket 05. They are recorded rather than waived.
