# Worktree placement

Create every worktree under the repository root at `.worktrees/<ticket-id>`.

Never create one as a sibling of the repository, on the Desktop, or at any
other path outside the repository root. A worktree reached through a junction
or other reparse point is refused even when its literal path looks contained.

Both `.worktrees/` and the Claude Code harness-owned
`.claude/worktrees/` are sanctioned and git-ignored.
