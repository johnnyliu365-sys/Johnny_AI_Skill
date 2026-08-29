# 功能集群 Context

每個功能集群在此目錄保留自身的已確認事實、來源追溯、責任邊界與待決事項；不得覆寫共同 `CONTEXT.md`。

## Managed direct-child partitions

This bounded index records partitions created or revised under the managed-artifact contract.
Legacy sibling migration is a separate, explicitly out-of-scope operation.

| Partition ID | Kind | Revision | SHA-256 | Lifecycle | Direct-child index |
| --- | --- | --- | --- | --- | --- |
| `CTX-PARTITION-ADAPTIVE-PROJECT-ORCHESTRATION` | `PARTITION_INDEX` | `REVISION_09` | `f8a615ba696db1196dd01c9932dea932ac8a2a0a3921addb6a98090a707133a1` | `ACTIVE` | [`adaptive-project-orchestration/README.md`](adaptive-project-orchestration/README.md) |
| `CTX-PARTITION-PLUGIN-ADOPTION-QUALITY` | `PARTITION_INDEX` | `REVISION_01` | `d8a62e7007447efa3a47dca9ba8bb6ab6ac013b2395cc4919c3593bfa12559dd` | `ARCHITECTURE_DRAFT / OWNER_EXACT_APPROVAL_PENDING` | [`plugin-adoption-quality/README.md`](plugin-adoption-quality/README.md) |
