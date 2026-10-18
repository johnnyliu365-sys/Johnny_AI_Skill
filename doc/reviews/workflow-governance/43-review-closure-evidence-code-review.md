# Ticket 43 — local closure evidence review

## Source admission

Authority: `batch-checklist-local-20261018`; Root-scoped
`grant-wg43-closure-local-20261018`. This is local construction, not deployment
or a qualification of the evidence source.

Independent `/root/batch_authority_review` first rejected `55a7ce32` for three
ticket defects: test PASS was not child closure, expected finding/dependency
coverage was missing, and failure precedence was undefined. Revision02
`101e16ad25799d2a9b3158a8afb9782bc836a5a3`, ticket blob
`9c3afe7ba4281333f7ed36eb0177a1c2edd4fdef`, received APPROVED after those exact
findings were corrected. No product/test code changed during ticket review.

Root read source parity against `930fad32e15a76cd54423e34ea941a630af039da` for
all five allowed files, then allocated clean non-reparse repository-contained
`.worktrees/skill-improvement-43-closure`, branch
`codex/skill-improvement-43-closure`, baseline
`67fe2cca54ff61bc3561ed8d2788d2e01b5acd8d`. Author
`/root/review_closure_impl` receives only the type/constructor phase first;
`/root/review_closure_review` is the distinct review seat. The reviewed leaf
is byte-identical at allocation. Command ceiling300s, single90s, no network,
no author helpers. No new production authority source is granted.

Status: IMPLEMENTING_CONTRACTS. Mandatory qualified adversarial review and
real evidence resolver remain unproved; neither the document approval nor
constructor tests may stand in for those claims. Do not close checklist07/09.

Worktree owner is the named seat; retain candidates until review/evidence seal
and integration permit restricted teardown. Recovery holds remain untouched.

## C1 constructor review

Author `14811b79ef0c67223a07ee7551dfe9da4e213c23` changed only the existing
contracts/test files; no gate/Router behavior. Author47s commands includes a
corrected negative test that had incorrectly used different child identities.
Independent `/root/review_closure_review` at exact detached candidate APPROVED
TYPE_PHASE_ONLY: 11tests/41subtests, strict mypy for the three declared product
modules, diff checks. Six imported-Test-type collection warnings are not failures.
No product correction finding. Root returned AUTO_CONTINUE for C2–C4 to the
same author, conservatively accounting80/300s pending exact review timing.
This does not replace mandatory adversarial qualification.

## C1–C4 engineering result; formal review blocked

Candidate `d477020e0fb010ea12d610e3588630284472ecf8` changes exactly the five
allowed paths. Independent `/root/review_closure_review` confirmed ENGINEERING_PASS:
19tests/58subtests, three-module strict mypy, diff checks. Existing source,
Expected, AC and cleanup checks precede the new finite closure checks; only
REVIEW→HANDOFF requires closure. Author bypassed child-binding check and3cases
turned red. Reviewer inverted reviewer identity comparison through a different
door: a valid closure was denied and the named test failed. Exact restoration
and complete focused suite green; review worktree diff exit0.

Growth179product/428test lines is above150/180 signal. Reviewer inspected separate
DTO/reducer/consumer responsibilities and found no blocking duplication. No new
file/framework. Command accounting: author conservative122s included80s earlier
estimate; actual C1 reviewer36.1s replaces33s estimate, final reviewer22.6s gives
conservative147.7/300s. No cap/reset/third correction.

Final review verdict BLOCKED / REVIEW_BLOCKED: mandatory qualified read-only
Host audit is UNAVAILABLE, not an implementation finding. Existing CVE-D9
source integration and D10 typed observation are not that qualification.
Do not integrate this candidate or retry its passing implementation. Both
registered author/review worktrees and candidate ref are retained; no teardown
while required review evidence is unresolved. Other local tickets continue.
