# Ticket 05B2 Codex Command-Attempt Classification Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05b2-codex-command-attempt-classification` / `CLOSURE-LOCAL-INSTALL-T05B2-01` |
| Reviewed baseline | `22600c385bebf1a919bf05fb2745661c4d920b29` |
| Implementation / handoff | `e8beeac74635573c94d1a4f5852fe0ea2224d9e4` / `d3bb4ade4f420e2a2bb38b779db0263d0a90f10a` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED`; one same-closure additive correction is permitted |

The implementation changes exactly the three authorized source/test paths and
the handoff changes only `doc/WorkProgressReport.md`. The implementation lane
is clean and no additional branch or worktree exists. Independent execution
used an immutable commit export and did not write the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 4/4 focused and 227/227 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy over 110 source files and in-memory compile over all three authorized Python paths. |
| Scope / ancestry / residue | PASS: additive ancestry from `22600c3`, exact three-path implementation, WPR-only handoff, clean tracked/ignored lane and `git diff --check`. Review cache stayed outside the repository. |
| C1 finite models | FAIL: six discriminator fields declared by the frozen models are optional at validation time because defaults manufacture them. Independent missing-field enumeration accepts `CodexPreStartFailure.start_state`, `CodexStartedFailure.start_state`, both confirmation targets and both confirmation start states. |
| C1 recursive strictness | FAIL: `model_construct` observations carrying raw strings for enum/literal fields are serialized to JSON and then accepted by `model_validate_json`; independent pre-start, started-failure and marketplace-confirmation probes all reached a journal transition instead of `INVALID_OBSERVATION`. |
| C2 admission | PASS: an independent 14-cell enumeration admits exactly the two frozen command/journal pairs and rejects the remaining twelve; malformed, request-mismatch and attempt-mismatch reasons are distinct. |
| C3 transition | PASS: six pre-start cells are byte/value-equivalent, twelve started-failure cells change only the target to `MAY_EXIST`, and all three confirmations plus removal order match the closure. |
| C4 result / exception boundary | PASS: rejection contains only `status` and `reason`; `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` propagate. No host/process/filesystem/target-project effect is present. |
| Reverse mutations | PASS: treating access denied as attempted failed two T3 cells; leaving started failures unchanged failed all twelve started-failure cells; mapping `already_added=true` to `OWNED` failed the pre-existing assertion. Each mutation was isolated and discarded with the review export. |

## Closure and CodeReview.md mapping

- **C1 / T1 / null-shape class:** blocking. Missing explicit discriminator
  fields and constructed raw-string values are accepted rather than failing
  recursive validation.
- **C2 / T2 / error-code class:** pass. The full admission matrix and three
  journal rejection categories are finite and distinct.
- **C3 / T3 / authority-bypass class:** transition behavior passes, but C1's
  incompletely typed constructed observations can still reach those authority
  transitions, so approval remains blocked.
- **C4 / T4 / exception class:** pass. The four frozen unexpected and
  process-control exception types propagate and no broad catch is present.
- **Test truthfulness class:** blocking. The committed test's
  `required_models` table omits the six accepted missing discriminator cells,
  and its constructed table checks swapped values but not correctly spelled
  raw strings that bypass strict Python enum typing through JSON validation.
- **Path-prefix and token classes:** not applicable; this ticket introduces no
  path or credential input. **Agent-role class:** no orchestration surface is
  introduced. Dependencies, scope and no-effect isolation otherwise pass.

## Batched findings

**CR-133 — `IMPLEMENTATION_DEFECT`, C1/T1.** Lines 61, 69, 75-76 and
83-84 of `codex_command_attempts.py` provide defaults for fields that the
frozen closure requires callers to supply and recursive validation to reject
when missing. Independent enumeration accepts all six missing cells. Lines
146-152 then round-trip through JSON, which converts raw-string enum/literal
values from `model_construct` into valid members; three independently
constructed raw-string observations produced journals. Make every observation
field explicit and revalidate the Python-typed field values without a JSON
coercion path.

**CR-134 — `EVIDENCE_DEFECT`, C1/T1/CodeReview.md class 7.** Lines 107-125
of `test_codex_command_attempts.py` test only selected required fields and use
implicit defaults as their valid baseline. Lines 159-180 cover swapped
constructed literals but omit correctly spelled raw-string enum/literal
values. Commit the complete four-model per-field missing table and constructed
raw-type cells so both portions of CR-133 turn red before the correction and
green afterward.

## Conclusion

`CHANGES_REQUESTED`. CR-133 and CR-134 are the complete blocking batch for
closure revision 01; C2-C4 have no other blocking finding. Preserve the same
ticket, task, worktree, branch, allocation and receipt. The correction must be
one additive implementation commit in the same three-path scope followed by a
WPR-only handoff. This correction review will be terminal for this closure: a
remaining blocker requires `CONVERGENCE_REVIEW_REQUIRED`, not a second
implementation correction. No integration or downstream dispatch is
authorized by this review.
