# WA-01 | Activation and host-gate contracts

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-WA-01` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01` / AC-1, AC-2 and the strict-contract portion of AC-9 |
| Requirement / Context / ADR | `PRD-20260829-048` / `CHG-20260829-048` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` Revision 01, SHA-256 `23cb8df55a9cf69730e7bff6303af1705dc7b479c1bd1a72e033ac6fed2bdd9e` / `ADR-20260829-036` |
| State / closure | `PLANNED / OWNER_TICKET_APPROVAL_PENDING / NON_DISPATCHABLE`; `CLOSURE-PLUGIN-ADOPTION-QUALITY-WA-01`, revision 01 |
| Document revision | `01` |
| Opening authority | Project owner approved architecture candidate `d684f1479573475c82cad7d4a4abecc60e9665e3`, authorizing reviewer opening of `WA-01` only. This ticket still requires exact owner approval before dispatch. |
| Source baseline / dependency | `5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4`; no source ticket dependency. Candidate must descend from the committed ticket authority. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; proposed `READY_LOW_MODEL`, one synchronous owner lane and no helper. |
| Worktree / branch / task | After exact ticket approval, reviewer allocates `.worktrees/plugin-adoption-quality-wa-01` on `implement/plugin-adoption-quality-wa-01` from the then-current committed `main`, then binds this exact ticket revision and baseline. Same-lifetime dispatch uses one native call and one wait; no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / STANDARD`; Python 3.11, Pydantic strict models, complete annotations, `mypy --strict`, deterministic pure tests and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This closure is pure contract/planning code. It performs no filesystem, Git, process, environment, network, provider, host CLI, hook, target-project, subagent, publication, installation, release or deployment effect. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/project_adoption_contracts.py
modify = library/workflow_router/project_adoption_contracts.py
create = tests/test_project_adoption_contracts.py
modify = tests/test_project_adoption_contracts.py
create = modules/element/python/plugin-adoption-quality/wa-01-activation-host-gate-contracts/
modify = modules/element/python/plugin-adoption-quality/wa-01-activation-host-gate-contracts/
forbid = library/workflow_router/__init__.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/router.py
forbid = library/workflow_router/profile.py
forbid = library/local_orchestration/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create one private module, `library/workflow_router/project_adoption_contracts.py`, whose public
surface inside that module freezes the strict activation contract family and one pure planner:

```python
plan_project_activation(request: ProjectActivationRequest) -> ProjectActivationResult
```

The request binds one `request_ref`, canonical repository ID, `SupportedHost`, matching
`HostInstructionKind`, expected target-document ID, exact expected current SHA-256, ephemeral
current document text, installed plugin ID/version and takeover skill ID. The planner recognizes
one fixed, versioned Johnny activation-block marker pair and returns exactly one tagged result:

```text
PLANNED(CreateBlockPlan | UpdateBlockPlan | NoChangePlan)
| REFUSED(STALE_PRESTATE | HOST_KIND_MISMATCH | BLOCK_DUPLICATED
          | BLOCK_MALFORMED | INPUT_INVALID)
```

Create and update plans carry exact expected pre/post digests and the complete proposed target text.
`NoChangePlan` carries the verified existing digest and no replacement text. Refusal variants carry
only `request_ref`, one finite reason and a bounded field identifier; no variant uses action-
dependent nullable fields. The planner preserves every byte-equivalent character outside the one
delimited block, is deterministic and performs no write/readback itself.

The module also freezes `ActivationState`, `ActivationAction` and
`HostBehaviorGateState = HOST_GATE_ENFORCED | INSTRUCTION_ONLY | UNAVAILABLE` plus a strict
`HostBehaviorGateClassification`. It never derives `HOST_GATE_ENFORCED` from an instruction,
manifest, requested plan or caller claim. WA-02 will own effect adapters and evidence-qualified
classification; this ticket supplies only the finite contract.

The exact version-1 block grammar is:

```text
<!-- johnny-ai-skill:project-adoption:v1:begin -->
For software-change work in this repository, load and follow the installed
`{skill_id}` skill from plugin `{plugin_id}` version `{plugin_version}` as the entry route.
Load only the stage/reference it routes. If that installed identity is absent or stale,
stop before governed mutation and report the mismatch; do not copy plugin governance here.
<!-- johnny-ai-skill:project-adoption:v1:end -->
```

The strict patterns are `plugin_id = [a-z0-9][a-z0-9-]{0,63}`,
`plugin_version = [0-9]+(?:\.[0-9]+){2}(?:-[a-z0-9.-]+)?`, and
`skill_id = [a-z0-9][a-z0-9-]{0,63}:[a-z0-9][a-z0-9-]{0,63}`. Backticks, braces,
whitespace, control characters, slashes, URLs and marker text reject. The planner emits exactly
this LF-normalized block internally while preserving the target document's existing outside text
and newline convention at the insertion/replacement boundary.

`TicketDecompositionDecision = READY_LOW_MODEL`: one pure strict contract/planner closure has no
provider, host, filesystem or integration effect and leaves no unresolved architecture decision.

## Frozen contract and responsibility rules

- Reuse the existing `workflow-router-poc` strict `RouterModel` convention from
  `library.workflow_router.contracts`; do not modify or re-export it.
- `SupportedHost.CODEX` accepts only `CODEX_AGENTS`; `CLAUDE_CODE` accepts only
  `CLAUDE_PROJECT_INSTRUCTION`. Cross-pairs refuse with `HOST_KIND_MISMATCH`.
- Digests are lowercase 64-character SHA-256 values over UTF-8 bytes. The caller's expected digest
  is checked against the supplied ephemeral text before any plan is returned.
- There is exactly zero or one well-formed activation block. Duplicate, nested, reversed or partial
  markers refuse; the planner never chooses first-match-wins.
- Block content is derived only from bounded plugin ID/version, skill ID and canonical fixed prose
  declared in this module. It cannot carry raw governance/reference bodies, prompts, secrets,
  absolute paths, URIs or host transcripts.
- A large outside document is not rejected by size. Its outside text must remain exact.
- The module stays private: `library.workflow_router.__init__` remains byte-identical.

### Reusable-module selection record

```text
selected: workflow-router-poc@5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4
why: strict immutable RouterModel and finite-state contract conventions match this pure planner.
read: MODULE_CATALOG -> workflow-control index -> workflow_router/README -> public __init__
      -> contracts.py RouterModel.
dependency: none beyond existing Pydantic/Router contract primitives.
rejected: artifact-tree and host-effect implementations; they own different closures.
boundary: no adapter, filesystem, host hook, dispatch, repository gate or package export.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| WA1 | Every enum, request and tagged result constructs through ordinary strict validators and JSON round-trips. Empty/whitespace IDs, wrong enum primitives, extra fields, `None`, malformed digests, raw paths/URIs and contradictory variant fields reject. |
| WA2 | An absent block with a matching empty/current-document digest returns deterministic `CreateBlockPlan`; applying its proposed text in the test fake yields the exact post-digest and preserves the original document text around the insertion point. |
| WA3 | One existing older/different Johnny block returns `UpdateBlockPlan`; only the bytes between exact markers change. Prefix, suffix, newline convention and unrelated instruction text remain exact. |
| WA4 | Exact current content returns `NoChangePlan` with no replacement field. Repeating the request produces byte-identical serialized output. |
| WA5 | Wrong pre-digest, host/instruction-kind cross-pair, duplicate/nested/reversed/partial marker and mismatched installed identity each return the named finite refusal with no proposed text. |
| WA6 | `HostBehaviorGateClassification` represents all three states, but no activation-planner result can contain or imply `HOST_GATE_ENFORCED`; a manifest/instruction-only fixture remains exactly `INSTRUCTION_ONLY`. |
| WA7 | AST/source checks prove a single planner entry, tagged no-null variants, SHA-256 use, private-module boundary and absence of filesystem/process/network/environment/provider/host/subagent/Git/importlib/dynamic lookup/`Any`/`cast`/raw-mapping effects. |
| WAM1 | Reverse-mutate the digest check to trust the caller; WA5's stale-prestate case turns red, then exact restoration returns green. |
| WAM2 | Reverse-mutate update composition to normalize or drop outside text; WA3 turns red, then exact restoration returns green. |
| WAM3 | Reverse-mutate marker resolution to first-match-wins; the duplicate-marker WA5 case turns red, then exact restoration returns green. |

Strong-type preflight constructs every success/refusal variant through ordinary public validators
and round-trips. Negative cases may use malformed raw input only to prove rejection; they are not
success evidence. This is new behavior, so no ceremonial baseline-red claim is required.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_project_adoption_contracts.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_workflow_router.py
py -3.11 -m mypy --strict library/workflow_router/project_adoption_contracts.py tests/test_project_adoption_contracts.py
py -3.11 -m compileall -q library/workflow_router/project_adoption_contracts.py
git diff --check 5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4 HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket blob/baseline/boundary, ordinary-constructor
preflight, tagged no-null plan shapes, outside-text preservation, host asymmetry and no-effect
private-module boundary. It reruns focused/regression/type/compile gates and performs one independent
counter-mutation not selected by the implementer. Any full-suite failure is compared unreduced with
clean `main`; no baseline failure is reported as candidate success.

## Ownership and return

After exact ticket approval, the Terra/xhigh reviewer dispatches once, waits once, reviews, commits
the candidate and submits it to `admit_document_mutation`. The Luna/xhigh implementation owner
modifies only the declared source/test/element paths, does not commit or push, and cannot change the
SPEC, Context, ticket, host adapter, profile or other Agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with WA/WAM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes adapter/hook implementation, target
mutation, dispatch proof, integration, push, publication, installation, release or deployment.
