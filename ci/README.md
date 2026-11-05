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

<!-- HOST_VS_RUNNER -->
