# Router Framework POC Context

## Wayfinder 決策

```json
{
  "project_id": "router-framework-poc",
  "decision": "GO",
  "decision_reasons": [
    "範圍限於本機、可測的流程核心，沒有外部服務或正式資料依賴。",
    "可用 Pydantic 契約、LangGraph transition 與 fake adapter 驗證核心假設。"
  ],
  "product": {
    "target_users": ["接管專案的 AI Agent", "專案負責人"],
    "core_problem": "共享 Context 膨脹且 Agent 可在缺少正式來源時錯誤跨關卡。",
    "value_proposition": "以可重建的最小 Context 視圖、封閉 transition 與引用映射維持可追溯流程。",
    "mvp_scope": ["以一個實際專案 Profile 執行受控流程", "耐久化 human approval 與 MCP 來源讀取"],
    "out_of_scope": ["真實 LLM", "付費 Provider", "部署", "任何被接管專案的商業決策"]
  },
  "business": {
    "model": "內部可重用工程流程框架",
    "validation_method": "完成 INTAKE 到 WAYFINDER、ARCHITECTURE 與 Grill 引用映射的本機 POC。",
    "success_metrics": ["所有非法 transition fail closed", "引用原文不進共享儲存", "重試不建立重複引用"],
    "stop_conditions": ["無法在不保存共享原文的前提下維持追溯", "核心轉移無法以強型別表達"]
  },
  "constraints": {
    "tech_limits": ["Python 3.11", "不啟動外部服務", "不使用 Secret 或付費 Provider"],
    "cost_ceiling": "本機開發套件與測試，零付費 API 呼叫"
  },
  "risks": [
    {
      "risk": "外部框架的內部 API 變動造成耦合",
      "mitigation": "僅使用 LangGraph、Temporal、MCP 與 Agents SDK 的公開介面，並將其置於 adapter 邊界。"
    }
  ],
  "assumptions": ["使用者於 2026-08-02 的『開始實作』同時核准本 POC SPEC 與單一初始 ticket。"]
}
```

## 高階架構與 Grill 收斂

```text
Pydantic contracts → LangGraph transition graph → Capability adapter
        ↓                         ↓                       ↓
  Profile validation        ContextView descriptor   OpenAI Agent definition
        ↓                         ↓                       ↓
      Temporal durable wait ← RouterDecision → MCP resource source port
                                      ↓
                         Citation ledger projection
```

- `ContextView` 的持久內容只含 descriptor；原文 `ContextPacket` 只交給引用 Agent 的 worktree。
- `side_context_id` 由 Router event、來源版本、span、目標產物、引用者指紋與引用序號穩定推導；重試重用同一 ID，下一次真實引用或不同引用者使用新的 ID。
- 外部框架呼叫均可替換為 fake adapter；任一未解析 source、capability 或核准皆輸出 `SUSPEND`。
