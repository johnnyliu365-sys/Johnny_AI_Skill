# R01 — Versioned Route Instruction Contract

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 02 / AC-12 through AC-14 shared route precondition |
| Change / ADR | `CHG-20260814-019`; `ADR-20260814-011` |
| State | `CHANGES_REQUESTED / REVISION_03_REFROZEN` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R01-03` / R1-R7 plus CR-R01-001 through CR-R01-004 |
| Baseline | Router policy freeze `ffc2197f4ac9be495651fd970c0c3f21737aa3bc` |
| Delivery profile | `STANDARD`; one Luna implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Planned implementation owner | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Planned branch | `codex/implementation-router-route-instruction-r01` from the exact registry commit containing `PRG-20260814-444` |
| Dispatch binding | `hnd_adaptive_router_r01_20260814`; `aln_adaptive_router_r01_20260814`; receipt `rcpt_adaptive_router_r01_20260814`; question `q-adaptive-router-r01-20260814`; correlation `corr-adaptive-router-r01-20260814`; side context `scx-adaptive-router-r01-20260814-01` |
| Correction binding | `hnd_adaptive_router_r01_r02_20260814`; review baseline `334935dfd557e7d244b31de37e80db8911f27069`; same allocation/receipt/owner/branch; additive after handoff `a16dfc38eb6141e2aef5fa480be741b1f057ca57` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure typed Router/Profile contracts and tests, no external effect |

## One observable outcome

A caller can evaluate any existing Router state/event and receive one decision that names the
exact versioned skill policy to read and the exact typed return family/events expected from the
selected action. A technical halt or undeclared transition returns the Profile's versioned
`router-control` reference and a no-return contract. No action is selected from model memory.

`expected_return` always describes the typed result expected from the **primary next action
selected by this decision**. It never repeats the event that entered the Router merely because
that event selected the transition.

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

## Revision-02 exact Profile route table

The following table is exhaustive for the existing POC Profile. `EVENT(...)` means
`ReturnContractKind.ROUTER_EVENT`; `IMPLEMENTATION(...)` means
`ReturnContractKind.IMPLEMENTATION_RETURN`. The contract ID is
`return-<current-stage>-<input-event>`, and its revision equals the selected skill reference's
`source_revision`. The `IMPLEMENTATION_DISPATCH_CONFIRMED` row describes the primary planning
lane continuation; the independently admitted ticket lane continues to use its already frozen
`ImplementationReturn` handoff contract.

| Current stage / input event | Exact skill reference ID | Exact expected return |
| --- | --- | --- |
| `INTAKE / INTAKE` | `discovery-change` | `EVENT(WAYFINDER_GO, WAYFINDER_NO_GO)` |
| `WAYFINDER / WAYFINDER_GO` | `discovery-change` | `EVENT(ACTION_COMPLETED)` |
| `WAYFINDER / WAYFINDER_NO_GO` | `router-control` | `NO_RETURN` |
| `ARCHITECTURE / ACTION_COMPLETED` | `discovery-change` | `EVENT(ACTION_COMPLETED)` |
| `GRILL / ACTION_COMPLETED` | `context-routing` | `EVENT(ACTION_COMPLETED)` |
| `CONTEXT / ACTION_COMPLETED` | `specification-ticketing` | `EVENT(ACTION_COMPLETED)` |
| `SPEC / ACTION_COMPLETED` | `specification-ticketing` | `EVENT(APPROVAL_GRANTED, APPROVAL_DENIED)` |
| `SPEC / APPROVAL_GRANTED` | `specification-ticketing` | `EVENT(TICKET_DISPATCH_REQUIRED)` |
| `TICKETS / TICKET_DISPATCH_REQUIRED` | `implementation-authority` | `EVENT(IMPLEMENTATION_DISPATCH_CONFIRMED)` |
| `TICKETS / IMPLEMENTATION_DISPATCH_CONFIRMED` | `discovery-change` | `EVENT(ACTION_COMPLETED)` |
| `IMPLEMENT / IMPLEMENTATION_RETURNED` | `implementation-tdd` | `EVENT(VALIDATION_PASSED, VALIDATION_FAILED)` |
| `GRILL / INTEGRATION_COMPLETED` | `discovery-change` | `EVENT(ACTION_COMPLETED)` |
| `GRILL / AUDIT_COMPLETED` | `review-checks` | `EVENT(ACTION_COMPLETED)` |
| `IMPLEMENT / ACTION_COMPLETED` | `implementation-tdd` | `EVENT(VALIDATION_PASSED, VALIDATION_FAILED)` |
| `SMOKE_TEST / VALIDATION_PASSED` | `review-checks` | `EVENT(ACTION_COMPLETED)` |
| `SMOKE_TEST / VALIDATION_FAILED` | `implementation-tdd` | `IMPLEMENTATION(COMPLETED, BLOCKED, CHANGE_DETECTED)` |
| `REVIEW / ACTION_COMPLETED` | `review-checks` | `EVENT(ACTION_COMPLETED)` |
| `HANDOFF / ACTION_COMPLETED` | `router-control` | `NO_RETURN` |
| `IMPLEMENT / REQUIREMENT_CHANGED` | `discovery-change` | `EVENT(ACTION_COMPLETED)` |

## Revision-02 exact policy metadata

Production does not read these files. The Profile stores the following real metadata frozen
from the Router policy baseline; tests independently hash the files and compare exact bytes.

| Reference ID | Source revision | Content digest |
| --- | --- | --- |
| `router-control` | `rev-23dd53ad68e5562f` | `sha256_23dd53ad68e5562f39a35f06f9c21a970b6eb94eab3aeeae468cc8b5cd68b091` |
| `discovery-change` | `rev-5d432a8246bce4ed` | `sha256_5d432a8246bce4ed890289e24c50e2e29360df165eeb7f9355cb02228e1d10ef` |
| `context-routing` | `rev-5f1e7958c70c8493` | `sha256_5f1e7958c70c8493de83aa1481e0f3f3e59c5a40e745a12077eb372fa6e0815e` |
| `specification-ticketing` | `rev-c7011f440caa3ec8` | `sha256_c7011f440caa3ec8fe83e119a110aa368ec4cc130cf71671d0199987140c8af7` |
| `implementation-authority` | `rev-855117ed19c9c952` | `sha256_855117ed19c9c952f8903bc56ce070d2cf3805fb51d7a450c46bbf8a00480f50` |
| `implementation-tdd` | `rev-38408006f23df3b6` | `sha256_38408006f23df3b66a4368e2b8794cc099b84ea20417e56d881ff19512345574` |
| `review-checks` | `rev-4b8527305609194a` | `sha256_4b8527305609194ae9dd26c16a05ff72d22b1f20a8cb925175d6793766bb5f54` |

`SkillReference` rejects an all-zero revision or all-zero content digest. Within one Profile,
one `reference_id` may repeat only with identical revision/digest metadata. Every rule's return
contract revision must equal its skill reference revision; the fallback pair follows the same
rule. A conflicting reference ID or revision mismatch fails Profile construction before any
Router capability/effect.

Revision-02 tests replace the incoming-event assertion with the exhaustive table above and
verify real file hashes. Required reversals: restoring the incoming-event echo makes the
`INTAKE` direction test red; replacing one real digest with the all-zero placeholder makes the
policy-authenticity test red. Both are restored exactly before final verification.

## Revision-03 P0 source-type closure

No route value, policy ID, revision, digest, contract, validator or public behavior changes in
this revision. The correction is limited to these exact type/evidence requirements:

- production `_PolicyRoute.reference_id`, the Profile reference-map key and
  `_policy_reference_for` parameter use `OpaqueMetadataId`;
- `_POLICY_REFERENCES: tuple[SkillReference, ...]` and
  `_POLICY_ROUTES: tuple[_PolicyRoute, ...]` are explicit;
- the local generated contract ID is explicitly `OpaqueMetadataId`;
- test `_ExpectedRoute.reference_id` uses `OpaqueMetadataId`;
- test `_ExpectedPolicy` uses `OpaqueMetadataId`, `RevisionDigest`, `EvidenceDigest` and
  `PurePosixPath` for its four domain fields;
- `_EXPECTED_ROUTES: tuple[_ExpectedRoute, ...]` and
  `_EXPECTED_POLICIES: tuple[_ExpectedPolicy, ...]` are explicit;
- policy hash evidence reads the typed policy path directly, canonicalizes only CRLF to LF,
  hashes those bytes and does not import/call `subprocess` or Git;
- the AST source gate includes `_PolicyRoute`, `_ExpectedRoute`, `_ExpectedPolicy` and the four
  named module constants, rejecting raw `str` domain fields/parameters and missing annotations.

Required revision-03 reversals: changing `_PolicyRoute.reference_id` back to `str` turns the
P0 source gate red; deleting one named tuple annotation turns the same gate red. Restore both
exactly, then rerun the unchanged revision-02 route/hash oracle and all prior verification.

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
