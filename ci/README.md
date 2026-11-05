# CI: the whole suite on Linux and Windows

`.github/workflows/ci.yml` runs on every push and pull request, one job per operating system
(`ubuntu-latest`, `windows-latest`), Python 3.11, full history checkout, `PYTHONUTF8=1`, a neutral git
identity for tests that commit, token permission `contents: read`, no secret. Third-party actions are pinned to
a full commit sha with the version in a comment.

A job runs `python -m pytest tests -q -p no:cacheprovider -rf --junitxml=<file>` and then
`python ci/check_registered_failures.py --os <linux|windows> --junit <file>`. The checker's exit is the job's
result; the pytest exit is not.

## The list: `registered-failures.json`

`{"linux": [row, ...], "windows": [row, ...]}`; a row is `{"test": <pytest node id>, "reason": <why it fails in
this environment>, "follow_up": <ticket path or "environment">}`. A reason names the cause. It is never
"flaky". A test is registered for an operating system only after the CI log of that operating system shows it
failing, and it is removed when it passes.

## The checker: `check_registered_failures.py`

| Exit | Meaning |
| --- | --- |
| 0 | the failed and errored test ids of the report equal the registered set for `--os` |
| 1 | a mismatch, one line per subject: `UNREGISTERED_FAILURE <id>`, `REGISTERED_NOW_PASSING <id>`, `REGISTERED_NOT_FAILING <id>` |
| 2 | the report or the list cannot be read or breaks its schema (one `INPUT_ERROR` line on stderr) |
| 3 | bad arguments |

Choices where the ticket is silent, all fail-closed:

- A registered test that was skipped, or does not appear in the report, is `REGISTERED_NOT_FAILING` (exit 1),
  so a stale row cannot hide behind a skip. Skipped tests that are not registered are ignored.
- Both operating system keys must be present in the list; an extra key, an extra field in a row, a non-string
  or blank field and a repeated test id on one operating system are exit 2.
- A report that declares a DOCTYPE or an entity is exit 2.
- Ids are compared as whole strings. The id is rebuilt from the junit `classname` (module path up to the first
  `test_*` part, then the class chain) and `name`; a collection error (empty classname) is the module file.

## Host versus runner

The "host" is the maintainer's Windows 11 workstation, where a full run fails on a fixed set of tests. The
differences between the host and each runner, with their causes, are listed below once the CI runs have shown
them.

### Registered counts

Windows runner 47 rows, Linux runner 234 rows (read from CI runs 42009508339 and 42011080430; the Windows set was identical in both runs).

### Host failures that do not fail on a runner

- `tests/test_atomic_conditional_replace_capability.py::test_acr6_committed_candidate_diff_and_forbidden_paths`: on the host the disposable Git fixture cannot be set up (`RuntimeError: disposable Git fixture setup failed`); on the runners it passes.
- `tests/test_plugin_publication.py::PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected`: fails on the host only; passes on both runners.
- `tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services` and `...::test_temporal_approval_signal_requires_matching_authority_state`: on the host Windows application control blocks `temporal_sdk_bridge` (`DLL load failed ... blocked`); the runners load it.

### Windows runner failures that do not fail on the host

The 39 rows of `test_dispatch_authority`, `test_dispatch_session`, `test_parallel_worker_dispatch`, `test_review_return` and `test_plugin_distribution_bundle`: the runner's temp directory is the 8.3 short path `C:/Users/RUNNER~1/...`, which makes the worktree containment check refuse the worktree; the host's temp path has no short name. `test_acr2_linux_requires_an_actual_linux_kernel_and_backend` fails on the host and on the Windows runner for different causes (the host has WSL but the proof fails there; the runner has none).

### Linux runner

Every failure on the Linux runner is a Windows-only facility the test needs (`st_file_attributes`, `cmd.exe`, `powershell.exe`, `%LOCALAPPDATA%`, batch-file shims, Windows path forms, the pywin32 binding), or one of the operating-system independent failures that also fail on the host (pinned commit not in the clone, `test_acr6_exact_test_only_boundary`, the router audit step, the refusal-guidance roster). `tests/test_codex_registration_contracts.py` is a collection error; the workflow passes `--continue-on-collection-errors` so that it does not stop the rest of the suite.

The reason of each row names its own cause. Rows whose follow-up is this ticket's path are failures that are not environment capabilities; they need a follow-up ticket from the control plane, which this ticket may not create.
