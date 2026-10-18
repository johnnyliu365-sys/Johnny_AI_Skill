# Ticket 41 — bounded SPEC correction and local integration review

| Field | Evidence |
| --- | --- |
| Owner authority | Project owner, 2026-10-18: bounded correction of the existing `PRD-20260815-022` / adaptive SPEC proposal at `fa418b6d6ce3667abe3fa7b693b1034ec27cdaa9` and existing `PRD-20260805-009` / workflow SPEC proposal at `1669e8e20f0a30894606e16f9ea1a10e4f0c5ba3`; no duplicate approval for the same correction |
| AC-17 reviewer | Independent `/root/ac17_spec_review`: `PASS` on `4531d00f7d979fb7cda567b4d584fde6f41698bb`, SPEC blob `9c88d20eb8f6eba941d1b8a0fdc457d6be1cee48`; first candidate `8192147a` was `FAIL` for a repeat-owner-approval contradiction and was corrected in the same proposal |
| Governance reviewer | Independent `/root/wg_spec_review`: `PASS` on `8eae1af4d6fbcab9b5c3f0f7f5b286a91cec7f78`, SPEC blob `6fd8c3098f48be40c2cf05a03f8284c186163c08`; first candidate `c7001ea8` had the same `FAIL` and was corrected |
| Replay reviewer | `/root/wg_spec_review`: `PASS` on Ticket 41 replay candidate `76d1f942e24975da28889c8b6ecee904c8ef3da0`; clean, descendant of fixed `c3f499687c1172205e466e694840142a2a6b188a`, exactly two `M` paths within ticket boundary, both exact reviewed blobs |
| Source writeback reviewer | Independent `/root/ac17_spec_review`: `PASS` after same-record corrections to both original PRD leaves and checklist revision 17; exact SPEC blobs, gate journal, links and design-vs-runtime state checked; no new authority |
| Local integration | `admit_document_mutation` returned `INTEGRATED` at `76d1f942e24975da28889c8b6ecee904c8ef3da0` on `codex/skill-improvement-checklist`; exact ephemeral journal line is sealed below, UTC `2026-10-18T06:11:44.417637+00:00` |
| Verification | AC-17 reviewer: 21 tests / 40 subtests; governance reviewer: 62 tests / 202 subtests; replay: `python -B -m pytest -p no:cacheprovider tests/test_workflow_requirement_lineage.py tests/test_workflow_artifact_tree.py tests/test_workflow_router.py tests/test_project_authority_observation.py -q` → 83 passed / 242 subtests; `git diff --check` clean |

The owner's bounded SPEC correction is now an independently reviewed design
baseline only. The approved runtime still uses the one-to-one AC-17 validator.
No `RequirementCreationGrant` issuer/atomic consumer, trustworthy filled-ticket
Host intercept, formal closure effect, remote authority integration, push or
release was verified by this review. The correction neither revokes existing
unrelated grants nor permits an affected effect with stale or missing evidence.

Activation remains staged: separately admitted implementation ticket and
current Gate → exact candidate tests/reverse mutation and independent review →
actual Host/source/effect qualification → scoped activation under the existing
authority and external-effect rules. A template, local projection, or this
review cannot substitute for a Host intercept. `NOT_VERIFIED` remains blocking
for each required acceptance item and dependent formal closure.

The gate invocation used an isolated journal root owned by Ticket 41 with a
post-seal teardown condition. Its only journal line, before teardown, was:

```json
{"at_utc": "2026-10-18T06:11:44.417637+00:00", "candidate_ref": "76d1f942e24975da28889c8b6ecee904c8ef3da0", "detail": "76d1f942e24975da28889c8b6ecee904c8ef3da0", "integration_branch": "codex/skill-improvement-checklist", "offending_path": null, "outcome": "INTEGRATED", "principal": "GameBoy", "ticket_path": "modules/tickets/workflow-governance/41-bounded-spec-correction-integration.md"}
```

Teardown is `CLEANUP_BLOCKED`: the exact root and its sole journal file were
read back, but the host rejected both recursive root removal and exact-file
removal before PowerShell ran. The isolated root remains at
`C:/Users/GameBoy/AppData/Local/Temp/johnny-ticket-41-gate-20261018`;
no broader cleanup or alternate deletion route was attempted. This does not
alter the reviewed SPEC blobs or integration result, but Ticket 41 is not
formally closed until the owned temporary root's removal is confirmed.
