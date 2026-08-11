# 05B3A — Codex Safe Compensation Port Capability

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02 and AC-07 effect-boundary seam |
| State | `PLANNED / READY_FOR_DISPATCH` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B3A-01` / A1-A5 |
| Dependency | Integrated 05B1/05B2 at control baseline; ADR-20260811-004 |
| Control / implementation / reviewer | Current `main` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` / independent current `main` reviewer |
| Worktree / branch | Existing `workflow-implementation`; new ticket branch required from the reviewed handoff because its current branch is immutable rejected 05B3 evidence |
| Language | Python 3.11; strict Pydantic/mypy |

## One observable outcome

Given an untrusted adapter candidate, return either one frozen, fully typed
five-operation compensation capability or a finite `INVALID_PORT` rejection
without reading a dynamic descriptor, invoking an operation, running a command
or touching a filesystem. This ticket does not plan compensation, reduce
authority or execute a capability.

## Exact source boundary

Only these new paths may change:

1. `library/local_orchestration/codex_compensation_port.py`
2. `tests/test_codex_compensation_port.py`

All existing source/tests and root exports are read-only. The terminal 05B3
branch is evidence only: no copy, cherry-pick, import or source reuse.

## Public contract and architecture

- The sole dynamic entry is `admit_codex_compensation_port(candidate: object)`;
  `object` is validated immediately and never crosses the returned boundary.
- The result is a discriminated union of a frozen
  `CodexCompensationPortCapability` and a finite rejection with public status
  `INVALID_PORT` plus one unique internal reason.
- The five required names are `remove_plugin`, `remove_marketplace`,
  `list_plugins`, `list_marketplaces` and `prove_installed_path_absent`. Each
  must resolve in the concrete class MRO to an ordinary `FunctionType`
  instance method. Static/class methods, properties, custom descriptors,
  per-instance callable objects, built-ins and variadic or wrong-arity
  functions reject; unrelated class members do not affect admission.
- Lookup must bypass caller overrides: obtain the concrete class through the
  built-in `object.__getattribute__`, then read `__mro__` and each class
  `__dict__` through the built-in `type.__getattribute__`. Runtime arity uses
  safe code/default metadata of the raw function only. Calling
  `inspect.signature()` or following `__signature__` / `__wrapped__` on
  caller-controlled data is forbidden.
- Raw functions are bound explicitly into the exact frozen capability. The
  factory never dynamically gets a candidate member and never calls one.
- Strong request/manifest and five operation return contracts are defined here
  for later 05B3C use; no raw output, exception text, receipt, absolute path or
  registration success enters admission results.

## Acceptance Closure Set — revision 01

| ID | Finite completion rule |
| --- | --- |
| `A1` | A valid plain-method adapter returns one exact frozen capability; all five bound operations retain distinct typed signatures. Admission itself produces zero reads/calls beyond static function metadata. |
| `A2` | For each of five names, missing, non-callable, property, staticmethod, classmethod, custom descriptor, per-instance callable, zero/two-request, variadic and required-keyword-only shapes return finite `INVALID_PORT` with the exact reason and zero descriptor/operation calls. |
| `A3` | Candidate and callable traps on `__getattribute__`, `__get__`, `__signature__` and `__wrapped__` remain unread. A trap that would raise `RuntimeError`, `MemoryError`, `KeyboardInterrupt` or `SystemExit` cannot escape admission. |
| `A4` | `None`, empty/blank text and tuple/list/dict candidates reject identically before effects. Extra unrelated class members neither grant nor remove the five required operations. |
| `A5` | Only after successful admission may a caller invoke a bound operation. An exception from that actual operation is not swallowed or reclassified by the capability. Serialized admission results are metadata-only. |

## TDD design and CodeReview.md §2.1 mapping

- **Null/empty/container (class 2):** `None`, `''`, whitespace, tuple, list and
  dict all reject with zero observable reads/calls.
- **Error-code consistency (class 5):** table every A2 shape to fixed public
  `INVALID_PORT` and one finite internal reason; no exception text.
- **Exception propagation (class 6):** all four process/control traps cannot be
  reached during admission; the same four exceptions from an explicitly
  invoked valid bound operation propagate.
- **Path/token classes (1/4):** not applicable; this ticket accepts no path,
  URI, credential or token.
- **Authority bypass (class 3):** direct use of an unadmitted candidate is not
  part of the public capability API; copied/malformed capability construction
  cannot be accepted as an admission result.
- **Truthfulness (class 7 / CR):** reverse static lookup to dynamic `getattr`,
  replace code-object validation with `inspect.signature`, and accept one
  descriptor/callable shape; each isolated reverse must make the named test red.

First red must be captured before production source exists. Focused/full
unittest, strict full-tree mypy with a removed external cache, in-memory
compile, source/diff/scope and zero-residue checks are required. One
implementation commit is followed by one WPR-only handoff commit. No live
Codex, target-project write, network, Secret, integration, push, release or
deployment is authorized.
