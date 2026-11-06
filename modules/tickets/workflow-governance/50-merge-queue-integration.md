# 50｜Merge-queue integration script: submit, land, read back

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 integration row, R4-4 including the trust boundary, R4-7 merge-queue file and review record block, R4-8 integration script and its amendments, all as confirmed by the owner on 2026-11-05） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/50-merge-queue-integration-out/` / owner implementation seat / worktree `.worktrees/50-merge-queue-integration` / branch `cp/wave2-50-merge-queue-integration` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision02 after the revision01 initial review CHANGES_REQUESTED on `37bacce9`: S50-01 TICKET_DEFECT resolved by the owner on 2026-11-07 (merge landing, option A); implementation 2 dispatched, new review cadence） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/50-merge-queue-integration` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/50-merge-queue-integration-review` |
| 責任邊界 | the integration script, its tests and the scripts README |
| 禁止修改 | everything else, every other gate script included |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/integrate.py
create = tests/test_integrate.py
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/receipt_fence_check.py
forbid = skills/johnny-project-takeover/scripts/index_pins.py
forbid = skills/johnny-project-takeover/scripts/evidence_gate.py
forbid = skills/johnny-project-takeover/scripts/requirement_snapshot.py
forbid = skills/johnny-project-takeover/scripts/contract_gate.py
forbid = skills/johnny-project-takeover/scripts/coverage_map.py
forbid = skills/johnny-project-takeover/scripts/preflight.py
forbid = skills/johnny-project-takeover/scripts/repair_guard.py
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

The owner approved wave 2 and R4-8 on 2026-11-04 and confirmed the queue-branch, exit-column, red-before-fault and R4-4 trust-boundary corrections on 2026-11-05. Integration is a script run by whoever holds budget (R4-4); a candidate lands only when its independent review approves it, it fast-forwards the current tip, the affected specs and CI invariants rerun green in an integration clone the seats cannot write, and both remote compare-and-swaps hold at push time. After the push, the CI result is read back; a red result blocks further landings until a follow-up entry clears it.

`integrate.py <subcommand> --config <integration.json> [options]`, subcommands `submit`, `land`, `readback`. Exit codes (R4-8): `0` landed, recorded, or nothing to do; `1` an entry bounced or a precondition is red; `2` git, the remote or a configured command cannot serve the run; `3` usage.

### Configuration file (`integration.json`, path given by `--config`)

One JSON object, every value one JSON value; unknown keys, missing keys, repeated keys, `NaN`/`Infinity` and text-rule breaks are exit 3 naming the key.

| Key | Value |
| --- | --- |
| `remote` | the git remote URL or path the integration clone fetches from and pushes to |
| `branch` | the integration branch name |
| `queue_branch` | the queue branch name; default `<branch>-queue` when the key is absent |
| `queue_path` | repository-relative path of the queue file on the queue branch, canonical form (ticket 51 revision03 rule) |
| `spec_command` | argument list run in the integration clone; the affected spec paths are appended as further arguments; exit 0 green, any other exit red |
| `invariant_command` | argument list for the CI invariant classes, run in the integration clone; exit 0 green, any other exit red |
| `ci_status_command` | argument list with exactly one argument equal to `{sha}`, replaced by the landed sha; its stdout, stripped of one trailing newline, is exactly `green`, `red` or `pending`; anything else, or a non-zero exit, is a fault |
| `timeout_seconds` | positive integer bounding every configured command (default 600 when absent) |

Commands run without a shell, with argv0 resolved by the rules of ticket 55 revision03 (absolute; relative with a separator joined to the integration clone; bare names from `PATH` entries only; `.bat`/`.cmd` refused), stdin closed, bounded by `timeout_seconds`, and on timeout the process tree is killed.

### Queue file (R4-7, with the R4-8 amendments)

`{"entries": [<entry>, ...]}` on the queue branch at `queue_path`, UTF-8, LF, one entry per object with exactly the fields of R4-7: `ticket`, `candidate`, `parent`, `review`, `review_candidate`, `reviewer`, `submitter`, `state`, `landed_sha`, `reason`, `clears`. `state` is one of `QUEUED`, `LANDED_PENDING_CI`, `LANDED`, `LANDED_CI_RED`, `CLEARED`, `BOUNCED`; terminal states are `LANDED`, `LANDED_CI_RED`, `CLEARED`, `BOUNCED`. Key = (`ticket`, `candidate`). Shas are full lower-case hex of the repository's object format. A queue file that breaks this schema is exit 2 (the run cannot serve) naming the entry and field; the script never rewrites an entry it cannot parse. A missing queue file on an existing queue branch is an empty queue; a missing queue branch is created by the first `submit` (orphan commit holding only the queue file).

### Review record (R4-7)

The record at `review` is read as the blob at the current remote tip of `branch`, through the verified integration clone. The script takes the last fenced block tagged `review-verdict` whose `candidate` equals the entry's candidate; its `verdict` must be `APPROVED`, or the record must also hold a fenced `convergence-disposition` block for that candidate with `disposition: APPROVED` (CodeReview §5 rule B). `reviewer` and `submitter` match `seat:<profile>/<run-id>` (profile and run id each one or more of letters, digits, `.`, `_`, `-`), differ, and the submitter appears as `reviewer` in no `review-verdict` block of the record. A row copy that differs from the record is `BOUNCED` with `REVIEW_MISMATCH`.

### Subcommands

- `submit --ticket <id> --candidate <sha> --review <repository-relative path> --submitter <seat id> [--clears <ticket>@<sha>,...]`: verifies the record as above at the current tip, refuses an existing key (any state) with exit 1 `KEY_EXISTS`, records `parent` = the current remote tip of `branch`, and writes a `QUEUED` entry as one commit on the queue branch, pushed with `--force-with-lease` on the queue-branch sha it read. A lost lease is exit 1 `QUEUE_MOVED` and nothing is written. A refused review is exit 1 with `REVIEW_MISMATCH` and nothing is written.
- `land`: blocked (exit 1 `BLOCKED_BY_CI`, nothing pushed) while any entry is `LANDED_PENDING_CI`, or any is `LANDED_CI_RED` and no `QUEUED` entry's `clears` lists every red key. Otherwise it takes the oldest admissible `QUEUED` entry (the oldest entry whose `clears` lists every red key while a red block holds) and, in a fresh integration clone fetched with `transfer.fsckObjects=true` and `fetch.fsckObjects=true` (R4-4), checks that the candidate is present and the current tip is its ancestor (else `BOUNCED NOT_FAST_FORWARD`), re-reads the review record at that tip (else `BOUNCED REVIEW_MISMATCH`), computes the affected specs (R4-7: every spec whose file, or whose `pages.json` entry, names a path the candidate changed; without `pages.json`, from file paths alone), runs `spec_command` with them and `invariant_command` on the fast-forwarded tree (red: `BOUNCED SPEC_RED` or `INVARIANT_RED`), then pushes the candidate to `branch` and the queue commit recording `LANDED_PENDING_CI` with `landed_sha` to `queue_branch` in one `git push --atomic` with `--force-with-lease` on each sha it read. A lost lease on the tip is `BOUNCED TIP_MOVED`, on the queue `QUEUE_MOVED` (no state change is pushed for a lost queue lease; the next run re-reads). A bounce is written to the queue branch and exits 1. One entry per run.
- `readback`: for every `LANDED_PENDING_CI` entry runs `ci_status_command`; `green` moves it to `LANDED` and every entry its `clears` names from `LANDED_CI_RED` to `CLEARED`; `red` moves it to `LANDED_CI_RED`; `pending` leaves it. All changes are one queue commit pushed with a lease. Exit 0 when the queue was read and every status was served, even if some stay pending.

### Rules every wave-2 gate follows (binding here)

- Red before fault: a run reports every red it can find and exits 1 if there is one, with each fault on stderr on one line; it exits 2 only when it found no red. A fault that leaves nothing to check (an unreadable config, the remote unreachable) ends the run at once.
- Text values: every string read from an input (config, queue file, review record, arguments, command output) is valid Unicode without lone surrogates or control characters (U+0000–U+001F, U+007F); in a file it is the red or fault the table above names, in an argument exit 3. Every printed subject is escaped to one line on stdout and stderr; an unwritable stdout or stderr is exit 2.
- Git environment: every git child runs with `--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_GRAFT_FILE` pointing at a fresh path that does not exist, `-c core.commitGraph=false`, and with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_SHALLOW_FILE`, `GIT_REPLACE_REF_BASE` and every `GIT_CONFIG*` variable removed; `git` is resolved from absolute `PATH` entries only.
- JSON: repeated keys, `NaN`, `Infinity`, a BOM-less non-UTF-8 byte and nesting too deep to parse are input errors of that file, never an unexpected exception.
- The integration clone is created fresh for each `land` under a temporary directory and removed afterwards, also on failure; no run reads objects from a store a seat can write.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/50-merge-queue-integration`.
- reviewer：`ticket-review` seat in `.worktrees/50-merge-queue-integration-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-2, R4-4, R4-7, R4-8, CodeReview §5.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/integrate.py`
- 公開契約／資料模型：typed dataclasses `Config`, `QueueEntry`, `ReviewVerdict`, `Bounce`; the states, bounce reasons and exit codes above; stdlib only.

## TDD 設計

Tests build a bare repository as the remote (a local path) and real clones in temporary directories; the configured commands are small Python scripts written by the test.

1. 正常行為：submit an approved candidate, land it (fast-forward, specs and invariants green, atomic push), read back `green` → `LANDED`; a convergence-disposition record lands like an `APPROVED` one; nothing queued → exit 0.
2. 規則違反／輸入錯誤：every bounce reason in its own test (`REVIEW_MISMATCH` for a missing block, a wrong verdict, a candidate mismatch, a row copy differing from the record, submitter = reviewer, submitter appearing as reviewer; `KEY_EXISTS` for each terminal and non-terminal state; `NOT_FAST_FORWARD`; `SPEC_RED`; `INVARIANT_RED`; `TIP_MOVED` and `QUEUE_MOVED` with a racing push injected between read and push); `BLOCKED_BY_CI` for a pending and for a red entry; a clearing entry lands while a red block holds and its green readback moves the red entries to `CLEARED`; every config error is exit 3.
3. 外部失敗／fail-closed：remote unreachable, `git` missing, a configured command missing, timing out (its tree killed) or answering outside its format → exit 2 with the cause; a corrupt queue file → exit 2 and nothing rewritten; a forged object injected into the remote's store (loose object whose content does not match its id) makes the fsck clone fail → exit 2, nothing pushed.
4. 回歸保護：a queue write never moves the integration tip; one `land` lands at most one entry; the atomic push leaves both branches unchanged when one lease fails; a replace ref, a graft file, a commit-graph and inherited `GIT_*` variables in the environment change nothing; an affected spec listed through `pages.json` is passed to `spec_command`; a review record read from the candidate branch instead of the tip is not accepted; every printed subject holding a newline or U+2028 prints on one line.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `review` and `queue_path` canonical form (backslash, `..`, `./`, leading `/`, drive letter, empty, trailing `/`); affected-spec match on path segments, not prefixes (`specs2/` versus `specs/`) |
| 2 | null／空字串／陣列 | 是 | empty and missing config keys, empty argument lists, an empty queue, an empty `clears`, a record with no block |
| 3 | 權限繞過 | 是 | a candidate landing without its own approved record (direct); a submitter approving itself, or a record read from a seat-writable store or from the candidate branch (indirect) |
| 4 | Token 格式與比較 | 是 | shas compared in full, case-sensitively, at the repository's id width; seat ids by the exact format; a verdict compared exactly |
| 5 | 錯誤碼是否一致 | 是 | each bounce reason distinct; red before fault; a bounce is 1, a fault 2, usage 3 |
| 6 | 例外是否會拋出 | 是 | every git, file and command failure caught → exit 2 with one line; no traceback |

## 完成定義與證據

- `python -m pytest tests/test_integrate.py -q` exit 0; `mypy --strict --python-version 3.11` on the script exit 0; stdlib only; no `Any`; no `type: ignore`.
- **反向突變證據**：for each bounce reason and each rule above remove its check → its test red → restore; plus: queue written to the integration branch (red), non-atomic two pushes (red), lease dropped (red), clone without fsck (red), review read at the candidate (red), git environment not scrubbed (red), a fault dropping an earlier red (red). An equivalent survivor stays in the M1 capture, marked, with its reason.
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and `integrate.py`; every cell runs at the committed candidate and each capture starts with the sha256 of the script it ran; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script; it writes only to the remote named in the target project's own configuration.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (after the revision01 initial review `CHANGES_REQUESTED` and the owner decision of 2026-11-07)

Review record section "Revision01 initial review".

S50-01 is a `TICKET_DEFECT`. The record is read at the tip, and the candidate had to fast-forward that tip, so nothing could ever land. The owner decided "1.A" on 2026-11-07: a candidate lands as a merge commit into the current tip. Spec R4-2, R4-4, R4-7 and R4-8 now say so (signature row 2026-11-07). In this ticket, revision02 replaces every statement about fast-forwarding:

- `land`, in a fresh verified integration clone, does these steps in order:
  1. Re-reads the review record at the current tip. If the record does not admit the entry, the entry is `BOUNCED REVIEW_MISMATCH`, and no configured command runs.
  2. Checks that the candidate is not already contained in the tip. If it is, the entry is `BOUNCED ALREADY_LANDED`.
  3. Makes one merge commit, with the tip as first parent and the candidate as second. A conflict is `BOUNCED MERGE_CONFLICT`, and nothing runs.
  4. Runs `spec_command` with the affected specs, then `invariant_command`, on the merged tree.
  5. Pushes the merge commit to `branch` and the queue commit to `queue_branch` in one `git push --atomic`, with a lease on each sha it read. `landed_sha` is the merge commit.
- `NOT_FAST_FORWARD` is gone from the bounce reasons, and `MERGE_CONFLICT` and `ALREADY_LANDED` join them.
- `submit` still records `parent` as the tip it read. A later tip is not a bounce reason.

| Finding | Class | Work in implementation 2 |
| --- | --- | --- |
| S50-01 | TICKET_DEFECT | the merge landing above; a successful-land test against real git with no patch of `Integrator._record`: the record is committed on the tip, the candidate is a sibling of it, `land` lands a merge commit, readback marks `LANDED` |
| S50-02 | IMPLEMENTATION_DEFECT (safety) | no configured command runs on a candidate that the record does not admit, or that conflicts; the reviewer's `unapproved` probe is a test whose marker file is never written |
| S50-03 | EVIDENCE_DEFECT | a land test with the approving record only on a seat branch that descends from the candidate: `REVIEW_MISMATCH`, tip unchanged; the reviewer's CM-A3 turns it red |
| S50-04 | IMPLEMENTATION_DEFECT | NaN, Infinity, control-character and lone-surrogate errors in the config name the key; tests pin each |
| S50-05 | EVIDENCE_DEFECT | M1 is rerun one pytest at a time with `-rfE`, failing names kept; a mutation whose run crashed is rerun, never counted red |
| S50-06 | IMPLEMENTATION_DEFECT | `pages.json` is read with `utf-8-sig`, so a BOM is not a red |
| S50-07 | OUT_OF_SCOPE_HARDENING, closed here | git children run with `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL` set to a path that does not exist, so a global config cannot weaken the verified fetch |
| S50-08 | OUT_OF_SCOPE_HARDENING, closed here | the fetch takes only `branch`, `queue_branch` and the candidates of queued entries |
| S50-09 | OUT_OF_SCOPE_HARDENING, closed here | `mypy --strict` on the test file exit 0 |
| S58-04, S60-01 | routed from tickets 58 and 60 | the removed-variable list is the shared one: the thirteen names of `evidence_gate.py`, every `GIT_CONFIG*` name and every `GIT_TEST_*` name |
| S57-05 | routed from ticket 57, carried | the template's configuration cross-check needs both the template (ticket 57) and `integrate.py` on one tree. This ticket's branch starts before ticket 57, so the cross-check is pinned after integration, in the first change that touches either |

The work is additive commits on `37bacce9`. The next review is the revision02 initial review.
