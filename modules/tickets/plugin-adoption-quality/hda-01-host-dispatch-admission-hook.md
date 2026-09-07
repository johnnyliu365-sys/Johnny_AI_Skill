# HDA-01 | Plugin-shipped host dispatch-admission hook

| Field | Value |
| --- | --- |
| Artifact ID / kind / document revision | `TICKET-PLUGIN-ADOPTION-QUALITY-HDA-01` / `IMPLEMENTATION_TICKET_PROPOSAL` / `01` |
| State / closure | `OWNER_EXACT_APPROVAL_PENDING / NON_DISPATCHABLE`; `CLOSURE-HDA-01`, proposed revision 01 |
| Authority / baseline | Owner's 2026-09-07 control-plane audit direction; draft and index only, based on `afb071b4ced5e92aabf74130ad1678ee4ce725d2`. No source, hook installation, target write, push or release authorization. |
| Lineage | REQ-20260829-048; ADR-20260829-036; SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01 AC-5/6/9 are related behavior, not approval of this new host-level mechanism. Sealed Context `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` revision 01 is reference-only. |
| Owner / reviewer / implementation | Human project owner retains exact approval; current-session `ticket-review` owns this draft. Implementation owner, worktree, branch and host/profile binding remain unassigned. No dispatch. |
| Delivery / language / effects | Proposed `POC / HIGH_ASSURANCE`. Strict typed boundary and non-executing script parser; final language/parser/runtime and strict-check command require qualification before dispatch. No UI rendering; `XSS_NOT_APPLICABLE`, but parsing untrusted script is a security boundary. |

## Source readback and layer distinction

All local citations below were read at the baseline above:

- [REQ-048](../../../doc/requirements/active/2026/plugin-adoption-quality/REQ-20260829-048.md),
  lines 42–44: implicit machine-global **target adoption** is forbidden; an approved target block
  and separately approved self-contained Claude target hook/config are the adoption surface.
- [ADR-036](../../../doc/adr/ADR-20260829-036-project-scoped-workflow-activation-and-admission.md),
  lines 107–111: machine-global instruction copies are rejected; a disableable host hook is not
  repository authority.
- [Dispatch profile](../../../doc/runbooks/dispatch-model-profile.md), lines 27–30, 34–35 and
  83–87: host model values are injected data, `ARCHITECTURE_OWNER` is human, and the old
  provider-specific mapping is retired.
- [WA-02](wa-02-project-activation-host-effect-adapter.md), lines 58–60 and 91–93, owns target
  instruction/hook adoption, not this plugin-enabled host dispatch policy.

This proposal places executable **host behavior configuration** in plugin `hooks/hooks.json`.
It does not place Johnny prose in a user's global instruction file and does not adopt or write a
target repository. Under the owner's proposed distinction, REQ-048 property 1's target-adoption
constraint does not prohibit this separate plugin-host surface. It does not waive target opt-in,
change the accepted SPEC's scope, or authorize an implicit user-settings write. Exact approval
must accept this distinction before implementation; existing SPEC/Context text is not rewritten.

The [Claude hooks reference](https://code.claude.com/docs/en/hooks#hook-locations), read 2026-09-07,
documents plugin hooks as enabled with the plugin. Its
[PreToolUse decision contract](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)
defines denial output. Documentation is not installed-host qualification.

## One proposed observable closure

At `PreToolUse`, matcher exactly `Agent|Workflow`, refuse the following requests before the
matched tool executes. Every refusal emits `permissionDecision = "deny"` and a bounded,
named rule in `permissionDecisionReason`, without copying script, prompt, secret or raw profile.
A valid request makes **no permission grant**: ordinary host approval and repository gates remain.

| Cell / named denial | Input and required result |
| --- | --- |
| HDA1 / `AGENT_MODEL_REQUIRED` | `Agent` lacks `tool_input.model`, or supplies null/empty/whitespace rather than a validated explicit model: deny. No inherited/default model fallback. |
| HDA2 / `ARCHITECTURE_TIER_FORBIDDEN` | `Agent` selects a model mapped by the injected profile to the owner-reserved top tier: deny. No provider/model name literal in hook source. |
| HDA3 / `DISPATCH_PROFILE_INVALID` | Missing, stale, malformed, ambiguous or unsupported injected host/profile mapping, including the reserved-tier mapping: deny; never infer a model from its name. |
| HDA4 / `WORKFLOW_META_INVALID` | Parse the script's single `export const meta` as a pure literal, never evaluate/import/run it. Require `meta.dispatch[]` entries `{label, decision, flips, bound}`. Missing/duplicate/dynamic metadata or malformed entry: deny. |
| HDA5 / `DISPATCH_DECISION_REQUIRED` | Any dispatch entry has empty/whitespace `decision`: deny. |
| HDA6 / `DISPATCH_FLIPS_REQUIRED` | Any dispatch entry has empty/whitespace `flips`: deny. |
| HDA7 / `DISPATCH_LABEL_UNBOUND` | Each parsed `agent(` call's label prefix must uniquely match one declared dispatch entry; absent/dynamic/unmatched/ambiguous label: deny. |
| HDA8 / `DISPATCH_BOUND_EXCEEDED` | Count of parsed `agent(` calls exceeds the sum of validated `bound` values: deny. Bounds must be finite positive integers, with safe summation; invalid bounds deny as `WORKFLOW_META_INVALID`. |
| HDA9 / `WORKFLOW_MODEL_REQUIRED` | Any parsed `agent(` call lacks an explicit validated `model:` field: deny. No inherited/default model. |
| HDA10 / `WORKFLOW_SYNTAX_UNSUPPORTED` | Syntax outside the qualified static grammar, including indirect/aliased/dynamically generated dispatch, is refused rather than executed or silently ignored. |
| HDA11 / `PAYLOAD_HOOKS_MISSING` | The proposed `.claude-plugin/plugin.json` change adds `"hooks"` to `payload.trees`; regenerated payload contains the hook/config and all required local dependencies. A config alone does not prove a working hook. |
| HDA12 / host qualification | On the exact Claude version/profile, real matched invalid tool calls do not dispatch; valid calls remain subject to ordinary permissions. Disabled, missing, crashed or timed-out interception is never reported as enforced. |

The owner-specified static count is a script admission check, **not** proof of runtime fan-out.
Comments/string literals are not call nodes. Loops, recursion, aliases, spreads and computed model
or label values must be refused unless a future approved grammar proves their bounded expansion.
Metadata describes a decision; caller-written metadata is not owner approval or dispatch authority.

## Qualification decisions still open — no implementer may guess

1. The current profile calls `ARCHITECTURE_OWNER` a human, not a model. Define and approve a
   separate injected reserved-tier/model mapping and its provenance/version binding; do not
   relabel Sol or any Claude alias as that human role. Names such as sonnet/opus/haiku/fable may
   appear in qualified **profile data only**, never as hook policy constants.
2. Pin actual `Agent`/`Workflow` tool-input schemas, label-prefix grammar, the nonempty literal
   types of `decision`/`flips`, parser package/version, input/resource bounds and typed DTOs.
   Demonstrate that the installed host emits both tool events. Matcher text is not such proof.
3. Resolve how a direct `Agent` call binds the owner's dispatch decision. The minimal model
   checks above alone do not establish that binding; do not invent an undocumented input field.
4. Qualify profile injection, hook entry/runtime availability and deterministic failure handling.
   A host that lets a timed-out hook continue cannot support an unconditional fail-closed claim.
5. Align the approved SPEC/Context and finite closure with these decisions before marking this
   proposal dispatchable. No frozen meaning is delegated to an implementer.

## Proposed future boundary, not present write authority

The later implementation ticket must name exact files for the hook adapter, pure parser/validator,
profile data seam, strict tests and element index. Proposed shipping entry is `hooks/hooks.json`;
proposed manifest effect is only `.claude-plugin/plugin.json` `payload.trees += "hooks"`.
No skills/reference prose, user-global instruction file, target hook/config, provider call or
repository integration belongs to that source closure. Do not allocate a worktree from this draft.
Shared PAQ-REL-01, after separate authority, owns regeneration/repin/version/tag and installation;
changing an allowlist here would not itself be a release.

## TDD and adversarial evidence required before closure

Every named denial HDA1–HDA11 gets a separate ordinary-constructor negative cell and a valid
control. For **each** rule the reviewer relaxes only that check, reruns its named test and records
red, restores exact source bytes, and records green. A fixture intercepted by another validator
does not prove the intended rule. HDA12 additionally uses the real host boundary and a disabled
hook negative control. Zero red is a finding, not a pass.

Before implementation approval, freeze actual test names, first-red slots, strict-check commands,
candidate SHA and unreduced evidence locations. The single reviewer owns the verdict; a bounded
adversarial helper supplies findings only. No tests, mutations, host effects or dispatch ran while
opening this proposal. `ACTION_COMPLETED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING`.

## Explicit non-claims

The hook is plugin-enabled, disableable host configuration, not repository authority or a global
proof that every agent obeys governance. It does not qualify Codex, enforce target document indexes,
establish a decision's truth, replace reviewer judgment, or prove actual model execution by itself.
Same-lifetime reviewer dispatch/wait/review remains runner/queue/receipt/descriptor-free.
