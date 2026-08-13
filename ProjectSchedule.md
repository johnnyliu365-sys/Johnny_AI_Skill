# 通用功能模組庫工作排程

## 現行階段

- 日期：2026-08-08（Asia/Taipei）
- 階段：`LOCAL_ORCHESTRATION_INSTALLER_POC_SPEC_DRAFT`
- 目前功能集群：`local-orchestration-installer` 正在規格化；既有 `autonomous-collaboration-audit` POC 已收斂至 handoff，`router-framework`、`context-load-telemetry` 與 `reusable-module-library` 維持既有完成狀態，不混入本 POC。
- 唯一工作流程：`Workflow.md`

## 順序

1. 建立共同 Context、PRD、需求變更、安全邊界與 SPEC，並取得使用者核准。
2. 拆成單一垂直工單並取得第二次核准。
3. 逐張工單依 TDD，在本專案重新實作、Smoke Test、review 與 handoff。

## 優先序

1. Python NLP 契約與規則式文字處理。
2. Python 金流契約、帳本與 idempotency 邊界。
3. Python 可靠性與 LINE transport 集群。
4. Kotlin 地理解析候選集群。
5. C# 遊戲規則候選集群。

## Ticket Handoff

- `01-library-root-and-readmes`：`DONE`（commit `9b218a9`）。
- `02-python-nlp-contracts`：`DONE`（commit `88fbfc0`）。
- `03-python-nlp-rule-parsers`：`DONE`（commit `d03880e`）。
- `04-python-nlp-provider-boundaries`：`DONE`（commit `02fa06f`；起始 rollback tag `rollback/ticket-04-start-20260801`）。
- `05-python-payment-contracts-ledger`：`DONE`（commit `17ed764`）。
- `06-python-payment-provider-reconciliation`：`DONE`（commit `6c7d9dc`）。
- `07-python-reliability-core`：`DONE`（commit `7b56135`）。
- `08-python-line-transport-identity`：`DONE`（commit `fd5187b`）。
- `09-python-event-timeline-audit`：`DONE`（commit `655f09d`）。
- `10-python-engagement-rules`：`DONE`（commit `f0a4bfc`）。
- 下一張候選：`11-kotlin-offline-geo-resolution`；必須等待使用者明確確認後才可開始。

## Router Framework POC

1. `01-poc-router-core`：`DONE`；已建立 Profile 驅動的路由核心、Context 引用映射與四個框架接點，並完成測試與 review。
2. POC 完成後，才依證據決定是否擴充為能接管真實專案的 MVP；不得自動升級。

## Module Application Skill POC

1. `01-module-catalog-skill`：`DONE`；已建立 READY 模組選擇卡、可攜 Codex skill 和新專案最小載入指引。
2. 後續套件發行或全域 skill 安裝必須由新的 CHG、SPEC 與 ticket 處理；目前只交付可版控的 repo 內來源。

## Plugin Distribution POC

1. `01-private-git-plugin`：`DONE`；已建立 repository-root plugin manifest、private Git marketplace catalog、接管 skill 與可拔除契約 README。
2. 個人 Codex 環境的實際安裝、啟用、停用與 marketplace 移除由使用者自行選擇；不得當作公司專案的 runtime 或 CI 依賴。

## Claude Code Plugin Distribution POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder and specification | DONE | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| Shared-skill Claude manifest and marketplace entry | DONE | `modules/tickets/claude-code-plugin-distribution/01-claude-code-plugin.md` |
| Static validation and code review | DONE | JSON, skill/plugin validation, 48 tests, 54 strict type-checked source files, and diff check |
| Live Claude Code smoke test | USER_ENVIRONMENT | `claude plugin validate .` after cloning with private-repository access |

## Context Load Telemetry POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder, change, specification, and ticket | DONE | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| Metadata-only telemetry and validator | DONE | `modules/tickets/context-load-telemetry/01-metadata-only-telemetry.md` |
| Test, type-check, and review | DONE | 55 tests, strict type checking across 56 source files, compile check, and review |

## Plugin Release 0.3.0

| Milestone | State | Evidence |
| --- | --- | --- |
| Change, specification, and release ticket | DONE | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` |
| Manifest and shared-skill packaging | DONE | `modules/tickets/plugin-release-telemetry/01-package-current-skill.md` |
| Validation and review | DONE | Plugin/skill validation, 55 tests, strict type checking across 56 source files, and diff check |
| Commit | DONE | `368d513` (`release: package plugin version 0.3.0`) |
| Push | IN_PROGRESS | Push the reviewed release and its documentation handoff to `origin/main` |

## Historical Private Router POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder, Architecture, Grill, and ADR | DONE | `doc/context/private-router-saas/main.md`; `doc/adr/ADR-20260804-001-private-router-saas.md` |
| Change and specification draft | DONE | `CHG-20260804-008`; `modules/spec/private-router-saas.md` |
| Product-owner specification approval | DONE | Owner approved `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` on `2026-08-04` |
| Ticket planning and second approval | DONE | Project owner approved `01-private-router-metadata-gate` on `2026-08-04` |
| Implementation, test, review, and release | DONE | 64 tests, strict type check, compile, plugin validation, Code Review, and handoff completed for `01-private-router-metadata-gate` |

| Future commercialisation / deployment | SUPERSEDED | `CHG-20260805-010` changes the active objective to non-commercial multi-AI collaboration automation. |

## Continuous Workflow Governance POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change and Grill | DONE | `CHG-20260805-009`; `doc/context/workflow-governance/main.md` |
| Specification | DONE | `modules/spec/workflow-governance.md` (`APPROVED` on `2026-08-05`) |
| Ticket plan, named implementation owner, and second approval | DONE | `01-enforce-continuation-and-handoff` approved on `2026-08-05`; implementation worktree assigned and reviewer recorded. |
| Implementation, verification, review, and handoff | DONE | Implementation worktree completed at `a94e207`; independent 73-test / strict-type review is `APPROVED` in `doc/reviews/workflow-governance/01-enforce-continuation-and-handoff-code-review.md`; integrated by `2f545c8`. |

## Autonomous Multi-AI Collaboration and Audit POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change and Grill | DONE | `CHG-20260805-010`; `doc/context/autonomous-collaboration-audit/main.md` |
| Specification | DONE | `modules/spec/autonomous-collaboration-audit.md` (`APPROVED` on `2026-08-05`) |
| Ticket 01 dispatch | IN_PROGRESS | Owner selected `ONE_IMPLEMENTATION_AGENT` and confirmed `01-topology-dispatch-lanes` as delivered to the named existing implementation worktree; planning lane moved to Grill for ticket 02. |
| Ticket 02 / 03 | PLANNED | Ticket 02 is in planning-lane Grill; ticket 03 remains planned. Each receives authority only from its own future delivery confirmation. |
| Implementation, review, and handoff | IN_PROGRESS | Ticket 01 implementation owner synchronizes its own worktree, performs TDD and returns typed evidence. |

## Local Orchestration Adapter and Detachable Installer POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change, Wayfinder, Architecture and Grill | DONE | `CHG-20260808-011`; `doc/context/local-orchestration-installer/main.md`; `doc/adr/ADR-20260808-003-local-orchestration-installer.md` |
| Specification | DONE | `modules/spec/local-orchestration-installer.md` was approved by the owner on `2026-08-08`. |
| Ticket 01 implementation | DONE / APPROVED / INTEGRATED | Closure `C1..C8` passed; implementation `ddd9f55`, correction `040a0f6`, review `dc63364` and guarded merge `491f98b`. |
| Ticket 02 implementation | DONE / APPROVED / INTEGRATED | Closure `D1..D8` passed; implementation `6cc8fb5`, independent review `4527f49`, guarded merge `92c58bf`; allocation and branch released. |
| Ticket 03 implementation | DONE / APPROVED / INTEGRATED | Closure `H1..H8`; implementation `16597b6`, H7 correction `673ff7c`, final review `5601594`, guarded merge `60cb8cf`; allocation and branch released. |
| Toolchain and Codex capability probe | DONE / VERIFIED | Inno Setup 6.7.3 is installed per user with valid signature and compile proof. One disposable Codex CLI marketplace/plugin was installed, hash-verified and completely removed without target-project access. |
| Parent Ticket 05 Codex CLI adapter | SUPERSEDED / CONVERGENCE_DECOMPOSED | Correction review found CR-80..CR-85; rejected branch/SHAs remain evidence and its allocation/receipt are closed. |
| Ticket 05A CLI contract/preflight | DONE / APPROVED / INTEGRATED | Implementation `97ab31c`; repaired handoff `fb755268`; review `d54c0bd`; owner-authorized ledger-preserving merge `b22c6c4`; post-merge verification passed. |
| Ticket 05S combined staging parent | SUPERSEDED / DECOMPOSED | Rejected commits remain immutable evidence; no correction or integration. |
| Ticket 05S1 disposable environment core | DONE / APPROVED / INTEGRATED | Correction `41d5ce4`, handoff `e1087d3`, review `17ea1d5` and guarded merge `504a3ec`; post-merge verification passed. |
| Ticket 05S1R project-owned disposable runtime root | COMPLETE / APPROVED / INTEGRATED | Guarded merge `d399364` preserves the full parent/correction/child history and both WPR evidence sets; post-merge core 10, six-suite 79, full 414 and strict static checks pass. |
| Ticket 05S1R1 TEMP-checkout portability evidence | COMPLETE / APPROVED / INTEGRATED | Implementation `d024e69a`, handoff `3488efea`, review `abb07bb`, merge `d399364`; CR-169 closed. |
| Ticket 05S2 bounded child-process runner | DONE / APPROVED / INTEGRATED | Revision-03 `33a8fa9` / `dba0621b`, review `c97b754`, guarded merge `6e24e06`; CR-124 resolved and post-merge verification passed. |
| Ticket 05S3 Codex protocol fixture | DONE / APPROVED / INTEGRATED | Correction `4835b0f`, handoff `008fac8`, final review `c518e62` and guarded merge `43a1639`; CR-125 closed and post-merge verification passed. |
| Ticket 05S4 Codex lifecycle oracle | DONE / APPROVED / INTEGRATED | Correction `02f33ef`, handoff `52ab9c0`, review `68ff06b`, guarded merge `4af381c`; CR-126/CR-127 closed and post-merge verification passed. |
| Ticket 05B transactional registration parent | SUPERSEDED / CONVERGENCE_DECOMPOSED | Terminal CR-98..CR-104 evidence is immutable; replaced by 05B1-05B4 after integrated staging. |
| Ticket 05B1 registration contracts/journal | DONE / APPROVED / INTEGRATED | Correction `dc57ff9`, handoff `1df30ae`, review `36ec95c` and guarded merge `bbc7de5`; CR-128..CR-132 closed and post-merge verification passed. |
| Ticket 05B2 command-attempt classification | COMPLETE / APPROVED / INTEGRATED | Corrected strict classifier and full C1-C4 matrix integrated by `c97505c`; completion recorded by `ef45f65`. |
| Ticket 05B3 exhaustive compensation | SUPERSEDED / CONVERGENCE_DECOMPOSED | Terminal rejected evidence retained; replaced by ADR-20260811-004 and 05B3A-05B3C. |
| Ticket 05B3A safe port capability | COMPLETE / APPROVED / INTEGRATED | Revision-02 correction `a87af38`, handoff `0378655`, review `dda8ba4` and guarded merge `8a13eb7`; post-merge focused/full/type/compile passed and CR-137..CR-139 are closed. |
| Ticket 05B3B pure compensation reducer | SUPERSEDED / CONVERGENCE_DECOMPOSED | Revision-02 `3f22551` / `4d5bbef` remains terminal rejected evidence; no third same-closure correction or integration. |
| Ticket 05B3B1 recursive plan identity admission | COMPLETE / APPROVED / INTEGRATED | Implementation `b50699c`, handoff `441bcc8`, review `382cc95`, merge `ac91290`; terminal I1-I5 plus parent R1-R5 and all eight reversals passed. |
| Ticket 05B3C compensation composition | COMPLETE / APPROVED / INTEGRATED | Guarded merge `d8f6127` integrated reviewed handoff `6d7dd37`; post-merge verification passed. |
| Ticket 05B4 registration composition parent | CONVERGENCE_DECOMPOSED / CHILD_05B4B1_INTEGRATED / CHILD_05B4B2_DECOMPOSED | CR-148/CR-149 are closed; B2 is split into independently reviewable B2A-B2E. |
| Ticket 05B4A registration port capability | COMPLETE / APPROVED / INTEGRATED | Correction `3ab5971`, handoff `7ce9bb3`, terminal review `47bc1e1` and guarded merge `5f30a71`; CR-146/CR-147 closed. |
| Ticket 05B4A1 plugin identity authority | COMPLETE / APPROVED / INTEGRATED | Implementation `76f0b96`, handoff `30d6bcf`, review `42e1590`, merge `3399cf9`; exact I1-I6 passed. |
| Ticket 05B4B registration transaction parent | CONVERGENCE_DECOMPOSED | Split pure forward decisions from effect/proof/receipt/compensation/oracle composition. |
| Ticket 05B4B1 pure registration reducer | COMPLETE / APPROVED / INTEGRATED | Correction `64e9e0a`, handoff `918c9af`, review `71f30be`, guarded merge `d7c5934`; post-merge verification passed. |
| Ticket 05B4B2 transaction parent | CONVERGENCE_DECOMPOSED / B2A-B2D_INTEGRATED / B2E_DECOMPOSED | Transaction authority, forward composition and both settlement lanes are integrated; lifecycle acceptance is split into E0-E6. |
| Ticket 05B4B2A transaction authority | COMPLETE / APPROVED / INTEGRATED | Correction `4e6924b`, handoff `e4841ab`, review `e03cb8d`, guarded merge `494aaca`; post-merge focused 11/11, full 294/294, strict mypy and compile 122 files pass. |
| Ticket 05B4B2B/B1/B2 and B2C | COMPLETE / APPROVED / INTEGRATED | Forward `63e8a7b`; claim `0c4476f`; compensation context `e7cd37b`; proof settlement `af3a95a`. |
| Ticket 05B4B2D compensation settlement | COMPLETE / APPROVED / INTEGRATED | Implementation `bf9278f`, handoff `60a8311`, review `eef459e`, guarded merge `9769a75`; post-merge 353 tests and strict mypy passed. |
| Ticket 05B4B2E lifecycle acceptance parent | CONVERGENCE_DECOMPOSED / NON_DISPATCHABLE | E0 oracle evidence, E1 identity, E2/E3 adapters, E4 success, E5 compensation and E6 isolation are separately accepted. |
| Ticket 05B4B2E0 oracle logical installed path | COMPLETE / APPROVED / INTEGRATED | Merge `3fc2f99`; post-merge focused 17/full 360/strict mypy pass; allocation released and receipt closed. |
| Ticket 05B4B2E1 oracle identity binding | COMPLETED / APPROVED / INTEGRATED | Merge `27c8305`; CR-159 closed by recursive 14-node rejection, full 370 and strict typing. |
| Ticket 05B4B2E2A oracle version observation | COMPLETED / APPROVED / INTEGRATED | Merge `52a2a4e`; combined focused 44/full 379/strict mypy pass. |
| Ticket 05B4B2E3A compensation finite failure | COMPLETED / APPROVED / INTEGRATED | Merge `b324f91`; combined focused 44/full 379/strict mypy pass. |
| Ticket 05B4B2E2B registration no-effect failure | COMPLETED / APPROVED / INTEGRATED | Merge `784d08a`; CR-160 incident remains truthfully preserved. |
| Ticket 05B4B2E3B oracle owned-absence preservation | COMPLETED / APPROVED / INTEGRATED | Merge `dc07eec`; CR-161 subclass/constructed evidence is finitely blocked. |
| Ticket 05B4B2E2 registration oracle adapter | COMPLETED / APPROVED / INTEGRATED | Merge `d3d3c1d`; post-merge focused 14/full 409/strict mypy and compile 134 pass; allocation released and receipt closed. |
| Ticket 05B4B2E3C compensation request revalidation | COMPLETED / APPROVED / INTEGRATED | Merge `c042af1`; reviewer focused 24/full 395/strict mypy 132 passed. |
| Ticket 05B4B2E3D compensation response admission | REFREEZE_REQUIRED / 05S1R_DEPENDENCY_SATISFIED | Owner2 uncommitted two-path work is preserved at exact hashes. Refreeze against merge `d399364` before resume. |
| Ticket 05B4B2E3 compensation oracle adapter | PLANNED / DEPENDENCY_WAIT | Refreeze as a thin effect adapter only after E3D approval/integration. |
| Ticket 05B4B2E4 registration success acceptance | REFREEZE_REQUIRED / 05S1R_DEPENDENCY_SATISFIED | Immutable implementation/handoff `3375237`/`5cf2235` remain on the existing E4 branch; refreeze its revision-02 correction against merge `d399364`. |
| Tickets 05B4B2E5-E6 lifecycle acceptance | PLANNED / DEPENDENCY_WAIT | Compensation and isolation remain small dependency-ordered acceptance tickets. |
| Ticket 05C receipt removal/replay | PLANNED / DEPENDENCY_WAIT / REFREEZE_REQUIRED | Starts only after 05A/05B approval/integration and a finite behavior/rollback closure refreeze. |
| Ticket 06A Codex role-profile capability proof | DONE / APPROVED_EVIDENCE / INSTALL_BLOCKED / INTEGRATED | Implementation `38e9a8b`, handoff `f6f186f`, review `62955ec`, guarded merge `de4141e`; actual installed-host result is `ROLE_ISOLATION_UNPROVEN / ACCESS_DENIED / OUTPUT_UNAVAILABLE`, so capability dependents stay blocked. |
| Autonomous Ticket 04 reviewer-only authority | PLANNED / DEPENDENCY_WAIT | Starts only after reviewed 06A `SUPPORTED`; typed fake effect gate, not a real Agent turn. |
| Tickets 06B/06C role-profile lifecycle/composition | PLANNED / DEPENDENCY_WAIT | Wait for 06A and autonomous Ticket 04; own/remove profiles, then compose exact reviewer authority. |
| Ticket 04 package parent | DECOMPOSED / NON_DISPATCHABLE | `CHG-20260812-014`; replaced by serial 04A-04I. |
| Ticket 04A payload manifest contract | PLANNED / DEPENDENCY_WAIT | After runtime/host prerequisites; pure typed source/test only. |
| Ticket 04B Inno installer build source | PLANNED / DEPENDENCY_WAIT | After 04A integration; `.iss`/build source and disposable compile only. |
| Ticket 04C version-one candidate freeze | PLANNED / DEPENDENCY_WAIT | After 04A/04B integration; freeze complete clean source SHA. |
| Ticket 04D remote staging warm backup | PLANNED / DEPENDENCY_WAIT | After 04C: create/fast-forward exact candidate to `origin/staging`, then SHA readback. No push now. |
| Ticket 04E disposable Windows environment | PLANNED / DEPENDENCY_WAIT | After 04D; qualify standard-user Windows isolation only, no product install. |
| Ticket 04F Windows release build | PLANNED / DEPENDENCY_WAIT | After 04D/04E; clean staging export build only, no install. |
| Ticket 04G disposable Windows install | PLANNED / DEPENDENCY_WAIT | After 04F; physical install acceptance only. |
| Ticket 04H disposable Windows uninstall | PLANNED / DEPENDENCY_WAIT | After 04G; product removal/absence/foreign preservation only. |
| Ticket 04I first-version freeze | PLANNED / DEPENDENCY_WAIT | After 04G/04H; immutable source/toolchain/manifest/artifact/review record. |

## Guided Project Bootstrap and Adaptive Delivery

| Stage | State | Evidence / next gate |
| --- | --- | --- |
| Requirement / architecture | DONE | `CHG-20260813-016/017`; `ADR-20260813-008/009`; install/init separation, reviewer-first activation, adaptive delivery and post-POC staging lifecycle confirmed by owner. |
| Exact specification | DRAFT / OWNER_REVIEW_REQUIRED | `modules/spec/adaptive-project-orchestration.md` AC-01 through AC-11. |
| Ticket decomposition | BLOCKED / SPEC_APPROVAL_REQUIRED | Candidate sequence is recorded in the draft SPEC; no formal ticket, owner, receipt, branch or worktree allocation yet. |
| Current implementation lanes | UNAFFECTED | 05S1R continues on its frozen baseline; owner2 E3D state remains preserved. |

### Ticket 05 selection after external capability proof

The owner-authorized probe resolved the two external uncertainties without
claiming that discovery code is production source. Codex CLI 0.144.0-alpha.4
completed exact marketplace add, plugin add, structured verification, plugin
remove and marketplace remove for a disposable local payload; matching source
and installed hashes plus final plugin/marketplace/path absence were recorded.
Inno Setup 6.7.3 was independently signature/version/compile verified.

Ticket `05-codex-cli-host-adapter` is now the sole selected vertical slice. It
must turn the documented CLI mechanism into strict receipt-bound adapter source
within K1–K8, four production files and one test. It uses exactly one branch in
the existing sole implementation worktree; no second live registration,
additional worktree, target-project access or schedule is authorized. Ticket 04
remains dependency-waiting until independent Ticket-05 approval and integration.

### Version-one staging and package convergence

Owner change `CHG-20260812-014` makes remote `staging` a pre-release-build warm
source backup and the baseline for later feature/architecture work. The remote
has no current `staging` ref, while unfinished local `main` is ahead of
`origin/main`; therefore no push occurs now. After runtime/host prerequisites,
04A and 04B separately implement and integrate the manifest contract and Inno
build source. 04C freezes that exact clean candidate and 04D alone may create or
fast-forward `origin/staging` to its SHA with mandatory readback. Package parent
04 is non-dispatchable; serial 04E-04I separately accept Windows environment,
clean-export release build, install, uninstall/absence and immutable version-one
evidence. Public release, deployment and `main` push remain outside this plan.

Initial independent review `dac99fd` reproduced false/escaping boundary results,
partial registration residue, foreign absence-proof acceptance and an adapter
contract incompatible with the documented CLI. Ticket design repair
`CLOSURE-LOCAL-INSTALL-T05-02` adds the missing installer-owned marketplace
source boundary and exact public JSON contract. The same implementation lane
received its one additive correction; Ticket 04 remains dependency-waiting.

The single correction review covered `c2ea3f8`, `3f6c41a`, `13d02de` and
`4c9525b`. Although focused/full tests and strict typing pass, the public CLI
JSON DTOs, canonical root/proof binding, finite failure mapping, cleanup proof,
foreign collision gate and evidence matrix still fail CR-80..CR-85. Ticket 05
is now `CONVERGENCE_REVIEW_REQUIRED`; no third same-closure correction,
integration, Ticket-04 dispatch, new branch or new worktree is permitted before
control-plane decomposition.

### Ticket 05 convergence decomposition

| Item | Authoritative reference |
| --- | --- |
| Superseded parent | `PRG-20260810-082`; `codex-cli-host-adapter-and-detachable-installer`; `CLOSURE-LOCAL-INSTALL-T05-02` |
| Child 05A | `05a-codex-cli-preflight-contract`; integrated by `b22c6c4` |
| Child 05B | `05b-codex-cli-transactional-registration`; current references below |
| Child 05C | `05c-codex-cli-receipt-removal`; `PLANNED / DEPENDENCY_WAIT / REFREEZE_REQUIRED` |

### Ticket 05B selection and dispatch

Only the reference chain is retained here; requirements live in the ticket and
findings live in the review report.

| Stage | Authoritative identifiers |
| --- | --- |
| Dependency | Ticket 05A integration `b22c6c4` |
| Revision 01 dispatch | `PRG-20260810-095`; `hnd_local_orchestration_install_05b_20260810`; `aln_local_orchestration_install_05b_20260810`; `rcpt_local_orchestration_install_05b_20260810`; `corr-local-orchestration-install-05b-20260810` |
| Revision 01 return/review | `5e919069`; `ef1cf42`; `PRG-20260810-097`; `f02704f`; `CR-92..CR-97` |
| Revision 02 refreeze | `PRG-20260810-098`; `a7dd4a4`; `CLOSURE-LOCAL-INSTALL-T05B-02` |
| Revision 02 correction | `PRG-20260810-099`; `hnd_local_orchestration_install_05b_corr1_r02_20260810`; `corr-local-orchestration-install-05b-corr1-r02-20260810`; `1a269411`; `ed74589` |
| Terminal review | `PRG-20260810-101`; control commit `24227ac`; `CR-98..CR-104`; `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |

### Ticket 05S staging-first convergence

The owner requires an isolated verification environment before 05B/05C/04 are
rewritten. Host capability inspection found no available Windows Sandbox
executable, no current Hyper-V management permission and no running Windows
container engine. A Linux-container or temporary-directory-only claim cannot
serve as Windows package staging.

The first bounded gate is therefore Ticket 05S: a test-owned executable child
process plus persisted disposable filesystem state that independently proves
the documented Codex add/list/remove/absence lifecycle without invoking live
Codex. The initial 05S return did not yet expose the injectable bounded command
port or official add/remove shapes and leaked roots on invalid topology, so
revision 02 is the sole same-branch correction. Ticket 05B remains immutable
blocked evidence while 05S is corrected and terminally reviewed. Only after 05S
integration will the control plane refreeze 05B and 05C against the staging
oracle; Ticket 04 will additionally require a real disposable Windows
user-profile provider.

Revision 02 did not pass terminal review. Its exact full-suite command creates
repository caches and fails R12, while adversarial probes found state-only
foreign installed truth and incomplete SemVer/path/process evidence. 05S is now
paused at `CONVERGENCE_REVIEW_REQUIRED`; 05B/05C/04 are not refrozen or
dispatched.

Owner decision `PRG-20260811-106` decomposes, rather than repairs, 05S. The new
serial path is `05S1 environment → 05S2 process runner → 05S3 protocol fixture
→ 05S4 lifecycle oracle`. Acceptance responsibility stays with the independent
control-plane reviewer and each child owns only its named behavior. 05S1 is
selected next but remains `NOT_DISPATCHED`; no automatic correction loop,
branch or allocation was created by decomposition.

The owner subsequently authorized starting the environment-first ticket. 05S1
now has one unique handoff/allocation/receipt and may use only the sole existing
implementation worktree. 05S2–05S4 remain unallocated and cannot start.

The independent 05S1 review passed the focused/full suites, strict typing,
overlay, fault cleanup and physical child-escape probe, but a real Windows root
junction is not recognized by the Python 3.11 `Path.is_symlink()` gate. It is
misclassified only after an external marker read, and the submitted test proves
only a mocked branch. 05S1 is therefore paused at
`CONVERGENCE_REVIEW_REQUIRED`; 05S2 remains dependency-waiting and no automatic
correction or integration is scheduled.

The project owner subsequently authorized one bounded exception:
`OVR-LOCAL-INSTALL-T05S1-REPARSE-20260811-01`. It retains the existing 05S1
branch, worktree, allocation and receipt, and permits only early Windows
reparse-point detection plus a physical root-junction test. A bounded
test-fixture subprocess may create the junction; production code still cannot
execute a child process. The closure remains E1-E4/T1-T4 and 05S2 stays blocked.

The final owner-scoped 05S1 review approves correction `41d5ce4` and handoff
`e1087d3`. A fresh exported checkout passed the physical root-junction test,
177-test suite, strict typing and zero-residue checks. CR-118/CR-119 are closed;
05S2 remains dependency-waiting until the guarded 05S1 integration completes.

Guarded merge `504a3ec` integrates the reviewed 05S1 branch with control
approval `17ea1d5` as its first parent and handoff `e1087d3` as its second.
The progress-ledger conflict retained every PRG-108 through PRG-112 record.
Post-merge focused 5/5, full 177/177, strict typing, compilation and residue
checks passed. 05S1 is complete; 05S2 is the next serial ticket.

05S2 is now frozen as a process-only ticket. It owns one strict request/result
union, exact `shell=False` execution, a deterministic fixture and physical
timeout/WinError 5/WinError 206 evidence. It may import integrated 05S1 but may
not modify it or model Codex/plugin/install state. The sole implementation
worktree is reused; no additional worktree is authorized.

The independent 05S2 review passed focused 5/5, full 182/182, strict typing,
physical WinError 2/5/206 and extended timeout cleanup. It nevertheless proved
a real cwd-junction escape that wrote external bytes, an accepted NUL
executable that leaked `ValueError`, and a non-truthful committed late-sentinel
window. The control-plane closure also omitted finite kill/wait failure
semantics. Owner override `OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01`
refreezes only CR-120..CR-123 as `CLOSURE-LOCAL-INSTALL-T05S2-02` and
authorizes one additive correction on the existing branch/worktree. Any
blocker in the final correction review stops; merge and 05S3 dispatch remain
unauthorized until approval.

The revision-02 correction `34babbd` and handoff `c324c52` close the four
refrozen findings, and fresh-export focused 10/10, full 187/187, strict typing,
physical junction and cleanup checks pass. Final adversarial review nevertheless
proves CR-124: a first run-wait `OSError` is routed through the timeout cleanup
path and returned as `TIMEOUT_AFTER_START` after successful kill/reap. Because
the frozen P3/T3 union has no truthful started-child observation-failure state,
05S2 stops at `CHANGES_REQUESTED / TICKET_DEFECT`; no second correction,
integration or 05S3 dispatch is authorized.

The owner now authorizes revision 03 under
`OVR-LOCAL-INSTALL-T05S2-R03-20260811-01`. It refreezes CR-124 only: a real
run timeout and a first-wait `OSError` receive distinct triggers and successful
cleanup results, while every kill/reap failure records its initiating trigger.
One additive correction may run on the existing 05S2 branch/worktree. No new
branch/worktree or 05S3 dispatch is authorized before independent approval.

The revision-03 final independent review approves implementation `33a8fa9`
and handoff `dba0621b`. A fresh immutable export passed focused 12/12, full
189/189, strict mypy and compile across 91 files, plus the six-cell trigger /
cleanup matrix and strict malformed-model probes. CR-124 is resolved; guarded
integration is authorized, while 05S3 remains undispatched for this turn.

Guarded merge `6e24e06` integrates the control approval `c97b754` as first
parent and reviewed handoff `dba0621b` as second parent. The sole conflict was
the progress ledger; PRG-114 through PRG-124 were retained once in numeric
order. Post-merge focused 12/12, full 189/189, strict mypy and compile over 91
files passed with zero residue. 05S2 is complete. 05S3 is ready but remains
undispatched because this turn ends after the 05S2 integration.

05S3 implementation `bd59011` and docs-only handoff `f725d48` passed their
focused/full suites, strict typing, child binding, topology and cleanup checks.
Independent bounded-input probes nevertheless found CR-125: standard-library
JSON decoding can escape as `RecursionError` or plain `ValueError` instead of a
declared rejection. The ticket is `CHANGES_REQUESTED / FINAL_REVIEW_STOPPED`;
no correction, integration or 05S4 dispatch is authorized automatically.

The owner authorizes `OVR-LOCAL-INSTALL-T05S3-CR125-20260811-01` and
`CLOSURE-LOCAL-INSTALL-T05S3-02` for CR-125 only. The existing 05S3 lane may
add one correction from `f725d48` that maps the two proven standard JSON
decoder exceptions to the existing finite rejection and adds exact regression
tests. No new branch/worktree or 05S4 is authorized; the next review is final.

The revision-02 final review approves correction `4835b0f` and handoff
`008fac8`. Fresh-export focused 6/6, full 195/195, strict mypy and compile over
96 files passed. Exact original-shape decoder probes, duplicate-key specificity,
process-control exception escape and both independent reverse mutations passed
with zero residue. CR-125 is closed; guarded integration is authorized, but no
merge or 05S4 dispatch is performed by this correction authorization.

Guarded merge `43a1639` integrates control approval `c518e62` as first parent
and reviewed handoff `008fac8` as second parent. The sole conflict was the
progress ledger; PRG-126 through PRG-131 were retained exactly once in numeric
order. Post-merge focused 6/6, full 195/195, strict mypy and in-memory compile
over 96 files, exact CR-125 probes, source sentinels and zero-residue readback
passed. 05S3 is complete; 05S4 is ready but remains undispatched in this turn.

The owner then instructed the control plane to correct the stale 05S4 ticket
state and dispatch it. Commit `5ff47a2` synchronized the ready state before
ticket baseline `85ac8a0` froze O1–O6, the six-file source ceiling, real-child
composition and the complete CodeReview.md §2.1 TDD matrix. 05S4 is now the
unique active implementation ticket; 05B/05C remain outside its scope.
