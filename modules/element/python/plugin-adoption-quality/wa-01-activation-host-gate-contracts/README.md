# WA-01 — activation and host-gate contracts

| Field | Value |
| --- | --- |
| Ticket | `TICKET-PLUGIN-ADOPTION-QUALITY-WA-01` |
| SPEC | `SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01` |
| Source | `library/workflow_router/project_adoption_contracts.py` |
| Tests | `tests/test_project_adoption_contracts.py` |
| Language | Python 3.11 / strict Pydantic |
| Status | `IMPLEMENTED` |

WA-01 defines the immutable activation request, finite host-gate classification,
tagged create/update/no-change plans and sanitized refusal results.  Its planner
is pure: adapters own target-document reads, writes and readback in later tickets.

The module remains private and is intentionally not exported from
`library.workflow_router.__init__`.
