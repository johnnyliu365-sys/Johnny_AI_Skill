# 36｜從釘選 Git 來源讀取測試消費者

| 欄位 | 內容 |
| --- | --- |
| State | `SLICE_LOCAL_INTEGRATED` at `e1ca2d4b`；承接 Ticket 32，清單 08 仍未完成 |
| Authority | 既有 `PRD-20260805-009`／`CHG-20260805-009`、Owner 清單 08；不新增需求身分 |
| Baseline | 本票 docs-only commit；派工時精確 pin |
| Roles | 低成本實作席位與不同獨審席位；Root 控制面 |
| Profile | `STANDARD`；只讀本地 Git 已釘選 commit，不執行測試或修改工作樹 |

## 先查重用與邊界

Ticket 32 的 `PythonTestConsumerInventory` 已有純 AST 圖與 `UNRESOLVED` 語意；本票不得複製解析器。`plugin_publication.py` 有自己的 Git tree 讀取，但屬發布邊界，不能讓測試來源依賴它。新增一個單責 Host adapter 將精確 Git tree 的 Python blob 餵給現有 inventory；同一模組只保留釘選來源與讀取結果，不做退役決策。不得重用工作副本文字、`git status` 自報或當前 `HEAD` 代替傳入的完整 commit SHA。

```johnny-boundary
create = library/local_orchestration/test_dependency_source_adapter.py
create = tests/test_test_dependency_source_adapter.py
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
forbid = library/workflow_router/
forbid = library/local_orchestration/test_dependency_inventory.py
```

## Work／驗收

1. 只接受已存在的完整 commit SHA 及 repository root；從 Git committed tree 讀取有界的追蹤 Python blobs，將來源相對路徑、UTF-8 內容交給現有 `PythonTestConsumerInventory`。結果攜帶精確 commit 身分，不能把當前工作副本或其他分支內容混進去。非 commit、無效 root、超出大小／檔數界線、symlink/gitlink、不合法路徑、不可解碼 blob 與 Git 失敗均具名 fail-closed；不得執行來源中的 Python 或 shell。
2. 固定 temp Git 情境：CI 直接命令只命名 consumer，consumer 經 wrapper/import 指向 helper；從釘選 commit 讀取後 `retirement_inventory(helper)` 必須列直接與傳遞消費者。再改工作副本、切換 HEAD、在新 commit 刪除依賴，釘選舊 commit 的盤點不能漂移；釘選新 commit 才可變。前置測試紅燈不構成忽略下游消費者的理由。
3. `DeclaredTestCommand` 仍需呼叫端提供；本票不宣稱已從真 CI 配置可信解析命令，也不授權刪除舊測試。未辨識入口維持既有 `UNRESOLVED`。讀取上限與命令 timeout 是有界工程保護，不新增背景掃描、Runner 或第二套 dependency graph。
4. Reviewer 從不同門突變 commit pin 或間接邊，使具名格轉紅，再還原綠；確認合法無消費者來源可被讀取，但 `retirement_authorized` 仍為 false。

Run：`python -m pytest tests/test_test_dependency_source_adapter.py tests/test_test_dependency_inventory.py -q`、`mypy --strict library/local_orchestration/test_dependency_source_adapter.py`、`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選完整 SHA、檔案、測試、反向突變目標、未驗證 CI／退役缺口。實作者不整合、不推送。若無法在本票兩檔內保證釘選來源或需要新授權來源，回 `CHANGE_DETECTED`。

## 實作與獨審結果

初版 `1d96fafe` 的獨審拒收兩項 Closure 1 缺陷：Git replace ref 可令同一舊 SHA 的內容漂移，非 `.py` gitlink 被略過卻回 COMPLETE。原票 additive correction `4c6cfbeb` 關閉兩項；原 reviewer 從公開入口重跑 commit/blob replace 與非 `.py` symlink/gitlink 負例，並複驗兩項反向突變紅→綠。最終 26 tests／2 subtests、strict mypy、diff check 通過；受控整合 `e1ca2d4b` 的兩個 Git blob 與受審候選相同，本地再跑 26 tests／2 subtests 和 strict mypy 通過。詳見 `doc/reviews/workflow-governance/36-git-pinned-test-source-inventory-code-review.md`。真 CI 命令仍由 caller 提供，退役授權始終為 false，不得把此切片勾成清單 08 完成。
