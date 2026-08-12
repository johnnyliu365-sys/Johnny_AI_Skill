# Ticket 05B4B2E0 Codex Oracle Logical Installed Path Code Review

## Review decision

`CHANGES_REQUESTED / SAME_CLOSURE_CORRECTION`

The immutable return closes the required-field, persistence, response,
payload/digest and physical-locator portions of O1-O8. Two bounded defects
remain in the same frozen logical-path responsibility. No requirement change,
new branch or new worktree is required.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e0-codex-oracle-logical-installed-path`; `CLOSURE-LOCAL-INSTALL-T05B4B2E0-01`; O1-O8 |
| Owner / branch | Task `019fcc9c-f34f-7d53-a313-c70c90bf3245`; existing `workflow-implementation`; `codex/implementation-codex-oracle-logical-path-05b4b2e0` |
| Dispatch / chain | `060109b79f94c02214d1f1e7127f7175a0bfd207 -> f79696241a828e1d523370d6b03ff0c6ed45355c -> 05b65bce17be0dbab7aeefc8118ad8d37e3d5bce` |
| Scope | Implementation changes exactly the four authorized oracle staging/test paths; handoff changes only `doc/WorkProgressReport.md`. The submitted worktree is clean and the existing three-worktree topology is unchanged. |

## Closure and CodeReview.md verification

| Gate | Result |
| --- | --- |
| O1 first red | PASS: the committed evidence records the missing required identity field as Pydantic `extra_forbidden`, with staging production unchanged during first red. |
| O2 round trip | PASS: the exact logical path travels through identity, command JSON, persisted state, exact payload/digest and `CodexPluginAdd.installedPath`. |
| O3 physical separation | PASS: the physical locator remains exactly `plugins/<plugin-id>.json`; payload creation, validation and removal use only that relative locator below the disposable payload root. |
| O4 malformed paths | **FAIL — CR-158:** the validators accept a segment ending in a space, for example `C:\owned \plugin`. Win32 normalizes trailing spaces and periods in ordinary path segments, so this is not the frozen unambiguous normalized Windows path. The same gap exists independently in the Pydantic parent contract and fresh child validator. |
| O5 persisted truth | PASS: missing/extra/malformed state and state-only or payload-only logical-path tamper fail closed through exact schema, bytes and digest checks. |
| O6 exact owned identity | **FAIL — CR-157:** `_exact_plugin()` omits `installed_path` from the expected identity. After adding at the frozen logical path, an otherwise identical `PLUGIN_REMOVE` command carrying a different valid logical path returns `OracleCompleted` and deletes the owned payload. The new identity field therefore does not authorize the exact object being removed. |
| O7 type/effect boundary | PASS: no `Any`, `type: ignore`, broad catch, optional authority, dynamic lookup, historical-source reuse or live Codex/host/network/target-project/package effect is introduced. `XSS_NOT_APPLICABLE`. |
| O8 standard evidence | PASS for the four submitted reversals. Independent Unicode-safe snapshot verification passed focused 14/14, full 357/357, strict mypy 130 files and in-memory compile 130 files. Those reversals do not cover CR-157 or CR-158. |
| CodeReview §2.1 | Class 1 FAIL only through CR-158 path ambiguity; class 3 FAIL only through CR-157 exact identity authorization; class 7 requires committed regressions and isolated reversals for both gaps. Class 8 is `XSS_NOT_APPLICABLE`. |

## CR-157 / CR-158 bounded correction

Both findings are `IMPLEMENTATION_DEFECT` under the existing O2/O4/O6/O8
closure. Keep the same ticket, implementation owner, worktree, branch,
allocation, receipt and correlation. Previous implementation and handoff
commits remain immutable evidence.

- Add a committed regression proving that a `PLUGIN_REMOVE` command with a
  different valid logical installed path returns the finite existing block,
  leaves state and payload bytes unchanged, and does not remove the owned
  plugin. Bind `_exact_plugin()` to the exact `installed_path` as well as the
  already-checked plugin fields.
- Add committed parent-contract and fresh-child command-boundary cells for
  path segments ending in a space or period. Both must fail before mutation;
  state and payload bytes remain unchanged. Apply the same finite rule to
  persisted records.
- Independently reverse the exact-installed-path identity comparison and the
  segment-ending normalization guard; each named committed regression must
  turn red, followed by exact blob restoration.

Only the original four implementation paths and a later WPR-only handoff may
change. No E1-E6 work, branch/worktree creation, new dependency, live Codex,
host/network/target-project effect, staging push, package, release or
deployment is authorized.

## Disposition

`CHANGES_REQUESTED`. CR-157 and CR-158 are the complete blocking batch for
revision 02. A same-branch additive correction may be dispatched only after
the control review and correction handoff are committed.

## Final correction review

| Gate | Result |
| --- | --- |
| Immutable correction | PASS: `05b65bce17be0dbab7aeefc8118ad8d37e3d5bce -> 1d465775b71530193cb584fcdc2aed90c873e4f8 -> 002b2982cbf111262865946dc16d83c23a7bc879`; correction changes only contracts, fresh child and focused test; handoff changes only WPR PRG-270. |
| CR-157 | PASS: exact plugin matching now includes `installed_path`. A valid alternate path returns `COMMAND_INVALID`, preserves exact state/payload bytes and leaves the plugin present. Reviewer reproduced the original exploit and the corrected behavior. |
| CR-158 | PASS: both validators reject every segment ending in ASCII space or period. Parent construction, tampered fresh-child command and persisted-record cells all fail before an authorized mutation/result. |
| Independent verification | PASS in repository-external Unicode-safe snapshot: focused 17/17, full 360/360, strict mypy 130 files and in-memory compile 130 files. Source/scope/diff/ancestry/topology and submitted-lane residue checks pass. |
| Evidence truthfulness | PASS: reviewer removed the exact path comparison and CR-157 turned red; reviewer removed parent/child segment-ending guards and the named parent, fresh-child and persisted-state CR-158 checks turned red. Exact immutable blobs were restored and the named tests returned green. |
| CodeReview §2.1 / XSS | Classes 1, 3 and 7 PASS after correction. Class 8 remains `XSS_NOT_APPLICABLE`: no renderer, DOM/HTML, JavaScript context or privileged bridge exists. |

## Final disposition

`APPROVED / READY_TO_MERGE`. CR-157 and CR-158 are closed. Guarded
integration may merge only exact handoff
`002b2982cbf111262865946dc16d83c23a7bc879`, preserving this approval as
first-parent control history. E1 remains blocked until integration completes.

## Guarded integration

Merge `3fc2f99f9cd4a7fff3e100918089ffed99cc16ab` preserves approval
`28486b8bee3a3df912cdfca9f2061b12c2704b94` as first parent and exact handoff
`002b2982cbf111262865946dc16d83c23a7bc879` as second parent. The sole conflict
was append-only WPR evidence; PRG-267 through PRG-271 were explicitly retained
once and in event order. Post-merge focused 17/17, full 360/360, strict mypy
130 files and compile 130 files pass. E0 is complete and its allocation and
receipt are closed against replay.
