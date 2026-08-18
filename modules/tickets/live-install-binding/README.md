# Live install binding ticket registry

| Field | Binding |
| --- | --- |
| SPEC / AC | `modules/spec/environment-capability-bootstrap.md` (`CONTROL_BOOTSTRAP` boundary) + Plugin Distribution Revision 02 AC-05, AC-06, AC-13 |
| Baseline | `v0.4.0` = `d1d20808a6586a33ecf755efe3aa72e6285ac968` (pushed; rollback point) |
| Authority | Owner-direct allocation, same mode as the plugin-distribution 10–15 closure line |
| Workload | `external_effects=LOCAL_HOST`, `uncertainty=KNOWN_DOMAIN` → derived `STANDARD`; L2 carries a supply-chain surface (locked-hash wheel installs) and is handled at `HIGH_ASSURANCE` review depth |
| Boundary | Per-user Johnny root only (`JOHNNY_ROOT` override honored everywhere); no admin, PATH, global-tool or target-project effect; downloads only after explicit user confirmation (granted for this line on 2026-08-19); every qualification runs in a disposable root |

Closure evidence is recorded per ticket in this file (STANDARD intensity: commit-per-ticket,
compact evidence rows; no separate leaf tree).

| # | Ticket | Sole closure | State |
| --- | --- | --- | --- |
| L1 | Root layout + durable stores | `JohnnyRootLayout`, file-backed install journal and uninstall ledger implementing the frozen Ticket 11/12 ports | `IN_PROGRESS` |
| L2 | Real venv effect port | `py -3.11` venv plus `pip install --require-hashes` from the approved lock; finite subprocess failure semantics | `PLANNED` |
| L3 | Payload + launcher ports + entry | Digest-verified extraction, launcher copy, `johnny_router_entry.py` | `PLANNED` |
| L4 | Registration readback | Post-install typed proof that runtime, venv and launcher exist and execute | `PLANNED` |
| L5 | install.ps1 live wiring | Confirmed plan invokes the real transaction; `LIVE_INSTALL_NOT_AUTHORIZED` retires | `PLANNED` |
| L6 | Uninstall live wiring | `johnny-router uninstall` composes the real Ticket 12 transaction | `PLANNED` |
| L7 | End-to-end qualification | Real bundle → real install into disposable root → readback → real uninstall → zero residue | `PLANNED` |
| L8 | Owner real-machine smoke | Owner runs install → status → uninstall on the real per-user root | `OWNER_EFFECT_REQUIRED` |
