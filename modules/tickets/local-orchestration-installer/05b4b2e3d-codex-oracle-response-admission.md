# 05B4B2E3D — Codex Oracle Compensation Response Admission

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-07 and AC-08 |
| State | `FROZEN / READY_FOR_DISPATCH` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2E3D-01` / P1-P8 |
| Dependency | E2 merge `d3d3c1d`, E3A `b324f91`, E3B `dc07eec` and E3C `c042af1` approved/integrated |
| Planned owner | Exact Local project/task for existing `workflow-implementer-2`; no new worktree |
| Control / reviewer | Current control task is both ticket author and independent reviewer; it must not implement source/tests |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## One observable outcome

One pure staging boundary receives an expected compensation `OracleAction` and
one untrusted `OracleRunResult`, then returns exactly one recursively rebuilt
typed protocol response, one typed installed-path absence, or one metadata-only
finite rejection. The future E3 effect adapter can consume this boundary without
copying response validators or manufacturing success from a block, wrong surface,
constructed value or caller-provided payload.

## Frozen design

- Add only `tests/staging/codex_lifecycle_oracle/response_admission.py` and
  `tests/test_codex_oracle_response_admission.py`.
- The public function accepts `object` plus an exact `OracleAction`; it returns a
  closed union of accepted protocol response, accepted absence, or rejected
  metadata. No `None`, raw mapping, exception text, caller callable, path,
  command, diagnostic or dynamic member lookup crosses the boundary.
- Supported protocol actions are `PLUGIN_REMOVE`, `MARKETPLACE_REMOVE`,
  `PLUGIN_LIST` and `MARKETPLACE_LIST`. Exact `OracleAbsent` is accepted only
  for `ABSENCE`. Every other action/result combination is finite rejection.
- An accepted protocol value must be rebuilt from exact built-in state at every
  Pydantic node. Subclasses, missing/extra fields, constructed or injected
  nested values, wrong surface/payload pairs and caller-controlled property,
  equality, hash, repr or serialization execution reject before any value is
  exposed.
- Exact `OracleBlocked` maps to one finite dependency-blocked reason without
  retaining its raw reason. Wrong result type, malformed state and
  action/surface mismatch remain separately finite so E3 can map them to its
  existing `DEPENDENCY_BLOCKED` or `EVIDENCE_INVALID` values without guessing.
- This ticket is pure projection only. It may not call `CodexLifecycleOracle`,
  inspect a lease, allocate/delete files, mutate state, import E2's private
  helpers, build the E3 port, or perform removal/list/absence effects.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `P1` | First red is the missing response-admission module. The implementation commit changes exactly the two frozen paths. |
| `P2` | Non-`OracleAction`, unsupported action, non-run-result, subclass and constructed/extra top-level values return one finite invalid/malformed rejection without exception or caller protocol execution. |
| `P3` | Exact `PLUGIN_REMOVE` plus exact matching `CodexPluginRemove` is rebuilt and accepted; wrong surface, wrong payload, missing/extra/injected field and malformed nested value reject. |
| `P4` | Exact `MARKETPLACE_REMOVE` plus exact matching `CodexMarketplaceRemove` is rebuilt and accepted; the same finite negative matrix rejects. |
| `P5` | Exact `PLUGIN_LIST` recursively rebuilds installed/available entries, optional marketplace source and primitive fields; duplicate/foreign entries remain data, while subclasses and malformed/constructed nodes reject. |
| `P6` | Exact `MARKETPLACE_LIST` recursively rebuilds entries and optional marketplace source; subclasses and malformed/constructed nodes reject. |
| `P7` | Exact `OracleAbsent` is accepted only for `ABSENCE`; absence under another action and completed response under `ABSENCE` reject. Exact `OracleBlocked` always returns metadata-only dependency-blocked evidence and never leaks its reason. |
| `P8` | Independently reverse action/surface matching, one recursive exact-state guard and the absence gate. Each named test turns red and exact blobs restore; focused/full serial unittest, strict mypy, in-memory compile, source/scope/diff/ancestry/topology/residue checks pass. |

## TDD / CodeReview matrix

- Path-prefix class: not applicable; no path comparison is introduced. Source
  scan must confirm no path, filesystem or locator authority enters this module.
- Authority-bypass class: the boundary is pure and exposes no effect capability;
  unsupported/wrong action cannot obtain an accepted response.
- Exception/error class: every named invalid shape and exact `OracleBlocked`
  returns a finite value; no raw reason or exception text is retained.
- Test-truth class: P3, P5 and P7 each have a named reversal in P8.
- XSS: `XSS_NOT_APPLICABLE`; no Browser, WebView, renderer, DOM, JavaScript or
  privileged bridge exists.
- Task/worktree class: product task root, filesystem identity and linked Git
  worktree metadata must match the permanent owner worktree before dispatch.

## Exact source, return and boundary

Return one exact two-path implementation commit, then one unique
`doc/WorkProgressReport.md`-only handoff. No numeric line limit is an acceptance
criterion. No E3 effect adapter, E4-E6, live Codex, environment mutation,
filesystem/network/target-project effect, Agent control, staging push, package,
release or deployment is authorized.
