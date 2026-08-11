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
