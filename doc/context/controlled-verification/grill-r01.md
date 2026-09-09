# Controlled verification — owner Grill and approval packet

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `GRILL-CONTROLLED-VERIFICATION-20260909-01` / `OWNER_GRILL` / `04` |
| Lifecycle | `OWNER_APPROVED / COMPLETED / CVQ01_PREPARATION_ONLY` |
| Owner | Human project owner; the assistant and research helper do not answer or approve for them |
| Sources | [REQ-051](../../requirements/active/2026/environment-control/REQ-20260908-051.md), [Wayfinder](wayfinder-r01.md), [architecture](architecture-r01.md), [shared Context candidate](main.md), [qualification SPEC candidate](../../../modules/spec/controlled-verification-qualification.md) |

## Already answered — do not reopen

| Decision | Confirmed meaning |
| --- | --- |
| D1 | Enforce approved source responsibility/dependencies; no line-count ceiling |
| D2 | Restrict only explicitly enrolled Johnny Agent sessions/worktrees; preserve other projects and human terminals |
| D3 | Dedicated launcher + restricted Windows identity + protected broker; qualification in the existing Windows VM only, no physical-host configuration change or external model call |

These decisions are already committed in REQ-051 revision 04. The guest `admin=true` report is
readiness input, not a new permission request or an installed-capability PASS.

## Proposed closure of the engineering questions

| Concern | Proposed exact answer / acceptance |
| --- | --- |
| Observable result | A finite capability report with separately named proven, failed, unavailable and unrun capabilities. Completing an investigation does not mean the final enforcement product is delivered. |
| Flow and ownership | Four slices each have validation, command/event, storage owner, read projection, returned state and lifecycle/privacy in the architecture. No new generic workflow tree. |
| Responsibility and language | Python typed contracts, separate admission/execution/recovery/evidence/host boundaries, short-lived explicit Composition Root and injected fakes. Existing WA-04 remains the only source-responsibility slice. |
| Policy and permission | Independently resolved protected approval; untrusted workload cannot write policy, broker/configuration or final evidence and never uses the protection-owner token. |
| Cost and operations | Proposed SPEC section 4 fixes one lane, zero automatic retries, 30-second workload cases, 1,200-second total manifest ceiling and explicit CPU/memory/disk/process/evidence bounds. These are experiment ceilings, not guessed production defaults. |
| Disk limit | Count or deny every subject-writable workspace/temp/profile/cache destination; free space and monitoring do not qualify. Missing hard control refuses dependent work. |
| Restart/idempotency | Protected monotonic attempt evidence; same key starts at most once; completed plus stale UI replays only; ambiguous crash window requires recovery, never automatic redispatch. |
| Host coverage | Closed exact-version/surface effect roster; unknown paths refuse. Offline real tool dispatch is required; fake-hook tests and CLI-to-Desktop inference are insufficient. |
| Provider/cache/data | No external model calls, real credentials, production data, new cache service or telemetry subsystem. Synthetic evidence is bounded and failed attempts are preserved. |
| Recovery | Exact VM/checkpoint and protected bootstrap before mutations; no implicit restore/delete or persistent service. Failed cleanup blocks dependent work. |
| XSS | Not applicable to the new CLI/OS qualification slice; adding renderer/privileged bridge triggers a separate upstream classification. |
| Compatibility | Existing EC-10 resource rules, WA-04 ownership, integration gate and probabilistic installed-activation policy remain unchanged. |

## Independent decision-support input, not owner approval

The existing Sol/high `RESEARCH_HELPER` was reused for one read-only bounded query while the
parent drafted. It returned five concrete gaps: disk accounting scope, closed host effect roster,
identity continuity through spawn, crash/claim reconciliation and typed prerequisite admission.
The SPEC candidate addresses them in sections 2–6. No helper wrote source, ran a workload,
approved the architecture or supplied the final review verdict. No activity polling was used.

The same helper then challenged the immutable candidate
`190c094b70ef07917f0ef7a9e52806085c062b8f` (SPEC revision 01, LF digest
`f281c9bc4ad668db44bea5c165fad0a1f9bd408bd45cb656d4cfb8190b9f027a`). Parent waited through
`wait_agent` and independently checked the cited contract/state clauses. Five genuine draft
defects were accepted and addressed in SPEC revision 02, before any implementation dispatch:

| Finding | Revision-02 disposition |
| --- | --- |
| Pre-launch object requires post-launch OS identity and invents VM fields for pure work | PureContractBinding and NativePreLaunchBinding are disjoint tags; later LaunchObservation holds actual native identities |
| Prerequisite matching lacks a closed constituent contract | Exact prerequisite key, observation revision/digest, independent resolver variants and finite refusal detail are defined |
| Partial admission has no deterministic report reduction | Four tagged case results preserve every expected slot; complete/incomplete observation and cleanup states have exact outcome precedence |
| Recovery-required attempt has no lawful settlement | Original failure is retained; a separate owner-bound RecoveryRecord may resolve cleanup dependency, never relaunch the old attempt |
| Roster coverage is an unchecked completeness assertion | Exact host key, entries/aliases, actual discovered set, reachability, dispositions and zero-unknown set comparison are required |

This is specification decision support, not ticket code review, a fabricated approved Closure Set,
or a native capability test. Proposed pure/native result constructors and the finite reduction
rules must still be exercised by CVQ-01's admitted implementation/type preflight. No production
PASS is inferred from correcting prose.

### Bounded correction check and parent convergence

The same helper checked correction candidate `2e726fbc48ff76fb4908f29a3cf4d79408820860`,
SPEC revision 02 LF digest `d9a8e86c15d715949ac3820b7d8d07d70075fc4a33b7087f2fee131139ec1494`.
It closed the pure/native binding, constituent prerequisite and append-only recovery findings.
It still found three exact draft gaps: undefined top-level evaluation return; absent tools forced
into present-entry IDs; and discovery/enforcement roster evidence with circular timing.

The parent accepted those counterexamples and made one control-plane convergence revision (SPEC
03): a closed QualificationEvaluation union; PRESENT/ABSENT category coverage with exact-set
comparison over present identities only; and pre-execution HostRosterDiscoveryCoverage separate
from post-execution HostRosterEnforcementCoverage. These are direct closures of existing rules,
not an expansion of D1/D2/D3. No third helper review or implementation correction loop is started.
The last helper return was FINDINGS, not NO_FINDINGS or approval. Revision 03 is parent-corrected
and was owner-unapproved when submitted; constructor/native execution evidence does not yet exist. This record must
not be presented as an adversarial code-review PASS or a qualified host.

## Exact response requested at revision 03 — historical

Owner review is requested for this packet's proposed engineering closure and the exact indexed
revisions of the architecture, shared Context candidate and qualification SPEC. On approval:

1. Record the actual owner response and seal the approved shared Context; do not fabricate a
   prior Grill completion or overwrite an existing sealed shared Context.
2. Record the exact SPEC approval and permit preparation of **CVQ-01 only**, the source-only
   qualification-contract/prerequisite/report-admission ticket.
3. The normal ticket preflight/approval and same-lifetime implementation path still apply.
   No VM, host configuration, account/ACL, checkpoint, install, provider, push or release effect
   follows from the CVQ-01 source-only approval.

Unproved native primitives are deliberately the future investigation's output; the implementer
must not fill that gap by choosing weaker behavior. There is no new D1/D2/D3 decision and no
request to repeat the guest elevation command. The revision-03 packet was not an approval record.

## Actual owner response and stage continuation — 2026-09-09

The human owner's next response was `核准`, answering the exact question to approve architecture,
Context and SPEC revision 03 and prepare CVQ-01 only, without VM operations. This is the actual
owner response, not an assistant/helper inference or a retroactive code-review approval.

Approved packet commit: `161c4e095697fff6e4693b8d9bfce866878277dd`.

| Approved source | Revision | LF SHA-256 |
| --- | --- | --- |
| Architecture | `01` | `ac345d47550020af5bcffc3fc2000f4f1c33b526f9240d2cf33f8dad9f24db62` |
| Shared Context draft | `01` | `9a909d610acf53e023e2b1d53161d5ba3d319e116b5264538d9914ca7c4cad41` |
| Grill packet | `03` | `185ec0ae2aa533d82fca7a91d02b64ab1dc699584d55319d0d3a018452788584` |
| Qualification SPEC | `03` | `e5ed081dcbb3f1aadfbe43d874273fabafea521e49c6301496ea24b9054c46a5` |

Ordered control-plane returns: `APPROVAL_GRANTED` resolves this Grill; `ACTION_COMPLETED`
permits CONTEXT's first seal; CONTEXT completion permits recording the exact SPEC signature;
SPEC completion permits `AUTO_CONTINUE -> TICKETS` for CVQ-01 preparation. Each action uses
only its declared scoped authority. Subsequent ticket preflight and dispatch confirmation are
not pre-approved by this response. Native capability evidence remains absent.

Revision 04 records approval only. No third helper review, source implementation, VM operation,
provider request, integration, push or release occurred. The original helper findings remain
historical evidence above, not a fabricated PASS. Ticket creation is recorded by its own tree.
