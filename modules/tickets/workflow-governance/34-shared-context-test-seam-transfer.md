# 34｜Shared Context 測試責任接線與舊格退役（B）

| 欄位 | 內容 |
| --- | --- |
| State | `B_LOCAL_INTEGRATED` at `b4a7dbe6`；獨審通過、五格契約測試已搬遷 |
| Authority | 同一 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md`；Ticket 25 的 TEST→A→B 規則；Ticket 33 A `ac369235` 已獨審且整合 |
| Baseline | 派工時精確釘選本控制分支 HEAD；獨立 repo-contained worktree |
| Profile／roles | `STANDARD`；低成本實作者與另一席獨立審閱；Reviewer 強度不低於實作 |
| Nature | 測試接線／既有格轉移；產品 code 與已核准 Expected 不變 |

## 邊界宣告

```johnny-boundary
modify = tests/test_workflow_router.py
modify = tests/test_shared_context_service.py
forbid = library/
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
```

不新增檔案，不建立共用測試框架。`tests/test_workflow_router.py` 已逾三千行；這張票把 Shared Context **contract-only** 格放到已存在的聚焦測試檔，避免繼續堆疊。聚焦檔維持 service 邊界與其輸入契約的單一能力責任；重用該檔 `_request`／`_state` fixture，不複製一套大型 helper。

## 已封存的 A 證據／TEST seam

- A source：原 `RouterEngine.decide_shared_context_access` 規則；A target：`SharedContextAccessService.decide_access`，Git blob 於 `ac369235` 與受審候選完全相同。
- 公開使用入口仍為 `RouterEngine.decide_shared_context_access`，不是單純 service 單測。Ticket 33 Reviewer 已在新 service 改壞 sealed read 和 writer role，使公開 Router cells 轉紅、還原綠。
- B 前先在固定 A baseline 跑 `tests/test_workflow_router.py` 與 `tests/test_shared_context_service.py`；記錄現有 cell 身分及 subtest 結果。

## B 工作

1. 將下列五個 **contract-only** test methods 從巨大 Router 測試檔移至現有 Shared Context 聚焦檔，沿用相同 Expected 與 negative rows，不得以簡化為由刪除 assertion／subtest。方法可以改名，但交付須列逐格對照：
   - `test_shared_context_contracts_round_trip_and_reject_operation_matrix`
   - `test_shared_context_manifest_and_state_are_metadata_only`
   - `test_shared_context_profile_accepts_distinct_project_metadata`
   - `test_shared_context_manifest_accepts_semantic_tree_reference_ids`
   - `test_shared_context_rejects_reserved_expected_revision`
2. Router 測試檔保留 `test_shared_context_public_entrypoint_exists` 與其餘五個 **公開入口行為** 格，不得改成只斷言委派呼叫、不得改 Expected。其 sealed-read、writer-role、revision/change-control 仍須穿過實際 Router→service seam。
3. 退役條件是新檔五格逐項綠、公開入口六格保留並綠、對應負向突變仍紅；舊格才可從原檔移除。只移走上述 contract-only 格，不順手重排其他 Router 測試。

## Acceptance／停止

- 正常：候選產品 A 的同一 SHA/blob 不變；候選 B 兩測試檔通過，五格有逐項對照；既有公開入口行為仍抓得到新 service 故意改錯。
- 失敗／邊界：不能把測試搬到新檔卻載入舊產品 baseline；不能只比 test 總數、不能刪掉原有 negative rows；B 僅是測試接線，不得回報為第二次產品拆分。
- 若搬遷需要改生產 contracts、SPEC、AC 或新增檔案，回 `CHANGE_DETECTED`；不自行擴大。

Run：`python -m pytest tests/test_workflow_router.py tests/test_shared_context_service.py -q`、`python -m mypy --strict tests/test_shared_context_service.py`、`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選完整 SHA、五格對照、前後測試數／subtests、公開入口格、偏差與未驗證項。獨審另席在隔離工作樹對新 service 分支作反向突變紅→還原綠，並檢查五格的 negative-row 保存。
