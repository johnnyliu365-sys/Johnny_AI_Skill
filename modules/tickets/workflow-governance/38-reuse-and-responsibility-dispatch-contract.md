# 38｜派工前固定重用與責任邊界證據

| 欄位 | 內容 |
| --- | --- |
| State | `TEMPLATE_SLICE_LOCAL_INTEGRATED` at `3557bc20`；不得宣稱已具 Host dispatch admission 或語意耦合自動判斷 |
| Authority | 既有 `PRD-20260805-009`、Owner 2026-10-18 清單 03／11 及「程式與腳本不得堆疊」指示；不新增 PRD／SPEC |
| Baseline | 本票 docs-only commit，派工時釘完整 SHA |
| Roles | 低成本實作席位、不同獨審席位、Root 控制面 |
| Profile | `COMPACT`；本票只改既有模板及其測試，不呼叫外部模型或產品 effect |

## 查重與精確邊界

沿用 `modules/tickets/TEMPLATE.md` 的 `johnny-boundary` 和
`document_mutation_gate.py` 已有的 Git-diff 路徑拒收，不另建 Gate。
沿用 `tests/test_ticket_template_contract.py` 的活躍 section／bullet 與反向突變
測試，不另造 parser 或測試框架。此票只讓單票在派工前承載可檢查的最小結構
決策；Host 是否確實消費該票仍是清單 03 的未解外層缺口。

```johnny-boundary
modify = modules/tickets/TEMPLATE.md
modify = tests/test_ticket_template_contract.py
forbid = library/
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
```

## Work／驗收

1. 在既有「實作範圍、依賴與 ticket elements」節加入一個有界的結構決策欄，
   指名實際重用的生產模組／共用測試 harness 與依賴方向；若不重用，寫具體原因。
   每個允許新增的程式或腳本檔須有獨立責任、消費者與驗收格；不得因換票重新
   建立 browser、mock、fixture、decoder、pixel comparator 等已有共用件。
2. 對現有與新檔分開列預期產品碼、測試／腳本、文件及證據產物增量；同票修正
   沿用原預算。數量／行數只觸發結構審查，不作自動拆檔、縮碼或放行依據。
   已通過且不在本票邊界的功能／介面不得為修正另一問題順手改動。
3. 測試預設在隔離暫存處產物；只有票中具名、必要的證據檔可以寫入正式樹。
   原始碼與腳本保留必要技術註解，不得加入 owner prompt、工單敘事或治理副本。
4. 擴充**既有**模板測試：填票情境須能讀出上述活躍欄位，刪除、註解或移到
   錯節的獨立突變須令具名格轉紅；原模板已有的 Expected、`johnny-boundary`、
   reviewer 與停止條件測試不得退化。使用虛構通用案例，無真實 target 路徑。
5. Reviewer 對照兩檔實際 diff、測試與反向突變，確認此票沒有聲稱模板文字
   能在 Agent 寫入前攔截檔案，亦未把語意耦合偽裝成機器可判定。

Run：`python -m pytest tests/test_ticket_template_contract.py -q`、
`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整候選 SHA、
實際兩檔、驗證與突變證據、未解 Host admission／結構語意缺口。
不新增檔案、PRD、SPEC、Gate、Framework，不整合、不推送。

## 實作與獨審

初版 `f95face6` 被獨審指出目錄型 `create` 未逐檔綁定責任、暫存樣本會污染
Git worktree。原實作者在同票 correction commits `d28f55ca`、`3557bc20` 修正兩項
與樣本預算數量不一致；原 reviewer 用兩個不同的填票入口反向突變驗證轉紅→綠，
最終 35 項測試、`git diff --check` 綠。既有 document-mutation gate 直接以精確
reviewed candidate 回傳 `INTEGRATED` at `3557bc20`。詳見
`doc/reviews/workflow-governance/38-reuse-and-responsibility-dispatch-contract-code-review.md`。
本票只完成模板切片，不使清單 03／11 的 Host／語意結構缺口消失。
