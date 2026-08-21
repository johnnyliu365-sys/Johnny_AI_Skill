# 實機功能驗證 047｜P6：三隻腳合起來走一遍的紀錄

本文件是 [`modules/tickets/workstation-dispatch/p6-live-functional-verification.md`](../../modules/tickets/workstation-dispatch/p6-live-functional-verification.md)
的交付物——三段驗證（失敗演練＋重派、完整往返、commit 觸發）在**真安裝的 JohnnyRouter
store** 上的逐行紀錄，不是測試暫存。第一段已經真的發生；第二、三段的欄位先立好，
狀態如實標記，內容由控制面完成後回填。

## 一、資料來源

本次擷取讀了三份 store 檔案，全部只讀，沒有寫入：

| 檔案 | 角色 |
| --- | --- |
| `C:\Users\User\AppData\Local\JohnnyRouter\queue\dispatch-journal.jsonl` | 第一手來源（票的「第一步排查起點」指定的檔案）；receipt 層級的派工事件序列 |
| `C:\Users\User\AppData\Local\JohnnyRouter\queue\worker-assignments-v1.json` | 交叉佐證；每個 claim 目前的 `lifecycle`（`CLAIMED` / `SETTLED`）與其 worker／worktree／branch 綁定 |
| `C:\Users\User\AppData\Local\JohnnyRouter\queue\metadata\live-dispatch-metadata-v1.json` | 交叉佐證；每個 receipt 目前的 `lifecycle`（此刻只列 `ACTIVE` 的），連同 ticket digest／baseline commit 綁定 |

`dispatch-journal.jsonl` 全檔只有 7 行（讀取當下已到檔尾），全部摘錄如下，不是節選。
三份檔案的檔案系統修改時間都落在同一分鐘附近，與本次派工（receipt-002）同時，屬於
剛發生的即時狀態，不是歷史快照。

## 二、gov-15 對照：沒有路回來

票裡點名這四條（13:15–13:17）當對照組——這是 P5 重派路第一次在真 store 上被走到，
但沒有走完。

| # | `at_utc` | `receipt_id` | `outcome` | `superseded_by_receipt_id` |
| --- | --- | --- | --- | --- |
| 1 | 13:15:12.403261 | `receipt-gov15-ignore-venv-001` | `DISPATCHED` | — |
| 2 | 13:15:39.135330 | `receipt-gov15-ignore-venv-001` | `DISPATCHED` | — |
| 3 | 13:15:58.467571 | `receipt-gov15-ignore-venv-002` | `RECEIPT_CONFLICT` | — |
| 4 | 13:17:01.089301 | `receipt-gov15-ignore-venv-002` | `RECEIPT_CONFLICT` | — |

逐行說明：

- **#1** 是 gov-15 這次真派工的第一次 `DISPATCHED`——receipt-001 核發，`grant_id`
  為 `9fbc529278f3457ea1dea0db56479d9f`（這個 grant id 在全部 7 條紀錄裡都一樣，
  推斷是 session／principal 層級的授權，不是每張票各自一個 grant；receipt 才是
  per-ticket 的單位）。交叉比對 `worker-assignments-v1.json`：這個 receipt 綁的
  claim 是 `claim-842e7cb977f34fcabea9148423a5529b`，worker_ref
  `worker-gov15-sonnet-01`，**目前 lifecycle 是 `SETTLED`**——代表這個 claim 後來
  真的走過補償結清，對得上票面敘述「gov-15 試車走過 grant → admit → claim →
  spawn 失敗 → 補償（真的）」。journal 本身沒有獨立的 `SPAWN_FAILED` 或
  `SETTLED` outcome 列，補償真的結清這件事**只能從 worker-assignments 的
  lifecycle 欄位交叉證明**，journal 逐行看不到。
- **#2** 是同一個 `receipt-gov15-ignore-venv-001`，27 秒後又出現一次
  `DISPATCHED`。同一 receipt id 重複出現同一 outcome，原始資料就是這樣，我沒有
  找到第三份檔案能解釋這是重試還是重放；如實記錄，不猜測成因。
- **#3、#4** 是嘗試把 receipt-001 撤銷、換發 receipt-002（即 `redispatch_worker`
  的路徑）——但兩次都撞上 `RECEIPT_CONFLICT`，中間隔了約 1 分 3 秒，仍是同一個
  目標 receipt id `receipt-gov15-ignore-venv-002`。
- **全檔找不到任何一條 `receipt-gov15-ignore-venv-001` 的 `REVOCATION_*`
  條目**——重派兩次都卡在 `RECEIPT_CONFLICT`，沒有走到撤銷那一步。交叉比對
  `live-dispatch-metadata-v1.json`：`receipt-gov15-ignore-venv-001` 現在
  **`lifecycle` 仍是 `ACTIVE`**，也就是這張 receipt 至今沒有被正式撤銷，還開著。
  這就是票面說的「P5 重派路：只在測試 store 上證過，真 store 上那張被 brick 的
  receipt 至今還躺著」——**沒有路回來**。

這張舊 brick receipt 不在本票範圍內清理（票面「不在本票範圍」已明講），這裡只記錄
它現在的真實狀態，供對照。

## 三、P6 第一段：失敗演練＋重派（有路回來）

本票自己的 receipt，三條 `at_utc` 幾乎連續（14:27:27，相隔數十毫秒）：

| # | `at_utc` | `receipt_id` | `outcome` | `superseded_by_receipt_id` |
| --- | --- | --- | --- | --- |
| 5 | 14:27:27.612470 | `receipt-p6-live-verification-001` | `DISPATCHED` | `null` |
| 6 | 14:27:27.636489 | `receipt-p6-live-verification-001` | `REVOCATION_REVOKED` | `receipt-p6-live-verification-002` |
| 7 | 14:27:27.639500 | `receipt-p6-live-verification-002` | `DISPATCHED` | `null` |

逐行說明，對照票面第一段的敘述「admit → claim → spawn 失敗 → 補償 settle。然後走
`redispatch_worker`：撤銷 → 新 receipt → 新 claim → 真 spawn」：

- **#5** 是刻意會失敗的 spawn port 那次派工——receipt-001 核發。交叉比對
  `worker-assignments-v1.json`：綁定 claim
  `claim-e6aef7577b3a449e9bf43ee74fc5e0a9`，worker_ref `worker-p6-drill-01`，
  worktree_ref／branch_ref 都是 `worktree-p6liveverification-01` /
  `branch-p6liveverification-01`。**目前 lifecycle 是 `SETTLED`**——即補償已結
  清，對上「spawn 失敗 → 補償 settle」。同 gov-15 的情形，journal 本身沒有獨立
  列出 spawn 失敗或補償的 outcome，這一步的「真的失敗、真的補償」只能靠
  worker-assignments 的 lifecycle 交叉證明；`SETTLED` 是這裡唯一能看到的直接
  證據。
- **#6** 是 `redispatch_worker` 的撤銷動作——`outcome` 正是票面要求的
  `REVOCATION_*`，`superseded_by_receipt_id` 明確指向
  `receipt-p6-live-verification-002`。`host_worktree_path` 在這條是 `null`
  （撤銷動作本身不綁定某個 worktree，合理）。**這一步和 gov-15 那四條的關鍵差
  異：gov-15 卡在 `RECEIPT_CONFLICT`、從未走到撤銷；這裡撤銷確實發生了。**
- **#7** 是新 receipt、新 claim、真 spawn。交叉比對兩份檔案：
  `worker-assignments-v1.json` 顯示 claim
  `claim-c62c4574260c4c52a02053041c1ea850` 綁定
  receipt-p6-live-verification-002、worker_ref `worker-p6-sonnet-01`，**目前
  lifecycle 是 `CLAIMED`**（還沒結清——因為這個 worker 就是我，我還沒回報）；
  `live-dispatch-metadata-v1.json` 顯示這個 receipt **`lifecycle` 是
  `ACTIVE`**，`baseline_commit` 為 `d4f8e350ab581c99b952020e99c6eb549effd5eb`，
  與我所在 worktree 的 HEAD 一致。

第一段的結論：journal 出現了票面要求的 `REVOCATION_*` 條目與
`superseded_by_receipt_id`，重演了 gov-15 被 brick 的完整路徑，但這次撤銷確實
發生、新 receipt 確實核發、真 spawn 確實生出了 worker——**有路回來**。

## 四、我是誰

我是 `receipt-p6-live-verification-002` 這次 `DISPATCHED`（上表 #7）真的生出來的
worker：

- **receipt**：`receipt-p6-live-verification-002`
- **claim**：`claim-c62c4574260c4c52a02053041c1ea850`
- `worker-assignments-v1.json` 裡對應的 `worker_ref`：`worker-p6-sonnet-01`
- `worktree_ref` / `branch_ref`：`worktree-p6liveverification-01` /
  `branch-p6liveverification-01`（對應本機路徑
  `.worktrees/p6`、分支 `implement/p6-live-verification`）
- 綁定 commit：`d4f8e350ab581c99b952020e99c6eb549effd5eb`（worktree HEAD，與
  `live-dispatch-metadata-v1.json` 的 `baseline_commit` 一致）
- 此刻 claim 的 lifecycle 是 `CLAIMED`——本文件本身就是我在完成交付物的過程，
  回報之後（`record_worker_return`）這個 lifecycle 預期會轉為 `SETTLED`，那是
  第二段的起點。

## 五、第二段：完整往返（排程器實機）

**狀態：完成（2026-08-21 14:35 UTC）。**

第一段最後一步的真 spawn 已經發生（即本文件的作者，見上一節）。第二段要驗的是
「worker 回報後」的路徑：`record_worker_return`（settle ＋入列）→ 控制面審閱 →
worker 的 branch 就緒 → `integrate_next_work` 拉取並經閘門完成真的整合，全程
不得由控制面手動 merge 或手動組 `DocumentMutationRequest`。

我回報本交付物之前，這一段還沒有可摘錄的 journal 條目——交叉比對
`document-mutation-journal.jsonl`，目前最後一條是 `implement/gov-16-named-invariant-failure`
（14:20:39），沒有任何一條 `ticket_path` 指向
`modules/tickets/workstation-dispatch/p6-live-functional-verification.md`。

以下欄位待控制面在完成第二段後回填：

| 欄位 | 內容 |
| --- | --- |
| `record_worker_return` journal 條目（settle ＋入列） | `RECORDED`。佇列本身無 journal（P3 設計），證據是 store 狀態：work item `work-e225adf125d9444fb309585f86a70be0` 產生（後由拉取轉 `PULLED`）；claim `claim-c62c4574260c4c52a02053041c1ea850` 轉 `SETTLED` |
| 控制面審閱結論 | 通過；交付物由控制面以 `f68be93` 提交於 `implement/p6-live-verification`（審閱與 branch 記帳是控制面的常規工作，不在被驗的 Router 步驟清單內） |
| worker branch 就緒判定 | `implement/p6-live-verification` @ `f68be93`，可 ff |
| `integrate_next_work` 的 `document-mutation-journal.jsonl` 條目（`outcome`、`candidate_ref`、`detail`） | `14:35:55.508767+00:00`／`outcome: INTEGRATED`／`candidate_ref: implement/p6-live-verification`／`detail: f68be9357ecedb15b3a08d64cd7faca3ea1ad6ed`——**main 移到 f68be93，merge 由閘門在 `integrate_next_work` 內執行** |
| 是否全程沒有手動 merge／手動組 `DocumentMutationRequest` | 是。控制面呼叫的只有 `record_worker_return` 與 `integrate_next_work` 兩個進入點（driver 腳本 `p6_stage_b.py` 全文可查）；`DocumentMutationRequest` 由 `integrate_next_work` 內部從 `TicketResolution` 構造 |

## 六、第三段：commit 觸發（實機首次）

**狀態：BLOCKED——這條腿端到端不存在，已開 P7。**

依 P6 的規則（卡住 → 停下、記錄、開新票，不得手動代勞後宣稱通過），第三段在
arm 訂閱之前的機制清查就停了：

- `WorkSource.COMMIT_TRIGGER` 在整個 library **沒有任何生產者**——只有
  `work_queue`（收）與 `dispatch_session`（正確擱置）認識它。
- `event_runner` 的產品是**喚醒**，與 work queue 之間零引用。
- `work_queue.py:284` 有現成的 commit-trigger 建構子——插座在，線不在。

控制面**沒有**手動呼叫 `enqueue_work` 假造一筆觸發項目來讓表格變綠。
接線是 `modules/tickets/workstation-dispatch/p7-commit-event-reaches-no-queue.md`；
P7 整合後回到這裡收尾第三段。

第三段要驗的是用既有 `runner subscribe` CLI（E13）對本 repo arm 一個訂閱、落一個
真 commit，觀察它以 `COMMIT_TRIGGER` 來源進入佇列，且消費端正確回報
`COMMIT_TRIGGER_PENDING` 不取走。本次擷取時，`dispatch-journal.jsonl` 裡沒有任何
`COMMIT_TRIGGER` 相關條目，這一段完全尚未開始。

以下欄位待控制面在完成第三段後回填：

| 欄位 | 內容 |
| --- | --- |
| 訂閱 arm 的憑證／確認 | 待補 |
| 觸發用的真 commit（hash） | 待補 |
| `dispatch-journal.jsonl` 裡 `COMMIT_TRIGGER` 來源的條目 | 待補 |
| 消費端 `COMMIT_TRIGGER_PENDING` 回報（不取走）的證據 | 待補 |

## 七、哪一步是誰做的

**控制面代勞清單必須為空是本票的通過條件。** 表頭與第一段的行如下；第二、三段留
待控制面在完成各自段落後依同一表頭回填。

| 段 | 步驟 | 執行方 | 證據 | 控制面手動代勞？ |
| --- | --- | --- | --- | --- |
| A | 用會失敗的 spawn port 派工（admit＋claim＋故意失敗的 spawn） | JohnnyRouter 派工機制 | journal #5 `DISPATCHED` receipt-001；`worker-assignments-v1.json` claim `claim-e6aef7577b3a449e9bf43ee74fc5e0a9` → `worker-p6-drill-01` | 否（三份 store 檔案中沒有看到人工介入痕跡） |
| A | spawn 失敗 → 補償 settle | JohnnyRouter 派工機制 | `worker-assignments-v1.json` 同一 claim 的 `lifecycle` 為 `SETTLED`（journal 無獨立列） | 否（同上；見下方註記） |
| A | `redispatch_worker`：撤銷 receipt-001 | JohnnyRouter 派工機制 | journal #6 `REVOCATION_REVOKED`，`superseded_by_receipt_id` = receipt-002 | 否 |
| A | `redispatch_worker`：核發 receipt-002、新 claim、真 spawn | JohnnyRouter 派工機制 | journal #7 `DISPATCHED` receipt-002；`worker-assignments-v1.json` claim `claim-c62c4574260c4c52a02053041c1ea850` → `worker-p6-sonnet-01`；`live-dispatch-metadata-v1.json` receipt-002 `lifecycle=ACTIVE` | 否（我＝這一步真 spawn 產生的 worker，正在寫這份文件本身就是這步真的發生的證據） |
| B | `record_worker_return`（settle ＋入列） | 待補 | 待補 | 待補 |
| B | 控制面審閱 | 待補 | 待補 | 待補 |
| B | `integrate_next_work`（經閘門整合） | 待補 | 待補 | 待補 |
| C | 訂閱 arm | 待補 | 待補 | 待補 |
| C | 真 commit 觸發、入列、`COMMIT_TRIGGER_PENDING` 回報 | 待補 | 待補 | 待補 |

**「否」欄位的證據邊界要說清楚**：以上四行的判斷依據是我讀到的三份 store 檔案
（journal、worker-assignments、live-dispatch-metadata），這三份都是**結果態**紀
錄（哪個 receipt／claim 現在是什麼狀態），不是**操作者身分**的直接證明（例如
driver 腳本自己的執行日誌）。就我能讀到的範圍，找不到任何手動編輯 store 檔案、
手動呼叫閘門或手動組裝回傳的痕跡，第一段四行的「控制面手動代勞」欄目前都是
「否」。若控制面另外持有 driver 執行紀錄能更直接地佐證，那份不在本票的邊界宣告
內（`modify`/`create` 只有本檔），我沒有讀，也不代勞去找。

## 八、我的邊界聲明

- 本次任務只新增了這一個檔案：`doc/runbooks/live-verification-047.md`。
- 沒有修改 `library/`、`tests/`、`modules/tickets/` 下任何檔案。
- 沒有執行 pytest（本票 `forbid = tests/`，也沒有新測試）。
- 沒有 `git commit`、沒有 `git merge`、沒有 `git push`。
- 讀取的三份 store 檔案（`dispatch-journal.jsonl`、`worker-assignments-v1.json`、
  `metadata/live-dispatch-metadata-v1.json`）以及
  `document-mutation-journal.jsonl` 全部只讀，沒有寫入。

## 九、候選觀察（非本票判定，是否開票由控制面／owner 決定）

- `receipt-gov15-ignore-venv-001` 目前在真 store 上 `lifecycle` 仍是 `ACTIVE`，
  從未被撤銷（見第二節）。票面已明講這張舊 brick receipt 不在本票範圍內清理，
  這裡只是把它現在的真實狀態留下來，供 owner／控制面判斷是否需要另開票處理。
- gov-15 的 `receipt-gov15-ignore-venv-001` 在 journal 裡於 13:15:12 與
  13:15:39 出現兩次幾乎相同的 `DISPATCHED` 記錄（同一 receipt id，相隔 27
  秒）。我沒有足夠證據判斷這是重試、重放還是別的機制行為，如實記錄，不在本票
  內下結論。
