# Ticket 05B4A Codex Registration Port Capability Code Review

## Review decision

`CHANGES_REQUESTED / ONE_ADDITIVE_CORRECTION_REQUIRED`

The complete initial-review blocking batch is CR-146 and CR-147. Both point to
the existing `CLOSURE-LOCAL-INSTALL-T05B4A-01` A3 metadata-only capability
boundary; the closure and product requirement do not change.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / owner | `05b4a-codex-registration-port-capability`; task `019ff01a-3afc-79e3-aa7e-a467b8da9b9d`; existing `workflow-implementer-2`; branch `codex/implementation-codex-registration-port-05b4a` |
| Dispatch baseline | `f5b187fa692b1b7aeda8e77d885cf331aac80ccb` |
| Implementation | `f344a49b323eac039c5f36f51c823dcf75fa7c9c` |
| Docs-only handoff | `7c4fd5970d54798040fb5a6ac128717bbeb49f79`; PRG-20260812-193 |
| Binding | `hnd_local_orchestration_install_05b4a_20260812`; `aln_local_orchestration_install_05b4a_20260812`; `rcpt_local_orchestration_install_05b4a_20260812`; `corr-local-orchestration-install-05b4a-20260812` |

## CodeReview.md verification

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
