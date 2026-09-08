# 功能集群 Context

每個功能集群在此目錄保留自身的已確認事實、來源追溯、責任邊界與待決事項；不得覆寫共同 `CONTEXT.md`。

## Managed direct-child partitions

This bounded index records partitions created or revised under the managed-artifact contract.
Legacy sibling migration is a separate, explicitly out-of-scope operation.

| Partition ID | Kind | Revision | SHA-256 | Lifecycle | Direct-child index |
| --- | --- | --- | --- | --- | --- |
| `CTX-PARTITION-ADAPTIVE-PROJECT-ORCHESTRATION` | `PARTITION_INDEX` | `REVISION_09` | `f8a615ba696db1196dd01c9932dea932ac8a2a0a3921addb6a98090a707133a1` | `ACTIVE` | [`adaptive-project-orchestration/README.md`](adaptive-project-orchestration/README.md) |
| `CTX-PARTITION-PLUGIN-ADOPTION-QUALITY` | `PARTITION_INDEX` | `REVISION_01` | `bc9564c192e229e0c637aa094f62761d1e8c62223cb23d38fd238361a3fe478e` | `SEALED / WA_01_UIX_01_TICKET_OPENING_AUTHORIZED` | [`plugin-adoption-quality/README.md`](plugin-adoption-quality/README.md) |
| `CTX-PARTITION-LOCAL-INSTALLER` | `PARTITION_INDEX` | `REVISION_03` | `9cf9d5762f21a767eef48b99009cff525be29759cb4aac3180cbc940850b2f1e` | `SEALED / OWNER_APPROVED` | [`local-orchestration-installer/README.md`](local-orchestration-installer/README.md) |
| `CTX-PARTITION-CONTROLLED-VERIFICATION` | `PARTITION_INDEX` | `REVISION_05` | `0e590a1e7fd68bffabffdfd9913dd1529bbd74ed3ecdc80533a7a835e3f54643` | `OWNER_BOUNDARY_APPROVED / LAB_QUALIFICATION_PENDING / NOT_SEALED` | [`controlled-verification/README.md`](controlled-verification/README.md) |
