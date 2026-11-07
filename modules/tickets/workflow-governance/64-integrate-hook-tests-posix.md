# 64｜Two integration-script tests write a git hook that POSIX never runs

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-6, R4-8; follow-up of a red CI readback on the integrated branch） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/64-integrate-hook-tests-posix-out/` / owner implementation seat / worktree `.worktrees/64-integrate-hook-tests-posix` / branch `cp/wave2-64-integrate-hook-tests-posix` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `INTEGRATED`（candidate `4283a006` integrated on `cp/wave2-gates` at `70a741f7` on 2026-11-07; CI run 42348718522 green on both jobs, clearing the red readback of `b95b4acd`; record `doc/reviews/workflow-governance/wave2-integration-2026-11-06.md`） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/64-integrate-hook-tests-posix` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/64-integrate-hook-tests-posix-review` |
| 責任邊界 | `tests/test_integrate.py` only |
| 禁止修改 | everything else; `integrate.py` does not change |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_integrate.py
forbid = skills/
forbid = ci/
forbid = .github/
forbid = library/
forbid = template/
```

## 使用者拍板與可觀察結果

Ticket 50 was integrated at `b95b4acd`. The CI readback of that commit, run 42338591673, is green on Windows and red on Linux with two `UNREGISTERED_FAILURE` lines:

- `tests/test_integrate.py::LandRaceTests::test_a_remote_that_refuses_the_push_for_another_reason_is_a_fault`
- `tests/test_integrate.py::SubmitRefusalTests::test_a_push_the_remote_refuses_for_another_reason_is_a_fault_not_queue_moved`

Both tests write a `pre-receive` hook into the bare remote with `write_text`, which leaves the file without its executable bit. Git for Windows runs such a hook anyway. Git on POSIX ignores it, so the push succeeds and the expected fault never comes: the land lands, and the submit queues. The script is correct. The two tests do not set up the refusal they test on POSIX. Every review of ticket 50 ran on Windows only, so none saw it.

R4-7 says a red readback blocks further landings until a follow-up clears it. This ticket is that follow-up. After it, both tests write their hook executable, through one helper the whole file uses for every hook it writes, and both pass on the Linux and Windows jobs.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/64-integrate-hook-tests-posix`.
- reviewer：`ticket-review` seat in `.worktrees/64-integrate-hook-tests-posix-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; CI run 42338591673; ticket 50.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：one test file; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`tests/test_integrate.py`
- 公開契約／資料模型：unchanged.

## TDD 設計

1. 正常行為：both tests pass on Windows and on the Linux CI job.
2. 規則違反／輸入錯誤：a test asserts that every hook the file writes has the executable bit for its owner on POSIX. On Windows that test is a no-op, and it says why.
3. 外部失敗／fail-closed：unchanged.
4. 回歸保護：every other test in the file passes unchanged.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule changes |
| 2 | null／空字串／陣列 | 否 | no input |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | the two tests' expected exit 2 is now produced on POSIX too |
| 6 | 例外是否會拋出 | 否 | unchanged |

## 完成定義與證據

- `python -m pytest tests/test_integrate.py -q` exit 0 on the host.
- **CI evidence**: one GitHub Actions run on a commit of this branch, with both jobs `success` and the two tests passing on Linux (the log shows no `UNREGISTERED_FAILURE`).
- **反向突變證據**: drop the executable bit in the helper. The Linux job must turn red; on this host the POSIX assertion test is not run. Restore.
- Receipt: R4-7 cells; passes `receipt_check.py` (P9) and `evidence_gate.py` (E1, run last). The full suite runs under the host lock: its failure set is a subset of the base names, with zero new red.

## 正式環境移植 SOP

- 不適用.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

### Carried after approval (CodeReview §5 rule B)

| Finding | Route |
| --- | --- |
| S64-01 | the next change of the hook guard: `test_no_hook_is_written_around_the_helper` reads the file as a whole, so the two-line `write_text` shape that caused this ticket turns it red |
| S64-02 | evidence only: the seat's receipt overstates three points; no result changes |
