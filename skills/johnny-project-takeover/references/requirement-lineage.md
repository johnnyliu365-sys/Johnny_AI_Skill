# Requirement lineage and archive library

Read this reference when creating, revising, superseding or locating a product requirement or
requirement change.

## One-to-one identity

Every product requirement has one matching change identifier with the same date/sequence suffix:

```text
PRD-YYYYMMDD-NNN <-> CHG-YYYYMMDD-NNN
```

The active `PRD.md` and `doc/RequirementChangeLog.md` are root indexes. They contain identifiers,
state and exact leaf references, not every requirement body. The canonical active leaf contains
the effective product statement, change decision and links to its Context/SPEC/ADR evidence.

## Retirement

When a requirement no longer applies, move the PRD/CHG pair out of the active tree into one
immutable archive bundle identified as `ARCH-REQ-YYYYMMDD-NNN`. The bundle records both retired
IDs, last active revision, reason, replacement IDs when any, and historical source commit.

Active PRD and change roots then retain only the archive bundle ID and its archive-tree reference.
They must not keep the retired requirement title/body, status narrative or replacement prose.
Git history remains evidence but is not the runtime lookup mechanism.

## SPEC archive

A SPEC that no longer governs any active work moves, unchanged, to
`doc/archive/specs/<year>/<slug>.md`. The year is the year it is archived. The move is a rename;
the content is not edited.

- The archive root `doc/archive/specs/README.md` lists only year partitions. Each year index lists
  one row per archived SPEC: an archive ID `ARCH-SPEC-YYYYMMDD-NNN`, the leaf link, the SPEC ID,
  its last active revision, the reason, the replacement where one exists, and the historical
  source commit (the last commit with the SPEC at its active path).
- The active SPEC index (`modules/spec/README.md`) keeps only the archive ID and the archive
  reference of an archived SPEC, never its title narrative or status.
- Active documents that cite an archived SPEC cite its archive path.
- Historical records keep the path they were written with. These are review records, tickets,
  handoffs and feature Context files. Git history is the evidence for that path.

The validation rules below apply to SPEC archive IDs as they apply to `ARCH-REQ` bundles.

## Validation

- Active PRD and CHG suffixes must match and resolve to one active leaf.
- An active ID cannot also appear in an archive bundle.
- An archived pair cannot remain reachable through an active child edge.
- Archive roots list only direct partitions; year/category indexes list only direct archive
  bundles; bundle leaves contain the retired association.
- Duplicate, dangling, cyclic, wrong-revision or mixed active/archive references are
  `HALT / REQUIREMENT_LINEAGE_INVALID`.
- For SPEC archive IDs, each of these is `HALT / REQUIREMENT_LINEAGE_INVALID`: a duplicate archive
  ID; a dangling or mixed active/archive reference; a SPEC present at both its active and its
  archive path.
