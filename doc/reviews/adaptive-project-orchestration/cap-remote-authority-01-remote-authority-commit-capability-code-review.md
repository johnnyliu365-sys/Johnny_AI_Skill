# CAP-REMOTE-AUTHORITY-01 — code review

| Field | Value |
| --- | --- |
| Ticket / Closure | `CAP-REMOTE-AUTHORITY-01` / Revision 13 `AC-17R13`, TDD item 26, `RAC1`–`RAC7` and `RACM1`–`RACM3` |
| Candidate / source baseline | `678338599529b80b1f7aafeccb111a228702f1e3` on `implement/cap-remote-authority-01` / `3f1499e6aff6a0f4638459f7ca2e4b6b4a0c8919` |
| Ticket authority read | `0bf4da9a440d43ee31af654465345d064b6ad607:modules/tickets/adaptive-project-orchestration/cap-remote-authority-01-remote-authority-commit-capability.md` |
| Conclusion | `BLOCKED / REQUIREMENT_CHANGED / CANDIDATE_NOT_INTEGRATED` |
| Reviewer | `ticket-review` semantic profile; sole conclusion and integrator |
| External state | No second live probe was run. Direct post-halt readback showed `refs/heads/main = 0bf4da9a440d43ee31af654465345d064b6ad607` and the isolated test ref absent. |

## Admission and evidence

The candidate contains exactly `tests/test_remote_authority_commit_capability.py`; the worktree
was clean after the reviewer committed it. The initial authorized live probe did not retain its
bounded result, so its candidate SHAs and provider outcome are not evidence and are not used here.
The isolated ref is absent after that attempt; no second remote effect was issued.

Reviewer static verification, with `CAP_REMOTE_AUTHORITY_01_LIVE_ACTIVATION` explicitly absent:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_remote_authority_commit_capability.py
10 passed, 1 skipped
py -3.11 -m mypy --strict tests/test_remote_authority_commit_capability.py
Success: no issues found in 1 source file
py -3.11 -m compileall -q tests/test_remote_authority_commit_capability.py
git diff --check
PASS
```

The candidate's normal test invocation made zero live calls under the absent activation gate. The
implementer also recorded each `RACM1`–`RACM3` red/restored result before the candidate commit.
Those green static checks do not discharge the blocked external-effect boundary below.

## Independent adversarial review

The reviewer bound both helpers to candidate `6783385` in detached read-only worktrees. The race
helper attacked `CONCURRENCY`, `AUTHORIZATION`, `IDEMPOTENCY` and `OBSERVABILITY`; the policy helper
attacked `AUTHORIZATION`, `CONSISTENCY`, `ERROR_PARTIAL_FAILURE` and cleanup/ABA behavior.

The policy helper reported one procedural deviation: its first failed in-memory seam may have made
one public `git ls-remote` read before it halted that seam. It performed no push, policy change,
configuration or deletion. That read is excluded from evidence; all later reproductions replaced
remote helpers completely. The reviewer independently reproduced every finding below with local
stubs and no remote helper invocation.

## Blocking findings

| ID | Classification | Closure item | Finding |
| --- | --- | --- | --- |
| `CR-CAPREMOTE-01` | `REQUIREMENT_CHANGED` | `RAC1`, `RAC3`, `RAC4`, external-effect activation | The live entry accepts caller-provided environment, evidence path, reservation path and runner. The source itself exposes the activation literal. A caller can choose a fresh path or delete a normal reservation and replay the effect. A host-protected, owner-issued one-shot external-effect grant is therefore required; the ticket's test-only boundary cannot supply it. |
| `CR-CAPREMOTE-02` | `IMPLEMENTATION_DEFECT` | `RAC3`, `RAC5`, cleanup rule | Cleanup removes protection and deletes any present isolated ref without proving it still equals a writer-owned expected SHA or using a conditional deletion lease. A concurrent writer can replace/recreate the ref and have its bytes deleted. |
| `CR-CAPREMOTE-03` | `IMPLEMENTATION_DEFECT` | `RAC6`, cleanup rule | If required pre-cleanup evidence persistence fails, the candidate changes its result to blocked but still starts cleanup. This violates the rule that preserved bounded evidence precedes cleanup. |

### Reviewer reproductions

All three used imported candidate code with `_direct_actor`, `_direct_observation`, `_run_exit`,
provider helpers and cleanup effects replaced locally; no remote command was callable.

```text
caller_selected_paths_replay ACTIVATED ACTIVATED 2
cleanup_foreign_ref ABSENT_CONFIRMED None
cleanup_after_persistence_failure BLOCKED ['called']
```

The first line proves two caller-selected reservation namespaces invoke the local runner twice.
The second proves a candidate expected SHA of `a…` does not prevent deletion after a simulated
external ref becomes `d…`. The third proves cleanup is invoked after the required pre-cleanup
evidence writer returns false.

## Required route

`CR-CAPREMOTE-01` changes the trust boundary, not merely an implementation detail. Do not issue a
second correction or another remote probe against this Closure revision. Return
`ImplementationReturn.CHANGE_DETECTED -> REQUIREMENT_CHANGED` to Architecture/Grill. The owner
must decide whether a host-owned, non-forgeable, one-shot external-effect grant can exist without
turning the same-lifetime dispatch lane into receipt/runner/descriptor infrastructure. Any new
design must also make cleanup conditional on the last writer-owned remote identity and refuse all
cleanup when durable pre-cleanup evidence cannot be retained.

Until that decision, candidate `6783385`, the unintegrated harness, the old live attempt and its
expired scope are evidence only. They authorize no remote writer, retry, cleanup, release or
deployment.
