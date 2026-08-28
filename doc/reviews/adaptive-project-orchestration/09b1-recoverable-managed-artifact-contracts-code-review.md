# R09B1 Recoverable Managed-Artifact Contracts — Code Review

| Field | Value |
| --- | --- |
| Review identity | `REVIEW-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS-01` |
| Ticket authority | `TICKET-ADAPTIVE-R09B1-RECOVERABLE-MANAGED-ARTIFACT-CONTRACTS` on `main` at `da537bc10afda6ea32917e31a9613dd648e5a7d2` |
| SPEC / Context / ADR | Adaptive Project Orchestration Revision 11 / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-11` / `ADR-20260828-032` |
| Reviewed candidates | initial `1bca660fa75caf82f84920d2ad1044b740f185d9`; one additive correction `0b48120ed145a3c9a43989e2b353d2611a6f3052`; branch `implement/adaptive-r09b1-recovery-contracts`; baseline `da537bc10afda6ea32917e31a9613dd648e5a7d2` |
| Roles | Luna/xhigh implementation owner; Terra/xhigh reviewer and sole integrator; two isolated Terra/xhigh read-only evidence lanes |
| Conclusion | `BLOCKED / EVIDENCE_ORDERING_DEVIATION / INTEGRATED_ALREADY / OWNER_DECISION_REQUIRED` |

## Admission and scope

The reviewer independently read the ticket, Revision 11 requirement/context/ADR, candidate
ancestry, worktree identity and the three declared changed paths. The implementation owner did not
commit or push. The lane was synchronous and needed no runner, queue, receipt, descriptor, gateway
or host-workspace readback. The candidate adds strict public value contracts and their focused tests
only; it has no writer, filesystem, journal, lock, resolver, process, network, provider, target,
publication, installation, release or deployment effect. XSS, UI, Secret, provider and deployment
checks are therefore not applicable; source/import inspection is the executable boundary evidence.

## Findings and convergence

The first reviewer-bound candidate accepted duplicate/non-canonical `APPLIED` artifact references
and generic body/locator-shaped recovery metadata. Both independent Terra/xhigh evidence lanes
reproduced those findings. The single permitted additive correction introduced lexically canonical,
unique refs and the constrained `RecoveryEvidenceRef` form. Both final lanes returned `NO_FINDINGS`.

After the document gate had already integrated the corrected candidate, the reviewer detected that
the ticket’s required additional reviewer-owned counter-mutation had not yet been performed. An
isolated detached snapshot then widened the recovery-reference validator to the generic metadata
pattern: the focused test turned red with three unfiltered assertions for `snapshot-body`,
`exception-detail`, and `workspace-record`. Exact restoration returned the source blob to
`38e7719408f4ea588a306f6dc950cefc87f09da9` and the focused suite green. This establishes no source
defect, but it cannot truthfully be represented as pre-integration evidence. The required review
sequence was violated, so this review cannot issue `APPROVED` without an owner disposition.

## Executed evidence

On corrected candidate `0b48120ed145a3c9a43989e2b353d2611a6f3052`:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_managed_artifact_recovery_contracts.py
  7 passed, 13 subtests passed
py -3.11 -m pytest -q -p no:cacheprovider tests/test_target_document_management.py tests/test_managed_artifact_planning.py tests/test_workflow_artifact_tree.py
  31 passed, 35 subtests passed
py -3.11 -m mypy --strict library/workflow_router/target_document_contracts.py tests/test_managed_artifact_recovery_contracts.py
  Success: no issues found in 2 source files
py -3.11 -m compileall -q library/workflow_router/target_document_contracts.py tests/test_managed_artifact_recovery_contracts.py
  exit 0
git diff --check da537bc10afda6ea32917e31a9613dd648e5a7d2 0b48120ed145a3c9a43989e2b353d2611a6f3052
  exit 0
```

The final adversarial lane independently rejected duplicate and reverse-order refs, body/exception/
path/workspace recovery strings, wrong hex case and wrong token lengths, malformed JSON and invalid
status/failure pairs. The additional research lane independently confirmed the constrained recovery
type, ref-to-digest positional pairing, unchanged legacy exports and absence of effect imports.

## Integration and required disposition

`admit_document_mutation` returned `INTEGRATED` with
`integrated_commit = 0b48120ed145a3c9a43989e2b353d2611a6f3052`; a non-force push and direct
`origin/main` readback both returned the same SHA. That source integration is factual but preceded
the reviewer’s required own counter-mutation. No successor ticket, publication, release,
installation or deployment is authorized. The owner must choose whether to accept this recorded
process deviation or require a separately approved recovery action.
