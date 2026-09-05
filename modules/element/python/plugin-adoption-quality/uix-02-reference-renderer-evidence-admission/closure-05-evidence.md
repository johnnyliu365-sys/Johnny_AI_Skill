# UIX-02 closure revision 05 evidence

Authority: registry/main `117346cf44fbbc75a08aca5677f223c38df0fb00`; ticket revision 15;
baseline `b419954bc57777661d7522247ffc26977f668ca7`; candidate worktree branch
`implement/plugin-adoption-quality-uix-02`.

The revision-05 delta is evidence-only. Production source remained byte-for-byte unchanged:
`library/workflow_router/ui_reference_renderer_admission.py` SHA-256
`6553EA8BA8BC4C2BEC2B9400883F41770662E9D13C6938871B8AFEF5BE7D3917`, equal before and after
every temporary counter-mutation. Only the focused test and this element evidence are changed.

## R05 evidence additions

### UIR7 closed production-source grammar

`tests/test_ui_reference_renderer_admission.py` now applies literal policy data to the actual
production `ast.Module`: exact import forms/members/relative levels with no aliases or star
imports; double-underscore loaded names/attributes are rejected while `__all__` assignment is
allowed; exact literal call targets reject unknown/qualified/dynamic call shapes, starred args and
unpacked keywords. Hostile snippets are parsed, never executed, covering module-alias `Any`,
aliased `cast`, ordinary `Any` aliases, direct/indirect `__builtins__`, call-result attributes,
star imports, unlisted imports/symbols, wrong relative levels, aliases, starred/unpacked calls and
unknown callees.

Production mutation: add `if False: __import__("os").system("never-executed")`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir7
F ... AssertionError: () != ("unlisted call target: __import__('os').system", ...)
1 failed, 6 deselected, 15 subtests passed
```

After exact removal, source SHA-256 returned to the recorded value and:

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir7
. [100%]
1 passed, 6 deselected, 15 subtests passed
```

### UIR6 independent observation uniqueness

Added named `rendered-desktop-observation-reference` and
`rendered-mobile-observation-reference` collisions with all other refs/digests unique.

Production mutation: remove `renderer_observation_ref` from the duplicate set and change its
expected size from 3 to 2.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir6
SUBFAILED(duplicate_dimension='rendered-desktop-observation-reference')
SUBFAILED(duplicate_dimension='rendered-mobile-observation-reference')
2 failed, 1 passed, 6 deselected, 8 subtests passed
```

After exact restoration, source SHA-256 returned to the recorded value and:

```text
1 passed, 6 deselected, 10 subtests passed
```

### UIR4 acknowledgement seam

UIR4 now directly and through nested request validation rejects missing, `False`, `None`, `1`,
`1.0` and `"true"` with every other artifact field valid. Both UNAVAILABLE and DECLINED
fallbacks assert the admitted acknowledgement is the literal `True`.

Production mutation: change `owner_manual_open_acknowledgement: Literal[True]` to add `= True`.

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py -k uir4
SUBFAILED(acknowledgement='missing-direct')
SUBFAILED(acknowledgement='missing-nested')
2 failed, 1 passed, 6 deselected, 5 subtests passed
```

After exact restoration, source SHA-256 returned to the recorded value and:

```text
1 passed, 6 deselected, 7 subtests passed
```

## Retained mutation evidence

Existing UIRM1–UIRM6 were rerun against the revised test seam; each mutation turned its named
cell red and each source restoration returned the production SHA-256 and named cell green:

| Mutation | Named command | Unreduced red result | Restored green result |
| --- | --- | --- | --- |
| UIRM1 authority branch bypass | `pytest ... -k uir3` | 7 failed, 1 passed, 6 deselected, 8 subtests | 1 passed, 6 deselected, 7 subtests |
| UIRM2 always-match target | `pytest ... -k uir5` | 1 failed, 6 deselected | 1 passed, 6 deselected, 8 subtests |
| UIRM3 default acknowledgement | `pytest ... -k uir4` | 2 failed, 1 passed, 6 deselected, 5 subtests | 1 passed, 6 deselected, 7 subtests |
| UIRM4 omit brief binding comparison | `pytest ... -k uir6` | 1 failed, 6 deselected, 10 subtests | 1 passed, 6 deselected, 10 subtests |
| UIRM5 allow punctuation category | `pytest ... -k uir1` | 8 failed, 1 passed, 6 deselected, 28 subtests | 1 passed, 6 deselected, 36 subtests |
| UIRM6 allow combining-mark category | `pytest ... -k uir1` | 3 failed, 1 passed, 6 deselected, 33 subtests | 1 passed, 6 deselected, 36 subtests |

The UIRM5/6 direct UIR1 outputs were named by subtest; UIRM6 independently reported both
`\\u034f\\u034f\\u034f` and `e\\u0301e` rejection assertions.

## Final gates

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py
7 passed, 83 subtests passed

py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_codesign_contracts.py tests/test_workflow_router.py
68 passed, 216 subtests passed

py -3.11 -B -m mypy --strict --no-incremental library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
Success: no issues found in 2 source files

py -3.11 -B -m compileall -q library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
exit 0

git diff --check
clean
```
