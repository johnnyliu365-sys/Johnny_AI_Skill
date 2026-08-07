# Code Review — Ticket 03: Plugin Policy and Fixed Dispatch Response

| Field | Value |
| --- | --- |
| Review result | `BLOCKED` |
| Reviewed implementation | `4d68938` (`feat: enforce plugin policy and dispatch response`) |
| Docs-only handoff | `9eda250` (`docs: hand off plugin policy response`) |
| Reviewed branch / owner | `codex/implementation-plugin-policy-and-response-03` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/03-plugin-policy-and-response.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-1, AC-3, AC-9, AC-10 |
| Submitted baseline | `ad70448`; submitted worktree clean |
| Review date | `2026-08-08 (Asia/Taipei)` |

## Scope and evidence reviewed

- Only committed artifacts were reviewed: implementation `4d68938`, docs-only handoff `9eda250`, the approved SPEC/ticket/Context, current Ticket-02 review return, and existing Router tests.
- The submitted branch merge-base is exactly `ad70448`; its submitted range contains only `4d68938` and `9eda250`. The implementation worktree was clean before and after review. No implementation file was modified, staged, merged, pushed, installed, or deployed.
- The document/skill/template wording correctly attempts to state the topology question, one named dispatch question, and the non-commercial boundary. Those text assertions cannot replace the executable Router policy or the metadata-only boundary below.

## Independent verification

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | Passed: `80` tests. |
| `python -m mypy --strict --no-incremental library tests` | Passed: `60` source files. |
| In-memory compile of `library/workflow_router/*.py` | Passed: `11` modules. |
| `git diff --check ad70448 4d68938` | Passed. |
| Synthetic `PolicyDocumentSource` read | Incorrectly returned its raw synthetic document string in a `RouterModel`. |
| Existing indirect private-router ticket approval test | Incorrectly still passes by advancing `TICKETS + APPROVAL_GRANTED` with a handoff directly to `IMPLEMENT`. |
| Synthetic formatted response with arbitrary shape-valid commit/ticket values | Incorrectly rendered a `工單 ready` response without a Router-owned pending dispatch descriptor or committed-artifact binding. |

## Blocking findings

### CR-16 — `PolicyDocumentResult` exposes raw document text across the Router boundary

**Impact:** `PolicyDocumentResult` is explicitly a `RouterModel`, yet it declares `text: NonBlankText | None` and `read_policy_document()` returns the entire value from an injected `PolicyDocumentSource`. Its caller can therefore serialize, retain, or place arbitrary policy/source content in Router state. This conflicts with the SPEC/ADR metadata-only boundary and the ticket's prohibition on raw Context, source, document text, prompts, paths, URIs, secrets, and PII. The fact that the supplied source is normally a plugin policy file does not make the public injected port safe: the protocol accepts any source.

**Independent reproduction:** a local source returning the non-sensitive sentinel `synthetic-unredacted-policy-content` produced `DocumentOutcome.LOADED` and exposed that exact sentinel through `result.text`.

**Evidence:** `library/workflow_router/policy_response.py:110-136` makes the raw text a Router model field; `:176-196` copies the injected source result into that field. The committed tests exercise only empty/error cases and never prove that a non-empty source cannot escape.

**Required correction:** remove raw document text from every persisted/returned Router model. If a policy source must be checked, consume it only inside an ephemeral local boundary and return a typed outcome/error plus non-content metadata; otherwise remove the unused document-reader surface. Add a regression that a unique synthetic source sentinel cannot appear in `model_dump()`, formatter output, Router state, telemetry, or an error result.

### CR-17 — The fixed reply is detached from the executable dispatch guard and the submitted baseline retains the legacy implementation grant

**Impact:** `FixedDispatchResponse` accepts any regex-shaped values and its public `render()` produces the human-facing dispatch question without a `PendingDispatchDescriptor`, receipt, reviewed handoff, or committed-artifact check. More importantly, the submitted source baseline has no Ticket-01 topology/dispatch contracts and retains the executable `TICKETS + APPROVAL_GRANTED -> IMPLEMENT` route. The new document assertion merely excludes that literal from selected Markdown; it does not change `profile.py`, `RouterEngine`, or the private Router. A valid-looking response can thus be rendered for a forged ticket, while the actual Router can still grant implementation through the retired transition. This violates AC-3 and the one-question/fail-closed policy.

**Independent reproduction:** `render_dispatch_response()` rendered a response constructed with `abcdef1`, `forged-ticket`, and `abcdef2`. Separately, the committed `test_ticket_approval_requires_metadata_handoff_on_the_indirect_client_path` passed because the private Router accepts `TICKETS + APPROVAL_GRANTED` plus a handoff and returns `IMPLEMENT`.

**Evidence:** `library/workflow_router/policy_response.py:51-75,138-173` has no Router-owned dispatch input; `library/workflow_router/profile.py:236-244` still declares the legacy advance. `tests/test_plugin_policy_and_response.py:163` scans documentation only, while `tests/test_private_router_metadata_gate.py:304-342` codifies the direct legacy grant as success. The required Ticket-01 public contract `67b049a` is cited in the ticket but is not contained in submitted baseline `ad70448`.

**Required correction:** after the Ticket-02 correction has supplied a reviewed source baseline containing the Ticket-01 contracts, bind response creation to the Router-owned pending-dispatch descriptor and its committed ticket/handoff references. Retire the direct approval-to-implementation path in the executable Profile and both direct/private entrypoints; malformed, absent, replayed, or caller-forged metadata must halt before a response or capability grant. Add direct and indirect Router tests proving the legacy event halts and only a receipt-bound descriptor can render the fixed response.

### CR-18 — Ticket 03 was implemented while the only active ticket was still under correction

**Impact:** Ticket 02's independent review returned `CHANGES_REQUESTED`, and the shared Context records that Ticket 03 is queued and starts TDD only when scheduled. The current ticket set permits one active implementation ticket. No ticket-scoped owner override records an exception. Accepting this delivery would defeat the worktree/lane isolation that this POC is meant to enforce and would force Ticket 03 to correct against an unreviewed, incomplete dependency baseline.

**Evidence:** the Ticket-02 review return on `main` is `c78af90`; `doc/context/autonomous-collaboration-audit/main.md` says Ticket 03 cannot start while the Ticket-02 correction is active; the submitted Ticket-03 range nevertheless contains source and test implementation commits.

**Required correction:** do not modify, merge, push, or resubmit Ticket 03 while Ticket 02 is in its correction lane. The automatic monitor must first receive and independently review a corrected Ticket-02 return. Then re-evaluate the eligible Ticket-03 dispatch against the resulting reviewed baseline, restart its TDD evidence as necessary, and submit a new implementation plus a docs-only handoff. This is an automatic dependency wait, not a new human approval question.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `BLOCKED` | The public models are typed, but a Router model carries raw document content. |
| Coding and architecture rules | `BLOCKED` | Formatter/policy is not composed with the Router-owned pending-dispatch contracts. |
| Logic and authorization | `BLOCKED` | Arbitrary caller-supplied response metadata renders, while the legacy executable implementation grant remains. |
| Boundary / exception handling | `BLOCKED` | Source text escapes the metadata-only boundary. |
| Security / privacy | `BLOCKED` | The injected source protocol can expose unredacted content through a serializable result. |
| Tests / smoke | `BLOCKED` | The suite passes but asserts documentation rather than the executable dispatch policy and omits the raw-text regression. |
| Dependencies | `BLOCKED` | Ticket 03 ran before the active Ticket-02 correction and without a submitted baseline containing Ticket-01 contracts. |
| SPEC / ticket / Context compliance | `BLOCKED` | CR-16 through CR-18 conflict with AC-3 and the metadata-only/one-active-ticket constraints. |
| CodeReview §2.1 path-prefix CR | `APPROVED` | Seven locator forms and null/empty/container inputs are covered at the formatter field boundary. |
| CodeReview §2.1 authority-bypass CR | `BLOCKED` | Response and legacy Router authorization remain detached from a trusted pending dispatch. |
| CodeReview §2.1 test-coverage CR | `BLOCKED` | Required mutation/negative coverage does not exercise the real Router transition or raw-source escape. |

## Return and continuation

`4d68938` and `9eda250` must not be merged, pushed, installed, or used as a policy baseline. Ticket 03 is `BLOCKED`, not a generic human wait: the active Ticket-02 correction is an automatic dependency event, and the submitted source has both a metadata-boundary failure and an executable dispatch-policy mismatch.

The control plane now remains subscribed only to the typed Ticket-02 correction return. When that committed return arrives, it must be independently reviewed first; only a passing result can make Ticket 03 eligible for a fresh, dependency-corrected implementation handoff. No new user approval is required for that re-evaluation.
