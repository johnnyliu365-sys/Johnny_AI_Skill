# Antigravity Distribution — Ticket Registry

| Field | Binding |
| --- | --- |
| Requirement | Owner directive 2026-08-19: the plugin installs into Claude Code **and** Antigravity, so the owner stops retyping instructions each session |
| Baseline | `main` = `c981973` |
| Authority | Owner-direct allocation, same mode as the live-install L-line |
| Boundary | Per-user customization roots only. No company repository is modified; foreign entries in shared config files are preserved byte-for-byte |

| # | Ticket | State |
| --- | --- | --- |
| A1 | Antigravity plugin surface + registration/removal | `OPEN` — awaiting a named implementation owner |

## Claude Code status (no ticket needed)

Already installable today: `.claude-plugin/marketplace.json` and
`.claude-plugin/plugin.json` are both present and the two skills
(`johnny-project-takeover`, `apply-reusable-modules`) live in the shared root
`skills/`. Nothing is installed on this machine yet (`~/.claude` has no
`plugins/`), but that is an owner action, not an engineering gap.
