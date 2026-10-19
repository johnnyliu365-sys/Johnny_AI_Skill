# Ticket46 local command-source review

## Admission

Original batch authority remains effective. Different seat batch_authority_review
APPROVED exact ticket46 atf4dbba5d684106f32ef36de8ed998201553b0f97,
leaf a4dd9aab32a1207ee281d7fe47ba717331b56f44. Root activates only
grant-wg46-local-command-source-20261019, exact four-path boundary, named author
and different reviewer, existing300s/150+100+50 limits. Prior36/39 usage remains
historical/UNKNOWN;30B599.2/600 unchanged. New manifest establishes local-only
commands; no existing CI or completeness/retirement authority is inferred.

Registered author/reviewer worktrees and branch are those in ticket46; owner is
the named seat/Ticket46, TTL through independent review and evidence seal.
No old asset removal; known cleanup denial remains a separate hold. All development
uses the native same-lifetime lane, no invented receipt/gateway prerequisite.
Root may reuse its existing landing worktree after clean/identity validation.

## Initial candidate / one bounded correction

Author returned352a0829aad3fd1ccc05e3f8c431082e156dfc21, exact four declared paths,
baseddd39b26f. Ordinary independent ticket46_command_review found one46-L2
IMPLEMENTATION_DEFECT: bounded deeply nested malformed JSON escapes json.loads as
RecursionError, rather than parserValueError / adapterCOMMAND_PLAN_INVALID.
Public probe b'['*1200+b'0'+b']'*1200 reproduced it. Other affected tests36passed/
21subtests, strict, compile/import/diff passed. Its different-door target-membership
mutation turned the unknown-target cell red; exact restore passed. Not approved yet.

Author's first reply had incomplete time bookkeeping, NOT an exhausted platform
quota. Root recovered its original session metadata: agent_path
/root/ticket46_command_impl, parent01a02958-71c0-7913-96ee-5b589c5fc993, log
C:/Users/GameBoy/.codex/sessions/2026/10/19/rollout-2026-10-19T12-53-26-01a15281-e11d-74c0-af54-7f6dab48d2bc.jsonl,
2164787bytes, SHA2566a63e0864da9127910b39ffeab8e0d6961f6c790d12cd0e4a9247aeb74032a83.
All53 original exec call/output pairs exist, including38 command-bearing calls;
outer tool wall headers total132.2s, matched call/result timestamps136.502s including
patch/transport overhead. Header rounding upper bound132.2+53*0.1=137.5s; charge
138s conservatively, leaving12/150, not UNKNOWN as free time. Original failing
suite runs are included. No rerun was used to reconstruct historical accounting.

Root admits exactly ONE author correction on the existing grant/worktree: catch
RecursionError at the JSON boundary and add the corresponding malformed-input
regression using the existing parameterized tests. No new file, contract or scope.
Maximum11 additional command seconds including inspections/Git/compile/import;
all command outputs must retain timing. Reviewer already reproduced the baseline
defect; author targets this regression only, reviewer reruns affected whole suite
within its own100s. No new author full-suite run or budget reset. If the11s cap is
insufficient, return BLOCKED, not another automatic attempt. Rest of the closure,
allowlist,300s total and non-CI/non-qualification claims remain unchanged.

## Correction review and exact integration authority

Original author committed2ba5578130301229253765ccdb50683a93f70828 after8.77s total
correction tool/command time. Focused1passed/18deselected/15subtests; cumulative
conservative146.77/150, not a fresh author allocation. Catching RecursionError and
the existing parameterized1200-depth malformed case close46-L2. Different original
reviewer /root/ticket46_command_review APPROVED that exact candidate: affected
36passed/22subtests, strict mypy, compile/import, diff and clean readback passed.
Deep nesting is asserted at the pure parser seam; named adapter error mapping is
verified from its unchanged ValueError catch, not a separate deep-case Git probe.

Reviewer initially estimated75s before its28.389s correction, which looked over
100. Root recovered original BOTH-phase transcript instead of resetting the budget:
C:/Users/GameBoy/.codex/sessions/2026/10/19/rollout-2026-10-19T13-06-57-01a1528e-40d2-72e0-a092-7a566c209d52.jsonl,
765226bytes, SHA25666279b692ad6603bdebc5b938786efda788139d61b02097b80b1aa1f871d672a.
Exact metadata binds that reviewer and parent01a02958; all21 call/output pairs,
including19 command calls, have original headers totaling75.1s and outer timestamp
total76.422s, patches/overhead included. Rounding upper75.1+21*0.1=77.2; charge78s
cumulative/100. Same reviewer accepted reconciliation and issued APPROVED, no rerun.

Reviewed final blobs:
- library/local_orchestration/test_command_source.py: 521ed828caae46260ef56ab4ac297ea8844d21ce
- library/local_orchestration/test_dependency_source_adapter.py: 0c5c0626637a00b68b159e4e84386d657df94cd8
- tests/test_test_dependency_source_adapter.py: 012c3a785fc286a625fb987a7d278a44650d1522
- tests/verification-commands.json: a0e95637 (full blob read back at integration)

The adapter's55-line growth crosses45 signal, not a hard size limit; reviewer
confirmed one Git composition/tree-filtering responsibility, pure105-line parser
separate, no duplicate Git runner, tests share original fixture. No framework or
new dependency. The manifest is local-only two suites, rawSHA256
72f44d70ef96f160f09432545aacde383f3480f69a7fbc77c13fd793359e0f67.

Author digest mutation raw call_7faa6a5b1a9345ceb88c758cf2c20a95 and exact restore
call_9e2f5f0f15ff4abe8b53862a44649e83 were recovered from its above hashed transcript:
the497-token original traceback was NOT reduced (only the author's later summary
had ellipses). Command python -m pytest tests/test_test_dependency_source_adapter.py
-k test_missing_invalid_and_wrong_digest_plans_have_named_failures -q -p no:cacheprovider;
weakening digest toifFalse yields TestDependencySourceError not raised,1failed /
19deselected,2.21s pytest,4.6360972s command. Restore yields1passed/19deselected,
1.91s pytest,4.3831864s command. Later test rename retains that exact digest assertion.

Independent target-membership mutation call_0e37e8fdc4fc40628b56555db61d3d23 ran
python -m pytest tests/test_test_dependency_source_adapter.py::GitTestDependencySourceAdapterTests::test_missing_invalid_wrong_digest_and_unpinned_targets_fail_closed -vv -p no:cacheprovider,
with no reducer. It disabled adapter target membership (not author's digest door).
Unreduced failure payload:
```text
tests/test_test_dependency_source_adapter.py::GitTestDependencySourceAdapterTests::test_missing_invalid_wrong_digest_and_unpinned_targets_fail_closed FAILED [100%]
...
        plan = self._command_plan_bytes(target="tests/not_committed.py")
        self._write_bytes("tests/verification-commands.json", plan)
        commit = self._commit("unknown-plan-target")
>       with self.assertRaises(SourceError) as error:
E       AssertionError: TestDependencySourceError not raised
tests\test_test_dependency_source_adapter.py:136: AssertionError
FAILED tests/test_test_dependency_source_adapter.py::GitTestDependencySourceAdapterTests::test_missing_invalid_wrong_digest_and_unpinned_targets_fail_closed - AssertionError: TestDependencySourceError not raised
1 failed in2.98s
```
The excerpt above is explanatory; the complete unfiltered diff/session/traceback
is the named raw call in the pinned transcript, not this shortened quotation.
Exact restore passed; adapter hash0c5c0626 matched candidate and review tree clean.
No zero-red accepted; no repeated mutation campaign after unrelated parser correction.

Root now admits exact source-only replay352a0829+2ba55781 onto current committed
control, using clean Root-owned reused .worktrees/skill-improvement-44-land and
newref codex/skill-improvement-46-land. Preserve all prior branches/journals/holds;
existing document mutation gate must read Ticket46 from integration branch, admit
only these four paths, and ff-only integrate. Root50s cumulative allocation remains;
author146.77+reviewer78+Root50 ceiling274.77/300. Final affected suite/strict/compile
and blob parity required. Registered journal root
C:/Users/GameBoy/AppData/Local/Temp/Johnny-checklist46-20261019, ownerRoot/Ticket46,
TTL through independent seal then existing CLEANUP_BLOCKED retention. No cleanup
attempt, test retirement, actual authority/Host qualification or formal activation.

## Local integration seal

Existing gate returned INTEGRATED ata0bfc286e2102b9ccfc2575f58bbb2e08b8f44b0,
replays999be61d+a0bfc286 on Rootcontrol192daef8. Only four authorized source/data
paths differ; final blobs equal reviewed candidate, including plan fullblob
a0e956376f00bf27cb9919e981f5de0724903bb9. Root integrated suite36passed/22subtests
in17.02s pytest, strict two modules and COMPILE_IMPORT_PASS. The three returned
wait intervals10.0088648+5.0033017+2.1437518=17.1559183s describe ONE ongoing shell
session, not three test attempts and not its complete elapsed command duration:
the process also ran between polls. Do not substitute wait time for command time.
Root's complete50s allocation is conservatively charged in the274.77/300 ledger;
this allocation is not a claimed precise measurement of the combined shell job.

Journal C:/Users/GameBoy/AppData/Local/Temp/Johnny-checklist46-20261019/queue/document-mutation-journal.jsonl,
384bytes, SHA256d76009e4b3a855733926f961d139f9e8b39f72638ad9f8e7e31ef17f0e53093b;
oneINTEGRATED record2026-10-19T05:14:45.432146+00:00, exactcandidate above,
integration branchcodex/skill-improvement-checklist, principalGameBoy, Ticket46.
Control was clean; main remainsa1cb6c13adbeb52a4117991727dcc3d4af6d2a33, clean.
Retain registered46 author/reviewer worktrees and shared Root landing/ref/journal
under CLEANUP_BLOCKED; cache inventory UNKNOWN, not 'nothing remains'. No cleanup
was attempted; old44/31B/45/30B/43 and Recovery holds preserved. Source capability
complete only; final08/12, test retirement, CI and Host/source qualifications open.

Independent seal: original reviewer SEAL_CONFIRMED at control5d0539bf, exactfour
blobs and384-byte journal/hash, clean control/main and unchangeda1cb6c13 main.
Seal used4.77s; conservatively charge reviewer83/100 cumulative (not78 after seal),
author146.77/150 and Rootfull50 remain; updated total279.77/300. No further tests,
mutation or cleanup. Seal confirms this slice only; no new global completion claim.
