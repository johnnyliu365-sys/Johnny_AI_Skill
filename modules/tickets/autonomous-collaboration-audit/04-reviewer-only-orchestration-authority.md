# 04 — Reviewer-only Orchestration Authority

| Field | Value |
| --- | --- |
| SPEC / change | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` revision 02 / `CHG-20260811-012` |
| State | `PLANNED / DEPENDENCY_WAIT` |
| Closure | `CLOSURE-AUTONOMOUS-COLLAB-T04-01` / R1-R4 |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |
| Dependency | Tickets 01-03 integrated; starts only after local 06A returns a reviewed `SUPPORTED` capability result and the sole implementation lane is released |
| Implementation owner | Existing task `019fcc9c-f34f-7d53-a313-c70c90bf3245` in the sole implementation worktree after its own receipt |
| Reviewer | Control-plane `main`; sole Agent-to-Agent orchestrator |
| Environment | Python 3.11 typed fake effect port; no real Agent/thread, target-project, network, Secret, push, release or deployment |

## One outcome

Add a typed authorization boundary in front of every Agent-to-Agent effect.
Only the exact reviewer grant may invoke one finite action against the named
implementation owner. Implementation-owner and forged/replayed paths return a
finite block before the fake port records an effect.

## Exact scope

- `library/workflow_router/contracts.py`
- new `library/workflow_router/orchestration_authority.py`
- `library/workflow_router/__init__.py`
- `skills/johnny-project-takeover/SKILL.md`
- new `tests/test_reviewer_orchestration_authority.py`
- `tests/test_plugin_policy_and_response.py`

No host SDK, Codex configuration, local installer, Git effect, model turn or
target-project file belongs to this ticket.

## Acceptance closure — `CLOSURE-AUTONOMOUS-COLLAB-T04-01`

| ID | Acceptance |
| --- | --- |
| `R1` | Finite `AgentRole`, `OrchestrationAction`, exact grant/request and closed authorized/blocked result types carry only opaque metadata. No nullable role/owner/effect port or generic string action exists. |
| `R2` | One exact named reviewer request matching project, ticket, reviewed handoff, unconsumed receipt, target implementation owner, action and correlation records exactly one fake effect and consumes that action binding. |
| `R3` | Implementation-owner direct request and an indirect wrapper path each return `ROLE_FORBIDDEN` before the fake effect. Generic control-plane capability, copied/forged reviewer, wrong ticket/handoff/receipt/target/correlation and replay also record zero effects with their finite reason. |
| `R4` | Takeover policy names the reviewer as sole orchestrator and implementer as non-delegating ticket worker. Policy is not used as the authority input; removing the typed role/receipt checks still fails executable regressions. |

## TDD matrix

- Path/identity boundary: exact, one-extra-character, trailing separator, case,
  encoded, traversal and empty values for any locator-like metadata; opaque IDs
  reject paths/URIs.
- Null/empty: omission, null, empty, whitespace, `[]` and `{}` for role,
  reviewer, owner, receipt, action and correlation.
- Authority bypass: direct implementation request, indirect adapter, generic
  control-plane substitution, forged reviewer, wrong target and replay.
- Token: N/A source sentinel rejects token/secret/credential fields.
- Errors/exceptions: every block has one external code and one internal finite
  reason; fake-port ordinary failure returns a finite effect failure while
  process-control exceptions are not broadly caught.
- Test truth: reverse role validation and receipt consumption independently;
  each matching test must fail before restoration.

## Return

First-red, focused/full unittest, strict mypy, in-memory compile, skill
validator/policy tests, source/scope/diff and zero-residue evidence. One
implementation commit, then one `WorkProgressReport.md`-only handoff. The
implementation owner cannot dispatch, review, integrate or control another
Agent.
