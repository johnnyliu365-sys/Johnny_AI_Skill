# Mandatory enforcement: boundary and refusal matrix

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `CONVERGENCE-CONTROLLED-VERIFICATION-20260908-01` / `ARCHITECTURE_PROPOSAL` / `04` |
| State | `OWNER_BOUNDARY_APPROVED / LAB_QUALIFICATION_PENDING / NOT_SEALED` |
| Requirement / intake | [REQ-051 revision 04](../../requirements/active/2026/environment-control/REQ-20260908-051.md) / [intake revision 04](intake-r01.md) |
| Inspection baseline | `b697738d009db37318ebc8762107ef8329e014db`; proposal predecessor `c17cc249fbb91339bc83314c0467eee3489339fc` |
| Authority | Owner accepted D2 scope and D3 protected-launch boundary; D3 binds proposal commit `f880f557dfaf50f7380270f7b9c7bdb6b3d526c1` and revision 03 LF digest `3aacc765314d87fa94759edecbf0f4e8525b106e4cad8a31e46d08f458eaee64`. This does not claim a qualified mechanism, completed Grill or installed enforcement. |

## Readback that changes the solution

On 2026-09-08 the exact local executable
`C:\Users\GameBoy\AppData\Local\OpenAI\Codex\bin\8e5b6932251c2c1c\codex.exe`
returned `codex-cli 0.153.4` for `--version`. `features list` returned
`hooks stable true` and `plugin_hooks removed false`. This is CLI feature readback only;
the removed legacy flag is not proof that plugin hooks are unavailable. No hook was installed
or trusted, no host tool interception was exercised, and Desktop qualification remains separate.

Current official [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks), sections
"Where Codex looks for hooks", "Review and trust hooks", "Tool coverage" and "PreToolUse",
documents user-level and plugin hooks, exact-definition trust, and pre-tool denial. However,
`write_stdin` does not re-enter PreToolUse, some tool paths opt out, and certain invalid output
fields cause continuation. Therefore feature availability is not complete mediation.

The official [Claude hooks reference](https://code.claude.com/docs/en/hooks#timeouts) states that
a timed-out command PreToolUse hook does not block the tool. Exit 1 is normally non-blocking;
proper denial is distinct from a crash. SessionEnd cleanup cannot be the sole guarantee when
the host crashes. This is documentation evidence, not a probe of the installed Claude version.

[Windows Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
documents process-group limits and termination when the last kill-on-close job handle closes.
It also names exceptions: WMI-created children are not ordinary job descendants, and some
completion-port notifications are not guaranteed. A Job Object alone therefore proves neither
all effect containment nor permission isolation. Handle ownership, startup attachment and actual
termination must be separately demonstrated with bounded disposable fixtures.

## Controls, not reminders

The proposal separates automatic entry, policy admission, OS execution and repository admission.
The Agent receives allowed action identifiers and results; it does not become the enforcement
authority by reading a skill. A user-level registration is executable configuration referencing
one installed implementation, not a machine-global copy of Johnny governance text.

| Owner failure | Mandatory check and effect | Required adversarial observation |
| --- | --- | --- |
| Natural-language reinterpretation | Resolve approved source, exact candidate snapshot, adapter, executable and ordered argument/run plan. Reject drift; never rewrite a rejected call into an allowed one. | Five runs with exactly one loaded slot cannot become five loaded slots; changing only script bytes, cwd, profile or an environment override also refuses before launch. |
| Excessive runtime or load | Attempt admission binds finite per-run and total deadlines, concurrency and resource caps. Executor cannot start the next run outside that plan. Required unavailable protection refuses. | An extra run, retry, stressor or worker is refused; timeout remains failure even if a later run would pass. Test with a bounded fixture, not whole-machine saturation. |
| Real orphan processes | Executor owns exact process/resource identity, cancellation and loss-of-owner cleanup, including crashes that skip normal cleanup code. | Kill a disposable executor/owner and verify its owned tree terminates within the approved deadline; an unrelated sentinel survives. A bare reused PID cannot authorize termination. |
| Stale host task display | Reconcile authoritative attempt/return evidence with verified live process identity. Do not use the UI task list or an empty transcript as ground truth. | Completed evidence plus a stale UI item starts zero new work; missing/conflicting evidence reports unresolved interruption, never fabricated completion or automatic re-dispatch. |
| Concurrent duplicate invocation | A single execution owner must claim the attempt before effects. Replays return its known state/result rather than create another workload. | Two requests for one attempt produce at most one launch; a crash at each claim/launch/result boundary cannot silently authorize another attempt. Primitive and recovery semantics require qualification. |
| Model progress polling | One bounded completion wait returns terminal evidence; cancellation and deadlines are program events. | Repeated progress reads cannot restart/extend work or mint new retries. No model loop or mandatory wake bridge is created. |
| Coupling and mixed responsibility | Reuse WA-04: source-derived symbols/dependencies/construction must satisfy the previously approved responsibility contract before authority integration. | Forbidden dependency, out-of-root concrete construction, undeclared symbol ownership or missing seam refuses. Splitting a coupled file must not help; a large cohesive fixture passes. |
| Bypass or policy tampering | Denied direct execution, interactive stdin, alternate tool effects and enforcement-policy writes must stay denied independently of hook success. | Disabled/crashed/timed-out hook, forged approval/result or an alternate execution path cannot perform the forbidden effect. Any escape means enforcement remains unqualified. |

These cells are design requirements, not executed tests or new runtime enum values. Their exact
inputs, deadlines, resource limits and commands must be frozen in separate implementation tickets.
No default of five stress runs, five host sessions or unlimited retries is imported from another
feature's policy; counts belong to each approved qualification plan.

## Narrow source checks; no claim to solve semantics with a script

An approved contract maps responsibility units to bounded source/symbol selectors, dependency
directions, state/effect ownership and explicit composition/test seams. A qualified language
adapter extracts facts from the candidate, not labels asserted by the implementer. The candidate
cannot approve a new contract or exception for itself. Unresolved dynamic/reflection paths cannot
silently count as accepted source facts; their support must be closed explicitly in that adapter.

Static checks cannot prove arbitrary business behavior has a single responsibility. The hard
claim is rejection of declared structural violations plus mandatory independent review before
integration, not elimination of all semantic mistakes. There is no line-count gate. Draft edits
are not automatically approved production code; no transactional editor/rollback guarantee or
R09B2 write path is introduced by this source-admission requirement.

## Existing ownership and impact

- [ADR-036](../../adr/ADR-20260829-036-project-scoped-workflow-activation-and-admission.md) and
  [workflow adoption SPEC](../../../modules/spec/workflow-adoption-activation.md) already own
  WA-04 structural admission. Reuse that slice; do not invent a duplicate validator family.
- [HDA-01](../../../modules/tickets/plugin-adoption-quality/hda-01-host-dispatch-admission-hook.md)
  proposes plugin-host dispatch checks; it is non-dispatchable and does not already protect shell
  execution, process lifetime or all Codex tool paths.
- [WA-02b](../../../modules/tickets/plugin-adoption-quality/wa-02b-target-activation-behavioral-hook.md)
  is a separate target-owned activation proposal. Loading a Skill is not permission to execute
  arbitrary work. Its target-write capability blocker is not a prerequisite for pure validation.
- [Environment SPEC](../../../modules/spec/environment-capability-bootstrap.md) EC-10 retains
  hard-limit admission. A required disk/container/process control cannot be omitted because a
  CPU/Job Object demonstration passed. Unsupported affected execution remains closed.

Plan validation, orchestration, process supervision, recovery, evidence and language analysis
remain separate units with injected ports and a short Composition Root. No replacement Router,
Agent-reviewer role, persistent wake runner or generic workflow tree is introduced. Existing
accepted ADR/SPEC/ticket bodies remain unchanged pending the scoped change decision.

## Owner decision D2: restricted execution lane

Owner-approved scope: only explicitly enrolled Johnny sessions/worktrees use a protected execution
lane. Agents may propose plans and candidate edits but cannot modify the active approval/policy
store or bypass controlled verification using arbitrary shell, interactive stdin or alternative
effect tools. Necessary read-only inspection and owner recovery remain available. Ordinary
unrelated projects and owner-operated terminals are not silently reconfigured.

This is a loss of unrestricted Agent execution in the enrolled lane. Without it, user-editable
hooks can improve behavior but cannot honestly satisfy the requested non-bypassable guarantee.
The owner has accepted this scoped loss of unrestricted execution. Selecting a concrete protected
service/account/container mechanism remains subject to bounded capability investigation; its
unmentioned administrative installation is not pre-authorized here. Do not re-ask the approved
scope question or treat that approval as proof of a host's capability.

## Bounded capability investigation: actual results, 2026-09-08

Reviewer inspected local executables and reused one `decision-support` helper for documentation
questions. The helper did not implement or supply the review verdict. Completion used
`wait_agent`, not transcript/status polling. No second ticket reviewer was appointed.

| Observation | Result | Limit of the evidence |
| --- | --- | --- |
| Codex executable named above | `0.153.4` | CLI version, not Desktop qualification |
| Installed Claude executable, WinGet `Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe/claude.exe` | `2.1.231`; help exposes `--tools`, `--disallowedTools`, `--strict-mcp-config`, `--settings`, `--setting-sources` | No authenticated model turn or tool-denial attack performed |
| `C:\ProgramData\OpenAI\Codex\requirements.toml` existence | `False` | Does not exclude every other policy source; isolated RPC below returned null |
| Docker client/server version | `29.5.3 / 29.5.3` | Engine responds; no workload started or image downloaded |
| Available WSL distributions | `Ubuntu`, `docker-desktop` | No distribution entered or configured |
| Named Hyper-V lab readback | `Get-VM -Name 'Johnny-MSIX-Lab-20260905'` refused for insufficient permission | No assertion about VM power state or guest readiness |

The [Claude CLI reference](https://code.claude.com/docs/en/cli-reference) distinguishes tool
selection from configuration loading; `--bare` also skips hooks/plugins, so it cannot silently
stand in for installed-plugin qualification. The [Claude sandbox documentation](https://code.claude.com/docs/en/sandboxing)
does not support its built-in Bash sandbox on native Windows. WSL2/Linux support is not evidence
for native Windows or complete effect containment. The [Codex Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
protects filesystem/network boundaries; its presence alone does not bind execution to an approved
verification plan. Both hosts remain conditional, not proven impossible and not qualified.

### Isolated Codex metadata preflight

One child process only; no model, thread, turn, provider, command-execution or MCP-tool request.
The executable used a fresh child-only `CODEX_HOME` and empty working directory under this owned
worktree's ignored `.worktrees/host-config-probe-d95b2fd9d5fd4687b93b9bed59bd0048` directory.
No credentials were copied. Credential-like environment variable names were removed from the
child environment. Existing user settings and other sessions were not changed. This separation
is test hygiene, not a protected identity or a claim to prohibit every possible network request.

Launch was `app-server --stdio --strict-config`, with overrides `sandbox_mode="read-only"`,
`approval_policy="never"`, `web_search="disabled"`, `analytics.enabled=false` and `--disable` for:
`shell_tool`, `unified_exec`, `code_mode`, `code_mode_host`, `apps`, `plugins`, `remote_plugin`,
`browser_use`, `browser_use_external`, `browser_use_full_cdp_access`, `computer_use`, `hooks`.
An outer 30-second total read deadline and bounded exit cleanup applied; no retry was used.

Requests, in order: `initialize` with experimental API enabled; `initialized` notification;
`configRequirements/read`; `config/read` with `includeLayers=false`;
`experimentalFeature/list` with limit 1000; `mcpServerStatus/list` with limit 100.
These are the documented [App Server](https://learn.chatgpt.com/docs/app-server) protocol names,
not a claimed production gateway. Selected actual response fields:

```json
{
  "requirements": null,
  "config": {
    "sandbox_mode": "read-only",
    "approval_policy": "never",
    "web_search": "disabled",
    "features": {"shell_tool": false, "unified_exec": false}
  },
  "experimentalFeatureList": [
    {"name": "shell_tool", "enabled": false, "stage": "stable"},
    {"name": "unified_exec", "enabled": true, "stage": "stable"}
  ],
  "featureNextCursor": null,
  "mcp": {"data": [], "nextCursor": null},
  "exitCode": 0,
  "processExited": true,
  "durationMs": 2008
}
```

The two `unified_exec` views disagree. Neither configuration acceptance nor this feature listing
proves the actual offered tool roster or a successful bypass. No exact-version source explanation
was obtained in the bounded follow-up. Do not invent a Windows forced-on rule or speculatively
patch around it. Classification: **configuration accepted; execution mediation UNKNOWN**.
Process exit is evidence for this child only, not a crash/descendant-containment qualification.

### Existing regression baseline, not new enforcement acceptance

Using `C:\Users\GameBoy\AppData\Local\JohnnyRouter\venv\Scripts\python.exe` in this worktree:

```text
-B -m unittest tests.test_workflow_intensity -v
Ran 6 tests in 0.003s
OK

-B -m unittest tests.test_subscription_builder.DeadlineProbeTests.test_the_probe_proves_a_real_one_shot -v
Ran 1 test in 0.063s
OK
```

The intake `NormalizedGoal` validated and derived `high_assurance`. The timer test proves only
an existing one-shot timer fires; it does not terminate workloads. Its production deadline port
is receipt-bound, so it must not be reused here by fabricating a receipt. No reverse-mutation,
process-orphan, resource-cap, source-coupling or installed-host acceptance test passed this turn.

## Owner-accepted protection boundary: D3

Owner-accepted boundary: an explicitly enrolled session starts
through a dedicated launcher under a restricted Windows identity, separate from the protected
plan/policy/evidence owner. A narrow broker validates the approved plan and owns execution and
cleanup. The model receives only admitted operations; arbitrary effect tools and the broker's
control channel are not exposed to it. This is an OS/host protection boundary, not governance
text injected into model memory. A Job Object remains a process-limit component, not the whole
boundary. The installer may provision these components only after qualification and later release
authority; no service/account name or implementation technology is frozen here.

This choice adds a dedicated launch path and protected identity/configuration lifecycle, including
owner recovery. It does not retrofit non-bypassability into the currently unrestricted session.
Enrollment must be observable; unsupported or tampered enrollment refuses controlled execution,
while unrelated projects and owner terminals stay unchanged. Claude and Codex each require their
own test result; passing a Linux container fixture cannot qualify native Windows hosts.

The owner has accepted this boundary and qualification in the existing Windows test VM, with no
physical-host configuration changes or external model calls. Do not ask for this decision again.
On acceptance, a fresh read confirmed `administratorToken=false`; `Get-VM` still refused for
insufficient permission. Approval and operating-system capability are different facts. A normal
UAC-mediated, exact-target readback may establish lab metadata without changing host policy.
The qualification ticket must pin VM/snapshot identity,
the owned disposable resources, bounded commands/time/resource budgets, cleanup/sentinel checks
and zero external model calls. Do not silently elevate, modify the main
machine's managed policy, reuse real project workloads or create an always-running service now.

Pure verification-plan contracts and the existing WA-04 structural gate do not depend on that
lab's availability; they can proceed after their own specification/ticket admission. The current
documents are not those approved tickets. Installed release acceptance still requires the full
bypass/refusal matrix above for both hosts.

Return: docs-only `ACTION_COMPLETED`; D3 acceptance emits `OWNER_INPUT_PROVIDED` for the bounded
DELTA capability investigation. No enforcement code is delivered by this proposal, and none of
the listed adversarial tests is reported as passed. This revision records bounded investigation
completion and the owner's protected-launch decision; it does not mark Grill,
capability qualification, implementation or publication complete.
