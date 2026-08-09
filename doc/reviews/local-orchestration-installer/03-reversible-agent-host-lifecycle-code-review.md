# 03 Reversible Agent Host Capability Gate - Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `03-reversible-agent-host-lifecycle` |
| Result | `APPROVED / READY_TO_MERGE` after one correction review |
| Reviewer | Codex / current `main` worktree |
| Single branch | `codex/implementation-host-capability-gate-03` |
| Closure | `CLOSURE-LOCAL-INSTALL-T03-01` / `H1..H8` |

## Boundary and revisions

The reviewed range is dispatch baseline `963319b`, implementation
`16597b6`, and docs-only handoff `62394f1`. The implementation changes exactly
the four authorized production files and one test; the handoff changes only
`doc/WorkProgressReport.md`. The sole implementation worktree is clean. No
Ticket-01/02 source, live host adapter, real command, subprocess/network/login,
target-project write, packaging, schedule, push, deployment, extra branch or
extra worktree is present.

## Independent verification

| Check | Evidence |
| --- | --- |
| Scope / ceiling | Production `545 / 550`; test `317 / 450` non-blank lines. `git diff --check`, ancestry and exact commit-boundary checks passed. |
| Green run | Project Python 3.11 exact unittest: 8/8 passed. Full discovery: 155/155 passed. Strict mypy over five authorized files: no issues. In-memory compile of all five files passed. |
| Actual Git | A supported recorded fake and an executable-unavailable blocked fake ran between recursive SHA-256 snapshots of one existing and one empty actual temporary Git repository. Both repositories were byte-identical; existing porcelain stayed `?? existing.txt`, empty porcelain stayed empty. |
| Reverse mutations | Eight isolated commit archives reversed H1..H8 independently. Every focused test exited nonzero for the intended observable behavior. The implementation worktree was never modified. |
| Forbidden capability | Case-sensitive `Any` / `type: ignore` and folded subprocess/network/host-config/target-project/real-host command scans were clean. |

## Closure mapping

| Closure | Result | Mutation-sensitive evidence |
| --- | --- | --- |
| `H1` | PASS | Exact six-call lifecycle returned `SUPPORTED`, bound receipt/proof and ended absent. Retaining the registration after unregister failed H1. |
| `H2` | PASS | Codex and Claude stayed `UNVERIFIED` with zero fake effects; copied public-host requests were revalidated. Removing request revalidation failed H2. |
| `H3` | PASS | Canonical key passed; suffix, trailing separator, case, encoded separator, traversal and empty variants failed before effects. Relaxing equality failed H3. |
| `H4` | PASS | None, empty, whitespace, empty-container and omitted shapes were rejected at the declared strict boundaries. Weakening evidence-ID validation failed H4. |
| `H5` | PASS | Direct and full removal bound installation, host, key and receipt; foreign/cross/retry cases did not overwrite effects. Accepting a foreign receipt failed H5. |
| `H6` | PASS | The five frozen port failures produced distinct finite blocked reasons without uncaught exceptions or false support. Collapsing the unavailable reason failed H6. |
| `H7` | PASS after correction | Normal and forged-proof reports are metadata-only. The Gate now reconstructs returned proof metadata before absence verification; malformed nested evidence blocks without leak. Removing only that reconstruction fails the focused H7 regression. |
| `H8` | PASS | The four production files contain no forbidden dynamic/effect capability. Adding a subprocess marker failed H8. |

## CodeReview.md checks

| Check | Result |
| --- | --- |
| Types and layering | PASS after correction. Models and ports are explicit and strict; the lifecycle proof is recursively revalidated at the Gate boundary. |
| Logic / reachability | PASS for all declared normal and five failure routes. Public Codex/Claude paths cannot reach recorded effects. |
| Path-prefix matrix | PASS. Exact, suffix, trailing separator, case, encoded separator, traversal and empty cases map one-to-one to H3. |
| Permission bypass | PASS. Public query, copied public-host request, direct removal and indirect full lifecycle all converge on the recorded/exact-receipt gates. |
| Test truthfulness | PASS after correction. H1..H8 original reverse mutations and the focused forged-proof reverse mutation all fail for the intended observable behavior. Red evidence is recorded in the two docs-only handoffs. |
| Security / privacy | PASS after correction. Normal and forged-proof reports are metadata-only; malformed proof evidence blocks before absence verification or serialization. Actual Git remained untouched. |
| Dependencies / reuse | PASS. Only existing `InstallationId` and project Pydantic are reused; no catalog/historical host module or runtime dependency was added. |

## Initial batched findings - closed by correction

1. `IMPLEMENTATION_DEFECT` - H7, `library/local_orchestration/host_lifecycle.py:96` and `:107`. The gate validates the request but does not reconstruct and validate the `AgentHostRemovalProof` returned by the injected lifecycle before matching and returning it. A port can return a nominal `AgentHostRemovalProof` whose nested `HostEvidenceId` was created through Pydantic non-validating construction; the gate returns `SUPPORTED` and serializes `SECRET-SENTINEL`. Reproduction: subclass `RecordedHostLifecycle`, return `proof.model_copy(update={"evidence_id": HostEvidenceId.model_construct(value="SECRET-SENTINEL")})`, return a valid absent command, then call `verify_recorded`; the sentinel appears in `result.model_dump_json()`. Required correction: fail closed on every invalid returned proof before it can reach a receipt/report, without broad exception swallowing or changing H1..H8.
2. `EVIDENCE_DEFECT` - H7, `tests/test_reversible_agent_host_lifecycle.py:234`. The committed H7 test rejects unknown request fields and serializes normal fakes, but does not inject malformed typed port output. Add one focused regression asserting the forged proof cannot produce `SUPPORTED`, cannot leak the sentinel, and does not create a new unrelated effect. Include its reverse mutation in correction evidence.

## Initial conclusion

`CHANGES_REQUESTED`. The frozen closure remains
`CLOSURE-LOCAL-INSTALL-T03-01`; there is no requirement change or reason for a
new branch/worktree. The same implementation owner must append one correction
commit and one docs-only correction handoff on the existing Ticket-03 branch.
This is the only correction review allowed for this closure revision.

## Correction review

The same Ticket-03 branch appended correction implementation `673ff7c` and
docs-only handoff `633505e`; no branch/worktree, reset, amend, rebase, force,
merge, live host action, target-project write, push, deployment or schedule was
created. The correction changes only `host_lifecycle.py` and the existing test.

| Check | Correction-review evidence |
| --- | --- |
| Focused H7 | Reviewer-owned forged-proof probe returned `BLOCKED / REMOVAL_PROOF_MISMATCH`, serialized no sentinel, performed zero absence checks and preserved the unrelated marker. |
| Green / regression | Ticket-03 module 9/9; full discovery 156/156; strict mypy five files; in-memory compile five files. |
| Scope / ceiling | Production `549 / 550`; test `351 / 450`; exact source/test and docs-only commit boundaries; clean implementation worktree. |
| Actual Git | Supported, unavailable-blocked and forged-proof calls left existing and empty actual Git repositories byte-identical with unchanged porcelain. |
| Reverse mutation | In an isolated archive of `633505e`, deleting only the four-line proof reconstruction made the focused H7 test fail with `SUPPORTED` and serialized `SECRET-SENTINEL`. |
| Source / safety | Forbidden-capability and dynamic-type scans remained clean; Codex and Claude remain `UNVERIFIED`; no production adapter exists. |

Both initial findings are closed. No open `IMPLEMENTATION_DEFECT`,
`EVIDENCE_DEFECT`, `TICKET_DEFECT`, `REQUIREMENT_CHANGED` or blocking
hardening item remains.

## Final conclusion

`APPROVED / READY_TO_MERGE`. Guarded local integration still requires a
merge-tree/conflict check and post-merge verification. This approval does not
authorize push, deployment, schedule activation, live host/Git mutation,
target-project writes or Ticket-04 implementation.
