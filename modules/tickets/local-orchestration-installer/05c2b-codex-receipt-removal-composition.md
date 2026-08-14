# 05C2B — Codex Receipt Removal Composition

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-06 and AC-07 |
| Change / PRD / Context | `CHG-20260808-011` / `PRD.md §15` / `doc/context/local-orchestration-installer/main.md` |
| Revision | `02` |
| State | `PLANNED / REFREEZE_COMPLETE` |
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

## Frozen public contract

- Add `codex_receipt_removal_composition.py`, its direct test and export-only
  package-root changes. Public names are exactly:
  `CodexReceiptRemovalCompositionBlockReason`,
  `CodexReceiptRemovalNotInstalled`, `CodexReceiptRemovalRemoved`,
  `CodexReceiptRemovalCompositionBlocked`,
  `CodexReceiptRemovalCompositionResult`, and
  `compose_codex_receipt_removal(invocation: object, port_candidate: object)
  -> CodexReceiptRemovalCompositionResult`.
- The two completion DTOs are strict frozen Pydantic models with only status
  `NOT_INSTALLED` or `REMOVED`. The blocked DTO is strict/frozen, has only
  status `UNINSTALL_BLOCKED` and the closed composition block enum. No result
  retains a port, callable, request, receipt, path, raw output or diagnostic.
- Build the request through 05C1 before port admission or any operation. Map
  05C1's `INVALID_INVOCATION`, `INVALID_RECEIPT` and `RECEIPT_MISMATCH` by
  explicit enum identity. Invalid invocation must not inspect the port
  candidate. Admit the candidate only through existing
  `admit_codex_compensation_port`; any rejected admission maps to
  `INVALID_PORT` and performs zero operations.
- Pass the single rebuilt 05C1 request object unchanged to every admitted
  operation. Never rebuild from the raw invocation after 05C1 succeeds.
- Pre-proof order is plugin list, marketplace list, installed-path absence.
  Normalize each already-returned value only through integrated 05C2A
  `observe_codex_compensation_operation`. Only exact `PROVED_ABSENT` for both
  plugin collections, marketplace and installed path returns `NOT_INSTALLED`.
  Any owned `RESIDUE` proceeds to removal. `MALFORMED`, `MISMATCH`, `UNPROVED`
  or observation rejection blocks before remove calls. Unrelated foreign
  marketplace/plugin/available entries are preserved foreign state, not owned
  residue; they remain acceptable only when 05C2A classifies the exact owned
  identity as `PROVED_ABSENT`.
- Mutation order is plugin removal then marketplace removal. A declared or
  invalid plugin result blocks before marketplace removal; a marketplace
  failure blocks before post-proof. Undeclared adapter exceptions propagate;
  no broad catch converts them to success or absence.
- Post-proof uses fresh plugin list, marketplace list and installed-path calls
  in that order. Only their exact conjunctive absence returns `REMOVED`.
- Partial retry with any residue never returns early `NOT_INSTALLED`; it repeats
  the ordered removal attempt and terminal proof. Completed replay returns
  `NOT_INSTALLED` with zero removal calls.
- Exact operation sequences are: completed replay `list_plugins`,
  `list_marketplaces`, `prove_installed_path_absent`; successful removal adds
  `remove_plugin`, `remove_marketplace`, then the same three fresh post-proofs.
  Plugin failure stops after call four, marketplace failure after call five,
  and any post-proof failure completes all eight calls but never returns
  `REMOVED`.
- The finite composition block enum contains only
  `INVALID_INVOCATION`, `INVALID_RECEIPT`, `RECEIPT_MISMATCH`, `INVALID_PORT`,
  `PRE_REMOVAL_EVIDENCE_INVALID`, `PLUGIN_REMOVAL_FAILED`,
  `MARKETPLACE_REMOVAL_FAILED` and `POST_REMOVAL_EVIDENCE_INVALID`.
- No historical journal, fake plan, private import, duplicated response
  admission, raw output, optional port, `Any`, `type: ignore`, broad clear,
  dynamic lookup or new path authority is allowed.

## TDD closure

| ID | Required evidence |
| --- | --- |
| `B1` | First red is the missing new module/public exports; exact completed replay returns `NOT_INSTALLED` with list/list/path calls only and the same rebuilt request identity. |
| `B2` | Owned plugin-only, marketplace-only, path-only and combined residue all proceed to exact plugin-before-marketplace removal. |
| `B3` | Pre-proof declared failure, malformed, mismatch and unproved matrices block before both removal operations; unrelated foreign entries coexist with owned absence and are not mutated. |
| `B4` | Plugin removal failure prevents marketplace removal; marketplace failure prevents post-proof; both use exact finite reasons. |
| `B5` | Fresh post-proof requires both plugin collections, marketplace and path absence; each missing conjunct blocks `REMOVED`. |
| `B6` | Completed replay is mutation-free; partial retry is not mistaken for completed replay and preserves ordered removal. |
| `B7` | Invalid invocation/receipt/identity/capability matrices are finite and zero-operation; invalid invocation leaves port traps untouched, and admission invokes no candidate descriptor/equality/serialization hook. Exact adapter exceptions propagate and stop subsequent calls. |
| `B8` | Independently reverse remove order, all four absence conjuncts, replay zero-removal and failure short-circuit; each named test turns red and exact bytes restore. |
| `B9` | Focused/full serial unittest, strict full-tree mypy, in-memory compile, source sentinel, exact scope/diff, tracked/ignored/cache readback and topology pass. |

CodeReview.md path-prefix, permission, null-equivalent, token/identity, finite
error, exception and test-truthfulness defect classes must be marked applicable
or not applicable with evidence. Path-prefix is not applicable because the
coordinator creates no path authority; permission/effect order is covered by
B1-B7; null/type/identity, finite errors and undeclared exceptions by B3-B7;
test truthfulness by B8-B9. No implementation authority exists until a separate
exact lane registry is committed.

## Reserved writable scope

1. `library/local_orchestration/codex_receipt_removal_composition.py`
2. `tests/test_codex_receipt_removal_composition.py`
3. export-only `library/local_orchestration/__init__.py`

No other source/test/document path, live Codex/host/target-project effect,
worktree creation, helper Agent, branch fan-out, package/install, push, release
or deployment is authorized. There is no numeric line criterion.

## Planned binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05C2B-01` |
| Workspace / handoff | `wsb_local_orchestration_install_05c2b_20260814_01` / `hnd_local_orchestration_install_05c2b_20260814` |
| Allocation / receipt | `aln_local_orchestration_install_05c2b_20260814` / `rcpt_local_orchestration_install_05c2b_20260814` |
| Correlation / question | `corr-local-orchestration-install-05c2b-20260814` / `q-local-orchestration-install-05c2b-20260814` |
| Side context | `scx-local-orchestration-install-05c2b-20260814-01` |
| Authority | Project-owner standing auto-continue `PRG-20260809-042`; freeze is not dispatch. |

05C2A dependency is exact integration
`e2e2fe986243fa64f7ce9a67903904310341597b`. Revision 02 closes the former
public-name and foreign-state ambiguity against the integrated 05C1 and 05C2A
contracts; it is a control refreeze, not a requirement change.
