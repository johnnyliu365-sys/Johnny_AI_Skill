# 派工模型 Profile（現行主機對應）

| Field | Value |
| --- | --- |
| Revision | `2026-08-22 / REVISION_02` |
| Requirement lineage | `PRD-20260822-030` / `CHG-20260822-030` / `doc/requirements/active/2026/adaptive-orchestration/REQ-20260822-030.md` |
| Policy source | `modules/spec/executor-routing.md` revision 01 and `modules/tickets/workstation-dispatch/p8-provider-neutral-executor-routing.md` revision 02 |
| Authority | Project owner directive, 2026-08-22 (Asia/Taipei) |
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
- Dispatch requires the live descriptor, exact ticket/handoff artifacts, receipt, verified task
  workspace/worktree/branch/baseline binding, and the host gateway. A stopped runner does not
  prevent manual receipt admission, but it means no automatic wake may be claimed.
- The implementation owner receives identifier-only dispatch, modifies only its declared
  boundary, and returns a typed result. The owner directive for P8R says the reviewer writes
  the candidate commit after review and is the only role that submits it to integration.
- A provider credential or host execution failure is a named capability result. It is neither
  permission to substitute another profile nor evidence that a selected profile ran.

## 最小派工訊息

派工訊息只傳一次性的 `ACTION_REQUIRED`、`dispatch_ref`、registry commit、ticket、receipt
與 owner task；需要時可加一行有界 resume state。不要重抄 ticket 已定義的 scope、驗收、
TDD、邊界、安全或 return contract。實作者從精確 ticket 讀取那些規則，並依 ticket 的
owner override 決定是否 commit；P8R 的 override 明定實作者不 commit。

## Revision record

`REVISION_02` supersedes the previous provider-specific Sonnet/Opus/Fable mapping. It applies
the owner-approved provider-neutral policy in `REQ-20260822-030`: Luna/xhigh is the standard
implementation profile; Terra/xhigh is normal review and the sole single-ticket implementation
elevation; Sol/high is limited to decision support and the corresponding elevated review. The
previous mapping remains available through Git history, not as active dispatch policy.
