# Receipt: ticket calc/01 revision02 correction (REQ-CALC-001, REQ-CALC-002)

## tests
cell: tests
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/tests.txt
exit: 0

````
.......                                                                  [100%]
7 passed in 0.10s
exit=0
````

## strict
cell: strict
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/strict.txt
exit: 0

````
Success: no issues found in 4 source files
exit=0
````

## contract
cell: contract
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/contract.txt
exit: 0

````
requirements=2 specs=1 defects=0
exit=0
````

## preflight
cell: preflight
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/preflight.txt
exit: 0

````
tools=2 served=2
exit=0
````

## mut-adds
cell: mut-adds
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-adds.txt
exit: 1

````
diff --git a/src/calc.py b/src/calc.py
index 66ac98b..93cf05d 100644
--- a/src/calc.py
+++ b/src/calc.py
@@ -8,4 +8,4 @@ def add(a: int, b: int) -> int:
 
 def subtract(a: int, b: int) -> int:
     """Return a minus b."""
-    return a - b
+    return a + b
.FF.FF.                                                                  [100%]
================================== FAILURES ===================================
_________________________ SubtractTests.test_subtract _________________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract>

    def test_subtract(self) -> None:
>       self._check("basic")

tests\test_calc.py:45: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 8 != 2
__________________ SubtractTests.test_subtract_beyond_64_bit __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_64_bit>

    def test_subtract_beyond_64_bit(self) -> None:
>       self._check("beyond_64_bit")

tests\test_calc.py:57: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 1 != 36893488147419103233
_________________ SubtractTests.test_subtract_large_negative __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_large_negative>

    def test_subtract_large_negative(self) -> None:
>       self._check("large_negative")

tests\test_calc.py:60: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: -18446744073709551615 != -18446744073709551617
_________________ SubtractTests.test_subtract_negative_result _________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_negative_result>

    def test_subtract_negative_result(self) -> None:
>       self._check("negative_result")

tests\test_calc.py:48: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 8 != -2
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract - AssertionError: 8 != 2
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_64_bit - Asser...
FAILED tests/test_calc.py::SubtractTests::test_subtract_large_negative - Asse...
FAILED tests/test_calc.py::SubtractTests::test_subtract_negative_result - Ass...
4 failed, 3 passed in 0.12s
exit=1
````

## mut-adds-restored
cell: mut-adds-restored
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-adds-restored.txt
exit: 0

````
?? doc/handoffs/2026/governance/receipts/calc-01-subtract-c1/
tree clean after restore
.......                                                                  [100%]
7 passed in 0.03s
exit=0
````

## mut-swap
cell: mut-swap
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-swap.txt
exit: 1

````
diff --git a/src/calc.py b/src/calc.py
index 66ac98b..89b1015 100644
--- a/src/calc.py
+++ b/src/calc.py
@@ -8,4 +8,4 @@ def add(a: int, b: int) -> int:
 
 def subtract(a: int, b: int) -> int:
     """Return a minus b."""
-    return a - b
+    return b - a
.FFFFF.                                                                  [100%]
================================== FAILURES ===================================
_________________________ SubtractTests.test_subtract _________________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract>

    def test_subtract(self) -> None:
>       self._check("basic")

tests\test_calc.py:45: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: -2 != 2
__________________ SubtractTests.test_subtract_beyond_64_bit __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_64_bit>

    def test_subtract_beyond_64_bit(self) -> None:
>       self._check("beyond_64_bit")

tests\test_calc.py:57: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: -36893488147419103233 != 36893488147419103233
______________ SubtractTests.test_subtract_beyond_float_mantissa ______________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_float_mantissa>

    def test_subtract_beyond_float_mantissa(self) -> None:
>       self._check("beyond_float_mantissa")

tests\test_calc.py:54: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: -9007199254740993 != 9007199254740993
_________________ SubtractTests.test_subtract_large_negative __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_large_negative>

    def test_subtract_large_negative(self) -> None:
>       self._check("large_negative")

tests\test_calc.py:60: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 18446744073709551617 != -18446744073709551617
_________________ SubtractTests.test_subtract_negative_result _________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_negative_result>

    def test_subtract_negative_result(self) -> None:
>       self._check("negative_result")

tests\test_calc.py:48: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 2 != -2
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract - AssertionError: -2 ...
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_64_bit - Asser...
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_float_mantissa
FAILED tests/test_calc.py::SubtractTests::test_subtract_large_negative - Asse...
FAILED tests/test_calc.py::SubtractTests::test_subtract_negative_result - Ass...
5 failed, 2 passed in 0.12s
exit=1
````

## mut-swap-restored
cell: mut-swap-restored
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-swap-restored.txt
exit: 0

````
?? doc/handoffs/2026/governance/receipts/calc-01-subtract-c1/
tree clean after restore
.......                                                                  [100%]
7 passed in 0.03s
exit=0
````

## mut-float
cell: mut-float
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-float.txt
exit: 1

````
diff --git a/src/calc.py b/src/calc.py
index 66ac98b..faf17de 100644
--- a/src/calc.py
+++ b/src/calc.py
@@ -8,4 +8,4 @@ def add(a: int, b: int) -> int:
 
 def subtract(a: int, b: int) -> int:
     """Return a minus b."""
-    return a - b
+    return int(float(a) - float(b))
..FFF..                                                                  [100%]
================================== FAILURES ===================================
__________________ SubtractTests.test_subtract_beyond_64_bit __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_64_bit>

    def test_subtract_beyond_64_bit(self) -> None:
>       self._check("beyond_64_bit")

tests\test_calc.py:57: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 36893488147419103232 != 36893488147419103233
______________ SubtractTests.test_subtract_beyond_float_mantissa ______________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_beyond_float_mantissa>

    def test_subtract_beyond_float_mantissa(self) -> None:
>       self._check("beyond_float_mantissa")

tests\test_calc.py:54: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: 9007199254740992 != 9007199254740993
_________________ SubtractTests.test_subtract_large_negative __________________

self = <tests.test_calc.SubtractTests testMethod=test_subtract_large_negative>

    def test_subtract_large_negative(self) -> None:
>       self._check("large_negative")

tests\test_calc.py:60: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_calc.py:42: in _check
    self.assertEqual(subtract(case["a"], case["b"]), case["expected"])
E   AssertionError: -18446744073709551616 != -18446744073709551617
=========================== short test summary info ===========================
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_64_bit - Asser...
FAILED tests/test_calc.py::SubtractTests::test_subtract_beyond_float_mantissa
FAILED tests/test_calc.py::SubtractTests::test_subtract_large_negative - Asse...
3 failed, 4 passed in 0.12s
exit=1
````

## mut-float-restored
cell: mut-float-restored
candidate: 3c51c45fe5b958e9aed7f601649ab1d98062b8bb
tool_digest:
- src/calc.py=a120559617110dd442e5f544830ebf4738c32d08b066c571f337c6fce65cfc67
- tests/test_calc.py=05f9e76aa9cd978ad33cf5c79200319c0320ed4fa2e12e9357a926f4bcfc9790
- tests/ledger/calc.json=808d799ae38787a6520f21105a6b698d713199bbbd0e28d350b574d2e6ff3b65
capture: calc-01-subtract-c1/mut-float-restored.txt
exit: 0

````
?? doc/handoffs/2026/governance/receipts/calc-01-subtract-c1/
tree clean after restore
.......                                                                  [100%]
7 passed in 0.03s
exit=0
````

## STATEMENT
cell: STATEMENT

ImplementationReturn: COMPLETED, then ACTION_COMPLETED. No review approval, merge or release is claimed.
Cells ran at 3c51c45fe5b958e9aed7f601649ab1d98062b8bb, the correction commit on branch seat/calc-subtract, in the owner worktree .worktrees/calc-subtract. This receipt is a separate docs-only commit on top; the review candidate is the branch tip.
Before the correction the branch was merged with origin/main (merge b70830c). The ticket conflicted (the branch had DONE from the first receipt, main has revision02); the ticket was taken as main has it, since revision02 on main is authoritative per the ticket.
F1: tests/test_calc.py now opens with requirement, source (sha256 of doc/requirements/sources/calc.md) and mutation declarations for REQ-CALC-001 and REQ-CALC-002; expected values and operands are read from tests/ledger/calc.json and no assertion holds a literal expected value. Cell contract: defects=0.
F2: cell preflight ran the correction dispatch with a preflight block: tools=2 served=2. dispatch_lint printed LINT PASS and the dispatch sha256 is 6527eb9f62e0f59ace3dcf9c6f01a0003c5cd74418cd7bc1d83f1c6ff32fa43c, equal to the state row.
F4: cell strict is mypy --strict --python-version 3.11 src tests, passing.
F5: ledger cases beyond 2**53 and 2**64 added; the reviewer's float mutation turns three tests red (cell mut-float).
Reverse mutation: the subtract body was changed to a + b, b - a and int(float(a) - float(b)); each turned tests red and was restored with git checkout, after which the suite is green (cells mut-*, mut-*-restored). The mutation named add-subtracts-operands was declared in the spec header but not run, because add is outside this ticket's boundary.
Gates not run: coverage_map (no test was removed against main, no map file exists), repair_guard (not a tool repair), integrate (outside this seat). The state row stays IN_PROGRESS as the ticket directs; DONE is set after review.
