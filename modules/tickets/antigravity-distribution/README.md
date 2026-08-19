# Antigravity Distribution — Ticket Registry

| Field | Binding |
| --- | --- |
| Requirement | Owner directive 2026-08-19: the plugin installs into Claude Code **and** Antigravity, so the owner stops retyping instructions each session |
| Baseline | `main` = `c981973` |
| Authority | Owner-direct allocation, same mode as the live-install L-line |
| Boundary | Per-user customization roots only. No company repository is modified; foreign entries in shared config files are preserved byte-for-byte |

| # | Ticket | State |
| --- | --- | --- |
| A1 | Antigravity plugin surface + registration/removal | `CLOSED` — owner-executed 2026-08-19; A1-R1/R3/R4/R5/R6/R7 green (9 tests). A1-R2 satisfied by owner readback from a running Antigravity session, which listed `johnny-project-takeover` and `apply-reusable-modules` among its loaded skills alongside the built-in and Chrome DevTools plugin skills, proving the global `skills.json` entry is ingested. |

## Claude Code status (no ticket needed)

Already installable today: `.claude-plugin/marketplace.json` and
`.claude-plugin/plugin.json` are both present and the two skills
(`johnny-project-takeover`, `apply-reusable-modules`) live in the shared root
`skills/`. Nothing is installed on this machine yet (`~/.claude` has no
`plugins/`), but that is an owner action, not an engineering gap.

## A1-R2 readback (2026-08-19)

A running Antigravity session enumerated its loaded skills and returned both
Johnny skills by name and description, grouped with the built-in
`agy-customizations` / `antigravity-guide` / `google-antigravity-sdk` skills:

```text
apply-reusable-modules   選用 Johnny AI Skill 可重用模組
johnny-project-takeover  專案接管與規範工作流程
```

This is product-level evidence, not a file listing: the entry written to
`~/.gemini/config/skills.json` is discovered and ingested, and the canonical
`skills/` tree is read in place with no copy anywhere.

Two Antigravity installations exist on this host (`Antigravity` and
`Antigravity IDE`). They keep separate state under `~/.gemini/antigravity` and
`~/.gemini/antigravity-ide` but share the global customization root
`~/.gemini/config/`, so one registration covers both.

Discovery note recorded during the readback: Antigravity loads `GEMINI.md` and
`AGENTS.md` as hierarchical Rules. This repository already ships `AGENTS.md`,
so the worktree-placement rule added in governance 02 reaches Antigravity
directly, without depending on the plugin surface.
