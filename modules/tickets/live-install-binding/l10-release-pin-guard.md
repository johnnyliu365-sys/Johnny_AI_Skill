# L10 — Release Pin Guard

| Field | Value |
| --- | --- |
| Requirement | Control-plane finding 2026-08-19 (recorded when L9 closed): the wrapper's approved digest is a hand-written literal that nothing derives or checks against a build |
| State | `CLOSED` |
| Baseline | `main` = `f5737aa` |
| Workload | `SMALL`; no baseline-red (not a bugfix) |
| Language / XSS | Python 3.11 strict Pydantic/mypy + Windows cmd batch / `XSS_NOT_APPLICABLE` |

## The defect being closed

`johnny-install.cmd` pins two literals: the bundle file name
`johnny-ai-skill-0.4.1.zip` and the approved digest
`f67047f4…`. The same version appears in `.codex-plugin/plugin.json` and in
`plugin_bundle_builder._CANDIDATE_NAME`. Nothing ties the three together and
nothing compares the digest against a built artifact.

The failure is silent and reaches the user: a release bumps the version,
the wrapper keeps the previous name and digest, and every owner who
double-clicks it gets `DIGEST_MISMATCH` (or `BUNDLE_NOT_FOUND`) against a
correctly built bundle. The wrapper is the one component whose whole job is
to be right about the approved artifact.

## Frozen responsibility

- The version is declared in exactly one place, `.codex-plugin/plugin.json`.
  The bundle builder's candidate name and the wrapper's bundle name must agree
  with it, proven by test rather than by discipline.
- The digest cannot be derived statically (the bundle is a build output that
  cannot live in the repository), so it is checked functionally: a release
  preflight recomputes the digest of a given bundle and compares it to the
  wrapper's pin.
- The preflight reads the wrapper as data. It never rewrites the pin
  automatically: a wrapper that edits itself to match whatever bundle it is
  shown would defeat the approval it exists to enforce.
- Finite typed outcomes only; no exception escapes to the caller.

## Authorized implementation scope

```text
library/local_orchestration/release_pin_guard.py
tests/test_release_pin_guard.py
modules/tickets/live-install-binding/README.md
modules/tickets/live-install-binding/l10-release-pin-guard.md
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `L10-R1` | The wrapper's bundle name, `plugin_bundle_builder._CANDIDATE_NAME` and `.codex-plugin/plugin.json` version agree; a mutation to any one of the three turns the cell red. |
| `L10-R2` | The preflight extracts the wrapper's pinned name and digest by parsing the file, and refuses a malformed or unreadable wrapper with a typed failure. |
| `L10-R3` | Given a bundle whose digest matches the pin, the preflight returns `MATCHED`; given any other bundle, `DIGEST_MISMATCH`; given a bundle whose file name differs from the pinned name, `BUNDLE_NAME_MISMATCH`. |
| `L10-R4` | Run against the real released artifact, the preflight returns `MATCHED` for the current wrapper and the shipped `johnny-ai-skill-0.4.1.zip`. |
| `L10-R5` | `mypy --strict` clean; full suite green; `tests/.johnny-runtime` zero residue. |

## Closure evidence (2026-08-19)

- `L10-R1` The wrapper's bundle name, `_CANDIDATE_NAME` and the manifest
  version all agree. Reverse mutation: bumping the manifest to `0.4.2` without
  touching the wrapper or the builder turns this cell red, which is exactly the
  silent release defect the ticket names.
- `L10-R2` The real wrapper yields both literals; an absent wrapper and a
  wrapper without pins are refused with distinct typed failures.
- `L10-R3` Matching bundle -> `MATCHED`. Rebuilt content under the same name ->
  `DIGEST_MISMATCH`. Version bumped with the wrapper left behind ->
  `BUNDLE_NAME_MISMATCH`. Unreadable bundle -> `BUNDLE_UNREADABLE`.
- `L10-R4` Gated run against the shipped `johnny-ai-skill-0.4.1.zip` returns
  `MATCHED`.
- `L10-R5` `mypy --strict` clean; full suite green; zero runtime residue.

## Release procedure this adds

Before publishing a release asset, run the preflight against the built bundle
and require `MATCHED`. A refusal means the wrapper and the bundle disagree and
shipping them together would hand the owner a refusal on a correct artifact.
The preflight never rewrites the pin: updating it stays a deliberate act.
