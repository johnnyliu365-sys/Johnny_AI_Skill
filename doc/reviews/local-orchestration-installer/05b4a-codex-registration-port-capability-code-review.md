# Ticket 05B4A Codex Registration Port Capability Code Review

## Review decision

`APPROVED / READY_TO_MERGE`

The sole additive correction closes the complete initial-review batch CR-146
and CR-147 without changing `CLOSURE-LOCAL-INSTALL-T05B4A-01`, its A1-A7
acceptance closure or the product requirement. No blocking finding remains.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / owner | `05b4a-codex-registration-port-capability`; task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; branch `codex/implementation-codex-registration-port-05b4a` |
| Dispatch baseline | `f5b187fa692b1b7aeda8e77d885cf331aac80ccb` |
| Implementation | `f344a49b323eac039c5f36f51c823dcf75fa7c9c` |
| Docs-only handoff | `7c4fd5970d54798040fb5a6ac128717bbeb49f79`; PRG-20260812-193 |
| Binding | `hnd_local_orchestration_install_05b4a_20260812`; `aln_local_orchestration_install_05b4a_20260812`; `rcpt_local_orchestration_install_05b4a_20260812`; `corr-local-orchestration-install-05b4a-20260812` |

## Initial CodeReview.md verification

| Gate | Result |
| --- | --- |
| Exact ancestry / scope | PASS: `f5b187f -> f344a49 -> 7c4fd59`; implementation changes exactly the three authorized paths and handoff changes only `doc/WorkProgressReport.md`. The implementation worktree is clean and the three-worktree topology is unchanged. |
| Focused / regression | PASS on a Unicode-safe immutable ZIP export: focused 6/6 and full discovery 266/266. |
| Strict type / compile | PASS: strict full-tree mypy and in-memory compile over 118 files. |
| A1 / A2 | PASS: exact request/result rebuilding, finite nested-shape rejection, binding/version/target/locator/digest/auth mismatch classification and zero pre-validation trap invocation are covered and independently read. |
| A3 | CHANGES_REQUESTED: factory-token checks and safe `repr` pass, but generic serialization exposes the four admitted bound operations. |
| A4 / A5 | PASS: finite candidate/method rejection and inherited-method admission hold; candidate, metaclass, descriptor, annotations, wrapper/default, representation and process-control traps remain uninvoked. |
| A6 | PASS: imports remain contract-only; source review found no live effect, `Any`, `type: ignore`, broad catch, optional port, dynamic candidate lookup, raw output or rejected-source reuse. |
| A7 test truthfulness | PARTIAL: the four required isolated reversals were independently reproduced and restored, but the submitted A3 evidence does not test its frozen serialization rule. |
| Diff / residue | PASS for the immutable return: `git diff --check`, exact commit scopes, tracked/ignored/cache readbacks and dependency isolation are clean. |

## Blocking findings

### CR-146 — IMPLEMENTATION_DEFECT — serialized capability leaks effect authority

Closure: A3 and the frozen boundary requiring that serialization, `repr`,
errors and handoff never expose bound functions.

`CodexRegistrationPortCapability` is a dataclass whose fields include the
private authority token and all four bound operations. Independent probes on
the immutable handoff reproduced both bypasses:

- `dataclasses.asdict(capability)` returns `_authority`, `status`,
  `fresh_preflight`, `add_marketplace`, `add_plugin` and `prove`; all four
  operation values are callable.
- `pickle.loads(pickle.dumps(capability))` rejects `metadata()` because its
  copied token is no longer current, yet `fresh_preflight` remains callable
  and executes. Authority validation therefore does not contain the leaked
  effect handle.

This is blocking because 05B4A exists specifically to prevent unreviewed or
copied effect authority from crossing the registration boundary. The return
must not be merged or used by 05B4B while generic serialization can export the
operations.

### CR-147 — EVIDENCE_DEFECT — A3 claims metadata-only without a serialization probe

Closure: A3 and A7.

The committed A3 test checks `metadata().model_dump()`, safe `repr`, fake and
copied tokens, and an empty forged instance. It does not exercise a standard
structural serializer or pickle round-trip, while PRG-193 states that A3 is
metadata-only. The missing probe allowed CR-146 to pass focused and full
tests. Correction evidence must make the serialization leak red before the
smallest production correction and must retain all existing A3 assertions.

## Complete-batch disposition

No other blocking finding was discovered across A1-A7. The reviewer
independently reversed request/source binding, wrong-target rejection,
descriptor-free MRO access and private constructor authority; all four named
tests turned red, and the restored source blob exactly matched
`fd54d220c969e35d44112c2101a0b2d79f042c6a` before focused tests returned 6/6.

One additive same-ticket correction is required on the existing branch and
worktree. It must add committed A3 red/green coverage proving standard
dataclass structural serialization and pickle/copy transfer cannot export or
retain callable operations or usable authority. Metadata must remain exactly
`ADMITTED / 4`, `repr` and errors must remain metadata-only, all existing
constructor and zero-invocation cases must remain green, and no operation may
run during admission or probes. No new source file, dependency, branch,
worktree, product behavior, 05B4B work, merge, push, release, deployment or
live/target-project effect is authorized.

## Terminal correction review

| Field | Evidence |
| --- | --- |
| Correction implementation | `3ab59717a9b8d57fbca8fbd8d86937a8f9eaacee`; additive changes only to the registration-port module and its focused test |
| Correction handoff | `7ce9bb36e90af669daa5dfa2999638a112f4cde3`; WPR-only PRG-20260812-196 |
| Ancestry | `7c4fd59 -> 3ab5971 -> 7ce9bb3`; the initial implementation and review evidence remain immutable ancestors |
| Binding | `hnd_local_orchestration_install_05b4a_correction_01_20260812`; retained allocation `aln_local_orchestration_install_05b4a_20260812`, receipt `rcpt_local_orchestration_install_05b4a_20260812` and correlation `corr-local-orchestration-install-05b4a-correction-01-20260812` |

### Terminal CodeReview.md verification

| Gate | Result |
| --- | --- |
| Exact ancestry / scope | PASS: both additive commits descend from the submitted handoff; implementation changes only the two correction-authorized paths and handoff changes only `doc/WorkProgressReport.md`. The implementation worktree is clean. |
| Focused / regression | PASS on a Unicode-safe immutable ZIP export: focused 6/6 and full discovery 266/266. |
| Strict type / compile | PASS: strict full-tree mypy and in-memory compile over 118 files. |
| CR-146 / A3 behavior | PASS: capability is slotted and non-dataclass; `asdict`, `astuple`, shallow/deep copy and pickle round-trip all fail finitely without exporting or retaining an operation. Metadata remains exactly `ADMITTED / 4`, repr/errors are metadata-only and adapter operation count is zero. |
| CR-147 / A3 evidence | PASS: all five transfer probes are committed in the named A3 test. The first-red record identifies five independent failures against unchanged production, and the reviewer reproduced every corrected probe. |
| A1-A6 regression | PASS: exact request/result binding, target/version classification, finite malformed input, descriptor/metaclass trap isolation and contract-only source constraints remain intact. Source sentinel found no `Any`, `type: ignore`, broad catch, dynamic candidate lookup, optional port or historical-source reuse. |
| A7 truthfulness | PASS: the reviewer independently reversed request/source binding, wrong-target rejection, descriptor-free MRO access and private constructor authority. Every mutation turned red; inverse patches restored source blob `a85f134b5999fc50e07e2fab617c4c8450d669cd`, test blob `93d4d405b43008142b811ad899f803887a5540cf` and focused 6/6. |
| Diff / residue | PASS: exact commit scopes, `git diff --check`, submitted-lane tracked/ignored/cache readbacks and three-worktree topology are clean. Review execution remained outside all worktrees. |

## Terminal disposition

CR-146 is closed as `IMPLEMENTATION_DEFECT_RESOLVED`; CR-147 is closed as
`EVIDENCE_DEFECT_RESOLVED`. Guarded integration is authorized only with this
formal review commit as first parent and reviewed handoff `7ce9bb3` as second
parent. The merge must preserve every WPR record exactly once and rerun
focused/full/type/compile/source/diff/residue checks. No push, release,
deployment, live Codex mutation or target-project write is authorized.

## Guarded integration

Merge `5f30a717e16cbdc126a685e48542c11337310bbf` preserves formal terminal
review `47bc1e1ab23a489ba8043ca20dcdf64646e126a3` as first parent and reviewed
handoff `7ce9bb36e90af669daa5dfa2999638a112f4cde3` as second parent. Product
source and tests merged without conflict; the sole WPR conflict retained
PRG-191 through PRG-197 exactly once and in order. Integrated source/test blobs
equal the reviewed correction.

On the merged tree, focused 6/6, serial full discovery 266/266, strict mypy
118 files and in-memory compile 118 files passed. Source sentinel,
`git diff --check`, parent/blob equality and tracked/ignored/cache residue
checks passed. No live Codex mutation, target-project write, push, release or
deployment occurred.
