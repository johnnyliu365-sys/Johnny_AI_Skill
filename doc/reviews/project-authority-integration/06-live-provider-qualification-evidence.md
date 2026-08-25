# PAI-06 live provider qualification — evidence record

| Field | Value |
| --- | --- |
| Named project | `Johnny_AI_Skill` development repository (cross-machine, two workstations) |
| Repository | `https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git` (public) |
| Declared authority ref | `refs/heads/main` |
| Provider / method | github.com / `gh` CLI (GraphQL + REST) and git https protocol |
| Observer | control plane on the owner's User workstation, owner-directed |
| Owner authority | Owner instruction, 2026-08-25 (Asia/Taipei): "你來跑06-07" |
| Correlation | `pai06-live-qual-20260824` |
| Observation time | `2026-08-25T04:05:16Z` through cleanup readback |
| Baseline | development `main = bb9b7bc826b22d6ea35765bc1ee7cd9169d2e8cc` before, unchanged after |

## Method

All probes ran against a disposable branch `qual-hc-20260824` created from `main` for this
qualification only. No protection, ref or setting on `main` was touched at any point; the
before/after readback of `main` is identical. Every probe is an actual provider action with its
response read back — nothing below is inferred from documentation.

## Per-capability results

| # | Capability | Probe | Provider response (verbatim where quoted) | Result |
| --- | --- | --- | --- | --- |
| 1 | Direct remote observation of the authority ref | `git ls-remote <url> refs/heads/main`, no local cache | `bb9b7bc8…` — equal to local `main` | `PROVEN` |
| 2 | Enforcement policy readback | `PUT`/readback branch protection on the qual branch | `enforce_admins: true`, `required_approving_review_count: 1`, `dismiss_stale_reviews: true`, `allow_force_pushes: false` | `PROVEN` (policy) |
| 3 | Direct update of a protected line is refused | push a probe commit straight to the protected branch, admin credential, git protocol | `remote rejected … (protected branch hook declined)`; "Changes must be made through a pull request"; exit 1 | `PROVEN` |
| 4 | Merge without approval is refused | open PR `#1` (head = probe commit, base = protected branch); read state; then attempt the merge itself | `reviewDecision: REVIEW_REQUIRED`, `mergeStateStatus: BLOCKED`; merge attempt: "is not mergeable: the base branch policy prohibits the merge" | `PROVEN` |
| 5 | Self-approval is refused | `gh pr review --approve` on own PR | `GraphQL: Review Can not approve your own pull request` | `PROVEN` (provider blocks it) |
| 6 | Stale-approval invalidation — behaviour | would require an approval that a later head-change dismisses | single-account cannot create an approval to dismiss (see #5), so the dismissal behaviour was never observed; only the `dismiss_stale_reviews: true` policy readback in #2 exists | `UNPROVEN` (named reason: single-account limit) |
| 7 | Admin-flag bypass (`gh pr merge --admin`) against `enforce_admins` | probe was prepared but **blocked by this workstation's local execution policy**, not by a provider readback | no provider response exists | `UNPROVEN` (named reason: probe not executed; provider behaviour must not be inferred) |

## Honest summary

Per `ADR-20260824-020` decision 6:

- **Ordinary-actor enforcement: `PROVEN` by direct readback** — a protected authority line
  refuses direct pushes (even over an admin credential on the git protocol), refuses merge
  without an approving review, and refuses self-approval.
- **Admin-actor enforcement: `UNPROVEN`** — the `--admin` merge probe did not run, and the
  stale-approval dismissal behaviour is unobservable with a single account. Neither leg may be
  recorded as `PROVEN` from documentation, and neither is.
- Residual risk stated plainly: the gate operator's own account is an administrator. Whether the
  provider stops that account's deliberate `--admin` bypass is untested. The control that does
  bind that account today is process (the gate is the only integration path this project uses),
  not a proven provider mechanism.

## Cleanup readback

PR `#1` `CLOSED`, never merged. Both qualification branches deleted (`qual-hc` remote count 0).
Protection rule deleted with the branch. `main` before and after:
`bb9b7bc826b22d6ea35765bc1ee7cd9169d2e8cc`, byte-identical readback.
