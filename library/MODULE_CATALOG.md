# 可重用模組選擇卡

這是 AI 的最小載入入口。先以需求關鍵字選擇卡片，再讀取該卡的 README、公開 `__init__.py` 與必要契約；不得先讀完整 `library/`、所有測試或未命中的同族模組。

| ID | 命中需求 | 公開 import | 直接相依 | 最小閱讀路徑 |
| --- | --- | --- | --- | --- |
| `text-contracts` | 文字驗證、正規化、受控輸入 | `library.NLP.python.text_contracts` | — | README → `__init__.py` → `contracts.py` |
| `rule-field-parser` | 固定標記、欄位、frame 解析 | `library.NLP.python.rule_parser` | `text-contracts` | README → `__init__.py` → contracts → parser |
| `analysis-provider-boundary` | AI／多模態 provider、payload 驗證 | `library.NLP.python.provider_ports` | — | README → `__init__.py` → contracts → validator |
| `payment-contracts` | 付款意圖、金額、幣別、idempotency | `library.金流串接.python.payment_contracts` | — | README → `__init__.py` → `contracts.py` |
| `subscription-ledger` | 訂閱、權益、退款、不可變帳本 | `library.金流串接.python.subscription_ledger` | `payment-contracts` | README → `__init__.py` → `ledger.py` |
| `payment-provider-boundary` | 付款授權、確認、退款、fake provider | `library.金流串接.python.provider_ports` | `payment-contracts` | README → `__init__.py` → contracts → fake provider |
| `payment-reconciliation` | provider event 對帳、journal、人工審查 | 三個付款模組組合 | payment contracts／ledger／provider | README → `__init__.py` → reconciliation |
| `reliability-core` | outbox、worker、idempotency、emergency stop | `library.功能集群.python.reliability_core` | — | README → `__init__.py` → core |
| `identity-resolution` | stable identity、顯示名稱、unknown identity | `library.功能集群.python.identity_resolution` | — | README → `__init__.py` → resolver |
| `line-transport-boundary` | 出站訊息、LINE 類 transport、fake sender | `library.功能集群.python.line_transport` | `identity-resolution` | README → `__init__.py` → contracts → fake transport |
| `event-timeline-audit` | 事件重播、audit、deterministic hash | `library.功能集群.python.event_timeline_audit` | — | README → `__init__.py` → timeline |
| `engagement-rules` | 資格、進度、獎勵允許、policy | `library.功能集群.python.engagement_rules` | — | README → `__init__.py` → rules |
| `workflow-router-poc` | 專案關卡、Context router、核准等待 | `library.workflow_router` | Pydantic／LangGraph／Temporal／MCP | README → contracts → profile → selected adapter |

## 不可省略的邊界

- 所有卡片都是本地、強型別核心；沒有真實 Provider、資料庫、網路、Secret 或商業效果。
- 卡片命中只代表「值得讀取」，不是採用、寫入或部署授權；正式採用仍須經目標專案的 Wayfinder、Grill、SPEC 與 ticket。
- Kotlin 與 C# 候選模組尚未交付，不能列為可選卡片；未命中需求必須回到 Wayfinder／Grill，不得由 AI 拼湊相近實作。

## 常見組合

- 結構化文字：`text-contracts → rule-field-parser`
- 付款本地流程：`payment-contracts → subscription-ledger`；需 provider event 時才加入 `payment-provider-boundary → payment-reconciliation`
- 可控出站工作：`identity-resolution → reliability-core → line-transport-boundary`
- 純規則與可重播驗證：`event-timeline-audit`、`engagement-rules`
