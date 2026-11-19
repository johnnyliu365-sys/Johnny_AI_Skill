# 71｜Publication 0.5.0: manifests aligned (version, Apache-2.0, author), Level 1 only for Claude Code and Codex, the publication commit reachable from a ref, the marketplace re-pinned

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（REQ-20261103-043 wave 3 "publication 0.5"; owner decisions 2026-11-07 "2.B", 2026-11-18 "2A", and 2026-11-19 on Level 2, the Codex install path and the Codex manifest） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/71-publication-out/` / owner implementation seat / worktree `.worktrees/71-publication` / branch `cp/wave3-71-publication` / baseline the wave-3 branch after ticket 73 is integrated |
| 實作語言 | JSON manifests; Python 3.11 for the tests（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED`（revision02; strict tier; rule-only review before dispatch; the last wave-3 code ticket, after ticket 73） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/71-publication` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/71-publication-review` |
| 責任邊界 | the two shipped manifests, the README's install sections, one SKILL.md sentence, the publication test constants, the changelog entry, and the publication commit built locally with the committed generator |
| 禁止修改 | `library/` code, the gate scripts, the governance documents; any push to the publication repository (the control plane pushes after the owner confirms) |
| 環境 | `LOCAL`; the publication repository and the anchor ref only after the owner confirms |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = README.md
modify = skills/johnny-project-takeover/SKILL.md
modify = tests/test_plugin_publication.py
modify = tests/test_plugin_payload_boundary.py
modify = ci/registered-failures.json
modify = doc/HARNESS-CHANGELOG.md
forbid = library/
forbid = skills/johnny-project-takeover/scripts/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
```

## 使用者拍板與可觀察結果

Owner decisions this ticket carries out:

- **2026-11-07 "2.B":** the marketplace re-pin waits for the wave-3 publication.
- **2026-11-18 "2A":** the plugin licence is Apache License 2.0, as `LICENSE` states, and the author is Johnny Liu.
- **REQ-20261103-043, wave 3:** publication 0.5, with the publication commit reachable from a ref.

Today `.claude-plugin/marketplace.json` pins `0b3afd36` (0.4.14). No ref of the development repository reaches that commit, so four publication tests are base failures:

- `CommittedPinTests::test_the_pinned_sha_exists`;
- `test_l5_stale_candidate_pin_is_named_before_generation`;
- the two `PublicationReachabilityTests`.

Process tier: strict.

**Revision02** carries out three owner decisions of 2026-11-19:
- the Level 2 runtime does not ship;
- the Codex install path is the one the owner verified with `codex-cli 0.167.0-alpha.3.2`;
- `.codex-plugin/plugin.json` is retired, because Codex reads the shared `.claude-plugin/plugin.json`.

  The last decision rests on evidence: this host's Codex lists `johnny-ai-skill` at `0.4.14`, a version only the Claude manifest holds, and the 0.4.14 publication tree has no `.codex-plugin`. Deleting the file needs the Level 2 packaging code retired too, which is ticket 78. This ticket leaves the file untouched; it is not in the payload.

After this ticket:

- **Version:** `0.5.0` in `.claude-plugin/plugin.json` and in the plugin entry of `.claude-plugin/marketplace.json`.
- **Licence:** `"Apache-2.0"` in both, replacing `"Proprietary"`.
- **Author:** `author.name` is `Johnny Liu`, and so is the marketplace `owner.name`. The URLs stay `https://github.com/johnnyliu365-sys`. No e-mail address appears in any manifest.
- **Descriptions and keywords:** they no longer name context-load telemetry or the router, which tickets 65 and 66 retired. They describe the project-takeover workflow with its gate scripts, and reusable-module selection.
- **The README's install sections:**
  - The Level 2 section ("Level 2：安裝完整 Router Runtime"), the status check and the Level 2 error table are removed. They are replaced by one section for users of a 0.4.x Level 2 runtime. It covers:
    - its own `uninstall` command, run through `%LOCALAPPDATA%\JohnnyRouter\launcher\johnny-router.ps1`, or the `JOHNNY_ROOT` root when set;
    - what that command removes and what it leaves;
    - when the folder may be deleted by hand: when uninstall cannot run, for example after a failed install whose `install-journal.jsonl` blocks a reinstall.
  - The Claude Code section installs from the development repository's `v0.5.0` tag. The command is `claude plugin marketplace add https://raw.githubusercontent.com/johnnyliu365-sys/Johnny_AI_Skill/v0.5.0/.claude-plugin/marketplace.json`, followed by the existing install, update and uninstall commands.
  - A new Codex section gives these steps:
    1. `codex --version`, with the note that the `plugin add` command is needed: `0.167.0-alpha.3.2` has it, while `0.130.0-alpha.5` lists only `plugin marketplace`.
    2. `codex plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill --ref v0.5.0`. Codex takes a GitHub source and a ref, not a raw `marketplace.json` URL.
    3. `codex plugin add johnny-ai-skill@johnny-ai-skill --json`.
    4. The version check: `codex plugin list --marketplace johnny-ai-skill --json`, where the entry `johnny-ai-skill@johnny-ai-skill` shows `version` `0.5.0`, `installed` true and `enabled` true. A new Codex session then loads it.
    5. Removal: `codex plugin remove johnny-ai-skill@johnny-ai-skill --json`, and `codex plugin marketplace remove johnny-ai-skill --json`.
- **SKILL.md:** the sentence on the kept launcher commands (`SKILL.md:112`, after "The honest statement is: …") is replaced by one sentence. It says that a 0.4.x Level 2 runtime is removed by its own `uninstall`, as the README describes. The no-runner statement before it stays.
- **The publication commit:**
  - The seat builds it locally with the committed generator: `python -m library.local_orchestration.plugin_publication --repo . --manifest .claude-plugin/plugin.json --marketplace .claude-plugin/marketplace.json --ref refs/heads/publication-0.5.0`.
  - The generator repins `marketplace.json` to the new commit.
  - The STATEMENT records the commit id, its tree id and the file count. The run is repeated once, and the second run must give the same commit id.
  - The seat creates the local ref `refs/heads/publication-0.5.0` and pushes nothing.
- **The package carries the new gates.** The seat checks the publication commit, not the development tree:
  - it extracts the publication commit's tree into an empty directory;
  - it runs the gate scripts from that directory: `dispatch_lint.py` with `--ticket` (R7) and R8, `evidence_gate.py` on a receipt with an `effort:` line, and `usage_report.py` with an expectation that names a model and an effort;
  - the sha256 of every gate script in the package equals that of the same file on the development branch;
  - both manifests in the package say `0.5.0`, and the package holds no `.codex-plugin` and no Level 2 file;
  - the marketplace pin names this publication commit;
  - the package's README holds the Codex section and no Level 2 install section.

  The STATEMENT records each result.
- **The publication tests:** `_RELEASE_VERSION` is `0.5.0`. The four base failures pass on the host once the anchor ref exists locally. On CI they pass once the control plane has pushed the anchor ref, so until then they stay registered. Each changed constant is named in the STATEMENT.
- **The changelog:** `doc/HARNESS-CHANGELOG.md` gains a 0.5.0 entry naming:
  - the router library retirement (tickets 65, 66, 68), and the governance documents cleared of retired surfaces (ticket 67);
  - the gate scripts as the default path;
  - the `USAGE` cell (ticket 69), and the model and effort bound to each profile (ticket 76);
  - the template follow-ups (ticket 70), and the repository's own ticket template with dispatch lint R7 (ticket 75);
  - the wave-3 rule texts (ticket 74);
  - the licence alignment.

  The entry also has a section for outside readers, so that a user or a Codex host run does not follow a retired specification. It states:
  - which surfaces were retired: the flow engine, the private router, the profile, router telemetry, and the cross-lifetime bridge (runner, wake, dispatch and review CLI families, live descriptor);
  - that the seven router-era SPECs now live in `doc/archive/specs/2026/`, as `ARCH-SPEC-20261118-001` to `007`;
  - that nine router-era ADRs are marked `SUPERSEDED` in place;
  - which documents to read instead: `AGENTS.md`, `Workflow.md`, `CodeReview.md` and `modules/spec/workflow-governance.md`.
- **After review approval and the owner's confirmation**, the control plane does the outward steps, which are not this seat's work:
  1. push the publication commit to `Johnny_AI_Skill_publication` `main`, with tag `plugin-v0.5.0`;
  2. push `refs/heads/publication-0.5.0` to the development repository, and tag `v0.5.0` on the development commit whose `marketplace.json` pins the publication commit, which is the tag the README's install commands name;
  3. read both back;
  4. remove the four rows from `ci/registered-failures.json` in an additive commit, once CI shows them passing.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/71-publication`.
- reviewer：`ticket-review` seat in `.worktrees/71-publication-review`.
- **Owner override record**：the outward pushes wait for the owner's explicit confirmation in chat.
- `ImplementationHandoff`：this ticket; `library/local_orchestration/plugin_publication.py`; tickets 65 to 70.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：manifests and tests; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the manifest fields above.

## TDD 設計

1. 正常行為:
   - `--verify-only` with the new pin and the local anchor ref prints `verified <sha>` and exits 0.
   - The four publication tests pass on the host.
2. 規則違反／輸入錯誤:
   - a shipped manifest with `Proprietary`, with a version other than `0.5.0`, or with an author other than `Johnny Liu` fails a test of `tests/test_plugin_payload_boundary.py`;
   - a README that names `johnny-install.cmd` as an install step, or lacks the Codex `plugin add` step, fails a test there;
   - a manifest containing an `@` in any author or owner field fails.
3. 外部失敗／fail-closed: `--verify-only` without the anchor ref refuses, as today.
4. 回歸保護: the payload closure test passes. The publication tree carries `LICENSE`, `NOTICE` and `README.md`, and no retired module.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | payload rules unchanged |
| 2 | null／空字串／陣列 | 是 | an empty author name fails |
| 3 | 權限繞過 | 是 | no e-mail address in a manifest; no push by the seat |
| 4 | Token 格式與比較 | 是 | the version string compared exactly, `0.5.0` |
| 5 | 錯誤碼是否一致 | 否 | no exit codes change |
| 6 | 例外是否會拋出 | 否 | no new code |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_plugin_publication.py tests/test_plugin_payload_boundary.py -q` exits 0 on the host with the local anchor ref.
  - `mypy --strict --python-version 3.11` on the two test files exits 0.
- **G1**: the generator run twice, giving the same commit id both times.
- **V1**: `--verify-only` exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - put `Proprietary` back in one manifest;
  - put a Level 2 install section back in the README;
  - drop `NOTICE` from the payload.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`. The four publication rows stay registered until the anchor ref is pushed.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last).

## 正式環境移植 SOP

- The publication push, the anchor push and the readback are the control plane's, after the owner confirms. The record holds:
  - the pushed commit id;
  - `git ls-remote` of both repositories;
  - one `--verify-only` run on a fresh clone made with `--no-hardlinks`.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
