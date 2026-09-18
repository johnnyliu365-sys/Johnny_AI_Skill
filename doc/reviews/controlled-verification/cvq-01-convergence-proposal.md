# CVQ-01 — schema preflight convergence proposal

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01-CONVERGENCE` / `CODE_REVIEW` / `01` |
| Lifecycle / conclusion | `OWNER_DECISION_REQUIRED / PROPOSAL_ONLY / NON_DISPATCHABLE` |
| Control baseline | `89d91e68f00ef509537a57b85a32b450e6cca81b` |
| Examined source | `9796790d33b6d1374469fad1b37e1f4991262a43`; initial `cd228a790b2f37bc2cad109978f8822ad5bb2da6` preserved |
| Ticket | [CVQ-01](../../../modules/tickets/controlled-verification/cvq-01-qualification-admission.md), document 04, LF `1ab65b3a70b7bedd43eb017943adbe7bf89509dd18aeb8c3c2d6bcb7876de872`; closure 02 unchanged |
| Contract | [Qualification SPEC](../../../modules/spec/controlled-verification-qualification.md), revision 04, LF `4cad6a88b9d151a05bf409f8b61bc97580e80303f58a2377cb0301815b999a1d` |
| Evidence | [Schema preflight](cvq-01-schema-preflight.md), revision 02, LF `28d8dbd7f3836ac3088829385cf45a0e816e5e27014d28aa8fdbdde27b30eb06` |
| Responsibility | Parent owns this conclusion. Reused Terra/xhigh helper supplied read-only symbol/fixture/AST inventory; no implementation, test execution or approval was delegated in this convergence action |

## 1. Diagnosis and retained boundary

The owner-approved two-phase exception was exercised, not ignored: schema construction first,
then actual reviewer preflight before behavior. Initial and one correction both failed that
preflight. Revision 02 evidence preserves real strict-type/test runs, malformed-JSON masking,
duplicate-report acceptance, zero-red guard removals and exact restoration. Repeating those
unchanged commands or renaming another correction would not resolve the control defect.

There are both implementation defects and underspecified control predicates. The implementation
omits already-required observer/roster evidence and exhaustive discriminating tests. The frozen
text also leaves two design decisions implicit: what closed static surface CQ11 admits, and
the applicability of host/native evidence. The parent must settle those before another dispatch;
the failure is not evidence that a stronger implementation model alone would fix the contract.

The approved architecture and sealed shared Context were reread. No changes to D1/D2/D3,
Python 3.11, three injected read-only ports, pure/native proof separation or repository authority
are proposed. No native capability, full dispatch, installation or release is claimed delivered.
The goal remains complete dispatch first, then one-click installation/removal; existing Git
rollback refs and unintegrated source candidates remain intact.

## 2. Two owner decisions — recommendations, not enacted rules

### D-CQ11: closed permitted surface for this pure package

Recommend a package-scoped positive import/call policy instead of an open-ended effect denylist.
This is the finite CQ11 predicate, not a new general-purpose analyzer or runtime sandbox.

- External imports for the schema slice: `__future__.annotations`; `enum.Enum`;
  `typing.Annotated`, `Literal`, `Mapping`, `Protocol`, `TypeAlias`, `Union`;
  `pydantic.BaseModel`, `ConfigDict`, `Field`, `StringConstraints`, `Discriminator`, `Tag`,
  `model_validator`. Every other external import rejects unless a reviewed policy revision adds it.
- Internal imports resolve to the ticket's constituent DAG, regardless of relative/absolute
  spelling, package-form import, aliases or function/class nesting. Wildcards reject. Reject
  cycles and imports through a facade that reach forbidden constituents.
- The call inventory is a separate finite symbol table: explicitly admitted pure builtins,
  approved constructors/decorators, locally declared pure helpers and approved value operations.
  Alias resolution must preserve the original symbol; unresolved dynamic calls or alias rebinding
  reject. The exact call table must be frozen in the next control revision before implementation;
  the implementer may not extend it merely to make the current code pass.
- Existing exclusions remain: `Any`, casts, Pydantic bypass construction/copy-update, dynamic
  import, `eval`/`exec`, reflective `getattr`/`setattr`, ambient mutable services and effect APIs.
  Match qualified and aliased forms throughout the AST, including unused renamed helpers.
- Facades permit only docstrings, future imports, explicit re-exports and a literal immutable
  `__all__`; not functions, classes, validators or initialization calls.

Tradeoff: adding a legitimate dependency needs a small explicit policy amendment. This is
preferable to claiming that seven forbidden module names cover all filesystem/network/process
effects. It does not claim to confine hostile arbitrary Python or replace protected execution.

### D-CLAIM: explicit evidence applicability, not nullable inference

Recommend an approved, tagged claim scope with the following finite applicability table. Exact
DTO names/fields and new tag vocabulary must be transcribed into the next SPEC/closure revision;
these proposed meanings are not current implementation authority.

| Actual case | Claim scope / required evidence |
| --- | --- |
| PURE_RULE or SOURCE_PROPERTY | Pure-rule claim only, even when its subject is a native or host rule; no native capability assertion |
| TRUSTED_NATIVE_DISCOVERY of a non-host primitive | Native-probe scope; no host roster and no prerequisite requiring its own completed probe |
| TRUSTED_NATIVE_DISCOVERY for HOST_MEDIATION | Exact host discovery scope; approved expected roster plus actual discovered set, not an enforcement verdict |
| ADVERSARIAL_WORKLOAD | Native-property scope; measured native behavior and bounded launch/cleanup evidence |
| REAL_HOST_PROPERTY | Exact host-property scope; independently accepted discovery prerequisite and later actual entry observations |

`CapabilityKey` identifies its subject separately: HOST_MEDIATION requires a host-scoped key;
other families may use an explicitly approved host-scoped or platform-scoped key. A host-scoped
key carries exactly one HostSurface; a platform-only key carries none. No empty/null stand-in and
no CLI/Desktop aliasing. Pure-rule results may describe a host-scoped rule but cannot prove that
host's enforcement.

For native claims, distinguish a measured primitive record (primitive, race-model and failure-
semantics refs all required) from an unsupported/unavailable probe record (finite reason and
probe evidence, no invented working primitive). A not-run record has only its real plan/event
evidence. Pure claims carry no native-proof payload. FAILED measured observations retain their
primitive evidence; UNAVAILABLE or NOT_RUN must not be upgraded to PROVEN. This replaces
"where applicable" with an executable tag predicate without requiring fake positive evidence.

## 3. Connected data graph — proposed transport placement

The three existing ports remain the only external data seams. Ordinary validation is shape
evidence, never authenticity. Proposed transport placement below closes S7/S8; the exact public
wire inventory must be frozen after the owner decisions, before a new schema dispatch.

| Owner / seam | Typed data made reachable | Time and authority rule |
| --- | --- | --- |
| Independently composed ApprovedManifestPort FOUND | Exact approved manifest and referenced approved roster snapshot bodies: key, roster ref/digest, finite PRESENT/ABSENT category closures | Read independently of caller JSON. Manifest identifies expected subjects/checks/prerequisite pins, not future execution identities |
| QualificationCase subject | Tagged no-roster, host-discovery subject or host-property subject; host subjects bind the exact roster key and approved roster ref/digest | Native primitive discovery is not automatically a host discovery case. Host discovery must not require its own future discovery-coverage ref |
| PrerequisiteEvidencePort FOUND | Existing exact prerequisite binding, including approved observation revision/evidence digest | HOST_ROSTER_DISCOVERY names a completed discovery result for a later host-property case; never an enforcement result |
| EvidenceObservationPort FOUND | Authenticated typed evidence subjects and their necessary observed payloads: discovery set/coverage or enforcement coverage as appropriate | Protected adapter resolves actual data; caller-supplied ref/digest/comparison is not self-authentication. MISSING/CONFLICTING retain real rejection evidence |
| Executed case observation | Observer identity plus exact check/evidence bindings; native launch identity only after launch | Add the missing observer for both pure and native execution; launch observer is not a substitute for pure execution observer |
| Report admission | Exact expected case/check coverage plus independently resolved roster bodies/observations | Compare actual sets and keys; never accept a comparison enum alone. Discovery completeness and enforcement remain separate predicates |

The evidence-subject union needs separate finite alternatives for case, check, cleanup,
prerequisite binding, roster absence, discovered set, discovery coverage and present-entry
enforcement. An ABSENT subject binds roster key/category/discovery surface; it must not require
dispatch-entry ID or enforcement oracle. An enforcement subject binds its actual entry and oracle.
Each returned subject, ref, digest and observer is compared to the requested approved binding.
No fourth port, ambient dictionary/service locator, deferred untyped JSON or additional authority
store is introduced. Capability observations must also be reachable at their owning report/evidence
seam; an exported but disconnected DTO is not a completed contract.

The current nullable `host_roster_subject` additionally imposes a roster on *all*
TRUSTED_NATIVE_DISCOVERY cases (`manifest_contracts.py`, candidate lines 90–100). That is not
the SPEC's distinction between primitive discovery and host discovery. This is recorded now,
not silently added as a later surprise finding or implementation instruction.

## 4. Concrete coverage inventory and finite test work

This is the inspected candidate inventory, **not** a frozen count for the amended design. Internal
base classes and the three Protocol classes are not DTO rows. Facades own no independent DTOs.

| Constituent | Public concrete DTOs at `9796790` |
| --- | --- |
| values (1) | CapabilityKey |
| bindings (3) | PureContractBinding, NativePreLaunchBinding, LaunchObservation |
| prerequisites (7) | PrerequisiteKey, PrerequisiteRequirement, PrerequisiteEvidenceBinding, FoundPrerequisite, MissingPrerequisite, ConflictingPrerequisite, QualificationPrerequisiteSet |
| roster (9) | HostEffectRosterKey, HostRosterSubject, HostEffectEntry, PresentHostCategoryCoverage, AbsentHostCategoryCoverage, DiscoveredEffectSet, HostRosterDiscoveryCoverage, HostEffectObservation, HostRosterEnforcementCoverage |
| manifest (6) | QualificationScope, ResourceBounds, CleanupBounds, EvidenceBounds, QualificationCase, QualificationManifest |
| report (16) | CheckObservation, CompleteExecutionObservation, IncompleteExecutionObservation, CapabilityObservation, ExecutedPureCaseResult, ExecutedNativeConfirmedCaseResult, ExecutedNativeRecoveryCaseResult, RefusedPrerequisiteCaseResult, RefusedOtherCaseResult, RefusedRecoveryCaseResult, UnavailableCaseResult, NotRunCaseResult, QualificationReport, ManifestRefusedEvaluation, ReportRejectedEvaluation, ReportAcceptedEvaluation |
| ports (11) | ApprovedManifestFound, ApprovedManifestMissing, ApprovedManifestConflicting, CaseEvidenceSubject, CheckEvidenceSubject, CleanupEvidenceSubject, RosterEvidenceSubject, EvidenceObservationRequest, AuthenticatedEvidence, MissingEvidence, ConflictingEvidence |

The parent verified the named source declarations:
1 + 3 + 7 + 9 + 6 + 16 + 11 = **53 concrete public DTOs**. The enumerated names, not an estimated
module subtotal, are the expected inventory. There are also 7 constrained scalar aliases, 3 ports and 9 tagged
aliases with **30 total branches**:
AttemptBinding 2; PrerequisiteResolution 3; HostCategoryCoverage 2; ExecutionObservation 2;
CaseResult 8; QualificationEvaluation 3; ApprovedManifestResolution 3; EvidenceSubject 4;
EvidenceResolution 3.

The 30 enum types contain 119 named values at this candidate. Each enum value needs its own
enum-constructor/TypeAdapter round-trip row. **Do not demand an illegal DTO field placement just
to cover an enum:** public Admission and broad Refusal vocabulary do not all occur as accepted
values in current DTO fields. Test finite field-specific subsets and their rejections separately.

| Catalog section | Fixed evidence required before dispatch |
| --- | --- |
| Public DTO rows | Explicit public constructor, exact valid inputs/wire expectation and owning module for every target DTO; no bypass construction |
| Tagged alias rows | One ordinary TypeAdapter JSON round-trip per branch; direct DTO construction alone cannot prove union discrimination |
| Enum rows | Literal expected enum names/values, every value's round-trip; affected DTO subset positives and illegal-value negatives |
| Required-field rows | Hand-authored required-field list per public fixture; one omission and one JSON-null cell per required field, plus one extra-field cell per DTO |
| Other wire fields | Explicit default/optional behavior if allowed, including discriminator omission rules. Nullability is never inferred from what the implementation currently accepts |
| Domain rows | Distinct strict integer, positive, nonnegative, zero-only, opaque-ID, digest, duplicate, tag/binding and cleanup cells required by CQ02 |
| AST controls | Relative, absolute and package-form forbidden imports; aliases; nested/renamed helpers; indirect facade reachability; dynamic/bypass calls; facade logic and ambient mutable state |

For the current inventory there would be 53 direct DTO and 30 alias-branch positive rows, plus
119 enum rows. The required-field negative count is `2 × sum(explicit required fields) + DTO count`.
Do not declare that count complete until the amended public field inventory is frozen. Reflection
may produce the **observed** inventory for comparison, but may not generate its own expected
list from `model_fields`, schema or the same validators being tested. Compare identities as well
as counts. Changes to fields/variants cannot silently reduce coverage.

Negative fixtures start from valid JSON decoded structurally, remove/change exactly one field,
then serialize valid JSON. Assert the intended error location/type; `json_invalid` is not a
required-field rejection. Restore the positive/zero-only mutation cells removed in the correction
and test duplicate report IDs. These are finite table-driven checks, not one bespoke script per
fixture. Keep fixtures/data, contract assertions and AST policy in their existing separate owners;
no giant mixed test runner or new background process.

## 5. Decomposition and continuation

Do not split this shared contract into concurrent type-owner lanes, and do not disguise a third
correction as a new implementation ticket. The current phase has one coherent public-contract
boundary but an incomplete control inventory. Recommended sequence:

1. Owner decides D-CQ11 and D-CLAIM. This document is a proposal, not a completed owner Grill.
2. Parent transcribes those choices into a proposed SPEC amendment and closure revision 03,
   with exact public wire/required-field catalog, final counts, positive call policy and typed
   port-result graph. Preserve closure 02 and both candidates as historical evidence.
3. Obtain exact owner approval for that changed closure. The existing two-phase approval is not
   a blanket approval for new semantics or a third loop. Only then reassess low-model admission
   and dispatch a new bounded schema phase to the same Luna/xhigh owner, if admissible.
4. Parent reviews actual constructors, strict types and finite matrix; independent reverse
   mutations must fail the intended cells. Zero red is a finding. Behavior remains NOT_ADMITTED
   until all schema preflight requirements pass; no dummy reference or mocked capability can
   replace native evidence. Preserve the finite command/resource budget; no stress repetition.
5. Behavior stays separated into the already-owned prerequisite, roster, report and composition
   units. Each behavior slice needs its own observable test closure against the frozen contracts;
   integration/release and native/host qualification remain separate later authority boundaries.

This control action edits documentation only. No source candidate, main branch, sealed Context,
approved SPEC, host/provider/VM, publication or remote ref is changed. Return `ACTION_COMPLETED`
for the convergence proposal, then `WAIT_FOR_HUMAN` for the two named design decisions.
