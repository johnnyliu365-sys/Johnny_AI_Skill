# 05C — Codex Receipt-Bound Removal Parent

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `CONVERGENCE_DECOMPOSED / NON_DISPATCHABLE` |
| Dependency | Tickets 05A and 05B, including lifecycle/isolation E0-E6, independently approved and integrated |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Environment | Windows user scope through recorded ports and project-owned disposable staging only; no live Codex, target-project mutation, packaging, deployment or release |

## User-observable outcome

Given the exact persisted Codex registration receipt, one removal invocation
removes the receipt-owned plugin before the receipt-owned marketplace and
reports `REMOVED` only after fresh plugin, marketplace and installed-path
absence evidence agrees. A later invocation returns `NOT_INSTALLED` without a
remove effect. Invalid, foreign, mismatched or incomplete evidence returns
`UNINSTALL_BLOCKED` without touching unrelated state.

## Decomposition decision

The former C1-C5 closure mixed three independently reviewable responsibilities
and incorrectly required `host` and `HostRegistrationKey` from
`CodexRegistrationReceipt`. Those fields belong to the separate generic
`AgentHostReceipt` lifecycle and do not exist in the integrated Codex receipt.
This is a non-high-risk `TICKET_DEFECT`, not a product requirement change.

The parent is replaced by these serial children:

1. [05C1 — receipt removal request](05c1-codex-receipt-removal-request.md):
   pure recursive receipt admission and exact conversion to the integrated
   compensation manifest/request; zero effects.
2. [05C2 — receipt removal composition](05c2-codex-receipt-removal-composition.md):
   invoke only the admitted closed capability, preserve official remove order,
   settle fresh absence and replay into finite public results.
3. [05C3 — receipt removal acceptance](05c3-codex-receipt-removal-acceptance.md):
   prove full register/receipt/remove/replay behavior, foreign preservation and
   target-project non-interference in the integrated disposable staging oracle.

Only 05C1 is initially dispatchable. 05C2 depends on approved integration of
05C1; 05C3 depends on approved integration of 05C2. Overlapping typed contracts
and ordered effects make parallel implementation unsafe and unnecessary.

## Corrected ownership boundary

- The persisted `CodexRegistrationReceipt` is the Codex registration identity;
  05C does not invent a host key or a second receipt algebra.
- The removal invocation independently supplies the expected installation ID
  and canonical root. Receipt, invocation and every port proof must match.
- Structurally invalid, constructed, subclassed, extra/private-state or
  invocation-mismatched receipts block before effects. A byte-identical
  serialized/reloaded receipt remains the same persisted metadata identity;
  the former unimplementable prohibition on an indistinguishable "copy" is
  removed.
- Higher-level ledger integrity and owned-payload deletion remain with the
  installer ledger/package tickets. 05C may neither claim nor implement them.

## Shared restrictions

- Reuse only independently integrated registration receipt, compensation port,
  DTO and staging-oracle contracts. No rejected historical source may be copied
  or cherry-picked.
- No `Any`, `type: ignore`, optional/`None` port, caller-controlled dynamic
  member lookup, broad catch/clear, raw exception text, new dependency or
  numeric line limit is accepted.
- No live Codex/home/config effect, target-project write, network, push,
  staging publication, installer build/install, Secret, release or deployment.
- `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript
  context or privileged bridge is introduced. A later renderer must re-enter
  the Workflow XSS gate.

## Parent completion

This parent completes only after 05C1-05C3 are each independently approved and
guarded-integrated. It never receives an implementation branch, allocation or
receipt.
