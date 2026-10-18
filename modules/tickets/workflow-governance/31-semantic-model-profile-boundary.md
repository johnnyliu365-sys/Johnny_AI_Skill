# 31｜通用 Skill 的模型角色來源不得凍結名稱

| 欄位 | 內容 |
| --- | --- |
| State | `SLICE_LOCAL_INTEGRATED` at `68a10057`；Owner 2026-10-18 改進清單項目 10 的最小獨立切片 |
| Authority | 現有 `PRD-20260822-030`／`CHG-20260822-030`、`doc/runbooks/dispatch-model-profile.md` 作當前資料來源，以及 Owner 本次「通用 skill 不寫死模型名、按難度分派並記錄升級理由」 |
| Baseline | 本票所在控制面 commit；派工時 pin |
| Owner / reviewer | 低成本實作席位與另一獨立審閱席位 |
| Profile | `COMPACT`；只改語義規則與其 pin／測試，不啟動模型或付費 API |

## 邊界宣告

```text
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

## 審閱／整合結果

`ffd9d7c8400d948cbc11b821699c06f09537fb08` 經原 reviewer 兩次具名
限縮拒收後通過：普通 `TICKET_OPENING` 的低／高 profile 對照與同步路徑
`NOT_REQUIRED` readback 均已校正。36 tests／74 subtests 綠，反向突變紅→綠。
四個落地 Git blob 與候選完全相同；控制面閘門本地整合為 `68a10057`。
完整紀錄見 `doc/reviews/workflow-governance/31-semantic-model-profile-boundary-code-review.md`。

## 31B — 固定交付回報，沿原清單10補缺

前段31模型映射切片已完成，不重做。此段DOCUMENT_REVIEW_PENDING，Root Grant
`grant-wg31b-report-local-20261018`追溯Owner `batch-checklist-local-20261018`；
同一需求／票／既有證據不重置。基準`cfd64358`，派工時讀回最終文件commit／leaf；
31B新增命令上限180s、單次60s，歷史31耗用另保留，不挪用或重置。initial+一次correction。
COMPACT，無production行為；只補既有模板及其契約驗證，不宣稱Host enforcement。
作者`/root/completion_report_impl`（當下gpt-6-luna/high），另一席
`/root/completion_report_review`（gpt-6-sol/high）；same-lifetime direct lane。
worktree `.worktrees/skill-improvement-31b-report`、branch同名`codex/skill-improvement-31b-report`；
review `.worktrees/skill-improvement-31b-review`。Root先核對containment/非reparse/clean。

```johnny-boundary
modify = modules/tickets/TEMPLATE.md
modify = template/modules/tickets/TEMPLATE.md
modify = tests/test_ticket_template_contract.py
forbid = library/
forbid = skills/
forbid = doc/
forbid = modules/spec/
```

create/delete/dependency=none。沿用既有 `_assert_template_contract`、`_SlotMutation`、
active-section/comment/fence排除及通用虛構filled例子。不得另建parser、report engine、
新測試檔或重新跑已完成31選模測試。只有兩模板及其直接test consumer受影響。

在既有「完成回寫」保留檔案及commit，新增七個唯一active bullet：功能、新測試、
產品拆分、埋點、證據、未驗證項、下一步。每項要求精確位置／證據；未做者明填
N/A與理由，未驗證者NOT_VERIFIED與原因，禁止填PASS。產品拆分須引用真正產品責任
source→target及候選行為驗證；僅拆腳本／測試工具不能報產品拆分。這是交付格式，
不是另建WPR或將模型文字當證明。paid API／credential隔離仍為獨立未驗證缺口。

驗收31B-R1：兩模板同一完整欄位契約通過，原有46tests不降低。
31B-R2：七欄每欄刪除、藏comment/fence、移出completion節至少一種負例，必須紅；
沿既有參數化mutation資料，不複製七套測試函式。缺欄不能被其他節同名詞補足。
31B-R3：虛構純腳本修改案例產品拆分=N/A，未實測功能=NOT_VERIFIED，下一步指出
缺口；真正產品拆分例子綁真seam與測試位置。此固定情境只證明格式/可表達性，
不宣稱以字串檢查能判斷語意真偽。
31B-R4：作者移除一欄驗證→具名負例紅→還原；獨審改另一模板活躍欄→紅→還原。
Run `python -m pytest tests/test_ticket_template_contract.py -q`、`git diff --check`。
產品碼0、模板各≤14行、測試≤60行為結構review訊號，不壓縮或再造框架。
author只commit三路徑、return candidate/checks/findings/deviations/累計時間；Root維護
票面／review並經既有mutation gate本地整合。assets owner具名席位，TTL至review+
evidence seal及整合後受限移除；未整合/Recovery保留。network/paidcall/helper=0。
本地模板結果不等於runtime Host admission，清單10不得因此整項勾選。
