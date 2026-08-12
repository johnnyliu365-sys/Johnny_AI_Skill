# 05B4B2B2 — Codex Registration Compensation Context Binding

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / unchanged AC-01, AC-02, AC-07 and AC-08 compensation authority seam |
| State | `FROZEN / DISPATCH_PENDING` |
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
  Mutation or substitution of installation, root, marketplace, source, plugin,
  expected plugin ID, version, installed locator, auth policy, digest, attempt,
  journal state or plan must finite-fail validation.
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
| `B3` | Exact recursive validation binds request, journal and rebuilt plan. Each request field, attempt, journal state, plan identity/status/order and nested constructed-invalid shape is rejected rather than normalized or guessed. |
| `B4` | Exact B2B1 terminal compensation claim consumption still returns one rebuilt decision with the same complete bound context; an altered nested context cannot pass claim rebuilding. Started-add recovery remains unchanged. |
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
