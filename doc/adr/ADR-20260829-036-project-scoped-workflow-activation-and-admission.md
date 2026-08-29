# ADR-20260829-036 — Project-scoped workflow activation and admission

- Date: `2026-08-29 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision maker: Project owner
- Related change: `PRD-20260829-048` / `CHG-20260829-048`
- Refines: `ADR-20260828-031`; it does not weaken the repository gate or reopen R09B2.

## Context

Installed use has shown that rules available only after the takeover skill is selected do not
reliably become the first action of a new host session. The current package exposes skills, while
the unfinished Revision 09 still lacks its repository-admission, host-behavior and installed-
qualification closures. Consequently the model can create a formal leaf without its index, write
multiple responsibilities into one module, or implement work itself before it loads the rule that
required a lower-tier owner.

These failures do not share one enforcement mechanism. Source and document shape can be validated
from the ticket and candidate tree. A native subagent call cannot be reconstructed from Git. One
layer must not claim to prove what belongs to another.

Claude's official [hooks guide](https://code.claude.com/docs/en/hooks-guide) and
[hooks reference](https://code.claude.com/docs/en/hooks) document project-scoped hooks and
pre-tool blocking; this is the capability basis for the optional Claude adapter, not evidence that
any particular target has enabled or passed it.

## Decision

Adopt four independent layers:

1. **Project activation.** An explicit adoption operation plans one bounded block in each selected
   host's auto-loaded project instruction file. Codex and Claude Code have separate adapters and
   readback; neither adapter is evidence for the other. The target owner approves that mutation.
   The block names the installed takeover skill and requires it as the entry route for software
   changes; it does not copy Workflow or references. It is conditional on skill availability and
   remains harmless after plugin removal.
2. **Project host behavior gate.** Host enforcement is an optional, separately classified layer.
   Claude Code may use an owner-approved project `.claude/settings.json` `PreToolUse`/`Stop` hook
   backed by a target-owned, self-contained script. It may block classifiable direct-write bypasses
   and request bounded correction, but cannot replace repository admission or import the plugin at
   target runtime. Codex remains `INSTRUCTION_ONLY` unless an equivalent installed host surface is
   independently proven. Host asymmetry is reported, not hidden.
3. **Repository admission.** Integration derives the managed-document and source path sets from the
   actual candidate. Document admission validates every selected ancestor edge through the declared
   root. Responsibility admission validates a ticket-owned responsibility/dependency contract with
   the chosen language's strict plus AST/source/schema checks. Either refusal leaves the authority
   ref unchanged.
4. **Host orchestration observation.** A live reviewer owns native same-lifetime delegation and one
   completion wait. Evidence is `HOST_PROVEN` only when the host supplies a callback/readback that
   the caller cannot forge. Otherwise it is honestly `REVIEWER_OBSERVED`; absence is
   `UNAVAILABLE`. Git author, branch, prompt or receipt text is never upgraded into proof.

The per-project capability state is reported separately:

```text
ActivationState = ACTIVE | ABSENT | STALE | HOST_SURFACE_UNAVAILABLE
HostBehaviorGateState = HOST_GATE_ENFORCED | INSTRUCTION_ONLY | UNAVAILABLE
AdmissionState  = LOCAL_GATE_ENFORCED | REMOTE_GATE_ENFORCED | UNAVAILABLE
DispatchEvidence = NOT_REQUIRED | REVIEWER_OBSERVED | HOST_PROVEN | UNAVAILABLE
```

`REMOTE_GATE_ENFORCED` additionally requires the declared authority ref's remote rules to prevent
bypass; local gate success alone never implies it.

## Responsibility and composition map

- `ProjectAdoptionPlanner` is pure. It receives canonical repository identity, host kind and the
  exact current instruction-file digest, then returns a create/update/no-op plan.
- One host-specific `ProjectInstructionAdapter` applies an owner-approved plan and reads back the
  resulting digest. It has no Git integration or subagent authority.
- An optional `ProjectHostBehaviorGateAdapter` plans, applies and reads back only the target-owned
  project hook/config. It has neither repository authority nor a plugin-cache/runtime dependency.
- `ArtifactTopologyAdmissionPort` owns document-tree validation only.
- `ResponsibilityBoundaryAdmissionPort` owns ticket-declared responsibility/dependency validation
  only and delegates language syntax to bounded adapters.
- `NativeDispatchCoordinator` exists only inside the live reviewer session. It does not write
  durable receipts or claim host provenance unavailable to it.
- `WorkflowIntegrationAdmission` is the Composition Root that evaluates independent results and
  invokes the existing authority-line gate only after all applicable results are accepted.

## Consequences

- The first implementation sequence is activation/host-gate contracts and readback,
  document-topology repository admission, responsibility-boundary admission, native-dispatch
  behavioral qualification, then installed cross-host readiness. Shared `PAQ-REL-01` performs the
  later selected release composition.
- Cross-host means mandatory Codex and Claude Code qualification with the same public contracts and
  independent host evidence. A single-host pass is an incomplete cluster, not a reduced success.
- Revision 09's R09C purpose is retained and may be satisfied by the document-admission slice; its
  unavailable local transactional writer is not a prerequisite for read-only candidate refusal.
- No generic line-count or file-count threshold becomes architecture policy.
- Hosts without native dispatch provenance still improve default routing, but the UI/report must
  label the result `REVIEWER_OBSERVED`, not enforced.
- Behavioral release evidence uses five fresh sessions per host/scenario, accepts route selection at
  four-of-five only when all five avoid forbidden effects, and forbids retry-until-green. Evidence
  binds versioned fixture, host/plugin/model semantic-profile versions and bounded outcome digests.
- WA/UIX cluster closure produces readiness only. One shared `PAQ-REL-01` owns any version bump,
  regeneration, repin, tag, publication and installed readback; clusters ready at one baseline ship
  once rather than racing two release effects.

## Alternatives rejected

- **Add more takeover prose.** It is unavailable before skill activation and cannot reject a bad
  candidate.
- **Use Git shape as dispatch proof.** The reviewer can create the same branch, author and commit;
  the evidence is caller-forgeable.
- **Install machine-global instructions.** They affect unrelated projects and violate scoped
  capability adoption.
- **Treat a Claude project hook as repository authority.** It improves host behavior but remains
  bypassable/disableable host configuration; final integration authority stays in repository
  admission.
- **Reject large files.** Size correlates weakly with responsibility and produces false confidence.
- **Require a runner/receipt.** Same-lifetime delegation already has a live reviewer and native
  wait; a cross-lifetime bridge solves a different problem.

## Approval boundary

This accepted ADR authorizes reviewer opening of `WA-01` only. Ticket approval and dispatch remain
separate. It grants no target instruction/hook mutation, source implementation, dispatch,
publication, installation or release.
