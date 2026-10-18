# 40｜新專案工單模板與現行派工契約一致

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN / DISPATCHABLE`；只收斂 scaffold 模板斷邊，不宣稱 Host admission 已完成 |
| Authority | 已核准 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md` AC 5–8、Owner 2026-10-18 checklist 03／11 與本輪繼續完成指示；不新增 PRD |
| Baseline | 本票 docs-only commit 的完整 SHA；派工前固定 |
| Roles | 低成本 implementation owner、不同獨立 reviewer、Root 控制面 |
| Profile | `COMPACT`；本機模板與測試，沒有 target 寫入、外部模型或發布效果 |

## 已確認斷邊與重用

`template/README.md` 明示新專案複製 `template/modules/tickets/TEMPLATE.md`，但目前
`tests/test_ticket_template_contract.py` 只驗本庫 `modules/tickets/TEMPLATE.md`。前者仍缺
後者的核准 Expected、停止條件、`johnny-boundary`、重用／新檔責任／預算及測試接線欄。
沿用現有模板測試的 active section／bullet helper，不新增 validator、派工閘門、測試框架。
這張票只修出貨 scaffold；Host 是否讀取已填票件仍是 checklist 03 的獨立缺口。

```johnny-boundary
modify = template/modules/tickets/TEMPLATE.md
modify = tests/test_ticket_template_contract.py
forbid = library/
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
```

## Work／驗收

1. 在既有 scaffold 模板補齊現行單票必需的核准 SPEC revision、可觀察 Expected、
   正常／失敗／邊界驗收、需求變更停止條件、`johnny-boundary` 的 modify/create/delete/forbid、
   角色隔離、具名 I/O、直接依賴、共用件重用、逐個新增程式／腳本檔責任、原票預算、
   暫存產物、既有行為保留，以及 TEST→A→B 所需的測試接線／反向突變欄。
2. Scaffold 是供 target 建立 target-owned 工單的模板；不得複製 Johnny 插件的
   `library/` runtime 路徑或要求 target 安裝插件後才能執行測試／CI。凡僅由本庫
   的整合器提供的機械保護，模板須誠實標明為 host／reviewer admission 的責任，
   不以文字宣稱寫入前已硬攔截。
3. 擴充同一測試檔，以虛構通用工單填入 scaffold，驗證必要活躍欄位與 canonical
   模板的結構義務一致；至少對 scaffold 的 Expected、停止條件、重用及新增檔責任
   各做缺失／移位反向突變紅→綠。測試不得只搜尋靜態字串，也不得把 target
   特定路徑、SHA、模型名寫入通用模板。
4. 只修改上列兩檔，不新增檔案。預期 scaffold 文檔約 +70～130 行、既有測試約
   +45～90 行；修正沿用同一預算。行數只作結構審查訊號，不逼拆檔或壓行。

Run：`python -m pytest tests/test_ticket_template_contract.py -q`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整候選 SHA、實際兩檔、
具名測試與反向突變結果、scope deviations、未完成的 Host 派工准入缺口。
Implementation owner 不整合、不推送；reviewer 獨立讀回、突變與判定。
