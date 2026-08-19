# A1 — Antigravity Plugin Surface, Registration and Removal

| Field | Value |
| --- | --- |
| Requirement | Owner directive 2026-08-19: Antigravity must load the Johnny skills without the owner retyping instructions each session |
| State | `OPEN` — awaiting a named implementation owner |
| Baseline | `main` = `c981973` |
| Workload | `STANDARD`; the removal path touches a shared user config file and is reviewed at `HIGH_ASSURANCE` depth |
| Language / XSS | Python 3.11 strict Pydantic/mypy + JSON / `XSS_NOT_APPLICABLE` |

## One outcome

Antigravity loads `johnny-project-takeover` and `apply-reusable-modules` in
every session without the owner restating them, and a removal path takes that
registration away again while leaving every customization the owner did not
install untouched.

## Verified platform facts (control plane, 2026-08-19)

Read from Antigravity's own shipped documentation at
`~/.gemini/antigravity-ide/builtin/skills/agy-customizations/docs/`. Two
Antigravity installations share these roots: `~/.gemini/antigravity` and
`~/.gemini/antigravity-ide`; the customization roots below are common to both.

- A plugin is a subdirectory of a `plugins/` folder inside a customization root
  (project `.agents/`, or `~/.gemini/config/` globally):

  ```text
  plugins/<plugin_name>/
  ├── plugin.json       # required marker; {"name": "..."} , name optional
  ├── mcp_config.json   # optional
  ├── hooks.json        # optional
  ├── rules/*.md        # optional
  └── skills/<skill_name>/SKILL.md
  ```

- `skills.json` and `plugins.json` live in a customization root and share one
  schema: `{"entries": [{"path": ..., "include_only": [...], "exclude": [...]}],
  "inherits": [...]}`.
- **Path resolution**: `/` absolute, `~/` home-relative, and anything else is
  resolved **relative to the repository root** (the folder containing `.git`).
- Skill format is already compatible: Antigravity reads `SKILL.md` with `name:`
  and `description:` frontmatter, exactly like the existing root `skills/`.
  Its extra `metadata:` block is optional.

## Frozen responsibility

- **One source of truth for skill content.** The root `skills/` tree stays
  canonical. Do not copy the skills into a second directory: two trees drift.
  Prefer a `skills.json`/`plugins.json` `entries` path that points at the
  canonical tree. If any copy proves unavoidable, a regression must pin the two
  trees byte-identical and fail on drift.
- **Symlinks are forbidden.** `build_payload_manifest` raises on a symlink
  inside a payload tree (`payload tree contains a symlink`), so a symlinked
  skills directory would break the release bundle. Windows symlink creation
  also needs privileges the installer must not require.
- **Foreign customizations are preserved.** Registration and removal edit
  shared user config files. Every entry the owner did not install must survive
  byte-for-byte, including on the removal path. Removal is idempotent and never
  deletes a config file it did not create.
- Per-user scope only. No admin rights, no PATH change, no company-repository
  effect.
- Removal must be provable: a readback shows the Johnny entry absent and the
  foreign entries unchanged.

## Open question the implementer must resolve first

`.agents/plugins/marketplace.json` already exists in this repository and
declares a `plugins[].source.url` pointing at the GitHub repo with
`policy.installation`/`policy.authentication` fields. **That shape appears in
no Antigravity documentation shipped on this machine**, which documents only
`plugin.json`, `plugins.json` and `skills.json`. Determine whether this file is
a real (newer or private) Antigravity marketplace format, a speculative draft,
or a mis-copied Claude Code convention — then either bind it as the install
route or remove it. Do not build on it until its status is proven.

## Authorized implementation scope

```text
.agents/
library/local_orchestration/          # registration and removal ports
tests/
README.md                             # Antigravity install section
modules/tickets/antigravity-distribution/
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `A1-R1` | The open question above is resolved with evidence, and the chosen install route is stated before any code is written. |
| `A1-R2` | A real Antigravity session loads both skills with no per-session instruction from the owner. Evidence is a readback from the running product, not a file listing. |
| `A1-R3` | Skill content has exactly one source of truth. If a second tree exists, a regression proves byte-equality and turns red on drift. |
| `A1-R4` | Registration is idempotent: running it twice leaves one entry, not two. |
| `A1-R5` | Removal takes the Johnny entry away and leaves pre-existing foreign entries byte-identical. Proven with a config file that already carries foreign entries before the test runs. |
| `A1-R6` | A clean-clone bundle build still returns `BUNDLED`, and the payload manifest contains no symlink. |
| `A1-R7` | `mypy --strict` clean; full suite green; `tests/.johnny-runtime` zero residue. |

## Environment facts

- Python is `py -3.11` (no `python`, no `pwsh`; Windows PowerShell 5.1).
- Console codepage is cp950: decode subprocess output as bytes/UTF-8, never
  `text=True`.
- Working copies are CRLF; mutation and edit scripts must normalize `\r\n`.
- Worktrees follow ticket `workflow-governance/02`: create them under the
  repository root, never as a sibling folder.
