# UIX-02 reference-renderer evidence admission — code review

| Field | Value |
| --- | --- |
| Review ID / revision | `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` / `13` |
| Ticket / closure | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` authority document revision `13`, outcome revision `14` / effective `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02` revision `04`; correction review completed 2026-09-05 |
| Authority commit | `87681ccb24576006ee9dcdaf8e49815faf3a3a42`; ticket LF SHA-256 `0c97862043b8202617cbbe0a6a2b1e61787f64334e89abd46d5c97e51de6789d` |
| Local control-plane proposal commit | `377b45cc7a4ac038d00b8f52a5a14b282dbde337`; intentionally unpushed under the 2026-09-01 owner authority |
| Owner approval source | Project owner, 2026-09-01 (Asia/Taipei): candidate authority commit `a616e561423fd40508dfbebcb33b798e071b5462`, ticket revision-08 LF-normalized SHA-256 `7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953` |
| Closure revision 04 approval source | Project owner, 2026-09-01 (Asia/Taipei): candidate authority commit `515e2fd81f8b54030c5fd27abbd43cd63d5df3bc`, ticket revision-11 LF-normalized SHA-256 `348a5c2f12a773b77898616b71ce70947625f1f9fb6db021b0c4ca171fa437fb` |
| Candidate / baseline | `b419954bc57777661d7522247ffc26977f668ca7` / `18ed02c736812e2e7fab738dc2b8a7036d1da987` |
| Branch / owner | `implement/plugin-adoption-quality-uix-02` / `implementation-standard` |
| Reviewer / helper | `ticket-review` / one read-only `RESEARCH_HELPER` |
| Result | `BLOCKED / EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED / CANDIDATE_NOT_INTEGRATED` |

Sections preceding the 2026-09-05 review below retain point-in-time historical evidence and
authority restrictions. Current execution authority and findings are bound by the metadata above
and that dated section; earlier exhausted closures are not reopened.

## Admission and boundary

The candidate descends from the exact approved authority baseline and changes only the declared
private source, focused test and element paths. The worktree is clean after the reviewer-created
candidate commit. No renderer, browser, provider, filesystem, network, process, target,
publication, installation, release or deployment effect was performed.

The implementation-owner focused, regression, strict-type and compile gates returned green. A
separate Terra/xhigh read-only helper attacked the exact candidate and returned findings only; it
did not modify, approve or integrate the candidate. The reviewer then reproduced the findings
against ordinary public constructors with unreduced command output.

## Blocking ticket defect

UIR6 requires valid-but-different request identity or approved-content identity to return
`CONTENT_BINDING_MISMATCH`. The frozen evidence variants contain no request reference, brief ID,
approved-content digest or derived binding digest. Reusing one ordinary
`RenderedReferenceEvidence` under two otherwise valid requests with different request refs, brief
IDs and content digests returns `ADMITTED_RENDERED` twice. `CONTENT_BINDING_MISMATCH` is declared
but unreachable.

Adding a comparable binding to the evidence variants changes the ticket-defined public DTO shape.
The implementation owner cannot invent that contract, so this is `TICKET_DEFECT`, not an
implementation correction. Closure revision 01 is non-dispatchable until the owner approves a
revised binding contract.

## Other candidate findings

The same bounded review batch found three additional frozen-contract gaps:

1. `AVAILABLE_AUTHORIZED` plus `ARTIFACT_ONLY` currently returns `ADMITTED_ARTIFACT`; the ticket
   must state explicitly whether artifact fallback is reserved to `UNAVAILABLE` and `DECLINED`.
2. UIR1 requires bounded Unicode metadata to round-trip without normalization, but every opaque
   identifier uses an ASCII-only pattern and rejects the Unicode cell.
3. The implementation accepts undeclared aliases for `renderer_target` and
   `owner_manual_open_acknowledgement`, so the exact DTO shape and extra-field rejection are not
   closed.

The last two are implementation defects once the ticket contract is repaired. The first is an
ambiguity that the revised ticket must close rather than asking the implementation owner to infer
a truth table.

## Reproduced evidence

```text
same evidence + request/content identity A -> ADMITTED_RENDERED
same evidence + request/content identity B -> ADMITTED_RENDERED
AVAILABLE_AUTHORIZED + ARTIFACT_ONLY       -> ADMITTED_ARTIFACT
bounded Unicode request identity           -> ValidationError/string_pattern_mismatch
declared_renderer_target alias              -> accepted
owner_manual_open_acknowledged alias        -> accepted

focused                                     7 passed
UIX-01/workflow regression                  68 passed, 216 subtests passed
mypy --strict                               Success: no issues found in 2 source files
compileall                                  exit 0
git diff --check                            clean
```

The green suite does not discharge the missing discriminating cells. Because review admission is
blocked by a ticket defect, no reviewer counter-mutation or document-mutation integration was
performed.

## Revision 01 conclusion and route

Final conclusion: `BLOCKED / TICKET_DEFECT`. Candidate
`faf3d05e07f83a8c7804313b4d3435d01da338b0` remains only preserved evidence on its implementation
branch and must not enter `main`.

The control plane must propose one revised closure that adds an evidence-to-request/content
binding, closes the authorized-artifact truth-table cell, admits bounded Unicode without
normalization and rejects undeclared aliases. Exact owner approval is required before the same
implementation owner receives one additive correction.

## Closure revision 02 initial review

The owner approved closure revision 02, and the same Luna/xhigh owner returned additive candidate
`611959f69df9bb639509d7e9068e86fb8b3e4564`. That candidate adds the required binding, closes the
capability/state/evidence truth table, accepts bounded Unicode and removes the two undeclared
aliases. Its current focused, regression, strict-type and compile gates are green.

A second read-only helper audit and the reviewer independently reproduced two remaining findings:

1. **UIR1 implementation defect.** The unsafe-value validator rejects `://` and a short marker
   list, but ordinary identifiers `mailto:owner@example.test`, `javascript:alert(1)`,
   `authorization:bearer-token`, `prompt injection` and `C:drive-relative` are all accepted.
   The existing credential test supplies an unknown field name, so `extra="forbid"` turns it red
   without exercising the value validator.
2. **Correction-baseline evidence defect.** The final test module imports
   `ReferenceEvidenceBinding`, while baseline `faf3d05e07f83a8c7804313b4d3435d01da338b0`
   contains no such symbol. Running that final test against the named baseline stops at collection,
   so it does not reproduce the ticket-required named UIR1/UIR2/UIR4/UIR6 red cells. Green current
   tests and later reverse mutations cannot be presented as that historical baseline evidence.

Reviewer reproduction used ordinary public construction and direct Git object readback:

```text
mailto:owner@example.test      -> accepted
javascript:alert(1)            -> accepted
authorization:bearer-token     -> accepted
prompt injection               -> accepted
C:drive-relative               -> accepted
baseline has binding symbol    -> false
corrected test imports symbol  -> true
```

These are one `IMPLEMENTATION_DEFECT` and one `EVIDENCE_DEFECT` under the approved closure, not a
new requirement. Closure revision 02 therefore permits its single additive correction on the
same ticket, owner, worktree and branch. The correction must strengthen the value gate with direct
malicious-value cells and add reproducible candidate-baseline evidence that reaches the named UIR
behaviors rather than failing collection. No reset, amend, force, fresh branch or source integration
is permitted.

## Closure revision 02 correction review

The single permitted correction produced candidate
`07edaff11bfe981987288a9c1b6becb67c4e69ad`. It closes the five examples named by review revision
02, but the implementation remains a substring denylist and still accepts ordinary raw credential
or prompt payloads:

```text
access_token=abc                 -> accepted
Authorization Bearer abc         -> accepted
api-key=abc                       -> accepted
ignore previous instructions      -> accepted
```

This remains a UIR1 `IMPLEMENTATION_DEFECT`; enumerating the reviewer's latest examples is not a
closed boundary. The correction also changed no element/evidence artifact and the final test still
imports `ReferenceEvidenceBinding`, which is absent from baseline `faf3d05e...`. Baseline's own
tests contain neither the binding-mismatch cell nor the authorized-artifact refusal cell. The
required named UIR1/UIR2/UIR4/UIR6 baseline-red evidence therefore remains an `EVIDENCE_DEFECT`.

The helper's findings were reproduced by the reviewer with ordinary public construction and direct
Git object readback. Current focused/regression/type gates remain green, but green current behavior
does not replace the missing historical evidence and does not close the unsafe-value boundary.

This was closure revision 02's correction review. A second failure at the same closure revision
requires `CONVERGENCE_REVIEW_REQUIRED`; no third automatic correction, source integration or push
is allowed. Candidate `07edaff11bfe981987288a9c1b6becb67c4e69ad` remains preserved evidence on
the implementation branch only.

## Control-plane convergence conclusion

The convergence root cause is in the closure text, not implementer capability:

1. UIR1 froze a semantic denylist requirement without an executable predicate capable of deciding
   all admitted and rejected identifiers. Each correction could only enumerate newly observed
   examples, so the frozen clause itself made closure non-convergent.
2. The revision-02 baseline-red clause required named cells to execute on
   `faf3d05e07f83a8c7804313b4d3435d01da338b0`, but those cells depend on a type absent from that
   baseline and therefore stop at collection. The required evidence was structurally unreachable.

This is UIX-02's second `TICKET_DEFECT` cycle. The Luna/xhigh implementation owner followed the
then-effective ticket, returned bounded changes and green current-candidate gates, and is not the
bottleneck. No third correction or implementation dispatch is admissible.

Ticket document revision 08 proposed closure revision 03. The project owner approved its exact
LF-normalized digest on 2026-09-01, and ticket revision 09 now records revision 03 as effective. It
replaces the semantic denylist with a closed Unicode General Category predicate and marks the
unreachable baseline-red clause `SUPERSEDED` in favor of candidate-bound reviewer reverse
mutations with unreduced output.

The approval resolves the closure-text convergence decision only. It does not authorize a third
correction, allocate an implementation owner, integrate either preserved candidate, push,
publish, mutate a target or invoke a provider. The review therefore remains blocked at
`IMPLEMENTATION_NOT_AUTHORIZED`; candidate
`07edaff11bfe981987288a9c1b6becb67c4e69ad` remains non-integrated evidence.

One governance recommendation is recorded as owner-pending and is not applied here: add a closure
preflight to the control-plane flow for UIX-03 and every later ticket. Before a closure freezes, the
preflight should require an executable predicate for every universal boundary rule and should prove
that every named baseline-red cell can collect on its named baseline. No governance reference is
changed by this review.

## Closure revision 03 adversarial review

The reviewer bound a Terra/xhigh read-only `RESEARCH_HELPER` audit to docs candidate
`7abe2a997e2e68c7e3adb97442d2324c380d4094`, closure revision 03 and the direct ticket/review/
pitfall leaves. The helper returned `FINDINGS`; it modified nothing and did not approve, integrate,
commit, push or perform an external effect.

The material finding maps directly to UIR1. Revision 03 calls `L* / M* / N*` the complete positive
allowlist while also claiming zero-width characters reject. Python 3.11 independently reports:

```text
U+034F COMBINING GRAPHEME JOINER  -> category Mn
U+FE0F VARIATION SELECTOR-16      -> category Mn
U+0301 COMBINING ACUTE ACCENT     -> category Mn
revision-03 predicate(U+034F x 3) -> admitted
revision-03 predicate(U+FE0F x 3) -> admitted
```

This is a `TICKET_DEFECT`: an implementer can follow the executable allowlist exactly and violate
the closure's stated zero-width boundary. Ticket revision 10 therefore proposes closure revision
04 with a complete `L* / N*` allowlist, explicit `M*` rejection, named mark fixtures and UIRM6.
The owner approved this repair direction; at this review point exact artifact approval was still
pending. No implementation dispatch or third correction was admissible from direction authority.

## Closure revision 04 proposal audit and additive correction

The same Terra/xhigh read-only helper attacked exact proposal candidate
`f910b8db8c3fa28e4ce07b46317d87e383f771d0` and returned two material findings in one batch:

1. The proposal described `L* / N*`, but did not explicitly replace the operative UIR1 matrix row
   that still requires `L* / M* / N*`. Approval would therefore leave contradictory normative
   requirements.
2. The named bare mark fixtures were one or two code points long. They would remain rejected by
   the minimum-length gate after a mutation admitted `M*`, so UIRM6 could stay green for the wrong
   reason.

The reviewer independently reproduced both findings. Python 3.11 reports the bare values as
length one, the ordinary `e + U+0301` sequence as length two, and both `U+034F × 3` and
`e + U+0301 + e` as length three. Under `L* / M* / N*` those two length-valid mark values admit;
under `L* / N*` they reject. Precomposed `éab` remains a length-three `L*` positive control.

Ticket document revision 11 applied one additive proposal correction: at that review point exact
approval would replace all three operative grammar locations, the fixtures were length-valid, and
UIRM6 named the exact mutation and red assertions. This correction was still a proposal; it was
neither exact owner approval nor implementation authority.

## Closure revision 04 proposal correction review

The same Terra/xhigh read-only helper attacked exact corrected-proposal candidate
`04b4bf750972976c04ac18ce54c286b147092de0` against parent
`f910b8db8c3fa28e4ce07b46317d87e383f771d0` and returned `NO_FINDINGS`. The helper modified
nothing and held no approval, integration, dispatch or external-effect authority.

The reviewer independently reproduced the candidate-bound evidence:

```text
value                    length/categories       L*/N*   L*/M*/N*
U+034F × 3               3 / Mn,Mn,Mn            reject  admit
U+FE0F × 3               3 / Mn,Mn,Mn            reject  admit
e + U+0301 + e           3 / Ll,Mn,Ll            reject  admit
éab                      3 / Ll,Ll,Ll            admit   admit
éab == NFD(éab)                                    false
```

The proposal explicitly names every operative revision-03 grammar location that exact approval
must replace, and no third-correction, implementation, integration, push, publication or external
effect authority appears in the ticket, review, registry or pitfall leaves. Ticket revision 11's
LF-normalized digest and every direct index edge match. The corrected proposal was therefore ready
for exact owner approval and remained `NON_DISPATCHABLE` at this review point.

## Closure revision 04 exact approval writeback

The project owner approved exact ticket document revision 11 at candidate authority commit
`515e2fd81f8b54030c5fd27abbd43cd63d5df3bc`, LF-normalized leaf SHA-256
`348a5c2f12a773b77898616b71ce70947625f1f9fb6db021b0c4ca171fa437fb`, on 2026-09-01
(Asia/Taipei). Ticket revision 12 records revision 04 as the effective closure and marks revision
03's `L* / M* / N*` grammar historical and `SUPERSEDED`.

The operative frozen-rule bullet and UIR1 row now use only `L* / N*`, the named mark fixtures are
length-valid, and UIRM6 names the `L* / N* -> L* / M* / N*` mutation and its direct red assertions.
This approval changes only the acceptance closure. It does not allocate an implementation owner,
authorize a third correction, integrate either preserved candidate, push, publish, mutate a target
or invoke a provider. UIX-02 remains `NON_DISPATCHABLE` until separate implementation authority.

## Closure revision 04 approval-writeback adversarial review

The same Terra/xhigh read-only helper attacked exact approval-writeback candidate
`803f853fac75d7761fb6f62f40249eae469cb6cc` and returned one material consistency finding. The
ticket, review and both direct indexes recorded closure revision 04 as approved, while Pitfall C14
still said its exact leaf/digest was pending approval. The stale sentence granted no unsafe
authority, but made lifecycle readback contradictory.

The reviewer independently reproduced the mismatch with direct committed-object reads. This
revision applies one additive docs-only correction to C14: revision 04 is exact-approved and
written back, while third correction, implementation dispatch, integration, push, publication and
external effects remain unauthorized. Ticket revision 12 and its digest are unchanged.

## Closure revision 04 approval-writeback correction review

The same Terra/xhigh read-only helper attacked exact corrected candidate
`6110c0d79ac663832d57e9bb5d17d5dbb9e27d80` against parent
`803f853fac75d7761fb6f62f40249eae469cb6cc` and returned `NO_FINDINGS`. The reviewer independently
confirmed the ancestry, direct LF-normalized ticket/review digests, index edges, Unicode predicate
matrix and clean diff.

Ticket, review, both indexes and Pitfall C14/C15/C16 now agree: closure revision 04 is
exact-approved and effective; ticket revision 12 remains `NON_DISPATCHABLE`; the initial and
revision-02 lanes are consumed/exhausted; no third correction, implementation dispatch,
integration, push, publication, provider or external effect is authorized. This closes the
approval-writeback document review only and does not approve implementation.

## Closure revision 04 implementation review — 2026-09-05

The owner authorized execution and the current-session reviewer reused the original Luna/xhigh
owner. Candidate `18ed02c736812e2e7fab738dc2b8a7036d1da987` is a reviewer-created additive
commit over `07edaff11bfe981987288a9c1b6becb67c4e69ad`, not approval or integration. Only the
declared private module and test changed. Focused plus UIX-01/Router regression returned 75 passed
and 216 subtests passed. The unchanged baseline's focused and strict-type gates also passed.

Adversarial plan: closure 04, REQUIRED by owner, one reused Terra/xhigh RESEARCH_HELPER,
READ_ONLY_INTENT_ONLY, NO_EXTERNAL_EFFECT; SPEC_GAP, BOUNDARY_DATA, STATE_TRANSITION,
AUTHORIZATION, CONSISTENCY, REGRESSION and OBSERVABILITY. It inspected committed blobs and returned
FINDINGS without changes or approval. The current-session reviewer independently reproduced every
helper finding, plus the additional findings below, against this exact candidate.

### One batched correction — frozen closure unchanged

| ID | Classification / cell | Finding and required correction |
| --- | --- | --- |
| R04-F1 | IMPLEMENTATION_DEFECT / UIR1, UIR4 | Strict artifact construction accepts integer `1` and float `1.0` as manual acknowledgement and transforms them into `True`. Require the literal boolean without numeric coercion, including nested request validation; pin positive true and missing/false/null/numeric/string negatives. |
| R04-F2 | EVIDENCE_DEFECT / UIR1, UIR2, UIR4 | Defaulting the required acknowledgement to true leaves UIR4 green; lowering the ID minimum from 3 to 1 leaves UIR1 green. Pin both length boundaries and each required ref/digest/acknowledgement independently, keeping all other fields valid so another missing field cannot mask the mutation. Use named/subtest negative values so UIRM6 reports both length-valid CGJ and decomposed-mark rejection assertions, not only the loop's first failure. |
| R04-F3 | EVIDENCE_DEFECT / UIR7 | Both aliased `Any` and dynamic builtin import with an attribute call leave the source gate green. The AST/source guard must inspect actual imported symbols/aliases and dynamic builtins/attribute calls at the production source boundary, with discriminating negative fixtures, not the test's own source. |
| R04-F4 | EVIDENCE_DEFECT / UIR3 | Restricting the early unauthorized wait to rendered evidence leaves UIR3 green. Pin every evidence variant and authority-before-binding/duplicate/target/state ordering with otherwise constructible requests. |
| R04-F5 | EVIDENCE_DEFECT / UIR6 | Removing only brief-ID binding comparison leaves UIR6 green. Removing only digest uniqueness also leaves UIR6 green because the fixture simultaneously duplicates refs. Pin request/brief/content mismatches and each rendered/artifact uniqueness violation independently; include the remaining finite state/evidence cross-pairs. |
| R04-F6 | EVIDENCE_DEFECT / UIR5 | Restricting ANY to TERMINAL leaves UIR5 green. Pin ANY against every finite actual target for rendered and artifact evidence and the declared mismatches. |

The existing authorized same-ticket lane receives this one additive correction on the same branch;
the owner does not commit or push. No new closure or architecture is proposed. Completion must
include evidence references for the exact changes and UIR/UIRM/type/regression/compile results.
The reviewer will create the next candidate, rerun independent mutations, and retain final
conclusion responsibility. Integration, push, release and external effects remain unauthorized.

### Independent unreduced reproduction

All commands ran directly in `.worktrees/plugin-adoption-quality-uix-02`, with no output-reduction
wrapper. Each mutation changed only the production module temporarily. The raw source Git blob hash
was `276af7788be3b307a3cb8be22211588c13f1d6d4` before and after restoration; the restored
focused suite returned `7 passed`. No forbidden dynamic call was executed: that mutation was in
a literal `if False` branch and solely tested AST detection.

Numeric acknowledgement probe used the ordinary `ArtifactReferenceEvidence.model_validate`
constructor with valid binding/refs/digest and each displayed input:

```text
True bool ADMITTED True
1 int ADMITTED True
1.0 float ADMITTED True
False bool REJECTED
None NoneType REJECTED
'true' str REJECTED
```

#### Aliased type (reviewer-selected independent door)

Add `from typing import Any as Unchecked` and `reviewer_alias_probe: Unchecked = "opaque"`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir7
.                                                                        [100%]
1 passed, 6 deselected in 0.61s
```

Exit code 0; zero red is a finding, not a pass.

#### Missing acknowledgement

Change `owner_manual_open_acknowledgement: Literal[True]` to the same declaration with `= True`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir4
.                                                                        [100%]
1 passed, 6 deselected in 0.64s
```

Exit code 0; zero red is a finding, not a pass.

#### Brief binding

Replace only `and binding.brief_id == request.brief_id` with `and True`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir6
.                                                                        [100%]
1 passed, 6 deselected in 0.60s
```

Exit code 0; zero red is a finding, not a pass.

#### Dynamic import / attribute call

Add `if False: __import__("os").system("never-executed")` on separate indented lines; never execute it.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir7
.                                                                        [100%]
1 passed, 6 deselected in 0.58s
```

Exit code 0; zero red is a finding, not a pass.

#### Authority variants

Add `and isinstance(trusted_request.evidence, RenderedReferenceEvidence)` to the unauthorized early-wait condition.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir3
.                                                                        [100%]
1 passed, 6 deselected in 0.60s
```

Exit code 0; zero red is a finding, not a pass.

#### Overlapping duplicate checks

Replace only `or len({evidence.desktop_digest, evidence.mobile_digest}) != 2` with `or False`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir6
.                                                                        [100%]
1 passed, 6 deselected in 0.58s
```

Exit code 0; zero red is a finding, not a pass.

#### Finite ANY coverage

Require `actual_target is TERMINAL` in the ANY matching arm; preserve exact-target matching.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir5
.                                                                        [100%]
1 passed, 6 deselected in 0.58s
```

Exit code 0; zero red is a finding, not a pass.

#### Minimum length

Change only `Field(min_length=3, max_length=128)` to `Field(min_length=1, max_length=128)`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir1
.                                                                        [100%]
1 passed, 6 deselected in 0.61s
```

Exit code 0; zero red is a finding, not a pass.

## Closure revision 04 correction review — 2026-09-05

The same Luna/xhigh owner returned one additive correction. The current-session reviewer committed
candidate `b419954bc57777661d7522247ffc26977f668ca7` on the existing implementation branch.
Its parent is `18ed02c736812e2e7fab738dc2b8a7036d1da987`; neither candidate is integrated.
The same read-only Terra/xhigh helper audited committed objects and returned FINDINGS. The
current-session reviewer reproduced those findings and selected an additional independent door:
an aliased `typing.cast` call, rather than the implementer's reported aliased-Any/dynamic-import
mutations. The helper never approved, edited, dispatched or performed an external effect.

### Verified improvement and remaining findings

The strict acknowledgement correction is real: numeric inputs reject both at direct artifact
construction and within nested requests. Temporarily bypassing the new before-validator makes all
four named numeric assertions fail. The reviewer also observed red assertions for the repaired
minimum length, marks, brief binding, digest uniqueness, finite ANY targets, authority variants and
the originally reported Any/dynamic-import probes. Byte-exact restoration returns the suite green.

| Finding | Closure / classification | Candidate-bound result |
| --- | --- | --- |
| R04-C1 | UIR7 / EVIDENCE_DEFECT; R04-F3 remains open | Aliased `cast`, qualified `typing.Any`, and indirect `__builtins__["__import__"]` all leave UIR7 green. Checking the original Any symbol fixed that probe, but does not close the frozen no-cast/no-Any/no-dynamic-lookup source boundary. |
| R04-C2 | UIR6 / EVIDENCE_DEFECT; R04-F5 remains open | Removing observation-ref membership **and changing the expected set cardinality from 3 to 2** leaves UIR6 green. This is the exact reproduced mutation; removing only the member would reject legitimate evidence and is not the claimed proof. Desktop/observation and mobile/observation collisions are not independently pinned. |
| R04-C3 | UIRM3 -> UIR4 / EVIDENCE_DEFECT; R04-F2 remains open | Giving the mandatory acknowledgement a default true leaves the specified UIR4 green. UIR1 correctly turns red instead, so this is an unsatisfied named evidence mapping, not a claim that the unmutated implementation accepts missing acknowledgement. |

These three families are within the unchanged frozen closure. No new architecture, requirement,
provider operation or production exploit is alleged. The other batched fixes are retained.
The final conclusion is **BLOCKED / EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED**, not approval.
Per `CodeReview.md` section 5, this closure has consumed its initial and single correction review.
The reviewer has not issued a third correction. Further work requires control-plane convergence
and the necessary owner authority; no gate integration, push or publication was attempted.

### Verification and applicability

- Direct focused/regression command: `py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py tests/test_ui_codesign_contracts.py tests/test_workflow_router.py` — 75 passed, 275 subtests passed (7 focused tests / 59 focused subtests).
- `py -3.11 -B -m mypy --strict --no-incremental library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py` — Success: no issues found in 2 source files.
- `py -3.11 -B -m compileall -q library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py` — exit 0.
- Primary-path smoke is the ordinary reducer admission exercised directly by UIR2/UIR4.
- Worktree and branch are unchanged; source/test diff remains within the declared boundary.
- XSS, renderer/browser/provider, filesystem/network/process effects, tenant persistence,
  migrations and deployment are not exercised by this pure metadata module. No external-effect
  readiness or actual rendered-output claim follows from these tests.
- This is a BLOCKED review, so green suite/type results do not claim completion of all UIR/UIRM gates.

### Exact correction-candidate mutation transcripts

All following runs use candidate `b419954bc57777661d7522247ffc26977f668ca7` in the existing
UIX-02 worktree. The production module, not a copied test predicate, was temporarily patched.
Commands use standard-library unittest directly, with complete unreduced output and no wrapper.
The raw source blob before and after restoration is `f1c1adb2a9433ae2c246ccb182639cdfce3b182d`.
Dynamic-import probes sit in literal `if False` branches and were never executed.


#### r2_cast_alias

Exact temporary replacement:

```diff
-from typing import Annotated, Literal, Self, TypeAlias, Union
+from typing import Annotated, Literal, Self, TypeAlias, Union
+from typing import cast as reinterpret
+
+
+def _reviewer_alias_cast(value: object) -> str:
+    return reinterpret(str, value)
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
.
----------------------------------------------------------------------
Ran 1 test in 0.029s

OK
```

Exit code 0.

#### r2_missing_ack

Exact temporary replacement:

```diff
-    owner_manual_open_acknowledgement: Literal[True]
+    owner_manual_open_acknowledgement: Literal[True] = True
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir4_absence_or_decline_uses_artifact_fallback
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

Exit code 0.

#### r2_qualified_any

Exact temporary replacement:

```diff
-from typing import Annotated, Literal, Self, TypeAlias, Union
+from typing import Annotated, Literal, Self, TypeAlias, Union
+import typing as t
+
+probe: t.Any = "opaque"
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
.
----------------------------------------------------------------------
Ran 1 test in 0.026s

OK
```

Exit code 0.

#### r2_indirect_import

Exact temporary replacement:

```diff
-_SHA256_PATTERN = r"^[0-9a-f]{64}$"
+_SHA256_PATTERN = r"^[0-9a-f]{64}$"
+
+if False:
+    dynamic_importer = __builtins__["__import__"]
+    dynamic_importer("os")
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
.
----------------------------------------------------------------------
Ran 1 test in 0.027s

OK
```

Exit code 0.

#### r2_observation_ref

Exact temporary replacement:

```diff
-                    evidence.renderer_observation_ref,
-                }
-            )
-            != 3
+                }
+            )
+            != 2
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
.
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

Exit code 0.

#### r2_dynamic_import

Exact temporary replacement:

```diff
-_SHA256_PATTERN = r"^[0-9a-f]{64}$"
+_SHA256_PATTERN = r"^[0-9a-f]{64}$"
+
+if False:
+    __import__("os").system("never-executed")
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
F
======================================================================
FAIL: test_uir7_ast_proves_private_no_effect_boundary (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 803, in test_uir7_ast_proves_private_no_effect_boundary
    self.assertTrue(names.isdisjoint(forbidden_names))
AssertionError: False is not true

----------------------------------------------------------------------
Ran 1 test in 0.032s

FAILED (failures=1)
```

Exit code 1.

#### r2_authority_variants

Exact temporary replacement:

```diff
-    if trusted_request.capability_state is RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED:
+    if trusted_request.capability_state is RendererCapabilityState.AVAILABLE_NOT_AUTHORIZED and isinstance(trusted_request.evidence, RenderedReferenceEvidence):
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission
FFF
======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (evidence='artifact')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 402, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: AdmittedArtifactDecision(kind='ADMITTED_ARTIFACT', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.ARTIFACT_ONLY: 'ARTIFACT_ONLY'>, evidence=ArtifactReferenceEvidence(kind='ARTIFACT_ONLY', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_artifact_ref='artifactdesktop', mobile_artifact_ref='artifactmobile', artifact_set_digest='dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd', owner_manual_open_acknowledgement=True)) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (evidence='unavailable')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 402, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.STATE_EVIDENCE_MISMATCH: 'STATE_EVIDENCE_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

======================================================================
FAIL: test_uir3_unauthorized_capability_waits_without_admission (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir3_unauthorized_capability_waits_without_admission) (ordering='state-before-authority')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 461, in test_uir3_unauthorized_capability_waits_without_admission
    self.assertIsInstance(decision, RendererWaitDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.STATE_EVIDENCE_MISMATCH: 'STATE_EVIDENCE_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererWaitDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (failures=3)
```

Exit code 1.

#### r2_duplicate_masking

Exact temporary replacement:

```diff
-            or len({evidence.desktop_digest, evidence.mobile_digest}) != 2
+            or False
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
F
======================================================================
FAIL: test_uir6_state_duplicate_and_identity_mismatch_refuse (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse) (duplicate_dimension='rendered-digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 664, in test_uir6_state_duplicate_and_identity_mismatch_refuse
    self.assertIsInstance(duplicate_result, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='screenshotdesktop', mobile_screenshot_ref='screenshotmobile', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.006s

FAILED (failures=1)
```

Exit code 1.

#### r2_any_finite_targets

Exact temporary replacement:

```diff
-    return request.renderer_target is RendererTarget.ANY or request.renderer_target is request.actual_target
+    return (request.renderer_target is RendererTarget.ANY and request.actual_target is RendererTarget.TERMINAL) or request.renderer_target is request.actual_target
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target
FFFFFF
======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (rendered_any_target=<RendererTarget.DOM: 'DOM'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 535, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_target, AdmittedRenderedDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedRenderedDecision'>

======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (rendered_any_target=<RendererTarget.NATIVE_ENGINE: 'NATIVE_ENGINE'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 535, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_target, AdmittedRenderedDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedRenderedDecision'>

======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (rendered_any_target=<RendererTarget.NATIVE_MOBILE: 'NATIVE_MOBILE'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 535, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_target, AdmittedRenderedDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedRenderedDecision'>

======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (artifact_any_target=<RendererTarget.DOM: 'DOM'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 548, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_artifact, AdmittedArtifactDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedArtifactDecision'>

======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (artifact_any_target=<RendererTarget.NATIVE_ENGINE: 'NATIVE_ENGINE'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 548, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_artifact, AdmittedArtifactDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedArtifactDecision'>

======================================================================
FAIL: test_uir5_target_mismatch_and_any_target (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir5_target_mismatch_and_any_target) (artifact_any_target=<RendererTarget.NATIVE_MOBILE: 'NATIVE_MOBILE'>)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 548, in test_uir5_target_mismatch_and_any_target
    self.assertIsInstance(any_artifact, AdmittedArtifactDecision)
AssertionError: RendererRefusedDecision(kind='REFUSED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reason=<RendererRefusalReason.TARGET_MISMATCH: 'TARGET_MISMATCH'>) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.AdmittedArtifactDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.007s

FAILED (failures=6)
```

Exit code 1.

#### r2_alias_any

Exact temporary replacement:

```diff
-from typing import Annotated, Literal, Self, TypeAlias, Union
+from typing import Annotated, Literal, Self, TypeAlias, Union
+from typing import Any as Unchecked
+
+reviewer_alias_probe: Unchecked = "opaque"
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary
F
======================================================================
FAIL: test_uir7_ast_proves_private_no_effect_boundary (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir7_ast_proves_private_no_effect_boundary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 772, in test_uir7_ast_proves_private_no_effect_boundary
    self.assertFalse(
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1 test in 0.023s

FAILED (failures=1)
```

Exit code 1.

#### r2_brief_binding

Exact temporary replacement:

```diff
-        and binding.brief_id == request.brief_id
+        and True
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse
F
======================================================================
FAIL: test_uir6_state_duplicate_and_identity_mismatch_refuse (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir6_state_duplicate_and_identity_mismatch_refuse)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 720, in test_uir6_state_duplicate_and_identity_mismatch_refuse
    self.assertIsInstance(changed_brief_result, RendererRefusedDecision)
AssertionError: AdmittedRenderedDecision(kind='ADMITTED_RENDERED', request_ref='requestuiref', brief_id='briefuidashboard', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', renderer_state=<ReferenceRendererState.RENDERED_AVAILABLE: 'RENDERED_AVAILABLE'>, evidence=RenderedReferenceEvidence(kind='RENDERED_AVAILABLE', binding=ReferenceEvidenceBinding(request_ref='requestuiref', brief_id='briefother', approved_content_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'), desktop_screenshot_ref='screenshotdesktop', mobile_screenshot_ref='screenshotmobile', desktop_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', mobile_digest='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc', renderer_observation_ref='rendererobservation')) is not an instance of <class 'library.workflow_router.ui_reference_renderer_admission.RendererRefusedDecision'>

----------------------------------------------------------------------
Ran 1 test in 0.005s

FAILED (failures=1)
```

Exit code 1.

#### r2_marks

Exact temporary replacement:

```diff
-    if not all(unicodedata.category(character)[0] in ("L", "N") for character in value):
+    if not all(unicodedata.category(character)[0] in ("L", "M", "N") for character in value):
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
FFF
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='\\u034f\\u034f\\u034f')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 260, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='\\ufe0f\\ufe0f\\ufe0f')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 260, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='e\\u0301e')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 260, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.022s

FAILED (failures=3)
```

Exit code 1.

#### r2_minimum_length

Exact temporary replacement:

```diff
-    Field(min_length=3, max_length=128),
+    Field(min_length=1, max_length=128),
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
FF
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='a')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 266, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (identifier='ab')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 266, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.020s

FAILED (failures=2)
```

Exit code 1.

#### r2_numeric_ack

Exact temporary replacement:

```diff
-        if type(value) is not bool or value is not True:
+        if False:
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
FFFF
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (acknowledgement='1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 190, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (acknowledgement='1.0')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 190, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (nested_acknowledgement='1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 217, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip) (nested_acknowledgement='1.0')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 217, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.032s

FAILED (failures=4)
```

Exit code 1.

#### r2_ack_uir1

Exact temporary replacement:

```diff
-    owner_manual_open_acknowledgement: Literal[True]
+    owner_manual_open_acknowledgement: Literal[True] = True
```

```text
py -3.11 -B -m unittest tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip
F
======================================================================
FAIL: test_uir1_public_variants_strictly_round_trip (tests.test_ui_reference_renderer_admission.UIReferenceRendererAdmissionTests.test_uir1_public_variants_strictly_round_trip)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\.worktrees\plugin-adoption-quality-uix-02\tests\test_ui_reference_renderer_admission.py", line 199, in test_uir1_public_variants_strictly_round_trip
    with self.assertRaises(ValidationError):
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 1 test in 0.007s

FAILED (failures=1)
```

Exit code 1.

#### Restoration readback

```text
f1c1adb2a9433ae2c246ccb182639cdfce3b182d
.......
----------------------------------------------------------------------
Ran 7 tests in 0.077s

OK
```

The final missing-acknowledgement comparison was also restored by the exact inverse patch.
Final full-suite readback returned 75 passed and 275 subtests passed in 4.66s; the raw source hash
remained `f1c1adb2a9433ae2c246ccb182639cdfce3b182d`, `git diff --check` passed and
`git status --short` returned no changes.
