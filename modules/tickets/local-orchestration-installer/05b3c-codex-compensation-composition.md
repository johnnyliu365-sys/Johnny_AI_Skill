# 05B3C — Codex Compensation Composition

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 compensation seam |
| State | `REVIEW_APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3C-01` / C1-C8 |
| Dependency | 05B3A and 05B3B1 integrated |
| Owner / worktree | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` / existing `workflow-implementer-2`; one new ticket branch from reviewed current main, no new worktree |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Compose the validated 05B3A capability with the reducer approved through 05B3B1: execute
only the planned operations in exact order, validate each returned observation
against the exact manifest, continue after every declared finite failure, and
return the reducer result. No runtime callable introspection is permitted.

Only the new coordinator module, its focused test and export-only root changes
are authorized. The integrated port and reducer modules/tests remain read-only.

## Frozen composition design

- Public composition accepts one exact admitted
  `CodexCompensationPortCapability`, one exact recursively revalidated
  `CodexCompensationPortRequest`, and one reducer plan. Null, text, container,
  malformed, forged-empty or request/plan identity-mismatched inputs return
  the existing metadata-only `COMPENSATION_BLOCKED / PLAN_INVALID` with zero
  operation calls.
- The coordinator must validate the plan through the public reducer boundary
  before effects. A valid no-compensation plan returns the reducer's exact
  no-op result with zero calls. A valid required plan is the sole case allowed
  to execute its exact ordered steps.
- Each operation receives the same exact validated port request. The mapping is
  fixed: `REMOVE_PLUGIN -> remove_plugin`,
  `REMOVE_MARKETPLACE -> remove_marketplace`,
  `PROVE_PLUGIN_LISTS_ABSENT -> list_plugins`,
  `PROVE_MARKETPLACE_ABSENT -> list_marketplaces`, and
  `PROVE_INSTALLED_LOCATION_ABSENT -> prove_installed_path_absent`.
- Exact removal proof type, status and revalidated manifest produce
  `CodexRemovalConfirmed`; every finite wrong/malformed/mismatched return
  produces `CodexRemovalFailed`. The loop continues through every later step.
- Plugin-list truth is computed independently for installed and available.
  Exact absence is `PROVED_ABSENT`; an exact manifest-identity target is
  `RESIDUE`; a same-plugin-ID entry whose plugin/marketplace/version/auth
  identity differs is `MISMATCH`; a wrong or recursively malformed list is
  `MALFORMED` for both truths.
- Marketplace-list truth uses the exact requested marketplace name and source.
  Exact absence is `PROVED_ABSENT`, an exact target row is `RESIDUE`, a
  same-name row with mismatched source is `MISMATCH`, and a wrong or
  recursively malformed list is `MALFORMED`.
- An exact installed-path proof with the exact revalidated manifest and literal
  `True` is `PROVED_ABSENT`; exact manifest plus literal `False` is `RESIDUE`,
  a foreign manifest is `MISMATCH`, and a wrong/recursively malformed proof is
  `MALFORMED`.
- Only expected finite returned values are normalized. `RuntimeError`,
  `MemoryError`, `KeyboardInterrupt` and `SystemExit` raised by an admitted
  operation propagate unchanged at that exact step; no broad catch converts or
  swallows them, and no later operation runs after an escaping exception.
- After all finite outcomes are collected, the coordinator calls the public
  reducer once with the exact tuple and returns its result without adding a
  second result algebra or raw diagnostics.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `C1` | Exact capability/request/plan admission is proven before effects. Null/text/container, malformed/forged-empty capability or request, request-manifest versus plan-request mismatch, stale/copy/constructed-invalid plan, and no-compensation cases are committed zero-call cells with exact finite results. |
| `C2` | All reachable authority pairs execute exactly the reducer's frozen step order. Both-authority calls exactly five operations; marketplace-only calls exactly four; no-authority calls zero. Every call receives the same exact request object. |
| `C3` | Each of the five operations independently returns one finite wrong/malformed value. The exact normalized failure observation is recorded, every later finite step still runs, and the final reducer result retains the correct residual authority and ordered reasons. |
| `C4` | Removal success versus wrong status/type/foreign manifest, plugin installed/available absence/residue/mismatch/malformed, marketplace absence/residue/mismatch/malformed, and installed-path absent/residue/mismatch/malformed each map to the exact reducer observation and metadata-only final result. |
| `C5` | Exact request/manifest binding is recursive and occurs before equality or serialization of supplied/returned malformed fields. Missing, `None`, empty, whitespace, list, dict and plain-object substitutions at every coordinator-owned manifest seam return finite results without caller trap invocation. |
| `C6` | Cross five operations with `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit`: all 20 exceptions propagate unchanged, the failing operation is the last call, and no broad catch or raw exception text reaches a result. |
| `C7` | Independently reverse exact step dispatch, continue-after-finite-failure, removal-manifest admission, independent plugin-list truth, and operation-exception propagation. All five isolated mutations turn their named committed tests red and are restored. |
| `C8` | Focused/full unittest, strict full-tree mypy, in-memory compile, source/scope/diff and tracked/ignored/cache readback pass. Implementation changes only the three authorized paths; the handoff commit changes only `doc/WorkProgressReport.md`. |

## Exact source and TDD boundary

1. New `library/local_orchestration/codex_compensation_composition.py`.
2. New `tests/test_codex_compensation_composition.py`.
3. Export-only `library/local_orchestration/__init__.py`.

The first red is the committed focused test failing with `ModuleNotFoundError`
before the coordinator exists. Tests use only admitted in-memory fake ports and
pure models; no process, filesystem, live Codex, host, target project or
network effect is authorized. No `Any`, `type: ignore`, broad catch, dynamic
member/signature inspection, `None` port, new dependency or historical-source
copy is accepted.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3C-01` |
| Handoff | `hnd_local_orchestration_install_05b3c_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b3c_20260812` / `rcpt_local_orchestration_install_05b3c_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b3c-20260812` / `q-local-orchestration-install-05b3c-20260812` |
| Side context | `scx-local-orchestration-install-05b3c-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; create only branch `codex/implementation-codex-compensation-composition-05b3c` from exact reviewed control baseline after dispatch. |
| Return | One exact-scope implementation commit, then one `doc/WorkProgressReport.md`-only handoff reserved as PRG-20260812-188. |

## Terminal independent review

Implementation `b44cb38bbdff181d7aef46feef7fc9db62ec1edb` and docs-only
handoff `6d7dd37095005b11d68e136d6687d402b5187c9e` are independently
`APPROVED / READY_TO_MERGE`. The reviewer reran focused 6/6, full 260/260,
strict mypy and in-memory compile over 116 files, C1-C6 adversarial probes,
and all five C7 isolated reversals. Exact ancestry, three-path implementation
scope, WPR-only handoff, integrated dependency blobs and zero residue passed.

This approval is limited to compensation execution and observation reduction.
Ticket 05B4 remains solely responsible for binding fresh registration
admission, exact receipt/proof/journal evidence and the 05S4 oracle to the
manifest; that downstream responsibility is not silently absorbed here.
