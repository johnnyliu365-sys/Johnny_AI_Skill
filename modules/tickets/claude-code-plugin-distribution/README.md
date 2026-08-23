# Claude Code Plugin Distribution Tickets

| Field | Binding |
| --- | --- |
| SPEC / Context | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` Revision 03 / sealed Context Revision 02, blob `f53b2a7dedf055e50ad44804e590f22991a3d5c9` |
| Requirement / architecture | `PRD-20260823-034` / `CHG-20260823-034`, amended by `PRD-20260823-035` / `CHG-20260823-035` / `ADR-20260823-015` and `ADR-20260823-017` |
| Planning baseline | `1caa2f2355638c75610dc848b5bd23d8f97d0bcb` |
| Control owner / reviewer | Terra `ticket-review` profile; profile selection remains capability-verified at dispatch. |
| State | `REVISION_03 / F3_SERIAL_DECOMPOSITION_AUTHORIZED` |

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
| [08-isolated-publication-live-cutover.md](08-isolated-publication-live-cutover.md) | `BLOCKED / OWNER_EFFECT_AUTHORITY_REQUIRED / SUCCESSOR_VERSION_0.4.11` / `CLOSURE_03_PENDING` | A real isolated Claude install from README reaches only the publication object graph. | F3 integrated at `7a64f63`; owner selected `0.4.11`. A fresh exact external-effect authority and L1–L6 proof remain required before re-admission. |
| [09-pin-carrier-closure-normalization.md](09-pin-carrier-closure-normalization.md) | `DONE / APPROVED / INTEGRATED` — `ca9e988` | The Ticket 06 closure treats the self-pin carrier by the same strict, reversible normalizer as the generator. | Ticket 08 L2 blocker is repaired locally; its publication candidate still requires regeneration, re-pin and full L2 readback. |
| [10-installed-cache-symbolic-remote-head.md](10-installed-cache-symbolic-remote-head.md) | `DONE / APPROVED / INTEGRATED` — `829aaa0` | A normal clone's symbolic remote default head is admitted only when it is strictly bound to the same remote `main` root and payload closure. | CLOSURE_02 admits only exact raw LF and rejects CRLF/trailing whitespace; independent reverse mutations and strict checks passed. Ticket 08 still requires a fresh owner re-admission and full live L1–L6 proof. |
| [11-level-one-payload-topology.md](11-level-one-payload-topology.md) | `DONE / APPROVED / INTEGRATED` — `7a64f63` | The Level 1 declaration is exactly the reachable reusable-source surface, excluding host-local publication/cache/installer tooling. | `POC / STANDARD`; independently reverse-mutated, gate-integrated and pushed. It enabled successor version selection but not Ticket 08's external effects. |

No ticket authorizes a runner, queue, receipt, host gateway, remote Git mutation, repository
creation, public release or user-installation effect by implication. Same-lifetime POC coding and
review use the reviewer dispatch/wait/receive loop; the guarded integration gate remains the only
main mutation control. Ticket 08 separately names its real external effects.
