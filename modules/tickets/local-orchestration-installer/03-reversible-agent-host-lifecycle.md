# 03 — Reversible Agent Host Lifecycle

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-02, AC-03, AC-06, AC-07, AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `PLANNED` |
| Language | Python 3.11 / Pydantic strict; adapter subprocess calls through injected port only |
| Baseline | Ticket 01 reviewed/integrated baseline |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex implementation Agent / a fresh synchronized separate worktree after explicit dispatch |
| Environment | User-scope Agent host test environment only; no target project, no hidden config edit, no forced model turn |

## User-observable outcome

The setup flow can list Codex and Claude as `SUPPORTED` only when a tested user-scope adapter can detect, register, verify and later return `HostRemovalProof` for its exact installer-owned registration/payload. Missing CLI, access denial, login/policy failure, foreign existing plugin, unknown output or unsuccessful removal is clearly `INSTALL_BLOCKED` / `UNINSTALL_BLOCKED`, never a partial success.

## Scope and boundary

In scope: `HostLifecyclePort`, typed detection/registration/removal receipt/proof, command-runner port and fake adapters; one independently verified adapter implementation per available supported host; a host capability report that contains no command output, paths, tokens or project data. Proposed paths: `library/local_orchestration/{host_lifecycle,host_adapters,process_runner}.py` and `tests/test_reversible_agent_host_lifecycle.py`.

Out of scope: guessing undocumented Codex/Claude config formats, direct edits to host caches, host account login, marketplace credentials, model/thread creation, target project files, runtime event processing, Inno packaging and automatic host updates.

Frontend composition / DI: installer host-selection/status view is composed from typed `HostCapabilityReport`; production binds a verified `CommandRunnerPort`, while tests bind recorded fake command responses. UI text shows supported/foreign/blocked and retry state without exposing command output.

## Handoff and role assignment

- Control-plane/reviewer remains Codex/current `main`; implementation owner is the named separate Codex implementation Agent; owner override `N/A`.
- The handoff must state which host(s) are expected to be live-tested. Current control-plane discovery found `codex.exe` but execution returned access denied; no actual Codex command form is approved or assumed. `claude` was not detected. These facts require capability testing, not a weakened adapter.
- `COMPLETED` is legal only for a host whose complete reversible lifecycle has evidence. A host that cannot prove removal is `BLOCKED`, and later packaging must omit it rather than leave residue.

## TDD and defect checks

1. **Normal lifecycle red/green:** fake host initially lacks a registration; green proves typed `detect → register → verify → receipt → unregister → HostRemovalProof` removes the exact registration and any receipt-owned host payload. A real host smoke is required only after fake contract coverage passes.
2. **Path-prefix boundary:** test exact receipt-owned host path/identifier, one-extra-character prefix, trailing slash, casing, URL encoding, traversal and empty value. Adapter must never remove a value outside its exact receipt mapping.
3. **Null / empty boundary:** test `None`, omitted/undefined-equivalent, empty, whitespace and empty container host ID, receipt, command result and removal proof; all halt before a process invocation.
4. **Authority bypass:** direct `unregister` and indirect install/update/retry paths must require an installer-owned receipt for the same installation ID. A manually installed marketplace/plugin entry is `FOREIGN` through every entry point.
5. **Token comparison:** adapter must not accept/store a credential or token. Source-scan no token equality comparison and no command output/argument persistence; host identity receipts are typed non-secret metadata.
6. **Stable errors / exception behavior:** inject executable missing, access denied, nonzero command result, malformed output, login/policy denial, timeout and removal failure. Assert finite public state, unique internal reason, no exception escapes the application boundary and no false receipt/success is emitted.
7. **Regression proof:** test that a removed host has no receipt-owned registration/payload, a foreign host remains untouched, and a raw command/source sentinel cannot enter report, ledger or log. Preserve first red evidence.

## Completion evidence

- Required: red evidence; fake lifecycle tests; strict mypy; compile; metadata/privacy sentinel; live user-scope smoke for each claimed host; exact removal proof; target-repository non-interference snapshot; review and docs-only handoff.
- Formal-environment migration: no deployment. Host account/plugin state changes occur only in an explicit local test profile and must be reversed by the same adapter before handoff.
