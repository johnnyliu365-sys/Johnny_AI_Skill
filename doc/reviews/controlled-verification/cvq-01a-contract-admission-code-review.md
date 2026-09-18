# CVQ-01A | Contract admission code review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A` / `CODE_REVIEW` / `02` |
| Conclusion / round | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`; closure 01 initial plus correction review exhausted |
| Authority | [CVQ-01A](../../../modules/tickets/controlled-verification/cvq-01a-contract-admission.md) document 02 at `106c8e970e348c9f9157decc2dc5336a4f4ae237`, LF `956e63af1c37c3f2f85285d6e6f55b9d4723f8ff89582d598a609f45ba9c2d24`; approved SPEC 07 / wire 03 / Context 02 pins unchanged |
| Source / candidate | `5d7789db6b950d317e7b500b757aa77a54d609ed` -> `fd8c1a33599b5217136ec67c8b64ade07ef6d56e` (includes `61919a3d3cf817b85c1f0c80a5232e4f00a69f36`) |
| Reviewer / owner | `root`, ticket-review; retained `cve_wire_implementer`, implementation-standard / Luna xhigh |
| Isolation / effects | Parent detached `.worktrees/cvq-01a-review`; helper `READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT`; source-only constructors, no provider/target/VM/native execution |

## 1. Candidate identity and observed checks

Parent independently checked ancestry, clean owner tree and the actual eight-path diff. Changes
are within the declared writable paths. The CQ11 method plus following source is exactly equal
to the baseline after LF normalization; it remains explicitly unqualified and outside A's oracle.
The five named old scenario builders no longer remain as duplicate assertion-module builders.
This does not discharge CA10: deleted domain assertions must still execute after relocation.

Interpreter: Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0. Commands run in the candidate snapshot,
one foreground process, bounded with `subprocess.run(sys.argv[1:], timeout=60)`, no output filter,
no load, retries, dependency changes or background process. Parent read complete command output.

```text
python -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
Success: no issues found in 14 source files (exit 0)
python -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
Ran 18 tests in 0.170s; OK (exit 0, restored candidate rerun)
git diff --check
exit 0
```

The type-check result includes two newly added suppressions (F03); it is not proof of P0 compliance.
The 18 methods exercise an incomplete matrix (F01-F08); the green count is not acceptance.

## 2. One complete, batched blocking finding set

Paths below are relative to the candidate. Each item corrects an already frozen predicate, not a
new requirement. Helper findings were independently checked by the parent against the same source.

| ID / class | Closure / candidate location | Reproducible gap and required disposition |
| --- | --- | --- |
| F01 `EVIDENCE_DEFECT` | CA02; `tests/test_verification_qualification_contracts.py:327-337` | `reject` catches broad `Exception`, checks only `ValueError`/optional error details and a final location segment. No authored finite error-type assertion. Use `ValidationError` and independent literal expected location/type per row; unrelated root errors or `json_invalid` cannot satisfy it. |
| F02 `EVIDENCE_DEFECT` | CA03; `tests/test_verification_qualification_domains.py:76-164` | Digest negatives retain the preceding illegal `project_id=é-case`; removing Digest grammar still passes all 18 methods (M1). Strict bool/float/string and Lane 0/2 cells are absent; coercible PositiveInteger passes M2. Rebuild a valid base per cell; exercise every frozen scalar/bound and assert the intended error. |
| F03 `IMPLEMENTATION_DEFECT` | P0 / section 4 strict type; domains `:147-157` | `type[object]` followed by two `type: ignore[attr-defined]` suppressions hides the validation API. Use the existing typed model seam or separately typed calls; no suppression/new generic framework. |
| F04 `EVIDENCE_DEFECT` | CA05; domains `:200-243` | Missing full five-row/both-key applicability, membership/key disagreement, duplicate/disagreeing prerequisite and two-case HOST_DISCOVERY cells. Several negative inputs also disagree in an earlier prerequisite. Complete the existing finite matrix with one deliberate invalid predicate per payload. |
| F05 `EVIDENCE_DEFECT` | CA06; domains `:245-266` | RefusedClaimProof pairs are covered, but PURE_RULE / MEASURED_NATIVE / UNAVAILABLE_PROBE / NOT_COMPLETED scope/result compatibility is not. Standalone proof round trips in contracts `:722-738` do not test their enclosing claim. Restore all frozen valid/invalid proof combinations. |
| F06 `EVIDENCE_DEFECT` | CA07; domains `:268-294` | Alleged duplicate entry retains SHELL_EXECUTION inside DIRECT_WRITE and can fail category agreement first; dead `if False` expression adds no oracle. Missing independent global entry/alias duplicates, case refs, observed sorting, all-ABSENT/zero-present and negative observations. Keep category agreement valid when targeting global uniqueness. |
| F07 `IMPLEMENTATION_DEFECT / EVIDENCE_DEFECT` | CA08; `library/controlled_verification/qualification_ports.py:41-62`, domains `:296-321` | `roster_plan_coverage` validates pins only; an otherwise coherent later HOST_PROPERTY case `case-not-in-plan` is accepted although its same-key plan only names `case-property`. Add the frozen local case-membership comparison, not external resolution. Test duplicate/wrong key/wrong digest/native-primitive-empty/future-discovery-intent cells as well as existing missing/extra/ref cases. |
| F08 `EVIDENCE_DEFECT` | CA09 / CA10; domains `:323-344`, report `:331-339` | Only four single-field authenticated negatives remain. Removed report/case/claim/check/requirement/capability duplicate families, launch/cleanup/roster constraints and remaining shared identities are not equivalently relocated. Removing report result-ID uniqueness stays all green (M3). Restore the original assertions and complete the frozen local matrix; do not restore scenario-builder duplication. |
| F09 `EVIDENCE_DEFECT` | Section 4 evidence and return | Return used `IMPLEMENTED`, not `ImplementationReturn.COMPLETED`, and does not discharge every named baseline-red / predicate-family mutation with exact command, exit, result and restoration. Supply the frozen evidence mapping; label later baseline reproduction honestly, never fabricate chronological first-red. Missing immutable earlier records remain a visible gap rather than a pass. |

CA01's positive/catalog checks and CA04's newly added joins ran green. They must be preserved;
their section-4 reverse-mutation evidence still belongs in F09. No separate type, dependency,
performance, security, XSS, UI, migration or deployment requirement is invented by this review.

## 3. Parent counterexamples and restoration

Parent used independent doors rather than the implementer's reported upper-bound/argv examples.
Each mutation ran the complete two-module unittest command in section 1 with all 18 method names
and full output visible. A zero-red result is a finding, never successful mutation evidence.

| ID | Exact weakened candidate symbol | Unreduced run observed | Restoration |
| --- | --- | --- | --- |
| M1 | `qualification_values.Digest`: replace regex `StringConstraints(pattern=...)` with `StringConstraints()` | exit 0, 18 OK, 0.155s; zero red | exact source restored; named CA03 method exit 0, 1 OK, 0.004s |
| M2 | `qualification_values.PositiveInteger`: `Field(gt=0)` -> `Field(gt=0, strict=False)` | exit 0, 18 OK, 0.161s; zero red | exact source restored; named CA03 method exit 0, 1 OK, 0.004s |
| M3 | `report_contracts.QualificationReport.unique_report_cells`: prepend `False and` to result-ID duplicate branch | exit 0, 18 OK, 0.163s; zero red | exact source restored; complete final rerun exit 0, 18 OK, 0.170s |

Ordinary-constructor probe for F07 used fixture `native_case` with REAL_HOST_PROPERTY,
`host_capability_key()` and HostPropertySubject whose key/ref/digest exactly match
`approved_roster_plan()` (`roster-approved`, `d` x 64). Both manifest scope and its single
HOST_PROPERTY requirement coherently name the candidate case. Discovery coverage is
`coverage-cvq`, `e` x 64; baseline/manifest digests use the existing fixture constants.

```text
ApprovedManifestFound(manifest=<coherent case-property manifest>, roster_plans=(approved_roster_plan(),))
case-property ACCEPTED EXPECTED_ACCEPT
ApprovedManifestFound(manifest=<same construction with coherent case-not-in-plan IDs>, roster_plans=(approved_roster_plan(),))
case-not-in-plan ACCEPTED EXPECTED_REJECT
```

No `model_construct`, `model_copy`, native effect or resolver-authenticity assumption was used.
After every temporary source mutation was restored, parent checked clean `git status`, no HEAD
diff, full strict/type and unittest reruns, and `CQ11_BODY_EXACTLY_PRESERVED`. The implementer's
worktree was never mutated by the reviewer.

## 4. Required adversarial evidence and route

Retained Terra/xhigh helper returned FINDINGS for exact candidate fd8c1a3, closure 01,
REQUIRED / SPEC_GAP, BOUNDARY_DATA, CONSISTENCY, REGRESSION / READ_ONLY_INTENT_ONLY /
NO_EXTERNAL_EFFECT. Its seven findings corroborate F01, F02, F04-F08. It performed read-only
source inspection, no tests, writes, dispatch or approval. Root owns this verdict.

Route `ACTION_COMPLETED / CHANGES_REQUESTED` -> one additive correction with the same owner,
branch and closure. Bind this review and ticket document 03 at their committed control identity.
B remains DEPENDENCY_PENDING / NON_DISPATCHABLE. Correction review is the last review under
closure 01; if defects remain, return CONVERGENCE_REVIEW_REQUIRED rather than a third attempt.
Nothing here authorizes integration, push, release, installation or evaluator behavior.

## 5. Correction review — 2026-09-18

Sections 1–4 preserve the initial review at control `96223979e527edfddc73b1b67046c1438019cab4`.
That exact authority dispatched document 03's ONE correction to the retained Luna/xhigh owner;
parent waited with wait_agent, not activity polling. Owner returned
`070039b6227205f7bb4592f203a4fd7455311f31`, an additive child of fd8c1a3, and the correctly typed
ImplementationReturn.COMPLETED. No source changes were requested after that return.

Parent verified clean owner/source identity, ancestry and exactly four correction paths:
qualification_ports.py, roster_contracts.py, contract tests and domain tests. The original eight
paths remain the complete baseline-to-candidate set. CQ11 body remains exactly baseline-equivalent.
Review snapshot `.worktrees/cvq-01a-review-correction` is detached at the correction SHA.

The section-1 full commands ran unfiltered and exit 0: 23 tests (0.190s initially, 0.182s after
final restoration); strict mypy, 14 files. No remaining `type: ignore` in the domain test. This
closes F03; F01 now catches ValidationError and asserts authored location/error families.
Digest fixture contamination and PositiveInteger/Lane negatives are improved. Report result/
claim negatives and the missing HOST_PROPERTY membership guard are now present. These gains are
preserved, not reset or dismissed because other cells still fail review.

### Independent correction counter-mutations

Every row is a separate temporary mutation on the exact correction snapshot, with the preceding
mutation restored first. Commands use the same 60-second foreground wrapper and interpreter;
no output reducer. Parent read the complete unittest output, not the implementer's summary.

| ID / existing finding | Mutation and full observed result | Exact restoration result |
| --- | --- | --- |
| CM1 / F02, CA03 | `qualification_values.NonNegativeInteger`: `Field(ge=0)` -> `Field(ge=0, strict=False)`; full two-module command: exit 0, 23 OK, 0.195s. **Zero red**: required NonNeg bool/float/string rejection is not pinned | CA03 method: exit 0, 1 OK, 0.006s |
| CM2 / F06, CA07 | Disable only `ApprovedHostRosterPlan.complete_planned_categories` global alias duplicate branch with `False and`; full two-module command: exit 0, 23 OK, 0.190s. **Zero red**: entry ID and case-ref duplicates mask the alias predicate | CA07 method: exit 0, 1 OK, 0.010s |
| CM3 / F05, CA06 | `CapabilityObservation.proof_matches_result`: remove only `or not terminal_result` from the PURE_RULE branch, leaving scope comparison intact; full two-module command: exit 0, 23 OK, 0.182s. **Zero red**: scope negative alone does not pin result compatibility | CA06 method: exit 0, 1 OK, 0.002s |
| CM4 / F07, CA08 | Disable only `ApprovedManifestFound.roster_plan_coverage` case-ID membership branch; named CA08 method: exit 1, one failure at domains.py:593, `AssertionError: ValidationError not raised`, 0.009s | Same method exit 0, 1 OK, 0.009s. This particular correction is independently proved |

Named commands above are `python -B -m unittest -v` plus
`tests.test_verification_qualification_domains.QualificationDomainTests.` followed by
`test_scalar_domains_and_all_bounds`, `test_roster_local_invariants`,
`test_refusal_proof_result_matrix` or `test_approved_manifest_plan_coverage`, respectively.
The full command is the unchanged section-1 two-module invocation. CM1–CM3 each independently
ran all 23 method names to exclude a missing assertion being hidden in a different matrix method.

After source restoration, parent mechanically restored original CRLF bytes only after confirming
LF source equality to `git cat-file --filters HEAD:<path>`. All four mutated files then matched
their exact checkout bytes. Clean status/no HEAD diff, diff-check, full 23-test and strict-type
reruns were observed. No source mutation was committed or applied to the owner's worktree.

### Remaining batch and helper disposition

Required retained Terra/xhigh helper inspected correction 070039b6 under the same four categories,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. It returned four findings, no writes/tests or approval.
Parent checked all against the actual complete test source:

| Existing finding | Correction disposition |
| --- | --- |
| F02 | PARTIAL: Digest and positive integers improved; CM1 proves NonNeg strictness still unpinned. The frozen scalar family cannot be marked complete |
| F04 | PARTIAL evidence only: more applicability/prerequisite cells exist; no complete per-predicate mutation result was supplied, so no full matrix qualification is claimed |
| F05 | PARTIAL: each proof family now has an enclosing example, but CM3 proves PURE_RULE result compatibility still unpinned |
| F06 | PARTIAL: sorting/negative-shape examples improved; CM2 independently reproduces helper's overlapping entry/alias/case-ref negative. domains.py:468-470 changes only comparison to MISMATCH; required nonzero discovery counters have no positive cell |
| F07 | Primary implementation defect CLOSED by CM4; CA08 evidence still incomplete: domains.py:523-594 never constructs extra-plan rejection for a native-primitive-only NO_ROSTER manifest |
| F08 | PARTIAL: report/check/requirement examples improved, but no negative for QualificationCase.expected_check_ids or CapabilityObservation.case_ids duplicates; domains.py:596-717 still omits several shared authenticated subject/payload identities |
| F09 | NOT CLOSED: owner confirmed only the listed mutation subset was performed, remaining individual CA05–CA09 families NOT_RUN/MISSING. Baseline chronology also includes the ticket defect below |

The helper's evidence supports the recorded missing cells; root's CM1–CM4 support the actual
mutation conclusions. No helper verdict substitutes for root review. XSS, provider effects,
native isolation, UI, migrations, release readiness and runtime behavior remain out of A's scope.

### Baseline requirement defect — not an implementer failure

Parent requested an evidence-only clarification, explicitly prohibiting new tests/source work.
Owner reported saved baseline-red summaries for CA04 argv/cwd/environment, CA05 pure host, CA06
refusal result, CA07 planned sorting and CA08 extra-pure-plan. Those are owner-supplied summaries,
not newly parent-reproduced historical transcripts. For CA03 case_output_bytes it correctly
reported MISSING: exact 5d7789d already passed the bound; only a later candidate mutation was red.

Parent independently inspected clean detached 5d7789d and ran ordinary EvidenceBounds constructors:

```text
manifest_contracts.py:63: case_output_bytes: PositiveInteger = Field(le=262_144)
EvidenceBounds(total_bytes=1, case_output_bytes=262144)
BASELINE_LIMIT total_bytes=1 case_output_bytes=262144
EvidenceBounds(total_bytes=1, case_output_bytes=262145)
BASELINE_LIMIT_PLUS_ONE_REJECTED [(('case_output_bytes',), 'less_than_equal')]
```

This is `TICKET_DEFECT`: section 4 requires defect baseline-red on a predicate already correct
at that baseline. The parent owns that preflight mistake. Do not fabricate red, mislabel a
candidate mutation as original baseline evidence, or reject valid code just to satisfy that
history. Changing the evidence requirement needs exact control-plane approval; it is not silently
waived here. Genuine counter-mutation gaps above remain independently blocking.

Route ACTION_COMPLETED / CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED. A closure 01 is exhausted,
source owner/view closed to further implementation; no third correction. B remains dependency
blocked. See convergence proposal revision 08 for an owner-pending replan, not dispatch authority.
