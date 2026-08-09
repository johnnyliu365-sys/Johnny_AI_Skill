# 05 — Codex CLI Host Adapter

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / AC-01, AC-02, AC-07 and AC-08 |
| Context / change | `doc/context/local-orchestration-installer/main.md` / `CHG-20260808-011` |
| State | `SUPERSEDED / CONVERGENCE_DECOMPOSED` |
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

## Initial frozen closure — `CLOSURE-LOCAL-INSTALL-T05-01`

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

## Corrected closure — `CLOSURE-LOCAL-INSTALL-T05-02`

Initial review `dac99fd` classified CR-73 as a `TICKET_DEFECT`: the initial
closure required the documented local marketplace lifecycle without defining
the marketplace source locator required by the public CLI. This correction is
ticket design repair under the already approved SPEC; it does not change the
user outcome, authority, implementation owner, branch, worktree, allocation or
receipt. All K1–K8 requirements remain, with these finite clarifications:

| Repair | Required correction behavior |
| --- | --- |
| `R1` — owned source | Add a strict named marketplace-source reference to the install request. It identifies only a relative payload below the canonical installer-owned root. The injected filesystem boundary resolves and proves the ephemeral absolute local source before the first CLI effect; the adapter strictly reconstructs that returned proof and rejects target-project, URI, cwd-relative, foreign-installation, traversal, prefix/suffix/case or non-normalized values. No absolute source is stored in the receipt, Router, telemetry or handoff. |
| `R2` — actual CLI contract | Use the official command surface: plain typed `codex --version`; `plugin marketplace add <local-source> --json`; `plugin add <plugin>@<marketplace> --json` without `--version`; documented add/list/remove JSON DTOs (`marketplaceName`/`installedRoot`, marketplace `name`/`root`, plugin `installed`/`available`, and add/remove plugin identity fields). The expected plugin version is verified from observed output rather than supplied through an unsupported flag. |
| `R3` — exact receipt | A success receipt includes the canonical `HostRegistrationKey` and binds the current installation, marketplace source reference, marketplace, plugin, expected/observed version, manifest digest, exact installed relative locator and observed CLI plugin identity. Do not invent owner, digest or registration fields that the CLI does not emit; ownership comes from preflight absence plus the exact current-attempt request/add result/filesystem proof. |
| `R4` — finite boundaries | Root request/receipt and every returned port DTO are reconstructed with strict validation before use. Missing/invalid ports fail construction; timeout is finite and within bounds; nonzero, malformed JSON, unsupported surface, invalid UTF-8 and declared process errors return one finite typed blocked reason with zero false success. |
| `R5` — attempt cleanup | After the first owned mutation, every later failure attempts only current-attempt exact cleanup in plugin-then-marketplace order. Stale/missing verification cannot skip cleanup. Cleanup failure remains blocked with retry authority and never reports installed/absent. |
| `R6` — terminal absence | `ABSENT` or `REMOVED` requires the conjunction of exact plugin absence, exact marketplace absence and exact owned-path absence. A retry after plugin removal but before marketplace removal must finish or block marketplace removal; it cannot return early absence. |
| `R7` — exact proof | Filesystem manifest/absence results are recursively strict-revalidated and must match installation plus the exact source/installed locator and digest where applicable. Nominal, constructed, foreign, prefix/suffix/case, replayed or stale proof never authorizes success. |
| `R8` — evidence truth | Add one-to-one tests for every initial K1–K8 and R1–R7 boundary, including official JSON fixtures, cleanup/retry terminal state, unrelated plugin/marketplace invariance, actual existing/empty Git byte and porcelain snapshots, exact first-red output and isolated reverse mutations. The owner clears reviewer-generated `__pycache__/` before returning a clean worktree. |

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

## Correction handoff

| Field | Value |
| --- | --- |
| Correction handoff | `hnd_local_orchestration_install_05_cr1_20260809` |
| Initial review | `dac99fd` / `doc/reviews/local-orchestration-installer/05-codex-cli-host-adapter-code-review.md` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05-02` (`K1..K8` plus finite repairs `R1..R8`) |
| Retained lane | Ticket `05`; task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; branch `codex/implementation-codex-cli-host-adapter-05`; allocation `aln_local_orchestration_install_05_20260809`; receipt `rcpt_local_orchestration_install_05_20260809` |
| Expected control baseline | The control-plane commit containing this ticket repair and `PRG-20260809-080` |
| Authorized correction | Additive implementation correction(s) and one docs-only correction handoff, limited to the same four production files and one test. The final net source/test ceilings remain `400` / `450`; simplify or replace incorrect code rather than adding another file. |
| Required return | Exact first-red names/reasons, official-schema fixtures, CR-73..CR-79 probes, K1–K8/R1–R8 green, strict mypy, no-bytecode in-memory compile, source/scope checks, actual-Git isolation, reverse mutations, clean worktree, implementation commit(s), then docs-only handoff commit. |
| Still prohibited | New branch/worktree, reset, amend, rebase, force, historical-source reuse, second live registration, target-project write, package/Ticket-04 work, merge, push, deployment or schedule action. |

## Correction review outcome

Correction commits `c2ea3f8`, `3f6c41a` and `13d02de` plus final docs handoff
`4c9525b` received the single allowed correction review. The submitted green
suite passed, but CR-80..CR-85 remain against the frozen K/R closure: public CLI
JSON is still modeled with incompatible fields; canonical source/root ownership
is not carried through proof; real process/filesystem failures can escape;
cleanup is not absence-verified; foreign plugin-name collision reaches mutation;
and the required first-red/reverse/byte-snapshot evidence is not reproducible.

Per Workflow §8.1, no third same-closure correction may be dispatched. The
ticket is blocked for control-plane architecture/ticket decomposition. Preserve
the current branch, commits, allocation and receipt as immutable evidence; this
state authorizes neither a new branch/worktree nor Ticket 04.

## Control-plane decomposition outcome

On 2026-08-10 the project owner instructed the control plane to begin the
required decomposition. This parent ticket is now historical and may never
re-enter `IMPLEMENT`. Its branch
`codex/implementation-codex-cli-host-adapter-05`, submitted SHAs, allocation
`aln_local_orchestration_install_05_20260809` and receipt
`rcpt_local_orchestration_install_05_20260809` remain immutable review evidence;
the allocation is released and the receipt is closed/non-reusable.

The unchanged approved SPEC outcome is decomposed into three sequential,
independently reviewed user-observable tickets:

1. [05A — contract and ownership preflight](05a-codex-cli-preflight-contract.md)
   owns official list DTOs, canonical root/source proof, collision checks and
   finite zero-mutation boundary failures.
2. [05B — transactional registration](05b-codex-cli-transactional-registration.md)
   owns official add DTOs, exact receipt construction, effect journaling and
   verified current-attempt compensation.
3. [05C — receipt-bound removal and replay](05c-codex-cli-receipt-removal.md)
   owns official remove DTOs, conjunctive terminal absence, replay isolation
   and the final production `SUPPORTED` lifecycle projection.

CR-80 maps to 05A/A1, 05B/B1 and 05C/C2; CR-81 to 05A/A2, 05B/B2 and
05C/C1/C3; CR-82 to 05A/A4, 05B/B5 and 05C/C2/C5; CR-83 to 05B/B3/B4 and
05C/C3; CR-84 to 05A/A3; CR-85 to A5/B5/C5. Evidence is therefore attached to
each vertical behavior, not split into a horizontal evidence-only ticket.

Only Ticket 05A is selected. It receives a unique handoff/allocation/receipt
and may create one new-ticket branch in the existing sole implementation
worktree from the clean integrated control baseline. Tickets 05B/05C and 04
remain `PLANNED / DEPENDENCY_WAIT`; no concurrent branch or worktree exists.
