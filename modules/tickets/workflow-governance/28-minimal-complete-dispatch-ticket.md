# 28｜最小且完整的派工票面

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN`；Owner 2026-10-18 改進清單項目 03 的獨立切片 |
| Authority | 既有 `PRD-20260805-009`／`CHG-20260805-009`、`modules/spec/workflow-governance.md` AC 2–5；本次 Owner 要求派工來源完整、最小，不新增需求身分 |
| Source baseline | 本票所在控制面 commit；獨立實作 worktree |
| Implementation language | Markdown 模板與 Python 3.11 驗證 |
| Implementation owner / reviewer | 分席；Reviewer 不改實作者 worktree |
| Profile | `COMPACT`；模板欄位及固定情境，不觸及產品／外部 effect |

## 邊界宣告

```johnny-boundary
modify = modules/tickets/TEMPLATE.md
create = tests/test_ticket_template_contract.py
forbid = modules/spec/
forbid = doc/requirements/
forbid = skills/
```

新測試檔只負責既有 ticket template 的契約，不建立另一套 Ticket Parser、Router
或審批流程。不得為每個功能重建同類測試工具。

## Objective／可觀察契約

既有 `specification-ticketing.md` 與 `ticket-decomposition.md` 已列完整派工要素，
只補 `modules/tickets/TEMPLATE.md` 缺的精確位置，不複製政策正文。完成的單票能從
核准來源取得 Expected，不使實作者猜業務規則。實作者發現新的業務決定必須回
`CHANGE_DETECTED`，而不是自寫 Expected。Bug、補測試與同功能返工沿用原需求
身分／revision，是否真正變更需求仍由既有 Change Control 決定。

## Work／驗收

1. 在模板既有欄位附近補最小填寫槽：核准契約來源與 revision、具名輸入→輸出／
   狀態／錯誤、可觀察 Expected、精確 modify/create/delete/forbid、依賴及其狀態、
   正常／失敗／邊界驗收、停止條件、獨立 reviewer 與回件。可直接指向已有同義
   欄位，不應重複新增第二份值。
2. 補一句需求身分重用：缺陷修正／補測試／同功能返工不自行建立第二份 PRD；
   實際產品需求改變回既有 Requirement Change，票內不得核准自身變更。
3. 在唯一新測試檔做可重跑的模板結構與固定情境回放：正常的前端票能找到
   已核准 Expected、輸入輸出、失敗／邊界與 reviewer；拿掉任一關鍵槽即紅。
   新業務決策缺來源的情境預期 `CHANGE_DETECTED`，不得讓實作者自行填值。
   這是模板契約驗證，不得宣稱已攔下所有舊票或完成 Host dispatch admission。

Acceptance：既有模板欄位不被刪減；新增文字不含特定專案、票號、SHA 或模型名；
新測試檔責任單一且可由 Reviewer 對缺 Expected 與缺 stop condition 做反向突變。
Run：`python -m pytest tests/test_ticket_template_contract.py -q`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、完整 candidate SHA、變更檔、
測試與反向突變目標、仍缺的真正派工准入能力。實作者不整合、不推送。
