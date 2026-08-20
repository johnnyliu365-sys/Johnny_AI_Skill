# 05 — 改名被擋住就留下孤兒

| Field | Value |
| --- | --- |
| State | `OPEN`，已派給 implementation owner |
| Baseline | `main`，C9 診斷完成之後 |
| Workload | `SMALL`；Python 3.11 strict、TDD、需反向突變 |
| 依據 | `modules/tickets/PITFALL-REGISTER.md` 的 **C9**（完整因果鏈在那裡，不要重新推導） |

## 一個結果

`tests/test_disposable_environment_core.py::DisposableEnvironmentCoreTests::test_cr167_non_exact_root_names_block_before_marker_read_or_delete`
不再因為一次暫時性的 Windows 檔案鎖就在 `tests/.johnny-runtime` 留下孤兒環境。

## 已知事實（C9 已證實，不要重跑獵捕）

發生率約 1/11，第 11 輪重現。因果鏈：

1. cr167 把環境目錄**改名**成 `johnny-stage-env-prefix-similar`。
2. 改名以 `PermissionError: [WinError 5]` 失敗——**不是刪除失敗，是改名失敗**。
   別的行程握著該目錄的 handle（登記簿 B2：Windows share-mode，讀者擋住刪除者，
   這次證實也擋得住改名）。
3. 例外從斷言區拋出，**環境沒有被拆除**。
4. 之後每個用 disposable environment 的 cell 以
   `the exact project-runtime parent was not removed` 與
   `FileExistsError [WinError 183]` 連鎖失敗。

**六個失敗只有第一個是病因，其餘五個是併發症。**

## 要達成的兩件事

**一、改名要撐得過暫時性的 `WinError 5`。**

用有上限的重試、或改成根本不需要改名的驗證方式，都可以。**做法由你決定**——
這張票規定的是結果，不是手段。若你認為這個 cell 根本在斷言錯的東西，
不要自己繞過去，回報給派工者。

**二、環境拆除必須落在每一條路徑上，包含斷言失敗時。**

現在只要斷言先炸，拆除就不會執行。這是「一個失敗變成六個」的真正原因，
比第一件更重要：就算改名偶爾還是失敗，只要拆除一定發生，就不會污染後續。

## 驗收

| Ref | 要求 | 證據 |
| --- | --- | --- |
| 05-R1 | 改名遇到暫時性 `WinError 5` 時不會讓測試留下環境 | 測試：模擬第一次改名拋 `PermissionError(WinError 5)`，斷言最終 `tests/.johnny-runtime` 為空 |
| 05-R2 | 斷言失敗時環境仍被拆除 | 測試：讓 cell 內的斷言失敗，斷言 runtime root 仍被清空 |
| 05-R3 | 原本的安全性質沒有被削弱 | cr167 原本要證明的事（非精確 root 名稱會在讀 marker 或刪除之前被擋下）仍然成立 |
| 05-R4 | 測試有鑑別力 | 反向突變：把你加的韌性拿掉，05-R1 要轉紅；把拆除移回只在成功路徑執行，05-R2 要轉紅。兩個都要還原成綠並回報 |
| 05-R5 | 全套件綠且零殘留 | 跑完印出**完整**的 `FAILED`／`SUBFAILED` 清單（登記簿 D4：永不截斷帶錯誤的輸出，這條今天已經復發過一次） |

## 邊界

- 只動 `tests/staging/environment_core/` 與 `tests/test_disposable_environment_core.py`
  這條線所需的檔案。不要動 `library/` 下的產品程式碼——這是測試基礎設施的缺陷。
- **一次只能有一個 pytest 行程**在這個 checkout 裡。並行會污染共享的 runtime root，
  那正是這張票要修的那一族。
- 開始前若 `tests/.johnny-runtime` 已經存在，代表上一輪留下殘留：清掉並在回報裡說明。

```johnny-status
id = 05
title = 改名被擋住就留下孤兒
state = DONE
stage = F | 修法 | DONE
stage = M | 突變驗證 | DONE
```
