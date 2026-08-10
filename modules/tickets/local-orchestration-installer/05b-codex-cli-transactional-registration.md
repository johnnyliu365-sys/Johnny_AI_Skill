# 05B — Codex CLI Transactional Registration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `IN_PROGRESS / IMPLEMENTATION_DISPATCHED` |
| Dependency | Satisfied: Ticket 05A independently approved and integrated by `b22c6c4` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Environment | Windows user scope; recorded command/filesystem ports only; no live registration, target project, login, Secret, network, packaging, deployment or schedule |

## User-observable outcome

After an integrated 05A preflight returns `ELIGIBLE`, one registration attempt
adds the exact installer-owned marketplace and plugin in documented order. It
returns a strict `REGISTRATION_VERIFIED` receipt only after official structured
output, observed version and exact manifest proof agree. Any later failure
compensates only current-attempt effects and reports `INSTALL_BLOCKED`; it never
reports success or leaves unverified partial state.

This ticket does not expose the public uninstaller or final `SUPPORTED`
projection; receipt-bound removal and replay are owned by Ticket 05C.

## Scope and cumulative ceiling

Authorized production files are the 05A files plus
`library/local_orchestration/host_lifecycle.py`. The only new test file is
`tests/test_codex_cli_registration.py`.

- Relative to the decomposition baseline, cumulative 05A+05B production must
  stay at or below 310 non-blank lines; cumulative 05A+05B tests at or below 320.
- Use only independently integrated 05A contracts. Rejected parent Ticket-05
  source/tests remain historical evidence and may not be copied or cherry-picked.
- No public removal/replay API, broad cache deletion, optional port, `Any`,
  `type: ignore`, hidden config edit, target-project access or extra file.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05B-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `B1` — official mutations | Use `plugin marketplace add <proved-local-source> --json` then `plugin add <plugin>@<marketplace> --json`. Marketplace-add requires documented `marketplaceName`, `installedRoot`, `alreadyAdded`; plugin-add requires documented `pluginId`, `name`, `marketplaceName`, `version`, `installedPath`, `authPolicy`. Reject `{}`, missing/extra/invented fields and identity mismatch. |
| `B2` — exact receipt | Post-add structured lists and the injected manifest port must prove the exact plugin identity, observed version, canonical root, source locator, installed relative locator and expected SHA-256. Only then issue a receipt bound to current installation, `HostRegistrationKey`, marketplace, plugin and observed fields. Do not invent CLI owner/digest fields or persist absolute paths. |
| `B3` — effect journal before parse | Record marketplace/plugin current-attempt ownership immediately after each zero-exit mutation and before response parsing. Every subsequent validation, list, manifest, timeout, process or filesystem failure invokes exact plugin-then-marketplace compensation for effects that may exist; stale verification cannot skip cleanup. |
| `B4` — verified compensation | Compensation is successful only after exact plugin absence, marketplace absence and current-attempt installed-path absence are independently verified. Remove failure, malformed remove output, stale list/path state or foreign state remains `INSTALL_BLOCKED` with bounded retry authority and never reports registered/absent. Unrelated entries remain invariant. |
| `B5` — evidence truth | Preserve first-red names/reasons for B1–B4; cover official fixtures and a failure injected before/after every effect/parse/proof boundary. Run focused/full tests, strict mypy, no-bytecode compile, cumulative line/scope/source checks, byte+porcelain Git isolation and reverse mutations for mutation DTOs, receipt binding, effect timing, order and terminal compensation. |

## TDD defect classification

- Path-prefix/case boundary: B2/B4 (`CodeReview.md` §2.1 class 1).
- `None`/empty equivalence: B1/B2 (`§2.1` class 2).
- Authority bypass: B2/B3/B4 (`§2.1` class 3).
- Stable error and exception behavior: B3/B4/B5 (`§2.1` classes 5 and 6).
- Test truthfulness: B5 (`§2.1` class 7).
- Token comparison is not applicable; the source sentinel must prove no
  credential/token field or comparison was introduced.

## Completion and rollback boundary

Completion requires one ticket-only implementation commit, B1–B5 red/green and
reverse evidence, focused/full regression, strict typing, compile, cumulative
scope/line checks, byte+porcelain Git isolation, clean status and a separate
docs-only handoff. The only rollback is B3/B4 exact current-attempt
compensation. A compensation proof failure remains blocked and retryable; it
does not authorize manual cache deletion, another plugin removal or live repair.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05b_20260810` |
| Allocation | `aln_local_orchestration_install_05b_20260810` |
| Receipt | `rcpt_local_orchestration_install_05b_20260810` |
| Correlation / question | `corr-local-orchestration-install-05b-20260810` / `q-local-orchestration-install-05b-20260810` |
| Authority | Owner instruction `可以開始派工` on 2026-08-10 plus approved program authority `PRG-20260809-042`; this unique receipt applies only to Ticket 05B |
| Required baseline | The control-plane docs commit containing this dispatch, whose parent is integrated baseline `10c2080`; branch `codex/implementation-codex-cli-registration-05b` must start at that exact dispatch commit |
| Branch/worktree rule | In the same sole implementation worktree, first prove the 05A branch is clean at `fb755268`, preserve it as immutable evidence, then create exactly the named 05B branch. Do not create another worktree, delete a branch or reuse rejected Ticket-05 source. |
| Required scope | B1–B5 only, using the independently integrated 05A contracts; authorized production is limited to the 05A files plus `host_lifecycle.py`, and the only new test file is `test_codex_cli_registration.py` within cumulative `310 / 320` ceilings |
| Required return | One ticket-only implementation commit, complete B1–B5 evidence and cache-free clean state, then one separate docs-only handoff commit. Return typed `BLOCKED` or `CHANGE_DETECTED` with concrete evidence if the closure cannot be completed. No review/integration/next-ticket decision. |
| Not granted | Ticket 05C/04 source, public removal/replay, live Codex mutation, broad clear/delete, optional/`None` port, `Any`, `type: ignore`, hidden host/config/cache write, target-project access, network/login/Secret, packaging, merge, push, release, deployment or schedule |

## Review and handoff boundary

Ticket 05B is the sole selected implementation lane. The delivery confirmation
for `q-local-orchestration-install-05b-20260810` starts only this receipt-bound
lane. Independent review follows the implementation/docs handoff; any correction
is additive on this same 05B branch and never creates another branch or worktree.
