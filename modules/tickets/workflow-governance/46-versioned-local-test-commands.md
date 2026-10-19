# 46｜釘選版本的本地驗證命令來源

| Field | Binding |
| --- | --- |
| State / Closure | PREPARED / 46-L1–L4 revision01 |
| Authority | Owner batch-checklist-local-20261018, latest implementation-plan instruction; checklist08/12, original PRD-20260805-009 / CHG-20260805-009 / workflow-governance SPEC. Original36/39 complete evidence retained; this is their command-source follow-up, no new PRD |
| Baseline | 10b06f82c0825d6339d12712f0b2f752114c8790; SPEC blob a700cad60de40096770582b04915bf490fd66a19; sealed CONTEXT blob06baa4dea5db1c3370086552c35a1d8f721ad47e; final reviewed document commit/leaf pinned before dispatch |
| Grant / roles | Root delegated grant-wg46-local-command-source-20261019, conditional on independent document review; Root control; /root/ticket46_command_impl gpt-6-luna/xhigh; /root/ticket46_command_review gpt-6-sol/high separate ordinary reviewer |
| Workspace | .worktrees/skill-improvement-46-commands / codex/skill-improvement-46-commands; reviewer .worktrees/skill-improvement-46-review; exact Git/clean/nonreparse readback before use |
| Profile / limits | STANDARD: bounded local Git data adapter, no authority/Host/neweffect. 300 command seconds total, author150/reviewer100/Root50, <=60s per command, initial+one correction. Prior36/39 historical usage retained UNKNOWN where unmeasured, not credited as free time; this explicitly derived new command-source allocation does not reset any prior work. 30B599.2/600 unchanged |
| Language / return | Python3.11 strict; ImplementationReturn COMPLETED/BLOCKED/CHANGE_DETECTED with candidate/files/checks/findings/deviations/actual cumulative command wall; no self-approval/integration/delegation |

```johnny-boundary
modify = library/local_orchestration/test_dependency_source_adapter.py
modify = tests/test_test_dependency_source_adapter.py
create = library/local_orchestration/test_command_source.py
create = tests/verification-commands.json
forbid = library/local_orchestration/test_dependency_inventory.py
forbid = library/workflow_router/
forbid = .github/
forbid = skills/
forbid = doc/
forbid = modules/
forbid = requirements-dev.txt
```

## One observable behavior

`GitTestDependencySourceAdapter.read_inventory_from_command_plan(repository_root,
commit_sha, test_ref, expected_plan_sha256)` reads the fixed
`tests/verification-commands.json` and Python blobs from the SAME full committed
SHA, validates the exact expected raw-byte SHA256 and closed local-plan grammar,
then feeds existing DeclaredTestCommand / PythonTestConsumerInventory.
Return existing GitPinnedTestDependencyInventory, retirement_authorized alwaysFalse.
No commands are executed by the adapter; no CI workflow or new runner is created.
Existing read_inventory with caller declarations remains unchanged and distinct.
This proves committed local source, not trusted Owner/remote CI authorization.

Reuse existing Git root/commit validation, bounded _run_git/deadline, object reads,
Git-replace protection, tree-mode checks, Python inventory and existing temp fixture.
New `test_command_source.py` owns only pure JSON decoding/validation to existing
DeclaredTestCommand tuple; no filesystem/runner/Graph/authorization engine.
New JSON file is the one maintained local data source for these two suite sets.
Existing adapter owns Git pin and composition. Do not copy Git/parser/test harness.

## Closed plan format / exact data

Root establishes new local command data under batch authority; it is NOT an
assertion that these commands existed in CI. JSON exactly:
schema_revision=1, scope=LOCAL_VERIFICATION_ONLY, commands=nonempty ordered array
of {command_ref, argv}. No other keys, duplicate JSON keys, coercion or defaults.
command_ref opaque nonempty [a-z][a-z0-9:-]{2,127}, unique; <=32 commands,
<=32 argv items, <=65536 payload bytes, strict UTF8. Public parser takes bytes and
returns tuple[DeclaredTestCommand,...], malformed input raises ValueError.
Internal strict wire models allowed, no Any/cast/bypass constructors.

Each argv starts exactly [python,-m,pytest], followed by >=1 unique literal
repository-relative `tests/... .py` file targets, ending exactly
[-q,-p,no:cacheprovider]. No empty segments, traversal, backslashes, absolute/
drive paths, variables, wildcard, expression, shell command, -c, unknown flag or
dynamic command. Match targets against the same pinned Python tree before
constructing inventory, not against the mutable worktree. False/bool revision
must reject, not coerce to1. Unknown targets refuse, not a false empty graph.

Two exact command records (and no full-suite/CI coverage claim):
- local:ticket-content: python -m pytest tests/test_ticket_content.py tests/test_ticket_template_contract.py -q -p no:cacheprovider
- local:test-inventory: python -m pytest tests/test_test_dependency_source_adapter.py tests/test_test_dependency_inventory.py -q -p no:cacheprovider

Source failures use existing TestDependencySourceError/finite enum; add only
COMMAND_PLAN_MISSING, COMMAND_PLAN_INVALID, COMMAND_PLAN_DIGEST_MISMATCH as needed;
Git/read/time/mode limits keep their existing reasons. Validate digest syntax and
raw-byte equality, source bounds and complete literal command map before returning.
The existing public result/constructor and DeclaredTestCommand success shape can
be ordinary-constructed before behavior; no new public DTO required.

## Acceptance / verification

46-L1 positive: current two-record plan parses; committed fictional plan names a
consumer→wrapper→helper chain and public adapter reports real transitive command
edge; retirement remainsFalse. No code/pytest/manifest argv executed by loader.
46-L2 negative: absent plan, wrong digest, wrong/extra/duplicate key, empty plan,
bool revision, wrong scope, invalidUTF8/size, duplicate ID/target, unknown target,
shell/variables/unknownflag/path traversal all refuse by named reason. Unknown
source cannot be treated as complete no-consumer. Reuse parameterized cases.
46-L3 exact source: working-copy plan/Python changes, moved HEAD and Git replace
cannot alter the old committed plan/graph; new pinned version only changes after
its own expected digest is supplied. Existing source adapter tests remain valid.
46-L4 author weakens raw digest/closed-plan predicate and observes named red then
exact restored green; independent reviewer uses different source/target validation
door, unreduced output and exact restoration. Zero red is finding.

Run python -m pytest tests/test_test_dependency_source_adapter.py tests/test_test_dependency_inventory.py -q -p no:cacheprovider;
python -m mypy --strict library/local_orchestration/test_command_source.py library/local_orchestration/test_dependency_source_adapter.py;
compile/import, public Git fixture smoke and git diff --check. No unrelated full
suite, real target/provider/credential/model/API or CI calls in product/tests.
TEST→A→B=N/A, no responsibility transfer or test retirement. XSS/DB/UI N/A.

Growth signals: existing adapter463 lines, extend only composition <=45 lines;
pure parser<=120; tests existing355 +<=140 lines; JSON<=40. Crossing a signal
requires responsibility review, never compression or mechanical split. Source
comments technical only; no Owner prompt, ticket narrative or generated reports.
Only test temp fixtures use existing harness; owner=Ticket46/seat, TTL through
review/seal, bounded registered artifacts retained under existing no-retry cleanup
hold if teardown unavailable. Do not remove any old worktree/journal/Recovery.

After approved source review, Root existing document mutation gate local integration
with exact blob parity. Checklist08/12 remain open for actual CI coverage/retirement
and other source/effect requirements. No push/release/Host activation or .github
configuration. A CI wrapper can consume this source later after its own scope,
complete required-suite selection and authorization; it must not duplicate argv.
