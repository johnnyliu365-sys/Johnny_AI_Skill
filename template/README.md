# 新專案工作環境 Bootstrap 模板庫

本目錄是新專案建立時的受版控模板庫；通用發行版必須附帶同一份 `template/` 目錄。

## 固定結構

```text
<project-root>/
├─ Workflow.md
├─ AGENTS.md
├─ CONTEXT.md
├─ PRD.md
├─ ProjectSchedule.md
├─ modules/
│  ├─ spec/
│  ├─ tickets/
│  └─ element/{typescript,python,java}/
└─ doc/
   ├─ context/
   ├─ reviews/
   ├─ adr/
   ├─ RequirementChangeLog.md
   ├─ WorkProgressReport.md
   └─ security-agent-boundary.md
```

## 建置順序

1. 從通用發行版複製 `Workflow.md` 與 `AGENTS.md` 至新專案根目錄。
2. 建立上方固定目錄；不得建立 `doc/specs/` 或 `doc/tickets/`。
3. 複製並填寫 `CONTEXT.TEMPLATE.md`、`doc/context/TEMPLATE.md`、`doc/RequirementChangeLog.TEMPLATE.md`、`modules/spec/TEMPLATE.md`、
   `modules/tickets/TEMPLATE.md`、`doc/reviews/TEMPLATE.md`、`doc/adr/TEMPLATE.md` 與相符語言的 element 模板。
4. 先完成 `CONTEXT.md`、`PRD.md`、`ProjectSchedule.md`、需求變更與安全邊界的最小內容，再開始第一個 Grill。

## Plugin policy baseline

新專案沿用 `Workflow.md` 的唯一 policy：plugin application 先詢問 `可用 coding Agent 數量為 1 或 2？`；提交 ticket 與文件交接後，控制面只輸出固定的 `工單 ready`／`文件交接` 欄位，再提出一次具名 dispatch-confirmation 問題。未確認前不得授予 branch、worktree、source、Context 或 implementation capability。`WAIT_FOR_HUMAN` 只等待這個精確決策，未授權或無效狀況一律 `HALT`。

模板不承諾 SaaS、價格、entitlement 或部署；任何既有 commercial POC 文字只能標示為歷史記錄，不能當作現行產品方向。
