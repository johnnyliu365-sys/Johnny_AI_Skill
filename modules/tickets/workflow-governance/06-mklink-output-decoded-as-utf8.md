# 06 — mklink 的輸出用 UTF-8 解，這台是 cp950

| Field | Value |
| --- | --- |
| State | `IN_PROGRESS` — 已有 session 在做，本票為補開 |
| Baseline | `main`，governance 05 整合之後 |
| Workload | `SMALL`；規則明確、可單一 cell 驗證 |
| 來源 | governance 05 的實作者在範圍外發現並標記；owner 按下 chip 啟動 |

## 一個結果

`test_t3_physical_root_junction_blocks_before_marker_read_through` 不再因為解碼失敗
而丟掉 `mklink` 的 stderr，套件也不再為此產生
`PytestUnhandledThreadExceptionWarning`。

## 事實（已證實，不要重新推導）

`tests/test_disposable_environment_core.py` 的 t3 用
`subprocess.run(..., encoding="utf-8", errors="strict")` 執行
`cmd.exe /d /c mklink /J ...`。這台主機主控台是 **cp950**，`mklink` 的在地化輸出
解不動，`UnicodeDecodeError` 在 subprocess 的 `_readerthread` 裡被拋出，pytest 以
`PytestUnhandledThreadExceptionWarning` 呈現（八個警告之一）。

**在 HEAD 上就存在**，以乾淨副本執行該 cell 確認過，與 governance 05 無關。

**影響**：測試仍然會過，因為它只斷言 `junction.returncode == 0`；但
`junction.stderr` 是被當成斷言訊息傳進去的，解碼一炸就沒了——**真的 mklink 失敗時，
錯誤訊息會是沒有用的那一種**。這是登記簿 E 族（環境）的形狀：cp950 主控台。

## 邊界

`shell=False`、`check=False` 與 5 秒逾時維持不變。修的是解碼，不是執行方式。

## 驗收

| Ref | 要求 | 證據 |
| --- | --- | --- |
| 06-R1 | 該 cell 執行後不再出現 `PytestUnhandledThreadExceptionWarning` | 單跑該 cell，警告數比修前少一 |
| 06-R2 | `mklink` 真的失敗時，stderr 會出現在斷言訊息裡 | 測試或實證：注入一個會失敗的 mklink，確認訊息帶得出內容 |
| 06-R3 | 全套件綠且零殘留 | 跑完印出**完整**的 `FAILED`／`SUBFAILED` 清單（登記簿 D4） |

## 流程備註（給之後看的人）

這張票是**補開**的。實作者在自己票的範圍外發現缺陷，正確地標記成 chip 而不是順手夾帶
修改；owner 按下之後才有 session 開始做。因此該 session：

- **沒有經過工單**就開始工作（票是派工的單位，也是狀態頁唯一讀得到的東西）；
- **在根目錄 checkout 上工作**，不是綁定的實作者 worktree，與 `Workflow.md` §5
  「Agent 只能寫入自己的 worktree」不一致。

兩者都不是那位實作者的錯——chip 的機制不會經過主管的 worktree 配置。**這是機制與流程
之間的缺口**：chip 能讓「該讓 owner 知道的事」浮到介面上（目前唯一在 app 裡真的看得見
的通道），但它繞過了派工。要不要讓 chip 走工單，是 owner 的決定。

```johnny-status
id = 06
title = mklink 的輸出用 UTF-8 解
state = IN_PROGRESS
stage = F | 修法 | OPEN
stage = V | 驗證 | OPEN
```
