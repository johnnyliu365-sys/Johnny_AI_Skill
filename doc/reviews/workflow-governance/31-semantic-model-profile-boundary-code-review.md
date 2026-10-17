# Ticket 31 independent review — 2026-10-18

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/31-semantic-model-profile-boundary.md` |
| Baseline | `c5c1bc7135458f3e9476aa27df13c9e75f9f3cec` |
| Final candidate | `ffd9d7c8400d948cbc11b821699c06f09537fb08` |
| Reviewer | Separate `gpt-6-sol/high` read-only seat |
| Conclusion | `APPROVED_SLICE`; model selection only, checklist 10 remains open |

The first candidate `42e0074d` changed only four declared paths and passed its
targeted tests, but its low-tier test had no simultaneously available high-tier
profile. The reviewer refused it as insufficient evidence. The additive
correction `4f9ecb2d` supplied both profiles and an ordinary `TICKET_OPENING`
route; reviewer-owned in-memory mutation selecting the high profile turned the
named cell red, and restoration returned it to green. The reviewer then found
that unconditional Host readback wording contradicted same-lifetime dispatch's
`NOT_REQUIRED` rule. Final correction `ffd9d7c8` requires applicable verified
model availability/capability evidence without requiring synchronous
task/workspace/profile readback, gateway, receipt or runner. Cross-lifetime
requirements remain distinct.

Final targeted run: `python -m pytest tests/test_adversarial_review_policy.py
tests/test_executor_routing.py -q` → 36 passed, 74 subtests; `git diff --check`
and worktree clean. Root cherry-picked the three reviewed commits onto the
current checklist branch and verified all four final Git blobs exactly match
the approved candidate. The control-plane mutation gate returned `INTEGRATED`
at `68a100579bdf943e6ed0c98f5242f84f15839deb`. No push, release, paid
provider call or real Host qualification was performed. Paid-test isolation
and fixed human report fields remain outside this slice.
