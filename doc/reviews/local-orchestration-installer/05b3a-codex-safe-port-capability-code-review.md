# Ticket 05B3A Codex Safe Port Capability Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05b3a-codex-safe-port-capability` / `CLOSURE-LOCAL-INSTALL-T05B3A-01` / A1-A5 |
| Reviewed baseline | `3e5ae000aad64eca493ce003f04984dbd818a2e7` |
| Implementation / handoff | `1c3739d305e83c97dd1be723240456cb954ea6cd` / `0275daf172ca3536f7ab6b9fff880bb54478d9af` |
| Branch / owner | `codex/implementation-codex-safe-port-capability-05b3a` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`; complete initial-review batch is CR-137 through CR-139 |

The implementation and docs commits are single-parent descendants of the
reviewed handoff. The implementation adds exactly the two authorized paths;
the handoff changes only `doc/WorkProgressReport.md`. The existing three
worktrees and both tracked and ignored readbacks remain clean.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 5/5 focused and 235/235 full unittest tests. |
| Strict type / compile | PASS: strict full-tree mypy over 112 source files and in-memory compile over the same 112 Python files. |
| Scope / ancestry / residue | PASS: exact `3e5ae00 -> 1c3739d -> 0275daf` ancestry, two-path implementation, WPR-only handoff, `git diff --check`, clean lane and removed external review caches. |
| A1 admitted capability | PASS for ordinary plain-method adapters: admission performs no operation, returns a frozen five-operation capability and exposes only metadata. FAIL for the frozen zero-descriptor condition described under A3. |
| A2 finite shape matrix | PASS for all five names across missing, non-function, property, static/class method, custom descriptor, per-instance callable, builtin, wrong-arity, variadic, keyword-only and defaulted shapes. |
| A3 descriptor and exception boundary | FAIL: a candidate `__class__` property executes at line 164; metaclass `__mro__` and `__dict__` properties execute at lines 221/228. `RuntimeError`, `MemoryError`, `KeyboardInterrupt` and `SystemExit` all escape candidate admission. |
| A4 invalid candidates / unrelated members | PASS for the committed null/text/container and unrelated-member cells. FAIL for a caller metaclass `__eq__`: tuple membership at line 168 invokes it and lets `RuntimeError` escape. |
| A5 operation propagation / metadata | PASS: the four actual-operation exception types propagate only after ordinary admission; accepted/rejected serialization remains metadata-only. |
| Reverse truthfulness | FAIL: the three reported mutations do not expose the candidate-class, metaclass-MRO/dictionary or metaclass-equality paths. Seven independent runtime probes reproduced the escapes against the submitted commit. |

## Closure and CodeReview.md mapping

- **A1/A3 / zero-descriptor admission:** blocking. `object.__getattribute__`
  and `type.__getattribute__` still run matching data descriptors; the ticket's
  prescribed primitives are therefore not a safe implementation boundary.
- **A2 / null-shape and error-code classes:** pass for the finite committed
  table and uniform public `INVALID_PORT` result.
- **A4 / authority-bypass class:** blocking only at the metaclass equality
  path; ordinary malformed/capability candidates are rejected.
- **A5 / exception class:** actual admitted operation propagation passes, but
  the same four exceptions incorrectly escape during admission under A3.
- **Test truthfulness class:** blocking. The committed descriptor cases cover
  operation descriptors and function signature metadata, not the class and
  metaclass surfaces that the production lookup actually touches.
- **Path-prefix and token classes:** not applicable. **Agent-role class:** no
  orchestration surface is introduced. Dependencies and two-file isolation
  otherwise pass.

## Batched findings

**CR-137 — `TICKET_DEFECT`, A1/A3.** ADR-20260811-004 and closure revision 01
prescribe `object.__getattribute__(candidate, "__class__")` and
`type.__getattribute__(class, "__mro__"/"__dict__")` as if those calls bypass
descriptors. Python still resolves a candidate `__class__` data descriptor and
matching metaclass data descriptors through those primitives. Independent
probes made the three properties execute and raise. Refreeze the architecture
around built-in `type(candidate)` plus the raw `type.__dict__` getset
descriptors (or an equivalently proven primitive), and enumerate these exact
adversarial classes before another source correction.

**CR-138 — `IMPLEMENTATION_DEFECT`, A1/A3/A4.** Line 168 tests the untrusted
class with `candidate_class in (str, tuple, list, dict)`. Tuple equality can
fall back to the caller's metaclass `__eq__`; an independent adapter with all
five valid plain methods raised `RuntimeError` before finite admission. Use
identity-only built-in-type exclusion after the refrozen safe class lookup and
prove that caller equality is never invoked.

**CR-139 — `EVIDENCE_DEFECT`, A3/CodeReview.md class 7.** The committed A3
test covers instance `__getattribute__`, operation `__get__`, and function
`__signature__`/`__wrapped__`, but omits candidate `__class__`, metaclass
`__mro__`, metaclass `__dict__`, and metaclass `__eq__`. It also does not inject
all four frozen unexpected/process-control exceptions into the admission
traps. Commit the finite table and reverse mutations so each path turns red
before the correction and stays unread afterward.

## Conclusion

`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`. CR-137 through CR-139 are the
complete blocking batch for closure revision 01; A2 and A5 have no other
blocking finding. No integration or 05B3C dispatch is authorized. The control
plane must correct and refreeze the ticket before the same owner may append one
correction implementation and one WPR-only handoff on the existing branch.

## Revision 02 correction review

| Field | Value |
| --- | --- |
| Ticket / closure | `05b3a-codex-safe-port-capability` / `CLOSURE-LOCAL-INSTALL-T05B3A-02` / R1-R4 |
| Reviewed correction | Implementation `a87af389835f481882dc9e18e69177e8d156278a`; docs-only handoff `0378655864e4277d553558a40d5122702aa3d7d9` |
| Exact ancestry / scope | PASS: `0275daf -> a87af38 -> 0378655`; correction changes only the authorized capability source and focused test, while the handoff changes only `doc/WorkProgressReport.md`. |
| Standard verification | PASS: immutable Unicode-safe export, focused 6/6, full 236/236, strict mypy 112 files, in-memory compile 112 files, reviewed/restored source blob `a6ca8635ca8246fa0f98207f73ef494c568223ae`, diff/scope and clean lane readback. |
| R1-R3 | PASS: class acquisition uses built-in `type(candidate)`; MRO and class dictionaries use the captured raw built-in getset descriptors; exclusions and exact shapes use identity; all 16 candidate/metaclass process-control trap cells remain unread; revision-01 shape, metadata and explicit-operation behavior remains green. |
| R4 reverse truthfulness | PASS: five isolated reviewer mutations independently turned red for candidate `object.__getattribute__`, metaclass `type.__getattribute__`, equality membership, `inspect.signature` and property admission, then were restored to the reviewed blob. |
| Review result | `APPROVED / READY_TO_MERGE`; CR-137 through CR-139 are closed. |

The first reviewer full-suite attempt was discarded because Windows `tar`
omitted Unicode paths from extraction; a Python `tarfile` extraction proved
those paths present and produced the authoritative results above. A later
reviewer timeout left two exact disposable stage roots; they were removed
before the clean authoritative rerun. Neither event changed an implementation
worktree or target project.

No blocking finding remains for revision 02. Guarded integration may include
this branch independently; 05B3C remains dependency-waiting on 05B3B.
