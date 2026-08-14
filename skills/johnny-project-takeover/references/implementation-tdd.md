# Implementation TDD and completion

Read this reference only after exact ticket, receipt, owner and workspace admission succeeds.

## One behavior at a time

1. Write an executable test at the ticket's approved seam.
2. Run it and record the first failure caused by missing behavior.
3. Write the smallest production change that makes it pass.
4. Run affected tests, strict type checks, lint, formatting, build and data validation.
5. Run the ticket's primary-path smoke test.

Do not start another behavior, ticket or commit before the current behavior and smoke gate are
green.

The ticket must name every applicable TDD category from the canonical review checks. Generic
labels such as “normal/invalid/external/regression” are insufficient. A relevant category
missing from ticket design is a `TICKET_DEFECT`, not an instruction for the implementer to
invent new scope.

Record the first-red test name and failure reason in the ticket evidence. A test written after
production behavior exists is regression evidence, not proof of red-first TDD.

## Type and layering gate

Use named domain types, immutable models, explicit nullability and complete parameter/return
types. Dynamic external input is validated and converted at the boundary. Do not propagate
`Any`, implicit `any` or unvalidated dynamic objects inward.

Use `mypy --strict` or Pyright strict for Python, TypeScript strict for Node.js, and an
equivalent checker elsewhere. Domain holds invariants and values; Application holds use cases,
ports and transaction boundaries; Infrastructure implements external adapters; Transport/UI
handles serialization and presentation. Outer layers do not hold business rules or secrets.

## Smoke gate

Start the affected application/service or invoke its real local entry seam, run at least one
primary observable path and confirm expected result plus absence of obvious runtime/load
errors. If automation is impossible, record exact manual steps and result. Failure returns to
the TDD loop.

## Ticket completion

A ticket is complete only when:

- TDD and affected regression tests pass;
- type, lint, format, build and data gates pass, or a specifically authorized blocker is
  recorded;
- AC, error behavior, data contract, privacy/logging and applicable security matrices have
  reproducible evidence;
- the owner worktree creates one implementation commit containing only this ticket;
- the Work Progress Report records identifiers/results in a separate docs-only commit;
- no cache or unauthorized residue remains.

Return `ImplementationReturn`: `COMPLETED`, `BLOCKED` or `CHANGE_DETECTED`. Do not claim review
approval, merge, release or deployment.
