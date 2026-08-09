# 05A — Codex CLI Contract and Ownership Preflight

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `COMPLETE / APPROVED / READY_TO_MERGE` |
| Parent evidence | Superseded Ticket 05; review `593e33a`; CR-80, CR-81, CR-82, CR-84 and CR-85 |
| Baseline | Current control-plane decomposition commit, containing integrated Tickets 01–03 and no production Codex CLI adapter |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, current model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree; the original and first-correction Luna runs remain immutable evidence |
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
  must stay at or below 180 non-blank lines and the test file at or below 180.
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

## Owner-scoped convergence override and final correction handoff

The owner instruction on 2026-08-10 to re-check the submitted correction and
re-dispatch according to the verified result is the explicit, single-use
override contemplated by the correction review. It does not weaken A1–A5 or
authorize another review loop. It permits exactly one final additive repair on
the existing branch/worktree; the parent cluster ceiling remains `400 / 450`.

| Field | Value |
| --- | --- |
| Reconfirmation | Control review `277a0d0` plus a fresh independent run: focused `13/13`, full `169/169`, strict mypy `82` files and in-memory compile pass; explicit-null, parsed-version and relative-root probes fail exactly as recorded |
| Final handoff | `hnd_local_orchestration_install_05a_corr2_owner_20260810` |
| Retained allocation / receipt | `aln_local_orchestration_install_05a_20260810` / `rcpt_local_orchestration_install_05a_20260810` |
| Correlation / question | `corr-local-orchestration-install-05a-corr2-owner-20260810` / `q-local-orchestration-install-05a-corr2-owner-20260810` |
| Required implementation base | Existing branch `codex/implementation-codex-cli-preflight-05a` at docs handoff `59c3f96`; preserve `88f7aae`, `67dc1db`, `b6594b9` and `59c3f96`, then add commits only |
| Exact repair | Reject explicitly present `marketplaceSource: null` on both official DTOs while preserving field absence; return semantic version capture only; require the expanded canonical root and resulting proof path to be absolute Windows paths before exact case-sensitive equality; add the three omitted observable tests and truthful reverse evidence |
| Ceiling | Cumulative production/test `180 / 180`; use readable named validation and return typed `BLOCKED / TICKET_DEFECT` rather than compressing away a contract |
| Required return | One final additive implementation commit, complete A1–A5 verification and one separate docs-only handoff. The implementation owner makes no review or integration decision. |
| Terminal rule | The following independent review must be `APPROVED`, or stop this lane as `BLOCKED / SUPERSEDE_REQUIRED`; no further same-ticket implementation correction is authorized. |

## Terminal review result

Final implementation `97ab31c` closes executable A1 through A4 and passes the
focused/full/type/compile/scope/adversarial/reverse checks. A5 does not close:
ignored `.mypy_cache` state was rewritten during the implementation turn while
the handoff claimed no hidden-state write, and the docs-only handoff `4fc81a5`
reuses canonical progress ID `PRG-20260810-087`.

The terminal conclusion is `BLOCKED / SUPERSEDE_REQUIRED`. Allocation and
receipt are not valid for another 05A correction. No implementation dispatch,
new branch/worktree, integration or dependent-ticket start is authorized.

## One-time evidence cleanup exception

The owner explicitly authorizes one evidence-only continuation from `4fc81a5`
in the existing implementation worktree and branch. Handoff
`hnd_local_orchestration_install_05a_evidence_cleanup_20260810`, allocation
`aln_local_orchestration_install_05a_evidence_cleanup_20260810` and receipt
`rcpt_local_orchestration_install_05a_evidence_cleanup_20260810` apply only to:

1. removing generated `.mypy_cache`, `.pytest_cache` and `__pycache__`
   directories that resolve beneath the assigned implementation worktree;
2. rerunning verification with mypy cache redirected to a unique OS-temporary
   directory, then proving both tracked and ignored state are clean;
3. one additive docs-only commit that changes the branch-local duplicate
   `PRG-20260810-087` heading to reserved `PRG-20260810-091`, corrects the
   hidden-state claim and records the cleanup evidence.

No source/test edit, implementation commit, new branch/worktree, history
rewrite, integration or dependent ticket is authorized. The following review
is restricted to CR-90, CR-91 and A5.

## Evidence cleanup review result

Control review of repaired docs-only handoff `fb755268` independently passed
focused `16/16`, full `172/172`, strict mypy across `82` files using a removed
OS-temporary cache, four-file in-memory compile, the exact source sentinel and
diff check. Both tracked and ignored status are empty and no allowed generated
cache remains beneath the implementation worktree. `PRG-20260810-091` is unique
to the branch handoff, while canonical control record `PRG-20260810-087`
remains distinct. CR-90, CR-91 and A5 are closed; the ticket is
`APPROVED / READY_TO_MERGE` pending a separate guarded integration decision.
