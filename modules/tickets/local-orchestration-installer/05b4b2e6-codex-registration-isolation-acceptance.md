# 05B4B2E6 — Codex Registration Isolation Acceptance

| Field | Value |
| --- | --- |
| State | `CONVERGENCE_DECOMPOSED / ALL_CHILDREN_COMPLETE / NON_DISPATCHABLE` |
| Dependency | 05B4B2E4 and 05B4B2E5 approved and integrated |
| Allocation | None; a parent ticket never receives implementation authority |

## Reserved responsibility

Run the already accepted success and compensation entry points against seeded
foreign oracle state while two separate sentinel target-project repositories
remain outside the disposable environment. Prove foreign state/payload bytes
and both target repositories' tracked bytes plus porcelain are identical
before/after. This is evidence-only acceptance and adds no new lifecycle
behavior. Exact closure is frozen after E4/E5 integration. No numeric line
limit applies.

## Decomposition decision

The planned ticket assumed both lifecycle lanes already exposed reusable
entrypoints. E4 does; E5 intentionally remained a one-file evidence fixture.
Implementing the original E6 directly would therefore either import private
test helpers, copy the compensation transaction, or combine reusable-boundary
work with two independent isolation claims. All three would increase rework.

E6 is split into:

1. `05B4B2E6P`: extract the already accepted E5 behavior into one reusable,
   staging-only typed entrypoint and keep E5 green.
2. `05B4B2E6A`: use the accepted success and compensation entrypoints to prove
   seeded foreign oracle records and payloads are unchanged.
3. `05B4B2E6B`: use the same entrypoints to prove two external sentinel target
   repositories retain exact tracked bytes and clean porcelain.

E6A and E6B may run in parallel only after E6P is independently approved and
integrated. No child adds production behavior or may touch a real target
project. Each receives a separate closure, receipt, review and integration.

All three children are now independently approved and integrated: E6P by
`7334cc5314592ac159e9418a145121d31e4156d5`, E6B by
`0e0934d17382f3fd8ff17878d88ce1e597e35b91`, and E6A by
`fe0059ec5b811c6c67065c9be04eafca0629493a`. This parent remains an immutable,
non-dispatchable decomposition record; its isolation objective is complete.
