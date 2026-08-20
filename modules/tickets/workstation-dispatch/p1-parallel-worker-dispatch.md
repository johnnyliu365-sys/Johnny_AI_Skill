# P1 — 用 Router 記帳，管多個平行工人

| Field | Value |
| --- | --- |
| Owner | 控制面 |
| Baseline | `main`，V2-S2 之後 |
| Workload | `STANDARD`；Python 3.11 strict、TDD、需反向突變 |

## 一個結果

同時有多張票在跑的時候，「哪張票在誰手上、在哪個 worktree、發過哪張 receipt」是**持久的事實**，不是我記在對話裡的東西。同一張票發不出第二份 receipt，兩個工人不會互相踩，每個 verdict 只被消費一次。

## 分工：Router 不知道「子代理」是什麼

owner 指出 Codex 也有子代理，所以這條線是通用的，不是 Claude 專屬。這件事決定了邊界該畫在哪：

- **host 生工人。** 怎麼生是 host 的事——Claude 的 Agent 工具、Codex 的子代理、或未來任何機制。
- **Router 記帳。** 它記的是「某張票、某個 worktree、某個分支、某張 receipt」。

**Router 這一側絕對不能出現 subagent、Claude、Codex 這些字。** 一旦出現，這條線就綁死在一個 host 上，而它的價值正好來自不綁。既有的 `dispatch_authority` 目前一個字都沒有，這個性質要用測試守住，不能靠自律。

## 已經有的，不要重造

查過了，Router 這側幾乎是齊的。`admit_dispatch` 已經是完整的閘門：

1. 讀 owner 授權，沒有就 `DISPATCH_AUTHORITY_ABSENT`
2. `verify_worktree_contained`——用**解析後的真實路徑**驗 worktree 在 repo 根目錄下，junction 一律拒絕
3. 登記 artifact（identity 衝突會擋）
4. CAS 發 receipt
5. 回讀驗證 `verify_receipt_claimable`
6. 全程寫 journal，帶 principal

`DispatchAdmissionRequest` 本來就帶 `worktree_fingerprint`、`branch_fingerprint`、`repository_root`、`host_worktree_path`。也就是說**「一個工人在某個 worktree 上為某張票工作」這個模型已經存在**，只是從來沒有人拿它跑平行。

`review_return` / `review_return_consumption` 也已經有跨行程鎖與恰好一次消費（W5）。

## 沒有被證明的（這才是這張票的內容）

**1. 並行發放安不安全。** 這是最可能有缺陷的地方，而且有前例：W5 查出我自己寫的元件完全沒有鎖，而更早的元件都有。兩個行程同時為不同票 `admit_dispatch`，或同時為同一張票，會發生什麼——沒有人測過。

**2. 工人怎麼把 verdict 交回來。** 它可以用 Bash 跑 runtime 的 `review submit`，機制上通，但沒實機驗過。

**3. 對話死掉留下的孤兒 receipt。** 工人不在了、receipt 還在。這跟孤兒 lease 是同一族問題，而那一族咬過我們一次。

**4. 隔離 worktree 實際開在哪。** Agent 工具有 `isolation: worktree`，看起來開在 `.claude/worktrees/`，但那是**推測不是量測**——而 owner 有明文規矩：不准在 repo 根目錄外面長資料夾。包含性閘門會擋，但我要先知道它擋不擋得住。

## 第一個交付物是測試，不是抽象

不要先寫新模組。先寫一個會失敗的測試，證明既有機制在並行下成立或不成立：

| Ref | 要求 | 證據 |
| --- | --- | --- |
| P1-R1 | 兩張不同的票並行發放，各拿到自己的 receipt，互不干擾 | 真的多行程，不是執行緒 |
| P1-R2 | 同一張票並行發放兩次，只有一份 receipt 成立，另一次拿到具名拒絕 | 同上；斷言恰好一次 |
| P1-R3 | worktree 在 repo 根目錄外時被拒絕，且**沒有**發出 receipt | 拒絕後查發放紀錄為空 |
| P1-R4 | journal 記得下每一次嘗試，包含被拒絕的 | 讀 journal 斷言 |
| P1-R5 | Router 這側不含任何 host 名詞 | 掃原始碼斷言 `subagent`/`claude`/`codex` 零命中——通用性用測試守住 |
| P1-R6 | 測試有鑑別力 | 反向突變：拿掉包含性閘門，R3 要轉紅 |

R1 到 R4 如果**通過**，代表 Router 這側本來就成立，缺的只有薄薄一層黏合，那是好消息。如果**失敗**，我們就找到一個真缺陷——那更值得。兩種結果都不是白工。

## 之後才做的（先不要做）

工人回傳 verdict 的實機驗證、孤兒 receipt 政策、把 V2 的看板接到這些 receipt 上。等上面證明完再說。

```johnny-status
id = P1
title = 用 Router 記帳管多個平行工人
state = IN_PROGRESS
stage = T | 並行證明 | DONE
stage = G | 黏合層 | OPEN
stage = V | 工人回傳 | OPEN
```
