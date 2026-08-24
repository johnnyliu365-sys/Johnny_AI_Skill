# ADR-20260824-019｜Provider usage telemetry evidence

- 日期：`2026-08-24 (Asia/Taipei)`
- 狀態：`ACCEPTED`
- 決策者：project owner
- 關聯需求：[`REQ-20260803-006`](../requirements/active/2026/reusable-platform/REQ-20260803-006.md)
- 關聯規格：[`modules/spec/context-load-telemetry.md`](../../modules/spec/context-load-telemetry.md) Revision 03

## 背景與問題

目前的 Router telemetry POC 可以驗證 caller 已提供的 usage pair，也可以估算路由前後
應載入的 reference 大小；它不能自行取得 Codex 或 Claude Code 的實際 provider usage。
`JsonlContextUsageStore` 又接受 raw path，依 Revision 02 的 project-isolation 規則不能
用於受控公司專案。因此既不能以估算宣稱省下真實 token，也不能把未證明的 host 輸出或
既有 conversation 畫面當成帳務證據。

## 決策

1. telemetry 分成三個不可混用的結論：

   | 結論 | 所需證據 | 允許的敘述 |
   | --- | --- | --- |
   | `LOAD_ESTIMATE` | Router metadata 與檔案大小 | 「估算載入量」；不是 provider 用量。 |
   | `OBSERVED_USAGE` | 已驗證的單次 terminal host usage event | 該次執行的實際 input/output token；不得宣稱節省。 |
   | `MATCHED_REDUCTION` | 兩個隔離、可比較且品質合格的 provider usage records | 實際 provider input-token 差額與百分比。 |

2. provider-neutral `ProviderUsageEvidencePort` 只接受一個已結束 host run 的 ephemeral
   terminal event，於邊界驗證後產出 metadata-only `ProviderUsageObservation`。它的輸入、
   output、error、storage 與 report 不得保留 prompt、response、source text、URI、cookie、
   authorization header、credential 或 raw host event。
3. `ProviderUsageObservation` 必須含 opaque `host_run_ref` 的不可逆 fingerprint、provider、
   exact model、host version/configuration fingerprint、project snapshot fingerprint、input token
   count，以及存在時的 output/cached-input token count。沒有 provider input count，結果是
   `HOST_USAGE_UNAVAILABLE`，不是零、估算或可比較的 usage。
4. 每個 host adapter 都先以 fake terminal event 完成純解析與 strict typed admission。真實
   Codex／Claude CLI run 是 paid Provider effect，必須由另一張 ticket 逐次取得 owner
   effect authority、記錄 exact host/model/workspace/correlation，並 read back terminal evidence。
   目前 CLI 的 JSON/stream-json flag 只證明候選 transport，尚未證明其 usage schema。
5. `MATCHED_REDUCTION` 只允許兩個 fresh isolated session，且 pair 的 provider、exact model、
   effort/configuration fingerprint、cache mode、project snapshot、frozen task contract、comparison
   group 與 attempt 相同。兩次 session 不得 resume、share conversation、read the other run's
   output or handoff；執行順序須預先隨機化。任一 quality failure、missing field 或 mismatch
   使 pair fail closed。
6. 初期正常工作流只可產生 `OBSERVED_USAGE` 趨勢；它不能被彙整或外推成「已省 token」。
   `MATCHED_REDUCTION` 只能由專門、逐次授權的隔離實驗輸出，且只對該 evidence population
   有效。
7. 本 ADR 不定義費用、幣別或價格。input-token reduction 不是價格節省；cached/uncached
   rate、output rate 與 seat/subscription accounting 需要另一份經 owner 核准的需求變更。

## Revision 02 storage completion

`TelemetryStorageRef` 是 opaque typed identity；ownership ledger 是唯一可將它解析為
Johnny-root 內實體位置的 composition-root dependency。任何 request、result、CLI argument、
report、journal 或 error 都不得帶 raw path。驗證依下列固定 precedence 失敗：

1. malformed identity、extra field、missing expected revision 或不允許的 operation/payload
   combination → `STORAGE_REF_INVALID`；
2. ref 不存在、project/ledger/stream 不完全相符 → `STORAGE_OWNERSHIP_MISMATCH`；
3. lifecycle 不是該 operation 的 `ACTIVE` 前置狀態 → `STORAGE_CLOSED`；
4. resolved owned location 越界、reparse/symlink、非 ledger descendant 或 target-project path
   → `STORAGE_BOUNDARY_VIOLATION`；
5. schema-invalid telemetry record → `RECORD_INVALID`。

合法 operation matrix 是：

| Operation | Required lifecycle | `record` | `lifecycle` / `record_count` on success | `validation_report_ref` / `failure_ref` on success |
| --- | --- | --- | --- | --- |
| `APPEND` | `ACTIVE` | present | `ACTIVE`; count after append is required | both absent |
| `READ` | `ACTIVE` | absent | `ACTIVE`; snapshot count is required | both absent |
| `VALIDATE` | `ACTIVE` | absent | `ACTIVE`; validated count is required | report ref required; failure ref absent |
| `DETACH` | `ACTIVE` | absent | `DETACHED`; removed-record count is required | both absent |
| `UNINSTALL` | `ACTIVE` | absent | `REMOVED`; removed-record count is required | both absent |

`TelemetryStoragePort` is the only production caller contract. It has the one strict signature
`execute(request: TelemetryStorageRequest) -> TelemetryStorageResponse`; callers receive that port
from the composition root and may not construct an adapter. `TelemetryStorageRequest` is a
discriminated union of `AppendTelemetryStorageRequest` and
`NoRecordTelemetryStorageRequest`. Every member has exactly `storage_ref`,
`expected_project_id`, `expected_storage_revision`, and `operation`; the append member has exactly
one additional `record: ContextUsageRecord`, while the no-record member has no additional payload
field and admits only `READ`, `VALIDATE`, `DETACH`, or `UNINSTALL`. There is no path, lookup key,
root override, filter, pagination, or dynamic extra field in either command.

`TelemetryStorageResponse` is also a discriminated union. The five completed response members
have the common envelope `storage_ref`, `storage_revision`, `operation`,
`decision=COMPLETED`, `lifecycle`, and `record_count`. `CompletedReadResponse` has exactly one
additional `read_payload: TelemetryStorageReadPayload`; its `records` is the complete immutable
tuple of validated `ContextUsageRecord` values in ledger append order, with
`record_count == len(records)`. A `ContextUsageRecord` is already the metadata-only schema in this
SPEC: it structurally excludes source text, prompt, response, URI, credential, raw event and path.
Completed `VALIDATE` has exactly `validation_report_ref`; completed `APPEND`, `DETACH`, and
`UNINSTALL` have neither read payload nor report ref. `TelemetryStorageFailure` has exactly the
common identity/revision/operation envelope, a non-`COMPLETED` finite decision and one opaque
`failure_ref`; it has no lifecycle, count, read payload or validation report. The response union
has no optional catch-all payload field.

The future source boundary is fixed as follows. A new
`library/local_orchestration/telemetry_storage/contracts.py` owns the strict commands, responses,
port protocol and no-path safe types. A new
`library/local_orchestration/telemetry_storage/johnny_owned_adapter.py` implements that protocol
and is the only source allowed to import the legacy `JsonlContextUsageStore` codec. A composition
root in `library/local_orchestration/telemetry_storage/composition.py` resolves the ownership
ledger and returns a `TelemetryStoragePort`; product callers import the contracts, never the
adapter or legacy codec. `library/workflow_router/telemetry.py` retains metadata value types only
and must not import storage I/O. `library/workflow_router/telemetry_cli.py` remains a legacy
development-only path-taking entry point and is not reachable from the composition root or any
controlled-target command. This direction is one-way: `contracts <- adapter <- composition root`;
callers depend only on `contracts`, and no lower layer imports a caller or target-project module.

`TelemetryStorageResult.storage_revision` is required in every result. On a successful mutating
operation it is the new ledger revision; on a successful read/validate it equals the expected
revision; on every failure it only echoes the request's expected revision and never reveals a
current revision. `lifecycle` is required only for `COMPLETED`; `record_count` is required only
for `COMPLETED`; `validation_report_ref` is required only for `COMPLETED / VALIDATE`; all three
are absent for a failure. `failure_ref` is absent on `COMPLETED` and required for every failed
decision as an opaque stable fingerprint of the finite decision, never raw diagnostics.

`DETACHED` and `REMOVED` reject every operation as `STORAGE_CLOSED`; no action recreates them.
The storage adapter is the only implementation allowed to use the legacy JSONL codec internally.
No caller-selectable path or target repository write is admitted.

## 實作順序與回復

1. 先實作 opaque storage contracts／lifecycle 和 pure provider-usage response admission，均以
   fake port、無 host invocation 的測試完成。
2. 再實作 Johnny-owned storage adapter 與 sanitized aggregate report；未獲外部 authority
   前不啟動 Codex、Claude Code、runner 或任何 provider call。
3. 每個 host 的 one-shot usage probe 以獨立 `HIGH_ASSURANCE` ticket 取得 effect authority。
   probe 失敗或 schema 不符時，adapter capability 維持 `UNAVAILABLE`。
4. 只有已證明的 host 才能進入 pair experiment ticket。撤除 adapter 或 detach telemetry
   stream 時，只刪除 ledger-owned state，不改動公司專案、既有 host configuration 或歷史
   review evidence。

## 替代方案

- **以 bytes／四分之一 UTF-8 長度估算冒充實際 token**：拒絕；估算與 provider usage 不同。
- **從互動式 UI 或 usage limit 截圖抓數字**：拒絕；沒有一次 run 的 typed、可重讀證據。
- **連續兩次在同一 conversation 做相同工作**：拒絕；第二次受前一次答案與路徑污染。
- **以 runner 或 polling 收集 usage**：拒絕；runner 只送達跨生命週期 artifact，polling 既不
  產生 usage evidence 又浪費 token。
