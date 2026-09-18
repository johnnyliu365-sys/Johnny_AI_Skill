# CVQ-01A1 | Scalar and wire admission review

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01A1` / `CODE_REVIEW` / `01` |
| Conclusion / round | `CHANGES_REQUESTED`; closure01 initial review, one additive correction remains |
| Authority | [A1](../../../modules/tickets/controlled-verification/cvq-01a1-scalar-wire-admission.md) document02 at `10cded441222587e05dcf6657637d48c34baf4ab`, LF `1381a8d86b2f8fff947350a9fe3da38e942d59dce2271907d00246b5942e15e6`; closure `CLOSURE-CVQ-01A1/01`; approved upstream pins unchanged |
| Source / candidate | `070039b6227205f7bb4592f203a4fd7455311f31` -> `b1aa3fafaf03a7c47a869210b3934399124df933` |
| Owner / reviewer | Retained `cve_wire_implementer`, implementation-standard; root, ticket-review and sole verdict owner |
| Isolation / effects | Parent detached `.worktrees/cvq-01a1-review`; helper `READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT`; constructor-local tests only, no host/provider/target/VM/runtime effect |

## 1. Identity and observed checks

Parent read the exact ticket, wire, candidate diff and relevant methods, verified ancestry and
clean owner worktree. Exactly three declared paths changed: domains, scalars and fixtures.
Production source is unchanged. No new dependency, suppression, public schema or evaluator is
introduced. Scalar tests are explicitly imported into the existing domains entrypoint; all four
new methods execute once in the complete 26-method suite. No separate scalar input is passed to
that full-suite command. Non-scalar domain methods remain unchanged.

Parent used Python 3.11.9, Pydantic 2.13.4 and mypy 2.3.0. Each Python command is bounded by
`python -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)'`
followed by the exact Python executable and arguments. One foreground process, no load/retries,
no output-reducing wrapper. Full outputs were read before assigning results.

```text
python -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
Success: no issues found in 15 source files (exit 0)
python -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
Ran 26 tests in 0.236s; OK (exit 0)
git diff --check 070039b6227205f7bb4592f203a4fd7455311f31 b1aa3fafaf03a7c47a869210b3934399124df933
exit 0
```

These checks establish collection/type availability, not completion of SW01-08. Catalog totals
remain the independently recounted 81/413/335/78/751; do not revive the superseded 333/747 claim.

## 2. Complete initial-review finding batch

All paths below are relative to candidate b1aa3faf. All findings concern already-frozen A1
requirements; none grants a schema, validator, scope, resource or architecture change.

| ID / class | Existing closure and location | Gap and required correction |
| --- | --- | --- |
| F01 `EVIDENCE_DEFECT` | SW01/SW03, finite catalog; contracts `:211-290`, catalog `:11-252` | The inventory compares field names/defaults but never field annotations; Protocols/QualificationModel are skipped without independent expected inventories for the three ports/bases. Actual alias membership is not compared: source substring presence and successful expected branches do not exclude extras. Complete literal expected types, closed alias and port/base inventories and compare actual observations to them. Keep expected data in the catalog, ordinary fixture/TypeAdapter controls, and all current counts. Do not derive expected values from production. No new production mutation permission is inferred by this finding. |
| F02 `EVIDENCE_DEFECT` | SW02/SW03; contracts `:327-396`, `:419-429`, `:472-480`, `:514-525` | Required-null rows use broad field-name family alternatives (enum/literal, model/dict), not the literal expected error tuple for each field. They have no per-cell subTest ID. Default null/wrong and selector negatives merely catch ValidationError or TypeError/ValueError without the required exact type/location or declared callable-selector form. Supply literal finite per-row expectations and named cells; unrelated rejection cannot count. Preserve the integer-vs-Literal default distinction and the CaseResult/EvidenceResolution exceptions specified by the ticket. |
| F03 `EVIDENCE_DEFECT` | SW04 / CA10 preservation; scalars `:65-107`, `:159-178`; baseline domains `test_scalar_domains_and_all_bounds` | Relocation drops `a_case` and `a.case` negatives. Parent M2 proves accepting both is invisible to the named method. Baseline JSON negative-counter and Lane 0/2 rows are replaced by constructor-only edge rows, not fully preserved as recorded. Restore all predecessor values/path-specific assertions and provide the actual old-method -> new subTest row map. The return's three additional old method names do not occur in this baseline; correct the mapping, do not invent history. |
| F04 `EVIDENCE_DEFECT` | SW08; contracts `:907-910` | Only frozen/extra flags are asserted. The named method does not assert strict/validate_assignment/revalidate_instances, ordinary assignment's frozen_instance location, or tuple-array/scalar/null behavior. Parent M1 changes revalidate always to never and leaves both the named method and all 26 tests green. Complete exactly the frozen SW08 observations and its two independent mutation doors. |
| F05 `EVIDENCE_DEFECT` | Ticket evidence/return; SW01-08 | The completion return gives mutation-family summaries, not the pinned per-predicate patch/command/exit/cell/restoration map. SW08 reports frozen only, and SW01 does not distinguish the required row-removal and real-default experiments. Parent has not authenticated the missing transcript outputs and marks them NOT_VERIFIED, not failed runs. Supply the already-required complete evidence with exact retrievable output references or unreduced output, distinguish honest baseline green from red, and do not call a zero-red experiment success. Preserve source/fixture responsibility and bounded execution; no new helper script or generic mutation framework. |

SW05-07's new methods execute and visibly contain the strict-domain, edge and nine-bound rows.
Their full mutation matrix remains NOT_VERIFIED by the parent at this initial failing review;
it is not silently passed. The one correction must return all frozen evidence together, not only
the two counterexamples below. SW01/03 existing positive and enum tests must be preserved.

## 3. Parent independent counterexamples

Both experiments changed only the parent's clean, candidate-bound snapshot, never the owner's
worktree. Both enter through doors absent from the implementer's reported frozen/whole-pattern
examples. Patches were restored before subsequent runs. Git object for qualification_values.py
after restoration is `64dfe86ceab3d22ac859723437d1e99dc05cd209`; pristine checked-out bytes
SHA-256 `f2586c8934fefde012b40c9e4e1fc33ec407ce9d791d0df2ebb720d0451f6e97` matches before/after M2.

M1 patch, QualificationModel.model_config:

```diff
-        revalidate_instances="always",
+        revalidate_instances="never",
```

Command: `python -B -m unittest -v tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration`.
Unreduced output, exit0 (the defect is ZERO_RED):

```text
test_immutable_contract_configuration (tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

The full two-module suite also remained exit0, 26 OK, 0.201s; parent read every method line.
After exact-source restoration the same named command was exit0, 1 OK, 0.000s. This is not
red/green proof and is recorded as F04.

M2 patch, OpaqueMetadataId pattern:

```diff
-    StringConstraints(pattern=r"^[a-z][a-z0-9-]{2,127}$"),
+    StringConstraints(pattern=r"^[a-z][a-z0-9._-]{2,127}$"),
```

Command: `python -B -m unittest -v tests.test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains`.
Unreduced output, exit0 (ZERO_RED):

```text
test_identifier_digest_text_domains (tests.test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

After byte restoration the same named command was exit0, 1 OK, 0.003s; clean git status. This
is F03, not evidence that accepting separators is permitted. Temporary CRLF restoration was
resolved inside the reviewer snapshot from the exact candidate; no owner file was overwritten.

## 4. Bounded adversarial evidence and applicability

Retained helper returned four static FINDINGS at this exact candidate: catalog closure,
dropped separator rows, broad errors and incomplete configuration checks. Parent independently
read the implicated source; M1/M2 validate the latter and dropped-row defects behaviorally.
The helper's suggested alias/field-type mutations were NOT_RUN and exceed the ticket's named
read-only-symbol exceptions; they are not permission to perform them. F01 rests on the actual
missing assertions and frozen catalog requirement, not invented experimental evidence.

The helper initially misreported an unavailable method reference. A bounded reference-only
addendum resolved the complete candidate blob `8c8d9a2839fedf69c87ddbcb98f004fad1578ac0` for
skills/johnny-project-takeover/references/adversarial-review.md, retained its four findings and
reported no remaining scope deviation. No second code audit, tests or mutations were requested
from it. Parent owns the conclusion; the helper has no approval authority.

REQUIRED / SPEC_GAP, BOUNDARY_DATA, CONSISTENCY, REGRESSION /
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. No UI/XSS, migration, dependency update, privileged
capability or production deployment exists in this three-test-file patch; those effect-specific
checks are NOT_APPLICABLE here, not runtime readiness claims. Same-lifetime reviewer orchestration
requires no runner/receipt/descriptor. No main/staging/push/release effect is authorized.

## 5. Return and continuation

ACTION_COMPLETED / CHANGES_REQUESTED -> AUTO_CONTINUE / one additive A1 correction on
codex/cvq-01 from b1aa3faf, same owner/profile/worktree and closure01, binding A1 document03
and this review at their committed control revision. No reset/amend/force or model elevation.
A2/A3/B remain dependency-pending. Correction review is the final review for closure01; remaining
blocking defects return CONVERGENCE_REVIEW_REQUIRED, not a third correction.

Host incident is separate: a parent-session request received HTTP400 unsupported_parameter for
access_programs.cyber. Its parameter-injection source is unproven. No account/plugin/config
change was made. Native owner reuse ultimately returned the candidate through wait_agent;
the failed duplicate-name spawn created no new seat. The repository's evidence gaps above are
independent of that transient host failure.
