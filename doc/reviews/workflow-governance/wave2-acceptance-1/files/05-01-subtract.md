# Receipt: ticket 01 subtract, REQ-CALC-002, run at the implementation commit

## tests
cell: tests
candidate: bd3e756d2bdc6e18a70357cacc66e6bfefe7d216
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=d0bdbff6ee6c62952e8920d7eafe29b564d54261cbc96c383e5181a6788ee0da
capture: evidence-01/tests.txt
exit: 0

````
....                                                                     [100%]
4 passed in 0.02s
exit=0
````

## smoke
cell: smoke
candidate: bd3e756d2bdc6e18a70357cacc66e6bfefe7d216
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=d0bdbff6ee6c62952e8920d7eafe29b564d54261cbc96c383e5181a6788ee0da
capture: evidence-01/smoke.txt
exit: 0

````
2 -2 0 2 5
exit=0
````

## mutation
cell: mutation
candidate: bd3e756d2bdc6e18a70357cacc66e6bfefe7d216
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=d0bdbff6ee6c62952e8920d7eafe29b564d54261cbc96c383e5181a6788ee0da
capture: evidence-01/mutation.txt
exit: 1

````
.FFF                                                                     [100%]
================================== FAILURES ===================================
_________________________ SubtractTests.test_subtract _________________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract>

    def test_subtract(self) -> None:
>       self.assertEqual(subtract(5, 3), 2)
E       AssertionError: 8 != 2

tests\test_calc.py:13: AssertionError
_________________ SubtractTests.test_subtract_negative_result _________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_negative_result>

    def test_subtract_negative_result(self) -> None:
>       self.assertEqual(subtract(3, 5), -2)
E       AssertionError: 8 != -2

tests\test_calc.py:16: AssertionError
_______________ SubtractTests.test_subtract_zero_and_negatives ________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_zero_and_negatives>

    def test_subtract_zero_and_negatives(self) -> None:
        self.assertEqual(subtract(0, 0), 0)
>       self.assertEqual(subtract(-4, -6), 2)
E       AssertionError: -10 != 2

tests\test_calc.py:20: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract - AssertionError: 8 != 2
FAILED tests/test_calc.py::SubtractTests::test_subtract_negative_result - Ass...
FAILED tests/test_calc.py::SubtractTests::test_subtract_zero_and_negatives - ...
3 failed, 1 passed in 0.07s
exit=1
````

## restored
cell: restored
candidate: bd3e756d2bdc6e18a70357cacc66e6bfefe7d216
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=d0bdbff6ee6c62952e8920d7eafe29b564d54261cbc96c383e5181a6788ee0da
capture: evidence-01/restored.txt
exit: 0

````
....                                                                     [100%]
4 passed in 0.01s
exit=0
````

## STATEMENT
cell: STATEMENT

Candidate bd3e756 is the implementation commit; this receipt and the ticket state row are committed after it in a docs-only commit on the same branch.
Cell tests is the ticket's completion command, `python -m pytest -q`, 4 passed.
Cell smoke calls subtract and add through the module import seam; the fixture has no application entry point.
Cells mutation and restored are the reverse-mutation evidence: with `return a - b` replaced by `return a + b` in a scratch export (never in the worktree), the three subtract tests go red and add stays green; the restored export is green again.
Not run: strict type check, lint, formatting and build, because the fixture project declares no such tool; this is stated here, not claimed.
