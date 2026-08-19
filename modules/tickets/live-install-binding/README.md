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
| L9 | One-click wrapper (`johnny-install.cmd`) | Digest-pinned double-click entry delegating to `install.ps1`; see [`l9-one-click-wrapper.md`](l9-one-click-wrapper.md) | `CLOSED` — first delivery `7613aeb`, two P1 corrections applied. R1–R3/R5 by test (6 tests); R4 real-artifact chain executed by the control plane on the released 443,765-byte zip: digest `f67047f4…` verified → `install.ps1` extracted → dependency plan displayed → `INSTALL` gate reached → non-interactive run ended `USER_DECLINED` exit 2, no stray `install.ps1` beside the wrapper |
| L10 | Release pin guard | The wrapper's pinned name is proven against the single declared plugin version, and a release preflight compares its pinned digest to the built artifact | `CLOSED` — 9 tests incl. gated real-artifact `MATCHED`; a version bump that forgets the wrapper turns L10-R1 red |

Full suite after closure: `849 passed, 5 skipped (gated qualification), 2665 subtests`;
`mypy --strict` clean over every new module and test.

## 0.4.2 owner smoke on a second machine (2026-08-19, OWNER_EXECUTED)

The owner installed the published `v0.4.2` release on a **different machine**
from the one that carries the development checkout, through the one-click
wrapper alone. This is stronger evidence than L8: nothing on that host came
from a source tree.

Observed, in order:

- The wrapper verified the bundle and printed
  `Bundle archive SHA-256: 90fd1579b6279cc0fe552dc0b5ad679a41dfe40077e77ee05f75fed84361998e`,
  equal to the approved release digest.
- `Control Python probe: Python 3.11.9`, then the exact six-entry dependency
  plan with per-artifact digests.
- The owner typed `INSTALL`; the install completed.
- Re-running the wrapper to check whether the install had succeeded was
  correctly refused with `{"code": "VENV_ALREADY_PRESENT", "status": "BLOCKED"}`
  and exit 2, without touching the existing runtime.
- That refusal was **readable**: the console held on the localized pause prompt
  instead of closing. This is CR-L9-01's fix meeting its real case, on the
  exact path it was written for.
- `johnny-router.ps1 status` returned
  `{"launcher_present": true, "ledger_present": true, "plugin_version": "0.4.2", "status": "OK", "venv_present": true}`.

**Update 2026-08-20:** now exercised. Upgrading to 0.4.3, the owner ran the launcher uninstall on that same second machine: `REMOVED` with all five components listed (`PLUGIN_PAYLOAD`, `VENV`, `LAUNCHER`, `QUEUE`, `TELEMETRY`), `root_deleted: true`, `remaining: []`. The 0.4.2 lifecycle is owner-verified end to end on a host with no development checkout.

Follow-up recorded, not a defect: the plugin deliberately does not modify
`PATH`, so `johnny-router` is not a global command and the owner initially
could not find the installation. The launcher is invoked by full path at
`%LOCALAPPDATA%\JohnnyRouter\launcher\johnny-router.ps1`. The README's
removal instructions show the bare command name, which reads as if it were on
`PATH`; worth a documentation pass.

## 0.4.3 owner upgrade smoke on the second machine (2026-08-20, OWNER_EXECUTED)

The full upgrade path, exercised by the owner on the host with no development
checkout: launcher uninstall of 0.4.2 (`REMOVED`, five components,
`root_deleted: true`, `remaining: []`), release-asset download, one-click
wrapper with the digest verified against the approved
`016e466d96f664f80ffaaa02712eb72ef675cdb39fba500a3e055a51ff38771e`, `INSTALL`
confirmation, and

```json
{"launcher_present": true, "ledger_present": true, "plugin_version": "0.4.3", "status": "OK", "venv_present": true}
```

Three releases, three owner-verified installs on that machine; 0.4.2's full
lifecycle closed end to end on the way. The installed runtime now carries the
complete loop CLI: `dispatch`, `runner subscribe`, `review`.

## CR-L9-01 — blocked exits were invisible to a double-click user (control-plane review)

The first delivery exited straight out of every `BLOCKED` path. Explorer closes the console
the moment a `.cmd` ends, so the digest refusal this wrapper exists to deliver was never
readable: the window flashed and vanished. Every exit now holds the console first, pinned by
`BlockedPathVisibilityTests`, which asserts structurally rather than matching the localized
pause prompt (that would bind the test to the host codepage). Removing any one `pause` turns
that cell red.

Second correction: the recorded R4 evidence used a synthetic two-file zip with the pinned
digest rewritten to match, which proves the mechanism but never exercises the real artifact —
precisely where the control-plane probe had found `tar -xf` failing. That cell is now labelled
a mechanism smoke, and the real-artifact chain is recorded above as a control-plane execution,
following the L8 `OWNER_EXECUTED` precedent. `.gitattributes` was also narrowed back to the
authorized scope (`*.cmd`/`*.bat` CRLF); the repo-wide `* text=auto` rule was measured to cause
no digest regression but was outside this ticket's frozen scope.

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
