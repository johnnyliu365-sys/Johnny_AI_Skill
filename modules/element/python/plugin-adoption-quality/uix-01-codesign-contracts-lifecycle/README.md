# UIX-01 UI co-design contracts and lifecycle

Status: implemented.

The production implementation is the private, strict, effect-free module
`library/workflow_router/ui_codesign_contracts.py`. Its acceptance and reverse-
mutation evidence is in `tests/test_ui_codesign_contracts.py`.

This element owns bounded schemas and the deterministic reducer for the
brief-to-owner-acceptance lifecycle. It intentionally has no renderer,
provider, browser, filesystem, process, network, environment, or host effect.
