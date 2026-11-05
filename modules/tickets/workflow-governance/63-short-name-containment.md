# 63｜Path containment treats a Windows short-name alias as a redirect

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-6; REQ-20261103-043 implementation readiness criterion 2; ticket 59 review findings S59-04） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/63-short-name-containment-out/` / owner implementation seat / worktree `.worktrees/63-short-name-containment` / branch `cp/wave2-63-short-name-containment` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `IN_PROGRESS`（closure revision02 after the revision01 initial review CHANGES_REQUESTED on `b74840f1`: S63-01 containment bypass (blocks), S63-02 the same class already at the base, S63-07 the 39th row; correction 1 returned (`00fdc179`, CI run 42123979062 green on both jobs); revision02 initial review dispatched） |
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
