# 59｜Wave-2 acceptance (2): CI green on Linux and Windows apart from registered failures

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-6; REQ-20261103-043 implementation readiness criterion 2） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/59-ci-linux-windows-out/` / owner implementation seat / worktree `.worktrees/59-ci-linux-windows` / branch `cp/wave2-59-ci-linux-windows` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11 for the checker and its test（CONTEXT.md Implementation language）; YAML for the workflow |
| 狀態 | `IN_PROGRESS`（closure revision02 after the revision01 initial review CHANGES_REQUESTED on `3ab5ac43`: S59-01 P0, S59-08 TICKET_DEFECT; correction 1 returned (`e067b81b`, CI run 42084063480 green on both jobs); revision02 initial review dispatched） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/59-ci-linux-windows` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/59-ci-linux-windows-review` |
| 責任邊界 | the CI workflow, the registered-failure list, its checker and the checker's test |
| 禁止修改 | everything else; no test is skipped, deleted or weakened to make CI green |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
create = .github/workflows/ci.yml
create = ci/registered-failures.json
create = ci/check_registered_failures.py
create = ci/README.md
create = tests/test_ci_registered_failures.py
forbid = skills/
forbid = library/
forbid = modules/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = template/
forbid = requirements-dev.txt
forbid = requirements-runtime.lock
```

## 使用者拍板與可觀察結果

The owner made implementation readiness criterion 2 part of wave-2 acceptance on 2026-11-03: "CI is green on Linux and Windows apart from registered environment failures, each listed by name." After this ticket every push to the plugin repository runs the whole test suite on Linux and on Windows; a job is green only when every failing test is registered for that operating system with a reason, and every registered failure still fails.

### Workflow (`.github/workflows/ci.yml`)

- Triggers: `push` to any branch and `pull_request`; one job per operating system in a matrix of `ubuntu-latest` and `windows-latest`; Python 3.11; `actions/checkout` with `fetch-depth: 0` (several tests read history and tags); the git identity set to a neutral CI identity for tests that commit; `PYTHONUTF8=1`.
- Steps: `pip install -r requirements-dev.txt`; `python -m pytest tests -q -p no:cacheprovider -rf --continue-on-collection-errors --junitxml=<file>` (revision02: a module that fails to import is a collection error the checker reports by its file, so one such module cannot stop the rest of the run); then `python ci/check_registered_failures.py --os <linux|windows> --junit <file>`, whose exit is the job's result (the pytest exit itself is not the job's result).
- Third-party actions are pinned to a full commit sha with the version in a comment; no secret is read; the token permission is `contents: read`.

### Registered failures (`ci/registered-failures.json`)

`{"linux": [<row>, ...], "windows": [<row>, ...]}`, each row `{"test": "<pytest node id>", "reason": "<why it fails in this environment>", "follow_up": "<ticket path or 'environment'>"}`. Both lists are filled from the CI runs; the host's base names (the eight that fail on every full run here) are the starting point for Windows, and each difference between the host and the CI runner is named in `ci/README.md`. A reason names the cause (for example a pin to a commit not in the repository, a platform capability the runner lacks), never "flaky".

### Checker (`ci/check_registered_failures.py`)

Exit 0 when the junit report's failed and errored test ids for `--os` equal the registered set for that operating system; exit 1 with one line per unexpected failure (`UNREGISTERED_FAILURE <id>`) and per registered test that passed (`REGISTERED_NOW_PASSING <id>`, so the list never goes stale); exit 2 when the report or the list cannot be read or does not follow its schema; exit 3 on bad arguments. Skipped tests are neither failures nor passes. Every printed subject is escaped to one line.

### Evidence of green

The seat pushes its own ticket branch `cp/wave2-59-ci-linux-windows` (and no other branch) to `origin` to run the workflow, reads the runs with `gh run list` and `gh run view --log-failed`, registers the Linux failures with their reasons, and repeats until both jobs are green on one commit. The receipt records the run id, its URL, the commit sha and both job conclusions, with `gh run view <id> --json jobs` saved as a capture.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/59-ci-linux-windows`.
- reviewer：`ticket-review` seat in `.worktrees/59-ci-linux-windows-review`.
- **Owner override record**：the owner said "推" and "繼續處理wave2" on 2026-11-05; pushing this ticket's own branch to run CI is within that.
- `ImplementationHandoff`：this ticket, R4-6, REQ-20261103-043 readiness criterion 2.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：CI configuration and a command-line checker; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the five paths in the boundary block
- 公開契約／資料模型：the registered-failure schema and the checker's codes above.

## TDD 設計

1. 正常行為：a junit report whose failures equal the registered set → exit 0; an empty report and an empty list → exit 0.
2. 規則違反／輸入錯誤：an unregistered failure → `UNREGISTERED_FAILURE`; a registered test that passed → `REGISTERED_NOW_PASSING`; an error (not a failure) counts as a failure; a row without a reason, an empty reason, a repeated test id, an unknown operating system key → exit 2.
3. 外部失敗／fail-closed：a missing or malformed junit file → exit 2; a list that is not JSON → exit 2.
4. 回歸保護：the real `ci/registered-failures.json` parses and every row has a non-empty reason and follow-up. Both lists come from CI runs; where the Windows CI list differs from this host's base names, `ci/README.md` names each difference and its cause.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | test ids compared exactly: a parametrised id, a class-qualified id, an id that is a prefix of another |
| 2 | null／空字串／陣列 | 是 | empty reason, empty lists, a report with no test cases |
| 3 | 權限繞過 | 是 | the workflow's token is read-only; no step reads a secret |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | 1 for a mismatch, 2 for an unreadable input, 3 for usage |
| 6 | 例外是否會拋出 | 是 | malformed XML and JSON caught → exit 2 with one line |

## 完成定義與證據

- `python -m pytest tests/test_ci_registered_failures.py -q` exit 0; `mypy --strict --python-version 3.11` on the checker exit 0; stdlib only.
- **反向突變證據**：drop the now-passing check, treat errors as passes, accept a row without a reason, compare ids by prefix: each → a named test red → restore.
- **CI evidence**：one GitHub Actions run on a commit of this branch with both jobs `success`; run id, URL and the jobs JSON captured in the receipt.
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts at the commit; every cell runs at the committed candidate; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- local full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- The workflow runs on the plugin repository only; it deploys nothing and reads no secret.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record section "Revision01 initial review". S59-08 is a `TICKET_DEFECT`: the frozen pytest command lacked `--continue-on-collection-errors`, which the seat added with cause; the command above now holds it. This is a closure rebuild: the work is one additive correction commit on the revision01 candidate `3ab5ac43`, and the next review is the revision02 initial review.

| Finding | Class | Work in correction 1 |
| --- | --- | --- |
| S59-01 | IMPLEMENTATION_DEFECT (P0: source type) | no `Any` in the test file (`object`, `dict[str, object]`); `mypy --strict` on the test file exit 0. AGENTS.md P0 covers every formal source file, tests included |
| S59-02 | IMPLEMENTATION_DEFECT | the acr2 and acr3 rows name the real cause (the test's label validator refuses `linux-fs:ext2/ext3`) and `follow_up` = `modules/tickets/workflow-governance/62-registered-known-failures.md` |
| S59-03 | IMPLEMENTATION_DEFECT | the file-lock row names the real cause (closed stdin then `communicate()` on POSIX) and `follow_up` = ticket 62 |
| S59-04 | TICKET_DEFECT, routed | the 39 Windows 8.3 rows name the cause (`resolves_within_root` treats a short-name alias as a redirect) and `follow_up` = `modules/tickets/workflow-governance/63-short-name-containment.md` |
| S59-05 | TICKET_DEFECT, routed | the seven rows per OS that named this ticket name ticket 62 instead |
| S59-06 | EVIDENCE_DEFECT | pin that the checker step's exit is the job's result: the checker line ends at the junit argument, no `continue-on-error`, no `||` or `;` after the checker |
| S59-07 | EVIDENCE_DEFECT | pin the permissions block to exactly `contents: read` and refuse `github.token` and `secrets.` anywhere in the workflow |
| S59-11 | EVIDENCE_DEFECT | `ci/README.md`: a cause for every host-only failure, those four described as base-capture failures not seen at the candidate, and the Linux paragraph corrected by S59-02 and S59-03 |

A CI run on the correction commit with both jobs `success` is part of the evidence. Carried, no work here: S59-09 (DOCTYPE refusal for non-UTF-8 reports) and S59-10 (id normalisation, `follow_up` domain, duplicate JSON keys, subtests inside a registered test) are out-of-scope hardening for a later change of this gate.
