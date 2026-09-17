# Machine-validated Agent dispatch and return — contract draft

| Field | Value |
| --- | --- |
| Specification ID / revision | `SPEC-CONTROLLED-VERIFICATION-DISPATCH-20260918-01` / `01` |
| Lifecycle | `DRAFT / CONTRACT_CONVERGENCE / NON_DISPATCHABLE` |
| Author / branch / baseline | Current-session reviewer; `codex/controlled-verification-intake`; `64882e6a2aaf96bb4c1f16309257be38600b1d3f` |
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
Reject unknown schema versions and malformed IDs. Parser byte/depth/node/string limits and
package/version qualification are mandatory unresolved entries in section 8, not hidden defaults.

Parse into immutable named DTOs before any effect. Preserve exact identifier/path code points;
reject rather than silently trim, lowercase or normalize authority identity. A separate explicit
identity resolver maps external IDs to existing internal opaque IDs. Structured content and
human-readable findings are data, never additional executable instructions. The controller may
render human explanations separately; Agent-to-Agent control messages remain schema-defined.

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

Before SPEC approval, close exact parser package/grammar/resource bounds, constituent DTO types,
canonical serialization/digest algorithm, path-operation grammar, authoritative resolver/claim
and evidence contracts, correction/research message variants, source/test boundaries and check
commands. Complete required architecture/Context reattachment and type-preflight planning without
rewriting a sealed Context or delegating design choices to an implementer. This draft cannot mark
those missing decisions READY or use CVQ-01's pending exception as precedent.

The first pure implementation cut remains CVE-01 after exact SPEC and ticket admission. Actual
host/control-path mediation, evidence production and both-host installed behavior need separately
qualified adapters; external effects and release remain separately authorized. P1 A's approved
direction does not enable reduced review until its canonical policy and verifier qualification are
delivered. No source, host settings, YAML executable configuration, test harness, installation,
integration, push or release is changed by this document.
