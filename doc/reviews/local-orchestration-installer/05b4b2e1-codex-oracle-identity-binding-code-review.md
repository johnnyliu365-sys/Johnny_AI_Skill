# Ticket 05B4B2E1 Codex Oracle Identity Binding Code Review

## Review decision

`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION`

The immutable return correctly maps a valid exact registration request to the
staging oracle identity and passes its submitted verification. One bounded
admission defect remains under the frozen I5/I8 responsibility: injected extra
state on most nested request models is discarded by rebuilding and is then
accepted. No requirement change, new branch or new worktree is required.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e1-codex-oracle-identity-binding`; `CLOSURE-LOCAL-INSTALL-T05B4B2E1-01`; I1-I8 |
| Owner / branch | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; `codex/implementation-codex-oracle-identity-binding-05b4b2e1` |
| Dispatch / chain | `97cc49a3b2fec25b9b6e2dbc9f9d1794808a2c09 -> 25b3f9c6541df00d95679233056fcdcf30433a50 -> 6ee9b4a96a5a1720c04845b9edb115d689472f34` |
| Scope | Implementation changes exactly the two authorized staging/test paths; handoff changes only `doc/WorkProgressReport.md`. The submitted worktree is clean and the existing three-worktree topology is unchanged. |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| I1 first red | PASS: the committed evidence records `ModuleNotFoundError` for the missing staging module before production existed. |
| I2 rebuilt request | PASS for the declared request fields: the accepted value is rebuilt and no declared nested object identity is retained. |
| I3 identity fields | PASS: marketplace, plugin, plugin ID, version and auth policy come from the rebuilt request; fixture labels are named staging-only constants. |
| I4 logical paths | PASS: Windows joining uses the fixed logical root and exact owned relative locators; no host path or environment value is read. |
| I5 invalid state | **FAIL — CR-159:** independent probes injected an undeclared attribute into exact `preflight`, `installation_id`, `root`, `marketplace`, `plugin`, `marketplace_source`, `source_locator` and `installed_locator` models. Every value was returned as `OracleIdentityBound`; only the separately probed auth-policy injection was rejected. The outer `model_validate(value)` call reuses/rebuilds nested exact instances without proving their original state shape, so nested extra state is erased rather than rejected. |
| I6 no effects | PASS: no command, oracle, port, callable, environment, filesystem, network, target-project or Agent authority is exposed. |
| I7 source discipline | PASS: no `Any`, `type: ignore`, broad catch, optional authority, dynamic member discovery, signature inspection or historical-source reuse. `XSS_NOT_APPLICABLE`. |
| I8 evidence | PASS for the submitted three required reversals and extra top-level guard reversal. **FAIL for CR-159:** committed coverage does not exercise every nested exact model with injected state and therefore cannot prove I5's complete boundary. |
| CodeReview §2.1 | Class 3 fails through CR-159 admission of state outside the exact reviewed request shape; class 7 requires committed regressions plus a guard reversal. Class 8 is `XSS_NOT_APPLICABLE`. |

## CR-159 bounded correction

CR-159 is `IMPLEMENTATION_DEFECT` under existing I5/I8. Keep the same ticket,
implementation owner, worktree, branch, allocation, receipt and correlation.
Previous implementation and handoff commits remain immutable evidence.

- Add a typed recursive state-shape guard after exact integrated type admission
  and before binding. It must prove that the original request and every nested
  exact Pydantic model contain only their declared state. It must not invoke a
  caller protocol, dynamic member discovery, representation or serialization.
- Add a committed table that independently injects extra state into the outer
  request and every nested model used by the request: preflight,
  installation ID, root, marketplace, plugin, marketplace source, attempt ID,
  expected version, source locator, installed locator, digest, expected auth
  policy and expected plugin ID. Every cell must finitely return
  `OracleIdentityBindingRejected` without a partial identity or effect.
- Reverse the recursive nested-state guard once. The named committed table
  must turn red for the nested cells, followed by exact source/test blob
  restoration and a green rerun.

Only the original two implementation paths and a later WPR-only handoff may
change. No E2-E6 work, branch/worktree creation, new dependency, live Codex,
host/filesystem/network/target-project effect, staging push, package, release
or deployment is authorized.

## Disposition

`CHANGES_REQUESTED`. CR-159 is the complete blocking batch for revision 02. A
same-branch additive correction may be dispatched only after this review and
its correction handoff are committed.

## Final correction review

| Gate | Result |
| --- | --- |
| Immutable correction | PASS: `6ee9b4a96a5a1720c04845b9edb115d689472f34 -> ef80813b223b53f638b7c263054a6f03045c28a7 -> 658f3d7e886d1fd5ddca7bc2c39a8cd887afa4d0`; correction changes only the original two E1 paths and handoff changes only WPR PRG-277. |
| CR-159 | PASS: fixed-field recursive checking covers the exact request, preflight, all five preflight children and all seven other request value objects. Undeclared dictionary state, Pydantic extra/private state and altered field sets reject before identity binding. |
| Independent verification | PASS in a Unicode-safe repository-external snapshot: focused/relevant 27/27, full serial 370/370, strict mypy 132 files and in-memory compile 132 files. An additional 42-cell matrix injected extra/private/field-set state across all 14 nodes and every cell returned the finite rejection. |
| Evidence truthfulness | PASS: reviewer reduced the recursive guard to its outer request check. The committed matrix then failed for all 13 nested nodes with `OracleIdentityBound`; restoring exact source SHA-256 `272C5BCBBA20AD4757B5FB6EF540A96EF9E03D5A3F4D81CBBAB0092A5AD5D784` made the named test green. |
| CodeReview §2.1 / XSS | Classes 3 and 7 PASS after correction. Class 8 remains `XSS_NOT_APPLICABLE`: no renderer, DOM/HTML, JavaScript context or privileged bridge exists. |

## Final disposition

`APPROVED / READY_TO_MERGE`. CR-159 is closed. Guarded integration may merge
only exact handoff `658f3d7e886d1fd5ddca7bc2c39a8cd887afa4d0`, preserving this
approval as first-parent control history. E2/E3 remain undispatched until the
integration and post-merge readback pass.
