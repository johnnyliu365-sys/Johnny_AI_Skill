# Independent review checks

Read this reference only in ticket/cluster review or when designing the ticket's TDD matrix.
`CodeReview.md` defines review entry, evidence, finding routing and final conclusions; this file
is the canonical specialized checklist.

## Required dimensions

Review clarity/strong typing, project conventions, logic, boundary/error behavior, security,
performance, test truthfulness, dependency necessity and SPEC/ticket/Context conformity.
Additionally apply the specialized categories below when relevant.

## Defect categories

| Category | TDD minimum | Review action |
| --- | --- | --- |
| Path identity/prefix | exact match, extra suffix, slash variation, case, URL encoding, `..`, empty | verify canonical/path-component comparison; map all seven cells |
| Missing values | `null`, `undefined`, empty string, whitespace, empty list/object | verify which forms are intentionally equivalent |
| Authorization bypass | missing/wrong/expired credential and every indirect entry | enumerate all reachable paths from the composition root and confirm one gate |
| Token parsing/comparison | prefix/space/case/empty/length/non-ASCII; fixed-time compare | inspect source for forbidden equality and parser bypass |
| Error-code consistency | each failure asserts fixed public shape and distinct internal reason | prevent public side channel and internal diagnostic collapse |
| Exception behavior | inject each dependency failure; assert observable state/effect and throw/no-throw | detect swallowed errors and auxiliary failures that break primary flow |
| Test truthfulness | AC-to-test mapping and bounded reverse mutation | confirm assertions cover observable behavior and authentic first-red order |
| XSS/privileged JS | use `xss-review.md` matrix | trace every source/sink and privileged path |
| Task/worktree binding | control/sibling/parent/child/prefix-similar roots, prompt-only `cd`, unreadable root, wrong Git pointer/identity | independently read product, filesystem and Git evidence |
| Adaptive profile/resources | every factor/hard escalation, default one implementer, disjoint lanes, reviewer-only helper | recompute from actual diff/effects; reject model/size-based authority |
| POC/staging ancestry | unreviewed/ambiguous POC, wrong repo/base/ancestry, dirty/stale/diverged ref, altered plan, force/reset/delete | independently verify acceptance, Git ancestry, publication authority and release separation |

## Multi-Agent authority review

From effective reviewer and implementation sessions, enumerate actual thread-control tools and
the Johnny gateway caller surface. The reviewer positive path must bind one live descriptor and
receipt. The implementation session must prove both built-in tool absence and gateway
unreachability. Direct tool, MCP alias, indirect adapter, forged identity, replay and every wrong
project/ticket/handoff/target/worktree/branch/baseline/action/correlation combination must fail
before host effect.

## Ticket dispatch schema review

Read the exact ticket blob bound to the receipt. Require `State`, finite `Closure`,
`Implementation language`, `Profile / resource`, XSS classification, owner, worktree, branch,
baseline, allocation, receipt and correlation. Verify its commit against the registry and SPEC/
target Context. Re-run the strong-type preflight from `specification-ticketing.md`.

Missing or inferred fields are `TICKET_DEFECT / TICKET_SCHEMA_INVALID / NON_DISPATCHABLE`, even
if the implementation happens to look correct.
