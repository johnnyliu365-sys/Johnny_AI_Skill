# 04G — Disposable Windows Install Verification

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-01 through AC-05, AC-08 through AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Dependency | 04E provider and exact 04F artifact approved |
| Environment | Fresh exact 04E-qualified boundary; never target project |
| Implementation owner | `UNALLOCATED` |
| XSS | Inherit 04B/04F classification |

## Sole outcome

Install exact 04F artifact once and prove correct per-user owned state.
Uninstaller behavior is reserved for 04H; sandbox destruction is not proof.

## Acceptance cells

- Positive host produces `INSTALLED` only after payload/ledger/runtime/receipt
  physical readback.
- No host, foreign state, bad manifest/digest/root, missing capability,
  process/config/filesystem failure or interruption never false-succeeds.
- Admin/system/arbitrary/prefix-confusable/target-project and indirect bypass
  fail before effect.
- Target repositories remain byte/Git unchanged; Secret/raw Context absent; one
  install-guard reverse mutation turns red and is restored.

Report binds environment, staged source and artifact digests plus fresh facts.
