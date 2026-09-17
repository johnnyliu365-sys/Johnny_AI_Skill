# Machine-validated Agent dispatch and return — contract draft

| Field | Value |
| --- | --- |
| Specification ID / revision | `SPEC-CONTROLLED-VERIFICATION-DISPATCH-20260918-01` / `03` |
| Lifecycle | `DRAFT / CONTRACT_CONVERGENCE / NON_DISPATCHABLE` |
| Author / branch / baseline | Current-session reviewer; `codex/controlled-verification-intake`; revision-03 baseline `db6bd375f52389a7f428918e68a16e331bfa0d66` |
| Lineage | [REQ-051](../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 08 D4/D7; `PRD-20260908-051 / CHG-20260908-051` |
| Control / ticket | [CVE-00](../tickets/controlled-verification/cve-00-contract-convergence.md), [CVE-01](../tickets/controlled-verification/cve-01-compact-dispatch-admission.md) |
| Existing Context / qualification | [Context revision 02](../../doc/context/controlled-verification/main.md) is reference-only and sealed; [qualification SPEC](controlled-verification-qualification.md) is unchanged and does not approve this protocol |
| Proposed language / risk | Python 3.11, strict immutable boundary DTOs, `mypy --strict`; POC / HIGH_ASSURANCE for authority and untrusted-input boundaries. No UI rendering: XSS_NOT_APPLICABLE for this slice |

## 1. Scope and claim boundary

The session generates a data packet from an independently approved current ticket contract.
A program admits it before delivery; a program admits the child's structured report before
projecting a Router return. Models do not decide schema validity, authority, whether checks ran,
or whether changed paths stayed in scope. The single reviewer still judges semantics and review.

This draft defines the focused protocol boundary, not a full product executor, a CI platform,
new Router or a provider client. Other CVE cuts retain their own responsibilities. Nothing here
is implemented, qualified or owner-approved as a SPEC yet. The owner approved P1 A and the D7
requirement; that is not approval of unseen schema details or installed-host enforcement.

## 2. Wire format and strict parsing

YAML is external data only. The proposal permits one UTF-8 mapping document using mappings,
sequences and explicitly typed scalar values; no arbitrary object construction, custom tags,
anchors, aliases, merge keys, duplicate keys, extra keys, implicit type coercion or multiple documents.
Quoted text that resembles a number remains text and fails an integer field; bool is not integer.
Reject unknown schema versions and malformed IDs. The concrete revision-02 engineering proposal
below freezes parsing policy and bounds; package/adapter qualification remains required, not assumed.

Parse into immutable named DTOs before any effect. Preserve exact identifier/path code points;
reject rather than silently trim, lowercase or normalize authority identity. A separate explicit
identity resolver maps external IDs to existing internal opaque IDs. Structured content and
human-readable findings are data, never additional executable instructions. The controller may
render human explanations separately; Agent-to-Agent control messages remain schema-defined.

### 2.1 Proposed parser contract and finite limits

Use the pure-Python event parser of `PyYAML==6.0.3`, explicitly selecting `BaseLoader`,
with a bounded event consumer; do not use its object constructors or implicit scalar resolver.
This is a dependency proposal, not permission to install it or alter the runtime lock. The
package publishes this version and Python compatibility in its [release metadata](https://pypi.org/project/PyYAML/6.0.3/).
Its [event API](https://raw.githubusercontent.com/yaml/pyyaml/6.0.3/lib/yaml/events.py)
exposes scalar style, anchors, tags and document boundaries for rejection before DTO conversion.

`safe_load` alone is insufficient: the upstream [mapping constructor](https://raw.githubusercontent.com/yaml/pyyaml/6.0.3/lib/yaml/constructor.py)
assigns by key, and its safe constructor also supports merges and implicit scalar conversions.
The proposed boundary therefore detects duplicates before mapping insertion and never dispatches
from the resulting unvalidated dynamic object.

| Limit / lexical rule | Revision-02 proposal |
| --- | --- |
| Raw input | At most 65,536 bytes; strict UTF-8; no BOM, NUL or unpaired surrogate |
| Structure | One mapping document; maximum container depth 16 (root = 1); 4,096 value nodes including keys; 256 members per collection |
| Scalars | At most 4,096 UTF-8 bytes after decoding; stricter field-specific bounds below also apply |
| Keys | ASCII schema field names only; exact duplicates, unknown keys and `<<` refuse; keys cannot be collections |
| YAML features | Reject anchors, aliases, any explicit tag, directives, extra documents and block scalar styles; ordinary block/flow mappings and sequences remain allowed |
| Scalars to DTOs | Quoted scalars are strings. Plain `true`, `false`, `null` and JSON decimal integer grammar are typed tokens; other plain scalars are strings. Field validation never converts a string into a number or Boolean |
| Numbers | No float fields; integer values within 0..2,147,483,647 before tighter field limits; Boolean is never integer |

Limits reject rather than truncate. Input bytes are bounded before parser construction; depth,
node and collection limits are enforced while consuming events, not after recursive object
construction. These logical limits do not prove a hard CPU/memory deadline for a parser call;
that stronger claim belongs to separately qualified execution containment. Runtime packaging
must pin actual distribution artifacts and type stubs through the owning dependency workflow.

### 2.2 Canonical digest without self-reference

The wire packet carries its logical `dispatch_digest` or `report_digest`, not the digest of its
own raw bytes. Independently observed `raw_sha256` belongs to the transport/evidence record
outside that packet. Never serialize a raw-body digest into the very body it describes.

Proposed `CVE-CJSON-1` uses the validated schema's primitive projection and Python 3.11
`json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)`.
Object keys are ASCII, arrays retain order, enums project their exact wire value, and only
schema-declared integers/Booleans/null/strings are present. No floats, sets, Unicode normalization,
trimming or alias fields. Encode the result as ASCII bytes without BOM/newline. Omit only the
top-level self-digest field; all other required fields remain. Hash the bytes prefixed by
`johnny.cve.dispatch.v1` followed by one NUL byte, or `johnny.cve.report.v1` followed by one NUL
byte, with SHA-256 and lowercase hex output. This is a specified narrow serialization, not a
claim to implement RFC 8785. Cross-host consumers must use the same qualified codec/test vectors.

LF-normalized artifact digests retain their existing meaning and are never substituted for
the raw-byte observation or this logical packet digest. None of these digests proves authority.

## 3. Dispatch contract proposal

Every row is required unless a tagged variant explicitly says otherwise. Exact DTO definitions
will close constituent types and bounds before approval; this table is not executable JSON Schema.

| Field / named boundary | Required meaning |
| --- | --- |
| `schema_version`, `dispatch_id`, `dispatch_digest` | Versioned schema, unique lifecycle identity, digest of the canonical validated packet excluding its own digest field; bind original source blob digest separately |
| `ticket`, `stage` | Exact external ticket ID; this variant's stage is IMPLEMENT only, not an arbitrary task message |
| `authority` | Exact spec ID/revision/digest, ticket revision/digest, closure revision/slice, approved artifact commit, full baseline Git object ID and repository identity |
| `owner` | Implementation/reviewer identities, role separation, assigned lane, exact worktree/branch binding and admitted semantic model-profile revision; model name alone grants nothing |
| `scope.allowlist` | Approved path grants with explicit CREATE/MODIFY/DELETE/RENAME permissions; default deny; mode/type/submodule changes are unsupported and refuse |
| `scope.forbidden_paths`, `scope.forbidden_invariants` | Distinct path selectors and registered invariant predicate IDs; explicit prohibition prevails, unknown predicate refuses |
| `work` | Unique item IDs and exact approved refs, matching the complete current slice; no new task meaning from free text |
| `preserve`, `acceptance` | Exact required invariant/closed-finding/AC refs; complete coverage may be many-to-many but cannot omit requirements |
| `checks` | Unique check and execution-slot IDs plus approved execution-plan refs; resolve executable/argv, snapshot, dependencies, environment, order/load/count/retry/deadlines independently |
| `return_schema` | A fixed registered schema ID/revision/digest; it resolves the closed status variants and required fields, never a caller-defined validator or a second wire field list |

The owner's command strings are presentation of registered checks, not text passed to a shell.
The admission resolves the actual executable/argv from the approved plan; display drift rejects.
`authentication_changes` resolves a registered semantic invariant, not a glob. An invariant with
no qualified executable predicate is unproven and cannot be marked enforced by an AI assertion.

Path comparison uses the actual bound repository/filesystem semantics, not string-prefix tests.
Traversal, absolute/drive/UNC paths, ambiguous separator/case aliases and reparse/symlink escape
must not widen grants. Freeze the supported path-pattern grammar and operation types before
approval; arbitrary regex/glob language is not accepted by implication. Rename checks both paths.

### 3.1 Constituent types proposed for the first pure cut

All DTOs are immutable, reject extra fields, and disable string trimming/coercion. Do not inherit
the existing `RouterModel` unchanged: its `str_strip_whitespace=True` would silently change wire
identity. Dynamic parser values terminate at the codec; named types cross the application ports.

| Type | Closed proposal |
| --- | --- |
| `ExternalId` / `ItemId` | Exact string matching `[A-Za-z][A-Za-z0-9_.-]{0,127}`; `CV1` is legal and is not lowercased into an internal ID |
| `InternalId` | Existing registered opaque ID grammar `[a-z][a-z0-9-]{2,127}`; explicit registry mapping from external IDs |
| `Digest` / `GitObjectId` | 64 lowercase hex SHA-256; Git ID is `{algorithm: SHA1 or SHA256, hex: exact 40 or 64 lowercase hex}` and must match the repository format |
| `ArtifactBinding` | `{id: ExternalId, revision: positive integer, lf_sha256: Digest}`; revision display padding is not wire identity |
| `ItemReference` | `{artifact: ArtifactBinding, item: ItemId}`; resolution is independent of free text or a guessed anchor |
| `RelativePath` | Exact 1..1,024 UTF-8 bytes; forward-slash separated nonempty segments; no absolute/drive/UNC form, backslash, NUL, `.` or `..` segment |
| `PathSelector` | Tagged `EXACT{path: RelativePath}` or `TREE{prefix: RelativePath}`; TREE matches whole segments below its prefix, never a string-prefix sibling; no arbitrary wildcard/regex interpreter |
| `PathGrant` | `{selector: PathSelector, operations: unique ordered tuple of CREATE, MODIFY, DELETE, RENAME}`; both rename endpoints require grants. Mode/type/submodule changes refuse in this first revision |
| `WorkItem` / `PredicateRef` | `{id: ItemId, ref: ItemReference}`; unique IDs within each collection; exact approved slice coverage, not an Agent-written interpretation |
| `CheckSlot` | `{check_id: ItemId, slot_id: ItemId, plan: ArtifactBinding}`; pair unique; executable/argv and repetition parameters resolved from the plan |
| `OwnerBinding` | `{implementation: InternalId, reviewer: InternalId, lane: InternalId, worktree: Digest, branch: Digest, profile: ArtifactBinding}`; distinct roles; fingerprints are actual independently computed bindings |
| `ScopeBinding` | Allowlist 1..256 grants; forbidden selectors/invariant IDs 0..256 each; explicit prohibition wins; unknown invariant rejects |

Wire strings such as `sql/**` may be human renderings of a registered TREE selector but are not
executed as a second glob language. Platform-specific reserved names, case collisions, filesystem
identity and link/reparse escape require the Git/filesystem adapter's separate qualification;
the lexical type cannot declare those checks passed. Exact approved schema IDs fix the remaining
root shape from section 3; a wire sender cannot supply its own required-field list.

## 4. Program-before-delivery boundary

1. Parse/validate the closed schema and resolve independent approval records; syntax is not authority.
2. Compare exact ticket/SPEC/closure/baseline/repository/owner/profile/worktree with the approved
   current lane, including source revision invalidation. Resolve actual baseline identity and
   clean lane state; a caller's assertions are not readback.
3. Check complete Work/Preserve/Acceptance/Check coverage, operation/path grants and invariants.
4. Resolve required execution/budget capabilities, then claim the existing dispatch identity
   atomically before delivery. Identical replay retrieves status; changed replay refuses.
5. Only the trusted composition passes the admitted immutable packet to the host effect adapter.
   It revalidates admission freshness at the effect boundary. A writable packet checked then
   reread later is insufficient. All rejected paths make zero child-dispatch calls.

No Boolean `validated: true` from a caller, guessed descriptor or free-form follow-up can open
another path. Interrupted/uncertain delivery is reconciled against actual lane evidence; absence
of a transcript never authorizes another launch. Reuse existing lifecycle/qualification work.
Source-only fake ports prove pure decisions, not actual host dispatch, race exclusion or confinement.

## 5. Structured implementation report and independent validation

All report variants bind `schema_version`, `dispatch: {id, digest}`, `ticket`, ticket and
SPEC revisions/digests, full `baseline`, owner/lane and report identity/digest to the admitted input.
Section 10.1 is the exact root shape; separate top-level dispatch_id/dispatch_digest aliases refuse.
The example omitted several bindings; they must be supplied by the real protocol, not guessed.
Canonical fields are `changed_files` and `scope_deviations`; reject `files`/`deviations` aliases or
both spellings. Their arrays may be empty, never omitted. Findings are bounded structured entries
with rule/item/evidence refs and an optional bounded explanation; no secrets or executable prose.

| Wire variant | Candidate / work / checks |
| --- | --- |
| `IMPLEMENTED` | Required full candidate commit ID; exact dispatched work IDs all DONE; each required check/slot carries its actual execution-evidence ref, not merely PASS |
| `BLOCKED` | Explicit tagged `NO_CANDIDATE` or `COMMIT` binding, named blocker and observed partial work/check statuses; no invented candidate or successful unrun checks |
| `CHANGE_DETECTED` | Same explicit candidate alternative, named changed-contract refs and actual partial observations; never mutate approved scope to make the return pass |

`changed_files` describes committed candidate changes only. NO_CANDIDATE requires that list to
be empty; bounded partial-work evidence may describe uncommitted work but cannot replace a
candidate, grant completion or be mistaken for an empty clean working tree.

The implementation report is an assertion until independently admitted:

- When a candidate is present, resolve it as a commit in the bound repository and assigned candidate lane, check
  baseline ancestry and frozen branch/snapshot identity; an existing unrelated commit is insufficient.
- Compute the actual baseline-to-candidate change set from Git; compare exactly to reported changes
  and evaluate grants for additions, modifications, removals, both rename paths, mode/type changes
  and reject mode/type/submodule operations. No supported submodule operation exists in this revision.
- Verify required invariants and candidate-bound check evidence through the shared CVE-02 evidence
  contract. Manifest/producer/environment/toolchain/attempt/role must match. Missing/unrun/stale/
  forged/cancelled evidence and unexpected failures never satisfy an obligation through YAML PASS
  or exit zero alone. A required first-red/reverse-red slot preserves its actual FAILED result;
  only its independently matched failure-causality oracle can satisfy that negative obligation.
- Require exact work/check ID coverage; an extra "regression: PASS" not present in the admitted plan
  is not authority. Keep partial/failing observations as non-success evidence; never fabricate green.
- Bind settlement to report identity/digest. Identical repeat cannot settle/route twice; altered
  repeat conflicts. Nonempty findings stay visible for reviewer disposition. Scope deviations cannot
  count as a successfully admitted implementation, regardless of the status word supplied.

NO_CANDIDATE reports skip commit/diff validation only for that absent candidate; they can return
BLOCKED/CHANGE_DETECTED, never an implemented success. Actual worktree safety observations remain
separate and mandatory wherever their approved predicate applies.

Accepted IMPLEMENTED maps to existing `ImplementationReturnStatus.COMPLETED` and a metadata-only
return, never APPROVED/merged/released. BLOCKED maps to BLOCKED; CHANGE_DETECTED maps to
CHANGE_DETECTED with REQUIREMENT_CHANGED. Malformed reports return a named admission rejection,
not a fabricated successful implementation return. Current reviewer and integration gates remain.

### 5.1 Report constituent and event proposal

`CandidateBinding` is `NO_CANDIDATE{kind}` or `COMMIT{kind, commit: GitObjectId}`.
`GitChange` has operation and nullable old/new `RelativePath`: CREATE requires only new; DELETE
only old; MODIFY requires both equal; RENAME requires both distinct. The actual Git adapter
must use the same frozen rename-detection policy for reported/observed comparison. Until that
policy is qualified, an ambiguous rename cannot be silently relabelled to obtain admission.

`WorkObservation` binds `id: ItemId`, `state: DONE|PARTIAL|NOT_STARTED` and nullable evidence ID.
`CheckObservation` binds check/slot IDs, `state: PASSED|FAILED|UNRUN|UNKNOWN|CANCELLED` and nullable
execution-evidence ID. DONE and any claimed executed check require independently accepted evidence;
PASSED/FAILED describe the check's actual outcome, not satisfaction of the slot's expected oracle.
Expected-red satisfaction never relabels FAILED as PASSED. UNRUN is explicit,
not an omitted slot. Findings, blockers and deviations are records with a registered code,
an `ItemReference`, 1..64 evidence IDs and a 0..4,096-byte explanation. These records are data,
never commands. Collections have the section-2 limit and exact dispatched ID coverage, including
unstarted work. BLOCKED requires at least one blocker; CHANGE_DETECTED requires at least one
changed `ArtifactBinding`. Candidate absence never forces a fictional commit or clean-tree claim.

Proposed event mapping is IMPLEMENTED -> COMPLETED/ACTION_COMPLETED,
BLOCKED -> BLOCKED/IMPLEMENTATION_RETURNED, and
CHANGE_DETECTED -> CHANGE_DETECTED/REQUIREMENT_CHANGED. Do not force REQUIREMENT_CHANGED through
`ImplementationReturnEvent`: that existing wrapper only admits ordinary return-event kinds.
Use the Router's existing change-event route. No new event vocabulary or retry authority is added.

## 6. Responsibility, reuse and data lifetime

Selected inventory: `workflow-router-poc` at the baseline above, from its delivered catalog card
and [public API](../../library/workflow_router/__init__.py). Scoped source inspection found:

- [ImplementationHandoff / ImplementationReturn](../../library/workflow_router/contracts.py)
  already separate roles and constrain return events. Internal opaque IDs are lower-case bounded
  IDs; external TICKET-008 must resolve through a registered mapping, not be blindly lowercased.
- [ApprovedDispatchArtifactRegistry](../../library/workflow_router/policy_response.py) matches
  reviewed artifact identities/commits but does not itself validate this YAML or actual Git diffs.
- [ImplementationReturnEvent](../../library/workflow_router/guarded_integration.py) carries
  owner/lane/baseline metadata and an optional receipt; it is not complete execution provenance.
- [CodexThreadDispatchRequest](../../library/workflow_router/thread_dispatch_contracts.py)
  is explicitly receipt-bound. Reuse relevant concepts, not that receipt prerequisite for a
  same-lifetime lane. No new receipt issuer, queue, runner or cross-lifetime bridge is needed.

Proposed boundaries: strict wire codec; pure ticket/scope/return admission; independent authority,
Git-diff and execution-evidence resolver ports; existing lifecycle/claim adapter; host delivery
adapter; metadata-only Router projection. Short-lived controller composition injects these.
No pure validator imports Git/subprocess/host effect code or appends everything to central Router
contracts.py. Tests keep codecs, domain predicates, port fakes and integration fixtures separate.

The source-cut proposal groups the new work under `library/workflow_router/controlled_dispatch/`:
`scalars.py` owns identity/lexical values; `dispatch_contracts.py` owns dispatch DTOs;
`report_contracts.py` owns report variants; `codec.py` owns bounded YAML decoding;
`canonical.py` owns deterministic bytes/digests; `ports.py` owns typed observations/protocols;
`dispatch_admission.py` and `report_admission.py` own their separate pure predicates;
`scope.py` owns selector/operation comparison; `projection.py` owns metadata-only return mapping.
These are proposed paths, not created files or an implementation allowlist. No validator imports
subprocess, Git or host APIs. Claim/delivery composition and production adapters are later cuts,
not silently bundled into this pure ticket. Tests mirror these responsibilities rather than
building a single giant adversarial harness.

Target-owned ticket/dispatch/report artifacts remain versioned with digest indexes. Raw YAML,
relative paths, code/work descriptions and detailed evidence stay outside durable Router state;
only bound IDs/digests/statuses are projected. Protected evidence follows its owning lifecycle;
unknown/failed attempts are retained. No target runtime dependency on the plugin is introduced.

## 7. Finite acceptance cuts

| Cell | Required negative / positive proof |
| --- | --- |
| MP-1 | Valid ordinary constructors round-trip; duplicate keys/coercions/unknown schema/enums/unsafe YAML/over-limit input refuse before effects |
| MP-2 | Each stale source/owner/revision/baseline/scope/work/check/profile mismatch refuses; exact approved mapping admits |
| MP-3 | Same-input concurrent/replayed dispatch never launches twice; crash ambiguity never becomes a fresh attempt |
| MP-4 | Omitted changed file, rename-source escape, wrong repo/unrelated candidate and unproved invariant refuse; actual in-bound Git changes pass |
| MP-5 | Fake PASS, stale execution, wrong observer/slot and incomplete collection refuse; genuine full exact-check evidence admits |
| MP-6 | BLOCKED/CHANGE_DETECTED need no fictional commit; IMPLEMENTED cannot omit one; status mapping preserves review and effect separation |
| MP-7 | Direct/alias/nested/correction host path cannot bypass validation; Codex and Claude independently prove actual mediation or remain UNAVAILABLE |

Each pure predicate needs an independently discriminating reverse mutation and restored green;
each actual host/atomic/Git/evidence claim needs its real boundary qualification. Report the two
strengths separately. No real fixture, run, check or host result is claimed in this draft.

## 8. Readiness and bounded next work

Revision 02 supplies concrete proposals for the parser, limits, primitives/report variants,
canonical digest, path selectors, source responsibility cuts and event mapping. It does not
freeze an unseen implementation ticket. Before SPEC approval, close the remaining complete root
DTO/port success and rejection constructors, authoritative resolver/claim and evidence observations,
Git rename/platform policy, correction/research message schemas, exact per-ticket source/test
boundaries, dependency qualification and check commands. Complete required architecture/Context reattachment and type-preflight planning without
rewriting a sealed Context or delegating design choices to an implementer. This draft cannot mark
those missing decisions READY or use CVQ-01's pending exception as precedent.

The remaining CVE-01 cuts require exact SPEC and ticket admission; CVE-01A's narrower reviewed
foundation is preserved as described in section 10.5, not retroactively expanded. Actual
host/control-path mediation, evidence production and both-host installed behavior need separately
qualified adapters; external effects and release remain separately authorized. P1 A's approved
direction does not enable reduced review until its canonical policy and verifier qualification are
delivered. No source, host settings, YAML executable configuration, test harness, installation,
integration, push or release is changed by this document.

## 9. Bounded helper return and reviewer disposition, 2026-09-18

At baseline `36688a83def524e1bf1af03d2d5f4a13413cbf23`, the reviewer reused the existing
`enforcement_capability` decision-support helper with one structured read-only C00-1/C00-4 task.
The parent checked packet keys/role/scope and actual clean branch, baseline, artifact digests and
profile before the native follow-up. These session-local checks are not the unimplemented product
dispatch gate, exhaustive schema qualification or enforced filesystem isolation. `wait_agent`
returned `PROPOSAL_READY`, `NO_CANDIDATE`, no reported changed files and no reported deviations.

The parent retained proposals for typed variants, separated modules and independent negative
oracles, but did not approve the helper result unchanged. It removed the raw-body digest cycle,
avoided importing unspecified RFC 8785 machinery, preserved external uppercase item IDs, specified
TREE selectors instead of silently dropping the owner's subtree prohibitions, and kept unsupported
Git operation types closed. Numeric bounds and one existing return-event selection are engineering
proposals for the exact SPEC review, not three separate owner questionnaires. Root retains the sole
review conclusion. No implementer, production code, test execution or host enforcement was delivered.

## 10. Revision-03 convergence: complete dispatch boundary proposal

This section replaces the remaining open engineering choices in sections 3, 5 and 8 where named
below. It remains a proposal for owner approval, not an approval signature or capability verdict.
The full-delivery goal and verified rollback refs are bound in CVE-00 revision 05. A reused
decision-support helper returned a finite read-only proposal against control commit
`31a946b4bc8ea21530691cb01c596cae8ed3c8df`; root independently checked the cited Router contracts,
registry and integration wrapper. No source implementation was delegated in that research action.

### 10.1 Exact root shapes and constituent rules

`Counter31` means an exact integer 0..2,147,483,647, rejecting bool; `Revision` is 1..2,147,483,647.
The bounded counter is not represented as an unsigned 32-bit full-range contract.
`ItemId` uses `ExternalId` grammar without lowercasing. A collection retains declared order for
canonical bytes; uniqueness and approval comparison use its named key. Default collection bound
is 0..256 and sections 2/3.1 lexical/aggregate bounds still apply. There are no implicit defaults:
nullable fields and empty collections must appear explicitly. All shapes are immutable named
contracts with unknown fields rejected. No raw mapping escapes the wire codec.

| Record | Exact fields / additional constraints |
| --- | --- |
| `ArtifactBinding` | `id: ExternalId, revision: Revision, lf_sha256: Digest` |
| `ClosureBinding` | `artifact: ArtifactBinding, slice: ItemId` — one current approved slice, not a model-selected set of work |
| `AuthorityBinding` | `repository: ExternalId, object_format: GitAlgorithm, spec: ArtifactBinding, ticket: ArtifactBinding, closure: ClosureBinding, approved_artifact_commit: GitObjectId, baseline: GitObjectId`; both Git algorithms equal object_format |
| `DispatchPacket` | `schema_version: CVE_DISPATCH_V1, dispatch_id: ExternalId, dispatch_digest: Digest, ticket: ExternalId, stage: IMPLEMENT, authority: AuthorityBinding, owner: OwnerBinding, objective: ItemReference, scope: ScopeBinding, work: tuple[WorkItem], preserve: tuple[PredicateRef], acceptance: tuple[PredicateRef], checks: tuple[CheckSlot], return_schema: ArtifactBinding` |
| `DispatchBinding` | `id: ExternalId, digest: Digest` |
| `ReportCommon` | `schema_version: CVE_REPORT_V1, report_id: ExternalId, report_digest: Digest, dispatch: DispatchBinding, ticket: ArtifactBinding, spec: ArtifactBinding, baseline: GitObjectId, owner: OwnerBinding, changed_files: tuple[GitChange], scope_deviations: tuple[DiagnosticRecord], work: tuple[WorkObservation], checks: tuple[CheckObservation], findings: tuple[DiagnosticRecord]` |
| `ImplementedReport` | Every ReportCommon field plus top-level `status: IMPLEMENTED, candidate: CommitCandidate`; all work DONE, all required checks independently accepted, scope_deviations empty |
| `BlockedReport` | Every ReportCommon field plus `status: BLOCKED, candidate: CandidateBinding, blockers: tuple[DiagnosticRecord]` with 1..256 blockers |
| `ChangeDetectedReport` | Every ReportCommon field plus `status: CHANGE_DETECTED, candidate: CandidateBinding, changed_contracts: tuple[ArtifactBinding]` with 1..256 distinct changed bindings |

ReportCommon is a constituent, not another wire nesting level. The report union discriminates on
the owner's top-level `status`; there is no competing `result.kind` or `files` alias. Fields unique
to a different report variant reject. Candidate, WorkObservation, CheckObservation and
DiagnosticRecord are the exact section-5.1 types; diagnostic codes must resolve under the bound
return schema. A diagnostic's evidence can prove absence/failure, not just successful execution.

Dispatch ticket equals authority.ticket.id. Work, acceptance and checks each contain 1..256
entries; preserve may be empty only when the independently approved slice is also empty. Scope
requires 1..256 grants; its forbidden collections may be empty. Item IDs, path-selector/operation
pairs, forbidden predicates and check/slot pairs are unique. Work, Preserve, Acceptance, checks,
objective and return schema equal the independently compiled current slice, including each
reference's revision/digest and check order. Same ID with different content rejects. A fixed
return schema owns variant fields and registered codes; the sender cannot supply a validator.

### 10.2 Independent authority, observations and effect ordering

The short-lived trusted composition supplies an `AdmissionContext` containing independently
chosen `project: ExternalId, expected_dispatch: ExternalId, approval: ArtifactBinding,
lane: InternalId, generation: Revision`. The untrusted packet cannot select a different approval
or invoke a port against arbitrary filesystem/remote paths. `ApprovedSlice` contains the complete
expected DispatchPacket fields except its self-digest, plus that context and the qualified
execution/evidence/host policy references. It is loaded from protected owner approval; a copied
ticket or computed digest does not create that approval.

Every port returns a tagged immutable success value or a named failure, never a truthy flag,
dynamic dict or exception-as-success. Source-contract tests use explicit fake ports and make no
claim that those fakes are protected in production.

| Port / input | Required success observation | Finite failure domain |
| --- | --- | --- |
| Authority resolver / AdmissionContext | `RESOLVED {context, slice: ApprovedSlice}` | NOT_FOUND, STALE, CONFLICTING, UNAVAILABLE |
| Lane observer / independently bound lane | `CURRENT {repository, object_format, baseline, owner, generation, clean: true, observation_id}`; actual filesystem/worktree/branch identity, not string labels | DIRTY, MISMATCH, STALE, UNAVAILABLE |
| Git candidate observer / lane plus asserted commit | `OBSERVED {repository, object_format, baseline, candidate, generation, changes, observation_id}`; commit existence and ancestry checked inside adapter | NOT_FOUND, WRONG_REPOSITORY, NON_DESCENDANT, STALE_SNAPSHOT, DIRTY_LANE, UNSUPPORTED_CHANGE, UNAVAILABLE |
| Evidence resolver / expected candidate and CheckSlot | `RESOLVED {evidence_ref, candidate, slot, plan, attempt, role, producer, toolchain, environment, disposition, manifest_digest, raw_evidence_refs}` from the sole CVE-02 evidence schema | MISSING, DUPLICATE, STALE, BINDING_MISMATCH, UNVERIFIABLE, UNAVAILABLE |
| Host delivery / bound admitted command plus claim | HOST_ACCEPTED with delivery identity; NO_EFFECT with observed refusal; EFFECT_UNCERTAIN with recovery reference | No additional success alternative; unsupported capability is observed NO_EFFECT, transport ambiguity is EFFECT_UNCERTAIN |

The evidence disposition remains PASSED, FAILED, UNRUN, UNKNOWN or CANCELLED even when its
record authenticates. Authentic FAILED is not a missing record and cannot disappear into PASS.
Slot acceptance is separate: a qualified expected-red oracle may be satisfied by the named
assertion failure, never merely a nonzero exit, collection error, timeout or unrelated failure.
Expected attempts, roles, producers, environment and toolchain come from the approved plan, not
report fields. The single CVE-02 schema must be frozen before a report-admission ticket can bind
this port; this proposal does not create a competing evidence contract.

Admission resolves source, full slice, lane and required capabilities before the claim. The
protected controller then atomically claims `dispatch_id` bound to dispatch digest, project,
ticket, owner/lane, baseline, generation and exact host surface. Results are CLAIMED,
ALREADY_CLAIMED (same identity plus recorded state), IDENTITY_CONFLICT or STORAGE_UNAVAILABLE.
Claim persistence precedes the one host call. Same identity returns its existing outcome; altered
identity refuses. A claim without proof of no effect is uncertain, not permission to retry.

Before effect, the broker independently revalidates the source/generation and executes from an
immutable admitted snapshot. A validation result or `AdmittedDispatch` Python object is data,
not an unforgeable capability; an imported constructor or forged object must not bypass the
broker's own invariants. Policy/evidence ownership and immutable-source execution require CVQ
qualification. A hash check followed by use of mutable files is insufficient.

Reconciliation yields NO_EFFECT, HOST_ACCEPTED, EFFECT_UNCERTAIN, NOT_FOUND, IDENTITY_CONFLICT
or STORAGE_UNAVAILABLE. It does not launch. Settlement is bound to report ID/digest and the
claimed identity, yielding SETTLED, ALREADY_SETTLED, CLAIM_NOT_FOUND, CLAIM_MISMATCH or
STORAGE_UNAVAILABLE. Identical settlement is idempotent; changed report content conflicts and
cannot emit another Router event. Durable projection/outbox consumption must share the claimed
generation; an in-memory seen-set is not cross-process exactly-once proof. No new synchronous
receipt issuer, wake queue or always-running runner is introduced.

### 10.3 Deterministic Git change policy

Read the exact baseline/candidate raw tree delta with rename detection disabled. Reject mode,
type, submodule, unresolved filesystem identity and unsupported object-format changes before
scope comparison. Pair a deleted regular file and added regular file as RENAME only when their
blob IDs and modes are equal and that pairing is unique within the delta. This classification is
performed independently, not chosen by the report. Both endpoints require RENAME grants.
Modified or ambiguously paired moves remain DELETE plus CREATE and require those permissions.
The report must equal this complete canonical change set; an unproved reported rename rejects.
No similarity threshold, locale-dependent output parser or first-match pairing is admitted.

The Git/filesystem adapter separately qualifies case collisions, Windows reserved names,
reparse/link traversal and repository containment. Lexical RelativePath validation alone cannot
assert these facts. A declared forbidden predicate must have a qualified source-derived result;
failure to resolve it is rejection, never an AI declaration that the invariant seems preserved.

### 10.4 Correction and research are separate data variants

Correction V1 binds `correction_id: ExternalId, correction_digest: Digest,
original_dispatch: DispatchBinding, correction_ref: ArtifactBinding, review_commit: GitObjectId,
prior_report_digest: Digest, ticket: ArtifactBinding, owner: OwnerBinding, baseline: GitObjectId`,
plus `failed_predicates: tuple[ItemReference]` and `evidence: tuple[InternalId]`, each 1..64.
Its schema version is CVE_CORRECTION_V1. Resolve scope and full required sets from the admitted
original slice; a correction cannot supply replacements or increase execution slots. It preserves
ticket revision, owner and lane. A formally revised ticket needs a newly admitted dispatch/view
bound to the new approval, while retaining the same implementation owner where lifecycle permits;
it is not permission to silently resume the old packet. Correction return adds exact correction
binding to its registered report variant. One review plus one correction remains the cycle bound.

Research V1 binds `research_id: ExternalId, research_digest: Digest, query: ItemReference,
registry_commit: GitObjectId, reviewer: InternalId, helper: InternalId, view: InternalId,
sources: tuple[ItemReference], work: tuple[WorkItem], return_schema: ArtifactBinding,
max_findings: Counter31`, with schema CVE_RESEARCH_V1 and effect_policy READ_ONLY_NO_EFFECT.
Sources are 1..64, work 1..32 and max_findings 1..64. Reviewer/helper are distinct. No writable
scope, test execution, delegation or provider effect may be represented. Its report has schema
CVE_RESEARCH_REPORT_V1, exact research ID/digest, status COMPLETED or BLOCKED,
candidate NO_CANDIDATE, bounded findings/evidence, and empty changed_files/scope_deviations.
BLOCKED also requires a named diagnostic. It never projects an implementation completion or
approval. Input minimization is not a claim that a reused Agent's previous context was erased.

Auxiliary digests use the section-2.2 canonical method with only their own top-level self-digest
omitted and distinct NUL-terminated domains `johnny.cve.correction.v1`, `johnny.cve.research.v1`
and `johnny.cve.research-report.v1`. These new domains are not delivered by CVE-01A's two existing
fingerprint functions. Every auxiliary variant needs its own ordinary constructors, codec
rejections, fixed vectors and independently discriminating mutations before admission.

### 10.5 Completion order and unresolved approval/capability boundaries

CVE-01A at `d0c93111ee1ae6a7f98779cc64b8e8ba52a62d03` supplies only strict scalars, lexical
paths/selectors, canonical values/bytes and dispatch/report fingerprints plus tests. It does not
supply the root DTOs, YAML codec, authority resolver, evidence verifier or host adapter. Its
20-test review is not acceptance of any missing component.

The next bounded cuts are: (1) root/constituent contracts and constructor tests, (2) qualified
bounded YAML event codec, (3) current-slice projection and pure dispatch admission, (4) CVE-02
complete-cell evidence contract and independent verifier, (5) actual Git observation and report
admission, (6) qualified atomic claim/recovery/controller, (7) auxiliary variants and Router
projection, and (8) separate Codex/Claude protected delivery plus enrolled end-to-end acceptance.
CVE-03 budgets and the qualified finite executor are required dependencies of effect delivery;
WA-04/CVE-04 and CVE-05/06 remain required integration/release evidence, not optional polish.
Concrete per-ticket file boundaries and commands are compiled only from an approved closed SPEC.

Retain PyYAML 6.0.3 as the parser proposal, but it is absent from the inspected runtime lock.
Qualify exact artifacts/type boundary in a separate development environment; pin supported
artifacts through the existing dependency owner. Do not alter the installed Router interpreter.
Codec tests must observe all section-2 rejection rules and bounds while consuming events. Neither
successful parsing nor a 64 KiB input ceiling proves OS CPU/memory containment.

Root rejects the helper's assumption that CVE-01A already included root DTO/codec delivery and
its implied unforgeable Python wrapper. The deterministic rename rule above also resolves its
conflicting ambiguous-rename suggestions. These are documented engineering corrections, not
owner decisions or scope reduction. Remaining approval is the complete affected contract/Context
packet and the separately asked construction-before-preflight ordering exception. No owner Grill
has been performed by another Agent. Production capability, VM operation and later installation
must still supply their own exact, current evidence and permitted effect boundary.

### 10.6 Evidence and shared-budget convergence disposition

A second bounded research return at `db6bd375f52389a7f428918e68a16e331bfa0d66` covered
CVE-00 C00-2/C00-3 only. It supplied proposals, not approved CVE-02/CVE-03 contracts or delivered
ports. Root keeps the following constraints for the next contract cut:

- CVE-02 owns one ordered plan/slot/attempt/role schema consumed unchanged by CVE-05 and CVE-06.
  Every declared slot needs one result, including refused, unavailable, conditional and unrun
  slots. Intentional repeats, first-red/green and reviewer-red/restoration are distinct slots.
- Separate actual execution outcome from the expected oracle. A first-red/reverse-red keeps
  FAILED plus EXPECTED_FAILURE_OBSERVED; zero red, a different assertion, import/collection
  failure, timeout, cancellation and output overflow cannot satisfy its registered cause.
  Restored green has separate evidence. At least one reviewer mutation in the review set uses a
  different guard/path from the implementer; not every individual mutation must use a new door.
- Preserve every earlier attempt. The proposed reduction cannot both allow infrastructure
  retries and unconditionally fail on every earlier infrastructure failure: freeze a separate
  recovery-group predicate before admitting any retry. Assertion failures are never retryable;
  required consecutive-success predicates inspect the full declared sequence, not a filtered
  all-green subsequence. Until that algebra closes, no retry-enabled product plan is admitted.
- The plan binds the reviewed candidate separately from each actual executed snapshot. First-red
  baseline and declared mutated snapshots must resolve their own exact source/transform identities;
  they cannot falsely claim to be the final candidate's unmodified tree.
- Evidence authentication is an independently qualified protected-record/producer boundary, not
  a candidate-supplied `verified` field. Reject the helper's proposed self-covering signature
  digest: no digest or proof is included in its own digest input. A cryptographic signing service
  is not implicitly selected or required merely to authenticate protected local evidence.
- Reserve one root budget across parent, descendants, resumes and retries before effects.
  Per-child limits are views/subceilings of that capacity, never additional money. Keep consumed
  usage and outstanding reservations disjoint; closing a child cannot erase its consumed usage
  or count the same descendant twice. Concurrent last-capacity reservations need a qualified
  atomic storage boundary, not just a pure arithmetic test.
- Separate cumulative usage from simultaneous resource leases and cleanup capacity. Charge
  model input once under the qualified provider's counting semantics; cached-input fields may
  be subsets of input, not additional tokens. Missing dimensions stay unavailable. Never add
  unlike units or overlapping provider counters to manufacture a total or savings percentage.
- KNOWN usage may release proved unused reservation; unknown-but-independently-hard-bounded usage
  conservatively charges its full allowance, without claiming that amount was measured. Unknown
  unbounded usage blocks further work, grants no refund and cannot establish a hard token cap.
  Release process/resource leases only after owned cleanup evidence; cleanup failure retains
  RECOVERY_REQUIRED, bounded recovery capacity and the original failed attempt.

These dispositions reject concrete proposal defects before implementation. Remaining contracts
are named, not assigned to an implementer: exact retry reduction, snapshot variants, authenticated
evidence variants and budget units/account transitions. Numeric work/cleanup ceilings must become
approved profile data for each supported host; the qualification SPEC's synthetic lab ceilings
are not production defaults. No fixed token amount is invented here, and no metadata-only host
probe proves enforceability. Proceed with the already-approved capability-first investigation
once its separately pending constructor/preflight exception is decided; do not build a product
adapter around an unproved hard-cap or dispatch surface.
