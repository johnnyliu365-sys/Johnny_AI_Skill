# Host Gateway Workspace Binding Context — Revision 02

| Field | Value |
| --- | --- |
| Feature cluster | `host-gateway-workspace-binding` |
| Artifact | `CTX-HOST-GATEWAY-20260823-02` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner directive, 2026-08-23 (Asia/Taipei) / `PRD-20260822-032` / `CHG-20260822-032` |
| Replaces | `CTX-HOST-GATEWAY-20260822-01`; the revision-01 leaf remains sealed historical evidence. |
| Shared baseline | `c69bb29954cea884513fb1d8b53dd9a04f5f0f3c` |
| Responsibility boundary | Privileged, reviewer-owned host capability/readback admission for a prospective implementation task. |
| Forbidden changes | Provider login/invocation, credential storage, task creation, message delivery, receipt consumption, runner/subscription/wake lifecycle, Git/worktree creation, P8R source, and shared `CONTEXT.md` mutation. |

## Stable high-assurance boundary

- R07 remains the contract family for a privileged host boundary. It requires exact task/project
  identity, effective profile/effort/rank readback, three-way workspace proof, active receipt and
  descriptor correlation before an implementation-source or Agent-control effect.
- The current desktop host still lacks effective-profile/effort/rank readback for a prospective
  implementation task. Its only high-assurance result is the finite
  `CAPABILITY_UNAVAILABLE`; prompts, shell directories, static configuration, CLI login,
  self-report and runner state are not substitute evidence.
- The generic collaboration subagent interface is not a fallback transport for the high-assurance
  gateway. It cannot supply the required workspace/profile proof.
- This is a privileged host capability and remains `HIGH_ASSURANCE`. Its reverse-mutation and
  adversarial acceptance obligations are retained intact.

## Facts invalidated by CHG-20260822-032

- P8R no longer waits for this gateway. The revision-01 statement that P8R can be re-evaluated
  only after a compatible gateway is replaced by a separate POC manual-evidence route.
- `TAD-ADAPTIVE-R07-HOST-CAPABILITY-01` is blocked by `CHG-20260822-032`. The sealed ticket leaf
  is historical evidence only; a future host-gateway implementation requires a replacement
  `HIGH_ASSURANCE` ticket and may not claim the POC known gap as a successful binding.
- The POC reviewer counter-mutation proves only the bounded resolver closure. It neither changes
  this gateway's requirements nor grants a host-control capability.

## Downstream architecture boundary

Revision 08 of the adaptive orchestration SPEC must express two non-overlapping paths:

1. the POC manual-evidence path for a bounded, no-effect ticket, with the named workspace
   readback gap and no automatic-wake claim; and
2. the existing high-assurance host path, which rejects absent, asserted, stale, mismatched or
   lower-rank readback before any effect.

No provider, task, receipt, workspace, runner, Git or source effect is authorized by this Context.

## Seal and provenance

- Shared Context reference: `CONTEXT.md`, stable-fact fingerprint `e8eabdd8`.
- Requirement lineage: `PRD-20260822-031` / `CHG-20260822-031`, amended by
  `PRD-20260822-032` / `CHG-20260822-032`.
- This revision supersedes the P8R-dependency fact in `codex-desktop-readback.md`; it does not
  alter that sealed leaf.
