# Ticket 05B4B2E3D Codex Oracle Response Admission Code Review

## Review decision

`APPROVED / READY_TO_MERGE`

Closure revision 02 refroze the unobservable constructor-provenance requirement,
and the additive revision-03 correction closes the fail-open optional-source
projection. Independent terminal verification of exact handoff
`5fa24b5acceacf98cf101a0126e03388fa70e659` passes. Guarded integration of the
complete immutable history is authorized.

## Revision-02 blocking findings (closed by revision-03)

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

## Revision-03 terminal review

### Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e3d-codex-oracle-response-admission`; `CLOSURE-LOCAL-INSTALL-T05B4B2E3D-02`; P1-P8 |
| Binding | Task `019ffb0c-db88-7303-895c-aecfadde7c8d`; handoff `hnd_local_orchestration_install_05b4b2e3d_cr170_171_r03_20260814`; receipt `rcpt_local_orchestration_install_05b4b2e3d_r03_20260814`; correlation `corr-local-orchestration-install-05b4b2e3d-cr170-171-r03-20260814` |
| Chain | Control refreeze `f12018e979788a571e3d6d746857ddc42cd57810` -> history merge `8de02cb42fe3d78ebeef8b9a4c3a9de93a9052ab` -> correction `0018b0d089f6a79704a60ae7b8861a6c658a1e53` -> WPR `febd0df19f95b4b393ddc782af9404378f29e3e7` -> factual docs correction `5fa24b5acceacf98cf101a0126e03388fa70e659` |
| Scope | Correction changes exactly the frozen source and focused-test paths; the two following commits change only `doc/WorkProgressReport.md`. Ancestry, diff and clean permanent-owner readback pass. |

### Independent verification

| Gate | Reviewer result |
| --- | --- |
| Immutable export | PASS. Exact handoff ZIP-exported below reviewer-owned TEMP; archive SHA-256 `0EB4AB41A67BD3C97A8D4B0619E2F6FEAA242DFAE727B5C8457FCF5FEEEDB1A6`. |
| Tests | PASS. Focused `13/13`; full explicit serial discovery `432/432`. |
| Static validation | PASS. Strict mypy with explicit package bases `138/138`; in-memory compile `138/138`; exact-path source sentinel found no `Any`, `type: ignore`, dynamic lookup, effect API or renderer/JavaScript sink. |
| Adversarial matrix | PASS. Plugin-list and marketplace-list reject ten present-invalid source cells; two legitimate omissions accept; two fully populated constructed sources accept only as newly rebuilt instances. |
| Test truth | PASS. Reviewer monkeypatched present-invalid admission to absence; committed `test_p8_reverse_present_invalid_source_cannot_be_absent` turned red, then runtime binding restored. |
| XSS / capability | `XSS_NOT_APPLICABLE`. No Browser, WebView, HTML/DOM renderer, JavaScript context, Native Bridge, IPC or Extension API changes. |

### Finding closure and mandatory checks

- **CR-170 / ticket correctness:** CLOSED. Revision 02 specifies only observable
  exact-state admission; state-equivalent constructed data is recursively
  revalidated and rebuilt, while malformed, missing, extra, subclass,
  injected/private and invalid primitive state rejects.
- **CR-171 / logic and edge cases:** CLOSED. A closed typed tri-state separates
  absence, rebuilt-valid and present-invalid sources; parent entries omit only
  actual absence and reject present-invalid values.
- **Strong types and conventions:** PASS. Closed dataclass union, explicit
  Pydantic models, exact primitives and finite results; no untyped effect port.
- **Tests and mutation truth:** PASS for named P5/P6 matrices and P8 reversal.
- **Dependencies, traceability and evidence:** PASS. Project-owned runtime,
  immutable chain, exact hashes and no historical-source reuse.
- **Role, task/worktree binding and adaptive profile:** PASS. The named owner
  used the single permanent owner2 worktree, no helper/fan-out and no
  orchestration authority.
- **State, error, exception, path, token and authority classes:** PASS or not
  applicable. Invalid shapes are finite metadata-only rejections; no caller
  protocol, filesystem/path, token, Secret, external provider or effect exists.

## Terminal decision

`APPROVED / READY_TO_MERGE`. Integrate the complete exact handoff history by a
normal guarded merge. Preserve every unique WPR record exactly once if the
predicted append conflict occurs, then rerun focused/full/static checks. No
push, package/build/install, live Codex/host/target-project mutation, staging
publication, Secret, release or deployment is authorized.
