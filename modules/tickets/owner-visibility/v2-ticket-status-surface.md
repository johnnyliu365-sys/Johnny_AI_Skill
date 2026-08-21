# V2｜票狀態總覽介面

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理／基礎設施功能票；標準見 `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `modules/tickets/owner-visibility/v1-owner-status-surface.md`（V1 機制沿用之處；V2 只換掉三個 lane 的內容） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 無紀錄（早於本欄要求） |
| 實作語言 | Python 3.11（依 `CONTEXT.md` › 實作語言規範的統一後端語言） |
| 狀態 | `BLOCKED`（board 記為 `NEEDS_OWNER`；卡在「讀不到」區塊與 `IN_PROGRESS` 外觀未經 owner 核准——核准的樣張裡沒有畫，是實作時補的） |
| 共同基準 | `main` at `c1bb040`（v0.4.5 released） |
| 實作者 | UI implementation owner ＋ 控制面（兩半平行分工，見下方角色指派） |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | `library/local_orchestration/ticket_status_template.py`（UI）與 `library/local_orchestration/ticket_status_pipeline.py`（pipeline，控制面）及各自測試 |
| 禁止修改 | 對方負責的檔案（UI 不動 pipeline，pipeline 不動 template）；`v2-approved-mockup.html` 已核准的版面配置、色票與密度不得重新設計 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

owner 開一頁就能回答，不用終端機、不用讀 ticket 檔案：**哪張票在哪個階段、卡在哪個
commit、真的要接手時該對一個對話講什麼。** 設計已由 owner 核准：
[`v2-approved-mockup.html`](v2-approved-mockup.html)。

V1 建的是一個「工人」板，owner 要的是「票」板；V1 的機制留下，三個 lane 換掉。

**一條規則凌駕版面：短清單不能是因為讀失敗才短。** 如果 pipeline 讀不到三個票檔，
頁面要顯示讀得到的那些，**同時**明講有三個缺失、為什麼。owner 掃過一個五列頁面、沒看到
`NEEDS_OWNER` 列就會停止盯著看；如果缺的三個裡有兩個正等他，這頁造成的傷害比沒有頁面
更大。這與
`modules/tickets/workflow-governance/04-skill-implies-a-runtime-that-may-not-exist.md`
同一個缺陷——敘述沒發生的事，讓 owner 的信任被錯誤的完成敘事吃掉。開工前讀
`modules/tickets/PITFALL-REGISTER.md`；family C 是這個失敗換了件衣服。

## 實作範圍、依賴與 ticket elements

兩半在一個文件契約碰面，彼此不碰對方的檔案：

| 半邊 | Owner | 檔案 |
| --- | --- | --- |
| **UI**——頁面 | UI implementation owner（本票） | `ticket_status_template.py` 及其測試 |
| **Pipeline**——事實 | 控制面 | `ticket_status_pipeline.py` 及其測試 |

pipeline 產生一個純 `dict`（JSON 形狀、只用 stdlib 型別）；template 把這個 dict 轉成頁面。
兩者互不 import，下方契約就是完整介面，所以兩半可以同時開工。

pipeline 這半的規則：票的狀態必須來自票檔裡**宣告的、機器可讀的區塊**，不得解析 State
欄位裡的英文句子猜狀態；沒有那個區塊的票進 `unreadable`，不得用猜的。commit 與 subject
來自對票檔路徑跑 `git log -1`，所以「這張票卡在哪」由 repository 回答，不靠人記得更新一行。

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：UI 半邊由 UI implementation owner 負責；Pipeline 半邊由控制面
  直接負責——兩者在各自 worktree 平行工作，只透過下方「公開契約」交會。
- reviewer：控制面（Opus 5）；與 UI implementation owner 不同 worktree。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

- UI 組合邊界（screen／layout／component）：`ticket_status_template.py` 的
  `def render(document: dict) -> str`，純函式，接收 pipeline 產生的 dict、輸出完整
  HTML 字串，無元件化框架。
- Composition Root 與依賴生命週期：無執行期依賴注入容器；`render` 無狀態，呼叫方在狀態
  變化時重新呼叫並整份覆寫輸出檔（原子寫入由呼叫端負責，非本票 UI 半邊範圍）。
- 注入的具名介面：`document`（下方公開契約）是唯一輸入，沒有 API、state、navigation、
  clock、feature flag、analytics、i18n、權限等注入面。
- production binding 與 test fake／stub：production 呼叫方讀 pipeline 的即時
  `build_document()` 輸出；測試以固定樣本 [`v2-document-sample.json`](v2-document-sample.json)
  取代即時管線輸出，所以渲染器是對它實際會收到的資料測的。
- 元件輸入／輸出、loading／empty／error、權限與可存取性驗收：`unreadable` 非空時頁面
  顯著陳述（V2-U4）；每個可為 null 的欄位都要能渲染完整列而不拋例外（V2-U3）；無 loading
  狀態（靜態渲染，非非同步）；無權限概念（單一 owner 本機頁面）；light／dark／system 三態
  皆須可解析（V2-U7）；必須能用 Explorer 雙擊以 `file://` 開啟，故無 build step、無
  fetch、無 ES modules、樣式全部 inline。

- 實際原始碼路徑：`library/local_orchestration/ticket_status_template.py`（UI）、
  `library/local_orchestration/ticket_status_pipeline.py`（pipeline）
- 公開契約／資料模型：

```text
document
├─ generated_at   str   ISO 8601 with offset
├─ head           {branch: str, commit: str}
├─ release        {version: str, commit: str} | null
├─ rollback       {commit: str} | null
├─ tickets        [ticket, …]        排序：NEEDS_OWNER 優先，其餘在後
└─ unreadable     [{label, path, reason}, …]   讀不到的來源

ticket
├─ id              str        如 "V1"、"E14"
├─ module          str        票所在資料夾
├─ title           str
├─ state           "NEEDS_OWNER" | "REJECTED" | "DONE" | "IN_PROGRESS" | "APPROVED"
│                  DONE 是完成但還沒裁決；APPROVED／REJECTED 是兩種裁決。完成不等於核准。
├─ reason          str | null   NEEDS_OWNER／REJECTED 必填，其餘不得填
├─ stages          [{ref: str, label: str, state: "DONE"|"OPEN"}, …]
├─ commit          {sha: str, subject: str} | null
├─ released_in     str | null
├─ ticket_path     str
└─ handoff_command str        可直接複製使用，不必再填任何東西
```

所有字串都是**不受信任文字**，必須逃逸——票名與 commit subject 來自檔案與 git，含
`<script>` 的 subject 必須以字元形式渲染，絕不能變成標記。

## TDD 設計

1. 正常行為：`render` 用 `v2-document-sample.json` 重現核准樣張的欄位——id、stage
   refs、commit sha、handoff command 全部出現（V2-U1）。
2. 規則違反／輸入錯誤：未逃逸的不受信任文字（title、commit subject 內含 `<script>`、
   `"`）不得以標記形式進入輸出（V2-U2）；每個可為 null 的欄位（`commit`／
   `released_in`／`reason`／空 `stages`）都必須渲染出完整列而不拋例外（V2-U3）。
3. 外部失敗／fail-closed：`unreadable` 非空時頁面必須顯著陳述，反向突變拿掉該區塊要
   轉紅（V2-U4）；pipeline 讀不到來源一律進 `unreadable`，絕不用猜的（同族缺陷見上方
   「一條規則凌駕版面」）。
4. 回歸保護：五種狀態不看文字也能兩兩分辨（V2-U5）；stdlib-only 不變，AST 掃描比對
   `tests/test_owner_status_surface.py::DependencyTests`（V2-U6）；light／dark／system
   三態皆可解析、無 build step（V2-U7）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 不涉路徑比對 |
| 2 | null／空字串／陣列 | 是 | 見 V2-U3：`commit`／`released_in`／`reason` 為 null、`stages` 為空陣列 |
| 3 | 權限繞過 | 否 | 單一 owner 本機頁面，無多使用者權限模型 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 否 | 純渲染頁面，不是 API，無對外錯誤碼 |
| 6 | 例外是否會拋出 | 是 | 每個可為 null 的欄位、以及含惡意標記的文字，都不得讓 `render` 拋例外或中斷 |

## 完成定義與證據

| Ref | 要求 | 證據 |
| --- | --- | --- |
| V2-U1 | `render` 重現核准樣張中的欄位 | 用 `v2-document-sample.json` 渲染並斷言 id、stage refs、commit sha、handoff command 全部出現 |
| V2-U2 | 不受信任文字被逃逸 | 渲染含 `<script>` 與 `"` 的 title 與 commit subject，斷言兩者都不以標記形式出現 |
| V2-U3 | 每個可為 null 的欄位都可以是 null | 渲染 `commit`／`released_in`／`reason` 皆 null、`stages` 為空的票，斷言仍產生完整列且不拋例外 |
| V2-U4 | `unreadable` 非空時被顯著陳述 | 斷言頁面明講；反向突變拿掉該區塊要轉紅 |
| V2-U5 | 五種狀態不靠文字也能兩兩分辨 | 對區辨屬性或 class 的結構性斷言，不是對文案 |
| V2-U6 | 只用 stdlib | AST 斷言無第三方 import，比對 `tests/test_owner_status_surface.py::DependencyTests` |
| V2-U7 | light、dark、未標記的 system 三態皆可解析 | 每個顏色都是 bare `:root` 上的 token；沒有顏色只定義在 media query 或 `[data-theme]` 區塊內；`body` 有明確 token 背景 |

- **反向突變證據**：V2-U4 已執行——拿掉 `unreadable` 區塊，5 個 cell 轉紅（區塊本身、計數、位置在票列之上、有票且同時有失敗的情況、family-C cell）；另單獨把空清單守衛改成忽略失敗，恰好 1 個 cell 轉紅。皆還原轉綠。
- **缺陷修正** baseline-red：不適用（新行為，非缺陷修正）。

## 正式環境移植 SOP

不適用（本票只產生一個由呼叫端寫入 per-user Johnny root 的靜態頁面；無 migration、無新增環境變數）。

## 完成回寫

- 實際檔案：`library/local_orchestration/ticket_status_pipeline.py`、`ticket_status_template.py`、`ticket_status_publish.py` 與三者的測試
- commit：管線與接線 `f3a2981`／`2abcae3`；UI 半部 `a8f0ddf`；五狀態與配色見 V2-S1~S4
- WorkProgress：不適用

```johnny-status
id = V2
title = 工單狀態頁
state = APPROVED
stage = D | 設計核准 | DONE
stage = U | UI 樣板 | DONE
stage = P | 資料管線 | DONE
stage = W | 接線 | DONE
```
