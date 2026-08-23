# 09｜Pin-carrier closure normalization

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 02, AC-1 through AC-4; Ticket 06 closure contract; Ticket 08 L2 blocker record |
| PRD / CHG / Context | `PRD-20260823-034` / `CHG-20260823-034` / sealed Context Revision 01, blob `0fef3f1e4c8ce317873cdf2f73dc1bd793579217` |
| State / closure | `APPROVED / DISPATCH_READY` / `CLOSURE_01` |
| Exact baseline | `3f510ff816cb012b4efaed679720bc7721848169` |
| Dependency | Ticket 06 integrated closure modules; Ticket 08 blocked L2 record. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket only, no helper |
| Delivery profile | `POC / HIGH_ASSURANCE`: fixes the supply-chain closure proof used before an external publication. No remote, release or install effect is permitted in this ticket. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over each changed public module and focused test module |
| XSS classification | `N/A` |
| Worktree / branch | `.worktrees/claude-publication-09` / `implement/claude-publication-09-pin-carrier-closure` |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/plugin_publication.py
modify = library/local_orchestration/publication_repository_closure.py
modify = tests/test_plugin_publication.py
modify = tests/test_publication_repository_closure.py
forbid = .claude-plugin/plugin.json
forbid = .claude-plugin/marketplace.json
forbid = README.md
forbid = library/local_orchestration/claude_plugin_cache_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = skills/
forbid = install.ps1
forbid = johnny-install.cmd
```

The change is a local verifier/generator contract correction. It must not create, move, delete or
push a Git ref; contact a remote; create a repository or tag; invoke the Claude CLI; or alter the
Ticket 08 candidate's metadata, descriptor, README or generated pin.

## Sole observable closure

For a declared payload whose marketplace manifest is also its pin carrier, the closure verifier
accepts the generated publication root only when its carrier is exactly the generator's one-field,
one-occurrence, dead-SHA normalization and can be healed with the live candidate pin to byte-equal
content. It continues to reject every changed path, extra/missing tree entry, non-carrier blob
change, malformed carrier, second occurrence, usable/moved carrier SHA or carrier not declared in
the payload.

The pin carrier is not omitted from the payload comparison and no path pattern grants an
exception. The implementation must introduce one shared, typed normalization/healing primitive
used by both generation and closure verification, so the two paths cannot silently adopt different
placeholder, JSON-location, cardinality or line-ending rules. The verifier's public inputs stay
strongly typed and all invalid dynamic input is normalized at its boundary.

## Frozen contract

1. A pin-carrier is explicitly named as a declared relative payload path; an absent carrier retains
   Ticket 06's exact byte/blob equality behavior.
2. For an explicitly named carrier, generation replaces exactly the one full source SHA at the
   established marketplace `plugins[0].source.sha` location with the established dead full-SHA
   placeholder before hashing the parentless root.
3. Closure verification reads the generated carrier blob and accepts it only if it contains that
   placeholder exactly once at the same location. It heals only that occurrence with the live,
   validated full pin and requires byte equality with the candidate carrier after the established
   line-ending normalization.
4. The pin to heal with must be the validated candidate/source identity already bound by the
   closure call; a partial, malformed, absent, second or unrelated SHA is a finite refusal, never
   an ignored mismatch.
5. The carrier remains part of the full ref/parent/root/tree closure. No branch/ref rule, remote
   behavior or promotion/CAS behavior changes in this ticket.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| N1 matching generated carrier | A generated parentless fixture with an explicitly declared carrier verifies `VERIFIED`; re-running generation produces the same root. |
| N2 only-field mutation | Changing any marketplace-carrier field other than its one SHA, adding a second SHA occurrence, using a non-placeholder SHA in the generated tree, or healing with another valid SHA turns the closure red. Exact restoration returns green. |
| N3 ordinary payload unchanged | With no named carrier, ordinary content mismatch remains `TREE_MISMATCH`; an extra/missing path or ref still returns its existing named failure. |
| N4 carrier admission | A carrier outside the declared payload, malformed JSON/location, partial/malformed live pin, or bypass-built malformed typed input is refused before `VERIFIED`. |
| N5 shared primitive | Generator and closure tests use the one shared typed primitive; a test that changes its placeholder/cardinality behavior makes either path red. |
| N6 adversarial review | Terra independently adds a reachable development ref/tree after an otherwise green local fixture, observes the Ticket 06 closure turn red, then restores green; it separately mutates the carrier's non-SHA content and observes red. |

## Verification and completion

Run focused generator/closure tests, `tests/test_plugin_payload_boundary.py`, strict mypy over the
two changed modules/tests, compileall and `git diff --check`. The reviewer performs N6 from a
fresh local fixture and verifies Ticket 08's recorded root `758a7187f6cee5dbb231cd85fe2c4f5d3e03f4b3`
can obtain `VERIFIED` only after the full carrier proof is present.

`COMPLETED` returns `ACTION_COMPLETED`. A request to reuse the empty publication repository,
push a payload/tag/ref, modify the Ticket 08 candidate or run Claude is `BLOCKED` or
`CHANGE_DETECTED`; it does not become an effect through this ticket.
