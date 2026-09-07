# Plugin adoption quality tickets

This partition contains only direct-child ticket metadata. Consumers resolve one exact ticket;
they do not load both clusters or copy ticket bodies into dispatch prompts.

| Child ID / leaf | Kind | Revision | SHA-256 | Lifecycle | State |
| --- | --- | --- | --- | --- | --- |
| [hda-01-host-dispatch-admission-hook](hda-01-host-dispatch-admission-hook.md) | `IMPLEMENTATION_TICKET_PROPOSAL` | `01` | `c2b0a3d1beb04281c7f2650fcd20d56e6ec0a14b5711d76877c1e78cd3254ec5` | `PLANNED` | `OWNER_EXACT_APPROVAL_PENDING / NON_DISPATCHABLE` |
| [wa-01-activation-host-gate-contracts](wa-01-activation-host-gate-contracts.md) | `IMPLEMENTATION_TICKET` | `05` | `32ac8d730b49d390386dfd2f5e2171016e9808aa2f2e74b056d4bcb9a9f416f5` | `CLOSED` | `APPROVED / AUTHORITY_INTEGRATED` |
| [uix-01-codesign-contracts-lifecycle](uix-01-codesign-contracts-lifecycle.md) | `IMPLEMENTATION_TICKET` | `03` | `ea6999d898a857f744a925f1f400a18b9a6f1177f236653ddce27e96efe075a5` | `CLOSED` | `APPROVED / AUTHORITY_INTEGRATED` |
| [wa-02-project-activation-host-effect-adapter](wa-02-project-activation-host-effect-adapter.md) | `IMPLEMENTATION_TICKET` | `01` | `95fce94a98fb510432d19c3d6d7daaebdc9c4ee14dfbc04ba3e9de2bf2b624e0` | `ACTIVE` | `CAPABILITY_BLOCKED / NON_DISPATCHABLE` |
| [uix-02-reference-renderer-evidence-admission](uix-02-reference-renderer-evidence-admission.md) | `IMPLEMENTATION_TICKET` | `17` | `a1baa09958be1fcd57825b47947133ad1c854992dd013dc1ee0ebfb247d4873f` | `ACTIVE` | `APPROVED / LOCAL_INTEGRATED / REMOTE_SYNC_PENDING` |

## Historical approval notes

The table above is current; the following notes preserve earlier point-in-time states.

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
Its first candidate is not integrated: review proved the frozen evidence DTOs cannot express UIR6
request/content binding, so revision 03 recorded `TICKET_DEFECT`. Revision 04 proposed closure
revision 02 with an explicit evidence binding, complete truth table, bounded Unicode and canonical
field names. Revision 05 records exact owner approval and permits one additive same-ticket
correction. Revision 06 records that closure revision 02's initial candidate still accepts unsafe
opaque values and lacks reproducible named baseline-red evidence; its one additive correction is
now exhausted. Revision 07 records that the correction still has both defect classes and routes to
control-plane convergence; no third correction is dispatchable. It grants no renderer, provider,
target-write or publication effect. Revision 08 proposed closure revision 03; the project owner
approved that exact leaf and digest on 2026-09-01. Revision 09 records revision 03 as the effective
closure, while keeping implementation dispatch, a third correction, candidate integration, push,
publication and every external effect unauthorized. An adversarial audit then proved revision 03's
`L* / M* / N*` allowlist contradicts its zero-width rejection claim. Revision 10 records the
resulting `TICKET_DEFECT` and proposes closure revision 04 with an `L* / N*`-only grammar. The
initial proposal audit found a stale operative UIR1 rule and length-masked fixtures; revision 11
corrected both. The project owner approved that exact leaf and digest on 2026-09-01; revision 12
records closure revision 04 as effective while leaving implementation, a third correction,
integration, push, publication and every external effect unauthorized.

Revision 13 records the owner's 2026-09-05 execution authority: reuse the existing Luna/xhigh
owner and worktree for closure revision 04, then independent adversarial findings and current-session
review. Candidate integration, push, publication and external effects remain unauthorized.

Revision 14 records the completed closure-04 initial/correction review: candidate `b419954b`
remains unintegrated with three remaining evidence-defect families. The existing allocation is
preserved but further correction is non-dispatchable pending control-plane convergence.
