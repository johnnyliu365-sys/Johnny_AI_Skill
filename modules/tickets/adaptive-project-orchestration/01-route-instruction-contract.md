# R01 — Versioned Route Instruction Contract

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 02 / AC-12 through AC-14 shared route precondition |
| Change / ADR | `CHG-20260814-019`; `ADR-20260814-011` |
| State | `IN_PROGRESS / IMPLEMENTATION_DISPATCH_CONFIRMED` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R01-01` / R1-R7 revision 01 |
| Baseline | Router policy freeze `ffc2197f4ac9be495651fd970c0c3f21737aa3bc` |
| Delivery profile | `STANDARD`; one Luna implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Planned implementation owner | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Planned branch | `codex/implementation-router-route-instruction-r01` from the exact registry commit containing `PRG-20260814-444` |
| Dispatch binding | `hnd_adaptive_router_r01_20260814`; `aln_adaptive_router_r01_20260814`; receipt `rcpt_adaptive_router_r01_20260814`; question `q-adaptive-router-r01-20260814`; correlation `corr-adaptive-router-r01-20260814`; side context `scx-adaptive-router-r01-20260814-01` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure typed Router/Profile contracts and tests, no external effect |

## One observable outcome

A caller can evaluate any existing Router state/event and receive one decision that names the
exact versioned skill policy to read and the exact typed return family/events expected from the
selected action. A technical halt or undeclared transition returns the Profile's versioned
`router-control` reference and a no-return contract. No action is selected from model memory.

This ticket does not implement model-role readiness/wake, ticket decomposition, UI/design-source
routing, a policy-file reader/registry, or `ArtifactRef.uri` removal. Those are later closures.

## Frozen public contracts

Add and publicly export these exact finite contracts in `library.workflow_router`:

```text
ReturnContractKind = ROUTER_EVENT | IMPLEMENTATION_RETURN | NO_RETURN

SkillReference = {
  reference_id: OpaqueMetadataId,
  source_revision: RevisionDigest,
  content_digest: EvidenceDigest
}

ExpectedReturnContract = {
  contract_id: OpaqueMetadataId,
  contract_revision: RevisionDigest,
  return_kind: ReturnContractKind,
  router_events: tuple[RouterEventKind, ...],
  implementation_statuses: tuple[ImplementationReturnStatus, ...]
}
```

`SkillReference.reference_id` additionally rejects locator/sensitive markers `://`, `\`, `/`,
`prompt` and `secret` after case normalization; the shared opaque-ID regex alone is not
sufficient. A reference is resolved by a later registry boundary, never by treating the ID as a
path or URI.

`ExpectedReturnContract` validates ordinary public construction and JSON round-trip:

- `ROUTER_EVENT`: one or more unique `router_events`, zero implementation statuses;
- `IMPLEMENTATION_RETURN`: one or more unique implementation statuses, zero router events;
- `NO_RETURN`: both tuples empty;
- every wrong, missing, extra, null, duplicate or mixed-family shape fails strict validation.

`TransitionRule` requires one `skill_reference` and one `expected_return`. A
`ProjectWorkflowProfile` requires one `router_control_reference` and one
`halt_return_contract`, whose kind must be `NO_RETURN`. `RouterDecision` requires and serializes
one `skill_reference` and one `expected_return`; neither is optional and neither accepts a raw
path, URI, prompt, policy body, Secret or descriptive fallback.

## Exact source boundary

- `library/workflow_router/contracts.py`
- `library/workflow_router/profile.py`
- `library/workflow_router/router.py`
- `library/workflow_router/__init__.py`
- `tests/test_workflow_router.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

No other production/test/document path is writable. Existing `ArtifactRef` and Context routing
behavior are preserved byte-for-behavior in this closure.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `R1` | Both new public models and the enum construct and JSON round-trip through ordinary strict constructors for every valid finite family. The complete wrong/null/empty/extra/duplicate/mixed matrix fails. |
| `R2` | Every `TransitionRule` and `ProjectWorkflowProfile` from `build_router_poc_profile()` has one non-empty versioned policy reference and one valid expected-return contract; the Profile fallback is exact `router-control` plus `NO_RETURN`. |
| `R3` | Every successful/retry decision copies the selected rule's exact reference and expected return. Every declared human wait uses that rule's exact contract. |
| `R4` | Delivery mismatch, topology mismatch, blocked implementation return, retired transition, missing/ambiguous source, invalid receipt/proposal/pending descriptor and undeclared transition all return the exact Profile router-control/no-return fallback before capability or effect. |
| `R5` | Decision serialization contains only the three reference metadata fields and finite expected-return fields; it contains no raw path, URI, policy text, prompt, Secret or exception detail introduced by this ticket. |
| `R6` | Existing Router/private-router/collaboration/guarded-integration behavior remains green. No new policy reader, model invocation, task/worktree/Git/host/network effect or `ArtifactRef` migration occurs. |
| `R7` | Two bounded reversals are proven and exactly restored: making `TransitionRule.skill_reference` optional turns the required-field test red; substituting the Profile fallback for one successful declared route turns the exact-copy test red. |

## TDD and source gates

First red imports `SkillReference`, `ExpectedReturnContract` and `ReturnContractKind` from the
public package and fails because they do not exist. Before production mutation, retain the exact
ImportError text and confirm the current focused Router regression is `90/90`.

Committed tests must inspect the new class/field annotations and validators and reject `Any`,
`object`, `type: ignore`, cast, optional/None success fields, dynamic member lookup, Pydantic
construct/update bypass and broad catches introduced in the new contract surface. Existing
legacy code outside the new symbols is not silently rewritten or used as positive evidence.

Verification is one focused `tests.test_workflow_router`, the existing six-module Router suite,
the full explicit serial unittest suite, strict full-tree mypy with an external removable cache,
in-memory compile, exact five-file implementation diff, source sentinel, topology, tracked and
ignored porcelain, and cache/runtime/bytecode absence.

## Return and safety

Return one implementation commit containing exactly the five implementation paths, then one
separate WPR-only handoff commit with first-red, R1-R7, both reversal reds/restorations and all
verification identities. `ImplementationReturn` is `COMPLETED`, `BLOCKED` or `CHANGE_DETECTED`.

No helper/subagent, new worktree, self-review/integration, next ticket, 06G0P mutation, live
model/Figma/Codex/home/App/target-project/network effect, push/staging publication, package,
install, Secret, release or deployment.
