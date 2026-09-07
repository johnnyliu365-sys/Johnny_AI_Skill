# WA-02b | Target activation behavioral hook extension proposal

| Field | Value |
| --- | --- |
| Artifact ID / kind / document revision | `TICKET-PLUGIN-ADOPTION-QUALITY-WA-02B` / `IMPLEMENTATION_TICKET_PROPOSAL` / `01` |
| State / closure | `OWNER_EXACT_APPROVAL_PENDING / CAPABILITY_BLOCKED / NON_DISPATCHABLE`; `CLOSURE-WA-02B`, proposed revision 01 |
| Authority / audit baseline | Owner's 2026-09-07 control-plane direction, proposal only; source findings at `afb071b4ced5e92aabf74130ad1678ee4ce725d2`, drafting after HDA-01 commit `37b9e7b333183bbb9123e3d17839b13a44fed598`. No hook source, target mutation, gateway implementation, dispatch, push or release. |
| Lineage | REQ-20260829-048; ADR-20260829-036; SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01 AC-1/2/8/9/10; sealed Context `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` revision 01, read-reference only. |
| Owner / reviewer / implementer | Human owner approves exact proposal and any upstream change; current-session `ticket-review` owns the scope finding. Implementer/task/worktree/branch unassigned. |
| Profile / type / effect | Proposed `POC / HIGH_ASSURANCE`; strict typed host adapters, final schema/checker commands frozen only after qualification. No UI, `XSS_NOT_APPLICABLE`; privileged target configuration is a separate future effect. |

## Task 2 determination: partially covered, not the requested complete closure

The existing [WA-02 revision 01](wa-02-project-activation-host-effect-adapter.md), LF digest
`95fce94a98fb510432d19c3d6d7daaebdc9c4ee14dfbc04ba3e9de2bf2b624e0`, remains byte-identical.
The following are source readbacks, not assumptions from its title:

| Requested behavior | Actual WA-02 span | Determination |
| --- | --- | --- |
| Claude self-contained target hook/config | Lines 60, 91–93, WAE3 at line 126 | Covered as a finite Claude hook bundle, independently read back and not plugin-runtime dependent. |
| Codex project instruction | Lines 58, 91; WAE2 at line 125 | Covered by `CODEX_INSTRUCTION` and `CODEX_AGENTS`. |
| Codex target hook/config, including proposed `.codex/hooks.json` | Request union lines 57–62 has no Codex hook variant | Not covered. `CODEX_AGENTS` is an instruction kind, not a hook API or evidence that `.codex/hooks.json` is supported. |
| SessionStart injects exact WA-01 block; before-Skill governed mutation denial | Observable closure lines 46–87 and deferred TDD lines 115–141 | No such named event/transition acceptance cells; the generic Claude bundle does not close them. |
| Permission to execute now | Lines 9–14 and 143–147 | Still `CAPABILITY_BLOCKED / NON_DISPATCHABLE`, gateway unproved. |

[REQ-048](../../../doc/requirements/active/2026/plugin-adoption-quality/REQ-20260829-048.md)
lines 23–29 distinguish host behavior from repository authority and leave Codex instruction-only
until its surface is proven; lines 42–44 scope target adoption and separately approve the Claude
self-contained hook. [ADR-036](../../../doc/adr/ADR-20260829-036-project-scoped-workflow-activation-and-admission.md)
decision 2 has the same asymmetry. Neither source already approves a Codex hook implementation.
This new proposal records the owner's requested extension rather than silently rewriting WA-02,
the accepted requirement, sealed Context or SPEC. Their required alignment remains owner-pending.

## Proposed closure, not implementation authority

1. **SessionStart activation.** For each qualified host, inject the same bounded version-1 text
   defined by [WA-01](wa-01-activation-host-gate-contracts.md) lines 71–88. Reuse that block's
   derivation from validated plugin ID/version and skill ID; do not create a second prose grammar.
   WA-01 lines 103–105 prohibit governance/reference bodies, prompts, secrets, absolute paths,
   URIs and transcripts in the block. No Workflow or reference prose is copied to a target.
2. **Before-Skill mutation gate.** Until the host observes the required installed Skill invocation
   in the current target/session, deny classifiable governance mutation at PreToolUse with
   `GOVERNANCE_SKILL_NOT_LOADED`. Skill invocation itself and non-mutating inspection remain
   possible, so the gate cannot deadlock activation. A failed/stale/wrong-skill request or merely
   saying that the skill loaded must not unlock the gate. A successful invocation is behavioral
   ordering evidence only, not proof that the model obeyed it or that a later mutation is approved.
3. **Two independent adapters.** Claude target `.claude/settings.json` and self-contained script;
   Codex target hook/config, with `.codex/hooks.json` a **proposed qualification target only**.
   Prove actual supported event/tool schemas and readback for each installed host/version. If a
   host has no `Skill` tool, prove its native equivalent and obtain approval for that mapping;
   do not create a fictional tool, manifest capability or compatibility shim.
4. **Target-owned, project-scoped execution.** Hook implementation and config must execute without
   importing plugin cache, Johnny runtime, user-home scripts or another repository. Only the
   bounded activation block names the installed skill. Target adoption uses its separately
   approved exact plan and qualified gateway; this proposal supplies no target write grant.
5. **Honest lifecycle and isolation.** Session/target/version changes invalidate any prior load
   observation. Missing, disabled, stale, bypassed or unqualified hooks remain `INSTRUCTION_ONLY`
   or `UNAVAILABLE`, never `HOST_GATE_ENFORCED`. Detach preserves target files and the remaining
   block is harmless when the skill is absent. No runner/queue/receipt/descriptor is introduced
   as a prerequisite for same-lifetime delegation.

## Frozen meaning still required before dispatch

The later owner-approved closure must enumerate which governed operations and actual host tools
are intercepted (including supported edit/write and shell bypasses), exact event-order semantics,
successful Skill-load observation, session-state ownership, restart/compaction behavior and bounded
error handling. It must define the final strict DTOs, source/test/element paths, commands and
capability evidence references. No source boundary is writable from this proposal.

The hook is not a repository admission gate and cannot police an unobservable arbitrary external
write. A host timeout/failure that permits a tool to run is a qualification finding, not fail-closed
success. Codex and Claude qualification cannot borrow results from one another.

## Proposed acceptance matrix

| Cell | Required observation on each separately qualified host |
| --- | --- |
| WAB1 | SessionStart emits the exact WA-01 v1 block and only its allowed fields; duplicated governance prose or mismatched block bytes reject. |
| WAB2 | Before the required successful Skill invocation, each declared governed-mutation path denies with zero mutation; a valid Skill invocation is not itself blocked. |
| WAB3 | Failed/wrong/stale invocation, caller-forged load flag, another session or target cannot unlock; ordinary read-only discovery remains usable. |
| WAB4 | After the correct load, mutation still needs ordinary host permission, ticket boundary and repository admission; activation is not mutation authority. |
| WAB5 | Target script/config executes independently of Johnny runtime/cache; exact target readback, outside-content preservation and separately authorized adoption are required. |
| WAB6 | Disabled/stale/missing/interception-failed hooks classify honestly; plugin detach neither deletes target files nor leaves a runtime import requirement. |
| WAB7 | Codex instruction and hook variants cannot be conflated; absent native hook/Skill-equivalent support is `UNAVAILABLE`, not a fabricated pass. |
| WAB8 | Fixed five-session evidence per host/scenario follows SPEC AC-10; at least four intended routes and all five without forbidden effects. No retry-until-green. |

For every denial, remove the corresponding check in an isolated approved candidate: its named
cell must turn red, exact restoration must return green. Pin candidate/host/profile/fixture
identities and unreduced outputs. The reviewer performs at least one independent attack through
a different entry than the implementer's fixtures; the helper returns findings, never a verdict.
These are future evidence requirements; no mutation/test/host qualification ran while drafting.

## Dependency and return

WA-02 remains `HOST_EXTERNAL_EFFECT_GATEWAY_UNPROVEN`; this proposal neither cures nor bypasses it.
Qualification of a hook event alone does not qualify target adoption's protected effect gateway.
Conversely, this target-write blocker is not a new prerequisite for ordinary same-lifetime dispatch.

Opening return: `ACTION_COMPLETED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING`.
Further implementation remains blocked until exact upstream/closure approval and separate real
capability evidence. Shared PAQ-REL-01 still owns any later release; no release authority is added.
