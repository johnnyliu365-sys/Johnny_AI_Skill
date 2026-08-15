# Handoff Artifact Tree

這是本專案對 target-owned handoff 台帳的設計期索引。它不是 live receipt、role-wake
registration 或 implementation authority。機器可讀 manifest、typed validator 與 event
adapter 必須在獨立 SPEC 核准、ticket 實作及 review 通過後才能成為正式能力。

## 標準目錄

```text
doc/handoffs/
  README.md
  index.json
  <year>/
    README.md
    index.json
    <feature>/
      README.md
      index.json
      <ticket-id>/
        README.md
        index.json
        <handoff-id>.json
```

若 target project 已有同用途位置，沿用既有位置並在 SPEC 記錄 exact mapping，不建立平行
台帳。每個 index 只列直接子節點 metadata；Router 只解析一條 exact path。

## Design branches

| Child ID | Kind | Revision | Lifecycle | Reference |
| --- | --- | --- | --- | --- |
| `HANDOFF-YEAR-2026` | `PARTITION_INDEX` | `design-01` | `ACTIVE` | [`2026/README.md`](2026/README.md) |

正式 `index.json` 不在架構階段偽造。它必須由核准 ticket 依
[`modules/spec/receipt-bound-role-supervision.md`](../../modules/spec/receipt-bound-role-supervision.md)
的強型別契約建立並驗證。

## Invariants

- committed exact leaf 才能成為 handoff 證據；工作樹、聊天與截圖不是 authority。
- ordinary source commit 不喚醒角色。
- reserved handoff path 的無效聲明只能產生 sanitized fault，不能成為可信 payload。
- sealed leaf 不原地修改；correction 建立新 leaf 並保留前一 leaf reference。
- 插件拔除不刪除此樹，也不要求接手者沿用 Johnny。
