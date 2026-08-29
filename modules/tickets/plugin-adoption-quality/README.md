# Plugin adoption quality tickets

This partition contains only direct-child ticket metadata. Consumers resolve one exact ticket;
they do not load both clusters or copy ticket bodies into dispatch prompts.

| Child ID / leaf | Kind | Revision | SHA-256 | Lifecycle | State |
| --- | --- | --- | --- | --- | --- |
| [wa-01-activation-host-gate-contracts](wa-01-activation-host-gate-contracts.md) | `IMPLEMENTATION_TICKET` | `01` | `bffbcec38db0b55dbab93da4be741432a37494996dc9459212008690af8539f7` | `PLANNED` | `OWNER_TICKET_APPROVAL_PENDING / NON_DISPATCHABLE` |
| [uix-01-codesign-contracts-lifecycle](uix-01-codesign-contracts-lifecycle.md) | `IMPLEMENTATION_TICKET` | `01` | `6792c32ac438b1000fc4439c9e6a11c7cd6ca93c8cdbda7511289a28882ffe16` | `PLANNED` | `OWNER_TICKET_APPROVAL_PENDING / NON_DISPATCHABLE` |

The architecture approval at `d684f1479573475c82cad7d4a4abecc60e9665e3` authorized opening
these first tickets only. Each exact ticket requires separate owner approval before dispatch.
`WA-01` and `UIX-01` have disjoint source/test/element boundaries; neither authorizes the other's
lane, any target/host/provider effect or shared `PAQ-REL-01` publication.
