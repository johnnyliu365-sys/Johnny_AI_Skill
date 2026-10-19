# Continuous Workflow Governance POC — Ticket Set

> Approved specification: [workflow-governance.md](../../spec/workflow-governance.md) (`SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`). This ticket set creates no implementation authority by itself.

## Delivery objective

Deliver one control-plane policy vertical slice: completion evidence must re-enter the Router, safe stages continue in the active task, declared authority gates wait precisely, unsafe conditions halt, and implementation work returns its evidence or a requirement-change event to the control plane. The slice applies the same rules to formal frontend handoff without adding a target-project runtime dependency.

## Ticket status

| Ticket | User-observable capability | State | Required authority |
| --- | --- | --- | --- |
| [01-enforce-continuation-and-handoff](01-enforce-continuation-and-handoff.md) | Post-commit Router continuation, typed implementation return, and policy/template enforcement | `DONE` | Review approved; integrated into `main` by merge `2f545c8` (the ticket file records the closure; this row had gone stale) |
| [02-repo-contained-worktree-layout](02-repo-contained-worktree-layout.md) | Every agent's worktree lives under the repository root, proven host-side | `CLOSED` | Owner-executed 2026-08-19; R1-R6 green, reverse mutation proven. The dispatch-admission gate its R3 anticipated is now wired by workstation-dispatch W1 |
| [03-suite-order-fragility](03-suite-order-fragility.md) | A poisoned shared runtime root is reported once, with its cause and remedy, instead of eighty misleading failures | `CLOSED` | Real cause found: per-process claim map versus a shared on-disk root, orphaned by concurrent pytest processes. The opening diagnosis was wrong and is corrected in place |
| [04-skill-implies-a-runtime-that-may-not-exist](04-skill-implies-a-runtime-that-may-not-exist.md) | The skill no longer narrates wakes nothing performs; agents must verify automation readiness before claiming any automatic effect | `CLOSED` | Found by the owner watching a false wake narrative on a real project; ships as 0.4.4 |
| [24-independent-admitted-ticket-continuation](24-independent-admitted-ticket-continuation.md) | A waiting ticket cannot freeze an unrelated admitted ticket or transfer its authority | `OWNER_WAIT_SLICE_LOCAL_INTEGRATED` | `af24945f` gated and another seat verified exact blob parity; B full closure preserved in Ticket 30 |
| [25-refactor-test-seam-transfer](25-refactor-test-seam-transfer.md) | A responsibility split moves behavior tests and mutation targets with the production seam before the next split | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `970b99cc`; checklist 04 closed by Tickets 33–34 |
| [26-active-writer-worktree-branch-uniqueness](26-active-writer-worktree-branch-uniqueness.md) | The existing worker-claim ledger rejects two active writers on one worktree or branch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `9cedb55f`; generic prewrite protection still open |
| [27-evidence-linked-ticket-status-projection](27-evidence-linked-ticket-status-projection.md) | Opt-in evidence-bearing stage projection rejects false APPROVED with required work unverified | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `3196712d`; parent/finding projection added by Ticket 35, formal closure still open |
| [28-minimal-complete-dispatch-ticket](28-minimal-complete-dispatch-ticket.md) | One ticket template carries sourced Expected, I/O, failure/boundary acceptance and stop/review conditions | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review approved; `cfa46704`; Host dispatch admission still open |
| [29-mainline-ticket-projection](29-mainline-ticket-projection.md) | Separate the work mainline from a single ticket; recommend next recheck without granting dispatch | `SLICE_LOCAL_INTEGRATED` | Independent review approved; `2fa4ca6f`; trusted source and formal closure remain open |
| [30-trusted-independent-ticket-continuation](30-trusted-independent-ticket-continuation.md) | Source-bound candidate and bounded native protection-tool construction, without Host/closure authority | `LOCAL_BATCH_RESOURCE_AMENDED / N2_N3B2_C1_F1_C2_C3_C4_N4A1_ENGINEERING_STAGED_PASS / C5_E01_CHANGES_REQUESTED / B3_F01_ENGINEERING_PASS / QUALIFIED_AUDIT_BLOCKED / 30B_REVIEW_BLOCKED` | C4 final8a24b9eb/seal468e9c6b; N4-A1 final5449c063/seal74fd796a. C5 candidate38417fe9/closure11 E01 actual-vs-expected evidence correction; no Host/source qualification or integration, history preserved |
| [31-semantic-model-profile-boundary](31-semantic-model-profile-boundary.md) | Keep universal Skill model-neutral and distinguish product work from script-only delivery | `31B_LOCAL_INTEGRATED / CLEANUP_BLOCKED` | Model slice68a10057 retained; report slice independently approved e83a4a72, gate64157fbe,65tests and exact3blob parity. Paid-test isolation remains unverified; teardown policy-blocked, no normal closure |
| [32-test-consumer-inventory](32-test-consumer-inventory.md) | Find direct and indirect test consumers before test retirement | `SLICE_LOCAL_INTEGRATED` | Independent review and control gate passed at `2a19406d`; Host/CI retirement admission open |
| [33-shared-context-service-seam](33-shared-context-service-seam.md) | TEST→A transfers actual Shared Context behavior from Router to one service | `A_LOCAL_INTEGRATED` | Independent review approved; `ac369235`; B test seam/retirement still open |
| [34-shared-context-test-seam-transfer](34-shared-context-test-seam-transfer.md) | Move five contract-only cells while keeping public Router behavior cells mutation-sensitive | `B_LOCAL_INTEGRATED` | Independent review approved; `b4a7dbe6`; checklist 04 complete locally |
| [35-parent-finding-status-closure](35-parent-finding-status-closure.md) | Show required child and Finding closure without a false APPROVED parent | `SLICE_LOCAL_INTEGRATED` | Independent review approved correction; `215a599f`; projection only, formal Review authority still open |
| [36-git-pinned-test-source-inventory](36-git-pinned-test-source-inventory.md) | Read test consumers from an exact Git commit instead of caller-supplied working-copy text | `SLICE_LOCAL_INTEGRATED` | Independent review approved correction; `e1ca2d4b`; CI commands and retirement authority still open |
| [37-retired-wpr-commit-conflict](37-retired-wpr-commit-conflict.md) | Remove the obsolete standalone WPR commit completion obligation and keep its policy pins aligned | `SLICE_LOCAL_INTEGRATED` | Initial review found a timing defect; same-ticket correction approved and locally gated at `2f1c29cb` |
| [38-reuse-and-responsibility-dispatch-contract](38-reuse-and-responsibility-dispatch-contract.md) | A dispatch ticket names reused modules, separate code/test/script responsibilities and bounded growth evidence before implementation | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review and document gate approved at `3557bc20`; Host admission and semantic structural review remain separate gaps |
| [39-literal-suite-consumer-inventory](39-literal-suite-consumer-inventory.md) | Trace literal SUITES registry references through Python wrappers before test retirement | `INVENTORY_SLICE_LOCAL_INTEGRATED` | Independent review approved correction and local gate integrated `e9177f80`; real CI command source and retirement authority stay open |
| [40-scaffold-ticket-template-parity](40-scaffold-ticket-template-parity.md) | Keep the shipped new-project ticket scaffold aligned with current single-ticket fields | `TEMPLATE_SLICE_LOCAL_INTEGRATED` | Independent review approved candidate `91ee17c3`; exact-blob replay passed document gate at `5776139a`; Host admission remains open |
| [41-bounded-spec-correction-integration](41-bounded-spec-correction-integration.md) | Integrate the two owner-authorized bounded corrections into the original SPEC design baselines | `DESIGN_LOCAL_COMPLETE / CLEANUP_CONFIRMED / RUNTIME_NOT_EFFECTIVE` | Original design replay `76d1f942`; independently reviewed state-binding correction `cca2db71`; sealed two-record journal and exact isolated teardown verified; runtime/Host activation separate |
| [42-retired-workprogress-template-consistency](42-retired-workprogress-template-consistency.md) | Remove the retired WorkProgress return obligation from both ticket templates | `COMPLETE_LOCAL / CLEANUP_CONFIRMED` | Independently reviewed candidate `0d4dbb14`, gate `INTEGRATED`; 46 tests; sealed journal and dedicated worktree/ref teardown verified, Host effect unclaimed |

Local batch child (not an invented member of the bounded29→30 mainline):
[43-review-closure-evidence](43-review-closure-evidence.md) — checklist07/09/12,
SPEC AC11 existing Review route; `ENGINEERING_PASS / REVIEW_BLOCKED`, candidate
`d477020e0fb010ea12d610e3588630284472ecf8`; independent19tests/58subtests and
different-door reverse mutation passed. Required qualified Host adversarial audit
is UNAVAILABLE; no integration. Exact local Grant traces `batch-checklist-local-20261018`.

[44-requirement-revision-compatibility](44-requirement-revision-compatibility.md) —
checklist03/11/12, existing AC17 reviewed design; `LOCAL_INTEGRATED / CLEANUP_BLOCKED`
at `1aa5ed22bc270b8d8604be89c9f23b0942c8dee5`, independent14tests/30subtests,
reviewed blob parity and immutable seal confirmed. Host policy rejected teardown
before execution; registered resources remain. Pure history compatibility only;
legacy validation/activation unchanged. No normal closure or whole-checklist PASS.

[45-ticket-content-completeness](45-ticket-content-completeness.md) — checklist03/12,
AC10 pure instance-content diagnostics; LOCAL_INTEGRATED / CLEANUP_BLOCKED,
guarded local commit a29c0e53a3fb868248d53eb9442dd6719daf1e09, independent
revision02 approval and152tests. No committed-source, grant, receipt or Host
admission claim; exact two reviewed blobs read back, old holds unchanged.

[46-versioned-local-test-commands](46-versioned-local-test-commands.md) — checklist08/12,
LOCAL_INTEGRATED / CLEANUP_BLOCKED at a0bfc286, independently reviewed2ba55781;
36tests/22subtests, strict and compile/import passed; local command-source follow-up
to36/39, one versioned local-only plan,
same-commit Git readback and existing inventory, no test CI or retirement authority.

## Shared baseline

- Specification: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`)
- Change: `CHG-20260805-009`
- Context: [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md)
- Documentation baseline: `04146af` (`docs: draft continuous workflow governance`)
- Delivery environment: local Python workflow-router POC plus detached Codex/Claude guidance source. No hosted service, background worker, target-project dependency, or external provider is in scope.

## 30M mainline provenance and scope

This migration declares **only the bounded trusted-continuation mainline**, not the
entire historical feature or the twelve-outcome improvement programme. The approved
REQ-20260805-009 continuity amendment and SPEC AC9 distinguish a mainline from a
ticket; the owner's 2026-10-18 document-migration authority permits recording the
evidenced slice. Ticket30's existing proposal and actual reuse identify 29→30.
The programme still requires all twelve outcomes; unchecked items are not optional.
No order in that checklist creates a ticket dependency.

| Metadata / fact | Exact source, approval and interpretation |
| --- | --- |
| `objective-wg-continuation` | Delivery objective above, REQ-20260805-009 continuity amendment, SPEC AC9–11: retain the mainline across ticket completion and independent waits. This graph covers only the projection→trusted-continuation capability chain, not all programme work |
| `owner-wg-control` | Owner's checklist work principles and Ticket30 Roles: Root owns requirements, conflict resolution, orchestration and integration; a named implementer has only its exact phase Grant; another seat independently reviews. No model name implies authority |
| `handoff-wg-continuation` | Ticket29 Objective/Expected and Ticket30 source/Stop/Return: implementation returns candidate/files/checks/findings/deviations; Root rechecks authority, sources and dependencies before any next action. Per-phase role/worktree/baseline is in Ticket30, not inherited from historical Ticket01 |
| `wg-ticket-29`, required | Ticket29 pure-projection scope, unchanged baseline leaf `6b7c3dc3f83bae8469199afd6fb372582dddaa31`. `completed` means that local deliverable only. `admission-wg29-local` resolves to `2fa4ca6f075e3692fbb085670fa4b303b0ba09ef`; `review-wg29-slice` resolves to the exact review leaf blob `4bc3fed5bf89d9c8c3693375a3925852d3ad9c9f`, APPROVED_SLICE, candidate `9a07cc5b5611c856807a7085ad3a41701613dc56` |
| `wg-ticket-30`, required; depends on29 | Ticket30 reuses `mainline_projection.py`, developed by29; its 30A assembly calls that projection. Baseline leaf `7d7fa0358641b508fdbbf684324151bc878e0ab2`. Full Ticket30 is not admitted: the consumed 30A Grant does not cover real-source/effect work. `waiting` is this read-only projection's open node awaiting the next phase Grant/remote-source availability, not a Router WAIT_FOR_HUMAN event or a global freeze |
| `review-wg30a-fixture` | Existing Ticket30 review, Closure02 correction and integration seal: reviewed `629030f4678b5d600c9ad53baf60967c25ecefbc`, locally gated `b7e9e2f35bd997c65df80541ec0196a000ab3e46`, 91 focused tests, fixture-only. Evidence is retained; it grants no admission to the remainder |
| Optional / outside scope | No optional node is identified within this two-node slice. Other feature tickets remain in the historical human registry, not silently classified optional. Required/optional membership for a **full-programme** graph is not established by this migration |

Version/provenance bindings below are immutable source **commit** SHAs, not blob SHAs
or moving HEAD. Context04 and SPEC03 both resolve at
`0c5ff55db4f3875091c2a37a4c9fcc36a7055e7c` to blobs
`06baa4dea5db1c3370086552c35a1d8f721ad47e` and
`a700cad60de40096770582b04915bf490fd66a19`. The canonical combined PRD/CHG leaf
at `e551c556bc37c413e26d21e6795dbf10673c355c` is blob
`1bc5e679944aeb6d7b830ccbf2b3fd768b599548`: both bindings intentionally refer to
the same existing leaf, not newly duplicated requirement/change documents.
Context04's authority declaration retains the owner's exact acf0ffa1 / ded322b3
approval provenance; SPEC03 retains 35b25d60 independent review and fixture-only
bootstrap. No source text is copied into the machine block.

The wire types require opaque lower-case IDs. Architecture Owner assigns technical
aliases `context-johnny-rev04` and `spec-wg-rev03` to those exact artifacts; the latter
maps to full SPEC ID `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`.
`prj_01c2721cc4852c4b` is the deterministic wire encoding
`prj_ + SHA256(UTF8("github.com/johnnyliu365-sys/Johnny_AI_Skill"))[:16]`, not a newly
discovered approved project ID or an authority source. Only the approved Context04
repository/ref and its exact independently read version supply identity authority;
aliases must be checked against that binding, never used to self-authorize a reader.
Each `ticket_revision` is SHA256(baseline committed leaf bytes + NUL +
`mainline-migration/revision-01`) prefixed `rev-`: an assigned migration revision,
not a self-referential file digest. The separate `leaf_digest` hashes the final
committed raw bytes after all leaf edits, including these machine sections.

Unproven relations are not encoded as false facts: full-programme required/optional
ticket membership and its cross-feature edges remain UNKNOWN. Existing evidence
shows reuse chains25→33→34,27→35,32→36→39, but not membership here. The historical
Ticket02 row says CLOSED while its exact leaf says OPEN; no decision on that
unrelated historical conflict is fabricated. Do not change sealed/closed contracts.
To expand this graph, recommend first map the twelve outcomes to already-approved
ticket scopes and validate each remaining edge; do not infer a dependency from its
number or re-request the already-approved programme objective. None of those gaps
blocks this bounded migration or independent admitted work.

## Mainline source contract

```json
{
  "schema_id": "mainline-index/revision-01",
  "project_id": "prj_01c2721cc4852c4b",
  "feature": "workflow-governance",
  "mainline_ref": "wg-continuation-mainline",
  "objective_ref": "objective-wg-continuation",
  "owner_ref": "owner-wg-control",
  "handoff_ref": "handoff-wg-continuation",
  "bindings": [
    {"kind": "context", "identity": "context-johnny-rev04", "artifact_ref": "CONTEXT.md", "revision_sha": "0c5ff55db4f3875091c2a37a4c9fcc36a7055e7c"},
    {"kind": "prd", "identity": "PRD-20260805-009", "artifact_ref": "doc/requirements/active/2026/workflow-governance/REQ-20260805-009.md", "revision_sha": "e551c556bc37c413e26d21e6795dbf10673c355c"},
    {"kind": "change", "identity": "CHG-20260805-009", "artifact_ref": "doc/requirements/active/2026/workflow-governance/REQ-20260805-009.md", "revision_sha": "e551c556bc37c413e26d21e6795dbf10673c355c"},
    {"kind": "spec", "identity": "spec-wg-rev03", "artifact_ref": "modules/spec/workflow-governance.md", "revision_sha": "0c5ff55db4f3875091c2a37a4c9fcc36a7055e7c"}
  ],
  "tickets": [
    {"ticket_ref": "wg-ticket-29", "ticket_revision": "rev-fbf3d7b26587673550ebfc2395b6d8b7375f13fe6480aefab05db44f168293ad", "leaf_ref": "modules/tickets/workflow-governance/29-mainline-ticket-projection.md", "leaf_digest": "sha256_d6d3b25dd516ea4f2fb9daf90f1b39917e0f5bc9ecc3e647492656f411efe94f", "required": true, "status": "completed", "depends_on": [], "admission_ref": "admission-wg29-local", "evidence_refs": ["review-wg29-slice"]},
    {"ticket_ref": "wg-ticket-30", "ticket_revision": "rev-535a99b32754942aacc4870710766125881110e5f61646594a6d049846a8704d", "leaf_ref": "modules/tickets/workflow-governance/30-trusted-independent-ticket-continuation.md", "leaf_digest": "sha256_5e28ca25a5e01e8912cf1b496108157b3d758c37be4a875def7e1cac4e778fc0", "required": true, "status": "waiting", "depends_on": ["wg-ticket-29"], "admission_ref": null, "evidence_refs": ["review-wg30a-fixture"]}
  ]
}
```

Document migration is not source/Host qualification. Until independent review,
guarded local integration, source publication and a qualified readback are separately
proved, this block is only the versioned declaration input. It cannot issue a
receipt, dispatch/spawn, qualify a Host, or close Ticket30/checklist01/02. Future
readback must validate every mirrored field and raw digest at one fresh observed
authority SHA; it must not call the fixture-only request with real documents.

## Authority and handoff

The following is **historical Ticket01 handoff only**, not an active writer allocation:
the separate `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree,
branch `codex/implementation-private-router-saas-01`, baseline `7769710`, and
2026-08-05 approval. Ticket01's completed contract is not reopened. Current control
ownership and phase-scoped handoff are resolved through the 30M provenance above
and exact Ticket30 phase records; no old path grants current write authority.

The implementation handoff consists of the approved specification, this ticket, Context references, TDD cuts, exact target paths, and the return-event rules. A completion returns evidence for review; a requirement, architecture, public-contract, frontend composition/DI, or acceptance change returns `REQUIREMENT_CHANGED` to Grill.
