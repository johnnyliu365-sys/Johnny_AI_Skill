# Ticket 07 — deferred shipped-governance verification

| Field | Value |
| --- | --- |
| Ticket ID | PAI-07-DEFERRED-SHIPPED-GOVERNANCE-VERIFICATION |
| State | COMPLETED / RELEASED_0.4.13 / INSTALL_VERIFIED |
| Dependencies | PAI-01 through PAI-05 accepted; PAI-06 is not a release prerequisite. Exact owner release authority is required only when this verification is activated. |
| Source specification | Project authority integration SPEC Revision 11, ticket order item 07 |
| Planning baseline | main at 4df52d0df1fbe479cc9737d390df34d36e402b66 |
| Required future effect | Governance wording alignment followed by regenerated Level 1 publication root, new version, immutable tag, real installation/reload, and CLI readback. |

## Activation — exact bindings (2026-08-25)

| Binding | Value |
| --- | --- |
| Owner release authority | Owner instruction, 2026-08-25: "你來跑06-07,跑完重安裝" |
| Source paths | `skills/johnny-project-takeover/references/router-control.md`, `skills/johnny-project-takeover/references/implementation-authority.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `tests/test_plugin_publication.py` (release-version pin only), `library/workflow_router/profile.py` and `tests/test_workflow_router.py` (R01 versioned-reference registry: a changed reference must re-register its revision/digest — required by `RouteInstructionContractTests`) |
| Governance decisions carried | `ADR-20260824-020` decisions 1–6 (declared authority line, direct remote observation, `LOCAL_INTEGRATED` vs `AUTHORITY_INTEGRATED`, declared topology, high-collaboration PR evidence, provider enforcement qualification) |
| Generator | `write_publication_commit` at the candidate's own revision |
| Version / tag | `0.4.13` / `plugin-v0.4.13`, create-only; existing tags immutable |
| Release target | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill_publication.git`, `main` compare-and-swap plus absent-only tag |
| Installation target | Owner's User workstation Claude CLI, user scope, raw-descriptor marketplace |
| Pre baselines | development `main` at candidate creation; publication `main = 3b84c5f0f7df0582bd2459e83c6067ed45fb7613`, retained tags `plugin-v0.4.10/11/12` |
| Correlation | `pai07-governance-release-20260825` |
| Rollback | Forward-fix only; a defective release gets a successor version, never a moved tag |

```johnny-boundary
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/implementation-authority.md
modify = .claude-plugin/plugin.json
modify = .claude-plugin/marketplace.json
modify = tests/test_plugin_publication.py
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
forbid = .codex-plugin/
forbid = commands/
forbid = library/local_orchestration/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = install.ps1
forbid = johnny-install.cmd
```

## Completion record (2026-08-25)

- Source commit `995c10e7` (wording + versions + R01 re-registration) and generated-pin commit
  `69f46d66` on `implement/pai07-governance-release`; integrated by `admit_document_mutation`
  as development `main = 69f46d66`, pushed, and read back identically from the direct remote.
- The R01 versioned-reference contract fired as designed on its first release: changing the two
  references turned `RouteInstructionContractTests` red until their revision/digest were
  re-registered in `library/workflow_router/profile.py` and its double-entry test pin. The
  boundary was amended to admit exactly those two files, with the reason recorded.
- Full suite on the candidate: 1783 passed, 22 skipped, 3810 subtests, and exactly one failure —
  `test_refusal_guidance` `ClassificationAuditTests` — which fails identically on clean `main`
  before this candidate and is therefore pre-existing (unclassified Failure enums introduced by
  the PAI series, whose integrations ran focused tests only). Reported, not absorbed: it lives in
  `library/local_orchestration/`, outside this boundary and outside the shipped payload.
  Gated qualifications: 28 passed, 1 skipped.
- Generated root `C = 97e9d1aecc4dbf06adc9eb4b9e45dbeefc6e574c`: 142 files, zero
  `tests/`/`doc/`/`modules/`/`local_orchestration` paths, version `0.4.13`, neutralised pin
  carrier. Publication promotion was compare-and-swap: `main` moved `3b84c5f0 -> C` under
  `--force-with-lease` pinned to the expected old value; absent-only tag `plugin-v0.4.13 = C`;
  retained tags `0.4.10/11/12` read back unchanged.
- Real reinstall on the owner's workstation through the raw marketplace descriptor: CLI reports
  version `0.4.13`; the shipped L4 verifier returned `VERIFIED` with reachable refs
  `main`, `origin/HEAD` (normal-clone symbolic head, admitted per ticket 10), `origin/main`,
  `plugin-v0.4.13`, and **exactly one reachable commit, `C`** — no development history in the
  installed cache. Stale version directories from earlier installs remain in the CLI cache as
  inert leftovers; the active version is `0.4.13`.
- PAI-06 evidence: [`06-live-provider-qualification-evidence.md`](../../../doc/reviews/project-authority-integration/06-live-provider-qualification-evidence.md).

## Vertical closure reserved

When an owner authorizes a release, align the named governance source files with the approved
bridge and authority-line decisions, regenerate the exact Level 1 payload, assign a new version,
create an immutable tag, install or reload the named target, and verify the actual CLI-visible
payload/version. The later exact ticket must bind source paths, generator revision, payload tree,
release target, version, tag, installation target, pre/post baselines, correlation, readback and
rollback/forward-fix evidence.

This is a future verification contract, not a current PAI-08 predecessor and not a release grant.
It creates no payload change, version, tag, CLI command, provider use, publication, deployment,
receipt, descriptor, runner, or dispatch. PAI-08 may record only its deferred state; it may not
claim that the installed plugin already conveys this governance update.
