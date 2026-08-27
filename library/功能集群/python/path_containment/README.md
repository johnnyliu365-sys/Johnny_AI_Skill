# Path Containment（Python）

| Field | Value |
| --- | --- |
| Module ID | `path-containment` |
| Lifecycle | `READY` |
| Public import | `library.local_orchestration.path_containment: resolves_within_root` |
| Contract source | `library/local_orchestration/path_containment.py` |
| Behavior evidence | `tests/test_worktree_containment.py` — contained path, sibling escape, redirected child and redirected base cases |
| Dependencies | Standard library only; no reusable-module dependency |

## Public capability

`resolves_within_root(target, base)` is the one local containment predicate for a caller that
already owns both `Path` values. It rejects an absent/unresolvable path, a base that resolves to
a different location, and an existing ancestor that redirects outside the resolved base. It
accepts only a target that resolves within the exact base. It returns a Boolean; it does not
create, delete, open, lock, serialize, log, or disclose a path.

## Minimum reading path

1. This card.
2. `library/local_orchestration/path_containment.py`.
3. `tests/test_worktree_containment.py` when containment or redirected-path behavior matters.

## Required use and prohibited use

- Use it before a local adapter creates or opens a derived owned path whose existing ancestors
  could redirect elsewhere. Callers retain their own effect, error and authorization policy.
- Pass only internally derived `Path` values. No Router, telemetry, request, response, error,
  log, provider or target boundary may expose either path.
- It is a predicate, not a path allocator, a sandbox, a lock, an authorization grant, a
  filesystem effect, or a substitute for exact identity admission.
- A `False` result must fail closed before the caller's filesystem effect; do not resolve it by
  recreating, normalizing, retrying, or following a redirected path.

## Selection record

```text
selected: path-containment@42b2be1 (pre-existing source, newly cataloged without source change)
why: a later local telemetry lock adapter must keep its internally derived lock file beneath the
     Johnny-owned telemetry root while rejecting redirected ancestors.
read: this README -> path_containment.py -> test_worktree_containment.py.
dependency: none.
boundary: it establishes neither telemetry ownership nor a filesystem effect; the calling
          adapter must continue to bind exact metadata identity and own its own error handling.
```
