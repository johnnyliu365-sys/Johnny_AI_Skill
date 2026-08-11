# Ticket 05B1 Codex Registration Contracts and Journal Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05b1-codex-registration-contracts-and-journal` / `CLOSURE-LOCAL-INSTALL-T05B1-01` plus `CLOSURE-LOCAL-INSTALL-T05B1-02` |
| Reviewed baseline | `16d48ac70cf560f073adb58991d4f0800f28ac9e` |
| Implementation / handoff | Initial `fbedefcef113ff1a85e5709ea80c205c54ff85eb` / `6969d4412d0391684739890e4fc3e5451d4ed6c0`; correction `dc57ff9314b8ee1cc7e158af9b4b2a65723422ee` / `1df30ae6ed9a87b4b9fe35b64ea09ccc107cccee` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | Initial `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`; final correction review `APPROVED / READY_TO_MERGE` |

The implementation changes only the three authorized source/test paths and
the handoff changes only `doc/WorkProgressReport.md`. The implementation
worktree is clean. Independent execution used a fresh immutable export and did
not write either implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 4/4 focused and 209/209 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy and in-memory compile over 104 Python files. |
| Scope / ancestry / residue | PASS: exact three-path implementation, one-file handoff, additive ancestry, diff/source checks and clean tracked/ignored readback. Review export and external cache were removed and read back absent. |
| C1 observed DTOs | PASS for committed null/blank/container/path validation. Independent equal/prefix/trailing-slash/case/encoding/traversal/empty probes all behaved fail-closed, but not all seven are committed TDD cells. |
| C2/C3 exact proof | FAIL: `CodexRegistrationProofRequest` has only observed `auth_policy`; it has no independent expected policy. A request-only exact proof for an observation changed to `foreign-policy` returned `CodexRegistrationReceipt` carrying that policy. |
| C3 exception boundary | UNFROZEN/FAIL: an injected proof-port `RuntimeError` propagates. The closure says CodeReview.md class 6 applies but never declares whether this dependency failure must throw or return a finite rejection. |
| C4 journal | FAIL: `(PREEXISTING, MAY_EXIST)`, `(PREEXISTING, OWNED)` and `(MAY_EXIST, OWNED)` are accepted and grant plugin authority even though plugin cannot be attempted after a pre-existing or unresolved marketplace. |

## Closure and mandatory-check mapping

- **C1 / T1 / path-prefix class:** behavior passes independently, evidence
  fails because the committed table omits the complete seven named cells.
- **C2-C3 / T2 / strong types and authority:** blocked. The expected auth
  policy has no separate typed authority source, so proof equality only proves
  that two copies of the same untrusted observation agree.
- **C3 / T4 / exception class:** ticket defect. The required throw/no-throw
  behavior for the external proof port is not specified or tested.
- **C4 / T3 / current-attempt authority:** implementation fails impossible
  ordering. `PREEXISTING` and `MAY_EXIST` marketplace states must terminate the
  plugin side at `NOT_ATTEMPTED`; the current model checks only marketplace
  `NOT_ATTEMPTED`.
- **Null/container class:** committed DTO coverage passes, but required
  `None`/wrong proof-port cells are absent.
- **Authority bypass:** fail due foreign observed auth policy producing a
  receipt and impossible journals granting plugin removal authority.
- **Test truthfulness:** fail. `RequestOnlyProofPort("auth-policy")` mutates the
  proof rather than testing a foreign observed-auth request, and T3 calls
  impossible journal states legal.
- **Security / isolation:** no live Codex, filesystem, target-project, network
  or Secret effect occurred; receipt serialization omits absolute paths.
- **Dependencies / scope:** pass. No new dependency or rejected-source reuse.

## Batched findings

**CR-128 — `TICKET_DEFECT`, C2/C3/T2.** The closure requires observed
`authPolicy` to map to the exact request-owned policy, but C2 never defines an
expected-policy field or other authority source. Lines 112-136 of
`codex_registration_contracts.py` can bind root/path to locators but can only
copy the observation's policy. Refreeze a distinct typed expected policy and
require observation/proof/receipt equality to it before the proof port runs.

**CR-129 — `EVIDENCE_DEFECT`, C3/T2/class 7.** Lines 117-130 and 258-264 of
`test_codex_registration_contracts.py` do not implement the described
request-only foreign-auth probe. The fake receives a trusted request and then
returns a deliberately different proof, so `PROOF_MISMATCH` is guaranteed.
The missing cell changes the observed request policy while keeping the
expected policy fixed; the submitted implementation returns a receipt.

**CR-130 — `TICKET_DEFECT`, C3/T4/CodeReview.md class 6.** The ticket declares
the exception class applicable but never chooses the observable result for a
proof-port failure. Lines 201-216 catch some shape exceptions while an injected
`RuntimeError` escapes. Refreeze a typed proof-port failure and explicitly
state finite mapping versus propagation for typed, unexpected and
process-control exceptions.

**CR-131 — `IMPLEMENTATION_DEFECT`, C4/T3.** Lines 283-290 reject a plugin
state only when marketplace is `NOT_ATTEMPTED`. Lines 292-305 of the test then
mark downstream plugin states legal for `MAY_EXIST` and `PREEXISTING`
marketplaces. A marketplace still unresolved or already pre-existing cannot
authorize a later plugin attempt; those states must fail recursive validation.

**CR-132 — `EVIDENCE_DEFECT`, C1/C2/T1/T2/classes 1 and 2.** The committed
path table does not contain the complete equal/prefix-plus-character/trailing-
slash/case/encoding/traversal/empty matrix, and no test supplies `None` or a
wrong-shape proof port. Independent probes show the current path behavior is
fail-closed, but CodeReview.md requires these TDD cases to be committed.

## Conclusion

`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-128 through CR-132 are the
complete blocking batch for closure revision 01. Ticket defects return to the
control plane before any correction. The same ticket, task, worktree, branch,
allocation and valid receipt remain bound; no replacement branch/worktree,
integration, downstream dispatch, live Codex mutation, target-project write,
push, release or deployment is authorized by this review.

## Final correction review — closure revision 02

### Independent verification

| Check | Result / evidence |
| --- | --- |
| Ancestry / scope / residue | PASS: `dc57ff9` is additive on submitted `6969d44` and changes only the three authorized source/test paths; `1df30ae` changes only `doc/WorkProgressReport.md`. The branch and tracked/ignored readbacks are clean. |
| Focused / full | PASS: fresh immutable export ran focused 7/7 and full 212/212 unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy reported no issues in 104 files; three authorized Python paths compiled in memory. External mypy cache and review residue read back absent. |
| R1 / CR-128 / CR-129 | PASS: a trusted expected policy plus foreign observed policy returns `INVALID_INPUT`, no receipt and zero proof-port calls. Proof and metadata-only receipt bind the expected policy. |
| R2 / CR-130 | PASS: only `CodexRegistrationProofPortFailure` maps to `PROOF_PORT_FAILED`; malformed shape maps to `INVALID_PROOF`; `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` propagate. |
| R3 / CR-131 | PASS: an independent 16-cell enumeration accepts exactly the frozen seven state pairs, rejects nine, and grants plugin-before-marketplace removal authority only for `MAY_EXIST`/`OWNED`. |
| R4 / CR-132 | PASS: the committed table contains equal plus six invalid path cells for both observed fields, `None`/wrong port cells, foreign auth, exception cells and all 16 journal pairs. |
| Reverse mutations | PASS: disabling expected-policy equality changes the target result to `PROOF_MISMATCH`; replacing the typed catch makes the declared failure escape; disabling the journal guard accepts forbidden states. Each targeted committed test turns red. |
| No-effect boundary | PASS: the ticket remains pure contracts/tests. No Codex command, filesystem, target-project, network, Secret, orchestration, packaging, push, release or deployment effect exists. |

### Mandatory CodeReview.md mapping

- **Path-prefix class (CR):** all seven named cells map to
  `test_r4_every_path_boundary_cell_rejects_before_proof_port` for both
  marketplace root and plugin path; the exact cell succeeds and every other
  cell rejects before the proof port.
- **Authority bypass (CR):** expected policy is distinct from observation;
  foreign observation cannot reach the port. Impossible journal states cannot
  create removal authority. Receipt serialization contains no observed
  absolute path.
- **Test truthfulness (CR):** direct independent probes reproduce R1-R3, and
  three source-level in-memory mutations independently make their target tests
  fail. First-red evidence is consistent with the submitted correction.
- **Null/container, error-code and exception TDD:** committed strict DTO,
  `None`/wrong port, finite typed failure and explicit propagation cells pass.
- **Agent role, dependencies and scope:** no orchestration API or new dependency
  is introduced; source and handoff scopes are exact.

### Final decision

`APPROVED / READY_TO_MERGE`. CR-128 through CR-132 are closed. No blocking
finding remains in closure revision 02, and no new probe expands the frozen
closure. Guarded integration may proceed; downstream Ticket 05B2 remains
blocked until that integration is recorded.
