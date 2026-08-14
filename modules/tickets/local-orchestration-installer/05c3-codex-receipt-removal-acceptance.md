# 05C3 — Codex Receipt Removal Acceptance

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06, AC-07 and AC-08 |
| Revision | `02` |
| State | `PLANNED / UPSTREAM_MARKETPLACE_SOURCE_GAP / BLOCKED_BY_05C2C3` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C3-01` / A1-A8 |
| Dependency | 05C2B, 05C2C1 and 05C2C2 integrated; 05C2C3 marketplace-source truth must be independently approved and integrated |
| Profile / XSS | `STANDARD`; one implementation owner, no helper / `XSS_NOT_APPLICABLE` |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## Reserved responsibility

Using only the integrated project-owned disposable staging lease and oracle,
prove `register -> receipt -> remove -> fresh absence -> replay` end to end.
The same transactions must preserve seeded foreign state/payloads and two
external sentinel repositories byte-for-byte with unchanged Git porcelain.

## Frozen behavior pending dependency readback

- Acceptance-only staging/test changes; no new product behavior.
- One fresh success transaction produces the actual integrated receipt. The
  exact receipt is then consumed by 05C1/05C2B through an admitted oracle port.
- First removal returns `REMOVED`, exact owned plugin/marketplace/logical and
  physical payload state is absent, and second removal returns mutation-free
  `NOT_INSTALLED`.
- Foreign prefix-similar marketplace/plugin records and payload bytes remain
  exact across success, removal and replay.
- Existing and empty external sentinel repositories remain byte-identical and
  Git-clean. No target-project path enters a product DTO or effect request.
- Reverse receipt binding, remove order, each of three absence conjuncts,
  replay zero-removal and both isolation gates independently.
- This contract-staging evidence does not by itself claim live-host
  `SUPPORTED`; that projection still requires the separately approved host and
  disposable-Windows gates fixed by the SPEC.

## Revision-02 dependency readback

The exact integrated flow was exercised in one project-owned disposable lease:
registration returned `RegistrationSuccessAccepted`, receipt conversion returned
`CodexReceiptRemovalReady`, and adapter admission returned
`CodexCompensationOracleAdapter`; nevertheless the first removal returned
`UNINSTALL_BLOCKED / PRE_REMOVAL_EVIDENCE_INVALID` before either remove call.
The exact lease was removed and no runtime residue remained.

Root cause is an upstream typed-evidence gap. `OracleAction.ABSENCE` can return
`OracleAbsent` only after owned state and payloads are gone; coherent owned
presence currently collapses into `OracleBlocked / COMMAND_INVALID`. The
compensation adapter therefore cannot distinguish exact installed-path presence
from an unproved dependency failure, and 05C2B correctly refuses to treat that
failure as residue. Mapping generic blocked/error results to presence, weakening
`UNPROVED`, or skipping pre-proof is forbidden.

05C2C1 adds exact staging-oracle installed-path presence evidence and admission;
05C2C2 maps only that admitted evidence to `absent=False`. This child will be
refrozen against both exact integrated APIs. No 05C3 implementation authority
exists now.

## Post-05C2C2 dependency readback

Guarded integration `bc97a42638540cb56e0b2b0c716bd93ddeb5dbba`
closed installed-path truth, but an exact disposable probe still returned
`UNINSTALL_BLOCKED / PRE_REMOVAL_EVIDENCE_INVALID` with zero removal calls.
The three pure observations were:

- plugin lists: installed `RESIDUE`, available `PROVED_ABSENT`;
- installed path: `RESIDUE`;
- marketplace: `MISMATCH`.

The marketplace list hard-codes source `oracle-source`, while the exact
receipt/manifest binds `marketplaces/acceptance-market`. Ticket 05C2C3 owns
only this staging source-truth defect. 05C3 remains non-dispatchable until
05C2C3 is independently approved/integrated and this ticket is revision-03
refrozen against the resulting exact API. Generic mismatch must never be
weakened to residue.
