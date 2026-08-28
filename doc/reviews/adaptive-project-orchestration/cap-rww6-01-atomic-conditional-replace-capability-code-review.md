# CAP-RWW6-01 — Atomic Conditional Replace capability review

| Field | Value |
| --- | --- |
| Review / ticket / closure | `REVIEW-ADAPTIVE-CAP-RWW6-01-ATOMIC-CONDITIONAL-REPLACE-CAPABILITY-01` / `TICKET-ADAPTIVE-CAP-RWW6-01-ATOMIC-CONDITIONAL-REPLACE-CAPABILITY` / `CLOSURE-ADAPTIVE-CAP-RWW6-01-ATOMIC-CONDITIONAL-REPLACE-CAPABILITY-01` |
| Baseline / candidate | `6953f1e49bc60e66a5f8a2ce9cfd879f0d606ece` / `5763caf5dc26e382dd8092545fde053063792a37` |
| Result | `APPROVED_EVIDENCE / INTEGRATED / AUTHORITY_PUSH_CONFIRMED / ALL_EXECUTED_TUPLES_NO / ARCHITECTURE_DECISION_REQUIRED` |
| Boundary | Only `tests/test_atomic_conditional_replace_capability.py` changed from the ticket baseline. No production source, existing regression test, ticket, SPEC, Context, ADR, plugin, provider or target runtime changed. |
| Model lanes | Terra/xhigh investigation owner; Sol/high reviewer; two isolated Terra/xhigh read-only evidence helpers. |

## Qualification evidence

| Exact subject | Native primitive / result | Race and finite outcome | Opaque evidence ref |
| --- | --- | --- | --- |
| Windows `10.0.19045` / NTFS | `MoveFileExW(MOVEFILE_REPLACE_EXISTING)` / `NO` | An external replacement before the native final mutation was overwritten; `FINAL_WINDOW_NOT_CONDITIONAL`. | `sha256:da095c5acc0eb0ce8df5b17bc0dc0cc77f7d05784221d1a44cc8209f445dc16b` |
| Linux `6.18.33.1-microsoft-standard-WSL2` / WSL DrvFS (`v9fs`/`9p`, `/mnt/c`) | `renameat2(RENAME_NOREPLACE)` / `NO` | The primitive was unavailable (`EINVAL`) on this exact tuple; target remained absent and the outcome was `PRIMITIVE_UNAVAILABLE_NO_EFFECT`. This is not a claim about ext4 or other Linux backends. | `sha256:304931044f2c73ca68560e38664e9e55a34c1d60eb7d5080b26e59db656a465d` |
| CPython `3.11.9` / NTFS abstraction | `NONE` / `NO` | A final-window audit at ordinary `os.replace` showed external bytes overwritten; `FINAL_WINDOW_NOT_CONDITIONAL`. | `sha256:51147bbb99213cf6a32afd2797c26cdc780f53699e6145b95c8999a0d4622e52` |

No executed tuple produced `YES` or `CONDITIONAL`. Therefore this review records a capability
boundary, not a runtime admission. R09B2 and both of its source candidates remain blocked.

## Review evidence

- Focused capability suite: `8 passed`.
- Strict type check and compile passed; baseline-to-candidate `git diff --check` passed.
- Transaction/race helper independently reproduced the three `NO` outcomes and found no remaining
  evidence defect.
- Platform/security helper independently verified exact Linux kernel/backend matching, no
  caller-asserted absence/write path, strict qualification-field consistency, opaque evidence shape
  and the test-only boundary; it found no remaining evidence defect.
- The reviewer counter-mutated the `NONE` primitive subject guard. The targeted qualification test
  failed (`1 failed`) because a Windows `NONE` primitive was then accepted; exact restoration made
  the full focused suite green again.

## Integration and continuation

`admit_document_mutation` returned `INTEGRATED` with candidate
`5763caf5dc26e382dd8092545fde053063792a37`. A non-force push followed by direct `origin/main`
readback matched that SHA. The required continuation is `ARCHITECTURE_DECISION_REQUIRED`: choose a
new architecture/SPEC direction for R09B2 or leave it stopped. This evidence does not authorize
another correction of `f99d836`, a production Atomic Conditional Replace adapter, target mutation,
publication, installation, release or deployment.
