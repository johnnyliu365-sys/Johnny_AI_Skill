# 雷點登記簿（Pitfall Register）

> 本專案實際踩過、查證過、修掉的雷，供後續 debugger 與稽核人員查閱。
> 每一條都有三件事：**雷是什麼、證據在哪、修法與防回歸在哪**。
> 深入細節一律以工單為準（每條附工單連結）；本文件是索引，不是替代品。
> 最後更新：2026-08-20（0.4.3 發行前統整）。

---

## A. 權限模型類（最高嚴重度——外部審查五輪反覆命中的族群）

### A1. 從呼叫端資料鑄造權限（minting authority from caller data）
- **雷**：runner 曾把 subscription 檔（呼叫端資料）裡的 receipt 寫進 durable
  checkpoint——等於偽造的 receipt 能滿足自己的喚醒申領。改名、搬移該能力都不算修好。
- **證據**：外部審查連續三輪 P0（[event-runner-binding/README.md](event-runner-binding/README.md)
  CLOSURE-E8-02／E8-03 全程記錄）；別名回流突變證明 name-based 檢查是假綠。
- **修法**：runtime 只留 `verify_receipt_claimable`（純讀取）；發放權移到
  workstation 入口（[workstation-dispatch/w1](workstation-dispatch/w1-dispatch-authority-admission.md)）。
- **防回歸**：`tests/test_review_correction_regressions.py` 的
  runtime-binding-identity 細胞——斷言**執行期實際綁定的物件型別**，不是名字。
  別名回流突變會轉紅（實測）。

### A2. 能力持有＝能力可用（capability held is capability used）
- **雷**：元件只要持有一個「型別上帶有」發放／申領方法的物件，就算從未呼叫也算違規。
- **證據**：E8-03 P0——runner 建構完整 boundary 即被退回。
- **修法**：三個 scoped facade，各自只暴露該側需要的方法——
  `wake_scoped_boundary`（read/claim/settle）、`issuance_scoped_boundary`
  （register/issue/read）、`review_return_boundary`（兩個 read、零寫入）。
- **防回歸**：各票的 facade-surface 測試＋runtime-identity 斷言。
- **誠實邊界**：單一 Python 行程內任何程式碼仍可 import 完整 boundary；此殘留
  已明文記錄，待 OS 行程權限分離（workstation 線後續）。

### A3. 能力用「宣稱」而非「探測」
- **雷**：`state=PROVEN` 若可由呼叫端傳入，等於 A1 換個欄位。
  `MonotonicDeadlineCapabilityProof` 曾經**只有契約、沒有 probe**。
- **證據**：[event-runner-binding/README.md](event-runner-binding/README.md) E9 節。
- **修法**：`deadline_capability.py`——真的排一次 monotonic one-shot timer 並要求
  它**燒到期才觸發**；wake 能力由 `probe_wake_capability` 實際執行宣告命令證明；
  E12 的注入端點（env var）**同樣要過 probe** 才被採用。
- **防回歸**：`SubscriptionInputs` 連 receipt 綁定欄位的**名字都不能出現**
  （`tests/test_subscription_builder.py` 逐一斷言）。

### A4. verdict 可被憑空提交
- **雷**：審查結論是帶權限的證物；若不綁「真的派過工＋reviewer 真的被叫醒過」，
  任何人可對從未發生的審查交結論。
- **證據**：[workstation-dispatch/w2](workstation-dispatch/w2-reviewer-return-path.md)。
- **修法**：提交前讀兩個 durable 事實——receipt ACTIVE＋該 receipt 存在
  `HOST_ACCEPTED` 的喚醒紀錄（`NO_EFFECT`／`EFFECT_UNCERTAIN` 不算送達）。
- **防回歸**：反向突變——拿掉喚醒檢查三格轉紅。

---

## B. 分散式／並行類

### B1. 行程內推理蓋在共用 durable 狀態上（本專案最大的一族）
- **雷**：共用磁碟狀態＋行程內記憶體判斷＋無跨行程鎖 ⇒ 並行即壞。
  兩處實例：測試的 `_CLAIMED_MARKERS`（孤兒 lease 癱瘓全套件）、
  **production 的 review submit/consume**（兩個並行 `review consume` 各發一次
  RouterEvent——同一工作流轉換被驅動兩次）。
- **證據**：[workflow-governance/03](workflow-governance/03-suite-order-fragility.md)
  完整因果鏈（含兩次錯誤診斷的更正）＋
  [workstation-dispatch/w5](workstation-dispatch/w5-cross-process-exactly-once.md)。
  量化：單一並行掃描者使 200 次 teardown 失敗 16 次；並行雙 pytest 96 failed。
- **修法**：排它鎖抽成 `file_lock.py`（原本有**兩份相同的私有副本**，本身就違規），
  review 臨界區整段上鎖。
- **防回歸**：`tests/test_review_return_concurrency.py`——barrier 撐大競態窗口，
  雙消費者必須恰為 `["EMITTED","NOTHING_PENDING"]`；拿掉鎖即轉紅（實測）。

### B2. Windows share-mode：讀者擋住刪除者
- **雷**：被列舉中的目錄、被讀取中的檔案在 Windows 上**不能刪**。任何
  「一邊掃描、一邊刪除」的並行組合都會間歇性 `DELETE_FAILED`。
- **證據**：隔離實驗 16/200（governance 03 addendum）。
- **修法／緩解**：測試層以 guard 揭露（見 C1）；營運規則：**同一 checkout
  一次只跑一個 pytest 行程**。
- **同族先例**：CR-L8-01——uninstall 在自有 venv 的 python 上執行，鎖住自己的
  exe 導致 `REMOVAL_FAILED`；修法是 launcher 先把 venv 複製到 %TEMP% 再執行移除
  （[live-install-binding/README.md](live-install-binding/README.md)）。

### B3. 「恰好一次」的排序方向
- **雷**：先交出事件再標記已消費 ⇒ 崩潰時同一轉換被驅動兩次。
- **修法**：**標記先落盤（fsync）、事件後交付**——崩潰損失的是一次「看得見、
  可刻意重放」的發射，而不是一次隱形的重複驅動
  （[workstation-dispatch/w3](workstation-dispatch/w3-router-return-consumption.md)）。

---

## C. 測試假綠類（每一條都曾讓紅燈裝綠）

### C1. 孤兒 lease 毒化全套件、且以誤導訊息呈現
- **雷**：殘留一個 lease ⇒ 約 80 個不相關測試以
  `project-runtime provisioning must succeed` 失敗——既不說原因也不說解法。
  更危險的是它**訓練讀者忽略失敗**（「殘留啦，清掉重跑」）。
- **證據與修法**：governance 03。`tests/test_aaa_runtime_root_guard.py` 排序在
  最前，單一具名失敗講明：孤兒路徑、孤兒**永遠不正常**（是洩漏）、可能原因
  （並行 pytest／被 kill 的執行）、先查因再清除。**不自動刪任何東西**
  （ADR-20260813-007 原樣保留）。

### C2. 子字串斷言命中錯的東西（CR-E7-01 的藏身處）
- **雷**：E6 R3 斷言 `"handoff" in payload`——期限喚醒的 payload 帶
  `handoff_id=-` 欄位，子字串剛好命中 ⇒ **handoff 喚醒死了一整條線卻長期綠燈**。
- **證據**：[event-runner-binding/e10](event-runner-binding/e10-handoff-driven-wake.md)。
- **修法**：斷言具名欄位（`action=REVIEW_HANDOFF`、拒絕 `SUPERVISION_DEADLINE`）。

### C3. 夾具常數讓期限永遠在過去
- **雷**：`started_at_ms=1_000` 對上 monotonic 時鐘 ⇒ 期限喚醒在 arm 當下就發射，
  掩蓋 handoff 路徑全死；`subscription_builder` 也繼承了同一常數。
- **修法**：一律用 runtime 實際比對的時鐘（`monotonic_ns()//1_000_000`），
  回歸釘死起點落在呼叫前後的區間內。

### C4. 「檔案存在」不等於「事件發生」
- **雷**：capability probe 會真的執行 wake 命令並寫出同一個檔案——等待
  「檔案存在」的 qualification 等到的是 probe 的產物。
- **修法**：等待內容特徵（`ROLE_WAKE_V1`），不是存在性。

### C5. 名字檢查可被別名繞過
- **雷**：namespace／facade-surface 檢查在別名回流（`import X as _Y`）下維持綠。
- **證據**：E8 第五輪 P0；L9 驗收時同手法再抓一次。
- **修法**：斷言執行期實際綁定物件的 `type(...) is`＋方法不存在；
  E13 驗收沿用同標準。

### C6. 用假產物測抽取，真產物才會爆
- **雷**：L9 首版 R4 用合成 zip＋改寫 pin——機制綠，真 bundle 上 `tar -xf`
  抽單檔其實會失敗。缺席 zip 的 junction 回歸也是同族（guard 拿掉仍綠）。
- **修法**：實物證據另列（比照 L8 `OWNER_EXECUTED` 體例）；junction 回歸改用
  真可抽取 bundle；抽取改 `System.IO.Compression`。

### C7. 測試讀自己的原始碼找禁用字串
- **雷**：W4 首版在自己檔案裡搜 `settle_role_wake_attempt`——**斷言本身就含
  那個字串**，自我指涉必失敗（或反向必假綠）。
- **修法**：檢查模組命名空間綁了什麼，不是檔案文字。

### C8. 每段接縫都測過 ≠ 整條鏈成立
- **雷**：CR-E7-01 就是兩段各自正確、接點死掉。W2 的「喚醒證據」曾由測試自己
  claim/settle 模擬。
- **修法**：[workstation-dispatch/w4](workstation-dispatch/w4-whole-chain-qualification.md)
  ——一次 gated 執行跑完 dispatch→runner→commit→喚醒→verdict→RouterEvent，
  **無任何夾具發放任何東西**（以命名空間斷言證明）。

---

## D. 發行工程類

### D1. Wrapper 的 digest pin 手寫、無人校驗
- **雷**：升版忘改 wrapper ⇒ 使用者雙擊拿到 `DIGEST_MISMATCH`——**靜默直達
  使用者**的缺陷，且無測試會抓。
- **修法**：[live-install-binding/l10](live-install-binding/l10-release-pin-guard.md)
  ——版本單一來源（manifest）＋名稱一致性測試（升版不改 wrapper 即紅）＋
  發行前 preflight 對實建 bundle 比對 digest（gated `MATCHED`）。
  preflight **絕不自動改寫 pin**。

### D2. digest 依賴 source_commit ⇒ 發行必須兩段 commit
- **雷**：release commit 無法包含自己產物的 digest（循環）。
- **修法**：commit A（升版＝bundle source）→ clean clone 建 bundle 得 digest →
  commit B（wrapper／測試雙登錄 pin；不在 payload 內故不影響已建 bundle）。
  tag 指向 **A**。0.4.2 實例：`558a17b`→`e6ccfdc`。

### D3. SOURCE_DIRTY 與 porcelain 的邊界
- **雷**：pycache、工作樹、任何未追蹤檔都會讓 deterministic build 拒絕；
  但 porcelain（`--untracked-files=all`）**不含被 ignore 的路徑**。
- **修法**：一律從 clean clone 建（L7 教訓）；`.worktrees/`、`.claude/worktrees/`
  進**會提交的** `.gitignore`（`.git/info/exclude` 是本機的、換機即失效——
  governance 02）。注意：`AGENTS.md`、`README.md` 在 payload 白名單內，
  改動即改 bundle digest。

### D4. 被提交的 .pyc 與被截斷的錯誤輸出（複合雷）
- **雷**：`.gitignore` 從未有 pycache 規則 ⇒ 56 個 `.pyc` 進版控 ⇒ 與 main
  checkout 的未追蹤 pycache 相撞 ⇒ **三次 ff-merge 被拒**——而 merge 輸出接了
  `tail -1`，錯誤被截掉，**三次都誤報整併成功**。
- **修法**：根規則 `__pycache__/`＋`*.py[cod]`；營運紀律：**永不截斷可能帶錯誤
  的命令輸出**。發行 bundle 未受影響（manifest 本就按副檔名排除 .pyc）。

---

## E. 環境／平台類（本機事實，違反即浪費一輪 debug）

| 雷 | 症狀 | 修法 |
| --- | --- | --- |
| cp950 主控台 | subprocess `text=True` 對中文檔名／輸出直接炸 | bytes＋UTF-8 `errors="replace"`；Python 加 `-X utf8` |
| CRLF 工作副本 | byte-exact 突變腳本比對不到；`.cmd` 用 LF 會解析錯亂 | 腳本一律先 normalize `\r\n`；`.gitattributes` 釘 `*.cmd`/`*.bat` CRLF＋測試 pin |
| 只有 `py -3.11` | `python`、`pwsh` 不存在 | 一律 `py -3.11`；PowerShell 5.1 語法（無 `&&`） |
| Git Bash MSYS 路徑轉換 | `cmd.exe /d /c` 的 `/d` `/c` 被轉成磁碟路徑，命令靜默變成開互動 shell | 經 Python subprocess 呼叫，或 `//d //c` |
| Windows 時鐘粒度 ~15.6ms | 追蹤時間軸同刻事件排序不可信 | 同刻戳事件不得當作順序證據（E10 調查記錄） |
| 唯讀 git 物件 | `rmtree` 失敗 | `chmod onerror` 的刪除 helper |
| Explorer 雙擊 `.cmd` | script 一結束視窗即關，BLOCKED 原因沒人看得到 | 每個 exit 前 `pause`；結構性測試釘死（拿掉任一 pause 即紅，CR-L9-01） |
| 外掛不改 PATH | 裝好後找不到 `johnny-router` | 以完整路徑呼叫 launcher（README 已載明）；重跑 installer 會 `VENV_ALREADY_PRESENT` 擋下屬預期 |
| Antigravity agentapi | LS 位址＋CSRF token **每次 IDE 啟動都變**；`new-conversation` 外部不可用（projectsStore nil）；probe 會真的送一則訊息（耗額度） | 呼叫時從行程清單探索（`antigravity_wake_command.py`）；喚醒走 send-message 到**既有對話**；注入端點也要過 probe |

---

## F. 流程／認知類（給稽核人員：這些是「人」的雷）

1. **先重現、後診斷。** governance 03 兩次錯誤初診都來自巧合推論
   （「加檔案就壞」→其實殘留早就在；「順序相依」→其實是並行洩漏）。
   兩次更正都**留在票裡沒有塗掉**——錯誤的推理過程本身就是稽核材料。
2. **先讀證據、後清除。** 第一次孤兒 lease 被直接刪掉，marker 裡的 owner
   身分（可直接指認建立者）跟著消失，多花一輪才查到根因。
3. **移除一層時，枚舉它的職責。** E10 根因：批次層被拿掉，它負責填的
   `review_instruction` 沒人接手 ⇒ 整條 handoff 喚醒結構性死亡。
4. **文件與登記處會漂移。** E1–E6 標 `IN_PROGRESS` 實已交付、governance 01
   票內 `DONE` 而登記列 `IN_PROGRESS`、README 曾宣稱尚不成立的能力
   （0.4.1 的 wake 宣稱，發行後更正並如實標注「已發行 zip 仍帶此缺陷」）。
   稽核時**以票內 closure 證據為準**，登記列僅供索引。
5. **一次的失敗不是缺陷、也不是健康。** 有一筆無法重現的單次失敗
   （governance 03「unexplained observation」）——記錄、不解釋、不掩蓋。

---

## 快速對照：族群 → 防回歸所在

| 族群 | 討厭的測試（動它前先讀對應票） |
| --- | --- |
| 權限鑄造／別名回流 | `test_review_correction_regressions.py` |
| 跨行程恰好一次 | `test_review_return_concurrency.py` |
| 孤兒 lease 揭露 | `test_aaa_runtime_root_guard.py` |
| 發行 pin 漂移 | `test_release_pin_guard.py` |
| 全鏈整合 | `test_whole_chain_qualification.py`（gated） |
| handoff 喚醒鑑別 | `test_event_runner_qualification.py` R3（gated） |
| worktree 包含性 | `test_worktree_containment.py` |
| 一鍵安裝可讀拒絕 | `test_one_click_installer.py` |
