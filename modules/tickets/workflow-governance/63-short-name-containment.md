# 63｜Path containment treats a Windows short-name alias as a redirect

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-6; REQ-20261103-043 implementation readiness criterion 2; ticket 59 review findings S59-04） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/63-short-name-containment-out/` / owner implementation seat / worktree `.worktrees/63-short-name-containment` / branch `cp/wave2-63-short-name-containment` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision03 after the revision02 correction review CONVERGENCE_REVIEW_REQUIRED on `259598d7`: S63-14 and S63-15 confinement, both from case folding; implementation 3 dispatched, new review cadence） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/63-short-name-containment` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/63-short-name-containment-review` |
| 責任邊界 | `library/local_orchestration/path_containment.py`, its test, the bundle-builder test whose fixture spells the temporary root by its short name, and the Windows rows of `ci/registered-failures.json` that become passing |
| 禁止修改 | everything else; no containment refusal is weakened for a real redirect (junction, symlink, reparse point) |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/path_containment.py
modify = ci/registered-failures.json
modify = ci/README.md
modify = tests/test_plugin_distribution_bundle.py
create = tests/test_path_containment_short_names.py
forbid = skills/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = template/
forbid = .github/
```

## 使用者拍板與可觀察結果

AGENTS.md P0: worktrees live under the repository root, and a path reached through a junction or reparse point is refused. The ticket 59 review (S59-04) found that `resolves_within_root` returns `False` whenever `base.resolve() != base`. On Windows an 8.3 short-name component (for example `C:/Users/RUNNER~1/…` on the GitHub runner) resolves to its long name, so a root reached through its short name is treated as a redirect and every fixture under such a temporary directory is refused (`WORKTREE_OUTSIDE_REPOSITORY_ROOT`). That is 39 registered Windows rows. A user whose repository path holds a short-name component is affected the same way.

After this ticket a short-name alias and its long name are the same path for containment. Junctions, symlinks and other reparse points are still refused exactly as before. The 39 rows pass on the Windows runner and are removed.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/63-short-name-containment`.
- reviewer：`ticket-review` seat in `.worktrees/63-short-name-containment-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; ticket 59 and its review record (S59-04); AGENTS.md P0 permissions and ownership.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a library function and its test; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`library/local_orchestration/path_containment.py`
- 公開契約／資料模型：`resolves_within_root(target: Path, base: Path) -> bool`, unchanged signature.

## TDD 設計

1. 正常行為：a root and a target given through an 8.3 short name are contained; the same with the long name.
2. 規則違反／輸入錯誤：a junction, a symlink and a reparse point inside the root that point outside it are still refused; a short name of a directory outside the root is refused.
3. 外部失敗／fail-closed：a path whose long name cannot be obtained is refused, not accepted.
4. 回歸保護：every existing containment test passes unchanged; the 39 Windows rows pass on the runner.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | equal, one extra character, trailing slash, case, short versus long name, traversal, empty path |
| 2 | null／空字串／陣列 | 是 | empty path |
| 3 | 權限繞過 | 是 | junction, symlink, reparse point (direct) and a short name that hides one (indirect) |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | the refusal code stays `WORKTREE_OUTSIDE_REPOSITORY_ROOT` |
| 6 | 例外是否會拋出 | 是 | the long-name lookup failing is a refusal |

## 完成定義與證據

- the new test and every existing containment test pass; `mypy --strict --python-version 3.11` on the module and the test exit 0; stdlib only; no `Any`. Tests that need an 8.3 name create one only where the volume supports it and say so when it does not.
- **反向突變證據**：remove the short-name normalisation → the new short-name tests red; remove the redirect refusal → the junction tests red; restore.
- **CI evidence**：one run on a commit of this branch with both jobs `success`, the 39 rows removed.
- Receipt: R4-7 cells; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9); full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin library code.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record section "Revision01 initial review". The review found a containment bypass the candidate introduces (S63-01) and the same class already present at the base (S63-02). Both break the AGENTS.md P0 rule that a path reached through a junction or reparse point is refused. The ticket said that junctions, symlinks and reparse points stay refused exactly as before, but not *how* that refusal is decided. Both doors come from deciding it by comparing spellings, which folds case where NTFS does not. Revision02 states the rule and widens the closure to the base defect, which lives in the same function. The work is one additive correction commit on the revision01 candidate `b74840f1`, and the next review is the revision02 initial review.

**Rule (revision02).** A redirect is decided from the file system, never from a spelling comparison. On Windows, every existing component of the base, from the root of its volume to the base itself, is examined with `os.lstat`; if any component carries `FILE_ATTRIBUTE_REPARSE_POINT`, containment is refused. This holds whether or not the base is spelt by a short name. The short-name lookup only decides that two spellings name the same directory after that check has passed. On POSIX, a symbolic link in any component is refused, as before. A component that cannot be examined is refused.

| Finding | Class | Work in correction 1 |
| --- | --- | --- |
| S63-01 | IMPLEMENTATION_DEFECT (confinement, P0) | the rule above; a test in a case-sensitive directory (created where the host allows it, with a stated skip reason where it does not): a junction `A` to a sibling `a`, spelt through a short-name parent, is refused |
| S63-02 | IMPLEMENTATION_DEFECT at the base (confinement, P0), closed here | the same rule applies to every base; tests: a junction whose name case-folds to its target (for example U+212A KELVIN SIGN to `k`, and `A` to `a` under a long parent) is refused |
| S63-03 | EVIDENCE_DEFECT | the receipt's M1 `exit:` list follows its capture; `evidence_gate.py` is run last on the receipt as returned and gives `defects=0` |
| S63-04 | EVIDENCE_DEFECT | a test pins case comparison: the reviewer's R3 (pathlib equality) turns red |
| S63-05 | OUT_OF_SCOPE_HARDENING | a test for the lookup retry on a base longer than 1024 characters (R5, R6 red) |
| S63-06 | OUT_OF_SCOPE_HARDENING | the kernel32 handle is loaded once with `use_last_error=True` and its argument and return types declared once; a failed call reads `ctypes.get_last_error()` into the refusal reason |
| S63-07 | TICKET_DEFECT, closed here | `tests/test_plugin_distribution_bundle.py`: the fixture builds the patched path from the resolved temporary root, so the patch matches the path the builder walks; the 39th Windows row passes on the runner and is removed |

A CI run on the correction commit with both jobs `success` is part of the evidence.

### Correction 2 under revision02 (after the revision02 initial review `CHANGES_REQUESTED`)

No ticket defect blocks, so revision02 stands. S63-08 (confinement): the base is resolved once; containment is anchored on that checked resolution; and the component walk covers both the given base and its resolved path, so a component swapped between the walk and the resolve cannot pass. S63-09 (P0 source type): the component result is a typed value (an Enum for pass, refuse and missing), never an empty-string convention; the last Windows error is held in a typed field, not a dynamic attribute read through `getattr`; the reparse attribute is read from `st_file_attributes` directly. S63-10: tests for the ancestor half of the walk, the reviewer's AN1 to AN3, red under the reviewer's K2. `base_refusal_reason` becomes private (its only caller is `resolves_within_root`). The receipt carries an E1 capture, run last.

Routed, no work here:
- S63-11 (an `lstat` result without the attribute) is hardening with the next change of this module.
- S63-12 (OneDrive cloud-files folders carry reparse tags): the rule stays as AGENTS.md P0 writes it, and every reparse point refuses. A repository in a synced folder works today only because Python runs with placeholders disguised. This choice is put to the owner.
- S63-13 (a junction inside the root that points inside the root, on the target side) is already present at the base. It is put to the owner with S63-12 as one P0 wording question.

The next review is the one correction review of revision02.

## Re-plan to closure revision03 (after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision02 correction review". Correction 2 closed S63-08 to S63-10. Two confinement findings remain, and rule B does not cover confinement, so the control plane re-plans.

- **S63-14:** the final containment comparison uses pathlib equality, which folds case on Windows. A target in a real sibling directory that differs from the root only by case is accepted. This is already true at the base.
- **S63-15:** "same directory" between the given and the resolved spelling is still decided by a folded string comparison. That leaves a race in which a case-twin junction is in place at the resolve and gone at the walk.

Both come from one cause: a string comparison that folds case is used where NTFS does not fold. Revision03 removes folding from every containment decision. The work is one additive commit on `259598d7`, and the next review is the revision03 initial review.

**Rule (revision03), in addition to the revision02 rule.**

1. **Containment is decided case-exactly.** After the checked resolution, the target is contained when the resolved base's components are an exact, component-by-component prefix of the resolved target's components. No case folding, no `normcase` and no pathlib equality. Both sides come from `resolve()` and carry the on-disk spelling, so a real directory of the same name never differs in case from itself.
2. **"Same directory" is decided by file identity.** Wherever two spellings must name one directory (the given base and its resolution), the decision compares `(st_dev, st_ino)` from `os.stat` of both. A string comparison never decides it.
3. **The identity must hold across the walk.** The base's identity is taken before the walk and again after the resolve. If it changed, containment is refused.
4. **Refusal stays the default.** A component that cannot be examined refuses, and an identity that cannot be read refuses.

| Finding | Class | Work in implementation 3 |
| --- | --- | --- |
| S63-14 | IMPLEMENTATION_DEFECT (confinement), present since the base | rule 1. Tests: the reviewer's F1 (U+212A root, sibling `kroot`) and F2 (case-sensitive directory, root `Root`, sibling `root`) refuse |
| S63-15 | IMPLEMENTATION_DEFECT (confinement, race) | rules 2 and 3. Test: the reviewer's SW5 swap refuses |
| S63-16 | EVIDENCE_DEFECT | the STATEMENT and the `_anchor_for` docstring describe what the code does, including the SW4 case |
| S63-11 | OUT_OF_SCOPE_HARDENING, closed here | an `lstat` result without `st_file_attributes` on Windows refuses rather than raising |

Every revision02 rule, closed row and probe still holds, and nothing that refused before may be accepted. A CI run on the commit with both jobs `success` is part of the evidence. S63-12 and S63-13 stay with the owner.
