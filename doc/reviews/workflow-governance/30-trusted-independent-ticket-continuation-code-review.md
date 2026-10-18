# Ticket 30 source-contract decision review — 2026-10-18

| Field | Evidence |
| --- | --- |
| Prior control baseline | `789302c4345aedb5439770ebb7aad1c9ac0f3cd8` |
| Initial decision candidate | `0bfb4a2869f9fbb73e67a3c1a436a8e341fd66c2` — two findings |
| Additive correction | `f13f35711594af241c83b803f91f0f472baa6241`; Ticket30 leaf blob `823ef2d0e86bbc74a8508263be1a8bde678f6324` |
| Independent reviewer | `/root/ticket42_review` (`gpt-6-sol/high`), different from the Architecture Owner analysis |
| Conclusion | `PASS` for bounded docs-only technical source contract; `NON_DISPATCHABLE` remains |

First review found that an index-only graph contradicted workflow-governance
SPEC AC9's committed-leaf derivation, and that existing `GitBlobReadResult`
has a string payload, insufficient for a raw-byte digest claim. The same-ticket
correction requires a unique machine-readable ticket fence in each committed
leaf, compares its graph/status fields with the index and rejects mismatches;
the candidate projection is built only from validated leaves. The bounded
readback port now names a raw-byte result using the existing finite status
enum, hashes those bytes, and strictly decodes UTF-8 before JSON parsing.

Reviewer readback of the exact correction found both findings closed,
one-file docs-only scope, clean worktree and `git diff --check` exit 0. No
runtime tests or external effects were performed; this is a source-contract
decision, not an implemented or qualified adapter. No target facts were
inferred from the human status table. Mainline migration, admitted declaration
readback, ticket-scoped Grant, Router/Host admission, and formal closure stay
unverified. No push or release occurred.
