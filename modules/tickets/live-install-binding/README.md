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
| L1 | Root layout + durable stores | `JohnnyRootLayout`, file-backed install journal and uninstall ledger implementing the frozen Ticket 11/12 ports | `CLOSED` — `0381939`; 9 tests / 16 subtests |
| L2 | Real venv effect port | `py -3.11` venv plus `pip install --require-hashes` from the approved lock; finite subprocess failure semantics | `CLOSED` — `83b3636`; 5 tests / 9 subtests; real paths proven in L7 |
| L3 | Payload + launcher ports + entry | Digest-verified extraction, launcher copy, `johnny_router_entry.py` | `CLOSED` — `fc4d25f`; 8 tests / 2 subtests |
| L4 | Registration readback | Post-install typed proof through the real entry chain | `CLOSED` — `5fec8d5`; 3 tests / 5 subtests |
| L5 | install.ps1 live wiring | Stdlib bootstrap → hash-locked venv → typed composition on the venv interpreter; `LIVE_INSTALL_NOT_AUTHORIZED` retired | `CLOSED` — `8771c0c` + module-context fix `dd8d959`; 6 tests; ps1 parse pass |
| L6 | Uninstall live wiring | `johnny-router uninstall` composes the real Ticket 12 transaction over marker-proven state; bookkeeping and empty root cleared | `CLOSED` — `eea61ec`; 4 tests |
| L7 | End-to-end qualification | Clean-clone bundle → real venv with real locked downloads → tampered-pin rejection → full install chain → entry self-proof → real uninstall to zero residue | `CLOSED` — gated `JOHNNY_LIVE_QUAL` run: Q1–Q5 `5 passed` (2026-08-19); staging/workspace residue zero; clone-build fix committed after a real `SOURCE_DIRTY` catch |
| L8 | Owner real-machine smoke | Owner runs install → status → uninstall on the real per-user root | `CLOSED / OWNER_EXECUTED` — 2026-08-19: first run caught CR-L8-01, second run on candidate `bb95089` (digest `f5791d93…`) green end to end: `INSTALLED` (receipt `receipt-live-20260819090130`) → status `OK 0.4.0` → launcher uninstall `REMOVED`, `root_deleted`, `ZERO_RESIDUE` |
| L9 | One-click wrapper (`johnny-install.cmd`) | Digest-pinned double-click entry delegating to `install.ps1`; see [`l9-one-click-wrapper.md`](l9-one-click-wrapper.md) | `OPEN` — ticketed 2026-08-19, awaiting named implementation owner |

Full suite after closure: `849 passed, 5 skipped (gated qualification), 2665 subtests`;
`mypy --strict` clean over every new module and test.

## CR-L8-01 — venv self-deletion lock (caught by the owner smoke, as designed)

The first owner run proved install and status, then hit `REMOVAL_FAILED` on uninstall: the
live CLI ran on the owned venv's python, which locks its own executable and loaded native
modules, so the venv could not delete itself. The in-process qualification could not see
this class. Fix: the launcher's uninstall branch executes from a disposable copy of the venv
(owned venv stays unlocked), and the gated qualification now drives uninstall through the
installed launcher exactly as an owner does — rerun green `5 passed`. Secondary finding: the
failed partial `rmtree` destroyed ownership markers, so the retry correctly halted as
`FOREIGN_STATE_PRESENT`; the remnant (verified as same-day owned state via the ledger) was
removed by owner-authorized manual recovery to zero residue. Known recovery procedure: a
marker-destroyed root cannot re-prove ownership and requires owner manual removal.
