# 44｜需求版本關聯的本地相容驗證

| 欄位 | 值 |
| --- | --- |
| State / Closure | `DOCUMENT_REVIEW_PENDING` / 44-L1–L4 revision01 |
| Authority | `batch-checklist-local-20261018`，清單03/11/12；原 PRD-20260815-022／CHG-20260815-022、adaptive-project-orchestration AC17 requirement-identity reviewed design baseline；原PRD不新增 |
| Grant | Root delegated `grant-wg44-lineage-local-20261018`；文件獨審通過後限本地pure相容建置 |
| Baseline | source101e16ad25799d2a9b3158a8afb9782bc836a5a3；實作從本票已受審文件commit，Root讀回source parity及exactleaf |
| Roles | Root control；`/root/lineage_compat_impl` gpt-6-luna/xhigh；不同席 `/root/lineage_compat_review` gpt-6-sol/high；當下工具availability及既有同類pure實作證據選定，非名稱授權 |
| Workspace | `.worktrees/skill-improvement-44-lineage` / `codex/skill-improvement-44-lineage`；review `.worktrees/skill-improvement-44-review`；先核Git/clean/非reparse containment |
| Profile / limits | STANDARD，純資料相容驗證、無授權或外部effect；命令累計300s／單次90s、initial+一次correction、network=0、helper=0。歷史耗用保留 |

```johnny-boundary
modify = library/workflow_router/requirement_lineage.py
modify = tests/test_workflow_requirement_lineage.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/router.py
forbid = library/workflow_router/profile.py
forbid = library/local_orchestration/
forbid = doc/
forbid = modules/
forbid = skills/
forbid = template/
```

## 單一結果及相容邊界

沿用RequirementLineageGate，在同一模組增加明確版本化的
`validate_revision_history` 純方法：驗證一個既有PRD的有序revision/CHG關聯，回
candidate metadata；不提供建立/改寫PRD、Grant、索引遷移或啟用新規則的操作。
現有`validate`、所有一對一資料/測試、archive resolver、public imports不變。
舊規則只有在完整migration/Host qualification及正式activation後才可切換，本票
絕不更改它。純方法不是第二套授權引擎，只有關聯資料驗證責任。

重用現有RequirementId、RequirementChangeId、RevisionDigest、EvidenceDigest及
RequirementLifecycle／strict RouterModel；不改巨大contracts.py，不造Resolver。
同模組最少型別：

- `RequirementRevisionLink`：change_id、from_revision、to_revision、approval_ref
  （OpaqueMetadataId）、approval_digest（EvidenceDigest）。from/to必須不同，
  approval非空／非零digest；它只引用外部核准，不證明核准者身份。
- `RequirementRevisionHistory`：prd_id、initial_revision、effective_revision、
  links（tuple[RequirementRevisionLink,...]）。欄位strict、frozen、extra forbid。
- `RequirementRevisionHistoryResult`：scope固定CANDIDATE_ONLY，valid bool、
  reason為None或有限 `DUPLICATE_CHANGE / BROKEN_REVISION_CHAIN / EFFECTIVE_REVISION_MISMATCH`。
  valid iff reason None；不存在effect/creation授權欄位。

順序規則：空links只准initial==effective；每一筆from等於當前revision、to不可為
已出現revision，CHG ID不能重複；終點必須等於effective。同PRD可有多個獨立CHG，
CHG日期/編號不需等於PRD後綴。一個CHG影響兩個PRD可各在各自選定history出現；
不得跨history作全域唯一錯誤推定。方法不掃全部tree、不猜批次關聯。

實作可先在本兩檔建真型別/constructor tests，獨審pin後再接pure方法。普通
constructor/roundtrip涵蓋wrongprimitive/empty/zero evidence/unknownfield；不cast、
Any、繞過constructor或把legacy pair當Grant。此票預算不新增任何正式寫入能力。

## Closure

- 44-L1：不改需求的bug/correction用同一空history回candidatevalid，沒有PRD/CHG
  建立效應；同PRD的兩個不同CHG revisionchain有效，舊一對一validator完整回歸。
- 44-L2：wrongfrom、cycle、重複CHG、錯終點具名拒絕；raw malformed DTO在constructor
  拒絕。不接受自報approved bool；approvalref/digest缺失拒絕，但明說不是trusted issuance。
- 44-L3：兩個history共享同CHG各自有效；只處理選定PRD，不拒絕合法跨PRD變更。
  空links且改effective拒絕。沒有新PRD、archive或文件效果；無配置啟用此candidate方法。
- 44-L4：真實方法移除鏈條檢查讓具名測試轉紅→精確還原；reviewer另改終點/重複
  判定轉紅→還原。strict、既有lineage suite全綠，不能刪舊suffix測試換取綠燈。

原因優先：逐筆先duplicate change，再chain/cycle；遍歷後effective mismatch。
既有source gate只保護其原named manifest，不為新方法降低其檢查或更改舊manifest。
若其module-wide限制實際阻擋合法純新增，由Root依同票影響修明精確測試，不任意放寬。

Run：`python -m pytest tests/test_workflow_requirement_lineage.py -q`；
`python -m mypy --strict library/workflow_router/requirement_lineage.py`；compile/import、
`git diff --check`。預期產品增量≤110行、tests≤120行，超量做結構審查不是壓縮。
新檔/依賴/截圖/永久測試產物=0；已有testhelpers沿用；TEST→A→B=N/A（無責任搬移）。
作者只commit自己worktree不自審／整合，Return candidate/files/checks/findings/
deviations/cumulative time/limits。獨審通過才既有document mutation gate本地整合。
owner/TTL/teardown：具名席位資產在review+evidence seal且已整合乾淨後normal移除，
Recovery或未整合候選保留。正式Host issuer/atomic consumption/index migration仍
未完成，本票不勾整項11，不push/release/deploy、不改其他專案。
