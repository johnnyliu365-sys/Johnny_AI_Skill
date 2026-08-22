# 交接：Level 1 plugin 的出貨邊界（2026-08-22）

寫給接手的 agent（Codex 或其他 host）。**這份文件不重述規則**——規則在票裡，
重抄會產生第二份會漂移的來源。這裡只講「你現在站在哪、下一步是什麼、哪裡會踩到」。

## 動手前

照 [`AGENTS.md`](../../AGENTS.md) 的啟動順序走，它會把你路由到
[`Workflow.md`](../../Workflow.md) 與被指定的 skill reference。
**不要載入完整 Workflow、全部 references 或整個 library。**

角色分層與派工長度見 [`dispatch-model-profile.md`](dispatch-model-profile.md)。
debug 任何「奇怪」的問題先查 [`PITFALL-REGISTER.md`](../../modules/tickets/PITFALL-REGISTER.md)。

## 這條線在解什麼

裝 Level 1 plugin 曾經等於 **`git clone` 整個開發庫**：12 MB、89 個 commit 的歷史，
`tests/`、`doc/`、`modules/tickets/`（全部治理票）都落到使用者硬碟上，
而真正要用的 `skills/` ＋ `commands/` 只有 131 KB。

四張票，前三張已整合：

| 票 | 狀態 | 做了什麼 |
| --- | --- | --- |
| [`01`](../../modules/tickets/claude-code-plugin-distribution/01-claude-code-plugin.md) | `DONE` | 最初的 plugin／marketplace 條目 |
| [`02`](../../modules/tickets/claude-code-plugin-distribution/02-the-plugin-ships-the-whole-development-repository.md) | `DONE` | 白名單宣告 ＋ 閉包證明（39 cell）。**交付宣告，不是硬碟差異** |
| [`03`](../../modules/tickets/claude-code-plugin-distribution/03-the-pin-and-the-tree-are-unrelated.md) | `DONE` | 產生器 ＋ 把釘子綁到樹（40 cell）。797 檔 → **242 檔** |
| [`04`](../../modules/tickets/claude-code-plugin-distribution/04-the-pin-is-not-bound-to-reachability.md) | **`OPEN`** | **你的下一步**：把釘子綁到可達性 |

整合點：`45b7c914`（票 02）、`53c6d4e3`（票 03），皆經 `admit_document_mutation` 判 `INTEGRATED`。

## 下一步：派票 04

票已寫好，直接派即可（`Sonnet 5 high`，理由寫在票裡）。

```
git worktree add -b implement/plugin-04-reachable-pin .worktrees/plugin-04 10e3eb33
```

派工訊息只放：要做什麼、票在哪、worktree／branch、跑測試的指令、不要 commit、回報什麼。
**不要重抄診斷、證據、驗收、邊界**——那些全在票裡。

## 推送狀態（重要）

本次交接連同以下兩者一起推上 `origin`：

- **`main`** — 含票 02／03 的整合與票 04
- **`refs/heads/publication-0.4.9`** → `696319f8` — 發佈樹本身

發佈 commit 必須跟著推，否則你在本機 clone 之後
`test_the_pinned_sha_exists` 會直接紅——那個 commit 是 parentless，
不會跟著 `main` 一起過來。

**但票 04 仍然要做，範圍已縮小。** 推送時順手把錨定換成了可推送的分支
（`refs/publication/0.4.9` 已刪除，本機與 origin 都是 `publication-0.4.9`），
所以「namespace 選錯」那一半沒了。**剩下的那一半才是重點**：
刪掉錨定 ref，套件仍然全綠——**可達性還不是一個被測試釘住的事實。**

**其餘一律不推。** 本專案規則：沒有被明確指示就不 push。

**repo 目前是 PRIVATE。** `raw.githubusercontent.com` 只服務公開 repo，
所以安裝指令在公開前**必然 404**，這條路徑在公開前無法驗證。
**不得宣稱驗過。**


公開之後使用者會打的指令（實測形狀，尚未線上驗證）：

```
claude plugin marketplace add https://raw.githubusercontent.com/johnnyliu365-sys/Johnny_AI_Skill/main/.claude-plugin/marketplace.json
claude plugin install johnny-ai-skill@johnny-ai-skill
```

第一行不 clone（只快取一個 JSON 檔）；第二行抓釘住的那棵樹。

## 本機環境（違反就浪費一輪）

`py -3.11`（**沒有** `python`）、無 pwsh、主控台 cp950、工作副本 CRLF。

**repo 路徑含中文**，venv 建在 repo 內會產生大量假紅。一律建在外面的 ASCII 路徑：

```
py -3.11 -m venv C:\Users\User\AppData\Local\Temp\v04
C:\Users\User\AppData\Local\Temp\v04\Scripts\python.exe -m pip install -q -r requirements-dev.txt
```

`requirements-dev.txt` 已含 `pytest==9.1.1`；只裝 pytest 會得到 111 個 collection error
（缺 `pydantic`），那不是候選的問題。

**同一個 checkout 一次只能跑一個 pytest**——並行會污染共享 runtime root。

跑套件**永遠不要只看最後一行**（登記簿 D4）：

```
python -m pytest -q -p no:cacheprovider 2>&1 | grep -E "^(FAILED|SUBFAIL|ERROR)"
```

**同一個 commit 在 worktree 與 main checkout 會給出不同答案**（登記簿 C13）。
`PayloadClosureTests` 在 `.worktrees/*` 全綠，在 main checkout 4 紅——變數是
`.claude/worktrees/`，那是 Claude Code harness 建的目錄，只存在於 main checkout，
而閉包掃描會 stat 檔案系統。**乾淨 clone 上會是綠的**（沒有那個目錄），
但這代表整合前的全套件必須至少在「使用者會拿到的那個形狀」上跑過一次，
否則閘門會綠在一個被環境遮住的缺陷上——這已經發生過一次了。

受閘測試要 `JOHNNY_LIVE_QUAL=1`，涉及五個檔（`test_whole_chain_qualification.py` 等）。
基準：全套件 1641 passed／22 skipped／零 FAILED；受閘 28 passed／1 skipped／零 FAILED。

## 整合怎麼做

實作者**不 commit**；審閱者審完後代為 commit 到候選分支，再過閘門。閘門自己執行
`merge --ff-only`，所以：

- **整合前 `main` 不能移動**，否則候選 ff 不進去（要先 stash）
- 候選分支若與 `main` 同一個點，閘門會回 `INTEGRATED` 但**什麼都沒整進去**
  ——確認 `integrated_commit` 是候選的 sha，不是舊的 main HEAD

呼叫形狀：`admit_document_mutation(JohnnyRootLayout.resolve(), DocumentMutationRequest(...))`，
`ticket_path` 是 repo 相對路徑且**票必須已經在 `main` 上**。
`JohnnyRootLayout` 在 `library/local_orchestration/johnny_root_layout.py`（不是 `runtime_root`）。

## 這條線特有的地雷

- **`.claude-plugin/plugin.json` 的 `payload` 這個 key，Claude Code 不讀**
  （`claude plugin validate --strict` 會說 `Unknown field 'payload'`）。
  它的消費者只有產生器與測試。這件事必須明說，不得讓文件讀起來像它是 runtime 行為。
- **驗證 manifest 時指到檔案本身**，不要指到 repo 根——指到根會被根目錄的
  `CLAUDE.md` 警告蓋掉，看不到真正的那條。
- **SHA-1 不動點**：commit 不能包含一個記載自己 id 的檔案。發佈的那份
  `marketplace.json` 記 40 個零（解析不到任何物件 → fail closed）。
  **不要「順手修好」它**——填真實 id 就會出貨一個指向 797 檔整包的活釘子。
- **餵路徑給 git 一律用二進位模式。** 文字模式 stdin 會把 `\n` 改成 `\r\n`，
  git 收到帶尾隨 CR 的路徑會忽略它、印 stderr、**然後回傳 0**。payload 曾因此靜默變空。
  **零退出碼不是任何東西被暫存的證據。**
- **`git ls-files` 會 escape 非 ASCII 路徑**，所以 `git ls-files | grep '[^\x00-\x7F]'`
  在一個滿是中文路徑的 repo 上回空——那是假陰性。用 `-z`。
- 宣告的 payload 有 **42 個非 ASCII 路徑**（`library/` 底下的中文目錄）。
  本機 round-trip 正常，但它們會送到別人的檔案系統與編碼上。尚未在別的平台驗過。

## 這條線之外還欠著的

| 事項 | 在哪 |
| --- | --- |
| `gov-23` 審完但未整合 | worktree `.worktrees/gov-23`，branch `implement/gov-23-unbounded-wait`，commit `425e6b6a` |
| `dispatch_session.py:697` 的 `KeyError` | `_SETTLE_FAILURE_NAMES` 漏了 `LOCK_CONTENDED`；在 gov-23 邊界外 |
| README 的安裝章節 | 本機英文版與 GitHub 上的中文版**已分歧**，需先決定以哪份為底 |
| 44 個未分類的 `Failure` enum | governance 22 的後續 |
| `johnny-install.cmd` 三個拒絕代碼已分類未印出 | governance 22 宣告的缺口 |
| 出貨文件裡的死連結 | 票 02 實作者列於 `_REFERENCES_OUTSIDE_PAYLOAD`，標記 `DEVELOPMENT_ONLY` |
| 閉包測試依賴工作副本狀態（C13） | 未開票；修法方向是讓分類只依 repo 事實 |

## 一句話的方法論

這條線上最貴的兩個發現，都是**審閱者從實作者沒走的門進去**才看到的，而且**都是零紅**：

1. 釘子釘到一個只有 3 個檔、連 `skills/` 都沒有的 commit → 39 cell 全綠（登記簿 D7）
2. 刪掉唯一指向發佈 commit 的 ref → 79 cell 全綠（票 04）

兩次的形狀一樣：**測試驗了一件真事，只是那件事不是我們要保證的那件事。**
接手時請照 governance 17 繼續——**零紅是發現，不是通過。**
