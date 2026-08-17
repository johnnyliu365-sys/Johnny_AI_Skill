# 04 — Profile-bound CLI preflight

| Field | Binding |
| --- | --- |
| SPEC / AC / requirement | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` Revision 02 / AC-04, AC-05 / `PRD-20260802-004` / `CHG-20260802-004` / `REQ-20260802-004` |
| Context / implementation baseline / dependency | `ctx-plugin-distribution-r02` / `7a0d276c1acccfe07db230c6bb6c0d700cee8819` / Ticket 02 integrated at `b5e73655eae8f6995cab803e1be276ced492dcff` |
| Closure | `CLOSURE-PD-04-R03-02`; replaces the unbound R03-01 ticket with the exact Profile, CLI request/result and probe contracts already closed by SPEC Revision 02 |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior task is retired and has no authority over this ticket |
| Implementation allocation | ticket ref `ticket-pd04-profile-cli-01`; role `role-impl-pd04-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01`; branch `codex/plugin-distribution-04-profile-cli` / `branch-pd04cli-01`; receipt `receipt-pd04-20260817-001`; correlation `corr-pd04-20260817-001` |
| Dispatch mode | Owner-authorized manual bootstrap forwarding by the current reviewer; this ticket must not claim a live Router dispatch, host subscription, heartbeat, polling, automation or target effect |
| Implementation language / strict checker | Python 3.11.9 / `python -m mypy --strict library/workflow_router/profile.py library/local_orchestration/johnny_router_contracts.py library/local_orchestration/johnny_router_cli.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `TICKET_REFROZEN / READY_LOW_MODEL / DISPATCH_REQUIRED` / `XSS_NOT_APPLICABLE` |
| Boundary classification | In-memory request/profile/probe and stdout JSON only; no import-time or runtime process, filesystem, Git, host, network, runner, receipt-store, target-project or provider effect |

## Sole closure and public contracts

`build_plugin_distribution_profile() -> ProjectWorkflowProfile` is added only to
`library/workflow_router/profile.py`. It starts from `build_router_poc_profile()` and preserves
its `delivery_stage`, `router_control_reference`, `halt_return_contract` and exact
`transition_rules`. It replaces only these project-owned bindings:

| Role / metadata | Exact value |
| --- | --- |
| profile | `profile_id="plugin-distribution-poc-r02"`, `profile_version="2"`, `shared_context_ref="ctx-plugin-distribution-r02"`, `architecture_owner_capability_ref="cap-plugin-distribution-architecture-owner-r02"` |
| architecture owner | `model-gpt-5-6-sol-xhigh-architecture-r02`, `cap-plugin-distribution-architecture-r02`, `evidence-owner-approved-plugin-architecture-r02`, `ACTIVE` |
| supervisor reviewer | `model-gpt-5-6-terra-high-senior-r02`, `cap-plugin-distribution-ticket-review-r02`, `evidence-owner-approved-terra-senior-r02`, `ACTIVE` |
| implementation owner | `model-gpt-5-6-luna-xhigh-implementer-r02`, `cap-plugin-distribution-implementation-r02`, `evidence-owner-approved-luna-implementer-r02`, `SLEEPING` |
| research helper | `model-gpt-5-6-luna-readonly-helper-r02`, `cap-plugin-distribution-readonly-research-r02`, `evidence-reviewer-owned-helper-policy-r02`, `SLEEPING` |

Create `library/local_orchestration/johnny_router_contracts.py` using frozen, strict Pydantic
models (`extra="forbid"`, no `Any`, no dynamic map) with this complete public boundary:

```text
JohnnyRouterOperation = PREFLIGHT | REGISTER_PROJECT | DETACH_PROJECT
                      | REGISTER_SUBSCRIPTION | CANCEL_SUBSCRIPTION
                      | ROUTE_EVENT | STATUS | UNINSTALL
JohnnyRouterRequest = {
  operation: JohnnyRouterOperation,
  expected_profile_id: Literal["plugin-distribution-poc-r02"],
  expected_profile_version: Literal["2"]
}
PreflightProbe = { git_available: bool, python_version: tuple[int, int, int] | null }
JohnnyRouterResultStatus = SUCCEEDED | BLOCKED | CAPABILITY_UNAVAILABLE
                              | NOT_FOUND | CONFLICT | HALTED
JohnnyRouterResultCode = PREFLIGHT_PASSED | UNKNOWN_OPERATION | INVALID_ARGUMENTS
                      | STALE_PROFILE | INVALID_PROBE | GIT_UNAVAILABLE
                      | PYTHON_UNAVAILABLE | PYTHON_INCOMPATIBLE
                      | OPERATION_UNAVAILABLE | NOT_FOUND | CONFLICT | HALTED
```

`JohnnyRouterResult` is the closed discriminated union of frozen strict result values. Every
member has `status`, `code`, `operation: JohnnyRouterOperation | null`, and the expected profile
ID/version. Only these Ticket 04 combinations are constructible:

| Condition | Result |
| --- | --- |
| exact `PREFLIGHT`, exact profile, Git available and Python `>=3.11,<3.14` | `SUCCEEDED / PREFLIGHT_PASSED / PREFLIGHT` |
| unknown argv operation, wrong argv shape/type, stale profile, malformed/bypassed probe | `BLOCKED` with respectively `UNKNOWN_OPERATION`, `INVALID_ARGUMENTS`, `STALE_PROFILE` or `INVALID_PROBE`; `operation=null` only for unknown/invalid argv |
| Git unavailable, Python absent or incompatible | `CAPABILITY_UNAVAILABLE` with respectively `GIT_UNAVAILABLE`, `PYTHON_UNAVAILABLE` or `PYTHON_INCOMPATIBLE` |
| one of the seven valid non-`PREFLIGHT` operations | `CAPABILITY_UNAVAILABLE / OPERATION_UNAVAILABLE / <that operation>` |
| `NOT_FOUND`, `CONFLICT` or `HALTED` | exact matching status/code; declared public union members only and never returned by Ticket 04 |

`JohnnyRouterPreflightPort` has exactly `probe() -> PreflightProbe`; a `PreflightProbe` is
round-tripped through its ordinary validator before use. `main(argv, ports)` in
`library/local_orchestration/johnny_router_cli.py` accepts only the positional closed request
shape `(OPERATION, "plugin-distribution-poc-r02", "2")`, calls the profile builder, writes exactly
one canonical `JohnnyRouterResult` JSON value to stdout, and returns that typed result. The
runtime preflight port is called only for an exact, non-stale `PREFLIGHT`; stdout is not a
preflight-port call. Unknown/stale input and all non-preflight operations must be resolved before
the probe. Importing either new local-orchestration module or `profile.py` performs no effect.

Writable scope: `library/workflow_router/profile.py`,
`library/local_orchestration/johnny_router_contracts.py`,
`library/local_orchestration/johnny_router_cli.py`,
`tests/test_plugin_distribution_profile.py` and `tests/test_plugin_distribution_cli.py`. No
launcher, package root export, composition root, runner, receipt-store or external effect.

## TDD, verification and return

Closure `CLOSURE-PD-04-R03-02`:

- C1: Profile builder preserves base transitions/contracts and binds all four exact role rows.
- C2: the exact preflight request emits one canonical success JSON result.
- C3: unavailable Git, absent Python and incompatible Python return the named finite result.
- C4: unknown argv, wrong shape, stale ID/version, malformed/bypassed probe and all seven deferred
  operations return their exact finite result; unknown/stale/deferred cases have zero preflight-port
  calls.
- C5: importing each new module and `profile.py` is silent; stdout is empty and no probe is called.

First red: `python -m pytest -q tests/test_plugin_distribution_cli.py -k test_cli_unknown_operation_returns_blocked_without_preflight_port_call`.
Verify with `python -m pytest -q tests/test_plugin_distribution_profile.py tests/test_plugin_distribution_cli.py`,
the strict checker above and `python -m pytest -q`; in-memory compile every Python source; then
reverse-mutate the closed argv operation-admission guard so C4 turns red, restore exact bytes and
rerun the focused closure. Remove every test/cache/bytecode residue before commit.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`, `BLOCKED -> HALT` with its
failed cell and preserved branch state, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED` with the
conflicting frozen reference. A need for a new operation, profile field, port, output field or
effect boundary is `CHANGE_DETECTED`; it does not expand this ticket.

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation / integration | `09ec98d0194f3bc84bbb6c0b182975e695682d8f` / `4fd29cdcb92a6afe304ebc5cd2d4a6a5f337136d` |
| Independent closure | focused `7 passed, 14 subtests`; full `734 passed, 2,537 subtests`; strict `mypy --no-incremental` passed for the three named source files; 206 Python files compiled in memory. |
| Boundary checks | Public DTO/result-union ordinary construction and JSON round-trip passed; a fresh `python -B` process imported all three modules with empty stdout/stderr; C2--C4 probe-call boundaries passed. |
| Reverse / residue | Owner's named C4 operation-admission guard turned red and was byte-restored; reviewer rerun found `POST_TEST_CLEAN=PASS` with no cache/bytecode residue. |
| Review | `APPROVED`; no XSS, host, network, filesystem, Git, runner, receipt-store or target-project effect was introduced. |

Canonical Git-blob SHA-256: `profile.py` `D40B6E141F3655849F521C6883F15F3CB934FE5DA750AAB0C3F7416BDC80534D`; `johnny_router_contracts.py` `8E6CEB3FAC266EB9EEDE5BEC88645606A475AFB7BD0723D99D0DD542DF49168D`; `johnny_router_cli.py` `CBC87920C83973B1F57EBCC63D6846DBDA7499538A51EA81A4AEE0622FFA3AEA`; `test_plugin_distribution_profile.py` `71DC8CF35E0BEDD74DB0D79CA43D7D181A9D976B7B24D3E433F13C1906FC1C60`; `test_plugin_distribution_cli.py` `C03BDA311A163F0AD354505A499240A4058A10D11E13236D1B672D43ADB2F666`.
