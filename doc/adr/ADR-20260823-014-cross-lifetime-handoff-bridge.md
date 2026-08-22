# ADR-20260823-014 — The runner is a cross-lifetime handoff bridge, not a dispatch precondition

- Date: `2026-08-23 (Asia/Taipei)`
- Status: `ACCEPTED` — the owner has explicitly accepted Decision 3, which reverses the
  same-turn-wait alternative recorded as owner-rejected in ADR-20260815-012.
- Decision makers: project owner and architecture owner
- Related specification: `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2`
- Related change: pending
- Narrows: `ADR-20260815-012`

## Owner acceptance of the reversal

ADR-012 lists `Same-turn blocking model wait` under **Alternatives rejected**: "rejected by the
owner; only the event adapter plus wake port is admissible."

Decision 3 below makes exactly that the default. The owner accepted this reversal on
`2026-08-23 (Asia/Taipei)`. Its ground is that ADR-012
grouped blocking wait with heartbeat and polling under "spends tokens without evidence", and the
three do not share a cost profile. Polling and heartbeat **re-read** on an interval, so cost grows
with elapsed time. A blocking wait is one call that returns when the child settles: it **holds**
the parent's context rather than re-sending it, and costs one notification regardless of how long
the child runs. Measured on 2026-08-22: thirteen dispatches, one completion notification each,
zero interval reads.

The accepted default does not remove the unarmed path: when a producer and consumer have different
lifetimes and the bridge is unavailable, a person still relays completion as governance 04
documents.

## Context

Two tickets ran a complete cycle on 2026-08-22: dispatch, implementation, review with reverse
mutation, full suite, gated integration. The runtime state afterwards:

| File | Last written |
| --- | --- |
| `runner-state.json` (`status: STOPPED`) | 2026-08-21 |
| `work-queue-v1.json` | 2026-08-21 |
| `worker-assignments-v1.json` | 2026-08-21 |
| `dispatch-journal.jsonl` | 2026-08-21, zero entries that day |
| **`document-mutation-journal.jsonl`** | **2026-08-22, eighteen entries** |

The entire queue, runner and dispatch-authority subsystem was untouched while the only control
that actually governs `main` — `admit_document_mutation` — did all the work.

Meanwhile a second host read ADR-012 together with `references/router-control.md` and
`references/implementation-authority.md`, all of which state the receipt-bound gateway in the
present indicative, and concluded that a live descriptor is a precondition for creating any
implementation lane. It then proposed a four-port host gateway, an App Server capability
qualification ticket and a change-control exception: four layers of prerequisite, no product
movement, terminating in a documented absence of any effective-profile readback endpoint.

That is governance 04's family one level up. Prose describing an optional mechanism in the
present indicative, read by an agent as a universal precondition.

## Decision

**1. The runner plus its gateway is a cross-lifetime handoff bridge.** It is not a core mechanism
of this system. It supplies event delivery on a host that does not supply it. On Claude Code the
harness wakes the parent when a child settles; on Codex `wait_agent` is the only completion
callback and the parent must stay alive. The same component is redundant on the first host and
load-bearing on the second.

**2. The bridge is load-bearing only when producer and consumer are in different lifetimes.**
Same lifetime — dispatch, wait, receive — needs no bridge. Different lifetime — a commit landing
with nobody running, a cross-session handoff, machine A committing and machine B reacting — needs
one. Dispatch is synchronous, therefore **no bridge may sit on the dispatch path**, and no
synchronous flow may be blocked because a bridge is absent.

**3. The default workflow is synchronous.** The reviewer dispatches, waits (`wait_agent` or a
harness notification), receives, reviews, and integrates through `admit_document_mutation`. No
runner, no queue, no receipt, no descriptor. This is the reversal named at the top of this
document.

**4. The bridge's primary use is a deliberate model handoff, not an unattended commit.** Because
the workflow changes model between phases, every phase change necessarily crosses host, session
and context. That is far more frequent than the unattended case, which ADR-012 treated as the
motivating scenario.

**5. Review is split by kind, and each kind is matched to a model's disposition.**

| Reviewer | Reviews | Why that model |
| --- | --- | --- |
| Codex | Each implementer ticket: conformance to the implementation specification, and code security as defence in depth | Divergence is an advantage in **breadth scanning** — it looks where nobody told it to look |
| Claude Code | After a feature cluster completes: **architectural consistency** | Cluster review needs a correct model of the project; alignment between architecture and function is this model's default bias |
| Antigravity | Red-team testing, risk-boundary audit, technical-debt review | An outsider with no stake in the design sees outside our framing |

Two constraints on this split. The author of a ticket does not review that ticket. Independent
review must be **cross-model**: another instance of the same lineage is not independent, because
context contamination is what changes between instances and disposition is not.

**6. The bridge does not restore a session; it carries an artifact.** Codex's `thread/start`
creates a new actor rather than resuming the original, and that is acceptable rather than a
limitation, because durable state lives in tickets, journals and the artifact tree, and an agent
is expected to re-derive from artifacts. It follows that **the artifact tree is the bridge's
payload format**, which is why durable state is metadata-only, why a ticket must be
self-sufficient, and why a dispatch message may not restate what the ticket already holds.

**7. Wake capability has three finite states, not two.**

| State | Meaning | Remedy |
| --- | --- | --- |
| `NOT_REQUIRED` | The host delivers natively | Nothing to do |
| `AVAILABLE` | The host does not deliver; the bridge is present and proved by an actual delivery | Nothing to do |
| `UNAVAILABLE` | The host does not deliver and the bridge is not available | A person relays, which is governance 04's unarmed path |

`wake_capability` currently exposes `PROVEN` and `UNAVAILABLE` only, which folds "not needed" into
"broken". An agent reading the folded value can only treat it as degradation, and will build
compensating machinery. Two facts with different remedies must not share a name.

## Alternatives rejected

- **Build the host gateway, receipt issuance and durable queue before dispatching anything.**
  Four layers of prerequisite for one ticket, and the App Server exposes no documented endpoint
  for effective model and effort readback, so the chain fails closed at its own end. The cost is
  paid whether or not the capability is ever reached.
- **A bootstrap exception permitting one unverified dispatch.** Narrow at first, and an exception
  with no expiry becomes the rule.
- **Gateway self-attestation standing in for host readback.** That changes what readback means and
  must go through change control rather than arrive as an implementation detail.
- **A second instance of the same model as the independent reviewer.** Rejected on measured
  grounds, recorded below.

## Consequences, risks and recovery

**ADR-012 is narrowed, not replaced.** Receipt-bound supervision remains the mechanism for the
asynchronous case. It stops being a precondition for synchronous dispatch. The two skill
references that state it in the present indicative — `references/router-control.md` and
`references/implementation-authority.md` — require a separate ticket to carry the same
qualification; this ADR does not edit them.

**The three-way review split has one measured datum, and it is a miss rather than a success.**
On 2026-08-22 an Opus implementer and an Opus reviewer each found real defects in the other's
work: the reviewer's ticket contained a contradiction the implementer surfaced, and the
implementer's pin was bound to nothing, which the reviewer's counter-mutation exposed. Neither
found pitfall C13 — the same commit answers differently in a worktree than in the main checkout,
because a harness-created directory exists in one and not the other. Both actors ran the suite in
a worktree. Neither considered running it where a user would. That is a shared blind spot from a
shared lineage, it is an environment and boundary question, and it belongs to the third
reviewer's category. **The outsider leg is not insurance; it is the category that has already
been missed once, and the gate went green on it.**

**Third-party review must be fed artifacts, never a summary.** A summary written by either of the
first two models reintroduces their framing through the input, so the model changes and the blind
spot does not.

**The third-party pass doubles as an acceptance test of the artifact format.** A reviewer with no
shared context can only work from what is written. If it cannot review from the artifacts alone,
the finding is that our artifacts are insufficient, not that the reviewer is.

**Known gaps, stated rather than closed.**

1. *A stale event has no named outcome.* Measured: `STALE`, `SUPERSEDED` and `BASELINE` have zero
   occurrences in `work_queue.py` and `commit_trigger_intake.py`. An event delivered late may name
   a baseline that has moved. The gate refuses it, but the refusal is named "merge failed" rather
   than "this event expired": two different facts under one name, which is governance 16's family.
2. *A stuck event is not visible.* Timers and polling are forbidden and liveness is discovered on
   read, which is correct. But an event nobody claims is currently indistinguishable from an empty
   queue. This needs a query entry point, not a timer. The shape is ticket 21's.
3. *Landing-point semantics were undeclared.* Decision 6 closes this one.

**Recovery.** Nothing here forbids genuine asynchronous wake. If a case arises where an event must
start work with no person and no live parent, the bridge is the mechanism for it. This ADR forbids
only treating that mechanism as a precondition for work that is synchronous.

## Revision and supersession record

| Date | Actor / baseline | Summary |
| --- | --- | --- |
| 2026-08-23 | Architecture owner / `main` | Drafted as `PROPOSED`. Decision 3 reverses an alternative ADR-012 recorded as owner-rejected and is held pending the owner's explicit word; the remaining decisions stand independently of it. |
| 2026-08-23 | Project owner / owner confirmation | Accepted Decision 3 and therefore the ADR. Same-lifecycle `dispatch → wait → review → guarded integration` is the default; the runner remains only a cross-lifetime handoff bridge. |
