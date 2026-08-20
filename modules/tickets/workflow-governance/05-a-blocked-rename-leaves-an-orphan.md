# 05｜改名被擋住就留下孤兒

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／測試基礎設施缺陷，非產品行為；來源為 `PITFALL-REGISTER.md` C9） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/PITFALL-REGISTER.md` › C9（完整因果鏈在那裡，不要重新推導） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `DONE` |
| 共同基準 | `main`，C9 診斷完成之後 |
| 實作者 | implementation owner（無紀錄，早於本欄要求） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `tests/staging/environment_core/` 與 `tests/test_disposable_environment_core.py` 這條線所需的檔案 |
| 禁止修改 | `library/` 下的產品程式碼——這是測試基礎設施的缺陷 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

`tests/test_disposable_environment_core.py::DisposableEnvironmentCoreTests::test_cr167_non_exact_root_names_block_before_marker_read_or_delete`
不再因為一次暫時性的 Windows 檔案鎖就在 `tests/.johnny-runtime` 留下孤兒環境。

已知事實（C9 已證實，不要重跑獵捕）：發生率約 1/11，第 11 輪重現。因果鏈：

1. cr167 把環境目錄**改名**成 `johnny-stage-env-prefix-similar`。
2. 改名以 `PermissionError: [WinError 5]` 失敗——**不是刪除失敗，是改名失敗**（別的行程握著該目錄的 handle：Windows share-mode，讀者擋住刪除者，這次證實也擋得住改名，見 `PITFALL-REGISTER.md` B2）。
3. 例外從斷言區拋出，**環境沒有被拆除**。
4. 之後每個用 disposable environment 的 cell 以
   `the exact project-runtime parent was not removed` 與
   `FileExistsError [WinError 183]` 連鎖失敗。

**六個失敗只有第一個是病因，其餘五個是併發症。**

## 實作範圍、依賴與 ticket elements

要達成的兩件事：

1. **改名要撐得過暫時性的 `WinError 5`。** 用有上限的重試、或改成根本不需要改名的驗證方式，都可以。**做法由實作者決定**——這張票規定的是結果，不是手段。若實作者認為這個 cell 根本在斷言錯的東西，不要自己繞過去，回報給派工者。
2. **環境拆除必須落在每一條路徑上，包含斷言失敗時。** 現在只要斷言先炸，拆除就不會執行。這是「一個失敗變成六個」的真正原因，比第一件更重要：就算改名偶爾還是失敗，只要拆除一定發生，就不會污染後續。

全域營運規則（同一 checkout 一次只能跑一個 pytest 行程；開始前若 `tests/.johnny-runtime`
已存在代表上一輪殘留，須清掉並在回報裡說明）不在此重複列出，見 `Workflow.md` 與
`PITFALL-REGISTER.md` §B2。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：無紀錄（早於本欄要求）。
- reviewer：控制面（Opus 5）；與實作者不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：本票只改測試基礎設施（disposable environment 的改名與拆除邏輯），不觸及任何正式 UI 邊界。

- 實際原始碼路徑：`tests/staging/environment_core/`、`tests/test_disposable_environment_core.py`
- 公開契約／資料模型：無變更

## TDD 設計

1. 正常行為：改名遇到暫時性 `WinError 5` 時不影響最終清理結果。
2. 規則違反／輸入錯誤：不適用（無外部輸入格式）。
3. 外部失敗／fail-closed：斷言失敗時環境仍必須被拆除，不得因斷言先炸而跳過清理。
4. 回歸保護：cr167 原本要證明的性質（非精確 root 名稱會在讀 marker 或刪除之前被擋下）不變。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 本票不涉路徑比對；cr167 既有的非精確名稱斷言不變動 |
| 2 | null／空字串／陣列 | 否 | 不涉輸入處理 |
| 3 | 權限繞過 | 否 | 不涉權限判斷 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 不新增對外錯誤碼 |
| 6 | 例外是否會拋出 | 是 | 改名的暫時性 `WinError 5` 與斷言失敗都不得讓拆除邏輯被跳過 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| 05-R1 | 改名遇到暫時性 `WinError 5` 時不會讓測試留下環境 | 測試：模擬第一次改名拋 `PermissionError(WinError 5)`，斷言最終 `tests/.johnny-runtime` 為空 |
| 05-R2 | 斷言失敗時環境仍被拆除 | 測試：讓 cell 內的斷言失敗，斷言 runtime root 仍被清空 |
| 05-R3 | 原本的安全性質沒有被削弱 | cr167 原本要證明的事（非精確 root 名稱會在讀 marker 或刪除之前被擋下）仍然成立 |
| 05-R5 | 全套件綠且零殘留 | 跑完印出**完整**的 `FAILED`／`SUBFAILED` 清單（規則見 `PITFALL-REGISTER.md` §D4；此紀律當時已復發一次，故本票要求逐字列出，不看摘要） |

- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：05-R4——把新增的韌性拿掉，05-R1 轉紅；把拆除移回只在成功路徑執行，05-R2 轉紅；兩者皆已還原成綠。
- **缺陷修正** baseline-red：`test_cr167_non_exact_root_names_block_before_marker_read_or_delete` 在暫時性 `WinError 5` 下失敗並留下孤兒環境（發生率約 1/11，第 11 輪重現，詳見 `PITFALL-REGISTER.md` C9）。

## 正式環境移植 SOP

不適用（僅測試基礎設施，無 migration、環境變數或部署影響）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：無紀錄（早於本欄要求）
- WorkProgress：不適用

```johnny-status
id = 05
title = 改名被擋住就留下孤兒
state = DONE
stage = F | 修法 | DONE
stage = M | 突變驗證 | DONE
```
