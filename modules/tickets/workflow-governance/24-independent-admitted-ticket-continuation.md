# 24｜獨立已准入票的接續回放

| 欄位 | 內容 |
| --- | --- |
| State | `CLOSURE_REVISION_03 / OWNER_WAIT_SLICE_LOCAL_INTEGRATED` at `af24945f`；獨立票接續移至同需求 Ticket 30，清單 02 未完成 |
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
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
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

## Closure revision 02：真正 Owner effect wait 與獨立票接續

這是同一票的受限修正，沿用原始需求、finding、審閱證據及工作預算；不新增 PRD、
SPEC、平行狀態機或真實 SQL 執行。既有 SPEC AC 2–4 已宣告具名不可逆 effect wait，
但 POC Profile 漏 `EXTERNAL_DECISION_REQUIRED` 路由。由 Architecture Owner 確認
`IMPLEMENT` 階段的該事件只表示「等待精確 Owner effect 決定」，絕不執行 effect。

1. 在現有 Profile 宣告 `IMPLEMENT + EXTERNAL_DECISION_REQUIRED` 的 `SUSPEND /
   WAIT_FOR_HUMAN` 轉移，使用具名 effect wait reason；來源至少需要唯一的精確 Ticket。
   不得將 `TICKET_DISPATCH_REQUIRED` 或 dispatch receipt 重用為 SQL／外部 effect。
2. 事件攜帶精確 ticket/effect 識別；Router 在 WAIT 前核對事件 ticket 與可信
   `RouterState.artifact_refs` 的唯一 Ticket 一致，缺失／不符／歧義均 `HALT`。
   effect 識別若缺失則拒絕；其業務合法性仍由既有 Host effect gate 驗證，
   不能由此純 Router 的事件自報推定已獲准。
   WAIT 決策只回傳 metadata 識別與原因，不給 capability、Context、effect 權限。
   不增加新的授權來源；此純路由不能被稱為 SQL 執行准入或真實 Host effect gate。
3. 用真實 `RouterEngine.decide` 建立同主線的 A、B 固定回放：A 的具名 SQL effect
   等待，無相依且來源／授權完整的 B 按其**原本已宣告**的安全路由 AUTO_CONTINUE；
   B 缺授權、缺必要來源時維持原阻斷，不借 A 的等待或核准；版本漂移仍由既有
   來源解析閘門處理，不以此純 Router 回放冒充。依既有 planning／依賴
   契約證明 A 仍待決，B 完成不使整條主線完成；若既有契約無法表達，回報精確缺口，
   不偽造主線 PASS。
4. 更新既有 `router-control.md` Continuation 段，僅說明精確 ticket/effect wait
   不凍結無相依且已准入的其他票。同步更新既有 Profile/reference digest pin 和
   pin 測試。不要寫死 SQL、專案路徑、票號或模型名於通用 skill。
5. 新增正反向測試：A wait 的原因與識別、B 合法接續、B 缺證據阻斷、event
   ticket 失配或 effect 識別缺失阻斷、A 相依票不可借 B 通行；Reviewer 對「全域凍結 B」及
   「偷放行 A／無效 B」各做一個可觀察反向突變。候選保留原初稿拒收歷史。

允許在上述四個 library/test 檔與既有 `router-control.md` 內做最小變更。實作者
先獨立提交政策文字，再提交 library/test 與 pin（控制面 gate 不接受單次混合政策
與 runtime 改動）；不新增檔案，不改其他 Profile、SPEC、Grant 或 effect backend。
若需要新的 Host effect 權限、預算、正式環境服務或超出本票路徑，回 `BLOCKED`。
Run：`python -m pytest tests/test_autonomous_collaboration.py tests/test_workflow_router.py -q`、
`mypy --strict`（實際修改的 Python 模組）、`git diff --check`。

## Convergence decision／Closure revision 03：保留要求，拆開准入

Revision 02 的獨審只證明具名 Owner-effect wait；同時確認可信主線、票間相依、B 的
live admission 與來源讀回不在本票可安全證明的現有契約中。原始 A／B 完整驗收及
Finding 不刪除、不重置預算或歷史。為使已獨審的最小可用能力不被假裝成整票完成，
本票現在只准入「A 的精確 effect wait」切片；「B 獨立已准入接續及主線保持開放」
由同一 PRD／SPEC 的 [Ticket 30](30-trusted-independent-ticket-continuation.md) 承接。

本票局部准入所需證據固定為 `e0bbe9e5` 的六個精確檔案、原政策 pin、81 tests／
237 subtests、strict mypy、ticket 身分反向突變紅→綠，以及另一席對落地 blob
等同性的確認。准入只整合純 Router WAIT 路由，**不**發行 Owner effect grant、
不執行 SQL、不得放行 B、不得把本票或清單 02 標成完整完成。任何新增權限或
安全不變量變更仍依既有 Change Control。本 revision 是既有需求的 ticket
拆分，不新增 PRD、SPEC、人工審批關卡或第三次 correction。
