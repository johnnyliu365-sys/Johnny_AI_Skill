# Ticket 05B3B Codex Compensation Reducer Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05b3b-codex-compensation-reducer` / `CLOSURE-LOCAL-INSTALL-T05B3B-01` / B1-B5 |
| Reviewed baseline | `3e5ae000aad64eca493ce003f04984dbd818a2e7` |
| Implementation / handoff | `e7bdee5b1bcd21d5cbc589f7abed4da156d0fdc8` / `aab7bf5df0c4501ba30e364fa4c76936412c4282` |
| Branch / owner | `codex/implementation-codex-compensation-reducer-05b3b` / task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d` |
| Review result | `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`; complete initial-review batch is CR-140 through CR-143 |

The implementation and docs commits are single-parent descendants of the
reviewed handoff. The implementation adds exactly the two authorized paths;
the handoff changes only `doc/WorkProgressReport.md`. The existing three
worktrees and both tracked and ignored readbacks remain clean.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 7/7 focused and 237/237 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy over 112 source files and in-memory compile over the same 112 Python files. |
| Scope / ancestry / residue | PASS: exact `3e5ae00 -> e7bdee5 -> aab7bf5` ancestry, two-path implementation, WPR-only handoff, `git diff --check`, clean lane and removed external review caches. |
| B1 journal admission | PASS: the six integrated-05B2 reachable pairs produce exact plans; the seventh legal-but-unreachable pair, nine illegal pairs, cross-request, replay and malformed journal inputs block finitely. |
| B2 plan order | PASS for plugin-before-marketplace removal. BLOCKED at the proof boundary because revision 01 says only “fixed order” and does not freeze the exact three-step sequence; the implementation selected plugin lists, installed location, marketplace. |
| B3 exact plan/outcomes | PASS for committed missing/extra/reordered/wrong-step and constructed observation cells. FAIL: line 339 uses tuple equality on `type(plan)`, so a wrong-plan metaclass `__eq__` can raise all four probed exception types instead of returning `PLAN_INVALID`. |
| B4 residual authority | PASS for absence truth conjunctions and effect-level clearing. BLOCKED: `remaining_authority` collapses `MAY_EXIST` and `OWNED`, and the result carries no request/attempt identity; two distinct current-authority states serialize identically. |
| B5 finite metadata | PASS for finite status/reason shape and absence of raw command/path/output data, subject to the missing exact current-attempt binding in B4. |
| Reverse truthfulness | FAIL: the handoff reports only three mutations although the ticket requires five independent reversals: pre-existing authority, removal order, finite-failure completeness, early authority clearing and stale-authority retention. |

## Closure and CodeReview.md mapping

- **B1 / null-shape and error-code classes:** pass for the frozen journal
  admission matrix and finite reasons.
- **B2 / authority-bypass class:** removal authority passes, but the proof order
  is not an executable frozen contract and therefore cannot be approved for
  later composition.
- **B3 / malformed boundary:** blocking. A wrong plan can execute caller
  metaclass equality and escape instead of producing the required finite block.
- **B4/B5 / authority and traceability:** blocking at ticket design. Effect-only
  authority loses both the original `MAY_EXIST`/`OWNED` state and exact
  request/attempt binding that the unchanged compensation behavior preserved.
- **Test truthfulness class:** blocking. Two required independent reverse
  protections are absent, and no committed wrong-plan metaclass probe exists.
- **Path-prefix and token classes:** not applicable; this pure ticket accepts no
  path or credential. **Agent-role class:** no orchestration surface exists.
  Dependency and no-effect isolation otherwise pass.

## Batched findings

**CR-140 — `TICKET_DEFECT`, B2.** Closure revision 01 requires the three proof
steps to follow a fixed order but never names that order. The prior unchanged
05B3 D3 contract lists fresh plugin lists, fresh marketplace list, then exact
installed-path absence; the implementation instead places installed-location
proof before marketplace proof. Refreeze one exact ordered tuple before 05B3C
can safely compose the two modules.

**CR-141 — `TICKET_DEFECT`, B4/B5.** Revision 01 says the result retains
unresolved “current-attempt authority” but does not freeze its typed identity.
The implementation returns only effect names. Independent MAY_EXIST and OWNED
marketplace-residue plans produce byte-equivalent results, and neither result
binds request or attempt ID. This silently weakens the unchanged prior D4/D5
contract, which retained the exact residual journal. Refreeze a recursively
validated residual current-attempt journal (or an equivalent exact typed
identity/state record) and its serialization matrix.

**CR-142 — `IMPLEMENTATION_DEFECT`, B3.** `_plan_fields_are_exact()` line 339
uses `type(plan) in (...)`. Equality can fall back to an untrusted wrong-plan
metaclass. Independent probes made `RuntimeError`, `MemoryError`,
`KeyboardInterrupt` and `SystemExit` escape before `PLAN_INVALID`. Replace the
membership comparison with identity-only exact-type checks and commit the four
finite wrong-plan cells.

**CR-143 — `EVIDENCE_DEFECT`, B2/B4/CodeReview.md class 7.** The ticket freezes
five independent reverse mutations, while PRG-171 records only removal order,
plugin-list conjunction and outcome-count completeness. Commit separate
pre-existing-authority, early-clear and stale-authority reversals so all five
named protections are independently red, along with the CR-142 wrong-plan
probe, before the final green verification.

## Conclusion

`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-140 through CR-143 are the
complete blocking batch for closure revision 01; B1 and the pure no-effect
boundary have no other blocking finding. No integration or 05B3C dispatch is
authorized. The control plane must correct and refreeze the ticket before the
same owner may append one correction implementation and one WPR-only handoff
on the existing branch.

## Revision 02 correction review

| Field | Value |
| --- | --- |
| Ticket / closure | `05b3b-codex-compensation-reducer` / `CLOSURE-LOCAL-INSTALL-T05B3B-02` / R1-R5 |
| Reviewed correction | Implementation `3f22551b8f581d087ef0cdbad6a70fbd671202e2`; docs-only handoff `4d5bbefe42e1d1ae3206b29e877f0556bda3ce4c` |
| Exact ancestry / scope | PASS: `aab7bf5 -> 3f22551 -> 4d5bbef`; correction changes only the authorized reducer source and focused test, while the handoff changes only `doc/WorkProgressReport.md`. |
| Standard verification | PASS: immutable Unicode-safe export, focused 15/15, full 245/245, strict mypy 112 files, in-memory compile 112 files, reviewed/restored source blob `70685c0a722f9acda5256b92c51c202fb6d222be`, diff/scope and clean lane readback. |
| R1 / R2 | PASS for the exact proof order, all reachable authority pairs, request/attempt-bound residual journal, MAY_EXIST-versus-OWNED serialization, cross-request/attempt, substituted-state and stale-plan cells. |
| R3 / R5 | **FAIL:** an exact `CodexCompensationPlan` whose exact `CodexCompensationPlanIdentity` was created with `model_construct()` and one malformed nested field escapes as `PydanticSerializationError` instead of returning finite `PLAN_INVALID`. The reviewer reproduced this independently for all four identity fields: request, attempt ID, marketplace state and plugin state. |
| R4 reverse truthfulness | PASS: six isolated reviewer mutations independently turned red for proof order, pre-existing authority, complete-after-declared-failure reduction, early authority clearing, stale-authority retention and wrong-plan equality, then were restored to the reviewed blob. |
| Review result | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`; CR-144 and CR-145 are the complete revision-02 blocking batch. |

### Revision 02 findings

**CR-144 — `IMPLEMENTATION_DEFECT`, R3/R5.**
`_revalidate_plan()` guards exact-field admission and plan rebuilding, but calls
`_plan_matches_rebuild()` after its exception boundary. That helper serializes
the supplied nested identity. A constructed exact identity can therefore make
Pydantic raise `PydanticSerializationError`, violating the frozen rule that
constructed malformed models fail finitely. Recursive exact validation must
occur before comparison, and serialization/validation failure must map to
`PLAN_INVALID` without catching process-control exceptions.

**CR-145 — `EVIDENCE_DEFECT`, R3/R5 and CodeReview.md class 7.** The committed
malformed matrix covers normalized outcomes and a wrong top-level plan type,
but no recursively malformed exact plan identity. Add the four constructed
identity cells and prove each produces metadata-only `PLAN_INVALID` without an
exception escape.

This is the correction review for the same ticket sequence. Per Workflow.md
§8.1, no automatic third implementation correction is permitted. 05B3B is not
approved or integrable; return to control-plane convergence review and keep
05B3C dependency-waiting. No live Codex mutation, target-project write, push,
release or deployment is authorized.
