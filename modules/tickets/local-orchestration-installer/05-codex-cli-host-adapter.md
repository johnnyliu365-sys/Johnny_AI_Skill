# 05 — Codex CLI Host Adapter

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `IN_PROGRESS / DISPATCH_PREPARED` |
| Language | Python 3.11, strict Pydantic contracts and a Windows Codex CLI infrastructure adapter |
| Baseline | Tickets 01–03 reviewed and integrated at `60cb8cf`; owner-authorized Codex CLI lifecycle proof recorded by `PRG-20260809-077` |
| Control-plane owner / reviewer | Codex / current `main` worktree |
| Implementation owner / worktree | Codex task `019fcc9c-f34f-7d53-a313-c70c90bf3245`, model `gpt-5.6-luna`, reasoning `xhigh`, existing sole `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` worktree |
| Environment | Windows user scope only; no target project, login, Secret, network, deployment or schedule |

## User-observable outcome

Given an installer-owned local marketplace payload, Codex registration reports
`SUPPORTED` only after the public CLI has added the exact marketplace and exact
plugin, validated their structured output and verified the installed manifest.
Removal accepts only the matching receipt, removes the exact plugin before the
exact marketplace, verifies both absent plus the exact installed path absent,
and returns a proof bound to the same installation. Replay reports absence
without touching another plugin, marketplace, cache root or target repository.

## Scope and fixed production surface

Authorized production changes are limited to:

- `library/local_orchestration/host_contracts.py`
- `library/local_orchestration/host_lifecycle.py`
- new `library/local_orchestration/codex_cli_adapter.py`
- `library/local_orchestration/__init__.py`

The only authorized test file is new
`tests/test_codex_cli_host_adapter.py`. Net production additions across the four
files must stay at or below 400 non-blank lines; the test file must stay at or
below 450 non-blank lines. Exceeding either ceiling returns `BLOCKED` for ticket
repair instead of adding files or abstractions.

The adapter owns only Codex's documented `plugin marketplace add/list/remove`
and `plugin add/list/remove` lifecycle for one exact installer-owned local
marketplace and plugin. Command execution and filesystem inspection are
required constructor-injected typed ports; neither port may be optional or
default to `None`. The Windows process binding uses an argument vector,
`shell=False`, a finite timeout and UTF-8 structured output. Dynamic JSON is
validated at the boundary before entering domain code.

Out of scope: Claude, hidden config edits, recursive cache deletion, broad
`clear`, login/auth changes, connectors, model execution, marketplace update,
network download, compiler/package work, target-project access, Secret handling,
push, deployment, release, another worktree or another implementation branch.

## Frozen closure — `CLOSURE-LOCAL-INSTALL-T05-01`

| Cut | Required red/green behavior |
| --- | --- |
| `K1` | Strict named value objects validate CLI version, marketplace, plugin, version, manifest digest and exact receipt/proof identity. Reject `None`, omitted, empty, whitespace, extra fields, wrong enum/value and unvalidated dynamic input before effects. |
| `K2` | Detect the injected executable and parse the exact Codex CLI version/capability. Missing executable, access denied, timeout, nonzero exit, malformed JSON or unsupported command surface maps to one finite typed blocked reason. |
| `K3` | Preflight structured marketplace/plugin lists. An exact foreign registration, same name under another owner/version, copied receipt, suffix/prefix/case mismatch or stale installation blocks before mutation; no existing registration is overwritten. |
| `K4` | Register in the only allowed order: exact marketplace add, exact plugin add, exact structured list verification and manifest SHA-256 equality. Success issues one receipt bound to installation, host, registration key, marketplace, plugin, version and digest; no command output/path/raw manifest enters Router or telemetry state. |
| `K5` | A failure after the first owned effect is finite and retryable. Recovery may invoke only the matching CLI remove operation proven by the current attempt; it never recursively deletes a cache or reports success with a partial registration. |
| `K6` | Unregister requires the exact receipt, removes plugin then marketplace, parses each response, verifies both absent and verifies the exact installed path returned by registration absent. Only then may it issue the matching `HostRemovalProof`. |
| `K7` | Replay, foreign receipt, tampered digest, mismatched owner/manifest, failed remove, stale list response and path-prefix tricks remain blocked or idempotently absent with zero unrelated effects. Existing installed plugins and marketplaces are byte/list invariant. |
| `K8` | Run exact ticket tests, full project tests, strict mypy, in-memory compile, source sentinel and reverse mutations for K1–K7. Existing and empty temporary Git repositories remain byte/porcelain identical. The control-plane live proof in `PRG-20260809-077` is capability evidence only; implementation may not perform a second live registration. |

## Evidence and review boundary

1. Preserve the first failing test name and reason for each K1–K8 cut before
   production changes.
2. Reverse-mutate at least strict JSON admission, owner/receipt matching,
   manifest equality, command order, failure recovery and absence verification;
   each focused test must fail and then pass after exact restoration.
3. Production source contains no `Any`, `type: ignore`, optional/`None` port,
   hidden-config/cache write, broad clear/delete, shell command string, Secret,
   target-project path, network or historical source copy.
4. Return one implementation commit, complete verification, and one separate
   docs-only handoff commit. The implementation owner makes no review,
   integration, packaging or next-ticket decision.
5. `CHANGES_REQUESTED` permits at most one additive correction on the same
   ticket, branch, owner, allocation and receipt. It never creates another
   branch or worktree; a failed correction review returns
   `CONVERGENCE_REVIEW_REQUIRED`.

## Implementation handoff

| Field | Value |
| --- | --- |
| Handoff | `hnd_local_orchestration_install_05_20260809` |
| Allocation | `aln_local_orchestration_install_05_20260809` |
| Receipt | `rcpt_local_orchestration_install_05_20260809` |
| Correlation / question | `corr-local-orchestration-install-05-20260809` / `q-local-orchestration-install-05-20260809` |
| Authority | Owner continuation plus exact tool/probe authority on 2026-08-09; bounded continuous authority `PRG-20260809-042`; capability proof `PRG-20260809-077` |
| Required baseline | The docs-only control commit containing this dispatch |
| Granted scope | Only the four production files, one test, K1–K8 evidence and implementation/docs-only commits listed above |
| Branch rule | Create exactly one new-ticket branch in the existing sole implementation worktree; review correction stays additive on that same branch |
| Not granted | Another worktree/branch, a second live Codex registration, hidden config/cache mutation, target-project write, compiler/package work, merge, push, deployment or schedule action |
