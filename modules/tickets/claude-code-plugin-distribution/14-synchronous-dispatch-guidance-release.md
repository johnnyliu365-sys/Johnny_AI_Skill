# 14｜Synchronous-dispatch guidance qualification and Level 1 release

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 05, AC-1 through AC-7 and AC-11; ADR-20260823-014 Decisions 1–3 and 7 |
| Requirement / Context / architecture | `PRD-20260823-034` / `CHG-20260823-034`; sealed Context Revision 04 (`f175d6a6842ca1d24a3cfd85e3a24542e7d7b9a3`); ADR-20260823-014, ADR-20260823-015 and ADR-20260823-018 |
| State / closure | `APPROVED_NOT_DISPATCHED / CLOSURE_01` |
| Baseline | `b5be5e26a8ff84fbae0ab7a659c505a1216fb09c` |
| Control owner / reviewer | Current-session Codex reviewer; `ticket-review` profile, Terra/xhigh minimum |
| Implementation owner | `implementation-standard`, Luna/xhigh; one owner and no helper lane |
| Delivery stage / profile | `POC / STANDARD` for source changes and review; `POC / HIGH_ASSURANCE` for the exact owner-authorized publication, tag and isolated install effects below |
| Implementation language / checker | Markdown source guidance and JSON manifests; JSON parsing plus existing Python 3.11 publication and cache-closure checks |
| XSS / effects | XSS_NOT_APPLICABLE. The implementation owner has no host, runner, queue, receipt, task-control, ref, tag, remote, credential, cache or CLI effect authority. |
| Worktree / branch | `.worktrees/claude-publication-14-sync-dispatch-release` / `implement/claude-publication-14-sync-dispatch-release` |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → receive → review. No runner, queue, receipt, live descriptor or host workspace readback is a precondition. |

## Cause and required correction

ADR-20260823-014 is accepted. It says that the runner and its receipt-bound gateway bridge
different lifetimes only; the default same-lifetime path is reviewer dispatch → wait → receive →
review → `admit_document_mutation`, with no runner, queue, receipt, descriptor or host gateway.

The following shipped references still describe the cross-lifetime machinery in the present
indicative and therefore turned an optional bridge into a universal dispatch precondition. Ticket
05 in `context-load-telemetry` is already corrected and is not in this ticket's boundary.

1. `skills/johnny-project-takeover/references/router-control.md`, **Dispatch admission**: scope
   the descriptor/receipt rule to cross-lifetime dispatch. State that a synchronous reviewer-owned
   lane does not consume a receipt and must not halt because that bridge is unavailable.
2. `skills/johnny-project-takeover/references/implementation-authority.md`, **Orchestration
   gateway**: scope gateway validation and host-readback requirements to the cross-lifetime path.
   Preserve reviewer-only agent control and fail-closed binding in that path.
3. The same reference, **Task/worktree admission**: preserve the three-way normalized-root,
   filesystem-identity and Git-metadata proof where a host task is resumed across lifetimes. For a
   synchronous lane the reviewer directly allocates the repository-contained worktree and binds
   the owner to its exact ticket, branch and worktree; absent host readback may not block it.

The correction must name the three finite wake dispositions from ADR-014: `NOT_REQUIRED`,
`AVAILABLE` and `UNAVAILABLE`. It must neither claim an unavailable wake was delivered nor invent
a receipt issuer, host gateway, durable queue or runner for the synchronous path.

## Boundary declaration

```johnny-boundary
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/implementation-authority.md
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = README.md
modify = tests/test_plugin_publication.py
forbid = .codex-plugin/
forbid = commands/
forbid = library/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

The implementation owner changes only the six declared files, does not commit, and returns the
uncommitted diff plus test evidence. It must not hand-edit a publication SHA, create/move/delete
any ref, contact a remote, invoke Claude, alter a user cache or claim that a release occurred.
The reviewer alone may generate and repin the self-referential carrier, commit the reviewed
candidate, execute the authorized external operations, integrate, and push.

## Release version and exact owner effect authority

The changed `skills/` tree is Level 1 payload. `0.4.11` and `plugin-v0.4.11` are immutable, so
the selected successor is `0.4.12`; a changed payload must not reuse its tag.

This owner directive authorizes one reviewer-operated release attempt only after the candidate is
reviewed and all local checks below pass:

| Binding | Authorized value |
| --- | --- |
| Development candidate branch / temporary raw ref | `implement/claude-publication-14-sync-dispatch-release` / `refs/heads/verify/claude-publication-14-v0412-synchronous-dispatch` |
| Correlation | `claude-publication-14-v0412-synchronous-dispatch-20260824` |
| Publication repository / version | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git` / `0.4.12` |
| Required pre-effect snapshot | default branch `main`; `main = 5c1cb9aec837a2fc8c76634404bccd393a0b9281`; `plugin-v0.4.10 = b52215eb3ee5dfa101e65c189441e62c20ca45e6`; `plugin-v0.4.11 = 5c1cb9aec837a2fc8c76634404bccd393a0b9281`; `plugin-v0.4.12` absent |

Immediately before every remote mutation the reviewer re-reads the remote. Any changed default
branch, main SHA, retained tag, foreign ref or pre-existing `plugin-v0.4.12` is
`HALT / RELEASE_READBACK_MISMATCH`; there is no retry, fallback or tag movement.

Subject to that readback and the local/reverse-mutation evidence, the owner authorizes the
reviewer to: create only the new generated parentless root `C` at publication `main` through the
Ticket-07 compare-and-swap plan; create the absent-only `plugin-v0.4.12` at `C`; push only the
named temporary development ref; run the README commands in a disposable isolated
`CLAUDE_CONFIG_DIR`; after verified closure, integrate the exact candidate and push development
`main`; and then repeat the isolated main-descriptor readback. No other remote, tag, user-profile,
credential, runner or provider effect is authorized.

## Observable closure and required evidence

The shipped source distinguishes both dispatch paths without weakening the cross-lifetime gate.
A reader can route same-lifetime work without an invented bridge, while a different-lifetime
handoff still requires its receipt-bound safeguards and honestly reports an unarmed wake.

The resulting Level 1 `0.4.12` payload is a generator-produced parentless root `C`; publication
`main` and `plugin-v0.4.12` name exactly `C`; retained tags validate from their own target
declarations; and a real isolated Claude installation from the README reaches no development
tree.

At minimum, the implementation owner runs:

```text
py -3.11 -m unittest discover -s tests -p test_plugin_publication.py -v
py -3.11 -m unittest discover -s tests -p test_publication_repository_closure.py -v
py -3.11 -m unittest discover -s tests -p test_claude_plugin_cache_closure.py -v
git diff --check
```

The reviewer independently verifies scope and clean ancestry; performs one textual reverse
mutation that removes the synchronous exception and confirms the new guidance check fails; and
performs Ticket 08's independent reachable-development-tree/cache mutation after an otherwise
green isolated install. A zero-red counter-mutation blocks approval. The reviewer then verifies
JSON, generator reproducibility, exact publication remote closure, isolated candidate and main
descriptor installation, and guarded integration. The completion record names the candidate SHA,
generated root, pre/post remote snapshots, tag, sanitized CLI/cache result and integrated commit.

## Completion and continuation

`ImplementationReturn.COMPLETED` becomes `ACTION_COMPLETED` only after reviewer evidence,
candidate commit, release readbacks, `admit_document_mutation`, development-main push and final
main-descriptor isolated closure. It does not authorize changes to Codex distribution or Ticket
05's contract boundary.

After this cluster closes, the Router returns to the already-approved
`context-load-telemetry/05-opaque-storage-port-contracts` ticket and dispatches it through the
same-lifetime `wait_agent` loop.

## Completion record

- Candidate and guarded integration: `47502bb112934feb6efead3af89a9ca3b54404c4`, integrated
  by `admit_document_mutation` and pushed as development `main`; local `main`, `origin/main`
  and the candidate all read back to that exact commit.
- Publication pre-state was `main = 5c1cb9aec837a2fc8c76634404bccd393a0b9281`, retained
  `plugin-v0.4.10 = b52215eb3ee5dfa101e65c189441e62c20ca45e6`, retained
  `plugin-v0.4.11 = 5c1cb9aec837a2fc8c76634404bccd393a0b9281`, and no `plugin-v0.4.12`.
  The authorized promotion produced parentless root
  `C = 3b84c5f0f7df0582bd2459e83c6067ed45fb7613`; publication `main` and the new,
  absent-only `plugin-v0.4.12` tag now name exactly `C`, while both retained tags are unchanged.
- The temporary raw candidate ref named in this ticket read back to the candidate before
  deletion and was removed only after source-main integration.
- Candidate and fresh main-descriptor isolated Claude installs both reported marketplace
  `johnny-ai-skill`, plugin `johnny-ai-skill@johnny-ai-skill`, version `0.4.12`, and only the
  two declared skills. The sanitized cache verifier reported `VERIFIED` at `C`.
- The independent installed-cache counter-mutation made an exact reachable
  `modules/review.py` development sentinel and returned `SENTINEL_REACHABLE`; exact ref and
  `HEAD` restoration then returned `VERIFIED`.
- Candidate scope/ancestry checks, JSON/generator/remote-closure checks, the three focused
  publication/cache suites, `git diff --check`, and the textual synchronous-guidance reverse
  mutation all passed before integration.

```johnny-status
id = 14
title = Synchronous-dispatch guidance qualification and Level 1 release
state = DONE
stage = A | Source guidance and candidate metadata | DONE
stage = B | Reviewer-generated root and remote closure | DONE
stage = C | Isolated candidate/main install and guarded integration | DONE
```
