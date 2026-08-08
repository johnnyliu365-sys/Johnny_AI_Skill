# Code Review — Ticket 03 Dispatch-admission Correction

| Field | Value |
| --- | --- |
| Review result | `CHANGES_REQUESTED` |
| Reviewed implementation | `ea556b0` (`fix: halt dispatch without reviewed artifacts`) |
| Docs-only handoff | `cfd4e15` (`docs: hand off ticket three dispatch admission correction`) |
| Reviewed branch / owner | `codex/implementation-plugin-policy-and-response-03-rework` / Codex implementation Agent |
| Required ticket | `modules/tickets/autonomous-collaboration-audit/03-plugin-policy-and-response.md` |
| Governing specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` / AC-1, AC-3, AC-9, AC-10 |
| Review baseline | `5d55586`; submitted branch was rebased to the current control-plane baseline without merge commit or reset |
| Review date | `2026-08-08 (Asia/Taipei)` |

## Scope and evidence reviewed

- Only committed artifacts were reviewed: correction `ea556b0`, docs-only handoff `cfd4e15`, the approved SPEC/ticket/Context, and preceding Ticket-03 review returns.
- The branch merge-base is exactly `5d55586`; current ticket and review artifacts are retained. The integration-basis blocker is closed.
- CR-27 is closed for *absent* fields: direct Router and private-client paths halt before a pending descriptor when either reviewed commit field is `None`.
- The individual seven named path/URI labels are now present for both commit fields. No raw policy text, path, URI, Secret or PII is persisted by the reviewed Router models.
- Reviewer validation used `-B` and disabled pytest cache; the implementation worktree remains clean and no bytecode cache was recreated. The submitted compile evidence is recorded but was not independently rerun because `compileall` writes generated files in the separately owned worktree.

## Independent verification

| Check | Result |
| --- | --- |
| `python -B -m unittest discover -s tests` | Passed: `127` tests. |
| `python -B -m pytest -q -p no:cacheprovider` | Passed: `127` tests and `137` subtests. |
| `python -B -m mypy --strict --no-incremental library tests` | Passed: `65` source files. |
| `git diff --check 5d55586 ea556b0` | Passed. |
| Missing ticket / handoff / both commit fields | Passed: direct Router and private client halt before a pending descriptor. |
| Raw handoff containing valid-shaped forged commits | **Failed:** Router creates `wait_for_human`; its own client then renders `deadbee` / `cafe123`. |
| Ticket-required missing-value forms | **Failed:** tests use the literal string `"undefined"` and tuple `()`, not field omission plus both required `[]` and `{}` containers. |
| Handoff verification count | **Failed:** committed handoff says pytest has `130` subtests; independent run has `137`. |

## Blocking findings

### CR-29 — Router treats untrusted handoff commit metadata as reviewed artifact identity

**Impact:** the new admission guard proves only that the fields are non-null. `ImplementationHandoff` is normalized from the incoming raw request, so a caller can provide well-formed but arbitrary commits. The Router copies them into its newly created descriptor and the private client correctly renders that *forged* descriptor. This is still the CR-26 forgery through the upstream handoff boundary, not a validated reviewed-artifact binding.

**Independent reproduction:** a `TICKET_DISPATCH_REQUIRED` request with `ticket_docs_commit=deadbee` and `handoff_docs_commit=cafe123` returned `forged_handoff_plan=wait_for_human`; `PrivateRouterClient.render_dispatch_response()` then returned `forged_handoff_render=rendered` and included `deadbee`.

**Evidence:** `router.py:234-248` checks only `None` then copies the raw values. `ImplementationHandoff` and `RouterRequestEnvelope` remain caller-normalized metadata, not a control-plane artifact registry.

**Required correction:** introduce an injected, typed approved-handoff/artifact registry at the Private Router boundary. It must resolve the reviewed ticket/handoff commits by the authorized handoff and ticket identity, and Router admission must `HALT` unless that registry exactly matches the incoming metadata. The pending descriptor must be built only from registry-approved values. Add direct/private regressions where valid-shaped raw handoff commit substitutions, ticket substitutions, handoff substitutions and owner substitutions all halt before question, pending descriptor, receipt or `AUTO_RUN`; only a registered exact record may render.

### CR-30 — Required missing-value TDD cases are substituted rather than exercised

**Impact:** CodeReview §2.1 requires `null`, `undefined`, `''`, whitespace, `[]` and `{}`. The submitted test uses a literal `"undefined"` value (not field omission / undefined) and a tuple `()` (neither required empty container). This leaves two deserialization boundary shapes unverified and does not prove equivalent missing states cannot create output or authority.

**Evidence:** `tests/test_plugin_policy_and_response.py:383-395` tests `None`, `"undefined"`, `""`, whitespace and `()`, only against `ticket_docs_commit`.

**Required correction:** for each relevant ticket/handoff commit field, test field omission as the Python/JSON undefined equivalent, `None`, empty string, whitespace, `[]` and `{}`. Assert each fails closed before rendered text, pending dispatch, receipt acceptance or implementation lane grant. Retain the existing seven named path/URI cases for both fields.

### CR-31 — Docs-only validation evidence reports the wrong pytest subtest count

**Impact:** `WorkProgressReport` is the ticket's formal verification evidence. It reports `127 passed / 130 subtests`, while the independently replayed command returns `127 passed / 137 subtests`. The evidence is not reproducible as recorded and cannot support an approval.

**Evidence:** `doc/WorkProgressReport.md` PRG-20260808-008 versus the independent `python -B -m pytest -q -p no:cacheprovider` run.

**Required correction:** after source/test corrections, update the docs-only handoff with the exact rerun command and its actual count. Do not change prior historical handoff evidence; create the required new docs-only commit.

## Mandatory Code Review checklist

| Area | Result | Basis |
| --- | --- | --- |
| Strong types / clarity | `CHANGES_REQUESTED` | The types distinguish absent and formatted commits, but no type identifies a registry-approved artifact. |
| Coding and architecture rules | `CHANGES_REQUESTED` | Admission is centralized, yet trust is derived from raw handoff data rather than a control-plane source. |
| Logic and authorization | `CHANGES_REQUESTED` | CR-29 permits a valid-shaped forged handoff to render an authoritative response. |
| Boundary / exception handling | `CHANGES_REQUESTED` | `None` is fail-closed; unknown formatted values are not. |
| Security / privacy | `CHANGES_REQUESTED` | Raw policy content remains contained, but forged metadata can misstate reviewed commits. |
| Tests / smoke | `CHANGES_REQUESTED` | Required guard regressions pass, while CR-30 and the recorded validation mismatch leave mandatory evidence incomplete. |
| Dependencies | `APPROVED` | Rebase to `5d55586` preserves the current control-plane requirements and isolated Ticket-03 lane. |
| SPEC / ticket / Context compliance | `CHANGES_REQUESTED` | AC-3 still lacks end-to-end trusted reviewed-artifact admission. |
| CodeReview §2.1 path-prefix CR | `APPROVED` | Seven named path/URI boundary labels are individually asserted for both commit fields. |
| CodeReview §2.1 authority-bypass CR | `CHANGES_REQUESTED` | Missing metadata halts, but valid-shaped raw handoff substitutions bypass reviewed-artifact identity. |
| CodeReview §2.1 test-coverage CR | `CHANGES_REQUESTED` | Missing undefined/`[]`/`{}` cases and unreproducible handoff count prevent a complete coverage conclusion. |

## Return and continuation

Ticket 03 remains `IN_PROGRESS`; receipt `c569056` remains valid. `CHANGES_REQUESTED → IMPLEMENT` is automatic: the implementation owner keeps the existing rebased Ticket-03 rework branch, creates CR-29/CR-30 red tests, adds the smallest typed approved-artifact registry boundary, verifies it, and records the exact validation counts in a new docs-only handoff. No human confirmation, merge, push, installation, deployment, host configuration, target-project mutation, Secret, provider or other-ticket action is authorized.
