# Receipt-bound Role Supervision Handoff Partition

此 feature partition 在架構階段只固定 future exact-leaf 路徑與責任邊界。SPEC 尚未取得
exact owner approval，因此目前沒有 ticket index、handoff leaf、receipt 或 wake authority。

核准後的 Reviewer 必須依 approved SPEC 將每張 ticket 建立為一個直接 child index：

```text
doc/handoffs/2026/receipt-bound-role-supervision/<ticket-id>/README.md
doc/handoffs/2026/receipt-bound-role-supervision/<ticket-id>/index.json
doc/handoffs/2026/receipt-bound-role-supervision/<ticket-id>/<handoff-id>.json
```

不得在此 README 複製 ticket、SPEC、progress、review 或聊天內容。
