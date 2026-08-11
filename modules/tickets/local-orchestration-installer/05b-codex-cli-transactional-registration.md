# 05B — Codex CLI Transactional Registration

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `SUPERSEDED / CONVERGENCE_DECOMPOSED / IMMUTABLE_REJECTED_EVIDENCE` — replaced by 05B1 through 05B4; no old allocation or branch authority |
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

## Scope

The independently integrated 05A baseline is `b22c6c4`. Revision 02 permits
changes only to:

```text
library/local_orchestration/host_contracts.py
library/local_orchestration/codex_cli_adapter.py
library/local_orchestration/__init__.py
tests/test_codex_cli_preflight.py
tests/test_codex_cli_registration.py
```

- Numeric source/test line ceilings were introduced by the control plane and
  were never an owner requirement. They are superseded as a quality or
  acceptance gate. Diff size may be reported as information only; scope is
  bounded by the files, behavior, contracts and finite closure in this ticket.
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
| `B5` — finite evidence truth | The numbered matrix below is the complete required failure surface. Preserve first-red names/reasons, make every cell green, and retain one isolated reverse mutation for each of B1, B2, B3, B4 and B5. Run focused/full tests, strict full-tree mypy, in-memory no-bytecode compile, source/scope/diff checks, byte-plus-porcelain Git isolation and final tracked/ignored/cache absence. Claims must quote the exact commands and counts actually run. |

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
reverse evidence, focused/full regression, strict typing, compile, exact scope
checks, byte+porcelain Git isolation, clean status and a separate
docs-only handoff. The only rollback is B3/B4 exact current-attempt
compensation. A compensation proof failure remains blocked and retryable; it
does not authorize manual cache deletion, another plugin removal or live repair.

## Authority and review references

| Stage | Identifiers / state |
| --- | --- |
| Revision 01 dispatch | `PRG-20260810-095`; `hnd_local_orchestration_install_05b_20260810`; `aln_local_orchestration_install_05b_20260810`; `rcpt_local_orchestration_install_05b_20260810`; `corr-local-orchestration-install-05b-20260810`; branch `codex/implementation-codex-cli-registration-05b` |
| Revision 01 review | `5e919069`; `ef1cf42`; `PRG-20260810-097`; `f02704f`; `CR-92..CR-97` |
| Revision 02 refreeze | `PRG-20260810-098`; `a7dd4a4`; `CLOSURE-LOCAL-INSTALL-T05B-02` |
| Revision 02 correction | `PRG-20260810-099`; `hnd_local_orchestration_install_05b_corr1_r02_20260810`; retained allocation/receipt above; `corr-local-orchestration-install-05b-corr1-r02-20260810`; starting HEAD `ef1cf42` |
| Terminal return | Implementation `1a26941176b4ce3c122c41644817e3429cb7c8a5`; handoff `ed74589c12072d5d70e168735e6ccc440c681ced` |
| Authoritative review | `PRG-20260810-101`; control commit `24227ac`; `doc/reviews/local-orchestration-installer/05b-codex-cli-transactional-registration-code-review.md`; `CR-98..CR-104` |
| Current state | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`; all prior dispatch authority is consumed/inactive; no automatic continuation |

## Post-staging convergence decomposition

Owner instructions to build isolation first and split the stuck ticket are now
actionable because 05S1-05S4 are independently integrated. This parent and its
rejected commits remain immutable evidence; they are not reopened.

1. `05B1` defines strict observed-add proof, metadata-only receipt and
   current-attempt journal contracts with no effects.
2. `05B2` classifies command-start truth and produces journal transitions
   without granting authority on pre-command unavailable/access-denied cases.
3. `05B3` performs exhaustive plugin-first compensation and all three fresh
   absence proofs, returning only unresolved effects.
4. `05B4` composes fresh 05A admission, 05B1-05B3 and the 05S4 oracle into the
   full registration result and finite M01-M18 evidence.

Each child receives a unique closure, allocation and receipt. Only 05B1 is
currently dispatched; later children remain dependency-waiting.
