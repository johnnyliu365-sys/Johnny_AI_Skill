# 05B — Codex CLI Transactional Registration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED / REVISION_02_FROZEN / OWNER_DISPATCH_REQUIRED` |
| Dependency | Satisfied: Ticket 05A independently approved and integrated by `b22c6c4` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Implementation language | Python 3.11, as fixed by the approved SPEC; this field was missing from closure revision 01 and is repaired by the control-plane review |
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

The independently integrated 05A baseline is `b22c6c4`, measured as `177`
production and `171` test non-blank lines relative to the decomposition
baseline. Revision 02 permits changes only to:

```text
library/local_orchestration/host_contracts.py
library/local_orchestration/codex_cli_adapter.py
library/local_orchestration/__init__.py
tests/test_codex_cli_preflight.py
tests/test_codex_cli_registration.py
```

- Final cumulative 05A+05B production must stay at or below `460` non-blank
  lines and their two test files at or below `540`. This replaces the defective
  `310 / 320` ceiling; it is not authority for Ticket 05C or another file.
- The submitted `305 / 299` result is evidence, not a target. Deleting or
  rewriting compressed 05B lines in an additive correction commit is allowed;
  resetting, amending or discarding commits is not.
- Every changed declaration and transaction step must use readable named types,
  helpers and one statement per line. Semicolon-combined imports, assignments,
  conditions, returns or enum members fail the P0 readability gate.
- Use only integrated 05A contracts. Rejected parent Ticket-05 source/tests
  remain historical evidence and may not be copied or cherry-picked.
- No public removal/replay API, broad cache deletion, optional/`None` port,
  `Any`, `type: ignore`, hidden config edit, target-project access or extra file.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05B-02`

The official Codex CLI field surface is the current
[OpenAI command reference](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli):
marketplace add yields `marketplaceName`, `installedRoot`, `alreadyAdded`; plugin
add yields `pluginId`, `name`, `marketplaceName`, `version`, `installedPath`,
`authPolicy`. These raw path fields are ephemeral proof inputs and are never
persisted in a receipt.

| ID | Required first-red and green behavior |
| --- | --- |
| `B1` — request-bound fresh admission | `CodexPreflightEligible` binds the exact `CodexPreflightRequest` and observed CLI version. Registration recursively revalidates equality with the current request, then freshly resolves the exact source and reruns marketplace plus installed/available plugin collision checks immediately before the first mutation. A cloned/mismatched eligibility value, source mismatch or fresh collision blocks with zero mutation. |
| `B2` — official add proof and distinct receipt | After fresh admission, call exact marketplace add then plugin add. Strict DTOs reject `{}`, missing/extra/null/empty fields and identity mismatch. Both complete add DTOs enter the injected manifest proof boundary. It must prove that observed `installedRoot`, `installedPath` and `authPolicy` map to the exact request-owned relative locators/policy, version and digest. A separate `CodexRegistrationReceipt` binds installation, canonical key/root, marketplace, plugin, observed version, relative source/installed locators, auth policy and digest; it contains no absolute path. |
| `B3` — typed current-attempt journal | Marketplace and plugin use separate finite states `NOT_ATTEMPTED`, `MAY_EXIST`, `OWNED`, `PREEXISTING`. Mark `MAY_EXIST` immediately before each effectful command; a valid current-attempt response confirms `OWNED`. Marketplace `alreadyAdded=true` becomes `PREEXISTING`, blocks, and grants no removal authority. Timeout, nonzero, zero-exit parse/schema/identity failure after an attempted mutation retains `MAY_EXIST`; plugin uncertainty compensates plugin before marketplace. Pre-command invalid input/port/source/collision grants no effect authority. |
| `B4` — exhaustive verified compensation | For each journaled `MAY_EXIST` or `OWNED` effect, attempt exact plugin then marketplace removal without short-circuiting after one failure. Plugin removal strictly binds `pluginId`, `name`, `marketplaceName`; marketplace removal strictly binds `marketplaceName`, `installedRoot` through the same ephemeral path-proof boundary. Fresh exact plugin absence, marketplace absence and installed-path absence must all pass. Every remove/list/parse/proof failure or residue remains `INSTALL_BLOCKED / COMPENSATION_FAILED` with only the exact unresolved effect states. Never remove `PREEXISTING` or unrelated entries and never report registered/absent from stale proof. |
| `B5` — finite evidence truth | The numbered matrix below is the complete required failure surface. Preserve first-red names/reasons, make every cell green, and retain one isolated reverse mutation for each of B1, B2, B3, B4 and B5. Run focused/full tests, strict full-tree mypy, in-memory no-bytecode compile, source/scope/line/diff checks, byte-plus-porcelain Git isolation and final tracked/ignored/cache absence. Claims must quote the exact commands and counts actually run. |

## Finite TDD and fault matrix

Each row is a required named test or a finite `subTest` table; “each field” means
only the fields explicitly listed in that row.

| Cell | Required injected cases and terminal assertion |
| --- | --- |
| `M01` | Eligible request mismatch for installation, root, source, marketplace or plugin: `INSTALL_BLOCKED`, no mutation command. |
| `M02` | Fresh source proof mismatch for installation/root/locator/absolute ownership, plus source-port validation or filesystem failure: blocked before mutation. |
| `M03` | Fresh marketplace collision, installed-plugin collision and available-plugin collision, including case variants: blocked before mutation. |
| `M04` | Marketplace-add executable unavailable, access denied, timeout, nonzero and generic process error: finite reason; only timeout/nonzero/generic attempted outcomes may retain marketplace `MAY_EXIST` removal authority. |
| `M05` | Marketplace-add `{}`, extra field, null/empty text, each missing field (`marketplaceName`, `installedRoot`, `alreadyAdded`), foreign identity/root and `alreadyAdded=true`: blocked; `true` performs no removal. |
| `M06` | Plugin-add executable unavailable, access denied, timeout, nonzero and generic process error: finite reason; an attempted/ambiguous plugin is compensated before any owned marketplace. |
| `M07` | Plugin-add `{}`, extra field, null/empty text, each missing field (`pluginId`, `name`, `marketplaceName`, `version`, `installedPath`, `authPolicy`) and foreign identity/version/path/auth: blocked and compensated from the typed journal. |
| `M08` | Post-add marketplace-list timeout, nonzero, malformed/extra output, missing exact entry and foreign identity: blocked and compensated. |
| `M09` | Post-add plugin-list timeout, nonzero, malformed/extra output, missing/disabled exact entry and foreign identity/version: blocked and compensated. |
| `M10` | Manifest port exception or malformed proof, then mismatch of installation, registration key, root, marketplace, plugin, version, source locator, installed locator, auth policy or digest: blocked and compensated. |
| `M11` | Exact success proves both add DTOs reached the manifest boundary; the distinct receipt contains every required typed relative/identity field and no absolute path. |
| `M12` | Plugin-remove timeout, nonzero, `{}`, extra field, each missing field (`pluginId`, `name`, `marketplaceName`) and identity mismatch: marketplace removal and all three absence probes still run; unresolved plugin authority remains. |
| `M13` | Marketplace-remove timeout, nonzero, `{}`, extra field, each missing field (`marketplaceName`, `installedRoot`) and identity/root mismatch: all absence probes still run; unresolved marketplace authority remains. |
| `M14` | Marketplace-absence list timeout, nonzero, malformed/extra output or exact residue: `COMPENSATION_FAILED`. |
| `M15` | Plugin-absence list timeout, nonzero, malformed/extra output, exact installed/available residue or disabled residue: `COMPENSATION_FAILED`. |
| `M16` | Installed-path absence port exception, malformed proof, foreign installation/root/locator/digest or `absent=false`: `COMPENSATION_FAILED`. |
| `M17` | Unrelated marketplace/plugin entries remain byte/value identical across success failure, compensation failure and bounded retry; retry contains only unresolved current-attempt states. |
| `M18` | Existing and empty temporary Git repositories remain file-byte and `git status --porcelain` identical; source sentinel rejects prohibited constructs and semicolon-compressed changed code. |

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

## Historical revision-01 implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05b_20260810` |
| Allocation | `aln_local_orchestration_install_05b_20260810` |
| Receipt | `rcpt_local_orchestration_install_05b_20260810` |
| Correlation / question | `corr-local-orchestration-install-05b-20260810` / `q-local-orchestration-install-05b-20260810` |
| Authority | Owner instruction `可以開始派工` on 2026-08-10 plus approved program authority `PRG-20260809-042`; consumed by closure revision 01 only |
| Required baseline | Dispatch `f68d9d6`; branch `codex/implementation-codex-cli-registration-05b` |
| Preserved return | Implementation `5e919069`; docs-only handoff `ef1cf42`; both are immutable review evidence |
| Current status | Inactive. It does not authorize revision-02 correction work. |
| Not granted | Ticket 05C/04 source, public removal/replay, live Codex mutation, broad clear/delete, optional/`None` port, `Any`, `type: ignore`, hidden host/config/cache write, target-project access, network/login/Secret, packaging, merge, push, release, deployment or schedule |

## Revision-02 correction and handoff boundary

- Refreezing this ticket is documentation work only. It creates no correction
  handoff and sends no instruction to the implementation task.
- A future explicit owner dispatch may reactivate the retained allocation and
  receipt only through a new revision-02 correction handoff bound to the exact
  control-plane refreeze commit and branch HEAD `ef1cf42` after clean-state
  readback.
- That handoff must keep task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, the sole
  implementation worktree and branch
  `codex/implementation-codex-cli-registration-05b`. No new branch/worktree,
  reset, amend, force operation or history replacement is permitted.
- Exactly one additive source/test correction commit and one separate docs-only
  handoff may be returned. The following independent review is terminal for
  revision 02: failure pauses the lane without another automatic dispatch.

## Initial independent review result

Review `doc/reviews/local-orchestration-installer/05b-codex-cli-transactional-registration-code-review.md`
records `BLOCKED / TICKET_DEFECT` for implementation `5e919069` and handoff
`ef1cf42`. CR-92 through CR-97 are batched against B1–B5. The submitted green,
full regression, strict type, compile and numerical scope results reproduce,
but foreign observed add fields can produce success, cloned admission can
authorize another installation, and compensation can delete a pre-existing
marketplace while skipping a possibly-created plugin after timeout.

Closure revision 02 above resolves CR-92 by fixing Python 3.11, enumerating the
finite M01–M18 matrix and replacing the compression-inducing ceiling with the
bounded `460 / 540` cumulative ceiling. It does not close CR-93 through CR-97;
those remain the exact implementation/evidence correction scope if the owner
later dispatches revision 02. The existing branch, allocation and receipt remain
inactive evidence until then; no new branch or worktree is authorized.
