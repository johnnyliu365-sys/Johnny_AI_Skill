# Code Review — 01 Enforce Continuation and Implementation Handoff

## Result

**APPROVED** on 2026-08-05. The reviewed implementation range is `7ca74ab..a94e207` on `codex/implementation-private-router-saas-01`.

| Source | Reference |
| --- | --- |
| Change | `CHG-20260805-009` |
| Context | `doc/context/workflow-governance/main.md` |
| Specification | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` |
| Ticket | `01-enforce-continuation-and-handoff` |
| Control-plane owner / reviewer | Codex / `main` worktree |
| Implementation owner | Codex implementation Agent / `codex/implementation-private-router-saas-01` |

The review evaluates contents and reproducible evidence, not authorship. Initial commits `d7e40cf`, `8bd984c`, and `423c41b` were externally advanced with indeterminate provenance. Corrective commits `eb4bb8f`, `7faa590`, `af6bf43`, `a17bec3`, and evidence commit `a94e207` were supplied from the named implementation worktree.

## Reviewed behaviour

- `RouterEngine` requires a typed `ImplementationHandoff` only where a Profile explicitly declares `TICKETS + APPROVAL_GRANTED → IMPLEMENT`; a bare event returns `SUSPEND + HALT`, no next stage, source, Context, or capability.
- A private request carries only typed metadata. The `PrivateRouterClient` projects the same missing-handoff decision to `ROUTER_POLICY_BLOCKED`, with no grant.
- A valid non-frontend handoff advances exactly to `IMPLEMENT`; owner collisions, undeclared handoffs, incomplete frontend Composition Root data, and events mixing handoff with completion/return are rejected.
- A blocked implementation return halts at the direct and private entrypoints. `CHANGE_DETECTED` re-enters `GRILL` through `REQUIREMENT_CHANGED`.
- Existing Profiles remain compatible when they submit legacy bare `ACTION_COMPLETED`; new completion evidence is rejected unless the Profile declares its action kind.

## Independent verification

Executed from the named implementation worktree at `a94e207`, with `PYTHONDONTWRITEBYTECODE=1`:

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | PASS — 73 tests |
| `python -m mypy --strict library tests --cache-dir <temporary-review-cache>` | PASS — 58 source files |
| In-memory `compile()` of every `library/workflow_router/*.py` file | PASS |
| `git diff --check 7ca74ab..HEAD` | PASS |
| `git status --short` | PASS — clean |
| Mutation: remove the `requires_implementation_handoff` guard in a disposable detached review worktree | PASS — `test_ticket_approval_requires_a_valid_handoff_at_the_direct_router_entrypoint` failed because the bare event became `ADVANCE` rather than `SUSPEND`; temporary worktree removed afterward |

The ticket also records the approved Windows-equivalent per-file `py_compile` command. The literal wildcard form was not used as a passing claim because PowerShell does not expand it for Python.

## CodeReview.md §2 checks

| Check | Result and evidence |
| --- | --- |
| Clear, strongly typed design | PASS — immutable strict Pydantic contracts expose finite status, stage, owner, scope, evidence, continuation, and blocker types; no unvalidated dynamic values enter Router decisions. |
| Existing conventions / layering | PASS — contracts validate at the boundary; `Profile` declares legal transitions; `RouterEngine` decides; `PrivateRouterClient` only projects a validated decision. No new runtime dependency or persistence adapter. |
| Logic correctness | PASS — reviewed `contracts.py`, `profile.py`, `router.py`, and `private_router.py`; direct and indirect regression tests prove the declared handoff route, blocked return, and requirement-change route. |
| Boundary and exceptions | PASS — strict models reject unexpected locator-like fields, absent/blank identifiers, empty collections, event conflicts, invalid front-end contract, and role collision. Existing adapter failure tests remain green. |
| Security and performance | PASS — handoff/completion models permit opaque IDs and digests, never paths, URIs, prompt/source text, secrets, or PII; the added route is in-process constant-size metadata validation with no I/O or loop. |
| Tests and smoke | PASS — 73 deterministic tests plus direct mutation proof. Metadata-only router smoke proves one re-route and no unsafe grant for failed handoff/return. |
| Dependencies | PASS — no dependency added or upgraded. |
| Specification / ticket / Context traceability | PASS — change, Context, approved SPEC, ticket, owners, worktree, TDD evidence, implementation commits, and review result are linked in the ticket and `WorkProgressReport.md`. |

## CodeReview.md §2.1 defect checks

| Category | Result |
| --- | --- |
| 1. Path-prefix mismatch | PASS — `test_handoff_contracts_reject_locator_and_empty_boundary_inputs` rejects exact, prefix-plus, trailing slash, case, encoded, traversal, and empty unknown `source_path` forms. `extra="forbid"` means no locator route reaches source resolution. |
| 2. null / empty values | PASS — the same boundary test covers `null`, empty string, whitespace, empty tuple, list, and dict for required IDs/references/statuses. |
| 3. authorization bypass | PASS — reviewed from the two composition roots: direct `RouterEngine.decide()` and `PrivateRouterClient.route()`. Both bare ticket-approval paths halt; valid handoff advances. The mutation test confirms the direct guard is material. |
| 4. token format / comparison | N/A and checked — no credential/token was added; opaque metadata IDs are structural identifiers, not secrets. No credential comparison exists in the changed paths. |
| 5. error-code consistency | PASS — private failures project to the stable public `ROUTER_POLICY_BLOCKED`; direct Router retains typed internal blocker codes with no source/profile disclosure. |
| 6. external exception | PASS for this slice — new code performs no external I/O. Existing private client/service exception boundaries remain in the green suite; validation errors are explicit, typed failures. |
| 7. actual test coverage | PASS — each ticket TDD cut maps to direct/private tests and the full suite. The missing-handoff mutation made its assertion fail. Historical Pydantic boundary tests honestly passed first because prior strict validation already enforced the rule; no fabricated red result is claimed, and this does not leave an uncovered changed behaviour. |

## Residual limits and handoff

- This is a local, metadata-only POC. It does not start a model, Temporal worker, MCP server, provider, network service, or host-controlled automatic turn.
- The Router can classify and continue one legal action; a host may still end a session or require its own approval. That platform boundary is documented, not bypassed.
- The next legal workflow state after this approved review is `HANDOFF`. A new or changed requirement must emit `REQUIREMENT_CHANGED` and return to Grill; no unapproved implementation is auto-started.
