# Ticket 05B4B2B1 Codex Registration Terminal Claim Authority Code Review

## Review decision

`CHANGES_REQUESTED`

The immutable return satisfies C1-C3 and C6-C8, but CR-155 shows that C4/C5
claim binding is not immutable. The live claim and its private registry record
share the same Pydantic metadata instance. Mutating that instance in place with
`object.__setattr__` changes phase/generation while preserving the identity
check used during consumption, so the altered claim is consumed successfully.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2b1-codex-registration-terminal-claim-authority`; `CLOSURE-LOCAL-INSTALL-T05B4B2B1-01`; C1-C8 |
| Owner / branch | Task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; `codex/implementation-codex-registration-terminal-claim-05b4b2b1` |
| Dispatch baseline | `588e605967c40e70a2e8fbc380734968011ad075` |
| Implementation | `a57dd0a1c8a8cc173ef96a63632e53326a5a9808`; exactly the new settlement-authority module and focused test |
| Docs-only handoff | `ad2fc5003d04289b9971e8bfe8f9c0d066e19f4b`; only `doc/WorkProgressReport.md`, PRG-20260812-242 |
| Binding | `hnd_local_orchestration_install_05b4b2b1_20260812`; `aln_local_orchestration_install_05b4b2b1_20260812`; `rcpt_local_orchestration_install_05b4b2b1_20260812`; `corr-local-orchestration-install-05b4b2b1-20260812` |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| Ancestry / scope / residue | PASS: `588e605 -> a57dd0a -> ad2fc50`; implementation adds exactly the two authorized paths, handoff changes WPR only, submitted lane is clean, and three-worktree topology is unchanged. |
| C1 first red | PASS: WPR records the exact absent-module `ModuleNotFoundError` before production creation. |
| C2 admission / provenance | PASS: exact integrated B2B provenance admits without effect; invalid, trap and unregistered-clone values block, and ordinary module attributes expose no registration surface. |
| C3 forward classification | PASS: ready/next-ready/blocked data remain exact; terminal proof/compensation and started-add recovery become only their matching claim kind; delegated order and exceptions remain unchanged. |
| C4 immutable exact binding | **FAIL — CR-155 / IMPLEMENTATION_DEFECT:** `ClaimRecord.metadata` and live claim `_metadata` are the same object. The independent probe changes `phase` from `PLUGIN_ADD` to `FRESH_PREFLIGHT` and generation from `3` to `999` in place; consumption still returns `CodexRegistrationProofRequired`, because `claim_metadata_value is record.metadata` remains true. Exact attempt/phase/generation binding is therefore not enforced. |
| C5 one-shot exact consumption | PASS for kind, clone, replacement-metadata, foreign and replay cells, but FAIL through CR-155 because an altered live claim remains admissible. Tombstoning itself is atomic. |
| C6 synchronization / lifecycle | PASS: duplicate consumption yields one decision and one block; weak owner loss invalidates unconsumed state without an unbounded strong registry. |
| C7 type / effect / XSS boundary | PASS: no `Any`, `type: ignore`, broad catch, optional port, dynamic lookup/signature or settlement/host/target effect. `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge exists. |
| C8 evidence truthfulness | PASS for submitted provenance, classification, tombstone, kind and closure reversals. Those reversals do not exercise in-place mutation of the shared binding object; CR-155 requires one bounded named regression and binding-comparison reversal inside existing C4/C5. |
| Independent standard verification | PASS in the repository-external immutable snapshot: focused 12/12, full serial 329/329, strict mypy 126 source files and in-memory compile. |
| CodeReview section 2.1 class 1 | PASS / no filesystem path router is added; attempt identity is exact rather than prefix-authorized. |
| CodeReview section 2.1 class 3 | FAIL only through CR-155: the consumption gate admits the same live authority after its binding fields have changed. No effect is invoked by this ticket. |
| CodeReview section 2.1 class 7 | FAIL only through CR-155: replacement metadata is tested, but same-object in-place mutation follows a different observable path and currently succeeds. |
| CodeReview section 2.1 class 8 | `XSS_NOT_APPLICABLE` for the reviewed source and test paths. |

## CR-155 bounded correction

CR-155 is an `IMPLEMENTATION_DEFECT` under frozen C4/C5, not a requirement or
ticket change. In the same branch and allocation, add a named first-red test
that mutates the exact live claim metadata in place through
`object.__setattr__`, using valid alternate attempt/phase/generation values.
Every altered cell must return finite `INVALID_CLAIM`; an unchanged claim must
still consume once.

Keep an authority-owned canonical binding that is not the same mutable object
exposed by the claim. Before tombstoning, validate exact closed field types and
compare the live claim's attempt/phase/generation/kind to that canonical
binding without caller equality, hashing, representation or serialization.
The registry must remain lexical, synchronized, identity-only and weakly
bounded. Add an isolated comparison-gate reversal that makes the named CR-155
test red and restore exact blobs.

The correction is additive and may change only the existing settlement module
and focused test, followed by one WPR-only handoff. Preserve all C1-C8 tests and
five submitted reversals. No new branch/worktree, public export, settlement
effect, B2C/B2D work, integration, push, release or deployment is authorized.

## Disposition

`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION_REQUIRED`. This is the one bounded
correction allowed for closure revision `CLOSURE-LOCAL-INSTALL-T05B4B2B1-01`.
The same ticket, implementation owner, worktree, branch, allocation, receipt
and correlation remain valid.
