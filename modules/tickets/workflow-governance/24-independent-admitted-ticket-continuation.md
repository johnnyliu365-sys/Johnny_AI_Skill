# 24｜獨立已准入票的接續回放

| 欄位 | 內容 |
| --- | --- |
| State | `REVIEW_CHANGES_REQUESTED / CAPABILITY_GAP`；Owner 2026-10-18 改進清單項目 02 |
| Authority | `PRD-20260805-009`、`CHG-20260805-009`、`modules/spec/workflow-governance.md` AC 1–4；本票只驗證現行授權內的接續，不改批准含義 |
| Baseline | `7c1660e53f0789a416f5858d933519af76ef5b9b`；同一 repo 的獨立 worktree |
| Implementation language | Python 3.11；政策文件 Markdown |
| Implementation owner | 低成本實作席位，單票 worktree；不得自審 |
| Reviewer | 與實作者不同的獨立席位；主 session 保持控制面 |
| Profile | `STANDARD`：跨兩個票級狀態的接續契約；無外部模型／正式環境 effect |
| Environment | 隔離本地測試，不碰 Vita360、正式 DB、付費 API、Push、Release |

## 邊界宣告

```johnny-boundary
modify = tests/test_autonomous_collaboration.py
modify = skills/johnny-project-takeover/references/router-control.md
modify = library/workflow_router/router.py
modify = library/workflow_router/contracts.py
create =
delete =
forbid = modules/spec/
forbid = doc/requirements/
forbid = .worktrees/
```

`router.py`／`contracts.py` 只在測試揭示現有契約無法滿足時才可窄修；不得新增平行 Router、queue、runner、receipt 或全專案人工等待狀態。不得修改已確認無問題的票／功能。

## Objective 與依賴

同一主線內，一張票因精確 Human Owner effect 等待時，不得把另一張**無相依且已有有效 admission** 的票一起凍結；待人工作業的票不得自行越權。延續同一 PRD/SPEC，不新增需求身分。前置依賴是現行 `RouterEngine.decide`、既有 `CollaborationDispatchPlan` 與 `Workflow.md` 的 `AUTO_CONTINUE / WAIT_FOR_HUMAN / HALT`；不得把一張票的 receipt 用於另一張。

## Work／Expected

1. 先新增固定情境測試，分別建立票 A、票 B 的精確狀態和事件：A 的 SQL／不可逆 effect 需要 Owner 決定，B 是不同票、無相依、來源與授權完整的安全下一步。A 回 `WAIT_FOR_HUMAN`，B 照既有 Profile `AUTO_CONTINUE`；A 的等待原因和證據不能轉借 B。
2. 測試另一條邊界：B 若來源版本、授權或 admission 有誤，必須仍由原有阻斷規則停止；不得因 A 等待而跳過或放寬 B 的 gate。
3. 在 `router-control.md` 的現有 Continuation 段補充「等待只作用於精確票／effect；同主線中其他獨立已准入票仍依各自 authority 判定」。每次 effect 前只重查該票受影響的 live source／scope，不以聊天記憶替代。不要新增第二套全域狀態或審批。
4. 若測試顯示現有 Router 做不到，只在列出的 Router 檔窄修；若需要改既有 SPEC、authority schema 或超出票級邊界，回 `CHANGE_DETECTED`，不猜需求。

## Acceptance／停止條件

- 正常：A 等待，B 自動接續；A 的結果保持待決且主線不可被首票完成誤標完成。
- 失敗／邊界：B 缺有效授權、來源漂移或與 A 有相依時，不能借用 A 的放行。`WAIT_FOR_HUMAN` 必須具名；缺證據仍 fail closed。
- 測試需在真實 Router 呼叫路徑進入，不能只檢查 helper；對「全域等待使 B 停住」或「偷放行 A／B」各有一個可觀察的負向斷言。
- 不新增檔案、PRD、SPEC、模型呼叫或外部 effect。若現有 Profile 無法表達無相依關係，不自行發明新的 authority 欄位；回 `BLOCKED` 附精確缺口。

## Run／Return

Run：`python -m pytest tests/test_autonomous_collaboration.py -q`、`git diff --check`。獨審另作一次反向突變，證明至少一個新斷言在相反結果時轉紅，再還原回綠。

Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選完整 SHA、實際變更檔、命令／退出碼、測試結果、發現、scope deviations、未驗證項。實作者不整合、不推送；Review 不得由同席完成。

## Review 01 / pending correction

獨審結論 `CHANGES_REQUESTED`，精確證據見
`doc/reviews/workflow-governance/24-independent-admitted-ticket-continuation-code-review.md`。
目前候選僅證明派工確認等待，不證明 SQL/不可逆 effect 等待或主線相依；
`EXTERNAL_DECISION_REQUIRED` 在事件列舉中存在，但現行 POC Profile 未宣告對應轉移。
不得把此候選算作項目 02 完成，也不得藉修正自行新增權限。
