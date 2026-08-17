# 03 — Payload manifest and import isolation

| Field | Binding |
| --- | --- |
| SPEC / AC / requirement | `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H` Revision 02 / AC-02, AC-03, AC-04 / `PRD-20260802-004` / `CHG-20260802-004` / `REQ-20260802-004` |
| Context / planning baseline | `doc/context/plugin-distribution/main.md` / `ctx-plugin-distribution-r02` / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Closure / dependency | `CLOSURE-PD-03-R03-03`; replaces R03-02 because its two-file scope could not make the existing Router package import-safe without optional `langgraph`; Ticket 02 integrated at `b5e73655eae8f6995cab803e1be276ced492dcff`; implementation baseline `33b04c7e4f322dae9ebc674ed7f263cdcded78d5` |
| Control / reviewer | Architecture owner and replacement reviewer task `019fbda1-2365-77d2-b510-dff079d02bff`; prior Senior task is retired from this ticket |
| Implementation allocation | ticket ref `ticket-pd03-payload-manifest-02`; role `role-impl-pd03-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pluginimpl2-01` at `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; branch `codex/plugin-distribution-03-payload-manifest` / `branch-pd03manifest-01`; receipt `receipt-pd03-20260817-002`; correlation `corr-pd03-20260817-002`; correction `correction-pd03-20260817-003` |
| Implementation language / strict checker | Python 3.11.9 / `python -m mypy --strict library/local_orchestration/windows_package_manifest.py library/workflow_router/__init__.py` |
| Profile / state / XSS | `plugin-distribution-poc-r02` v2 / POC / Luna xhigh / one implementation lane / no helper / `TICKET_CORRECTED / CORRECTION_AUTHORIZED` / `XSS_NOT_APPLICABLE` |
| Boundary classification | Read-only repository input and task-owned temporary extraction only; no archive publication, process, network, host, Secret, Provider or target-project effect |

## Sole closure and boundary

Implement the SPEC's public `PayloadManifestEntry = { archive_relative_path, sha256,
byte_length }` and `PayloadManifest = { schema_version = 1, plugin_id, plugin_version,
source_commit, dependency_lock_digest, entries }` as frozen strict Pydantic values. Entries are
non-empty, unique and ordinal-sorted canonical `/`-separated archive-relative paths; absolute,
drive, UNC, `.`/`..`, backslash, duplicate, excluded and `payload-manifest.json` self-entry paths
fail before any output. SHA-256 is lowercase 64-hex and byte length is non-negative.

`build_payload_manifest(repository_root, source_commit, dependency_lock)` reads only the clean
source tree and returns the typed value. It loads the committed `requirements-runtime.lock`
through the Ticket 02 public loader and rejects inequality with the supplied typed lock. The
allowlist is exactly `.codex-plugin/plugin.json`,
`skills/**`, `library/**`, `AGENTS.md`, `Workflow.md`, `CodeReview.md`, `README.md`, `install.ps1`,
`johnny-router.ps1` and `requirements-runtime.lock`; missing required roots fail closed. Exclude
Git/worktree metadata, `doc/`, `modules/`, `tests/`, Claude metadata, build/staging/review evidence,
caches, bytecode, coverage, telemetry, receipts, queues, `.env`, Secrets and target content. The
manifest canonical UTF-8 JSON digest excludes the manifest itself.

Ticket 03 admits `install.ps1` and `johnny-router.ps1` when present but does not require them at
this baseline because Tickets 10–11 create those later-stage artifacts. Their absence becomes a
hard failure in the final deterministic-bundle/qualification closure.

Windows exclusion comparisons are case-insensitive and path-component exact: excluded `tests`,
`.env`, `secret` and `secrets` variants fail, while prefix-similar `tests2`, `.env2` and `secret2`
remain ordinary allowlisted names. Empty, whitespace, absolute, drive, UNC, backslash, `.`/`..`,
colon/ADS and percent-encoded archive identities fail before file reads.

An extracted task-owned disposable fixture built from the returned entries must import Router
core and read both shipped skills plus `library/MODULE_CATALOG.md` without the development
checkout or optional integration packages. The test actively blocks `langgraph`, `temporalio`,
`mcp` and `openai`; retaining installed site-packages is not absence evidence.
`library.workflow_router` stops eagerly importing `.graph`. Its existing `build_router_graph`
public export remains available through a typed lazy module attribute and imports `.graph` only
when that optional capability is requested. All other exports and `__all__` identities remain
unchanged. The fixture and every cache/bytecode artifact are removed before return. The dependency
lock is read-only input.

Writable scope: `library/local_orchestration/windows_package_manifest.py`,
`library/workflow_router/__init__.py` and `tests/test_plugin_distribution_payload_manifest.py`.
No archive, process, host or target effect.

## TDD, verification and return

Closure `CLOSURE-PD-03-R03-03`: M1 ordinary manifest round-trip; M2 complete allowlist and exact
committed-lock equality; M3 duplicate/excluded/escape/self-entry plus the complete Windows path
matrix above; M4 optional-package-blocked isolated core import/read with lazy graph access. First red:
`python -m pytest -q tests/test_plugin_distribution_payload_manifest.py -k test_payload_manifest_rejects_excluded_target_tree`.
Verify with `python -m pytest -q tests/test_plugin_distribution_payload_manifest.py`,
`python -m mypy --strict library/local_orchestration/windows_package_manifest.py library/workflow_router/__init__.py` and
`python -m pytest -q`; reverse-mutate the path admission guard. Return typed completion with
commit, M1–M4 results, verification-output digests and clean tracked/ignored porcelain.

`ImplementationReturn` is exactly: `COMPLETED → ACTION_COMPLETED`; `BLOCKED → HALT` with the exact
failed capability or verification cell and preserved branch/commit state; `CHANGE_DETECTED →
REQUIREMENT_CHANGED` with the conflicting frozen contract reference. No return authorizes archive
publication, installation, Router binding or target effect. Rollback before integration is branch
non-selection; after integration it is an additive forward-fix.
