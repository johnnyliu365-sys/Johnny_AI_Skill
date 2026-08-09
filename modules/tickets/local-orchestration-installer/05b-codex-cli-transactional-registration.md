# 05B — Codex CLI Transactional Registration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Dependency | Ticket 05A independently approved and integrated |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-luna`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree after a future unique dispatch |
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

## Review and future handoff boundary

Ticket 05B remains `PLANNED` until 05A is integrated. Its future handoff must
create a new ticket-bound receipt and exactly one active branch in the same sole
implementation worktree. No current implementation authority is granted by this
planning document.
