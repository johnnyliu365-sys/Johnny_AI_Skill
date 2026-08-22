# Architecture Decision Records

僅在出現重大且難以回復的決策時，才在此建立 ADR。

| ADR | 狀態 | 用途 |
| --- | --- | --- |
| [ADR-20260804-001-private-router-saas.md](ADR-20260804-001-private-router-saas.md) | `SUPERSEDED` for future direction | 保留歷史 private Router SaaS POC 的決策與邊界。 |
| [ADR-20260805-002-autonomous-collaboration-control-plane.md](ADR-20260805-002-autonomous-collaboration-control-plane.md) | `ACCEPTED — Grill converged` | 定義非商用多 AI 協作／稽核控制平面的高階架構。 |
| [ADR-20260811-004-safe-codex-compensation-boundary.md](ADR-20260811-004-safe-codex-compensation-boundary.md) | `ACCEPTED` | 將任意 callable 邊界收斂為零副作用 capability、純 reducer 與薄 composition。 |
| [ADR-20260812-005-codex-registration-transaction-boundary.md](ADR-20260812-005-codex-registration-transaction-boundary.md) | `ACCEPTED` | 將 process-local 一次性交易 authority、forward effects、settlement 與 disposable lifecycle acceptance 分開驗收。 |
| [ADR-20260812-006-version-one-staging-and-package-convergence.md](ADR-20260812-006-version-one-staging-and-package-convergence.md) | `ACCEPTED` | 以遠端 staging 溫備、串行小工單與不可變 evidence record 收斂第一版打包／系統整合。 |
| [ADR-20260813-008-guided-project-bootstrap-and-adaptive-delivery.md](ADR-20260813-008-guided-project-bootstrap-and-adaptive-delivery.md) | `PARTIALLY_SUPERSEDED` | Adaptive delivery 保留；target-local Johnny ignore/worktree 決策由 `ADR-20260815-013` 取代。 |
| [ADR-20260814-011-tiered-model-router-lifecycle.md](ADR-20260814-011-tiered-model-router-lifecycle.md) | `ACCEPTED / ROUTER_PHASE_AUTHORIZED` | 定義 architecture owner、supervisor、implementer 的 readiness／sleep／wake，以及低階 ticket admission 與選配 design source。 |
| [ADR-20260815-012-receipt-bound-event-driven-completion-supervision.md](ADR-20260815-012-receipt-bound-event-driven-completion-supervision.md) | `ACCEPTED` | 以 Git ref 事件、receipt-bound handoff、一次性 role wake 與模型分級期限監督實作；永不隱含 heartbeat，且插件可無條件拔除。（同步派工的部分由 `ADR-20260823-014` 收窄） |
| [ADR-20260815-013-isolated-environment-capability-bootstrap.md](ADR-20260815-013-isolated-environment-capability-bootstrap.md) | `ACCEPTED` | 優先重用相容使用者工具，將控制 Python、side-by-side 環境、資源限制與可移除狀態隔離在 Johnny per-user root。 |
| [ADR-20260823-014-cross-lifetime-handoff-bridge.md](ADR-20260823-014-cross-lifetime-handoff-bridge.md) | `ACCEPTED` | 把 runner／gateway 定義為跨生命週期的交接橋接器，收窄 `ADR-20260815-012`：同步派工不需要橋；並定義三類審查與能力三態。Decision 3 已經 owner 明示接受。 |
