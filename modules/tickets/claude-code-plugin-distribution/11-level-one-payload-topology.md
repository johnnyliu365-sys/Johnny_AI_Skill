# 11｜Level 1 reachable payload topology

| Field | Binding |
| --- | --- |
| SPEC / AC | Revision 03, AC-10; AC-3 compatibility guard |
| PRD / CHG / Context | `PRD-20260823-035` / `CHG-20260823-035` / sealed Context Revision 02, blob `f53b2a7dedf055e50ad44804e590f22991a3d5c9` |
| State / closure | `DONE / APPROVED / INTEGRATED` / `F3` |
| Integration | `admit_document_mutation` → `7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7` |
| Exact baseline | `e5278cde35f2b956d62508564407f6bfd419c6bb` |
| Dependency | Tickets 02–05, 06, 07, 09 and 10 remain historical evidence. Ticket 08 is blocked and has no successor-version/effect authority. |
| Control owner / reviewer | `ticket-review` — Terra / xhigh |
| Implementation owner | `implementation-standard` — Luna / xhigh; one ticket, no helper lane |
| Delivery profile | `POC / STANDARD`: deterministic local manifest, source and test changes only. No Claude CLI, user cache, remote, repository, ref, tag, version, release, source URL, descriptor pin or push effect is permitted. |
| Implementation language / checker | Python 3.11 / `mypy --strict` over changed Python production/test modules; JSON boundary validation remains required. |
| XSS classification | `N/A` |
| Worktree / branch | `.worktrees/claude-publication-11` / `implement/claude-publication-11-payload-topology` |
| Dispatch mode | Same-lifetime reviewer dispatch → `wait_agent` → receive → independent review. In this POC profile, no runner, queue, receipt, live dispatch descriptor or host workspace-binding readback is a precondition; their absence must not be reported as delivery. |

## Boundary declaration

```johnny-boundary
modify = .claude-plugin/plugin.json
modify = AGENTS.md
modify = skills/johnny-project-takeover/SKILL.md
modify = library/catalog/workflow-control/README.md
modify = library/local_orchestration/plugin_publication.py
modify = tests/test_plugin_payload_boundary.py
forbid = .claude-plugin/marketplace.json
forbid = README.md
forbid = CodeReview.md
forbid = Defined_wayfinder.md
forbid = Workflow.md
forbid = install.ps1
forbid = johnny-install.cmd
forbid = library/local_orchestration/claude_plugin_cache_closure.py
forbid = library/local_orchestration/publication_repository_closure.py
forbid = library/local_orchestration/publication_promotion.py
forbid = library/local_orchestration/windows_package_manifest.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = tests/test_claude_plugin_cache_closure.py
forbid = tests/test_publication_repository_closure.py
```

No other `library/local_orchestration/` file is writable. The candidate changes the Level 1
declaration and the one generator-owned declaration parser/matcher that materializes it; it does
not change the Level 2 package declaration, any source or marketplace pin, or any release input.

## Sole observable closure

The Level 1 generator accepts a clean, segment-exact nested-tree allowlist and materializes only
the Claude skill's reachable reusable-source surface. The committed declaration carries
`.claude-plugin`, `commands`, `skills`, `template`, `library/NLP`, `library/功能集群`,
`library/金流串接`, `library/catalog`, and `library/workflow_router`, plus exact
`library/__init__.py` and `library/MODULE_CATALOG.md` files and the existing root governance
documents. It carries neither `library/` as a whole nor a path below
`library/local_orchestration/`, `install.ps1`, or `johnny-install.cmd`.

The catalog no longer presents `local-orchestration` as a `READY` Claude-plugin selection. The
worktree containment invariant stays in `AGENTS.md` as policy; the detached plugin does not point
to a host-only helper as if it were a usable runtime API. Existing selected reusable library
partitions, catalogue traversal, workflow-router contracts and plugin skill/command surface remain
closed and usable.

## Frozen contract

1. `payload.trees` accepts only non-empty clean repository-relative directory paths composed of
   ordinary segments. It rejects absolute paths, `.`/`..`, empty segments, whitespace-padded
   entries, forbidden paths and sibling/prefix ambiguity. Membership compares full path segments:
   `library/local_orchestration/x.py`, `libraryx/x.py`, and an undeclared `library/new_dev/x.py`
   are outside the F3 declaration.
2. The generator, `declared_payload_files()`, the closure scanner and all payload tests use that
   single declaration/matcher implementation. No second membership algorithm, hand-maintained
   release tree or broad `library` fallback is introduced.
3. The payload's declared text documents remain closed. `AGENTS.md` states contained worktree
   policy without a reference to an absent local-orchestration helper; the takeover skill no
   longer uses `install.ps1` as a path-shaped dependency; the workflow-control catalog does not
   link the excluded local-orchestration README.
4. `library/local_orchestration/plugin_publication.py` is development control-plane source during
   this one source candidate and is absent from its future generated Level 1 tree. Its change is
   expected to change the generated root; this ticket must not select or write a version/tag/SHA.
5. The Level 2 `_PAYLOAD_TREE_ROOTS` literal, bundle installer and Codex/plugin sources remain
   byte-for-byte outside this ticket. A ticket that needs one of them returns `CHANGE_DETECTED`.

## TDD matrix

| Cell | Required executable proof |
| --- | --- |
| F3-1 nested declaration admission | A fixture declaring the approved nested library trees loads and matches only exact segment descendants. Traversal, empty, absolute, whitespace-padded and prefix/sibling entries are rejected at the manifest boundary. |
| F3-2 exclusion by construction | The committed generated payload contains no `library/local_orchestration/` path and no standalone installer. A bounded reverse mutation that adds the excluded local-orchestration tree/path to the declaration turns the topology proof red; byte-for-byte restoration returns green. |
| F3-3 reachable surface closure | The committed declaration still carries the two skills, two commands, root catalog, all selected reusable partitions and workflow router. Removing one retained catalog/router surface entry turns `assert_payload_closed()` red; exact restoration returns green. |
| F3-4 static-reference repair | The revised AGENTS/skill/catalog prose has no unresolved reference to an excluded helper, installer or local-orchestration catalog leaf. The existing closed-reference test stays green without broadly declaring development-only exceptions. |
| F3-5 independent review mutation | Terra creates a fresh manifest fixture or bounded candidate mutation independent of the implementer's evidence. One forbidden local-orchestration admission must go red, and exact restoration must return green. A zero-red mutation blocks approval. |
| F3-6 Level 2 independence | The existing literal-independence test stays green and the candidate diff contains no Level 2 manifest or installer path. |

## Strong-type and verification preflight

The public change is a JSON declaration parsed at the existing validation boundary. The
implementer must preserve named `PayloadDeclarationError` rejection for malformed declaration
input and must not introduce `Any`, cast, dynamic lookup or a raw-string prefix rule into the
matcher. Construct positive fixture declarations through normal JSON/file loading; malformed
declarations are negative-only inputs.

Run, at minimum:

```text
py -3.11 -m unittest discover -s tests -p test_plugin_payload_boundary.py -v
py -3.11 -m mypy --strict library/local_orchestration/plugin_publication.py tests/test_plugin_payload_boundary.py
py -3.11 -m compileall -q library/local_orchestration/plugin_publication.py tests/test_plugin_payload_boundary.py
git diff --check
```

The implementation owner records F3-2 and F3-3 reverse-mutation commands/results and commits
only the declared source boundary. `COMPLETED` returns `ACTION_COMPLETED` with the candidate
commit and evidence summaries; any request to choose a version, repin, mutate a remote/ref/tag,
run Claude, modify a cache, or broaden the payload returns `CHANGE_DETECTED` or `BLOCKED`.

## Review and continuation

Terra verifies candidate ancestry against the exact baseline, declared-path-only diff, all TDD
cells, strict type/compile/diff gates, and independently runs F3-5. Passing review permits only
`admit_document_mutation` from this ticket's boundary, followed by a readback/push of its source
commit. It does not re-admit Ticket 08. The next Router event is the owner decision selecting a
successor version/tag; no agent infers that value from this ticket.

## Completion evidence

Luna/xhigh implemented the declared six-path candidate at
`7a64f6312d8cd2a84a8821eb1dac2f00e205c8b7`. The focused payload-boundary suite passed 41 tests;
strict mypy, compileall, JSON validation and diff check were green. The implementer recorded F3-2
and F3-3 red-to-green reverse mutations.

Terra/xhigh independently verified clean ancestry and the exact six-path boundary, then ran F3-5
through the production materializer: adding only
`library/local_orchestration/plugin_publication.py` produced
`GREEN -> TOPOLOGY_ASSERTION_RED -> GREEN` after byte-exact restoration. The reviewer found no
Level 2, marketplace, installer, version, pin, source-URL or external-effect change. The document
mutation gate integrated the exact candidate and `origin/main` read back the stated commit.
