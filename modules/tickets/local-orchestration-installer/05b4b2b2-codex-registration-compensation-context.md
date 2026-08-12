# 05B4B2B2 — Codex Registration Compensation Context Binding

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 compensation authority seam |
| State | `APPROVED / READY_TO_MERGE` |
| Closure | `CLOSURE-LOCAL-INSTALL-T05B4B2B2-01` / B1-B7 |
| Dependency | 05B4B2B1 approved and integrated by `0c4476f8d40b53292ea69d0daec084860beeaa03` |
| Planned owner | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; one new ticket branch in that same worktree, no new worktree |
| Language / XSS | Python 3.11 strict Pydantic/mypy / `XSS_NOT_APPLICABLE` |

## Ticket-defect finding and one observable outcome

The planned B2D composition requires an exact compensation manifest containing
plugin ID, version, installed locator, auth policy and digest. A terminal
`CodexRegistrationCompensationRequired` currently retains only its journal and
plan, which do not contain those fields. Accepting them later from a caller
would permit target substitution at the removal boundary.

Extend only the pure terminal compensation decision so it also retains the
exact already-validated `CodexRegistrationPortRequest` from which its journal
and plan were built. Recursively validate that the request, journal and plan
describe one identical attempt. This ticket invokes no effect and does not
change proof decisions or started-add recovery, which already retains its exact
registration request.

## Frozen design

- Add required field `request: CodexRegistrationPortRequest` to
  `CodexRegistrationCompensationRequired`; never make it optional and never
  synthesize missing values.
- `_compensation_required` must place the exact current validated registration
  request into the terminal decision. The decision validator must require exact
  concrete request/journal/plan types and rebuild their trusted forms.
- Bind request preflight and attempt ID exactly to the journal. Rebuild the
  compensation plan from that journal and request and require the supplied plan
  to match type, status, ordered steps, journal, request, attempt and identity.
  Every request field must retain its exact recursively validated type and
  value. Fields repeated by journal/plan must match those structures. Fields
  carried only by the request (expected plugin ID/version, installed locator,
  auth policy and digest) are not self-authenticating public data: their
  authority comes only from the opaque one-shot B2B1 claim that owns the
  original terminal decision. B2D must consume that live claim and must never
  accept a raw terminal DTO, caller replacement request or caller-built
  compensation manifest as authority.
- Proof-required and blocked branches remain behaviorally unchanged. No
  compensation capability, composition, removal or proof operation is invoked.
- Existing B2B1 recursive claim rebuild must continue to accept an exact
  compensation decision and reject constructed-invalid nested context without
  adding a new claim or settlement API.

## Acceptance Closure Set

| ID | Finite completion rule |
| --- | --- |
| `B1` | First red asserts terminal compensation context is absent from the integrated model/return; production is unchanged during red. |
| `B2` | Every exact terminal compensation path carries the complete exact `CodexRegistrationPortRequest` already used by the reducer; proof and blocked paths remain unchanged. |
| `B3` | Exact recursive validation binds request, journal and rebuilt plan. Every request field requires its exact closed type; request fields repeated by journal/plan must match; plan identity/status/order and nested constructed-invalid shapes are rejected rather than normalized or guessed. Valid but different request-only values cannot be authenticated by a public DTO and therefore are never an authority boundary. |
| `B4` | Exact B2B1 terminal compensation claim consumption still returns one rebuilt claim-owned decision with the same complete bound context; altered live claim binding and constructed-invalid nested context cannot pass claim rebuilding. A raw or caller-constructed terminal DTO, including one with valid replacement request-only values, is rejected by claim consumption. Started-add recovery remains unchanged. |
| `B5` | Source is pure and invokes zero registration/compensation/proof/oracle/process/filesystem/host/network/target-project effects; no new public capability, registry, optional field, `Any`, `type: ignore`, broad catch or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| `B6` | Independently reverse request retention, request/journal equality and rebuilt-plan equality. Each named committed test turns red and exact blobs restore. |
| `B7` | Focused reducer plus settlement-authority tests, full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology and tracked/ignored/cache readbacks pass. |

## Exact source and return

1. Existing `library/local_orchestration/codex_registration_reducer.py`.
2. Existing `tests/test_codex_registration_reducer.py`.

All other source/tests and package exports remain read-only. The B2B1 focused
suite is a mandatory read-only regression. No numeric line limit is an
acceptance criterion. Return one exact two-path implementation commit, then one
`doc/WorkProgressReport.md`-only handoff reserved as `PRG-20260812-253`.

No B2C/B2D/B2E/05C work, live Codex, process, filesystem, host, network,
target-project mutation, other Agent, review, integration, push, release or
deployment is authorized.

## Planned dispatch binding

| Field | Value |
| --- | --- |
| Project / closure | `prj-local-orchestration-installer-poc-20260808` / `CLOSURE-LOCAL-INSTALL-T05B4B2B2-01` |
| Handoff | `hnd_local_orchestration_install_05b4b2b2_20260812` |
| Allocation / receipt | `aln_local_orchestration_install_05b4b2b2_20260812` / `rcpt_local_orchestration_install_05b4b2b2_20260812` |
| Correlation / question | `corr-local-orchestration-install-05b4b2b2-20260812` / `q-local-orchestration-install-05b4b2b2-20260812` |
| Side context | `scx-local-orchestration-install-05b4b2b2-20260812-01` |
| Owner / lane | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; later create only `codex/implementation-codex-registration-compensation-context-05b4b2b2` from the exact dispatch commit. |

Freeze is not dispatch. A later dispatch registry must bind the exact freeze
commit and verified clean lane before implementation starts.

## Dispatch registry

| Field | Value |
| --- | --- |
| Reviewed freeze | `2183afb3956744163c22cb16f1c2285d0aa82de8`; exact B1-B7; `XSS_NOT_APPLICABLE` |
| Delivery authority | Project-owner standing instruction to continue approved work; `IMPLEMENTATION_DISPATCH_CONFIRMED` for this ticket only |
| Lane readback | Task is idle; existing `workflow-implementer-2` is clean at exact submitted HEAD `2f9968ccb3825a77d26202c008c0cc6ea94cc3ed`; exactly three existing worktrees |
| Branch | Create only `codex/implementation-codex-registration-compensation-context-05b4b2b2` from this exact dispatch-registry commit in the same worktree; no new worktree |
| Binding | `hnd_local_orchestration_install_05b4b2b2_20260812`; `aln_local_orchestration_install_05b4b2b2_20260812`; `rcpt_local_orchestration_install_05b4b2b2_20260812`; `corr-local-orchestration-install-05b4b2b2-20260812`; `q-local-orchestration-install-05b4b2b2-20260812`; `scx-local-orchestration-install-05b4b2b2-20260812-01` |

This is the single dispatch. Only the exact two implementation paths and later
WPR-only PRG-20260812-253 are writable in this lane.

## Review correction and decision

Independent review classified CR-156 as a `TICKET_DEFECT`: the original B3
wording required a public DTO to distinguish two separately valid values for a
field that exists nowhere else in that DTO. No deterministic validator can do
that without external authority. The correction above makes the already
integrated B2B1 opaque one-shot claim the sole authority boundary; raw DTOs do
not satisfy its consumer. This is not a product requirement change and requires
no implementation rewrite.

Terminal independent review of implementation `7603d6b75a665f9cbf4e06b0afe7e0421fb912ff`
and WPR-only handoff `e12ee8bef24172db517bfb346bd7fd4f972a2759`
is `APPROVED / READY_TO_MERGE` under corrected B1-B7.
