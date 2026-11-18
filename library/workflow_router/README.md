# Workflow Router contracts

The flow engine, the private router, the profile and the router telemetry were retired
(REQ-20261103-043 wave 3, owner decision 2026-11-18). What stays is the typed vocabulary
the receipt and dispatch families use.

- `contracts.py`: strongly typed router values (`RouterState`, `RouterEvent`, `RouterDecision`, `ContextView`, the Wayfinder gap types).
- `wayfinder_gap.py`: the Wayfinder two-round information-gap rule as one function, `decide_wayfinder_gap`.
- The remaining `*_contracts.py` modules, `artifact_tree.py`, `library_selection.py`, `requirement_lineage.py` and `supervision_policy.py` serve the cross-lifetime bridge that ticket 66 retires.
