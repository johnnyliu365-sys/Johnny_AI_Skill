# 38｜派工前固定重用與責任邊界證據

| 欄位 | 內容 |
| --- | --- |
| State | `TEMPLATE_SLICE_LOCAL_INTEGRATED` at `3557bc20`；不得宣稱已具 Host dispatch admission 或語意耦合自動判斷 |
| Authority | 既有 `PRD-20260805-009`、Owner 2026-10-18 清單 03／11 及「程式與腳本不得堆疊」指示；不新增 PRD／SPEC |
| Baseline | 本票 docs-only commit，派工時釘完整 SHA |
| Roles | 低成本實作席位、不同獨審席位、Root 控制面 |
| Profile | `COMPACT`；本票只改既有模板及其測試，不呼叫外部模型或產品 effect |

## 查重與精確邊界

### 38B：開發前責任圖與候選整合檢查（local construction）

Owner 2026-10-29 指示明確涵蓋程式及腳本：開發前建立責任邊界、
BOUNDARY_MAP 與 shared，並以可執行檢查約束修改。沿用本票、
PRD-20260805-009、原 SPEC AC-10/11 及批次本地授權；不新增 PRD。
Architecture Owner /root/authority_topology_architecture 判定為 STANDARD：
多個本地元件與共享契約、可逆、無 privileged/外部 effect。既有38A結果保留。

38B State：SOURCE_BUILD_ADMITTED / NOT_HOST_ENFORCED。先依現行規則建置及
驗證新能力，不能要求尚未存在的 map 才能建置 map 本身。新規則的全域
強制啟用不在本次建置內；既有合法、未綁新 map 的票不因此全部凍結。
30B/43、Host qualification 與安裝 Recovery 均不因38B而變更。

Control：/root。Implementation：/root/native_service_impl，限定接管既有
`.worktrees/skill-improvement-38`、branch `codex/skill-improvement-38`。
Independent review：/root/authority_install_inventory，既有
`.worktrees/skill-improvement-38-review`、branch `codex/skill-improvement-38-review`。
舊 allocation 已完成；不得修改 native-service 或任何其他 worktree。
建置前將乾淨3557bc20以 fast-forward 接到含本段的 control commit，讀回 exact
HEAD/ticket blob 後作為唯一 implementation baseline；這是本批文件變更，不
自動納入其他 source candidate。Root記錄最終SHA及leaf LF digest於dispatch。

Grant ID `batch-checklist-local-20261019-uncapped/t38b-boundary-map-local-01`：
簽發者 Root，依既有批次派生授權，非 implementer 自發；用途限以下精確本地
CREATE/MODIFY、測試、additive修正、獨審與受控本地整合。保留歷史記帳、
單次命令逾時/資源監控；無累計秒數/固定修正次數重置。無 push/release/
deployment/帳戶/ACL/服務/Host/model/network/正式閘門啟用授權。

38B 精確邊界（下列取代舊38A兩檔 scope，僅限本次切片；無 DELETE）：

```johnny-boundary
create = shared/BOUNDARY_MAP.toml
create = library/local_orchestration/boundary_map.py
create = tests/test_boundary_map.py
modify = modules/tickets/TEMPLATE.md
modify = template/modules/tickets/TEMPLATE.md
modify = tests/test_ticket_template_contract.py
modify = library/local_orchestration/document_mutation_gate.py
modify = tests/test_document_mutation_gate.py
forbid = modules/spec/
forbid = skills/
forbid = AGENTS.md
forbid = library/local_orchestration/native_windows/
```

本段新舊兩個 fence 是歷史與新allocation分期，不可直接交給first-match parser。
Root須在dispatch前將下方舊scope移為history的非johnny-boundary fence，保留唯一
活躍38B區塊；不得讓候選自己擴權。控制文件不在實作者scope。

BOUNDARY_MAP 唯一來源固定 `shared/BOUNDARY_MAP.toml`，TOML schema revision1、
scope LOCAL_SOURCE_BOUNDARY。每個module有唯一id、精確無wildcard roots、
owner、單一responsibility、LIBRARY/SHARED/HARNESS/SCRIPT/TEST kind、
allowed_dependencies及optional共享alias。拒絕未知key/ID、重複/重疊roots、
非canonical路徑與case碰撞；shared是查重/共用件映射，不是萬用utils堆積區。
沿用既有library/harness位置，不為新名稱搬動已確認功能。

38B-F1：map缺失/型別錯誤/owner或responsibility空白/unknown dependency/
ambiguous ownership須有限拒絕；合法map正常建構並通過。單票固定map digest、
baseline及selected module IDs；三者缺失/不符不能PASS。
38B-F2：actual Git diff的每個新增/修改/刪除程式、測試、腳本恰好歸一個已選模組。
Python AST讀候選實際import/from（含relative），非允許內部依賴與產品依賴
測試須拒絕。未解析動態載入/syntax failure/無合格parser的腳本須NOT_VERIFIED，
不是PASS；不能用regex冒充PowerShell AST。語意重複/職責是否合理仍由reviewer判斷。
38B-F3：重用既有document_mutation_gate的Git讀取與diff/normalize/path拒絕，
只在既有merge前接一次檢查；從integration側的固定map/ticket讀回，candidate
自改map不能放寬自己的檢查。非PASS時原integration HEAD不動；合法候選確實可
通過原入口整合。新舊解析不得產生循環import或第二套path/Git framework。
38B-F4：雙份模板同步要求開工前讀map、綁定模組與重用來源；既有38A與completion
測試維持。不得將模板文字或local gate當成Host prewrite/spawn攔截證據。

新檔責任：map為唯一結構資料；boundary_map.py為有界typed parser/evaluator，
消費者為原document gate與聚焦測試；test_boundary_map.py只測上述契約/依賴。
預期增量：產品2檔modify+1檔create（新增checker目標<500有效行，超過則結構審查，
不壓碼或為行數拆碎）；測試2modify+1create（重用既有Git fixture，拒絕大型新框架）；
模板2modify；資料1create。產物預設pytest暫存，無截圖/正式repo新證據腳本。

驗證：聚焦pytest（三個既有/新增test files）、strict mypy於受影響產品模組、
compile/import、git diff --check；每命令60s，逾時先定位。負例含stale digest/
wrong baseline/self-widen/未選模組/unowned/case/path traversal/產品import harness/
relative/dynamic/unsupported script；保留合法candidate整合正例。作者反向突變
及reviewer至少一個不同門突變須具名轉紅、精確還原綠。禁止全部拒絕換通過。
Return：IMPLEMENTED/BLOCKED/CHANGE_DETECTED、exact candidate/files/checks/
findings/deviations/NOT_VERIFIED。獨審前不整合、不啟用全域強制規則。

沿用 `modules/tickets/TEMPLATE.md` 的 `johnny-boundary` 和
`document_mutation_gate.py` 已有的 Git-diff 路徑拒收，不另建 Gate。
沿用 `tests/test_ticket_template_contract.py` 的活躍 section／bullet 與反向突變
測試，不另造 parser 或測試框架。此票只讓單票在派工前承載可檢查的最小結構
決策；Host 是否確實消費該票仍是清單 03 的未解外層缺口。

```text
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
