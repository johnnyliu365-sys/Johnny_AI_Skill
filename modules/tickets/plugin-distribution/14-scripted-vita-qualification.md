# 14 — Scripted SourceProjectA package qualification

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-06, AC-10–AC-15 / `ctx-plugin-distribution-r02` |
| Dependencies / planning baseline | 08, 12, 13 / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b`; live implementation binding required |
| Profile / state / XSS | Luna xhigh, no model/helper during matrix / `PLANNED / LOW_MODEL_CANDIDATE / ALLOCATION_REQUIRED` / `XSS_NOT_APPLICABLE` |

## Sole closure and boundary

One deterministic qualification report installs the candidate only into a Johnny-owned disposable
copy and runs two bounded matrices: target preservation/install/uninstall, then Router transitions,
invalid handoffs, roles, FIFO and dependency clusters. The original
`D:\SourceProjectA\SourceProjectA\private-target-repo` is read-only pre/post evidence. Missing host wake remains
non-binding. All disposable copies, runtime, cache and generated evidence are deleted afterward.

Writable scope: `tests/test_plugin_distribution_vita_qualification.py` and
`tests/staging/plugin_distribution_vita/`. No original Vita or production effect.

## TDD, verification and return

Closure `CLOSURE-PD-14-R03-01`: V1 package-only install; V2 original identity preserved; V3 valid
matrix; V4 invalid bindings rejected; V5 FIFO/cluster; V6 uninstall and zero residue. First red:
`python -m pytest -q tests/test_plugin_distribution_vita_qualification.py -k test_qualification_preserves_original_vita_head_and_status`.
Verify with `python -m pytest -q tests/test_plugin_distribution_vita_qualification.py`,
`python -m mypy --strict tests/test_plugin_distribution_vita_qualification.py` and
`python -m pytest -q`, then prove staging/residue absence. Return typed evidence;
manual forwarding cannot satisfy host-wake or Router-binding cells.
Return is exactly `ImplementationReturn.COMPLETED | BLOCKED | CHANGE_DETECTED`.

## Integrated evidence

| Field | Evidence |
| --- | --- |
| State | `INTEGRATED / CLOSED` |
| Implementation | `feat: add scripted SourceProjectA package qualification` on `claude/skill-plugin-parallel-control-42c487`; owner-authorized direct allocation |
| Original resolution | `D:\SourceProjectA\SourceProjectA\private-target-repo` does not exist on this host; the harness resolves the same original repository at `C:\Users\User\Desktop\SourceProjectA\private-target-repo` (its own Git repository, HEAD `8aee42f6`), with `JOHNNY_VITA_ORIGINAL` as explicit override. Hosts without the original skip as `VITA_ORIGINAL_UNAVAILABLE` instead of faking a result. |
| Closure | V1 candidate bundle `BUNDLED` and extracted only manifest-listed paths plus `payload-manifest.json` into the Johnny-owned disposable root; the disposable target copy stayed digest-identical and carried no johnny path. V2 the original repository's HEAD and porcelain-status digest are identical before and after the whole pipeline; only read-only Git queries touched it. V3 composition `COMPOSED`, valid subscription `REGISTERED`, review wake flow `HOST_ACCEPTED` then `QUEUED_NO_WAKE`. V4 foreign project binding `REJECTED / INVALID_BINDING`; unavailable host wake preflight `REJECTED / HOST_WAKE_CAPABILITY_UNAVAILABLE` (non-binding). V5 claimed batch clusters `(cluster-a, cluster-b)` in exact FIFO admission order. V6 receipt-owned uninstall `REMOVED`, repeat `NOT_INSTALLED`, only the seeded foreign entry remained, target digest unchanged, and the whole disposable workspace was deleted with read-only Git objects cleared. |
| Verification | qualification `6 passed`; `mypy --strict --no-incremental --explicit-package-bases` clean over both new files (the sole transitive finding is a pre-existing `redundant-cast` in frozen `test_plugin_distribution_git_subscription.py:229`, untouched by this ticket); full `795 passed, 2594 subtests`; 222 Python files compiled in memory; `johnny-vita-qual-*` residue count zero after runs (five stale trees from pre-fix iterations were deleted with the same harness cleaner). |
| Boundary | No original-Vita write, no production effect, no model call during the matrix, no heartbeat/polling; all writes confined to one `tempfile.mkdtemp` workspace deleted in the same run. |

Canonical SHA-256: `test_plugin_distribution_vita_qualification.py`
`647751917673BE89E5B3348DED0634DC31C8DC4C1CE422B409D5ADBFDBC4AB77`;
`harness.py` `B3118A4E342F09DA433754834C59FD036F50FC06D91AD8D7D0FF08FC08199E83`;
`__init__.py` `DCEE6A774B40047BBB5297DC86D01265CD1138FB6239356A4EF23960E65D1054`.
