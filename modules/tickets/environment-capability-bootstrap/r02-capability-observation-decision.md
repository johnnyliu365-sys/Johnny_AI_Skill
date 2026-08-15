# Revision 02 Environment Capability Admission Decision

| Field | Value |
| --- | --- |
| Artifact / authority | `TAD-ENV-R02-01`; Environment Capability Bootstrap Revision 02, EC-02, EC-09, EC-10 and EC-10A |
| Requirement / Context / ADR | `PRD-20260816-025` / `CHG-20260816-025` / `CONTEXT.md` seal and `doc/context/environment-capability-bootstrap/main.md` / `ADR-20260816-014` |
| Baseline / decision | `b6183658b7c16f9b0723482cee62fe89e677ebf3` / `UPSTREAM_DECISION_REQUIRED` |
| Effects / XSS | Discovery, acquisition, activation, enforcement and removal are not admitted; `XSS_NOT_APPLICABLE` |

## Missing contract that blocks vertical tickets

The SPEC defines plans, evidence, resource plans and named ports, but not the typed normalized
`CapabilityDiscoveryPort` observation, project-constraint readback, capacity observation,
planner decision/result or resource-enforcement attachment result. The exact LIGHT/STANDARD caps
cannot be calculated or rejected from an undeclared available-CPU/RAM/GPU/VRAM input model.

The named ports have responsibilities but no public input/output/error algebra. A planner ticket
would have to invent version-constraint normalization, capacity units, local-reservation failure
precedence and the relationship between a port readback and `CapabilityEvidence`; adapter work
would additionally cross acquisition/process/installation high-assurance effects.

## Required route

`UPSTREAM_DECISION_REQUIRED / ENVIRONMENT_OBSERVATION_AND_PLAN_RESULT_CONTRACT_UNDEFINED`.
Architecture must seal finite observation, plan-result and enforcement-result contracts before a
pure planner can receive Python 3.11/mypy-strict source locations, finite first-red TDD, resource
binding and typed return. No installation, process, target, tool, credential or external effect
is authorized by this decision.
