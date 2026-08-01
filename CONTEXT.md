# 通用功能模組庫

本檔案是本專案的共用事實來源。所有功能集群的 SPEC、工單與元素索引只能引用並補充本檔，不得覆寫其邊界。

## 已確認事實與共同邊界

- 專案目標：將使用者授權的既有本機專案中，可安全抽離的功能，重新實作為可重用、強型別且可測試的通用模組庫。
- 授權來源專案僅供唯讀參考：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 `來源專案D`；本專案不得回寫、搬移或修改它們的任何檔案。
- 首要功能集群為：NLP、金流串接，以及可靠性、LINE transport、身份解析、地理解析、互動／遊戲規則等其他候選集群。
- 產物必須重新定義資料模型、公開介面、依賴與測試；不得直接複製來源專案的秘密、設定、營運資料、租戶資料、資料庫 schema、PII、憑證或網域業務規則。
- `來源專案D` 的 ML 訓練產物僅可作為離線分類／品質分析的參考，不能成為對外訊息、派單或付款決策的權威。
- SourceProjectA 金流原始碼受其 P0／P1 部署與驗證閘門限制；本專案只抽取可測試的付款契約、idempotency、帳本與 provider adapter 模式，不能宣稱相容或可啟用既有正式收款。
- 每個實作模組資料夾都必須有 README，說明責任、公開契約、相依、禁止用途、來源追溯與驗證命令。

## 識別碼登錄

- SPEC 專案代號：`AI-WORKFLOW`。
- SPEC 功能鍵：全大寫 kebab-case，穩定對應 `modules/spec/<feature>.md`。
- SPEC 格式：`SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`。

## 衍生 SPEC 索引

### `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`｜通用功能模組庫

- 規格路徑：`modules/spec/reusable-module-library.md`
- 專屬 Context：`doc/context/reusable-module-library/main.md`
- 原引用章節：`已確認事實與共同邊界`
- 收斂結果摘要：已核准將來源專案的候選能力分為 NLP、金流與其他功能集群；只在本專案重新實作可驗證的通用邊界。
- 責任範圍：本機通用模組庫與 README；不含任何來源專案、部署、外部 provider、真實資料或憑證操作。
- PRD／需求變更：`PRD.md §1`／`CHG-20260801-001`
- 回掛 commit：待文件基準提交；工單待第二次核准。
