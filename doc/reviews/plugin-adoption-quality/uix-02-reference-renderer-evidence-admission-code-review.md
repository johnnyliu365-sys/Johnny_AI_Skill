# UIX-02 reference-renderer evidence admission — code review

| Field | Value |
| --- | --- |
| Review ID / revision | `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` / `02` |
| Ticket / closure | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` document revision `05` / `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02` revision `02` |
| Authority commit | `542f356a6affaa6e4b1b2e73e5594325fbfbe37b` |
| Candidate / baseline | `611959f69df9bb639509d7e9068e86fb8b3e4564` / `faf3d05e07f83a8c7804313b4d3435d01da338b0` |
| Branch / owner | `implement/plugin-adoption-quality-uix-02` / `implementation-standard` |
| Reviewer / helper | `ticket-review` / one read-only `RESEARCH_HELPER` |
| Result | `CHANGES_REQUESTED / IMPLEMENTATION_DEFECT / EVIDENCE_DEFECT / CANDIDATE_NOT_INTEGRATED` |

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
