# Receipt: ticket 01 subtract revision02 correction, run at the correction commit

## tests
cell: tests
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/tests.txt
exit: 0

````
.....                                                                    [100%]
5 passed in 0.03s
exit=0
````

## smoke
cell: smoke
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/smoke.txt
exit: 0

````
2 -2 0 2 5 True
exit=0
````

## mypy
cell: mypy
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/mypy.txt
exit: 0

````
Success: no issues found in 4 source files
exit=0
````

## contract
cell: contract
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/contract.txt
exit: 0

````
requirements=2 specs=1 defects=0
exit=0
````

## mutation-add
cell: mutation-add
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/mutation-add.txt
exit: 1

````
F....                                                                    [100%]
================================== FAILURES ===================================
______________________________ AddTests.test_add ______________________________

self = <tests.test_calc.AddTests testMethod=test_add>

    def test_add(self) -> None:
        for a, b, expected in LEDGER["add"]:
>           assert add(a, b) == expected
E           assert -1 == 5
E            +  where -1 = add(2, 3)

tests\test_calc.py:31: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_calc.py::AddTests::test_add - assert -1 == 5
1 failed, 4 passed in 0.08s
exit=1
````

## mutation-subtract
cell: mutation-subtract
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/mutation-subtract.txt
exit: 1

````
.FFFF                                                                    [100%]
================================== FAILURES ===================================
_________________________ SubtractTests.test_subtract _________________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract>

    def test_subtract(self) -> None:
        for a, b, expected in LEDGER["subtract"][:1]:
>           assert subtract(a, b) == expected
E           assert 8 == 2
E            +  where 8 = subtract(5, 3)

tests\test_calc.py:37: AssertionError
_________________ SubtractTests.test_subtract_beyond_64_bits __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_64_bits>

    def test_subtract_beyond_64_bits(self) -> None:
        for a, b, expected in LEDGER["subtract"][4:]:
>           assert subtract(a, b) == expected
E           assert 0 == 36893488147419103232
E            +  where 0 = subtract(18446744073709551616, -18446744073709551616)

tests\test_calc.py:49: AssertionError
_________________ SubtractTests.test_subtract_negative_result _________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_negative_result>

    def test_subtract_negative_result(self) -> None:
        for a, b, expected in LEDGER["subtract"][1:2]:
>           assert subtract(a, b) == expected
E           assert 8 == -2
E            +  where 8 = subtract(3, 5)

tests\test_calc.py:41: AssertionError
_______________ SubtractTests.test_subtract_zero_and_negatives ________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_zero_and_negatives>

    def test_subtract_zero_and_negatives(self) -> None:
        for a, b, expected in LEDGER["subtract"][2:4]:
>           assert subtract(a, b) == expected
E           assert -10 == 2
E            +  where -10 = subtract(-4, -6)

tests\test_calc.py:45: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract - assert 8 == 2
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_64_bits - asse...
FAILED tests/test_calc.py::SubtractTests::test_subtract_negative_result - ass...
FAILED tests/test_calc.py::SubtractTests::test_subtract_zero_and_negatives - ...
4 failed, 1 passed in 0.09s
exit=1
````

## mutation-wrap
cell: mutation-wrap
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/mutation-wrap.txt
exit: 1

````
..F..                                                                    [100%]
================================== FAILURES ===================================
_________________ SubtractTests.test_subtract_beyond_64_bits __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_64_bits>

    def test_subtract_beyond_64_bits(self) -> None:
        for a, b, expected in LEDGER["subtract"][4:]:
>           assert subtract(a, b) == expected
E           assert 0 == 36893488147419103232
E            +  where 0 = subtract(18446744073709551616, -18446744073709551616)

tests\test_calc.py:49: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_64_bits - asse...
1 failed, 4 passed in 0.08s
exit=1
````

## restored
cell: restored
candidate: b00b521c23f6f8b6ec863cbae0509f93ddca4e52
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=43b0cbd4f77e525b45f7e45f62032d2dd14e0f89b2dbc2759e720456485d6f22
- tests/ledger/calc.json=c3720198072c3b50bb766a9e44888783d02eb6ba683effb1136035e34528fb8d
capture: evidence-01-c1/restored.txt
exit: 0

````
.....                                                                    [100%]
5 passed in 0.02s
exit=0
````

## STATEMENT
cell: STATEMENT

Correction commit b00b521c23f6f8b6ec863cbae0509f93ddca4e52 (parent: the merge of origin/main into seat/calc-subtract). Every cell ran at it. This receipt is committed after it, in a commit that adds only receipt files; the review candidate is the branch tip.
ImplementationReturn: COMPLETED -> ACTION_COMPLETED. Evidence: this receipt, cells tests, smoke, mypy, contract, mutation-add, mutation-subtract, mutation-wrap, restored.
Smoke command: `python -c` importing add and subtract from src.calc and printing the five ledger-style results plus the beyond-64-bit check, through the module import seam; the fixture has no application entry point.
Cell mypy is `python -m mypy --strict --python-version 3.11 --no-incremental src tests` (F3). Cell contract is `contract_gate.py` against the snapshot with specs=tests, exit 0 with defects=0 (F1).
Cells mutation-add, mutation-subtract and mutation-wrap are reverse mutations in scratch exports of the correction commit, never in the worktree: add returns a - b (test_add red), subtract returns a + b (four subtract tests red), subtract wraps at 64 bits (only test_subtract_beyond_64_bits red, F5). Cell restored is an unmutated export, green.
Choice made where the rules are silent: revision01 set the ticket state to DONE before review. That state was discarded by taking the main-branch revision02 ticket in the merge; the state row stays IN_PROGRESS for review, as the revision02 dispatch directs, and DONE is for the control plane after approval.
Choice: the merge of origin/main into the seat branch resolved the one conflict (the ticket) by taking main's version whole.
Choice: the old receipt 01-subtract.md and its evidence-01 directory are kept unchanged as history of revision01.
