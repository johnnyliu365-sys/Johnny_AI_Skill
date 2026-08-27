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
| [ADR-20260823-015-dedicated-plugin-publication-repository.md](ADR-20260823-015-dedicated-plugin-publication-repository.md) | `ACCEPTED` | 將 Claude marketplace descriptor 與實際 plugin source 分離；後者改由只含 parentless payload commits 的獨立 publication repository 提供，並以 CAS 發布與真實 CLI object-graph closure 驗證守住。 |
| [ADR-20260823-016-codex-cli-cross-lifetime-wake-bridge.md](ADR-20260823-016-codex-cli-cross-lifetime-wake-bridge.md) | `ACCEPTED` | Codex 跨生命週期以 one-shot CLI actor 交接 artifact，不復原 Desktop parent；同步 `wait_agent` 不需 bridge，且 capability 保留 `NOT_REQUIRED`／`AVAILABLE`／`UNAVAILABLE` 三態。 |
| [ADR-20260823-017-level-one-payload-topology.md](ADR-20260823-017-level-one-payload-topology.md) | `ACCEPTED` | 將 Claude Level 1 payload 收斂為可達 reusable surface，排除 host-local publication/cache/installer tooling。 |
| [ADR-20260823-018-version-specific-publication-tag-payloads.md](ADR-20260823-018-version-specific-publication-tag-payloads.md) | `ACCEPTED` | 保留 immutable multi-release tags：current root 對候選 payload 驗證，歷史 tag 對其自身的 in-tree declaration、版本與樹形狀驗證，且不虛稱 current blob 比對。 |
| [ADR-20260824-019-provider-usage-telemetry-evidence.md](ADR-20260824-019-provider-usage-telemetry-evidence.md) | `ACCEPTED` | 區分載入估算、一次 host usage 觀測與可比較的實際 token reduction，並將 provider usage 保持 metadata-only。 |
| [ADR-20260824-020-declared-project-authority-line-and-provider-enforcement.md](ADR-20260824-020-declared-project-authority-line-and-provider-enforcement.md) | `ACCEPTED` | 以宣告的遠端權威線與直接 readback 定義整合完成；高協作 PR 可見但不取代 gate，provider enforcement 必須以實測讀回證明。 |
| [ADR-20260825-021-core-cluster-closure-and-deferred-operational-verification.md](ADR-20260825-021-core-cluster-closure-and-deferred-operational-verification.md) | `ACCEPTED` | 將純核心 closure 與日後 per-project qualification／shipped governance verification 分開；核心完成不虛稱 provider 或發布完成。 |
| [ADR-20260827-022-lock-bound-telemetry-storage.md](ADR-20260827-022-lock-bound-telemetry-storage.md) | `ACCEPTED` | 將 Context Governor 的 durable storage 收斂為 exact-identity lock、持鎖重驗與無副作用 contention。 |
| [ADR-20260827-023-exclusive-file-lock-catalog-admission.md](ADR-20260827-023-exclusive-file-lock-catalog-admission.md) | `ACCEPTED` | 將既有 blocking exclusive file lock 誠實 catalog；不把未知錯誤偽裝為 contention。 |
| [ADR-20260827-024-classified-nonblocking-file-lock.md](ADR-20260827-024-classified-nonblocking-file-lock.md) | `ACCEPTED` | 在不改既有 blocking consumers 下，新增有證據界定的 finite nonblocking acquisition。 |
| [ADR-20260827-025-preprovisioned-telemetry-storage-transactions.md](ADR-20260827-025-preprovisioned-telemetry-storage-transactions.md) | `ACCEPTED` | 受控 telemetry storage 僅接受預先 provision 的 owned ledger，並以可恢復 all-or-nothing transaction 協調 stream 與 lifecycle。 |
| [ADR-20260827-026-per-stream-ownership-ledger-readiness.md](ADR-20260827-026-per-stream-ownership-ledger-readiness.md) | `ACCEPTED` | 將私有 ledger 分割為 exact-stream entry，令 per-stream lock 真正序列化 CAS；另提供 recovery-only immutable-identity lookup。 |
| [ADR-20260827-027-lock-bound-telemetry-transaction-protocol.md](ADR-20260827-027-lock-bound-telemetry-transaction-protocol.md) | `ACCEPTED` | 封閉私有 journal/recovery、deterministic revision 與五項 storage operation adapter 協定，不改公開 contracts。 |
| [ADR-20260827-028-private-telemetry-storage-composition.md](ADR-20260827-028-private-telemetry-storage-composition.md) | `ACCEPTED` | 將已交付的 private ledger、lock 與 transaction adapter 綁入唯一 no-effect composition factory，不擴張公開 surface。 |
| [ADR-20260827-029-host-bootstrap-router-provisioning-and-composition.md](ADR-20260827-029-host-bootstrap-router-provisioning-and-composition.md) | `ACCEPTED` | 將 root readiness、runtime owned-entry delegation 與 storage composition 收斂為三個不可互換的私有責任。 |
