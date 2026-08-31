# CAP-HOST-EFFECT-GRANT-01 — prove Host External-Effect Gateway capability

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-CAP-HOST-EFFECT-GRANT-01` / `CAPABILITY_INVESTIGATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 14 / AC-17R14 |
| Requirement / Context / ADR | `PRD-20260829-047` / `CHG-20260829-047` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260829-14` (`bc93c2aa1b25cf0510721785ed4f3f43b43e4daab448aaf0f8b569772b337ef0`) / `ADR-20260829-035` |
| State / closure | `OPEN / APPROVED / DISPATCHABLE`; `CLOSURE-ADAPTIVE-CAP-HOST-EFFECT-GRANT-01`, revision 01 |
| Document revision | `02` |
| Opening authority | Project owner approved Revision 14 candidate `c3da092eb5cbd78938fb6f43480c525a9ee2258e` on 2026-08-29 and authorized reviewer opening of this evidence-only capability investigation. Exact ticket approval and dispatch remain separate; no gateway implementation, elevation, credential, service/task creation, remote/provider/Git effect, CAP-REMOTE retry, publication, installation, release or deployment is authorized. |
| Approval authority | Project owner, 2026-08-31 (Asia/Taipei): approved exact ticket candidate/authority commit `bc59172b90c8211c03596418a1be3f6712b70de6`, leaf SHA-256 `aa79425fb8566c7741dc132ac2fe0a063a681522280c1171b4f0facebf396abf`. This authorizes one Terra/xhigh evidence-only same-lifetime investigation lane only while a Sol/high reviewer is active; it grants no external effect, gateway implementation or successor resumption. |
| Source baseline / subject | `4f501ccc4f4ecf943fd3f0f6be89871b7341a4ac`; read-only qualification of the current Windows host tuple and installed Codex/Claude runtime surfaces. CAP-REMOTE candidate `678338599529b80b1f7aafeccb111a228702f1e3` remains non-integrated evidence and is not a repair source. |
| Observed tuple at opening | Microsoft Windows 10 Pro `10.0.19045` build `19045`, NTFS system volume, interactive principal `desktop-28erpq1\gameboy`, Codex CLI `0.151.0-alpha.7.2`, Claude Code `2.1.231`. These observations identify the investigation subject only; they do not prove a gateway. |
| Control owner / reviewer | `ticket-review-hard` semantic profile — Sol/high; sole final reviewer and integrator. |
| Investigation owner | `implementation-high-assurance` semantic profile — Terra/xhigh. The indivisible proof crosses OS principal separation, one-shot grant races, caller tamper/replay and conditional cleanup semantics. Reviewer capability is not lower than the implementation owner. |
| Worktree / branch / task | After exact approval, reviewer allocates `.worktrees/cap-host-effect-grant-01` on `implement/cap-host-effect-grant-01` from the then-current committed authority baseline and reuses one Terra/xhigh implementation task. Same-lifetime dispatch uses one native call and one wait; the investigated gateway is not required for dispatch and no runner, queue, receipt, descriptor or bridge is created. |
| Delivery / language | `POC / HIGH_ASSURANCE / HIGH_ASSURANCE_REQUIRED`; Python 3.11 strict typed, test-only read-only host probes and deterministic local adversarial harnesses. A positive claim requires actual host evidence; mock or documentation-only success is forbidden. |
| XSS / effects | `XSS_NOT_APPLICABLE`. The investigation performs read-only host observation only. It must not install/register a Windows service or scheduled task, elevate, access credentials/grant material, change ACLs, invoke a remote/provider transport, create/delete a ref, or mutate any target/workspace/system configuration. |

## Boundary declaration

```johnny-boundary
create = tests/test_host_external_effect_grant_capability.py
modify = tests/test_host_external_effect_grant_capability.py
create = modules/element/python/adaptive-project-orchestration/cap-host-effect-grant-01-host-external-effect-gateway-capability/
modify = modules/element/python/adaptive-project-orchestration/cap-host-effect-grant-01-host-external-effect-gateway-capability/
forbid = library/
forbid = tests/test_remote_authority_commit_capability.py
forbid = tests/test_atomic_conditional_replace_capability.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

This is an evidence harness only. It cannot add a gateway, production adapter, grant store,
credential broker, provider transport, remote writer, fallback file or environment activation.

## One observable closure

Produce one strict, typed `HostExternalEffectGatewayQualification` for each exact installed host
surface:

1. `CODEX_DESKTOP_OR_CLI / WINDOWS_10_19045 / NTFS / desktop-28erpq1\gameboy`.
2. `CLAUDE_CODE_CLI_2_1_231 / WINDOWS_10_19045 / NTFS / desktop-28erpq1\gameboy`.

Each result is exactly one tagged variant:

```text
AVAILABLE {
  host_surface, platform_tuple, independent_principal_ref,
  protection_primitive, atomic_one_shot_consume_primitive,
  gateway_owned_transport_ref, conditional_cleanup_primitive,
  plan_binding_evidence_ref, tamper_race_evidence_ref
}

UNAVAILABLE {
  host_surface, platform_tuple,
  reasons: non-empty unique tuple of
    INDEPENDENT_PRINCIPAL_ABSENT | GRANT_STORE_CALLER_FORGEABLE
  | ATOMIC_ONE_SHOT_CONSUME_UNPROVEN | PLAN_BINDING_UNPROVEN
  | GATEWAY_OWNED_TRANSPORT_UNPROVEN | CONDITIONAL_CLEANUP_UNPROVEN,
  observation_evidence_refs
}
```

There is no `UNKNOWN`, optimistic `CONDITIONAL` or nullable success field. A host surface qualifies
`AVAILABLE` only when read-only actual-host evidence proves every success field for the same
platform/runtime tuple. If no separately registered and independently protected gateway is
observable, `UNAVAILABLE` is the successful investigation result. Cross-host inference is
forbidden: a Codex result does not qualify Claude Code and vice versa.

The harness may use OS/process-token/service-registration/ACL metadata APIs only to observe facts.
It may use pure in-memory race models to reject invalid designs, but such models cannot produce
`AVAILABLE`. It must not probe grant contents, credentials or unrestricted process/environment
state. Evidence contains only bounded versions, principal/protection identifiers, primitive names,
finite reasons, digests and opaque observation refs.

## Non-negotiable proof rules

- The independent principal/protection boundary must be outside the plugin, CLI, current Agent
  runtime, ordinary user-writable files, environment, Router metadata, receipts and user cache.
- The runtime cannot mint, read, alter, erase, substitute or replay grant material. Same-user ACL,
  DPAPI under the same user, a prompt, file existence or environment value is not proof.
- Grant reservation/consumption is one atomic host operation bound to one immutable plan digest.
  A check followed by write/rename/delete is rejected.
- The gateway, not the caller, resolves and revalidates canonical repository, full refs, actor,
  transport, allowed effect set, correlation and expiry before every effect.
- A positive capability owns privileged transport and direct readback; a wrapper around caller
  credentials or caller-selected command execution is not a gateway.
- Cleanup requires durable pre-cleanup evidence and an atomically expected-SHA-conditional delete
  primitive. Observation followed by ordinary deletion is rejected. Missing support yields
  `CONDITIONAL_CLEANUP_UNPROVEN`, not a weakened profile.
- Capability absence never affects the normal same-lifetime `reviewer -> wait_agent -> review ->
  gate` path. No runner/receipt/gateway compensation may be created.

### Reusable-module selection record

```text
selected: none.
why: the catalog has no READY host-protected external-effect-grant module.
read: MODULE_CATALOG -> workflow-control index only; no near-match selected.
dependency: sealed Revision 14 Context and ADR-035; CAP-REMOTE is negative evidence only.
rejected: Router receipts, environment, ordinary files/user cache, Host Bootstrap and telemetry;
          none owns an independent principal, grant lifecycle or privileged transport.
boundary: evidence-only readback; no source capability, provider effect or gateway installation.
```

`TicketDecompositionDecision = HIGH_ASSURANCE_REQUIRED`: this is one evidence-only qualification
with one indivisible trust/race/cleanup proof burden. Splitting those proofs would permit a partial
green result to masquerade as capability availability.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| HEG1 | Every enum/platform/host/evidence/result variant ordinary-constructs, strict-validates and JSON-round-trips. Missing/null/extra fields, wrong primitives, raw paths/URIs/secrets, duplicate reasons/evidence refs, success without every proof field and unavailable without a reason reject. |
| HEG2 | Read-only actual-host observation binds exact OS/build/filesystem, installed host/version and effective process principal. Cached declarations, prompt text, environment literals and a different host surface cannot substitute. |
| HEG3 | Every observed same-user/file/environment/cache/receipt/Router candidate is classified caller-forgeable. A positive independent-principal claim requires an actually registered, separately protected gateway identity and access boundary that the runtime cannot mint/read/change/delete. |
| HEG4 | `AVAILABLE` requires an actual atomic one-shot reservation/consume primitive. The adversarial race schedules two consumes and tamper/replay around the final boundary; exactly one may consume and the runtime cannot restore/reuse the grant. In-memory/mock races may turn invalid claims red but cannot prove availability. |
| HEG5 | Plan-binding evidence proves the gateway independently resolves every canonical binding and rejects caller-selected path/ref/actor/effect/evidence destinations. First-match shorthand and ambiguous resolution fail closed. |
| HEG6 | Transport/readback and cleanup are gateway-owned. A caller credential wrapper, check-then-effect, missing durable pre-cleanup evidence or observation-plus-unconditional-delete forces `UNAVAILABLE`; no remote effect is executed. |
| HEG7 | Codex and Claude results are produced independently. Either or both may be `UNAVAILABLE`; the result never blocks direct same-lifetime dispatch or invents runner/receipt fallback. |
| HEG8 | Focused tests, strict type check, compile, exact boundary/index checks and source/AST effect scan pass; no production source, system registration, ACL, credential, provider or remote target changes occur. |
| HEGM1 | Reverse-mutate same-user/file/environment proof to qualify as independent; HEG3 turns red, then exact restoration returns green. |
| HEGM2 | Reverse-mutate consume to check-then-mark or permit replay; HEG4 turns red, then exact restoration returns green. |
| HEGM3 | Reverse-mutate cleanup to ordinary read-then-delete; HEG6 turns red, then exact restoration returns green. |

The authentic first-red slot is the focused test command after the strict test-only DTOs and host
probes are specified but before their implementation exists. It must fail for the missing
qualification entry point, not because an external effect was denied. Only actual same-tuple host
observation may supply the final capability result.

## Required reviewer-owned adversarial evidence

After the investigation owner returns, the Sol/high reviewer binds the exact candidate and uses
two distinct, read-only evidence lanes. Helpers may not modify, commit, push, dispatch, approve,
integrate, install a service/task, elevate, access credentials or invoke any provider/remote effect.

1. **Principal/grant helper** attacks process identity, ACL/DPAPI/same-user assumptions, grant
   mint/read/change/delete/replay paths and atomic-consume races.
2. **Plan/cleanup helper** attacks canonical binding, first-match ambiguity, transport ownership,
   evidence persistence and expected-SHA-conditional cleanup semantics.

The reviewer reproduces findings, runs all closure checks and performs one additional mutation
through a different production path. An `AVAILABLE` finding still authorizes no gateway or remote
effect; architecture must separately bind that exact tuple before any successor.

## Verification and return

Investigation-owner commands:

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_host_external_effect_grant_capability.py
py -3.11 -B -m mypy --strict --no-incremental tests/test_host_external_effect_grant_capability.py
py -3.11 -B -m compileall -q tests/test_host_external_effect_grant_capability.py
git diff --check <ticket-integrated-authority> HEAD
git status --short
```

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with one qualification per
exact host surface and bounded evidence refs; `BLOCKED -> HALT` only when the exact read-only host
observation itself cannot run; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` for an actual Revision
14 conflict. The investigation owner does not commit or push. No result by itself resumes
CAP-REMOTE or WA-02; a separate architecture/ticket decision is required.
