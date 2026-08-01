# 09｜Python 可重播事件時間線與 Audit

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（§功能集群／事件時間線） |
| 需求變更 | `CHG-20260801-001` |
| 狀態 | `PLANNED` |
| 環境 | `LOCAL` |
| 責任邊界 | 通用事件、狀態、replay、不可變 audit 與 deterministic comparison |
| 禁止修改 | Dispatch 的派單規則、raw event、報表、租戶資料與自動化 |

## 可觀察結果

同一事件序列與設定重播兩次，得到相同狀態與 audit 摘要；不明事件保留為 unresolved，而非補造狀態。

## 實作範圍與來源追溯

- 預定實際程式碼：`library/功能集群/python/event_timeline_audit/`。
- 參考：來源專案D 的 timeline runtime、golden replay 與 Shadow Judge 分層；排除所有派單領域字彙。

## TDD 設計

1. 正常：合法事件可進行狀態遷移並留下 audit。
2. 違規：未知事件與不合法順序回傳 unresolved／conflict。
3. 回歸：固定 input 必得 deterministic output hash。
