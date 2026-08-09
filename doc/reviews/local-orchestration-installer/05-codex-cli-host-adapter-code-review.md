# 05 Codex CLI Host Adapter - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05-codex-cli-host-adapter` |
| Result | Initial `CHANGES_REQUESTED`; correction `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |
| Reviewer | Codex / current `main` worktree |
| Single branch | `codex/implementation-codex-cli-host-adapter-05` |
| Closure | Initial `CLOSURE-LOCAL-INSTALL-T05-01`; correction `CLOSURE-LOCAL-INSTALL-T05-02` / `K1..K8 + R1..R8` |

## Boundary and revisions

The reviewed range is dispatch baseline `8d3c1b3`, implementation `0c2ab95`,
and docs-only handoff `39936fc`. The implementation commit changes exactly the
four authorized production files and one authorized test; the handoff changes
only `doc/WorkProgressReport.md`. The implementation worktree was clean before
independent verification and no additional branch or worktree was created.

## Independent verification

| Check | Evidence |
| --- | --- |
| Green baseline | Focused unittest 15/15 and full discovery 171/171 passed. Strict mypy reported no issues in 82 source files. `git diff --check` passed. These checks reproduce the handoff but do not close the adversarial failures below. |
| Scope / ceiling | Final implementation diff is limited to the authorized files. Net production additions are `394 / 400`; the test contains `362 / 450` non-blank lines. |
| CLI source of truth | The current official [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli) says marketplace add consumes a Git/local marketplace **source**; plugin add accepts plugin identity plus optional marketplace, with no `--version`; plugin-list JSON contains `installed`/`available`; marketplace-list JSON contains `marketplaces` entries with `name`, `root` and optional source. The implementation instead assumes name-as-source, `--version`, and invented owner/digest/registration/path list fields. |
| Local CLI check | `codex.exe` resolves to the WindowsApps package but this control shell receives `Access is denied`, matching the previously recorded boundary. No second live registration or mutation was attempted. `PRG-20260809-077` remains capability evidence only. |
| Adversarial probes | `None` request/receipt/command port and invalid UTF-8 raised uncaught exceptions; NaN timeout was accepted; official marketplace JSON returned `MALFORMED_OUTPUT`; post-add stale verification made zero cleanup calls; marketplace-remove failure followed by retry returned `ABSENT` while the owned marketplace remained; foreign path/installation absence evidence also returned `ABSENT`. |
| Worktree residue | The reviewer reran the claimed compile step and it generated only reproducible untracked `__pycache__/` directories. Per worktree ownership, the reviewer did not remove them; the implementation owner must clear them before the correction return. |

## Closure mapping

| Closure | Result | Independent result |
| --- | --- | --- |
| `K1` | FAIL | Root `None` inputs and a `None` command port escape as `AttributeError`; returned port evidence is accepted by nominal type without recursive strict reconstruction. |
| `K2` | FAIL | NaN violates the finite-timeout contract, invalid UTF-8 escapes, and the detector expects undocumented version JSON/command-list fields. |
| `K3` | INCOMPLETE | Existing/foreign happy probes pass against invented list records, but copied/suffix/case/stale matrices are absent and the real CLI list schema cannot reach this gate. |
| `K4` | FAIL | Marketplace source, command vectors and JSON contracts do not match the public CLI. `CodexRegistrationReceipt` also omits the required canonical registration key. |
| `K5` | FAIL | When plugin add succeeds but structured verification is stale/missing, no plugin or marketplace cleanup is attempted and a partial registration can remain. |
| `K6` | FAIL | A failed marketplace removal followed by retry reports `ABSENT` without checking/removing the still-present marketplace. Foreign absence evidence can also authorize terminal absence. |
| `K7` | FAIL | Exact owner/path evidence is not consumed and existing marketplace absence is not part of replay success; unrelated list/byte invariance is not actually exercised. |
| `K8` | FAIL | The test creates a `.git-marker` in a temporary directory, not existing/empty Git repositories with byte and porcelain snapshots. Red and reverse evidence is generic rather than the required named, reproducible matrix. |

## CodeReview.md checks

| Check | Result |
| --- | --- |
| Types and layering | FAIL. Named Pydantic models exist, but untrusted root/port values are not consistently revalidated and the CLI response models do not represent the actual boundary. |
| Logic / reachability | FAIL. Normal documented CLI output cannot reach success; multiple failure/retry paths report a finite value with owned residue or raise uncaught exceptions. |
| Path-prefix matrix | FAIL. Only one suffix path case exists; exact, trailing separator, case, encoded separator, traversal and empty cases are not mapped one-to-one to K1/K7. |
| Permission / ownership bypass | FAIL. A shape-valid absence result for another installation/path is accepted as proof for the requested receipt. |
| Test truthfulness | FAIL. The 15 committed tests pass, but K1–K8 and the handoff describe substantially broader behavior than their assertions. The Git test is not a Git test. |
| Security / privacy | BLOCKED by ownership-proof failures. No target repository or Secret was touched, but false terminal absence can strand plugin/marketplace residue. |
| Dependencies / reuse | PASS. No new runtime dependency or historical-source import was added. |

## Batched findings

1. **CR-73 — `TICKET_DEFECT`, K1/K4.** The frozen ticket requires the documented local marketplace lifecycle but does not define the local marketplace source locator that `codex plugin marketplace add` requires. Repair the ticket with a strict installer-owned source contract and re-freeze the closure before implementation correction. The source must be proven under the installer-owned root and must never be a target-project path, URI, arbitrary cwd-relative string or persisted raw path.
2. **CR-74 — `IMPLEMENTATION_DEFECT`, K2/K4.** `codex_cli_adapter.py:60-65`, `:136-155` and `host_contracts.py` model a non-existent CLI contract: name is passed as marketplace source, plugin add uses unsupported `--version`, version detection expects undocumented JSON, and list records require fields the official JSON does not emit. The receipt also lacks K4's canonical registration key. Align commands and strict response DTOs to the documented CLI and bind the receipt only from current-attempt request plus observed add/list/filesystem evidence.
3. **CR-75 — `IMPLEMENTATION_DEFECT`, K1/K2.** `codex_cli_adapter.py:37-40`, `:50-52`, `:93-95` and `:158-168` allow NaN timeout and leak `AttributeError`/`UnicodeDecodeError` for declared boundary failures. Reconstruct all root inputs before any port call, reject missing/invalid injected ports at construction, require `math.isfinite`, and map process decoding/failure paths to finite typed blocked reasons without broad success fallbacks.
4. **CR-76 — `IMPLEMENTATION_DEFECT`, K5.** `codex_cli_adapter.py:66-86` excludes `RECEIPT_MISMATCH` from fallback cleanup even when both marketplace and plugin add already succeeded. The independent stale-list probe records zero remove calls. Cleanup authority must be bound to the current attempt and remove only that exact plugin then marketplace; cleanup failure must remain blocked/retryable, never silently retain a partial success.
5. **CR-77 — `IMPLEMENTATION_DEFECT`, K6/K7.** `codex_cli_adapter.py:101-107` returns `ABSENT` when the plugin is absent even if the exact owned marketplace remains. A marketplace-remove failure followed by retry therefore produces false terminal absence with zero correction mutation. Terminal absence must be the conjunction of exact plugin, exact marketplace and exact owned path absence.
6. **CR-78 — `IMPLEMENTATION_DEFECT`, K1/K6/K7.** `codex_cli_adapter.py:105-118` tests only `isinstance(CodexAbsenceEvidence)`. A valid evidence object for another installation and path authorizes `ABSENT`; non-validating constructed nested output is likewise not reconstructed. Strictly revalidate every returned port DTO and compare installation ID plus exact owned locator before idempotent or successful removal.
7. **CR-79 — `EVIDENCE_DEFECT`, K1..K8.** `tests/test_codex_cli_host_adapter.py` and handoff `39936fc` do not contain the claimed complete boundary, real-schema, cleanup/retry, exact-proof, actual-Git or reverse-mutation evidence. Add the complete frozen matrix, preserve exact first-red names/reasons, run actual existing/empty Git byte and porcelain snapshots, and record reproducible reverse mutations. Do not claim the prior live probe as implementation verification.

## Conclusion

`CHANGES_REQUESTED`. The approved SPEC and user outcome remain unchanged, but
CR-73 requires a control-plane ticket repair and a new closure revision before
the implementation owner resumes. There is no `REQUIREMENT_CHANGED` and no
`FRESH_BRANCH_REQUIRED` evidence. Keep the same ticket, implementation task,
worktree, branch, allocation and receipt; corrections must be additive commits
on `codex/implementation-codex-cli-host-adapter-05`. This is the single initial
review permitted for the corrected closure; only one correction review follows.

## Correction review — `CLOSURE-LOCAL-INSTALL-T05-02`

### Correction boundary and submitted revisions

The correction review covers additive implementation commits `c2ea3f8`,
`3f6c41a` and `13d02de`, intermediate docs-only commit `09b4824`, and final
docs-only handoff `4c9525b`, all descended from the original handoff `39936fc`
on the same branch and worktree. The branch and implementation worktree were
clean at handoff and remained clean after reviewer-owned no-bytecode checks. No
new branch, worktree, live registration, target-project write, merge, push,
deployment or schedule action occurred.

### Correction independent verification

| Check | Result / evidence |
| --- | --- |
| Submitted green suite | PASS: focused unittest `15/15`; full discovery `171/171`; strict mypy `82` files; in-memory compile of the four production files and one test; `git diff --check`. |
| Scope / ceiling | PASS: only the four production files and one test contain implementation changes. Independent non-blank comparison against `8d3c1b3` is production `394 / 400`, not the handoff's `396`; the test is `205 / 450`. |
| Current official CLI contract | FAIL: the current official [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands.md?surface=cli) documents plugin add fields `pluginId`, `name`, `marketplaceName`, `version`, `installedPath`, `authPolicy`; plugin-list entries use `pluginId`, `name`, `marketplaceName`, `version`, `installed`, `enabled`, `source`, `installPolicy`, `authPolicy`; marketplace add includes `marketplaceName`, `installedRoot`, `alreadyAdded`. The submitted DTOs still require `id`/`root`, use `pluginName`/`installedRoot` for plugin mutation, reject documented extra fields, and make every mutation identity field optional. |
| Official-schema probes | FAIL: documented marketplace-add JSON returns `MALFORMED_OUTPUT` with zero cleanup calls; documented plugin-add JSON returns `MALFORMED_OUTPUT`, removes only the marketplace and never the plugin whose add may already have succeeded; documented plugin-list JSON fails strict validation with ten errors. Conversely, empty `{}` marketplace/plugin mutation objects can reach terminal `INSTALLED`. |
| Canonical ownership probes | FAIL: source locators with case mismatch are accepted; `C:\foreign\JohnnyAIWorkflow\...` is accepted solely because the path contains a magic directory segment, and that foreign proof can authorize terminal `ABSENT`. `CodexInstallRequest`, manifest evidence and absence evidence contain no canonical `InstallRoot` binding or exact source-root proof. |
| Finite failure probes | FAIL: real `subprocess.TimeoutExpired`, filesystem `source()` `OSError`, and filesystem `inspect()` `OSError` escape instead of returning the finite typed result algebra. The committed fake covers `TimeoutError`, not the exception raised by `subprocess.run`. |
| Cleanup / retry probes | FAIL: mutation ownership flags are set only after successful response parsing, so a CLI effect followed by documented-but-rejected JSON is not fully reversed. `_cleanup` trusts remove responses and performs no list/path absence verification; the adapter cannot distinguish successful cleanup from retained residue. |
| Collision / preflight probe | FAIL: an existing same plugin name under another marketplace passes preflight and the adapter begins marketplace/plugin mutations, contrary to K3's foreign-owner collision rule. |
| Evidence truth | FAIL: the committed Git test compares porcelain only, not byte plus porcelain snapshots; the handoff's named `test_r1...test_r4...` first-red tests do not exist in any submitted commit; reverse-mutation evidence is a generic assertion without reproducible mutation commands/results; intermediate docs commit `09b4824` and the independently measured `394` production lines are omitted or misstated in the return. |

### Corrected closure mapping

| Item | Result | Independent correction result |
| --- | --- | --- |
| `K1 / R1` | FAIL | Typed relative paths exist, but case variants and a foreign root containing `JohnnyAIWorkflow` are accepted; no canonical `InstallRoot` is carried or matched. |
| `K2 / R2 / R4` | FAIL | Plain version parsing works, but documented plugin/marketplace JSON cannot complete the lifecycle and real process/filesystem failures can escape. |
| `K3` | FAIL | Exact duplicate identity blocks, but the same plugin under a foreign marketplace is allowed to reach mutation. |
| `K4 / R3` | FAIL | The canonical registration key is present, but empty mutation output is accepted and the receipt is not derived from the documented observed plugin identity/path fields. |
| `K5 / R5` | FAIL | Some scripted cleanup calls occur, but effect flags are late and cleanup does not prove plugin, marketplace and path absence. |
| `K6 / R6` | FAIL | The scripted invented-schema happy path checks the three absence booleans, but the documented CLI schema cannot reach it and foreign-root evidence can still yield `ABSENT`. |
| `K7 / R7` | FAIL | Recursive Pydantic reconstruction is improved, but evidence lacks canonical root/source identity and case-exact matching; foreign source/root proof remains authoritative. |
| `K8 / R8` | FAIL | Green/type/compile/diff checks pass, but official fixtures, first-red evidence, reverse mutations and byte-level Git snapshots are not truthfully reproducible. |

### Correction-review batched findings

1. **CR-80 — `IMPLEMENTATION_DEFECT`, K2/K4/R2/R3.** `host_contracts.py:329-442` and `codex_cli_adapter.py:51-61,106-122` still model non-public plugin JSON. Replace invented `id`/`root` and `pluginName`/plugin `installedRoot` fields with the documented DTOs, make required output identity required, reject `{}`, and derive the receipt only from the exact observed public fields plus current filesystem proof.
2. **CR-81 — `IMPLEMENTATION_DEFECT`, K1/K6/K7/R1/R6/R7.** `host_contracts.py:265-326` and `codex_cli_adapter.py:110-173` do not bind the source, manifest or absence proof to `CANONICAL_INSTALL_ROOT`; substring/suffix/case-fold matching accepts foreign roots and case variants. Carry and compare the canonical root and exact relative source/installed locators at every port boundary and in every success/absence proof.
3. **CR-82 — `IMPLEMENTATION_DEFECT`, K2/K5/K6/R4.** `codex_cli_adapter.py:124-134` misses `subprocess.TimeoutExpired`, while source/inspect port exceptions at `:49,59,72,77,84,88` are outside the finite mapping. Every declared command/filesystem failure must return a named blocked reason without escaping.
4. **CR-83 — `IMPLEMENTATION_DEFECT`, K5/R5.** `codex_cli_adapter.py:51-65,175-184` records ownership only after parsing and treats remove-response parsing as cleanup proof. Current-attempt effects must become compensable before parsing their response, and cleanup must verify exact plugin, marketplace and path absence before it can be reported as successful.
5. **CR-84 — `IMPLEMENTATION_DEFECT`, K3.** `codex_cli_adapter.py:140-143` checks only the exact `plugin@marketplace` identifier. The frozen same-name/foreign-owner collision cell must block before the first mutation.
6. **CR-85 — `EVIDENCE_DEFECT`, K8/R8.** `tests/test_codex_cli_host_adapter.py:146-242` uses non-public JSON fixtures, compares Git porcelain without byte snapshots, and does not preserve the named first-red or reproducible reverse-mutation evidence claimed by `4c9525b`. The handoff also reports `396` production lines while independent non-blank comparison is `394` and omits intermediate docs commit `09b4824`.

### Correction conclusion and convergence route

`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. This is the one permitted
correction review for `CLOSURE-LOCAL-INSTALL-T05-02`; CR-80 through CR-85 are
all tied to its frozen K/R items and still affect correctness, ownership,
cleanup and evidence truth. Workflow §8.1 therefore forbids a third automatic
implementation correction. Ticket 05 returns to the control plane for
architecture/ticket decomposition. The existing branch and all submitted SHAs
remain immutable evidence; no integration, new branch/worktree or Ticket-04
dispatch is authorized.

## Control-plane convergence decomposition

The owner instructed the control plane to begin decomposition on 2026-08-10.
No third correction review or implementation dispatch is added to this closure.
Parent Ticket 05 is superseded as an executable ticket; its rejected branch,
implementation/docs SHAs and this review remain immutable evidence. Its old
allocation is released and its receipt is closed/non-reusable.

| Finding | Replacement closure |
| --- | --- |
| CR-80 — public DTO mismatch | 05A/A1 list DTOs; 05B/B1 add DTOs; 05C/C2 remove DTOs |
| CR-81 — root/source/proof identity | 05A/A2; 05B/B2; 05C/C1 and C3 |
| CR-82 — escaping process/filesystem failures | 05A/A4; 05B/B5; 05C/C2 and C5 |
| CR-83 — late/unverified compensation | 05B/B3 and B4; 05C/C3 |
| CR-84 — same-name foreign marketplace | 05A/A3 |
| CR-85 — untruthful/incomplete evidence | 05A/A5; 05B/B5; 05C/C5 |

The split is vertical and serial: zero-mutation eligibility, transactional
registration, then receipt-bound removal/replay. Each ticket carries its own
first-red, official-fixture, reverse-mutation and Git-isolation evidence. There
is no evidence-only ticket and no broad "all failures" closure. The final child
retains the parent's cumulative 400 production / 450 test non-blank-line ceiling.

Only 05A may enter implementation after the decomposition commit. It receives a
new ticket-bound receipt and one active new-ticket branch in the existing sole
implementation worktree from the clean integrated baseline. This does not
rewrite or delete the rejected branch and does not authorize concurrent 05B,
05C or Ticket-04 work.
