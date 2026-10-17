# 30｜可信的獨立票接續與主線保持開放

| 欄位 | 內容 |
| --- | --- |
| State | `PREFLIGHT_REQUIRED / NON_DISPATCHABLE`；承接 Ticket 24 revision02 未完成的 B 閉包 |
| Authority | 同一 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md` AC 1–4 及 Owner 2026-10-18 清單 02；不新增需求身分 |
| Source baseline | Ticket 24 A 切片受控整合後的精確本地 commit，派工前 pin |
| Owner / reviewer | 低成本實作席位與另一獨立審閱席位；Root 控制面 |
| Profile | `STANDARD`；不執行真實 SQL、外部模型或正式環境 effect |

## 狀態及既有能力

Ticket 24 的 Owner-effect wait 只處理 A。Ticket 29 的 `mainline_projection` 只處理
不可變 metadata 讀取；它沒有可信 target source、live 授權或正式 closure 權力。
這兩者都不能單獨證明 B 的接續。沿用既有 Router、ticket/source admission、
`CollaborationDispatchPlan`、Review 與受控整合，不建立第二套 Router／狀態機。

## Preflight 待解的精確邊界

由 Architecture Owner 在派工前從現有 target-versioned 來源與 Router 呼叫路徑
釘定：主線 ID／revision、A/B/C 的 dependency、每票的有效 grant/admission、
live source readback、完成證據，以及哪個既有入口消費該投影。盤點完才列精確
modify/create/forbid 路徑與預算。本票目前**沒有可用的 `johnny-boundary`**，因此
不得派工，也不得用 Agent 自報的主線／grant／版本填空。這是受限前置設計，不是
額外人工核准關卡；若既有授權不足才升級 Owner。

## 必須保存的驗收

- A 的具名 Owner wait 不轉移 authority；B 在同主線、無相依、且自身有效准入時
  走自己原有安全路由；A 等待不全域凍結 B。
- B 缺 grant/source、來源漂移或依賴 A 時拒絕；不能借用 A 的證據或 receipt。
- B 結束後 A 仍待決，主線未結案；必要／可選子項及 Finding 去向仍依既有
  Review／closure 進行，不讓 metadata 投影自授權。
- 固定 A/B/C 情境進入真實 Router/Host admission 入口；對全域凍結與無效放行
  各做獨立負向突變。原 Ticket 24 的失敗證據、預算及 Review 歷史持續引用。

只有 preflight 產出有界、可驗證的入口與精確路徑後才能設定 `OPEN` 並派工。
不得為了綠燈放寬已核准的安全不變量。
