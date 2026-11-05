# CI: the whole suite on Linux and Windows

`.github/workflows/ci.yml` runs on every push and pull request, one job per operating system
(`ubuntu-latest`, `windows-latest`), Python 3.11, full history checkout, `PYTHONUTF8=1`, a neutral git
identity for tests that commit, token permission `contents: read`, no secret. Third-party actions are pinned to
a full commit sha with the version in a comment.

A job runs `python -m pytest tests -q -p no:cacheprovider -rf --junitxml=<file> --continue-on-collection-errors` and then
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

Windows runner 44 rows, Linux runner 228 rows (ticket 62 removed 3 and 6 rows that its fixes turned green; the earlier counts, 47 and 234, were read from CI runs 42009508339 and 42011080430).

### Host failures that do not fail on a runner

These four failed in the base capture (`C:/Temp/claude/jas48_F1_base.txt`, a full run in the clone `C:/Temp/claude/jas48_base`). None of them failed on the host at the candidate, in either locked full run, so they belong to that base capture and not to the current host. They pass on both runners.

- `tests/test_atomic_conditional_replace_capability.py::test_acr6_committed_candidate_diff_and_forbidden_paths`: in the base clone `git checkout --detach 6953f1e49bc60e66a5f8a2ce9cfd879f0d606ece` (the ticket authority baseline) failed, so the disposable Git fixture could not be set up (`RuntimeError: disposable Git fixture setup failed`); the runners clone with full history and the baseline exists there.
- `tests/test_plugin_publication.py::PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected`: in the base clone `require_existing_commit` raised `PinnedCommitError: the pinned sha names no commit in this repository` for the root commit `fcb4604572e7a325b970c19303829c42226802ed`, which that clone does not hold; the runners fetch full history (`fetch-depth: 0`) and hold it.
- `tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services` and `...::test_temporal_approval_signal_requires_matching_authority_state`: in the base capture Windows application control blocked `temporal_sdk_bridge` (`DLL load failed ... blocked`); the runners load it.

### Windows runner failures that do not fail on the host

The 39 rows of `test_dispatch_authority`, `test_dispatch_session`, `test_parallel_worker_dispatch`, `test_review_return` and `test_plugin_distribution_bundle`: the runner's temp directory is the 8.3 short path `C:/Users/RUNNER~1/...`. `path_containment.resolves_within_root` returns `False` whenever `base.resolve() != base`, so it treats the short-name alias of the repository root as a redirect and the worktree is refused. That is a product defect on a supported platform, not a capability the runner lacks; the host's temp path has no short name. Follow-up: `modules/tickets/workflow-governance/63-short-name-containment.md`. `test_acr2_linux_requires_an_actual_linux_kernel_and_backend` fails on the Windows runner because it has no WSL Linux backend (`_PlatformProofUnavailable: LINUX`); on the host the WSL proof does not run either.

### Line endings (checkout configuration)

The maintainer's checkout has repo-local `core.autocrlf=false`. The Windows runner has none repo-local and runs under the system default `core.autocrlf=true` (`file:C:/Program Files/Git/etc/gitconfig true`, printed by the workflow's identity step), so LF blobs become CRLF working files there; the Linux runner has the setting unset and keeps LF. No registered failure is a line-ending failure: on the Windows runner the byte-checking tests pass under `autocrlf=true`, and the workflow does not change the setting, so that difference stays visible instead of being tuned away.

### Linux runner

Most Linux failures are a Windows-only facility the test needs (`st_file_attributes`, `cmd.exe`, `powershell.exe`, `%LOCALAPPDATA%`, batch-file shims, Windows path forms, the pywin32 binding). Not every row is an environment failure:

- Three Linux rows were defects in their tests, not missing capabilities, and ticket 62 fixed them: `test_acr2_linux_requires_an_actual_linux_kernel_and_backend` and `test_acr3_acm1_current_python_abstraction_final_window_qualifies_no` (the test's label validator refused the runner's `linux-fs:ext2/ext3` because of the `/`; the label now spells it `ext2-ext3`), and `tests/test_file_lock.py::BlockingAcquisitionTests::test_a_waiter_is_held_out_and_then_let_in_rather_than_refused` (the test closed the waiter's stdin and then called `communicate()`, which raised `ValueError: I/O operation on closed file` on POSIX; stdin is no longer closed first). Their rows are gone.
- Four rows per operating system stay registered with ticket 62 as their follow-up: the marketplace pin `0b3afd3645946f97662c336f0e6ac0dcae502e69` (one payload-boundary test and three publication tests). The pinned commit is the generated publication commit of the separate publication repository, so this repository holds no such object; the pin is also stale against the declared payload. Re-pinning is the owner's publication step. The other three OS-independent rows that ticket 62 inherited (`test_acr6_exact_test_only_boundary`, the router audit step, the refusal-guidance roster) are fixed in their tests and their rows are gone.

Those four Linux rows, and the four on Windows, carry `modules/tickets/workflow-governance/62-registered-known-failures.md` as their follow-up. `tests/test_codex_registration_contracts.py` is a collection error; the workflow passes `--continue-on-collection-errors` so that it does not stop the rest of the suite.

The reason of each row names its own cause. A row whose follow-up is a ticket path is a failure that is not an environment capability; the ticket named there owns it.
