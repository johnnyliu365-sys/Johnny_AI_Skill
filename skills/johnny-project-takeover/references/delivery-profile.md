# Delivery profile and lifecycle

Read this reference during intake, delivery-stage changes, resource planning, POC freeze or
staging admission. Do not load it for an implementation ticket whose profile and baseline
have already been admitted.

## Delivery maturity

`delivery_stage` describes the product promise:

- `POC` validates the smallest explicit feasibility assumptions and ends in a GO/NO-GO.
- `MVP` requires an approved change record and a new Wayfinder pass over MVP value, risk,
  scope and acceptance.
- `COMMERCIAL` requires an approved change record and a new Wayfinder pass over operational,
  security, support, observability, data-governance, legal and service-level commitments.

Do not infer a maturity upgrade from chat or from a successful POC. Router state and the
approved Project Workflow Profile must agree or the route suspends.

## Workflow intensity

`delivery_profile` describes the assurance needed by the current project or ticket:

- `COMPACT`: one bounded, reversible change using an established pattern and deterministic
  verification. Requirements, AC, owner, first red/green evidence and independent review
  still apply.
- `STANDARD`: multiple local components, a shared contract, a new adapter or moderate
  uncertainty.
- `HIGH_ASSURANCE`: high impact, difficult recovery, new architecture or a formal external
  boundary. Include alternatives, threat/failure matrix and adversarial verification.

Assess change surface, coupling, uncertainty, failure impact, reversibility, verification
environment and external effects. Missing evidence never defaults to `COMPACT`. Authentication,
authorization, secrets, payment, regulated data, destructive migration, release/deployment,
signing/supply chain, irreversible effects, distributed consistency, sandbox escape,
privileged host capability and privileged XSS force `HIGH_ASSURANCE`. Project size, file count,
line count and model name never lower the profile.

## Resource plan

Default to one implementer and no helper. Use zero implementers for read-only/document-only
work. Add parallel lanes only when ownership, files and AC are disjoint and the integration
order is explicit. A high-search, low-authority, zero-write-conflict task may receive one
reviewer-owned read-only/no-code research helper. The implementation owner never controls a
helper or another Agent. Model tier is a cost/capability choice, not authority.

Reassess when requirements, risk, security/XSS classification, coupling or verification
results change. Upgrade automatically when evidence requires it; downgrade only with recorded
evidence and without removing required tests or findings.

## POC freeze and staging

After independent POC review and owner acceptance, create a typed `StagingTransitionPlan`
bound to repository identity, accepted POC commit, expected staging ref, frozen version record
and plan digest.

- Without unique review, acceptance and commit identity, return
  `WAIT_FOR_HUMAN / POST_POC_BASELINE_REQUIRED` and create no feature worktree.
- A local staging ref may be created or verified-fast-forwarded only to the accepted POC or a
  verified successor. Never reset, force, delete, overwrite the frozen POC or resolve a
  conflict silently.
- Remote staging publication is a separate effect requiring authority, remote-history check
  and exact SHA readback.
- Every later branch/worktree is admitted from the read-back staging SHA. Wrong ref, stale or
  dirty base, divergence, repository mismatch or wrong ancestry halts before effect.
- Staging integration is not release. Packaging requires a separate promotion gate.
- Staging is not an installation/effect sandbox. Host, installation, removal, migration and
  other effects require a receipt-bound disposable environment.
