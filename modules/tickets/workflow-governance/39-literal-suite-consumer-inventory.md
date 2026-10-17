# 39｜追蹤具名 SUITES 清單的間接測試消費者

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN / INVENTORY_SLICE_ONLY`；不得由此授權測試退役 |
| Authority | 既有 `PRD-20260805-009`、已核准 workflow-governance SPEC、Owner 改進清單 08 與 2026-10-18 第 6 項；不建立新 PRD |
| Baseline | 本票 docs-only commit，派工時釘完整 SHA |
| Owner／reviewer | 低成本實作席位；獨立審閱另席；Root 控制面 |
| Profile | `COMPACT`；純 AST inventory，無來源執行、Git mutation、網路或正式 effect |

## 先查重用與邊界

沿用 Ticket 32 的 `PythonTestConsumerInventory` 與 Ticket 36 的釘選 Git blob adapter；
不得另造 graph、CI parser、測試 runner 或退役引擎。`SUITES` 是本票唯一新識別形態，
只處理 Python module-level 的靜態 literal 清單／tuple／set／dict 中明確指向已知
測試 source 的字串；未能安全解析的 expression 一律 `UNRESOLVED`。

```johnny-boundary
modify = library/local_orchestration/test_dependency_inventory.py
modify = tests/test_test_dependency_inventory.py
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
forbid = library/local_orchestration/test_dependency_source_adapter.py
```

## Work／驗收

1. 在既有 AST inventory 將 module-level `SUITES` 的靜態測試路徑／模組引用納入
   consumer edge；同一 source 經 `SUITES` → wrapper import → declared CI command 的
   直接與傳遞消費者均可查到。不得從 Actual／測試結果推斷依賴；`SUITES` 名稱以外
   的任意程式變數不猜測。
2. 動態值、重複賦值、無法識別的測試字串與引用未知檔案不能回 `COMPLETE` 空圖；
   必須以既有 `UNRESOLVED` 語意 fail-closed。合法純 literal 且無消費者可回空圖，
   `retirement_authorized` 永遠維持 false。
3. 固定虛構情境：CI 只直接呼叫 `tests/test_consumer.py`，該檔 import
   `tests/test_suite_registry.py`，後者 `SUITES = {'smoke': ['tests/test_helper.py']}`。
   查 `test_helper` 時必列 registry 直接消費與 consumer/CI 傳遞消費；把 helper
   的 `SUITES` 引用拿掉應使具名格轉紅，還原轉綠。前置紅燈不許當作沒有消費者。
4. 只改上述兩個既有檔案；不新增檔案、PRD、SPEC、框架或大型測試腳本。
   預期產品碼增量約 35–70 行、測試約 35–70 行、文件與持久證據 0；
   修正沿用同票同預算。行數是結構審查訊號，不准靠壓行或隨意拆檔達標。

Run：`python -m pytest tests/test_test_dependency_inventory.py tests/test_test_dependency_source_adapter.py -q`、
`mypy --strict library/local_orchestration/test_dependency_inventory.py`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選 SHA、兩個實際檔案、
測試／反向突變證據與未完成的真 CI 命令及退役 gate 缺口。實作者不整合、不推送。
