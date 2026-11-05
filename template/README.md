# 新專案工作環境 Bootstrap 模板庫

本目錄是新專案建立時的受版控模板庫；通用發行版必須附帶同一份 `template/` 目錄。

## 固定結構

```text
<project-root>/
├─ Workflow.md
├─ AGENTS.md
├─ CONTEXT.md
├─ PRD.md                         # active requirement root index
├─ ProjectSchedule.md
├─ modules/
│  ├─ spec/
│  ├─ tickets/
│  └─ element/{typescript,python,java}/
└─ doc/
   ├─ context/                    # architecture feature Context leaves
   ├─ requirements/
   │  └─ active/<year>/<domain>/
   ├─ archive/
   │  └─ requirements/<year>/
   ├─ reviews/
   ├─ adr/
   ├─ handoffs/
   │  └─ <year>/governance/
   │     ├─ integration.json      # from integration.TEMPLATE.json
   │     ├─ MERGE-QUEUE.json      # from MERGE-QUEUE.TEMPLATE.json; lives on the queue branch only
   │     └─ <receipt>.md          # from RECEIPT.TEMPLATE.md, at the path a ticket's state row names
   ├─ RequirementChangeLog.md
   ├─ WorkProgressReport.md
   └─ security-agent-boundary.md
```

## 建置順序

1. 從通用發行版複製 `Workflow.md` 與 `AGENTS.md` 至新專案根目錄。
2. 建立上方固定目錄；不得建立 `doc/specs/` 或 `doc/tickets/`。
3. 複製並填寫 `CONTEXT.TEMPLATE.md`、`doc/context/TEMPLATE.md`、`doc/RequirementChangeLog.TEMPLATE.md`、
   `doc/requirements/REQ.TEMPLATE.md`、`doc/archive/requirements/ARCH-REQ.TEMPLATE.md`、`modules/spec/TEMPLATE.md`、
   `modules/tickets/TEMPLATE.md`、`doc/reviews/TEMPLATE.md`、`doc/adr/TEMPLATE.md` 與相符語言的 element 模板。
4. Copy the state-file templates (see "State files" below) before the first ticket needs them.
5. 先完成 `CONTEXT.md`、`PRD.md`、`ProjectSchedule.md`、需求變更與安全邊界的最小內容，再開始第一個 Grill。

## State files

A project starts with the four files the gates and the integration script read, so the first
ticket needs no hand-made file:

| Template | Copy to | Holds |
| --- | --- | --- |
| `modules/tickets/TEMPLATE.md` | `modules/tickets/<feature>/<ticket>.md` | the ticket; its state row reads `<STATE>`; dispatch=sha256:<hex of the dispatch file>; receipt `<path>` |
| `doc/handoffs/governance/RECEIPT.TEMPLATE.md` | the receipt path the ticket's state row names | one run cell per command, one statement cell per choice made where the work was silent |
| `doc/handoffs/governance/integration.TEMPLATE.json` | `doc/handoffs/<year>/governance/integration.json` | the integration configuration: remote, branch, queue branch, queue path, the spec, invariant and CI-status commands, the timeout |
| `doc/handoffs/governance/MERGE-QUEUE.TEMPLATE.json` | the `queue_path` key of the copied configuration, on the queue branch | the empty merge queue, `{"entries": []}` |

The queue file lives on the queue branch, not on the integration branch: copy it to `queue_path`
on the queue branch (by default `<branch>-queue`), never to the integration branch, so a queue
write never moves the integration tip. The configuration and the receipt live on the integration
branch like any other project file.

## Policy and dispatch safety

Templates keep policy reads metadata-only: raw document text, prompts, paths,
URIs, secrets and PII do not enter Router models or handoff evidence. A fixed
dispatch response is produced from the ticket's state row and the digest of its dispatch file
(workflow-governance Revision 04 R4-1); on the transitional bridge path it is produced from the live
Private Router pending descriptor and its reviewed ticket/handoff receipt, and a copied, replayed,
absent or mismatched descriptor is fail-closed there. `COMMERCIAL` is not an implied
objective; use `POC` unless an approved Profile and change record establish
another stage.
