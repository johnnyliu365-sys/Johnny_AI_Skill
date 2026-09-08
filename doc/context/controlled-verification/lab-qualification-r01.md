# Protected execution: Windows lab qualification plan

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `PLAN-CONTROLLED-VERIFICATION-LAB-20260908-01` / `CAPABILITY_QUALIFICATION_PLAN` / `01` |
| Lifecycle | `DRAFT / GUEST_READBACK_REQUIRED / NOT_DISPATCHABLE` |
| Requirement | [REQ-051 revision 04](../../requirements/active/2026/environment-control/REQ-20260908-051.md) |
| Accepted boundary | [Convergence revision 04](enforcement-boundary-r01.md); owner decision D3 recorded in `b299e5f2899041f1317b7a9426998028a323c6b8` |
| Purpose | Freeze a small qualification sequence for the accepted boundary before any production enforcement implementation or workload. |

## Authority and exclusions

Only the existing Windows test VM is an effect target. Do not change physical-host accounts,
ACLs, managed Codex/Claude configuration, firewall, services or unrelated projects. No external
model request, provider credential migration, package publication, push, existing guest data
deletion, VM replacement, or whole-machine stress is authorized by this plan.

The owner's accepted boundary is not re-opened by this document. Actual fixtures still require
an admitted exact specification/ticket, an immutable candidate and qualified prerequisites.
This plan is not an implementation dispatch, a fabricated receipt or a capability PASS.
Guest authentication must use a user-controlled local prompt or user-operated guest terminal;
never send a password to the Agent or save it in an artifact.

## Phase 0: observed host-side baseline

The earlier [provisioning review](../../reviews/local-orchestration-installer/env-msix-01-provisioning-review.md)
records the expected VM identity. Fresh native readback on `2026-09-08T10:39:49.2539936Z`
matched it exactly:

```json
{
  "id": "CV-LAB-READBACK-20260908-01",
  "status": "METADATA_READ_ONLY",
  "vm": {
    "id": "7701b26b-5b5a-42c0-b1e1-36d34dfdaa46",
    "name": "Johnny-MSIX-Lab-20260905",
    "state": "Running",
    "generation": 2,
    "checkpointType": "Standard",
    "checkpointIds": [],
    "adapterCount": 1,
    "connectedAdapterCount": 0
  },
  "failure": null
}
```

Method: normal UAC launch of the literal System32 Windows PowerShell executable; read-only
`Get-VM -Id`, exact ID/name comparison, `Get-VMSnapshot`, `Get-VMNetworkAdapter`. A single owned
job had a 15-second wait deadline, zero retry, and owned-job cleanup. Parent observed native
process exit 0, then read the result file. No VM start/stop, snapshot, network, account or guest
mutation was performed. The outer wait was 25 seconds; this diagnostic does not claim the
future crash-proof executor's cleanup guarantees.

Diagnostic recipe: this owned worktree's ignored
`.worktrees/lab-readback-20260908-01/read-lab.ps1`, LF SHA-256
`645a51d53dbd7ad3dfcc8bc7c0f2c8302f72695b1420021a9880209a051d1d50`.
Its generated `result.json` is local readback material, not trusted policy. No receipt or
provider credential was acquired. The VM is running and disconnected; **guest readiness,
recoverability and enforcement remain unproven**.

## Remaining prerequisites before a mutating fixture

1. Read inside this exact guest: Windows build, PowerShell version, admin-token availability,
   exact installed CLI executables/versions, and availability of a user-controlled execution
   entry. Do not assume the physical host's installations also exist in the guest.
2. Capture an owned restore point and verify its exact VM/checkpoint identity before new account,
   ACL or fixture changes. The readback above found no checkpoint. Do not call that recoverable
   or restore/delete an unrelated snapshot. Snapshot storage headroom must be checked first.
3. Bind a new guest-only fixture root, protected policy/evidence owner and restricted subject
   identity. Preserve existing accounts and guest files. Verify SID/ACL/readback, not display names.
4. Qualify the outer containment and required finite resource controls before hostile execution.
   If a required cap is unavailable, refuse the dependent fixture; do not substitute monitoring.
5. Pin fixture source/candidate SHA, executable identity, exact command and environment map,
   allowed writes, expected cells, deadlines, evidence locations and cleanup. A candidate cannot
   alter its approval plan; extra tests/retries/load require an explicit amended plan.

Guest access is presently unconfirmed. No credential has been requested from an Agent-visible
channel. Lack of guest access blocks guest effects only, not pure specification work or normal
same-lifetime delegation after ticket admission.

### Minimal owner-run guest readback

Run this inside the test VM's PowerShell, not the physical host. It reads metadata only and does
not execute discovered CLIs, read credentials, install packages or change accounts/settings:

```powershell
$guestIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$guestPrincipal = [Security.Principal.WindowsPrincipal]::new($guestIdentity)
$guestTools = @(Get-Command codex,claude,python -CommandType Application -ErrorAction SilentlyContinue | Select-Object Name,Source)
[pscustomobject]@{
    os = [Environment]::OSVersion.VersionString
    powershell = $PSVersionTable.PSVersion.ToString()
    admin = $guestPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    tools = $guestTools
} | ConvertTo-Json -Depth 3
```

No returned tool entry means absent from that command search, not proof that no installation
exists anywhere. Owner-relayed output is discovery input; actual qualification must independently
bind guest/VM identity and collect its own exact evidence before a passing verdict.

## Qualification sequence and refusal evidence

Each row owns one observable claim; tests must not collapse the rows into one generic PASS.
These are required fixture outcomes, not a claim that the production contracts already exist.

| Order | Claim | Control / adversarial observation | Refusal or non-claim |
| --- | --- | --- | --- |
| Q1 | Policy and execution identities are separate | Restricted subject can propose a request but cannot edit active policy, approval, broker executable/configuration or final evidence; protected owner can perform its declared operation. | A caller-supplied digest or writable approval file grants no authority. Any writable authority surface is a finding. |
| Q2 | Exact plan reaches execution without reinterpretation | One bounded synthetic plan starts its declared operation; changing argv, cwd, environment, executable/script bytes, source binding, run count, retry count or loaded-slot placement starts nothing. | No work proceeds merely because the request's profile name is valid. Changed script bytes with unchanged argv must be detected against a protected snapshot. |
| Q3 | Work starts inside effective resource/process protection | Controlled fixture verifies pre-launch attachment, limits, and denied escape paths; an unrelated sentinel remains alive and unchanged. | Timer firing, a late attach or absence of observed load does not prove containment. Required unsupported controls refuse launch. |
| Q4 | Loss and cancellation terminate only owned work | Separate bounded cases terminate the disposable owner/executor or cancel an attempt and observe owned-tree exit; sentinel survives. | Hook/session cleanup alone is insufficient. Cleanup failure preserves evidence and blocks dependent execution. |
| Q5 | Reconciliation does not re-run completed work | Completed return plus stale UI starts zero work; interrupted/no-return and conflicting identity stay unresolved; duplicate concurrent requests cause at most one launch. | An empty transcript is not proof of never-started work; a bare PID does not authorize killing a process. |
| Q6 | Codex has no alternate effect route in the enrolled configuration | Independently exercise direct execution, interactive continuation, file effects, other tool/MCP routes, client-control-channel reachability, and policy changes. Disable/crash/timeout the advisory hook while protection persists. | The earlier `config/read` versus `experimentalFeature/list` mismatch stays UNKNOWN until actual effect tests resolve it. CLI results do not qualify Desktop. |
| Q7 | Claude has no alternate effect route in the enrolled configuration | Repeat applicable effects independently, including built-in tools, inherited MCP/configuration and hook failure. Read installed profile/tool configuration back. | A tool flag, Linux sandbox result or a `--bare` session that omits the plugin cannot establish installed native-Windows plugin support. |
| Q8 | Responsibility admission uses candidate source facts | Existing WA-04 slice rejects a forbidden dependency, mixed ownership and concrete construction outside its composition boundary. Mechanically splitting coupled code remains red; a large cohesive fixture is green. | No line-count ceiling or new parallel validator family. A structural pass is not a replacement for ticket review. |

Q2/Q5/Q8 pure contracts can be developed independently after their own ticket admission. Q3/Q4
must not await live model credentials. For Q6/Q7, prefer a deterministic loopback provider fixture
with synthetic inputs and scripted responses, not an external language model. Any unsupported
offline host path is reported as unqualified rather than falling back to a real provider.
This is a proposed test technique; its host compatibility and implementation are not yet proven.
Windows lab network isolation must remain effective throughout the no-external-call qualification.

## Bounded work, evidence and cleanup

- One fixture lane at a time. No five-run stability or CPU saturation suite is imported from
  the motivating incident. Each declared control/mutation runs once; automatic retry count is zero.
- Exact per-cell time, CPU, memory, disk, process and worker budgets must be part of the admitted
  fixture contract before it can run. A missing bound is a refusal, not a value for the Agent to
  infer at execution time. Limits chosen for a capability experiment are not production defaults.
- Parent waits for completion once. Program events handle exit/deadline/cancellation. No model
  progress polling, tail loop or replacement task creation based on a stale display.
- Evidence binds VM and restore-point identities, subject/owner identities, fixture/candidate
  digest, requested and observed action, duration/limits, terminal reason, and sentinel/cleanup
  readback. Preserve all failed attempts and unreduced named-test output for reviewer mutations.
- Zero collected tests, zero expected reds, timeout, unresolved interruption, unavailable host,
  cleanup failure or missing evidence cannot be upgraded to PASS. Reviewer owns the final verdict.
- Cleanup touches only newly owned fixture resources after exact identity checks. Restore-point
  reversion, deletion of existing data or changes affecting other lab work require separate exact
  authority. Preserve recovery evidence; do not reset the VM merely to make an error disappear.

## Continuation

Host-side metadata readback is complete. Next obtain the guest's minimal readback through a
user-controlled guest entry, then finish the exact qualification specification and ticket.
No new architecture choice is being asked. D1/D2/D3 remain accepted; no fixture implementation,
host configuration, VM mutation, production enforcement, integration or release is complete.
