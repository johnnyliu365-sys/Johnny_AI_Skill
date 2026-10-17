# 25｜重構時 TEST → A → B 的測試接線轉移

| 欄位 | 內容 |
| --- | --- |
| State | `IN_PROGRESS`；Owner 2026-10-18 改進清單項目 04 |
| Authority | 既有 `PRD-20260805-009`／`CHG-20260805-009` 與 `modules/spec/workflow-governance.md` 的逐行為驗證；本次 Owner 指示補足重構接線，不新增 PRD |
| Source baseline | `7a391b9d96d539db0f5afdfab3334d98638fcd61`；獨立 worktree |
| Implementation language | Markdown 政策／模板；Python 3.11 pin 與回放測試 |
| Implementation owner / reviewer | 不同席位；主 session 只處理控制面 |
| Profile | `STANDARD`：跨測試接線與產品 seam 的重構驗收；不含真服務／外部 effect |

## 邊界宣告

```johnny-boundary
modify = skills/johnny-project-takeover/references/implementation-tdd.md
modify = modules/tickets/TEMPLATE.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
modify = tests/test_private_router_metadata_gate.py
forbid = modules/spec/
forbid = doc/requirements/
forbid = library/workflow_router/private_router.py
```

所有政策文字只放 skill/template，不把 Owner prompt、工單敘事或測試情境塞進正式原始碼。不可把 profile pin 的修改當作產品拆分完成。

## Objective／Work

重構同一能力時，先固定能力的可觀察測試與承接計畫（TEST），才改第一個產品責任邊界（A）；A 的候選版必須通過真實使用入口及新 seam 的負向突變，再進第二段（B）。測試只檢查舊入口是否委派新 service，不足以證明 service 的行為。

1. 在現有 `implementation-tdd.md` 的「One behavior at a time」或 TDD/Smoke 邊界補精確的 TEST→A→B 接線規則：每段指明產品入口、當下被測實作 seam、能力輸入輸出、負向突變目標、測試承接/舊測試退役條件；A 之後先在候選版驗證，再開 B。不要新增 Stage／Gate／平行流程。
2. 在既有 Ticket 模板的 TDD 區加適用於責任拆分票的精簡欄位：TEST seam、A source/target、B dependency、測試接線與突變轉移。非拆分票填 N/A reason，不得要求所有票額外儀式。保持 `johnny-boundary` 及既有模板結構。
3. 更新 `implementation-tdd.md` 的兩處正式 digest pin，並跑原有 pin test。
4. 固定回放一個現有 Router→service 路徑：在既有 `tests/test_private_router_metadata_gate.py` 增加或指認真正穿過 `PrivateRouterClient` 與 `FakePrivateRouterService` 的行為斷言。審閱時對 service 行為而非 client 委派本身做反向突變，須讓該能力 cell 轉紅，還原回綠。若既有測試已足夠，勿重複加大型腳本，回傳精確既有 cell。

## Acceptance／停止

- 正常：TEST 規劃可精確指定 A/B 各自的產品與測試 seam；候選 A 行為驗證與 service 突變紅／還原綠可重跑，B 必須依賴 A 綠的證據。
- 失敗／邊界：只驗委派而 service 被改錯，不得報能力承接完成；候選版沒跑、只跑舊 baseline，不得進 B。
- 本票不移動任何生產 Router 邏輯，不新增檔案，不修改 Vita360。若需要修改正式 SPEC/AC 才能解釋 A/B，回 `CHANGE_DETECTED`。

Run：`python -m pytest tests/test_workflow_router.py tests/test_private_router_metadata_gate.py -q`、`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選完整 SHA、實際路徑、命令結果、突變 target/cell/紅綠輸出、scope deviations、未驗證項。獨審由另一席作獨立反向突變。
