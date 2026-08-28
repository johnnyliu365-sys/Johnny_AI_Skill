# ADR-20260828-032｜Recoverable managed-artifact runtime

- 日期：`2026-08-28（Asia/Taipei）`
- 狀態：`ACCEPTED`
- 決策者：Project owner
- 關聯規格：`SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2`（Revision 11 draft）
- 關聯需求變更：`PRD-20260828-044`／`CHG-20260828-044`
- 取代的未決缺口：R09B review 的 durable recovery、cross-writer preservation 與 resolver error policy。

## 背景

R09B 的 initial candidate 與唯一允許的 correction 都沒有成為 integration authority。第二輪
對抗性審查證明三個問題：持久 rollback/cleanup I/O failure 可以留下 candidate bytes；CAS
rejection 會以 stale baseline 覆寫外部 writer；以及 post-state resolver 的一般失敗與 raw
exception 缺少可執行的區分。以第三次修正補洞會違反 bounded convergence，也會把設計決策
藏在 implementation 中。

## 決策

### 1. Runtime-own recovery and a stopped state

`TransactionalManagedArtifactWriter` 的 successor 是唯一 transaction authority。它先在
worktree 對應的 private Git metadata path 建立並 fsync recovery record，再開始第一次目標
replace/unlink；record 以 canonical relative target identity、baseline/candidate digest、action
order、attempt count 與 opaque recovery reference 為主體，snapshot bytes 只存在同一 private
recovery boundary。它不是 target source、Git commit、Router metadata、log 或 plugin payload。

同一 recovered writer uses `exclusive-file-lock` to serialize cooperating runtime instances. The
lock is advisory by design, so every pre-write, post-write and rollback step independently compares
the current bytes with its expected baseline or its own candidate digest. A mismatch means the
runtime must not overwrite the conflicting bytes.

Rollback and temporary cleanup receive exactly two bounded attempts. If all baseline bytes/absence
and temporary cleanup are then proved, the transaction returns its normal finite rejection. If not,
the record and snapshots stay durable, the result is `RECOVERY_REQUIRED`, and every subsequent
`apply` first refuses with that state. A separately explicit recovery operation is the only route to
clear it: it repeats the same comparisons and proves restoration before deleting snapshots, while
retaining a metadata-only settled record.

### 2. Plugin/CLI is untrusted intent, Runtime is verification boundary

The plugin/CLI may present a typed intent but cannot provide authority by asserting a plan, a lock,
a path, a digest, a resolver outcome or a recovery status. Runtime independently validates plan
shape; repository baseline; normalized containment and reparse-point exclusion; exact pre-state
bytes/digests; per-effect compare-and-swap; candidate bytes/digests; canonical lifecycle/edge
post-state; and the recovery journal before every operation. No hook, host capability, receipt,
runner, queue or external call is introduced by this ADR.

### 3. Canonical-only artifact resolution

`ArtifactTreeResolver` already resolves a caller-supplied exact family/root/ordered-path/node tuple
without scanning siblings. That is the R09B post-state input. The runtime must construct and call
that canonical contract directly. R09B adds no string lookup. If a later boundary offers a shorthand,
it must collect its candidates in a bounded declared namespace and accept only cardinality one;
zero maps to not-found and more than one maps to ambiguity. It must never select the first candidate.

Expected resolver non-success is handled as its existing finite decision. A narrowly classified
runtime invariant exception at the resolver call boundary becomes the named sanitized
`RUNTIME_INVARIANT_FAILED` result only after recovery has completed; this is not a broad exception
catch and does not expose exception text.

## Consequences

- A runtime crash or persistent recovery failure is visible and blocks subsequent writes instead of
  masquerading as a clean all-or-nothing transaction.
- An uncooperative writer may leave the workspace in a recovery-required state, but is never erased
  by stale rollback. Human investigation/recovery is explicit evidence, not an automatic claim.
- The existing advisory lock is selected only for cooperating mutual exclusion; it is not represented
  as protection from arbitrary file writes.
- R09B must be replaced by a new, complete transaction closure. The previous candidate branches are
  preserved but cannot be rebased, merged or corrected again.
