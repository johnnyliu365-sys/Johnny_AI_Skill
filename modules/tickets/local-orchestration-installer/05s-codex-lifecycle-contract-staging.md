# 05S — Codex Lifecycle Contract Staging

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07, AC-08 and Test seams 2, 3, 5, 6 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011`; verification-architecture revision approved by the owner on 2026-08-10 |
| State | `IN_PROGRESS / CHANGES_REQUESTED / REVISION_02_CORRECTION_PREPARED` |
| Dependency | Ticket 05A independently approved and integrated by `b22c6c4` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Implementation language | Python 3.11 with strict typing |
| Environment | Disposable test-owned process/filesystem sandbox only; no live Codex CLI state, Windows package installation, user profile/configuration, target project, network, login, Secret, push or deployment |

## User-observable outcome

A reviewer can run one bounded command that provisions a disposable Codex CLI
contract environment, executes a real child process against persisted sandbox
state, observes exact marketplace/plugin add, list, remove and absence results,
then destroys the sandbox. A post-effect failure leaves observable residue until
an explicit matching removal is performed. Unrelated state and two synthetic Git
repositories remain unchanged.

This ticket creates the missing verification environment; it does not repair or
integrate Ticket 05B. After 05S is independently approved and integrated, the
control plane must refreeze 05B, 05C and Ticket 04 against its evidence. A full
Windows user-profile sandbox remains a separate Ticket-04 packaging gate.

## Architecture and truth boundary

- The sandbox owns one unique OS-temporary root outside both repository
  worktrees. It contains a test-only executable shim, strict persisted state,
  source/installed payload copies and unrelated sentinels.
- Commands cross a real `subprocess` boundary. A test-only command port replaces
  only the executable token with the exact sandbox shim; it never invokes the
  host `codex` executable and never edits global `PATH`, `%LOCALAPPDATA%`, Codex
  configuration or registry state.
- List, add, remove and absence results are reconstructed from freshly loaded,
  recursively validated persisted state. Success/absence proof must not be
  generated from the caller request, queued response or stale snapshot.
- Finite fault injection is a strict enum recorded in sandbox state. A
  post-effect fault is applied only after the state/file effect is durably
  observable; a pre-effect fault produces no state authority.
- The operator-facing evidence projection contains only scenario/result enums,
  command identifiers, relative owned locators, digests and presence booleans.
  It contains no absolute path, raw prompt, target-project data, Secret or PII.

## Scope

Production `library/local_orchestration` source is read-only for this ticket.
Implementation is limited to the following new test-support surface plus the
separate docs-only handoff:

```text
tests/staging/__init__.py
tests/staging/codex_lifecycle/__init__.py
tests/staging/codex_lifecycle/contracts.py
tests/staging/codex_lifecycle/sandbox.py
tests/staging/codex_lifecycle/shim.py
tests/test_codex_lifecycle_staging.py
doc/WorkProgressReport.md
```

No hard line-count limit applies. Scope is controlled by the named behavior,
files, strong types and finite closure. Do not add `Any`, `type: ignore`,
optional/`None` effect ports, shell command strings, broad clear/delete,
Docker/VM/Windows-Sandbox provisioning, product-adapter changes, historical
Ticket-05 source, a second worktree or a live host mutation.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `S1` — disposable provision | Provisioning creates one unique external temporary root, a test-only executable and recursively strict empty state. The root is not beneath either repository worktree and no global environment/configuration value is changed. Invalid/relative/reused roots fail before process or filesystem effects. |
| `S2` — stateful successful lifecycle | A real child-process sequence observes empty lists, adds the exact marketplace, adds the exact plugin/payload, observes both installed, removes plugin before marketplace, then freshly observes plugin, marketplace and installed path absent. Outputs match the documented structured field surface used by 05A/05B/05C. |
| `S3` — independent truth | After every effect, fresh list/absence results come from reloaded state and actual sandbox files. Mutating the request or a previous response cannot change observed truth. Corrupt, missing, extra, null, foreign or stale state blocks rather than fabricating success/absence. |
| `S4` — effect timing | A finite pre-effect failure creates no state. A finite post-marketplace or post-plugin failure leaves exactly the effected state observable. Matching explicit removal clears only that state; a removal failure leaves residue visible for retry. |
| `S5` — foreign-state isolation | Pre-seeded unrelated marketplace/plugin entries and sentinel files remain byte/value identical through success, failure, compensation and retry. Same-name foreign ownership is never silently overwritten or removed. |
| `S6` — target and host isolation | Existing and empty synthetic Git repositories remain byte-plus-porcelain identical. The test records the exact child executable and proves it is the sandbox shim; the live `codex` executable, user Codex state and real target projects receive no call or write. |
| `S7` — teardown and evidence truth | Teardown validates the exact sandbox root and removes it; final readback proves absence. Focused/full tests, strict full-tree mypy with repository-external removed cache, in-memory compile, source sentinel, `git diff --check`, reverse mutations and tracked/ignored/cache readback all pass. Claims report exact commands/counts and do not invent retroactive first-red evidence. |

## Finite scenario matrix

| Cell | Scenario and terminal assertion |
| --- | --- |
| `E01` | Clean full lifecycle: exact add/list/remove/absence order and final root teardown. |
| `E02` | Marketplace pre-effect versus post-effect failure: respectively no entry versus one freshly listable owned entry. |
| `E03` | Plugin pre-effect versus post-effect failure: respectively no plugin versus one freshly listable installed plugin/path. |
| `E04` | Plugin-removal and marketplace-removal failure independently retain only their actual residue and permit bounded retry. |
| `E05` | Corrupt/missing/extra/null/stale persisted state and file/state disagreement never report installed or absent success. |
| `E06` | Unrelated and same-name foreign entries are preserved; exact owned identity alone can mutate. |
| `E07` | Request/response mutation after an effect does not alter fresh list or path truth. |
| `E08` | Synthetic Git bytes/porcelain, live-host call sentinel, global environment and both repository worktrees remain invariant; exact teardown removes only the sandbox root. |

## Revision-02 correction closure — `CLOSURE-LOCAL-INSTALL-T05S-02`

This section supersedes revision 01 wherever the two differ. It is the one
additive correction permitted after the independent review of `18b99de` and
`2bed349`. Existing commits remain immutable evidence.

| ID | Required correction behavior |
| --- | --- |
| `C1` — relocatable, exception-safe provisioning | Tests accept explicit existing forbidden roots and run from any checkout/CI location without a fixed sibling name. Validate and resolve all forbidden roots before `mkdtemp` or `mkdir`; store their resolved values. Any validation or initialization exception removes only the exact newly created marked root and leaves no staging residue. Teardown remains valid if the caller later moves or removes a forbidden root. |
| `C2` — injectable bounded command port | Add a strict test-only port that satisfies the current `CodexCommandPort` protocol. It accepts the full Codex argument vector and a finite positive timeout, replaces only the first executable token with the recorded Python/shim entrypoint, invokes one real child with `shell=False`, and maps timeout, unavailable, access and generic process failures to stable test results without invoking live `codex`. Record the actual process executable, shim script and full original/effective argv separately. |
| `C3` — official protocol shapes | The child emits the documented exact JSON surfaces: marketplace add `marketplaceName`/`installedRoot`/`alreadyAdded`; plugin add `pluginId`/`name`/`marketplaceName`/`version`/`installedPath`/`authPolicy`; plugin remove `pluginId`/`name`/`marketplaceName`; marketplace remove `marketplaceName`/`installedRoot`; marketplace/plugin lists retain the 05A shapes. Raw absolute sandbox paths are ephemeral child-protocol inputs only and never enter evidence, receipt, Router, telemetry or handoff text. |
| `C4` — recursively coherent persisted truth | Controller and copied child validation enforce the same finite identity, semantic-version, nonblank record, ownership and uniqueness rules. An owned plugin requires the exact owned marketplace; owned records must match the exact identity; file/state agreement is checked in both directions; invalid identity, blank/extra/null/container fields, missing source/payload, unexpected payload, plugin-without-marketplace and stale digest all block with no installed/absent success. |
| `C5` — independent owned absence with foreign preservation | Pre-seed both valid unrelated marketplace/plugin records and same-name foreign collisions. Prove unrelated records and sentinel bytes remain identical through clean success/removal, pre/post-effect failure, compensation and bounded retry. Exact owned absence is reported independently of preserved foreign state; no same-name foreign record grants mutation authority. |
| `C6` — finite failure and response contract | Every blocked child response uses one stable external exit/status shape plus one unique internal finite reason. For each injected filesystem/process dependency failure, tests assert both observable residue and whether an exception is returned or propagated. No child execution is unbounded. |
| `C7` — truthful replayable evidence | The handoff states exact focused/full/type/compile/sentinel/diff commands and counts. The full command is exactly `python -m unittest discover -s tests -v`. Focused tests run from a disposable exported checkout without manual topology repair. A final independent readback proves zero staging roots created by the run, zero repository cache, and unchanged tracked/ignored/Git state. |

### Revision-02 finite TDD matrix

| Cell | First-red and green assertion |
| --- | --- |
| `R01` | Root path boundary covers exactly equal, prefix-plus-character, trailing slash, case variation, encoded form, traversal and empty/relative forms; invalid/missing/reused forbidden roots create no root. |
| `R02` | Initialization failure after root creation removes only that exact new root; subsequent valid provision/teardown succeeds; moved/removed forbidden roots do not prevent teardown. |
| `R03` | The port is runtime-compatible with `CodexCommandPort`; full argv and positive timeout are mandatory; null, empty, whitespace, list/object, extra token and nonpositive timeout inputs fail before a child. |
| `R04` | Exact original/effective argv proves only the executable boundary changed; actual executable is Python, argv shim is the sandbox copy, and no resolved executable or child equals live `codex`. |
| `R05` | Exact marketplace/plugin add, list, remove and absence sequence passes strict official DTO parsing, including ephemeral root/path proof and `alreadyAdded=false`. Missing/extra/null/empty official fields fail. |
| `R06` | Process unavailable, access, timeout, nonzero and generic failures are finite. Pre-effect failures create no state; ambiguous/post-effect failures leave only fresh observable residue for exact retry. |
| `R07` | Empty text, whitespace, empty list/object, null, extra field, invalid semantic version, duplicate identity and malformed JSON persisted state all block with the exact finite reason. |
| `R08` | Missing source, missing payload, unexpected payload, wrong digest, owned plugin without exact owned marketplace and owned record/identity mismatch block both list and absence success. |
| `R09` | Valid unrelated marketplace/plugin records plus sentinel bytes remain identical across clean lifecycle, post-marketplace failure, post-plugin failure, remove failure, compensation and retry. |
| `R10` | Same-name foreign marketplace/plugin collisions block add/remove, remain byte/value-identical and never become owned. Exact owned absence remains independently observable while unrelated records remain present. |
| `R11` | Request and prior-response mutation cannot change fresh persisted/file truth; state/file and list/absence responses are reloaded for every child command. |
| `R12` | Existing and empty synthetic Git repositories remain byte-plus-porcelain identical; focused/full/type/compile/sentinel/diff commands are exact; failed and successful runs leave zero staging/cache roots. |

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05s_20260810` |
| Allocation | `aln_local_orchestration_install_05s_20260810` |
| Receipt | `rcpt_local_orchestration_install_05s_20260810` |
| Correlation / question | `corr-local-orchestration-install-05s-20260810` / `q-local-orchestration-install-05s-20260810` |
| Authority | Owner instruction to establish the isolated test environment before refreezing downstream tickets; continuing program authority `PRG-20260809-042` |
| Required baseline | The control-plane docs commit that adds this ticket and verification-architecture revision |
| Branch/worktree rule | Preserve the inactive 05B branch and submitted SHAs as immutable evidence. In the same sole implementation worktree, create exactly one new-ticket branch `codex/implementation-codex-lifecycle-staging-05s` from the exact required baseline. No additional worktree or concurrent branch. |
| Required return | One implementation commit containing only the authorized test-support files, complete S1–S7/E01–E08 evidence, clean worktree, then one separate docs-only handoff commit. No review, integration or downstream-ticket decision. |

### Revision-02 correction handoff

| Field | Value |
| --- | --- |
| Review | `doc/reviews/local-orchestration-installer/05s-codex-lifecycle-contract-staging-code-review.md`; findings `CR-105..CR-111` |
| Immutable submitted evidence | Implementation `18b99de`; docs-only handoff `2bed349` |
| Reused authority | Same ticket, task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, implementation owner, sole implementation worktree, branch `codex/implementation-codex-lifecycle-staging-05s`, allocation `aln_local_orchestration_install_05s_20260810` and receipt `rcpt_local_orchestration_install_05s_20260810` |
| Correction correlation | `corr-local-orchestration-install-05s-r02-20260810` |
| Required baseline | The control-plane review/refreeze commit containing `CLOSURE-LOCAL-INSTALL-T05S-02`; the implementation branch stays in place and receives additive commits only |
| Allowed correction scope | The same six test-support Python files plus the separate docs-only `doc/WorkProgressReport.md` handoff; production source remains read-only |
| Required return | One additive implementation correction commit closing `C1..C7/R01..R12`, then one separate docs-only handoff commit with exact commands/counts and zero-residue readback |

## Review and continuation

The initial reviewer executed revision 01 and batched `CR-105..CR-111`. The
implementation owner may now make the single additive revision-02 correction on
the same branch/worktree. No replacement branch/worktree is permitted. The next
review is terminal for revision 02. Only `APPROVED` plus a safe guarded
integration permits 05B/05C/04 refreeze. This staging evidence is not proof that
a packaged installer works in a clean Windows user profile.
