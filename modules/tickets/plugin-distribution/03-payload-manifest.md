# 03 — Payload manifest and import isolation

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-02, AC-03, AC-04 / `ctx-plugin-distribution-r02` |
| Requirement / baseline / dependency | `REQ-20260802-004` / planning `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` / 02 |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required before ready |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

One strict `PayloadManifest` describes the complete allowlist with unique ordinal-sorted
`PayloadManifestEntry` paths and hashes; excluded trees, path escape, manifest self-entry and
optional integrations are rejected before archive creation. An extracted fixture built from that
manifest imports Router core and reads both skills and module catalog without the development
checkout or optional packages. The dependency lock is read-only input.

Writable scope: `library/local_orchestration/windows_package_manifest.py` and
`tests/test_plugin_distribution_payload_manifest.py`. No archive, process, host or target effect.

## TDD, verification and return

Closure `CLOSURE-PD-03-R03-01`: M1 ordinary manifest round-trip; M2 complete allowlist; M3
duplicate/excluded/escape/self-entry rejection; M4 isolated core import/read. First red:
`python -m pytest -q tests/test_plugin_distribution_payload_manifest.py -k test_payload_manifest_rejects_excluded_target_tree`.
Verify with `python -m pytest -q tests/test_plugin_distribution_payload_manifest.py`,
`python -m mypy --strict library/local_orchestration/windows_package_manifest.py` and
`python -m pytest -q`; reverse-mutate the path admission guard. Return typed completion with
commit, cell/digest/cleanup evidence; changes to the allowlist return `CHANGE_DETECTED`.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
