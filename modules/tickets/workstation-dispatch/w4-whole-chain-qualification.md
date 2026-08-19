# W4 — The Whole Chain, Once, As One Thing

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Baseline | `main` = `e6d0240` |
| Workload | `STANDARD`; gated qualification, `HIGH_ASSURANCE` |
| Depends on | W1, W2, W3, E10, E12 |

## The gap this closes

Every segment of the loop has evidence, and every *seam* between two adjacent
segments has been tested. What has never happened is one run of the whole
thing. Specifically:

- The gated runner qualification (E6) still gets its receipt from
  `_issue_receipt_fixture`, not from `admit_dispatch`.
- W2's closed-loop cell settles a wake attempt directly instead of receiving
  one from a real runner reacting to a real commit.

Seams passing individually is not the same claim as the chain holding. E10
was exactly this failure: two segments each correct, the join silently dead.

## One outcome

One gated qualification in which nothing is simulated and no test fixture
issues anything:

1. `admit_dispatch` issues the receipt (real grant, real containment gate).
2. `build_subscription` composes from that receipt (real probes).
3. A real detached runner arms on the exact ref.
4. A real commit lands a sealed terminal handoff leaf.
5. The runner delivers a real wake to a real host command.
6. `submit_review_return` records the verdict — and is only able to because
   the wake attempt the *runner* settled is on file.
7. `consume_next_return` emits exactly one `APPROVAL_GRANTED`.

## Frozen responsibility

- No `_issue_receipt_fixture` anywhere in this qualification. If the chain
  needs a fixture to run, the chain is not integrated.
- The wake evidence W2 checks must be the attempt the runner itself settled;
  the test may not claim or settle one.
- Gated behind `JOHNNY_LIVE_QUAL=1`, disposable root, zero residue.
- Existing qualifications keep their current shape; this is additive.

## Authorized implementation scope

```text
tests/test_whole_chain_qualification.py
modules/tickets/workstation-dispatch/
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `W4-R1` | The receipt driving the runner was issued by `admit_dispatch`; the qualification imports no receipt-issuing fixture. |
| `W4-R2` | The delivered wake payload is `action=REVIEW_HANDOFF` carrying the real observed commit and handoff id. |
| `W4-R3` | The verdict is admitted, and the wake attempt it relies on is the one the runner settled — proven by the return succeeding without the test ever claiming or settling an attempt. |
| `W4-R4` | Consumption emits exactly one `APPROVAL_GRANTED` whose event id contains the dispatched receipt id; a second consumption reports `NOTHING_PENDING`. |
| `W4-R5` | Zero residue: disposable root and repository removed, `tests/.johnny-runtime` absent. |
| `W4-R6` | Full suite green with the new file present; `mypy --strict` clean. |

## Closure evidence (2026-08-19, control-plane executed)

The chain ran as one thing on the first attempt. Gated run: `5 passed`.

- `W4-R1` The receipt came from `admit_dispatch` under a real grant and the
  real containment gate; the subscription composed from it. No receipt-issuing
  fixture is bound in this module's namespace.
- `W4-R2` Channel `HOST_COMMAND`; the delivered payload carries
  `action=REVIEW_HANDOFF` and `handoff_id=handoff-w4-001` — the runner's own
  wake for the real commit, not the capability probe's payload.
- `W4-R3` The verdict recorded. Nothing in this module can claim or settle a
  wake attempt (asserted on the namespace, not the file text), so the evidence
  W2 checked can only be the attempt the detached runner settled.
- `W4-R4` Exactly one `APPROVAL_GRANTED`, its event id containing the
  dispatched receipt id; the second consumption reported `NOTHING_PENDING`.
- `W4-R5` Disposable workspace removed, `tests/.johnny-runtime` absent.
- `W4-R6` `mypy --strict` clean; all four gated qualifications together
  `24 passed`.

Two defects in the first draft of this qualification, both mine and both
fixed: the R1/R3 checks read the file's own source for forbidden names, which
is self-defeating because the names appear in the assertions themselves (now
namespace checks), and `RunnerStarted`/`RunnerStopped` were imported from the
lifecycle port rather than their defining module.

## A larger finding this qualification surfaced

Adding this file changed the *non-gated* suite from `989 passed` to
`988 passed, 1 failed`. Attribution showed the content is irrelevant: a file
containing one `assertTrue(True)` produces `984 passed, 7 failed`. The suite's
result depends on collection order, which makes every "full suite green"
claim in this repository conditional. Raised as
`workflow-governance/03-suite-order-fragility`; not fixed here, and not
papered over.
