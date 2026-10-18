# 41｜既有需求與治理 SPEC 的限定修訂整合

| 欄位 | 內容 |
| --- | --- |
| State | `DESIGN_LOCAL_COMPLETE / CLEANUP_CONFIRMED / RUNTIME_NOT_EFFECTIVE`；僅設計基準與本票暫存 journal 閉合，不啟用 runtime |
| Authority | Owner 2026-10-18 限定修正授權；原 `PRD-20260815-022`／`PRD-20260805-009`、原兩份 SPEC；不新增 PRD、政策或效果權限 |
| Baseline | 本票落地後的精確控制分支 SHA，執行前固定；AC-17 原提案 `fa418b6d6ce3667abe3fa7b693b1034ec27cdaa9`，治理提案原內容 `1669e8e20f0a30894606e16f9ea1a10e4f0c5ba3` |
| Candidate | AC-17 `4531d00f7d979fb7cda567b4d584fde6f41698bb`；治理 `8eae1af4d6fbcab9b5c3f0f7f5b286a91cec7f78`；本地 replay 後須核對兩份 Git blob 相同 |
| Owner／reviewer | Root 受控本地整合；兩位未撰寫各自 SPEC 的獨立 reviewer 已對精確候選複驗 |
| Profile | `STANDARD`；無 Host 資格、target 寫入、push 或發布效果 |

沿用原需求與原 SPEC，不建立平行來源。本票只把已獨立複驗的兩份限縮
SPEC 修訂以精確 blob 落到本地控制線；原 PRD leaf 的授權狀態由控制面
另作具名文件對照，不把設計核准誤寫成 runtime 已啟用。

```johnny-boundary
modify = modules/spec/adaptive-project-orchestration.md
modify = modules/spec/workflow-governance.md
forbid = library/
forbid = skills/
forbid = tests/
forbid = doc/requirements/
forbid = template/
```

## 驗收與停止

1. 從本票固定 baseline replay 兩個受審候選；兩份落地 blob 必須逐一等於
   獨審通過的 `9c88d20eb8f6eba941d1b8a0fdc457d6be1cee48` 與
   `6fd8c3098f48be40c2cf05a03f8284c186163c08`。
2. 獨審對應 AC-17 `4531d00f` 與治理 `8eae1af4` 的完整修訂差異；舊候選的
   FAIL 不得冒充最後 PASS。兩者僅讓設計基準在版本證據落地後生效；
   既有一對一 validator、實作 Grant、Host qualification、正式效應均不提前切換。
3. `git diff --check` 與受影響的 lineage／artifact／Router／authority 聚焦測試
   必須通過。受控本地整合失敗時保留原 branch 與候選，不以重置或強推消除差異。
4. 回件列出兩個候選、兩個獨審結論、精確落地 blob、本地整合 SHA、未啟用能力。

新檔授權僅為本張 target-owned Ticket；無產品碼、測試碼、截圖或其他新檔。

## Closure evidence

兩份精確 blob 已於本地 `76d1f942e24975da28889c8b6ecee904c8ef3da0`
通過 document mutation gate 整合，獨審與測試見
[Ticket 41 review](../../../doc/reviews/workflow-governance/41-bounded-spec-correction-integration-code-review.md)。
這只完成文件設計基準；任何 runtime／Host／外部效果仍未驗收。

## 同票狀態綁定修正

首次整合的 SPEC 正文仍顯示「獨審待完成」，與已保存的 PASS 證據矛盾。
在原兩檔 boundary 內追加狀態綁定，獨立複驗後再由相同文件閘門
整合於 `cca2db71ba09fea1330fcdc0b93095024dfe4ce3`。目前 AC-17 SPEC
blob 為 `ffb5304ed0a53df5dbd0b7697e7e18cdfeb39c7c`，治理 SPEC
blob 為 `4323863f09ef89382e27eb1e4fc99ba652171da4`；兩者不改設計
驗收或 runtime 權限。詳細審閱與 journal 見原 [Ticket 41 review](../../../doc/reviews/workflow-governance/41-bounded-spec-correction-integration-code-review.md)。
本票唯一隔離 journal 的兩筆原始紀錄與 SHA-256 已先封存在 review，
再對精確檔案及兩個空父目錄做受限清理；路徑、無 reparse、唯一資產、
筆數與 digest 均於刪除前讀回，`Test-Path` 清理後為 false。先前遭 Host
policy 拒絕的嘗試仍保留為歷史，不再是現行 `CLEANUP_BLOCKED`。
本票只完成兩份 SPEC 的本地設計基準，runtime／Host／Grant 仍未生效。
