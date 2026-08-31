# Plugin adoption quality tickets

This partition contains only direct-child ticket metadata. Consumers resolve one exact ticket;
they do not load both clusters or copy ticket bodies into dispatch prompts.

| Child ID / leaf | Kind | Revision | SHA-256 | Lifecycle | State |
| --- | --- | --- | --- | --- | --- |
| [wa-01-activation-host-gate-contracts](wa-01-activation-host-gate-contracts.md) | `IMPLEMENTATION_TICKET` | `05` | `32ac8d730b49d390386dfd2f5e2171016e9808aa2f2e74b056d4bcb9a9f416f5` | `CLOSED` | `APPROVED / AUTHORITY_INTEGRATED` |
| [uix-01-codesign-contracts-lifecycle](uix-01-codesign-contracts-lifecycle.md) | `IMPLEMENTATION_TICKET` | `03` | `d2ba0ef2d19102191b0b2f164c6f1c4a681553acadccb794e04712e50a3365da` | `CLOSED` | `APPROVED / AUTHORITY_INTEGRATED` |
| [wa-02-project-activation-host-effect-adapter](wa-02-project-activation-host-effect-adapter.md) | `IMPLEMENTATION_TICKET` | `01` | `95fce94a98fb510432d19c3d6d7daaebdc9c4ee14dfbc04ba3e9de2bf2b624e0` | `ACTIVE` | `CAPABILITY_BLOCKED / NON_DISPATCHABLE` |
| [uix-02-reference-renderer-evidence-admission](uix-02-reference-renderer-evidence-admission.md) | `IMPLEMENTATION_TICKET` | `02` | `8de151e0600d669e8031ca49a2195abaeaf46c36f66369b1783252c2a9bd46d9` | `ACTIVE` | `APPROVED / DISPATCHABLE` |

The architecture approval at `d684f1479573475c82cad7d4a4abecc60e9665e3` authorized opening
these first tickets. The project owner approved their exact revision-01 candidate at
`5b8adfee3201d8a945a775d5a238e8c6acfca8ee` on 2026-08-31. `WA-01` dispatches first;
`UIX-01` reuses the implementation owner only after that allocation is released. Their
source/test/element boundaries are disjoint, and neither authorizes any target/host/provider effect
or shared `PAQ-REL-01` publication.

WA-01 revision 03 was the convergence proposal after the reviewer's independent alias-bypass
counter-mutation left WA7 green. It added one discriminating WAM4 evidence cell without changing
the production contract or source boundary. The project owner approved exact candidate
`2dca143f297c64058fdbc720038d75d59032e0b5`; revision 04 records that authority and permits one
fresh correction dispatch to the existing implementation owner.

WA-01 and UIX-01 source plus indexed review evidence are authority-integrated. Their shared
implementation-owner allocation is released. Neither closure implies renderer/provider execution,
target adoption, publication, installation, release or deployment.

On 2026-08-31 the project owner authorized opening WA-02 and UIX-02. WA-02 records the real
upstream blocker: no committed independently protected host external-effect gateway is qualified,
so it cannot dispatch or fall back to the legacy check-then-replace writer. UIX-02 is a pure
renderer-evidence admission ticket whose exact revision-01 candidate was approved by the owner on
2026-08-31; revision 02 records that authority and permits one same-lifetime implementation lane.
It grants no renderer, provider, target-write or publication effect.
