# ADR-20260823-017 — Level 1 ships a reachable reusable surface, not host-local tooling

- Date: `2026-08-23 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260823-035` / `CHG-20260823-035`
- Affected specification: `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P`, Revision 03
- Amends: `ADR-20260823-015-dedicated-plugin-publication-repository.md`

## Context

ADR-015 correctly moved Claude's clone boundary to a dedicated publication repository, but it
left Level 1's declaration at the entire `library/` root. The payload consequently contains the
generator, publication contracts and cache verifier that decide whether a payload can be released.
Those tools live in `library/local_orchestration/`, so repairing them also changes the generated
payload root. The same self-reference produced the Ticket 04 pin contradiction and, after Ticket
10, the immutable `plugin-v0.4.10` collision.

F3 requires a topology correction before a successor version is chosen. A one-file exception for
`worktree_containment.py` was evaluated and rejected: importing that module initializes the
host-only `library.local_orchestration` package and requires its broad runtime dependency set.
Shipping only that leaf would make an unavailable host capability look delivered.

## Decision

Level 1 becomes an explicit reachable reusable-source surface:

```text
Level 1 trees
  .claude-plugin/  commands/  skills/  template/
  library/NLP/  library/功能集群/  library/金流串接/
  library/catalog/  library/workflow_router/

Level 1 exact library files
  library/__init__.py
  library/MODULE_CATALOG.md

Not Level 1
  library/local_orchestration/**
  install.ps1  johnny-install.cmd
```

The manifest/generator contract accepts clean nested tree declarations and evaluates them by full
segment-prefix, never by a raw string prefix. The declaration does not name `library/` itself.
Therefore an undeclared child such as `library/local_orchestration/plugin_publication.py` cannot
enter Level 1 merely because it shares a top-level directory with reusable source.

The installed catalog retains reusable source that its skills may select. It no longer offers the
host-local `local-orchestration` entry as a Claude-plugin module. `AGENTS.md` retains the
repository-contained-worktree rule as policy, without pointing a detached plugin at a missing
host helper. Level 2's package declaration is a separate owner and is not changed.

## Alternatives and trade-offs

- **Keep `library/` and add an exclusion list.** Rejected: a new sibling under `library/` would
  silently publish unless each development path were remembered in a denylist; that is the
  remainder model F3 removes.
- **Ship only `worktree_containment.py`.** Rejected: its containing package initialization imports
  the absent host runtime. A static path is not a usable runtime boundary.
- **Remove all reusable library source from Level 1.** Rejected: it breaks the installed
  reusable-module selector, which intentionally traverses an exact selected card, public API and
  contract.
- **Choose `0.4.11` immediately.** Rejected: F3 exists to stop tool repairs from repeatedly
  changing the root before the successor version is selected.

## Consequences, risks and recovery

- F3 changes the generated payload root but creates no external effect and no version/tag choice.
- A successor release must use a new immutable version/tag after F3 is integrated, reviewed and
  its generated tree is proved closed.
- The controlled source has one more declaration shape to validate: malformed nested paths,
  overlapping/sibling leakage and undeclared local-orchestration entries need negative tests.
- Recovery before release is a normal source revert. Recovery after a future release remains the
  ADR-015 descriptor rollback path; no immutable tag is moved.
