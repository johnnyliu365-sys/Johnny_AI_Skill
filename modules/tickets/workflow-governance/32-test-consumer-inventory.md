# 32｜測試退役前的實際消費者盤點

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN`；Owner 2026-10-18 改進清單項目 08 的有界切片 |
| Authority | 既有 `implementation-tdd.md` 的 TEST→A→B 承接／退役條款與 Owner 本次清單 08；不新增需求身分 |
| Baseline | 本票所在控制面 commit；派工時 pin |
| Owner / reviewer | 低成本實作席位、另一席獨立審閱；Root 控制面 |
| Profile | `COMPACT`；純解析／證據，不執行測試命令、刪除或 Git effect |

## 先查重用與精確邊界

已窄查 `library/local_orchestration/` 與 `tests/`：沒有測試消費者圖或退役分析器；
`runtime_dependency_lock.py` 處理的是 Runtime 依賴鎖，不承擔測試入口關係。
現有 `implementation-tdd.md` 可直接沿用退役條款，不改正文。
單一新模組只處理測試依賴 inventory；單一新測試檔只驗此責任。

```johnny-boundary
create = library/local_orchestration/test_dependency_inventory.py
create = tests/test_test_dependency_inventory.py
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
forbid = library/workflow_router/
```

## 受限工作與驗收

1. 接收由呼叫端已讀取的、具名且精確的 Python source 文字及已宣告的測試入口
   命令；保持純函數，不自行搜尋 repo、不執行 command、不寫檔。用 AST 辨識
   `import tests.foo`、`from tests import foo`、`from tests.foo import bar`、
   `importlib.import_module("tests.foo")` 與 literal `subprocess` argv 中的
   `-m tests.foo`／測試檔路徑，形成被消費者到消費者的精確邊。
2. 對 `SUITES`／wrapper 透過具名 Python import 形成的傳遞依賴做圖遍歷。
   解析不了的 dynamic import、動態命令、字串拼接與非 Python 入口，回
   `UNRESOLVED`，不得當成「無消費者」。不以單一 CI 文本 grep 或 pytest
   綠燈推斷未列入的測試可退役。
3. `retirement_inventory(test_ref)` 回報直接與傳遞消費者及未解析來源；
   只做證據盤點，**不作退役授權**。真正退役仍需 TEST→A→B 候選行為、
   入口切換及 Reviewer 證據；後續 Host/CI 接線另循原流程。本票不刪測試。

固定情境：CI 直接命令未列 `tests.test_helper`，但 `tests.test_consumer` 與
`doc/runbooks/smoke.py` import 它時仍列兩個消費者；wrapper literal
`subprocess.run([sys.executable, "-m", "tests.test_helper"])` 亦列出；
動態 target 拒絕宣稱安全。正向情境中獨立、靜態、沒有 consumer 的 module
只回 inventory 為空，不等於已核准退役。前置失敗不可以遮住下游消費者。

Run：`python -m pytest tests/test_test_dependency_inventory.py -q`、
`mypy --strict library/local_orchestration/test_dependency_inventory.py`、
`git diff --check`。Reviewer 反向突變忽略 `from tests import ...` 或
literal subprocess，使相應 cell 轉紅，復原綠。Return：
`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整 SHA、檔案、測試、
解析限制、未完成的 Host/CI admission；不得宣稱清單 08 全部完成。
