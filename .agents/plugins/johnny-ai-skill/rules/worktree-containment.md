# Worktree placement

Create every worktree under the repository root at `.worktrees/<ticket-id>`.

Never create one as a sibling of the repository, on the Desktop, or at any
other path outside the repository root. A worktree reached through a junction
or other reparse point is refused even when its literal path looks contained.

`library/local_orchestration/worktree_containment.py` provides
`sanctioned_worktree_path(repository_root, ticket_id)` for the correct path and
`verify_worktree_contained(repository_root, worktree_path)` to check one that
arrived another way. Both `.worktrees/` and the Claude Code harness-owned
`.claude/worktrees/` are sanctioned and git-ignored.
