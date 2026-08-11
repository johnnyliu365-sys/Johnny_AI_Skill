# 05B3 — Codex Exhaustive Compensation

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 compensation seam |
| State | `IN_PROGRESS / IMPLEMENTATION_DISPATCH_CONFIRMED` |
| Dependency | Ticket 05B1 and 05B2 independently approved and integrated by `bbc7de5` and `c97505c` / `ef45f65` |
| Implementation owner | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation` worktree and branch only |
| Acceptance owner | Independent control-plane reviewer; no implementation writes |
| Language | Python 3.11, strict Pydantic and mypy |

## One outcome

Provide one production compensation coordinator for an exact current Codex
registration attempt. It invokes only a required injected typed port, removes
current-attempt plugin authority before marketplace authority, executes every
required removal and all three fresh absence probes without finite-failure
short-circuiting, and returns only the authority that fresh proof still leaves
unresolved.

This ticket does not perform registration admission, add commands, final
receipt issuance, public uninstall, live Codex access, target-project access or
05S4 oracle composition. Tests use a deterministic in-memory port. Ticket 05B4
will bind that port to fresh 05A/05B observations and the test-owned 05S4
oracle; production source must not import `tests/`.

## Exact source boundary

Only these paths may change:

1. `library/local_orchestration/codex_compensation.py` — new strict manifest,
   port, observation, result and coordinator contracts.
2. `tests/test_codex_compensation.py` — complete finite TDD matrix and fake
   port only.
3. `library/local_orchestration/__init__.py` — export only the new public
   surface.

Integrated 05B1/05B2 source and tests are read-only dependencies. Rejected
Ticket-05/05B source is immutable historical evidence and may not be copied,
cherry-picked or imported. There is no numeric line target; scope, strong
contracts, finite behavior, readability and truthful evidence are the quality
gates.

## Required typed boundary

- A frozen `CodexCompensationManifest` binds the exact installation ID, root,
  marketplace name and source locator, plugin ID/name/version, installed
  locator, auth policy and artifact digest. It is owner intent for this attempt,
  not a success receipt and not existence proof.
- A frozen compensation request binds that manifest to the exact
  `CodexPreflightRequest`, `CodexRegistrationAttemptId` and 05B1 journal. The
  coordinator recursively revalidates request, journal and manifest equality
  before any port call.
- One required non-null runtime-checkable port has five distinct methods:
  plugin removal, marketplace removal, fresh plugin list, fresh marketplace
  list and installed-path absence proof. Every call receives the same validated
  request; no generic action string or nullable port is permitted.
- Plugin and marketplace removal confirmations are distinct strict models.
  Marketplace removal carries the observed absolute root only as an ephemeral
  value and must bind the canonical manifest source locator. Plugin removal
  binds plugin ID, plugin name and marketplace name.
- Fresh list calls return the integrated strict `CodexPluginList` and
  `CodexMarketplaceList`. The coordinator, not the port, decides whether the
  exact manifest identity remains. Unrelated entries are ignored and never
  removed or persisted.
- Installed-path absence proof binds installation ID, root, installed locator,
  digest and `absent=true`. It contains no caller-selected absolute path.
- A declared typed port failure and malformed returned observation map to a
  finite step failure and do not suppress later finite steps. `RuntimeError`,
  `MemoryError`, `KeyboardInterrupt` and `SystemExit` are not broadly caught.

## Frozen acceptance closure — `CLOSURE-LOCAL-INSTALL-T05B3-01`

| ID | Required first-red and green behavior |
| --- | --- |
| `D1` — exact admission | Revalidate the manifest, request, attempt ID and journal recursively. Only the six journal pairs reachable from integrated 05B2 are admitted: `(NOT_ATTEMPTED, NOT_ATTEMPTED)`, `(MAY_EXIST, NOT_ATTEMPTED)`, `(OWNED, NOT_ATTEMPTED)`, `(PREEXISTING, NOT_ATTEMPTED)`, `(OWNED, MAY_EXIST)` and `(OWNED, OWNED)`. Malformed, replayed, cross-request, manifest-mismatch, unreachable `(OWNED, PREEXISTING)` or invalid-port input returns a distinct finite rejection with zero port calls. |
| `D2` — exact removal authority | `(NOT_ATTEMPTED, NOT_ATTEMPTED)` and `(PREEXISTING, NOT_ATTEMPTED)` return a typed no-compensation result with zero calls. Every other admitted journal invokes removal only for `MAY_EXIST` or `OWNED`; plugin is always attempted before marketplace. `PREEXISTING` and `NOT_ATTEMPTED` never grant a removal call. Each confirmation must match every field of its exact manifest authority. |
| `D3` — exhaustive fresh proof | After the authorized removals, invoke fresh plugin list, fresh marketplace list and installed-path absence in a fixed documented order. A declared failure or malformed/mismatched confirmation at any removal/probe step is recorded but never short-circuits later finite steps. All three probes run whenever compensation authority exists, including after either removal failure. |
| `D4` — residual authority only | Marketplace authority resolves to `NOT_ATTEMPTED` only when the fresh marketplace list has no exact manifest entry. Plugin authority resolves to `NOT_ATTEMPTED` only when both fresh plugin lists contain no exact manifest entry and the exact installed-path proof says absent. Removal confirmation alone never clears authority. A failed removal whose complete fresh absence is proved remains a failure result but carries no retry authority for that resolved effect. Residue or unproved absence retains exactly the original `MAY_EXIST`/`OWNED` state. |
| `D5` — finite metadata-only result | Return one strict `COMPENSATED`, `COMPENSATION_NOT_REQUIRED`, `COMPENSATION_FAILED` or pre-effect `COMPENSATION_BLOCKED` model. Failure contains an ordered unique tuple of finite step reasons plus the recursively valid residual journal; it contains no raw command, stdout/stderr, absolute path, exception text, receipt, final registration success or broad-clear authority. |

## Required TDD and review matrix

| Cell | Exact assertion |
| --- | --- |
| `T1 / D1` | Remove every field from manifest/request/observations one at a time; add extra, null, blank, container, wrong enum/literal and constructed values. Table all seven legal 05B1 journal pairs, the six admitted 05B2-reachable pairs, request/attempt replay and every one-field manifest mismatch. Assert zero port calls on rejection. |
| `T2 / D2` | Table all admitted pairs and assert exact call sequence: none for no-authority/pre-existing, marketplace-only for marketplace authority, and plugin-then-marketplace for two-effect authority. Inject every plugin-confirmation and marketplace-confirmation identity/root mismatch. |
| `T3 / D3` | At each of the two removal and three absence steps, inject declared port failure and malformed return separately. Assert every later finite step still runs exactly once and the ordered failures contain the exact step/reason. |
| `T4 / D4` | Cross the three fresh absence truths over a two-effect journal. Assert marketplace residual depends only on its fresh list; plugin residual depends on both plugin list and installed-path proof. Assert removal failure plus proved absence clears retry authority while retaining the failure result. |
| `T5 / D5` | Assert all result variants are recursively strict and metadata-only; declared failures are finite, while `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` propagate. Preserve unrelated marketplace/plugin entries byte/value-identically in the fake port. |

CodeReview.md classes 1, 2, 3, 5, 6 and 7 apply. Token comparison is
not applicable. Source must reject `Any`, `type: ignore`, optional/`None`
effect ports, raw dict contracts, generic action strings, broad catches or
clear/delete shortcuts, caller-synthesized final success and compressed
multi-statement production lines.

## Reverse mutations

Independently reverse and restore each guard below; the named focused test must
turn red before restoration:

1. permit `PREEXISTING` to invoke marketplace removal;
2. stop after a plugin-removal failure instead of invoking marketplace and all
   three probes;
3. clear plugin authority from removal confirmation without both absence
   proofs;
4. retain stale plugin retry authority after both fresh plugin absences pass;
5. accept a foreign marketplace removal root or foreign installed-path proof.

## Verification and return

Run focused/full unittest, strict full-tree mypy using a validated external
cache removed afterward, in-memory compile, source/scope/diff sentinels and
tracked/ignored/cache zero-residue readback. Record the exact first-red,
green, finite call sequences and five reverse mutations.

Return one implementation commit containing exactly the three authorized
paths, followed by one docs-only commit changing only
`doc/WorkProgressReport.md`. The implementation owner works alone and makes no
review, integration, downstream-dispatch or Agent-control decision. No new
branch/worktree, reset, rebase, amend, force, merge, cherry-pick, stash, push,
release, deployment, live Codex mutation or target-project write.

## Dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B3-01` |
| Handoff | `hnd_local_orchestration_install_05b3_20260811` |
| Allocation / receipt | `aln_local_orchestration_install_05b3_20260811` / `rcpt_local_orchestration_install_05b3_20260811` |
| Correlation / question | `corr-local-orchestration-install-05b3-20260811` / `q-local-orchestration-install-05b3-20260811` |
| Side context | `scx-local-orchestration-install-05b3-20260811-01` |
| Authority | Owner instruction to continue under the approved workflow; program authority `PRG-20260809-042`; integrated dependency `c97505c67d4a7ba602f590ff281fda0d1663768d` / `ef45f65` |
| Ticket-doc baseline | `77c8756d341bd8b0c93899cac6132f18c31b4840` |
| Expected lane admission | Existing branch `codex/implementation-codex-protocol-fixture-05s3` at exact clean HEAD `b8090078c6a41f19cba0c216f2a3e7030dc4dec8`, then normal `git merge --ff-only` to the control handoff commit. No new branch/worktree. |
| Return | One exact-scope implementation commit, then one `doc/WorkProgressReport.md`-only handoff reserved as unique `PRG-20260811-162`. |
