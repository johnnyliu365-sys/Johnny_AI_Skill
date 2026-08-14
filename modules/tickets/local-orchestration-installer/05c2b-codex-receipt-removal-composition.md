# 05C2B — Codex Receipt Removal Composition

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06 and AC-07 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `01` |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05C2B-01` / B1-B9 |
| Dependency | 05C2A independently approved and integrated |
| Profile / resource | `STANDARD`; one implementation owner, no helper; no parallel lane because the public observation contract is a serial dependency |
| XSS | `XSS_NOT_APPLICABLE`: typed Python orchestration only; no Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |

## Reserved observable outcome

Consume one exact 05C1 invocation and one admitted closed compensation port.
Fresh exact pre-removal absence returns mutation-free `NOT_INSTALLED`;
otherwise remove the exact plugin before the exact marketplace and return
`REMOVED` only after fresh conjunctive plugin/marketplace/path absence. Every
invalid, foreign or incomplete result is finite `UNINSTALL_BLOCKED`.

## Frozen behavior pending 05C2A readback

- Add one composition module, one direct test and export-only package-root
  changes. The final public names may be refrozen only against 05C2A's exact
  integrated API; behavior below may not expand.
- Build the request through 05C1 before port admission or any operation. Map
  05C1's `INVALID_INVOCATION`, `INVALID_RECEIPT` and `RECEIPT_MISMATCH` exactly.
- Admit the existing five-operation capability. Invalid capability is
  `INVALID_PORT` and performs zero calls.
- Pre-proof order is plugin list, marketplace list, installed-path absence.
  Normalize every result through 05C2A. Only exact absence of both plugin
  collections, the marketplace and installed path returns `NOT_INSTALLED`.
  Any owned residue proceeds to removal. Malformed, mismatched, unproved or
  foreign evidence blocks before remove calls.
- Mutation order is plugin removal then marketplace removal. A declared or
  invalid plugin result blocks before marketplace removal; a marketplace
  failure blocks before post-proof. Undeclared adapter exceptions propagate;
  no broad catch converts them to success or absence.
- Post-proof uses fresh plugin list, marketplace list and installed-path calls
  in that order. Only their exact conjunctive absence returns `REMOVED`.
- Partial retry with any residue never returns early `NOT_INSTALLED`; it repeats
  the ordered removal attempt and terminal proof. Completed replay returns
  `NOT_INSTALLED` with zero removal calls.
- The finite block enum is receipt-removal-specific and contains only
  `INVALID_INVOCATION`, `INVALID_RECEIPT`, `RECEIPT_MISMATCH`, `INVALID_PORT`,
  `PRE_REMOVAL_EVIDENCE_INVALID`, `PLUGIN_REMOVAL_FAILED`,
  `MARKETPLACE_REMOVAL_FAILED` and `POST_REMOVAL_EVIDENCE_INVALID`.
- No historical journal, fake plan, private import, duplicated response
  admission, raw output, optional port, `Any`, `type: ignore`, broad clear,
  dynamic lookup or new path authority is allowed.

## Reserved TDD closure

| ID | Required evidence |
| --- | --- |
| `B1` | First red is the missing new module; exact completed replay returns `NOT_INSTALLED` with list/list/path calls only. |
| `B2` | Owned plugin-only, marketplace-only, path-only and combined residue all proceed to exact plugin-before-marketplace removal. |
| `B3` | Pre-proof declared failure, malformed, mismatch and foreign-state matrices block before both removal operations. |
| `B4` | Plugin removal failure prevents marketplace removal; marketplace failure prevents post-proof; both use exact finite reasons. |
| `B5` | Fresh post-proof requires both plugin collections, marketplace and path absence; each missing conjunct blocks `REMOVED`. |
| `B6` | Completed replay is mutation-free; partial retry is not mistaken for completed replay and preserves ordered removal. |
| `B7` | Invalid invocation/receipt/identity/capability matrices are finite and zero-effect; trap descriptors/equality/serialization are not invoked before admission. |
| `B8` | Independently reverse remove order, all four absence conjuncts, replay zero-removal and failure short-circuit; each named test turns red and exact bytes restore. |
| `B9` | Focused/full serial unittest, strict full-tree mypy, in-memory compile, source sentinel, exact scope/diff, tracked/ignored/cache readback and topology pass. |

CodeReview.md path-prefix, permission, null-equivalent, token/identity, finite
error, exception and test-truthfulness defect classes must be marked applicable
or not applicable with evidence during refreeze. No implementation authority,
branch, allocation or receipt exists while this ticket is dependency-waiting.

## Reserved writable scope

1. `library/local_orchestration/codex_receipt_removal_composition.py`
2. `tests/test_codex_receipt_removal_composition.py`
3. export-only `library/local_orchestration/__init__.py`

No other source/test/document path, live Codex/host/target-project effect,
worktree creation, helper Agent, branch fan-out, package/install, push, release
or deployment is authorized. There is no numeric line criterion.
