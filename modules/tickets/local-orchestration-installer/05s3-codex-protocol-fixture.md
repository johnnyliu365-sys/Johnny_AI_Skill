# 05S3 — Codex Protocol Fixture

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-08 protocol seam only |
| Context / decision | `doc/context/local-orchestration-installer/main.md` / `PRG-20260811-106` |
| State | `CHANGES_REQUESTED / FINAL_REVIEW_STOPPED` — CR-125 |
| Dependency | 05S1 and 05S2 independently approved and integrated by `504a3ec` and `6e24e06` |
| Implementation language | Python 3.11 |
| Implementation responsibility | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-terra`, reasoning `xhigh`, in the sole implementation worktree after exact receipt admission |
| Acceptance responsibility | Independent control-plane reviewer in the control worktree; no implementation writes |
| Environment level | Test-owned 05S1 filesystem plus the integrated 05S2 runner; no live Codex, target project, installer or host registration |

## One outcome

Provide a deterministic child fixture and strict parser for the six documented
Codex marketplace/plugin add, list and remove JSON surfaces. The fixture proves
that response bytes came from a real bounded child. It does not persist
lifecycle state, decide ownership, compensate effects or prove absence.

## Authorized scope

```text
tests/staging/codex_protocol/__init__.py
tests/staging/codex_protocol/contracts.py
tests/staging/codex_protocol/fixture.py
tests/staging/codex_protocol/fixture_child.py
tests/test_codex_protocol_fixture.py
doc/WorkProgressReport.md       # separate docs-only return only
```

Integrated 05S1, 05S2 and production files are read-only. The implementation
may import 05S1/05S2 and the integrated 05A list DTOs, but must not copy,
cherry-pick or import source/tests from the rejected combined-05S history. No
marketplace/plugin persistence or payload, transaction journal, production
adapter, target-project or live-host behavior is in scope. The one bounded
response file defined below is transport, not lifecycle state.

## Frozen public JSON schemas

All objects forbid extra fields. Every listed text field is a strict nonblank
string; booleans are strict booleans and do not accept `0`/`1`. Required fields
cannot be absent or null.

| Surface | Exact JSON object |
| --- | --- |
| Marketplace add | `marketplaceName`, `installedRoot`, `alreadyAdded` |
| Marketplace list | `marketplaces`; each entry has required `name`, `root` and optional `marketplaceSource` object with exact `type`, `value` |
| Marketplace remove | `marketplaceName`, `installedRoot` |
| Plugin add | `pluginId`, `name`, `marketplaceName`, `version`, `installedPath`, `authPolicy` |
| Plugin list | `installed`, `available`; every entry has required `pluginId`, `name`, `marketplaceName`, `version`, `installed`, `enabled`, `source`, `installPolicy`, `authPolicy` and optional exact `marketplaceSource` |
| Plugin remove | `pluginId`, `name`, `marketplaceName` |

Marketplace/plugin list parsing must reuse the integrated 05A
`CodexMarketplaceList` and `CodexPluginList` contracts rather than redefine
them. An optional `marketplaceSource` may be absent; explicit null is invalid.
`version` is plain strict nonblank documented text. This ticket must not add a
SemVer parser or reject a non-SemVer version string.

The four mutation contracts are strict frozen models named
`CodexMarketplaceAdd`, `CodexMarketplaceRemove`, `CodexPluginAdd` and
`CodexPluginRemove`. The six-way `CodexProtocolPayload` union and its surface
cross-check must make it impossible to label one DTO as another surface.

## Frozen child and response transport

- `CodexProtocolSurface` is the only operation selector and has exactly six
  values: `MARKETPLACE_ADD`, `MARKETPLACE_LIST`, `MARKETPLACE_REMOVE`,
  `PLUGIN_ADD`, `PLUGIN_LIST`, `PLUGIN_REMOVE`.
- The real fixture invocation uses the integrated `BoundedChildProcessRunner`,
  an absolute Python executable, the fixture-child script, and only the selected
  enum value as protocol input. The response identity, fields and values are
  generated in the child; the parent must not construct or reuse request values
  as response proof.
- The 05S2 working directory is exactly the lease's `temporary` directory. The
  child writes raw response bytes only to fixed relative file
  `.johnny-05s3-response.json` there. No caller-supplied output locator, stdout
  capture, shell, PATH lookup or ambient environment is permitted.
- Before start, that exact response file must be absent. After a successful
  process observation, the parent accepts only one ordinary non-reparse file
  at that exact owned location, reads at most 65,536 bytes, decodes strict UTF-8
  and parses the bytes. It must not scan, recursively clear or delete another
  path.
- Response inspection/removal uses one required typed response-file port with a
  concrete exact-file binding. It is never optional. Tests may inject a strict
  port only for deterministic read or cleanup faults; real success, collision
  and topology cases use the concrete filesystem binding.
- The exact response file is removed on every completed path. A failed process,
  missing/invalid file, read/decode/parse/schema failure or exact-file cleanup
  failure returns a finite rejection and cannot leak an exception. 05S1 teardown
  remains responsible only for the exact leased root.
- A successful result carries the selected surface and the typed payload read
  from the child. A rejected result carries only the surface and one
  `CodexProtocolRejectReason`: `PROCESS_FAILED`, `RESPONSE_MISSING`,
  `RESPONSE_BOUNDARY_INVALID`, `RESPONSE_TOO_LARGE`, `INVALID_UTF8`,
  `MALFORMED_JSON`, `DUPLICATE_KEY`, `SCHEMA_INVALID` or `CLEANUP_FAILED`.
  There is no optional port, `None` placeholder, raw exception, stdout/stderr or
  absolute response-file locator in either result.
- Parsed `installedRoot`, `installedPath`, list roots and source values are
  ephemeral protocol data. Tests may inspect them in memory but no absolute
  value may be copied into committed evidence, Router state, telemetry or the
  docs-only return.

## Acceptance closure — `CLOSURE-LOCAL-INSTALL-T05S3-01`

| ID | Protocol-only acceptance |
| --- | --- |
| `D1` | The four mutation models and reused two list models accept exactly the frozen public fields and strict types, including strict `alreadyAdded`/installed/enabled booleans and plain nonblank version text. |
| `D2` | For every surface, strict parsing rejects empty object, malformed JSON, invalid UTF-8, every missing required field, top-level and nested extra fields where applicable, null/blank required values, wrong scalar/container types and duplicate object keys. Optional source absence succeeds and explicit null fails. |
| `D3` | Each of the six success surfaces runs through the real integrated 05S2 runner in one 05S1 lease, and the accepted payload comes only from the child's fixed response file. A process failure or missing response cannot be reported as parsed success. |
| `D4` | Parent environment, bytes outside the lease and integrated files remain invariant. Each case removes only its response file, tears down its exact lease and leaves zero response files, staging roots or repository caches. No absolute fixture value becomes durable evidence. |

## Finite TDD matrix

| Cell | Required first-red and green assertion |
| --- | --- |
| `T1` | The focused test initially fails because the new protocol module does not exist. Green proves all six canonical child payloads parse to the matching typed union member, with both optional-source present and absent list entries and a non-SemVer nonblank plugin version accepted. |
| `T2` | A table-driven parser test covers every D2 rejection for every surface. Each required field is removed independently; list wrappers and nested entries both receive extra/null/blank/wrong-type probes. Integer booleans and explicit-null optional sources fail. |
| `T3` | A real child is invoked six times through 05S2. The parent arguments contain only script plus surface selection; accepted child-only sentinel values were not supplied by the parent. Injected non-success and a child success with no response both return their exact finite rejection. |
| `T4` | Pre-existing response collision blocks before child start. Oversize, reparse/non-file response and exact-file cleanup failure are finite. Success and every rejection preserve an external sibling and parent environment, then leave zero `.johnny-05s3-response.json`, `johnny-stage-env-*`, `.mypy_cache`, `.pytest_cache` or `__pycache__` residue. |

### CodeReview.md §2.1 interception map

| Defect class | Disposition |
| --- | --- |
| 1 path prefix / physical redirection | D3/D4 and T3/T4 require exact owned file topology and no external write/delete. |
| 2 null / empty representations | D1/D2 and T1/T2 explicitly separate optional absence from null/blank/wrong type. |
| 3 permission bypass | Not applicable; no protected host or target resource is opened. |
| 4 token parsing/comparison | Not applicable; no credential or token is accepted. |
| 5 result-code consistency | D3 and T3 require accepted/rejected result truth after the actual process outcome. |
| 6 exception propagation | D2-D4 require every declared byte, schema, process and cleanup failure to remain finite. |
| 7 test truthfulness | Reviewer must reverse-check child-output binding, strict mutation rejection and cleanup/readback claims. |

## Evidence and stop boundary

Use strict TDD and record the real first red. The exact focused command is
`python -B -m unittest tests.test_codex_protocol_fixture -v`; the full command
is `python -B -m unittest discover -s tests -v`. Run strict full-tree mypy with
`--no-incremental` and a validated repository-external temporary cache, remove
that cache, then run in-memory compile, source/scope sentinel, `git diff
--check`, clean tracked/ignored readback and zero-residue checks.

Return one implementation commit containing only the five authorized Python
files, then one docs-only commit changing only `doc/WorkProgressReport.md`.
The implementation owner makes no review, integration or 05S4 decision. The
independent reviewer reruns the matrix from a fresh export and performs
adversarial child-binding, response-topology and cleanup probes. Any blocker
stops without automatic correction, replacement branch/worktree or downstream
dispatch.
