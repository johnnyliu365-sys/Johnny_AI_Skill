# 21｜commit 觸發只在 Windows 有，非 Windows 要誠實地說

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（可攜性第二半；上游為票 20 的鎖） |
| 第一步排查起點 | `library/local_orchestration/windows_native_git_ref.py`（唯一 import `pywin32` 的檔案） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/gov-21`／branch `implement/gov-21-ref-watch-capability` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `cc9deda`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Sonnet 5 high（一般票：能力宣告與降級，形狀已有前例） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 原生 watcher 的平台能力宣告與非 Windows 的降級路徑 |
| 禁止修改 | `commit_trigger_intake.py`（P7 的 tee 不動）；`work_queue.py`；`file_lock.py`（票 20 的範圍） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/windows_native_git_ref.py
modify = library/local_orchestration/event_runner.py
modify = tests/test_event_runner_cli.py
modify = tests/test_ref_watch_capability.py
create = tests/test_ref_watch_capability.py
forbid = library/local_orchestration/commit_trigger_intake.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/file_lock.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

在沒有原生 exact-ref watch 的平台上，runner **啟動得起來、喚醒照走、並且明說
commit 觸發不可用**——不是崩潰，也不是假裝有。

## 為什麼是「誠實降級」而不是「補實作」

本專案已經有這個模式的前例：喚醒能力未證明時，解析出的通道是 candidate inbox，
runner **據實記錄一個 completion candidate 而不是宣稱已喚醒**。那條規則來自
governance 04——skill 用直述句描寫沒在跑的機制，導致 agent 對未 arm 的專案回報假喚醒。

補 inotify／FSEvents 是**另一件事**，而且是一件大事（兩套平台 API、各自的語義差異、
各自的測試）。本票只做一件事：**讓「這個平台沒有這條腿」變成一個可查詢、被測試釘住的
事實**，而不是一個 import 錯誤。

## 現況（2026-08-22 實測）

- `pywin32` 全 library 只被 `windows_native_git_ref.py` import。
- 票 20 完成後，鎖不再是障礙；**這個檔案是 runtime 最後一個 Windows 綁定**。
- P7 的 tee 掛在這個 watcher 交給 controller 的 sink 上——**tee 本身與平台無關**，
  沒有 watcher 就沒有訊號，佇列就不會收到 `COMMIT_TRIGGER`。這是正確的行為，
  只是目前沒有被說出來。

## 不可讓的性質

1. **import 時不得炸。** 非 Windows 平台 import 這個模組必須成功，能力以**值**回報，
   不是以 ImportError 回報。
2. **具名的能力查詢**：比照 `probe_wake_capability` 的形狀，回一個有限的結果
   （可用／不可用＋具名原因），不是布林。
3. **runner 在沒有 watcher 時仍啟動**，喚醒路徑一件不少；`runner status` 要能表達
   「commit 觸發不可用」這個事實。
4. **不得假裝**：沒有 watcher 就不得有任何東西往佇列放 `COMMIT_TRIGGER`。
   以測試釘住——這正是 governance 04 那一族。

## TDD 設計

1. 正常行為：Windows 上能力回報可用，既有 watcher 行為完全不變。
2. 規則違反／輸入錯誤：不適用（無外部輸入）。
3. 外部失敗／fail-closed：模擬平台不支援 → 能力回報不可用且具名；
   runner 仍啟動；佇列**零** `COMMIT_TRIGGER` 項目。
4. 回歸保護：P7 的 tee 測試（`test_commit_trigger_intake.py`）完全不改且維持綠；
   `runner status` 既有欄位語意不變，只增不改。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | **是** | 「沒有 watcher」與「watcher 有但沒訊號」必須是兩個可區分的事實，不得都變成「佇列是空的」 |
| 3 | 權限繞過 | 否 | 不涉權限 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | **是** | 平台不支援、pywin32 缺失、watcher 啟動失敗各自具名 |
| 6 | 例外是否會拋出 | **是** | 非 Windows import 不得拋；watcher 啟動失敗不得毀掉 runner |

## 完成定義與證據

- **反向突變證據**：至少三組——讓非 Windows import 拋 ImportError、
  讓能力不可用時 runner 仍宣稱 commit 觸發可用、讓「沒有 watcher」與「佇列空」折疊成
  同一個結果；各指名哪個測試轉紅、還原後轉綠。
- **README 的誠實限制要同步更新**：目前寫「runtime 是 Windows-only」，票 20＋21 完成後
  應改為「commit 觸發是 Windows-only，其餘可攜」。**這一行由審閱者在整合時改，
  不在實作者邊界內**（README 不在本票的 modify 清單）。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。

- **全套件責任**：多張票並行實作，實作者只跑本票指定的測試檔；全套件與殘留檢查由審閱者於整合前執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 不在本票範圍

實作 inotify／FSEvents（另票，且需要真的 Linux／macOS 機器才驗得了）；
在非 Windows 實機上執行驗證——**本機沒有那些平台，平台分支以模擬與程式碼審閱擔保，
不得宣稱已在 POSIX 實機驗過**。

## 正式環境移植 SOP

不適用（本機能力宣告；隨下次發行進 bundle）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = 21
title = commit 觸發只在 Windows 有，非 Windows 要誠實地說
state = IN_PROGRESS
stage = C | 能力以值回報 | OPEN
stage = D | 降級不假裝 | OPEN
stage = M | 突變驗證 | OPEN
```
