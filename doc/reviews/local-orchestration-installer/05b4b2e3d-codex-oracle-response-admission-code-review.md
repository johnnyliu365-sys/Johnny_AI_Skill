# Ticket 05B4B2E3D Codex Oracle Response Admission Code Review

## Review decision

`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`

The submitted two-commit return is structurally clean and every committed test
passes, but independent adversarial probes expose one impossible ticket
requirement and one fail-open nested-value projection. No integration or
implementation correction is authorized before the ticket is refrozen.

## Blocking findings

### CR-170 — `TICKET_DEFECT`: constructor provenance is not observable from a state-equivalent Pydantic value

P2 and the frozen design require every `model_construct` value to reject even
when its type and complete state are otherwise identical to a normally
validated value. Reviewer created one validated `CodexProtocolAccepted` and one
fully populated `model_construct` instance. Their exact `__dict__`,
`__pydantic_fields_set__`, `__pydantic_extra__`, `__pydantic_private__` and
serialized reduction state were identical. The submitted admission therefore
accepted and safely rebuilt the constructed envelope.

The implementation cannot infer missing provenance from identical observable
state without adding an explicit authority/provenance carrier. Refreeze P2/P5/P6
to require exact-type, exact-state, validator-safe rebuilding: malformed,
extra, subclass, injected or validator-bypassing invalid state must reject;
state-equivalent input may be revalidated and rebuilt. If constructor provenance
itself must be enforced, that is a separate architecture/authority ticket.

### CR-171 — `IMPLEMENTATION_DEFECT`: malformed optional marketplace source is silently converted to absence

`_rebuild_marketplace_source` returns `None` for both a legitimately absent
optional source and a present malformed source. Both parent rebuilders then
interpret `None` as absence and construct a successful entry without
`marketplaceSource` (source lines 223-300). Reviewer supplied a fully populated
plugin entry whose present source was constructed without required `value`.
Admission returned `CodexProtocolAccepted` and the rebuilt entry had a null
source instead of returning `MALFORMED_RESPONSE`. The marketplace-entry path has
the same control flow.

After CR-170 refreeze, the correction must distinguish absent optional data from
present-invalid data and reject the latter. Add named plugin-list and
marketplace-list cells for missing-field, invalid primitive, subclass and
injected optional sources; each must remain finite and execute no caller
protocol.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e3d-codex-oracle-response-admission`; `CLOSURE-LOCAL-INSTALL-T05B4B2E3D-01`; P1-P8 |
| Owner binding | Project `3a624854-bf2f-4aa8-9b04-5f73e9ab2a28`; task `019ffb0c-db88-7303-895c-aecfadde7c8d`; revision-02 receipt `rcpt_local_orchestration_install_05b4b2e3d_r02_20260814` |
| Chain | Registry `334757cd80d5a4d30db8b375d230115662099b3b` -> implementation `c588bf6d24fcb459919130e5bebaeb961de72ca4` -> WPR-only handoff `77be19295f9cd22d085f98b33e522b9152057318` |
| Scope | Implementation adds exactly the two frozen paths; handoff changes only `doc/WorkProgressReport.md`; ancestry and `git diff --check` pass. |

## Independent verification

| Gate | Reviewer result |
| --- | --- |
| Immutable export | PASS. Exact handoff was ZIP-exported beneath reviewer-owned system TEMP; both Unicode library trees were present. |
| Submitted tests | PASS. Focused `10/10`; full explicit serial discovery `424/424`. |
| Static checks | PASS. Strict mypy with explicit package bases checked `136/136`; in-memory compile checked `136/136`; external reviewer cache was removed. |
| Exact scope / residue | PASS. Exact implementation/handoff paths, parent links, branch HEAD, clean permanent worktree and unchanged three-worktree topology pass. |
| P2 constructed provenance probe | FAIL / CR-170. A fully populated constructed envelope is observationally identical to the validated envelope and is accepted. |
| P5/P6 malformed optional-source probe | FAIL / CR-171. Present-invalid nested source is dropped and the containing response is accepted. |
| XSS / privileged capability | `XSS_NOT_APPLICABLE`. No Browser, WebView, HTML/DOM renderer, JavaScript context, bridge, IPC or extension capability changed. |

## CodeReview.md mandatory checks

- **Strong types / conventions:** PASS for the published API and finite result
  algebra; no `Any`, `type: ignore`, `None` effect port or dynamic lookup.
- **Logic / edge cases / security:** FAIL for CR-171's fail-open optional-state
  collapse.
- **Test truth / mutation:** FAIL for CR-170/171 coverage despite the three
  submitted P8 mutations passing.
- **Dependencies / traceability:** PASS. The lane uses the integrated
  project-owned runtime and no historical source copy.
- **Agent role / task binding:** PASS. The implementation owner used only the
  exact permanent worktree and did not orchestrate another Agent.
- **Adaptive profile:** PASS. One owner and no helper remain proportionate.

## Required continuation

Control must refreeze the observable admission rule described by CR-170 before
one additive same-branch correction can address CR-171 and its missing tests.
The immutable implementation/handoff remain evidence. No new branch/worktree,
reset, rewrite, integration, push, package/build/install, live Codex,
target-project write, release or deployment is authorized by this review.
