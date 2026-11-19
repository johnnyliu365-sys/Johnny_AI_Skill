# Ticket 79 — rule-only review before dispatch

Ticket: `modules/tickets/workflow-governance/79-read-only-lookup-goes-to-the-leaf.md`. Process tier: strict. A rule-only review is outside the `CodeReview.md` §5 count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.

## Revision01 (commit `bf401f26`), independent `ticket-review` seat

**verdict: CHANGES_REQUESTED**

The seat read `AGENTS.md`, `SKILL.md`, `Workflow.md` §0, the tree and context references, the command, the 2026-11-20 REQ row, and every test that reads these files. It modified nothing.

It confirmed:
- no test outside the boundary pins the changed text;
- the new text passes RETIRED_SURFACE, the reviewer patterns, the provider-literal ban and the payload closure.

Its main point was that the exemption, as written, went far wider than a read-only lookup.

| id | severity | finding | revision02 |
| --- | --- | --- | --- |
| S79R-01 | High | The new condition exempted every action that is not a change or a "writing tool": tests, gate scripts, provider calls, reading secrets. "會寫入的工具" cannot be decided. | The old condition stays, with only the lookup carved out: "除下方唯讀查詢外，…" |
| S79R-02 | High | The skill step pointed at the target project's copy of `AGENTS.md`, which P0 says does not exist and old copies lack | The step links this plugin's own `AGENTS.md#read-only-lookup` |
| S79R-03 | High | No fail-closed rule: most document kinds have no named index, and unready projects and HALT rules did not apply to a lookup | Exact file only when named. A missing or ambiguous index, a missing leaf, or a revision/digest mismatch gets the answer "not found" with the paths read, and no scan, no answer from memory, no Wayfinder. |
| S79R-04 | Medium | Rule questions were unanswerable, because the rules live in files the paragraph forbade | Rule questions use this file's 流程索引 and read only the one file that holds the rule, in the installed plugin version, naming file and version |
| S79R-05 | Medium | Ticket state could be read from an index row, another worktree or uncommitted files | The committed leaf in the current checkout decides; the answer names leaf and commit; when a receipt or the queue is needed, this is stated, not inferred |
| S79R-06 | Medium | A question could turn itself into an unrequested change, and routing questions were unclassified | Report and stop; only a user request starts the start order; "next step" and "can X be dispatched, integrated or approved" are workflow actions |
| S79R-07 | Medium | "Any document" covered secrets, production logs, outside files | The P0 sentence is in the paragraph |
| S79R-08 | Low | The test said five original steps, but there are four | "four original steps, renumbered 2 to 5" |
| S79R-09 | Low | The anchor placement was undecidable in CommonMark | Between step 5 and 「狀態只保存」, with blank lines, as with `p0-source-type` |
| S79R-10 | Low | The new description dropped maturity, staging and context minimisation | Restored |
| S79R-11 | Medium | Skipping start step 1 overrode a target project's own rules | "target project 自己的治理檔另有規定時從其規定" in both texts |
| S79R-12 | Medium | Target-project copies keep the old rule; ticket 77 could reproduce the bug | Stated in the ticket. Ticket 77 builds from 0.5.0 copies; ticket 71's README tells projects to re-copy. |
| S79R-13 | Low (note) | The boundary passes; `test_l5_stale_candidate_pin_is_named_before_generation` is already a registered base failure | No change |
| S79R-14 | Low (note) | The overlap with the reference router's index row is decided by step 1's "and stop" | No change |

## Revision02 (commit `73baf7ec`), correction rule-only review by the same seat

**verdict: CHANGES_REQUESTED**

S79R-01 to S79R-12 are CLOSED. Safety pass on the final paragraph:
- a mutation, a secret read and an unrequested change are blocked;
- a gate or test run was still possible (S79R-16).

| id | severity | finding | revision03 |
| --- | --- | --- | --- |
| S79R-15 | High | The description's "rule: answer it" has a colon and space, which breaks the YAML frontmatter (PyYAML `ScannerError`); the skill would not register. Also present in revision01 and missed there. | "rule; answer it"; TDD 2 parses the frontmatter. The control plane confirmed that the revision03 text parses. |
| S79R-16 | Medium | The exemption still allowed running a gate script, tests or another program to answer a state question | "不執行閘門腳本、測試或其他程式" |
| S79R-17 | Low | "revision／digest 不符" needs a hash computation, a program run | "索引與 leaf 記載的 revision 不符" |
| S79R-18 | Low (note) | Rule questions about the target project's own rules would always be "not found" | "本插件規則的查詢以…" |
| S79R-19 | Low (note) | The ticket stated ticket 71's README note and ticket 77's copies as facts | Reworded as control-plane follow-ups |

### Control-plane disposition

Revision03 applies only the reviewer's exact fixes, and does not go to a third rule-only round. This follows the smallest-fix practice (L-19), as with tickets 67, 73 to 76. Ticket 79 is ready for dispatch after ticket 73 is integrated.

## Seat token use

| seat | model | effort | input | cache write | cache read | output |
| --- | --- | --- | --- | --- | --- | --- |
| rule-only review, revision01 | claude-opus-5-5 | high | 36 | 116047 | 1628459 | 26040 |
| correction rule-only review, revision02 | claude-opus-5-5 | high | 14 | 34042 | 834466 | 8809 |
