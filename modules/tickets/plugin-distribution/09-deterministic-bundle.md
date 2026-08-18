# 09 — Deterministic plugin bundle

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-01, AC-02, AC-03 / `ctx-plugin-distribution-r02` |
| Dependency / source baseline | Ticket 03 integration `764b70ec0a87ea1818c1c8a1abcdaa4475a22af2` / closure `7a0d276` / current `main` `574e6e8b473dfc598d5c72506e253a1babc2c256` |
| Control / reviewer | Current architecture owner and reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior has no authority |
| Implementation allocation | ticket `ticket-pd09-deterministic-bundle-01`; role `role-impl-pd09-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01`; branch `codex/plugin-distribution-09-deterministic-bundle` / `branch-pd09bundle-01`; receipt `receipt-pd09-20260818-001`; correlation `corr-pd09-20260818-001` |
| Dispatch mode | User-authorized one-time manual bootstrap forwarding while live Router dispatch remains unavailable; no live descriptor, host subscription, heartbeat, polling, automation, publication, installation or target-project effect |
| Implementation language / strict checker | Python 3.11.9 / `python -B -m mypy --strict library/local_orchestration/plugin_bundle_builder.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `INTEGRATED / CLOSED`; implementation `1000ebae1151b7a83fe81b7db884ac6162ec87d4`; correction `daea4146e2dfd3526632c6118197003fa20603c7` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

Create `library/local_orchestration/plugin_bundle_builder.py` and its one direct test module.
It consumes the existing read-only `PayloadManifest`, `PayloadManifestEntry`,
`build_payload_manifest`, `RuntimeDependencyLock` and `load_runtime_dependency_lock` contracts;
those five dependency symbols and `requirements-runtime.lock` are read-only. It may use only
read-only local Git invocations (`rev-parse HEAD` and `status --porcelain=v1 --untracked-files=all`)
to prove the source identity and cleanliness. It must not configure, stage, commit, reset, fetch,
push, tag, modify or delete Git state.

The public strong types are frozen strict Pydantic values (`extra="forbid"`,
`revalidate_instances="always"`; no `Any`, raw exception text, source bytes, paths or handles in
results):

```text
PluginBundleBuildRequest = {
  repository_root: Path,
  output_root: Path,
  manifest: PayloadManifest
}
PluginBundleBuildStatus = BUNDLED | BLOCKED
PluginBundleBuildFailure = REQUEST_INVALID | GIT_READBACK_UNAVAILABLE | SOURCE_DIRTY |
                           SOURCE_IDENTITY_MISMATCH | MANIFEST_MISMATCH |
                           ENTRY_UNAVAILABLE | ENTRY_CONTENT_MISMATCH | OUTPUT_UNAVAILABLE
PluginBundleBuildResult = {
  status: PluginBundleBuildStatus,
  source_commit: str | null,
  manifest_digest: str | null,
  archive_sha256: str | null,
  archive_byte_length: int | null,
  failure: PluginBundleBuildFailure | null
}
PluginBundleBuilder = {
  build(PluginBundleBuildRequest) -> PluginBundleBuildResult
}
```

`BUNDLED` has the exact manifest `source_commit`, canonical manifest digest, lowercase archive
SHA-256 and positive byte length, with no failure. `BLOCKED` has exactly one failure and no
success fields. Invalid exact types or roots return `REQUEST_INVALID`; an unavailable or malformed
Git readback returns `GIT_READBACK_UNAVAILABLE`; a non-empty porcelain result returns
`SOURCE_DIRTY`; a HEAD unequal to `manifest.source_commit` returns `SOURCE_IDENTITY_MISMATCH`.
Only after those gates may the builder load the committed lock, rebuild the manifest and require
exact equality with the request manifest. A differing rebuilt manifest is `MANIFEST_MISMATCH`;
missing/unreadable/symlink entry is `ENTRY_UNAVAILABLE`; byte length or digest mismatch is
`ENTRY_CONTENT_MISMATCH`. Every block occurs before a candidate archive exists.

`output_root` must resolve to an existing directory outside `repository_root`; its fixed candidate
is `johnny-ai-skill-0.4.0.zip` and it must not already exist. Write only through a same-directory
temporary file, then atomically publish that one candidate on success; remove a temporary file on
all failure paths. The candidate contains every manifest entry exactly once, ordinal by its
forward-slash path, followed only by `payload-manifest.json` containing
`manifest.canonical_json().encode("utf-8")`. It has no directory entries, extra fields or archive
comment. Each entry uses timestamp `1980-01-01T00:00:00`, `create_system=3`, regular mode `0644`,
UTF-8 name encoding, `ZIP_DEFLATED` level `9`; file data is the verified entry bytes. The generated
manifest is intentionally not a manifest entry. No source tree, candidate path, Router state,
network, host, process other than the declared read-only Git readback, provider, installation,
publication or target-project effect belongs here.

Writable scope: `library/local_orchestration/plugin_bundle_builder.py` and
`tests/test_plugin_distribution_bundle.py` only. Candidate ZIPs, fixture repositories and
extraction roots exist only under test-owned temporary directories and are removed before return.

## TDD, verification and return

Closure `CLOSURE-PD-09-R04-01`:

- B1: two clean copies at the same committed source identity and identical manifest produce
  byte-identical candidates and equal SHA-256 values.
- B2: a changed allowlisted file committed as a distinct clean source identity produces a new
  manifest and a different archive SHA-256.
- B3: ZIP inspection proves exact entry order, manifest-last rule, no directory/extra/comment,
  fixed timestamp/system/mode, UTF-8 names and deflate level-compatible metadata.
- B4: dirty source, wrong HEAD, changed/rebuilt manifest, pre-existing output, invalid output root,
  missing or changed entry, duplicate/excluded manifest identity and source symlink each block
  before candidate publication with their finite result; malformed duplicate/excluded identities
  reject through `PayloadManifest` before `build` is called.
- B5: an extracted candidate in an isolated child Python process loads both shipped skills,
  `library.workflow_router` and `library/MODULE_CATALOG.md` without the development checkout;
  its temporary extraction and every candidate/cache/bytecode artifact are removed.

First red is exactly:

```text
python -B -m pytest -q -p no:cacheprovider tests/test_plugin_distribution_bundle.py -k test_same_commit_and_toolchain_emit_identical_zip_bytes
```

Run the focused closure, the named strict checker, the direct Ticket 03 regression
`tests/test_plugin_distribution_payload_manifest.py`, and in-memory compilation of the new
source/test files. Reverse-mutate the manifest-last ZIP write so the named B3 cell turns red,
restore exact bytes, rerun the focused cell and remove every temporary/archive/cache/bytecode
residue before one implementation commit. Return exactly `ImplementationReturn.COMPLETED →
ACTION_COMPLETED`, `BLOCKED → HALT` with its failed closure cell and preserved branch state, or
`CHANGE_DETECTED → REQUIREMENT_CHANGED` only for a conflict in the frozen lock/manifest contract.
