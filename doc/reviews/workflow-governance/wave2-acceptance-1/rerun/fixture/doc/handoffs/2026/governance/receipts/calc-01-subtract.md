# Receipt: ticket calc/01 subtract(a, b) returns a - b (REQ-CALC-002)

## green-tests
cell: green-tests
candidate: d4fca80be98dfbabb2b8fd53fe13ae44414e89ed
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=3e32d0ebca190ac777dd33976a73db42c7c3499bc6538f9779ea8f729c16be96
capture: calc-01-subtract/green.txt
exit: 0

````
....                                                                     [100%]
4 passed in 0.02s
exit=0
````

## mutation-red
cell: mutation-red
candidate: d4fca80be98dfbabb2b8fd53fe13ae44414e89ed
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=3e32d0ebca190ac777dd33976a73db42c7c3499bc6538f9779ea8f729c16be96
capture: calc-01-subtract/mutation-red.txt
exit: 1

````
 src/calc.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
.FF.                                                                     [100%]
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
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract - AssertionError: 8 != 2
FAILED tests/test_calc.py::SubtractTests::test_subtract_negative_result - Ass...
2 failed, 2 passed in 0.09s
exit=1
````

## mutation-restored
cell: mutation-restored
candidate: d4fca80be98dfbabb2b8fd53fe13ae44414e89ed
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=3e32d0ebca190ac777dd33976a73db42c7c3499bc6538f9779ea8f729c16be96
capture: calc-01-subtract/mutation-restored.txt
exit: 0

````
?? doc/handoffs/2026/governance/receipts/
tree clean after restore
....                                                                     [100%]
4 passed in 0.03s
exit=0
````

## STATEMENT
cell: STATEMENT

Candidate is the implementation commit d4fca80be98dfbabb2b8fd53fe13ae44414e89ed on branch seat/calc-subtract; this receipt and the ticket state are a separate docs-only commit on top of it.
The commands ran in the owner worktree .worktrees/calc-subtract with the tree at the candidate and clean.
New behavior: no first-red run is claimed (implementation-tdd.md). Reverse mutation of the one named behavior: the subtract body was changed from a - b to a + b; test_subtract and test_subtract_negative_result turned red (8 != 2, 8 != -2); the mutation was restored with git checkout and the suite is green again (cell mutation-restored).
test_subtract_zero did not turn red under that mutation (0 + 0 equals 0 - 0); it is a boundary case, not the discriminating test for the behavior.
Strict type check, lint, format, build and data gates: the ticket names none beyond python -m pytest -q and none is configured in the project; not run.
Smoke: the primary path is the real import seam, from src.calc import subtract, exercised by the tests above; no service or entry point exists.
The implementation commit was made by the earlier session; this session re-ran every command above at the candidate and did not rely on that session's claims.
