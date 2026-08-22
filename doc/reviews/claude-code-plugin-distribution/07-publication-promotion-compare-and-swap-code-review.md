# Ticket 07 code review — publication promotion CAS contract

| Field | Value |
| --- | --- |
| Ticket / closure | `claude-code-plugin-distribution/07-publication-promotion-compare-and-swap` / `CLOSURE_01` |
| Reviewer profile | Terra / `xhigh` |
| Baseline / candidate | `b7ffaba` / `9ffedeb` plus sole correction `2ca8743` |
| Verdict | `CHANGES_REQUESTED / EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED` |
| Integration / external effect | None. No marketplace repin, publication ref, remote, repository, CLI or credential action occurred. |

## Evidence

The candidate boundary contains only `library/local_orchestration/publication_promotion.py` and `tests/test_publication_promotion.py`. Fresh-clone checks passed: promotion `8 passed`; ticket 06 closure plus payload `53 passed, 296 subtests passed`; `mypy --strict` across six direct paths; `compileall`; manifest JSON parsing; and `git diff --check`.

The reviewer independently changed a plan's expected-old SHA and tag target after planning. Both changed `VERIFIED` to named `READBACK_MISMATCH` rejections, and exact restoration returned `VERIFIED`. Static review found no production process, Git, credential, hard-coded GitHub endpoint or external-effect call.

## Blocking evidence defect

P5 freezes direct proof for malformed version/ref plus null and missing-field snapshots as well as bypass-built DTOs. The submitted test covers only a bypass-built partial SHA and malformed plan. A reviewer probe confirms the runtime returns finite refusals for the omitted four inputs, but that probe is not a durable TDD regression. The first correction instead repaired P4; no further automatic correction is permitted in `CLOSURE_01`.

## Required continuation

The control plane refreezes the identical contract as `CLOSURE_02`. It retains the unintegrated candidate evidence, permits only the four omitted P5 direct tests unless a test reveals a finite-result defect, and requires a fresh Terra review. No requirement, topology, model profile or external-effect authority changed.

## CLOSURE 02 review

| Field | Value |
| --- | --- |
| Ticket / closure | `claude-code-plugin-distribution/07-publication-promotion-compare-and-swap` / `CLOSURE_02` |
| Reviewer profile | Terra / `xhigh` |
| Baseline / source candidate | `fd23dc0817034831c3211bc86fa72fab17b451df` / `659bac61e73f03ccadf5ec60033bf944f4516578` |
| Reviewer-generated candidate | `4a77414e017131c1fda581250c38dd3d0a86e4e2` |
| Verdict | `APPROVED` |
| Integration | `admit_document_mutation` returned `INTEGRATED` with `integrated_commit = 4a77414e017131c1fda581250c38dd3d0a86e4e2`. |

The CLOSURE_02 source diff is limited to the two declared creation paths. Its additive correction
adds direct P5 regression cases for a malformed version, malformed ref, null snapshot and
snapshot missing `repository`; each is finite and planless. A fresh clone at `659bac6` passed
promotion `12 passed`; ticket-06 closure plus payload checks `53 passed, 296 subtests passed`;
strict mypy across six direct paths; `compileall`; manifest parsing; and `git diff --check`.

The reviewer independently created a valid update plan, mutated its expected-old `main` SHA, and
observed `VERIFIED -> READBACK_MISMATCH -> VERIFIED` after exact restoration. The new module
contains no production process, Git, credential, hard-coded GitHub endpoint or external-effect
call. This closes the CLOSURE_01 evidence defect without changing the frozen contract.

Only after source approval, the reviewer regenerated the permitted marketplace pin in the
candidate worktree. The generator created local-only anchor `refs/heads/publication-0.4.9` at
`b16151cb977ffaf610e06b7ec626ccbec52634b5`, wrote that generated value to the marketplace
manifest, and its `--verify-only` readback passed. The full publication suite then passed
`53 passed, 286 subtests passed`. No remote, repository, real tag, Claude CLI, credential or
other external effect occurred.
