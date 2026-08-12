# Ticket 05B4B2B Codex Registration Forward Composition Code Review

## Review decision

`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED`

The submitted implementation has exact ancestry and scope, and its committed
focused/full suites pass. Independent adversarial review nevertheless found two
effect-boundary defects inside the frozen F2/F7 closure. Both are bounded
implementation corrections; neither changes the requirement or public design.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2b-codex-registration-forward-composition`; `CLOSURE-LOCAL-INSTALL-T05B4B2B-01`; F1-F8 |
| Owner / branch | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; `codex/implementation-codex-registration-forward-05b4b2b` |
| Dispatch baseline | `770f04f101d3625422e9531001db19ed05933d6f` |
| Implementation | `b6349d5486b81c0c97040fcc16bf14e1c69c1dcd`; exactly the new forward module and focused test |
| Docs-only handoff | `031c2ff0585b59510d1ee5746fd9acc60a837eaf`; only `doc/WorkProgressReport.md`, unique PRG-20260812-226 |
| Binding | `hnd_local_orchestration_install_05b4b2b_20260812`; `aln_local_orchestration_install_05b4b2b_20260812`; `rcpt_local_orchestration_install_05b4b2b_20260812`; `corr-local-orchestration-install-05b4b2b-20260812` |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| Ancestry / scope / residue | PASS: `770f04f -> b6349d5 -> 031c2ff`; implementation adds exactly the two authorized paths, handoff changes WPR only, the submitted lane is clean, and the three-worktree topology is unchanged. |
| F1 first red | PASS: the WPR records the exact absent-module `ModuleNotFoundError` before production creation. |
| F2 capability admission | PASS for ordinary and submitted adversarial capability cells: exact capability/metadata/`MethodType`/common-owner/raw-function checks rebuild the capability without invoking an operation. **FAIL for constructed coordinator authority as CR-151.** |
| F3-F6 forward behavior | PASS for committed and independently rerun cells: fresh, marketplace and plugin dispatch in exact order; duplicate/re-entry/foreign/stale blocks, return classification, twelve exception propagation cells and conservative recovery remain green. |
| F7 constructed-invalid / transfer safety | **FAIL — CR-151 / IMPLEMENTATION_DEFECT:** `begin`, `execute` and `recovery` access `_transaction`/`_capability` without the exact authority validation used by `metadata`. A coordinator made with `object.__new__`, a foreign token and caller-supplied exact-shaped fields can begin and execute; the independent probe returned `CodexRegistrationNextReadyPhase` and recorded `['FRESH']`, while `metadata()` correctly rejected the same object. The effect entry therefore bypasses the factory and authority gate. |
| F7 caller-protocol safety | **FAIL — CR-152 / IMPLEMENTATION_DEFECT:** `__reduce_ex__` calls `operator.index(protocol)` before raising `TypeError`. An `IndexTrap.__index__` probe raised the caller's `RuntimeError('INDEX_TRAP')` and recorded one invocation. Serialization refusal must not inspect or execute caller protocol. |
| F8 evidence truthfulness | PASS for the five submitted reversals, but they do not cover CR-151 or CR-152. The correction must add named first-red regressions and independent authority-gate/protocol-trap reversals. |
| Independent verification | PASS in repository-external immutable export `DE60DC08E8841BD6CA290046F85CE4DE20C214B86086E7C7EE6A62AAECD55CC9`: focused 16/16 and full 310/310. Source sentinel found no `Any`, `type: ignore`, broad catch or forbidden effect import. The two direct adversarial probes above fail the frozen contract. |
| CodeReview section 2.1 classes 3 and 7 | FAIL only for CR-151/CR-152: an alternate effect route lacks authority validation, and the committed fabricated-input tests did not cover constructed coordinator execution or caller-controlled pickle protocol. |
| XSS review | `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript execution context or privileged JavaScript bridge/API is introduced. |

## CR-151 / CR-152 bounded correction

CR-151 and CR-152 form one same-closure correction batch. Add one private exact
authority validator (or an equivalent single gate) and invoke it before any
state access or effect in `begin`, `execute` and `recovery`; metadata/repr must
remain on the same gate. Missing, foreign or wrong-type token, capability or
transaction slots must fail finitely and trap-free before transaction mutation
or operation invocation. Do not attempt to make `object.__new__` impossible;
make every public authority-consuming entry point reject its products.

`__reduce_ex__` must reject directly without `operator.index`, conversion,
comparison, hashing, representation or any other inspection of `protocol`.
Add first-red cells for constructed-invalid `begin`/`execute`/`recovery` and an
`__index__` trap, then reverse the common authority gate and the direct
serialization rejection independently. Preserve the existing five reversals
and all F1-F8 behavior.

The correction may change only the existing forward module and focused test,
followed by one WPR-only handoff. It is additive on the same ticket, task,
worktree, branch, allocation, receipt and correlation. No reset, amend, new
branch/worktree, public contract, B2C-B2E/05C work, live effect, integration,
push, release or deployment is authorized.

## Disposition

`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED`. Retain immutable
implementation `b6349d5` and handoff `031c2ff` as evidence. The only legal
continuation is the bounded CR-151/CR-152 correction above.

## First correction review — CR-153

The additive return `031c2ff -> cf54940 -> 35fc40f` has exact two-path and
WPR-only scopes, is clean, preserves the three-worktree topology and passes in
an immutable export: CR regressions 3/3, focused 19/19 and full 313/313. It
closes CR-152: `__reduce_ex__` raises direct `TypeError`, and an independent
`IndexTrap` records zero invocations.

CR-151 is not yet closed. The new `_CoordinatorAuthority` is validated only by
exact type plus fields that point back to the coordinator, capability and
transaction. An independent probe created both the coordinator and an
exact-shaped `_CoordinatorAuthority` with `object.__new__`, set those four
identity relationships, and received `CodexRegistrationReadyLease` followed by
`CodexRegistrationNextReadyPhase`; the admitted fake recorded one `FRESH`
effect. No private constructor or factory provenance was required.

This is CR-153 / `IMPLEMENTATION_DEFECT` under the same F2/F7 requirement:
field-shape self-consistency is not construction authority. The bounded
correction must make the public coordinator constructor reject unconditionally
and have the factory register each live exact coordinator in a private
process-local provenance registry. The registry record, not coordinator- or
caller-constructed fields, must bind the exact coordinator instance to its
capability and transaction. Every public authority-consuming entry must check
that record before state/effect. Registry access must be synchronized,
identity-based, finite and caller-protocol-free; it must not accept an
unregistered exact-shaped coordinator/authority clone. Use weak ownership or an
equivalent bounded lifecycle so admission does not create an unbounded strong
reference leak.

Add a first-red exact-shaped deep-clone cell reproducing the reviewer probe and
an isolated registry-gate reversal. Preserve the closed CR-152 cell and all
seven earlier reversals. The same two source/test paths plus WPR-only handoff
remain the entire correction scope. No public contract, other ticket, new
branch/worktree, live effect, integration, push, release or deployment is
authorized.

Decision remains `CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED`.
