# ADR-20260811-004｜Closed compensation capability and pure reducer

- Date: `2026-08-11（Asia/Taipei）`
- Status: `ACCEPTED`
- Decision maker: Project owner
- Related specification: `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X`
- Related change: `CHG-20260808-011`（behavior unchanged）

## Background and problem

Ticket 05B3 closure revision 01 reached terminal
`CONVERGENCE_REVIEW_REQUIRED`. Its open structural `Protocol` boundary tried
to prove arbitrary Python callables safe by using `inspect.signature()`.
Signature inspection can execute caller-controlled `__signature__` or
`__wrapped__` descriptors, so the boundary cannot simultaneously accept an
unrestricted callable object and promise zero descriptor effects.

The product requirement is unchanged: only exact current-attempt authority may
remove effects, all proofs must run exhaustively, and invalid ports must fail
finitely before any effect. The implementation boundary must be narrowed.

## Decision

Split compensation into three independently reviewable capabilities:

1. **05B3A — closed port capability.** A factory receives an untrusted
   `object`, obtains its concrete class only with built-in `type(candidate)`,
   and obtains the real class MRO and raw class dictionaries only through the
   trusted getset descriptors captured from immutable built-in `type.__dict__`.
   It accepts the five required names only when their raw values are plain
   Python `FunctionType` instance methods with finite code-object arity, then
   binds those functions without resolving candidate attributes. It returns
   either a frozen typed capability or a finite rejection. It never calls
   `object.__getattribute__` or `type.__getattribute__` for caller-owned class
   metadata, never compares an untrusted class by equality, never calls
   `inspect.signature()` on caller-controlled data, and never invokes a
   caller-controlled descriptor or operation.
2. **05B3B — pure planner/reducer.** A deterministic domain function derives
   the exact ordered compensation plan from an integrated 05B1 journal and
   reduces a complete finite observation sequence to a recursively strict
   residual journal. The residual record preserves the exact request and
   attempt identity plus each original `MAY_EXIST`, `OWNED`, `PREEXISTING` or
   `NOT_ATTEMPTED` state; only the corresponding fresh absence proof may
   replace current-attempt removal authority with `NOT_ATTEMPTED`. It has no
   port, callable, descriptor, command or filesystem dependency.
3. **05B3C — thin composition.** Only after 05B3A and 05B3B are independently
   approved and integrated, a coordinator executes the validated capability
   in the reducer's order, validates returned observations against the exact
   manifest, and supplies normalized outcomes to the reducer.

05B3A and 05B3B use disjoint files and only integrated 05B1/05B2 dependencies,
so two named implementation owners may work in parallel. 05B3C remains
dependency-waiting and owns all cross-module composition.

## Alternatives and trade-offs

| Alternative | Decision |
| --- | --- |
| Add another catch around `inspect.signature()` | Rejected: it may hide the exception but still executes a forbidden descriptor. |
| Inspect `type(callable).__call__` while retaining arbitrary callable objects | Rejected: wrapper, inheritance and callable metadata surfaces remain wider than the required adapter contract. |
| Trust mypy and skip runtime admission | Rejected: the external adapter boundary is dynamic and must fail finitely. |
| Closed plain-method capability plus pure reducer | Adopted: narrows the runtime surface, removes unsafe introspection and makes effect admission independent from state reduction. |

## Consequences, risks and recovery

- Plain methods are intentionally required; static methods, class methods,
  properties, custom descriptors, per-instance callable objects, variadic
  methods and signature metadata are rejected.
- The factory may read immutable Python function code/default metadata but may
  not dynamically read the candidate or callable object.
- The reducer cannot manufacture host truth; 05B3C is responsible for exact
  manifest-bound observation validation.
- Rejected 05B3 commits remain immutable evidence and are not source inputs.
  Recovery is to abandon the new child branches before integration; no target
  project, live Codex state or host configuration is involved.

## Revision / supersession record

- Initial accepted convergence decision following terminal review
  `97167046ff8a3889d36e369566b8e6342bdb5691`.
- Revision 02 follows review `14fda317538f6661573cf687468f5291ced84ff7`:
  it replaces descriptor-resolving lookup primitives, freezes identity-only
  class checks, names the exact proof order, and restores the exact residual
  current-attempt identity/state contract without changing product behavior.
