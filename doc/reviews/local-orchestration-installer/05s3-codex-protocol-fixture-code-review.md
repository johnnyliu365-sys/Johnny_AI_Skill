# Ticket 05S3 Codex Protocol Fixture Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05s3-codex-protocol-fixture` / `CLOSURE-LOCAL-INSTALL-T05S3-01` / D1-D4 and T1-T4 |
| Reviewed baseline | `130ef794e8d62d32f89054ad86f75f7dfd8cd42c` |
| Implementation | `bd59011636fd87f6c8ba28b25253ab21e7980d1c` |
| Docs-only handoff | `f725d48238402606107b0e304b6bf7213c0acc2b` |
| Branch / owner | `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED / FINAL_REVIEW_STOPPED` |

The submitted ancestry is exact: `130ef79 -> bd59011 -> f725d48`. The
implementation changes exactly the five authorized Python files and the
handoff changes only `doc/WorkProgressReport.md`. Both worktrees were clean and
`git diff --check` passed. Review execution used a fresh immutable export and
never modified the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 4/4 focused and 193/193 full unittest tests. |
| Strict typing / compile | PASS: strict mypy checked 96 source files with a removed external temporary cache; all 96 Python files compiled in memory. |
| Scope / source | PASS: exact authorized paths, no `Any`, `type: ignore`, optional effect port, request synthesis, raw child output, or rejected combined-05S source reuse. |
| Protocol / child binding | PASS: all six strict schemas, duplicate-key checks, real 05S2 child responses, fixed response-file topology, process-failure mapping and child-only sentinel binding passed. |
| Cleanup / isolation | PASS: collision, topology, read and cleanup cases preserved external bytes and parent environment; repository cache, response-file and staging-root residue were zero. |
| Bounded decoder exception probes | **FAIL:** a 3,062-byte nested-array value escaped as `RecursionError`; a 5,061-byte integer value escaped as plain `ValueError`. Both are below the 65,536-byte response limit. |

## Closure mapping

| Item | Result | Independent disposition |
| --- | --- | --- |
| `D1 / T1` | PASS | The four mutation DTOs and reused two list DTOs enforce the frozen fields and strict scalar types. |
| `D2 / T2` | FAIL | Declared malformed/schema cases pass, but two bounded JSON inputs escape the finite rejection union. |
| `D3 / T3` | PASS | Each surface is bound to a real bounded child and accepted data comes only from the fixed response file. |
| `D4 / T4` | FAIL only on exception finiteness | Invariants and residue pass, but the parser can throw before returning a named rejection. |

## CodeReview.md mandatory checks

- **Clear strong types:** PASS for the public models and ports; FAIL at the
  decoder boundary because valid `bytes` can escape the declared result union.
- **Existing coding conventions:** PASS. The fixture follows the integrated
  frozen Pydantic, protocol and unittest structure.
- **Logic correctness:** FAIL CR-125. `json.loads` has bounded failure modes
  beyond `JSONDecodeError` that are not mapped.
- **Edge cases:** FAIL the deep-container and oversized-integer decoder cases;
  the required schema, topology, process and cleanup cases pass.
- **Security / performance:** PASS for isolation and bounded transport size.
  The escaped exceptions are correctness/reliability defects, not a new host
  capability.
- **Test coverage / smoke:** FAIL T2 exception containment despite green
  focused/full suites; no committed cases exercise these standard decoder
  limits.
- **Dependency reasonableness:** PASS. No dependency or production file
  changed.
- **Project specification:** FAIL D2/D4 until every bounded decoder failure
  returns one declared rejection.

CodeReview.md defect classes 5, 6 and 7 apply: the declared result and actual
exception surface diverge, exceptions cross the boundary, and the green matrix
does not prove the frozen finite-result claim. Path, null, permission and token
classes either pass or are not applicable.

## Finding

**CR-125 - `IMPLEMENTATION_DEFECT`, D2/D4 and T2/T4.**
`tests/staging/codex_protocol/contracts.py:226-241` decodes with `json.loads`
but catches only `_DuplicateJsonKey` and `json.JSONDecodeError`. Independent
bounded probes caused `RecursionError` for a 1,500-level array and `ValueError`
for a 5,000-digit integer. Neither returned `MALFORMED_JSON` or another named
`CodexProtocolRejectReason`. The implementation must contain all standard JSON
decoder failures admitted by the response-byte contract and add both exact
regressions; no raw exception text may enter evidence or a result.

## Conclusion

`CHANGES_REQUESTED / FINAL_REVIEW_STOPPED`. CR-125 is a narrow implementation
defect; the remaining closure passes. Per the ticket stop boundary, this review
does not authorize an automatic correction, replacement branch/worktree,
integration, 05S4 dispatch, live Codex mutation, target-project write, push,
release or deployment. Allocation `aln_local_orchestration_install_05s3_20260811`
is released and receipt `rcpt_local_orchestration_install_05s3_20260811` is
closed against replay. Submitted commits remain immutable review evidence.

## Owner-authorized revision-02 disposition

The owner authorizes `OVR-LOCAL-INSTALL-T05S3-CR125-20260811-01` and
`CLOSURE-LOCAL-INSTALL-T05S3-02` for CR-125 only. The same task, implementation
worktree and branch may add one correction commit from exact submitted HEAD
`f725d48238402606107b0e304b6bf7213c0acc2b`, followed by one docs-only
handoff. The correction must retain duplicate-key specificity, map only the
documented standard JSON decoder failures to the existing finite result, and
add the two exact bounded regression probes. The next independent review is
final for this override; any blocker stops without another correction or 05S4.

## Revision-02 final independent review

| Field | Value |
| --- | --- |
| Closure / override | `CLOSURE-LOCAL-INSTALL-T05S3-02` / `OVR-LOCAL-INSTALL-T05S3-CR125-20260811-01` / CR-125 only |
| Control baseline | `4b17a2587cd247c2c97fffbf7785e284a8610500` |
| Correction / handoff | `4835b0f0b5f404d13dd04e0aa55ca6205a816f2c` / `008fac8327ce783b2cc39331064eed8e31c9a34d` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Final result | `APPROVED / INTEGRATION_AUTHORIZED` |

The correction is exactly additive: `f725d48 -> 4835b0f -> 008fac8`. The
implementation commit changes only the two authorized Python files and the
handoff changes only `doc/WorkProgressReport.md`. Both worktrees remained clean
and exactly the original two worktrees exist. Review ran from a fresh immutable
ZIP export and never wrote to the implementation worktree.

### Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 6/6 focused and 195/195 full unittest tests. |
| Strict type / compile | PASS: strict mypy over 96 source files with a removed external cache; in-memory compile over the same 96 files. |
| Exact CR-125 probes | PASS: the original nested-object forms were 3,062 and 5,061 bytes, both below the bound, and both returned `MALFORMED_JSON`. |
| Result specificity | PASS: duplicate-key input remained `DUPLICATE_KEY`; injected `MemoryError` escaped and was not misclassified. |
| Reverse mutations | PASS: independently removing only `RecursionError` made the deep-array test error; removing only `ValueError` made the huge-integer test error. The review export was restored to the submitted bytes before final readback. |
| Scope / source / ancestry | PASS: exact two-file implementation scope, one-file docs scope, additive ancestry, source sentinel and `git diff --check`. |
| Isolation / residue | PASS: both worktrees clean; repository cache, fixed response-file and owned staging-root counts were zero. |

### Closure and mandatory-check mapping

| Item | Result | Independent disposition |
| --- | --- | --- |
| `D1 / T1` | PASS | Revision-01 strict public models and all six canonical payloads remain green. |
| `D2 / T2` | PASS | Every declared schema case plus both bounded standard decoder limits returns a finite typed result. |
| `D3 / T3` | PASS | Real-child binding and exact process-failure truth remain green in focused/full suites. |
| `D4 / T4` | PASS | Exception finiteness, topology, cleanup, invariants and zero residue all pass. |

- **Clear strong types:** PASS. The parser retains the declared finite result
  union without adding a broad or nullable path.
- **Existing coding conventions:** PASS. The correction is the smallest change
  to the existing strict parser and unittest structure.
- **Logic correctness:** PASS. Duplicate keys are handled before the broader
  decoder `ValueError`; the two proven decoder limits map to `MALFORMED_JSON`.
- **Edge cases:** PASS. Both standard decoder limits, duplicate keys and the
  excluded process-control exception were independently exercised.
- **Security / performance:** PASS. The 65,536-byte transport bound and all
  filesystem/process isolation behavior remain unchanged.
- **Test coverage / smoke:** PASS. Both exact tests fail under their matching
  one-line reverse mutation and pass after restoration.
- **Dependency reasonableness:** PASS. No dependency or production file changed.
- **Project specification:** PASS. CR-125 is closed without changing D1-D4 or
  inventing a new result contract.

CodeReview.md defect classes 5, 6 and 7 now pass. No new blocking finding
exists.

### Final conclusion

`APPROVED / INTEGRATION_AUTHORIZED`. A later guarded integration may preserve
the control review commit as first parent and reviewed handoff `008fac8` as
second parent. Allocation `aln_local_orchestration_install_05s3_r02_20260811`
and receipt `rcpt_local_orchestration_install_05s3_r02_20260811` remain active
only until that integration is verified. This correction review does not merge,
dispatch 05S4, push, release, deploy, mutate live Codex or touch a target project.

## Guarded integration

Merge `43a1639cfda44b4b9c664c584cf557b47ddb510a` preserves control approval
`c518e6211f6c7f8d90df2f7681fd457036cf8978` as first parent and reviewed
handoff `008fac8327ce783b2cc39331064eed8e31c9a34d` as second parent. The only
conflict was `doc/WorkProgressReport.md`; PRG-126 through PRG-131 were retained
exactly once and in numeric order.

Post-merge verification passed: focused 6/6, full 195/195, strict mypy and
in-memory compile over 96 files, exact 3,062/5,061-byte decoder probes,
duplicate-key specificity, excluded `MemoryError`, source sentinels,
`git diff --check`, two clean worktrees and zero cache/response/staging-root
residue. Ticket 05S3 is `COMPLETE / APPROVED / INTEGRATED`; 05S4 is ready but
was not dispatched. No push, release, deployment, live Codex mutation or
target-project write occurred.
