# Ticket 36 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/36-git-pinned-test-source-inventory.md` |
| Baseline | `ace42df8a37931282145f1a31949815f8a222d3b` |
| Initial candidate / correction | `1d96fafea56ca8e5b2de37f9b37cf64b50f98c4e` / `4c6cfbeb34d1235bf78c0293e05f26dd2474976b` |
| Reviewer | Separate `gpt-6-sol/high` seat in isolated worktree |
| Conclusion | Initial `CHANGES_REQUESTED / IMPLEMENTATION_DEFECT`; correction `APPROVED` |

The reviewer used the public `read_inventory` entry to reproduce two Closure 1 failures despite 22 initial passing tests. First, `git replace old new` made a pinned old commit report new content and zero old consumers while still returning the old SHA. Second, a non-`.py` gitlink was skipped before its tree mode was checked and incorrectly returned a complete inventory. The same-ticket correction applies `git --no-replace-objects` to every Git read and rejects symlink/gitlink tree entries before suffix filtering. Reviewer public probes confirmed commit and blob replacement cannot drift the result, and non-Python gitlink/symlink refuse with `UNSUPPORTED_TREE_ENTRY`.

Reviewer-owned reverse mutations changing the pinned read to `HEAD` and dropping the indirect consumer edge each turned named tests red; restoration returned green. Final candidate suite: 26 passed, 2 subtests; strict mypy and `git diff --check` passed. The 457-line initial adapter kept bounded Git reading and source identity separate from the existing AST dependency parser; length alone was not a defect. No source is executed and no retirement permission is issued. Review worktree returned clean to its original branch.

Root cherry-picked both reviewed commits onto `control/skill-improvement-36-land`, verified the two resulting Git blobs exactly equal correction candidate `4c6cfbeb`, and the existing control-plane gate returned `INTEGRATED` at `e1ca2d4b7b9bf5876291800dd1f6d5df73b31c3a`. The integration branch independently reran 26 tests, 2 subtests and strict mypy. No push, release, target write or test deletion occurred. Real CI command source and retirement admission remain unverified; checklist 08 stays unchecked.
