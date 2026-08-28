# ADR-20260828-033｜Atomic Conditional Replace capability gate

- 日期：`2026-08-28（Asia/Taipei）`
- 狀態：`ACCEPTED`
- 決策者：Project owner
- 關聯規格：`SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2`（Revision 12）
- 關聯需求變更：`PRD-20260828-045`／`CHG-20260828-045`
- 延續：`ADR-20260828-032` 的 RWW6 cross-writer preservation。

## 背景

R09B2 的兩個非整合候選以 final digest check 加普通 `os.replace`／`unlink` 實作 mutation。
對抗性證據證明 uncooperative writer 可在最後 check 後、syscall 前寫入，接著被候選覆寫或
刪除。這不是 recovery policy 的小缺口，而是 final mutation primitive 的能力缺口。

## 決策

1. RWW6 保持不變。Runtime only on a proven `AtomicConditionalReplace` capability may execute a
   managed target mutation.
2. Capability proof is per exact Windows/Linux + filesystem backend + current abstraction tuple.
   Its result is `YES`, `NO` or `CONDITIONAL`; `YES` needs an actual native primitive whose final
   mutation is conditional on the target still holding the previously observed identity.
3. A pre-check followed by `os.replace`, `rename` or `unlink` is explicitly insufficient. Advisory
   lock is cooperating serialization, never the proof for a lock-ignoring writer.
4. `CAP-RWW6-01` investigates native primitive, race model, failure semantics and adversarial
   post-check reproduction for Windows, Linux and the current abstraction. It makes no R09B2 source
   correction and no runtime write capability available.
5. Unproved platform/backend combinations fail closed and do not execute the R09B2 write path. If
   no supported filesystem proves the capability, architecture/SPEC makes the second decision.

## Consequences

- `f99d836` remains non-integrated defect evidence; no further implementer correction is allowed.
- A future R09B2 implementation may use only an exact CAP evidence record marked `YES`, or a
  `CONDITIONAL` record after runtime detection proves the stated constraints.
- Absence of proof yields an honest stopped state rather than a best-effort cross-writer claim.
