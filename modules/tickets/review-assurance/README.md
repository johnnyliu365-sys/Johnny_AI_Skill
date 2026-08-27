# Review Assurance Tickets

| Ticket | Capability | Lifecycle / state |
| --- | --- | --- |
| [01-adversarial-review-and-deployment-readiness-policy](01-adversarial-review-and-deployment-readiness-policy.md) | Ticket-level independent adversarial audit contract, corrected same-lifetime multi-Agent review policy, and deployment readiness matrix | `APPROVED / DISPATCHABLE / CLOSURE_REVISION_02` |

## Shared baseline

- Requirement: `PRD-20260827-042` / `CHG-20260827-042`
- Specification: `SPEC-AI-WORKFLOW-REVIEW-ASSURANCE-20260827-01KZ9A1B2C3D4E5F6G7H8J9K0L`
- Context: `doc/context/review-assurance/main.md`
- ADR: `ADR-20260827-030-adversarial-review-and-deployment-readiness.md`
- Baseline: `ac68374546d3f324ca60c175014e7eb6bf2751f9`

This cluster is policy-source-only. Its ticket cannot publish a plugin, invoke an LLM provider,
create a runner/queue, access secrets or production data, run a migration, release or deploy.
