# 02 — Repo-contained Worktree Layout, Enforced at Dispatch Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `modules/spec/receipt-bound-role-supervision.md` AC-11 (write-owning execution identity) — extends the existing receipt-bound worktree binding with a containment predicate |
| Requirement | Owner directive 2026-08-19: every agent, across every model, places its worktree under the repository root. No more sibling or scattered folders. |
| State | `OPEN` — awaiting a named implementation owner |
| Baseline | `main` = `94bd8c7` |
| Workload | `STANDARD`; the admission gate touches frozen dispatch contracts and is reviewed at `HIGH_ASSURANCE` depth |
| Language / XSS | Python 3.11 strict Pydantic/mypy + Markdown / `XSS_NOT_APPLICABLE` |

## One outcome

Every implementation worktree, whichever model or tool created it, lives at
`<repository root>/.worktrees/<ticket-id>`. A dispatch whose worktree resolves
outside the repository root is refused fail-closed before any receipt is issued,
so the rule binds models that never read this repository's documentation.

## Frozen responsibility

- The canonical location is `.worktrees/<ticket-id>` directly under the
  repository root. The leading dot is load-bearing (see finding 5), not
  cosmetic.
- The ignore rule is `/.worktrees/` in the **committed** `.gitignore`, never
  `.git/info/exclude`. Exclude is per-clone local state: it does not survive a
  clone to another machine or another agent's checkout.
- The admission gate reuses the existing containment predicate precedent
  `_resolves_within_root` in `library/local_orchestration/payload_effect_ports.py`,
  including its base self-resolution precheck. Do not write a second
  containment implementation.
- Refusal is finite and fail-closed: `HALT / WORKTREE_OUTSIDE_REPOSITORY_ROOT`,
  no receipt issued, no partial state written.
- The worktree path is read back from the host. It is never accepted from the
  ticket payload: caller data must not be able to mint its own approval.
- AC-11 is unchanged in substance. This ticket constrains only *where* a
  worktree may live, not what it may write.
- The rule governs worktrees an **agent** creates under this checkout. The
  owner's own checkouts and clones are out of scope and must not be moved,
  pruned or otherwise touched: the owner works from them directly and may
  re-clone from GitHub at any time. `git worktree prune` is **not**
  authorized by this ticket.

## Authorized implementation scope

```text
.gitignore
AGENTS.md
library/workflow_router/            # admission gate and its contracts
tests/
modules/tickets/workflow-governance/README.md
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | `/.worktrees/` is committed in `.gitignore`, and a worktree created there leaves `git status --porcelain=v1 --untracked-files=all` empty. Proven by regression, not assumed (see finding 1). |
| `R2` | A worktree nested at `.worktrees/` is not collected by the test run (no double collection), and a clean-clone bundle build still returns `BUNDLED`. |
| `R3` | Dispatch admission refuses a worktree outside the repository root with `HALT / WORKTREE_OUTSIDE_REPOSITORY_ROOT`; readback proves no receipt was issued and no approved state was written. |
| `R4` | Containment resists reparse evasion: a junctioned repository root and a junctioned worktree path both refuse. Reverse mutation — removing the base self-resolution precheck turns this cell red. |
| `R5` | Every agent-created worktree resolves under `.worktrees/`. Owner-owned checkouts, clones and their worktree registrations are byte-unchanged and still registered afterwards — evidence must show `git worktree prune` was never run. |
| `R6` | `mypy --strict` clean; full suite green; `tests/.johnny-runtime` zero residue. |

## Control-plane findings the implementer must not rediscover

1. The bundle builder reads exactly `git status --porcelain=v1 --untracked-files=all`
   (`plugin_bundle_builder.py:154-156`). That excludes ignored paths, so a
   `.gitignore`d `.worktrees/` does **not** trigger `SOURCE_DIRTY`. Prove this by
   regression rather than assuming it — the release chain depends on it.
2. `ADR-20260813-007` requires final verification to read **ignored** porcelain
   (to prove `tests/.johnny-runtime` absence). That check will now also surface
   `.worktrees/`. Reconcile it so the ignored-status verification still
   distinguishes runtime residue from the sanctioned worktree root. Do not
   weaken the ADR-007 check to make it pass.
3. `AGENTS.md` is in the payload manifest's `_REQUIRED_FILES`
   (`windows_package_manifest.py`), so editing it **changes the bundle digest**.
   That is correct for a future release, but the published `v0.4.1` asset is
   immutable and the L9 wrapper pins its digest `f67047f4…`. Do not rebuild or
   re-tag `v0.4.1`; this change ships in the next release with its own digest.
4. `.claude/worktrees/` is presently excluded only by `.git/info/exclude:7` —
   local, per-clone, uncommitted. That fragility is exactly what this ticket
   removes.
5. This repository has no `pytest.ini`, `pyproject.toml`, `setup.cfg` or
   `mypy.ini`, so pytest's default `norecursedirs` (which includes `.*`) is what
   keeps a nested worktree out of collection. If a non-dot directory name is
   chosen instead, an explicit `norecursedirs` entry becomes mandatory and R2
   must prove it.

## Environment facts

- Python is `py -3.11` (no `python`, no `pwsh`; Windows PowerShell 5.1).
- Console codepage is cp950: decode subprocess output as bytes/UTF-8, never
  `text=True`.
- Working copies are CRLF; mutation and edit scripts must normalize `\r\n`.
