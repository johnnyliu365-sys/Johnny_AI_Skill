# Controlled verification — DELTA Wayfinder

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `WAYFINDER-CONTROLLED-VERIFICATION-20260909-01` / `WAYFINDER_RESULT` / `01` |
| Lifecycle | `GO / QUALIFICATION_FIRST / NOT_IMPLEMENTATION_AUTHORITY` |
| Input | [Intake revision 04](intake-r01.md), committed before this evaluation; [REQ-051 revision 04](../../requirements/active/2026/environment-control/REQ-20260908-051.md) |
| Inspection baseline | `d3c78b5b154b04a7fdaad544a3d00f1e91271dcb`; product baseline remains the intake's `b697738d009db37318ebc8762107ef8329e014db` |
| Scope | Four DELTA slices only; no business, price, provider or maturity redefinition |

## Required result

```json
{
  "project_id": "johnny-ai-skill",
  "intake_mode": "DELTA",
  "product_kind": "CONTROL_PLANE",
  "decision": "GO",
  "decision_reasons": [
    "Four owner-confirmed observable slices bound the change.",
    "Existing Router and WA-04 ownership permit separate pure rules, source admission and OS/host adapters.",
    "An offline disposable Windows lab permits bounded capability investigation before production promises.",
    "Unqualified mandatory controls refuse dependent execution; a failed investigation returns to the owner rather than weakening the guarantee."
  ],
  "product": {
    "target_users": ["Project owner", "Ticket reviewer", "Enrolled implementation Agent"],
    "core_problem": "Reinterpreted verification instructions, unbounded or duplicate work and responsibility mixing currently depend on Agent restraint.",
    "value_proposition": "Program-enforced approved execution and source admission with independently checkable refusal and completion evidence.",
    "mvp_scope": ["approved-verification-execution", "wa-04-responsibility-admission", "owned-execution-recovery", "automatic-host-enforcement"],
    "out_of_scope": ["Replacement Router", "Unrelated project restrictions", "Physical-host configuration changes during qualification", "External model calls during qualification", "Production installation or release", "Universal semantic correctness or numeric file-size limits"]
  },
  "observable_slices": [
    {
      "feature_id": "approved-verification-execution",
      "actor": "Ticket reviewer",
      "user_goal": "Run the exact approved verification plan without reinterpretation.",
      "interaction_boundary": "cli_command",
      "primary_actions": ["Request verification by approved reference", "Receive bounded terminal evidence"],
      "observable_outcomes": ["Exact ordered plan only", "Changed command, source, environment, count or load starts no work"],
      "states": {"success": ["All expected checks and cleanup evidenced"], "in_progress": ["One owned finite attempt"], "empty": ["Missing plan refuses"], "error": ["Drift, limit or verification failure remains failure"], "authorization": ["Approval is resolved independently of caller assertions"]}
    },
    {
      "feature_id": "wa-04-responsibility-admission",
      "actor": "Ticket reviewer",
      "user_goal": "Reject source violating the approved responsibility contract before integration.",
      "interaction_boundary": "event_contract",
      "primary_actions": ["Submit exact candidate to existing admission composition"],
      "observable_outcomes": ["Forbidden dependency and construction reject", "Splitting files cannot hide coupling", "Large cohesive fixture can pass"],
      "states": {"success": ["Declared source facts satisfy WA-04"], "in_progress": ["Bounded candidate analysis"], "empty": ["Missing required contract refuses"], "error": ["Unsupported analysis or violation refuses"], "authorization": ["Candidate cannot approve its own contract"]}
    },
    {
      "feature_id": "owned-execution-recovery",
      "actor": "Reviewer resuming an interrupted session",
      "user_goal": "Reconcile actual work without rerunning completed work or killing unrelated processes.",
      "interaction_boundary": "event_contract",
      "primary_actions": ["Reconcile one attempt", "Cancel only proven-owned work"],
      "observable_outcomes": ["Stale display plus verified completion causes zero launches", "Owner loss terminates owned descendants", "Ambiguity preserves recovery evidence"],
      "states": {"success": ["Verified terminal result returned without rerun"], "in_progress": ["Existing owned live attempt reattached by event wait"], "empty": ["No evidence means unknown, not never-started"], "error": ["Conflict or failed cleanup requires recovery"], "authorization": ["Stable identity, not process name or bare PID, controls cleanup"]}
    },
    {
      "feature_id": "automatic-host-enforcement",
      "actor": "Owner of an explicitly enrolled session",
      "user_goal": "Use a protected launch path for Codex and Claude without relying on remembered prose.",
      "interaction_boundary": "cli_command",
      "primary_actions": ["Start enrolled host through protected launcher", "Read exact enforcement coverage"],
      "observable_outcomes": ["Unauthorized alternate effect remains denied when a hook fails", "Unqualified host refuses protected launch", "Unrelated terminals remain unchanged"],
      "states": {"success": ["Exact host/version/configuration and effect paths qualified"], "in_progress": ["One bounded enrollment/qualification action"], "empty": ["Absent host or evidence stays unqualified"], "error": ["Bypass, stale configuration or unsupported cap refuses"], "authorization": ["Protected broker/policy owner is separate from restricted execution identity"]}
    }
  ],
  "function_derived_architecture": [
    {"feature_id": "approved-verification-execution", "backend_use_cases": ["Resolve approved immutable plan", "Execute ordered finite attempt", "Match expected evidence"], "domain_rules": ["No implicit amendment or retry-to-green"], "data_owners": ["Target owns ticket/approval intent", "Protected control plane owns execution evidence"], "separability_confirmed": true, "open_assumptions": ["Windows primitive qualification remains required"]},
    {"feature_id": "wa-04-responsibility-admission", "backend_use_cases": ["Existing WA-04 candidate admission"], "domain_rules": ["Source-derived facts, not line counts"], "data_owners": ["Target owns candidate and approved responsibility contract"], "separability_confirmed": true, "open_assumptions": ["WA-04 is specified, not yet delivered"]},
    {"feature_id": "owned-execution-recovery", "backend_use_cases": ["Single attempt ownership", "Reconcile terminal/process evidence", "Bounded owned cleanup"], "domain_rules": ["Unknown is not safe to retry", "At most one launch per approved attempt"], "data_owners": ["Protected attempt/evidence store"], "separability_confirmed": true, "open_assumptions": ["Crash windows and child escape require executable evidence"]},
    {"feature_id": "automatic-host-enforcement", "backend_use_cases": ["Protected host launch", "Independent per-host effect mediation qualification"], "domain_rules": ["Hooks are not final authority", "Absent support is not a successful fallback"], "data_owners": ["Owner controls enrollment and policy", "Host adapter owns exact installed-surface observations"], "separability_confirmed": true, "open_assumptions": ["Offline exact-version host exercise is not yet qualified", "CLI evidence does not qualify Desktop"]}
  ],
  "business": null,
  "constraints": {"tech_limits": ["Windows test VM only for effects", "No external model calls", "No Agent-visible credentials", "Finite hard resource caps before dependent workload", "Separate Codex and Claude qualification"], "cost_ceiling": null},
  "baseline_reference": "johnny-ai-skill@b697738d009db37318ebc8762107ef8329e014db",
  "delta_scope": ["approved-verification-execution", "wa-04-responsibility-admission", "owned-execution-recovery", "automatic-host-enforcement"],
  "risks": [
    {"risk": "Required OS/host primitive may be unavailable", "mitigation": "Capability-first experiment with an explicit unsupported result; no dependent workload or production guarantee"},
    {"risk": "A fixture escapes its intended scope", "mitigation": "Exact disposable guest, admitted outer protection and owned restore point before adversarial effects"},
    {"risk": "Ambiguous evidence produces duplicate work or a false pass", "mitigation": "Independent source/identity binding, finite failure states and reviewer counter-mutations"}
  ],
  "assumptions": [
    "GO authorizes architecture work, not a claim that both hosts already support complete mediation.",
    "The qualification SPEC may close with unsupported capability evidence; such a result does not complete the product requirement.",
    "D1, D2 and D3 remain the committed owner decisions; no new business or production rollout decision is inferred."
  ]
}
```

## Source and transition boundary

The [lab record](lab-qualification-r01.md) distinguishes owner-relayed guest discovery from
qualification. The [convergence record](enforcement-boundary-r01.md) contains actual CLI metadata,
the unresolved Codex tool-state discrepancy and the limited existing regression baseline.
No live workload, host-denial or orphan-cleanup PASS is inferred from them.

Return: `WAYFINDER_GO`. The next scoped action is architecture drafting over these four slices;
Grill, shared-Context sealing, SPEC approval, tickets and effects retain their separate gates.
