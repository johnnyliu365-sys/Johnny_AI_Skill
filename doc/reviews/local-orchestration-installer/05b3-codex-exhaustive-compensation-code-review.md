# Ticket 05B3 Codex Exhaustive Compensation Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05b3-codex-exhaustive-compensation` / `CLOSURE-LOCAL-INSTALL-T05B3-01` |
| Reviewed baseline | `fd1647d548b05ec89de4d38e41cea92911405f08` |
| Implementation / handoff | `0f7951224de7b3fdde6ab81fc640f7894fc0a140` / `b59e97b0912f4e347b37efcbec266f7713868a43` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED`; complete initial-review blocking batch is CR-135 and CR-136 |

The implementation commit changes exactly the three authorized source/test
paths and the handoff changes only `doc/WorkProgressReport.md`. The submitted
lane is clean, descends additively from the reviewed handoff, and did not
create another branch or worktree. Independent verification used an immutable
commit export and did not modify the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 8/8 focused and 238/238 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy over 112 source files and in-memory compile over all three authorized Python paths. |
| Scope / ancestry / residue | PASS: exact `fd1647d -> 0f79512 -> b59e97b` ancestry, three-path implementation, WPR-only handoff, clean tracked/ignored implementation lane and `git diff --check`. |
| D1 request authority | PASS: the six reachable pairs are admitted; the seventh legal 05B1 pair, replayed attempt, malformed constructed journal and manifest mismatch are blocked before effects. An independent cross-request journal probe returned `JOURNAL_REQUEST_MISMATCH` with zero calls. |
| D1 port admission | FAIL: a structural object with all five required attribute names but non-callable values passes the runtime protocol check and raises `TypeError` on the first authorized effect. A second object with five zero-argument methods also raises `TypeError`. Both must be finite `INVALID_PORT` rejections with zero calls under D1. |
| D2 exact removal | PASS: no call for no-authority or pre-existing states; authorized two-effect compensation is plugin-first; exact confirmation identities and marketplace root are checked. |
| D3 exhaustive proof | PASS: each declared or malformed removal/probe failure still executes all later finite steps in the fixed five-step sequence. |
| D4 residual authority | PASS: the full installed/available-plugin, marketplace and installed-path truth matrix retains only unresolved effect authority; proved absence clears retry authority even when removal failed. |
| D5 finite result | PASS: finite result algebra, ordered unique step failures, metadata-only serialization and propagation of the four frozen unexpected/process-control exceptions. |
| Reverse mutations | PASS: all five frozen reversals independently turned the named focused test red: pre-existing removal; short-circuit after plugin failure; clear without both plugin absence proofs; retain stale plugin retry; accept foreign marketplace root. Each mutation ran in-memory and the reviewed source remained byte-identical. |

## Closure and CodeReview.md mapping

- **D1 / T1 / null-shape and error-code classes:** blocking. The request and
  journal validation behavior is correct, but invalid five-method structural
  ports can escape the finite `INVALID_PORT` result as `TypeError`.
- **D2 / T2 / authority-bypass class:** pass. Only `MAY_EXIST` and `OWNED`
  authorize removal; pre-existing and not-attempted states cannot remove.
- **D3 / T3 / exception class:** pass for declared failures and malformed
  observations. Every later finite step runs once and unexpected/process-control
  exceptions are not broadly caught.
- **D4 / T4 / path class:** pass. Marketplace root and installed locator proof
  use exact typed identity/equality; no prefix or broad-clear path is present.
- **D5 / T5 / metadata and dependency classes:** pass. Results contain no raw
  output, absolute path, exception text, receipt or final registration success;
  no production dependency on tests or 05S4 exists.
- **Test truthfulness class:** blocking. The committed T1 suite checks per-field
  omission and extra fields, but not the frozen null/blank/container/wrong
  enum-or-literal matrix, cross-request journal cell, or callable/signature
  invalid-port cells. The one `object()` port case cannot expose CR-135.
- **Token and Agent-role classes:** not applicable; this ticket adds neither a
  credential comparison nor Agent orchestration surface.

## Batched findings

**CR-135 — `IMPLEMENTATION_DEFECT`, D1/T1.**
`codex_compensation.py:290-303` relies on `isinstance(port,
CodexCompensationPort)`. Python's runtime-checkable structural protocol proves
only that the five names exist; it does not prove that each value is callable
or accepts the exact request argument. Independent probes with five integers
and with five zero-argument methods both passed line 290 and raised `TypeError`
instead of returning `COMPENSATION_BLOCKED / INVALID_PORT` before any port
call. Add a side-effect-free, finite runtime port admission guard for all five
named operations and preserve propagation only after a valid port has entered
an actual operation.

**CR-136 — `EVIDENCE_DEFECT`, D1/T1/CodeReview.md class 7.**
`test_codex_compensation.py:312-373` covers missing and extra fields plus one
constructed journal-state case, while lines 570-572 cover only an object with
no port surface. It omits the frozen null, blank, container, wrong
enum/literal and constructed cells, the cross-request journal cell, and ports
whose five names exist but are non-callable or signature-incompatible. Commit
the complete finite D1/T1 table, including zero-call assertions and both
authority/no-authority requests for invalid ports, so CR-135 is red before the
correction and green afterward.

## Conclusion

`CHANGES_REQUESTED`. CR-135 and CR-136 are the complete blocking batch for
closure revision 01; D2-D5 have no other blocking finding. Preserve the same
ticket, task, worktree, branch, allocation and receipt. The correction is one
additive implementation commit in the same three-path scope followed by a
WPR-only handoff. Its review is terminal for this closure: any remaining
blocker requires `CONVERGENCE_REVIEW_REQUIRED`, not another implementation
correction. No integration or downstream dispatch is authorized by this
review.
