# Protected execution qualification specification — candidate

| Field | Value |
| --- | --- |
| Specification ID / revision | `SPEC-CONTROLLED-VERIFICATION-QUALIFICATION-20260909-01` / `01` |
| Status | `DRAFT / OWNER_GRILL_AND_APPROVAL_REQUIRED / NOT_EFFECTIVE` |
| Author / worktree / baseline | Current-session drafting assistant; `codex/controlled-verification-intake`; `d3c78b5b154b04a7fdaad544a3d00f1e91271dcb` |
| PRD / CHG | `PRD-20260908-051` / `CHG-20260908-051` |
| Context sources | [Wayfinder](../../doc/context/controlled-verification/wayfinder-r01.md), [architecture proposal](../../doc/context/controlled-verification/architecture-r01.md), [owner Grill packet](../../doc/context/controlled-verification/grill-r01.md), [managed index](../../doc/context/controlled-verification/README.md) |
| Shared Context | Not sealed; this candidate cannot authorize ticket creation or implementation until owner convergence, Context sealing and exact SPEC approval |
| Language / checker | Python 3.11, frozen validated contracts, `mypy --strict`; exact PowerShell native operational recipes are edge transport only |
| Maturity / intensity | POC / HIGH_ASSURANCE, derived from REQ-051's privileged cross-boundary workload; docs-only drafting has zero implementers |

## 1. Goal, scope and non-claims

Determine whether the accepted launcher/restricted-identity/protected-broker boundary can enforce
the requested invariants on the Windows lab and each declared Codex/Claude host surface. Produce
exact capability evidence, including honest unsupported results, before product adapters rely on
it. Missing capability is an output of the investigation, not permission to change the guarantee.

This SPEC does not deliver the final controlled verification product, install a production
service, publish a plugin, enroll the physical host, replace the Router or implement WA-04 again.
WA-04 keeps its approved source-admission contract and later independent ticket. No generic file
length limit, user-global governance copy, mandatory synchronous runner/receipt, provider call,
new real project workload or five-session stress suite is introduced.

## 2. Public contracts and independent authority

All objects are immutable, reject extra fields/coercions and use ordinary validated construction.
IDs/digests reuse the existing opaque-metadata and exact-digest conventions. Integers are strict
integers, never booleans/floats/strings. Optional data uses tagged alternatives, not correlated
nullable fields. Candidate source and operational paths never enter durable Router state.

| Contract | Required meaning |
| --- | --- |
| `QualificationScope` | Exact project/baseline, capability IDs, approved manifest revision/digest and `PURE_CONTRACT` or `WINDOWS_LAB`; native scope additionally binds exact VM, guest/bootstrap and checkpoint evidence references |
| `CapabilityKey` | Capability family, adapter revision, platform and exact host surface when applicable; `CODEX_CLI`, `CODEX_DESKTOP`, `CLAUDE_CODE_CLI` are distinct, never interchangeable |
| `QualificationPrerequisiteSet` | Unique required prerequisite keys and independent evidence references; missing, stale, conflicting or unavailable prerequisite refuses only dependent cells |
| `QualificationCase` | Unique cell ID, capability key, control/attack/reviewer-mutation role, immutable fixture/executable/dependency identities, exact argv/cwd/environment plan, expected oracle, prerequisite keys and resource/cleanup/evidence bounds |
| `QualificationManifest` | Nonempty ordered cases, exact source and owner-approved revision, single lane, explicit total budget, no implicit discovery expansion; duplicate cases/IDs or incomplete roster coverage reject |
| `AttemptBinding` | Manifest/case identities plus protected policy digest/owner, restricted subject, broker binary/configuration, enrollment/launcher, immutable candidate snapshot, resource plan, VM/checkpoint, OS execution identity and evidence owner; no caller boolean grants authority |
| `CapabilityObservation` | Independent observer identity and evidence binding, exact key, finite result, native primitive/race/failure semantics where applicable, named case observations; a reported PASS without its required positive/refusal evidence is malformed |
| `QualificationReport` | Exact manifest/baseline and complete expected-cell coverage, finite per-capability results, evidence references/digests and next-boundary classification; no model-authored test counts or review approval |

Finite proposal vocabulary:

```text
CapabilityFamily = PLAN_BINDING | POLICY_ISOLATION | RESOURCE_CONTAINMENT
                 | OWNED_CLEANUP | ATTEMPT_RECONCILIATION | HOST_MEDIATION
                 | RESPONSIBILITY_ADMISSION
Observation = PROVEN | FAILED | UNAVAILABLE | NOT_RUN
Admission = ADMITTED | REFUSED
Refusal = SOURCE_MISMATCH | INVALID_MANIFEST | APPROVAL_UNRESOLVED
        | PREREQUISITE_UNPROVEN | RESOURCE_ENFORCEMENT_UNAVAILABLE
        | HOST_ROSTER_UNQUALIFIED | EVIDENCE_INVALID | RECOVERY_REQUIRED
ReportOutcome = QUALIFIED_FOR_DECLARED_SCOPE | CAPABILITY_UNAVAILABLE
              | QUALIFICATION_FAILED | INCOMPLETE
```

These are new qualification-domain contracts, not additions to `ProcessStage` or new global
Router enums. A `PROVEN` prerequisite is returned by its protected evidence resolver for an exact
scope, never trusted because the caller supplied that word. Production integration still requires
its own review and authority gate after qualification. A report may honestly close an
investigation with `CAPABILITY_UNAVAILABLE`; it cannot then close REQ-051 as implemented.

## 3. Admission and immutable execution binding

1. Resolve the approved manifest independently of the requesting Agent; validate its scope and
   source identity. No arbitrary profile, command, retry count or load parameter is accepted by
   the public invocation. A manifest proposal has no execution authority.
2. Resolve every expected prerequisite and exact effect roster; compute the dependent case set
   from committed data. Unknown/unobservable effect paths refuse affected host qualification.
3. Bind code plus transitive executable inputs to a protected immutable snapshot through launch.
   Hashing a writable file and executing it later is insufficient. Substitution after admission
   must either be impossible by the proved primitive or refuse before work starts.
4. Validate finite budgets and prove required native controls before untrusted/project work.
   Trusted fixed bootstrap/read-only primitive discovery is separate from hostile workload; it
   must not execute a malicious fixture to discover whether containment existed.
5. Claim one immutable attempt key through a proved exclusive/atomic claim boundary before launch.
   A caller-supplied duplicate key is not a new attempt and cannot obtain a new budget.
6. Wait through process/events with deadlines, observe exact terminal/cleanup evidence and assemble
   the report. No model progress polling, natural-language command reconstruction or hidden retry.

Manifest amendment creates a new reviewed revision and invalidates prior admission. The request
cannot convert five slots with exactly one loaded slot into five loaded slots, even when total
run count stays unchanged. Changing script bytes alone, environment, working directory, approval
owner, resource mapping or evidence destination is equally a new binding.

## 4. Resource scope and finite experiment policy

The following is a proposed lab ceiling, not a production default or current permission to run:

| Dimension | Qualification ceiling / semantics |
| --- | --- |
| Active lanes / automatic retries | Exactly one active lane; zero automatic retries |
| Work per case | Each declared control/attack runs once; reviewer weaken/observe/restore is a separately declared sequence, never an implicit rerun-until-green |
| Workload duration | At most 30 seconds per synthetic workload case; at most 1,200 seconds summed approved case deadlines in one manifest; no test launches that would exceed the remaining total bound |
| Cleanup | At most 10 seconds per launched case, counted within the manifest's total; failure produces `RECOVERY_REQUIRED` |
| CPU | At most 1 CPU-equivalent (1,000 millicpu) for the whole owned workload tree, expressed through an actually proved native hard cap |
| Memory / process count | At most 512 MiB committed memory across the workload tree; at most 4 owned workload processes including descendants |
| Disk/temp | At most 64 MiB of newly allocated writable data across **all** subject-writable roots: workspace outputs, TEMP, user profile/cache, redirected paths and descendants; alternate writable destinations must be denied or counted |
| Containers / build workers | Zero; this investigation does not launch containers or build workers as a fallback |
| Evidence | At most 32 MiB total protected evidence and 256 KiB per case output; overflow stops the case and marks evidence incomplete, never silently truncates a PASS |

Read-only fixture/dependency bytes are separately pinned; the restricted subject may not change
them. Protected evidence and VM checkpoints are outside the workload's 64 MiB only if that subject
cannot write them. Their separate capacity/preflight is mandatory. A free-space reading, dynamic
VHD maximum, command flag, application size check or periodic monitor is not a workload disk cap.
If all writable paths cannot be bounded, report `RESOURCE_ENFORCEMENT_UNAVAILABLE` and do not run
the dependent adversarial cases. Do not discover the limit by exhausting the guest/system disk.

The exact operational ticket must bind the concrete test executables, paths, native cap settings,
case expansion, identities and cleanup resources within these ceilings. Larger or longer work
requires a displayed amended plan and owner decision; an implementer cannot enlarge this table.
CLI startup that cannot fit a ceiling stays unavailable for that manifest, not silently exempt.

## 5. Attempt state and restart reconciliation

These are execution-attempt states, not a replacement workflow state machine:

```text
ABSENT -> CLAIMED -> LAUNCH_BOUND -> RETURN_RECORDED -> CLEANED
                      |                  |
                      +-> RECOVERY_REQUIRED <-+
CLAIMED -> RECOVERY_REQUIRED
```

`ABSENT` means the protected claim resolver proved no claim for this key; an empty transcript
does not establish it. Only the claiming invocation may proceed toward launch. Every state has a
monotonic recorded revision; unexpected transitions refuse. `LAUNCH_BOUND` requires a stable OS
identity tied to the exact attempt and isolation primitive, not a bare reusable PID.

A restarted observer never converts `CLAIMED` or a missing terminal record into a fresh launch.
It either reattaches to independently proved live owned work using one event wait, returns the
verified terminal result, or enters `RECOVERY_REQUIRED`. Crashes before/after native launch and
before/after return persistence must be separate cases; no exactly-once claim may be inferred
from a lock name or a filesystem existence check. Concurrent requests for the same key produce
at most one launch; unresolved native/ledger disagreement permits zero additional launches.

`CLEANED` is immutable final evidence that return and owned cleanup were observed. Replaying it
while a host UI still says Running returns the existing evidence and starts zero work. A failed
test may reach CLEANED; cleanup success does not turn its test result into PASS. Failed cleanup
blocks dependent execution and retains evidence until an owner-scoped recovery operation.

## 6. Closed per-host effect roster

Each host surface/version/binary digest/enrolled configuration has its own committed roster.
Every offered or otherwise model-reachable effect entry maps to one of `DENIED`, `BROKER_ONLY`
or `READ_ONLY`, with actual reachability and a repeatable oracle. Required categories are shell
and unified execution, interactive stdin/continuation, direct edits/patches, code-mode/nested
execution, MCP/apps/plugins, browser/computer use and client-control/configuration channels.
Nonexistent categories require evidence of absence for that exact surface, not an empty list
supplied by the Agent. New/unmapped/dynamically unobservable entries yield
`HOST_ROSTER_UNQUALIFIED`; configuration readback alone cannot close a contradictory tool roster.

Test through the host's real tool registration/dispatch path using a deterministic offline fixture
only if the exact host supports it. A mock broker, direct call to the hook, isolated request parser
or a session omitting the installed plugin is not installed-host mediation proof. Incompatible
offline execution yields UNAVAILABLE; external model requests and credential transfer remain
forbidden. CLI qualification never qualifies Desktop. No new Desktop bridge is built under this
investigation. Every claimed surface needs both a permitted positive effect and denied bypasses,
including disabled/crashed/timed-out advisory hooks.

## 7. Acceptance cells and adversarial evidence

The ticket expands each dimension below into unique named cells with exact fixture/oracle refs;
the reviewer checks the frozen expansion before execution. No case is generated ad hoc by a model.

| AC | Required result / negative evidence |
| --- | --- |
| CVQ-AC01 | Ordinary public constructor/round-trip accepts the full positive scope/manifest/report. Missing/extra fields, null in required fields, bool-as-int, illegal enum, duplicate IDs, zero/negative limits and incompatible tagged data reject. |
| CVQ-AC02 | Each of candidate, script/dependency bytes, argv, cwd, environment, run order/count/load, policy owner/revision, resource scope and evidence destination drift causes zero launches. A candidate cannot approve its own altered manifest. |
| CVQ-AC03 | Missing/stale/conflicting prerequisite refuses dependent native/host cells; pure contract checks remain admissible without a VM, CLI, runner, receipt or external provider. |
| CVQ-AC04 | Restricted subject cannot modify protected policy/broker/config/approval/evidence; authorized broker observation remains possible. Workload token is not the protection-owner token; admission-to-launch substitution fails. |
| CVQ-AC05 | Each required resource cap has a native primitive, race model, failure semantics, pre-launch evidence and bounded adversarial reproduction. All disk/temp destinations are counted or denied; unsupported caps refuse before hostile work. |
| CVQ-AC06 | Cancellation, total deadline and disposable owner/broker loss terminate only the exact owned tree within cleanup deadline; unrelated sentinel survives. Breakaway/indirect-child/handle escape paths are tested or explicitly unqualified. |
| CVQ-AC07 | Same-key barrier concurrency launches at most once. Completed evidence plus stale UI launches zero times. Claim/launch/return crash gaps and conflicting PID/evidence never authorize automatic redispatch. |
| CVQ-AC08 | Exact Codex and Claude surface rosters cover all reachable effects and fail closed on unknown paths; real offline host dispatch positive and bypass cases are required independently. Hook failure cannot be promoted to enforcement success. |
| CVQ-AC09 | Every expected cell appears exactly once with bound evidence. Missing/duplicate/forged/wrong-candidate output, empty collection, zero expected mutation reds, timeout, overflow or cleanup failure cannot produce QUALIFIED. Reviewer reads unreduced admitted output; incomplete output remains incomplete. |
| CVQ-AC10 | Q8 reuses the separately delivered WA-04 contract/adapter, if available: forbidden dependency, outside-root construction, undeclared responsibility and missing seam reject; mechanical file splitting stays red and a cohesive large fixture passes. Missing WA-04 returns UNAVAILABLE for that capability, never a new duplicate validator. |

For every acceptance predicate that cannot be proven by strict types, name a reviewer-run reverse
mutation that weakens that predicate, makes the corresponding cell red and returns green after
exact restoration. At least one reviewer mutation must enter a different guard/path than the
implementer's example. Pure-report tests prove the reporting gate only; native and installed-host
evidence are separate and cannot be fabricated by fake ports. The independent helper supplies
finite adversarial evidence; the current-session reviewer alone concludes the review.

## 8. Composition, data, security and operations

The short-lived composition injects `ApprovedManifestPort`, `PrerequisiteEvidencePort`,
`AttemptClaimPort`, `ImmutableSnapshotPort`, `ProtectedExecutionPort`, `CompletionWaitPort` and
`EvidenceObservationPort`. Pure admission/report assembly never spawns, reads ambient credentials,
writes active policy, invokes Git integration or modifies VM state. Fake ports support deterministic
source-only tests; qualification of their real counterparts is a different result. Source modules
separate contracts, admission, execution, recovery, host adapters and evidence responsibilities.

Data/pipeline/lifetime ownership follows the architecture map. No target runtime dependency on
Johnny, new provider, database deployment, telemetry pipeline or cache service is required by this
qualification SPEC. Durable recovery storage must prove the claim/settlement semantics above;
its backend is investigated, not silently chosen during product implementation.

`XSS_NOT_APPLICABLE` for this CLI/OS slice: no untrusted Browser/WebView/HTML/JavaScript sink is
introduced. Any new renderer or privileged bridge is an upstream change, not a ticket detail.
Exact lab VM: `7701b26b-5b5a-42c0-b1e1-36d34dfdaa46` / `Johnny-MSIX-Lab-20260905`. Before effects,
bind fresh guest/VM identity, admitted protected OS/module bootstrap, owned checkpoint and concrete
subject/evidence roots. The previous name-import diagnostic script is not a mutating executor.
No physical-host account/ACL/service/policy change, external networking/model call, real credential
capture, package install or VM restore/delete is authorized by approving the pure contract slice.

Recovery is fail-closed. Preserve failed attempts; no reset to manufacture a clean result.
Checkpoint creation/restore, guest account/ACL work, fixture/tool transfer and native execution
each need an exact operational ticket/authority. Inspection capability is not effect authority.
No guessed account/service name, approval receipt or gateway is created to avoid this boundary.

## 9. Proposed ticketing sequence — not opened or dispatched

1. **CVQ-01: qualification contracts and pure prerequisite/report admission.** One independently
   observable source-only slice: reject malformed/forged/incomplete qualification and permit exact
   pure cases while dependent OS/host cases remain unqualified. Proposed boundaries:
   `library/controlled_verification/qualification_contracts.py`,
   `library/controlled_verification/qualification_admission.py`,
   `library/controlled_verification/__init__.py`,
   `tests/test_verification_qualification_contracts.py`,
   `tests/test_verification_qualification_admission.py`. No subprocess, filesystem effect,
   broker implementation, VM access, production integration or central Router enlargement.
2. **CVQ-02: exact lab recovery/bootstrap operation.** Freeze a reviewed protected recipe, guest
   entry and owned checkpoint; read back actual identities before any new account/ACL/fixture.
   No reuse of the historical provisioning ticket as a new effect grant.
3. **CVQ-03: Windows primitive investigation.** Bind a finite subset of native identity/immutable
   launch/resource/cleanup/claim cases. Return native proofs or explicit unsupported semantics;
   required missing containment prevents dependent hostile execution.
4. **CVQ-04: host mediation and composed capability report.** Independent exact-surface rosters and
   offline evidence; unavailable surfaces stay unavailable. Q8 consumes WA-04 evidence only after
   its separately approved delivery. No release or replacement source validator.

CVQ-01's exact closure/model/profile and normal constructor/type preflight belong in its future
ticket after approval, not an implementation prompt. Standard implementation uses the registered
`implementation-standard`, review `ticket-review`; elevation follows the existing assessment rule,
not this document's profile name. Same-lifetime dispatch uses the existing owner lane and event wait.

## 10. Approval and continuation

No approval signature exists. Owner D1/D2/D3 approve the direction, not this newly authored exact
SPEC. [Grill](../../doc/context/controlled-verification/grill-r01.md) must be completed with the
owner, then shared Context sealed and the exact SPEC approved before ticket creation. The first
proposed approval is limited to CVQ-01 ticket preparation; VM operations, other tickets, native
effects and installation/release remain outside it. Never report an unopened ticket as dispatched.
