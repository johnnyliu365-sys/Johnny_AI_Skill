# Claude Code Plugin Distribution Tickets

| Field | Binding |
| --- | --- |
| SPEC / Context | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` Revision 02 / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| Requirement / architecture | `PRD-20260823-034` / `CHG-20260823-034` / `ADR-20260823-015` |
| Planning baseline | `8033a01ba2f3fc1a07bfa7c1c5bf41d9cd50f0b0` |
| Control owner / reviewer | Terra `ticket-review` profile; profile selection remains capability-verified at dispatch. |
| State | `REVISION_02 / SERIAL_DECOMPOSITION_AUTHORIZED` |

Tickets 01–05 remain completed evidence for payload declaration, content binding and old-source
reachability. They are not authority for publication-repository isolation. New tickets are serial:
06 establishes the read-only closure proof, 07 establishes a no-effect promotion contract, and 08
performs the one owner-authorized live cutover.

| Ticket | State | Sole observable closure | Admission / dependency |
| --- | --- | --- | --- |
| `01-claude-code-plugin` | `DONE` | Shared-skill plugin entry | Historical |
| `02-the-plugin-ships-the-whole-development-repository` | `DONE` | Payload declaration closure | Historical |
| `03-the-pin-and-the-tree-are-unrelated` | `DONE` | Pin/tree binding | Historical |
| `04-the-pin-is-not-bound-to-reachability` | `DONE` | Publication-anchor reachability | Historical |
| `05-reachability-measures-the-wrong-thing` | `DONE` | Clean-clone fetchability evidence | Historical |
| [06-publication-repository-closure.md](06-publication-repository-closure.md) | `DONE / APPROVED / INTEGRATED` — `46ad6d3` | A Git object graph is accepted only when every reachable ref/tree is declared payload. | `POC / STANDARD`; no remote publication effect. |
| [07-publication-promotion-compare-and-swap.md](07-publication-promotion-compare-and-swap.md) | `DONE / APPROVED / INTEGRATED` — `4a77414` | A promotion plan either binds one exact old/new/tag transaction or returns a finite refusal. | CLOSURE_01 converged on its evidence defect; CLOSURE_02 added the four direct P5 regressions and passed fresh Terra review. |
| [08-isolated-publication-live-cutover.md](08-isolated-publication-live-cutover.md) | `APPROVED / RE-ADMITTED` / `CLOSURE_02` | A real isolated Claude install from README reaches only the publication object graph. | Ticket 09 repaired L2; the candidate, root, remote snapshot and isolated install must all be regenerated/read back against `f099ff7` before any publication effect. |
| [09-pin-carrier-closure-normalization.md](09-pin-carrier-closure-normalization.md) | `DONE / APPROVED / INTEGRATED` — `ca9e988` | The Ticket 06 closure treats the self-pin carrier by the same strict, reversible normalizer as the generator. | Ticket 08 L2 blocker is repaired locally; its publication candidate still requires regeneration, re-pin and full L2 readback. |

No ticket authorizes a runner, queue, receipt, host gateway, remote Git mutation, repository
creation, public release or user-installation effect by implication. Same-lifetime POC coding and
review use the reviewer dispatch/wait/receive loop; the guarded integration gate remains the only
main mutation control. Ticket 08 separately names its real external effects.
