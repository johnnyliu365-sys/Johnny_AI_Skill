# UIX-02 reference-renderer evidence admission — code review

| Field | Value |
| --- | --- |
| Review ID / revision | `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` / `06` |
| Ticket / closure | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` document revision `10` / effective but blocked `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02` revision `03`; revision 04 is `OWNER_EXACT_APPROVAL_PENDING` |
| Authority commit | `8f5e59ca3ac13a00bcaf6c5b5f54e49ad4872267` |
| Local control-plane proposal commit | `377b45cc7a4ac038d00b8f52a5a14b282dbde337`; intentionally unpushed under the 2026-09-01 owner authority |
| Owner approval source | Project owner, 2026-09-01 (Asia/Taipei): candidate authority commit `a616e561423fd40508dfbebcb33b798e071b5462`, ticket revision-08 LF-normalized SHA-256 `7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953` |
| Candidate / baseline | `07edaff11bfe981987288a9c1b6becb67c4e69ad` / `faf3d05e07f83a8c7804313b4d3435d01da338b0` |
| Branch / owner | `implement/plugin-adoption-quality-uix-02` / `implementation-standard` |
| Reviewer / helper | `ticket-review` / one read-only `RESEARCH_HELPER` |
| Result | `BLOCKED / TICKET_DEFECT_CYCLE_03 / CLOSURE_REVISION_04_PROPOSED / OWNER_EXACT_APPROVAL_PENDING / IMPLEMENTATION_NOT_AUTHORIZED / CANDIDATE_NOT_INTEGRATED` |

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
The owner approved this repair direction, but exact revision-10 leaf approval remains pending.
No implementation dispatch or third correction is admissible before that exact approval.
