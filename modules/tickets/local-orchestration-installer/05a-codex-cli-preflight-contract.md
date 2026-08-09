# 05A — Codex CLI Contract and Ownership Preflight

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |
| Parent evidence | Superseded Ticket 05; review `593e33a`; CR-80, CR-81, CR-82, CR-84 and CR-85 |
| Baseline | Current control-plane decomposition commit, containing integrated Tickets 01–03 and no production Codex CLI adapter |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-luna`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Single active branch | `codex/implementation-codex-cli-preflight-05a`, created by the implementation owner from the decomposition baseline after preserving the rejected Ticket-05 branch as read-only evidence |
| Environment | Windows user scope; recorded command/filesystem ports only; no live registration, target project, login, Secret, network, packaging, deployment or schedule |

## User-observable outcome

Before any Codex registration mutation, the local installer can report one
finite `ELIGIBLE` or `INSTALL_BLOCKED` preflight result. `ELIGIBLE` requires the
documented Codex CLI version/list schemas, an exact installer-owned local
marketplace source below the canonical install root, and complete absence of
colliding plugin/marketplace identities. Every invalid source, foreign state or
boundary failure blocks with zero CLI mutation and zero target-project access.

This ticket does not register or remove a plugin and does not project Codex as
`SUPPORTED`. Those behaviors are owned by Tickets 05B and 05C.

## Small scope and cumulative ceiling

Authorized production changes are limited to:

```text
library/local_orchestration/host_contracts.py
library/local_orchestration/codex_cli_adapter.py
library/local_orchestration/__init__.py
```

The only authorized test file is:

```text
tests/test_codex_cli_preflight.py
```

- Relative to the decomposition baseline, cumulative net production additions
  must stay at or below 170 non-blank lines and the test file at or below 180.
- Start from the integrated control baseline. Do not copy, cherry-pick or import
  source/tests from rejected Ticket-05 commits `0c2ab95`, `c2ea3f8`, `3f6c41a`
  or `13d02de`; they are review evidence, not an implementation source.
- No optional/`None` port, `Any`, `type: ignore`, hidden config/cache edit,
  command shell string, broad clear/delete or additional abstraction/file.
- If A1–A5 cannot fit, return `BLOCKED / TICKET_DEFECT`; do not expand scope.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05A-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `A1` — public list boundary | Parse plain typed `codex --version` and the documented marketplace/plugin list JSON only. Marketplace entries use required `name`/`root` plus the documented optional source field; plugin list uses required `installed`/`available` collections and documented plugin fields. Reject `{}`, missing/extra fields, `None`, empty, whitespace, wrong types, invalid UTF-8, nonzero output and invented `id`/plugin `root` shapes before any mutation. |
| `A2` — canonical owned source | A strict request carries only an installer-owned relative marketplace-source locator. A required injected filesystem port resolves it against `CANONICAL_INSTALL_ROOT` and returns a recursively revalidated proof containing the same installation identity, canonical root and exact case-sensitive normalized relative locator. Absolute, URI, cwd-relative, traversal, foreign root, prefix/suffix, casing and nominally constructed proof all block. No absolute path enters receipt, Router, telemetry or handoff state. |
| `A3` — collision preflight | Exact structured lists return `ELIGIBLE` only when both requested marketplace and plugin name are absent. Exact duplicate, same plugin name under any other marketplace, same marketplace name at another root/source, copied/stale identity or case variant returns `INSTALL_BLOCKED` before the first mutation. Existing list entries remain byte/value invariant. |
| `A4` — finite boundary failures | Missing executable, access/policy denial, `subprocess.TimeoutExpired`, finite timeout rejection, command `OSError`, filesystem `OSError`, malformed output and unsupported surface map to named finite blocked reasons. No declared process/filesystem exception escapes and no mutation command is invoked. |
| `A5` — evidence truth | Preserve the exact first-red name/reason for A1–A4; run official-schema fixtures, focused/full tests, strict mypy, in-memory no-bytecode compile, source/scope/line checks, `git diff --check` and reverse mutations for schema admission, canonical-root matching, collision blocking and exception mapping. Existing and empty temporary Git repositories must be byte plus porcelain identical. |

## TDD defect classification

- Path-prefix and case boundary: A2/A3 (`CodeReview.md` §2.1 class 1).
- `None`/empty equivalence: A1/A2 (`§2.1` class 2).
- Authority bypass: A2/A3 (`§2.1` class 3).
- Stable error/exception behavior: A1/A4 (`§2.1` classes 5 and 6).
- Test truthfulness: A5 (`§2.1` class 7).
- Token comparison is not applicable; source sentinel must prove no credential or
  token field/comparison was introduced.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05a_20260810` |
| Allocation | `aln_local_orchestration_install_05a_20260810` |
| Receipt | `rcpt_local_orchestration_install_05a_20260810` |
| Correlation / question | `corr-local-orchestration-install-05a-20260810` / `q-local-orchestration-install-05a-20260810` |
| Authority | Owner instruction `開始拆` on 2026-08-10 plus bounded continuation `PRG-20260809-042`; this unique receipt applies only to Ticket 05A |
| Required baseline | The control-plane docs commit containing this decomposition and dispatch |
| Branch/worktree rule | Preserve `codex/implementation-codex-cli-host-adapter-05` and its SHAs as immutable evidence, then use the same sole implementation worktree for exactly one new-ticket branch named above. Do not create another worktree or concurrent branch. |
| Required return | One implementation commit, complete A1–A5 evidence, clean worktree, then one separate docs-only handoff commit. No review/integration/next-ticket decision. |
| Not granted | Ticket 05B/05C/04 source, rejected-source reuse, live Codex mutation, hidden config/cache write, target-project access, Secret, packaging, merge, push, release, deployment or schedule |

## Review convergence rule

The reviewer executes A1–A5 once and batches all findings. At most one additive
correction may occur on the same 05A branch/allocation/receipt. A failed
correction review returns `CONVERGENCE_REVIEW_REQUIRED`; it never creates a
same-ticket branch or worktree.

## Single correction handoff

| Field | Value |
| --- | --- |
| Review / findings | Control review `1cc4e99`; CR-86 through CR-89 in `doc/reviews/local-orchestration-installer/05a-codex-cli-preflight-code-review.md` |
| Correction handoff | `hnd_local_orchestration_install_05a_corr1_20260810` |
| Retained allocation / receipt | `aln_local_orchestration_install_05a_20260810` / `rcpt_local_orchestration_install_05a_20260810` |
| Correlation / question | `corr-local-orchestration-install-05a-corr1-20260810` / `q-local-orchestration-install-05a-corr1-20260810` |
| Required implementation base | Existing branch `codex/implementation-codex-cli-preflight-05a` at docs handoff `67dc1db`; keep implementation `88f7aae` and all evidence immutable and add commits only |
| Required correction | CR-86: exact public `marketplaceSource` type/value DTO on both list-entry types plus strict supported version text. CR-87: exact case-sensitive canonical-root-plus-locator proof and complete path matrix. CR-88: collision across both `installed` and `available`. CR-89: committed missing tests and reproducible per-guard reverse results without rewriting the original red history. |
| Return | One additive correction implementation commit, complete A1..A5 verification within cumulative production/test `170 / 180`, then one separate docs-only correction handoff commit. Return typed `BLOCKED / TICKET_DEFECT` if the frozen closure cannot fit. |
| Still prohibited | New branch/worktree, amend/reset/rebase/force, historical-source reuse, broad clear/delete, optional/`None` ports, `Any`, `type: ignore`, live Codex mutation, target-project access, hidden host state, Ticket 05B/05C/04, merge, push, release, deployment or schedule |
