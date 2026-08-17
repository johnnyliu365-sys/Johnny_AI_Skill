# 02 — Runtime dependency lock

| Field | Binding |
| --- | --- |
| SPEC / AC / Context | Plugin Distribution Revision 02 / AC-03, AC-04, AC-05 / `ctx-plugin-distribution-r02` |
| Requirement / planning baseline | `REQ-20260802-004` / `a45686dd0238d69fac6c0b740a2b91ba51d5d90a` |
| Control / reviewer | Senior `01a00e7d-7ef4-7ac1-96ce-e6c2b7592f5b` |
| Implementation allocation | role `role-impl-pd02-luna-001`; task `01a00eac-b464-7ee1-ac76-465477768e02`; worktree `worktree-pd02impl2-01` at `C:\Users\<user>\Desktop\AI控制工作workflow-implementer-2`; branch `codex/plugin-distribution-02-runtime-lock` / `branch-pd02runtime-01`; baseline `496971ccfaa9db25bde3d69c526166b82b9c4ca4`; receipt `receipt-pd02-20260817-002`; dispatch `dispatch-pd02-20260817-002` |
| Profile / environment | `plugin-distribution-poc-r02` v2; Luna xhigh; Windows x64; CPython 3.11.9; no helper |
| State / XSS | `READY_LOW_MODEL / RECEIPT_BOUND / DISPATCH_PENDING`; `XSS_NOT_APPLICABLE` |

## Sole closure and public boundary

`requirements-runtime.lock` round-trips through strict `LockedArtifact`,
`RuntimeDependency` and `RuntimeDependencyLock` values and rejects any unknown, duplicate,
unhashed or environment-mismatched entry before dependency installation. The six approved wheels
are exactly: `pydantic-2.13.4` SHA-256 `45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba`;
`pydantic_core-2.46.4-cp311-win_amd64` `6f2eeda33a839975441c86a4119e1383c50b47faf0cbb5176985565c6bb02c33`;
`pywin32-311-cp311-win_amd64` `3ce80b34b22b17ccbd937a6e78e7225d80c52f5ab9940fe0506a1a16f3dab503`;
`annotated_types-0.8.0` `f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0`;
`typing_extensions-4.15.0` `f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548`;
`typing_inspection-0.4.2` `4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7`.

Writable scope: `library/local_orchestration/runtime_dependency_lock.py`,
`requirements-runtime.lock`, `tests/test_plugin_distribution_dependency_lock.py`. No process,
network, pip install, host, Git or target effect. Dependencies: none.

## TDD, verification and return

Closure `CLOSURE-PD-02-R03-01`: L1 ordinary parse/serialize; L2 exact six-entry identity; L3
unknown/duplicate/hash/platform rejection; L4 canonical digest stability. First red:
`python -m pytest -q tests/test_plugin_distribution_dependency_lock.py -k test_runtime_lock_rejects_unhashed_wheel_before_install`.
Verify with `python -m pytest -q tests/test_plugin_distribution_dependency_lock.py`,
`python -m mypy --strict library/local_orchestration/runtime_dependency_lock.py` and
`python -m pytest -q`; reverse-mutate the hash gate once and restore bytes. `ImplementationReturn.COMPLETED`
returns commit, cell results, output digests and zero residue; `CHANGE_DETECTED` returns upstream.
