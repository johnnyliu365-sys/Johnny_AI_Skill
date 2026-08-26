# 17｜Fresh `0.4.14` Codex release readmission

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 07, AC-1 through AC-11; Revision-07 clauses 1–4 |
| PRD / CHG / Context / architecture | `PRD-20260823-037` / `CHG-20260823-037`, `PRD-20260826-040` / `CHG-20260826-040`; Context Revision 06 (`CTX-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260826-06`, sealed blob `59363cf1309d8905e1064e76126dbe3fde9bd8e3`); ADR-015 and ADR-018. |
| State / closure | `APPROVED_NOT_DISPATCHED / CLOSURE_01` |
| Dependency | Ticket 16 must be `DONE / APPROVED / INTEGRATED` on the observed development authority line. Ticket 15 is terminally blocked and is not retried. |
| Control owner / reviewer | Current-session Codex reviewer; `ticket-review` profile. The reviewer personally performs every release readback, cache proof, candidate commit, gate admission and push. |
| Implementation owner | None. This is reviewer-only evidence and integration work; it does not delegate source changes. |
| Delivery profile | `POC / HIGH_ASSURANCE`: fresh public-ref snapshot, isolated actual Codex install/cache proof and guarded authority-line integration. |
| Worktree / branch | Reviewer rebases the preserved reviewed Ticket-15 source candidate onto the post-Ticket-16 authority SHA, records the exact branch and candidate SHA, and creates one temporary Git marketplace ref for the isolated Codex proof. No replacement payload is made by hand. |
| Language / checker | Python 3.11 verification contracts plus the real Codex plugin CLI. |
| XSS / effects | `N/A`; all named Git, cache, CLI and authority-line effects are reviewer-only and must be directly read back. |

## Boundary declaration

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = commands/johnny-project-takeover.md
modify = skills/johnny-project-takeover/SKILL.md
create = skills/johnny-project-takeover/references/codex-native-same-lifetime-delegation.md
modify = README.md
modify = tests/test_plugin_publication.py
forbid = template/
forbid = library/
forbid = modules/
forbid = doc/
forbid = README.md
forbid = .codex-plugin/
forbid = install.ps1
forbid = johnny-install.cmd
```

The preserved Ticket-15 source commit is evidence only until this ticket freshly binds it. The
declared source paths are allowed because that exact reviewed candidate carries them; the reviewer
may not change them while rebasing. It may run the generator and let the generator write the
marketplace pin only if it reproduces the already-existing immutable `0.4.14` root. No one may
hand-edit a SHA, move/delete/recreate any tag, force a publication ref, change a user
profile/cache, or reuse Ticket 15’s stale effect authority.

## Sole observable closure

The development authority line advertises the existing `0.4.14` payload only after a fresh
isolated Codex install proves `VERIFIED` with the Ticket-16 cache verifier: the plugin checkout
binds to the expected generated root, and any retained historical release tags validate against
their own immutable target declarations. The current source candidate's generated root, public
publication `main` and `plugin-v0.4.14` tag must all be the same parentless commit. Any changed,
unknown, missing or mismatched fact halts before development integration.

Codex's effective `plugin marketplace add` capability admits a local or Git marketplace source;
it does not admit the raw descriptor URL used by Claude's documented marketplace flow. This POC
therefore uses the candidate development repository and its exact temporary Git ref only inside a
fresh disposable `CODEX_HOME`. That host-owned marketplace clone is a named limitation, not
plugin-cache closure evidence and not a claim that Codex avoided cloning development history. The
plugin install still resolves its declared `source.url` to the independent publication repository.
Eliminating this marketplace clone, and retaining no historical release payload in either cache,
is the separately deferred next-major-version archive/snapshot objective.

## Reviewer-only effect authority

This owner directive authorizes one fresh, non-retry readmission after Ticket 16 is integrated.
Immediately before every effect, directly read the development authority SHA, publication `main`,
all admitted publication refs/tags and the named temporary candidate ref. The exact values found
become this attempt’s record; they are not inferred from Ticket 15.

Allowed effects, in order:

1. Rebase the preserved reviewed source candidate onto the observed development authority SHA;
   generate and verify its root against its declaration. The root must equal existing publication
   `main` and the existing immutable `plugin-v0.4.14` target.
2. Update only the generator-owned marketplace pin in that candidate when regeneration proves the
   same root; commit the reviewed candidate and push one newly named temporary Git marketplace
   ref.
3. In a short-path disposable `CODEX_HOME`, add the development repository as a Git marketplace at
   that exact temporary ref, install `johnny-ai-skill@johnny-ai-skill`, and directly verify the
   installed plugin version, checkout root, ref grammar and installed-cache closure. Do not alter
   the user’s global configuration/cache or describe the host marketplace clone as payload closure.
4. Only after all source, ref and cache evidence is green, invoke `admit_document_mutation`,
   non-force push the resulting development `main`, and directly read back its exact SHA.

An existing/moved/mismatched tag, changed publication root, unknown ref, regeneration mismatch,
cache failure, install failure, gate refusal, push failure or readback mismatch is
`HALT / RELEASE_READBACK_MISMATCH`. It authorizes no retry, tag operation, publication push,
cache edit, user-profile effect or fallback release path.

## Verification and completion

Run the Ticket-15 source/payload tests plus the repaired installed-cache and publication-closure
suites, strict typing/compile checks from Ticket 16, generator reproduction and the actual
isolated Codex install/readback. Terra records the candidate/root/tag/integrated SHA and sanitized
cache result. Completion is `AUTHORITY_INTEGRATED` only after the gate returns the candidate SHA,
the non-force push succeeds and direct `origin/main` readback equals it.

The next major-version goal—archive/snapshot installation with no retained historical payload in
the cache—is not an alternative path here. It needs a separate requirement and architecture
decision after this corrective release is closed.
