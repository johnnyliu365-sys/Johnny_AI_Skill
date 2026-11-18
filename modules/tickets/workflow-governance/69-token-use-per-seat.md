# 69｜Wave-3 acceptance (5): every receipt records its token use per seat, compared with the model-tier expectation

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-7 receipt cells; REQ-20261103-043 implementation readiness criterion 5） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/69-token-use-per-seat-out/` / owner implementation seat / worktree `.worktrees/69-token-use-per-seat` / branch `cp/wave3-69-token-use` / baseline the wave-3 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `REVIEW_APPROVED`（candidate `7cc0e08f`; revision01 correction review `CONVERGENCE_REVIEW_REQUIRED`, disposition APPROVED under rule B; S69-07, S69-08 carried） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/69-token-use-per-seat` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/69-token-use-per-seat-review` |
| 責任邊界 | the receipt's `USAGE` cell in the evidence gate and the receipt template, a usage report script with its expectation file, their tests, and the dispatch profile runbook's expectation section |
| 禁止修改 | every other gate script, the router library, the governance documents |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/evidence_gate.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = tests/test_gate_evidence.py
modify = template/doc/handoffs/governance/RECEIPT.TEMPLATE.md
modify = template/README.md
modify = tests/test_state_file_templates.py
modify = doc/runbooks/dispatch-model-profile.md
create = skills/johnny-project-takeover/scripts/usage_report.py
create = tests/test_usage_report.py
create = template/doc/handoffs/governance/usage-expectation.TEMPLATE.json
forbid = library/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
forbid = modules/spec/
```

## 使用者拍板與可觀察結果

The owner set wave-3 acceptance criterion 5 on 2026-11-03 (REQ-20261103-043): every ticket receipt records its token use per seat, and the record is compared with the model-tier expectation. After this ticket:

### The `USAGE` cell (receipt grammar, `evidence_gate.py`)

A receipt holds one `USAGE` cell per seat that worked on the ticket's candidate: the implementation seat and every review seat. Like `STATEMENT`, it is informational, so it has no capture, exit or fence. Its fields come one per line, in this order:

```text
## USAGE <seat>
cell: USAGE
seat: seat:<profile>/<run-id>
profile: <semantic profile reference from doc/runbooks/dispatch-model-profile.md>
model: <the model the host reports>
input_tokens: <integer >= 0>
cache_write_tokens: <integer >= 0>
cache_read_tokens: <integer >= 0>
output_tokens: <integer >= 0>
source: <where the numbers come from, for example "host transcript usage, summed per message">
```

The evidence gate:

- accepts any number of `USAGE` cells;
- refuses one that misses a field, repeats one, puts the fields in the wrong order, carries a non-integer or negative count, or carries a run field (`candidate`, `capture`, `exit`, `tool_digest` or a fence). Each refusal is a red with a named code, listed in the README;
- refuses two `USAGE` cells for one seat;
- never requires a `USAGE` cell, because a receipt is written before the review seats exist. `usage_report.py` enforces presence.

Every printed subject is escaped to one line.

### `usage_report.py`

```text
python usage_report.py --expectation FILE RECEIPT...
```

It reads each receipt and the expectation file. For every `USAGE` cell it prints one line: the seat, the profile, the output tokens, the processed tokens (input + cache write + cache read), and the verdict against the profile's expectation (`WITHIN`, `OVER_OUTPUT`, `OVER_PROCESSED` or `UNKNOWN_PROFILE`).

Exit codes, as R4-2 sets them:

| Exit | When |
| --- | --- |
| 0 | every seat is within its expectation |
| 1 | a receipt has no `USAGE` cell, a profile is unknown, or a seat is over its expectation; all of them are listed |
| 2 | a receipt or the expectation file cannot be read, or breaks its schema |
| 3 | usage error |

The JSON input rules of the wave-2 gates apply: repeated keys, NaN and Infinity are refused.

### The expectation (`usage-expectation.TEMPLATE.json`; the runbook section)

One object per semantic profile, with `output_tokens_max` and `processed_tokens_max`. The plugin's own values are the proposal below. They are taken from wave 2, as the 90th percentile per role over this session's 129 seat runs, and rounded up. The owner confirmed them on 2026-11-18 ("1A", REQ-20261103-043):

| Profile | `output_tokens_max` | `processed_tokens_max` | Wave-2 basis (median / p90 / max) |
| --- | --- | --- | --- |
| `implementation-standard` | 130000 | 24000000 | output 62791 / 126017 / 297953; processed 8.2M / 23.8M / 121.8M |
| `implementation-elevated` | 130000 | 24000000 | not used in wave 2; same as standard until measured |
| `ticket-review` | 110000 | 23000000 | output 64172 / 105208 / 221702; processed 10.2M / 22.3M / 108.9M |

`doc/runbooks/dispatch-model-profile.md` gains a section that does three things:

- names the expectation file;
- says the control plane appends each seat's `USAGE` cell from the host's report after the seat returns;
- says a seat over its expectation is a fact to explain in the review record, not a block on integration.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/69-token-use-per-seat`.
- reviewer：`ticket-review` seat in `.worktrees/69-token-use-per-seat-review`.
- **Owner override record**：`N/A`；the expectation values were confirmed by the owner on 2026-11-18 ("1A").
- `ImplementationHandoff`：this ticket; REQ-20261103-043 criterion 5; ticket 51 (evidence gate grammar); ticket 57 (receipt template).
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：command-line scripts and templates; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the `USAGE` cell and the expectation schema above.

## TDD 設計

1. 正常行為:
   - A receipt with valid `USAGE` cells passes the evidence gate exactly as before.
   - `usage_report.py` prints one line per seat, and exits 0 when every seat is within its expectation.
2. 規則違反／輸入錯誤, one test each:
   - a missing field, a repeated field, fields out of order, a negative count, a non-integer count;
   - a run field inside a `USAGE` cell;
   - two `USAGE` cells for one seat;
   - a receipt without `USAGE`, which `usage_report.py` reports with exit 1;
   - an unknown profile;
   - over output, and over processed.
3. 外部失敗／fail-closed: an unreadable receipt, an expectation file that is not JSON or has a repeated key, a NaN, or a missing profile key gives exit 2.
4. 回歸保護: every existing evidence-gate test passes unchanged. The receipt template, filled with a real capture and a real `USAGE` cell, passes the gate.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty value, a zero count, no `USAGE` cell |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | the seat id form `seat:<profile>/<run-id>`; integers compared exactly |
| 5 | 錯誤碼是否一致 | 是 | 1 for a missing or over value, 2 for an unreadable input, 3 for usage |
| 6 | 例外是否會拋出 | 是 | malformed JSON and an undecodable receipt are exit 2 with one line |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_gate_evidence.py tests/test_usage_report.py tests/test_state_file_templates.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on both scripts exits 0.
  - The scripts use the stdlib only and no `Any`.
- **反向突變證據**, each restored after it turns a named test red:
  - accept a negative count;
  - accept a run field in `USAGE`;
  - drop the presence check in the report;
  - compare `>=` instead of `>`.
- Receipt:
  - R4-7 cells, passing P9 and E1 (E1 runs last).
  - The receipt itself carries the implementation seat's `USAGE` cell, appended by the control plane after return.
- The full suite runs under the host lock: its failures are a subset of the base names, with zero new red.

## 正式環境移植 SOP

- 不適用：plugin scripts and templates.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
