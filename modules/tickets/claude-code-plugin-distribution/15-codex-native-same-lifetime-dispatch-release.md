# 15｜Codex native same-lifetime dispatch guidance and Level 1 release

| Field | Binding |
| --- | --- |
| SPEC / AC | Specification Revision 06, AC-1 through AC-7 and Revision-06 continuation clauses 1–5 |
| Requirement / Context / architecture | `PRD-20260826-040` / `CHG-20260826-040`; Context Revision 05 (`CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260826-05`, sealed blob `1dbdf84d0abc5e732f3915e2195321a44db29056`); ADR-014 through ADR-018. |
| State / closure | `APPROVED_NOT_DISPATCHED / CLOSURE_01` |
| Control owner / reviewer | Current-session Codex reviewer; semantic `ticket-review` profile. The reviewer personally performs review, reverse mutation, candidate commits, gate admission and every release effect. |
| Implementation owner | One current-session owner selected from this ticket's `implementation-standard` profile; the ordinary model/effort binding is recorded only at dispatch. One owner; no helpers. |
| Delivery stage / profile | `POC / STANDARD` for source and deterministic tests; `POC / HIGH_ASSURANCE` for publication, remote refs/tag, development-main push, and isolated Codex cache verification. |
| Worktree / branch / baseline | Reviewer creates `.worktrees/claude-publication-15-codex-native-dispatch-release` on `implement/claude-publication-15-codex-native-dispatch-release` from the clean authority-line SHA containing this committed ticket. The SHA is recorded at dispatch. |
| Language / checker | Markdown and JSON; Python 3.11 `unittest` policy/payload/publication checks; JSON parsing. |
| XSS / effects | `N/A` for source closure. The implementation owner has no runner, queue, receipt, task-control, ref, tag, remote, credential, cache or CLI effect authority. |

## Cause and desired behavior

The current entry command ends with “say what it is” and “Do not begin implementation work.” That is correct before a ticket exists, but false after the Router has already declared an admitted same-lifetime `AUTO_CONTINUE → IMPLEMENT` action. Codex exposes native subagent delegation and completion waiting; the command/skill must direct their use only in that case.

```text
admitted exact ticket + same-lifetime AUTO_CONTINUE → IMPLEMENT
  → reviewer creates the ticket-bound owner through Codex native delegation
  → reviewer waits for completion without activity/status polling
  → implementation return → reviewer review / counter-mutation / existing gate
```

This direct synchronous coordination must not create a runner, queue, receipt issuer, pending descriptor, gateway, host-readback adapter, durable state, or false wake claim. A cross-lifetime handoff remains receipt-bound. If Codex cannot expose native delegation or the ticket's selected profile, return `HALT / CODEX_NATIVE_DELEGATION_UNAVAILABLE` rather than have the reviewer implement or fabricate an adapter.

## Boundary declaration

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = commands/johnny-project-takeover.md
modify = skills/johnny-project-takeover/SKILL.md
create = skills/johnny-project-takeover/references/codex-native-same-lifetime-delegation.md
modify = README.md
modify = tests/test_plugin_publication.py
modify = .claude-plugin/marketplace.json
forbid = .codex-plugin/
forbid = library/
forbid = template/
forbid = modules/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

The implementation owner changes only the first six source/test paths, does not commit, alter the marketplace pin, create/move/delete refs, contact a remote, change a cache, invoke a CLI, or claim publication. The reviewer alone may generate the publication root, repin the carrier, commit, run release readbacks, create the authorized tag, push, install/update in an isolated Codex plugin cache, and invoke `admit_document_mutation`.

## TDD and deterministic source closure

| Cell | Required behavior |
| --- | --- |
| T1 | The command distinguishes pre-ticket narration from an already-admitted same-lifetime implementation continuation; it does not globally forbid the latter. |
| T2 | The skill/reference requires native Codex delegation only after exact ticket, worktree, baseline, profile and direct-lane bindings, and names reviewer ownership. |
| T3 | The reference directs completion waiting without status/activity polling and preserves `NOT_REQUIRED` for the bridge. |
| T4 | Missing native delegation or selected profile produces only `HALT / CODEX_NATIVE_DELEGATION_UNAVAILABLE`; no reviewer-implementation fallback, runner, queue, receipt, descriptor or fabricated adapter is allowed. |
| T5 | The command/skill/reference contain no provider/model literal; selected model and effort are read from the ticket/profile. |
| T6 | The plugin manifest declares exactly `0.4.14`; the generated payload contains the corrected command, skill and reference and remains declaration-valid. |
| M1 | Remove the admitted direct-lane exception from the command: T1 turns red; restore byte-for-byte and return green. |
| M2 | Remove the named unavailable-capability halt or add a reviewer fallback: T4 turns red; restore byte-for-byte and return green. |
| M3 | Add a provider/model literal to the new Codex guidance: T5 turns red; restore byte-for-byte and return green. |

The implementation owner runs:

```text
py -3.11 -m unittest tests.test_plugin_publication -v
py -3.11 -m unittest tests.test_plugin_payload_boundary -v
py -3.11 -m unittest tests.test_claude_plugin_cache_closure -v
git diff --check
```

The reviewer independently repeats the focused suites and `git diff --check`, validates JSON, inspects exact cumulative scope, and performs M1–M3 in a disposable copy. A zero-red mutation blocks approval.

## Exact reviewer-only release authority

After a green source review, this owner directive authorizes one reviewer-operated release attempt only. The successor is `0.4.14`; `plugin-v0.4.14` must be absent before mutation and may be created only at the newly generated parentless root `C`.

| Binding | Authorized value |
| --- | --- |
| Candidate branch / temporary raw ref | `implement/claude-publication-15-codex-native-dispatch-release` / `refs/heads/verify/claude-publication-15-v0414-codex-native-dispatch` |
| Correlation | `claude-publication-15-v0414-codex-native-dispatch-20260826` |
| Publication repository | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git` |
| Development authority line | `origin/main`; its current SHA, publication `main`, retained tags and absent `plugin-v0.4.14` are freshly read immediately before every remote mutation. |
| Allowed effects | Generate `C`; CAS-push only publication `main`; create only the absent `plugin-v0.4.14` tag at `C`; push only the named temporary candidate ref; use the documented main descriptor only in an isolated Codex plugin configuration/cache; gate-integrate then non-force-push development `main`; and directly read back every named result. |

Any changed development authority SHA, publication main, retained ref, unknown ref, existing `plugin-v0.4.14`, failed cache closure, failed install/update, or mismatched readback is `HALT / RELEASE_READBACK_MISMATCH`. No retry, force, tag move, cache edit, source-pin hand edit, or broader user-profile mutation is authorized.

## Completion and continuation

`ImplementationReturn.COMPLETED` becomes `ACTION_COMPLETED` only after source/test/reverse-mutation evidence, candidate and generated-pin commits, publication and tag readbacks, guarded integration, development authority-line push/readback, and isolated Codex installed-cache version/content evidence. The completion record names candidate, root, tag, integrated commit, and sanitized cache result. No successful source test alone claims a native subagent was actually invoked in a future session.
