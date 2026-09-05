# CAP-MSIX-01 — Prove the package lifecycle entry points before implementation

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `CAP-MSIX-01` / `CAPABILITY_INVESTIGATION` / `01` |
| State / closure | `RESEARCH_AUTHORIZED` / `CLOSURE-CAP-MSIX-01`, revision 01 |
| Authority | Owner's 2026-09-05 project-convergence/MSIX directive plus acceptance of Johnny one-click complete removal. Investigation only; not implementation approval or an external-effect grant. |
| Requirement / ADR | `PRD/CHG-20260905-050` revision 02 / `ADR-20260905-038` revision 02 |
| Context / SPEC | `doc/context/local-orchestration-installer/msix.md` revision 02; installer SPEC effective MSIX override (package-effect acceptance still being frozen) |
| Source baseline | `21ddcaa9dd90682d771a1dc9c1f8972434a5b5c5`; use the subsequent exact committed ticket/registry as query authority |
| Reviewer / research owner | Current-session reviewer / reuse `/root/plugin_adoption_implementer`, Luna/xhigh, explicitly read-only research role for this query |
| Workspace / profile | Current Johnny repository, immutable committed reads; no write worktree/branch allocation. POC / STANDARD; one helper, no fan-out. |
| ContextView / return | `CAPMSIX01R1-20260905`; prior UIX-02 view remains closed. Return `FINDINGS`, `NO_FINDINGS` or `BLOCKED`, never implementation/release success. |
| Language / effects / XSS | No product code or public DTO. Documentation research and bounded read-only local commands; `XSS_NOT_APPLICABLE`; no renderer/provider/account/host mutation. |

## One observable outcome

A finite capability matrix for the accepted MSIX lifecycle, separating documented
primitives, locally observed tools, and still-unexecuted Windows behavior. The reviewer
must be able to select the next **real** proof step without treating an emulator,
command exit code, package presence or installation instructions as lifecycle evidence.

## Read boundary

Read the exact requirement/ADR/Context and this ticket. Use official Microsoft Learn,
Windows SDK/NuGet documentation and official Python packaging documentation only when
directly needed. Repository source is limited to the named installer entrypoints in
the MSIX Context; do not scan/load the whole library or old installer ticket history.
Read-only tool discovery may inspect Windows SDK tool locations, command availability,
Windows version and supported command help. Do not read credentials, host configs,
installed-package inventories unrelated to Johnny, production data or another project.

## Closed questions and evidence cells

| Cell | Required question / evidence |
| --- | --- |
| MC1 | Can MakeAppx/SignTool be obtained as official, version-pinned, user-local tools without running an admin SDK installer? Identify exact official package/tool locations, provenance verification, dependencies and documented limitations. Observe what is available locally. Do not download/install/execute acquired tools in this research lane. |
| MC2 | For a packaged full-trust desktop app, identify supported package identity/location readback and launch mechanism. Explain which facts require actual package deployment/launch and cannot be established by an unsigned archive. |
| MC3 | Identify supported removal primitives and the lifetime problem when an app removes its own package: request, async completion, process termination/in-use behavior, independent post-removal observation, failure and retry. A completion callback that dies with the package is not proof. Report unresolved race/ownership questions rather than inventing a service/helper. |
| MC4 | Define the isolated test prerequisites for install/update/Johnny removal/direct Windows removal: exact package identity and certificate trust scope, disposable Windows user/VM, mutable-state readback, external-host sentinels and cleanup evidence. Distinguish developer/test signature from company distribution; do not import/create/export certificates. |
| MC5 | Counter-evidence: package installed without host activation; nonzero/removal timeout/ambiguous readback; direct Windows removal with external registration residue. Name what must remain unproved, and how a future reviewer would falsify an unjustified COMPLETE claim. |

For each cell give native primitive/API or tool, race model, failure semantics, one
adversarial reproduction recipe, source URL or exact local command/output, and one of
`DOCUMENTED_NOT_EXECUTED`, `LOCALLY_OBSERVED`, `UNAVAILABLE`, `REQUIRES_ISOLATED_EXECUTION`.
No YES/proved lifecycle claim without the corresponding actual observation. A missing
SDK is a provisioning task, not evidence that MSIX itself is impossible.

## Write/effect boundary and continuation

Research owner writes no file, changes no ref, installs no tool/package/certificate,
invokes no host mutation/provider, creates no process/service/user/VM and spawns no
helper. Ordinary read-only command subprocesses are allowed; that is not permission
to launch product/runtime processes. Parent persists the reviewed evidence in a
directly indexed report and alone selects implementation boundaries.

No runtime receipt/runner/gateway is needed for this same-lifetime research query.
Dispatch once, then `wait_agent`; no activity/status polling. Source/bootstrap/build
implementation waits for the resulting exact capability plan and its admission.
