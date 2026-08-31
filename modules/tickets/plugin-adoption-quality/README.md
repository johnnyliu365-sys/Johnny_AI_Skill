# Plugin adoption quality tickets

This partition contains only direct-child ticket metadata. Consumers resolve one exact ticket;
they do not load both clusters or copy ticket bodies into dispatch prompts.

| Child ID / leaf | Kind | Revision | SHA-256 | Lifecycle | State |
| --- | --- | --- | --- | --- | --- |
| [wa-01-activation-host-gate-contracts](wa-01-activation-host-gate-contracts.md) | `IMPLEMENTATION_TICKET` | `03` | `723598f5a99cd5cc86c20a5463901fdac00e020b6c4bb9ad9d37687d82ecd61c` | `ACTIVE` | `OPEN / CONVERGENCE_APPROVAL_REQUIRED / NON_DISPATCHABLE` |
| [uix-01-codesign-contracts-lifecycle](uix-01-codesign-contracts-lifecycle.md) | `IMPLEMENTATION_TICKET` | `02` | `439b0ddc481c166081956aed0c576045e450520ad7639e7ecc01ba13d52c722a` | `ACTIVE` | `OPEN / APPROVED / DISPATCHABLE_AFTER_WA_01_ALLOCATION_RELEASE` |

The architecture approval at `d684f1479573475c82cad7d4a4abecc60e9665e3` authorized opening
these first tickets. The project owner approved their exact revision-01 candidate at
`5b8adfee3201d8a945a775d5a238e8c6acfca8ee` on 2026-08-31. `WA-01` dispatches first;
`UIX-01` reuses the implementation owner only after that allocation is released. Their
source/test/element boundaries are disjoint, and neither authorizes any target/host/provider effect
or shared `PAQ-REL-01` publication.

WA-01 revision 03 is a convergence proposal after the reviewer's independent alias-bypass
counter-mutation left WA7 green. It adds one discriminating WAM4 evidence cell without changing the
production contract or source boundary. It is not dispatchable until the owner approves its exact
candidate.
