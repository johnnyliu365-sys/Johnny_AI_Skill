# ADR-20260813-008 — Guided Project Bootstrap and Adaptive Delivery

## Status

`ACCEPTED_REQUIREMENT / SPECIFICATION_IN_PROGRESS`

## Context

Johnny is an external control plane, while project source, tests, Context,
specifications, tickets and delivery evidence belong to the user's target
repository. Installing Johnny cannot identify which repository the user wants
to govern and therefore cannot safely create project files, Git worktrees or
Agent tasks during package installation.

The existing workflow also applies one detailed ceremony to every project.
That is appropriate for high-risk or cross-boundary work, but disproportionate
for a small, reversible change with an established implementation pattern.
Project size alone is not a safe classifier: a one-file authentication,
payment, migration or privileged-WebView change may be high assurance.

## Decision

### Guided initialization

1. Package installation writes only installer-owned Johnny payload, a Getting
   Started README and an initialization entry point below the Johnny-owned
   install root. It does not touch a target repository or open an Agent task.
2. The user invokes initialization for a selected target Git repository.
   Johnny first performs a read-only preflight and displays the exact planned
   target-owned documents, ignore entry, local execution root and reviewer
   capability.
3. Only one explicit initialization confirmation authorizes those bounded
   target-project writes. Initialization creates target-owned project
   artifacts and a project-local ignored `.johnny/worktrees/` execution root,
   then opens or binds one reviewer task when the host proves that capability.
4. No implementation worktree or implementation task is created at bootstrap.
   The reviewer creates or reuses one only after an approved ticket has an
   exact receipt. Only the reviewer can control that task.
5. If host task creation cannot be proved, initialization returns a finite
   blocked/manual-handoff result. The README is the recovery and manual
   bootstrap path, not the primary workflow and not evidence that automation
   occurred.

### Adaptive delivery

Johnny selects an evidence-backed `DeliveryProfile` for the project and
re-evaluates it for every ticket:

| Profile | Eligible work | Required ceremony | Default implementation resource |
| --- | --- | --- | --- |
| `COMPACT` | Local, reversible, established-pattern work with one bounded change surface, deterministic tests and no escalation trigger | Concise target-owned Context/SPEC/ticket sections; no ADR unless a decision changes; focused tests plus affected regression and independent review | One implementation owner using an economy/balanced host model tier |
| `STANDARD` | Multiple local components, a shared contract, a new adapter or moderate ambiguity, all with bounded and reversible effects | Normal Architecture/Grill/Context/SPEC/ticket closure and full affected verification | One balanced/frontier implementation owner; a second lane only for disjoint tickets |
| `HIGH_ASSURANCE` | Any hard escalation trigger, broad coupling, difficult rollback, novel architecture or production/release boundary | Full architecture alternatives, threat/failure analysis, explicit closure matrices, adversarial verification and strongest independent review | Frontier-capability implementation owner(s), limited to independently owned non-conflicting tickets |

Hard escalation triggers include authentication/authorization, Secret or
credential handling, payment, personal or regulated data, destructive data
migration, deployment/release/signing/supply-chain effects, irreversible
external effects, concurrency/distributed consistency, sandbox escape, Native
Bridge/IPC/Extension capability, and `PRIVILEGED_XSS_REVIEW`. They can raise a
profile but never lower a mandatory security gate.

Model names are host mappings, not authority. The reviewer records a finite
`ImplementationResourcePlan` containing the selected model capability tier,
lane count, evidence and budget ceiling. More implementers are allowed only
when tickets have disjoint write ownership and independent acceptance. The
default is one implementer. The default helper count is zero; a reviewer may
provision one read-only, no-code research helper only for high-search,
independently bounded work and remains its sole orchestrator.

## Consequences

- A simple project does not need the same artifact depth or verification
  breadth as a payment, migration or privileged-host project.
- Traceability is retained because even `COMPACT` has explicit requirements,
  acceptance, ownership, red/green evidence and independent review.
- Target repositories receive their own product artifacts only after explicit
  initialization; Johnny governance source remains in the plugin/install
  cache.
- Existing implementation worktrees are not moved. Migration to the new
  project-local execution root requires a separately reviewed lifecycle ticket.
- The active 05S1R repository-test migration is unrelated and continues on its
  frozen baseline.

