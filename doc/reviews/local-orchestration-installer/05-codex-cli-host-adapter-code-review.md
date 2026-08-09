# 05 Codex CLI Host Adapter - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `05-codex-cli-host-adapter` |
| Result | `CHANGES_REQUESTED` |
| Reviewer | Codex / current `main` worktree |
| Single branch | `codex/implementation-codex-cli-host-adapter-05` |
| Closure | Initial `CLOSURE-LOCAL-INSTALL-T05-01` / `K1..K8` |

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
