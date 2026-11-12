# Receipt: ticket calc/01 finding C1, declared mutation add-subtracts-operands

## mut-add-subtracts
cell: mut-add-subtracts
candidate: 92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c2/mut-add-subtracts.txt
exit: 1

````
diff --git a/src/calc.py b/src/calc.py
index 66ac98b..7844f14 100644
--- a/src/calc.py
+++ b/src/calc.py
@@ -3,7 +3,7 @@
 
 def add(a: int, b: int) -> int:
     """Return a plus b."""
-    return a + b
+    return a - b
 
 
 def subtract(a: int, b: int) -> int:
F......                                                                  [100%]
================================== FAILURES ===================================
______________________________ AddTests.test_add ______________________________

self = <tests.test_calc.AddTests testMethod=test_add>

    def test_add(self) -> None:
        case = _case("add", "basic")
>       self.assertEqual(add(case["a"], case["b"]), case["expected"])
E       AssertionError: -1 != 5

tests\test_calc.py:36: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_calc.py::AddTests::test_add - AssertionError: -1 != 5
1 failed, 6 passed in 0.14s
exit=1
````

## mut-add-subtracts-restored
cell: mut-add-subtracts-restored
candidate: 92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c2/mut-add-subtracts-restored.txt
exit: 0

````
?? doc/handoffs/2026/governance/receipts/calc-01-subtract-c2/
tree clean after restore
.......                                                                  [100%]
7 passed in 0.05s
exit=0
````

## STATEMENT
cell: STATEMENT

ImplementationReturn: COMPLETED, then ACTION_COMPLETED. No review approval, merge or release is claimed.
This receipt closes finding C1 of the correction review in doc/reviews/calc/01-subtract-code-review.md and adds to, and does not replace, calc-01-subtract-c1.md, whose ten cells ran at 3c51c45fe5b958e9aed7f601649ab1d98062b8bb.
The cells here ran at 92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6, the merge of origin/main (the correction review record) into seat/calc-subtract; the merge changes only doc/reviews/calc/01-subtract-code-review.md. The three tool blobs listed are identical at 3c51c45 and at 92d59c0623bfbf3e8c9f6e1509e0289c0d4321f6.
The earlier STATEMENT gave the boundary as the reason for not running add-subtracts-operands. That was wrong: a reverse mutation is restored and commits nothing. The mutation changed the body of add from a + b to a - b; test_add turned red (-1 != 5); after git checkout the suite is green (7 passed).
C2 and C3 are carried as hardening of the test ledger per the control plane note; no change was made to any source or test file.
