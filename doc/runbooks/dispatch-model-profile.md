# 派工模型 Profile（現行主機對應）

| Field | Value |
| --- | --- |
| Revision | `2026-11-19 / REVISION_04` |
| Requirement lineage | `PRD-20260822-030` / `CHG-20260822-030` / `doc/requirements/active/2026/adaptive-orchestration/REQ-20260822-030.md`; synchronous-dispatch alignment `REQ-20260824-038` / `ADR-20260824-020` decision 8 |
| Policy source | `modules/spec/executor-routing.md` revision 01 and `modules/tickets/workstation-dispatch/p8-provider-neutral-executor-routing.md` revision 02 |
| Authority | Project owner directives, 2026-08-22 and 2026-08-29 (Asia/Taipei) |
| Scope | Current semantic role-to-profile intent. This file does not grant a role, issue a receipt, prove a credential, or start a host process. |

This document records current **profile data**, not permanent workflow policy. Role authority,
receipt/worktree admission, and the fact that model identity never grants authority remain governed
by `Workflow.md` and the corresponding typed control-plane contracts. A provider/model/effort
tuple must be verified as available by the relevant host capability boundary at dispatch time;
configuration in this document is not availability evidence.

## Semantic profile registry

| Semantic profile reference | Provider/model/effort intent | Permitted routing purpose | Capability status at dispatch |
| --- | --- | --- | --- |
| `decision-support` | Sol / high | Project-initial review; requirement-change review requiring a complex-decision inventory | Verify before selection |
| `ticket-review` | Terra / xhigh | General ticket opening and independent ticket review | Verify before selection |
| `implementation-standard` | Luna / xhigh | Normal single-ticket implementation | Verify before selection |
| `implementation-elevated` | Terra / xhigh | One ticket only after a valid hard-ticket assessment | Verify before selection |
| `elevated-review` | Sol / high | Review binding for that same elevated implementation ticket only | Verify before selection |

An authenticated Claude Code profile may be represented by an analogous registered profile only
after its credential and host capability have been separately proved. It is not selected merely
because its CLI is installed. Likewise, no resolver source may embed any of the provider/model
values above; the values belong in injected profile data.

## Selection and escalation rules

1. `ARCHITECTURE_OWNER` is always the human project owner. Sol is not an implementation owner
   and is not a general ticket-opening/review default.
2. A normal implementation ticket uses `implementation-standard` (Luna/xhigh) and binds
   `ticket-review` (Terra/xhigh). The reviewer's verified capability rank must be greater than
   or equal to the implementation profile's rank.
3. Before any elevation, the reviewer must decide whether the ticket can be decomposed without
   breaking its observable closure. A ticket that can be reasonably decomposed is split rather
   than elevated.
4. An indivisible ticket may use `implementation-elevated` (Terra/xhigh) only when the exact
   ticket and closure carry a `HardTicketAssessment` proving both no further valid decomposition
   and a named capability gap beyond Luna. The same ticket then binds `elevated-review`
   (Sol/high). This is a one-ticket exception, not a global profile switch.
5. If the bounded implementation/review cycle still lacks capability, return
   `MODEL_CAPABILITY_INSUFFICIENT` and route to the human architecture owner. Do not infer a
   further implementer elevation or fallback.

## Dispatch and reporting discipline

- The reviewer is the only Agent-to-Agent orchestrator. A profile name, prompt, CLI login, or
  model setting is never dispatch authority.
- **Same-lifetime synchronous dispatch** is `reviewer -> wait_agent -> review -> gate`. Its
  admission evidence is the exact ticket, any ticket-declared handoff, a reviewer-established
  clean baseline, and the repository-contained worktree/branch binding. Receipt, runner, queue,
  host gateway, task/workspace/profile readback and automatic wake are
  `NOT_REQUIRED`; their absence must not block this path or be reported as a delivery failure.
- the default cross-lifetime route is the ticket's state row plus the dispatch-file digest (R4-1).
- The implementation owner receives identifier-only dispatch, modifies only its declared
  boundary, and returns a typed result. The P8R owner directive that the reviewer alone submits the
  candidate is superseded by Revision 04 R4-4 (`CHG-20261103-043`): the candidate is submitted to
  the merge queue by the implementation owner or a budget holder who is not its reviewer, and
  integration is run by the versioned integration script.
- A provider credential or host execution failure is a named capability result. It is neither
  permission to substitute another profile nor evidence that a selected profile ran.

## Token use per seat and the expectation

Wave-3 acceptance criterion 5 (`REQ-20261103-043`): every ticket receipt records its token use per
seat and compares it with the model-tier expectation.

- The expectation file is `usage-expectation.json`, copied from
  `template/doc/handoffs/governance/usage-expectation.TEMPLATE.json`. It holds one object per
  semantic profile with `model`, `effort`, `output_tokens_max` and `processed_tokens_max`
  (processed is input plus cache write plus cache read tokens). `model` and `effort` are each one
  item matching `[A-Za-z0-9][A-Za-z0-9._-]*`. The shipped template holds the placeholders
  `<host-model>` and `<host-effort>` and names no provider or model; a project replaces them with
  its host's values before the report reads the file.
- Tokens stay the unit of account and no price table is used. A token count is comparable only
  between seats that ran the same model at the same effort, so the model and the effort are
  recorded beside the tokens. The `USAGE` cell has an `effort:` line directly after `model:`; the
  host transcript records both on every message.
- The control plane starts every seat with the model and effort its dispatch names. A dispatch
  with a top-level `profile:` field also carries top-level `model:` and `effort:` fields
  (`dispatch_lint.py` rule R8).
- A seat whose model or effort differs from its profile's entry is a red (`MODEL_MISMATCH` or
  `EFFORT_MISMATCH` in `usage_report.py`), and the review record explains it. A receipt without
  an `effort:` line prints `EFFORT_UNRECORDED`, which is not a red by itself.
- The elevation route for a hard ticket stays `implementation-elevated`, with its own entry in the
  expectation file.
- The control plane appends each seat's `USAGE` cell (receipt grammar in
  `skills/johnny-project-takeover/scripts/README.md`) from the host's report after the seat
  returns; a seat does not write its own. `evidence_gate.py` checks the cell's form and never
  requires it. `skills/johnny-project-takeover/scripts/usage_report.py --expectation <file> <receipt>...` enforces presence and prints
  one verdict per seat.
- Order of the receipt checks: P9 judges the receipt as the seat returned it, before the control
  plane appends any `USAGE` cell. After appending them, the control plane reruns E1 only. P9 is
  not rerun on a receipt that holds `USAGE` cells, because its checker reads every section but
  `STATEMENT` as a run cell.
- A seat over its expectation, or off its model or effort, is a fact to explain in the review
  record. It is not a block on integration.
- The values in the template are a proposal taken from wave 2 (the 90th percentile per role over
  129 seat runs, rounded up): `implementation-standard` 130000 output and 24000000 processed,
  `implementation-elevated` the same until measured, `ticket-review` 110000 output and 23000000
  processed. The owner confirmed these values on 2026-11-18 ("1A", `REQ-20261103-043`).

## 最小派工訊息

同生命週期訊息只傳一次性的 `ACTION_REQUIRED`、精確 ticket、reviewer-established baseline
與 worktree/branch binding；需要時可加一行有界 resume state。`dispatch_ref`、registry
commit、receipt 與 owner task 是跨生命週期 receipt-bound 路徑的欄位，不得反向成為同步派工
前置條件。不要重抄 ticket 已定義的 scope、驗收、TDD、邊界、安全或 return contract。
實作者從精確 ticket 讀取那些規則，並依 ticket 的 owner override 決定是否 commit；P8R 的
override 明定實作者不 commit。

## Revision record

`REVISION_04` (2026-11-19, ticket 76) binds every seat's model and effort to its profile, as
described in "Token use per seat and the expectation". The provider-neutral registry above is
unchanged. It records the host values observed for the usage expectation of this repository
(`doc/handoffs/2026/workflow-governance/usage-expectation.json`, not shipped) as observed host
data, not as dispatch policy:
- `implementation-standard`: `claude-sonnet-5-5` at `high`, as observed on the seats of tickets 65,
  66, 68, 69, 70 and 72;
- `ticket-review`: `claude-opus-5-5` at `high`, as observed;
- `implementation-elevated`: assumed equal to `ticket-review` until measured, since no elevated
  seat has run.
The registry's `xhigh` for these three profiles differs from the observed `high`. That difference
is a calibration item for the owner; this revision does not change the registry.

`REVISION_03` corrects a false universal admission prerequisite. It aligns this profile with
`ADR-20260824-020` decision 8: descriptor/receipt/gateway evidence belongs only to the
cross-lifetime receipt-bound path; the reviewer-owned synchronous path remains bridge-free.
`REVISION_02` superseded the previous provider-specific Sonnet/Opus/Fable mapping. Its
provider-neutral model policy remains unchanged: Luna/xhigh is the standard implementation
profile; Terra/xhigh is normal review and the sole single-ticket implementation elevation;
Sol/high is limited to decision support and the corresponding elevated review. The previous
mapping remains available through Git history, not as active dispatch policy.

`CHG-20261103-043` (2026-11-03) amends the P8R submission sentence above: submission to the merge
queue by the implementation owner or a budget holder who is not the candidate's reviewer;
integration by the versioned integration script (workflow-governance Revision 04 R4-4).
