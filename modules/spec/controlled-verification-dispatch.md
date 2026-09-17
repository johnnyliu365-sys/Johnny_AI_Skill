# Machine-validated Agent dispatch and return — contract draft

| Field | Value |
| --- | --- |
| Specification ID / revision | `SPEC-CONTROLLED-VERIFICATION-DISPATCH-20260918-01` / `02` |
| Lifecycle | `DRAFT / CONTRACT_CONVERGENCE / NON_DISPATCHABLE` |
| Author / branch / baseline | Current-session reviewer; `codex/controlled-verification-intake`; `36688a83def524e1bf1af03d2d5f4a13413cbf23` |
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
| `scope.allowlist` | Approved path grants with explicit create/modify/delete/rename/type-change permissions; default deny |
| `scope.forbidden_paths`, `scope.forbidden_invariants` | Distinct path selectors and registered invariant predicate IDs; explicit prohibition prevails, unknown predicate refuses |
| `work` | Unique item IDs and exact approved refs, matching the complete current slice; no new task meaning from free text |
| `preserve`, `acceptance` | Exact required invariant/closed-finding/AC refs; complete coverage may be many-to-many but cannot omit requirements |
| `checks` | Unique check and execution-slot IDs plus approved execution-plan refs; resolve executable/argv, snapshot, dependencies, environment, order/load/count/retry/deadlines independently |
| `return_schema` | A fixed registered schema ID/revision/digest; the wire's displayed status/required-field list must equal that schema, never a caller-defined validator |

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

All report variants bind `schema_version`, `dispatch_id`, `dispatch_digest`, `ticket`, ticket and
SPEC revisions/digests, full `baseline`, owner/lane and report identity/digest to the admitted input.
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
  and supported submodule operations. Undeclared/unqualified operation types reject.
- Verify required invariants and candidate-bound check evidence through the shared CVE-02 evidence
  contract. Manifest/producer/environment/toolchain/attempt/role must match; missing/unrun/stale/
  forged/cancelled/failed required checks never become success through YAML PASS or exit zero alone.
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
execution-evidence ID. DONE/PASSED requires independently accepted evidence; UNRUN is explicit,
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

The first pure implementation cut remains CVE-01 after exact SPEC and ticket admission. Actual
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
