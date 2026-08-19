# W4 — The Whole Chain, Once, As One Thing

| Field | Value |
| --- | --- |
| State | `OPEN` |
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
