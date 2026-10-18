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

## 31B admission under the local batch

Original31 remains complete. Root-scoped `grant-wg31b-report-local-20261018`
traces `batch-checklist-local-20261018`, not a new PRD. Independent
`/root/batch_authority_review` APPROVED docs at
`ce9c2c08d7d10186daeffafb5f39f06dac22561e`, ticket blob
`e1db75ef2e156fd869bf035b96b71fc25278147d`. Only three existing template/test
paths; no product/runtime or Host-isolation claim. Root verified source parity
fromcfd64358, then allocated clean non-reparse contained
`.worktrees/skill-improvement-31b-report`, branchcodex/skill-improvement-31b-report,
baseline`1aa5ed22bc270b8d8604be89c9f23b0942c8dee5`, exact same ticket.
Author `/root/completion_report_impl`, distinct reviewer
`/root/completion_report_review`; COMPACT, commands180s/single60s, no network,
helpers or newfiles. Normal template work needs no new DTO bootstrap. Preserve
earlier31 evidence/budget; this finite slice cannot claim paid-API isolation.

## 31B implementation and same-reviewer correction

Author first candidate `942244ea30b17ef1d1e02d433a57f5123c5f2838` passed60tests,
but independent `/root/completion_report_review` rejected four within-contract
gaps: prefix matching accepted 功能延伸 as 功能; a filled example mixed product
changes with script-only claims; hidden/fenced/moved completion cells were absent;
and the author validator reverse-mutation evidence was missing. No new AC or PRD.

Same author additive correction `e83a4a72b848102a5eb6b82abaa3189e5245f88b` preserves
the first candidate and all findings. Before the fix, the new label-extension cell
failed with DID NOT RAISE against942244ea. Exact label boundaries now reject it.
The filled product example and separate script-only fixture are consistent;
the latter has product0/0, N/A product split and NOT_VERIFIED Host admission.
Representative comment/fence/move cells reuse the existing mutation helper.

Same independent reviewer ran65tests, focused4completion cells, then renamed the
scaffold's active 功能 label to 功能延伸. The named scaffold test failed missing
功能; exact restoration followed by65passed and clean Git status. Final blobs:
ticket template `b88a909c935ce655c423838ee55f882ec0937fee`;
scaffold `4f4d18872ebb1a57a199f9282e12c09880a909bd`;
test `8806650439b744e6d3c8a19b053f9e51c5f12e32`.

Structural review: test+117/-1 exceeds60-line signal, but reuses `_fill_ticket`,
`_SlotMutation` and active-section parsing; one script-only fixture, no new test
file/framework. Reviewer found no blocking duplication. Templates each+7;
product0. Reviewer command sum approximately58s (initial25s estimate,
correction33s measured sum); author initial16s estimate plus correction45s.
Combined conservative135/180s reserved before integration; no budget reset.

R4 recovered from the author's existing execution output, without rerun:
`python -m pytest tests/test_ticket_template_contract.py -k "completion and removed" -q`.
Removing the whole `_COMPLETION_FIELDS` lookup/assertion loop gave exit1,
14failed/51deselected in1.07s; named
`test_mutating_a_named_template_policy_breaks_its_contract_cell[completion_功能_removed]`
failed with DID NOT RAISE. Restoring the exact loop and repeating the same command
gave exit0,14passed/51deselected in0.35s. Author command-wall sum estimate62.4s
(initial16.7 + correction45.7), excluding patch/model time; combined with review
58s estimate remains below the conservative135s account above. No old evidence
is replaced by a fresh run.

Root will reuse its clean, non-reparse `.worktrees/skill-improvement-44-land`
integration workspace after the immutable44seal, rather than create another
worktree. This is a new31B lease on a Root-owned resource, not permission to
erase44 evidence or claim its cleanup succeeded. Branch remains
`codex/skill-improvement-44-land`; ff-only advance to current control baseline,
then replay only942244ea/e83a4a72 and verify exact reviewed blob parity before
the existing document mutation gate. Journal owner Root, exact temporary root
`%TEMP%/Johnny-checklist31b-20261018`, only if absent. TTL through integration,
immutable evidence seal and independent readback; policy-blocked teardown
remains blocked, never bypassed. Author/reviewer worktrees retain their own
registered identities. No push, external model call or Host activation.

Final independent verdict `/root/completion_report_review`: APPROVED exact
e83a4a72 against1aa5ed22, all four original findings closed after the R4 evidence
readback above. Root may now perform only that reviewed local integration.

### 31B local integration seal

At control baseline `0af05936fe9fa3810c5b411ef75d330649d19f28`, Root reused its
registered44-land workspace and replayed only the two reviewed31B commits.
Candidate `64157fbed9754d89fb66c473252cecbca0d525ff` has all three exact blobs
listed above. Existing `admit_document_mutation` read the committed31B boundary
from the integration branch and returned INTEGRATED at that SHA; HEAD readback
and worktree clean confirmed. Integrated template suite65passed in0.92s;
replay/integration/test commands11.44s, conservative cumulative147/180s.

Journal `%TEMP%/Johnny-checklist31b-20261018/queue/document-mutation-journal.jsonl`
has one event: at_utc2026-10-18T13:36:05.444196+00:00, candidate/detail64157fbe,
branchcodex/skill-improvement-checklist, principalGameBoy, exactTicket31 path,
outcomeINTEGRATED, offending_pathnull. SHA256
`42ee735c8a9c31a3d434c13d6d0ab7d8ebc9bee1201c890fea518760f02d784e`.
Preserve raw journal, author/reviewer worktrees and the shared Root landing
workspace. Known Host teardown prohibition is not retried by an equivalent
command; `LOCAL_INTEGRATED / CLEANUP_BLOCKED`, not normal closure. Source/test
commits and permanent tests remain protected. Fixed report format is now locally
verified; paid-API isolation and full checklist10 remain unverified.
