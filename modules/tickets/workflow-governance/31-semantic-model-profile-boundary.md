# 31｜通用 Skill 的模型角色來源不得凍結名稱

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN`；Owner 2026-10-18 改進清單項目 10 的最小獨立切片 |
| Authority | 現有 `PRD-20260822-030`／`CHG-20260822-030`、`doc/runbooks/dispatch-model-profile.md` 作當前資料來源，以及 Owner 本次「通用 skill 不寫死模型名、按難度分派並記錄升級理由」 |
| Baseline | 本票所在控制面 commit；派工時 pin |
| Owner / reviewer | 低成本實作席位與另一獨立審閱席位 |
| Profile | `COMPACT`；只改語義規則與其 pin／測試，不啟動模型或付費 API |

## 邊界宣告

```johnny-boundary
modify = skills/johnny-project-takeover/references/model-role-routing.md
modify = skills/johnny-project-takeover/references/delivery-profile.md
modify = tests/test_adversarial_review_policy.py
modify = tests/test_executor_routing.py
forbid = doc/runbooks/dispatch-model-profile.md
forbid = modules/spec/
forbid = doc/requirements/
```

## Objective／Expected

通用 Skill 保留角色權限、低成本優先與「審閱能力不得低於實作」不變量，
但不把某一次 Host 的模型名稱或能力排序當永久政策。實際 provider/model/effort、
可用性及可比較的能力 rank 只從本次生效、經驗證的 ProjectWorkflowProfile／
Host capability 資料取得。`doc/runbooks/dispatch-model-profile.md` 是可更新資料，
本票不擅改其映射，也不推定不同版本名稱的能力相同。

1. 移除通用 `model-role-routing.md` 與 `delivery-profile.md` 內目前寫死的
   Terra／Luna 預設對應；換成語義 `SUPERVISOR_REVIEWER`、
   `IMPLEMENTATION_OWNER`、`ARCHITECTURE_OWNER` 和當前 Profile 讀回規則。
   普通盤點不預設最高能力階；難度超出標準 implementer 且不能再拆時，
   同票能力升級須具名 HardTicketAssessment，reviewer rank 隨之滿足
   `reviewer >= implementer`，不跨票擴散。
2. 已查明這兩份 reference 並未由 `profile.py` pin；不得憑猜測新增假 pin。
   沿用 `library/local_orchestration/executor_routing.py` 的既有
   `VerifiedCapabilityRank`、`HardTicketAssessment`、reviewer rank 檢查，
   及 `ProjectWorkflowProfile` 的角色資料，不建立第二套選模引擎。
3. 在既有政策及 executor 測試內新增或引用精確正反情境：更換 provider/model
   不改語義角色及 authority；缺 verified capability 或 reviewer rank 較低
   時 fail closed；普通盤點按現有 route 不被硬推最高階。既有 cell 已涵蓋者
   只記證據，不重複造測試檔。

Acceptance：通用 Skill 不含固定模型名；Profile 資料仍能在驗證後決定當次映射，
升級理由可追溯且只單票生效，模型身分不產生授權。反向突變將 reviewer rank
降到 implementer 以下或拿掉能力證據，具名 cell 必須轉紅，還原綠。
Run：`python -m pytest tests/test_adversarial_review_policy.py tests/test_executor_routing.py -q`、
`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整 candidate SHA、變更檔、
測試、突變證據、仍缺的本機付費服務隔離／固定回報欄位。這只完成清單 10
的模型選擇切片，不宣稱整項完成；不得 push／release／部署。
