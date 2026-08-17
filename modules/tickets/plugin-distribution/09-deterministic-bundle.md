# 09 — Deterministic plugin bundle

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-01, AC-02, AC-03 / `ctx-plugin-distribution-r02` |
| Dependency / planning baseline | 03 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no helper / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

`PluginBundleBuilder` consumes the read-only lock/manifest and one clean source commit, then emits
byte-identical ZIP bytes and SHA-256 for identical inputs. Constants are frozen: forward-slash
ordinal paths; no directory entries; timestamp `1980-01-01T00:00:00`; `create_system=3`; regular
file mode `0644`; UTF-8 names; `ZIP_DEFLATED` level 9; empty extra/comment; manifest last. Any
dirty source, excluded path, duplicate or changed source identity blocks before output publish.

Writable scope: `library/local_orchestration/plugin_bundle_builder.py` and
`tests/test_plugin_distribution_bundle.py`; candidate ZIPs exist only in temporary Johnny output.

## TDD, verification and return

Closure `CLOSURE-PD-09-R03-01`: B1 identical bytes; B2 changed input changes digest; B3 canonical
metadata; B4 dirty/excluded/duplicate block; B5 isolated extracted import. First red:
`python -m pytest -q tests/test_plugin_distribution_bundle.py -k test_same_commit_and_toolchain_emit_identical_zip_bytes`.
Verify with `python -m pytest -q tests/test_plugin_distribution_bundle.py`,
`python -m mypy --strict library/local_orchestration/plugin_bundle_builder.py` and
`python -m pytest -q`; reverse-mutate one ZIP constant. Delete all candidate fixtures; return typed
commit/cell/digest/cleanup evidence.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.
